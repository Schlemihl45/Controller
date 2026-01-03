# gui/pages/tools_page.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QGridLayout, QToolButton, QPushButton, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).parent.parent / "database.db"

from database.databaseManager import Database

from gui.scrollWidget import ScrollWidget
from gui.MakeTouchButton import make_touch_button
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Signal, Qt


class ToolsFrame(QFrame):
    """
    Represents a single Tool in the ToolsPage.
    Clickable QFrame with a label showing the tool name.
    """
    open_tool_detail = Signal(int, str, str, float, float, float, float, int, float, float, str, str)


    def __init__(self, tool_id: int, name: str, type: str, diameter: float, radius: float, cutting_length: float, length: float, flutes: int, zOffset: float, rOffset: float, supplier: str, description: str,  parent=None):
        super().__init__(parent)
        self.tool_id = tool_id
        self.name = name

        # Set frame style
        self.setStyleSheet("""
            QFrame {
                background-color: #1c314d;
                border: 1px solid #3A4F74;
                border-radius: 8px;
            }
        """)

        # Layout and label
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 9, 0)
        self.layout.setSpacing(6)


        # Load icons
        icon_endmill = QIcon("../assets/endmill.svg")
        icon_radiusEndmill = QIcon("../assets/radius_endmill.svg")
        icon_facemill = QIcon("../assets/facemill.svg")
        icon_chamferEndmill = QIcon("../assets/chamfermill.svg")
        icon_threadmill = QIcon("../assets/threadmill.svg")
        icon_drill = QIcon("../assets/drill.svg")



        # Icon
        self.icon = QToolButton(self)
        if type == "Endmill":
            self.icon.setIcon(icon_endmill)
        elif type == "Radius Endmill":
            self.icon.setIcon(icon_radiusEndmill)
        elif type == "Facemill":
            self.icon.setIcon(icon_facemill)
        elif type == "Chamfermill":
            self.icon.setIcon(icon_chamferEndmill)
        elif type == "Drill":
            self.icon.setIcon(icon_drill)
        else:
            self.icon.setIcon(icon_endmill)

        self.icon.setStyleSheet("border: none;")
        self.icon.setIconSize(QSize(64, 64))
        self.layout.addWidget(self.icon)
        self.icon.setEnabled(False)

        # Description
        # --- Description widget ---
        description_widget = QWidget(self)
        description_layout = QGridLayout(description_widget)
        description_layout.setContentsMargins(9, 15, 9, 15)
        description_layout.setSpacing(12)

        # --- Header Labels ---
        lbl_name_h = QLabel("Name")
        lbl_spacer_h = QLabel("")  # Spacer, unsichtbar
        lbl_diam_h = QLabel("Ø")
        lbl_len_h = QLabel("Cutting Length")
        lbl_flutes_h = QLabel("Flutes")

        header_labels = [
            lbl_name_h,
            lbl_spacer_h,
            lbl_diam_h,
            lbl_len_h,
            lbl_flutes_h,
        ]

        for col, lbl in enumerate(header_labels):
            lbl.setStyleSheet("color: #E6E6E6; font-size: 12px; border: none;")
            if col == 1:
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            lbl.setAlignment(Qt.AlignLeft if col == 0 else Qt.AlignCenter)
            description_layout.addWidget(lbl, 0, col)

        # --- Value labels ---
        self.lbl_name = QLabel(f"{name}")
        self.lbl_spacer = QLabel("")  # Spacer
        self.lbl_diameter = QLabel(f"{diameter} mm")
        self.lbl_length = QLabel(f"{cutting_length} mm")
        self.lbl_flutes = QLabel(f"{flutes}")

        value_labels = [
            self.lbl_name,
            self.lbl_spacer,
            self.lbl_diameter,
            self.lbl_length,
            self.lbl_flutes,
        ]

        for col, lbl in enumerate(value_labels):
            lbl.setStyleSheet("color: #E6E6E6; font-size: 18px; font-weight: bold; border: none;")
            if col == 1:
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            lbl.setAlignment(Qt.AlignLeft if col == 0 else Qt.AlignRight)
            description_layout.addWidget(lbl, 1, col)

        # Details button
        self.details_button = QToolButton(self)
        self.details_button.setText("...")
        self.details_button.setStyleSheet("background-color: #34455f; border: none;")
        self.details_button.clicked.connect(
            lambda: self.open_tool_detail.emit(tool_id, name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier, description)
        )

        self.layout.addWidget(self.icon)
        self.layout.addWidget(description_widget,1)
        self.layout.addStretch()
        self.layout.addWidget(self.details_button)

class ToolsPage(QWidget):
    """
    ToolsPage for the CNC Controller GUI.
    Loads all tools from the SQLite database and creates clickable ToolFrames.
    """
    openToolDetail = Signal(int, str, str, float, float, float, float, int, float, float, str, str)

    def __init__(self):
        super().__init__()

        # Main layout for this page
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 9)
        self.buttons_layout.setSpacing(6)


        self.addToolButton = QToolButton(self)
        self.addToolButton.setIcon(QIcon("../assets/addTool.svg"))
        self.addToolButton.setIconSize(QSize(48, 48))
        self.addToolButton.setStyleSheet("background-color: #1c314d;")
        self.addToolButton.clicked.connect(self.openToolDetail.emit)
        self.addToolButton.setIconSize(QSize(48, 48))

        self.buttons_layout.addWidget(self.addToolButton)

        self.spacer = QPushButton(self)
        self.spacer.setText("Tools")
        self.spacer.setStyleSheet("background-color: #1c314d; text-align: left; font-weight: bold; font-size: 24px; padding-left: 25px;")
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.buttons_layout.addWidget(self.spacer)

        self.sortLayout = QHBoxLayout()
        self.sortFrame = QFrame(self)
        self.sortFrame.setObjectName("sortFrame")
        self.sortFrame.setLayout(self.sortLayout)
        self.sortLabel = QLabel(self)
        self.sortLabel.setText("Sort by")
        self.sortLabel.setObjectName("sortLabel")
        self.sortComboBox = QComboBox(self)
        self.sortComboBox.setObjectName("sortComboBox")
        self.sortComboBox.addItems(["Name", "Type", "Diameter", "Cutting Length", "Flutes"])
        self.sortComboBox.currentTextChanged.connect(self.sort_tools)
        self.sortLayout.addWidget(self.sortLabel)
        self.sortLayout.addWidget(self.sortComboBox)

        self.buttons_layout.addWidget(self.sortFrame)

        self.main_layout.addLayout(self.buttons_layout)

        # Scroll area
        self.scroll_widget = ScrollWidget()
        self.main_layout.addWidget(self.scroll_widget)

        # Load tools from DB and create ToolFrames
        self.database = Database()
        self.load_tools()

    def load_tools(self):
        """
        Loads all tools from the database and creates a ToolsFrame for each.
        """

        tools = self.database.get_all_tools(order_by="id")

        frames = []
        for tool_id, name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier, description in tools:
            frame = ToolsFrame(tool_id, name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier, description)
            frame.open_tool_detail.connect(self.openToolDetail.emit)
            frames.append(frame)

        # Add all frames to the scroll widget
        self.scroll_widget.load_objects(frames)

    def sort_tools(self, key):
        if not DB_PATH.exists():
            print("Database does not exist:", DB_PATH)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if key == "Name":
            order_by = "name COLLATE NOCASE"
        elif key == "Type":
            order_by = "type"
        elif key == "Diameter":
            order_by = "diameter"
        elif key == "Cutting Length":
            order_by = "cutting_length"
        elif key == "Flutes":
            order_by = "flutes"
        else:
            order_by = "id"

        cursor.execute(f"SELECT id, name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier, description FROM tools ORDER BY {order_by} ASC")
        tools = cursor.fetchall()
        conn.close()

        frames = []
        for tool_id, name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier, description in tools:
            frame = ToolsFrame(tool_id, name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier, description)
            frame.open_tool_detail.connect(self.openToolDetail.emit)
            frames.append(frame)

        self.scroll_widget.load_objects(frames)
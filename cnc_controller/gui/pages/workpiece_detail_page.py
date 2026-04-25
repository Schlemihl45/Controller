from pathlib import Path

from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFrame, QLabel, QToolButton, QVBoxLayout, QWidget

from database.workpiece_model import Workpiece
from gui.widgets.scroll_widget import ScrollWidget


class FileFrame(QFrame):
    def __init__(self, filename: str, parent=None):
        super().__init__(parent)

        self.setStyleSheet(
            """
            QFrame {
                background-color: #1c314d;
                border-radius: 8px;
                border: 1px solid #2E3440;
            }
            QLabel {
                color: #E6E6E6;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        lbl_filename = QLabel(filename)
        lbl_filename.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #E6E6E6;"
        )
        layout.addWidget(lbl_filename)


class WorkpieceDetailPage(QWidget):
    """
    WorkpieceDetailPage for the CNC Controller GUI.
    """

    def __init__(self, parent=None, workpiece: Workpiece | None = None):
        super().__init__(parent)

        self.workpiece = workpiece

        # Load the .ui
        loader = QUiLoader()
        ui_path = Path(__file__).parent / "workpiece_detail_page.ui"
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise IOError(f"Cannot open {ui_path}")
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Title
        self.name_label = self.ui.findChild(
            QToolButton, "workpieceDetailPage_nameButton"
        )
        self.name_label.setText(self.workpiece.name)

        # File browser
        self.files_placeholder = self.ui.findChild(
            QFrame, "files_placeholderFrame"
        )
        self.filesBrowser = ScrollWidget()

        placeholder_layout = QVBoxLayout(self.files_placeholder)
        placeholder_layout.setContentsMargins(0, 0, 0, 0)
        placeholder_layout.addWidget(self.filesBrowser)

        self.load_workpiece_files()

    def load_workpiece_files(self):
        if not self.workpiece or not self.workpiece.path.exists():
            return

        files_frame = []
        file_types = [".cnc", ".nc", ".gcode"]

        for file in self.workpiece.path.iterdir():
            if file.is_file() and file.suffix in file_types:
                frame = FileFrame(file.name, self.filesBrowser)
                files_frame.append(frame)

        if not files_frame:
            placeholder = QLabel("No G-Code files found.")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet(
                "color: #AAB2C5; font-size: 16px;"
            )
            self.filesBrowser.objects_layout.addWidget(placeholder)
            return

        self.filesBrowser.load_objects(files_frame)

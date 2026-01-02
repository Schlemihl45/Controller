from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QPlainTextEdit, QLabel, QComboBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox

from gui.ToolInputWidget import ToolInputWidget

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database.db"


class ToolDetailPage(QWidget):
    """
    Page for creating or editing a tool.
    """
    tool_saved = Signal()
    tool_deleted = Signal()

    def __init__(self, tool_id: int = None, name: str = "", type: str = None, diameter: float = 0.0, radius: float = 0.0, cutting_length: float = 0.0, length: float = 0.0, flutes: int = None, zOffset: float = 0.0, rOffset: float = 0.0, supplier: str = None, description: str = None):
        super().__init__()

        self.tool_id = tool_id

        # Load UI file
        loader = QUiLoader()
        ui_path = Path(__file__).parent / "ToolDetailPage.ui"
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise IOError(f"Cannot open {ui_path}")

        self.ui = loader.load(ui_file, self)  # pass self as parent
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # remove margins
        layout.setSpacing(0)
        layout.addWidget(self.ui)
        # Assuming self.ui is the loaded UI
        self.render_frame = self.ui.findChild(QWidget, "toolDetailPage_renderFrame")

        # Create layout for the placeholder
        render_layout = QVBoxLayout(self.render_frame)
        render_layout.setContentsMargins(0, 0, 0, 0)
        render_layout.setSpacing(0)

        # Add the ToolInputWidget
        self.toolInputWidget = ToolInputWidget(name, type, diameter,cutting_length, length, self.render_frame)
        render_layout.addWidget(self.toolInputWidget)

        self.save_button = self.ui.findChild(QPushButton, "toolDetailPage_saveButton")
        self.save_button.clicked.connect(self.save_tool)

        self.delete_button = self.ui.findChild(QPushButton, "toolDetailPage_deleteButton")
        self.delete_button.clicked.connect(lambda: self.confirm_delete())

        self.name_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_nameLineEdit")
        self.name_lineEdit.setText(name)
        self.diameter_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_diameterLineEdit")
        self.diameter_lineEdit.setText(str(diameter))
        self.length_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_lengthLineEdit")
        self.length_lineEdit.setText(str(length))
        self.cuttingLength_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_cuttingLengthLineEdit")
        self.cuttingLength_lineEdit.setText(str(cutting_length))
        self.flutes_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_flutesLineEdit")
        self.flutes_lineEdit.setText(str(flutes))
        self.radius_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_radiusLineEdit")
        self.radius_lineEdit.setText(str(radius))
        self.zOffset_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_zOffsetLineEdit")
        self.zOffset_lineEdit.setText(str(zOffset))
        self.rOffset_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_rOffsetLineEdit")
        self.rOffset_lineEdit.setText(str(rOffset))
        self.supplier_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_supplierLineEdit")
        self.supplier_lineEdit.setText(str(supplier))
        self.description_plainTextEdit = self.ui.findChild(QPlainTextEdit, "toolDetailPage_descriptionPlainTextEdit")
        self.description_plainTextEdit.setPlainText(str(description))

        self.type_comboBox = self.ui.findChild(QComboBox, "toolDetailPage_typeComboBox")
        self.type_comboBox.setCurrentText(type)
        self.type_comboBox.currentTextChanged.connect(self.type_changed)

    def type_changed(self, type):
        print(type)

        if type == "Endmill":
            self.radius_lineEdit.setEnabled(False)
        elif type == "Radius Endmill":
            pass
        elif type == "Torus Endmill":
            pass
        elif type == "Facemill":
            pass
        elif type == "Drill":
            pass
        elif type == "Threadmill":
            pass

    def save_tool(self):
        """
        Save the current tool to the database.
        If a tool with the same id exists, update it. Otherwise insert a new tool.
        """
        # Daten aus den Widgets auslesen
        name = self.name_lineEdit.text()
        type = self.type_comboBox.currentText()
        diameter = float(self.diameter_lineEdit.text() or 0)
        radius = float(self.radius_lineEdit.text() or 0)
        length = float(self.length_lineEdit.text() or 0)
        cutting_length = float(self.cuttingLength_lineEdit.text() or 0)
        flutes_text = self.flutes_lineEdit.text()
        flutes = int(flutes_text) if flutes_text.isdigit() else None
        zOffset = float(self.zOffset_lineEdit.text() or 0)
        rOffset = float(self.rOffset_lineEdit.text() or 0)
        supplier = self.supplier_lineEdit.text()
        description = self.description_plainTextEdit.toPlainText()

        # Verbindung zur DB
        if not DB_PATH.exists():
            print("Database not found:", DB_PATH)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if self.tool_id:  # 🔹 Bestehendes Tool anhand der ID updaten
            cursor.execute("""
                UPDATE tools
                SET name=?, type=?, diameter=?, radius=?, cutting_length=?, length=?, flutes=?, zOffset=?, rOffset=?, supplier=?, description=?
                WHERE id=?
            """, (name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier, description,
                  self.tool_id))
            print(f"Tool '{name}' updated.")
        else:  # 🔹 Neues Tool anlegen
            cursor.execute("""
                INSERT INTO tools (name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier,
                  description))
            self.tool_id = cursor.lastrowid  # 🔹 ID merken
            print(f"Tool '{name}' created.")

        conn.commit()
        conn.close()

        self.tool_saved.emit()

    def confirm_delete(self):
        name = self.name_lineEdit.text()

        msg = QMessageBox(self)
        msg.setObjectName("deleteTool_messageBox")
        msg.setWindowTitle("Delete Tool")
        msg.setText(f"Do you really want to delete the tool:\n\n{name}?")
        msg.setIcon(QMessageBox.Warning)

        delete_btn = msg.addButton("Delete", QMessageBox.DestructiveRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)

        msg.setDefaultButton(cancel_btn)

        msg.exec()

        if msg.clickedButton() == delete_btn:
            self.delete_tool(self.tool_id)

    def delete_tool(self, tool_id: int):
        if not DB_PATH.exists():
            print("Database not found:", DB_PATH)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Prüfen, ob das Tool existiert
        cursor.execute("SELECT name FROM tools WHERE id=?", (tool_id,))
        result = cursor.fetchone()
        if not result:
            print(f"Tool with ID {id} does not exist")
            conn.close()
            return

        # Löschen
        cursor.execute("DELETE FROM tools WHERE id=?", (tool_id,))
        conn.commit()
        conn.close()
        print(f"Tool '{result[0]}' deleted.")

        # Liste neu laden, falls diese Methode aus MainPage aufgerufen wird:
        if hasattr(self, 'load_tools'):
            self.load_tools()  # refresh tools list

        self.tool_deleted.emit()

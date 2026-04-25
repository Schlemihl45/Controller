from PySide6.QtWidgets import (
    QWidget, QToolButton, QVBoxLayout, QLineEdit, QPushButton,
    QPlainTextEdit, QLabel, QComboBox, QMessageBox,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Signal, QSize, Qt
from PySide6.QtGui import QIcon, QIntValidator, QDoubleValidator
from pathlib import Path

from gui.pages.tool_input_widget import ToolInputWidget
from gui.widgets.touch_button import make_touch_button
from database.db_manager import Database


class ToolDetailPage(QWidget):
    """
    Page for creating or editing a tool.
    """
    tool_saved = Signal()
    tool_deleted = Signal()

    standardText = "Material:\nRPM:\nFeedrate:"


    def __init__(self, tool_id: int = None, name: str = "", tool_type: str = "Endmill", diameter: float = 0.0, radius: float = 0.0, cutting_length: float = 0.0, length: float = 0.0, flutes: int = None, zOffset: float = 0.0, rOffset: float = 0.0, supplier: str = None, description: str = standardText):
        super().__init__()

        self.tool_id = tool_id

        self.database = Database()

        self._updating_lineedits = False

        # Load UI file
        loader = QUiLoader()
        ui_path = Path(__file__).parent / "tool_detail_page.ui"
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
        self.toolInputWidget = ToolInputWidget(name, tool_type, diameter, cutting_length, length, self.render_frame)
        self.toolInputWidget.dimension_changed.connect(self.on_dimension_changed)

        render_layout.addWidget(self.toolInputWidget)

        self.save_button = self.ui.findChild(QToolButton, "toolDetailPage_saveButton")
        make_touch_button(self.save_button,
                          icon_path="../assets/saveTool.svg",
                          clicked_icon_path="../assets/saveTool_clicked.svg")

        # Dein bestehendes clicked-Signal bleibt für die Logik
        self.save_button.pressed.connect(self.save_tool)

        self.delete_button = self.ui.findChild(QToolButton, "toolDetailPage_deleteButton")
        make_touch_button(self.delete_button,
                          icon_path="../assets/deleteTool.svg",
                          clicked_icon_path="../assets/deleteTool.svg")
        self.delete_button.clicked.connect(lambda: self.confirm_delete())

        self.name_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_nameLineEdit")
        self.name_lineEdit.setText(name)

        self.diameter_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_diameterLineEdit")
        self.diameter_lineEdit.setText(str(diameter))
        self.diameter_validator = QDoubleValidator(0.0, 100, 2, self)
        self.diameter_lineEdit.editingFinished.connect(lambda: self.validate_field(self.diameter_lineEdit, self.diameter_validator))

        self.length_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_lengthLineEdit")
        self.length_lineEdit.setText(str(length))
        self.length_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.length_lineEdit.editingFinished.connect(lambda: self.validate_field(self.length_lineEdit, self.length_validator))

        self.cuttingLength_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_cuttingLengthLineEdit")
        self.cuttingLength_lineEdit.setText(str(cutting_length))
        self.cuttingLength_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.cuttingLength_lineEdit.editingFinished.connect(lambda: self.validate_field(self.cuttingLength_lineEdit, self.cuttingLength_validator))

        self.flutes_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_flutesLineEdit")
        self.flutes_lineEdit.setText(str(flutes))
        self.flutes_validator = QIntValidator(0.0, 20.0, self)
        self.flutes_lineEdit.editingFinished.connect(lambda: self.validate_field(self.flutes_lineEdit, self.flutes_validator))

        self.radius_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_radiusLineEdit")
        self.radius_lineEdit.setText(str(radius))
        self.radius_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.radius_lineEdit.editingFinished.connect(lambda: self.validate_field(self.radius_lineEdit, self.radius_validator))

        self.zOffset_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_zOffsetLineEdit")
        self.zOffset_lineEdit.setText(str(zOffset))
        self.zOffset_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.zOffset_lineEdit.editingFinished.connect(lambda:self.validate_field(self.zOffset_lineEdit, self.zOffset_validator))

        self.rOffset_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_rOffsetLineEdit")
        self.rOffset_lineEdit.setText(str(rOffset))
        self.rOffset_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.rOffset_lineEdit.editingFinished.connect(lambda: self.validate_field(self.rOffset_lineEdit, self.rOffset_validator))

        self.supplier_lineEdit = self.ui.findChild(QLineEdit, "toolDetailPage_supplierLineEdit")
        self.supplier_lineEdit.setText(str(supplier))

        self.description_plainTextEdit = self.ui.findChild(QPlainTextEdit, "toolDetailPage_descriptionPlainTextEdit")
        self.description_plainTextEdit.setPlainText(str(description))

        self.type_comboBox = self.ui.findChild(QComboBox, "toolDetailPage_typeComboBox")
        self.type_comboBox.setCurrentText(tool_type)
        self.type_comboBox.currentTextChanged.connect(self.type_changed)

        for edit in [self.length_lineEdit, self.cuttingLength_lineEdit, self.diameter_lineEdit, self.radius_lineEdit]:
            edit.textChanged.connect(self.line_edit_changed)


    def validate_field(self, line_edit, validator_field):
        validator = validator_field
        text = line_edit.text()
        state = validator.validate(text, 0)[0]
        if state != QDoubleValidator.Acceptable:
            # z.B. zurücksetzen oder warnen
            line_edit.setStyleSheet("border: 1px solid red;")
        else:
            line_edit.setStyleSheet("border: 1px solid #2E3440;")

    def line_edit_changed(self):
        if self._updating_lineedits:
            return  # Ignore programmatic changes
        self.toolInputWidget.draw_tool(
            self.type_comboBox.currentText(),
            diameter=self.diameter_lineEdit.text(),
            length=self.length_lineEdit.text(),
            cutting_length=self.cuttingLength_lineEdit.text(),
            radius=self.radius_lineEdit.text()
        )

    def on_dimension_changed(self, dim_id, value):
        self._updating_lineedits = True
        if dim_id == "length":
            self.length_lineEdit.setText(str(value))
        elif dim_id == "cutting_length":
            self.cuttingLength_lineEdit.setText(str(value))
        elif dim_id == "diameter":
            self.diameter_lineEdit.setText(str(value))
        self._updating_lineedits = False

    def type_changed(self, tool_type):
        print(f"new tool_type: {tool_type}")
        if tool_type == "Endmill":
            self.radius_lineEdit.setEnabled(False)
            self.toolInputWidget.draw_tool(tool_type)
        elif tool_type == "Radius Endmill":
            print("changed to radius endmill")
            self.toolInputWidget.draw_tool(tool_type)
        elif tool_type == "Facemill":
            self.toolInputWidget.draw_tool(tool_type)
        elif tool_type == "Drill":
            self.toolInputWidget.draw_tool(tool_type)
        elif tool_type == "Chamfermill":
            self.toolInputWidget.draw_tool(tool_type)
        elif tool_type == "Threadmill":
            self.toolInputWidget.draw_tool(tool_type)

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

        self.database.save_tool(self.tool_id, name, type, diameter, radius, length, cutting_length, flutes, zOffset, rOffset, supplier, description)

        self.tool_saved.emit()

    def confirm_delete(self):
        name = self.name_lineEdit.text()

        msg = QMessageBox(self)
        #msg.setWindowFlag(Qt.FramelessWindowHint)
        msg.setObjectName("deleteTool_messageBox")
        msg.setWindowTitle("Delete Tool")
        msg.setText(f"Do you really want to delete the tool:\n\n{name}")
        msg.setIcon(QMessageBox.Warning)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("confirmDeleteTool_delete_button")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("confirmDeleteTool_cancel_button")

        msg.addButton(delete_btn, QMessageBox.DestructiveRole)
        msg.addButton(cancel_btn, QMessageBox.RejectRole)

        msg.setDefaultButton(cancel_btn)

        msg.exec()

        if msg.clickedButton() == delete_btn:
            self.delete_tool(self.tool_id)

    def delete_tool(self, tool_id: int):
        self.database.delete_tool(tool_id)

        if hasattr(self, 'load_tools'):
            self.load_tools()  # refresh tools list

        self.tool_deleted.emit()

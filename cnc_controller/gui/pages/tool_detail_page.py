from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPlainTextEdit, QPushButton,
    QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)

from database.db_manager import Database
from gui.pages.tool_input_widget import ToolInputWidget
from gui.widgets.touch_button import make_touch_button

ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"


class ToolDetailPage(QWidget):
    """Page for creating or editing a tool."""

    tool_saved = Signal()
    tool_deleted = Signal()

    standardText = "Material:\nRPM:\nFeedrate:"

    def __init__(
        self,
        tool_id: int = None,
        name: str = "",
        tool_type: str = "Endmill",
        diameter: float = 0.0,
        radius: float = 0.0,
        cutting_length: float = 0.0,
        length: float = 0.0,
        flutes: int = None,
        zOffset: float = 0.0,
        rOffset: float = 0.0,
        supplier: str = None,
        description: str = standardText,
    ):
        super().__init__()

        self.tool_id = tool_id
        self.database = Database()
        self._updating_lineedits = False

        # ── Root layout (horizontal: left panel | right action buttons) ──
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Left side ──────────────────────────────────────────────────
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Render frame (ToolInputWidget lives here)
        self.render_frame = QFrame(self)
        self.render_frame.setObjectName("toolDetailPage_renderFrame")
        self.render_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        render_layout = QVBoxLayout(self.render_frame)
        render_layout.setContentsMargins(0, 0, 0, 0)
        render_layout.setSpacing(0)

        self.toolInputWidget = ToolInputWidget(
            name, tool_type, diameter, cutting_length, length, self.render_frame
        )
        self.toolInputWidget.dimension_changed.connect(self.on_dimension_changed)
        render_layout.addWidget(self.toolInputWidget)
        left_layout.addWidget(self.render_frame)

        # Bottom row: info form | description + offsets
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(6)

        # Info form frame
        self.info_frame = QFrame(self)
        self.info_frame.setObjectName("toolDetailPage_infoFrame")
        self.info_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        info_form = QFormLayout(self.info_frame)

        self.name_lineEdit = QLineEdit(str(name))
        self.name_lineEdit.setObjectName("toolDetailPage_nameLineEdit")
        self.name_lineEdit.setPlaceholderText("Name")
        info_form.addRow("Name", self.name_lineEdit)

        self.type_comboBox = QComboBox()
        self.type_comboBox.setObjectName("toolDetailPage_typeComboBox")
        self.type_comboBox.addItems(
            ["Endmill", "Radius Endmill", "Facemill", "Drill", "Threadmill", "Chamfermill"]
        )
        self.type_comboBox.setCurrentText(tool_type)
        info_form.addRow("Type", self.type_comboBox)

        self.diameter_lineEdit = QLineEdit(str(diameter))
        self.diameter_lineEdit.setObjectName("toolDetailPage_diameterLineEdit")
        self.diameter_lineEdit.setPlaceholderText("Tool Diameter")
        self.diameter_lineEdit.setAlignment(Qt.AlignCenter)
        info_form.addRow("Diameter", self.diameter_lineEdit)

        self.radius_lineEdit = QLineEdit(str(radius))
        self.radius_lineEdit.setObjectName("toolDetailPage_radiusLineEdit")
        self.radius_lineEdit.setPlaceholderText("Tool Radius")
        self.radius_lineEdit.setAlignment(Qt.AlignCenter)
        info_form.addRow("Radius", self.radius_lineEdit)

        self.cuttingLength_lineEdit = QLineEdit(str(cutting_length))
        self.cuttingLength_lineEdit.setObjectName("toolDetailPage_cuttingLengthLineEdit")
        self.cuttingLength_lineEdit.setPlaceholderText("Cutting Length")
        self.cuttingLength_lineEdit.setAlignment(Qt.AlignCenter)
        info_form.addRow("Cutting Length", self.cuttingLength_lineEdit)

        self.length_lineEdit = QLineEdit(str(length))
        self.length_lineEdit.setObjectName("toolDetailPage_lengthLineEdit")
        self.length_lineEdit.setPlaceholderText("Total Length")
        self.length_lineEdit.setAlignment(Qt.AlignCenter)
        info_form.addRow("Length", self.length_lineEdit)

        self.flutes_lineEdit = QLineEdit(str(flutes))
        self.flutes_lineEdit.setObjectName("toolDetailPage_flutesLineEdit")
        self.flutes_lineEdit.setPlaceholderText("Number of Flutes")
        self.flutes_lineEdit.setAlignment(Qt.AlignCenter)
        info_form.addRow("Flutes", self.flutes_lineEdit)

        self.supplier_lineEdit = QLineEdit(str(supplier))
        self.supplier_lineEdit.setObjectName("toolDetailPage_supplierLineEdit")
        self.supplier_lineEdit.setPlaceholderText("Name of Supplier")
        self.supplier_lineEdit.setAlignment(Qt.AlignCenter)
        info_form.addRow("Supplier", self.supplier_lineEdit)

        bottom_row.addWidget(self.info_frame)

        # Description + offsets frame
        self.description_frame = QFrame(self)
        self.description_frame.setObjectName("toolDetailPage_descriptionFrame")
        self.description_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        desc_layout = QVBoxLayout(self.description_frame)

        desc_layout.addWidget(QLabel("Description"))

        self.description_plainTextEdit = QPlainTextEdit()
        self.description_plainTextEdit.setObjectName("toolDetailPage_descriptionPlainTextEdit")
        self.description_plainTextEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.description_plainTextEdit.setPlainText(str(description))
        desc_layout.addWidget(self.description_plainTextEdit)

        offsets_form = QFormLayout()

        self.zOffset_lineEdit = QLineEdit(str(zOffset))
        self.zOffset_lineEdit.setObjectName("toolDetailPage_zOffsetLineEdit")
        self.zOffset_lineEdit.setPlaceholderText("Tool Z-Offset")
        self.zOffset_lineEdit.setAlignment(Qt.AlignCenter)
        offsets_form.addRow("Z-Offset", self.zOffset_lineEdit)

        self.rOffset_lineEdit = QLineEdit(str(rOffset))
        self.rOffset_lineEdit.setObjectName("toolDetailPage_rOffsetLineEdit")
        self.rOffset_lineEdit.setPlaceholderText("Radius Compensation")
        self.rOffset_lineEdit.setAlignment(Qt.AlignCenter)
        offsets_form.addRow("Radius Compensation", self.rOffset_lineEdit)

        desc_layout.addLayout(offsets_form)
        bottom_row.addWidget(self.description_frame)

        left_layout.addLayout(bottom_row)
        root_layout.addLayout(left_layout)

        # ── Right side: action buttons ──────────────────────────────────
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.save_button = QToolButton(self)
        self.save_button.setObjectName("toolDetailPage_saveButton")
        self.save_button.setMinimumSize(100, 100)
        self.save_button.setText("Save")
        make_touch_button(
            self.save_button,
            icon_path=str(ASSETS_DIR / "saveTool.svg"),
            clicked_icon_path=str(ASSETS_DIR / "saveTool_clicked.svg"),
        )
        right_layout.addWidget(self.save_button)

        self.delete_button = QToolButton(self)
        self.delete_button.setObjectName("toolDetailPage_deleteButton")
        self.delete_button.setMinimumSize(100, 100)
        self.delete_button.setText("Delete")
        make_touch_button(
            self.delete_button,
            icon_path=str(ASSETS_DIR / "deleteTool.svg"),
            clicked_icon_path=str(ASSETS_DIR / "deleteTool.svg"),
        )
        right_layout.addWidget(self.delete_button)

        spacer_btn = QPushButton(self)
        spacer_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_layout.addWidget(spacer_btn)

        root_layout.addLayout(right_layout)

        # ── Validators ─────────────────────────────────────────────────
        self.diameter_validator = QDoubleValidator(0.0, 100.0, 2, self)
        self.length_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.cuttingLength_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.flutes_validator = QIntValidator(0, 20, self)
        self.radius_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.zOffset_validator = QDoubleValidator(0.0, 250.0, 2, self)
        self.rOffset_validator = QDoubleValidator(0.0, 250.0, 2, self)

        # ── Signal connections ──────────────────────────────────────────
        self.save_button.pressed.connect(self.save_tool)
        self.delete_button.clicked.connect(self.confirm_delete)

        self.diameter_lineEdit.editingFinished.connect(
            lambda: self.validate_field(self.diameter_lineEdit, self.diameter_validator)
        )
        self.length_lineEdit.editingFinished.connect(
            lambda: self.validate_field(self.length_lineEdit, self.length_validator)
        )
        self.cuttingLength_lineEdit.editingFinished.connect(
            lambda: self.validate_field(self.cuttingLength_lineEdit, self.cuttingLength_validator)
        )
        self.flutes_lineEdit.editingFinished.connect(
            lambda: self.validate_field(self.flutes_lineEdit, self.flutes_validator)
        )
        self.radius_lineEdit.editingFinished.connect(
            lambda: self.validate_field(self.radius_lineEdit, self.radius_validator)
        )
        self.zOffset_lineEdit.editingFinished.connect(
            lambda: self.validate_field(self.zOffset_lineEdit, self.zOffset_validator)
        )
        self.rOffset_lineEdit.editingFinished.connect(
            lambda: self.validate_field(self.rOffset_lineEdit, self.rOffset_validator)
        )
        self.type_comboBox.currentTextChanged.connect(self.type_changed)

        for edit in [
            self.length_lineEdit, self.cuttingLength_lineEdit,
            self.diameter_lineEdit, self.radius_lineEdit,
        ]:
            edit.textChanged.connect(self.line_edit_changed)

    # ── Slots ────────────────────────────────────────────────────────────

    def validate_field(self, line_edit: QLineEdit, validator) -> None:
        text = line_edit.text()
        state = validator.validate(text, 0)[0]
        if state != QDoubleValidator.Acceptable:
            line_edit.setStyleSheet("border: 1px solid red;")
        else:
            line_edit.setStyleSheet("border: 1px solid #2E3440;")

    def line_edit_changed(self) -> None:
        if self._updating_lineedits:
            return
        self.toolInputWidget.draw_tool(
            self.type_comboBox.currentText(),
            diameter=self.diameter_lineEdit.text(),
            length=self.length_lineEdit.text(),
            cutting_length=self.cuttingLength_lineEdit.text(),
            radius=self.radius_lineEdit.text(),
        )

    def on_dimension_changed(self, dim_id: str, value: float) -> None:
        self._updating_lineedits = True
        if dim_id == "length":
            self.length_lineEdit.setText(str(value))
        elif dim_id == "cutting_length":
            self.cuttingLength_lineEdit.setText(str(value))
        elif dim_id == "diameter":
            self.diameter_lineEdit.setText(str(value))
        self._updating_lineedits = False

    def type_changed(self, tool_type: str) -> None:
        if tool_type == "Endmill":
            self.radius_lineEdit.setEnabled(False)
        else:
            self.radius_lineEdit.setEnabled(True)
        self.toolInputWidget.draw_tool(tool_type)

    def save_tool(self) -> None:
        """Save the current tool to the database (insert or update)."""
        name = self.name_lineEdit.text()
        tool_type = self.type_comboBox.currentText()
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

        self.database.save_tool(
            self.tool_id, name, tool_type, diameter, radius,
            length, cutting_length, flutes, zOffset, rOffset,
            supplier, description,
        )
        self.tool_saved.emit()

    def confirm_delete(self) -> None:
        name = self.name_lineEdit.text()
        msg = QMessageBox(self)
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

    def delete_tool(self, tool_id: int) -> None:
        self.database.delete_tool(tool_id)
        self.tool_deleted.emit()

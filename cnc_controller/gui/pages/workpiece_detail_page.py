from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPlainTextEdit,
    QSizePolicy, QToolButton, QVBoxLayout, QWidget,
)

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
    Shows workpiece metadata and lists associated G-code files.
    """

    def __init__(self, parent=None, workpiece: Workpiece | None = None):
        super().__init__(parent)

        self.workpiece = workpiece

        # ---- Root layout ----
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(9, 9, 9, 9)
        root_layout.setSpacing(6)

        # ---- Header row: name button + delete button ----
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        self.name_label = QToolButton(self)
        self.name_label.setObjectName("workpieceDetailPage_nameButton")
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.name_label.setText(self.workpiece.name if self.workpiece else "")
        header_layout.addWidget(self.name_label)

        self.delete_button = QToolButton(self)
        self.delete_button.setObjectName("workpieceDetailPage_deleteProjectButton")
        self.delete_button.setMinimumSize(100, 100)
        self.delete_button.setText("Delete")
        header_layout.addWidget(self.delete_button)

        root_layout.addLayout(header_layout)

        # ---- Middle row: description ----
        middle_layout = QHBoxLayout()

        self.description_frame = QFrame(self)
        self.description_frame.setObjectName("workpieceDetailPage_descriptionFrame")
        self.description_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        desc_layout = QVBoxLayout(self.description_frame)
        self.description_edit = QPlainTextEdit(self.description_frame)
        self.description_edit.setObjectName("workpieceDetailPage_descriptionTextEdit")
        desc_layout.addWidget(self.description_edit)
        middle_layout.addWidget(self.description_frame)

        root_layout.addLayout(middle_layout)

        # ---- File browser ----
        self.files_placeholder = QFrame(self)
        self.files_placeholder.setObjectName("files_placeholderFrame")
        self.files_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.filesBrowser = ScrollWidget()
        placeholder_layout = QVBoxLayout(self.files_placeholder)
        placeholder_layout.setContentsMargins(0, 0, 0, 0)
        placeholder_layout.addWidget(self.filesBrowser)

        root_layout.addWidget(self.files_placeholder)

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
            placeholder.setStyleSheet("color: #AAB2C5; font-size: 16px;")
            self.filesBrowser.objects_layout.addWidget(placeholder)
            return

        self.filesBrowser.load_objects(files_frame)

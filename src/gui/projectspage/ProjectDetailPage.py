from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QToolButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtGui import QIcon
from pathlib import Path

from database.project_model import Project


class ProjectDetailPage(QWidget):
    """
    Rudimentäre Detailseite für ein Projekt.
    Lädt das .ui-File und zeigt Basisinformationen aus dem Projektobjekt.
    """

    def __init__(self, parent=None, project: Project | None = None):
        super().__init__(parent)

        self.project = project

        # 🔹 UI-Datei laden
        loader = QUiLoader()
        ui_path = Path(__file__).parent / "ProjectDetailPage.ui"
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise IOError(f"Cannot open {ui_path}")
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Layout setzen (damit QWidget korrekt dargestellt wird)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.name_label = self.ui.findChild(QToolButton, "projectDetailPage_nameButton")
        self.name_label.setText(self.project.name)

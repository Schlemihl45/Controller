from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolButton,
    QLabel,
    QFrame,
    QHBoxLayout
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtGui import QIcon

from PySide6.QtCore import Signal

from gui.scrollWidget import ScrollWidget
from database.databaseManager import Database
from database.project_model import Project


class ProjectFrame(QFrame):
    """Ein einzelnes Projekt als klickbarer Frame."""

    openProjectDetails = Signal(Project)

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        print(project)

        self.setStyleSheet("""
            QFrame {
                background-color: #1c314d;
                border-radius: 8px;
                border: 1px solid #2E3440;
            }
            QLabel {
                color: #E6E6E6;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        icon_path = QIcon("../assets/file-3d.svg")
        icon = QToolButton(self)
        icon.setIcon(icon_path)
        icon.setStyleSheet("border: none;")
        icon.setIconSize(QSize(48, 48))
        layout.addWidget(icon)
        icon.setEnabled(False)

        lbl_name = QLabel(project.name)
        lbl_name.setStyleSheet("color: #E6E6E6; font-size: 24px; font-weight: bold; border: none;")

        open_btn = QToolButton()
        open_btn.setText("...")
        open_btn.setStyleSheet("background-color: #34455f;")
        open_btn.setFixedSize(QSize(64, 64))
        open_btn.clicked.connect(lambda: self.openProjectDetails.emit(self.project))

        layout.addWidget(lbl_name)
        layout.addStretch()
        layout.addWidget(open_btn)

class ProjectsPage(QWidget):
    """
    ProjectsPage for the CNC Controller GUI.
    """
    openProjectDetails = Signal(Project)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.repo = Database()

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Button Layout
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 9)
        self.buttons_layout.setSpacing(6)

        self.addProjectButton = QToolButton(self)
        self.addProjectButton.setIcon(QIcon("../assets/addTool.svg"))
        self.addProjectButton.setIconSize(QSize(48, 48))
        self.addProjectButton.setStyleSheet("background-color: #1c314d;")
        self.addProjectButton.setIconSize(QSize(48, 48))

        self.buttons_layout.addWidget(self.addProjectButton)

        self.spacer = QToolButton(self)
        self.spacer.setStyleSheet("background-color: #1c314d;")
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.buttons_layout.addWidget(self.spacer)

        self.main_layout.addLayout(self.buttons_layout)

        # Scroll area
        self.scroll_widget = ScrollWidget()
        self.main_layout.addWidget(self.scroll_widget)

        # Initial load
        self.load_projects()

    def load_projects(self):

        self.repo.initialize()
        self.repo.sync_with_filesystem()

        projects = self.repo.load_projects(order_by="name")

        frames = []
        for project in projects:
            frame = ProjectFrame(project, self.scroll_widget)
            frame.openProjectDetails.connect(self.openProjectDetails.emit)
            frames.append(frame)

        self.scroll_widget.load_objects(frames)

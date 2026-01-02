# gui/pages/tools_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from gui.scrollWidget import ScrollWidget


class ProjectsPage(QWidget):
    """
    ToolsPage for the CNC Controller GUI.

    Contains a ScrollWidget where tool buttons or other widgets can be added.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout for this page
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Scroll area
        self.scroll_widget = ScrollWidget()
        self.main_layout.addWidget(self.scroll_widget)

        # For testing: add 2 example buttons
        self.add_test_buttons()

    def add_test_buttons(self):
        """
        Adds a few placeholder buttons to the scroll area.
        Replace or extend this function to add real tool buttons.
        """
        for i in range(20):
            btn = QPushButton(f"Project {i+1}")
            btn.setMinimumHeight(50)
            self.scroll_widget.objects_layout.addWidget(btn)

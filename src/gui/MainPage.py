import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from pathlib import Path

class MainPage(QMainWindow):
    """
    This is the main page of the application.
    """
    def __init__(self):
        super().__init__()

        loader = QUiLoader()

        ui_path = Path(__file__).parent / "MainPage.ui"
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise IOError(f"Cannot open {ui_path}")
        self.loaded_ui = loader.load(ui_file)
        ui_file.close()

        self.setCentralWidget(self.loaded_ui)
        self.setWindowTitle("Controller")
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication

from database.db_manager import Database
from gui.main_page import MainPage


def main():
    """
    Main entry point of the CNC Controller application.
    Initializes database, creates the QApplication, sets stylesheet, and launches the MainPage.
    """
    # Initialize database
    database = Database()
    database.initialize()

    # Create Qt Application
    app = QApplication(sys.argv)

    # Load main window
    window = MainPage()

    # Load stylesheet
    qss_path = Path(__file__).parent.parent / "themes" / "stylesheet.qss"
    if qss_path.exists():
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Stylesheet not found at {qss_path}")

    # Show main window
    window.show()

    # Execute application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

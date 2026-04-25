import sys
from pathlib import Path

# Ensure cnc_controller/ is on the path regardless of working directory
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from gui.main_page import MainPage
from database.db_manager import Database


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

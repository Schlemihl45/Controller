import sys
import sqlite3
from pathlib import Path
from PySide6.QtWidgets import QApplication
from gui.MainPage import MainPage

from database.databaseManager import Database

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
    qss_path = Path(__file__).parent / "gui" / "stylesheet.qss"
    if qss_path.exists():
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Stylesheet not found at {qss_path}")

    # Print current working directory for debugging
    import os
    print("Current Working Directory:", os.getcwd())

    # Show main window
    window.show()

    # Execute application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

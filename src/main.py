import sys
import sqlite3
from pathlib import Path
from PySide6.QtWidgets import QApplication
from gui.MainPage import MainPage

# Database file path
DB_PATH = Path(__file__).parent / "database.db"


def init_db():
    """
    Initialize the SQLite database and create tables if they do not exist.
    Tables:
        - tools: Tool information for the CNC
        - projects: Projects containing multiple files
        - files: Files associated with projects, can store metadata
        - workpieces: Workpiece data linked to files or projects
    """
    if not DB_PATH.exists():
        print(f"Database not found, creating new DB at {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create tools table
        cursor.execute("""
        CREATE TABLE tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            diameter REAL,
            cutting_length REAL,
            length REAL,
            flutes INTEGER NOT NULL,
            time_used REAL,
            last_used DATETIME
        )
        """)

        conn.commit()
        conn.close()
        print("Database initialized successfully.")

    else:
        print(f"Database already exists at {DB_PATH}")


def main():
    """
    Main entry point of the CNC Controller application.
    Initializes database, creates the QApplication, sets stylesheet, and launches the MainPage.
    """
    # Initialize database
    init_db()

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

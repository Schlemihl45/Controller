import sys
from PySide6.QtWidgets import QApplication
from gui.MainPage import MainPage

def main():
    app = QApplication(sys.argv)
    window = MainPage()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
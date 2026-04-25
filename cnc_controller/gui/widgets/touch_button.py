from PySide6.QtWidgets import QPushButton, QToolButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QTimer

def make_touch_button(
    button: QPushButton,
    icon_path: str,
    clicked_icon_path: str,
    border_normal: str = "#3A4F74",
    border_pressed: str = "orange"
):
    """
    Macht einen Button touch-kompatibel mit kurzem visuellem Feedback.
    Verhindert Bildschirm-Wackeln durch konstante Rahmenbreite.
    """

    # Grunddesign einmalig setzen
    button.setIcon(QIcon(icon_path))
    button.setIconSize(QSize(64, 64))
    button.setStyleSheet(f"""
        border: 1px solid {border_normal};
        border-radius: 6px;
        background-color: #1c314d;
        transition: all 0.1s ease-in-out; /* sanfter Übergang */
    """)

    def on_click():
        """Kurzer visueller Effekt beim Tippen/Klicken."""
        # Icon wechseln + Farbe anpassen (aber gleiche Rahmenbreite!)
        button.setIcon(QIcon(clicked_icon_path))
        button.setStyleSheet(f"""
            border: 1px solid {border_pressed};   /* gleiche Breite! */
            border-radius: 6px;
            background-color: #1c314d;
            transition: all 0.1s ease-in-out;
        """)

        # Nach kurzer Zeit zurücksetzen (kein Flackern)
        QTimer.singleShot(150, reset_style)

    def reset_style():
        """Zurück zum normalen Stil."""
        button.setIcon(QIcon(icon_path))
        button.setStyleSheet(f"""
            border: 1px solid {border_normal};
            border-radius: 6px;
            background-color: #1c314d;
            transition: all 0.1s ease-in-out;
        """)

    # Einheitlich auf Klick reagieren (funktioniert bei Maus & Touch)
    button.clicked.connect(on_click)

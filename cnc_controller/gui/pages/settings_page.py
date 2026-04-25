"""
SettingsPage — application and machine configuration.

Planned content:
- Network / LinuxCNC connection settings
- Unit system (mm / inch)
- Display preferences
- User accounts / PIN protection
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal


class SettingsPage(QWidget):
    """Placeholder for the settings page."""

    # Signals this page will eventually emit
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E6E6E6;")
        layout.addWidget(title)

        placeholder = QFrame(self)
        placeholder.setObjectName("settingsPage_contentFrame")
        placeholder.setStyleSheet("background-color: #1c314d; border-radius: 8px;")
        layout.addWidget(placeholder, stretch=1)

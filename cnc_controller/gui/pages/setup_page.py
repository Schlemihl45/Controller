"""
SetupPage — machine homing, tool offsets, and work-coordinate setup.

Planned content:
- Homing controls (home all axes, individual axis)
- Tool length measurement
- Work-coordinate origin setting (G54–G59)
- Fixture offset table
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal


class SetupPage(QWidget):
    """Placeholder for the machine setup page."""

    # Signals this page will eventually emit
    homing_requested = Signal()
    wcs_changed = Signal(int)  # Work-coordinate system number

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("Setup")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E6E6E6;")
        layout.addWidget(title)

        placeholder = QFrame(self)
        placeholder.setObjectName("setupPage_contentFrame")
        placeholder.setStyleSheet("background-color: #1c314d; border-radius: 8px;")
        layout.addWidget(placeholder, stretch=1)

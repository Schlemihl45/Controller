"""
StatisticsPage — machining history, tool wear, and runtime analytics.

Planned content:
- Total machine runtime
- Per-tool usage time and wear indicator
- Workpiece completion rate (from Kanban data)
- Alarm / error history log
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal


class StatisticsPage(QWidget):
    """Placeholder for the statistics and analytics page."""

    # Signals this page will eventually emit
    export_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("Statistics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E6E6E6;")
        layout.addWidget(title)

        placeholder = QFrame(self)
        placeholder.setObjectName("statisticsPage_contentFrame")
        placeholder.setStyleSheet("background-color: #1c314d; border-radius: 8px;")
        layout.addWidget(placeholder, stretch=1)

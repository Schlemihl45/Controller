from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame, QScroller
from PySide6.QtCore import Qt, Signal
from pathlib import Path
from PySide6.QtWidgets import QSizePolicy

class ScrollWidget(QWidget):
    """
    Vertical scroll widget for touch input.

    Functions:
        - Adding a Widget to the scroll area
        - Deleting a Widget from the scroll area
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # ScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        QScroller.grabGesture(scroll_area.viewport(), QScroller.TouchGesture)

        # Content Widget
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.objects_layout = QVBoxLayout(self.content_widget)
        self.objects_layout.setContentsMargins(0, 0, 0, 0)
        self.objects_layout.setSpacing(6)

        scroll_area.setWidget(self.content_widget)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        main_layout.setSpacing(0)

        self.setStyleSheet("background-color:transparent;")

    def load_objects(self, widgets: list[QWidget]):
        self.delete_objects()
        for w in widgets:
            self.objects_layout.addWidget(w)
        self.objects_layout.addStretch()

    def delete_objects(self):
        while self.objects_layout.count():
            item = self.objects_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)




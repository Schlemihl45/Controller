from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QScroller

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QLinearGradient, QColor


class FadeOverlay(QWidget):
    """Zeichnet einen transparenten Farbverlauf für oben oder unten."""

    def __init__(self, position: str = "top", color=QColor("#1e2633"), parent=None):
        super().__init__(parent)
        self.position = position
        self.color = color
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.position == "top":
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0.0, self.color)
            gradient.setColorAt(1.0, QColor(self.color.red(),
                                             self.color.green(),
                                             self.color.blue(), 0))
        else:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0.0, QColor(self.color.red(),
                                             self.color.green(),
                                             self.color.blue(), 0))
            gradient.setColorAt(1.0, self.color)

        painter.fillRect(self.rect(), gradient)

class ScrollWidget(QWidget):
    """
    Vertical scroll widget for touch input with top/bottom fade overlays.
    """

    FADE_HEIGHT = 24

    def __init__(self, parent=None):
        super().__init__(parent)

        # ScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        QScroller.grabGesture(self.scroll_area.viewport(), QScroller.TouchGesture)

        # Content Widget
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.objects_layout = QVBoxLayout(self.content_widget)
        self.objects_layout.setContentsMargins(0, 0, 0, 0)
        self.objects_layout.setSpacing(6)

        self.scroll_area.setWidget(self.content_widget)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.scroll_area)

        # Fade overlays
        self.fade_top = FadeOverlay("top", parent=self)
        self.fade_bottom = FadeOverlay("bottom", parent=self)

        self.fade_top.setFixedHeight(self.FADE_HEIGHT)
        self.fade_bottom.setFixedHeight(self.FADE_HEIGHT)

        self.setStyleSheet("background-color: transparent;")

    def resizeEvent(self, event):
        """Positioniert die Fades korrekt."""
        w = self.width()
        h = self.height()

        self.fade_top.setGeometry(0, 0, w, self.FADE_HEIGHT)
        self.fade_bottom.setGeometry(0, h - self.FADE_HEIGHT, w, self.FADE_HEIGHT)

        super().resizeEvent(event)

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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScroller
from PySide6.QtGui import QPainter, QLinearGradient, QColor


class FadeOverlay(QWidget):
    """Zeichnet einen transparenten Farbverlauf für oben oder unten."""

    def __init__(self, position: str = "top", color=QColor("#1e2633"), parent=None):
        super().__init__(parent)
        self.position = position
        self.color = color
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def set_color(self, color: QColor):
        """Farbe dynamisch ändern."""
        self.color = color
        self.update()

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
    FADE_HEIGHT = 24

    def __init__(self, parent=None, scroll_active=True, fade=True, fade_color=QColor("#1e2633")):
        super().__init__(parent)

        # ScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._scroll_enabled = True
        self._scroller_target = self.scroll_area.viewport()
        QScroller.grabGesture(self._scroller_target, QScroller.TouchGesture)

        # Content Widget
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.objects_layout = QVBoxLayout(self.content_widget)
        self.objects_layout.setContentsMargins(0, 0, 0, 0)
        self.objects_layout.setSpacing(6)
        self.objects_layout.setAlignment(Qt.AlignTop)  # WICHTIG: immer top

        self.scroll_area.setWidget(self.content_widget)

        # Dummy-Stretch am Ende
        self._bottom_stretch = QWidget()
        self._bottom_stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.objects_layout.addWidget(self._bottom_stretch)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.scroll_area)

        # Fade overlays
        self.fade_enabled = fade
        self.fade_color = fade_color
        self.fade_top = None
        self.fade_bottom = None
        if self.fade_enabled:
            self._create_fades()
            # Scrollbar überwachen
            self.scroll_area.verticalScrollBar().valueChanged.connect(self._update_fade_visibility)

        self.setStyleSheet("background-color: transparent;")

    def _create_fades(self):
        """Fades erzeugen."""
        self.fade_top = FadeOverlay("top", self.fade_color, parent=self)
        self.fade_bottom = FadeOverlay("bottom", self.fade_color, parent=self)
        self.fade_top.setFixedHeight(self.FADE_HEIGHT)
        self.fade_bottom.setFixedHeight(self.FADE_HEIGHT)
        self.fade_top.show()
        self.fade_bottom.show()
        self._update_fade_visibility()  # initial

    def _update_fade_visibility(self):
        """Fades nur anzeigen, wenn noch Scrollbewegung in die Richtung möglich."""
        if not self.fade_enabled or not self.fade_top or not self.fade_bottom:
            return

        scrollbar = self.scroll_area.verticalScrollBar()
        max_val = scrollbar.maximum()
        current_val = scrollbar.value()

        self.fade_top.setVisible(current_val > 0)
        self.fade_bottom.setVisible(current_val < max_val)

    def set_fade_enabled(self, enabled: bool):
        """Fade ein-/ausschalten."""
        if enabled and not self.fade_enabled:
            self.fade_enabled = True
            self._create_fades()
            self.scroll_area.verticalScrollBar().valueChanged.connect(self._update_fade_visibility)
        elif not enabled and self.fade_enabled:
            self.fade_enabled = False
            if self.fade_top:
                self.fade_top.hide()
            if self.fade_bottom:
                self.fade_bottom.hide()

    def set_fade_color(self, color: QColor):
        """Fade-Farbe ändern."""
        self.fade_color = color
        if self.fade_top:
            self.fade_top.set_color(color)
        if self.fade_bottom:
            self.fade_bottom.set_color(color)

    def resizeEvent(self, event):
        """Positioniert die Fades korrekt."""
        w = self.width()
        h = self.height()
        if self.fade_top and self.fade_bottom:
            self.fade_top.setGeometry(0, 0, w, self.FADE_HEIGHT)
            self.fade_bottom.setGeometry(0, h - self.FADE_HEIGHT, w, self.FADE_HEIGHT)
        super().resizeEvent(event)

    def load_objects(self, widgets: list[QWidget]):
        self.delete_objects()
        for w in widgets:
            self.objects_layout.addWidget(w)
        self.objects_layout.addStretch()
        self._update_fade_visibility()

    def delete_objects(self):
        while self.objects_layout.count():
            item = self.objects_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self._update_fade_visibility()

    def add_widget(self, widget: QWidget):
        """Fügt Widget **vor dem Dummy-Stretch** ein, damit es oben bleibt."""
        self.objects_layout.insertWidget(self.objects_layout.count() - 1, widget)
        self._update_fade_visibility()

    def set_scroll_enabled(self, enabled: bool):
        if self._scroll_enabled == enabled:
            return

        self._scroll_enabled = enabled

        if enabled:
            QScroller.grabGesture(self._scroller_target, QScroller.TouchGesture)
        else:
            QScroller.ungrabGesture(self._scroller_target)

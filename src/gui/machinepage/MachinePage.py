from PySide6.QtWidgets import QWidget, QPushButton, QStackedWidget, QToolButton, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QEvent
from pathlib import Path


class MachinePage(QWidget):
    """
    Grundlegende Seite zur Maschinensteuerung.
    Lädt nur das zugehörige .ui-Layout.
    """

    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        ui_path = Path(__file__).parent / "MachinePage.ui"
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise IOError(f"Cannot open {ui_path}")

        self.ui = loader.load(ui_file, self)  # pass self as parent
        ui_file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # remove margins
        layout.setSpacing(0)
        layout.addWidget(self.ui)

        """
        Find all functional widgets
        """

        # Manual mode button
        self.manual_mode_button = self.ui.findChild(QToolButton, "manual_mode_button")
        self.manual_mode_button.clicked.connect(lambda: self.switch_mode("manual"))

        # Auto mode button
        self.auto_mode_button = self.ui.findChild(QToolButton, "auto_mode_button")
        self.auto_mode_button.clicked.connect(lambda: self.switch_mode("auto"))

        # Stacked widget(s)
        self.mode_stackedWidget = self.ui.findChild(QStackedWidget, "machinePage_modeStackedWidget")
        self.manual_widget = self.ui.findChild(QWidget, "manualPage")
        self.auto_widget = self.ui.findChild(QWidget, "autoPage")

        self.mode_stackedWidget.setCurrentWidget(self.manual_widget)

        self._swipe_start_x = None
        for child in self.ui.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self._swipe_start_x = event.pos().x()
        elif event.type() == QEvent.MouseButtonRelease and self._swipe_start_x is not None:
            delta_x = event.pos().x() - self._swipe_start_x
            threshold = 100
            if delta_x > threshold:
                self.switch_mode("manual")
            elif delta_x < -threshold:
                self.switch_mode("auto")
            self._swipe_start_x = None
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._swipe_start_x = event.pos().x()

    def mouseReleaseEvent(self, event):
        if self._swipe_start_x is None:
            return

        delta_x = event.pos().x() - self._swipe_start_x
        threshold = 5000  # Pixel-Schwelle für echten Wisch

        if delta_x > threshold:
            # Wisch nach rechts → Manual Mode
            self.switch_mode("manual")
        elif delta_x < -threshold:
            # Wisch nach links → Auto Mode
            self.switch_mode("auto")

        self._swipe_start_x = None


    # Switching between the mode-pages
    def switch_mode(self, mode: str):
        if mode == "manual":
            if self.manual_mode_button:
                self.manual_mode_button.setChecked(True)
                self.auto_mode_button.setChecked(False)

                self.manual_mode_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self.auto_mode_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            if self.manual_widget:
                self.mode_stackedWidget.setCurrentWidget(self.manual_widget)
        elif mode == "auto":
            if self.auto_mode_button:
                self.auto_mode_button.setChecked(True)
                self.auto_mode_button.setChecked(False)

                self.manual_mode_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                self.auto_mode_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            if self.auto_widget:
                   self.mode_stackedWidget.setCurrentWidget(self.auto_widget)
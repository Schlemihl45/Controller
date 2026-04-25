from pathlib import Path

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QPushButton,
    QSizePolicy, QStackedWidget, QToolButton, QVBoxLayout, QWidget,
)


class MachinePage(QWidget):
    """Machine control page with Manual and Auto mode tabs."""

    def __init__(self):
        super().__init__()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---- Mode selector buttons ----
        mode_bar = QHBoxLayout()
        mode_bar.setSpacing(0)

        self.manual_mode_button = QToolButton(self)
        self.manual_mode_button.setObjectName("manual_mode_button")
        self.manual_mode_button.setText("Manual")
        self.manual_mode_button.setCheckable(True)
        self.manual_mode_button.setChecked(True)
        self.manual_mode_button.setAutoExclusive(True)
        self.manual_mode_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        mode_bar.addWidget(self.manual_mode_button)

        self.auto_mode_button = QToolButton(self)
        self.auto_mode_button.setObjectName("auto_mode_button")
        self.auto_mode_button.setText("AUTO")
        self.auto_mode_button.setCheckable(True)
        self.auto_mode_button.setAutoExclusive(True)
        self.auto_mode_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        mode_bar.addWidget(self.auto_mode_button)

        root_layout.addLayout(mode_bar)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        root_layout.addWidget(line)

        # ---- Mode stacked widget ----
        self.mode_stackedWidget = QStackedWidget(self)
        self.mode_stackedWidget.setObjectName("machinePage_modeStackedWidget")
        self.mode_stackedWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Manual page
        self.manual_widget = QWidget()
        self.manual_widget.setObjectName("manualPage")
        manual_layout = QVBoxLayout(self.manual_widget)

        self.manual_jogFrame = QFrame(self.manual_widget)
        self.manual_jogFrame.setObjectName("manual_jogFrame")
        jog_grid = QGridLayout(self.manual_jogFrame)
        jog_buttons = [
            (0, 0, "Diag"), (0, 1, "Y +"),  (0, 2, "Diag"), (0, 4, "Z +"),
            (1, 0, "X -"),  (1, 1, "RAPID"), (1, 2, "X +"),  (1, 4, ""),
            (2, 0, "Diag"), (2, 1, "Y -"),   (2, 2, "Diag"), (2, 4, "Z -"),
        ]
        for row, col, label in jog_buttons:
            btn = QPushButton(label, self.manual_jogFrame)
            btn.setMinimumSize(100, 100)
            jog_grid.addWidget(btn, row, col)
        manual_layout.addWidget(self.manual_jogFrame)

        self.manual_mdiFrame = QFrame(self.manual_widget)
        self.manual_mdiFrame.setObjectName("manual_mdiFrame")
        self.manual_mdiFrame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        mdi_layout = QVBoxLayout(self.manual_mdiFrame)
        mdi_btn = QPushButton("MDI", self.manual_mdiFrame)
        mdi_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        mdi_layout.addWidget(mdi_btn)
        manual_layout.addWidget(self.manual_mdiFrame)

        # Auto page
        self.auto_widget = QWidget()
        self.auto_widget.setObjectName("autoPage")
        auto_layout = QVBoxLayout(self.auto_widget)
        self.autoPage_codeFrame = QFrame(self.auto_widget)
        self.autoPage_codeFrame.setObjectName("autoPage_codeFrame")
        auto_layout.addWidget(self.autoPage_codeFrame)

        self.mode_stackedWidget.addWidget(self.manual_widget)
        self.mode_stackedWidget.addWidget(self.auto_widget)
        self.mode_stackedWidget.setCurrentWidget(self.manual_widget)
        root_layout.addWidget(self.mode_stackedWidget)

        # ---- Swipe state ----
        self._swipe_start_x = None
        for child in self.findChildren(QWidget):
            child.installEventFilter(self)

        # ---- Signal connections ----
        self.manual_mode_button.clicked.connect(lambda: self.switch_mode("manual"))
        self.auto_mode_button.clicked.connect(lambda: self.switch_mode("auto"))

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

    def switch_mode(self, mode: str):
        if mode == "manual":
            self.manual_mode_button.setChecked(True)
            self.auto_mode_button.setChecked(False)
            self.manual_mode_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.auto_mode_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.mode_stackedWidget.setCurrentWidget(self.manual_widget)
        elif mode == "auto":
            self.auto_mode_button.setChecked(True)
            self.manual_mode_button.setChecked(False)
            self.manual_mode_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.auto_mode_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.mode_stackedWidget.setCurrentWidget(self.auto_widget)

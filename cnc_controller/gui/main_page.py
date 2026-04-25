from pathlib import Path

from PySide6.QtCore import Qt, QTime, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QToolButton, QVBoxLayout, QWidget,
)

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"

from gui.widgets.touch_button import make_touch_button
from gui.pages.machine_page import MachinePage
from gui.pages.tool_detail_page import ToolDetailPage
from gui.pages.tools_page import ToolsPage
from gui.pages.workpiece_detail_page import WorkpieceDetailPage
from gui.pages.workpieces_page import WorkpiecesPage


class MainPage(QMainWindow):
    """Main window of the CNC Controller application."""

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(str(ASSETS_DIR / "logo.svg")))
        self.setWindowTitle("Controller")
        self.resize(700, 950)

        # ── Central widget ──────────────────────────────────────────────
        central = QWidget(self)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(9, 0, 9, 0)
        root_layout.setSpacing(0)

        # ── Status frame ────────────────────────────────────────────────
        status_frame = QFrame(central)
        status_frame.setObjectName("statusFrame")
        status_frame.setFrameShape(QFrame.StyledPanel)
        status_frame.setFrameShadow(QFrame.Raised)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(9, 9, 9, 9)

        self.status_LED = QFrame(status_frame)
        self.status_LED.setObjectName("statusFrame_LED")
        self.status_LED.setFixedSize(16, 16)
        self.status_LED.setFrameShape(QFrame.StyledPanel)
        self.status_LED.setFrameShadow(QFrame.Raised)
        status_layout.addWidget(self.status_LED)

        self.status_output = QLabel("IDLE", status_frame)
        self.status_output.setObjectName("statusFrame_output")
        status_layout.addWidget(self.status_output)

        status_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        self.status_time = QLabel("00:00:00", status_frame)
        self.status_time.setObjectName("statusFrame_time")
        status_layout.addWidget(self.status_time)

        root_layout.addWidget(status_frame)

        # ── Top frame ───────────────────────────────────────────────────
        top_frame = QFrame(central)
        top_frame.setObjectName("topFrame")
        top_frame.setFrameShape(QFrame.StyledPanel)
        top_frame.setFrameShadow(QFrame.Raised)
        top_frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        top_grid = QGridLayout(top_frame)
        top_grid.setContentsMargins(0, 0, 0, 0)

        # Position frame ── col 0
        pos_frame = QFrame(top_frame)
        pos_frame.setObjectName("topFrame_positionFrame")
        pos_frame.setFrameShape(QFrame.StyledPanel)
        pos_frame.setFrameShadow(QFrame.Raised)
        pos_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        pos_grid = QGridLayout(pos_frame)
        pos_grid.setContentsMargins(0, 9, 0, 0)

        rv = Qt.AlignRight | Qt.AlignVCenter

        pos_grid.addWidget(
            QLabel("Axis Position", alignment=Qt.AlignBottom | Qt.AlignHCenter), 0, 2
        )
        pos_grid.addWidget(
            QLabel("Remaining Path", alignment=Qt.AlignBottom | Qt.AlignHCenter), 0, 3
        )

        for row, axis in enumerate(("X", "Y", "Z"), start=1):
            pos_grid.addWidget(QLabel(axis, alignment=rv), row, 0)
            icon_btn = QPushButton("", pos_frame)
            icon_btn.setFlat(True)
            pos_grid.addWidget(icon_btn, row, 1)

        self.position_x = QLabel("0.00", pos_frame)
        self.position_x.setObjectName("positionFrame_xCoordinate")
        self.position_x.setAlignment(rv)
        pos_grid.addWidget(self.position_x, 1, 2)
        pos_grid.addWidget(QLabel("0.00", alignment=rv), 1, 3)

        self.position_y = QLabel("0.00", pos_frame)
        self.position_y.setObjectName("positionFrame_yCoordinate")
        self.position_y.setAlignment(rv)
        pos_grid.addWidget(self.position_y, 2, 2)
        pos_grid.addWidget(QLabel("0.00", alignment=rv), 2, 3)

        self.position_z = QLabel("0.00", pos_frame)
        self.position_z.setObjectName("positionFrame_zCoordinate")
        self.position_z.setAlignment(rv)
        pos_grid.addWidget(self.position_z, 3, 2)
        pos_grid.addWidget(QLabel("0.00", alignment=rv), 3, 3)

        top_grid.addWidget(pos_frame, 3, 0)

        # Spindle + feedrate column ── col 1
        sf_col = QVBoxLayout()

        spindle_frame = QFrame(top_frame)
        spindle_frame.setObjectName("topFrame_spindleFrame")
        spindle_frame.setFrameShape(QFrame.StyledPanel)
        spindle_frame.setFrameShadow(QFrame.Raised)
        spindle_frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        spindle_layout = QHBoxLayout(spindle_frame)

        spindle_icon = QPushButton("", spindle_frame)
        spindle_icon.setObjectName("spindleFrame_spindleIcon")
        spindle_layout.addWidget(spindle_icon)

        spindle_info = QVBoxLayout()
        spindle_info.setSpacing(6)
        spindle_info.setContentsMargins(0, 10, 0, 10)

        rpm_row = QHBoxLayout()
        self.spindle_rpm = QLabel("0", spindle_frame)
        self.spindle_rpm.setObjectName("spindleFrame_rpm")
        self.spindle_rpm.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rpm_row.addWidget(self.spindle_rpm)
        rpm_row.addWidget(QLabel("1/min", spindle_frame))
        spindle_info.addLayout(rpm_row)

        load_row = QHBoxLayout()
        self.spindleFrame_load_bar = QProgressBar(spindle_frame)
        self.spindleFrame_load_bar.setObjectName("spindleFrame_loadBar")
        self.spindleFrame_load_bar.setMaximumHeight(4)
        self.spindleFrame_load_bar.setMaximum(150)
        self.spindleFrame_load_bar.setValue(0)
        self.spindleFrame_load_bar.setTextVisible(False)
        load_row.addWidget(self.spindleFrame_load_bar)
        self.spindleFrame_load_value = QLabel("0 %", spindle_frame)
        self.spindleFrame_load_value.setObjectName("spindleFrame_loadValue")
        load_row.addWidget(self.spindleFrame_load_value)
        spindle_info.addLayout(load_row)

        spindle_layout.addLayout(spindle_info)
        sf_col.addWidget(spindle_frame)

        feedrate_frame = QFrame(top_frame)
        feedrate_frame.setObjectName("topFrame_feedrateFrame")
        feedrate_frame.setFrameShape(QFrame.StyledPanel)
        feedrate_frame.setFrameShadow(QFrame.Raised)
        feedrate_frame.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        feedrate_layout = QHBoxLayout(feedrate_frame)

        feedrate_icon = QPushButton("", feedrate_frame)
        feedrate_icon.setObjectName("feedrateFrame_feedrateIcon")
        feedrate_icon.setFlat(True)
        feedrate_layout.addWidget(feedrate_icon)

        self.feedrate_value = QLabel("0", feedrate_frame)
        self.feedrate_value.setObjectName("feedrateFrame_feedrate")
        self.feedrate_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        feedrate_layout.addWidget(self.feedrate_value)
        feedrate_layout.addWidget(QLabel("mm/min", feedrate_frame))

        sf_col.addWidget(feedrate_frame)
        top_grid.addLayout(sf_col, 3, 1)

        root_layout.addWidget(top_frame)

        # ── Central frame ───────────────────────────────────────────────
        central_frame = QFrame(central)
        central_frame.setObjectName("centralFrame")
        central_frame.setFrameShape(QFrame.StyledPanel)
        central_frame.setFrameShadow(QFrame.Raised)
        central_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        central_vlayout = QVBoxLayout(central_frame)
        central_vlayout.setContentsMargins(0, 0, 0, 0)
        central_vlayout.setSpacing(0)

        self.centralFrame_stackedWidget = QStackedWidget(central_frame)
        self.centralFrame_stackedWidget.setObjectName("centralFrame_stackedWidget")
        self.centralFrame_stackedWidget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        # Menu page
        self.centralFrame_menuPage = QWidget()
        self.centralFrame_menuPage.setObjectName("centralFrame_menuPage")
        menu_grid = QGridLayout(self.centralFrame_menuPage)
        menu_grid.setContentsMargins(0, 0, 0, 0)

        self.menu_machine_button = QToolButton()
        self.menu_machine_button.setObjectName("menuPage_machineButton")
        self.menu_machine_button.setText("Machine")
        self.menu_machine_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.menu_machine_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        menu_grid.addWidget(self.menu_machine_button, 0, 0)

        self.menu_workpieces_button = QToolButton()
        self.menu_workpieces_button.setObjectName("menuPage_workpiecesButton")
        self.menu_workpieces_button.setText("Workpieces")
        self.menu_workpieces_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.menu_workpieces_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        menu_grid.addWidget(self.menu_workpieces_button, 0, 1)

        self.menu_tools_button = QToolButton()
        self.menu_tools_button.setObjectName("menuPage_toolsButton")
        self.menu_tools_button.setText("Tools")
        self.menu_tools_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.menu_tools_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        menu_grid.addWidget(self.menu_tools_button, 2, 0)

        self.menu_setup_button = QToolButton()
        self.menu_setup_button.setObjectName("menuPage_setupButton")
        self.menu_setup_button.setText("Setup")
        self.menu_setup_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        menu_grid.addWidget(self.menu_setup_button, 2, 1)

        self.menu_statistics_button = QToolButton()
        self.menu_statistics_button.setObjectName("menuPage_statisticsButton")
        self.menu_statistics_button.setText("Statistics")
        self.menu_statistics_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        menu_grid.addWidget(self.menu_statistics_button, 3, 0)

        self.menu_settings_button = QToolButton()
        self.menu_settings_button.setObjectName("menuPage_settingsButton")
        self.menu_settings_button.setText("Settings")
        self.menu_settings_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.menu_settings_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        menu_grid.addWidget(self.menu_settings_button, 3, 1)

        self.centralFrame_stackedWidget.addWidget(self.centralFrame_menuPage)
        self.centralFrame_stackedWidget.setCurrentWidget(self.centralFrame_menuPage)
        self.lastPage = self.centralFrame_menuPage

        # Sub-pages (pre-created once, reused)
        self.machinePage = MachinePage()
        self.centralFrame_stackedWidget.addWidget(self.machinePage)

        self.toolsPage = ToolsPage()
        self.centralFrame_stackedWidget.addWidget(self.toolsPage)

        self.workpiecesPage = WorkpiecesPage(self)
        self.centralFrame_stackedWidget.addWidget(self.workpiecesPage)

        central_vlayout.addWidget(self.centralFrame_stackedWidget)
        root_layout.addWidget(central_frame)

        # ── Bottom frame ────────────────────────────────────────────────
        bottom_frame = QFrame(central)
        bottom_frame.setObjectName("bottomFrame")
        bottom_frame.setFrameShape(QFrame.StyledPanel)
        bottom_frame.setFrameShadow(QFrame.Raised)
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 0, 0, 9)

        self.quick_light_button = QToolButton(bottom_frame)
        self.quick_light_button.setObjectName("bottomFrame_lightButton")
        self.quick_light_button.setMinimumSize(100, 100)
        self.quick_light_button.setText("Light")
        self.quick_light_button.setCheckable(True)
        bottom_layout.addWidget(self.quick_light_button)

        self.quick_coolant_button = QToolButton(bottom_frame)
        self.quick_coolant_button.setObjectName("bottomFrame_coolantButton")
        self.quick_coolant_button.setMinimumSize(100, 100)
        self.quick_coolant_button.setText("Coolant")
        self.quick_coolant_button.setCheckable(True)
        bottom_layout.addWidget(self.quick_coolant_button)

        for _ in range(3):
            placeholder = QPushButton("", bottom_frame)
            placeholder.setMinimumSize(100, 100)
            placeholder.setCheckable(True)
            bottom_layout.addWidget(placeholder)

        bottom_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        self.quick_return_button = QToolButton(bottom_frame)
        self.quick_return_button.setObjectName("bottomFrame_returnButton")
        self.quick_return_button.setMinimumSize(100, 100)
        self.quick_return_button.setText("Return")
        self.quick_return_button.setFocusPolicy(Qt.StrongFocus)
        self.quick_return_button.setAttribute(Qt.WA_AcceptTouchEvents, True)
        make_touch_button(
            self.quick_return_button,
            icon_path=str(ASSETS_DIR / "return.svg"),
            clicked_icon_path=str(ASSETS_DIR / "return.svg"),
        )
        bottom_layout.addWidget(self.quick_return_button)

        root_layout.addWidget(bottom_frame)

        # ── Signal connections ──────────────────────────────────────────
        self.menu_machine_button.clicked.connect(self.open_MachinePage)
        self.menu_workpieces_button.clicked.connect(self.open_workpiecesPage)
        self.menu_tools_button.clicked.connect(self.open_toolsPage)
        self.quick_coolant_button.toggled.connect(self.toggle_coolant_button)
        self.quick_light_button.toggled.connect(self.toggle_light_button)
        self.quick_return_button.clicked.connect(self.on_return_button_clicked)
        self.toolsPage.addToolButton.clicked.connect(lambda: self.openToolDetailPage())
        self.toolsPage.openToolDetail.connect(self.openToolDetailPage)
        self.workpiecesPage.openWorkpieceDetails.connect(self.openWorkpieceDetails)

        # ── Initial state ───────────────────────────────────────────────
        self.set_status_led("orange")
        self.setup_status_time()

    # ── Slots ────────────────────────────────────────────────────────────

    def openWorkpieceDetails(self, workpiece) -> None:
        if hasattr(self, "workpieceDetailPage") and self.workpieceDetailPage is not None:
            self.centralFrame_stackedWidget.removeWidget(self.workpieceDetailPage)
            self.workpieceDetailPage.deleteLater()
        self.workpieceDetailPage = WorkpieceDetailPage(self, workpiece)
        self.centralFrame_stackedWidget.addWidget(self.workpieceDetailPage)
        self.centralFrame_stackedWidget.setCurrentWidget(self.workpieceDetailPage)
        self.lastPage = self.workpiecesPage

    def refresh_tools_list(self) -> None:
        self.toolsPage.load_tools()

    def open_MachinePage(self) -> None:
        self.centralFrame_stackedWidget.setCurrentWidget(self.machinePage)
        self.lastPage = self.centralFrame_menuPage

    def openToolDetailPage(
        self,
        tool_id=None,
        name="",
        tool_type="Endmill",
        diameter=0.0,
        radius=0.0,
        cutting_length=0.0,
        length=0.0,
        flutes=None,
        zOffset=0.0,
        rOffset=0.0,
        supplier="",
        description="",
    ) -> None:
        if hasattr(self, "toolDetailPage") and self.toolDetailPage is not None:
            self.centralFrame_stackedWidget.removeWidget(self.toolDetailPage)
            self.toolDetailPage.deleteLater()
        self.toolDetailPage = ToolDetailPage(
            tool_id, name, tool_type, diameter, radius,
            cutting_length, length, flutes, zOffset, rOffset,
            supplier, description,
        )
        self.centralFrame_stackedWidget.addWidget(self.toolDetailPage)
        self.centralFrame_stackedWidget.setCurrentWidget(self.toolDetailPage)
        self.lastPage = self.toolsPage
        self.toolDetailPage.tool_saved.connect(self.refresh_tools_list)
        self.toolDetailPage.tool_deleted.connect(self.on_return_button_clicked)

    def on_return_button_clicked(self) -> None:
        self.centralFrame_stackedWidget.setCurrentWidget(self.lastPage)
        if self.lastPage == self.toolsPage:
            self.lastPage = self.centralFrame_menuPage
            self.toolsPage.load_tools()
        if self.lastPage == self.workpiecesPage:
            self.lastPage = self.centralFrame_menuPage
            self.workpiecesPage.load_workpieces()

    def open_toolsPage(self) -> None:
        self.lastPage = self.centralFrame_stackedWidget.currentWidget()
        self.toolsPage.load_tools()
        self.centralFrame_stackedWidget.setCurrentWidget(self.toolsPage)

    def open_workpiecesPage(self) -> None:
        self.lastPage = self.centralFrame_stackedWidget.currentWidget()
        self.centralFrame_stackedWidget.setCurrentWidget(self.workpiecesPage)

    def output(self, text: str) -> None:
        self.status_output.setText(text)

    def setup_status_time(self) -> None:
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_status_time)
        self.time_timer.start(1000)

    def update_status_time(self) -> None:
        self.status_time.setText(QTime.currentTime().toString("HH:mm:ss"))

    def set_status_led(self, color: str) -> None:
        self.status_LED.setStyleSheet(f"""
            background-color: {color};
            border-radius: 8px;
            border: 1px solid #333;
        """)

    def toggle_coolant_button(self, checked: bool) -> None:
        try:
            icon_name = "coolant_on.svg" if checked else "coolant_off.svg"
            self.quick_coolant_button.setIcon(QIcon(str(ASSETS_DIR / icon_name)))
        except Exception:
            self.quick_coolant_button.setIcon(QIcon(str(ASSETS_DIR / "coolant_error.svg")))

    def toggle_light_button(self, checked: bool) -> None:
        try:
            icon_name = "light_on.svg" if checked else "light_off.svg"
            self.quick_light_button.setIcon(QIcon(str(ASSETS_DIR / icon_name)))
        except Exception:
            self.quick_light_button.setIcon(QIcon(str(ASSETS_DIR / "light_error.svg")))

    def update_spindle_load(self, load_percent: float) -> None:
        self.spindleFrame_load_bar.setValue(int(load_percent))
        self.spindleFrame_load_value.setText(f"{round(load_percent)} %")

        if load_percent < 80:
            color = "#1E88E5"
        elif load_percent <= 100:
            color = "yellow"
        elif load_percent <= 120:
            color = "orange"
        else:
            color = "red"

        self.spindleFrame_load_bar.setStyleSheet(f"""
        QProgressBar#spindleFrame_loadBar {{
            color: #E6E6E6;
            font-size: 14px;
            font-weight: bold;
            text-align: right;
        }}
        QProgressBar#spindleFrame_loadBar::chunk {{
            background-color: {color};
            border-radius: 2px;
            max-height: 10px;
        }}
        """)

from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QToolButton, QProgressBar,
    QLabel, QFrame, QStackedWidget, QWidget,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QSize, Qt, QTimer, QTime
from PySide6.QtGui import QIcon
import random
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"

from gui.widgets.scroll_widget import ScrollWidget
from gui.widgets.touch_button import make_touch_button
from gui.pages.tools_page import ToolsPage
from gui.pages.tool_detail_page import ToolDetailPage
from gui.pages.machine_page import MachinePage
from gui.pages.workpieces_page import WorkpiecesPage
from gui.pages.workpiece_detail_page import WorkpieceDetailPage


class MainPage(QMainWindow):
    """
    This is the main page of the application.
    """
    def __init__(self):
        super().__init__()

        # Loading the UI file
        loader = QUiLoader()

        ui_path = Path(__file__).parent / "main_page.ui"
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise IOError(f"Cannot open {ui_path}")
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.setWindowIcon(QIcon(str(ASSETS_DIR / "logo.svg")))

        self.setCentralWidget(self.ui)
        self.setWindowTitle("Controller")
        self.resize(700, 950)


        """
        Loading all feature-widgets
        """
        self.centralFrame_stackedWidget = self.ui.findChild(QStackedWidget, "centralFrame_stackedWidget")
        self.centralFrame_menuPage = self.ui.findChild(QWidget, "centralFrame_menuPage")
        self.centralFrame_stackedWidget.setCurrentWidget(self.centralFrame_menuPage)
        self.lastPage = self.centralFrame_menuPage

        self.toolsPage = ToolsPage()
        self.centralFrame_stackedWidget.addWidget(self.toolsPage)

        self.toolsPage.addToolButton.clicked.connect(lambda: self.openToolDetailPage())

        self.toolDetailPage = ToolDetailPage()
        self.toolDetailPage.tool_saved.connect(self.refresh_tools_list)
        self.toolDetailPage.tool_deleted.connect(lambda: print("Tool deleted"))
        self.centralFrame_stackedWidget.addWidget(self.toolDetailPage)

        self.toolsPage.openToolDetail.connect(self.openToolDetailPage)
        self.workpiecesPage = WorkpiecesPage(self)
        self.centralFrame_stackedWidget.addWidget(self.workpiecesPage)

        self.workpiecesPage.openWorkpieceDetails.connect(self.openWorkpieceDetails)
        # Status frame
        self.status_time = self.ui.findChild(QLabel, "statusFrame_time")
        self.status_output = self.ui.findChild(QLabel, "statusFrame_output")
        self.status_LED = self.ui.findChild(QFrame, "statusFrame_LED")

        # Position frame
        self.position_x = self.ui.findChild(QLabel, "positionFrame_xCoordinate")
        self.position_y = self.ui.findChild(QLabel, "positionFrame_yCoordinate")
        self.position_z = self.ui.findChild(QLabel, "positionFrame_zCoordinate")

        # Spindle frame
        self.spindle_rpm = self.ui.findChild(QLabel, "spindleFrame_rpm")
        self.spindleFrame_load_bar = self.ui.findChild(QProgressBar, "spindleFrame_loadBar")
        self.spindleFrame_load_value = self.ui.findChild(QLabel, "spindleFrame_loadValue")

        # feedrate frame
        self.feedrate_value = self.ui.findChild(QLabel, "feedrateFrame_feedrate")

        # menu buttons
        self.menu_machine_button = self.ui.findChild(QToolButton, "menuPage_machineButton")
        self.menu_machine_button.clicked.connect(self.open_MachinePage)

        self.menu_workpieces_button = self.ui.findChild(QToolButton, "menuPage_workpiecesButton")
        self.menu_workpieces_button.clicked.connect(self.open_workpiecesPage)
        self.menu_tools_button = self.ui.findChild(QToolButton, "menuPage_toolsButton")
        self.menu_tools_button.clicked.connect(self.open_toolsPage)
        self.menu_settings_button = self.ui.findChild(QToolButton, "menuPage_settingsButton")
        self.menu_setup_button = self.ui.findChild(QToolButton, "menuPage_setupButton")
        self.menu_statistics_button = self.ui.findChild(QToolButton, "menuPage_statisticsButton")

        # quick buttons
        self.quick_coolant_button = self.ui.findChild(QToolButton, "bottomFrame_coolantButton")
        self.quick_coolant_button.toggled.connect(self.toggle_coolant_button)
        self.quick_light_button = self.ui.findChild(QToolButton, "bottomFrame_lightButton")
        self.quick_light_button.toggled.connect(self.toggle_light_button)

        # Quick Return Button
        self.quick_return_button = self.ui.findChild(QToolButton, "bottomFrame_returnButton")
        self.quick_return_button.setAttribute(Qt.WA_AcceptTouchEvents, True)
        self.quick_return_button.setFocusPolicy(Qt.StrongFocus)

        # Erst Touch-Icon einstellen
        make_touch_button(
            self.quick_return_button,
            icon_path=str(ASSETS_DIR / "return.svg"),
            clicked_icon_path=str(ASSETS_DIR / "return.svg"),
        )

        self.quick_return_button.clicked.connect(self.on_return_button_clicked)

        # Zufällige Positionen
        self.position_x.setText(f"{random.uniform(0, 1000):.2f}")
        self.position_y.setText(f"{random.uniform(0, 750):.2f}")
        self.position_z.setText(f"{random.uniform(0, 250):.2f}")

        # Zufällige Spindelwerte
        rpm = random.randint(0, 30000)  # Spindeldrehzahl in U/min
        load = random.uniform(0, 150)  # Spindellast in %

        self.spindle_rpm.setText(f"{rpm}")
        self.update_spindle_load(load)

        # Zufällige Feedrate
        feedrate = random.uniform(0, 12500)  # mm/min
        self.feedrate_value.setText(f"{feedrate:.0f}")
        self.set_status_led("orange")
        self.setup_status_time()

    def openWorkpieceDetails(self, workpiece):
        print(workpiece)

        self.workpieceDetailPage = WorkpieceDetailPage(self, workpiece)
        self.centralFrame_stackedWidget.addWidget(self.workpieceDetailPage)
        self.centralFrame_stackedWidget.setCurrentWidget(self.workpieceDetailPage)
        self.lastPage = self.workpiecesPage

    def refresh_tools_list(self):
        """
        Ruft die ToolsPage auf, um die Liste der Tools neu zu laden.
        """
        self.toolsPage.load_tools()

    def open_MachinePage(self):
        self.machinePage = MachinePage()
        self.centralFrame_stackedWidget.addWidget(self.machinePage)
        self.centralFrame_stackedWidget.setCurrentWidget(self.machinePage)
        self.lastPage = self.centralFrame_menuPage

    def openToolDetailPage(self, tool_id=None, name="", type="Endmill", diameter="", radius = "", cutting_length = "", length="", flutes = "", zOffset= 0.0,  rOffset= 0.0, supplier = ""):
        """
        Opens ToolDetailPage either empty (new tool) or with existing tool data.
        """
        self.toolDetailPage = ToolDetailPage(tool_id, name, type, diameter, radius, cutting_length, length, flutes, zOffset, rOffset, supplier)
        self.centralFrame_stackedWidget.addWidget(self.toolDetailPage)
        self.centralFrame_stackedWidget.setCurrentWidget(self.toolDetailPage)
        self.lastPage = self.toolsPage

        self.toolDetailPage.tool_saved.connect(self.refresh_tools_list)
        self.toolDetailPage.tool_deleted.connect(self.on_return_button_clicked)

    def on_return_button_clicked(self):
        self.centralFrame_stackedWidget.setCurrentWidget(self.lastPage)
        if self.lastPage == self.toolsPage:
            self.lastPage = self.centralFrame_menuPage
            self.toolsPage.load_tools()

        if self.lastPage == self.workpiecesPage:
            self.lastPage = self.centralFrame_menuPage
            self.workpiecesPage.load_workpieces()


    def open_toolsPage(self):
        self.lastPage = self.centralFrame_stackedWidget.currentWidget()
        self.toolsPage.load_tools()
        self.centralFrame_stackedWidget.setCurrentWidget(self.toolsPage)


    def open_workpiecesPage(self):
        self.lastPage = self.centralFrame_stackedWidget.currentWidget()
        self.centralFrame_stackedWidget.setCurrentWidget(self.workpiecesPage)
    # Status output
    def output(self, text: str):
        self.status_output.setText(text)

    # Sets up and updates the time
    def setup_status_time(self):
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_status_time)
        self.time_timer.start(1000)

    def update_status_time(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.status_time.setText(current_time)

    # Changes the color of the status LED
    def set_status_led(self, color: str):
        self.status_LED.setStyleSheet(f"""
            background-color: {color};
            border-radius: 8px;
            border: 1px solid #333;
        """)

    # Update coolant button color and send command to the API
    def toggle_coolant_button(self, checked: bool):
        try:
            print(checked)
            if checked:
                print("Coolant on")
                self.quick_coolant_button.setIcon(QIcon(str(ASSETS_DIR / "coolant_on.svg")))
            else:
                print("Coolant off")
                self.quick_coolant_button.setIcon(QIcon(str(ASSETS_DIR / "coolant_off.svg")))
        except Exception as e:
            print("ERROR when changing coolant state:", e)
            self.quick_coolant_button.setIcon(QIcon(str(ASSETS_DIR / "coolant_error.svg")))

    # Update light button and send command to the API
    def toggle_light_button(self, checked: bool):
        try:
            if checked:
                self.quick_light_button.setIcon(QIcon(str(ASSETS_DIR / "light_on.svg")))
            else:
                self.quick_light_button.setIcon(QIcon(str(ASSETS_DIR / "light_off.svg")))
        except Exception as e:
            print("ERROR when changing light state:", e)
            self.quick_light_button.setIcon(QIcon(str(ASSETS_DIR / "light_error.svg")))

    # Update spindle load bar and value
    def update_spindle_load(self, load_percent: float):
        bar = self.spindleFrame_load_bar
        value = self.spindleFrame_load_value

        bar.setValue(int(load_percent))
        value.setText(f"{str(round(load_percent))} %")

        if load_percent < 80:
            color = "#1E88E5"
        elif load_percent <= 100:
            color = "yellow"
        elif load_percent <= 120:
            color = "orange"
        else:
            color = "red"

        bar.setStyleSheet(f"""
        QProgressBar#spindleFrame_loadBar {{
            color: #E6E6E6;
            font-size: 14px;
            font-weight: bold;
            text-align: right;
        }}

        QProgressBar#spindleFrame_loadBar::chunk {{
            background-color: {color};
            border-radius: 2px;
            max-heigt: 10px;
        }}
        """)

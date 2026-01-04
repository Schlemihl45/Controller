from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolButton,
    QLabel,
    QFrame,
    QHBoxLayout,
    QSizePolicy,
)
from PySide6.QtCore import (
    QSize,
    Qt,
    Signal,
    QPointF,
    QByteArray,
    QMimeData,
    QTimer,
)
from PySide6.QtGui import QIcon, QDrag
import json

from gui.scrollWidget import ScrollWidget
from database.databaseManager import Database
from database.workpiece_model import Workpiece
from gui.KanbanBoard import KanbanBoard


class WorkpieceFrame(QFrame):
    openWorkpieceDetails = Signal(object)

    def __init__(self, workpiece: Workpiece, parent=None):
        super().__init__(parent)
        self.workpiece = workpiece

        # ---- Styling ----
        self.setStyleSheet(
            """
            QFrame {
                background-color: #1c314d;
                border-radius: 8px;
                border: 1px solid #2E3440;
            }
            QLabel {
                color: #E6E6E6;
                border: none;
            }
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        icon = QToolButton(self)
        icon.setIcon(QIcon("../assets/file-3d.svg"))
        icon.setIconSize(QSize(48, 48))
        icon.setEnabled(False)
        icon.setStyleSheet("border: none;")
        layout.addWidget(icon)

        lbl_name = QLabel(workpiece.name)
        lbl_name.setStyleSheet(
            "color: #E6E6E6; font-size: 24px; font-weight: bold;"
        )

        open_btn = QToolButton()
        open_btn.setText("...")
        open_btn.setFixedSize(QSize(64, 64))
        open_btn.setStyleSheet("background-color: #34455f;")
        open_btn.clicked.connect(
            lambda: self.openWorkpieceDetails.emit(self.workpiece)
        )

        layout.addWidget(lbl_name)
        layout.addStretch()
        layout.addWidget(open_btn)

        # ---- Drag / Long-Press State ----
        self._drag_start_pos = None
        self._drag_active = False

        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._start_drag_after_hold)

    # --------------------------------------------------
    # ScrollWidget-Hilfsfunktion
    # --------------------------------------------------
    def _get_scroll_widget(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, "set_scroll_enabled"):
                return parent
            parent = parent.parent()
        return None

    # --------------------------------------------------
    # Maus-Events (Long-Press aktiviert Drag)
    # --------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
            self._hold_timer.start(250)

    def mouseReleaseEvent(self, event):
        self._hold_timer.stop()

    # --------------------------------------------------
    # Drag starten – natives Qt-Drag-System
    # --------------------------------------------------
    def _start_drag_after_hold(self):
        scroll = self._get_scroll_widget()
        if scroll:
            scroll.set_scroll_enabled(False)

        drag = QDrag(self)
        mime = QMimeData()
        print(self.workpiece.path)
        payload = {"name": self.workpiece.name,
                   "path": str(self.workpiece.path),}
        mime.setData(
            "application/x-kanban-workpiece",
            QByteArray(json.dumps(payload).encode("utf-8")),
        )
        drag.setMimeData(mime)

        pixmap = self.grab().scaled(
            int(self.width() * 0.5),
            int(self.height() * 0.5),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        drag.setPixmap(pixmap)

        if self._drag_start_pos is not None:
            hotspot = QPointF(self._drag_start_pos) * 0.5
            drag.setHotSpot(hotspot.toPoint())

        drag.exec(Qt.CopyAction)

        if scroll:
            scroll.set_scroll_enabled(True)


# --------------------------------------------------
# WorkpiecesPage
# --------------------------------------------------
class WorkpiecesPage(QWidget):
    """
    WorkpiecesPage for the CNC Controller GUI.
    """

    openWorkpieceDetails = Signal(Workpiece)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.repo = Database()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(6)

        # Button-Leiste oben
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(6)

        add_button = QToolButton(self)
        add_button.setIcon(QIcon("../assets/addTool.svg"))
        add_button.setIconSize(QSize(48, 48))
        add_button.setStyleSheet("background-color: #1c314d;")
        buttons_layout.addWidget(add_button)

        spacer_btn = QToolButton(self)
        spacer_btn.setStyleSheet("background-color: #1c314d;")
        spacer_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        buttons_layout.addWidget(spacer_btn)

        self.main_layout.addLayout(buttons_layout)

        kanban_container = QFrame(self)
        kanban_container.setObjectName("kanban_container")
        kanban_container_layout = QVBoxLayout()
        kanban_container_layout.setContentsMargins(0, 0, 0, 0)
        kanban_container.setLayout(kanban_container_layout)

        # Kanban Board + Scrollbereich
        kanban_board = KanbanBoard(self)
        kanban_board.setObjectName("kanban_board")

        kanban_container_layout.addWidget(kanban_board)

        scroll_widget = ScrollWidget()

        self.main_layout.addWidget(kanban_container)
        self.main_layout.addWidget(scroll_widget)

        kanban_board.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        scroll_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )

        self.kanbanBoard = kanban_board
        self.scroll_widget = scroll_widget

        self.load_workpieces()

    def load_workpieces(self):
        """Workpieces aus Datenbank laden und anzeigen."""
        self.repo.initialize()
        self.repo.sync_with_filesystem()

        workpieces = self.repo.load_workpieces(order_by="name")
        print(workpieces)

        frames = []
        for workpiece in workpieces:
            frame = WorkpieceFrame(
                workpiece, self.scroll_widget.content_widget
            )
            frame.openWorkpieceDetails.connect(
                self.openWorkpieceDetails.emit
            )
            frames.append(frame)

        self.scroll_widget.load_objects(frames)

from pathlib import Path
import json

from PySide6.QtCore import Qt, QTimer, QMimeData, QByteArray, QPointF, QSize
from PySide6.QtGui import QColor, QDrag, QIcon
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy, QToolButton,
    QVBoxLayout, QWidget,
)

from database.workpiece_model import Workpiece
from gui.widgets.scroll_widget import ScrollWidget

ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"


class KanbanCard(QFrame):
    """Kanban-Karte mit Long-Press Drag."""

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name

        # ---- Styling ----
        self.setStyleSheet(
            """
            QFrame {
                background-color: #2a3f5f;
                border-radius: 8px;
                border: 1px solid #2E3440;
                padding: 6px;
            }
            QLabel {
                border: none;
            }
            QPushButton {
                border: none;
            }
            """
        )
        #self.setFixedSize(250, 75)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # ---- Layout ----
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)

        self.label = QLabel(name)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.label)

        self.counter_label = QPushButton(self)
        self.counter_label.setStyleSheet("color: #E6E6E6; font-weight: bold;")
        self.counter_label.clicked.connect(self.counter_clicked)
        layout.addWidget(self.counter_label)

        delete_btn = QToolButton()
        delete_btn.setIcon(QIcon(str(ASSETS_DIR / "delete.svg")))
        delete_btn.setIconSize(QSize(25, 25))
        delete_btn.setStyleSheet("border: none;")
        delete_btn.clicked.connect(self.delete_self)
        layout.addWidget(delete_btn)

        # ---- Drag / Long-Press State ----
        self._drag_start_pos = None
        self._drag_active = False

        # Timer für Long-Press Drag
        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._start_drag_after_hold)

    def counter_clicked(self):
        dialog = QDialog()
        dialog.setWindowTitle(f"Change Workpiece Counter - {self.name}")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1c314d;
                border-radius: 8px;
                padding: 9px;
            }
            QLabel {
                color: #E6E6E6;
                font-weight: bold;
                font-size: 18pt;
            }
            QLineEdit {
                background-color: #2a3f5f;
                color: white;
                border: 1px solid #4c566a;
                border-radius: 4px;
                padding: 4px;
                font-size: 18pt;
                text-align: center;
            }
            QPushButton {
                background-color: #34455f;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)

        form_layout = QFormLayout(dialog)

        current_edit = QLineEdit(str(self.current_count))
        total_edit = QLineEdit(str(self.total_count))

        form_layout.addRow("Current count", current_edit)
        form_layout.addRow("Total count", total_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addWidget(buttons)

        def accept_changes():
            try:
                new_current = int(current_edit.text())
                new_total = int(total_edit.text())
            except ValueError:
                dialog.reject()
                return

            self.current_count = new_current
            self.total_count = new_total

            if hasattr(self, "workpiece") and self.workpiece is not None:
                self.workpiece.kanban_currrent = self.current_count
                self.workpiece.kanban_total = self.total_count
                self.workpiece.save_to_json()

            self.counter_label.setText(f"{self.current_count} / {self.total_count}")
            dialog.accept()

        buttons.accepted.connect(accept_changes)
        buttons.rejected.connect(dialog.reject)

        dialog.exec_()



    def set_counter(self, current: int, total: int = None):
        """
        Setzt den Counter (z.B. für die Anzahl der Workpieces).
        current = aktueller Stand
        total = Gesamtzahl (falls None, wird current verwendet)
        """
        self.current_count = current
        self.total_count = total if total is not None else current

        self.counter_label.setText(f"{self.current_count}/{self.total_count}")
        # --------------------------------------------------
    # Hilfsfunktion: nächstes ScrollWidget finden
    # --------------------------------------------------
    def _get_scroll_widget(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, "set_scroll_enabled"):
                return parent
            parent = parent.parent()
        return None

    # --------------------------------------------------
    # Maus-Events für Long-Press Drag
    # --------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
            self._hold_timer.start(250)

    def mouseReleaseEvent(self, event):
        self._hold_timer.stop()

    # --------------------------------------------------
    # Drag starten (Qt-internes System nutzt Pixmap)
    # --------------------------------------------------
    def _start_drag_after_hold(self):
        self.hide()
        scroll = self._get_scroll_widget()
        if scroll:
            scroll.set_scroll_enabled(False)

        drag = QDrag(self)
        mime = QMimeData()
        payload = {"name": self.name}
        mime.setData(
            "application/x-kanban-card",
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

        drag.exec(Qt.MoveAction)

        if scroll:
            scroll.set_scroll_enabled(True)

        self.show()
    # --------------------------------------------------
    # Karte löschen
    # --------------------------------------------------
    def delete_self(self):
        layout = self.parent().layout() if self.parent() else None
        if layout:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget() == self:
                    item.widget().setParent(None)
                    break
        self.deleteLater()

# --------------------------------------------------
# Kanban Column
# --------------------------------------------------
class KanbanColumn(QFrame):
    def __init__(self, title: str, board: "KanbanBoard",parent=None):
        super().__init__(parent)

        self.board = board

        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel(title)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-weight: bold; color: white;")
        layout.addWidget(lbl)

        self.container = ScrollWidget(self, fade = True, fade_color = QColor("#1c314d"))
        self.container.content_widget.setAcceptDrops(True)
        self.container_layout = self.container.objects_layout

        layout.addWidget(self.container)
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def add_workpiece(self, wp: Workpiece):
        """Fügt ein Workpiece hinzu oder erhöht den Counter, falls es schon existiert."""
        wp = Workpiece.load_from_json(wp.path)
        print(wp.path)
        existing_card = self.board.find_card_for_workpiece(wp)
        if existing_card:
            # Karte existiert → Counter erhöhen, keine neue Karte
            existing_card.total_count += 1
            wp.kanban_total += 1
            wp.save_to_json()
            existing_card.set_counter(existing_card.current_count, existing_card.total_count)
            print(
                f"Existing card '{existing_card.name}' counter updated: {existing_card.current_count}/{existing_card.total_count}")
            return

        # keine Karte gefunden → neue Karte erzeugen
        card = KanbanCard(wp.name, self.container)
        card.workpiece = wp
        wp.kanban_total += 1
        wp.save_to_json()
        card.current_count = wp.kanban_current
        card.total_count = wp.kanban_total
        card.set_counter(card.current_count, card.total_count)
        self.container.add_widget(card)
        card.show()

    def dragEnterEvent(self, event):
        if (
            event.mimeData().hasFormat("application/x-kanban-card")
            or event.mimeData().hasFormat("application/x-kanban-workpiece")
        ):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        # Projekt → Karte
        if mime.hasFormat("application/x-kanban-workpiece"):
            data = json.loads(bytes(mime.data("application/x-kanban-workpiece")).decode())
            wp = Workpiece(name=data["name"], path=Path(data.get("path", data["name"])))
            self.add_workpiece(wp)  # <-- benutzt add_workpiece mit Counter
        # Karte → Karte
        elif mime.hasFormat("application/x-kanban-card"):
            card = event.source()
            if card:
                card.setParent(self.container)
                self.container.add_widget(card)
                card.show()
        event.acceptProposedAction()


# --------------------------------------------------
# Kanban Board
# --------------------------------------------------
class KanbanBoard(QWidget):
    """Board mit mehreren Spalten."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(9,9,9,9)
        layout.setSpacing(12)

        lines = []

        for i in range(2):
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setFixedWidth(2)  # Breite der Linie anpassen
            line.setStyleSheet("""
                    background: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(46,52,64,0),
                        stop:0.1 #2E3440,
                        stop:0.9 #2E3440,
                        stop:1 rgba(46,52,64,0)
                    );
                """)
            lines.append(line)


        self.todo_column = KanbanColumn("To Do", self)
        self.progress_column = KanbanColumn("In Progress", self)
        self.done_column = KanbanColumn("Done", self)

        layout.addWidget(self.todo_column)
        layout.addWidget(lines[0])
        layout.addWidget(self.progress_column)
        layout.addWidget(lines[1])
        layout.addWidget(self.done_column)

    def find_card_for_workpiece(self, wp: Workpiece) -> KanbanCard | None:
        """Sucht in allen Spalten nach einer Karte für dieses Workpiece."""
        for col in (self.todo_column, self.progress_column, self.done_column):
            for i in range(col.container_layout.count()):
                item = col.container_layout.itemAt(i)
                widget = item.widget()
                if isinstance(widget, KanbanCard) and getattr(widget, "workpiece", None):
                    if widget.workpiece.path == wp.path:  # <-- über eindeutigen Identifier
                        return widget
        return None

    def clear_board(self):
        for col in (self.todo_column, self.progress_column, self.done_column):
            while col.container_layout.count():
                item = col.container_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

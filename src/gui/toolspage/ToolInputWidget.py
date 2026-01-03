from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QLineEdit,
    QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QColor, QBrush, QPolygonF, QPainterPath
from PySide6.QtGui import QPainter

from PySide6.QtCore import Signal

class ToolInputWidget(QWidget):
    dimension_changed = Signal(str, float)

    def __init__(self, name, tool_type="Endmill", diameter=0, cutting_length=0, length=0, parent=None):
        super().__init__(parent)

        # -----------------------------
        # Tool Properties
        # -----------------------------
        self.name = name
        self.tool_type = tool_type
        self.diameter = diameter
        self.cutting_length = cutting_length
        self.length = length

        # -----------------------------
        # Colors
        # -----------------------------
        self.color_holder = QColor("grey").darker(140)
        self.color_shaft = QColor("#8FAADC").darker(140)
        self.color_cutter = QColor("orange").darker(140)
        self.color_dimension = QColor("#8FAADC")

        # -----------------------------
        # Scene Setup
        # -----------------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6,6,6,6)
        layout.setSpacing(6)

        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.view)

        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setMinimumHeight(200)
        self.view.setMinimumWidth(150)

        self.dimension_proxies = []

        self.draw_tool(self.tool_type)

    # -----------------------------
    # Helper Functions
    # -----------------------------
    def add_line(self, x1, y1, x2, y2, pen=None):
        if pen is None:
            pen = QPen(QColor("#E6E6E6"))
            pen.setWidth(3)
            pen.setCapStyle(Qt.RoundCap)
        self.scene.addLine(x1, y1, x2, y2, pen)

    def add_rect(self, x, y, w, h, color, z=-10):
        item = self.scene.addRect(QRectF(x, y, w, h), QPen(Qt.NoPen), QBrush(color))
        item.setZValue(z)
        return item

    def add_triangle(self, points, color, z=-10):
        poly = QPolygonF([QPointF(*p) for p in points])
        item = self.scene.addPolygon(poly, QPen(Qt.NoPen), QBrush(color))
        item.setZValue(z)
        return item

    def add_circle(self, cx, cy, radius, color, z=-10):
        item = self.scene.addEllipse(cx-radius, cy-radius, 2*radius, 2*radius, QPen(Qt.NoPen), QBrush(color))
        item.setZValue(z)
        return item

    def add_arc(self, x, y, w, h, start_angle_deg, span_angle_deg, color=QColor("#E6E6E6"), z=-10):
        pen = QPen(color)
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)

        path = QPainterPath()
        path.arcMoveTo(QRectF(x, y, w, h), start_angle_deg)
        path.arcTo(QRectF(x, y, w, h), start_angle_deg, span_angle_deg)

        item = self.scene.addPath(path, pen)  # nur Pen, keine Brush
        item.setZValue(z)
        return item

    def add_dimension(self, x1, y1, x2, y2, text, width=50, widget_pos=None, dim_id = None):

        pen = QPen(self.color_dimension, 2)
        self.add_line(x1, y1, x2, y2, pen)

        # Input Box
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setFixedWidth(75)
        container.setStyleSheet("background-color: transparent;")
        container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        edit = QLineEdit()
        edit.setText(str(text))
        edit.setFixedWidth(width)
        edit.setAlignment(Qt.AlignCenter)
        edit.setStyleSheet("background-color: transparent;color: #E6E6E6; font-size: 14px; font-weight: bold; border: none;")

        if dim_id is not None:
            def on_text_changed(value):
                try:
                    val = float(value)
                    self.dimension_changed.emit(dim_id, val)
                except ValueError:
                    pass  # ignore non-numeric input

            edit.textChanged.connect(on_text_changed)

        unit = QLabel("mm")
        unit.setFixedWidth(50)
        unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(edit)
        layout.addWidget(unit)

        proxy = self.scene.addWidget(container)

        if widget_pos is not None:
            proxy.setPos(widget_pos[0], widget_pos[1])
        else:
            proxy.setPos((x1 + x2) / 2 - container.sizeHint().width() / 2,
                         (y1 + y2) / 2 - container.sizeHint().height() / 2)

        self.dimension_proxies.append(proxy)
        return edit

    # -----------------------------
    # Draw Tool
    # -----------------------------
    def draw_tool(self, tool_type,length = 0, cutting_length= 0, diameter=0, radius = 0):
        self.length = length
        self.cutting_length = cutting_length
        self.diameter = diameter
        self.radius = radius

          # Clear previous
        for proxy in self.dimension_proxies:
            self.scene.removeItem(proxy)
            proxy.widget().deleteLater()
        self.dimension_proxies.clear()
        self.scene.clear()

        # Common: Toolholder axis
        self.add_line(0, -50, 0, 50)
        self.add_line(0, -50, -50, -50)
        self.add_line(0, 50, -50, 50)
        self.add_rect(-50, -50, 50, 100, self.color_holder, z=-20)

        if tool_type == "Endmill":
            self.add_rect(0, -25, 25, 50, self.color_shaft)
            self.add_rect(25, -25, 150, 50, self.color_cutter)
            self.add_line(40, -25, 65, 25)
            self.add_line(90, -25, 115, 25)
            self.add_line(140, -25, 165, 25)
            self.add_line(0, -25, 175, -25)
            self.add_line(0, 25, 175, 25)
            self.add_line(175, -25, 175, 25)
            self.add_line(25, -25, 25, 25)

            # Dimensions
            self.add_dimension(0, -75, 175, -75, self.length, widget_pos=(50, -100), dim_id="length")
            self.add_dimension(25, 50, 175, 50, self.cutting_length, widget_pos=(75, 50), dim_id="cutting_length")
            self.add_dimension(200, 25, 200, -25, self.diameter, widget_pos=(200, -10), dim_id="diameter")

        elif tool_type == "Radius Endmill":
            self.add_rect(0, -25, 25, 50, self.color_shaft)
            self.add_rect(25, -25, 125, 50, self.color_cutter)
            self.add_circle(150, 0, 25, self.color_cutter)
            self.add_line(0, -25, 150, -25)
            self.add_line(0, 25, 150, 25)
            self.add_line(25, -25, 25, 25)
            self.add_line(40, -25, 65, 25)
            self.add_line(90, -25, 115, 25)
            self.add_line(140, -25, 163, 20)
            self.add_arc(125, -25, 50, 50, 90, -180)

            # Dimensions
            self.add_dimension(0, -75, 175, -75, self.length, widget_pos=(50, -100), dim_id="length")
            self.add_dimension(25, 50, 175, 50, self.cutting_length, widget_pos=(75, 50), dim_id="cutting_length")
            self.add_dimension(200, 25, 200, -25, self.diameter, widget_pos=(200, -10), dim_id="diameter")

        elif tool_type == "Chamfermill":
            self.add_rect(0, -25, 100, 50, self.color_shaft)
            self.add_rect(100, -25, 50, 50, self.color_cutter)
            self.add_triangle([[149, -25], [175, 0], [149, 25]], self.color_cutter)
            self.add_line(0, -25, 150, -25)
            self.add_line(0, 25, 150, 25)
            self.add_line(150, -25, 175, 0)
            self.add_line(150, 25, 175, 0)
            self.add_line(175, 0, 150, -25)
            self.add_line(175, 0, 150, 25)
            self.add_line(100, -25, 100, 25)

            # Dimensions
            self.add_dimension(0, -75, 175, -75, self.length, widget_pos=(50, -100), dim_id="length")
            self.add_dimension(100, 50, 175, 50, self.cutting_length, widget_pos=(95, 50), dim_id="cutting_length")
            self.add_dimension(200, 25, 200, -25, self.diameter, widget_pos=(200, -10), dim_id="diameter")

        elif tool_type == "Facemill":
            self.add_rect(0, -25, 125, 50, self.color_shaft)
            self.add_rect(125, -25, 50, 50, self.color_cutter)
            self.add_line(140, -25, 165, 25)
            self.add_line(0, -25, 175, -25)
            self.add_line(0, 25, 175, 25)
            self.add_line(175, -25, 175, 25)
            self.add_line(125, -25, 125, 25)

            # Dimensions
            self.add_dimension(0, -75, 175, -75, self.length, widget_pos=(50, -100), dim_id="length")
            self.add_dimension(125, 50, 175, 50, self.cutting_length, widget_pos=(110, 50), dim_id="cutting_length")
            self.add_dimension(200, 25, 200, -25, self.diameter, widget_pos=(200, -10), dim_id="diameter")

        elif tool_type == "Drill":
            self.add_rect(0, -25, 25, 50, self.color_shaft)
            self.add_rect(25, -25, 125, 50, self.color_cutter)
            self.add_triangle([[149, -25], [175, 0], [149, 25]], self.color_cutter)
            self.add_line(0, -25, 150, -25)
            self.add_line(0, 25, 150, 25)
            self.add_line(150, -25, 175, 0)
            self.add_line(150, 25, 175, 0)
            self.add_line(175, 0, 150, -25)
            self.add_line(175, 0, 150, 25)
            self.add_line(25, -25, 25, 25)
            self.add_line(40, -25, 85, 25)
            self.add_line(90, -25, 135, 25)

            # Dimensions
            self.add_dimension(0, -75, 175, -75, self.length, widget_pos=(50, -100), dim_id="length")
            self.add_dimension(25, 50, 175, 50, self.cutting_length, widget_pos=(75, 50), dim_id="cutting_length")
            self.add_dimension(200, 25, 200, -25, self.diameter, widget_pos=(200, -10), dim_id="diameter")

        else:
            self.add_rect(0, -25, 25, 50, self.color_shaft)
            self.add_rect(25, -25, 150, 50, self.color_cutter)
            self.add_line(0, -25, 175, -25)
            self.add_line(0, 25, 175, 25)
            self.add_line(175, -25, 175, 25)
            self.add_line(40, -25, 65, 25)
            self.add_line(90, -25, 115, 25)
            self.add_line(140, -25, 165, 25)

            # Dimensions
            self.add_dimension(0, -75, 175, -75, self.length, widget_pos=(50, -100), dim_id="length")
            self.add_dimension(25, 50, 175, 50, self.cutting_length, widget_pos=(75, 50), dim_id="cutting_length")
            self.add_dimension(200, 25, 200, -25, self.diameter, widget_pos=(200, -10), dim_id="diameter")

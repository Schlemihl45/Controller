from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsLineItem,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsProxyWidget,
    QLineEdit, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QRectF, QSize, QLineF
from PySide6.QtGui import QPen, QColor
from PySide6.QtGui import QPainter

class ToolInputWidget(QWidget):
    """
    QWidget for entering tool parameters with 2D visualization.
    Currently supports fixed Endmill model.
    """
    def __init__(self, name, type, diameter, cutting_length, length, parent=None):
        super().__init__(parent)

        self.name = name
        self.type = type
        self.diameter = diameter
        self.cutting_length = cutting_length
        self.length = length

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Graphics View
        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.view)

        # Scene
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setMinimumHeight(200)
        self.view.setMinimumWidth(150)

        # Draw fixed Endmill model
        self.draw_endmill()

        print(length, diameter)

    def draw_endmill(self):
        """
        Draw a simple 2D endmill with dimension lines.
        All geometry is scaled using the factor.
        """
        self.scene.clear()

        factor = 1.0  # global scale factor

        pen = QPen(QColor("#E6E6E6"))
        pen.setWidth(3)

        dimensionPen = QPen(QColor("#8FAADC"))
        dimensionPen.setWidth(2)

        # -----------------------------
        # Endmill cutting geometry
        # -----------------------------
        self.scene.addLine(
            0 * factor, -25 * factor,
            175 * factor, -25 * factor,
            pen
        )
        self.scene.addLine(
            0 * factor, 25 * factor,
            175 * factor, 25 * factor,
            pen
        )
        self.scene.addLine(
            175 * factor, -25 * factor,
            175 * factor, 25 * factor,
            pen
        )
        # -----------------------------
        # Toolholder transition
        # -----------------------------
        self.scene.addLine(
            25 * factor, -25 * factor,
            25 * factor, 25 * factor,
            pen
        )

        # -----------------------------
        # Center axis
        # -----------------------------
        self.scene.addLine(
            0 * factor, -50 * factor,
            0 * factor, 50 * factor,
            pen
        )
        self.scene.addLine(
            0 * factor, -50 * factor,
            -50 * factor, -50 * factor,
            pen
        )
        self.scene.addLine(
            0 * factor, 50 * factor,
            -50 * factor, 50 * factor,
            pen
        )

        # -----------------------------
        # Dimension: cutting length
        # -----------------------------
        self.scene.addLine(
            0 * factor, -75 * factor,
            175 * factor, -75 * factor,
            dimensionPen
        )

        # midpoint cutting length
        cut_mid_x = (0 + 175) / 2 * factor
        cut_mid_y = -90 * factor

        self.cut_length_input = self.add_dimension_input(
            cut_mid_x,
            cut_mid_y,
            f"{self.length}", 50
        )

        # -----------------------------
        # Dimension: total length
        # -----------------------------
        self.scene.addLine(
            25 * factor, 50 * factor,
            175 * factor, 50 * factor,
            dimensionPen
        )
        # midpoint total length
        total_mid_x = (25 + 175) / 2 * factor
        total_mid_y = 65 * factor

        self.total_length_input = self.add_dimension_input(
            total_mid_x,
            total_mid_y,
            f"{self.cutting_length}", 50
        )

        # -----------------------------
        # Dimension: diameter
        # -----------------------------
        self.scene.addLine(
            200 * factor, 25 * factor,
            200 * factor, -25 * factor,
            dimensionPen
        )
        # midpoint diameter
        diam_mid_x = 245 * factor
        diam_mid_y = 0 * factor

        self.diameter_input = self.add_dimension_input(
            diam_mid_x,
            diam_mid_y,
            f"{self.diameter}", 40
        )

    def add_dimension_input(self, x, y, text, length):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        container.setFixedWidth(100)
        container.setStyleSheet("background-color: transparent;")
        container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        edit = QLineEdit()
        edit.setText(text)
        edit.setFixedWidth(length)
        edit.setAlignment(Qt.AlignCenter)
        edit.setStyleSheet("background-color: transparent; color: #E6E6E6; font-size: 14px; font-weight: bold;")

        unit = QLabel("mm")
        unit.setFixedWidth(50)
        unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(edit)
        layout.addWidget(unit)

        proxy = self.scene.addWidget(container)
        proxy.setPos(
            x - container.sizeHint().width() / 2,
            y - container.sizeHint().height() / 2
        )

        return edit
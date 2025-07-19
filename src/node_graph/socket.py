from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPen, QBrush, QColor, QFont
from PySide6.QtCore import QRectF


SOCKET_INPUT = QColor(100, 100, 100)
SOCKET_OUTPUT = QColor(100, 100, 100)
SOCKET_INPUT_CONNECTED = QColor(255, 255, 100)
SOCKET_OUTPUT_CONNECTED = QColor(150, 255, 150)
SOCKET_BORDER = QColor(180, 180, 180)
TEXT_COLOR = QColor(60, 60, 60)


class Socket(QGraphicsItem):
    def __init__(self, node, socket_type="input", position=0, label=""):
        super().__init__()
        self.node = node
        self.socket_type = socket_type  # "input" or "output"
        self.position = position
        self.label = label
        self.connections = []
        self.radius = 6
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def paint(self, painter, option, widget):
        # Socket circle
        if self.socket_type == "input":
            color = SOCKET_INPUT if not self.connections else SOCKET_INPUT_CONNECTED
        else:
            color = SOCKET_OUTPUT if not self.connections else SOCKET_OUTPUT_CONNECTED

        painter.setBrush(QBrush(color))
        painter.setPen(QPen(SOCKET_BORDER, 2))
        painter.drawEllipse(self.boundingRect())

        # Socket label
        painter.setPen(QPen(TEXT_COLOR))
        font = QFont("JetBrains Mono", 8)
        painter.setFont(font)
        if self.socket_type == "input":
            painter.drawText(15, 5, self.label)
        else:
            painter.drawText(-60, 5, self.label)

    def get_connection_point(self):
        return self.scenePos()

    def add_connection(self, connection):
        self.connections.append(connection)
        self.update()

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
            self.update()

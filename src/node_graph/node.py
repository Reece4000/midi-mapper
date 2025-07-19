from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QFont, QColor
from PySide6.QtWidgets import QGraphicsItem
from src.node_graph.socket import Socket


NODE_BACKGROUND = QColor(250, 250, 250)
NODE_BACKGROUND_SELECTED = QColor(255, 240, 240)
NODE_BORDER = QColor(200, 200, 200)
NODE_BORDER_SELECTED = QColor(255, 0, 0)
NODE_TITLE_BACKGROUND = QColor(240, 240, 240)
NODE_TITLE_BACKGROUND_SELECTED = QColor(255, 100, 100)
NODE_SHADOW = QColor(0, 0, 0, 120)
TEXT_COLOR = QColor(60, 60, 60)


class Node(QGraphicsItem):
    def __init__(self, title="Node", node_type="input", width=150, height=64):
        super().__init__()
        self.title = title
        self.width = width
        self.height = height
        self.type = node_type
        self.input_sockets = []
        self.output_sockets = []

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Create default sockets
        if self.type in ("output", "process"):
            self.add_input_socket()

        if self.type in ("process", "input"):
            self.add_output_socket()

        self.update_socket_positions()

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        # Node background
        rect = self.boundingRect()

        # Shadow
        shadow_rect = rect.translated(3, 3)
        painter.setBrush(QBrush(NODE_SHADOW))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shadow_rect, 5, 5)

        # Main node
        if self.isSelected():
            painter.setBrush(QBrush(NODE_BACKGROUND_SELECTED))
            painter.setPen(QPen(NODE_BORDER_SELECTED, 2))
        else:
            painter.setBrush(QBrush(NODE_BACKGROUND))
            painter.setPen(QPen(NODE_BORDER, 2))

        painter.drawRoundedRect(rect, 5, 5)

        # Title bar
        title_rect = QRectF(0, 0, self.width, 25)
        if self.isSelected():
            painter.setBrush(QBrush(NODE_TITLE_BACKGROUND_SELECTED))
        else:
            painter.setBrush(QBrush(NODE_TITLE_BACKGROUND))
        painter.drawRoundedRect(title_rect, 5, 5)
        painter.drawRect(QRectF(0, 20, self.width, 5))  # Square off bottom

        # Title text
        painter.setPen(QPen(TEXT_COLOR))
        font = QFont("JetBrains Mono", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)

    def add_input_socket(self):
        socket = Socket(self, "input", len(self.input_sockets))
        socket.setParentItem(self)
        self.input_sockets.append(socket)
        self.update_socket_positions()
        return socket

    def add_output_socket(self):
        socket = Socket(self, "output", len(self.output_sockets))
        socket.setParentItem(self)
        self.output_sockets.append(socket)
        self.update_socket_positions()
        return socket

    def update_socket_positions(self):
        # Position input sockets
        input_spacing = (self.height - 30) / max(1, len(self.input_sockets) + 1)
        for i, socket in enumerate(self.input_sockets):
            y = 30 + input_spacing * (i + 1)
            socket.setPos(-socket.radius, y)

        # Position output sockets
        output_spacing = (self.height - 30) / max(1, len(self.output_sockets) + 1)
        for i, socket in enumerate(self.output_sockets):
            y = 30 + output_spacing * (i + 1)
            socket.setPos(self.width + socket.radius, y)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update all connections when node moves
            for socket in self.input_sockets + self.output_sockets:
                for connection in socket.connections:
                    connection.update()
        return super().itemChange(change, value)

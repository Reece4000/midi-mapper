from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPen, QPainterPath, QColor


CONNECTION_COLOR = QColor(200, 200, 200)
CONNECTION_COLOR_SELECTED = QColor(255, 255, 100)


class Connection(QGraphicsItem):
    def __init__(self, start_socket, end_socket=None):
        super().__init__()
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.end_pos = QPointF(0, 0)
        self.setZValue(-1)  # Draw connections behind nodes

    def boundingRect(self):
        start = self.start_socket.get_connection_point()
        end = self.end_socket.get_connection_point() if self.end_socket else self.end_pos

        # Map to local coordinates
        start = self.mapFromScene(start)
        end = self.mapFromScene(end)

        return QRectF(start, end).normalized().adjusted(-10, -10, 10, 10)

    def paint(self, painter, option, widget):
        start = self.start_socket.get_connection_point()
        end = self.end_socket.get_connection_point() if self.end_socket else self.end_pos

        # Map to local coordinates
        start = self.mapFromScene(start)
        end = self.mapFromScene(end)

        # Create bezier curve
        path = QPainterPath()
        path.moveTo(start)

        # Control points for bezier curve
        ctrl_offset = abs(end.x() - start.x()) * 0.5
        ctrl1 = QPointF(start.x() + ctrl_offset, start.y())
        ctrl2 = QPointF(end.x() - ctrl_offset, end.y())

        path.cubicTo(ctrl1, ctrl2, end)

        # Draw connection
        pen = QPen(CONNECTION_COLOR, 3)
        if self.isSelected():
            pen.setColor(CONNECTION_COLOR_SELECTED)
            pen.setWidth(4)

        painter.setPen(pen)
        painter.drawPath(path)

    def set_end_pos(self, pos):
        self.end_pos = pos
        self.prepareGeometryChange()
        self.update()

    def connect_to_socket(self, socket):
        self.end_socket = socket
        self.end_socket.add_connection(self)
        self.start_socket.add_connection(self)
        self.prepareGeometryChange()
        self.update()

    def disconnect(self):
        if self.start_socket:
            self.start_socket.remove_connection(self)
        if self.end_socket:
            self.end_socket.remove_connection(self)
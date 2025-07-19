import sys
import math
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
                               QGraphicsItem, QGraphicsProxyWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QWidget, QMenu)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QTimer
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont, QPainterPath, QPolygonF

# Color Constants
CANVAS_BACKGROUND = QColor(35, 35, 35)
GRID_COLOR = QColor(60, 60, 60, 150)
NODE_BACKGROUND = QColor(250, 250, 250)
NODE_BACKGROUND_SELECTED = QColor(255, 240, 240)
NODE_BORDER = QColor(200, 200, 200)
NODE_BORDER_SELECTED = QColor(255, 0, 0)
NODE_TITLE_BACKGROUND = QColor(240, 240, 240)
NODE_TITLE_BACKGROUND_SELECTED = QColor(255, 100, 100)
NODE_SHADOW = QColor(0, 0, 0, 120)

SOCKET_INPUT = QColor(100, 100, 100)
SOCKET_OUTPUT = QColor(100, 100, 100)
SOCKET_INPUT_CONNECTED = QColor(255, 255, 100)
SOCKET_OUTPUT_CONNECTED = QColor(150, 255, 150)
SOCKET_BORDER = QColor(180, 180, 180)
CONNECTION_COLOR = QColor(200, 200, 200)
CONNECTION_COLOR_SELECTED = QColor(255, 255, 100)

TEXT_COLOR = QColor(60, 60, 60)


class Socket(QGraphicsItem):
    def __init__(self, node, socket_type="input", position=0, label="Socket"):
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


class Node(QGraphicsItem):
    def __init__(self, title="Node", node_type="input", width=150, height=100):
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
            self.add_input_socket("Input")

        if self.type in ("process", "input"):
            self.add_output_socket("Output")

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

    def add_input_socket(self, label="Input"):
        socket = Socket(self, "input", len(self.input_sockets), label)
        socket.setParentItem(self)
        self.input_sockets.append(socket)
        self.update_socket_positions()
        return socket

    def add_output_socket(self, label="Output"):
        socket = Socket(self, "output", len(self.output_sockets), label)
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


class NodeGraphView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Set scene rect to very large area for "infinite" canvas
        self.scene.setSceneRect(-10000, -10000, 20000, 20000)

        # View settings
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Connection creation
        self.temp_connection = None
        self.connection_start_socket = None

        # Grid settings
        self.grid_size = 50
        self.show_grid = True

    def drawBackground(self, painter, rect):
        # Draw dark background
        painter.fillRect(rect, CANVAS_BACKGROUND)

        # Draw grid
        if self.show_grid:
            painter.setPen(QPen(GRID_COLOR, 0.5))

            # Get visible rect in scene coordinates
            left = int(rect.left()) - (int(rect.left()) % self.grid_size)
            top = int(rect.top()) - (int(rect.top()) % self.grid_size)

            # Draw vertical lines
            x = left
            while x < rect.right():
                painter.drawLine(x, rect.top(), x, rect.bottom())
                x += self.grid_size

            # Draw horizontal lines
            y = top
            while y < rect.bottom():
                painter.drawLine(rect.left(), y, rect.right(), y)
                y += self.grid_size

    def wheelEvent(self, event):
        # Zoom functionality
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        # Get the mouse position
        old_pos = self.mapToScene(event.position().toPoint())

        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

        # Get the new position and move scene to keep mouse position
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            # Pan with middle mouse button
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            # Create fake left button event for panning
            fake_event = event.__class__(
                event.type(),
                event.position(),
                Qt.LeftButton,
                Qt.LeftButton,
                event.modifiers()
            )
            super().mousePressEvent(fake_event)
            return
        elif event.button() == Qt.LeftButton:
            item = self.itemAt(event.position().toPoint())
            if isinstance(item, Socket):
                # Start connection
                self.start_connection(item)
                return  # Don't pass to super() to avoid selection issues
            elif not item and event.modifiers() == Qt.ControlModifier:
                # Click on empty space - create node
                self.create_node_at_position(self.mapToScene(event.position().toPoint()))
                return
        elif event.button() == Qt.RightButton:
            # Context menu
            self.show_context_menu(event.position().toPoint())
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_connection:
            # Update temporary connection
            scene_pos = self.mapToScene(event.position().toPoint())
            self.temp_connection.set_end_pos(scene_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            # Create fake left button release event for panning
            fake_event = event.__class__(
                event.type(),
                event.position(),
                Qt.LeftButton,
                Qt.LeftButton,
                event.modifiers()
            )
            super().mouseReleaseEvent(fake_event)
            self.setDragMode(QGraphicsView.RubberBandDrag)
            return
        elif event.button() == Qt.LeftButton and self.temp_connection:
            # Try to complete connection
            item = self.itemAt(event.position().toPoint())
            if isinstance(item, Socket) and self.can_connect(self.connection_start_socket, item):
                self.temp_connection.connect_to_socket(item)
            else:
                # Cancel connection - safely remove from scene
                self.cancel_connection()

            # Always reset connection state
            self.temp_connection = None
            self.connection_start_socket = None
            return

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            # Delete selected items
            selected_items = self.scene.selectedItems()
            for item in selected_items:
                if isinstance(item, Connection):
                    item.disconnect()
                    self.scene.removeItem(item)
                elif isinstance(item, Node):
                    # Remove all connections to this node
                    for socket in item.input_sockets + item.output_sockets:
                        for connection in socket.connections[:]:  # Copy list to avoid modification during iteration
                            connection.disconnect()
                            self.scene.removeItem(connection)
                    self.scene.removeItem(item)
        elif event.key() == Qt.Key_G:
            # Toggle grid
            self.show_grid = not self.show_grid
            self.update()
        super().keyPressEvent(event)

    def start_connection(self, socket):
        self.connection_start_socket = socket
        self.temp_connection = Connection(socket)
        self.scene.addItem(self.temp_connection)

    def cancel_connection(self):
        if self.temp_connection:
            # Make sure the connection is properly removed from the scene
            if self.temp_connection.scene() is not None:
                try:
                    self.scene.removeItem(self.temp_connection)
                except RuntimeError:
                    pass  # Item already removed or being destroyed

            # Clean up references
            self.temp_connection = None

    def can_connect(self, socket1, socket2):
        if not socket1 or not socket2:
            return False
        if socket1 == socket2:
            return False
        if socket1.node == socket2.node:
            return False
        if socket1.socket_type == socket2.socket_type:
            return False
        return True

    def create_node_at_position(self, pos, node_type="input"):
        node = Node(f"Node {len(self.scene.items()) + 1}", node_type)
        node.setPos(pos)
        self.scene.addItem(node)

    def show_context_menu(self, pos):
        menu = QMenu(self)

        # Add node action
        add_node_action = menu.addAction("Add Node")
        add_node_action.triggered.connect(
            lambda: self.create_node_at_position(self.mapToScene(pos))
        )

        # Toggle grid action
        grid_action = menu.addAction("Toggle Grid")
        grid_action.triggered.connect(lambda: setattr(self, 'show_grid', not self.show_grid) or self.update())

        # Reset zoom action
        reset_zoom_action = menu.addAction("Reset Zoom")
        reset_zoom_action.triggered.connect(lambda: self.resetTransform())

        menu.exec(self.mapToGlobal(pos))


class NodeGraphWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create layout
        layout = QVBoxLayout(self)

        # Create toolbar
        toolbar_layout = QHBoxLayout()

        add_in_node_btn = QPushButton("Add Input Node")
        add_in_node_btn.clicked.connect(self.add_input_node)
        toolbar_layout.addWidget(add_in_node_btn)

        add_process_node_btn = QPushButton("Add Process Node")
        add_process_node_btn.clicked.connect(self.add_process_node)
        toolbar_layout.addWidget(add_process_node_btn)

        add_out_node_btn = QPushButton("Add Output Node")
        add_out_node_btn.clicked.connect(self.add_output_node)
        toolbar_layout.addWidget(add_out_node_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)
        toolbar_layout.addWidget(clear_btn)

        toolbar_layout.addStretch()

        layout.addLayout(toolbar_layout)

        # Create node graph view
        self.node_view = NodeGraphView()
        layout.addWidget(self.node_view)

    def add_input_node(self):
        # Add node at center of current view
        center = self.node_view.mapToScene(self.node_view.rect().center())
        self.node_view.create_node_at_position(center, "input")

    def add_process_node(self):
        # Add node at center of current view
        center = self.node_view.mapToScene(self.node_view.rect().center())
        self.node_view.create_node_at_position(center, "process")

    def add_output_node(self):
        # Add node at center of current view
        center = self.node_view.mapToScene(self.node_view.rect().center())
        self.node_view.create_node_at_position(center, "output")

    def clear_all(self):
        self.node_view.scene.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create a main window to hold the widget when running standalone
    main_window = QMainWindow()
    main_window.setWindowTitle("Node Graph Editor")
    main_window.setGeometry(100, 100, 1200, 800)

    widget = NodeGraphWidget()
    main_window.setCentralWidget(widget)

    main_window.show()
    sys.exit(app.exec())
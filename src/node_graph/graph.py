from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtGui import QPen, QPainter, QColor
from PySide6.QtCore import Qt
from src.node_graph.socket import Socket
from src.node_graph.node import Node
from src.node_graph.connector import Connection


CANVAS_BACKGROUND = QColor(35, 35, 35)
GRID_COLOR = QColor(60, 60, 60, 150)


class NodeGraphView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.node_count = {"input": 0, "process": 0, "output": 0}
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

    def get_node_title(self, node_type):
        return f"{node_type.title()} Node {self.node_count[node_type] + 1}"

    def create_node_at_position(self, pos, node_type="input"):
        node = Node(self.get_node_title(node_type), node_type)
        node.setPos(pos)
        self.scene.addItem(node)
        self.node_count[node_type] += 1

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

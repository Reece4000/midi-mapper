from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget
from src.node_graph.graph import NodeGraphView


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
        center = self.node_view.mapToScene(self.node_view.rect().center())
        self.node_view.create_node_at_position(center, "input")

    def add_process_node(self):
        center = self.node_view.mapToScene(self.node_view.rect().center())
        self.node_view.create_node_at_position(center, "process")

    def add_output_node(self):
        center = self.node_view.mapToScene(self.node_view.rect().center())
        self.node_view.create_node_at_position(center, "output")

    def clear_all(self):
        self.node_view.scene.clear()
        self.node_view.node_count = {"input": 0, "process": 0, "output": 0}

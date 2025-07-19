from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QTextEdit, QComboBox
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtCore import Qt
from src.midi_handler import MidiHandler



class MidiMonitor(QWidget):
    def __init__(self):
        super().__init__()

        self.midi_handler = MidiHandler(callback=self.midi_callback)

        self.setWindowTitle("MIDI Monitor")
        self.setWindowIcon(QIcon("resources/icon.png"))
        self.resize(800, 500)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # ---- Input device pair ----
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)

        self.input_combo = QComboBox()
        self.input_combo.addItems(self.midi_handler.get_in_ports())
        self.input_combo.setMaximumWidth(300)
        self.input_combo.currentIndexChanged.connect(self.change_midi_input)
        form_layout.addRow(QLabel("MIDI Input:"), self.input_combo)

        self.output_combo = QComboBox()
        self.output_combo.addItems(self.midi_handler.get_out_ports())
        self.output_combo.setMaximumWidth(300)
        self.output_combo.currentIndexChanged.connect(self.change_midi_output)
        form_layout.addRow(QLabel("MIDI Output:"), self.output_combo)

        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)

        # --- Title + Message display ---
        self.title_label = QLabel("Incoming MIDI Messages")
        self.title_label.setObjectName("titleLabel")
        main_layout.addWidget(self.title_label)

        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.message_display.setObjectName("messageDisplay")
        main_layout.addWidget(self.message_display)

    def midi_callback(self, msg, timestamp):
        event_type, control, val = msg[0], msg[1], msg[2]
        status_hex = f"{event_type:02X}"
        message_str = f"Status: 0x{status_hex}, Data1: {control}, Data2: {val}"

        # Append the message to the display
        self.message_display.append(message_str)

        # Auto-scroll to the latest message
        self.message_display.moveCursor(QTextCursor.End)
        self.midi_handler.midi_out.send_message(msg)
        
    def change_midi_input(self, index):
        port_name = self.input_combo.itemText(index)
        self.midi_handler.set_midi_in(port_name)

    def change_midi_output(self, index):
        port_name = self.output_combo.itemText(index)
        self.midi_handler.set_midi_out(port_name)
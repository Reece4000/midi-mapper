import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from src.app import MidiMonitor



if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='light_red.xml', invert_secondary=True)
    window = MidiMonitor()
    window.show()
    sys.exit(app.exec())

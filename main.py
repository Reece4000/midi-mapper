import sys
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from src.app import MidiMonitor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    extra = {

        # Button colors
        'danger': '#dc3545',
        'warning': '#ffc107',
        'success': '#17a2b8',

        # Font
        'font_family': 'JetBrains Mono',
        'font_size': '12px',
        'line_height': '2px',

        # 'density_scale': '-4',

    }

    # apply_stylesheet(app, theme='dark_cyan.xml', extra=extra)
    apply_stylesheet(app, theme='light_red.xml', invert_secondary=True, extra=extra)
    window = MidiMonitor()
    window.show()
    sys.exit(app.exec())

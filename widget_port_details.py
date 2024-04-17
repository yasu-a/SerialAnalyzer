from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from utils import g_ports
from wdiget_port_selector import PortListWidget
from widget_port_parameter import PortParameterWidget


class PortDetailWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        self.setFixedWidth(200)

        layout = QGridLayout(self)
        self.setLayout(layout)

    def set_values_on_view(self, mapping):
        layout: QGridLayout = self.layout()

        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        keys = sorted(mapping.keys())
        for i_row, key in enumerate(keys):
            label = QLabel(self)
            label.setText(key)
            layout.addWidget(label, i_row, 0)

            label = QLabel(self)
            label.setText(mapping[key])
            layout.addWidget(label, i_row, 1)

    KEYS = {
        "baudrate": "BAUD",
        "state": "状態",
        "name": "デバイス名"
    }

    FORMATS = {
        "baudrate": "{} baud",
    }

    @classmethod
    def map_serial_info(cls, serial_info: dict):
        result = {}
        for k, v in serial_info.items():
            k = cls.KEYS.get(k, k)
            v = cls.FORMATS.get(k, "{}").format(v)
            result[k] = v
        return result

    @pyqtSlot()
    def update_port_info(self):
        if g_ports.has_active():
            serial_info = self.map_serial_info(g_ports.active_port_info)
            self.set_values_on_view(serial_info)
            self.setEnabled(True)
        else:
            self.setEnabled(False)

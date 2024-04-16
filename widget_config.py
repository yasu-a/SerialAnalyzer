from pprint import pformat

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from utils import g_ports
from wdiget_port_selector import PortListWidget


class SerialConfigWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        self.setFixedWidth(200)

        layout = QVBoxLayout(self)

        w_port_list = PortListWidget(self)
        w_port_list.any_state_changed.connect(self.update_current_device_info)
        layout.addWidget(w_port_list)

        l_current_device = QTextEdit()
        l_current_device.setReadOnly(True)
        layout.addWidget(l_current_device)
        self.__t_current_device = l_current_device

        layout.addStretch()

    def update_current_device_info(self):
        if g_ports.has_active():
            self.__t_current_device.setText(pformat(g_ports.active_port_info))
        else:
            self.__t_current_device.setText("")

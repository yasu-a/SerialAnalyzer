from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from utils import g_ports
from wdiget_port_selector import PortListWidget
from widget_port_parameter import PortParameterWidget


class HorizontalSplitWidget(QFrame):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class PortConfigWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        self.setFixedWidth(200)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        layout.addWidget(QLabel(self, text="<html><b>シリアルポート</b></html>"))

        w_port_params = PortParameterWidget(self)
        layout.addWidget(w_port_params)

        w_port_list = PortListWidget(self)
        w_port_list.any_state_changed.connect(self.update_current_device_info)
        layout.addWidget(w_port_list)

        layout.addWidget(HorizontalSplitWidget(self))

        layout.addWidget(QLabel(self, text="<html><b>接続中のポート</b></html>"))

        l_current_device = QTextEdit()
        l_current_device.setReadOnly(True)
        layout.addWidget(l_current_device)
        self.__t_current_device = l_current_device

        layout.addStretch()

    def update_current_device_info(self):
        if g_ports.has_active():
            info = g_ports.active_port_info
            self.__t_current_device.setText(
                "\n".join(f"{k}: {v!r}" for k, v in info.items())
            )
        else:
            self.__t_current_device.setText("")

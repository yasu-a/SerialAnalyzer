from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from wdiget_port_selector import PortListWidget
from widget_port_details import PortDetailWidget
from widget_port_parameter import PortParameterWidget


class HorizontalSplitWidget(QFrame):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class PortConfigWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__parameter_change_flag = False

        self.__init_ui()

    def __init_ui(self):
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        layout.addWidget(QLabel(self, text="<html><b>シリアルポート</b></html>"))

        w_port_params = PortParameterWidget(self)
        layout.addWidget(w_port_params)

        w_port_list = PortListWidget(self)
        layout.addWidget(w_port_list)

        layout.addWidget(HorizontalSplitWidget(self))

        layout.addWidget(QLabel(self, text="<html><b>接続中のポート</b></html>"))

        w_port_details = PortDetailWidget()
        w_port_list.any_state_changed.connect(w_port_details.update_port_info)
        w_port_list.any_params_changed.connect(w_port_details.update_port_info)
        layout.addWidget(w_port_details)
        self.__w_port_details = w_port_details

        layout.addStretch(1)

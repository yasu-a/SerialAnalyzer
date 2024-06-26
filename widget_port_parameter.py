from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from utils import g_ports, COMPortParameters


class PortParameterWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        layout = QGridLayout(self)
        self.setLayout(layout)

        l_baudrate = QComboBox(self)
        l_baudrate.addItems(
            list(
                map(
                    "{} baud".format,
                    ["300", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"],
                )
            )
        )
        l_baudrate.setCurrentText("9600 baud")
        l_baudrate.currentTextChanged.connect(self.on_parameter_changed)
        layout.addWidget(l_baudrate, 0, 0)
        self.__l_baudrate = l_baudrate

    @pyqtSlot()
    def on_parameter_changed(self):
        baudrate = int(self.__l_baudrate.currentText().split(" ")[0])
        g_ports.set_params_and_reopen(
            COMPortParameters(
                baudrate=baudrate,
            )
        )

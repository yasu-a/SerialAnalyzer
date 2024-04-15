from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox
from serial import Serial

from utils import list_device_names


class SerialConfigWidget(QWidget):
    port_updated = pyqtSignal(Serial)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__init_ui()

        self.__timer = QTimer(self)
        self.__timer.setInterval(1000)
        self.__timer.timeout.connect(self.update_device_list)
        self.__timer.start()

        self.__ser: Serial | None = None

    def __init_ui(self):
        layout = QVBoxLayout(self)

        cb_device = QComboBox()
        cb_device.currentIndexChanged.connect(self.update_port_selection)
        layout.addWidget(cb_device)
        self.__cb_device = cb_device

        self.setLayout(layout)

    def update_device_list(self):
        device_list = list_device_names()
        self.__cb_device.blockSignals(True)
        self.__cb_device.clear()
        self.__cb_device.addItem("<Select>")
        for device_name in device_list:
            self.__cb_device.addItem(device_name)
        self.__cb_device.blockSignals(False)

        if self.__ser is not None:
            try:
                i = device_list.index(self.__ser.port) + 1
            except ValueError:
                pass
            else:
                self.__cb_device.setCurrentIndex(i)

    def close_port(self):
        if self.__ser is None:
            return

        self.__ser.close()
        self.port_updated.emit(self.__ser)
        self.__ser = None

    def update_port_selection(self, index):
        device_name = self.__cb_device.itemText(index)
        print(device_name, self.__ser)
        if self.__ser is not None and self.__ser.port == device_name:
            return

        self.close_port()
        print("Closed")

        if device_name == "<Select>":
            return

        self.__ser = Serial(port=device_name, baudrate=9600, timeout=0.1)
        self.port_updated.emit(self.__ser)
        print(self.__ser)

    def showEvent(self, evt):
        self.update_device_list()

    def closeEvent(self, evt):
        self.close_port()

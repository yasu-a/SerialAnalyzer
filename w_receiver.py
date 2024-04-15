from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from serial import Serial, SerialException

from w_logger import LoggerWidget


class SerialReceiverViewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__init_ui()

        self.__timer = QTimer(self)
        self.__timer.setInterval(20)
        self.__timer.timeout.connect(self.update_log)
        self.__timer.start()

        self.__ser = None

    def __init_ui(self):
        layout = QVBoxLayout()

        te_log = LoggerWidget(self)
        layout.addWidget(te_log)
        self.__te_log = te_log

        self.setLayout(layout)

    def update_log(self):
        self.__timer.blockSignals(True)

        self.__te_log.dispatch_clear_later()

        try:
            if self.__ser is None:
                return
            if not self.__ser.in_waiting:
                return
            self.__te_log.session_begin()
            while self.__ser.in_waiting:
                values = self.__ser.read(2048)
                self.__te_log.append(values)
            self.__te_log.session_end()
        except SerialException:
            pass
        finally:
            self.__timer.blockSignals(False)

    @pyqtSlot(Serial)
    def update_port(self, ser: Serial):
        if ser.is_open:
            self.__ser = ser
        else:
            self.__ser = None

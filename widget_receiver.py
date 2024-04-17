from PyQt5.QtCore import *
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget

from serial_core import COMPortIOError
from status import g_get_status
from utils import g_ports, block_signals_context
from widget_logging_field import LogViewWidget, LogBuffer


class SerialReceiverViewWidget(QTabWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__buf = LogBuffer(self)

        self.__init_ui()

        self.__timer = QTimer(self)
        self.__timer.setInterval(10)
        self.__timer.timeout.connect(self.update_log)
        self.__timer.start()

    def __init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        logger = LogViewWidget(self)
        logger.setMinimumWidth(840)
        self.__buf.session_completed.connect(logger.update_by_session)
        layout.addWidget(logger)
        self.__logger = logger

    def update_log(self):
        self.__logger.dispatch_clear_later()
        with block_signals_context(self.__logger):
            if not g_ports.has_active():
                return
            active_io = g_ports.active_port_io

            try:
                n_available = active_io.n_available
                if n_available:
                    self.__buf.session_begin()
                    values = active_io.receive_bytes(n_available)
                    self.__buf.append(values)
                    self.__buf.session_end()
            except COMPortIOError as e:
                g_get_status().error(f"データを受信できません：{type(e).__name__}")

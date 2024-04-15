from PyQt5.QtWidgets import QWidget, QVBoxLayout

from w_config import SerialConfigWidget
from w_receiver import SerialReceiverViewWidget
from w_sender import SerialSenderWidget


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout(self)

        w_config = SerialConfigWidget(self)
        layout.addWidget(w_config)
        self.__w_config = w_config

        w_receiver = SerialReceiverViewWidget(self)
        w_config.port_updated.connect(w_receiver.update_port)
        layout.addWidget(w_receiver)
        self.__w_receiver = w_receiver

        w_sender = SerialSenderWidget(self)
        w_config.port_updated.connect(w_sender.update_port)
        layout.addWidget(w_sender)
        self.__w_sender = w_sender

        self.setLayout(layout)

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from widget_config import SerialConfigWidget
from widget_receiver import SerialReceiverViewWidget
from widget_sender import SerialSenderWidget


class MainWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        root_layout = QHBoxLayout(self)
        self.setLayout(root_layout)

        # left
        left_layout = QVBoxLayout(self)
        root_layout.addLayout(left_layout)

        w_config = SerialConfigWidget(self)
        left_layout.addWidget(w_config)
        self.__w_config = w_config

        # right
        right_layout = QVBoxLayout(self)
        root_layout.addLayout(right_layout)

        w_receiver = SerialReceiverViewWidget(self)
        right_layout.addWidget(w_receiver)
        self.__w_receiver = w_receiver

        w_sender = SerialSenderWidget(self)
        right_layout.addWidget(w_sender)
        self.__w_sender = w_sender

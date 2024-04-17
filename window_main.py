import psutil
from PyQt5.QtCore import QObject, QSize, QTimer
from PyQt5.QtWidgets import *

from status import StatusMessageHandler, register_message_handler, g_get_status
from widget_main import MainWidget


class AppStatusMessageHandler(StatusMessageHandler):
    def __init__(self, main_window: "MainWindow"):
        self.__main_window = main_window

    def info(self, message: str, tag: str = None):
        self.__main_window.set_status_message("info", message, tag)

    def error(self, message: str, tag: str = None):
        self.__main_window.set_status_message("error", message, tag)


class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine | self.Sunken)


class MainWindow(QMainWindow):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

        register_message_handler(AppStatusMessageHandler(main_window=self))

        timer = QTimer(self)
        timer.setInterval(1000)
        timer.timeout.connect(self.timer_timeout)
        timer.start()

    def __init_ui(self):
        w_main = MainWidget(self)
        self.setCentralWidget(w_main)

        self.resize(QSize(1200, 800))
        self.setWindowTitle("MoroMonitor Mk.1")

        status = QStatusBar(self)
        status.addPermanentWidget(VLine())
        self.cpu_label = QLabel(self)
        self.cpu_label.setFixedWidth(100)
        status.addPermanentWidget(self.cpu_label)
        self.setStatusBar(status)

    def showEvent(self, evt):
        g_get_status().info("COMポートを開いてください")

    def set_status_message(self, level, message, tag):
        if tag is None:
            if level == "error":
                message = f"<html><font color=\"red\">{message}</font></html>"
            elif level == "info":
                pass
            else:
                assert False, level
            self.statusBar().showMessage(message)
        elif tag == "cpu":
            self.cpu_label.setText(message)
        else:
            assert False, tag

    def timer_timeout(self):
        g_get_status().info("CPU: {:.0f}%".format(psutil.cpu_percent()), tag="cpu")

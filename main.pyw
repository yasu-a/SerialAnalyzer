import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import *
from w_main import MainWidget

_excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    _excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = my_exception_hook


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        w_main = MainWidget(self)
        self.setCentralWidget(w_main)

        self.resize(QSize(1000, 800))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.setFont(QFont("Consolas", 10))
    app.exec()

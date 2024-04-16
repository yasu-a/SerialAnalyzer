from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import *
from widget_main import MainWidget

if __name__ == '__main__':
    import sys

    sys._excepthook = sys.excepthook


    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)


    sys.excepthook = exception_hook


class MainWindow(QMainWindow):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        w_main = MainWidget(self)
        self.setCentralWidget(w_main)

        self.resize(QSize(1200, 800))
        self.setWindowTitle("MoroMonitor Mk.1")

        self.__status = QStatusBar(self)
        self.setStatusBar(self.__status)

    def showEvent(self, evt):
        self.__status.showMessage("COMポートを開いてください")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.setFont(QFont("Meiryo", 9))
    app.setStyle('Fusion')
    app.exec()

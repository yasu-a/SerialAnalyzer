from PyQt5.QtGui import *

from PyQt5.QtWidgets import *

if __name__ == '__main__':
    import sys

    sys._excepthook = sys.excepthook


    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)


    sys.excepthook = exception_hook

if __name__ == '__main__':
    app = QApplication(sys.argv)

    from window_main import MainWindow

    window = MainWindow()
    window.show()
    app.setFont(QFont("Meiryo", 9))
    app.setStyle('Fusion')
    app.exec()

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit


class LogFreezeDialog(QDialog):
    def __init__(self, parent=None, text=""):
        super().__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout()

        self.__te = QPlainTextEdit()
        self.__te.insertPlainText(text)
        self.__te.setReadOnly(True)
        layout.addWidget(self.__te)

        self.setLayout(layout)

        self.resize(QSize(1000, 500))

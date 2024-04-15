from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QCheckBox, \
    QPushButton

from d_freeze import LogFreezeDialog
from utils import decode_ascii


class SessionBuffer:
    def __init__(self, curent_line_no: int):
        self.__curent_line_no = curent_line_no
        self.__timestamp = datetime.now().time()
        self.__values = []

    def append_bytes(self, values: bytes):
        self.__values += list(values)

    BLOCK_SIZE = 16

    def __iter_blocks(self):
        i = 0
        while i < len(self.__values):
            block = self.__values[i:i + self.BLOCK_SIZE]
            yield block
            i += self.BLOCK_SIZE

    HEADER_LENGTH = 15

    def to_string(self):
        block_bytes = [
            " ".join("{:02x}".format(value) for value in block)
            for block in self.__iter_blocks()
        ]
        block_asciis = [
            "".join(decode_ascii(block, replace_error='・'))
            for block in self.__iter_blocks()
        ]
        block_headers = [
            str(self.__timestamp) if i == 0 else ""
            for i in range(len(block_bytes))
        ]
        lines = [
            f'{self.__curent_line_no + i:>5d} | {header.ljust(self.HEADER_LENGTH)} | {b.ljust(3 * self.BLOCK_SIZE)}| {a}'
            for i, (header, b, a) in enumerate(zip(block_headers, block_bytes, block_asciis))
        ]
        content = "\n".join(lines) + "\n"
        return content, self.__curent_line_no + len(block_headers)


class LoggerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__current_line_no = 1
        self.__clear_later = False
        self.__buf: None | SessionBuffer = None

        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout()

        field = QPlainTextEdit(self)
        field.setReadOnly(True)
        field.setTextInteractionFlags(Qt.NoTextInteraction)
        layout.addWidget(field)
        self.__field = field

        layout_control = QHBoxLayout()

        cb_scroll = QCheckBox(self)
        cb_scroll.setText("Autoscroll")
        cb_scroll.setChecked(True)
        layout_control.addWidget(cb_scroll)
        self.__cb_scroll = cb_scroll

        b_clear = QPushButton(self)
        b_clear.setText("Clear")
        b_clear.clicked.connect(self.clear_later)
        layout_control.addWidget(b_clear)

        b_freeze = QPushButton(self)
        b_freeze.setText("Freeze")
        b_freeze.clicked.connect(self.freeze)
        layout_control.addWidget(b_freeze)

        layout.addLayout(layout_control)

        self.setLayout(layout)

    def freeze(self):
        dialog = LogFreezeDialog(self, text=self.__field.document().toRawText())
        dialog.exec()

    def clear_later(self):
        self.__clear_later = True

    def dispatch_clear_later(self):
        if self.__clear_later:
            self.__clear_later = False
            self.__field.clear()

    def session_begin(self):
        self.__buf = SessionBuffer(curent_line_no=self.__current_line_no)

    def __scroll_to_bottom(self):
        if not self.__cb_scroll.isChecked():
            return

        sb = self.__field.verticalScrollBar()
        sb.setValue(sb.maximum())

    def session_end(self):
        content, self.__current_line_no = self.__buf.to_string()
        self.__field.insertPlainText(content)
        self.__buf = None
        self.__scroll_to_bottom()

    def append(self, values: bytes):
        assert isinstance(values, bytes)
        self.__buf.append_bytes(values)
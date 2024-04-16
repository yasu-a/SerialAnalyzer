from abc import ABC, abstractmethod
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QCheckBox, \
    QPushButton

from d_freeze import LogFreezeDialog
from utils import decode_ascii


class SessionBuffer(ABC):
    def __init__(self):
        self.__timestamp = datetime.now().time()
        self.__values = []

    def append_bytes(self, values: bytes):
        self.__values += list(values)

    @property
    def values(self) -> list[int]:
        return self.__values

    @property
    def timestamp(self):
        return self.__timestamp


class SessionBufferStringBuilder(ABC):
    def __init__(self, session_buffer: SessionBuffer):
        self.__session_buffer = session_buffer

    @property
    def _buf(self):
        return self.__session_buffer

    @abstractmethod
    def to_string(self):
        raise NotImplementedError()


class HexStringBuilder(SessionBufferStringBuilder):
    HEADER_LENGTH = 15
    BLOCK_SIZE = 16

    def _iter_blocks(self):
        i = 0
        while i < len(self._buf.values):
            block = self._buf.values[i:i + self.BLOCK_SIZE]
            yield block
            i += self.BLOCK_SIZE

    def to_string(self) -> str:
        block_bytes = [
            " ".join("{:02x}".format(value) for value in block)
            for block in self._iter_blocks()
        ]
        block_asciis = [
            "".join(decode_ascii(block, replace_error='・'))
            for block in self._iter_blocks()
        ]
        block_headers = [
            str(self._buf.timestamp) if i == 0 else ""
            for i in range(len(block_bytes))
        ]
        lines = [
            f'{1 + i:>5d} | {header.ljust(self.HEADER_LENGTH)} | {b.ljust(3 * self.BLOCK_SIZE)}| {a}'
            for i, (header, b, a) in enumerate(zip(block_headers, block_bytes, block_asciis))
        ]
        content = "\n".join(lines) + "\n"
        return content


class TextStringBuilder(SessionBufferStringBuilder):
    NEW_LINE = 0x0a

    def _iter_blocks(self):
        i = 0
        block = []
        while i < len(self._buf.values):
            value = self._buf.values[i]
            if value == self.NEW_LINE:
                yield block
                block.clear()
            else:
                block.append(decode_ascii(value))
            i += 1

    def to_string(self) -> str:
        content = decode_ascii(self._buf.values, replace_error='・', enable_spaces=True)
        return content


class LogBuffer(QObject):
    session_completed = pyqtSignal(SessionBuffer)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__buf: None | SessionBuffer = None

    def session_begin(self):
        self.__buf = SessionBuffer()

    def append(self, values: bytes):
        assert isinstance(values, bytes)
        self.__buf.append_bytes(values)

    def session_end(self):
        self.session_completed.emit(self.__buf)
        self.__buf = None


class LogViewWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__clear_later = False

        self.__init_ui()

    def __init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        field = QPlainTextEdit(self)
        field.setReadOnly(True)
        field.setFont(QFont("Consolas", 9))
        field.setTextInteractionFlags(Qt.NoTextInteraction)
        layout.addWidget(field)
        self.__field = field

        layout_control = QHBoxLayout()
        layout.addLayout(layout_control)

        cb_scroll = QCheckBox(self)
        cb_scroll.setText("自動スクロール")
        cb_scroll.setChecked(True)
        layout_control.addWidget(cb_scroll)
        self.__cb_scroll = cb_scroll

        cb_hex = QCheckBox(self)
        cb_hex.setText("16進数")
        cb_hex.setChecked(True)
        layout_control.addWidget(cb_hex)
        self.__cb_hex = cb_hex

        layout_control.addStretch(1)

        b_clear = QPushButton(self)
        b_clear.setText("クリア")
        b_clear.clicked.connect(self.clear_later)
        layout_control.addWidget(b_clear)

        b_freeze = QPushButton(self)
        b_freeze.setText("編集モード")
        b_freeze.clicked.connect(self.freeze)
        layout_control.addWidget(b_freeze)

    def __get_current_string_builder(self):
        if self.__cb_hex.isChecked():
            return HexStringBuilder
        else:
            return TextStringBuilder

    def freeze(self):
        dialog = LogFreezeDialog(self, text=self.__field.document().toRawText())
        dialog.exec()

    def clear_later(self):
        self.__clear_later = True

    def dispatch_clear_later(self):
        if self.__clear_later:
            self.__clear_later = False
            self.__field.clear()

    def __scroll_to_bottom(self):
        if not self.__cb_scroll.isChecked():
            return

        sb = self.__field.verticalScrollBar()
        sb.setValue(sb.maximum())

    @pyqtSlot(SessionBuffer)
    def update_by_session(self, buf: SessionBuffer):
        sb_cls = self.__get_current_string_builder()
        sb = sb_cls(buf)
        content = sb.to_string()
        self.__field.insertPlainText(content)
        self.__scroll_to_bottom()

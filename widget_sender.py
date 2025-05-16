import binascii
import collections

from PyQt5.QtCore import QObject, Qt, QEvent
from PyQt5.QtGui import QKeyEvent, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QCheckBox

from serial_core import COMPortIOError, COMPortOSError, COMPortClosedError
from status import g_get_status
from utils import decode_ascii, block_signals_context
from utils import g_ports


class SendBuffer:
    def __init__(self):
        self.__history: list[bytes] = []
        self.__pointer = None
        self.__buffer: bytes = b""

    def update_buffer(self, value: bytes):
        assert isinstance(value, bytes)
        self.__buffer = value

    def notify_flush(self):
        if self.__buffer:
            self.__history.append(self.__buffer)
        self.__buffer = b""
        self.__pointer = None

    def pointed(self) -> bytes:
        if self.__pointer is None:
            return self.__buffer
        else:
            try:
                return self.__history[-(self.__pointer + 1)]
            except IndexError:
                assert False

    def pointed_as_hex_text(self) -> str:
        return "".join("{:02x}".format(byte) for byte in self.pointed())

    def go_back_history(self):
        if self.__pointer is None:
            if len(self.__history) > 0:
                self.__pointer = 0
        else:
            if self.__pointer + 1 < len(self.__history):
                self.__pointer += 1
        print(self.__pointer, self.__history)

    def get_forward_history(self):
        if self.__pointer is not None:
            if -1 <= self.__pointer - 1:
                self.__pointer -= 1
            if self.__pointer < 0:
                self.__pointer = None
        print(self.__pointer, self.__history)


class SerialSenderWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__buf = SendBuffer()
        self.__state = None

        self.__init_ui()

    EMPTY_PLACEHOLDER_BYTES = "送信する16進数を入力してエンター 例：48656c6c6f2121"
    EMPTY_PLACEHOLDER_TEXT = "送信する文字列を入力してエンター 例：Hello!!"

    def __init_ui(self):
        layout = QVBoxLayout()

        e_bytes = QLineEdit(self)
        e_bytes.setFont(QFont("Consolas"))
        e_bytes.textChanged.connect(self.__e_bytes_changed)
        e_bytes.returnPressed.connect(self.flush)
        e_bytes.installEventFilter(self)
        layout.addWidget(e_bytes)
        self.__e_bytes = e_bytes

        e_text = QLineEdit(self)
        e_text.setFont(QFont("Consolas"))
        e_text.textChanged.connect(self.__e_text_changed)
        e_text.returnPressed.connect(self.flush)
        e_text.installEventFilter(self)
        layout.addWidget(e_text)
        self.__e_text = e_text

        cb_newline = QCheckBox(self)
        cb_newline.setText("改行コード\"\\n\"を送る")
        layout.addWidget(cb_newline)
        self.__cb_newline = cb_newline

        self.setLayout(layout)

        self.set_indicator(
            "empty",
            self.EMPTY_PLACEHOLDER_BYTES,
            self.EMPTY_PLACEHOLDER_TEXT,
            placeholder=True
        )

    def current_input_bytes(self) -> bytes:
        return bytes(bytearray.fromhex(self.__e_bytes.text()))

    def on_key_entered_on_line_edit(self, evt: QKeyEvent):
        if evt.key() == Qt.Key_Up:
            self.__buf.go_back_history()
            with block_signals_context(self.__e_bytes) as eb:
                eb.setText(self.__buf.pointed_as_hex_text())
            self.__notify_set_e_bytes(self.__buf.pointed_as_hex_text(), update_buffer=False)
        elif evt.key() == Qt.Key_Down:
            self.__buf.get_forward_history()
            with block_signals_context(self.__e_bytes) as eb:
                eb.setText(self.__buf.pointed_as_hex_text())
            self.__notify_set_e_bytes(self.__buf.pointed_as_hex_text(), update_buffer=False)

    def eventFilter(self, obj, evt):
        if obj in (self.__e_text, self.__e_bytes) and evt.type() == QEvent.KeyPress:
            assert isinstance(evt, QKeyEvent)
            self.on_key_entered_on_line_edit(evt)
        return super().eventFilter(obj, evt)

    def set_indicator(self, state: str, bytes_text: str | None, string_text: str | None,
                      placeholder=False):
        with block_signals_context(self.__e_bytes, self.__e_text) as (eb, et):

            if bytes_text is not None:
                if placeholder:
                    eb.setPlaceholderText(bytes_text)
                    eb.setText("")
                else:
                    eb.setText(bytes_text)
            if string_text is not None:
                if placeholder:
                    et.setPlaceholderText(string_text)
                    et.setText("")
                else:
                    et.setText(string_text)

            if state == "empty":
                eb.setStyleSheet("color: black; font-weight: normal;")
                et.setStyleSheet("color: black; font-weight: normal;")
            elif state == "ok_bytes":
                eb.setStyleSheet("color: green; font-weight: bold;")
                et.setStyleSheet("color: black; font-weight: normal;")
            elif state == "ok_bytes_but_ng_encoding":
                eb.setStyleSheet("color: green; font-weight: bold;")
                et.setStyleSheet("color: red; font-weight: bold;")
            elif state == "ok_text":
                eb.setStyleSheet("color: black; font-weight: normal;")
                et.setStyleSheet("color: green; font-weight: bold;")
            elif state == "ng_bytes":
                eb.setStyleSheet("color: red; font-weight: bold;")
                et.setStyleSheet("color: red; font-weight: bold;")
            elif state == "ng_text":
                eb.setStyleSheet("color: red; font-weight: bold;")
                et.setStyleSheet("color: red; font-weight: bold;")
            else:
                assert False, state
            self.__state = state

    def __notify_set_e_bytes(self, text, update_buffer=True):
        try:
            data = bytes(bytearray.fromhex(text))
            if update_buffer:
                self.__buf.update_buffer(data)
        except ValueError:
            self.set_indicator(
                "ng_bytes",
                None,
                "(MALFORMED BYTES)",
                placeholder=True,
            )
            return

        try:
            text = decode_ascii(data)
        except ValueError:
            self.set_indicator(
                "ok_bytes_but_ng_encoding",
                None,
                "(FAILED TO DECODE BYTES)",
                placeholder=True,
            )
        else:
            if self.__buf.pointed():
                self.set_indicator(
                    "ok_bytes",
                    None,
                    text,
                )
            else:
                self.set_indicator(
                    "empty",
                    self.EMPTY_PLACEHOLDER_BYTES,
                    self.EMPTY_PLACEHOLDER_TEXT,
                    placeholder=True
                )

    def __e_bytes_changed(self, text):
        self.__notify_set_e_bytes(text)

    def __e_text_changed(self, text):
        try:
            encoded_bytes = text.encode("latin-1")
            self.__buf.update_buffer(encoded_bytes)
            with block_signals_context(self.__e_bytes) as eb:
                eb.setText(binascii.hexlify(encoded_bytes).decode("latin-1"))
        except ValueError:
            self.set_indicator(
                "ng_text",
                "(FAILED TO ENCODE TEXT)",
                None,
                placeholder=True,
            )
            return

        if self.__buf.pointed():
            self.set_indicator(
                "ok_text",
                "".join(hex(value)[2:] for value in self.__buf.pointed()),
                None,
            )
        else:
            self.set_indicator(
                "empty",
                self.EMPTY_PLACEHOLDER_BYTES,
                self.EMPTY_PLACEHOLDER_TEXT,
                placeholder=True
            )

    def flush(self):
        fail = True
        bytes_sent = None

        try:
            if self.__cb_newline.isChecked():
                if self.__state.startswith("ok") or self.__state == "empty":
                    if g_ports.has_active():
                        bytes_sent = self.current_input_bytes() + b"\x0a"
                        g_ports.active_port_io.send_bytes(bytes_sent)
                        fail = False
                    else:
                        raise COMPortClosedError()
            else:
                if self.__state.startswith("ok"):
                    if g_ports.has_active():
                        bytes_sent = self.current_input_bytes()
                        g_ports.active_port_io.send_bytes(bytes_sent)
                        fail = False
                    else:
                        raise COMPortClosedError()
        except COMPortIOError as e:
            g_get_status().error(f"データを送信できません：{type(e).__name__}")

        if fail:
            return

        self.__buf.notify_flush()

        values = " ".join(f"{value:02x}" for value in bytes_sent)
        g_get_status().info(f"データを送信しました：{values}")

        self.set_indicator(
            "empty",
            self.EMPTY_PLACEHOLDER_BYTES,
            self.EMPTY_PLACEHOLDER_TEXT,
            placeholder=True
        )

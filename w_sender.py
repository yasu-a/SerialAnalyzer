from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from serial import Serial

from utils import decode_ascii


class SerialSenderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__values = b""
        self.__state = None

        self.__ser = None

        self.__init_ui()

    EMPTY_PLACEHOLDER_BYTES = "Enter bytes to send like \"48656c6c6f2121\""
    EMPTY_PLACEHOLDER_TEXT = "Enter text to send like \"Hello!!\""

    def __init_ui(self):
        layout = QVBoxLayout()

        e_bytes = QLineEdit(self)
        e_bytes.textChanged.connect(self.__le_bytes_changed)
        e_bytes.returnPressed.connect(self.flush)
        layout.addWidget(e_bytes)
        self.__e_bytes = e_bytes

        e_text = QLineEdit(self)
        e_text.textChanged.connect(self.__le_text_changed)
        e_text.returnPressed.connect(self.flush)
        layout.addWidget(e_text)
        self.__e_text = e_text

        self.setLayout(layout)

        self.set_indicator(
            "empty",
            self.EMPTY_PLACEHOLDER_BYTES,
            self.EMPTY_PLACEHOLDER_TEXT,
            placeholder=True
        )

    def set_indicator(self, state: str, bytes_text: str | None, string_text: str | None,
                      placeholder=False):
        eb, es = self.__e_bytes, self.__e_text
        try:
            eb.blockSignals(True)
            es.blockSignals(True)

            if bytes_text is not None:
                if placeholder:
                    eb.setPlaceholderText(bytes_text)
                    eb.setText("")
                else:
                    eb.setText(bytes_text)
            if string_text is not None:
                if placeholder:
                    es.setPlaceholderText(string_text)
                    es.setText("")
                else:
                    es.setText(string_text)

            if state == "empty":
                eb.setStyleSheet("color: black; font-weight: normal;")
                es.setStyleSheet("color: black; font-weight: normal;")
            elif state == "ok_bytes":
                eb.setStyleSheet("color: black; font-weight: bold;")
                es.setStyleSheet("color: green; font-weight: normal;")
            elif state == "ok_bytes_but_ng_encoding":
                eb.setStyleSheet("color: black; font-weight: bold;")
                es.setStyleSheet("color: red; font-weight: bold;")
            elif state == "ok_text":
                eb.setStyleSheet("color: green; font-weight: normal;")
                es.setStyleSheet("color: black; font-weight: bold;")
            elif state == "ng_bytes":
                eb.setStyleSheet("color: red; font-weight: bold;")
                es.setStyleSheet("color: red; font-weight: bold;")
            elif state == "ng_text":
                eb.setStyleSheet("color: blue; font-weight: bold;")
                es.setStyleSheet("color: red; font-weight: bold;")
            else:
                assert False, state
            self.__state = state
        finally:
            eb.blockSignals(False)
            es.blockSignals(False)

    def __le_bytes_changed(self, text):
        try:
            self.__values = bytearray.fromhex(text)
        except ValueError:
            self.set_indicator(
                "ng_bytes",
                None,
                "(MALFORMED BYTES)",
                placeholder=True,
            )
            return

        try:
            text = decode_ascii(self.__values)
        except ValueError:
            self.set_indicator(
                "ok_bytes_but_ng_encoding",
                None,
                "(FAILED TO DECODE BYTES)",
                placeholder=True,
            )
        else:
            if self.__values:
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

    def __le_text_changed(self, text):
        try:
            self.__values = text.encode("latin-1")
        except ValueError:
            self.set_indicator(
                "ng_text",
                "(FAILED TO ENCODE TEXT)",
                None,
                placeholder=True,
            )
            return

        if self.__values:
            self.set_indicator(
                "ok_text",
                "".join(hex(value)[2:] for value in self.__values),
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
        if not self.__state.startswith("ok"):
            return
        if self.__ser is not None:
            self.__ser.write(self.__values)
        self.set_indicator(
            "empty",
            self.EMPTY_PLACEHOLDER_BYTES,
            self.EMPTY_PLACEHOLDER_TEXT,
            placeholder=True
        )

    @pyqtSlot(Serial)
    def update_port(self, ser: Serial):
        if ser.is_open:
            self.__ser = ser
        else:
            self.__ser = None

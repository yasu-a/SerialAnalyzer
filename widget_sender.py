from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QCheckBox

from serial_core import COMPortIOError
from utils import decode_ascii, find_main_window
from utils import g_ports


class SerialSenderWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__values = b""
        self.__state = None

        self.__init_ui()

    EMPTY_PLACEHOLDER_BYTES = "ここに送信する16進数を入力してエンター \"48656c6c6f2121\""
    EMPTY_PLACEHOLDER_TEXT = "ここに送信する文字を入力してエンター \"Hello!!\""

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
                eb.setStyleSheet("color: red; font-weight: bold;")
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
        fail = True
        try:
            if self.__cb_newline.isChecked():
                if self.__state.startswith("ok") or self.__state == "empty":
                    if g_ports.has_active():
                        g_ports.active_port_io.send_bytes(self.__values + b"\x0a")
                        fail = False
            else:
                if self.__state.startswith("ok"):
                    if g_ports.has_active():
                        g_ports.active_port_io.send_bytes(self.__values)
                        fail = False
        except COMPortIOError as e:
            main_window = find_main_window()
            if main_window:
                main_window.statusBar().showMessage(
                    f"データの送信に失敗しました：{type(e).__name__}"
                )

        if fail:
            return

        main_window = find_main_window()
        if main_window:
            values = " ".join(f"{value:02x}" for value in self.__values)
            main_window.statusBar().showMessage(f"Data sent: {values}")
        self.__values = b""
        self.set_indicator(
            "empty",
            self.EMPTY_PLACEHOLDER_BYTES,
            self.EMPTY_PLACEHOLDER_TEXT,
            placeholder=True
        )

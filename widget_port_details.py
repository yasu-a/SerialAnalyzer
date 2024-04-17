import collections
from collections import OrderedDict
from datetime import time, datetime

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from utils import g_ports


def maybe_datetime_to_time_string(maybe_datetime: datetime | None) -> str:
    return "-" if maybe_datetime is None else str(maybe_datetime.time())[:-7]


class PortDetailWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

    def __init_ui(self):
        self.setFixedWidth(200)

        layout = QGridLayout(self)
        self.setLayout(layout)

    def set_values_on_view(self, mapping):
        layout: QGridLayout = self.layout()

        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

        for i_row, key in enumerate(mapping):
            label = QLabel(self)
            label.setText(key)
            layout.addWidget(label, i_row, 0)

            label = QLabel(self)
            label.setText(mapping[key])
            layout.addWidget(label, i_row, 1)

    KEY_MAPPER = OrderedDict([
        ("name", "名前"),
        ("state", "状態"),
        ("baudrate", "BAUD"),
        ("created_at", "開始"),
        ("accessed_at", "アクセス"),
        ("received_at", "受信"),
        ("total_n_received", "受信量"),
        ("sent_at", "送信"),
        ("total_n_sent", "送信量"),
    ])

    KEY_ORDER = collections.defaultdict(lambda: 999, {k: i for i, k in enumerate(KEY_MAPPER)})
    print(KEY_ORDER)
    VALUE_MAPPER = {
        "received_at": maybe_datetime_to_time_string,
        "sent_at": maybe_datetime_to_time_string,
        "created_at": maybe_datetime_to_time_string,
        "accessed_at": maybe_datetime_to_time_string,
    }

    FORMATS = {
        "baudrate": "{} baud",
        "total_n_received": "{:,} bytes",
        "total_n_sent": "{:,} bytes",
    }

    @classmethod
    def map_serial_info(cls, serial_info: dict):
        result = OrderedDict()
        keys = sorted(serial_info.keys(), key=cls.KEY_ORDER.__getitem__)
        for k in keys:
            v = serial_info[k]
            v = cls.VALUE_MAPPER.get(k, lambda x: x)(v)
            v = cls.FORMATS.get(k, "{}").format(v)
            k = cls.KEY_MAPPER.get(k, k)
            result[k] = v
        return result

    @pyqtSlot()
    def update_port_info(self):
        if g_ports.has_active():
            serial_info = self.map_serial_info(g_ports.active_port_info)
            self.set_values_on_view(serial_info)
            self.setEnabled(True)
        else:
            self.setEnabled(False)

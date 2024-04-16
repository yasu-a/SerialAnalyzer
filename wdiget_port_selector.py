from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QCheckBox

from utils import g_ports, block_signals_context, COMPortState


class PortListWidget(QWidget):
    any_state_changed = pyqtSignal()

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.__init_ui()

        self.__previous_state_list: list[COMPortState] = g_ports.state_list

        self.__port_list_update_timer = QTimer(self)
        self.__port_list_update_timer.setInterval(500)
        self.__port_list_update_timer.timeout.connect(self.update_port_list)
        self.__port_list_update_timer.start()

    def __init_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        l_ports = QListWidget(self)
        l_ports.setMinimumHeight(30)
        l_ports.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        l_ports.clicked.connect(self.port_selection_clicked)
        layout.addWidget(l_ports)
        self.__l_ports = l_ports

        cb_auto_connect = QCheckBox(self)
        cb_auto_connect.setText("Auto connect")
        layout.addWidget(cb_auto_connect)
        self.__cb_auto_connect = cb_auto_connect

    LIST_ITEM_TEXT_DISCONNECT = "<DISCONNECTED>"

    def __add_item(self, name: str | None):
        if name is None:
            text = self.LIST_ITEM_TEXT_DISCONNECT
        else:
            text = f"{name} {g_ports.get_port_state(name).value.replace('DISCONNECTED', '')}"
        self.__l_ports.addItem(text)
        if name is not None:
            if g_ports.get_port_state(name) == COMPortState.DISCONNECTED:
                item = self.__l_ports.item(self.__l_ports.count() - 1)
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

    def _reflect_port_list(self):
        with block_signals_context(self.__l_ports) as l:
            l.clear()
            self.__add_item(None)
            for value in g_ports.name_list:
                self.__add_item(value)

            if not g_ports.has_active():
                l.setCurrentRow(0)
            else:
                if g_ports.active_port_state == COMPortState.DISCONNECTED:
                    l.setCurrentRow(0)
                else:
                    i = g_ports.name_list.index(g_ports.active_port_name)
                    l.setCurrentRow(i + 1)

    def __get_selected_item(self) -> str | None:
        if self.__l_ports.currentRow() == 0:
            return None
        else:
            item_text = self.__l_ports.currentItem().text()
            port_name = item_text.split(" ")[0]
            return port_name

    def process_auto_connect(self):
        if self.__cb_auto_connect.isChecked():
            if not g_ports.has_active():
                try:
                    i = g_ports.state_list.index(COMPortState.CLOSED)
                except ValueError:
                    pass
                else:
                    g_ports.activate_one(g_ports.name_list[i])

    def update_port_list(self):
        g_ports.update_connection_state()

        state_list = g_ports.state_list
        changed = (
                self.__previous_state_list is not None
                and state_list != self.__previous_state_list
        )
        self.__previous_state_list = state_list

        if changed:
            self._reflect_port_list()
            self.any_state_changed.emit()

        self.process_auto_connect()

    def port_selection_clicked(self):
        if g_ports.has_active():
            current_port_name = g_ports.active_port_name
        else:
            current_port_name = None

        new_port_name = self.__get_selected_item()

        if current_port_name == new_port_name:
            return

        g_ports.activate_one(new_port_name)
        self.any_state_changed.emit()

    def showEvent(self, evt):
        self._reflect_port_list()

    def closeEvent(self, evt):
        self.__port_list_update_timer.stop()
        g_ports.activate_one(None)

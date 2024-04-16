import contextlib
from dataclasses import dataclass
from enum import Enum

from PyQt5.QtWidgets import QMainWindow, QApplication

from serial_core import *


def decode_ascii(values: bytes | list[int], replace_error=None, enable_spaces=False):
    if not isinstance(values, list):
        values = list(values)
    assert isinstance(values, list)
    for i in range(len(values)):
        value = values[i]
        if enable_spaces:
            error = 0x7d < value
        else:
            error = value < 0x20 or 0x7d < value
        if error:
            if replace_error is not None:
                values[i] = None
            else:
                raise ValueError()
    return "".join(replace_error if value is None else chr(value) for value in values)


def find_main_window() -> QMainWindow | None:
    # Global function to find the (open) QMainWindow in application
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
    return None


@contextlib.contextmanager
def block_signals_context(*objects):
    assert len(objects) > 0

    try:
        for obj in objects:
            obj.blockSignals(True)

        if len(objects) == 1:
            yield objects[0]
        else:
            yield objects
    finally:
        for obj in objects:
            obj.blockSignals(False)


class COMPortState(Enum):
    DISCONNECTED = "DISCONNECTED"
    CLOSED = "CLOSED"
    OPEN = "OPEN"


class COMPort:
    def __init__(self, device_name):
        self.__is_connected = False
        self.__conn: COMPortConnection = COMPortConnection(device_name)

    def _set_connected(self, value: bool):
        if not value:
            self.deactivate()
        self.__is_connected = value

    def update_connection_state(self, connected_device_names):
        self._set_connected(self.__conn.device_name in connected_device_names)

    @property
    def state(self) -> COMPortState:
        if not self.__is_connected:
            return COMPortState.DISCONNECTED
        else:
            if self.__conn.alive:
                return COMPortState.OPEN
            else:
                return COMPortState.CLOSED

    def activate(self):
        if self.state == COMPortState.CLOSED:
            self.__conn.open()

    def deactivate(self):
        if self.state == COMPortState.OPEN:
            self.__conn.close()

    @property
    def device_name(self):
        return self.__conn.device_name

    @property
    def serial_info(self) -> dict:
        info = self.__conn.info or {}
        info["name"] = self.device_name
        info["state"] = str(self.state.value)
        return info

    @property
    def io(self):
        return self.__conn.io

    def __repr__(self):
        return f"<COMPort {self.serial_info}>"


class COMPortSet:
    def __init__(self):
        names = [f"COM{i}" for i in range(1, 8 + 1)]
        self.__ports: dict[str, COMPort] = {name: COMPort(name) for name in names}

    def update_connection_state(self):
        device_name_list = list_device_names()
        for port in self.__ports.values():
            port.update_connection_state(device_name_list)

    @property
    def name_list(self) -> list[str]:
        return [port.device_name for port in self.__ports.values()]

    @property
    def state_list(self) -> list[COMPortState]:
        return [port.state for port in self.__ports.values()]

    def activate_one(self, target_name: str | None):
        assert target_name is None or target_name in self.__ports, target_name
        for name, port in self.__ports.items():
            if name == target_name:
                port.activate()
            else:
                port.deactivate()

    def __get_current_port(self) -> COMPort | None:
        for port in self.__ports.values():
            if port.state == COMPortState.OPEN:
                return port
        return None

    def __get_current_one_port(self) -> COMPort:
        current = self.__get_current_port()
        assert current is not None
        return current

    def has_active(self):
        return self.__get_current_port() is not None

    @property
    def active_port_info(self):
        return self.__get_current_one_port().serial_info

    @property
    def active_port_state(self) -> COMPortState:
        return self.__get_current_one_port().state

    def get_port_state(self, name: str) -> COMPortState:
        return self.__ports[name].state

    @property
    def active_port_io(self):
        return self.__get_current_one_port().io

    @property
    def active_port_name(self):
        return self.__get_current_one_port().device_name


g_ports = COMPortSet()

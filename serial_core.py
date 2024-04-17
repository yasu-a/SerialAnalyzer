from dataclasses import dataclass
from enum import Enum

from serial import Serial

__all__ = (
    "list_device_names",
    "COMPortConnection",
)


def list_device_names() -> list[str]:
    from serial.tools import list_ports

    ports = list_ports.comports()
    return sorted(port.device for port in ports)


class COMPortConnection:
    def __init__(self, device_name):
        self.__device_name = device_name
        self.__ser: Serial | None = None

    @property
    def device_name(self):
        return self.__device_name

    def open(self, **pyserial_params):
        assert self.__ser is None
        self.__ser = Serial(self.__device_name, **pyserial_params)

    def close(self):
        assert self.__ser is not None
        self.__ser.close()
        self.__ser = None

    @property
    def alive(self):
        if self.__ser:
            return self.__ser.is_open
        else:
            return False

    @property
    def io(self):
        return COMPortIO(self, self.__ser)

    @property
    def info(self) -> dict | None:
        if self.__ser:
            return {
                "baudrate": self.__ser.baudrate,
            }
        else:
            return None


class COMPortIOError(RuntimeError):
    pass


class COMPortOSError(COMPortIOError):
    pass


class COMPortClosedError(COMPortIOError):
    pass


class COMPortIO:
    def __init__(self, conn: "COMPortConnection", ser: Serial):
        self.__conn = conn
        self.__ser = ser

    def send_bytes(self, values: bytes) -> None:
        if self.__ser:
            try:
                self.__ser.write(values)
            except OSError:
                raise COMPortOSError()
            else:
                return
        else:
            raise COMPortClosedError()

    def receive_bytes(self, size) -> bytes:
        if self.__ser:
            try:
                data = self.__ser.read(size)
            except OSError:
                raise COMPortOSError()
            else:
                return data
        else:
            raise COMPortClosedError()

    @property
    def n_available(self) -> int:
        if self.__ser:
            try:
                return self.__ser.in_waiting
            except OSError:
                raise COMPortOSError()
        else:
            raise COMPortClosedError()

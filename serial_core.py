import sys
import traceback
from dataclasses import dataclass
from datetime import datetime

from PyQt5.QtCore import QMutex
from serial import Serial, SerialException

__all__ = (
    "list_device_names",
    "COMPortConnection",
)


def list_device_names() -> list[str]:
    from serial.tools import list_ports

    ports = list_ports.comports()
    return sorted(port.device for port in ports)


@dataclass(frozen=False)
class COMPortStat:
    mutex: QMutex
    created_at: datetime | None = None
    sent_at: datetime | None = None
    received_at: datetime | None = None
    total_n_sent: int = 0
    total_n_received: int = 0

    @classmethod
    def create_instance(cls):
        return cls(
            mutex=QMutex(),
        )

    def to_info(self) -> dict:
        return {
            "created_at": self.created_at,
            "sent_at": self.sent_at,
            "received_at": self.received_at,
            "total_n_sent": self.total_n_sent,
            "total_n_received": self.total_n_received,
            "accessed_at": self.accessed_at,
        }

    def __enter__(self):
        self.mutex.lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mutex.unlock()
        return False

    @property
    def accessed_at(self) -> datetime | None:
        def latest(x: datetime | None, y: datetime | None):
            vx = x.timestamp() if x else 0
            vy = y.timestamp() if y else 0
            if vx < vy:
                return y
            else:
                return x

        return latest(self.sent_at, self.received_at)


class COMPortConnection:
    def __init__(self, device_name):
        self.__device_name = device_name
        self.__ser: Serial | None = None
        self.__stat = COMPortStat.create_instance()

    @property
    def device_name(self):
        return self.__device_name

    def open(self, **pyserial_params):
        assert self.__ser is None
        try:
            self.__ser = Serial(self.__device_name, **pyserial_params)
        except SerialException as e:
            print(e, file=sys.stderr)
            self.__ser = None
        else:
            with self.__stat as stat:
                stat.created_at = datetime.now()

    def close(self):
        assert self.__ser is not None
        self.__ser.close()
        self.__ser = None
        with self.__stat as stat:
            stat.created_at = None

    @property
    def alive(self):
        if self.__ser:
            return self.__ser.is_open
        else:
            return False

    @property
    def io(self):
        return COMPortIO(self, self.__ser, self.__stat)

    @property
    def info(self) -> dict | None:
        if self.__ser:
            return {
                "baudrate": self.__ser.baudrate,
                **self.__stat.to_info(),
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
    def __init__(self, conn: "COMPortConnection", ser: Serial, stat: COMPortStat):
        self.__conn = conn
        self.__ser = ser
        self.__stat = stat

    def send_bytes(self, values: bytes) -> None:
        if self.__ser:
            try:
                n_sent = self.__ser.write(values)
                with self.__stat as stat:
                    stat.sent_at = datetime.now()
                    stat.total_n_sent += n_sent
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
                with self.__stat as stat:
                    stat.received_at = datetime.now()
                    stat.total_n_received += len(data)
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

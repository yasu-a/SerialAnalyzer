from serial.tools import list_ports


def decode_ascii(values: bytes | list[int], replace_error=None):
    if not isinstance(values, list):
        values = list(values)
    assert isinstance(values, list)
    for i in range(len(values)):
        value = values[i]
        if value < 0x20 or 0x7d < value:
            if replace_error is not None:
                values[i] = None
            else:
                raise ValueError()
    return "".join(replace_error if value is None else chr(value) for value in values)


def list_device_names() -> list[str]:
    ports = list_ports.comports()
    return [port.device for port in ports]

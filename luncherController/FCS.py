"""FCS: decodes the controller status packet (48 bytes, big-endian, UDP 192.168.109.1:5000 -> 192.168.109.201:5005).

Offsets follow the PLC layout %MB200.. (byte 0 = MB200). Pure parsing, no Qt, no sockets.
"""
import struct

FCS_LEN = 48

_FLOATS = {  # name: offset (REAL, big-endian)
    "Pan_ActPos": 2,
    "Tilt_ActPos": 6,
    "LRF_Dis": 10,
    "LRF_Vel": 14,
    "Temprature": 18,
    "Humidity": 22,
    "R_Spare201": 26,
    "R_Spare202": 30,
}

# bit flags: name -> (byte offset, bit index)
_BITS = {
    "Pan_Servo_OnStatus": (42, 0),
    "Pan_Servo_Fault": (42, 1),
    "Pan_Servo_Hlimit": (42, 2),
    "Pan_Servo_Llimit": (42, 3),
    "Pan_Servo_Homed": (42, 4),
    "Tilt_Servo_OnStatus": (43, 0),
    "Tilt_Servo_Fault": (43, 1),
    "Tilt_Servo_Hlimit": (43, 2),
    "Tilt_Servo_Llimit": (43, 3),
    "Tilt_Servo_Homed": (43, 4),
    "AutoMode": (44, 0),
    "Servos_On": (44, 1),
    "Servos_Homed": (44, 2),
    "Camera_Status": (44, 3),
}


def FCS(data: bytes) -> dict:
    """Return a dict with all named fields of one 48-byte controller packet.

    Raises ValueError if the length is wrong.
    """
    if len(data) != FCS_LEN:
        raise ValueError(f"FCS: expected {FCS_LEN} bytes, got {len(data)}")

    out = {"ID3": struct.unpack_from(">H", data, 0)[0]}
    for name, off in _FLOATS.items():
        out[name] = struct.unpack_from(">f", data, off)[0]
    out["Heartbeat"] = struct.unpack_from(">I", data, 34)[0]
    out["Fire_ShootNo"] = struct.unpack_from(">H", data, 38)[0]
    out["W_Spare203"] = struct.unpack_from(">H", data, 40)[0]
    for name, (off, bit) in _BITS.items():
        out[name] = bool((data[off] >> bit) & 1)
    out["ID4"] = struct.unpack_from(">H", data, 46)[0]
    return out


# ---------------------------------------------------------------- receiver
import time

from udp.UDPReceiver import UDPReceiver


def format_fcs(fields: dict) -> str:
    """One log line per packet: name=value pairs, ASCII only."""
    parts = []
    for name, val in fields.items():
        if isinstance(val, bool):
            if val:
                parts.append(name)  # only TRUE flags, keeps line short
        elif isinstance(val, float):
            parts.append(f"{name}={val:.4f}")
        else:
            parts.append(f"{name}={val}")
    return " | ".join(parts)


class FcsReceiver:
    """Decodes and logs every controller packet. Reading is done by UDPReceiver."""

    def __init__(self, bind_ip="", port=5005, log_path=None):
        self._log_path = log_path
        self.last = None  # latest decoded packet (dict), read by LCS
        self._rx = UDPReceiver(bind_ip, port, on_packet=self._on_packet)

    @property
    def count(self):
        return self._rx.count

    def start(self):
        self._rx.start()

    def stop(self):
        self._rx.stop()

    def _log(self, line):
        # print(line, flush=True)
        if self._log_path:
            with open(self._log_path, "a", encoding="ascii", errors="replace") as f:
                f.write(line + "\n")

    def _on_packet(self, data, src):
        n = self._rx.count
        stamp = time.strftime("%H:%M:%S")
        if len(data) != FCS_LEN:
            self._log(f"[{stamp}] [RX FCS] #{n} from {src[0]}:{src[1]} len={len(data)} (ignored, expected {FCS_LEN})")
            return
        try:
            fields = FCS(data)
        except ValueError as e:
            self._log(f"[{stamp}] [RX FCS] #{n} decode error: {e}")
            return
        self.last = fields
        self._log(f"[{stamp}] [RX FCS] #{n} from {src[0]}:{src[1]} | {format_fcs(fields)}")

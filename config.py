"""Read settings from the .env file (no extra packages needed).

Usage:
    from config import cfg
    cfg("PLC_IP")              -> "192.168.109.1"
    cfg("PLC_PORT", 5000)      -> 5000 (number, because the default is a number)
    cfg("PULSE_S")             -> 0.3

Priority: real environment variable > .env file > default you pass in.
"""
import os
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent / ".env"
_values = {}


def _load():
    if not _ENV_FILE.exists():
        return
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        _values[key.strip()] = value.strip()


def cfg(name, default=None):
    """Return the setting as text, or as a number if the default is a number."""
    if name in os.environ:
        raw = os.environ[name]
    elif name in _values:
        raw = _values[name]
    else:
        return default

    if isinstance(default, bool):
        return raw.lower() in ("1", "true", "yes", "on")
    if isinstance(default, int):
        return int(raw)
    if isinstance(default, float):
        return float(raw)
    return raw


_load()

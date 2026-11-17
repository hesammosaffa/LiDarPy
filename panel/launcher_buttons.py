"""Launcher mode buttons.
Each click sends ONE pulse (bit = 1, wait, bit = 0) from its own thread.
The sender must be the SAME UDPSender that LCS uses (lcs._sender)."""
import threading
import time

PULSE_S = 0.3   # how long the bit stays 1 (must be longer than the send interval)


def pulse(set_bit):
    """Set the bit to 1, wait, then set it back to 0."""
    set_bit(1)
    time.sleep(PULSE_S)
    set_bit(0)


def run_once(action, lock):
    """Run `action` in a new thread. If the last run is still going, skip this click."""
    if not lock.acquire(blocking=False):
        return

    def worker():
        try:
            action()
        finally:
            lock.release()

    threading.Thread(target=worker, daemon=True).start()


def connect_buttons(ui, sender):
    """ui = find-widget function, sender = the UDPSender used by LCS."""
    actions = {
        "btnServoOn":  lambda: pulse(sender.set_pb_ServoOn),
        "btnServoOff": lambda: pulse(sender.set_pb_ServoOff),
        "btnHome":     lambda: pulse(sender.set_pb_home),
        "btnAuto":     lambda: pulse(sender.set_pb_auto),
    }
    for name, action in actions.items():
        lock = threading.Lock()     # one lock per button
        ui(name).clicked.connect(lambda checked=False, a=action, l=lock: run_once(a, l))

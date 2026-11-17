"""Feedback: shows PLC status on the UI whenever it changes.

No new socket, no waiting thread. A QTimer (GUI thread) looks at the latest
packet kept by FcsReceiver (fcs_rx.last) every 100 ms. Nothing blocks, so it
does not matter how long the PLC takes to answer.
"""
from PySide6.QtCore import QObject, QTimer, Signal

# FCS key -> label shown to the user (add more lines to show more status)
STATUS = {
    "Servos_On":     "Servo On",
    "Servos_Homed":  "Homed",
    "AutoMode":      "Auto",
    "Pan_Servo_Fault":  "Pan Fault",
    "Tilt_Servo_Fault": "Tilt Fault",
}


class Feedback(QObject):
    # emitted ONLY when a status value changes: (label, new_value)
    changed = Signal(str, bool)

    def __init__(self, fcs_rx, period_ms=100):
        super().__init__()
        self._fcs = fcs_rx
        self._old = {}
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check)
        self._timer.start(period_ms)

    def _check(self):
        fb = self._fcs.last           # newest packet, or None before the first one
        if not fb:
            return
        for key, label in STATUS.items():
            value = fb[key]
            if self._old.get(key) != value:      # changed since last check?
                self._old[key] = value
                self.changed.emit(label, value)


def show_feedback(fcs_rx, statusbar_or_print=print):
    """Simplest use: print every change. Replace `print` with a UI function."""
    fb = Feedback(fcs_rx)
    fb.changed.connect(lambda label, v: statusbar_or_print(f"{label}: {'ON' if v else 'OFF'}"))
    return fb


# ---------------------------------------------------------------- button colors
# button name -> (FCS key, value that means "active")
BUTTONS = {
    "btnServoOn":  ("Servos_On", True),
    "btnServoOff": ("Servos_On", False),   # green when servos are OFF
    "btnHome":     ("Servos_Homed", True),
    "btnAuto":     ("AutoMode", True),
}
GREEN = "background-color: #b7e4c7; color: #1b4332;"   # light green


def color_buttons(ui, fcs_rx, period_ms=100):
    """Light-green button when its feedback is active, original look otherwise.
    Runs in the GUI thread through a QTimer: nothing blocks."""
    buttons = {n: ui(n) for n in BUTTONS}
    original = {n: b.styleSheet() for n, b in buttons.items()}   # remember the look
    state = {}

    def check():
        fb = fcs_rx.last
        if not fb:
            return
        for name, (key, wanted) in BUTTONS.items():
            active = (fb[key] == wanted)
            if state.get(name) != active:          # only touch the button on change
                state[name] = active
                buttons[name].setStyleSheet(
                    original[name] + GREEN if active else original[name])

    timer = QTimer()
    timer.timeout.connect(check)
    timer.start(period_ms)
    return timer          # keep it in a variable

"""Loads the layout from mainwindow.ui (edit it in Qt Designer). Logic only here."""
import sys
from pathlib import Path
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

from app.lidar_view import LidarView
from app.widgets import ToggleSwitch, GaugePanel
from luncherController.FCS import FcsReceiver
from luncherController.LCS import LCS
import luncherController.LCS as lcs_mod
from pid.PID import PanTiltPID
from config import cfg


UI = Path(__file__).resolve().parent / "ui" / "mainwindow.ui"


def load_ui():
    loader = QUiLoader()
    for cls in (LidarView, ToggleSwitch, GaugePanel):
        loader.registerCustomWidget(cls)
    f = QFile(str(UI)); f.open(QFile.ReadOnly)
    win = loader.load(f); f.close()
    if win is None:
        raise RuntimeError(f"cannot load {UI}")
    return win


def main():
    app = QApplication(sys.argv)
    w = load_ui()
    ui = lambda n: w.findChild(object, n)

    view, swSearch, swStatic = ui("lidarView"), ui("swSearch"), ui("swStatic")

    # ---- PID: one shared instance, gains read from the UI spin boxes ----
    shared_pid = PanTiltPID()

    def apply_pid(*_):
        shared_pid.pan.kp, shared_pid.pan.ki, shared_pid.pan.kd = (
            ui("kpPan").value(), ui("kiPan").value(), ui("kdPan").value())
        shared_pid.tilt.kp, shared_pid.tilt.ki, shared_pid.tilt.kd = (
            ui("kpTilt").value(), ui("kiTilt").value(), ui("kdTilt").value())

    for n in ("kpPan", "kiPan", "kdPan", "kpTilt", "kiTilt", "kdTilt"):
        ui(n).valueChanged.connect(apply_pid)
    apply_pid()
    # LCS.set_xyz builds PanTiltPID(...) on each call; make it return the shared instance
    lcs_mod.PanTiltPID = lambda **kw: shared_pid

    fcs_rx = FcsReceiver(
        cfg("FEEDBACK_LISTEN_IP", ""),
        cfg("FEEDBACK_LISTEN_PORT", 5005),
        log_path=cfg("FEEDBACK_LOG_FILE", "fcs_log.txt"),
    )
    fcs_rx.start()

    lcs = LCS(
        cfg("PLC_IP_ADDRESS", "192.168.109.1"),
        cfg("PLC_COMMAND_PORT", 5000),
        log_path=cfg("COMMAND_LOG_FILE", "lcs_log.txt"),
        view=view,
        fcs=fcs_rx,
    )
    lcs.start()

    rangeSpin = ui("rangeSpin")
    swSearch.toggled.connect(lambda on: view.set_probe_enabled(not on))
    view.set_probe_enabled(not swSearch.isChecked())
    swStatic.toggled.connect(view.set_hide_static)
    view.set_max_range(rangeSpin.value())
    rangeSpin.valueChanged.connect(view.set_max_range)
    gauge_pan, gauge_tilt = ui("gauge1"), ui("gauge2")
    # Tilt: half-dial, +90 at top, 0 at right, -90 at bottom (matches the sketch)
    gauge_tilt.set_arc(180.0, -180.0)

    state = {"locked": False}

    def probe(locked, x, y, z, vx, vy, vz, v):
        state["locked"] = bool(locked)
        if locked:
            lcs.set_xyz(x, y, z)
        # Gauges show measured angles from the FCS feedback (degrees, 0 = center)
        act = fcs_rx.last
        if act is not None:
            gauge_pan.set_value(act["Pan_ActPos"])
            gauge_tilt.set_value(act["Tilt_ActPos"])

    view.probeChanged.connect(probe)
    # Motion pad: jog the set-point by the selected step (only while NOT locked).
    # Units of the step = units of Pan_SetPos/Tilt_SetPos (assumed degrees; confirm).
    def step_value():
        steps = (("step01", cfg("JOG_STEP_0_1", 0.1)), ("step05", cfg("JOG_STEP_0_5", 0.5)),
                 ("step1", cfg("JOG_STEP_1", 1.0)), ("step10", cfg("JOG_STEP_10", 10.0)),
                 ("step100", cfg("JOG_STEP_100", 100.0)))
        for n, v in steps:
            w = ui(n)
            if w is not None and w.isChecked():
                return v
        return 1.0

    def jog(dp, dt):
        if state["locked"]:
            return
        d = lcs._sender.data
        d["Pan_SetPos"] = d["Pan_SetPos"] + dp * step_value()
        d["Tilt_SetPos"] = d["Tilt_SetPos"] + dt * step_value()

    def center():
        if state["locked"]:
            return
        lcs._sender.data["Pan_SetPos"] = 0.0
        lcs._sender.data["Tilt_SetPos"] = 0.0

    for name, fn in (("padLeft", lambda: jog(-1, 0)), ("padRight", lambda: jog(1, 0)),
                     ("padUp", lambda: jog(0, 1)), ("padDown", lambda: jog(0, -1)),
                     ("padCenter", center)):
        b = ui(name)
        if b is not None:
            b.clicked.connect(fn)

    fire_btn = ui("pushButton")   # FIRE button in mainwindow.ui (was "firePushButton")
    fire_sw = ui("swFire")
    if fire_btn and fire_sw:
        def sync_fire(on):
            fire_btn.setEnabled(on)
            fire_btn.setText("FIRE" if on else "FIRE\nLock")
            if not on:
                lcs.fire_off()
        fire_sw.toggled.connect(sync_fire)
        sync_fire(fire_sw.isChecked())
        fire_btn.pressed.connect(lcs.fire_on)
        fire_btn.released.connect(lcs.fire_off)

    app.aboutToQuit.connect(fcs_rx.stop)
    app.aboutToQuit.connect(view.shutdown)
    app.aboutToQuit.connect(lcs.stop)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

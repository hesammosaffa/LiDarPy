"""Loads the layout from mainwindow.ui (edit it in Qt Designer). Logic only here."""
import sys
from pathlib import Path
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from app.lidar_view import LidarView
from app.widgets import ToggleSwitch, GaugePanel

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
    rangeSpin = ui("rangeSpin")
    swSearch.toggled.connect(lambda on: view.set_probe_enabled(not on))
    view.set_probe_enabled(not swSearch.isChecked())
    swStatic.toggled.connect(view.set_hide_static)
    view.set_max_range(rangeSpin.value())
    rangeSpin.valueChanged.connect(view.set_max_range)
    g = [ui(n) for n in ("gVx", "gVy", "gVz", "gV")]

    def probe(locked, x, y, z, vx, vy, vz, v):
        for gg, val in zip(g, (vx, vy, vz, v)):
            gg.set_value(val)
    view.probeChanged.connect(probe)
    app.aboutToQuit.connect(view.shutdown)
    w.show()
    sys.exit(app.exec())


main()

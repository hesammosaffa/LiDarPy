import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QGridLayout, QLabel, QSpinBox, QPushButton, QSizePolicy)
from lidar_view import LidarView
from widgets import ToggleSwitch, GaugePanel


def row(text, w):
    h = QHBoxLayout()
    h.addWidget(QLabel(text)); h.addStretch(1); h.addWidget(w)
    return h


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lidar Tracker")
        self.resize(1100, 700)
        root = QWidget(); self.setCentralWidget(root)
        lay = QHBoxLayout(root)
        self.view = LidarView()
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self.view, 1)

        side = QWidget(); side.setMinimumWidth(280); side.setMaximumWidth(340)
        sl = QVBoxLayout(side); lay.addWidget(side)
        self.swSearch, self.swStatic, self.swFire = ToggleSwitch(), ToggleSwitch(), ToggleSwitch()
        sl.addLayout(row("Search (on = probe off)", self.swSearch))
        sl.addLayout(row("Hide Static", self.swStatic))
        sl.addLayout(row("Fire", self.swFire))
        self.rangeSpin = QSpinBox()
        self.rangeSpin.setRange(10, 500); self.rangeSpin.setValue(100); self.rangeSpin.setSuffix(" m")
        sl.addLayout(row("Range", self.rangeSpin))
        btn = QPushButton("FIRE"); btn.setFixedSize(80, 80)
        btn.setStyleSheet("QPushButton { background-color:#3A3A3C; color:white; border:2px solid #5A5A5C;"
                          " border-radius:40px; font-weight:bold; }"
                          "QPushButton:pressed { background-color:#FF3B30; border-color:#FF3B30; }")
        sl.addWidget(btn)
        grid = QGridLayout()
        self.gVx, self.gVy = GaugePanel("vx"), GaugePanel("vy")
        self.gVz, self.gV = GaugePanel("vz"), GaugePanel("v", lo=0, hi=20)
        for g, (r, c) in ((self.gVx, (0, 0)), (self.gVy, (0, 1)), (self.gVz, (1, 0)), (self.gV, (1, 1))):
            grid.addWidget(g, r, c)
        sl.addLayout(grid)

        self.swSearch.toggled.connect(lambda on: self.view.set_probe_enabled(not on))
        self.view.set_probe_enabled(not self.swSearch.isChecked())
        self.swStatic.toggled.connect(self.view.set_hide_static)
        self.view.set_max_range(self.rangeSpin.value())
        self.rangeSpin.valueChanged.connect(lambda m: self.view.set_max_range(m))
        self.view.probeChanged.connect(self._probe)
        self.swFire.toggled.connect(lambda on: None)   # TODO: send fire state over UDP

    def _probe(self, locked, x, y, z, vx, vy, vz, v):
        self.gVx.set_value(vx); self.gVy.set_value(vy)
        self.gVz.set_value(vz); self.gV.set_value(v)

    def closeEvent(self, e):
        self.view.shutdown(); e.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow(); w.show()
    sys.exit(app.exec())

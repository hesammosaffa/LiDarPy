"""LidarView - the Qt widget. Heavy work lives in app/lidar/*; this file only connects the parts."""
import threading

import numpy as np
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget

from .lidar.config import RANGE_IMAGE, BEV, BG_BGR, AIM_REF_W, AIM_REF_H
from .lidar.source import CloudSource
from .lidar.static_filter import StaticFilter
from .lidar.renderer import DepthRenderer
from .lidar.tracker import TargetTracker
from .lidar import projection, overlay


class LidarView(QWidget):
    # locked, x, y, z, vx, vy, vz, speed
    probeChanged = Signal(bool, float, float, float, float, float, float, float)
    _frameReady = Signal()
    _unlocked = Signal()

    def __init__(self, parent=None, msop=6699, difop=7788):
        super().__init__(parent)
        self.setMinimumSize(320, 240)
        self.setMouseTracking(True)

        # display settings
        self._mode, self._rmax, self._hide = RANGE_IMAGE, 100.0, False
        self._w, self._h = 320, 240

        # mouse / probe state
        self._probe, self._hover, self._hover_ok = False, QPointF(), False
        self._aim = None              # (dpx, dpy) from CCS; None = unknown

        # parts
        self._tracker = TargetTracker()
        self._static = StaticFilter()
        self._renderer = DepthRenderer()
        self._source = CloudSource(msop, difop)
        self.init_ok = self._source.ok

        # latest cloud (shared between worker and GUI thread)
        self._cur = np.zeros((0, 3), np.float32)
        self._cur_lock = threading.Lock()

        # latest picture
        self._frame = None            # QImage
        self._buf = None              # numpy buffer behind it

        self._wake = threading.Event()
        self._stop = False
        self._frameReady.connect(self._on_frame)
        self._unlocked.connect(self._after_unlock)
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

    # ------------------------------------------------------------ public API
    def set_mode(self, m):
        self._mode = m
        self._wake.set()

    def set_max_range(self, r):
        self._rmax = float(r)
        self._renderer.reset_lut()
        self._wake.set()

    def set_hide_static(self, on):
        self._hide = bool(on)
        self._wake.set()

    def set_probe_enabled(self, on):
        self._probe = on
        self._hover_ok = False
        if not on:
            self._release_lock()
        self.setCursor(Qt.BlankCursor if on else Qt.ArrowCursor)
        self.update()

    def set_aim(self, dpx, dpy, dthx=0.0, dthy=0.0):
        """Red + position from CCS (simulator) as pixel offsets from centre (reference 1200x520)."""
        self._aim = (dpx, dpy)
        self.update()

    def frame_size(self):
        """(w, h) of the rendered frame: the QImage once it exists, else the widget size."""
        f = self._frame
        return (f.width(), f.height()) if f is not None else (self._w, self._h)

    def pixel_to_angle(self, px, py, *args, **kw):
        """Pixel in the current frame -> (dthx, dthy) deg from centre. +x right, +y up."""
        w, h = self.frame_size()
        return projection.pixel_to_angle(px, py, w, h, *args, **kw)

    def point_to_pixel(self, x, y, z=0.0):
        """Point (x forward, y left) -> (px, py) in the current frame. z is accepted but not used."""
        w, h = self.frame_size()
        return projection.point_to_pixel(x, y, w, h)

    def shutdown(self):
        self._stop = True
        self._wake.set()
        self._source.stop()
        self._worker.join(1.0)

    def closeEvent(self, e):
        self.shutdown()
        e.accept()

    # -------------------------------------------------------------- worker
    def _loop(self):
        seen = 0
        have_cloud = False
        raw = np.zeros((0, 3), np.float32)
        while not self._stop:
            new = False
            if self._source.available:
                seq = self._source.wait(seen, 30)
                if seq != seen:
                    seen, raw = self._source.take()
                    new, have_cloud = True, True
            else:
                self._wake.wait(0.03)
            if self._stop:
                break
            changed = self._wake.is_set()
            self._wake.clear()
            if not (new or changed or self._frame is None):
                continue
            if new:
                self._static.update(raw)
            if not have_cloud and self._frame is not None and not changed:
                continue
            pts = self._static.apply(raw, self._hide) if have_cloud else raw
            if new:
                with self._cur_lock:
                    self._cur = pts
            self._buf, self._frame = self._renderer.render(
                pts, self._w, self._h, self._mode, self._rmax, self.init_ok)
            self._frameReady.emit()

    # ------------------------------------------------------------- GUI side
    def resizeEvent(self, e):
        self._w, self._h = max(1, self.width()), max(1, self.height())
        self._wake.set()

    def _on_frame(self):
        self._track_lock()
        self.update()

    def paintEvent(self, ev):
        g = QPainter(self)
        if self._frame is not None and self._frame.size() == self.size():
            g.drawImage(ev.rect().topLeft(), self._frame, ev.rect())
        else:
            g.fillRect(self.rect(), QColor(*BG_BGR[::-1]))
        g.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        # screen centre = (dpx, dpy) = (0, 0)
        overlay.draw_plus(g, QPointF(w / 2.0, h / 2.0), QColor(235, 50, 45), 5)
        if self._probe:
            if self._tracker.locked:
                overlay.draw_lock(g, self._tracker.pos, w, h, self._mode)
            if self._aim is not None:
                ax = w / 2.0 + self._aim[0] / AIM_REF_W * w
                ay = h / 2.0 - self._aim[1] / AIM_REF_H * h
                overlay.draw_plus(g, QPointF(ax, ay), QColor(235, 50, 45), 8)
            if self._hover_ok:
                overlay.draw_plus(g, self._hover, QColor(255, 255, 255), 10)

    # ---------------------------------------------------------------- mouse
    def mouseMoveEvent(self, e):
        if self._probe and self._hover_ok:
            self.update(overlay.plus_rect(self._hover))
        self._hover, self._hover_ok = e.position(), True
        if self._probe:
            self.update(overlay.plus_rect(self._hover))

    def leaveEvent(self, e):
        if self._hover_ok:
            self.update(overlay.plus_rect(self._hover))
        self._hover_ok = False

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            if self._tracker.locked:
                threading.Thread(target=self._unlock_worker, daemon=True).start()
        elif e.button() == Qt.LeftButton and self._probe:
            self._lock_at(e.position())

    def _unlock_worker(self):
        # runs off the GUI thread: only state changes; UI work goes back via signal
        self._tracker.release()
        self._unlocked.emit()

    def _after_unlock(self):
        self._publish()
        self.update()

    # -------------------------------------------------------------- tracking
    def _cloud(self):
        with self._cur_lock:
            return self._cur

    def _lock_at(self, click):
        if self._tracker.lock_at(self._cloud(), click.x(), click.y(),
                                 self.width(), self.height(), self._mode):
            self._publish()
            self.update()

    def _release_lock(self):
        if self._tracker.release():
            self._publish()

    def _track_lock(self):
        if self._tracker.update(self._cloud()):
            self._publish()

    def _publish(self):
        t = self._tracker
        if not t.locked:
            self.probeChanged.emit(False, 0, 0, 0, 0, 0, 0, 0)
            return
        speed = float(np.linalg.norm(t.vel))
        self.probeChanged.emit(True, *map(float, t.pos), *map(float, t.vel), speed)

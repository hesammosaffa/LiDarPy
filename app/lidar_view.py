"""LidarView - port of lidarwidget.h. Driver contact is rs_bridge (C++); everything else is here."""
import math
import threading
import time

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QImage, QFontMetrics
from PySide6.QtWidgets import QWidget

try:
    import rs_bridge
except ImportError:          # lets the UI start without the driver
    rs_bridge = None

RANGE_IMAGE, BEV = 0, 1
H_FOV, V_FOV, BEV_SCALE = math.radians(60.0), math.radians(25.0), 8.0
VOXEL, STATIC_FRAMES, OFFSET = 0.5, 20, 1 << 20
BG_BGR = (24, 20, 20)

# Colour bands as fractions of rMax: (t0, t1, colour at t0, colour at t1). RGB. EDIT HERE.
BANDS = [
    (0.0, 0.1, (150, 200, 255), (0, 50, 200)),     # light -> dark blue
    (0.1, 0.5, (255, 180, 0), (255, 90, 0)),       # orange
    (0.5, 0.9, (200, 120, 255), (80, 0, 120)),     # light -> dark purple
    (0.9, 1.0, (255, 60, 60), (140, 0, 0)),        # red
]


def depth_color(t):
    t = min(max(t, 0.0), 1.0)
    for t0, t1, a, b in BANDS:
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            return tuple(int(a[i] + (b[i] - a[i]) * u + 0.5) for i in range(3))
    return BANDS[-1][3]


def voxel_keys(p):
    i = (np.floor(p / VOXEL).astype(np.int64) + OFFSET) & 0x1FFFFF
    return (i[:, 0] << 42) | (i[:, 1] << 21) | i[:, 2]


class LidarView(QWidget):
    probeChanged = Signal(bool, float, float, float, float, float, float, float)
    _frameReady = Signal()

    def __init__(self, parent=None, msop=6699, difop=7788):
        super().__init__(parent)
        self.setMinimumSize(320, 240)
        self.setMouseTracking(True)
        self._mode, self._rmax, self._hide = RANGE_IMAGE, 100.0, False
        self._w, self._h = 320, 240
        self._probe, self._hover, self._hover_ok = False, QPointF(), False
        self._locked, self._lock = False, np.zeros(3)
        self._v = np.zeros(3)
        self._misses, self._last_t = 0, 0.0
        self._cur = np.zeros((0, 3), np.float32)
        self._cur_lock = threading.Lock()
        self._hist_k = np.zeros(0, np.int64)
        self._hist_c = np.zeros(0, np.int64)
        self._frame = None            # QImage
        self._buf = None              # numpy buffer behind it
        self._lut = None
        self._wake = threading.Event()
        self._stop = False
        self._src = rs_bridge.LidarSource(msop, difop) if rs_bridge else None
        self.init_ok = bool(self._src and self._src.ok)
        self._frameReady.connect(self._on_frame)
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()

    # ------------------------------------------------------------ public API
    def set_mode(self, m):
        self._mode = m; self._wake.set()

    def set_max_range(self, r):
        self._rmax = float(r); self._lut = None; self._wake.set()

    def set_hide_static(self, on):
        self._hide = bool(on); self._wake.set()

    def set_probe_enabled(self, on):
        self._probe = on
        self._hover_ok = False
        if not on:
            self._release_lock()
        self.setCursor(Qt.BlankCursor if on else Qt.ArrowCursor)
        self.update()

    def shutdown(self):
        self._stop = True
        self._wake.set()
        if self._src:
            self._src.stop()
        self._worker.join(1.0)

    closeEvent = lambda self, e: (self.shutdown(), e.accept())

    # -------------------------------------------------------------- worker
    def _loop(self):
        seen = 0
        have_cloud = False
        raw = np.zeros((0, 3), np.float32)
        while not self._stop:
            new = False
            if self._src:
                seq = self._src.wait(seen, 30)
                if seq != seen:
                    seen, raw = self._src.take()
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
                self._update_static(raw)
            if not have_cloud and self._frame is not None and not changed:
                continue
            pts = self._filtered(raw) if have_cloud else raw
            if new:
                with self._cur_lock:
                    self._cur = pts
            self._render(pts, self._w, self._h)
            self._frameReady.emit()

    def _update_static(self, raw):
        keys = np.unique(voxel_keys(raw)) if len(raw) else np.zeros(0, np.int64)
        old = np.zeros(len(keys), np.int64)
        if len(self._hist_k) and len(keys):
            idx = np.searchsorted(self._hist_k, keys)
            idx[idx >= len(self._hist_k)] = 0
            hit = self._hist_k[idx] == keys
            old[hit] = self._hist_c[idx[hit]]
        self._hist_k, self._hist_c = keys, old + 1

    def _filtered(self, raw):
        if not self._hide or not len(raw):
            return raw
        keys = voxel_keys(raw)
        idx = np.searchsorted(self._hist_k, keys)
        idx[idx >= len(self._hist_k)] = 0
        return raw[self._hist_c[idx] < STATIC_FRAMES]

    # ---------------------------------------------------------- projection
    def _project(self, p, w, h):
        """-> (x, y, valid) float arrays for Nx3 points."""
        if self._mode == RANGE_IMAGE:
            ok0 = p[:, 0] > 0
            x = w / 2.0 - np.arctan2(p[:, 1], p[:, 0]) / H_FOV * w
            y = h / 2.0 - np.arctan2(p[:, 2], p[:, 0]) / V_FOV * h
        else:
            ok0 = np.ones(len(p), bool)
            x = w / 2.0 - p[:, 1] * BEV_SCALE
            y = h - 40.0 - p[:, 0] * BEV_SCALE
        return x, y, ok0 & (x >= 0) & (y >= 0) & (x < w) & (y < h)

    def _render(self, pts, w, h):
        rmax = self._rmax
        depth = np.full((h, w), 1e9, np.float32)
        if len(pts):
            x, y, ok = self._project(pts, w, h)
            p = pts[ok]
            px, py = x[ok].astype(np.int32), y[ok].astype(np.int32)
            r = np.sqrt((p * p).sum(1))
            size = np.where(r > 14, 1, np.where(r > 7, 2, np.where(r > 4.7, 3, 4)))
            for sz in (1, 2, 3, 4):
                m = size == sz
                if not m.any():
                    continue
                order = np.argsort(-r[m])          # far first, near written last -> nearest wins
                d = np.full((h, w), 1e9, np.float32)
                d[py[m][order], px[m][order]] = r[m][order]
                if sz > 1:                          # dot covers px..px+sz-1
                    d = cv2.erode(d, np.ones((sz, sz), np.uint8), anchor=(sz - 1, sz - 1),
                                  borderType=cv2.BORDER_CONSTANT, borderValue=1e9)
                np.minimum(depth, d, out=depth)
        if self._lut is None:
            self._lut = np.array([depth_color(i / 255.0) for i in range(256)], np.uint8)
        idx = np.clip(depth * (255.0 / rmax) + 0.5, 0, 255).astype(np.uint8)
        rgb = self._lut[idx]
        rgb[depth >= 1e8] = BG_BGR[::-1]
        buf = np.ascontiguousarray(np.dstack([rgb, np.full((h, w), 255, np.uint8)]))
        img = QImage(buf.data, w, h, w * 4, QImage.Format_RGBA8888)
        self._buf, self._frame = buf, img
        p = QPainter(img)
        self._draw_legend(p, h)
        p.end()

    def _draw_legend(self, g, h):
        rmax = self._rmax
        for i in range(160):
            g.setPen(QColor(*depth_color(i / 159.0)))
            g.drawLine(30 + i, h - 150, 30 + i, h - 142)
        g.setPen(QColor(200, 200, 200))
        for f, dx in ((0.0, 0), (0.1, 16), (0.5, 80), (0.9, 144)):
            g.drawText(30 + dx, h - 156, f"{rmax * f:.0f}")
        g.drawText(30 + 160 + 4, h - 142, f"{rmax:.0f} m")
        g.setPen(QColor(180, 180, 180))
        g.drawText(30, h - 125, "RANGE IMAGE (right click = BEV)" if self._mode == RANGE_IMAGE
                   else "BEV (right click = range image)")
        if not self.init_ok:
            g.setPen(Qt.red)
            g.drawText(30, 30, "LiDAR driver init failed")

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
        if self._probe:
            if self._locked:
                self._draw_lock(g)
            if self._hover_ok:
                self._draw_plus(g, self._hover, QColor(255, 255, 255), 10)

    @staticmethod
    def _plus_rect(c):
        return QRect(int(c.x()) - 14, int(c.y()) - 14, 28, 28)

    def mouseMoveEvent(self, e):
        if self._probe and self._hover_ok:
            self.update(self._plus_rect(self._hover))
        self._hover, self._hover_ok = e.position(), True
        if self._probe:
            self.update(self._plus_rect(self._hover))

    def leaveEvent(self, e):
        if self._hover_ok:
            self.update(self._plus_rect(self._hover))
        self._hover_ok = False

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.set_mode(BEV if self._mode == RANGE_IMAGE else RANGE_IMAGE)
        elif e.button() == Qt.LeftButton and self._probe:
            self._lock_at(e.position())

    @staticmethod
    def _draw_plus(g, c, col, arm):
        g.setPen(QPen(col, 2))
        g.drawLine(QPointF(c.x() - arm, c.y()), QPointF(c.x() + arm, c.y()))
        g.drawLine(QPointF(c.x(), c.y() - arm), QPointF(c.x(), c.y() + arm))

    def _draw_lock(self, g):
        x, y, ok = self._project(self._lock[None, :].astype(np.float32), self.width(), self.height())
        if not ok[0]:
            return
        s = QPointF(float(x[0]), float(y[0]))
        g.setPen(QPen(QColor(60, 220, 90), 2))
        g.setBrush(Qt.NoBrush)
        g.drawRect(QRectF(s.x() - 14, s.y() - 14, 28, 28))
        self._draw_plus(g, s, QColor(235, 50, 45), 8)
        txt = f"X {self._lock[0]:.2f}  Y {self._lock[1]:.2f}  Z {self._lock[2]:.2f} m"
        fm = QFontMetrics(g.font())
        tw, th = fm.horizontalAdvance(txt) + 10, fm.height() + 4
        tx = s.x() + 20
        if tx + tw > self.width():
            tx = s.x() - 20 - tw
        box = QRectF(tx, s.y() - th / 2.0, tw, th)
        g.setPen(Qt.NoPen)
        g.setBrush(QColor(0, 0, 0, 170))
        g.drawRoundedRect(box, 3, 3)
        g.setPen(QColor(255, 255, 255))
        g.drawText(box, Qt.AlignCenter, txt)

    # -------------------------------------------------------------- tracking
    def _cloud(self):
        with self._cur_lock:
            return self._cur

    def _lock_at(self, click):
        cur = self._cloud()
        if not len(cur):
            return
        x, y, ok = self._project(cur, self.width(), self.height())
        d2 = (x - click.x()) ** 2 + (y - click.y()) ** 2
        d2[~ok] = np.inf
        i = int(np.argmin(d2))
        if not d2[i] < 400.0:
            return
        self._lock = cur[i].astype(np.float64)
        self._v[:] = 0
        self._misses, self._locked = 0, True
        self._last_t = time.monotonic()
        self._publish()
        self.update()

    def _release_lock(self):
        was = self._locked
        self._locked = False
        self._v[:] = 0
        if was:
            self._publish()

    def _track_lock(self):
        if not self._locked:
            return
        cur = self._cloud()
        d2 = ((cur - self._lock) ** 2).sum(1) if len(cur) else np.zeros(0)
        i = int(np.argmin(d2)) if len(d2) else -1
        if i < 0 or not d2[i] < 0.25:
            self._misses += 1
            if self._misses >= 5:
                self._release_lock()
            return
        self._misses = 0
        near = cur[((cur - cur[i]) ** 2).sum(1) < 0.09]
        now = near.astype(np.float64).mean(0)
        t = time.monotonic()
        dt, self._last_t = t - self._last_t, t
        if dt > 0.01:
            d = now - self._lock
            still = math.sqrt(float((d * d).sum())) < 0.10
            self._v += 0.4 * ((0.0 if still else 1.0) * d / dt - self._v) if not still else 0.4 * (0 - self._v)
        self._lock = now
        self._publish()

    def _publish(self):
        if not self._locked:
            self.probeChanged.emit(False, 0, 0, 0, 0, 0, 0, 0)
            return
        v = float(np.linalg.norm(self._v))
        self.probeChanged.emit(True, *map(float, self._lock), *map(float, self._v), v)

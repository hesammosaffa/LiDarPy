"""ToggleSwitch, GaugeDial, GaugePanel - ported 1:1 from toggleswitch.h / gaugewidget.h."""
import math
from PySide6.QtCore import Qt, QPointF, QRectF, QSize, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QPolygonF
from PySide6.QtWidgets import QAbstractButton, QWidget, QLabel, QVBoxLayout, QSizePolicy


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._offset = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(51, 31)
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, on):
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(1.0 if on else 0.0)
        self._anim.start()

    def getOffset(self):
        return self._offset

    def setOffset(self, v):
        self._offset = v
        self.update()

    offset = Property(float, getOffset, setOffset)

    def sizeHint(self):
        return QSize(51, 31)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        o, n, k = (58, 58, 60), (52, 199, 89), self._offset
        p.setBrush(QColor(*[int(o[i] + (n[i] - o[i]) * k) for i in range(3)]))
        r = self.height() / 2.0
        p.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), r, r)
        pad = 2.0
        d = self.height() - 2 * pad
        x = pad + k * (self.width() - self.height())
        p.setBrush(Qt.white)
        p.drawEllipse(QRectF(x, pad, d, d))


class GaugeDial(QWidget):
    START, SWEEP, TICKS = -135.0, 270.0, 8

    def __init__(self, title, unit, lo, hi, parent=None):
        super().__init__(parent)
        self.title, self.unit, self.lo, self.hi, self.value = title, unit, lo, hi, lo
        self.START, self.SWEEP = GaugeDial.START, GaugeDial.SWEEP  # per-instance arc
        self.setMinimumSize(90, 90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_range(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.value = min(max(self.value, lo), hi)
        self.update()

    def set_arc(self, start, sweep):
        """Arc in degrees, clockwise from 12 o'clock. Value lo maps to start."""
        self.START, self.SWEEP = float(start), float(sweep)
        self.update()

    def set_value(self, v):
        v = min(max(v, self.lo), self.hi)
        if v != self.value:
            self.value = v
            self.update()

    def _angle(self, v):
        return self.START + self.SWEEP * (v - self.lo) / (self.hi - self.lo)

    def paintEvent(self, _):
        g = QPainter(self)
        g.setRenderHint(QPainter.Antialiasing)
        side = min(self.width(), self.height())
        g.translate(self.width() / 2.0, self.height() / 2.0)
        g.scale(side / 200.0, side / 200.0)
        # face
        g.setPen(QPen(QColor(95, 95, 100), 4))
        g.setBrush(QColor(28, 28, 32))
        g.drawEllipse(QPointF(0, 0), 96, 96)
        # ticks
        f = g.font(); f.setPixelSize(12); g.setFont(f)
        for i in range(self.TICKS + 1):
            a = self.START + self.SWEEP * i / self.TICKS
            g.save()
            g.rotate(a)
            g.setPen(QPen(QColor(210, 210, 215), 3 if i % 2 == 0 else 1.5))
            g.drawLine(QPointF(0, -90), QPointF(0, -78 if i % 2 == 0 else -83))
            g.restore()
            if i % 2 == 0:
                rad = math.radians(a)
                cx, cy = 64 * math.sin(rad), -64 * math.cos(rad)
                v = self.lo + (self.hi - self.lo) * i / self.TICKS
                g.setPen(QColor(200, 200, 205))
                g.drawText(QRectF(cx - 18, cy - 8, 36, 16), Qt.AlignCenter, f"{v:.0f}")
        # texts
        f.setPixelSize(20); f.setBold(True); g.setFont(f)
        g.setPen(QColor(255, 214, 92))
        g.drawText(QRectF(-40, 22, 80, 24), Qt.AlignCenter, self.title)
        f.setPixelSize(12); f.setBold(False); g.setFont(f)
        g.setPen(QColor(160, 160, 165))
        g.drawText(QRectF(-40, 46, 80, 16), Qt.AlignCenter, self.unit)
        # needle
        g.save()
        g.rotate(self._angle(self.value))
        g.setPen(Qt.NoPen)
        g.setBrush(QColor(230, 70, 55))
        g.drawPolygon(QPolygonF([QPointF(-4, 0), QPointF(0, -74), QPointF(4, 0)]))
        g.restore()
        g.setBrush(QColor(60, 60, 65))
        g.setPen(QPen(QColor(150, 150, 155), 2))
        g.drawEllipse(QPointF(0, 0), 7, 7)


class GaugePanel(QWidget):
    def __init__(self, title="v", unit="°", lo=-180.0, hi=180.0, parent=None):
        super().__init__(parent)
        self.unit = unit
        self.dial = GaugeDial(title, unit, lo, hi, self)
        self.box = QLabel(self)
        self.box.setAlignment(Qt.AlignCenter)
        self.box.setMinimumHeight(24)
        self.box.setStyleSheet("QLabel { background:#1C1C1E; color:#F2F2F7;"
                               " border:1px solid #5A5A5C; border-radius:4px; font-weight:bold; }")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        lay.addWidget(self.dial, 1)
        lay.addWidget(self.box)
        self.set_value(0.0)

    def _get_title(self): return self.dial.title
    def _set_title(self, t): self.dial.title = t; self.dial.update()
    def _get_min(self): return self.dial.lo
    def _set_min(self, v): self.dial.set_range(float(v), self.dial.hi)
    def _get_max(self): return self.dial.hi
    def _set_max(self, v): self.dial.set_range(self.dial.lo, float(v))
    title = Property(str, _get_title, _set_title)
    minimum = Property(float, _get_min, _set_min)
    maximum = Property(float, _get_max, _set_max)

    def set_arc(self, start, sweep):
        self.dial.set_arc(start, sweep)

    def set_value(self, v):
        self.dial.set_value(v)
        self.box.setText(f"{v:.2f} {self.unit}")

"""Small drawing helpers for the cross, lock box and angle label."""
import math

import numpy as np
from PySide6.QtCore import Qt, QPointF, QRectF, QRect
from PySide6.QtGui import QColor, QPen, QFontMetrics

from .projection import project


def plus_rect(c):
    """Area to repaint around a cross."""
    return QRect(int(c.x()) - 14, int(c.y()) - 14, 28, 28)


def draw_plus(g, c, col, arm):
    g.setPen(QPen(col, 2))
    g.drawLine(QPointF(c.x() - arm, c.y()), QPointF(c.x() + arm, c.y()))
    g.drawLine(QPointF(c.x(), c.y() - arm), QPointF(c.x(), c.y() + arm))


def draw_lock(g, lock, w, h, mode):
    """Green box on the locked point with its angle offsets."""
    x, y, ok = project(lock[None, :].astype(np.float32), w, h, mode)
    if not ok[0]:
        return
    s = QPointF(float(x[0]), float(y[0]))
    g.setPen(QPen(QColor(60, 220, 90), 2))
    g.setBrush(Qt.NoBrush)
    g.drawRect(QRectF(s.x() - 14, s.y() - 14, 28, 28))
    lx, ly, lz = (float(v) for v in lock[:3])
    dthx = -math.degrees(math.atan2(ly, lx))   # same sign as xyz_to_offsets (left = negative px)
    dthy = math.degrees(math.atan2(lz, lx))
    txt = f"dthx {dthx:+.3f}°  dthy {dthy:+.3f}°"
    fm = QFontMetrics(g.font())
    tw, th = fm.horizontalAdvance(txt) + 10, fm.height() + 4
    tx = s.x() + 20
    if tx + tw > w:
        tx = s.x() - 20 - tw
    box = QRectF(tx, s.y() - th / 2.0, tw, th)
    g.setPen(Qt.NoPen)
    g.setBrush(QColor(0, 0, 0, 170))
    g.drawRoundedRect(box, 3, 3)
    g.setPen(QColor(255, 255, 255))
    g.drawText(box, Qt.AlignCenter, txt)

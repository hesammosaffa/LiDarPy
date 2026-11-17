"""Turns a point cloud into a QImage (depth picture + legend)."""
import cv2
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QImage

from .colormap import depth_color
from .config import RANGE_IMAGE, BG_BGR
from .projection import project


class DepthRenderer:
    def __init__(self):
        self._lut = None          # depth index -> colour table

    def reset_lut(self):
        """Call when max range changes."""
        self._lut = None

    def render(self, pts, w, h, mode, rmax, init_ok):
        """-> (numpy buffer, QImage). Keep the buffer alive as long as the image is used."""
        depth = np.full((h, w), 1e9, np.float32)
        if len(pts):
            x, y, ok = project(pts, w, h, mode)
            p = pts[ok]
            px, py = x[ok].astype(np.int32), y[ok].astype(np.int32)
            r = np.sqrt((p * p).sum(1))
            # near points are drawn bigger
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
        g = QPainter(img)
        self._draw_legend(g, h, mode, rmax, init_ok)
        g.end()
        return buf, img

    @staticmethod
    def _draw_legend(g, h, mode, rmax, init_ok):
        for i in range(160):
            g.setPen(QColor(*depth_color(i / 159.0)))
            g.drawLine(30 + i, h - 150, 30 + i, h - 142)
        g.setPen(QColor(200, 200, 200))
        for f, dx in ((0.0, 0), (0.1, 16), (0.5, 80), (0.9, 144)):
            g.drawText(30 + dx, h - 156, f"{rmax * f:.0f}")
        g.drawText(30 + 160 + 4, h - 142, f"{rmax:.0f} m")
        g.setPen(QColor(180, 180, 180))
        g.drawText(30, h - 125, "RANGE IMAGE (right click = BEV)" if mode == RANGE_IMAGE
                   else "BEV (right click = range image)")
        if not init_ok:
            g.setPen(Qt.red)
            g.drawText(30, 30, "LiDAR driver init failed")

"""3D point <-> pixel. The only place that knows the camera mapping."""
import math

import numpy as np

from .config import RANGE_IMAGE, H_FOV, V_FOV, BEV_SCALE


def project(p, w, h, mode):
    """Nx3 points -> (x, y, valid) float arrays."""
    if mode == RANGE_IMAGE:
        ok0 = p[:, 0] > 0
        x = w / 2.0 - np.arctan2(p[:, 1], p[:, 0]) / H_FOV * w
        y = h / 2.0 - np.arctan2(p[:, 2], p[:, 0]) / V_FOV * h
    else:
        ok0 = np.ones(len(p), bool)
        x = w / 2.0 - p[:, 1] * BEV_SCALE
        y = h - 40.0 - p[:, 0] * BEV_SCALE
    return x, y, ok0 & (x >= 0) & (y >= 0) & (x < w) & (y < h)


def pixel_to_angle(px, py, w, h, h_fov=math.degrees(H_FOV), v_fov=math.degrees(V_FOV)):
    """Pixel -> (dthx, dthy) in degrees from centre. +x right, +y up."""
    return (px - w / 2.0) / w * h_fov, (h / 2.0 - py) / h * v_fov


def point_to_pixel(x, y, w, h, z=0.0):
    """Point (x forward, y left) -> (px, py). Same mapping as the range image.
    z is not used, so py is always the centre row."""
    return w / 2.0 - math.atan2(y, x) / H_FOV * w, h / 2.0

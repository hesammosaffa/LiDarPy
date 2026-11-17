"""Hides points that stay in the same voxel for many frames."""
import numpy as np

from .config import VOXEL, STATIC_FRAMES, OFFSET


def voxel_keys(p):
    """Nx3 points -> one int64 key per voxel."""
    i = (np.floor(p / VOXEL).astype(np.int64) + OFFSET) & 0x1FFFFF
    return (i[:, 0] << 42) | (i[:, 1] << 21) | i[:, 2]


class StaticFilter:
    def __init__(self):
        self._keys = np.zeros(0, np.int64)     # voxels seen in the last frame
        self._count = np.zeros(0, np.int64)    # how many frames in a row

    def update(self, raw):
        """Call once per new frame."""
        keys = np.unique(voxel_keys(raw)) if len(raw) else np.zeros(0, np.int64)
        old = np.zeros(len(keys), np.int64)
        if len(self._keys) and len(keys):
            idx = np.searchsorted(self._keys, keys)
            idx[idx >= len(self._keys)] = 0
            hit = self._keys[idx] == keys
            old[hit] = self._count[idx[hit]]
        self._keys, self._count = keys, old + 1

    def apply(self, raw, hide):
        """Return raw, or raw without static points when hide is True."""
        if not hide or not len(raw):
            return raw
        keys = voxel_keys(raw)
        idx = np.searchsorted(self._keys, keys)
        idx[idx >= len(self._keys)] = 0
        return raw[self._count[idx] < STATIC_FRAMES]

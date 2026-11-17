"""Target lock and tracking. No Qt here, so it is easy to test."""
import math
import time

import numpy as np

from .projection import project


class TargetTracker:
    MAX_MISSES = 5          # frames without a match before the lock is dropped

    def __init__(self):
        self.locked = False
        self.pos = np.zeros(3)      # locked point (x, y, z)
        self.vel = np.zeros(3)      # smoothed velocity
        self._misses = 0
        self._last_t = 0.0

    def lock_at(self, cloud, click_x, click_y, w, h, mode):
        """Lock the cloud point nearest to the click. Returns True if locked."""
        if not len(cloud):
            return False
        x, y, ok = project(cloud, w, h, mode)
        d2 = (x - click_x) ** 2 + (y - click_y) ** 2
        d2[~ok] = np.inf
        i = int(np.argmin(d2))
        if not d2[i] < 400.0:
            return False
        self.pos = cloud[i].astype(np.float64)
        self.vel[:] = 0
        self._misses, self.locked = 0, True
        self._last_t = time.monotonic()
        return True

    def release(self):
        """Drop the lock. Returns True if it was locked."""
        was = self.locked
        self.locked = False
        self.vel[:] = 0
        return was

    def update(self, cloud):
        """Follow the target in a new frame. Returns True if the result should be published."""
        if not self.locked:
            return False
        cur = cloud
        d2 = ((cur - self.pos) ** 2).sum(1) if len(cur) else np.zeros(0)
        i = int(np.argmin(d2)) if len(d2) else -1
        if i < 0 or not d2[i] < 0.25:
            self._misses += 1
            if self._misses >= self.MAX_MISSES:
                return self.release()
            return False
        self._misses = 0
        near = cur[((cur - cur[i]) ** 2).sum(1) < 0.09]
        now = near.astype(np.float64).mean(0)
        t = time.monotonic()
        dt, self._last_t = t - self._last_t, t
        if dt > 0.01:
            d = now - self.pos
            still = math.sqrt(float((d * d).sum())) < 0.10
            self.vel += 0.4 * ((0.0 if still else 1.0) * d / dt - self.vel) if not still else 0.4 * (0 - self.vel)
        self.pos = now
        return True

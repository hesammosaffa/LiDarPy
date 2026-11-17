"""Lidar driver wrapper (rs_bridge is the C++ part)."""
try:
    import rs_bridge
except ImportError:          # lets the UI start without the driver
    rs_bridge = None


class CloudSource:
    def __init__(self, msop, difop):
        self._src = rs_bridge.LidarSource(msop, difop) if rs_bridge else None
        self.ok = bool(self._src and self._src.ok)

    @property
    def available(self):
        return self._src is not None

    def wait(self, seen, timeout_ms):
        return self._src.wait(seen, timeout_ms)

    def take(self):
        """-> (sequence number, Nx3 points)"""
        return self._src.take()

    def stop(self):
        if self._src:
            self._src.stop()

"""PID for pan/tilt. Setpoint is always 0; input is the offset (delta) in degrees,
output is the velocity command (vp, vt).

    pid = PanTiltPID()
    vp, vt = pid.update(delta_p, delta_t)   # call once per new measurement
"""
import time


class PID:
    def __init__(self, kp=5, ki=0.1, kd=0.0, out_limit=None, in_limit=None, d_filter=0.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.out_limit = out_limit      # max |output| (None = unlimited)
        self.in_limit = in_limit        # max |input| (delta is clamped to +-in_limit)
        self.d_filter = d_filter        # 0 = no filter, 0..1 low-pass on D term
        self.reset()

    def reset(self):
        self._i = 0.0
        self._prev_err = None
        self._prev_t = None
        self._d = 0.0

    def update(self, delta, now=None):
        """delta: measured offset. Setpoint = 0, so error = 0 - delta."""
        if self.in_limit is not None:
            delta = max(-self.in_limit, min(self.in_limit, delta))
        err = 0.0 - delta
        now = time.monotonic() if now is None else now
        dt = None if self._prev_t is None else now - self._prev_t
        self._prev_t = now

        d = 0.0
        if dt is not None and dt > 1e-6:
            # integral with anti-windup (clamped so I alone can't exceed the output limit)
            self._i += self.ki * err * dt
            if self.out_limit is not None:
                self._i = max(-self.out_limit, min(self.out_limit, self._i))
            raw_d = (err - self._prev_err) / dt
            self._d = self.d_filter * self._d + (1.0 - self.d_filter) * raw_d
            d = self._d
        self._prev_err = err

        out = self.kp * err + self._i + self.kd * d
        if self.out_limit is not None:
            out = max(-self.out_limit, min(self.out_limit, out))
        return out


class PanTiltPID:
    """Two independent PIDs. Pan delta in [-180, 180] deg, tilt delta in [-90, 90] deg."""

    def __init__(self, kp_p=1.0, ki_p=0.0, kd_p=0.0, kp_t=1.0, ki_t=0.0, kd_t=0.0,
                 vp_max=None, vt_max=None, d_filter=0.0):
        self.pan = PID(kp_p, ki_p, kd_p, out_limit=vp_max, in_limit=180.0, d_filter=d_filter)
        self.tilt = PID(kp_t, ki_t, kd_t, out_limit=vt_max, in_limit=90.0, d_filter=d_filter)

    def update(self, delta_p, delta_t, now=None):
        """-> (vp, vt)"""
        return self.pan.update(delta_p, now), self.tilt.update(delta_t, now)

    def reset(self):
        self.pan.reset()
        self.tilt.reset()

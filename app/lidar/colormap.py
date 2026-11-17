"""Depth -> colour."""

# Colour bands as fractions of rMax: (t0, t1, colour at t0, colour at t1). RGB. EDIT HERE.
BANDS = [
    (0.0, 0.1, (150, 200, 255), (0, 50, 200)),     # light -> dark blue
    (0.1, 0.5, (255, 180, 0), (255, 90, 0)),       # orange
    (0.5, 0.9, (200, 120, 255), (80, 0, 120)),     # light -> dark purple
    (0.9, 1.0, (255, 60, 60), (140, 0, 0)),        # red
]


def depth_color(t):
    """t in 0..1 (fraction of max range) -> (r, g, b)."""
    t = min(max(t, 0.0), 1.0)
    for t0, t1, a, b in BANDS:
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            return tuple(int(a[i] + (b[i] - a[i]) * u + 0.5) for i in range(3))
    return BANDS[-1][3]

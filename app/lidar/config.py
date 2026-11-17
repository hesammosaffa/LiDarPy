"""All tunable numbers in one place."""
import math

# View modes
RANGE_IMAGE, BEV = 0, 1

# Field of view used to draw the range image (radians)
H_FOV = math.radians(60.0)
V_FOV = math.radians(25.0)

# Bird-eye view: pixels per metre
BEV_SCALE = 8.0

# Static filter: voxel size (m) and frames before a voxel counts as static
VOXEL = 0.5
STATIC_FRAMES = 20
OFFSET = 1 << 20

# Background colour (B, G, R)
BG_BGR = (24, 20, 20)

# Reference frame size used by set_aim (pixels)
AIM_REF_W, AIM_REF_H = 1200.0, 520.0

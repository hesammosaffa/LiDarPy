"""LCS: controller command sender. Transmission is done by UDPSender (luncherController/UDPSend.py).

Frame for offsets: sensor axis (0,0) deg, +X right, +Y up.
"""
import math

from udp.UDPSend import UDPSender
from pid.PID import PanTiltPID

def xyz_to_offsets(view, x, y):
    """Point (x forward, y left) -> (dthx, dthy) in degrees. w/h are read from the view's
    current frame on every call (view.frame_size()). z is not used, so dthy is 0."""
    px, py = view.point_to_pixel(x, y)
    teta_x,teta_y = view.pixel_to_angle(px, py)
    # print("teta_x,teta_y ==> ",teta_x,teta_y)
    return view.pixel_to_angle(px, py)


class LCS:
    def __init__(self, ip="192.168.109.1", port=5000, my_ip="192.168.109.201", period_s=0.002, log_path=None, console_every_s=1.0, fcs=None, view=None, pan_sign=1.0, tilt_sign=1.0, gain=0.1):
        self._pan_sign, self._tilt_sign, self._gain = pan_sign, tilt_sign, gain
        self._view = view  # LidarView: provides frame_size() / pixel_to_angle()
        self._fcs = fcs  # FcsReceiver: source of Pan_ActPos / Tilt_ActPos
        # log_path / console_every_s are accepted for compatibility but unused:
        # UDPSender has no logging hook.
        self._sender = UDPSender(plc_ip=ip, plc_port=port, my_ip=my_ip, interval=period_s)

    def set_xyz(self, x, y, z=0.0):
        """Call from the main app whenever a new position is available."""
        o = xyz_to_offsets(self._view, float(x), float(y))
        if o is not None:
            d = self._sender.data
            pan, tilt = o
            print("pan raw ==> ",pan)
            if self._fcs is not None:
                act = self._fcs.last
                if act is None:   # no feedback yet: don't send a relative value as absolute
                    return
                
                pid = PanTiltPID(kp_p=1, kp_t=2.0, vp_max=8000, vt_max=8000)
                vp, vt = pid.update(pan, tilt)
                print("vp ==> ",vp)
                pan=-100 if vp>0 else 100
                vp, vt = abs(vp), abs(vt)

              
                print("pan ==> ",pan)
            self._sender.update_position(pan, 0, vp, vt)

    def set_field(self, name, value):
        """Set a packet field by its name in UDPSender.data (e.g. "Control_Mode", "ID1")."""
        if name not in self._sender.data:
            raise KeyError(f"unknown field: {name}")
        self._sender.data[name] = value

    def fire_on(self):
        """Call when the FIRE button is pressed."""
        self._sender.Fire1(True)

    def fire_off(self):
        """Call when the FIRE button is released."""
        self._sender.Fire1(False)

    def start(self):
        self._sender.start()

    def stop(self):
        self._sender.stop()

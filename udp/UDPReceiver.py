"""UDPReceiver: generic UDP packet reader. Binds a port, reads datagrams in a
daemon thread and hands each one to a callback: on_packet(data: bytes, src: (ip, port)).
No decoding here."""
import socket
import threading


class UDPReceiver:
    def __init__(self, bind_ip="", port=5005, on_packet=None, bufsize=256):
        self._addr = (bind_ip, port)
        self._on_packet = on_packet
        self._bufsize = bufsize
        self._stop = threading.Event()
        self._sock = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.count = 0

    def start(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(self._addr)
        self._sock.settimeout(0.3)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._sock:
            self._sock.close()
            self._sock = None

    def _run(self):
        while not self._stop.is_set():
            try:
                data, src = self._sock.recvfrom(self._bufsize)
            except socket.timeout:
                continue
            except OSError:
                break
            self.count += 1
            if self._on_packet:
                try:
                    self._on_packet(data, src)
                except Exception as e:
                    print(f"UDPReceiver callback error: {e}", flush=True)

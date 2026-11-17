"""Listen on UDP and print each x,y,z packet (3 x float32, little-endian)."""
import socket
import struct

IP = "127.0.0.1"
PORT = 9000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))
print(f"Listening on {IP}:{PORT} ... (Ctrl+C to stop)")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        if len(data) != 12:
            print(f"bad packet from {addr}: {len(data)} bytes")
            continue
        x, y, z = struct.unpack("<3f", data)
        print(f"x={x:10.3f}  y={y:10.3f}  z={z:10.3f}")
except KeyboardInterrupt:
    pass
finally:
    sock.close()

import socket
from pyais import decode

# --- Configuration ---
UDP_IP = "127.0.0.1"     # Input from AIS-catcher
UDP_PORT = 10110
TCP_IP = "0.0.0.0"       # OpenCPN will connect here
TCP_PORT = 10111

# --- Setup UDP socket (receive AIS NMEA) ---
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))
print(f"[UDP] Listening for AIS messages on {UDP_IP}:{UDP_PORT}...")

# --- Setup TCP server (send decoded positions to OpenCPN) ---
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((TCP_IP, TCP_PORT))
tcp_sock.listen(1)
print(f"[TCP] Waiting for OpenCPN to connect on {TCP_IP}:{TCP_PORT}...")

conn, addr = tcp_sock.accept()
print(f"[TCP] OpenCPN connected from {addr}")

# --- Main loop ---
while True:
    data, _ = udp_sock.recvfrom(1024)
    message = data.decode(errors="ignore").strip()

    if not message.startswith("!AI"):
        continue

    try:
        msg = decode(message)

        if hasattr(msg, "lat") and hasattr(msg, "lon"):
            lat = msg.lat
            lon = msg.lon
            mmsi = msg.mmsi

            print(f"[DECODED] MMSI:{mmsi}  LAT:{lat:.5f}  LON:{lon:.5f}")

            # Construct a minimal NMEA sentence for OpenCPN
            nmea_line = f"!AIVDM,1,1,,A,{mmsi},{lat:.5f},{lon:.5f}*00\r\n"
            conn.sendall(nmea_line.encode())

    except Exception as e:
        print("[ERROR] Could not decode:", e)

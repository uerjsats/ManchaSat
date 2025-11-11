import socket
from pyais import decode

# --- Configuration ---
UDP_IP = "127.0.0.1"     # AIS-catcher sends here
UDP_PORT = 10110

print(f"[UDP] Listening for AIS messages on {UDP_IP}:{UDP_PORT}...")

# --- Setup UDP socket ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode(errors="ignore").strip()

    if not message.startswith("!AI"):
        continue

    try:
        msg = decode(message)
        # Only some AIS message types include lat/lon (types 1, 2, 3, 18, 19)
        if hasattr(msg, "lat") and hasattr(msg, "lon"):
            mmsi = msg.mmsi
            lat = msg.lat
            lon = msg.lon
            sog = getattr(msg, "sog", None)
            cog = getattr(msg, "cog", None)
            print(f"MMSI:{mmsi}  LAT:{lat:.5f}  LON:{lon:.5f}  SOG:{sog}  COG:{cog}")
        else:
            print("[INFO] Non-position message received.")
    except Exception as e:
        print("[ERROR]", e)

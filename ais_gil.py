import socket
from pyais import decode

# --- Configuration ---
UDP_IP = "127.0.0.1"
UDP_PORT = 10120

TCP_IP = "127.0.0.1"
TCP_PORT2 = 10120

TCP_PORT1 = 10110

# --- Setup UDP socket ---
#udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#udp_sock.bind((UDP_IP, UDP_PORT))
#print(f"[UDP] Listening for AIS messages on {UDP_IP}:{UDP_PORT}...")

# --- Setup TCP socket (connect to RTL-SDR) ---
tcp_sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock1.connect(('localhost', TCP_PORT1))

# --- Setup TCP server (connect to OpenCPN) ---
#tcp_sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#tcp_sock2.bind((TCP_IP, TCP_PORT2))
#tcp_sock2.listen(1)
#print(f"[TCP] Waiting for OpenCPN to connect on {TCP_IP}:{TCP_PORT2}...")

#conn, addr = tcp_sock2.accept()
#print(f"[TCP] OpenCPN connected from {addr}")

# --- Main loop ---
while True:
    #data = tcp_sock1.recvfrom(1024)
    #cp_sock1.send("\xFE")
    #tcp_sock1.sendall(b"Hello, world")
    data = tcp_sock1.recv(512)
    #tcp_sock1.close()
    print(data)

#    message = data.encode(errors="ignore").strip()

#    if not message.startswith("!AI"):
#        continue

 #   try:
        # Extract AIS payload
 #       parts = message.split(",")
 #       if len(parts) < 6:
 #           continue

 #       payload = parts[5]  # AIS encoded payload
 #       msg = decode(payload)

 #       if hasattr(msg, "lat") and hasattr(msg, "lon"):
 #           lat = msg.lat
#            lon = msg.lon
#            mmsi = msg.mmsi

#            print(f"[DECODED] MMSI:{mmsi} LAT:{lat:.5f} LON:{lon:.5f}")

            # Dummy NMEA for OpenCPN
#            out_nmea = f"!AIVDM,1,1,,A,{mmsi},{lat:.5f},{lon:.5f}*00\r\n"
            #conn.sendall(out_nmea.encode())

#    except Exception as e:
#        print("[ERROR] Could not decode:", e)

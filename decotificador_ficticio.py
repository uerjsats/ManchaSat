# ais_simulador_e_receiver.py
import socket
import threading
import time
from pyais import decode

HOST = "127.0.0.1"   
PORT = 10110         


AIS_EXAMPLES = [
    b"!AIVDM,1,1,,A,13aG;P0P01G?tR;E`R2Dwwv028G,0*3F",
    b"!AIVDM,1,1,,A,15N?;P001oG?tR;E`R2Dwwv028G,0*5C",
    b"!AIVDM,1,1,,B,402OiTP001G?tR;E`R2Dwwv028G,0*1D",
    # Mensagem de tipo estática (exemplo sem posição)
    b"!AIVDM,1,1,,A,55NB1r02>t0a;88MD5Jp?w?02@E:,0*1C",
]

def sender_loop(host=HOST, port=PORT, interval=1.0):
    """Envia mensagens AIS de AIS_EXAMPLES para host:port periodicamente."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    i = 0
    try:
        while True:
            msg = AIS_EXAMPLES[i % len(AIS_EXAMPLES)]
            sock.sendto(msg, (host, port))
            # imprime no console do simulador (opcional)
            print(f"[simulador] enviou: {msg.decode(errors='ignore')}")
            i += 1
            time.sleep(interval)
    except Exception as e:
        print(f"[simulador] erro: {e}")
    finally:
        sock.close()

def processar_mensagem(msg_bytes):
    try:
        decoded = decode(msg_bytes)
        mmsi = getattr(decoded, "mmsi", "N/A")
        tipo = getattr(decoded, "type", "N/A")
        lat = getattr(decoded, "y", None)   # latitude (y)
        lon = getattr(decoded, "x", None)   # longitude (x)
        sog = getattr(decoded, "sog", None) # speed over ground
        cog = getattr(decoded, "cog", None) # course over ground

        lat_s = f"{lat:.6f}" if isinstance(lat, float) else lat
        lon_s = f"{lon:.6f}" if isinstance(lon, float) else lon
        sog_s = f"{sog} kn" if sog is not None else "N/A"
        cog_s = f"{cog}°" if cog is not None else "N/A"

        print(f"[receiver] MMSI: {mmsi} | Tipo: {tipo} | Lat: {lat_s} | Lon: {lon_s} | SOG: {sog_s} | COG: {cog_s}")
    except Exception as e:
        print(f"[receiver] Erro ao decodificar: {e}")

def receiver_loop(host="0.0.0.0", port=PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"[receiver] Aguardando dados AIS em {host}:{port} ... (Ctrl+C para encerrar)")
    try:
        while True:
            data, addr = sock.recvfrom(4096)
            processar_mensagem(data)
    except KeyboardInterrupt:
        print("\n[receiver] Interrompido pelo usuário.")
    except Exception as e:
        print(f"[receiver] erro: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    
    sender_thread = threading.Thread(target=sender_loop, args=(HOST, PORT, 1.0), daemon=True)
    sender_thread.start()

    
    receiver_loop("0.0.0.0", PORT)

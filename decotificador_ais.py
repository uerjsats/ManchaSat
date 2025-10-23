from pyais import decode
import socket


def processar_mensagem(msg_bytes):
    try:
        decoded = decode(msg_bytes)
        
        mmsi = getattr(decoded, "mmsi", "N/A")
        tipo = getattr(decoded, "type", "N/A")
        lat = getattr(decoded, "y", "N/A")       # latitude
        lon = getattr(decoded, "x", "N/A")       # longitude
        sog = getattr(decoded, "sog", "N/A")     # speed over ground
        cog = getattr(decoded, "cog", "N/A")     # course over ground

        print(f"MMSI: {mmsi} | Tipo: {tipo} | Lat: {lat} | Lon: {lon} | SOG: {sog} kn | COG: {cog}°")
    except Exception as e:
        print(f"Erro ao decodificar: {e}")


def receber_udp(host='0.0.0.0', port=10110):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Aguardando dados AIS em {host}:{port}...")

    while True:
        data, addr = sock.recvfrom(1024)  
        processar_mensagem(data)


if __name__ == "__main__":
    host = input("Host UDP (default 0.0.0.0): ") or "0.0.0.0"
    port = int(input("Porta UDP (default 10110): ") or 10110)
    receber_udp(host, port)


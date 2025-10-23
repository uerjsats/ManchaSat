
from pyais import decode
import socket


HOST = '0.0.0.0'   
PORT = 10110       

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(f"Aguardando dados AIS em {HOST}:{PORT}...")

while True:
    data, addr = sock.recvfrom(1024)  
    try:
        decoded = decode(data)
        print(decoded)
    except Exception as e:
        print(f"Erro ao decodificar: {e}")

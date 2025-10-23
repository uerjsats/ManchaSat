
from pyais import decode
import time


mensagens_ficticias = [
    b"!AIVDM,1,1,,A,15N?;P001oG?tR;E`R2Dwwv028G,0*5C",
    b"!AIVDM,1,1,,B,402OiTP001G?tR;E`R2Dwwv028G,0*1D",
    b"!AIVDM,1,1,,A,13aG;P0P01G?tR;E`R2Dwwv028G,0*3F",
]

print("Simulando recebimento de dados AIS...")

for msg in mensagens_ficticias:
    try:
        decoded = decode(msg)
        print(decoded)  
    except Exception as e:
        print(f"Erro ao decodificar: {e}")
    time.sleep(1)  

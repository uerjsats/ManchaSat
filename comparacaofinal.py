# ==========================================
#  FUNÇÕES DO GIL (AIS)
# ==========================================
from pyais.stream import TCPConnection
import csv
import cv2
import numpy as np

def receber_dados_ais(host='localhost', port=10110):
    """
    Lê uma única mensagem AIS tipo 21 do GPS e retorna (lat, lon, mmsi, nome)
    """
    msg_type = [21]

    for msg in TCPConnection(host, port=port):
        decoded = msg.decode()

        if decoded.msg_type in msg_type:
            return {
                "mmsi": decoded.mmsi,
                "nome": decoded.name,
                "lat": decoded.lat,
                "lon": decoded.lon
            }

    return None


# ==========================================
#  FUNÇÕES DO ORLANDO (CÂMERA)
# ==========================================
def processar_imagem_camera(caminho_imagem="teste.jpg"):
    """
    Retorna a latitude e longitude calculada a partir do pixel detectado da mancha.
    Aqui você deve colocar a sua lógica real de conversão pixel -> lat/lon.
    Por enquanto, retornarei valores fictícios apenas como exemplo.
    """

    img = cv2.imread(caminho_imagem)
    if img is None:
        print("ERRO: imagem não encontrada!")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = cv2.inRange(gray, 50, 255)
    kernel = np.ones((10, 10), np.uint8)
    clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        print("Nenhuma mancha detectada!")
        return None

    # usar o MAIOR contorno
    cont = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cont)

    # pixel representativo (centro do retângulo)
    px = x + w // 2
    py = y + h // 2

    # >>>>> IMPORTANTE <<<<<
    # Aqui você precisa substituir por sua fórmula real:
    lat_img = -22.94849
    lon_img = -43.17208

    return {
        "pixel_x": px,
        "pixel_y": py,
        "lat": lat_img,
        "lon": lon_img
    }


# ==========================================
#  COMPARAÇÃO ENTRE AIS E CÂMERA
# ==========================================
def comparar(ais, cam, tolerancia_percent=1):
    """
    Compara lat/lon de AIS vs Câmera usando tolerância percentual.
    """

    lat_tol = abs(ais["lat"]) * (tolerancia_percent / 100)
    lon_tol = abs(ais["lon"]) * (tolerancia_percent / 100)

    dif_lat = abs(ais["lat"] - cam["lat"])
    dif_lon = abs(ais["lon"] - cam["lon"])

    print("\n=== DADOS AIS ===")
    print(ais["lat"])
    print(ais["lon"])

    print("\n=== DADOS CÂMERA ===")
    print(cam["lat"])
    print(cam["lon"])
    print(f"Pixel detectado: ({cam['pixel_x']}, {cam['pixel_y']})")

    print("\n=== TOLERÂNCIAS ===")
    print(f"Lat tolerância: ±{lat_tol}")
    print(f"Lon tolerância: ±{lon_tol}")

    print("\n=== DIFERENÇAS ===")
    print(f"Δ latitude  = {dif_lat}")
    print(f"Δ longitude = {dif_lon}")

    if dif_lat <= lat_tol and dif_lon <= lon_tol:
        print("\nMESMA EMBARCAÇÃO ✔")
    else:
        print("\nEMBARCAÇÕES DIFERENTES ✘")


# ==========================================
#  PROGRAMA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    
    print("Lendo dados AIS...")
    ais = receber_dados_ais()

    print("Processando imagem...")
    cam = processar_imagem_camera("teste.jpg")

    if ais and cam:
        comparar(ais, cam, tolerancia_percent=1)
    else:
        print("Erro: não consegui obter AIS ou imagem.")

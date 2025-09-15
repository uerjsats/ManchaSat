import cv2
import numpy as np
from PIL import Image
import matplotlib

# ✅ Forçar o backend TkAgg antes de qualquer pyplot
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from picamzero import Camera
import subprocess
import threading
import ais  # Biblioteca para decodificação NMEA/AIS

# === Inicializar câmera ===
cam = Camera()

# === Função para detecção de manchas em imagem ===
def detectar_manchas_ampliado(frame_bgr):
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mascara = cv2.threshold(gray, 115, 225, cv2.THRESH_BINARY_INV)
    kernel = np.ones((7, 7), np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_total = mascara.shape[0] * mascara.shape[1]
    area_manchas = sum(cv2.contourArea(c) for c in contornos)
    area_percent = round((area_manchas / area_total) * 100, 2)
    return contornos, area_percent, mascara

# === Função para converter GIF em vídeo com análise ===
def gif_para_video(gif_path, video_path="output.mp4", fps=5):
    gif = Image.open(gif_path)
    num_frames = gif.n_frames
    areas = []

    # Pega resolução do primeiro frame
    gif.seek(0)
    frame_pil = gif.convert("RGB")
    frame_np = np.array(frame_pil)
    altura, largura, _ = frame_np.shape

    # Cria vídeo
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(video_path, fourcc, fps, (largura, altura))

    for i in range(num_frames):
        gif.seek(i)
        frame_pil = gif.convert("RGB")
        frame_np = np.array(frame_pil)
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

        contornos, area_percent, _ = detectar_manchas_ampliado(frame_bgr)
        areas.append(area_percent)

        frame_resultado = frame_bgr.copy()
        cv2.drawContours(frame_resultado, contornos, -1, (0, 255, 0), 2)
        cv2.putText(frame_resultado, f"Quadro {i+1} - {area_percent:.2f}%",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)

        video.write(frame_resultado)

    video.release()
    return areas

# === Thread para escutar AIS via rtl_ais ===
def escutar_ais():
    print("📡 Iniciando recepção AIS...")

    try:
        # ✅ Use caminho absoluto se necessário
        processo = subprocess.Popen(
            ["/home/uerjsats/rtl-ais/rtl_ais"],  # Ou "rtl_ais" se copiado para /usr/local/bin
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Agora também captura erros para análise
            text=True
        )
    except FileNotFoundError:
        print("❌ rtl_ais não encontrado. Verifique o caminho ou instale corretamente.")
        return

    for linha in processo.stdout:
        # === Tratamento de erros comuns do RTL-SDR ===
        if "PLL not locked" in linha:
            print("⚠️ Aviso: PLL not locked → o tuner não conseguiu travar na frequência. "
                  "Pode ser frequência fora da faixa (24 MHz a 1.7 GHz) ou problema de alimentação USB.")

        elif "underrun" in linha.lower():
            print("⚠️ Aviso: Buffer underrun → o Raspberry não conseguiu salvar/processar dados a tempo. "
                  "Reduza taxa de amostragem, aumente intervalo (-i) ou grave em /tmp.")

        elif linha.startswith("!AIVDM"):
            # === Decodificação AIS ===
            try:
                msg = ais.decode(linha.strip())
                mmsi = msg.get("mmsi")
                tipo = msg.get("type")
                lat = msg.get("y")
                lon = msg.get("x")
                if lat and lon:
                    print(f"🛳️ MMSI: {mmsi}, Tipo: {tipo}, Posição: ({lat:.5f}, {lon:.5f})")
                else:
                    print(f"🛳️ MMSI: {mmsi}, Tipo: {tipo} (sem posição)")
            except Exception:
                continue
        else:
            # Outras mensagens do rtl_ais
            print(f"🔎 Log SDR: {linha.strip()}")

# === Execução principal ===
if __name__ == "__main__":
    # Iniciar thread AIS
    thread_ais = threading.Thread(target=escutar_ais, daemon=True)
    thread_ais.start()

    # Iniciar gravação da câmera
    cam.start_preview()
    cam.record_video("test.mp4", duration=5)
    print("📷 Vídeo da câmera salvo como test.mp4")

    # Processar GIF
    gif_path = "/home/uerjsats/Downloads/1.gif"
    areas_detectadas = gif_para_video(gif_path, video_path="resultado.mp4", fps=5)

    # Imprimir no terminal
    print("\n📊 Área detectada por quadro:")
    for i, area in enumerate(areas_detectadas):
        print(f"Quadro {i+1}: {area:.2f}%")

    print("\n🎥 Vídeo com análise salvo em: resultado.mp4")

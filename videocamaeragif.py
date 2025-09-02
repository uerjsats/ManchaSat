import cv2
import numpy as np
from PIL import Image
from picamzero import Camera

cam = Camera()

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

    return contornos, area_percent

def gif_para_video(gif_path, video_path="resultado.mp4", fps=5):
    gif = Image.open(gif_path)
    num_frames = gif.n_frames

    # pega resolução do primeiro frame
    gif.seek(0)
    frame_pil = gif.convert("RGB")
    frame_np = np.array(frame_pil)
    altura, largura, _ = frame_np.shape

    # cria escritor de vídeo
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(video_path, fourcc, fps, (largura, altura))

    areas = []

    for i in range(num_frames):
        gif.seek(i)
        frame_pil = gif.convert("RGB")
        frame_np = np.array(frame_pil)
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

        contornos, area_percent = detectar_manchas_ampliado(frame_bgr)
        areas.append(area_percent)

        # desenha contornos e texto no frame
        frame_resultado = frame_bgr.copy()
        cv2.drawContours(frame_resultado, contornos, -1, (0, 255, 0), 2)
        cv2.putText(frame_resultado, f"Quadro {i+1} - {area_percent:.2f}%", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 0, 255), 2)

        # escreve no vídeo
        video.write(frame_resultado)

    video.release()
    print(f"\n🎥 Vídeo salvo em: {video_path}")
    return areas

# 🛰️ Executar
cam.start_preview()
cam.record_video("test.mp4", duration=5)

gif_path = "/home/uerjsats/Downloads/1.gif"
areas_detectadas = gif_para_video(gif_path, video_path="resultado.mp4", fps=5)

print("\n📊 Área detectada por quadro:")
for i, area in enumerate(areas_detectadas):
    print(f"Quadro {i+1}: {area:.2f}%")

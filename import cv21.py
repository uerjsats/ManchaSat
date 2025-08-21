import cv2
import numpy as np
from PIL import Image, ImageSequence
import matplotlib.pyplot as plt

def detectar_manchas_ampliado(frame_bgr):
    # Converter para escala de cinza e aplicar suavização
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold mais permissivo (detecta mais áreas escuras)
    _, mascara = cv2.threshold(gray, 115, 225, cv2.THRESH_BINARY_INV)

    # Morfologia para limpar e preencher regiões desconexas
    kernel = np.ones((7, 7), np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)

    # Contornos
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Calcular área da mancha
    area_total = mascara.shape[0] * mascara.shape[1]
    area_manchas = sum(cv2.contourArea(c) for c in contornos)
    area_percent = round((area_manchas / area_total) * 100, 2)

    return contornos, area_percent, mascara

def processar_gif_aprimorado(gif_path):
    gif = Image.open(gif_path)
    num_frames = gif.n_frames
    areas = []

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))

    for i in range(num_frames):
        gif.seek(i)
        frame_pil = gif.convert("RGB")
        frame_np = np.array(frame_pil)
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)

        contornos, area_percent, mascara = detectar_manchas_ampliado(frame_bgr)
        areas.append(area_percent)

        # Mostrar frame com contornos
        frame_resultado = frame_bgr.copy()
        cv2.drawContours(frame_resultado, contornos, -1, (0, 255, 0), 2)

        ax.clear()
        ax.imshow(cv2.cvtColor(frame_resultado, cv2.COLOR_BGR2RGB))
        ax.set_title(f"Quadro {i+1} — Mancha detectada: {area_percent:.2f}%")
        ax.axis("off")
        plt.pause(0.1)

    plt.ioff()
    plt.show()

    return areas

# 🛰️ Executar o algoritmo aprimorado
gif_path = "c:/Users/Helio/Desktop/codigos/1.gif"
areas_detectadas = processar_gif_aprimorado(gif_path)

# 📈 Plotar gráfico da evolução da mancha
plt.figure(figsize=(10, 4))
plt.plot(range(1, len(areas_detectadas)+1), areas_detectadas, marker='o', color='darkgreen')
plt.title("Evolução da área da mancha escura com detecção aprimorada")
plt.xlabel("Quadro")
plt.ylabel("Área detectada (%)")
plt.grid(True)
plt.tight_layout()
plt.show()

# 📋 Mostrar resultados no terminal
print("\n📊 Área detectada por quadro:")
for i, area in enumerate(areas_detectadas):
    print(f"Quadro {i+1}: {area:.2f}%")

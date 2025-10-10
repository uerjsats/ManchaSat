import cv2
import numpy as np
import time
from picamera2 import Picamera2

# === Inicializar Picamera2 ===
picam2 = Picamera2()
picam2.start()

# === Função de detecção de manchas ===
def detectar_manchas_final(frame_bgr):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    # --- fundo azul ---
    azul_min = np.array([85, 50, 50])
    azul_max = np.array([135, 255, 255])
    mask_azul = cv2.inRange(hsv, azul_min, azul_max)

    # --- manchas pretas / escuras ---
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 80])
    mask_preto = cv2.inRange(hsv, lower_black, upper_black)

    # --- combinar azul + preto ---
    mask_manchas = cv2.bitwise_and(mask_azul, mask_preto)

    # --- limpeza morfológica ---
    kernel = np.ones((5,5), np.uint8)
    mask_manchas = cv2.morphologyEx(mask_manchas, cv2.MORPH_OPEN, kernel)
    mask_manchas = cv2.morphologyEx(mask_manchas, cv2.MORPH_CLOSE, kernel)

    # --- contornos ---
    contornos, _ = cv2.findContours(mask_manchas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # --- porcentagem ---
    area_total = np.count_nonzero(mask_azul)
    area_manchas = sum(cv2.contourArea(c) for c in contornos)
    area_percent = round((area_manchas / area_total) * 100, 2) if area_total>0 else 0

    return contornos, area_percent, mask_manchas


# === Função principal para análise em tempo real ===
def analisar_camera_rpi_real_time(salvar_saida=False, duracao=60):
    largura, altura = 640, 480
    fps = 30

    if salvar_saida:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter("manchas_camera.mp4", fourcc, fps, (largura, altura))
    else:
        out = None

    print("🎥 Captura da câmera iniciada. Pressione Ctrl+C ou 'q' para sair.")

    start_time = time.time()

    try:
        while True:
            frame = picam2.capture_array()  # captura frame como NumPy array

            contornos, area_percent, _ = detectar_manchas_final(frame)

            # desenhar resultados
            frame_resultado = frame.copy()
            cv2.drawContours(frame_resultado, contornos, -1, (0, 255, 0), 2)
            cv2.putText(frame_resultado, f"Área: {area_percent:.2f}%",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Manchas - Camera RPi", frame_resultado)
            if out:
                out.write(frame_resultado)

            # sair
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if time.time() - start_time > duracao:
                break

    except KeyboardInterrupt:
        print("🛑 Interrompido pelo usuário.")

    if out:
        out.release()
        print("💾 Vídeo salvo como 'manchas_camera.mp4'")

    picam2.stop()
    cv2.destroyAllWindows()


# === Execução ===
if __name__ == "__main__":
    analisar_camera_rpi_real_time(salvar_saida=True, duracao=60)


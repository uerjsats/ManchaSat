import cv2
import numpy as np
from picamera2 import Picamera2

# === Inicializar Picamera2 ===
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480)},
    controls={"FrameDurationLimits": (33333, 33333)}
)
picam2.configure(config)
picam2.start()

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("manchas_rpi.mp4", fourcc, 30, (640, 480))

kernel = np.ones((10, 10), np.uint8)

print("🎥 Captura iniciada. Pressione 'q' para sair.")

try:
    while True:
        frame_color = picam2.capture_array("main")
        frame_color = cv2.cvtColor(frame_color, cv2.COLOR_RGB2BGR)
        # Converter imagem para HSV (melhor para filtrar tons escuros)
        hsv_img = cv2.cvtColor(frame_color, cv2.COLOR_BGR2HSV)
        # Máscara para tons de preto a marrom escuro (ajuste conforme seu experimento)
        # H: 0-30 | S: 0-100 | V: 0-80
        mask_escura = cv2.inRange(hsv_img, (0, 0, 0), (30, 100, 80))
        # Limpeza morfológica
        mask_clean = cv2.morphologyEx(mask_escura, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        result_frame = frame_color.copy()
        print(result_frame)
        manchas_detectadas = 0
        for c in contours:
            area = cv2.contourArea(c)
            if area < 20 or area > 15000:
                continue
            perimeter = cv2.arcLength(c, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter ** 2)
            if circularity > 0.80:  # ignora redondos (bolhas, sujeira comum)
                continue
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = float(w) / h if h != 0 else 0
            if 0.2 < aspect_ratio < 5:
                # Média de cor da mancha (área interna)
                mask = np.zeros(mask_clean.shape, np.uint8)
                cv2.drawContours(mask, [c], -1, 255, -1)
                mean_val = cv2.mean(hsv_img, mask=mask)
                # Verifica se tem “brilho” típico (não totalmente preto)
                if mean_val[2] > 10 and mean_val[1] > 10:  # V>10 S>10
                    manchas_detectadas += 1
                    cv2.rectangle(result_frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
                    cv2.putText(result_frame, f"Lat:{y + h // 2} Lon:{x + w // 2}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(result_frame, f"Manchas: {manchas_detectadas}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Manchas - RPi (Colorido)", result_frame)
        cv2.imshow("Binaria", mask_clean)
        out.write(result_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print("🛑 Captura interrompida pelo usuário.")

picam2.stop()
out.release()
cv2.destroyAllWindows()

print("✅ Vídeo salvo como 'manchas_rpi.mp4'")


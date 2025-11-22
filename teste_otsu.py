
import cv2
import numpy as np
from picamera2 import Picamera2

# === Inicializar Picamera2 ===
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (640, 480)},  # resolução
    controls={"FrameDurationLimits": (33333, 33333)}  # ~30 FPS
)
picam2.configure(config)
picam2.start()

# === Configuração do vídeo de saída ===
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("manchas_rpi.mp4", fourcc, 30, (640, 480))

kernel = np.ones((10,10), np.uint8)

print("🎥 Captura iniciada. Pressione Ctrl+C ou 'q' para sair.")

try:
    while True:
        # Captura frame da câmera
        frame = picam2.capture_array("main")

        # Converter para escala de cinza
        # Se o frame vier em RAW16, converta para uint8
        if frame.dtype != np.uint8:
            gray_img = (frame >> 8).astype(np.uint8)  # pega os 8 bits mais significativos
        else:
            gray_img = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Filtrar pixels muito escuros (manchas)
        fgray_img = cv2.inRange(gray_img, 50, 255)  # ajuste para tons de preto/mancha

        """cv2.imshow("GrayScaleImage",fgray_img) 
        cv2.waitKey(0)
        cv2.destroyAllWindows()"""



        # Binarização Otsu
        _, bw_img = cv2.threshold(fgray_img, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        """cv2.imshow("GrayScaleImage",bw_img) 
        cv2.waitKey(0)
        cv2.destroyAllWindows()"""

        # Limpeza morfológica
        binary_clean_img = cv2.morphologyEx(bw_img, cv2.MORPH_CLOSE, kernel)
        """cv2.imshow("GrayScaleImage", binary_clean_img) 
        cv2.waitKey(0)
        cv2.destroyAllWindows()"""
        # Detectar contornos
        contours, _ = cv2.findContours(binary_clean_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.imshow("GrayScaleImage", _) 
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        

        # Imagem para desenhar resultados
        result_frame = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)  # converter para BGR para desenhar

        for c in contours:
            area = cv2.contourArea(c)
            if area < 50:  # ignorar pequenas regiões
                continue

        # Calcular perímetro e circularidade
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)

        # Ignorar contornos muito circulares (por exemplo circularidade > 0.8)
        if circularity > 0.8:
            continue

        # Pontos extremos
        leftmost = tuple(c[c[:,:,0].argmin()][0])
        rightmost = tuple(c[c[:,:,0].argmax()][0])
        topmost = tuple(c[c[:,:,1].argmin()][0])
        bottommost = tuple(c[c[:,:,1].argmax()][0])
        points = [leftmost, rightmost, topmost, bottommost]
        labels = ['ESQ','DIR','TOPO','BASE']
        colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0)]

        # Retângulo delimitador
        x, y, w, h = cv2.boundingRect(c)

        # Desenhar contorno, retângulo e pontos
        cv2.drawContours(result_frame, [c], -1, (0,255,0), 2)
        cv2.rectangle(result_frame, (x,y), (x+w,y+h), (255,0,255),2)
        for point, color, label in zip(points, colors, labels):
            cv2.circle(result_frame, point, 5, color, -1)
            cv2.putText(result_frame, label, (point[0]+5, point[1]-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # Mostrar resultado em tempo real
            cv2.imshow("Manchas - RPi", result_frame)
            cv2.imshow("Binaria", binary_clean_img)

            # Gravar vídeo processado
            out.write(result_frame)

            # Sair com 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

except KeyboardInterrupt:
    print("🛑 Captura interrompida pelo usuário.")

# Liberar recursos
picam2.stop()
out.release()
cv2.destroyAllWindows()
print("✅ Vídeo salvo como 'manchas_rpi.mp4'")
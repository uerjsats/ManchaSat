import cv2
import numpy as np
import time
from picamera2 import Picamera2

# === Inicializar Picamera2 ===
picam2 = Picamera2()
picam2.start()

# === Função de detecção de manchas (linhas pretas) ===
def detectar_manchas_final(frame_bgr):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

    # --- Detecção de PRETO/MUITO ESCURO ---
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([151, 151, 151])  # Detecta preto e cinza muito escuro
    mask_preto = cv2.inRange(hsv, lower_black, upper_black)

    # --- Limpeza morfológica ---
    kernel = np.ones((3,3), np.uint8)
    mask_preto = cv2.morphologyEx(mask_preto, cv2.MORPH_OPEN, kernel, iterations=1)
    mask_preto = cv2.morphologyEx(mask_preto, cv2.MORPH_CLOSE, kernel, iterations=2)

    # --- Encontrar contornos ---
    contornos, _ = cv2.findContours(mask_preto, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # --- Filtrar para detectar APENAS LINHAS/BARRAS alongadas ---
    linhas_detectadas = []
    for c in contornos:
        area = cv2.contourArea(c)
        if area < 50:  # Ignorar ruído muito pequeno
            continue
        
        # Calcular retângulo rotacionado (para pegar orientação da linha)
        rect = cv2.minAreaRect(c)
        width, height = rect[1]
        
        if width == 0 or height == 0:
            continue
        
        # Aspect ratio (proporção) - linhas têm proporção alta
        aspect_ratio = max(width, height) / min(width, height)
        
        # Se aspect_ratio > 3, é uma linha/barra alongada
        if aspect_ratio > 3.0:
            linhas_detectadas.append(c)

    # --- Porcentagem ---
    area_total = frame_bgr.shape[0] * frame_bgr.shape[1]
    area_manchas = sum(cv2.contourArea(c) for c in linhas_detectadas)
    area_percent = round((area_manchas / area_total) * 100, 4) if area_total>0 else 0

    return linhas_detectadas, area_percent, mask_preto


# === Função principal para análise em tempo real ===
def analisar_camera_rpi_real_time(salvar_saida=False):
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
            frame = picam2.capture_array()  # captura frame como NumPy array (RGB)
            
            # Converter RGB para BGR
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            contornos, area_percent, mask_preto = detectar_manchas_final(frame_bgr)

            # desenhar resultados
            frame_resultado = frame_bgr.copy()
            
            # Desenhar cada linha detectada com informações
            for i, c in enumerate(contornos):
                # Desenhar contorno
                cv2.drawContours(frame_resultado, [c], -1, (0, 255, 0), 2)
                
                # Desenhar retângulo rotacionado
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(frame_resultado, [box], 0, (255, 0, 0), 2)
                
                # Calcular ângulo
                angle = rect[2]
                width, height = rect[1]
                if width < height:
                    angle = 90 - angle
                else:
                    angle = -angle
                
                # Mostrar informações
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    cv2.putText(frame_resultado, f"L{i+1}: {angle:.1f}deg", 
                               (cX-30, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Informações gerais
            cv2.putText(frame_resultado, f"Area: {area_percent:.4f}%",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(frame_resultado, f"Linhas: {len(contornos)}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # Mostrar janelas
            cv2.imshow("Mask - Deteccao Preto", mask_preto)
            cv2.imshow("Linhas Pretas - Camera RPi", frame_resultado)
            
            if out:
                out.write(frame_resultado)

            # sair
            if cv2.waitKey(1) & 0xFF == ord('q'):
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
    analisar_camera_rpi_real_time(salvar_saida=True)
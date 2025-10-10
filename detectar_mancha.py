import cv2
import numpy as np

# === Função para detecção de manchas ===
def detectar_manchas_final(frame_bgr):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    # --- fundo azul ---
    azul_min = np.array([85, 50, 50])
    azul_max = np.array([135, 255, 255])
    mask_azul = cv2.inRange(hsv, azul_min, azul_max)

    # --- manchas pretas / escuras ---
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 80])  # aumenta V para pegar cinza escuro
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




# === Função principal para analisar vídeo ===
def analisar_video(video_path, salvar_saida=True):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Erro ao abrir o vídeo.")
        return

    # informações do vídeo original
    fps = cap.get(cv2.CAP_PROP_FPS)
    largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # configuração do vídeo de saída (opcional)
    if salvar_saida:
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter("analise_manchas_saida.mp4", codec, fps, (largura, altura))
    else:
        out = None

    print("🎥 Analisando vídeo:", video_path)
    print("Pressione 'q' para sair da visualização.")

    frame_count = 0
    while True:
        ret, frame_bgr = cap.read()
        if not ret:
            break

        contornos, area_percent, mascara = detectar_manchas_final(frame_bgr)



        # desenha os resultados
        frame_resultado = frame_bgr.copy()
        cv2.drawContours(frame_resultado, contornos, -1, (0, 255, 0), 2)
        cv2.putText(frame_resultado, f"Area: {area_percent:.2f}%",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)

        cv2.imshow("Analise de Manchas - Video", frame_resultado)
        if out:
            out.write(frame_resultado)

        frame_count += 1
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    print(f"✅ Análise concluída. Frames processados: {frame_count}")
    cap.release()
    if out:
        out.release()
        print("💾 Vídeo salvo como 'analise_manchas_saida.mp4'")
    cv2.destroyAllWindows()


# === Execução ===
if __name__ == "__main__":
    analisar_video("manchas_video_rastro.mp4", salvar_saida=True)

import cv2
import numpy as np
import matplotlib.pyplot as plt

filein = "teste.jpg"

# Ler arquivo
img = cv2.imread(filein)
if img is None:
    print("Erro: Não foi possível carregar a imagem!")
    exit()

cv2.imshow("Original Image", img)

# Converter para escala de cinza
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Filtrar imagem cinza
fgray_img = cv2.inRange(gray_img, 50, 255)

# Transformar para imagem preto e branco
(thresh, bw_img) = cv2.threshold(fgray_img, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# Remover ruído da imagem
kernel = np.ones((10, 10), np.uint8)
binary_clean_img = cv2.morphologyEx(bw_img, cv2.MORPH_CLOSE, kernel) 
cv2.imshow("Binary Clean", binary_clean_img)

# Encontrar contornos na imagem binária
contours, hierarchy = cv2.findContours(binary_clean_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Criar imagens para visualização
contour_image = img.copy()
extreme_points_image = binary_clean_img.copy()
extreme_points_image = cv2.cvtColor(extreme_points_image, cv2.COLOR_GRAY2BGR)  # Converter para colorida para desenhar pontos

print("=== COORDENADAS DAS EXTREMIDADES DAS MANCHAS ===")

# Analisar cada contorno encontrado
for i, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    
    # Filtrar por área mínima (ajuste conforme necessário)
    if area > 100:
        print(f"\n--- Mancha {i+1} ---")
        print(f"Área: {area:.2f} pixels")
        
        # MÉTODO 1: Pontos extremos do contorno
        leftmost = tuple(contour[contour[:,:,0].argmin()][0])
        rightmost = tuple(contour[contour[:,:,0].argmax()][0])
        topmost = tuple(contour[contour[:,:,1].argmin()][0])
        bottommost = tuple(contour[contour[:,:,1].argmax()][0])
        
        print("Pontos extremos do contorno:")
        print(f"  Ponto mais à ESQUERDA: ({leftmost[0]}, {leftmost[1]})")
        print(f"  Ponto mais à DIREITA:  ({rightmost[0]}, {rightmost[1]})")
        print(f"  Ponto mais ao TOPO:    ({topmost[0]}, {topmost[1]})")
        print(f"  Ponto mais à BASE:     ({bottommost[0]}, {bottommost[1]})")
        
        # MÉTODO 2: Retângulo delimitador
        x, y, w, h = cv2.boundingRect(contour)
        bbox_points = {
            'superior_esquerdo': (x, y),
            'superior_direito': (x + w, y),
            'inferior_esquerdo': (x, y + h),
            'inferior_direito': (x + w, y + h)
        }
        
        print("\nRetângulo delimitador:")
        for ponto, coord in bbox_points.items():
            print(f"  {ponto.replace('_', ' ').title()}: ({coord[0]}, {coord[1]})")
        
        # MÉTODO 3: Encontrar todos os pontos na borda da mancha (coordenadas não-zero)
        y_coords, x_coords = np.where(binary_clean_img == 255)
        if len(x_coords) > 0 and len(y_coords) > 0:
            mancha_points = list(zip(x_coords, y_coords))
            
            # Encontrar pontos extremos na imagem binária completa
            min_x_bin, max_x_bin = np.min(x_coords), np.max(x_coords)
            min_y_bin, max_y_bin = np.min(y_coords), np.max(y_coords)
            
            # Encontrar coordenadas exatas dos pontos extremos
            left_point_bin = (min_x_bin, y_coords[np.argmin(x_coords)])
            right_point_bin = (max_x_bin, y_coords[np.argmax(x_coords)])
            top_point_bin = (x_coords[np.argmin(y_coords)], min_y_bin)
            bottom_point_bin = (x_coords[np.argmax(y_coords)], max_y_bin)
            
            print("\nPontos extremos na imagem binária:")
            print(f"  Esquerda: ({left_point_bin[0]}, {left_point_bin[1]})")
            print(f"  Direita:  ({right_point_bin[0]}, {right_point_bin[1]})")
            print(f"  Topo:     ({top_point_bin[0]}, {top_point_bin[1]})")
            print(f"  Base:     ({bottom_point_bin[0]}, {bottom_point_bin[1]})")
        
        # DESENHAR OS PONTOS EXTREMOS NAS IMAGENS
        
        # Desenhar contorno na imagem original
        cv2.drawContours(contour_image, [contour], -1, (0, 255, 0), 2)
        
        # Desenhar pontos extremos na imagem original
        points = [leftmost, rightmost, topmost, bottommost]
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Azul, Verde, Vermelho, Ciano
        labels = ['ESQ', 'DIR', 'TOP', 'BASE']
        
        for point, color, label in zip(points, colors, labels):
            cv2.circle(contour_image, point, 8, color, -1)
            cv2.putText(contour_image, label, (point[0] + 10, point[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Desenhar pontos extremos na imagem binária
        for point, color, label in zip(points, colors, labels):
            cv2.circle(extreme_points_image, point, 6, color, -1)
            cv2.putText(extreme_points_image, label, (point[0] + 8, point[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Desenhar retângulo delimitador
        cv2.rectangle(contour_image, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.rectangle(extreme_points_image, (x, y), (x + w, y + h), (255, 0, 255), 1)

# Mostrar resultados
cv2.imshow("Contornos com Pontos Extremos", contour_image)
cv2.imshow("Imagem Binária com Pontos Extremos", extreme_points_image)

# Salvar resultados
cv2.imwrite("contornos_com_pontos.jpg", contour_image)
cv2.imwrite("binaria_com_pontos.jpg", extreme_points_image)

print(f"\nTotal de manchas detectadas: {len([c for c in contours if cv2.contourArea(c) > 100])}")

cv2.waitKey(0)
cv2.destroyAllWindows()

# Versão alternativa para obter TODAS as coordenadas da borda
print("\n=== TODAS AS COORDENADAS DA BORDA ===")
for i, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    if area > 100:
        print(f"\nMancha {i+1} - Coordenadas da borda (primeiros 20 pontos):")
        for j, point in enumerate(contour[:20]):  # Mostra apenas os primeiros 20 pontos
            print(f"  Ponto {j+1}: ({point[0][0]}, {point[0][1]})")
        if len(contour) > 20:
            print(f"  ... e mais {len(contour) - 20} pontos")
import cv2
import numpy as np
import matplotlib
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt

filein = "teste.jpg"

# ler arquivo
img = cv2.imread(filein)
cv2.imshow("Original Image",img) 
#cv2.waitKey(0)
#cv2.destroyAllWindows()

# obter imagem cinza
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#cv2.imshow("GrayScaleImage",gray_img) 
#cv2.waitKey(0)
#cv2.destroyAllWindows()

# filtrar imagem cinza
fgray_img = cv2.inRange(gray_img, 50, 255)
#cv2.imshow("Gray Image Scale after Threshold",image) 
#cv2.waitKey(0)
#cv2.destroyAllWindows()
	
# Transformar para image preto e branco
(thresh, bw_img) = cv2.threshold(fgray_img, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
#cv2.imshow("BW_image",image) 
#cv2.waitKey(0)
#cv2.destroyAllWindows()

# Remover ruído da imagem (pequenos objetos)
kernel = np.ones((10, 10), np.uint8)
binary_clean_img = cv2.morphologyEx(bw_img, cv2.MORPH_CLOSE, kernel) 
cv2.imshow("Binary Clean",binary_clean_img) 
#cv2.waitKey(0)
#cv2.destroyAllWindows()
 
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_clean_img, connectivity=8)  
print(num_labels)
print(labels)
print(stats)
print(centroids)

contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
image_copy = binary_clean_img.copy()
cv2.drawContours(image=image_copy, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
                
# see the results
cv2.imshow('None approximation', image_copy)
cv2.waitKey(0)
cv2.imwrite('contours_none_image1.jpg', image_copy)
cv2.destroyAllWindows()

# plt.figure()
# #plt.imshow(binary_clean_img,cmap="gray")
# plt.title("Cleaned Image")
# plt.axis("on")
# pnt1 = plt.Circle((495,439),20,color='r')
# ax = plt.subplots()
# plt.gca().add_patch(pnt1)

# figure, axes = plt.subplots()
# draw_circle = plt.Circle((0.5, 0.5), 0.3)

# axes.set_aspect(1)
# axes.add_artist(draw_circle)
# plt.title("Circle")
# plt.show()

# #ax = plt.gca()
# #ax.cla() # clear things for fresh plot

# plt.show()

cv2.waitKey(0)
cv2.destroyAllWindows()
plt.close()

# detectar mancha, área, direção principal e coordenadas extremas 


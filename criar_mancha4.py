import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# ----- Configurações -----
N_OBJETOS = 8          # quantidade de círculos coloridos
DURACAO = 15           # segundos
FPS = 24
FRAMES = DURACAO * FPS
RASTRO_LEN = 60         # comprimento do rastro
FIM_RASTRO = 30        # frames até o rastro parar de crescer

# limites do gráfico (graus)
X_LIM = (-180, 180)    # longitude
Y_LIM = (-90, 90)      # latitude

# tamanho da figura (50x26 cm) e DPI
fig_width_cm = 50
fig_height_cm = 26
dpi = 150
fig_width_in = fig_width_cm / 2.54
fig_height_in = fig_height_cm / 2.54

# gera posições iniciais aleatórias (lon, lat)
pos = np.random.uniform([X_LIM[0], Y_LIM[0]], [X_LIM[1], Y_LIM[1]], (N_OBJETOS, 2))
vel = np.random.uniform(-0.2, 0.2, (N_OBJETOS, 2))  # variação em graus por frame
cores = ['red', 'green', 'blue', 'yellow', 'orange', 'purple', 'brown', 'gray']

# ----- Setup do plot -----
fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in), dpi=dpi)
ax.set_xlim(X_LIM)
ax.set_ylim(Y_LIM)
ax.set_facecolor('#87CEEB')  # azul claro

ax.set_title("ManchaSat Camera Scene Simulation", fontsize=14, fontweight='bold')
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# cria os pontos coloridos
pontos = []
for i in range(N_OBJETOS):
    ponto, = ax.plot([], [], 'o', color=cores[i % len(cores)], markersize=15)
    pontos.append(ponto)

# cria sombras/rastros aleatórios
num_sombras = random.randint(1, max(1, N_OBJETOS // 2 - 1))
indices_sombras = random.sample(range(N_OBJETOS), num_sombras)

rastros = []
historico = []
for i in range(N_OBJETOS):
    if i in indices_sombras:
        rastro, = ax.plot([], [], '-', color='black', linewidth=6, alpha=0.7)
        rastros.append(rastro)
        historico.append([])  # armazena posições passadas
    else:
        rastros.append(None)
        historico.append(None)

# ----- Função para converter lon/lat em pixels da figura -----
def lonlat_to_pixels(lon, lat):
    """Converte longitude e latitude para coordenadas em pixels do vídeo"""
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width_px, height_px = bbox.width * dpi, bbox.height * dpi
    px = (lon - X_LIM[0]) / (X_LIM[1] - X_LIM[0]) * width_px
    py = (lat - Y_LIM[0]) / (Y_LIM[1] - Y_LIM[0]) * height_px
    return px, py

# ----- Função de atualização -----
def update(frame):
    global pos, vel
    pos += vel

    # colisão com bordas (inverte direção)
    for i in range(N_OBJETOS):
        if pos[i, 0] < X_LIM[0] or pos[i, 0] > X_LIM[1]:
            vel[i, 0] *= -1
        if pos[i, 1] < Y_LIM[0] or pos[i, 1] > Y_LIM[1]:
            vel[i, 1] *= -1

    # atualiza rastros/manchas
    for i, rastro in enumerate(rastros):
        if rastro is not None:
            if frame < FIM_RASTRO:
                historico[i].append(pos[i].copy())
                if len(historico[i]) > RASTRO_LEN:
                    historico[i].pop(0)
            xy = np.array(historico[i])
            rastro.set_data(xy[:,0], xy[:,1])

    # atualiza posições dos pontos
    for i, ponto in enumerate(pontos):
        ponto.set_data(pos[i,0], pos[i,1])

        # Exemplo: pega pixels da bolinha
        px, py = lonlat_to_pixels(pos[i,0], pos[i,1])
        # print(f"Bola {i}: lon={pos[i,0]:.2f}, lat={pos[i,1]:.2f}, px={px:.1f}, py={py:.1f}")
        # Use (px, py) para interface com a câmera real
        # imprime coordenadas convertidas
        lat_deg, lat_min, lat_sec, lat_hem = decimal_to_dms(pos[i,1], is_lat=True)
        lon_deg, lon_min, lon_sec, lon_hem = decimal_to_dms(pos[i,0], is_lat=False)

        print(
                f"Bola {i}: "
                f"Lat = {abs(lat_deg)}° {lat_min}' {lat_sec:.2f}\" {lat_hem}, "
                f"Lon = {abs(lon_deg)}° {lon_min}' {lon_sec:.2f}\" {lon_hem}, "
                f"Pixel=({px:.1f}, {py:.1f})"
        )   



    return pontos + [r for r in rastros if r is not None]

def decimal_to_dms(value, is_lat=True):
    """
    Converte coordenada decimal para graus, minutos e segundos.
    value: latitude ou longitude em decimal
    is_lat: True = Latitude, False = Longitude (apenas para colocar N/S/E/W)
    """
    graus = int(value)
    minutos_float = abs(value - graus) * 60
    minutos = int(minutos_float)
    segundos = (minutos_float - minutos) * 60

    # Define letra de hemisfério
    if is_lat:
        hemis = "N" if value >= 0 else "S"
    else:
        hemis = "E" if value >= 0 else "W"

    return graus, minutos, segundos, hemis


# ----- Cria animação -----
ani = animation.FuncAnimation(
    fig, update, frames=FRAMES, interval=1000/FPS, blit=True
)

# salva vídeo em MP4
ani.save("manchas_video_pixels.mp4", fps=FPS, dpi=dpi, extra_args=['-vcodec', 'libx264'])

plt.close(fig)
print("✅ Vídeo 'manchas_video_pixels.mp4' criado com sucesso!")



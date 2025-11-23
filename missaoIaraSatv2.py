import time
import threading
import cv2
import numpy as np
import math
import serial
from pyais.stream import TCPConnection
from picamera2 import Picamera2

# ==========================================================
# Configuração do AIS Real
# ==========================================================
AIS_HOST = 'localhost'
AIS_PORT = 10110

NAVIOS_AIS = []           
NAVIOS_LOCK = threading.Lock()

# ==========================================================
# Configuração da Comunicação Serial
# ==========================================================
serial_port = '/dev/serial0' #Talvez altere, por versões
baudrate = 115200
ser = serial.Serial(serial_port, baudrate, timeout=1)

# ==========================================================
# Thread AIS
# ==========================================================
def thread_ais_real():
    global NAVIOS_AIS
    print(f"[AIS] Conectando ao AIS real {AIS_HOST}:{AIS_PORT}")

    for msg in TCPConnection(AIS_HOST, port=AIS_PORT):
        try:
            ais = msg.decode()
            if ais.msg_type != 21:
                continue

            mmsi = ais.mmsi
            nome = ais.name if ais.name else "DESCONHECIDO"
            lat = ais.lat
            lon = ais.lon

            with NAVIOS_LOCK:
                NAVIOS_AIS.append((mmsi, nome, lat, lon))

            print(f"[AIS] {mmsi} | {nome} | {lat:.4f}, {lon:.4f}")

        except Exception as e:
            print("[AIS] Erro:", e)

threading.Thread(target=thread_ais_real, daemon=True).start()

# ==========================================================
# Converter área em PX² → KM²
# ==========================================================
def areaPara_km2(area_px):
    deg_lat_per_px = 160 / 480
    deg_lon_per_px = 300 / 640
    area_1px_deg2 = deg_lat_per_px * deg_lon_per_px
    area_deg2 = area_px * area_1px_deg2
    km_por_grau = 111
    return area_deg2 * km_por_grau * km_por_grau

# ==========================================================
# Encontrar navio AIS mais próximo
# ==========================================================
def encontrar_navio_ais(lat_video, lon_video):
    with NAVIOS_LOCK:
        if not NAVIOS_AIS:
            return None, None

        melhor = None
        menor = float("inf")

        for mmsi, nome, lat, lon in NAVIOS_AIS:
            dist = math.sqrt((lat - lat_video)**2 + (lon - lon_video)**2)
            if dist < menor:
                menor = dist
                melhor = (mmsi, nome, lat, lon)

        return melhor, menor

# ==========================================================
# Detectar mancha escura
# ==========================================================
def calcular_area_mancha(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_dark = np.array([0, 20, 20])
    upper_dark = np.array([180, 150, 90])
    mask = cv2.inRange(hsv, lower_dark, upper_dark)

    kernel = np.ones((5, 5), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contornos, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contornos) == 0:
        return 0, None

    c = max(contornos, key=cv2.contourArea)
    area = cv2.contourArea(c)
    return area, c

# ==========================================================
# Iniciar câmera
# ==========================================================
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "XRGB8888", "size": (640, 480)}
    )
)
picam2.start()

ultimo_print = 0
DELAY_AREA = 1.5

print("\n[CAM] Sistema rodando... Pressione ESC para sair.\n")

# ==========================================================
# Thread que espera comando "12"
# ==========================================================
def ler_comando_serial():
    global ultimo_print

    while True:
        if ser.in_waiting > 0:
            comando = ser.read()
            if comando == b'1':
                comando2 = ser.read()
                if comando2 == b'2':
                    ser.write(b"[SERIAL] Comando 12 recebido!\n")
                    print("[SERIAL] Comando 12 recebido!")

                    while True:
                        frame = picam2.capture_array()

                        # ==================================================
                        #              DETECTAR MANCHA DE ÓLEO
                        # ==================================================
                        area_px, contorno = calcular_area_mancha(frame)

                        cx_m = cy_m = None
                        if contorno is not None and area_px > 0:
                            cv2.drawContours(frame, [contorno], -1, (0, 255, 255), 2)

                            M = cv2.moments(contorno)
                            if M["m00"] > 0:
                                cx_m = int(M["m10"] / M["m00"])
                                cy_m = int(M["m01"] / M["m00"])

                            area_km = areaPara_km2(area_px)

                            agora = time.time()
                            if agora - ultimo_print >= DELAY_AREA:
                                print(f"[MANCHA] {area_km:.6f} km^2")
                                ser.write(f"{area_km:.6f}".encode())
                                ultimo_print = agora

                        # ==================================================
                        #        DETECTAR QUALQUER NAVIO (SEM COR)
                        # ==================================================
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        blur = cv2.GaussianBlur(gray, (7, 7), 0)
                        edges = cv2.Canny(blur, 40, 120)

                        kernel_ship = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
                        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_ship)

                        cont_ship, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        navio_detectado = None
                        dist_min = 9999999

                        if cx_m is not None:
                            for c in cont_ship:
                                area_s = cv2.contourArea(c)
                                if area_s < 300:
                                    continue

                                x, y, w, h = cv2.boundingRect(c)
                                cx_n = x + w // 2
                                cy_n = y + h // 2

                                dist = math.sqrt((cx_n - cx_m)**2 + (cy_n - cy_m)**2)

                                if dist < dist_min:
                                    dist_min = dist
                                    navio_detectado = (cx_n, cy_n, c)

                        # ==================================================
                        #     ASSOCIAR NAVIO DETECTADO → AIS REAL
                        # ==================================================
                        if navio_detectado:
                            cx_n, cy_n, cnav = navio_detectado

                            cv2.drawContours(frame, [cnav], -1, (0, 255, 0), 3)

                            lon = -150 + (cx_n / 640) * 300
                            lat = 80 - (cy_n / 480) * 160

                            navio, dist = encontrar_navio_ais(lat, lon)

                            if navio:
                                mmsi, nome, la, lo = navio
                                print(f"\n>>> NAVIO MAIS PRÓXIMO DA MANCHA <<<\n{nome} | MMSI {mmsi}")
                                ser.write(f"2:{mmsi}:{lat}:{lon}:".encode())

                        # ==================================================
                        # Exibir tela
                        # ==================================================
                        cv2.imshow("Deteccao", frame)

                        if cv2.waitKey(1) == 27:  # ESC
                            break

                    ser.close()
                    cv2.destroyAllWindows()
                    picam2.stop()

        time.sleep(0.1)

threading.Thread(target=ler_comando_serial, daemon=True).start()

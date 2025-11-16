from pyais import decode
import socket
import csv
import os

CSV_FILE = "ais_dados.csv"
mmsi_names = {}  # armazena nomes de embarcações conhecidos

if not os.path.isfile(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["MMSI", "Tipo", "Nome", "Lat", "Lon", "SOG", "COG"])


def processar_mensagem(msg):
    global mmsi_names

    try:
        mmsi = getattr(msg, "mmsi", "N/A")
        tipo = getattr(msg, "type", "N/A")
        lat = getattr(msg, "y", getattr(msg, "lat", "N/A"))
        lon = getattr(msg, "x", getattr(msg, "lon", "N/A"))
        sog = getattr(msg, "sog", "N/A")
        cog = getattr(msg, "cog", "N/A")

        # Se a mensagem tiver shipname (tipo 5), atualiza o dicionário
        shipname = getattr(msg, "shipname", None)
        if shipname:
            mmsi_names[mmsi] = shipname

        # Usa o nome armazenado se disponível
        nome = mmsi_names.get(mmsi, "N/A")

        print(f"MMSI: {mmsi} | Tipo: {tipo} | Nome: {nome} | "
              f"Lat: {lat} | Lon: {lon} | SOG: {sog} kn | COG: {cog}°")

        # Salva no CSV
        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([mmsi, tipo, nome, lat, lon, sog, cog])

    except Exception as e:
        print("Erro ao processar mensagem:", e)


def receber_tcp(host='127.0.0.1', port=10110):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Conectando ao servidor TCP {host}:{port}...")
    sock.connect((host, port))
    print("Conectado! Aguardando mensagens AIS...\n")

    buffer = b""

    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Conexão TCP fechada pelo servidor.")
                break

            buffer += data

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue

                if not line.startswith(b"!AIVDM") and not line.startswith(b"!AIVDO"):
                    continue

                try:
                    msg = decode(line.decode("utf-8", errors="ignore"))
                    processar_mensagem(msg)
                except Exception as e:
                    # Mensagens fragmentadas tipo 5 podem causar erro
                    # Pode ser ignorado ou tratado com pyais.decode_msg
                    pass

        except KeyboardInterrupt:
            print("Encerrando conexão pelo usuário...")
            break
        except Exception as e:
            print("Erro na conexão TCP:", e)
            break

    sock.close()


if __name__ == "__main__":
    receber_tcp("127.0.0.1", 10110)

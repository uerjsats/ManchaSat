from pyais import decode
import socket

def processar_mensagem(msg):
    """
    Recebe objeto AIS decodificado e exibe informações principais
    """
    try:
        mmsi = getattr(msg, "mmsi", "N/A")
        tipo = getattr(msg, "type", "N/A")
        lat = getattr(msg, "y", getattr(msg, "lat", "N/A"))  # algumas versões usam lat/lon
        lon = getattr(msg, "x", getattr(msg, "lon", "N/A"))
        sog = getattr(msg, "sog", "N/A")
        cog = getattr(msg, "cog", "N/A")

        print(f"MMSI: {mmsi} | Tipo: {tipo} | Lat: {lat} | Lon: {lon} | "
              f"SOG: {sog} kn | COG: {cog}°")
    except Exception as e:
        print("Erro ao processar mensagem:", e)


def receber_tcp(host='127.0.0.1', port=10110):
    """
    Conecta via TCP ao AIS-catcher e processa mensagens AIS.
    """
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

            # processa mensagens completas separadas por '\n'
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue

                # ignora linhas que não são NMEA AIS
                if not line.startswith(b"!AIVDM") and not line.startswith(b"!AIVDO"):
                    continue

                try:
                    msg = decode(line.decode("utf-8", errors="ignore"))
                    processar_mensagem(msg)
                except Exception as e:
                    print(f"[Erro decode NMEA] {e}")

        except KeyboardInterrupt:
            print("Encerrando conexão pelo usuário...")
            break
        except Exception as e:
            print("Erro na conexão TCP:", e)
            break

    sock.close()


if __name__ == "__main__":
    receber_tcp("127.0.0.1", 10110)


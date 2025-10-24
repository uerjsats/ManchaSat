from rtlsdr import RtlSdr
from pyais import decode
import numpy as np

# --- Configuração do RTL-SDR ---
sdr = RtlSdr()
sdr.sample_rate = 2.4e6         # taxa de amostragem
sdr.center_freq = 162.0e6       # frequência central AIS
sdr.gain = 'auto'

SAMPLES = 256*1024              # número de amostras por captura

# --- Função para processar mensagens AIS ---
def processar_mensagem(msg_bytes):
    try:
        decoded = decode(msg_bytes)
        mmsi = getattr(decoded, "mmsi", "N/A")
        lat = getattr(decoded, "y", "N/A")
        lon = getattr(decoded, "x", "N/A")
        sog = getattr(decoded, "sog", "N/A")
        cog = getattr(decoded, "cog", "N/A")
        tipo = decoded.__class__.__name__   # nome do tipo da mensagem

        print(f"MMSI: {mmsi} | Tipo: {tipo} | Lat: {lat} | Lon: {lon} | SOG: {sog} kn | COG: {cog}°")
    except Exception as e:
        print(f"Erro ao decodificar mensagem: {e}")

# --- Função principal ---
def main():
    try:
        while True:
            print(f"Capturando {SAMPLES} amostras em {sdr.center_freq/1e6:.2f} MHz...")
            samples = sdr.read_samples(SAMPLES)

            # --- DEMODULAÇÃO GMSK necessária aqui ---
            # Por enquanto, simulamos algumas mensagens AIS de teste
            mensagens_ais = [
                b"!AIVDM,1,1,,A,15Muq@0020o?;TPG5J0Qw?vN0<0u,0*1C",
                b"!AIVDM,1,1,,B,15Muq@0020o?;TPG5J0Qw?vN0<0u,0*1C"
            ]

            for msg in mensagens_ais:
                processar_mensagem(msg)

    except KeyboardInterrupt:
        print("Encerrando captura AIS...")
    finally:
        sdr.close()
        print("Dispositivo RTL-SDR fechado com sucesso.")

if __name__ == "__main__":
    main()


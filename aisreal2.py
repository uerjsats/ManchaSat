#!/usr/bin/env python3
# decode_ais_validating.py
# Decodificador AIS (tipos 1/2/3) com detecção de sentinelas e validação de plausibilidade.

import sys

def sixbit_from_char(c):
    v = ord(c) - 48
    if v > 40:
        v -= 8
    return v & 0x3F

def payload_to_bitstring(payload):
    bits = []
    for ch in payload:
        v = sixbit_from_char(ch)
        bits.append(format(v, '06b'))
    return ''.join(bits)

def bits_to_uint(bs):
    if bs == '':
        return 0
    return int(bs, 2)

def bits_to_int_signed(bs):
    if bs == '':
        return 0
    if bs[0] == '1':
        val = int(bs, 2)
        bits = len(bs)
        val -= (1 << bits)
        return val
    else:
        return int(bs, 2)

def is_plausible_position(lat, lon):
    if lat is None or lon is None:
        return False
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return False
    return True

def is_plausible_sog(sog):
    # navigos raramente passam de 60 nós; aceitar até 70 para margem,
    # tratar None como não plausível para filtros mais estritos.
    if sog is None:
        return False
    return 0.0 <= sog <= 70.0

def is_plausible_heading(hdg):
    if hdg is None:
        return False
    return 0 <= hdg <= 359

def decode_position_report(bitstr):
    out = {}
    out['msgtype'] = bits_to_uint(bitstr[0:6])
    out['repeat'] = bits_to_uint(bitstr[6:8])
    out['mmsi'] = bits_to_uint(bitstr[8:38])
    out['nav_status'] = bits_to_uint(bitstr[38:42])

    rot_raw = bits_to_int_signed(bitstr[42:50])
    # ROT sentinel: -128 (0b10000000) indicates not available
    out['rot_raw'] = None if rot_raw == -128 else rot_raw

    sog_raw = bits_to_uint(bitstr[50:60])  # 10 bits
    # SOG: 1023 means not available (i.e. 102.3 knots). Convert to None.
    out['sog'] = None if sog_raw == 1023 else sog_raw / 10.0

    out['pos_acc'] = bits_to_uint(bitstr[60:61])

    lon_raw = bits_to_int_signed(bitstr[61:89])  # 28 bits signed
    lat_raw = bits_to_int_signed(bitstr[89:116]) # 27 bits signed

    # Sentinels for not available in the standard:
    LON_NOT_AVAILABLE = 181 * 600000        # 108600000
    LAT_NOT_AVAILABLE = 91 * 600000         # 54600000

    out['lon'] = None if lon_raw == LON_NOT_AVAILABLE else lon_raw / 600000.0
    out['lat'] = None if lat_raw == LAT_NOT_AVAILABLE else lat_raw / 600000.0

    cog_raw = bits_to_uint(bitstr[116:128])  # 12 bits -> 0.1 deg
    # COG sentinel: 3600 (i.e. 360.0 deg) used as not available
    out['cog'] = None if cog_raw >= 3600 else cog_raw / 10.0

    heading_raw = bits_to_uint(bitstr[128:137])  # 9 bits
    # Heading sentinel: 511 indicates not available
    out['true_heading'] = None if heading_raw == 511 else heading_raw

    out['timestamp'] = bits_to_uint(bitstr[137:143])
    return out

def pretty_print(decoded, raw_payload):
    print("Payload:", raw_payload)
    print("Message type:", decoded.get('msgtype'))
    print("MMSI:", decoded.get('mmsi'))
    print("Nav Status:", decoded.get('nav_status'))
    print("SOG (knots):", decoded.get('sog'))
    print("ROT raw:", decoded.get('rot_raw'))
    print("Position accuracy flag:", decoded.get('pos_acc'))
    print("Longitude:", decoded.get('lon'))
    print("Latitude :", decoded.get('lat'))
    print("COG (deg):", decoded.get('cog'))
    print("True heading:", decoded.get('true_heading'))
    print("Timestamp (s):", decoded.get('timestamp'))

def record_is_realistic(decoded):
    # Para considerar "real/aceitavel" vamos exigir:
    # - MMSI plausível (9 dígitos, não zero)
    # - posição válida e plausível
    # - SOG plausível (opcional — se None, aceitar mas marcar como suspeito)
    # - heading plausível
    mmsi = decoded.get('mmsi')
    if not (100000000 <= mmsi <= 999999999):
        return False

    lat = decoded.get('lat')
    lon = decoded.get('lon')
    if not is_plausible_position(lat, lon):
        return False

    # Se quiser filtrar mais estritamente, descomente as checagens abaixo:
    # if not is_plausible_sog(decoded.get('sog')):
    #     return False
    # if not is_plausible_heading(decoded.get('true_heading')):
    #     return False

    return True

def process_payload(payload, require_realistic=False):
    payload = payload.strip().strip('"').strip("'")
    bitstr = payload_to_bitstring(payload)
    if len(bitstr) < 6:
        print("Payload too short:", payload)
        return None
    msgtype = bits_to_uint(bitstr[0:6])
    if msgtype in (1,2,3):
        decoded = decode_position_report(bitstr)
        if require_realistic:
            if record_is_realistic(decoded):
                pretty_print(decoded, payload)
                return decoded
            else:
                print("Mensagem descartada (não plausível):", payload)
                return None
        else:
            pretty_print(decoded, payload)
            return decoded
    else:
        print("Mensagem tipo", msgtype, "não suportada pelo decodificador.")
        return None

def main():
    # Modo 1: receber payload na linha de comando
    # Modo 2: sem args -> ler linhas do stdin (ideal para pipe ou arquivo com vários payloads)
    require_realistic = True  # só imprime registros plausíveis (mude para False se não quiser filtrar)

    if len(sys.argv) >= 2:
        # aceitar múltiplos payloads passados na linha de comando
        for p in sys.argv[1:]:
            process_payload(p, require_realistic=require_realistic)
    else:
        # ler do stdin linha a linha
        print("Lendo payloads do stdin (uma linha por payload). Ctrl+D para terminar.")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            process_payload(line, require_realistic=require_realistic)

if __name__ == "__main__":
    main()

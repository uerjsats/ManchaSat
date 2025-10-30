#!/usr/bin/env python3
# decode_ais.py
# Small AIS AIVDM payload decoder for position reports (types 1/2/3) and basic fields.
# Usage:
#   python3 decode_ais.py 13aEOK?POOPD2WVMDLDRhgvl289?

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
        # two's complement
        val = int(bs, 2)
        bits = len(bs)
        val -= (1 << bits)
        return val
    else:
        return int(bs, 2)

def decode_position_report(bitstr):
    # According to ITU-R M.1371 (simplified)
    # bit offsets (0-based):
    # 0-5:    message type (6)
    # 6-7:    repeat (2)
    # 8-37:   MMSI (30)
    # 38-41:  navigational status (4)
    # 42-49:  rate of turn (ROT) (8, signed)
    # 50-59:  speed over ground (10)
    # 60:     position accuracy (1)
    # 61-88:  longitude (28, signed) -> degrees = raw / 600000.0
    # 89-115: latitude (27, signed) -> degrees = raw / 600000.0
    # 116-127: course over ground (12)
    # 128-136: true heading (9)
    # 137-142: timestamp (6)
    # (fields may continue)
    out = {}
    out['msgtype'] = bits_to_uint(bitstr[0:6])
    out['repeat'] = bits_to_uint(bitstr[6:8])
    out['mmsi'] = bits_to_uint(bitstr[8:38])
    out['nav_status'] = bits_to_uint(bitstr[38:42])
    out['rot_raw'] = bits_to_int_signed(bitstr[42:50])
    out['sog'] = bits_to_uint(bitstr[50:60]) / 10.0  # in knots (10 => 1.0 kn)
    out['pos_acc'] = bits_to_uint(bitstr[60:61])
    lon_raw = bits_to_int_signed(bitstr[61:89])
    lat_raw = bits_to_int_signed(bitstr[89:116])
    out['lon'] = None if lon_raw == 0x6791AC0 else lon_raw / 600000.0  # 181*600000 = 108600000 -> not available sentinel
    out['lat'] = None if lat_raw == 0x3412140 else lat_raw / 600000.0   # 91*600000 = 54600000 -> not available
    out['cog'] = bits_to_uint(bitstr[116:128]) / 10.0
    out['true_heading'] = bits_to_uint(bitstr[128:137])
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 decode_ais.py <AIVDM_payload_string>")
        print("Example: python3 decode_ais.py 13aEOK?POOPD2WVMDLDRhgvl289?")
        sys.exit(1)
    payload = sys.argv[1].strip()
    # remove enclosing quotes, commas etc if present
    payload = payload.strip('"').strip("'").strip()
    bitstr = payload_to_bitstring(payload)
    if len(bitstr) < 6:
        print("Payload too short")
        sys.exit(1)
    msgtype = bits_to_uint(bitstr[0:6])
    if msgtype in (1,2,3):
        decoded = decode_position_report(bitstr)
        pretty_print(decoded, payload)
    else:
        print("Message type", msgtype, "not fully supported by this small decoder.")
        print("Bit length:", len(bitstr))
        print("Raw bits (first 200):", bitstr[:200])

if __name__ == "__main__":
    main()

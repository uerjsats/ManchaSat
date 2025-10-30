#!/usr/bin/env python3
import sys, subprocess, re

# Import your existing functions
from missao_ais import payload_to_bitstring, bits_to_uint, decode_position_report, pretty_print

# Regex para extrair o payload do formato !AIVDM
pattern = re.compile(r'!AIVDM,\d+,\d+,[^,]*,[^,]*,([^,]*),')

# Inicia AIS-catcher
proc = subprocess.Popen(["AIS-catcher", "-v"], stdout=subprocess.PIPE, text=True)

print("🔎 Lendo dados AIS em tempo real... (CTRL+C para sair)\n")

for line in proc.stdout:
    match = pattern.search(line)
    if not match:
        continue
    payload = match.group(1).strip()

    try:
        bitstr = payload_to_bitstring(payload)
        msgtype = bits_to_uint(bitstr[0:6])

        if msgtype in (1,2,3):
            decoded = decode_position_report(bitstr)
            pretty_print(decoded, payload)
            print("-" * 40)

    except Exception as e:
        print("Erro ao decodificar:", e)

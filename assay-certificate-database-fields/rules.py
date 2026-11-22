#!/usr/bin/env python3
"""Ordinary PDF extraction: the certificate's text layer, read with pdftotext, and rules written from the
layout of one certificate (OREAS 902), then frozen. Usage: python3 rules.py cert.pdf  → JSON on stdout.
Needs pdftotext (poppler-utils)."""
import json, re, subprocess, sys
from pathlib import Path

FIELDS = list(json.loads(Path(__file__).with_name('fields.json').read_text())['fields'])
METHOD = [(r'\b4 ?acid|four[- ]acid', '4a'), (r'aqua regia', 'ar'), (r'h2so4|sul(ph|f)uric', 'h2so4'),
          (r'cyanide|nacn', 'cn'), (r'fire assay', 'fa')]
ROW = re.compile(r'^\s*(?P<name>[^()\d]*?)\s*\((?P<unit>wt\.?%|%|ppm|ppb|g/t)\)\s+(?P<value>[\d.]+)\s+(?P<sd>[\d.]+)', re.I)
TO = {('pct', 'wt.%'): 1, ('pct', '%'): 1, ('pct', 'ppm'): 1e-4, ('pct', 'ppb'): 1e-7,
      ('ppm', 'ppm'): 1, ('ppm', 'g/t'): 1, ('ppm', 'ppb'): 1e-3, ('ppm', 'wt.%'): 1e4, ('ppm', '%'): 1e4}

def extract(pdf):
    text = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True, check=True).stdout
    out, certified, method = dict.fromkeys(FIELDS), False, None
    for line in text.splitlines():
        if re.search(r'certified values', line, re.I): certified = True
        elif re.search(r'indicative values|performance gates', line, re.I): certified = False
        row = ROW.match(line)
        if not row:  # a line that names a method and holds no row is a section header
            method = next((m for pat, m in METHOD if re.search(pat, line, re.I)), method)
            continue
        if not certified or not method: continue
        name = row['name']
        el = 'cu' if re.search(r'\bCu\b|copper', name, re.I) else 'au' if re.search(r'\bAu\b|gold', name, re.I) else None
        if not el: continue
        unit = 'pct' if el == 'cu' else 'ppm'
        key = f'{el}_{method}_{unit}'
        if key not in out or out[key] is not None: continue  # first certified match wins
        k = TO[(unit, row['unit'].lower().replace('wt%', 'wt.%'))]
        out[key] = round(float(row['value']) * k, 10)
        out[key.replace(f'_{unit}', f'_sd_{unit}')] = round(float(row['sd']) * k, 10)
    return out

if __name__ == '__main__':
    print(json.dumps(extract(sys.argv[1]), indent=1))

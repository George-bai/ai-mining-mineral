#!/usr/bin/env python3
"""Score every reader's fields against the answer key, field by field.
Usage: python3 score.py <certs dir> <run dir>  → <run dir>/scores.json
<run dir>/<reader>/<cert>[.<attempt>].json holds the fields, bare (rules) or under "fields" (model).
check.json beside key.json holds hand corrections to the script's verdicts, each with its reason."""
import json, math, re, subprocess, sys
from pathlib import Path

here = Path(__file__).parent
KEY = json.loads((here / 'key.json').read_text())['certificates']
CHECK = json.loads((here / 'check.json').read_text()) if (here / 'check.json').exists() else {}
FIELDS = list(json.loads((here / 'fields.json').read_text())['fields'])
SCALES = (1, 1e-4, 1e4, 1e-3, 1e3, 1e-7, 1e7, 0.5, 2)  # unit conversions, and 2SD halved or 1SD doubled

same = lambda a, b: math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-12)

def numbers(pdf):
    text = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True, check=True).stdout
    return {float(n) for n in re.findall(r'\d+(?:\.\d+)?', text.replace(',', ''))}

def verdict(got, want, also, on_cert):
    if want is None and got is None: return 'right'
    if got is None: return 'missed'
    if any(w is not None and same(got, w) for w in [want, *also]): return 'right'
    # a number the certificate prints (in some unit) filed where it does not belong, against one it never prints
    return 'wrong field' if any(same(got * s, n) for s in SCALES for n in on_cert) else 'misread'

def score(certs, run):
    rows = []
    for reader in sorted(p for p in Path(run).iterdir() if p.is_dir()):
        for f in sorted(reader.glob('*.json')):
            cert, _, attempt = f.stem.partition('.')
            if cert not in KEY: continue
            data = json.loads(f.read_text())
            got = data.get('fields', data) if 'fields' in data else data
            on_cert = numbers(str(Path(certs) / cert / 'cert.pdf'))
            for field in FIELDS:
                g = None if got is None else got.get(field)
                g = float(g) if isinstance(g, (int, float)) else None
                v = verdict(g, KEY[cert]['fields'][field], KEY[cert]['also'].get(field, []), on_cert) if got is not None else 'no answer'
                fix = CHECK.get(f'{reader.name}/{f.stem}/{field}')
                if fix: v = fix['verdict']
                rows.append({'reader': reader.name, 'cert': cert, 'attempt': attempt or '1', 'field': field,
                             'got': g, 'want': KEY[cert]['fields'][field], 'verdict': v})
    (Path(run) / 'scores.json').write_text(json.dumps(rows, indent=0))
    return rows

if __name__ == '__main__':
    rows = score(*sys.argv[1:3])
    from collections import Counter
    for reader in sorted({r['reader'] for r in rows}):
        c = Counter(r['verdict'] for r in rows if r['reader'] == reader)
        print(reader, dict(c))
    for r in rows:
        if r['verdict'] != 'right': print(r)

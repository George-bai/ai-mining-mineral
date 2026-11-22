#!/usr/bin/env python3
"""Score every reader's fields against the answer key, field by field.
Usage: python3 score.py <certs dir> <run dir>  → <run dir>/scores.json
       python3 score.py test                    checks the grading of malformed answers (no PDFs needed)
<run dir>/<reader>/<cert>[.<attempt>].json holds the fields, bare (rules) or under "fields" (model).
Every reader needs every certificate of key.json, with the same attempts. An answer must hold exactly the twelve
fields, each a number or null: a missing field, a string or a boolean is 'invalid', never read as null.
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

def grade(got, cert, on_cert):
    """Verdict and value per field. got is None when the reply held no JSON ('no answer')."""
    exact = isinstance(got, dict) and set(got) == set(FIELDS)
    for field in FIELDS:
        if got is None:
            yield field, None, 'no answer'
            continue
        g = got.get(field) if exact else None
        if not exact or not (g is None or isinstance(g, (int, float)) and not isinstance(g, bool)):
            yield field, None, 'invalid'
            continue
        g = None if g is None else float(g)
        yield field, g, verdict(g, KEY[cert]['fields'][field], KEY[cert]['also'].get(field, []), on_cert)

def score(certs, run):
    rows = []
    for reader in sorted(p for p in Path(run).iterdir() if p.is_dir()):
        files = [f for f in sorted(reader.glob('*.json')) if f.stem.partition('.')[0] in KEY]
        attempts = {}
        for f in files:
            cert, _, attempt = f.stem.partition('.')
            attempts.setdefault(cert, set()).add(attempt or '1')
        if set(attempts) != set(KEY) or len({frozenset(a) for a in attempts.values()}) != 1:
            sys.exit(f'{reader.name}: incomplete run, every certificate needs the same attempts: '
                     f'{ {c: sorted(attempts.get(c, ())) for c in KEY} }')
        for f in files:
            cert, _, attempt = f.stem.partition('.')
            data = json.loads(f.read_text())
            got = data.get('fields') if isinstance(data, dict) and 'fields' in data else data
            on_cert = numbers(str(Path(certs) / cert / 'cert.pdf'))
            for field, g, v in grade(got, cert, on_cert):
                fix = CHECK.get(f'{reader.name}/{f.stem}/{field}')
                if fix: v = fix['verdict']
                rows.append({'reader': reader.name, 'cert': cert, 'attempt': attempt or '1', 'field': field,
                             'got': g, 'want': KEY[cert]['fields'][field], 'verdict': v})
    (Path(run) / 'scores.json').write_text(json.dumps(rows, indent=0))
    return rows

def selftest():
    right = lambda got, cert: sum(v == 'right' for _, _, v in grade(got, cert, set()))
    key = {c: KEY[c]['fields'] for c in KEY}
    assert sum(right(key[c], c) for c in KEY) == 84                       # the key itself: every field right
    assert sum(right({}, c) for c in KEY) == 0                            # an empty answer: nothing right (was 38)
    assert sum(right({f: '0.5' for f in FIELDS}, c) for c in KEY) == 0     # strings, even in empty fields (was 38)
    c = 'se147'
    assert dict((f, v) for f, _, v in grade({**key[c], 'au_fa_sd_ppm': True}, c, set()))['au_fa_sd_ppm'] == 'invalid'
    missing = {f: v for f, v in key[c].items() if f != 'cu_4a_pct'}
    assert {v for _, _, v in grade(missing, c, set())} == {'invalid'}       # a missing field spoils the answer
    assert {v for _, _, v in grade(None, c, set())} == {'no answer'}
    print('score.py test: the key scores 84 of 84; empty, string, boolean and incomplete answers score nothing')

if __name__ == '__main__':
    if sys.argv[1:] == ['test']:
        selftest(); sys.exit()
    rows = score(*sys.argv[1:3])
    from collections import Counter
    for reader in sorted({r['reader'] for r in rows}):
        c = Counter(r['verdict'] for r in rows if r['reader'] == reader)
        print(reader, dict(c))
    for r in rows:
        if r['verdict'] != 'right': print(r)

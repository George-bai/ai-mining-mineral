#!/usr/bin/env python3
"""The local model reads the same text layer as rules.py and fills the same fields.
Usage: [PROMPT=prompt-columns.md] python3 ask_model.py <endpoint> <model> <cert.pdf> <out.json>
PROMPT picks the instruction: prompt.md defines every field and the rules; prompt-columns.md gives the column names only.
Writes the parsed fields with the model's raw reply, its reasoning, the time and the token counts."""
import json, os, re, subprocess, sys, time, urllib.request
from pathlib import Path

here = Path(__file__).parent
spec = json.loads((here / 'fields.json').read_text())
endpoint, model, pdf, out = sys.argv[1:5]
text = subprocess.run(['pdftotext', '-layout', pdf, '-'], capture_output=True, text=True, check=True).stdout
prompt = (here / os.environ.get('PROMPT', 'prompt.md')).read_text().format(keys=', '.join(spec['fields']),
    fields='\n'.join(f'- `{k}`: {v}' for k, v in spec['fields'].items()),
    rules='\n'.join(f'- {r}' for r in spec['rules']), certificate=text)
body = {'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 32768}
start = time.time()
req = urllib.request.Request(endpoint.rstrip('/') + '/chat/completions', json.dumps(body).encode(),
                             {'Content-Type': 'application/json'})
reply = json.load(urllib.request.urlopen(req, timeout=1800))
msg = reply['choices'][0]['message']
content = msg.get('content') or ''
blocks = re.findall(r'\{[^{}]*\}', content)  # the last flat JSON object in the reply is the answer
try: fields = json.loads(blocks[-1]) if blocks else None
except json.JSONDecodeError: fields = None
Path(out).write_text(json.dumps({'fields': fields, 'content': content, 'reasoning': msg.get('reasoning'),
    'finish': reply['choices'][0].get('finish_reason'), 'usage': reply.get('usage'),
    'seconds': round(time.time() - start, 1), 'model': model}, indent=1))
print(out, round(time.time() - start, 1), 's', 'ok' if fields else 'NO JSON')

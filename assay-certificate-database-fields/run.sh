#!/usr/bin/env bash
# Every reader fills the fields from every certificate. Usage: ./run.sh <certs dir> <run dir> [attempts]
# Download first: while read id url; do mkdir -p certs/$id && curl -sSL -o certs/$id/cert.pdf "$url"; done < certificates.tsv
# ENDPOINT and MODEL name your OpenAI-compatible server (the article ran Qwen 3.8 27B on a machine on its own network).
# PROMPT=prompt-columns.md gives the model the column names only; its answers go to <run>/<model>-columns/.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd); certs=$1; run=$2; n=${3:-3}
endpoint=${ENDPOINT:-http://localhost:8000/v1}; model=${MODEL:-qwen38-27b}
reader=$model; [ "${PROMPT:-prompt.md}" = prompt.md ] || reader=$model-columns
mkdir -p "$run/rules" "$run/$reader"
while read -r id _; do
  python3 "$here/rules.py" "$certs/$id/cert.pdf" > "$run/rules/$id.json"
  for i in $(seq 1 "$n"); do  # one attempt at a time: the server is shared
    python3 "$here/ask_model.py" "$endpoint" "$model" "$certs/$id/cert.pdf" "$run/$reader/$id.$i.json"
  done
done < "$here/certificates.tsv"
python3 "$here/score.py" "$certs" "$run"

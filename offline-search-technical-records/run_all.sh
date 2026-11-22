#!/bin/bash
# One system on one collection, one repeat, in its own loopback-only namespace (offline.sh) and a fresh index.
# Usage: run_all.sh <system> <collection: focused|full> <repeat: 1|2> [questions.json]
# Needs LOCAL (models, corpus, venv, sag CLI) set; see README "Repeat it".
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
: "${LOCAL:?set LOCAL to the folder holding hf/, .venv/, sag-cli/ and corpus-*/}"
sys=$1 coll=$2 rep=$3 questions=${4:-$HERE/questions.json}
snap() { ls -d "$LOCAL"/hf/hub/models--"$1"/snapshots/*; }
py=$LOCAL/.venv/bin/python
sag=$LOCAL/sag-cli/node_modules/@zleap-ai/sag/native/linux-x64/sag
out=$LOCAL/runs/$sys/$coll/$rep
rm -rf "$out"; mkdir -p "$out"
args=(--sag "$sag" --corpus "$LOCAL/corpus-$coll" --questions "$questions" --out "$out" --label "$sys")
case $sys in
  keyword)   args+=(--modes fast) ;;
  tinybert)  args+=(--modes deep --scorer "ce:$(snap cross-encoder--ms-marco-TinyBERT-L2-v2)") ;;
  minilm)    args+=(--modes deep --scorer "ce:$(snap cross-encoder--ms-marco-MiniLM-L6-v2)") ;;
  qwen-rr)   args+=(--modes deep --scorer "qwen3rr:$(snap Qwen--Qwen3-Reranker-0.6B)") ;;
  hindsight) args+=(--modes deep --scorer "hindsight:$(snap hindsight-ai--hs-decide-1-flash)") ;;
  d1)        args+=(--modes deep --scorer "d1:$(snap LiquidAI--d1-2B)" --sag-settings '{"runtime": {"jev_context_tokens": 16000}}') ;;
  knowline)  args+=(--modes deep --scorer "proxy:http://127.0.0.1:8790/v1/systemone" \
                   --sag-settings '{"timeout_secs": 3600, "runtime": {"jev_concurrency": 1, "retry_total_secs": 14400}}') ;;
  *) echo "unknown system $sys" >&2; exit 2 ;;
esac
export HF_HOME=$LOCAL/hf
if [ "$sys" = knowline ]; then
  # KnowLine's own server inside the same namespace, on the GPU (its process peaked at 21.6 GiB here) or, with KNOWLINE_DEVICE=cpu, the
  # processor (far too slow for this protocol: see protocol.md); run.py starts once it answers
  dev=${KNOWLINE_DEVICE:-cuda}
  if [ "$dev" = cpu ]; then export CUDA_VISIBLE_DEVICES=""; else export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-2}; fi
  exec "$HERE/offline.sh" bash -c '"$1" -I "$2" --model "$3" --backend hf --device '"$dev"' --port 8790 --workers 1 > "$4/knowline.log" 2>&1 &
    server=$!
    until grep -q "systemone on" "$4/knowline.log"; do kill -0 $server 2>/dev/null || { echo "KnowLine server stopped" >&2; exit 1; }; sleep 2; done
    "$1" -I "$5/run.py" "${@:6}"; status=$?; kill $server; exit $status' x "$py" "$(snap PelaAI--KnowLine-4B-Gen5)/knowline_server.py" "$(snap PelaAI--KnowLine-4B-Gen5)" "$out" "$HERE" "${args[@]}"
fi
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-2}
exec "$HERE/offline.sh" "$py" -I "$HERE/run.py" "${args[@]}"

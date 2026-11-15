#!/usr/bin/env bash
# First test: each model reads each flowsheet through the Pi agent harness, with no skill.
# Usage: [MODELS=...] [DRAWINGS='p37*'] ./run.sh [run-name]     Output: ../local/runs/<run-name>/<model>/<flowsheet>/
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
# The cropped drawings: build them with prepare.sh, then point FIGURES at its figures/ folder.
figures=$(cd "${FIGURES:-$here/drawings/figures}" && pwd)
out=$here/../local/runs/${1:-run1}
# A clean Pi config folder, so no personal skill, setting or context file reaches the model.
# MODELS_JSON: your own copy of models.json with your endpoints (default: the example beside this script).
export PI_CODING_AGENT_DIR=$out/pi-agent
mkdir -p "$PI_CODING_AGENT_DIR" && cp "${MODELS_JSON:-$here/models.json}" "$PI_CODING_AGENT_DIR/models.json"

for model in ${MODELS:-qwen27b/qwen38-27b flashnext/qwen38-next-flash}; do
  for png in "$figures"/${DRAWINGS:-*}.png; do
    # one folder per provider and model, so two providers serving the same model name cannot overwrite each other
    dir=$out/${model//\//__}/$(basename "$png" .png)
    # Start each attempt from an empty folder, so a failed rerun cannot leave an old answer behind.
    rm -rf "$dir" && mkdir -p "$dir" && cd "$dir" && cp "$png" flowsheet.png
    start=$(date +%s)
    # stdin is closed: with an open pipe Pi waits for piped input and never starts.
    timeout 900 pi -p --mode json --model "$model" --no-session --no-skills --no-context-files \
      --no-extensions -e "$here/image-limit.ts" --no-prompt-templates --no-mcp --offline \
      @flowsheet.png "$(cat "$here/prompt.md")" < /dev/null > events.jsonl 2> stderr.txt || echo "exit $?" >> stderr.txt
    echo "$(( $(date +%s) - start ))" > seconds.txt
    echo "$dir: $(cat seconds.txt) s, $( [ -f flowsheet.mmd ] && wc -l < flowsheet.mmd || echo no ) lines"
  done
done

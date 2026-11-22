#!/usr/bin/env bash
# Each model answers prompt.md through the Pi agent harness, with its shell (so it can run Python), and no skill.
# Usage: [MODELS=...] [REPEATS=10 | REPS="6 7 8"] ./run.sh <run-name>
# Output: ../local/runs/<run-name>/<provider__model>/<repeat>/  (events.jsonl, stderr.txt, seconds.txt); then collect.py
# No time limit: an attempt runs until the model stops.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out=$here/../local/runs/${1:?run name}
# Hidden from the model: the clone this script sits in (check.py, the results, the article, earlier attempts), wherever
# it is, and the author's own folders where they exist.
root=$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || dirname "$here")
hide=()
for d in "$root" "$HOME/git" "$HOME/.claude" "$HOME/.codex"; do [ -e "$d" ] && hide+=(--tmpfs "$d"); done
# A clean Pi config folder, so no personal skill, setting or context file reaches the model.
# MODELS_JSON: your own copy of models.json with your endpoints (default: the example beside this script).
export PI_CODING_AGENT_DIR=$out/pi-agent
mkdir -p "$PI_CODING_AGENT_DIR" && cp "${MODELS_JSON:-$here/models.json}" "$PI_CODING_AGENT_DIR/models.json"
cp "$here/prompt.md" "$out/prompt-used.md"

for model in ${MODELS:-qwen27b/qwen38-27b flashnext/qwen38-next-flash}; do
  for rep in ${REPS:-$(seq 1 "${REPEATS:-10}")}; do   # REPS="6 7": run only those attempts, keeping the others
    dir=$out/${model//\//__}/$rep
    # Start from an empty folder, so a failed rerun cannot leave an old answer behind.
    rm -rf "$dir" && mkdir -p "$dir"
    # Fenced in (bubblewrap): its own /tmp, the clone out of sight, the rest read-only, so the model can read neither
    # the answer nor another attempt. Visible inside the clone: only this attempt's empty folder and Pi's config.
    fence=(bwrap --ro-bind / / --dev-bind /dev /dev --proc /proc --tmpfs /tmp "${hide[@]}"
      --bind "$dir" "$dir" --bind "$PI_CODING_AGENT_DIR" "$PI_CODING_AGENT_DIR" --chdir "$dir")
    start=$(date +%s)
    # stdin is closed: with an open pipe Pi waits for piped input and never starts.
    "${fence[@]}" pi -p --mode json --model "$model" --no-session --no-skills --no-context-files \
      --no-extensions --no-prompt-templates --no-mcp --offline \
      "$(cat "$here/prompt.md")" < /dev/null > "$dir/events.jsonl" 2> "$dir/stderr.txt" || echo "exit $?" >> "$dir/stderr.txt"
    echo "$(( $(date +%s) - start ))" > "$dir/seconds.txt"
    echo "$dir: $(cat "$dir/seconds.txt") s"
  done
done

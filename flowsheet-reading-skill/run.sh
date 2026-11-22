#!/usr/bin/env bash
# Each model reads each drawing through the Pi agent harness, with the flowsheet-reading skill or without it.
# Usage: [SKILL=flowsheet-reading] [MODELS=...] [REPEATS=3 | REP=n] [JOBS=1] ./run.sh <run-name> <drawing.png>...
#   REP     run only repeat number n (interleave.sh uses it)
#   SKILL   the skill folder to load; leave it out to run with no skill
#   JOBS    attempts at once per model (each model has its own queue)
# Output: ../local/runs/<run-name>/<provider__model>/<drawing>/<repeat>/  (flowsheet.mmd, events.jsonl, seconds.txt)
# No time limit: an attempt runs until the model stops.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
run=$1; shift
out=$here/../local/runs/$run
# A clean Pi config folder, so no personal skill, setting or context file reaches the model.
export PI_CODING_AGENT_DIR=$out/pi-agent
mkdir -p "$PI_CODING_AGENT_DIR" && cp "${MODELS_JSON:-$here/models.json}" "$PI_CODING_AGENT_DIR/models.json"
skill=${SKILL:+$(cd "$SKILL" && pwd)}
[ -n "$skill" ] && [ ! -d "$out/skill-used" ] && cp -r "$skill" "$out/skill-used"   # keep the exact skill each run used
export here out skill

attempt() {   # <model> <drawing.png> <repeat>
  local dir=$out/${1//\//__}/$(basename "$2" .png)/$3
  # Start from an empty folder, so a failed rerun cannot leave an old answer behind.
  rm -rf "$dir" && mkdir -p "$dir" && cd "$dir" && cp "$2" flowsheet.png
  local prompt skills=(--no-skills)
  prompt=$(cat "$here/prompt.md")
  if [ -n "$skill" ]; then skills+=(--skill "$skill"); prompt="/skill:flowsheet-reading $prompt"; fi
  local start=$(date +%s)
  # Each attempt runs fenced in (bubblewrap): its own /tmp, the repositories and other runs out of sight, home
  # read-only, so a model can neither read the answer keys nor see another attempt's crops nor install anything.
  # The folder above this one is hidden whole: in the public repository that is the repository itself, with this
  # folder's reference/, results/ and README.md. Shown again: the two extensions and, with the skill, the skill folder,
  # read-only; this attempt's folder and Pi's config, writable. The model endpoints stay reachable.
  local fence=(bwrap --ro-bind / / --dev-bind /dev /dev --proc /proc --tmpfs /tmp
    --tmpfs "$HOME/git" --tmpfs "$HOME/.claude" --tmpfs "$HOME/.codex" --tmpfs "$(cd "$here/.." && pwd)"
    --bind "$dir" "$dir" --bind "$PI_CODING_AGENT_DIR" "$PI_CODING_AGENT_DIR"
    --ro-bind "$here/image-limit.ts" "$here/image-limit.ts" --ro-bind "$here/loop-guard.ts" "$here/loop-guard.ts")
  [ -n "$skill" ] && fence+=(--ro-bind "$skill" "$skill")
  fence+=(--chdir "$dir")
  # stdin is closed: with an open pipe Pi waits for piped input and never starts.
  # If a run ends with no chart (stopped by a guard, or the model gave up), it is started once more in the same
  # folder with the same prompt and a fresh context; its events go to events-2.jsonl and restart.txt records it.
  local n
  for n in 1 2; do
    local ev=events.jsonl err=stderr.txt
    [ "$n" = 2 ] && { [ -f flowsheet.mmd ] && break; ev=events-2.jsonl err=stderr-2.txt; echo "restarted after $(( $(date +%s) - start )) s" > restart.txt; }
    "${fence[@]}" pi -p --mode json --model "$1" --no-session "${skills[@]}" --no-context-files \
      --no-extensions -e "$here/image-limit.ts" -e "$here/loop-guard.ts" --no-prompt-templates --no-mcp --offline \
      @flowsheet.png "$prompt" < /dev/null > "$ev" 2> "$err" || echo "exit $?" >> "$err"
  done
  echo "$(( $(date +%s) - start ))" > seconds.txt
  echo "$dir: $(cat seconds.txt) s, $( [ -f flowsheet.mmd ] && wc -l < flowsheet.mmd || echo no ) lines$( [ -f restart.txt ] && echo ', restarted' )"
}
export -f attempt

for model in ${MODELS:-qwen27b/qwen38-27b flashnext/qwen38-next-flash}; do
  for rep in ${REP:-$(seq 1 "${REPEATS:-1}")}; do for png in "$@"; do echo "$model $(realpath "$png") $rep"; done; done \
    | xargs -P "${JOBS:-1}" -L1 bash -c 'attempt "$@"' _ &
done
wait

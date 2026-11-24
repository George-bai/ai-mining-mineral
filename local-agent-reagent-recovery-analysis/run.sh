#!/usr/bin/env bash
# No. 4: the two questions to the local 27B model in Pi, one after the other in one session (the second follows up
# the first), with No. 2's historian MCP server and skill. A fresh session per repeat.
# Usage: REPEATS=3 ./run.sh <run-name> [conversation ids...]
# Needs: the mock historian on :8711 (No. 2: MOCK_SITES=31 MOCK_CONCENTRATORS=5 uvicorn mock_api:app --port 8711),
# No. 2's catalogue crawled, and the model server on :8088. Starts No. 2's MCP server over HTTP on :${MCP_PORT:-8713} itself.
# Output: ../local/runs/<run-name>/<id>/<repeat>/  (events.jsonl, answer.md, any chart, seconds.txt)
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
# No. 18: articles/<slug>/public in our repository, <slug> in the public one
pub=$(cd "$here/../../historian-tag-catalogue-for-agents/public" 2>/dev/null || cd "$here/../historian-tag-catalogue-for-agents" && pwd)
run=$1; shift
qfile=${QUESTIONS:-$here/questions.yaml}   # a list of conversations: id, turns
qfile=$(cd "$(dirname "$qfile")" && pwd)/$(basename "$qfile")
out=$here/../local/runs/$run
mkdir -p "$out"
out=$(cd "$out" && pwd)
env=${AGENT_ENV:-$here/../../local-agent-finds-historian-tags/local/agent-env}   # the agent's Python: pandas, numpy, matplotlib, scipy
[ -d "$env" ] || { echo "Set AGENT_ENV to a Python environment with pandas, numpy, matplotlib and scipy (README, Run it)." >&2; exit 1; }
env=$(cd "$env" && pwd)
data=$out/datasets && mkdir -p "$data"

# No. 2's MCP server over HTTP with its key; its dataset files go to this run's folder, which the agent may read
export MCP_API_KEY=$(head -c 18 /dev/urandom | base64 | tr -d '/+=')
DATASETS=$data AUDIT_LOG=$out/audit.jsonl "$pub/.venv/bin/python" "$pub/mcp_server.py" --http --port ${MCP_PORT:-8713} > "$out/mcp.log" 2>&1 &
mcp=$!
trap 'kill $mcp 2>/dev/null' EXIT
for i in $(seq 1 30); do curl -s -o /dev/null -m 1 http://127.0.0.1:${MCP_PORT:-8713}/mcp && break; sleep 1; done

# A clean Pi config folder: the model, the one MCP server, nothing personal
export PI_CODING_AGENT_DIR=$out/pi-agent
mkdir -p "$PI_CODING_AGENT_DIR" && cp "$here/models.json" "$PI_CODING_AGENT_DIR/models.json"
pi mcp add historian --exposure direct --description "The plant historian: tag catalogue search and time-series reads" \
  --url http://127.0.0.1:${MCP_PORT:-8713}/mcp --header "x-api-key=$MCP_API_KEY" > /dev/null
[ -d "$out/skill-used" ] || cp -r "$pub/skill/historian-tags" "$out/skill-used"
skill=$out/skill-used
# KIT=1: the labelled second run (README, Two runs; 23 Nov 2026 evening): No. 21's plant knowledge page and analytical skill added
extra=() && kit=$out/condition && mkdir -p "$kit"
if [ "${KIT:-}" = 1 ]; then
  n5=$(cd "$here/../../teaching-local-agent-site-analysis/public" 2>/dev/null || cd "$here/../teaching-local-agent-site-analysis" && pwd)
  cp "$n5/plant-knowledge/site-a-concentrator-1.md" "$kit/plant-knowledge.md"
  [ -d "$kit/site-analysis" ] || cp -r "${SKILLS_DIR:-$n5/../skills}/site-analysis" "$kit/site-analysis"
  printf '%s\n' "For any calculation, KPI, period average or relationship between plant variables, read and follow the site-analysis skill first." > "$kit/use-skill.md"
  extra+=(--append-system-prompt "$kit/plant-knowledge.md" --skill "$kit/site-analysis" --append-system-prompt "$kit/use-skill.md")
fi

ids=${*:-$(python3 -c "import yaml;print(' '.join(q['id'] for q in yaml.safe_load(open('$qfile'))))")}
# What the agent must not see: this repository, wherever it was cloned (the keys, the scripts, other attempts' answers), and
# the agent tools' own folders. Checked before the first attempt: a fence that leaves the key readable stops the run.
root=$(git -C "$here" rev-parse --show-toplevel 2>/dev/null || (cd "$here/.." && pwd))
hide=(--tmpfs "$HOME/git" --tmpfs "$HOME/.claude" --tmpfs "$HOME/.codex" --tmpfs "$root")
if bwrap --ro-bind / / --dev-bind /dev /dev --proc /proc --tmpfs /tmp "${hide[@]}" test -e "$here/key.json"; then
  echo "The fence leaves $here/key.json readable: not running." >&2; exit 1
fi
for rep in $(seq 1 "${REPEATS:-1}"); do
  for id in $ids; do
    dir=$out/$id/$rep
    rm -rf "$dir" && mkdir -p "$dir" && cd "$dir"
    n=$(python3 -c "import yaml;print(len(next(q['turns'] for q in yaml.safe_load(open('$qfile')) if q['id']=='$id')))")
    fence=(bwrap --ro-bind / / --dev-bind /dev /dev --proc /proc --tmpfs /tmp
      "${hide[@]}"
      --bind "$dir" "$dir" --bind "$PI_CODING_AGENT_DIR" "$PI_CODING_AGENT_DIR"
      --ro-bind "$data" "$data" --ro-bind "$env" "$env" --ro-bind "$skill" "$skill" --ro-bind "$kit" "$kit" --chdir "$dir")
    for turn in $(seq 1 "$n"); do
      text=$(python3 -c "import yaml;print(next(q['turns'] for q in yaml.safe_load(open('$qfile')) if q['id']=='$id')[$turn-1])")
      if [ "$turn" = 1 ]; then prompt="/skill:historian-tags $text

$(cat "$here/prompt.md")"; cont=(); else prompt=$text; cont=(--continue); fi
      start=$(date +%s.%N)
      PATH=$env/bin:$PATH timeout "${LIMIT:-1800}" "${fence[@]}" pi -p --mode json --model qwen27b/qwen38-27b \
        --session-dir "$dir/session" "${cont[@]}" --no-skills --skill "$skill" "${extra[@]}" --no-context-files --no-prompt-templates \
        --offline "$prompt" < /dev/null > events-$turn.jsonl 2> stderr-$turn.txt || echo "exit $?" >> stderr-$turn.txt
      python3 -c "print(round($(date +%s.%N) - $start, 1))" > seconds-$turn.txt
      python3 "$here/answer.py" events-$turn.jsonl > answer-$turn.md || true
    done
    echo "$id/$rep: $(cat seconds-*.txt | tr '\n' ' ') s, $(ls *.png 2>/dev/null | wc -l) png"
  done
done

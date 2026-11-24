#!/usr/bin/env bash
# No. 5: each question to the local 27B model in Pi with No. 2's historian MCP server and skill, in a fresh session,
# under one of three conditions:
#   bare       as No. 4, without the sentence saying how recovery is calculated
#   knowledge  plus the plant knowledge (plant-knowledge/site-a-concentrator-1.md) appended to the system prompt
#   skills     plus the analytical skill site-analysis (not published; SKILLS_DIR points at it) and one line saying to use it
# Usage: CONDITION=bare|knowledge|skills REPEATS=3 ./run.sh <run-name> [question ids...]
# Needs: the mock historian on :8711 (No. 2: MOCK_SITES=31 MOCK_CONCENTRATORS=5 uvicorn mock_api:app --port 8711),
# No. 2's catalogue crawled, and the model server on :8088. Starts No. 2's MCP server over HTTP on :${MCP_PORT:-8714} itself.
# Output: ../local/runs/<run-name>/<id>/<repeat>/  (events.jsonl, answer.md, any chart, seconds.txt)
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
# No. 18: articles/<slug>/public in our repository, <slug> in the public one
pub=$(cd "$here/../../historian-tag-catalogue-for-agents/public" 2>/dev/null || cd "$here/../historian-tag-catalogue-for-agents" && pwd)
run=$1; shift
qfile=${QUESTIONS:-$here/questions.yaml}   # harness checks: QUESTIONS=dev.yaml
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
DATASETS=$data AUDIT_LOG=$out/audit.jsonl "$pub/.venv/bin/python" "$pub/mcp_server.py" --http --port ${MCP_PORT:-8714} > "$out/mcp.log" 2>&1 &
mcp=$!
trap 'kill $mcp 2>/dev/null' EXIT
for i in $(seq 1 30); do curl -s -o /dev/null -m 1 http://127.0.0.1:${MCP_PORT:-8714}/mcp && break; sleep 1; done

# A clean Pi config folder: the model, the one MCP server, nothing personal
export PI_CODING_AGENT_DIR=$out/pi-agent
mkdir -p "$PI_CODING_AGENT_DIR" && cp "$here/models.json" "$PI_CODING_AGENT_DIR/models.json"
pi mcp add historian --exposure direct --description "The plant historian: tag catalogue search and time-series reads" \
  --url http://127.0.0.1:${MCP_PORT:-8714}/mcp --header "x-api-key=$MCP_API_KEY" > /dev/null
[ -d "$out/skill-used" ] || cp -r "$pub/skill/historian-tags" "$out/skill-used"
skill=$out/skill-used
cond=${CONDITION:?set CONDITION=bare, knowledge or skills}
extra=() && kit=$out/condition && mkdir -p "$kit"   # what this condition adds, visible read-only to the agent
if [ "$cond" != bare ]; then
  cp "$here/plant-knowledge/site-a-concentrator-1.md" "$kit/plant-knowledge.md"
  extra+=(--append-system-prompt "$kit/plant-knowledge.md")
fi
if [ "$cond" = skills ]; then
  [ -d "$kit/site-analysis" ] || cp -r "${SKILLS_DIR:-$here/../skills}/site-analysis" "$kit/site-analysis"
  printf '%s\n' "For any calculation, KPI, period average or relationship between plant variables, read and follow the site-analysis skill first." > "$kit/use-skill.md"
  extra+=(--skill "$kit/site-analysis" --append-system-prompt "$kit/use-skill.md")
fi

ids=${*:-$(python3 -c "import yaml;print(' '.join(q['id'] for q in yaml.safe_load(open('$qfile'))))")}
for rep in $(seq 1 "${REPEATS:-1}"); do
  for id in $ids; do
    dir=$out/$id/$rep
    rm -rf "$dir" && mkdir -p "$dir" && cd "$dir"
    question=$(python3 -c "import yaml;print(next(q['question'] for q in yaml.safe_load(open('$qfile')) if q['id']=='$id'))")
    prompt="/skill:historian-tags $question

$(cat "$here/prompt.md")"
    # Fenced in (bubblewrap): the repositories, keys and other runs out of sight; this attempt's folder writable;
    # the run's dataset files, the agent's Python and the skill read-only. The model and MCP endpoints stay reachable.
    fence=(bwrap --ro-bind / / --dev-bind /dev /dev --proc /proc --tmpfs /tmp
      --tmpfs "$HOME/git" --tmpfs "$HOME/.claude" --tmpfs "$HOME/.codex"
      --bind "$dir" "$dir" --bind "$PI_CODING_AGENT_DIR" "$PI_CODING_AGENT_DIR"
      --ro-bind "$data" "$data" --ro-bind "$env" "$env" --ro-bind "$skill" "$skill" --ro-bind "$kit" "$kit" --chdir "$dir")
    start=$(date +%s.%N)
    PATH=$env/bin:$PATH timeout "${LIMIT:-900}" "${fence[@]}" pi -p --mode json --model qwen27b/qwen38-27b --no-session \
      --no-skills --skill "$skill" "${extra[@]}" --no-context-files --no-prompt-templates --offline \
      "$prompt" < /dev/null > events.jsonl 2> stderr.txt || echo "exit $?" >> stderr.txt
    python3 -c "print(round($(date +%s.%N) - $start, 1))" > seconds.txt
    python3 "$here/answer.py" events.jsonl > answer.md || true
    echo "$id/$rep: $(cat seconds.txt) s, $(ls *.png 2>/dev/null | wc -l) png"
  done
done

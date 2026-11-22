#!/usr/bin/env bash
# Each model reads each drawing through Hermes Agent, with the flowsheet-reading skill or without it: the same drawings,
# prompt, skill, models, windows and restart rule as ../run.sh (Pi); only the harness differs.
# Usage: [SKILL=../flowsheet-reading] [MODELS=...] [REPEATS=2 | REP=n] [JOBS=1] ./run.sh <run-name> <drawing.png>...
# Needs ./fence.sh up first. Output: ../../local/runs/<run-name>/<provider__model>/<drawing>/<repeat>/
#   (flowsheet.mmd, stdout.txt: Hermes's final reply, seconds.txt); each attempt's Hermes home, with its session, beside it.
# Each attempt runs in a fresh container of the pinned image, on a Docker network with no route out but the proxy:
# it sees only its own folder (as /work), its own Hermes home and, with the skill, the skill folder (read-only).
# No time limit: an attempt runs until the model stops (Hermes's own limit is 500 tool calls a turn).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
run=$1; shift
out=$here/../../local/runs/$run
IMAGE=nousresearch/hermes-agent@sha256:adb7890916de63245523492be8f68f9d2095fecbec4e2a6dab7960381f0fc002   # v0.23.0
skill=${SKILL:+$(cd "$SKILL" && pwd)}
mkdir -p "$out"
[ -n "$skill" ] && [ ! -d "$out/skill-used" ] && cp -r "$skill" "$out/skill-used"   # keep the exact skill each run used
export here out run skill IMAGE CONFIG

attempt() {   # <model> <drawing.png> <repeat>
  local m=$1 port ctx d=$(basename "$2" .png)
  case $m in
    qwen27b/qwen38-27b) port=18001 ctx=96000 ;;
    flashnext/qwen38-next-flash) port=18002 ctx=262144 ;;
    *) echo "unknown model $m" >&2; return 1 ;;
  esac
  local dir=$out/${m//\//__}/$d/$3 home=$out/hermes-home/${m//\//__}/$d/$3
  # Start from empty folders, so a failed rerun cannot leave an old answer behind.
  rm -rf "$dir" "$home" && mkdir -p "$dir" "$home/home" && cp "$2" "$dir/flowsheet.png"
  touch "$home/.no-bundled-skills"   # no stock Hermes skills: only the one given (Pi: --no-skills)
  touch "$home/prompt.md"; [ -n "$skill" ] && mkdir -p "$home/skills/flowsheet-reading"   # mount points made by us, not by Docker as root
  chmod 700 "$home"                   # Hermes refuses a home others can write to
  sed -e "s|@MODEL@|${m#*/}|; s|@PORT@|$port|; s|@CONTEXT@|$ctx|" "${CONFIG:-$here/config.yaml.in}" > "$home/config.yaml"   # CONFIG: smoke tests only
  local mounts=(-v "$dir:/work" -v "$home:/opt/data" -v "$here/../prompt.md:/opt/data/prompt.md:ro") skills=()
  if [ -n "$skill" ]; then mounts+=(-v "$skill:/opt/data/skills/flowsheet-reading:ro"); skills=(-s flowsheet-reading); fi
  local start=$(date +%s) n
  # The image lets Hermes's file tools write only under /opt/data (HERMES_WRITE_SAFE_ROOT); /work is added, since the prompt
  # asks for the chart in the current directory (the first Hermes run, without it, is in development.md).
  # If a run ends with no chart, it is started once more in the same folder with the same prompt and a fresh session;
  # its reply goes to stdout-2.txt and restart.txt records it (as ../run.sh).
  for n in 1 2; do
    local ev=stdout.txt err=stderr.txt
    [ "$n" = 2 ] && { [ -f "$dir/flowsheet.mmd" ] && break; ev=stdout-2.txt err=stderr-2.txt; echo "restarted after $(( $(date +%s) - start )) s" > "$dir/restart.txt"; }
    docker run --rm --init --name "fsr-$run-${m#*/}-$d-$3-$n" --label fsr=1 --network fsr-fence --user "$(id -u):$(id -g)" \
      -e HERMES_HOME=/opt/data -e HOME=/opt/data/home -e HERMES_WRITE_SAFE_ROOT=/opt/data:/work "${mounts[@]}" -w /work --entrypoint hermes "$IMAGE" \
      chat --query-file /opt/data/prompt.md --image /work/flowsheet.png -Q \
      -t terminal,file,vision "${skills[@]}" --yolo --source tool \
      < /dev/null > "$dir/$ev" 2> "$dir/$err" || echo "exit $?" >> "$dir/$err"
  done
  echo "$(( $(date +%s) - start ))" > "$dir/seconds.txt"
  # The record of the run: every session of this attempt's Hermes home (one, two after a restart), as JSON lines.
  docker run --rm --init --network none --user "$(id -u):$(id -g)" -e HERMES_HOME=/opt/data -e HOME=/opt/data/home \
    -v "$home:/opt/data" --entrypoint hermes "$IMAGE" sessions export --format jsonl --yes /opt/data/session.jsonl \
    > /dev/null 2>> "$dir/stderr.txt" && cp "$home/session.jsonl" "$dir/session.jsonl" || echo "session export failed" >> "$dir/stderr.txt"
  echo "$dir: $(cat "$dir/seconds.txt") s, $( [ -f "$dir/flowsheet.mmd" ] && wc -l < "$dir/flowsheet.mmd" || echo no ) lines$( [ -f "$dir/restart.txt" ] && echo ', restarted' )"
}
export -f attempt

for model in ${MODELS:-qwen27b/qwen38-27b flashnext/qwen38-next-flash}; do
  for rep in ${REP:-$(seq 1 "${REPEATS:-2}")}; do for png in "$@"; do echo "$model $(realpath "$png") $rep"; done; done \
    | xargs -P "${JOBS:-1}" -L1 bash -c 'attempt "$@"' _ &
done
wait

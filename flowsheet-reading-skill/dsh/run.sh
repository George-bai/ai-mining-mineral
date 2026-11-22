#!/usr/bin/env bash
# Each model reads each drawing through DeepSeek Harness (dsh), with the flowsheet-reading skill or without it: the same
# drawings, prompt, skill, models, windows, fence, proxy and restart rule as ../hermes/run.sh; only the harness differs.
# Usage: [SKILL=../flowsheet-reading] [MODELS=...] [REPEATS=2 | REP=n] [JOBS=1] ./run.sh <run-name> <drawing.png>...
# Needs ../hermes/fence.sh up first. Output: ../../local/runs/<run-name>/<provider__model>/<drawing>/<repeat>/
#   (flowsheet.mmd, events.jsonl: every message dsh sent, seconds.txt); each attempt's dsh home, with its session, beside it.
# Each attempt runs in a fresh container on the Docker network with no route out but the proxy: it sees only its own folder
# (as /work), its own dsh home, dsh itself (read-only) and, with the skill, the skill folder (read-only).
# The container is the Hermes runs' image, used only as a runtime: its Node 26.12.1 runs dsh, and its Python 3.14.9 and
# Pillow 13.0.0 run the skill's scripts, as in the Hermes runs. Hermes itself is not started.
# No time limit: an attempt runs until the model stops.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
run=$1; shift
out=$here/../../local/runs/$run
IMAGE=nousresearch/hermes-agent@sha256:adb7890916de63245523492be8f68f9d2095fecbec4e2a6dab7960381f0fc002
DSH=${DSH:-$HOME/.npm-global/lib/node_modules/@deepseek-ai/dsh}
[ "$(node -p "require('$DSH/package.json').version")" = 0.2.2-rc.5 ] || { echo "dsh is not 0.2.2-rc.5" >&2; exit 1; }
skill=${SKILL:+$(cd "$SKILL" && pwd)}
mkdir -p "$out"
[ -n "$skill" ] && [ ! -d "$out/skill-used" ] && cp -r "$skill" "$out/skill-used"   # keep the exact skill each run used
export here out run skill IMAGE DSH PATCH

attempt() {   # <model> <drawing.png> <repeat>
  local m=$1 port ctx d=$(basename "$2" .png)
  case $m in
    qwen27b/qwen38-27b) port=18001 ctx=96000 ;;
    flashnext/qwen38-next-flash) port=18002 ctx=262144 ;;
    *) echo "unknown model $m" >&2; return 1 ;;
  esac
  local dir=$out/${m//\//__}/$d/$3 home=$out/dsh-home/${m//\//__}/$d/$3
  # Start from empty folders, so a failed rerun cannot leave an old answer behind.
  rm -rf "$dir" "$home" && mkdir -p "$dir" "$home/home" && cp "$2" "$dir/flowsheet.png"
  local dirs='[]' skillname=() mounts=(-v "$dir:/work" -v "$home:/opt/data" -v "$DSH:/opt/dsh:ro"
    -v "$here/driver.mjs:/opt/driver.mjs:ro" -v "$here/../prompt.md:/opt/prompt.md:ro")
  if [ -n "$skill" ]; then
    dirs='["/opt/skills"]' skillname=(flowsheet-reading)
    mounts+=(-v "$skill:/opt/skills/flowsheet-reading:ro")
  fi
  sed -e "s|@MODEL@|${m#*/}|; s|@PORT@|$port|; s|@CONTEXT@|$ctx|; s|@SKILLDIRS@|$dirs|" "${PATCH:-$here/patch.yml.in}" \
    > "$home/patch.yml"   # PATCH: smoke tests only
  local start=$(date +%s) n
  # If a run ends with no chart, it is started once more in the same folder with the same prompt and a fresh session;
  # its record goes to events-2.jsonl and restart.txt records it (as ../run.sh).
  for n in 1 2; do
    local ev=events.jsonl err=stderr.txt
    [ "$n" = 2 ] && { [ -f "$dir/flowsheet.mmd" ] && break; ev=events-2.jsonl err=stderr-2.txt; echo "restarted after $(( $(date +%s) - start )) s" > "$dir/restart.txt"; }
    # danger-full-access: no file sandbox and no approvals, as Hermes's --yolo; the container is the fence.
    docker run --rm --init --name "fsr-$run-${m#*/}-$d-$3-$n" --label fsr=1 --network fsr-fence --user "$(id -u):$(id -g)" \
      -e HOME=/opt/data/home -e DSH_HOME=/opt/data -e DSH_PERMISSION_MODE=danger-full-access -e DSH_TELEMETRY_DISABLED=1 \
      -e FENCE_API_KEY=none "${mounts[@]}" -w /work --entrypoint node "$IMAGE" \
      /opt/driver.mjs "${m#*/}" /opt/prompt.md flowsheet.png "attempt-$n" "${skillname[@]}" \
      < /dev/null > "$dir/$ev" 2> "$dir/$err" || echo "exit $?" >> "$dir/$err"
  done
  echo "$(( $(date +%s) - start ))" > "$dir/seconds.txt"
  echo "$dir: $(cat "$dir/seconds.txt") s, $( [ -f "$dir/flowsheet.mmd" ] && wc -l < "$dir/flowsheet.mmd" || echo no ) lines$( [ -f "$dir/restart.txt" ] && echo ', restarted' )"
}
export -f attempt

for model in ${MODELS:-qwen27b/qwen38-27b flashnext/qwen38-next-flash}; do
  for rep in ${REP:-$(seq 1 "${REPEATS:-2}")}; do for png in "$@"; do echo "$model $(realpath "$png") $rep"; done; done \
    | xargs -P "${JOBS:-1}" -L1 bash -c 'attempt "$@"' _ &
done
wait

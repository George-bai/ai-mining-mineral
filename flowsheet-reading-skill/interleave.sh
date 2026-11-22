#!/usr/bin/env bash
# Runs the attempts with the conditions interleaved: for each repeat and each drawing, every condition in turn, so that
# any drift in a model server falls on all conditions alike. Each attempt goes through run.sh.
# Usage: [MODELS=provider/model] [REPEATS=3] [JOBS=1] ./interleave.sh <run-prefix> <condition>... -- <drawing.png>...
#   condition  noskill, or a skill folder; its runs go to ../local/runs/<run-prefix>-<noskill | folder name>/
#   JOBS       attempts at once (they start in the interleaved order)
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
prefix=$1; shift
conds=()
while [ "$1" != -- ]; do
  if [ "$1" = noskill ]; then conds+=(noskill); else conds+=("$(cd "$1" && pwd)"); fi
  shift
done
shift
export here prefix
for rep in $(seq 1 "${REPEATS:-3}"); do for png in "$@"; do for c in "${conds[@]}"; do
  echo "$rep $(realpath "$png") $c"
done; done; done | xargs -P "${JOBS:-1}" -L1 bash -c '
  rep=$1 png=$2 c=$3
  if [ "$c" = noskill ]; then name=noskill; unset SKILL; else name=$(basename "$c"); export SKILL=$c; fi
  REP=$rep JOBS=1 "$here/run.sh" "$prefix-$name" "$png"' _

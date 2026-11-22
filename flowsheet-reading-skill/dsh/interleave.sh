#!/usr/bin/env bash
# As ../hermes/interleave.sh, for the DeepSeek Harness (dsh) runs: for each repeat and each drawing, every condition in
# turn, so that any drift in a model server falls on all conditions alike. Each attempt goes through ./run.sh. Two repeats.
# Usage: [MODELS=provider/model] [REPEATS=2] [JOBS=1] ./interleave.sh <run-prefix> <condition>... -- <drawing.png>...
#   condition  noskill, or a skill folder; its runs go to ../../local/runs/<run-prefix>-<noskill | folder name>/
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
for rep in $(seq 1 "${REPEATS:-2}"); do for png in "$@"; do for c in "${conds[@]}"; do
  echo "$rep $(realpath "$png") $c"
done; done; done | xargs -P "${JOBS:-1}" -L1 bash -c '
  rep=$1 png=$2 c=$3
  if [ "$c" = noskill ]; then name=noskill; unset SKILL; else name=$(basename "$c"); export SKILL=$c; fi
  REP=$rep JOBS=1 "$here/run.sh" "$prefix-$name" "$png"' _

#!/bin/bash
# Every planned run, one after another so the timings are not shared: keyword and the five GPU systems, each collection
# twice from a fresh index; then KnowLine on the GPU (REPS_KNOWLINE repeats, default 2). Logs to $LOCAL/runs/log.txt.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
: "${LOCAL:?set LOCAL}"
mkdir -p "$LOCAL/runs"
log=$LOCAL/runs/log.txt
failed=0
for sys in keyword tinybert minilm qwen-rr hindsight d1; do
  for coll in full focused; do
    for rep in 1 2; do
      echo "$(date '+%F %T %Z') start $sys $coll $rep" >> "$log"
      "$HERE/run_all.sh" "$sys" "$coll" "$rep" > "$LOCAL/runs/$sys-$coll-$rep.out" 2>&1 || { echo "FAILED $sys $coll $rep" >> "$log"; failed=$((failed + 1)); }
    done
  done
done
for rep in $(seq 1 "${REPS_KNOWLINE:-2}"); do
  for coll in full focused; do
    echo "$(date '+%F %T %Z') start knowline $coll $rep" >> "$log"
    "$HERE/run_all.sh" knowline "$coll" "$rep" > "$LOCAL/runs/knowline-$coll-$rep.out" 2>&1 || { echo "FAILED knowline $coll $rep" >> "$log"; failed=$((failed + 1)); }
  done
done
echo "$(date '+%F %T %Z') all done, $failed failed" >> "$log"
[ "$failed" -eq 0 ] || { echo "$failed runs failed: see $log" >&2; exit 1; }

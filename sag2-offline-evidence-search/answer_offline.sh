#!/bin/bash
# Runs answer.py with no network but loopback, the model server on this machine reached through one Unix socket:
# outside, socat joins the socket to the server's port; inside the namespace, socat offers the socket on 127.0.0.1.
# Usage: answer_offline.sh <python> <socket path> <model port> <answer.py arguments...>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
py=$1 sock=$2 port=$3; shift 3
rm -f "$sock"
socat UNIX-LISTEN:"$sock",fork TCP:127.0.0.1:"$port" & bridge=$!
trap 'kill $bridge 2>/dev/null; rm -f "$sock"' EXIT
"$HERE/offline.sh" bash -c 'socat TCP-LISTEN:"$2",bind=127.0.0.1,fork,reuseaddr UNIX-CONNECT:"$1" & sleep 1
  "$3" -I "$4/answer.py" "${@:5}" --url "http://127.0.0.1:$2/v1/chat/completions"' x "$sock" "$port" "$py" "$HERE" "$@"

#!/usr/bin/env bash
# The fence for the Hermes runs: a Docker network with no route out (fsr-fence) and the proxy, the one container on both
# that network and the ordinary bridge, forwarding port 18001 to the 27B's server and 18002 to Flash Next's.
# Usage: ./fence.sh up <proxy-log.jsonl> [<dump folder>] | ./fence.sh down | ./fence.sh check
# UP27B and UPFLASH name the two servers as host:port (the article ran Flash Next on a second machine on its own network).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
IMAGE=nousresearch/hermes-agent@sha256:adb7890916de63245523492be8f68f9d2095fecbec4e2a6dab7960381f0fc002
UP27B=${UP27B:-host.docker.internal:8088} UPFLASH=${UPFLASH:-host.docker.internal:8089}
case $1 in
  up)
    log=$(realpath "$2"); mkdir -p "$(dirname "$log")"; touch "$log"
    docker network inspect fsr-fence >/dev/null 2>&1 || docker network create --internal fsr-fence >/dev/null
    dump=() ; [ -n "${3:-}" ] && { mkdir -p "$3"; dump=(-e DUMP=/dump -v "$(realpath "$3"):/dump"); }
    docker rm -f fsr-proxy >/dev/null 2>&1 || true
    docker run -d --name fsr-proxy --label fsr=1 --user "$(id -u):$(id -g)" --add-host host.docker.internal:host-gateway \
      -v "$here/proxy.py:/proxy.py:ro" -v "$(dirname "$log"):/log" "${dump[@]}" --entrypoint python3 "$IMAGE" \
      /proxy.py "/log/$(basename "$log")" "18001=$UP27B" "18002=$UPFLASH" >/dev/null
    docker network connect fsr-fence fsr-proxy
    echo "fence up; proxy log $log" ;;
  down)
    docker rm -f fsr-proxy >/dev/null 2>&1 || true
    docker network rm fsr-fence >/dev/null 2>&1 || true
    echo "fence down" ;;
  check)   # from inside the fence: both models answer through the proxy; the outside world does not
    docker run --rm --network fsr-fence -e UP27B="$UP27B" -e UPFLASH="$UPFLASH" --entrypoint python3 "$IMAGE" -c '
import os, urllib.request
for name, url in (("27B via proxy", "http://fsr-proxy:18001/v1/models"), ("Flash Next via proxy", "http://fsr-proxy:18002/v1/models"),
                  ("outside: 1.1.1.1", "http://1.1.1.1/"), ("outside: pypi.org", "https://pypi.org/simple/"),
                  ("27B direct", "http://" + os.environ["UP27B"] + "/v1/models"), ("Flash Next direct", "http://" + os.environ["UPFLASH"] + "/v1/models")):
    try:
        urllib.request.urlopen(url, timeout=8); print(name, "REACHED")
    except Exception as e:
        print(name, "blocked:", type(e).__name__, str(e)[:60])' ;;
esac

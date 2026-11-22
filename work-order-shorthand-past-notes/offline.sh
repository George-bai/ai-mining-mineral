#!/bin/bash
# Run a command with no network but loopback: a new user and network namespace (unprivileged `unshare -rn`).
# Model weights must already be on disk; Hugging Face libraries are told not to look online.
# Usage: offline.sh <command> [args...]
exec unshare -rn env HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 bash -c 'ip link set lo up && exec "$@"' offline "$@"

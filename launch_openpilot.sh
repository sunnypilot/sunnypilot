#!/usr/bin/env bash
pkill -f system/updated/updated.py

#Get rid of any stubborn updated locks
rm -f /tmp/updated.lock
export API_HOST=https://api.konik.ai/
export ATHENA_HOST=wss://athena.konik.ai
set -euo pipefail
IFS=$'\n\t'

# On any failure, run the fallback launcher
trap 'exec ./launch_chffrplus.sh' ERR
C3_LAUNCH_SH="./sunnypilot/system/hardware/c3/launch_chffrplus.sh"

MODEL="$(tr -d '\0' < "/sys/firmware/devicetree/base/model")"
export MODEL

if [ "$MODEL" = "comma tici" ]; then
  # Force a failure if the launcher doesn't exist
  [ -x "$C3_LAUNCH_SH" ] || false

  # If it exists, run it
  exec "$C3_LAUNCH_SH"
fi

exec ./launch_chffrplus.sh

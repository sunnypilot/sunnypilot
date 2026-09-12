#!/bin/bash
# Run only cameras and modeld, with private Params and messaging.
# Stop the offroad jetlinkd owner first; never run this in a moving vehicle.
# OUTPUT may specify a new directory for logs, frame CSV and summary JSON.
set -eu
cd "$(dirname "$0")/.."
export PYTHONPATH=$PWD
exec /usr/local/venv/bin/python3 tools/jetlink_bench.py \
  --seconds "${1:-180}" --output "${OUTPUT:-/data/tmp/jetlink-bench-$(date +%Y%m%d-%H%M%S)}"

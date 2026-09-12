#!/usr/bin/env bash
# Presents the comma as a USB gadget so a Jetson can enumerate it.
#
# Only when the user has turned the link on: a gadget presented by default
# turns link_configured() true and routed manager away from the user's bundle.
# Read through openpilot.common.params so the key type and prefix match; a
# params library not built yet, or without the key, reads as off.
set -u
[ -f /AGNOS ] || exit 0
BASEDIR="$(cd "$(dirname "$0")/../../../.." && pwd)"
STATUS=/dev/shm/jetlink-gadget

enabled=$(PYTHONPATH="$BASEDIR" python3 - <<'PY' 2>/dev/null || echo 0
try:
  from openpilot.common.params import Params
  print(1 if Params().get_bool("JetlinkEnabled") else 0)
except Exception:
  print(0)
PY
)
[ "$enabled" = "1" ] || exit 0

REPO="$BASEDIR/jetlink_repo"
if [ ! -d "$REPO/jetlink" ]; then
  # submodule registered but never fetched; say so where the offroad alert reads
  echo "error: the jetlink package is not installed; run git submodule update --init jetlink_repo" \
    > "$STATUS" 2>/dev/null || true
  exit 0
fi

# the endpoints must exist before jetlinkd or modeld can open them, and that
# needs root. setup_gadget.sh leaves the reason in $STATUS for the offroad alert
sudo -n bash "$REPO/scripts/setup_gadget.sh" >/dev/null ||
  echo "jetlink: USB gadget setup failed" >&2
exit 0

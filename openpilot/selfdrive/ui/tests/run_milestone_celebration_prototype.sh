#!/usr/bin/env bash
# PROTOTYPE: launch the demo replay and comma four milestone celebration together.
set -e

prototype_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
prototype_replay_pid=""

cleanup_prototype() {
  if [[ -n "$prototype_replay_pid" ]]; then
    kill "$prototype_replay_pid" 2>/dev/null || true
    wait "$prototype_replay_pid" 2>/dev/null || true
  fi
}
trap cleanup_prototype EXIT INT TERM

export PATH="$prototype_root/.venv/bin:$PATH"
export SP_MILESTONE_PROTOTYPE=1
prototype_playback="${SP_MILESTONE_PLAYBACK:-1}"

"$prototype_root/openpilot/tools/replay/replay" --demo --playback "$prototype_playback" &
prototype_replay_pid=$!

"$prototype_root/.venv/bin/python" "$prototype_root/openpilot/selfdrive/ui/mici/onroad/augmented_road_view.py"

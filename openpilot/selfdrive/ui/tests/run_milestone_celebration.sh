#!/usr/bin/env bash
set -e

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
replay_pid=""
preview_pid=""

cleanup() {
  for pid in "$preview_pid" "$replay_pid"; do
    if [[ -n "$pid" ]]; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT INT TERM

export PATH="$repo_root/.venv/bin:$PATH"
export SP_MILESTONE_PREVIEW=1
playback="${SP_MILESTONE_PLAYBACK:-1}"

"$repo_root/openpilot/tools/replay/replay" --demo --playback "$playback" &
replay_pid=$!
"$repo_root/.venv/bin/python" "$repo_root/openpilot/selfdrive/ui/tests/milestone_preview.py" &
preview_pid=$!

"$repo_root/.venv/bin/python" "$repo_root/openpilot/selfdrive/ui/mici/onroad/augmented_road_view.py"

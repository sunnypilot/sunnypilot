#!/usr/bin/env bash
#
# Copyright (c) 2026-, Zeph Leggett.
#
# This file is part of sunnypilot and is licensed under the MIT License.
# See the LICENSE.md file in the root directory for more details.
#
# Replay the two upstream changes most likely to land on top of us.
#
# The accelerator work sits in modeld.py beside comma's chestnut, the file
# upstream keeps rewriting. Apply the two known changes to a throwaway
# worktree and report where they land.
#
#   38760  e3def37695  reverts 38742: moves the chestnut poller wait,
#                      helpers.chestnut_ready and one param key
#   38684  cb85ac1f0e  fused warp and policy into one run_model JIT
#
# A conflict inside openpilot/sunnypilot/ is ours to rebase. A conflict anywhere
# else means we changed a line upstream owns, and only that exits non-zero.
#
# Usage: merge_replay.sh [branch]   (default HEAD)

set -uo pipefail

REVERT=e3def37695   # revert 38742 (#38760)
FUSED=cb85ac1f0e    # amd warp (#38684)

# the revert also touches files this fork carries differently; only modeld
# and the param key matter
REVERT_PATHS=(openpilot/selfdrive/modeld openpilot/common/params_keys.h)

BRANCH="${1:-HEAD}"
REPO="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 2

SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/jetlink-merge-replay.XXXXXX")" || exit 2
TREE="$SCRATCH/worktree"

cleanup() {
  git -C "$REPO" worktree remove --force "$TREE" >/dev/null 2>&1
  rm -rf "$SCRATCH"
  git -C "$REPO" worktree prune >/dev/null 2>&1
}
trap cleanup EXIT

for commit in "$REVERT" "$FUSED"; do
  if ! git -C "$REPO" cat-file -e "${commit}^{commit}" 2>/dev/null; then
    echo "merge_replay: $commit is not in this checkout; fetch upstream first" >&2
    exit 2
  fi
done

# detached, so a branch checked out in another worktree still replays
if ! git -C "$REPO" worktree add --detach "$TREE" "$BRANCH" >/dev/null 2>&1; then
  echo "merge_replay: could not create a worktree for $BRANCH" >&2
  exit 2
fi

git -C "$REPO" format-patch -1 --stdout "$REVERT" -- "${REVERT_PATHS[@]}" > "$SCRATCH/revert.patch" || exit 2
git -C "$REPO" format-patch -1 --stdout "$FUSED" > "$SCRATCH/fused.patch" || exit 2

head_sha="$(git -C "$TREE" rev-parse --short HEAD)"
echo "merge replay of $BRANCH ($head_sha)"
echo

failures=0

replay() {
  local name="$1" patch="$2" out rc files outside conflicted file

  echo "=== $name ==="
  out="$(git -C "$TREE" apply --check --verbose "$patch" 2>&1)"
  rc=$?
  printf '%s\n' "$out"

  if [ "$rc" -eq 0 ]; then
    echo "-> clean"
    echo
    return
  fi

  # both shapes git uses: a hunk that would not apply, and a file it gave up on
  files="$(printf '%s\n' "$out" |
    sed -n -E -e 's/^error: patch failed: (.+):[0-9]+$/\1/p' \
              -e 's/^error: (.+): patch does not apply$/\1/p' \
              -e 's/^error: (.+): does not exist in index$/\1/p' |
    sort -u)"

  echo "-> failing hunks in:"
  printf '%s\n' "$files" | sed 's/^/     /'

  # applied for real: --check --3way returns 0 on a patch whose three-way
  # apply leaves conflict markers
  git -C "$TREE" apply --3way "$patch" >/dev/null 2>&1
  conflicted="$(git -C "$TREE" diff --name-only --diff-filter=U)"
  if [ -z "$conflicted" ]; then
    echo "-> --3way merges it cleanly: context drift, not a real conflict"
  else
    # region count: run against the parent branch too, the difference is what
    # this fork adds to a rebase
    echo "-> --3way still conflicts in:"
    while IFS= read -r file; do
      echo "     $file ($(grep -c '^<<<<<<<' "$TREE/$file") region(s))"
    done <<< "$conflicted"
  fi
  git -C "$TREE" reset --hard >/dev/null 2>&1
  git -C "$TREE" clean -fdq >/dev/null 2>&1

  outside="$(printf '%s\n' "$files" | grep -v '^openpilot/sunnypilot/' | grep -v '^$')"
  if [ -n "$outside" ]; then
    echo "-> OUTSIDE openpilot/sunnypilot/, which is upstream's to own:"
    printf '%s\n' "$outside" | sed 's/^/     /'
    failures=$((failures + 1))
  else
    echo "-> confined to openpilot/sunnypilot/, ours to rebase"
  fi
  echo
}

replay "38760 revert ($REVERT), modeld and params only" "$SCRATCH/revert.patch"
replay "38684 fused warp ($FUSED)" "$SCRATCH/fused.patch"

if [ "$failures" -ne 0 ]; then
  echo "merge replay: $failures patch(es) conflict outside openpilot/sunnypilot/"
  echo "run it against the parent branch too: a hunk that fails there as well is not ours"
  exit 1
fi
echo "merge replay: nothing upstream owns conflicts"

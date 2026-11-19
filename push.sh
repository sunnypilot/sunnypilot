#!/usr/bin/env bash
#
# Push the Plan-Aligned Braking changes from your local sunnypilot repo to your fork as a PR-ready branch,
# WITHOUT touching your current branch, working tree, index, stash, or remotes.
#
# How it stays non-destructive:
#   * fetches the latest upstream master by URL into FETCH_HEAD (no remote is added or changed)
#   * builds the commit in a throw-away `git worktree` on top of that upstream master, from ONLY the 8 plan-align files
#   * pushes straight to your fork's URL (no remote switching needed, so there is nothing to switch back)
#   * removes the worktree, then compares a before/after snapshot of your repo and tells you if anything differs
#
# Run from anywhere inside your sunnypilot clone (the one where the fix is already applied):
#   ./push_plan_align_pr.sh                 # interactive: shows the diff, asks before pushing
#   ./push_plan_align_pr.sh --dry-run       # build + verify only, push nothing
#   ./push_plan_align_pr.sh -y              # no confirmation prompt
#   ./push_plan_align_pr.sh -b my-branch    # branch name on your fork (default: plan-aligned-braking)
#   ./push_plan_align_pr.sh --force         # overwrite the branch on your fork if it already exists
#
# Optional env overrides:  FORK_URL  UPSTREAM_URL  UPSTREAM_BRANCH
set -euo pipefail

FORK_URL="${FORK_URL:-https://github.com/datletrung/sunnypilot.git}"
UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/sunnypilot/sunnypilot.git}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-master}"
BRANCH="plan-aligned-braking"
ASSUME_YES=0
DRY_RUN=0
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    -b|--branch) BRANCH="${2:?branch name required}"; shift 2 ;;
    -y|--yes) ASSUME_YES=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

FILES=(
  "openpilot/common/params_keys.h"
  "openpilot/selfdrive/controls/lib/longitudinal_planner.py"
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/models.py"
  "openpilot/selfdrive/ui/sunnypilot/mici/layouts/models.py"
  "openpilot/sunnypilot/sunnylink/settings_ui_src/pages/models.yaml"
  "openpilot/sunnypilot/sunnylink/settings_ui.json"
  "openpilot/sunnypilot/selfdrive/controls/lib/plan_align.py"
  "openpilot/sunnypilot/selfdrive/controls/lib/tests/test_plan_align.py"
)

say()  { printf '\n\033[1m== %s\033[0m\n' "$*"; }
die()  { printf '\n\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }
warn() { printf '\033[33mwarning:\033[0m %s\n' "$*" >&2; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not inside a git repository"
cd "$ROOT"
[ -f openpilot/common/params_keys.h ] || die "this does not look like the sunnypilot repo root ($ROOT)"
git config user.email >/dev/null && git config user.name >/dev/null || die "git user.name / user.email are not set (git config --global user.name ...)"

snapshot() {
  echo "branch:   $(git rev-parse --abbrev-ref HEAD)"
  echo "head:     $(git rev-parse HEAD)"
  echo "remotes:  $(git remote -v | sha256sum | cut -c1-16)"
  echo "status:   $(git status --porcelain=v1 | sha256sum | cut -c1-16)"
  echo "unstaged: $(git diff | sha256sum | cut -c1-16)"
  echo "staged:   $(git diff --cached | sha256sum | cut -c1-16)"
  echo "stash:    $(git stash list | sha256sum | cut -c1-16)"
}
BEFORE="$(snapshot)"

TMP="$(mktemp -d)"
WT="$TMP/wt"
cleanup() {
  git worktree remove --force "$WT" >/dev/null 2>&1 || true
  git worktree prune >/dev/null 2>&1 || true
  rm -rf "$TMP"
}
trap cleanup EXIT

# 1. latest upstream, fetched by URL (touches no remote, no branch)
say "Fetching $UPSTREAM_URL ($UPSTREAM_BRANCH)"
git fetch --no-tags --quiet "$UPSTREAM_URL" "$UPSTREAM_BRANCH" || die "could not fetch upstream"
BASE="$(git rev-parse FETCH_HEAD)"
MB="$(git merge-base HEAD "$BASE" 2>/dev/null || true)"
[ -n "$MB" ] || { warn "no common history with upstream; diffing against upstream master directly"; MB="$BASE"; }
echo "upstream base : $(git rev-parse --short "$BASE")"
echo "your merge-base: $(git rev-parse --short "$MB")"

# 2. collect exactly the plan-align changes from your repo
say "Collecting the plan-align changes from your working tree"
PATCH="$TMP/changes.patch"; : > "$PATCH"
COPIED=()
MISSING=()
for f in "${FILES[@]}"; do
  if [ ! -e "$f" ]; then MISSING+=("$f"); continue; fi
  if git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then
    git diff "$MB" -- "$f" >> "$PATCH"        # tracked: committed and/or uncommitted changes vs merge-base
  else
    COPIED+=("$f")                             # untracked new file
  fi
done
[ ${#MISSING[@]} -eq 0 ] || die "these files are missing, so the fix is not fully applied here: ${MISSING[*]}"
[ -s "$PATCH" ] || [ ${#COPIED[@]} -gt 0 ] || die "no plan-align changes found in $ROOT (nothing differs from upstream)"

# 3. build the commit in a throw-away worktree on top of upstream master
say "Building the commit on a clean upstream checkout (your working tree is not touched)"
git worktree add --detach --quiet "$WT" "$BASE"
if [ -s "$PATCH" ]; then
  git -C "$WT" apply --3way --index "$PATCH" || die "changes do not apply cleanly on the latest upstream master (conflict). Nothing was pushed."
fi
for f in "${COPIED[@]}"; do
  mkdir -p "$WT/$(dirname "$f")"
  cp "$f" "$WT/$f"
  git -C "$WT" add -- "$f"
done

# only the 8 expected files may be in the commit
EXPECTED="$(printf '%s\n' "${FILES[@]}" | sort)"
STAGED="$(git -C "$WT" diff --cached --name-only | sort)"
UNEXPECTED="$(comm -13 <(printf '%s\n' "$EXPECTED") <(printf '%s\n' "$STAGED") || true)"
[ -z "$UNEXPECTED" ] || die "unexpected files would be committed:\n$UNEXPECTED"
[ -n "$STAGED" ] || die "nothing to commit: upstream already contains these changes"

# 4. verify before anything leaves your machine
say "Verifying"
for f in "${FILES[@]}"; do
  case "$f" in *.py) python3 -m py_compile "$WT/$f" || die "syntax error in $f" ;; esac
done
echo "python syntax: ok"
if python3 -c 'import yaml' 2>/dev/null; then
  python3 "$WT/openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py" --check || die "settings_ui.json is out of sync with the YAML"
else
  warn "PyYAML not installed; skipped the settings_ui.json <-> YAML sync check"
fi
git -C "$WT" diff --cached --stat

git -C "$WT" commit --quiet -m "controls: Plan-Aligned Braking (alpha)" -m \
"Models with a learned action head can command less braking than their own plan implies, so with no lead car the
car creeps toward stops and overshoots red lights, more so at higher speed. Pull the e2e acceleration toward the
stronger of the plan-implied accel and the decel needed to stop at the plan's predicted stop point.

- only ever brakes harder, only while the action accel is already braking, never with a lead, floored at -3.0 m/s^2
- off by default; sunnylink + TICI + mici toggle marked Alpha
- Custom (non-Default) models only, same gate as Blendful (ModelRunnerTypeCache)
- unit tests in sunnypilot/selfdrive/controls/lib/tests/test_plan_align.py"
NEWSHA="$(git -C "$WT" rev-parse --short HEAD)"
echo "commit: $NEWSHA"

# 5. push
if [ "$DRY_RUN" -eq 1 ]; then
  say "Dry run: built and verified commit $NEWSHA, nothing pushed"
else
  if [ "$ASSUME_YES" -ne 1 ]; then
    printf '\nPush commit %s to %s as branch "%s"? [y/N] ' "$NEWSHA" "$FORK_URL" "$BRANCH"
    read -r ans
    case "$ans" in y|Y|yes|YES) ;; *) echo "aborted; nothing pushed"; exit 0 ;; esac
  fi
  say "Pushing to $FORK_URL"
  PUSH_ARGS=()
  [ "$FORCE" -eq 1 ] && PUSH_ARGS+=(--force)
  if ! git -C "$WT" push "${PUSH_ARGS[@]}" "$FORK_URL" "HEAD:refs/heads/$BRANCH"; then
    die "push failed. If it is an auth error, log in first (gh auth login, or a GitHub personal access token as the HTTPS password). If the branch already exists on your fork, re-run with --force or pick another name with -b."
  fi
fi

# 6. restore / prove nothing local changed
cleanup
trap - EXIT
say "Checking your local repo is exactly as you left it"
AFTER="$(snapshot)"
if [ "$BEFORE" = "$AFTER" ]; then
  echo "branch, HEAD, remotes, working tree, index and stash: all unchanged"
else
  warn "local state differs from before:"; diff <(echo "$BEFORE") <(echo "$AFTER") || true
fi

if [ "$DRY_RUN" -eq 0 ]; then
  OWNER="$(printf '%s' "$FORK_URL" | sed -E 's#^.*github\.com[:/]([^/]+)/([^/.]+)(\.git)?$#\1#')"
  REPO="$(printf '%s' "$FORK_URL"  | sed -E 's#^.*github\.com[:/]([^/]+)/([^/.]+)(\.git)?$#\2#')"
  UP_OWNER="$(printf '%s' "$UPSTREAM_URL" | sed -E 's#^.*github\.com[:/]([^/]+)/([^/.]+)(\.git)?$#\1#')"
  UP_REPO="$(printf '%s' "$UPSTREAM_URL"  | sed -E 's#^.*github\.com[:/]([^/]+)/([^/.]+)(\.git)?$#\2#')"
  if [ "$OWNER" != "$FORK_URL" ] && [ "$UP_OWNER" != "$UPSTREAM_URL" ]; then
    say "Open the PR"
    echo "https://github.com/$UP_OWNER/$UP_REPO/compare/$UPSTREAM_BRANCH...$OWNER:$REPO:$BRANCH?expand=1"
  fi
fi

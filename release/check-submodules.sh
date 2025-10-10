#!/usr/bin/env bash
set -euo pipefail

has_submodule_changes() {
  local submodule_path="$1"
  if [ -n "${SUBMODULE_PATHS:-}" ]; then
    echo " ${SUBMODULE_PATHS} " | grep -qw " ${submodule_path} "
    return $?
  fi
  return 1
}

required_branch_for() {
  local sub="$1"
  local lts_branch="${LTS_BRANCH:-master-tici}"
  local lts_list=" ${LTS_SUBMODULES:-} "

  # Hard guarantee for these two; env list is still honored for flexibility
  case "$sub" in
    opendbc_repo|panda) echo "$lts_branch"; return 0 ;;
  esac

  if echo "$lts_list" | grep -qw " $sub "; then
    echo "$lts_branch"
  else
    echo "master"
  fi
}

while read -r hash submodule ref; do
  # robust blank-skip (no &&/|| precedence footgun)
  if [ -z "${hash:-}" ] || [ -z "${submodule:-}" ]; then
    continue
  fi

  # strip +/- from `git submodule status`
  hash="${hash#[-+]}"

  # ignore specific submodule if desired
  if [ "$submodule" = "tinygrad_repo" ]; then
    echo "Skipping $submodule"
    continue
  fi

  target_branch="$(required_branch_for "$submodule")"
  echo "Submodule ${submodule}: enforcing origin/${target_branch}"

  if [ "${CHECK_PR_REFS:-}" = "true" ] && has_submodule_changes "$submodule"; then
    echo "  (changed in PR) verifying hash ${hash} exists"
    git -C "$submodule" fetch --depth 100 origin
    if git -C "$submodule" cat-file -e "$hash" 2>/dev/null; then
      echo "  ${submodule} ok (hash exists)"
    else
      echo "  ${submodule}: ${hash} does not exist in the repository"
      exit 1
    fi
  else
    echo "  Checking ${submodule} on origin/${target_branch}: verifying ${hash} is contained"
    git -C "$submodule" fetch --depth 100 origin "${target_branch}"
    if git -C "$submodule" branch -r --contains "$hash" | grep -q "origin/${target_branch}"; then
      echo "  ${submodule} ok"
    else
      echo "  ${submodule}: ${hash} is not on ${target_branch}"
      exit 1
    fi
  fi
done <<<"$(git submodule status --recursive)"

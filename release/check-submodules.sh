#!/usr/bin/env bash

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
  case "$sub" in
    opendbc_repo|panda) echo "master-tici" ;;
    *)                  echo "master" ;;
  esac
}

while read -r hash submodule ref; do
  if [ -z "${hash:-}" ] || [ -z "${submodule:-}" ]; then
    continue
  fi

  hash="${hash#[-+]}"

  if [ "$submodule" = "tinygrad_repo" ]; then
    echo "Skipping $submodule"
    continue
  fi

  if [ "${CHECK_PR_REFS:-}" = "true" ] && has_submodule_changes "$submodule"; then
    echo "Checking $submodule (changed in PR): verifying hash $hash exists"
    git -C "$submodule" fetch --depth 100 origin
    if git -C "$submodule" cat-file -e "$hash" 2>/dev/null; then
      echo "$submodule ok (hash exists)"
    else
      echo "$submodule: $hash does not exist in the repository"
      exit 1
    fi
  else
    branch="$(required_branch_for "$submodule")"
    echo "Checking $submodule on origin/$branch: verifying $hash is contained"
    git -C "$submodule" fetch --depth 100 origin "$branch"
    if git -C "$submodule" branch -r --contains "$hash" | grep -q "origin/$branch"; then
      echo "$submodule ok"
    else
      echo "$submodule: $hash is not on $branch"
      exit 1
    fi
  fi
done <<<"$(git submodule status --recursive)"

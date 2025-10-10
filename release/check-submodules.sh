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

    git -C "$submodule" fetch --no-tags origin "$branch" --depth=0
    git -C "$submodule" fetch --no-tags origin "$hash" || true
    if ! git -C "$submodule" cat-file -e "$hash^{commit}" 2>/dev/null; then
      echo "  $submodule: commit $hash not present locally after fetch"
      git -C "$submodule" remote -v
      exit 1
    fi

    if git -C "$submodule" merge-base --is-ancestor "$hash" "origin/$branch"; then
      echo "$submodule ok"
    else
      echo "$submodule: $hash is not on $branch"
      echo "  Debug:"
      git -C "$submodule" show -s --oneline "$hash" || true
      git -C "$submodule" log --oneline -n 20 "origin/$branch" || true
      exit 1
    fi
  fi
done <<<"$(git submodule status --recursive)"

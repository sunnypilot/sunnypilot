#!/usr/bin/env bash
# How to use: run from the root of the openpilot repository with the following command: ./release/ci/sync-lfs.sh

# Set variables
export their_repo="https://github.com/commaai/openpilot.git"
export their_branch="master"
export current_branch=$(git rev-parse --abbrev-ref HEAD)
export our_lfs_url=${LFS_URL:-"https://gitlab.com/sunnypilot/public/sunnypilot-lfs.git/info/lfs"}
export our_lfs_push_url=${LFS_PUSH_URL:-"ssh://git@gitlab.com/sunnypilot/public/sunnypilot-lfs.git"}

echo "Syncing LFS objects from $their_repo:$their_branch to $our_lfs_url"
echo "Pushing LFS objects to $our_lfs_push_url"

# Function to reset to the current branch and perform a hard reset
function reset_hard {
    exit_status=$?
    echo "Resetting to the current branch and performing a hard reset..."
    git reset --hard
    git switch $current_branch
    exit $exit_status
}

# Set trap to ensure reset on exit
trap reset_hard SIGINT SIGTERM EXIT

# Add remote if it does not exist
git remote add comma $their_repo 2>/dev/null || echo "Remote 'comma' already exists."

# Fetch the specified branch from the remote
git fetch comma $their_branch

# Clean up old branch if it exists
git branch -D ${their_branch}-upstream 2>/dev/null || echo "No old branch to clean up."

# Checkout new branch based on the upstream branch
git checkout -b ${their_branch}-upstream comma/$their_branch

# Write the .lfsconfig directly
cat <<EOL > .lfsconfig
[lfs]
    url = $our_lfs_url
    pushurl = $our_lfs_push_url
    locksverify = false
EOL

# Fetch all LFS objects and push them to the specified pushurl
git lfs fetch --all
git lfs push --all $our_lfs_push_url
git restore .lfsconfig

# Switch back to the current branch (handled by trap)

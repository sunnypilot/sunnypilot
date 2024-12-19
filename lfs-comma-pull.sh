#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
FETCH_ALL=0
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -a|--all) FETCH_ALL=1 ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

# Function to clean up resources
cleanup() {
    if [ -f .lfsconfig.backup ]; then
        mv .lfsconfig.backup .lfsconfig
        echo -e "${GREEN}Restored original LFS configuration${NC}"
    else
        rm -f .lfsconfig
    fi
    git remote remove comma-lfs-sync 2>/dev/null || true
}

# Set up trap to ensure cleanup on script exit
trap cleanup EXIT

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle errors
handle_error() {
    echo -e "${RED}$1${NC}"
    exit 1
}

# Function to get LFS objects
get_lfs_objects() {
    local mode=$1
    if [ "$mode" = "missing" ]; then
        git lfs ls-files | awk '$2 == "-" {$1=""; $2=""; sub(/^[ \t]+/, ""); print}'
    else
        git lfs ls-files | awk '{$1=""; $2=""; sub(/^[ \t]+/, ""); print}'
    fi
}

# Function to perform LFS operations
perform_lfs_operations() {
    git lfs fetch ${FETCH_ALL:+"--all"} comma-lfs-sync || handle_error "Failed to fetch LFS objects"
    git lfs checkout || handle_error "Failed to checkout LFS objects"
    echo -e "${GREEN}Successfully fetched ${FETCH_ALL:+"all"}${FETCH_ALL:-"missing"} LFS objects${NC}"
}

# Check if git-lfs is installed
if ! command_exists git-lfs; then
    echo -e "${RED}Error: git-lfs is not installed${NC}"
    echo "Please install git-lfs first:"
    echo "  brew install git-lfs    # On macOS"
    echo "  apt-get install git-lfs # On Ubuntu/Debian"
    exit 1
fi

# Clean up any existing LFS config
echo -e "${YELLOW}Cleaning up existing LFS configurations...${NC}"
git config --unset-all lfs.url
git config --unset-all lfs.pushurl
git config --local --unset-all lfs.url
git config --local --unset-all lfs.pushurl

# Backup current LFS config
[ -f .lfsconfig ] && cp .lfsconfig .lfsconfig.backup

# Check for and use upstream config
if [ ! -f .lfsconfig-comma ]; then
    handle_error "Warning: .lfsconfig-comma not found"
fi

# Switch to upstream config and pull objects
echo -e "${YELLOW}Using upstream LFS configuration...${NC}"
git remote add comma-lfs-sync https://github.com/commaai/openpilot.git
git fetch comma-lfs-sync
cp .lfsconfig-comma .lfsconfig
echo -e "${GREEN}Switched to upstream LFS configuration${NC}"

if [ $FETCH_ALL -eq 1 ]; then
    echo -e "${YELLOW}Fetching all LFS objects (including already present)...${NC}"
    perform_lfs_operations
else
    MISSING_FILES=$(get_lfs_objects "missing")
    if [ ! -z "$MISSING_FILES" ]; then
        echo -e "${YELLOW}Missing files to fetch:${NC}"
        echo "$MISSING_FILES"
        perform_lfs_operations
    else
        echo -e "${GREEN}No missing LFS objects to fetch${NC}"
    fi
fi

echo -e "${GREEN}LFS sync completed successfully${NC}"
exit 0
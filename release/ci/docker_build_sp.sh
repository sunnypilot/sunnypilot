#!/bin/sh
# run_openpilot_docker.sh
# POSIX-compliant script to run openpilot in Docker for local testing

# === Configurable Variables ===

# Base image to use (required)
BASE_IMAGE="${BASE_IMAGE:-commaai/openpilot-base:latest}"

# Working directory inside the container
WORKDIR="/tmp/openpilot"

# Local project path
LOCAL_DIR="$PWD"

# Shared memory size (adjust for large builds/tests)
SHM_SIZE="2G"

# Environment configuration
CI=1
PYTHONWARNINGS="error"
FILEREADER_CACHE=1
PYTHONPATH="$WORKDIR"

# Optional: GitHub Actions env vars — set them only if needed for local mirroring/debug
USE_GITHUB_ENV_VARS=false  # set to true to enable GitHub-related mounts/envs
GITHUB_WORKSPACE="${GITHUB_WORKSPACE:-$HOME/openpilot_ci}"  # fallback path

# === Docker Command ===

docker run --rm \
  --shm-size "$SHM_SIZE" \
  -v "$LOCAL_DIR":"$WORKDIR" \
  -w "$WORKDIR" \
  -e CI="$CI" \
  -e PYTHONWARNINGS="$PYTHONWARNINGS" \
  -e FILEREADER_CACHE="$FILEREADER_CACHE" \
  -e PYTHONPATH="$PYTHONPATH" \
  ${USE_GITHUB_ENV_VARS:+\
  -e NUM_JOBS \
  -e JOB_ID \
  -e GITHUB_ACTION \
  -e GITHUB_REF \
  -e GITHUB_HEAD_REF \
  -e GITHUB_SHA \
  -e GITHUB_REPOSITORY \
  -e GITHUB_RUN_ID \
  -v "$GITHUB_WORKSPACE/.ci_cache/scons_cache":/tmp/scons_cache \
  -v "$GITHUB_WORKSPACE/.ci_cache/comma_download_cache":/tmp/comma_download_cache \
  -v "$GITHUB_WORKSPACE/.ci_cache/openpilot_cache":/tmp/openpilot_cache } \
  "$BASE_IMAGE" /bin/bash -c "${1:-/bin/bash}"

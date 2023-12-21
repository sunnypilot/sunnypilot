# UNUSED YET BUT I WANT TO KEEP IT BECAUSE I INTEND TO USE IT SOON

#!/usr/bin/env bash

# set -e

# DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
# cd $DIR

# # Take parameters as arguments
# SOURCE_DIR=$1
# OUTPUT_DIR=$2

# # Check parameters
# if [ -z "$SOURCE_DIR" ] || [ -z "$OUTPUT_DIR" ]; then
#     echo "Error: No source or output directory provided."
#     exit 1
# fi

# if [ -z "$TARGETPLATFORM" ]; then
#     # Detect the platform (e.g., x86_64, aarch64, etc.)
#     platform=$(uname -m)

#     # Map to Docker's platform syntax
#     if [ "$platform" = "x86_64" ]; then
#         TARGETPLATFORM="linux/amd64"
#     elif [ "$platform" = "aarch64" ]; then
#         TARGETPLATFORM="linux/arm64"
#     # Add here more elif statements for other architectures if needed.
#     else
#         echo "Unknown platform: $platform"
#         exit 1
#     fi

#     export TARGETPLATFORM
# fi

# echo "TARGETPLATFORM IS: [${TARGETPLATFORM}]"

# # Let's bring the submodules!
# git submodule update --init --recursive

# # Build
# docker compose -f ${SOURCE_DIR}/docker-compose.yml build
# docker compose -f ${SOURCE_DIR}/docker-compose.yml up

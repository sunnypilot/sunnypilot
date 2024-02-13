# UNUSED YET BUT I WANT TO KEEP IT BECAUSE I INTEND TO USE IT SOON

# #!/usr/bin/env bash
# DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
# cd $DIR

# DEV_BRANCH=$1
# GIT_ORIGIN=$2
# if [ -z "$DEV_BRANCH" ]; then
#     DEV_BRANCH="dev-c3-test"
# fi

# if [ -z "$GIT_ORIGIN" ]; then
#     GIT_ORIGIN="git@github.com:devtekve/openpilot-og.git" #This is a default that should be changed
#     echo "No GIT_ORIGIN provided, we will use the default [${GIT_ORIGIN}]"
# fi

# VERSION=$(date '+%Y.%m.%d')
# SOURCE_DIR="$(git rev-parse --show-toplevel)"
# OUTPUT_DIR=${SOURCE_DIR}/output


# echo "Calling to build [${DIR}/build.sh ${SOURCE_DIR} ${OUTPUT_DIR} ${VERSION}]"
# $DIR/build.sh "${SOURCE_DIR}" "${OUTPUT_DIR}" "${VERSION}"

# echo "Calling to publish [${DIR}/publish.sh ${SOURCE_DIR} ${OUTPUT_DIR} ${DEV_BRANCH} ${VERSION} ${GIT_ORIGIN}]"
# $DIR/publish.sh "${SOURCE_DIR}" "${OUTPUT_DIR}" "${DEV_BRANCH}" "${VERSION}" "${GIT_ORIGIN}"

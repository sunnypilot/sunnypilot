#!/usr/bin/bash -e

# git diff --name-status origin/release3-staging | grep "^A" | less

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"

cd $DIR

BUILD_DIR=/data/media/openpilot-dev
SOURCE_DIR="$(git rev-parse --show-toplevel)"

FILES_SRC="release/files_tici"
DEV_BRANCH="dev-c3"

BUILD_PANDA_DIR=/data/media/panda/openpilot-dev


# set git identity
source $DIR/identity.sh
export GIT_SSH_COMMAND="ssh -i /data/gitkey"

echo "[-] Setting up repo T=$SECONDS"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR
cd $BUILD_DIR
git init
# set git username/password
source /data/identity.sh
git remote add origin https://github.com/sunnyhaibin/sunnypilot.git
git fetch origin $DEV_BRANCH

# do the files copy
echo "[-] copying files T=$SECONDS"
cd $SOURCE_DIR
cp -pR --parents $(cat release/files_common) $BUILD_DIR/
cp -pR --parents $(cat $FILES_SRC) $BUILD_DIR/

# in the directory
cd $BUILD_DIR

rm -f panda/board/obj/panda.bin.signed
rm -f panda/board/obj/panda_h7.bin.signed
rm -f panda/board/obj/bootstub.panda.bin
rm -f panda/board/obj/bootstub.panda_h7.bin

VERSION=$(date '+%Y.%m.%d')
echo "#define COMMA_VERSION \"$VERSION-dev\"" > common/version.h

echo "[-] committing version $VERSION T=$SECONDS"
git add -f .
git commit -a -m "sunnypilot v$VERSION release"
git branch --set-upstream-to=origin/$DEV_BRANCH

# Build panda firmware
pushd panda/
scons -u .
mv board/obj/panda.bin.signed $BUILD_PANDA_DIR/panda.bin.signed
mv board/obj/panda_h7.bin.signed $BUILD_PANDA_DIR/panda_h7.bin.signed
mv board/obj/bootstub.panda.bin $BUILD_PANDA_DIR/bootstub.panda.bin
mv board/obj/bootstub.panda_h7.bin $BUILD_PANDA_DIR/bootstub.panda_h7.bin
popd

# Build
export PYTHONPATH="$BUILD_DIR"
scons -j$(nproc)

# Ensure no submodules in release
if test "$(git submodule--helper list | wc -l)" -gt "0"; then
  echo "submodules found:"
  git submodule--helper list
  exit 1
fi
git submodule status

# Cleanup
find . -name '*.a' -delete
find . -name '*.o' -delete
find . -name '*.os' -delete
find . -name '*.pyc' -delete
find . -name 'moc_*' -delete
find . -name '*.cc' -delete
find . -name '__pycache__' -delete
find selfdrive/ui/ -name '*.h' -delete
rm -rf panda/board panda/certs panda/crypto
rm -rf .sconsign.dblite Jenkinsfile release/
rm selfdrive/modeld/models/supercombo.onnx
rm -rf selfdrive/ui/replay/
# Move back signed panda fw
mkdir -p panda/board/obj
mv $BUILD_PANDA_DIR/panda.bin.signed panda/board/obj/panda.bin.signed
mv $BUILD_PANDA_DIR/panda_h7.bin.signed panda/board/obj/panda_h7.bin.signed
mv $BUILD_PANDA_DIR/bootstub.panda.bin panda/board/obj/bootstub.panda.bin
mv $BUILD_PANDA_DIR/bootstub.panda_h7.bin panda/board/obj/bootstub.panda_h7.bin

# Restore third_party
git checkout third_party/

# Mark as prebuilt release
touch prebuilt

# include source commit hash and build date in commit
GIT_HASH=$(git --git-dir=$SOURCE_DIR/.git rev-parse HEAD)
DATETIME=$(date '+%Y-%m-%dT%H:%M:%S')
SP_VERSION=$(cat $SOURCE_DIR/common/version.h | awk -F\" '{print $2}')

# Add built files to git
git add -f .
git commit --amend -m "sunnypilot v$VERSION
version: sunnypilot v$SP_VERSION release
date: $DATETIME
master commit: $GIT_HASH
"
git branch -m dev-c3

# Run tests
#TEST_FILES="tools/"
#cd $SOURCE_DIR
#cp -pR -n --parents $TEST_FILES $BUILD_DIR/
#cd $BUILD_DIR
#RELEASE=1 selfdrive/test/test_onroad.py
#selfdrive/manager/test/test_manager.py
#selfdrive/car/tests/test_car_interfaces.py
#rm -rf $TEST_FILES

if [ ! -z "$PUSH" ]; then
  echo "[-] pushing T=$SECONDS"
  git push -f origin $DEV_BRANCH
fi

echo "[-] done T=$SECONDS"

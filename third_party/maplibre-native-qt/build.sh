#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"

ARCHNAME=$(uname -m)
MAPLIBRE_FLAGS="-DMLN_QT_WITH_LOCATION=OFF"
if [ -f /AGNOS ]; then
  ARCHNAME="larch64"
  #MAPLIBRE_FLAGS="$MAPLIBRE_FLAGS -DCMAKE_SYSTEM_NAME=Android -DANDROID_ABI=arm64-v8a"
fi

if [[ "$(uname)" == "Darwin" ]]; then
  # We are on macOS, set ARCHNAME to "darwin"
  export ARCHNAME="darwin"
  echo "Running on macOS, ARCHNAME set to $ARCHNAME"
fi

cd $DIR
if [ ! -d maplibre ]; then
  git clone git@github.com:maplibre/maplibre-native-qt.git $DIR/maplibre
fi

cd maplibre
git fetch --all
git checkout 3726266e127c1f94ad64837c9dbe03d238255816
git submodule update --depth=1 --recursive --init

# build
mkdir -p build
cd build
set -x
cmake $MAPLIBRE_FLAGS $DIR/maplibre
make -j$(nproc) || make -j2 || make -j1

INSTALL_DIR="$DIR/$ARCHNAME"
rm -rf $INSTALL_DIR
mkdir -p $INSTALL_DIR

rm -rf $INSTALL_DIR/lib $DIR/include
mkdir -p $INSTALL_DIR/lib $INSTALL_DIR/include $DIR/include
cp -r $DIR/maplibre/build/src/core/include/* $INSTALL_DIR/include
cp -r $DIR/maplibre/src/**/*.hpp $DIR/include

if [[ "${ARCHNAME}" == "darwin" ]]; then
  cp -r $DIR/maplibre/build/src/core/QMapLibre.framework $INSTALL_DIR/lib/QMapLibre.framework
else
  cp -r $DIR/maplibre/build/src/core/*.so* $INSTALL_DIR/lib/ 
fi

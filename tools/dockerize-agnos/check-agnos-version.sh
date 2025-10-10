#!/usr/bin/env bash

# sanity check: is this AGNOS?
if [ ! -f /AGNOS ]; then
    echo "ERROR: This script must execute on AGNOS OS."
    exit 255
fi

# find base directory
unset BASEDIR
unset WORKINGDIR
for path in ../.. .. .; do
    [ -f "$path/launch_env.sh" ] && BASEDIR=$(readlink -f "$path")
done
if [ -z "$BASEDIR" ]; then
    echo "ERROR: OP base directory not found."
    exit 255
fi
cd $BASEDIR

source launch_env.sh
echo "Required  AGNOS=$AGNOS_VERSION"
VERSION=$(< /VERSION)
echo "Installed AGNOS=$VERSION"

if [ "$AGNOS_VERSION" != "$VERSION" ]; then
  echo "AGNOS version does not match."
  echo "You likely need to update the agnos-system base image."
  echo "Aborting."
  exit 1
fi

exit 0

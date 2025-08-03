#!/bin/bash

# Reads AGNOS system image URL from system/hardware/tici/agnos.json

# find base directory
unset BASEDIR
unset WORKINGDIR
AGNOSJSON="system/hardware/tici/agnos.json"
for path in ../.. .. .; do
    [ -f "$path/$AGNOSJSON" ] && BASEDIR=$(readlink -f "$path")
done
if [ -z "$BASEDIR" ]; then
    echo "ERROR: OP base directory not found."
    exit 255
fi
WORKINGDIR="$BASEDIR/tools/dockerize-agnos"
echo "BASEDIR=$BASEDIR"
echo "WORKINGDIR=$WORKINGDIR"
cd $WORKINGDIR

SYSTEMURL=$(jq -r '.[] | select(.name == "system") | .url' ../../system/hardware/tici/agnos.json)
HASH=$(jq -r '.[] | select(.name == "system") | .hash' ../../system/hardware/tici/agnos.json)
SYSTEMIMGXZ="tmp/$(basename $SYSTEMURL)"
SYSTEMIMG="${SYSTEMIMGXZ%.xz}"

echo "SYSTEMURL=$SYSTEMURL"
echo "HASH=$HASH"

# Download system image
echo "Download system image from $SYSTEMURL"
curl -C - $SYSTEMURL -o $SYSTEMIMGXZ

# Decompress
echo "Decompress system image to $SYSTEMIMG"
rm -f $SYSTEMIMG
xz -d -k $SYSTEMIMGXZ

# Verify Integrity of sparse image
echo "Verify integrity of decompressed sparse image $SYSTEMIMG"
if ! echo "$HASH  $SYSTEMIMG" | sha256sum -c; then
    exit 255
fi

#!/usr/bin/env bash
###
### Download and convert AGNOS system image to docker base image
###
### Requires Linux and root to mount and copy from ext4 filesystem
###

# Check if running as root or sudo
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root or with sudo."
    echo "This script requires root on Linux to copy from ext4 filesystem."
    exit 1
fi

# Check for required utilities
for util in simg2img xz jq curl sha256sum; do
    if ! command -v $util >/dev/null 2>&1; then
        echo "ERROR: $util is not installed."
        exit 10
    fi
done

# Check if docker buildx is installed
if ! docker buildx version >/dev/null 2>&1; then
    echo "Error: docker-buildx must be installed (or podman-docker)."
    exit 255
fi

### Find current system image URL within system/hardware/tici/agnos.json

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
mkdir -p $WORKINGDIR/tmp

SYSTEMURL=$(jq -r '.[] | select(.name == "system") | .url' $BASEDIR/system/hardware/tici/agnos.json)
HASH=$(jq -r '.[] | select(.name == "system") | .hash' $BASEDIR/system/hardware/tici/agnos.json)
SYSTEMIMGXZ="tmp/$(basename $SYSTEMURL)"
SYSTEMIMG="${SYSTEMIMGXZ%.xz}"
SYSTEMRAW="${SYSTEMIMG%.img}.raw.img"

echo "SYSTEMURL=$SYSTEMURL"
echo "HASH=$HASH"

# KEEP downloaded img.xz if it already existed, or KEEP=1
if [ -f "$SYSTEMIMGXZ" ] || [ -n "$KEEP" ]; then
    KEEP=1
fi

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

# Convert to raw image
echo "Converting '$SYSTEMIMG' to raw image"
rm -f $SYSTEMRAW
simg2img "$SYSTEMIMG" "$SYSTEMRAW" || { echo "Error: Failed to convert '$SYSTEMIMG' to raw image."; exit 1; }
echo "Conversion complete. Output file: $SYSTEMRAW"

### exit upon uncaught error
set -e

### Cleanup possible leftover mounts from failed previous attempts
# quickly unmount and get rid of reference to previous tmp mount (even if it's busy), ignore errors
umount -l -q tmp/rootfs-img-mount/ >/dev/null 2>&1 || :
rm -rf tmp/rootfs-img-mount/
mkdir -p tmp/rootfs-img-mount/
echo "Mounting '$SYSTEMRAW' at tmp/rootfs-img-mount/"
mount -o loop,ro "$SYSTEMRAW" tmp/rootfs-img-mount/

echo "Building Dockerfile.agnos-system"
docker buildx build -f Dockerfile.agnos-system -t agnos-system .
echo "Unmounting tmp/rootfs-img-mount/"
umount -l tmp/rootfs-img-mount

# CLEANUP: Remove temporary agnos system mountpoint
rmdir tmp/rootfs-img-mount/ 
# CLEANUP: Remove the intermediate .img
rm -f "$SYSTEMIMG"
# CLEANUP: Remove raw.img
rm -f "$SYSTEMRAW"
# CLEANUP: Remove .img.xz
if [ -n "$KEEP" ]; then
    echo "KEEPING $SYSTEMIMGXZ"
else
    echo "Deleting $SYSTEMIMGXZ"
    rm -f "$SYSTEMIMGXZ"
fi

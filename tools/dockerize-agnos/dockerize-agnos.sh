#!/usr/bin/env bash
###
### This script requires Linux to mount and copy the ext4 AGNOS system image
###

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run as root or with sudo."
    exit 1
fi

# Check if simg2img and xz are installed
if ! command -v simg2img >/dev/null 2>&1; then
    echo "Error: simg2img is not installed."
    exit 1
fi

if ! command -v xz >/dev/null 2>&1; then
    echo "Error: xz is not installed."
    exit 1
fi

# Check if docker buildx is installed
if ! docker buildx version >/dev/null 2>&1; then
    echo "Error: docker buildx must be installed."
fi

# Check if parameter is provided
if [ -z "$1" ]; then
    echo "Error: No file parameter provided."
    exit 1
fi

# Check if file exists
if [ ! -f "$1" ]; then
    echo "Error: File '$1' does not exist."
    exit 1
fi

# Check if file name starts with "system-" and ends with ".img.xz"
if [[ ! "$1" =~ ^system-.*\.img\.xz$ ]]; then
    echo "Error: File name '$1' must start with 'system-' and end with '.img.xz'."
    exit 1
fi

# Extract intermediate and raw img filenames
systemimgxz="$1"
systemimg="${systemimgxz%.xz}"
systemrawimg="${systemimg%.img}.raw.img"

echo "Decompressing '$systemimgxz' to '$systemimg'..."
xz -d -k "$systemimgxz" || { echo "Error: Failed to decompress '$systemimgxz'."; exit 1; }
echo "Converting '$systemimg' to raw image..."
simg2img "$systemimg" "${systemimg%.img}.raw.img" || { echo "Error: Failed to convert '$systemimg' to raw image."; exit 1; }

echo "Conversion complete. Output file: $systemrawimg"

mkdir -p tmp/rootfs-img-mount/
mkdir -p tmp/rootfs-tmp-docker/
echo "Mounting '$systemrawimg' at tmp/rootfs-img-mount/"
mount -o loop,ro "$systemrawimg" tmp/rootfs-img-mount/
echo "Copying contents of tmp/rootfs-img-mount/ to tmp/rootfs-tmp-docker/"
cp -a tmp/rootfs-img-mount/. tmp/rootfs-tmp-docker/
echo "Unmounting tmp/rootfs-img-mount/"
umount tmp/rootfs-img-mount
echo "Building Dockerfile.agnos-system"
docker buildx build -f Dockerfile.agnos-system -t agnos-system .

# CLEANUP: Remove temporary agnos system mountpoint
rmdir tmp/rootfs-img-mount/ 
# CLEANUP: Remove temporary docker rootfs
rm -rf tmp/rootfs-tmp-docker/
# CLEANUP: Remove the intermediate .img
rm -f "$systemimg"
# CLEANUP: Remove raw.img
rm -f "$systemrawimg"

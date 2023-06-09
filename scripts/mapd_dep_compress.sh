#! usr/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null && pwd)"

tar -cf - -C "$DIR/third_party" mapd | xz -9zev -T0 > "$DIR/selfdrive/mapd/assets/mapd_deps.tar.xz"

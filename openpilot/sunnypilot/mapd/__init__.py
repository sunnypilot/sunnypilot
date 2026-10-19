import os
from openpilot.common.basedir import BASEDIR

MAPD_BIN_DIR = os.path.join(BASEDIR, 'openpilot', 'third_party/mapd_pfeiferj')
MAPD_PATH = os.path.join(MAPD_BIN_DIR, 'mapd')

# mapd still runs (OSM downloads) but has no position source since ubloxd owns LastGPSPosition;
# map-based features stay off until mapd is rebuilt
MAPD_AVAILABLE = True

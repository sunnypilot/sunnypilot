"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Where local mode keeps its state, and the wire constants both halves share.

Every key here is under the `SunnylinkLocal` prefix, which the cloud daemon may neither read nor
write (`local_params.py`): a phone cannot enroll, rename or unpair itself through a local session,
only through the cloud settings-write an account already has to be allowed to make.
"""
from __future__ import annotations

from openpilot.common.params import Params

SUNNYLINK_LOCAL_UDP_PORT = 53133
SUNNYLINK_LOCAL_WS_PORT = 8443

# The beacon line the phone broadcasts: `SUNNYLINK1 {"v":1,"role":"app",...}`. A locator, never a
# credential.
BEACON_PREFIX = "SUNNYLINK1"

# The enrolled phones, `{"v": 2, "grants": [...]}`, written only by the local daemon.
LOCAL_APPS_KEY = "SunnylinkLocalApps"
# Display metadata per enrolled key id: `{"v": 2, "apps": {key_id: {"alias", "last_seen"}}}`.
LOCAL_APPS_META_KEY = "SunnylinkLocalAppsMeta"

# The freshest beacon, for the settings UI to show that a phone is around.
DISCOVERED_APP_KEY = "SunnylinkLocalDiscoveredApp"
# The settings UI asks for a pairing window here; the daemon publishes the QR it minted.
PAIRING_REQUEST_KEY = "SunnylinkLocalPairingRequest"
PAIRING_QR_KEY = "SunnylinkLocalPairingQr"
# The settings UI asks the daemon to drop one phone (key id) or all of them.
REVOKE_KEY = "SunnylinkLocalRevoke"
REVOKE_ALL_KEY = "SunnylinkLocalRevokeAll"


def is_locally_paired(params: Params | None = None) -> bool:
  """True once this device has at least one enrolled phone.

  Reads the registry rather than the authority: `sunnylinkd` asks this at startup and the device UI
  renders it continuously, and neither may build a second authority in its own process.
  """
  params = params or Params()
  return bool(params.get(LOCAL_APPS_KEY))


def format_endpoint(host: str, ws_port: int = SUNNYLINK_LOCAL_WS_PORT) -> str:
  return f"ws://{host}:{ws_port}"

"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Keep these tests out of the device's real params.

Some of them exercise code that clears params. On the comma that is the live
directory: a suite run cleared JetlinkEngineReady once and left the device on
the small model with nothing reported, because ready() is params-only.
params.cc reads OPENPILOT_PREFIX on every Params(), so setting it before any
test module is imported covers the whole subtree.
"""
from openpilot.common.prefix import OpenpilotPrefix

# a prefix isolates Params and msgq; the environment alone left the msgq
# directory absent on AGNOS and broke any test using a real SubMaster
_prefix = OpenpilotPrefix()
_prefix.__enter__()


def pytest_sessionfinish(session, exitstatus):
  _prefix.__exit__(None, None, None)

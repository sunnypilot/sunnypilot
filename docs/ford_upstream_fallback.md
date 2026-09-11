# Ford toggle-off upstream restoration

`FordModelActionController` is the only setting that can select custom Ford
steering. It defaults false. With it false or absent, no custom path controller
is created and normal lateral-control curvature passes unchanged to the Ford
sender. A stored `FordPscmObserver` or retired virtual-angle setting cannot
override that choice. The observer toggle is removed from Sunnylink; its stored
parameter remains readable for compatibility but has no selection effect.

Selection remains fixed for the lifetime of controlsd. Sunnylink changes require
a real offroad-to-onroad cycle, as before. The startup diagnostic reports
`controller=upstream` when the experiment is not selected.

## Sender behavior

The new `fordLateralPath.enabled` field conveys startup selection independently
of `valid`. Its default is false. The sender uses custom mode only when this
field is true on a Ford CAN FD vehicle. This prevents invalid model geometry
or disengagement in the selected experiment from choosing a different controller.

Toggle-off restores the upstream Ford sender:

- 20 Hz steering messages on both CAN FD and legacy Ford.
- CAN FD limited mode 1 while active, mode 0 while inactive, with upstream ramp
  type 0, counters and checksums.
- C0, C1 and C3 zero; C2 follows upstream actuator curvature.
- Upstream curvature amplitude/rate limits and the measured-curvature error
  clamp above 9 m/s.
- Upstream anti-overshoot handling for Bronco Sport and F-150 MK14.

The reference is the upstream implementation already merged into this branch,
opendbc `f95f996f5917dcbbf2e32fe51b606a24cf836af6`. Its Ford sender differs from
the locally available comma opendbc `3e92d112129507debe45364891954db70238997a`
only in sunnypilot's additional `CP_SP`/`CC_SP` interface arguments. This change
restores that implementation; it does not upgrade unrelated upstream code.

Toggle-on retains the previous custom 100 Hz sender, mode 2, ramp type 3 and
existing path limits. The model-action controller's command law and diagnostic
identity `model-action-c1-feedback-v3` are unchanged. Legacy Ford always uses
upstream control. The opendbc dependency is now
`64aa61b9b3fd26e70a7caa915acab207ff3cd64a`. No Panda safety code is changed;
its existing limited-mode checks already use 20 Hz curvature limits.

## Validation

- Combined Ford, Sunnylink, parameter, logging, replay-tool and Ford safety
  suite: **683 passed, 178 existing skips, 9,145 subtests passed**.
- Real startup → controlsd → Float32 publication → conversion → Ford sender:
  14 new toggle-off cases, covering all six CAN FD platforms plus legacy
  Escape, with both stored observer settings. They preserve the upstream
  actuator output, including when custom model geometry is missing, and verify
  20 Hz cadence, engage/disengage/reengage, zero path terms, mode, ramp,
  counters and checksums across 4,200 control cycles / 840 steering messages.
- The existing toggle-on, stale-input, invalid-input and 100 Hz integration
  regressions continue to pass.
- Additional Ford interface fuzz checks: **11 passed**, 60 generated examples
  each, with real Cap'n Proto conversion and car-interface application. The
  initially missing neural-network-data dependency was initialized at the
  repository's existing pin `03cac2d30e111e0689c0429cb8c1fe6cb5a905af`.
- Packet equivalence: **55,000 toggle-off cycles across all 11 Ford platforms**
  match the pinned upstream sender exactly. **30,000 toggle-on cycles across
  six CAN FD platforms** match the previous custom sender exactly. All 90,305
  outgoing packets and returned actuator values match, including invalid paths,
  inactive periods, both turn directions and speed boundaries. Disabled
  selection also ignores deliberately nonzero, valid custom path fields.
- Ruff, controller type check, generated Sunnylink schema check and diff
  whitespace checks pass.

The packet comparison loads the exact old controller **and its old CAN builder**
from trusted local Git sources. It does not compare two aliases of the modified
code. Results and source hashes are in `ford_upstream_fallback_validation.json`.
No device build, boot or physical steering validation is claimed.

## Reproduction

Use the pinned opendbc dependency and native project dependencies:

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
python -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/sunnypilot/sunnylink/tests openpilot/common/tests/test_params.py opendbc_repo/opendbc/car/ford/tests/test_ford.py opendbc_repo/opendbc/safety/tests/test_ford.py
FUZZ_SEED=20260911 python -m pytest -q -p no:cacheprovider openpilot/selfdrive/car/tests/test_car_interfaces.py -k FORD
python -m tools.ford_pscm_lab.upstream_fallback_check --cycles 5000 --output .cache/ford_upstream_fallback/equivalence.json
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
```

The comparison requires both pinned baseline commits in the local opendbc Git
object store. The previous overflow/replay records describe their historical
source hashes; the comparison here establishes unchanged toggle-on sender output.

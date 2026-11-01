"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import os

SUNNYPILOT_CAR_SEGMENTS_REPO = os.environ.get("SUNNYPILOT_CAR_SEGMENTS_REPO",
                                               "https://huggingface.co/datasets/sunnypilot/sunnypilotCarSegments")
SUNNYPILOT_CAR_SEGMENTS_BRANCH = os.environ.get("SUNNYPILOT_CAR_SEGMENTS_BRANCH", "main")


def get_url(route, segment, file="rlog.zst"):
  return f"{SUNNYPILOT_CAR_SEGMENTS_REPO}/resolve/{SUNNYPILOT_CAR_SEGMENTS_BRANCH}/segments/{route.replace('|', '/')}/{segment}/{file}"


def sunnypilot_car_segments_source(sr, seg_idxs, fns, /):
  from openpilot.tools.lib.file_sources import eval_source
  return eval_source({seg: [get_url(sr.route_name, seg, fn) for fn in fns] for seg in seg_idxs})

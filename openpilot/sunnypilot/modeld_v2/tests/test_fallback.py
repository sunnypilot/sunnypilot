"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import io

from openpilot.common.hardware import hw
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.modeld.helpers import dump_oob
import openpilot.sunnypilot.modeld_v2.modeld as modeld_module
from openpilot.sunnypilot.modeld_v2.tests import helpers as tests_helpers
from openpilot.sunnypilot.modeld_v2.tests.helpers import DummyModel, DummyBundle, CAM_W, CAM_H
from openpilot.sunnypilot.models.fetcher import ModelParser
from openpilot.sunnypilot.models.helpers import REQUIRED_JSON_VERSION

tmp_path = tests_helpers.tmp_path


def manifest_bundle(short_name: str, file_name: str, is_big: bool) -> dict:
  """A whole-file manifest bundle as the fetcher parses it from driving_models_*.json."""
  return {
    "index": 0,
    "short_name": short_name,
    "display_name": short_name,
    "generation": 1,
    "environment": "release",
    "runner": "tinygrad",
    "is_big": is_big,
    "minimum_selector_version": str(REQUIRED_JSON_VERSION),
    "ref": short_name,
    "overrides": {"lat": ".1", "long": ".3"},
    "models": [{
      "type": "supercombo",
      "artifact": {"file_name": file_name, "download_uri": {"url": f"https://example.com/{file_name}", "sha256": "s"}},
    }],
  }


class TestFallback(OpenpilotTestCase):
  def test_find_dual_model_in_bundle(self, tmp_path, monkeypatch):
    lebowski_file = 'driving_lebowski.pkl'
    tsfdo_file = 'driving_tsfdo.pkl'
    (tmp_path / lebowski_file).write_bytes(b'fkasdjfkljf')
    (tmp_path / tsfdo_file).write_bytes(b'dskfajklsdjlsfka')

    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    big_bundle = DummyBundle(models=[DummyModel('supercombo', lebowski_file)])
    small_bundle = DummyBundle(models=[DummyModel('supercombo', tsfdo_file)])
    big_pkl = modeld_module._find_driving_pkl(big_bundle)
    small_pkl = modeld_module._find_driving_pkl(small_bundle)

    assert big_pkl is not None and lebowski_file in big_pkl
    assert small_pkl is not None and tsfdo_file in small_pkl

  def test_download_models_and_init_modelstate_fallback(self, tmp_path, monkeypatch):
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    big_bundle = ModelParser.parse_models({"bundles": [manifest_bundle("big", "big_driving_test_tinygrad.pkl", True)]})[0]
    small_bundle = ModelParser.parse_models({"bundles": [manifest_bundle("small", "driving_test_tinygrad.pkl", False)]})[0]

    buf = io.BytesIO()
    dump_oob(tests_helpers.make_pkl_data(tests_helpers.ARCHETYPES['supercombo_non20hz']), buf)
    oob_bytes = buf.getvalue()

    for bundle in (big_bundle, small_bundle):
      (tmp_path / bundle.models[0].artifact.fileName).write_bytes(oob_bytes)

    monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None, *, chestnut=None: small_bundle)
    assert modeld_module.ModelState(CAM_W, CAM_H, chestnut=False).chestnut is False

    monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None, *, chestnut=None: big_bundle)
    try:
      assert modeld_module.ModelState(CAM_W, CAM_H, chestnut=True).chestnut is True
    except Exception as e:
      assert "AMD" in str(e) or "device" in str(e).lower()

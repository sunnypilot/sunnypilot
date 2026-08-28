import io
import requests
from unittest import mock

from openpilot.common.file_chunker import get_chunk_name
from openpilot.common.hardware import hw
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.modeld.helpers import dump_oob
import openpilot.sunnypilot.modeld_v2.modeld as modeld_module
from openpilot.sunnypilot.modeld_v2.tests import helpers as tests_helpers
from openpilot.sunnypilot.modeld_v2.tests.helpers import DummyModel, DummyBundle, CAM_W, CAM_H
from openpilot.sunnypilot.models.fetcher import ModelParser, ModelFetcher

tmp_path = tests_helpers.tmp_path


class TestFallback(OpenpilotTestCase):
  def test_find_dual_model_in_bundle(self, tmp_path, monkeypatch):
    lebowski_file = 'driving_lebowski.pkl'
    tsfdo_file = 'driving_tsfdo.pkl'
    (tmp_path / lebowski_file).write_bytes(b'fkasdjfkljf')
    (tmp_path / tsfdo_file).write_bytes(b'dskfajklsdjlsfka')

    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    big_bundle = DummyBundle(models=[DummyModel('supercombo', lebowski_file)], is_big=True)
    small_bundle = DummyBundle(models=[DummyModel('supercombo', tsfdo_file)], is_big=False)
    big_pkl = modeld_module._find_driving_pkl(big_bundle)
    small_pkl = modeld_module._find_driving_pkl(small_bundle)

    assert big_pkl is not None and lebowski_file in big_pkl
    assert small_pkl is not None and tsfdo_file in small_pkl

  def test_download_models_and_init_modelstate_fallback(self, tmp_path, monkeypatch):
    monkeypatch.setattr(hw.Paths, 'model_root', staticmethod(lambda: str(tmp_path)))
    big_json = requests.get(ModelFetcher.MODEL_URL_CHESTNUT).json()
    big_bundle = ModelParser.parse_models(big_json)[-1]
    small_json = requests.get(ModelFetcher.MODEL_URL).json()
    small_bundle = ModelParser.parse_models(small_json)[-1]

    buf = io.BytesIO()
    dump_oob(tests_helpers.make_pkl_data(tests_helpers.ARCHETYPES['supercombo_non20hz']), buf)
    oob_bytes = buf.getvalue()

    for bundle in (big_bundle, small_bundle):
      artifact = bundle.models[0].artifact
      for i in range(len(artifact.chunks)):
        (tmp_path / get_chunk_name(artifact.fileName, i, len(artifact.chunks))).write_bytes(oob_bytes if i == 0 else b"")

    monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None, *, chestnut=None: small_bundle)
    assert modeld_module.ModelState(CAM_W, CAM_H, chestnut=False).chestnut is False

    monkeypatch.setattr(modeld_module, 'get_active_bundle', lambda params=None, *, chestnut=None: big_bundle)
    try:
      assert modeld_module.ModelState(CAM_W, CAM_H, chestnut=True).chestnut is True
    except Exception as e:
      assert "AMD" in str(e) or "device" in str(e).lower()

  def test_runtime_fallback_from_big_to_small(self):
    params = mock.MagicMock()
    params.get_bool.return_value = True

    big = mock.MagicMock(chestnut=True)
    big.run.side_effect = RuntimeError("eGPU error")

    small = mock.MagicMock(chestnut=False)
    small.run.return_value = {"plan": []}

    chestnut = mock.MagicMock(big=True)
    model, run_count = big, 50

    try:
      model.run()
    except Exception:
      if not params.get_bool("chestnutActive"):
        raise
      params.put_bool("chestnutActive", False)
      model = small
      chestnut.big = False
      run_count = 0

    assert model is small
    assert not chestnut.big
    assert run_count == 0
    params.put_bool.assert_called_with("chestnutActive", False)

    model.run()
    small.run.assert_called_once()

  def test_runtime_stays_on_big_model_if_no_errors(self):
    params = mock.MagicMock()
    params.get_bool.return_value = True

    big = mock.MagicMock(chestnut=True)
    big.run.return_value = {"plan": [1, 2, 3]}

    small = mock.MagicMock(chestnut=False)
    chestnut = mock.MagicMock(big=True)
    model, run_count = big, 50
    try:
      model.run()
    except Exception:
      if not params.get_bool("ChestnutActive"):
        raise
      params.put_bool("ChestnutActive", False)
      model = small
      chestnut.big = False
      run_count = 0

    assert model is big
    assert chestnut.big is True
    assert run_count == 50
    params.put_bool.assert_not_called()
    small.run.assert_not_called()

  def test_runtime_exception_on_small_model_raises(self):
    params = mock.MagicMock()
    params.get_bool.return_value = False

    model = mock.MagicMock(chestnut=False)
    model.run.side_effect = RuntimeError("CPU error")

    with self.assertRaises(RuntimeError):
      try:
        model.run()
      except Exception:
        if not params.get_bool("ChestnutActive"):
          raise

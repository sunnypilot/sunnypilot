"""Filtered registry names must remain distinct across the C/Python boundary."""
import tempfile
import unittest

from openpilot.common import params as native


class TestParamsFlagBuffers(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.params = native.Params(self.directory.name)

  def tearDown(self):
    self.params._finalizer()
    self.directory.cleanup()

  def test_filtered_names_are_unique_registered_keys(self):
    all_keys = set(self.params.all_keys())
    for flag in (native.ParamKeyFlag.BACKUP, native.ParamKeyFlag.CLEAR_ON_MANAGER_START, native.ParamKeyFlag.CLEAR_ON_ONROAD_TRANSITION):
      names = self.params.all_keys(flag)
      self.assertEqual(len(names), len(set(names)))
      self.assertTrue(set(names) <= all_keys)
    backup = set(self.params.all_keys(native.ParamKeyFlag.BACKUP))
    self.assertTrue({b'MapboxNextTurnEnabled', b'MapboxTurnLeadDistance'} <= backup)
    self.assertTrue({b'MapboxTurnIntent', b'MapboxTurnContext', b'MapboxTurnCue'}.isdisjoint(backup))

  def test_each_output_buffer_survives_another_c_api_string_result(self):
    expected = self.params.all_keys(native.ParamKeyFlag.BACKUP)
    output = (native.ParamsBuffer*1024)()
    count = native.params_keys_by_flag(self.params.p, int(native.ParamKeyFlag.BACKUP), output, len(output))
    native.params_get_default(self.params.p, b'LongitudinalPersonality')
    self.assertEqual([native._copy_string(output[i]) for i in range(count)], expected)

  def test_small_output_array_still_reports_total_matching_key_count(self):
    expected = self.params.all_keys(native.ParamKeyFlag.BACKUP)
    output = (native.ParamsBuffer*2)()
    count = native.params_keys_by_flag(self.params.p, int(native.ParamKeyFlag.BACKUP), output, len(output))
    self.assertEqual(count, len(expected))
    self.assertEqual([native._copy_string(output[i]) for i in range(len(output))], expected[:len(output)])


if __name__ == '__main__':
  unittest.main()

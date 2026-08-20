import unittest
from types import SimpleNamespace

from opendbc.car import structs
from opendbc.car.toyota.carcontroller import get_long_tune
from opendbc.car.toyota.values import CAR, ToyotaFlags
from opendbc.sunnypilot.car.interfaces import _initialize_toyota
from opendbc.sunnypilot.car.toyota.values import ToyotaFlagsSP


def build_params(*, tss2=True):
  flags = ToyotaFlags.TSS2.value if tss2 else 0
  CP = structs.CarParams(
    brand="toyota",
    carFingerprint=str(CAR.TOYOTA_COROLLA_TSS2),
    flags=flags,
  )
  return CP, structs.CarParamsSP()


class TestTss2LongTuning(unittest.TestCase):
  def test_param_handoff(self):
    for enabled in (False, True):
      with self.subTest(enabled=enabled):
        CP, CP_SP = build_params()
        _initialize_toyota(CP, CP_SP, {"ToyotaTSS2Long": int(enabled)})
        self.assertEqual(bool(CP_SP.flags & ToyotaFlagsSP.TSS2_LONG_TUNING), enabled)

  def test_tss2_tune_selection(self):
    controller_params = SimpleNamespace(ACCEL_MAX=2.0, ACCEL_MIN=-3.5)
    CP, CP_SP = build_params()

    stock_tune = get_long_tune(CP, CP_SP, controller_params)
    stock_tune.speed = 2.0
    self.assertEqual(stock_tune.k_i, 0.5)
    stock_tune.speed = 5.0
    self.assertEqual(stock_tune.k_i, 0.25)

    CP_SP.flags |= ToyotaFlagsSP.TSS2_LONG_TUNING.value
    custom_tune = get_long_tune(CP, CP_SP, controller_params)
    custom_tune.speed = 0.0
    self.assertEqual(custom_tune.k_i, 0.30)
    custom_tune.speed = 5.0
    self.assertEqual(custom_tune.k_i, 0.28)

  def test_non_tss2_ignores_custom_tune_flag(self):
    controller_params = SimpleNamespace(ACCEL_MAX=2.0, ACCEL_MIN=-3.5)
    CP, CP_SP = build_params(tss2=False)
    CP_SP.flags |= ToyotaFlagsSP.TSS2_LONG_TUNING.value

    standard_tune = get_long_tune(CP, CP_SP, controller_params)
    standard_tune.speed = 0.0
    self.assertEqual(standard_tune.k_i, 3.6)


if __name__ == "__main__":
  unittest.main()

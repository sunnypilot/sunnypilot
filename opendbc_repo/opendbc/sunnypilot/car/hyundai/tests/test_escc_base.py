import unittest

from opendbc.sunnypilot.car.hyundai.escc import EnhancedSmartCruiseControl, ESCC_MSG
from opendbc.car.hyundai.carstate import CarState
from opendbc.car import structs
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP


class TestEscc(unittest.TestCase):
  def _make_car_params(self):
    params = structs.CarParams()
    params.carFingerprint = "HYUNDAI_SONATA"
    return params

  def _make_car_params_sp(self):
    params = structs.CarParamsSP()
    params.flags = HyundaiFlagsSP.ENHANCED_SCC
    return params

  def _make_escc(self):
    return EnhancedSmartCruiseControl(self._make_car_params(), self._make_car_params_sp())

  def test_escc_msg_id(self):
    escc = self._make_escc()
    self.assertEqual(escc.trigger_msg, ESCC_MSG)

  def test_enabled_flag(self):
    car_params = self._make_car_params()
    for value in range(256):
      with self.subTest(flags=value):
        car_params_sp = structs.CarParamsSP()
        car_params_sp.flags = value
        escc = EnhancedSmartCruiseControl(car_params, car_params_sp)
        self.assertEqual(escc.enabled, bool(value & HyundaiFlagsSP.ENHANCED_SCC))

  def test_update_car_state(self):
    car_params = self._make_car_params()
    car_params_sp = self._make_car_params_sp()
    escc = EnhancedSmartCruiseControl(car_params, car_params_sp)
    car_state = CarState(car_params, car_params_sp)
    car_state.escc_cmd_act = 1
    car_state.escc_aeb_warning = 1
    car_state.escc_aeb_dec_cmd_act = 1
    car_state.escc_aeb_dec_cmd = 1
    escc.update_car_state(car_state)
    self.assertEqual(escc.car_state, car_state)

  def test_update_scc12(self):
    car_params = self._make_car_params()
    car_params_sp = self._make_car_params_sp()
    escc = EnhancedSmartCruiseControl(car_params, car_params_sp)
    car_state = CarState(car_params, car_params_sp)
    car_state.escc_cmd_act = 1
    car_state.escc_aeb_warning = 1
    car_state.escc_aeb_dec_cmd_act = 1
    car_state.escc_aeb_dec_cmd = 1
    escc.update_car_state(car_state)
    scc12_message = {}
    escc.update_scc12(scc12_message)
    self.assertEqual(scc12_message["AEB_CmdAct"], 1)
    self.assertEqual(scc12_message["CF_VSM_Warn"], 1)
    self.assertEqual(scc12_message["CF_VSM_DecCmdAct"], 1)
    self.assertEqual(scc12_message["CR_VSM_DecCmd"], 1)
    self.assertEqual(scc12_message["AEB_Status"], 2)

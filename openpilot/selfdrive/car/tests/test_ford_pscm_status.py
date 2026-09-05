import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpilot.cereal import custom
from openpilot.selfdrive.car.ford_pscm_status import MESSAGE, SIGNALS, populate_ford_pscm_status
from openpilot.selfdrive.car.helpers import convert_to_capnp
from opendbc.can import CANPacker, CANParser
from opendbc.car import Bus, structs
from opendbc.car.ford.values import FordFlags


class TestFordPscmStatus(unittest.TestCase):
  def setUp(self):
    self.cp = SimpleNamespace(brand='ford', flags=FordFlags.CANFD)
    self.packer = CANPacker('ford_lincoln_base_pt')
    self.parser = CANParser('ford_lincoln_base_pt', [(MESSAGE, 33), ('Yaw_Data_FD1', 100)], 0)

  def update_status(self, timestamp, *, lateral_state=2, limit=0, capability=2, denied=False):
    status = self.packer.make_can_msg(MESSAGE, 0, dict(zip(SIGNALS, (lateral_state, limit, capability, denied), strict=True)))
    yaw = self.packer.make_can_msg('Yaw_Data_FD1', 0, {'VehYaw_W_Actl': 0.1})
    self.parser.update([(timestamp, [status, yaw])])

  def publish(self, *, can_valid=True):
    state_sp = convert_to_capnp(structs.CarStateSP(speedLimit=13.5))
    populate_ford_pscm_status(self.cp, {Bus.pt: self.parser}, state_sp, can_valid)
    return state_sp

  def test_decodes_status_and_preserves_receipt_time_across_other_can_messages(self):
    self.update_status(1_000_000_000, limit=2, capability=1, denied=True)
    original = self.publish()
    self.assertEqual(original.speedLimit, 13.5)
    status = original.fordPscmStatus
    self.assertTrue(status.valid)
    self.assertEqual(status.canMonoTime, 1_000_000_000)
    self.assertEqual((status.lateralState, status.limit, status.capability, status.denied), (2, 2, 1, True))

    # carStateSP may publish at 100 Hz while this 33 Hz message is absent. New
    # unrelated CAN must not freshen the timestamp of an old PSCM status.
    yaw = self.packer.make_can_msg('Yaw_Data_FD1', 0, {'VehYaw_W_Actl': .2})
    self.parser.update([(1_080_000_000, [yaw])])
    copied = self.publish().fordPscmStatus
    self.assertEqual(copied.canMonoTime, 1_000_000_000)
    self.assertEqual((copied.limit, copied.capability, copied.denied), (2, 1, True))

    self.update_status(1_090_000_000, lateral_state=3, limit=3, capability=2)
    next_state = self.publish()
    with custom.CarStateSP.from_bytes(next_state.to_bytes()) as decoded:
      latest = decoded.fordPscmStatus
      self.assertTrue(latest.valid)
      self.assertEqual(latest.canMonoTime, 1_090_000_000)
      self.assertEqual((latest.lateralState, latest.limit, latest.capability, latest.denied), (3, 3, 2, False))

  def test_absent_parser_unseen_message_and_invalid_can_do_not_claim_valid_status(self):
    state = custom.CarStateSP.new_message()
    populate_ford_pscm_status(self.cp, {}, state, True)
    self.assertFalse(state.fordPscmStatus.valid)
    self.assertEqual(state.fordPscmStatus.canMonoTime, 0)
    self.assertFalse(self.publish().fordPscmStatus.valid)
    self.update_status(1_000_000_000)
    invalid = self.publish(can_valid=False).fordPscmStatus
    self.assertFalse(invalid.valid)
    self.assertEqual(invalid.canMonoTime, 1_000_000_000)

  def test_mixed_timestamps_or_malformed_status_cannot_enable_feedback(self):
    self.update_status(1_000_000_000)
    self.parser.ts_nanos[MESSAGE][SIGNALS[-1]] = 990_000_000
    self.assertFalse(self.publish().fordPscmStatus.valid)
    self.parser.ts_nanos[MESSAGE][SIGNALS[-1]] = 1_000_000_000
    for value in (float('nan'), -1, 1.5, 4):
      self.parser.vl[MESSAGE]['LatCtlLim_D_Stat'] = value
      self.assertFalse(self.publish().fordPscmStatus.valid)

  def test_other_vehicles_and_legacy_messages_default_to_unavailable(self):
    for cp in (SimpleNamespace(brand='toyota'), SimpleNamespace(brand='ford', flags=0)):
      state = custom.CarStateSP.new_message(speedLimit=10.)
      populate_ford_pscm_status(cp, {}, state, True)
      self.assertFalse(state.fordPscmStatus.valid)
      self.assertEqual(state.fordPscmStatus.canMonoTime, 0)
      self.assertEqual(state.speedLimit, 10.)
    # Old recordings/readers have no appended status pointer; defaults must
    # remain unavailable rather than interpreting zeroed enums as fresh data.
    self.assertFalse(custom.CarStateSP.new_message().fordPscmStatus.valid)

  def test_actual_card_update_populates_status_after_dataclass_conversion(self):
    self.update_status(1_000_000_000, limit=1)
    source_path = Path(__file__).resolve().parents[1] / 'card.py'
    source = ast.parse(source_path.read_text())
    car_class = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == 'Car')
    method = next(n for n in car_class.body if isinstance(n, ast.FunctionDef) and n.name == 'state_update')
    statements = method.body
    first = next(i for i, n in enumerate(statements) if isinstance(n, ast.Assign) and ast.unparse(n.value) == 'self.CI.update(can_list)')
    last = next(i for i, n in enumerate(statements) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                and isinstance(n.value.func, ast.Name) and n.value.func.id == 'populate_ford_pscm_status')
    self.assertGreater(last, first)
    code = compile(ast.Module(body=statements[first:last + 1], type_ignores=[]), str(source_path), 'exec')
    ci = SimpleNamespace(update=lambda _: (SimpleNamespace(canValid=True), structs.CarStateSP(speedLimit=11.)),
                         can_parsers={Bus.pt: self.parser})
    environment = {'self': SimpleNamespace(CP=self.cp, CI=ci), 'can_list': [], 'convert_to_capnp': convert_to_capnp,
                   'populate_ford_pscm_status': populate_ford_pscm_status}
    exec(code, environment)
    self.assertTrue(environment['CS_SP'].fordPscmStatus.valid)
    self.assertEqual(environment['CS_SP'].fordPscmStatus.canMonoTime, 1_000_000_000)
    self.assertEqual(environment['CS_SP'].fordPscmStatus.limit, 1)


if __name__ == '__main__':
  unittest.main()

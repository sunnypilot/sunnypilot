import math
import unittest
from types import SimpleNamespace as NS
from unittest.mock import mock_open, patch

from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.automatic_set import (
  AutomaticSet, StableMapLimit, auto_supported, fresh_message, read_map_evidence, resolve_auto_map,
)


class MapMessages:
  def __init__(self, now, limit):
    self.data = {'gpsLocationExternal': NS(hasFix=True), 'liveMapDataSP': NS(speedLimitValid=True, speedLimit=limit)}
    self.seen = dict.fromkeys(self.data, True)
    self.valid = dict.fromkeys(self.data, True)
    self.logMonoTime = dict.fromkeys(self.data, round(now * 1e9))

  def __getitem__(self, topic):
    return self.data[topic]


class TestAutomaticSet(unittest.TestCase):
  def setUp(self):
    self.auto = AutomaticSet()
    self.options = {'selected': True, 'supported': True, 'enabled': True, 'available': True, 'control_ok': True,
                    'pedal': False, 'manual_event': False, 'manual_press': False, 'cancel': False, 'held': False,
                    'target': 80., 'current': 50., 'minimum': 30.}

  def tick(self, now, **options):
    return self.auto.update(now=now, **(self.options | options))

  def arm(self):
    self.assertIsNone(self.tick(100.))
    self.assertIsNone(self.tick(100.1))
    return self.tick(100.7)

  def test_set_changes_after_quiet_period(self):
    self.assertEqual(self.arm(), 80.)
    self.assertEqual(self.tick(100.8, target=40.), 40.)

  def test_raw_target_below_minimum_is_not_rounded_up(self):
    self.arm()
    self.assertIsNone(self.tick(101., target=30.3 * 0.99))
    self.assertIsNone(self.tick(101., target=math.nextafter(30., 0.)))
    self.assertEqual(self.tick(101., target=30.), 30.)

  def test_nonfinite_and_out_of_range_targets(self):
    self.arm()
    for target in (math.nan, math.inf, -math.inf, -1., 0., 20., 145.01):
      with self.subTest(target=target):
        self.assertIsNone(self.tick(101., target=target))
    self.assertIsNone(self.tick(101., current=255.))
    self.assertIsNone(self.tick(101., minimum=math.nan))
    self.assertEqual(self.tick(101., target=145.), 145.)

  def test_manual_priority_and_new_engagement(self):
    for event in ('manual_event', 'manual_press', 'cancel', 'pedal'):
      with self.subTest(event=event):
        self.setUp()
        self.arm()
        self.assertIsNone(self.tick(101., **{event: True}))
        self.assertIsNone(self.tick(102.))
        self.assertIsNone(self.tick(103., enabled=False))
        self.assertIsNone(self.tick(104.))
        self.assertIsNone(self.tick(104.1))
        self.assertEqual(self.tick(104.7), 80.)

  def test_guards_and_no_automatic_engagement(self):
    self.arm()
    for options in ({'enabled': False}, {'selected': False}, {'supported': False}, {'available': False},
                    {'control_ok': False}, {'target': None}, {'held': True}):
      with self.subTest(options=options):
        self.setUp()
        self.arm()
        self.assertIsNone(self.tick(101., **options))

  def test_platform_scope(self):
    values = {'brand': 'honda', 'carFingerprint': 'HONDA_CITY_7G', 'openpilotLongitudinalControl': True,
              'pcmCruise': False, 'dashcamOnly': False, 'passive': False}
    self.assertTrue(auto_supported(NS(**values)))
    for brand in ('honda', 'toyota', 'hyundai', 'subaru', 'ford', 'volkswagen'):
      with self.subTest(brand=brand):
        self.assertTrue(auto_supported(NS(**(values | {'brand': brand, 'carFingerprint': 'SYNTHETIC_NON_PCM'}))))
    for change in ({'openpilotLongitudinalControl': False},
                   {'pcmCruise': True}, {'dashcamOnly': True}, {'passive': True}):
      with self.subTest(change=change):
        self.assertFalse(auto_supported(NS(**(values | change))))


class TestMapEvidence(unittest.TestCase):
  def resolve(self, now, *, token=None, limit=50 / 3.6, offset_type=0, offset=0, metric=True, valid=True):
    messages = MapMessages(now, limit)
    evidence = {'version': 1, 'valid': valid, 'position': {'logMonoTime': round(now * 1e9) if token is None else token},
                'speedLimit': limit}
    return resolve_auto_map(self.stable, messages, 'gpsLocationExternal', now, offset_type, offset, metric, evidence)

  def setUp(self):
    self.stable = StableMapLimit()

  def test_repeated_token_does_not_establish_stability(self):
    for now in (100., 101., 102., 103., 104.):
      self.assertIsNone(self.resolve(now, token=100_000_000_000))
    self.assertIsNone(self.resolve(105.))
    self.assertAlmostEqual(self.resolve(107.), 50 / 3.6)

  def test_new_limit_and_configuration_require_new_stability(self):
    self.assertIsNone(self.resolve(100.))
    self.assertAlmostEqual(self.resolve(102.), 50 / 3.6)
    self.assertIsNone(self.resolve(103., limit=80 / 3.6))
    self.assertAlmostEqual(self.resolve(105., limit=80 / 3.6), 80 / 3.6)
    self.assertIsNone(self.resolve(106., limit=80 / 3.6, offset_type=2, offset=-10))
    self.assertAlmostEqual(self.resolve(108., limit=80 / 3.6, offset_type=2, offset=-10), 72 / 3.6)

  def test_offset_units(self):
    for kind, value, metric, expected in ((0, -10, True, 50 / 3.6), (1, -5, True, 45 / 3.6),
                                          (1, -5, False, 50 / 3.6 - 5 * 0.44704), (2, -10, True, 45 / 3.6)):
      with self.subTest(kind=kind, metric=metric):
        self.setUp()
        self.assertIsNone(self.resolve(100., offset_type=kind, offset=value, metric=metric))
        self.assertAlmostEqual(self.resolve(102., offset_type=kind, offset=value, metric=metric), expected)

  def test_float32_envelope_keeps_precise_minimum_from_producer(self):
    for now in (100., 102.):
      messages = MapMessages(now, 8.333333015441895)
      evidence = {'version': 1, 'valid': True, 'position': {'logMonoTime': round(now * 1e9)}, 'speedLimit': 30 / 3.6}
      target = resolve_auto_map(self.stable, messages, 'gpsLocationExternal', now, 0, 0, True, evidence)
    self.assertGreaterEqual(target * 3.6, 30.)

  def test_stale_future_regressive_and_invalid_evidence(self):
    self.resolve(100.)
    self.assertIsNone(self.resolve(102., token=102_000_000_001))
    self.assertIsNone(self.resolve(106., token=102_000_000_000))
    self.assertIsNone(self.resolve(107., valid=False))
    self.assertIsNone(self.resolve(108.))
    self.assertIsNone(self.resolve(109., token=107_500_000_000))
    self.assertAlmostEqual(self.resolve(111.), 50 / 3.6)

  def test_explicit_invalid_proof_restarts_active_stability(self):
    self.assertIsNone(self.resolve(100.))
    self.assertIsNone(self.resolve(101.))
    self.assertIsNone(self.resolve(101.5, valid=False))
    self.assertIsNone(self.stable.candidate)
    self.assertEqual(self.stable.first_stamp, 0)
    self.assertIsNone(self.resolve(102.))
    self.assertEqual(self.stable.first_stamp, 102_000_000_000)
    self.assertIsNone(self.resolve(103.9))
    self.assertAlmostEqual(self.resolve(104.), 50 / 3.6)

  def test_evidence_read_errors_are_unavailable_input(self):
    with patch('builtins.open', side_effect=OSError('unavailable')):
      self.assertIsNone(read_map_evidence())
    with patch('builtins.open', mock_open(read_data=b'invalid json')):
      self.assertIsNone(read_map_evidence())
    with patch('builtins.open', mock_open(read_data=b'{}')), patch(
      'openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.automatic_set.json.loads',
      side_effect=RecursionError('excessive JSON nesting'),
    ):
      self.assertIsNone(read_map_evidence())

  def test_missing_proof_mismatched_limit_and_bad_messages(self):
    messages = MapMessages(100., 50 / 3.6)
    for evidence in (None, {}, {'version': 1, 'valid': True, 'position': {'logMonoTime': 100_000_000_000}, 'speedLimit': 80 / 3.6},
                     {'version': 1, 'valid': False, 'position': {'logMonoTime': 100_000_000_000}, 'speedLimit': None},
                     {'version': 1, 'valid': False, 'position': {'logMonoTime': 100_000_000_000}, 'speedLimit': 'bad'}):
      with self.subTest(evidence=evidence):
        self.assertIsNone(resolve_auto_map(self.stable, messages, 'gpsLocationExternal', 100., 0, 0, True, evidence))
    for topic in messages.data:
      messages.valid[topic] = False
      self.assertFalse(fresh_message(messages, topic, 100., 3))
    messages = MapMessages(100., 50 / 3.6)
    self.assertTrue(fresh_message(messages, 'liveMapDataSP', 103., 3))
    self.assertFalse(fresh_message(messages, 'liveMapDataSP', 103.000000001, 3))


if __name__ == '__main__':
  unittest.main()

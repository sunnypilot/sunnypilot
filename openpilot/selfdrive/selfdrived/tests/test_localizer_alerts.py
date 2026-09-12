import collections

from opendbc.car.structs import car

from openpilot.cereal import log, messaging
from openpilot.common.test import OpenpilotTestCase
from openpilot.common.params import Params
from openpilot.selfdrive.locationd.helpers import PoseCalibrator
from openpilot.selfdrive.selfdrived.events import Events
from openpilot.selfdrive.selfdrived.helpers import ExcessiveActuationCheck
from openpilot.selfdrive.selfdrived.selfdrived import SelfdriveD
from openpilot.sunnypilot.selfdrive.selfdrived.accelerator_events import AcceleratorEvents
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventName = log.OnroadEvent.EventName

# every service update_events() reads, with the size the list-typed ones need
SERVICES = {'controlsState': None, 'deviceState': None, 'modelV2': None, 'userBookmark': None,
            'driverMonitoringState': None, 'longitudinalPlanSP': None, 'peripheralState': None,
            'extrinsicsCalibration': None, 'driverAssistance': None, 'deviceMotion': None,
            'modelDataV2SP': None, 'managerState': None, 'radarState': None, 'longitudinalPlan': None,
            'vehicleParameters': None, 'carControl': None, 'pandaStates': 0}


class FakeSubMaster:
  """A SubMaster that has received nothing: every message is the capnp default."""

  def __init__(self):
    self.frame = 10000
    self.data = {s: getattr(messaging.new_message(s, size), s) for s, size in SERVICES.items()}
    self.seen = dict.fromkeys(SERVICES, False)
    self.alive = dict.fromkeys(SERVICES, True)
    self.valid = dict.fromkeys(SERVICES, True)
    self.freq_ok = dict.fromkeys(SERVICES, True)
    self.updated = dict.fromkeys(SERVICES, False)
    self.recv_frame = collections.defaultdict(int)

  def __getitem__(self, s):
    return self.data[s]

  def all_checks(self, service_list=None):
    return True

  def all_alive(self, service_list=None):
    return True

  def all_freq_ok(self, service_list=None):
    return True


class FakeRatekeeper:
  lagging = False


class FakeIcbm:
  def run(self, *args):
    pass


class TestLocalizerAlerts(OpenpilotTestCase):
  def setup_method(self):
    self.sd = SelfdriveD.__new__(SelfdriveD)
    self.sd.params = Params()
    self.sd.sm = FakeSubMaster()
    self.sd.events = Events()
    self.sd.events_sp = EventsSP()
    self.sd.accelerator_events = AcceleratorEvents()
    self.sd.CP = car.CarParams.new_message()
    self.sd.rk = FakeRatekeeper()
    self.sd.pose_calibrator = PoseCalibrator()
    self.sd.calibrated_pose = None
    self.sd.excessive_actuation_check = ExcessiveActuationCheck()
    self.sd.excessive_actuation = False
    self.sd.initialized = True
    self.sd.enabled = False
    self.sd.startup_event = None
    self.sd.big_model_loading = False
    self.sd.big_model_active = False
    self.sd.big_model_failed = False
    self.sd.big_model_ready_t = 0.  # past the settling window
    self.sd.dm_lockout_set = False
    self.sd.dm_uncertain_alerted = False
    self.sd.recalibrating_seen = False
    self.sd.is_ldw_enabled = False
    self.sd.disengage_on_accelerator = False
    self.sd.mismatch_counter = 0
    self.sd.not_running_prev = None
    self.sd.ignored_processes = set()
    self.sd.logged_comm_issue = None
    self.sd.last_functional_fan_frame = 0
    self.sd.sensor_packets = []
    self.sd.camera_packets = []
    self.sd.CS_prev = car.CarState.new_message()
    self.sd.cruise_mismatch_counter = 0
    self.sd.last_steering_pressed_frame = 0
    self.sd.gps_location_service = 'gpsLocationExternal'
    self.sd.distance_traveled = 0
    self.sd.experimental_mode = False
    self.sd.is_metric = False
    self.sd.icbm = FakeIcbm()

    # calibrated, so only the seen guard keeps paramsdTemporaryError away
    self.sd.sm['extrinsicsCalibration'].calStatus = log.ExtrinsicsCalibration.Status.calibrated

    self.CS = car.CarState.new_message()

  def test_never_received(self):
    self.sd.update_events(self.CS)
    assert not self.sd.events.has(EventName.posenetInvalid)
    assert not self.sd.events.has(EventName.locationdTemporaryError)
    assert not self.sd.events.has(EventName.paramsdTemporaryError)

  def test_posenet_not_ok_once_seen(self):
    self.sd.sm.seen['deviceMotion'] = True
    self.sd.sm['deviceMotion'].posenetOK = False
    self.sd.sm['deviceMotion'].inputsOK = True
    self.sd.update_events(self.CS)
    assert self.sd.events.has(EventName.posenetInvalid)
    assert not self.sd.events.has(EventName.locationdTemporaryError)

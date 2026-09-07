import collections
from unittest.mock import Mock

from opendbc.car.structs import car

from openpilot.cereal import log, messaging
from openpilot.common.test import OpenpilotTestCase
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.selfdrive.locationd.helpers import PoseCalibrator
from openpilot.selfdrive.selfdrived.events import Events
from openpilot.selfdrive.selfdrived.helpers import ExcessiveActuationCheck
from openpilot.selfdrive.selfdrived.selfdrived import SelfdriveD
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.selfdrive.car.intelligent_cruise_button_management.controller import IntelligentCruiseButtonManagement

EventName = log.OnroadEvent.EventName

# every service update_events() reads, with the size the list-typed ones need
SERVICES = {'controlsState': None, 'deviceState': None, 'modelV2': None, 'userBookmark': None,
            'driverMonitoringState': None, 'longitudinalPlanSP': None, 'peripheralState': None,
            'extrinsicsCalibration': None, 'driverAssistance': None, 'deviceMotion': None,
            'modelDataV2SP': None, 'managerState': None, 'radarState': None, 'longitudinalPlan': None,
            'vehicleParameters': None, 'carControl': None, 'pandaStates': 0}


class TestLocalizerAlerts(OpenpilotTestCase):
  def setup_method(self):
    self.sd = SelfdriveD.__new__(SelfdriveD)
    self.sd.params = Params()
    self.sd.sm = messaging.SubMaster(list(SERVICES))
    self.sd.sm.frame = 10000
    for service, size in SERVICES.items():
      self.sd.sm.data[service] = getattr(messaging.new_message(service, size), service)
      self.sd.sm.alive[service] = self.sd.sm.valid[service] = self.sd.sm.freq_ok[service] = True
    self.sd.sm.recv_frame = collections.defaultdict(int)
    self.sd.events = Events()
    self.sd.events_sp = EventsSP()
    self.sd.CP = car.CarParams.new_message()
    self.sd.rk = Mock(spec=Ratekeeper, lagging=False)
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
    self.sd.big_model_running = False
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
    self.sd.icbm = Mock(spec=IntelligentCruiseButtonManagement)

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

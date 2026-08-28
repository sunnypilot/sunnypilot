import threading
import time
from types import SimpleNamespace

from openpilot.common.test import OpenpilotTestCase
from openpilot.cereal import log, messaging
from openpilot.cereal.messaging import SubMaster, PubMaster
from openpilot.selfdrive.ui.soundd import SELFDRIVE_STATE_TIMEOUT, Soundd, check_selfdrive_timeout_alert
from openpilot.selfdrive.ui.sunnypilot.onroad.milestone_tracker_prototype import PerDriveMilestoneTracker

AudibleAlert = log.SelfdriveState.AudibleAlert


class TestSoundd(OpenpilotTestCase):
  def test_milestone_chime_uses_real_assisted_distance(self):
    soundd = Soundd()
    soundd.milestone_tracker = PerDriveMilestoneTracker(milestone_meters=10.0)

    class SubMasterStub:
      def __init__(self):
        self.logMonoTime = {'carState': 0}
        self.data = {
          'deviceState': SimpleNamespace(started=True),
          'carState': SimpleNamespace(vEgo=10.0),
          'carControl': SimpleNamespace(latActive=True, longActive=True),
        }

      def __getitem__(self, service):
        return self.data[service]

    sm = SubMasterStub()
    soundd.update_milestone_alert(sm)
    sm.logMonoTime['carState'] = 500_000_000
    soundd.update_milestone_alert(sm)
    sm.logMonoTime['carState'] = 1_000_000_000
    soundd.update_milestone_alert(sm)

    assert soundd.current_alert == AudibleAlert.complete

  def test_check_selfdrive_timeout_alert(self, mocker):
    sm = SubMaster(['selfdriveState', 'selfdriveStateSP'])
    pm = PubMaster(['selfdriveState', 'selfdriveStateSP'])

    cs = messaging.new_message('selfdriveState')
    cs.selfdriveState.enabled = True
    threading.Timer(0.01, pm.send, args=("selfdriveState", cs)).start()
    sm.update(100)
    assert sm.updated['selfdriveState']

    sm.recv_time['selfdriveState'] = 0
    clock = mocker.patch("openpilot.selfdrive.ui.soundd.time.monotonic", return_value=SELFDRIVE_STATE_TIMEOUT)
    assert not check_selfdrive_timeout_alert(sm)

    clock.return_value = SELFDRIVE_STATE_TIMEOUT + 0.1
    assert check_selfdrive_timeout_alert(sm)

    clock.return_value = SELFDRIVE_STATE_TIMEOUT + 10
    assert not check_selfdrive_timeout_alert(sm)

  def test_check_selfdrive_timeout_alert_mads_lateral_only(self):
    sm = SubMaster(['selfdriveState', 'selfdriveStateSP'])
    pm = PubMaster(['selfdriveState', 'selfdriveStateSP'])

    for _ in range(100):
      cs = messaging.new_message('selfdriveState')
      cs.selfdriveState.enabled = False

      ss_sp = messaging.new_message('selfdriveStateSP')
      ss_sp.selfdriveStateSP.mads.enabled = True

      pm.send("selfdriveState", cs)
      pm.send("selfdriveStateSP", ss_sp)

      time.sleep(0.01)

      sm.update(0)

      assert not check_selfdrive_timeout_alert(sm)

    for _ in range(SELFDRIVE_STATE_TIMEOUT * 110):
      sm.update(0)
      time.sleep(0.01)

    assert check_selfdrive_timeout_alert(sm)

  # TODO: add test with micd for checking that soundd actually outputs sounds

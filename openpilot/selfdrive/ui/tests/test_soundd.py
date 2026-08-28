import threading
import time

from openpilot.common.test import OpenpilotTestCase
from openpilot.cereal import log, messaging
from openpilot.cereal.messaging import SubMaster, PubMaster
from openpilot.selfdrive.ui.soundd import SELFDRIVE_STATE_TIMEOUT, Soundd, calculate_volume_for_device, check_selfdrive_timeout_alert
from openpilot.selfdrive.ui.sunnypilot.onroad.milestone_tracker_prototype import MILESTONE_EVENT_PAYLOAD

AudibleAlert = log.SelfdriveState.AudibleAlert


class TestSoundd(OpenpilotTestCase):
  def test_comma_four_volume_is_20_percent_louder_than_comma_three_x(self):
    for weighted_db in (20.0, 30.0, 40.0, 50.0):
      with self.subTest(weighted_db=weighted_db):
        comma_three_x_volume = calculate_volume_for_device(weighted_db, "tizi")
        comma_four_volume = calculate_volume_for_device(weighted_db, "mici")
        assert comma_four_volume == min(1.0, comma_three_x_volume * 1.2)

  def test_milestone_chime_uses_ui_milestone_event(self):
    soundd = Soundd()

    class SubMasterStub:
      def __init__(self):
        self.updated = {'customReservedRawData0': True}
        self.data = {'customReservedRawData0': MILESTONE_EVENT_PAYLOAD}

      def __getitem__(self, service):
        return self.data[service]

    sm = SubMasterStub()
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

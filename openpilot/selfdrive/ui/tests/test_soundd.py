import os
import threading
import time
import wave

from openpilot.common.test import OpenpilotTestCase
from openpilot.cereal import log, messaging
from openpilot.cereal.messaging import SubMaster, PubMaster
from openpilot.selfdrive.ui.soundd import SAMPLE_RATE, SELFDRIVE_STATE_TIMEOUT, Soundd, check_selfdrive_timeout_alert
from openpilot.sunnypilot.selfdrive.ui.robotic_sounds import ROBOTIC_SOUND_FILES, ROBOTIC_SOUNDS_DIR, RoboticSoundPack

AudibleAlert = log.SelfdriveState.AudibleAlert


class TestSoundd(OpenpilotTestCase):
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

  def test_robotic_sound_pack_wav_formats(self):
    for alert_id, filename in ROBOTIC_SOUND_FILES.items():
      path = os.path.join(ROBOTIC_SOUNDS_DIR, filename)
      assert os.path.exists(path), f"Missing robotic sound for {alert_id}: {path}"
      with wave.open(path, "r") as wf:
        assert wf.getnchannels() == 1, f"{filename} must be mono"
        assert wf.getsampwidth() == 2, f"{filename} must be 16-bit PCM"
        assert wf.getframerate() == SAMPLE_RATE, f"{filename} must be {SAMPLE_RATE} Hz"
        assert wf.getnframes() > 0, f"{filename} must not be empty"

  def test_robotic_sound_pack_switching_and_quiet_mode(self):
    class _FakeParams:
      def __init__(self):
        self.vals = {"MiciRoboticUI": False, "QuietMode": False}

      def get_bool(self, key: str) -> bool:
        return self.vals.get(key, False)

    fake_params = _FakeParams()
    pack = RoboticSoundPack(fake_params, SAMPLE_RATE)
    pack.load()
    assert len(pack.sounds) == len(ROBOTIC_SOUND_FILES)

    soundd = Soundd.__new__(Soundd)
    soundd.params = fake_params
    soundd.enabled = False
    soundd._frame = 0
    soundd.robotic_sound_pack = pack
    soundd.load_sounds()
    soundd.current_alert = AudibleAlert.engage
    soundd.current_volume = 1.0
    soundd.current_sound_frame = 0
    soundd.pending_stop = False

    # Default buffer used when MiciRoboticUI is False
    buf_default = soundd.robotic_sound_pack.get_buffer(AudibleAlert.engage, soundd.loaded_sounds)
    assert buf_default is soundd.loaded_sounds[AudibleAlert.engage]

    # Switching MiciRoboticUI to True swaps buffer to robotic sound
    fake_params.vals["MiciRoboticUI"] = True
    assert pack.refresh_param() is True
    buf_robotic = soundd.robotic_sound_pack.get_buffer(AudibleAlert.engage, soundd.loaded_sounds)
    assert buf_robotic is pack.sounds[AudibleAlert.engage]
    assert buf_robotic is not buf_default

    # QuietMode still suppresses non-critical robotic engage chirp
    soundd.enabled = True
    assert not soundd.should_play_sound(AudibleAlert.engage)
    assert soundd.should_play_sound(AudibleAlert.warningImmediate)

  # TODO: add test with micd for checking that soundd actually outputs sounds

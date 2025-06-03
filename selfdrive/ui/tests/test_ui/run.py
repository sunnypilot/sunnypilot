#!/usr/bin/env python3
import capnp
import json
import pathlib
import shutil
import sys
import os
import pywinctl
import pyautogui
import pickle
import time
from collections import namedtuple

from cereal import car, log, custom
from msgq.visionipc import VisionIpcServer, VisionStreamType
from cereal.messaging import PubMaster, log_from_bytes, sub_sock
from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.common.prefix import OpenpilotPrefix
from openpilot.common.transformations.camera import CameraConfig, DEVICE_CAMERAS
from openpilot.selfdrive.selfdrived.alertmanager import set_offroad_alert
from openpilot.selfdrive.test.helpers import with_processes
from openpilot.selfdrive.test.process_replay.migration import migrate, migrate_controlsState, migrate_carState
from openpilot.tools.lib.logreader import LogReader
from openpilot.tools.lib.framereader import FrameReader
from openpilot.tools.lib.route import Route
from openpilot.tools.lib.cache import DEFAULT_CACHE_DIR

UI_DELAY = 0.5 # may be slower on CI?
TEST_ROUTE = "a2a0ccea32023010|2023-07-27--13-01-19"

STREAMS: list[tuple[VisionStreamType, CameraConfig, bytes]] = []
OFFROAD_ALERTS = ['Offroad_StorageMissing', 'Offroad_IsTakingSnapshot']
DATA: dict[str, capnp.lib.capnp._DynamicStructBuilder] = dict.fromkeys(
  ["carParams", "deviceState", "pandaStates", "controlsState", "selfdriveState",
  "liveCalibration", "modelV2", "radarState", "driverMonitoringState", "carState",
  "driverStateV2", "roadCameraState", "wideRoadCameraState", "driverCameraState"], None)

def setup_homescreen(click, pm: PubMaster, scroll=None):
  time.sleep(UI_DELAY)

def setup_settings_device(click, pm: PubMaster, scroll=None):
  click(100, 100)

def setup_settings_network(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  click(278, 405)

def setup_settings_network_advanced(click, pm: PubMaster, scroll=None):
  setup_settings_network(click, pm)
  click(1913, 90)

def setup_settings_toggles(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  click(278, 632)
  time.sleep(UI_DELAY)

def setup_settings_software(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  click(278, 742)
  time.sleep(UI_DELAY)

def setup_settings_firehose(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  scroll(-400, 278, 962)
  click(278, 862)

def setup_settings_developer(click, pm: PubMaster, scroll=None):
  CP = car.CarParams()
  CP.alphaLongitudinalAvailable = True
  Params().put("CarParamsPersistent", CP.to_bytes())

  setup_settings_device(click, pm)
  scroll(-400, 278, 962)
  click(278, 970)
  time.sleep(UI_DELAY)

def setup_onroad(click, pm: PubMaster, scroll=None):
  vipc_server = VisionIpcServer("camerad")
  for stream_type, cam, _ in STREAMS:
    vipc_server.create_buffers(stream_type, 5, cam.width, cam.height)
  vipc_server.start_listener()

  uidebug_received_cnt = 0
  packet_id = 0
  uidebug_sock = sub_sock('uiDebug')

  # Condition check for uiDebug processing
  check_uidebug = DATA['deviceState'].deviceState.started and not DATA['carParams'].carParams.notCar

  # Loop until 20 'uiDebug' messages are received
  while uidebug_received_cnt <= 20:
    for service, data in DATA.items():
      if data:
        data.clear_write_flag()
        pm.send(service, data)

    for stream_type, _, image in STREAMS:
      vipc_server.send(stream_type, image, packet_id, packet_id, packet_id)

    if check_uidebug:
      while uidebug_sock.receive(non_blocking=True):
        uidebug_received_cnt += 1
    else:
      uidebug_received_cnt += 1

    packet_id += 1
    time.sleep(0.05)

def setup_onroad_disengaged(click, pm: PubMaster, scroll=None):
  DATA['selfdriveState'].selfdriveState.enabled = False
  setup_onroad(click, pm)
  DATA['selfdriveState'].selfdriveState.enabled = True

def setup_onroad_override(click, pm: PubMaster, scroll=None):
  DATA['selfdriveState'].selfdriveState.state = log.SelfdriveState.OpenpilotState.overriding
  setup_onroad(click, pm)
  DATA['selfdriveState'].selfdriveState.state = log.SelfdriveState.OpenpilotState.enabled


def setup_onroad_wide(click, pm: PubMaster, scroll=None):
  DATA['selfdriveState'].selfdriveState.experimentalMode = True
  DATA["carState"].carState.vEgo = 1
  setup_onroad(click, pm)

def setup_onroad_sidebar(click, pm: PubMaster, scroll=None):
  setup_onroad(click, pm)
  click(500, 500)
  setup_onroad(click, pm)

def setup_onroad_wide_sidebar(click, pm: PubMaster, scroll=None):
  setup_onroad_wide(click, pm)
  click(500, 500)
  setup_onroad_wide(click, pm)

def setup_body(click, pm: PubMaster, scroll=None):
  DATA['carParams'].carParams.brand = "body"
  DATA['carParams'].carParams.notCar = True
  DATA['carState'].carState.charging = True
  DATA['carState'].carState.fuelGauge = 50.0
  setup_onroad(click, pm)

def setup_keyboard(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  scroll(-400, 278, 962)
  click(278, 970)
  click(1930, 390)

def setup_keyboard_uppercase(click, pm: PubMaster, scroll=None):
  setup_keyboard(click, pm, scroll)
  click(200, 800)

def setup_driver_camera(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  click(1720, 825)
  DATA['deviceState'].deviceState.started = False
  setup_onroad(click, pm)
  DATA['deviceState'].deviceState.started = True

def setup_onroad_alert(click, pm: PubMaster, text1, text2, size, status=log.SelfdriveState.AlertStatus.normal):
  print(f'setup onroad alert, size: {size}')
  state = DATA['selfdriveState']
  origin_state_bytes = state.to_bytes()
  cs = state.selfdriveState
  cs.alertText1 = text1
  cs.alertText2 = text2
  cs.alertSize = size
  cs.alertStatus = status
  cs.alertType = "test_onroad_alert"
  setup_onroad(click, pm)
  DATA['selfdriveState'] = log_from_bytes(origin_state_bytes).as_builder()

def setup_onroad_alert_small(click, pm: PubMaster, scroll=None):
  setup_onroad_alert(click, pm, 'This is a small alert message', '', log.SelfdriveState.AlertSize.small)

def setup_onroad_alert_mid(click, pm: PubMaster, scroll=None):
  setup_onroad_alert(click, pm, 'Medium Alert', 'This is a medium alert message', log.SelfdriveState.AlertSize.mid)

def setup_onroad_alert_full(click, pm: PubMaster, scroll=None):
  setup_onroad_alert(click, pm, 'Full Alert', 'This is a full alert message', log.SelfdriveState.AlertSize.full)

def setup_offroad_alert(click, pm: PubMaster, scroll=None):
  for alert in OFFROAD_ALERTS:
    set_offroad_alert(alert, True)

  # Toggle between settings and home to refresh the offroad alert widget
  setup_settings_device(click, pm)
  click(100, 100)

def setup_update_available(click, pm: PubMaster, scroll=None):
  Params().put_bool("UpdateAvailable", True)
  release_notes_path = os.path.join(BASEDIR, "RELEASES.md")
  with open(release_notes_path) as file:
    release_notes = file.read().split('\n\n', 1)[0]
  Params().put("UpdaterNewReleaseNotes", release_notes + "\n")

  setup_settings_device(click, pm)
  click(100, 100)

def setup_pair_device(click, pm: PubMaster, scroll=None):
  click(1950, 435)
  click(1800, 900)

def setup_settings_sunnylink(click, pm: PubMaster, scroll=None):
  Params().put_bool("SunnylinkEnabled", True)

  setup_settings_device(click, pm)
  click(278, 522)
  time.sleep(UI_DELAY)

def setup_settings_sunnylink_sponsor_button(click, pm: PubMaster, scroll=None):
  setup_settings_sunnylink(click, pm)
  click(1967, 225)
  time.sleep(UI_DELAY)

def setup_settings_models(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  click(278, 852)
  time.sleep(UI_DELAY)


def setup_settings_steering(click, pm: PubMaster, scroll=None):
  CP = car.CarParams()
  CP.carFingerprint = "HONDA_CIVIC"
  CP_SP = custom.CarParamsSP()
  CP_SP.neuralNetworkLateralControl.model.name = CP.carFingerprint
  CP_SP.neuralNetworkLateralControl.fuzzyFingerprint = True
  Params().put("CarParamsPersistent", CP.to_bytes())
  Params().put("CarParamsSPPersistent", CP_SP.to_bytes())

  setup_settings_device(click, pm)
  click(278, 962)
  time.sleep(UI_DELAY)

def setup_settings_steering_mads(click, pm: PubMaster, scroll=None):
  Params().put_bool("Mads", True)

  setup_settings_device(click, pm)
  click(278, 962)
  click(970, 250)
  time.sleep(UI_DELAY)

def setup_settings_steering_alc(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  click(278, 962)
  click(970, 534)
  time.sleep(UI_DELAY)

def setup_settings_driving(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  scroll(-1, 278, 962)
  click(278, 962)
  time.sleep(UI_DELAY)

def setup_settings_visuals(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  scroll(-400, 278, 962)
  click(278, 560)
  time.sleep(UI_DELAY)

def setup_settings_trips(click, pm: PubMaster, scroll=None):
  setup_settings_device(click, pm)
  scroll(-400, 278, 962)
  click(278, 646)
  time.sleep(UI_DELAY)

def setup_settings_vehicle(click, pm: PubMaster, scroll=None):
  Params().put("CarPlatformBundle", json.dumps(
    {
      "platform": "HONDA_CIVIC_2022",
      "name": "Honda Civic 2022-24"
    }
  ))

  setup_settings_device(click, pm)
  scroll(-400, 278, 962)
  click(278, 754)
  time.sleep(UI_DELAY)

CASES = {
  "homescreen": setup_homescreen,
  "prime": setup_homescreen,
  "pair_device": setup_pair_device,
  "settings_device": setup_settings_device,
  "settings_network": setup_settings_network,
  "settings_network_advanced": setup_settings_network_advanced,
  "settings_toggles": setup_settings_toggles,
  "settings_software": setup_settings_software,
  "settings_firehose": setup_settings_firehose,
  "settings_developer": setup_settings_developer,
  "onroad": setup_onroad,
  "onroad_disengaged": setup_onroad_disengaged,
  "onroad_override": setup_onroad_override,
  "onroad_sidebar": setup_onroad_sidebar,
  "onroad_alert_small": setup_onroad_alert_small,
  "onroad_alert_mid": setup_onroad_alert_mid,
  "onroad_alert_full": setup_onroad_alert_full,
  "onroad_wide": setup_onroad_wide,
  "onroad_wide_sidebar": setup_onroad_wide_sidebar,
  "driver_camera": setup_driver_camera,
  "body": setup_body,
  "offroad_alert": setup_offroad_alert,
  "update_available": setup_update_available,
  "keyboard": setup_keyboard,
  "keyboard_uppercase": setup_keyboard_uppercase
}

CASES.update({
  "settings_sunnylink": setup_settings_sunnylink,
  "settings_sunnylink_sponsor_button": setup_settings_sunnylink_sponsor_button,
  "settings_models": setup_settings_models,
  "settings_steering": setup_settings_steering,
  "settings_steering_mads": setup_settings_steering_mads,
  "settings_steering_alc": setup_settings_steering_alc,
  "settings_driving": setup_settings_driving,
  "settings_visuals": setup_settings_visuals,
  "settings_trips": setup_settings_trips,
  "settings_vehicle": setup_settings_vehicle,
})

TEST_DIR = pathlib.Path(__file__).parent

TEST_OUTPUT_DIR = TEST_DIR / "report_1"
SCREENSHOTS_DIR = TEST_OUTPUT_DIR / "screenshots"


class TestUI:
  def __init__(self):
    os.environ["SCALE"] = "1"
    sys.modules["mouseinfo"] = False

  def setup(self):
    self.pm = PubMaster(list(DATA.keys()))
    DATA['deviceState'].deviceState.networkType = log.DeviceState.NetworkType.wifi
    DATA['deviceState'].deviceState.lastAthenaPingTime = 0
    for _ in range(10):
      self.pm.send('deviceState', DATA['deviceState'])
      DATA['deviceState'].clear_write_flag()
      time.sleep(0.05)
    try:
      self.ui = pywinctl.getWindowsWithTitle("ui")[0]
    except Exception as e:
      print(f"failed to find ui window, assuming that it's in the top left (for Xvfb) {e}")
      self.ui = namedtuple("bb", ["left", "top", "width", "height"])(0,0,2160,1080)

  def screenshot(self, name):
    im = pyautogui.screenshot(SCREENSHOTS_DIR / f"{name}.png", region=(self.ui.left, self.ui.top, self.ui.width, self.ui.height))
    assert im.width == 2160
    assert im.height == 1080

  def click(self, x, y, *args, **kwargs):
    pyautogui.click(self.ui.left + x, self.ui.top + y, *args, **kwargs)
    time.sleep(UI_DELAY) # give enough time for the UI to react

  def scroll(self, clicks, x, y, *args, **kwargs):
    pyautogui.scroll(clicks, self.ui.left + x, self.ui.top + y, *args, **kwargs)
    time.sleep(UI_DELAY)

  @with_processes(["ui"])
  def test_ui(self, name, setup_case):
    self.setup()
    setup_case(self.click, self.pm, self.scroll)
    self.screenshot(name)

def create_screenshots():
  if TEST_OUTPUT_DIR.exists():
    shutil.rmtree(TEST_OUTPUT_DIR)

  SCREENSHOTS_DIR.mkdir(parents=True)

  route = Route(TEST_ROUTE)

  segnum = 2
  lr = LogReader(route.qlog_paths()[segnum])
  DATA['carParams'] = next((event.as_builder() for event in lr if event.which() == 'carParams'), None)
  for event in migrate(lr, [migrate_controlsState, migrate_carState]):
    if event.which() in DATA:
      DATA[event.which()] = event.as_builder()

    if all(DATA.values()):
      break

  cam = DEVICE_CAMERAS[("tici", "ar0231")]

  frames_cache = f'{DEFAULT_CACHE_DIR}/ui_frames'
  if os.path.isfile(frames_cache):
    with open(frames_cache, 'rb') as f:
      frames = pickle.load(f)
      road_img = frames[0]
      wide_road_img = frames[1]
      driver_img = frames[2]
  else:
    with open(frames_cache, 'wb') as f:
      road_img = FrameReader(route.camera_paths()[segnum]).get(0, pix_fmt="nv12")[0]
      wide_road_img = FrameReader(route.ecamera_paths()[segnum]).get(0, pix_fmt="nv12")[0]
      driver_img = FrameReader(route.dcamera_paths()[segnum]).get(0, pix_fmt="nv12")[0]
      pickle.dump([road_img, wide_road_img, driver_img], f)

  STREAMS.append((VisionStreamType.VISION_STREAM_ROAD, cam.fcam, road_img.flatten().tobytes()))
  STREAMS.append((VisionStreamType.VISION_STREAM_WIDE_ROAD, cam.ecam, wide_road_img.flatten().tobytes()))
  STREAMS.append((VisionStreamType.VISION_STREAM_DRIVER, cam.dcam, driver_img.flatten().tobytes()))

  t = TestUI()

  for name, setup in CASES.items():
    with OpenpilotPrefix():
      params = Params()
      params.put("DongleId", "123456789012345")
      params.put("SunnylinkDongleId", "123456789012345")
      if name == 'prime':
        params.put('PrimeType', '1')
      elif name == 'pair_device':
        params.put('ApiCache_Device', '{"is_paired":0, "prime_type":-1}')

      t.test_ui(name, setup)

if __name__ == "__main__":
  print("creating test screenshots")
  create_screenshots()

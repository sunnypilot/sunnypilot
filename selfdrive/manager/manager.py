#!/usr/bin/env python3
import datetime
import os
import signal
import sys
import traceback
from typing import List, Tuple, Union

from cereal import custom
import cereal.messaging as messaging
import openpilot.selfdrive.sentry as sentry
from openpilot.common.params import Params, ParamKeyType
from openpilot.common.text_window import TextWindow
from openpilot.system.hardware import HARDWARE, PC
from openpilot.selfdrive.manager.helpers import unblock_stdout, write_onroad_params, save_bootlog
from openpilot.selfdrive.manager.mapd_installer import VERSION
from openpilot.selfdrive.manager.process import ensure_running
from openpilot.selfdrive.manager.process_config import managed_processes
from openpilot.selfdrive.athena.registration import register, UNREGISTERED_DONGLE_ID, is_registered_device
from openpilot.common.swaglog import cloudlog, add_file_handler
from openpilot.system.version import is_dirty, get_commit, get_version, get_origin, get_short_branch, \
                           get_normalized_origin, terms_version, training_version, \
                           is_tested_branch, is_release_branch, is_release_sp_branch


def manager_init() -> None:
  save_bootlog()

  params = Params()
  params.clear_all(ParamKeyType.CLEAR_ON_MANAGER_START)
  params.clear_all(ParamKeyType.CLEAR_ON_ONROAD_TRANSITION)
  params.clear_all(ParamKeyType.CLEAR_ON_OFFROAD_TRANSITION)
  if is_release_branch():
    params.clear_all(ParamKeyType.DEVELOPMENT_ONLY)

  default_params: List[Tuple[str, Union[str, bytes]]] = [
    ("CompletedTrainingVersion", "0"),
    ("DisengageOnAccelerator", "0"),
    ("GsmMetered", "1"),
    ("HasAcceptedTerms", "0"),
    ("LanguageSetting", "main_en"),
    ("OpenpilotEnabledToggle", "1"),
    ("LongitudinalPersonality", str(custom.LongitudinalPersonalitySP.standard)),

    ("AccMadsCombo", "1"),
    ("AutoLaneChangeTimer", "0"),
    ("AutoLaneChangeBsmDelay", "1"),
    ("BelowSpeedPause", "0"),
    ("BrakeLights", "0"),
    ("BrightnessControl", "0"),
    ("CustomTorqueLateral", "0"),
    ("CameraControl", "2"),
    ("CameraControlToggle", "0"),
    ("CameraOffset", "4"),
    ("CarModel", ""),
    ("CarModelText", ""),
    ("ChevronInfo", "1"),
    ("MadsCruiseMain", "1"),
    ("CustomBootScreen", "0"),
    ("CustomOffsets", "0"),
    ("DevUIInfo", "0"),
    ("DisableOnroadUploads", "0"),
    ("DisengageLateralOnBrake", "0"),
    ("DrivingModelGeneration", "0"),
    ("DynamicLaneProfile", "1"),
    ("EnableMads", "1"),
    ("EnhancedScc", "0"),
    ("FeatureStatus", "1"),
    ("HandsOnWheelMonitoring", "0"),
    ("HideVEgoUi", "0"),
    ("LastSpeedLimitSignTap", "0"),
    ("LkasToggle", "0"),
    ("MadsIconToggle", "1"),
    ("MaxTimeOffroad", "9"),
    ("NNFF", "0"),
    ("OnroadScreenOff", "-2"),
    ("OnroadScreenOffBrightness", "50"),
    ("OnroadScreenOffEvent", "1"),
    ("OnroadSettings", "1"),
    ("PathOffset", "0"),
    ("ReverseAccChange", "0"),
    ("ScreenRecorder", "1"),
    ("ShowDebugUI", "1"),
    ("SpeedLimitControlPolicy", "3"),
    ("SpeedLimitEngageType", "0"),
    ("SpeedLimitValueOffset", "0"),
    ("SpeedLimitOffsetType", "0"),
    ("SpeedLimitWarningType", "0"),
    ("SpeedLimitWarningValueOffset", "0"),
    ("SpeedLimitWarningOffsetType", "0"),
    ("StandStillTimer", "0"),
    ("StockLongToyota", "0"),
    ("TorqueDeadzoneDeg", "0"),
    ("TorqueFriction", "1"),
    ("TorqueMaxLatAccel", "250"),
    ("TrueVEgoUi", "0"),
    ("TurnSpeedControl", "0"),
    ("TurnVisionControl", "0"),
    ("VisionCurveLaneless", "0"),
    ("VwAccType", "0"),
    ("OsmDbUpdatesCheck", "0"),
    ("OsmDownloadedDate", "0"),
    ("OSMDownloadProgress", "{}"),
    ("MapdVersion", f"{VERSION}"),
  ]
  if not PC:
    default_params.append(("LastUpdateTime", datetime.datetime.utcnow().isoformat().encode('utf8')))

  if params.get_bool("RecordFrontLock"):
    params.put_bool("RecordFront", True)

  # set unset params
  for k, v in default_params:
    if params.get(k) is None:
      params.put(k, v)

  # parameters set by Environment Variables
  if os.getenv("HANDSMONITORING") is not None:
    params.put_bool("HandsOnWheelMonitoring", bool(int(os.getenv("HANDSMONITORING", "0"))))

  # Create folders needed for msgq
  try:
    os.mkdir("/dev/shm")
  except FileExistsError:
    pass
  except PermissionError:
    print("WARNING: failed to make /dev/shm")

  # set version params
  params.put("Version", get_version())
  params.put("TermsVersion", terms_version)
  params.put("TrainingVersion", training_version)
  params.put("GitCommit", get_commit())
  params.put("GitBranch", get_short_branch())
  params.put("GitRemote", get_origin())
  params.put_bool("IsTestedBranch", is_tested_branch())
  params.put_bool("IsReleaseBranch", is_release_branch())
  params.put_bool("IsReleaseSPBranch", is_release_sp_branch())

  # set dongle id
  reg_res = register(show_spinner=True)
  if reg_res:
    dongle_id = reg_res
  else:
    serial = params.get("HardwareSerial")
    raise Exception(f"Registration failed for device {serial}")
  if params.get("HardwareSerial") is None:
    try:
      serial = HARDWARE.get_serial()
      params.put("HardwareSerial", serial)
    except Exception:
      cloudlog.exception("Error getting serial for device")
  os.environ['DONGLE_ID'] = dongle_id  # Needed for swaglog
  os.environ['GIT_ORIGIN'] = get_normalized_origin() # Needed for swaglog
  os.environ['GIT_BRANCH'] = get_short_branch() # Needed for swaglog
  os.environ['GIT_COMMIT'] = get_commit() # Needed for swaglog

  if not is_dirty():
    os.environ['CLEAN'] = '1'

  # init logging
  sentry.init(sentry.SentryProject.SELFDRIVE)
  cloudlog.bind_global(dongle_id=dongle_id,
                       version=get_version(),
                       origin=get_normalized_origin(),
                       branch=get_short_branch(),
                       commit=get_commit(),
                       dirty=is_dirty(),
                       device=HARDWARE.get_device_type())

  if os.path.isfile(os.path.join(sentry.CRASHES_DIR, 'error.txt')):
    os.remove(os.path.join(sentry.CRASHES_DIR, 'error.txt'))

  models_dir = "/data/media/0/models"
  if not os.path.exists(models_dir):
    os.makedirs(models_dir)

  # preimport all processes
  for p in managed_processes.values():
    p.prepare()


def manager_cleanup() -> None:
  # send signals to kill all procs
  for p in managed_processes.values():
    p.stop(block=False)

  # ensure all are killed
  for p in managed_processes.values():
    p.stop(block=True)

  cloudlog.info("everything is dead")


def manager_thread() -> None:
  cloudlog.bind(daemon="manager")
  cloudlog.info("manager start")
  cloudlog.info({"environ": os.environ})

  params = Params()

  ignore: List[str] = []
  if params.get("DongleId", encoding='utf8') in (None, UNREGISTERED_DONGLE_ID):
    ignore += ["manage_athenad", "uploader"]
  if os.getenv("NOBOARD") is not None:
    ignore.append("pandad")
  ignore += [x for x in os.getenv("BLOCK", "").split(",") if len(x) > 0]
  if params.get("DriverCameraHardwareMissing") and not is_registered_device():
    ignore += ["dmonitoringd", "dmonitoringmodeld"]

  sm = messaging.SubMaster(['deviceState', 'carParams'], poll='deviceState')
  pm = messaging.PubMaster(['managerState'])

  write_onroad_params(False, params)
  ensure_running(managed_processes.values(), False, params=params, CP=sm['carParams'], not_run=ignore)

  started_prev = False

  while True:
    sm.update(1000)

    started = sm['deviceState'].started

    if started and not started_prev:
      params.clear_all(ParamKeyType.CLEAR_ON_ONROAD_TRANSITION)
    elif not started and started_prev:
      params.clear_all(ParamKeyType.CLEAR_ON_OFFROAD_TRANSITION)

    # update onroad params, which drives boardd's safety setter thread
    if started != started_prev:
      write_onroad_params(started, params)

    started_prev = started

    ensure_running(managed_processes.values(), started, params=params, CP=sm['carParams'], not_run=ignore)

    running = ' '.join("%s%s\u001b[0m" % ("\u001b[32m" if p.proc.is_alive() else "\u001b[31m", p.name)
                       for p in managed_processes.values() if p.proc)
    print(running)
    cloudlog.debug(running)

    # send managerState
    msg = messaging.new_message('managerState', valid=True)
    msg.managerState.processes = [p.get_process_state_msg() for p in managed_processes.values()]
    pm.send('managerState', msg)

    # Exit main loop when uninstall/shutdown/reboot is needed
    shutdown = False
    for param in ("DoUninstall", "DoShutdown", "DoReboot"):
      if params.get_bool(param):
        shutdown = True
        params.put("LastManagerExitReason", f"{param} {datetime.datetime.now()}")
        cloudlog.warning(f"Shutting down manager - {param} set")

    if shutdown:
      break


def main() -> None:
  manager_init()
  if os.getenv("PREPAREONLY") is not None:
    return

  # SystemExit on sigterm
  signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(1))

  try:
    manager_thread()
  except Exception:
    traceback.print_exc()
    sentry.capture_exception()
  finally:
    manager_cleanup()

  params = Params()
  if params.get_bool("DoUninstall"):
    cloudlog.warning("uninstalling")
    HARDWARE.uninstall()
  elif params.get_bool("DoReboot"):
    cloudlog.warning("reboot")
    HARDWARE.reboot()
  elif params.get_bool("DoShutdown"):
    cloudlog.warning("shutdown")
    HARDWARE.shutdown()


if __name__ == "__main__":
  unblock_stdout()

  try:
    main()
  except KeyboardInterrupt:
    print("got CTRL-C, exiting")
  except Exception:
    add_file_handler(cloudlog)
    cloudlog.exception("Manager failed to start")

    try:
      managed_processes['ui'].stop()
    except Exception:
      pass

    # Show last 3 lines of traceback
    error = traceback.format_exc(-3)
    error = "Manager failed to start\n\n" + error
    with TextWindow(error) as t:
      t.wait_for_exit()

    raise

  # manual exit because we are forked
  sys.exit(0)

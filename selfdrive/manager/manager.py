#!/usr/bin/env python3
import datetime
import os
import signal
import subprocess
import sys
import traceback

import cereal.messaging as messaging
import selfdrive.crash as crash
from common.basedir import BASEDIR
from common.params import Params, ParamKeyType
from common.text_window import TextWindow
from selfdrive.boardd.set_time import set_time
from selfdrive.hardware import EON, HARDWARE, PC, TICI
from selfdrive.hardware.eon.apk import (pm_apply_packages, update_apks)
from selfdrive.manager.helpers import unblock_stdout
from selfdrive.manager.process import ensure_running
from selfdrive.manager.process_config import managed_processes
from selfdrive.athena.registration import register, UNREGISTERED_DONGLE_ID
from selfdrive.swaglog import cloudlog, add_file_handler
from selfdrive.version import dirty, get_git_commit, version, origin, branch, commit, \
                              terms_version, training_version, comma_remote, \
                              get_git_branch, get_git_remote

def manager_init():

  # update system time from panda
  set_time(cloudlog)

  params = Params()
  params.clear_all(ParamKeyType.CLEAR_ON_MANAGER_START)

  default_params = [
    ("CompletedTrainingVersion", "0"),
    ("HasAcceptedTerms", "0"),
    ("OpenpilotEnabledToggle", "1"),
    ("IsMetric", "1"),
    ("CommunityFeaturesToggle", "1"),
    ("EndToEndToggle", "1"),
    ("IsOpenpilotViewEnabled", "0"),
    ("OpkrAutoShutdown", "2"),
    ("OpkrForceShutdown", "5"),
    ("OpkrAutoScreenOff", "0"),
    ("OpkrUIBrightness", "0"),
    ("OpkrUIBrightness", "0"),
    ("OpkrUIVolumeBoost", "0"),
    ("OpkrEnableDriverMonitoring", "1"),
    ("OpkrEnableLogger", "0"),
    ("OpkrEnableUploader", "0"),
    ("OpkrEnableGetoffAlert", "1"),
    ("OpkrAutoResume", "1"),
    ("OpkrVariableCruise", "0"),
    ("OpkrLaneChangeSpeed", "45"),
    ("OpkrAutoLaneChangeDelay", "0"),
    ("OpkrSteerAngleCorrection", "0"),
    ("PutPrebuiltOn", "0"),
    ("LdwsCarFix", "0"),
    ("LateralControlMethod", "0"),
    ("CruiseStatemodeSelInit", "1"),
    ("InnerLoopGain", "31"),
    ("OuterLoopGain", "25"),
    ("TimeConstant", "14"),
    ("ActuatorEffectiveness", "20"),
    ("Scale", "1500"),
    ("LqrKi", "15"),
    ("DcGain", "27"),
    ("IgnoreZone", "1"),
    ("PidKp", "25"),
    ("PidKi", "50"),
    ("PidKd", "150"),
    ("PidKf", "7"),
    ("CameraOffsetAdj", "60"),
    ("SteerRatioAdj", "142025"),
    ("SteerRatioMaxAdj", "142025"),
    ("SteerActuatorDelayAdj", "30"),
    ("SteerRateCostAdj", "50"),
    ("SteerLimitTimerAdj", "40"),
    ("TireStiffnessFactorAdj", "65"),
    ("SteerMaxBaseAdj", "384"),
    ("SteerMaxAdj", "384"),
    ("SteerDeltaUpBaseAdj", "3"),
    ("SteerDeltaUpAdj", "3"),
    ("SteerDeltaDownBaseAdj", "7"),
    ("SteerDeltaDownAdj", "7"),
    ("SteerMaxvAdj", "10"),
    ("OpkrBatteryChargingControl", "1"),
    ("OpkrBatteryChargingMin", "70"),
    ("OpkrBatteryChargingMax", "80"),
    ("LeftCurvOffsetAdj", "0"),
    ("RightCurvOffsetAdj", "0"),
    ("DebugUi1", "0"),
    ("DebugUi2", "0"),
    ("LongLogDisplay", "0"),
    ("OpkrBlindSpotDetect", "1"),
    ("OpkrMaxAngleLimit", "90"),
    ("OpkrSpeedLimitOffset", "0"),
    ("LimitSetSpeedCamera", "0"),
    ("LimitSetSpeedCameraDist", "0"),
    ("OpkrMapSign", "0"),
    ("OpkrLiveSteerRatio", "0"),
    ("OpkrVariableSteerMax", "0"),
    ("OpkrVariableSteerDelta", "0"),
    ("FingerprintTwoSet", "0"),
    ("OpkrVariableCruiseProfile", "0"),
    ("OpkrLiveTune", "1"),
    ("OpkrDrivingRecord", "0"),
    ("OpkrTurnSteeringDisable", "0"),
    ("CarModel", ""),
    ("CarModelAbb", ""),
    ("OpkrHotspotOnBoot", "0"),
    ("OpkrSSHLegacy", "1"),
    ("ShaneFeedForward", "0"),
    ("CruiseOverMaxSpeed", "0"),
    ("JustDoGearD", "0"),
    ("LanelessMode", "0"),
    ("ComIssueGone", "0"),
    ("MaxSteer", "384"),
    ("MaxRTDelta", "112"),
    ("MaxRateUp", "3"),
    ("MaxRateDown", "7"),
    ("SteerThreshold", "150"),
    ("RecordingCount", "100"),
    ("RecordingQuality", "1"),
    ("CruiseGapAdjust", "0"),
    ("AutoEnable", "1"),
    ("CruiseAutoRes", "0"),
    ("AutoResOption", "0"),
    ("SteerWindDown", "0"),
    ("OpkrMonitoringMode", "0"),
    ("OpkrMonitorEyesThreshold", "75"),
    ("OpkrMonitorNormalEyesThreshold", "50"),
    ("OpkrMonitorBlinkThreshold", "50"),
    ("MadModeEnabled", "1"),
    ("OpkrFanSpeedGain", "0"),
    ("WhitePandaSupport", "0"),
    ("SteerWarningFix", "0"),
    ("OpkrRunNaviOnBoot", "0"),
  ]
  if not PC:
    default_params.append(("LastUpdateTime", datetime.datetime.utcnow().isoformat().encode('utf8')))
  if TICI:
    default_params.append(("EnableLteOnroad", "0"))

  if params.get_bool("RecordFrontLock"):
    params.put_bool("RecordFront", True)

  # set unset params
  for k, v in default_params:
    if params.get(k) is None:
      params.put(k, v)

  # is this dashcam?
  if os.getenv("PASSIVE") is not None:
    params.put_bool("Passive", bool(int(os.getenv("PASSIVE"))))

  if params.get("Passive") is None:
    raise Exception("Passive must be set to continue")

  if EON:
    update_apks(show_spinner=True)

  os.umask(0)  # Make sure we can create files with 777 permissions

  # Create folders needed for msgq
  try:
    os.mkdir("/dev/shm")
  except FileExistsError:
    pass
  except PermissionError:
    print("WARNING: failed to make /dev/shm")

  # set version params
  params.put("Version", version)
  params.put("TermsVersion", terms_version)
  params.put("TrainingVersion", training_version)
  params.put("GitCommit", get_git_commit(default=""))
  params.put("GitBranch", get_git_branch(default=""))
  params.put("GitRemote", get_git_remote(default=""))

  # set dongle id
  reg_res = register(show_spinner=True)
  if reg_res:
    dongle_id = reg_res
  elif not reg_res:
    dongle_id = "maintenance"
  else:
    serial = params.get("HardwareSerial")
    raise Exception(f"Registration failed for device {serial}")
  os.environ['DONGLE_ID'] = dongle_id  # Needed for swaglog

  if not dirty:
    os.environ['CLEAN'] = '1'

  cloudlog.bind_global(dongle_id=dongle_id, version=version, dirty=dirty,
                       device=HARDWARE.get_device_type())

  if comma_remote and not (os.getenv("NOLOG") or os.getenv("NOCRASH") or PC):
    crash.init()

  # ensure shared libraries are readable by apks
  if EON:
    os.chmod(BASEDIR, 0o755)
    os.chmod("/dev/shm", 0o777)
    os.chmod(os.path.join(BASEDIR, "cereal"), 0o755)

  crash.bind_user(id=dongle_id)
  crash.bind_extra(dirty=dirty, origin=origin, branch=branch, commit=commit,
                   device=HARDWARE.get_device_type())

#  os.system("/data/openpilot/gitcommit.sh")

def manager_prepare():
  for p in managed_processes.values():
    p.prepare()


def manager_cleanup():
  if EON:
    pm_apply_packages('disable')

  for p in managed_processes.values():
    p.stop()

  cloudlog.info("everything is dead")


def manager_thread():
  cloudlog.info("manager start")
  cloudlog.info({"environ": os.environ})

  # save boot log
  #subprocess.call("./bootlog", cwd=os.path.join(BASEDIR, "selfdrive/loggerd"))

  params = Params()

  ignore = []
  if params.get("DongleId", encoding='utf8') == UNREGISTERED_DONGLE_ID:
    ignore += ["manage_athenad", "uploader"]
  if os.getenv("NOBOARD") is not None:
    ignore.append("pandad")
  if os.getenv("BLOCK") is not None:
    ignore += os.getenv("BLOCK").split(",")

  if EON:
    pm_apply_packages('enable')

  ensure_running(managed_processes.values(), started=False, not_run=ignore)

  started_prev = False
  sm = messaging.SubMaster(['deviceState'])
  pm = messaging.PubMaster(['managerState'])

  while True:
    sm.update()
    not_run = ignore[:]

    if sm['deviceState'].freeSpacePercent < 5:
      not_run.append("loggerd")

    started = sm['deviceState'].started
    driverview = params.get_bool("IsDriverViewEnabled")
    ensure_running(managed_processes.values(), started, driverview, not_run)

    # trigger an update after going offroad
    if started_prev and not started and 'updated' in managed_processes:
      os.sync()
      managed_processes['updated'].signal(signal.SIGHUP)

    started_prev = started

    running_list = ["%s%s\u001b[0m" % ("\u001b[32m" if p.proc.is_alive() else "\u001b[31m", p.name)
                    for p in managed_processes.values() if p.proc]
    cloudlog.debug(' '.join(running_list))

    # send managerState
    msg = messaging.new_message('managerState')
    msg.managerState.processes = [p.get_process_state_msg() for p in managed_processes.values()]
    pm.send('managerState', msg)

    # TODO: let UI handle this
    # Exit main loop when uninstall is needed
    if params.get_bool("DoUninstall"):
      break


def main():
  prepare_only = os.getenv("PREPAREONLY") is not None

  manager_init()

  # Start UI early so prepare can happen in the background
  if not prepare_only:
    managed_processes['ui'].start()

  manager_prepare()

  if prepare_only:
    return

  # SystemExit on sigterm
  signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(1))

  try:
    manager_thread()
  except Exception:
    traceback.print_exc()
    crash.capture_exception()
  finally:
    manager_cleanup()

  if Params().get_bool("DoUninstall"):
    cloudlog.warning("uninstalling")
    HARDWARE.uninstall()


if __name__ == "__main__":
  unblock_stdout()

  try:
    main()
  except Exception:
    add_file_handler(cloudlog)
    cloudlog.exception("Manager failed to start")

    # Show last 3 lines of traceback
    error = traceback.format_exc(-3)
    error = "Manager failed to start\n\n" + error
    with TextWindow(error) as t:
      t.wait_for_exit()

    raise

  # manual exit because we are forked
  sys.exit(0)

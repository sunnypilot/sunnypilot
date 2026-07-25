import os
import operator
import platform

from opendbc.car.structs import car
from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.common.hardware import PC, TICI
from openpilot.system.manager.process import PythonProcess, NativeProcess, DaemonProcess
from openpilot.common.hardware.hw import Paths

from openpilot.sunnypilot.mapd.mapd_manager import MAPD_PATH

from openpilot.sunnypilot.models.helpers import get_active_model_runner
from openpilot.sunnypilot.sunnylink.utils import sunnylink_need_register, sunnylink_ready, use_sunnylink_uploader

WEBCAM = os.getenv("USE_WEBCAM") is not None

def driverview(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started or params.get_bool("IsDriverViewEnabled")

def notcar(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started and CP.notCar

def iscar(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started and not CP.notCar

def logging(started: bool, params: Params, CP: car.CarParams) -> bool:
  run = (not CP.notCar) or not params.get_bool("DisableLogging")
  return started and run

def ublox_available() -> bool:
  return os.path.exists('/dev/ttyHS0') and not os.path.exists('/persist/comma/use-quectel-gps')

def ublox(started: bool, params: Params, CP: car.CarParams) -> bool:
  use_ublox = ublox_available()
  if use_ublox != params.get_bool("UbloxAvailable"):
    params.put_bool("UbloxAvailable", use_ublox, block=True)
  return started and use_ublox

def joystick(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started and params.get_bool("JoystickDebugMode")

def not_joystick(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started and not params.get_bool("JoystickDebugMode")

def long_maneuver(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started and params.get_bool("LongitudinalManeuverMode")

def lat_maneuver(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started and params.get_bool("LateralManeuverMode")

def not_long_maneuver(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started and not params.get_bool("LongitudinalManeuverMode")

def qcomgps(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started and not ublox_available()

def always_run(started: bool, params: Params, CP: car.CarParams) -> bool:
  return True

def only_onroad(started: bool, params: Params, CP: car.CarParams) -> bool:
  return started

def only_offroad(started: bool, params: Params, CP: car.CarParams) -> bool:
  return not started

def livestream(started: bool, params: Params, CP: car.CarParams) -> bool:
  return params.get_bool("IsLiveStreaming")

def use_github_runner(started, params, CP: car.CarParams) -> bool:
  return not PC and params.get_bool("EnableGithubRunner") and (
    not params.get_bool("NetworkMetered") and not params.get_bool("GithubRunnerSufficientVoltage"))

def use_copyparty(started, params, CP: car.CarParams) -> bool:
  return bool(params.get_bool("EnableCopyparty"))

def sunnylink_ready_shim(started, params, CP: car.CarParams) -> bool:
  """Shim for sunnylink_ready to match the process manager signature."""
  return sunnylink_ready(params)

def sunnylink_need_register_shim(started, params, CP: car.CarParams) -> bool:
  """Shim for sunnylink_need_register to match the process manager signature."""
  return sunnylink_need_register(params)

def use_sunnylink_uploader_shim(started, params, CP: car.CarParams) -> bool:
  """Shim for use_sunnylink_uploader to match the process manager signature."""
  return use_sunnylink_uploader(params)

def is_tinygrad_model(started, params, CP: car.CarParams) -> bool:
  """Check if the active model runner is SNPE."""
  return bool(get_active_model_runner(params, not started) == custom.ModelManagerSP.Runner.tinygrad)

def is_stock_model(started, params, CP: car.CarParams) -> bool:
  """Check if the active model runner is stock."""
  return bool(get_active_model_runner(params, not started) == custom.ModelManagerSP.Runner.stock)

def mapd_ready(started: bool, params: Params, CP: car.CarParams) -> bool:
  return bool(os.path.exists(Paths.mapd_root()))

def uploader_ready(started: bool, params: Params, CP: car.CarParams) -> bool:
  if not params.get_bool("OnroadUploads"):
    return only_offroad(started, params, CP)

  return always_run(started, params, CP)

def or_(*fns):
  return lambda *args: operator.or_(*(fn(*args) for fn in fns))

def and_(*fns):
  return lambda *args: operator.and_(*(fn(*args) for fn in fns))

def not_(*fns):
  return lambda *args: operator.not_(*(fn(*args) for fn in fns))

procs = [
  DaemonProcess("manage_athenad", "openpilot.system.athena.manage_athenad", "AthenadPid"),

  NativeProcess("loggerd", "openpilot/system/loggerd", ["./loggerd"], logging),
  NativeProcess("encoderd", "openpilot/system/loggerd", ["./encoderd"], only_onroad),
  NativeProcess("stream_encoderd", "openpilot/system/loggerd", ["./encoderd", "--stream"], or_(and_(livestream, not_(iscar)), notcar)),
  PythonProcess("logmessaged", "openpilot.system.logmessaged", always_run),

  NativeProcess("camerad", "openpilot/system/camerad", ["./camerad"], or_(driverview, livestream), enabled=not WEBCAM),
  PythonProcess("webcamerad", "openpilot.system.camerad.webcam.camerad", driverview, enabled=WEBCAM),
  PythonProcess("proclogd", "openpilot.system.proclogd", only_onroad, enabled=platform.system() != "Darwin"),
  PythonProcess("journald", "openpilot.system.journald", only_onroad, platform.system() != "Darwin"),
  PythonProcess("micd", "openpilot.system.micd", iscar),
  PythonProcess("timed", "openpilot.system.timed", always_run, enabled=not PC),

  PythonProcess("modeld", "openpilot.selfdrive.modeld.modeld", and_(only_onroad, is_stock_model)),
  PythonProcess("dmonitoringmodeld", "openpilot.selfdrive.modeld.dmonitoringmodeld", driverview, enabled=(WEBCAM or not PC)),

  PythonProcess("sensord", "openpilot.system.sensord.sensord", only_onroad, enabled=not PC),
  PythonProcess("ui", "openpilot.selfdrive.ui.ui", always_run, restart_if_crash=True),
  PythonProcess("soundd", "openpilot.selfdrive.ui.soundd", driverview),
  PythonProcess("locationd", "openpilot.selfdrive.locationd.locationd", only_onroad),
  NativeProcess("_pandad", "openpilot/selfdrive/pandad", ["./pandad"], always_run, enabled=False),
  PythonProcess("calibrationd", "openpilot.selfdrive.locationd.calibrationd", only_onroad),
  PythonProcess("torqued", "openpilot.selfdrive.locationd.torqued", only_onroad),
  PythonProcess("controlsd", "openpilot.selfdrive.controls.controlsd", and_(not_joystick, iscar)),
  PythonProcess("joystickd", "openpilot.tools.joystick.joystickd", or_(joystick, notcar)),
  PythonProcess("selfdrived", "openpilot.selfdrive.selfdrived.selfdrived", only_onroad),
  PythonProcess("card", "openpilot.selfdrive.car.card", only_onroad),
  PythonProcess("deleter", "openpilot.system.loggerd.deleter", always_run),
  PythonProcess("dmonitoringd", "openpilot.selfdrive.monitoring.dmonitoringd", driverview, enabled=(WEBCAM or not PC)),
  PythonProcess("qcomgpsd", "openpilot.system.qcomgpsd.qcomgpsd", qcomgps, enabled=TICI),
  PythonProcess("pandad", "openpilot.selfdrive.pandad.pandad", always_run),
  PythonProcess("paramsd", "openpilot.selfdrive.locationd.paramsd", only_onroad),
  PythonProcess("lagd", "openpilot.selfdrive.locationd.lagd", only_onroad),
  PythonProcess("ubloxd", "openpilot.system.ubloxd.ubloxd", ublox, enabled=TICI),
  PythonProcess("pigeond", "openpilot.system.ubloxd.pigeond", ublox, enabled=TICI),
  PythonProcess("plannerd", "openpilot.selfdrive.controls.plannerd", not_long_maneuver),
  PythonProcess("maneuversd", "openpilot.tools.longitudinal_maneuvers.maneuversd", long_maneuver),
  PythonProcess("lateral_maneuversd", "openpilot.tools.lateral_maneuvers.lateral_maneuversd", lat_maneuver),
  PythonProcess("radard", "openpilot.selfdrive.controls.radard", only_onroad),
  PythonProcess("hardwared", "openpilot.system.hardware.hardwared", always_run),
  PythonProcess("modem", "openpilot.common.hardware.tici.modem", always_run, enabled=TICI),
  PythonProcess("tombstoned", "openpilot.system.tombstoned", always_run, enabled=not PC),
  PythonProcess("updated", "openpilot.system.updated.updated", only_offroad, enabled=not PC),
  PythonProcess("uploader", "openpilot.system.loggerd.uploader", uploader_ready),
  PythonProcess("statsd", "openpilot.sunnypilot.system.statsd", always_run),
  PythonProcess("feedbackd", "openpilot.selfdrive.ui.feedback.feedbackd", only_onroad),

  # debug procs
  NativeProcess("bridge", "openpilot/cereal/messaging", ["./bridge"], notcar),
  PythonProcess("webrtcd", "openpilot.system.webrtc.webrtcd", or_(and_(livestream, not_(iscar)), notcar)),
  PythonProcess("joystick", "openpilot.tools.joystick.joystick_control", and_(joystick, iscar)),

  # sunnylink <3
  DaemonProcess("manage_sunnylinkd", "openpilot.sunnypilot.sunnylink.athena.manage_sunnylinkd", "SunnylinkdPid"),
  PythonProcess("sunnylink_registration_manager", "openpilot.sunnypilot.sunnylink.registration_manager", sunnylink_need_register_shim),
  PythonProcess("statsd_sp", "openpilot.sunnypilot.sunnylink.statsd", and_(always_run, sunnylink_ready_shim)),
]

# sunnypilot
procs += [
  # Models
  PythonProcess("models_manager", "openpilot.sunnypilot.models.manager", only_offroad),
  NativeProcess("modeld_tinygrad", "openpilot/sunnypilot/modeld_v2", ["./modeld"], and_(only_onroad, is_tinygrad_model)),

  # Backup
  PythonProcess("backup_manager", "openpilot.sunnypilot.sunnylink.backups.manager", and_(only_offroad, sunnylink_ready_shim)),

  # mapd
  NativeProcess("mapd", Paths.mapd_root(), ["bash", "-c", f"{MAPD_PATH} > /dev/null 2>&1"], mapd_ready),
  PythonProcess("mapd_manager", "openpilot.sunnypilot.mapd.mapd_manager", always_run),

  # locationd
  NativeProcess("locationd_llk", "openpilot/sunnypilot/selfdrive/locationd", ["./locationd"], only_onroad),
]

if os.path.exists("./github_runner.sh"):
  procs += [NativeProcess("github_runner_start", "openpilot/system/manager",
                          ["./github_runner.sh", "start"], and_(only_offroad, use_github_runner), sigkill=False)]

if os.path.exists("../../sunnypilot/sunnylink/uploader.py"):
  procs += [PythonProcess("sunnylink_uploader", "openpilot.sunnypilot.sunnylink.uploader", use_sunnylink_uploader_shim)]

if os.path.exists("../../third_party/copyparty/copyparty-sfx.py"):
  sunnypilot_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
  copyparty_args = [f"-v{Paths.crash_log_root()}:/swaglogs:r"]
  copyparty_args += [f"-v{Paths.log_root()}:/routes:r"]
  copyparty_args += [f"-v{Paths.model_root()}:/models:rw"]
  copyparty_args += [f"-v{sunnypilot_root}:/sunnypilot:rw"]
  copyparty_args += ["-p8080"]
  copyparty_args += ["-z"]
  copyparty_args += ["-q"]
  procs += [NativeProcess("copyparty-sfx", "openpilot/third_party/copyparty", ["./copyparty-sfx.py", *copyparty_args], and_(only_offroad, use_copyparty))]

managed_processes = {p.name: p for p in procs}

import os
import traceback
from datetime import datetime
"""Install exception handler for process crash."""
import sentry_sdk
import subprocess
from enum import Enum
from sentry_sdk.integrations.threading import ThreadingIntegration

from openpilot.common.api.sunnylink import UNREGISTERED_SUNNYLINK_DONGLE_ID
from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.system.athena.registration import UNREGISTERED_DONGLE_ID, is_registered_device
from openpilot.system.hardware import HARDWARE, PC
from openpilot.system.hardware.hw import Paths
from openpilot.common.swaglog import cloudlog
from openpilot.system.version import get_build_metadata, get_version


class SentryProject(Enum):
  # python project
  SELFDRIVE = "https://7e3be9bfcfe04c9abe58bd25fe290d1a@o1138119.ingest.sentry.io/6191481"
  # native project
  SELFDRIVE_NATIVE = "https://7e3be9bfcfe04c9abe58bd25fe290d1a@o1138119.ingest.sentry.io/6191481"


CRASHES_DIR = Paths.community_crash_root()
IP_ADDRESS = "{{auto}}"


def report_tombstone(fn: str, message: str, contents: str) -> None:
  cloudlog.error({'tombstone': message})

  with sentry_sdk.configure_scope() as scope:
    bind_user()
    scope.set_extra("tombstone_fn", fn)
    scope.set_extra("tombstone", contents)
    sentry_sdk.capture_message(message=message)
    sentry_sdk.flush()


def capture_exception(*args, **kwargs) -> None:
  save_exception(traceback.format_exc())
  cloudlog.error("crash", exc_info=kwargs.get('exc_info', 1))

  try:
    bind_user()
    sentry_sdk.capture_exception(*args, **kwargs)
    sentry_sdk.flush()  # https://github.com/getsentry/sentry-python/issues/291
  except Exception:
    cloudlog.exception("sentry exception")


def save_exception(exc_text: str) -> None:
  if not os.path.exists(CRASHES_DIR):
    os.makedirs(CRASHES_DIR)

  files = [
    os.path.join(CRASHES_DIR, datetime.now().strftime('%Y-%m-%d--%H-%M-%S.log')),
    os.path.join(CRASHES_DIR, 'error.txt')
  ]

  for file in files:
    with open(file, 'w') as f:
      if file.endswith("error.txt"):
        lines = exc_text.splitlines()[-3:]
        f.write("\n".join(lines))
      else:
        f.write(exc_text)

  print('Logged current crash to {}'.format(files))


def bind_user() -> None:
  dongle_id, gitname, _ = get_properties()
  sentry_sdk.set_user({"id": dongle_id, "ip_address": IP_ADDRESS, "name": gitname})


def capture_warning(warning_string: str) -> None:
  bind_user()
  sentry_sdk.capture_message(warning_string, level='warning')
  sentry_sdk.flush()


def capture_info(info_string: str) -> None:
  bind_user()
  sentry_sdk.capture_message(info_string, level='info')
  sentry_sdk.flush()


def set_tag(key: str, value: str) -> None:
  sentry_sdk.set_tag(key, value)


def get_properties() -> tuple[str, str, str]:
  params = Params()
  hardware_serial: str = params.get("HardwareSerial", encoding='utf-8') or ""
  gitname: str = params.get("GithubUsername", encoding='utf-8') or ""
  dongle_id: str = params.get("DongleId", encoding='utf-8') or f"{UNREGISTERED_DONGLE_ID}-{hardware_serial}"
  sunnylink_dongle_id: str = params.get("SunnylinkDongleId", encoding='utf-8') or UNREGISTERED_SUNNYLINK_DONGLE_ID

  return dongle_id, gitname, sunnylink_dongle_id


def get_init() -> None:
  params = Params()
  dongle_id, _, _ = get_properties()
  route_name = params.get("CurrentRoute", encoding='utf-8')
  subprocess.call(["./bootlog", "--started"], cwd=os.path.join(BASEDIR, "system/loggerd"))
  with sentry_sdk.configure_scope() as scope:
    if route_name is not None:
      route_id = dongle_id + "/" + route_name
      sentry_sdk.set_tag("route_name", route_id)
      scope.add_attachment(path=os.path.join(Paths.log_root(), "params", route_name), filename=route_id)


def init(project: SentryProject) -> bool:
  build_metadata = get_build_metadata()
  # forks like to mess with this, so double check
  #comma_remote = build_metadata.openpilot.comma_remote and "commaai" in build_metadata.openpilot.git_origin
  #if not comma_remote or not is_registered_device() or PC:
  #  return False

  #env = "release" if build_metadata.tested_channel else "master"
  env = build_metadata.channel_type
  dongle_id, gitname, sunnylink_dongle_id = get_properties()

  integrations = []
  if project == SentryProject.SELFDRIVE:
    integrations.append(ThreadingIntegration(propagate_hub=True))

  sentry_sdk.init(project.value,
                  default_integrations=False,
                  release=get_version(),
                  integrations=integrations,
                  traces_sample_rate=1.0,
                  max_value_length=8192,
                  environment=env,
                  send_default_pii=True)

  build_metadata = get_build_metadata()

  sentry_sdk.set_user({"id": dongle_id})
  sentry_sdk.set_user({"ip_address": IP_ADDRESS})
  sentry_sdk.set_user({"name": gitname})
  sentry_sdk.set_tag("dirty", build_metadata.openpilot.is_dirty)
  sentry_sdk.set_tag("origin", build_metadata.openpilot.git_origin)
  sentry_sdk.set_tag("branch", build_metadata.channel)
  sentry_sdk.set_tag("commit", build_metadata.openpilot.git_commit)
  sentry_sdk.set_tag("device", HARDWARE.get_device_type())
  sentry_sdk.set_tag("sunnylink_dongle_id", sunnylink_dongle_id)

  if project == SentryProject.SELFDRIVE:
    sentry_sdk.Hub.current.start_session()

  return True

"""Install exception handler for process crash."""
import sentry_sdk
from enum import Enum
from sentry_sdk.integrations.threading import ThreadingIntegration

from openpilot.common.params import Params
#from openpilot.selfdrive.athena.registration import is_registered_device
from openpilot.system.hardware import HARDWARE, PC
from openpilot.system.swaglog import cloudlog
from openpilot.system.version import get_branch, get_commit, get_origin, get_version, \
                              is_comma_remote, is_dirty, is_tested_branch, get_branch_type

import os
import traceback
from datetime import datetime


class SentryProject(Enum):
  # python project
  SELFDRIVE = "https://7e3be9bfcfe04c9abe58bd25fe290d1a@o1138119.ingest.sentry.io/6191481"
  # native project
  SELFDRIVE_NATIVE = "https://7e3be9bfcfe04c9abe58bd25fe290d1a@o1138119.ingest.sentry.io/6191481"


CRASHES_DIR = '/data/community/crashes/'
IP_ADDRESS = "{{auto}}"


def report_tombstone(fn: str, message: str, contents: str) -> None:
  cloudlog.error({'tombstone': message})

  with sentry_sdk.configure_scope() as scope:
    scope.set_extra("tombstone_fn", fn)
    scope.set_extra("tombstone", contents)
    sentry_sdk.capture_message(message=message)
    sentry_sdk.flush()


def capture_exception(*args, **kwargs) -> None:
  save_exception(traceback.format_exc())
  cloudlog.error("crash", exc_info=kwargs.get('exc_info', 1))

  try:
    sentry_sdk.capture_exception(*args, **kwargs)
    sentry_sdk.flush()  # https://github.com/getsentry/sentry-python/issues/291
  except Exception:
    cloudlog.exception("sentry exception")


def save_exception(exc_text):
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


def capture_warning(warning_string):
  sentry_sdk.capture_message(warning_string, level='warning')
  sentry_sdk.flush()


def capture_info(info_string):
  sentry_sdk.capture_message(info_string, level='info')
  sentry_sdk.flush()


def set_tag(key: str, value: str) -> None:
  sentry_sdk.set_tag(key, value)


def init(project: SentryProject) -> bool:
  # forks like to mess with this, so double check
  #comma_remote = is_comma_remote() and "commaai" in get_origin(default="")
  #if not comma_remote or not is_registered_device() or PC:
  #  return False

  #env = "release" if is_tested_branch() else "master"
  env = get_branch_type()
  dongle_id = Params().get("DongleId", encoding='utf-8')
  gitname = Params().get("GithubUsername", encoding='utf-8')

  integrations = []
  if project == SentryProject.SELFDRIVE:
    integrations.append(ThreadingIntegration(propagate_hub=True))
  else:
    sentry_sdk.utils.MAX_STRING_LENGTH = 8192

  sentry_sdk.init(project.value,
                  default_integrations=False,
                  release=get_version(),
                  integrations=integrations,
                  traces_sample_rate=1.0,
                  environment=env,
                  send_default_pii=True)

  sentry_sdk.set_user({"id": dongle_id})
  sentry_sdk.set_user({"ip_address": IP_ADDRESS})
  sentry_sdk.set_user({"username": gitname})
  sentry_sdk.set_tag("dirty", is_dirty())
  sentry_sdk.set_tag("origin", get_origin())
  sentry_sdk.set_tag("branch", get_branch())
  sentry_sdk.set_tag("commit", get_commit())
  sentry_sdk.set_tag("device", HARDWARE.get_device_type())

  if project == SentryProject.SELFDRIVE:
    sentry_sdk.Hub.current.start_session()

  return True

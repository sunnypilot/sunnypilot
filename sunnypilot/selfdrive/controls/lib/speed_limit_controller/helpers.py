from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller import DEBUG, SpeedLimitControlState
from openpilot.common.swaglog import cloudlog


def debug(msg):
  if not DEBUG:
    return
  cloudlog.debug(msg)


def description_for_state(speed_limit_control_state):
  if speed_limit_control_state == SpeedLimitControlState.inactive:
    return 'INACTIVE'
  if speed_limit_control_state == SpeedLimitControlState.preActive:
    return 'PRE_ACTIVE'
  if speed_limit_control_state == SpeedLimitControlState.pending:
    return 'PENDING'
  if speed_limit_control_state == SpeedLimitControlState.adapting:
    return 'ADAPTING'
  if speed_limit_control_state == SpeedLimitControlState.active:
    return 'ACTIVE'

  return ''

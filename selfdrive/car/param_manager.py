from types import SimpleNamespace

from openpilot.common.params import Params


class ParamManager:
  def __init__(self):
    self._params_list: SimpleNamespace = self._create_namespace({
      "acc_mads_combo": False,
      "below_speed_pause": False,
      "enable_mads": False,
      "experimental_mode": False,
      "is_metric": False,
      "last_speed_limit_sign_tap": False,
      "mads_main_toggle": False,
      "pause_lateral_speed": 0,
      "reverse_acc_change": False,
      "reverse_dm_cam": False,
      "speed_limit_control_enabled": False,
      "subaru_manual_parking_brake": False,
      "toyota_auto_lock_by_speed": False,
      "toyota_auto_unlock_by_shifter": False,
      "toyota_lkas_toggle": False,
      "toyota_sng_hack": False,
    })

  @staticmethod
  def _create_namespace(data: dict) -> SimpleNamespace:
    return SimpleNamespace(**data)

  def get_params(self) -> SimpleNamespace:
    return self._params_list

  def update(self, params: Params) -> None:
    self._params_list = self._create_namespace({
      "acc_mads_combo": params.get_bool("AccMadsCombo"),
      "below_speed_pause": params.get_bool("BelowSpeedPause"),
      "enable_mads": params.get_bool("EnableMads"),
      "experimental_mode": params.get_bool("ExperimentalMode"),
      "is_metric": params.get_bool("IsMetric"),
      "last_speed_limit_sign_tap": params.get_bool("LastSpeedLimitSignTap"),
      "mads_main_toggle": params.get_bool("MadsCruiseMain"),
      "pause_lateral_speed": int(params.get("PauseLateralSpeed", encoding="utf8")),
      "reverse_acc_change": params.get_bool("ReverseAccChange"),
      "reverse_dm_cam": params.get_bool("ReverseDmCam"),
      "speed_limit_control_enabled": params.get_bool("EnableSlc"),
      "subaru_manual_parking_brake": params.get_bool("SubaruManualParkingBrakeSng"),
      "toyota_auto_lock_by_speed": params.get_bool("ToyotaAutoLockBySpeed"),
      "toyota_auto_unlock_by_shifter": params.get_bool("ToyotaAutoUnlockByShifter"),
      "toyota_lkas_toggle": params.get_bool("LkasToggle"),
      "toyota_sng_hack": params.get_bool("ToyotaSnG"),
    })

"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time

import openpilot.cereal.messaging as messaging
import numpy as np
from openpilot.cereal import log, custom

from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.livedelay.helpers import get_lat_delay
from openpilot.sunnypilot.modeld_v2.modeld_base import ModelStateBase
from openpilot.sunnypilot.selfdrive.controls.lib.blinker_pause_lateral import BlinkerPauseLateral
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_v0 import LatControlTorque as LatControlTorqueV0


class ControlsExt(ModelStateBase):
  _radar_tracks_active: bool
  _radar_tracks_cache: tuple[dict[str, int | float], ...]
  _radar_tracks_cache_initialized: bool

  def __init__(self, CP: structs.CarParams, params: Params):
    ModelStateBase.__init__(self)
    self.CP = CP
    self.params = params
    self._param_update_time: float = 0.0
    self.blinker_pause_lateral = BlinkerPauseLateral()

    cloudlog.info("controlsd_ext is waiting for CarParamsSP")
    self.CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
    cloudlog.info("controlsd_ext got CarParamsSP")

    self.sm_services_ext = ['radarState', 'selfdriveStateSP', 'liveTracks']
    self.pm_services_ext = ['carControlSP']
    self._reset_radar_track_cache()

  def _reset_radar_track_cache(self) -> None:
    self._radar_tracks_active = False
    self._radar_tracks_cache = ()
    self._radar_tracks_cache_initialized = False

  def initialize_lateral_control(self, lac, CI, dt):
    enforce_torque_control = self.params.get_bool("EnforceTorqueControl")
    torque_versions = self.params.get("TorqueControlTune")
    if not enforce_torque_control:
      if self.CP.lateralTuning.which() == 'torque':
        return LatControlTorqueV0(self.CP, self.CP_SP, CI, dt)  # FIXME-SP: revert when upstream fixes tuning issues with v1
      return lac

    if torque_versions == 0.0:  # v0
      return LatControlTorqueV0(self.CP, self.CP_SP, CI, dt)
    else:
      return lac

  def get_params_sp(self, sm: messaging.SubMaster) -> None:
    if time.monotonic() - self._param_update_time > PARAMS_UPDATE_PERIOD:
      self.blinker_pause_lateral.get_params()

      if self.CP.lateralTuning.which() == 'torque':
        self.lat_delay = get_lat_delay(self.params, sm["liveDelay"].lateralDelay)

      self._param_update_time = time.monotonic()

  def get_lat_active(self, sm: messaging.SubMaster) -> bool:
    if self.blinker_pause_lateral.update(sm['carState']):
      return False

    ss_sp = sm['selfdriveStateSP']
    if ss_sp.mads.available:
      return bool(ss_sp.mads.active)

    # MADS not available, use stock state to engage
    return bool(sm['selfdriveState'].active)

  @staticmethod
  def get_lead_data(_lead, src: log.RadarState.LeadData) -> None:
    _lead.dRel = src.dRel
    _lead.yRel = src.yRel
    _lead.vRel = src.vRel
    _lead.aRel = src.deprecated.aRel
    _lead.vLead = src.vLead
    _lead.dPath = src.deprecated.dPath
    _lead.vLat = src.deprecated.vLat
    _lead.vLeadK = src.vLeadK
    _lead.aLeadK = src.aLeadK
    _lead.fcw = src.deprecated.fcw
    _lead.status = src.present
    _lead.aLeadTau = src.aLeadTau
    _lead.modelProb = src.modelProb
    _lead.radar = src.radar
    _lead.radarTrackId = src.radarTrackId

  @staticmethod
  def build_radar_track_data(live_tracks, valid: bool, model=None,
                             model_valid: bool = False) -> tuple[bool, tuple[dict[str, int | float], ...]]:
    radar_tracks_active = valid and len(live_tracks.trackSources) > 0
    if not radar_tracks_active:
      return False, ()

    source_tracks = [track for track in live_tracks.points if track.motionState in (1, 2)]
    if not source_tracks:
      return True, ()

    path_x = np.asarray(model.position.x, dtype=float) if model_valid else np.empty(0)
    path_y = np.asarray(model.position.y, dtype=float) if model_valid else np.empty(0)
    path_valid = len(path_x) >= 2 and len(path_x) == len(path_y) and np.all(np.isfinite(path_x)) and np.all(np.isfinite(path_y))
    radar_tracks = []
    for src in source_tracks:
      center_y = float(np.interp(src.dRel, path_x, path_y)) if path_valid else 0.0
      radar_tracks.append({
        "trackId": int(src.trackId),
        "dRel": float(src.dRel),
        "yRel": float(src.yRel + center_y),
        "vRel": float(src.vRel),
        "motionState": int(src.motionState),
        "age": int(src.trackAge),
      })
    return radar_tracks_active, tuple(radar_tracks)

  @staticmethod
  def set_radar_track_data(CC_SP: custom.CarControlSP, active: bool,
                           radar_tracks: tuple[dict[str, int | float], ...]) -> None:
    CC_SP.radarTracksActive = active
    CC_SP.radarTracks = radar_tracks

  @classmethod
  def get_radar_track_data(cls, CC_SP: custom.CarControlSP, live_tracks, valid: bool,
                           model=None, model_valid: bool = False) -> None:
    active, radar_tracks = cls.build_radar_track_data(live_tracks, valid, model, model_valid)
    cls.set_radar_track_data(CC_SP, active, radar_tracks)

  def update_radar_track_cache(self, live_tracks, valid: bool, model=None,
                               model_valid: bool = False, inputs_updated: bool = True) -> None:
    if self._radar_tracks_cache_initialized and not inputs_updated:
      return

    self._radar_tracks_active, self._radar_tracks_cache = self.build_radar_track_data(
      live_tracks, valid, model, model_valid,
    )
    self._radar_tracks_cache_initialized = True

  def state_control_ext(self, sm: messaging.SubMaster) -> custom.CarControlSP:
    CC_SP = custom.CarControlSP.new_message()

    self.get_lead_data(CC_SP.leadOne, sm['radarState'].leadOne)
    self.get_lead_data(CC_SP.leadTwo, sm['radarState'].leadTwo)
    self.update_radar_track_cache(
      sm['liveTracks'], sm.valid['liveTracks'], sm['modelV2'], sm.valid['modelV2'],
      sm.updated['liveTracks'] or sm.updated['modelV2'],
    )
    self.set_radar_track_data(CC_SP, self._radar_tracks_active, self._radar_tracks_cache)

    # MADS state
    mads_src = sm['selfdriveStateSP'].mads
    CC_SP.mads.state = mads_src.state
    CC_SP.mads.enabled = mads_src.enabled
    CC_SP.mads.active = mads_src.active
    CC_SP.mads.available = mads_src.available

    # ICBM state
    icbm_src = sm['selfdriveStateSP'].intelligentCruiseButtonManagement
    CC_SP.intelligentCruiseButtonManagement.state = icbm_src.state
    CC_SP.intelligentCruiseButtonManagement.sendButton = icbm_src.sendButton
    CC_SP.intelligentCruiseButtonManagement.vTarget = icbm_src.vTarget

    return CC_SP

  @staticmethod
  def publish_ext(CC_SP: custom.CarControlSP, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    cc_sp_send = messaging.new_message('carControlSP')
    cc_sp_send.valid = sm['carState'].canValid
    cc_sp_send.carControlSP = CC_SP

    pm.send('carControlSP', cc_sp_send)

  def run_ext(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    CC_SP = self.state_control_ext(sm)
    self.publish_ext(CC_SP, sm, pm)

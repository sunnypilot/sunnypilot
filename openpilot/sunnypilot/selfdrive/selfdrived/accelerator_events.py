"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Onroad events for an accelerator that joins mid-drive. The native big model block
expects a board loaded before the first modelV2; an off-board one joins onto a
modelV2 the small model already publishes and can leave and come back.
"""
import openpilot.cereal.messaging as messaging
from openpilot.cereal import custom
from openpilot.selfdrive.selfdrived.events import Events, EventName
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventNameSP = custom.OnroadEventSP.EventName
AcceleratorState = custom.ModelDataV2SP.AcceleratorState


class AcceleratorEvents:
  def __init__(self):
    self.big_model_available = False
    self.big_model_running = False
    self.link_lost = False

  def update(self, sm: messaging.SubMaster, enabled: bool, events: Events, events_sp: EventsSP) -> None:
    status = sm['modelDataV2SP']

    # stale status does not rearm the chime; only a fresh unavailable state does
    if all(sm.seen[s] and sm.alive[s] and sm.valid[s] for s in ('modelV2', 'modelDataV2SP')):
      available = status.bigModelAvailable and not sm['modelV2'].big
      if available and not self.big_model_available:
        events_sp.add(EventNameSP.bigModelAvailable)
      self.big_model_available = available

    # a join holding modelV2 back keeps the driver out, as the native load does; a late join never blocks
    if status.acceleratorState == AcceleratorState.joining and not sm.alive['modelV2']:
      events.add(EventName.bigModelLoading)

    # a chestnut dropping modelV2.big already raises the native bigModelFailed
    running_big = sm.alive['modelV2'] and sm.valid['modelV2'] and sm['modelV2'].big and \
      status.acceleratorState != AcceleratorState.none
    # a fall while engaged is a soft disable, latched until disengage since the state machine
    # cancels a soft disable the tick its event disappears. bigModelFailed drives the main
    # state machine, bigModelLinkLost drives MADS and carries the guidance
    if self.big_model_running and not running_big and enabled:
      self.link_lost = True
    self.big_model_running = running_big
    if not enabled:
      self.link_lost = False
    if self.link_lost:
      events.add(EventName.bigModelFailed)
      events_sp.add(EventNameSP.bigModelLinkLost)

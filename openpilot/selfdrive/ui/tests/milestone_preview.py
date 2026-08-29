#!/usr/bin/env python3
"""Publish deterministic milestone events for the local comma-four UI preview."""

import itertools
import time

from openpilot.cereal import messaging


def main() -> None:
  pm = messaging.PubMaster(["assistedDrivingMilestoneState"])
  milestones = itertools.cycle(((1, 0, "mads"), (2, 1, "fullAssist"), (5, 2, "mads"), (10, 5, "fullAssist")))
  event_id = 0
  milestone, previous_milestone, category = 0, 0, "mads"
  next_event_time = time.monotonic() + 1.0

  while True:
    now = time.monotonic()
    if now >= next_event_time:
      event_id += 1
      milestone, previous_milestone, category = next(milestones)
      next_event_time = now + 6.0

    msg = messaging.new_message("assistedDrivingMilestoneState")
    state = msg.assistedDrivingMilestoneState
    state.enabled = True
    if event_id:
      state.event.id = event_id
      state.event.category = category
      state.event.distanceMeters = milestone * 1609.344
      state.event.previousDistanceMeters = previous_milestone * 1609.344
      state.event.unit = "imperial"
    pm.send("assistedDrivingMilestoneState", msg)
    time.sleep(0.1)


if __name__ == "__main__":
  main()

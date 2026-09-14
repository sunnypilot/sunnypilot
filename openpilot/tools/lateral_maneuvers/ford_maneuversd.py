#!/usr/bin/env python3
"""Run the existing lateral maneuver suite through one Ford output at a time."""
from openpilot.tools.lateral_maneuvers.lateral_maneuversd import main


if __name__ == '__main__':
  main(ford_channels=True)

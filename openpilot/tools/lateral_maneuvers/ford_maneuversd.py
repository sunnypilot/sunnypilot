#!/usr/bin/env python3
"""Run the existing lateral maneuver suite through one Ford output at a time."""
from openpilot.tools.lateral_maneuvers.lateral_maneuversd import main as suite_main
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.ford_channel_test import KEYBOARD_PARAM
from openpilot.tools.lateral_maneuvers.ford_keyboard import main as keyboard_main


def main():
  if Params().get_bool(KEYBOARD_PARAM):
    keyboard_main()
  else:
    suite_main(ford_channels=True)


if __name__ == '__main__':
  main()

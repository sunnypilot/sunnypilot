#!/usr/bin/env python3
import os
import argparse
import threading
import numpy as np
try:
  import pygame as pg
except ImportError:
  print("pygame is not installed. Please install it with 'uv pip install pygame'")

from cereal import messaging
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.system.hardware import HARDWARE
from openpilot.tools.lib.kbhit import KBHit

# Set SDL environment variable to avoid using a video driver for headless operation
os.environ["SDL_VIDEODRIVER"] = "dummy"

EXPO = 0.4  # Exponential factor for joystick response curve


class Keyboard:
  def __init__(self):
    self.kb = KBHit()
    self.axis_increment = 0.05  # 5% of full actuation each key press
    self.axes_map = {'w': 'gb', 's': 'gb',
                     'a': 'steer', 'd': 'steer'}
    self.axes_values = {'gb': 0., 'steer': 0.}
    self.axes_order = ['gb', 'steer']
    self.cancel = False

  def update(self):
    key = self.kb.getch().lower()
    self.cancel = False
    if key == 'r':
      self.axes_values = dict.fromkeys(self.axes_values, 0.)
    elif key == 'c':
      self.cancel = True
    elif key in self.axes_map:
      axis = self.axes_map[key]
      incr = self.axis_increment if key in ['w', 'a'] else -self.axis_increment
      self.axes_values[axis] = float(np.clip(self.axes_values[axis] + incr, -1, 1))
    else:
      return False
    return True


class PyGameJoystick:
  def __init__(self):
    # Initialize pygame and joystick subsystem
    pg.init()
    if not pg.joystick.get_init():
      pg.joystick.init()

    # Find connected joysticks
    joystick_count = pg.joystick.get_count()
    if joystick_count == 0:
      print("No joysticks found. Please connect a controller.")
      exit(1)

    # Initialize the first joystick
    self.joystick = pg.joystick.Joystick(0)
    self.joystick.init()

    print(f"Using joystick: {self.joystick.get_name()}")
    print(f"Number of axes: {self.joystick.get_numaxes()}")
    print(f"Number of buttons: {self.joystick.get_numbuttons()}")
    print(f"Number of hats: {self.joystick.get_numhats()}")

    # This supports PlayStation and Xbox controllers on different platforms
    if HARDWARE.get_device_type() == 'pc':
      # Xbox mapping on PC
      self.accel_axis = 5  # Right trigger
      self.brake_axis = 4  # Left trigger
      self.steer_axis = 0  # Left stick horizontal
      self.cancel_button = 3  # Y/Triangle button
    else:
      # PlayStation mapping on comma device
      self.accel_axis = 5  # R2
      self.brake_axis = 4  # L2
      self.steer_axis = 0  # Left stick horizontal
      self.cancel_button = 3  # Triangle button

    # Configure for adaptive mappings based on detected controller
    controller_name = self.joystick.get_name().lower()
    if "xbox" in controller_name:
      print("Xbox controller detected, using Xbox mappings")
      self.accel_axis = 5  # Right trigger (RT)
      self.brake_axis = 4  # Left trigger (LT)
      self.cancel_button = 3  # Y button
    elif "playstation" in controller_name or "dual" in controller_name:
      print("PlayStation controller detected, using PlayStation mappings")
      self.accel_axis = 5  # R2
      self.brake_axis = 4  # L2
      self.cancel_button = 3  # Triangle

    # Initialize values
    self.axes_values = {'gb': 0., 'steer': 0.}  # Maintain same keys as Keyboard class
    self.axes_order = ['gb', 'steer']  # Match expected format
    self.cancel = False
    self.deadzone = 0.03  # 3% deadzone for noisy joysticks

    # Process events once to clear the event queue
    pg.event.pump()

  def update(self):
    # Process pygame events
    try:
      for event in pg.event.get():
        if event.type == pg.JOYDEVICEREMOVED:
          if event.instance_id == self.joystick.get_instance_id():
            print("Joystick disconnected!")
            self.axes_values = {'gb': 0., 'steer': 0.}
            return False

        elif event.type == pg.JOYBUTTONDOWN:
          if event.button == self.cancel_button:
            self.cancel = True

        elif event.type == pg.JOYBUTTONUP:
          if event.button == self.cancel_button:
            self.cancel = False
    except Exception as e:
      print(f"Error processing events: {e}")
      return False

    # Read current joystick state directly
    try:
      if not self.joystick.get_init():
        print("Joystick not initialized")
        return False

      # Read steering (left stick horizontal)
      steer_raw = self.joystick.get_axis(self.steer_axis) * -1
      steer = steer_raw if abs(steer_raw) > self.deadzone else 0.0

      # Read gas (right trigger)
      accel_raw = self.joystick.get_axis(self.accel_axis)
      # Convert from [-1, 1] to [0, 1] range (triggers often start at -1 when not pressed)
      accel = (accel_raw + 1) / 2 if self.accel_axis in [4, 5] else accel_raw
      accel = accel if accel > self.deadzone else 0.0

      # Read brake (left trigger)
      brake_raw = self.joystick.get_axis(self.brake_axis)
      # Convert from [-1, 1] to [0, 1] range (triggers often start at -1 when not pressed)
      brake = (brake_raw + 1) / 2 if self.brake_axis in [4, 5] else brake_raw
      brake = brake if brake > self.deadzone else 0.0

      # Apply expo for steering
      self.axes_values['steer'] = EXPO * steer**3 + (1 - EXPO) * steer  # Apply expo for fine control

      # Calculate combined gas/brake value for output [-1, 1] where negative is brake
      self.axes_values['gb'] = accel - brake

    except Exception as e:
      print(f"Error reading joystick: {e}")
      self.axes_values = {'gb': 0., 'steer': 0.}
      return False
    return True


def send_thread(joystick):
  pm = messaging.PubMaster(['testJoystick'])
  rk = Ratekeeper(100, print_delay_threshold=None)

  while True:
    if rk.frame % 20 == 0:
      print('\n' + ', '.join(f'{name}: {round(v, 3)}' for name, v in joystick.axes_values.items()))

    joystick_msg = messaging.new_message('testJoystick')
    joystick_msg.valid = True
    joystick_msg.testJoystick.axes = [joystick.axes_values[ax] for ax in joystick.axes_order]

    pm.send('testJoystick', joystick_msg)
    rk.keep_time()


def joystick_control_thread(joystick):
  Params().put_bool('JoystickDebugMode', True)
  threading.Thread(target=send_thread, args=(joystick,), daemon=True).start()
  while True:
    joystick.update()


def main():
  joystick_control_thread(PyGameJoystick())

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Publishes events from your joystick to control your car.\n' +
                                               'openpilot must be offroad before starting joystick_control. This tool supports ' +
                                               'PlayStation and Xbox controllers on various platforms.',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--keyboard', action='store_true', help='Use your keyboard instead of a joystick')
  args = parser.parse_args()

  if not Params().get_bool("IsOffroad") and "ZMQ" not in os.environ:
    print("The car must be off before running joystick_control.")
    exit()

  print()
  if args.keyboard:
    print('Gas/brake control: `W` and `S` keys')
    print('Steering control: `A` and `D` keys')
    print('Buttons')
    print('- `R`: Resets axes')
    print('- `C`: Cancel cruise control')
    joystick_control_thread(Keyboard())
  else:
    print('Using pygame joystick')
    print('Standard controller mapping:')
    print('- Left stick: Steering')
    print('- Right trigger (R2): Gas')
    print('- Left trigger (L2): Brake')
    print('- Triangle/Y button: Cancel')
    joystick_control_thread(PyGameJoystick())

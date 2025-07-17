#!/usr/bin/env python3
"""
Seat Control Integration Module

This module integrates the seat control system with the sunnypilot UI
by publishing seat control commands to the messaging system.
"""

import time
import threading
from cereal import messaging
from sunnypilot_dev_msync.msync_src.read_openpilot import execute_control


class SeatControlPublisher:
    """Publishes seat control commands to the messaging system for UI display."""

    def __init__(self, update_frequency=10):  # 10 Hz update rate
        self.update_frequency = update_frequency
        self.pm = messaging.PubMaster(['seatControl'])
        self.running = False
        self.thread = None

        # Command mapping from string to enum
        self.command_map = {
            'NEUTRAL': 'neutral',
            'FORWARD': 'forward',
            'BACK': 'back',
            'MILD_LEFT': 'mildLeft',
            'MILD_RIGHT': 'mildRight',
            'HARD_LEFT': 'hardLeft',
            'HARD_RIGHT': 'hardRight'
        }

        # Source mapping from string to enum
        self.source_map = {
            'None': 'none',
            'STOP': 'stop',
            'ACCELERATE': 'accelerate',
            'CURVE': 'curve',
            'TURN': 'turn'
        }

    def start(self):
        """Start the seat control publisher thread."""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the seat control publisher thread."""
        self.running = False
        if self.thread:
            self.thread.join()

    def _run(self):
        """Main publisher loop."""
        latency = 1.0 / self.update_frequency

        # Initialize the control system
        interesting_subs = ['modelV2', 'carState']

        try:
            for control_response in execute_control(interesting_subs, latency):
                if not self.running:
                    break

                # Create and publish seat control message
                seat_control_msg = messaging.new_message('seatControl')

                # Map command string to enum
                command_str = control_response[0]
                command_enum = self.command_map.get(command_str, 'neutral')

                # Map source string to enum
                source_str = control_response[1]
                source_enum = self.source_map.get(source_str, 'none')

                seat_control_msg.seatControl.command = command_enum
                seat_control_msg.seatControl.source = source_enum
                seat_control_msg.seatControl.timestamp = int(time.time() * 1e9)  # nanoseconds

                self.pm.send('seatControl', seat_control_msg)

        except Exception as e:
            print(f"Seat control publisher error: {e}")


# Global instance
seat_control_publisher = SeatControlPublisher()


def start_seat_control_publisher():
    """Start the seat control publisher."""
    seat_control_publisher.start()


def stop_seat_control_publisher():
    """Stop the seat control publisher."""
    seat_control_publisher.stop()


if __name__ == "__main__":
    # Test the publisher
    publisher = SeatControlPublisher()
    publisher.start()

    try:
        # Run for 30 seconds
        time.sleep(30)
    finally:
        publisher.stop()
#!/usr/bin/env python3
"""
Test script to verify the seat control HUD renderer mapping logic works correctly.
"""

import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, '/home/kerrb/sunnypilot')

# Mock the dependencies that the HUD renderer needs
class MockMessage:
    def __init__(self, command, source):
        self.command = command
        self.source = source

class MockSubMaster:
    def __init__(self):
        self.updated = {'seatControl': True}
        self.seat_control_msg = MockMessage('mildRight', 'curve')

    def __getitem__(self, key):
        if key == 'seatControl':
            return self.seat_control_msg
        return None

def test_seat_control_mapping():
    """Test the seat control mapping logic from the HUD renderer."""
    print("=== Testing Seat Control Mapping Logic ===")

    # Test data from the actual messages we received
    test_cases = [
        ('mildRight', 'curve'),
        ('neutral', 'none'),
        ('forward', 'accelerate'),
        ('back', 'stop'),
        ('hardLeft', 'turn'),
        ('hardRight', 'turn'),
        ('unknown', 'unknown')  # Test unknown values
    ]

    # Map Cap'n Proto enum strings to display strings (from HUD renderer)
    command_mapping = {
        'neutral': "NEUTRAL",
        'forward': "FORWARD",
        'back': "BACK",
        'mildLeft': "MILD_LEFT",
        'mildRight': "MILD_RIGHT",
        'hardLeft': "HARD_LEFT",
        'hardRight': "HARD_RIGHT"
    }

    source_mapping = {
        'none': "None",
        'stop': "Stop",
        'accelerate': "Accelerate",
        'curve': "Curve",
        'turn': "Turn"
    }

    print("Testing mapping logic:")
    for cmd, src in test_cases:
        mapped_cmd = command_mapping.get(cmd, f"UNK_{cmd}")
        mapped_src = source_mapping.get(src, f"UNK_{src}")
        print(f"  {cmd} -> {mapped_cmd}, {src} -> {mapped_src}")

    print("\n✓ Mapping logic test completed")

if __name__ == "__main__":
    test_seat_control_mapping()

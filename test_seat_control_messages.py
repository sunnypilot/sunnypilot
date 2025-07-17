#!/usr/bin/env python3
"""
Test script to verify seat control messages are being published and received correctly.
"""

import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, '/home/kerrb/sunnypilot')

try:
    from cereal import messaging
    print("✓ Successfully imported messaging")
except ImportError as e:
    print(f"✗ Failed to import messaging: {e}")
    sys.exit(1)

def test_seat_control_messages():
    """Test if seat control messages are being published and received."""
    print("\n=== Testing Seat Control Messaging ===")

    try:
        # Create subscriber
        print("Creating SubMaster for seatControl...")
        sm = messaging.SubMaster(['seatControl'])
        print("✓ SubMaster created successfully")

        # Check if service is in the updated dict
        print(f"Updated dict keys: {list(sm.updated.keys())}")

        if 'seatControl' in sm.updated:
            print("✓ seatControl service found in SubMaster")
        else:
            print("✗ seatControl service NOT found in SubMaster")
            return

        # Listen for messages
        print("\nListening for seat control messages (10 seconds)...")
        start_time = time.time()
        message_count = 0

        while time.time() - start_time < 10:
            sm.update()

            if sm.updated['seatControl']:
                message_count += 1
                seat_control = sm['seatControl']
                print(f"Message {message_count}: command={seat_control.command}, source={seat_control.source}")

            time.sleep(0.1)

        print(f"\nReceived {message_count} messages in 10 seconds")

        if message_count == 0:
            print("✗ No seat control messages received")
        else:
            print("✓ Seat control messages are being received")

    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_seat_control_messages()

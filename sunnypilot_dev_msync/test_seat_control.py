#!/usr/bin/env python3
"""
Test Seat Control Messaging

This script tests the seat control messaging system by sending test commands
and verifying they are received correctly.
"""

import sys
import os
import time
import threading

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from cereal import messaging
from sunnypilot_dev_msync.seat_control_integration import SeatControlPublisher


def test_publisher():
    """Test the seat control publisher."""
    print("Testing seat control publisher...")

    # Create publisher
    publisher = SeatControlPublisher(update_frequency=5)

    # Create subscriber to monitor messages
    sm = messaging.SubMaster(['seatControl'])

    try:
        # Start publisher
        publisher.start()

        # Monitor messages for 10 seconds
        start_time = time.time()
        message_count = 0

        while time.time() - start_time < 10:
            sm.update(timeout=100)

            if sm.updated['seatControl']:
                seat_control = sm['seatControl']
                message_count += 1

                print(f"Message #{message_count}:")
                print(f"  Command: {seat_control.command}")
                print(f"  Source: {seat_control.source}")
                print(f"  Timestamp: {seat_control.timestamp}")
                print()

            time.sleep(0.1)

        print(f"Received {message_count} messages in 10 seconds")

    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        publisher.stop()


def test_manual_publisher():
    """Test manual message publishing."""
    print("Testing manual message publishing...")

    pm = messaging.PubMaster(['seatControl'])

    # Test different commands
    test_commands = [
        ('neutral', 'none'),
        ('forward', 'accelerate'),
        ('back', 'stop'),
        ('mildLeft', 'curve'),
        ('mildRight', 'curve'),
        ('hardLeft', 'turn'),
        ('hardRight', 'turn'),
    ]

    for command, source in test_commands:
        msg = messaging.new_message('seatControl')
        msg.seatControl.command = command
        msg.seatControl.source = source
        msg.seatControl.timestamp = int(time.time() * 1e9)

        pm.send('seatControl', msg)
        print(f"Sent: {command} from {source}")
        time.sleep(0.5)

    print("Manual test completed")


def test_subscriber():
    """Test the seat control subscriber."""
    print("Testing seat control subscriber...")
    print("Listening for seat control messages for 10 seconds...")

    sm = messaging.SubMaster(['seatControl'])

    start_time = time.time()
    message_count = 0

    try:
        while time.time() - start_time < 10:
            sm.update(timeout=100)

            if sm.updated['seatControl']:
                seat_control = sm['seatControl']
                message_count += 1

                print(f"Received message #{message_count}:")
                print(f"  Command: {seat_control.command}")
                print(f"  Source: {seat_control.source}")
                print(f"  Timestamp: {seat_control.timestamp}")
                print()

    except KeyboardInterrupt:
        print("Test interrupted")

    print(f"Received {message_count} messages in 10 seconds")


def main():
    print("Seat Control Messaging Test")
    print("=" * 40)

    if len(sys.argv) > 1:
        test_type = sys.argv[1]

        if test_type == "publisher":
            test_publisher()
        elif test_type == "manual":
            test_manual_publisher()
        elif test_type == "subscriber":
            test_subscriber()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available tests: publisher, manual, subscriber")
    else:
        print("Usage: python test_seat_control.py [publisher|manual|subscriber]")
        print()
        print("Tests:")
        print("  publisher  - Test the full publisher system")
        print("  manual     - Test manual message publishing")
        print("  subscriber - Test message receiving")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Seat Control Service

This service runs as a background process to publish seat control commands
to the messaging system for UI display.
"""

import argparse
import sys
import os
import signal
import time

from sunnypilot_dev_msync.seat_control_integration import SeatControlPublisher


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("Received shutdown signal, stopping seat control service...")
    global publisher
    if publisher:
        publisher.stop()
    sys.exit(0)


def main():
    global publisher

    parser = argparse.ArgumentParser(description='Seat Control Service')
    parser.add_argument('--frequency', type=int, default=10, help='Update frequency in Hz')
    args = parser.parse_args()

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start the publisher
    publisher = SeatControlPublisher(update_frequency=args.frequency)

    try:
        print(f"Starting seat control service at {args.frequency} Hz")
        publisher.start()

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down seat control service...")
        publisher.stop()
        sys.exit(0)
    except Exception as e:
        print(f"Error in seat control service: {e}")
        publisher.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()

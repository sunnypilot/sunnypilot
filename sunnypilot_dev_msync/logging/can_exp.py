from openpilot.openpilot_dev_msync.logging.log_constants import MESSAGE_TYPES
from openpilot.selfdrive.debug.can_printer import CanPrinter
import os

def main(bus, max_msg, addr):
    can_printer = CanPrinter(bus, max_msg, addr)
    can_printer.run()

if __name__ == "__main__":
    bus = "0"
    max_msg = None
    addr = "127.0.0.1"

    print(f"Experimenting with CAN data on bus {bus} at {addr}\n")
    main(bus, max_msg, addr)

import cantools
import os
import re
import sys

car = "toyota_tss2_adas"
dbc_file = './openpilot_dev_msync/data/' + car + '.dbc'
log_file = None  # Set to None to read from stdin
out_file = None  # Set to None if you don't want to write to a file
db = cantools.database.load_file(dbc_file)
line_re = re.compile(r'^([0-9A-Fa-f]{4})\([^\)]*\)\([^\)]*\)\([^\)]*\)\s+([0-9A-Fa-f]+)')
interesting_signals = ["VXFR", "VXRR", "VXFL", "VXRL"]
# interesting_signals = ["SSA", "SSAS", "SSAV", "INTG"]
interesting_signals = ["LONG_DIST", "LAT_DIST", "REL_ACCEL", "REL_SPEED"]

def interesting(sig):
    return sig.name in interesting_signals

def parse_logs(regex, log_file=None, out_file=None):
    infile = open(log_file) if log_file else sys.stdin
    out_f = open(out_file, 'w') if out_file else None

    for line in infile:
        m = regex.match(line)
        if not m:
            continue
        can_id = int(m.group(1), 16)
        data = bytes.fromhex(m.group(2))
        try:
            msg = db.get_message_by_frame_id(can_id)
            decoded = msg.decode(data)
            output = f"{msg.name} ({hex(can_id)}): {decoded}\n"
            if out_f:
                out_f.write(output)
            # Print detailed signal info
            is_valid = decoded.get("VALID", 1)
            if not is_valid:
                continue
            for signal in msg.signals:
                unit = signal.unit if signal.unit else ''
                value = decoded.get(signal.name, 'N/A')
                if interesting(signal):
                    print(f"Signal: {signal.name} {unit}, Value: {value} {signal.unit}\n")
        except Exception:
            continue

    if out_f:
        out_f.close()

def constant_parse(regex, log_file=None):
    infile = open(log_file) if log_file else sys.stdin
    signal_values = dict.fromkeys(interesting_signals)
    # Print initial blank lines for each signal
    print('\n' * (len(interesting_signals) - 1))

    for line in infile:
        m = regex.match(line)
        if not m:
            continue
        can_id = int(m.group(1), 16)
        data = bytes.fromhex(m.group(2))
        try:
            msg = db.get_message_by_frame_id(can_id)
            decoded = msg.decode(data)
            is_valid = decoded.get("VALID", 1)
            if not is_valid:
                continue


            for signal in msg.signals:
                if interesting(signal):
                    value = decoded.get(signal.name, 'N/A')
                    signal_values[signal.name] = value

            # Move cursor up N lines
            sys.stdout.write(f"\033[{len(interesting_signals)}A")
            # Print each signal on its own line, padded for alignment
            for sig in interesting_signals:
                val = signal_values[sig]
                if isinstance(val, float):
                    val_str = f"{val:.4f}"
                else:
                    val_str = str(val)
                # Find the signal object to get its unit
                signal_obj = next((s for m in db.messages for s in m.signals if s.name == sig), None)
                unit_str = f" [{signal_obj.unit}]" if signal_obj and signal_obj.unit else ""
                sys.stdout.write(f"{sig.ljust(12)}{unit_str.ljust(8)}: {val_str.ljust(12)}\n")
            sys.stdout.flush()

        except Exception:
            continue

if __name__ == "__main__":
    # parse_logs(line_re, log_file, out_file)
    constant_parse(line_re, log_file)

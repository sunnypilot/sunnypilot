from openpilot.tools.lib.logreader import LogReader
from openpilot.openpilot_dev_msync.log_constants import MESSAGE_TYPES
from openpilot.selfdrive.debug.can_printer import CanPrinter
import openpilot.selfdrive.debug.dump
import os

CHUNK_PATH = "comma2k19/Chunk_1/b0c9d2329ad1606b"

def gather_types(sub_dirs):
    """Gather unique message types from all subdirectories."""
    types = set()
    for sub_dir in sub_dirs:
        for seg in os.listdir(os.path.join(os.getcwd(), CHUNK_PATH, sub_dir)):
            seg_path = os.path.join(os.getcwd(), CHUNK_PATH, sub_dir, seg)
            lr = LogReader(seg_path + "/raw_log.bz2")
            for msg in lr:
                t = msg.which()
                if t not in types:
                    print(msg)
                types.add(t)
    return types

def unique_types(lr):
    """Collect unique message types from the log reader."""
    types = {msg.which() for msg in lr} # Collect unique message types
    for t in types:
      print(f"Type: {t}")
      for msg in lr:
        if msg.which() == t:
          print(msg)
          break
    return types

def read_local(data_dir, segments):
    for s in segments:
        log_path = os.path.join(data_dir, s, "raw_log.bz2")
        lr = LogReader(log_path)
        print(f"Reading segment {s}")
        unique_types(lr)



def main(sub_dir):
    print("Experimenting with log data...\n*****Chunk 1*****")
    print("Timestamp:", sub_dir)
    data_dir = os.path.join(os.getcwd(), CHUNK_PATH, sub_dir)
    segments = os.listdir(data_dir)
    segments = sorted(segments, key=lambda x: int(x))

    seg_start = 0
    seg_num = len(segments)
    seg_step = 1

    for s in range(seg_start, seg_num, seg_step):
        read_local(data_dir, segments[s:s + seg_step])
    return 0

if __name__ == "__main__":
    timestamps = os.listdir("comma2k19/Chunk_1/b0c9d2329ad1606b")
    # main(timestamps[0])
    print(gather_types(timestamps))  # Example usage of gather_types



import os
import sys
import re
import shutil
import argparse

DONGLE_ID = '52a8edf5ce93e696'
SEGMENT_NAME_RE = r'[0-9]{4}-[0-9]{2}-[0-9]{2}--[0-9]{2}-[0-9]{2}-[0-9]{2}--[0-9]+'
OP_SEGMENT_DIR_RE = r'^({})$'.format(SEGMENT_NAME_RE)


class Expander(object):
  def __init__(self, data_dir):
    self._expand_directories(data_dir)

  def _expand_directories(self, data_dir):
    files = os.listdir(data_dir)

    for f in files:
      fullpath = os.path.join(data_dir, f)
      if not os.path.isdir(fullpath):
        continue

      op_match = re.match(OP_SEGMENT_DIR_RE, f)
      if not op_match:
        continue

      subfiles = os.listdir(fullpath)
      for sf in subfiles:
        oldpath = os.path.join(fullpath, sf)
        newname = '{}|{}--{}'.format(DONGLE_ID, f, sf)
        newpath = os.path.join(data_dir, newname)
        print('Will move froom {}  to {}'.format(oldpath, newpath))
        os.rename(oldpath, newpath)

      print('Will remove source dir {}'.format(fullpath))
      shutil.rmtree(fullpath)


def get_arg_parser():
  parser = argparse.ArgumentParser(
      description="Expand downloaded segments from device into single folder",
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("data_dir", nargs='?', default=os.getenv('UNLOGGER_DATA_DIR'),
                      help="Path to directory in which log and camera files are located.")

  return parser


def main(argv):
  args = get_arg_parser().parse_args(sys.argv[1:])

  if args.data_dir is not None:
    Expander(args.data_dir)
    print("done")
  else:
    print("missing data dir")

  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))

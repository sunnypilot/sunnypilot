import os
import re
import subprocess
import tempfile
from pathlib import Path

from cffi import FFI

from opendbc.safety import LEN_TO_DLC

libsafety_dir = os.path.dirname(os.path.abspath(__file__))


def _build_libsafety(release: bool = False) -> str:
  """Compile libsafety.so to a temp file and return its path."""
  root = str(Path(libsafety_dir).parents[3])
  safety_c = os.path.join(libsafety_dir, "safety.c")

  cflags = [
    '-Wall', '-Wextra', '-Werror', '-nostdlib', '-fno-builtin',
    '-std=gnu11', '-Wfatal-errors', '-Wno-pointer-to-int-cast',
    '-g', '-O0', '-fno-omit-frame-pointer',
  ]
  # Coverage must exclude the branches inserted by UBSan.
  if os.environ.get("SAFETY_COVERAGE") == "1":
    ldflags = ['-fprofile-arcs', '-ftest-coverage'] if not release else []
  else:
    ldflags = ['-fsanitize=undefined', '-fno-sanitize-recover=undefined']
  cflags += ldflags
  if not release:
    cflags += ['-DALLOW_DEBUG']

  fd, safety_os = tempfile.mkstemp(suffix='.os', dir=libsafety_dir)
  os.close(fd)
  fd, libsafety_so = tempfile.mkstemp(suffix='.so')
  os.close(fd)

  subprocess.check_call(['cc', '-fPIC', *cflags, '-I', root, '-c', safety_c, '-o', safety_os])
  subprocess.check_call(['cc', '-shared', safety_os, '-o', libsafety_so, *ldflags])
  return libsafety_so


def cdef_from_file(path: Path) -> str:
  source = path.read_text()
  source = re.sub(r"//[^\n]*|/\*.*?\*/", "", source, flags=re.DOTALL)
  source = re.sub(r"__attribute__\(\(.*\)\)", "", source)

  # Keep integer constants, type declarations, and function signatures, including definitions.
  constants = re.findall(r"^#define \w+ \d+[UuLl]*[ \t]*$", source, re.MULTILINE)
  types = re.findall(r"^(?:typedef|struct|enum)\b(?:[^;{]|\{[^}]*\})+;", source, re.MULTILINE)
  functions = re.findall(r"^((?!typedef\b)\w[\w *]*\b\w+\([^;{}]*\))\s*[;{]", source, re.MULTILINE)
  return "\n".join([*constants, *types, *(f"{signature};" for signature in dict.fromkeys(functions))])


ffi = FFI()
safety_dir = Path(libsafety_dir).parents[1]
ffi.cdef(cdef_from_file(safety_dir / "can.h"), packed=True)
for path in (safety_dir / "declarations.h", safety_dir / "ignition.h", safety_dir / "sunnypilot" / "mads_declarations.h", Path(libsafety_dir) / "safety.c"):
  ffi.cdef(cdef_from_file(path))

class CANPacket:
  pass

# Functions not captured by cdef_from_file (macros, non-standard formatting, or generated)
ffi.cdef("""
int get_alternative_experience(void);
int get_desired_angle_last(void);
void set_honda_bosch_long(bool c);
int get_honda_hw(void);
void set_ignition_can(bool c);
uint32_t get_acc_main_on_mismatches(void);
int get_temp_debug(void);
void mutation_set_active_mutant(int id);
int mutation_get_active_mutant(void);
""")

class LibSafety:
  pass
libsafety: LibSafety

def load(path):
  global libsafety
  libsafety = ffi.dlopen(str(path))

def __getattr__(name):
  if name == "libsafety":
    load(_build_libsafety())
    return libsafety
  raise AttributeError(name)

def make_CANPacket(addr: int, bus: int, dat):
  ret = ffi.new('CANPacket_t *')
  ret[0].extended = 1 if addr >= 0x800 else 0
  ret[0].addr = addr
  ret[0].data_len_code = LEN_TO_DLC[len(dat)]
  ret[0].bus = bus
  ret[0].data = bytes(dat)
  return ret

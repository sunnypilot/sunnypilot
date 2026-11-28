# Serve test/mockgpu's usb gpu to a program that runs its real usb path (DEV=USB+AMD) through libusb_mock.c. 
import os, sys, socket, struct, subprocess, tempfile, traceback, pathlib
if sys.platform == "darwin":
  from tinygrad.runtime.autogen import libc
  def _memfd_create(name, flags):
    fd, path = tempfile.mkstemp()
    os.unlink(path)
    return fd
  libc.memfd_create = _memfd_create
from test.mockgpu.am.amdriver import AMUSBDriver
from test.mockgpu.usb import MockUSB3

CTRL_OUT, CTRL_IN, BULK_OUT, BULK_IN, PROGRESS = range(1, 6)
LIBUSB_ERROR_IO = -1

def build(out:pathlib.Path) -> pathlib.Path:
  lib = out / ("libusb_mock.dylib" if sys.platform == "darwin" else "libusb_mock.so")
  subprocess.check_call([os.getenv("CC", "cc"), "-shared", "-fPIC", "-O2", "-o", str(lib), str(pathlib.Path(__file__).with_name("libusb_mock.c"))])
  return lib

def recv(conn:socket.socket, n:int) -> bytes|None:
  buf = bytearray()
  while len(buf) < n:
    if not (b:=conn.recv(n - len(buf))): return None
    buf += b
  return bytes(buf)

def serve(conn:socket.socket, driver:AMUSBDriver, usb:MockUSB3):
  while (hdr:=recv(conn, 10)) is not None:
    op, req, value, index, n = struct.unpack("<BBHHI", hdr)
    data, out = (recv(conn, n) or b"") if op in (CTRL_OUT, BULK_OUT) else b"", b""
    try:
      if op in (CTRL_IN, BULK_IN, PROGRESS): driver.progress()
      if op == CTRL_OUT: usb.control_write(req, value, index, data)
      elif op == CTRL_IN: out = bytes(usb.control_read(req, n, value, index))
      elif op == BULK_OUT: usb.bulk_write(data)
      elif op == BULK_IN: out = bytes(usb.bulk_read(n))
      elif op != PROGRESS: raise ValueError(f"unknown op {op}")
      rc = len(out) if op in (CTRL_IN, BULK_IN) else n
    except Exception:
      traceback.print_exc()
      out, rc = b"", LIBUSB_ERROR_IO
    conn.sendall(struct.pack("<i", rc) + out)

def main(cmd:list[str]) -> int:
  with tempfile.TemporaryDirectory() as tmp:
    lib, path = build(pathlib.Path(tmp)), os.path.join(tmp, "usb.sock")
    driver, usb = AMUSBDriver(), MockUSB3()
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(path)
    srv.listen(1)
    srv.settimeout(0.5)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"} | {"LIBUSB_PATH": str(lib), "MOCKUSB_SOCKET": path}
    child = subprocess.Popen(cmd, env=env)
    while child.poll() is None:
      try: conn, _ = srv.accept()
      except socket.timeout: continue
      conn.settimeout(None)
      with conn: serve(conn, driver, usb)
    return child.wait()

if __name__ == "__main__":
  if len(sys.argv) < 2: sys.exit("usage: usb_server.py COMMAND...")
  sys.exit(main(sys.argv[1:]))

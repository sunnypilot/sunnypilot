# The Qualcomm compiler off the device (x86 CI: qemu; Apple silicon: docker) must emit the same binaries the device's own compiler does,
# or the qcom mock is exact for programs a comma device never runs. Kernel sources and their on-device binaries come from a630 compile caches.
#   on the device:  python test/device/qcom/compiler_parity.py dump CACHE.db [...] test/mockgpu/qcom/a630_compiled.pkl.xz
#   anywhere:       python test/device/qcom/compiler_parity.py check test/mockgpu/qcom/a630_compiled.pkl.xz [WORKERS]
import sys, os, sqlite3, pickle, lzma, hashlib
from concurrent.futures import ProcessPoolExecutor

def dump(dbs:list[str], out:str):
  pairs:dict[str, tuple[str, bytes]] = {}
  for db in dbs:
    con = sqlite3.connect(db)
    for (table,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'compile_qcomcl%'"):
      for src, val in con.execute(f"SELECT key, val FROM '{table}'"):
        lib = pickle.loads(val)
        if src in pairs and pairs[src][1] != lib: raise RuntimeError(f"the device compiled one source two ways ({table})")
        pairs[src] = (table, lib)
  with lzma.open(out, "wb") as f: pickle.dump(sorted((t, src, lib) for src, (t, lib) in pairs.items()), f)
  print(f"{len(pairs)} sources -> {out}")

_compiler = None
def _compile(item:tuple[str, str, bytes]) -> tuple[str, str]:
  global _compiler
  from tinygrad.runtime.support.compiler_qcom import QCOMCompiler
  if _compiler is None: _compiler = QCOMCompiler("a630")
  table, src, lib = item
  try: out = _compiler.compile(src)
  except Exception as e: return "error", f"{table} {hashlib.sha256(src.encode()).hexdigest()[:12]}: {type(e).__name__}: {str(e)[:200]}"
  return ("same", "") if out == lib else ("diff", f"{table} {hashlib.sha256(src.encode()).hexdigest()[:12]}: {len(out)} vs {len(lib)} bytes")

def check(data:str, workers:int):
  with lzma.open(data, "rb") as f: items = pickle.load(f)
  import platform
  if platform.machine() != "aarch64":  # fetch and extract the compiler rootfs once, before the workers race to it
    from tinygrad.runtime.support.compiler_qcom import QCOMCompiler
    QCOMCompiler("a630").compiler_process.kill()
  with ProcessPoolExecutor(workers) as pool: res = list(pool.map(_compile, items, chunksize=4))
  for kind, msg in res:
    if kind != "same": print(kind.upper(), msg)
  same = sum(k == "same" for k, _ in res)
  print(f"{same}/{len(items)} sources compile to the device's bytes")
  if same != len(items): sys.exit(1)

if __name__ == "__main__":
  if sys.argv[1] == "dump": dump(sys.argv[2:-1], sys.argv[-1])
  else: check(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else (os.cpu_count() or 1))

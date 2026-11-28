# Writes test/mockgpu/qcom/a630_verified.sigs: the Adreno instruction signatures (emu.adreno_signatures) of every kernel whose mock results
# were bit-identical to an Adreno 630, from probe_a630.py result dirs (one per IMAGE mode) and per-kernel replays of real models.
#   DEV=MOCK+QCOM CACHEDB=probe.db python test/device/qcom/verify_a630.py PROBES HWDIR EMUDIR IMAGE [...] [OPS HWDIR EMUDIR] [KERNELS HEXFILE]
#     [PATCH HWDIR EMUDIR BASE.lib (one per probe_patch.py template)] [-- STEPS HW_JSON_DIR EMU_JSON_DIR MODELS_DIR]
# a signature seen in any kernel that did not match is left out, so one mismatch keeps it unverified everywhere
import sys, os, glob, json, importlib.util
import numpy as np
from tinygrad.helpers import Context
import test.mockgpu.qcom.emu as emu
here = os.path.dirname(os.path.abspath(__file__))

def probe_images(case:str, image:int) -> list[bytes]:  # the shader images a probe case runs, captured from the mock
  spec = importlib.util.spec_from_file_location("probe_a630", os.path.join(here, "probe_a630.py"))
  pa = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(pa)
  seen, orig = [], emu.run
  def capture(d):
    seen.append(bytes(d.image))
    return orig(d)
  emu.run = capture
  try:
    with Context(IMAGE=image):
      gens, fn = pa.CASES[case]
      fn(*[pa.T(g(case, i)) for i, g in enumerate(gens)]).realize()
  finally: emu.run = orig
  return seen

def captured(run) -> list[bytes]:  # the shader images the mock runs while run() executes
  seen, orig = [], emu.run
  def capture(d):
    seen.append(bytes(d.image))
    return orig(d)
  emu.run = capture
  try: run()
  finally: emu.run = orig
  return seen

def ops_images(case:str) -> list[bytes]:
  spec = importlib.util.spec_from_file_location("probe_ops", os.path.join(here, "probe_ops.py"))
  po = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(po)
  from tinygrad import Tensor
  dts, fn = po.cases()[case]
  def go():
    with Context(**po.flags(case)): fn(*[Tensor(po.gen(dt, case, i)) for i, dt in enumerate(dts)]).realize()
  return captured(go)

def same(a:str, b:str) -> bool|None:
  x, y = np.load(a), np.load(b)
  if "error" in x.files or "error" in y.files: return None
  return int(x["inhash"]) == int(y["inhash"]) and x["out"].shape == y["out"].shape and np.array_equal(x["out"].view(np.uint8), y["out"].view(np.uint8))

def main(argv:list[str]):
  good, bad = set(), set()
  ops = argv[argv.index("OPS") + 1:argv.index("OPS") + 3] if "OPS" in argv else []
  if ops: argv = argv[:argv.index("OPS")] + argv[argv.index("OPS") + 3:]
  for f in sorted(glob.glob(os.path.join(ops[0], "*.npz"))) if ops else []:  # probe_ops.py: every tinygrad op and cast
    g = os.path.join(ops[1], os.path.basename(f))
    if not os.path.exists(g) or (ok := same(f, g)) is None: continue
    (good if ok else bad).update(s for img in ops_images(os.path.basename(f)[:-4]) for s in emu.adreno_signatures(img))
  extra = argv[argv.index("KERNELS") + 1:argv.index("KERNELS") + 2] if "KERNELS" in argv else []
  if extra: argv = argv[:argv.index("KERNELS")] + argv[argv.index("KERNELS") + 2:]
  for f in extra:  # a whole model run (e.g. driver monitoring) that matched the a630 end to end: one shader image per line, hex
    good.update(s for line in open(f) if line.strip() for s in emu.adreno_signatures(bytes.fromhex(line.strip())))
  patches = []  # one PATCH group per probe_patch.py template
  while "PATCH" in argv:
    patches.append(argv[argv.index("PATCH") + 1:argv.index("PATCH") + 4])
    argv = argv[:argv.index("PATCH")] + argv[argv.index("PATCH") + 4:]
  if "--" in argv: probes, steps = argv[:argv.index("--")], argv[argv.index("--") + 1:]
  else: probes, steps = argv, []
  for patch in patches:
    for f in sorted(glob.glob(os.path.join(patch[0], "*.npz"))):  # single encodings from probe_patch.py
      g = os.path.join(patch[1], os.path.basename(f))
      if not os.path.exists(g) or "error" in np.load(f).files or "error" in np.load(g).files: continue  # refused by the mock: never verified
      sigs = set(emu.adreno_signatures(int(np.load(f)["word"]).to_bytes(8, "little")))
      if os.path.basename(f) == "orig.npz":  # the template matching vouches for its own instructions
        sigs |= set(emu.adreno_signatures(emu.qcom_image(open(patch[2], "rb").read())))
      (good if np.array_equal(np.load(f)["out"], np.load(g)["out"]) else bad).update(sigs)
  assert probes[0] == "PROBES"
  for i in range(1, len(probes), 3):
    hw, em, image = probes[i], probes[i + 1], int(probes[i + 2])
    for f in sorted(glob.glob(os.path.join(hw, "*.npz"))):
      g = os.path.join(em, os.path.basename(f))
      if not os.path.exists(g) or (ok := same(f, g)) is None: continue
      sigs = {s for img in probe_images(os.path.basename(f)[:-4], image) for s in emu.adreno_signatures(img)}
      (good if ok else bad).update(sigs)
  if steps:
    from openpilot.sunnypilot.modeld_v2.helpers import read_parts
    assert steps[0] == "STEPS"
    hw_dir, emu_dir, models = steps[1:4]
    for f in sorted(glob.glob(os.path.join(hw_dir, "*.json"))):
      g = os.path.join(emu_dir, os.path.basename(f))
      if not os.path.exists(g): continue
      name, part = os.path.basename(f)[:-5].split("_", 1)
      parts, _ = read_parts(os.path.join(models, name + ".pkl"))
      key = next(k for k in parts if "".join(c for c in repr(k).replace(" ", "") if c.isalnum() or c == "_") == part)
      header, blob = parts[key]
      tainted:set = set()  # buffers last written by a kernel that differed: a kernel reading one proves nothing either way
      def buf(d): return ("in", d["input"]) if "input" in d else ("buf", d["buffer"])
      for (i, _, hh), (_, _, eh) in zip(json.load(open(f)), json.load(open(g)), strict=True):
        call = header["calls"][i]
        outs = {buf(call["args"][o]) for o in call.get("outs", [0])} if call["kind"] == "program" else {buf(call["args"][0])}
        ins = {buf(call["args"][o]) for o in call.get("ins", [])} if call["kind"] == "program" else {buf(call["args"][1])}
        from_tainted = bool(ins & tainted)
        if hh == eh: tainted -= outs  # identical outputs are clean whatever produced them
        else: tainted |= outs
        if from_tainted or call["kind"] != "program": continue
        sigs = set(emu.adreno_signatures(emu.qcom_image(bytes(blob[slice(*call["lib"])]))))
        (good if hh == eh else bad).update(sigs)
  ok = good - bad
  out = os.path.join(here, "..", "..", "mockgpu", "qcom", "a630_verified.sigs")
  with open(out, "w") as fh:
    fh.write("# adreno 630 instruction signatures the qcom mock reproduces bit for bit; written by test/device/qcom/verify_a630.py\n")
    fh.write("".join(s + "\n" for s in sorted(ok)))
  print(f"{len(ok)} verified signatures -> {os.path.normpath(out)}; seen in a mismatching kernel: {sorted(bad)}")

if __name__ == "__main__": main(sys.argv[1:])

This prebuilt release requires rebuilding `openpilot/common/libparams_c.so` when
the compiled Params registry changes. Editing `params_keys.h` alone does not
register a key with the shipped Python API. The Python wrapper still validates
every key through the native registry.

From the checkout root, with Python 3.11+ and a Docker ARM64 Linux builder:

```sh
python3 openpilot/tools/params/rebuild.py --work-dir /tmp/sunnypilot-params-arm64
```

The script copies only the required source into that temporary directory,
verifies the three ARM64 dependency wheels against this checkout's `uv.lock`,
and builds with the pinned Debian image/compiler. The compile and test
containers have networking disabled and no repository mount. The output is
`/tmp/sunnypilot-params-arm64/out/libparams_c.so`; installation is deliberately
separate. `provenance.json`, `out/build.json` and `out/verification.json` record
the inputs, command, binary hash and checks. Existing wheel downloads are
verified and reused. An unavailable pinned package is a build error.

The checked-in `build_provenance.json` describes the shipped feature build.
The previous build preserved all 273 base key names, types, flags and raw defaults
and added five Mapbox keys. The navigation build adds only `NavModelState`;
all 278 previous registry entries were compared against the real ARM64 library
and remain identical. The status JSON clears on manager startup and going offroad. The C API exports and dynamic
library dependencies match the base release, with no increased symbol-version
requirements. The `params_keys_by_flag` correction returns distinct buffers
owned by the handle instead of aliasing one temporary string.

Verification executes all 13 original Params test method bodies, the three
buffer regressions, typed new-key round trips, asynchronous JSON writes, and
both lifecycle clears against the real ARM64 Linux library. Only logging and
the test-directory fixture are substituted. These are Linux container tests;
the library has not been executed on the vehicle device.

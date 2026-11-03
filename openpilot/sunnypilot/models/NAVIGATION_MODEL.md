# Experimental learned navigation model

The normal model selector can expose **RL Navigation80eedcdd**, compiled locally
from the exact official ONNX SHA256
`1d18c42ea4cd95c8bffab4635844b78b8e2d4e25b9de44a9c5ac2e0961371a2e`.
The ONNX pointer is present at comma commit
`afbf2e547e9319e2eb9f515e1e4330af63705cec`, but it was unchanged when that commit
updated the separate N16 PKL. This ONNX must not be described as the N16 weights.

No device model is included or selected automatically. No manifest/artifact means
no selectable entry, and the runtime reports navigation unsupported. The exact
ONNX runs on Mac CPU with five recurrent queues; that does not supply a runnable
Chestnut artifact or prove route following or curb clearance.

## Offroad target build

The following reuses this repository's existing Chestnut native-model compiler
recipe. The complete RL Navigation graph has **not yet been built or validated on
a target device** as part of this change. It requires an offroad comma device,
the supported connected Chestnut GPU, and the normal model-compilation
dependencies. The Mac ORT result is not a substitute for this check.

Obtain the ONNX by a trusted transfer and verify the exact hash above. A mirror
carrying those official bytes is:

`https://github.com/happymaj11r/openpilot-models/releases/download/big-nav-model-integration-1d18c42e/big_driving_supercombo.onnx`

Then, from the repository root on the offroad target:

```sh
python3 -m openpilot.sunnypilot.models.build_navigation_model --onnx /path/to/big_driving_supercombo.onnx
```

The installer verifies the source hash, invokes `compile_modeld_v2.py` with
`DEV=USB+AMD:LLVM`, `FRAME_DEV=CPU`, `FLOAT16=1`, `GMMU=0`, `TC_OPT=2`,
`TC_MIN_GLOBALS=32`, all inputs on-device and one benchmark run. It stops if the
device enters onroad. A failed build publishes no selector entry. After checking
the generated plain artifact's hash, target and navigation input/output protocol,
it writes the artifact and `rl_nav_80eedcdd_bundle.json` under
`Paths.model_root()`. It does not change the selected model or start a drive.

After a successful validated build, explicitly select the experimental model in
the existing Chestnut model selector while offroad. The local row survives remote
catalog refreshes, while the downloaded remote catalog stays unchanged. Removing
or changing its artifact makes the local row unavailable. Existing bundles remain
available through the ordinary selector.

## Protocol and unchanged controls

The bundle uses **generation12 as sunnypilot's existing native/action protocol**,
not as a training checkpoint number. This graph preserves the semantic CTV3
output slices, including plan990, action4, desire-state8 and desire-prediction32,
and adds map/navigation feature heads and two recurrent queues. The adapter's
float32 host layout already fits the verified map input; it is unchanged.

The existing action conversion,1.6m/s curvature hold, steering and cooperative
steering code are preserved. An unbundled `COMBINED_MODEL_PKL` override cannot
activate learned-navigation capability because its generation/control metadata
is absent. The small fallback lacks navigation inputs and reports unsupported.

Map and instruction conditioning is enabled only with matching real route
ownership/generation and fresh inputs. The automatic route must match the active
signal session, or be an explicitly retained outgoing continuation of a route
this model already consumed. `NavModelState.active` reports consumed conditioning
inputs, not successful autonomous turn completion.

A target build, source-versus-device numerical comparison and recorded-route
evaluation with real navigation inputs are still required before road-test
readiness can be claimed. No controller or curb-safety verdict follows from the
Mac runtime smoke or the metadata/selector tests.

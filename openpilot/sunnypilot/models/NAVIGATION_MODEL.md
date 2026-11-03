# Experimental learned navigation model

Install this branch, park the device with the supported Chestnut GPU connected,
then open **Settings → Models → Prepare Navigation Model**. Keep the device
parked and powered throughout preparation. This downloads approximately 815 MB,
checks its official size and SHA-256, and builds the device artifact locally.
Download progress and the build stage appear in the Models screen. Compilation
has no measured time estimate yet. **Cancel** stops the preparation job and its
compiler; entering onroad also stops it. Failure leaves an explanation in Models
and does not activate or register an incomplete model.

After the screen says the model is ready, explicitly choose **RL Navigation
80eedcdd (experimental)** in the existing Chestnut model selector. Preparation
never changes the current model. Selecting this model is a whole-drive choice;
signal-created navigation routes do not swap models on each turn. The ordinary
small model remains the fallback and does not support navigation conditioning.

The build checks for the reviewed compiler, libusb and LLVM 18 or newer with the
AMDGPU backend before downloading. It requires at least 4 GiB of free model
storage. Missing device dependencies produce an error; this feature does not
install system libraries. The compiler log is
`Paths.model_root()/rl_nav_80eedcdd_build.log`. An interrupted verified download
can be reused on the next attempt; incomplete downloads are never accepted.

## Exact checkpoint and build

The source is the official ONNX SHA-256
`1d18c42ea4cd95c8bffab4635844b78b8e2d4e25b9de44a9c5ac2e0961371a2e`,
814,591,106 bytes, referenced by comma commit
`afbf2e547e9319e2eb9f515e1e4330af63705cec`. This is the earlier learned navigation
checkpoint **80eedcdd/12864**, not the separate N16 compiled PKL updated in that
commit. The download uses the public `happymaj11r/openpilot-models` release as an
alternate transport because the official LFS object is unavailable. Only bytes
matching the authoritative upstream pointer are accepted.

The existing reviewed `compile_modeld_v2.py` is invoked with
`DEV=USB+AMD:LLVM`, `FRAME_DEV=CPU`, `FLOAT16=1`, `GMMU=0`, `TC_OPT=2`,
`TC_MIN_GLOBALS=32`, all inputs on-device and one benchmark run. The generated
plain artifact must match its hash, AMD device specification, all five recurrent
state pairs and the navigation/action output protocol before the descriptor is
published. No artifact means no selectable local model. Existing image warp
artifacts are reused; no new warp build is required.

The bundle uses generation 12 as the native action protocol, not a training
checkpoint number. Normal remote catalogs remain unchanged. Removing or changing
the local artifact makes its entry unavailable. Preparing and selecting it use
the existing model manager request, status and cancel mechanism; no new Params
keys are required.

## Validation limits

The exact ONNX has run on Mac CPU with real recorded camera frames and real
mini-route/map inputs. A same-model Nav versus NoNav test changed the predicted
turn response. That is a fixed-view neural response test, not proof of physical
turn completion, receiving lane choice or curb clearance. The full model has not
been compiled or run on the user's device here; device compilation time, memory
requirements beyond the preliminary storage check and source/device numerical
parity remain unmeasured. A successful preparation is an artifact/protocol check,
not a road-test readiness or safety verdict.

Existing action conversion, the 1.6 m/s curvature hold, steering and cooperative
steering are preserved. Navigation conditioning requires matching route ownership
and fresh map/instruction inputs. `NavModelState.active` reports consumed inputs,
not successful autonomous maneuver completion.

The goal of dockerizing agnos is to speed up C3X native binary prebuilds by 30x+ by building on more powerful Linux aarch64 machines.

# dockerize-agnos.sh usage
```
# Run this on any Linux then upload the docker base image to a repo.
# It works on x86_64 because it's only copying files without executing anything.
sudo tools/dockerize-agnos/dockerize-agnos.sh

# Docker build must happen on Linux aarch64
sudo docker buildx build -f Dockerfile.sunnypilot_agnos -t test1 .

```

# TODO Items
* Currently the binary output will fail when you enable MADS because dmonitoringmodeld can't find `dmonitoring_model_tinygrad.pkl` et al. The [default model binaries](https://gitlab.com/sunnypilot/public/docs.sunnypilot.ai3/-/tree/main/models/recompiled2/model-Space%20Lab%202%20v2%20(July%2026,%202025)-78?ref_type=heads) must be built separately and copied into the build.
* The build output must be commit to a git branch for it to work on the device. Replicate how the prebuilt commit looks as if it came from the github workflow.
* Cleaner and still correct: Get rid of the build flag by instead detecting QCOM && missing kgsl device.

# Regarding `/dev/kgsl-3d0` during build-time
Builds within dockerized-agnos fail when tinygrad tries to use `/dev/kgsl-3d0` to compile and test the default model.

```
33.18   File "/data/openpilot/tinygrad/runtime/ops_qcom.py", line 320, in __init__
33.18     self.fd = FileIOInterface('/dev/kgsl-3d0', os.O_RDWR)
33.18               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
33.18   File "/data/openpilot/tinygrad/runtime/support/hcq.py", line 27, in __init__
33.18     self.fd:int = fd or os.open(path, flags)
33.18                         ^^^^^^^^^^^^^^^^^^^^
33.18 FileNotFoundError: [Errno 2] No such file or directory: '/dev/kgsl-3d0'
33.30 scons: *** [selfdrive/modeld/models/driving_policy_tinygrad.pkl] Error 1
```

Note: `selfdrive/modeld/SConscript` skips model compilation when it detects you want QCOM2 native builds but it can't.


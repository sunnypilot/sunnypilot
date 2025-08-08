The goal of dockerizing agnos is to speed up C3X native binary prebuilds by 30x+ by building on more powerful Linux aarch64 machines.

# dockerize-agnos.sh usage
```
# Run this on any Linux then upload the docker base image to a repo.
# It works on x86_64 because it's only copying files without executing anything.
sudo tools/dockerize-agnos/dockerize-agnos.sh

# Disable tinygrad default model compilation for build to succeed.
git am tools/dockerize-agnos/DEMO-disable-QCOM-tinygrad-compile.patch

# Docker build must happen on Linux aarch64
sudo docker buildx build -f Dockerfile.sunnypilot_agnos -t test1 .

```

# TODO Items
* Due to the unavailable `/dev/kgsl-3d0` you need to disable QCOM tinygrad compilation to avoid a build failure. Let's add a build flag?
* Currently the binary output will fail when you enable MADS because dmonitoringmodeld can't find `dmonitoring_model_tinygrad.pkl` et al. The default model binaries must be built separately and copied into the build.
* The build output must be commit to a git branch for it to work on the device.

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

It's good to know the build environment is so exactly like the device that it is trying to build the same way. It doesn't attempt to do this within a vanilla Ubuntu aarch64 image. Where in the source is deciding to use kgsl instead of CPU or LLVM?


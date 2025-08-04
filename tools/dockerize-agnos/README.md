= dockerize-agnos.sh
* Copy the `system-*.img.xz` file into `tools/dockerize-agnos/tmp` before running the script if you want to avoid downloading the image repeatedly. Note the script deletes this file as the last step to fully clean up after itself.
* Should docker base image include the system image hash within the name? e.g. `agnos-system-base-$HASH`
The hash identifies which OS image is installed onto devices. You probably need some way for older branches to find their respective agnos base image? They each know the agnos system hash so they would know the exact agnos base image name. This is also how you know which old agnos images are safe to delete. 

= Regarding `/dev/kgsl-3d0`
Builds within dockerized-agnos fail when tinygrad tries to use `/dev/kgsl-3d0` to compile and test.

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

= DEMO-disable-QCOM-tinygrad-compile.patch
`git am DEMO-disable-QCOM-tinygrad-compile.patch`

Due to the missing `/dev/kgsl-3d0` you need to disable QCOM tinygrad compilation to avoid a build failure. Perhaps we should replace this with a prebuilt and downloaded model copied into the docker imageprior to scons?

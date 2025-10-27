## What is LAICa?
LAICa is a fork of [sunnypilot](https://github.com/sunnyhaibin/sunnypilot), an open source driver assistance system. SunnyPilot offers the user a unique driving experience for over 300+ supported car makes and models with modified behaviors of driving assist engagements

This particular fork is used in my 2021 Volkswagen GLI, attempting to add modifications and hacks to the SunnyPilot codebase for my personal use.

The catch is I'm trying to do this without doing heavy modifications to the codebase, only minor changes through clever tactics that mostly leverage Python's polymorphism to override original behavior.

## Installation
Run this in Comma 3X:

```bash
cd /data; rm  -rf ./openpilot; git clone -b master --recurse-submodules https://github.com/lesmo/laica.git openpilot; cd /data/openpilot; git lfs pull; sudo reboot
```

## 🎆 Pull Requests
I welcome both pull requests and issues on GitHub.

Pull requests should be against the most current `master` branch.

## 📊 User Data

By default, sunnypilot uploads the driving data to comma servers. You can also access your data through [comma connect](https://connect.comma.ai/).

sunnypilot is open source software. The user is free to disable data collection if they wish to do so.

sunnypilot logs the road-facing camera, CAN, GPS, IMU, magnetometer, thermal sensors, crashes, and operating system logs.
The driver-facing camera and microphone are only logged if you explicitly opt-in in settings.

By using this software, you understand that use of this software or its related services will generate certain types of user data, which may be logged and stored at the sole discretion of comma. By accepting this agreement, you grant an irrevocable, perpetual, worldwide right to comma for the use of this data.

## Licensing

sunnypilot is released under the [MIT License](LICENSE). This repository includes original work as well as significant portions of code derived from [openpilot by comma.ai](https://github.com/commaai/openpilot), which is also released under the MIT license with additional disclaimers.

The original openpilot license notice, including comma.ai’s indemnification and alpha software disclaimer, is reproduced below as required:

> openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.
>
> Any user of this software shall indemnify and hold harmless Comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.
>
> **THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
> YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
> NO WARRANTY EXPRESSED OR IMPLIED.**

For full license terms, please see the [`LICENSE`](LICENSE) file.

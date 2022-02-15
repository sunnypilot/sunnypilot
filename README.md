Table of Contents
=======================

* [Join our Discord](#-join-our-discord-)
* [Read Before Installing](#-read-before-installing-)
* [Highlight Features](#-highlight-features)
* [Driving Enhancement](#-driving-enhancement)
* [Branch Definitions](#-branch-definitions)
* [Recommended Branches](#-recommended-branches)
* [Installation](#-installation)
* [How-Tos](#-How-Tos-)
* [Donate](#-donate-)
* [Pull Requests](#-Pull-Requests-)
* [Special Thanks](#-special-thanks)
* [Licensing](#licensing)

---

💭 Join our Discord 💭
---

Join sunnyhaibin's openpilot server!
* https://discord.gg/wRW3meAgtx

🚨 Read Before Installing 🚨
---

It is recommended to read this entire page before proceeding. This will ensure that you are selecting the right branch for your car to have the best driving experience.

This fork is recommended to be used for Hyundai/Kia/Genesis (**HKG**), Honda, Toyota, and Subaru cars. It is a fork of [comma.ai's openpilot](https://github.com/commaai/openpilot). By installing this software, you accept all responsibility for anything that might occur while you use it. All contributors to this fork are not liable. <ins>**Use at your own risk.**</ins>

🚗 Highlight Features
---

### Driving Enhancement
* [**Modified Assistive Driving Safety (MADS)**](#modified-assistive-driving-safety-mads) - openpilot Automatic Lane Centering (ALC) and Adaptive Cruise Control (ACC) / Smart Cruise Control (SCC) can be engaged independently of each other
* [**Dynamic Lane Profile (DLP)**](#dynamic-lane-profile-dlp) - dynamically switch lane profile base on lane recognition confidence
* Quiet Drive 🤫 - Toggle to mute all notification sounds (excluding driver safety warnings)
* Force Car Recognition (FCR) - Use a selector to force your car to be recognized by openpilot
* [**Enhanced Speed Control**](#enhanced-speed-control) - Utilizes data from vision or OpenStreetMap to achieve dynamic speed control without user's intervention. Only available to openpilot longitudinal capable cars

🚗 Driving Enhancement
---

### Modified Assistive Driving Safety (MADS)
The goal of Modified Assistive Driving Safety (MADS) is to enhance the user driving experience with modified behaviors of openpilot engagements. This feature complies with comma.ai's safety rules as accurately as possible with the following changes:
* openpilot ALC and ACC/SCC can be engaged independently of each other
* Dedicated button to toggle openpilot ALC:
  * `LFA` button: Newer HKG cars
  * `CRUISE (MAIN)` button: Most HKG cars, Subaru (Global and Pre Global)
  * `LKAS` button: Honda, Toyota
* `SET-` button enables ACC/SCC
* `CANCEL` button only disables ACC/SCC
* `CRUISE (MAIN)` button disables openpilot completely when `OFF` (strictly enforced in panda safety code)
* `BRAKE pedal` press will pause openpilot ALC; `BRAKE pedal` release will resume openpilot ALC; `BRAKE pedal` release will NOT resume ACC/SCC without an explicit entry
* `GAS pedal` press will not disengage openpilot ALC or ACC/SCC
* `TURN SIGNALS` (`Left` or `Right`) will pause openpilot ALC if the vehicle speed is below the threshold for openpilot Automatic Lane Change
* Event audible alerts are more relaxed to match manufacturer's stock behavior

### Dynamic Lane Profile (DLP)
Dynamic Lane Profile (DLP) aims to provide the best driving experience with staying within the lane confidently. Dynamic Lane Profile allows openpilot to dynamically switch between lane profiles base on lane recognition confidence level on road.

There are 3 modes to select on the onroad camera screen:
* **Auto Lane**: openpilot dynamically chooses between `Laneline` or `Laneless` model
* **Laneline**: openpilot uses Laneline model only.
* **Laneless**: openpilot uses Laneless model only.

To use Dynamic Lane Profile, do the following:
```
1. openpilot Settings -> Toggles -> Disable use of lanelines -> ON toggle
2. Reboot.
3. Before driving, on the onroad camera screen, toggle between the 3 modes by pressing on the button.
4. Drive. 
```

### Enhanced Speed Control
This fork now allows openpilot-longitudinal-capable cars to dynamically adjust the longitudinal plan based on the fetched map data. Big thanks to the Move Fast team for the amazing implementation!

Certain features are only available with an active data connection, via:
* [comma Prime](https://comma.ai/prime) - Intuitive service provided directly by comma, or;
* Personal Hotspot - From your mobile device, or a dedicated hotspot from a cellular carrier.

Features:
* [Vision-based Turn Control]: Use vision path predictions to estimate the appropriate speed to drive through turns ahead - i.e., slowing down for curves
* [Map-Data-based Turn Control]: Use curvature information from map data to define speed limits to take turns ahead - i.e., slowing down for curves
  * **Note: Require data connection**
* [Speed Limit Control]: Use speed limit signs information from map data and car interface to automatically adapt cruise speed to road limits
  * **Note: Require data connection**
    * [Speed Limit Offset]: When Speed Limit Control is enabled, set speed limit slightly higher than the actual speed limit for a more natural drive
      * **Note: Require data connection**
* [Hands on Wheel Monitoring]" Monitor and alert when driver is not keeping the hands on the steering wheel

Instruction (WIP)

⚒ Branch Definitions
---

* `prod`: Production branches. Include features that are tested by users and ready to use. ✅
* `staging`: Staging branches. Include new features that are not tested by users. No stability guaranteed. 🚨
* `feature`: Feature branches. Represent new features being added to the system. No stability guaranteed. 🚨
* `test`: Test branches. For experimenting with concepts that might not get used in the project. No stability guaranteed. 🚨
* `develop`: Development branches. All features are gathered in respective versions. Reviewed features will be committed to `develop`. No stability guaranteed. 🚨
* `full`: Full Feature branches.
* `personal`: sunnyhaibin's personal branches, on top of Full Feature.
* `hkg`: Hyundai/Kia/Genesis(HKG)-specific branches. Only for HKG cars.
* `honda`: Honda-specific branches. Only for Honda cars.
* `toyota`: Toyota-specific branches. Only for Toyota cars.
* `subaru`: Subaru-specific branches. Only for Subaru cars.

Example:
* [`0.8.12-prod-full-honda`](https://github.com/sunnyhaibin/openpilot/tree/0.8.12-prod-full-hkg): 0.8.12-based, Production, Full Feature, Honda branch
* [`0.8.12-prod-personal-hkg`](https://github.com/sunnyhaibin/openpilot/tree/0.8.12-prod-personal-hkg): 0.8.12-based, Production, sunnyhaibin's personal Full Feature, Hyundai/Kia/Genesis branch

📰 Recommended Branches
---
* `prod-full-<car_brand>`: Contains all features supported by this fork, such as Modified Assistive Driving Safety (MADS), Dynamic Lane Profile (DLP), etc.
* `prod-personal-<car_brand>`: sunnyhaibin's everyday use branch, contains changes and good stuff for my personal use and quality-of-life features.
    * **Hyundai: Sonata N Line 2021**

⚒ Installation
---

### Smiskol URL (Quickest and Easiest)
To install sunnyhaibin's fork, simply use the Smiskol URL (thanks [Shane](https://github.com/sshane/openpilot-installer-generator)!) on the setup screen for "Custom Software" after you factory reset or uninstalled openpilot from a previous install:

```
https://smiskol.com/fork/sunnyhaibin/<insert_branch_name>
```
For example, if you would like to install the branch for HKG:

* [`0.8.12-prod-full-hkg`](https://github.com/sunnyhaibin/openpilot/tree/0.8.12-prod-full-hkg):
    ```
    https://smiskol.com/fork/sunnyhaibin/0.8.12-prod-full-hkg
    ```

* [`0.8.12-prod-personal-hkg`](https://github.com/sunnyhaibin/openpilot/tree/0.8.12-prod-personal-hkg):
    ```
    https://smiskol.com/fork/sunnyhaibin/0.8.12-prod-personal-hkg
    ```

### SSH (More Versatile)
If you are looking to install sunnyhaibin's fork via SSH, run the following command in an SSH terminal after connecting to your device:

* [`0.8.12-prod-full-hkg`](https://github.com/sunnyhaibin/openpilot/tree/0.8.12-prod-full-hkg):
    ```
    cd /data; rm -rf ./openpilot; git clone -b 0.8.12-prod-full-hkg --depth 1 --single-branch --recurse-submodules --shallow-submodules https://github.com/sunnyhaibin/openpilot.git openpilot; cd openpilot; pkill -f thermald; rm -f prebuilt; reboot; sudo reboot
    ```

* [`0.8.12-prod-personal-hkg`](https://github.com/sunnyhaibin/openpilot/tree/0.8.12-prod-personal-hkg):
    ```
    cd /data; rm -rf ./openpilot; git clone -b 0.8.12-prod-personal-hkg --depth 1 --single-branch --recurse-submodules --shallow-submodules https://github.com/sunnyhaibin/openpilot.git openpilot; cd openpilot; pkill -f thermald; rm -f prebuilt; reboot; sudo reboot
    ```
After running the command to install the desired branch, reboot the comma device to ensure to take the change in effect:
1. C3: `sudo reboot`
2. C2 or EON: `reboot`

📗 How Tos 📗
---

How-To instructions can be found in [HOW-TOS.md](https://github.com/sunnyhaibin/openpilot/blob/(!)README/HOW-TOS.md).

💰 Donate 💰
---

If you find any of the features useful, feel free to donate to support for future feature development.

Thank you for your continuous love and support! Enjoy 🥰

**PayPal:**

<a href="https://paypal.me/sunnyhaibin0850" target="_blank">
<img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal this" title="PayPal - The safer, easier way to pay online!" border="0" />
</a>
<br></br>

**PayPal QR Code:**

![sunnyhaibin0850_qrcode_paypal.me.png](sunnyhaibin0850_qrcode_paypal.me.png)

🎆 Pull Requests 🎆
---

We welcome both pull requests and issues on GitHub. Bug fixes are encouraged.

Pull requests should be against the most current `prod-full` branch.

🏆 Special Thanks
---

* [spektor56](https://github.com/spektor56/openpilot)
* [mob9221](https://github.com/mob9221/opendbc)
* [briantran33](https://github.com/briantran33/openpilot)
* [Aragon7777](https://github.com/aragon7777/openpilot)
* [sshane](https://github.com/sshane/openpilot-installer-generator)
* [jung](https://github.com/chanhojung/openpilot)
* [dri94](https://github.com/dri94/openpilot)
* [JamesKGithub](https://github.com/JamesKGithub/FrogPilot)
* [twilsonco](https://github.com/twilsonco/openpilot)
* [martinl](https://github.com/martinl/openpilot)
* [multikyd](https://github.com/openpilotkr)
* [Move Fast GmbH](https://github.com/move-fast/openpilot)
* [Dragonpilot](https://github.com/dragonpilot-community/dragonpilot)

Licensing
------

openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.

Any user of this software shall indemnify and hold harmless comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.

**THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
NO WARRANTY EXPRESSED OR IMPLIED.**

---

<img src="https://d1qb2nb5cznatu.cloudfront.net/startups/i/1061157-bc7e9bf3b246ece7322e6ffe653f6af8-medium_jpg.jpg?buster=1458363130" width="75"></img> <img src="https://cdn-images-1.medium.com/max/1600/1*C87EjxGeMPrkTuVRVWVg4w.png" width="225"></img>

[![openpilot tests](https://github.com/commaai/openpilot/workflows/openpilot%20tests/badge.svg?event=push)](https://github.com/commaai/openpilot/actions)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/context:python)
[![Language grade: C/C++](https://img.shields.io/lgtm/grade/cpp/g/commaai/openpilot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/commaai/openpilot/context:cpp)
[![codecov](https://codecov.io/gh/commaai/openpilot/branch/master/graph/badge.svg)](https://codecov.io/gh/commaai/openpilot)
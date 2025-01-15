![](https://user-images.githubusercontent.com/47793918/233812617-beab2e71-57b9-479e-8bff-c3931347ca40.png)

Table of Contents
=======================

* [Join our Discord](#-join-our-discord)
* [What is sunnypilot?](#-what-is-sunnypilot)
* [Running in a car](#-running-on-a-dedicated-device-in-a-car)
* [Read Before Installing](#-read-before-installing)
* [Prohibited Safety Modifications](#-prohibited-safety-modifications)
* [Installation](#-installation)
* [Highlight Features](#-highlight-features)
* [Driving Enhancements](#-driving-enhancements)
* [Branch Definitions](#-branch-definitions)
* [Recommended Branches](#-recommended-branches)
* [Pull Requests](#-Pull-Requests)
* [Licensing](#licensing)
* [Donate](#-support-sunnypilot)

---

<details><summary><h3>💭 Join our Discord</h3></summary>

---

Join the official sunnypilot Discord server to stay up to date with all the latest features and be a part of shaping the future of sunnypilot!
* https://discord.gg/sunnypilot

  ![](https://dcbadge.vercel.app/api/server/wRW3meAgtx?style=flat) ![Discord Shield](https://discordapp.com/api/guilds/880416502577266699/widget.png?style=shield)

</details>

<details><summary><h3>🌞 What is sunnypilot?</h3></summary>

---

[sunnypilot](https://github.com/sunnyhaibin/sunnypilot) is a fork of comma.ai's openpilot, an open source driver assistance system. sunnypilot offers the user a unique driving experience for over 250+ supported car makes and models with modified behaviors of driving assist engagements. sunnypilot complies with comma.ai's safety rules as accurately as possible.

</details>

<details><summary><h3>🚘 Running on a dedicated device in a car</h3></summary>

---

To use sunnypilot in a car, you need the following:
* A supported device to run this software
    * a [comma three](https://comma.ai/shop/products/three), or
    * a comma two (only with older versions below 0.8.13)
* This software
* One of [the 290+ supported cars](https://github.com/commaai/openpilot/blob/master/docs/CARS.md). We support Honda, Toyota, Hyundai, Nissan, Kia, Chrysler, Lexus, Acura, Audi, VW, Ford and more. If your car is not supported but has adaptive cruise control and lane-keeping assist, it's likely able to run sunnypilot.
* A [car harness](https://comma.ai/shop/products/car-harness) to connect to your car

Detailed instructions for [how to mount the device in a car](https://comma.ai/setup).

</details>

<details><summary><h3>🚨 Read Before Installing</h3></summary>

---

It is recommended to read this **entire page** before proceeding. This will ensure that you fully understand each added feature on sunnypilot, and you are selecting the right branch for your car to have the best driving experience.

This is a fork of [comma.ai's openpilot](https://github.com/commaai/openpilot). By installing this software, you accept all responsibility for anything that might occur while you use it. All contributors to sunnypilot are not liable. ❗<ins>**Use at your own risk.**</ins>❗

</details>

<details><summary><h3>⛔ Prohibited Safety Modifications</h3></summary>

---

All [official sunnypilot branches](https://github.com/sunnyhaibin/sunnypilot/branches) strictly adhere to [comma.ai's safety policy](https://github.com/commaai/openpilot/blob/master/docs/SAFETY.md). Any changes that go against this policy will result in your fork and your device being banned from both comma.ai and sunnypilot channels.

The following changes are a **VIOLATION** of this policy and **ARE NOT** included in any sunnypilot branches:
* Driver Monitoring:
    * ❌ "Nerfing" or reducing monitoring parameters.
* Panda safety:
    * ❌ No preventing disengaging of <ins>**LONGITUDINAL CONTROL**</ins> (acceleration/brake) on brake pedal press.
    * ❌ No auto re-engaging of <ins>**LONGITUDINAL CONTROL**</ins> (acceleration/brake) on brake pedal release.
    * ❌ No disengaging on ACC MAIN in OFF state.

</details>


<details><summary><h3>⚒ Installation</h3></summary>

---

  <details><summary>URL (Easy)</summary>

comma three
------

Please refer to [Recommended Branches](#-recommended-branches) to find your preferred/supported branch. This guide will assume you want to install the latest `release-c3` branch.

* sunnypilot not installed or you installed a version before 0.8.17?
  1. [Factory reset/uninstall](https://github.com/commaai/openpilot/wiki/FAQ#how-can-i-reset-the-device) the previous software if you have another software/fork installed.
  2. After factory reset/uninstall and upon reboot, select `Custom Software` when given the option.
  3. Input the installation URL per [Recommended Branches](#-recommended-branches). Example: ```release-c3.sunnypilot.ai``` [^4] (note: `https://` is not requirement on the comma three)
  4. Complete the rest of the installation following the onscreen instructions.

* sunnypilot already installed and you installed a version after 0.8.17?
  1. On the comma three, go to `Settings` ▶️ `Software`.
  2. At the `Download` option, press `CHECK`. This will fetch the list of latest branches from sunnypilot.
  3. At the `Target Branch` option, press `SELECT` to open the Target Branch selector.
  4. Scroll to select the desired branch per [Recommended Branches](#-recommended-branches). Example: `release-c3`

|    Branch    |         Installation URL         |
|:------------:|:--------------------------------:|
| `release-c3` | https://release-c3.sunnypilot.ai |
| `staging-c3` | https://staging-c3.sunnypilot.ai |
|   `dev-c3`   | https://dev-c3.sunnypilot.ai     |

Requires further assistance with software installation? Join the [sunnypilot Discord server](https://discord.sunnypilot.com) and message us in the `#installation-help` channel.

comma two
------

1. [Factory reset/uninstall](https://github.com/commaai/openpilot/wiki/FAQ#how-can-i-reset-the-device) the previous software if you have another software/fork installed.
2. After factory reset/uninstall and upon reboot, select `Custom Software` when given the option.
3. Input the installation URL per [Recommended Branches](#-recommended-branches). Example: ```https://smiskol.com/fork/sunnyhaibin/0.8.12-4-prod```
4. Complete the rest of the installation following the onscreen instructions.

Requires further assistance with software installation? Join the [sunnypilot Discord server](https://discord.sunnypilot.com) and message us in the `#installation-help` channel.

  </details>

  <details>
  <summary>SSH (More Versatile)</summary>
  <br>

Prerequisites: [How to SSH](https://github.com/commaai/openpilot/wiki/SSH)

If you are looking to install sunnypilot via SSH, run the following command in an SSH terminal after connecting to your device:

comma three:
------
* [`release-c3`](https://github.com/sunnyhaibin/openpilot/tree/release-c3):

  ```
  cd /data; rm -rf ./openpilot; git clone -b release-c3 --recurse-submodules https://github.com/sunnyhaibin/sunnypilot.git openpilot; cd openpilot; sudo reboot
  ```

comma two:
------
* [`0.8.12-prod-personal-hkg`](https://github.com/sunnyhaibin/openpilot/tree/0.8.12-prod-personal-hkg):

  ```
  cd /data; rm -rf ./openpilot; git clone -b 0.8.12-prod-personal-hkg --recurse-submodules https://github.com/sunnyhaibin/sunnypilot.git openpilot; cd openpilot; sudo reboot
  ```

After running the command to install the desired branch, your comma device should reboot.
  </details>

</details>


<details><summary><h3>🚗 Highlight Features</h3></summary>

---

### Quality of Life Enhancements
- [**Modified Assistive Driving Safety (MADS)**](#modified-assistive-driving-safety-mads) - Automatic Lane Centering (ALC) / Lane Keep Assist System (LKAS) and Adaptive Cruise Control (ACC) / Smart Cruise Control (SCC) can be engaged independently of each other

### Visual Enhancements
* **M.A.D.S Boarder color** - Dedicated icon to display M.A.D.S. engagement status* 
    * Green🟢: openpilot is engaged as normal
    * Black⚫: M.A.D.S. engaged, steering or longitudinal is being manually overridden by user
    * Blue🔵: M.A.D.S. engaged but longitudinal is not
    * White⚪: M.A.D.S. suspended or disengaged
  -
</details>

<details><summary><h3>🚗 Driving Enhancements</h3></summary>

---

### Modified Assistive Driving Safety (MADS)
The goal of Modified Assistive Driving Safety (MADS) is to enhance the user driving experience with modified behaviors of driving assist engagements. This feature complies with comma.ai's safety rules as accurately as possible with the following changes:
* sunnypilot Automatic Lane Centering (ALC) and ACC/SCC can be engaged independently of each other
* Dedicated button to toggle sunnypilot ALC:
    * `CRUISE (MAIN)` button: All supported cars on sunnypilot
        * `LFA` button: Newer HKG cars with `LFA` button
        * `LKAS` button: Honda, Toyota, Global Subaru
* `SET-` button enables ACC/SCC
* `CANCEL` button only disables ACC/SCC
* `CRUISE (MAIN)` must be `ON` to use ACC/SCC
* `CRUISE (MAIN)` button disables ACC/SCC completely when `OFF` **(strictly enforced in panda safety code)**

### Disengage Lateral ALC on Brake Press Mode toggle
Dedicated toggle to handle Lateral state on brake pedal press and release:
1. `ON`: `BRAKE pedal` press will pause Automatic Lane Centering; `BRAKE pedal` release will resume Automatic Lane Centering. Note: `BRAKE pedal` release will NOT resume ACC/SCC/Long control without explicit user engagement **(strictly enforced in panda safety code)**
2. `OFF`: `BRAKE pedal` press will NOT pause Automatic Lane Centering; `BRAKE pedal` release will NOT resume ACC/SCC/Long control without explicit user engagement **(strictly enforced in panda safety code)**


Certain features are only available with an active data connection, via:
* [comma Prime](https://comma.ai/prime) - Intuitive service provided directly by comma, or
* Personal Hotspot - From your mobile device, or a dedicated hotspot from a cellular carrier.


### Custom Stock Longitudinal Control
While using stock Adaptive/Smart Cruise Control, Custom Stock Longitudinal Control in sunnypilot allows sunnypilot to manipulate and take over the set speed on the car's dashboard.

**Supported Cars:**
* Hyundai/Kia/Genesis
    * CAN platform
    * CAN-FD platform with 0x1CF broadcasted in CAN traffic
* Honda Bosch
* Volkswagen MQB

**Instruction**

**📗 How to use Custom Longitudinal Control on sunnypilot **

When using Speed Limit, Vision, or Map based Turn control, you will be setting the "MAX" ACC speed on the sunnypilot display instead of the one in the dashboard. The car will then set the ACC setting in the dashboard to the targeted speed, but will never exceed the max speed set on the sunnypilot display. A quick press of the RES+ or SET- buttons will change this speed by 5 MPH or KM/H on the sunnypilot display, while a long deliberate press (about a 1/2 second press) changes it by 1 MPH or KM/H. DO NOT hold the RES+ or SET- buttons for longer that a 1 second. Either make quick or long deliberate presses only.

**‼ Where to look when setting ACC speed ‼**

Do not look at the dashboard when setting your ACC max speed. Instead, only look at the one on the sunnypilot display, "MAX". The reason you need to look at the sunnypilot display is because sunnypilot will be changing the one in the dashboard. It will be adjusting it as needed, never raising it above the one set on the sunnypilot display. ONLY look at the MAX speed on the sunnypilot display when setting the ACC speed instead of the dashboard!

(Courtesy instructions from John, author of jvePilot)

### Gap Adjust Cruise
This fork now allows supported openpilot longitudinal cars to adjust the cruise gap between the car and the lead car.

**Supported cars:**
* sunnypilot Longitudinal Control capable

🚨**PROCEED WITH EXTREME CAUTION AND BE READY TO MANUALLY TAKE OVER AT ALL TIMES**

There are 4 modes to select on the steering wheel and/or the onroad camera screen:
* **Stock Gap**: Stock sunnypilot distance - 1.45 second profile
* **Mild Gap**: Semi-aggressive distance - 1.25 second profile
* 🚨**Aggro Gap**🚨: Aggressive distance - 1.0 second profile

**Availability**

|      Car Make       | Stock Gap | Mild Gap | Aggro Gap |
|:-------------------:|:---------:|:--------:|:---------:|
|     Honda/Acura     |     ✅     |    ✅     |     ✅     |
| Hyundai/Kia/Genesis |     ✅     |    ✅     |     ✅     |
|    Toyota/Lexus     |     ✅     |    ✅     |     ✅     |
|  Volkswagen MQB/PQ  |     ✅     |    ✅     |     ✅     |

</details>


<details><summary><h3>⚒ Branch Definitions</h3></summary>

---

|    Tag    | Definition           | Description                                                                                                                                                                                 |
|:---------:|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `release` | Release branches     | Include features that are **verified** by trusted testers and the community. Ready to use. ✅                                                                                                |
| `staging` | Staging branches     | Include new features that are **tested** by trusted testers and the community. Stability may vary. ⚠                                                                                        |
|   `dev`   | Development branches | All features are gathered in respective versions. Reviewed and merged features will be committed to `dev`. Stability may vary. ⚠                                                            |
| `master`  | Main branch          | Syncs with [commaai's openpilot `master`](https://github.com/commaai/openpilot) upstream branch. Accepts all pull requests. Does not include all sunnypilot features. Stability may vary. ⚠ |

Example:
* [`release-c3`](https://github.com/sunnyhaibin/sunnypilot/tree/release-c3): Latest release branch for comma three that are verified by trusted testers and the community. Ready to use.
* [`staging-c3`](https://github.com/sunnyhaibin/sunnypilot/tree/staging-c3): Latest staging branch for comma three that are tested by trusted testers and the community. Verification required.
* [`dev-c3`](https://github.com/sunnyhaibin/sunnypilot/tree/dev-c3): Latest development branch for comma three that include all sunnypilot features. Testing required.

</details>

<details><summary><h3>✅ Recommended Branches</h3></summary>

---

| Branch                                                                              | Definition                                              | Compatible Device | Changelogs                                                                                 |
|:------------------------------------------------------------------------------------|---------------------------------------------------------|-------------------|--------------------------------------------------------------------------------------------|
| [`release-c3`](https://github.com/sunnyhaibin/sunnypilot/tree/release-c3)           | • Latest release/stable branch                          | comma three       | [`CHANGELOGS.md`](https://github.com/sunnyhaibin/sunnypilot/blob/release-c3/CHANGELOGS.md) |
| [`staging-c3`](https://github.com/sunnyhaibin/sunnypilot/tree/staging-c3)           | • Latest staging branch                                 | comma three       | [`CHANGELOGS.md`](https://github.com/sunnyhaibin/sunnypilot/blob/staging-c3/CHANGELOGS.md) |
| [`dev-c3`](https://github.com/sunnyhaibin/sunnypilot/tree/dev-c3)                   | • Latest development branch with experimental features  | comma three       | [`CHANGELOGS.md`](https://github.com/sunnyhaibin/sunnypilot/blob/dev-c3/CHANGELOGS.md)     |

</details>


<details><summary><h3>🎆 Pull Requests</h3></summary>

---

We welcome both pull requests and issues on GitHub. Bug fixes are encouraged.

Pull requests should be against the most current `master-new` branch.

</details>

<details><summary><h3>📊 User Data</h3></summary>

---

By default, sunnypilot uploads the driving data to comma servers. You can also access your data through [comma connect](https://connect.comma.ai/).

sunnypilot is open source software. The user is free to disable data collection if they wish to do so.

sunnypilot logs the road-facing camera, CAN, GPS, IMU, magnetometer, thermal sensors, crashes, and operating system logs.
The driver-facing camera is only logged if you explicitly opt-in in settings. The microphone is not recorded.

By using this software, you understand that use of this software or its related services will generate certain types of user data, which may be logged and stored at the sole discretion of comma. By accepting this agreement, you grant an irrevocable, perpetual, worldwide right to comma for the use of this data.

</details>

<details><summary><h3>Licensing</h3></summary>

openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.

Any user of this software shall indemnify and hold harmless comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.

**THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
NO WARRANTY EXPRESSED OR IMPLIED.**

</details>

<h3>💰 Support sunnypilot</h3>

---

If you find any of the features useful, consider becoming a [patron on Patreon](https://www.patreon.com/sunnyhaibin) or a [sponsor on GitHub](https://github.com/sponsors/sunnyhaibin) to support future feature development and improvements.


By becoming a patron/sponsor, you will gain access to exclusive content, early access to new features, and the opportunity to directly influence the project's development.

<h3>Patreon</h3>

<a href="https://www.patreon.com/sunnyhaibin">
  <img src="https://user-images.githubusercontent.com/47793918/244128051-bc7e913e-a196-4455-926e-23aec9a4bd3b.png" alt="Become a Patron" width="300" style="max-width: 100%; height: auto;">
</a>
<br>

<h3>GitHub Sponsor</h3>

<a href="https://github.com/sponsors/sunnyhaibin">
  <img src="https://user-images.githubusercontent.com/47793918/244135584-9800acbd-69fd-4b2b-bec9-e5fa2d85c817.png" alt="Become a Sponsor" width="300" style="max-width: 100%; height: auto;">
</a>
<br>

<h3>PayPal</h3>

<a href="https://paypal.me/sunnyhaibin0850" target="_blank">
<img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal this" title="PayPal - The safer, easier way to pay online!" border="0" />
</a>
<br></br>

Your continuous love and support are greatly appreciated! Enjoy 🥰

<span>-</span> Jason, Founder of sunnypilot

[^1]:Requires data connection if not using Offline Maps data
[^2]:At least 50 GB of storage space is required. If you have the 32 GB version of comma three, upgrading with a compatible 250 GB or 1 TB SSD is strongly recommended
[^4]:Shortened URL for convenience. Full URL is ```smiskol.com/fork/sunnyhaibin/release-c3```


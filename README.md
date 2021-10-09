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

---

💭 Join our Discord 💭
---

Join sunnyhaibin's openpilot server!
* https://discord.gg/wRW3meAgtx

🚨 Read Before Installing 🚨
---

It is recommended to read this entire page before proceeding. This will ensure that you are selecting the right branch for your car to have the best driving experience.

This fork is recommended to be used for Hyundai, Kia, and Genesis (HKG) cars. It is a fork of [comma.ai's openpilot](https://github.com/commaai/openpilot). By installing this software, you accept all responsibility for anything that might occur while you use it. All contributors to this fork are not liable. <ins>**Use at your own risk.**</ins>

🚗 Highlight Features
---

### Driving Enhancement
* [**NEW❗ Modified Assistive Driving Safety (MADS)**](#new-modified-assistive-driving-safety-mads) - openpilot (Automatic) Lane Centering (ALC) and Hyundai SCC can be engaged independently of each other
* [**NEW❗ Dynamic Lane Profile (DLP)**](#new-dynamic-lane-profile-dlp) - dynamically switch lane profile base on lane recognition confidence
* Quiet Drive - Toggle to mute all notification sounds (excluding driver safety warnings)
* Force Car Recognition (FCR) - Use a selector to force your car to be recognized by openpilot

🚗 Driving Enhancement
---

### NEW❗ Modified Assistive Driving Safety (MADS)
The goal of Modified Assistive Driving Safety (MADS) is to enhance the user driving experience with modified behaviors of openpilot engagements. This feature complies with comma.ai's safety rules as accurately as possible with the following changes:
* openpilot ALC and Hyundai SCC/ACC can be engaged independently of each other
* `LFA` button (only on newer HKG vehicles) or `CRUISE (MAIN)` button toggles openpilot ALC
* `SET-` button enables Hyundai SCC/ACC
* `CANCEL` button only disables Hyundai SCC/ACC
* `CRUISE (MAIN)` button disables openpilot completely when `OFF` (strictly enforced in panda safety code)
* `BRAKE pedal` press will pause openpilot ALC; `BRAKE pedal` release will resume openpilot ALC
* `GAS pedal` press will not disengage openpilot ALC or Hyundai SCC/ACC
* `TURN SIGNALS` (`Left` or `Right`) will pause openpilot ALC if the vehicle speed is below the threshold for openpilot Automatic Lane Change
* Event audible alerts are more relaxed to match Hyundai stock behavior

### NEW❗ Dynamic Lane Profile (DLP)
Dynamic Lane Profile (DLP) aims to provide the best driving experience with staying within the lane confidently. Dynamic Lane Profile allows openpilot to dynamically switch between lane profiles base on lane recognition confidence level on road.

There are 3 modes to select on the onroad camera screen:
* **Auto Lane**: openpilot dynamically chooses Laneline or Laneless model
* **Laneline**: openpilot uses Laneline model only.
* **Laneless**: openpilot uses Laneless model only.

To use Dynamic Lane Profile, do the following:
```
1. openpilot Settings -> Toggles -> Disable use of lanelines -> ON toggle
2. Reboot.
3. Before driving, on the onroad camera screen, toggle between the 3 modes by pressing on the button.
4. Drive. 
```

⚒ Branch Definitions
---

* `prod`: Production branches. Include features that are tested by users and ready to use. ✅
* `staging`: Staging branches. Include new features that are not tested by users. No stability guaranteed. 🚨
* `feature`: Feature branches. Represent new features being added to the system. No stability guaranteed. 🚨
* `test`: Test branches. For experimenting with concepts that might not get used in the project. No stability guaranteed. 🚨
* `develop`: Development branches. All features are gathered in respective versions. Reviewed features will be committed to `develop`. No stability guaranteed. 🚨

📰 Recommended Branches
---
* `prod-mads`: Contains Modified Assistive Driving Safety (MADS).
    * HKG cars with `LFA` button on the steering wheel will use `LFA` button to engage MADS:
        * Hyundai: [Sonata] 2020-2021
        * Hyundai: [Elantra] 2021
    * HKG cars with **NO** `LFA` button but only `CRUISE (ACC MAIN)` button on the steering wheel will use `CRUISE (ACC MAIN)` button to engage MADS:
        * All officially supported HKG cars **without** `LFA` button on steering wheel
* `prod-full`: Contains all features supported by this fork, such as Modified Assistive Driving Safety (MADS), Dynamic Lane Profile (DLP), etc.
* `prod-personal`: sunnyhaibin's everyday use branch, contains changes and good stuff for my personal use (i.e. custom alerts, custom boot screens, quick boot time, etc.) and quality-of-life features.
    * Hyundai: [Sonata N Line] 2021

⚒ Installation
---

### Smiskol URL (Quickest and Easiest)
To install sunnyhaibin's fork, simply use the Smiskol URL (thanks [Shane](https://github.com/sshane/openpilot-installer-generator)!) on the setup screen for "Custom Software" after you factory reset or uninstalled openpilot from a previous install:

```
https://smiskol.com/fork/sunnyhaibin/<insert_branch_name>
```
For example, if you would like to install the branch:

* [`0.8.9-prod-full`](https://github.com/sunnyhaibin/openpilot/tree/0.8.9-prod-full):
    ```
    https://smiskol.com/fork/sunnyhaibin/0.8.9-prod-full
    ```

* [`0.8.9-prod-personal`](https://github.com/sunnyhaibin/openpilot/tree/0.8.9-prod-personal):
    ```
    https://smiskol.com/fork/sunnyhaibin/0.8.9-prod-personal
    ```

### SSH (More Versatile)
If you are looking to install sunnyhaibin's fork via SSH, run the following command in an SSH terminal after connecting to your device:

* [`0.8.9-prod-full`](https://github.com/sunnyhaibin/openpilot/tree/0.8.9-prod-full):
    ```
    cd /data; cp -rf ./openpilot ./openpilot.bak; rm -rf ./openpilot; git clone https://github.com/sunnyhaibin/openpilot.git openpilot; cd openpilot; git checkout 0.8.9-prod-full; pkill -f thermald; rm -f prebuilt
    ```

* [`0.8.9-prod-personal`](https://github.com/sunnyhaibin/openpilot/tree/0.8.9-prod-personal):
    ```
    cd /data; cp -rf ./openpilot ./openpilot.bak; rm -rf ./openpilot; git clone https://github.com/sunnyhaibin/openpilot.git openpilot; cd openpilot; git checkout 0.8.9-prod-personal; pkill -f thermald; rm -f prebuilt
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

<a href="https://www.paypal.com/donate?business=haibin.wen3%40gmail.com&no_recurring=10&currency_code=USD" target="_blank">
<img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal this" title="PayPal - The safer, easier way to pay online!" border="0" />
</a>
<br></br>

**PayPal QR Code:**

![haibin.wen3@gmail.com_paypal_qr.png.png](haibin.wen3@gmail.com_paypal_qr.png)

🎆 Pull Requests 🎆
---

We welcome both pull requests and issues on GitHub. Bug fixes are encouraged.

Pull requests should be against the most current `develop-full` branch.

🏆 Special Thanks
---

* [spektor56](https://github.com/spektor56/openpilot)
* [mob9221](https://github.com/mob9221/opendbc)
* [briantran33](https://github.com/briantran33/openpilot)
* [Aragon7777](https://github.com/aragon7777/openpilot)
* [sshane](https://github.com/sshane/openpilot-installer-generator)
* [dri94](https://github.com/dri94/openpilot)
* [JamesKGithub](https://github.com/JamesKGithub/FrogPilot)

Table of Contents
=======================

* [Donate](#-donate-)
* [Read Before Installing](#-read-before-installing-)
* [Highlight Features](#-highlight-features)
* [Driving Enhancement](#-driving-enhancement)
* [Branch Definitions](#-branch-definitions)
* [Recommended Branches](#-recommended-branches)
* [Special Thanks](#-special-thanks)

---

💰 Donate 💰
---

If you find any of the features useful, feel free to donate to support for future development.

Thank you for your continuous love and support!

**PayPal:**

<a href="https://www.paypal.com/donate?business=haibin.wen3%40gmail.com&no_recurring=10&currency_code=USD" target="_blank">
<img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal this" title="PayPal - The safer, easier way to pay online!" border="0" />
</a>
<br></br>

**PayPal QR Code:**

![haibin.wen3@gmail.com_paypal_qr.png.png](haibin.wen3@gmail.com_paypal_qr.png)

🚨 Read Before Installing 🚨
---

It is recommended to read this entire page before proceeding. This will ensure that you are selecting the right branch for your car to have the best driving experience.

This fork is recommended to be used for Hyundai, Kia, and Genesis (HKG) cars. It is a fork of [comma.ai's openpilot](https://github.com/commaai/openpilot). By installing this software, you accept all responsibility for anything that might occur while you use it. All contributors to this fork are not liable. <ins>**Use at your own risk.**</ins>

🚗 Highlight Features
---

### Driving Enhancement
* [**NEW❗ Modified Assistive Driving Safety (MADS)**](#new-modified-assistive-driving-safety-mads) - openpilot ALC and Hyundai SCC can be engaged independently of each other
* [**(WIP) NEW❗ Dynamic Lane Profile (DLP)**](#wip-new-dynamic-lane-profile-dlp) - dynamically switch lane profile base on lane recognition confidence

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

### (WIP) NEW❗ Dynamic Lane Profile (DLP)
Dynamic Lane Profile (DLP) aims to provide the best driving experience with staying within the lane confidently. Dynamic Lane Profile allows openpilot to dynamically switch between lane profiles base on lane recognition confidence level on road.

⚒ Branch Definitions
---

* `prod`: Production branches. Include features that are tested by users and ready to use. ✅
* `staging`: Staging branches. Include new features that are not tested by users. No stability guaranteed. 🚨
* `feature`: Feature branches. Represent new features being added to the system. No stability guaranteed. 🚨
* `test`: Test branches. For experimenting with concepts that might not get used in the project. No stability guaranteed. 🚨
* `develop`: Development branches. All features are gathered in respective versions. Reviewed features will be committed to `develop`. No stability guaranteed. 🚨

📰 Recommended Branches
---
* `<version>-prod-mads-lfa`: Contains Modified Assistive Driving Safety (MADS). For HKG vehicles with `LFA` button on the steering wheel.
    * Hyundai: [Sonata] 2020-2021
    * Hyundai: [Elantra] 2021
* `<version>-prod-mads-non-lfa`: Contains Modified Assistive Driving Safety (MADS). For HKG vehicles with no `LFA` button and only `CRUISE (MAIN)` button on the steering wheel.
    * Tested vehicles (will update as more testers confirm functionallity)
      * Hyundai: [Genesis] 2015-2016
* `<version>-prod-personal-mads-sonata`: sunnyhaibin's everyday use branch, contains changes and good stuff for my personal use (i.e. custom alerts, DLP, etc.) and quality-of-life features.
    * Hyundai: [Sonata N Line] 2021

🏆 Special Thanks
---

* [Spektor56](https://github.com/spektor56/openpilot)
* [mob9221](https://github.com/mob9221/opendbc)
* [briantran33](https://github.com/briantran33/openpilot)
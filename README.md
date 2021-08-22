Table of Contents
=======================

* [Read Before Installing](#read-before-installing)
* [Highlight Features](#highlight-features)
* [Driving Enhancement](#driving-enhancement-1)
* [Branch Definitions](#branch-definitions)
* [Special Thanks](#special-thanks)

---

Read Before Installing
---

It is recommended to read this entire page before proceeding. This will ensure that you are selecting the right branch for your car to have the best driving experience.

This fork is recommended to be used for Hyundai, Kia, and Genesis (HKG) cars. It is a fork of [comma.ai's openpilot](https://github.com/commaai/openpilot). By installing this software, you accept all responsibility for anything that might occur while you use it. All contributors to this fork are not liable. <ins>**Use at your own risk.**</ins>

Highlight Features
---

### Driving Enhancement
* [**NEW❗ Modified Assistive Driving Safety (MADS)**](#new-modified-assistive-driving-safety-mads) - openpilot ALC and Hyundai SCC can be engaged independently of each other

Driving Enhancement
---

### NEW❗ Modified Assistive Driving Safety (MADS)
The goal of this feature is to enhance the user driving experience with modified behaviors of openpilot engagements. This feature complies with comma.ai's safety rules as accurately as possible with the following changes:
* openpilot ALC and Hyundai SCC/ACC can be engaged independently of each other
* `LFA` button (only on newer HKG vehicles) or `CRUISE (MAIN)` button toggles openpilot ALC
* `SET-` button enables Hyundai SCC/ACC
* `CANCEL` button only disables Hyundai SCC/ACC
* `CRUISE (MAIN)` button disables openpilot completely when `OFF` (strictly enforced in panda safety code)
* `BRAKE pedal` press will pause openpilot ALC; `BRAKE pedal` release will resume openpilot ALC
* `GAS pedal` press will not disengage openpilot ALC or Hyundai SCC/ACC
* `TURN SIGNALS` (`Left` or `Right`) will pause openpilot ALC if the vehicle speed is below the threshold for openpilot Automatic Lane Change
* Event audible alerts are more relaxed to match Hyundai stock behavior

Branch Definitions
---

* `prod`: Production branches. Include features that are tested by users and ready to use.
* `staging`: Staging branches. Include new features that are not tested by users. No stability guaranteed.
* `feature`: Feature branches. Represent new features being added to the system. No stability guaranteed.
* `test`: Test branches. For experimenting with concepts that might not get used in the project. No stability guaranteed.
* `develop`: Development branches. All features are gathered in respective versions. Features will be committed to `develop` after review. No stability guaranteed.

Special Thanks
---

* [Spektor56](https://github.com/spektor56/openpilot)
* [mob9221](https://github.com/mob9221/opendbc)
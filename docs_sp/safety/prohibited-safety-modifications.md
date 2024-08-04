# Prohibited Safety Modifications

All [official sunnypilot branches](https://github.com/sunnyhaibin/sunnypilot/branches) strictly adhere to [comma.ai's safety policy](https://github.com/commaai/openpilot/blob/master/docs/SAFETY.md). Any changes that go against this policy will result in your fork and your device being banned from both comma.ai and sunnypilot channels.

The following changes are a **VIOLATION** of this policy and **ARE NOT** included in any sunnypilot branches:

!!! danger "Driver Monitoring"
    - "Nerfing" or reducing monitoring parameters.

!!! danger "Panda Safety"
    - No preventing disengaging of <ins>**LONGITUDINAL CONTROL**</ins> (acceleration/brake) on brake pedal press.
    - No auto re-engaging of <ins>**LONGITUDINAL CONTROL**</ins> (acceleration/brake) on brake pedal release.
    - No disengaging on ACC MAIN in OFF state.

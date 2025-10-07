# Prohibited Safety Modifications

All [official sunnypilot branches](https://github.com/sunnyhaibin/sunnypilot/branches) strictly adhere to [comma.ai's safety policy](https://github.com/commaai/openpilot/blob/master/docs/SAFETY.md). Any changes that go against 
this policy will result in your fork and your device being banned from both comma.ai and sunnypilot channels.

The following changes are **VIOLATIONS** of the safety policy and **ARE NOT** supported in any official sunnypilot branches:

!!! danger "Driver Monitoring"
    - "Nerfing" or reducing monitoring parameters.

!!! danger "Panda Safety"
    - No preventing disengaging of <ins>**longitudinal control**</ins> (positive/negative acceleration) on brake pedal press.
    - No auto re-engaging of <ins>**longitudinal control**</ins> (positive/negative acceleration) on brake pedal release.
    - No disengaging on `CRUISE MAIN` in `OFF` state.

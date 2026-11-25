"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
# Parameters that should never be remotely modified
BLOCKED_PARAMS = {
  "AdbEnabled",
  "BluetoothAllowed",
  "BluetoothEnabled",
  "CompletedSunnylinkConsentVersion",
  "CompletedTrainingVersion",
  "GithubUsername",  # Could grant SSH access
  "GithubSshKeys",   # Direct SSH key injection
  "HasAcceptedTerms",
  "HasAcceptedTermsSP",
  "OnroadCycleRequested",      # Prevent remote cycle trigger
  "ParamsVersion",         # Device-managed version counter
}


def is_local_param(key: str) -> bool:
  return key.startswith("SunnylinkLocal")


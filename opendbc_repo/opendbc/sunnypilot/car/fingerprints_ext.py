"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


def merge_fingerprints(fingerprints, new_fingerprints):
  """
    Merge fingerprints by extending lists for matching keys,
    adding all entries regardless of duplicates.
  """
  for car, fp_list in new_fingerprints.items():
    if car not in fingerprints:
      fingerprints[car] = fp_list
    else:
      fingerprints[car].extend(fp_list)

  return fingerprints

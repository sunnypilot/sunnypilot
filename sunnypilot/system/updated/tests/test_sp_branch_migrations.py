"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from openpilot.common.params import Params
from openpilot.system.updated.updated import Updater


@pytest.mark.parametrize(("device_type", "branch", "expected"), [
  ("tici", "staging-c3-new", "staging-tici"),
  ("tici", "dev-c3-new", "staging-tici"),
  ("tici", "master", "master-tici"),
  ("tici", "master-dev-c3-new", "master-tici"),
  ("tizi", "staging-c3-new", "staging"),
  ("tizi", "dev-c3-new", "dev"),
  ("tizi", "master-dev-c3-new", "master-dev"),
  ("tizi", "release3", "release-tizi"),
  ("tizi", "release3-staging", "release-tizi-staging"),
  ("mici", "release3", "release-mici"),
  ("mici", "release3-staging", "release-mici-staging"),
])
def test_sp_branch_migrations_from_current_branch(mocker, device_type, branch, expected):
  params = Params()
  params.remove("UpdaterTargetBranch")

  mocker.patch("openpilot.system.updated.updated.HARDWARE.get_device_type", return_value=device_type)
  mocker.patch.object(Updater, "get_branch", return_value=branch)

  assert Updater().target_branch == expected


@pytest.mark.parametrize(("device_type", "branch", "expected"), [
  ("tici", "staging-c3-new", "staging-tici"),
  ("tici", "dev-c3-new", "staging-tici"),
  ("tici", "master", "master-tici"),
  ("tici", "master-dev-c3-new", "master-tici"),
  ("tizi", "staging-c3-new", "staging"),
  ("tizi", "dev-c3-new", "dev"),
  ("tizi", "master-dev-c3-new", "master-dev"),
  ("tizi", "release3", "release-tizi"),
  ("tizi", "release3-staging", "release-tizi-staging"),
  ("mici", "release3", "release-mici"),
  ("mici", "release3-staging", "release-mici-staging"),
])
def test_sp_branch_migrations_from_param(mocker, device_type, branch, expected):
  params = Params()
  params.put("UpdaterTargetBranch", branch)

  mocker.patch("openpilot.system.updated.updated.HARDWARE.get_device_type", return_value=device_type)

  try:
    assert Updater().target_branch == expected
  finally:
    params.remove("UpdaterTargetBranch")


@pytest.mark.parametrize(("device_type", "branch"), [
  ("tici", "unknown"),
  ("tizi", "unknown"),
  ("mici", "unknown"),
])
def test_sp_branch_migrations_passthrough(mocker, device_type, branch):
  params = Params()
  params.remove("UpdaterTargetBranch")

  mocker.patch("openpilot.system.updated.updated.HARDWARE.get_device_type", return_value=device_type)
  mocker.patch.object(Updater, "get_branch", return_value=branch)

  assert Updater().target_branch == branch

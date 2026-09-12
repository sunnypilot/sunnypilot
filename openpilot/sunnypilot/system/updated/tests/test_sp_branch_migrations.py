"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase

from openpilot.common.params import Params
from openpilot.system.updated.updated import Updater


class TestBranchMigrations(OpenpilotTestCase):
  @parameterized.expand([
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
  ], names=["device_type", "branch", "expected"])
  def test_sp_branch_migrations_from_current_branch(self, mocker, device_type, branch, expected):
    params = Params()
    params.remove("UpdaterTargetBranch")

    mocker.patch("openpilot.system.updated.updated.HARDWARE.get_device_type", return_value=device_type)
    mocker.patch.object(Updater, "get_branch", return_value=branch)

    assert Updater().target_branch == expected


  @parameterized.expand([
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
  ], names=["device_type", "branch", "expected"])
  def test_sp_branch_migrations_from_param(self, mocker, device_type, branch, expected):
    params = Params()
    params.put("UpdaterTargetBranch", branch, block=True)

    mocker.patch("openpilot.system.updated.updated.HARDWARE.get_device_type", return_value=device_type)

    try:
      assert Updater().target_branch == expected
    finally:
      params.remove("UpdaterTargetBranch")


  @parameterized.expand([
    ("tici", "unknown"),
    ("tizi", "unknown"),
    ("mici", "unknown"),
  ], names=["device_type", "branch"])
  def test_sp_branch_migrations_passthrough(self, mocker, device_type, branch):
    params = Params()
    params.remove("UpdaterTargetBranch")

    mocker.patch("openpilot.system.updated.updated.HARDWARE.get_device_type", return_value=device_type)
    mocker.patch.object(Updater, "get_branch", return_value=branch)

    assert Updater().target_branch == branch

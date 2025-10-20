import platform
import pytest

import cereal.messaging as messaging

from sunnypilot.navd.navigationd import Navigationd
from openpilot.sunnypilot.navd.helpers import Coordinate


class TestNavigationd:
  is_darwin = platform.system() == "Darwin"

  @pytest.fixture(autouse=True)
  def setup_method(self, mocker):
    if self.is_darwin:
      mocker.patch('cereal.messaging.SubMaster')
      mocker.patch('cereal.messaging.PubMaster')

  def test_init(self):
    nav = Navigationd()
    assert nav.sm is not None
    assert nav.pm is not None
    assert nav.rk is not None
    assert nav.route is None
    assert nav.destination is None
    assert nav.new_destination == ''
    assert nav.frame == -1
    assert nav.last_position is None
    assert not nav.is_metric
    assert not nav.valid

  def test_update_params(self):
    nav = Navigationd()
    nav.last_position = None
    nav._update_params()
    assert nav.frame == -1
    nav.last_position = Coordinate(latitude=37.0, longitude=128.0)
    nav._update_params()
    assert nav.frame == 0  # frame only updates when last position is set

  def test_update_navigation_no_position(self):
    nav = Navigationd()
    nav.last_position = None
    banner, progress, nav_data = nav._update_navigation()
    assert banner == ''
    assert progress is None
    assert nav_data == {}

  def test_update_navigation(self):
    nav = Navigationd()
    nav.last_position = Coordinate(latitude=37.0, longitude=128.0)
    nav.route = {'580 Winchester dr, oxnard, CA': True}
    banner, progress, nav_data = nav._update_navigation()
    assert isinstance(banner, str)
    assert not progress  # no route was actually set
    assert isinstance(nav_data, dict)

  def test_build_navigation_message(self):
    if self.is_darwin:
      nav = Navigationd()
      msg = nav._build_navigation_message('', None, {})
      assert msg.bannerInstructions == ''
      assert msg.totalDistanceRemaining == 0.0
      assert msg.totalTimeRemaining == 0.0
      assert msg.valid is False
    else:
      sm = messaging.SubMaster(['navigationd'])
      nav = Navigationd()
      msg = nav._build_navigation_message('', None, {})

      nav.pm.send('navigationd', msg)
      sm.update()
      received_msg = sm['navigationd']

      assert received_msg.bannerInstructions == msg.bannerInstructions
      assert received_msg.totalDistanceRemaining == msg.totalDistanceRemaining
      assert received_msg.totalTimeRemaining == msg.totalTimeRemaining
      assert received_msg.valid == msg.valid

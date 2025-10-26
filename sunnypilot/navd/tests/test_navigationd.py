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
      msg = nav._build_navigation_message('', None, {}, True)
      assert msg.navigationd.bannerInstructions == ''
      assert msg.navigationd.valid is False
    else:
      sm = messaging.SubMaster(['navigationd'])
      nav = Navigationd()
      msg = nav._build_navigation_message('', None, {}, True)

      nav.pm.send('navigationd', msg)
      sm.update()
      received_msg = sm['navigationd']

      assert received_msg.bannerInstructions == msg.navigationd.bannerInstructions
      assert received_msg.valid == msg.navigationd.valid

  def test_cancel_route(self):
    nav = Navigationd()
    nav.last_position = Coordinate(latitude=37.0, longitude=128.0)
    nav.route = {'580 Winchester dr, oxnard, CA': True}
    nav.cancel_route_counter = 30
    nav._update_params()
    assert nav.route is None
    assert nav.destination is None

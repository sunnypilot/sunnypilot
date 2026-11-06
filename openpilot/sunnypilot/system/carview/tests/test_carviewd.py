"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import http.client
import json
import threading

import pytest

from openpilot.sunnypilot.system.carview import carviewd

CAR = {'vEgo': 12.5, 'gear': 'drive', 'engaged': True, 'mads': True, 'vCruise': 104.6}


@pytest.fixture
def server(tmp_path):
  srv = carviewd.make_server(lambda: dict(CAR), tmp_path / "stats.jsonl", host="127.0.0.1", port=0, send_hz=200)
  threading.Thread(target=srv.serve_forever, daemon=True).start()
  yield srv, tmp_path / "stats.jsonl"
  srv.shutdown()
  srv.server_close()


def request(srv, method, path, body=None, headers=None):
  conn = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
  conn.request(method, path, body=body, headers=headers or {})
  return conn, conn.getresponse()


def test_serves_the_page(server):
  srv, _ = server
  _, r = request(srv, "GET", "/")
  assert r.status == 200
  assert r.getheader("Content-Type").startswith("text/html")
  assert b"new EventSource('/events')" in r.read()


@pytest.mark.parametrize("path,content_type,marker", [
  ("/cars.js", "text/javascript", b"export function buildCar"),
  ("/view.js", "text/javascript", b"export function createView"),
  ("/garage", "text/html", b"import { buildCar"),
  ("/test", "text/html", b"carview test"),
])
def test_serves_the_scene_and_the_other_pages(server, path, content_type, marker):
  srv, _ = server
  _, r = request(srv, "GET", path)
  assert r.status == 200
  assert r.getheader("Content-Type").startswith(content_type)
  assert marker in r.read()


def test_every_served_file_exists():
  for name, _ in carviewd.STATIC_FILES.values():
    assert (carviewd.STATIC_DIR / name).is_file()


def test_unknown_paths_are_not_found(server):
  srv, _ = server
  for method, path in (("GET", "/../carviewd.py"), ("GET", "/static/index.html"), ("POST", "/")):
    _, r = request(srv, method, path, body=b"{}", headers={"Content-Length": "2"})
    assert r.status == 404


def test_streams_the_car_state_with_a_sequence(server):
  srv, _ = server
  conn, r = request(srv, "GET", "/events")
  assert r.getheader("Content-Type") == "text/event-stream"
  events = []
  while len(events) < 3:
    line = r.fp.readline().decode().strip()
    if line.startswith("data: "):
      events.append(json.loads(line[len("data: "):]))
  conn.close()
  assert all(e['vEgo'] == CAR['vEgo'] and e['gear'] == 'drive' and 'ts' in e for e in events)
  assert [e['n'] for e in events] == sorted(e['n'] for e in events) and len({e['n'] for e in events}) == 3


def test_a_report_is_logged_with_the_car_state(server):
  srv, log = server
  page = {'fps': 60, 'webgl2': True, 'visibility': 'visible'}
  _, r = request(srv, "POST", "/report", body=json.dumps(page), headers={"Content-Type": "application/json"})
  assert r.status == 200 and 'serverTime' in json.loads(r.read())
  record = json.loads(log.read_text().splitlines()[-1])
  assert record['page'] == page
  assert record['car']['gear'] == 'drive' and record['car']['vEgo'] == CAR['vEgo']
  assert record['client'] == "127.0.0.1"


@pytest.mark.parametrize("body", [b"not json", b"[1, 2]", b""])
def test_a_bad_report_is_refused_and_not_logged(server, body):
  srv, log = server
  _, r = request(srv, "POST", "/report", body=body, headers={"Content-Length": str(len(body))})
  assert r.status in (400, 413)
  assert not log.exists()


def test_an_oversized_report_is_refused(server):
  srv, log = server
  body = json.dumps({'pad': "x" * carviewd.MAX_REPORT_BYTES})
  _, r = request(srv, "POST", "/report", body=body)
  assert r.status == 413
  assert not log.exists()


def test_too_many_streams_are_turned_away(server):
  srv, _ = server
  open_streams = [request(srv, "GET", "/events") for _ in range(carviewd.MAX_STREAMS)]
  assert all(r.status == 200 for _, r in open_streams)
  _, r = request(srv, "GET", "/events")
  assert r.status == 503
  for conn, _ in open_streams:
    conn.close()


def test_the_log_rolls_over_past_its_size(tmp_path):
  log = tmp_path / "stats.jsonl"
  for i in range(5):
    carviewd.append_report(log, {'i': i, 'pad': "x" * 40}, max_bytes=100)
  rolled = tmp_path / "stats.jsonl.1"
  assert rolled.exists()
  assert log.stat().st_size <= 100 + 60
  last = [json.loads(line)['i'] for line in log.read_text().splitlines()]
  assert last[-1] == 4


def test_it_runs_only_while_the_enabled_file_exists(tmp_path, monkeypatch):
  from openpilot.system.manager import process_config
  flag = tmp_path / "enabled"
  monkeypatch.setattr(process_config, "carview_enabled_path", lambda: flag)
  assert not process_config.carview(True, None, None)
  flag.touch()
  assert process_config.carview(True, None, None) and process_config.carview(False, None, None)
  assert any(p.name == "carviewd" for p in process_config.procs)


class FakeSM:
  """The latest message of each service carviewd reads, as SubMaster gives them."""

  def __init__(self, alive=True):
    from openpilot.cereal import messaging
    self.builders = {s: messaging.new_message(s) for s in carviewd.SERVICES}
    self.alive = dict.fromkeys(carviewd.SERVICES, alive)

  def __getitem__(self, service):
    return getattr(self.builders[service], service)


def test_view_state_reads_real_message_fields_with_nothing_set():
  # every field it reads has to exist in these message types, or the page gets nothing
  state = carviewd.view_state(FakeSM())
  assert state['gear'] == 'unknown' and state['leads'] == [] and state['speedLimit'] == 0.
  assert 'nav' not in state


def test_view_state_carries_the_road_the_leads_and_the_cues():
  sm = FakeSM()
  m = sm['modelV2']
  xs = [float(i) for i in range(33)]
  m.position.x, m.position.y, m.position.z = xs, [0.1] * 33, [0.0] * 33
  m.init('laneLines', 4)
  for i, line in enumerate(m.laneLines):
    line.x, line.y, line.z = xs, [-5.4 + 3.6 * i] * 33, [1.3] * 33
  m.laneLineProbs = [0.2, 0.9, 0.9, 0.2]
  m.init('roadEdges', 2)
  for i, edge in enumerate(m.roadEdges):
    edge.x, edge.y, edge.z = xs, [-7.0 + 14 * i] * 33, [1.3] * 33
  m.roadEdgeStds = [0.3, 0.4]
  lead = sm['radarState'].leadOne
  lead.present, lead.dRel, lead.yRel, lead.vLead, lead.aLeadK = True, 30.0, 0.5, 12.0, -1.5
  sm['longitudinalPlanSP'].speedLimit.resolver.speedLimit = 29.06
  sm['longitudinalPlanSP'].speedLimit.resolver.speedLimitValid = True
  nav = sm['navInstruction']
  nav.maneuverPrimaryText, nav.maneuverDistance, nav.maneuverModifier = "Marsh St", 1609.0, "right"

  state = carviewd.view_state(sm)
  assert len(state['model']['path'][0]) == 33 and len(state['model']['lines']) == 4 and len(state['model']['edges']) == 2
  assert state['model']['lineProbs'] == [0.2, 0.9, 0.9, 0.2]
  assert state['leads'] == [{'d': 30.0, 'y': 0.5, 'v': 12.0, 'a': -1.5}]
  assert state['speedLimit'] == 29.06
  assert state['nav']['primary'] == "Marsh St" and state['nav']['modifier'] == "right"
  json.dumps(state)  # the page gets it as JSON


def test_view_state_leaves_out_a_model_that_isnt_running():
  assert 'model' not in carviewd.view_state(FakeSM(alive=False))


class FakeNet:
  """ip and iptables-legacy as the hotspot helper sees them, recording what it asks for."""

  def __init__(self, tethering, car_address, nat, uplink="ppp0"):
    self.tethering, self.car_address, self.nat, self.uplink, self.calls = tethering, car_address, nat, uplink, []

  def __call__(self, cmd):
    self.calls.append(cmd)
    if cmd[:4] == ["ip", "-4", "-o", "addr"]:
      out = "1: lo    inet 127.0.0.1/8 scope host lo\n"
      if self.car_address:
        out += f"1: lo    inet {carviewd.CAR_ADDRESS}/32 scope global lo\n"
      if self.tethering and "lo" not in cmd:
        out += f"3: wlan0    inet {carviewd.TETHER_ADDRESS}/24 brd 192.168.43.255 scope global wlan0\n"
      return 0, out
    if cmd[:3] == ["ip", "route", "show"]:
      return 0, f"default via 10.64.64.64 dev {self.uplink} metric 1000\n" if self.uplink else ""
    if "-C" in cmd:
      return (0 if self.nat else 1), ""
    return 0, ""

  def asked(self, *words):
    return [c for c in self.calls if all(w in c for w in words)]


def test_hotspot_on_gets_the_car_address_and_internet_sharing():
  net = FakeNet(tethering=True, car_address=False, nat=False)
  carviewd.Hotspot(net).update()
  assert net.asked("sudo", "addr", "add", f"{carviewd.CAR_ADDRESS}/32", "lo")
  assert net.asked("iptables-legacy", "-A", "ppp0", "MASQUERADE")


def test_hotspot_already_set_up_is_left_alone():
  net = FakeNet(tethering=True, car_address=True, nat=True)
  carviewd.Hotspot(net).update()
  assert not net.asked("sudo", "add") and not net.asked("-A")


def test_off_the_hotspot_the_car_address_is_taken_away():
  net = FakeNet(tethering=False, car_address=True, nat=False)
  carviewd.Hotspot(net).update()
  assert net.asked("sudo", "addr", "del", f"{carviewd.CAR_ADDRESS}/32", "lo")
  assert not net.asked("iptables-legacy")


def test_no_uplink_means_no_sharing_rule():
  net = FakeNet(tethering=True, car_address=True, nat=False, uplink=None)
  carviewd.Hotspot(net).update()
  assert not net.asked("iptables-legacy")

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
  ("/garage", "text/html", b"import { buildCar"),
])
def test_serves_the_car_models_and_the_garage(server, path, content_type, marker):
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

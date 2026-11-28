"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import signal
import time
from collections import deque
from itertools import count

from jeepney import DBusAddress, HeaderFields, MessageType, new_error, new_method_call, new_method_return

from openpilot.common.test import Mocker, OpenpilotTestCase
from openpilot.sunnypilot.system import bluetooth_manager as bm
from openpilot.sunnypilot.system import connect_phone as cp

ADAPTER = "/org/bluez/hci0"
DEVICE = ADAPTER + "/dev_4A_3B_2C_1D_0E_0F"
SETUP = ["GetManagedObjects", "UnregisterAdvertisement", "UnregisterApplication", "Pairable", "Alias", "Powered",
         "DiscoverableTimeout", "Discoverable", "RegisterApplication", "RegisterAdvertisement"]
TEARDOWN = ["UnregisterAdvertisement", "UnregisterApplication", "Discoverable", "Powered"]


def variant(value) -> tuple:
  return "b" if isinstance(value, bool) else "s" if isinstance(value, str) else "u", value


class FakeBus:
  """Stands in for the system bus: records what is sent and answers method calls the way BlueZ does."""

  def __init__(self, failing: tuple[str, ...] = (), adapter: bool = True):
    self.outgoing_serial = count(1)
    self.sent: list = []
    self.inbox: deque = deque()
    self.failing = failing  # method names, or property names for Set
    self.adapter = adapter
    self.owner = 5  # bluetoothd is ":1.<owner>" on the bus
    self.registered: set[str] = set()  # object paths registered with the running bluetoothd
    self.props = {"Powered": False, "Pairable": True, "Alias": "comma-0a1b2c3d", "Discoverable": False}
    self.devices: dict[str, dict[str, bool]] = {}
    self.dead = False
    self.hung = False  # bluetoothd takes calls and never answers
    self.closed = False
    self.timeout = 0.0

  def restart_bluetoothd(self):
    # a killed bluetoothd comes back under a new name without its registrations; the kernel keeps the adapter powered
    self.owner += 1
    self.registered.clear()

  def objects(self) -> dict:
    if not self.adapter:
      return {}
    adapter = {
      bm.ADAPTER_IFACE: {name: variant(value) for name, value in self.props.items()},
      bm.GATT_MANAGER_IFACE: {},
      bm.ADVERTISING_MANAGER_IFACE: {"ActiveInstances": ("y", int(bm.ADVERTISEMENT_PATH in self.registered))},
    }
    return {ADAPTER: adapter} | {path: {bm.DEVICE_IFACE: {name: variant(value) for name, value in props.items()}}
                                 for path, props in self.devices.items()}

  def send(self, msg, serial=None):
    if self.dead:
      raise BrokenPipeError
    msg.header.serial = next(self.outgoing_serial) if serial is None else serial
    msg.serialise()  # raises when a body does not match its signature  # codespell:ignore serialise
    self.sent.append(msg)
    if msg.header.message_type != MessageType.method_call or self.hung:
      return

    member = msg.header.fields[HeaderFields.member]
    if (msg.body[1] if member == "Set" else member) in self.failing:
      reply = new_error(msg, "org.bluez.Error.Failed")
    elif not self.adapter and msg.header.fields[HeaderFields.path].startswith(ADAPTER):
      reply = new_error(msg, "org.freedesktop.DBus.Error.UnknownObject")
    elif member == "RemoveDevice" and not self.props["Powered"]:
      reply = new_error(msg, "org.bluez.Error.NotReady")
    elif member == "GetManagedObjects":
      reply = new_method_return(msg, "a{oa{sa{sv}}}", (self.objects(),))
    else:
      if member == "Set":
        self.props[msg.body[1]] = msg.body[2][1]
      elif member.startswith("Register"):
        self.registered.add(msg.body[0])
      elif member.startswith("Unregister"):
        self.registered.discard(msg.body[0])
      elif member == "RemoveDevice":
        del self.devices[msg.body[0]]
      reply = new_method_return(msg)
    reply.header.fields[HeaderFields.sender] = f":1.{self.owner}"
    self.inbox.append(reply)

  def receive(self, timeout: float = 0.0):
    self.timeout = timeout
    if self.dead:
      raise ConnectionResetError
    if not self.inbox:
      raise TimeoutError
    return self.inbox.popleft()

  def close(self):
    self.closed = True

  def calls(self) -> list[str]:
    return [m.body[1] if (member := m.header.fields[HeaderFields.member]) == "Set" else member
            for m in self.sent if m.header.message_type == MessageType.method_call]


class FakeParams:
  def __init__(self, values: dict | None = None, bus: FakeBus | None = None):
    self.bus = bus
    self.data = values or {}
    self.puts: list[str] = []

  def get(self, key):
    return self.data.get(key)

  def get_bool(self, key):
    return bool(self.data.get(key))

  def put(self, key, value):
    self.data[key] = value
    self.puts.append(key)
    if self.bus is not None and key == "BluetoothEnabled" and not value:
      self.bus.adapter = False  # AGNOS stops the UART attach, and BlueZ drops the adapter

  put_bool = put

  def remove(self, key):
    self.data.pop(key, None)


def make(mocker: Mocker, **bus_kwargs) -> tuple[bm.BluetoothManager, FakeBus]:
  bus = FakeBus(**bus_kwargs)
  mocker.patch.object(bm, "Params", return_value=FakeParams(bus=bus))
  mocker.patch.object(bm, "CALL_TIMEOUT", 0.01)
  manager = bm.BluetoothManager(mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock())
  manager._conn = bus
  return manager, bus


def make_ready(mocker: Mocker) -> tuple[bm.BluetoothManager, FakeBus]:
  manager, bus = make(mocker)
  manager.set_enabled(True)
  manager._reconcile()
  assert manager.ready
  bus.sent.clear()
  return manager, bus


def incoming(path: str, iface: str, member: str, signature: str | None = None, body: tuple = ()):
  msg = new_method_call(DBusAddress(path, ":1.42", iface), member, signature, body)
  msg.header.serial = 1000
  msg.header.fields[HeaderFields.sender] = ":1.5"
  return msg


def from_bluez(manager: bm.BluetoothManager, bus: FakeBus, *call):
  """Deliver a method call from BlueZ and return the reply."""
  bus.sent.clear()
  manager._dispatch(incoming(*call))
  return bus.sent[-1]


def write(manager: bm.BluetoothManager, bus: FakeBus, value: bytes, **options):
  options = {"device": ("o", DEVICE), "mtu": ("q", 247), "link": ("s", "LE")} | options
  return from_bluez(manager, bus, bm.RX_PATH, bm.GATT_CHARACTERISTIC_IFACE, "WriteValue", "aya{sv}", (value, options))


def disconnects(bus: FakeBus) -> list[str]:
  return [m.header.fields[HeaderFields.path] for m in bus.sent if m.header.fields.get(HeaderFields.member) == "Disconnect"]


class TestObjects(OpenpilotTestCase):
  def test_gatt_tree_never_asks_for_pairing(self, mocker):
    manager, bus = make(mocker)
    reply = from_bluez(manager, bus, bm.APP_PATH, bm.OBJECT_MANAGER_IFACE, "GetManagedObjects")

    tree = reply.body[0]
    assert set(tree) == {bm.SERVICE_PATH, bm.RX_PATH, bm.TX_PATH}
    flags = [f for path in (bm.RX_PATH, bm.TX_PATH) for f in tree[path][bm.GATT_CHARACTERISTIC_IFACE]["Flags"][1]]
    assert sorted(flags) == ["notify", "write", "write-without-response"]

  def test_advertisement_has_no_name_or_tx_power(self, mocker):
    manager, bus = make(mocker)
    reply = from_bluez(manager, bus, bm.ADVERTISEMENT_PATH, bm.PROPERTIES_IFACE, "GetAll", "s", (bm.ADVERTISEMENT_IFACE,))

    assert reply.body[0] == {"Type": ("s", "peripheral"), "ServiceUUIDs": ("as", [bm.SERVICE_UUID])}

  def test_unknown_method_gets_an_error(self, mocker):
    manager, bus = make(mocker)
    reply = from_bluez(manager, bus, bm.RX_PATH, bm.GATT_CHARACTERISTIC_IFACE, "ReadValue", "a{sv}", ({},))

    assert reply.header.message_type == MessageType.error


class TestWrite(OpenpilotTestCase):
  def test_write_reaches_callback(self, mocker):
    manager, bus = make(mocker)
    reply = write(manager, bus, b"\x01\x02")

    manager._on_write.assert_called_once_with(DEVICE, b"\x01\x02", 247)
    assert manager.connected == {DEVICE}
    assert disconnects(bus) == []
    assert reply.header.message_type == MessageType.method_return
    assert reply.header.fields[HeaderFields.reply_serial] == 1000

  def test_write_at_an_offset_disconnects(self, mocker):
    manager, bus = make(mocker)
    write(manager, bus, b"\x01", offset=("q", 20))

    manager._on_write.assert_not_called()
    assert disconnects(bus) == [DEVICE]

  def test_write_longer_than_one_packet_disconnects(self, mocker):
    manager, bus = make(mocker)
    write(manager, bus, bytes(244))
    manager._on_write.assert_called_once()

    write(manager, bus, bytes(245))
    manager._on_write.assert_called_once()
    assert disconnects(bus) == [DEVICE]

  def test_failing_callback_keeps_serving(self, mocker):
    manager, bus = make(mocker)
    manager._on_write.side_effect = ValueError
    reply = write(manager, bus, b"\x01")

    assert reply.header.message_type == MessageType.method_return

  def test_notify_sends_value(self, mocker):
    manager, bus = make(mocker)
    assert manager.notify(b"\x05\x06")

    signal = bus.sent[-1]
    assert signal.header.fields[HeaderFields.path] == bm.TX_PATH
    assert signal.body == (bm.GATT_CHARACTERISTIC_IFACE, {"Value": ("ay", b"\x05\x06")}, [])

  def test_notify_reports_what_was_not_sent(self, mocker):
    manager, bus = make(mocker)
    bus.dead = True
    assert not manager.notify(b"\x05")

    manager._conn = None
    assert not manager.notify(b"\x05")

  def test_disconnect(self, mocker):
    manager, bus = make(mocker)
    manager.disconnect(DEVICE)

    assert disconnects(bus) == [DEVICE]
    assert bus.sent[-1].header.fields[HeaderFields.interface] == bm.DEVICE_IFACE


class TestReconcile(OpenpilotTestCase):
  def test_setup_order(self, mocker):
    manager, bus = make(mocker)
    manager.set_enabled(True)
    manager._reconcile()

    assert manager.ready
    assert bus.calls() == SETUP
    assert bus.props == {"Powered": True, "Pairable": False, "Alias": "comma", "DiscoverableTimeout": 0, "Discoverable": True}

  def test_set_enabled_writes_only_on_change(self, mocker):
    manager, bus = make(mocker)
    manager.set_enabled(False)
    manager._reconcile()
    assert manager._params.puts == []

    manager.set_enabled(True)
    manager.set_enabled(True)
    assert manager._params.puts == ["BluetoothEnabled"]
    assert manager._params.data["BluetoothEnabled"] is True

  def test_disabled_does_nothing(self, mocker):
    manager, bus = make(mocker)
    manager._reconcile()

    assert not manager.ready
    assert bus.calls() == []

  def test_waits_for_adapter(self, mocker):
    manager, bus = make(mocker, adapter=False)
    manager.set_enabled(True)
    manager._reconcile()
    assert not manager.ready

    bus.adapter = True
    manager._reconcile()
    assert manager.ready

  def test_never_advertises_while_bondable(self, mocker):
    manager, bus = make(mocker, failing=("Pairable",))
    manager.set_enabled(True)
    manager._reconcile()

    assert not manager.ready
    assert "Powered" not in bus.calls()
    assert "RegisterAdvertisement" not in bus.calls()

  def test_never_powers_on_under_the_hostname(self, mocker):
    manager, bus = make(mocker, failing=("Alias",))
    manager.set_enabled(True)
    manager._reconcile()

    assert not manager.ready
    assert "Powered" not in bus.calls()

  def test_failed_registration_is_rolled_back(self, mocker):
    manager, bus = make(mocker, failing=("RegisterAdvertisement",))
    manager.set_enabled(True)
    manager._reconcile()

    assert not manager.ready
    assert bus.calls()[-2:] == ["UnregisterAdvertisement", "UnregisterApplication"]

  def test_healthy_adapter_costs_one_call(self, mocker):
    manager, bus = make_ready(mocker)
    manager._reconcile()

    assert manager.ready
    assert bus.calls() == ["GetManagedObjects"]

  def test_registers_again_after_power_loss(self, mocker):
    manager, bus = make_ready(mocker)
    bus.props["Powered"] = False
    manager._reconcile()

    assert manager.ready
    assert bus.calls() == SETUP

  def test_registers_again_when_made_pairable(self, mocker):
    manager, bus = make_ready(mocker)
    bus.props["Pairable"] = True
    manager._reconcile()

    assert manager.ready
    assert bus.calls() == SETUP
    assert not bus.props["Pairable"]

  def test_registers_again_after_bluetoothd_restart(self, mocker):
    manager, bus = make_ready(mocker)
    bus.restart_bluetoothd()
    assert bus.props["Powered"]
    manager._reconcile()

    assert manager.ready
    assert bus.calls() == SETUP
    assert bus.registered == {bm.APP_PATH, bm.ADVERTISEMENT_PATH}

  def test_paired_device_is_removed_before_advertising(self, mocker):
    manager, bus = make_ready(mocker)
    bus.props["Pairable"] = True
    bus.devices[DEVICE] = {"Connected": False, "Paired": True}
    manager._reconcile()

    assert manager.ready
    assert bus.devices == {}
    calls = bus.calls()
    assert calls.index("Powered") < calls.index("RemoveDevice") < calls.index("RegisterApplication")

  def test_registers_again_after_release(self, mocker):
    manager, bus = make_ready(mocker)
    from_bluez(manager, bus, bm.ADVERTISEMENT_PATH, bm.ADVERTISEMENT_IFACE, "Release")
    assert not manager.ready

    manager._reconcile()
    assert manager.ready

  def test_disable_powers_off_before_the_param_clears(self, mocker):
    manager, bus = make_ready(mocker)
    manager.set_enabled(False)
    assert manager._params.data["BluetoothEnabled"] is True

    manager._reconcile()
    assert not manager.ready
    assert bus.calls() == TEARDOWN
    assert not bus.props["Powered"] and not bus.props["Discoverable"]
    assert manager._params.data["BluetoothEnabled"] is False
    assert not bus.adapter

    manager._reconcile()
    assert bus.calls() == TEARDOWN
    assert manager._params.puts.count("BluetoothEnabled") == 2

  def test_tick_runs_while_bluetoothd_does_not_answer(self, mocker):
    manager, bus = make_ready(mocker)
    bus.hung = True
    manager._reconcile()

    manager._on_tick.assert_called_once_with()

  def test_unanswered_reconcile_keeps_the_adapter_for_teardown(self, mocker):
    manager, bus = make_ready(mocker)
    bus.hung = True
    manager._reconcile()
    assert manager.ready

    bus.hung = False
    bus.sent.clear()
    manager.set_enabled(False)
    manager._reconcile()
    assert bus.calls() == TEARDOWN
    assert not bus.props["Powered"]

  def test_stop_abandons_a_waiting_call(self, mocker):
    manager, bus = make_ready(mocker)
    mocker.patch.object(bm, "CALL_TIMEOUT", 5.0)
    mocker.patch.object(manager, "_on_tick", side_effect=manager.stop)
    bus.hung = True
    started = time.monotonic()
    manager._reconcile()

    assert time.monotonic() - started < 1.0

  def test_stop_skips_the_remaining_setup_steps(self, mocker):
    manager, bus = make(mocker)
    send = bus.send

    def stop_after_alias(msg, serial=None):
      send(msg, serial)
      if msg.body[1:2] == ("Alias",):
        manager.stop()
    mocker.patch.object(bus, "send", side_effect=stop_after_alias)
    manager.set_enabled(True)
    manager._reconcile()

    assert not manager.ready
    assert bus.calls()[-1] == "Alias"

  def test_connected_devices(self, mocker):
    manager, bus = make_ready(mocker)
    mocker.patch.object(manager, "_on_disconnect", side_effect=ValueError)
    bus.devices[DEVICE] = {"Connected": True, "Paired": False}
    manager._reconcile()
    assert manager.connected == {DEVICE}
    manager._on_disconnect.assert_not_called()

    bus.devices[DEVICE]["Connected"] = False
    manager._reconcile()
    assert manager.connected == frozenset()
    manager._on_disconnect.assert_called_once_with(DEVICE)
    assert manager.ready

  def test_device_seen_only_by_its_write_is_reported_gone(self, mocker):
    manager, bus = make_ready(mocker)
    write(manager, bus, b"\x01")
    manager._reconcile()

    manager._on_disconnect.assert_called_once_with(DEVICE)

  def test_serves_bluez_while_waiting_for_a_reply(self, mocker):
    manager, bus = make(mocker)
    bus.inbox.append(incoming(bm.APP_PATH, bm.OBJECT_MANAGER_IFACE, "GetManagedObjects"))

    assert manager._call(new_method_call(DBusAddress(ADAPTER, bm.BLUEZ, bm.GATT_MANAGER_IFACE), "RegisterApplication", "oa{sv}", (bm.APP_PATH, {}))) == ()
    assert bus.sent[-1].header.fields[HeaderFields.reply_serial] == 1000


class TestRun(OpenpilotTestCase):
  def run_manager(self, mocker):
    manager, bus = make(mocker)
    manager._conn = None
    mocker.patch.object(bm, "open_dbus_connection", return_value=bus)
    mocker.patch.object(bm, "RECONCILE_PERIOD", 0)
    manager.set_enabled(True)
    return manager, bus

  def test_stop_powers_off_and_closes(self, mocker):
    manager, bus = self.run_manager(mocker)
    manager._on_tick.side_effect = manager.stop
    manager.run()

    manager._on_tick.assert_called_once_with()
    assert bus.calls() == SETUP + TEARDOWN
    assert not bus.props["Powered"] and not bus.props["Discoverable"]
    assert bus.closed
    assert not manager.ready
    assert not manager.notify(b"\x05")

  def test_dead_bus_still_closes(self, mocker):
    manager, bus = self.run_manager(mocker)
    manager._on_tick.side_effect = lambda: setattr(bus, "dead", True)

    with self.assertRaises(ConnectionResetError):
      manager.run()
    assert bus.closed
    assert manager._conn is None
    assert not manager.ready

  def test_calls_are_short_once_stopping(self, mocker):
    manager, bus = make(mocker)
    mocker.patch.object(bm, "CALL_TIMEOUT", 5.0)
    manager.stop()
    manager._call(new_method_call(DBusAddress(ADAPTER, bm.BLUEZ, bm.GATT_MANAGER_IFACE), "UnregisterApplication", "o", (bm.APP_PATH,)))

    assert 0 < bus.timeout <= bm.STOP_CALL_TIMEOUT

  def test_failing_tick_keeps_running(self, mocker):
    manager, bus = self.run_manager(mocker)

    def tick():
      if manager._on_tick.call_count == 1:
        raise ValueError
      manager.stop()
    manager._on_tick.side_effect = tick
    manager.run()

    assert manager._on_tick.call_count == 2
    assert bus.closed


def make_daemon(mocker: Mocker, **values):
  mocker.patch.object(cp, "qr_text", return_value="SLC1:qr")
  mocker.patch.object(bm, "grant_count", return_value=0)
  params = FakeParams({"BluetoothAllowed": True} | values)
  bt = mocker.patch.object(bm, "BluetoothManager").return_value
  bt.ready = False
  return bm.Daemon(params, cp.ConnectPhoneWindow()), params, bt


def request(params: FakeParams, action: str, seq: int):
  params.data[cp.REQUEST_KEY] = {"seq": seq, "action": action}


class TestDaemon(OpenpilotTestCase):
  def test_open_then_ready(self, mocker):
    daemon, params, bt = make_daemon(mocker)
    request(params, "open", 7)
    daemon.step(100.0)

    assert cp.REQUEST_KEY not in params.data
    window = params.data[cp.WINDOW_KEY]
    assert (window["seq"], window["state"], window["qr"], window["deadline"]) == (7, "starting", "SLC1:qr", 100.0 + cp.WINDOW_SECONDS)
    bt.set_enabled.assert_called_with(True)

    bt.ready = True
    daemon.step(101.0)
    assert params.data[cp.WINDOW_KEY]["state"] == "open"

  def test_window_is_written_only_when_it_changes(self, mocker):
    daemon, params, bt = make_daemon(mocker)
    daemon.step(100.0)
    daemon.step(101.0)
    assert params.puts == [cp.WINDOW_KEY, bm.STATUS_KEY]
    assert params.data[cp.WINDOW_KEY] == {"seq": 0, "state": "closed", "reason": "", "prompt": None}
    bt.set_enabled.assert_called_with(False)

  def test_cancel(self, mocker):
    daemon, params, bt = make_daemon(mocker)
    request(params, "open", 7)
    daemon.step(100.0)
    request(params, "cancel", 8)
    daemon.step(101.0)

    assert params.data[cp.WINDOW_KEY] == {"seq": 7, "state": "closed", "reason": "cancel", "prompt": None}
    bt.set_enabled.assert_called_with(False)

  def test_not_opened_while_bluetooth_is_off(self, mocker):
    daemon, params, bt = make_daemon(mocker, BluetoothAllowed=False)
    request(params, "open", 7)
    daemon.step(100.0)

    assert params.data[cp.WINDOW_KEY] == {"seq": 7, "state": "closed", "reason": "bluetooth_off"}
    cp.qr_text.assert_not_called()
    bt.set_enabled.assert_called_with(False)

  def test_turning_bluetooth_off_closes_the_window(self, mocker):
    daemon, params, bt = make_daemon(mocker)
    request(params, "open", 7)
    daemon.step(100.0)
    params.data["BluetoothAllowed"] = False
    daemon.step(101.0)

    assert params.data[cp.WINDOW_KEY] == {"seq": 7, "state": "closed", "reason": "bluetooth_off", "prompt": None}
    bt.set_enabled.assert_called_with(False)

  def test_missing_device_key(self, mocker):
    daemon, params, bt = make_daemon(mocker)
    cp.qr_text.side_effect = RuntimeError
    request(params, "open", 7)
    daemon.step(100.0)

    assert params.data[cp.WINDOW_KEY] == {"seq": 7, "state": "closed", "reason": "no_key"}
    bt.set_enabled.assert_called_with(False)

    cp.qr_text.side_effect = ValueError
    request(params, "open", 8)
    daemon.step(101.0)
    assert params.data[cp.WINDOW_KEY] == {"seq": 8, "state": "closed", "reason": "error"}

    cp.qr_text.side_effect = None
    request(params, "open", 9)
    daemon.step(102.0)
    assert params.data[cp.WINDOW_KEY]["state"] == "starting"

  def test_a_grant_keeps_bluetooth_on_without_a_window(self, mocker):
    daemon, params, bt = make_daemon(mocker)
    mocker.patch.object(bm, "grant_count", return_value=1)
    daemon.step(100.0)
    bt.set_enabled.assert_called_with(True)

    params.data["BluetoothAllowed"] = False
    daemon.step(101.0)
    bt.set_enabled.assert_called_with(False)

  def test_enable_is_written_again_once_without_an_adapter(self, mocker):
    daemon, params, bt = make_daemon(mocker)
    mocker.patch.object(bm, "grant_count", return_value=1)
    for now in (100.0, 109.9):
      daemon.step(now)
    assert "BluetoothEnabled" not in params.puts

    for now in (110.0, 111.0, 130.0):
      daemon.step(now)
    assert params.puts.count("BluetoothEnabled") == 1

    bt.ready = True
    daemon.step(131.0)
    bt.ready = False
    for now in (132.0, 142.0):
      daemon.step(now)
    assert params.puts.count("BluetoothEnabled") == 2

  def test_write_disconnects_the_phone(self, mocker):
    daemon, params, bt = make_daemon(mocker)
    daemon.on_write(DEVICE, b"\x01", 247)

    bt.disconnect.assert_called_once_with(DEVICE)

  def run_main(self, mocker, runs: list):
    handlers = mocker.patch.object(bm.signal, "signal")
    params = FakeParams({"BluetoothAllowed": True})
    mocker.patch.object(bm, "Params", return_value=params)
    mocker.patch.object(bm, "RESTART_BACKOFF", 0.03)
    mocker.patch.object(bm, "RECONCILE_PERIOD", 0.01)
    mocker.patch.object(bm, "grant_count", return_value=0)
    manager = mocker.patch.object(bm, "BluetoothManager")
    def run(*_):
      outcome = runs.pop(0)
      if outcome == "signal":
        handlers.call_args.args[1](signal.SIGTERM, None)
      else:
        raise outcome
    manager.return_value.run.side_effect = run
    bm.main()
    return manager, handlers, params

  def test_main_wires_the_manager(self, mocker):
    manager, handlers, params = self.run_main(mocker, ["signal"])

    bt = manager.return_value
    bt.run.assert_called_once_with()
    bt.stop.assert_called_once_with()
    assert [call.args[0] for call in handlers.call_args_list] == [signal.SIGINT, signal.SIGTERM]
    on_write, on_disconnect, on_tick = manager.call_args.args
    on_write(DEVICE, b"\x01", 247)
    bt.disconnect.assert_called_once_with(DEVICE)
    on_tick()
    bt.set_enabled.assert_called_with(False)

  def test_main_replaces_a_failed_manager_and_keeps_ticking(self, mocker):
    manager, handlers, params = self.run_main(mocker, [ConnectionResetError(), ValueError(), "signal"])

    assert manager.call_count == 3
    assert manager.return_value.run.call_count == 3
    assert params.puts == [cp.WINDOW_KEY, bm.STATUS_KEY]

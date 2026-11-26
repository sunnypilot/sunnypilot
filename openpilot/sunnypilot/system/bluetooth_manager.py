"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import selectors
import signal
import threading
import time
from collections.abc import Callable

from jeepney import DBusAddress, HeaderFields, Message, MessageFlag, MessageType, new_error, new_method_call, new_method_return, new_signal
from jeepney.io.threading import open_dbus_connection
from jeepney.wrappers import Properties

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.system.ble.session import Engine
from openpilot.sunnypilot.system.connect_phone import REQUEST_KEY, STATUS_KEY, WINDOW_KEY, ConnectPhoneWindow, grant_count

BLUEZ = "org.bluez"
ADAPTER_IFACE = "org.bluez.Adapter1"
DEVICE_IFACE = "org.bluez.Device1"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHARACTERISTIC_IFACE = "org.bluez.GattCharacteristic1"
ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
OBJECT_MANAGER_IFACE = "org.freedesktop.DBus.ObjectManager"
PROPERTIES_IFACE = "org.freedesktop.DBus.Properties"

SERVICE_UUID = "6530b12c-c8cc-4b5c-a767-5b842c630dfa"
RX_UUID = "a8b19254-6b8c-4074-8846-40b50f7f9583"
TX_UUID = "936a1543-21ef-40a0-9318-201db2f992f7"

APP_PATH = "/sunnypilot/gatt"
SERVICE_PATH = APP_PATH + "/service"
RX_PATH = SERVICE_PATH + "/rx"
TX_PATH = SERVICE_PATH + "/tx"
ADVERTISEMENT_PATH = "/sunnypilot/advertisement"

# no characteristic may carry an encrypt, secure or authorize flag: those start OS pairing
GATT_OBJECTS = {
  SERVICE_PATH: {GATT_SERVICE_IFACE: {"UUID": ("s", SERVICE_UUID), "Primary": ("b", True)}},
  RX_PATH: {GATT_CHARACTERISTIC_IFACE: {"UUID": ("s", RX_UUID), "Service": ("o", SERVICE_PATH), "Flags": ("as", ["write", "write-without-response"])}},
  TX_PATH: {GATT_CHARACTERISTIC_IFACE: {"UUID": ("s", TX_UUID), "Service": ("o", SERVICE_PATH), "Flags": ("as", ["notify"])}},
}
# no LocalName and no Includes: the advertisement carries neither a name nor TX power
OBJECTS = GATT_OBJECTS | {ADVERTISEMENT_PATH: {ADVERTISEMENT_IFACE: {"Type": ("s", "peripheral"), "ServiceUUIDs": ("as", [SERVICE_UUID])}}}

# GAP Device Name, readable by any phone before it authenticates; the default is the hostname, which carries the serial.
# At most 10 bytes: the kernel shortens a longer name in the default scan response.
ALIAS = "comma"

RECONCILE_PERIOD = 1.0  # seconds
CALL_TIMEOUT = 5.0  # seconds
STOP_CALL_TIMEOUT = 0.5  # seconds, once stop() is called: the manager kills the process 5 s after SIGINT
ENABLE_RETRY_AFTER = 10.0  # seconds enabled without a ready adapter
RESTART_BACKOFF = 1.0  # seconds before a new manager replaces a failed one, doubling up to the maximum
RESTART_BACKOFF_MAX = 60.0  # seconds


def _prop(ifaces: dict, iface: str, name: str, default=None):
  return ifaces.get(iface, {}).get(name, (None, default))[1]


class BluetoothManager:
  def __init__(self, on_write: Callable[[str, bytes, int], None], on_disconnect: Callable[[str], None] | None = None,
               on_tick: Callable[[], None] | None = None,
               stream_fds: Callable[[], list[tuple[int, int]]] | None = None,
               on_stream_ready: Callable[[int, bool, bool], None] | None = None,
               has_active_session: Callable[[], bool] | None = None):
    # all callbacks run on the run() thread
    self._on_write = on_write  # device path, value, mtu
    self._on_disconnect = on_disconnect  # device path
    self._on_tick = on_tick
    self._stream_fds = stream_fds
    self._on_stream_ready = on_stream_ready
    self._has_active_session = has_active_session
    self._params = Params()
    self._conn = None
    self._enabled = False
    self._exit = False
    self._adapter: str | None = None  # the adapter this manager has changed; ready implies it is set
    self._ready = False
    self._connected: frozenset[str] = frozenset()
    self._stale_connected_since: float | None = None
    self._failed_step: str | None = None
    self._last_reconcile = 0.0
    self._last_tick = 0.0

  @property
  def ready(self) -> bool:
    return self._ready

  @property
  def connected(self) -> frozenset[str]:
    return self._connected

  def set_enabled(self, enabled: bool):
    # off is written by run() after its teardown: AGNOS removes the adapter as soon as the param clears
    if enabled and not self._params.get_bool("BluetoothEnabled"):
      self._params.put_bool("BluetoothEnabled", True)
    self._enabled = enabled

  def notify(self, data: bytes) -> bool:
    # BlueZ sends a notification to every subscribed device, never to one
    return self._send(new_signal(DBusAddress(TX_PATH, interface=PROPERTIES_IFACE), "PropertiesChanged", "sa{sv}as",
                                 (GATT_CHARACTERISTIC_IFACE, {"Value": ("ay", data)}, [])))

  def disconnect(self, device: str):
    cloudlog.warning(f"bluetooth: disconnecting {device}")
    self._send(new_method_call(DBusAddress(device, BLUEZ, DEVICE_IFACE), "Disconnect"))

  def stop(self):
    self._exit = True

  def run(self):
    self._conn = open_dbus_connection(bus="SYSTEM")
    try:
      while not self._exit:
        if time.monotonic() - self._last_reconcile >= RECONCILE_PERIOD:
          self._last_reconcile = time.monotonic()
          self._reconcile()
        self._tick()
        self._wait_and_dispatch()
    finally:
      try:
        self._teardown()
      except Exception:
        cloudlog.exception("bluetooth: teardown failed")
      conn, self._conn = self._conn, None
      conn.close()
      self._set_connected(frozenset())

  def _wait_and_dispatch(self):
    # Drain any already-buffered D-Bus messages without blocking.
    while not self._exit:
      try:
        self._dispatch(self._conn.receive(timeout=0))
      except TimeoutError:
        break
    if self._exit:
      return

    entries = self._stream_fds() if self._stream_fds is not None else []
    if not entries:
      try:
        self._dispatch(self._conn.receive(timeout=RECONCILE_PERIOD))
      except TimeoutError:
        pass
      return

    dbus_fd = self._conn.sock.fileno()
    sel = selectors.DefaultSelector()
    try:
      sel.register(dbus_fd, selectors.EVENT_READ, data="dbus")
      for fd, events in entries:
        try:
          sel.register(fd, events, data="stream")
        except (OSError, ValueError):
          pass
      ready = sel.select(timeout=RECONCILE_PERIOD)
      for key, mask in ready:
        if key.data == "dbus":
          while not self._exit:
            try:
              self._dispatch(self._conn.receive(timeout=0))
            except TimeoutError:
              break
        else:
          self._callback(
            self._on_stream_ready,
            key.fd,
            bool(mask & selectors.EVENT_READ),
            bool(mask & selectors.EVENT_WRITE),
          )
    finally:
      sel.close()

  def _send(self, msg: Message) -> bool:
    conn = self._conn
    if conn is None:
      return False
    try:
      conn.send(msg)
    except OSError:
      return False
    return True

  def _callback(self, callback: Callable | None, *args):
    if callback is None:
      return
    try:
      callback(*args)
    except Exception:
      cloudlog.exception("bluetooth: callback failed")

  def _tick(self):
    if not self._exit and time.monotonic() - self._last_tick >= RECONCILE_PERIOD:
      self._last_tick = time.monotonic()
      self._callback(self._on_tick)

  def _set_connected(self, connected: frozenset[str]):
    gone, self._connected = self._connected - connected, connected
    for device in gone:
      self._callback(self._on_disconnect, device)

  def _call(self, msg: Message) -> tuple | None:
    # RegisterApplication is answered only after BlueZ has read our objects, so keep serving while waiting
    serial = next(self._conn.outgoing_serial)
    self._conn.send(msg, serial=serial)
    stopping = self._exit
    deadline = time.monotonic() + (STOP_CALL_TIMEOUT if stopping else CALL_TIMEOUT)
    # a stop() abandons a call that is still waiting, and the tick keeps running while bluetoothd does not answer
    while (remaining := deadline - time.monotonic()) > 0 and self._exit == stopping:
      try:
        reply = self._conn.receive(timeout=min(remaining, RECONCILE_PERIOD))
      except TimeoutError:
        self._tick()
        continue
      if reply.header.fields.get(HeaderFields.reply_serial) == serial:
        return reply.body if reply.header.message_type == MessageType.method_return else None
      self._dispatch(reply)
    return None

  def _reconcile(self):
    if not self._enabled:
      self._teardown()
      self._set_connected(frozenset())
      if self._params.get_bool("BluetoothEnabled"):
        self._params.put_bool("BluetoothEnabled", False)
      return

    reply = self._call(new_method_call(DBusAddress("/", BLUEZ, OBJECT_MANAGER_IFACE), "GetManagedObjects"))
    if reply is None:
      # no answer says nothing about the adapter: forgetting it here would make the teardown skip the power-off
      return
    objects = reply[0]
    self._set_connected(frozenset(path for path, ifaces in objects.items() if _prop(ifaces, DEVICE_IFACE, "Connected")))
    adapter = next((path for path, ifaces in objects.items() if GATT_MANAGER_IFACE in ifaces and ADVERTISING_MANAGER_IFACE in ifaces), None)

    if self._connected and self._has_active_session is not None and not self._has_active_session():
      now = time.monotonic()
      if self._stale_connected_since is None:
        self._stale_connected_since = now
      elif now - self._stale_connected_since >= 15.0:
        cloudlog.warning(f"bluetooth: disconnecting stale idle devices {sorted(self._connected)}")
        for path in self._connected:
          self._call(new_method_call(DBusAddress(path, BLUEZ, DEVICE_IFACE), "Disconnect"))
        self._stale_connected_since = None
        self._set_connected(frozenset())
    else:
      self._stale_connected_since = None

    if self._ready and adapter == self._adapter:
      ifaces = objects[adapter]
      # a restarted bluetoothd keeps the adapter powered but has no advertisement;
      # while a phone is connected, single-role controllers may pause advertising without losing the app.
      if (_prop(ifaces, ADAPTER_IFACE, "Powered") and not _prop(ifaces, ADAPTER_IFACE, "Pairable", True) and
          (self._connected or _prop(ifaces, ADVERTISING_MANAGER_IFACE, "ActiveInstances", 0) >= 1)):
        return
      cloudlog.warning(f"bluetooth: lost {adapter}, setting up again")

    self._ready = False
    self._adapter = adapter
    if adapter is not None:
      self._setup(adapter, objects)

  def _setup(self, adapter: str, objects: dict):
    self._unregister(adapter)
    for path, ifaces in objects.items():
      if _prop(ifaces, DEVICE_IFACE, "Connected"):
        cloudlog.warning(f"bluetooth: disconnecting leftover {path} before setup")
        self._call(new_method_call(DBusAddress(path, BLUEZ, DEVICE_IFACE), "Disconnect"))
    adapter_address = DBusAddress(adapter, BLUEZ, ADAPTER_IFACE)
    props = Properties(adapter_address)
    paired = [path for path, ifaces in objects.items() if _prop(ifaces, DEVICE_IFACE, "Paired")]
    steps = (
      # never advertise while bondable: phones authenticate in the app layer
      ("Pairable", props.set("Pairable", "b", False)),
      ("Alias", props.set("Alias", "s", ALIAS)),
      ("Powered", props.set("Powered", "b", True)),
      # BlueZ refuses RemoveDevice on an unpowered adapter
      *(("RemoveDevice", new_method_call(adapter_address, "RemoveDevice", "o", (path,))) for path in paired),
      # on the adapter, not the advertisement: this kernel always writes its own Flags field and would send a second one
      ("DiscoverableTimeout", props.set("DiscoverableTimeout", "u", 0)),
      ("Discoverable", props.set("Discoverable", "b", True)),
      ("RegisterApplication", new_method_call(DBusAddress(adapter, BLUEZ, GATT_MANAGER_IFACE), "RegisterApplication", "oa{sv}", (APP_PATH, {}))),
      ("RegisterAdvertisement", new_method_call(DBusAddress(adapter, BLUEZ, ADVERTISING_MANAGER_IFACE), "RegisterAdvertisement", "oa{sv}",
                                                (ADVERTISEMENT_PATH, {}))),
    )
    for step, msg in steps:
      failed = not self._exit and self._call(msg) is None
      if self._exit:
        return
      if failed:
        if step != self._failed_step:
          cloudlog.warning(f"bluetooth: {step} failed on {adapter}")
        self._failed_step = step
        self._unregister(adapter)
        return

    self._failed_step = None
    self._ready = True
    cloudlog.info(f"bluetooth: advertising on {adapter}")

  def _unregister(self, adapter: str):
    self._ready = False
    self._call(new_method_call(DBusAddress(adapter, BLUEZ, ADVERTISING_MANAGER_IFACE), "UnregisterAdvertisement", "o", (ADVERTISEMENT_PATH,)))
    self._call(new_method_call(DBusAddress(adapter, BLUEZ, GATT_MANAGER_IFACE), "UnregisterApplication", "o", (APP_PATH,)))

  def _teardown(self):
    adapter, self._adapter = self._adapter, None
    if adapter is None:
      return
    self._unregister(adapter)
    props = Properties(DBusAddress(adapter, BLUEZ, ADAPTER_IFACE))
    # BlueZ stores Discoverable and applies it again to every new adapter
    self._call(props.set("Discoverable", "b", False))
    self._call(props.set("Powered", "b", False))

  def _dispatch(self, msg: Message):
    if msg.header.message_type != MessageType.method_call:
      return

    fields = msg.header.fields
    target = (fields.get(HeaderFields.path), fields.get(HeaderFields.interface), fields.get(HeaderFields.member))

    if target == (APP_PATH, OBJECT_MANAGER_IFACE, "GetManagedObjects"):
      reply = new_method_return(msg, "a{oa{sa{sv}}}", (GATT_OBJECTS,))
    elif target[1:] == (PROPERTIES_IFACE, "GetAll") and msg.body and msg.body[0] in OBJECTS.get(target[0], {}):
      reply = new_method_return(msg, "a{sv}", (OBJECTS[target[0]][msg.body[0]],))
    elif target == (RX_PATH, GATT_CHARACTERISTIC_IFACE, "WriteValue"):
      value, options = msg.body
      device, mtu = options["device"][1], options["mtu"][1]
      self._connected |= {device}
      # BlueZ has already acked the write and discards this reply, so the only refusal is a disconnect.
      # A long write arrives joined at offset 0, so the length is checked as well.
      if options.get("offset", ("q", 0))[1] != 0 or len(value) > mtu - 3:
        cloudlog.warning(f"bluetooth: bad WriteValue offset={options.get('offset')} len={len(value)} mtu={mtu} from {device}")
        self.disconnect(device)
      else:
        self._callback(self._on_write, device, bytes(value), mtu)
      reply = new_method_return(msg)
    elif target in ((TX_PATH, GATT_CHARACTERISTIC_IFACE, "StartNotify"), (TX_PATH, GATT_CHARACTERISTIC_IFACE, "StopNotify")):
      reply = new_method_return(msg)
    elif target == (ADVERTISEMENT_PATH, ADVERTISEMENT_IFACE, "Release"):
      self._ready = False
      reply = new_method_return(msg)
    else:
      reply = new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod")

    if not msg.header.flags & MessageFlag.no_reply_expected:
      self._conn.send(reply)


class Daemon:
  def __init__(self, params, window: ConnectPhoneWindow):
    self._params = params
    self._window = window
    self._engine = Engine(params, window)
    self.bt = self.new_manager()
    self._refused: dict | None = None  # shown in place of the window state until the next request
    self._written: dict | None = None
    self._status: dict | None = None
    self._retry_at: float | None = None

  def new_manager(self) -> BluetoothManager:
    self.bt = BluetoothManager(
      self.on_write,
      self._engine.on_disconnect,
      self.tick,
      stream_fds=self._engine.stream_selector_entries,
      on_stream_ready=self.on_stream_ready,
      has_active_session=lambda: self._engine.connected() > 0,
    )
    return self.bt

  def on_stream_ready(self, fd: int, readable: bool, writable: bool):
    self._act(self._engine.on_stream_ready(fd, readable, writable))

  def on_write(self, device: str, value: bytes, mtu: int):
    self._act(self._engine.on_write(device, value, mtu, time.monotonic()))

  def _act(self, actions: list):
    for kind, data in actions:
      if kind == "notify":
        self.bt.notify(data)
      else:
        self.bt.disconnect(data)

  def tick(self):
    try:
      self.step(time.monotonic())
    except Exception:
      cloudlog.exception("bluetooth: tick failed")

  def step(self, now: float):
    params, bt, window = self._params, self.bt, self._window
    allowed = params.get_bool("BluetoothAllowed")

    request = params.get(REQUEST_KEY)
    if request is not None:
      params.remove(REQUEST_KEY)
    if isinstance(request, dict):
      self._refused = None
      seq, action = request.get("seq", 0), request.get("action")
      if action == "cancel":
        window.cancel()
      elif action == "open" and not allowed:
        self._refused = {"seq": seq, "state": "closed", "reason": "bluetooth_off"}
      elif action == "open":
        try:
          window.open(now, seq)
        except Exception as e:
          cloudlog.exception("bluetooth: connect phone window not opened")
          self._refused = {"seq": seq, "state": "closed", "reason": "no_key" if isinstance(e, RuntimeError) else "error"}
      elif action in ("allow", "deny") and allowed:
        self._act(self._engine.answer(action == "allow", now))
      elif action == "remove" and allowed:
        self._act(self._engine.remove(request.get("phone")))

    if not allowed:
      window.cancel("bluetooth_off")
    window.tick(now, bt.ready)
    self._act(self._engine.tick(now))

    phones = grant_count()
    enabled = allowed and (window.active or phones >= 1)
    bt.set_enabled(enabled)
    if not enabled or bt.ready:
      self._retry_at = None
    elif self._retry_at is None:
      self._retry_at = now + ENABLE_RETRY_AFTER
    elif now >= self._retry_at:
      self._retry_at = float("inf")
      cloudlog.warning("bluetooth: no adapter, writing BluetoothEnabled again")
      params.put_bool("BluetoothEnabled", True)

    state = self._refused or (window.state() | {"prompt": self._engine.prompt(now)})
    if state != self._written:
      params.put(WINDOW_KEY, state)
      self._written = state

    status = {"enabled": enabled, "connected": self._engine.connected(), "phones": phones}
    if status != self._status:
      params.put(STATUS_KEY, status)
      self._status = status


def main():
  # selfdrived blocks engagement while an always-run process is dead, and the manager never starts it again:
  # only a signal ends this loop
  exiting = threading.Event()
  daemon = Daemon(Params(), ConnectPhoneWindow())

  def on_signal(*_):
    exiting.set()
    daemon.bt.stop()

  for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, on_signal)

  backoff = RESTART_BACKOFF
  while True:
    started = time.monotonic()
    try:
      daemon.bt.run()
    except Exception:
      cloudlog.exception("bluetooth: manager failed")
    if time.monotonic() - started >= RESTART_BACKOFF_MAX:
      backoff = RESTART_BACKOFF
    retry_at = time.monotonic() + backoff
    backoff = min(backoff * 2, RESTART_BACKOFF_MAX)
    while not exiting.is_set() and time.monotonic() < retry_at:
      exiting.wait(RECONCILE_PERIOD)
      daemon.tick()
    if exiting.is_set():
      return
    daemon.new_manager()


if __name__ == "__main__":
  main()

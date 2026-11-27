"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import errno
import select
import selectors
import socket
from collections import deque
from dataclasses import dataclass, field

STREAM_OPEN = 0x01
STREAM_OPEN_OK = 0x02
STREAM_DATA = 0x03
STREAM_WINDOW = 0x04
STREAM_CLOSE = 0x05
STREAM_ERROR = 0x06

ERR_REFUSED = 1
ERR_UNSUPPORTED_PORT = 2
ERR_LIMIT = 3
ERR_PROTOCOL = 4

INITIAL_WINDOW = 8_192
WINDOW_UPDATE_THRESHOLD = 2_048
MAX_DATA_CHUNK = 1_024
MAX_STREAMS_PER_DEVICE = 8
OPEN_TIMEOUT = 5.0
ALLOWED_PORTS = (22,)


@dataclass(eq=False)
class _TcpStream:
  device: str
  stream_id: int
  sock: socket.socket
  opened_at: float
  peer_window: int
  local_window: int = INITIAL_WINDOW
  consumed_since_ack: int = 0
  connecting: bool = True
  eof_from_phone: bool = False
  tx_queue: deque[bytes] = field(default_factory=deque)

  @property
  def fd(self) -> int:
    return self.sock.fileno()

  @property
  def want_write(self) -> bool:
    return self.connecting or bool(self.tx_queue)


class Streams:
  def __init__(self, target_host: str = "127.0.0.1"):
    self._target_host = target_host
    self._streams: dict[tuple[str, int], _TcpStream] = {}
    self._by_fd: dict[int, _TcpStream] = {}

  def has_streams(self) -> bool:
    return bool(self._streams)

  def selector_entries(self) -> list[tuple[int, int]]:
    entries: list[tuple[int, int]] = []
    for st in self._streams.values():
      events = selectors.EVENT_READ
      if st.want_write:
        events |= selectors.EVENT_WRITE
      entries.append((st.fd, events))
    return entries

  def handle(self, device: str, body: bytes, now: float) -> list[tuple[str, bytes]]:
    if len(body) < 3:
      return []
    stream_id = int.from_bytes(body[0:2], "big")
    kind = body[2]
    payload = body[3:]
    if stream_id == 0:
      return []

    key = (device, stream_id)
    if kind == STREAM_OPEN:
      return self._open(device, stream_id, payload, now)

    st = self._streams.get(key)
    if st is None:
      return []

    if kind == STREAM_DATA:
      if not payload or st.eof_from_phone:
        return []
      if len(payload) > st.local_window:
        self._close_stream(st)
        return [(device, _err(stream_id, ERR_PROTOCOL, "window exceeded"))]
      st.local_window -= len(payload)
      st.tx_queue.append(payload)
      return self._flush_tx(st)

    if kind == STREAM_WINDOW:
      if len(payload) != 4:
        return []
      credit = int.from_bytes(payload, "big")
      st.peer_window += credit
      return self._drain_rx(st)

    if kind == STREAM_CLOSE:
      st.eof_from_phone = True
      if not st.tx_queue and not st.connecting:
        self._close_stream(st)
      return []

    return []

  def on_socket_ready(self, fd: int, readable: bool, writable: bool) -> list[tuple[str, bytes]]:
    st = self._by_fd.get(fd)
    if st is None:
      return []
    out: list[tuple[str, bytes]] = []
    if st.connecting and writable:
      err = st.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
      if err != 0:
        device, sid = st.device, st.stream_id
        self._close_stream(st)
        return [(device, _err(sid, ERR_REFUSED, f"connect failed ({err})"))]
      st.connecting = False
      out.append((st.device, _open_ok(st.stream_id, st.local_window)))
      if st.tx_queue:
        out += self._flush_tx(st)
      elif st.eof_from_phone:
        self._close_stream(st)
        return out

    if (st.device, st.stream_id) not in self._streams:
      return out

    if writable and st.tx_queue:
      out += self._flush_tx(st)

    if (st.device, st.stream_id) not in self._streams:
      return out

    if readable and not st.connecting:
      out += self._drain_rx(st)
    return out

  def tick(self, now: float) -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    for st in list(self._streams.values()):
      if st.connecting and now - st.opened_at >= OPEN_TIMEOUT:
        device, sid = st.device, st.stream_id
        self._close_stream(st)
        out.append((device, _err(sid, ERR_REFUSED, "connect timed out")))
    return out

  def close_device(self, device: str):
    for st in [s for s in self._streams.values() if s.device == device]:
      self._close_stream(st)

  def _open(self, device: str, stream_id: int, payload: bytes, now: float) -> list[tuple[str, bytes]]:
    if len(payload) != 6:
      return [(device, _err(stream_id, ERR_PROTOCOL, "bad open"))]
    port = int.from_bytes(payload[0:2], "big")
    peer_window = int.from_bytes(payload[2:6], "big")
    if port not in ALLOWED_PORTS:
      return [(device, _err(stream_id, ERR_UNSUPPORTED_PORT, f"port {port} not allowed"))]
    if (device, stream_id) in self._streams:
      return [(device, _err(stream_id, ERR_PROTOCOL, "duplicate stream id"))]
    if sum(1 for d, _ in self._streams if d == device) >= MAX_STREAMS_PER_DEVICE:
      return [(device, _err(stream_id, ERR_LIMIT, "too many open streams"))]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
      err = sock.connect_ex((self._target_host, port))
    except OSError as e:
      sock.close()
      return [(device, _err(stream_id, ERR_REFUSED, str(e)))]
    if err not in (0, errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK):
      sock.close()
      return [(device, _err(stream_id, ERR_REFUSED, f"connect failed ({err})"))]

    if err != 0:
      _, writable, _ = select.select([], [sock], [], 0.05)
      if writable:
        so_err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if so_err != 0:
          sock.close()
          return [(device, _err(stream_id, ERR_REFUSED, f"connect failed ({so_err})"))]
        err = 0

    st = _TcpStream(
      device=device,
      stream_id=stream_id,
      sock=sock,
      opened_at=now,
      peer_window=peer_window,
      connecting=(err != 0),
    )
    self._streams[(device, stream_id)] = st
    self._by_fd[st.fd] = st
    if not st.connecting:
      return [(device, _open_ok(stream_id, st.local_window))]
    return []

  def _flush_tx(self, st: _TcpStream) -> list[tuple[str, bytes]]:
    if st.connecting:
      return []
    written_total = 0
    while st.tx_queue:
      chunk = st.tx_queue[0]
      try:
        sent = st.sock.send(chunk)
      except BlockingIOError:
        break
      except OSError:
        device, sid = st.device, st.stream_id
        self._close_stream(st)
        return [(device, _close(sid, 1))]
      if sent == 0:
        break
      written_total += sent
      if sent < len(chunk):
        st.tx_queue[0] = chunk[sent:]
        break
      st.tx_queue.popleft()

    out: list[tuple[str, bytes]] = []
    if written_total > 0:
      st.consumed_since_ack += written_total
      st.local_window += written_total
      if st.consumed_since_ack >= WINDOW_UPDATE_THRESHOLD:
        ack = st.consumed_since_ack
        st.consumed_since_ack = 0
        out.append((st.device, _window(st.stream_id, ack)))

    if st.eof_from_phone and not st.tx_queue:
      self._close_stream(st)
    return out

  def _drain_rx(self, st: _TcpStream) -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    while st.peer_window > 0:
      to_read = min(MAX_DATA_CHUNK, st.peer_window)
      try:
        data = st.sock.recv(to_read)
      except BlockingIOError:
        break
      except OSError:
        device, sid = st.device, st.stream_id
        self._close_stream(st)
        out.append((device, _close(sid, 1)))
        return out
      if not data:
        device, sid = st.device, st.stream_id
        self._close_stream(st)
        out.append((device, _close(sid, 0)))
        return out
      st.peer_window -= len(data)
      out.append((st.device, _data(st.stream_id, data)))
    return out

  def _close_stream(self, st: _TcpStream):
    self._streams.pop((st.device, st.stream_id), None)
    self._by_fd.pop(st.fd, None)
    try:
      st.sock.close()
    except OSError:
      pass


def _open_ok(stream_id: int, window: int) -> bytes:
  return stream_id.to_bytes(2, "big") + bytes([STREAM_OPEN_OK]) + window.to_bytes(4, "big")


def _data(stream_id: int, payload: bytes) -> bytes:
  return stream_id.to_bytes(2, "big") + bytes([STREAM_DATA]) + payload


def _window(stream_id: int, credit: int) -> bytes:
  return stream_id.to_bytes(2, "big") + bytes([STREAM_WINDOW]) + credit.to_bytes(4, "big")


def _close(stream_id: int, reason: int) -> bytes:
  return stream_id.to_bytes(2, "big") + bytes([STREAM_CLOSE, reason & 0xFF])


def _err(stream_id: int, code: int, message: str) -> bytes:
  return stream_id.to_bytes(2, "big") + bytes([STREAM_ERROR, code & 0xFF]) + message.encode()

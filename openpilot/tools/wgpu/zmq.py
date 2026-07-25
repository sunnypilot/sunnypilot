import time

import zmq

import openpilot.cereal.messaging as messaging


WGPU_CAR_PARAMS = "wgpuCarParams"


def service_port(endpoint: str) -> int:
  # Keep this in sync with cereal/messaging/bridge_zmq.cc.
  value = 0xcbf29ce484222325
  for char in endpoint.encode():
    value ^= char
    value = (value * 0x100000001b3) & 0xffffffffffffffff
  return 8023 + (value % (65535 - 8023))


class ZmqSubSocket:
  def __init__(self, endpoint: str, address: str, conflate: bool = False):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.SUB)
    self.socket.setsockopt(zmq.SUBSCRIBE, b"")
    self.socket.setsockopt(zmq.RECONNECT_IVL_MAX, 500)
    if conflate:
      self.socket.setsockopt(zmq.CONFLATE, 1)
    self.socket.connect(f"tcp://{address}:{service_port(endpoint)}")

  def receive(self, non_blocking: bool = False) -> bytes | None:
    try:
      return self.socket.recv(flags=zmq.NOBLOCK if non_blocking else 0)
    except zmq.Again:
      return None

  def drain(self, wait_for_one: bool = False) -> list[bytes]:
    messages = []
    if wait_for_one:
      message = self.receive()
      if message is not None:
        messages.append(message)
    while (message := self.receive(non_blocking=True)) is not None:
      messages.append(message)
    return messages


class ZmqSubMaster:
  def __init__(self, services: list[str], address: str):
    self.services = services
    self.sockets = {service: ZmqSubSocket(service, address, conflate=True) for service in services}
    self.poller = zmq.Poller()
    self.socket_to_service = {}
    for service, sub in self.sockets.items():
      self.poller.register(sub.socket, zmq.POLLIN)
      self.socket_to_service[sub.socket] = service

    self.data = {service: getattr(messaging.new_message(service).as_reader(), service) for service in services}
    self.seen = dict.fromkeys(services, False)
    self.updated = dict.fromkeys(services, False)
    self.recv_frame = dict.fromkeys(services, 0)
    self.frame = -1

  def __getitem__(self, service: str):
    return self.data[service]

  def update(self, timeout: int = 100) -> None:
    self.frame += 1
    self.updated = dict.fromkeys(self.services, False)
    for socket, _ in self.poller.poll(timeout):
      service = self.socket_to_service[socket]
      raw = self.sockets[service].receive(non_blocking=True)
      if raw is None:
        continue
      event = messaging.log_from_bytes(raw)
      self.data[service] = getattr(event, service)
      self.seen[service] = True
      self.updated[service] = True
      self.recv_frame[service] = self.frame


class ZmqPubMaster:
  def __init__(self, services: list[str]):
    context = zmq.Context.instance()
    self.sockets = {}
    for service in services:
      socket = context.socket(zmq.PUB)
      socket.bind(f"tcp://*:{service_port(service)}")
      self.sockets[service] = socket
    # Give already-running bridge subscribers time to finish their handshake.
    time.sleep(0.1)

  def send(self, service: str, message) -> None:
    self.sockets[service].send(message.to_bytes(), flags=zmq.NOBLOCK)

  def send_raw(self, service: str, data: bytes) -> None:
    self.sockets[service].send(data, flags=zmq.NOBLOCK)

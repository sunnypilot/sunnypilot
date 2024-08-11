#!/usr/bin/env python3
#TODO: Add this to files_common to allow release to public

from __future__ import annotations

import base64
import gzip
import json
import os
import threading
import time

from openpilot.selfdrive.athena.athenad import ws_send, jsonrpc_handler, \
  recv_queue, RECONNECT_TIMEOUT_S, UploadQueueCache, upload_queue, cur_upload_items, backoff, ws_manage
from jsonrpc import dispatcher
from websocket import (ABNF, WebSocket, WebSocketException, WebSocketTimeoutException,
                       create_connection)

from openpilot.common.api import SunnylinkApi
from openpilot.common.params import Params
from openpilot.common.realtime import set_core_affinity
from openpilot.common.swaglog import cloudlog

SUNNYLINK_ATHENA_HOST = os.getenv('SUNNYLINK_ATHENA_HOST', 'wss://ws.stg.api.sunnypilot.ai')
HANDLER_THREADS = int(os.getenv('HANDLER_THREADS', "4"))
LOCAL_PORT_WHITELIST = {8022}

params = Params()
sunnylink_api = SunnylinkApi(params.get("SunnylinkDongleId", encoding='utf-8'))
def handle_long_poll(ws: WebSocket, exit_event: threading.Event | None) -> None:
  end_event = threading.Event()

  threads = [
    threading.Thread(target=ws_manage, args=(ws, end_event), name='ws_manage'),
    threading.Thread(target=ws_recv, args=(ws, end_event), name='ws_recv'),
    threading.Thread(target=ws_send, args=(ws, end_event), name='ws_send'),
    threading.Thread(target=ws_ping, args=(ws, end_event), name='ws_ping'),
    threading.Thread(target=ws_queue, args=(end_event,), name='ws_queue'),
    # threading.Thread(target=upload_handler, args=(end_event,), name='upload_handler'),
    # threading.Thread(target=log_handler, args=(end_event,), name='log_handler'),
    # threading.Thread(target=stat_handler, args=(end_event,), name='stat_handler'),
  ] + [
    threading.Thread(target=jsonrpc_handler, args=(end_event,), name=f'worker_{x}')
    for x in range(HANDLER_THREADS)
  ]

  for thread in threads:
    thread.start()
  try:
    while not end_event.wait(0.1):
      if exit_event is not None and exit_event.is_set():
        end_event.set()
  except (KeyboardInterrupt, SystemExit):
    end_event.set()
    raise
  finally:
    for thread in threads:
      cloudlog.debug(f"athena.joining {thread.name}")
      thread.join()


def ws_recv(ws: WebSocket, end_event: threading.Event) -> None:
  last_ping = int(time.monotonic() * 1e9)
  while not end_event.is_set():
    try:
      opcode, data = ws.recv_data(control_frame=True)
      if opcode in (ABNF.OPCODE_TEXT, ABNF.OPCODE_BINARY):
        if opcode == ABNF.OPCODE_TEXT:
          data = data.decode("utf-8")
        recv_queue.put_nowait(data)
        cloudlog.debug(f"sunnylinkd.ws_recv.recv {data}")
      elif opcode in (ABNF.OPCODE_PING, ABNF.OPCODE_PONG):
        cloudlog.debug(f"sunnylinkd.ws_recv.pong {opcode}")
        last_ping = int(time.monotonic() * 1e9)
        Params().put("LastSunnylinkPingTime", str(last_ping))
    except WebSocketTimeoutException:
      ns_since_last_ping = int(time.monotonic() * 1e9) - last_ping
      if ns_since_last_ping > RECONNECT_TIMEOUT_S * 1e9:
        cloudlog.exception("sunnylinkd.ws_recv.timeout")
        end_event.set()
    except Exception:
      cloudlog.exception("sunnylinkd.ws_recv.exception")
      end_event.set()


def ws_ping(ws: WebSocket, end_event: threading.Event) -> None:
  # last_ping = int(time.monotonic() * 1e9)
  while not end_event.is_set():
    try:
      ws.ping()
      cloudlog.debug(f"sunnylinkd.ws_recv.ws_ping: Pinging")
    except Exception:
      cloudlog.exception("sunnylinkd.ws_ping.exception")
      end_event.set()
    time.sleep(RECONNECT_TIMEOUT_S * 0.8)  # Sleep about 80% before a timeout

def ws_queue(end_event: threading.Event) -> None:
  resume_requested = False
  tries = 0

  while not end_event.is_set() and not resume_requested:
    try:
      if not resume_requested:
        cloudlog.debug(f"sunnylinkd.ws_queue.resume_queued")
        sunnylink_api.resume_queued(timeout=29)
        resume_requested = True
        tries = 0
    except Exception:
      cloudlog.exception("sunnylinkd.ws_queue.resume_queued.exception")
      resume_requested = False
      tries += 1
      time.sleep(backoff(tries))  # Wait for the backoff time before the next attempt
  cloudlog.debug("Resume requested or end_event is set, exiting ws_queue thread")


@dispatcher.add_method
def getParamsAllKeys() -> list[str]:
  keys: list[str] = [k.decode('utf-8') for k in Params().all_keys()]
  return keys


@dispatcher.add_method
def getParams(params_keys: list[str], compression: bool = False) -> str | dict[str, str]:
  try:
    params = Params()
    params_dict: dict[str, bytes] = {key: params.get(key) or b'' for key in params_keys}

    # Compress the values before encoding to base64 as output from params.get is bytes and same for compression
    if compression:
      params_dict = {key: gzip.compress(value) for key, value in params_dict.items()}

    # Last step is to encode the values to base64 and decode to utf-8 for JSON serialization
    return {key: base64.b64encode(value).decode('utf-8') for key, value in params_dict.items()}

  except Exception as e:
    return cloudlog.exception("sunnylinkd.getParams.exception", e)

@dispatcher.add_method
def saveParams(params_to_update: dict[str, str], compression: bool = False) -> None:
  params = Params()
  try:
    params_dict = {key: base64.b64decode(value) for key, value in params_to_update.items()}

    if compression:
      params_dict = {key: gzip.decompress(value) for key, value in params_dict.items()}

    for key, value in params_dict.items():
      params.put(key, value)
  except Exception as e:
    return cloudlog.exception("sunnylinkd.saveParams.exception", e)


def main(exit_event: threading.Event = None):
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("failed to set core affinity")

  UploadQueueCache.initialize(upload_queue)

  ws_uri = SUNNYLINK_ATHENA_HOST
  conn_start = None
  conn_retries = 0
  while exit_event is None or not exit_event.is_set():
    try:
      if conn_start is None:
        conn_start = time.monotonic()

      cloudlog.event("sunnylinkd.main.connecting_ws", ws_uri=ws_uri, retries=conn_retries)
      ws = create_connection(ws_uri,
                             cookie="jwt=" + sunnylink_api.get_token(),
                             enable_multithread=True,
                             timeout=30.0)
      cloudlog.event("sunnylinkd.main.connected_ws", ws_uri=ws_uri, retries=conn_retries,
                     duration=time.monotonic() - conn_start)
      conn_start = None

      conn_retries = 0
      cur_upload_items.clear()

      handle_long_poll(ws, exit_event)
    except (KeyboardInterrupt, SystemExit):
      break
    except (ConnectionError, TimeoutError, WebSocketException):
      conn_retries += 1
      params.remove("LastSunnylinkPingTime")
    except Exception:
      cloudlog.exception("sunnylinkd.main.exception")

      conn_retries += 1
      params.remove("LastSunnylinkPingTime")

    time.sleep(backoff(conn_retries))


if __name__ == "__main__":
  main()

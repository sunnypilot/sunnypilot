#!/usr/bin/env python3
import math
import os
import tempfile
from dataclasses import dataclass

from opendbc.can.parser import CANParser


RADAR_500_51F_DBC_TEMPLATE = """
BO_ {addr_dec} RADAR_TRACK_{addr_hex}: 8 RADAR
 SG_ UNKNOWN_1 : 7|8@0- (1,0) [-128|127] "" XXX
 SG_ AZIMUTH : 12|10@0- (0.2,0) [-102.4|102.2] "" XXX
 SG_ STATE : 15|3@0+ (1,0) [0|7] "" XXX
 SG_ LONG_DIST : 18|11@0+ (0.1,0) [0|204.7] "" XXX
 SG_ REL_ACCEL : 33|10@0- (0.02,0) [-10.24|10.22] "" XXX
 SG_ ZEROS : 37|4@0+ (1,0) [0|255] "" XXX
 SG_ COUNTER : 38|1@0+ (1,0) [0|1] "" XXX
 SG_ STATE_3 : 39|1@0+ (1,0) [0|1] "" XXX
 SG_ REL_SPEED : 53|14@0- (0.01,0) [-81.92|81.92] "" XXX
 SG_ STATE_2 : 55|2@0+ (1,0) [0|3] "" XXX
"""

RADAR_3A5_3C4_DBC_TEMPLATE = """
BO_ {addr_dec} RADAR_TRACK_{addr_hex}: 24 RADAR
 SG_ CHECKSUM : 0|16@1+ (1,0) [0|65535] "" XXX
 SG_ COUNTER : 16|8@1+ (1,0) [0|255] "" XXX
 SG_ NEW_SIGNAL_1 : 25|2@0+ (1,0) [0|3] "" XXX
 SG_ NEW_SIGNAL_3 : 28|2@0+ (1,0) [0|3] "" XXX
 SG_ COUNTER_3 : 31|2@0+ (1,0) [0|3] "" XXX
 SG_ NEW_SIGNAL_2 : 38|7@0- (1,0) [0|127] "" XXX
 SG_ COUNTER_256 : 47|8@0+ (1,0) [0|255] "" XXX
 SG_ NEW_SIGNAL_6 : 51|4@0+ (1,0) [0|15] "" XXX
 SG_ STATE : 54|3@0+ (1,0) [0|7] "" XXX
 SG_ NEW_SIGNAL_8 : 62|7@0- (1,0) [0|127] "" XXX
 SG_ LONG_DIST : 63|12@1+ (0.05,0) [0|8191] "m" XXX
 SG_ LAT_DIST : 76|12@1- (0.05,0) [0|127] "" XXX
 SG_ REL_SPEED : 88|14@1- (0.01,0) [0|16383] "" XXX
 SG_ NEW_SIGNAL_4 : 103|2@0+ (1,0) [0|3] "" XXX
 SG_ LAT_DIST_ACCEL : 104|13@1- (1,0) [0|8191] "" XXX
 SG_ REL_ACCEL : 118|10@1- (0.02,0) [0|1023] "" XXX
 SG_ NEW_SIGNAL_5 : 133|4@0+ (1,0) [0|15] "" XXX
"""

RADAR_210_21F_DBC_TEMPLATE = """
BO_ {addr_dec} RADAR_TRACK_{addr_hex}: 32 RADAR
 SG_ CHECKSUM : 0|16@1+ (1,0) [0|65535] "" XXX
 SG_ COUNTER : 16|8@1+ (1,0) [0|255] "" XXX
 SG_ 1_COUNTER_255 : 47|8@0+ (1,0) [0|255] "" XXX
 SG_ 1_STATE_ALT : 51|4@0+ (1,0) [0|15] "" XXX
 SG_ 1_STATE : 55|4@0+ (1,0) [0|15] "" XXX
 SG_ 1_NEW_SIGNAL_3 : 63|8@0- (1,0) [0|255] "" XXX
 SG_ 1_LONG_DIST : 64|12@1+ (0.05,0) [0|4095] "" XXX
 SG_ 1_LAT_DIST : 76|12@1- (0.05,0) [0|4095] "" XXX
 SG_ 1_REL_SPEED : 88|14@1- (0.01,0) [0|16383] "" XXX
 SG_ 1_NEW_SIGNAL_1 : 102|2@1+ (1,0) [0|3] "" XXX
 SG_ 1_LAT_ACCEL : 104|13@1- (1,0) [0|8191] "" XXX
 SG_ 1_REL_ACCEL : 118|10@1- (1,0) [0|1023] "" XXX
 SG_ 2_COUNTER_255 : 175|8@0+ (1,0) [0|255] "" XXX
 SG_ 2_STATE_ALT : 179|4@0+ (1,0) [0|15] "" XXX
 SG_ 2_STATE : 183|4@0+ (1,0) [0|15] "" XXX
 SG_ 2_NEW_SIGNAL_3 : 191|8@0- (1,0) [0|255] "" XXX
 SG_ 2_LONG_DIST : 192|12@1+ (0.05,0) [0|4095] "" XXX
 SG_ 2_LAT_DIST : 204|12@1- (0.05,0) [0|4095] "" XXX
 SG_ 2_REL_SPEED : 216|14@1- (0.01,0) [0|65535] "" XXX
 SG_ 2_NEW_SIGNAL_1 : 230|2@1+ (1,0) [0|3] "" XXX
 SG_ 2_LAT_ACCEL : 232|13@1- (1,0) [0|8191] "" XXX
 SG_ 2_REL_ACCEL : 246|10@1- (1,0) [0|1023] "" XXX
"""

RADAR_602_611_DBC_TEMPLATE = """
BO_ {addr_dec} RADAR_TRACK_{addr_hex}: 8 RADAR
 SG_ 1_DISTANCE : 0|10@1+ (0.25,0) [0|255.75] "" XXX
 SG_ 1_LATERAL : 10|11@1+ (0.03,-30.705) [-30.705|30.705] "" XXX
 SG_ 1_SPEED : 21|10@1+ (0.25,-128) [-128|127.75] "" XXX
 SG_ 2_DISTANCE : 31|10@1+ (0.25,0) [0|255.75] "" XXX
 SG_ 2_LATERAL : 41|11@1+ (0.03,-30.705) [-30.705|30.705] "" XXX
 SG_ 2_SPEED : 52|10@1+ (0.25,-128) [-128|127.75] "" XXX
 SG_ COUNTER : 62|2@1+ (1,0) [0|3] "" XXX
"""


@dataclass(frozen=True)
class RadarSpec:
  name: str
  start_addr: int
  msg_count: int
  dbc_template: str
  track_prefixes: tuple[str, ...]

  @property
  def end_addr(self) -> int:
    return self.start_addr + self.msg_count - 1

  def contains(self, address: int) -> bool:
    return self.start_addr <= address <= self.end_addr


RADAR_SPECS = (
  RadarSpec("RADAR_500_51F", 0x500, 32, RADAR_500_51F_DBC_TEMPLATE, ("",)),
  RadarSpec("RADAR_210_21F", 0x210, 16, RADAR_210_21F_DBC_TEMPLATE, ("1_", "2_")),
  RadarSpec("RADAR_3A5_3C4", 0x3A5, 32, RADAR_3A5_3C4_DBC_TEMPLATE, ("",)),
  RadarSpec("RADAR_602_611", 0x602, 16, RADAR_602_611_DBC_TEMPLATE, ("1_", "2_")),
)


def build_seen_address_map() -> dict[str, set[int]]:
  return {radar_spec.name: set() for radar_spec in RADAR_SPECS}


def get_radar_spec(address: int) -> RadarSpec | None:
  for radar_spec in RADAR_SPECS:
    if radar_spec.contains(address):
      return radar_spec
  return None


def is_exclusive_full_range_match(radar_spec: RadarSpec, seen_addresses: dict[str, set[int]]) -> bool:
  expected_addresses = set(range(radar_spec.start_addr, radar_spec.end_addr + 1))
  if seen_addresses[radar_spec.name] != expected_addresses:
    return False

  for other_spec in RADAR_SPECS:
    if other_spec.name == radar_spec.name:
      continue

    other_expected_addresses = set(range(other_spec.start_addr, other_spec.end_addr + 1))
    if seen_addresses[other_spec.name] == other_expected_addresses:
      return False

  return True


def get_radar_dbc_path(radar_spec: RadarSpec) -> str:
  dbc_path = os.path.join(tempfile.gettempdir(), f"{radar_spec.name.lower()}_radar_ui.dbc")
  dbc_content = "\n".join(
    radar_spec.dbc_template.format(addr_dec=addr, addr_hex=f"{addr:x}")
    for addr in range(radar_spec.start_addr, radar_spec.end_addr + 1)
  )
  if not os.path.exists(dbc_path) or open(dbc_path).read() != dbc_content:
    with open(dbc_path, "w") as f:
      f.write(dbc_content)
  return dbc_path


def get_radar_can_parser(radar_spec: RadarSpec, bus: int) -> CANParser:
  messages = [(f"RADAR_TRACK_{addr:x}", 50) for addr in range(radar_spec.start_addr, radar_spec.end_addr + 1)]
  return CANParser(get_radar_dbc_path(radar_spec), messages, bus)


def get_track_storage_key(radar_spec: RadarSpec, bus: int, addr: int, track_prefix: str) -> tuple[str, int, int]:
  if radar_spec.name in ("RADAR_500_51F", "RADAR_3A5_3C4"):
    return (radar_spec.name, bus, addr)

  track_index = int(track_prefix[0]) - 1
  return (radar_spec.name, bus, addr * 2 + track_index)


def get_track_ts_nanos(parser: CANParser, msg_name: str, radar_spec: RadarSpec, track_prefix: str) -> int:
  if radar_spec.name == "RADAR_602_611":
    return parser.ts_nanos[msg_name][f"{track_prefix}DISTANCE"]
  if radar_spec.name == "RADAR_210_21F":
    return parser.ts_nanos[msg_name][f"{track_prefix}LONG_DIST"]
  return parser.ts_nanos[msg_name]["LONG_DIST"]


def decode_radar_track(radar_spec: RadarSpec, track_msg, track_prefix: str) -> tuple[float, float, float, float]:
  if radar_spec.name == "RADAR_602_611":
    return (
      track_msg[f"{track_prefix}DISTANCE"],
      track_msg[f"{track_prefix}LATERAL"],
      track_msg[f"{track_prefix}SPEED"],
      float("nan"),
    )

  if radar_spec.name == "RADAR_210_21F":
    return (
      track_msg[f"{track_prefix}LONG_DIST"],
      track_msg[f"{track_prefix}LAT_DIST"],
      track_msg[f"{track_prefix}REL_SPEED"],
      float("nan"),
    )

  if radar_spec.name == "RADAR_500_51F":
    azimuth = math.radians(track_msg["AZIMUTH"])
    long_dist = track_msg["LONG_DIST"]
    return (
      math.cos(azimuth) * long_dist,
      0.5 * -math.sin(azimuth) * long_dist,
      track_msg["REL_SPEED"],
      track_msg["REL_ACCEL"],
    )

  return (
    track_msg["LONG_DIST"],
    track_msg["LAT_DIST"],
    track_msg["REL_SPEED"],
    track_msg["REL_ACCEL"],
  )


def is_radar_track_valid(radar_spec: RadarSpec, track_msg, track_prefix: str) -> bool:
  if radar_spec.name == "RADAR_602_611":
    return track_msg[f"{track_prefix}DISTANCE"] != 255.75

  if radar_spec.name == "RADAR_210_21F":
    return track_msg[f"{track_prefix}STATE"] in (3, 4)

  return track_msg["STATE"] in (3, 4)

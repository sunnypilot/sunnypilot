#!/usr/bin/env python3


def _comment(*parts: str) -> str:
  return " ".join(parts)


RADAR_3A5_3C4_MESSAGE_COMMENT = _comment(
  "Common Hyundai/Kia/Genesis 3A5-3C4 track layout, validated across HDA1/HDA2 and CCNC/non-CCNC routes.",
  "Rich width, length, absolute-speed, orientation, and shape data was populated only on EV9/Ioniq 9 in the tested corpus;",
  "HDA2 alone does not imply support, and the extension attributes belong to the same 32 tracks rather than extra objects.",
  "The HKG CAN-FD checksum uses the CAN address as its data ID.",
  "No dedicated oncoming value or flag was found; bit 29 remained zero even for physics-based oncoming candidates.",
  "Bits 26, 29, 39, 55, 117, 136-137, 143, 171, and 188-191 remained zero and are reserved.",
  "The Sportage HEV 2026 route uses an incompatible overlapping layout and must not be decoded with this DBC.",
)

RADAR_3A5_3C4_SIGNAL_COMMENTS = (
  ("CHECKSUM", "16-bit HKG CAN-FD checksum using the CAN address as the data ID."),
  ("COUNTER", "8-bit transmit-cycle counter. It covers 0-255 and wraps; it is separate from the per-track update counter."),
  ("STATE_ALT", "Compressed STATE mirror: 0=empty, 1=tentative/unresolved, 2=measured, 3=coasted."),
  ("MOTION_STATE", _comment(
    "Ground-frame target-motion class: 0=unknown, 1=stationary, 2=moving.",
    "Related Hyundai radar data defines the unused fourth 2-bit value as stopped, not oncoming;",
    "that bit remained zero throughout the tested 3A5 corpus.",
  )),
  ("TRACK_COUNTER", "Per-track modulo-4 update counter. It normally advances with AGE and may hold between updates."),
  ("TRACK_QUALITY", _comment(
    "Unsigned 7-bit track quality/existence score. Empty and tentative tracks are low, measured tracks are high,",
    "and coasted tracks decline as COAST_AGE increases.",
    "A related Hyundai object layout defines its 7-bit quality level as reliability, validity, or probability evidence;",
    "the raw radar scale is not confirmed to be a percentage.",
  )),
  ("AGE", "Per-track alive age/lifetime count, observed 0-255. It normally increments by one on an update and may hold."),
  ("COAST_AGE", "Prediction age: normally 0 in measured STATE=3, starts at 1 in coasted STATE=4, and increments to 15."),
  ("STATE", _comment(
    "Track lifecycle: 0=empty, 1/2=tentative acquisition, 3=measured, 4=coasted/predicted,",
    "7=unresolved tentative. Values 5 and 6 were not observed.",
  )),
  ("RCS", _comment(
    "Signed radar cross-section/return-strength value. Distance-controlled samples consistently increase from small",
    "to passenger to large targets, and its distribution closely matches the detailed 210-21F field.",
    "The raw unit is not calibrated.",
  )),
  ("LONG_DIST", _comment(
    "Longitudinal distance from the ego radar. The 13th bit continues through 204.8 m rather than being a flag.",
    "STATE=0 may carry endpoint sentinels.",
  )),
  ("LAT_DIST", "Lateral position relative to the ego axis. STATE=0 values are empty-track data, not target positions."),
  ("REL_SPEED", "Longitudinal speed relative to ego; negative means the target is moving longitudinally slower than ego."),
  ("NEW_SIGNAL_4", "Unknown category, observed 0-2. Zero dominates; 1/2 occur more often on moving targets."),
  ("REL_LAT_SPEED", "Target lateral speed relative to the ego vehicle axis."),
  ("REL_ACCEL", "Target longitudinal acceleration relative to ego acceleration."),
  ("NEW_SIGNAL_18", _comment(
    "Unknown optional measurement-status attribute. EV9/Ioniq 9 use 1/2 almost exclusively for measured STATE=3 tracks",
    "and 0 for coasted STATE=4 tracks; the distinction between 1 and 2 is unknown. The rare value 3 is also observed.",
  )),
  ("NEW_SIGNAL_5", "Unknown sparse optional attribute. Observed 0-32 and almost always 0; no stable correlation was found."),
  ("WIDTH", _comment(
    "Strongly identified target width in 0.1 m units from recurring approximately 2.0 m passenger cars.",
    "Observed 0.0-3.0 m; many platforms transmit 0. Every address in the range can carry it.",
  )),
  ("LENGTH", _comment(
    "Strongly identified target length in 0.1 m units from approximately 4.0 m cars and 13.0-15.5 m long vehicles.",
    "This is an 8-bit field; many platforms transmit 0.",
  )),
  ("ABS_SPEED", _comment(
    "Strongly inferred absolute target-speed magnitude. On Ioniq 9 it matches",
    "hypot(ego speed + REL_SPEED, REL_LAT_SPEED), including targets without dimensions; observed 0.0-54.4 m/s.",
  )),
  ("ORIENTATION_ANGLE", _comment(
    "Strongly inferred target orientation relative to the ego axis. Moving vehicles cluster near 0 degrees;",
    "it is associated with dimension-bearing targets. Values near +/-180 can be real rearward orientation on rich tracks,",
    "while non-rich platforms use +180 as an unavailable/default value.",
  )),
  ("NEW_SIGNAL_13", "Unknown optional 0-10 shape/geometry metric, nonzero only on dimension-bearing targets in tested routes."),
  ("NEW_SIGNAL_12", _comment(
    "Strong geometry-age/maturity candidate: two Ioniq 9 routes progressed 0, 1, 2, ... 10 and saturated at 10.",
    "Cross-platform confirmation is still insufficient for a semantic rename.",
  )),
  ("NEW_SIGNAL_14", "Unknown optional geometry category, observed 0-3. The common NEW_SIGNAL_14-17 tuple is 2,2,2,1."),
  ("NEW_SIGNAL_15", "Unknown optional geometry category, observed 0-2. The common NEW_SIGNAL_14-17 tuple is 2,2,2,1."),
  ("NEW_SIGNAL_16", "Unknown optional geometry category, observed 0-3. The common NEW_SIGNAL_14-17 tuple is 2,2,2,1."),
  ("NEW_SIGNAL_17", "Unknown optional geometry category, observed 0-2. The common NEW_SIGNAL_14-17 tuple is 2,2,2,1."),
)


def generate():
  parts = []
  parts.append("""
VERSION ""


NS_ :
    NS_DESC_
    CM_
    BA_DEF_
    BA_
    VAL_
    CAT_DEF_
    CAT_
    FILTER
    BA_DEF_DEF_
    EV_DATA_
    ENVVAR_DATA_
    SGTYPE_
    SGTYPE_VAL_
    BA_DEF_SGTYPE_
    BA_SGTYPE_
    SIG_TYPE_REF_
    VAL_TABLE_
    SIG_GROUP_
    SIG_VALTYPE_
    SIGTYPE_VALTYPE_
    BO_TX_BU_
    BA_DEF_REL_
    BA_REL_
    BA_DEF_DEF_REL_
    BU_SG_REL_
    BU_EV_REL_
    BU_BO_REL_
    SG_MUL_VAL_

BS_:

BU_: XXX
    """)

  for a in range(0x3A5, 0x3A5 + 32):
    parts.append(f"""
BO_ {a} RADAR_TRACK_{a:x}: 24 RADAR
 SG_ CHECKSUM : 0|16@1+ (1,0) [0|65535] "" XXX
 SG_ COUNTER : 16|8@1+ (1,0) [0|255] "" XXX
 SG_ STATE_ALT : 25|2@0+ (1,0) [0|3] "" XXX
 SG_ MOTION_STATE : 28|2@0+ (1,0) [0|2] "" XXX
 SG_ TRACK_COUNTER : 31|2@0+ (1,0) [0|3] "" XXX
 SG_ TRACK_QUALITY : 38|7@0+ (1,0) [0|127] "" XXX
 SG_ AGE : 47|8@0+ (1,0) [0|255] "" XXX
 SG_ COAST_AGE : 51|4@0+ (1,0) [0|15] "" XXX
 SG_ STATE : 54|3@0+ (1,0) [0|7] "" XXX
 SG_ RCS : 62|7@0- (1,0) [-64|63] "" XXX
 SG_ LONG_DIST : 63|13@1+ (0.05,0) [0|409.55] "m" XXX
 SG_ LAT_DIST : 76|12@1- (0.05,0) [-102.4|102.35] "m" XXX
 SG_ REL_SPEED : 88|14@1- (0.01,0) [-81.92|81.91] "m/s" XXX
 SG_ NEW_SIGNAL_4 : 103|2@0+ (1,0) [0|2] "" XXX
 SG_ REL_LAT_SPEED : 104|13@1- (0.01,0) [-40.96|40.95] "m/s" XXX
 SG_ REL_ACCEL : 118|10@1- (0.02,0) [-10.24|10.22] "m/s^2" XXX
 SG_ NEW_SIGNAL_18 : 129|2@0+ (1,0) [0|3] "" XXX
 SG_ NEW_SIGNAL_5 : 135|6@0+ (1,0) [0|32] "" XXX
 SG_ WIDTH : 138|5@1+ (0.1,0) [0|3.1] "m" XXX
 SG_ LENGTH : 151|8@0+ (0.1,0) [0|25.5] "m" XXX
 SG_ ABS_SPEED : 152|10@1+ (0.1,0) [0|102.3] "m/s" XXX
 SG_ ORIENTATION_ANGLE : 162|9@1- (1,0) [-180|180] "deg" XXX
 SG_ NEW_SIGNAL_13 : 175|4@0+ (1,0) [0|10] "" XXX
 SG_ NEW_SIGNAL_12 : 179|4@0+ (1,0) [0|10] "" XXX
 SG_ NEW_SIGNAL_14 : 181|2@0+ (1,0) [0|3] "" XXX
 SG_ NEW_SIGNAL_15 : 183|2@0+ (1,0) [0|2] "" XXX
 SG_ NEW_SIGNAL_16 : 185|2@0+ (1,0) [0|3] "" XXX
 SG_ NEW_SIGNAL_17 : 187|2@0+ (1,0) [0|2] "" XXX

VAL_ {a} STATE_ALT 0 "EMPTY" 1 "TENTATIVE" 2 "MEASURED" 3 "COASTED" ;
VAL_ {a} MOTION_STATE 0 "UNKNOWN" 1 "STATIONARY" 2 "MOVING" ;
VAL_ {a} STATE 0 "EMPTY" 1 "TENTATIVE_1" 2 "TENTATIVE_2" 3 "MEASURED" 4 "COASTED" 7 "UNRESOLVED_TENTATIVE" ;
    """)

    parts.append(f'CM_ BO_ {a} "{RADAR_3A5_3C4_MESSAGE_COMMENT}";\n')
    parts.extend(f'CM_ SG_ {a} {signal} "{comment}";\n' for signal, comment in RADAR_3A5_3C4_SIGNAL_COMMENTS)

  return {"hyundai_radar_3a5_3c4.dbc": "".join(parts)}

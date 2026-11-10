"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

h3lite: the few H3 functions the car needs, in pure Python.

sunnypilot doesn't add Python packages, so instead of the h3 package this is a
line-by-line port of the parts of Uber's H3 v4.1.2 C library we use:
latLngToCell, cellToLatLng, cellToParent and a one-ring disk. Cell ids match
the real library exactly (tests/test_h3lite.py checks this against h3-py when
it's installed, and against fixed vectors when it isn't), so the site and the
server can keep using h3-js and h3-pg on the same ids.

H3 is Copyright Uber Technologies, Inc., licensed under the Apache License 2.0
(https://github.com/uber/h3). The tables below are copied from its
faceijk.c and baseCells.c.
"""
from __future__ import annotations

import math

MAX_RES = 15
NUM_FACES = 20
NUM_BASE_CELLS = 122

_EPSILON = 1e-16
_SQRT3_2 = 0.8660254037844386467637231707529361834714
_SQRT7 = 2.6457513110645905905016157536392604257102
_AP7_ROT_RADS = 0.333473172251832115336090755351601070065900389
_RES0_U_GNOMONIC = 0.38196601125010500003
_2PI = 2.0 * math.pi

# Directions (index digits)
_CENTER, _K, _J, _JK, _I, _IK, _IJ = range(7)
_UNIT_VECS = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0))
_ROT_CCW = (0, _IK, _JK, _K, _IJ, _I, _J)   # digit -> digit rotated 60 degrees ccw
_ROT_CW = (0, _JK, _IJ, _J, _IK, _K, _I)    # digit -> digit rotated 60 degrees cw

# face neighbor quadrants
_IJ_Q, _KI_Q, _JK_Q = 1, 2, 3

# bit layout of an H3 index
_MODE_OFFSET = 59
_RES_OFFSET = 52
_BC_OFFSET = 45
_H3_INIT = (1 << 45) - 1   # every digit set to 7
_CELL_MODE = 1


def _max_dim(res: int) -> int:     # Class II resolutions only
  return 2 * 7 ** (res // 2)


def _unit_scale(res: int) -> int:  # Class II resolutions only
  return 7 ** (res // 2)


# --- tables copied from H3 v4.1.2 faceijk.c and baseCells.c ---

FACE_CENTER_GEO = (
  (0.80358264971899, 1.2483974196173961), (1.3077478834556382, 2.5369450098779214),
  (1.054751253523952, -1.3475173589003966), (0.6001915955381868, -0.45060390946975576),
  (0.49171542819877384, 0.40198820291130694), (0.1727453274156187, 1.6781468852804338),
  (0.6059293215713507, 2.9539233298124117), (0.42737051832897965, -1.8888762003362853),
  (-0.07906611854921283, -0.7334295133808677), (-0.23096164445538364, 0.506495587332349),
  (0.07906611854921283, 2.4081631402089254), (0.23096164445538364, -2.635097066257444),
  (-0.1727453274156187, -1.4634457683093596), (-0.6059293215713507, -0.18766932377738163),
  (-0.42737051832897965, 1.2527164532535078), (-0.6001915955381868, 2.6909887441200375),
  (-0.49171542819877384, -2.7396044506784865), (-0.80358264971899, -1.8931952339723972),
  (-1.3077478834556382, -0.6046476437118721), (-1.054751253523952, 1.7940752946893965),
)
FACE_CENTER_POINT = (
  (0.2199307791404606, 0.6583691780274996, 0.7198475378926182),
  (-0.2139234834501421, 0.1478171829550703, 0.9656017935214205),
  (0.1092625278784797, -0.481195157287321, 0.8697775121287253),
  (0.7428567301586791, -0.3593941678278028, 0.5648005936517033),
  (0.8112534709140969, 0.3448953237639384, 0.472138773641393),
  (-0.1055498149613921, 0.9794457296411413, 0.1718874610009365),
  (-0.8075407579970092, 0.1533552485898818, 0.5695261994882688),
  (-0.2846148069787907, -0.8644080972654206, 0.4144792552473539),
  (0.7405621473854482, -0.6673299564565524, -0.0789837646326737),
  (0.8512303986474293, 0.4722343788582681, -0.2289137388687808),
  (-0.7405621473854481, 0.6673299564565524, 0.0789837646326737),
  (-0.8512303986474292, -0.4722343788582682, 0.2289137388687808),
  (0.1055498149613919, -0.9794457296411413, -0.1718874610009365),
  (0.8075407579970092, -0.1533552485898819, -0.5695261994882688),
  (0.2846148069787908, 0.8644080972654204, -0.4144792552473539),
  (-0.7428567301586791, 0.3593941678278027, -0.5648005936517033),
  (-0.811253470914097, -0.3448953237639382, -0.472138773641393),
  (-0.2199307791404607, -0.6583691780274996, -0.7198475378926182),
  (0.213923483450142, -0.1478171829550704, -0.9656017935214205),
  (-0.1092625278784796, 0.481195157287321, -0.8697775121287253),
)
FACE_AXIS_AZ_CII = (
  5.6199582685239395, 5.7603390817141875, 0.78021365439343, 0.4304693639799999,
  6.130269123335111, 2.692877706530643, 2.982963003477244, 3.532912002790141,
  3.494305004259568, 3.0032141694995382, 5.930472956509812, 0.13837848409025486,
  0.4487149470591504, 0.15862965011254937, 5.891865957979238, 2.711123289609793,
  3.294508837434268, 3.80481969224544, 3.6644388790551923, 2.361378999196363,
)
# per face: (central, ij, ki, jk) neighbors as (face, (i, j, k) translate, ccw 60 rotations)
FACE_NEIGHBORS = (
  ((0, (0, 0, 0), 0), (4, (2, 0, 2), 1), (1, (2, 2, 0), 5), (5, (0, 2, 2), 3)),
  ((1, (0, 0, 0), 0), (0, (2, 0, 2), 1), (2, (2, 2, 0), 5), (6, (0, 2, 2), 3)),
  ((2, (0, 0, 0), 0), (1, (2, 0, 2), 1), (3, (2, 2, 0), 5), (7, (0, 2, 2), 3)),
  ((3, (0, 0, 0), 0), (2, (2, 0, 2), 1), (4, (2, 2, 0), 5), (8, (0, 2, 2), 3)),
  ((4, (0, 0, 0), 0), (3, (2, 0, 2), 1), (0, (2, 2, 0), 5), (9, (0, 2, 2), 3)),
  ((5, (0, 0, 0), 0), (10, (2, 2, 0), 3), (14, (2, 0, 2), 3), (0, (0, 2, 2), 3)),
  ((6, (0, 0, 0), 0), (11, (2, 2, 0), 3), (10, (2, 0, 2), 3), (1, (0, 2, 2), 3)),
  ((7, (0, 0, 0), 0), (12, (2, 2, 0), 3), (11, (2, 0, 2), 3), (2, (0, 2, 2), 3)),
  ((8, (0, 0, 0), 0), (13, (2, 2, 0), 3), (12, (2, 0, 2), 3), (3, (0, 2, 2), 3)),
  ((9, (0, 0, 0), 0), (14, (2, 2, 0), 3), (13, (2, 0, 2), 3), (4, (0, 2, 2), 3)),
  ((10, (0, 0, 0), 0), (5, (2, 2, 0), 3), (6, (2, 0, 2), 3), (15, (0, 2, 2), 3)),
  ((11, (0, 0, 0), 0), (6, (2, 2, 0), 3), (7, (2, 0, 2), 3), (16, (0, 2, 2), 3)),
  ((12, (0, 0, 0), 0), (7, (2, 2, 0), 3), (8, (2, 0, 2), 3), (17, (0, 2, 2), 3)),
  ((13, (0, 0, 0), 0), (8, (2, 2, 0), 3), (9, (2, 0, 2), 3), (18, (0, 2, 2), 3)),
  ((14, (0, 0, 0), 0), (9, (2, 2, 0), 3), (5, (2, 0, 2), 3), (19, (0, 2, 2), 3)),
  ((15, (0, 0, 0), 0), (16, (2, 0, 2), 1), (19, (2, 2, 0), 5), (10, (0, 2, 2), 3)),
  ((16, (0, 0, 0), 0), (17, (2, 0, 2), 1), (15, (2, 2, 0), 5), (11, (0, 2, 2), 3)),
  ((17, (0, 0, 0), 0), (18, (2, 0, 2), 1), (16, (2, 2, 0), 5), (12, (0, 2, 2), 3)),
  ((18, (0, 0, 0), 0), (19, (2, 0, 2), 1), (17, (2, 2, 0), 5), (13, (0, 2, 2), 3)),
  ((19, (0, 0, 0), 0), (15, (2, 0, 2), 1), (18, (2, 2, 0), 5), (14, (0, 2, 2), 3)),
)
# [face][i][j][k] -> (base cell, ccw 60 rotations), flattened as face*27 + i*9 + j*3 + k
FACE_IJK_BASE_CELLS = (
  (16,0), (18,0), (24,0), (33,0), (30,0), (32,3), (49,1), (48,3), (50,3),
  (8,0), (5,5), (10,5), (22,0), (16,0), (18,0), (41,1), (33,0), (30,0),
  (4,0), (0,5), (2,5), (15,1), (8,0), (5,5), (31,1), (22,0), (16,0),
  (2,0), (6,0), (14,0), (10,0), (11,0), (17,3), (24,1), (23,3), (25,3),
  (0,0), (1,5), (9,5), (5,0), (2,0), (6,0), (18,1), (10,0), (11,0),
  (4,1), (3,5), (7,5), (8,1), (0,0), (1,5), (16,1), (5,0), (2,0),
  (7,0), (21,0), (38,0), (9,0), (19,0), (34,3), (14,1), (20,3), (36,3),
  (3,0), (13,5), (29,5), (1,0), (7,0), (21,0), (6,1), (9,0), (19,0),
  (4,2), (12,5), (26,5), (0,1), (3,0), (13,5), (2,1), (1,0), (7,0),
  (26,0), (42,0), (58,0), (29,0), (43,0), (62,3), (38,1), (47,3), (64,3),
  (12,0), (28,5), (44,5), (13,0), (26,0), (42,0), (21,1), (29,0), (43,0),
  (4,3), (15,5), (31,5), (3,1), (12,0), (28,5), (7,1), (13,0), (26,0),
  (31,0), (41,0), (49,0), (44,0), (53,0), (61,3), (58,1), (65,3), (75,3),
  (15,0), (22,5), (33,5), (28,0), (31,0), (41,0), (42,1), (44,0), (53,0),
  (4,4), (8,5), (16,5), (12,1), (15,0), (22,5), (26,1), (28,0), (31,0),
  (50,0), (48,0), (49,3), (32,0), (30,3), (33,3), (24,3), (18,3), (16,3),
  (70,0), (67,0), (66,3), (52,3), (50,0), (48,0), (37,3), (32,0), (30,3),
  (83,0), (87,3), (85,3), (74,3), (70,0), (67,0), (57,1), (52,3), (50,0),
  (25,0), (23,0), (24,3), (17,0), (11,3), (10,3), (14,3), (6,3), (2,3),
  (45,0), (39,0), (37,3), (35,3), (25,0), (23,0), (27,3), (17,0), (11,3),
  (63,0), (59,3), (57,3), (56,3), (45,0), (39,0), (46,3), (35,3), (25,0),
  (36,0), (20,0), (14,3), (34,0), (19,3), (9,3), (38,3), (21,3), (7,3),
  (55,0), (40,0), (27,3), (54,3), (36,0), (20,0), (51,3), (34,0), (19,3),
  (72,0), (60,3), (46,3), (73,3), (55,0), (40,0), (71,3), (54,3), (36,0),
  (64,0), (47,0), (38,3), (62,0), (43,3), (29,3), (58,3), (42,3), (26,3),
  (84,0), (69,0), (51,3), (82,3), (64,0), (47,0), (76,3), (62,0), (43,3),
  (97,0), (89,3), (71,3), (98,3), (84,0), (69,0), (96,3), (82,3), (64,0),
  (75,0), (65,0), (58,3), (61,0), (53,3), (44,3), (49,3), (41,3), (31,3),
  (94,0), (86,0), (76,3), (81,3), (75,0), (65,0), (66,3), (61,0), (53,3),
  (107,0), (104,3), (96,3), (101,3), (94,0), (86,0), (85,3), (81,3), (75,0),
  (57,0), (59,0), (63,3), (74,0), (78,3), (79,3), (83,3), (92,3), (95,3),
  (37,0), (39,3), (45,3), (52,0), (57,0), (59,0), (70,3), (74,0), (78,3),
  (24,0), (23,3), (25,3), (32,3), (37,0), (39,3), (50,3), (52,0), (57,0),
  (46,0), (60,0), (72,3), (56,0), (68,3), (80,3), (63,3), (77,3), (90,3),
  (27,0), (40,3), (55,3), (35,0), (46,0), (60,0), (45,3), (56,0), (68,3),
  (14,0), (20,3), (36,3), (17,3), (27,0), (40,3), (25,3), (35,0), (46,0),
  (71,0), (89,0), (97,3), (73,0), (91,3), (103,3), (72,3), (88,3), (105,3),
  (51,0), (69,3), (84,3), (54,0), (71,0), (89,0), (55,3), (73,0), (91,3),
  (38,0), (47,3), (64,3), (34,3), (51,0), (69,3), (36,3), (54,0), (71,0),
  (96,0), (104,0), (107,3), (98,0), (110,3), (115,3), (97,3), (111,3), (119,3),
  (76,0), (86,3), (94,3), (82,0), (96,0), (104,0), (84,3), (98,0), (110,3),
  (58,0), (65,3), (75,3), (62,3), (76,0), (86,3), (64,3), (82,0), (96,0),
  (85,0), (87,0), (83,3), (101,0), (102,3), (100,3), (107,3), (112,3), (114,3),
  (66,0), (67,3), (70,3), (81,0), (85,0), (87,0), (94,3), (101,0), (102,3),
  (49,0), (48,3), (50,3), (61,3), (66,0), (67,3), (75,3), (81,0), (85,0),
  (95,0), (92,0), (83,0), (79,0), (78,0), (74,3), (63,1), (59,3), (57,3),
  (109,0), (108,0), (100,5), (93,1), (95,0), (92,0), (77,1), (79,0), (78,0),
  (117,4), (118,5), (114,5), (106,1), (109,0), (108,0), (90,1), (93,1), (95,0),
  (90,0), (77,0), (63,0), (80,0), (68,0), (56,3), (72,1), (60,3), (46,3),
  (106,0), (93,0), (79,5), (99,1), (90,0), (77,0), (88,1), (80,0), (68,0),
  (117,3), (109,5), (95,5), (113,1), (106,0), (93,0), (105,1), (99,1), (90,0),
  (105,0), (88,0), (72,0), (103,0), (91,0), (73,3), (97,1), (89,3), (71,3),
  (113,0), (99,0), (80,5), (116,1), (105,0), (88,0), (111,1), (103,0), (91,0),
  (117,2), (106,5), (90,5), (121,1), (113,0), (99,0), (119,1), (116,1), (105,0),
  (119,0), (111,0), (97,0), (115,0), (110,0), (98,3), (107,1), (104,3), (96,3),
  (121,0), (116,0), (103,5), (120,1), (119,0), (111,0), (112,1), (115,0), (110,0),
  (117,1), (113,5), (105,5), (118,1), (121,0), (116,0), (114,1), (120,1), (119,0),
  (114,0), (112,0), (107,0), (100,0), (102,0), (101,3), (83,1), (87,3), (85,3),
  (118,0), (120,0), (115,5), (108,1), (114,0), (112,0), (92,1), (100,0), (102,0),
  (117,0), (121,5), (119,5), (109,1), (118,0), (120,0), (95,1), (108,1), (114,0),
)
# base cell -> (home face, i, j, k, is pentagon, cw offset face 1, cw offset face 2)
BASE_CELL_DATA = (
  (1,1,0,0,0,0,0), (2,1,1,0,0,0,0), (1,0,0,0,0,0,0), (2,1,0,0,0,0,0),
  (0,2,0,0,1,-1,-1), (1,1,1,0,0,0,0), (1,0,0,1,0,0,0), (2,0,0,0,0,0,0),
  (0,1,0,0,0,0,0), (2,0,1,0,0,0,0), (1,0,1,0,0,0,0), (1,0,1,1,0,0,0),
  (3,1,0,0,0,0,0), (3,1,1,0,0,0,0), (11,2,0,0,1,2,6), (4,1,0,0,0,0,0),
  (0,0,0,0,0,0,0), (6,0,1,0,0,0,0), (0,0,0,1,0,0,0), (2,0,1,1,0,0,0),
  (7,0,0,1,0,0,0), (2,0,0,1,0,0,0), (0,1,1,0,0,0,0), (6,0,0,1,0,0,0),
  (10,2,0,0,1,1,5), (6,0,0,0,0,0,0), (3,0,0,0,0,0,0), (11,1,0,0,0,0,0),
  (4,1,1,0,0,0,0), (3,0,1,0,0,0,0), (0,0,1,1,0,0,0), (4,0,0,0,0,0,0),
  (5,0,1,0,0,0,0), (0,0,1,0,0,0,0), (7,0,1,0,0,0,0), (11,1,1,0,0,0,0),
  (7,0,0,0,0,0,0), (10,1,0,0,0,0,0), (12,2,0,0,1,3,7), (6,1,0,1,0,0,0),
  (7,1,0,1,0,0,0), (4,0,0,1,0,0,0), (3,0,0,1,0,0,0), (3,0,1,1,0,0,0),
  (4,0,1,0,0,0,0), (6,1,0,0,0,0,0), (11,0,0,0,0,0,0), (8,0,0,1,0,0,0),
  (5,0,0,1,0,0,0), (14,2,0,0,1,0,9), (5,0,0,0,0,0,0), (12,1,0,0,0,0,0),
  (10,1,1,0,0,0,0), (4,0,1,1,0,0,0), (12,1,1,0,0,0,0), (7,1,0,0,0,0,0),
  (11,0,1,0,0,0,0), (10,0,0,0,0,0,0), (13,2,0,0,1,4,8), (10,0,0,1,0,0,0),
  (11,0,0,1,0,0,0), (9,0,1,0,0,0,0), (8,0,1,0,0,0,0), (6,2,0,0,1,11,15),
  (8,0,0,0,0,0,0), (9,0,0,1,0,0,0), (14,1,0,0,0,0,0), (5,1,0,1,0,0,0),
  (16,0,1,1,0,0,0), (8,1,0,1,0,0,0), (5,1,0,0,0,0,0), (12,0,0,0,0,0,0),
  (7,2,0,0,1,12,16), (12,0,1,0,0,0,0), (10,0,1,0,0,0,0), (9,0,0,0,0,0,0),
  (13,1,0,0,0,0,0), (16,0,0,1,0,0,0), (15,0,1,1,0,0,0), (15,0,1,0,0,0,0),
  (16,0,1,0,0,0,0), (14,1,1,0,0,0,0), (13,1,1,0,0,0,0), (5,2,0,0,1,10,19),
  (8,1,0,0,0,0,0), (14,0,0,0,0,0,0), (9,1,0,1,0,0,0), (14,0,0,1,0,0,0),
  (17,0,0,1,0,0,0), (12,0,0,1,0,0,0), (16,0,0,0,0,0,0), (17,0,1,1,0,0,0),
  (15,0,0,1,0,0,0), (16,1,0,1,0,0,0), (9,1,0,0,0,0,0), (15,0,0,0,0,0,0),
  (13,0,0,0,0,0,0), (8,2,0,0,1,13,17), (13,0,1,0,0,0,0), (17,1,0,1,0,0,0),
  (19,0,1,0,0,0,0), (14,0,1,0,0,0,0), (19,0,1,1,0,0,0), (17,0,1,0,0,0,0),
  (13,0,0,1,0,0,0), (17,0,0,0,0,0,0), (16,1,0,0,0,0,0), (9,2,0,0,1,14,18),
  (15,1,0,1,0,0,0), (15,1,0,0,0,0,0), (18,0,1,1,0,0,0), (18,0,0,1,0,0,0),
  (19,0,0,1,0,0,0), (17,1,0,0,0,0,0), (19,0,0,0,0,0,0), (18,0,1,0,0,0,0),
  (18,1,0,1,0,0,0), (19,2,0,0,1,-1,-1), (19,1,0,0,0,0,0), (18,0,0,0,0,0,0),
  (19,1,0,1,0,0,0), (18,1,0,0,0,0,0),
)


# --- ijk coordinates ---

def _lround(x: float) -> int:
  """C lroundl: halves round away from zero."""
  return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))


def _normalize(i: int, j: int, k: int) -> tuple[int, int, int]:
  if i < 0:
    j -= i
    k -= i
    i = 0
  if j < 0:
    i -= j
    k -= j
    j = 0
  if k < 0:
    i -= k
    j -= k
    k = 0
  m = min(i, j, k)
  if m > 0:
    i -= m
    j -= m
    k -= m
  return i, j, k


def _add(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
  return _normalize(a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scaled_sum(c: tuple[int, int, int], iv, jv, kv) -> tuple[int, int, int]:
  i, j, k = c
  return _normalize(iv[0] * i + jv[0] * j + kv[0] * k,
                    iv[1] * i + jv[1] * j + kv[1] * k,
                    iv[2] * i + jv[2] * j + kv[2] * k)


def _up_ap7(c):
  i, j = c[0] - c[2], c[1] - c[2]
  return _normalize(_lround((3 * i - j) / 7.0), _lround((i + 2 * j) / 7.0), 0)


def _up_ap7r(c):
  i, j = c[0] - c[2], c[1] - c[2]
  return _normalize(_lround((2 * i + j) / 7.0), _lround((3 * j - i) / 7.0), 0)


def _down_ap7(c):
  return _scaled_sum(c, (3, 0, 1), (1, 3, 0), (0, 1, 3))


def _down_ap7r(c):
  return _scaled_sum(c, (3, 1, 0), (0, 3, 1), (1, 0, 3))


def _rotate60ccw(c):
  return _scaled_sum(c, (1, 1, 0), (0, 1, 1), (1, 0, 1))


def _rotate60cw(c):
  return _scaled_sum(c, (1, 0, 1), (1, 1, 0), (0, 1, 1))


def _unit_to_digit(c) -> int:
  c = _normalize(*c)
  for d, u in enumerate(_UNIT_VECS):
    if c == u:
      return d
  return 7


def _hex2d_to_ijk(x: float, y: float) -> tuple[int, int, int]:
  a1, a2 = abs(x), abs(y)
  x2 = a2 / _SQRT3_2
  x1 = a1 + x2 / 2.0
  m1, m2 = int(x1), int(x2)
  r1, r2 = x1 - m1, x2 - m2

  if r1 < 0.5:
    if r1 < 1.0 / 3.0:
      i = m1
      j = m2 if r2 < (1.0 + r1) / 2.0 else m2 + 1
    else:
      j = m2 if r2 < (1.0 - r1) else m2 + 1
      i = m1 + 1 if (1.0 - r1) <= r2 < (2.0 * r1) else m1
  else:
    if r1 < 2.0 / 3.0:
      j = m2 if r2 < (1.0 - r1) else m2 + 1
      i = m1 if (2.0 * r1 - 1.0) < r2 < (1.0 - r1) else m1 + 1
    else:
      i = m1 + 1
      j = m2 if r2 < (r1 / 2.0) else m2 + 1

  # fold across the axes if necessary
  if x < 0.0:
    if j % 2 == 0:
      i = i - 2 * (i - j // 2)
    else:
      i = i - (2 * (i - (j + 1) // 2) + 1)
  if y < 0.0:
    i = i - (2 * j + 1) // 2
    j = -j
  return _normalize(i, j, 0)


def _ijk_to_hex2d(c) -> tuple[float, float]:
  i, j = c[0] - c[2], c[1] - c[2]
  return i - 0.5 * j, j * _SQRT3_2


# --- sphere <-> face ---

def _pos_angle(rads: float) -> float:
  tmp = rads + _2PI if rads < 0.0 else rads
  if rads >= _2PI:
    tmp -= _2PI
  return tmp


def _constrain_lng(lng: float) -> float:
  while lng > math.pi:
    lng -= _2PI
  while lng < -math.pi:
    lng += _2PI
  return lng


def _azimuth(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
  return math.atan2(math.cos(lat2) * math.sin(lng2 - lng1),
                    math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lng2 - lng1))


def _az_distance(lat1: float, lng1: float, az: float, distance: float) -> tuple[float, float]:
  if distance < _EPSILON:
    return lat1, lng1
  az = _pos_angle(az)
  if az < _EPSILON or abs(az - math.pi) < _EPSILON:
    lat2 = lat1 + distance if az < _EPSILON else lat1 - distance
    if abs(lat2 - math.pi / 2) < _EPSILON:
      return math.pi / 2, 0.0
    if abs(lat2 + math.pi / 2) < _EPSILON:
      return -math.pi / 2, 0.0
    return lat2, _constrain_lng(lng1)

  sinlat = math.sin(lat1) * math.cos(distance) + math.cos(lat1) * math.sin(distance) * math.cos(az)
  sinlat = max(-1.0, min(1.0, sinlat))
  lat2 = math.asin(sinlat)
  if abs(lat2 - math.pi / 2) < _EPSILON:
    return math.pi / 2, 0.0
  if abs(lat2 + math.pi / 2) < _EPSILON:
    return -math.pi / 2, 0.0
  sinlng = math.sin(az) * math.sin(distance) / math.cos(lat2)
  coslng = (math.cos(distance) - math.sin(lat1) * math.sin(lat2)) / math.cos(lat1) / math.cos(lat2)
  sinlng = max(-1.0, min(1.0, sinlng))
  coslng = max(-1.0, min(1.0, coslng))
  return lat2, _constrain_lng(lng1 + math.atan2(sinlng, coslng))


def _closest_face(lat: float, lng: float) -> tuple[int, float]:
  r = math.cos(lat)
  z, x, y = math.sin(lat), math.cos(lng) * r, math.sin(lng) * r
  face, sqd = 0, 5.0
  for f, (fx, fy, fz) in enumerate(FACE_CENTER_POINT):
    d = (fx - x) ** 2 + (fy - y) ** 2 + (fz - z) ** 2
    if d < sqd:
      face, sqd = f, d
  return face, sqd


def _geo_to_hex2d(lat: float, lng: float, res: int) -> tuple[int, float, float]:
  face, sqd = _closest_face(lat, lng)
  r = math.acos(1 - sqd / 2)
  if r < _EPSILON:
    return face, 0.0, 0.0

  flat, flng = FACE_CENTER_GEO[face]
  theta = _pos_angle(FACE_AXIS_AZ_CII[face] - _pos_angle(_azimuth(flat, flng, lat, lng)))
  if res % 2:
    theta = _pos_angle(theta - _AP7_ROT_RADS)

  r = math.tan(r) / _RES0_U_GNOMONIC
  for _ in range(res):
    r *= _SQRT7
  return face, r * math.cos(theta), r * math.sin(theta)


def _hex2d_to_geo(x: float, y: float, face: int, res: int) -> tuple[float, float]:
  r = math.hypot(x, y)
  if r < _EPSILON:
    return FACE_CENTER_GEO[face]
  theta = math.atan2(y, x)
  for _ in range(res):
    r /= _SQRT7
  r = math.atan(r * _RES0_U_GNOMONIC)
  if res % 2:
    theta = _pos_angle(theta + _AP7_ROT_RADS)
  theta = _pos_angle(FACE_AXIS_AZ_CII[face] - theta)
  flat, flng = FACE_CENTER_GEO[face]
  return _az_distance(flat, flng, theta, r)


# --- H3 index bits ---

def get_resolution(h: int) -> int:
  return (h >> _RES_OFFSET) & 15


def get_base_cell(h: int) -> int:
  return (h >> _BC_OFFSET) & 127


def _digit(h: int, r: int) -> int:
  return (h >> ((MAX_RES - r) * 3)) & 7


def _set_digit(h: int, r: int, d: int) -> int:
  off = (MAX_RES - r) * 3
  return (h & ~(7 << off)) | (d << off)


def _leading_digit(h: int) -> int:
  for r in range(1, get_resolution(h) + 1):
    d = _digit(h, r)
    if d:
      return d
  return 0


def _rotate_index60ccw(h: int) -> int:
  for r in range(1, get_resolution(h) + 1):
    h = _set_digit(h, r, _ROT_CCW[_digit(h, r)])
  return h


def _rotate_index60cw(h: int) -> int:
  for r in range(1, get_resolution(h) + 1):
    h = _set_digit(h, r, _ROT_CW[_digit(h, r)])
  return h


def _rotate_pent60ccw(h: int) -> int:
  found = False
  for r in range(1, get_resolution(h) + 1):
    h = _set_digit(h, r, _ROT_CCW[_digit(h, r)])
    if not found and _digit(h, r) != 0:
      found = True
      if _leading_digit(h) == _K:
        h = _rotate_index60ccw(h)
  return h


def _is_pentagon_base(bc: int) -> bool:
  return 0 <= bc < NUM_BASE_CELLS and bool(BASE_CELL_DATA[bc][4])


def _face_ijk_base(face: int, c) -> tuple[int, int]:
  return FACE_IJK_BASE_CELLS[face * 27 + c[0] * 9 + c[1] * 3 + c[2]]


def _face_ijk_to_h3(face: int, c, res: int) -> int:
  h = _H3_INIT | (_CELL_MODE << _MODE_OFFSET) | (res << _RES_OFFSET)
  for r in range(res - 1, -1, -1):
    last = c
    if (r + 1) % 2:
      c = _up_ap7(c)
      center = _down_ap7(c)
    else:
      c = _up_ap7r(c)
      center = _down_ap7r(c)
    diff = _normalize(last[0] - center[0], last[1] - center[1], last[2] - center[2])
    h = _set_digit(h, r + 1, _unit_to_digit(diff))

  if max(c) > 2:
    raise ValueError("coordinates off the base cell's face")
  bc, rots = _face_ijk_base(face, c)
  h = (h & ~(127 << _BC_OFFSET)) | (bc << _BC_OFFSET)

  if _is_pentagon_base(bc):
    if _leading_digit(h) == _K:
      data = BASE_CELL_DATA[bc]
      h = _rotate_index60cw(h) if face in (data[5], data[6]) else _rotate_index60ccw(h)
    for _ in range(rots):
      h = _rotate_pent60ccw(h)
  else:
    for _ in range(rots):
      h = _rotate_index60ccw(h)
  return h


def _adjust_overage_class2(face: int, c, res: int, pent_leading4: bool) -> tuple[int, tuple[int, int, int], bool]:
  """Move coordinates that fell off the face onto the neighboring face. Returns (face, ijk, moved)."""
  max_dim = _max_dim(res)
  if sum(c) <= max_dim:
    return face, c, False

  if c[2] > 0:
    if c[1] > 0:
      orient = FACE_NEIGHBORS[face][_JK_Q]
    else:
      orient = FACE_NEIGHBORS[face][_KI_Q]
      if pent_leading4:
        # rotate around the pentagon's center for its missing sequence
        tmp = _rotate60cw((c[0] - max_dim, c[1], c[2]))
        c = _normalize(tmp[0] + max_dim, tmp[1], tmp[2])
  else:
    orient = FACE_NEIGHBORS[face][_IJ_Q]

  new_face, (ti, tj, tk), ccw = orient
  for _ in range(ccw):
    c = _rotate60ccw(c)
  s = _unit_scale(res)
  c = _normalize(c[0] + ti * s, c[1] + tj * s, c[2] + tk * s)
  return new_face, c, True


def _h3_to_face_ijk(h: int) -> tuple[int, tuple[int, int, int]]:
  bc = get_base_cell(h)
  if not 0 <= bc < NUM_BASE_CELLS:
    raise ValueError("invalid base cell")
  if _is_pentagon_base(bc) and _leading_digit(h) == _IK:
    h = _rotate_index60cw(h)

  data = BASE_CELL_DATA[bc]
  face, c = data[0], (data[1], data[2], data[3])
  res = get_resolution(h)
  possible_overage = _is_pentagon_base(bc) or not (res == 0 or c == (0, 0, 0))
  for r in range(1, res + 1):
    c = _down_ap7(c) if r % 2 else _down_ap7r(c)
    d = _digit(h, r)
    if 0 < d < 7:
      c = _add(c, _UNIT_VECS[d])
  if not possible_overage:
    return face, c

  orig = c
  adj_res = res
  if adj_res % 2:
    c = _down_ap7r(c)
    adj_res += 1
  pent_leading4 = _is_pentagon_base(bc) and _leading_digit(h) == _I
  face, c, moved = _adjust_overage_class2(face, c, adj_res, pent_leading4)
  if moved:
    if _is_pentagon_base(bc):
      while moved:
        face, c, moved = _adjust_overage_class2(face, c, adj_res, False)
    if adj_res != res:
      c = _up_ap7r(c)
  elif adj_res != res:
    c = orig
  return face, c


# --- public API ---

def latlng_to_cell(lat: float, lng: float, res: int) -> int:
  """Cell containing a point given in degrees, like h3.latlng_to_cell."""
  if not 0 <= res <= MAX_RES:
    raise ValueError("resolution out of range")
  if not (math.isfinite(lat) and math.isfinite(lng)):
    raise ValueError("coordinates must be finite")
  face, x, y = _geo_to_hex2d(math.radians(lat), math.radians(lng), res)
  return _face_ijk_to_h3(face, _hex2d_to_ijk(x, y), res)


def cell_to_latlng(h: int) -> tuple[float, float]:
  """Center of a cell in degrees."""
  face, c = _h3_to_face_ijk(h)
  lat, lng = _hex2d_to_geo(*_ijk_to_hex2d(c), face, get_resolution(h))
  return math.degrees(lat), math.degrees(lng)


def cell_to_parent(h: int, res: int) -> int:
  child_res = get_resolution(h)
  if not 0 <= res <= child_res:
    raise ValueError("parent resolution must be between 0 and the cell's resolution")
  h = (h & ~(15 << _RES_OFFSET)) | (res << _RES_OFFSET)
  for r in range(res + 1, child_res + 1):
    h = _set_digit(h, r, 7)
  return h


def grid_disk1(h: int) -> set[int]:
  """The cell and the cells touching it (h3.grid_disk(h, 1)).

  Steps one cell along each of the six ijk axes on the cell's face and maps
  that center back to a cell, so it also works across face edges.
  """
  face, c = _h3_to_face_ijk(h)
  res = get_resolution(h)
  out = {h}
  for u in _UNIT_VECS[1:]:
    x, y = _ijk_to_hex2d(_add(c, u))
    lat, lng = _hex2d_to_geo(x, y, face, res)
    out.add(latlng_to_cell(math.degrees(lat), math.degrees(lng), res))
  return out


def cell_to_str(h: int) -> str:
  return format(h, "x")


def str_to_cell(s: str) -> int:
  return int(s, 16)

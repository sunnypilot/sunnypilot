from opendbc.car.structs import CarParams
from opendbc.car.chrysler.values import CAR

Ecu = CarParams.Ecu


FW_VERSIONS_EXT = {
  CAR.RAM_1500_5TH_GEN: {
    (Ecu.combinationMeter, 0x742, None): [
      b'68453485AC',
      b'68510283AH',
    ],
    (Ecu.eps, 0x75a, None): [
      b'68552791AA',
    ],
    (Ecu.engine, 0x7e0, None): [
      b'05149390AA ',
      b'68378696AI ',
      b'68500631AF',
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'68360085AF',
      b'68360086AL',
      b'68502996AC',
    ],
  },

  CAR.RAM_HD_5TH_GEN: {
    # Added: 2024 RAM 2500 (VIN: 3C6UR4HJ9RG206624)
    # fuzzyFingerprint was True due to these missing entries.
    # combinationMeter: 68628472AC is a new variant (existing DB has 68628474AB)
    # engine: 68617375AB  is a new 2024 firmware (note trailing space)
    # transmission: 68617338AA — RAM HD now reports a transmission ECU on 0x7e1
    #   (this ECU was not present in earlier model years / not previously in the DB)
    (Ecu.combinationMeter, 0x742, None): [
      b'68628472AC',
    ],
    (Ecu.engine, 0x7e0, None): [
      b'68617375AB ',
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'68617338AA',
    ],
  },
}

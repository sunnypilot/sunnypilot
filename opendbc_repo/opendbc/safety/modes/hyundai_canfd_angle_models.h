#pragma once

#include "opendbc/safety/declarations.h"

// Hyundai CAN-FD Angle Steering Vehicle Models
//
// Each angle steering vehicle has unique physics (wheelbase, steer ratio, mass/tire stiffness
// → slip factor) that determine the ISO lateral accel/jerk limits at the steering angle level.
//
// The model ID is passed from openpilot via safety_param_sp bits [4:7] (4 bits = 16 possible models).
// ID 0 is reserved for "unknown/fallback" and uses the baseline (most conservative) model.
//
// The slip_factor is pre-computed from calc_slip_factor(VehicleModel(CP)) in Python.
// See opendbc/car/vehicle_model.py for the formula.

// Model IDs — passed via safety_param_sp bits [4:7]
// These must stay in sync with HyundaiAngleSteeringModel in values.py
enum {
  HYUNDAI_ANGLE_MODEL_BASELINE = 0,             // fallback: uses KIA_SPORTAGE_HEV_2026 (most conservative)
  HYUNDAI_ANGLE_MODEL_KIA_SPORTAGE_HEV_2026,    // 1 - baseline vehicle
  HYUNDAI_ANGLE_MODEL_HYUNDAI_IONIQ_5_PE,        // 2
  HYUNDAI_ANGLE_MODEL_KIA_EV6_2025,              // 3
  HYUNDAI_ANGLE_MODEL_KIA_EV9,                   // 4
  HYUNDAI_ANGLE_MODEL_GENESIS_GV80_2025,         // 5
  HYUNDAI_ANGLE_MODEL_HYUNDAI_SANTA_FE_HEV_5TH,  // 6
  HYUNDAI_ANGLE_MODEL_HYUNDAI_IONIQ_9,           // 7
  HYUNDAI_ANGLE_MODEL_KIA_SORENTO_HEV_4TH_LFA2, // 8
  HYUNDAI_ANGLE_MODEL_GENESIS_GV70_E_2ND_GEN,    // 9
  HYUNDAI_ANGLE_MODEL_HYUNDAI_AZERA_HEV_7TH,     // 10

  HYUNDAI_ANGLE_MODEL_COUNT,  // must be last — used for bounds checking
};

// Bit field extraction for model ID from safety_param_sp
#define HYUNDAI_ANGLE_MODEL_SHIFT 4U
#define HYUNDAI_ANGLE_MODEL_MASK  0xFU  // 4 bits

static inline uint8_t hyundai_get_angle_model_id(uint16_t safety_param_sp) {
  uint8_t model_id = (uint8_t)((safety_param_sp >> HYUNDAI_ANGLE_MODEL_SHIFT) & HYUNDAI_ANGLE_MODEL_MASK);
  return (model_id >= HYUNDAI_ANGLE_MODEL_COUNT) ? HYUNDAI_ANGLE_MODEL_BASELINE : model_id;
}


// Look up the angle steering params for a given model ID.
// Returns the baseline (most conservative) model for unknown IDs.
static const AngleSteeringParams *hyundai_get_angle_params(uint8_t model_id) {
  // Vehicle model parameters for each angle steering platform.
  // slip_factor: calc_slip_factor(VehicleModel(CP))  — see vehicle_model.py
  // steer_ratio: CP.steerRatio
  // wheelbase:   CP.wheelbase
  //
  // Values sourced from opendbc/car/hyundai/values.py CarSpecs definitions.
  static const AngleSteeringParams HYUNDAI_ANGLE_MODELS[] = {
    // [0] BASELINE (fallback) — same as KIA_SPORTAGE_HEV_2026
    [HYUNDAI_ANGLE_MODEL_BASELINE] = {
      .slip_factor = -0.0006085930193026732,
      .steer_ratio = 13.7,
      .wheelbase = 2.756,
    },

    // [1] KIA_SPORTAGE_HEV_2026 — mass=1812, wb=2.756, sr=13.7
    [HYUNDAI_ANGLE_MODEL_KIA_SPORTAGE_HEV_2026] = {
      .slip_factor = -0.0006085930193026732,
      .steer_ratio = 13.7,
      .wheelbase = 2.756,
    },

    // [2] HYUNDAI_IONIQ_5_PE — mass=1948, wb=2.97, sr=14.26
    [HYUNDAI_ANGLE_MODEL_HYUNDAI_IONIQ_5_PE] = {
      .slip_factor = -0.0008688329819908074,
      .steer_ratio = 14.26,
      .wheelbase = 2.97,
    },

    // [3] KIA_EV6_2025 — mass=2055, wb=2.9, sr=16
    [HYUNDAI_ANGLE_MODEL_KIA_EV6_2025] = {
      .slip_factor = -0.000889804937754786,
      .steer_ratio = 16.0,
      .wheelbase = 2.9,
    },

    // [4] KIA_EV9 — mass=2664, wb=3.1, sr=16
    [HYUNDAI_ANGLE_MODEL_KIA_EV9] = {
      .slip_factor = -0.0005410588125765342,
      .steer_ratio = 16.0,
      .wheelbase = 3.1,
    },

    // [5] GENESIS_GV80_2025 — mass=2258, wb=2.95, sr=14.14
    [HYUNDAI_ANGLE_MODEL_GENESIS_GV80_2025] = {
      .slip_factor = -0.0005685702046115589,
      .steer_ratio = 14.14,
      .wheelbase = 2.95,
    },

    // [6] HYUNDAI_SANTA_FE_HEV_5TH_GEN — mass=2035, wb=2.81, sr=13.72
    [HYUNDAI_ANGLE_MODEL_HYUNDAI_SANTA_FE_HEV_5TH] = {
      .slip_factor = -0.00059689759884299,
      .steer_ratio = 13.72,
      .wheelbase = 2.81,
    },

    // [7] HYUNDAI_IONIQ_9 — mass=2700, wb=3.13, sr=16.02
    [HYUNDAI_ANGLE_MODEL_HYUNDAI_IONIQ_9] = {
      .slip_factor = -0.0005358728714041771,
      .steer_ratio = 16.02,
      .wheelbase = 3.13,
    },

    // [8] KIA_SORENTO_HEV_4TH_GEN_LFA2 — mass=1970, wb=2.814, sr=13.27
    [HYUNDAI_ANGLE_MODEL_KIA_SORENTO_HEV_4TH_LFA2] = {
      .slip_factor = -0.0009169985667169079,
      .steer_ratio = 13.27,
      .wheelbase = 2.814,
    },

    // [9] GENESIS_GV70_ELECTRIFIED_2ND_GEN — mass=2260, wb=2.87, sr=17.1
    [HYUNDAI_ANGLE_MODEL_GENESIS_GV70_E_2ND_GEN] = {
      .slip_factor = -0.0005844189054075528,
      .steer_ratio = 17.1,
      .wheelbase = 2.87,
    },

    // [10] HYUNDAI_AZERA_HEV_7TH_GEN — mass=1720, wb=2.895, sr=13.5
    [HYUNDAI_ANGLE_MODEL_HYUNDAI_AZERA_HEV_7TH] = {
      .slip_factor = -0.0005793721359940619,
      .steer_ratio = 13.5,
      .wheelbase = 2.895,
    },
  };
  // const AngleSteeringParams *result_model;
  //
  // if (model_id >= HYUNDAI_ANGLE_MODEL_COUNT) {
  //   result_model = &HYUNDAI_ANGLE_MODELS[HYUNDAI_ANGLE_MODEL_BASELINE];
  // } else {
  //   result_model = &HYUNDAI_ANGLE_MODELS[model_id];
  // }
  
  return &HYUNDAI_ANGLE_MODELS[model_id];
}

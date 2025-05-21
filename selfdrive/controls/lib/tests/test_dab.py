import pytest
from cereal import log
from openpilot.sunnypilot.selfdrive.controls.lib.dab.dab import (
    DynamicAccelerationBoost, DabInputs, LeadData, PHANTOM_BRAKE_SPEED
)


def test_dab_basic():
    helper = DynamicAccelerationBoost()
    inputs = DabInputs(
        v_ego=10.0,
        a_ego=0.0,
        v_set=15.0,
        output_a_mpc=0.5,
        output_a_e2e=0.5,
        v_desired=[10.0] * 5,
        allow_throttle=True,
        radar_lead=LeadData(False),
        personality=log.LongitudinalPersonality.standard,
    )
    out = helper.compute({}, inputs)
    assert isinstance(out.a_final, float)
    assert out.a_final >= 0.0


def test_dab_jerk_limit():
    helper = DynamicAccelerationBoost()
    inputs = DabInputs(
        v_ego=0.0,
        a_ego=0.0,
        v_set=10.0,
        output_a_mpc=2.0,
        output_a_e2e=2.0,
        v_desired=[10.0] * 5,
        allow_throttle=True,
        radar_lead=LeadData(False),
        personality=log.LongitudinalPersonality.standard,
    )
    out1 = helper.compute({}, inputs)
    inputs.output_a_mpc = 0.0
    inputs.output_a_e2e = 0.0
    out2 = helper.compute({}, inputs)
    assert abs(out2.a_final - out1.a_final) <= 0.1
import numpy as np
from cereal import log
from openpilot.sunnypilot.selfdrive.controls.lib.dab.dab import (
    DynamicAccelerationBoost, DabInputs, DabOutputs, LeadData, CurvatureData, JERK_LIMIT_BP, JERK_LIMIT_VALS, DT_MDL
)


def make_inputs():
    return DabInputs(
        v_ego=10.0,
        a_ego=0.0,
        v_set=15.0,
        output_a_target=1.0,
        v_desired=[10.0]*5,
        allow_throttle=True,
        radar_lead=LeadData(False, 0.0, 0.0, 0.0),
        model_lead=LeadData(False, 0.0, 0.0, 0.0),
        curvature=CurvatureData(0.0, [], [], [], []),
        personality=log.LongitudinalPersonality.standard,
    )


def test_compute_returns_dataclass():
    dab = DynamicAccelerationBoost()
    out = dab.compute(make_inputs())
    assert isinstance(out, DabOutputs)


def test_apply_jerk_limit():
    dab = DynamicAccelerationBoost()
    a_raw = 2.0
    v_ego = 30.0
    expected_delta = float(np.interp(v_ego, JERK_LIMIT_BP, JERK_LIMIT_VALS)) * DT_MDL
    dab._prev_a_final = 0.0
    limited = dab._apply_jerk_limit(a_raw, v_ego)
    assert abs(limited - dab._prev_a_final) <= expected_delta + 1e-6


def test_catchup_overrides_negative_planner():
    helper = DynamicAccelerationBoost()
    inputs = DabInputs(
        v_ego=10.0,
        a_ego=0.0,
        v_set=15.0,
        output_a_mpc=-0.5,
        output_a_e2e=-0.5,
        v_desired=[10.0] * 5,
        allow_throttle=True,
        radar_lead=LeadData(True, 60.0, 0.0, 10.0),
        personality=log.LongitudinalPersonality.standard,
    )
    out = helper.compute({}, inputs)
    assert out.weight > 0.0
    assert out.a_final > -0.5


def test_phantom_brake_gate_speed_threshold():
    helper = DynamicAccelerationBoost()
    inputs = DabInputs(
        v_ego=PHANTOM_BRAKE_SPEED - 1.0,
        a_ego=0.0,
        v_set=30.0,
        output_a_mpc=0.0,
        output_a_e2e=-1.0,
        v_desired=[30.0] * 5,
        allow_throttle=True,
        radar_lead=LeadData(False),
        personality=log.LongitudinalPersonality.standard,
    )

    helper.compute({}, inputs)
    assert helper._phantom_time == 0.0

    inputs.v_ego = PHANTOM_BRAKE_SPEED + 1.0
    helper.compute({}, inputs)
    assert helper._phantom_time > 0.0

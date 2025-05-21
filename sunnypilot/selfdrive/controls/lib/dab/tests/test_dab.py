from cereal import log
from openpilot.sunnypilot.selfdrive.controls.lib.dab.dab import (
    LeadData, CurvatureData, DabInputs, DabOutputs, DynamicAccelerationBoost,
)
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N


def make_inputs():
    curvature = CurvatureData(0.0, [0.0, 1.0, 2.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [10.0, 10.0, 10.0])
    return DabInputs(
        v_ego=5.0,
        a_ego=0.0,
        v_set=10.0,
        output_a_target=0.5,
        output_a_mpc=0.5,
        output_a_e2e=0.5,
        v_desired=[10.0] * CONTROL_N,
        allow_throttle=True,
        radar_lead=LeadData(False),
        model_lead=LeadData(False),
        curvature=curvature,
        personality=log.LongitudinalPersonality.standard,
    )


def test_dataclasses_basic():
    ld = LeadData(True, 5.0, -1.0, 4.0)
    assert ld.status and ld.dRel == 5.0
    cd = CurvatureData(0.1, [0.0], [0.0], [0.0], [1.0])
    assert cd.desired == 0.1
    inputs = make_inputs()
    assert isinstance(inputs, DabInputs)


def test_compute_returns_outputs(monkeypatch):
    dab = DynamicAccelerationBoost()
    monkeypatch.setattr(dab, "_update_gate_toggles", lambda: None)
    out = dab.compute({}, make_inputs())
    assert isinstance(out, DabOutputs)


def test_curviness_property(monkeypatch):
    dab = DynamicAccelerationBoost()
    monkeypatch.setattr(dab, "_update_gate_toggles", lambda: None)
    dab.compute({}, make_inputs())
    assert isinstance(dab.curviness, float)

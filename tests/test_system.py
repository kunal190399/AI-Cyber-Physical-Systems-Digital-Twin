import json
from cps_twin.cli import run_simulation
from cps_twin.models import ControlCommand
from cps_twin.perception import HazardDetector
from cps_twin.safety import SafetySupervisor


def test_safety_override_stops_robot_for_hazard():
    supervisor = SafetySupervisor(hazard_threshold=0.7)
    command = supervisor.apply(ControlCommand(0.5, 0.1, 2), 0.9, 3.0)
    assert command.safety_override
    assert command.linear == 0.0
    assert command.angular == 0.0
    assert "hazard_probability_threshold" in command.override_reason


def test_safety_override_stops_robot_near_obstacle():
    command = SafetySupervisor().apply(ControlCommand(0.5, 0.0, 0), 0.1, 0.2)
    assert command.safety_override
    assert command.linear == 0.0


def test_detector_returns_probability():
    detector = HazardDetector(seed=3)
    probability = detector.predict_probability(1400, 45, 0.8)
    assert 0.0 <= probability <= 1.0


def test_simulation_is_reproducible(tmp_path):
    a = run_simulation(25, seed=11, output=str(tmp_path / "a.jsonl"))
    b = run_simulation(25, seed=11, output=str(tmp_path / "b.jsonl"))
    assert a == b
    first = json.loads((tmp_path / "a.jsonl").read_text().splitlines()[0])
    assert "hazard_probability" in first
    assert "safety_override" in first


def test_simulation_respects_facility_bounds():
    records = run_simulation(120, seed=5, output=None)
    assert all(0.15 <= r["pose_x"] <= 9.85 for r in records)
    assert all(0.15 <= r["pose_y"] <= 9.85 for r in records)

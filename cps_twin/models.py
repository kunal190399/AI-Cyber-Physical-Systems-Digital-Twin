"""Shared data structures for the simulated CPS."""
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RobotState:
    x: float = 1.0
    y: float = 1.0
    yaw: float = 0.0
    linear_velocity: float = 0.0
    angular_velocity: float = 0.0


@dataclass
class SensorReading:
    obstacle_range_m: float
    gas_ppm: float
    temperature_c: float
    vibration_g: float


@dataclass
class ControlCommand:
    linear: float
    angular: float
    waypoint_index: int
    safety_override: bool = False
    override_reason: str = ""


@dataclass
class Telemetry:
    sim_time_s: float
    pose_x: float
    pose_y: float
    yaw_rad: float
    commanded_linear_mps: float
    commanded_angular_rps: float
    obstacle_range_m: float
    gas_ppm: float
    temperature_c: float
    vibration_g: float
    hazard_probability: float
    hazard_detected: bool
    safety_override: bool
    override_reason: str
    waypoint_index: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

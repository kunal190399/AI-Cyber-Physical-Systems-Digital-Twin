"""Independent safety layer that can override autonomy commands."""
from cps_twin.models import ControlCommand


class SafetySupervisor:
    def __init__(self, hazard_threshold: float = 0.72, min_obstacle_range_m: float = 0.55) -> None:
        self.hazard_threshold = hazard_threshold
        self.min_obstacle_range_m = min_obstacle_range_m

    def apply(self, command: ControlCommand, hazard_probability: float, obstacle_range_m: float) -> ControlCommand:
        reasons = []
        if hazard_probability >= self.hazard_threshold:
            reasons.append("hazard_probability_threshold")
        if obstacle_range_m <= self.min_obstacle_range_m:
            reasons.append("obstacle_proximity")
        if reasons:
            return ControlCommand(0.0, 0.0, command.waypoint_index, True, "+".join(reasons))
        return command

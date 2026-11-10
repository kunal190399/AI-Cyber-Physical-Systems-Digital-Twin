"""Deterministic 2-D industrial inspection-robot simulation."""
import math
import numpy as np
from cps_twin.models import ControlCommand, RobotState, SensorReading


class FacilitySimulation:
    def __init__(self, seed: int = 7, dt: float = 0.1) -> None:
        self.rng = np.random.default_rng(seed)
        self.dt = dt
        self.time = 0.0
        self.robot = RobotState()
        self.waypoints = [(8.0, 1.0), (8.0, 8.0), (1.0, 8.0), (1.0, 1.0)]
        self.waypoint_index = 0
        self.obstacles = [(4.5, 3.2, 0.8), (6.0, 6.0, 0.7), (2.5, 5.0, 0.6)]
        self.hazard = (6.8, 3.0)

    def sense(self) -> SensorReading:
        x, y = self.robot.x, self.robot.y
        obstacle_range = 8.0
        for ox, oy, radius in self.obstacles:
            obstacle_range = min(obstacle_range, max(0.0, math.hypot(x - ox, y - oy) - radius))
        hazard_distance = math.hypot(x - self.hazard[0], y - self.hazard[1])
        plume = 1250.0 * math.exp(-0.5 * (hazard_distance / 1.6) ** 2)
        gas = max(0.0, 390.0 + plume + self.rng.normal(0, 35))
        temp = 23.0 + 17.0 * math.exp(-0.5 * (hazard_distance / 1.9) ** 2) + self.rng.normal(0, 1.2)
        vibration = max(0.0, 0.12 + 0.55 * max(0.0, 1.2 - obstacle_range) + self.rng.normal(0, 0.035))
        return SensorReading(float(obstacle_range), float(gas), float(temp), float(vibration))

    def plan(self) -> ControlCommand:
        tx, ty = self.waypoints[self.waypoint_index]
        dx, dy = tx - self.robot.x, ty - self.robot.y
        distance = math.hypot(dx, dy)
        if distance < 0.35:
            self.waypoint_index = (self.waypoint_index + 1) % len(self.waypoints)
            tx, ty = self.waypoints[self.waypoint_index]
            dx, dy = tx - self.robot.x, ty - self.robot.y
        target_yaw = math.atan2(dy, dx)
        yaw_error = (target_yaw - self.robot.yaw + math.pi) % (2 * math.pi) - math.pi
        angular = float(np.clip(1.8 * yaw_error, -1.2, 1.2))
        linear = 0.65 if abs(yaw_error) < 0.65 else 0.12
        return ControlCommand(linear, angular, self.waypoint_index)

    def step(self, command: ControlCommand) -> RobotState:
        dt = self.dt
        self.robot.yaw = (self.robot.yaw + command.angular * dt + math.pi) % (2 * math.pi) - math.pi
        nx = self.robot.x + command.linear * math.cos(self.robot.yaw) * dt
        ny = self.robot.y + command.linear * math.sin(self.robot.yaw) * dt
        # Keep the robot inside the 10 m x 10 m facility boundary.
        self.robot.x = float(np.clip(nx, 0.15, 9.85))
        self.robot.y = float(np.clip(ny, 0.15, 9.85))
        self.robot.linear_velocity = command.linear
        self.robot.angular_velocity = command.angular
        self.time += dt
        return self.robot

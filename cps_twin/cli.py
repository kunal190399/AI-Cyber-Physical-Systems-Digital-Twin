"""Run the complete closed-loop CPS simulation from the command line."""
import argparse
from cps_twin.models import Telemetry
from cps_twin.perception import HazardDetector
from cps_twin.safety import SafetySupervisor
from cps_twin.simulator import FacilitySimulation
from cps_twin.telemetry import TelemetryWriter


def run_simulation(steps: int = 600, seed: int = 7, output: str | None = "data/run.jsonl", mqtt: str | None = None) -> list[dict]:
    sim = FacilitySimulation(seed=seed)
    detector = HazardDetector(seed=seed)
    safety = SafetySupervisor()
    writer = TelemetryWriter(output=output, mqtt_host=mqtt)
    records: list[dict] = []
    try:
        for _ in range(steps):
            reading = sim.sense()
            probability = detector.predict_probability(reading.gas_ppm, reading.temperature_c, reading.vibration_g)
            proposed = sim.plan()
            safe_command = safety.apply(proposed, probability, reading.obstacle_range_m)
            robot = sim.step(safe_command)
            record = Telemetry(
                sim_time_s=round(sim.time, 3), pose_x=round(robot.x, 4), pose_y=round(robot.y, 4),
                yaw_rad=round(robot.yaw, 4), commanded_linear_mps=safe_command.linear,
                commanded_angular_rps=safe_command.angular, obstacle_range_m=round(reading.obstacle_range_m, 3),
                gas_ppm=round(reading.gas_ppm, 2), temperature_c=round(reading.temperature_c, 2),
                vibration_g=round(reading.vibration_g, 3), hazard_probability=round(probability, 4),
                hazard_detected=probability >= safety.hazard_threshold, safety_override=safe_command.safety_override,
                override_reason=safe_command.override_reason, waypoint_index=safe_command.waypoint_index,
            ).to_dict()
            records.append(record)
            writer.write(record)
    finally:
        writer.close()
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AI CPS digital-twin simulation")
    parser.add_argument("--steps", type=int, default=600)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", default="data/run.jsonl")
    parser.add_argument("--mqtt", default=None, help="Optional MQTT broker hostname")
    args = parser.parse_args()
    records = run_simulation(args.steps, args.seed, args.output, args.mqtt)
    overrides = sum(bool(r["safety_override"]) for r in records)
    alarms = sum(bool(r["hazard_detected"]) for r in records)
    print(f"Completed {len(records)} steps; alarms={alarms}; safety overrides={overrides}; output={args.output}")


if __name__ == "__main__":
    main()

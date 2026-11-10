#!/usr/bin/env python3
"""ROS 2 adapter: replay JSONL telemetry on /cps/robot/telemetry.

Run inside a sourced ROS 2 environment with rclpy and std_msgs installed.
"""
import argparse
import json
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TelemetryReplayNode(Node):
    def __init__(self, input_path: str, rate_hz: float = 10.0) -> None:
        super().__init__("cps_twin_telemetry_replay")
        self.publisher = self.create_publisher(String, "/cps/robot/telemetry", 10)
        with open(input_path, encoding="utf-8") as stream:
            self.records = [line.strip() for line in stream if line.strip()]
        self.index = 0
        self.timer = self.create_timer(1.0 / rate_hz, self.publish_next)
        self.get_logger().info(f"Loaded {len(self.records)} telemetry records")

    def publish_next(self) -> None:
        if self.index >= len(self.records):
            self.get_logger().info("Replay complete")
            self.destroy_timer(self.timer)
            return
        # Validate JSON before publishing to avoid emitting malformed messages.
        record = json.loads(self.records[self.index])
        message = String()
        message.data = json.dumps(record)
        self.publisher.publish(message)
        self.index += 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/run.jsonl")
    parser.add_argument("--rate", type=float, default=10.0)
    args = parser.parse_args()
    rclpy.init()
    node = TelemetryReplayNode(args.input, args.rate)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

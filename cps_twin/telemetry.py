"""Structured telemetry logging and optional MQTT publishing."""
import json
from pathlib import Path
from typing import Any


class TelemetryWriter:
    def __init__(self, output: str | None = None, mqtt_host: str | None = None) -> None:
        self.path = Path(output) if output else None
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("", encoding="utf-8")
        self.client: Any = None
        if mqtt_host:
            try:
                import paho.mqtt.client as mqtt
            except ImportError as exc:
                raise RuntimeError("Install optional dependency with: pip install -e '.[mqtt]'") from exc
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.client.connect(mqtt_host, 1883, 30)
            self.client.loop_start()

    def write(self, record: dict[str, Any]) -> None:
        payload = json.dumps(record, separators=(",", ":"))
        if self.path:
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(payload + "\n")
        if self.client:
            self.client.publish("cps/robot/telemetry", payload, qos=0)

    def close(self) -> None:
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

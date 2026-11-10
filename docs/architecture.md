# System architecture and validation notes

## Closed-loop signal path

1. The facility simulator advances a 2-D robot model at a fixed 100 ms step.
2. Range, gas-like concentration, temperature and vibration sensors generate noisy observations.
3. A Random Forest classifier estimates the probability of an abnormal multi-sensor condition.
4. A waypoint controller proposes linear and angular velocities.
5. An independent safety supervisor can replace the proposed velocities with zero.
6. Robot dynamics apply the final command; the next sensor cycle closes the feedback loop.
7. A structured record is written to JSONL and optionally published over MQTT.

## State and interface contracts

- Pose: metres and radians in a facility-local 2-D frame.
- Linear velocity: m/s; angular velocity: rad/s.
- Sensor channels: obstacle range in metres, gas-like reading in ppm-equivalent synthetic units, temperature in °C and vibration in g-equivalent synthetic units.
- Time: monotonically increasing simulation seconds.
- Telemetry: one JSON object per simulation step.

## Safety concept

The planner is not trusted to enforce every safety constraint. The safety supervisor independently checks the ML hazard score and obstacle proximity. When either configured threshold is crossed, it issues a zero-velocity command and records the reason. This is a demonstrator pattern only: thresholds are illustrative, and the model is not safety-certified.

## Verification strategy

The automated tests verify deterministic seeded execution, probability bounds, safety override behaviour, telemetry schema and facility boundary constraints. Further engineering validation should include:

- scenario-based coverage of obstacle layouts and hazard source locations;
- sensor noise, bias, dropout and stuck-at fault injection;
- latency and message-loss measurements for MQTT and ROS 2;
- controller stability and stopping-distance analysis;
- independent test data for classifier calibration and false-negative analysis;
- software-in-the-loop, hardware-in-the-loop and physical-robot tests before any real-world use.

## Extension path

A natural next stage is to replace the simplified plant with Gazebo, publish sensor topics using ROS 2 messages, integrate SLAM Toolbox and Nav2, and bridge telemetry to the dashboard. Physical sensors and actuators should be introduced only with calibrated interfaces, emergency-stop design, risk assessment and supervised testing.

"""Train and run a compact anomaly detector on synthetic sensor features."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier


class HazardDetector:
    """A reproducible ML baseline; never use this synthetic model for real safety."""

    def __init__(self, seed: int = 7) -> None:
        rng = np.random.default_rng(seed)
        normal = np.column_stack([
            rng.normal(420, 65, 1200), rng.normal(24, 3, 1200),
            rng.normal(0.15, 0.07, 1200),
        ])
        hazardous = np.column_stack([
            rng.normal(1050, 180, 500), rng.normal(39, 7, 500),
            rng.normal(0.65, 0.2, 500),
        ])
        x = np.clip(np.vstack([normal, hazardous]), [0, -10, 0], [2500, 100, 3])
        y = np.r_[np.zeros(len(normal)), np.ones(len(hazardous))]
        self.model = RandomForestClassifier(n_estimators=100, max_depth=7, random_state=seed, class_weight="balanced")
        self.model.fit(x, y)

    def predict_probability(self, gas_ppm: float, temperature_c: float, vibration_g: float) -> float:
        features = np.array([[gas_ppm, temperature_c, vibration_g]])
        return float(self.model.predict_proba(features)[0, 1])

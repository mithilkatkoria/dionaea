"""Synthetic *event* stream generation, with fully known anomaly intervals.

This is a teaching model, NOT measured Venus flytrap physiology and NOT
real-world sensor data. Every sample is one discrete time step.
"""
from dataclasses import asdict, dataclass
import random


@dataclass(frozen=True)
class Scenario:
    seed: int = 42
    length: int = 360
    noise: float = 0.09
    signal: float = 0.67
    burst: float = 0.006
    episode_count: int = 5
    episode_length: int = 17

    def validate(self) -> None:
        if not (120 <= self.length <= 1200):
            raise ValueError("length must be 120..1200")
        for label in ("noise", "signal", "burst"):
            value = getattr(self, label)
            if not (0 <= value <= 1):
                raise ValueError(f"{label} must be between 0 and 1")
        if not (1 <= self.episode_count <= 12):
            raise ValueError("episode_count must be 1..12")
        if not (4 <= self.episode_length <= 60):
            raise ValueError("episode_length must be 4..60")
        if (self.episode_count + 1) * (self.episode_length + 4) >= self.length:
            raise ValueError("episodes are too densely packed")


def make_stream(config: Scenario) -> dict:
    """Make independent seeded trials; each interval is [start, end).

    Within an anomaly interval, P(event=1) = signal. Outside, background
    Bernoulli noise is generated; occasional correlated noise bursts model
    a challenge to detectors requiring multiple nearby events.
    """
    config.validate()
    rng = random.Random(config.seed)
    gap = config.length // (config.episode_count + 1)
    episodes = []
    for i in range(1, config.episode_count + 1):
        jitter = rng.randint(-max(1, gap // 7), max(1, gap // 7))
        start = i * gap + jitter
        start = max(10, min(config.length - config.episode_length - 2, start))
        if episodes:
            start = max(start, episodes[-1][1] + 3)
        episodes.append((start, start + config.episode_length))
    if episodes[-1][1] > config.length:
        raise ValueError("episodes exceed stream length")

    truths = [any(a <= t < b for a, b in episodes) for t in range(config.length)]
    values = []
    remaining_burst = 0
    for is_signal in truths:
        if is_signal:
            values.append(int(rng.random() < config.signal))
            remaining_burst = 0
        else:
            if remaining_burst == 0 and rng.random() < config.burst:
                remaining_burst = rng.randint(3, 5)
            if remaining_burst:
                values.append(int(rng.random() < 0.88))
                remaining_burst -= 1
            else:
                values.append(int(rng.random() < config.noise))
    return {
        "config": asdict(config),
        "events": values,
        "episodes": [{"start": a, "end": b} for a, b in episodes],
        "truth": [int(v) for v in truths],
    }

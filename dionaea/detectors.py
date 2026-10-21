"""Four transparent, causal, online detectors.

No algorithm has access to the ground-truth intervals. Every method uses
exactly the same event stream and a shared alarm cooldown.
"""
from collections import deque
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Settings:
    window: int = 6
    count: int = 3
    alpha: float = 0.80
    threshold: float = 1.60
    cooldown: int = 6

    def validate(self):
        if not (1 <= self.window <= 30):
            raise ValueError("window must be 1..30")
        if not (2 <= self.count <= 8):
            raise ValueError("count must be 2..8")
        if not (0.0 <= self.alpha < 1.0):
            raise ValueError("alpha must be >= 0 and < 1")
        if not (0.1 <= self.threshold <= 8.0):
            raise ValueError("threshold must be between 0.1 and 8.0")
        if not (0 <= self.cooldown <= 40):
            raise ValueError("cooldown must be 0..40")


METHODS = ("single", "pair", "count", "leaky")
NAMES = {
    "single": "Single event",
    "pair": "Two events / timed window",
    "count": "Sliding-window count",
    "leaky": "Leaky evidence accumulator",
}


def detect(events: list[int], method: str, settings: Settings) -> dict:
    """Process events in time order, using current and previous events only.

    A trigger at t causes cooldown for times t+1 .. t+cooldown.
    Detector state is cleared on a trigger to avoid artificially inflated
    confidence; this is a modelling choice, not a plant physiology claim.
    """
    if method not in METHODS:
        raise ValueError(f"Unknown detector {method}")
    settings.validate()
    alarms, confidence = [], []
    next_armed = 0
    last_touch = None
    recent = deque()
    score = 0.0
    for t, bit in enumerate(events):
        if bit not in (0, 1):
            raise ValueError("All event values must be 0 or 1")
        if t < next_armed:
            confidence.append(0.0)
            continue
        fired = False
        if method == "single":
            score = float(bit)
            fired = bool(bit)
        elif method == "pair":
            if last_touch is not None and t - last_touch > settings.window:
                last_touch = None
            if bit:
                if last_touch is not None:
                    fired = True
                    last_touch = None
                else:
                    last_touch = t
            score = float(last_touch is not None) if not fired else 2.0
        elif method == "count":
            while recent and t - recent[0] > settings.window:
                recent.popleft()
            if bit:
                recent.append(t)
            score = float(len(recent))
            fired = len(recent) >= settings.count
        else:
            score = settings.alpha * score + bit
            fired = score >= settings.threshold
        confidence.append(round(score, 5))
        if fired:
            alarms.append(t)
            next_armed = t + settings.cooldown + 1
            last_touch = None
            recent.clear()
            score = 0.0
    return {"method": method, "name": NAMES[method], "alarms": alarms,
            "confidence": confidence, "settings": asdict(settings)}

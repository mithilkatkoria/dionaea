"""Episode-level evaluation: first alarm in each episode = TP.

Other alarms (including duplicates within an already hit episode) = FP.
A missed episode = FN. Delay = first alarm time minus episode start.
This is NOT the official Numenta Anomaly Benchmark (NAB) score.
"""
from statistics import mean
from .detectors import METHODS, Settings, detect
from .model import Scenario, make_stream


def evaluate(alarms: list[int], episodes: list[dict], length: int) -> dict:
    if alarms != sorted(alarms) or len(set(alarms)) != len(alarms):
        raise ValueError("alarms must be sorted and distinct")
    matched = set()
    latencies = []
    false_alarms = []
    for alarm in alarms:
        index = next((i for i, e in enumerate(episodes)
                      if e["start"] <= alarm < e["end"]), None)
        if index is not None and index not in matched:
            matched.add(index)
            latencies.append(alarm - episodes[index]["start"])
        else:
            false_alarms.append(alarm)
    tp = len(matched)
    fn = len(episodes) - tp
    fp = len(false_alarms)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    # A deliberately explicit cost model: miss = 4, false alarm = 2,
    # one step of detection delay = 0.03. These weights are a hypothesis.
    cost = 4 * fn + 2 * fp + 0.03 * sum(latencies)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(precision, 4),
            "recall": round(recall, 4), "f1": round(f1, 4),
            "mean_delay": round(mean(latencies), 3) if latencies else None,
            "false_alarms_per_100_steps": round(100 * fp / length, 3),
            "cost": round(cost, 3), "false_alarm_times": false_alarms}


def simulate(config: Scenario, settings: Settings) -> dict:
    stream = make_stream(config)
    results = {}
    for name in METHODS:
        record = detect(stream["events"], name, settings)
        record["metrics"] = evaluate(record["alarms"], stream["episodes"], config.length)
        results[name] = record
    stream["detectors"] = results
    return stream

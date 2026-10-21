"""Repeatable train/test evaluation with model selection done on train only.

Command: python -m dionaea.benchmark
Output: experiments/benchmark_results.json and experiments/RESULTS.md
"""
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
from pathlib import Path
from statistics import mean, stdev
from .detectors import METHODS, Settings, detect
from .evaluate import evaluate
from .model import Scenario, make_stream

ROOT = Path(__file__).resolve().parents[1]
TRAIN_SEEDS = tuple(range(1000, 1015))
TEST_SEEDS = tuple(range(2000, 2040))

REGIMES = {
    "moderate / independent noise": dict(noise=0.09, signal=0.67, burst=0.0),
    "sparse true events": dict(noise=0.09, signal=0.30, burst=0.0),
    "high background noise": dict(noise=0.23, signal=0.67, burst=0.0),
    "correlated noise bursts": dict(noise=0.06, signal=0.67, burst=0.027),
}


def candidates(method: str) -> list[Settings]:
    default = Settings()
    if method == "single":
        return [default]
    if method == "pair":
        return [replace(default, window=w) for w in (2, 4, 6, 9, 12)]
    if method == "count":
        return [replace(default, window=w, count=c)
                for w in (4, 7, 10, 14) for c in (2, 3, 4)]
    return [replace(default, alpha=a, threshold=q)
            for a in (0.55, 0.70, 0.82, 0.90)
            for q in (1.5, 1.9, 2.3, 2.8)]


def record(method: str, settings: Settings, stream: dict) -> dict:
    alarms = detect(stream["events"], method, settings)["alarms"]
    return evaluate(alarms, stream["episodes"], len(stream["events"]))


def choose_train_settings(method: str, train_streams: list[dict]) -> tuple[Settings, float]:
    options = candidates(method)
    scores = []
    for settings in options:
        costs = [record(method, settings, s)["cost"] for s in train_streams]
        scores.append((mean(costs), settings))
    # Explicitly resolve ties by original candidate order (stable min).
    return min(scores, key=lambda pair: pair[0])[1], min(s[0] for s in scores)


def run() -> dict:
    train_streams = [make_stream(Scenario(seed=seed, **REGIMES["moderate / independent noise"]))
                     for seed in TRAIN_SEEDS]
    trained = {method: choose_train_settings(method, train_streams) for method in METHODS}
    results = {
        "methodology": "Synthetic binary event streams; 15 independent training seeds; "
                       "40 held-out seeds per regime; episodes not samples are the positives. "
                       "Settings selected once on moderate-noise training scenarios and fixed thereafter.",
        "train_seeds": [TRAIN_SEEDS[0], TRAIN_SEEDS[-1]],
        "test_seeds": [TEST_SEEDS[0], TEST_SEEDS[-1]],
        "test_regimes": REGIMES,
        "cost_definition": "4*FN + 2*FP + 0.03*sum(first_detection_delays), lower is better; subjective weights",
        "selected_settings": {m: asdict(trained[m][0]) for m in METHODS},
        "train_mean_cost": {m: round(trained[m][1], 3) for m in METHODS},
        "results": {},
    }
    for regime, properties in REGIMES.items():
        streams = [make_stream(Scenario(seed=seed, **properties)) for seed in TEST_SEEDS]
        summary = {}
        for method in METHODS:
            records = [record(method, trained[method][0], s) for s in streams]
            metric_keys = ("tp", "fp", "fn", "precision", "recall", "f1", "cost", "false_alarms_per_100_steps")
            row = {k: round(mean(r[k] for r in records), 3) for k in metric_keys}
            row["cost_sd"] = round(stdev(r["cost"] for r in records), 3)
            available_latencies = [r["mean_delay"] for r in records if r["mean_delay"] is not None]
            row["mean_delay_detected_only"] = round(mean(available_latencies), 3) if available_latencies else None
            summary[method] = row
        results["results"][regime] = summary
    return results


def markdown_report(data: dict) -> str:
    lines = ["# Dionaea — benchmark results", "", "## Experimental setup", "",
             data["methodology"], "", "**No external dataset used; no NAB score is claimed.**", "",
             "Training and test seeds are disjoint. Lower cost is better, but the cost weights are a research choice.", "",
             "## Selected parameters (trained on moderate noise only)", "", "```json",
             json.dumps(data["selected_settings"], indent=2), "```", "", "## Held-out results", ""]
    for regime, rows in data["results"].items():
        lines.extend([f"### {regime}", "",
                      "| Detector | Recall | Precision | F1 | False alerts (mean) | Cost (mean ± SD) |",
                      "|---|---:|---:|---:|---:|---:|"])
        for method, values in rows.items():
            lines.append(f"| {method} | {values['recall']:.3f} | {values['precision']:.3f} | "
                         f"{values['f1']:.3f} | {values['fp']:.2f} | "
                         f"{values['cost']:.2f} ± {values['cost_sd']:.2f} |")
        lines.append("")
    lines.extend(["## What to investigate yourself", "",
                  "- Does the detector ranking reverse when anomalies have very low event probability?",
                  "- How do bursty false signals defeat algorithms that count nearby events?",
                  "- Change the penalty on false positives and re-tune; do the rankings change?",
                  "- Investigate whether increasing the cooldown changes the ranking.", "",
                  "## Honest limitations", "",
                  "This is an illustrative synthetic experiment, not a proof of general superiority. "
                  "The parameters were chosen using simulated events; the evaluation costs are subjective. "
                  "All detector designs are existing general ideas, not new CS inventions. "
                  "No statistical significance test or real-world validation has been performed. "
                  "The plant biology is an inspiration, not the implementation of a biological model.", ""])
    return "\n".join(lines)


def main():
    data = run()
    path = ROOT / "experiments"
    path.mkdir(exist_ok=True)
    (path / "benchmark_results.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (path / "RESULTS.md").write_text(markdown_report(data), encoding="utf-8")
    for regime, values in data["results"].items():
        best = min(values, key=lambda m: values[m]["cost"])
        print(f"{regime}: lowest mean cost {best} ({values[best]['cost']})")
    print("Wrote experiments/benchmark_results.json and experiments/RESULTS.md")


if __name__ == "__main__":
    main()

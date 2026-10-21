"""Build a fixed teaching trace using the production Python detectors."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
from dionaea.detectors import METHODS, Settings, detect

ROOT = Path(__file__).resolve().parents[1]


def build_example():
    events = [1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0]
    settings = Settings(window=3, count=3, alpha=.8, threshold=1.6, cooldown=0)
    return {"kind": "teaching_example", "description": "A handmade binary sequence, not measured data. No truth labels or performance scores.",
            "events": events, "settings": asdict(settings),
            "detectors": {method: detect(events, method, settings) for method in METHODS}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "public/learning-example.json"
    content = json.dumps(build_example(), indent=2) + "\n"
    if args.check:
        if path.read_text(encoding="utf-8") != content:
            raise SystemExit("Teaching trace is stale. Run python -m scripts.build_learning_example")
        print("PASS teaching trace matches the Python engine")
    else:
        path.write_text(content, encoding="utf-8", newline="\n")
        print("Wrote public/learning-example.json using the unchanged Python engine")


if __name__ == "__main__":
    main()

"""Fail if a benchmark rerun changes either published result file."""
from hashlib import sha256
from pathlib import Path
from dionaea.benchmark import main

paths = [Path("experiments") / name for name in ("RESULTS.md", "benchmark_results.json")]
before = {p: p.read_bytes() for p in paths}
main()
for path in paths:
    actual = path.read_bytes()
    if actual != before[path]:
        raise SystemExit(f"Benchmark changed {path}; investigate before publishing.")
    print(f"UNCHANGED {path}: {sha256(actual).hexdigest()}")

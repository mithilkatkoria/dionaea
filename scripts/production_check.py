"""Verify a real HTTPS deployment against the local Python engine."""
import argparse
import json
from pathlib import Path
import urllib.request
import urllib.error
from dionaea.evaluate import simulate
from dionaea.detectors import Settings
from dionaea.model import Scenario
from scripts.build_learning_example import build_example

parser = argparse.ArgumentParser()
parser.add_argument("url")
parser.add_argument("--output", default="test-results/api-production.json")
args = parser.parse_args()
base = args.url.rstrip("/")
records = []


def probe(path, expected=200, method="GET"):
    request = urllib.request.Request(base + path, method=method)
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        body = response.read()
        headers = dict(response.headers)
        status = response.status
    assert status == expected, (path, status, expected)
    for name, value in (("X-Content-Type-Options", "nosniff"), ("X-Frame-Options", "DENY")):
        assert response.headers.get(name) == value, (path, name)
    assert "script-src 'self'" in response.headers.get("Content-Security-Policy", ""), path
    records.append({"path": path, "method": method, "status": status, "bytes": len(body),
                    "content_type": response.headers.get("Content-Type"),
                    "cache_control": response.headers.get("Cache-Control"),
                    "edge_cache": response.headers.get("X-Vercel-Cache")})
    if method == "HEAD":
        assert not body, path
    return body


for route in ("/", "/index.html", "/style.css", "/main.js", "/learning.js", "/favicon.svg", "/robots.txt", "/api/health"):
    probe(route)
assert json.loads(probe("/learning-example.json")) == build_example(), "Teaching trace differs from Python"
actual = json.loads(probe("/api/simulate?seed=42"))
assert actual == simulate(Scenario(), Settings()), "Production algorithm differs from local Python"
assert json.loads(probe("/api/simulate?seed=987&noise=0.2&alpha=0.9&threshold=2.3")) == simulate(
    Scenario(seed=987, noise=.2), Settings(alpha=.9, threshold=2.3))
zero = json.loads(probe("/api/simulate?seed=42&noise=0&signal=0&burst=0"))
assert all(bit == 0 for bit in zero["events"])
assert all(record["metrics"]["mean_delay"] is None for record in zero["detectors"].values())
saved = json.loads(Path("experiments/benchmark_results.json").read_text(encoding="utf-8"))
assert json.loads(probe("/api/benchmark")) == saved
probe("/api/benchmark")
for query in ("seed=-1", "seed=1000000", "seed=", "noise=NaN", "alpha=inf", "seed=1&seed=2", "extra=1"):
    assert "error" in json.loads(probe("/api/simulate?" + query, 400))
for route in ("/missing", "/api/missing", "/.env", "/.git/config", "/app.py", "/dionaea/model.py"):
    probe(route, 404)
for route in ("/api/simulate", "/api/benchmark", "/api/health"):
    assert "error" in json.loads(probe(route, 405, "POST"))
    probe(route, method="HEAD")
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
Path(args.output).write_text(json.dumps({"base": base, "passed": True,
    "production_matches_local_python": True, "benchmark_matches_saved": True,
    "zero_events_and_null_delay": True, "routes": records}, indent=2) + "\n", encoding="utf-8", newline="\n")
print(f"PASS {len(records)} live route/method checks, production/local equality, saved benchmark and empty-event case")

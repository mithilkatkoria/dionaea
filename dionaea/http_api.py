"""Shared HTTP boundary for local development and Vercel Python functions."""
from http.server import BaseHTTPRequestHandler
import json
import math
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .detectors import METHODS, Settings
from .evaluate import simulate
from .model import Scenario

ROOT = Path(__file__).resolve().parents[1]
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
}
DEFAULTS = {
    "seed": (int, 42), "noise": (float, .09), "signal": (float, .67),
    "burst": (float, .006), "window": (int, 6), "count": (int, 3),
    "alpha": (float, .80), "threshold": (float, 1.60), "cooldown": (int, 6),
}


def simulation_query(query: str) -> dict:
    if len(query) > 2048:
        raise ValueError("Query is too long (maximum 2048 characters)")
    fields = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=16)
    if fields.keys() - DEFAULTS.keys():
        raise ValueError("Unknown simulation parameter")
    values = {}
    for name, (convert, default) in DEFAULTS.items():
        if name not in fields:
            values[name] = default
            continue
        if len(fields[name]) != 1 or not fields[name][0]:
            raise ValueError(f"{name} must have exactly one non-empty value")
        try:
            values[name] = convert(fields[name][0])
        except (ValueError, OverflowError):
            raise ValueError(f"{name} must be a valid {convert.__name__}") from None
        if not math.isfinite(values[name]):
            raise ValueError(f"{name} must be finite")
    if not 0 <= values["seed"] <= 999999:
        raise ValueError("seed must be 0..999999")
    scenario = Scenario(**{k: values[k] for k in ("seed", "noise", "signal", "burst")})
    settings = Settings(**{k: values[k] for k in ("window", "count", "alpha", "threshold", "cooldown")})
    return simulate(scenario, settings)


def api_response(path: str, query: str = "") -> tuple[int, dict]:
    if path == "/api/health":
        return 200, {"ok": True, "data_kind": "synthetic", "detectors": list(METHODS)}
    if path == "/api/simulate":
        try:
            return 200, simulation_query(query)
        except (ValueError, OverflowError) as exc:
            return 400, {"error": str(exc)}
    if path == "/api/benchmark":
        try:
            return 200, json.loads((ROOT / "experiments/benchmark_results.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return 503, {"error": "Saved benchmark is unavailable. Please retry later."}
    return 404, {"error": "API route not found"}


class APIHandler(BaseHTTPRequestHandler):
    def respond(self, status: int, content: bytes, content_type: str, cache="no-store"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", cache)
        for key, value in SECURITY_HEADERS.items():
            self.send_header(key, value)
        if status == 405:
            self.send_header("Allow", "GET, HEAD")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(content)

    def json_response(self, status: int, value, cache="no-store"):
        body = json.dumps(value, separators=(",", ":"), allow_nan=False).encode("utf-8")
        self.respond(status, body, "application/json; charset=utf-8", cache)

    def do_GET(self):
        url = urlsplit(self.path)
        status, value = api_response(url.path, url.query)
        cache = "public, max-age=0, s-maxage=3600" if url.path == "/api/benchmark" and status == 200 else "no-store"
        self.json_response(status, value, cache)

    def do_HEAD(self):
        self.do_GET()

    def method_not_allowed(self):
        self.json_response(405, {"error": "Method not allowed. Use GET or HEAD."})

    do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = method_not_allowed

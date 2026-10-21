"""Minimal local HTTP server. No Python dependencies beyond the standard library."""
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from dionaea.detectors import Settings
from dionaea.evaluate import simulate
from dionaea.model import Scenario

ROOT = Path(__file__).resolve().parent
MIMES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "application/javascript; charset=utf-8", ".svg": "image/svg+xml"}


class Handler(BaseHTTPRequestHandler):
    def respond(self, code: int, content: bytes, content_type: str):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def json_response(self, code: int, value):
        self.respond(code, json.dumps(value, separators=(",", ":")).encode(), "application/json")

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/health":
            self.json_response(200, {"ok": True})
            return
        if url.path == "/api/simulate":
            try:
                qs = parse_qs(url.query)
                def p(name, fn, default):
                    return fn(qs[name][0]) if name in qs else default
                config = Scenario(seed=p("seed", int, 42),
                                  noise=p("noise", float, 0.09),
                                  signal=p("signal", float, 0.67),
                                  burst=p("burst", float, 0.006))
                settings = Settings(window=p("window", int, 6),
                                    count=p("count", int, 3),
                                    alpha=p("alpha", float, 0.80),
                                    threshold=p("threshold", float, 1.60),
                                    cooldown=p("cooldown", int, 6))
                self.json_response(200, simulate(config, settings))
            except (ValueError, OverflowError) as exc:
                self.json_response(400, {"error": str(exc)})
            return
        if url.path == "/api/benchmark":
            path = ROOT / "experiments" / "benchmark_results.json"
            if not path.exists():
                self.json_response(404, {"error": "Run python -m dionaea.benchmark first"})
            else:
                self.respond(200, path.read_bytes(), "application/json")
            return
        files = {"/": "index.html", "/index.html": "index.html", "/style.css": "style.css",
                 "/main.js": "main.js"}
        name = files.get(url.path)
        if name is None:
            self.respond(404, b"Not found", "text/plain; charset=utf-8")
            return
        path = ROOT / "web" / name
        self.respond(200, path.read_bytes(), MIMES.get(path.suffix, "application/octet-stream"))


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Dionaea lab running at http://127.0.0.1:8765")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()

"""Real HTTP integration tests for local and production Python entrypoints."""
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import threading
import unittest
from unittest.mock import patch
from app import Handler
from api.simulate import handler as SimulationHandler
from api.benchmark import handler as BenchmarkHandler
from api.health import handler as HealthHandler
from dionaea.http_api import api_response
from dionaea.evaluate import simulate
from dionaea.model import Scenario
from dionaea.detectors import Settings


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, method="GET", port=None):
        connection = HTTPConnection("127.0.0.1", port or self.server.server_port, timeout=5)
        connection.request(method, path)
        response = connection.getresponse()
        status, headers, body = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return status, headers, body

    def test_same_python_algorithm_over_http(self):
        status, _, body = self.request("/api/simulate?seed=42")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), simulate(Scenario(), Settings()))

    def test_valid_boundary_values(self):
        for query in ("seed=0&noise=0&signal=1&burst=0&window=1&count=2&alpha=0&threshold=0.1&cooldown=0",
                      "seed=999999&window=30&count=8&threshold=8&cooldown=40&alpha=0.999"):
            with self.subTest(query=query):
                self.assertEqual(self.request("/api/simulate?" + query)[0], 200)

    def test_invalid_queries_are_json_400(self):
        for query in ("seed=-1", "seed=1000000", "seed=1.5", "seed=", "seed=1&seed=2",
                      "unknown=1", "noise=NaN", "alpha=inf", "noise=-0.1", "noise=1.1",
                      "window=0", "count=9", "threshold=0", "cooldown=41", "seed", "signal=abc"):
            with self.subTest(query=query):
                status, headers, body = self.request("/api/simulate?" + query)
                self.assertEqual(status, 400)
                self.assertIn("application/json", headers["Content-Type"])
                self.assertIsInstance(json.loads(body)["error"], str)
                self.assertNotIn(b"Traceback", body)

    def test_oversized_query(self):
        self.assertEqual(self.request("/api/simulate?seed=" + "0" * 2100)[0], 400)

    def test_too_many_fields(self):
        self.assertEqual(self.request("/api/simulate?" + "&".join("seed=1" for _ in range(17)))[0], 400)

    def test_health(self):
        status, _, body = self.request("/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["data_kind"], "synthetic")

    def test_benchmark_is_saved_result(self):
        from pathlib import Path
        status, headers, body = self.request("/api/benchmark")
        self.assertEqual(status, 200)
        self.assertIn("s-maxage=3600", headers["Cache-Control"])
        self.assertEqual(json.loads(body), json.loads(Path("experiments/benchmark_results.json").read_text()))

    def test_missing_benchmark_is_honest_error(self):
        with patch("dionaea.http_api.Path.read_text", side_effect=OSError):
            self.assertEqual(api_response("/api/benchmark"), (503, {"error": "Saved benchmark is unavailable. Please retry later."}))

    def test_api_unknown_route(self):
        status, _, body = self.request("/api/missing")
        self.assertEqual(status, 404)
        self.assertEqual(json.loads(body)["error"], "API route not found")

    def test_unsupported_methods(self):
        for method in ("POST", "PUT", "PATCH", "DELETE", "OPTIONS"):
            with self.subTest(method=method):
                status, headers, body = self.request("/api/simulate", method)
                self.assertEqual(status, 405)
                self.assertEqual(headers["Allow"], "GET, HEAD")
                self.assertIn("error", json.loads(body))

    def test_head_has_no_body(self):
        for path in ("/", "/api/simulate", "/api/health", "/api/benchmark"):
            with self.subTest(path=path):
                status, headers, body = self.request(path, "HEAD")
                self.assertEqual(status, 200)
                self.assertEqual(body, b"")
                self.assertGreater(int(headers["Content-Length"]), 0)

    def test_static_routes(self):
        for path in ("/", "/index.html", "/main.js", "/style.css", "/learning.js", "/learning-example.json", "/favicon.svg", "/robots.txt"):
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertIn("must-revalidate", headers["Cache-Control"])
                self.assertGreater(len(body), 0)

    def test_sources_and_private_files_are_not_served(self):
        for path in ("/.env", "/.git/config", "/app.py", "/dionaea/model.py", "/../README.md", "/missing"):
            with self.subTest(path=path):
                status, _, body = self.request(path)
                self.assertEqual(status, 404)
                self.assertIn(b"Off the", body)

    def test_security_and_simulation_cache_headers(self):
        for path in ("/", "/api/simulate", "/api/health", "/missing"):
            status, headers, _ = self.request(path)
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(headers["X-Frame-Options"], "DENY")
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
            if path.startswith("/api/"):
                self.assertEqual(headers["Cache-Control"], "no-store")

    def test_production_entrypoints_serve_real_http(self):
        for handler, path in ((SimulationHandler, "/api/simulate?seed=7"),
                              (BenchmarkHandler, "/api/benchmark"),
                              (HealthHandler, "/api/health")):
            with self.subTest(path=path):
                server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    status, _, body = self.request(path, port=server.server_port)
                    self.assertEqual(status, 200)
                    self.assertIsInstance(json.loads(body), dict)
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()

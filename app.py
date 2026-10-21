"""Local development server. The production entrypoints live in api/."""
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from dionaea.http_api import APIHandler

ROOT = Path(__file__).resolve().parent
FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/main.js": ("main.js", "application/javascript; charset=utf-8"),
    "/learning.js": ("learning.js", "application/javascript; charset=utf-8"),
    "/learning-example.json": ("learning-example.json", "application/json; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
    "/robots.txt": ("robots.txt", "text/plain; charset=utf-8"),
}


class Handler(APIHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path.startswith("/api/"):
            return super().do_GET()
        name, mime = FILES.get(path, ("404.html", "text/html; charset=utf-8"))
        status = 200 if path in FILES else 404
        self.respond(status, (ROOT / "public" / name).read_bytes(), mime, "public, max-age=0, must-revalidate")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Dionaea lab running at http://127.0.0.1:8765", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

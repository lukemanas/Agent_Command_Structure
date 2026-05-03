"""Demo service — stdlib-only HTTP server used as a target for AgentCS workers.

The dispatch table is `ROUTES`. Tests call `handle(path)` directly so they don't
need a running server. To run live: `python3 service.py [port]`.
"""
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# (status_code, body) per path. Workers add new routes by inserting entries here.
ROUTES = {
    "/health": (200, "ok"),
    "/hello": (200, "hello world"),
}


def handle(path):
    """Return (status, body) for a GET on `path`."""
    if path in ROUTES:
        return ROUTES[path]
    return (404, "not found")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, body = handle(self.path)
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args, **_kwargs):
        pass


def serve(port=8000):
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"serving on http://127.0.0.1:{p}")
    serve(p)

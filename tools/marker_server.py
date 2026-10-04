#!/usr/bin/env python3
"""Serve one immutable, benign marker response to the Android lab emulator."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json


HOST = "127.0.0.1"
PORT = 18765
MARKER = {
    "kind": "lab-marker",
    "message": "benign",
}
MARKER_BODY = json.dumps(MARKER, separators=(",", ":")).encode("utf-8")


class MarkerHandler(BaseHTTPRequestHandler):
    server_version = "DivarLabMarker/1.0"
    sys_version = ""

    def _reply(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - HTTP method name
        if self.path == "/marker":
            self._reply(200, MARKER_BODY)
        else:
            self._reply(404, b'{"error":"not_found"}')

    def do_HEAD(self) -> None:  # noqa: N802 - HTTP method name
        self.send_error(405, "Only GET /marker is supported")

    def do_POST(self) -> None:  # noqa: N802 - HTTP method name
        self.send_error(405, "Only GET /marker is supported")

    def do_PUT(self) -> None:  # noqa: N802 - HTTP method name
        self.send_error(405, "Only GET /marker is supported")

    def do_DELETE(self) -> None:  # noqa: N802 - HTTP method name
        self.send_error(405, "Only GET /marker is supported")


def make_server(port: int = PORT) -> ThreadingHTTPServer:
    """Return a server bound only to the host loopback interface."""
    server = ThreadingHTTPServer((HOST, port), MarkerHandler)
    server.daemon_threads = True
    return server


def main() -> None:
    with make_server() as server:
        print(f"Benign lab marker: http://{HOST}:{PORT}/marker", flush=True)
        print("Stop with Ctrl-C.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

"""
fdk_runtime.sidecar — a dependency-free reference HTTP surface.

The realistic deployment of FDK in an agent stack is a *sidecar*: the planner
POSTs a candidate action, the engine returns a verdict, and the orchestrator
executes only on ALLOW. This module provides that surface using ONLY the Python
standard library (`http.server`) so the package stays dependency-free.

    POST /v1/decide   {request body}  -> 200 {decision}   (or 400 {DENY decision})
    GET  /healthz                     -> 200 {"status": "ok", ...}

It is a *reference* server: single-threaded, no TLS, no auth on the endpoint
itself. For production, put the pure `handle_decide(engine, body)` function
behind a real ASGI/WSGI server (uvicorn/gunicorn) with TLS, request auth, and
rate limiting — the decision logic is identical. The fail-closed contract holds
at the HTTP layer too: an unparseable body returns a DENY decision, not an
ALLOW, and never a bare 500.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from fdk_runtime.codec import CodecError, decode_request
from fdk_runtime.engine import PolicyDecision, PolicyEngine, Verdict


def handle_decide(engine: PolicyEngine, body: bytes) -> tuple[int, dict[str, object]]:
    """Pure request handler (no sockets) — easy to unit-test. Returns
    `(http_status, decision_dict)`. A malformed body yields HTTP 400 with a
    fail-closed DENY body; a decided action yields 200 with its decision."""
    try:
        payload = json.loads(body)
        action, graph = decode_request(payload)
    except (json.JSONDecodeError, CodecError, TypeError) as exc:
        denied = PolicyDecision(
            Verdict.DENY, "<unparseable>", "<unknown>",
            reasons=(f"fail-closed: bad request: {type(exc).__name__}: {exc}",),
            fail_closed=True,
        )
        return 400, denied.to_dict()
    decision = engine.evaluate(action, graph)
    return 200, decision.to_dict()


def make_handler(engine: PolicyEngine) -> type[BaseHTTPRequestHandler]:
    """Build a request-handler class bound to `engine`."""

    class _Handler(BaseHTTPRequestHandler):
        server_version = "fdk-runtime/sidecar"

        def _write(self, status: int, body: dict[str, object]) -> None:
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            if self.path == "/healthz":
                self._write(200, {"status": "ok", "service": "fdk-runtime"})
            else:
                self._write(404, {"error": "not found"})

        def do_POST(self) -> None:
            if self.path != "/v1/decide":
                self._write(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0) or 0)
            body = self.rfile.read(length) if length else b""
            status, decision = handle_decide(engine, body)
            self._write(status, decision)

        def log_message(self, *_args: object) -> None:
            """Silence the default stderr access log (the audit sink is the
            record of decisions, not this)."""

    return _Handler


def serve(engine: PolicyEngine, host: str = "127.0.0.1", port: int = 8099) -> None:
    """Run the reference sidecar (blocking). Front this with a real server in
    production — see the module docstring."""
    httpd = HTTPServer((host, port), make_handler(engine))
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()

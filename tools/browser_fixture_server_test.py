#!/usr/bin/env python3
"""Check real asset bytes, bounded accept bursts and failure transparency.

--legacy runs the same burst/oracle against the previous server and must fail.
No request retry, longer wait, app substitute or relaxed assertion is used.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import threading
from urllib.request import urlopen
from urllib.error import HTTPError

from browser_fixture_server import BrowserFixtureServer

ROOT = Path(__file__).resolve().parents[1]
CLIENTS = 32
CONNECT_SECONDS = 0.4


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def burst(server_type):
    handler = partial(Quiet, directory=str(ROOT))
    server = server_type(("127.0.0.1", 0), handler)
    thread = None
    connections = []
    failures = []
    try:
        paths = [item["path"] for item in
                 json.loads((ROOT / "src/js/manifest.json").read_text())["files"][:CLIENTS]]
        barrier = threading.Barrier(CLIENTS)

        def connect(path):
            barrier.wait(timeout=5)
            sock = None
            try:
                sock = socket.create_connection(server.server_address, timeout=CONNECT_SECONDS)
                sock.sendall((f"GET /{path} HTTP/1.0\r\nHost: 127.0.0.1\r\n\r\n").encode())
                return path, sock, None
            except OSError as exc:
                if sock:
                    sock.close()
                return path, None, type(exc).__name__

        # Hold dispatch during a deterministic simultaneous accept burst. This
        # isolates listen-backlog capacity from CPU/network timing or app code.
        with ThreadPoolExecutor(max_workers=CLIENTS) as pool:
            for path, sock, error in pool.map(connect, paths):
                if error:
                    failures.append({"path": path, "error": error})
                else:
                    connections.append((path, sock))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        checked = []
        for path, sock in connections:
            sock.settimeout(5)
            response = b""
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                response += chunk
            header, body = response.split(b"\r\n\r\n", 1)
            assert header.startswith(b"HTTP/1.0 200"), (path, header)
            expected = (ROOT / path).read_bytes()
            assert body == expected, path
            checked.append({"path": path, "sha256": hashlib.sha256(body).hexdigest()})
            sock.close()
        result = {"queue": server.request_queue_size, "requested": CLIENTS,
                  "completed": len(checked), "failures": failures, "assets": checked}
        print(json.dumps(result))
        assert len(checked) == CLIENTS and not failures, "fixture dropped candidate assets"

        # A missing asset remains 404. Increasing capacity cannot synthesize it.
        try:
            urlopen(f"http://127.0.0.1:{server.server_port}/__jpw_absent_asset__.js", timeout=5)
            raise AssertionError("missing asset received false success")
        except HTTPError as exc:
            assert exc.code == 404, exc.code
            exc.close()
    finally:
        for _, sock in connections:
            sock.close()
        if thread:
            server.shutdown()
            thread.join(timeout=5)
            assert not thread.is_alive(), "fixture server leaked serving thread"
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", action="store_true")
    args = parser.parse_args()
    burst(ThreadingHTTPServer if args.legacy else BrowserFixtureServer)
    print("BROWSER FIXTURE SERVER PASS — 32 real assets, hashes, 404 and cleanup")

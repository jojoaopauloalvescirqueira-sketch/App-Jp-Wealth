#!/usr/bin/env python3
"""Browser proof for the JP Wealth coordinated brand, without user storage."""
from __future__ import annotations

import base64
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import tempfile
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:
        pass

    def handle(self) -> None:
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            # Chrome can abandon a speculative asset request while shutting down.
            pass


class CDP:
    def __init__(self, websocket_url: str):
        host_path = websocket_url.removeprefix("ws://")
        host_port, path = host_path.split("/", 1)
        host, port = host_port.split(":")
        self.socket = socket.create_connection((host, int(port)))
        key = base64.b64encode(os.urandom(16)).decode()
        request = (f"GET /{path} HTTP/1.1\r\nHost: {host_port}\r\nUpgrade: websocket\r\n"
                   f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.socket.sendall(request.encode())
        if b" 101 " not in self.socket.recv(4096):
            raise AssertionError("handshake CDP recusado")
        self.message_id = 0

    def _receive(self) -> dict[str, object]:
        header = self.socket.recv(2)
        if not header or (header[0] & 15) != 1:
            raise AssertionError("frame CDP inesperado")
        size = header[1] & 127
        if size == 126:
            size = struct.unpack("!H", self.socket.recv(2))[0]
        elif size == 127:
            size = struct.unpack("!Q", self.socket.recv(8))[0]
        data = b""
        while len(data) < size:
            data += self.socket.recv(size - len(data))
        return json.loads(data)

    def evaluate(self, expression: str):
        self.message_id += 1
        payload = json.dumps({"id": self.message_id, "method": "Runtime.evaluate", "params": {
            "expression": expression, "returnByValue": True, "awaitPromise": True}}, separators=(",", ":")).encode()
        mask = os.urandom(4)
        header = bytes([0x81, 0x80 | (len(payload) if len(payload) < 126 else 126)])
        if len(payload) >= 126:
            header += struct.pack("!H", len(payload))
        self.socket.sendall(header + mask + bytes(value ^ mask[index % 4] for index, value in enumerate(payload)))
        while True:
            response = self._receive()
            if response.get("id") != self.message_id:
                continue
            result = response["result"]
            if "exceptionDetails" in result:
                raise AssertionError(result["exceptionDetails"])
            return result["result"].get("value")

    def close(self) -> None:
        self.socket.close()


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def main() -> None:
    if not CHROME.is_file():
        raise SystemExit("ENVIRONMENT_ERROR: Google Chrome indisponivel")
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Quiet)
    server_port = int(server.server_address[1])
    threading.Thread(target=server.serve_forever, daemon=True).start()
    debug_port = free_port()
    with tempfile.TemporaryDirectory(prefix="jpw-brand-browser-") as profile:
        chrome = subprocess.Popen([str(CHROME), "--headless=new", "--disable-gpu", "--no-first-run",
                                   f"--remote-debugging-port={debug_port}", f"--user-data-dir={profile}",
                                   f"http://127.0.0.1:{server_port}/index.html"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            target = None
            for _ in range(100):
                try:
                    pages = json.load(urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json/list", timeout=.2))
                    target = next((page for page in pages if page.get("type") == "page" and f":{server_port}/" in page.get("url", "")), None)
                    if target:
                        break
                except Exception:
                    pass
                time.sleep(.05)
            if not target:
                raise AssertionError("Chrome CDP nao expôs a pagina")
            cdp = CDP(target["webSocketDebuggerUrl"])
            try:
                for _ in range(100):
                    if cdp.evaluate("typeof openAppIconPicker === 'function'"):
                        break
                    time.sleep(.05)
                else:
                    raise AssertionError("modulo da marca nao carregou")
                cdp.evaluate("applyAppIconChoice('primary');")
                initial = cdp.evaluate("JSON.stringify({choice:currentAppIconChoice(),head:document.querySelector('[data-jp-brand-wordmark]').getAttribute('src'),manifest:document.querySelector('link[rel=manifest]').getAttribute('href')})")
                assert '"choice":"primary"' in initial and 'brand-red' in initial and 'jp-wealth.webmanifest' in initial, initial
                settings = cdp.evaluate("openSettingsModal('appearance'); JSON.stringify({title:document.querySelector('#appIconConfig h2')?.textContent,button:document.querySelector('#chooseAppIconBtn')?.textContent,overlay:document.querySelector('#settingsOverlay')?.classList.contains('show')})")
                for fragment in ('Marca do JP Wealth', 'Alterar marca', '"overlay":true'):
                    assert fragment in settings, settings
                cdp.evaluate("closeSettingsModal({restoreFocus:false});")
                cancel = cdp.evaluate("openAppIconPicker(); document.querySelector('[data-app-icon-select=secondary]').click(); document.querySelector('#closeAppIconBtn').click(); currentAppIconChoice()")
                assert cancel == "primary", cancel
                after = cdp.evaluate("const url=location.href; applyAppIconChoice('secondary'); JSON.stringify({choice:currentAppIconChoice(),sameUrl:url===location.href,head:document.querySelector('[data-jp-brand-wordmark]').getAttribute('src'),favicon:document.querySelector('link[rel=icon]').getAttribute('href'),apple:document.querySelector('link[rel=apple-touch-icon]').getAttribute('href'),manifest:document.querySelector('link[rel=manifest]').getAttribute('href'),brand:document.documentElement.dataset.brandChoice,plate:getComputedStyle(document.querySelector('[data-jp-brand-wordmark]')).backgroundColor})")
                for fragment in ('"choice":"secondary"', '"sameUrl":true', 'brand-black', 'pwa-icon-secondary', 'jp-wealth-black.webmanifest', '"brand":"secondary"'):
                    assert fragment in after, after
                assert '"plate":"rgb(247, 248, 250)"' in after, after
                assert cdp.evaluate("localStorage.setItem('jpwealth_v9_icon_choice','invalid'); currentAppIconChoice()") == "primary"
            finally:
                cdp.close()
        finally:
            chrome.terminate()
            chrome.wait(timeout=10)
            server.shutdown()
    print("BRAND_IDENTITY_BROWSER PASS")


if __name__ == "__main__":
    main()

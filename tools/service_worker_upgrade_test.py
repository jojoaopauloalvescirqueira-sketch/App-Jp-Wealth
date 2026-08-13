#!/usr/bin/env python3
"""Caracterização real do ciclo conservador de atualização da PWA."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
import json
import mimetypes
import os
import shutil
import socket
import tempfile
import threading
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = "/sw.js"


def digest(data: bytes) -> str: return sha256(data).hexdigest()


def markerize(root: Path, build: str) -> None:
    (root / "build-id.js").write_text(f"const JP_WEALTH_BUILD_ID = 'test-{build}';\n", encoding="utf-8")
    index = root / "index.html"; html = index.read_text(encoding="utf-8")
    html = html.replace("</head>", f'<meta name="jpwealth-test-html-build" content="{build}"></head>', 1)
    html = html.replace("</body>", f'<script>window.__JPW_TEST_JS_BUILD="{build}";</script></body>', 1)
    index.write_text(html, encoding="utf-8")
    css = root / "src/styles/app.css"
    css.write_text(css.read_text(encoding="utf-8") + f"\n:root{{--jpwealth-test-css-build:{build};}}\n", encoding="utf-8")
    sw = root / "sw.js"; source = sw.read_text(encoding="utf-8")
    source += f"\n// jpwealth test worker build: {build}\nself.addEventListener('message',event=>{{if(event.data?.type==='jpwealth-test-build'&&event.ports[0])event.ports[0].postMessage({{build:JP_WEALTH_BUILD_ID,cache:CACHE_NAME}});}});\n"
    sw.write_text(source, encoding="utf-8")


def safe_headers(headers) -> dict[str, str]:
    return {key: value for key, value in headers.items() if key.lower() not in {"cookie", "authorization", "proxy-authorization"}}


class UpgradeHandler(BaseHTTPRequestHandler):
    roots: dict[str, Path] = {}; mode = "old"; requests: list[dict] = []
    def log_message(self, *_args): pass
    def do_GET(self): self.serve(True)
    def do_HEAD(self): self.serve(False)
    def serve(self, send_body: bool):
        parsed = urlsplit(self.path); relative = unquote(parsed.path).lstrip("/") or "index.html"
        root = self.roots[self.mode].resolve(); file = (root / relative).resolve()
        if (root not in file.parents and file != root) or not file.is_file(): self.send_error(404); return
        body = file.read_bytes(); body_sha = digest(body); etag = f'"{body_sha}"'
        content_type = "application/javascript; charset=utf-8" if file.suffix == ".js" else (mimetypes.guess_type(file.name)[0] or "application/octet-stream")
        modified = datetime.fromtimestamp(file.stat().st_mtime, timezone.utc); last_modified = format_datetime(modified, usegmt=True)
        status = 200
        if self.headers.get("If-None-Match") == etag: status = 304
        elif not self.headers.get("If-None-Match") and self.headers.get("If-Modified-Since"):
            try: status = 304 if parsedate_to_datetime(self.headers["If-Modified-Since"]).timestamp() >= modified.timestamp() else 200
            except (TypeError, ValueError, IndexError): pass
        cache_control = "no-cache, max-age=0, must-revalidate" if parsed.path in {"/", "/index.html", SCRIPT_PATH} else "no-store"
        self.send_response(status); self.send_header("Content-Type", content_type); self.send_header("Cache-Control", cache_control); self.send_header("ETag", etag); self.send_header("Last-Modified", last_modified); self.end_headers()
        if send_body and status == 200: self.wfile.write(body)
        if parsed.path == SCRIPT_PATH:
            self.requests.append({"timestamp": datetime.now(timezone.utc).isoformat(), "method": self.command, "url": parsed.path, "query": parsed.query, "request_headers": safe_headers(self.headers), "service_worker_script": self.headers.get("Service-Worker", "").lower() == "script", "status": status, "content_type": content_type, "cache_control": cache_control, "etag": etag, "last_modified": last_modified, "published_build": self.mode, "disk_sha256": body_sha, "sent_body_sha256": body_sha if status == 200 else None})


def start_server(old_root: Path, new_root: Path):
    with socket.socket() as sock: sock.bind(("127.0.0.1", 0)); port = sock.getsockname()[1]
    handler = type("InstrumentedUpgradeHandler", (UpgradeHandler,), {"roots": {"old": old_root, "new": new_root}, "requests": []})
    server = ThreadingHTTPServer(("127.0.0.1", port), handler); threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, handler, f"http://127.0.0.1:{port}/"


def direct_fetch(url: str) -> dict:
    with urlopen(Request(url, headers={"Cache-Control": "no-cache"}), timeout=5) as response:
        body = response.read(); return {"status": response.status, "sha256": digest(body), "headers": dict(response.headers.items())}


def chromium_path() -> str | None:
    paths = [os.environ.get("JP_WEALTH_CHROMIUM", ""), "/usr/bin/chromium", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    return next((path for path in paths if path and Path(path).exists()), None)


def state(page):
    return page.evaluate("""async()=>{const r=await navigator.serviceWorker.getRegistration(),w=x=>x?{url:x.scriptURL,state:x.state}:null;return {scope:r?.scope,updateViaCache:r?.updateViaCache,installing:w(r?.installing),waiting:w(r?.waiting),active:w(r?.active),controller:navigator.serviceWorker.controller?.scriptURL||null}}""")


def worker_build(page, target="controller"):
    return page.evaluate("""async target=>{const r=await navigator.serviceWorker.getRegistration();const w=target==='waiting'?r?.waiting:navigator.serviceWorker.controller;if(!w)throw new Error('worker ausente: '+target);return await new Promise((resolve,reject)=>{const c=new MessageChannel(),t=setTimeout(()=>reject(new Error('worker não respondeu')),3000);c.port1.onmessage=e=>{clearTimeout(t);resolve(e.data)};w.postMessage({type:'jpwealth-test-build'},[c.port2])})}""", target)


def page_build(page):
    return page.evaluate("""()=>({html:document.querySelector('meta[name="jpwealth-test-html-build"]')?.content||'',css:getComputedStyle(document.documentElement).getPropertyValue('--jpwealth-test-css-build').trim(),js:window.__JPW_TEST_JS_BUILD||'',id:JP_WEALTH_BUILD_ID})""")


def page(context, observed, label):
    item = context.new_page()
    item.on("console", lambda message: observed["console"].append({"page": label, "type": message.type, "text": message.text}))
    item.on("pageerror", lambda error: observed["pageerror"].append({"page": label, "error": str(error)}))
    item.on("requestfailed", lambda request: observed["requestfailed"].append({"page": label, "url": request.url, "failure": request.failure}))
    item.add_init_script("window.__jpwUpgradeEvents=[];navigator.serviceWorker?.addEventListener('controllerchange',()=>window.__jpwUpgradeEvents.push('controllerchange')); ")
    return item


def arm(page):
    page.evaluate("""async()=>{const r=await navigator.serviceWorker.getRegistration(),log=window.__jpwUpgradeEvents||(window.__jpwUpgradeEvents=[]);const watch=w=>w&&w.addEventListener('statechange',()=>log.push('statechange:'+w.state));r.addEventListener('updatefound',()=>{log.push('updatefound');watch(r.installing)});watch(r.active)}""")


def wait_until(page, predicate: str, timeout=8000): page.wait_for_function(predicate, timeout=timeout)


def wait_for_waiting_worker(page, timeout=8.0):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        last = page.evaluate("""async()=>{const r=await navigator.serviceWorker.getRegistration();return {installing:r?.installing?.state||null,waiting:r?.waiting?.state||null,active:r?.active?.state||null}}""")
        if last["waiting"] == "installed":
            return last
        time.sleep(0.05)
    raise AssertionError(f"worker novo nao chegou a waiting/installed: {last}")


def main():
    with tempfile.TemporaryDirectory(prefix="jpwealth-pwa-upgrade-") as temp_dir:
        temp = Path(temp_dir); old_root, new_root = temp / "old", temp / "new"
        shutil.copytree(ROOT, old_root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache")); shutil.copytree(ROOT, new_root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
        markerize(old_root, "old"); markerize(new_root, "new")
        old_sha, new_sha = digest((old_root / "sw.js").read_bytes()), digest((new_root / "sw.js").read_bytes())
        assert old_sha != new_sha
        server, handler, base = start_server(old_root, new_root); observed = {"console": [], "pageerror": [], "requestfailed": []}; report = {"hashes": {"old": old_sha, "new": new_sha}}
        try:
            with sync_playwright() as playwright:
                options = {"headless": True, "args": ["--no-sandbox"]}; executable = chromium_path()
                if executable: options["executable_path"] = executable
                browser = playwright.chromium.launch(**options); context = browser.new_context()
                context.route("**/api.frankfurter.dev/**", lambda route: route.fulfill(status=200, content_type="application/json", body='{"rate":1}'))
                context.route("**/ff-high-impact.json", lambda route: route.fulfill(status=200, content_type="application/json", body='{"events":[]}'))
                a = page(context, observed, "old-a"); a.goto(base + "index.html", wait_until="load"); wait_until(a, "navigator.serviceWorker.controller"); a.reload(wait_until="load"); wait_until(a, "navigator.serviceWorker.controller")
                b = page(context, observed, "old-b"); b.goto(base + "index.html?tab=b", wait_until="load"); wait_until(b, "navigator.serviceWorker.controller")
                a.evaluate("()=>caches.open('external-app-cache').then(c=>c.put('/external',new Response('keep')))" )
                report["before"] = {"a": {"page": page_build(a), "worker": worker_build(a), "state": state(a)}, "b": {"page": page_build(b), "worker": worker_build(b), "state": state(b)}}
                offline_old = page(context, observed, "old-offline"); context.set_offline(True); offline_old.goto(base + "index.html?offline=old", wait_until="load"); wait_until(offline_old, "navigator.serviceWorker.controller"); report["offline_old"] = {"page": page_build(offline_old), "worker": worker_build(offline_old)}; offline_old.close(); context.set_offline(False)
                handler.mode = "new"; report["direct_new_before_update"] = direct_fetch(base + "sw.js"); assert report["direct_new_before_update"]["sha256"] == new_sha
                arm(a); arm(b); request_count = len(handler.requests)
                # Descoberta real: o controller antigo entrega seu index cacheado e o
                # bootstrap desse proprio build chama registration.update(). Assim o
                # worker novo instala sem misturar HTML novo com assets antigos. O
                # harness nao pode forcar update() por fora do runtime.
                discovery = page(context, observed, "discovery"); discovery.goto(base + "index.html?discover=new", wait_until="load"); wait_until(discovery, "navigator.serviceWorker.controller")
                wait_for_waiting_worker(discovery)
                report["runtime_discovery"] = {"page": page_build(discovery), "worker": worker_build(discovery), "waiting_worker": worker_build(discovery, "waiting"), "state": state(discovery)}
                report["waiting_detected"] = {"a": state(a), "b": state(b), "events_a": a.evaluate("window.__jpwUpgradeEvents"), "events_b": b.evaluate("window.__jpwUpgradeEvents")}
                report["waiting"] = {"a": {"page": page_build(a), "controller": worker_build(a), "events": a.evaluate("window.__jpwUpgradeEvents"), "state": state(a)}, "b": {"page": page_build(b), "controller": worker_build(b), "events": b.evaluate("window.__jpwUpgradeEvents"), "state": state(b)}, "caches": a.evaluate("caches.keys()")}
                discovery.close(); a.close(); time.sleep(.3); report["after_close_a"] = {"state_b": state(b), "caches": b.evaluate("caches.keys()")}
                b.close(); time.sleep(.7)
                online_new = page(context, observed, "new-online"); online_new.goto(base + "index.html?build=new", wait_until="load"); wait_until(online_new, "navigator.serviceWorker.controller"); online_new.reload(wait_until="load"); wait_until(online_new, "navigator.serviceWorker.controller")
                report["new_online"] = {"page": page_build(online_new), "worker": worker_build(online_new), "state": state(online_new), "caches": online_new.evaluate("caches.keys()")}
                online_new.close(); context.set_offline(True)
                offline_new = page(context, observed, "new-offline"); offline_new.goto(base + "index.html?offline=new", wait_until="load"); wait_until(offline_new, "navigator.serviceWorker.controller")
                report["new_offline"] = {"page": page_build(offline_new), "worker": worker_build(offline_new), "state": state(offline_new), "caches": offline_new.evaluate("caches.keys()")}
                context.set_offline(False); browser.close()
            report["server_update_requests"] = handler.requests[request_count:]; report["observed"] = observed
        finally: server.shutdown(); server.server_close()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    console_errors = [item for item in observed["console"] if item["type"] == "error"]
    assert not observed["pageerror"] and not console_errors and not observed["requestfailed"], report
    for item in (report["before"]["a"], report["before"]["b"]): assert item["page"] == {"html":"old","css":"old","js":"old","id":"test-old"} and item["worker"]["build"] == "test-old" and item["state"]["updateViaCache"] == "none", report
    assert report["runtime_discovery"]["page"] == {"html":"old","css":"old","js":"old","id":"test-old"}, report
    assert report["runtime_discovery"]["worker"]["build"] == "test-old" and report["runtime_discovery"]["waiting_worker"]["build"] == "test-new", report
    assert "jp-wealth-test-new" in report["waiting"]["caches"], report
    for key in ("a", "b"):
        item = report["waiting"][key]; assert item["page"] == {"html":"old","css":"old","js":"old","id":"test-old"} and item["controller"]["build"] == "test-old" and "controllerchange" not in item["events"], report
    assert report["after_close_a"]["state_b"]["waiting"] and "jp-wealth-test-new" in report["after_close_a"]["caches"], report
    for key in ("new_online", "new_offline"):
        item = report[key]; assert item["page"] == {"html":"new","css":"new","js":"new","id":"test-new"} and item["worker"]["build"] == "test-new", report
    assert "external-app-cache" in report["new_online"]["caches"], report
    update = [item for item in report["server_update_requests"] if item["service_worker_script"] and item["published_build"] == "new"]
    assert update and update[-1]["status"] == 200 and update[-1]["sent_body_sha256"] == new_sha, report
    print("PWA UPGRADE OK — waiting conservador, duas abas, build íntegro, offline e cache externo verificados.")


if __name__ == "__main__": main()

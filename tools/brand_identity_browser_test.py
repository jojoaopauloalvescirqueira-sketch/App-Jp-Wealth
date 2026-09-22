#!/usr/bin/env python3
"""Browser proof for the JP Wealth coordinated brand, without user storage."""
from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args: object) -> None:
        pass

class BrowserFixtureServer(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True

    def handle(self) -> None:
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            # Chrome can abandon a speculative asset request while shutting down.
            pass


def main() -> None:
    os.chdir(ROOT)
    server = BrowserFixtureServer(("127.0.0.1", 0), Quiet)
    server_port = int(server.server_address[1])
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{server_port}/index.html", wait_until="load")
                page.wait_for_function("typeof openAppIconPicker === 'function'")
                page.evaluate("applyAppIconChoice('primary');")
                initial = page.evaluate("JSON.stringify({choice:currentAppIconChoice(),head:document.querySelector('[data-jp-brand-wordmark]').getAttribute('src'),manifest:document.querySelector('link[rel=manifest]').getAttribute('href')})")
                assert '"choice":"primary"' in initial and 'brand-red' in initial and 'jp-wealth.webmanifest' in initial, initial
                settings = page.evaluate("openSettingsModal('appearance'); JSON.stringify({title:document.querySelector('#appIconConfig h2')?.textContent,button:document.querySelector('#chooseAppIconBtn')?.textContent,overlay:document.querySelector('#settingsOverlay')?.classList.contains('show')})")
                for fragment in ('Marca do JP Wealth', 'Alterar marca', '"overlay":true'):
                    assert fragment in settings, settings
                page.evaluate("closeSettingsModal({restoreFocus:false});")
                cancel = page.evaluate("openAppIconPicker(); document.querySelector('[data-app-icon-select=secondary]').click(); document.querySelector('#closeAppIconBtn').click(); currentAppIconChoice()")
                assert cancel == "primary", cancel
                after = page.evaluate("const url=location.href; applyAppIconChoice('secondary'); JSON.stringify({choice:currentAppIconChoice(),sameUrl:url===location.href,head:document.querySelector('[data-jp-brand-wordmark]').getAttribute('src'),favicon:document.querySelector('link[rel=icon]').getAttribute('href'),apple:document.querySelector('link[rel=apple-touch-icon]').getAttribute('href'),manifest:document.querySelector('link[rel=manifest]').getAttribute('href'),brand:document.documentElement.dataset.brandChoice,plate:getComputedStyle(document.querySelector('[data-jp-brand-wordmark]')).backgroundColor})")
                for fragment in ('"choice":"secondary"', '"sameUrl":true', 'brand-black', 'pwa-icon-secondary-512', 'jp-wealth-black.webmanifest', '"brand":"secondary"'):
                    assert fragment in after, after
                assert '"plate":"rgb(247, 248, 250)"' in after, after
                assert page.evaluate("localStorage.setItem('jpwealth_v9_icon_choice','invalid'); currentAppIconChoice()") == "primary"
            finally:
                browser.close()
    finally:
        server.shutdown()
    print("BRAND_IDENTITY_BROWSER PASS")


if __name__ == "__main__":
    main()

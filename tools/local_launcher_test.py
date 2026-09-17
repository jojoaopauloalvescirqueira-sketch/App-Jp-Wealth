#!/usr/bin/env python3
"""Real loopback HTTP and isolated launcher fixtures; never opens a browser."""
import contextlib
import hashlib
from html.parser import HTMLParser
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from urllib.parse import quote, urljoin, urlsplit

import launch_local as launcher

ROOT = Path(__file__).resolve().parents[1]
SENTINEL = b'SYNTHETIC PRIVATE DATA - MUST NOT BE SERVED'


@contextlib.contextmanager
def serving(root, port=0):
    with launcher.LocalServer(root, port=port) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server
        finally:
            server.shutdown()
            thread.join(timeout=3)


def request(server, path, method='GET', headers=None):
    connection = http.client.HTTPConnection(launcher.HOST, server.server_port, timeout=3)
    try:
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        return response.status, {key.lower(): value for key, value in response.getheaders()}, response.read()
    finally:
        connection.close()


def fixture(base, name='Pasta sintética com espaços e ação'):
    root = base / name
    files = {
        'index.html': b'<!doctype html><title>SYNTHETIC JP Wealth</title>',
        'build-id.js': b'const BUILD="synthetic";',
        'sw.js': b'/* synthetic worker */',
        'assets/public.png': b'synthetic-public-image',
        'src/js/manifest.json': b'{"files":[]}',
        'src/js/public.js': b'/* synthetic script */',
        'manifests/test.webmanifest': b'{"name":"Synthetic"}',
        'downloads/nocuda/test.pine': b'// synthetic download',
        'docs/normative/ANEXO_PARAMETRICO_CANONICO.md': b'# Synthetic reference',
        'private.json': SENTINEL,
        '.git/config': SENTINEL,
        'data/backup.json': SENTINEL,
        'docs/private.md': SENTINEL,
        'assets/.hidden': SENTINEL,
    }
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    (root / 'tools').mkdir()
    shutil.copy2(ROOT / 'tools/launch_local.py', root / 'tools/launch_local.py')
    shutil.copy2(ROOT / 'Abrir JP Wealth.command', root / 'Abrir JP Wealth.command')
    return root


class LocalHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='jpw-launcher-test-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = fixture(self.base)
        self.server = self.enterContext(serving(self.root)) if hasattr(self, 'enterContext') else None
        if self.server is None:  # macOS Python 3.9 also remains supported.
            context = serving(self.root)
            self.server = context.__enter__()
            self.addCleanup(context.__exit__, None, None, None)

    def test_public_files_root_health_and_head(self):
        for path in ['/', '/index.html', '/build-id.js', '/sw.js', '/assets/public.png?v=test',
                     '/src/js/public.js', '/downloads/nocuda/test.pine',
                     '/docs/normative/ANEXO_PARAMETRICO_CANONICO.md']:
            with self.subTest(path=path):
                status, headers, body = request(self.server, path)
                self.assertEqual(status, 200)
                self.assertTrue(body)
                self.assertEqual(headers.get('cache-control'), 'no-cache')
                self.assertEqual(headers.get('x-content-type-options'), 'nosniff')
        status, headers, body = request(self.server, '/assets/public.png', 'HEAD')
        self.assertEqual((status, body), (200, b''))
        self.assertEqual(int(headers['content-length']), len(b'synthetic-public-image'))
        status, headers, body = request(self.server, '/manifests/test.webmanifest')
        self.assertEqual(headers['content-type'], 'application/manifest+json')
        status, _, body = request(self.server, launcher.HEALTH_PATH)
        health = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(health, {'app': launcher.PROTOCOL, 'root': launcher.root_id(self.root),
                                  'pid': os.getpid()})
        self.assertNotIn(str(self.root), body.decode())
        self.assertEqual(launcher.probe(self.root, self.server.origin), health)
        self.assertFalse(launcher.probe(self.base / 'different', self.server.origin))

    def test_foreign_hosts_and_origins_are_rejected(self):
        for headers in [{'Host': 'evil.example'}, {'Host': 'localhost:8765'},
                        {'Host': '127.0.0.1'}, {'Origin': 'https://evil.example'},
                        {'Origin': 'null'}]:
            with self.subTest(headers=headers):
                self.assertEqual(request(self.server, '/index.html', headers=headers)[0], 403)
        self.assertEqual(request(self.server, '/index.html', headers={'Origin': self.server.origin})[0], 200)

    def test_private_paths_traversal_and_directory_listing_are_rejected(self):
        for path in ['/private.json', '/.git/config', '/data/backup.json', '/docs/private.md',
                     '/tools/launch_local.py', '/assets/', '/src/', '/assets/.hidden',
                     '/assets/../private.json', '/assets/%2e%2e/private.json',
                     '/assets/%2e%2e%2fprivate.json', '/assets/%252e%252e/private.json',
                     '/assets/%5c..%5cprivate.json', '/assets/%00public.png']:
            with self.subTest(path=path):
                status, _, body = request(self.server, path)
                self.assertEqual(status, 404)
                self.assertNotIn(SENTINEL, body)
        before = (self.root / 'private.json').read_bytes()
        self.assertEqual(request(self.server, '/private.json', 'PUT')[0], 501)
        self.assertEqual((self.root / 'private.json').read_bytes(), before)

    def test_external_and_private_internal_symlinks_are_rejected(self):
        external = self.base / 'external-private.json'
        external.write_bytes(SENTINEL)
        (self.root / 'assets/external.json').symlink_to(external)
        (self.root / 'assets/internal.json').symlink_to(self.root / 'private.json')
        (self.root / 'assets/private-dir').symlink_to(self.root / 'data', target_is_directory=True)
        for path in ['/assets/external.json', '/assets/internal.json', '/assets/private-dir/backup.json']:
            with self.subTest(path=path):
                status, _, body = request(self.server, path)
                self.assertEqual(status, 404)
                self.assertNotIn(SENTINEL, body)


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('src', 'href') and value:
                self.urls.add(value)


class ProductAssetsTests(unittest.TestCase):
    def test_all_html_manifest_and_precache_resources_are_served(self):
        parser = References()
        parser.feed((ROOT / 'index.html').read_text())
        paths = {'/', '/index.html', '/sw.js', '/build-id.js'}
        for resource in parser.urls:
            parsed = urlsplit(resource)
            if not parsed.scheme and not parsed.netloc and parsed.path:
                paths.add(urlsplit(urljoin('/index.html', resource)).path)
        manifest = json.loads((ROOT / 'src/js/manifest.json').read_text())
        paths.update('/' + entry['path'] for entry in manifest['files'])
        sw = (ROOT / 'sw.js').read_text().split('].flatMap', 1)[0]
        paths.update(urljoin('/', path) for path in re.findall(r"['\"](\./[^'\"]*)['\"]", sw))
        for manifest_path in (ROOT / 'manifests').glob('*.webmanifest'):
            manifest_url = '/' + manifest_path.relative_to(ROOT).as_posix()
            paths.add(manifest_url)
            data = json.loads(manifest_path.read_text())
            paths.add(urljoin(manifest_url, data['start_url']))
            paths.update(urljoin(manifest_url, icon['src']) for icon in data['icons'])
        css = (ROOT / 'src/styles/app.css').read_text()
        for resource in re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)', css):
            if not urlsplit(resource).scheme and not resource.startswith('#'):
                paths.add(urljoin('/src/styles/app.css', resource.strip()))
        self.assertGreater(len(paths), 100, 'Resource coverage unexpectedly empty')
        with serving(ROOT) as server:
            for path in sorted(paths):
                with self.subTest(path=path):
                    encoded = quote(path, safe='/%?=&')
                    status, headers, body = request(server, encoded)
                    self.assertEqual(status, 200)
                    local = ROOT / (urlsplit(path).path.lstrip('/') or 'index.html')
                    self.assertEqual(hashlib.sha256(body).digest(), hashlib.sha256(local.read_bytes()).digest())
                    if path.endswith(('.js', '.mjs')):
                        self.assertIn(headers.get('content-type'), ('text/javascript', 'application/javascript'))
            self.assertEqual(request(server, '/assets/pwa-icon-primary-512.png?v=synthetic')[0], 200)
        print('Public runtime HTTP resources exercised:', len(paths), flush=True)


class LauncherCLITests(unittest.TestCase):
    def test_start_reopen_and_busy_port_without_changing_origin(self):
        with socket.socket() as guard:
            guard.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                guard.bind((launcher.HOST, launcher.PORT))
            except OSError as error:
                self.skipTest('Fixed port already occupied; no unrelated process touched: ' + str(error))
        with tempfile.TemporaryDirectory(prefix='jpw-cli-test-') as directory:
            root = fixture(Path(directory))
            command = [sys.executable, str(root / 'tools/launch_local.py'), '--no-open']
            owned_pid = None
            try:
                first = subprocess.run(command, cwd='/tmp', capture_output=True, text=True, timeout=10)
                self.assertEqual(first.returncode, 0, first.stderr)
                health = launcher.probe(root)
                self.assertIsInstance(health, dict)
                owned_pid = health['pid']
                self.assertIn(launcher.URL, first.stdout)
                # Exercise Finder shell path handling, not only Python entry point.
                second = subprocess.run(['/bin/zsh', str(root / 'Abrir JP Wealth.command'), '--no-open'],
                                        cwd='/tmp', capture_output=True, text=True, timeout=10)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(launcher.probe(root)['pid'], owned_pid)
                self.assertIn(launcher.URL, second.stdout)
                other = fixture(Path(directory), 'Outra pasta sintética')
                refused = subprocess.run([sys.executable, str(other / 'tools/launch_local.py'), '--no-open'],
                                         capture_output=True, text=True, timeout=10)
                self.assertEqual(refused.returncode, 1)
                self.assertIn(launcher.ORIGIN, refused.stderr)
                self.assertIn('Nenhum endereço alternativo', refused.stderr)
                self.assertEqual(launcher.probe(root)['pid'], owned_pid)
            finally:
                if owned_pid is not None:
                    # PID came only from the server started above with this unique fixture root.
                    os.kill(owned_pid, signal.SIGTERM)
                    deadline = time.monotonic() + 4
                    while launcher.probe(root) and time.monotonic() < deadline:
                        time.sleep(0.05)
            self.assertIsNone(launcher.probe(root))


if __name__ == '__main__':
    unittest.main(verbosity=2)

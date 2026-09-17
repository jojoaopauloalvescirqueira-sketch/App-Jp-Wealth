#!/usr/bin/env python3
"""Inicializador macOS: mesma origem, arquivos públicos e dados no navegador."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]
HOST = '127.0.0.1'
PORT = 8765
ORIGIN = 'http://{}:{}'.format(HOST, PORT)
URL = ORIGIN + '/index.html'
HEALTH_PATH = '/.jp-wealth-local'
PROTOCOL = 'jpwealth-local-launcher-v1'
PUBLIC_FILES = {'index.html', 'build-id.js', 'sw.js'}
PUBLIC_DIRS = {'assets', 'src', 'manifests', 'downloads'}
NORMATIVE_FILES = {
    'docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf',
    'docs/normative/ANEXO_PARAMETRICO_CANONICO.md',
}


def public_path(relative):
    parts = Path(relative).parts
    return (not any(part.startswith('.') for part in parts) and
            (relative in PUBLIC_FILES or relative in NORMATIVE_FILES or
             (parts and parts[0] in PUBLIC_DIRS)))


def root_id(root):
    return hashlib.sha256(str(root.resolve()).encode('utf-8')).hexdigest()


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, root, port=PORT):
        self.root = Path(root).resolve()
        super().__init__((HOST, port), LocalHandler)
        self.origin = 'http://{}:{}'.format(HOST, self.server_port)


class LocalHandler(SimpleHTTPRequestHandler):
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map,
                          **{'.mjs': 'text/javascript',
                             '.webmanifest': 'application/manifest+json'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(args[2].root), **kwargs)

    def log_message(self, *args):
        pass  # Não registrar URLs, conteúdo do operador ou requisições.

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def send_head(self):
        # Host fechado também impede servir a página via DNS rebinding.
        if self.headers.get('Host') != self.server.origin.split('://', 1)[1]:
            self.send_error(403)
            return None
        origin = self.headers.get('Origin')
        if origin and origin != self.server.origin:
            self.send_error(403)
            return None
        path = unquote(urlsplit(self.path).path)
        if path == HEALTH_PATH:
            body = json.dumps({'app': PROTOCOL, 'root': root_id(self.server.root),
                               'pid': os.getpid()}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(body)
            return None
        relative = path.lstrip('/') or 'index.html'
        if not public_path(relative) or '\\' in relative or '\x00' in relative:
            self.send_error(404)
            return None
        target = (self.server.root / relative).resolve()
        try:
            resolved = target.relative_to(self.server.root).as_posix()
        except ValueError:
            self.send_error(404)
            return None
        if not public_path(resolved) or not target.is_file():
            self.send_error(404)
            return None
        # SimpleHTTPRequestHandler mantém streaming/HEAD e tipo MIME dos assets.
        return super().send_head()


def probe(root, origin=ORIGIN):
    """None: porta indisponível; dict: servidor conhecido; False: outro serviço."""
    try:
        opener = build_opener(ProxyHandler({}))
        with opener.open(origin + HEALTH_PATH, timeout=0.7) as response:
            data = json.loads(response.read(4096))
        if (isinstance(data, dict) and data.get('app') == PROTOCOL and
                data.get('root') == root_id(root)):
            return data
        return False
    except (OSError, ValueError):
        return None


def start(root):
    running = probe(root)
    if running:
        return running
    # Bind distingue porta livre de serviço incompatível antes de abrir Safari.
    # A segunda checagem no filho cobre dois cliques simultâneos.
    child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--serve'],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True,
                             close_fds=True)
    for _ in range(40):
        running = probe(root)
        if running:
            return running
        if child.poll() is not None:
            break
        time.sleep(0.1)
    if child.poll() is None:
        child.terminate()
    raise RuntimeError('Não foi possível usar {}. A porta pode estar ocupada por '
                       'outro serviço ou outra pasta do JP Wealth. Nenhum endereço '
                       'alternativo foi aberto; seus dados permanecem preservados.'
                       .format(ORIGIN))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--no-open', action='store_true', help='Verificar sem abrir Safari')
    args = parser.parse_args()
    try:
        if not (ROOT / 'index.html').is_file() or not (ROOT / 'src/js/manifest.json').is_file():
            raise RuntimeError('Mantenha o atalho e a pasta tools junto do index.html do JP Wealth.')
        if args.serve:
            with LocalServer(ROOT) as server:
                server.serve_forever()
            return 0
        start(ROOT)
        if not args.no_open:
            subprocess.run(['/usr/bin/open', '-a', 'Safari', URL], check=True)
        print('JP Wealth disponível em ' + URL)
        print('Use sempre este atalho. Você pode fechar esta janela do Terminal.')
        print('Na primeira abertura, importe o backup completo do acesso anterior.')
        return 0
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print('JP Wealth: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

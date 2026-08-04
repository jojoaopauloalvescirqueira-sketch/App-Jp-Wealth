#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
print('JP Wealth disponível em http://127.0.0.1:8000')
ThreadingHTTPServer(('127.0.0.1', 8000), SimpleHTTPRequestHandler).serve_forever()

#!/usr/bin/env python3
"""Run downloader integrity tests with the host or bundled Node runtime."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
parser = argparse.ArgumentParser()
parser.add_argument('--node', default=os.environ.get('JPW_NODE') or shutil.which('node') or str(bundled))
args = parser.parse_args()
if not Path(args.node).is_file():
    print('ENVIRONMENT_ERROR: Node runtime absent; use --node or JPW_NODE')
    print('JPW_TEST_RESULT: ENVIRONMENT_ERROR')
    sys.exit(1)
result = subprocess.run([args.node, str(ROOT / 'tools/stoikus_download_test.js')], cwd=ROOT,
                        capture_output=True, text=True, timeout=30)
print(result.stdout, end='')
print(result.stderr, end='', file=sys.stderr)
sys.exit(result.returncode)

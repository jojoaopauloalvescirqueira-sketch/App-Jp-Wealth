#!/usr/bin/env python3
"""Synthetic source-byte reproductions for the N2 saving integrity contract.

The probe executes the production persistence/Alladin modules in a disposable VM.
Only browser adapters and unrelated inputs are synthetic. Financial formulas are
not replaced or asserted here. Native browser journeys are separate acceptance.
"""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--artifact', type=Path)
    args = parser.parse_args()
    candidates = [os.environ.get('JPW_NODE', ''), shutil.which('node') or '',
        str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')]
    node = next((p for p in candidates if p and Path(p).is_file()), None)
    if not node:
        print('NOT_RUN: Node runtime unavailable for source integrity probe')
        return 2
    with tempfile.TemporaryDirectory(prefix='jpw-saving-integrity-') as tmp:
        artifact = args.artifact or Path(tmp)/'receipt.json'
        artifact.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run([node, str(args.root/'tools/fixtures/saving_persistence_integrity_probe.js'),
            str(args.root), str(artifact)], cwd=args.root, check=False)
        return result.returncode

if __name__ == '__main__':
    raise SystemExit(main())

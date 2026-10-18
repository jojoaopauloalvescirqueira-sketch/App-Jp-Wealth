#!/usr/bin/env python3
"""Product distribution oracles against the real, offline official generator."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from build_reproducibility_test import arquivos_do_candidato, montar

ROOT = Path(__file__).resolve().parents[1]
VENDOR = 'src/vendor/aisol-dot-globe/'
DATA = 'src/data/market-hours/'
AISOL = 'src/js/40-app/31-market-hours/aisol/'
INPUTS = (
    AISOL+'engine.js', AISOL+'entry.js',
    *(VENDOR+name for name in ('aisol-globe.iife.js', 'component.original.js',
      'build-lock.json', 'build-meta.json', 'build-receipt.json', 'NOTICES.md',
      'THREE-LICENSE.txt', 'ESBUILD-LICENSE.txt')),
    *(DATA+name for name in ('calendar-v1.json', 'rules.json', 'sources.json', 'zoneinfo/manifest.json')),
    *(DATA+'zoneinfo/'+zone for zone in ('UTC', 'America/Sao_Paulo', 'America/New_York',
      'America/Toronto', 'Europe/London', 'Europe/Berlin', 'Europe/Paris', 'Asia/Tokyo',
      'Asia/Hong_Kong', 'Asia/Shanghai', 'Asia/Kolkata', 'Asia/Seoul', 'Asia/Riyadh', 'Australia/Sydney')),
    'tools/compile_market_hours.py', 'tools/build_market_globe.py',
)


def build(root, *flags, success=True):
    result = subprocess.run([sys.executable, 'tools/rebuild_monolith.py', *flags],
                            cwd=root, capture_output=True, text=True)
    assert (result.returncode == 0) == success, result.stdout + result.stderr
    return result.stdout + result.stderr


def inspect(root):
    bootstrap = (root/'build-id.js').read_text()
    match = re.search(r'window.JPW_MARKET_HOURS_MANIFEST = (\{[^\n]+\});', bootstrap)
    assert match, 'official build omits lazy market-hours resource manifest'
    manifest = json.loads(match[1])
    build_id = re.search(r"JP_WEALTH_BUILD_ID = '([^']+)'", bootstrap)[1]
    assert manifest['schemaVersion'] == 1 and manifest['buildId'] == build_id
    assert len(bootstrap.encode()) < 50000, 'bootstrap contains bulk runtime bytes'
    assert 'JPWAisolGlobeRuntime' not in bootstrap
    sidecar = root/manifest['payload']['path']
    sidecar_text = sidecar.read_text()
    assert sidecar_text.startswith('window.JPWMarketHoursAssets.register(')
    envelope = json.loads(sidecar_text.split('register(', 1)[1].removesuffix(');\n'))
    html = (root/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').read_text()
    inert = re.search(r'<script type="application/json" id="jpw-market-hours-payload">(.*?)</script>', html, re.S)
    assert inert, 'portable omits inert market-hours bytes'
    assert '<' not in inert[1], 'raw HTML delimiter in inert JSON'
    assert json.loads(inert[1]) == envelope
    assert envelope['schemaVersion'] == 1 and envelope['buildId'] == build_id
    for key, relative in [('catalog', DATA+'calendar-v1.json'), ('renderer', VENDOR+'aisol-globe.iife.js')]:
        original = (root/relative).read_bytes()
        assert envelope['files'][key].encode() == original, key
        assert manifest['resources'][key] == dict(path=relative, bytes=len(original), sha256=hashlib.sha256(original).hexdigest())
    scripts = json.loads((root/'src/js/manifest.json').read_text())
    assert len(scripts['runtimeAssets']) == 4, 'market resources expanded PDF runtimeAssets'
    assert all(item['path'] != manifest['resources']['renderer']['path'] for item in scripts['files'])
    assert '<script src="'+manifest['resources']['renderer']['path']+'"></script>' not in html
    sw = (root/'sw.js').read_text()
    for relative in [DATA+'calendar-v1.json', VENDOR+'aisol-globe.iife.js',
                     *('src/js/40-app/31-market-hours/'+n for n in ('01-sessions.js', '02-assets.js', '03-view.js', '04-controller.js'))]:
        assert "'./"+relative+"'" in sw, 'offline precache missing '+relative
    assert manifest['payload']['path'] not in sw, 'file sidecar belongs outside web precache'
    assert 'skipWaiting' not in sw
    return build_id, envelope


def main():
    files = sorted(set(arquivos_do_candidato()) | set(INPUTS))
    with tempfile.TemporaryDirectory(prefix='jpw-market-build-') as temp:
        root = Path(temp)
        montar(root, files)
        build(root)
        first, envelope = inspect(root)
        # Bytes containing an HTML terminator stay inert and round-trip exactly.
        catalog = root/DATA/'calendar-v1.json'
        catalog.write_bytes(catalog.read_bytes()+b'\r\n')
        build(root)
        second, _ = inspect(root)
        assert first != second, 'calendar bytes missing from build fingerprint'
        catalog.write_text(json.dumps({'synthetic': '</script><script>alert(1)</script>'}))
        build(root)
        inspect(root)
        # Changed adaptation without a fresh vendor receipt must never ship.
        for relative in [AISOL+'engine.js', AISOL+'entry.js', VENDOR+'component.original.js', VENDOR+'aisol-globe.iife.js']:
            target = root/relative
            saved = target.read_bytes()
            target.write_bytes(saved+b'\n')
            error = build(root, success=False)
            assert 'Aisol' in error and ('divergente' in error or 'diferente' in error), error
            target.write_bytes(saved)
        # A declared input disappearing must fail loudly, even before first commit.
        for relative in INPUTS:
            target = root/relative
            saved = target.read_bytes()
            target.unlink()
            error = build(root, success=False)
            assert 'input oficial do build ausente' in error and relative in error, error
            target.write_bytes(saved)
        # Refresh hashes through the official builder, preserving all ordering/metadata.
        original = json.loads((root/'src/js/manifest.json').read_text())
        target = root/original['files'][0]['path']
        target.write_bytes(target.read_bytes()+b'\n')
        build(root, '--refresh-manifest')
        refreshed = json.loads((root/'src/js/manifest.json').read_text())
        for before, after in zip(original['files'], refreshed['files']):
            assert {k:v for k,v in before.items() if k != 'sha256'} == {k:v for k,v in after.items() if k != 'sha256'}
            assert after['sha256'] == hashlib.sha256((root/after['path']).read_bytes()).hexdigest()
        print('MARKET HOURS BUILD PASS: official bytes, inert portable, lightweight metadata, conservative precache, receipt refusal, missing inputs, manifest refresh')


if __name__ == '__main__':
    main()

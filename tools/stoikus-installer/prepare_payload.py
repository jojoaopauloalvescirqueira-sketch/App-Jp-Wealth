#!/usr/bin/env python3
"""Verify current daily sources and immutable official catalog; copy exact payload bytes."""
from __future__ import annotations
from io import BytesIO
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_leverage_package import (ROOT, PRODUCT, MANIFEST_PATH, DAILY_GUIDE, DAILY_PROGRAMS,
    checked_file, daily_inventory, local_dependencies, write_changed, build)

INSTALLER_VERSION = '1.0.0-beta.1'
PRODUCT_VERSION = '1.23.0'
FILENAME = 'Stoikus_Setup_1.0.0-beta.1_win-x64.exe'
GENERATED = 'tools/stoikus-installer/generated/'
# Frozen official archives, never rebuilt here. Different versions are catalog
# evidence for identity only, not runtime/native approval for this candidate.
HISTORY = {
 'JPW_Genetrix_Fontes_v1.20.0.zip': ('1.20.0', '9a0bb0a4cb61b1e63eee99b10bde64a446f1d383ad5179bf5b05d9c85b65af7d'),
 'JPW_Alavancagem_Atual_Compilado_v1.20.0.zip': ('1.20.0', '0f23b0f0163d824a78ff0e2ee0b8bb90f08c5075b293968f2cc940666b5447ba'),
 'JPW_Genetrix_Fontes_v1.21.2.zip': ('1.21.2', 'a9a77be170036747fec8322fdba7d80bd6256fbcae87e4c6dadb1348ff916261'),
 'JPW_Stoikus_Fontes_v1.22.0.zip': ('1.22.0', '79d481a624d37dccb2237f37db7a35b2746a0b8281d183b1ce30fcba0bfc9c95'),
}
ROLES = {'JPW_Stoikus_Monitor': 'monitor', 'JPW_Alavancagem_Atual': 'account',
         'JPW_NoCuda_Channels': 'nocuda', 'JPW_Stoikus_Abrir_Paineis': 'openPanels'}

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def unavailable_installer_record():
    return {'available': False, 'installerVersion': INSTALLER_VERSION, 'productVersion': PRODUCT_VERSION,
            'platform': 'win-x64', 'filename': FILENAME, 'path': None, 'releaseUrl': None,
            'sha256': None, 'bytes': None, 'unsigned': True,
            'nativeTests': {'windowsX64': 'NOT_RUN', 'parallelsArm': 'NOT_RUN', 'browser': 'NOT_RUN'},
            'nativeEvidence': None,
            'reason': 'Candidato beta não assinado. Provas do mesmo EXE em Windows x64, Parallels ARM e navegador: NOT_RUN; download público indisponível.'}

def entries(raw):
    result = {}
    case_names = set()
    try:
        with zipfile.ZipFile(BytesIO(raw)) as archive:
            for info in archive.infolist():
                name = info.filename
                path = PurePosixPath(name)
                if (not name or path.is_absolute() or path.as_posix() != name or '\\' in name or ':' in name
                    or any(part in ('.', '..') for part in path.parts)
                    or any(ord(c) < 32 for c in name) or info.is_dir()
                    or stat.S_ISLNK(info.external_attr >> 16) or name.casefold() in case_names):
                    raise ValueError('Unsafe, duplicate or case-colliding archive path: ' + name)
                case_names.add(name.casefold())
                result[name] = archive.read(info)
    except (zipfile.BadZipFile, RuntimeError) as error:
        raise ValueError('Invalid archive') from error
    return result

def verified_download(root, record):
    if (not isinstance(record, dict) or record.get('available') is not True
        or not re.fullmatch(r'downloads/jpw-alavancagem-atual/[A-Za-z0-9._-]+\.zip', str(record.get('path', '')))
        or record.get('filename') != PurePosixPath(record['path']).name):
        raise ValueError('Invalid official download record')
    raw = checked_file(root, record['path'], 'downloads/jpw-alavancagem-atual/').read_bytes()
    if type(record.get('bytes')) is not int or len(raw) != record['bytes'] or digest(raw) != record.get('sha256'):
        raise ValueError('Archive hash/size mismatch')
    return raw

def prepare(root=ROOT):
    root = Path(root)
    manifest = json.loads(checked_file(root, MANIFEST_PATH, 'downloads/').read_text())
    if manifest.get('schemaVersion') != 1 or manifest.get('version') != PRODUCT_VERSION:
        raise ValueError('Unsupported product manifest')
    source_files = manifest.get('sourceFiles', [])
    hashes = manifest.get('sourceHashes', {})
    if (not source_files or len(set(p.casefold() for p in source_files)) != len(source_files)
        or set(hashes) != {p.removeprefix(PRODUCT) for p in source_files}):
        raise ValueError('Incomplete or case-colliding source inventory')
    sources, dependencies = {}, {}
    for relative in source_files:
        raw = checked_file(root, relative, PRODUCT).read_bytes()
        name = relative.removeprefix(PRODUCT)
        if digest(raw) != hashes[name]:
            raise ValueError('Source identity mismatch: ' + name)
        sources[name] = raw
        if relative.endswith(('.mq5', '.mqh')):
            dependencies[relative] = local_dependencies(relative, raw.decode('utf-8'))
            if not dependencies[relative].issubset(source_files):
                raise ValueError('Undeclared source dependency')
    daily = daily_inventory(source_files, dependencies)
    expected = {'LEIA_PRIMEIRO.md' if p == DAILY_GUIDE else p.removeprefix(PRODUCT) for p in daily}
    sdk_raw = verified_download(root, manifest['downloads']['source'])
    if entries(sdk_raw) != sources:
        raise ValueError('SDK archive/source identity mismatch')
    raw = verified_download(root, manifest['downloads']['dailySource'])
    contents = entries(raw)
    if set(contents) != expected:
        raise ValueError('Daily inventory differs from source dependency closure')
    for name, content in contents.items():
        source = DAILY_GUIDE.removeprefix(PRODUCT) if name == 'LEIA_PRIMEIRO.md' else name
        if content != sources[source]:
            raise ValueError('Daily archive/source identity mismatch: ' + name)
    programs = sorted(p.removeprefix(PRODUCT) for p in DAILY_PROGRAMS)
    if sorted(p for p in contents if p.endswith('.mq5')) != programs or any(p.endswith('.ex5') for p in contents):
        raise ValueError('Daily payload must contain exactly four source programs')
    known = {}
    def catalog(members, version):
        for name, content in sorted(members.items()):
            if not name.startswith('MQL5/'):
                continue
            # Only program/include/resources in these official packages can
            # establish ownership. State/data/locks never enter the catalog.
            if not re.fullmatch(r'MQL5/(Experts|Indicators|Scripts|Include|Images)/JPWealth/[A-Za-z0-9._-]+', name):
                raise ValueError('Unexpected historical MQL path: ' + name)
            item = {'path': name, 'sha256': digest(content), 'bytes': len(content), 'version': version}
            known.setdefault((name, item['sha256']), item)
    for filename, (version, sha) in sorted(HISTORY.items()):
        historical = checked_file(root, 'downloads/jpw-alavancagem-atual/' + filename, 'downloads/').read_bytes()
        if digest(historical) != sha:
            raise ValueError('Immutable official archive altered: ' + filename)
        catalog(entries(historical), version)
    catalog(entries(sdk_raw), PRODUCT_VERSION)
    catalog(contents, PRODUCT_VERSION)
    known_files = sorted(known.values(), key=lambda f: (f['path'], f['sha256']))
    payload = {'schemaVersion': 1, 'installerVersion': INSTALLER_VERSION, 'productVersion': PRODUCT_VERSION,
        'calculationVersion': '1.9.0', 'archiveSha256': digest(raw), 'archiveBytes': len(raw),
        'files': [{'path': name, 'sha256': digest(content), 'bytes': len(content)} for name, content in sorted(contents.items())],
        'programs': [{'source': p, 'output': p[:-4] + '.ex5', 'role': ROLES[PurePosixPath(p).stem]} for p in programs],
        'knownFiles': known_files,
        'legacyFiles': [f for f in known_files if f['path'] not in contents and PurePosixPath(f['path']).suffix in ('.mq5', '.ex5')
                        and f['path'] not in {p[:-4] + '.ex5' for p in programs}]}
    write_changed(root / GENERATED / 'payload.zip', raw)
    write_changed(root / GENERATED / 'payload.json', (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode())
    return {'payloadPath': GENERATED + 'payload.zip', 'manifestPath': GENERATED + 'payload.json', 'manifest': payload}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--record-unavailable', action='store_true', help='Add unavailable public installer metadata through the official package builder')
    args = parser.parse_args()
    if args.record_unavailable:
        build(args.root, installer_record=unavailable_installer_record())
    result = prepare(args.root)
    print(f"Payload verified: {result['manifest']['archiveSha256']} ({result['manifest']['archiveBytes']} bytes); {len(result['manifest']['files'])} files")

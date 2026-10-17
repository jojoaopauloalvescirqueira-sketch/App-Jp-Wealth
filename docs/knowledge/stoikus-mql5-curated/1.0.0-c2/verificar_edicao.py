#!/usr/bin/env python3
"""Read-only integrity check for this curated documentary edition (stdlib only).

Exit 0: structurally intact; 1: inconsistent; 2: unavailable root/manifest/I/O.
An external --manifest-sha256 pin authenticates the expected manifest bytes only
when that pin was obtained through a trusted channel. Hashes alone do not prove
authorship, financial validity, adoption, a current pilot or native MT5 results.
"""
import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata

MANIFEST = 'MANIFESTO_CURADO.json'
KIT_MANIFEST = 'harness-candidato/manifest.json'
KIT_MANIFEST_SHA256 = '004f96cc9a4a094d1dfdeebd803c83ebaf4482d8af07a3d0e1984124ec0328b6'
STATES = {
    'schema': 'stoikus-curated-edition/1',
    'edition_id': 'stoikus-documental-curada-1.0.0-c2',
    'status': 'CURATED_DOCUMENTARY_CANDIDATE',
    'manual_revision': '1.0.0', 'harness_version': '0.1.0 CANDIDATE R3',
    'adoption': 'NOT_ADOPTED', 'native_mt5': 'NOT_RUN',
    'current_behavioral_pilot': 'NOT_RUN', 'historical_results': 'HISTORICAL_ONLY',
}
REQUIRED = frozenset((
    'COMECE_AQUI.md', 'LEIA_ME_KIT.md', 'CURADORIA.md', 'DEPENDENCIAS.md',
    'HISTORICO.md', 'MANUAL.md', KIT_MANIFEST,
    'publication/Stoikus_Engenharia_MQL5_Manual.docx',
    'publication/Stoikus_Engenharia_MQL5_Manual.pdf',
    'publication/toc-pages.json',
    'curadoria/MAPA_ORIGEM.json', 'curadoria/TRANSFORMACOES.json',
    'curadoria/INDICE_PESQUISA_ATUAL.json', 'curadoria/REFERENCIAS_EXTERNAS.json',
    'research/neural-coverage.json', 'research/coverage-summary.json',
    'verificar_edicao.py', 'tests/test_verificar_edicao.py',
)) | frozenset('publication/diagram-%d%s' % (i, suffix)
              for i in range(1, 4) for suffix in ('.png', '-semantics.json'))
TASK2 = frozenset(('verificar_edicao.py', 'tests/test_verificar_edicao.py'))


def is_hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def is_path(value):
    return (isinstance(value, str) and bool(value) and not value.startswith('/')
            and not any(c in value for c in ('\\', ':'))
            and all(part not in ('', '.', '..') for part in value.split('/'))
            and not any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF
                        for c in value))


def canonical_identity(rows):
    plain = [{key: item[key] for key in ('path', 'bytes', 'sha256')}
             for item in sorted(rows, key=lambda item: item['path'])]
    return hashlib.sha256(json.dumps(plain, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def load_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def invalid_constant(_value):
        raise ValueError('non-JSON numeric constant')

    return json.loads(data.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=invalid_constant)


def validate_manifest(document, add):
    if not isinstance(document, dict):
        add('MANIFEST_TYPE', MANIFEST)
        return None
    for key, expected in STATES.items():
        if document.get(key) != expected:
            add('EDITION_STATE', MANIFEST)
    exclusion = document.get('self_exclusion')
    if (not isinstance(exclusion, dict) or exclusion.get('path') != MANIFEST
            or exclusion.get('other_exclusions') != []):
        add('SELF_EXCLUSION', MANIFEST)
    rows = document.get('files')
    if not isinstance(rows, list) or not rows:
        add('INVENTORY_TYPE_OR_EMPTY', MANIFEST)
        return None
    paths = []
    normalized = set()
    directories = {}
    valid_rows = True
    for row in rows:
        if not isinstance(row, dict) or not is_path(row.get('path')):
            add('ENTRY_PATH_OR_TYPE', MANIFEST)
            valid_rows = False
            continue
        path = row['path']
        paths.append(path)
        normalized_path = unicodedata.normalize('NFC', path).casefold()
        if normalized_path in normalized or path == MANIFEST:
            add('PATH_COLLISION', MANIFEST)
        normalized.add(normalized_path)
        components = path.split('/')
        for i in range(1, len(components)):
            prefix = '/'.join(components[:i])
            norm = unicodedata.normalize('NFC', prefix).casefold()
            if norm in directories and directories[norm] != prefix:
                add('PATH_COLLISION', MANIFEST)
            directories[norm] = prefix
        if type(row.get('bytes')) is not int or row['bytes'] < 0 or not is_hash(row.get('sha256')):
            add('ENTRY_SIZE_OR_HASH', MANIFEST)
            valid_rows = False
        provenance = row.get('provenance')
        if not isinstance(provenance, dict):
            add('PROVENANCE', MANIFEST)
            continue
        disposition = provenance.get('disposition')
        scope = provenance.get('scope')
        if disposition not in ('PRESERVED', 'TRANSFORMED', 'GENERATED', 'TASK2_VERIFIER') or scope not in (
                'DOCUMENTARY', 'HISTORICAL_ONLY', 'EDITION_INTEGRITY_ONLY'):
            add('PROVENANCE', MANIFEST)
        if disposition in ('PRESERVED', 'TRANSFORMED'):
            if (not is_path(provenance.get('source_path'))
                    or not is_hash(provenance.get('source_sha256'))
                    or not isinstance(provenance.get('source_category'), str)):
                add('PROVENANCE', MANIFEST)
            if disposition == 'PRESERVED' and provenance.get('source_sha256') != row.get('sha256'):
                add('PRESERVED_IDENTITY', MANIFEST)
        if path.startswith(('research/', 'validation/')) and scope != 'HISTORICAL_ONLY':
            add('HISTORICAL_SCOPE', MANIFEST)
        if path in TASK2 and (disposition != 'TASK2_VERIFIER' or scope != 'EDITION_INTEGRITY_ONLY'):
            add('PROVENANCE', MANIFEST)
        if path in REQUIRED and row.get('bytes') == 0:
            add('REQUIRED_EMPTY', path)
    if paths != sorted(paths):
        add('INVENTORY_ORDER', MANIFEST)
    if normalized.intersection(directories):
        add('PATH_COLLISION', MANIFEST)
    if not REQUIRED.issubset(paths):
        add('REQUIRED_CONTENT', MANIFEST)
    count = document.get('file_count_excluding_manifest')
    if type(count) is not int or count != len(rows):
        add('FILE_COUNT', MANIFEST)
    if valid_rows and document.get('content_identity_sha256') != canonical_identity(rows):
        add('CONTENT_IDENTITY', MANIFEST)
    return rows if valid_rows else None


def read_file(directory_fd, name, keep=False):
    """Open relative to a trusted directory descriptor, without following links."""
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=directory_fd)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError('not a regular file')
        sha = hashlib.sha256()
        size = 0
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            sha.update(chunk)
            size += len(chunk)
            if keep:
                chunks.append(chunk)
        return size, sha.hexdigest(), b''.join(chunks)
    finally:
        os.close(descriptor)


def scan(directory_fd, add, prefix=''):
    """Inventory regular files; reject links/special files, including unlisted ones."""
    files = {}
    kit_data = None
    with os.scandir(directory_fd) as entries:
        names = sorted(entry.name for entry in entries)
    for name in names:
        path = prefix + name
        if not is_path(path):
            add('PHYSICAL_PATH', '.')
            continue
        try:
            mode = os.stat(name, dir_fd=directory_fd, follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):
                add('SYMLINK', path)
            elif stat.S_ISDIR(mode):
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=directory_fd)
                try:
                    nested, data = scan(child, add, path + '/')
                    files.update(nested)
                    if data is not None:
                        kit_data = data
                finally:
                    os.close(child)
            elif stat.S_ISREG(mode):
                if path == MANIFEST:
                    files[path] = None
                else:
                    size, sha, data = read_file(directory_fd, name, keep=path == KIT_MANIFEST)
                    files[path] = {'path': path, 'bytes': size, 'sha256': sha}
                    if path == KIT_MANIFEST:
                        kit_data = data
            else:
                add('SPECIAL_FILE', path)
        except (OSError, ValueError):
            add('IO_UNAVAILABLE', path)
    return files, kit_data


def verify(edition_root, manifest_sha256=None):
    result = {'ok': False, 'exit_code': 1, 'checked_files': 0, 'errors': []}

    def add(kind, path):
        result['errors'].append({'type': kind, 'path': path})
        if kind in ('ROOT_UNAVAILABLE', 'MANIFEST_UNAVAILABLE', 'IO_UNAVAILABLE',
                    'CAPABILITY_UNAVAILABLE'):
            result['exit_code'] = 2

    if manifest_sha256 is not None and not is_hash(manifest_sha256):
        add('MANIFEST_PIN_FORMAT', MANIFEST)
        return result
    # Refuse unavailable safe I/O before touching the edition. Do not replace
    # descriptor-relative or no-follow operations with a weaker fallback.
    flags = ('O_RDONLY', 'O_DIRECTORY', 'O_NOFOLLOW', 'O_NONBLOCK')
    calls = ('open', 'close', 'read', 'fstat', 'lstat', 'stat', 'scandir')
    if (any(type(getattr(os, name, None)) is not int for name in flags)
            or any(not callable(getattr(os, name, None)) for name in calls)):
        add('CAPABILITY_UNAVAILABLE', '.')
        return result
    for capability, names in (
            ('supports_dir_fd', ('open', 'stat')),
            ('supports_fd', ('scandir',)),
            ('supports_follow_symlinks', ('stat',))):
        supported = getattr(os, capability, None)
        if (not isinstance(supported, (set, frozenset))
                or any(getattr(os, name) not in supported for name in names)):
            add('CAPABILITY_UNAVAILABLE', '.')
            return result
    try:
        if stat.S_ISLNK(os.lstat(edition_root).st_mode):
            add('SYMLINK', '.')
            return result
        root_fd = os.open(edition_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except (OSError, ValueError):
        add('ROOT_UNAVAILABLE', '.')
        return result
    try:
        try:
            if stat.S_ISLNK(os.stat(MANIFEST, dir_fd=root_fd, follow_symlinks=False).st_mode):
                add('SYMLINK', MANIFEST)
                return result
            _, sha, data = read_file(root_fd, MANIFEST, keep=True)
        except (OSError, ValueError):
            add('MANIFEST_UNAVAILABLE', MANIFEST)
            return result
        result['manifest_sha256'] = sha
        if manifest_sha256 is not None and sha != manifest_sha256:
            add('MANIFEST_PIN_MISMATCH', MANIFEST)
            return result
        try:
            document = load_json(data)
        except (ValueError, UnicodeError, RecursionError):
            add('MANIFEST_JSON', MANIFEST)
            return result
        rows = validate_manifest(document, add)
        if rows is None or result['errors']:
            return result
        actual, kit_data = scan(root_fd, add)
        expected = {row['path']: row for row in rows}
        for path in sorted(set(expected) - set(actual)):
            add('MISSING_FILE', path)
        for path in sorted(set(actual) - set(expected) - {MANIFEST}):
            add('EXTRA_FILE', path)
        for path in sorted(set(expected).intersection(actual)):
            if actual[path]['bytes'] != expected[path]['bytes']:
                add('SIZE_MISMATCH', path)
            if actual[path]['sha256'] != expected[path]['sha256']:
                add('HASH_MISMATCH', path)
            result['checked_files'] += 1
        kit = actual.get(KIT_MANIFEST)
        if kit is None or kit['sha256'] != KIT_MANIFEST_SHA256:
            add('IMMUTABLE_KIT', KIT_MANIFEST)
        else:
            # Only the known, byte-pinned kit manifest is interpreted. External
            # REPO/SOURCES references and historical research hashes are not
            # treated as missing local files or current behavioral evidence.
            kit_rows = load_json(kit_data)['files']
            kit_paths = {KIT_MANIFEST} | {'harness-candidato/' + row['path'] for row in kit_rows}
            if len(kit_paths) != 45 or kit_paths != {p for p in expected if p.startswith('harness-candidato/')}:
                add('KIT_INVENTORY', KIT_MANIFEST)
            for row in kit_rows:
                path = 'harness-candidato/' + row['path']
                if actual.get(path, {}).get('sha256') != row['sha256']:
                    add('IMMUTABLE_KIT', path)
        if not result['errors']:
            result.update(ok=True, exit_code=0,
                          content_identity_sha256=document['content_identity_sha256'])
        return result
    except (OSError, ValueError, RecursionError):
        add('IO_UNAVAILABLE', '.')
        return result
    finally:
        os.close(root_fd)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps({'ok': False, 'exit_code': 2, 'checked_files': 0,
                          'errors': [{'type': 'ARGUMENT_ERROR', 'path': '.'}]}))
        raise SystemExit(2)


def main():
    parser = Parser(description=__doc__)
    parser.add_argument('--edition-root', type=Path, default=Path(__file__).absolute().parent)
    parser.add_argument('--manifest-sha256')
    args = parser.parse_args()
    result = verify(args.edition_root, args.manifest_sha256)
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())

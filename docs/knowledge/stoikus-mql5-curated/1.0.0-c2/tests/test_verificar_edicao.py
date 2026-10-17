"""Integration tests; every mutation is confined to a disposable edition copy.

Run with python3 -B -m unittest discover -s tests -p test_verificar_edicao.py.
No historical script, source dependency, network service or MT5 is executed.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SOURCE = Path(__file__).absolute().parents[1]
MANIFEST = 'MANIFESTO_CURADO.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def seal(document):
    """Independent fixture serialization, never called on the delivered edition."""
    document['files'].sort(key=lambda item: item['path'])
    rows = [{key: item[key] for key in ('path', 'bytes', 'sha256')}
            for item in document['files']]
    document['file_count_excluding_manifest'] = len(rows)
    document['content_identity_sha256'] = digest(json.dumps(
        rows, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def snapshot(root):
    entries = {}
    for path in sorted(root.rglob('*')):
        st = path.lstat()
        entries[path.relative_to(root).as_posix()] = (
            st.st_mode, st.st_size, st.st_mtime_ns,
            os.readlink(path) if path.is_symlink() else
            digest(path.read_bytes()) if path.is_file() else None)
    return entries


class EditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = tempfile.TemporaryDirectory(prefix='stoikus-check-tests-')
        cls.base = Path(cls.storage.name)
        cls.pristine = cls.base / 'pristine'
        shutil.copytree(SOURCE, cls.pristine, symlinks=True)

    @classmethod
    def tearDownClass(cls):
        cls.storage.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=self.base, prefix='case-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'edition'
        shutil.copytree(self.pristine, self.root, symlinks=True)
        self.document = json.loads((self.root / MANIFEST).read_bytes())

    def write_manifest(self, reseal=False):
        if reseal:
            seal(self.document)
        (self.root / MANIFEST).write_text(
            json.dumps(self.document, ensure_ascii=False), encoding='utf-8')

    def run_checker(self, expected=1, root=None, extra=(), default=False):
        command = [sys.executable, '-B', str(self.root / 'verificar_edicao.py')]
        if not default:
            command += ['--edition-root', str(root if root is not None else self.root)]
        result = subprocess.run(command + list(extra), cwd=self.base,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                                text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual(result.stderr, '')
        parsed = json.loads(result.stdout)
        self.assertIs(parsed['ok'], expected == 0)
        self.assertEqual(parsed['exit_code'], expected)
        for error in parsed['errors']:
            self.assertIsInstance(error['type'], str)
            self.assertFalse(error['path'].startswith('/'))
            self.assertNotIn('..', error['path'].split('/'))
        self.assertNotIn(str(self.base), result.stdout)
        return parsed

    def row(self, path='MANUAL.md'):
        return next(row for row in self.document['files'] if row['path'] == path)

    def test_real_isolated_edition_is_accepted_without_writes(self):
        before = snapshot(self.root)
        result = self.run_checker(expected=0)
        self.assertEqual(result['checked_files'], 212)
        self.assertEqual(snapshot(self.root), before)

    def test_default_root_is_script_directory(self):
        self.run_checker(expected=0, default=True)

    def test_valid_external_pin_is_accepted(self):
        self.run_checker(expected=0, extra=(
            '--manifest-sha256', digest((self.root / MANIFEST).read_bytes())))

    def test_wrong_pin_is_rejected_before_json_is_trusted(self):
        (self.root / MANIFEST).write_bytes(b'not JSON /private/secret')
        result = self.run_checker(extra=('--manifest-sha256', '0' * 64))
        self.assertEqual(result['errors'], [
            {'type': 'MANIFEST_PIN_MISMATCH', 'path': MANIFEST}])

    def test_invalid_pin_is_rejected(self):
        self.run_checker(extra=('--manifest-sha256', 'not-a-hash'))

    def test_same_size_tampering_is_rejected(self):
        path = self.root / 'MANUAL.md'
        data = path.read_bytes()
        path.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        result = self.run_checker()
        self.assertIn('HASH_MISMATCH', [e['type'] for e in result['errors']])

    def test_size_change_is_rejected(self):
        with (self.root / 'MANUAL.md').open('ab') as handle:
            handle.write(b'X')
        result = self.run_checker()
        self.assertIn('SIZE_MISMATCH', [e['type'] for e in result['errors']])

    def test_missing_file_is_inconsistency(self):
        (self.root / 'MANUAL.md').unlink()
        self.run_checker()

    def test_extra_file_is_rejected(self):
        (self.root / 'unlisted.txt').write_text('extra')
        self.run_checker()

    def test_cache_is_not_implicitly_excluded(self):
        cache = self.root / '__pycache__'
        cache.mkdir()
        (cache / 'unlisted.pyc').write_bytes(b'cache')
        self.run_checker()

    def test_empty_inventory_is_rejected_even_when_resealed(self):
        self.document['files'] = []
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_unrelated_self_consistent_tree_is_rejected(self):
        for path in list(self.root.iterdir()):
            if path.name not in (MANIFEST, 'verificar_edicao.py'):
                shutil.rmtree(path) if path.is_dir() else path.unlink()
        script = self.root / 'verificar_edicao.py'
        data = script.read_bytes() if script.exists() else b''
        self.document['files'] = [{'path': script.name, 'bytes': len(data),
                                  'sha256': digest(data), 'provenance': {
                                      'disposition': 'TASK2_VERIFIER',
                                      'scope': 'EDITION_INTEGRITY_ONLY'}}]
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_duplicate_path_is_rejected(self):
        self.document['files'].append(dict(self.row()))
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_case_collision_is_rejected(self):
        row = dict(self.row()); row['path'] = 'manual.md'
        self.document['files'].append(row)
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_file_directory_collision_is_rejected(self):
        row = dict(self.row()); row['path'] = 'MANUAL.md/child'
        self.document['files'].append(row)
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_noncanonical_paths_are_rejected(self):
        for path in ('../outside', '/private/secret', 'C:/secret',
                     'research\\secret', 'a//b', './MANUAL.md', 'a/../b',
                     'a/', '', 'a\x00b', 'a\nb'):
            with self.subTest(path=repr(path)):
                row = self.row()
                row['path'] = path
                try:
                    self.write_manifest()
                    self.run_checker()
                finally:
                    row['path'] = 'MANUAL.md'

    def test_unicode_normalization_collision_is_rejected(self):
        for name in ('caf\u00e9.txt', 'cafe\u0301.txt'):
            row = dict(self.row()); row['path'] = name
            self.document['files'].append(row)
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_unsorted_inventory_is_rejected(self):
        self.document['files'].reverse()
        self.write_manifest()
        self.run_checker()

    def test_invalid_size_types_are_rejected(self):
        for size in (True, -1, 1.5, '172529', None):
            with self.subTest(size=size):
                self.row()['bytes'] = size
                self.write_manifest()
                self.run_checker()

    def test_invalid_hash_types_are_rejected(self):
        for sha in (None, 123, 'A' * 64, 'g' * 64, '0' * 63):
            with self.subTest(sha=sha):
                self.row()['sha256'] = sha
                self.write_manifest()
                self.run_checker()

    def test_wrong_count_and_identity_are_rejected(self):
        for key, value in (('file_count_excluding_manifest', 1),
                           ('file_count_excluding_manifest', True),
                           ('content_identity_sha256', '0' * 64)):
            with self.subTest(key=key, value=value):
                original = self.document[key]
                self.document[key] = value
                self.write_manifest()
                self.run_checker()
                self.document[key] = original

    def test_false_states_and_wrong_identity_are_rejected(self):
        for key, value in (('adoption', 'ADOPTED'), ('native_mt5', 'PASS'),
                           ('current_behavioral_pilot', 'PASS'),
                           ('historical_results', 'CURRENT'), ('schema', 'other'),
                           ('edition_id', 'other'), ('status', 'FINAL'),
                           ('manual_revision', '2.0.0'), ('harness_version', 'FINAL')):
            with self.subTest(key=key):
                original = self.document[key]
                self.document[key] = value
                self.write_manifest()
                self.run_checker()
                self.document[key] = original

    def test_invalid_provenance_is_rejected(self):
        for provenance in (None, {}, {'disposition': 'PRESERVED', 'scope': 'DOCUMENTARY',
                                      'source_path': '../private', 'source_sha256': '0' * 64}):
            with self.subTest(provenance=provenance):
                self.row()['provenance'] = provenance
                self.write_manifest()
                self.run_checker()

    def test_manifest_cannot_list_itself_or_other_exclusions(self):
        row = dict(self.row()); row['path'] = MANIFEST
        self.document['files'].append(row)
        self.write_manifest(reseal=True)
        self.run_checker()
        self.document['files'].remove(row)
        self.document['self_exclusion']['other_exclusions'] = ['private']
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_immutable_kit_cannot_be_rehashed_to_accept_edits(self):
        path = self.root / 'harness-candidato/manifest.json'
        path.write_bytes(path.read_bytes() + b' ')
        self.row('harness-candidato/manifest.json')['sha256'] = digest(path.read_bytes())
        self.row('harness-candidato/manifest.json')['bytes'] = path.stat().st_size
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_required_manual_cannot_be_removed_and_resealed(self):
        self.document['files'].remove(self.row())
        (self.root / 'MANUAL.md').unlink()
        self.write_manifest(reseal=True)
        self.run_checker()

    def test_symlink_file_is_rejected_without_exposing_target(self):
        outside = Path(self.temp.name) / 'private.txt'
        outside.write_text('PRIVATE SENTINEL')
        (self.root / 'MANUAL.md').unlink()
        (self.root / 'MANUAL.md').symlink_to(outside)
        result = self.run_checker()
        self.assertNotIn('PRIVATE SENTINEL', json.dumps(result))
        self.assertIn('SYMLINK', [e['type'] for e in result['errors']])

    def test_symlink_directory_is_rejected(self):
        outside = Path(self.temp.name) / 'external-research'
        (self.root / 'research').rename(outside)
        (self.root / 'research').symlink_to(outside, target_is_directory=True)
        self.run_checker()

    def test_symlink_manifest_is_rejected(self):
        outside = Path(self.temp.name) / 'external-manifest'
        (self.root / MANIFEST).rename(outside)
        (self.root / MANIFEST).symlink_to(outside)
        self.run_checker()

    def test_symlink_root_is_rejected(self):
        linked = Path(self.temp.name) / 'linked'
        linked.symlink_to(self.root, target_is_directory=True)
        self.run_checker(root=linked)

    def test_special_file_is_rejected_without_blocking(self):
        os.mkfifo(self.root / 'unlisted-pipe')
        self.run_checker()

    def test_unavailable_root_or_manifest_returns_two(self):
        self.run_checker(expected=2, root=self.root / 'missing')
        self.run_checker(expected=2, root=self.root / 'MANUAL.md')
        (self.root / MANIFEST).unlink()
        self.run_checker(expected=2)

    def test_invalid_json_and_types_are_inconsistencies(self):
        for data in (b'{', b'\xff', b'[]', b'null', b'{"files":null}',
                     b'{"schema":"x","schema":"y"}'):
            with self.subTest(data=data):
                (self.root / MANIFEST).write_bytes(data)
                self.run_checker()

    def test_non_list_files_and_non_object_rows_are_rejected(self):
        for entries in (None, {}, 'files', [None], ['path']):
            with self.subTest(entries=entries):
                self.document['files'] = entries
                self.write_manifest()
                self.run_checker()

    def test_failed_check_also_does_not_write(self):
        (self.root / 'unlisted.txt').write_text('extra')
        before = snapshot(self.root)
        self.run_checker()
        self.assertEqual(snapshot(self.root), before)

    def test_argument_errors_use_exit_two_without_private_paths(self):
        self.run_checker(expected=2, extra=('--unknown', str(self.base)))

    def test_missing_safe_filesystem_capabilities_return_two(self):
        # Fault injection is confined to a child process. Removing a required
        # real OS capability must fail closed before reading the edition.
        # Preload argparse's lazy stdlib dependency before OS fault injection;
        # the probes exercise this checker's boundary, not Python bootstrap.
        wrapper = '''import os, runpy, shutil, sys
checker = runpy.run_path(sys.argv[1])
script, root, mode, capability = sys.argv[1:5]
if mode == 'attribute':
    delattr(os, capability)
else:
    getattr(os, capability).discard(getattr(os, sys.argv[5]))
if mode == 'attribute' and capability in (
        'open', 'close', 'read', 'fstat', 'lstat', 'stat', 'scandir'):
    # Python's CLI bootstrap itself needs these APIs; exercise verify()'s
    # boundary directly after loading, as in the independent review probe.
    result = checker['verify'](checker['Path'](root))
    print(checker['json'].dumps(result))
    raise SystemExit(result['exit_code'])
sys.argv = [script, '--edition-root', root]
raise SystemExit(checker['main']())
'''
        probes = [('attribute', name) for name in (
            'O_RDONLY', 'O_DIRECTORY', 'O_NOFOLLOW', 'O_NONBLOCK',
            'open', 'close', 'read', 'fstat', 'lstat', 'stat', 'scandir',
            'supports_dir_fd', 'supports_fd', 'supports_follow_symlinks')]
        probes += [('support', 'supports_dir_fd', 'open'),
                   ('support', 'supports_dir_fd', 'stat'),
                   ('support', 'supports_fd', 'scandir'),
                   ('support', 'supports_follow_symlinks', 'stat')]
        before = snapshot(self.root)
        for probe in probes:
            with self.subTest(probe=probe):
                result = subprocess.run([
                    sys.executable, '-I', '-B', '-c', wrapper,
                    str(self.root / 'verificar_edicao.py'), str(self.root), *probe],
                    cwd=self.base,
                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                    text=True, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(result.stderr, '')
                parsed = json.loads(result.stdout)
                self.assertFalse(parsed['ok'])
                self.assertEqual(parsed['exit_code'], 2)
                self.assertEqual(parsed['checked_files'], 0)
                self.assertEqual(parsed['errors'], [
                    {'type': 'CAPABILITY_UNAVAILABLE', 'path': '.'}])
                self.assertNotIn(str(self.base), result.stdout)
        self.assertEqual(snapshot(self.root), before)


if __name__ == '__main__':
    unittest.main()

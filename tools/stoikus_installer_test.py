#!/usr/bin/env python3
"""Adversarial payload / release metadata tests using temporary real archives."""
import hashlib
import ast
import base64
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_leverage_package import MANIFEST_PATH, PRODUCT, build, validate_installer_record, INSTALLER_RELEASE_PREFIX

def module():
    path = ROOT / 'tools/stoikus-installer/prepare_payload.py'
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location('stoikus_payload', path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

class PayloadTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='jpw-installer-test-')
        self.root = Path(self.scratch.name)
        shutil.copytree(ROOT / 'downloads/jpw-alavancagem-atual', self.root / 'downloads/jpw-alavancagem-atual')
        shutil.copytree(ROOT / PRODUCT, self.root / PRODUCT)
        self.prepare = module()
        self.assertIsNotNone(self.prepare, 'dedicated verified payload generator is missing')

    def tearDown(self):
        self.scratch.cleanup()

    def metadata(self):
        return json.loads((self.root / MANIFEST_PATH).read_text())

    def save(self, manifest):
        (self.root / MANIFEST_PATH).write_text(json.dumps(manifest))

    def rewrite(self, mutate):
        manifest = self.metadata()
        record = manifest['downloads']['dailySource']
        path = self.root / record['path']
        with zipfile.ZipFile(path) as archive:
            members = [(i.filename, archive.read(i)) for i in archive.infolist()]
        members = mutate(members)
        with zipfile.ZipFile(path, 'w') as archive:
            for name, content in members:
                archive.writestr(name, content)
        raw = path.read_bytes()
        record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        self.save(manifest)

    def test_complete_deterministic_identity_and_safe_legacy_catalog(self):
        result = self.prepare.prepare(self.root)
        raw = (self.root / result['payloadPath']).read_bytes()
        manifest = result['manifest']
        self.assertEqual(raw, (self.root / self.metadata()['downloads']['dailySource']['path']).read_bytes())
        self.assertEqual(len(manifest['files']), 86)
        self.assertEqual(len(manifest['programs']), 4)
        self.assertEqual({p['role'] for p in manifest['programs']}, {'monitor', 'account', 'nocuda', 'openPanels'})
        current = {f['path'] for f in manifest['files']}
        self.assertTrue(all(f['path'].startswith('MQL5/') and f['path'] not in current and Path(f['path']).suffix in ('.mq5', '.ex5') for f in manifest['legacyFiles']))
        self.assertTrue(any(f['path'].endswith('JPW_Stoikus_Supervisor.mq5') for f in manifest['legacyFiles']))
        self.assertTrue(any(f['path'].endswith('.ex5') for f in manifest['knownFiles']))
        self.assertEqual(len(manifest['knownFiles']), len({(f['path'],f['sha256']) for f in manifest['knownFiles']}))
        self.assertEqual(result, self.prepare.prepare(self.root))

    def test_current_release_identity_and_fixed_four_program_roles(self):
        result = self.prepare.prepare(self.root)
        payload = result['manifest']
        self.assertEqual(payload['productVersion'], '1.23.0')
        self.assertEqual(payload['calculationVersion'], '1.9.0')
        self.assertEqual(self.metadata()['downloads']['dailySource']['filename'], 'JPW_Stoikus_Uso_Fontes_v1.23.0.zip')
        self.assertEqual(payload['archiveSha256'], '0bc6c856410b576ebf0412aa341056e8e02463c8f848fe34d2bd4e983ae5f7a3')
        self.assertEqual({p['source'] for p in payload['programs']}, {
            'MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5',
            'MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5',
            'MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5',
            'MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5'})
        self.assertTrue(all(p['output'] == p['source'][:-4] + '.ex5' for p in payload['programs']))

    def test_refuses_other_product_version_without_writing_payload(self):
        manifest = self.metadata()
        for version in ['1.22.1', '1.23.1', '99.0.0']:
            with self.subTest(version=version):
                manifest['version'] = version
                self.save(manifest)
                with self.assertRaisesRegex(ValueError, 'Unsupported product manifest'):
                    self.prepare.prepare(self.root)
                self.assertFalse((self.root / self.prepare.GENERATED).exists())

    def test_refuses_archive_filename_mismatch_before_payload_generation(self):
        manifest = self.metadata()
        manifest['downloads']['dailySource']['filename'] = 'JPW_Stoikus_Uso_Fontes_v1.22.1.zip'
        self.save(manifest)
        with self.assertRaises(ValueError):
            self.prepare.prepare(self.root)
        self.assertFalse((self.root / self.prepare.GENERATED).exists())

    def test_rejects_archive_source_and_historical_mutation(self):
        for kind in ('daily', 'source', 'history'):
            with self.subTest(kind=kind):
                if kind == 'daily': path = self.root / self.metadata()['downloads']['dailySource']['path']
                elif kind == 'source': path = self.root / PRODUCT / 'MQL5/Include/JPWealth/JPW_Stoikus_Risk_Core.mqh'
                else: path = self.root / 'downloads/jpw-alavancagem-atual/JPW_Genetrix_Fontes_v1.20.0.zip'
                original = path.read_bytes()
                path.write_bytes(original + b'tamper')
                with self.assertRaises(ValueError): self.prepare.prepare(self.root)
                path.write_bytes(original)

    def test_rejects_traversal_case_duplicates_unexpected_and_missing_members(self):
        manifest = self.metadata()
        daily_path = self.root / manifest['downloads']['dailySource']['path']
        raw = daily_path.read_bytes()
        transforms = [lambda m: m + [('MQL5/../evil.mq5', b'evil')],
                      lambda m: m + [(m[0][0].lower(), m[0][1])],
                      lambda m: m + [('MQL5/Files/private.lock', b'unsafe')],
                      lambda m: m[:-1],
                      lambda m: [(n, b'tampered' if n.endswith('Risk_Core.mqh') else b) for n,b in m]]
        for transform in transforms:
            self.rewrite(transform)
            with self.assertRaises(ValueError): self.prepare.prepare(self.root)
            daily_path.write_bytes(raw)
            self.save(manifest)

    def test_portable_never_embeds_future_executable(self):
        source = (ROOT / 'tools/rebuild_monolith.py').read_text()
        tree = ast.parse(source)
        node = next(n for n in tree.body if isinstance(n, ast.Assign) and
                    any(isinstance(t, ast.Name) and t.id == 'leverage_downloads' for t in n.targets))
        downloads = {'dailySource': {'available': True}, 'installer': {'available': True},
                     'source': {'available': True}, 'compiled': {'available': False}}
        result = eval(compile(ast.Expression(node.value), 'official-delivery-expression', 'eval'),
                      {'leverage_manifest': {'downloads': downloads}})
        self.assertEqual(set(result), {'dailySource', 'source'})

    def available_record(self, raw=b'MZ synthetic EXE fixture - never native evidence', suffix='.json'):
        record = self.prepare.unavailable_installer_record()
        sha = hashlib.sha256(raw).hexdigest()
        record.update(available=True, path='downloads/jpw-alavancagem-atual/' + record['filename'],
                      releaseUrl=INSTALLER_RELEASE_PREFIX + 'fixture/' + record['filename'],
                      sha256=sha, bytes=len(raw), nativeTests={s: 'PASS' for s in record['nativeTests']}, nativeEvidence={})
        (self.root / record['path']).write_bytes(raw)
        for stage in record['nativeTests']:
            relative = 'docs/validation/fixture/' + stage + suffix
            receipt = self.root / relative
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text(json.dumps({'candidateSha256': sha, 'stage': stage, 'status': 'PASS'}))
            record['nativeEvidence'][stage] = {'path': relative, 'sha256': hashlib.sha256(receipt.read_bytes()).hexdigest()}
        return record

    def test_available_metadata_rejects_empty_executable(self):
        record = self.available_record(raw=b'')
        with self.assertRaises(ValueError): validate_installer_record(self.root, record, '1.23.0')

    def test_available_metadata_rejects_receipt_paths_incompatible_with_browser(self):
        for suffix in ('.txt', '-ação.json'):
            with self.subTest(suffix=suffix):
                record = self.available_record(suffix=suffix)
                with self.assertRaises(ValueError): validate_installer_record(self.root, record, '1.23.0')

    def test_available_metadata_requires_candidate_bytes_and_stage_receipts(self):
        record = self.available_record()
        validate_installer_record(self.root, record, '1.23.0')
        for delta in ({'releaseUrl': 'https://evil.example/file.exe'}, {'sha256': '0' * 64}, {'nativeEvidence': {}}):
            with self.assertRaises(ValueError):
                validate_installer_record(self.root, dict(record, **delta), '1.23.0')
        receipt = self.root / record['nativeEvidence']['browser']['path']
        receipt.write_text(json.dumps({'candidateSha256': '0' * 64, 'stage': 'browser', 'status': 'PASS'}))
        record['nativeEvidence']['browser']['sha256'] = hashlib.sha256(receipt.read_bytes()).hexdigest()
        with self.assertRaises(ValueError): validate_installer_record(self.root, record, '1.23.0')

    def test_build_environment_preserves_overrides_and_uses_platform_temp_defaults(self):
        import os
        import tempfile
        sys.path.insert(0, str(ROOT / 'tools/stoikus-installer'))
        spec = importlib.util.spec_from_file_location('installer_build', ROOT / 'tools/stoikus-installer/build.py')
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        self.assertTrue(hasattr(helper, 'build_environment'), 'portable build environment helper is missing')
        override = {'DOTNET_CLI_HOME': str(self.root / 'home'), 'NUGET_PACKAGES': str(self.root / 'packages')}
        self.assertEqual({k: helper.build_environment(override)[k] for k in override}, override)
        defaults = helper.build_environment({})
        self.assertEqual(Path(defaults['DOTNET_CLI_HOME']), Path(tempfile.gettempdir()) / 'jpw-dotnet-home')
        self.assertEqual(Path(defaults['NUGET_PACKAGES']), Path(tempfile.gettempdir()) / 'jpw-nuget')

    def test_optional_installer_record_preserved_and_false_release_refused(self):
        record = self.prepare.unavailable_installer_record()
        manifest = self.metadata()
        manifest['downloads']['installer'] = record
        self.save(manifest)
        self.assertEqual(build(self.root)['downloads'].get('installer'), record)
        for delta in ({'available': True}, {'filename': '../bad.exe'}, {'productVersion': '0.0.0'}):
            bad = dict(record, **delta)
            manifest['downloads']['installer'] = bad
            self.save(manifest)
            with self.assertRaises(ValueError): build(self.root)

if __name__ == '__main__': unittest.main(verbosity=2)

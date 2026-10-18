#!/usr/bin/env python3
"""Independent sealed Interface R4 archive and adversarial distribution contract."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import shutil
import unittest
import zipfile

from build_leverage_package import ROOT, MANIFEST_PATH, OUTPUT, PRODUCT, build
from leverage_package_test import EXPECTED_MEMBERS, R5_MEMBERS, assert_release_inventory
from stoikus_daily_package_test import DAILY_MEMBERS, R5_DAILY_MEMBERS, check_archive

ASSETS = {
    'nativeKit': ('Kit_Windows_Stoikus_Assinatura_R4.zip', '86b9fb52e811c953f2e142f7670327685748bf75848c0ce2bea644eaa664d474'),
    'nativePin': ('root-pin-R4.json', '009cd46d458a4a85c14a0cae0c76ea9d730b47656304d36dfb7552fb952e8932'),
    'preview': ('Previa_Stoikus_Interface_R4.html', 'b1e44151cc4acf5fa96fb0bb0a349b2ecab0ca631e59649629c253adb83f70f2'),
}
NATIVE_FIELDS = ('nativeCompilation', 'nativeRuntime', 'humanAcceptance', 'windowsX64')
DAILY_SHA256 = '0b3d6b2ba9897a04262baf703282dfe84abdeb19ab26e39c3da21bf31e5855ef'
BUILD_ID = '45beb82e9366197542bfa5c7084a28bc05dd6b155f5a3777fdaa95f15b67239d'
MQL_FINGERPRINT = 'b2b0afc9535816685decb8d5860a90fee35642b1ea3e6720523ecd8145c00d81'


def release_contract(root):
    artifacts = {}
    for kind, (name, digest) in ASSETS.items():
        raw = (root / OUTPUT / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest, name
        artifacts[kind] = dict(available=True, path=OUTPUT + name, filename=name, sha256=digest, bytes=len(raw))
    return dict(revision='R4', candidate='1.22.3-interface', archiveVariant='interface',
                state='SOURCE_ONLY_NATIVE_PENDING', artifacts=artifacts,
                **{key: 'NOT_RUN' for key in NATIVE_FIELDS})


class InterfacePackageTests(unittest.TestCase):
    version = '1.22.3'
    assets = ASSETS
    members = EXPECTED_MEMBERS
    daily_members = DAILY_MEMBERS
    daily_sha256 = DAILY_SHA256
    build_id = BUILD_ID
    fingerprint = MQL_FINGERPRINT
    variant = 'interface'

    def release_contract(self):
        artifacts = {}
        for kind, (name, digest) in self.assets.items():
            raw = (self.root / OUTPUT / name).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == digest, name
            artifacts[kind] = dict(available=True, path=OUTPUT + name, filename=name, sha256=digest, bytes=len(raw))
        return dict(revision='R5' if self.version == '1.23.0' else 'R4', candidate=self.version + '-interface',
                    archiveVariant=self.variant, state='SOURCE_ONLY_NATIVE_PENDING', artifacts=artifacts,
                    **{key: 'NOT_RUN' for key in NATIVE_FIELDS})

    def setUp(self):
        self.temporary = TemporaryDirectory(prefix='jpw-interface-distribution-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.manifest = json.loads((ROOT / MANIFEST_PATH).read_text())
        self.manifest.pop('interfaceRelease', None)
        # Reconstruct an independent historical release, without a current-version optional installer.
        self.manifest.get('downloads', {}).pop('installer', None)
        self.manifest['version'] = self.version
        self.manifest['sourceFiles'] = sorted(PRODUCT + name for name in self.members)
        self.populate_sources()
        (self.root / OUTPUT).mkdir(parents=True)
        for source in (ROOT / OUTPUT).glob('*.zip'):
            if not source.name.endswith('_interface.zip') and source.name != self.assets['nativeKit'][0]:
                shutil.copyfile(source, self.root / OUTPUT / source.name)
        for name, _ in self.assets.values():
            shutil.copyfile(ROOT / OUTPUT / name, self.root / OUTPUT / name)
        self.manifest['interfaceRelease'] = self.release_contract()
        self.save()

    def populate_sources(self):
        raw = (ROOT / OUTPUT / f'JPW_Stoikus_Fontes_v{self.version}{"_" + self.variant if self.variant else ""}.zip').read_bytes()
        assert len(raw) == 790705
        assert hashlib.sha256(raw).hexdigest() == '736df358a40fbf15fca52432b44db406cd4677eccd2b5d5f147a9ebb6fe11be2'
        with zipfile.ZipFile(__import__('io').BytesIO(raw)) as archive:
            assert set(archive.namelist()) == EXPECTED_MEMBERS
            archive.extractall(self.root / PRODUCT)

    def save(self):
        (self.root / MANIFEST_PATH).write_text(json.dumps(self.manifest))

    def snapshot(self):
        return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob('*') if path.is_file()}

    def rejected(self, manifest, label):
        self.manifest = manifest
        self.save()
        before = self.snapshot()
        with self.assertRaises((ValueError, FileNotFoundError), msg=label):
            build(self.root)
        self.assertEqual(self.snapshot(), before, 'rejection mutated bytes: ' + label)

    def test_interface_names_sealed_bytes_and_idempotence(self):
        before = self.snapshot()
        first = build(self.root)
        self.assertEqual(first['downloads']['source']['filename'], f'JPW_Stoikus_Fontes_v{self.version}{"_" + self.variant if self.variant else ""}.zip')
        self.assertEqual(first['downloads']['dailySource']['filename'], f'JPW_Stoikus_Uso_Fontes_v{self.version}{"_" + self.variant if self.variant else ""}.zip')
        assert_release_inventory(first)
        check_archive(self.root, first, 'source', self.members)
        check_archive(self.root, first, 'dailySource', self.daily_members)
        self.assertEqual(first['downloads']['dailySource']['sha256'], self.daily_sha256)
        self.assertEqual(first['runtimeBuildId'], self.build_id)
        self.assertEqual(first['mqlSourceFingerprint'], self.fingerprint)
        self.assertEqual(first['interfaceRelease'], self.release_contract())
        self.assertFalse(first['downloads']['compiled']['available'])
        for path, digest in before.items():
            if path != MANIFEST_PATH:
                self.assertEqual(hashlib.sha256((self.root / path).read_bytes()).hexdigest(), digest, path)
        mtimes = {path: path.stat().st_mtime_ns for path in self.root.rglob('*') if path.is_file()}
        self.assertEqual(build(self.root), first)
        self.assertEqual({p: p.stat().st_mtime_ns for p in mtimes}, mtimes)

    def test_absent_contract_keeps_default_names_and_archive_bytes(self):
        interface = build(self.root)
        self.manifest.pop('interfaceRelease')
        self.save()
        default = build(self.root)
        for kind in ('source', 'dailySource'):
            self.assertEqual(default['downloads'][kind]['filename'], interface['downloads'][kind]['filename'].replace('_interface.zip', '.zip'))
            self.assertEqual(default['downloads'][kind]['sha256'], interface['downloads'][kind]['sha256'])
            self.assertEqual(default['downloads'][kind]['bytes'], interface['downloads'][kind]['bytes'])
        self.assertNotIn('interfaceRelease', default)

    def test_invalid_release_values_and_unbounded_keys_rejected(self):
        original = deepcopy(self.manifest)
        for key, values in {
            'revision': ('R2', '', None, 3), 'candidate': ('1.22.4-interface', None),
            'archiveVariant': ('interface' if not self.variant else '', '../interface', '/interface', 'interface.zip', True, None),
            'state': ('PASS', 'COMPILED', None), **{key: ('PASS', None) for key in NATIVE_FIELDS},
        }.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    changed = deepcopy(original); changed['interfaceRelease'][key] = value
                    self.rejected(changed, key)
        for value in (None, [], 'interface', {}, dict(original['interfaceRelease'], extra=True)):
            with self.subTest(value=value):
                changed = deepcopy(original); changed['interfaceRelease'] = value
                self.rejected(changed, 'invalid release schema')
        for key in original['interfaceRelease']:
            changed = deepcopy(original); del changed['interfaceRelease'][key]
            self.rejected(changed, 'missing release field ' + key)

    def test_artifact_inventory_metadata_and_unsafe_paths_rejected(self):
        original = deepcopy(self.manifest)
        mutations = {
            'available': (False, 1, None), 'filename': ('renamed.zip', None),
            'sha256': ('0' * 64, '', None), 'bytes': (0, -1, True, '10', 10),
            'path': ('../root-pin-R4.json', '/root-pin-R4.json', OUTPUT + '../root-pin-R4.json',
                     OUTPUT + 'subdir/root-pin-R4.json', 'https://example.com/root-pin-R4.json',
                     OUTPUT + 'root-pin-R4.json?x=1', OUTPUT + 'root-pin-R4.json#fragment',
                     OUTPUT + 'root-pin-R4.ex5', OUTPUT + 'Kit_Windows_Stoikus_Assinatura_R4.zip'),
        }
        for key, values in mutations.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    changed = deepcopy(original); changed['interfaceRelease']['artifacts']['nativePin'][key] = value
                    self.rejected(changed, 'artifact ' + key)
        for kind in self.assets:
            changed = deepcopy(original); del changed['interfaceRelease']['artifacts'][kind]
            self.rejected(changed, 'missing artifact ' + kind)
        changed = deepcopy(original); changed['interfaceRelease']['artifacts']['arbitrary'] = {}
        self.rejected(changed, 'extra artifact')
        for value in (None, [], 'files'):
            changed = deepcopy(original); changed['interfaceRelease']['artifacts'] = value
            self.rejected(changed, 'invalid artifact inventory')
        for key in original['interfaceRelease']['artifacts']['nativePin']:
            changed = deepcopy(original); del changed['interfaceRelease']['artifacts']['nativePin'][key]
            self.rejected(changed, 'missing metadata ' + key)
        changed = deepcopy(original); changed['interfaceRelease']['artifacts']['nativePin']['extra'] = True
        self.rejected(changed, 'unbounded metadata')

    def test_missing_corrupt_and_symlink_assets_rejected_even_with_coherent_metadata(self):
        original = deepcopy(self.manifest)
        for kind, (name, _) in self.assets.items():
            target = self.root / OUTPUT / name; raw = target.read_bytes()
            target.unlink(); self.rejected(deepcopy(original), 'missing ' + kind)
            target.write_bytes(raw[:-1])
            changed = deepcopy(original)
            record = changed['interfaceRelease']['artifacts'][kind]
            record['sha256'] = hashlib.sha256(raw[:-1]).hexdigest(); record['bytes'] = len(raw)-1
            self.rejected(changed, 'coherent corrupt ' + kind)
            target.unlink()
            outside = self.root / name; outside.write_bytes(raw)
            target.symlink_to(outside)
            self.rejected(deepcopy(original), 'symlink ' + kind)
            target.unlink(); target.write_bytes(raw); outside.unlink()

    def test_source_identity_and_guide_corruption_rejected(self):
        original = deepcopy(self.manifest)
        for member in ('MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh', 'STOIKUS_USO_DIARIO.md'):
            target = self.root / PRODUCT / member; raw = target.read_bytes()
            target.write_bytes(raw + b'\n// unauthorized byte change\n')
            self.rejected(deepcopy(original), 'changed sealed source ' + member)
            target.write_bytes(raw)
        for kind in ('duplicate', 'substitute'):
            changed = deepcopy(original)
            changed['sourceFiles'][-1] = changed['sourceFiles'][0] if kind == 'duplicate' else PRODUCT + 'rogue.md'
            with self.assertRaises(AssertionError): assert_release_inventory(changed)
            self.rejected(changed, 'source inventory ' + kind)

    def test_interface_rejects_native_promotion_and_unproved_ex5(self):
        original = deepcopy(self.manifest)
        for mutation in ('status', 'artifact', 'ex5', 'compiled-default', 'compiled-interface'):
            changed = deepcopy(original); generated = None
            if mutation == 'status': changed['validation']['compilation']['status'] = 'passed'
            elif mutation == 'artifact': changed['nativeArtifact'] = {'cpu': 'X64 Regular', 'artifacts': []}
            elif mutation == 'ex5':
                generated = self.root / PRODUCT / 'MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.ex5'
            else:
                generated = self.root / OUTPUT / ('JPW_Stoikus_Compilado_v' + self.version + ('_' + self.variant if mutation.endswith('interface') and self.variant else '') + '.zip')
            if generated: generated.write_bytes(b'fake compiler proof' * 100)
            self.rejected(changed, mutation)
            if generated: generated.unlink()


def candidate():
    """Validate the generated public candidate without writing to its inputs."""
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text())
    if manifest["version"] == "1.23.0":
        from stoikus_r5_release_test import candidate as r5_candidate
        return r5_candidate()
    assert manifest['interfaceRelease'] == release_contract(ROOT)
    assert manifest['runtimeBuildId'] == BUILD_ID
    assert manifest['mqlSourceFingerprint'] == MQL_FINGERPRINT
    assert manifest['nativeArtifact'] is None
    assert not manifest['downloads']['compiled']['available']
    assert manifest['validation']['compilation']['status'] == 'pending'
    assert manifest['validation']['terminal']['status'] == 'pending'
    assert_release_inventory(manifest)
    assert manifest['downloads']['source']['filename'] == 'JPW_Stoikus_Fontes_v1.22.3_interface.zip'
    assert manifest['downloads']['dailySource']['filename'] == 'JPW_Stoikus_Uso_Fontes_v1.22.3_interface.zip'
    check_archive(ROOT, manifest, 'source', EXPECTED_MEMBERS)
    check_archive(ROOT, manifest, 'dailySource', DAILY_MEMBERS)
    assert manifest['downloads']['dailySource']['sha256'] == DAILY_SHA256
    pin = json.loads((ROOT / OUTPUT / 'root-pin-R4.json').read_text())
    assert pin['source_zip_sha256'] == DAILY_SHA256
    assert pin['mql_source_fingerprint'] == MQL_FINGERPRINT
    assert pin['runtime_build_id'] == BUILD_ID
    assert pin['kit_package_sha256'] == ASSETS['nativeKit'][1]
    print('PASS generated Interface R4 candidate, three sealed artifacts and exact kit/daily binding; native NOT_RUN')


def controls():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(InterfacePackageTests)
    from stoikus_r5_release_test import R5ReleaseTests
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(R5ReleaseTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise AssertionError('Interface R4 package controls failed')


if __name__ == '__main__':
    controls()

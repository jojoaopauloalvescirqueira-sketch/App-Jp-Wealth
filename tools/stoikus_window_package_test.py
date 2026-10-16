"""Candidate packaging behavior; does not certify native compilation/runtime."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import tempfile
import unittest
import zipfile

from build_stoikus_window_candidate import prepare, verify
from build_leverage_package import make_archive

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = 'mt5/jpw-alavancagem-atual/'


def digest_tree(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class CandidatePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='stoikus-window-package-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.root = self.home / 'project'
        shutil.copytree(ROOT / PRODUCT, self.root / PRODUCT)
        downloads = self.root / 'downloads/jpw-alavancagem-atual'
        downloads.mkdir(parents=True)
        shutil.copyfile(ROOT / 'downloads/jpw-alavancagem-atual/manifest.json', downloads / 'manifest.json')
        (downloads / 'historical.zip').write_bytes(b'historical fixture - must remain byte identical')
        version = self.root / PRODUCT / 'MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh'
        text = re.sub(r'(#define JPW_PRODUCT_VERSION )"[^"]+"', r'\1"1.23.0"', version.read_text())
        text = re.sub(r'(#define JPW_PRODUCT_MQL_VERSION )"[^"]+"', r'\1"1.230"', text)
        version.write_text(text)
        self.output = self.home / 'candidate'

    def test_reproducible_complete_daily_inventory_and_source_preservation(self):
        before = digest_tree(self.root)
        one = prepare(self.root, self.output)
        other = self.home / 'second'
        two = prepare(self.root, other)
        self.assertEqual(one, two)
        self.assertEqual(digest_tree(self.root), before)
        checked = verify(self.output)
        self.assertEqual(checked['productVersion'], '1.23.0')
        self.assertEqual(checked['calculationVersion'], '1.9.0')
        self.assertEqual(checked['nativeCompilation'], 'NOT_RUN')
        with zipfile.ZipFile(self.output / 'JPW_Stoikus_Uso_Fontes_v1.23.0.zip') as archive:
            programs = [p for p in archive.namelist() if p.endswith('.mq5')]
            self.assertEqual(len(programs), 4)
            self.assertTrue(all(not p.endswith('.ex5') for p in archive.namelist()))
            self.assertIn('LEIA_PRIMEIRO.md', archive.namelist())

    def test_existing_output_is_not_replaced(self):
        self.output.mkdir()
        marker = self.output / 'keep'
        marker.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):
            prepare(self.root, self.output)
        self.assertEqual(marker.read_bytes(), b'keep')

    def test_missing_dependency_fails_without_output_or_source_mutation(self):
        victim = self.root / PRODUCT / 'MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh'
        victim.unlink()
        before = digest_tree(self.root)
        with self.assertRaises((ValueError, FileNotFoundError)):
            prepare(self.root, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(digest_tree(self.root), before)

    def test_unproved_ex5_is_rejected(self):
        target = self.root / PRODUCT / 'MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.ex5'
        target.write_bytes(b'old binary')
        with self.assertRaisesRegex(ValueError, 'EX5'):
            prepare(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_version_or_financial_calculation_mismatch_is_rejected(self):
        version = self.root / PRODUCT / 'MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh'
        version.write_text(version.read_text().replace('"1.9.0"', '"2.0.0"'))
        with self.assertRaisesRegex(ValueError, 'vers'):
            prepare(self.root, self.output)
        self.assertFalse(self.output.exists())

    def repin(self, identity, manifest):
        for name, value in [('identity.json', identity), ('candidate-manifest.json', manifest)]:
            (self.output / name).write_text(json.dumps(value))
        pin = json.loads((self.output / 'root-pin.json').read_text())
        pin['identitySha256'] = hashlib.sha256((self.output / 'identity.json').read_bytes()).hexdigest()
        pin['manifestSha256'] = hashlib.sha256((self.output / 'candidate-manifest.json').read_bytes()).hexdigest()
        (self.output / 'root-pin.json').write_text(json.dumps(pin))

    def test_commented_expected_calculation_does_not_approve_other_active_version(self):
        version = self.root / PRODUCT / 'MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh'
        text = version.read_text().replace('#define JPW_CALCULATION_VERSION "1.9.0"',
            '// #define JPW_CALCULATION_VERSION "1.9.0"\n#define JPW_CALCULATION_VERSION "2.0.0"')
        version.write_text(text)
        with self.assertRaisesRegex(ValueError, 'vers'):
            prepare(self.root, self.output)

    def test_verifier_requires_both_archives_even_with_coherent_local_pin(self):
        prepare(self.root, self.output)
        identity = json.loads((self.output / 'identity.json').read_text())
        manifest = json.loads((self.output / 'candidate-manifest.json').read_text())
        identity['downloads'].pop('dailySource')
        manifest['downloads'].pop('dailySource')
        self.repin(identity, manifest)
        with self.assertRaisesRegex(ValueError, 'archive|download|Archive|invent'):
            verify(self.output)

    def test_verifier_requires_daily_dependency_closure_even_with_coherent_local_pin(self):
        prepare(self.root, self.output)
        identity = json.loads((self.output / 'identity.json').read_text())
        manifest = json.loads((self.output / 'candidate-manifest.json').read_text())
        path = self.output / identity['downloads']['dailySource']['filename']
        with zipfile.ZipFile(path) as archive:
            members = [(name, archive.read(name)) for name in archive.namelist()
                       if name != 'MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh']
        raw = make_archive(members)
        path.write_bytes(raw)
        record = identity['downloads']['dailySource']
        record['sha256'], record['bytes'] = hashlib.sha256(raw).hexdigest(), len(raw)
        manifest['downloads']['dailySource'] = record
        self.repin(identity, manifest)
        with self.assertRaisesRegex(ValueError, 'depend|invent'):
            verify(self.output)

    def test_tampered_archive_is_rejected_by_verifier(self):
        prepare(self.root, self.output)
        target = self.output / 'JPW_Stoikus_Uso_Fontes_v1.23.0.zip'
        target.write_bytes(target.read_bytes() + b'altered')
        with self.assertRaisesRegex(ValueError, 'hash|SHA|bytes'):
            verify(self.output)


if __name__ == '__main__':
    unittest.main(verbosity=2)

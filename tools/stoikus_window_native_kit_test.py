"""Compile-only kit sealing tests; Windows execution remains NOT_RUN."""
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import unittest
from stoikus_window_package_test import CandidatePackageTests, digest_tree
import build_stoikus_window_candidate as candidate
import build_stoikus_window_native_kit as kit


class NativeKitTests(CandidatePackageTests):
    def setUp(self):
        super().setUp()
        guide = self.root / kit.official.DAILY_GUIDE
        guide.write_text("Candidato privado de interface JPW_Stoikus_Uso_Fontes_v1.23.0_interface.zip; recibo e demo pendentes.\n\n" + guide.read_text())
        candidate.prepare(self.root, self.output)
        self.preview = self.home / 'preview.html'
        self.preview.write_text('<html>fictional preview</html>')
        self.kit = self.home / 'kit'

    def build(self):
        return kit.prepare(self.output, self.preview, self.kit)

    def check_verifier(self, success):
        result = subprocess.run([sys.executable, str(self.kit / 'verify_native_ui_kit.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)

    def test_kit_identity_exact_core_and_positive_verifier(self):
        before = digest_tree(self.output)
        pin = self.build()
        historical = kit.historical_templates()
        self.assertEqual((self.kit / 'NativeKit.Core.ps1').read_bytes(), historical['NativeKit.Core.ps1'])
        self.assertEqual(digest_tree(self.output), before)
        self.assertEqual(pin['runtime_status'], 'NOT_RUN')
        self.check_verifier(True)
        identity = json.loads((self.kit / kit.IDENTITY).read_text())
        self.assertEqual(len(identity['programs']), 4)
        self.assertEqual(identity['zip']['sha256'], candidate.verify(self.output)['downloads']['dailySource']['sha256'])
        runner = (self.kit / 'Compile-Stoikus-UI.ps1').read_text()
        normalize = lambda text: re.sub(r"(?m)^(\$Pinned\w+=)'[a-f0-9]{64}'$", r"\1'<pin>'", text)
        self.assertEqual(normalize(runner), normalize(kit.adapt(historical['Compile-Stoikus-UI.ps1']).decode()))
        for name in ('verify_native_ui_kit.py', 'Test-NativeUI-Kit.ps1', 'identity.schema.json'):
            self.assertEqual((self.kit / name).read_bytes(), kit.adapt(historical[name]))
        for guard in ('Assert-NoRunningMetaEditor', 'Copy-StandardClosure', 'Stop-OwnedCompiler', 'Save-CompilerOutputs', 'Test-CompileLog', 'PinnedFreezeSha256'):
            self.assertIn(guard, runner)

    def test_freeze_v1_retains_canonical_complete_source_meaning(self):
        import hashlib
        self.build()
        freeze = json.loads((self.kit / kit.FREEZE).read_text())
        info = candidate.verify(self.output)
        expected = {kit.official.PRODUCT + key: value for key, value in info['sourceHashes'].items()}
        expected['docs/preview/stoikus-window-controls/index.html'] = hashlib.sha256(self.preview.read_bytes()).hexdigest()
        aggregate = hashlib.sha256(json.dumps(expected, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(freeze['source_hashes'], expected)
        self.assertEqual(freeze['interface_fingerprint'], aggregate)
        self.assertEqual(freeze['scope'], 'DECLARED_SDK_SOURCES_AND_PREVIEW_BEFORE_DISTRIBUTION_SEAL')
        with kit.zipfile.ZipFile(self.kit / kit.PAYLOAD) as archive:
            self.assertEqual(freeze['daily_entries'], len(archive.infolist()))
        for key in ('native_compilation', 'native_execution', 'human_acceptance', 'windows_x64'):
            self.assertEqual(freeze[key], 'NOT_RUN')
        # A source-only change with identical preview must change the V1 aggregate.
        source = self.root / kit.official.DAILY_GUIDE
        source.write_bytes(source.read_bytes() + b'\nSource-only fixture change.\n')
        changed_candidate = self.home / 'changed-candidate'
        candidate.prepare(self.root, changed_candidate)
        changed_kit = self.home / 'changed-kit'
        kit.prepare(changed_candidate, self.preview, changed_kit)
        changed = json.loads((changed_kit / kit.FREEZE).read_text())
        self.assertNotEqual(changed['interface_fingerprint'], freeze['interface_fingerprint'])
        self.assertEqual(changed['source_hashes']['docs/preview/stoikus-window-controls/index.html'], expected['docs/preview/stoikus-window-controls/index.html'])

    def test_guide_pin_receipt_and_external_archive_contract(self):
        import hashlib
        pin = self.build()
        guide = (self.kit / 'LEIA-PRIMEIRO.md').read_text()
        references = set(re.findall(r'\$pin\.([A-Za-z_][A-Za-z0-9_]*)', guide))
        self.assertFalse(references - set(pin), references - set(pin))
        self.assertIn('`' + kit.OUTER + '`', guide)
        self.assertNotIn('Kit_Windows_Stoikus_Assinatura_R5.zip', guide)
        identity = json.loads((self.kit / kit.IDENTITY).read_text())
        for field in ('root_freeze_sha256', 'mql_source_fingerprint', 'interface_fingerprint', 'runtime_build_id', 'calculation_version'):
            self.assertEqual(pin[field], identity['origin'][field])
        self.assertEqual(pin['source_zip_sha256'], identity['zip']['sha256'])
        raw = (self.kit / kit.OUTER).read_bytes()
        self.assertEqual(pin['kit_package_filename'], kit.OUTER)
        self.assertEqual(pin['kit_package_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(pin['kit_package_bytes'], len(raw))
        self.assertIn('reviews', pin)
        with kit.zipfile.ZipFile(self.kit / kit.OUTER) as archive:
            self.assertEqual(set(archive.namelist()), set(pin['files_sha256']))
            self.assertEqual(len(archive.namelist()), 9)
            self.assertNotIn('root-pin-R5.json', archive.namelist())
            for name in archive.namelist():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), pin['files_sha256'][name])

    def test_wrong_historical_hash_refused(self):
        bad = self.home / 'bad.zip'
        bad.write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError, 'historical'):
            kit.historical_templates(bad)

    def test_existing_and_symlink_outputs_preserved(self):
        self.kit.mkdir()
        (self.kit / 'keep').write_text('keep')
        with self.assertRaises(FileExistsError): self.build()
        self.assertEqual((self.kit / 'keep').read_text(), 'keep')
        link = self.home / 'link'
        link.symlink_to(self.home / 'missing')
        with self.assertRaises(FileExistsError): kit.prepare(self.output, self.preview, link)

    def test_verifier_rejects_corrupted_core_freeze_identity_payload_and_runner(self):
        self.build()
        for name in ['NativeKit.Core.ps1', kit.FREEZE, kit.IDENTITY, kit.PAYLOAD, 'Compile-Stoikus-UI.ps1', 'Test-NativeUI-Kit.ps1']:
            path = self.kit / name
            raw = path.read_bytes()
            path.write_bytes(raw + b'corruption')
            self.check_verifier(False)
            path.write_bytes(raw)
        self.check_verifier(True)

# Inherited packaging tests have their own setup assumptions; run only the kit cases.
for _name in list(vars(CandidatePackageTests)):
    if _name.startswith('test_'):
        setattr(NativeKitTests, _name, None)

if __name__ == '__main__': unittest.main()

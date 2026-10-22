"""Compile-only kit sealing tests; Windows execution remains NOT_RUN."""
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import unittest
import shutil
import hashlib
from stoikus_window_package_test import CandidatePackageTests, digest_tree
import build_stoikus_window_candidate as candidate
import build_stoikus_window_native_kit as kit


class NativeKitTests(CandidatePackageTests):
    def setUp(self):
        super().setUp()
        guide = self.root / kit.official.DAILY_GUIDE
        self.original_guide = guide.read_bytes()
        guide.write_text("Candidato privado de interface JPW_Stoikus_Uso_Fontes_v1.23.0_interface.zip; recibo e demo pendentes.\n\n" + guide.read_text())
        candidate.prepare(self.root, self.output)
        # Keep the historical preview-key oracle truthful inside a temporary root.
        historical_root = kit.ROOT
        archive_name, _ = kit.official.INTERFACE_ARTIFACTS['nativeKit']
        shutil.copy2(historical_root / kit.official.OUTPUT / archive_name,
                     self.root / kit.official.OUTPUT / archive_name)
        kit.ROOT = self.root
        self.addCleanup(setattr, kit, 'ROOT', historical_root)
        self.preview = self.root / 'docs/preview/stoikus-window-controls/index.html'
        self.preview.parent.mkdir(parents=True, exist_ok=True)
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


    def test_explicit_baseline_valid_and_invalid_without_output(self):
        baseline = 'ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34'
        kit.prepare(self.output, self.preview, self.kit, baseline_commit=baseline)
        freeze = json.loads((self.kit / kit.FREEZE).read_text())
        identity = json.loads((self.kit / kit.IDENTITY).read_text())
        self.assertEqual(freeze['baseline_commit'], baseline)
        self.assertEqual(identity['origin']['baseline_commit'], baseline)
        self.check_verifier(True)
        for index, invalid in enumerate(('', baseline[:-1], baseline+'0', baseline.upper(), 'g'*40)):
            with self.subTest(baseline=invalid):
                output = self.home / ('invalid-baseline-'+str(index))
                before = digest_tree(self.output)
                with self.assertRaisesRegex(ValueError, 'Baseline commit'):
                    kit.prepare(self.output, self.preview, output, baseline_commit=invalid)
                self.assertFalse(output.exists())
                self.assertEqual(digest_tree(self.output), before)

    def test_freeze_records_actual_current_preview_path(self):
        preview = self.root / 'docs/preview/stoikus-painel-personalizavel/index.html'
        preview.parent.mkdir(parents=True)
        preview.write_bytes(b'<html>current isolated preview</html>')
        kit.prepare(self.output, preview, self.kit)
        freeze = json.loads((self.kit / kit.FREEZE).read_text())
        relative = preview.relative_to(self.root).as_posix()
        expected = {kit.official.PRODUCT+key: value for key,value in candidate.verify(self.output)['sourceHashes'].items()}
        expected[relative] = hashlib.sha256(preview.read_bytes()).hexdigest()
        self.assertEqual(freeze['source_hashes'], expected)
        self.assertNotIn('docs/preview/stoikus-window-controls/index.html', freeze['source_hashes'])
        self.assertEqual(freeze['interface_fingerprint'], hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest())
        self.check_verifier(True)

    def test_outside_root_preview_refused_without_output(self):
        preview = self.home / 'outside-preview.html'
        preview.write_bytes(b'<html>outside source root</html>')
        before = digest_tree(self.output)
        with self.assertRaises(ValueError):
            kit.prepare(self.output, preview, self.kit)
        self.assertFalse(self.kit.exists())
        self.assertEqual(digest_tree(self.output), before)

    def ordinary_candidate(self):
        # The real failure used an ordinary daily guide, not the private prefix in setUp.
        (self.root / kit.official.DAILY_GUIDE).write_bytes(self.original_guide)
        output = self.home / 'ordinary-candidate'
        candidate.prepare(self.root, output)
        return output

    def test_ordinary_guide_derivation_preserves_original_and_exact_closure(self):
        source = self.ordinary_candidate()
        before = digest_tree(source)
        info = candidate.verify(source)
        pin = kit.prepare(source, self.preview, self.kit)
        with kit.zipfile.ZipFile(source / info['downloads']['dailySource']['filename']) as archive:
            original = {name:archive.read(name) for name in archive.namelist()}
        with kit.zipfile.ZipFile(self.kit / kit.PAYLOAD) as archive:
            derived = {name:archive.read(name) for name in archive.namelist()}
        self.assertEqual(set(original), set(derived))
        self.assertEqual([name for name in original if original[name]!=derived[name]], ['LEIA_PRIMEIRO.md'])
        guide = derived['LEIA_PRIMEIRO.md']
        self.assertTrue(guide.endswith(original['LEIA_PRIMEIRO.md']))
        prefix = guide[:-len(original['LEIA_PRIMEIRO.md'])].decode()
        for text in ('Candidato privado de interface',kit.PAYLOAD,kit.OUTER,'root-pin-R5.json','recibo','demo','NOT_RUN'):
            self.assertIn(text,prefix)
        self.assertEqual(original['LEIA_PRIMEIRO.md'],self.original_guide)
        self.assertNotEqual(pin['source_zip_sha256'],info['downloads']['dailySource']['sha256'])
        programs = {name for name in derived if name.endswith('.mq5')}
        self.assertEqual(programs,set(info['dailyPrograms']))
        self.assertEqual(len(programs),4)
        dependencies = {kit.official.PRODUCT+name:kit.official.local_dependencies(kit.official.PRODUCT+name,raw.decode())
                        for name,raw in original.items() if name.endswith(('.mq5','.mqh'))}
        closure = set(kit.official.DAILY_PROGRAMS)
        pending = list(closure)
        while pending:
            for dependency in dependencies.get(pending.pop(),set()):
                self.assertIn(dependency.removeprefix(kit.official.PRODUCT),derived)
                if dependency not in closure:
                    closure.add(dependency);pending.append(dependency)
        self.assertEqual({name for name in derived if name.startswith('MQL5/')},
                         {name.removeprefix(kit.official.PRODUCT) for name in closure})
        for name,raw in derived.items():
            if name.startswith('MQL5/'):
                self.assertEqual(raw,original[name])
                self.assertEqual(hashlib.sha256(raw).hexdigest(),info['sourceHashes'][name])
        freeze = json.loads((self.kit / kit.FREEZE).read_text())
        self.assertEqual(freeze['daily_entries'],len(derived))
        self.assertEqual(freeze['native_guide_derivation'],{
            'source_zip_sha256':info['downloads']['dailySource']['sha256'],
            'original_guide_sha256':hashlib.sha256(original['LEIA_PRIMEIRO.md']).hexdigest(),
            'native_guide_sha256':hashlib.sha256(guide).hexdigest()})
        self.assertEqual(digest_tree(source),before)
        self.check_verifier(True)

    def rebind_ordinary_hashes(self, folder):
        # Reach the unchanged semantic guards after normal entry/ZIP/pin rebinding.
        identity = json.loads((folder / kit.IDENTITY).read_text())
        pin = json.loads((folder / 'root-pin-R5.json').read_text())
        raw = (folder / kit.PAYLOAD).read_bytes()
        with kit.zipfile.ZipFile(folder / kit.PAYLOAD) as archive:
            identity['entries']=[{'path':name,'bytes':len(archive.read(name)),
                                 'sha256':hashlib.sha256(archive.read(name)).hexdigest()} for name in archive.namelist()]
        by_name={row['path']:row['sha256'] for row in identity['entries']}
        for row in identity['programs']:row['sha256']=by_name[row['path']]
        identity['zip'].update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
        runner=folder / 'Compile-Stoikus-UI.ps1'
        runner.write_text(re.sub(r"(?m)^\$PinnedZipSha256='[a-f0-9]{64}'$", "$PinnedZipSha256='"+identity['zip']['sha256']+"'",runner.read_text()))
        for row in identity['kit_files']:row['sha256']=hashlib.sha256((folder / row['name']).read_bytes()).hexdigest()
        (folder / kit.IDENTITY).write_bytes(kit.encode(identity))
        pin['source_zip_sha256']=identity['zip']['sha256']
        pin['files_sha256']={name:hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in pin['files_sha256']}
        outer=kit.official.make_archive([(name,(folder / name).read_bytes()) for name in pin['files_sha256']])
        (folder / kit.OUTER).write_bytes(outer)
        pin.update(kit_package_sha256=hashlib.sha256(outer).hexdigest(),kit_package_bytes=len(outer))
        (folder / 'root-pin-R5.json').write_bytes(kit.encode(pin))

    def test_derived_kit_rejects_rebound_source_guide_and_unbound_pin(self):
        source=self.ordinary_candidate()
        info=candidate.verify(source)
        kit.prepare(source,self.preview,self.kit)
        with kit.zipfile.ZipFile(self.kit / kit.PAYLOAD) as archive:
            original={name:archive.read(name) for name in archive.namelist()}
        for label,expected in [('source','source freeze differs'),('guide','inner guide private-candidate/ZIP mismatch'),
                               ('runner','runner pin PinnedFreezeSha256'),('root','pin runtime_build_id')]:
            with self.subTest(mutation=label):
                folder=self.home / ('rebound-'+label)
                shutil.copytree(self.kit,folder)
                if label in ('source','guide'):
                    members=dict(original)
                    if label=='source':members[info['dailyPrograms'][0]]+=b'\n// tamper\n'
                    else:members['LEIA_PRIMEIRO.md']=self.original_guide
                    (folder / kit.PAYLOAD).write_bytes(kit.official.make_archive(list(members.items())))
                elif label=='runner':
                    runner=folder / 'Compile-Stoikus-UI.ps1'
                    text,count=re.subn(r"(?m)^\$PinnedFreezeSha256='[a-f0-9]{64}'$",'',runner.read_text())
                    self.assertEqual(count,1);runner.write_text(text)
                self.rebind_ordinary_hashes(folder)
                if label=='root':
                    p=folder / 'root-pin-R5.json';pin=json.loads(p.read_text());pin['runtime_build_id']='0'*64;p.write_bytes(kit.encode(pin))
                result=subprocess.run([sys.executable,str(folder / 'verify_native_ui_kit.py')],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn(expected,result.stdout+result.stderr)
        self.check_verifier(True)

    def test_invalid_candidate_refused_before_native_output(self):
        info=candidate.verify(self.output)
        path=self.output / info['downloads']['dailySource']['filename']
        path.write_bytes(path.read_bytes()+b'tamper')
        with self.assertRaisesRegex(ValueError,'Archive SHA256/bytes differ'):
            self.build()
        self.assertFalse(self.kit.exists())

# Inherited packaging tests have their own setup assumptions; run only the kit cases.
for _name in list(vars(CandidatePackageTests)):
    if _name.startswith('test_'):
        setattr(NativeKitTests, _name, None)

if __name__ == '__main__': unittest.main()

#!/usr/bin/env python3
"""R4 preparation boundaries; no native execution or browser."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import shutil
import unittest

from build_stoikus_interface_kit import (
    ROOT, R3_KIT_SHA256, load_r3_templates, prepare_output, adapt_template, prepare,
)


class BrandingDistributionTests(unittest.TestCase):
    def test_sealed_r3_inventory_and_core_logic_preserved(self):
        templates = load_r3_templates(ROOT)
        self.assertEqual(len(templates), 9)
        raw = templates['NativeKit.Core.ps1']
        self.assertEqual(adapt_template('NativeKit.Core.ps1', raw, {}), raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '2dba568c184e31f1e28814c706d3e6a9459fe4e45524e33b52db14c0776ed542')

    def test_coherent_corrupt_historical_kit_is_rejected(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / 'downloads/jpw-alavancagem-atual/Kit_Windows_Stoikus_Interface.zip'
            target.parent.mkdir(parents=True)
            original = ROOT / target.relative_to(root)
            shutil.copyfile(original, target)
            target.write_bytes(target.read_bytes() + b'coherent metadata cannot approve new bytes')
            self.assertNotEqual(hashlib.sha256(target.read_bytes()).hexdigest(), R3_KIT_SHA256)
            with self.assertRaisesRegex(ValueError, 'R3'):
                load_r3_templates(root)

    def test_existing_output_is_preserved(self):
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / 'already-sealed'
            output.mkdir()
            sentinel = output / 'historical'; sentinel.write_bytes(b'keep')
            with self.assertRaises(FileExistsError):
                prepare_output(output)
            self.assertEqual(sentinel.read_bytes(), b'keep')

    def test_missing_daily_program_is_rejected_before_any_write(self):
        with TemporaryDirectory(prefix='jpw-r4-no-write-') as temporary:
            root = Path(temporary) / 'project'
            manifest = json.loads((ROOT / 'downloads/jpw-alavancagem-atual/manifest.json').read_text())
            for relative in manifest['sourceFiles'] + [
                'downloads/jpw-alavancagem-atual/Kit_Windows_Stoikus_Interface.zip',
                'downloads/jpw-alavancagem-atual/Previa_Stoikus_Interface_R4.html',
            ]:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, target)
            manifest['sourceFiles'].remove('mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5')
            (root / 'downloads/jpw-alavancagem-atual/manifest.json').write_text(json.dumps(manifest))
            before = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
            output = Path(temporary) / 'sealed'
            with self.assertRaisesRegex(ValueError, 'Programas de uso diario ou guia ausentes'):
                prepare(root, output, {})
            self.assertEqual({p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}, before)
            self.assertFalse(output.exists())

    def test_reference_adaptation_keeps_control_statements(self):
        raw = (b"if($identity.candidate_version -cne '1.22.2-interface'){throw 'R3'}\n"
               b"$path='root-pin-R3.json'; $zip='JPW_Stoikus_Uso_Fontes_v1.22.2_interface.zip'\n")
        adapted = adapt_template('Compile-Stoikus-UI.ps1', raw, {})
        self.assertEqual(adapted, raw.replace(b'1.22.2', b'1.22.3').replace(b'R3', b'R4'))
        self.assertIn(b"if($identity.candidate_version -cne", adapted)
        self.assertIn(b"{throw 'R4'}", adapted)


if __name__ == '__main__':
    unittest.main(verbosity=2)

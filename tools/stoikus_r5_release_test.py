#!/usr/bin/env python3
"""Independent R5 sealed release pins, inventory and adversarial controls."""
from pathlib import Path
import hashlib
import json
import shutil
from copy import deepcopy
import unittest

from build_leverage_package import ROOT, OUTPUT, PRODUCT, MANIFEST_PATH, build
from leverage_package_test import R5_MEMBERS, assert_release_inventory
from stoikus_daily_package_test import R5_DAILY_MEMBERS, check_archive
from stoikus_interface_package_test import InterfacePackageTests

ASSETS = {
    'nativeKit': ('Kit_Windows_Stoikus_Janelas_R5.zip', '5c32d1a5bf3ff2e2023c2c0e7b29c6425d1cc1bd5169f5fdf03f277d8fc9f8f4'),
    'nativePin': ('root-pin-R5.json', 'bb6ad986db99b3f9dca2437e83f9fd928f4df7830a9866da5d2b0b7bc731447a'),
    'preview': ('Previa_Stoikus_Janelas_R5.html', '90fd6a0d542ce9abb538d61f0b5b8e5470d364eae1dd47ceed4504f6b67cbfd7'),
}
SDK_SHA256 = '65ed7e2cb6f9fe680695ef67e47eb9aa873a66e2bfd214c1ebd71a41367fcf63'
DAILY_SHA256 = '0bc6c856410b576ebf0412aa341056e8e02463c8f848fe34d2bd4e983ae5f7a3'
BUILD_ID = 'c1298741ec9673c2644cfaad83e6444b06a4ae7e0a5ec78f85f2c65d2781ea31'
FINGERPRINT = '62c9bb7d36aed866983449c4327fb529b994464cb1422bf9516c639ea4fb94ac'


class R5ReleaseTests(InterfacePackageTests):
    version = '1.23.0'
    assets = ASSETS
    members = R5_MEMBERS
    daily_members = R5_DAILY_MEMBERS
    daily_sha256 = DAILY_SHA256
    build_id = BUILD_ID
    fingerprint = FINGERPRINT
    variant = ''

    def populate_sources(self):
        for name in self.members:
            target = self.root / PRODUCT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / PRODUCT / name, target)

    def test_exact_r5_sdk_and_daily_identity_without_suffix(self):
        result = build(self.root)
        self.assertEqual(result['downloads']['source']['sha256'], SDK_SHA256)
        self.assertEqual(result['downloads']['source']['bytes'], 803890)
        self.assertEqual(result['downloads']['dailySource']['bytes'], 469034)
        self.assertEqual(result['interfaceRelease']['archiveVariant'], '')
        self.assertEqual(len(self.members), 139)
        self.assertEqual(len(self.daily_members), 86)

    def test_empty_variant_does_not_bypass_build_or_daily_pins(self):
        # Guide corruption leaves the runtime fingerprint unchanged: the daily
        # digest must independently reject it, even with an empty archive suffix.
        self.test_source_identity_and_guide_corruption_rejected()

    def test_all_added_headers_and_sealed_readme_are_bound(self):
        for member in (
            'MQL5/Include/JPWealth/JPW_Stoikus_HUD.mqh',
            'MQL5/Include/JPWealth/JPW_Stoikus_Visual.mqh',
            'MQL5/Include/JPWealth/JPW_Stoikus_Window.mqh',
            'README.md',
        ):
            target = self.root / PRODUCT / member
            raw = target.read_bytes()
            target.write_bytes(raw + b'\nunauthorized change\n')
            self.rejected(deepcopy(self.manifest), member)
            target.write_bytes(raw)

    def test_cross_release_and_terminal_promotion_rejected(self):
        original = deepcopy(self.manifest)
        for key, value in (('revision', 'R4'), ('candidate', '1.22.3-interface')):
            changed = deepcopy(original)
            changed['interfaceRelease'][key] = value
            self.rejected(changed, 'cross release ' + key)
        changed = deepcopy(original)
        changed['validation']['terminal']['status'] = 'passed'
        self.rejected(changed, 'terminal promoted')


def candidate():
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text())
    assert manifest['version'] == '1.23.0'
    assert_release_inventory(manifest)
    assert manifest['runtimeBuildId'] == BUILD_ID
    assert manifest['mqlSourceFingerprint'] == FINGERPRINT
    assert manifest['interfaceRelease']['revision'] == 'R5'
    assert manifest['interfaceRelease']['candidate'] == '1.23.0-interface'
    assert manifest['interfaceRelease']['archiveVariant'] == ''
    assert manifest['interfaceRelease']['state'] == 'SOURCE_ONLY_NATIVE_PENDING'
    for key in ('nativeCompilation', 'nativeRuntime', 'humanAcceptance', 'windowsX64'):
        assert manifest['interfaceRelease'][key] == 'NOT_RUN'
    assert manifest['nativeArtifact'] is None
    assert not manifest['downloads']['compiled']['available']
    assert all(manifest['validation'][kind]['status'] == 'pending' for kind in ('compilation', 'terminal'))
    assert hashlib.sha256(check_archive(ROOT, manifest, 'source', R5_MEMBERS)).hexdigest() == SDK_SHA256
    assert hashlib.sha256(check_archive(ROOT, manifest, 'dailySource', R5_DAILY_MEMBERS)).hexdigest() == DAILY_SHA256
    for kind, (filename, digest) in ASSETS.items():
        record = manifest['interfaceRelease']['artifacts'][kind]
        raw = (ROOT / OUTPUT / filename).read_bytes()
        assert record == dict(available=True, path=OUTPUT + filename, filename=filename, sha256=digest, bytes=len(raw))
        assert hashlib.sha256(raw).hexdigest() == digest
    pin = json.loads((ROOT / OUTPUT / 'root-pin-R5.json').read_text())
    assert pin['source_zip_sha256'] == DAILY_SHA256
    assert pin['mql_source_fingerprint'] == FINGERPRINT
    assert pin['runtime_build_id'] == BUILD_ID
    assert pin['kit_package_sha256'] == ASSETS['nativeKit'][1]
    print('PASS R5 sealed SDK139/daily86; source-only, exact pins; native NOT_RUN')


def controls():
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(R5ReleaseTests))
    if not result.wasSuccessful():
        raise AssertionError('R5 release controls failed')


if __name__ == '__main__':
    controls()
    candidate()

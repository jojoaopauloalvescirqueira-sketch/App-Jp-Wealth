#!/usr/bin/env python3
"""Independent usage archive contract and adversarial builder controls.

The fixture is extracted from the immutable local 1.22.0 archive, verified
against its frozen digest before extraction, with the authorized usage and diagnostic additions.
No generated manifest defines the expected inventory.
"""
from io import BytesIO
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
import argparse
import hashlib
import json
import re
import stat
import zipfile

from build_leverage_package import build, MANIFEST_PATH, PRODUCT, VERSION_HEADER
from leverage_package_test import EXPECTED_MEMBERS, R5_WINDOW_HEADERS, R5_MEMBERS, assert_historical_archive, assert_historical_stoikus_archive, assert_historical_stoikus_1_22_1_archive

ROOT = Path(__file__).resolve().parents[1]
BASELINE_ARCHIVE = 'downloads/jpw-alavancagem-atual/JPW_Stoikus_Fontes_v1.22.0.zip'
GUIDE = 'STOIKUS_USO_DIARIO.md'
SCRIPT = 'MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5'
MONITOR_LOG = 'MQL5/Include/JPWealth/JPW_Stoikus_Monitor_Log.mqh'
DAILY_PROGRAMS = {
    'MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5',
    'MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5',
    'MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5',
    SCRIPT,
}
# Frozen, independently named dependencies. Removing a real include from the
# implementation cannot silently shrink the oracle, nor can an unrelated file
# replace one of these members merely by maintaining the count.
DAILY_INCLUDES = {
    *('MQL5/Include/JPWealth/JPW_Alavancagem_' + name + '.mqh' for name in (
        'Actions', 'Cockpit', 'Coordinator', 'Core', 'Diagnostics', 'Diagnostics_Core',
        'Genesis_Core', 'Genesis_Store', 'MDD', 'Observer_Presence', 'Panel', 'Positions',
        'Presentation', 'Profile', 'RaizN_Config', 'RaizN_Core', 'RaizN_Factor',
        'RaizN_Horizon', 'RaizN_Live', 'RaizN_Observer', 'RaizN_Store', 'Samples',
        'StopRisk_Core', 'StopRisk_Store', 'StopRisk_Terminal', 'Store_Result',
        'Terminal', 'Version')),
    *('MQL5/Include/JPWealth/JPW_NoCuda_' + name + '.mqh' for name in (
        'Core', 'Fibo_Controller', 'Fibo_Core', 'Fibo_Store', 'Fibo_Sync', 'Fibo_Terminal',
        'Fibo_UI', 'Projection', 'Projection_Core', 'Render', 'Store', 'Terminal', 'UI')),
    *('MQL5/Include/JPWealth/JPW_PersonalHistory_' + name + '.mqh' for name in (
        'Controller', 'Core', 'Export', 'Store', 'Terminal', 'UI')),
    *('MQL5/Include/JPWealth/JPW_SignalCopy_' + name + '.mqh' for name in (
        'Controller', 'Core', 'Terminal', 'Types', 'UI')),
    *('MQL5/Include/JPWealth/JPW_Stoikus_' + name + '.mqh' for name in (
        'Accountant_Runtime', 'Brand', 'Ledger_Bridge', 'Ledger_Core', 'Ledger_Preparation',
        'Ledger_Store', 'Ledger_Terminal', 'Monitor_Core', 'Monitor_Status', 'Monitor_UI',
        'Observer_Runtime', 'Risk_Core', 'Risk_Store', 'Risk_Terminal', 'UI')),
    'MQL5/Include/JPWealth/JPW_UI_Design.mqh',
    'MQL5/Include/JPWealth/JPW_UI_Focus.mqh',
}
DAILY_RESOURCES = {
    'MQL5/Images/JPWealth/JPW_Stoikus_Logo_' + theme + '_' + str(scale) + '.bmp'
    for theme in ('Light', 'Dark') for scale in (100, 125, 150, 200)
}
DAILY_MEMBERS = DAILY_PROGRAMS | DAILY_INCLUDES | DAILY_RESOURCES | {'LEIA_PRIMEIRO.md'}
assert len(DAILY_INCLUDES) == 69 and len(DAILY_MEMBERS) == 82
DAILY_1_22_1_MEMBERS = frozenset(DAILY_MEMBERS)
DAILY_INCLUDES.add(MONITOR_LOG)
DAILY_MEMBERS.add(MONITOR_LOG)
assert len(DAILY_INCLUDES) == 70 and len(DAILY_MEMBERS) == 83
SDK_MEMBERS = EXPECTED_MEMBERS | {SCRIPT, GUIDE}
assert len(SDK_MEMBERS) == 136
R5_DAILY_MEMBERS = DAILY_MEMBERS | R5_WINDOW_HEADERS
assert len(R5_DAILY_MEMBERS) == 86


def assert_historical_daily_archive(raw):
    """Frozen 1.22.1 daily package identity, before any extraction."""
    assert len(raw) == 441515
    assert hashlib.sha256(raw).hexdigest() == '2dd00aa8a4b4cb90f6b4eca36af4ef8d3e475ad5c856e163d9dc5c19fe6a99cf'
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist())) == 82
        assert set(archive.namelist()) == DAILY_1_22_1_MEMBERS
        assert not any(name.lower().endswith('.ex5') for name in archive.namelist())
        header = archive.read('MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh')
        assert b'#define JPW_PRODUCT_VERSION "1.22.1"' in header
        assert b'#define JPW_PRODUCT_MQL_VERSION "1.221"' in header
        assert b'#define JPW_CALCULATION_VERSION "1.9.0"' in header


def check_archive(root, manifest, kind, expected):
    entry = manifest['downloads'].get(kind)
    assert entry and entry['available'], f'{kind} is absent from the public download contract'
    raw = (root / entry['path']).read_bytes()
    assert entry['bytes'] == len(raw)
    assert entry['sha256'] == hashlib.sha256(raw).hexdigest()
    variant = manifest.get('interfaceRelease', {}).get('archiveVariant', '')
    suffix = '_' + variant if variant else ''
    assert entry['filename'] == f'JPW_Stoikus_{"Uso_Fontes" if kind == "dailySource" else "Fontes"}_v{manifest["version"]}{suffix}.zip'
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist())) == len(expected)
        assert set(archive.namelist()) == expected, f'{kind} differs from the frozen inventory'
        for name in expected:
            source = GUIDE if name == 'LEIA_PRIMEIRO.md' else name
            assert archive.read(name) == (root / PRODUCT / source).read_bytes(), name
        assert not any(n.endswith('.ex5') for n in archive.namelist())
        if kind == 'dailySource':
            assert {n for n in archive.namelist() if n.endswith('.mq5')} == DAILY_PROGRAMS
            assert not any(n.endswith(('_Tests.mq5', '_Lab.mq5')) for n in archive.namelist())
            # Needed risk libraries stay byte-identical and must remain read-only.
            for name in (expected - DAILY_RESOURCES - {"LEIA_PRIMEIRO.md"}):
                text = re.sub(r'/\*.*?\*/|//[^\n]*', '', archive.read(name).decode(), flags=re.S)
                assert not re.search(r'\b(OrderSend|OrderSendAsync)\s*\(', text), name
    return raw


def fixture(root):
    # The immutable ZIP is part of the checkout. A previous /tmp snapshot or
    # the current source tree cannot silently become the fixture baseline.
    raw = (ROOT / BASELINE_ARCHIVE).read_bytes()
    assert_historical_stoikus_archive(raw)  # Literal size/hash before extraction.
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text())
    manifest.pop('interfaceRelease', None)
    # This historical synthetic release has no installer; never inherit current-version metadata.
    manifest.get('downloads', {}).pop('installer', None)  # Original default-path controls remain independent.
    manifest['version'] = '1.22.3'
    manifest['coverage'] = manifest['coverage'].replace('1.22.0', '1.22.3')
    manifest['sourceFiles'] = sorted(PRODUCT + name for name in SDK_MEMBERS)
    manifest['nativeArtifact'] = None
    manifest['validation']['compilation'] = {'status': 'pending', 'detail': 'Synthetic fixtures; NOT_RUN'}
    product_root = root / PRODUCT
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        for info in archive.infolist():
            name = info.filename
            relative = PurePosixPath(name)
            assert not relative.is_absolute() and relative.as_posix() == name
            assert not any(part in ('.', '..') for part in relative.parts)
            assert not info.is_dir() and not stat.S_ISLNK(info.external_attr >> 16)
            target = product_root / name
            assert target.resolve() == product_root.resolve() / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(info))
    (root / PRODUCT / GUIDE).write_text('# Fixture usage guide\n')
    (root / PRODUCT / SCRIPT).write_text('#include <JPWealth/JPW_Alavancagem_Version.mqh>\nvoid OnStart() {}\n')
    (root / PRODUCT / MONITOR_LOG).write_text('// Synthetic diagnostic-only include fixture.\n')
    monitor = root / PRODUCT / 'MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5'
    monitor.write_bytes(monitor.read_bytes() + b'\n#include <JPWealth/JPW_Stoikus_Monitor_Log.mqh>\n')
    version = root / VERSION_HEADER
    version.write_text(version.read_text().replace('"1.22.0"', '"1.22.3"').replace('"1.220"', '"1.223"'))
    path = root / MANIFEST_PATH
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(manifest))


def assert_rejected(root, description):
    try:
        build(root)
    except (ValueError, FileNotFoundError):
        return
    raise AssertionError('accepted ' + description)


def controls():
    for name, check in (
        ('JPW_Stoikus_Fontes_v1.22.1.zip', assert_historical_stoikus_1_22_1_archive),
        ('JPW_Stoikus_Uso_Fontes_v1.22.1.zip', assert_historical_daily_archive),
    ):
        historical = (ROOT / 'downloads/jpw-alavancagem-atual' / name).read_bytes()
        check(historical)
        for changed in (historical[:-1], historical[:100] + bytes([historical[100] ^ 1]) + historical[101:]):
            try:
                check(changed)
            except AssertionError:
                pass
            else:
                raise AssertionError('immutable historical archive accepted altered bytes: ' + name)
    print('PASS immutable 1.22.1 SDK/daily archives and size/hash counterexamples')
    with TemporaryDirectory(prefix='jpw-stoikus-daily-') as directory:
        root = Path(directory)
        fixture(root)
        first = build(root)
        daily = check_archive(root, first, 'dailySource', DAILY_MEMBERS)
        sdk = check_archive(root, first, 'source', SDK_MEMBERS)
        assert not first['downloads']['compiled']['available']
        manifest_path = root / MANIFEST_PATH
        before = manifest_path.read_bytes()
        mtimes = {p: p.stat().st_mtime_ns for p in (manifest_path, root / first['downloads']['dailySource']['path'], root / first['downloads']['source']['path'])}
        assert build(root) == first
        assert {p: p.stat().st_mtime_ns for p in mtimes} == mtimes
        assert check_archive(root, first, 'dailySource', DAILY_MEMBERS) == daily
        assert check_archive(root, first, 'source', SDK_MEMBERS) == sdk
        print('PASS separate frozen inventories; bytes/hash; reproduction and idempotence')
        for member in (GUIDE, SCRIPT, MONITOR_LOG, 'MQL5/Include/JPWealth/JPW_Stoikus_Risk_Core.mqh', next(iter(DAILY_RESOURCES))):
            target = root / PRODUCT / member
            content = target.read_bytes()
            target.unlink()
            assert_rejected(root, 'missing usage dependency ' + member)
            target.write_bytes(content)
            manifest_path.write_bytes(before)
        script = root / PRODUCT / SCRIPT
        original = script.read_bytes()
        for line in (
            '#include "../../rogue.mqh"',
            '#include <JPWealth/undeclared.mqh>',
            '#include <JPWealth/../../rogue.mqh>',
            '#include <JPWealth/JPW_Alavancagem_Tests.mq5>',
            '#resource "\\Images\\JPWealth\\undeclared.bmp"',
            '#resource "\\Images\\..\\outside.bmp"',
        ):
            script.write_bytes(original + (line + '\n').encode())
            assert_rejected(root, 'unsafe or undeclared include/resource ' + line)
            script.write_bytes(original)
            manifest_path.write_bytes(before)
        dependency = root / PRODUCT / 'MQL5/Include/JPWealth/JPW_Stoikus_Risk_Core.mqh'
        saved = dependency.read_bytes()
        dependency.unlink()
        link_target = root / 'symlink-target.mqh'
        link_target.write_bytes(saved)
        dependency.symlink_to(link_target)
        assert_rejected(root, 'symlink dependency')
        dependency.unlink()
        dependency.write_bytes(saved)
        link_target.unlink()
        manifest_path.write_bytes(before)
        compiled = script.with_suffix('.ex5')
        compiled.write_bytes(b'not proved by native compiler' * 50)
        assert_rejected(root, 'EX5 without exact native evidence')
        compiled.unlink()
        assert build(root) == first
        print('PASS absent guide/script/dependencies, traversal, unsafe resources, symlink and unproved EX5 rejected')


def candidate():
    manifest = json.loads((ROOT / MANIFEST_PATH).read_text())
    assert manifest['version'] in ('1.22.3', '1.23.0')
    sdk = R5_MEMBERS if manifest['version'] == '1.23.0' else SDK_MEMBERS
    daily = R5_DAILY_MEMBERS if manifest['version'] == '1.23.0' else DAILY_MEMBERS
    assert set(manifest['sourceFiles']) == {PRODUCT + name for name in sdk}
    check_archive(ROOT, manifest, 'dailySource', daily)
    check_archive(ROOT, manifest, 'source', sdk)
    assert_historical_archive((ROOT / 'downloads/jpw-alavancagem-atual/JPW_Genetrix_Fontes_v1.21.2.zip').read_bytes())
    assert_historical_stoikus_archive((ROOT / 'downloads/jpw-alavancagem-atual/JPW_Stoikus_Fontes_v1.22.0.zip').read_bytes())
    assert_historical_stoikus_1_22_1_archive((ROOT / 'downloads/jpw-alavancagem-atual/JPW_Stoikus_Fontes_v1.22.1.zip').read_bytes())
    assert_historical_daily_archive((ROOT / 'downloads/jpw-alavancagem-atual/JPW_Stoikus_Uso_Fontes_v1.22.1.zip').read_bytes())
    if 'interfaceRelease' in manifest:
        from stoikus_interface_package_test import candidate as interface_candidate
        interface_candidate()
    print('PASS actual candidate inventories, bytes, source parity, immutable historical archives')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixtures-only', action='store_true')
    args = parser.parse_args()
    controls()
    if not args.fixtures_only:
        candidate()

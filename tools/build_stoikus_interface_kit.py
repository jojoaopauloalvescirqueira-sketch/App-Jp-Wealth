#!/usr/bin/env python3
"""Prepare the R4 source-only kit with official archive/identity helpers.

The external pin records exact bytes, never compilation or human acceptance.
Historical R3 inputs are read only. Final SDK/daily publication still uses
build_leverage_package.py after its independent sealed-input review.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path
import re
import zipfile

import build_leverage_package as package

ROOT = Path(__file__).resolve().parents[1]
R3_KIT_SHA256 = 'c584076a3b1450bb5c0e0a17aaefce903291737a2c245833860942d10286ef97'
KIT_NAME = 'Kit_Windows_Stoikus_Assinatura_R4.zip'
PIN_NAME = 'root-pin-R4.json'
PREVIEW_NAME = 'Previa_Stoikus_Interface_R4.html'
DAILY_NAME = 'JPW_Stoikus_Uso_Fontes_v1.22.3_interface.zip'
IDENTITY_NAME = 'stoikus-1.22.3-interface.identity.json'
FREEZE_NAME = 'source-freeze-R4.json'
BASE_COMMIT = '0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874'
R3_MEMBERS = frozenset({
    'Compile-Stoikus-UI.ps1', 'NativeKit.Core.ps1', 'Test-NativeUI-Kit.ps1',
    'identity.schema.json', 'source-freeze-R3.json',
    'stoikus-1.22.2-interface.identity.json', 'verify_native_ui_kit.py',
    'LEIA-PRIMEIRO.md', 'JPW_Stoikus_Uso_Fontes_v1.22.2_interface.zip',
})


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def load_r3_templates(root: Path) -> dict[str, bytes]:
    path = package.checked_file(root, package.OUTPUT + 'Kit_Windows_Stoikus_Interface.zip', package.OUTPUT)
    raw = path.read_bytes()
    if sha(raw) != R3_KIT_SHA256:
        raise ValueError('R3 kit bytes differ from the historically sealed input')
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        if len(archive.infolist()) != len(R3_MEMBERS) or set(archive.namelist()) != R3_MEMBERS:
            raise ValueError('R3 kit inventory differs')
        return {name: archive.read(name) for name in archive.namelist()}


def prepare_output(path: Path) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError('Existing evidence preserved; choose a fresh output directory')
    path.mkdir(parents=True)


def adapt_template(name: str, raw: bytes, bindings: dict[str, str]) -> bytes:
    if name == 'NativeKit.Core.ps1':
        return raw  # All validators, extraction and compilation-log logic stay exact.
    text = raw.decode('utf-8')
    for old, new in bindings.items():
        text = text.replace(old, new)
    text = text.replace('Kit_Windows_Stoikus_Interface.zip', KIT_NAME)
    text = text.replace('1.22.2', '1.22.3').replace('R3', 'R4')
    if name == 'LEIA-PRIMEIRO.md':
        text = text.replace('O gate host do freeze R4 passou 48/48;',
                            'O gate host desta revisão exige seu próprio recibo;')
        text = text.replace('O antigo pacote 1.22.3 não identifica esta interface.',
                            'O pacote histórico 1.22.2/R3 não identifica esta assinatura R4.')
    return text.encode('utf-8')


def verify_history(root: Path, expected: dict[str, str]) -> None:
    for relative, digest in expected.items():
        raw = package.checked_file(root, relative, package.OUTPUT).read_bytes()
        if sha(raw) != digest:
            raise ValueError('Historical download changed: ' + relative)


def prepare(root: Path, output: Path, history: dict[str, str]) -> dict:
    templates = load_r3_templates(root)
    verify_history(root, history)
    manifest = json.loads(package.checked_file(root, package.MANIFEST_PATH, package.OUTPUT).read_text())
    if manifest['version'] != '1.22.3' or manifest.get('nativeArtifact') is not None:
        raise ValueError('R4 requires version 1.22.3 and no native artifact')
    if any(manifest['validation'][kind]['status'] != 'pending' for kind in ('compilation', 'terminal')):
        raise ValueError('Native state must remain pending/NOT_RUN')
    sources = manifest['sourceFiles']
    if len(sources) != len(set(sources)):
        raise ValueError('Duplicate source inventory')
    dependencies = {}
    for relative in sources:
        path = package.checked_file(root, relative, package.PRODUCT)
        if path.suffix == '.mq5' and path.with_suffix('.ex5').exists():
            raise ValueError('Unproved EX5 present; source-only kit refused')
        dependencies[relative] = package.local_dependencies(relative, path.read_text()) if path.suffix in ('.mq5', '.mqh') else set()
        if not dependencies[relative].issubset(sources):
            raise ValueError('Local dependency missing from SDK inventory')
    daily = package.daily_inventory(sources, dependencies)
    preview = package.checked_file(root, package.OUTPUT + PREVIEW_NAME, package.OUTPUT).read_bytes()
    version = package.checked_file(root, package.VERSION_HEADER, package.PRODUCT).read_text()
    if ('#define JPW_CALCULATION_VERSION "1.9.0"' not in version
            or '#define JPW_PRODUCT_MQL_VERSION "1.223"' not in version):
        raise ValueError('Calculation/MQL version mismatch')
    if output.exists() or output.is_symlink():
        raise FileExistsError('Existing evidence preserved; choose a fresh output directory')
    build_id = package.stamp_source_build(root, sources, manifest['version'])
    if build_id == '1bc02d97bdf034e824df726debb7087193a9fbb7cc1ebbad3c15dc7e83894100':
        raise ValueError('Historical R3 build reused')
    members = [('LEIA_PRIMEIRO.md' if rel == package.DAILY_GUIDE else rel.removeprefix(package.PRODUCT),
                package.checked_file(root, rel, package.PRODUCT).read_bytes()) for rel in daily]
    daily_zip = package.make_archive(members)
    source_hashes = {rel: sha(package.checked_file(root, rel, package.PRODUCT).read_bytes()) for rel in sorted(sources)}
    mql_hashes = {rel.removeprefix(package.PRODUCT): digest for rel, digest in source_hashes.items() if package.runtime_source(rel)}
    source_hashes[package.OUTPUT + PREVIEW_NAME] = sha(preview)
    fingerprint = sha(canonical(mql_hashes))
    interface_fingerprint = sha(canonical(source_hashes))
    freeze = dict(schema='JPW_STOIKUS_INTERFACE_FREEZE_V1', candidate='1.22.3-interface',
                  product_version='1.22.3', calculation_version='1.9.0', baseline_commit=BASE_COMMIT,
                  runtime_build_id=build_id, mql_source_fingerprint=fingerprint,
                  interface_fingerprint=interface_fingerprint, source_hashes=source_hashes,
                  scope='DECLARED_SDK_SOURCES_AND_PREVIEW_BEFORE_DISTRIBUTION_SEAL',
                  daily_entries=len(members), native_compilation='NOT_RUN', native_execution='NOT_RUN',
                  human_acceptance='NOT_RUN', windows_x64='NOT_RUN')
    freeze_raw = json_bytes(freeze)
    old_identity = json.loads(templates['stoikus-1.22.2-interface.identity.json'])
    old = old_identity['origin']
    bindings = {old['root_freeze_sha256']: sha(freeze_raw), old['mql_source_fingerprint']: fingerprint,
                old['interface_fingerprint']: interface_fingerprint, old['runtime_build_id']: build_id,
                old_identity['zip']['sha256']: sha(daily_zip)}
    kit = {name: adapt_template(name, templates[name], bindings) for name in (
        'Compile-Stoikus-UI.ps1', 'NativeKit.Core.ps1', 'Test-NativeUI-Kit.ps1',
        'identity.schema.json', 'verify_native_ui_kit.py', 'LEIA-PRIMEIRO.md')}
    identity = dict(schema_version=1, kind='JPW_STOIKUS_UI_NATIVE_COMPILE_IDENTITY',
                    candidate_version='1.22.3-interface', frozen=True,
                    origin=dict(generated_by='root', freeze_id='stoikus-interface-R4',
                                root_freeze_sha256=sha(freeze_raw), mql_source_fingerprint=fingerprint,
                                interface_fingerprint=interface_fingerprint, runtime_build_id=build_id,
                                calculation_version='1.9.0', baseline_commit=BASE_COMMIT),
                    kit_files=[dict(name=name, sha256=sha(kit[name])) for name in ('Compile-Stoikus-UI.ps1', 'NativeKit.Core.ps1')],
                    zip=dict(filename=DAILY_NAME, sha256=sha(daily_zip), bytes=len(daily_zip)),
                    programs=[dict(path=rel.removeprefix(package.PRODUCT), sha256=source_hashes[rel]) for rel in sorted(package.DAILY_PROGRAMS)],
                    entries=[dict(path=name, bytes=len(raw), sha256=sha(raw)) for name, raw in sorted(members)])
    kit.update({IDENTITY_NAME: json_bytes(identity), FREEZE_NAME: freeze_raw, DAILY_NAME: daily_zip})
    kit_zip = package.make_archive(list(kit.items()))
    pin = dict(kind='JPW_STOIKUS_UI_NATIVE_KIT_ROOT_PIN', candidate='1.22.3-interface',
               status='SEALED_SOURCE_ONLY', freeze_id='stoikus-interface-R4',
               root_freeze_sha256=sha(freeze_raw), mql_source_fingerprint=fingerprint,
               interface_fingerprint=interface_fingerprint, runtime_build_id=build_id,
               calculation_version='1.9.0', source_zip_sha256=sha(daily_zip),
               kit_package_filename=KIT_NAME, kit_package_sha256=sha(kit_zip),
               files_sha256={name: sha(raw) for name, raw in sorted(kit.items())},
               reviews={key: 'NOT_RUN_AT_SEAL' for key in ('source_and_manifest', 'host_full', 'python_independent_byte_check',
                        'negative_tamper_fixtures', 'powershell_static_review', 'windows_power_shell_fixtures',
                        'mt5_compilation', 'mt5_demo_runtime', 'independent_windows_x64', 'owner_acceptance')})
    prepare_output(output)
    sealed = output / 'sealed-R4'; sealed.mkdir()
    for name, raw in kit.items():
        (sealed / name).write_bytes(raw)
    (output / KIT_NAME).write_bytes(kit_zip)
    (output / PIN_NAME).write_bytes(json_bytes(pin))
    (sealed / PIN_NAME).write_bytes(json_bytes(pin))
    verify_history(root, history)
    result = dict(kit=package.download_record(package.OUTPUT + KIT_NAME, kit_zip),
                  pin=package.download_record(package.OUTPUT + PIN_NAME, json_bytes(pin)),
                  preview=package.download_record(package.OUTPUT + PREVIEW_NAME, preview),
                  daily_sha256=sha(daily_zip), runtime_build_id=build_id,
                  mql_fingerprint=fingerprint, interface_fingerprint=interface_fingerprint,
                  native_state='NOT_RUN', output=str(output))
    (output / 'seal.json').write_bytes(json_bytes(result))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--history-inventory', type=Path, required=True)
    args = parser.parse_args()
    history = json.loads(args.history_inventory.read_text())
    print(json.dumps(prepare(args.root.resolve(), args.output, history), ensure_ascii=False))


if __name__ == '__main__':
    main()

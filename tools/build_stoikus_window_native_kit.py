"""Seal a private 1.23.0 compile-only kit from the approved historical R4 safety core.

No Windows execution, installation, terminal launch, or native approval occurs here.
"""
import argparse
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

import build_leverage_package as official
import build_stoikus_window_candidate as candidate

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = 'stoikus-1.23.0-interface.identity.json'
FREEZE = 'source-freeze-R5.json'
PAYLOAD = 'JPW_Stoikus_Uso_Fontes_v1.23.0_interface.zip'
OUTER = 'Kit_Windows_Stoikus_Janelas_R5.zip'
BASELINE = '0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874'
sha, encode = candidate.sha, candidate.encode


def historical_templates(path=None):
    name, approved = official.INTERFACE_ARTIFACTS['nativeKit']
    path = Path(path) if path else ROOT / official.OUTPUT / name
    raw = path.read_bytes()
    if sha(raw) != approved:
        raise ValueError('Approved historical nativeKit SHA256 differs')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def adapt(raw):
    return raw.decode('utf-8').replace('1.22.3', '1.23.0').replace('R4', 'R5').encode('utf-8')


def prepare(source, preview, output):
    source, preview, output = Path(source), Path(preview), Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError('Existing output preserved; choose a fresh directory')
    if not output.parent.is_dir():
        raise FileNotFoundError('Output parent must already exist')
    original = {p.name: sha(p.read_bytes()) for p in source.iterdir() if p.is_file()}
    info = candidate.verify(source)
    preview_raw = preview.read_bytes()
    old = historical_templates()
    old_identity = json.loads(old['stoikus-1.22.3-interface.identity.json'])
    preview_name = 'docs/preview/stoikus-window-controls/index.html'
    source_hashes = {official.PRODUCT + name: value for name, value in info['sourceHashes'].items()}
    source_hashes[preview_name] = sha(preview_raw)
    interface_fingerprint = sha(json.dumps(source_hashes, sort_keys=True, separators=(',', ':')).encode())
    payload = (source / info['downloads']['dailySource']['filename']).read_bytes()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        daily_entries = len(archive.infolist())
    freeze = {
        'schema': 'JPW_STOIKUS_INTERFACE_FREEZE_V1', 'candidate': '1.23.0-interface',
        'product_version': '1.23.0', 'calculation_version': '1.9.0', 'baseline_commit': BASELINE,
        'runtime_build_id': info['runtimeBuildId'], 'mql_source_fingerprint': info['mqlSourceFingerprint'],
        'interface_fingerprint': interface_fingerprint,
        'source_hashes': source_hashes,
        'scope': 'DECLARED_SDK_SOURCES_AND_PREVIEW_BEFORE_DISTRIBUTION_SEAL',
        'daily_entries': daily_entries, 'native_compilation': 'NOT_RUN',
        'native_execution': 'NOT_RUN', 'human_acceptance': 'NOT_RUN', 'windows_x64': 'NOT_RUN',
    }
    freeze_raw = encode(freeze)
    origin = {
        'generated_by': 'root', 'freeze_id': 'stoikus-interface-R5',
        'root_freeze_sha256': sha(freeze_raw),
        **{key: freeze[key] for key in ('mql_source_fingerprint', 'interface_fingerprint', 'runtime_build_id', 'calculation_version', 'baseline_commit')},
    }
    runner = adapt(old['Compile-Stoikus-UI.ps1']).decode()
    bindings = {
        'PinnedZipSha256': sha(payload), 'PinnedCoreSha256': sha(old['NativeKit.Core.ps1']),
        'PinnedFreezeSha256': sha(freeze_raw), 'PinnedMqlFingerprint': info['mqlSourceFingerprint'],
        'PinnedInterfaceFingerprint': freeze['interface_fingerprint'], 'PinnedRuntimeBuildId': info['runtimeBuildId'],
    }
    for key, value in bindings.items():
        runner, count = re.subn(r"(?m)^\$" + key + r"='[a-f0-9]{64}'$", '$' + key + "='" + value + "'", runner)
        if count != 1: raise ValueError('Historical runner pin guard missing: ' + key)
    entries = []
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for member in archive.infolist():
            raw = archive.read(member)
            entries.append({'path': member.filename, 'bytes': len(raw), 'sha256': sha(raw)})
    by_name = {entry['path']: entry for entry in entries}
    identity = {
        **{key: old_identity[key] for key in ('schema_version', 'kind', 'frozen')},
        'candidate_version': '1.23.0-interface', 'origin': origin,
        'kit_files': [{'name': 'Compile-Stoikus-UI.ps1', 'sha256': sha(runner.encode())},
                      {'name': 'NativeKit.Core.ps1', 'sha256': sha(old['NativeKit.Core.ps1'])}],
        'zip': {'filename': PAYLOAD, 'sha256': sha(payload), 'bytes': len(payload)},
        'programs': [{'path': row['path'], 'sha256': by_name[row['path']]['sha256']} for row in old_identity['programs']],
        'entries': entries,
    }
    files = {name: adapt(old[name]) for name in ('LEIA-PRIMEIRO.md', 'Test-NativeUI-Kit.ps1', 'identity.schema.json', 'verify_native_ui_kit.py')}
    guide = files['LEIA-PRIMEIRO.md'].decode('utf-8')
    for before, after in ((old_identity['origin']['runtime_build_id'], info['runtimeBuildId']),
                          (old_identity['origin']['interface_fingerprint'], freeze['interface_fingerprint']),
                          (old_identity['zip']['sha256'], sha(payload))):
        if guide.count(before) != 1:
            raise ValueError('Historical guide exact identity reference missing')
        guide = guide.replace(before, after)
    if guide.count('Kit_Windows_Stoikus_Assinatura_R5.zip') != 1:
        raise ValueError('Historical guide outer package reference missing')
    guide = guide.replace('Kit_Windows_Stoikus_Assinatura_R5.zip', OUTER)
    files['LEIA-PRIMEIRO.md'] = guide.encode('utf-8')
    files.update({'NativeKit.Core.ps1': old['NativeKit.Core.ps1'], 'Compile-Stoikus-UI.ps1': runner.encode(),
                  FREEZE: freeze_raw, IDENTITY: encode(identity), PAYLOAD: payload})
    pin = {
        'kind': 'JPW_STOIKUS_UI_NATIVE_KIT_ROOT_PIN', 'status': 'SEALED_SOURCE_ONLY',
        'candidate': '1.23.0-interface', 'freeze_id': origin['freeze_id'],
        **{key: origin[key] for key in ('interface_fingerprint', 'runtime_build_id', 'calculation_version')},
        'root_freeze_sha256': origin['root_freeze_sha256'],
        'mql_source_fingerprint': origin['mql_source_fingerprint'],
        'source_zip_sha256': sha(payload),
        'files_sha256': {name: sha(raw) for name, raw in sorted(files.items())},
        'reviews': {key: 'NOT_RUN_AT_SEAL' for key in (
            'source_and_manifest', 'host_full', 'python_independent_byte_check',
            'negative_tamper_fixtures', 'powershell_static_review', 'windows_power_shell_fixtures',
            'mt5_compilation', 'mt5_demo_runtime', 'independent_windows_x64', 'owner_acceptance')},
        'compilation_status': 'NOT_RUN', 'runtime_status': 'NOT_RUN',
        'independent_windows_x64': 'NOT_RUN', 'human_acceptance': 'NOT_RUN',
    }
    # Seal only the nine kit files. The external pin binds the resulting archive;
    # excluding the pin avoids a circular archive/pin digest.
    outer_raw = official.make_archive(sorted(files.items()))
    pin.update(kit_package_filename=OUTER, kit_package_sha256=sha(outer_raw), kit_package_bytes=len(outer_raw))
    with tempfile.TemporaryDirectory(prefix='stoikus-native-kit-', dir=output.parent) as temporary:
        stage = Path(temporary) / 'kit'
        stage.mkdir()
        for name, raw in files.items(): (stage / name).write_bytes(raw)
        (stage / 'root-pin-R5.json').write_bytes(encode(pin))
        result = subprocess.run([sys.executable, str(stage / 'verify_native_ui_kit.py')], capture_output=True, text=True)
        if result.returncode:
            raise ValueError('Historical kit verifier rejected candidate: ' + result.stdout + result.stderr)
        (stage / OUTER).write_bytes(outer_raw)
        if candidate.verify(source) != info or original != {p.name: sha(p.read_bytes()) for p in source.iterdir() if p.is_file()} or preview.read_bytes() != preview_raw:
            raise ValueError('Candidate/preview inputs changed during sealing')
        stage.rename(output)
    return pin


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--preview', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.candidate, args.preview, args.output), indent=2))

if __name__ == '__main__': main()

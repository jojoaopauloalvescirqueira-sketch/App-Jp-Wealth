"""Prepare a local 1.23.0 source candidate using unchanged official archive helpers.

The published R4 manifest/site and all historical archives remain untouched.
This seals source bytes only; it does not certify compilation or native use.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import tempfile
import zipfile

import build_leverage_package as official

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.23.0'
MQL_VERSION = '1.230'
CALCULATION = '1.9.0'



def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def zip_history(root):
    directory = root / official.OUTPUT
    return {p.name: sha(p.read_bytes()) for p in sorted(directory.glob('*.zip')) if p.is_file()}


def prepare(root, output):
    root, output = Path(root).resolve(), Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError('Existing candidate/evidence preserved; choose a fresh output directory')
    if not output.parent.is_dir():
        raise FileNotFoundError('Create the output parent directory first')
    historical = zip_history(root)
    original = json.loads(official.checked_file(root, official.MANIFEST_PATH, official.OUTPUT).read_text())
    sources = set(original['sourceFiles'])
    mql = root / official.PRODUCT / 'MQL5'
    for path in mql.rglob('*'):
        if path.suffix.lower() == '.ex5':
            raise ValueError('Unproved EX5 in sources; source-only candidate refused')
        if path.is_file() and path.suffix in ('.mqh', '.mq5'):
            sources.add(path.relative_to(root).as_posix())
    sources = sorted(sources)
    version = official.checked_file(root, official.VERSION_HEADER, official.PRODUCT).read_text()
    for macro, expected in [('JPW_PRODUCT_VERSION', VERSION), ('JPW_PRODUCT_MQL_VERSION', MQL_VERSION),
                            ('JPW_CALCULATION_VERSION', CALCULATION)]:
        found = re.findall(r'(?m)^[ \t]*#define[ \t]+' + re.escape(macro) + r'[ \t]+"([^"\r\n]+)"[ \t]*$', version)
        if found != [expected]:
            raise ValueError('Cabecalho de versao/calculo diverge do candidato autorizado: ' + macro)
    raw_sources = {rel: official.checked_file(root, rel, official.PRODUCT).read_bytes() for rel in sources}
    with tempfile.TemporaryDirectory(prefix='stoikus-candidate-stage-', dir=output.parent) as temporary:
        work = Path(temporary)
        staged = work / 'project'
        for rel, raw in raw_sources.items():
            target = staged / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        manifest = dict(original)
        manifest.pop('interfaceRelease', None)
        manifest['version'] = VERSION
        manifest['sourceFiles'] = sources
        manifest['nativeArtifact'] = None
        manifest['validation'] = {
            'mathematics': {'status': 'pending', 'detail': 'Calculo1.9.0 preservado; recibos host deste candidato separados.'},
            'compilation': {'status': 'pending', 'detail': 'NOT_RUN: nenhum EX5 deste candidato comprovado.'},
            'terminal': {'status': 'pending', 'detail': 'NOT_RUN: interacao nativa e aceite humano pendentes.'},
        }
        target = staged / official.MANIFEST_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encode(manifest))
        generated = official.build(staged)
        bundle = work / 'bundle'
        bundle.mkdir()
        for kind in ('source', 'dailySource'):
            record = generated['downloads'][kind]
            shutil.copyfile(staged / record['path'], bundle / record['filename'])
        (bundle / 'candidate-manifest.json').write_bytes(encode(generated))
        identity = {
            'schema': 'JPW_STOIKUS_WINDOW_CANDIDATE_V1',
            'productVersion': VERSION, 'mqlVersion': MQL_VERSION, 'calculationVersion': CALCULATION,
            'runtimeBuildId': generated['runtimeBuildId'],
            'mqlSourceFingerprint': generated['mqlSourceFingerprint'],
            'sourceHashes': generated['sourceHashes'],
            'dailyPrograms': sorted(p.removeprefix(official.PRODUCT) for p in official.DAILY_PROGRAMS),
            'downloads': {k: generated['downloads'][k] for k in ('source', 'dailySource')},
            'nativeCompilation': 'NOT_RUN', 'nativeRuntime': 'NOT_RUN',
            'humanAcceptance': 'NOT_RUN', 'independentWindowsX64': 'NOT_RUN',
            'historicalArchives': historical,
        }
        (bundle / 'identity.json').write_bytes(encode(identity))
        (bundle / 'root-pin.json').write_bytes(encode({
            'schema': 'JPW_STOIKUS_WINDOW_LOCAL_ROOT_PIN_V1',
            'meaning': 'Local consistency pin; not a digital signature or native approval.',
            'identitySha256': sha((bundle / 'identity.json').read_bytes()),
            'manifestSha256': sha((bundle / 'candidate-manifest.json').read_bytes()),
        }))
        verify(bundle)
        if zip_history(root) != historical or any((root / rel).read_bytes() != raw for rel, raw in raw_sources.items()):
            raise ValueError('Source/history changed during build; candidate not sealed')
        bundle.rename(output)
    return identity


def verify(output):
    output = Path(output)
    pin = json.loads((output / 'root-pin.json').read_text())
    if (sha((output / 'identity.json').read_bytes()) != pin['identitySha256'] or
            sha((output / 'candidate-manifest.json').read_bytes()) != pin['manifestSha256']):
        raise ValueError('Identity/manifest SHA256 differs from local pin')
    identity = json.loads((output / 'identity.json').read_text())
    if (identity.get('schema') != 'JPW_STOIKUS_WINDOW_CANDIDATE_V1' or
            identity.get('productVersion') != VERSION or identity.get('mqlVersion') != MQL_VERSION or
            identity.get('calculationVersion') != CALCULATION or
            any(identity.get(key) != 'NOT_RUN' for key in ('nativeCompilation', 'nativeRuntime',
                                                          'humanAcceptance', 'independentWindowsX64'))):
        raise ValueError('Candidate identity/version/native state is invalid')
    manifest = json.loads((output / 'candidate-manifest.json').read_text())
    if (manifest['sourceHashes'] != identity['sourceHashes'] or
            manifest['runtimeBuildId'] != identity['runtimeBuildId'] or
            manifest['mqlSourceFingerprint'] != identity['mqlSourceFingerprint']):
        raise ValueError('Source identity differs from manifest')
    expected_programs = set(p.removeprefix(official.PRODUCT) for p in official.DAILY_PROGRAMS)
    if set(identity['dailyPrograms']) != expected_programs:
        raise ValueError('Four daily entrypoints differ')
    if set(identity.get('downloads', {})) != {'source', 'dailySource'}:
        raise ValueError('Required archive download records missing or unexpected')
    if any(manifest.get('downloads', {}).get(kind) != record
           for kind, record in identity['downloads'].items()):
        raise ValueError('Archive download metadata differs from manifest')
    if (manifest.get('version') != VERSION or manifest.get('nativeArtifact') is not None or
            any(manifest.get('validation', {}).get(kind, {}).get('status') != 'pending'
                for kind in ('compilation', 'terminal'))):
        raise ValueError('Manifest version/native state is invalid')
    sources = {official.PRODUCT + name for name in identity['sourceHashes']}
    if set(manifest['sourceFiles']) != sources:
        raise ValueError('Manifest source inventory differs')
    sdk_record = identity['downloads']['source']
    sdk_raw = (output / sdk_record['filename']).read_bytes()
    if sha(sdk_raw) != sdk_record['sha256'] or len(sdk_raw) != sdk_record['bytes']:
        raise ValueError('SDK archive SHA256/bytes differ')
    dependencies = {}
    with zipfile.ZipFile(output / sdk_record['filename']) as sdk:
        for name in sdk.namelist():
            if name.endswith(('.mq5', '.mqh')):
                relative = official.PRODUCT + name
                dependencies[relative] = official.local_dependencies(relative, sdk.read(name).decode('utf-8'))
                if not dependencies[relative].issubset(sources):
                    raise ValueError('SDK dependency missing from inventory')
    daily_expected = {'LEIA_PRIMEIRO.md' if rel == official.DAILY_GUIDE else rel.removeprefix(official.PRODUCT)
                      for rel in official.daily_inventory(sorted(sources), dependencies)}
    for kind, record in identity['downloads'].items():
        path = output / record['filename']
        raw = path.read_bytes()
        if sha(raw) != record['sha256'] or len(raw) != record['bytes']:
            raise ValueError('Archive SHA256/bytes differ: ' + record['filename'])
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or any(name.endswith('.ex5') for name in names):
                raise ValueError('Duplicate entry or unproved EX5')
            if kind == 'source' and set(names) != set(identity['sourceHashes']):
                raise ValueError('SDK inventory differs from declared source hashes')
            if kind == 'dailySource' and set(names) != daily_expected:
                raise ValueError('Daily dependency inventory is incomplete or unexpected')
            if kind == 'dailySource' and {name for name in names if name.endswith('.mq5')} != expected_programs:
                raise ValueError('Daily package does not contain exactly four programs')
            for name in names:
                original = 'STOIKUS_USO_DIARIO.md' if name == 'LEIA_PRIMEIRO.md' else name
                if original not in identity['sourceHashes'] or sha(archive.read(name)) != identity['sourceHashes'][original]:
                    raise ValueError('Entry hash differs: ' + name)
    return identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    result = verify(args.output) if args.verify else prepare(args.root, args.output)
    print(json.dumps({key: result[key] for key in ('productVersion', 'runtimeBuildId',
                                                   'mqlSourceFingerprint', 'nativeCompilation')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

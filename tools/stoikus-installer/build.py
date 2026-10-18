#!/usr/bin/env python3
"""Build a LOCAL unsigned Windows x64 candidate; never enable/publicize downloads."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import shutil
import tempfile
from prepare_payload import (ROOT, GENERATED, INSTALLER_VERSION, PRODUCT_VERSION,
    FILENAME, prepare, digest, write_changed)

SDK_VERSION = '10.0.402'
PROJECT = 'tools/stoikus-installer/src/Stoikus.Installer.App/Stoikus.Installer.App.csproj'
OUTPUT = 'tools/stoikus-installer/artifacts/'

def build_environment(environ=None):
    env = dict(os.environ if environ is None else environ)
    env.setdefault('DOTNET_CLI_HOME', str(Path(tempfile.gettempdir()) / 'jpw-dotnet-home'))
    env.setdefault('NUGET_PACKAGES', str(Path(tempfile.gettempdir()) / 'jpw-nuget'))
    env.update(DOTNET_NOLOGO='1', DOTNET_CLI_TELEMETRY_OPTOUT='1')
    return env


def publish(root=ROOT, dotnet=None):
    root = Path(root)
    selected_dotnet = dotnet or os.environ.get('JPW_DOTNET') or shutil.which('dotnet')
    if not selected_dotnet or not Path(selected_dotnet).is_file():
        raise ValueError('Official .NET SDK not found; provide --dotnet, JPW_DOTNET, or dotnet on PATH')
    dotnet = Path(selected_dotnet).resolve()
    env = build_environment()
    version = subprocess.check_output([str(dotnet), '--version'], cwd=root / 'tools/stoikus-installer', env=env, text=True).strip()
    if version != SDK_VERSION:
        raise ValueError(f'Expected official SDK {SDK_VERSION}; observed {version}')
    payload = prepare(root)['manifest']
    project = root / PROJECT
    if not project.is_file():
        raise ValueError('App project is not yet available')
    output = root / OUTPUT
    output.mkdir(parents=True, exist_ok=True)
    # A fresh directory prevents stale executables entering a new candidate.
    with tempfile.TemporaryDirectory(prefix='publish-', dir=output) as temporary:
        restore = [str(dotnet), 'restore', str(project), '-r', 'win-x64', '-p:EnableWindowsTargeting=true']
        command = [str(dotnet), 'publish', str(project), '-c', 'Release', '-r', 'win-x64', '--self-contained', 'true',
            '--no-restore', '-p:EnableWindowsTargeting=true', '-p:PublishSingleFile=true',
            '-p:IncludeNativeLibrariesForSelfExtract=true', '-p:PublishTrimmed=false', '-p:PublishAot=false',
            '-o', temporary]
        subprocess.run(restore, cwd=root / 'tools/stoikus-installer', env=env, check=True)
        subprocess.run(command, cwd=root / 'tools/stoikus-installer', env=env, check=True)
        executable = Path(temporary) / 'JPWealth.Stoikus.Installer.exe'
        if not executable.is_file() or executable.stat().st_size < 1024:
            raise ValueError('Publish did not produce the expected Windows executable')
        raw = executable.read_bytes()
        if raw[:2] != b'MZ':
            raise ValueError('Candidate is not a PE executable')
        candidate = output / FILENAME
        write_changed(candidate, raw)
    record = {'schemaVersion': 1, 'candidateRevision': 'R4', 'installerVersion': INSTALLER_VERSION, 'productVersion': PRODUCT_VERSION,
        'platform': 'win-x64', 'filename': FILENAME, 'sha256': digest(raw), 'bytes': len(raw),
        'unsigned': True, 'scope': 'LOCAL_CANDIDATE_ONLY', 'sdkVersion': version,
        'payloadSha256': payload['archiveSha256'], 'payloadManifestSha256': digest((root / GENERATED / 'payload.json').read_bytes()),
        'nativeTests': {'windowsX64': 'NOT_RUN', 'parallelsArm': 'NOT_RUN', 'browser': 'NOT_RUN'},
        'publicDownloadAvailable': False}
    write_changed(output / 'installer-candidate.json', (json.dumps(record, indent=2) + '\n').encode())
    return candidate, record

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--dotnet', type=Path, help='Official SDK executable; defaults to JPW_DOTNET or dotnet on PATH')
    args = parser.parse_args()
    candidate, record = publish(args.root, args.dotnet)
    print(f"LOCAL_CANDIDATE_ONLY: {candidate}\nSHA-256: {record['sha256']}\n{record['bytes']} bytes; unsigned; native tests NOT_RUN; public download disabled")

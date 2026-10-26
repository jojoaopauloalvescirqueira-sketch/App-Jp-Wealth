#!/usr/bin/env python3
"""Stoikus native cycle: compile and run the MQL5 test scripts in the isolated MT5 lab.

The Mac freezes the MQL5 tree into a deterministic payload, sends it over SSH
to the Windows agent (C:\\MT5Lab\\bin), fetches the agent's results and writes
a MT5_NATIVE receipt. Compilation and test scripts are separate native gates;
Tester, terminal interaction, alerts and installation stay NOT_RUN. The lab
holds only a demo-or-offline portable terminal; nothing here sends orders.

Contract: docs/architecture/STOIKUS-NATIVE-CYCLE.md and
docs/work/CHG-STOIKUS-NATIVE-CYCLE-20261026.md.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tempfile
import time
import zipfile

from leverage_suite import RESULTS, aggregate_result, fingerprint
from stoikus_native_parsers import classify_excerpt

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = 'mt5/jpw-alavancagem-atual'
AGENT_DIR = ROOT / 'tools/stoikus_native/windows'
AGENT_FILES = ('Invoke-StoikusNativeRun.ps1', 'Test-StoikusNativeAgent.ps1', 'NativeKit.Core.ps1')
# NativeKit.Core.ps1 is reused byte for byte from Kit_Windows_Stoikus_Painel_C5_D1.zip.
CORE_SHA256 = '2dba568c184e31f1e28814c706d3e6a9459fe4e45524e33b52db14c0776ed542'
LAB_ROOT = 'C:/MT5Lab'
AGENT_SCRIPT = 'C:\\MT5Lab\\bin\\Invoke-StoikusNativeRun.ps1'
SELF_TEST_SCRIPT = 'C:\\MT5Lab\\bin\\Test-StoikusNativeAgent.ps1'
IDENTITY_KIND = 'JPW_STOIKUS_NATIVE_CYCLE_IDENTITY'
AGENT_RECEIPT_SCHEMA = 'JPW_STOIKUS_NATIVE_AGENT_RECEIPT_V1'
# Same refusals as Open-ValidatedPayload in NativeKit.Core.ps1.
FORBIDDEN = re.compile(r'(?i)\.(ex5|ex4|log|exe|dll|ps1|bat|cmd|lnk)$|^MQL5/Files(/|$)')
ENTRY_CAP, ENTRY_COUNT_CAP, TOTAL_CAP = 8 * 1024 * 1024, 512, 64 * 1024 * 1024
RESULTS_CAP = 256 * 1024 * 1024
RUN_ID = re.compile(r'^[A-Za-z0-9_-]{1,64}$')
TASK_NAME = 'StoikusNativeAgent'
AGENT_TIMEOUT = 3 * 3600
POLL_INTERVAL = 10.0
SCOPES = ('compile', 'tests', 'all')
NOT_MEASURED_GATES = ('tester', 'terminal_interaction', 'alerts_sound', 'installation')


class TransportError(RuntimeError):
    pass


class SshTransport:
    """OpenSSH with the lab's dedicated key alias; BatchMode never prompts for a password."""

    OPTIONS = ('-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15')

    def __init__(self, host: str):
        self.host = host

    def run(self, command: str, timeout: float) -> tuple[int, str]:
        # stdin closed: a remote prompt (e.g. a password) fails at once instead of hanging.
        try:
            done = subprocess.run(['ssh', '-n', *self.OPTIONS, self.host, command], capture_output=True, stdin=subprocess.DEVNULL,
                                  text=True, encoding='utf-8', errors='replace', timeout=timeout, check=False)
        except subprocess.TimeoutExpired as error:
            raise TransportError(f'remote command exceeded {timeout:g}s') from error
        return done.returncode, done.stdout + done.stderr

    def put(self, local_path: Path, remote_path: str) -> None:
        self.copy([str(local_path), f'{self.host}:{scp_path(remote_path)}'])

    def get(self, remote_path: str, local_path: Path) -> None:
        self.copy([f'{self.host}:{scp_path(remote_path)}', str(local_path)])

    def copy(self, arguments: list[str]) -> None:
        done = subprocess.run(['scp', '-q', *self.OPTIONS, *arguments], capture_output=True, text=True, check=False)
        if done.returncode != 0:
            raise TransportError(f'scp failed: {done.stderr.strip()}')


def scp_path(remote_path: str) -> str:
    """Windows OpenSSH addresses drive paths as /C:/..."""
    return '/' + remote_path.replace('\\', '/').lstrip('/')


def remote_run_dir(run_id: str) -> str:
    if not RUN_ID.match(run_id):
        raise ValueError(f'invalid run id: {run_id!r}')
    return f'{LAB_ROOT}/runs/{run_id}'


def windows_path(remote_path: str) -> str:
    return remote_path.replace('/', '\\')


def prepare_command(run_id: str) -> str:
    """Fails (mkdir error) when the run id was already used."""
    return f'mkdir {windows_path(remote_run_dir(run_id))}\\inbox'


def trigger_command(run_id: str, script: str, arguments: str = '') -> str:
    """The agent runs in the lab user's interactive session: a one-shot task, recreated with /create /f.

    The SSH logon cannot reach WMI, other sessions' processes or the desktop; `schtasks /change`
    would prompt for the user's password, so it is never used.
    """
    remote_run_dir(run_id)
    action = (f'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy RemoteSigned -WindowStyle Hidden '
              f'-File {script} -RunId {run_id}{arguments}')
    return (f'schtasks /create /tn {TASK_NAME} /tr "{action}" /sc once /st 23:59 /it /f && '
            f'schtasks /run /tn {TASK_NAME}')


def delete_task_command() -> str:
    """`/sc once` keeps a real trigger at 23:59; the task is removed as soon as the run is done."""
    return f'schtasks /delete /tn {TASK_NAME} /f'


def remove_task(transport) -> str:
    try:
        code, output = transport.run(delete_task_command(), timeout=60)
    except TransportError as error:
        return f'FAILED: {error}'
    return 'DELETED' if code == 0 else f'FAILED: {output.strip()}'


def agent_command(run_id: str, scope: str) -> str:
    if scope not in SCOPES:
        raise ValueError(f'invalid scope: {scope!r}')
    return trigger_command(run_id, AGENT_SCRIPT, f' -Scope {scope}')


def wait_done(transport, run_id: str, timeout: float, interval: float) -> dict:
    """Poll the agent's done.json, written last and atomically by the agent's finally block."""
    path = windows_path(remote_run_dir(run_id)) + '\\done.json'
    deadline = time.monotonic() + timeout
    while True:
        code, output = transport.run(f'type {path}', timeout=60)
        if code == 0 and output.strip():
            return json.loads(output.strip().lstrip('﻿'))
        if time.monotonic() >= deadline:
            raise TransportError(f'agent did not finish within {timeout:g}s')
        time.sleep(interval)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_value(root: Path, *args: str) -> str:
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else 'UNKNOWN'


def mql_files(root: Path) -> list[Path]:
    base = root / PRODUCT / 'MQL5'
    return sorted(path for path in base.rglob('*') if path.is_file() and path.name != '.DS_Store')


def input_hashes(root: Path) -> dict[str, str]:
    """Frozen inputs: the MQL5 tree under `root` plus this runner and its agent."""
    hashes = {path.relative_to(root).as_posix(): sha256_bytes(path.read_bytes()) for path in mql_files(root)}
    tools = [ROOT / 'tools/stoikus_native_runner.py', ROOT / 'tools/stoikus_native_parsers.py',
             *(AGENT_DIR / name for name in AGENT_FILES)]
    hashes.update({f'runner:{path.relative_to(ROOT).as_posix()}': sha256_bytes(path.read_bytes())
                   for path in tools if path.is_file()})
    return hashes


def build_payload(root: Path, out_dir: Path) -> tuple[Path, dict]:
    """Deterministic payload.zip and the identity NativeKit.Core validates it against."""
    base = root / PRODUCT
    entries, total = [], 0
    for path in mql_files(root):
        relative = path.relative_to(base).as_posix()
        if FORBIDDEN.search(relative):
            raise ValueError(f'forbidden artifact in payload: {relative}')
        if path.is_symlink():
            raise ValueError(f'symlink refused in payload: {relative}')
        data = path.read_bytes()
        if len(data) > ENTRY_CAP:
            raise ValueError(f'entry exceeds 8 MiB: {relative}')
        total += len(data)
        entries.append({'path': relative, 'bytes': len(data), 'sha256': sha256_bytes(data), 'data': data})
    if not entries or len(entries) > ENTRY_COUNT_CAP or total > TOTAL_CAP:
        raise ValueError('payload outside the NativeKit.Core caps')
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / 'payload.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for entry in entries:
            info = zipfile.ZipInfo(entry['path'], date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, entry.pop('data'))
    programs = sorted(entry['path'] for entry in entries if entry['path'].endswith('.mq5'))
    identity = {'kind': IDENTITY_KIND, 'schema_version': 1, 'product': PRODUCT,
                'zip': {'name': zip_path.name, 'bytes': zip_path.stat().st_size, 'sha256': sha256_bytes(zip_path.read_bytes())},
                'programs': programs,
                'tests': [path for path in programs if path.startswith('MQL5/Scripts/') and path.endswith('_Tests.mq5')],
                'entries': entries}
    return zip_path, identity


def safe_extract(archive_path: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.infolist()
        if sum(member.file_size for member in members) > RESULTS_CAP:
            raise ValueError('results exceed the size cap')
        for member in members:
            name = PurePosixPath(member.filename)
            if member.filename.startswith('/') or '..' in name.parts or ':' in member.filename or '\\' in member.filename:
                raise ValueError(f'unsafe result entry: {member.filename}')
        destination.mkdir(parents=True, exist_ok=False)
        archive.extractall(destination)


def check(name: str, result: str, reason: str, **details: object) -> dict:
    assert result in RESULTS, result
    return {'name': name, 'result': result, 'reason': reason, **details}


def verified_file(results_dir: Path, relative: str | None, expected: str | None) -> bytes | None:
    if not relative or not expected:
        return None
    path = results_dir / relative
    if not path.is_file():
        return None
    data = path.read_bytes()
    return data if sha256_bytes(data) == expected else None


def compile_check(program: str, row: dict | None, results_dir: Path, expected_sha256: str | None) -> dict:
    name = f'compile:{program}'
    if row is None:
        return check(name, 'ENVIRONMENT_ERROR', 'no compile record from the agent')
    log = verified_file(results_dir, row.get('log'), row.get('log_sha256'))
    details = {key: row.get(key) for key in ('status', 'exit_code', 'source_sha256', 'log_sha256', 'ex5_sha256', 'ex5_bytes')}
    details['log_result'] = row.get('log_result')
    if row.get('source_sha256') != expected_sha256:
        return check(name, 'TEST_HARNESS_FAIL', 'compiled source differs from the frozen identity', **details)
    if row.get('log') and log is None:
        return check(name, 'TEST_HARNESS_FAIL', 'compile log missing or hash differs from the agent record', **details)
    result_log = row.get('log_result') or {}
    if row.get('status') == 'COMPILED' and result_log.get('accepted') and row.get('ex5_sha256'):
        return check(name, 'PASS', 'log with 0 errors and 0 warnings and a new EX5', **details)
    if row.get('status') == 'FAILED' and (result_log.get('errors') or result_log.get('warnings')):
        return check(name, 'PRODUCT_FAIL', 'compiler reported errors or warnings', **details)
    if row.get('status') == 'FAILED' and result_log.get('errors') == 0 and result_log.get('warnings') == 0:
        return check(name, 'TEST_HARNESS_FAIL', 'compiler reported 0 errors and 0 warnings, but the frozen '
                     f'NativeKit.Core log grammar refused the log ({result_log.get("reason")})', **details)
    return check(name, 'ENVIRONMENT_ERROR', f'compilation incomplete: {row.get("status")}', **details)


def test_check(script_path: str, row: dict | None, compiled: str, results_dir: Path) -> dict:
    script = PurePosixPath(script_path).stem
    name = f'test:{script}'
    if compiled != 'PASS':
        return check(name, 'NOT_RUN', 'the script did not compile in this run')
    if row is None:
        return check(name, 'ENVIRONMENT_ERROR', 'no execution record from the agent')
    excerpt = verified_file(results_dir, row.get('excerpt'), row.get('excerpt_sha256'))
    if excerpt is None:
        return check(name, 'TEST_HARNESS_FAIL', 'log excerpt missing or hash differs from the agent record')
    text = excerpt.decode('utf-16') if excerpt.startswith((b'\xff\xfe', b'\xfe\xff')) else excerpt.decode('utf-8', 'replace')
    verdict = classify_excerpt(script, text)
    details = {key: verdict[key] for key in ('summary_line', 'passes', 'failures', 'total', 'fail_lines', 'runtime_errors', 'not_run_line')}
    details.update(status=row.get('status'), duration_seconds=row.get('duration_seconds'), excerpt_sha256=row.get('excerpt_sha256'))
    if row.get('status') != 'RAN' and verdict['result'] != 'PRODUCT_FAIL':
        return check(name, 'ENVIRONMENT_ERROR', f'execution incomplete: {row.get("status")}', **details)
    return check(name, str(verdict['result']), str(verdict['reason']), **details)


def agent_problem(agent: dict, identity: dict, run_id: str) -> str | None:
    if agent.get('schema') != AGENT_RECEIPT_SCHEMA or agent.get('run_id') != run_id:
        return 'agent receipt schema or run id differs'
    if agent.get('core_sha256') != CORE_SHA256:
        return 'agent loaded a NativeKit.Core different from the pinned one'
    payload = agent.get('payload') or {}
    if payload.get('zip_sha256') != identity['zip']['sha256'] or payload.get('validation') != 'PASS':
        return 'agent did not validate the payload that was sent'
    if agent.get('error'):
        return f'agent error: {agent["error"]}'
    return None


def execute(transport, root: Path, artifact: Path, scope: str = 'all', run_id: str | None = None,
            poll_interval: float = POLL_INTERVAL) -> dict:
    run_id = run_id or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    remote_run_dir(run_id)
    started = now()
    before = input_hashes(root)
    artifact = artifact.resolve()
    results_dir = artifact.with_suffix('.results')
    checks: list[dict] = []
    agent: dict = {}
    identity: dict = {}
    task_cleanup = 'NOT_STARTED'
    with tempfile.TemporaryDirectory(prefix='stoikus-native-') as work:
        work_dir = Path(work)
        zip_path, identity = build_payload(root, work_dir)
        identity_path = work_dir / 'identity.json'
        identity_path.write_text(json.dumps(identity, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        try:
            code, output = transport.run(prepare_command(run_id), timeout=60)
            if code != 0:
                raise TransportError(f'could not create the run folder (already used?): {output.strip()}')
            inbox = remote_run_dir(run_id) + '/inbox'
            transport.put(zip_path, f'{inbox}/payload.zip')
            transport.put(identity_path, f'{inbox}/identity.json')
            code, output = transport.run(agent_command(run_id, scope), timeout=60)
            if code != 0:
                raise TransportError(f'could not start the agent task: {output.strip()}')
            try:
                reported = wait_done(transport, run_id, AGENT_TIMEOUT, poll_interval)
            finally:
                task_cleanup = remove_task(transport)
            local_results = work_dir / 'results.zip'
            transport.get(reported['results'], local_results)
        except (TransportError, KeyError, ValueError, OSError) as error:
            checks.append(check('transport', 'ENVIRONMENT_ERROR', str(error)))
        else:
            problem = None
            if sha256_bytes(local_results.read_bytes()) != reported.get('sha256'):
                problem = 'results.zip SHA-256 differs from the hash the agent reported'
            else:
                try:
                    safe_extract(local_results, results_dir)
                    agent = json.loads((results_dir / 'agent-receipt.json').read_text(encoding='utf-8'))
                    problem = agent_problem(agent, identity, run_id)
                except (ValueError, OSError, zipfile.BadZipFile) as error:
                    problem = str(error)
            if problem:
                checks.append(check('results-integrity', 'TEST_HARNESS_FAIL', problem))
            else:
                checks.append(check('results-integrity', 'PASS', 'hash, entries and agent receipt verified',
                                    results_sha256=reported['sha256']))
                rows = {row.get('path'): row for row in agent.get('compile', [])}
                frozen = {entry['path']: entry['sha256'] for entry in identity['entries']}
                compiled = {}
                for program in identity['programs']:
                    result = compile_check(program, rows.get(program), results_dir, frozen.get(program))
                    compiled[program] = result['result']
                    checks.append(result)
                if scope != 'compile':
                    test_rows = {row.get('script'): row for row in agent.get('tests', [])}
                    for script in identity['tests']:
                        checks.append(test_check(script, test_rows.get(PurePosixPath(script).stem), compiled[script], results_dir))
                golden = agent.get('golden') or {}
                same = re.fullmatch(r'[a-f0-9]{64}', str(golden.get('before_sha256'))) and \
                    golden.get('before_sha256') == golden.get('after_sha256')
                checks.append(check('golden-unchanged', 'PASS' if same else 'TEST_HARNESS_FAIL',
                                    'golden terminal inventory identical before and after' if same
                                    else 'golden terminal inventory changed or was not measured', **golden))
    after = input_hashes(root)
    changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
    if changed:
        checks.append(check('input-stability', 'TEST_HARNESS_FAIL',
                            'inputs changed during the run; the receipt cannot certify one candidate', paths=changed))
    counts = Counter(item['result'] for item in checks)
    compile_checks = [item for item in checks if item['name'].startswith('compile:')]
    test_checks = [item for item in checks if item['name'].startswith('test:')]
    receipt = {
        'schema_version': 1, 'suite': 'MT5_NATIVE', 'scope': scope, 'run_id': run_id,
        'started_at': started, 'finished_at': now(),
        'result': aggregate_result(checks),
        'status': 'PASSED' if checks and all(item['result'] == 'PASS' for item in checks) else 'FAILED',
        'summary': {result: counts[result] for result in RESULTS},
        'candidate': {'head': git_value(root, 'rev-parse', 'HEAD'), 'branch': git_value(root, 'branch', '--show-current'),
                      'dirty_status': git_value(root, 'status', '--porcelain=v1').splitlines(),
                      'input_fingerprint': fingerprint(before), 'source_hashes': before, 'inputs_unchanged': not changed,
                      'payload_sha256': identity.get('zip', {}).get('sha256')},
        'environment': {'mac': {'platform': platform.platform(), 'python': sys.version.split()[0]},
                        'lab': agent.get('environment')},
        'native_gates': {'compilation': aggregate_result(compile_checks), 'test_scripts': aggregate_result(test_checks),
                         **{gate: 'NOT_RUN' for gate in NOT_MEASURED_GATES}},
        'results_dir': results_dir.name if results_dir.exists() else None,
        'lab_task_cleanup': task_cleanup,
        'checks': checks,
        'limits': 'Native evidence of these bytes only. Tester, chart interaction, alerts, installation and '
                  'human acceptance are not covered; no orders are sent and no real account is used.',
    }
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return receipt


def local_agent_hashes() -> dict[str, str]:
    hashes = {name: sha256_bytes((AGENT_DIR / name).read_bytes()) for name in AGENT_FILES}
    if hashes['NativeKit.Core.ps1'] != CORE_SHA256:
        raise ValueError('local NativeKit.Core.ps1 differs from the sealed kit')
    return hashes


def install_agent(transport) -> dict:
    """Publish the agent to C:\\MT5Lab\\bin and confirm every file by its SHA-256 on Windows."""
    hashes = local_agent_hashes()
    transport.run('if not exist C:\\MT5Lab\\bin mkdir C:\\MT5Lab\\bin', timeout=60)
    for name in AGENT_FILES:
        transport.put(AGENT_DIR / name, f'{LAB_ROOT}/bin/{name}')
    _, output = transport.run('powershell.exe -NoProfile -NonInteractive -Command "Get-ChildItem C:\\MT5Lab\\bin -File | '
                              'ForEach-Object { $_.Name + \' \' + (Get-FileHash $_.FullName -Algorithm SHA256).Hash }"', timeout=60)
    remote = {}
    for line in output.splitlines():
        parts = line.strip().rsplit(' ', 1)
        if len(parts) == 2 and re.fullmatch(r'[A-Fa-f0-9]{64}', parts[1]):
            remote[parts[0]] = parts[1].lower()
    mismatched = sorted(name for name in AGENT_FILES if remote.get(name) != hashes[name])
    return {'installed': not mismatched, 'mismatched': mismatched, 'hashes': hashes}


def self_test(transport, run_id: str | None = None, poll_interval: float = POLL_INTERVAL) -> dict:
    run_id = run_id or 'selftest-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    code, output = transport.run(f'mkdir {windows_path(remote_run_dir(run_id))}', timeout=60)
    if code != 0:
        raise TransportError(f'could not create the self-test folder: {output.strip()}')
    code, output = transport.run(trigger_command(run_id, SELF_TEST_SCRIPT), timeout=60)
    if code != 0:
        raise TransportError(f'could not start the self-test task: {output.strip()}')
    try:
        outcome = wait_done(transport, run_id, 600, poll_interval)
    finally:
        cleanup = remove_task(transport)
    outcome['lab_task_cleanup'] = cleanup
    return outcome


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--host', default='jpw-mt5-lab', help='SSH alias of the lab (see ~/.ssh/config)')
    parser.add_argument('--scope', choices=SCOPES, default='all')
    parser.add_argument('--artifact', type=Path)
    parser.add_argument('--run-id')
    parser.add_argument('--install-agent', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    transport = SshTransport(args.host)
    if args.install_agent:
        outcome = install_agent(transport)
        print(json.dumps(outcome, indent=2))
        return 0 if outcome['installed'] else 1
    if args.self_test:
        outcome = self_test(transport)
        print(json.dumps(outcome, indent=2))
        return 0 if outcome.get('result') == 'PASS' else 1
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    artifact = args.artifact or ROOT / 'tools/.artifacts' / f'mt5-native-{stamp}.json'
    receipt = execute(transport, ROOT, artifact, scope=args.scope, run_id=args.run_id)
    print(f'RECEIPT: {artifact}\nRESULT: {receipt["result"]}\nSUMMARY: {json.dumps(receipt["summary"])}')
    print(f'NATIVE GATES: {json.dumps(receipt["native_gates"])}')
    return 0 if receipt['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

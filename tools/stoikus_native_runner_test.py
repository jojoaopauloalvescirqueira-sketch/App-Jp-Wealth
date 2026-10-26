#!/usr/bin/env python3
"""Host controls for the Stoikus native runner; no SSH, Windows or MT5 is used.

A fake transport plays the Windows agent: it reads the uploaded payload and
identity and answers with an agent receipt built from a scenario, so the
whole Mac-side flow (freeze, transport, verification, classification and the
final receipt) is exercised against controlled native outcomes.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import zipfile

import stoikus_native_runner as runner
from stoikus_native_parsers_test import EXAMPLES, mt5_line

KIT = runner.ROOT / 'downloads/jpw-alavancagem-atual/Kit_Windows_Stoikus_Painel_C5_D1.zip'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FakeTransport:
    """In-memory stand-in for the lab: remote paths map to a local directory."""

    def __init__(self, scenario: dict | None = None):
        self.remote = Path(tempfile.mkdtemp(prefix='fake-mt5lab-'))
        self.scenario = scenario or {}
        self.commands: list[str] = []

    def local(self, remote_path: str) -> Path:
        return self.remote / remote_path.replace('\\', '/').lstrip('/').replace(':', '')

    def put(self, local_path: Path, remote_path: str) -> None:
        target = self.local(remote_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(local_path, target)

    def get(self, remote_path: str, local_path: Path) -> None:
        shutil.copyfile(self.local(remote_path), local_path)

    def run(self, command: str, timeout: float) -> tuple[int, str]:
        """Plays cmd.exe on the lab for the three commands the runner may send."""
        self.commands.append(command)
        if command.startswith('mkdir '):
            target = self.local(command[len('mkdir '):].strip())
            if target.exists():
                return 1, 'A subdirectory or file already exists.'
            target.mkdir(parents=True)
            return 0, ''
        if command.startswith('schtasks /create'):
            self.answer(self.run_id(command))
            return 0, 'SUCCESS: Attempted to run the scheduled task "StoikusNativeAgent".'
        if command.startswith('schtasks /delete'):
            return 0, 'SUCCESS: The scheduled task "StoikusNativeAgent" was successfully deleted.'
        if command.startswith('type '):
            path = self.local(command[len('type '):].strip())
            return (0, path.read_text()) if path.exists() else (1, 'The system cannot find the file specified.')
        return 1, f'unexpected command: {command}'

    @staticmethod
    def run_id(command: str) -> str:
        return command.split('-RunId ')[1].split()[0].rstrip('"')

    def answer(self, run_id: str) -> None:
        inbox = self.local(runner.remote_run_dir(run_id) + '/inbox')
        identity = json.loads((inbox / 'identity.json').read_text())
        mutate = self.scenario.get('before_answer')
        if mutate:
            mutate()
        compile_rows, files = [], {}
        frozen = {entry['path']: entry['sha256'] for entry in identity['entries']}
        for program in identity['programs']:
            name = Path(program).stem
            outcome = self.scenario.get('compile', {}).get(name, 'COMPILED')
            if outcome == 'MISSING':
                continue
            log = f'compiling \'{name}.mq5\'\nResult: 0 errors, 0 warnings, 10 ms elapsed\n'
            accepted = outcome in ('COMPILED', 'TAMPERED')
            warnings = 1 if outcome == 'WARNING' else 0
            if outcome == 'WARNING':
                log = f'compiling \'{name}.mq5\'\nimplicit conversion warning\nResult: 0 errors, 1 warnings, 10 ms elapsed\n'
            files[f'logs/compile/{name}.log'] = log.encode()
            compile_rows.append({'path': program, 'source_sha256': '0' * 64 if outcome == 'TAMPERED' else frozen[program],
                                 'status': 'COMPILED' if accepted else ('TIMEOUT' if outcome == 'TIMEOUT' else 'FAILED'),
                                 'exit_code': 1, 'log': f'logs/compile/{name}.log',
                                 'log_sha256': sha256(files[f'logs/compile/{name}.log']),
                                 'log_result': None if outcome == 'TIMEOUT' else
                                 {'accepted': accepted, 'reason': 'ok' if accepted else 'UNRECOGNIZED_OR_FOREIGN_BODY_LINE',
                                  'errors': 0, 'warnings': warnings},
                                 'ex5_sha256': '1' * 64 if accepted else None, 'ex5_bytes': 2048 if accepted else None})
        test_rows = []
        for test in identity['tests']:
            name = Path(test).stem
            status, lines = self.scenario.get('tests', {}).get(name, ('RAN', ['starting', EXAMPLES[name][0]]))
            excerpt = '\n'.join(mt5_line(name, line) for line in lines).encode()
            files[f'logs/tests/{name}.log'] = excerpt
            test_rows.append({'script': name, 'status': status, 'duration_seconds': 3.2,
                              'excerpt': f'logs/tests/{name}.log', 'excerpt_sha256': sha256(excerpt)})
        golden = self.scenario.get('golden', ('a' * 64, 'a' * 64))
        receipt = {'schema': runner.AGENT_RECEIPT_SCHEMA, 'run_id': run_id,
                   'core_sha256': self.scenario.get('core_sha256', runner.CORE_SHA256),
                   'payload': {'zip_sha256': identity['zip']['sha256'], 'validation': 'PASS'},
                   'environment': {'os': 'Windows 11 synthetic', 'metaeditor': {'sha256': '2' * 64, 'version': '5.0.0.5000'},
                                   'terminal': {'sha256': '3' * 64, 'version': '5.0.0.5000'}},
                   'golden': {'before_sha256': golden[0], 'after_sha256': golden[1]},
                   'compile': compile_rows, 'tests': test_rows, 'error': self.scenario.get('agent_error')}
        files['agent-receipt.json'] = json.dumps(receipt).encode()
        files.update(self.scenario.get('extra_entries', {}))
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        results = self.local(runner.remote_run_dir(run_id) + '/results.zip')
        results.write_bytes(buffer.getvalue())
        reported = self.scenario.get('reported_sha256', sha256(buffer.getvalue()))
        done = {'results': runner.remote_run_dir(run_id) + '/results.zip', 'sha256': reported, 'error': None}
        self.local(runner.remote_run_dir(run_id) + '/done.json').write_text('﻿' + json.dumps(done))


class PayloadTests(unittest.TestCase):
    def test_payload_is_deterministic_and_core_compatible(self):
        with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as two:
            zip_a, identity_a = runner.build_payload(runner.ROOT, Path(one))
            zip_b, identity_b = runner.build_payload(runner.ROOT, Path(two))
            self.assertEqual(zip_a.read_bytes(), zip_b.read_bytes())
            self.assertEqual(identity_a, identity_b)
            on_disk = sorted(p for p in (runner.ROOT / runner.PRODUCT / 'MQL5').rglob('*') if p.is_file() and p.name != '.DS_Store')
            entries = identity_a['entries']
            self.assertEqual(len(entries), len(on_disk))
            self.assertLessEqual(len(entries), 512)
            self.assertEqual(identity_a['zip'], {'name': 'payload.zip', 'bytes': zip_a.stat().st_size, 'sha256': sha256(zip_a.read_bytes())})
            with zipfile.ZipFile(zip_a) as archive:
                self.assertEqual(archive.namelist(), [entry['path'] for entry in entries])
                for entry in entries:
                    data = archive.read(entry['path'])
                    self.assertTrue(entry['path'].startswith('MQL5/'))
                    self.assertNotRegex(entry['path'], r'(?i)\.(ex5|ex4|log|exe|dll|ps1|bat|cmd|lnk)$|^MQL5/Files(/|$)')
                    self.assertEqual((entry['bytes'], entry['sha256']), (len(data), sha256(data)))
                    self.assertLessEqual(entry['bytes'], 8 * 1024 * 1024)
            self.assertEqual(len(identity_a['programs']), 34)
            self.assertEqual(len(identity_a['tests']), 24)
            self.assertTrue(set(identity_a['tests']) <= set(identity_a['programs']))

    def test_forbidden_artifact_in_the_tree_refuses_the_payload(self):
        with tempfile.TemporaryDirectory() as root:
            product = Path(root) / runner.PRODUCT / 'MQL5/Scripts/JPWealth'
            product.mkdir(parents=True)
            (product / 'JPW_X_Tests.mq5').write_text('void OnStart(){}')
            (product / 'JPW_X_Tests.ex5').write_bytes(b'old binary')
            with self.assertRaisesRegex(ValueError, 'forbidden'):
                runner.build_payload(Path(root), Path(root) / 'out')

    def test_reused_core_is_byte_identical_to_the_sealed_kit(self):
        local = (runner.AGENT_DIR / 'NativeKit.Core.ps1').read_bytes()
        with zipfile.ZipFile(KIT) as kit:
            self.assertEqual(local, kit.read('NativeKit.Core.ps1'))
        self.assertEqual(sha256(local), runner.CORE_SHA256)


class RunnerFlowTests(unittest.TestCase):
    def run_cycle(self, scenario: dict | None = None, scope: str = 'all', root: Path = runner.ROOT) -> dict:
        transport = FakeTransport(scenario)
        self.addCleanup(shutil.rmtree, transport.remote, True)
        with tempfile.TemporaryDirectory() as directory:
            receipt = runner.execute(transport, root, Path(directory) / 'native.json', scope=scope, run_id='T20261026', poll_interval=0)
            self.assertEqual(json.loads((Path(directory) / 'native.json').read_text())['result'], receipt['result'])
            return receipt

    def check(self, receipt: dict, name: str) -> dict:
        return next(check for check in receipt['checks'] if check['name'] == name)

    def test_clean_cycle_passes_with_separate_native_gates(self):
        receipt = self.run_cycle()
        self.assertEqual(receipt['result'], 'PASS')
        self.assertEqual(receipt['summary']['PASS'], 34 + 24 + 2)
        self.assertEqual(receipt['native_gates']['compilation'], 'PASS')
        self.assertEqual(receipt['native_gates']['test_scripts'], 'PASS')
        for gate in ('tester', 'terminal_interaction', 'alerts_sound', 'installation'):
            self.assertEqual(receipt['native_gates'][gate], 'NOT_RUN')
        self.assertTrue(receipt['candidate']['inputs_unchanged'])
        self.assertEqual(receipt['suite'], 'MT5_NATIVE')

    def test_compile_only_scope_leaves_test_scripts_not_run(self):
        receipt = self.run_cycle(scope='compile')
        self.assertEqual(receipt['result'], 'PASS')
        self.assertEqual(receipt['native_gates']['test_scripts'], 'NOT_RUN')
        self.assertFalse(any(check['name'].startswith('test:') for check in receipt['checks']))

    def test_compile_warning_is_product_fail_and_blocks_its_test(self):
        receipt = self.run_cycle({'compile': {'JPW_Alavancagem_Genesis_Tests': 'WARNING'}})
        self.assertEqual(receipt['result'], 'PRODUCT_FAIL')
        self.assertEqual(self.check(receipt, 'compile:MQL5/Scripts/JPWealth/JPW_Alavancagem_Genesis_Tests.mq5')['result'], 'PRODUCT_FAIL')
        self.assertEqual(self.check(receipt, 'test:JPW_Alavancagem_Genesis_Tests')['result'], 'NOT_RUN')

    def test_compile_timeout_is_environment_error(self):
        receipt = self.run_cycle({'compile': {'JPW_Stoikus_Monitor': 'TIMEOUT'}})
        self.assertEqual(self.check(receipt, 'compile:MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5')['result'], 'ENVIRONMENT_ERROR')

    def test_zero_zero_log_refused_by_the_frozen_grammar_is_a_harness_failure(self):
        receipt = self.run_cycle({'compile': {'JPW_Stoikus_Abrir_Paineis': 'REFUSED'}})
        verdict = self.check(receipt, 'compile:MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5')
        self.assertEqual(verdict['result'], 'TEST_HARNESS_FAIL')
        self.assertIn('log grammar refused', verdict['reason'])

    def test_compiled_source_different_from_the_identity_is_refused(self):
        receipt = self.run_cycle({'compile': {'JPW_Stoikus_Monitor': 'TAMPERED'}})
        verdict = self.check(receipt, 'compile:MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5')
        self.assertEqual(verdict['result'], 'TEST_HARNESS_FAIL')
        self.assertIn('frozen identity', verdict['reason'])

    def test_missing_compile_record_is_environment_error_and_blocks_the_test(self):
        receipt = self.run_cycle({'compile': {'JPW_NoCuda_Core_Tests': 'MISSING'}})
        self.assertEqual(self.check(receipt, 'compile:MQL5/Scripts/JPWealth/JPW_NoCuda_Core_Tests.mq5')['result'], 'ENVIRONMENT_ERROR')
        self.assertEqual(self.check(receipt, 'test:JPW_NoCuda_Core_Tests')['result'], 'NOT_RUN')

    def test_agent_error_or_foreign_core_refuses_every_native_verdict(self):
        for scenario in ({'agent_error': 'Golden terminal incomplete'}, {'core_sha256': 'f' * 64}):
            with self.subTest(scenario=scenario):
                receipt = self.run_cycle(scenario)
                self.assertEqual(self.check(receipt, 'results-integrity')['result'], 'TEST_HARNESS_FAIL')
                self.assertFalse(any(check['name'].startswith(('compile:', 'test:')) for check in receipt['checks']))
                self.assertEqual(receipt['native_gates']['compilation'], 'NOT_RUN')
                self.assertEqual(receipt['native_gates']['test_scripts'], 'NOT_RUN')

    def test_lab_task_is_deleted_after_every_run(self):
        receipt = self.run_cycle()
        self.assertEqual(receipt['lab_task_cleanup'], 'DELETED')

    def test_failing_script_and_missing_summary_are_classified(self):
        receipt = self.run_cycle({'tests': {
            'JPW_SignalCopy_Tests': ('RAN', [EXAMPLES['JPW_SignalCopy_Tests'][1]]),
            'JPW_Alavancagem_Tests': ('RAN', ['script loaded']),
            'JPW_Alavancagem_Metrics_Tests': ('RAN', [EXAMPLES['JPW_Alavancagem_Metrics_Tests'][2]])}})
        self.assertEqual(self.check(receipt, 'test:JPW_SignalCopy_Tests')['result'], 'PRODUCT_FAIL')
        self.assertEqual(self.check(receipt, 'test:JPW_Alavancagem_Tests')['result'], 'ENVIRONMENT_ERROR')
        self.assertEqual(self.check(receipt, 'test:JPW_Alavancagem_Metrics_Tests')['result'], 'NOT_RUN')
        self.assertEqual(receipt['result'], 'PRODUCT_FAIL')

    def test_timeout_with_a_passing_summary_is_not_pass(self):
        receipt = self.run_cycle({'tests': {'JPW_NoCuda_Core_Tests': ('TIMEOUT', [EXAMPLES['JPW_NoCuda_Core_Tests'][0]])}})
        self.assertEqual(self.check(receipt, 'test:JPW_NoCuda_Core_Tests')['result'], 'ENVIRONMENT_ERROR')

    def test_reported_hash_mismatch_refuses_the_results(self):
        receipt = self.run_cycle({'reported_sha256': '9' * 64})
        self.assertEqual(receipt['result'], 'TEST_HARNESS_FAIL')
        self.assertEqual(self.check(receipt, 'results-integrity')['result'], 'TEST_HARNESS_FAIL')
        self.assertFalse(any(check['name'].startswith(('compile:', 'test:')) for check in receipt['checks']))

    def test_unsafe_result_entry_refuses_the_results(self):
        receipt = self.run_cycle({'extra_entries': {'../escape.txt': b'x'}})
        self.assertEqual(self.check(receipt, 'results-integrity')['result'], 'TEST_HARNESS_FAIL')

    def test_changed_golden_terminal_is_harness_failure(self):
        receipt = self.run_cycle({'golden': ('a' * 64, 'b' * 64)})
        self.assertEqual(self.check(receipt, 'golden-unchanged')['result'], 'TEST_HARNESS_FAIL')
        self.assertEqual(receipt['result'], 'TEST_HARNESS_FAIL')

    def test_source_change_during_the_run_is_detected(self):
        copy = Path(tempfile.mkdtemp(prefix='native-root-'))
        self.addCleanup(shutil.rmtree, copy, True)
        shutil.copytree(runner.ROOT / runner.PRODUCT / 'MQL5', copy / runner.PRODUCT / 'MQL5')
        target = copy / runner.PRODUCT / 'MQL5/Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5'
        receipt = self.run_cycle({'before_answer': lambda: target.write_bytes(target.read_bytes() + b'\n// drift\n')}, root=copy)
        self.assertEqual(self.check(receipt, 'input-stability')['result'], 'TEST_HARNESS_FAIL')
        self.assertFalse(receipt['candidate']['inputs_unchanged'])

    def test_remote_commands_stay_inside_the_lab(self):
        transport = FakeTransport()
        self.addCleanup(shutil.rmtree, transport.remote, True)
        with tempfile.TemporaryDirectory() as directory:
            runner.execute(transport, runner.ROOT, Path(directory) / 'n.json', scope='all', run_id='T20261026', poll_interval=0)
        kinds = [' '.join(command.split()[:2]) for command in transport.commands]
        self.assertEqual(kinds[:2], ['mkdir C:\\MT5Lab\\runs\\T20261026\\inbox', 'schtasks /create'])
        self.assertTrue(all(kind.startswith('type ') for kind in kinds[2:-1]))
        self.assertEqual(transport.commands[-1], 'schtasks /delete /tn StoikusNativeAgent /f')
        for command in transport.commands[:-1]:
            self.assertIn('C:\\MT5Lab\\', command)
        for command in transport.commands:
            self.assertNotRegex(command, r'(?i)Remove-Item|\brm\b|\bdel\b|format|Set-ExecutionPolicy|/change|taskkill')
        trigger = transport.commands[1]
        self.assertIn('C:\\MT5Lab\\bin\\Invoke-StoikusNativeRun.ps1 -RunId T20261026 -Scope all', trigger)
        self.assertIn(' /it /f && schtasks /run /tn StoikusNativeAgent', trigger)

    def test_reused_run_id_is_refused_without_starting_the_agent(self):
        transport = FakeTransport()
        self.addCleanup(shutil.rmtree, transport.remote, True)
        transport.local(runner.remote_run_dir('T20261026') + '/inbox').mkdir(parents=True)
        with tempfile.TemporaryDirectory() as directory:
            receipt = runner.execute(transport, runner.ROOT, Path(directory) / 'n.json', run_id='T20261026', poll_interval=0)
        self.assertEqual(self.check(receipt, 'transport')['result'], 'ENVIRONMENT_ERROR')
        self.assertFalse(any(command.startswith('schtasks') for command in transport.commands))

    def test_agent_that_never_finishes_is_an_environment_error(self):
        class Silent(FakeTransport):
            def answer(self, run_id):
                return None
        transport = Silent()
        self.addCleanup(shutil.rmtree, transport.remote, True)
        original = runner.AGENT_TIMEOUT
        runner.AGENT_TIMEOUT = 0
        self.addCleanup(setattr, runner, 'AGENT_TIMEOUT', original)
        with tempfile.TemporaryDirectory() as directory:
            receipt = runner.execute(transport, runner.ROOT, Path(directory) / 'n.json', run_id='T20261026', poll_interval=0)
        self.assertEqual(self.check(receipt, 'transport')['result'], 'ENVIRONMENT_ERROR')
        self.assertIn('did not finish', self.check(receipt, 'transport')['reason'])
        self.assertEqual(transport.commands[-1], 'schtasks /delete /tn StoikusNativeAgent /f')
        self.assertEqual(receipt['lab_task_cleanup'], 'DELETED')

    def test_invalid_run_id_is_refused(self):
        with self.assertRaises(ValueError):
            runner.remote_run_dir('../x')


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
    raise SystemExit(0 if result.wasSuccessful() else 1)

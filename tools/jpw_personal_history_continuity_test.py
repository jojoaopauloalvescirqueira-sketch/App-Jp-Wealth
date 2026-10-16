#!/usr/bin/env python3
"""Compile actual PersonalHistory bodies and run isolated real SQLite proofs.

The optional baseline reproducer uses frozen base product sources. Synthetic
clock/fault primitives live in the host shim; domain algorithms remain MQL.
"""
import argparse
import csv
import hashlib
import json
import platform
import subprocess
import tempfile
import time
from pathlib import Path
import jpw_personal_history_test as h

BASE = '0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874'
BASE_CASES = ['CONT-01', 'CONT-02', 'CONT-03', 'CONT-04', 'CONT-07']
CONT_CASES = [f'CONT-{i:02d}' for i in range(1, 14)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--regression-receipt', type=Path, help='Fresh matching 20 HIS-AC receipt proves CONT-14')
    args = parser.parse_args()
    ids = args.case or (BASE_CASES if args.baseline else CONT_CASES)
    allowed = BASE_CASES if args.baseline else CONT_CASES
    if any(case not in allowed for case in ids) or len(set(ids)) != len(ids):
        parser.error('unknown or repeated continuity case')
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = args.output / 'receipt.json'
    if receipt.exists():
        parser.error('existing evidence preserved; use a new output')
    attempt = Path(tempfile.mkdtemp(prefix='host-', dir=args.output))
    support = h.SUPPORT
    product = [h.CORE, h.STORE, h.EXPORT, h.UI, h.CONTROLLER, h.STORE_RESULT, h.SCRIPT,
               h.PRESENTATION, h.ACTIONS, h.TERMINAL]
    helpers = ['compat.hpp', 'drain.hpp', 'export_drain.hpp', 'store_cases.cpp', 'ui_cases.cpp',
               'controller_cases.cpp', 'ui_seams.cpp', 'controller_seams.cpp', 'continuity_cases.cpp',
               'continuity_process.hpp', 'continuity_baseline_cases.cpp']
    dependencies = product + [support / name for name in helpers] + [Path(__file__), Path(h.__file__)]
    actual = {}

    def source(path):
        value = subprocess.check_output(['git', 'show', BASE + ':' + str(path.relative_to(h.ROOT))],
                                        cwd=h.ROOT, text=True) if args.baseline else path.read_text()
        actual[str(path.relative_to(h.ROOT))] = hashlib.sha256(value.encode()).hexdigest()
        return value

    parts = [(support / 'compat.hpp').read_text(), h.translate(source(h.STORE_RESULT)),
             h.translate(source(h.CORE)), h.translate(source(h.STORE))]
    if not args.baseline:
        parts.append((support / 'drain.hpp').read_text())
    parts.append(h.translate(source(h.EXPORT)))
    if not args.baseline:
        parts.append((support / 'export_drain.hpp').read_text())
    parts.extend([h.translate(source(h.SCRIPT)), (support / 'store_cases.cpp').read_text()])
    if args.baseline:
        parts.append((support / 'continuity_baseline_cases.cpp').read_text())
        entry = 'if(argc!=3)return 2;host_root=argv[1];try{continuity_case(argv[2]);'
    else:
        parts.extend([h.ui_source(), h.controller_source(), (support / 'continuity_process.hpp').read_text(),
                      (support / 'continuity_cases.cpp').read_text()])
        entry = ('if(argc!=3&&argc!=4)return 2;host_root=argv[1];'
                 'host_program=std::filesystem::absolute(argv[0]).string();try{'
                 'if(argc==4)continuity_phase(argv[3]);else continuity_case(argv[2]);')
    parts.append('int main(int argc,char**argv){' + entry +
                 'return 0;}catch(const std::exception&e){std::cerr<<"PRODUCT_FAIL|"<<e.what()<<"\\n";return 1;}}')
    cpp = attempt / 'source.cpp'
    cpp.write_text('\n'.join(parts) + '\n')
    hashes = {str(path.relative_to(h.ROOT)): h.sha(path) for path in dependencies}
    if args.baseline:
        hashes.update(actual)
    binary = attempt / 'test'
    command = ['clang++', '-std=c++17', '-Wall', '-Wextra', '-Wno-unused-parameter',
               '-Wno-deprecated-declarations', str(cpp), '-lsqlite3', '-o', str(binary)]
    if platform.system() != 'Darwin':
        command.append('-lcrypto')
    build = subprocess.run(command, text=True, capture_output=True)
    (attempt / 'compile.log').write_text(build.stdout + build.stderr)
    results = []
    if build.returncode == 0:
        for case in ids:
            directory = attempt / case
            directory.mkdir()
            started = time.monotonic()
            run = subprocess.run([str(binary), str(directory), case], text=True, capture_output=True)
            (directory / 'run.log').write_text(run.stdout + run.stderr)
            failure = None
            if run.returncode == 0 and case == 'CONT-11':
                # Independent CSV parser verifies every exported sequence and
                # payload digest, including embedded CRLF/quotes/UTF8/wide IDs.
                try:
                    marker = next(line for line in run.stdout.splitlines() if line.startswith('CSV_CHECK|'))
                    _, path, wanted = marker.split('|')
                    with (directory / path.replace('\\', '/')).open(newline='', encoding='utf-8') as stream:
                        rows = list(csv.DictReader(stream, delimiter=';'))
                    assert len(rows) == int(wanted) == 100001
                    for sequence, row in enumerate(rows, 1):
                        assert row['sequence'] == str(sequence)
                        assert hashlib.sha256(row['payload'].encode()).hexdigest() == row['sha256']
                    assert any(row['subject_id_text'] == "'9007199254740993" for row in rows)
                except Exception as error:
                    failure = str(error) or 'independent CSV verification failed'
            results.append({'id': case, 'status': 'PASS' if run.returncode == 0 and failure is None else 'PRODUCT_FAIL',
                            'exit': run.returncode, 'seconds': time.monotonic() - started, 'independent_failure': failure})
    if args.regression_receipt and build.returncode == 0:
        original = json.loads(args.regression_receipt.read_text())
        matching = all(original.get('source_sha256', {}).get(str(path.relative_to(h.ROOT))) == h.sha(path) for path in product)
        passed = original.get('classification') == 'PASS' and matching and original.get('sources_unchanged_during_execution') is True
        passed = passed and {case['id'] for case in original.get('cases', [])} == {f'HIS-AC{i:02d}' for i in range(1, 21)}
        results.append({'id': 'CONT-14', 'status': 'PASS' if passed else 'PRODUCT_FAIL',
                        'regression_receipt': str(args.regression_receipt), 'regression_sha256': h.sha(args.regression_receipt)})
    unchanged = all(h.sha(path) == hashes[str(path.relative_to(h.ROOT))] for path in dependencies) if not args.baseline else True
    status = 'TEST_HARNESS_FAIL' if build.returncode else 'PASS' if unchanged and all(case['status'] == 'PASS' for case in results) else 'PRODUCT_FAIL'
    receipt.write_text(json.dumps({'schema': 'jpw-personal-history-continuity-host/v1', 'baseline': args.baseline,
                                  'baseline_product_commit': BASE if args.baseline else None, 'status': status,
                                  'native': 'NOT_RUN', 'sources': hashes, 'compiled_source_sha256': h.sha(cpp),
                                  'sources_unchanged_during_execution': unchanged, 'compile_exit': build.returncode,
                                  'attempt': str(attempt), 'cases': results}, indent=2) + '\n')
    print(receipt)
    print('JPW_TEST_RESULT: ' + status)
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

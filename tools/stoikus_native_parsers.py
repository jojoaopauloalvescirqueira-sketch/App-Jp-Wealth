#!/usr/bin/env python3
"""Verdicts for the 24 Stoikus MQL5 test scripts from native Experts-log excerpts.

The scripts only report through Print, each with its own summary format, so
each one has an explicit specification here. A verdict never becomes PASS
without exactly one recognised summary reporting zero failures:

- summary with failures, a FAIL status word or an individual failure line -> PRODUCT_FAIL
- a native runtime error (array out of range, zero divide, ...)           -> PRODUCT_FAIL
- the script's own NOT_RUN line and no summary                             -> NOT_RUN
- no summary at all                                                        -> ENVIRONMENT_ERROR
- several summaries, or a summary counting zero asserts                    -> TEST_HARNESS_FAIL

`anchors` are literal fragments of the script's Print calls; the host test
checks they still exist, so a changed summary format fails on the Mac first.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / 'mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth'

RUNTIME_ERROR = re.compile(r'critical runtime error|array out of range|zero divide|'
                           r'invalid pointer access|stack overflow|not enough memory')
LOG_PREFIX = re.compile(r'^[A-Z]{2}$')
GENERIC_FAIL = r'^FAIL: '


@dataclass(frozen=True)
class Spec:
    summaries: tuple[str, ...]
    anchors: tuple[str, ...]
    fail_line: str = GENERIC_FAIL
    not_run: str | None = None
    patterns: tuple[re.Pattern[str], ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'patterns', tuple(re.compile(pattern) for pattern in self.summaries))


def asserts_summary(name: str) -> Spec:
    """`<name> PASS: %d asserts` or `<name> FAIL: %d of %d asserts`."""
    return Spec(summaries=(rf'^{name} (?P<status>PASS): (?P<passes>\d+) asserts$',
                           rf'^{name} (?P<status>FAIL): (?P<failures>\d+) of (?P<total>\d+) asserts$'),
                anchors=(f'{name} PASS: %d asserts', f'{name} FAIL: %d of %d asserts'))


SPECS: dict[str, Spec] = {
    'JPW_Alavancagem_Tests': asserts_summary('JPW_Alavancagem_Tests'),
    'JPW_Alavancagem_Genesis_Tests': asserts_summary('JPW_Alavancagem_Genesis_Tests'),
    'JPW_Alavancagem_RaizN_Tests': asserts_summary('JPW_Alavancagem_RaizN_Tests'),
    'JPW_Alavancagem_RaizN_Config_Tests': Spec(
        summaries=asserts_summary('JPW_Alavancagem_RaizN_Config_Tests').summaries,
        anchors=asserts_summary('JPW_Alavancagem_RaizN_Config_Tests').anchors
        + ('JPW RaizN config tests NOT_RUN: synthetic folder unavailable',),
        not_run=r'^JPW RaizN config tests NOT_RUN: '),
    'JPW_Alavancagem_RaizN_Store_Tests': Spec(
        summaries=asserts_summary('JPW_Alavancagem_RaizN_Store_Tests').summaries,
        anchors=asserts_summary('JPW_Alavancagem_RaizN_Store_Tests').anchors
        + ('JPW RaizN store tests NOT_RUN: synthetic folder unavailable',),
        not_run=r'^JPW RaizN store tests NOT_RUN: '),
    'JPW_Alavancagem_RaizN_Factor_Tests': Spec(
        summaries=(r'^JPW RaizN factor (?P<status>PASS): (?P<passes>\d+) asserts$',
                   r'^JPW RaizN factor (?P<status>PRODUCT_FAIL): (?P<failures>\d+)/(?P<total>\d+) failed$'),
        anchors=('JPW RaizN factor PASS: %d asserts', 'JPW RaizN factor PRODUCT_FAIL: %d/%d failed',
                 'JPW factor tests NOT_RUN: synthetic folder unavailable'),
        not_run=r'^JPW factor tests NOT_RUN: '),
    'JPW_Alavancagem_Genesis_Store_Tests': Spec(
        summaries=(r'^JPW Genesis store synthetic tests: (?P<passes>\d+) PASS / (?P<failures>\d+) FAIL$',),
        anchors=('JPW Genesis store synthetic tests: ', ' PASS / ', ' FAIL',
                 'GENESIS STORE TESTS NOT_RUN: synthetic folder unavailable'),
        not_run=r'^GENESIS STORE TESTS NOT_RUN: '),
    'JPW_Alavancagem_Metrics_Tests': Spec(
        summaries=(r'^JPW Metrics synthetic tests: (?P<passes>\d+) PASS / (?P<failures>\d+) FAIL$',),
        anchors=('JPW Metrics synthetic tests: ', ' PASS / ', ' FAIL',
                 'METRICS TESTS NOT_RUN: synthetic folder unavailable'),
        not_run=r'^METRICS TESTS NOT_RUN: '),
    'JPW_Alavancagem_Diagnostics_Tests': Spec(
        summaries=(r'^JPW_Alavancagem_Diagnostics_Tests (?P<status>PASS|FAIL): (?P<passes>\d+) passed; '
                   r'(?P<failures>\d+) failed; synthetic folder: ',),
        anchors=('JPW_Alavancagem_Diagnostics_Tests ', ' passed; ', ' failed; synthetic folder: '),
        fail_line=r'^DIAGNOSTICS FAIL: '),
    'JPW_Alavancagem_Observer_Tests': Spec(
        summaries=(r'^JPW_Alavancagem_Observer_Tests (?P<status>PASS|FAIL): (?P<passes>\d+) PASS / (?P<failures>\d+) FAIL$',),
        anchors=('JPW_Alavancagem_Observer_Tests %s: %d PASS / %d FAIL',)),
    'JPW_Alavancagem_Panel_Tests': Spec(
        summaries=(r'^JPW_Alavancagem_Panel_Tests (?P<status>PASS|FAIL): (?P<total>\d+) asserts; (?P<failures>\d+) failures$',),
        anchors=('JPW_Alavancagem_Panel_Tests ', 'PASS: ', ' asserts; ', ' failures')),
    'JPW_Alavancagem_Positions_Tests': Spec(
        summaries=(r'^JPW Positions: (?P<passes>\d+) PASS / (?P<failures>\d+) FAIL$',),
        anchors=('JPW Positions: ', ' PASS / ', ' FAIL')),
    'JPW_Alavancagem_Profile_Tests': Spec(
        summaries=(r'^JPW Alavancagem Profile Tests: (?P<total>\d+) verificacoes, (?P<failures>\d+) falhas\. (?P<status>PASS|FAIL)$',),
        anchors=('JPW Alavancagem Profile Tests: ', ' verificacoes, ', ' falhas. '),
        fail_line=r'^JPW perfil teste falhou: '),
    'JPW_Alavancagem_RaizN_Horizon_Tests': Spec(
        summaries=(r'^JPW_Alavancagem_RaizN_Horizon_Tests (?P<status>PASS|FAIL): (?P<total>\d+) asserts$',),
        anchors=('JPW_Alavancagem_RaizN_Horizon_Tests %s: %d asserts',)),
    'JPW_Alavancagem_RaizN_Live_Tests': Spec(
        summaries=(r'^JPW_Alavancagem_RaizN_Live_Tests (?P<status>PASS): (?P<passes>\d+) asserts$',
                   r'^JPW_Alavancagem_RaizN_Live_Tests (?P<status>FAIL): (?P<failures>\d+) failures / (?P<passes>\d+) passes$'),
        anchors=('JPW_Alavancagem_RaizN_Live_Tests PASS: ', 'JPW_Alavancagem_RaizN_Live_Tests FAIL: ', ' failures / ', ' passes')),
    'JPW_Alavancagem_StopRisk_Tests': Spec(
        summaries=(r'^JPW_Alavancagem_StopRisk_Tests (?P<status>PASS|FAIL): (?P<total>\d+) asserts, (?P<failures>\d+) failures$',),
        anchors=('JPW_Alavancagem_StopRisk_Tests ', ' asserts, ', ' failures')),
    'JPW_NoCuda_Core_Tests': Spec(
        summaries=(r'^JPW_NoCuda_Core_Tests: (?P<status>PASS|FAIL) \((?P<passes>\d+) asserts, (?P<failures>\d+) failures\)$',),
        anchors=('JPW_NoCuda_Core_Tests: ', ' asserts, ', ' failures)')),
    'JPW_NoCuda_Fibo_Tests': Spec(
        summaries=(r'^JPW NoCuda Fibo core: (?P<total>\d+) asserts; failures=(?P<failures>\d+)\.',),
        anchors=('JPW NoCuda Fibo core: ', ' asserts; failures=')),
    'JPW_NoCuda_Projection_Tests': Spec(
        summaries=(r'^JPW_NoCuda_Projection_Tests: (?P<passes>\d+) PASS / (?P<failures>\d+) FAIL$',),
        anchors=('JPW_NoCuda_Projection_Tests: ', ' PASS / ', ' FAIL')),
    'JPW_NoCuda_Store_Tests': Spec(
        summaries=(r'^JPW_NoCuda_Store_Tests (?P<status>PASS|FAIL): (?P<total>\d+) asserts, (?P<failures>\d+) failures$',),
        anchors=('JPW_NoCuda_Store_Tests %s: %d asserts, %d failures',),
        fail_line=r'^FAIL NoCuda store: '),
    'JPW_PersonalHistory_Tests': Spec(
        summaries=(r'^PERSONAL_SYNTHETIC_RESULT\|(?P<failures>\d+)\|',),
        anchors=('PERSONAL_SYNTHETIC_RESULT|',),
        fail_line=r'^PERSONAL_TEST_FAIL\|'),
    'JPW_SignalCopy_Tests': Spec(
        summaries=(r'^JPW_SIGNAL_COPY: (?P<passes>\d+) PASS / (?P<failures>\d+) FAIL$',),
        anchors=('JPW_SIGNAL_COPY: ', ' PASS / ', ' FAIL')),
    'JPW_Stoikus_Ledger_Tests': Spec(
        summaries=(r'^LEDGER_SYNTHETIC_RESULT failures=(?P<failures>\d+);',),
        anchors=('LEDGER_SYNTHETIC_RESULT failures=',),
        fail_line=r'^LEDGER_TEST_FAIL '),
    'JPW_Stoikus_Risk_Tests': Spec(
        summaries=(r'^HOST/PURE_RESULTS (?P<passes>\d+) PASS / (?P<failures>\d+) FAIL;',),
        anchors=('HOST/PURE_RESULTS ', ' PASS / ', ' FAIL; '),
        fail_line=r'^PRODUCT_FAIL '),
}


def script_messages(script: str, text: str) -> list[str]:
    """Messages of this script; Experts-log lines of other programs are dropped."""
    messages = []
    for raw in text.splitlines():
        line = raw.rstrip('\r')
        parts = line.split('\t')
        if len(parts) >= 5 and LOG_PREFIX.match(parts[0]):
            if parts[3].split(' (')[0] != script:
                continue
            line = '\t'.join(parts[4:])
        if line.strip():
            messages.append(line)
    return messages


def number(groups: dict[str, str | None], key: str) -> int | None:
    value = groups.get(key)
    return int(value) if value is not None else None


def classify_excerpt(script: str, text: str) -> dict[str, object]:
    verdict: dict[str, object] = {'script': script, 'result': 'TEST_HARNESS_FAIL', 'reason': '',
                                  'summary_line': None, 'passes': None, 'failures': None, 'total': None,
                                  'fail_lines': [], 'runtime_errors': [], 'not_run_line': None}
    spec = SPECS.get(script)
    if spec is None:
        verdict['reason'] = 'no parser specification for this script'
        return verdict
    messages = script_messages(script, text)
    matches = [(message, match) for message in messages for pattern in spec.patterns
               if (match := pattern.match(message))]
    summary_lines = {message for message, _ in matches}
    verdict['runtime_errors'] = [message for message in messages if RUNTIME_ERROR.search(message)]
    verdict['fail_lines'] = [message for message in messages
                             if re.match(spec.fail_line, message) and message not in summary_lines]
    not_run = [message for message in messages if spec.not_run and re.match(spec.not_run, message)]

    def done(result: str, reason: str) -> dict[str, object]:
        verdict.update(result=result, reason=reason)
        return verdict

    if len(matches) > 1:
        return done('TEST_HARNESS_FAIL', f'{len(matches)} summary lines; verdict is ambiguous')
    if not matches:
        if verdict['runtime_errors']:
            return done('PRODUCT_FAIL', 'native runtime error before any summary')
        if not_run:
            verdict['not_run_line'] = not_run[0]
            return done('NOT_RUN', 'the script declared NOT_RUN')
        return done('ENVIRONMENT_ERROR', 'no recognised summary line; the run is incomplete')

    message, match = matches[0]
    groups = match.groupdict()
    status = groups.get('status')
    passes, failures, total = number(groups, 'passes'), number(groups, 'failures'), number(groups, 'total')
    if failures is None and status == 'PASS':
        failures = 0
    elif failures is None and verdict['fail_lines']:
        failures = len(verdict['fail_lines'])
    if total is None and passes is not None and failures is not None:
        total = passes + failures
    if passes is None and total is not None and failures is not None:
        passes = total - failures
    verdict.update(summary_line=message, passes=passes, failures=failures, total=total)

    if verdict['runtime_errors']:
        return done('PRODUCT_FAIL', 'native runtime error')
    if status in ('FAIL', 'PRODUCT_FAIL') and failures == 0:
        return done('PRODUCT_FAIL', 'status word reports failure while the count is zero')
    if status == 'PASS' and failures:
        return done('PRODUCT_FAIL', 'status word reports PASS while failures were counted')
    if status in ('FAIL', 'PRODUCT_FAIL') or failures:
        return done('PRODUCT_FAIL', 'the script reported failures')
    if verdict['fail_lines']:
        return done('PRODUCT_FAIL', 'individual failure lines contradict the passing summary')
    if total == 0:
        return done('TEST_HARNESS_FAIL', 'summary counts zero asserts')
    return done('PASS', 'one summary with zero failures')

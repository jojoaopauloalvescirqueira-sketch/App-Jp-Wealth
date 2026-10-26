#!/usr/bin/env python3
"""Host controls for the native MQL5 test-script parsers; no MT5 is executed.

Example lines mirror the Print/PrintFormat calls of each *_Tests.mq5. The
anchor test keeps the table bound to the current sources: a changed summary
format must fail here instead of silently becoming ENVIRONMENT_ERROR natively.
"""
from __future__ import annotations

import unittest

from stoikus_native_parsers import SCRIPTS_DIR, SPECS, classify_excerpt

# script -> (passing summary, failing summary, own NOT_RUN line or None)
EXAMPLES = {
    'JPW_Alavancagem_Tests': ('JPW_Alavancagem_Tests PASS: 120 asserts', 'JPW_Alavancagem_Tests FAIL: 2 of 120 asserts', None),
    'JPW_Alavancagem_Diagnostics_Tests': ('JPW_Alavancagem_Diagnostics_Tests PASS: 14 passed; 0 failed; synthetic folder: JPWealth\\Synthetic\\test_1',
                                          'JPW_Alavancagem_Diagnostics_Tests FAIL: 13 passed; 1 failed; synthetic folder: JPWealth\\Synthetic\\test_1', None),
    'JPW_Alavancagem_Genesis_Store_Tests': ('JPW Genesis store synthetic tests: 40 PASS / 0 FAIL', 'JPW Genesis store synthetic tests: 39 PASS / 1 FAIL',
                                            'GENESIS STORE TESTS NOT_RUN: synthetic folder unavailable'),
    'JPW_Alavancagem_Genesis_Tests': ('JPW_Alavancagem_Genesis_Tests PASS: 31 asserts', 'JPW_Alavancagem_Genesis_Tests FAIL: 1 of 31 asserts', None),
    'JPW_Alavancagem_Metrics_Tests': ('JPW Metrics synthetic tests: 55 PASS / 0 FAIL', 'JPW Metrics synthetic tests: 54 PASS / 1 FAIL',
                                      'METRICS TESTS NOT_RUN: synthetic folder unavailable'),
    'JPW_Alavancagem_Observer_Tests': ('JPW_Alavancagem_Observer_Tests PASS: 22 PASS / 0 FAIL', 'JPW_Alavancagem_Observer_Tests FAIL: 21 PASS / 1 FAIL', None),
    'JPW_Alavancagem_Panel_Tests': ('JPW_Alavancagem_Panel_Tests PASS: 96 asserts; 0 failures', 'JPW_Alavancagem_Panel_Tests FAIL: 96 asserts; 3 failures', None),
    'JPW_Alavancagem_Positions_Tests': ('JPW Positions: 18 PASS / 0 FAIL', 'JPW Positions: 17 PASS / 1 FAIL', None),
    'JPW_Alavancagem_Profile_Tests': ('JPW Alavancagem Profile Tests: 25 verificacoes, 0 falhas. PASS', 'JPW Alavancagem Profile Tests: 25 verificacoes, 2 falhas. FAIL', None),
    'JPW_Alavancagem_RaizN_Config_Tests': ('JPW_Alavancagem_RaizN_Config_Tests PASS: 44 asserts', 'JPW_Alavancagem_RaizN_Config_Tests FAIL: 1 of 44 asserts',
                                           'JPW RaizN config tests NOT_RUN: synthetic folder unavailable'),
    'JPW_Alavancagem_RaizN_Factor_Tests': ('JPW RaizN factor PASS: 30 asserts', 'JPW RaizN factor PRODUCT_FAIL: 2/30 failed',
                                           'JPW factor tests NOT_RUN: synthetic folder unavailable'),
    'JPW_Alavancagem_RaizN_Horizon_Tests': ('JPW_Alavancagem_RaizN_Horizon_Tests PASS: 27 asserts', 'JPW_Alavancagem_RaizN_Horizon_Tests FAIL: 27 asserts', None),
    'JPW_Alavancagem_RaizN_Live_Tests': ('JPW_Alavancagem_RaizN_Live_Tests PASS: 33 asserts', 'JPW_Alavancagem_RaizN_Live_Tests FAIL: 1 failures / 32 passes', None),
    'JPW_Alavancagem_RaizN_Store_Tests': ('JPW_Alavancagem_RaizN_Store_Tests PASS: 61 asserts', 'JPW_Alavancagem_RaizN_Store_Tests FAIL: 1 of 61 asserts',
                                          'JPW RaizN store tests NOT_RUN: synthetic folder unavailable'),
    'JPW_Alavancagem_RaizN_Tests': ('JPW_Alavancagem_RaizN_Tests PASS: 19 asserts', 'JPW_Alavancagem_RaizN_Tests FAIL: 1 of 19 asserts', None),
    'JPW_Alavancagem_StopRisk_Tests': ('JPW_Alavancagem_StopRisk_Tests PASS: 48 asserts, 0 failures', 'JPW_Alavancagem_StopRisk_Tests FAIL: 48 asserts, 1 failures', None),
    'JPW_NoCuda_Core_Tests': ('JPW_NoCuda_Core_Tests: PASS (70 asserts, 0 failures)', 'JPW_NoCuda_Core_Tests: FAIL (69 asserts, 1 failures)', None),
    'JPW_NoCuda_Fibo_Tests': ('JPW NoCuda Fibo core: 40 asserts; failures=0. NATIVE PARITY NOT TESTED; measurements remain UNVERIFIED_NATIVE.',
                              'JPW NoCuda Fibo core: 40 asserts; failures=2. NATIVE PARITY NOT TESTED; measurements remain UNVERIFIED_NATIVE.', None),
    'JPW_NoCuda_Projection_Tests': ('JPW_NoCuda_Projection_Tests: 35 PASS / 0 FAIL', 'JPW_NoCuda_Projection_Tests: 34 PASS / 1 FAIL', None),
    'JPW_NoCuda_Store_Tests': ('JPW_NoCuda_Store_Tests PASS: 52 asserts, 0 failures', 'JPW_NoCuda_Store_Tests FAIL: 52 asserts, 1 failures', None),
    'JPW_PersonalHistory_Tests': ('PERSONAL_SYNTHETIC_RESULT|0|native terminal and notifications not exercised',
                                  'PERSONAL_SYNTHETIC_RESULT|2|native terminal and notifications not exercised', None),
    'JPW_SignalCopy_Tests': ('JPW_SIGNAL_COPY: 60 PASS / 0 FAIL', 'JPW_SIGNAL_COPY: 59 PASS / 1 FAIL', None),
    'JPW_Stoikus_Ledger_Tests': ('LEDGER_SYNTHETIC_RESULT failures=0; native terminal/account integration not exercised',
                                 'LEDGER_SYNTHETIC_RESULT failures=1; native terminal/account integration not exercised', None),
    'JPW_Stoikus_Risk_Tests': ('HOST/PURE_RESULTS 26 PASS / 0 FAIL; native compile/runtime NOT_RUN unless separately executed',
                               'HOST/PURE_RESULTS 25 PASS / 1 FAIL; native compile/runtime NOT_RUN unless separately executed', None),
}


# Their FAIL summary carries only the status word, never a failure count.
UNCOUNTED_FAILURES = {'JPW_Alavancagem_RaizN_Horizon_Tests'}


def mt5_line(script: str, message: str) -> str:
    """One Experts-log line as the terminal writes it (prefix columns, tab separated)."""
    return f'KQ\t0\t21:04:51.217\t{script} (EURUSD,H1)\t{message}'


class ParserTableTests(unittest.TestCase):
    def test_table_covers_exactly_the_test_scripts_in_the_tree(self):
        on_disk = {path.stem for path in SCRIPTS_DIR.glob('*_Tests.mq5')}
        self.assertEqual(len(on_disk), 24)
        self.assertEqual(set(SPECS), on_disk)
        self.assertEqual(set(EXAMPLES), on_disk)

    def test_every_anchor_still_exists_in_its_source(self):
        for script, spec in SPECS.items():
            source = (SCRIPTS_DIR / f'{script}.mq5').read_text(encoding='utf-8', errors='replace')
            for anchor in spec.anchors:
                with self.subTest(script=script, anchor=anchor):
                    self.assertIn(anchor, source)


class ClassificationTests(unittest.TestCase):
    def check(self, script: str, lines: list[str], expected: str) -> dict:
        verdict = classify_excerpt(script, '\n'.join(mt5_line(script, line) for line in lines))
        self.assertEqual(verdict['result'], expected, (script, lines, verdict))
        return verdict

    def test_passing_summary_is_pass_with_counts(self):
        for script, (passing, _, _) in EXAMPLES.items():
            with self.subTest(script=script):
                verdict = self.check(script, ['starting', passing], 'PASS')
                self.assertEqual(verdict['failures'], 0)
                self.assertEqual(verdict['summary_line'], passing)

    def test_failing_summary_is_product_fail(self):
        for script, (_, failing, _) in EXAMPLES.items():
            with self.subTest(script=script):
                verdict = self.check(script, [failing], 'PRODUCT_FAIL')
                if script in UNCOUNTED_FAILURES:
                    self.assertIsNone(verdict['failures'])
                else:
                    self.assertGreater(verdict['failures'], 0)

    def test_missing_summary_is_environment_error_never_pass(self):
        for script in EXAMPLES:
            with self.subTest(script=script):
                self.check(script, [], 'ENVIRONMENT_ERROR')
                self.check(script, ['script JPWealth\\x loaded successfully', 'unrelated output'], 'ENVIRONMENT_ERROR')

    def test_own_not_run_line_is_not_run(self):
        for script, (_, _, not_run) in EXAMPLES.items():
            if not_run is None:
                continue
            with self.subTest(script=script):
                self.check(script, [not_run], 'NOT_RUN')

    def test_duplicate_summary_is_ambiguous(self):
        for script, (passing, failing, _) in EXAMPLES.items():
            with self.subTest(script=script):
                self.check(script, [passing, passing], 'TEST_HARNESS_FAIL')
                self.check(script, [passing, failing], 'TEST_HARNESS_FAIL')

    def test_native_runtime_error_overrides_a_passing_summary(self):
        script, (passing, _, _) = 'JPW_Alavancagem_Tests', EXAMPLES['JPW_Alavancagem_Tests']
        for error in ('array out of range in \'JPW_Alavancagem_Core.mqh\' (120,15)', 'zero divide in \'x.mqh\' (1,1)',
                      'critical runtime error 503 in OnStart function'):
            with self.subTest(error=error):
                verdict = self.check(script, [error, passing], 'PRODUCT_FAIL')
                self.assertEqual(verdict['runtime_errors'], [error])

    def test_individual_failure_line_contradicting_a_passing_summary_is_product_fail(self):
        cases = {
            'JPW_Alavancagem_Tests': 'FAIL: leverage gross notional',
            'JPW_Alavancagem_Diagnostics_Tests': 'DIAGNOSTICS FAIL: corruption refused',
            'JPW_NoCuda_Store_Tests': 'FAIL NoCuda store: busy DB initialized',
            'JPW_Alavancagem_Profile_Tests': 'JPW perfil teste falhou: hash da fixture local',
            'JPW_PersonalHistory_Tests': 'PERSONAL_TEST_FAIL|record order',
            'JPW_Stoikus_Ledger_Tests': 'LEDGER_TEST_FAIL cycle close',
            'JPW_Stoikus_Risk_Tests': 'PRODUCT_FAIL RIS-01 scope',
        }
        for script, fail_line in cases.items():
            with self.subTest(script=script):
                verdict = self.check(script, [fail_line, EXAMPLES[script][0]], 'PRODUCT_FAIL')
                self.assertEqual(verdict['fail_lines'], [fail_line])

    def test_failing_summary_lines_are_not_double_counted_as_failure_lines(self):
        verdict = self.check('JPW_Alavancagem_Genesis_Tests', [EXAMPLES['JPW_Alavancagem_Genesis_Tests'][1]], 'PRODUCT_FAIL')
        self.assertEqual(verdict['fail_lines'], [])

    def test_zero_asserts_cannot_pass(self):
        self.check('JPW_Alavancagem_Tests', ['JPW_Alavancagem_Tests PASS: 0 asserts'], 'TEST_HARNESS_FAIL')
        self.check('JPW_SignalCopy_Tests', ['JPW_SIGNAL_COPY: 0 PASS / 0 FAIL'], 'TEST_HARNESS_FAIL')

    def test_status_word_contradicting_counts_is_product_fail(self):
        self.check('JPW_Alavancagem_StopRisk_Tests', ['JPW_Alavancagem_StopRisk_Tests FAIL: 48 asserts, 0 failures'], 'PRODUCT_FAIL')
        self.check('JPW_Alavancagem_StopRisk_Tests', ['JPW_Alavancagem_StopRisk_Tests PASS: 48 asserts, 2 failures'], 'PRODUCT_FAIL')

    def test_lines_of_another_script_are_ignored(self):
        other = mt5_line('JPW_Alavancagem_Genesis_Tests', EXAMPLES['JPW_Alavancagem_Tests'][0])
        verdict = classify_excerpt('JPW_Alavancagem_Tests', other)
        self.assertEqual(verdict['result'], 'ENVIRONMENT_ERROR')

    def test_unknown_script_is_harness_failure(self):
        self.assertEqual(classify_excerpt('JPW_Unknown_Tests', '')['result'], 'TEST_HARNESS_FAIL')


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__)))
    raise SystemExit(0 if result.wasSuccessful() else 1)

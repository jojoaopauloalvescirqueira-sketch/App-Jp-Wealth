#!/usr/bin/env python3
"""D1: literal UI oracles fixed before the comparison renderer changes.

Synthetic full-app browser test. Missing baseline feature is reported separately
from a financial defect. This focal does not certify other browsers or human UX.
"""
import argparse
import ast
import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'src/js/20-ui/20-finpes-comparison.js'


def fixture_literal(file, name):
    tree = ast.parse((ROOT / file).read_text())
    return next(ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def seed(page):
    template = fixture_literal('tools/finpes_comparison_test.py', 'SEED_MES_COMPLETO')
    script = ''.join(template.replace('{K}', month).replace('{REC}', str(inc)).replace('{EXE}', str(exp))
                     for month, inc, exp in [('2026-02', 100000, 0), ('2026-03', 100000, 300000),
                         ('2026-05', 500000, 200000), ('2026-07', 500000, 500000),
                         ('2026-08', 200000, 100000), ('2026-09', 600000, 400000)])
    page.evaluate('() => {' + script + '''
      pfActAddExpense('2026-04', {name:'Despesa parcial'});
      const april=S.personalFinance.months['2026-04'];
      pfActUpdateExpenseField('2026-04', april.expenses[0].id, 'executedCash', 12345);
      window.__onbShown=true; closeModal();
      localStorage.setItem('d1-preserve-preference','synthetic-kept');
      JPWNavigation.navigateLocal('finpes','comparativo'); fcGoTo('2026-09');
    }''')


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    result = {'source_sha256': hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(),
              'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'css_sha256': hashlib.sha256((ROOT / 'src/styles/app.css').read_bytes()).hexdigest(),
              'index_sha256': hashlib.sha256((ROOT / 'index.html').read_bytes()).hexdigest(),
              'baseline_scope': 'JS feature presence; visual baseline is survey-baseline-02, not this receipt.',
              'coverage_limits': [{'verification': 'Native select popup option selection via keyboard',
                  'status': 'NOT_RUN', 'reason': 'Playwright key sequences did not select an option in independent plain HTML probes, both headed and headless macOS Chromium. See d1-native-probe-01.json and d1-native-probe-headed-01.json. Native change events, Tab traversal, and keyboard button activation are tested separately.'}],
              'checks': []}
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()

    def check(name, condition, detail=None):
        assert condition, (name, detail)
        result['checks'].append({'name': name, 'status': 'PASS', 'detail': detail})
        print('PASS ' + name, flush=True)

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=os.environ['JP_WEALTH_CHROMIUM'])
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block', has_touch=True)
            install_bootstrap(context)
            context.add_init_script('window.__onbShown=true;')
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='load')
            wait_bootstrap(page)
            seed(page)
            check('original twelve-month table', page.locator('#fcSeries .fc-srow:not(.fc-head)').count() == 12)
            if args.baseline:
                check('baseline feature absent; not a financial defect', page.locator('#fcMetric').count() == 0)
                page.screenshot(path=str(output / 'baseline.png'), full_page=True)
                result['status'] = 'BASELINE_FAIL'
                result['reason'] = 'Approved D1 visualization and native exploration controls absent.'
                return

            check('metric default and native month selector', page.locator('#fcMetric').input_value() == 'despesa'
                  and page.locator('#fcMonthSelect option').count() == 12)
            check('semantic table preserved', page.locator('#fcSeries table tbody tr').count() == 12
                  and page.locator('#fcSeries thead th').count() == 6)
            points = page.locator('#fcChart [data-fc-point]').evaluate_all('(nodes)=>nodes.map(n=>[n.dataset.fcPoint,Number(n.dataset.value)])')
            check('complete facts including zero; gaps never points', points == [
                ['2026-02', 0], ['2026-03', 300000], ['2026-05', 200000],
                ['2026-07', 500000], ['2026-08', 100000], ['2026-09', 400000]], points)
            check('line breaks across absent and partial months', page.locator('#fcChart [data-fc-line]').get_attribute('d').count('M') == 3)
            page.evaluate('''() => {
              window.__d1Before={s:JSON.stringify(S),ls:JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))};
              window.__d1Saves=0; const originalSave=save; save=(...a)=>{__d1Saves++;return originalSave(...a);};
              window.__d1Series=0; const originalSeries=pfCompSeries;
              pfCompSeries=(...a)=>{__d1Series++;return originalSeries(...a);};
            }''')
            page.locator('#fcMetric').focus()
            page.locator('#fcMetric').select_option('sobra')
            check('metric focus and one canonical series read', page.evaluate("document.activeElement.id==='fcMetric' && __d1Series===1"))
            page.locator('#fcMonthSelect').focus()
            page.locator('#fcMonthSelect').select_option('2026-03')
            check('negative surplus remains a fact', '-R$ 2.000,00' in page.locator('#fcChartReadout').inner_text()
                  and page.locator('#fcChart [data-fc-point="2026-03"]').get_attribute('data-value') == '-200000',
                  page.locator('#fcChartReadout').inner_text())
            check('month focus survives render', page.evaluate("document.activeElement.id==='fcMonthSelect'"))
            page.locator('#fcMonthSelect').select_option('2026-04')
            check('partial month has explicit visible reason', 'parcial' in page.locator('#fcChartReadout').inner_text().lower()
                  and page.locator('#fcChart [data-fc-point="2026-04"]').count() == 0)
            page.locator('#fcMetric').select_option('comprometimento')
            page.locator('#fcMonthSelect').select_option('2026-03')
            check('ratio unit is percent', '300%' in page.locator('#fcChartReadout').inner_text())
            page.locator('#fcMonthSelect').select_option('2026-06')
            check('virtual month explained', 'não registrado' in page.locator('#fcChartReadout').inner_text().lower())
            page.locator('#fcMetric').select_option('divida')
            check('debt zero follows its own metric coverage', page.locator('#fcChart [data-fc-point="2026-04"]').get_attribute('data-value') == '0'
                  and page.locator('#fcChart [data-fc-point]').count() == 7)
            page.locator('#fcMetric').select_option('receita')
            check('income metric reads canonical amounts', page.locator('#fcChart [data-fc-point="2026-02"]').get_attribute('data-value') == '100000'
                  and page.locator('#fcChart [data-fc-point="2026-06"]').count() == 0)
            page.locator('#fcMetric').focus()
            page.keyboard.press('Tab')
            check('native keyboard traversal reaches month selector', page.evaluate("document.activeElement.id==='fcMonthSelect'"))
            page.locator('[data-fc-nav="-1"]').focus()
            page.keyboard.press('Enter')
            check('previous window button keeps focus', page.evaluate("document.activeElement.dataset.fcNav==='-1'"))
            page.locator('[data-fc-nav="1"]').tap()
            page.locator('#fcMetric').select_option('despesa')
            check('native touch navigation returns window', page.locator('#fcMonthSelect option').last.get_attribute('value') == '2026-09')
            check('interaction has zero state/storage/save writes', page.evaluate('''() => __d1Saves===0 && __d1Before.s===JSON.stringify(S) &&
              __d1Before.ls===JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))'''))

            page.evaluate("JPWNavigation.navigateLocal('finpes','mensal'); fbGoTo('2026-09');")
            field = page.locator('[data-fe-campo="executedCash"]').first
            field.fill('4.321,00')
            field.press('Tab')
            page.evaluate("JPWNavigation.navigateLocal('finpes','comparativo');")
            check('budget edit refreshes graph without cache', page.locator('#fcChart [data-fc-point="2026-09"]').get_attribute('data-value') == '432100')
            pf_before = page.evaluate('JSON.stringify(S.personalFinance)')
            state_saved = page.evaluate("localStorage.getItem('jpwealth_v9_state')")
            page.reload(wait_until='load')
            wait_bootstrap(page)
            page.evaluate("closeModal(); JPWNavigation.navigateLocal('finpes','comparativo'); fcGoTo('2026-09');")
            check('reload preserves saved personal finance and preference', page.evaluate('JSON.stringify(S.personalFinance)') == pf_before
                  and page.evaluate("localStorage.getItem('d1-preserve-preference')") == 'synthetic-kept'
                  and json.loads(page.evaluate("localStorage.getItem('jpwealth_v9_state')"))['personalFinance'] == json.loads(state_saved)['personalFinance'])

            for width in [320, 390, 768, 1440]:
                page.set_viewport_size({'width': width, 'height': 1000})
                check(f'controls and table scroll region at {width}', page.locator('#fcMetric').is_visible()
                      and page.locator('#fcMonthSelect').is_visible()
                      and page.locator('#fcSeries .fc-table-scroll').get_attribute('tabindex') == '0')
                page.screenshot(path=str(output / f'comparison-{width}.png'), full_page=True)
            page.evaluate('''() => {
              const original=pfCompSeries;
              pfCompSeries=(...args)=>original(...args).map(m=>({...m,despesa:{status:'FUTURE_STATUS',value:999999999}}));
              window.JPWFinComparison.render();
            }''')
            check('unknown metric status fails closed', page.locator('#fcChart [data-fc-point]').count() == 0
                  and '9.999.999' not in page.locator('#fcChartReadout').inner_text())
            page.evaluate("S.personalFinance.moneyUnit='UNKNOWN_UNIT'; window.JPWFinComparison.render();")
            check('unsupported money unit refuses all chart numbers', page.locator('#fcChart').count() == 0
                  and 'R$' not in page.locator('#finpesComparisonRoot').inner_text()
                  and 'não reconhecida' in page.locator('#finpesComparisonRoot').inner_text())
            check('no uncaught browser errors', not errors, errors)
            assert_fixture_requests(context)
            check('no unexpected network resources', True)
            result['status'] = 'PASS'
            context.close()
            browser.close()
    except Exception as error:
        result['status'] = 'PRODUCT_FAIL' if isinstance(error, AssertionError) else 'TEST_HARNESS_FAIL'
        result['error'] = str(error)
        raise
    finally:
        (output / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        server.shutdown()
        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    run()

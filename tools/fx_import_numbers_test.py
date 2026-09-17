#!/usr/bin/env python3
"""Deterministic HTML import regressions; synthetic data, no app storage/network.

The optional --model argument can run the same oracles against a saved baseline.
No application sources or user profiles are modified.
"""
import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright
import notes_launcher_test as launcher

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'src/js/10-domain/17-fx-consolidated-model.js'
FIXTURES = ROOT / 'tools/fixtures/mt5-consolidated'


def fixture(*, volume='1', price='1', profit='120', time='2026.01.02 10:00:00', extra=''):
    return f'''<!doctype html><html lang="pt"><body><table>
    <tr><td>Account:</td><td>999001</td></tr><tr><td>Currency:</td><td>USD</td></tr>
    {extra}<tr><th>Deals</th></tr>
    <tr><th>Time</th><th>Deal</th><th>Type</th><th>Volume</th><th>Price</th><th>Commission</th><th>Fee</th><th>Swap</th><th>Profit</th></tr>
    <tr><td>{time}</td><td>123456789012345678</td><td>buy</td><td>{volume}</td><td>{price}</td><td>0</td><td>0</td><td>0</td><td>{profit}</td></tr>
    </table></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=Path, default=MODEL)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(**launcher.launch_options())
        context = browser.new_context(service_workers='block')
        requests, errors = [], []
        context.route('**/*', lambda route: (requests.append(route.request.url), route.abort()))
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content('<!doctype html><title>Synthetic number parsing</title>')
        page.add_script_tag(content=args.model.read_text())

        def parse(html, **options):
            return page.evaluate('a=>{const r=JPWFXConsolidated.parseHTML(a.html,a.options);return {report:r,errors:JPWFXConsolidated.validateReport(r)}}', {'html': html, 'options': options})

        def check(name, actual, expected):
            checks.append({'scenario': name, 'expected': expected, 'observed': actual,
                           'result': 'PASS' if actual == expected else 'PRODUCT_FAIL'})

        en = (FIXTURES / 'classic-en.html').read_text()
        pt = (FIXTURES / 'classic-pt.html').read_text()
        for label, html in [('EN', en), ('EN numbers Portuguese lang', en.replace('lang="en"', 'lang="pt"')),
                            ('EN numbers Portuguese captions', en.replace('Company:', 'Empresa:').replace('Deals</th>', 'Negociações</th>'))]:
            r = parse(html)
            row = r['report']['deals'][2]
            check(label, [r['errors'], row['volume'], row['price'], row['profit'], r['report']['summary']['balance']],
                  [[], 0.4, 1.103, 120, 1585])
        for label, html in [('PT', pt), ('PT numbers English lang', pt.replace('lang="pt"', 'lang="en"'))]:
            r = parse(html)
            row = r['report']['deals'][0]
            check(label, [r['errors'], row['ticket'], row['volume'], row['profit'], row['netResult']],
                  [[], '123456789012345678', 0.1, 1234.56, 1233.06])

        for value, expected in [('1,234.56', 1234.56), ('1.234,56', 1234.56), ('1\u00a0234.56', 1234.56),
                                ('1\u202f234,56', 1234.56), ("1'234.56", 1234.56), ('(12,34)', -12.34),
                                ('−12.34', -12.34), ('12.34 %', 12.34), ('0.00000001', 0.00000001), ('0', 0)]:
            r = parse(fixture(profit=value))
            check('precise value ' + value, [r['errors'], r['report']['deals'][0]['profit']], [[], expected])
        for value in ['12,34.56', '1.23.45', '1 23.00', '1 2', '1e6', 'NaN', 'Infinity', '1.123456789', '9007199254740992']:
            r = parse(fixture(profit=value))
            check('malformed value ' + value, 'number_invalid' in r['errors'], True)

        ambiguous = fixture(profit='1.234')
        r = parse(ambiguous)
        check('ambiguous separator cannot import', ['number_format_ambiguous' in r['errors'], r['report']['deals'][0]['profit']], [True, None])
        for fmt, expected in [('decimal-dot', 1.234), ('decimal-comma', 1234)]:
            r = parse(ambiguous, numberFormat=fmt)
            warning = next((i['message'] for i in r['report']['issues'] if i['code'] == 'number_format_confirmed'), '')
            check('explicit numeric review ' + fmt, [r['errors'], r['report']['deals'][0]['profit'], '1.234 → ' + str(expected) in warning], [[], expected, True])
        r = parse(fixture(volume='0.10', profit='1.234'))
        check('consistent evidence resolves grouping', [r['errors'], r['report']['deals'][0]['profit']], [[], 1.234])
        r = parse(fixture(volume='0.10', profit='12,34'))
        check('mixed format refuses import', 'number_format_conflict' in r['errors'], True)
        r = parse(fixture(profit='1,23'), numberFormat='decimal-dot')
        check('override cannot accept malformed grouping', 'number_invalid' in r['errors'], True)
        r = parse(fixture(profit='1.23'), numberFormat='decimal-comma')
        check('opposite override cannot multiply decimals', 'number_invalid' in r['errors'], True)
        r = parse(fixture(volume='1/2/3'))
        check('extra volume component never discarded', 'number_invalid' in r['errors'], True)
        for value in ['', '—', '-']:
            r = parse(fixture(profit=value))
            check('missing remains unknown ' + repr(value), [r['errors'], r['report']['deals'][0]['profit'], r['report']['deals'][0]['netResult']], [[], None, None])

        for value, expected in [('2026-01-23T10:30:12.123Z', '2026-01-23T10:30:12.123Z'),
                                ('23/01/2026 10:30', '2026-01-23T10:30:00'),
                                ('01/23/2026 10:30', '2026-01-23T10:30:00'),
                                ('01.01.2026', '2026-01-01')]:
            r = parse(fixture(time=value))
            check('valid date ' + value, [r['errors'], r['report']['deals'][0]['time']], [[], expected])
        r = parse(fixture(time='02/03/2026 10:30'))
        check('ambiguous date refuses import', ['date_order_ambiguous' in r['errors'], r['report']['deals'][0]['time']], [True, None])
        r = parse(fixture(time='23/01/2026').replace('<td>123456789012345678</td>', '<td></td>'))
        check('localized row missing ticket cannot disappear',
              [any(i['code'] == 'ticket_missing' for i in r['report']['issues']), bool(r['errors']), len(r['report']['deals'])], [True, True, 0])
        for order, expected in [('dmy', '2026-03-02T10:30:00'), ('mdy', '2026-02-03T10:30:00')]:
            r = parse(fixture(time='02/03/2026 10:30'), dateOrder=order)
            check('explicit date order ' + order, [r['errors'], r['report']['deals'][0]['time']], [[], expected])
        period = '<tr><td>Period:</td><td>01/01/2026 - 31/03/2026</td></tr>'
        r = parse(fixture(time='02/03/2026', extra=period))
        check('period corroborates day first', [r['errors'], r['report']['deals'][0]['time'], r['report']['period']['to']], [[], '2026-03-02', '2026-03-31'])
        r = parse(fixture(time='01/23/2026', extra=period))
        check('conflicting date order refuses import', 'date_order_conflict' in r['errors'], True)
        for value in ['31/02/2026', '2026.02.29', '2026.13.01', '23/01/2026 24:01:00']:
            r = parse(fixture(time=value))
            check('invalid date ' + value, 'date_invalid' in r['errors'], True)
        r = parse(fixture(extra='<tr><td>Period:</td><td>unknown range</td></tr>'))
        check('unreadable declared period blocks', 'date_invalid' in r['errors'], True)
        r = parse(fixture(extra='<tr><td>Balance:</td><td>1.23.45</td></tr>'))
        check('malformed summary never disappears silently', 'number_invalid' in r['errors'], True)

        # Genuine normalized values survive the actual import/export state path.
        result = page.evaluate('''html=>{const M=JPWFXConsolidated,r=M.parseHTML(html),s=M.emptyState(),a={id:'synthetic',...r.identity},p=M.previewImport(s,a,r,{fileHash:'synthetic-numbers'}),one=M.applyImport(s,p,{}),restored=JSON.parse(JSON.stringify(one.state)),repeat=M.applyImport(restored,M.previewImport(restored,a,r,{fileHash:'synthetic-numbers'}),{});return {valid:M.validateState(restored).ok,same:JSON.stringify(restored)===JSON.stringify(repeat.state),profit:restored.accounts[0].deals[2].profit,price:restored.accounts[0].deals[2].price}}''', en.replace('lang="en"', 'lang="pt"'))
        check('normalized roundtrip and duplicate no-op', result, {'valid': True, 'same': True, 'profit': 120, 'price': 1.103})
        check('no browser errors', errors, [])
        check('no external requests', requests, [])
        context.close()
        browser.close()
    report = {'result': 'PASS' if all(c['result'] == 'PASS' for c in checks) else 'PRODUCT_FAIL',
              'model': str(args.model.resolve()), 'sha256': hashlib.sha256(args.model.read_bytes()).hexdigest(),
              'syntheticOnly': True, 'checks': checks}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()

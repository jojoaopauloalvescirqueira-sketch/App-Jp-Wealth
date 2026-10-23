#!/usr/bin/env python3
"""Economic calendar contract: synthetic source data, real pure JS and collector.

No live network, browser profile, financial state or repository receipts are used.
Breaks caught: wrong month boundaries/time zone; empty filter masquerading as
unknown coverage; discarded cancellation; duplicate/rescheduled source identities;
unsafe links; mutated package; collector overwriting good output after bad input.
Inline distribution additionally preserves source markup as text without allowing
an HTML closing-script sequence to escape the generated JavaScript block.
"""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'src/js/40-app/16-monthly-economic-data.js'
COLLECTOR = ROOT / 'infra/monthly-economic-feed/collect_feed.py'
NODE = os.environ.get('JPW_NODE') or shutil.which('node') or str(
    Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
STAMP = '2026-10-23T12:00:00Z'


def event(identity, at=None, date=None, precision='instant', impact='high', **extra):
    return dict(id=identity, title=identity, currency='USD', impact=impact,
                date=date or (at or '')[:10], at=at, precision=precision,
                sourceId='fixture', sourceUrl='https://example.org/calendar',
                timeZone='America/New_York', status='scheduled', reviewedAt=STAMP,
                **extra)


def fixture(events):
    return {'schemaVersion': 1, 'generatedAt': STAMP, 'updatedAt': STAMP,
            'sources': [{'id': 'fixture', 'name': 'Synthetic fixture', 'currency': 'USD',
                         'url': 'https://example.org/calendar', 'timeZone': 'America/New_York'}],
            'events': events,
            'coverage': [{'currency': 'USD', 'sourceId': 'fixture', 'month': '2026-10',
                          'from': '2026-10-01', 'to': '2026-10-31', 'status': 'confirmed',
                          'reviewedAt': STAMP, 'reason': 'Synthetic complete source month.'}]}


NODE_PROBE = r"""
const fs=require('node:fs'),vm=require('node:vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
let source=fs.readFileSync(input.model,'utf8');
if(input.fixture) source=source.replace(/\/\* JPW_MONTHLY_DATA_BEGIN \*\/[\s\S]*?\/\* JPW_MONTHLY_DATA_END \*\//,
 '/* JPW_MONTHLY_DATA_BEGIN */'+JSON.stringify(input.fixture)+'/* JPW_MONTHLY_DATA_END */');
const c={Intl,URL,console}; c.window=c;
const RealDate=Date;c.Date=class extends RealDate{static now(){return Date.parse('2026-10-23T12:00:00Z');}};
for(const key of ['fetch','document','localStorage','sessionStorage','S'])
 Object.defineProperty(c,key,{get(){throw new Error('Forbidden IO: '+key);}});
vm.createContext(c);vm.runInContext(source,c,{timeout:2000});
const api=c.JPWEconomicCalendar;
let result;
try {
 if(input.action==='metadata') result={sources:api.sources(),metadata:api.metadata()};
 else if(input.action==='immutability'){
   const first=api.queryRange(input.query);first.events[0].title='MUTATED';
   const sources=api.sources();sources[0].name='MUTATED';
   result={again:api.queryRange(input.query),sources:api.sources()};
 }else result=api.queryRange(input.query);
 process.stdout.write(JSON.stringify({result}));
}catch(error){process.stdout.write(JSON.stringify({error:error.name,message:error.message}));}
"""


class ModelContract(unittest.TestCase):
    def call(self, events=None, query=None, action=None, package=None):
        self.assertTrue(MODEL.exists(), 'Monthly public economic model is not implemented')
        data = {'model': str(MODEL), 'query': query or {
            'from': '2026-10-01', 'to': '2026-10-31', 'timeZone': 'UTC'}}
        if package is not None or events is not None:
            data['fixture'] = package if package is not None else fixture(events)
        if action: data['action'] = action
        p = subprocess.run([NODE, '-e', NODE_PROBE], input=json.dumps(data), text=True,
                           capture_output=True, timeout=8)
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def test_01_first_and_last_civil_day_are_inclusive(self):
        data = [event('before', '2026-09-30T23:59:59Z'),
                event('first', '2026-10-01T00:00:00Z'),
                event('last', '2026-10-31T23:59:59Z'),
                event('after', '2026-11-01T00:00:00Z')]
        self.assertEqual([e['id'] for e in self.call(data)['result']['events']], ['first', 'last'])

    def test_02_instant_moves_to_user_day_and_retains_source_date(self):
        result = self.call([event('boundary', '2026-10-01T00:30:00Z')], {
            'from': '2026-09-30', 'to': '2026-09-30', 'timeZone': 'America/Sao_Paulo'})['result']
        self.assertEqual(result['events'][0]['date'], '2026-09-30')
        self.assertEqual(result['events'][0]['sourceDate'], '2026-10-01')

    def test_03_date_only_never_shifts_with_user_zone(self):
        result = self.call([event('civil', date='2026-10-01', precision='date')], {
            'from': '2026-10-01', 'to': '2026-10-01', 'timeZone': 'Pacific/Honolulu'})['result']
        self.assertEqual(result['events'][0]['date'], '2026-10-01')
        self.assertIsNone(result['events'][0]['at'])

    def test_04_currency_and_impact_filters_do_not_change_coverage(self):
        package = fixture([event('a', '2026-10-02T12:00:00Z')])
        result = self.call(package=package, query={'from':'2026-10-01','to':'2026-10-31',
            'currencies':['USD'],'impacts':['low'],'timeZone':'UTC'})['result']
        self.assertEqual(result['events'], [])
        self.assertEqual(result['coverage'][0]['status'], 'confirmed')

    def test_05_explicit_empty_filter_means_empty_and_unknown_currency_remains_unknown(self):
        package = fixture([event('a', '2026-10-02T12:00:00Z')])
        self.assertEqual(self.call(package=package, query={'from':'2026-10-01','to':'2026-10-31',
            'currencies':[],'timeZone':'UTC'})['result']['events'], [])
        result = self.call(package=package, query={'from':'2026-10-01','to':'2026-10-31',
            'currencies':['CHF'],'timeZone':'UTC'})['result']
        self.assertEqual(result['events'], [])
        self.assertTrue(result['coverage'])
        self.assertTrue(all(x['status'] in ('pending','unavailable') for x in result['coverage']))

    def test_06_latest_revision_reschedules_same_identity_and_keeps_cancelled(self):
        old = event('same', '2026-10-02T12:00:00Z', sequence=1)
        new = event('same', '2026-10-03T12:00:00Z', sequence=2)
        cancelled = event('cancelled', '2026-10-04T12:00:00Z')
        cancelled['status'] = 'cancelled'
        result = self.call([new,old,cancelled])['result']['events']
        self.assertEqual([(x['id'],x['date'],x['status']) for x in result],
                         [('same','2026-10-03','scheduled'),('cancelled','2026-10-04','cancelled')])

    def test_07_unsafe_external_link_and_offsetless_instant_are_not_exposed(self):
        unsafe=event('bad-link','2026-10-02T12:00:00Z');unsafe['sourceUrl']='javascript:alert(1)'
        ambiguous=event('bad-time','2026-10-02T12:00:00')
        result=self.call([unsafe,ambiguous,event('ok','2026-10-02T12:00:00Z')])['result']
        self.assertEqual([x['id'] for x in result['events']], ['ok'])
        self.assertEqual(result['coverage'][0]['status'], 'partial')

    def test_08_invalid_range_and_zone_refuse_without_io(self):
        for query in [{'from':'2026-02-30','to':'2026-03-01'},
                      {'from':'2026-10-31','to':'2026-10-01'},
                      {'from':'2026-10-01','to':'2026-10-31','timeZone':'Invalid/Zone'}]:
            self.assertIn('error', self.call([], query))

    def test_09_returned_objects_cannot_mutate_embedded_data(self):
        result=self.call([event('a','2026-10-02T12:00:00Z')],action='immutability')['result']
        self.assertEqual(result['again']['events'][0]['title'],'a')
        self.assertEqual(result['sources'][0]['name'],'Synthetic fixture')

    def test_10_missing_month_and_expired_review_are_not_confirmed(self):
        package=fixture([]);package['coverage'][0]['validUntil']='2026-10-22T12:00:00Z'
        self.assertEqual(self.call(package=package)['result']['coverage'][0]['status'],'stale')
        result=self.call(package=package,query={'from':'2026-11-01','to':'2026-11-30',
            'currencies':['USD'],'timeZone':'UTC'})['result']
        self.assertTrue(all(x['status']=='unavailable' for x in result['coverage']))

    def test_11_shipped_package_has_real_uid_and_honest_pending_currencies(self):
        result=self.call()['result']
        events=result['events'];ids=[x['id'] for x in events]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertIn('bea:afcb09fd-b564-4125-88aa-a0b23b358a6f',ids)
        self.assertTrue(any(x['currency']=='GBP' for x in events))
        for currency in ['CHF']:
            rows=[x for x in result['coverage'] if x['currency']==currency]
            self.assertTrue(rows,currency)
            self.assertTrue(all(x['status']=='pending' for x in rows),currency)
        self.assertTrue(any(x['currency']=='NZD' and x['status']=='partial' for x in result['coverage']))
        self.assertTrue(any(x['currency']=='NZD' and x['precision']=='instant' for x in events))
        self.assertTrue(all(x['sourceUrl'].startswith(('https://','http://')) for x in events))


class CollectorContract(unittest.TestCase):
    def module(self):
        self.assertTrue(COLLECTOR.exists(),'Monthly BEA collector is not implemented')
        spec=importlib.util.spec_from_file_location('monthly_economic_collector',COLLECTOR)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        return mod

    def test_12_ics_unfolds_and_uses_uid_instead_of_date_for_identity(self):
        mod=self.module()
        text='BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nUID:stable\r\nDTSTART:20261001T003000Z\r\nSUMMARY:GDP\\,\r\n+ continued\r\nSEQUENCE:2\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'.replace('+ continued',' continued')
        rows=mod.parse_bea_ics(text,STAMP)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['id'],'bea:stable')
        self.assertEqual(rows[0]['title'],'GDP,continued')
        self.assertEqual(rows[0]['at'],'2026-10-01T00:30:00Z')

    def test_13_collector_refuses_missing_identity_and_invalid_timestamp(self):
        mod=self.module()
        for fields in ['DTSTART:20261001T003000Z\nSUMMARY:GDP',
                       'UID:a\nDTSTART:20260230T003000Z\nSUMMARY:GDP']:
            with self.assertRaises(ValueError):
                mod.parse_bea_ics('BEGIN:VCALENDAR\nBEGIN:VEVENT\n'+fields+'\nEND:VEVENT\nEND:VCALENDAR',STAMP)

    def test_14_invalid_input_never_overwrites_existing_output(self):
        self.module()
        with tempfile.TemporaryDirectory(prefix='jpw-monthly-feed-test-') as folder:
            root=Path(folder);bad=root/'bad.ics';out=root/'existing.json'
            bad.write_text('<html>rate limited</html>');out.write_text('preserved')
            p=subprocess.run([os.sys.executable,str(COLLECTOR),'--month','2026-10',
                '--input-bea',str(bad),'--output',str(out)],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertEqual(out.read_text(),'preserved')

    def test_15_embedded_data_matches_canonical_package(self):
        self.assertTrue(MODEL.exists(),'Monthly package is not embedded')
        path=ROOT/'infra/monthly-economic-feed/data/monthly-economic-2026-10.json'
        self.assertTrue(path.exists(),'Canonical public monthly package is missing')
        match=re.search(r'/\* JPW_MONTHLY_DATA_BEGIN \*/([\s\S]*?)/\* JPW_MONTHLY_DATA_END \*/',MODEL.read_text())
        self.assertIsNotNone(match)
        self.assertEqual(json.loads(match.group(1)),json.loads(path.read_text()))

    def test_16_offline_collector_reproduces_real_month_without_fresh_capture_claim(self):
        self.module()
        snapshot=ROOT/'infra/monthly-economic-feed/evidence/bea-schedule.ics'
        canonical=json.loads((ROOT/'infra/monthly-economic-feed/data/bea-2026-10.json').read_text())
        with tempfile.TemporaryDirectory(prefix='jpw-monthly-offline-') as folder:
            output=Path(folder)/'bea.json'
            p=subprocess.run([os.sys.executable,str(COLLECTOR),'--month','2026-10',
                '--input-bea',str(snapshot),'--output',str(output)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            actual=json.loads(output.read_text())
            self.assertEqual([x['id'] for x in actual['events']],[x['id'] for x in canonical['events']])
            self.assertEqual(len(actual['events']),5)
            self.assertIsNone(actual['provenance']['capturedAt'])
            self.assertEqual(actual['provenance']['sha256'],hashlib.sha256(snapshot.read_bytes()).hexdigest())

    def test_17_offline_package_check_reproduces_without_writing_product_files(self):
        script=ROOT/'infra/monthly-economic-feed/build_package.py'
        spec=importlib.util.spec_from_file_location('monthly_economic_builder',script)
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        self.assertTrue(callable(getattr(builder,'build_package',None)),
                        'Offline builder needs explicit non-writing check mode')
        canonical=ROOT/'infra/monthly-economic-feed/data/monthly-economic-2026-10.json'
        before=[(path.stat().st_mtime_ns,path.read_bytes()) for path in (MODEL,canonical)]
        p=subprocess.run([os.sys.executable,str(script),'--check'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('Offline package verified',p.stdout)
        self.assertEqual(before,[(path.stat().st_mtime_ns,path.read_bytes()) for path in (MODEL,canonical)])


class InlineDistributionContract(unittest.TestCase):
    TITLE = 'GDP <b>release</b> </ScRiPt><script>window.__calendarInjected=true</script>'

    def generated_fixture(self, folder):
        root = Path(folder)
        source = ROOT / 'infra/monthly-economic-feed'
        target = root / 'infra/monthly-economic-feed'
        shutil.copytree(source, target)
        model = root / 'src/js/40-app/16-monthly-economic-data.js'
        model.parent.mkdir(parents=True)
        model.write_bytes(MODEL.read_bytes())
        bea_path = target / 'data/bea-2026-10.json'
        bea = json.loads(bea_path.read_text())
        bea['events'][0]['title'] = self.TITLE
        identity = bea['events'][0]['id']
        bea_path.write_text(json.dumps(bea, ensure_ascii=False))
        spec = importlib.util.spec_from_file_location('monthly_inline_builder', target / 'build_package.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        builder.ROOT = root
        builder.build_package()
        return model, target / 'data/monthly-economic-2026-10.json', identity

    def test_18_generated_js_escapes_html_delimiters_without_changing_canonical_titles(self):
        with tempfile.TemporaryDirectory(prefix='jpw-calendar-inline-') as folder:
            model, canonical, identity = self.generated_fixture(folder)
            source = model.read_text()
            packet = json.loads(canonical.read_text())
            self.assertEqual(next(row['title'] for row in packet['events'] if row['id'] == identity), self.TITLE)
            self.assertIn(self.TITLE, canonical.read_text())
            self.assertIsNone(re.search(r'(?i)</script', source),
                              'Generated JS contains an HTML closing-script delimiter')
            result = subprocess.run([NODE, '-e', NODE_PROBE], input=json.dumps({
                'model': str(model), 'query': {'from': '2026-10-01', 'to': '2026-10-31', 'timeZone': 'UTC'}}),
                capture_output=True, text=True, timeout=8)
            self.assertEqual(result.returncode, 0, result.stderr)
            events = json.loads(result.stdout)['result']['events']
            self.assertEqual(next(row['title'] for row in events if row['id'] == identity), self.TITLE)

    def test_19_portable_style_inline_html_never_executes_title_markup(self):
        from playwright.sync_api import sync_playwright
        from dashboard_macro_test import launch_browser
        with tempfile.TemporaryDirectory(prefix='jpw-calendar-inline-browser-') as folder:
            model, _, identity = self.generated_fixture(folder)
            with sync_playwright() as playwright:
                browser = launch_browser(playwright)
                try:
                    page = browser.new_page()
                    page.set_content('<!doctype html><script>' + model.read_text() + '</script>')
                    self.assertFalse(page.evaluate('window.__calendarInjected === true'),
                                     'Economic title escaped its inline script and executed markup')
                    self.assertTrue(page.evaluate('!!window.JPWEconomicCalendar'))
                    actual = page.evaluate("id => JPWEconomicCalendar.queryRange({from:'2026-10-01',to:'2026-10-31',timeZone:'UTC'}).events.find(row => row.id === id).title", identity)
                    self.assertEqual(actual, self.TITLE)
                finally:
                    browser.close()


if __name__=='__main__':
    unittest.main(verbosity=2)

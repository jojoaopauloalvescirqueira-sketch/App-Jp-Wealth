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
if(input.runtimePayload){
 const payload=input.runtimePayload,stamp=payload.collectedAt||payload.generated_at;
 const mode=payload.version===1?'legacy-partial':'normalized';
 c.JPWCalendarFeed={snapshot:()=>({payload,revision:'SYN runtime',fetchedAt:Date.parse(stamp),mode}),status:()=>({mode,collectedAt:stamp})};
}
const api=c.JPWEconomicCalendar;
let result;
try {
 if(input.action==='metadata') result={sources:api.sources(),metadata:api.metadata()};
 else if(input.action==='metadata-immutability'){
   const first=api.metadata();first.limitations.push('MUTATED');
   first.editorialPolicy.origins[0].publisher='MUTATED';
   first.officialBaseMetadata.limitations.push('MUTATED');
   first.updatePolicy.forexFactoryMaxAgeSeconds=-1;
   result={metadata:api.metadata()};
 }
 else if(input.action==='immutability'){
   const first=api.queryRange(input.query);first.events[0].title='MUTATED';
   const sources=api.sources();sources[0].name='MUTATED';
   result={again:api.queryRange(input.query),sources:api.sources()};
 }else result=api.queryRange(input.query);
 process.stdout.write(JSON.stringify({result}));
}catch(error){process.stdout.write(JSON.stringify({error:error.name,message:error.message}));}
"""


class ModelContract(unittest.TestCase):
    def call(self, events=None, query=None, action=None, package=None, runtime_payload=None):
        self.assertTrue(MODEL.exists(), 'Monthly public economic model is not implemented')
        data = {'model': str(MODEL), 'query': query or {
            'from': '2026-10-01', 'to': '2026-10-31', 'timeZone': 'UTC'}}
        if package is not None or events is not None:
            data['fixture'] = package if package is not None else fixture(events)
        if action: data['action'] = action
        if runtime_payload is not None: data['runtimePayload'] = runtime_payload
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
            self.assertTrue(any(x['sourceId']=='chf-pending' and x['status']=='pending' for x in rows),currency)
        self.assertTrue(any(x['currency']=='NZD' and x['status']=='partial' for x in result['coverage']))
        self.assertTrue(any(x['currency']=='NZD' and x['precision']=='instant' for x in events))
        self.assertTrue(all(x['sourceUrl'].startswith(('https://','http://')) for x in events))

    def test_20_nine_currencies_and_verified_oct28_policy_events(self):
        metadata=self.call(action='metadata')['result']['metadata']
        self.assertEqual(set(metadata['currencies']),{'USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY'})
        result=self.call(query={'from':'2026-10-28','to':'2026-10-28','currencies':['CAD','USD'],
                               'impacts':['high'],'timeZone':'America/Sao_Paulo'})['result']
        expected={'boc-policy-2026-10:'+kind:'2026-10-28T13:45:00+00:00'
                  for kind in ['rate-decision','policy-statement','monetary-policy-report']}
        expected.update({'boc-policy-2026-10:press-conference':'2026-10-28T14:30:00+00:00',
                         'fed-fomc-2026-10:rate-decision':'2026-10-28T18:00:00+00:00',
                         'fed-fomc-2026-10:policy-statement':'2026-10-28T18:00:00+00:00',
                         'fed-fomc-2026-10:press-conference':'2026-10-28T18:30:00+00:00'})
        from datetime import datetime, timezone
        for family,at in expected.items():
            rows=[e for e in result['events'] if e.get('familyKey')==family]
            self.assertEqual(len(rows),1,(family,rows))
            self.assertEqual(datetime.fromisoformat(rows[0]['at'].replace('Z','+00:00')).astimezone(timezone.utc).isoformat(),at)
            self.assertEqual(rows[0]['date'],'2026-10-28')
            self.assertEqual(rows[0]['impact'],'high')

    def test_21_weekly_coverage_cannot_confirm_another_day_in_the_same_month(self):
        package=fixture([]);package['coverage'][0].update({'from':'2026-10-25','to':'2026-10-31'})
        outside=self.call(package=package,query={'from':'2026-10-20','to':'2026-10-20','currencies':['USD'],'timeZone':'UTC'})['result']
        self.assertFalse(any(row['status']=='confirmed' for row in outside['coverage']),outside)
        inside=self.call(package=package,query={'from':'2026-10-28','to':'2026-10-28','currencies':['USD'],'timeZone':'UTC'})['result']
        self.assertTrue(any(row['status']=='confirmed' for row in inside['coverage']),inside)


    def test_22_composed_metadata_scopes_original_official_policy(self):
        canonical = json.loads((ROOT / 'infra/monthly-economic-feed/data/monthly-economic-2026-10.json').read_text())
        metadata = self.call(action='metadata')['result']['metadata']
        policy = metadata['editorialPolicy']
        self.assertEqual(policy['kind'], 'mixed', 'Composed events cannot be described as solely JP editorial impact')
        self.assertEqual(policy['publisherRole'], 'composition-policy')
        self.assertEqual(policy['origins'], [
            {'id':'forexfactory','publisher':'Forex Factory','kind':'provider'},
            {'id':'jpw-editorial','publisher':'JP Wealth','kind':'editorial'}])
        self.assertEqual(set(metadata['currencies']), {'USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY'})
        self.assertEqual(metadata['updatePolicy'], {
            'queryMode':'synchronous-snapshot', 'refreshMode':'shared-public-feed-adapter',
            'sourceAgeBasis':'collectedAt', 'forexFactoryMaxAgeSeconds':7200,
            'officialExpiryBasis':'coverage.validUntil', 'externalSchedule':'not-asserted'})
        original = metadata['officialBaseMetadata']
        self.assertEqual(original['scope'], 'official-base-before-public-feed')
        self.assertEqual(set(original['currencies']), {'USD','GBP','JPY','NZD','CHF'})
        self.assertEqual(len(original['sourceIds']), 11)
        self.assertFalse(any(source_id.startswith('ff-') for source_id in original['sourceIds']))
        self.assertEqual(original['editorialPolicy']['id'], 'jpw-macro-impact-v1')
        self.assertEqual(original['editorialPolicy']['kind'], 'editorial')
        self.assertEqual(original['generatedAt'], '2026-10-23T15:52:12Z')
        self.assertEqual(original['updatedAt'], '2026-10-23T15:52:12Z')
        self.assertEqual(metadata['generatedAtScope'], 'official-base')
        self.assertEqual(metadata['generatedAt'], original['generatedAt'])
        old_claims = [
            'Entrega parcial por fontes/famílias; não comprova mês completo de todas as cinco moedas.',
            'Não contém valores anteriores, consenso, resultado, surpresa ou impacto nativo de provedor.',
            'Sem atualização automática no app; pacote estático revisado, validade de cobertura de 48 horas.']
        for claim in old_claims:
            self.assertIn(claim, original['limitations'], 'Original official metadata must remain recoverable in its own scope')
            self.assertNotIn(claim, metadata['limitations'], 'An old official-base claim cannot describe the combined feed')
        self.assertEqual(metadata['officialBaseMetadata'], canonical['officialBaseMetadata'])
        self.assertEqual(metadata['editorialPolicy'], canonical['editorialPolicy'])
        self.assertEqual(metadata['updatePolicy'], canonical['updatePolicy'])
        self.assertEqual(metadata['publicFeedProvenance'], canonical['publicFeedProvenance'])
        self.assertEqual(self.call(action='metadata-immutability')['result']['metadata'], metadata)
        # The official-only control stays honest without acquiring an FF policy.
        official = fixture([event('SYN official', '2026-10-02T12:00:00Z')])
        official.update(currencies=['USD'], months=['2026-10'],
                        editorialPolicy={'id':'SYN-official-only','publisher':'JP Wealth','kind':'editorial','dateOnly':'SYN civil date'},
                        limitations=['SYN original official scope'])
        control = self.call(package=official, action='metadata')['result']['metadata']
        self.assertEqual(control['editorialPolicy'], official['editorialPolicy'])
        self.assertEqual(control['limitations'], official['limitations'])
        self.assertIsNone(control['officialBaseMetadata'])
        self.assertIsNone(control['updatePolicy'])
        self.assertEqual(control['generatedAtScope'], 'packet')
        legacy = {'version':1,'generated_at':STAMP,'events':[{
            'title':'SYN runtime FF','country':'USD','date':'2026-10-23T12:00:00Z','impact':'High'}]}
        for payload in [legacy, {'schemaVersion':2,'collectedAt':STAMP,'packagePublishedAt':STAMP,
                'sourcePublishedAt':None,'currencies':['USD'],'sources':[{'id':'ff-USD',
                'currency':'USD','name':'Synthetic FF','url':'https://www.forexfactory.com/calendar'}],
                'events':[],'coverage':[]}]:
            dynamic = self.call(package=official, action='metadata', runtime_payload=payload)['result']['metadata']
            self.assertEqual(dynamic['editorialPolicy']['kind'], 'mixed')
            self.assertEqual(dynamic['editorialPolicy']['origins'], policy['origins'])
            self.assertEqual(dynamic['editorialPolicy']['dateOnly'], official['editorialPolicy']['dateOnly'])
            self.assertEqual(dynamic['updatePolicy'], metadata['updatePolicy'])
            self.assertEqual(dynamic['limitations'], metadata['limitations'], 'Runtime compatibility and shipped composition need the same truthful global limits')
            self.assertEqual(dynamic['officialBaseMetadata'], {
                'scope':'official-base-before-public-feed','generatedAt':STAMP,'updatedAt':STAMP,
                'currencies':['USD'],'sourceIds':['fixture'],
                'editorialPolicy':official['editorialPolicy'],'limitations':official['limitations']})
            self.assertEqual(dynamic['feed']['mode'], 'legacy-partial' if payload.get('version')==1 else 'normalized')
        # Exercise the compiler with an independent synthetic old policy. Only
        # composition may add metadata; actual event/coverage records retain identity.
        script = ROOT / 'infra/monthly-economic-feed/build_package.py'
        spec = importlib.util.spec_from_file_location('metadata_composition_builder', script)
        builder = importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        snapshot = json.loads(json.dumps(official))
        ff = event('SYN FF', '2026-10-28T17:00:00Z')
        ff.update(sourceId='ff-USD', sourceUrl='https://www.forexfactory.com/calendar',
                  provider='Forex Factory', providerImpact='High', impactOrigin='provider')
        public = {'schemaVersion':2,'collectedAt':'2026-10-28T20:00:00Z',
                  'packagePublishedAt':'2026-10-28T20:01:00Z','sourcePublishedAt':None,
                  'currentWeekFrom':'2026-10-25','currencies':['USD'],
                  'sources':[{'id':'ff-USD','currency':'USD','name':'Synthetic FF','url':'https://www.forexfactory.com/calendar'}],
                  'events':[ff], 'coverage':[{'sourceId':'ff-USD','currency':'USD','month':'2026-10',
                    'from':'2026-10-25','to':'2026-10-31','status':'partial','reviewedAt':'2026-10-28T20:00:00Z'}]}
        merged = builder.merge_public_packet(official, public)
        self.assertEqual(merged['officialBaseMetadata'], {
            'scope':'official-base-before-public-feed','generatedAt':snapshot['generatedAt'],
            'updatedAt':snapshot['updatedAt'],'currencies':['USD'],'sourceIds':['fixture'],
            'editorialPolicy':snapshot['editorialPolicy'],'limitations':snapshot['limitations']})
        self.assertEqual(merged['events'], snapshot['events'] + public['events'])
        self.assertEqual(merged['sources'], snapshot['sources'] + public['sources'])
        self.assertEqual(merged['coverage'], snapshot['coverage'] + public['coverage'])
        self.assertEqual(public['events'], [ff])
        self.assertEqual(self.call(package=merged, action='metadata')['result']['metadata']['editorialPolicy']['kind'], 'mixed')


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


class SharedFeedContract(unittest.TestCase):
    def test_shared_public_runtime_and_legacy_consumers(self):
        script=ROOT/'tools/economic_calendar_feed_runtime_test.js'
        self.assertTrue(script.is_file(),'Permanent shared runtime cases are required')
        run=subprocess.run([NODE,str(script)],cwd=ROOT,text=True,capture_output=True,timeout=30)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        report=json.loads(run.stdout)
        self.assertEqual(report.get('suite'),'economic-calendar-feed-runtime')
        rows=report.get('results',[])
        self.assertEqual(len(rows),24,'Runtime must report all 24 permanent cases')
        self.assertEqual(len({row.get('id') for row in rows}),24)
        self.assertEqual({row.get('id','').split('-')[2] for row in rows},{str(i).zfill(2) for i in range(1,25)})
        self.assertTrue(all(row.get('classification')=='PASS' for row in rows),report)
        self.assertEqual(report.get('summary'),{'PASS':24,'PRODUCT_FAIL':0})
        print(run.stdout,end='')

    def test_public_collector_preservation_and_archives(self):
        script=ROOT/'tools/ff_calendar_collector_test.py'
        self.assertTrue(script.is_file(),'Permanent public collector cases are required')
        run=subprocess.run([os.sys.executable,str(script)],cwd=ROOT,text=True,capture_output=True,timeout=60)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        print(run.stdout+run.stderr,end='')


if __name__=='__main__':
    unittest.main(verbosity=2)

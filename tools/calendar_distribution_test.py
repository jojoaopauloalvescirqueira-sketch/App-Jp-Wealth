#!/usr/bin/env python3
"""CALENDAR-DISTRIBUTION-01: current calendar/agenda bytes in four distributions.

Uses real UI, canonical writer, service worker and reload in disposable contexts.
Only existing nominal bootstrap feeds are intercepted; the shipped monthly pack
is loaded unchanged. The portable case receives exactly one copied HTML file.
Approved source: docs/superpowers/plans/2026-10-23-calendar-agenda.md.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import partial
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
import time
import traceback
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeout
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from notes_launcher_test import Quiet, launch_options

ROOT = Path(__file__).resolve().parents[1]
PORTABLE = 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
MAIN_KEY = 'jpwealth_v9_state'
PREFS_KEY = 'jpwealth_calendar_view_v1'
PANEL = '#calendarDialog .calendar-panel'
NOW = datetime(2026, 10, 23, 12, tzinfo=timezone.utc)
CURRENCIES = ['USD', 'GBP', 'JPY', 'NZD', 'CHF']
IMPACTS = ['high', 'medium', 'low', 'unclassified']
MODULES = ['src/js/10-domain/19-personal-agenda.js',
           'src/js/40-app/16-monthly-economic-data.js',
           'src/js/40-app/19-calendar-agenda.js']
CASES = ('http', 'pwa-offline', 'modular-file', 'portable-file')


def inventory(root):
    manifest = root / 'src/js/manifest.json'
    entries = json.loads(manifest.read_text())['files']
    names = sorted(set([row['path'] for row in entries] + MODULES + [
        'index.html', 'src/styles/app.css', 'src/js/manifest.json', 'sw.js',
        'build-id.js', PORTABLE, 'tools/calendar_distribution_test.py',
        'tools/browser_bootstrap_fixture.py', 'tools/browser_fixture_server.py',
        'tools/notes_launcher_test.py']))
    return {name: {'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest(),
                   'bytes': (root / name).stat().st_size}
            if (root / name).is_file() else None for name in names}


def source_packet(root):
    text = (root / MODULES[1]).read_text()
    match = re.search(r'/\* JPW_MONTHLY_DATA_BEGIN \*/([\s\S]*?)/\* JPW_MONTHLY_DATA_END \*/', text)
    if not match:
        raise ValueError('HARNESS: shipped economic packet delimiters missing')
    packet = json.loads(match.group(1))
    assert len(packet['events']) > 0, 'Shipped economic package must contain actual source events'
    assert len({e['id'] for e in packet['events']}) == len(packet['events']), 'Duplicate source event IDs'
    return packet


def expected_events(packet, currencies=CURRENCIES, impacts=IMPACTS, zone='UTC',
                    start='2026-10-01', end='2026-11-30'):
    """Independent civil-date/filter oracle over this run's shipped public data."""
    rows = []
    for event in packet['events']:
        date = event['date'] if event['precision'] == 'date' else datetime.fromisoformat(
            event['at'].replace('Z', '+00:00')).astimezone(ZoneInfo(zone)).date().isoformat()
        if event['currency'] in currencies and event['impact'] in impacts and start <= date <= end:
            rows.append({'id': event['id'], 'title': event['title'], 'date': date,
                         'sourceDate': event['date'], 'precision': event['precision'],
                         'currency': event['currency'], 'impact': event['impact']})
    return sorted(rows, key=lambda row: row['id'])


def query(page, currencies=CURRENCIES, impacts=IMPACTS, zone='UTC',
          start='2026-10-01', end='2026-11-30'):
    return page.evaluate('o=>JPWEconomicCalendar.queryRange(o)', {
        'from': start, 'to': end, 'currencies': currencies, 'impacts': impacts, 'timeZone': zone})


def financial(page):
    return page.evaluate("""()=>{
      const omit=doc=>{const copy=structuredClone(doc);delete copy.personalAgenda;delete copy.dataGovernance;return copy;};
      return {memory:omit(S),disk:omit(JSON.parse(localStorage.getItem(LSKEY)))};
    }""")


def instrument(page):
    page.evaluate("""()=>{
      window.__calendarDistributionWrites=[];
      for(const method of ['setItem','removeItem','clear']){
        const original=Storage.prototype[method];
        Storage.prototype[method]=function(...args){
          if(this===localStorage)__calendarDistributionWrites.push({method,key:args[0]||null});
          return original.apply(this,args);
        };
      }
    }""")


def main_writes(page):
    return page.evaluate('key=>__calendarDistributionWrites.filter(w=>w.key===key||w.method==="clear").length', MAIN_KEY)


def confirmed(page):
    receipt = page.evaluate('jpWealthPersistenceLastResult()')
    assert receipt['status'] == 'CONFIRMED', receipt
    assert page.evaluate('JSON.stringify(S.personalAgenda)===JSON.stringify(JSON.parse(localStorage.getItem(LSKEY)).personalAgenda)'), 'Memory and durable agenda differ'
    return receipt


def require_apis(page):
    loaded = page.evaluate("""()=>({navigation:!!window.JPWNavigation,
      agenda:typeof window.JPWAgenda?.commands?.save==='function',
      economic:typeof window.JPWEconomicCalendar?.queryRange==='function',
      calendar:typeof window.JPWCalendar?.open==='function',
      header:!!document.querySelector('#headerCalendarBtn')})""")
    assert all(loaded.values()), 'Required Calendar/Agenda distribution API/UI absent: ' + json.dumps(loaded)


def open_calendar(page):
    page.evaluate('closeModal();window.__onbShown=true')
    page.locator('#headerCalendarBtn').click()
    expect(page.locator('#calendarDialog')).to_be_visible()
    assert page.locator('#calendarDialog').evaluate("e=>e.matches(':modal')"), 'Header must open the real native dialog'
    expect(page.locator(PANEL + ' [data-calendar-date="2026-10-23"]')).to_have_count(1)
    return page.locator(PANEL)


def assert_dots(page, packet, currencies, impacts):
    expected = Counter(row['date'] for row in expected_events(packet, currencies, impacts,
                      start='2026-10-01', end='2026-10-31'))
    page.wait_for_function("""expected=>{
      const cells=[...document.querySelectorAll('#calendarDialog [data-calendar-date]')].filter(e=>e.dataset.calendarDate.startsWith('2026-10'));
      return cells.length===31&&cells.every(e=>!!e.querySelector('.calendar-economic-dot')===!!expected[e.dataset.calendarDate]);
    }""", arg=dict(expected))
    assert page.locator(PANEL + ' .calendar-economic-dot').count() > 0, 'Actual shipped feed must paint economic markers'
    return dict(expected)


def assert_source_disclosures(panel, packet, row):
    links = panel.locator('.calendar-source-links [data-calendar-source]')
    expect(links).to_have_count(len(packet['sources']))
    actual = sorted(links.evaluate_all('es=>es.map(e=>({id:e.dataset.calendarSource,url:e.getAttribute("href"),name:e.textContent}))'), key=lambda source:source['id'])
    expected = sorted(({'id':source['id'],'url':source['url'],'name':source['name']}
                       for source in packet['sources']), key=lambda source:source['id'])
    assert actual == expected, {'actualSourceLinks':actual, 'expectedSourceLinks':expected}
    disclosures = []
    for source in packet['sources']:
        source_row = panel.locator('.calendar-source-links [data-calendar-source="'+source['id']+'"]').locator('..')
        attribution = source_row.locator('p.calendar-meta')
        expect(attribution).to_have_count(1 if source.get('attribution') else 0)
        if source.get('attribution'):
            expect(attribution).to_have_text(source['attribution'])
        label = source_row.locator('span.calendar-meta')
        expect(label).to_have_count(1 if source.get('license') else 0)
        license_link = source_row.locator('.calendar-license-link')
        expect(license_link).to_have_count(1 if source.get('license') and source.get('licenseUrl') else 0)
        if source.get('license'):
            expect(label).to_have_text(source['license'])
            if source.get('licenseUrl'):
                expect(license_link).to_have_attribute('href',source['licenseUrl'])
                expect(license_link).to_have_text(source['license'])
        disclosures.append({'id':source['id'],'url':source['url'],
                            'attribution':attribution.inner_text() if attribution.count() else None,
                            'license':label.inner_text() if label.count() else None,
                            'licenseUrl':license_link.get_attribute('href') if license_link.count() else None})
    row['sourceDisclosures'] = disclosures


def read_pack_and_filters(page, packet, row):
    before = financial(page)
    raw = page.evaluate('localStorage.getItem(LSKEY)')
    writes_before = main_writes(page)
    for zone in ('UTC', 'America/Sao_Paulo', 'Pacific/Auckland'):
        result = query(page, zone=zone)
        actual = sorted(({key: event[key] for key in ('id', 'title', 'date', 'sourceDate',
                         'precision', 'currency', 'impact')} for event in result['events']), key=lambda event:event['id'])
        assert actual == expected_events(packet, zone=zone), {'zone':zone, 'actual':actual}
    filtered = query(page, currencies=['GBP'], impacts=['low'])
    assert sorted(e['id'] for e in filtered['events']) == [e['id'] for e in expected_events(packet, ['GBP'], ['low'])]
    assert filtered['events'], 'Filter proof needs actual GBP low-impact source events'
    coverage = query(page)['coverage']
    assert any(c['currency']=='CHF' and c['status'] in ('pending','unavailable','partial','stale') for c in coverage), 'CHF pending coverage must remain explicit'
    panel = open_calendar(page)
    assert_dots(page, packet, CURRENCIES, ['high'])
    panel.locator('[data-calendar-action="filters"]').click()
    assert panel.locator('[data-calendar-currency]').count() == 5
    assert set(panel.locator('[data-calendar-currency]').evaluate_all('es=>es.map(e=>e.value)')) == set(CURRENCIES)
    for impact in ('medium','low','unclassified'):
        panel.locator('[data-calendar-filter="impacts"][value="'+impact+'"]').check()
    for currency in ('USD','JPY','NZD','CHF'):
        panel.locator('[data-calendar-filter="currencies"][value="'+currency+'"]').uncheck()
    row['filteredEconomicDayCounts'] = assert_dots(page, packet, ['GBP'], IMPACTS)
    chosen = expected_events(packet, ['GBP'], ['low'], start='2026-10-01', end='2026-10-31')[0]['date']
    panel.locator('[data-calendar-date="'+chosen+'"]').click()
    expected_ids = sorted(e['id'] for e in expected_events(packet, ['GBP'], IMPACTS, start=chosen, end=chosen))
    expect(panel.locator('[data-calendar-economic-id]')).to_have_count(len(expected_ids))
    assert sorted(panel.locator('[data-calendar-economic-id]').evaluate_all('es=>es.map(e=>e.dataset.calendarEconomicId)')) == expected_ids
    panel.locator('.calendar-header [data-calendar-action="info"]').click()
    assert 'GBP' in panel.locator('.calendar-source-list').inner_text()
    assert_source_disclosures(panel, packet, row)
    for currency in ('USD','JPY','NZD','CHF'):
        panel.locator('[data-calendar-filter="currencies"][value="'+currency+'"]').check()
    panel.locator('.calendar-header [data-calendar-action="info"]').click()
    panel.locator('[data-calendar-action="filters"]').click()
    panel.locator('[data-calendar-date="2026-10-23"]').click()
    panel.locator('[data-calendar-action="new"]').click()
    panel.locator('[name="title"]').fill('SYN distribution task')
    panel.locator('[name="notes"]').fill('Synthetic distribution persistence probe')
    assert financial(page) == before and page.evaluate('localStorage.getItem(LSKEY)') == raw, 'Calendar reads, filters or unsaved draft changed the confirmed document'
    assert main_writes(page) == writes_before, 'Calendar must not write the main document before explicit Save'
    extra = page.evaluate('key=>__calendarDistributionWrites.filter(w=>w.key!==key).map(w=>w.key)', MAIN_KEY)
    assert set(extra) <= {PREFS_KEY}, {'unexpectedAuxiliaryWrites':extra}
    row['readOnlyBeforeSave'] = {'mainWrites':0, 'preferenceWrites':len(extra), 'zones':['UTC','America/Sao_Paulo','Pacific/Auckland'], 'ffBootstrap':'nominal weekly fixture has zero events; monthly markers come from shipped source pack'}
    return before


def reload(page, row):
    page.reload(wait_until='load')
    wait_bootstrap(page)
    require_apis(page)
    page.evaluate('closeModal();window.__onbShown=true')
    row['reloads'] = row.get('reloads', 0) + 1


def crud(page, packet, row, base):
    panel = page.locator(PANEL)
    panel.locator('[data-calendar-action="save-form"]').click()
    expect(panel.locator('[name="title"]')).to_have_count(0)
    receipt = confirmed(page)
    items = page.evaluate('JPWAgenda.queries.snapshot().items')
    assert len(items) == 1 and items[0]['title'] == 'SYN distribution task', items
    item = items[0]
    assert item['date']=='2026-10-23' and item['kind']=='task' and item['allDay'] is True
    assert financial(page) == base, 'Agenda creation changed an adjacent financial family'
    row['created'] = {'id':item['id'], 'receipt':receipt, 'date':item['date']}
    reload(page,row)
    assert page.evaluate('JPWAgenda.queries.snapshot().items') == items, 'Reload changed task fields or identifier'
    prefs = page.evaluate('JSON.parse(localStorage.getItem("'+PREFS_KEY+'"))')
    assert set(prefs['currencies'])==set(CURRENCIES) and set(prefs['impacts'])==set(IMPACTS), prefs
    panel = open_calendar(page)
    expect(panel.locator('[data-calendar-personal-id="'+item['id']+'"]')).to_have_count(1)
    panel.locator('[data-calendar-personal-id="'+item['id']+'"] [data-calendar-action="edit"]').click()
    panel.locator('[name="title"]').fill('SYN distribution revised')
    panel.locator('[data-calendar-action="save-form"]').click()
    expect(panel.locator('[name="title"]')).to_have_count(0)
    confirmed(page)
    panel.locator('[data-calendar-personal-id="'+item['id']+'"] input[type="checkbox"]').check()
    page.wait_for_function('id=>!!JPWAgenda.queries.snapshot().items.find(i=>i.id===id)?.completedAt', arg=item['id'])
    confirmed(page)
    reload(page,row)
    changed = page.evaluate('JPWAgenda.queries.snapshot().items')
    assert len(changed)==1 and changed[0]['id']==item['id'] and changed[0]['title']=='SYN distribution revised' and changed[0]['completedAt'], changed
    assert financial(page)==base, 'Agenda edit or completion changed an adjacent financial family'
    panel = open_calendar(page)
    expect(panel.locator('[data-calendar-personal-id="'+item['id']+'"] input[type="checkbox"]')).to_be_checked()
    panel.locator('[data-calendar-personal-id="'+item['id']+'"] [data-calendar-action="edit"]').click()
    panel.locator('[data-calendar-action="remove-form"]').click()
    expect(panel.locator('[data-calendar-action="confirm-remove"]')).to_be_visible()
    assert len(page.evaluate('JPWAgenda.queries.snapshot().items'))==1, 'First Delete must request explicit confirmation'
    panel.locator('[data-calendar-action="confirm-remove"]').click()
    expect(panel.locator('[name="title"]')).to_have_count(0)
    confirmed(page)
    reload(page,row)
    assert page.evaluate('JPWAgenda.queries.snapshot().items')==[], 'Confirmed deletion did not survive reload'
    assert financial(page)==base, 'Agenda removal changed an adjacent financial family'
    row['crud'] = {'createdReloadId':item['id'], 'editedReloadSameId':True,
                   'completionReload':True, 'explicitDeleteReload':True,
                   'adjacentFinancialFamilies':'unchanged excluding writer governance metadata'}


def run_case(browser, root, url, name, packet, row):
    context = browser.new_context(viewport={'width':1280,'height':900},
                                  timezone_id='UTC', service_workers='allow' if name=='pwa-offline' else 'block')
    install_bootstrap(context)
    context.add_init_script('window.__onbShown=true;')
    page = context.new_page()
    page.clock.set_fixed_time(NOW)
    row.update(pageErrors=[], failedRequests=[], localFileRequests=[], serviceWorkerResponses=[], reloads=0)
    page.on('pageerror', lambda error:row['pageErrors'].append(str(error)))
    page.on('requestfailed', lambda request:row['failedRequests'].append({'url':request.url,'failure':request.failure}))
    page.on('request', lambda request:row['localFileRequests'].append(request.url) if request.url.startswith('file:') else None)
    page.on('response', lambda response:row['serviceWorkerResponses'].append(response.url) if response.from_service_worker else None)
    try:
        row['url'] = url
        page.goto(url, wait_until='load')
        page.wait_for_function('typeof S!=="undefined"&&typeof save==="function"&&window.JPWNavigation')
        row['knownBoot'] = True
        wait_bootstrap(page)
        require_apis(page)
        page.evaluate("""()=>{
          // This is a fresh origin with nominal feed fixtures. Preserve the
          // canonical bootstrap references so reload does not legitimately
          // re-create a missing FX daily-reference aggregate and audit entry.
          closeModal();S=structuredClone(S);S.onboarding.done=true;
          S.calendarDistributionProbe='SYN_CALENDAR_DISTRIBUTION';
          if(save()!==true)throw Error('HARNESS: synthetic confirmed base refused');
          JPWAgenda.commands.resetContext();
        }""")
        assert page.evaluate('jpWealthPersistenceLastResult().status') == 'CONFIRMED'
        if name=='pwa-offline':
            page.wait_for_function('navigator.serviceWorker.controller', timeout=30000)
            cached = page.evaluate("""async modules=>{
              await navigator.serviceWorker.ready;
              const keys=(await caches.keys()).filter(k=>k.startsWith('jp-wealth-'));
              const entries=[];for(const key of keys){const cache=await caches.open(key);entries.push({key,modules:await Promise.all(modules.map(async path=>{
                const response=await cache.match('/'+path);
                const sha256=response?[...new Uint8Array(await crypto.subtle.digest('SHA-256',await response.arrayBuffer()))].map(n=>n.toString(16).padStart(2,'0')).join(''):null;
                return {path,cached:!!response,sha256};
              }))});}return entries;
            }""", MODULES)
            assert any(all(module['cached'] for module in cache['modules']) for cache in cached), 'Actual PWA cache omits Calendar/Agenda runtime: '+json.dumps(cached)
            expected_hashes={path:hashlib.sha256((root/path).read_bytes()).hexdigest() for path in MODULES}
            assert any(all(module['sha256']==expected_hashes[module['path']] for module in cache['modules']) for cache in cached), 'PWA cached module bytes differ from current source'
            row['serviceWorker'] = {'controller':page.evaluate('navigator.serviceWorker.controller.scriptURL'), 'caches':cached}
            context.set_offline(True)
            reload(page,row)
            assert page.evaluate('navigator.onLine') is False
            assert page.evaluate('!!navigator.serviceWorker.controller')
            assert all(any(url.endswith('/'+path) for url in row['serviceWorkerResponses']) for path in ['index.html']+MODULES), 'Offline reload must actually receive document and runtime modules from the service worker'
            row['offlineReload'] = True
        instrument(page)
        base = read_pack_and_filters(page,packet,row)
        crud(page,packet,row,base)
        if name=='portable-file':
            assert set(row['localFileRequests'])=={url}, 'Standalone portable used a local dependency outside its single copied HTML: '+json.dumps(row['localFileRequests'])
        assert_fixture_requests(context)
        assert not row['pageErrors'], row['pageErrors']
        row['result'] = 'PASS'
    except Exception as error:
        product = isinstance(error,AssertionError) or isinstance(error,PlaywrightTimeout) and row.get('knownBoot')
        row.update(result='PRODUCT_FAIL' if product and not str(error).startswith('HARNESS:') else 'TEST_HARNESS_FAIL',
                   detail=str(error), traceback=traceback.format_exc())
    finally:
        row['publicNetworkUnexpected'] = context._jpw_bootstrap_unexpected
        context.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--case',choices=CASES,help='Run one named distribution; default runs all four')
    args=parser.parse_args();root=args.root.resolve();out=args.receipt.resolve();out.parent.mkdir(parents=True,exist_ok=True)
    started=time.monotonic();server=None
    report={'id':'CALENDAR-DISTRIBUTION-01','root':str(root),'startedUTC':datetime.now(timezone.utc).isoformat(),
            'cases':[],'requiredCases':list(CASES),'selectedCases':[args.case] if args.case else list(CASES),
            'limits':['Fresh synthetic Chromium contexts only; no real browser profiles or finance records.',
                      'Native Safari, physical touch, screen reader and human acceptance NOT_RUN.']}
    try:
        report['inputsBefore']=inventory(root);packet=source_packet(root)
        report['economicPack']={'events':len(packet['events']),'months':dict(Counter(e['date'][:7] for e in packet['events'])),
                                'sources':[s['id'] for s in packet['sources']],'generatedAt':packet.get('generatedAt')}
        report['git']={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
                       'branch':subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()}
        server=BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        with sync_playwright() as pw, tempfile.TemporaryDirectory(prefix='jpw-calendar-portable-') as folder:
            options=launch_options();report['runtime']={'python':os.sys.executable,'launch':options}
            browser=pw.chromium.launch(**options);report['runtime']['browserVersion']=browser.version
            for name in report['selectedCases']:
                row={'name':name,'result':'NOT_RUN'}
                if name=='portable-file':
                    isolated=Path(folder)/'calendar-portable.html';shutil.copyfile(root/PORTABLE,isolated)
                    contents=list(Path(folder).iterdir())
                    assert contents==[isolated], 'Portable fixture must contain exactly one HTML file'
                    row['isolatedInventory']=[{'name':isolated.name,'bytes':isolated.stat().st_size,
                                              'sha256':hashlib.sha256(isolated.read_bytes()).hexdigest()}]
                    assert row['isolatedInventory'][0]['sha256']==report['inputsBefore'][PORTABLE]['sha256']
                    url=isolated.as_uri()
                elif name=='modular-file':url=(root/'index.html').as_uri()
                else:url=f'http://127.0.0.1:{server.server_port}/index.html'
                run_case(browser,root,url,name,packet,row)
                report['cases'].append(row)
                print(json.dumps({key:row[key] for key in ('name','result','detail','reloads') if key in row},ensure_ascii=False),flush=True)
            browser.close()
    except Exception as error:
        report['harnessError']={'result':'ENVIRONMENT_ERROR' if 'Executable doesn\'t exist' in str(error) else 'TEST_HARNESS_FAIL',
                                'detail':str(error),'traceback':traceback.format_exc()}
    finally:
        if server:server.shutdown();server.server_close()
        report['inputsAfter']=inventory(root);report['sourceUnchanged']=report.get('inputsBefore')==report['inputsAfter']
        report['durationSeconds']=time.monotonic()-started
        report['counts']={status:sum(row['result']==status for row in report['cases'])
                          for status in ('PASS','PRODUCT_FAIL','TEST_HARNESS_FAIL','ENVIRONMENT_ERROR','NOT_RUN')}
        report['result']='PASS' if report['cases'] and report['sourceUnchanged'] and not report.get('harnessError') and all(row['result']=='PASS' for row in report['cases']) else report['harnessError']['result'] if report.get('harnessError') else 'PRODUCT_FAIL' if any(row['result']=='PRODUCT_FAIL' for row in report['cases']) else 'TEST_HARNESS_FAIL'
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(report['result']+' '+str(out),flush=True)
    return 0 if report['result']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())

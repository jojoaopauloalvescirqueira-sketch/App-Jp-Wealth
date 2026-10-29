#!/usr/bin/env python3
"""Calendar cache failure/retry in a synthetic real-browser profile.

Same oracle for --root baseline and candidate. No live feed; source scripts and
the three remaining weekly DOM consumers run with only the technical cache key faulted.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from datetime import datetime, timezone

from playwright.sync_api import expect, sync_playwright
from calendar_economic_table_contract import assert_values, assert_layout, collapsed


def load(root, name):
    spec = importlib.util.spec_from_file_location(name, root / 'tools' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SETUP = """() => {
  closeModal(); window.alert=()=>{};
  JPWNavigation.navigateLocal('research','calendar');
  JPWEcal.open(document.getElementById('gdNewsMoreBtn'));
  const get=Storage.prototype.getItem, set=Storage.prototype.setItem, remove=Storage.prototype.removeItem;
  const key='jpwealth.ui.ffNews.v1';
  const date=new Date(Date.now()+30*60*1000);
  const payload=label=>({version:1,generated_at:date.toISOString(),events:[
    {title:label+' USD',country:'USD',date:date.toISOString(),impact:'High',forecast:'1',previous:'2'},
    {title:label+' EUR',country:'EUR',date:date.toISOString(),impact:'High',forecast:'3',previous:'4'}]});
  window.__cacheTest={get,set,remove,key,readFault:false,writeFault:false,ops:[],old:payload('ANTIGO'),next:payload('NOVO')};
  Storage.prototype.getItem=function(k){
    if(this===localStorage && k===key && __cacheTest.readFault) throw new DOMException('synthetic read denied','SecurityError');
    return get.call(this,k);
  };
  Storage.prototype.setItem=function(k,v){
    __cacheTest.ops.push(['set',String(k)]);
    if(this===localStorage && k===key && __cacheTest.writeFault) throw new DOMException('synthetic quota','QuotaExceededError');
    return set.call(this,k,v);
  };
  Storage.prototype.removeItem=function(k){__cacheTest.ops.push(['remove',String(k)]);return remove.call(this,k);};
  Storage.prototype.clear=function(){throw new Error('clear forbidden in cache test');};
  set.call(localStorage,'closure-cache-unrelated','preserved');
  set.call(localStorage,key,JSON.stringify({fetchedAt:Date.now()-60*60*1000,payload:__cacheTest.old}));
  __cacheTest.ops=[];
  return __cacheTest.next;
}"""

SNAPSHOT = """() => {
  ffNewsRenderAll(); dashMacroRender();
  const text=selector=>document.querySelector(selector)?.textContent||'';
  const emptyText=selector=>{const el=document.querySelector(selector);return el && !el.hidden && getComputedStyle(el).display!=='none' ? el.textContent : '';};
  const c=__cacheTest;
  return {raw:c.get.call(localStorage,c.key),state:JSON.stringify(S),
    main:c.get.call(localStorage,'jpwealth_v9_state'),unrelated:c.get.call(localStorage,'closure-cache-unrelated'),
    source:c.get.call(localStorage,'jpwealth.ui.ffNews.sourceUrl'),ops:c.ops.slice(),
    widget:text('#gdNewsStatus'),widgetEvents:text('#gdNewsList'),
    modal:text('#ecalFreshness')+' '+emptyText('#ecalEmpty'),
    modalEvents:text('#ecalBody'),monthly:document.querySelector('#execEcal')?.innerHTML||'',dashboard:text('[data-dm-card="research"]'),
    emptyNodes:['#ecalEmpty'].map(selector=>{
      const el=document.querySelector(selector);return {selector,hidden:el.hidden,display:getComputedStyle(el).display,text:el.textContent};}),
    dataAvailable:ecalEvents()!==null,
    filters:[ecalState.filter],monthlyIdentity:document.getElementById('execEcal')===c.monthlyHost,
    monthlySelection:document.querySelector('#execEcal [data-calendar-date][aria-selected="true"]')?.dataset.calendarDate,
    monthlyMonth:document.querySelector('#execEcal .calendar-month-label')?.textContent};
}"""


def public_fixture(label):
    currencies=['USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY']
    stamp='2026-10-28T20:00:00Z'
    sources=[dict(id='ff-'+c,name='Forex Factory · '+c,currency=c,url='https://www.forexfactory.com/calendar',timeZone='America/New_York',provider='forexfactory') for c in currencies]
    events=[]
    for currency,impact in [('CAD','high'),('USD','high'),('EUR','medium'),('GBP','low'),('JPY','unclassified')]:
        events.append(dict(id='SYN-'+label+'-'+currency,title='SYN FF '+label+' '+currency,currency=currency,
            impact=impact,date='2026-10-28',at='2026-10-28T18:00:00Z',precision='instant',
            sourceId='ff-'+currency,sourceUrl='https://www.forexfactory.com/calendar',timeZone='America/New_York',
            forecast='0' if currency=='CAD' else '−0.5%' if currency=='USD' else '',previous='0.0%' if currency=='CAD' else '1.2M' if currency=='USD' else '',
            provider='forexfactory',providerImpact={'high':'High','medium':'Medium','low':'Low','unclassified':'Holiday'}[impact],impactOrigin='provider',status='scheduled',
            reviewedAt=stamp,observedAt=stamp,timeConfirmed=False,observationStatus='present',snapshotId='SYN-'+label))
    coverage=[dict(sourceId='ff-'+c,currency=c,month='2026-10',from_='2026-10-25',to='2026-10-31',
                  status='partial',reviewedAt=stamp,validUntil='2026-10-28T22:00:00Z',scope='weekly-snapshot',reason='Synthetic week only') for c in currencies]
    for row in coverage:row['from']=row.pop('from_')
    return dict(schemaVersion=2,currencies=currencies,sources=sources,events=events,coverage=coverage,
                collectedAt=stamp,packagePublishedAt=stamp,sourcePublishedAt=None,currentWeekFrom='2026-10-25',updatedAt=stamp)


def shared_calendar_pipeline(browser, bootstrap, url, width, theme):
    context=browser.new_context(viewport={'width':width,'height':900},timezone_id='America/Sao_Paulo',service_workers='block')
    bootstrap.install_bootstrap(context);context.add_init_script('window.__onbShown=true')
    mode={'status':200,'payload':{'version':1,'generated_at':'2026-10-28T19:00:00Z','events':[]},'calls':0}
    def respond(route):
        mode['calls']+=1;route.fulfill(status=mode['status'],content_type='application/json',body=json.dumps(mode['payload']))
    context.route(bootstrap.FEED_URL,respond)
    try:
        page=context.new_page();page.clock.set_fixed_time(datetime(2026,10,28,20,5,tzinfo=timezone.utc))
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url,wait_until='load');bootstrap.wait_bootstrap(page)
        page.evaluate("theme=>{closeModal();window.__onbShown=true;document.documentElement.dataset.theme=theme;JPWNavigation.navigate('tools-calendar')}",theme)
        panel=page.locator('#execEcal .calendar-panel');expect(panel).to_be_visible()
        page.evaluate('window.__economicPipelineHost=document.getElementById("execEcal")')
        before=page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY)})')
        cell=panel.locator('[data-calendar-date="2026-10-28"]');cell.click()
        selected=cell.get_attribute('data-calendar-date');month=panel.locator('.calendar-month-label').inner_text()
        panel.locator('.calendar-header [data-calendar-action="info"]').click()
        mode['payload']=public_fixture('primeira');mode['calls']=0
        panel.locator('[data-calendar-action="refresh-economic"]').click()
        page.wait_for_function("window.JPWCalendarFeed.snapshot()?.payload.schemaVersion===2 && !ffNewsInFlight")
        expect(panel.locator('.calendar-event-title').filter(has_text='SYN FF primeira CAD')).to_have_count(1)
        # Real v2 producer -> domain -> both table values; zero is a string fact.
        table_events=[e for e in mode['payload']['events'] if e['impact']=='high']
        assert_values(panel,table_events);assert_layout(panel);collapsed(panel)
        expect(panel.locator('.calendar-event-title').filter(has_text='SYN FF primeira USD')).to_have_count(1)
        assert mode['calls']==1,mode['calls']
        assert not panel.locator('.calendar-event-title').filter(has_text='SYN FF primeira EUR').count()
        # Approved table contract: provenance starts collapsed. Verify the
        # actual source for each synthetic CAD/USD observation through its i,
        # preserving both provenances and both visible pending-time warnings.
        provenance=[]
        for event in table_events:
            event_row=panel.locator('[data-calendar-economic-id='+json.dumps(event['id'])+']')
            expect(event_row).to_have_count(1)
            toggle=event_row.locator('[data-calendar-action="economic-detail"]')
            expect(toggle).to_have_attribute('aria-expanded','false')
            detail_id=toggle.get_attribute('aria-controls')
            assert detail_id, 'Each event must control its own provenance detail'
            detail=panel.locator('[id='+json.dumps(detail_id)+']')
            expect(detail).not_to_be_visible()
            expect(event_row.locator('.calendar-event-warning')).to_be_visible()
            expect(event_row.locator('.calendar-event-warning')).to_contain_text('Horário a confirmar.')
            toggle.click()
            expect(detail).to_be_visible()
            expect(panel.locator('[data-calendar-action="economic-detail"][aria-expanded="true"]')).to_have_count(1)
            source=detail.get_by_role('link',name='Fonte: Forex Factory',exact=True)
            expect(source).to_have_count(1);expect(source).to_have_attribute('href',event['sourceUrl'])
            expect(detail).to_contain_text('Horário original:')
            expect(detail).to_contain_text(event['timeZone'])
            provenance.append({'event':event['id'],'currency':event['currency'],'sourceUrl':source.get_attribute('href')})
            toggle.click()
            expect(toggle).to_have_attribute('aria-expanded','false');expect(detail).not_to_be_visible()
        assert {row['currency'] for row in provenance}=={'CAD','USD'}, provenance
        collapsed(panel)
        assert set(page.evaluate('ffNewsReadCache().events.map(e=>e.country)'))=={'USD'},'Weekly view must retain High/four-currency cut'
        assert cell.locator('.calendar-economic-dot').count()==1
        panel.locator('.calendar-header [data-calendar-action="info"]').click()
        panel.locator('[data-calendar-action="new"]').click()
        title=panel.locator('[name="title"]');title.fill('SYN rascunho durante notícia')
        title.evaluate('node=>{node.focus();node.setSelectionRange(4,10)}')
        mode['payload']=public_fixture('segunda');mode['calls']=0
        page.evaluate('async()=>{await Promise.all([JPWCalendarFeed.refresh(true),JPWCalendarFeed.refresh(true)])}')
        assert mode['calls']==1,mode['calls']
        expect(title).to_be_focused();expect(title).to_have_value('SYN rascunho durante notícia')
        assert title.evaluate('node=>[node.selectionStart,node.selectionEnd]')==[4,10]
        panel.locator('[data-calendar-action="cancel-form"]').click()
        expect(panel.locator('.calendar-event-title').filter(has_text='SYN FF segunda CAD')).to_have_count(1)
        assert panel.locator('.calendar-month-label').inner_text()==month
        assert panel.locator('[data-calendar-date][aria-selected="true"]').get_attribute('data-calendar-date')==selected
        assert page.evaluate('document.getElementById("execEcal")===__economicPipelineHost')
        saved=page.evaluate('localStorage.getItem("jpwealth.ui.ffNews.v1")');mode['status']=500
        page.evaluate('async()=>{await JPWCalendarFeed.refresh(true)}')
        assert page.evaluate('localStorage.getItem("jpwealth.ui.ffNews.v1")')==saved
        expect(panel.locator('.calendar-event-title').filter(has_text='SYN FF segunda CAD')).to_have_count(1)
        panel.locator('.calendar-header [data-calendar-action="info"]').click()
        expect(panel.locator('.calendar-info')).to_contain_text('Não foi possível atualizar')
        assert page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY)})')==before
        assert not errors,errors
        return {'nineCurrencyTransport':True,'CADAndUSDHighVisible':True,'mediumExcluded':True,'redDot':True,
                'perEventProvenance':provenance,'bothPendingTimeWarningsVisible':True,'sourcesInitiallyCollapsed':True,
                'legacyFourHighPreserved':True,'oneFetchForConcurrentRefreshes':True,'draftFocusCursorPreserved':True,
                'monthSelectionHostPreserved':True,'failedRefreshPreservesLastValid':True,'financialUnchanged':True}
    finally:context.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--artifact',type=Path,required=True)
    args=parser.parse_args(); root=args.root.resolve()
    research=load(root,'research_navigation_test')
    bootstrap=load(root,'browser_bootstrap_fixture')
    sources=['src/js/40-app/15-ff-news.js','src/js/40-app/16-monthly-economic-data.js','src/js/40-app/19-calendar-agenda.js','src/js/40-app/17-economic-calendar.js','src/js/20-ui/25-dash-macro.js','index.html','src/styles/app.css','tools/browser_bootstrap_fixture.py']
    result={'root':str(root),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'sources':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in sources},'checks':[],'cases':[]}

    def check(name,passed,detail=None):
        result['checks'].append({'name':name,'status':'PASS' if passed else 'PRODUCT_FAIL','detail':detail})

    def warnings(label,snap,kind):
        for area in ['widget','modal','dashboard']:
            text=snap[area].lower()
            check(label+' '+area+' storage warning','armazenamento' in text and kind in text,snap[area])

    server,url=research.serve()
    try:
        with sync_playwright() as pw:
            browser=research.launch_browser(pw)
            try:
                for width,theme in [(1440,'light'),(390,'dark')]:
                    for case in ['quota-old','quota-empty','read-denied','invalid-json','invalid-envelope','http-invalid','http-error','fresh-and-inflight']:
                        label=f'{width}-{theme}/{case}'
                        context=browser.new_context(viewport={'width':width,'height':900},service_workers='block')
                        bootstrap.install_bootstrap(context)
                        context.add_init_script('window.__onbShown=true;')
                        page=context.new_page(); errors=[]
                        page.on('pageerror',lambda error:errors.append(str(error)))
                        mode={'status':200,'payload':{'version':1,'generated_at':'2026-09-10T00:00:00Z','events':[]},'calls':0}
                        def respond(route):
                            mode['calls']+=1
                            route.fulfill(status=mode['status'],content_type='application/json',body=json.dumps(mode['payload']))
                        context.route(bootstrap.FEED_URL,respond)
                        try:
                            page.goto(url,wait_until='load');bootstrap.wait_bootstrap(page)
                            mode['payload']=page.evaluate(SETUP)
                            page.evaluate('(theme)=>document.documentElement.setAttribute("data-theme",theme)',theme)
                            page.locator('#ecalFilters [data-ecal-cur="USD"]').click()
                            page.evaluate("() => JPWCalendar.mountWorkspace()")
                            page.evaluate('window.__cacheTest.monthlyHost=document.getElementById("execEcal")')
                            before=page.evaluate(SNAPSHOT); mode['calls']=0
                            if case=='quota-empty':
                                page.evaluate('() => __cacheTest.remove.call(localStorage,__cacheTest.key)')
                            if case.startswith('quota'):
                                page.evaluate('() => {__cacheTest.writeFault=true;ffNewsFetch(true);}')
                            elif case=='read-denied':
                                page.evaluate('() => {__cacheTest.readFault=true;}')
                            elif case in ['invalid-json','invalid-envelope']:
                                invalid='{' if case=='invalid-json' else json.dumps({'fetchedAt':1,'payload':{'version':99,'events':[]}})
                                page.evaluate('(raw)=>__cacheTest.set.call(localStorage,__cacheTest.key,raw)',invalid)
                            elif case.startswith('http'):
                                mode['status']=500 if case=='http-error' else 200
                                mode['payload']={'invalid':'synthetic'}
                                page.evaluate('() => ffNewsFetch(true)')
                            else:
                                page.evaluate('() => __cacheTest.set.call(localStorage,__cacheTest.key,JSON.stringify({fetchedAt:Date.now(),payload:__cacheTest.old}))')
                                page.evaluate('() => {ffNewsFetch(false);ffNewsFetch(false);}')
                                check(label+' fresh cache avoids fetch',mode['calls']==0,mode['calls'])
                                page.evaluate('() => {ffNewsFetch(true);ffNewsFetch(true);}')
                            page.wait_for_function('() => !ffNewsInFlight')
                            after=page.evaluate(SNAPSHOT)
                            if case.startswith('quota'):
                                warnings(label,after,'não atualizado')
                                check(label+' preserved rejected cache',after['raw']==(None if case=='quota-empty' else before['raw']),after['raw'])
                                check(label+' no new payload in views',all('NOVO' not in after[x] for x in ['widgetEvents','modalEvents','dashboard']))
                                check(label+' prior payload remains visible' if case=='quota-old' else label+' absence not fabricated',
                                  all('ANTIGO' in after[x] for x in ['widgetEvents','modalEvents','dashboard']) if case=='quota-old' else not after['dataAvailable'])
                            elif case=='read-denied':
                                warnings(label,after,'ler')
                                check(label+' protected bytes after denied read',after['raw']==before['raw'])
                                check(label+' no invented readable data',not after['dataAvailable'])
                            elif case.startswith('invalid'):
                                check(label+' invalid bytes preserved on read',after['raw']==invalid)
                                check(label+' unavailable distinct from empty',not after['dataAvailable'] and 'Sem dados' in after['modal'] and 'dados ainda não carregados' in after['dashboard'])
                            elif case.startswith('http'):
                                check(label+' old bytes survive provider failure',after['raw']==before['raw'])
                                check(label+' provider failure shown in all consumers',all('Sem conexão' in after[key] for key in ['widget','modal','dashboard']),{key:after[key] for key in ['widget','modal','dashboard']})
                            else:
                                check(label+' duplicate inflight calls coalesced',mode['calls']==1,mode['calls'])
                            check(label+' filter state preserved',after['filters']==['USD'],after['filters'])
                            check(label+' shared FF preserves monthly host and selection',after['monthlyIdentity'] and after['monthlySelection']==before['monthlySelection'] and after['monthlyMonth']==before['monthlyMonth'])
                            check(label+' financial and unrelated state preserved',all(after[x]==before[x] for x in ['state','main','unrelated','source']))
                            check(label+' writes limited to cache',all(x[1]=='jpwealth.ui.ffNews.v1' for x in after['ops']),after['ops'])
                            if case=='quota-old':
                                bounds=page.locator('#ecalFreshness').evaluate('(el)=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,width:innerWidth,overflow:el.scrollWidth>el.clientWidth+1};}')
                                check(label+' modal warning fits viewport',bounds['left']>=0 and bounds['right']<=width and not bounds['overflow'],bounds)
                                picture=args.artifact.with_name(args.artifact.stem+f'-{width}-{theme}.png')
                                page.screenshot(path=str(picture));result.setdefault('screenshots',[]).append(str(picture))
                            # Real existing retry control, after removing only synthetic faults.
                            page.keyboard.press('Escape')
                            page.evaluate('() => {__cacheTest.readFault=false;__cacheTest.writeFault=false;JPWNavigation.navigate("forex-overview");}')
                            mode['status']=200; mode['payload']=page.evaluate('() => __cacheTest.next')
                            page.locator('#gdNewsRefreshBtn').click()
                            page.wait_for_function('() => !ffNewsInFlight')
                            page.evaluate('() => {JPWNavigation.navigateLocal("research","calendar");JPWEcal.open(document.getElementById("gdNewsMoreBtn"));}')
                            page.wait_for_function('() => !ffNewsInFlight')
                            recovered=page.evaluate(SNAPSHOT)
                            check(label+' retry stores new payload',json.loads(recovered['raw'])['payload']==mode['payload'])
                            check(label+' retry all consumers recover',all('armazenamento' not in recovered[x].lower() for x in ['widget','modal','dashboard']) and all('NOVO' in recovered[x] for x in ['widgetEvents','modalEvents','dashboard']))
                            check(label+' retry protects financial state',all(recovered[x]==before[x] for x in ['state','main','unrelated','source']))
                            check(label+' no browser exceptions',not errors,errors)
                            bootstrap.assert_fixture_requests(context)
                            result['cases'].append({'case':label,'observed':after,'recovered':recovered,'feed_calls':mode['calls']})
                        finally:context.close()
                for width,theme in [(1440,'light'),(390,'dark')]:
                    label=f'{width}-{theme}/shared-v2-pipeline'
                    try:
                        details=shared_calendar_pipeline(browser,bootstrap,url,width,theme)
                        check(label,True,details);result['cases'].append({'case':label,'observed':details})
                    except AssertionError as error:
                        check(label,False,str(error))
            finally:browser.close()
    except Exception as exc:
        result['environment_error']={'type':type(exc).__name__,'message':str(exc)}
    finally:server.shutdown();server.server_close()
    result['counts']={s:sum(x['status']==s for x in result['checks']) for s in ['PASS','PRODUCT_FAIL']}
    args.artifact.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'counts':result['counts'],'environment_error':result.get('environment_error'),'artifact':str(args.artifact)},ensure_ascii=False))
    return 2 if result.get('environment_error') else 1 if result['counts']['PRODUCT_FAIL'] else 0


if __name__=='__main__':raise SystemExit(main())

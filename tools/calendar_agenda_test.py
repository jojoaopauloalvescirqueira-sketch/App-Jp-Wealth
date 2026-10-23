#!/usr/bin/env python3
"""CALENDAR-AGENDA-UI-01: approved calendar UI in synthetic browser contexts.
Real product APIs/writers are exercised where loaded; no operator profile is used.
"""
import argparse, functools, json, os, re, threading, traceback
from datetime import datetime, timezone
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from dashboard_macro_test import launch_browser
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass

def run(page, width, theme):
    assert page.evaluate("!!window.JPWCalendar"), 'Approved calendar UI API is absent'
    assert page.evaluate("!!window.JPWAgenda && !!window.JPWEconomicCalendar"), 'Required agenda/feed APIs are absent'
    page.evaluate("closeModal(); window.__onbShown=true; document.documentElement.dataset.theme='"+theme+"'")
    page.locator('#headerCalendarBtn').click()
    expect(page.locator('#calendarDialog')).to_be_visible()
    panel=page.locator('#calendarDialog .calendar-panel')
    assert panel.count()==1
    cells=panel.locator('[data-calendar-date]')
    assert cells.count() in (28,35,42), cells.count()
    assert panel.locator('[data-calendar-date][tabindex="0"]').count()==1
    active=panel.locator('[data-calendar-date][tabindex="0"]'); date=active.get_attribute('data-calendar-date')
    active.focus(); page.keyboard.press('ArrowRight')
    assert page.locator(':focus').get_attribute('data-calendar-date')!=date
    for key,expected in [('ArrowLeft','2026-10-23'),('ArrowDown','2026-10-30'),('ArrowUp','2026-10-23'),('Home','2026-10-19'),('End','2026-10-25'),('PageDown','2026-11-25'),('PageUp','2026-10-25'),('ArrowLeft','2026-10-24')]:
        page.keyboard.press(key);assert page.locator(':focus').get_attribute('data-calendar-date')==expected,(key,page.locator(':focus').get_attribute('data-calendar-date'))
    page.keyboard.press('Enter')
    assert page.locator('#calendarDialog').evaluate("e=>e.matches(':modal')")
    assert panel.locator('[data-calendar-date][aria-selected="true"]').count()==1
    geometry=panel.evaluate("e=>({w:e.getBoundingClientRect().width,sw:e.scrollWidth,cw:e.clientWidth})")
    assert geometry['sw']<=geometry['cw']+1, geometry
    assert geometry['w']<=min(760,width)+1, geometry
    bounds=page.locator('#calendarDialog').bounding_box();assert bounds['x']>=0 and bounds['y']>=0 and bounds['x']+bounds['width']<=width+1,bounds
    if width>700:
        anchor=page.locator('#headerCalendarBtn').bounding_box()
        assert abs(bounds['y']-anchor['y']-anchor['height']-12)<=1,(bounds,anchor)
        assert abs(bounds['x']+bounds['width']-anchor['x']-anchor['width'])<=1,(bounds,anchor)
    if width==320:
        assert cells.first.bounding_box()['width']>=44, cells.first.bounding_box()
    panel.locator('[data-calendar-action="new"]').click()
    panel.locator('[name="title"]').fill('SYN tarefa preservada')
    panel.locator('[name="notes"]').fill('Rascunho sintético')
    before=page.evaluate('localStorage.getItem(LSKEY)')
    page.keyboard.press('Escape')
    assert not page.locator('#calendarDialog').evaluate('e=>e.open')
    page.locator('#headerCalendarBtn').click()
    expect(panel.locator('[name="title"]')).to_have_value('SYN tarefa preservada')
    page.mouse.click(2,2)
    assert not page.locator('#calendarDialog').evaluate('e=>e.open')
    expect(page.locator('#headerCalendarBtn')).to_be_focused()
    page.locator('#headerCalendarBtn').click()
    expect(panel.locator('[name="title"]')).to_have_value('SYN tarefa preservada')
    assert page.evaluate('localStorage.getItem(LSKEY)')==before, 'Dismissal must not save a form'
    panel.locator('[data-calendar-action="cancel-form"]').click()
    assert panel.locator('[name="title"]').count()==0
    panel.locator('[data-calendar-action="filters"]').click()
    assert panel.locator('[data-calendar-currency]').count()==5
    assert set(panel.locator('[data-calendar-currency]').evaluate_all('es=>es.map(e=>e.value)'))=={'USD','GBP','JPY','NZD','CHF'}
    panel.locator('[data-calendar-action="filters"]').click()
    page.keyboard.press('Escape')
    page.locator('#headerNotificationsBtn').click()
    assert page.evaluate('JPWCalendar.open()') is False, 'Calendar must refuse overlay stacking'
    page.keyboard.press('Escape')
    if page.evaluate('!!window.JPWAgenda'):
        page.locator('#headerCalendarBtn').click()
        panel.locator('[data-calendar-action="new"]').click()
        panel.locator('[name="title"]').fill('SYN tarefa confirmada')
        panel.locator('[data-calendar-action="save-form"]').click()
        expect(panel.locator('[name="title"]')).to_have_count(0)
        assert any(i['title']=='SYN tarefa confirmada' for i in page.evaluate('JPWAgenda.queries.snapshot().items'))
        row=panel.locator('[data-calendar-personal-id]').filter(has_text='SYN tarefa confirmada')
        row.locator('input[type=checkbox]').check()
        assert any(i.get('completedAt') for i in page.evaluate('JPWAgenda.queries.snapshot().items') if i['title']=='SYN tarefa confirmada')
        edit=row.locator('[data-calendar-action="edit"]');edit.focus()
        page.evaluate("JPWCalendar.refresh()")
        expect(edit).to_be_focused()
        edit.click()
        title=panel.locator('[name="title"]');title.fill('SYN edição preservada')
        title.evaluate('e=>{e.focus();e.setSelectionRange(4,10)}')
        page.evaluate("JPWCalendar.refresh()")
        expect(title).to_be_focused()
        assert title.evaluate('e=>[e.selectionStart,e.selectionEnd]')==[4,10]
        draft=page.evaluate("jpwWorkspaceDrafts().find(d=>d.provider==='calendar-agenda')")
        assert draft and 'token' not in json.loads(draft['text']) and 'token' not in draft
        page.evaluate("""()=>{const p=JPWAgenda.queries.prepare({id:null});const r=JPWAgenda.commands.save({input:{kind:'task',title:'SYN mudança externa',notes:'',date:'2026-10-24',allDay:true,startTime:'',endDate:'2026-10-24',endTime:'',timeZone:'UTC'},token:p.token});if(!r.ok)throw Error(JSON.stringify(r));}""")
        expect(title).to_have_value('SYN edição preservada')
        panel.locator('[data-calendar-action="save-form"]').click()
        expect(panel.locator('[data-calendar-action="refresh-revision"]')).to_be_visible()
        expect(title).to_have_value('SYN edição preservada')
        panel.locator('[data-calendar-action="refresh-revision"]').click()
        panel.locator('[data-calendar-action="save-form"]').click()
        expect(panel.locator('[name="title"]')).to_have_count(0)
        panel.locator('[data-calendar-action="new"]').click()
        panel.locator('[name="kind"]').select_option('appointment')
        panel.locator('[name="allDay"]').uncheck()
        panel.locator('[name="title"]').fill('SYN hora ambígua')
        panel.locator('[name="date"]').fill('2026-11-01')
        panel.locator('[name="startTime"]').fill('01:30')
        panel.locator('[name="endDate"]').fill('2026-11-01')
        panel.locator('[name="endTime"]').fill('02:30')
        panel.locator('[name="timeZone"]').fill('America/New_York')
        before=page.evaluate('localStorage.getItem(LSKEY)')
        panel.locator('[data-calendar-action="save-form"]').click()
        choice=panel.locator('[name="startAtChoice"]')
        expect(choice).to_be_visible();expect(choice).to_have_value('')
        assert page.evaluate('localStorage.getItem(LSKEY)')==before
        choice.select_option(index=1)
        panel.locator('[data-calendar-action="save-form"]').click()
        expect(panel.locator('[name="title"]')).to_have_count(0)
        # The domain ends appointments exclusively; midnight must not mark tomorrow.
        panel.locator('[data-calendar-action="new"]').click()
        panel.locator('[name="kind"]').select_option('appointment')
        panel.locator('[name="allDay"]').uncheck()
        panel.locator('[name="title"]').fill('SYN termina à meia-noite')
        panel.locator('[name="date"]').fill('2026-10-24')
        panel.locator('[name="startTime"]').fill('23:00')
        panel.locator('[name="endDate"]').fill('2026-10-25')
        panel.locator('[name="endTime"]').fill('00:00')
        panel.locator('[name="timeZone"]').fill('America/Sao_Paulo')
        panel.locator('[data-calendar-action="save-form"]').click()
        expect(panel.locator('[name="title"]')).to_have_count(0)
        panel.locator('[data-calendar-date="2026-10-24"]').click()
        expect(panel.locator('[data-calendar-personal-id]').filter(has_text='SYN termina à meia-noite')).to_have_count(1)
        panel.locator('[data-calendar-date="2026-10-25"]').click()
        expect(panel.locator('[data-calendar-personal-id]').filter(has_text='SYN termina à meia-noite')).to_have_count(0)
    icons=panel.locator('.calendar-icon-button').evaluate_all("es=>es.map(e=>{const a=e.getBoundingClientRect(),b=e.querySelector('svg').getBoundingClientRect();return {w:a.width,h:a.height,dx:Math.abs(a.x+a.width/2-b.x-b.width/2),dy:Math.abs(a.y+a.height/2-b.y-b.height/2)}})")
    assert all(i['w']>=44 and i['h']>=44 and i['dx']<=2 and i['dy']<=2 for i in icons),icons
    if page.evaluate('!!window.JPWEconomicCalendar'):
        marker=panel.locator('[data-calendar-date]:has(.calendar-economic-dot)').first
        if marker.count():
            date=marker.get_attribute('data-calendar-date');marker.click()
            panel.locator('[data-calendar-action="new"]').click()
            panel.locator('[name="title"]').fill('SYN dois marcadores')
            panel.locator('[data-calendar-action="save-form"]').click()
            expect(panel.locator('[name="title"]')).to_have_count(0)
            marker=panel.locator('[data-calendar-date="'+date+'"]')
            dot=marker.locator('.calendar-economic-dot').bounding_box();number=marker.locator('.calendar-day-number').bounding_box()
            assert abs(dot['x']+dot['width']/2-number['x']-number['width']/2)<=1
            assert marker.locator('.calendar-personal-dot').count()==1
            assert 'evento' in marker.get_attribute('aria-label') and any(c.isdigit() for c in marker.get_attribute('aria-label'))
    return {**geometry,'icons':icons,'workflows':['keyboard','dismiss-draft','filters','overlay-guard','task-save-complete','focus-cursor-refresh','stale-review','explicit-DST-choice','exclusive-midnight']}

def calendar_packet(context, adjacent=False):
    from monthly_economic_feed_test import event, fixture
    packet=fixture([event('SYN-high-1',at='2026-10-23T15:00:00Z'),event('SYN-high-2',at='2026-10-23T16:00:00Z'),event('SYN-medium',at='2026-10-24T16:00:00Z',impact='medium'),event('SYN-dateonly',date='2026-10-25',precision='date')])
    if adjacent:
        packet['events'] += [event('SYN-previous-month',date='2026-09-28',precision='date'),event('SYN-next-month',date='2026-11-01',precision='date')]
    packet['sources'][0].update(attribution='Source: Synthetic fixture; adapted by JP Wealth',license='Synthetic terms',licenseUrl='https://example.org/terms')
    packet['coverage'] += [{'currency':c,'sourceId':None,'month':'2026-10','from':'2026-10-01','to':'2026-10-31','status':'pending','reviewedAt':None,'reason':'Synthetic unpublished currency month.'} for c in ['GBP','JPY','NZD','CHF']]
    if adjacent:
        for row in packet['coverage']:
            if row['currency']=='GBP':row.update(status='confirmed',reason='Synthetic confirmed October; September is not covered.')
    source=(ROOT/'src/js/40-app/16-monthly-economic-data.js').read_text()
    source=re.sub(r'/\* JPW_MONTHLY_DATA_BEGIN \*/[\s\S]*?/\* JPW_MONTHLY_DATA_END \*/','/* JPW_MONTHLY_DATA_BEGIN */'+json.dumps(packet)+'/* JPW_MONTHLY_DATA_END */',source)
    context.route('**/src/js/40-app/16-monthly-economic-data.js',lambda route:route.fulfill(status=200,content_type='application/javascript',body=source))

def controlled_economic_query(page):
    page.evaluate("""()=>{closeModal();window.__onbShown=true;
      const api=window.JPWEconomicCalendar;window.__calendarQuery={fail:false,calls:[]};
      window.JPWEconomicCalendar={...api,queryRange(query){__calendarQuery.calls.push(structuredClone(query));if(__calendarQuery.fail)throw new Error('SYN economic query failure');return api.queryRange(query)}};
    }""")
    return page.evaluate('({state:JSON.stringify(S),document:localStorage.getItem(LSKEY)})')

def adjacent_selection(page, range_only=False):
    before=controlled_economic_query(page)
    page.locator('#headerCalendarBtn').click();panel=page.locator('#calendarDialog .calendar-panel')
    expect(panel.locator('[data-calendar-date="2026-10-23"] .calendar-economic-dot')).to_have_count(1)
    month=panel.locator('.calendar-month-label').inner_text()
    if range_only:
        queries=page.evaluate('__calendarQuery.calls')
        assert queries[-1]['from']=='2026-09-28' and queries[-1]['to']=='2026-11-01',queries
        for date in ['2026-09-28','2026-11-01']:
            expect(panel.locator(f'[data-calendar-date="{date}"] .calendar-economic-dot')).to_have_count(1)
    date='2026-09-28'
    cell=panel.locator(f'[data-calendar-date="{date}"]');cell.click()
    assert panel.locator('.calendar-month-label').inner_text()==month,'Selecting an adjacent day must not navigate the visible month'
    expect(panel.locator(f'[data-calendar-date="{date}"][aria-selected="true"][tabindex="0"]')).to_be_focused()
    assert panel.locator('[data-calendar-date][tabindex="0"]').count()==1
    if range_only:
        expect(panel.locator('[data-calendar-economic-id="SYN-previous-month"]')).to_have_count(1)
        # October coverage cannot stand in for an adjacent selected September day.
        panel.locator('[data-calendar-action="filters"]').click()
        for currency in ['USD','JPY','NZD','CHF']:
            panel.locator(f'[data-calendar-currency="{currency}"]').uncheck()
        page.evaluate('JPWCalendar.refresh()')
        expect(panel.locator('.calendar-agenda .calendar-coverage-note')).to_contain_text('confirmação')
        panel.locator('.calendar-header [data-calendar-action="info"]').click()
        assert 'setembro de 2026' in panel.locator('.calendar-info').inner_text()
        assert 'Indisponível' in panel.locator('.calendar-source-list').inner_text()
        assert 'Confirmada' not in panel.locator('.calendar-source-list').inner_text()
    after=page.evaluate('({state:JSON.stringify(S),document:localStorage.getItem(LSKEY)})')
    assert after==before,'Adjacent selection and filters must not write financial state'
    return {'visible_month':'October retained','selected_adjacent':date,'single_roving_focus':True,'displayed_range':'2026-09-28 through 2026-11-01' if range_only else 'selection only','read_only':True}

def feed_recovery(page):
    before=controlled_economic_query(page)
    page.locator('#headerCalendarBtn').click();panel=page.locator('#calendarDialog .calendar-panel')
    expect(panel.locator('[data-calendar-economic-id="SYN-high-1"]')).to_have_count(1)
    page.evaluate('__calendarQuery.fail=true;JPWCalendar.refresh()')
    expect(panel.locator('[data-calendar-economic-id="SYN-high-1"]')).to_have_count(1)
    expect(panel.locator('.calendar-agenda .calendar-coverage-note')).to_contain_text('desatualizados')
    panel.locator('.calendar-header [data-calendar-action="info"]').click()
    info=panel.locator('.calendar-info')
    assert 'Atualização da fonte:' in info.inner_text(),'Last valid source revision must survive query failure'
    assert 'Não foi possível' in info.inner_text() and 'desatualizados' in info.inner_text()
    expect(info.locator('[data-calendar-source]')).to_have_count(1)
    # No successful data exists for GBP-only: it must not inherit USD events or revision.
    panel.locator('[data-calendar-action="filters"]').click()
    for currency in ['USD','JPY','NZD','CHF']:
        panel.locator(f'[data-calendar-currency="{currency}"]').uncheck()
    page.evaluate('JPWCalendar.refresh()')
    expect(panel.locator('[data-calendar-economic-id]')).to_have_count(0)
    assert panel.locator('.calendar-economic-dot').count()==0
    expect(panel.locator('.calendar-agenda .calendar-coverage-note')).to_contain_text('Não foi possível')
    assert 'Nenhum item' not in panel.locator('.calendar-agenda').inner_text(),'A failed query must not announce absence'
    assert 'Atualização da fonte:' not in info.inner_text(),'A new failed context must not inherit another context revision'
    # Returning to the exact original filter recovers its prior values as stale.
    for currency in ['USD','JPY','NZD','CHF']:
        panel.locator(f'[data-calendar-currency="{currency}"]').check()
    page.evaluate('JPWCalendar.refresh()')
    expect(panel.locator('[data-calendar-economic-id="SYN-high-1"]')).to_have_count(1)
    assert 'Atualização da fonte:' in info.inner_text()
    panel.locator('[data-calendar-action="next"]').click();page.evaluate('JPWCalendar.refresh()')
    expect(panel.locator('[data-calendar-economic-id]')).to_have_count(0)
    assert 'Atualização da fonte:' not in info.inner_text()
    panel.locator('[data-calendar-action="previous"]').click();page.evaluate('JPWCalendar.refresh()')
    expect(panel.locator('[data-calendar-economic-id="SYN-high-1"]')).to_have_count(1)
    # A later successful query removes the failure label without dropping items.
    page.evaluate('__calendarQuery.fail=false;JPWCalendar.refresh()')
    expect(panel.locator('[data-calendar-economic-id="SYN-high-1"]')).to_have_count(1)
    assert 'Não foi possível' not in panel.locator('.calendar-agenda').inner_text()
    assert 'desatualizados' not in info.inner_text()
    after=page.evaluate('({state:JSON.stringify(S),document:localStorage.getItem(LSKEY)})')
    assert after==before,'Feed query recovery and filters must not write financial state'
    return {'last_valid':'preserved with stale label and source revision','context_isolation':['currency filter','month'],'recovery':'explicit later query','read_only':True}

def edges(page):
    page.evaluate("closeModal();window.__onbShown=true")
    page.evaluate("""()=>{const set=window.setTimeout,clear=window.clearTimeout;window.__calendarTimers=new Map();window.setTimeout=function(fn,ms,...args){const track=new Error().stack.includes('armClock');let id;id=set(()=>{__calendarTimers.delete(id);fn(...args)},ms);if(track)__calendarTimers.set(id,{ms});return id};window.clearTimeout=function(id){__calendarTimers.delete(id);return clear(id)}}""")
    page.locator('#headerCalendarBtn').click();panel=page.locator('#calendarDialog .calendar-panel')
    expect(panel.locator('[data-calendar-date="2026-10-23"] .calendar-economic-dot')).to_have_count(1)
    assert '2 eventos econômicos' in panel.locator('[data-calendar-date="2026-10-23"]').get_attribute('aria-label')
    panel.locator('[data-calendar-action="new"]').click();panel.locator('[name="title"]').fill('SYN marcador pessoal');panel.locator('[data-calendar-action="save-form"]').click()
    expect(panel.locator('[name="title"]')).to_have_count(0)
    cell=panel.locator('[data-calendar-date="2026-10-23"]');expect(cell.locator('.calendar-personal-dot')).to_have_count(1)
    expect(panel.locator('.calendar-agenda-summary')).to_contain_text('3 itens')
    assert panel.locator('.calendar-agenda-group').all_text_contents()==['Economia','Sua agenda']
    assert '1 item da agenda' in cell.get_attribute('aria-label')
    dot=cell.locator('.calendar-economic-dot').bounding_box();num=cell.locator('.calendar-day-number').bounding_box()
    assert abs(dot['x']+dot['width']/2-num['x']-num['width']/2)<=1
    
    assert panel.locator('[data-calendar-date="2026-10-24"] .calendar-economic-dot').count()==0
    panel.locator('[data-calendar-action="filters"]').click();panel.locator('[data-calendar-filter="impacts"][value="medium"]').check()
    expect(panel.locator('[data-calendar-date="2026-10-24"] .calendar-economic-dot')).to_have_count(1)
    panel.locator('[data-calendar-action="filters"]').click()
    panel.locator('[data-calendar-date="2026-10-25"]').click()
    expect(panel.locator('.calendar-event-time').filter(has_text='Data · horário não informado')).to_have_count(1)
    panel.locator('.calendar-header [data-calendar-action="info"]').click()
    assert 'CHF' in panel.locator('.calendar-source-list').inner_text() and 'Pendente' in panel.locator('.calendar-source-list').inner_text()
    assert 'classificação editorial JP Wealth' in panel.locator('.calendar-info').inner_text()
    assert 'Source: Synthetic fixture; adapted by JP Wealth' in panel.locator('.calendar-info').inner_text()
    expect(panel.locator('.calendar-source-links [data-calendar-source]')).to_have_attribute('href','https://example.org/calendar')
    expect(panel.locator('.calendar-source-links .calendar-license-link')).to_have_attribute('href','https://example.org/terms')
    panel.locator('.calendar-header [data-calendar-action="info"]').click()
    assert page.evaluate('__calendarTimers.size')==1
    page.clock.fast_forward(13*3600*1000+100)
    expect(panel.locator('[data-calendar-date="2026-10-24"][aria-current="date"]')).to_have_count(1)
    assert page.evaluate('__calendarTimers.size')==1
    page.locator('#calendarDialog [data-calendar-action="close"]').click()
    assert page.evaluate('__calendarTimers.size')==0, 'A closed calendar must not retain day timers'
    # Incompatible preferences stay byte-exact after a filter interaction.
    opaque='{"schemaVersion":999,"future":"SYN preserved"}'
    page.evaluate('(raw)=>{localStorage.setItem("jpwealth_calendar_view_v1",raw);JPWCalendar.resetContext()}',opaque)
    page.locator('#headerCalendarBtn').click();panel.locator('[data-calendar-action="filters"]').click()
    panel.locator('[data-calendar-filter="currencies"][value="CHF"]').uncheck()
    assert page.evaluate('localStorage.getItem("jpwealth_calendar_view_v1")')==opaque
    page.evaluate('JPWCalendar.close();localStorage.removeItem("jpwealth_calendar_view_v1");JPWCalendar.resetContext()')
    # Independent day/month state uses the exact same factory in the workspace.
    page.evaluate("()=>{const host=document.createElement('div');host.id='SYN_calendar_workspace';document.body.append(host);JPWCalendar.mountWorkspace(host)}")
    work=page.locator('#SYN_calendar_workspace');expect(work.locator('.calendar-panel')).to_be_visible()
    month=work.locator('.calendar-month-label').inner_text()
    page.locator('#headerCalendarBtn').click();panel.locator('[data-calendar-action="next"]').click()
    assert work.locator('.calendar-month-label').inner_text()==month
    page.evaluate('JPWCalendar.close();JPWCalendar.deactivateWorkspace()')
    assert page.evaluate('__calendarTimers.size')==0
    page.evaluate("()=>{document.getElementById('SYN_calendar_workspace').remove();S.dataGovernance.backup.lastConfirmedAt='2026-10-03T04:30:00.000Z';JPWCalendar.open()}")
    panel.locator('[data-calendar-action="today"]').click();panel.locator('[data-calendar-action="next"]').click()
    panel.locator('[data-calendar-date="2026-11-01"]').click()
    expect(panel.locator('.calendar-event-app')).to_have_count(1)
    panel.locator('[data-calendar-date="2026-11-02"]').click()
    expect(panel.locator('.calendar-event-app')).to_have_count(0)
    page.evaluate("S.dataGovernance.backup.lastConfirmedAt='2026-10-25T15:00:00.000Z';JPWCalendar.refresh()")
    assert page.evaluate("dgBackupStatus().state")== 'unknown',page.evaluate("({status:dgBackupStatus(),now:new Date().toISOString(),at:S.dataGovernance.backup.lastConfirmedAt})")
    expect(panel.locator('[data-calendar-date="2026-11-01"] .calendar-personal-dot')).to_have_count(0)
    page.evaluate("S.dataGovernance.backup.lastConfirmedAt='';JPWCalendar.refresh()")
    panel.locator('[data-calendar-action="today"]').click()
    expect(panel.locator('.calendar-event-app')).to_have_count(0)
    return {'timer_open':1,'timer_closed':0,'opaque_preferences':'preserved','workspace_state':'independent','synthetic_feed_markers':'filtered and counted','date_precision':'no invented time','pending_coverage':'visible','backup':'elapsed30days across DST; no future or missing invented date','midnight':'real timer advanced to new day'}

def preference_preservation(page,variant):
    raw=json.dumps({'schemaVersion':1,'currencies':['USD','GBP','JPY','NZD','CHF'],'impacts':['high'],'contents':['economic','personal','app'],**({'future':{'SYN':'preserved'}} if variant=='pref-extension' else {})},separators=(',',':'))
    if variant=='pref-duplicates':raw=raw.replace('["high"]','["high","high"]')
    page.evaluate("""({raw,fail})=>{closeModal();window.__onbShown=true;localStorage.setItem('jpwealth_calendar_view_v1',raw);window.__calendarOriginalGet=Storage.prototype.getItem;if(fail)Storage.prototype.getItem=function(key){if(this===localStorage&&key==='jpwealth_calendar_view_v1')throw new Error('SYN selective read failure');return __calendarOriginalGet.call(this,key)};JPWCalendar.resetContext()}""",{'raw':raw,'fail':variant=='pref-read'})
    page.locator('#headerCalendarBtn').click();panel=page.locator('#calendarDialog .calendar-panel')
    if variant=='pref-read':expect(panel.locator('.calendar-notice')).to_contain_text('temporários')
    panel.locator('[data-calendar-action="filters"]').click();panel.locator('[data-calendar-filter="currencies"][value="USD"]').uncheck()
    observed=page.evaluate("__calendarOriginalGet.call(localStorage,'jpwealth_calendar_view_v1')")
    assert observed==raw,{'case':variant,'before':raw,'after':observed}
    page.evaluate('()=>{Storage.prototype.getItem=__calendarOriginalGet;}')
    return {'raw_bytes':'preserved','filter_interaction':'real checkbox','case':variant}

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--artifact');p.add_argument('--width',type=int);p.add_argument('--path',default='index.html');p.add_argument('--case',action='append');args=p.parse_args()
    server=BrowserFixtureServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start(); results=[]
    try:
        with sync_playwright() as pw:
            browser=launch_browser(pw)
            cases=[(1440,'light','baseline')] if args.baseline else [(w,t,'ui') for w in ([args.width] if args.width else [1440,390,320]) for t in ['light','dark']]
            if not args.baseline and args.path=='index.html':cases.extend([(320,'light',kind) for kind in ['edges','pref-read','pref-extension','pref-duplicates','adjacent-selection','adjacent-range','feed-recovery']])
            if args.case:cases=[case for case in cases if case[2] in args.case]
            for width,theme,kind in cases:
                ctx=browser.new_context(viewport={'width':width,'height':900},timezone_id='America/New_York' if kind=='edges' else 'America/Sao_Paulo',service_workers='block');install_bootstrap(ctx);ctx.add_init_script('window.__onbShown=true')
                if kind=='edges' or kind.startswith('adjacent-') or kind=='feed-recovery':calendar_packet(ctx,adjacent=kind.startswith('adjacent-'))
                page=ctx.new_page()
                if kind=='edges':page.clock.install(time=datetime(2026,10,23,15,tzinfo=timezone.utc))
                else:page.clock.set_fixed_time(datetime(2026,10,23,15,tzinfo=timezone.utc))
                errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                try:
                    page.goto(f'http://127.0.0.1:{server.server_port}/{args.path}',wait_until='load');wait_bootstrap(page)
                    details=preference_preservation(page,kind) if kind.startswith('pref-') else edges(page) if kind=='edges' else adjacent_selection(page,kind=='adjacent-range') if kind.startswith('adjacent-') else feed_recovery(page) if kind=='feed-recovery' else run(page,width,theme)
                    assert not errors,errors
                    results.append({'case':f'calendar-{kind}-{width}-{theme}','result':'PASS','geometry':details})
                    if args.artifact:
                        folder=Path(args.artifact).parent;folder.mkdir(parents=True,exist_ok=True)
                        page.screenshot(path=str(folder/f'calendar-{kind}-{width}-{theme}.png'))
                except Exception as e:
                    results.append({'case':f'calendar-{kind}-{width}-{theme}','result':'PRODUCT_FAIL' if isinstance(e,AssertionError) else 'TEST_HARNESS_FAIL','evidence':str(e),'traceback':traceback.format_exc()})
                finally:ctx.close()
            browser.close()
    finally:server.shutdown();server.server_close()
    out=json.dumps({'results':results},ensure_ascii=False,indent=2);print(out)
    if args.artifact:Path(args.artifact).write_text(out)
    raise SystemExit(0 if results and all(r['result']=='PASS' for r in results) else 1)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""NOTIFICATIONS-CENTER-01: read-only projections and session-only notifications.

The source contract is exercised through DOM controls and real product APIs.
All profiles and data are synthetic; external resources use existing fixtures.
Native alert/confirm dialogs are observed and dismissed by Playwright, not replaced.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright, expect
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def prepare(browser, url, viewport=None, theme='light'):
    context = browser.new_context(viewport=viewport or {'width': 1440, 'height': 900},
                                  timezone_id='UTC', service_workers='block')
    install_bootstrap(context)
    context.add_init_script('window.__onbShown=true;window.__notificationXss=0')
    page = context.new_page()
    page.clock.set_fixed_time(NOW)
    dialogs = []
    def dismiss(dialog):
        dialogs.append({'type': dialog.type, 'message': dialog.message})
        dialog.dismiss()
    page.on('dialog', dismiss)
    page.notification_errors = []
    page.on('pageerror', lambda error: page.notification_errors.append(str(error)))
    page.goto(url, wait_until='load')
    wait_bootstrap(page)
    page.evaluate("theme=>{window.__onbShown=true;closeModal();document.documentElement.dataset.theme=theme;}", theme)
    return context, page, dialogs


def refresh(page):
    page.evaluate('JPWNotifications.refresh()')


def open_center(page, area='all'):
    if not page.locator('#notificationCenter').evaluate('e=>e.open'):
        page.locator('#headerNotificationsBtn').click()
    page.locator('#notificationArea').select_option(area)


def rows(page):
    return page.locator('#notificationList [data-notification-id]:visible')


def ids(page):
    return rows(page).evaluate_all('els=>els.map(e=>e.dataset.notificationId)')


def instrument(page):
    page.evaluate("""() => {
      window.__notificationWrites=[];
      for(const method of ['setItem','removeItem','clear']){
        const original=Storage.prototype[method];
        Storage.prototype[method]=function(...args){
          window.__notificationWrites.push({method,area:this===localStorage?'local':'session',key:args[0]||null});
          return original.apply(this,args);
        };
      }
    }""")


def snapshot(page):
    return page.evaluate("""() => ({state:JSON.stringify(S),
      local:JSON.stringify(Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))),
      session:JSON.stringify(Object.fromEntries(Object.keys(sessionStorage).sort().map(k=>[k,sessionStorage.getItem(k)]))),
      writes:window.__notificationWrites.length})""")


def unchanged(page, before):
    after = snapshot(page)
    assert after == before, {'changed': [k for k in before if after[k] != before[k]],
                             'writes': page.evaluate('window.__notificationWrites')}


def seed_calendar(page, minutes=16, title='SYN Calendário', age_minutes=0):
    page.evaluate("""({minutes,title,age})=>{
      const now=Date.now();
      localStorage.setItem(FF_NEWS_CACHE_KEY,JSON.stringify({fetchedAt:now-age*60000,payload:{
        version:1,generated_at:new Date(now).toISOString(),events:[
          {title,country:'USD',impact:'High',date:new Date(now+minutes*60000).toISOString(),forecast:'',previous:''}
        ]}}));
      ffNewsLastError=false;ffNewsCacheReadFailed=false;ffNewsCacheWriteFailed=false;
    }""", {'minutes': minutes, 'title': title, 'age': age_minutes})


def seed_areas(page):
    page.evaluate("""() => {
      S.onboarding={...S.onboarding,done:true};
      S.quarantine={...(S.quarantine||{}),inicio:'2026-09-14',fim:'2026-12-14'};
      S.phases[0].orders.push({id:'SYN_ORDER_REVIEW',par:'EURUSD',lote:0.01,entry:1.1,sl:1.09,
        tp:1.12,dir:'Compra',status:'Aberta',result:0,needsReview:true});
      S.dataGovernance.backup.lastConfirmedAt='2020-01-01T00:00:00Z';
      S.personalFinance.months['2026-08']={createdAt:'2026-08-01T00:00:00Z',incomes:[],
        expenses:[{id:'SYN_PENDING',name:'SYN despesa',status:'PENDENTE',targetAmount:null,
        expectedAmount:null,executedCash:null,executedCard:null,installments:null}],
        notes:[],debtSnapshots:[],allocations:[]};
      S.alladin.schemaVersion=999;
      ncDirty=true;
      mvpNotesUI.draftDirty=true;
      mvpNotesUI.selectedId='SYN_NOTE';
      mvpNotesUI.draft={title:'SYN nota',content:'SYN conteúdo privado'};
    }""")
    seed_calendar(page)
    refresh(page)


def all_areas_and_readonly(page, _dialogs):
    seed_areas(page)
    instrument(page)
    before = snapshot(page)
    requests = []
    page.on('request', lambda request: requests.append(request.url))
    open_center(page)
    initial = ids(page)
    assert initial and len(initial) == len(set(initial)), initial
    assert not any(item.startswith('unavailable:') for item in initial), initial
    expected_sources = {'system': 'system:backup', 'forex': 'forex:clearance',
                        'pf': 'pf:pending', 'alladin': 'alladin:compatibility',
                        'research': 'research:nocoda-draft', 'notes': 'notes:draft'}
    for area in ['system', 'forex', 'pf', 'alladin', 'research', 'notes']:
        page.locator('#notificationArea').select_option(area)
        assert rows(page).count() > 0, {'missing_area': area}
        assert expected_sources[area] in ids(page), {'area': area, 'actual': ids(page)}
        if area == 'forex':
            assert 'forex:order-review' in ids(page), 'Review flags in actual S.phases[].orders were omitted'
        if area == 'alladin':
            assert rows(page).count() == 1, 'Future schema and its consequent read refusal are one underlying condition'
        for _ in range(3):
            refresh(page)
        assert len(ids(page)) == len(set(ids(page))), area
    page.locator('#notificationArea').select_option('all')
    assert ids(page) == initial
    assert rows(page).evaluate_all("es=>es.every(e=>['live','event'].includes(e.dataset.kind)&&['critical','warning','info'].includes(e.dataset.severity))")
    page.locator('#notificationReadAll').click()
    assert page.locator('#notificationList [data-unread="true"]').count() == 0
    expect(page.locator('#notificationBadge')).not_to_be_visible()
    refresh(page)
    assert page.locator('#notificationList [data-unread="true"]').count() == 0
    for _ in range(3):
        page.locator('#notificationClose').click()
        page.locator('#headerNotificationsBtn').click()
    unchanged(page, before)
    assert requests == [], requests
    return {'initial_items': len(initial), 'areas': 6, 'extra_requests': len(requests)}


def resolution_and_navigation(page, _dialogs):
    seed_areas(page)
    open_center(page, 'pf')
    pending = rows(page).filter(has_text='pendência').first
    assert pending.count(), rows(page).all_text_contents()
    pending_id = pending.get_attribute('data-notification-id')
    pending.locator('[data-notification-read]').click()
    assert pending.get_attribute('data-unread') == 'false'
    pending.locator('[data-notification-go]').click()
    expect(page.locator('#notificationCenter')).not_to_be_visible()
    assert page.evaluate("JPWNavigation.current().primary==='personal-finance' && finpesGetView()==='mensal'"), page.evaluate('JPWNavigation.current()')
    assert page.evaluate("document.querySelector('#finpes').contains(document.activeElement)"), 'PF target must receive keyboard focus'
    page.evaluate('closeModal()')
    assert page.evaluate("S.personalFinance.months['2026-08'].expenses[0].status") == 'PENDENTE'
    page.evaluate("S.personalFinance.months['2026-08'].expenses[0].status='PAGO'")
    refresh(page)
    open_center(page, 'pf')
    assert pending_id not in ids(page), {'resolved_still_live': pending_id}
    return {'destination': 'finpes/mensal', 'resolved_id': pending_id}


def calendar_lifecycle(page, _dialogs):
    title = 'SYN Calendário limiar'
    seed_calendar(page, 16, title)
    refresh(page)
    open_center(page, 'research')
    event = rows(page).filter(has_text=title)
    assert event.count() == 1, rows(page).all_text_contents()
    first_id = event.get_attribute('data-notification-id')
    first_severity = event.get_attribute('data-severity')
    event.locator('[data-notification-read]').click()
    assert event.get_attribute('data-unread') == 'false'
    page.clock.set_fixed_time(datetime(2026, 9, 14, 12, 1, tzinfo=timezone.utc))
    page.evaluate('ffNewsRenderAll()')
    expect(event).to_have_attribute('data-severity', 'warning')
    assert event.count() == 1
    assert event.get_attribute('data-notification-id') == first_id
    assert event.get_attribute('data-severity') != first_severity, '15-minute boundary did not change presentation'
    assert event.get_attribute('data-unread') == 'true', 'Material imminence change did not renew attention'
    for _ in range(3):
        refresh(page)
    assert event.count() == 1
    page.clock.set_fixed_time(datetime(2026, 9, 14, 12, 17, tzinfo=timezone.utc))
    refresh(page)
    assert rows(page).filter(has_text=title).count() == 0, 'Past calendar event remains upcoming'
    seed_calendar(page, 30, 'SYN Amanhã')
    page.clock.set_fixed_time(datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc))
    refresh(page)
    assert rows(page).filter(has_text='SYN Amanhã').count() == 0
    return {'event_id': first_id, 'threshold_minutes': 15, 'past_and_day_rollover': True}


def calendar_cache_and_xss(page, _dialogs):
    title = '<img src=x onerror="window.__notificationXss=1"> SYN texto literal'
    seed_calendar(page, 10, title, 31)
    page.evaluate('ffNewsCacheWriteFailed=true')
    refresh(page)
    open_center(page, 'research')
    assert rows(page).filter(has_text=title).count() == 1
    assert page.locator('#notificationList img').count() == 0
    assert page.evaluate('window.__notificationXss') == 0
    text = page.locator('#notificationList').inner_text().lower()
    assert 'cache' in text and ('não' in text or 'falha' in text or 'desatual' in text), text
    page.evaluate('localStorage.removeItem(FF_NEWS_CACHE_KEY);ffNewsLastError=true;ffNewsCacheWriteFailed=false')
    refresh(page)
    assert rows(page).filter(has_text=title).count() == 0
    text = page.locator('#notificationList').inner_text().lower()
    assert rows(page).count() > 0 and ('calendário' in text or 'agenda' in text), text
    assert rows(page).locator('[data-severity="warning"], [data-severity="critical"]').count() or rows(page).evaluate_all("es=>es.some(e=>['warning','critical'].includes(e.dataset.severity))")
    return {'literal_external_title': True, 'stale_and_missing_cache': True}


def native_events_and_exclusions(page, dialogs):
    open_center(page)
    page.locator('#notificationReadAll').click()
    instrument(page)
    before = snapshot(page)
    message = 'SYN alerta nativo <svg onload="window.__notificationXss=2">'
    page.evaluate('message=>alert(message)', message)
    assert dialogs[-1] == {'type': 'alert', 'message': message}, dialogs
    refresh(page)
    event = rows(page).filter(has_text=message)
    assert event.count() == 1
    assert event.get_attribute('data-kind') == 'event'
    assert page.locator('#notificationList svg[onload]').count() == 0
    assert page.evaluate('window.__notificationXss') == 0
    before_events = page.locator('#notificationList [data-kind="event"]').count()
    result = page.evaluate("confirm('SYN confirmação destrutiva não deve virar notificação')")
    assert result is False
    assert dialogs[-1]['type'] == 'confirm'
    refresh(page)
    assert page.locator('#notificationList [data-kind="event"]').count() == before_events
    assert rows(page).filter(has_text='SYN confirmação destrutiva').count() == 0
    unchanged(page, before)
    return {'native_alert_seen': True, 'native_confirm_excluded': True}


def event_area_provenance(page, dialogs):
    page.evaluate("JPWNavigation.navigate('personal-finance')")
    page.evaluate("fbAtoUI({ok:false,erro:'SYN recusa em Finanças Pessoais'})")
    assert dialogs[-1]['type'] == 'alert' and 'SYN recusa em Finanças Pessoais' in dialogs[-1]['message']
    refresh(page)
    open_center(page, 'pf')
    assert rows(page).filter(has_text='SYN recusa em Finanças Pessoais').count() == 1
    assert 'Exibida em Finanças Pessoais' in rows(page).filter(has_text='SYN recusa em Finanças Pessoais').inner_text()
    page.locator('#notificationArea').select_option('system')
    assert rows(page).filter(has_text='SYN recusa em Finanças Pessoais').count() == 1, 'Shared message source must remain System; screen is contextual, not causal provenance'
    page.locator('#notificationClose').click()
    page.evaluate("JPWNavigation.navigate('alladin');showSessionNotice('SYN atividade do Alladin')")
    refresh(page)
    open_center(page, 'alladin')
    assert rows(page).filter(has_text='SYN atividade do Alladin').count() == 1
    return {'pf_real_feedback_producer': True, 'alladin_session_notice_context': True, 'screen_is_not_causal_origin': True}


def completion_details(page, _dialogs):
    page.evaluate("S.onboarding.done=true;S.onboarding.epStatus='Ainda vou configurar antes de iniciar o período.';S.onboarding.epRestrictiveAccepted=true")
    assert page.evaluate("getOnboardingCompletionState().severity") == 'critical'
    refresh(page)
    open_center(page, 'forex')
    card=page.locator('[data-notification-id="forex:clearance"]')
    assert card.get_attribute('data-severity') == 'critical'
    assert 'Proteção' in card.inner_text(), 'The done flag must not conceal detailed completion warnings'
    card.locator('[data-notification-go]').click()
    assert page.evaluate("JPWNavigation.current().primary==='forex'")
    assert page.evaluate("document.getElementById(JPWNavigation.current().screen).contains(document.activeElement)"), 'Forex destination must receive keyboard focus'
    return {'detailed_completion_when_done': True, 'forex_destination_focus': True}


def alladin_balance_quality(page, _dialogs):
    # Existing cash-only-currency fixture from alladin_ledger_read_model_test.py:
    # ledger readability is true while the per-cash currency contract refuses.
    page.evaluate("""() => { S.alladin={schemaVersion:6,reportingCurrency:'BRL',assets:[],instruments:[],
      accounts:[{accountId:'account',name:'SYN conta',recordStatus:'ACTIVE'}],
      cashAccounts:[{cashAccountId:'cash',accountId:'account',currency:'BRL',recordStatus:'ACTIVE'}],
      transactions:[{transactionId:'deposit',eventType:'DEPOSIT',status:'POSTED',amount:1000,
      currency:'USD',flowScope:'EXTERNAL',effectiveAt:'2026-02-01',
      recordedAt:'2026-02-01T10:00:00.000Z',cashAccountId:'cash'}]}; }""")
    assert page.evaluate('JPWAlladin.leitura.ledger().available') is True
    assert page.evaluate("JPWAlladin.leitura.saldoDeCaixa('cash').available") is False
    instrument(page)
    before=snapshot(page)
    refresh(page)
    open_center(page, 'alladin')
    assert page.locator('[data-notification-id="alladin:quality"]').count() == 1
    unchanged(page,before)
    row=page.locator('[data-notification-id="alladin:quality"]')
    row.locator('[data-notification-read]').click()
    assert row.get_attribute('data-unread') == 'false'
    # Change directly from currency refusal to accumulation overflow (L29 of
    # alladin_ledger_test.py), without an intermediate healthy refresh.
    page.evaluate("""() => {const tx=S.alladin.transactions[0];tx.currency='BRL';
      tx.amount=Number.MAX_SAFE_INTEGER-10;
      S.alladin.transactions.push({...tx,transactionId:'second',amount:20,effectiveAt:'2026-02-02'});}""")
    assert 'ALD_SOMA_FORA_DO_INTEIRO_SEGURO' in page.evaluate("JPWAlladin.leitura.saldoDeCaixa('cash').issues")
    refresh(page)
    assert row.get_attribute('data-unread') == 'true', 'A materially different quality refusal must renew attention'
    return {'readable_ledger_does_not_conceal_unavailable_balance': True, 'different_refusal_renews_attention': True}


def unknown_gate(page, _dialogs):
    page.evaluate("markJPWealthPersistenceOutcomeUnknown('SYN notifications test')")
    refresh(page)
    instrument(page)
    before = snapshot(page)
    open_center(page, 'system')
    text = page.locator('#notificationList').inner_text().lower()
    assert 'indeterminad' in text or 'desconhecid' in text, text
    page.locator('#notificationReadAll').click()
    page.locator('#notificationClose').click()
    assert page.evaluate('jpWealthPersistenceOutcomeIsUnknown()')
    assert page.evaluate('save()') is False
    unchanged(page, before)
    return {'unknown_preserved': True, 'save_refused': True}


def backup_status_consistency(page, _dialogs):
    instrument(page)
    page.evaluate("() => { S.onboarding.done=false; S.dataGovernance.backup.lastConfirmedAt=''; S.dataGovernance.changeLog=[]; }")
    before=snapshot(page);refresh(page);open_center(page,'system')
    assert page.locator('[data-notification-id="system:backup"]').count()==0, 'Empty inactive base must not receive backup reminder'
    unchanged(page,before)
    page.evaluate("() => { S.onboarding.done=true; S.dataGovernance.changeLog=[{ts:new Date().toISOString(),kind:'SYNTHETIC'}]; }")
    before=snapshot(page);refresh(page)
    assert page.locator('[data-notification-id="system:backup"]').count()==1, 'Active changed base requires backup reminder'
    unchanged(page,before)
    page.evaluate("() => { S.dataGovernance.backup.lastConfirmedAt=new Date().toISOString(); }")
    before=snapshot(page);refresh(page)
    assert page.locator('[data-notification-id="system:backup"]').count()==0, 'Current confirmation must not receive reminder'
    unchanged(page,before);page.evaluate('JPWNotifications.close()')
    for date, title in [('2020-01-01T00:00:00Z', 'Backup vencido — atualização recomendada'),
                        ('invalid-date', 'Data de confirmação precisa de verificação'),
                        ('2099-01-01T00:00:00Z', 'Data de confirmação precisa de verificação')]:
        page.evaluate("date => {S.dataGovernance.backup.lastConfirmedAt=date;}", date)
        before=snapshot(page)
        refresh(page);open_center(page,'system')
        row=page.locator('[data-notification-id="system:backup"]')
        expect(row.locator('h3')).to_have_text(title)
        if date!='2020-01-01T00:00:00Z':
            expect(row).not_to_contain_text('dias desde a última confirmação')
        page.evaluate('JPWNotifications.close()')
        unchanged(page,before)


def lifecycle_cleanup(page, _dialogs):
    page.evaluate("alert('SYN antes da substituição')")
    open_center(page)
    assert rows(page).filter(has_text='SYN antes da substituição').count() == 1
    page.evaluate('S=structuredClone(S)')
    refresh(page)
    open_center(page)
    assert rows(page).filter(has_text='SYN antes da substituição').count() == 0
    page.locator('#notificationClose').click()
    page.evaluate("alert('SYN antes da finalização')")
    page.evaluate("""() => {
      S.onboarding.done=true;
      if(save()!==true)throw Error('Fixture could not persist before finalization');
      sessionEpochCurrent();markSessionCheckpoint();
    }""")
    page.locator('#finalizeSessionBtn').click()
    page.evaluate('async()=>{await finalizeJPWealthSession();}')
    refresh(page)
    open_center(page)
    assert rows(page).filter(has_text='SYN antes da finalização').count() == 0
    assert page.evaluate('S.onboarding.done') is False, 'Finalization did not actually replace the operational state'
    return {'state_replacement_cleanup': True, 'real_finalization_cleanup': True}


def keyboard_and_geometry(page, _dialogs):
    page.locator('#headerNotificationsBtn').focus()
    page.keyboard.press('Enter')
    expect(page.locator('#notificationCenter')).to_be_visible()
    for step in range(18):
        page.keyboard.press('Tab')
        assert page.evaluate("document.getElementById('notificationCenter').contains(document.activeElement)"), {'key': 'Tab', 'step': step, 'active': page.evaluate('document.activeElement.outerHTML.slice(0,300)')}
    for step in range(4):
        page.keyboard.press('Shift+Tab')
        assert page.evaluate("document.getElementById('notificationCenter').contains(document.activeElement)"), {'key': 'Shift+Tab', 'step': step, 'active': page.evaluate('document.activeElement.outerHTML.slice(0,300)')}
    bounds = page.locator('#notificationCenter').evaluate("""e=>{const r=e.getBoundingClientRect();return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,w:innerWidth,h:innerHeight};}""")
    assert bounds['left'] >= -1 and bounds['top'] >= -1 and bounds['right'] <= bounds['w'] + 1 and bounds['bottom'] <= bounds['h'] + 1, bounds
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    page.keyboard.press('Escape')
    expect(page.locator('#notificationCenter')).not_to_be_visible()
    expect(page.locator('#headerNotificationsBtn')).to_be_focused()
    return bounds


def structure(page):
    assert page.locator('#headerNotificationsBtn').count() == 1, 'Required notifications bell is absent'
    assert page.locator('#headerActions #headerNotificationsBtn').count() == 1
    for item in ['notificationBadge', 'notificationCenter', 'notificationClose',
                 'notificationList', 'notificationArea', 'notificationReadAll']:
        assert page.locator('#'+item).count() == 1, item
    assert page.locator('#notificationCenter').evaluate('e=>e instanceof HTMLDialogElement')
    assert page.locator('#headerNotificationsBtn').get_attribute('aria-label')
    page.locator('#headerNotificationsBtn').click()
    expect(page.locator('#notificationCenter')).to_be_visible()
    assert page.evaluate("document.getElementById('notificationCenter').contains(document.activeElement)")
    page.locator('#notificationClose').click()
    expect(page.locator('#notificationCenter')).not_to_be_visible()
    expect(page.locator('#headerNotificationsBtn')).to_be_focused()
    page.evaluate("S.onboarding.done=true;S.dataGovernance.backup.lastConfirmedAt='2020-01-01T00:00:00Z'")
    refresh(page)
    open_center(page, 'system')
    page.locator('[data-notification-id="system:backup"] [data-notification-go]').click()
    expect(page.locator('#notificationCenter')).not_to_be_visible()
    page.wait_for_function("settingsIsOpen() && document.getElementById('settingsModal').contains(document.activeElement)")
    assert page.evaluate('settingsIsOpen()')
    assert not page.locator('#headerNotificationsBtn').evaluate('e=>document.activeElement===e')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--case', action='append', default=[], help='Run only named existing cases for a justified focal reproduction')
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []
    try:
        with sync_playwright() as p:
            executable = os.environ.get('JP_WEALTH_CHROMIUM')
            browser = p.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))
            url = 'http://127.0.0.1:'+str(server.server_port)+'/index.html'
            cases = [('bell-and-native-dialog', lambda page, _: structure(page), None, 'light')]
            if not args.baseline:
                cases += [
                    ('all-areas-filter-dedupe-readonly', all_areas_and_readonly, None, 'light'),
                    ('resolution-navigation', resolution_and_navigation, None, 'light'),
                    ('calendar-time-threshold-rollover', calendar_lifecycle, None, 'light'),
                    ('calendar-cache-xss', calendar_cache_and_xss, None, 'light'),
                    ('native-events-confirm-exclusion', native_events_and_exclusions, None, 'light'),
                    ('event-area-provenance', event_area_provenance, None, 'light'),
                    ('detailed-completion-focus', completion_details, None, 'light'),
                    ('alladin-balance-quality', alladin_balance_quality, None, 'light'),
                    ('unknown-persistence-gate', unknown_gate, None, 'light'),
                    ('backup-status-consistency', backup_status_consistency, None, 'light'),
                    ('replacement-finalization-cleanup', lifecycle_cleanup, None, 'light'),
                ]
                for theme in ['light', 'dark']:
                    for width in [1440, 390]:
                        cases.append((f'keyboard-geometry-{width}-{theme}', keyboard_and_geometry,
                                      {'width': width, 'height': 900 if width == 1440 else 844}, theme))
            if args.case:
                names = {case[0] for case in cases}
                assert set(args.case) <= names, {'unknown_cases': set(args.case)-names}
                cases = [case for case in cases if case[0] in args.case]
            for name, callback, viewport, theme in cases:
                context = None
                try:
                    context, page, dialogs = prepare(browser, url, viewport, theme)
                    page.set_default_timeout(5000)
                    details = callback(page, dialogs)
                    assert_fixture_requests(context)
                    assert not page.notification_errors, page.notification_errors
                    result = {'case': name, 'result': 'PASS', 'evidence': details}
                except Exception as error:
                    result = {'case': name, 'result': 'PRODUCT_FAIL' if isinstance(error, AssertionError) else 'TEST_HARNESS_FAIL',
                              'evidence': str(error), 'traceback': traceback.format_exc()}
                finally:
                    if context:
                        context.close()
                results.append(result)
                print(json.dumps(result, ensure_ascii=False), flush=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    source_paths = ['index.html','src/styles/app.css','src/js/40-app/18-notification-center.js',
                    'tools/notification_center_test.py','build-id.js']
    identity = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                for name in source_paths if (ROOT/name).exists()}
    print(json.dumps({'baseline': args.baseline, 'source_sha256': identity,
                      'results': results}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if results and all(row['result'] == 'PASS' for row in results) else 1)


if __name__ == '__main__':
    main()

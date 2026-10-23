#!/usr/bin/env python3
"""NOTIFICATION-ACTIONS-01: actionable, read-only conditions without an inbox.

The source contract is exercised through DOM controls and real product APIs.
All profiles and data are synthetic; external resources use existing fixtures.
Native alert/confirm dialogs are observed and dismissed by Playwright, not replaced.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from browser_fixture_server import BrowserFixtureServer as ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright, expect
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
REVIEW_CONTEXTS = [
    {'account_id': 'SYN_NOTIFY_A', 'period_id': 'SYN_NOTIFY_A_SEP', 'name': 'SYN Conta A',
     'currency': 'USD', 'flag': 'needsReview',
     'notification_id': 'forex:order-review:SYN_NOTIFY_A:SYN_NOTIFY_A_SEP'},
    {'account_id': 'SYN_NOTIFY_B', 'period_id': 'SYN_NOTIFY_B_SEP', 'name': 'SYN Conta B',
     'currency': 'EUR', 'flag': 'stopPhaseWarning',
     'notification_id': 'forex:order-review:SYN_NOTIFY_B:SYN_NOTIFY_B_SEP'},
]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def prepare(browser, url, viewport=None, theme='light', *, personal_finance_active=False, has_touch=False, timezone_id='UTC'):
    context = browser.new_context(viewport=viewport or {'width': 1440, 'height': 900},
                                  timezone_id=timezone_id, service_workers='block', has_touch=has_touch)
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
    if personal_finance_active:
        page.evaluate("() => { if(!JPWModuleAvailability.setState('personal-finance','active').ok) throw Error('PF fixture refused'); }")
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


def seed_review_contexts(page):
    # STATE-SCHEMA: accountContexts is canonical; S.phases remains immutable legacy.
    # Consumer fixtures are installed before read-only instrumentation, not by
    # changing a financial writer or automatically associating legacy orders.
    page.evaluate("""contexts => {
      const envelope=S.forex.accountContexts ||
        (S.forex.accountContexts={schemaVersion:1,revision:1,accounts:{},archivedAccounts:{},legacy:null});
      for(const c of contexts){
        S.accounts.push({forexAccountId:c.account_id,nome:c.name,tipo:'PRÓPRIA',
          platform:'MT5',platformCurrency:c.currency});
        const makePeriod=periodId=>({accountId:c.account_id,periodId,startedAt:'2026-09-14',
          currency:c.currency,si:10000,openingBook:10000,source:'synthetic notification fixture',
          observedAt:'2026-09-14T12:00:00.000Z',createdAt:'2026-09-14T12:00:00.000Z',
          activeOperation:null,phases:forexNewOperationPhases(),ledger:[],ledgerEvents:[],revision:1});
        const period=makePeriod(c.period_id);
        period.phases[0].orders=[{id:'SYN_SHARED_MANUAL_ID',orderId:'SYN_ORDER_'+c.account_id,
          brokerHash:'000_SYN_'+c.account_id,accountId:c.account_id,periodId:c.period_id,
          currency:c.currency,par:'EURUSD',lote:0.01,entry:1.1,sl:1.09,tp:1.12,
          tipo:'BUY',dir:'Compra',role:'GENESIS',status:'Aberta',result:0,[c.flag]:true}];
        const clean=makePeriod(c.period_id+'_CLEAN');
        envelope.accounts[c.account_id]={accountId:c.account_id,currentPeriodId:c.period_id,
          periods:{[c.period_id]:period,[clean.periodId]:clean},archived:false};
      }
    }""", REVIEW_CONTEXTS)


def seed_areas(page):
    seed_review_contexts(page)
    page.evaluate("JPWModuleAvailability.setState('personal-finance','active')")
    page.evaluate("""() => {
      S.onboarding={...S.onboarding,done:true};
      S.quarantine={...(S.quarantine||{}),inicio:'2026-09-14',fim:'2026-12-14'};
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
    expected_sources = {'system': 'system:backup', 'forex': REVIEW_CONTEXTS[0]['notification_id'], 'pf': 'pf:pending'}
    for area, expected_id in expected_sources.items():
        page.locator('#notificationArea').select_option(area)
        assert expected_id in ids(page), {'area': area, 'actual': ids(page)}
        if area == 'forex':
            reviews = [item for item in ids(page) if item.startswith('forex:order-review')]
            assert set(reviews) == {c['notification_id'] for c in REVIEW_CONTEXTS}, reviews
            assert len(reviews) == 2, 'Different account/period causes were merged'
            for c in REVIEW_CONTEXTS:
                row = page.locator('[data-notification-id="'+c['notification_id']+'"]')
                assert c['name'] in row.inner_text() and c['currency'] in row.inner_text()
        for _ in range(3):
            refresh(page)
        assert len(ids(page)) == len(set(ids(page))), area
    page.locator('#notificationArea').select_option('system')
    assert 'alladin:compatibility' in ids(page), 'Data integrity belongs to System even for a frozen module'
    page.locator('#notificationArea').select_option('all')
    assert ids(page) == initial
    assert not any(x.startswith(('calendar:', 'activity:', 'research:nocoda-draft', 'notes:draft')) for x in initial)
    assert rows(page).evaluate_all("es=>es.every(e=>['critical','warning','info'].includes(e.dataset.severity))")
    assert page.locator('[data-notification-read],#notificationReadAll').count() == 0
    count = page.locator('#notificationBadge').inner_text()
    for _ in range(3):
        page.locator('#notificationClose').click()
        page.locator('#headerNotificationsBtn').click()
    assert page.locator('#notificationBadge').inner_text() == count
    unchanged(page, before)
    assert requests == [], requests
    return {'initial_items': len(initial), 'extra_requests': len(requests), 'contextual_reviews': [c['notification_id'] for c in REVIEW_CONTEXTS], 'no_inbox': True}

def contextual_review_navigation(page, _dialogs):
    seed_review_contexts(page)
    before = page.evaluate('JSON.stringify(S)')
    destinations = []
    for c in REVIEW_CONTEXTS:
        refresh(page)
        open_center(page, 'forex')
        page.locator('[data-notification-go="'+c['notification_id']+'"]').click()
        assert page.evaluate('JPWNavigation.current().child') == 'forex-operation'
        selected = page.evaluate('JPWForex.state.operationalSelection()')
        assert selected['accountId'] == c['account_id'], selected
        assert selected['periodId'] == c['period_id'], selected
        assert page.evaluate('JSON.stringify(S)') == before, 'Following a contextual alert changed confirmed data'
        destinations.append({'accountId': selected['accountId'], 'periodId': selected['periodId']})
    return {'contextual_destinations': destinations, 'confirmed_state_preserved': True}


def resolution_and_navigation(page, _dialogs):
    seed_areas(page)
    open_center(page, 'pf')
    pending = page.locator('[data-notification-id="pf:pending"]')
    assert pending.is_visible()
    pending_id = pending.get_attribute('data-notification-id')
    pending.locator('[data-notification-go]').click()
    expect(page.locator('#notificationCenter')).not_to_be_visible()
    assert page.evaluate("JPWNavigation.current().primary==='personal-finance' && finpesGetView()==='mensal'"), page.evaluate('JPWNavigation.current()')
    assert page.evaluate("document.querySelector('#finpes').contains(document.activeElement)")
    assert page.evaluate("S.personalFinance.months['2026-08'].expenses[0].status") == 'PENDENTE'
    page.evaluate('closeModal()')
    refresh(page);open_center(page, 'pf')
    assert pending_id in ids(page), 'Consulting did not resolve the underlying condition'
    page.evaluate("S.personalFinance.months['2026-08'].expenses[0].status='PAGO'")
    refresh(page)
    assert pending_id not in ids(page), {'resolved_still_live': pending_id}
    return {'destination': 'finpes/mensal', 'resolved_id': pending_id, 'consult_does_not_resolve': True}

def calendar_lifecycle(page, _dialogs):
    title = 'SYN Calendário limiar'
    seed_calendar(page, 16, title)
    refresh(page);open_center(page)
    for when in [datetime(2026,9,14,12,0,tzinfo=timezone.utc),datetime(2026,9,14,12,1,tzinfo=timezone.utc),datetime(2026,9,14,12,17,tzinfo=timezone.utc),datetime(2026,9,15,12,0,tzinfo=timezone.utc)]:
        page.clock.set_fixed_time(when)
        page.evaluate('ffNewsRenderAll()');refresh(page)
        assert rows(page).filter(has_text=title).count() == 0, 'Economic agenda is not an action required by the system'
        assert not any(x.startswith('calendar:') for x in ids(page))
    assert page.evaluate('!!ffNewsReadCache()'), 'Removing notifications must not delete the agenda cache'
    return {'economic_agenda_excluded': True, 'threshold_day_rollover': True, 'agenda_preserved': True}

def calendar_cache_and_xss(page, _dialogs):
    title = '<img src=x onerror="window.__notificationXss=1"> SYN texto literal'
    seed_calendar(page, 10, title, 31)
    page.evaluate('ffNewsCacheWriteFailed=true')
    seed_review_contexts(page)
    page.evaluate('name=>{S.accounts.find(a=>a.forexAccountId==="SYN_NOTIFY_A").nome=name}', title)
    refresh(page);open_center(page)
    row=page.locator('[data-notification-id="'+REVIEW_CONTEXTS[0]['notification_id']+'"]')
    assert title in row.inner_text(), 'External account names must remain literal notification text'
    assert page.locator('#notificationList img,#notificationList [onerror]').count() == 0
    assert page.evaluate('window.__notificationXss') == 0
    assert not any(x.startswith('calendar:') for x in ids(page))
    page.evaluate('localStorage.removeItem(FF_NEWS_CACHE_KEY);ffNewsLastError=true;ffNewsCacheWriteFailed=false')
    refresh(page)
    assert not any(x.startswith('calendar:') for x in ids(page)), 'Missing/stale agenda stays in its own surface'
    return {'literal_external_title': True, 'stale_and_missing_agenda_excluded': True}

def native_events_and_exclusions(page, dialogs):
    open_center(page)
    instrument(page);before=snapshot(page)
    initial=ids(page)
    message='SYN alerta nativo <svg onload="window.__notificationXss=2">'
    page.evaluate('message=>alert(message)',message)
    assert dialogs[-1]=={'type':'alert','message':message},dialogs
    refresh(page)
    assert rows(page).filter(has_text=message).count()==0
    assert page.locator('#notificationList svg[onload]').count()==0
    assert page.evaluate('window.__notificationXss')==0
    result=page.evaluate("confirm('SYN confirmação destrutiva não deve virar notificação')")
    assert result is False and dialogs[-1]['type']=='confirm'
    refresh(page)
    assert ids(page)==initial and not any(x.startswith('activity:') for x in ids(page))
    unchanged(page,before)
    return {'native_alert_preserved':True,'native_confirm_preserved':True,'session_history_excluded':True}

def event_area_provenance(page, dialogs):
    page.evaluate("JPWModuleAvailability.setState('alladin','active')")
    page.evaluate("JPWNavigation.navigate('personal-finance')")
    page.evaluate("fbAtoUI({ok:false,erro:'SYN recusa em Finanças Pessoais'})")
    assert dialogs[-1]['type']=='alert' and 'SYN recusa em Finanças Pessoais' in dialogs[-1]['message']
    refresh(page);open_center(page)
    assert rows(page).filter(has_text='SYN recusa em Finanças Pessoais').count()==0
    page.locator('#notificationClose').click()
    page.evaluate("JPWNavigation.navigate('alladin');showSessionNotice('SYN atividade do Alladin')")
    refresh(page);open_center(page)
    assert rows(page).filter(has_text='SYN atividade do Alladin').count()==0
    assert not any(x.startswith('activity:') for x in ids(page))
    return {'native_feedback_preserved':True,'screen_not_inferred_as_origin':True,'unclassified_messages_excluded':True}

def completion_details(page, _dialogs):
    page.evaluate("S.onboarding.done=true;S.onboarding.epStatus='Ainda vou configurar antes de iniciar o período.';S.onboarding.epRestrictiveAccepted=true")
    assert page.evaluate("getOnboardingCompletionState().severity")=='critical'
    refresh(page);open_center(page)
    assert page.locator('[data-notification-id="forex:clearance"]').count()==0
    page.locator('#notificationClose').click()
    assert page.evaluate("JPWNavigation.navigate('forex-overview')")
    assert page.evaluate("getOnboardingCompletionState().severity")=='critical', 'Excluding permanent status must not remove the source warning'
    assert page.evaluate("getOperationalClearance(compute()).status")=='blocked', 'Presentation cannot homologate the normative engine'
    return {'permanent_status_excluded':True,'source_financial_protection_preserved':True}

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
    open_center(page, 'system')
    assert page.locator('[data-notification-id="alladin:quality"]').count() == 1
    unchanged(page,before)
    row=page.locator('[data-notification-id="alladin:quality"]')
    assert row.get_attribute('data-severity') == 'critical'
    prior_diagnostic=row.text_content()
    # Change directly from currency refusal to accumulation overflow (L29 of
    # alladin_ledger_test.py), without an intermediate healthy refresh.
    page.evaluate("""() => {const tx=S.alladin.transactions[0];tx.currency='BRL';
      tx.amount=Number.MAX_SAFE_INTEGER-10;
      S.alladin.transactions.push({...tx,transactionId:'second',amount:20,effectiveAt:'2026-02-02'});}""")
    assert 'ALD_SOMA_FORA_DO_INTEIRO_SEGURO' in page.evaluate("JPWAlladin.leitura.saldoDeCaixa('cash').issues")
    refresh(page)
    assert row.get_attribute('data-severity') == 'critical'
    assert row.text_content()!=prior_diagnostic, 'Changed quality cause must refresh the available diagnosis'
    return {'readable_ledger_does_not_conceal_unavailable_balance': True, 'different_refusal_renews_attention': True}


def unknown_gate(page, _dialogs):
    page.evaluate("markJPWealthPersistenceOutcomeUnknown('SYN notifications test')")
    refresh(page)
    instrument(page)
    before = snapshot(page)
    open_center(page, 'system')
    persistence=page.locator('[data-notification-id=\"system:persistence\"]')
    expect(persistence.locator('h3')).to_contain_text('Gravação não confirmada')
    persistence.locator('summary').click()
    text = page.locator('#notificationList').inner_text().lower()
    assert 'indeterminad' in text or 'desconhecid' in text, text
    count=page.locator('#notificationBadge').inner_text()
    page.locator('#notificationClose').click()
    open_center(page,'system')
    assert page.locator('#notificationBadge').inner_text()==count
    page.locator('#notificationClose').click()
    assert page.evaluate('jpWealthPersistenceOutcomeIsUnknown()')
    outcome=page.evaluate("() => {try{return {returned:save()};}catch(error){return {name:error.name};}}")
    assert outcome == {'name':'JPWealthPersistenceUnknownError'}, outcome
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
        # The compact title may summarize; the complete canonical reason stays
        # accessible in the progressive diagnosis, never silently discarded.
        expect(row).to_contain_text(title)
        if date!='2020-01-01T00:00:00Z':
            expect(row).not_to_contain_text('dias desde a última confirmação')
        page.evaluate('JPWNotifications.close()')
        unchanged(page,before)


def lifecycle_cleanup(page, _dialogs):
    page.evaluate("alert('SYN antes da substituição')")
    open_center(page)
    assert rows(page).filter(has_text='SYN antes da substituição').count() == 0
    page.evaluate('S=structuredClone(S)')
    refresh(page)
    open_center(page)
    assert rows(page).filter(has_text='SYN antes da substituição').count() == 0
    page.locator('#notificationClose').click()
    page.evaluate("alert('SYN antes da finalização')")
    open_center(page)
    assert rows(page).filter(has_text='SYN antes da finalização').count() == 0
    assert not any(x.startswith('activity:') for x in ids(page))
    page.locator('#notificationClose').click()
    before = page.evaluate("""() => {
      S.onboarding.done=true;
      S.onboarding.investorPassword='SYN_NOTIFICATION_SECRET';
      S.riskPinHash='a'.repeat(64);S.phaseUnlocked=[0];
      S.notificationContractSentinel={version:1,confirmed:['SYN fact',{currency:'USD',amount:'123.45'}]};
      if(save()!==true)throw Error('Fixture could not persist before finalization');
      sessionEpochCurrent();markSessionCheckpoint();
      window.__notificationStateBeforeFinalize=S;
      return {document:JSON.parse(localStorage.getItem(LSKEY)),
        cleanupEpoch:window.JP_WEALTH_SESSION_WIPE_EPOCH,
        drafts:jpwWorkspaceCapture().drafts};
    }""")
    assert before['document']['onboarding']['done'] is True
    assert before['document']['onboarding'].get('investorPassword', '') == ''
    assert before['drafts'] == [], 'This lifecycle fixture must not silently discard an unrelated draft'
    page.locator('#finalizeSessionBtn').click()
    page.evaluate('async()=>{await finalizeJPWealthSession();}')
    refresh(page)
    open_center(page)
    assert rows(page).filter(has_text='SYN antes da finalização').count() == 0
    assert not any(x.startswith('activity:') for x in ids(page)), 'Finalization must not rehydrate unclassified history'
    after = page.evaluate("""() => ({replaced:S!==window.__notificationStateBeforeFinalize,
      document:JSON.parse(localStorage.getItem(LSKEY)),state:structuredClone(S),
      cleanupEpoch:window.JP_WEALTH_SESSION_WIPE_EPOCH,
      oldReferenceUntouched:window.__notificationStateBeforeFinalize.onboarding.investorPassword==='SYN_NOTIFICATION_SECRET'
        && window.__notificationStateBeforeFinalize.riskPinHash==='a'.repeat(64)
        && JSON.stringify(window.__notificationStateBeforeFinalize.phaseUnlocked)==='[0]'})""")
    assert after['replaced'] and after['oldReferenceUntouched'], 'Finalization did not replace S independently'
    assert after['cleanupEpoch'] == before['cleanupEpoch'] + 1, 'Session cleanup did not run exactly once'
    # COMPLETE-BACKUP: preserve durable facts, including unknown fields; clear only
    # the declared transient authorization/secrets and capture recoverable drafts.
    # This expected document is independent of the product's final-state builder.
    expected = json.loads(json.dumps(before['document']))
    expected['riskPinHash'] = None
    expected['phaseUnlocked'] = []
    expected['onboarding']['investorPassword'] = ''
    for account in expected.get('accounts', []):
        account['investorPassword'] = ''
    expected['workspaceRecovery'] = {'schemaVersion': 1, 'pending': False, 'drafts': []}
    for target in ['document', 'state']:
        changed = [key for key in set(expected) | set(after[target]) if expected.get(key) != after[target].get(key)]
        assert after[target] == expected, {'target': target, 'unexpected_changed_keys': sorted(changed)}
    assert after['document']['onboarding']['done'] is True and after['state']['onboarding']['done'] is True
    return {'state_replacement_cleanup': True, 'real_finalization_cleanup': True,
            'durable_document_preserved': True, 'unknown_sentinel_preserved': True,
            'transient_cleanup_exact': True, 'unclassified_history_excluded_after_finalization': True}


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
                 'notificationList', 'notificationArea']:
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


def actionable_count_oracle(page):
    current=ids(page)
    assert len(current)==len(set(current)), 'Duplicate cause counted twice'
    assert not any(x.startswith(('calendar:','activity:')) for x in current), 'Excluded activity entered the action count'
    badge=page.locator('#notificationBadge')
    assert badge.inner_text()==str(len(current)), 'Badge must equal the number of active actionable conditions'
    assert badge.is_visible()==bool(current), 'Unresolved actionable conditions cannot be hidden by reading'
    assert page.locator('#notificationReadAll,[data-notification-read]').count()==0
    return len(current)


def actionable_count_contract(page, _dialogs):
    """NA-01: consulting a condition never clears an unresolved action."""
    page.evaluate("S.onboarding.done=true;S.dataGovernance.backup.lastConfirmedAt='2020-01-01T00:00:00Z'")
    refresh(page)
    open_center(page)
    assert page.locator('#notificationReadAll').count() == 0, 'Reading controls conceal unresolved actions'
    assert page.locator('[data-notification-read]').count() == 0
    assert page.locator('[data-notification-id="forex:clearance"]').count() == 0, 'Permanent normative limitation is not a resolvable action'
    before_count = actionable_count_oracle(page)
    assert before_count > 0
    for _ in range(3):
        page.locator('#notificationClose').click()
        page.locator('#headerNotificationsBtn').click()
    assert rows(page).count() == before_count
    assert page.locator('#notificationBadge').inner_text() == str(before_count), 'Consulting unresolved actions changed the active count'
    assert 'lida' not in page.locator('#notificationSummary').inner_text().lower()
    return {'active_count': before_count, 'reading_does_not_resolve': True}


def seed_planning(page):
    # Settle the existing quote provider through its real fixture-backed API
    # before the no-write observation window; notification navigation must not
    # inherit a background bootstrap/cache write unrelated to its own effects.
    page.evaluate('async()=>{await JPWMarket.usdBrl.refresh(false)}')
    return page.evaluate("""()=>{
      const a=JPWPlanning,make=name=>{
        const r=a.commands.execute('createAccount',{name,startMonth:'2026-05',initialUsd:1000,monthlyContributionUsd:100,profileId:'base',goals:{adequate:null,ideal:{value:300,currency:'USD'}}},a.queries.token());
        if(!r.ok)throw Error(JSON.stringify(r));return {id:r.accountId,planId:r.planId,name};
      };
      const accounts=[make('SYN Planejamento A'),make('SYN Planejamento B')];
      for(const c of accounts){const r=a.commands.execute('recordResult',{accountId:c.id,month:'2026-08',usd:0},a.queries.token(c.id));if(!r.ok)throw Error(JSON.stringify(r));}
      return accounts;
    }""")


def source_failure_recovery(page, _dialogs):
    """NA-02: failed verification replaces a condition without hiding its diagnosis."""
    seed_areas(page);open_center(page)
    assert 'pf:pending' in ids(page)
    original_count=rows(page).count()
    instrument(page);before=snapshot(page)
    page.evaluate("window.__notificationPendingReader=pfPendingBefore;pfPendingBefore=()=>{throw Error('SYN unreadable source')};JPWNotifications.invalidate('pf')")
    page.wait_for_function("document.querySelector('[data-notification-id=\"unavailable:pf\"]')")
    failure=page.locator('[data-notification-id="unavailable:pf"]')
    assert 'pf:pending' not in ids(page), 'A stale cause and its failed verifier cannot count twice'
    assert rows(page).count()==original_count
    assert failure.locator('details').count()==1, 'Last known diagnostic remains available under details'
    failure.locator('summary').click()
    assert 'pend' in failure.inner_text().lower()
    assert 'lida' not in page.locator('#notificationSummary').inner_text().lower()
    unchanged(page,before)
    page.evaluate('pfPendingBefore=window.__notificationPendingReader;JPWNotifications.invalidate("pf")')
    page.wait_for_function("document.querySelector('[data-notification-id=\"pf:pending\"]') && !document.querySelector('[data-notification-id=\"unavailable:pf\"]')")
    assert rows(page).count()==original_count
    return {'failed_source_not_healthy':True,'no_double_count':True,'last_diagnostic_retained':True,'recovery':True}


def generation_replacement_diagnosis(page, _dialogs):
    """NA-06: a failed reader cannot carry another document's last diagnosis."""
    seed_areas(page);open_center(page)
    assert page.locator('[data-notification-id="pf:pending"]').count()==1
    prior_month=page.evaluate("new Date('2026-08-15T12:00:00').toLocaleDateString('pt-BR',{month:'short',year:'numeric'})")
    assert prior_month in page.locator('[data-notification-id=\"pf:pending\"]').text_content()
    page.evaluate("window.__notificationPendingReader=pfPendingBefore;pfPendingBefore=()=>{throw Error('SYN unreadable generation')};JPWNotifications.invalidate('pf')")
    page.wait_for_function("document.querySelector('[data-notification-id=\"unavailable:pf\"]')")
    failure=page.locator('[data-notification-id="unavailable:pf"]')
    assert prior_month in failure.text_content(), 'Positive setup: preceding document diagnostic was retained'
    instrument(page);before=snapshot(page)
    page.evaluate("S=structuredClone(S);S.personalFinance.months={};JPWNotifications.invalidate('local')")
    page.wait_for_timeout(50)
    assert prior_month not in failure.text_content(), 'Previous generation diagnostic leaked into the replacement document'
    after=snapshot(page)
    assert after['local']==before['local'] and after['session']==before['session'] and after['writes']==before['writes']
    return {'positive_old_diagnosis':True,'generation_clears_stale_diagnosis':True,'no_persistence':True}


def forex_empty_context_no_action(page, _dialogs):
    """NA-07: an unused period is not a fabricated financial reconciliation."""
    seed_review_contexts(page)
    page.evaluate("""()=>{for(const account of Object.values(S.forex.accountContexts.accounts))for(const period of Object.values(account.periods))for(const phase of period.phases)phase.orders=[];}""")
    instrument(page);before=snapshot(page)
    refresh(page);open_center(page)
    assert not any(x.startswith('forex:') for x in ids(page)), {'spurious_forex_actions':ids(page)}
    unchanged(page,before)
    return {'empty_periods':4,'no_operation_facts_no_action':True,'readonly':True}


def frozen_operational_integrity(page, _dialogs):
    """NA-03: frozen domains stop operational reminders, never data-safety checks."""
    seed_areas(page)
    page.evaluate("JPWModuleAvailability.setState('forex','frozen');JPWModuleAvailability.setState('personal-finance','frozen');JPWNotifications.refresh()")
    instrument(page);before=snapshot(page)
    open_center(page)
    current=ids(page)
    assert not any(x.startswith(('forex:','pf:')) for x in current), current
    row=page.locator('[data-notification-id="alladin:compatibility"]')
    assert row.is_visible() and row.get_attribute('data-area')=='system'
    assert row.get_attribute('data-severity')=='critical'
    assert 'system:backup' in current
    unchanged(page,before)
    return {'operational_frozen_excluded':True,'integrity_frozen_retained':True,'no_readonly_writes':True}


def planning_context_and_guard(page, _dialogs):
    """NA-04: explicit account/month navigation, with dirty-cell cancellation."""
    accounts=seed_planning(page)
    assert page.evaluate("typeof JPWPlanning.queries.pendingActions==='function'")
    query=page.evaluate('JPWPlanning.queries.pendingActions({month:"2026-09"})')
    assert query['available'] and len(query['accounts'])==2, query
    assert all(a['count']==1 and a['firstMonth']=='2026-05' and a['dependencyMonth']=='2026-05' for a in query['accounts']),query
    page.evaluate('x=>JPWPlanning.ui.openMonthlyContext({accountId:x.id,planId:x.planId,month:"2026-05"})', accounts[0])
    page.locator('[data-pl-inline-open="result"][data-pl-inline-month="2026-05"]').click()
    editor=page.locator('[data-pl-inline-editor]')
    if not editor.count():editor=page.locator('.pl-inline-editor')
    field=editor.locator('input[name="value"]')
    field.fill('12.34')
    before_value=field.input_value()
    instrument(page);before=snapshot(page)
    refresh(page);open_center(page)
    target='planning:close:'+accounts[1]['id']+':'+accounts[1]['planId']
    assert target in ids(page),ids(page)
    page.locator('[data-notification-id="'+target+'"] [data-notification-go]').click()
    guard=page.locator('[data-pl-inline-guard]')
    expect(guard).to_be_visible()
    guard.locator('[data-pl-action="inline-continue"]').click()
    assert field.input_value()==before_value
    assert page.locator('[data-pl-account]').input_value()==accounts[0]['id']
    unchanged(page,before)
    field.press('Escape')
    refresh(page);open_center(page)
    page.locator('[data-notification-id="'+target+'"] [data-notification-go]').click()
    page.wait_for_function("JPWNavigation.current().primary==='planning' && JPWPlanning.ui.getView()==='monthly'")
    assert page.locator('[data-pl-account]').input_value()==accounts[1]['id']
    assert page.locator('[data-pl-month]').input_value()=='2026-05'
    assert page.locator('[data-pl-grid-month="2026-05"]').is_visible()
    unchanged(page,before)
    return {'explicit_accounts':2,'zero_result_counts_as_fact':True,'prior_dependency_accessible':True,'cancel_preserves_draft':True,'navigation_no_writes':True}


def forex_guard_generation_before_navigation(page, _dialogs):
    """NA-08: stale consent cannot navigate before its root identity is checked."""
    accounts=seed_planning(page);seed_review_contexts(page)
    page.evaluate('x=>JPWPlanning.ui.openMonthlyContext({accountId:x.id,planId:x.planId,month:"2026-05"})',accounts[0])
    page.locator('[data-pl-inline-open="result"][data-pl-inline-month="2026-05"]').click()
    page.locator('[data-pl-inline-editor] input[name="value"]').fill('12.34')
    refresh(page);open_center(page)
    target=REVIEW_CONTEXTS[1]['notification_id']
    page.locator('[data-notification-id="'+target+'"] [data-notification-go]').click()
    guard=page.locator('[data-pl-inline-guard]')
    expect(guard).to_be_visible()
    before=page.evaluate('({primary:JPWNavigation.current().primary,selection:JPWForex.state.operationalSelection(),state:JSON.stringify(S)})')
    assert before['primary']=='planning'
    page.evaluate('S={...S}')
    guard.locator('[data-pl-action="inline-discard"]').click()
    page.wait_for_timeout(100)
    after=page.evaluate('({primary:JPWNavigation.current().primary,selection:JPWForex.state.operationalSelection(),state:JSON.stringify(S)})')
    assert after['primary']=='planning', 'Stale generation must be rejected before navigation, even when the user consents to discarding a draft'
    assert after['selection']==before['selection'], {'before':before['selection'],'after':after['selection']}
    assert after['state']==before['state'], 'No confirmed financial state is changed by stale navigation recovery'
    return {'root_replaced_during_guard':True,'navigation_prevented':True,'selection_preserved':True}


def planning_month_boundary_clock(page, _dialogs):
    """NA-09: a real local-midnight timer promotes only past recorded months."""
    page.clock.install(time=datetime(2026,10,1,2,59,tzinfo=timezone.utc))
    page.evaluate('async()=>{await JPWMarket.usdBrl.refresh(false)}')
    account=page.evaluate("""()=>{const a=JPWPlanning,r=a.commands.execute('createAccount',{name:'SYN Virada mensal',startMonth:'2026-09',initialUsd:1000,monthlyContributionUsd:100,profileId:'base',goals:{adequate:null,ideal:{value:300,currency:'USD'}}},a.queries.token());if(!r.ok)throw Error(JSON.stringify(r));const actual=a.commands.execute('recordResult',{accountId:r.accountId,month:'2026-09',usd:0},a.queries.token(r.accountId));if(!actual.ok)throw Error(JSON.stringify(actual));return {id:r.accountId,planId:r.planId};}""")
    # Rearm the product's actual timer in the controlled scheduler. There is no
    # direct refresh after time crosses the month boundary.
    page.evaluate("window.dispatchEvent(new Event('pageshow'))")
    open_center(page)
    target='planning:close:'+account['id']+':'+account['planId']
    assert target not in ids(page), 'An in-progress current month is not yet a closure task'
    instrument(page)
    page.evaluate("()=>{window.__notificationFinancialCalls=[];window.__notificationFinancialWriter=jpWealthPersistDocument;jpWealthPersistDocument=function(...args){__notificationFinancialCalls.push({component:args[1]?.component||null,stack:new Error().stack.slice(0,1000)});return __notificationFinancialWriter.apply(this,args)};}")
    before=page.evaluate('({state:JSON.stringify(S),document:localStorage.getItem(LSKEY)})')
    page.clock.fast_forward(60000)
    page.wait_for_function("id=>[...document.querySelectorAll('[data-notification-id]')].some(e=>e.dataset.notificationId===id)",arg=target)
    after=page.evaluate('({state:JSON.stringify(S),document:localStorage.getItem(LSKEY),financialCalls:__notificationFinancialCalls,storageWrites:__notificationWrites,economicKeys:[FF_NEWS_CACHE_KEY,USDBRL_CACHE_KEY]})')
    state_same=after['state']==before['state'];document_same=after['document']==before['document']
    assert state_same and document_same and not after['financialCalls'], {'state_same':state_same,'document_same':document_same,'financial_calls':after['financialCalls'],'storage_writes':after['storageWrites']}
    assert all(w['area']=='local' and w['key'] in after['economicKeys'] for w in after['storageWrites']),after['storageWrites']
    assert page.locator('[data-notification-id="'+target+'"] [data-notification-go]').count()==1
    return {'automatic_local_midnight':True,'current_month_not_promoted':True,'explicit_zero_becomes_past_action':True,'financial_writes':len(after['financialCalls']),'independent_economic_cache_writes':after['storageWrites']}


def forex_price_reference_provenance(page, _dialogs):
    """NA-10: notification freshness follows the price used by the board."""
    seed_review_contexts(page)
    saved=page.evaluate("""()=>{
      if(save()!==true)throw Error('Synthetic reference fixture must persist');
      const api=JPWForex.state,at=new Date().toISOString(),accounts=['SYN_NOTIFY_A','SYN_NOTIFY_B'];
      for(const accountId of accounts){
        const periodId=accountId+'_SEP',currency=S.accounts.find(a=>a.forexAccountId===accountId).platformCurrency;
        const observed=api.recordAccountFacts({accountIndex:S.accounts.findIndex(a=>a.forexAccountId===accountId),periodId,si:10000,equity:10000,netCashflow:0,cashflowAdjustmentRecorded:true,currency,usdToAccountRate:currency==='USD'?1:0.9,source:'SYN equity observation',observedAt:at},{reason:'Synthetic notification provenance fixture'});
        if(!observed.ok)throw Error(JSON.stringify(observed));
        const manual=api.recordInstrumentContext({accountId,periodId,instrumentId:'EURUSD',expectedRevision:0,componentChanges:{price:{value:1.1,source:accountId==='SYN_NOTIFY_A'?'SYN manual fresh':'SYN manual stale',observedAt:accountId==='SYN_NOTIFY_A'?at:'2026-07-02T12:00:00.000Z'}}},{reason:'Synthetic notification price reference'});
        if(!manual.ok)throw Error(JSON.stringify(manual));
      }
      const daily=api.recordDailyReferences({quotes:{EURUSD:{base:'EUR',quote:'USD',rate:1.1,referenceDate:'2026-09-14',fetchedAt:at,source:'Frankfurter',sourceKind:'DAILY_REFERENCE'}},expectedRevision:api.dailyReferenceRevision(),expectedEpoch:jpWealthPersistenceEpoch()},{reason:'Synthetic daily reference fixture'});
      if(!daily.ok)throw Error(JSON.stringify(daily));
      const clean=S.forex.accountContexts.accounts.SYN_NOTIFY_A.periods.SYN_NOTIFY_A_SEP_CLEAN;
      clean.phases[0].orders=[{...S.forex.accountContexts.accounts.SYN_NOTIFY_A.periods.SYN_NOTIFY_A_SEP.phases[0].orders[0],periodId:clean.periodId}];
      S.instruments.find(i=>i.name==='EURUSD').updated='2026-07-02';
      return {manualFresh:api.instrumentContext({accountId:'SYN_NOTIFY_A',periodId:'SYN_NOTIFY_A_SEP',instrumentId:'EURUSD'}).value.price,manualStale:api.instrumentContext({accountId:'SYN_NOTIFY_B',periodId:'SYN_NOTIFY_B_SEP',instrumentId:'EURUSD'}).value.price,daily:api.dailyReference('EURUSD').value};
    }""")
    assert saved['manualFresh']['source']=='SYN manual fresh' and saved['manualStale']['source']=='SYN manual stale'
    instrument(page);before=snapshot(page);requests=[]
    page.on('request',lambda request:requests.append(request.url))
    refresh(page);open_center(page)
    fresh='forex:quotes:SYN_NOTIFY_A:SYN_NOTIFY_A_SEP'
    stale='forex:quotes:SYN_NOTIFY_B:SYN_NOTIFY_B_SEP'
    daily='forex:quotes:SYN_NOTIFY_A:SYN_NOTIFY_A_SEP_CLEAN'
    assert fresh not in ids(page), 'Fresh manual price cannot inherit the stale legacy-catalogue date'
    assert daily not in ids(page), 'Fresh canonical daily fallback cannot inherit the stale legacy date'
    unchanged(page,before);assert requests==[],requests
    page.evaluate("S.instruments.find(i=>i.name==='EURUSD').updated='2026-09-14'")
    before=snapshot(page);refresh(page)
    row=page.locator('[data-notification-id="'+stale+'"]')
    assert row.is_visible(), 'Stale manual price must remain actionable even with a fresh legacy catalogue'
    assert 'SYN manual stale' in row.text_content(), 'The diagnosis identifies the actual price source'
    assert 'NaN' not in row.text_content()
    unchanged(page,before);assert requests==[],requests
    row.locator('[data-notification-go]').click()
    selected=page.evaluate('JPWForex.state.operationalSelection()')
    assert selected['accountId']=='SYN_NOTIFY_B' and selected['periodId']=='SYN_NOTIFY_B_SEP',selected
    assert page.evaluate('JPWNavigation.current().child')=='forex-operation'
    unchanged(page,before);assert requests==[],requests
    return {'manual_fresh_overrides_stale_legacy':True,'manual_stale_overrides_fresh_legacy':True,'daily_fresh_fallback':True,'scoped_quote_navigation':True,'extra_requests':requests}


def planning_touch_navigation(page, _dialogs):
    """NA-05: touch opens the intended month without writing or auto-closing it."""
    accounts=seed_planning(page)
    instrument(page);before=snapshot(page)
    refresh(page);page.locator('#headerNotificationsBtn').tap()
    target='planning:close:'+accounts[1]['id']+':'+accounts[1]['planId']
    page.locator('[data-notification-id="'+target+'"] [data-notification-go]').tap()
    page.wait_for_function("JPWNavigation.current().primary==='planning'")
    assert page.locator('[data-pl-account]').input_value()==accounts[1]['id']
    assert page.locator('[data-pl-month]').input_value()=='2026-05'
    unchanged(page,before)
    return {'real_touch_tap':True,'month':'2026-05','financial_state_preserved':True}


def actionable_counterproofs(page, _dialogs):
    page.evaluate("S.onboarding.done=true;S.dataGovernance.backup.lastConfirmedAt='2020-01-01T00:00:00Z'")
    refresh(page);open_center(page)
    actionable_count_oracle(page)
    rejected=[]
    for mutant in ['hide-unresolved','duplicate-cause','promote-agenda']:
        page.evaluate("""kind=>{
          const list=document.getElementById('notificationList'),badge=document.getElementById('notificationBadge');
          window.__notificationCounterOriginal={html:list.innerHTML,text:badge.textContent,hidden:badge.hidden};
          if(kind==='hide-unresolved'){badge.textContent='0';badge.hidden=true;}
          else{const row=list.querySelector('[data-notification-id]').cloneNode(true);row.dataset.counterproof='true';
            if(kind==='promote-agenda'){row.dataset.notificationId='calendar:event:SYN';badge.textContent=String(Number(badge.textContent)+1);}
            list.append(row);}
        }""",mutant)
        try:actionable_count_oracle(page)
        except AssertionError:rejected.append(mutant)
        finally:
            page.evaluate("""()=>{const x=__notificationCounterOriginal;document.querySelectorAll('[data-counterproof]').forEach(n=>n.remove());const badge=document.getElementById('notificationBadge');badge.textContent=x.text;badge.hidden=x.hidden;}""")
        assert mutant in rejected, 'The common oracle accepted '+mutant
    actionable_count_oracle(page)
    return {'rejected_representative_violations':rejected}


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
                    ('actionable-only-unresolved-count', actionable_count_contract, None, 'light'),
                    ('source-failure-recovery',source_failure_recovery,None,'light'),
                    ('replacement-diagnosis-generation',generation_replacement_diagnosis,None,'light'),
                    ('actionable-counterproofs',actionable_counterproofs,None,'light'),
                    ('frozen-operational-integrity',frozen_operational_integrity,None,'light'),
                    ('forex-empty-context-no-action',forex_empty_context_no_action,None,'light'),
                    ('planning-context-dirty-guard',planning_context_and_guard,None,'light'),
                    ('forex-guard-generation-before-navigation',forex_guard_generation_before_navigation,None,'light'),
                    ('planning-local-month-boundary',planning_month_boundary_clock,None,'light'),
                    ('forex-price-reference-provenance',forex_price_reference_provenance,None,'light'),
                    ('planning-touch-context',planning_touch_navigation,{'width':390,'height':844},'light'),
                    ('all-areas-filter-dedupe-readonly', all_areas_and_readonly, None, 'light'),
                    ('contextual-review-navigation', contextual_review_navigation, None, 'light'),
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
                    for width in [1440, 390, 320]:
                        cases.append((f'keyboard-geometry-{width}-{theme}', keyboard_and_geometry,
                                      {'width': width, 'height': 900 if width == 1440 else 844}, theme))
            if args.case:
                names = {case[0] for case in cases}
                assert set(args.case) <= names, {'unknown_cases': set(args.case)-names}
                cases = [case for case in cases if case[0] in args.case]
            for name, callback, viewport, theme in cases:
                context = None
                try:
                    context, page, dialogs = prepare(browser, url, viewport, theme,
                        personal_finance_active=name in {'resolution-navigation', 'event-area-provenance'}, has_touch=name=='planning-touch-context',timezone_id='America/Sao_Paulo' if name=='planning-local-month-boundary' else 'UTC')
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

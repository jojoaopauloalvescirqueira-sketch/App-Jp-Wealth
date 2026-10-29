#!/usr/bin/env python3
"""Management annual workbook journeys: real DOM, synthetic isolated state.

The first assertion is RED on 3e24f60 because the approved interface is absent.
Financial expectations come from the approved workbook/plan, not UI text copies.
"""
import argparse
import json
import functools
import threading
import math
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from dashboard_macro_test import launch_browser

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def smoke(page):
    assert page.evaluate('!!window.JPWManagement'), 'Approved Management interface is absent'
    page.evaluate("navigateToScreen('management-accounting')")
    assert page.locator('#management').is_visible(), 'Accounting must have its own management screen'
    assert page.locator('#management').get_by_role('heading', name='Caixa Anual').count() == 1
    assert page.locator('#management [data-mg-account]').count() == 1
    assert page.locator('#management [data-mg-account]').input_value() == ''
    assert page.locator('#management [data-mg-action=new-plan]').count() == 0, 'No factual context may be silently assumed'


def seed(page):
    return page.evaluate("""() => {
      const a={forexAccountId:'MGMT-SYN-A',nome:'Conta anual sintética',tipo:'MESTRE',platformCurrency:'USD'};
      S.accounts.push(a);if(save()!==true)throw Error('Synthetic registration not confirmed');
      const r=JPWForex.state.recordAccountPeriod({accountId:a.forexAccountId,startedAt:'2026-01-01',currency:'USD',si:1000,openingBook:1000,source:'Synthetic annual opening',activateCurrentPeriod:false},{reason:'Synthetic fixture confirmed period'});
      if(!r.ok)throw Error(JSON.stringify(r));
      const p=S.forex.accountContexts.accounts[a.forexAccountId];
      return {accountId:a.forexAccountId,periodId:p.currentPeriodId};
    }""")


def choose(page, scope):
    page.locator('#management [data-mg-account]').select_option(scope['accountId'])
    page.locator('#management [data-mg-period]').select_option(scope['periodId'])


def ledger(page, scope):
    return page.evaluate('(t)=>JPWForex.state.accountLedger(t).value', scope)


def configure(page, scope):
    page.locator('#management [data-mg-action=new-plan]').click()
    form=page.locator('#management [data-mg-editor=plan]')
    for name,value in [('startDate','2026-10-01'),('annualTarget','25'),('daysPerWeek','5'),('monthsPerYear','12')]:
        form.locator('[name='+name+']').fill(value)
    assert ledger(page,scope)==[], 'Typing plan cannot write actuals'
    form.locator('[data-mg-action=review-plan]').click()
    assert ledger(page,scope)==[], 'Review cannot write actuals'
    assert page.evaluate("S.managementAnnual===undefined"), 'Review cannot persist configuration'
    form.locator('[name=confirmOpening]').check()
    form.locator('[data-mg-action=confirm-editor]').click()
    assert form.count()==0, 'Confirmed plan should close its editor'
    assert page.locator('[data-mg-action=edit-plan]').evaluate('n=>n===document.activeElement'), 'Plan confirmation must retain a visible focus destination'
    assert ledger(page,scope)==[], 'Saving plan cannot materialize daily closings'
    model=page.evaluate('(t)=>JPWManagementAnnual.queries.model({...t,year:2026})',scope)
    assert model['ok'],model
    s=model['model']['summary']
    assert math.isclose(s['dailyTarget'],1.25**(1/260)-1,rel_tol=1e-9),s
    assert math.isclose(s['fraction'],66/261,rel_tol=1e-12),s
    assert s['pendingDays']>0 and s['realDailyRate'] is None,s


def record(page, day, value, scope):
    page.locator('#management .mg-day [data-mg-action=edit-day][data-mg-date="'+day+'"]').click()
    form=page.locator('#management [data-mg-editor=day]')
    before=ledger(page,scope)
    form.locator('[name=value]').fill(value)
    assert ledger(page,scope)==before, 'Typing must not save'
    form.locator('[data-mg-action=review-day]').click()
    assert ledger(page,scope)==before, 'Review must not save'
    form.locator('[name=confirm]').check()
    form.locator('[data-mg-action=confirm-editor]').click()
    assert form.count()==0, 'Confirmed result should leave the editor'


def journeys(page, out):
    scope=seed(page)
    page.evaluate("navigateToScreen('dashboard'); navigateToScreen('management-accounting')")
    operational=page.evaluate('JSON.stringify(JPWForex.state.operationalSelection())')
    choose(page,scope)
    before=ledger(page,scope)
    page.locator('[data-mg-action=new-plan]').click()
    page.locator('[data-mg-editor=plan] [name=annualTarget]').fill('25')
    page.locator('[data-mg-action=cancel-edit]').click()
    assert page.locator('[data-mg-action=new-plan]').evaluate('n=>n===document.activeElement'), 'Cancelling plan must restore focus to its current trigger'
    assert ledger(page,scope)==before and page.evaluate('S.managementAnnual===undefined')
    configure(page,scope)
    record(page,'2026-10-01','10',scope)
    rows=ledger(page,scope)
    assert len(rows)==1 and rows[0]['resultado']==10 and rows[0]['saldo']==1010,rows
    record(page,'2026-10-02','0',scope)
    rows=ledger(page,scope)
    assert len(rows)==2 and rows[1]['resultado']==0 and rows[1]['saldo']==1010,rows
    assert page.evaluate('JSON.stringify(JPWForex.state.operationalSelection())')==operational
    page.screenshot(path=str(out/'annual-desktop.png'))
    return scope


def review_confirm(page, kind, reason):
    form=page.locator('#management [data-mg-editor="'+kind+'"]')
    form.locator('[name=reason]').fill(reason)
    form.locator('[data-mg-action=review-day]').click()
    form.locator('[name=confirm]').check()
    form.locator('[data-mg-action=confirm-editor]').click()
    assert form.count()==0, 'Confirmation failed: '+form.inner_text()


def declarations_drafts(page, scope):
    day='2026-10-05'
    page.locator('[data-mg-detail="'+day+'"]').click()
    before=ledger(page,scope)
    page.locator('[data-mg-action=no-result][data-mg-date="'+day+'"]').click()
    review_confirm(page,'no-result','Confirmei ausência de resultado realizado neste dia sintético')
    assert ledger(page,scope)==before, 'Declaration cannot create a zero ledger record'
    page.locator('#management .mg-day [data-mg-action=revoke-no-result][data-mg-date="'+day+'"]').click()
    review_confirm(page,'revoke','Correção da declaração sintética antes de informar resultado')
    assert ledger(page,scope)==before
    record(page,day,'-5',scope)
    rows=ledger(page,scope)
    assert len(rows)==3 and rows[-1]['resultado']==-5 and rows[-1]['saldo']==1005,rows
    page.locator('#management .mg-day [data-mg-action=edit-day][data-mg-date="'+day+'"]').click()
    form=page.locator('#management [data-mg-editor=day]')
    form.locator('[name=value]').fill('-4')
    form.locator('[name=note]').fill('Nota sintética mantida no escritor canônico')
    review_confirm(page,'day','Revisão explícita do resultado sintético')
    rows=ledger(page,scope)
    assert len(rows)==3 and rows[-1]['resultado']==-4 and rows[-1]['nota']=='Nota sintética mantida no escritor canônico',rows
    page.locator('[data-mg-action=other-date]').click()
    page.locator('dialog [name=otherDate]').fill('2026-10-03')
    page.locator('dialog [data-mg-action=choose-date]').click()
    page.locator('[data-mg-detail="2026-10-03"]').click()
    page.locator('[data-mg-action=no-result][data-mg-date="2026-10-03"]').click()
    review_confirm(page,'no-result','Dia fora da programação sem resultado, declarado explicitamente')
    assert page.locator('.mg-day[data-mg-date="2026-10-03"]').count()==1, 'Off-calendar declarations must remain visible and revocable'
    page.locator('#management .mg-day [data-mg-action=revoke-no-result][data-mg-date="2026-10-03"]').click()
    review_confirm(page,'revoke','Revogar declaração fora da programação para corrigir resultado')
    page.locator('[data-mg-action=other-date]').click()
    page.locator('dialog [name=otherDate]').fill('2026-10-03')
    page.locator('dialog [data-mg-action=choose-date]').click()
    form=page.locator('#management [data-mg-editor=day]')
    form.locator('[name=value]').fill('2')
    form.locator('[data-mg-action=review-day]').click()
    form.locator('[name=confirm]').check()
    form.locator('[data-mg-action=confirm-editor]').click()
    assert len(ledger(page,scope))==4, 'Off-calendar result must remain a canonical fact'
    assert 'Fora da programação' in page.locator('.mg-day[data-mg-date="2026-10-03"]').inner_text()
    day='2026-10-06'
    page.locator('#management .mg-day [data-mg-action=edit-day][data-mg-date="'+day+'"]').click()
    form=page.locator('#management [data-mg-editor=day]')
    form.locator('[name=value]').fill('17.25')
    form.locator('[data-mg-action=review-day]').click()
    form.locator('[name=confirm]').check()
    unchanged=ledger(page,scope)
    page.evaluate("window.dispatchEvent(new StorageEvent('storage',{key:LSKEY,newValue:localStorage.getItem(LSKEY)}))")
    assert form.locator('[data-mg-action=review-day]').count()==1, 'External data change must offer an explicit review refresh'
    assert form.locator('[name=value]').input_value()=='17.25'
    assert ledger(page,scope)==unchanged
    form.locator('[data-mg-action=review-day]').click()
    assert not form.locator('[name=confirm]').is_checked(), 'A refreshed review cannot retain prior authorization'
    before=ledger(page,scope)
    page.evaluate("navigateToScreen('dashboard')")
    assert page.locator('dialog.mg-dialog[open]').is_visible()
    page.locator('[data-mg-action=guard-stay]').click()
    assert form.locator('[name=value]').input_value()=='17.25'
    assert ledger(page,scope)==before
    page.set_viewport_size({'width':390,'height':844})
    assert form.locator('[name=value]').input_value()=='17.25', 'Responsive presentation cannot replace inputs'
    page.set_viewport_size({'width':1440,'height':1000})
    form.locator('[data-mg-action=cancel-edit]').click()
    assert ledger(page,scope)==before
    assert page.locator('[data-mg-detail="'+day+'"]').evaluate('(n)=>n===document.activeElement')


def annual_closure(page, scope):
    period=page.evaluate("""t=>{
      const r=JPWForex.state.recordAccountPeriod({accountId:t.accountId,startedAt:'2025-01-01',currency:'USD',si:1000,openingBook:1000,source:'Synthetic historical opening',activateCurrentPeriod:false},{reason:'Historical annual fixture'});
      if(!r.ok)throw Error(JSON.stringify(r));
      return Object.values(S.forex.accountContexts.accounts[t.accountId].periods).find(p=>p.startedAt==='2025-01-01').periodId;
    }""",scope)
    historical={**scope,'periodId':period}
    page.evaluate("navigateToScreen('dashboard');navigateToScreen('management-accounting')")
    choose(page,historical)
    page.locator('[data-mg-year]').fill('2025')
    page.locator('[data-mg-year]').press('Tab')
    page.locator('[data-mg-action=new-plan]').click()
    form=page.locator('[data-mg-editor=plan]')
    for name,value in [('startDate','2025-12-31'),('annualTarget','25'),('daysPerWeek','5'),('monthsPerYear','12')]:
        form.locator('[name='+name+']').fill(value)
    form.locator('[data-mg-action=review-plan]').click()
    form.locator('[name=confirmOpening]').check()
    form.locator('[data-mg-action=confirm-editor]').click()
    record(page,'2025-12-31','10',historical)
    before=page.evaluate('JSON.stringify(S)')
    page.locator('[data-mg-action=annual-review]').click()
    assert page.evaluate('JSON.stringify(S)')==before
    page.locator('[data-mg-annual-confirm]').check()
    page.locator('[data-mg-action=annual-confirm]').click()
    assert 'Ano fechado' in page.locator('[data-mg-closure]').inner_text()
    assert page.locator('[data-mg-action=annual-review]').evaluate('n=>n===document.activeElement')
    snapshots=page.evaluate('(t)=>JPWManagementAnnual.queries.model({...t,year:2025}).snapshots',historical)
    assert len(snapshots)==1
    page.locator('#management .mg-day [data-mg-action=edit-day]').click()
    form=page.locator('[data-mg-editor=day]')
    form.locator('[name=value]').fill('12')
    review_confirm(page,'day','Correção após fechamento anual sintético')
    assert 'Reconferência necessária' in page.locator('[data-mg-closure]').inner_text()
    after=page.evaluate('(t)=>JPWManagementAnnual.queries.model({...t,year:2025}).snapshots',historical)
    assert after==snapshots, 'Correction cannot rewrite a confirmed historical snapshot'
    page.locator('[data-mg-action=annual-review]').click()
    page.locator('[data-mg-annual-confirm]').check()
    page.locator('[data-mg-action=annual-confirm]').click()
    assert len(page.evaluate('(t)=>JPWManagementAnnual.queries.model({...t,year:2025}).snapshots',historical))==2
    page.locator('[data-mg-action=history]').click()
    page.locator('[data-mg-action=history-detail]').first.click()
    assert page.locator('.mg-snapshot-table tbody tr').count()==1
    page.locator('dialog [data-mg-action=close-dialog]').click()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('/private/tmp/jpw-portfolio-management-20261026/ui'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    report = {'cases': [], 'source': 'approved human plan / workbook Todas'}
    with BrowserFixtureServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT))) as server, sync_playwright() as pw:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        browser = launch_browser(pw)
        try:
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block')
            install_bootstrap(context, {'USDBRL': 5})
            context.add_init_script('window.__onbShown=true;')
            page = context.new_page()
            page.clock.set_fixed_time(datetime(2026, 10, 26, 15, tzinfo=timezone.utc))
            page_errors = []
            page.on('pageerror', lambda error: page_errors.append(str(error)))
            page.goto('http://127.0.0.1:' + str(server.server_port) + '/index.html')
            wait_bootstrap(page)
            page.evaluate('closeModal();')
            (args.out / 'bootstrap.json').write_text(json.dumps({'errors': page_errors, 'management': page.evaluate("[...document.scripts].filter(s=>s.src.includes('07-management')).map(s=>s.src)")}, indent=2) + '\n')
            assert not page_errors, page_errors
            smoke(page)
            report['cases'].append({'id': 'management-empty-no-assumptions', 'classification': 'PASS'})
            page.screenshot(path=str(args.out / 'empty-desktop.png'))
            scope=journeys(page,args.out)
            declarations_drafts(page,scope)
            annual_closure(page,scope)
            report['cases'] += [{'id': ident, 'classification': 'PASS'} for ident in ['management-plan-and-daily-confirmation','explicit-zero-loss-correction-note','no-result-and-explicit-revocation','off-calendar-daily-entry','draft-navigation-resize-cancel-focus','external-change-explicit-review-refresh','annual-close-reconfirm-immutable-snapshots']]
            context.close()
        finally:
            browser.close()
    (args.out / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS management annual real-browser smoke')


if __name__ == '__main__':
    main()

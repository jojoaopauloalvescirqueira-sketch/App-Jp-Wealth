#!/usr/bin/env python3
"""Real Management context controls resolve Reserve drafts without financial writes."""
import json
from playwright.sync_api import sync_playwright
from research_navigation_test import serve, launch_browser, boot
from fx_consolidated_storage_test import SEED


def snapshot(page):
    return page.evaluate("({state:JSON.stringify(S),stored:localStorage.getItem(LSKEY),operational:JSON.stringify(JPWForex.state.operationalSelection())})")


def run():
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = launch_browser(p)
            context, page, errors = boot(browser, url, {'width': 1440, 'height': 900})
            try:
                page.evaluate(SEED)
                page.evaluate("""() => {
                  for(const [accountId,currency,si] of [['fx_A','USD',10000],['fx_B','EUR',5000]]){
                    const r=JPWForex.state.recordAccountPeriod({accountId,startedAt:'2026-01-01',currency,si,openingBook:si,source:'Synthetic reserve draft fixture',activateCurrentPeriod:true},{reason:'Synthetic reserve draft fixture'});
                    if(!r.ok)throw Error(r.error);
                  }
                  JPWForex.state.selectOperationalAccount('fx_B');
                  window.__reservePeriods=Object.fromEntries(['fx_A','fx_B'].map(id=>[id,S.forex.accountContexts.accounts[id].currentPeriodId]));
                  JPWNavigation.navigate('management-reserves');
                }""")
                account = page.locator('#fxreserves [data-mg-account]')
                period = page.locator('#fxreserves [data-mg-period]')
                account.select_option('fx_A')
                period.select_option(page.evaluate('__reservePeriods.fx_A'))
                form = page.locator('#fxReserveFacts')
                form.evaluate("e=>e.closest('details').open=true")
                form.locator('[name=fcrConstituted]').fill('123')
                form.locator('[name=source]').fill('Synthetic preserved origin')
                form.locator('[name=reason]').fill('Synthetic reserve A draft')
                captured = form.evaluate("f=>({epoch:f.dataset.fxEpoch,revision:f.dataset.fxPeriodRevision,account:f.dataset.fxScopeAccount,period:f.dataset.fxScopePeriod})")
                before = snapshot(page)
                account.focus()
                account_node = account.element_handle()
                account.select_option('fx_B')
                guard = page.locator('dialog.mg-dialog[open]')
                assert guard.is_visible(), 'Changing Reserve context must offer an explicit draft decision'
                assert page.evaluate('JPWManagement.context().accountId') == 'fx_A'
                assert account.input_value() == 'fx_A', 'The declined selection must remain displayed'
                assert account_node.evaluate("e=>e.isConnected&&e===document.querySelector('#fxreserves [data-mg-account]')"), 'Restoring the accepted context preserves the actual control and its focus target'
                guard.locator('[data-mg-action=guard-stay]').click()
                assert account.evaluate('e=>e===document.activeElement'), 'Stay returns focus to the restored context control'
                assert form.locator('[name=fcrConstituted]').input_value() == '123'
                assert snapshot(page) == before
                account.select_option('fx_B')
                guard.locator('[data-mg-action=guard-preserve]').click()
                assert page.evaluate('JPWManagement.context().accountId') == 'fx_B'
                assert form.locator('[name=fcrConstituted]').input_value() == '', 'A draft cannot follow a different account'
                assert form.evaluate("f=>f.dataset.fxTouched!=='true'")
                period.select_option(page.evaluate('__reservePeriods.fx_B'))
                form.locator('[name=fcrConstituted]').fill('456')
                form.locator('[name=reason]').fill('Synthetic reserve B draft')
                assert not page.evaluate("JPWNavigation.navigate('dashboard')"), 'Leaving must await a draft decision'
                page.keyboard.press('Escape')
                assert page.evaluate('JPWNavigation.current().canonical') == 'management-reserves'
                assert form.locator('[name=fcrConstituted]').input_value() == '456'
                assert not page.evaluate("JPWNavigation.navigate('dashboard')")
                guard.locator('[data-mg-action=guard-discard]').click()
                assert page.evaluate('JPWNavigation.current().primary') == 'dashboard'
                assert snapshot(page) == before, 'Draft choices cannot write financial or operational state'
                assert page.evaluate("JPWNavigation.navigate('management-reserves')")
                assert form.locator('[name=fcrConstituted]').input_value() == ''
                account.select_option('fx_A')
                period.select_option(page.evaluate('__reservePeriods.fx_A'))
                assert form.locator('[name=fcrConstituted]').input_value() == '123'
                assert form.locator('[name=source]').input_value() == 'Synthetic preserved origin'
                assert form.locator('[name=reason]').input_value() == 'Synthetic reserve A draft'
                assert form.evaluate("f=>({epoch:f.dataset.fxEpoch,revision:f.dataset.fxPeriodRevision,account:f.dataset.fxScopeAccount,period:f.dataset.fxScopePeriod})") == captured
                assert page.evaluate('JPWManagement.hasPendingWork()')
                drafts = page.evaluate('JPWManagement.backupDrafts(false)')
                reserves = [d for d in drafts if d['context']['action'] == 'reserves']
                assert len(reserves) == 1 and json.loads(reserves[0]['text'])['fields']['fcrConstituted'] == '123'
                assert snapshot(page) == before, 'Collecting a recoverable draft is read-only'
                # A separately confirmed canonical write makes the old revision stale.
                page.evaluate("""() => {
                  const target=JPWManagement.context(),c=JPWForex.state.accountContext(target);
                  const r=JPWForex.state.recordAccountLedger({...target,action:'RECORDED',data:'2026-01-02',resultado:0,saldo:null,nota:'Synthetic concurrent confirmed fact'},
                    {reason:'Synthetic explicit concurrent change',expectedRevision:c.revision,expectedEpoch:jpWealthPersistenceEpoch()});
                  if(!r.ok)throw Error(r.error);JPWForex.ui.render();
                }""")
                stale_before = snapshot(page)
                assert form.evaluate("f=>f.dataset.fxPeriodRevision") == captured['revision'], 'Restoration must not refresh authorization'
                form.locator('[type=submit]').click()
                assert 'alterado' in form.locator('.fx-engine-response').inner_text().lower()
                assert snapshot(page) == stale_before
                assert not page.evaluate("JPWNavigation.navigate('dashboard')")
                guard.locator('[data-mg-action=guard-preserve]').click()
                assert page.evaluate("JPWNavigation.navigate('management-reserves')")
                assert form.locator('[name=fcrConstituted]').input_value() == '123'
                assert form.evaluate("f=>f.dataset.fxPeriodRevision") == captured['revision']
                assert not page.evaluate("JPWNavigation.navigate('management-accounting')")
                guard.locator('[data-mg-action=guard-preserve]').click()
                assert page.evaluate('JPWNavigation.current().canonical') == 'management-accounting'
                assert page.evaluate("JPWNavigation.navigate('management-reserves')")
                assert form.locator('[name=fcrConstituted]').input_value() == '123'
                assert form.evaluate("f=>f.dataset.fxPeriodRevision") == captured['revision']
                assert snapshot(page) == stale_before
                form.locator('[data-fx-refresh-reserves]').click()
                assert snapshot(page) == stale_before, 'An explicit revision refresh still cannot record facts'
                form.locator('[type=submit]').click()
                assert 'confirmado' in form.locator('.fx-engine-response').inner_text().lower()
                assert not page.evaluate('JPWManagement.hasPendingWork()')
                assert page.evaluate('JPWManagement.backupDrafts(false)') == [], 'Confirmed reserves cannot remain as an unsaved recovery draft'
                assert page.evaluate('JPWForex.state.accountContext(JPWManagement.context()).value.reserves.fcrConstituted') == 123
                confirmed_before = snapshot(page)
                form.locator('[name=reason]').fill('RAM-only draft after one confirmed record')
                page.evaluate('JPWManagement.reset()')
                assert not page.evaluate('JPWManagement.hasPendingWork()')
                assert page.evaluate('JPWManagement.backupDrafts(false)') == []
                assert snapshot(page) == confirmed_before, 'Clearing only RAM drafts cannot change financial facts'
                assert not errors['pageerror'], errors
                print(json.dumps({'status':'PASS','cases':['explicit Stay and returned focus','context-scoped Preserve','explicit Discard','Escape','cross-module and same-module navigation decision','original context restore','captured revision preserved','read-only draft recovery','stale write refusal','operational selection unchanged','confirmed write clears recovery draft','RAM reset']},ensure_ascii=False))
            finally:
                context.close()
                browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    run()

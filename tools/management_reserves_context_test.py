#!/usr/bin/env python3
"""Reserve adapter: explicit synthetic context, revision refusal and user-led review refresh.
Context provider is injected only to isolate this adapter; the real Management
selection controls and four-layout navigation have their separate UI regressions.
"""
import json
from playwright.sync_api import sync_playwright
from research_navigation_test import serve,launch_browser,boot
from fx_consolidated_storage_test import SEED

def run():
 s,u=serve()
 try:
  with sync_playwright() as p:
   b=launch_browser(p);c,q,errors=boot(b,u,{'width':1440,'height':900})
   try:
    q.evaluate(SEED)
    q.evaluate('''()=>{
      for(const [accountId,currency,si] of [['fx_A','USD',10000],['fx_B','EUR',5000]]){
        const r=JPWForex.state.recordAccountPeriod({accountId,startedAt:'2026-01-01',currency,si,openingBook:si,source:'Synthetic reserve context fixture',activateCurrentPeriod:true},{reason:'Synthetic reserve fixture'});if(!r.ok)throw Error(r.error);
      }
      JPWForex.state.selectOperationalAccount('fx_B');
      window.__reserveTarget={accountId:'fx_A',periodId:S.forex.accountContexts.accounts.fx_A.currentPeriodId};
      window.__reserveOperational=JSON.stringify(JPWForex.state.operationalSelection());
      window.__reserveManagement=JPWManagement;JPWManagement={...JPWManagement,context:()=>({...__reserveTarget})};
      JPWNavigation.navigate('management-reserves');document.querySelector('#fxReserveFacts').closest('details').open=true;JPWForex.ui.render();
    }''')
    form=q.locator('#fxReserveFacts');form.locator('[name="fcrConstituted"]').fill('100');form.locator('[name="source"]').fill('Synthetic reserve evidence');form.locator('[name="reason"]').fill('Synthetic explicit review')
    q.evaluate('''()=>{const ctx=JPWForex.state.accountContext(__reserveTarget);const r=JPWForex.state.recordAccountLedger({...__reserveTarget,action:'RECORDED',data:'2026-01-02',resultado:0,saldo:null,nota:'Synthetic concurrent fact'},{reason:'Synthetic concurrent change',expectedRevision:ctx.revision,expectedEpoch:jpWealthPersistenceEpoch()});if(!r.ok)throw Error(r.error);JPWForex.ui.render();window.__reserveBefore=JSON.stringify(S);window.__reserveRaw=localStorage.getItem(LSKEY);}''')
    form.locator('[type="submit"]').click()
    assert 'alterado' in form.locator('.fx-engine-response').inner_text().lower()
    assert q.evaluate('JSON.stringify(S)===__reserveBefore&&localStorage.getItem(LSKEY)===__reserveRaw')
    refresh=form.locator('[data-fx-refresh-reserves]');assert refresh.is_visible(),'stale reserve draft needs explicit refresh action'
    refresh.click()
    assert form.locator('[name="fcrConstituted"]').input_value()=='100'
    assert q.evaluate('JSON.stringify(S)===__reserveBefore&&localStorage.getItem(LSKEY)===__reserveRaw'),'refresh cannot write'
    assert not refresh.is_visible()
    assert form.locator('[type="submit"]').evaluate('e=>e===document.activeElement'),'refresh moves focus to the next explicit action'
    form.locator('[type="submit"]').click()
    assert 'confirmado' in form.locator('.fx-engine-response').inner_text().lower()
    assert q.evaluate('JPWForex.state.accountContext(__reserveTarget).value.reserves.fcrConstituted')==100
    assert q.evaluate('JPWForex.state.accountContext(__reserveTarget).value.reserves.previous') is None
    assert q.evaluate('JSON.stringify(JPWForex.state.operationalSelection())')==q.evaluate('__reserveOperational')
    assert not errors['pageerror'],errors
    print(json.dumps({'status':'PASS','cases':['stale refusal','explicit read-only refresh','typed values preserved','one explicitly confirmed observation','operational selection unchanged']}))
   finally:c.close();b.close()
 finally:s.shutdown()
if __name__=='__main__':run()

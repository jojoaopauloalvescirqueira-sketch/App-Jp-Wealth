#!/usr/bin/env python3
"""Synthetic behavior gates for selective notifications and visible rendering."""
import argparse, json, os, threading, traceback
from functools import partial
from notification_center_test import Quiet, ThreadingHTTPServer, ROOT, prepare, seed_areas, open_center
from playwright.sync_api import sync_playwright
from forex_execution_table_test import SEED

PROBE = r'''() => {
 window.__calls={};
 const wrap=(name)=>{const original=window[name];window[name]=function(...args){__calls[name]=(__calls[name]||0)+1;return original.apply(this,args)}};
 for(const name of ['compute','pfPendingBefore','ffNewsReadCache'])wrap(name);
}'''
def idle(page): page.wait_for_timeout(100)
def input_local(page):
    page.evaluate(PROBE)
    page.evaluate("""()=>{__calls={};const e=document.createElement('input');document.body.append(e);e.value='synthetic draft';e.dispatchEvent(new Event('input',{bubbles:true}));}""")
    idle(page)
    calls=page.evaluate('__calls')
    assert all(calls.get(k,0)==0 for k in ['compute','pfPendingBefore','ffNewsReadCache']), calls
    return calls

def selective(page):
    assert page.evaluate("typeof JPWNotifications.invalidate==='function'"), 'Selective invalidation API absent'
    page.evaluate(PROBE)
    page.evaluate("__calls={};JPWNotifications.invalidate('local');JPWNotifications.invalidate('local')")
    idle(page); calls=page.evaluate('__calls')
    assert not any(calls.values()), calls
    page.evaluate("__calls={};JPWNotifications.invalidate('pf');JPWNotifications.invalidate('pf')")
    idle(page); calls=page.evaluate('__calls')
    assert calls.get('pfPendingBefore')==1 and calls.get('compute',0)==0 and calls.get('ffNewsReadCache',0)==0, calls
    return calls

def refresh_cancels(page):
    assert page.evaluate("typeof JPWNotifications.invalidate==='function'"), 'Selective invalidation API absent'
    page.evaluate(PROBE)
    calls=page.evaluate("""async()=>{__calls={};JPWNotifications.invalidate('pf');JPWNotifications.refresh();const before={...__calls};await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));await new Promise(r=>setTimeout(r,100));return {before,after:{...__calls}};}""")
    assert calls['before']==calls['after'], calls
    return calls

def hidden_render(page):
    page.evaluate("JPWNavigation.navigate('personal-finance');closeModal()")
    idle(page)
    result=page.evaluate("""async()=>{const ids=['forexEnginePanel','forexReservesPanel','execOverview'];const nodes=ids.map(id=>document.getElementById(id)).filter(e=>e&&e.getClientRects().length===0);let count=0;const changes=[];const collect=rs=>{rs=rs.filter(r=>!(r.target.nodeType===1?r.target:r.target.parentElement)?.closest('#onboardingIncompleteBanner'));count+=rs.length;changes.push(...rs.map(r=>({target:r.target.id||r.target.parentElement?.id,type:r.type,attribute:r.attributeName})));};const o=new MutationObserver(collect);nodes.forEach(e=>o.observe(e,{subtree:true,childList:true,attributes:true,characterData:true}));render();await Promise.resolve();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));await new Promise(r=>setTimeout(r,100));collect(o.takeRecords());o.disconnect();return {count,changes,hidden:nodes.map(e=>e.id)}}""")
    assert result['hidden'], result
    assert result['count']==0, result
    return result

def catalog_once(page):
    result=page.evaluate("""()=>{const e=document.getElementById('fxRegistryRows');const first=e.firstElementChild;JPWForex.ui.render();JPWForex.ui.render();return {mounted:!!first,preserved:first===e.firstElementChild}}""")
    assert result['mounted'] and result['preserved'], result
    return result

def hidden_flags(page):
    page.evaluate("JPWNavigation.navigate('personal-finance');S.alladin.schemaVersion=999;JPWNotifications.refresh()")
    open_center(page,'alladin')
    assert page.locator('[data-notification-id="alladin:compatibility"]').count()==1
    return {'hidden_critical_flag_present':True}

def committed_hook(page):
    page.evaluate(PROBE)
    result=page.evaluate("""async()=>{__calls={};const refused=pfMutate('synthetic refused',()=>({ok:false,erro:'synthetic refusal'}));await new Promise(r=>setTimeout(r,100));const refusalCalls={...__calls};__calls={};const confirmed=pfMutate('synthetic confirmed',()=>({}));await new Promise(r=>setTimeout(r,100));return {refused,confirmed,refusalCalls,confirmedCalls:{...__calls}}}""")
    assert result['refused']['persistido'] is False and result['refusalCalls'].get('pfPendingBefore',0)==0,result
    assert result['confirmed']['persistido'] is True and result['confirmedCalls'].get('pfPendingBefore')==1,result
    return result

def entry_current_state(page):
    page.evaluate("JPWNavigation.navigate('personal-finance');S.protocolBreaches=17;JPWNavigation.navigate('forex-consolidated');fxSetContextExpanded(true)")
    assert '17' in page.locator('#breachNote').inner_text()
    return {'entry_reads_current_state':True}

def mounted_draft_focus(page):
    page.evaluate("JPWNavigation.navigate('forex-reserves')")
    result=page.evaluate("""()=>{const form=document.getElementById('fxReserveFacts');form.closest('details')?.setAttribute('open','');const e=form.elements.reason;e.value='SYN preserved draft';e.dispatchEvent(new Event('input',{bubbles:true}));e.focus();const before=form.dataset.fxFactsFingerprint;render();return {same:form===document.getElementById('fxReserveFacts'),value:e.value,focused:document.activeElement===e,touched:form.dataset.fxTouched,fingerprintBefore:before,fingerprintAfter:form.dataset.fxFactsFingerprint}}""")
    assert result['same'] and result['focused'] and result['value']=='SYN preserved draft' and result['touched']=='true',result
    assert result.get('fingerprintBefore')==result.get('fingerprintAfter'),result
    return result

def moved_clearance_current(page):
    page.evaluate("JPWNavigation.navigate('personal-finance');document.getElementById('mcClearanceTitle').textContent='SYN stale';document.getElementById('gdVrmValue').textContent='SYN stale VRM';JPWNavigation.navigate('forex-consolidated');fxSetContextExpanded(true)")
    assert page.locator('#mcClearanceCard').is_visible()
    title=page.locator('#mcClearanceTitle').inner_text()
    assert title!='SYN stale',{'title':title}
    vrm=page.locator('#gdVrmValue').inner_text()
    assert vrm!='SYN stale VRM',{'vrm':vrm}
    return {'current_title':title,'vrm':vrm}

def facts_details_demand(page):
    page.evaluate(SEED.replace("2026-09-22", "2026-09-14"))
    page.evaluate("JPWNavigation.navigate('forex-management-accounts')")
    details=page.locator('#fxAccountFacts').locator('..')
    details.evaluate("e=>e.open=false")
    page.evaluate("const f=document.getElementById('fxAccountFacts');f.dataset.fxTouched='';f.elements.si.value='';f.elements.currency.value='EUR';f.elements.accountIndex.replaceChildren();delete f.dataset.fxFactsFingerprint;JPWForex.ui.render()")
    assert page.locator('#fxAccountFacts [name=si]').input_value()=='', 'Closed facts details was populated before demand'
    details.locator('summary').click();idle(page)
    values=page.evaluate("""()=>{const f=document.getElementById('fxAccountFacts');return {si:f.elements.si.value,currency:f.elements.currency.value,options:f.elements.accountIndex.options.length,fingerprint:!!f.dataset.fxFactsFingerprint}}""")
    assert values=={'si':'10000','currency':'USD','options':1,'fingerprint':True},values
    result=page.evaluate("""()=>{const f=document.getElementById('fxAccountFacts'),e=f.elements.reason;e.value='SYN draft';e.dispatchEvent(new Event('input',{bubbles:true}));e.focus();JPWForex.ui.render();return {same:f===document.getElementById('fxAccountFacts'),draft:e.value,focus:document.activeElement===e}}""")
    assert result=={'same':True,'draft':'SYN draft','focus':True},result
    return values

def budget_real_host(page):
    page.evaluate("JPWNavigation.navigate('forex-reserves');document.getElementById('fxBudgetContext').textContent='SYN untouched';document.getElementById('fxBudgetHistory').textContent='SYN history';JPWForex.ui.render()")
    hidden={'context':page.locator('#fxBudgetContext').text_content(),'history':page.locator('#fxBudgetHistory').text_content()}
    assert hidden=={'context':'SYN untouched','history':'SYN history'},hidden
    page.evaluate("openSettingsModal('tool-params');document.getElementById('fxOperationBudget').closest('details').open=false")
    details=page.locator('#fxOperationBudget').locator('..')
    details.locator('summary').first.click();idle(page)
    current=page.locator('#fxBudgetContext').text_content()
    assert current!='SYN untouched' and 'Orçamento:' in current,current
    assert page.locator('#fxBudgetHistory').text_content()!='SYN history'
    return {'hidden_preserved':hidden,'opened_current':current}

def unavailable_calendar_destination(page):
    page.evaluate("JPWNavigation.navigate('personal-finance');ffNewsReadCache=()=>{throw Error('SYN unavailable')};JPWNotifications.refresh()")
    open_center(page,'research')
    page.locator('[data-notification-id="unavailable:collectCalendar"] [data-notification-go]').click()
    current=page.evaluate('JPWNavigation.current()')
    assert current['primary']=='research',current
    return current

def context_alias_single_paint(page):
    page.evaluate("JPWNavigation.navigate('forex-consolidated');JPWNavigation.navigate('personal-finance')")
    result=page.evaluate("""()=>{let paints=0;const original=renderPresentation;renderPresentation=function(...a){paints++;return original.apply(this,a)};const accepted=JPWNavigation.navigate('forex-overview');renderPresentation=original;return {accepted,paints}}""")
    assert result=={'accepted':True,'paints':1},result
    return result

def first_context_entry_expanded(page):
    page.evaluate("JPWNavigation.navigate('forex-overview')")
    overview=page.locator('#execOverview')
    assert overview.is_visible(), 'First compatibility context entry remained hidden'
    return {'first_context_visible':True}

def settings_close_exposure(page):
    page.evaluate(SEED.replace("2026-09-22", "2026-09-14"))
    page.evaluate("JPWNavigation.navigate('forex-overview')")
    before=page.locator('#mDD').text_content()
    result=page.evaluate("""()=>{openSettingsModal('tool-params');const scope=JPWForex.state.operationalSelection();const r=JPWForex.state.recordAccountFacts({accountIndex:0,periodId:scope.periodId,si:10000,equity:9500,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',source:'Synthetic updated equity',observedAt:'2026-09-14T12:00:00Z'},{reason:'Synthetic settings observation'});render();return r}""")
    assert result['persistido'] is True,result
    assert page.locator('#mDD').text_content()==before, 'Hidden financial projection was painted'
    page.evaluate('closeSettingsModal()');idle(page)
    status=page.locator('#mDD').text_content()
    expected=page.evaluate('fmtPct(compute().dd)')
    assert status==expected and status!=before,{'before':before,'after':status,'expected':expected}
    return {'writer_confirmed':True,'hidden_value':before,'exposed_value':status}

def settings_consolidated_inert(page):
    # Regression: active Consolidado remains mounted while Settings inerts appMain.
    # A confirmed financial writer must not reconstruct that hidden host.
    page.evaluate(SEED.replace("2026-09-22", "2026-09-14"))
    page.evaluate("JPWNavigation.navigate('forex-overview')")
    idle(page)
    before=page.locator('#mDD').text_content()
    result=page.evaluate("""async()=>{
      openSettingsModal('tool-params');
      const root=document.getElementById('fxconsolidated');
      const identity=document.getElementById('fxcIdentity').firstElementChild;
      let mutations=0;const changes=[];
      const collect=rs=>{for(const r of rs){const target=r.target.nodeType===1?r.target:r.target.parentElement;
        if(target?.closest('#onboardingIncompleteBanner'))continue;
        mutations++;if(changes.length<15)changes.push({target:target?.id,type:r.type,attribute:r.attributeName});}};
      const observer=new MutationObserver(collect);
      observer.observe(root,{subtree:true,childList:true,attributes:true,characterData:true});
      const scope=JPWForex.state.operationalSelection();
      const writer=JPWForex.state.recordAccountFacts({accountIndex:0,periodId:scope.periodId,si:10000,equity:9500,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',source:'Synthetic updated equity',observedAt:'2026-09-14T12:00:00Z'},{reason:'Synthetic settings observation'});
      render();await Promise.resolve();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      collect(observer.takeRecords());observer.disconnect();
      return {writer,inert:!!root.closest('[inert]'),mutations,changes,identityPreserved:identity===document.getElementById('fxcIdentity').firstElementChild};
    }""")
    assert result['writer']['persistido'] is True and result['inert'],result
    assert result['mutations']==0 and result['identityPreserved'],result
    assert page.locator('#mDD').text_content()==before, result
    page.evaluate('closeSettingsModal()');idle(page)
    after=page.locator('#mDD').text_content()
    assert after=='5,00%' and after!=before, {'before':before,'after':after}
    assert page.locator('#fxcIdentity .fxc-operating-identity').is_visible()
    return {**result,'hidden_value':before,'exposed_value':after}

def first_canonical_summary(page):
    page.evaluate("JPWNavigation.navigate('forex-consolidated')")
    text=page.locator('#fxOperationalSummary').inner_text()
    assert 'Conta operacional' in text,text
    assert 'Período operacional' in text,text
    return {'summary_current':True}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',action='append',default=[]);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.environ['JP_WEALTH_CHROMIUM'])
        for name,case in [('local-input-no-financial-collectors',input_local),('selective-source-coalescing',selective),('full-refresh-drains-dirty',refresh_cancels),('hidden-dom-zero-writes',hidden_render),('immutable-catalog-mounted-once',catalog_once),('hidden-critical-flags',hidden_flags),('committed-pf-hook-only',committed_hook),('entry-reads-current-state',entry_current_state),('mounted-draft-focus',mounted_draft_focus),('moved-clearance-current',moved_clearance_current),('facts-details-on-demand',facts_details_demand),('budget-real-host',budget_real_host),('unavailable-calendar-destination',unavailable_calendar_destination),('context-alias-single-paint',context_alias_single_paint),('first-context-entry-expanded',first_context_entry_expanded),('settings-close-exposure',settings_close_exposure),('first-canonical-summary',first_canonical_summary),('settings-consolidated-inert',settings_consolidated_inert)]:
          if args.case and name not in args.case:continue
          context=None
          try:
            context,page,_=prepare(browser,f'http://127.0.0.1:{server.server_port}/index.html');idle(page)
            results.append({'case':name,'result':'PASS','evidence':case(page)})
          except Exception as exc: results.append({'case':name,'result':'PRODUCT_FAIL' if isinstance(exc,AssertionError) else 'TEST_HARNESS_FAIL','evidence':str(exc),'trace':traceback.format_exc()})
          finally:
            if context:context.close()
        browser.close()
    finally:server.shutdown();server.server_close()
    print(json.dumps(results,indent=2,ensure_ascii=False));return int(any(r['result']!='PASS' for r in results))
if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Consolidado lazy tabs: real imports, hidden DOM and chart interaction regressions."""
import argparse, hashlib, json, os, threading, traceback
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright
from notification_center_test import Quiet, ThreadingHTTPServer, ROOT, prepare
from forex_professional_panel_test import seed, long_report

BINDINGS = r'''(() => {
  window.__chartDuplicateBindings=[];const seen=new WeakMap(),add=EventTarget.prototype.addEventListener;
  EventTarget.prototype.addEventListener=function(type,fn,options){
    if(this instanceof Element&&this.closest('figure[data-fxc-series]')&&['click','input','pointerdown','pointermove'].includes(type)){
      const counts=seen.get(this)||{};counts[type]=(counts[type]||0)+1;seen.set(this,counts);
      if(counts[type]>1)__chartDuplicateBindings.push({type,element:this.className,count:counts[type]});
    }
    return add.call(this,type,fn,options);
  };
})();'''
def settle(page):
    page.evaluate('async()=>{await Promise.resolve();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}')

def hidden_tabs(page):
    assert page.locator('#fxconsolidated [role=tabpanel][hidden]').evaluate_all('panels=>panels.every(p=>!p.firstElementChild)'), 'Inactive tabs eagerly mounted on first entry'
    for tab in ['history','statistics','risks','account']:
        page.locator('#fxcTab-'+tab).click();settle(page)
    evidence=[]
    for tab in ['account','history','statistics','risks']:
        page.locator('#fxcTab-'+tab).click();settle(page)
        value=page.evaluate('''async()=>{
          const panels=[...document.querySelectorAll('#fxconsolidated [role=tabpanel]')].filter(p=>p.hidden);
          const old=panels.map(p=>({id:p.id,child:p.firstElementChild,html:p.innerHTML}));
          let mutations=0;const targets=[];
          const collect=rs=>{mutations+=rs.length;for(const r of rs)if(targets.length<12)targets.push({id:r.target.id||r.target.parentElement?.id,type:r.type,attribute:r.attributeName,added:r.addedNodes.length,removed:r.removedNodes.length})};
          const observer=new MutationObserver(collect);panels.forEach(p=>observer.observe(p,{subtree:true,childList:true,characterData:true,attributes:true}));
          JPWFXConsolidated.render();JPWFXConsolidated.render();
          await Promise.resolve();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
          collect(observer.takeRecords());observer.disconnect();
          return {mutations,targets,hidden:old.map(x=>({id:x.id,sameNode:x.child===document.getElementById(x.id).firstElementChild,sameMarkup:x.html===document.getElementById(x.id).innerHTML})),duplicateBindings:__chartDuplicateBindings};
        }''')
        evidence.append({'active':tab,**value})
    assert all(v['mutations']==0 and all(p['sameNode'] and p['sameMarkup'] for p in v['hidden']) for v in evidence),evidence
    assert not page.evaluate('__chartDuplicateBindings'),evidence
    return evidence

def fresh_entry(page):
    page.locator('#fxcTab-statistics').click();page.locator('#fxcTab-history').click();page.locator('#fxcTab-account').click();settle(page)
    page.evaluate("window.__oldStatistics=document.getElementById('fxcPanel-statistics').firstElementChild;window.__oldHistory=document.getElementById('fxcPanel-history').firstElementChild")
    revised=long_report().replace(b'<td>120</td>',b'<td>220</td>')
    assert revised!=long_report()
    writer=page.evaluate('''async({html,hash})=>{
      const report=JPWFXConsolidated.parseHTML(html);
      const preview=JPWFXConsolidated.prepareImport(report,'PANEL-A',{fileHash:hash,fileName:'synthetic-revision.html',importedAt:'2026-10-14T12:00:00Z'});
      if(!preview.ok)throw Error(JSON.stringify(preview));
      return await JPWFXConsolidated.confirmImport(preview,{confirmIdentity:true,acceptRevision:true});
    }''',{'html':revised.decode(),'hash':hashlib.sha256(revised).hexdigest()})
    assert writer['ok'] and writer['persistido'],writer
    page.evaluate('JPWFXConsolidated.render()');settle(page)
    assert page.evaluate("__oldStatistics===document.getElementById('fxcPanel-statistics').firstElementChild&&__oldHistory===document.getElementById('fxcPanel-history').firstElementChild"),'Confirmed writer repainted inactive tab'
    assert '275' in page.locator('#fxcPanel-account .fxc-primary-kpis').inner_text()
    page.locator('#fxcTab-history').click()
    net=page.locator('#fxcPanel-history tbody tr').filter(has=page.locator('td:nth-child(2)',has_text='102')).first.locator('[data-value]').get_attribute('data-value')
    assert net=='218',net
    page.locator('#fxcTab-statistics').click()
    payoff=page.locator('#fxcPanel-statistics .fxc-metric').filter(has=page.locator('dt',has_text='Resultado líquido / saídas')).locator('dd').inner_text()
    assert payoff=='55 USD',payoff
    return {'writer':writer,'updatedDealNet':net,'expectedPayoff':payoff,'hiddenPreservedUntilEntry':True}

def presentation(page):
    page.set_viewport_size({'width':390,'height':900})
    page.locator('#fxcTab-account').click()
    # Constrain the real values-table viewport so its actual rows can scroll.
    page.add_style_tag(content='#fxcPanel-account .fxc-chart-values .fxc-scroll{max-height:120px}')
    chart=page.locator('#fxcPanel-account figure[data-fxc-series=main]')
    chart.locator('details summary').click()
    chart.locator('.fxc-chart-cursor').focus();page.keyboard.press('Home')
    for _ in range(4):page.keyboard.press('ArrowRight')
    state=page.evaluate('''()=>{
      const p=document.getElementById('fxcPanel-account'),f=p.querySelector('[data-fxc-series=main]'),cursor=f.querySelector('input');
      cursor.focus();const scroll=f.querySelector('.fxc-scroll');scroll.scrollTop=37;
      return {ticket:f.dataset.selectedTicket,point:f.dataset.selectedPoint,scroll:scroll.scrollTop,focus:cursor.id};
    }''')
    if state['scroll']<=0:raise RuntimeError('Scroll fixture did not overflow: '+str(state))
    page.evaluate('JPWFXConsolidated.render();JPWFXConsolidated.render()');settle(page)
    restored=page.evaluate('''()=>{const f=document.querySelector('#fxcPanel-account [data-fxc-series=main]');return {ticket:f.dataset.selectedTicket,point:f.dataset.selectedPoint,scroll:f.querySelector('.fxc-scroll').scrollTop,focus:document.activeElement.id,open:f.querySelector('details').open}}''')
    assert all(restored[k]==v for k,v in state.items()) and restored['open'],{'before':state,'after':restored}
    for tab in ['history','statistics','risks','history','statistics','account']:
        page.locator('#fxcTab-'+tab).click();settle(page)
    chart=page.locator('#fxcPanel-account figure[data-fxc-series=main]')
    assert chart.get_attribute('data-selected-point')=='4'
    chart.locator('.fxc-chart-next').click();settle(page)
    assert chart.get_attribute('data-selected-point')=='5','One click advanced more than one observation'
    assert not page.evaluate('__chartDuplicateBindings'),page.evaluate('__chartDuplicateBindings')
    return {'before':state,'after':restored,'oneClickAdvancedTo':'5','duplicateBindings':[]}

def inert_host(page):
    page.evaluate("openSettingsModal('forex-consolidated')")
    evidence={}
    for operation in ['draw','render']:
        evidence[operation]=page.evaluate("""async operation=>{
          const root=document.getElementById('fxconsolidated');let mutations=0;const targets=[];
          const collect=rs=>{for(const r of rs){const target=r.target.nodeType===1?r.target:r.target.parentElement;if(target?.closest('#onboardingIncompleteBanner'))continue;
            mutations++;if(targets.length<8)targets.push({id:target?.id,type:r.type});}};
          const observer=new MutationObserver(collect);observer.observe(root,{subtree:true,attributes:true,childList:true,characterData:true});
          if(operation==='draw')root.querySelector('.fxc-chart-plot')._fxcDraw();else JPWFXConsolidated.render();
          await Promise.resolve();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
          collect(observer.takeRecords());observer.disconnect();return {mutations,targets,inert:!!root.closest('[inert]')};
        }""",operation)
    # Exercise the actual Settings preference writer/handler which calls FX.render.
    page.locator('#fxcDefaultAccount').select_option('PANEL-A')
    page.evaluate("""()=>{window.__settingsRootWrites=0;window.__settingsRootChanges=[];const root=document.getElementById('fxconsolidated');window.__settingsRootObserver=new MutationObserver(rs=>{__settingsRootWrites+=rs.length;for(const r of rs)__settingsRootChanges.push({id:r.target.id||r.target.parentElement?.id,type:r.type,attribute:r.attributeName,added:r.addedNodes.length,removed:r.removedNodes.length});});__settingsRootObserver.observe(root,{subtree:true,attributes:true,childList:true,characterData:true});}""")
    page.locator('#fxcSaveDefault').click()
    page.wait_for_function("document.getElementById('fxcDefaultStatus').textContent==='Preferência salva.'")
    settle(page)
    evidence['preferenceWriter']=page.evaluate("""()=>{__settingsRootWrites+=__settingsRootObserver.takeRecords().length;__settingsRootObserver.disconnect();return {mutations:__settingsRootWrites,changes:__settingsRootChanges,importResultHidden:document.getElementById('fxcImportResult').hidden,remainingImportChildren:document.getElementById('fxcImportResult').childNodes.length,saved:S.fxConsolidated.defaultAccountId==='PANEL-A'};}""")
    page.evaluate('closeSettingsModal()')
    page.set_viewport_size({'width':1000,'height':900})
    page.wait_for_function("""()=>{const plot=document.querySelector('#fxcPanel-account .fxc-chart-plot'),svg=plot?.querySelector('svg');return !!svg&&plot.clientWidth>0&&svg.viewBox.baseVal.width===plot.clientWidth;}""")
    evidence['exposedRedraw']=page.evaluate("""()=>{const p=document.querySelector('#fxcPanel-account .fxc-chart-plot');return {width:p.clientWidth,svgWidth:p.querySelector('svg').viewBox.baseVal.width,segments:p.querySelectorAll('[data-fxc-segment]').length};}""")
    assert all(evidence[k]['inert'] and evidence[k]['mutations']==0 for k in ['draw','render']),evidence
    cleanup=evidence['preferenceWriter']
    # Existing cancel() explicitly clears the import notice after this command.
    # Account for those exact removals/hidden attribute; every other region,
    # including all four financial tabpanels, must remain unchanged.
    assert cleanup['saved'] and cleanup['importResultHidden'] and cleanup['remainingImportChildren']==0,evidence
    assert cleanup['mutations']==len(cleanup['changes']),evidence
    assert all(r['id']=='fxcImportResult' and
        ((r['type']=='childList' and r['added']==0) or (r['type']=='attributes' and r['attribute']=='hidden'))
        for r in cleanup['changes']),evidence
    cleanup['explicitCancelCleanupOnly']=True
    assert evidence['exposedRedraw']['segments']>0,evidence
    return evidence

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();args.out.parent.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.environ['JP_WEALTH_CHROMIUM'])
        for name,case in [('hidden-tabs-preserved',hidden_tabs),('current-model-on-entry',fresh_entry),('presentation-and-single-chart-binding',presentation),('inert-host-render-preference-and-resize',inert_host)]:
          ctx=None
          try:
            ctx,page,_=prepare(browser,f'http://127.0.0.1:{server.server_port}/index.html');page.clock.set_fixed_time(datetime(2026,10,14,12,tzinfo=timezone.utc));page.evaluate(BINDINGS);seed(page);settle(page)
            evidence=case(page);assert not page.notification_errors,page.notification_errors
            results.append({'case':name,'result':'PASS','evidence':evidence})
          except Exception as e:results.append({'case':name,'result':'PRODUCT_FAIL' if isinstance(e,AssertionError) else 'TEST_HARNESS_FAIL','evidence':str(e),'trace':traceback.format_exc()})
          finally:
            if ctx:ctx.close()
        browser.close()
    finally:server.shutdown();server.server_close()
    report={'source_sha256':hashlib.sha256((ROOT/'src/js/20-ui/28-fx-consolidated.js').read_bytes()).hexdigest(),'results':results}
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,indent=2,ensure_ascii=False));return int(any(x['result']!='PASS' for x in results))
if __name__=='__main__':raise SystemExit(main())

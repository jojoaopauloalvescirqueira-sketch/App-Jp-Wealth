#!/usr/bin/env python3
"""Contas e Período: synthetic UI context, drafts, persistence and rollback.
No real browser profile or financial data. Functional assertions precede captures.
"""
import argparse, json, hashlib, threading, traceback
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options, settle
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass
SEED=r'''() => {
 window.__onbShown=true;closeModal(); S=structuredClone(DEFAULTS);migrate();S.onboarding.done=true;
 S.accounts=[['A','MESTRE','base'],['B','PRÓPRIA','longevity']].map(([suffix,tipo,key])=>{
   const a={forexAccountId:'CONTA-'+suffix,nome:'Conta sintética '+suffix+' — identificação longa para revisão',tipo,platform:'MetaTrader 5',platformLogin:'00000'+suffix,platformCurrency:'USD',broker:'Corretora sintética',platformServer:'Servidor de demonstração',accountEnvironment:'demo'};
   a.riskProfileAssignment=JPWForex.state.createRiskProfileAssignment(a,key,{source:'Synthetic fixture',declaredBy:'Synthetic operator',reason:'Initial profile declaration'});a.perfil=riskProfileByAny(key).name;return a;
 });
 S.forex=JPWForex.state.empty(); S.operationHistory={schemaVersion:2,records:[]};if(!save())throw Error('Seed refused');
 for(const a of S.accounts){const r=JPWForex.state.recordAccountPeriod({accountId:a.forexAccountId,startedAt:'2026-01-01',currency:'USD',si:10000,openingBook:10000,source:'Synthetic fixture',activateCurrentPeriod:true},{reason:'Explicit synthetic period'});if(!r.ok)throw Error(JSON.stringify(r));}
 window.__periodA=S.forex.accountContexts.accounts['CONTA-A'].currentPeriodId;window.__periodB=S.forex.accountContexts.accounts['CONTA-B'].currentPeriodId;
 if(!JPWForex.state.selectOperationalContext('CONTA-A',__periodA).ok)throw Error('Context refused');render();JPWNavigation.navigate('forex-management-accounts');JPWForex.accountsUI.render();
}'''
def snap(page):return page.evaluate('JSON.stringify({state:S,raw:localStorage.getItem(LSKEY)})')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--baseline',type=Path);ap.add_argument('--case',default='');args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
    report={'cases':[],'build':(ROOT/'build-id.js').read_text().splitlines()[1],'sourceHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'index.html',ROOT/'src/js/20-ui/31-forex-accounts.js',ROOT/'src/js/40-app/24-fx-consolidated-import.js',ROOT/'src/js/10-domain/00-forex-state.js']}}
    with sync_playwright() as pw:
      browser=pw.chromium.launch(**launch_options())
      def run(name,fn):
        if args.case and args.case not in name:return
        ctx=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block');install_bootstrap(ctx);ctx.add_init_script('window.__onbShown=true;');page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept());rec={'name':name}
        try:
          page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page);page.evaluate(SEED);settle(page);fn(page,ctx);assert not errors,errors;assert_fixture_requests(ctx);rec['status']='PASS'
        except Exception as e:rec.update(status='PRODUCT_FAIL' if isinstance(e,AssertionError) else 'TEST_HARNESS_FAIL',error=str(e),trace=traceback.format_exc())
        finally:rec['pageerrors']=errors;ctx.close();report['cases'].append(rec);print(name,rec['status'],rec.get('error','')[:250],flush=True)
      def context(page,ctx):
        before=snap(page);old=page.evaluate('JPWForex.state.operationalSelection()')
        page.locator('[data-fx-examine="CONTA-B"]').click()
        assert page.evaluate('JPWForex.accountsUI.examination().accountId')=='CONTA-B'
        assert page.evaluate('JPWForex.state.operationalSelection()')==old
        assert snap(page)==before
        route=page.evaluate('JPWNavigation.current()')
        assert not page.evaluate("JPWForex.accountsUI.useContext('CONTA-B',__periodA)")
        assert page.evaluate('JPWNavigation.current()')==route and page.evaluate('JPWForex.state.operationalSelection()')==old
        page.evaluate('window.__navGuard=JPWForex.executionBoardUI.guardNavigation;JPWForex.executionBoardUI.guardNavigation=()=>false')
        assert not page.evaluate("JPWForex.accountsUI.useContext('CONTA-B',__periodB)")
        assert page.evaluate('JPWForex.state.operationalSelection()')==old
        page.evaluate('()=>{JPWForex.executionBoardUI.guardNavigation=__navGuard;}')
        page.locator('#fxAccountsUse').click();settle(page)
        assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='CONTA-B'
        assert page.locator('#executionBoard').is_visible()
        assert page.locator('#ebAccountSelect,[data-eb-manual],[data-eb-setup],#execWidgetGrid #accountPeriodCard').count()==0
        assert page.locator('[data-eb-manage]').is_visible()
        assert 'Longevity' in page.locator('#hdrProfile').inner_text()
        assert snap(page)==before
      run('examination-context-pair-no-writes',context)
      def registry_epoch(page,ctx):
        before=snap(page)
        observed=page.evaluate("""()=>{
          const results=[],key=BASE_EPOCH_STORAGE_KEY,original=Storage.prototype.setItem;
          const absent=()=>localStorage.removeItem(key);
          absent();const created=JPWFXConsolidated.beginRegistration(null,null),epoch=sessionEpochRead();JPWFXConsolidated.cancelRegistration();
          results.push(created.ok&&typeof epoch==='string'&&!!epoch);
          const second=JPWFXConsolidated.beginRegistration(null,null);JPWFXConsolidated.cancelRegistration();results.push(second.ok&&sessionEpochRead()===epoch);
          for(const mode of ['throw','noop']){absent();Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===key){if(mode==='throw')throw new DOMException('Synthetic denied','QuotaExceededError');return;}return original.call(this,k,v);};
            const refused=JPWFXConsolidated.beginRegistration(null,null);results.push(!refused.ok&&sessionEpochRead()===null);Storage.prototype.setItem=original;}
          absent();const setup=JPWFXConsolidated.beginAccountSetup('CONTA-A');results.push(setup.ok&&!!sessionEpochRead());JPWFXConsolidated.cancelAccountSetup();
          absent();const importing=JPWFXConsolidated.beginImportReview();results.push(importing.ok&&!!sessionEpochRead());
          localStorage.setItem(key,'');const invalid=JPWFXConsolidated.beginRegistration(null,null);results.push(!invalid.ok&&sessionEpochRead()==='');localStorage.setItem(key,epoch);
          return results;
        }""")
        assert all(observed),observed;assert snap(page)==before
      run('explicit-cadastro-establishes-only-absent-epoch',registry_epoch)
      def drafts(page,ctx):
        page.evaluate("JPWNavigation.navigate('forex-operation')")
        field=page.locator('[data-p="0"][data-o="0"][data-f="id"]');field.evaluate("e=>{e.closest('details').open=true}");field.fill('NÃO SALVO')
        before=snap(page);page.evaluate("JPWForex.accountsUI.useContext('CONTA-B',__periodB)")
        assert page.locator('#ebLeaveStay').is_visible();page.locator('#ebLeaveStay').click()
        assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='CONTA-A'
        assert field.input_value()=='NÃO SALVO' and snap(page)==before
        page.locator('[data-eb-manage]').click();page.locator('#ebLeaveDiscard').click();settle(page)
        assert page.locator('#forexAccountsWorkspace').is_visible()
        page.locator('[data-fx-examine="CONTA-A"]').click()
        page.locator('#fxAccountFacts').evaluate("e=>e.closest('details').open=true");page.locator('#fxAccountFacts [name=reason]').fill('Rascunho de observação')
        page.locator('[data-fx-examine="CONTA-B"]').click();assert page.locator('#fxAccountsStay').is_visible();page.locator('#fxAccountsStay').click()
        assert page.evaluate('JPWForex.accountsUI.examination().accountId')=='CONTA-A'
        assert page.locator('#fxAccountFacts [name=reason]').input_value()=='Rascunho de observação'
      run('board-and-account-drafts',drafts)
      def archived(page,ctx):
        old=page.evaluate('JPWForex.state.operationalSelection()')
        result=page.evaluate("()=>JPWForex.state.archiveRegisteredAccount('CONTA-B',{reason:'Synthetic archive',expectedEpoch:jpWealthPersistenceEpoch()})")
        assert result['ok'];page.evaluate('JPWForex.accountsUI.render()')
        assert page.locator('[data-fx-reregister="CONTA-B"]').count()==1
        result=page.evaluate("async()=>{const p=JPWFXConsolidated.beginRegistration(null,'CONTA-B');if(!p.ok)throw Error(p.error);return await JPWFXConsolidated.saveRegistration(p.token,{...p.draft,name:p.draft.name,profileKey:p.draft.profileKey},{confirmHistorical:true});}")
        assert result['ok'],result;page.evaluate('JPWForex.accountsUI.render()')
        assert page.locator('[data-fx-reregister="CONTA-B"]').count()==0
        assert page.locator('[data-fx-examine="CONTA-B"]').count()==1
        assert page.evaluate("!!S.forex.accountContexts.archivedAccounts['CONTA-B']")
        now=page.evaluate('JPWForex.state.operationalSelection()')
        assert now['accountId']==old['accountId'] and now['periodId']==old['periodId']
      run('archive-reregister-visible-once-preserves-context',archived)
      def views(page,ctx):
        for layout in ['sidebar','topbar','glass','submenu']:
          # Public setting followed by its controller, same existing nodes.
          page.evaluate("l=>{localStorage.setItem('jpw_nav_layout',l);mountNavigationLayout(l);}",layout)
          assert page.evaluate("JPWNavigation.children('forex').slice(0,3).map(x=>x.label)")==['Dashboard','Contas e Período','Execution Board']
          for alias in ['contas','forex-account','forex-management-accounts']:
            assert page.evaluate('(a)=>JPWNavigation.navigate(a)',alias)
            assert page.locator('#forexAccountsWorkspace').is_visible()
          for theme in ['light','dark']:
            page.evaluate("t=>{S.theme=t;document.documentElement.dataset.theme=t;document.body.dataset.theme=t;render();}",theme)
            for width in [1440,768,390,320]:
              page.set_viewport_size({'width':width,'height':1000 if width>900 else 844});page.locator('[data-fx-examine="CONTA-B"]').click();settle(page)
              assert page.locator('#fxAccountsUse').is_enabled()
              assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),(layout,theme,width,'global overflow')
              for selector in ['#fxAccountsCreate','#fxAccountsUse']:
                style=page.locator(selector).evaluate('e=>{const c=getComputedStyle(e),r=e.getBoundingClientRect();return {bg:c.backgroundColor,color:c.color,w:r.width,h:r.height};}')
                assert style['bg'] not in ['transparent','rgba(0, 0, 0, 0)'] and style['bg']!=style['color'],(selector,style)
                assert style['w']>=44 and style['h']>=44,(selector,style)
              if layout=='sidebar' and width in [1440,390]:
                page.locator('#forexAccountsWorkspace .jp-table-scroll').evaluate_all('nodes=>nodes.forEach(e=>e.scrollLeft=0)');page.screenshot(path=str(args.out/f'accounts-{theme}-{width}.png'),full_page=True)
      run('layouts-responsive-themes',views)
      def wizard(page,ctx):
        before=snap(page);page.locator('#fxAccountsCreate').click()
        page.locator('#fxcwNext').click();page.locator('#fxcr-name').fill('Conta CFD sintética — identificação extensa para avaliação de formulário')
        page.locator('#fxcr-type').select_option('PRÓPRIA');page.locator('#fxcr-login').fill('000012345678901234567890123456789')
        page.locator('#fxcwNext').click();page.locator('#fxcr-platform').select_option('MetaTrader 5')
        page.locator('#fxcr-broker').fill('Corretora exclusivamente sintética');page.locator('#fxcr-currency').fill('USD');page.locator('#fxcr-accountEnvironment').select_option('demo')
        page.locator('#fxcwNext').click();page.locator('#fxcr-profileKey').select_option('longevity');page.locator('#fxcwNext').click()
        for theme in ['light','dark']:
          page.evaluate("t=>{S.theme=t;document.documentElement.dataset.theme=t;document.body.dataset.theme=t;}",theme)
          for width in [1440,390,320]:
            page.set_viewport_size({'width':width,'height':900 if width>900 else 844})
            dialog=page.locator('#fxcRegistrationDialog');r=dialog.bounding_box()
            assert r and r['x']>=0 and r['x']+r['width']<=width+1
            assert dialog.evaluate('e=>e.scrollWidth<=e.clientWidth+2')
            for selector in ['#fxcwClose','#fxcwBack','#fxcRegistrationSave']:
              b=page.locator(selector);b.scroll_into_view_if_needed();box=b.bounding_box();assert b.is_visible() and box['height']>=44,(theme,width,selector,box,b.evaluate('e=>({min:getComputedStyle(e).minHeight,zoom:getComputedStyle(e).zoom})'))
            page.locator('#fxcRegistrationSave').focus()
            for _ in range(8):
              page.keyboard.press('Tab');assert dialog.evaluate('e=>e.contains(document.activeElement)')
            page.locator('#fxcwWork').evaluate('e=>e.scrollTop=0');page.locator('#fxcwClose').focus();page.screenshot(path=str(args.out/f'wizard-review-{theme}-{width}.png'))
        # Discard protection is user-visible; no registration occurs in this case.
        page.keyboard.press('Escape');assert page.locator('#fxcwKeep').is_visible();page.locator('#fxcwKeep').click()
        assert page.locator('#fxcr-login').input_value()=='000012345678901234567890123456789'
        page.keyboard.press('Escape');page.locator('#fxcwDiscardConfirm').click()
        page.evaluate("()=>{S.theme='light';}")
        # Theme preview is RAM-only, compare data with the original theme restored.
        expected=page.evaluate('x=>JSON.parse(x)',before)
        current=page.evaluate('({state:S,raw:localStorage.getItem(LSKEY)})');current['state']['theme']=expected['state']['theme']
        assert current==expected
      run('wizard-keyboard-responsive-long-identifiers',wizard)
      if args.baseline:
        def backwards(page,ctx):
          payload=page.evaluate("async()=>JSON.parse(await dgBuildBackupBlob(1,'synthetic.json',new Date().toISOString()).text())")
          accounts=payload['state']['accounts'];periods=payload['state']['forex']['accountContexts'];before=snap(page)
          server_old=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(args.baseline)));threading.Thread(target=server_old.serve_forever,daemon=True).start()
          oldctx=browser.new_context(service_workers='block');install_bootstrap(oldctx);oldctx.add_init_script('window.__onbShown=true');old=oldctx.new_page();old.on('dialog',lambda d:d.accept())
          try:
            old.goto(f'http://127.0.0.1:{server_old.server_port}/index.html');wait_bootstrap(old)
            old.evaluate("async data=>await importFullBackupFile(new File([JSON.stringify(data)],'synthetic-rollback.json',{type:'application/json'}))",payload)
            old.wait_for_function("S.accounts?.some(a=>a.forexAccountId==='CONTA-A')&&!S.workspaceRecovery?.pending")
            r=old.evaluate("()=>{S.accounts[0].nome='Conta A - edição sintética na versão anterior';const ok=save();return {ok,accounts:JSON.parse(localStorage.getItem(LSKEY)).accounts,periods:JSON.parse(localStorage.getItem(LSKEY)).forex.accountContexts};}")
            assert r['ok'] is True
            for a,b in zip(accounts,r['accounts']):
              for key in ['forexAccountId','accountEnvironment','riskProfileAssignment']:assert a[key]==b[key],key
            assert r['periods']==periods
            # Roundtrip the old writer's preserved document into the new validator.
            oldraw=old.evaluate('JSON.parse(localStorage.getItem(LSKEY))')
            normalized=page.evaluate('data=>normalizeImportedState(data)',oldraw)
            assert normalized['forex']['accountContexts']==periods
            invalid=json.loads(json.dumps(payload));invalid['state']['accounts'][0]['riskProfileAssignment']['profileKey']='invalid'
            assert page.evaluate('data=>{try{normalizeImportedState(data);return false}catch(e){return true}}',invalid)
            assert snap(page)==before
          finally:oldctx.close();server_old.shutdown();server_old.server_close()
        run('previous-version-read-write-roundtrip-and-invalid-import',backwards)
      browser.close()
    server.shutdown();server.server_close();report['status']='PASS' if all(x['status']=='PASS' for x in report['cases']) else 'PRODUCT_FAIL';(args.out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if report['status']=='PASS' else 1)
if __name__=='__main__':main()

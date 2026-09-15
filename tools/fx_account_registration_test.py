#!/usr/bin/env python3
"""Current registration is a prerequisite, not authorization to import.

Reuses the actual application's writer and existing synthetic browser bootstrap.
Exit status reflects assertions; no real account, file, economic API or profile.
--root permits the two original prepareImport oracles on an immutable baseline.
"""
import argparse, hashlib, json, sys, threading, traceback
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from fx_consolidated_storage_test import SEED, Quiet, finalize
from notes_launcher_test import launch_options
ROOT=Path(__file__).resolve().parents[1]
SOURCES=['src/js/00-core/04-persistence.js','src/js/10-domain/17-fx-consolidated-model.js','src/js/40-app/24-fx-consolidated-import.js',
         'src/js/20-ui/28-fx-consolidated.js','src/js/20-ui/08-input-bindings.js','src/styles/app.css']
SETUP=r"""() => {
  window.__begin=(report=__report(),id='fx_A')=>__fcs.api.beginRegistration(report,id);
  window.__saveReg=(p,extra={},options={})=>__fcs.api.saveRegistration(p.token,{...p.draft,name:p.draft.name||'Nova sintética',...extra},options);
}"""
CASES={
'required-missing-current-login':r"""async()=>{
  S.accounts[0].platformLogin='';const before=__snap(),result=__prepare();
  __assert(!result.ok,'Missing current login allowed preparation');__assert(__same(before,__snap()),'Preparation wrote');return result;
}""",
'required-historical-only':r"""async()=>{
  await __import();S.accounts=S.accounts.filter(a=>a.forexAccountId!=='fx_A');const before=__snap(),result=__prepare();
  __assert(!result.ok,'Archived-only account allowed preparation');__assert(__same(before,__snap()),'Preparation wrote');return result;
}""",
'valid-read-and-confirm':r"""async()=>{
 const before=__snap(),status=__fcs.api.inspectRegistration(__report(),'fx_A'),p=__prepare();
 __assert(status.status==='ready'&&p.ok&&__same(before,__snap()),'Valid preview not pure');
 const r=await __fcs.api.confirmImport(p,{confirmIdentity:true});__assert(r.ok&&S.fxConsolidated.receipts.length===1,'Valid import failed');return r;
}""",
'missing-format-identity-cannot-be-replaced-by-form':r"""async()=>{
 const before=__snap();let results=[];
 for(const report of [{...__report(),format:'unknown'},{...__report(),identity:{login:null}},null]){
  const r=__fcs.api.inspectRegistration(report,null),f=__begin(report);results.push(r);
  __assert(r.status==='invalid'&&!r.ok,'Invalid document admitted');
  if(report!==null)__assert(!f.ok,'Form bypassed invalid document');
 }
 __assert(__same(before,__snap()),'Invalid read wrote');return results;
}""",
'other-current-and-ambiguous':r"""async()=>{
 const before=__snap(),r=__fcs.api.inspectRegistration(__report(),'fx_B');
 __assert(r.status==='other'&&r.matches[0].id==='fx_A'&&!__prepare('10001','fx_B').ok,'Other account selected silently');
 __assert(__same(before,__snap()),'Selection changed state');
 S.accounts.push({...S.accounts[0],forexAccountId:'duplicate'});
 __assert(__fcs.api.inspectRegistration(__report(),'fx_A').status==='ambiguous','Ambiguity chose first');return r;
}""",
'platform-and-current-optional-identifiers':r"""async()=>{
 let outcomes=[];
 for(const field of ['platform','broker','platformCurrency','platformServer']){
  const before={...S.accounts[0]};S.accounts[0][field]=({platform:'MT4',broker:'Other Broker',platformCurrency:'EUR',platformServer:'OTHER'})[field];
  const report=__report();report.identity.server='SYNTHETIC';
  const r=__fcs.api.inspectRegistration(report,'fx_A');outcomes.push(r);
  __assert(!r.ok&&r.status==='mismatch','Mismatch passed '+field);S.accounts[0]=before;
 }
 __assert(__fcs.writes===0,'Mismatch wrote');return outcomes;
}""",
'incomplete-with-historical-display-fallback':r"""async()=>{
 await __import();S.accounts[0].platformLogin='';const before=__snap();
 __assert(__fcs.api.accounts()[0].login==='10001','Display history not retained');
 const r=__fcs.api.inspectRegistration(__report(),'fx_A'),p=__begin();
 __assert(r.status==='incomplete'&&p.mode==='complete'&&__same(before,__snap()),'Historical fallback authorized import');
 const saved=await __saveReg(p);__assert(saved.ok&&S.accounts[0].platformLogin==='10001','Completion failed');
 __assert(S.fxConsolidated.receipts.length===1,'Completion imported');return {r,saved};
}""",
 'completion-preserves-optional-identifiers':r"""async()=>{
 S.accounts[0].platformServer='Synthetic-Demo';S.accounts[0].platformCurrency='USD';S.accounts[0].platform='';
 const p=__begin(),before=__snap();
 const r=await __saveReg(p,{broker:'',currency:'',server:''});
 __assert(!r.ok&&__same(before,__snap()),'Completion erased known optional identifiers');return r;
}""",
'create-save-is-not-import':r"""async()=>{
 const before=__snap(),p=__begin(__report('40004'),null);__assert(p.ok&&p.mode==='create','New draft unavailable');
 __assert(p.draft.name===''&&!('satu' in p.draft)&&__same(before,__snap()),'Draft copied financial identity or wrote');
 const r=await __saveReg(p);__assert(r.ok&&S.accounts.length===4&&S.fxConsolidated.receipts.length===0,'Save imported or failed');
 const a=S.accounts[3];__assert(a.sini===0&&a.satu===0&&S.forex.activeAccountId==='fx_B'&&!S.forex.accounts[a.forexAccountId],'Financial observations restored');
 __assert(__same(before.manual,S.operationHistory),'Manual history changed');
 const imported=await __import('40004',r.accountId);__assert(imported.ok&&S.fxConsolidated.receipts.length===1,'Separate import failed');return {r,imported};
}""",
'cancel-and-duplicate-create':r"""async()=>{
 const before=__snap(),p=__begin(__report('40004'),null);__fcs.api.cancelRegistration();
 const r=await __saveReg(p);__assert(!r.ok&&__same(before,__snap()),'Cancelled draft saved');
 const q=__begin(null,null),duplicate=await __saveReg(q,{login:'10001',platform:'MT5',broker:'Synthetic Broker',currency:'USD'});
 __assert(!duplicate.ok&&__same(before,__snap()),'Duplicate created');return {r,duplicate};
}""",
'historical-explicit-reregistration-dedupe':r"""async()=>{
 await __import();const history=structuredClone(S.fxConsolidated),manual=structuredClone(S.operationHistory);
 S.accounts=S.accounts.filter(a=>a.forexAccountId!=='fx_A');save();
 const p=__begin();__assert(p.mode==='reregister','Historical draft not explicit');
 const refusal=await __saveReg(p);__assert(!refusal.ok&&S.accounts.length===2,'Historical confirmation bypass');
 const r=await __saveReg(p,{}, {confirmHistorical:true});__assert(r.ok&&r.accountId==='fx_A','Historical ID not reused');
 const a=S.accounts.find(a=>a.forexAccountId==='fx_A');__assert(a.satu===0&&a.sini===0&&S.forex.activeAccountId==='fx_B','Historical balances activated');
 __assert(__same(history,S.fxConsolidated)&&__same(manual,S.operationHistory),'Registration mutated histories');
 const d=await __import();__assert(d.duplicate&&S.fxConsolidated.receipts.length===1,'Reregistration lost deduplication');return {r,d};
}""",
'mismatched-selection-never-overwritten':r"""async()=>{
 const before=__snap(),p=__begin(__report('40004'),'fx_A');__assert(p.mode==='create','Mismatch overwrites selected');
 const r=await __saveReg(p);__assert(r.ok&&__same(before.accounts.slice(0,3),S.accounts.slice(0,3)),'Selected registry overwritten');return r;
}""",
'changed-registration-before-import-confirmation':r"""async()=>{
 const p=__prepare();S.accounts[0].platformLogin='';const before=__snap();
 const r=await __fcs.api.confirmImport(p,{confirmIdentity:true});__assert(!r.ok&&__same(before,__snap()),'Confirmation skipped registry');return r;
}""",
'new-duplicate-before-import-confirmation':r"""async()=>{
 const p=__prepare();S.accounts.push({...S.accounts[0],forexAccountId:'newdup'});const before=__snap();
 const r=await __fcs.api.confirmImport(p,{confirmIdentity:true});__assert(!r.ok&&__same(before,__snap()),'Confirmation skipped ambiguity');return r;
}""",
'queued-registration-cancel-and-concurrent-catalog':r"""async()=>{
 const p=__begin(__report('40004'),null),lock=sessionAcquireWriteLock;let execute;
 sessionAcquireWriteLock=fn=>new Promise(resolve=>execute=()=>resolve(fn()));
 const promise=__saveReg(p);__fcs.api.cancelRegistration();execute();const r=await promise;
 sessionAcquireWriteLock=lock;__assert(!r.ok&&__fcs.writes===0,'Queued cancelled write executed');
 const q=__begin(__report('40004'),null);S.accounts[1].nome='Outra versão';const before=__snap(),other=await __saveReg(q);
 __assert(!other.ok&&__same(before,__snap()),'Concurrent registry silently accepted');return {r,other};
}""",
'quota-refusal-draft-retry-one-registration':r"""async()=>{
 const p=__begin(__report('40004'),null),before=__snap();__fcs.mode='quota';const r=await __saveReg(p),after=__snap();
 __assert(!r.ok&&r.persistido===false&&!after.unknown,'Quota outcome incorrect');
 for(const key of ['fx','manual','accounts','forex','log','raw'])__assert(__same(before[key],after[key]),'Refusal changed '+key);
 __fcs.mode='normal';const retry=await __saveReg(p);__assert(retry.ok&&S.accounts.length===4&&!S.fxConsolidated.receipts.length,'Retry lost draft or imported');return {r,retry};
}""",
'no-op-write-no-success':r"""async()=>{
 const p=__begin(__report('40004'),null),before=__snap();__fcs.mode='noop';const r=await __saveReg(p),after=__snap();
 __assert(!r.ok&&r.persistido===false,'No-op reported success');
 for(const key of ['fx','manual','accounts','forex','log','raw'])__assert(__same(before[key],after[key]),'No-op changed '+key);return r;
}""",
'unknown-after-write-no-blind-retry':r"""async()=>{
 const p=__begin(__report('40004'),null);save=()=>{__fcs.realSave();throw Error('Synthetic post-write interruption');};
 const r=await __saveReg(p),after=__snap(),repeat=await __saveReg(p);
 __assert(r.persistido===null&&after.unknown&&repeat.persistido===null&&__fcs.writes===after.writes,'UNKNOWN allowed retry');
 __assert(JSON.parse(after.raw).accounts.length===4&&S.accounts.length===4&&!S.fxConsolidated.receipts.length,'Unknown discarded possible committed account');return {r,repeat};
}""",
'unknown-readback-no-retry':r"""async()=>{
 const p=__begin(__report('40004'),null);__fcs.mode='readback';const r=await __saveReg(p),writes=__fcs.writes;
 __assert(r.persistido===null&&jpWealthPersistenceOutcomeIsUnknown(),'Readback not UNKNOWN');
 __fcs.readFault=false;const retry=await __saveReg(p);__assert(!retry.ok&&__fcs.writes===writes,'Readback retry wrote');return {r,retry};
}""",
'epoch-recovery-and-foreign-domain-preservation':r"""async()=>{
 const p=__begin(__report('40004'),null);sessionEpochRotate();const before=__snap(),r=await __saveReg(p);
 __assert(!r.ok&&__same(before,__snap()),'Old epoch wrote');
 const q=__begin(__report('40004'),null);save=()=>{S.personalFinance.syntheticKeep='keep';return false;};
 const refused=await __saveReg(q);__assert(!refused.ok&&S.personalFinance.syntheticKeep==='keep','Rollback erased other flow');save=__fcs.realSave;return {r,refused};
}""",
 'metadata-minimal-catalog-retained':r"""async()=>{
 const report=__report();report.identity.server='Synthetic-Demo';await __fcs.api.saveDefaultAccount('fx_A');
 S.accounts[0].platform='';const p=__begin(report,'fx_A'),r=await __saveReg(p);__assert(r.ok,'Completion failed');
 const before=__snap(),snapshot=fxConsolidatedLongitudinalSnapshot(JSON.parse(before.raw));
 __assert(snapshot.accounts.find(a=>a.id==='fx_A').server==='Synthetic-Demo','Minimal catalogue lost explicit server');
 __assert(__same(before,__snap()),'Snapshot wrote');return {server:snapshot.accounts[0].server};
}""",
 'metadata-minimal-divergence-not-combined':r"""async()=>{
 await __fcs.api.saveDefaultAccount('fx_A');S.accounts[0].platformLogin='different';S.accounts[0].platformServer='Server of different account';
 const before=structuredClone(S.fxConsolidated),snapshot=fxConsolidatedLongitudinalSnapshot(S);
 __assert(__same(snapshot.accounts[0],before.accounts[0]),'Incompatible registry created hybrid identity');return {preserved:true};
}""",
'metadata-minimal-manual-identity-reregistered':r"""async()=>{
 S.operationHistory.records.push({accountId:'manual_unknown'});S.fxConsolidated=fxConsolidatedLongitudinalSnapshot(S);save();
 const report=__report('40004'),p=__begin(report,'manual_unknown');__assert(p.mode==='reregister','Missing manual identity not offered');
 const r=await __saveReg(p,{}, {confirmHistorical:true});__assert(r.ok&&r.accountId==='manual_unknown','Manual identity was replaced');
 const snapshot=fxConsolidatedLongitudinalSnapshot(S),account=snapshot.accounts.find(a=>a.id==='manual_unknown');
 __assert(account.login==='40004'&&account.broker==='Synthetic Broker'&&account.currency==='USD','Confirmed missing manual identity lost');return account;
}""",
'metadata-imported-history-not-enriched':r"""async()=>{
 await __import();const before=structuredClone(S.fxConsolidated);S.accounts[0].platformServer='Current server only';
 const snapshot=fxConsolidatedLongitudinalSnapshot(S);
 __assert(__same(snapshot.accounts[0],before.accounts[0]),'Current metadata backfilled an imported historical report');return {preserved:true};
}""",
'backup-registration-roundtrip':r"""async()=>{
 const p=__begin(__report('40004'),null),r=await __saveReg(p);__assert(r.ok,'Registration refused');
 const document=JSON.parse(await dgBuildBackupBlob(1,'synthetic.json','2026-01-31T12:00:00Z').text());
 const restored=normalizeImportedState(document);__assert(__same(restored.accounts,S.accounts)&&__same(restored.fxConsolidated,S.fxConsolidated),'Backup lost registration');return {registered:r.accountId};
}"""
}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--case',default='');args=ap.parse_args()
    if args.out.exists():ap.error('Choose a new evidence path')
    root=args.root.resolve();hashes=lambda:{s:hashlib.sha256((root/s).read_bytes()).hexdigest() for s in SOURCES}
    evidence={'root':str(root),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sources_before':hashes(),'cases':[]}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
    def run(browser,name,source=None,callback=None):
        if args.case and args.case not in name:return
        record={'name':name,'pageerrors':[],'console_errors':[]};context=None
        try:
            context=browser.new_context(service_workers='block',viewport={'width':1440,'height':1000});install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
            page=context.new_page();page.on('pageerror',lambda err:record['pageerrors'].append(str(err)));page.on('console',lambda m:record['console_errors'].append(m.text) if m.type=='error' else None)
            page.goto(url);wait_bootstrap(page);record['seed']=page.evaluate(SEED);page.evaluate(SETUP)
            record['observations']=page.evaluate(source) if source else callback(page,context)
            assert_fixture_requests(context);assert not record['pageerrors'],record['pageerrors']
            expected=('JP Wealth: falha ao gravar o estado no armazenamento local.','[persistência] DESFECHO INDETERMINADO','JP Wealth: conflito de concorrência entre abas detectado no save().') if any(s in name for s in ['quota','unknown','cross-tab']) else ()
            assert not [s for s in record['console_errors'] if not s.startswith(expected)],record['console_errors']
            record['status']='PASS'
        except Exception as error:
            record.update(status='PRODUCT_FAIL' if isinstance(error,AssertionError) or 'PRODUCT_ASSERTION:' in str(error) else 'TEST_HARNESS_FAIL',error=str(error),trace=traceback.format_exc())
        finally:
            if context:context.close()
            evidence['cases'].append(record);print(name,record['status'],record.get('error','')[:240],flush=True)
    def ui(page,context):
        page.evaluate("S.accounts.forEach(a=>a.tipo='PRÓPRIA');navNavigate('forex-consolidated')");page.locator('#fxcAccount').select_option('');assert page.locator('#fxcAccount').input_value()=='';before=page.evaluate('__snap()')
        page.locator('#fxcOpenImport').click();page.locator('#fxcFile').set_input_files(str(root/'tools/fixtures/mt5-consolidated/classic-en.html'));page.locator('#fxcAnalyze').click();page.locator('#fxcRegister').wait_for()
        assert page.evaluate('__snap()')==before
        page.locator('#fxcRegister').click();page.locator('#fxcr-name').fill('Cadastro pelo documento');page.keyboard.press('Escape')
        assert not page.locator('#fxcRegistrationDialog').is_visible();assert page.locator('#fxcRegister').evaluate('el=>document.activeElement===el')
        assert page.evaluate('__snap()')==before
        page.locator('#fxcRegister').click();page.locator('#fxcr-name').fill('Cadastro pelo documento')
        for width,theme in [(390,'light'),(390,'dark'),(1440,'dark'),(1440,'light')]:
            page.set_viewport_size({'width':width,'height':844});page.evaluate('(t)=>document.documentElement.dataset.theme=t',theme)
            assert page.locator('#fxcRegistrationDialog').evaluate('el=>el.scrollWidth<=el.clientWidth+2&&el.getBoundingClientRect().left>=0')
        page.locator('#fxcRegistrationSave').click();page.locator('#fxcConfirmImport').wait_for()
        saved=page.evaluate('__snap()');assert len(saved['accounts'])==4 and not saved['fx']['receipts'] and saved['forex']['activeAccountId']=='fx_B'
        assert not page.locator('#fxcConfirmIdentity').is_checked()
        page.locator('#fxcConfirmIdentity').check();page.locator('#fxcConfirmImport').click();page.wait_for_function('S.fxConsolidated.receipts.length===1')
        registered=page.evaluate('S.accounts[3].forexAccountId');page.reload();wait_bootstrap(page)
        assert page.evaluate('S.accounts.length===4&&S.fxConsolidated.receipts.length===1&&S.forex.activeAccountId==="fx_B"')
        return {'registered':registered,'savedBeforeImport':True,'reloaded':True,'cancelFocus':True,'themesAndMobile':True}
    def ui_accounts(page,context):
        page.evaluate("navNavigate('forex-account');renderContas()");before=page.evaluate('__snap()')
        page.locator('#addAccountBtn').click();page.locator('#fxcr-name').fill('Ficha cancelada')
        page.keyboard.press('Tab');assert page.locator('#fxcr-type').evaluate('el=>el===document.activeElement')
        page.locator('#fxcRegistrationCancel').click();assert page.evaluate('__snap()')==before
        assert page.locator('#addAccountBtn').evaluate('el=>el===document.activeElement')
        return {'cancelNoWrite':True,'keyboard':True}
    def ui_quota(page,context):
        page.evaluate("navNavigate('forex-account');renderContas()");page.locator('#addAccountBtn').click()
        page.locator('#fxcr-name').fill('Rascunho preservado');page.locator('#fxcr-platform').select_option('MetaTrader 5');page.locator('#fxcr-login').fill('40004');page.evaluate("__fcs.mode='quota'")
        before=page.evaluate('__snap()');page.locator('#fxcRegistrationSave').click();page.wait_for_function("document.getElementById('fxcRegistrationStatus').textContent.includes('recusada')")
        assert page.locator('#fxcr-name').input_value()=='Rascunho preservado' and page.evaluate('S.accounts.length===3')
        assert page.evaluate('__snap().raw')==before['raw']
        page.evaluate("__fcs.mode='normal'");page.locator('#fxcRegistrationSave').click();page.wait_for_function('S.accounts.length===4')
        assert page.evaluate('S.fxConsolidated.receipts.length===0');return {'draftPreserved':True,'retrySingle':True}
    def cross_tab(page,context):
        page.evaluate("window.__draft=__begin(__report('40004'),null)")
        other=context.new_page();other.goto(url);wait_bootstrap(other)
        raw=other.evaluate("()=>{S.accounts[1].nome='Alteração outra aba';if(save()!==true)throw Error('Fixture save failed');return localStorage.getItem(LSKEY)}")
        result=page.evaluate('__saveReg(__draft)');assert not result['ok'];assert page.evaluate('localStorage.getItem(LSKEY)')==raw
        return result
    def no_current_accounts(page,context):
        page.evaluate("S.accounts=[];navNavigate('forex-consolidated')")
        before=page.evaluate('__snap()');assert page.locator('#fxcAccount').input_value()==''
        page.locator('#fxcOpenImport').click();page.locator('#fxcFile').set_input_files(str(root/'tools/fixtures/mt5-consolidated/classic-en.html'))
        page.locator('#fxcAnalyze').click();page.locator('#fxcRegister').wait_for();page.locator('#fxcRegister').click()
        assert page.locator('#fxcr-login').input_value()=='900001'
        page.locator('#fxcRegistrationCancel').click();assert page.evaluate('__snap()')==before
        return {'identifiedWithoutAccount':True,'noWrite':True}
    def metadata_finalize(page,context):
        account=page.evaluate("""async()=>{const report=__report('40004');report.identity.server='Synthetic-Demo';const draft=__begin(report,null);const result=await __saveReg(draft);__assert(result.ok,'Registration failed');markSessionCheckpoint();return result.accountId;}""")
        finalize(page);page.reload();wait_bootstrap(page)
        item=page.evaluate('(id)=>S.fxConsolidated.accounts.find(a=>a.id===id)',account)
        assert item['server']=='Synthetic-Demo' and item['currency']=='USD',item
        assert page.evaluate('S.accounts.length===0&&S.fxConsolidated.receipts.length===0')
        return {'catalog':item,'currentAccountsCleared':True,'noImport':True}
    def remote_finalize(page,context):
        page.evaluate("async()=>{await __import();markSessionCheckpoint();navNavigate('forex-account');renderContas();}")
        page.locator('#addAccountBtn').click();page.locator('#fxcr-name').fill('Rascunho não confirmado')
        other=context.new_page();other.goto(url);wait_bootstrap(other);other.evaluate('()=>{window.__onbShown=true;closeModal();markSessionCheckpoint();}')
        finalize(other)
        page.wait_for_function("S.accounts.length===0&&!document.getElementById('fxcRegistrationDialog').open")
        assert page.evaluate('S.fxConsolidated.receipts.length===1&&S.operationHistory.records.length===1')
        page.reload();wait_bootstrap(page)
        assert page.evaluate('S.accounts.length===0&&S.fxConsolidated.receipts.length===1')
        return {'draftClosed':True,'historyRetained':True,'registrationRequiredAfterReload':True}
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(**launch_options())
            for name,source in CASES.items():run(browser,name,source=source)
            run(browser,'ui-identification-create-import-reload',callback=ui)
            run(browser,'ui-accounts-draft-keyboard-cancel',callback=ui_accounts)
            run(browser,'ui-quota-draft-retry',callback=ui_quota)
            run(browser,'cross-tab-registry-change',callback=cross_tab)
            run(browser,'remote-finalize-closes-registration',callback=remote_finalize)
            run(browser,'ui-no-current-accounts-identification',callback=no_current_accounts)
            run(browser,'metadata-new-registration-finalize-reload',callback=metadata_finalize)
            browser.close()
    finally:
        server.shutdown();server.server_close();evidence['sources_after']=hashes();evidence['unchanged']=evidence['sources_before']==evidence['sources_after']
        evidence['counts']={'total':len(evidence['cases']),'passed':sum(r['status']=='PASS' for r in evidence['cases'])}
        evidence['result']='PASS' if evidence['cases'] and all(r['status']=='PASS' for r in evidence['cases']) and evidence['unchanged'] else 'PRODUCT_FAIL'
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2));print(evidence['result'],evidence['counts'])
    return 0 if evidence['result']=='PASS' else 1
if __name__=='__main__':sys.exit(main())

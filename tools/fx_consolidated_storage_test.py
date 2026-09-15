#!/usr/bin/env python3
"""Consolidado: contratos reais de escrita/backup/lifecycle com dados sintéticos.

Chromium isolado, aplicativo servido por loopback e bootstrap econômico existente
interceptado. Nenhum perfil do operador, arquivo real ou API econômica é usado.
"""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    'src/js/10-domain/17-fx-consolidated-model.js',
    'src/js/40-app/24-fx-consolidated-import.js',
    'src/js/00-core/03-default-state.js', 'src/js/00-core/04-persistence.js',
    'src/js/30-accounting/01-daily-ledger.js', 'src/js/40-app/07-finalize-session.js',
)

SEED = r"""() => {
  window.__onbShown=true;closeModal();window.__alerts=[];
  window.alert=message=>__alerts.push(String(message));window.confirm=()=>true;
  const instruments=structuredClone(S.instruments);
  S=structuredClone(DEFAULTS);migrate();S.instruments=instruments;S.onboarding.done=true;
  S.accounts=[
    {forexAccountId:'fx_A',nome:'Mestre sintética',tipo:'MESTRE',broker:'Synthetic Broker',platform:'MetaTrader 5',platformLogin:'10001',investorPassword:'',sini:10000,satu:10100,perfil:'Base',perfilLocked:true},
    {forexAccountId:'fx_B',nome:'Outra sintética',tipo:'PRÓPRIA',broker:'Synthetic Broker',platform:'MetaTrader 5',platformLogin:'20002',investorPassword:'',sini:5000,satu:5000,perfil:'Base',perfilLocked:true},
    {nome:'Sem ID sintética',tipo:'PRÓPRIA',broker:'Synthetic Broker',platform:'MetaTrader 5',platformLogin:'30003',investorPassword:'',sini:2000,satu:2000,perfil:'Base',perfilLocked:true}
  ];
  S.forex.activeAccountId='fx_B';
  S.forex.accounts={fx_A:{currency:'USD',periodId:'period_A',si:10000,equity:10100},
    fx_B:{currency:'EUR',periodId:'period_B',si:5000,equity:5000}};
  S.operationHistory={schemaVersion:1,records:[{schemaVersion:1,operationId:'manual_A',
    accountId:'fx_A',periodId:'period_A',currency:'USD',instrument:'EURUSD',direction:'BUY',
    openedAt:'2026-01-01T10:00:00Z',closedAt:'2026-01-02T10:00:00Z',
    netResult:100,referenceBalance:10000,ordersSnapshot:[],custom:{preserve:true}}]};
  S.fxConsolidated=JPWFXConsolidated.emptyState();
  S.dataGovernance.changeLog=[];
  if(save()!==true)throw Error('Synthetic seed refused');
  sessionEpochCurrent();markSessionCheckpoint();
  const nativeGet=Storage.prototype.getItem,nativeSet=Storage.prototype.setItem;
  window.__fcs={api:JPWFXConsolidated,nativeGet,nativeSet,realSave:save,writes:0,mode:'normal',readFault:false};
  Storage.prototype.setItem=function(key,value){
    if(this===localStorage&&key===LSKEY){
      __fcs.writes++;
      if(__fcs.mode==='quota')throw new DOMException('Synthetic quota','QuotaExceededError');
      if(__fcs.mode==='noop')return;
      const result=nativeSet.call(this,key,value);
      if(__fcs.mode==='readback')__fcs.readFault=true;
      return result;
    }
    return nativeSet.call(this,key,value);
  };
  Storage.prototype.getItem=function(key){
    if(this===localStorage&&key===LSKEY&&__fcs.readFault)throw new DOMException('Synthetic readback denied','SecurityError');
    return nativeGet.call(this,key);
  };
  window.__snap=()=>({fx:structuredClone(S.fxConsolidated),manual:structuredClone(S.operationHistory),
    accounts:structuredClone(S.accounts),forex:structuredClone(S.forex),log:structuredClone(S.dataGovernance.changeLog),
    raw:__fcs.nativeGet.call(localStorage,LSKEY),unknown:jpWealthPersistenceOutcomeIsUnknown(),writes:__fcs.writes});
  window.__assert=(condition,message)=>{if(!condition)throw Error('PRODUCT_ASSERTION: '+message);};
  window.__same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
  window.__meta=(digit='a')=>({fileHash:digit.repeat(64),fileName:'synthetic-summary.pdf',importedAt:'2026-01-31T12:00:00Z'});
  window.__report=(login='10001')=>({format:'mt5-summary-pdf-v1',identity:{login,broker:'Synthetic Broker',currency:'USD',server:null},
    period:{from:'2026-01-01',to:'2026-01-31',declared:true},orders:[],deals:[],positions:[],
    summary:{balance:10100,netProfit:100},issues:[]});
  window.__prepare=(login='10001',id='fx_A',digit='a')=>__fcs.api.prepareImport(__report(login),id,__meta(digit));
  window.__import=async(login='10001',id='fx_A',digit='a')=>{
    const preview=__prepare(login,id,digit);__assert(preview.ok,JSON.stringify(preview));
    const result=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
    __assert(result.ok,JSON.stringify(result));return result;
  };
  return {build:JP_WEALTH_BUILD_ID,fixture:'synthetic-summary-and-manual',seedWritesExcluded:true};
}"""

CASES = {
    'reading-and-preview-are-pure': r"""async () => {
      const before=__snap();const accounts=__fcs.api.accounts();const preview=__prepare();
      __assert(preview.ok,JSON.stringify(preview));__fcs.api.cancelImport();
      __assert(__same(before,__snap()),'Read/preview/cancel mutated data or storage');
      __assert(accounts.length===3&&accounts[2].id==='live:2','Missing explicit transient identity');
      __assert(__same(DEFAULTS.fxConsolidated,__fcs.api.emptyState()),'Boot and model default disagree');
      return {accounts,counts:preview.counts,writes:__fcs.writes};
    }""",
    'confirmed-import-idempotence-source-separation': r"""async () => {
      const before=__snap(),first=await __import(),after=__snap(),second=await __import();
      __assert(first.persistido===true,'Import not confirmed');
      __assert(after.fx.receipts.length===1,'Receipt missing');
      __assert(__same(before.manual,after.manual)&&__same(before.forex,after.forex),'Import changed manual or operational Forex');
      __assert(second.persistido===false&&__same(after,__snap()),'Repeat changed data or saved again');
      __assert(!('investorPassword' in after.fx.accounts[0]),'Catalog retained a credential field');
      return {first,second,receipts:after.fx.receipts,writes:__fcs.writes};
    }""",
    'identity-mismatch-and-missing-account-number-blocked': r"""async () => {
      const before=__snap();const wrong=__prepare('20002','fx_A');
      __assert(!wrong.ok&&__same(before,__snap()),'Contradictory identity allowed');
      const report=__report();report.identity.login=null;
      const preview=__fcs.api.prepareImport(report,'fx_A',__meta());
      const confirmed=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      __assert(!preview.ok&&!confirmed.ok&&__same(before,__snap()),'Account number missing was authorized by a checkbox');
      return {wrong,preview,confirmed};
    }""",
    'incomplete-broker-server-requires-explicit-confirmation': r"""async () => {
      const before=__snap();
      const report=__report();report.identity.broker=null;report.identity.server=null;
      const preview=__fcs.api.prepareImport(report,'fx_A',__meta());
      __assert(preview.ok&&preview.requiresIdentityConfirmation,'Missing identity not explicit');
      const refused=await __fcs.api.confirmImport(preview);
      __assert(!refused.ok&&__same(before,__snap()),'Missing identity silently linked');
      const accepted=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      __assert(accepted.ok,'Explicit identity confirmation failed');
      return {refused,accepted};
    }""",
    'account-id-created-only-on-confirmation': r"""async () => {
      const before=__snap(),preview=__prepare('30003','live:2');
      __assert(preview.ok&&!('forexAccountId' in S.accounts[2]),'Preview assigned ID');
      const result=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      __assert(result.ok&&result.accountId===S.accounts[2].forexAccountId,'Explicit identity not committed');
      __assert(__same(before.forex,S.forex),'Identity created operational observation');
      const entry=S.fxConsolidated.accounts.find(a=>a.id===result.accountId);
      __assert(entry&&!('sini' in entry)&&!('satu' in entry)&&!('investorPassword' in entry),'Catalog copied financial account');
      return {result,catalog:entry};
    }""",
    'default-account-and-reset-preference': r"""async () => {
      const before=__snap(),saved=await __fcs.api.saveDefaultAccount('live:2');
      __assert(saved.ok&&S.fxConsolidated.defaultAccountId===S.accounts[2].forexAccountId,'Default ID not stable');
      __assert(__same(before.forex,S.forex)&&__same(before.manual,S.operationHistory),'Default selected operational account');
      const writes=__fcs.writes,repeat=await __fcs.api.saveDefaultAccount(saved.accountId);
      __assert(repeat.ok&&repeat.persistido===false&&__fcs.writes===writes,'Repeat default wrote');
      const reset=await __fcs.api.saveDefaultAccount(null);
      __assert(reset.ok&&S.fxConsolidated.defaultAccountId===null,'Automatic Mestre reset failed');
      return {saved,repeat,reset};
    }""",
    'stale-account-and-cancel-queued-confirmation': r"""async () => {
      const preview=__prepare();S.accounts.reverse();const before=__snap();
      const rejected=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      __assert(!rejected.ok&&__same(before,__snap()),'Changed account preview applied');
      S.accounts.reverse();
      const next=__prepare();
      const held=navigator.locks.request(JPW_STATE_WRITER_LOCK,()=>new Promise(resolve=>window.__releaseLock=resolve));
      while(!window.__releaseLock)await new Promise(resolve=>setTimeout(resolve,0));
      const confirmation=__fcs.api.confirmImport(next,{confirmIdentity:true});
      __fcs.api.cancelImport();window.__releaseLock();await held;
      const cancelled=await confirmation;
      __assert(!cancelled.ok&&__fcs.writes===0,'Cancelled queued import wrote');
      return {rejected,cancelled};
    }""",
    'public-preview-does-not-authorize-replacement': r"""async () => {
      const preview=__prepare();preview.report.summary.netProfit=999999;
      preview.report.originalBytes='ORIGINAL_MUST_NOT_PERSIST';
      const result=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      __assert(result.ok,'Stored preparation was not confirmed');
      __assert(!__snap().raw.includes('999999')&&!__snap().raw.includes('ORIGINAL_MUST_NOT_PERSIST'),'Public preview replaced stored preparation');
      const writes=__fcs.writes,forged=await __fcs.api.confirmImport({...preview,token:'forged'});
      __assert(!forged.ok&&__fcs.writes===writes,'Forged preview wrote');
      return {result,forged};
    }""",
    'quota-refusal-rollback-and-explicit-retry': r"""async () => {
      const preview=__prepare('30003','live:2'),before=__snap();__fcs.mode='quota';
      const refused=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      const after=__snap();
      for(const key of ['fx','manual','accounts','forex','log','raw'])__assert(__same(before[key],after[key]),'Refusal changed '+key);
      __assert(refused.persistido===false&&!after.unknown,'Quota incorrectly UNKNOWN');
      __fcs.mode='normal';const retried=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      __assert(retried.ok&&S.fxConsolidated.receipts.length===1,'Retry failed or duplicated');
      return {refused,retried};
    }""",
    'no-op-write-is-not-success': r"""async () => {
      const preview=__prepare(),before=__snap();__fcs.mode='noop';
      const result=await __fcs.api.confirmImport(preview,{confirmIdentity:true}),after=__snap();
      __assert(!result.ok&&result.persistido===false&&!after.unknown,'Silent no-op announced success');
      for(const key of ['fx','accounts','log','raw'])__assert(__same(before[key],after[key]),'No-op changed '+key);
      return {result,writes:after.writes};
    }""",
    'rollback-keeps-unrelated-domain-change': r"""async () => {
      const preview=__prepare(),before=__snap();
      save=()=>{S.personalFinance.syntheticConcurrent='keep';return false;};
      const result=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      __assert(!result.ok&&result.persistido===false,'Refusal not propagated');
      __assert(S.personalFinance.syntheticConcurrent==='keep','Rollback replaced all S');
      __assert(__same(before.fx,S.fxConsolidated)&&__same(before.log,S.dataGovernance.changeLog),'Own rollback failed');
      save=__fcs.realSave;return {result,unrelated:S.personalFinance.syntheticConcurrent};
    }""",
    'unknown-after-write-blocks-retry': r"""async () => {
      const preview=__prepare('30003','live:2');
      save=()=>{__fcs.realSave();throw Error('Synthetic after committed write');};
      const result=await __fcs.api.confirmImport(preview,{confirmIdentity:true}),after=__snap();
      __assert(result.persistido===null&&after.unknown,'Post-write exception not UNKNOWN');
      __assert(after.fx.receipts.length===1&&JSON.parse(after.raw).fxConsolidated.receipts.length===1,'UNKNOWN rolled back possible committed data');
      const repeat=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      const preference=await __fcs.api.saveDefaultAccount('fx_A');
      __assert(repeat.persistido===null&&preference.persistido===null&&__fcs.writes===after.writes,'UNKNOWN allowed retry');
      return {result,repeat,preference,writes:after.writes};
    }""",
    'unknown-readback-keeps-candidate': r"""async () => {
      const preview=__prepare();__fcs.mode='readback';
      const result=await __fcs.api.confirmImport(preview,{confirmIdentity:true}),after=__snap();
      __assert(result.persistido===null&&after.unknown,'Readback failure not UNKNOWN');
      __assert(after.fx.receipts.length===1&&JSON.parse(after.raw).fxConsolidated.receipts.length===1,'Readback failure lost candidate');
      __fcs.readFault=false;return {result,writes:after.writes};
    }""",
    'epoch-change-refuses-old-preview': r"""async () => {
      const preview=__prepare(),before=__snap();sessionEpochRotate();
      const result=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      __assert(!result.ok&&__same(before,__snap()),'Old epoch import changed base');return result;
    }""",
    'unavailable-epoch-refuses-without-writing': r"""async () => {
      const preview=__prepare(),before=__snap(),normal=Storage.prototype.getItem;
      Storage.prototype.getItem=function(key){
        if(this===localStorage&&key===BASE_EPOCH_STORAGE_KEY)throw new DOMException('Synthetic epoch read denied','SecurityError');
        return normal.call(this,key);
      };
      const confirmation=await __fcs.api.confirmImport(preview,{confirmIdentity:true});
      const prepared=__prepare(),preference=await __fcs.api.saveDefaultAccount('fx_A');
      __assert(!confirmation.ok&&!prepared.ok&&!preference.ok&&__same(before,__snap()),'Unavailable generation allowed a write');
      Storage.prototype.getItem=normal;
      return {confirmation,prepared,preference};
    }""",
    'backup-roundtrip-unknown-fields-and-future': r"""async () => {
      await __import();S.fxConsolidated.syntheticExtension={keep:['opaque']};save();
      const exported=JSON.parse(await dgBuildBackupBlob(1,'synthetic.json','2026-01-31T12:00:00Z').text());
      const before=__snap(),restored=normalizeImportedState(exported);
      __assert(__same(restored.fxConsolidated,before.fx)&&__same(restored.operationHistory,before.manual),'Backup changed histories');
      __assert(__same(before,__snap()),'Backup preparation changed S');
      for(const value of [null,[],17]){
        const bad=structuredClone(exported);bad.state.fxConsolidated=value;let refused=false;
        try{normalizeImportedState(bad);}catch(error){refused=true;}
        __assert(refused&&__same(before,__snap()),'Invalid present aggregate replaced base');
      }
      const future=structuredClone(exported);
      future.state.fxConsolidated={schemaVersion:99,unknown:{preserve:true},accounts:'future-opaque'};
      future.state.operationHistory={schemaVersion:99,records:'future-history-opaque',custom:[null,0]};
      const next=normalizeImportedState(future);
      __assert(__same(next.fxConsolidated,future.state.fxConsolidated),'Future MT5 normalized');
      __assert(__same(next.operationHistory,future.state.operationHistory),'Future manual normalized');
      return {covered:exported.cobertura.sections,future:next.fxConsolidated};
    }""",
    'future-envelope-commands-fail-closed': r"""async () => {
      S.fxConsolidated={schemaVersion:99,accounts:'opaque',unknown:{preserve:true}};save();const before=__snap();
      const prepared=__prepare(),preference=await __fcs.api.saveDefaultAccount('fx_A');
      __assert(!prepared.ok&&!preference.ok&&__same(before,__snap()),'Future aggregate overwritten');
      return {prepared,preference};
    }""",
    'future-manual-version-never-normalized': r"""async () => {
      for(const version of [99,'99',' 99 ']){
        S.operationHistory={schemaVersion:version,records:'future-opaque',extra:[null,0]};
        const before=structuredClone(S.operationHistory);operationNormalizeState();
        __assert(__same(S.operationHistory,before),'Future manual version normalized: '+version);
      }
      __assert(__fcs.writes===0,'Manual schema guard wrote');
      return {versions:[99,'99',' 99 '],writes:__fcs.writes};
    }""",
    'longitudinal-snapshot-keeps-incompatible-envelope-opaque': r"""async () => {
      for(const value of [null,[],{schemaVersion:1,accounts:[],receipts:[],revisions:[],defaultAccountId:17},
        {schemaVersion:99,accounts:[],future:true}]){
        const document=structuredClone(S);document.fxConsolidated=value;
        __assert(__same(fxConsolidatedLongitudinalSnapshot(document),value),'Invalid aggregate interpreted or repaired');
      }
      const document=structuredClone(S);document.accounts=[];
      document.operationHistory={schemaVersion:99,records:[{accountId:'future_opaque_account'}]};
      __assert(fxConsolidatedLongitudinalSnapshot(document).accounts.length===0,'Future manual schema interpreted');
      return {tested:'malformed and future envelopes remain opaque'};
    }""",
}


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def hashes(root):
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in SOURCES}


def finalize(page):
    page.locator('#finalizeSessionBtn').click()
    page.locator('#sessionHasCopy').click()
    assert 'consolidado fx' in page.locator('#modalBox').inner_text().lower()
    page.locator('#sessionProceed').click()
    page.locator('#sessionDeletePhrase').fill('ENCERRAR SESSÃO')
    page.locator('#sessionDeleteConfirm').click()
    page.wait_for_function("document.getElementById('sessionNotice').textContent.includes('Sessão finalizada')")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--case',default='')
    args=parser.parse_args();root=args.root.resolve()
    if args.out.exists():parser.error('Evidence exists; choose a new path')
    evidence={'root':str(root),'environment':'Chromium isolated contexts; loopback app; intercepted economic bootstrap',
              'sources_before':hashes(root),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':[]}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/index.html'

    def run(browser,name,source=None,callback=None):
        if args.case and args.case not in name:return
        record={'name':name,'pageerrors':[],'console_errors':[]};context=None
        try:
            context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
            install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
            page=context.new_page()
            page.on('pageerror',lambda error:record['pageerrors'].append(str(error)))
            page.on('console',lambda message:record['console_errors'].append(message.text) if message.type=='error' else None)
            page.goto(url);wait_bootstrap(page)
            page.wait_for_function("window.JPWFXConsolidated&&typeof JPWFXConsolidated.confirmImport==='function'")
            record['seed']=page.evaluate(SEED)
            record['observations']=page.evaluate(source) if source else callback(page,context,record)
            assert_fixture_requests(context)
            assert not record['pageerrors'],record['pageerrors']
            expected=('JP Wealth: falha ao gravar o estado no armazenamento local.',
                      'JP Wealth: conflito de concorrência entre abas detectado no save().',
                      '[persistência] DESFECHO INDETERMINADO')
            if not any(word in name for word in ('quota','unknown','cross-tab-conflict')):expected=()
            unexpected=[message for message in record['console_errors'] if not message.startswith(expected)]
            assert not unexpected,unexpected
            record['status']='PASS'
        except AssertionError as error:
            record.update(status='PRODUCT_FAIL',error=str(error),trace=traceback.format_exc())
        except Exception as error:
            status='PRODUCT_FAIL' if 'PRODUCT_ASSERTION:' in str(error) else 'TEST_HARNESS_FAIL'
            record.update(status=status,error=str(error),trace=traceback.format_exc())
        finally:
            if context:context.close()
            evidence['cases'].append(record)
            print(name,record['status'],record.get('error','')[:180],flush=True)

    def lifecycle(page,context,record):
        page.evaluate("async()=>{await __import();await __fcs.api.saveDefaultAccount('fx_A');markSessionCheckpoint();}")
        before=page.evaluate('__snap()')
        # A second actual app page must adopt the durable finalized document.
        second=context.new_page();second.goto(url);wait_bootstrap(second)
        second.evaluate('()=>{window.__onbShown=true;closeModal();}')
        page.evaluate('markSessionCheckpoint()')
        finalize(page)
        second.wait_for_function('S.accounts.length===0&&S.onboarding.done===false')
        after=page.evaluate('__snap()')
        remote=second.evaluate('()=>({fx:S.fxConsolidated,manual:S.operationHistory,accounts:S.accounts,forex:S.forex})')
        assert after['manual']==before['manual']
        assert after['fx']['receipts']==before['fx']['receipts'] and after['fx']['defaultAccountId']=='fx_A'
        assert after['accounts']==[] and remote['accounts']==[]
        assert remote['fx']==after['fx'] and remote['manual']==after['manual']
        catalog=page.evaluate('JPWFXConsolidated.accounts()')
        assert all(account['archived'] and account['liveIndex'] is None for account in catalog)
        assert not any('sini' in account or 'satu' in account or 'investorPassword' in account for account in after['fx']['accounts'])
        page.reload();wait_bootstrap(page)
        reloaded=page.evaluate('()=>({fx:S.fxConsolidated,manual:S.operationHistory,accounts:S.accounts})')
        assert reloaded['fx']==after['fx'] and reloaded['manual']==after['manual'] and reloaded['accounts']==[]
        return {'before':before,'after':after,'remote':remote,'catalog':catalog,'reloaded':reloaded}

    def cross_tab_conflict(page,context,record):
        page.evaluate('window.__preview=__prepare()')
        other=context.new_page();other.goto(url);wait_bootstrap(other)
        other_raw=other.evaluate("()=>{S.personalFinance.syntheticOtherTab='keep';if(save()!==true)throw Error('other write refused');return localStorage.getItem(LSKEY);}")
        result=page.evaluate('__fcs.api.confirmImport(__preview,{confirmIdentity:true})')
        after=page.evaluate('__snap()')
        assert result['persistido'] is False and after['raw']==other_raw and not after['fx']['receipts']
        return {'outcome':result,'otherRaw':other_raw,'after':after}

    def restore_file(page,context,record):
        page.evaluate("async()=>{await __import();window.__backup=JSON.parse(await dgBuildBackupBlob(1,'synthetic.json','2026-01-31T12:00:00Z').text());S.fxConsolidated=__fcs.api.emptyState();S.operationHistory={schemaVersion:1,records:[]};save();}")
        expected=page.evaluate('({fx:__backup.state.fxConsolidated,manual:__backup.state.operationHistory})')
        page.evaluate("importFullBackupFile(new File([JSON.stringify(__backup)],'synthetic-backup.json',{type:'application/json'}))")
        page.wait_for_function("__alerts.some(message=>message==='Backup importado com sucesso.')")
        after=page.evaluate('__snap()')
        assert after['fx']==expected['fx'] and after['manual']==expected['manual']
        return {'expected':expected,'after':after}

    def future_finalize(page,context,record):
        before=page.evaluate("()=>{S.fxConsolidated={schemaVersion:99,accounts:'opaque',extension:{keep:true}};S.operationHistory={schemaVersion:99,records:'opaque-future',extension:[0,null]};save();markSessionCheckpoint();return __snap();}")
        finalize(page);after=page.evaluate('__snap()')
        assert after['fx']==before['fx'] and after['manual']==before['manual']
        return {'before':before,'after':after}

    def late_local_import(page,context,record):
        # The existing transaction accepts the latest confirmed local save.
        # A report confirmed after opening the modal must not be rolled back by
        # restoring the earlier longitudinal snapshot.
        page.locator('#finalizeSessionBtn').click()
        page.locator('#sessionHasCopy').click()
        page.locator('#sessionProceed').click()
        imported=page.evaluate('async()=>{await __import();return __snap();}')
        page.locator('#sessionDeletePhrase').fill('ENCERRAR SESSÃO')
        page.locator('#sessionDeleteConfirm').click()
        page.wait_for_function("document.getElementById('sessionNotice').textContent.includes('Sessão finalizada')")
        after=page.evaluate('__snap()')
        assert after['fx']['receipts']==imported['fx']['receipts']
        assert after['manual']==imported['manual'] and after['accounts']==[]
        return {'imported':imported,'after':after}

    def failed_visual_cleanup(page,context,record):
        page.evaluate("()=>{__fcs.api.reset=()=>{throw Error('Synthetic visual cleanup failure');};}")
        finalize(page)
        after=page.evaluate('__snap()')
        assert after['accounts']==[] and len(after['manual']['records'])==1
        return {'after':after}

    def wipe(page,context,record):
        page.evaluate("async()=>{await __import();window.__oldPreview=__prepare('10001','fx_A','b');window.prompt=()=> 'APAGAR';await wipeAllData();}")
        outcome=page.evaluate('__fcs.api.confirmImport(__oldPreview,{confirmIdentity:true})')
        after=page.evaluate('__snap()')
        assert not outcome['ok'] and after['fx']['receipts']==[] and after['manual']['records']==[]
        return {'outcome':outcome,'after':after}

    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(**launch_options())
            for name,source in CASES.items():run(browser,name,source=source)
            run(browser,'backup-file-restore-real-flow',callback=restore_file)
            run(browser,'finalize-local-remote-and-reload',callback=lifecycle)
            run(browser,'future-histories-preserved-by-finalize',callback=future_finalize)
            run(browser,'late-local-confirmed-import-preserved-by-finalize',callback=late_local_import)
            run(browser,'failed-visual-cleanup-does-not-break-finalize',callback=failed_visual_cleanup)
            run(browser,'cross-tab-conflict-preserves-other-document',callback=cross_tab_conflict)
            run(browser,'explicit-wipe-removes-histories-and-invalidates-preview',callback=wipe)
            browser.close()
    except Exception as error:
        evidence.update(environment_error=str(error),trace=traceback.format_exc())
    finally:
        server.shutdown();server.server_close()
        evidence['sources_after']=hashes(root)
        evidence['source_unchanged']=evidence['sources_before']==evidence['sources_after']
        evidence['counts']={'total':len(evidence['cases']),'passed':sum(case['status']=='PASS' for case in evidence['cases']),
                            'failed':sum(case['status']!='PASS' for case in evidence['cases'])}
        statuses={case['status'] for case in evidence['cases']}
        if evidence.get('environment_error') or not evidence['source_unchanged']:
            evidence['result']='ENVIRONMENT_ERROR'
        elif 'PRODUCT_FAIL' in statuses:evidence['result']='PRODUCT_FAIL'
        elif 'TEST_HARNESS_FAIL' in statuses:evidence['result']='TEST_HARNESS_FAIL'
        else:evidence['result']='PASS' if evidence['cases'] else 'NOT_RUN'
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open('x') as output:json.dump(evidence,output,ensure_ascii=False,indent=2)
        print(json.dumps({key:evidence[key] for key in ('result','counts','source_unchanged')}))
    return 0 if evidence['result']=='PASS' else 1


if __name__=='__main__':sys.exit(main())

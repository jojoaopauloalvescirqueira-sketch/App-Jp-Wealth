#!/usr/bin/env python3
"""Documentary account profiles: temporal snapshots, atomic context, unchanged live risk.
Uses the existing real-browser bootstrap fixture and synthetic state only.
"""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options
from fx_consolidated_storage_test import SEED

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['src/js/00-core/01-risk-profiles.js','src/js/00-core/04-persistence.js',
           'src/js/10-domain/00-forex-state.js','src/js/10-domain/02-risk-calculations.js']
SETUP = r"""()=>{
 S.forex=JPWForex.state.empty();S.operationHistory={schemaVersion:2,records:[]};
 window.__state=JPWForex.state;
 window.__assign=(key='base',index=0)=>{
   const result=__state.mutate('synthetic-profile','Synthetic explicit choice',['accounts'],()=>{
     const a=S.accounts[index];a.riskProfileAssignment=__state.createRiskProfileAssignment(a,key,
       {source:'Synthetic manual declaration',declaredBy:'Synthetic operator',reason:'Synthetic deliberate assignment'});
     a.perfil=riskProfileByAny(key).name;
   });__assert(result.ok,JSON.stringify(result));return structuredClone(S.accounts[index].riskProfileAssignment);
 };
 window.__period=(startedAt='2026-01-01',index=0,extra={})=>{
   const accountId=S.accounts[index].forexAccountId,before=Object.keys(S.forex.accountContexts.accounts[accountId]?.periods||{});
   const r=__state.recordAccountPeriod({accountId,startedAt,currency:'USD',si:10000,openingBook:10000,
     source:'Synthetic initial capital',activateCurrentPeriod:true,...extra},{reason:'Synthetic explicit period'});
   return {...r,periodId:Object.keys(S.forex.accountContexts.accounts[accountId]?.periods||{}).find(x=>!before.includes(x))};
 };
 window.__facts=(periodId,equity=9500,index=0,options={})=>__state.recordAccountFacts({accountIndex:index,periodId,si:10000,
   currency:'USD',equity,netCashflow:0,cashflowAdjustmentRecorded:true,source:'Synthetic observation',observedAt:'2026-09-23T00:00:00Z'},
   {reason:'Synthetic observation',...options});
 if(save()!==true)throw Error('Synthetic setup not durable');
}"""
CASES = {
 'preparation-preserves-null-context-until-explicit-use':r"""()=>{
  const before=__state.operationalSelection(),raw=__snap().raw;
  __assert(before.accountId==='fx_A'&&before.periodId===null,'Fixture should have unique Master without period');
  const result=__state.withPreservedOperationalContext(()=>__period());
  __assert(result.ok&&__same(before,__state.operationalSelection()),'Preparing first period changed effective selection');
  __assert(__snap().raw!==raw,'Period must still persist');
  __assert(__state.selectOperationalContext('fx_A',result.periodId).ok,'Explicit use refused');
  __assert(__state.operationalSelection().periodId===result.periodId,'Explicit use did not release hold');
  const chosen=__state.operationalSelection(),original=save;save=()=>false;
  const refused=__state.withPreservedOperationalContext(()=>__period('2026-02-01'));save=original;
  __assert(!refused.ok&&__same(chosen,__state.operationalSelection()),'Refusal changed effective selection');
  return {before,period:result.periodId,refused};
 }""",
 'prepared-first-period-remains-unavailable-through-model-and-board-until-use':r"""()=>{
  const selected=__state.operationalSelection();__assert(selected.accountId==='fx_A'&&selected.periodId===null,'Fixture should lack selected period');
  const prepared=__state.withPreservedOperationalContext(()=>__period());__assert(prepared.ok,'Period preparation failed');
  const absent=[null,'',undefined].map(periodId=>__state.accountContext({accountId:'fx_A',periodId}));
  __assert(absent.every(r=>r.status==='NOT_COMPUTABLE'&&r.value===null),'Explicit absent period fell back');
  const legacy=__state.accountContext({accountId:'fx_A'});__assert(legacy.status==='OK'&&legacy.value.periodId===prepared.periodId,'Legacy omitted-period lookup changed');
  const record=__state.recordContext(__state.operationalSelection()),risk=__state.read(),board=JPWForex.executionBoard.read();
  __assert(record.status==='NOT_COMPUTABLE'&&record.accountId===null,'Record context activated absent period');
  __assert(risk.accountId===null&&risk.orders.total===0&&risk.account===null,'Risk model consumed prepared period');
  __assert(board.scope.periodId===null&&board.findings.some(f=>f.code==='BOARD_PERIOD_UNREGISTERED'),'Board model considers period selected');
  JPWForex.executionBoardUI.renderPhases();
  __assert(document.querySelectorAll('#phaseContainer .eb-order-table').length===0&&document.querySelectorAll('#phaseContainer [data-eb-save-row]').length===0,'Board exposes operable rows before use');
  __assert(JPWNavigation.navigate('forex-management-accounts')===true,'Accounts route refused');
  JPWForex.accountsUI.examine('fx_A',prepared.periodId);
  __assert(__state.operationalSelection().periodId===null,'Examination activated prepared period');
  const use=document.getElementById('fxAccountsUse');__assert(use&&!use.disabled,'Use action unavailable');use.click();
  __assert(__state.operationalSelection().periodId===prepared.periodId,'Explicit use did not activate period');
  JPWForex.executionBoardUI.renderPhases();
  __assert(__state.accountContext(__state.operationalSelection()).status==='OK'&&document.querySelectorAll('#phaseContainer .eb-order-table').length===6,'Use did not expose selected phases');
  return {before:{record:record.status,riskAccount:risk.accountId,boardPeriod:board.scope.periodId},after:__state.operationalSelection(),legacyOmissionPreserved:true};
 }""",
 'preparation-unknown-retains-pair-and-epoch-reset-releases-hold':r"""()=>{
  const before=__state.operationalSelection(),original=save;save=()=>undefined;
  const result=__state.withPreservedOperationalContext(()=>__period());save=original;
  __assert(result.persistido===null&&__same(before,__state.operationalSelection()),'Unknown result activated new fallback');
  // Epoch reset models a separately authorized reload/import boundary; it must not reuse a previous hold.
  resumeJPWealthPersistence();
  __assert(__state.operationalSelection().periodId===result.periodId,'Epoch retained stale hold');
  return {before,result};
 }""",
 'first-master-registration-preserves-unselected-context':r"""()=>{
  S.accounts=S.accounts.filter(a=>a.tipo!=='MESTRE');__assert(save()===true,'Fixture save refused');
  const before=__state.operationalSelection();__assert(before.accountId===null,'Fixture unexpectedly selected');
  const result=__state.withPreservedOperationalContext(()=>__state.mutate('synthetic-master','Synthetic explicit registration',['accounts'],()=>{
    S.accounts.push({forexAccountId:'fx_NEW',nome:'First synthetic Master',tipo:'MESTRE',platform:'MetaTrader 5',platformLogin:'0001',perfil:'',perfilLocked:false});
  }));
  const after=__state.operationalSelection();
  __assert(result.ok&&after.accountId===null&&after.periodId===null&&after.reason===before.reason,'New Master silently selected');
  return {before:{accountId:before.accountId,periodId:before.periodId},after:{accountId:after.accountId,periodId:after.periodId}};
 }""",
 'reload-invalid-profile-preserves-raw-and-blocks-writes':r"""()=>{
  __assign();const invalid=structuredClone(S);invalid.accounts[0].riskProfileAssignment.profileKey='invented';
  const raw=JSON.stringify(invalid);__fcs.nativeSet.call(localStorage,LSKEY,raw);return {reloadRaw:raw};
 }""",
 'archive-selected-explicit-without-hold-clears-instead-of-master-fallback':r"""()=>{
  const a=__period(),b=__period('2026-01-01',1);__state.selectOperationalContext('fx_B',b.periodId);
  const result=__state.archiveRegisteredAccount('fx_B',{reason:'Synthetic selected archive'}),selection=__state.operationalSelection();
  __assert(result.ok&&selection.accountId===null&&selection.periodId===null&&selection.requiresSelection,'Archive activated Master fallback');
  __assert(S.accounts.some(a=>a.forexAccountId==='fx_A'),'Remaining Master missing');return {result,selection};
 }""",
 'archive-selected-with-hold-clears-stale-pair':r"""()=>{
  const a=__period(),b=__period('2026-01-01',1);__state.selectOperationalContext('fx_B',b.periodId);
  __state.withPreservedOperationalContext(()=>({ok:true,persistido:false}));
  const result=__state.archiveRegisteredAccount('fx_B',{reason:'Synthetic held selected archive'}),selection=__state.operationalSelection();
  __assert(result.ok&&selection.accountId===null&&selection.periodId===null&&selection.requiresSelection,'Archive retained deleted account');return {result,selection};
 }""",
 'archive-other-account-preserves-held-and-fallback-context':r"""()=>{
  const a=__period(),b=__period('2026-01-01',1),snapshot=structuredClone(S.accounts[1]);
  const pair=()=>{const s=__state.operationalSelection();return [s.accountId,s.periodId,s.reason,s.requiresSelection];};
  const before=pair(),first=__state.archiveRegisteredAccount('fx_B',{reason:'Synthetic other archive'});
  __assert(first.ok&&__same(before,pair()),'Other archive changed fallback context');
  __assert(__state.mutate('synthetic-reregister','Synthetic preserved identity',['accounts'],()=>S.accounts.push(snapshot)).ok,'Synthetic reregister refused');
  __state.selectOperationalContext('fx_A',a.periodId);__state.withPreservedOperationalContext(()=>({ok:true,persistido:false}));
  const held=pair(),second=__state.archiveRegisteredAccount('fx_B',{reason:'Synthetic other archive with hold'});
  __assert(second.ok&&__same(held,pair()),'Other archive changed held context');return {first,second,before,held};
 }""",
 'archive-refusal-and-unknown-never-activate-fallback':r"""()=>{
  const a=__period(),b=__period('2026-01-01',1);__state.selectOperationalContext('fx_B',b.periodId);
  const before=__state.operationalSelection(),persisted=__snap(),original=save;save=()=>false;
  const refused=__state.archiveRegisteredAccount('fx_B',{reason:'Synthetic refused archive'});save=original;
  __assert(!refused.ok&&__same(before,__state.operationalSelection())&&__same(persisted,__snap()),'Refusal changed account, selection or persistence');
  save=()=>undefined;const unknown=__state.archiveRegisteredAccount('fx_B',{reason:'Synthetic unknown archive'});save=original;
  const selected=__state.operationalSelection();
  __assert(unknown.persistido===null&&jpWealthPersistenceOutcomeIsUnknown(),'Unknown archive not blocked');
  __assert(selected.accountId==='fx_B'&&selected.periodId===b.periodId,'Unknown archive activated another context');
  __assert(__snap().raw===persisted.raw,'Synthetic unknown unexpectedly wrote');return {refused,unknown,selected};
 }""",
 'archive-reload-keeps-legacy-boot-fallback':r"""()=>{
  const a=__period(),b=__period('2026-01-01',1);__state.selectOperationalContext('fx_B',b.periodId);
  const result=__state.archiveRegisteredAccount('fx_B',{reason:'Synthetic archive before reload'});
  __assert(result.ok&&__state.operationalSelection().accountId===null,'Archive did not clear RAM selection');
  return {masterPeriod:a.periodId};
 }""",
 'archive-reregister-archive-preserves-profile-history':r"""()=>{
  const assignment=__assign('longevity',1),id='fx_B';
  const first=__state.archiveRegisteredAccount(id,{reason:'Synthetic first archive'});__assert(first.ok,'First archive refused');
  const snapshot=structuredClone(S.forex.accountContexts.archivedAccounts[id]);
  const returnRegistration=__state.mutate('synthetic-reregister','Synthetic restored identity',['accounts'],()=>{
    const record=structuredClone(snapshot.record);record.sini=0;record.satu=0;S.accounts.push(record);
  });__assert(returnRegistration.ok,'Reregister refused');
  const second=__state.archiveRegisteredAccount(id,{reason:'Synthetic second archive'});__assert(second.ok,'Second legitimate archive refused');
  const current=S.forex.accountContexts.archivedAccounts[id];
  __assert(__same(current.previous,snapshot)&&__same(current.record.riskProfileAssignment,assignment),'Archive lost previous tombstone/profile');
  const roundtrip=normalizeImportedState(structuredClone(S));
  __assert(__same(roundtrip.forex.accountContexts.archivedAccounts[id],current),'Archive chain import changed history');
  const invalid=structuredClone(S);invalid.forex.accountContexts.archivedAccounts[id].previous.record.riskProfileAssignment.profileKey='invented';
  let rejected=false;try{normalizeImportedState(invalid);}catch(e){rejected=true;}__assert(rejected,'Nested invalid assignment imported');
  const duplicate=__state.archiveRegisteredAccount(id,{reason:'Synthetic duplicate archive'});__assert(!duplicate.ok,'Duplicate archive without registration accepted');
  return {first,second,duplicate,chainPreserved:true};
 }""",
 'legacy-no-base-fallback-or-backfill':r"""()=>{
  const p=__period();__assert(p.ok,'Legacy period refused');
  const before=__snap(),global=structuredClone(S.period),c=__state.accountProfileContext({accountId:'fx_A',periodId:p.periodId});
  __assert(c.current===null&&c.period===null&&c.legacyName==='Base','Legacy name became confirmed profile');
  __assert(c.status==='NOT_COMPUTABLE'&&!S.forex.accountContexts.accounts.fx_A.periods[p.periodId].riskProfileSnapshot,'Legacy backfilled');
  __assert(__same(before,__snap())&&__same(global,S.period),'Read wrote');return c;
 }""",
 'assignment-revision-and-explicit-following-period':r"""()=>{
  const a=__assign(),first=__period();__assert(first.ok,'First period refused');
  const prior=structuredClone(S.forex.accountContexts.accounts.fx_A.periods[first.periodId]);
  const b=__assign('longevity');__assert(b.revision===2&&__same(b.previous,a),'Revision chain missing');
  const current=__state.accountProfileContext({accountId:'fx_A',periodId:first.periodId});
  __assert(current.period.key==='base'&&current.next.key==='longevity'&&current.hasPendingChange,'Period changed retroactively');
  __assert(__same(prior,S.forex.accountContexts.accounts.fx_A.periods[first.periodId]),'Period rewritten');
  const historical=__period('2025-12-01',0,{activateCurrentPeriod:false});__assert(historical.ok,'Historical factual period refused');
  __assert(!S.forex.accountContexts.accounts.fx_A.periods[historical.periodId].riskProfileSnapshot,'Historical period inherited current assignment');
  const sameDay=__period('2026-01-01',0,{activateCurrentPeriod:false});__assert(sameDay.ok&&!S.forex.accountContexts.accounts.fx_A.periods[sameDay.periodId].riskProfileSnapshot,'Nonposterior period activated assignment');
  const following=__period('2026-02-01');__assert(following.ok,'Following period refused');
  const next=__state.accountProfileContext({accountId:'fx_A',periodId:following.periodId});
  __assert(next.period.key==='longevity'&&next.period.revision===2&&!next.hasPendingChange,'Following period failed to capture');
  const again=__assign('longevity');__assert(again.revision===2,'Same key invented revision');
  return {current,next,historicalProfileAbsent:true,priorPreserved:true};
 }""",
 'atomic-pair-selection-no-persistence':r"""()=>{
  __assign();__assign('high_longevity',1);const a=__period(),b=__period('2026-01-01',1);
  __assert(__state.selectOperationalContext('fx_A',a.periodId).ok,'Valid A selection refused');
  const before=__snap(),selected=__state.operationalSelection(),global=structuredClone(S.period);
  const inspected=__state.accountProfileContext({accountId:'fx_B',periodId:b.periodId});
  const failures=[['fx_B',a.periodId],['missing',b.periodId],['fx_A',null],[null,null]].map(v=>__state.selectOperationalContext(...v));
  __assert(failures.every(r=>!r.ok)&&__same(selected,__state.operationalSelection()),'Invalid pair partly changed selection');
  __assert(inspected.current.key==='high_longevity'&&__same(before,__snap()),'Inspection created financial facts');
  __assert(__state.selectOperationalContext('fx_B',b.periodId).ok,'Valid B selection refused');
  __assert(__same(before,__snap())&&__same(global,S.period),'Context selection persisted or changed global profile');
  S.accounts.push({...S.accounts[0]});const duplicate=__state.selectOperationalContext('fx_A',a.periodId);
  __assert(!duplicate.ok&&__state.operationalSelection().accountId==='fx_B','Ambiguous account selected');return {failures,duplicate};
 }""",
 'live-risk-invariant-to-documentary-profile':r"""()=>{
  __assign();const a=__period();__assert(__facts(a.periodId).ok,'Observation refused');__state.selectOperationalContext('fx_A',a.periodId);
  const first=JPWForex.readModel(),policy=structuredClone(first.policySnapshot),snapshot=structuredClone(first.accountProfile.period);
  __assign('high_longevity_plus');const second=JPWForex.readModel();
  __assert(__same(first.metrics,second.metrics)&&__same(first.accountPhase,second.accountPhase)&&__same(first.executionEligibility,second.executionEligibility),'Documentary profile changed risk');
  __assert(second.metrics.drawdown.value===5&&second.metrics.replication.replicationAllowed===false,'Normative baseline differs');
  __assert(__facts(a.periodId,8800).ok,'New equity refused');const live=JPWForex.readModel();
  __assert(live.metrics.drawdown.value===12&&live.accountPhase.value===4,'Profile snapshot froze live risk');
  __assert(__same(policy,live.policySnapshot)&&__same(snapshot,live.accountProfile.period),'Snapshot/policy rewritten');
  return {ddBefore:5,ddAfter:live.metrics.drawdown.value,phase:live.accountPhase.value,replicationAllowed:false};
 }""",
 'operation-captures-period-not-current-profile':r"""()=>{
  __assign();const a=__period();__assign('longevity');
  const r=__state.recordAccountOrders([{pi:0,oi:0,changes:{id:'SYNTH',brokerHash:'000000000000000000001',par:'EURUSD',tipo:'BUY',role:'GENESIS',
    status:'Pendente',lote:0.01,entry:1.1,sl:1,tp:1.2,costs:0,costBasis:'SEPARATE_FROM_RESULT',stopValidated:true}}],
    {accountId:'fx_A',periodId:a.periodId,reason:'Synthetic first fact'});
  __assert(r.ok,JSON.stringify(r));const op=S.forex.accountContexts.accounts.fx_A.periods[a.periodId].activeOperation;
  __assert(op.recordContext.riskProfileSnapshot.profileKey==='base','Operation used new assignment instead of period snapshot');
  const frozen=structuredClone(op);__assign('high_longevity');__assert(__same(op,frozen),'Open operation snapshot changed');
  const blocked=__period('2026-02-01');__assert(!blocked.ok,'Active operation lost period protection');
  return {recordContext:op.recordContext,blocked};
 }""",
 'observations-do-not-assign-profile-or-change-selection':r"""()=>{
  __assign();const a=__period(),b=__period('2026-01-01',1);__assert(__facts(a.periodId).ok,'A observation refused');
  __state.selectOperationalContext('fx_A',a.periodId);const before=__state.operationalSelection();
  __assert(__facts(b.periodId,9200,1,{preserveSelection:true}).ok,'B observation refused');
  __assert(S.forex.activeAccountId==='fx_A'&&__same(before,__state.operationalSelection()),'Examined B changed context');
  __assert(!S.forex.accountContexts.accounts.fx_B.periods[b.periodId].riskProfileSnapshot,'Observation backfilled profile');
  return {reference:S.forex.activeAccountId,selection:before};
 }""",
 'backup-roundtrip-unknown-fields-and-prewrite-rejection':r"""async()=>{
  __assign();const a=__period();S.accounts[0].accountEnvironment='demo';S.accounts[0].futureExtension={preserved:true};
  S.accounts[0].riskProfileAssignment.futureMetadata='keep';S.forex.accountContexts.accounts.fx_A.periods[a.periodId].riskProfileSnapshot.futureMetadata='keep';
  __assert(save()===true,'Fixture save refused');const before=__snap();
  const doc=JSON.parse(await dgBuildBackupBlob(1,'synthetic-profile.json','2026-09-23T00:00:00Z').text());
  const restored=normalizeImportedState(doc);__assert(__same(restored.accounts,S.accounts)&&__same(restored.forex,S.forex),'Roundtrip changed optional data');
  const bad=[d=>d.state.accounts[0].accountEnvironment='LIVE',d=>d.state.accounts[0].riskProfileAssignment.profileKey='invented',
    d=>d.state.accounts[0].riskProfileAssignment.revision=0,d=>d.state.accounts[0].riskProfileAssignment.accountId='fx_B',
    d=>d.state.forex.accountContexts.accounts.fx_A.periods[a.periodId].riskProfileSnapshot.periodId='wrong'];
  for(const change of bad){const copy=structuredClone(doc);change(copy);let refused=false;try{normalizeImportedState(copy);}catch(e){refused=true;}
    __assert(refused&&__same(before,__snap()),'Malformed import wrote or was accepted');}
  return {roundtrip:true,invalidRejected:bad.length,unknownFieldsPreserved:true};
 }""",
 'refused-period-keeps-assignment-without-snapshot':r"""()=>{
  const assignment=__assign(),before=__snap(),original=save;save=()=>false;
  const result=__period();save=original;
  __assert(!result.ok&&result.persistido===false&&__same(before,__snap()),'Refused period created profile snapshot');
  __assert(__same(assignment,S.accounts[0].riskProfileAssignment),'Refusal lost confirmed account assignment');
  const retry=__period();__assert(retry.ok&&Object.keys(S.forex.accountContexts.accounts.fx_A.periods).length===1,'Retry duplicated period');return {result,retry};
 }""",
 'legacy-backup-without-profile-extensions-remains-valid':r"""()=>{
  const old=structuredClone(S),before=__snap();const restored=normalizeImportedState(old);
  __assert(restored.accounts.every(a=>!('riskProfileAssignment'in a)&&!('accountEnvironment'in a)),'Legacy metadata fabricated');
  __assert(__same(before,__snap()),'Legacy normalization wrote');
  for(const key of ['invented','',null]){let rejected=false;try{__state.createRiskProfileAssignment(S.accounts[0],key,{source:'Synthetic',declaredBy:'Synthetic',reason:'Synthetic'});}catch(e){rejected=true;}__assert(rejected,'Invalid profile accepted');}
  return {legacyAccepted:true,noDefaultAssignment:true};
 }"""
}

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--case',default='');args=parser.parse_args()
    if args.out.exists():parser.error('Evidence path already exists')
    root=args.root.resolve();hashes=lambda:{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCES}
    report={'root':str(root),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'before':hashes(),'cases':[]}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options())
            for name,source in CASES.items():
                if args.case and args.case not in name:continue
                record={'name':name,'pageerrors':[]};context=None
                try:
                    context=browser.new_context(service_workers='block');install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
                    page=context.new_page();page.on('pageerror',lambda e,r=record:r['pageerrors'].append(str(e)))
                    page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page)
                    page.evaluate(SEED);page.evaluate(SETUP);record['observations']=page.evaluate(source)
                    if name=='reload-invalid-profile-preserves-raw-and-blocks-writes':
                        expected=record['observations']['reloadRaw'];page.reload();wait_bootstrap(page)
                        check=page.evaluate("""expected=>({recovery:jpWealthLoadRecoveryActive(),kind:jpWealthLoadRecovery.kind,
                          rawPreserved:localStorage.getItem(LSKEY)===expected,saveRefused:save()===false,
                          rawPreservedAfterSave:localStorage.getItem(LSKEY)===expected})""",expected)
                        assert check['recovery'] and check['kind']=='migracao' and check['rawPreserved'] and check['saveRefused'] and check['rawPreservedAfterSave'],check
                        record['observations']=check
                    if name=='archive-reload-keeps-legacy-boot-fallback':
                        expected=record['observations']['masterPeriod'];page.reload();wait_bootstrap(page)
                        selected=page.evaluate("()=>JPWForex.state.operationalSelection()")
                        assert selected['accountId']=='fx_A' and selected['periodId']==expected and selected['reason']=='UNIQUE_MASTER',selected
                        record['observations']={'afterReload':selected,'legacyBootFallbackPreserved':True}
                    assert_fixture_requests(context);assert not record['pageerrors'],record['pageerrors'];record['status']='PASS'
                except Exception as error:
                    record.update(status='PRODUCT_FAIL' if isinstance(error,AssertionError) or 'PRODUCT_ASSERTION:' in str(error) else 'TEST_HARNESS_FAIL',error=str(error),trace=traceback.format_exc())
                finally:
                    if context:context.close()
                    report['cases'].append(record);print(name,record['status'],record.get('error','')[:240],flush=True)
            browser.close()
    except Exception as error:report['environment_error']=str(error)
    finally:
        server.shutdown();server.server_close();report['after']=hashes();report['sourcesUnchanged']=report['before']==report['after']
        report['result']='PASS' if report['cases'] and all(c['status']=='PASS' for c in report['cases']) and report['sourcesUnchanged'] and not report.get('environment_error') else 'FAIL'
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report['result'],flush=True)
    return 0 if report['result']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Forex ledger: preserved confirmation, refusal and UNKNOWN contracts.

Retired planning-only cases are explicitly replaced by current independent
planning state/UI suites. No old planning case is counted as a current PASS.
Daily ledger/scoped writer/reserve financial oracles below remain unchanged.

Oráculos fixados antes do patch (CHG-FUNCTIONAL-RELIABILITY-20260911).
App real servido da --root, Chromium isolado e fixtures nominais existentes.
Não corrige nem classifica reservas como regra aprovada: caracteriza a discrepância.
Lifecycle mensal adaptado explicitamente em CHG-JPW-PLANNING-TEST-CONTRACT-20261006:
conferência de depósitos e fixture de correção já reaberta antes da falha física.
Oráculos monetários, rollback, concorrência, desfecho desconhecido e escrita única
permanecem intactos. O recibo bruto anterior não é reescrito por esta execução.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import threading
import traceback
import notes_launcher_test as launcher
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

SOURCE_PATHS = [
    'src/js/10-domain/00-forex-state.js',
    'src/js/10-domain/19-execution-market.js',
    'src/js/40-app/01-navigation.js',
    'src/js/30-accounting/01-daily-ledger.js',
    'src/js/30-accounting/04-patrimonial-simulation.js',
    'src/js/00-core/04-persistence.js',
]

SEED = """() => {
  window.__onbShown=true; closeModal();
  window.__alerts=[]; window.alert=t=>window.__alerts.push(String(t));
  window.confirm=()=>true;
  window.prompt=()=> 'Motivo sintético explícito';
  // Mantém os instrumentos da fixture econômica já concluída; o reset de
  // domínio não deve ressuscitar preços default anteriores ao bootstrap.
  const bootInstruments=structuredClone(S.instruments);
  const bootDailyReferences=structuredClone(S.forex.dailyReferences);
  S=structuredClone(DEFAULTS); migrate(); S.instruments=bootInstruments;
  // As referências já confirmadas também pertencem ao bootstrap. Apagá-las
  // provocaria uma gravação legítima e alheia ao caso durante a recarga.
  S.forex.dailyReferences=bootDailyReferences;
  S.onboarding.done=true;
  S.params.saldoIni=10000; S.params.saldoAtu=10000;
  S.ledger=[];
  // Contabilidade é segregada por conta/período desde o baseline a62258f.
  // Não semear o ledger global legado, que permanece fora dos totais atuais.
  S.accounts=[{forexAccountId:'PERSIST-A',nome:'Mestre sintético',tipo:'MESTRE',platformCurrency:'USD'}];
  const period=JPWForex.state.recordAccountPeriod({accountId:'PERSIST-A',startedAt:'2026-01-01',
    currency:'USD',si:10000,openingBook:10000,source:'Fixture sintética de persistência',activateCurrentPeriod:true},
    {reason:'Fixture sintética de persistência'});
  if(!period.ok)throw new Error(period.error);
  const selected=JPWForex.state.selectOperationalAccount('PERSIST-A');
  if(!selected.ok)throw new Error(selected.error);
  S.dataGovernance.changeLog=Array.from({length:400},(_,i)=>({id:'dg-old-'+i,ts:'2025-01-01T00:00:00Z',entity:'synthetic',action:'historical',recordId:'',label:''}));
  if(save()!==true) throw new Error('seed não gravou');
  window.__saveReal=save;
  window.__barrierWriterAttempts=0;
  const observedSetItem=Storage.prototype.setItem;
  Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===LSKEY)window.__barrierWriterAttempts++;return observedSetItem.call(this,k,v);};
  window.__period=(state=S)=>{const a=state.forex.accountContexts.accounts['PERSIST-A'];return a.periods[a.currentPeriodId];};
  window.__snap=()=>({fx:JSON.stringify(S.fxPlanning),ledger:JSON.stringify(__period().ledger),
    legacyLedger:JSON.stringify(S.ledger),
    accountState:JSON.stringify(S.forex.accountContexts),
    saldo:__period().ledger.at(-1)?.saldo??__period().openingBook,log:JSON.stringify(S.dataGovernance.changeLog),raw:localStorage.getItem(LSKEY),
    unknown:jpWealthPersistenceOutcomeIsUnknown(),recovered:document.getElementById('persistenceAlert')?.classList.contains('is-recovered'),saved:document.getElementById('savedTag').classList.contains('show')});
  window.__installFailure=(kind)=>{
    window.__saveCalls=0;
    if(kind==='quota'){
      window.__setReal=Storage.prototype.setItem;
      Storage.prototype.setItem=function(k,v){if(k===LSKEY)throw new DOMException('Quota sintética','QuotaExceededError');return window.__setReal.call(this,k,v);};
    }
    save=function(){window.__saveCalls++;
      if(kind==='false')return false;
      if(kind==='throw-before')throw new Error('exceção antes da escrita');
      if(kind==='throw-after'){window.__saveReal();throw new Error('exceção depois da escrita');}
      if(kind==='undefined')return undefined;
      return window.__saveReal();
    };
    if(kind==='blocked')blockJPWealthPersistence();
    if(kind==='recovery')jpWealthLoadRecovery.active=true;
  };
  window.__restoreFailure=()=>{
    if(window.__setReal){Storage.prototype.setItem=window.__setReal;window.__setReal=null;}
    save=window.__saveReal;
    if(jpWealthLoadRecovery.active)jpWealthLoadRecovery.active=false;
    if(jpWealthPersistenceIsBlocked())resumeJPWealthPersistence();
  };
  return __snap();
}"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class Server(ThreadingHTTPServer):
    # The app loads many local scripts at once. The default queue of five can
    # reset those requests on macOS before the browser reaches the fixture.
    request_queue_size = 128
    daemon_threads = True


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--artifact',type=Path,required=True)
    ap.add_argument('--case',default='')
    args=ap.parse_args(); root=args.root.resolve()
    test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    artifact={'root':str(root),'test_sha256':test_sha256,'sources':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCE_PATHS},'cases':[]}
    server=Server(('127.0.0.1',0),partial(Quiet,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/index.html'
    def case(name, callback):
        if args.case and args.case not in name:return
        record={'name':name,'observations':{},'console':[],'pageerror':[]}
        context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
        install_bootstrap(context)
        context.add_init_script('window.__onbShown=true;')
        page=context.new_page()
        page.on('console',lambda m:record['console'].append({'type':m.type,'text':m.text}))
        page.on('pageerror',lambda e:record['pageerror'].append(str(e)))
        try:
            page.goto(url);wait_bootstrap(page);page.evaluate(SEED)
            callback(page,record['observations'])
            assert_fixture_requests(context)
            assert not record['pageerror'],record['pageerror']
            record['status']='PASS'
        except Exception as e:
            record['status']='FAIL';record['error']=str(e);record['trace']=traceback.format_exc()
        finally:
            context.close();artifact['cases'].append(record)
            print(name,record['status'],record.get('error','')[:300],flush=True)
    def assert_unknown_save_barrier(p,o,label):
        # save() exposes UNKNOWN through its typed exception, rather than the
        # proven-refusal false result. Observe the real writer and durable base.
        before=p.evaluate('({writes:__barrierWriterAttempts,raw:localStorage.getItem(LSKEY)})')
        result=p.evaluate("""()=>{try{return {returned:save()};}catch(error){return {name:error.name,result:error.persistenceResult};}}""")
        after=p.evaluate('({writes:__barrierWriterAttempts,raw:localStorage.getItem(LSKEY),unknown:jpWealthPersistenceOutcomeIsUnknown()})')
        o[label]={'before':before,'result':result,'after':after}
        assert result.get('name')=='JPWealthPersistenceUnknownError',result
        assert result.get('result',{}).get('status')=='UNKNOWN' and result['result']['reason']=='PENDING_VERIFICATION',result
        assert after['unknown'] and after['writes']==before['writes'] and after['raw']==before['raw'],after
    def daily(mode,delete=False,update=False):
        def run(p,o):
            p.evaluate("() => {JPWNavigation.navigate('forex-reconciliation');}")
            if delete or update:
                p.evaluate("() => {const r=ledgerRecord({data:'2026-01-02',resultado:5,saldo:null,nota:'anterior'});if(!r.ok)throw Error(r.error);renderLedger();}")
            before=p.evaluate('__snap()');o['before']=before
            if not delete:
                p.locator('#ldDate').fill('2026-01-02');p.locator('#ldResult').fill('-100');p.locator('#ldNota').fill('rascunho sintético')
            p.evaluate('__installFailure',mode)
            p.locator('[data-ledger-void]' if delete else '#ldAddBtn').click()
            after=p.evaluate('__snap()');o['after']=after;o['status']=p.locator('#ldStatus').inner_text()
            assert '✓' not in o['status'] and o['status'],o
            if mode in ('throw-before','throw-after','undefined'):
                assert after['unknown'] and not after['saved'],after
                assert after['ledger']!=before['ledger']
                if mode=='throw-after':assert after['raw']!=before['raw']
                else:assert after['raw']==before['raw']
                calls=p.evaluate('__saveCalls');p.locator('[data-ledger-void]' if delete else '#ldAddBtn').click()
                assert p.evaluate('__saveCalls')==calls
                p.evaluate('__restoreFailure()');assert_unknown_save_barrier(p,o,'restoredWriterBarrier')
            else:
                for key in ['fx','ledger','legacyLedger','accountState','saldo','log','raw']:assert after[key]==before[key],key
                if not delete:assert p.locator('#ldResult').input_value()=='-100' and p.locator('#ldNota').input_value()=='rascunho sintético'
                p.evaluate('__restoreFailure()')
                p.evaluate("() => {S.atr55=7;save();}")
                assert p.evaluate("JSON.stringify(__period(JSON.parse(localStorage.getItem(LSKEY))).ledger)")==before['ledger']
                p.locator('[data-ledger-void]' if delete else '#ldAddBtn').click()
                committed=p.evaluate('__snap()');o['committed']=committed
                assert len(json.loads(committed['ledger']))==(0 if delete else 1)
                assert committed['saldo']==(10000 if delete else 9900)
                assert len(json.loads(committed['log']))==400
                assert json.loads(committed['log'])[-2]==json.loads(before['log'])[-1]
                if not delete:assert p.locator('#ldResult').input_value()==''
                p.reload();wait_bootstrap(p)
                assert p.evaluate('JSON.stringify(JPWForex.state.accountLedger(JPWForex.state.operationalSelection()).value)')==committed['ledger']
        return run
    def cancellation(p,o):
        p.evaluate("() => {const r=ledgerRecord({data:'2026-01-02',resultado:5,saldo:null,nota:'anterior'});if(!r.ok)throw Error(r.error);JPWNavigation.navigate('forex-reconciliation');renderLedger();window.confirm=()=>false;}")
        before=p.evaluate('__snap()');p.locator('#ldDate').fill('2026-01-02');p.locator('#ldResult').fill('12');p.locator('#ldAddBtn').click()
        p.locator('[data-ledger-void]').click();after=p.evaluate('__snap()');o.update(before=before,after=after)
        for key in ['fx','ledger','legacyLedger','accountState','saldo','log','raw']:assert after[key]==before[key]
        p.locator('#ldDate').fill('2026-01-01');p.locator('#ldAddBtn').click()
        assert p.evaluate('__snap().ledger')==before['ledger'],'cancelar backdate alterou ledger'
    def two_tabs(p,o):
        second=p.context.new_page();second.goto(url);wait_bootstrap(second)
        # B commits through the actual save implementation. No storage listener
        # is replaced: the observations prove whether A refuses its stale state.
        second.evaluate("() => {S.atr55=13;if(save()!==true)throw new Error('B não gravou');}")
        p.wait_for_timeout(100)
        before=p.evaluate('__snap()');result=p.evaluate("ledgerRecord({data:'2026-01-02',resultado:10,saldo:10010})");after=p.evaluate('__snap()')
        o.update(before=before,result=result,after=after)
        assert result.get('ok') is False,result
        assert after['fx']==before['fx'] and after['log']==before['log']
        assert json.loads(after['raw'])['atr55']==13
        second.close()
    def reserves(p,o):
        # V11 supersedes the earlier discrepancy characterization: explicit
        # nominal Master capital determines FCR; legacy onboarding is retained
        # as history and cannot certify constitution or release a cycle.
        actual=p.evaluate("""() => {
          const index=S.accounts.findIndex(a=>a.tipo==='MESTRE');
          const a=JPWForex.state.recordAccountFacts({accountIndex:index,si:10000,equity:10000,capitalNominal:5000,
            netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',source:'synthetic',observedAt:'2026-09-14T12:00:00Z'}, {reason:'Apuração sintética'});
          const b=JPWForex.state.recordReserves({capitalNominal:5000,fcrConstituted:1000,feoConstituted:600,
            sixMonthExpenseAmount:600,fcrLiquidityDays:1,feoLiquidityDays:2,verificationRecorded:true,verifiedAt:'2026-09-14T12:00:00Z',expensesApproved:true,source:'synthetic',expensePeriod:'2026-09/2027-02',determinationReference:'synthetic-reference',determinationRecorded:true}, {reason:'Reservas sintéticas'});
          const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),model=JPWForex.state.read();
          renderParams();const unchanged=before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY);
          return {a,b,unchanged,required:model.metrics.fcrRequirement,status:model.metrics.fcrStatus,opening:model.reserves.openingStatus};
        }""")
        o.update(actual)
        assert actual['a']['ok'] and actual['b']['ok'],actual
        assert actual['required']['value']==1100 and actual['required']['baseType']=='MASTER_NOMINAL_CAPITAL',actual
        assert actual['status']['status']=='BLOCKED' and actual['opening']=='BLOCKED' and actual['unchanged'],actual
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launcher.launch_options())
            for mode in ['quota','false','blocked','recovery','throw-before','throw-after','undefined']:
                case('daily-create-'+mode,daily(mode))
            case('daily-update-quota',daily('quota',update=True))
            case('daily-delete-quota',daily('quota',delete=True))
            for mode in ['throw-before','throw-after','undefined']:
                case('daily-delete-'+mode,daily(mode,delete=True))
            case('daily-cancel',cancellation)
            case('two-tabs-refusal',two_tabs)
            case('reserves-v11-nominal-capital-confirmation',reserves)
            browser.close()
    finally:
        server.shutdown();server.server_close()
        artifact['sources_after']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCE_PATHS}
        assert artifact['sources_after']==artifact['sources'],'fontes mudaram durante os focais'
        assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==test_sha256,'teste mudou durante a execução'
        artifact['summary']={'total':len(artifact['cases']),'passed':sum(c['status']=='PASS' for c in artifact['cases']),'failed':sum(c['status']=='FAIL' for c in artifact['cases'])}
        args.artifact.parent.mkdir(parents=True,exist_ok=True)
        args.artifact.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(artifact['summary']),flush=True)
    return 1 if artifact['summary']['failed'] or not artifact['cases'] else 0


if __name__=='__main__':
    raise SystemExit(main())

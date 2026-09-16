#!/usr/bin/env python3
"""Finalização contextual: contratos negativos e atomicidade em duas contas.

O oráculo anterior, que dependia de S.phases/S.activeOperation globais, está
arquivado em evidência externa. Esta suíte exercita o caminho atual do produto.
Todas as identidades e valores são sintéticos.
"""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import os,socket,threading
import notes_launcher_test as launcher
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_):pass
def serve():
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    server=ThreadingHTTPServer(('127.0.0.1',port),Quiet)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server,f'http://127.0.0.1:{port}/index.html'
SEED='''(kind) => {
  S=structuredClone(DEFAULTS);migrate();S.onboarding.done=true;
  S.accounts=[{forexAccountId:'FIN_A',nome:'Mestre sintética',tipo:'MESTRE',platformCurrency:'USD'},
    {forexAccountId:'FIN_B',nome:'Conta B sintética',tipo:'PRÓPRIA',platformCurrency:'USD'}];
  S.forex=JPWForex.state.empty();S.operationHistory={schemaVersion:2,records:[]};
  if(save()!==true)throw Error('Fixture refused');
  const x=JPWForex.state;
  for(const [accountId,si] of [['FIN_A',10000],['FIN_B',5000]]){
    const r=x.recordAccountPeriod({accountId,startedAt:'2026-09-01',currency:'USD',si,openingBook:si,
      source:'Fixture sintética',activateCurrentPeriod:true},{reason:'Fixture sintética'});
    if(!r.ok)throw Error(r.error);
  }
  const add=(accountId,status,result,costs=0,costBasis='INCLUDED_IN_RESULT')=>{
    x.selectOperationalAccount(accountId);const scope=x.operationalSelection();
    const r=x.recordAccountOrders([{pi:0,oi:0,changes:{id:accountId+'-1',par:'EURUSD',tipo:'BUY',
      role:'GENESIS',lote:.01,entry:1.1,sl:1.09,tp:1.2,status,result,costs,costBasis,
      stopValidated:true}}],{...scope,reason:'Fato sintético'});
    if(!r.ok)throw Error(r.error);return scope;
  };
  const a=add('FIN_A','Fechada',40),b=add('FIN_B',kind==='open'?'Aberta':'Fechada',
    kind==='open'?null:-20,kind==='costs'?-3:0,kind==='costs'?'SEPARATE_FROM_RESULT':'INCLUDED_IN_RESULT');
  navNavigate('forex-operation');execSetView('panel');JPWForex.executionBoardUI.render();
  return {a,b,opA:x.accountContext(a).value.activeOperation.operationId,
    opB:x.accountContext(b).value.activeOperation.operationId};
}'''
def read(page):return page.evaluate('''() => {
 const x=JPWForex.state,a=x.accountContext({accountId:'FIN_A',periodId:S.forex.accountContexts.accounts.FIN_A.currentPeriodId}).value,
 b=x.accountContext({accountId:'FIN_B',periodId:S.forex.accountContexts.accounts.FIN_B.currentPeriodId}).value;
 return {a:a.activeOperation?.operationId,b:b.activeOperation?.operationId,
 history:structuredClone(S.operationHistory.records),disk:localStorage.getItem(LSKEY),
 log:structuredClone(S.transitionLog),barrier:jpWealthPersistenceOutcomeIsUnknown()};
}''')
def review(page):
    return page.evaluate('''() => {JPWOperation.openReview();return {
      defenses:!!document.getElementById('finalDefenses'),
      confirm:!!document.getElementById('modalConfirm'),
      text:document.getElementById('modalBox')?.textContent||''};}''')
def click(page,defenses='0',word='FECHADO'):
    return page.evaluate('''({defenses,word}) => {
      const d=document.getElementById('finalDefenses'),w=document.getElementById('finalConfirm');
      if(d&&defenses!==null){d.value=defenses;d.dispatchEvent(new Event('input',{bubbles:true}));}
      if(w){w.value=word;w.dispatchEvent(new Event('input',{bubbles:true}));}
      document.getElementById('modalConfirm')?.click();
      return {error:document.getElementById('finalFail')?.textContent||'',
        open:document.getElementById('modalOverlay')?.className||''};
    }''',{'defenses':defenses,'word':word})
def main():
    server,url=serve();checks=[]
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(**launcher.launch_options());context=browser.new_context(
          viewport={'width':1440,'height':900},service_workers='block');page,errors=launcher.prepare(context,url)
        def seed(kind='closed'):return page.evaluate(SEED,kind)
        def ok(name,condition):assert condition,name;checks.append(name)
        seed('open');before=read(page)
        blocked=page.evaluate('JPWOperation.canFinalize()')
        ok('open position blocks finalization',not blocked['ok'] and blocked['motivo']=='open_position')
        direct=page.evaluate('JPWOperation.finalize({defenseCount:0})')
        ok('domain rejects direct finalization of open position',not direct['ok'])
        ok('open preflight leaves both accounts unchanged',before==read(page))
        seed();before=read(page);r=review(page)
        ok('review presents explicit defense and confirmation fields',r['defenses'] and r['confirm'])
        ok('opening review writes nothing',before==read(page))
        page.evaluate('closeModal()');ok('cancel review writes nothing',before==read(page))
        review(page);click(page,'0','ERRADO')
        ok('wrong confirmation writes nothing',before==read(page))
        page.evaluate('closeModal()');review(page);click(page,None,'FECHADO')
        ok('missing defense count is not implicit zero',before==read(page))
        for invalid in (-1,1.5,'0',''):
            rejected=page.evaluate('(v)=>JPWOperation.finalize({defenseCount:v})',invalid)
            ok(f'invalid defense count {invalid!r} cannot finalize',not rejected['ok'] and before==read(page))
        page.evaluate('closeModal()');review(page)
        stale=page.evaluate('''() => {
          const x=JPWForex.state,s=x.operationalSelection(),p=x.accountContext(s),o=p.value.phases[0].orders[0];
          return x.recordAccountOrders([{pi:0,oi:0,orderId:o.orderId,expectedVersion:o.recordVersion,
            changes:{result:-21}}],{...s,reason:'Correção sintética',expectedRevision:p.revision});
        }''')
        ok('synthetic correction succeeded',stale['ok']);after=read(page)
        attempt=page.evaluate('JPWOperation.finalize({defenseCount:0})')
        ok('stale review blocks finalization',not attempt['ok'] and attempt['motivo']=='review_stale')
        ok('stale review leaves confirmed facts unchanged',after==read(page))
        seed();review(page);page.evaluate("JPWForex.state.selectOperationalAccount('FIN_A')")
        attempt=page.evaluate('JPWOperation.finalize({defenseCount:0})')
        ok('switching account invalidates review',not attempt['ok']);
        ok('switching account creates no history',len(read(page)['history'])==0)
        seed();review(page);before=read(page)
        fail=page.evaluate('''() => {const normal=save;save=()=>false;
          try{return JPWOperation.finalize({defenseCount:0});}finally{save=normal;}}''')
        ok('refused finalization reports failure',not fail['ok'])
        ok('refused finalization rolls back both accounts and history',before==read(page))
        seed('costs');before=read(page);review(page);click(page,'0','FECHADO');after=read(page)
        ok('finalization closes only selected account',after['a']==before['a'] and after['b'] is None)
        ok('one scoped history record exists',len(after['history'])==1 and after['history'][0]['accountId']=='FIN_B')
        ok('separate costs counted exactly once',after['history'][0]['netResult']==-23)
        ok('history identifies selected operation and period',after['history'][0]['operationId']==before['b'] and bool(after['history'][0]['periodId']))
        ok('audit records selected operation once',len([x for x in after['log'] if x.get('operationId')==before['b'] and x.get('fase')=='operação finalizada'])==1)
        double=page.evaluate('JPWOperation.finalize({defenseCount:0})')
        ok('second finalization cannot duplicate history',not double['ok'] and len(read(page)['history'])==1)
        seed();before=read(page);review(page)
        unknown=page.evaluate('''() => {const normal=save;save=()=>undefined;
          try{return JPWOperation.finalize({defenseCount:0});}finally{save=normal;}}''')
        ok('unknown write outcome is not success',not unknown['ok'])
        ok('unknown outcome activates persistence barrier',read(page)['barrier'])
        ok('unknown outcome is absent from last confirmed disk snapshot',read(page)['disk']==before['disk'])
        blind=page.evaluate("JPWForex.state.recordAccountLedger({action:'RECORDED',accountId:'FIN_B',periodId:S.forex.accountContexts.accounts.FIN_B.currentPeriodId,data:'2026-09-03',resultado:0,saldo:null},{reason:'Blind retry'})")
        ok('unknown barrier prevents blind subsequent writer',not blind['ok'])
        ok('no browser page errors',not errors['pageerror'])
        context.close();browser.close()
    finally:server.shutdown()
    print(f'OPERATION FINALIZE TEST PASS — {len(checks)} scoped safety contracts')
if __name__=='__main__':main()

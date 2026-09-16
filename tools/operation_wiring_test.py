#!/usr/bin/env python3
"""Ligação real do Painel Operacional: DOM → rascunho → comando → disco.

O oráculo anterior baseado em S.phases global está preservado como evidência
externa. A suíte atual exercita os controles reais da operação por conta.
Todas as fixtures são sintéticas.
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
SEED='''() => {
  S=structuredClone(DEFAULTS);migrate();S.onboarding.done=true;
  S.accounts=[{forexAccountId:'WIRE_A',nome:'Mestre sintética',tipo:'MESTRE',platformCurrency:'USD'},
    {forexAccountId:'WIRE_B',nome:'Conta B sintética',tipo:'PRÓPRIA',platformCurrency:'USD'}];
  S.forex=JPWForex.state.empty();S.operationHistory={schemaVersion:2,records:[]};
  if(save()!==true)throw Error('Fixture refused');
  const x=JPWForex.state;
  for(const [accountId,si] of [['WIRE_A',10000],['WIRE_B',5000]]){
    const p=x.recordAccountPeriod({accountId,startedAt:'2026-09-01',currency:'USD',si,openingBook:si,
      source:'Fixture sintética',activateCurrentPeriod:true},{reason:'Fixture sintética'});
    if(!p.ok)throw Error(p.error);
  }
  x.selectOperationalAccount('WIRE_A');const scope=x.operationalSelection(),p=x.accountContext(scope).value;
  Object.assign(p.phases[0].orders[0],{id:'A-1',par:'EURUSD',tipo:'BUY',role:'GENESIS',lote:.01,
    entry:1.1,sl:1.09,tp:1.2,costs:0,costBasis:'INCLUDED_IN_RESULT',stopValidated:true});
  if(save()!==true)throw Error('Draft fixture refused');
  navNavigate('forex-operation');execSetView('panel');JPWForex.executionBoardUI.render();
  return {scope,periodB:S.forex.accountContexts.accounts.WIRE_B.currentPeriodId};
}'''
def state(page):return page.evaluate('''() => {
  const x=JPWForex.state,a=x.accountContext({accountId:'WIRE_A',periodId:S.forex.accountContexts.accounts.WIRE_A.currentPeriodId}).value,
    b=x.accountContext({accountId:'WIRE_B',periodId:S.forex.accountContexts.accounts.WIRE_B.currentPeriodId}).value;
  return {a:structuredClone(a.phases[0].orders[0]),aOp:a.activeOperation?.operationId,
    bOp:b.activeOperation?.operationId,disk:localStorage.getItem(LSKEY),view:execGetView(),
    selection:x.operationalSelection().accountId};
}''')
def field(page,key,value,event='change'):
    return page.evaluate('''({key,value,event}) => {
      const node=document.querySelector('#phaseContainer [data-p="0"][data-o="0"][data-f="'+key+'"]');
      if(!node)throw Error('Missing field '+key);
      node.value=value;node.dispatchEvent(new Event(event,{bubbles:true}));
      return {value:node.value,dirty:!!node.closest('[data-eb-row]')?.classList.contains('eb-dirty')};
    }''',{'key':key,'value':value,'event':event})
def save_row(page,reason='Fato sintético'):
    return page.evaluate('''(reason) => {
      const input=document.querySelector('#phaseContainer [data-eb-reason="0:0"]');
      if(input){input.value=reason;input.dispatchEvent(new Event('input',{bubbles:true}));}
      document.querySelector('#phaseContainer [data-eb-save-row="0:0"]').click();
      return {error:document.getElementById('ebError-0-0')?.textContent||'',
        value:document.querySelector('#phaseContainer [data-p="0"][data-o="0"][data-f="status"]')?.value};
    }''',reason)
def fill_birth(page):
    for key,value in [('id','A-1'),('par','EURUSD'),('tipo','BUY'),('role','GENESIS'),
        ('lote','0.01'),('entry','1.1'),('sl','1.09'),('tp','1.2'),('costs','0'),
        ('costBasis','INCLUDED_IN_RESULT')]:
        field(page,key,value,'input' if key in ('id','lote','entry','sl','tp','costs') else 'change')
    page.evaluate('''() => {
      const n=document.querySelector('#phaseContainer [data-p="0"][data-o="0"][data-f="stopValidated"]');
      n.checked=true;n.dispatchEvent(new Event('change',{bubbles:true}));
    }''')
def main():
    server,url=serve();checks=[]
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(**launcher.launch_options());context=browser.new_context(
          viewport={'width':1440,'height':900},service_workers='block');page,errors=launcher.prepare(context,url)
        def seed():return page.evaluate(SEED)
        def ok(name,condition):assert condition,name;checks.append(name)
        seed();before=state(page)
        fill_birth(page)
        options=page.evaluate('''() => [...document.querySelector('#phaseContainer [data-p="0"][data-o="0"][data-f="status"]').options].map(o=>o.value)''')
        ok('real Status select offers open and closed states','Aberta' in options and 'Fechada' in options)
        changed=field(page,'status','Aberta')
        ok('Status event marks draft',changed['dirty'])
        ok('Status event does not persist before Save',state(page)==before)
        page.evaluate("document.querySelector('#phaseContainer [data-eb-cancel-row=\"0:0\"]').click()")
        ok('Cancel restores confirmed row and disk',state(page)==before)
        fill_birth(page);field(page,'status','Aberta');outcome=save_row(page);birth=state(page)
        assert birth['a']['status']=='Aberta' and birth['aOp'],{'outcome':outcome,'birth':birth['a']}
        ok('Save opens factual operation',birth['a']['status']=='Aberta' and bool(birth['aOp']))
        ok('recorded order links account and period',birth['a']['accountId']=='WIRE_A' and bool(birth['a']['periodId']))
        ok('recorded row and operation are durable',birth['aOp'] in birth['disk'])
        ok('other account remains untouched',birth['bOp'] is None)
        page.evaluate('JPWForex.executionBoardUI.render()');after_render=state(page)
        ok('rerender preserves operation and order identity',after_render['aOp']==birth['aOp'] and after_render['a']['orderId']==birth['a']['orderId'])
        field(page,'par','GBPUSD');draft=state(page)
        ok('correction draft is in memory only',draft==after_render)
        save_row(page,'');no_reason=state(page)
        ok('correction without reason refused',no_reason['a']['par']=='EURUSD' and no_reason['a']['recordVersion']==birth['a']['recordVersion'])
        save_row(page,'Correção sintética');corrected=state(page)
        ok('Save correction retains operation identity',corrected['aOp']==birth['aOp'] and corrected['a']['orderId']==birth['a']['orderId'])
        ok('correction has explicit revision and motive',corrected['a']['par']=='GBPUSD' and corrected['a']['recordVersion']==2 and corrected['a']['revisions'][-1]['reason']=='Correção sintética')
        field(page,'result','25','input');field(page,'status','Fechada');pending=state(page)
        ok('closing status/result remains draft until Save',pending==corrected)
        close_outcome=save_row(page,'Fechamento sintético');refused=state(page)
        ok('Save line cannot bypass explicit close flow',bool(close_outcome['error']) and refused==corrected)
        page.evaluate("document.querySelector('#phaseContainer [data-eb-cancel-row=\"0:0\"]').click()")
        page.evaluate("document.querySelector('#phaseContainer [data-eb-close-row=\"0:0\"]').click()")
        modal=page.evaluate("({result,word}) => {document.getElementById('closeResultInput').value=result;document.getElementById('closeConfirmInput').value=word;document.getElementById('modalConfirm').click();return !!document.getElementById('closeResultInput')}",{'result':'25','word':'FECHADO'})
        closed=state(page)
        assert closed['a']['status']=='Fechada' and closed['a']['result']==25,{'modal':modal,'status':closed['a']['status'],'result':closed['a']['result']}
        ok('Save closes row with numeric result',closed['a']['status']=='Fechada' and closed['a']['result']==25)
        ok('closing retains operation identity',closed['aOp']==birth['aOp'])
        page.evaluate("JPWForex.state.selectOperationalAccount('WIRE_B');JPWForex.executionBoardUI.render()")
        other=state(page)
        ok('selection switches to B without changing A facts',other['selection']=='WIRE_B' and other['a']==closed['a'])
        page.evaluate("JPWForex.state.selectOperationalAccount('WIRE_A');JPWForex.executionBoardUI.render()")
        ok('return to A restores the same confirmed row',state(page)['a']==closed['a'])
        page.evaluate("execSetView('accounts')")
        ok('Contas is a local Operation workspace',state(page)['view']=='accounts')
        page.evaluate("execSetView('accounting')")
        ok('Contabilidade is a local Operation workspace',state(page)['view']=='accounting')
        page.evaluate("execSetView('engine')")
        ok('Fator de Correção is a local Operation workspace',state(page)['view']=='engine')
        page.evaluate("execSetView('panel')")
        ok('return to Painel keeps confirmed facts',state(page)['a']==closed['a'])
        ok('browser had no uncaught page errors',not errors['pageerror'])
        context.close();browser.close()
    finally:server.shutdown()
    print(f'OPERATION WIRING TEST PASS — {len(checks)} DOM and context contracts')
if __name__=='__main__':main()

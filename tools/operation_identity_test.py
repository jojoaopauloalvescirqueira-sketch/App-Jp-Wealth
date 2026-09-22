#!/usr/bin/env python3
"""Operação por conta: identidade factual, revisão e continuidade sintéticas.

O oráculo global anterior permanece em evidência externa desta campanha. Ele
invocava operationOnOrderStatus sobre S.phases, caminho substituído pelo escritor
contextual. Este teste verifica a identidade pela escrita e recarga reais.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import threading

import notes_launcher_test as launcher
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*_args):pass

class BrowserFixtureServer(ThreadingHTTPServer):
    request_queue_size=128
    daemon_threads=True

def serve():
    server=BrowserFixtureServer(('127.0.0.1',0),QuietHandler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server,f'http://127.0.0.1:{server.server_port}/index.html'

def main():
    server,url=serve()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launcher.launch_options())
            context=browser.new_context(viewport={'width':1440,'height':900},service_workers='block')
            page,observed=launcher.prepare(context,url)
            assert page.evaluate('DEFAULTS.activeOperation===null'), 'Estado legado inicial criou operação fantasma'
            periods=page.evaluate("""() => {
              S=structuredClone(DEFAULTS);migrate();S.onboarding.done=true;
              S.accounts=[{forexAccountId:'IDENT_A',nome:'Mestre A',tipo:'MESTRE',platformCurrency:'USD'},
                {forexAccountId:'IDENT_B',nome:'Conta B',tipo:'PRÓPRIA',platformCurrency:'USD'}];
              S.forex=JPWForex.state.empty();S.operationHistory={schemaVersion:1,records:[]};
              if(save()!==true)throw Error('Fixture refused');
              for(const [accountId,si] of [['IDENT_A',10000],['IDENT_B',5000]]){
                const r=JPWForex.state.recordAccountPeriod({accountId,startedAt:'2026-09-01',currency:'USD',
                  si,openingBook:si,source:'Fixture de identidade',activateCurrentPeriod:true},
                  {reason:'Fixture sintética de identidade'});
                if(!r.ok)throw Error(r.error);
              }
              navNavigate('forex-operation');execSetView('panel');JPWForex.executionBoardUI.render();
              const a=S.forex.accountContexts.accounts;
              return {a:a.IDENT_A.currentPeriodId,b:a.IDENT_B.currentPeriodId};
            }""")
            assert page.evaluate('JPWForex.state.operationalSelection().accountId')=='IDENT_A'
            birth=page.evaluate("""() => {
              const x=JPWForex.state,scope=x.operationalSelection();
              const result=operationRecordOrder(0,0,{id:'A1',brokerHash:'SYNTHETIC-IDENT-A1',par:'EURUSD',tipo:'BUY',role:'GENESIS',
                lote:.01,entry:1.1,sl:1.09,tp:1.2,status:'Aberta',result:null,
                costs:0,costBasis:'INCLUDED_IN_RESULT',stopValidated:true},{reason:'Primeiro fato sintético'});
              const p=x.accountContext(scope).value,o=p.phases[0].orders[0],disk=JSON.parse(localStorage.getItem(LSKEY));
              return {result,operationId:p.activeOperation?.operationId,orderId:o.orderId,
                linked:o.operationId===p.activeOperation?.operationId&&o.accountId==='IDENT_A'&&o.periodId===scope.periodId,
                recorded:o.recordStatus,version:o.recordVersion,phase:p.activeOperation?.maxAccountPhaseReached??null,
                openedAt:p.activeOperation?.openedAt,global:S.activeOperation,
                persisted:disk.forex.accountContexts.accounts.IDENT_A.periods[scope.periodId].activeOperation?.operationId};
            }""")
            assert birth['result']['ok'] and birth['result']['persistido'] is True,birth
            assert birth['operationId'] and birth['orderId'] and birth['linked'],birth
            assert birth['recorded']=='recorded' and birth['version']==1,birth
            assert birth['phase'] is None and birth['openedAt'] and birth['global'] is None,birth
            assert birth['persisted']==birth['operationId'],birth

            # A linha em edição não escreve. Salvar corrige a mesma identidade.
            page.evaluate('JPWForex.executionBoardUI.render()')
            page.evaluate('document.querySelector("#phaseContainer details[data-phase=\\"0\\"]").open=true')
            before=launcher.snapshot(page)
            page.evaluate('''() => {
              const field=document.querySelector('#phaseContainer [data-p="0"][data-o="0"][data-f="par"]');
              field.value='GBPUSD';field.dispatchEvent(new Event('change',{bubbles:true}));
            }''')
            launcher.unchanged(page,before,'Rascunho de instrumento não foi gravado')
            page.evaluate('''() => {
              const field=document.querySelector('#phaseContainer [data-eb-reason="0:0"]');
              field.value='Correção sintética justificada';field.dispatchEvent(new Event('input',{bubbles:true}));
              document.querySelector('#phaseContainer [data-eb-save-row="0:0"]').click();
            }''')
            corrected=page.evaluate("""() => {
              const p=JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value,o=p.phases[0].orders[0];
              return {operationId:p.activeOperation.operationId,orderId:o.orderId,version:o.recordVersion,
                par:o.par,before:o.revisions[1]?.before?.par,after:o.revisions[1]?.after?.par};
            }""")
            assert corrected=={'operationId':birth['operationId'],'orderId':birth['orderId'],
              'version':2,'par':'GBPUSD','before':'EURUSD','after':'GBPUSD'},corrected

            isolated=page.evaluate("""() => {
              const x=JPWForex.state,a=x.accountContext({accountId:'IDENT_A',periodId:S.forex.accountContexts.accounts.IDENT_A.currentPeriodId}).value;
              x.selectOperationalAccount('IDENT_B');const bScope=x.operationalSelection();
              const r=operationRecordOrder(0,0,{id:'B1',brokerHash:'SYNTHETIC-IDENT-B1',par:'EURUSD',tipo:'BUY',role:'GENESIS',
                lote:.01,entry:1.2,sl:1.1,tp:1.3,status:'Aberta',result:null,costs:0,
                costBasis:'INCLUDED_IN_RESULT',stopValidated:true},{reason:'Fato sintético B'});
              const b=x.accountContext(bScope).value;
              return {result:r,aId:a.activeOperation.operationId,bId:b.activeOperation?.operationId,
                aOrder:a.phases[0].orders[0].orderId,bOrder:b.phases[0].orders[0].orderId,
                aAccount:a.phases[0].orders[0].accountId,bAccount:b.phases[0].orders[0].accountId};
            }""")
            assert isolated['result']['ok'] and isolated['aId']==birth['operationId'],isolated
            assert isolated['bId'] and isolated['bId']!=isolated['aId'],isolated
            assert [isolated['aAccount'],isolated['bAccount']]==['IDENT_A','IDENT_B'],isolated

            revision=page.evaluate("""() => {
              const x=JPWForex.state,scope=x.operationalSelection(),p=x.accountContext(scope);
              const before=JSON.stringify(S.forex.accountContexts);
              const bad=x.recordAccountOrders([{pi:0,oi:0,changes:{par:'USDJPY'}}],{
                accountId:scope.accountId,periodId:scope.periodId,reason:'Revisão obsoleta',expectedRevision:p.revision-1});
              return {bad,unchanged:before===JSON.stringify(S.forex.accountContexts)};
            }""")
            assert not revision['bad']['ok'] and revision['unchanged'],revision

            legacy=page.evaluate("""() => {
              const x=JPWForex.state;x.selectOperationalAccount('IDENT_A');
              S.phases[0].orders[0]={id:'GLOBAL-LEGACY',par:'USDJPY',status:'Aberta'};
              S.activeOperation={operationId:'GLOBAL-OP',openedAt:null};
              const before=x.accountContext(x.operationalSelection()).value.activeOperation.operationId;
              const preview=x.legacyAccountPreview();
              const snap=x.confirmLegacyAccountSnapshot({reason:'Snapshot legado sem vínculo',expectedEpoch:jpWealthPersistenceEpoch()});
              const after=x.accountContext(x.operationalSelection()).value.activeOperation.operationId;
              return {before,after,snap,legacyId:S.forex.accountContexts.legacy?.id,
                globalId:S.activeOperation.operationId,scope:preview.operationScope};
            }""")
            assert legacy['snap']['ok'] and legacy['legacyId'] and legacy['globalId']=='GLOBAL-OP',legacy
            assert legacy['before']==legacy['after']==birth['operationId'],legacy
            assert legacy['scope'] is None,legacy

            page.reload(wait_until='domcontentloaded')
            page.wait_for_timeout(250)
            reload_state=page.evaluate("""() => {
              const x=JPWForex.state,s=x.operationalSelection(),a=x.accountContext(s).value,
                b=x.accountContext({accountId:'IDENT_B',periodId:S.forex.accountContexts.accounts.IDENT_B.currentPeriodId}).value;
              return {selected:s.accountId,a:a.activeOperation?.operationId,b:b.activeOperation?.operationId,
                legacy:S.forex.accountContexts.legacy?.id,global:S.activeOperation?.operationId,
                phase:operationPhaseIdxOrNull(null),zero:operationPhaseIdxOrNull(0)};
            }""")
            assert reload_state['selected']=='IDENT_A' and reload_state['a']==birth['operationId'],reload_state
            assert reload_state['b']==isolated['bId'] and reload_state['legacy']==legacy['legacyId'],reload_state
            assert reload_state['global']=='GLOBAL-OP' and reload_state['phase'] is None and reload_state['zero']==0,reload_state
            assert not observed['pageerror'],observed['pageerror']
            context.close();browser.close()
    finally:server.shutdown()
    print('OPERATION IDENTITY TEST PASS — two accounts, factual birth, correction, legacy separation and reload')

if __name__=='__main__':main()

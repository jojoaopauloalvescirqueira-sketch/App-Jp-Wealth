#!/usr/bin/env python3
"""V11 recordability, factual revisions and persistence barriers (synthetic).

Independent cases use the real document writer and nominal bootstrap. The old
questionnaire/cap oracles are preserved externally in record-before-* evidence.
This suite distinguishes recording facts from normative execution permission.
"""
import argparse
from functools import partial
import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
from playwright.sync_api import sync_playwright
import notes_launcher_test as launcher

ROOT=Path(__file__).resolve().parents[1]
SEED="""() => {
  S.phases=JPWForex.state.newOperationPhases();
  S.phases.forEach(p=>p.orders=emptyOrders(2));
  S.forex=JPWForex.state.empty();S.activeOperation=null;
  S.operationHistory={schemaVersion:1,records:[]};S.cycleRealizado=0;S.transitionLog=[];
  S.phaseUnlocked=[true,false,false,false,false,false];
  window.__alerts=[];window.alert=msg=>__alerts.push(String(msg));window.prompt=()=> 'Correção sintética justificada';window.confirm=()=>true;
  window.__fact=(patch={})=>({id:'FATO',par:'EURUSD',tipo:'BUY',role:'GENESIS',lote:1,entry:1.1,sl:1.09,tp:1.2,result:null,status:'Aberta',costs:-2,costBasis:'SEPARATE_FROM_RESULT',stopValidated:true,...patch});
  if(save()!==true)throw Error('Synthetic setup refused');
  render();renderPhases();navigateToScreen('forex-operation');
}"""

def seed(page):
    page.evaluate(SEED)

def result(page, script):
    return page.evaluate('() => {'+script+'}')

def assert_ok(value):
    assert value['ok'] is True, value

def record_blocked(page):
    r=result(page,"""
      S.quarantine={inicio:'2026-01-01',fim:'2099-01-01',ativa:true};
      S.phaseUnlocked=[true,true,true,true,true,true];
      const before=JPWForex.state.read();
      const a=operationRecordOrder(5,0,__fact({lote:999,sl:0}),{reason:'Fato fora dos limites'});
      const b=operationRecordOrder(0,0,__fact({par:'XAUUSD',tipo:'SELL'}),{reason:'Fato restrito e tese divergente'});
      return {a,b,canRecord:before.canRecord,eligible:before.executionEligibility.status,
        orders:operationLiveOrders().map(x=>x.o),findings:orderComplianceFindings(),unlocked:S.phaseUnlocked};
    """)
    assert_ok(r['a']);assert_ok(r['b'])
    assert r['canRecord'] and r['eligible']=='BLOCKED',r
    assert len(r['orders'])==2 and r['orders'][0]['par']=='XAUUSD',r
    assert r['orders'][1]['lote']==999 and r['orders'][1]['sl']==0,r
    assert {'INSTRUMENT_CONFLICT','DIRECTION_CONFLICT'} <= {x['code'] for x in r['findings']},r
    assert r['unlocked']==[True]*6,r

def render_and_typing(page):
    page.evaluate("() => {S.phases=S.phases.slice(0,4);S.phases[0].orders[0]=__fact();S.phaseUnlocked=[true,true,true,true];save();renderPhases();}")
    before=launcher.snapshot(page)
    page.evaluate('() => {for(let i=0;i<4;i++){render();renderPhases();} }')
    launcher.unchanged(page,before,'render legacy is read-only')
    assert page.locator('#phaseContainer [data-f="par"]:enabled').count()==8
    assert 'LEGACY' in page.locator('#phaseContainer').inner_text()
    page.locator('[data-p="0"][data-o="0"][data-f="id"]').fill('draft in DOM')
    launcher.unchanged(page,before,'typing does not save')
    page.locator('[data-p="0"][data-o="0"][data-f="id"]').blur()
    r=result(page,"return S.phases[0].orders[0];")
    assert r['id']=='draft in DOM' and r['revisions'][0]['before']['id']=='FATO',r
    assert r['policySnapshot']['policyVersion']=='LEGACY_UNRESOLVED',r

def version_and_void(page):
    r=result(page,"""
      const a=operationRecordOrder(0,0,__fact(),{reason:'Registrar execução'}),id=S.phases[0].orders[0].orderId;
      const b=operationRecordOrder(0,0,{lote:2},{reason:'Corrigir volume executado'});
      const c=operationVoidOrder(0,0,'Duplicidade identificada');
      const order=structuredClone(S.phases[0].orders[0]);const count=S.phases[0].orders.length;
      const d=operationRecordOrder(0,0,{lote:3},{reason:'Não pode reescrever anulação'});
      return {a,b,c,d,id,order,count,live:operationLiveOrders().length,ready:operationCanFinalize(),preflight:operationPreflight()};
    """)
    for k in ('a','b','c'):assert_ok(r[k])
    assert not r['d']['ok'] and r['count']==2 and r['live']==1,r
    o=r['order'];assert o['orderId']==r['id'] and o['recordVersion']==3 and o['recordStatus']=='voided',r
    assert o['revisions'][1]['before']['lote']==1 and o['revisions'][1]['after']['lote']==2,r
    assert o['revisions'][2]['before']['recordStatus']=='recorded' and o['voidReason']=='Duplicidade identificada',r
    assert r['ready']['ok'] and r['preflight']['estado']=='ready',r

def draft_delete(page):
    r=result(page,"const before=S.phases[0].orders.length;const a=operationAddDraft(0);const id=S.phases[0].orders.at(-1).orderId;const b=operationVoidOrder(0,before,'Rascunho descartado');return {a,b,before,after:S.phases[0].orders.length,id,active:S.activeOperation};")
    assert_ok(r['a']);assert_ok(r['b']);assert r['id'] and r['before']==r['after'] and r['active'] is None,r

def malformed_refused(page):
    before=launcher.snapshot(page)
    r=result(page,"return [operationRecordOrder(0,0,__fact({lote:-1}),{reason:'inválida'}),operationRecordOrder(0,0,__fact({status:'Fechada',result:null}),{reason:'ausente'}),operationRecordOrder(0,0,__fact({par:''}),{reason:'ausente'}),operationRecordOrder(0,0,__fact({costs:NaN}),{reason:'inválida'})];")
    assert all(not x['ok'] for x in r),r
    launcher.unchanged(page,before,'structural validation refuses without writes')

def planning_percent_display(page):
    before=launcher.snapshot(page)
    page.evaluate('() => renderParams()')
    assert page.locator('#rpRefM').inner_text()=='3,50%'
    assert page.locator('#rpRefA').inner_text()=='35,00%–40,00%'
    launcher.unchanged(page,before,'planning percentage presentation is read-only')

def unsupported_schema_read_only(page):
    page.evaluate('() => {S.forex.schemaVersion=99;}')
    before=launcher.snapshot(page)
    page.evaluate('() => renderPhases()')
    text=page.locator('#phaseContainer').inner_text()
    assert 'Registro indisponível: versão de dados incompatível.' in text
    assert 'SOMENTE LEITURA' in text and 'REGISTRO DISPONÍVEL' not in text
    refused=result(page,"return operationAddDraft(0);")
    assert refused['ok'] is False and refused['persistido'] is False,refused
    launcher.unchanged(page,before,'unsupported schema render and record refusal preserve all data')

def close_zero_and_refusal(page):
    assert_ok(result(page,"return operationRecordOrder(0,0,__fact(),{reason:'Execução'});"))
    page.evaluate('() => openCloseOrderModal(0,0)')
    page.locator('#closeConfirmInput').fill('FECHADO');page.locator('#modalConfirm').click()
    assert page.locator('[data-qid="resultado"] .modal-err').evaluate('e=>e.classList.contains("show")')
    page.locator('#closeResultInput').fill('0')
    page.evaluate('() => {window.__realSave=save;save=()=>false;}')
    before=result(page,'return JSON.stringify(S);')
    page.locator('#modalConfirm').click()
    assert result(page,'return JSON.stringify(S);')==before
    assert page.locator('#closeResultInput').input_value()=='0'
    page.evaluate('() => {save=__realSave;}');page.locator('#modalConfirm').click()
    r=result(page,'return S.phases[0].orders[0];')
    assert r['status']=='Fechada' and r['result']==0 and r['recordVersion']==2,r

def mutation_refusal_retry(page):
    r=result(page,"""
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),real=save;
      save=()=>false;const a=operationRecordOrder(0,0,__fact(),{reason:'Registro'});
      const after=JSON.stringify(S),afterRaw=localStorage.getItem(LSKEY);save=real;
      const b=operationRecordOrder(0,0,__fact(),{reason:'Registro'});
      return {a,b,unchanged:before===after,rawSame:raw===afterRaw,version:S.phases[0].orders[0].recordVersion};
    """)
    assert not r['a']['ok'] and r['unchanged'] and r['rawSame'],r
    assert_ok(r['b']);assert r['version']==1,r

def unknown_barrier(page):
    r=result(page,"""
      const real=save;save=()=>{throw Error('synthetic uncertain writer');};
      const a=operationRecordOrder(0,0,__fact(),{reason:'Registro incerto'});save=real;
      const candidate=JSON.stringify(S),writes=__notesLauncherWrites.length;
      const b=operationRecordOrder(0,1,__fact(),{reason:'Nova tentativa proibida'});
      return {a,b,unknown:jpWealthPersistenceOutcomeIsUnknown(),unchanged:candidate===JSON.stringify(S),noWrite:writes===__notesLauncherWrites.length};
    """)
    assert not r['a']['ok'] and r['a']['persistido'] is None and not r['b']['ok'],r
    assert r['unknown'] and r['unchanged'] and r['noWrite'],r

def context_and_extensions(page):
    r=result(page,"""
      S.phases[0].orders[0]={...__fact(),customExtension:{keep:['synthetic']}};
      const a=operationRecordOrder(0,0,{result:10,status:'Fechada'},{reason:'Fechamento legado'});
      const o=S.phases[0].orders[0],id=o.orderId,policy=JSON.stringify(o.policySnapshot),version=o.recordVersion;
      renderPhases();renderPhases();const b=operationRecordOrder(0,0,{result:12},{reason:'Correção de resultado'});
      return {a,b,o:S.phases[0].orders[0],id,policy,version};
    """)
    assert_ok(r['a']);assert_ok(r['b']);o=r['o']
    assert o['orderId']==r['id'] and o['policySnapshot']['policyVersion']=='LEGACY_UNRESOLVED',r
    assert o['customExtension']=={'keep':['synthetic']} and len(o['revisions'])==2,r
    assert o['revisions'][0]['context']['status']=='NOT_COMPUTABLE' and o['revisions'][0]['context']['accountInputs'] is None,r
    assert o['revisions'][1]['before']['result']==10,r

def pending_and_costs(page):
    r=result(page,"""
      const a=operationRecordOrder(0,0,__fact({status:'Pendente',pendingActive:true,amplifiesExposure:true,costs:-5}),{reason:'Pendente ampliadora'});
      const o=S.phases[0].orders[0],input=JPWForex.orderInputs(o,{currency:'USD'}),before=operationCanFinalize();
      const b=operationVoidOrder(0,0,'Pendente cancelada');return {a,b,input,before,after:operationCanFinalize(),o};
    """)
    assert_ok(r['a']);assert_ok(r['b']);assert r['input']['active'] and r['input']['kind']=='AMPLIFYING' and r['input']['stopValid'],r
    assert not r['before']['ok'] and r['after']['ok'] and r['o']['costs']==-5,r

def conflicted_finalization(page):
    r=result(page,"""
      JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity:10000,netCashflow:0,currency:'USD',source:'synthetic thesis context',observedAt:'2026-09-12T00:00:00Z'},{reason:'Conta observada antes dos fatos'});
      operationRecordOrder(0,0,__fact({status:'Fechada',result:50}),{reason:'Fechamento A'});
      operationRecordOrder(1,0,__fact({status:'Fechada',result:-20,par:'GBPUSD',tipo:'SELL'}),{reason:'Fechamento divergente'});
      S.activeOperation.openedAt='2026-01-01T12:00:00.000Z';S.activeOperation.openedAtSource='manual_legacy';
      const ids=operationLiveOrders().map(x=>x.o.orderId),a=finalizeOperation({defenseCount:0});
      return {a,ids,phases:S.phases.length,orders:operationLiveOrders().length,history:S.operationHistory.records.length,cycle:S.cycleRealizado};
    """)
    assert_ok(r['a']);h=r['a']['record'];assert r['phases']==6 and r['orders']==0 and r['history']==1 and r['cycle']==0,r
    assert h['netResult']==30 and h['resultConsolidation']=='CONTEXTUAL_HISTORY',r
    assert h['instrument'] is None and h['direction'] is None and len(h['complianceFindings'])==2,r
    assert [o['orderId'] for o in h['ordersSnapshot']]==r['ids'],r
    assert all(o['revisions'] for o in h['ordersSnapshot']) and h['recordContext']['statuteVersion']=='V11',r
    assert h['finalizationContext']['status']=='OK' and h['currency']=='USD',r

def legacy_finalization(page):
    r=result(page,"""
      S.phases=S.phases.slice(0,4);S.phases[2].orders[1]=__fact({status:'Fechada',result:17});
      S.activeOperation={operationId:'legacy_synthetic_stable',openedAt:'2026-01-01T12:00:00.000Z',openedAtSource:'manual_legacy',adoptedLegacyAt:'2026-01-02T00:00:00.000Z',maxAccountPhaseReached:null};
      const before=JSON.stringify(S),review=operationBuildSnapshot(S.activeOperation,{defenseCount:0}).record;
      const readOnly=before===JSON.stringify(S),a=finalizeOperation({defenseCount:0});
      return {a,review,readOnly,phases:S.phases.length};
    """)
    assert_ok(r['a']);h=r['a']['record'];assert r['readOnly'] and r['phases']==6,r
    assert h['policySnapshot']['policyVersion']=='LEGACY_UNRESOLVED' and h['maxGridPhaseReached'] is None,r
    assert h['ordersSnapshot'][0]['orderId']==r['review']['ordersSnapshot'][0]['orderId'],r
    assert h['ordersSnapshot'][0]['phase']==3 and h['ordersSnapshot'][0]['gridIndex']==1,r

def captured_reference_balance(page):
    r=result(page,"""
      const observe=(si,newPeriod)=>JPWForex.state.recordAccountFacts({accountIndex:0,si,equity:si,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',source:'synthetic-account',observedAt:'2026-09-14T12:00:00Z',newPeriod},{reason:'Observação explícita'});
      const account=observe(10000,false),order=operationRecordOrder(0,0,__fact({status:'Fechada',result:50}),{reason:'Fato confirmado'});
      const captured=structuredClone(S.activeOperation.recordContext),changed=observe(20000,true);
      const finalized=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});
      return {account,order,changed,captured,finalized};
    """)
    for key in ('account','order','changed','finalized'):assert_ok(r[key])
    h=r['finalized']['record']
    assert h['referenceBalance']==10000 and h['referenceBalanceType']=='account_si_at_first_record',r
    assert h['referenceBalanceProvenance']=='CAPTURED_ACCOUNT_OBSERVATION' and h['finalizationContext']['accountInputs']['si']==10000,r
    assert h['recordContext']['periodId']==h['finalizationContext']['periodId']==r['captured']['periodId'],r
    assert h['ordersSnapshot'][0]['revisions'][0]['context']['accountInputs']['si']==10000,r

def unknown_reference_never_backfilled(page):
    r=result(page,"""
      const order=operationRecordOrder(0,0,__fact({status:'Fechada',result:5}),{reason:'Fato sem conta conciliada'});
      const account=JPWForex.state.recordAccountFacts({accountIndex:0,si:20000,equity:20000,netCashflow:0,currency:'USD',source:'synthetic-account',observedAt:'2026-09-14T12:00:00Z'},{reason:'Observação posterior'});
      const before=JSON.stringify(S),finalized=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});return {order,account,finalized,unchanged:before===JSON.stringify(S),op:S.activeOperation,orders:operationLiveOrders().map(x=>x.o),history:S.operationHistory.records.length};
    """)
    for key in ('order','account'):assert_ok(r[key])
    assert not r['finalized']['ok'] and r['finalized']['motivo']=='monetary_context_missing',r
    assert r['unchanged'] and r['history']==0 and r['op']['recordContext']['accountInputs'] is None,r
    assert r['orders'][0].get('accountId') is None,r
    before=launcher.snapshot(page);page.evaluate('() => openFinalizeOperationModal()')
    assert 'a conta selecionada não preenche vínculos históricos ausentes' in page.locator('#modalBox').inner_text()
    launcher.unchanged(page,before,'missing monetary context explains refusal without changing facts')

def account_period_scoped_finalization(page):
    r=result(page,"""
      const observe=(index,si,equity,currency='USD')=>JPWForex.state.recordAccountFacts({accountIndex:index,si,equity,netCashflow:0,cashflowAdjustmentRecorded:true,currency,usdToAccountRate:0.9,source:'synthetic account context',observedAt:'2026-09-14T12:00:00Z'},{reason:'Observação explícita'});
      const a=observe(0,10000,10000),birth=operationRecordOrder(0,0,__fact({status:'Fechada',result:5}),{reason:'Fato na conta A'});
      const captured=structuredClone(S.activeOperation.recordContext);
      S.accounts.push({nome:'Synthetic account B',tipo:'MESTRE'});
      const b=observe(S.accounts.length-1,20000,17000,'EUR');
      const continuation=operationRecordOrder(1,0,__fact({role:'DEFENSE',status:'Fechada',result:7}),{reason:'Continuação da operação A'});
      S.activeOperation.openedAt='2026-01-01T00:00:00Z';S.activeOperation.openedAtSource='manual_legacy';
      const liveMax=S.activeOperation.maxAccountPhaseReached,selected=S.forex.activeAccountId;
      const before=JSON.stringify(S);openFinalizeOperationModal();
      const preview=operationFinalizeReview.op.maxAccountPhaseReached,readonly=before===JSON.stringify(S);
      const finalized=finalizeOperation({defenseCount:0});
      return {a,b,birth,continuation,captured,selected,liveMax,preview,readonly,finalized};
    """)
    for key in ('a','b','birth','continuation','finalized'):assert_ok(r[key])
    h=r['finalized']['record'];ctx=h['finalizationContext']
    assert r['selected']!=r['captured']['accountId'] and r['readonly'],r
    assert ctx['accountId']==r['captured']['accountId'] and ctx['periodId']==r['captured']['periodId'],r
    assert ctx['accountInputs']['currency']=='USD' and ctx['accountInputs']['si']==10000,r
    assert r['liveMax']==r['preview']==h['maxAccountPhaseReached']==0,r
    assert all(o['accountId']==ctx['accountId'] and o['periodId']==ctx['periodId'] and o['currency']=='USD' for o in h['ordersSnapshot']),r

def factual_input_versioning(page):
    r=result(page,"""
      const account=JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity:10000,netCashflow:0,currency:'USD',source:'synthetic conversion',observedAt:'2026-09-14T12:00:00Z'},{reason:'Observação explícita'});
      const ins=instFor('USDJPY');ins.preco=100;ins.cpl=100000;
      const birth=operationRecordOrder(0,0,__fact({par:'USDJPY',entry:110,sl:109,status:'Fechada',result:5}),{reason:'Fato e cotação observados'});
      const original=structuredClone(S.phases[0].orders[0]),context=structuredClone(S.activeOperation.recordContext);
      ins.preco=200;ins.cpl=10000;
      const corrected=operationRecordOrder(0,0,{result:6},{reason:'Correção registrada em outro instante'});
      const revised=structuredClone(S.phases[0].orders[0]);ins.preco=400;ins.cpl=5000;
      renderPhases();const same=JSON.stringify(revised)===JSON.stringify(S.phases[0].orders[0]);
      const finalized=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});
      return {account,birth,corrected,original,revised,context,same,finalized};
    """)
    for key in ('account','birth','corrected','finalized'):assert_ok(r[key])
    old=r['original']['calculationInputs'];new=r['revised']['calculationInputs'];h=r['finalized']['record']['ordersSnapshot'][0]
    assert r['same'] and old['conversionRate']==0.01 and old['contractSize']==100000,r
    assert new['conversionRate']==0.005 and new['contractSize']==10000,r
    assert old['provenance']==new['provenance']=='OBSERVED_AT_RECORDING',r
    assert old['currency']=='USD' and old['accountId']==r['context']['accountId'] and old['periodId']==r['context']['periodId'],r
    assert h['revisions'][0]['after']['calculationInputs']==old and h['revisions'][1]['before']['calculationInputs']==old,r
    assert h['calculationInputs']==new and h['revisions'][1]['after']['calculationInputs']==new,r

def unresolved_period_never_selected_fallback(page):
    r=result(page,"""
      const account=JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity:8400,netCashflow:0,currency:'USD',source:'synthetic scope',observedAt:'2026-09-14T12:00:00Z'},{reason:'Observação explícita'});
      const birth=operationRecordOrder(0,0,__fact({status:'Fechada',result:5}),{reason:'Fato confirmado'});
      S.activeOperation.recordContext.periodId='synthetic-unresolved-period';S.activeOperation.maxAccountPhaseReached=null;
      const original=JSON.stringify(S),review=operationCaptureReview(S.activeOperation),snapshot=operationBuildSnapshot(review,{defenseCount:0});
      return {account,birth,unchanged:original===JSON.stringify(S),review,snapshot};
    """)
    assert_ok(r['account']);assert_ok(r['birth'])
    assert r['unchanged'] and r['review']['maxAccountPhaseReached'] is None,r
    assert not r['snapshot']['ok'] and r['snapshot']['motivo']=='monetary_context_conflict',r

def account_observation_captures_peak(page):
    r=result(page,"""
      const observe=(equity,at)=>JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity,netCashflow:0,currency:'USD',source:'synthetic phase observation',observedAt:at},{reason:'Equity confirmada'});
      const birthAccount=observe(10000,'2026-09-12T00:00:00Z');
      const birthOrder=operationRecordOrder(0,0,__fact({status:'Fechada',result:5}),{reason:'Operação A'});
      const peak=observe(8000,'2026-09-12T04:00:00Z'),maxAtPeak=S.activeOperation.maxAccountPhaseReached;
      const h4a=JPWForex.state.recordH4({ddPercent:0,closedAt:'2026-09-12T08:00:00Z',source:'synthetic candle'},{reason:'Fechamento H4 confirmado'});
      const h4b=JPWForex.state.recordH4({ddPercent:0,closedAt:'2026-09-12T12:00:00Z',source:'synthetic candle'},{reason:'Fechamento H4 confirmado'});
      const recovered=observe(10000,'2026-09-12T16:00:00Z');
      const current=JPWForex.state.read().accountPhase.value,maxAfterRecovery=S.activeOperation.maxAccountPhaseReached;
      const finalized=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});
      return {birthAccount,birthOrder,peak,h4a,h4b,recovered,maxAtPeak,current,maxAfterRecovery,finalized};
    """)
    for key in ('birthAccount','birthOrder','peak','h4a','h4b','recovered','finalized'):assert_ok(r[key])
    assert r['current']==1 and r['maxAtPeak']==r['maxAfterRecovery']==r['finalized']['record']['maxAccountPhaseReached']==5,r

def account_peak_refusal_retry(page):
    r=result(page,"""
      const observe=equity=>JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity,netCashflow:0,currency:'USD',source:'synthetic phase observation',observedAt:'2026-09-12T00:00:00Z'},{reason:'Equity confirmada'});
      observe(10000);operationRecordOrder(0,0,__fact(),{reason:'Operação A'});
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),real=window.save;window.save=()=>false;
      const refused=observe(8000);window.save=real;
      const rollback=before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY),retry=observe(8000);
      return {refused,rollback,retry,max:S.activeOperation.maxAccountPhaseReached};
    """)
    assert not r['refused']['ok'] and r['refused']['persistido'] is False and r['rollback'],r
    assert_ok(r['retry']);assert r['max']==5,r

def account_peak_unknown(page):
    r=result(page,"""
      const observe=equity=>JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity,netCashflow:0,currency:'USD',source:'synthetic phase observation',observedAt:'2026-09-12T00:00:00Z'},{reason:'Equity confirmada'});
      observe(10000);operationRecordOrder(0,0,__fact(),{reason:'Operação A'});
      const real=window.save;window.save=()=>{throw Error('synthetic unknown outcome');};
      const unknown=observe(8000);window.save=real;
      const candidate=JSON.stringify(S),writes=__notesLauncherWrites.length,retry=observe(10000);
      return {unknown,retry,max:S.activeOperation.maxAccountPhaseReached,blocked:jpWealthPersistenceOutcomeIsUnknown(),same:candidate===JSON.stringify(S),noWrite:writes===__notesLauncherWrites.length};
    """)
    assert not r['unknown']['ok'] and r['unknown']['persistido'] is None and r['blocked'],r
    assert r['max']==5 and r['same'] and r['noWrite'] and not r['retry']['ok'],r

def v11_result_does_not_mix_legacy_cycle(page):
    r=result(page,"""
      S.cycleRealizado=123;
      const account=JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity:10000,netCashflow:0,currency:'BRL',usdToAccountRate:5,source:'synthetic currency scope',observedAt:'2026-09-12T00:00:00Z'},{reason:'Conta BRL observada'});
      const birth=operationRecordOrder(0,0,__fact({status:'Fechada',result:100}),{reason:'Resultado BRL'});
      const finalized=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});
      return {account,birth,finalized,legacyCycle:S.cycleRealizado,history:S.operationHistory.records.length};
    """)
    for key in ('account','birth','finalized'):assert_ok(r[key])
    h=r['finalized']['record']
    assert r['legacyCycle']==123 and r['history']==1 and h['netResult']==100,r
    assert h['currency']=='BRL' and h['accountId']==h['recordContext']['accountId'] and h['periodId']==h['recordContext']['periodId'],r

def migrated_reference_identity(page):
    r=result(page,"""
      const first=operationRecordOrder(0,0,__fact({status:'Migrada'}),{reason:'Referência do espelho legado'});
      const op=structuredClone(S.activeOperation),count=JPWForex.state.read().orders.raw.length;
      const actual=operationRecordOrder(1,0,__fact({status:'Fechada',result:17}),{reason:'Fechamento do fato efetivo'});
      const finalized=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});
      return {first,op,count,actual,finalized};
    """)
    for key in ('first','actual','finalized'):assert_ok(r[key])
    assert r['op']['operationId'] and r['op']['openedAt'] is None and r['op']['policySnapshot']['policyVersion']=='LEGACY_UNRESOLVED',r
    assert r['count']==0 and r['finalized']['record']['netResult']==17,r
    assert [o['status'] for o in r['finalized']['record']['ordersSnapshot']]==['Migrada','Fechada'],r

def roles_and_currency_labels(page):
    r=result(page,"""
      const known={accountId:'synthetic-a',periodId:'synthetic-p',currency:'USD'};
      S.phases[0].orders[0]={...__fact({role:'DEFENSE',status:'Fechada',result:100}),...known};
      S.phases[0].orders[1]={...__fact({role:'GENESIS',status:'Fechada',result:100}),...known,currency:'BRL'};
      renderPhases();const mixed=phasePositiveResults(0).text;
      const roles=[operationOrderLabel(0,0,S.phases[0].orders[0]),operationOrderLabel(0,1,S.phases[0].orders[1])];
      S.phases[0].orders[0].currency='BRL';renderPhasesLite(0);
      return {mixed,roles,total:document.querySelector('.phase[data-phase="0"] .lucro-sum').textContent,html:document.getElementById('phaseContainer').innerText};
    """)
    assert r['roles'][0].startswith('DEFESA') and r['roles'][1].startswith('GÊNESE'),r
    assert r['mixed']=='Não consolidado: conta, período ou moeda não conciliados',r
    assert 'R$' in r['total'] and '200,00' in r['total'] and 'Resultados positivos registrados' in r['html'],r
    assert 'Lucro técnico realizado' not in r['html'] and 'Risco na moeda da ordem' in r['html'],r

def order_risk_keeps_recorded_currency(page):
    r=result(page,"""
      const observe=(index,currency,rate)=>JPWForex.state.recordAccountFacts({accountIndex:index,si:10000,equity:10000,netCashflow:0,currency,usdToAccountRate:rate,source:'synthetic risk currency',observedAt:'2026-09-12T00:00:00Z'},{reason:'Conta explicitamente observada'});
      const account=observe(0,'BRL',5);instFor('EURUSD').preco=1.1;instFor('EURUSD').cpl=100000;
      const birth=operationRecordOrder(0,0,__fact(),{reason:'Fato da conta BRL'}),before=orderRisk(S.phases[0].orders[0]);
      S.accounts.push({nome:'Synthetic USD B',tipo:'MESTRE'});const other=observe(S.accounts.length-1,'USD',1);
      const after=orderRisk(S.phases[0].orders[0]);renderPhases();
      return {account,birth,other,before,after,text:document.querySelector('.phase[data-phase="0"] tbody tr .calc.neg').textContent};
    """)
    for key in ('account','birth','other'):assert_ok(r[key])
    assert abs(r['before']-5000)<0.001 and abs(r['after']-5000)<0.001,r
    assert 'R$' in r['text'] and '5.000' in r['text'],r

def mixed_context_cannot_finalize_as_one_currency(page):
    r=result(page,"""
      const account=JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity:10000,netCashflow:0,currency:'USD',source:'synthetic mixed import',observedAt:'2026-09-12T00:00:00Z'},{reason:'Conta USD observada'});
      const birth=operationRecordOrder(0,0,__fact({status:'Fechada',result:100}),{reason:'Fato USD'});
      S.phases[1].orders[0]={...structuredClone(S.phases[0].orders[0]),orderId:'synthetic-other-fact',currency:'BRL',accountId:'synthetic-other-account',periodId:'synthetic-other-period'};
      save();const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY);
      const finalized=finalizeOperation({defenseCount:0,openedAtManual:'2026-01-01T00:00:00Z'});
      return {account,birth,finalized:{ok:finalized.ok,motivo:finalized.motivo,net:finalized.record?.netResult,currency:finalized.record?.currency},
        unchanged:before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY),count:operationLiveOrders().length,history:S.operationHistory.records.length};
    """)
    assert_ok(r['account']);assert_ok(r['birth'])
    assert not r['finalized']['ok'] and r['finalized']['motivo']=='monetary_context_conflict',r
    assert r['unchanged'] and r['count']==2 and r['history']==0,r

def legacy_explicit_mixed_currency_refused(page):
    r=result(page,"""
      S.phases=S.phases.slice(0,4);
      S.phases[0].orders[0]=__fact({status:'Fechada',result:100,currency:'USD'});
      S.phases[1].orders[0]=__fact({status:'Fechada',result:100,currency:'BRL'});
      S.activeOperation={operationId:'synthetic-legacy-mixed',openedAt:'2026-01-01T00:00:00Z',openedAtSource:'manual_legacy',policySnapshot:{policyVersion:'LEGACY_UNRESOLVED'}};
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),a=finalizeOperation({defenseCount:0});
      return {a,same:before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY),count:operationLiveOrders().length};
    """)
    assert not r['a']['ok'] and r['a']['motivo']=='monetary_context_conflict' and r['same'] and r['count']==2,r

def orphan_context_does_not_bind_new_operation(page):
    r=result(page,"""
      const observe=(index,currency,rate)=>JPWForex.state.recordAccountFacts({accountIndex:index,si:10000,equity:10000,netCashflow:0,currency,usdToAccountRate:rate,source:'synthetic orphan context',observedAt:'2026-09-12T00:00:00Z'},{reason:'Conta observada'});
      observe(0,'USD',1);operationRecordOrder(0,0,__fact(),{reason:'Operação A original'});
      const a=structuredClone(S.activeOperation.recordContext);S.activeOperation.operationId='synthetic-orphan-a';
      S.phases.forEach(p=>p.orders=emptyOrders(2));
      S.accounts.push({nome:'Synthetic B',tipo:'MESTRE'});observe(S.accounts.length-1,'BRL',5);
      const selected=S.forex.activeAccountId,recorded=operationRecordOrder(0,0,__fact(),{reason:'Nova operação B'});
      const newborn={id:S.activeOperation.operationId,accountId:S.activeOperation.recordContext.accountId,orderAccountId:S.phases[0].orders[0].accountId};
      S.phases.forEach(p=>p.orders=emptyOrders(2));
      S.activeOperation={operationId:'synthetic-adopted-a',recordContext:a,adoptedLegacyAt:'2026-09-12T00:00:00Z',policySnapshot:{policyVersion:'LEGACY_UNRESOLVED'}};
      const adoptedRecord=operationRecordOrder(0,0,__fact(),{reason:'Fato na entidade adotada'});
      return {recorded,newborn,selected,a:a.accountId,adoptedRecord,adopted:{id:S.activeOperation.operationId,accountId:S.phases[0].orders[0].accountId}};
    """)
    assert_ok(r['recorded']);assert_ok(r['adoptedRecord'])
    assert r['newborn']['id']!='synthetic-orphan-a' and r['newborn']['accountId']==r['newborn']['orderAccountId']==r['selected']!=r['a'],r
    assert r['adopted']['id']=='synthetic-adopted-a' and r['adopted']['accountId']==r['a'],r

def prepare_budget(page,declare=True):
    r=result(page,"""
      const account=JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity:10000,netCashflow:0,currency:'USD',source:'synthetic budget account',observedAt:'2026-09-12T00:00:00Z'},{reason:'Conta observada'});
      const c=JPWForex.state.recordContext();
      window.__budgetScope={accountId:c.accountId,periodId:c.periodId,currency:'USD',operationId:null};
      window.__declareBudget=(extra={})=>JPWForex.state.recordOperationBudget({...__budgetScope,amount:500,source:'synthetic signed declaration',declaredBy:'Synthetic manager',declaredAt:'2026-09-12T04:00:00Z',...extra},{reason:'Declaração explícita'});
      return {account};
    """)
    assert_ok(r['account'])
    if declare:assert_ok(result(page,'return __declareBudget();'))

def first_record_attaches_budget(page):
    prepare_budget(page)
    r=result(page,"""
      const recorded=operationRecordOrder(0,0,__fact(),{reason:'Primeiro fato confirmado'});
      const o=S.phases[0].orders[0],c=S.activeOperation.recordContext;
      return {recorded,opId:S.activeOperation.operationId,order:o,budget:c.operationBudgetSnapshot,rows:S.forex.operationBudgets};
    """)
    assert_ok(r['recorded']);b=r['budget'];o=r['order']
    assert b['status']=='OK' and b['value']==500 and b['currency']=='USD' and len(r['rows'])==1,r
    assert b['declaration']['operationId']==o['operationId']==r['opId'],r
    assert b['declaration']['association']['firstRecordedAt']==o['revisions'][0]['recordedAt'],r
    assert b['declaration']['association']['doesNotProveExternalPreExecution'] is True,r
    assert b['declaration']['versions'][0]['recordingTiming']=='BEFORE_FIRST_SOFTWARE_RECORD',r
    assert o['operationBudgetSnapshot']==o['revisions'][0]['context']['operationBudgetSnapshot']==b,r

def budget_attachment_refusal_retry(page):
    prepare_budget(page)
    r=result(page,"""
      const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),real=window.save;window.save=()=>false;
      const refused=operationRecordOrder(0,0,__fact(),{reason:'Primeiro fato recusado'});window.save=real;
      const rollback=before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY),unbound=S.forex.operationBudgets[0].operationId;
      const retried=operationRecordOrder(0,0,__fact(),{reason:'Repetição confirmada'});
      return {refused,rollback,unbound,retried,opId:S.activeOperation.operationId,budgets:S.forex.operationBudgets};
    """)
    assert not r['refused']['ok'] and r['refused']['persistido'] is False and r['rollback'] and r['unbound'] is None,r
    assert_ok(r['retried']);assert len(r['budgets'])==1 and r['budgets'][0]['operationId']==r['opId'],r

def budget_attachment_unknown(page):
    prepare_budget(page)
    r=result(page,"""
      const real=window.save;window.save=()=>{throw Error('synthetic unknown');};
      const unknown=operationRecordOrder(0,0,__fact(),{reason:'Primeiro fato indeterminado'});window.save=real;
      const candidate=JSON.stringify(S),writes=__notesLauncherWrites.length,retry=operationRecordOrder(0,0,{lote:2},{reason:'Não repetir candidato indeterminado'});
      return {unknown,retry,same:candidate===JSON.stringify(S),noWrite:writes===__notesLauncherWrites.length,opId:S.activeOperation.operationId,budget:S.forex.operationBudgets[0],blocked:jpWealthPersistenceOutcomeIsUnknown()};
    """)
    assert not r['unknown']['ok'] and r['unknown']['persistido'] is None and r['blocked'],r
    assert not r['retry']['ok'] and r['same'] and r['noWrite'] and r['budget']['operationId']==r['opId'],r

def later_budget_does_not_backfill_first_snapshot(page):
    prepare_budget(page,declare=False)
    r=result(page,"""
      const first=operationRecordOrder(0,0,__fact(),{reason:'Fato sem declaração anterior'}),op=S.activeOperation;
      const original=structuredClone(op.recordContext.operationBudgetSnapshot);
      const declaration=__declareBudget({operationId:op.operationId});
      const correction=operationRecordOrder(0,0,{lote:0.5},{reason:'Fato corrigido após declaração'});
      return {first,declaration,correction,original,birth:S.activeOperation.recordContext.operationBudgetSnapshot,current:S.phases[0].orders[0].operationBudgetSnapshot,firstRevision:S.phases[0].orders[0].revisions[0].context.operationBudgetSnapshot};
    """)
    for key in ('first','declaration','correction'):assert_ok(r[key])
    assert r['original']['status']=='NOT_COMPUTABLE' and r['original']==r['birth']==r['firstRevision'],r
    assert r['current']['value']==500 and r['current']['declaration']['versions'][0]['recordingTiming']=='RETROSPECTIVE_DECLARATION',r
    assert r['current']['declaration']['versions'][0]['doesNotProveExternalPreExecution'] is True,r


def prepare_review_observation(page):
    r=result(page,"""
      const account=JPWForex.state.recordAccountFacts({accountIndex:0,si:10000,equity:9100,netCashflow:0,currency:'USD',source:'synthetic',observedAt:'2026-09-14T12:00:00Z'},{reason:'Equity confirmada'});
      const order=operationRecordOrder(0,0,__fact({status:'Fechada',result:5}),{reason:'Fechamento'});
      S.activeOperation.maxAccountPhaseReached=null;delete S.activeOperation.phaseCaptureFault;
      S.activeOperation.openedAt='2026-01-01T00:00:00Z';S.activeOperation.openedAtSource='manual_legacy';save();
      return {account,order};
    """)
    assert_ok(r['account']);assert_ok(r['order'])

def review_cancel_no_capture(page):
    prepare_review_observation(page)
    before=launcher.snapshot(page)
    page.evaluate('() => openFinalizeOperationModal()')
    r=result(page,'return {live:S.activeOperation.maxAccountPhaseReached,preview:operationFinalizeReview.op.maxAccountPhaseReached};')
    assert r['live'] is None and r['preview']==2,r
    launcher.unchanged(page,before,'opening review cannot capture in S')
    page.locator('#modalCancel').click()
    launcher.unchanged(page,before,'cancel cannot leave captured history')
    assert page.evaluate('operationFinalizeReview') is None

def reviewed_capture_is_confirmed(page):
    prepare_review_observation(page)
    page.evaluate('() => openFinalizeOperationModal()')
    reviewed=page.evaluate('operationFinalizeReview.op.maxAccountPhaseReached')
    page.locator('#finalDefenses').fill('0');page.locator('#finalConfirm').fill('FECHADO')
    page.locator('#modalConfirm').click()
    stored=result(page,'return JSON.parse(localStorage.getItem(LSKEY)).operationHistory.records[0];')
    assert stored['maxAccountPhaseReached']==reviewed==2 and stored['maxAccountPhaseIntegrity']=='observed',stored

def stale_review_requires_new_review(page):
    prepare_review_observation(page)
    page.evaluate('() => openFinalizeOperationModal()')
    r=result(page,"""
      const edit=operationRecordOrder(0,0,{result:7},{reason:'Correção posterior à revisão'}),before=JSON.stringify(S);
      const finalize=finalizeOperation({defenseCount:0});
      return {edit,finalize,same:before===JSON.stringify(S),history:S.operationHistory.records.length};
    """)
    assert_ok(r['edit']);assert not r['finalize']['ok'] and r['finalize']['motivo']=='review_stale' and r['same'] and r['history']==0,r
    page.locator('#modalCancel').click();page.evaluate('() => openFinalizeOperationModal()')
    page.locator('#finalDefenses').fill('0');page.locator('#finalConfirm').fill('FECHADO');page.locator('#modalConfirm').click()
    assert page.evaluate('S.operationHistory.records[0].netResult')==7


CASES=[record_blocked,render_and_typing,version_and_void,draft_delete,malformed_refused,planning_percent_display,unsupported_schema_read_only,
       close_zero_and_refusal,mutation_refusal_retry,unknown_barrier,context_and_extensions,
       pending_and_costs,conflicted_finalization,legacy_finalization,captured_reference_balance,unknown_reference_never_backfilled,
       account_period_scoped_finalization,factual_input_versioning,unresolved_period_never_selected_fallback,
       account_observation_captures_peak,account_peak_refusal_retry,account_peak_unknown,v11_result_does_not_mix_legacy_cycle,
       migrated_reference_identity,roles_and_currency_labels,order_risk_keeps_recorded_currency,mixed_context_cannot_finalize_as_one_currency,legacy_explicit_mixed_currency_refused,
       orphan_context_does_not_bind_new_operation,
       first_record_attaches_budget,budget_attachment_refusal_retry,budget_attachment_unknown,later_budget_does_not_backfill_first_snapshot,
       review_cancel_no_capture,reviewed_capture_is_confirmed,stale_review_requires_new_review]

def hashes(root):
    paths=[root/'index.html',root/'build-id.js',root/'src/styles/app.css',*sorted((root/'src/js').rglob('*.js'))]
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--out',type=Path);parser.add_argument('--case');parser.add_argument('--portable',action='store_true');args=parser.parse_args()
    root=args.root.resolve();launcher.ROOT=root
    report={'suite':'forex-recording-v11','inputs_before':hashes(root),'cases':[]}
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(launcher.Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(**launcher.launch_options())
        for test in CASES:
          if args.case and args.case not in test.__name__:continue
          context=browser.new_context(viewport={'width':1440,'height':900},service_workers='block',reduced_motion='reduce')
          row={'name':test.__name__}
          try:
            target='dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html' if args.portable else 'index.html'
            page,observed=launcher.prepare(context,f'http://127.0.0.1:{server.server_port}/{target}')
            row['build']=page.evaluate('JP_WEALTH_BUILD_ID');seed(page);test(page)
            if test in (unknown_barrier,account_peak_unknown,budget_attachment_unknown,orphan_context_does_not_bind_new_operation):
                expected=('[operação] identidade órfã descartada (sem ordens operacionais): synthetic-orphan-a' if test is orphan_context_does_not_bind_new_operation else '[persistência] DESFECHO INDETERMINADO — novas gravações bloqueadas: registro Forex')
                assert observed=={'pageerror':[],'console':[expected]},observed
                row['expected_console']=observed['console']
                launcher.assert_fixture_requests(context)
            else:launcher.assert_clean(context,observed)
            row['result']='PASS'
          except Exception as error:row.update(result='FAIL',error_type=type(error).__name__,detail=str(error))
          finally:context.close();report['cases'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
        browser.close()
    finally:
      server.shutdown();server.server_close();report['inputs_after']=hashes(root);report['source_unchanged']=report['inputs_before']==report['inputs_after']
      if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open('x') as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    return 0 if report['cases'] and report['source_unchanged'] and all(c['result']=='PASS' for c in report['cases']) else 1

if __name__=='__main__':sys.exit(main())

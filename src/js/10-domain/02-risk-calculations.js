// Current Forex projection. All normative arithmetic delegates to JPWForex.engine.
(function(root){
  const fx=root.JPWForex, e=fx.engine;
  const numeric=value=>typeof value==='number'&&Number.isFinite(value);
  const absent=(code,message)=>({status:'NOT_COMPUTABLE',value:null,findings:[{code,message,severity:'BLOCKING'}]});
  const value=result=>result&&result.status==='OK'?result.value:null;
  function conversion(ins,account){
    if(!ins||!account)return {quote:null,base:null};
    const quote=QUOTE_CCY[ins.name];
    const quoteUsd=quote==='USD'?1:quoteToUSD(quote);
    const accountRate=account.currency==='USD'?1:account.usdToAccountRate;
    return {quote:numeric(quoteUsd)&&numeric(accountRate)?quoteUsd*accountRate:null,
      base:numeric(usdPerBase(ins))&&numeric(accountRate)?usdPerBase(ins)*accountRate:null};
  }
  function orderInputs(order,account){
    const ins=instFor(order.par), rates=conversion(ins,account);
    const observed=fx.executionBoard?.instrumentInputs(ins,account,{accountId:order.accountId||account?.accountId,periodId:order.periodId||account?.periodId});
    return {side:order.tipo,entryPrice:order.entry,stopPrice:order.sl,volume:order.lote,
      contractSize:observed?observed.contractSize:(ins?ins.cpl:null),conversionRate:observed?observed.conversionRate:rates.quote,notionalConversionRate:observed?observed.notionalConversionRate:rates.base,
      stopValid:order.stopValidated===true,active:typeof order.pendingActive==='boolean'?order.pendingActive:null,
      kind:order.amplifiesExposure===true?'AMPLIFYING':order.amplifiesExposure===false?'REDUCING':null,
      exclusiveGroup:order.exclusiveGroup||null,exclusivityVerified:order.exclusivityVerified===true,
      exclusivityEvidence:order.exclusivityEvidence||null};
  }
  function readModel(target){
    const supported=fx.state.supported(), f=supported?S.forex:null;
    // Explicit historical scope never falls back to the selected account.
    const context=supported?(target===undefined?fx.state.recordContext():fx.state.recordContext(target)):null;
    const account=context&&context.accountInputs||null;
    const accountId=account?context.accountId:null;
    const accountRecord=accountId?(S.accounts||[]).find(a=>a.forexAccountId===accountId):null;
    const rawOrders=[];
    const unresolvedStatus=order=>order.recordStatus==='draft'||!['Aberta','Fechada','Pendente'].includes(order.status);
    for(const phase of S.phases||[])for(const order of phase.orders||[]){
      if(!order||order.recordStatus==='voided'||order.status==='Migrada')continue;
      // A draft without operational status is recoverable input, not a fact.
      // Contradictory or unknown statuses remain visible until explicitly reconciled.
      if(order.recordStatus==='draft'&&!order.status)continue;
      if(order.status||order.lote>0||order.entry>0||order.sl>0)rawOrders.push(order);
    }
    const facts=rawOrders.filter(o=>!o.accountId||o.accountId===accountId);
    const open=facts.filter(o=>o.status==='Aberta'), closed=facts.filter(o=>o.status==='Fechada');
    const unresolvedFacts=!account||facts.some(o=>unresolvedStatus(o)||o.accountId!==accountId||o.periodId!==account.periodId||o.currency!==account.currency);
    const unresolved=()=>absent('ORDER_CONTEXT_UNRESOLVED','Conta, período ou moeda dos fatos não conciliados. Ausência não representa risco zero.');
    const positions=open.map(o=>orderInputs(o,account));
    const pending=facts.filter(o=>o.status==='Pendente').map(o=>orderInputs(o,account));
    const dd=e.computeDrawdown(account||{});
    const rawPhase=e.resolveAccountPhase({ddPercent:value(dd)});
    const previous=account&&account.phaseState;
    const phase=previous&&Number.isInteger(previous.phase)?e.resolvePhaseReturnWithHysteresis({
      ddPercent:value(dd),previousPhase:previous.phase,since:previous.since,
      confirmedH4Closes:(f&&Array.isArray(f.h4Closes)?f.h4Closes:[]).filter(c=>c.accountId===accountId&&c.periodId===account.periodId&&Number.isFinite(Date.parse(c.closedAt))&&Date.parse(c.closedAt)<=Date.parse(account.observedAt))}):rawPhase;
    const phaseNumber=value(phase);
    const grid=f&&f.grid&&f.grid.operationId===(S.activeOperation&&S.activeOperation.operationId)?f.grid:null;
    const gridPhase=e.resolveActiveGridPhase({...grid,accountPhase:phaseNumber});
    const leverage=unresolvedFacts?unresolved():e.computeLeverage({si:account&&account.si,equity:account&&account.equity,
      positions:positions.map(p=>({volume:p.volume,contractSize:p.contractSize,conversionRate:p.notionalConversionRate}))});
    const genesis=facts.filter(o=>o.role==='GENESIS'&&o.recordStatus!=='voided');
    const marketContext=genesis.length===1&&account?fx.state.instrumentContext?.({accountId,periodId:account.periodId,instrumentId:genesis[0].par}):null;
    const observedAtr=marketContext?.status==='OK'?marketContext.value?.atr:null;
    const market=observedAtr?.timeframe==='H4'&&observedAtr?.unit==='PRICE'?{atrShort:observedAtr.short,atrLong:observedAtr.long}:{};
    const vrm=e.computeVRM(market),regime=e.resolveVRMRegime({vrm:value(vrm)});
    const effective=e.computeEffectiveLeverageLimit({phase:phaseNumber,vrm:value(vrm),otherLimits:[]});
    const aggregate=unresolvedFacts?unresolved():e.computeOpenAggregatePhaseRisk({positions,pendingOrders:pending});
    const realizedResults=closed.map(o=>o.result);
    // Costs are separately declared; absence is not a zero-cost assertion.
    const costs=facts.every(o=>numeric(o.costs)&&o.costBasis==='SEPARATE_FROM_RESULT')?facts.map(o=>o.costs):null;
    const committed=unresolvedFacts?unresolved():e.computeCommittedOperationRisk({positions,pendingOrders:pending,realizedResults,costs});
    // A recorded entry/stop and today's catalogue are not a pre-execution observation.
    // This delivery has no trustworthy historical admission snapshot for these facts.
    const admission={status:'BLOCKED',value:null,admissionBasis:'NO_PRE_EXECUTION_SNAPSHOT',
      findings:[{code:'ADMISSION_SNAPSHOT_MISSING',message:'Risco de admissão histórico não capturado antes da execução. O risco factual atual é apresentado separadamente.',severity:'BLOCKING'}]};
    const capacity=e.computePrudentialCapacity({si:account&&account.si,ddPercent:value(dd),committedRisk:value(committed)});
    const reserveObservation=f&&f.reserves&&f.reserves.accountId===accountId?f.reserves:null;
    const reserveMismatch=!!reserveObservation&&(!account||reserveObservation.periodId!==account.periodId||reserveObservation.currency!==account.currency);
    const r=reserveObservation&&!reserveMismatch?reserveObservation:{};
    const nominalConflict=numeric(r.capitalNominal)&&account&&numeric(account.capitalNominal)&&r.capitalNominal!==account.capitalNominal;
    const fcr=nominalConflict?absent('FCR_NOMINAL_CONFLICT','Capital nominal divergente entre observação da conta e reservas. É necessária conciliação explícita dos fatos.'):
      e.computeFCRRequirement({capitalNominal:accountRecord&&accountRecord.tipo==='MESTRE'?
        (numeric(r.capitalNominal)?r.capitalNominal:account&&account.capitalNominal):null,si:account&&account.si});
    const feo=e.computeFEORequirement({...r,si:account&&account.si});
    const fcrStatus=reserveMismatch?absent('RESERVE_CONTEXT_UNRESOLVED','Reserva registrada em período/moeda diferente; não conciliada com a observação atual.'):e.computeReserveStatus({requirement:fcr,constituted:r.fcrConstituted,liquidityDays:r.fcrLiquidityDays,
      verifiedAt:r.verifiedAt,verificationRecorded:r.verificationRecorded,fund:'FCR'});
    const feoStatus=reserveMismatch?absent('RESERVE_CONTEXT_UNRESOLVED','Reserva registrada em período/moeda diferente; não conciliada com a observação atual.'):e.computeReserveStatus({requirement:feo,constituted:r.feoConstituted,liquidityDays:r.feoLiquidityDays,
      verifiedAt:r.verifiedAt,verificationRecorded:r.verificationRecorded,fund:'FEO'});
    const active=S.activeOperation,opScope=active&&active.recordContext;
    const budgetScope={accountId,periodId:account&&account.periodId||null,
      operationId:opScope&&opScope.accountId===accountId&&opScope.periodId===account?.periodId?active.operationId:null};
    const budget=typeof fx.state.budgetSnapshot==='function'?fx.state.budgetSnapshot(budgetScope):absent('OPERATION_BUDGET_NOT_RECORDED','Orçamento declarado da operação ainda não registrado.');
    const sizing=e.computeSizingTrace?e.computeSizingTrace({}):absent('SIZING_TRACE_PENDING','Dimensionamento normativo indisponível.');
    const metrics={operationBudget:budget,sizingTrace:sizing,drawdown:dd,leverage,vrm,regime,effectiveLeverageLimit:effective,
      financialRisk:aggregate,admissionRisk:admission,committedRisk:committed,aggregateRisk:aggregate,
      prudentialCapacity:capacity,minimumStop:e.computeMinimumStop({atr:market.atrShort}),
      fcrRequirement:fcr,feoRequirement:feo,fcrStatus,feoStatus,
      replication:e.computeReplicationFirewall(account||{})};
    const findings=[];
    if(!supported)findings.push({code:'FOREX_SCHEMA_UNSUPPORTED',message:'Versão do agregado Forex desconhecida. Sem normalização automática.',severity:'BLOCKING'});
    if(!account)findings.push({code:'ACCOUNT_OBSERVATION_MISSING',message:'Registre conta, SI e equity flutuante com fonte. Saldo book não substitui equity.',severity:'BLOCKING'});
    if(facts.some(unresolvedStatus))findings.push({code:'ORDER_STATUS_UNRESOLVED',message:'Atividade legada com status não conciliado; registro preservado, exposição não presumida como zero.',severity:'BLOCKING'});
    if(facts.some(o=>!o.accountId))findings.push({code:'ORDER_ACCOUNT_UNRESOLVED',message:'Há fatos legados sem vínculo inequívoco de conta; exposições não constituem posição conciliada.',severity:'BLOCKING'});
    if(facts.some(o=>{const i=instFor(o.par);return i&&i.banned&&!i.unlocked;}))findings.push({code:'INSTRUMENT_RESTRICTED',message:'Instrumento registrado possui restrição normativa; o fato permanece auditável.',severity:'BLOCKING'});
    for(const m of Object.values(metrics))if(m&&Array.isArray(m.findings))findings.push(...m.findings);
    if(phase.findings)findings.push(...phase.findings);
    if(gridPhase.findings)findings.push(...gridPhase.findings);
    for(const key of ['P-14','P-17','P-18'])findings.push({code:key+'_PENDING',message:key+' PENDING: registro permitido; execução normativa BLOCKED.',severity:'BLOCKING',source:fx.policy.get(key).hostNorm});
    if(quarantineActive())findings.push({code:'QUARANTINE',message:'Quarentena registrada. P-24 não permite presumir prazo ou liberação.',severity:'BLOCKING'});
    if(numeric(value(leverage))&&numeric(phaseNumber)&&value(leverage)>fx.policy.phases[phaseNumber-1].maxLeverage)
      findings.push({code:'LEVERAGE_EXCEEDED',message:'Exposição acima do teto da fase da conta.',severity:'BLOCKING'});
    const unique=[...new Map(findings.map(item=>[item.code+'|'+item.message,item])).values()];
    const totalReserves=numeric(r.fcrConstituted)&&numeric(r.feoConstituted)?r.fcrConstituted+r.feoConstituted:null;
    return {policySnapshot:fx.policy.snapshot(),budgetScope,accountId,account:account?structuredClone(account):null,
      accountPhase:phase,rawAccountPhase:rawPhase,activeGridPhase:gridPhase,
      executionEligibility:{status:'BLOCKED',canExecuteNormatively:false,canRecord:supported,
        reason:'P-14/P-17/P-18 e requisitos de homologação não satisfeitos.'},canRecord:supported,
      metrics,findings:unique,orders:{open:open.length,closed:closed.length,total:facts.length,raw:facts.map(o=>structuredClone(o))},
      reserves:{observations:structuredClone(r),unmatchedObservation:reserveMismatch?structuredClone(reserveObservation):null,totalConstituted:totalReserves,openingStatus:'BLOCKED',
        distributionStatus:fcrStatus.status==='OK'&&feoStatus.status==='OK'?'PENDING_GOVERNANCE':'BLOCKED',
        ratchetStatus:'P-10_PENDING'},
      metricsStatus:account?'OBSERVED_WITH_LIMITATIONS':'NOT_COMPUTABLE'};
  }
  fx.readModel=readModel;fx.orderInputs=orderInputs;
})(globalThis);
function compute(){
  const model=JPWForex.state.read(),m=model.metrics;
  const val=x=>x&&x.status==='OK'?x.value:null;
  const phase=val(model.accountPhase),fi=Number.isInteger(phase)?phase-1:null;
  const matrix=activeRiskMatrix(),row=fi===null?{nome:model.accountPhase.compulsoryClose?'ENCERRAMENTO COMPULSÓRIO':'FASE NÃO CALCULÁVEL',alav:null,ddmax:null}:matrix[fi];
  const dd=val(m.drawdown),leverage=val(m.leverage),risk=val(m.aggregateRisk),committed=val(m.committedRisk);
  const open=model.orders.raw.filter(o=>o.status==='Aberta');
  const closed=model.orders.raw.filter(o=>o.status==='Fechada');
  const contextKnown=!model.findings.some(f=>['ORDER_STATUS_UNRESOLVED','ORDER_CONTEXT_UNRESOLVED'].includes(f.code));
  const financialKnown=contextKnown&&closed.every(o=>typeof o.result==='number'&&Number.isFinite(o.result));
  const net=financialKnown?closed.reduce((sum,o)=>sum+o.result,0):null;
  const grossProfit=financialKnown?closed.reduce((sum,o)=>sum+Math.max(0,o.result),0):null;
  return {forex:model,dd:dd===null?null:dd/100,ddDollar:dd===null||!model.account?null:dd/100*model.account.si,
    fi,fase:row,tetoAlav:row.alav,tetoRisco:null,loteTotal:open.every(o=>Number.isFinite(o.lote))?open.reduce((sum,o)=>sum+o.lote,0):null,
    riscoTotal:risk,riscoEstatutario:committed,lucroTecnico:null,resultadoBrutoPositivoFactual:grossProfit,netOp:net,
    perdaAtual:net===null?null:Math.max(0,-net),perdaCiclo:null,lucroArquivado:null,
    margemEstatutaria:null,margemInformativa:null,semStop:open.filter(o=>!(o.sl>0)||o.stopValidated!==true).length,
    alavCar:leverage,excesso:null,vrm:val(m.vrm),regime:val(m.regime)||'NOT_COMPUTABLE',
    status:'Registro permitido · execução normativa BLOCKED',sbCls:'sb-alert',ico:'⚠',
    sem:'BLOCKED — conformidade V11 pendente',semCls:'var(--warning)',
    sug:'Registre e corrija os fatos sem confundir gravação com autorização normativa. Consulte o Motor Forex para as lacunas.',
    excecao:true,profileFator:activeProfileFator(),mddScaled:activeMDDLimit(),alarmScaled:null,
    mScaled:fi===null?null:matrix};
}
function noExternalProtectionActive(){
  return !!(S.onboarding && S.onboarding.done && S.onboarding.epStatus==='Não vou utilizar.');
}
function noExternalProtectionWarning(){
  return 'Proteção externa desativada: este período está operando sem Equity Protector. Controle manual obrigatório. Risco aumentado de violação operacional.';
}
function shouldWarnManualRiskConfirmation(){
  const c=compute();
  const sameDayLoss=Array.isArray(S.ledger) && S.ledger.some(e=>e && e.data===todayISO() && (+e.result||0)<0);
  return noExternalProtectionActive() && (
    c.dd>0 || c.fi>0 || (Number.isFinite(c.riscoTotal)&&Number.isFinite(c.tetoRisco)&&c.riscoTotal>=0.8*c.tetoRisco) || isPropFirm(brokerFor(S.onboarding&&S.onboarding.corretora)||{}) || sameDayLoss
  );
}

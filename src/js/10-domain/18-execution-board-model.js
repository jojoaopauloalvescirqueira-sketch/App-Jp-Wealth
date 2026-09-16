// Execution Board: factual projections only. No storage, navigation or policy writes.
(function(root){
  'use strict';
  const fx=root.JPWForex, finite=Number.isFinite;
  const text=v=>typeof v==='string'?v.trim():'';
  const clone=v=>structuredClone(v);
  const metric=(value,unit,currency,reason,extra)=>Object.assign({status:finite(value)?'OK':'NOT_COMPUTABLE',value:finite(value)?value:null,unit,currency:currency||null,reason:reason||null},extra||{});
  const absent=(reason,unit='ACCOUNT_CURRENCY',currency)=>metric(null,unit,currency,reason);
  const sum=values=>values.every(finite)?values.reduce((a,b)=>a+b,0):null;
  const number=r=>r&&r.status==='OK'&&finite(r.value)?r.value:null;
  const factual=o=>o&&o.recordStatus!=='voided'&&o.status!=='Migrada'&&!(o.recordStatus==='draft'&&!o.status)&&!!(o.status||o.lote>0||o.entry>0||o.sl>0);
  const knownStatus=o=>o.recordStatus!=='draft'&&['Aberta','Fechada','Pendente'].includes(o.status);
  const issue=(code,message)=>({code,message});
  const percent=(m,si)=>Object.assign(m,{percent:finite(m.value)&&finite(si)&&si>0?m.value/si*100:null,percentBasis:'SI'});
  function engineMetric(result,currency){
    if(!result)return absent('Resultado normativo não disponível.',undefined,currency);
    return Object.assign(clone(result),{currency:currency||null,reason:result.findings?.map(f=>f.message||f.code).join(' · ')||null});
  }
  function closedNetResult(order){
    const currency=order?.currency;
    if(!order||order.status!=='Fechada'||order.recordStatus==='voided'||!finite(order.result))return absent('Resultado encerrado não informado.',undefined,currency);
    if(order.costBasis==='INCLUDED_IN_RESULT')return metric(order.result,'ACCOUNT_CURRENCY',currency,null,{method:'RESULT_INCLUDES_COSTS'});
    if(order.costBasis==='SEPARATE_FROM_RESULT'&&finite(order.costs))return metric(order.result+order.costs,'ACCOUNT_CURRENCY',currency,null,{method:'SIGNED_RESULT_PLUS_SEPARATE_COSTS'});
    return absent('Declare se os custos estão incluídos no resultado; custos separados exigem valor assinado.',undefined,currency);
  }
  function prepareInstrument(ins,account,scope){
    const instrumentId=root.instrumentId(ins.name), context=fx.state.instrumentContext?.({...scope,instrumentId});
    const observation=context?.status==='OK'?(context.observation||context.value):null;
    const dailyResult=fx.state.dailyReference?.(instrumentId),daily=dailyResult?.status==='OK'?dailyResult.value:null;
    const price=observation?.price?{...clone(observation.price),kind:'MANUAL'}:daily?{value:daily.rate,source:daily.source,referenceDate:daily.referenceDate,fetchedAt:daily.fetchedAt,kind:'DAILY_REFERENCE'}:
      {value:finite(ins.preco)?ins.preco:null,source:'Cadastro legado do instrumento',referenceDate:ins.updated||null,kind:'LEGACY_REFERENCE'};
    const contract=observation?.contract||{contractSize:finite(ins.cpl)?ins.cpl:null,source:'Cadastro do instrumento',observedAt:null};
    const conversion=observation?.conversion||null;
    return {id:instrumentId,name:ins.name,banned:!!ins.banned,unlocked:!!ins.unlocked,restriction:ins.banReason||null,price,contract:clone(contract),conversion:clone(conversion),atr:clone(observation?.atr||null),observation:clone(observation),dailyReference:clone(daily)};
  }
  function resolveConversions(instruments,account){
    const graph=new Map(),currencies=new Set(['USD','BRL','EUR','GBP','JPY','CHF','CAD','AUD','NZD']);
    const pair=i=>{const quote=typeof QUOTE_CCY==='object'?QUOTE_CCY[i.name]:null;return {base:currencies.has(i.name.slice(0,3))?i.name.slice(0,3):i.id,quote};};
    const add=(from,to,rate,provenance)=>{if(!from||!to||from===to||!finite(rate)||rate<=0)return;for(const [a,b,value] of [[from,to,rate],[to,from,1/rate]]){const edges=graph.get(a)||[];edges.push({from:a,to:b,rate:value,...clone(provenance)});graph.set(a,edges);}};
    // Only observed/manual or dated daily references enter conversion paths.
    // A displayed legacy price is not promoted to an observed conversion.
    for(const i of instruments){const p=i.price,{base,quote}=pair(i);if(p?.kind==='MANUAL'&&text(p.source)&&text(p.observedAt)||p?.kind==='DAILY_REFERENCE'&&text(p.source)&&text(p.referenceDate))add(base,quote,p.value,{instrumentId:i.id,source:p.source,kind:p.kind,observedAt:p.observedAt||null,referenceDate:p.referenceDate||null});}
    const dedicatedAccountRate=account?.currency!=='USD'&&finite(account?.usdToAccountRate)&&account.usdToAccountRate>0&&
      text(account?.source)&&text(account?.observedAt)&&Number.isFinite(Date.parse(account.observedAt))?
      {from:'USD',to:account.currency,rate:account.usdToAccountRate,source:account.source,kind:'ACCOUNT_OBSERVATION',observedAt:account.observedAt}:null;
    function path(from,to){
      if(from&&from===to)return {value:1,legs:[{from,to,rate:1,source:'Identidade da moeda',kind:'IDENTITY',observedAt:null}]};
      const queue=[{at:from,value:1,legs:[],visited:new Set([from])}];
      while(queue.length){const current=queue.shift();for(const edge of graph.get(current.at)||[]){if(current.visited.has(edge.to))continue;const next={at:edge.to,value:current.value*edge.rate,legs:[...current.legs,edge],visited:new Set([...current.visited,edge.to])};if(edge.to===to)return next;if(next.legs.length<3)queue.push(next);}}
      return {value:null,legs:[],reason:'Não há caminho de conversão com fonte e data para '+(from||'moeda desconhecida')+' → '+(to||'conta desconhecida')+'.'};
    }
    function accountPath(from){
      const derived=path(from,account?.currency);
      // Preserve the dedicated USD-to-account observation used by the account
      // adapter. A shorter route through a quoted price does not override it.
      // Identical currencies remain exact; instrument-specific manual rates
      // are resolved before this function and have the highest precedence.
      if(!dedicatedAccountRate||from===account?.currency)return {...derived,selection:from===account?.currency?'IDENTITY':'OBSERVED_PRICE_PATH',alternatives:[]};
      const usd=path(from,'USD');
      if(!finite(usd.value))return {...usd,selection:'ACCOUNT_OBSERVATION',alternatives:finite(derived.value)?[{...derived,selected:false,reason:'A conversão dedicada da conta exige um caminho identificado até USD.'}]:[]};
      const value=usd.value*dedicatedAccountRate.rate;
      const alternative=finite(derived.value)?{value:derived.value,legs:derived.legs,selected:false,differs:Math.abs(derived.value-value)>1e-12,
        reason:'Caminho derivado de preços preservado como alternativa; a conversão dedicada da conta tem precedência.'}:null;
      return {value,legs:[...usd.legs,clone(dedicatedAccountRate)],selection:'ACCOUNT_OBSERVATION',alternatives:alternative?[alternative]:[],
        reason:alternative?.differs?'Conversão dedicada da conta priorizada; o caminho derivado dos preços possui valor diferente.':null};
    }
    return instruments.map(i=>{const {base,quote}=pair(i),manual=i.conversion;
      if(manual)return {...i,conversion:{...manual,sourceKind:'MANUAL',selection:{quote:'INSTRUMENT_OBSERVATION',base:'INSTRUMENT_OBSERVATION'},legs:{quote:[{from:quote,to:account?.currency,rate:manual.quoteToAccountRate,source:manual.source,kind:'MANUAL',observedAt:manual.observedAt}],base:[{from:base,to:account?.currency,rate:manual.baseToAccountRate,source:manual.source,kind:'MANUAL',observedAt:manual.observedAt}]}}};
      const q=accountPath(quote),b=accountPath(base);
      return {...i,conversion:{quoteToAccountRate:q.value,baseToAccountRate:b.value,source:'Conversões pelas referências identificadas',sourceKind:'DERIVED',observedAt:null,
        selection:{quote:q.selection,base:b.selection},legs:{quote:q.legs,base:b.legs},alternatives:{quote:q.alternatives,base:b.alternatives},reasons:[q.reason,b.reason].filter(Boolean)}};
    });
  }
  function referenceInstrument(ins,account,currency){
    const size=ins.contract?.contractSize,rate=ins.conversion?.baseToAccountRate;
    const base=finite(account?.si)&&account.si>0&&finite(account?.equity)&&account.equity>0?Math.min(account.si,account.equity):null;
    const unit=finite(size)&&size>0&&finite(rate)&&rate>0?size*rate:null;
    const factors=fx.policy.get('P-12b').value;
    const ref=f=>metric(base!==null&&unit!==null?base*f/unit:null,'LOTS',null,'Referência nocional teórica; não é lote autorizado.',{base,multiple:f,lotMinimumEvaluated:false,executionEligibility:'BLOCKED'});
    const atr=ins.atr,vrm=atr?.timeframe==='H4'&&atr.unit==='PRICE'?fx.engine.computeVRM({atrShort:atr.short,atrLong:atr.long}):null;
    return {...clone(ins),notionalPerLot:metric(unit,'ACCOUNT_CURRENCY',currency,unit===null?'Contrato ou conversão não disponível.':null),normal:ref(factors.normal),restrictive:ref(factors.transition),
      vrm:vrm?engineMetric(vrm):absent('ATR 55/660 H4 não vinculado a este instrumento.','RATIO'),
      regime:vrm?engineMetric(fx.engine.resolveVRMRegime({vrm:number(vrm)})):absent('Regime sem ATRs identificados.','REGIME'),
      minimumStop:atr?.timeframe==='H4'&&atr.unit==='PRICE'?engineMetric(fx.engine.computeMinimumStop({atr:atr.short})):absent('ATR 55 H4 ausente.','PRICE'),
      rootN:absent('Fator F P-21 pendente; N depende de declaração do horizonte. Diagnóstico sem veto.','PERCENT'),
      operable:!ins.banned||ins.unlocked===true};
  }
  function instrumentInputs(ins,account,scope={}){
    const instruments=(typeof S==='object'&&Array.isArray(S.instruments)?S.instruments:ins?[ins]:[]).map(i=>prepareInstrument(i,account,scope));
    const item=resolveConversions(instruments,account).find(i=>i.id===root.instrumentId(ins?.name));
    return {contractSize:item?.contract?.contractSize??null,conversionRate:item?.conversion?.quoteToAccountRate??null,
      notionalConversionRate:item?.conversion?.baseToAccountRate??null,
      provenance:{...clone(scope),instrumentId:item?.id||null,contract:clone(item?.contract||null),conversion:clone(item?.conversion||null)}};
  }
  function project(input){
    const scope=clone(input.scope||{}), account=clone(input.account||null),currency=account?.currency||scope.currency||null,si=account?.si;
    const findings=clone(input.findings||[]),catalog=(input.instruments||[]).map(i=>referenceInstrument(i,account,currency));
    const catalogById=new Map(catalog.map(i=>[i.id,i]));
    const rows=(input.rows||[]).map(r=>({...clone(r),order:clone(r.order||r.o||{})}));
    const unresolved=[],ignored=[],matching=[];
    const identities=new Map();
    for(const row of rows){
      const o=row.order;
      if(!factual(o)){ignored.push(row);continue;}
      if(!knownStatus(o)||![o.accountId,o.periodId,o.currency,o.operationId,o.orderId].every(text)){
        row.reason='Status ou identidade do fato incompletos.';unresolved.push(row);continue;
      }
      if(o.accountId!==scope.accountId||o.periodId!==scope.periodId||o.currency!==currency||o.operationId!==scope.operationId){
        row.reason='Fato de outra conta, período, moeda ou operação.';ignored.push(row);continue;
      }
      const seen=identities.get(o.orderId);if(seen){row.reason='Identificador de ordem repetido.';unresolved.push(row);seen.duplicate=true;continue;}
      identities.set(o.orderId,row);matching.push(row);
    }
    for(let i=matching.length-1;i>=0;i--)if(matching[i].duplicate){const row=matching.splice(i,1)[0];row.reason='Identificador de ordem repetido.';unresolved.push(row);}
    const scoped=!!account&&text(scope.accountId)&&text(scope.periodId)&&account.periodId===scope.periodId&&(!input.operation||!!text(scope.operationId));
    const complete=!!scoped&&!unresolved.length;
    if(unresolved.length)findings.push(issue('BOARD_UNRESOLVED_FACTS','Existem fatos não conciliados; totais completos não presumem a qual conta pertencem.'));
    function enrich(row){
      const o=row.order,ins=catalogById.get(root.instrumentId(o.par));
      const prepared=row.inputs||{side:o.tipo,entryPrice:o.entry,stopPrice:o.sl,volume:o.lote,contractSize:ins?.contract?.contractSize,
        conversionRate:ins?.conversion?.quoteToAccountRate,notionalConversionRate:ins?.conversion?.baseToAccountRate,stopValid:o.stopValidated===true,
        active:o.pendingActive,kind:o.amplifiesExposure===true?'AMPLIFYING':o.amplifiesExposure===false?'REDUCING':null,
        exclusiveGroup:o.exclusiveGroup,exclusivityVerified:o.exclusivityVerified,exclusivityEvidence:o.exclusivityEvidence};
      const risk=o.status==='Aberta'?engineMetric(fx.engine.computeFinancialRisk(prepared),currency):absent('A ordem não está aberta.',undefined,currency);
      const notional=o.status==='Aberta'?fx.engine.computeLeverage({si:account?.si,equity:account?.equity,positions:[{volume:prepared.volume,contractSize:prepared.contractSize,conversionRate:prepared.notionalConversionRate}]}):null;
      const stopPercent=finite(ins?.price?.value)&&ins.price.value>0&&finite(o.sl)&&o.sl>0?Math.abs(ins.price.value-o.sl)/ins.price.value*100:null;
      return {...row,instrumentId:root.instrumentId(o.par),inputs:prepared,risk:percent(risk,si),notional:metric(notional?.status==='OK'?notional.grossNotional:null,'ACCOUNT_CURRENCY',currency),
        netResult:closedNetResult(o),atrMultiple:engineMetric(fx.engine.computeStopAtrMultiple({stopPercent,
          atr:ins?.atr?.timeframe==='H4'&&ins.atr.unit==='PRICE'?ins.atr.short:null,currentPrice:ins?.price?.value}))};
    }
    const enriched=matching.map(enrich);
    function totals(list,isComplete){
      const open=list.filter(r=>r.order.status==='Aberta'),closed=list.filter(r=>r.order.status==='Fechada'),pending=list.filter(r=>r.order.status==='Pendente');
      const defenses=closed.filter(r=>r.order.role==='DEFENSE'),unknownRoles=closed.some(r=>!['GENESIS','DEFENSE','OTHER'].includes(r.order.role));
      const m=(n,reason)=>percent(metric(isComplete?n:null,'ACCOUNT_CURRENCY',currency,isComplete?reason:'Contexto ou fatos não conciliados.'),si);
      const openRisk=m(sum(open.map(r=>number(r.risk))),'Risco positivo dos stops válidos das posições abertas.');
      const netAll=m(sum(closed.map(r=>number(r.netResult))),'Resultado realizado assinado; custos incluídos uma única vez.');
      const netDefenses=m(unknownRoles?null:sum(defenses.map(r=>number(r.netResult))),unknownRoles?'Há ordens encerradas sem papel declarado.':'Somente ordens encerradas explicitamente declaradas como defesa.');
      const costs=m(sum(list.map(r=>['SEPARATE_FROM_RESULT','INCLUDED_IN_RESULT'].includes(r.order.costBasis)?r.order.costs:null)), 'Custos assinados registrados; demonstrativo separado, sem nova dedução dos resultados líquidos.');
      const comp=net=>m(finite(openRisk.value)&&finite(net.value)?openRisk.value-net.value:null,'Demonstrativo econômico; não reduz risco comprometido nem amplia limites.');
      const leverage=isComplete?fx.engine.computeLeverage({si:account?.si,equity:account?.equity,positions:open.map(r=>({volume:r.inputs.volume,contractSize:r.inputs.contractSize,conversionRate:r.inputs.notionalConversionRate}))}):null;
      const aggregate=isComplete?fx.engine.computeOpenAggregatePhaseRisk({positions:open.map(r=>r.inputs),pendingOrders:pending.map(r=>r.inputs)}):null;
      const ids=new Set(open.map(r=>r.instrumentId));
      const pendingRisk=isComplete?fx.engine.computeOpenAggregatePhaseRisk({positions:[],pendingOrders:pending.map(r=>r.inputs)}):null;
      return {open:openRisk,aggregate:engineMetric(aggregate,currency),pending:engineMetric(pendingRisk,currency),costs,closedNetAll:netAll,closedNetDefenses:netDefenses,compensatedAll:comp(netAll),compensatedDefenses:comp(netDefenses),
        leverage:engineMetric(leverage),grossNotional:m(leverage?.status==='OK'?leverage.grossNotional:null),
        lots:metric(ids.size<=1&&isComplete?sum(open.map(r=>r.order.lote)):null,'LOTS',null,ids.size>1?'Volumes de instrumentos distintos não são somados.':null),
        counts:{open:open.length,closed:closed.length,pending:pending.length,defenses:defenses.length},complete:isComplete};
    }
    const total=totals(enriched,complete),normative=input.normative;
    const normativeAccountScoped=complete&&normative?.accountId===scope.accountId&&normative?.account?.periodId===scope.periodId;
    const foreignOperation=o=>factual(o)&&o.accountId===scope.accountId&&o.periodId===scope.periodId&&o.currency===currency&&o.operationId!==scope.operationId;
    // The canonical account projection sees all its active buffers. Its RC
    // cannot be relabelled as this operation's RC when another operation is
    // present in those buffers, even if the Board's factual filter excludes it.
    const normativeOperationMismatch=rows.some(r=>foreignOperation(r.order))||
      (normative?.orders?.raw||[]).some(foreignOperation);
    if(normativeOperationMismatch)findings.push(issue('BOARD_NORMATIVE_OPERATION_UNRESOLVED','O motor da conta inclui fatos de outra operação nos buffers ativos. Risco comprometido, capacidade e orçamento não estão conciliados com esta operação.'));
    const normativeScoped=normativeAccountScoped&&!normativeOperationMismatch;
    const unavailableNorm=()=>absent(normativeOperationMismatch?'Fatos de outra operação nos buffers do motor; contexto normativo da operação não conciliado.':'Contexto normativo não conciliado.',undefined,currency);
    const phases=(input.phases||[]).map((p,index)=>{
      const legacy=p.policyVersion==='LEGACY_UNRESOLVED'||input.phases.length===4;
      const members=enriched.filter(r=>r.pi===index),phaseComplete=complete&&!unresolved.some(r=>r.pi===index);
      const info=legacy?null:fx.policy.phases[index];
      return {index,id:legacy?'LEGACY_'+(index+1):info?.id??null,name:legacy?'LEGACY '+(index+1):info?.name||'Fase não identificada',legacy,
        ddMinPercent:info?.ddMinPercent??null,ddMaxPercent:info?.ddMaxPercent??null,maxLeverage:info?.maxLeverage??null,
        rows:members,allRows:rows.filter(r=>r.pi===index),metrics:totals(members,phaseComplete),
        instruments:[...new Set(members.map(r=>r.instrumentId))].map(id=>({id,name:id,metrics:totals(members.filter(r=>r.instrumentId===id),phaseComplete)})),
        technicalProfit:absent('Liquidação parcial corretiva e finalidade não demonstradas. Resultado positivo não é Lucro Técnico.'),
        freeNormativeMargin:absent('TRA P-17 pendente; largura de fase não é orçamento de risco.')};
    });
    const drawdown=engineMetric(fx.engine.computeDrawdown(account||{})),book=input.accountRecord,
      contextPeriod=input.contextPeriod||null;
    const accountPhase=normativeAccountScoped?engineMetric(normative.accountPhase):engineMetric(fx.engine.resolveAccountPhase({ddPercent:number(drawdown)}));
    const phaseLimit=accountPhase.status==='OK'?fx.policy.phases[accountPhase.value-1]?.maxLeverage:null;
    const equityFloor=scoped&&finite(si)&&si>0&&finite(account.netCashflow)&&(account.netCashflow===0||account.cashflowAdjustmentRecorded===true)?si*(1-fx.policy.get('P-03').value/100)+account.netCashflow:null;
    const result={selection:clone(input.selection||{}),scope,account,accountRecord:clone(book||null),operation:clone(input.operation||null),
      capital:{si:metric(finite(si)?si:contextPeriod?.si,'ACCOUNT_CURRENCY',currency),equity:metric(account?.equity,'ACCOUNT_CURRENCY',currency),nominal:metric(account?.capitalNominal,'ACCOUNT_CURRENCY',currency),
        book:metric(book?.currency===currency?book?.satu:null,'ACCOUNT_CURRENCY',currency,'Saldo book deste período; não é equity flutuante.'),
        floating:absent('Equity e saldo book não têm observação simultânea conciliada.',undefined,currency),
        periodResult:absent('O fechamento diário não captura moeda e cobertura completa do período. Resultados das ordens encerradas desta operação são apresentados separadamente.',undefined,currency),drawdown,
        stopoutEquity:metric(equityFloor,'ACCOUNT_CURRENCY',currency,'Referência do encerramento estatutário por DD; não é stop-out da corretora.',{ddMaxPercent:fx.policy.get('P-03').value})},
      risk:{open:total.open,aggregate:total.aggregate,pending:total.pending,costs:total.costs,leverage:total.leverage,grossNotional:total.grossNotional,
        committed:normativeScoped?engineMetric(normative.metrics?.committedRisk,currency):unavailableNorm(),
        prudential:normativeScoped?engineMetric(normative.metrics?.prudentialCapacity,currency):unavailableNorm(),
        prudentialRemaining:normativeScoped?engineMetric(normative.metrics?.prudentialCapacity,currency):unavailableNorm(),
        leverageLimit:metric(phaseLimit,'MULTIPLE',null,'Teto agregado da fase da conta; não substitui VRM, orçamento e risco de admissão por ordem.'),accountPhase,
        activeGridPhase:normativeScoped?engineMetric(normative.activeGridPhase):unavailableNorm(),
        operationBudget:normativeScoped?engineMetric(normative.metrics?.operationBudget,currency):unavailableNorm(),
        sizingTrace:clone(normative?.metrics?.sizingTrace||fx.engine.computeSizingTrace())},
      economics:{closedNetAll:total.closedNetAll,closedNetDefenses:total.closedNetDefenses,compensatedAll:total.compensatedAll,compensatedDefenses:total.compensatedDefenses},
      phases,rows:enriched,instruments:catalog,unresolved,ignored,findings:[...findings,...clone(normative?.findings||[])],complete,normativeScopeComplete:!!normativeScoped,
      canRecord:input.supported!==false,executionEligibility:clone(normative?.executionEligibility||{status:'BLOCKED',canExecuteNormatively:false,canRecord:input.supported!==false})};
    const baseSource={accountId:scope.accountId||null,periodId:scope.periodId||null,operationId:scope.operationId||null};
    const accountSource={...baseSource,label:'Observação da conta',source:account?.source||'Fonte da observação não identificada',observedAt:account?.observedAt||null};
    const orderSources=enriched.map(r=>({orderId:r.order.orderId,source:'Registro da ordem',recordedAt:r.order.recordedAt||r.order.updatedAt||r.order.calculationInputs?.recordedAt||null,recordVersion:r.order.recordVersion||null}));
    const sources={...baseSource,label:'Fatos da operação e observações identificadas',observedAt:null,account:accountSource,orders:orderSources,
      instruments:catalog.map(i=>({instrumentId:i.id,price:i.price,contract:i.contract,conversion:i.conversion,atr:i.atr}))};
    function annotate(value,source){
      if(!value||typeof value!=='object')return;
      if(Object.hasOwn(value,'status')&&Object.hasOwn(value,'value')){
        value.provenance=clone(source);if(!value.source)value.source=clone(source);return;
      }
      for(const child of Object.values(value))annotate(child,source);
    }
    annotate(result.capital,accountSource);
    result.capital.book.source=result.capital.book.provenance={...baseSource,label:'Fechamento book deste período ou saldo inicial observado',observedAt:contextPeriod?.observedAt||null};
    result.capital.periodResult.source=result.capital.periodResult.provenance={...baseSource,label:'Fechamentos diários sem moeda/cobertura conciliadas',observedAt:null};
    annotate(result.risk,sources);annotate(result.economics,sources);annotate(result.phases,sources);annotate(result.rows,sources);
    for(const i of result.instruments){const source={...baseSource,instrumentId:i.id,label:'Referência deste instrumento',observedAt:null,price:i.price,contract:i.contract,conversion:i.conversion,atr:i.atr};annotate(i,source);}
    return result;
  }
  function read(options={}){
    const source=S,selected=fx.state.operationalSelection(),requested=text(options.accountId)||selected.accountId;
    let accountId=requested;
    const periodId=text(options.periodId)||(accountId===selected.accountId?selected.periodId:null),
      workspace=accountId&&periodId?fx.state.accountContext({accountId,periodId}):null,
      contextPeriod=workspace?.status==='OK'?workspace.value:null,
      op=contextPeriod?.activeOperation||null,
      phases=contextPeriod?.phases||fx.state.newOperationPhases(),
      allRows=phases.flatMap((p,pi)=>(p.orders||[]).map((o,oi)=>({pi,oi,order:clone(o)})));
    const live=allRows.some(r=>factual(r.order));
    const accounts=(source.accounts||[]).filter(a=>text(a?.forexAccountId)).map(a=>({id:a.forexAccountId,name:a.nome||'Conta sem nome',type:a.tipo||null,currency:a.platformCurrency||null}));
    const findings=[];let reason=selected.reason,accountIndex=null;
    if(accountId&&!accounts.some(a=>a.id===accountId)){reason='ACCOUNT_NOT_REGISTERED';accountId=null;}
    if(accountId)accountIndex=(source.accounts||[]).findIndex(a=>a?.forexAccountId===accountId);
    if(!contextPeriod)findings.push(issue('BOARD_PERIOD_UNREGISTERED','Registre ou reconcilie um período em Contas antes de editar esta operação.'));
    if(live&&!op)findings.push(issue('BOARD_OPERATION_ID_MISSING','Há fatos sem identidade de operação neste período; preserve-os para revisão.'));
    const scope={accountId,periodId,operationId:op?.operationId||null};
    const context=accountId&&periodId?fx.state.recordContext({accountId,periodId}):null;
    const account=context?.status==='OK'?context.accountInputs:null;scope.currency=account?.currency||contextPeriod?.currency||null;
    const record=accountIndex!==null?source.accounts[accountIndex]:null;
    const bookRows=contextPeriod?.ledger||[],lastBook=bookRows.slice().sort((a,b)=>a.data.localeCompare(b.data)).at(-1)?.saldo??contextPeriod?.openingBook??null;
    const safeRecord=record?{name:record.nome||'',type:record.tipo||'',currency:contextPeriod?.currency||null,satu:lastBook,broker:record.broker||null,
      platform:text(record.platform)||null,login:text(record.platformLogin)||null,platformLogin:text(record.platformLogin)||null}:null;
    const normative=account?fx.state.read({accountId,periodId}):null;
    return project({scope,account,contextPeriod,accountRecord:safeRecord,operation:op?{operationId:op.operationId,policySnapshot:clone(op.policySnapshot||null)}:null,
      selection:{accountId,periodId,operationId:scope.operationId,accountIndex,reason,requiresSelection:!accountId,requiresObservation:!account,lockedToOperation:false,accounts},
      rows:allRows,phases:clone(phases),instruments:resolveConversions((source.instruments||[]).map(i=>prepareInstrument(i,account,scope)),account),normative,findings,supported:fx.state.supported()});
  }
  fx.executionBoard=Object.freeze({read,project,closedNetResult,instrumentInputs});
})(globalThis);

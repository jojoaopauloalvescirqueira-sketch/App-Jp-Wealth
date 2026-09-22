// Pure V11 projections. An OK arithmetic result never authorizes execution.
// Caller supplies explicit quantities and provenance; no S, DOM, storage or IO.
(function(root){
  'use strict';
  const ns=root.JPWForex||(root.JPWForex={});
  if(!ns.policy)throw new Error('JPWForex.policy must load before its engine');
  function createEngine(policy){
  // This boundary validates a calculation input, not the identity or authority
  // of an approver. Scenarios cannot activate a registry or authorize execution.
  if(!policy||!Object.isFrozen(policy)||typeof policy.version!=='string'||!policy.version||
     !['CURRENT_DOCUMENTARY','SCENARIO'].includes(policy.calculationMode)||
     typeof policy.get!=='function'||!policy.sources||!Object.isFrozen(policy.sources)||!Object.isFrozen(policy.sources.statute)||!Object.isFrozen(policy.sources.annex)||
     !policy.sources.statute||!policy.sources.annex||!Array.isArray(policy.phases)||!Object.isFrozen(policy.phases)||policy.phases.length!==6||!policy.planning||!Object.isFrozen(policy.planning)){
    throw new TypeError('Complete immutable policy registry required');
  }
  for(const id of ['P-03','P-04a','P-04b','P-11','P-12a','P-12b','P-14','P-16','P-17','P-18','P-20','P-27','P-28','FEO_COVERAGE']){
    const row=policy.get(id);if(!row||!Object.isFrozen(row)||row.id!==id||!ownFields(row,['value','authorityMode','hostNorm','homologationStatus']))throw new TypeError('Incomplete policy item '+id);
  }
  if(!policy.phases.every((p,i)=>Object.isFrozen(p)&&p.id===i+1&&Number.isFinite(p.ddMaxPercent)&&p.ddMaxPercent>(i?policy.phases[i-1].ddMaxPercent:0)&&Number.isFinite(p.maxLeverage)&&p.maxLeverage>0)||
      policy.phases[5].ddMaxPercent!==policy.get('P-03').value)throw new TypeError('Policy phase boundaries do not match DD_MAX');
  function ownFields(object,keys){return keys.every(key=>Object.prototype.hasOwnProperty.call(object,key));}
  const finite=x=>typeof x==='number'&&Number.isFinite(x);
  const positive=x=>finite(x)&&x>0;
  const nonnegative=x=>finite(x)&&x>=0;
  const validPhase=x=>Number.isInteger(x)&&x>=1&&x<=policy.phases.length;
  const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
  const finding=(code,message,source,severity='WARNING')=>({code,message,source:source||null,severity});
  function result(status,value,unit,findings,extra){return Object.assign({status,value,unit,findings:findings||[],policyVersion:policy.version,calculationMode:policy.calculationMode},extra||{});}
  function absent(fields,unit){return result('PENDING_INPUT',null,unit,[finding('MISSING_INPUT','Dados ausentes ou incompletos: '+fields.join(', '),null,'BLOCKING')],{missing:fields});}
  function invalid(message,unit){return result('NOT_COMPUTABLE',null,unit,[finding('INVALID_INPUT',message,null,'BLOCKING')]);}
  function ok(value,unit,findings,extra){return finite(value)||typeof value!=='number'?result('OK',value,unit,findings,extra):invalid('Resultado não finito.',unit);}
  function requireNumbers(input,keys,unit,validator){
    const missing=keys.filter(k=>input[k]===undefined||input[k]===null);
    if(missing.length)return absent(missing,unit);
    return keys.every(k=>(validator||finite)(input[k]))?null:invalid('Quantidades inválidas: '+keys.join(', '),unit);
  }
  function phaseInfo(n){return validPhase(n)?policy.phases[n-1]:null;}
  function param(id){const row=policy.get(id);return row?row.value:null;}
  function parameterWarnings(ids){return ids.map(id=>policy.get(id)).filter(row=>row&&row.homologationStatus!=='HOMOLOGATED'&&row.homologationStatus!=='NOT_APPLICABLE').map(row=>finding('PARAMETER_NOT_HOMOLOGATED','Valor documental '+row.id+': '+row.homologationStatus+'. Cálculo não homologa.',row.hostNorm));}
  function blockedParameters(ids,extra){return result('BLOCKED',null,'ACCOUNT_CURRENCY',ids.map(id=>finding(id+'_PENDING',id+' não possui valor vigente homologado; sem zero ou fallback.',policy.get(id).hostNorm,'BLOCKING')),extra);}

  function computeDrawdown(input){
    const x=input||{},unit='DD_PERCENT';
    const error=requireNumbers(x,['si','equity','netCashflow'],unit);if(error)return error;
    if(!positive(x.si))return invalid('SI deve ser positivo.',unit);
    if(x.netCashflow!==0&&x.cashflowAdjustmentRecorded!==true)return absent(['cashflowAdjustmentRecorded'],unit);
    // Positive net cashflow means deposits minus withdrawals; neutralize only
    // the documented adjustment. This does not redefine the cycle reference.
    const adjustedEquity=x.equity-x.netCashflow;
    return ok(Math.max(0,(x.si-adjustedEquity)/x.si*100),unit,[],{si:x.si,equity:x.equity,adjustedEquity,neutralizedCashflow:x.netCashflow});
  }
  function positionNotional(position){
    const p=position||{};
    const error=requireNumbers(p,['volume','contractSize','conversionRate'],'ACCOUNT_CURRENCY');if(error)return error;
    if(!nonnegative(p.volume)||!positive(p.contractSize)||!positive(p.conversionRate))return invalid('Volume/contrato/conversão inválidos.','ACCOUNT_CURRENCY');
    return ok(Math.abs(p.volume*p.contractSize*p.conversionRate),'ACCOUNT_CURRENCY');
  }
  function computeGrossNotional(input){
    const x=input||{},unit='ACCOUNT_CURRENCY';
    if(!Array.isArray(x.positions))return absent(['positions'],unit);
    let gross=0;
    for(const p of x.positions){const n=positionNotional(p);if(n.status!=='OK')return n;gross+=n.value;}
    return ok(gross,unit);
  }
  function computeLeverage(input){
    const x=input||{},unit='MULTIPLE';
    const error=requireNumbers(x,['si','equity'],unit);if(error)return error;
    if(!positive(x.si)||!positive(x.equity))return invalid('A base min(SI, Equity) deve ser positiva.',unit);
    if(!Array.isArray(x.positions))return absent(['positions'],unit);
    const notional=computeGrossNotional(x);
    if(notional.status!=='OK')return result(notional.status,null,unit,notional.findings);
    const gross=notional.value;
    const base=Math.min(x.si,x.equity);
    return ok(gross/base,unit,[],{grossNotional:gross,base});
  }
  function resolveAccountPhase(input){
    const x=input||{},unit='PHASE';
    const error=requireNumbers(x,['ddPercent'],unit,nonnegative);if(error)return error;
    const maximum=param('P-03');
    // Closure precedes numeric phase lookup, even when DD crosses many phases.
    if(x.ddPercent>=maximum)return result('BLOCKED',null,unit,[finding('COMPULSORY_CLOSE','DD atingiu o limite: encerramento compulsório e quarentena.','PDF pp52/54 Art6.1/6.3','BLOCKING')],{compulsoryClose:true,reachedPhase:6,ddPercent:x.ddPercent,ddMaxPercent:maximum});
    const phase=policy.phases.find(p=>x.ddPercent<=p.ddMaxPercent);
    return ok(phase.id,unit,parameterWarnings(['P-03']),{phase:phase.id,phaseInfo:phase,compulsoryClose:false,ddPercent:x.ddPercent});
  }
  function resolvePhaseReturnWithHysteresis(input){
    const x=input||{},current=resolveAccountPhase(x);if(current.status!=='OK')return current;
    if(!validPhase(x.previousPhase))return invalid('Fase anterior deve ser identificada para avaliar retorno.','PHASE');
    if(current.value>=x.previousPhase)return ok(current.value,'PHASE',current.findings,{phase:current.value,phaseInfo:phaseInfo(current.value),transition:current.value>x.previousPhase?'IMMEDIATE':'UNCHANGED',restoresPrunedPositions:false});
    const margin=param('P-04a'),count=param('P-04b');
    const closes=x.confirmedH4Closes;
    const since=typeof x.since==='string'?Date.parse(x.since):NaN;
    const pending=[];
    if(!Number.isFinite(since))pending.push('since');
    if(!Array.isArray(closes))pending.push('confirmedH4Closes');
    let selected=x.previousPhase;
    if(!pending.length){
      const valid=closes.every(c=>c&&c.timeframe==='H4'&&nonnegative(c.ddPercent)&&typeof c.closedAt==='string'&&Number.isFinite(Date.parse(c.closedAt)));
      if(!valid)pending.push('confirmedH4Closes.validity');
      const ordered=valid?closes.filter(c=>Date.parse(c.closedAt)>since).slice().sort((a,b)=>Date.parse(a.closedAt)-Date.parse(b.closedAt)):[];
      const conflict=ordered.some((c,i)=>i>0&&Date.parse(c.closedAt)===Date.parse(ordered[i-1].closedAt)&&c.ddPercent!==ordered[i-1].ddPercent);
      if(conflict)pending.push('confirmedH4Closes.conflictingValues');
      const unique=conflict?[]:ordered.filter((c,i)=>i===0||Date.parse(c.closedAt)!==Date.parse(ordered[i-1].closedAt));
      // Most recent actual closes; elapsed time and old favorable closes do not
      // establish confirmation. Crossing several return thresholds tests each.
      const recent=unique.slice(-count);
      for(let n=current.value;n<x.previousPhase;n++){
        const threshold=phaseInfo(n).ddMaxPercent-margin;
        if(x.ddPercent<=threshold&&recent.length===count&&recent.every(c=>c.ddPercent<=threshold)){selected=n;break;}
      }
    }
    const findings=parameterWarnings(['P-04a','P-04b']);
    if(selected===x.previousPhase)findings.push(finding('HYSTERESIS_HELD','Fase mantida: margem e fechamento H4 posterior ainda não demonstrados.','PDF p32 Art4.1 §5'));
    return ok(selected,'PHASE',findings,{phase:selected,phaseInfo:phaseInfo(selected),rawPhase:current.value,transition:selected<x.previousPhase?'CONFIRMED_RETURN':'HELD',missingEvidence:pending,restoresPrunedPositions:false});
  }
  function resolveActiveGridPhase(input){
    const x=input||{};
    if(x.structureKnown!==true||!validPhase(x.declaredPhase))return absent(['declaredPhase','structureKnown'],'PHASE');
    if(!validPhase(x.accountPhase))return absent(['accountPhase'],'PHASE');
    return ok(x.declaredPhase,'PHASE',[],{accountPhase:x.accountPhase,limitsFromPhase:x.accountPhase,maxLeverage:phaseInfo(x.accountPhase).maxLeverage,diverges:x.declaredPhase!==x.accountPhase,doesNotAuthorizeReconstruction:true});
  }
  function computeVRM(input){
    const x=input||{};const error=requireNumbers(x,['atrShort','atrLong'],'RATIO');if(error)return error;
    if(!nonnegative(x.atrShort)||!positive(x.atrLong))return invalid('ATR curto deve ser não negativo e ATR longo positivo.','RATIO');
    return ok(x.atrShort/x.atrLong,'RATIO',parameterWarnings(['P-11']),{periods:param('P-11'),recalculationPeriodicity:'PENDING'});
  }
  function resolveVRMRegime(input){
    const x=input||{},error=requireNumbers(x,['vrm'],'REGIME',nonnegative);if(error)return error;
    const t=param('P-12a'),limits=param('P-12b');
    const regime=x.vrm<t.normalBelow?'NORMAL':(x.vrm<=t.highAbove?'TRANSITION':'HIGH');
    const leverage=regime==='NORMAL'?limits.normal:(regime==='TRANSITION'?limits.transition:limits.high);
    return ok(regime,'REGIME',parameterWarnings(['P-12a']),{regime,maxLeveragePerOrder:leverage,amplificationForbidden:regime==='TRANSITION',recalculationPeriodicity:'PENDING'});
  }
  function computeEffectiveLeverageLimit(input){
    const x=input||{};if(!validPhase(x.phase))return absent(['phase'],'MULTIPLE_PER_ORDER');
    const vrm=resolveVRMRegime(x);if(vrm.status!=='OK')return result(vrm.status,null,'MULTIPLE_PER_ORDER',vrm.findings);
    if(!Array.isArray(x.otherLimits))return absent(['otherLimits'],'MULTIPLE_PER_ORDER');
    if(!x.otherLimits.every(nonnegative))return invalid('Demais tetos devem ser números não negativos.','MULTIPLE_PER_ORDER');
    const ceiling=Math.min(phaseInfo(x.phase).maxLeverage,vrm.maxLeveragePerOrder,...x.otherLimits);
    return ok(ceiling,'MULTIPLE_PER_ORDER',vrm.findings,{phaseLimit:phaseInfo(x.phase).maxLeverage,vrmLimit:vrm.maxLeveragePerOrder,regime:vrm.value,amplificationForbidden:vrm.amplificationForbidden,executionEligibility:'BLOCKED',notes:['Teto não dimensiona volume nem substitui os três limites de risco.']});
  }
  function computeFinancialRisk(input){
    const x=input||{},unit='ACCOUNT_CURRENCY';
    const error=requireNumbers(x,['entryPrice','stopPrice','volume','contractSize','conversionRate'],unit);if(error)return error;
    const side=typeof x.side==='string'?x.side.toUpperCase():'';
    if(!['BUY','SELL','LONG','SHORT'].includes(side))return invalid('Direção não identificada.',unit);
    if(!positive(x.entryPrice)||!positive(x.stopPrice)||!nonnegative(x.volume)||!positive(x.contractSize)||!positive(x.conversionRate))return invalid('Preço, volume, contrato ou conversão inválidos.',unit);
    if(x.stopValid!==true)return result('NOT_COMPUTABLE',null,unit,[finding('STOP_NOT_VALIDATED','Risco exige stop válido; não presumir validade pelo preenchimento.','PDF p69 Art8.4 §1','BLOCKING')]);
    const adverseDistance=['BUY','LONG'].includes(side)?x.entryPrice-x.stopPrice:x.stopPrice-x.entryPrice;
    return ok(Math.max(0,adverseDistance)*x.volume*x.contractSize*x.conversionRate,unit,[],{basis:'EXECUTION_TO_VALID_STOP',ignoresCurrentMarketPrice:true});
  }
  function sumPositionRisk(positions){
    if(!Array.isArray(positions))return absent(['positions'],'ACCOUNT_CURRENCY');
    let value=0;for(const p of positions){const r=computeFinancialRisk(p);if(r.status!=='OK')return r;value+=r.value;}
    return ok(value,'ACCOUNT_CURRENCY');
  }
  function pendingRisk(orders){
    if(!Array.isArray(orders))return absent(['pendingOrders'],'ACCOUNT_CURRENCY');
    let total=0;const groups=Object.create(null),findings=[];
    for(const order of orders){
      if(!order||typeof order.active!=='boolean')return absent(['pendingOrder.active'],'ACCOUNT_CURRENCY');
      if(!order.active)continue;
      if(order.kind==='REDUCING')continue;
      if(order.kind!=='AMPLIFYING')return invalid('Classificar ordem pendente como ampliadora ou redutora.','ACCOUNT_CURRENCY');
      const r=computeFinancialRisk(order);if(r.status!=='OK')return r;
      if(typeof order.exclusiveGroup==='string'&&order.exclusiveGroup){
        const list=groups[order.exclusiveGroup]||(groups[order.exclusiveGroup]=[]);
        list.push({risk:r.value,verified:order.exclusivityVerified===true&&typeof order.exclusivityEvidence==='string'&&order.exclusivityEvidence.trim().length>0});
      }else total+=r.value;
    }
    Object.keys(groups).forEach(key=>{
      const list=groups[key],verified=list.every(x=>x.verified);
      total+=verified?Math.max(...list.map(x=>x.risk)):list.reduce((a,x)=>a+x.risk,0);
      if(!verified)findings.push(finding('EXCLUSIVITY_UNPROVEN','Riscos pendentes somados: exclusividade sem garantia auditável.','PDF p72 Art8.4 §16'));
    });
    return ok(total,'ACCOUNT_CURRENCY',findings);
  }
  function computeOpenAggregatePhaseRisk(input){
    const x=input||{},open=sumPositionRisk(x.positions);if(open.status!=='OK')return open;
    const pending=pendingRisk(x.pendingOrders);if(pending.status!=='OK')return pending;
    return ok(open.value+pending.value,'ACCOUNT_CURRENCY',pending.findings,{openRisk:open.value,pendingRisk:pending.value,source:'PDF p70 Art8.4 §9',annexD11OmissionPreserved:true});
  }
  function computeCommittedOperationRisk(input){
    const x=input||{},aggregate=computeOpenAggregatePhaseRisk(x);if(aggregate.status!=='OK')return aggregate;
    if(!Array.isArray(x.realizedResults)||!Array.isArray(x.costs))return absent(['realizedResults','costs'],'ACCOUNT_CURRENCY');
    if(!x.realizedResults.every(finite)||!x.costs.every(finite))return invalid('Resultados e custos devem ser valores assinados, na moeda da conta.','ACCOUNT_CURRENCY');
    const losses=x.realizedResults.reduce((a,v)=>a+Math.max(0,-v),0),costs=x.costs.reduce((a,v)=>a+Math.max(0,-v),0);
    return ok(aggregate.value+losses+costs,'ACCOUNT_CURRENCY',aggregate.findings,{realizedLosses:losses,negativeCosts:costs,openRisk:aggregate.openRisk,pendingRisk:aggregate.pendingRisk,positiveAmountsDoNotOffset:true});
  }
  function computeAdmissionRisk(input){
    const x=input||{},financial=computeFinancialRisk(x);
    if(financial.status!=='OK')return financial;
    const error=requireNumbers(x,['si'],'SI_PERCENT',positive);if(error)return error;
    if(!validPhase(x.phase))return absent(['phase'],'SI_PERCENT');
    return blockedParameters(['P-14','P-18','P-17'],{financialRisk:financial.value,financialRiskPercent:financial.value/x.si*100,phase:x.phase,admissionBasis:'PRE_EXECUTION_SNAPSHOT',canRecord:true,executionEligibility:'BLOCKED'});
  }
  function computePrudentialCapacity(input){
    const x=input||{},unit='ACCOUNT_CURRENCY';
    const error=requireNumbers(x,['si','ddPercent','committedRisk'],unit);if(error)return error;
    if(!positive(x.si)||!nonnegative(x.ddPercent)||!nonnegative(x.committedRisk))return invalid('SI/DD/risco comprometido inválidos.',unit);
    const ceiling=Math.max(0,(param('P-03')-x.ddPercent)/100*x.si),remaining=Math.max(0,ceiling-x.committedRisk);
    const findings=[finding('GAP_BUFFER_PENDING','Sem reserva quantitativa adicional homologada para gap/deslizamento; risco residual não coberto.','PDF p71 Art8.4 §13-A')];
    return result(x.ddPercent>=param('P-03')?'BLOCKED':'OK',remaining,unit,findings,{ceiling,committedRisk:x.committedRisk,bufferValue:null,bufferStatus:'PENDING',bufferExcludedByExpressRule:true,executionEligibility:'BLOCKED',traStatus:'PENDING',effectiveAdmissionCapacity:null});
  }
  function computeMinimumStop(input){
    const x=input||{},error=requireNumbers(x,['atr'],'PRICE',nonnegative);if(error)return error;
    const multiple=param('P-20');
    return ok(x.atr*multiple,'PRICE',parameterWarnings(['P-16','P-20']),{multiple,atrPeriod:param('P-16'),timeframe:'H4',technicalAnalysisStillRequired:true});
  }
  function computeStopAtrMultiple(input){
    const x=input||{},error=requireNumbers(x,['stopPercent','atr','currentPrice'],'ATR_MULTIPLE');if(error)return error;
    if(!nonnegative(x.stopPercent)||!positive(x.atr)||!positive(x.currentPrice))return invalid('Stop percentual, ATR e preço atual devem permitir razão válida.','ATR_MULTIPLE');
    const atrPercent=x.atr/x.currentPrice*100,multiple=x.stopPercent/atrPercent;
    return ok(multiple,'ATR_MULTIPLE',parameterWarnings(['P-20']),{atrPercent,minimumMultiple:param('P-20'),meetsMinimum:multiple>=param('P-20'),technicalAnalysisStillRequired:true});
  }
  function computeRootNDiagnostic(input){
    const x=input||{},unit='PRICE',error=requireNumbers(x,['atr','n','f'],unit);
    const extra={diagnosticOnly:true,calculationMode:'USER_DIAGNOSTIC',normativeParameterActivated:false,
      n:finite(x.n)?x.n:null,f:finite(x.f)?x.f:null,timeframe:'H4'};
    if(error)return Object.assign(error,extra);
    if(!nonnegative(x.atr)||!Number.isSafeInteger(x.n)||x.n<=0||!positive(x.f))
      return Object.assign(invalid('ATR deve ser não negativo; N deve ser inteiro positivo de candles H4 e F deve ser positivo.',unit),extra);
    return Object.assign(ok(x.atr*Math.sqrt(x.n)*x.f,unit,[],{atr:x.atr}),extra);
  }
  function computeFCRRequirement(input){
    const x=input||{},error=requireNumbers(x,['capitalNominal'],'ACCOUNT_CURRENCY',positive);if(error)return error;
    const conflicts=[finding('FCR_BASE_CONFLICT','PDF usa capital nominal da Mestre; Anexo usa SI. Cálculo segue o PDF adotado; conflito documental permanece aberto.','PDF p86 Art13.2 §1 / Anexo K01')];
    if(x.si!==undefined&&x.si!==null&&!positive(x.si))return invalid('SI informado deve ser positivo.','ACCOUNT_CURRENCY');
    return ok(x.capitalNominal*param('P-03')/100,'ACCOUNT_CURRENCY',conflicts.concat(parameterWarnings(['P-03'])),{base:x.capitalNominal,baseType:'MASTER_NOMINAL_CAPITAL',ddMaxPercent:param('P-03'),si:x.si===undefined?null:x.si,baseEqualsSI:x.si===undefined||x.si===null?null:x.capitalNominal===x.si,liquidityMaximumDays:param('P-27').maximumDays});
  }
  function computeFEORequirement(input){
    const x=input||{},unit='ACCOUNT_CURRENCY';let observedSixMonthTotal=null;
    if(x.sixMonthExpenses!==undefined){
      if(!Array.isArray(x.sixMonthExpenses)||x.sixMonthExpenses.length!==param('FEO_COVERAGE')||!x.sixMonthExpenses.every(nonnegative))return invalid('Amostra auxiliar deve identificar seis valores mensais reais não negativos.',unit);
      observedSixMonthTotal=x.sixMonthExpenses.reduce((a,v)=>a+v,0);
    }
    const conflict=finding('FEO_HOMOLOGATION_CONFLICT','PDF mantém homologação nominal; Anexo trata percentual como derivado. Apuração registrada não encerra esse conflito.','PDF pp87/88 Art13.3 / Anexo P29');
    if(x.sixMonthExpenseAmount===undefined||x.sixMonthExpenseAmount===null||x.determinationRecorded!==true||x.expensesApproved!==true)return result('PENDING_INPUT',null,unit,[finding('FEO_EXPENSE_DETERMINATION_PENDING','Cobertura de seis meses ainda não apurada/registrada; série histórica não determina automaticamente o próximo período.','PDF pp87/88 Art13.3','BLOCKING'),conflict],{observedSixMonthTotal,coverageMonths:param('FEO_COVERAGE'),governanceStatus:'UNRESOLVED_NOMINAL_HOMOLOGATION'});
    if(!nonnegative(x.sixMonthExpenseAmount))return invalid('Montante apurado deve ser não negativo.',unit);
    if(x.si!==undefined&&x.si!==null&&!positive(x.si))return invalid('SI informado deve ser positivo.',unit);
    return ok(x.sixMonthExpenseAmount,unit,[conflict],{observedSixMonthTotal,coverageMonths:param('FEO_COVERAGE'),derivedPercent:positive(x.si)?x.sixMonthExpenseAmount/x.si*100:null,percentageDeterminesAmount:false,governanceStatus:'UNRESOLVED_NOMINAL_HOMOLOGATION',liquidityMaximumDays:param('P-28').maximumDays});
  }
  function computeReserveStatus(input){
    const x=input||{},r=x.requirement,unit='ACCOUNT_CURRENCY';
    if(!r)return absent(['requirement'],unit);
    if(!['OK','PENDING_INPUT','NOT_COMPUTABLE','BLOCKED'].includes(r.status)||!Array.isArray(r.findings))return invalid('Resultado do requisito inválido.',unit);
    if(r.status!=='OK')return result(r.status,null,unit,r.findings);
    if(!nonnegative(r.value))return invalid('Montante exigido não é um valor calculável.',unit);
    const error=requireNumbers(x,['constituted','liquidityDays'],unit,nonnegative);if(error)return error;
    if(!['FCR','FEO'].includes(x.fund))return invalid('Identificar o fundo FCR ou FEO.',unit);
    const maximum=x.fund==='FCR'?param('P-27').maximumDays:param('P-28').maximumDays;
    const verified=x.verificationRecorded===true&&typeof x.verifiedAt==='string'&&Number.isFinite(Date.parse(x.verifiedAt));
    const deficit=Math.max(0,r.value-x.constituted),surplus=Math.max(0,x.constituted-r.value),liquid=x.liquidityDays<=maximum;
    const value={required:r.value,constituted:x.constituted,deficit,surplus,fullyConstituted:deficit===0,liquidityCompliant:liquid,verificationRecorded:verified};
    const findings=r.findings.slice();
    if(deficit>0)findings.push(finding('RESERVE_DEFICIT','Reserva não integralmente constituída.','PDF pp86/88/91','BLOCKING'));
    if(!liquid)findings.push(finding('RESERVE_LIQUIDITY','Liquidez excede o limite documental.','Anexo P27/P28','BLOCKING'));
    if(!verified)findings.push(finding('RESERVE_VERIFICATION_PENDING','Verificação em ata não demonstrada.','PDF pp86/88 Art13.2 §5 e13.3 §9','BLOCKING'));
    return result(deficit>0||!liquid||!verified?'BLOCKED':'OK',value,unit,findings,{doesNotAuthorizeCycle:true,verificationStatus:verified?'RECORDED':'PENDING'});
  }
  function computeReplicationFirewall(input){
    const x=input||{},unit='FACTOR';
    const available=nonnegative(x.maxLossPercent)&&nonnegative(x.safetyMarginPercent);
    const literalBound=available?(x.maxLossPercent-x.safetyMarginPercent)/param('P-03'):null;
    const theoreticalCeiling=available&&literalBound>=0?literalBound:null;
    const findings=[finding('P-30_PENDING','Fatores satélites inexistentes normativamente até validações, homologação e incorporação; cadastro não autoriza replicação.','PDF p56 Art6.4 §1','BLOCKING')];
    if(available&&literalBound<0)findings.push(finding('NO_ADMISSIBLE_REPLICATION_RANGE','A margem supera MaxLoss: não existe fator não negativo que satisfaça a desigualdade.','PDF p56 Art6.4 §1','BLOCKING'));
    return result('BLOCKED',null,unit,findings,{formulaStatus:'DEFINED',literalBound,theoreticalCeiling,
      admissibleRange:theoreticalCeiling===null?null:[0,theoreticalCeiling],
      rangeStatus:!available?'PENDING_INPUT':literalBound<0?'NO_NONNEGATIVE_SOLUTION':literalBound===0?'ZERO_ONLY_DIAGNOSTIC':'DIAGNOSTIC_ONLY',
      inputsStatus:available?'SUPPLIED_NOT_HOMOLOGATED':'PENDING_INPUT',maxLossPercent:finite(x.maxLossPercent)?x.maxLossPercent:null,safetyMarginPercent:finite(x.safetyMarginPercent)?x.safetyMarginPercent:null,ddMaxPercent:param('P-03'),replicationAllowed:false});
  }
  function computeSizingTrace(){
    // PDF p66 Art8.2 §2 is ordered and unidirectional. With no applicable
    // admission limit, there is no first volume to reduce at later stages.
    // A caller-supplied lot or limit cannot fill the active registry's gap.
    const pending=['P-14','P-18'].filter(id=>param(id)===null);
    const firstFindings=pending.length?pending.map(id=>finding(id+'_PENDING',id+' ausente: o volume inicial por risco não é calculável.',policy.get(id).hostNorm,'BLOCKING')):
      [finding('ADMISSION_SIZING_NOT_ESTABLISHED','A aplicação do limite por ordem exige contrato normativo validado; esta revisão não ativa dimensionamento.','PDF p66 Art8.2 §2 I','BLOCKING')];
    const steps=[
      {id:'ADMISSION_RISK',label:'Volume pelo limite de risco, stop e equivalência financeira'},
      {id:'PHASE_LEVERAGE',label:'Redução pelo teto de alavancagem da fase'},
      {id:'VOLATILITY_REGIME',label:'Redução pelo regime de volatilidade'},
      {id:'PRO_FORMA_BUDGET_AND_AGGREGATE',label:'Risco comprometido/orçamento e agregado/TRA pro forma'}
    ].map((step,index)=>({...step,ordinal:index+1,status:index===0?'BLOCKED':'NOT_EVALUATED',value:null,unit:'LOTS',
      findings:index===0?firstFindings:[finding('PREVIOUS_SIZING_STEP_UNAVAILABLE','Etapa dependente não avaliada: o volume anterior não foi apurado.','PDF p66 Art8.2 §§2–3','BLOCKING')]}));
    return result('BLOCKED',null,'LOTS',firstFindings,{steps,finalVolume:null,limitingStep:null,
      blockedAtStep:'ADMISSION_RISK',executionEligibility:'BLOCKED',canRecord:true,
      institutionMinimumCheck:{status:'NOT_EVALUATED',value:null,roundingUpAllowed:false,source:'PDF p66 Art8.2 §5'},
      source:'PDF p66 Art8.2 §§2–7',scope:'TRACE_OF_BLOCKED_SEQUENCE_NOT_A_VOLUME_RECOMMENDATION'});
  }
  function computePlanningProjection(input){
    // Explicit dependency injection: the adapter supplies the existing JPWFx
    // pure projection. This module does not read current state or write ACTUAL.
    const x=input||{};
    if(typeof x.projector!=='function'||!x.assumptions||typeof x.assumptions!=='object')return absent(['assumptions','projector'],'PLANNING_TIMELINE');
    if(!['PLAN','SCENARIO'].includes(x.mode))return invalid('Projeção exige modo PLAN ou SCENARIO; ACTUAL não é projeção.','PLANNING_TIMELINE');
    try{
      const assumptions=JSON.parse(JSON.stringify(x.assumptions));
      const rows=x.projector(assumptions);
      if(!Array.isArray(rows))return invalid('Adapter JPWFx não devolveu uma série.','PLANNING_TIMELINE');
      return ok(rows,'PLANNING_TIMELINE',[],{mode:x.mode,source:'JPWFx',referenceMonthlyReturn:policy.planning.referenceMonthlyReturn,annualReferenceRange:policy.planning.annualReferenceRange});
    }catch(error){return result('NOT_COMPUTABLE',null,'PLANNING_TIMELINE',[finding('PLANNING_ADAPTER_FAILED','A projeção existente não pôde ser calculada.','docs/architecture/FX-PLANNING.md','BLOCKING')]);}
  }
  return Object.freeze({computeDrawdown,computeGrossNotional,computeLeverage,resolveAccountPhase,resolvePhaseReturnWithHysteresis,resolveActiveGridPhase,computeVRM,resolveVRMRegime,computeEffectiveLeverageLimit,computeFinancialRisk,computeAdmissionRisk,computeCommittedOperationRisk,computeOpenAggregatePhaseRisk,computePrudentialCapacity,computeMinimumStop,computeStopAtrMultiple,computeRootNDiagnostic,computeFCRRequirement,computeFEORequirement,computeReserveStatus,computeReplicationFirewall,computeSizingTrace,computePlanningProjection});
  }
  ns.createEngine=createEngine;
  ns.engine=createEngine(ns.policy);
})(typeof globalThis!=='undefined'?globalThis:window);

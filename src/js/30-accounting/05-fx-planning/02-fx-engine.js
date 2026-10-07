// ============ PLANEJAMENTO FX · MOTOR MATEMÁTICO PURO ============
// Funções determinísticas sem DOM, sem S, sem storage. Todos os valores derivados
// (séries, saldos, variâncias, custo médio, resumo anual) são SEMPRE recalculados
// daqui — nunca persistidos (mesmo princípio do MEI-JP). Precisão: float pleno em
// todo o pipeline; arredondamento só na exibição (04-fx-ui.js).

// ---- Série planejada (baseline OU forecast puro de premissas) ---------------
// Convenção aprovada (2026-08-11): resultado sobre o saldo de ABERTURA; aportes
// depois do resultado. close = open + open*rate + aportes.
// Availability accompanies every financial field. Null is absence, never zero.
function fxTimelineRow(row){
  const fields=['open','rate','profit','personalUsd','propUsd','contributionUsd','close'];
  const overflow=fields.some(k=>typeof row[k]==='number'&&!Number.isFinite(row[k]));
  fields.forEach(k=>{if(typeof row[k]==='number'&&!Number.isFinite(row[k]))row[k]=null;});
  if(overflow){row.status=row.phase==='actual'?'REVIEW_REQUIRED':'BLOCKED';row.reasonCode='NON_FINITE_RESULT';row.reason='Resultado não finito; confira as premissas e a base.';row.blockedBy=row.month;}
  row.availability=Object.fromEntries(fields.map(k=>[k,typeof row[k]==='number'&&Number.isFinite(row[k])]));
  row.available=fields.filter(k=>k!=='rate').every(k=>row.availability[k]);
  return row;
}
function fxPlannedTimeline(assumptions){
  const start=fxMonthKey(assumptions.startMonth);
  const horizon=Math.max(FX_HORIZON_MIN,Math.min(FX_HORIZON_MAX,Math.round(fxNum(assumptions.horizonMonths))));
  if(!start) return [];
  const rows=[]; let open=fxInputFinite(assumptions.initialBalanceUsd)?+assumptions.initialBalanceUsd:null,blockedBy='';
  for(let t=0;t<horizon;t++){
    const month=fxAddMonths(start,t),absent=fxMonthIsAbsent(assumptions,month);
    const rate=fxResolveRate(assumptions,month),contrib=fxPlannedContribution(assumptions,month);
    const profit=open!==null&&rate!==null?open*rate:null;
    const close=profit!==null&&contrib.totalUsd!==null?open+profit+contrib.totalUsd:null;
    const reasonCode=absent?'FORECAST_ABSENT':open===null?'PREVIOUS_MONTH_UNAVAILABLE':rate===null||contrib.totalUsd===null?'PREMISE_INVALID':'';
    rows.push(fxTimelineRow({month,phase:'planned',status:absent?'ABSENT':reasonCode?'BLOCKED':'PROJECTED',open,rate,profit,
      personalUsd:contrib.personalUsd,propUsd:contrib.propUsd,contributionUsd:contrib.totalUsd,close,
      reasonCode,reason:absent?'Previsão retirada deste mês.':reasonCode?'Encadeamento indisponível desde '+(blockedBy||month)+'.':'',blockedBy:reasonCode?(blockedBy||month):''}));
    if(!Number.isFinite(close)&&!blockedBy)blockedBy=month;
    open=Number.isFinite(close)?close:null;
  }
  return rows;
}

// ---- Aportes realizados por mês (derivados do ledger cambial) ---------------
function fxContributionsByMonth(contributions){
  const map={};
  (contributions||[]).forEach(c=>{
    const month=fxMonthKey(c.month); if(!month||!(fxNum(c.usdAmount)>0)) return;
    const slot=map[month]||(map[month]={personalUsd:0,propUsd:0,totalUsd:0});
    const usd=+c.usdAmount;
    if(c.source==='prop') slot.propUsd+=usd; else slot.personalUsd+=usd;
    slot.totalUsd+=usd;
  });
  return map;
}

// ---- Série realizada --------------------------------------------------------
// Percorre meses CONTÍGUOS fechados a partir do início do plano. A âncora do
// primeiro mês é o saldo inicial do BASELINE (parâmetro do plano — decisão 3).
// Álgebra idêntica ao MEI (R_aj = (V_t − V_{t−1} − F_t)/V_{t−1}):
//   entrada 'rate' → profit = open*rate;  entrada 'usd' → rate = profit/open.
// O campo não informado é DERIVADO e marcado como tal (derivedField).
function fxActualRow(month,rec,open,contrib){
  const inputType=rec.inputType==='usd'?'usd':'rate';
  const profit=inputType==='usd'&&fxInputFinite(rec.profitUsd)?+rec.profitUsd:
    inputType==='rate'&&open!==null&&fxInputFinite(rec.returnRate)?open*+rec.returnRate:null;
  const rate=inputType==='rate'&&fxInputFinite(rec.returnRate)?+rec.returnRate:
    profit!==null&&open>0?profit/open:null;
  const close=open!==null&&profit!==null?open+profit+contrib.totalUsd:null;
  return fxTimelineRow({month,phase:'actual',status:'FINALIZED',open,rate,profit,
    personalUsd:contrib.personalUsd,propUsd:contrib.propUsd,contributionUsd:contrib.totalUsd,close,
    inputType,derivedField:inputType==='usd'?'rate':'usd',valuationFxRate:rec.valuationFxRate||null,
    notes:rec.notes||'',source:rec.source||null,closedAt:rec.closedAt||'',reasonCode:'',reason:'',blockedBy:'',
    confirmedSnapshot:rec.confirmedSnapshot?structuredClone(rec.confirmedSnapshot):null});
}
function fxActualTimeline(plan,{asOf}={}){
  const start=fxMonthKey(plan.baseline.startMonth);if(!start)return [];
  const byMonth=fxContributionsByMonth(plan.contributions),rows=[];
  let open=fxInputFinite(plan.baseline.initialBalanceUsd)?+plan.baseline.initialBalanceUsd:null;
  for(let t=0;t<plan.baseline.horizonMonths;t++){
    const month=fxAddMonths(start,t),rec=(plan.actuals||{})[month];
    if(!rec||(rec.closureStatus||'FINALIZED')!=='FINALIZED'||open===null||fxValidateActualInput(rec).length)break;
    if(asOf&&String(rec.closedAt||'')>String(asOf))break;
    const row=fxActualRow(month,rec,open,byMonth[month]||{personalUsd:0,propUsd:0,totalUsd:0});
    if(row.close===null||!Number.isFinite(row.close))break;
    rows.push(row);open=row.close;
  }
  return rows;
}
function fxNextOpenMonth(plan){
  if(!plan||!plan.baseline)return '';
  const idx=fxActualTimeline(plan).length;
  return idx>=plan.baseline.horizonMonths?'':fxAddMonths(plan.baseline.startMonth,idx);
}

// Includes all recorded actuals, even after reopening. An unconfirmed actual
// never becomes a forecast, and its dependent values never gain implied validity.
function fxForecastTimeline(plan,{assumptions,asOf,rebases}={}){
  const premises=assumptions||plan.current,start=fxMonthKey(plan.baseline.startMonth);if(!start)return [];
  const byMonth=fxContributionsByMonth(plan.contributions),anchors=rebases||plan.rebases||[],rows=[];
  let open=fxInputFinite(plan.baseline.initialBalanceUsd)?+plan.baseline.initialBalanceUsd:null;
  let blockedBy='',reviewBlocked=false,actualContiguous=true;
  for(let t=0;t<plan.baseline.horizonMonths;t++){
    const month=fxAddMonths(start,t);
    let rec=(plan.actuals||{})[month];
    if(rec&&asOf&&String(rec.closedAt||'')>String(asOf))rec=null;
    if(rec){
      const status=rec.closureStatus||'FINALIZED',contrib=byMonth[month]||{personalUsd:0,propUsd:0,totalUsd:0};
      const row=fxActualRow(month,rec,actualContiguous?open:null,contrib);
      if(status!=='FINALIZED'||!actualContiguous||open===null||fxValidateActualInput(rec).length){
        row.status=status==='REOPENED'?'REOPENED':'REVIEW_REQUIRED';
        row.reasonCode=status==='REOPENED'?'ACTUAL_REOPENED':'ACTUAL_BASE_REVIEW';
        row.reason=status==='REOPENED'?'Realizado reaberto: exige conferência e nova finalização.':'Base em revisão: reconfirme cronologicamente após '+(blockedBy||month)+'.';
        row.blockedBy=blockedBy||month;
        row.profit=rec.inputType==='usd'&&fxInputFinite(rec.profitUsd)?+rec.profitUsd:null;
        row.rate=rec.inputType!=='usd'&&fxInputFinite(rec.returnRate)?+rec.returnRate:null;
        row.close=null;row.input=fxNormalizeActual(rec);fxTimelineRow(row);
        if(!blockedBy)blockedBy=month;open=null;reviewBlocked=true;actualContiguous=false;
      }else{open=row.close;}
      rows.push(row);continue;
    }
    actualContiguous=false;
    const anchor=anchors.filter(a=>a.month===month).slice(-1)[0];
    if(!reviewBlocked&&anchor&&fxInputFinite(anchor.openingBalanceUsd)&&+anchor.openingBalanceUsd>=0){open=+anchor.openingBalanceUsd;blockedBy='';}
    const absent=fxMonthIsAbsent(premises,month),rate=fxResolveRate(premises,month),contrib=fxPlannedContribution(premises,month);
    const profit=open!==null&&rate!==null?open*rate:null;
    const close=profit!==null&&contrib.totalUsd!==null?open+profit+contrib.totalUsd:null;
    const reasonCode=absent?'FORECAST_ABSENT':reviewBlocked?'ACTUAL_BASE_REVIEW':open===null?'PREVIOUS_MONTH_UNAVAILABLE':rate===null||contrib.totalUsd===null?'PREMISE_INVALID':'';
    rows.push(fxTimelineRow({month,phase:'forecast',status:absent?'ABSENT':reasonCode?'BLOCKED':'PROJECTED',open,rate,profit,
      personalUsd:contrib.personalUsd,propUsd:contrib.propUsd,contributionUsd:contrib.totalUsd,close,
      reasonCode,reason:absent?'Previsão retirada deste mês.':reasonCode?'Encadeamento indisponível desde '+(blockedBy||month)+'.':'',blockedBy:reasonCode?(blockedBy||month):''}));
    if(!Number.isFinite(close)&&!blockedBy)blockedBy=month;
    open=Number.isFinite(close)?close:null;
  }
  return rows;
}
function fxMonthlyTimeline(plan,options={}){return fxForecastTimeline(plan,options);}
// Forecast como era numa revisão anterior: usa o snapshot preservado e apenas os
// meses fechados até a data da revisão (closedAt ≤ supersededAt). Meses editados
// depois são reconstrução aproximada — sinalizado na interface, não no motor.
function fxForecastAtRevision(plan,revisionIndex){
  const rev=(plan.revisions||[])[revisionIndex];
  if(!rev) return null;
  if(rev.calculationSnapshot){
    const snap=rev.calculationSnapshot;
    return fxForecastTimeline({...plan,actuals:snap.actuals,contributions:snap.contributions,rebases:snap.rebases||[]},{assumptions:rev.snapshot});
  }
  return fxForecastTimeline(plan,{assumptions:rev.snapshot,asOf:rev.supersededAt});
}

// ---- Comparações (variância) -----------------------------------------------
// Realizado × Baseline, Realizado × Forecast anterior, Forecast atual × Baseline
// (requisito adicional). Nunca julga qualidade de execução — descreve trajetória.
function fxVarianceRows(seriesA,seriesB){
  const byMonth={};(seriesB||[]).forEach(r=>{byMonth[r.month]=r;});
  return (seriesA||[]).map(a=>{
    const b=byMonth[a.month];if(!b)return null;
    const available=Number.isFinite(a.close)&&Number.isFinite(b.close);
    const diffUsd=available?a.close-b.close:null;
    return {month:a.month,aClose:a.close,bClose:b.close,diffUsd,
      diffPct:available&&b.close!==0?diffUsd/b.close:null,
      rateDiff:Number.isFinite(a.rate)&&Number.isFinite(b.rate)?a.rate-b.rate:null,
      contributionDiffUsd:Number.isFinite(a.contributionUsd)&&Number.isFinite(b.contributionUsd)?a.contributionUsd-b.contributionUsd:null,
      available,reason:available?'':'Comparação indisponível: uma das bases está ausente ou em revisão.'};
  }).filter(Boolean);
}

// ---- Custo médio do dólar (média ponderada) --------------------------------
// câmbioMédio = Σ BRL investido / Σ USD adquirido — NUNCA média aritmética das
// cotações. Só entram transações affectsFxCostBasis:true (aquisições BRL→USD);
// créditos USD-nativos (Prop Firm) jamais alteram o custo histórico.
function fxCostBasis(contributions){
  let totalBrl=0, totalUsd=0, lastRate=null, lastMonth='';
  (contributions||[]).forEach(c=>{
    if(!c.affectsFxCostBasis) return;
    const usd=fxNum(c.usdAmount), rate=fxNum(c.acquisitionFxRate);
    if(!(usd>0&&rate>0)) return;
    totalBrl+=usd*rate; totalUsd+=usd;
    const stamp=fxMonthKey(c.month)+'|'+String(c.createdAt||'');
    if(stamp>=lastMonth){ lastMonth=stamp; lastRate=rate; }
  });
  return {totalBrlInvested:totalBrl, totalUsdAcquired:totalUsd,
    weightedAverageFx:totalUsd>0?totalBrl/totalUsd:null, lastAcquisitionFx:lastRate};
}

// ---- Resumo anual (derivado das datas — nunca blocos hardcoded) ------------
function fxAnnualSummary(rows){
  const years={};const order=[];
  (rows||[]).forEach(r=>{
    const y=fxYearOf(r.month);if(!y)return;
    if(!years[y]){years[y]={year:y,open:r.open,close:r.close,profitUsd:0,personalUsd:0,propUsd:0,
      contributionUsd:0,growthFactor:1,months:0,availableMonths:0,phases:{planned:0,actual:0,forecast:0}};order.push(y);}
    const acc=years[y];acc.close=r.close;acc.months++;
    const complete=['open','close','profit','personalUsd','propUsd','contributionUsd','rate'].every(k=>Number.isFinite(r[k]))&&(!r.status||['PROJECTED','FINALIZED'].includes(r.status));
    if(complete){acc.availableMonths++;acc.profitUsd+=r.profit;acc.personalUsd+=r.personalUsd;acc.propUsd+=r.propUsd;acc.contributionUsd+=r.contributionUsd;acc.growthFactor*=1+r.rate;}
    if(r.phase==='scenario'&&acc.phases.scenario==null)acc.phases.scenario=0;
    if(acc.phases[r.phase]!=null)acc.phases[r.phase]++;
  });
  return order.map(y=>{
    const a=years[y],complete=a.availableMonths===a.months;
    const subtotal={profitUsd:a.profitUsd,personalUsd:a.personalUsd,propUsd:a.propUsd,contributionUsd:a.contributionUsd};
    return {...a,profitUsd:complete?a.profitUsd:null,personalUsd:complete?a.personalUsd:null,propUsd:complete?a.propUsd:null,
      contributionUsd:complete?a.contributionUsd:null,growthFactor:complete?a.growthFactor:null,composedReturn:complete?a.growthFactor-1:null,
      coverage:complete?'COMPLETE':'PARTIAL',available:complete,subtotal:complete?null:subtotal,
      reason:complete?'':'Resumo parcial: '+a.availableMonths+' de '+a.months+' meses calculáveis.'};
  });
}
// Agregação cambial por ano sobre o ledger de aquisições.
function fxAnnualFxSummary(contributions){
  const years={}; const order=[];
  (contributions||[]).forEach(c=>{
    if(!c.affectsFxCostBasis) return;
    const usd=fxNum(c.usdAmount), rate=fxNum(c.acquisitionFxRate);
    if(!(usd>0&&rate>0)) return;
    const y=fxYearOf(c.month); if(!y) return;
    if(!years[y]){ years[y]={year:y,brlInvested:0,usdAcquired:0}; order.push(y); }
    years[y].brlInvested+=usd*rate; years[y].usdAcquired+=usd;
  });
  return order.sort().map(y=>{
    const a=years[y];
    return {...a, weightedAverageFx:a.usdAcquired>0?a.brlInvested/a.usdAcquired:null};
  });
}

// ---- Visão consolidada ------------------------------------------------------
// Estado calculável completo para a interface: séries, posição atual, desvios e
// custo cambial. Reservas NÃO são calculadas aqui: FCR/FEO vêm exclusivamente de
// reserveRequirementsCalc (10-domain/07) com fontes canônicas — a ponte de estado
// (03-fx-state.js) monta esse painel para não duplicar fonte normativa.
function fxOverview(plan){
  const baseline=fxPlannedTimeline(plan.baseline);
  const actual=fxActualTimeline(plan);
  const forecast=fxForecastTimeline(plan);
  const lastActual=actual.length?actual[actual.length-1]:null;
  const baselineAtLast=lastActual?baseline.find(r=>r.month===lastActual.month)||null:null;
  const unresolvedActuals=Object.keys(plan.actuals||{}).filter(m=>!actual.some(r=>r.month===m));
  const totals=actual.reduce((acc,r)=>{acc.personalUsd+=r.personalUsd;acc.propUsd+=r.propUsd;acc.profitUsd+=r.profit;return acc;},
    {personalUsd:0,propUsd:0,profitUsd:0});
  const cost=fxCostBasis(plan.contributions);
  return {
    baseline, actual, forecast, monthlyRows:forecast,
    coverage:unresolvedActuals.length?'PARTIAL':'COMPLETE',unresolvedActuals,
    lastConfirmedBalanceUsd:lastActual?lastActual.close:fxNum(plan.baseline.initialBalanceUsd),
    lastClosedMonth:lastActual?lastActual.month:'',
    nextOpenMonth:fxNextOpenMonth(plan),
    currentBalanceUsd:unresolvedActuals.length?null:lastActual?lastActual.close:fxNum(plan.baseline.initialBalanceUsd),
    baselineBalanceAtLastClose:baselineAtLast?baselineAtLast.close:null,
    deviationUsd:(!unresolvedActuals.length&&lastActual&&baselineAtLast)?lastActual.close-baselineAtLast.close:null,
    deviationPct:(!unresolvedActuals.length&&lastActual&&baselineAtLast&&baselineAtLast.close!==0)?(lastActual.close-baselineAtLast.close)/baselineAtLast.close:null,
    contributedPersonalUsd:unresolvedActuals.length?null:totals.personalUsd,
    contributedPropUsd:unresolvedActuals.length?null:totals.propUsd,
    contributedTotalUsd:unresolvedActuals.length?null:totals.personalUsd+totals.propUsd,
    realizedProfitUsd:unresolvedActuals.length?null:totals.profitUsd,
    confirmedSubtotal:unresolvedActuals.length?{...totals}:null,
    costBasis:cost,
    varianceActualVsBaseline:fxVarianceRows(actual,baseline),
    varianceForecastVsBaseline:fxVarianceRows(forecast,baseline)
  };
}

// Namespace público (padrão JPWGalton): uma única superfície global para testes
// e para as camadas de estado/UI.
window.JPWFx={
  model:{fxMonthKey,fxMonthIndex,fxMonthFromIndex,fxAddMonths,fxYearOf,
    fxNormalizeAssumptions,fxValidateAssumptions,fxResolveRate,fxPlannedContribution,fxMonthIsAbsent,
    fxNormalizeActual,fxValidateActualInput,fxNormalizeContribution,fxValidateContribution,
    fxCreatePlan,fxReviseAssumptions,FX_HORIZON_MIN,FX_HORIZON_MAX},
  engine:{fxPlannedTimeline,fxActualTimeline,fxForecastTimeline,fxMonthlyTimeline,fxTimelineRow,fxForecastAtRevision,
    fxNextOpenMonth,fxContributionsByMonth,fxVarianceRows,fxCostBasis,
    fxAnnualSummary,fxAnnualFxSummary,fxOverview}
};

// Scenario uses live ACTUAL but its own future assumptions and explicit anchors.
// Neither computing nor selecting this view writes the plan or actual records.
function fxScenarioTimeline(plan,scenario){
  return fxForecastTimeline(plan,{assumptions:scenario.assumptions,rebases:scenario.rebases||[]})
    .map(r=>r.phase==='actual'?r:{...r,phase:'scenario'});
}
window.JPWFx.engine.fxScenarioTimeline=fxScenarioTimeline;

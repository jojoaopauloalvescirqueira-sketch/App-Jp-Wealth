// ============ PLANEJAMENTO FX · MOTOR MATEMÁTICO PURO ============
// Funções determinísticas sem DOM, sem S, sem storage. Todos os valores derivados
// (séries, saldos, variâncias, custo médio, resumo anual) são SEMPRE recalculados
// daqui — nunca persistidos (mesmo princípio do MEI-JP). Precisão: float pleno em
// todo o pipeline; arredondamento só na exibição (04-fx-ui.js).

// ---- Série planejada (baseline OU forecast puro de premissas) ---------------
// Convenção aprovada (2026-08-11): resultado sobre o saldo de ABERTURA; aportes
// depois do resultado. close = open + open*rate + aportes.
function fxPlannedTimeline(assumptions){
  const start=fxMonthKey(assumptions.startMonth);
  const horizon=Math.max(FX_HORIZON_MIN,Math.min(FX_HORIZON_MAX,Math.round(fxNum(assumptions.horizonMonths))));
  if(!start) return [];
  const rows=[]; let open=Math.max(0,fxNum(assumptions.initialBalanceUsd));
  for(let t=0;t<horizon;t++){
    const month=fxAddMonths(start,t);
    const rate=fxResolveRate(assumptions,month);
    const contrib=fxPlannedContribution(assumptions,month);
    const profit=open*rate;
    const close=open+profit+contrib.totalUsd;
    rows.push({month, phase:'planned', open, rate, profit,
      personalUsd:contrib.personalUsd, propUsd:contrib.propUsd,
      contributionUsd:contrib.totalUsd, close});
    open=close;
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
function fxActualTimeline(plan,{asOf}={}){
  const start=fxMonthKey(plan.baseline.startMonth); if(!start) return [];
  const horizon=plan.baseline.horizonMonths;
  const byMonth=fxContributionsByMonth(plan.contributions);
  const rows=[]; let open=Math.max(0,fxNum(plan.baseline.initialBalanceUsd));
  for(let t=0;t<horizon;t++){
    const month=fxAddMonths(start,t);
    const rec=(plan.actuals||{})[month];
    if(!rec) break;                                   // realizado é contíguo desde o início
    if(asOf&&String(rec.closedAt||'')>String(asOf)) break; // reconstrução "como era" (forecast anterior)
    const contrib=byMonth[month]||{personalUsd:0,propUsd:0,totalUsd:0};
    let rate,profit,derivedField;
    if(rec.inputType==='usd'){
      profit=fxNum(rec.profitUsd);
      rate=open>0?profit/open:null;
      derivedField='rate';
    } else {
      rate=fxNum(rec.returnRate);
      profit=open*rate;
      derivedField='usd';
    }
    const close=open+profit+contrib.totalUsd;
    rows.push({month, phase:'actual', open, rate, profit,
      personalUsd:contrib.personalUsd, propUsd:contrib.propUsd,
      contributionUsd:contrib.totalUsd, close,
      inputType:rec.inputType, derivedField,
      valuationFxRate:rec.valuationFxRate||null, notes:rec.notes||''});
    open=close;
  }
  return rows;
}
// Próximo mês aberto para fechamento (mantém a contiguidade da série realizada).
function fxNextOpenMonth(plan){
  const done=fxActualTimeline(plan);
  const idx=done.length;
  return idx>=plan.baseline.horizonMonths?'':fxAddMonths(plan.baseline.startMonth,idx);
}

// ---- Forecast vigente (rolling forecast) -----------------------------------
// Histórico realizado + projeção futura nascida do ÚLTIMO fechamento real, com as
// premissas VIGENTES (plan.current). O baseline nunca participa deste cálculo —
// preservação garantida por construção (requisito Baseline × Forecast × Realizado).
function fxForecastTimeline(plan,{assumptions,asOf}={}){
  const premises=assumptions||plan.current;
  const actual=fxActualTimeline(plan,{asOf});
  const start=fxMonthKey(plan.baseline.startMonth); if(!start) return [];
  const horizon=plan.baseline.horizonMonths;
  const rows=actual.slice();
  let open=actual.length?actual[actual.length-1].close:Math.max(0,fxNum(plan.baseline.initialBalanceUsd));
  for(let t=actual.length;t<horizon;t++){
    const month=fxAddMonths(start,t);
    const rate=fxResolveRate(premises,month);
    const contrib=fxPlannedContribution(premises,month);
    const profit=open*rate;
    const close=open+profit+contrib.totalUsd;
    rows.push({month, phase:'forecast', open, rate, profit,
      personalUsd:contrib.personalUsd, propUsd:contrib.propUsd,
      contributionUsd:contrib.totalUsd, close});
    open=close;
  }
  return rows;
}
// Forecast como era numa revisão anterior: usa o snapshot preservado e apenas os
// meses fechados até a data da revisão (closedAt ≤ supersededAt). Meses editados
// depois são reconstrução aproximada — sinalizado na interface, não no motor.
function fxForecastAtRevision(plan,revisionIndex){
  const rev=(plan.revisions||[])[revisionIndex];
  if(!rev) return null;
  return fxForecastTimeline(plan,{assumptions:rev.snapshot,asOf:rev.supersededAt});
}

// ---- Comparações (variância) -----------------------------------------------
// Realizado × Baseline, Realizado × Forecast anterior, Forecast atual × Baseline
// (requisito adicional). Nunca julga qualidade de execução — descreve trajetória.
function fxVarianceRows(seriesA,seriesB){ // A − B, alinhado por mês
  const byMonth={}; (seriesB||[]).forEach(r=>{byMonth[r.month]=r;});
  return (seriesA||[]).map(a=>{
    const b=byMonth[a.month]; if(!b) return null;
    const diffUsd=a.close-b.close;
    return {month:a.month, aClose:a.close, bClose:b.close, diffUsd,
      diffPct:b.close!==0?diffUsd/b.close:null,
      rateDiff:(Number.isFinite(a.rate)&&Number.isFinite(b.rate))?a.rate-b.rate:null,
      contributionDiffUsd:a.contributionUsd-b.contributionUsd};
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
  const years={}; const order=[];
  (rows||[]).forEach(r=>{
    const y=fxYearOf(r.month); if(!y) return;
    if(!years[y]){ years[y]={year:y, open:r.open, close:r.close, profitUsd:0,
      personalUsd:0, propUsd:0, contributionUsd:0, growthFactor:1, months:0,
      phases:{planned:0,actual:0,forecast:0}}; order.push(y); }
    const acc=years[y];
    acc.close=r.close; acc.profitUsd+=r.profit; acc.personalUsd+=r.personalUsd;
    acc.propUsd+=r.propUsd; acc.contributionUsd+=r.contributionUsd;
    if(Number.isFinite(r.rate)) acc.growthFactor*=(1+r.rate);
    acc.months++; if(acc.phases[r.phase]!=null) acc.phases[r.phase]++;
  });
  return order.map(y=>{
    const a=years[y];
    return {...a, composedReturn:a.growthFactor-1}; // Π(1+r_t) − 1 dos meses do ano
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
  const totals=actual.reduce((acc,r)=>{acc.personalUsd+=r.personalUsd;acc.propUsd+=r.propUsd;acc.profitUsd+=r.profit;return acc;},
    {personalUsd:0,propUsd:0,profitUsd:0});
  const cost=fxCostBasis(plan.contributions);
  return {
    baseline, actual, forecast,
    lastClosedMonth:lastActual?lastActual.month:'',
    nextOpenMonth:fxNextOpenMonth(plan),
    currentBalanceUsd:lastActual?lastActual.close:fxNum(plan.baseline.initialBalanceUsd),
    baselineBalanceAtLastClose:baselineAtLast?baselineAtLast.close:null,
    deviationUsd:(lastActual&&baselineAtLast)?lastActual.close-baselineAtLast.close:null,
    deviationPct:(lastActual&&baselineAtLast&&baselineAtLast.close!==0)?(lastActual.close-baselineAtLast.close)/baselineAtLast.close:null,
    contributedPersonalUsd:totals.personalUsd,
    contributedPropUsd:totals.propUsd,
    contributedTotalUsd:totals.personalUsd+totals.propUsd,
    realizedProfitUsd:totals.profitUsd,
    costBasis:cost,
    varianceActualVsBaseline:fxVarianceRows(actual,baseline),
    varianceForecastVsBaseline:fxVarianceRows(forecast,baseline)
  };
}

// Namespace público (padrão JPWGalton): uma única superfície global para testes
// e para as camadas de estado/UI.
window.JPWFx={
  model:{fxMonthKey,fxMonthIndex,fxMonthFromIndex,fxAddMonths,fxYearOf,
    fxNormalizeAssumptions,fxValidateAssumptions,fxResolveRate,fxPlannedContribution,
    fxNormalizeActual,fxValidateActualInput,fxNormalizeContribution,fxValidateContribution,
    fxCreatePlan,fxReviseAssumptions,FX_HORIZON_MIN,FX_HORIZON_MAX},
  engine:{fxPlannedTimeline,fxActualTimeline,fxForecastTimeline,fxForecastAtRevision,
    fxNextOpenMonth,fxContributionsByMonth,fxVarianceRows,fxCostBasis,
    fxAnnualSummary,fxAnnualFxSummary,fxOverview}
};

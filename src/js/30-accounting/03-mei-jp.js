// ============ MEI-JP · MODELO ESTATÍSTICO INSTITUCIONAL ============
function meiMonthKey(value){
  const key=String(value||'').slice(0,7);
  return /^\d{4}-\d{2}$/.test(key)?key:'';
}
function meiMonthIndex(value){
  const key=meiMonthKey(value); if(!key) return null;
  const [year,month]=key.split('-').map(Number);
  return year*12+month-1;
}
function meiMonthsBetween(from,to){
  const a=meiMonthIndex(from), b=meiMonthIndex(to);
  return a==null||b==null?0:b-a;
}
function meiHistoryAllSorted(){
  return (S.mei&&Array.isArray(S.mei.history)?S.mei.history:[]).slice().sort((a,b)=>{
    const ad=String(a.date||''), bd=String(b.date||'');
    return ad.localeCompare(bd)||String(a.id||'').localeCompare(String(b.id||''));
  });
}
function meiHistorySorted(){
  const seen=new Set();
  return meiHistoryAllSorted().filter(r=>{
    const month=meiMonthKey(r.date);
    if(!month||seen.has(month)||!Number.isFinite(+r.endingEquity)||!(+r.endingEquity>0)) return false;
    seen.add(month); return true;
  });
}
function meiHistoryDiagnostics(){
  const all=meiHistoryAllSorted(), months=new Set(); let invalid=0, duplicates=0;
  all.forEach(r=>{
    const month=meiMonthKey(r.date), valid=month&&Number.isFinite(+r.endingEquity)&&(+r.endingEquity>0);
    if(!valid){ invalid++; return; }
    if(months.has(month)) duplicates++; else months.add(month);
  });
  return {stored:all.length, valid:months.size, invalid, duplicates};
}
// Fluxo líquido externo do registro: F_t = A_t − W_t (aportes − retiradas). Correção 5.
function meiFlow(r){ return (Number.isFinite(+r.contributions)?+r.contributions:0)-(Number.isFinite(+r.withdrawals)?+r.withdrawals:0); }
// Retornos da série patrimonial V_t — revisão metodológica v1.0 (Correções 4 e 5):
//  · retorno SIMPLES ajustado por fluxo (interface):  R_aj = (V_t − V_{t−1} − F_t) / V_{t−1}
//  · retorno LOG ajustado (motor estatístico):        r_aj = ln(1 + R_aj)
//  · lacunas entre registros: mensal-equivalente em log (r_mensal = r_intervalo / meses);
//    com F=0 isso é idêntico à antiga (V_t/V_{t−1})^(1/m) − 1 — sem regressão.
//  · validade: V>0 nas duas pontas E 1+R_aj > 0. Intervalos inválidos são EXCLUÍDOS do
//    cálculo com motivo registrado, mas o registro histórico NUNCA é apagado.
function meiReturnRows(){
  const rows=meiHistorySorted(), out=[];
  for(let i=1;i<rows.length;i++){
    const prev=+rows[i-1].endingEquity, cur=+rows[i].endingEquity, months=meiMonthsBetween(rows[i-1].date,rows[i].date);
    if(!(prev>0 && cur>0 && months>0)) continue; // guarda defensiva (meiHistorySorted já filtra V≤0/duplicados/ordem)
    const flow=meiFlow(rows[i]);
    const adjTotal=(cur-prev-flow)/prev;          // R_aj do intervalo completo
    if(!Number.isFinite(adjTotal) || !(1+adjTotal>0)){
      out.push({from:rows[i-1],to:rows[i],months,flow,valid:false,
        invalidReason:'retorno ajustado ≤ −100% (1+R_aj ≤ 0) — excluído do cálculo, registro preservado'});
      continue;
    }
    const logMonthly=Math.log1p(adjTotal)/months;  // r_aj mensal-equivalente (motor)
    const simpleMonthly=Math.expm1(logMonthly);    // R_aj mensal-equivalente (interface)
    out.push({from:rows[i-1],to:rows[i],months,flow,valid:true,returnPct:simpleMonthly,logReturn:logMonthly});
  }
  return out;
}
function meiValidReturnRows(){ return meiReturnRows().filter(r=>r.valid); }
function meiReturns(){ return meiValidReturnRows().map(r=>r.returnPct); }      // simples ajustado — leitura operacional
function meiLogReturns(){ return meiValidReturnRows().map(r=>r.logReturn); }   // log ajustado — média/variância/σ/GBM
function meiStd(values){
  if(values.length<2) return 0;
  const mean=values.reduce((a,v)=>a+v,0)/values.length;
  return Math.sqrt(values.reduce((a,v)=>a+(v-mean)*(v-mean),0)/(values.length-1));
}
function meiPercentile(values,p){
  if(!values.length) return 0;
  const pos=(values.length-1)*Math.max(0,Math.min(1,p));
  const lo=Math.floor(pos), hi=Math.ceil(pos), t=pos-lo;
  return values[lo]+((values[hi]??values[lo])-values[lo])*t;
}
function meiOutlierDiagnostics(values){
  if(values.length<4) return {count:0, lower:null, upper:null};
  const sorted=values.slice().sort((a,b)=>a-b), q1=meiPercentile(sorted,.25), q3=meiPercentile(sorted,.75), iqr=q3-q1;
  const lower=q1-1.5*iqr, upper=q3+1.5*iqr;
  return {count:values.filter(v=>v<lower||v>upper).length, lower, upper};
}
function calculateMEIHistoricalStats(){
  const rows=meiHistorySorted(), allReturnRows=meiReturnRows(), returnRows=allReturnRows.filter(r=>r.valid);
  // Separação obrigatória (Correção 4): simples ajustado para leitura; LOG ajustado para o motor.
  const simple=returnRows.map(r=>r.returnPct), logs=returnRows.map(r=>r.logReturn), n=logs.length;
  const meanSimple=n?simple.reduce((a,v)=>a+v,0)/n:0;
  const meanLog=n?logs.reduce((a,v)=>a+v,0)/n:0;
  const sigma=meiStd(logs); // σ histórica em retornos LOG ajustados — alimenta a calibração e o GBM
  let peak=0,maxDD=0;
  rows.forEach(r=>{ const e=+r.endingEquity; peak=Math.max(peak,e); if(peak>0) maxDD=Math.max(maxDD,1-e/peak); });
  const outliers=meiOutlierDiagnostics(logs); // sinalização IQR no domínio do motor (log)
  const flowsPresent=rows.some(r=>meiFlow(r)!==0);
  return {
    observations:n, months:rows.length, coveredMonths:returnRows.reduce((sum,r)=>sum+r.months,0),
    mean:meanSimple, meanSimple, meanLog, sigma, annualizedVolatility:sigma*Math.sqrt(12),
    best:n?Math.max(...simple):0, worst:n?Math.min(...simple):0, maxDrawdown:maxDD,
    positive:simple.filter(v=>v>0).length, negative:simple.filter(v=>v<0).length, zero:simple.filter(v=>v===0).length,
    outlierCount:outliers.count, outlierLower:outliers.lower, outlierUpper:outliers.upper,
    excludedReturns:allReturnRows.length-returnRows.length, flowsPresent
  };
}
// Qualidade da amostra (Correção 6) — classificação informativa, nunca certificação.
// Linguagem deliberadamente prudente: "preliminar/limitada", jamais "suficiente/definitiva".
function meiQuality(n){
  if(n<=5) return 'Insuficiente';
  if(n<=11) return 'Preliminar';
  if(n<=23) return 'Limitada';
  if(n<=35) return 'Moderada';
  if(n<=59) return 'Relevante';
  return 'Consolidada';
}
// Rótulos dos estágios (Correção 3) — usados pela configuração e pela simulação.
function meiStageLabel(stage){
  return ({institutional:'Institucional', preliminary:'Institucional + evidência preliminar',
    'hybrid-initial':'Híbrido inicial', 'hybrid-advanced':'Híbrido avançado',
    empirical:'Empírico predominante', unconfigured:'CID não configurado', off:'Desativado'})[stage]||'—';
}
function meiCalibration(profileKey){
  const mei=S.mei||DEFAULTS.mei, pr=getActiveRiskProfile(profileKey);
  const cid=+(mei.cid&&mei.cid[pr.key]);
  const stats=calculateMEIHistoricalStats(), n=stats.observations;
  if(!mei.enabled) return {enabled:false, reason:'O MEI-JP está desativado.', pr, cid, stats, modelStage:'off', sigmaUsed:0, historicalWeight:0};
  if(!(cid>0)) return {enabled:false, reason:'Configure o CID no MEI-JP para habilitar a simulação probabilística.', pr, cid:0, stats, modelStage:'unconfigured', sigmaUsed:0, historicalWeight:0};
  // Transição conservadora (Correção 3): w_h = clip((n − 6)/(36 − 6), 0, 1).
  // 0–5: institucional (w=0) · 6–11: evidência preliminar (w baixo) · 12–23: híbrido inicial ·
  // 24–35: híbrido avançado (histórico relevante, mas NÃO substitui o CID) · ≥36: empírico (w=1).
  const hs=Math.max(2,+mei.hybridStartMonths||6), es=Math.max(hs+1,+mei.empiricalStartMonths||36);
  let historicalWeight=0;
  if(n>=es) historicalWeight=1;
  else if(n>=hs) historicalWeight=Math.max(0,Math.min(1,(n-hs)/(es-hs)));
  let modelStage='institutional';
  if(n>=es) modelStage='empirical';
  else if(n>=24) modelStage='hybrid-advanced';
  else if(n>=12) modelStage='hybrid-initial';
  else if(n>=hs) modelStage='preliminary';
  // Interpolação LINEAR entre CID e σ histórica: decisão institucional de ENGENHARIA da v1.0
  // (simplicidade, transparência, continuidade, auditabilidade) — não é lei estatística.
  // Alternativas documentadas no Manual (cap. 9): combinação por variâncias, shrinkage,
  // bayesiana, ponderação exponencial, modelos por regime. Não implementadas nesta versão.
  const sigmaUsed=cid*(1-historicalWeight)+stats.sigma*historicalWeight;
  return {enabled:true, pr, cid, stats, modelStage, historicalWeight, institutionalWeight:1-historicalWeight, sigmaUsed, historicalSigma:stats.sigma};
}
function hashSeed(seed){
  let h=2166136261; const s=String(seed||'MEI-JP');
  for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619); }
  return h>>>0;
}
function meiRandom(seed){
  let state=(hashSeed(seed)||1)>>>0;
  return ()=>{ state=(state+0x6D2B79F5)>>>0; let t=state; t=Math.imul(t^(t>>>15),t|1); t^=t+Math.imul(t^(t>>>7),t|61); return ((t^(t>>>14))>>>0)/4294967296; };
}
function meiSystemRandom(){ return ()=>Math.random(); }
function meiNormal(random){
  let u=0,v=0; while(u===0) u=random(); while(v===0) v=random();
  return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);
}
function runMEIMonteCarlo(options={}){
  const cal=meiCalibration(options.profileKey);
  if(!cal.enabled) return {...cal, enabled:false, reason:cal.reason};
  const mei=S.mei, allowedCounts=[1000,2000,5000,10000];
  const horizon=Math.max(1,Math.min(120,Math.round(+options.horizonMonths||mei.horizonMonths||60)));
  const configuredCount=allowedCounts.includes(+mei.simulationCount)?+mei.simulationCount:5000;
  const count=allowedCounts.includes(+options.simulationCount)?+options.simulationCount:configuredCount;
  const confidence=Math.max(.5,Math.min(.99,+options.confidenceLevel||mei.confidenceLevel||.90));
  const startingEquity=Math.max(0,+options.startingEquity||0), expectedMonthlyReturn=riskProfileMonthlyTarget(cal.pr), sigma=cal.sigmaUsed;
  if(!(startingEquity>0)) return {...cal, enabled:false, reason:'Informe o saldo inicial para simular.'};
  // GBM sobre a variável patrimonial V_t (não preço de ativo):
  //   V_{t+1} = V_t · exp[(ln(1+r_p) − ½σ_p²) + σ_p·Z_t],  Z_t ~ N(0,1)
  // O drift logarítmico ln(1+r_p) preserva E[V_{t+1}/V_t]−1 = r_p (retorno aritmético do perfil);
  // −½σ² é a correção de Itô. σ_p (cal.sigmaUsed) já vive no domínio LOG: o CID é interpretado
  // como dispersão log-mensal e a σ histórica é calculada sobre retornos LOG ajustados por fluxo —
  // dimensionalmente consistente com o expoente do GBM (Correção 4).
  const logDrift=Math.log1p(expectedMonthlyReturn);
  const fixedSeed=String(options.seed??mei.fixedSeed??'').trim();
  const random=mei.seedMode==='fixed'?meiRandom(fixedSeed||'MEI-JP:v1'):meiSystemRandom();
  const samples=Array.from({length:horizon+1},()=>new Array(count));
  const maxDDs=new Array(count); let belowInitial=0, touchingMDD=0;
  const mdd=cal.pr.mdd;
  for(let p=0;p<count;p++){
    let equity=startingEquity, peak=startingEquity, maxDD=0; samples[0][p]=equity;
    for(let month=1;month<=horizon;month++){
      const z=meiNormal(random);
      const logStep=Math.max(-700,Math.min(700,(logDrift-.5*sigma*sigma)+sigma*z));
      equity*=Math.exp(logStep);
      if(!Number.isFinite(equity)) equity=Number.MAX_VALUE;
      if(equity>peak) peak=equity;
      maxDD=Math.max(maxDD,1-equity/peak); samples[month][p]=equity;
    }
    maxDDs[p]=maxDD; if(equity<startingEquity) belowInitial++; if(maxDD>=mdd) touchingMDD++;
  }
  const outerLo=(1-confidence)/2, outerHi=1-outerLo;
  const band=samples.map(a=>{ a.sort((x,y)=>x-y); return {p05:meiPercentile(a,outerLo),p25:meiPercentile(a,.25),median:meiPercentile(a,.5),p75:meiPercentile(a,.75),p95:meiPercentile(a,outerHi)}; });
  maxDDs.sort((a,b)=>a-b);
  return {enabled:true, ...cal, startingEquity, horizonMonths:horizon, simulationCount:count, confidenceLevel:confidence,
    muUsed:expectedMonthlyReturn, logDrift, seedFallback:mei.seedMode==='fixed'&&!fixedSeed,
    medianPath:band.map(x=>x.median), lowerBand:band.map(x=>x.p05), upperBand:band.map(x=>x.p95), lowerInnerBand:band.map(x=>x.p25), upperInnerBand:band.map(x=>x.p75),
    finalMedian:band[horizon].median, finalLower:band[horizon].p05, finalUpper:band[horizon].p95,
    probabilityBelowInitial:belowInitial/count, probabilityTouchMDD:touchingMDD/count,
    medianMaxDrawdown:meiPercentile(maxDDs,.5), percentileMaxDrawdown:meiPercentile(maxDDs,confidence)};
}

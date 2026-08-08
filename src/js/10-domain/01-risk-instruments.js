// ============ MOTOR DE RISCO POR INSTRUMENTO ============
// P&L de uma ordem é denominado na MOEDA DE COTAÇÃO do par; o risco em $ precisa converter.
const QUOTE_CCY={EURUSD:'USD',GBPUSD:'USD',AUDUSD:'USD',NZDUSD:'USD',US500:'USD',XAUUSD:'USD',
  USDJPY:'JPY',USDCHF:'CHF',USDCAD:'CAD',AUDCAD:'CAD'};
function instFor(par){
  if(!par) return null;
  const k=String(par).toUpperCase().replace(/[^A-Z0-9]/g,'');
  return S.instruments.find(i=>i.name===k)||null;
}
function quoteToUSD(ccy){ // 1 unidade da moeda de cotação em USD
  if(!ccy || ccy==='USD') return 1;
  const map={JPY:'USDJPY',CHF:'USDCHF',CAD:'USDCAD'};
  const ins=S.instruments.find(i=>i.name===map[ccy]);
  return (ins && ins.preco>0) ? 1/ins.preco : 1;
}

const ONBOARDING_STEPS=[
  {key:'ident',label:'Identificação'},
  {key:'instit',label:'Instituição'},
  {key:'risk',label:'Risco'},
  {key:'reserves',label:'Reservas'},
  {key:'cash',label:'Caixa Central'},
  {key:'protect',label:'Proteção'},
  {key:'database',label:'Base de Dados'}, // JPW-HJFGDE §5: termo de responsabilidade + pasta padrão
  {key:'consent',label:'Consentimento'}
];
function savedOnboardingBroker(){
  const ob=S.onboarding||{};
  return brokerFor(ob.corretora)||null;
}
function getSavedOnboardingStepStatus(step){
  const ob=S.onboarding||{};
  const broker=savedOnboardingBroker();
  const isProp=isPropFirm(broker||{});
  switch(step){
    case 'ident':
      return (String(ob.operador||'').trim() && String(ob.supervisor||'').trim() && (S.params.saldoIni||0)>0 && String(S.params.inicio||'').trim())?'complete':'pending';
    case 'instit':
      if(!ob.corretora) return 'pending';
      if(!(String(ob.brokerLogin||'').trim() && String(ob.investorPassword||'').trim() && String(ob.brokerServer||'').trim() && String(ob.plataforma||'').trim() && String(ob.alavCorretora||'').trim())) return 'warning';
      if(isProp && !(String(ob.propDailyDrawdown||'').trim() && String(ob.propMaxDrawdown||'').trim() && ob.restrictiveRuleAccepted)) return 'warning';
      return 'complete';
    case 'risk':
      return (S.period&&S.period.profile)?'complete':'pending';
    case 'reserves': {
      if(!(String(ob.reserveFcrCurrent||'').trim() && String(ob.reserveMonthlyExpenses||'').trim() && String(ob.reserveFeoCurrent||'').trim() && ob.reserveSegregationAccepted)) return 'pending';
      const fcrBad=ob.reserveFcrStatus && ob.reserveFcrStatus!=='Regular';
      const feoBad=ob.reserveFeoStatus && ob.reserveFeoStatus!=='Regular';
      if((fcrBad||feoBad) && !ob.reserveDeficitAccepted) return 'critical';
      return (fcrBad||feoBad)?'warning':'complete';
    }
    case 'cash':
      if(!(ob.centralCashStatus && ob.centralCashCustody && ob.fcrLiquidity && ob.feoLiquidity && ob.cashLedgerStatus && ob.centralCashPolicyAccepted)) return 'pending';
      if(ob.centralCashStatus==='Não.') return ob.centralCashNoAccepted?'warning':'critical';
      if(ob.centralCashStatus==='Em implantação.' || ob.cashLedgerStatus==='Registro parcial' || ob.cashLedgerStatus==='Ainda não existe registro formal') return 'warning';
      return 'complete';
    case 'protect':
      if(!(ob.epStatus && ob.epRestrictiveAccepted)) return 'pending';
      if(ob.epStatus==='Ainda vou configurar antes de iniciar o período.') return 'critical';
      if(ob.epStatus==='Não vou utilizar.') return ob.epNoConfigAccepted?'warning':'critical';
      if(ob.epStatus==='Sim, vou utilizar.' && (!ob.epPlatform || ob.epPlatform==='Nenhuma.' || (ob.epPlatform==='Outra.'&&!String(ob.epPlatformOther||'').trim()))) return 'warning';
      return 'complete';
    case 'database':
      // JPW-HJFGDE §5: aceito uma vez, vale para a base; a pasta padrão é opcional e
      // não muda o status (o cartão da Central acompanha o estado real do acesso).
      return (S.dataGovernance&&S.dataGovernance.responsibility&&S.dataGovernance.responsibility.accepted)?'complete':'pending';
    case 'consent':
      return (ob.consentAccepted && ob.summaryAccepted && String(ob.consentOperator||ob.operador||'').trim())?'complete':'pending';
  }
  return 'pending';
}
function getOnboardingCompletionState(){
  const counts={complete:0,pending:0,warning:0,critical:0};
  const steps=ONBOARDING_STEPS.map(s=>{
    const status=getSavedOnboardingStepStatus(s.key);
    counts[status]=(counts[status]||0)+1;
    return {...s,status};
  });
  const incompleteSteps=steps.filter(s=>s.status!=='complete');
  const severity=counts.critical?'critical':(counts.warning?'warning':(counts.pending?'pending':'complete'));
  return {complete:incompleteSteps.length===0,total:steps.length,completed:counts.complete||0,pending:counts.pending||0,warning:counts.warning||0,critical:counts.critical||0,severity,steps,incompleteSteps,firstIncomplete:incompleteSteps[0]||null};
}
function isOnboardingFullyComplete(){ return getOnboardingCompletionState().complete; }
function onboardingCompletionText(st){
  if(st.complete) return `${st.total} de ${st.total} seções concluídas.`;
  const names=st.incompleteSteps.map(x=>x.label).join(', ');
  return `${st.completed} de ${st.total} seções concluídas. Faltam: ${names}.`;
}
let onboardingWarningShownThisSession=false;
function openFirstIncompleteOnboarding(){
  const st=getOnboardingCompletionState();
  const step=st.firstIncomplete?st.firstIncomplete.key:'ident';
  openOnboardingModal((S.onboarding&&S.onboarding.done)?'edit':'new', step);
}
function renderOnboardingIncompleteBanner(){
  const el=$('onboardingIncompleteBanner'); if(!el) return;
  const st=getOnboardingCompletionState();
  if(st.complete){
    el.classList.remove('show','pending','warning','critical');
    return;
  }
  el.classList.remove('pending','warning','critical');
  el.classList.add('show',st.severity);
  el.setAttribute('role',st.severity==='critical'?'alert':'status');
  const title=st.severity==='critical'?'Formulário de Início possui pendências críticas':(st.severity==='warning'?'Formulário de Início possui pendências de atenção':'Formulário de Início ainda não concluído');
  const t=$('onbBannerTitle'), s=$('onbBannerText');
  if(t) t.textContent=title;
  if(s) s.textContent=onboardingCompletionText(st);
  const btn=$('onbBannerBtn');
  if(btn) btn.onclick=openFirstIncompleteOnboarding;
}
function renderExecutionOnboardingWarning(){
  const el=$('execOnboardingGovNote'); if(!el) return;
  const st=getOnboardingCompletionState();
  if(st.complete){ el.classList.remove('show'); return; }
  el.classList.add('show');
  const txt=$('execOnboardingGovText');
  if(txt) txt.textContent=`O Formulário de Início possui ${st.incompleteSteps.length} seção(ões) pendente(s). Revise antes de considerar o período plenamente autorizado.`;
  const btn=$('execOnboardingGovBtn');
  if(btn) btn.onclick=openFirstIncompleteOnboarding;
}
function showOnboardingCompleteNotice(){
  const t=$('savedTag'); if(!t) return;
  const old=t.textContent;
  t.textContent='Formulário de Início concluído';
  t.classList.add('show');
  setTimeout(()=>{ t.textContent=old||'salvo'; t.classList.remove('show'); },1800);
}
function maybeShowOnboardingNavReminder(screen){
  if(onboardingWarningShownThisSession || isOnboardingFullyComplete()) return;
  if(!['exec','motor','check'].includes(screen)) return;
  onboardingWarningShownThisSession=true;
  const el=$('onboardingIncompleteBanner');
  if(!el) return;
  el.style.boxShadow='0 0 0 2px var(--accent-tint)';
  setTimeout(()=>{ if(el) el.style.boxShadow=''; },1800);
}
function usdPerBase(ins){ // valor USD de 1 unidade da moeda-base (para o nocional)
  if(!ins) return 1;
  if(ins.name==='USDJPY'||ins.name==='USDCHF'||ins.name==='USDCAD') return 1; // base USD → nocional fixo
  if(ins.name==='AUDCAD'){
    const a=S.instruments.find(i=>i.name==='AUDUSD');
    return (a && a.preco>0)?a.preco:1;
  }
  return ins.preco; // pares cotados em USD (e US500/XAUUSD, já em USD)
}
function orderRisk(o){ // risco programado da ordem em USD (entrada → stop)
  if(!(o && o.lote>0 && o.entry>0 && o.sl>0)) return 0;
  const ins=instFor(o.par);
  const cpl=ins?ins.cpl:100000;
  const q=ins?(QUOTE_CCY[ins.name]||'USD'):'USD';
  return o.lote*cpl*Math.abs(o.entry-o.sl)*quoteToUSD(q);
}
function orderNotional(o){ // exposição nominal USD (independe de SL — ordem sem stop também pesa)
  if(!(o && o.lote>0)) return 0;
  const ins=instFor(o.par);
  const cpl=ins?ins.cpl:100000;
  return o.lote*cpl*(ins?usdPerBase(ins):1);
}
function netOpAtual(){ // resultado líquido fechado da OPERAÇÃO ATUAL (grades vivas) — Art. 9.2 + perdas
  let n=0;
  S.phases.forEach(ph=>ph.orders.forEach(o=>{ if(o.status==='Fechada') n+=(+o.result||0); }));
  return n;
}
function perdaCicloArq(){ // perdas realizadas de operações já arquivadas: nunca somem do DD (Art. 3.4§2)
  return Math.max(0, -(S.cycleRealizado||0));
}
function totalRiscoAbertoExc(exclPi,exclOi){ // risco aberto CONSOLIDADO (todas as grades), excluindo uma ordem
  let r=0;
  S.phases.forEach((ph,pi)=>ph.orders.forEach((o,oi)=>{
    if(pi===exclPi&&oi===exclOi) return;
    if(o.status==='Aberta') r+=orderRisk(o);
  }));
  return r;
}
function quarantineActive(){
  return !!(S.quarantine && todayISO()<=S.quarantine.fim);
}

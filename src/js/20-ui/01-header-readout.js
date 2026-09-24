// ============ TOP BAR · LEITURA DE ESTADO ============
// Somente leitura de valores já calculados — nenhum cálculo estatutário aqui.
function renderHeaderReadout(c){
  if(!c)c=compute(); // Navigation refresh uses the same read-only central projection.
  const set=(id,txt)=>{ const e=$(id); if(e) e.textContent=txt; };
  const p=(S&&S.params)||{};
  // A seleção Forex fornece referência documental do período, sem modificar
  // o perfil global usado nas simulações legadas nem congelar o motor vigente.
  const inOperation=$('exec')?.classList.contains('active');
  const inForex=inOperation||globalThis.JPWNavigation?.current?.().primary==='forex';
  const selected=inForex&&globalThis.JPWForex?.state?.operationalSelection?.();
  try{
    const pr=inForex?JPWForex.state.accountProfileContext?.(selected)?.period:getActiveRiskProfile();
    set('hdrProfile',pr?.name||(inForex?'Não informado':'—'));
  }catch(_){set('hdrProfile','—');}
  const scoped=inOperation&&selected?.accountId&&selected?.periodId?
    JPWForex.state.accountContext({accountId:selected.accountId,periodId:selected.periodId}):null;
  const startedAt=inOperation?(scoped?.status==='OK'?scoped.value.startedAt:null):p.inicio;
  set('hdrPeriod', startedAt ? fmtDateEU(startedAt) : '—');
  set('hdrEquity', fmtForexMoney(c&&c.forex&&c.forex.account?c.forex.account.equity:null,c&&c.forex&&c.forex.account,0));
  const ddEl=$('hdrDD');
  if(ddEl && c){
    ddEl.textContent=fmtPct(c.dd);
    const lim=c.mddScaled, r=lim>0?(c.dd/lim):0;
    ddEl.style.color = r>=1 ? 'var(--f4)' : r>=.75 ? 'var(--f3)' : r>=.5 ? 'var(--f2)' : 'var(--ink)';
  }
  // Espelho do painel "Perfil e Contexto" do Global Dashboard (Etapa 1) —
  // mesmos dados de c já usados em dFase/dAlav/hdrDD, só novos IDs de leitura.
  if(c){
  }
}
function startHeaderClock(){
  const el=$('hdrClock'); if(!el) return;
  const tick=()=>{ el.textContent=new Date().toLocaleTimeString('pt-BR',{hour12:false}); };
  tick(); setInterval(tick,1000);
}

// ============ TOP BAR · LEITURA DE ESTADO ============
// Somente leitura de valores já calculados — nenhum cálculo estatutário aqui.
function renderHeaderReadout(c){
  const set=(id,txt)=>{ const e=$(id); if(e) e.textContent=txt; };
  const p=(S&&S.params)||{};
  // getActiveRiskProfile() é o acessor canônico (lê S.period.profile e cai em 'base').
  try{ const pr=getActiveRiskProfile(); set('hdrProfile', (pr&&pr.name)||'—'); }
  catch(_){ set('hdrProfile','—'); }
  set('hdrPeriod', p.inicio ? fmtDateEU(p.inicio) : '—');
  set('hdrEquity', fmtMoney(p.saldoAtu||0));
  const ddEl=$('hdrDD');
  if(ddEl && c){
    ddEl.textContent=fmtPct(c.dd||0);
    const lim=c.mddScaled||0.15, r=lim>0?(c.dd/lim):0;
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

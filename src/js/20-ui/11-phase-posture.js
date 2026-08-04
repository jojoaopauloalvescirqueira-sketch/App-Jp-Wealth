// ============ Postura ofensiva/defensiva por fase (SET 2) ============
const PHASE_OBJECTIVE=[
  {t:'OFENSIVO',d:'Buscar lucro dentro do risco normal (teto 4,0x). Executar a tese com convicção — é na Fase 1 que a meta de ~3,5%/mês é construída com conforto.'},
  {t:'CAUTELA',d:'Lucro com mais cautela — o objetivo migra para breakeven / lucro reduzido. Teto cai para 2,0x; suspender novos lotes agressivos (Art. 2.1 §3).'},
  {t:'DEFENSIVO',d:'Sobrevivência. Apenas REDUZIR exposição em movimentos corretivos — nunca ampliar (teto 1,0x). Preservação de capital acima de qualquer tese.'},
  {t:'SALVAGUARDA',d:'Encerramento residual — atividade discricionária suspensa, sem novas posições (teto 0,4x). Prepare o relatório de incidente caso atinja 15%.'},
];
const OBJ_COL=['--f1','--f2','--f3','--f4'], OBJ_BG=['--f1-bg','--f2-bg','--f3-bg','--f4-bg'];
function renderObjective(fi){
  const el=$('objectiveCard'); if(!el) return;
  const o=PHASE_OBJECTIVE[fi];
  const pr=getActiveRiskProfile();
  const row=activeRiskMatrix()[fi];
  let desc=o.d;
  if(fi===0){
    desc=`Buscar lucro dentro do risco normal do perfil ${pr.name} (${fmtPct(row.ddmin)}–${fmtPct(row.ddmax)} de DD). Executar a tese com convicção; a referência mensal ativa é ${fmtPct(pr.mensal)}.`;
  }else if(fi===3){
    desc=`Encerramento residual — atividade discricionária suspensa, sem novas posições (teto 0,4x). Prepare o relatório de incidente caso atinja ${fmtPct(activeMDDLimit())}.`;
  }
  el.style.borderColor=`var(${OBJ_COL[fi]})`;
  el.innerHTML=`<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
    <div style="font-weight:800;font-size:calc(14px * var(--fs-scale));letter-spacing:.04em;color:var(${OBJ_COL[fi]});background:var(${OBJ_BG[fi]});padding:9px 15px;border-radius:8px;white-space:nowrap">FASE ${fi+1} · POSTURA ${o.t}</div>
    <div style="font-size:calc(13px * var(--fs-scale));color:var(--ink-dim);flex:1;min-width:240px;line-height:1.55">${desc}</div>
  </div>`;
}

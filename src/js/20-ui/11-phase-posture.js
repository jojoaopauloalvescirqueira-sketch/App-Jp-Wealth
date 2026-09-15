// ============ Postura ofensiva/defensiva por fase (SET 2) ============
const PHASE_OBJECTIVE=JPWForex.policy.phases.map(row=>({
  t:row.name.toUpperCase(),
  d:(row.amplification==='FORBIDDEN'?'Ampliação vedada. ':row.amplification==='DECLARED_ZONES_ONLY'?'Ampliação limitada às zonas declaradas. ':'Ampliação restrita pelo contrato. ')
    +'Teto estrutural '+fmtX(row.maxLeverage)+'; VRM e limites de risco são cumulativos. P-14/P-17/P-18 pendentes: a fase não concede autorização de execução.'
}));
const OBJ_COL=['--f1','--f2','--f2','--f3','--f3','--f4'], OBJ_BG=['--f1-bg','--f2-bg','--f2-bg','--f3-bg','--f3-bg','--f4-bg'];
function renderObjective(fi){
  const el=$('objectiveCard'); if(!el) return;
  const o=Number.isInteger(fi)?PHASE_OBJECTIVE[fi]:null;
  if(!o){el.style.borderColor='var(--ink-dim)';el.textContent='Fase não calculável. Registre SI, equity e fontes; questionários não liberam uma fase.';return;}
  const desc=o.d;
  el.style.borderColor=`var(${OBJ_COL[fi]})`;
  el.innerHTML=`<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">
    <div style="font-weight:800;font-size:calc(14px * var(--fs-scale));letter-spacing:.04em;color:var(${OBJ_COL[fi]});background:var(${OBJ_BG[fi]});padding:9px 15px;border-radius:8px;white-space:nowrap">FASE ${fi+1} · POSTURA ${o.t}</div>
    <div style="font-size:calc(13px * var(--fs-scale));color:var(--ink-dim);flex:1;min-width:240px;line-height:1.55">${desc}</div>
  </div>`;
}

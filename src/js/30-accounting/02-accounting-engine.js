// ============ MOTOR DA CONTABILIDADE (perfis V10 centralizados) ============
function acctProfile(){ return getActiveRiskProfile(); }
// Monthly projection belongs to JPWFx. No annual target is selected from the
// policy range, and an absent plan is unavailable rather than a zero-return plan.
function acctModel(){
  const pr=acctProfile(),api=window.JPWFx;
  const live=api&&api.state?api.state.fxOverviewLive():null;
  const projected=live?live.forecast:[];
  const scope=window.JPWForex?.state?.operationalSelection?.()||{};
  const period=scope.accountId&&scope.periodId?window.JPWForex.state.accountContext(scope):null;
  return {pr,saldoIni:period?.status==='OK'?period.value.openingBook:null,diasSem:S.acct&&S.acct.diasSemana||4.5,
    mesesAno:S.acct&&S.acct.mesesAno||10.5,diasAno:null,target:null,metaDia:null,metaMes:null,
    saldoFim:projected.length?projected[projected.length-1].close:null,
    available:!!live,source:'PLAN',live};
}
function acctProjection(){
  const m=acctModel();
  const start=new Date((m.live?m.live.plan.baseline.startMonth+'-01':S.params.inicio||todayISO())+'T00:00:00');
  const series=m.live?m.live.forecast:[];
  const rows=series.map((r,i)=>{
    const [year,month]=r.month.split('-').map(Number),date=new Date(year,month,0);
    return {idx:i+1,date,iso:dateISO(date),open:r.open,res:r.profit,close:r.close,
      cumPct:m.live.plan.baseline.initialBalanceUsd>0?r.close/m.live.plan.baseline.initialBalanceUsd-1:null};
  });
  return {m,start,rows};
}
function acctRealByDate(){ const map={}; ledgerSorted().forEach(e=>map[e.data]=e.saldo); return map; }
function acctRealNow(){ const led=ledgerSorted(); return led.length?led[led.length-1].saldo:acctModel().saldoIni; }
function acctPace(){
  const proj=acctProjection(), m=proj.m, today=todayISO(), real=acctRealNow();
  let k7=null; // data projetada em que o saldo projetado alcança o saldo real (K7)
  if(real<=m.saldoIni){ k7=dateISO(proj.start); }
  else { for(const r of proj.rows){ if(r.close>=real){ k7=r.iso; break; } } }
  const k8 = k7 ? Math.round((new Date(k7+'T00:00:00')-new Date(today+'T00:00:00'))/86400000) : null; // K8
  let idealToday=m.saldoIni;
  for(const r of proj.rows){ if(r.iso<=today) idealToday=r.close; else break; }
  return {m, real, idealToday, k7, k8, endDate:proj.rows.length?proj.rows[proj.rows.length-1].iso:today, proj};
}
function weekKey(d){ const x=new Date(d); const off=(x.getDay()+6)%7; x.setDate(x.getDate()-off); return dateISO(x); }
function acctWeekRow(sum){ return `<tr style="background:var(--panel-2)"><td colspan="3" style="font-weight:700;color:var(--ink)">Σ semana</td><td style="color:var(--f1);font-weight:700">${fmtMoney2(sum)}</td><td colspan="4"></td></tr>`; }

let acctDetailOpen=false; // estado de UI (não persiste entre sessões, só entre re-renders) — SET: escondido por padrão
function renderAcctSummary(m,p){
  const box=$('acctPeriodSummary'); if(!box) return;
  const k8=p.k8;
  const paceLabel=k8==null?'—':(k8>0?'+'+k8+' dias':(k8<0?k8+' dias':'no ritmo'));
  const paceColor=k8==null?'var(--ink-dim)':(k8>=0?'var(--f1)':'var(--f4)');
  box.innerHTML=`<div class="metrics" style="grid-template-columns:repeat(4,1fr)">
    <div class="metric"><div class="k">Perfil vigente</div><div class="v sm">${esc(m.pr.name)} · ${Math.round(m.pr.pct*100)}%</div></div>
    <div class="metric"><div class="k">Saldo inicial</div><div class="v sm">${fmtMoney2(m.saldoIni)}</div></div>
    <div class="metric"><div class="k">Meta anual</div><div class="v sm">${(m.target*100).toFixed(1).replace('.',',')}%</div></div>
    <div class="metric"><div class="k">Ritmo do ciclo (K8)</div><div class="v sm" style="color:${paceColor}">${paceLabel}</div><div class="sub">${k8==null?'sem medição':(k8<0?'atrás do ideal · sem pressa':(k8>0?'à frente do ideal':'equilíbrio'))}</div></div>
  </div>`;
}
function renderAcct(){
  const box=$('acctPeriodSummary');if(!box)return;
  const m=acctModel(),api=window.JPWFx,refs=api&&api.state&&api.state.fxPlanningReferences?api.state.fxPlanningReferences():null;
  const percent=v=>Number.isFinite(v)?(v*100).toLocaleString('pt-BR',{maximumFractionDigits:2})+'%':'indisponível';
  const money=v=>Number.isFinite(v)?fmtMoney2(v):'Indisponível';
  const scope=window.JPWForex?.state?.operationalSelection?.()||{};
  const period=scope.accountId&&scope.periodId?window.JPWForex.state.accountContext(scope):null;
  const currency=period?.status==='OK'?period.value.currency:null;
  box.innerHTML=`<p class="fxp-note">Conta ${esc(scope.accountId||'não selecionada')} · período ${esc(scope.periodId||'não registrado')} · moeda ${esc(currency||'não verificada')}</p><div class="metrics"><div class="metric"><div class="k">Saldo inicial book</div><div class="v sm">${money(m.saldoIni)}</div></div><div class="metric"><div class="k">Último saldo book</div><div class="v sm">${money(acctRealNow())}</div></div><div class="metric"><div class="k">Referência mensal do plano global</div><div class="v sm">${refs?percent(refs.monthly):'indisponível'}</div></div><div class="metric"><div class="k">Referência anual distinta</div><div class="v sm">${refs&&Array.isArray(refs.annualRange)?refs.annualRange.map(percent).join(' – '):'indisponível'}</div></div></div><p class="fxp-note">Fechamentos são fatos contábeis. Book, SI e equity são distintos. O plano global não atribui meta a esta conta.</p>`;
  const detail=$('acctPeriodDetail'),toggle=$('acctPeriodToggle');if(detail)detail.style.display='none';if(toggle)toggle.hidden=true;
  const chart=$('rvpChart');
  if(chart)chart.innerHTML='<p class="fxp-note">'+(m.available?'Projeção mensal disponível no Planejamento FX, com as premissas explícitas do plano.':'Sem plano explícito: projeção indisponível. Crie um plano no Planejamento FX.')+'</p><button type="button" id="acctGoPlanning">Abrir Planejamento</button>';
  if($('acctGoPlanning'))$('acctGoPlanning').onclick=()=>window.JPWNavigation.navigate('forex-planning');
  const proj=$('acctProjWrap');if(proj)proj.innerHTML='';
  const pace=$('dashCyclePace');if(pace)pace.innerHTML='<p class="fxp-note">Acompanhe ACTUAL × PLAN no Planejamento FX. As referências de retorno não determinam um ritmo obrigatório de execução.</p>';
  const sim=$('acctSimWrap');
  if(sim)sim.innerHTML='<p class="fxp-note">Simulação por conta indisponível nesta transição: não existe premissa estatística homologada para atribuir o plano global a esta conta.</p>';
  const th=$('ledgerBody')?.closest('table')?.querySelectorAll('thead th')[3];if(th)th.textContent='Queda book vs referência';
}
function renderAcctPace(p){
  const box=$('acctPace'); if(!box) return;
  const k8=p.k8==null?0:p.k8;
  const cap=Math.max(20, Math.ceil(Math.abs(k8)/10)*10);
  const half=Math.max(-50,Math.min(50,(k8/cap)*50));
  const ahead=k8>=0, strong=k8>cap*0.6;
  const color=ahead?(strong?'var(--f2)':'var(--f1)'):'var(--f4)';
  const seg=ahead?`left:50%;width:${half}%`:`left:${50+half}%;width:${-half}%`;
  const label=p.k8==null?'—':(k8>=1?`+${k8} dias à frente`:(k8<=-1?`${k8} dias atrás`:'no ritmo'));
  const interp = p.k8==null ? 'Registre ao menos um fechamento para medir o ritmo.'
    : strong ? 'Muito adiantado — pela hierarquia do Estatuto (preservação &gt; retorno, Art. 11.1) você pode <b>desacelerar</b> e reduzir risco; a meta já está folgada.'
    : k8>=1 ? 'Adiantado em relação ao ideal. Há margem para ser mais seletivo e reduzir exposição.'
    : k8<=-1 ? 'Abaixo do ritmo ideal — <b>sem pressa</b>. Sobrevivência precede retorno (Art. 2.1 §3); não amplie risco para “recuperar tempo”.'
    : 'No ritmo exato do ideal projetado.';
  box.innerHTML=`
    <div style="display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:14px">
      <div style="font-family:var(--mono);font-size:calc(32px * var(--fs-scale));font-weight:800;color:${color}">${label}</div>
      <div style="font-size:calc(12px * var(--fs-scale));color:var(--ink-dim)">seu saldo real corresponde ao ideal projetado para <b>${p.k7||'—'}</b></div>
    </div>
    <div style="position:relative;height:16px;background:var(--panel-2);border:1px solid var(--line);border-radius:999px;overflow:hidden;margin-bottom:6px">
      <div style="position:absolute;top:0;bottom:0;${seg};background:${color}"></div>
      <div style="position:absolute;left:50%;top:-2px;bottom:-2px;width:2px;background:var(--ink);opacity:.45"></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-family:var(--mono);font-size:calc(10px * var(--fs-scale));color:var(--ink-faint);margin-bottom:16px">
      <span>−${cap}d · atrás</span><span>ideal</span><span>+${cap}d · à frente</span>
    </div>
    <div class="metrics" style="grid-template-columns:repeat(3,1fr)">
      <div class="metric"><div class="k">Saldo real</div><div class="v sm">${fmtMoney2(p.real)}</div></div>
      <div class="metric"><div class="k">Ideal para hoje</div><div class="v sm">${fmtMoney2(p.idealToday)}</div></div>
      <div class="metric"><div class="k">Δ vs ideal</div><div class="v sm" style="color:${p.real-p.idealToday>=0?'var(--f1)':'var(--f4)'}">${fmtMoney2(p.real-p.idealToday)}</div></div>
    </div>
    <p style="font-size:calc(12px * var(--fs-scale));color:var(--ink-dim);margin-top:12px;line-height:1.55">${interp}</p>`;
  const dashBox=$('dashCyclePace');
  if(dashBox) dashBox.innerHTML=box.innerHTML;
}
function renderAcctProj(p){
  const wrap=$('acctProjWrap'); if(!wrap) return;
  const realMap=acctRealByDate(), today=todayISO();
  let rows='', weekSum=0, lastWk=null, realCarry=p.m.saldoIni;
  p.proj.rows.forEach(r=>{
    const wk=weekKey(r.date);
    if(lastWk!==null && wk!==lastWk){ rows+=acctWeekRow(weekSum); weekSum=0; }
    lastWk=wk; weekSum+=r.res;
    if(realMap[r.iso]!=null) realCarry=realMap[r.iso];
    const hasReal=r.iso<=today;
    const realTxt=hasReal?fmtMoney2(realCarry):'—';
    const delta=hasReal?realCarry-r.close:null;
    const isToday=r.iso===today;
    rows+=`<tr style="${isToday?'background:var(--indigo-deep)':''}">
      <td class="hl">${r.idx}</td><td>${r.iso}</td>
      <td>${fmtMoney2(r.open)}</td><td style="color:var(--f1)">${fmtMoney2(r.res)}</td><td>${fmtMoney2(r.close)}</td>
      <td>${(r.cumPct*100).toFixed(2).replace('.',',')}%</td>
      <td>${realTxt}</td>
      <td>${delta!=null?`<span style="color:${delta>=0?'var(--f1)':'var(--f4)'}">${fmtMoney2(delta)}</span>`:'—'}</td>
    </tr>`;
  });
  rows+=acctWeekRow(weekSum);
  wrap.innerHTML=`<table class="dtable" style="font-size:calc(11px * var(--fs-scale))">
    <thead><tr><th>#</th><th>Data</th><th>Inicial</th><th>Meta dia</th><th>Proj. acum.</th><th>%</th><th>Real acum.</th><th>Δ real−proj</th></tr></thead>
    <tbody>${rows}</tbody></table>`;
}
function drawRvpChart2(p){
  const box=$('rvpChart'); if(!box) return;
  const proj=p.proj.rows; if(!proj.length){ box.innerHTML=''; return; }
  const start=p.proj.start, today=todayISO();
  const spanDays=(new Date(proj[proj.length-1].iso+'T00:00:00')-start)/86400000||1;
  const projPts=proj.map(r=>({x:(r.date-start)/86400000, y:r.close}));
  const realPts=ledgerSorted().map(e=>({x:(new Date(e.data+'T00:00:00')-start)/86400000, y:e.saldo})).filter(pt=>pt.x>=0&&pt.x<=spanDays);
  const ys=[...projPts.map(a=>a.y),...realPts.map(a=>a.y),p.m.saldoIni,p.m.saldoFim];
  let ymin=Math.min(...ys), ymax=Math.max(...ys); const pad=(ymax-ymin)*0.08||Math.max(1,ymax*0.02); ymin-=pad; ymax+=pad;
  const W=720,H=250,L=CH.L,R=CH.R,T=CH.T,B=CH.B;
  const X=x=>L+(x/spanDays)*(W-L-R), Y=y=>T+(1-(y-ymin)/(ymax-ymin))*(H-T-B);
  const path=pts=>pts.map((a,i)=>(i?'L':'M')+X(a.x).toFixed(1)+' '+Y(a.y).toFixed(1)).join(' ');
  const grid=CH.gridY(W,L,R,Y,CH.ticks(ymin,ymax,4),fmtMoney);
  const todayX=(new Date(today+'T00:00:00')-start)/86400000;
  const dots=realPts.map(a=>`<circle cx="${X(a.x).toFixed(1)}" cy="${Y(a.y).toFixed(1)}" r="1.8" fill="var(--f1)"/>`).join('');
  const realArea=realPts.length>1
    ? `<path d="${CH.area(path(realPts),X(realPts[0].x),X(realPts[realPts.length-1].x),H-B)}" fill="var(--f1)" opacity=".14"/>` : '';
  const ysR=realPts.map(a=>a.y);
  const stats=CH.stats(L,T,[
    {mark:'□', label:'Projetado', value:fmtMoney(projPts[projPts.length-1].y), color:'var(--violet)'},
    ...(ysR.length?[
      {mark:'□', label:'Real',    value:fmtMoney(ysR[ysR.length-1]),                  color:'var(--f1)'},
      {mark:'↑', label:'Máximo',  value:fmtMoney(Math.max(...ysR)),                   color:'var(--data-num)'},
      {mark:'–', label:'Média',   value:fmtMoney(ysR.reduce((a,b)=>a+b,0)/ysR.length),color:'var(--data-drv)'},
      {mark:'↓', label:'Mínimo',  value:fmtMoney(Math.min(...ysR)),                   color:'var(--data-num)'},
    ]:[])
  ]);
  const callouts=CH.callout(W,R,Y(projPts[projPts.length-1].y),fmtMoney(projPts[projPts.length-1].y),'var(--violet)')
    + (ysR.length?CH.callout(W,R,Y(ysR[ysR.length-1]),fmtMoney(ysR[ysR.length-1]),'var(--f1)'):'');
  box.innerHTML=`<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;font-family:var(--mono)">
    <rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}" fill="var(--bg)"/>
    ${grid}
    ${todayX>=0&&todayX<=spanDays?`<line x1="${X(todayX).toFixed(1)}" x2="${X(todayX).toFixed(1)}" y1="${T}" y2="${H-B}" stroke="var(--ink-faint)" stroke-dasharray="2 3" opacity=".6"/>`:''}
    ${realArea}
    <path d="${path(projPts)}" fill="none" stroke="var(--violet)" stroke-width="1" stroke-dasharray="4 3"/>
    ${realPts.length>1?`<path d="${path(realPts)}" fill="none" stroke="var(--f1)" stroke-width="1.2"/>`:''}${dots}
    ${callouts}
    ${stats}
  </svg>${realPts.length?'':'<p style="font-size:var(--fs-sm);color:var(--ink-faint);margin-top:6px">Sem fechamentos ainda — a curva Real aparece a partir do primeiro lançamento.</p>'}`;
}

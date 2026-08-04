// ============ MOTOR DA CONTABILIDADE (perfis V10 centralizados) ============
function acctProfile(){ return getActiveRiskProfile(); }
function acctModel(){
  const pr=acctProfile();
  const saldoIni=S.params.saldoIni||0;
  const diasSem=(S.acct&&S.acct.diasSemana)||4.5;
  const mesesAno=(S.acct&&S.acct.mesesAno)||10.5;
  const diasAno=diasSem*52*(mesesAno/12);                               // Q8
  const target=pr.anual;                                               // E7 (pelo perfil)
  const saldoFim=saldoIni*(1+target);                                  // E8
  const metaDia = diasAno>0 ? Math.pow(1+target, 1/diasAno)-1 : 0;     // H12 = RATE(Q8,,-E6,E8)
  const metaMes = mesesAno>0 ? Math.pow(1+target, 1/mesesAno)-1 : 0;   // I12 = RATE(O8,,-E6,E8)
  return {pr, saldoIni, diasSem, mesesAno, diasAno, target, saldoFim, metaDia, metaMes};
}
// série projetada dia-a-dia (só dias úteis seg–sex), compõe a meta diária até atingir o alvo
function acctProjection(){
  const m=acctModel();
  const start=new Date((S.params.inicio||todayISO())+'T00:00:00');
  const rows=[]; let bal=m.saldoIni; const d=new Date(start); let idx=0, guard=0;
  const hardStop=new Date(start); hardStop.setFullYear(hardStop.getFullYear()+1);
  while(guard++<600){
    const dow=d.getDay();
    if(dow!==0 && dow!==6){
      idx++;
      const open=bal, res=bal*m.metaDia, close=bal+res;
      rows.push({idx, date:new Date(d), iso:dateISO(d), open, res, close, cumPct:m.saldoIni>0?close/m.saldoIni-1:0});
      bal=close;
      if(close>=m.saldoFim || d>=hardStop) break;
    }
    d.setDate(d.getDate()+1);
  }
  return {m, start, rows};
}
function acctRealByDate(){ const map={}; ledgerSorted().forEach(e=>map[e.data]=e.saldo); return map; }
function acctRealNow(){ const led=ledgerSorted(); return led.length?led[led.length-1].saldo:(S.params.saldoIni||0); }
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
  box.innerHTML=`<div class="metrics" style="grid-template-columns:repeat(4,1fr)">
    <div class="metric"><div class="k">Perfil vigente</div><div class="v sm">${esc(m.pr.name)} · ${Math.round(m.pr.pct*100)}%</div></div>
    <div class="metric"><div class="k">Saldo inicial</div><div class="v sm">${fmtMoney2(m.saldoIni)}</div></div>
    <div class="metric"><div class="k">Meta anual</div><div class="v sm">${(m.target*100).toFixed(1).replace('.',',')}%</div></div>
    <div class="metric"><div class="k">Início do período</div><div class="v sm">${S.params.inicio||'—'}</div></div>
  </div>`;
}
function renderAcct(){
  if(!$('acStart')) return;
  const m=acctModel();
  if(document.activeElement!==$('acStart')) $('acStart').value=S.params.inicio||todayISO();
  $('acToday').value=todayISO();
  if(document.activeElement!==$('acSaldoIni')) $('acSaldoIni').value=S.params.saldoIni;
  if(document.activeElement!==$('acDiasSem')) $('acDiasSem').value=m.diasSem;
  if(document.activeElement!==$('acMesesAno')) $('acMesesAno').value=m.mesesAno;
  $('acTarget').value=(m.target*100).toFixed(1).replace('.',',')+'%  ·  '+m.pr.name;
  $('acSaldoFim').value=fmtMoney2(m.saldoFim);
  $('acDiasAno').value=m.diasAno.toFixed(2).replace('.',',')+' dias úteis/ano';
  const p=acctPace();
  $('acEnd').value=p.endDate;
  renderAcctSummary(m,p);
  // TRAVADOS assim que o período começa (onboarding.done): perfil, data de início, saldo
  // inicial e programação. Mudar qualquer um no meio do período distorceria meta/MDD/DD
  // já em curso. Única forma de mudar é "Visualizar / Editar Formulário de Início" (Configurações),
  // que reabre o onboarding salvo sem reiniciar o ciclo operacional.
  const locked = !!(S.onboarding && S.onboarding.done);
  ['acStart','acSaldoIni','acDiasSem','acMesesAno'].forEach(id=>{ const el=$(id); if(el) el.disabled=locked; });
  const bwrap=$('acctProfileBtns');
  bwrap.innerHTML=acctProfiles().map(pr=>{
    const on=pr.key===m.pr.key;
    return `<button type="button" ${locked?'disabled':`data-prof="${pr.key}"`} style="flex:1;min-width:158px;text-align:left;padding:11px 14px;border-radius:10px;
      cursor:${locked?'default':'pointer'}; opacity:${locked&&!on?'.5':'1'};
      border:1.5px solid ${on?'var(--violet)':'var(--line)'};background:${on?'var(--indigo-deep)':'var(--panel)'}">
      <div style="font-weight:800;font-size:calc(13px * var(--fs-scale));color:${on?'var(--violet)':'var(--ink)'}">${pr.name} · ${Math.round(pr.pct*100)}%${on&&locked?' 🔒':''}</div>
      <div style="font-family:var(--mono);font-size:calc(10px * var(--fs-scale));color:var(--ink-dim);margin-top:3px">Anual ${(pr.anual*100).toFixed(0)}% · MDD ${(pr.mdd*100).toFixed(2).replace('.',',')}%${pr.lev!=null?' · '+fmtX(pr.lev)+'/ord':''}</div>
    </button>`;
  }).join('');
  const lockNote=$('acctProfileLockNote');
  if(locked){
    lockNote.innerHTML='<p class="expl" style="font-size:calc(12px * var(--fs-scale));color:var(--ink-faint)">🔒 Perfil, data de início, saldo inicial e programação travados nesta área — use <b style="color:var(--ink-dim)">Visualizar / Editar Formulário de Início</b> em ⚙ Configurações para revisar ou ajustar os dados do período ativo.</p>';
  } else {
    lockNote.innerHTML='';
    bwrap.querySelectorAll('[data-prof]').forEach(b=>b.addEventListener('click',()=>{
      S.period=S.period||{}; S.period.profile=b.dataset.prof;
      const pr=acctProfile(); S.params.refM=pr.mensal; S.params.refA=pr.anual;
      save(); renderAcct(); renderDash(); renderParams(); render();
    }));
  }
  $('acctMetas').innerHTML=`<div class="metrics" style="grid-template-columns:repeat(4,1fr)">
    <div class="metric"><div class="k">Meta diária</div><div class="v sm">${(m.metaDia*100).toFixed(3).replace('.',',')}%</div></div>
    <div class="metric"><div class="k">Meta mensal</div><div class="v sm">${(m.metaMes*100).toFixed(2).replace('.',',')}%</div></div>
    <div class="metric"><div class="k">Saldo atual (real)</div><div class="v sm">${fmtMoney2(p.real)}</div></div>
    <div class="metric"><div class="k">Resultado acumulado</div><div class="v sm" style="color:${p.real-m.saldoIni>=0?'var(--f1)':'var(--f4)'}">${fmtMoney2(p.real-m.saldoIni)} · ${(m.saldoIni>0?((p.real/m.saldoIni-1)*100):0).toFixed(2).replace('.',',')}%</div></div>
  </div>`;
  renderAcctPace(p);
  renderAcctProj(p);
  drawRvpChart2(p);
  renderAcctSim();
  const toggle=$('acctPeriodToggle'), detail=$('acctPeriodDetail');
  if(toggle && detail){
    detail.style.display=acctDetailOpen?'block':'none';
    toggle.textContent=(acctDetailOpen?'▾':'▸')+' Ver / editar Período & Metas';
  }
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

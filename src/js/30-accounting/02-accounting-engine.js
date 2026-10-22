// ============ MOTOR DA CONTABILIDADE (perfis V10 centralizados) ============
function acctProfile(){ return getActiveRiskProfile(); }
// Accounting contains operational facts only; planning is a separate primary module.
function acctModel(){
  const scope=window.JPWForex?.state?.operationalSelection?.()||{};
  const period=scope.accountId&&scope.periodId?window.JPWForex.state.accountContext(scope):null;
  return {pr:acctProfile(),saldoIni:period?.status==='OK'?period.value.openingBook:null,
    target:null,saldoFim:null,available:false,source:'OPERATIONAL',live:null};
}
function acctProjection(){return {m:acctModel(),start:new Date(todayISO()+'T00:00:00'),rows:[]};}
function acctRealByDate(){ const map={}; ledgerSorted().forEach(e=>map[e.data]=e.saldo); return map; }
function acctRealNow(){ const led=ledgerSorted(); return led.length?led[led.length-1].saldo:acctModel().saldoIni; }
function acctPace(){
  const proj=acctProjection();return {m:proj.m,real:acctRealNow(),idealToday:null,k7:null,k8:null,endDate:null,proj};
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
  const m=acctModel();
  const percent=v=>Number.isFinite(v)?(v*100).toLocaleString('pt-BR',{maximumFractionDigits:2})+'%':'indisponível';
  const scope=window.JPWForex?.state?.operationalSelection?.()||{};
  const period=scope.accountId&&scope.periodId?window.JPWForex.state.accountContext(scope):null;
  const currency=period?.status==='OK'?period.value.currency:null;
  const account=(S.accounts||[]).find(a=>a.forexAccountId===scope.accountId)||S.forex?.accountContexts?.archivedAccounts?.[scope.accountId]?.record;
  const money=v=>Number.isFinite(v)?fmtForexMoney(v,{currency}):'Indisponível';
  box.innerHTML=`<header class="acct-context-heading"><div><p class="eb-eyebrow">FOREX · FECHAMENTOS</p><h1>Contabilidade</h1><p>${esc(account?.nome||'Conta não selecionada')} · Período desde ${esc(period?.value?.startedAt||'não informado')} · ${esc(currency||'Moeda não verificada')}</p></div><div class="metrics"><div class="metric"><div class="k">Saldo inicial book</div><div class="v sm">${money(m.saldoIni)}</div></div><div class="metric"><div class="k">Último saldo book</div><div class="v sm">${money(acctRealNow())}</div></div></div></header><p class="fxp-note">Fechamentos desta conta e período. Book, SI e equity são distintos; registrar um fechamento não confirma equity.</p>`;
  for(const [id,label] of [['ldResult','Resultado do dia'],['ldSaldo','Saldo de fechamento']]){
    const input=$(id),target=input?.closest('.field')?.querySelector('label');
    if(target){target.textContent=label+' ('+(currency||'moeda não verificada')+')';target.htmlFor=id;}
  }
  const detail=$('acctPeriodDetail'),toggle=$('acctPeriodToggle');if(detail)detail.style.display='none';if(toggle)toggle.hidden=true;
  const chart=$('rvpChart');
  if(chart)chart.innerHTML='<div class="acct-planning-link"><p class="fxp-note">Planos, metas e resultados mensais pertencem ao menu Planejamento. Os registros desta conta operacional permanecem separados.</p><button type="button" id="acctGoPlanning" class="reset-btn">Abrir Planejamento</button></div>';
  if($('acctGoPlanning'))$('acctGoPlanning').onclick=()=>window.JPWNavigation.navigate('planning');
  const proj=$('acctProjWrap');if(proj)proj.innerHTML='';
  const pace=$('dashCyclePace');if(pace)pace.innerHTML='<p class="fxp-note">Consulte a comparação entre realizado e referência no menu Planejamento. As projeções não determinam um ritmo obrigatório de execução.</p>';
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

// Compatibility reader for the Forex Reserves boundary. No planning engine/state.
function fxReservePanelData(){
  const api=window.JPWForex&&window.JPWForex.state;
  const view=api&&api.read?api.read():{},reserves=view.reserves&&view.reserves.observations||{};
  const context=api&&api.accountContext?api.accountContext(view.budgetScope):null;
  const unavailable=()=>({status:'NOT_COMPUTABLE',value:null,unit:'ACCOUNT_CURRENCY',findings:[]});
  // Consume the exact results: a selected satellite, conflict or missing basis
  // cannot regain a Mestre requirement through this presentation adapter.
  const fcr=view.metrics?.fcrRequirement||unavailable(),feo=view.metrics?.feoRequirement||unavailable();
  const number=v=>typeof v==='number'&&Number.isFinite(v)?v:null;
  const fcrReq=fcr.status==='OK'?number(fcr.value):null,feoReq=feo.status==='OK'?number(feo.value):null;
  const fcrCur=number(reserves.fcrConstituted),feoCur=number(reserves.feoConstituted);
  const coverage=(cur,req)=>cur!==null&&req>0?cur/req*100:null;
  const difference=(cur,req)=>cur!==null&&req!==null?cur-req:null;
  const status=(cur,req)=>cur===null||req===null?'Pendente':cur<req?'Insuficiente':'Constituído — verificar governança';
  const hasDeficit=(fcrReq!==null&&fcrCur!==null&&fcrCur<fcrReq)||(feoReq!==null&&feoCur!==null&&feoCur<feoReq);
  const findings=[...fcr.findings,...feo.findings];
  if(fcr.findings.some(f=>f.code==='FCR_NOMINAL_CONFLICT'))findings.push({code:'NOMINAL_CAPITAL_DIVERGENCE',message:'Capital nominal da conta e da apuração divergem. Reconcilie os registros; nenhuma base foi escolhida automaticamente.'});
  return {accountId:view.budgetScope?.accountId||null,periodId:view.budgetScope?.periodId||null,
    currency:context?.status==='OK'?context.value.currency:null,
    capital:fcr.status==='OK'?number(fcr.base):null,masterCapital:fcr.status==='OK'?number(fcr.base):null,
    fcrReq,feoReq,fcrCur,feoCur,fcrStatus:status(fcrCur,fcrReq),feoStatus:status(feoCur,feoReq),
    fcrCoverage:coverage(fcrCur,fcrReq),feoCoverage:coverage(feoCur,feoReq),
    fcrDiff:difference(fcrCur,fcrReq),feoDiff:difference(feoCur,feoReq),hasDeficit,
    generalStatus:hasDeficit?'Déficit registrado':fcrReq===null||feoReq===null?'Requisitos não calculáveis':'Constituição informada; elegibilidade depende de governança',
    generalTone:hasDeficit?'var(--f4)':'var(--ink-dim)',status:'PENDING_GOVERNANCE',requirements:{fcr,feo},findings};
}
function fxpMoneyOrPending(value,context){return Number.isFinite(value)?fmtForexMoney(value,context):'não informado';}
function fxpReservesHTML(res){
  const row=(k,v)=>`<tr class="fxp-reserve-row"><td>${k}</td><td>${v}</td></tr>`;
  return `<details class="mc-disclosure fxp-disc fxp-reserves"><summary>Detalhes e governança das reservas</summary><div class="mc-disclosure-body"><div class="fxp-tablewrap"><table class="dtable"><tbody>
    ${row('Capital nominal explícito da Conta Mestre',fxpMoneyOrPending(res.capital,res))}
    ${row('FCR exigido pelo motor V11',fxpMoneyOrPending(res.fcrReq,res))}
    ${row('FCR constituído',fxpMoneyOrPending(res.fcrCur,res))}
    ${row('FEO apurado para seis meses de despesas reais',fxpMoneyOrPending(res.feoReq,res))}
    ${row('FEO constituído',fxpMoneyOrPending(res.feoCur,res))}
    ${row('Situação quantitativa',esc(res.generalStatus))}
    ${row('Governança',esc(res.status||'PENDING_GOVERNANCE'))}
    </tbody></table></div><ul>${(res.findings||[]).map(f=>`<li>${esc(f.message||f.code)}</li>`).join('')}</ul><p class="fxp-note">Valor calculado não resolve conflitos documentais nem concede autorização operacional. SI não substitui capital nominal; uma média mensal não substitui a apuração explícita de seis meses.</p></div></details>`;
}

// ============ PLANEJAMENTO FX · INTERFACE (tela principal própria) ============
// Renderiza dentro de #fxPlanningRoot (index.html, tela #fxplan — quinta tela
// principal da rail, mesma mecânica .tab/data-screen das demais). Quatro modos
// INTERNOS: Visão Geral · Planejamento · Realizado · Tabela.
// Nenhum cálculo financeiro vive aqui — tudo vem de window.JPWFx.engine/state.
// Terminologia obrigatória: premissa/projeção/simulação; campos PLANEJADOS e
// REALIZADOS nunca aparecem com a mesma semântica visual (badges PREMISSA/REAL).

let fxpView='overview';        // estado de UI, não persiste (padrão acctDetailOpen)
let fxpChartMode='usd';

const fxpPct=v=>Number.isFinite(v)?(v*100).toFixed(2).replace('.',',')+'%':'—';
const fxpParseNum=v=>{ const n=parseFloat(String(v??'').trim().replace(',','.')); return Number.isFinite(n)?n:null; };
const fxpParsePct=v=>{ const n=fxpParseNum(v); return n==null?null:n/100; };
const fxpErrHTML=errors=>`<div class="fxp-err" role="alert">${errors.map(e=>esc(e)).join('<br>')}</div>`;
const fxpBadge=(kind)=>kind==='REAL'
  ?'<span class="fxp-badge fxp-badge-real">REAL</span>'
  :(kind==='PROJ'?'<span class="fxp-badge fxp-badge-proj">PREMISSA</span>':'<span class="fxp-badge">'+esc(kind)+'</span>');

function fxpCurrentMonthKey(){ return new Date().toISOString().slice(0,7); }

// ---- Referência USD/BRL corrente (JPW-FGDEKM) -------------------------------
// Indicador único da tela: explica com QUE taxa o presente é convertido. Não se
// repete card a card. Nunca chama o dado de "ao vivo": a fonte publica uma
// referência por dia útil, então mostramos a data econômica (referenceDate) e,
// separadamente, quando consultamos (fetchedAt).
const fxpQuote=()=>(window.JPWMarket&&window.JPWMarket.usdBrl)?window.JPWMarket.usdBrl:null;
function fxpFmtRef(d){
  if(!d) return '—';
  const p=String(d).split('-');
  return p.length===3?`${p[2]}/${p[1]}/${p[0]}`:String(d);
}
function fxpFmtHora(ts){
  return ts?new Date(ts).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}):'—';
}
function fxpQuoteHTML(){
  const m=fxpQuote(); if(!m) return '';
  const q=m.get(), carregando=m.isLoading();
  // O botão só sinaliza disponibilidade; quem narra o estado é a mensagem. Ter
  // os dois dizendo "Consultando…" imprimia o texto duas vezes seguidas.
  const btn=`<button type="button" class="reset-btn fxp-quote-btn" id="fxpQuoteRefresh"${carregando?' disabled':''}>Atualizar cotação</button>`;
  if(carregando && q.status==='unavailable')
    return `<div class="fxp-quote" id="fxpQuoteBox" role="status"><span class="fxp-quote-lbl">USD/BRL de referência</span><span class="fxp-quote-msg">Consultando referência…</span>${btn}</div>`;
  if(q.status==='unavailable')
    return `<div class="fxp-quote fxp-quote-off" id="fxpQuoteBox" role="status">
      <span class="fxp-quote-lbl">USD/BRL de referência</span>
      <span class="fxp-quote-msg">Indisponível — valores presentes exibidos em USD. A premissa de câmbio futuro não é usada para marcar o presente.</span>${btn}</div>`;
  const velha=q.status==='stale';
  return `<div class="fxp-quote${velha?' fxp-quote-stale':''}" id="fxpQuoteBox" role="status">
    <span class="fxp-quote-lbl">USD/BRL de referência</span>
    <span class="fxp-quote-val">R$ ${q.rate.toFixed(4).replace('.',',')}</span>
    <span class="fxp-quote-meta">Referência ${fxpFmtRef(q.referenceDate)} · consultado às ${fxpFmtHora(q.fetchedAt)}</span>
    ${velha?'<span class="fxp-quote-tag">consulta desatualizada — revalidando</span>':''}
    ${btn}</div>`;
}
function fxpBindQuote(root){
  const m=fxpQuote(); if(!m) return;
  const b=root.querySelector('#fxpQuoteRefresh');
  if(b) b.addEventListener('click',()=>m.refresh(true));
}
// Registrado UMA vez: se ficasse dentro do render, cada repintura empilharia
// mais um ouvinte e a tela entraria em laço.
var fxpQuoteWired=false;
function fxpWireQuoteOnce(){
  const m=fxpQuote(); if(!m || fxpQuoteWired) return;
  fxpQuoteWired=true;
  m.onChange(()=>{ if(fxpView==='overview') renderFxPlanning(); });
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible' && fxpView==='overview') m.refresh(false);
  });
}

// ---- Formulário de criação (estado vazio) -----------------------------------
function fxpCreateFormHTML(){
  return `
  <p class="fxp-note" style="margin-bottom:14px">Nenhum planejamento ativo. O Planejamento FX registra a trajetória patrimonial
  Forex em três camadas separadas: <b>premissas</b> (o que você assume), <b>realizado</b> (o que aconteceu) e
  <b>normativo</b> (o que o Estatuto exige das reservas). As premissas aprovadas aqui viram o <b>baseline
  congelado</b> do plano — revisões futuras nunca o sobrescrevem.</p>
  <div class="params-grid">
    <div class="field"><label for="fxpName">Nome do planejamento</label><input type="text" id="fxpName" placeholder="ex.: Trajetória Família 10 anos"></div>
    <div class="field"><label for="fxpStart">Mês inicial</label><input type="month" id="fxpStart" value="${fxpCurrentMonthKey()}"></div>
    <div class="field"><label for="fxpHorizon">Horizonte (meses)</label><input type="number" min="1" max="600" step="1" id="fxpHorizon" value="60"><span class="note">Livre: 12, 36, 60, 120…</span></div>
    <div class="field"><label for="fxpInitial">Saldo inicial (USD)</label><input type="number" step="0.01" id="fxpInitial" placeholder="0.00"><span class="note">Parâmetro do planejamento — não altera a Conta Mestre nem o patrimônio institucional.</span></div>
    <div class="field"><label for="fxpDefaultRate">Rentabilidade planejada (% a.m.)</label><input type="text" id="fxpDefaultRate" placeholder="ex.: 1,50"><span class="note">Premissa sua, não meta do Estatuto nem promessa.</span></div>
    <div class="field"><label for="fxpProjFx">Câmbio projetado (R$/USD · opcional)</label><input type="text" id="fxpProjFx" placeholder="ex.: 5,40"><span class="note">Premissa para exibir projeções em BRL.</span></div>
    <div class="field"><label for="fxpRecPersonal">Aporte pessoal mensal planejado (USD · opcional)</label><input type="number" step="0.01" id="fxpRecPersonal" placeholder="0.00"></div>
    <div class="field"><label for="fxpRecProp">Aporte Prop Firm mensal planejado (USD · opcional)</label><input type="number" step="0.01" id="fxpRecProp" placeholder="0.00"></div>
  </div>
  <div id="fxpCreateErr"></div>
  <button class="unlock-phase-btn" id="fxpCreateBtn" style="margin-top:10px">Aprovar planejamento (congela o baseline)</button>
  <p class="expl" style="margin-top:10px;font-size:var(--fs-sm);color:var(--ink-faint)">Convenção documentada: a rentabilidade do mês incide sobre o saldo de abertura; aportes entram depois do resultado.</p>`;
}
function fxpRecurringMap(start,horizon,personal,prop){
  const map={};
  if((personal||0)>0||(prop||0)>0)
    for(let t=0;t<horizon;t++) map[fxAddMonths(start,t)]={personalUsd:personal||0,propUsd:prop||0};
  return map;
}
function fxpBindCreate(root){
  const btn=root.querySelector('#fxpCreateBtn'); if(!btn) return;
  btn.addEventListener('click',()=>{
    const g=id=>root.querySelector('#'+id).value;
    const start=fxMonthKey(g('fxpStart')), horizon=Math.round(fxpParseNum(g('fxpHorizon'))||0);
    const assumptions={
      startMonth:start, horizonMonths:horizon,
      initialBalanceUsd:fxpParseNum(g('fxpInitial'))||0,
      defaultMonthlyReturn:fxpParsePct(g('fxpDefaultRate')),
      projectedFxRate:fxpParseNum(g('fxpProjFx')),
      plannedContributions:fxpRecurringMap(start,horizon,fxpParseNum(g('fxpRecPersonal')),fxpParseNum(g('fxpRecProp')))
    };
    if(assumptions.defaultMonthlyReturn==null){ root.querySelector('#fxpCreateErr').innerHTML=fxpErrHTML(['Informe a rentabilidade planejada em % ao mês.']); return; }
    const res=window.JPWFx.state.fxPlanCreate({name:g('fxpName'),assumptions});
    if(!res.ok){ root.querySelector('#fxpCreateErr').innerHTML=fxpErrHTML(res.errors); return; }
    renderFxPlanning();
  });
}

// ---- Barra de modos ---------------------------------------------------------
// Padrão de abas completo (JPW-PNMKTS · P10): antes existiam role="tablist" e
// role="tab" sem tabpanel, sem aria-controls e sem teclado — anunciava-se como
// abas sem se comportar como abas. Agora tab↔panel estão associados, o foco é
// roving (só a aba ativa fica tabulável) e setas/Home/End navegam.
const FXP_MODES=[['overview','Visão Geral'],['planning','Planejamento'],['actuals','Realizado'],['table','Tabela']];
function fxpModesHTML(){
  return `<div class="fxp-modes" role="tablist" aria-label="Modos do Planejamento FX">`+FXP_MODES.map(([k,label])=>
    `<button type="button" class="reset-btn fxp-mode${fxpView===k?' fxp-mode-on':''}" role="tab"
      id="fxpTab-${k}" aria-controls="fxpPanel-${k}" aria-selected="${fxpView===k}"
      tabindex="${fxpView===k?'0':'-1'}" data-fxp-view="${k}">${label}</button>`).join('')+`</div>`;
}
function fxpBindTabs(root){
  const tabs=[...root.querySelectorAll('[data-fxp-view]')];
  const go=k=>{ fxpView=k; renderFxPlanning();
    const t=document.getElementById('fxpTab-'+k); if(t) t.focus(); };
  tabs.forEach(b=>b.addEventListener('click',()=>{ fxpView=b.dataset.fxpView; renderFxPlanning(); }));
  const bar=root.querySelector('.fxp-modes'); if(!bar) return;
  bar.addEventListener('keydown',ev=>{
    const i=FXP_MODES.findIndex(([k])=>k===fxpView); if(i<0) return;
    let n=null;
    if(ev.key==='ArrowRight'||ev.key==='ArrowDown') n=(i+1)%FXP_MODES.length;
    else if(ev.key==='ArrowLeft'||ev.key==='ArrowUp') n=(i-1+FXP_MODES.length)%FXP_MODES.length;
    else if(ev.key==='Home') n=0;
    else if(ev.key==='End') n=FXP_MODES.length-1;
    if(n==null) return;
    ev.preventDefault(); go(FXP_MODES[n][0]);
  });
}

// ---- Visão Geral ------------------------------------------------------------
function fxpOverviewHTML(live){
  const ov=live, plan=live.plan;
  const cb=ov.costBasis;
  const res=window.JPWFx.state.fxReservePanelData();
  const todayKey=fxpCurrentMonthKey();
  const baseToday=ov.baseline.filter(r=>r.month<=todayKey).slice(-1)[0]||null;
  const dev=ov.deviationUsd;
  // Desvio nunca comunicado só por cor (P6/§15): o sinal do número e a palavra
  // acima/abaixo carregam a informação sem depender de matiz.
  const devWord=dev==null?'':(dev>=0?'acima do baseline':'abaixo do baseline');
  return `
  <div class="fxp-kpis fxp-kpis-a">
    <div class="metric"><div class="k">Patrimônio do plano ${ov.lastClosedMonth?fxpBadge('REAL'):fxpBadge('PROJ')}</div><div class="v">${fmtMoney2(ov.currentBalanceUsd)}</div></div>
    <div class="metric"><div class="k">Baseline para ${ov.lastClosedMonth||(baseToday?baseToday.month:'—')} ${fxpBadge('PROJ')}</div><div class="v">${ov.baselineBalanceAtLastClose!=null?fmtMoney2(ov.baselineBalanceAtLastClose):(baseToday?fmtMoney2(baseToday.close):'—')}</div></div>
    <div class="metric"><div class="k">Desvio vs baseline</div><div class="v" style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${dev!=null?`${fmtMoney2(dev)} · ${ov.deviationPct!=null?fxpPct(ov.deviationPct):'—'}`:'— sem mês fechado'}</div>${dev!=null?`<div class="sub">${devWord}</div>`:''}</div>
  </div>
  ${fxpQuoteHTML()}
  <div class="fxp-chart-head">
    <h3>Trajetória patrimonial — baseline × projeção vigente × realizado</h3>
    <span class="fxp-spacer"></span>
    <button type="button" class="reset-btn fxp-mode${fxpChartMode==='usd'?' fxp-mode-on':''}" data-fxp-cur="usd" aria-pressed="${fxpChartMode==='usd'}">USD</button>
    <button type="button" class="reset-btn fxp-mode${fxpChartMode==='brl'?' fxp-mode-on':''}" data-fxp-cur="brl" aria-pressed="${fxpChartMode==='brl'}">BRL</button>
  </div>
  <div id="fxpMainChart"></div>
  <p class="fxp-note" id="fxpMainChartSummary"></p>
  <div class="fxp-kpis fxp-kpis-c">
    <div class="metric"><div class="k">Aportes realizados ${fxpBadge('REAL')}</div><div class="v">${fmtMoney2(ov.contributedTotalUsd)}</div><div class="sub">pessoal ${fmtMoney2(ov.contributedPersonalUsd)} · prop ${fmtMoney2(ov.contributedPropUsd)}</div></div>
    <div class="metric"><div class="k">Câmbio médio de aquisição</div><div class="v">${cb.weightedAverageFx!=null?'R$ '+cb.weightedAverageFx.toFixed(4).replace('.',','):'—'}</div>${cb.weightedAverageFx!=null?`<div class="sub">${'R$ '+Math.round(cb.totalBrlInvested).toLocaleString('pt-BR')} → ${fmtMoney2(cb.totalUsdAcquired)}</div>`:''}</div>
    <div class="metric"><div class="k">FCR (Art. 13.1) — cobertura</div><div class="v" style="color:${res.fcrStatus==='Regular'?'var(--f1)':'var(--f4)'}">${fxpPct(res.fcrCoverage/100)}</div><div class="sub">${esc(res.fcrStatus)}</div></div>
    <div class="metric"><div class="k">FEO (Art. 13.2) — cobertura temporal</div><div class="v" style="color:${res.feoStatus==='Regular'?'var(--f1)':'var(--f4)'}">${res.feoMonths.toFixed(1).replace('.',',')} meses</div><div class="sub">${esc(res.feoStatus)}</div></div>
  </div>
  <h3 class="fxp-h3-spaced">Rentabilidade mensal — planejado × realizado</h3>
  <div id="fxpReturnsChart"></div>
  <div id="fxpReservesPanel">${fxpReservesHTML(res)}</div>`;
}
// Camada D (P4/P5): os cards FCR/FEO acima já são o resumo; a tabela estatutária
// completa desce para disclosure, eliminando a duplicação perceptiva. Abaixo de
// 700px o CSS converte cada linha em rótulo→valor: antes, no mobile, a coluna de
// valores nascia fora da tela e a tabela mostrava apenas os rótulos.
function fxpReservesHTML(res){
  const row=(k,v)=>`<tr class="fxp-reserve-row"><td style="color:var(--ink-dim)">${k}</td><td>${v}</td></tr>`;
  return `
  <details class="mc-disclosure fxp-disc fxp-reserves">
  <summary><span class="t">Detalhes das reservas estatutárias</span><span class="chev">▾</span></summary>
  <div class="mc-disclosure-body">
  <div class="fxp-tablewrap"><table class="dtable" style="font-size:calc(11px * var(--fs-scale))"><tbody>
    ${row('Capital nominal da Conta Mestre (fonte: parâmetros do período)',fmtMoney2(res.capital))}
    ${row('FCR mínimo exigido — 15% (Art. 13.1)',fmtMoney2(res.fcrReq))}
    ${row('FCR constituído (declarado no Formulário de Início)',fmtMoney2(res.fcrCur))}
    ${row('Cobertura FCR',`<span style="color:${res.fcrStatus==='Regular'?'var(--f1)':'var(--f4)'}">${fxpPct(res.fcrCoverage/100)} · ${esc(res.fcrStatus)}${res.fcrDiff<0?' · déficit '+fmtMoney2(-res.fcrDiff):''}</span>`)}
    ${row('Despesas mensais elegíveis (declaradas)',fmtMoney2(res.monthly))}
    ${row('FEO mínimo exigido — 6 meses (Art. 13.2)',fmtMoney2(res.feoReq))}
    ${row('FEO constituído (declarado)',fmtMoney2(res.feoCur))}
    ${row('Cobertura FEO',`<span style="color:${res.feoStatus==='Regular'?'var(--f1)':'var(--f4)'}">${fxpPct(res.feoCoverage/100)} · ${res.feoMonths.toFixed(1).replace('.',',')} meses · ${esc(res.feoStatus)}${res.feoDiff<0?' · déficit '+fmtMoney2(-res.feoDiff):''}</span>`)}
    ${row('Situação geral',`<span style="color:${res.generalTone}">${esc(res.generalStatus)}</span>`)}
  </tbody></table></div>
  <p class="expl" style="font-size:var(--fs-sm);color:var(--ink-faint);margin-top:6px">Hierarquia de capitalização (Art. 13.3): I — recompor FCR; II — constituir FEO; III — reservas estratégicas; IV — dividendos/realocação. Este painel calcula e informa; nenhuma movimentação é executada. Valores constituídos são revisados em ⚙ Configurações → Formulário de Início.</p>
  </div></details>`;
}

// ---- Planejamento (premissas vigentes) --------------------------------------
function fxpPlanningHTML(live){
  const plan=live.plan, cur=plan.current, base=plan.baseline;
  const ovr=(obj)=>Object.entries(obj).map(([k,v])=>`${k}=${(v*100).toFixed(2).replace('.',',')}%`).join('; ');
  return `
  <p class="fxp-note">Baseline congelado em <b>${esc((base.frozenAt||'').slice(0,10)||'—')}</b> · ${plan.revisions.length} revisão(ões) de premissas registradas.
  Revisar premissas altera apenas a <b>projeção futura</b> — o baseline original e os meses realizados permanecem intactos para comparação.</p>
  <h3 class="fxp-h3">Premissas principais</h3>
  <div class="params-grid">
    <div class="field"><label>Mês inicial · horizonte · saldo inicial ${fxpBadge('PROJ')}</label><input type="text" value="${esc(base.startMonth)} · ${base.horizonMonths} meses · ${fmtMoney2(base.initialBalanceUsd)}" disabled><span class="note">Estruturais — congelados com o baseline.</span></div>
    <div class="field"><label for="fxpEditRate">Rentabilidade padrão vigente (% a.m.)</label><input type="text" id="fxpEditRate" value="${(cur.defaultMonthlyReturn*100).toFixed(2).replace('.',',')}"></div>
    <div class="field"><label for="fxpEditProjFx">Câmbio projetado (R$/USD)</label><input type="text" id="fxpEditProjFx" value="${cur.projectedFxRate!=null?String(cur.projectedFxRate).replace('.',','):''}" placeholder="ex.: 5,40"><span class="note">Premissa de projeção — nunca reescreve o custo histórico de aquisição.</span></div>
    <div class="field"><label for="fxpEditRecPersonal">Aporte pessoal mensal planejado (USD)</label><input type="number" step="0.01" id="fxpEditRecPersonal" placeholder="mantém plano atual"><span class="note">Se preenchido, substitui o planejado de TODOS os meses ainda abertos.</span></div>
    <div class="field"><label for="fxpEditRecProp">Aporte Prop Firm mensal planejado (USD)</label><input type="number" step="0.01" id="fxpEditRecProp" placeholder="mantém plano atual"></div>
    <div class="field"><label for="fxpEditNote">Nota da revisão</label><input type="text" id="fxpEditNote" placeholder="motivo da mudança de premissa"></div>
  </div>
  <details class="mc-disclosure fxp-disc">
    <summary><span class="t">Configurações avançadas — exceções por ano e por mês</span><span class="chev">▾</span></summary>
    <div class="mc-disclosure-body">
      <div class="params-grid">
        <div class="field"><label for="fxpEditYearOvr">Overrides por ano</label><input type="text" id="fxpEditYearOvr" value="${esc(ovr(cur.yearOverrides))}" placeholder="2028=1,20%; 2029=1,00%" aria-describedby="fxpYearOvrEcho"><span class="note">Formato AAAA=%; separados por ponto e vírgula.</span><span class="note" id="fxpYearOvrEcho"></span></div>
        <div class="field"><label for="fxpEditMonthOvr">Overrides por mês</label><input type="text" id="fxpEditMonthOvr" value="${esc(ovr(cur.monthOverrides))}" placeholder="2028-03=0,80%" aria-describedby="fxpMonthOvrEcho"><span class="note">Precedência: mês &gt; ano &gt; padrão.</span><span class="note" id="fxpMonthOvrEcho"></span></div>
      </div>
    </div>
  </details>
  <div id="fxpPlanningErr"></div>
  <button class="unlock-phase-btn fxp-actions" id="fxpReviseBtn">Salvar premissas vigentes (preserva baseline)</button>
  <div class="fxp-danger">
    <h4>Zona de perigo</h4>
    <p class="fxp-note">Excluir o planejamento remove plano, fechamentos e ledger de aportes do Planejamento FX (o restante do terminal não é afetado). Digite <b>EXCLUIR</b> para habilitar.</p>
    <div class="fxp-danger-row">
      <input type="text" id="fxpDeleteConfirm" placeholder="EXCLUIR" aria-label="Digite EXCLUIR para confirmar">
      <button class="reset-btn" id="fxpDeleteBtn" style="color:var(--f4);border-color:var(--f4)">Excluir planejamento</button>
    </div>
    <div id="fxpDeleteErr"></div>
  </div>`;
}
function fxpParseOverrides(str,monthly){
  const out={};
  String(str||'').split(';').map(s=>s.trim()).filter(Boolean).forEach(pair=>{
    const [k,v]=pair.split('=').map(s=>String(s||'').trim());
    const rate=fxpParsePct(String(v||'').replace('%',''));
    if(rate==null) return;
    if(monthly?fxMonthKey(k):/^\d{4}$/.test(k)) out[monthly?fxMonthKey(k):k]=rate;
  });
  return out;
}
function fxpBindPlanning(root,live){
  const q=id=>root.querySelector('#'+id);
  // Afordância dos overrides (P7): o campo é texto livre com sintaxe própria, e
  // nada dizia ao operador se ele acertou. O eco devolve o que o MESMO parser do
  // salvamento entendeu — sem tocar em schema, domínio ou formato persistido.
  const echo=(inputId,echoId,monthly)=>{
    const inp=q(inputId), out=q(echoId); if(!inp||!out) return;
    const render=()=>{
      const bruto=String(inp.value||'').split(';').map(s=>s.trim()).filter(Boolean);
      const lido=fxpParseOverrides(inp.value,monthly);
      const chaves=Object.keys(lido).sort();
      if(!bruto.length){ out.textContent='Nenhuma exceção — todos os meses usam a rentabilidade padrão.'; out.style.color=''; return; }
      const desc=chaves.map(k=>`${k} = ${(lido[k]*100).toFixed(2).replace('.',',')}%`).join(' · ');
      const perdidos=bruto.length-chaves.length;
      out.textContent=(chaves.length?`Entendido: ${desc}.`:'Nada reconhecido.')
        +(perdidos>0?` ${perdidos} trecho(s) não reconhecido(s) e ignorado(s) ao salvar.`:'');
      out.style.color=perdidos>0?'var(--f4)':'';
    };
    inp.addEventListener('input',render); render();
  };
  echo('fxpEditYearOvr','fxpYearOvrEcho',false);
  echo('fxpEditMonthOvr','fxpMonthOvrEcho',true);
  q('fxpReviseBtn').addEventListener('click',()=>{
    const plan=live.plan, cur=plan.current;
    const rate=fxpParsePct(q('fxpEditRate').value);
    if(rate==null){ q('fxpPlanningErr').innerHTML=fxpErrHTML(['Rentabilidade padrão inválida.']); return; }
    const recP=fxpParseNum(q('fxpEditRecPersonal').value), recF=fxpParseNum(q('fxpEditRecProp').value);
    let planned=cur.plannedContributions;
    if(recP!=null||recF!=null){
      planned={...cur.plannedContributions};
      const openFrom=live.nextOpenMonth||plan.baseline.startMonth;
      for(let t=0;t<plan.baseline.horizonMonths;t++){
        const m=fxAddMonths(plan.baseline.startMonth,t);
        if(m<openFrom) continue; // meses fechados mantêm o planejado da época
        const prev=planned[m]||{personalUsd:0,propUsd:0};
        planned[m]={personalUsd:recP!=null?recP:prev.personalUsd,propUsd:recF!=null?recF:prev.propUsd};
      }
    }
    const res=window.JPWFx.state.fxPlanReviseAssumptions({
      defaultMonthlyReturn:rate,
      yearOverrides:fxpParseOverrides(q('fxpEditYearOvr').value,false),
      monthOverrides:fxpParseOverrides(q('fxpEditMonthOvr').value,true),
      projectedFxRate:fxpParseNum(q('fxpEditProjFx').value),
      plannedContributions:planned
    },q('fxpEditNote').value);
    if(!res.ok){ q('fxpPlanningErr').innerHTML=fxpErrHTML(res.errors); return; }
    renderFxPlanning();
  });
  q('fxpDeleteBtn').addEventListener('click',()=>{
    if(q('fxpDeleteConfirm').value.trim()!=='EXCLUIR'){ q('fxpDeleteErr').innerHTML=fxpErrHTML(['Digite EXCLUIR para confirmar.']); return; }
    const res=window.JPWFx.state.fxPlanDelete();
    if(!res.ok){ q('fxpDeleteErr').innerHTML=fxpErrHTML(res.errors); return; }
    renderFxPlanning();
  });
}

// ---- Realizado (fechamento mensal + aportes) --------------------------------
function fxpActualsHTML(live){
  const plan=live.plan, next=live.nextOpenMonth;
  const closed=Object.keys(plan.actuals).sort();
  const contribs=plan.contributions.slice().sort((a,b)=>a.month.localeCompare(b.month)||String(a.createdAt).localeCompare(String(b.createdAt)));
  return `
  <div class="fxp-task">
  <h3 class="fxp-h3">Fechamento mensal ${fxpBadge('REAL')}</h3>
  <div class="params-grid">
    <div class="field"><label for="fxpActMonth">Mês</label>
      <select id="fxpActMonth">
        ${next?`<option value="${next}">${next} — próximo aberto</option>`:''}
        ${closed.map(m=>`<option value="${m}">${m} — editar fechado</option>`).join('')}
      </select><span class="note">Fechamentos são contíguos; editar mês fechado é auditado.</span></div>
    <div class="field"><label for="fxpActType">Entrada original</label>
      <select id="fxpActType"><option value="rate">Rentabilidade (%)</option><option value="usd">Resultado (USD)</option></select>
      <span class="note">O outro campo é derivado — mesma álgebra do MEI (resultado ÷ saldo de abertura).</span></div>
    <div class="field"><label for="fxpActValue">Valor</label><input type="text" id="fxpActValue" placeholder="ex.: -0,70 ou 1234,56"></div>
    <div class="field"><label for="fxpActFx">Câmbio de valuation (R$/USD · opcional)</label><input type="text" id="fxpActFx" placeholder="cotação do mês"><span class="note">Só para exibir o mês em BRL — não é custo de aquisição.</span></div>
    <div class="field fxp-field-wide"><label for="fxpActNotes">Observação do período</label><input type="text" id="fxpActNotes" placeholder="contexto do mês"></div>
  </div>
  <div id="fxpActErr"></div>
  <button class="unlock-phase-btn fxp-actions" id="fxpActBtn">${next?`Fechar ${next}`:'Editar mês selecionado'}</button>
  ${next?'':'<p class="fxp-note" style="color:var(--ink-dim)">Horizonte completamente fechado — apenas edição auditada disponível.</p>'}
  </div>
  <!-- P9: o ledger é tarefa distinta do fechamento. Seção PRÓPRIA e recolhível
       (o ticket admite "seção própria ou disclosure"), aberta por padrão: o
       fechamento vem primeiro e não exige atravessar o ledger, mas o registro
       continua visível — esconder por padrão o histórico de aportes trocaria um
       problema de hierarquia por um de descoberta. A contagem fica no rótulo. -->
  <details class="mc-disclosure fxp-disc" open>
  <summary><span class="t">Aportes realizados — ledger cambial (${contribs.length} lançamento${contribs.length===1?'':'s'})</span><span class="chev">▾</span></summary>
  <div class="mc-disclosure-body">
  <div class="params-grid">
    <div class="field"><label for="fxpCMonth">Mês</label><input type="month" id="fxpCMonth" value="${next||closed.slice(-1)[0]||plan.baseline.startMonth}"></div>
    <div class="field"><label for="fxpCSource">Origem</label><select id="fxpCSource"><option value="personal">Aporte pessoal</option><option value="prop">Prop Firm / origem operacional</option></select></div>
    <div class="field"><label for="fxpCCurrency">Moeda de origem</label><select id="fxpCCurrency"><option value="BRL">BRL (compra de USD)</option><option value="USD">USD nativo</option></select>
      <span class="note">BRL entra no custo médio; USD nativo (ex.: crédito de prop firm) fica fora dele.</span></div>
    <div class="field"><label for="fxpCAmount">Valor na moeda de origem</label><input type="text" id="fxpCAmount" placeholder="ex.: 10000,00"></div>
    <div class="field" id="fxpCRateField"><label for="fxpCRate">Câmbio efetivamente pago (R$/USD)</label><input type="text" id="fxpCRate" placeholder="ex.: 5,00"><span class="note">USD adquirido = BRL ÷ taxa.</span></div>
  </div>
  <div id="fxpCErr"></div>
  <button class="unlock-phase-btn fxp-actions" id="fxpCBtn">Registrar aporte</button>
  <div class="fxp-tablewrap" style="margin-top:12px"><table class="dtable" style="font-size:calc(11px * var(--fs-scale))">
    <thead><tr><th>Mês</th><th>Origem</th><th>Moeda</th><th>Valor origem</th><th>Taxa aquisição</th><th>USD</th><th>Custo médio?</th><th></th></tr></thead>
    <tbody>${contribs.length?contribs.map(c=>`<tr>
      <td class="hl">${esc(c.month)}</td><td>${c.source==='prop'?'Prop Firm':'Pessoal'}</td><td>${esc(c.originalCurrency)}</td>
      <td>${c.originalCurrency==='BRL'?'R$ '+(+c.originalAmount).toLocaleString('pt-BR',{minimumFractionDigits:2}):fmtMoney2(c.originalAmount||c.usdAmount)}</td>
      <td>${c.acquisitionFxRate!=null?'R$ '+(+c.acquisitionFxRate).toFixed(4).replace('.',','):'—'}</td>
      <td>${fmtMoney2(c.usdAmount)}</td>
      <td>${c.affectsFxCostBasis?'entra':'não entra'}</td>
      <td><button type="button" class="reset-btn fxp-del" data-fxp-del="${esc(c.id)}" aria-label="Remover aporte de ${esc(c.month)}">remover</button></td>
    </tr>`).join(''):'<tr><td colspan="8" style="color:var(--ink-faint)">Nenhum aporte registrado — indicadores permanecem “—” até existir lançamento real.</td></tr>'}</tbody>
  </table></div>
  </div></details>`;
}
function fxpBindActuals(root,live){
  const q=id=>root.querySelector('#'+id);
  const monthSel=q('fxpActMonth');
  const prefill=()=>{
    const rec=live.plan.actuals[monthSel.value];
    if(!rec){ q('fxpActValue').value=''; q('fxpActNotes').value=''; q('fxpActFx').value=''; return; }
    q('fxpActType').value=rec.inputType;
    q('fxpActValue').value=rec.inputType==='usd'?String(rec.profitUsd).replace('.',','):String((rec.returnRate*100).toFixed(4)).replace('.',',');
    q('fxpActFx').value=rec.valuationFxRate!=null?String(rec.valuationFxRate).replace('.',','):'';
    q('fxpActNotes').value=rec.notes||'';
  };
  monthSel.addEventListener('change',prefill); prefill();
  q('fxpActBtn').addEventListener('click',()=>{
    const type=q('fxpActType').value;
    const val=type==='usd'?fxpParseNum(q('fxpActValue').value):fxpParsePct(q('fxpActValue').value);
    if(val==null){ q('fxpActErr').innerHTML=fxpErrHTML(['Informe o valor do mês (percentual ou USD conforme a entrada).']); return; }
    const res=window.JPWFx.state.fxPlanRecordActual(monthSel.value,{
      inputType:type, returnRate:type==='rate'?val:null, profitUsd:type==='usd'?val:null,
      valuationFxRate:fxpParseNum(q('fxpActFx').value), notes:q('fxpActNotes').value});
    if(!res.ok){ q('fxpActErr').innerHTML=fxpErrHTML(res.errors); return; }
    renderFxPlanning();
  });
  const curSel=q('fxpCCurrency');
  const syncRate=()=>{ q('fxpCRateField').style.display=curSel.value==='BRL'?'':'none'; };
  curSel.addEventListener('change',syncRate); syncRate();
  q('fxpCBtn').addEventListener('click',()=>{
    const res=window.JPWFx.state.fxPlanAddContribution({
      month:fxMonthKey(q('fxpCMonth').value), source:q('fxpCSource').value,
      originalCurrency:curSel.value, originalAmount:fxpParseNum(q('fxpCAmount').value)||0,
      acquisitionFxRate:curSel.value==='BRL'?fxpParseNum(q('fxpCRate').value):null});
    if(!res.ok){ q('fxpCErr').innerHTML=fxpErrHTML(res.errors); return; }
    renderFxPlanning();
  });
  root.querySelectorAll('[data-fxp-del]').forEach(b=>b.addEventListener('click',()=>{
    const res=window.JPWFx.state.fxPlanRemoveContribution(b.dataset.fxpDel);
    if(res.ok) renderFxPlanning();
  }));
}

// ---- Tabela mensal + resumo anual ------------------------------------------
function fxpTableHTML(live){
  const ov=live;
  const baseByMonth={}; ov.baseline.forEach(r=>{baseByMonth[r.month]=r;});
  const rows=ov.forecast.map(r=>{
    const b=baseByMonth[r.month];
    const dev=b?r.close-b.close:null;
    const real=r.phase==='actual';
    return `<tr>
      <td class="hl">${r.month}</td>
      <td>${real?fxpBadge('REAL'):fxpBadge('PROJ')}${real&&r.derivedField?`<span class="fxp-derived" title="entrada original: ${r.inputType==='usd'?'resultado USD':'taxa %'}">${r.inputType==='usd'?'$→%':'%→$'}</span>`:''}</td>
      <td>${b?fmtMoney2(b.open):'—'}</td><td>${b?fxpPct(b.rate):'—'}</td><td>${b?fmtMoney2(b.profit):'—'}</td><td>${b?fmtMoney2(b.contributionUsd):'—'}</td><td>${b?fmtMoney2(b.close):'—'}</td>
      <td>${fmtMoney2(r.open)}</td><td>${fxpPct(r.rate)}</td><td>${fmtMoney2(r.profit)}</td><td>${fmtMoney2(r.personalUsd)}</td><td>${fmtMoney2(r.propUsd)}</td><td>${fmtMoney2(r.close)}</td>
      <td style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${dev!=null?fmtMoney2(dev):'—'}</td>
      <td style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${(dev!=null&&b&&b.close!==0)?fxpPct(dev/b.close):'—'}</td>
    </tr>`;
  }).join('');
  const annual=fxAnnualSummary(ov.forecast);
  const annualFx=fxAnnualFxSummary(live.plan.contributions);
  const fxByYear={}; annualFx.forEach(a=>{fxByYear[a.year]=a;});
  return `
  <p class="fxp-note" style="font-size:var(--fs-sm);color:var(--ink-dim)">BASELINE = premissas originais congeladas ${fxpBadge('PROJ')} · VIGENTE = realizado ${fxpBadge('REAL')} até o último fechamento e projeção com premissas atuais dali em diante. Meses realizados exibem a direção da derivação ($→% ou %→$).</p>
  <div class="fxp-tablewrap"><table class="dtable" style="font-size:calc(10.5px * var(--fs-scale))">
    <thead>
      <tr><th rowspan="2">Mês</th><th rowspan="2">Fase</th><th colspan="5">BASELINE (plano original)</th><th colspan="6">VIGENTE (realizado + projeção)</th><th colspan="2">Desvio</th></tr>
      <tr><th>Inicial</th><th>%</th><th>Res.</th><th>Aportes</th><th>Final</th><th>Inicial</th><th>%</th><th>Res.</th><th>Ap. pessoal</th><th>Ap. prop</th><th>Final</th><th>USD</th><th>%</th></tr>
    </thead>
    <tbody>${rows}</tbody>
  </table></div>
  <h3 style="margin:16px 0 6px;font-size:calc(13px * var(--fs-scale))">Resumo anual (derivado automaticamente)</h3>
  <div class="fxp-tablewrap"><table class="dtable" style="font-size:calc(11px * var(--fs-scale))">
    <thead><tr><th>Ano</th><th>Meses</th><th>Saldo inicial</th><th>Resultado</th><th>Rent. composta</th><th>Ap. pessoal</th><th>Ap. prop</th><th>Saldo final</th><th>BRL convertido</th><th>USD adquirido</th><th>Câmbio médio/ano</th></tr></thead>
    <tbody>${annual.map(a=>{
      const f=fxByYear[a.year];
      return `<tr><td class="hl">${a.year}</td><td>${a.phases.actual?`${a.phases.actual} real${a.phases.forecast?` + ${a.phases.forecast} proj`:''}`:`${a.months} proj`}</td>
        <td>${fmtMoney2(a.open)}</td><td>${fmtMoney2(a.profitUsd)}</td><td>${fxpPct(a.composedReturn)}</td>
        <td>${fmtMoney2(a.personalUsd)}</td><td>${fmtMoney2(a.propUsd)}</td><td>${fmtMoney2(a.close)}</td>
        <td>${f?'R$ '+Math.round(f.brlInvested).toLocaleString('pt-BR'):'—'}</td><td>${f?fmtMoney2(f.usdAcquired):'—'}</td>
        <td>${f&&f.weightedAverageFx!=null?'R$ '+f.weightedAverageFx.toFixed(4).replace('.',','):'—'}</td></tr>`;
    }).join('')}</tbody>
  </table></div>
  <details style="margin-top:12px"><summary style="cursor:pointer;font-size:var(--fs-sm);color:var(--ink-dim)">Trilha de auditoria do Planejamento FX (últimos eventos)</summary>
    <div style="font-family:var(--mono);font-size:calc(10.5px * var(--fs-scale));color:var(--ink-dim);line-height:1.8;margin-top:6px">
      ${(S.fxPlanning.auditLog||[]).slice(-10).reverse().map(e=>`${esc(String(e.ts||'').slice(0,16).replace('T',' '))} · ${esc(e.type)}${e.month?' · '+esc(e.month):''} · ${esc(e.detail||'')}`).join('<br>')||'—'}
    </div>
  </details>`;
}

// ---- Render principal -------------------------------------------------------
function renderFxPlanning(){
  const root=document.getElementById('fxPlanningRoot'); if(!root) return;
  const live=window.JPWFx.state.fxOverviewLive();
  if(!live){ root.innerHTML=fxpCreateFormHTML(); fxpBindCreate(root); return; }
  const body=fxpView==='overview'?fxpOverviewHTML(live)
    :fxpView==='planning'?fxpPlanningHTML(live)
    :fxpView==='actuals'?fxpActualsHTML(live)
    :fxpTableHTML(live);
  root.innerHTML=`
    <p class="fxp-note" style="margin-bottom:10px"><b>${esc(live.plan.name)}</b> · ${esc(live.plan.baseline.startMonth)} + ${live.plan.baseline.horizonMonths} meses ·
    ${live.lastClosedMonth?`fechado até <b>${live.lastClosedMonth}</b> · próximo aberto <b>${live.nextOpenMonth||'—'}</b>`:'nenhum mês fechado ainda'}</p>
    ${fxpModesHTML()}
    <div class="fxp-section" role="tabpanel" id="fxpPanel-${fxpView}" aria-labelledby="fxpTab-${fxpView}" tabindex="0">${body}</div>`;
  fxpBindTabs(root);
  if(fxpView==='overview'){
    // Cadência: entrada na tela + volta à visibilidade + TTL + botão manual.
    // Sem polling — refresh(false) respeita o TTL e o cooldown de falha.
    fxpWireQuoteOnce();
    fxpBindQuote(root);
    const m=fxpQuote(); if(m) m.refresh(false);
    root.querySelectorAll('[data-fxp-cur]').forEach(b=>b.addEventListener('click',()=>{ fxpChartMode=b.dataset.fxpCur; renderFxPlanning(); }));
    window.JPWFx.charts.fxDrawMainChart(root.querySelector('#fxpMainChart'),live.plan,live,fxpChartMode);
    const summary=root.querySelector('#fxpMainChartSummary');
    if(summary) summary.textContent=window.JPWFx.charts.fxMainChartSummaryText(live.plan,live,fxpChartMode);
    window.JPWFx.charts.fxDrawReturnsChart(root.querySelector('#fxpReturnsChart'),live);
  }
  if(fxpView==='planning') fxpBindPlanning(root,live);
  if(fxpView==='actuals') fxpBindActuals(root,live);
}
window.JPWFx.ui={renderFxPlanning};
// Primeira pintura + repintura ao entrar na tela (dados normativos do painel de
// reservas podem ter mudado via Formulário de Início).
renderFxPlanning();
document.querySelectorAll('.tab[data-screen="fxplan"]').forEach(t=>t.addEventListener('click',()=>renderFxPlanning()));

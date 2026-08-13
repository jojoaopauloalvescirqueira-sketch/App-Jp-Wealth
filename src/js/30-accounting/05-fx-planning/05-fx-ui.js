// ============ PLANEJAMENTO FX · INTERFACE (tela principal própria) ============
// Renderiza dentro de #fxPlanningRoot (index.html, tela #fxplan — quinta tela
// principal da rail, mesma mecânica .tab/data-screen das demais). Quatro modos
// INTERNOS: Visão Geral · Planejamento · Realizado · Histórico.
// Nenhum cálculo financeiro vive aqui — tudo vem de window.JPWFx.engine/state.
// Terminologia obrigatória: premissa/projeção/simulação; campos PLANEJADOS e
// REALIZADOS nunca aparecem com a mesma semântica visual (badges PREMISSA/REAL).

let fxpView='overview';        // estado de UI, não persiste (padrão acctDetailOpen)
let fxpChartMode='usd';
// Janela de exibição do gráfico em meses (1c). Recorte VISUAL sobre a série já
// calculada — nunca toca horizonte, baseline, projeção ou persistência. Não
// persiste, como os demais estados de UI desta tela.
let fxpHorizonWin=24;
// Filtro do Histórico (1g): 'all' | 'actual' | 'forecast'. Recorte de leitura,
// não de dado — o resumo anual segue calculado sobre o horizonte inteiro.
let fxpHistFilter='all';

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
// Estado vazio (1h): as três camadas explicadas à esquerda com o vocabulário de
// badges do produto, formulário à direita em três blocos. Todos os ids são os
// mesmos — fxpBindCreate e o teste dependem deles; muda a arrumação, não o
// contrato de DOM.
function fxpCreateFormHTML(){
  return `
  <div class="fxp-grid-empty">
  <aside class="fxp-col-side">
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Nenhum planejamento ativo</h3></div>
      <!-- Fase 2C: as três camadas descem para disclosure, como no protótipo
             ("Como as três camadas funcionam ▾"). O texto continua íntegro;
             o formulário de criação passa a ser a leitura primária do cartão. -->
        <details class="jp-p3">
          <summary>Como as três camadas funcionam</summary>
          <h4 class="fxp-empty-h">Três camadas que nunca se misturam</h4>
      <p class="fxp-note">O Planejamento FX registra a trajetória patrimonial Forex separando o que você assume, o que aconteceu e o que o Estatuto exige.</p>
      <div class="fxp-layer"><div class="fxp-layer-h">Premissas ${fxpBadge('PROJ')}</div>
        <p class="fxp-note">O que você assume: rentabilidade mensal, câmbio projetado e aportes planejados. Ao aprovar, viram o <b>baseline congelado</b> — revisões futuras nunca o sobrescrevem.</p></div>
      <div class="fxp-layer"><div class="fxp-layer-h">Realizado ${fxpBadge('REAL')}</div>
        <p class="fxp-note">Fechamentos mensais contíguos e ledger cambial de aportes. O custo médio do dólar usa média ponderada Σ BRL ÷ Σ USD; créditos USD nativos não o contaminam.</p></div>
      <div class="fxp-layer"><div class="fxp-layer-h">Normativo</div>
        <p class="fxp-note">FCR (Art. 13.1) e FEO (Art. 13.2) calculados pela mesma função do Formulário de Início. Este painel calcula e informa — nenhuma movimentação é executada.</p></div>
        </details>
      <p class="expl" style="font-size:var(--fs-xs);color:var(--ink-faint);margin:10px 0 0;line-height:1.55">Rentabilidade planejada é premissa sua — não deriva de perfis de risco nem constitui promessa de retorno.</p>
    </section>
  </aside>

  <div class="fxp-col-main">
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Identidade do plano</h3></div>
      <div class="params-grid">
        <div class="field"><label for="fxpName">Nome do planejamento</label><input type="text" id="fxpName" placeholder="ex.: Trajetória Família 10 anos"></div>
        <div class="field"><label for="fxpStart">Mês inicial</label><input type="month" id="fxpStart" value="${fxpCurrentMonthKey()}"></div>
        <div class="field"><label for="fxpHorizon">Horizonte (meses)</label><input type="number" min="1" max="600" step="1" id="fxpHorizon" value="60"><span class="note">Livre: 12, 36, 60, 120…</span></div>
      </div>
    </section>
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Ponto de partida</h3><span class="art">não altera a Conta Mestre</span></div>
      <div class="params-grid">
        <div class="field"><label for="fxpInitial">Saldo inicial (USD)</label><input type="number" step="0.01" id="fxpInitial" placeholder="0.00"><span class="note">Parâmetro do planejamento — não altera a Conta Mestre nem o patrimônio institucional.</span></div>
      </div>
    </section>
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Premissas</h3><span class="art">${fxpBadge('PROJ')}</span></div>
      <div class="params-grid">
        <div class="field"><label for="fxpDefaultRate">Rentabilidade planejada (% a.m.)</label><input type="text" id="fxpDefaultRate" placeholder="ex.: 1,50"><span class="note">Premissa sua, não meta do Estatuto.</span></div>
        <div class="field"><label for="fxpProjFx">Câmbio projetado (R$/USD)</label><input type="text" id="fxpProjFx" placeholder="ex.: 5,40"><span class="note">Opcional — só para exibir projeções em BRL.</span></div>
        <div class="field"><label for="fxpRecPersonal">Aporte pessoal mensal (USD)</label><input type="number" step="0.01" id="fxpRecPersonal" placeholder="0.00"><span class="note">Opcional.</span></div>
        <div class="field"><label for="fxpRecProp">Aporte Prop Firm mensal (USD)</label><input type="number" step="0.01" id="fxpRecProp" placeholder="0.00"><span class="note">Opcional.</span></div>
      </div>
      <div id="fxpCreateErr"></div>
      <button class="unlock-phase-btn fxp-actions" id="fxpCreateBtn">Aprovar planejamento</button>
      <p class="expl" style="margin-top:8px;font-size:var(--fs-xs);color:var(--ink-faint);line-height:1.55">Congela o baseline. A rentabilidade do mês incide sobre o saldo de abertura; aportes entram depois do resultado.</p>
    </section>
  </div>
  </div>`;
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
// A chave 'table' permanece — é contrato de DOM (id do painel, data-fxp-view e
// teste). Só o rótulo muda para Histórico, que é o que a tela faz (1g).
const FXP_MODES=[['overview','Visão Geral'],['planning','Planejamento'],['actuals','Realizado'],['table','Histórico']];
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
  const congelado=(plan.baseline.frozenAt||'').slice(0,10).split('-').reverse().join('/');
  const baseMes=ov.lastClosedMonth||(baseToday?baseToday.month:'—');
  // Média realizada para o subtítulo do gráfico mensal — leitura, não cálculo
  // novo: é a média aritmética das taxas dos meses já fechados.
  const reais=(ov.forecast||[]).filter(r=>r.phase==='actual');
  const mediaReal=reais.length?reais.reduce((a,r)=>a+(r.rate||0),0)/reais.length:null;
  const planejado=plan.current.defaultMonthlyReturn;
  const nAportes=(plan.contributions||[]).length;
  return `
  <div class="fxp-grid2">
  <div class="fxp-col-main">
    <!-- Ordem do herói conforme 1c: patrimônio, DESVIO, baseline. O desvio no
         meio porque é a leitura que responde "como estou" — o baseline é a
         referência que sustenta essa comparação, não um número autônomo. -->
    <div class="fxp-kpis fxp-kpis-a">
      <div class="metric"><div class="k">Patrimônio do plano ${ov.lastClosedMonth?fxpBadge('REAL'):fxpBadge('PROJ')}</div><div class="v">${fmtMoney2(ov.currentBalanceUsd)}</div><div class="sub">${ov.lastClosedMonth?'fechado em '+esc(ov.lastClosedMonth):'nenhum mês fechado'}</div></div>
      <div class="metric"><div class="k">Desvio vs baseline</div><div class="v" style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${dev!=null?fmtMoney2(dev):'—'}</div><div class="sub">${dev!=null?`${ov.deviationPct!=null?fxpPct(ov.deviationPct):'—'} · ${devWord}`:'sem mês fechado'}</div></div>
      <div class="metric"><div class="k">Baseline para ${esc(baseMes)} ${fxpBadge('PROJ')}</div><div class="v">${ov.baselineBalanceAtLastClose!=null?fmtMoney2(ov.baselineBalanceAtLastClose):(baseToday?fmtMoney2(baseToday.close):'—')}</div><div class="sub">${congelado?'congelado '+esc(congelado):'—'}</div></div>
    </div>

    <section class="fxp-block">
      <div class="fxp-block-head">
        <h3>Trajetória patrimonial</h3>
        <span class="art">baseline × projeção vigente × realizado</span>
        <span class="fxp-spacer"></span>
        ${fxpHorizonHTML(plan)}
        <button type="button" class="reset-btn fxp-mode${fxpChartMode==='usd'?' fxp-mode-on':''}" data-fxp-cur="usd" aria-pressed="${fxpChartMode==='usd'}">USD</button>
        <button type="button" class="reset-btn fxp-mode${fxpChartMode==='brl'?' fxp-mode-on':''}" data-fxp-cur="brl" aria-pressed="${fxpChartMode==='brl'}">BRL</button>
      </div>
      <div id="fxpMainChart"></div>
      <p class="fxp-note" id="fxpMainChartSummary"></p>
    </section>

    <section class="fxp-block">
      <div class="fxp-block-head">
        <h3>Rentabilidade mensal</h3>
        <span class="art">planejado ${planejado!=null?fxpPct(planejado)+' a.m.':'—'} × realizado${mediaReal!=null?', média '+fxpPct(mediaReal):''}</span>
      </div>
      <div id="fxpReturnsChart"></div>
    </section>

    <div class="fxp-kpis fxp-kpis-c">
      <div class="metric"><div class="k">Aportes realizados ${fxpBadge('REAL')}</div><div class="v">${fmtMoney2(ov.contributedTotalUsd)}</div><div class="sub">pessoal ${fmtMoney2(ov.contributedPersonalUsd)} · prop ${fmtMoney2(ov.contributedPropUsd)}</div></div>
    </div>
  </div>

  <aside class="fxp-col-side">
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Reservas estatutárias</h3><span class="art">Art. 13</span></div>
      ${fxpCovHTML('FCR · 13.1 — fundo de contingência',res.fcrCoverage,res.fcrStatus,
        `constituído ${fmtMoney2(res.fcrCur)} · exigido ${fmtMoney2(res.fcrReq)}`+(res.fcrDiff<0?` · déficit ${fmtMoney2(-res.fcrDiff)}`:''))}
      ${fxpCovHTML('FEO · 13.2 — fundo de estabilidade',res.feoCoverage,res.feoStatus,
        `${res.feoMonths.toFixed(1).replace('.',',')} de 6,0 meses`+(res.feoDiff<0?` · déficit ${fmtMoney2(-res.feoDiff)}`:''))}
      <p class="expl" style="font-size:var(--fs-xs);color:var(--ink-faint);margin:10px 0 0;line-height:1.55">Hierarquia de capitalização (Art. 13.3): recompor FCR, depois constituir FEO. Este painel calcula e informa — nenhuma movimentação é executada.</p>
      <button type="button" class="fxp-linkish" id="fxpGoOnboarding" style="margin-top:8px">Revisar no Formulário de Início</button>
      <div id="fxpReservesPanel">${fxpReservesHTML(res)}</div>
    </section>

    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Ledger cambial</h3></div>
      <dl class="fxp-pairs">
        <dt>Câmbio médio de aquisição</dt><dd class="hl">${cb.weightedAverageFx!=null?'R$ '+cb.weightedAverageFx.toFixed(4).replace('.',','):'—'}</dd>
        <dt>BRL convertido</dt><dd>${cb.totalBrlInvested?'R$ '+Math.round(cb.totalBrlInvested).toLocaleString('pt-BR'):'—'}</dd>
        <dt>USD adquirido</dt><dd>${cb.totalUsdAcquired?fmtMoney2(cb.totalUsdAcquired):'—'}</dd>
        <dt>Crédito USD nativo (prop)</dt><dd>${fmtMoney2(ov.contributedPropUsd)}</dd>
      </dl>
      ${fxpQuoteHTML()}
      <p class="expl" style="font-size:var(--fs-xs);color:var(--ink-faint);margin:10px 0 0;line-height:1.55">Σ BRL ÷ Σ USD, média ponderada. Crédito USD nativo não entra no custo médio.</p>
      <button type="button" class="fxp-linkish" id="fxpGoLedger" style="margin-top:8px">Ver ${nAportes} lançamento${nAportes===1?'':'s'} ›</button>
    </section>
  </aside>
  </div>`;
}
// Barra de cobertura normativa. O rótulo textual acompanha sempre — estado
// normativo nunca é comunicado só pela cor da barra.
function fxpCovHTML(rotulo,cobertura,status,meta){
  const reg=status==='Regular';
  const cor=reg?'var(--f1)':'var(--f4)';
  const larg=Math.max(0,Math.min(100,cobertura||0));
  return `<div class="fxp-cov">
    <div class="fxp-cov-top"><span class="fxp-cov-lbl">${esc(rotulo)}</span><span class="fxp-cov-val" style="color:${cor}">${fxpPct((cobertura||0)/100)}</span></div>
    <div class="fxp-cov-bar"><div class="fxp-cov-fill" style="width:${larg.toFixed(1)}%;background:${cor}"></div></div>
    <div class="fxp-cov-meta">${meta} · <span style="color:${cor}">${esc(status)}</span></div>
  </div>`;
}
// Janela de exibição do gráfico (1c). É recorte VISUAL da série já calculada:
// não altera horizonte, baseline, projeção nem nada persistido.
function fxpHorizonHTML(plan){
  const H=plan.baseline.horizonMonths;
  const ops=[...new Set([12,24,60,H].filter(n=>n<=H))].sort((a,b)=>a-b);
  if(ops.length<2) return '';
  return ops.map(n=>`<button type="button" class="reset-btn fxp-mode${fxpHorizonWin===n?' fxp-mode-on':''}" data-fxp-win="${n}" aria-pressed="${fxpHorizonWin===n}">${n}m</button>`).join('');
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
  const congeladoEm=(base.frozenAt||'').slice(0,10).split('-').reverse().join('/');
  const nFechados=(live.forecast||[]).filter(r=>r.phase==='actual').length;
  const ovr=(obj)=>Object.entries(obj).map(([k,v])=>`${k}=${(v*100).toFixed(2).replace('.',',')}%`).join('; ');
  return `
  <p class="fxp-note">Baseline congelado em <b>${esc((base.frozenAt||'').slice(0,10)||'—')}</b> · ${plan.revisions.length} revisão(ões) de premissas registradas.
  Revisar premissas altera apenas a <b>projeção futura</b> — o baseline original e os meses realizados permanecem intactos para comparação.</p>
  <div class="fxp-grid2">
  <div class="fxp-col-main">
  <!-- 1e: estruturais e revisáveis deixam de compartilhar a mesma grade. O que
       está congelado não aparece como campo desabilitado no meio dos editáveis
       — vira leitura, com a data do congelamento. -->
  <section class="fxp-block">
    <div class="fxp-block-head"><h3>Estruturais</h3><span class="art">congelados com o baseline${congeladoEm?' em '+esc(congeladoEm):''} — não editáveis</span></div>
    <dl class="fxp-pairs">
      <dt>Mês inicial</dt><dd>${esc(base.startMonth)}</dd>
      <dt>Horizonte</dt><dd>${base.horizonMonths} meses</dd>
      <dt>Saldo inicial (USD)</dt><dd class="hl">${fmtMoney2(base.initialBalanceUsd)}</dd>
    </dl>
  </section>
  <section class="fxp-block">
  <div class="fxp-block-head"><h3>Revisáveis</h3><span class="art">alteram apenas a projeção futura</span></div>
  <div class="params-grid">
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
  <button class="unlock-phase-btn fxp-actions" id="fxpReviseBtn">Salvar premissas vigentes</button>
  <p class="fxp-note" style="margin-top:6px">preserva o baseline e os ${nFechados} ${nFechados===1?'mês já fechado':'meses já fechados'}</p>
  </section>
  <div class="fxp-danger">
    <h4>Zona de perigo</h4>
    <p class="fxp-note">Excluir o planejamento remove plano, fechamentos e ledger de aportes do Planejamento FX (o restante do terminal não é afetado). Digite <b>EXCLUIR</b> para habilitar.</p>
    <div class="fxp-danger-row">
      <input type="text" id="fxpDeleteConfirm" placeholder="EXCLUIR" aria-label="Digite EXCLUIR para confirmar">
      <button class="reset-btn" id="fxpDeleteBtn" style="color:var(--f4);border-color:var(--f4)">Excluir planejamento</button>
    </div>
    <div id="fxpDeleteErr"></div>
  </div>
  </div>

  <aside class="fxp-col-side">
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Efeito da revisão sobre a projeção</h3><span class="art">${fxpBadge('PROJ')}</span></div>
      <dl class="fxp-pairs" id="fxpRevPreview">
        <dt>Vigente antes da revisão</dt><dd id="fxpRevBefore">—</dd>
        <dt>Com as premissas na tela</dt><dd class="hl" id="fxpRevAfter">—</dd>
        <dt>Baseline congelado</dt><dd id="fxpRevBase">—</dd>
      </dl>
      <p class="fxp-derived-preview" id="fxpRevDelta" aria-live="polite"></p>
      <p class="expl" style="font-size:var(--fs-xs);color:var(--ink-faint);margin:10px 0 0;line-height:1.55">Rentabilidade planejada é premissa sua — não deriva de perfil de risco nem constitui promessa de retorno.</p>
    </section>
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Revisões registradas</h3><span class="art">${plan.revisions.length}</span></div>
      ${plan.revisions.length?`<dl class="fxp-pairs">${plan.revisions.slice().reverse().map(rv=>
        `<dt>${esc(String(rv.supersededAt||'').slice(0,10))}</dt><dd>${esc(rv.note||'revisão de premissas')}</dd>`).join('')}</dl>`
        :'<p class="fxp-note" style="margin:0">Nenhuma revisão desde o congelamento do baseline.</p>'}
    </section>
  </aside>
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

  // Prévia do efeito da revisão (1e). Mesmo princípio da prévia do fechamento:
  // as premissas digitadas viram um conjunto CANDIDATO e quem projeta é o motor
  // (fxForecastTimeline já aceita assumptions). Nada é salvo, nada é revisado —
  // o baseline e os meses fechados seguem intactos até o botão ser apertado.
  const fim=serie=>{ const r=(serie||[])[(serie||[]).length-1]; return r?r.close:null; };
  const antes=fim(live.forecast), baseFim=fim(live.baseline);
  const previaRevisao=()=>{
    const E=window.JPWFx.engine; if(!E) return;
    const put=(id,txt)=>{ const e=q(id); if(e) e.textContent=txt; };
    put('fxpRevBefore',antes!=null?fmtMoney2(antes):'—');
    put('fxpRevBase',baseFim!=null?fmtMoney2(baseFim):'—');
    const taxa=fxpParsePct(q('fxpEditRate').value);
    if(taxa==null){ put('fxpRevAfter','—'); put('fxpRevDelta','Informe a rentabilidade para simular.'); return; }
    const anos=fxpParseOverrides(q('fxpEditYearOvr').value,false);
    const meses=fxpParseOverrides(q('fxpEditMonthOvr').value,true);
    const candidatas={...live.plan.current, defaultMonthlyReturn:taxa,
      yearOverrides:anos, monthOverrides:meses,
      projectedFxRate:fxpParseNum(q('fxpEditProjFx').value)};
    let depois=null;
    try{ depois=fim(E.fxForecastTimeline(live.plan,{assumptions:candidatas})); }catch(_){ }
    put('fxpRevAfter',depois!=null?fmtMoney2(depois):'—');
    const nExc=Object.keys(anos).length+Object.keys(meses).length;
    const delta=(depois!=null&&antes!=null)?depois-antes:null;
    const excTxt=nExc?`${nExc} exceç${nExc===1?'ão digitada':'ões digitadas'}, ainda não salva${nExc===1?'':'s'}`:'';
    // "+$0,00" é ruído: quando nada mudou, dizer que nada mudou.
    if(delta==null) put('fxpRevDelta',excTxt);
    else if(Math.abs(delta)<0.005) put('fxpRevDelta',excTxt||'Sem alteração em relação às premissas vigentes.');
    else put('fxpRevDelta',`${delta>0?'+':''}${fmtMoney2(delta)} ao fim do horizonte`+(excTxt?` · ${excTxt}`:''));
  };
  ['fxpEditRate','fxpEditProjFx','fxpEditYearOvr','fxpEditMonthOvr'].forEach(id=>{
    const e=q(id); if(e) e.addEventListener('input',previaRevisao);
  });
  previaRevisao();
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
  <!-- 1f: o mês aberto vira cartão de tarefa no topo, na gramática do
       .mc-exec-clearance do Execution Board — diz QUAL mês, sobre QUE saldo o
       resultado incide e por que a ordem importa, antes de qualquer campo. -->
  <section class="fxp-taskcard">
    <div class="fxp-taskcard-head">
      <span class="fxp-taskcard-lbl">${next?'Próximo mês aberto':'Horizonte fechado'}</span>
      <span class="fxp-taskcard-val">${esc(next||'—')}</span>
    </div>
    <p class="fxp-taskcard-txt">${next
      ?`Fechamentos são contíguos. Saldo de abertura <b>${fmtMoney2(fxpOpeningBalance(live,next))}</b> — o resultado do mês incide sobre ele e os aportes entram depois.`
      :'Todos os meses do horizonte estão fechados. Apenas edição auditada de mês já fechado permanece disponível.'}</p>
  </section>
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
  <!-- Prévia do derivado: calculada pelo MOTOR sobre um plano candidato, nunca
       por aritmética reescrita aqui. Nada é persistido enquanto não se fecha. -->
  <p class="fxp-derived-preview" id="fxpActPreview" aria-live="polite"></p>
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
// Saldo de abertura do mês alvo, lido da série que o motor já produziu: é o
// fechamento do mês anterior, ou o saldo inicial quando nada foi fechado.
function fxpOpeningBalance(live,mes){
  const reais=(live.forecast||[]).filter(r=>r.phase==='actual');
  const alvo=(live.forecast||[]).find(r=>r.month===mes);
  if(alvo) return alvo.open;
  const ultima=reais[reais.length-1];
  return ultima?ultima.close:live.plan.baseline.initialBalanceUsd;
}
// Prévia do fechamento (1f). Monta um plano CANDIDATO em memória e pede ao
// motor a linha do mês — o derivado e o saldo final saem da mesma função que
// produz o realizado de verdade. Não reescrevemos a álgebra aqui e nada toca
// S nem save().
function fxpPreviewActual(live,mes,entrada){
  const E=window.JPWFx.engine, M=window.JPWFx.model;
  if(!E||!M||!mes) return null;
  const plan=live.plan;
  const candidato={...plan, actuals:{...(plan.actuals||{}), [mes]:M.fxNormalizeActual(entrada)}};
  let linhas; try{ linhas=E.fxActualTimeline(candidato); }catch(_){ return null; }
  const linha=(linhas||[]).find(r=>r.month===mes);
  return linha||null;
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
  // Prévia ao vivo do derivado e do saldo final estimado.
  const previa=()=>{
    const el=q('fxpActPreview'); if(!el) return;
    const tipo=q('fxpActType').value;
    const bruto=tipo==='usd'?fxpParseNum(q('fxpActValue').value):fxpParsePct(q('fxpActValue').value);
    if(bruto==null){ el.textContent=''; return; }
    const linha=fxpPreviewActual(live,monthSel.value,{
      inputType:tipo, returnRate:tipo==='rate'?bruto:null, profitUsd:tipo==='usd'?bruto:null,
      valuationFxRate:fxpParseNum(q('fxpActFx').value), notes:''});
    if(!linha){ el.textContent=''; return; }
    const derivado=tipo==='usd'
      ? `taxa derivada ${fxpPct(linha.rate)}`
      : `resultado derivado ${fmtMoney2(linha.profit)}`;
    el.textContent=`${derivado} · saldo final estimado ${fmtMoney2(linha.close)}`;
  };
  ['fxpActType','fxpActValue','fxpActFx'].forEach(id=>{
    const e=q(id); if(e){ e.addEventListener('input',previa); e.addEventListener('change',previa); }
  });
  monthSel.addEventListener('change',()=>{ prefill(); previa(); }); prefill(); previa();
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
  // Filtro do 1g: recorte de LEITURA sobre as linhas já calculadas. Nenhuma
  // série é recalculada e nada é escondido do resumo anual, que continua sobre
  // o horizonte inteiro — filtrar a auditoria mudaria o que ela audita.
  const visiveis=ov.forecast.filter(r=>
    fxpHistFilter==='actual'?r.phase==='actual'
    :fxpHistFilter==='forecast'?r.phase!=='actual':true);
  const rows=visiveis.map(r=>{
    const b=baseByMonth[r.month];
    const dev=b?r.close-b.close:null;
    const real=r.phase==='actual';
    return `<tr>
      <td class="hl">${r.month}</td>
      <td>${real?fxpBadge('REAL'):fxpBadge('PROJ')}${real&&r.derivedField?`<span class="fxp-derived" title="entrada original: ${r.inputType==='usd'?'resultado USD':'taxa %'}">${r.inputType==='usd'?'$→%':'%→$'}</span>`:''}</td>
      <td class="fxg-b">${b?fmtMoney2(b.open):'—'}</td><td class="fxg-b">${b?fxpPct(b.rate):'—'}</td><td class="fxg-b">${b?fmtMoney2(b.profit):'—'}</td><td class="fxg-b">${b?fmtMoney2(b.contributionUsd):'—'}</td><td class="fxg-b">${b?fmtMoney2(b.close):'—'}</td>
      <td class="fxg-v">${fmtMoney2(r.open)}</td><td class="fxg-v">${fxpPct(r.rate)}</td><td class="fxg-v">${fmtMoney2(r.profit)}</td><td class="fxg-v">${fmtMoney2(r.personalUsd)}</td><td class="fxg-v">${fmtMoney2(r.propUsd)}</td><td class="fxg-v">${fmtMoney2(r.close)}</td>
      <td class="fxg-d" style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${dev!=null?fmtMoney2(dev):'—'}</td>
      <td class="fxg-d" style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${(dev!=null&&b&&b.close!==0)?fxpPct(dev/b.close):'—'}</td>
    </tr>`;
  }).join('');
  const annual=fxAnnualSummary(ov.forecast);
  const annualFx=fxAnnualFxSummary(live.plan.contributions);
  const fxByYear={}; annualFx.forEach(a=>{fxByYear[a.year]=a;});
  const filtros=[['all','Todos'],['actual','Só realizados'],['forecast','Só projetados']];
  return `
  <div class="fxp-modes fxp-histfilter" role="group" aria-label="Filtro do histórico">${filtros.map(([k,l])=>
    `<button type="button" class="reset-btn fxp-mode${fxpHistFilter===k?' fxp-mode-on':''}" data-fxp-hist="${k}" aria-pressed="${fxpHistFilter===k}">${l}</button>`).join('')}
    <span class="fxp-histcount">${visiveis.length} de ${ov.forecast.length} meses</span></div>
  <p class="fxp-note" style="font-size:var(--fs-sm);color:var(--ink-dim)">BASELINE = premissas originais congeladas ${fxpBadge('PROJ')} · VIGENTE = realizado ${fxpBadge('REAL')} até o último fechamento e projeção com premissas atuais dali em diante. Meses realizados exibem a direção da derivação ($→% ou %→$).</p>
  <div class="fxp-tablewrap"><table class="dtable fxp-hist" style="font-size:calc(10.5px * var(--fs-scale))">
    <thead>
      <tr><th rowspan="2">Mês</th><th rowspan="2">Fase</th><th colspan="5" class="fxg-b">BASELINE · plano original</th><th colspan="6" class="fxg-v">VIGENTE · realizado + projeção</th><th colspan="2" class="fxg-d">Desvio</th></tr>
      <tr><th class="fxg-b">Inicial</th><th class="fxg-b">%</th><th class="fxg-b">Resultado</th><th class="fxg-b">Aportes</th><th class="fxg-b">Final</th><th class="fxg-v">Inicial</th><th class="fxg-v">%</th><th class="fxg-v">Resultado</th><th class="fxg-v">Ap. pessoal</th><th class="fxg-v">Ap. prop</th><th class="fxg-v">Final</th><th class="fxg-d">USD</th><th class="fxg-d">%</th></tr>
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
    root.querySelectorAll('[data-fxp-win]').forEach(b=>b.addEventListener('click',()=>{ fxpHorizonWin=+b.dataset.fxpWin; renderFxPlanning(); }));
    // Atalhos da lateral: levam para onde o dado é editado, sem duplicar formulário.
    const ob=root.querySelector('#fxpGoOnboarding');
    if(ob) ob.addEventListener('click',()=>{
      // Guarda por typeof: no monólito reduzido o módulo de Configurações pode
      // não estar presente, e o botão não pode quebrar a tela.
      if(typeof openSettingsModal==='function') openSettingsModal('general',ob);
    });
    const led=root.querySelector('#fxpGoLedger');
    if(led) led.addEventListener('click',()=>{ fxpView='actuals'; renderFxPlanning(); });
    // Recorte visual da janela: fatia as séries JÁ calculadas. O motor não é
    // consultado de novo e nada persistido muda.
    const nWin=Math.min(fxpHorizonWin||live.forecast.length,live.forecast.length);
    const janela=nWin<live.forecast.length
      ? {...live, forecast:live.forecast.slice(0,nWin), baseline:live.baseline.slice(0,nWin)}
      : live;
    window.JPWFx.charts.fxDrawMainChart(root.querySelector('#fxpMainChart'),live.plan,janela,fxpChartMode);
    const summary=root.querySelector('#fxpMainChartSummary');
    if(summary) summary.textContent=window.JPWFx.charts.fxMainChartSummaryText(live.plan,janela,fxpChartMode);
    // Estado máximo (≥1120) abre o segundo gráfico; abaixo disso ele nasce
    // recolhido. Medido no container real, não na janela — é o painel que sabe
    // quanto espaço tem. O usuário pode abrir a qualquer largura.
    const caixa=root.querySelector('#fxpReturnsBox');
    if(caixa) caixa.open=root.clientWidth>=1120;
    window.JPWFx.charts.fxDrawReturnsChart(root.querySelector('#fxpReturnsChart'),live);
  }
  if(fxpView==='table')
    root.querySelectorAll('[data-fxp-hist]').forEach(b=>b.addEventListener('click',()=>{ fxpHistFilter=b.dataset.fxpHist; renderFxPlanning(); }));
  if(fxpView==='planning') fxpBindPlanning(root,live);
  if(fxpView==='actuals') fxpBindActuals(root,live);
}
window.JPWFx.ui={renderFxPlanning};
// Primeira pintura + repintura ao entrar na tela (dados normativos do painel de
// reservas podem ter mudado via Formulário de Início).
renderFxPlanning();
document.querySelectorAll('.tab[data-screen="fxplan"]').forEach(t=>t.addEventListener('click',()=>renderFxPlanning()));

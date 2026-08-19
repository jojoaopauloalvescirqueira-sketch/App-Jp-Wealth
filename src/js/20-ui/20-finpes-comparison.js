// ============ FINANÇAS PESSOAIS · COMPARATIVO MENSAL (PF-04) ============
// Renderizador do workspace #finpesComparativo. READ → DERIVE → COMPARE →
// PRESENT: consome exclusivamente pfCompMetrics/pfCompCompare/pfCompSeries.
// Nenhuma fórmula primária vive aqui; nada persiste (nem cache de KPI — a
// edição retroativa no Orçamento reflete aqui imediatamente); navegar não
// grava nem materializa. Apresentação DESCRITIVA: o módulo diz o que os dados
// demonstram, jamais avalia a pessoa ("saudável", "ruim" não existem aqui).

let fcMonth = null;

function fcCurrentKey(){
  if(!fcMonth || !pfMonthKeyValid(fcMonth)) fcMonth = pfCurrentMonthKey();
  return fcMonth;
}
function fcGoTo(key){ fcMonth = key; finpesComparisonRender(); }

const FC_METRIC_LABELS = {
  receita:'Receita recebida', despesa:'Despesa executada', sobra:'Sobra realizada',
  divida:'Dívida observada', comprometimento:'Comprometimento',
};

function fcPct(x){ return (x*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%'; }
function fcPP(x){ const v=(x*100).toLocaleString('pt-BR',{maximumFractionDigits:1}); return (x>=0?'+':'')+v+' p.p.'; }
function fcDelta(cents){ return (cents>=0?'+':'−')+formatBRLCents(Math.abs(cents)).replace('R$ ','R$ '); }

function finpesComparisonRender(){
  const root = document.getElementById('finpesComparisonRoot');
  if(!root) return;
  const key = fcCurrentKey();
  let html = `<div class="fb-header">
    <button type="button" class="reset-btn fb-nav" data-fc-nav="-1" title="Mês anterior">←</button>
    <span class="fb-month-label">${esc(pfMonthLabel(key))}</span>
    <button type="button" class="reset-btn fb-nav" data-fc-nav="1" title="Mês seguinte">→</button>
    <button type="button" class="reset-btn" data-fc-today title="Ir para o mês corrente">Hoje</button>
  </div>`;
  if(!pfMoneyUnitSupported()){
    // Read-only não autoriza reinterpretar unidade desconhecida: nenhum valor
    // é formatado como BRL. O banner do módulo (#finpesUnitNotice) já avisa.
    html += `<div class="card fb-card"><h2>Comparativo Mensal</h2>
      <p class="risk-note">Unidade monetária do agregado não reconhecida — comparativos financeiros indisponíveis. Nenhum dado foi alterado.</p></div>`;
    root.innerHTML = html;
    fcBind(root);
    return;
  }
  const bases = pfCompBaselines(key);
  html += `<div class="fc-comp-grid">`;
  html += fcCompareCardHTML('VS MÊS ANTERIOR', key, bases.previousMonth);
  html += fcCompareCardHTML('VS MESMO MÊS DO ANO ANTERIOR', key, bases.yearAgo);
  html += `</div>`;
  html += fcSeriesHTML(key);
  root.innerHTML = html;
  fcBind(root);
}

function fcCompareCardHTML(titulo, key, baseKey){
  const comp = pfCompCompare(key, baseKey);
  const linhas = Object.entries(comp.metrics).map(([nome, m])=>{
    const rotulo = FC_METRIC_LABELS[nome];
    if(!m.available)
      return `<div class="fc-mrow"><span class="fc-mname">${rotulo}</span>
        <span class="fc-na">comparação indisponível</span>
        <span class="fb-aux">${esc(m.motivo)}</span></div>`;
    if(nome==='comprometimento')
      return `<div class="fc-mrow"><span class="fc-mname">${rotulo}</span>
        <span>${fcPct(m.current)} <span class="fb-aux">vs ${fcPct(m.baseline)}</span></span>
        <span class="fc-delta">Δ ${fcPP(m.deltaPP)}</span></div>`;
    const pct = ('relativeChange' in m)
      ? (m.relativeChange!==null ? `<span class="fb-aux">${(m.relativeChange>=0?'+':'')+fcPct(m.relativeChange)}</span>`
                                 : (m.semAlteracao ? '<span class="fb-aux">sem alteração</span>' : '<span class="fb-aux">% N/A — base zero</span>'))
      : '';
    return `<div class="fc-mrow"><span class="fc-mname">${rotulo}</span>
      <span>${formatBRLCents(m.current)} <span class="fb-aux">vs ${formatBRLCents(m.baseline)}</span></span>
      <span class="fc-delta">Δ ${fcDelta(m.delta)} ${pct}</span></div>`;
  }).join('');
  return `<div class="card fb-card fc-compare" data-fc-base="${esc(baseKey)}">
    <h2>${titulo} <span class="art">${esc(pfMonthLabel(baseKey))}</span></h2>
    ${linhas}
  </div>`;
}

function fcSeriesHTML(key){
  const serie = pfCompSeries(key, 12);
  const cel = m => {
    if(m.status==='COMPLETE') return `<span class="fd-money">${formatBRLCents(m.value)}</span>`;
    if(m.status==='PARTIAL'){
      const cov = m.cov && typeof m.cov.conhecidas==='number' ? `${m.cov.conhecidas}/${m.cov.total}`
        : (m.cov && typeof m.cov.observadas==='number' ? `${m.cov.observadas}/${m.cov.relevantes}` : '');
      return (typeof m.known==='number')
        ? `<span class="fd-money">${formatBRLCents(m.known)}</span> <span class="fb-partial">parcial ${cov}</span>`
        : `<span class="fb-partial">parcial ${cov}</span>`;
    }
    return '<span class="fb-aux">—</span>';
  };
  const celRatio = m => m.status==='COMPLETE' ? `<span class="fd-money">${fcPct(m.value)}</span>`
    : (m.status==='PARTIAL' ? '<span class="fb-partial">parcial</span>' : `<span class="fb-aux">${m.motivo && m.motivo.includes('zero') ? 'N/A' : '—'}</span>`);
  const linhas = serie.map(mm => mm.materializado
    ? `<div class="fc-srow"><span>${esc(pfMonthLabel(mm.key))}</span>${['receita','despesa','sobra','divida'].map(n=>`<span>${cel(mm[n])}</span>`).join('')}<span>${celRatio(mm.comprometimento)}</span></div>`
    : `<div class="fc-srow fc-virtual"><span>${esc(pfMonthLabel(mm.key))}</span><span class="fb-aux" style="grid-column:span 5">Não registrado</span></div>`
  ).join('');
  return `<div class="card fb-card" id="fcSeries">
    <h2>Evolução — 12 meses <span class="art">derivada do estado vivo · mês não registrado é lacuna, nunca zero</span></h2>
    <div class="fc-srow fc-head"><span>Mês</span><span>Receita</span><span>Despesa</span><span>Sobra</span><span>Dívida</span><span>Compr.</span></div>
    ${linhas}
  </div>`;
}

function fcBind(root){
  root.querySelectorAll('[data-fc-nav]').forEach(b=>b.addEventListener('click',()=>{
    fcGoTo(pfMonthAdd(fcCurrentKey(), +b.dataset.fcNav));
  }));
  const hoje = root.querySelector('[data-fc-today]');
  if(hoje) hoje.addEventListener('click',()=>{ fcGoTo(pfCurrentMonthKey()); });
}

window.JPWFinComparison = { render: finpesComparisonRender };

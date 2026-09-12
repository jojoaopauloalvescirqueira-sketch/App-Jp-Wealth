// ============ FINANÇAS PESSOAIS · COMPARATIVO MENSAL (PF-04) ============
// Renderizador do workspace #finpesComparativo. READ → DERIVE → COMPARE →
// PRESENT: consome exclusivamente pfCompMetrics/pfCompCompare/pfCompSeries.
// Nenhuma fórmula primária vive aqui; nada persiste (nem cache de KPI — a
// edição retroativa no Orçamento reflete aqui imediatamente); navegar não
// grava nem materializa. Apresentação DESCRITIVA: o módulo diz o que os dados
// demonstram, jamais avalia a pessoa ("saudável", "ruim" não existem aqui).

let fcMonth = null;
let fcMetric = 'despesa';
let fcInspectedMonth = null; // exploração efêmera; nunca entra no agregado

function fcCurrentKey(){
  if(!fcMonth || !pfMonthKeyValid(fcMonth)) fcMonth = pfCurrentMonthKey();
  return fcMonth;
}
function fcGoTo(key){ fcMonth = key; fcInspectedMonth = key; finpesComparisonRender(); }

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
  const focusId = root.contains(document.activeElement) ? document.activeElement.id : '';
  const finish = () => {
    fcBind(root);
    const control = focusId && document.getElementById(focusId);
    if(control && root.contains(control)) control.focus({preventScroll:true});
  };
  const key = fcCurrentKey();
  let html = `<div class="fb-header">
    <button type="button" id="fcPrevious" class="reset-btn fb-nav" data-fc-nav="-1" title="Mês anterior" aria-label="Mês anterior">←</button>
    <span class="fb-month-label">${esc(pfMonthLabel(key))}</span>
    <button type="button" id="fcNext" class="reset-btn fb-nav" data-fc-nav="1" title="Mês seguinte" aria-label="Mês seguinte">→</button>
    <button type="button" id="fcToday" class="reset-btn" data-fc-today title="Ir para o mês corrente">Hoje</button>
  </div>`;
  if(!pfMoneyUnitSupported()){
    // Read-only não autoriza reinterpretar unidade desconhecida: nenhum valor
    // é formatado como BRL. O banner do módulo (#finpesUnitNotice) já avisa.
    html += `<div class="card fb-card"><h2>Comparativo Mensal</h2>
      <p class="risk-note">Unidade monetária do agregado não reconhecida — comparativos financeiros indisponíveis. Nenhum dado foi alterado.</p></div>`;
    root.innerHTML = html;
    finish();
    return;
  }
  // Uma leitura canônica por render: gráfico, seletor e tabela compartilham
  // exatamente as mesmas competências e os mesmos estados de cobertura.
  const serie = pfCompSeries(key, 12);
  if(!serie.some(m => m.key === fcInspectedMonth)) fcInspectedMonth = key;
  html += fcEvolutionHTML(serie);
  const bases = pfCompBaselines(key);
  html += `<div class="fc-comp-grid">`;
  html += fcCompareCardHTML('VS MÊS ANTERIOR', key, bases.previousMonth);
  html += fcCompareCardHTML('VS MESMO MÊS DO ANO ANTERIOR', key, bases.yearAgo);
  html += `</div>`;
  html += fcSeriesHTML(serie);
  root.innerHTML = html;
  finish();
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

function fcEvolutionHTML(serie){
  const metric = FC_METRIC_LABELS[fcMetric] ? fcMetric : 'despesa';
  const label = FC_METRIC_LABELS[metric];
  const unit = metric === 'comprometimento' ? '%' : 'BRL · R$';
  const format = metric === 'comprometimento' ? fcPct : formatBRLCents;
  const complete = m => m && m.status === PF_METRIC_COMPLETE && Number.isFinite(m.value);
  const selected = serie.find(m => m.key === fcInspectedMonth);
  const selectedMetric = selected && selected[metric];
  const selectedIndex = serie.indexOf(selected);
  const values = serie.filter(m => complete(m[metric])).map(m => m[metric].value);
  // Somente geometria. Nenhuma métrica primária, subtotal ou preenchimento de
  // lacuna é calculado aqui; PARTIAL/UNAVAILABLE interrompem o caminho.
  let low = values.length ? Math.min(0, ...values) : 0;
  let high = values.length ? Math.max(0, ...values) : 0;
  const scaleLow = low, scaleHigh = high;
  if(high === low){ low -= 1; high += 1; }
  const W = 720, H = 220, pad = 12;
  const X = i => pad + i / Math.max(1, serie.length - 1) * (W - 2 * pad);
  const Y = value => pad + (high - value) / (high - low) * (H - 2 * pad);
  let path = '', continuation = false;
  const points = serie.map((month, i) => {
    const value = month[metric];
    if(!complete(value)){ continuation = false; return ''; }
    const x = X(i).toFixed(2), y = Y(value.value).toFixed(2);
    path += (continuation ? ' L ' : ' M ') + x + ' ' + y;
    continuation = true;
    return `<circle data-fc-point="${esc(month.key)}" data-value="${value.value}" cx="${x}" cy="${y}" r="${month.key === fcInspectedMonth ? 5 : 3}" fill="var(--violet)" stroke="var(--panel)" stroke-width="1.5" vector-effect="non-scaling-stroke"/>`;
  }).join('');
  const status = selectedMetric && selectedMetric.status === PF_METRIC_PARTIAL
    ? pfCompStatusLabel(selectedMetric) + ' — dados incompletos; nenhum ponto é apresentado'
    : (selectedMetric && selectedMetric.motivo) || 'Dados indisponíveis';
  const readout = complete(selectedMetric)
    ? `<b>${format(selectedMetric.value)}</b> <span>· completo</span>`
    : `<span>${esc(status)}</span>`;
  const period = serie.length ? `${pfMonthLabel(serie[0].key)} a ${pfMonthLabel(serie[serie.length-1].key)}` : '';
  return `<div class="card fb-card fc-evolution" id="fcEvolution">
    <h2 id="fcChartTitle">Evolução — 12 meses <span class="art">${esc(period)}</span></h2>
    <div class="fc-chart-controls">
      <label for="fcMetric">Métrica<select id="fcMetric">${Object.entries(FC_METRIC_LABELS).map(([name, text]) => `<option value="${name}"${name === metric ? ' selected' : ''}>${text}</option>`).join('')}</select></label>
      <label for="fcMonthSelect">Mês em foco<select id="fcMonthSelect">${serie.map(m => `<option value="${esc(m.key)}"${m.key === fcInspectedMonth ? ' selected' : ''}>${esc(pfMonthLabel(m.key))}</option>`).join('')}</select></label>
    </div>
    <p class="fc-chart-readout" id="fcChartReadout" role="status" aria-live="polite"><strong>${esc(label)} · ${esc(selected ? pfMonthLabel(selected.key) : '')}</strong> ${readout}</p>
    <div class="fc-chart-scale"><span>${esc(label)} · ${unit}</span><span>${values.length ? `${format(scaleLow)} a ${format(scaleHigh)}` : 'Sem valores completos'}</span></div>
    <svg class="fc-chart" id="fcChart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img" aria-labelledby="fcChartTitle" aria-describedby="fcChartReadout fcChartNote">
      ${[pad, H/2, H-pad].map(y => `<line x1="${pad}" x2="${W-pad}" y1="${y}" y2="${y}" stroke="var(--line)" vector-effect="non-scaling-stroke"/>`).join('')}
      ${values.length ? `<line x1="${pad}" x2="${W-pad}" y1="${Y(0)}" y2="${Y(0)}" stroke="var(--ink-faint)" stroke-dasharray="4 4" vector-effect="non-scaling-stroke"/>` : ''}
      ${selectedIndex >= 0 ? `<line x1="${X(selectedIndex)}" x2="${X(selectedIndex)}" y1="${pad}" y2="${H-pad}" stroke="var(--ink-dim)" stroke-dasharray="3 4" vector-effect="non-scaling-stroke"/>` : ''}
      <path data-fc-line d="${path.trim()}" fill="none" stroke="var(--violet)" stroke-width="2" vector-effect="non-scaling-stroke"/>${points}
    </svg>
    <div class="fc-chart-axis">${[0, serie.length-1].filter(i => i >= 0).map(i => `<span>${esc(serie[i].key)}</span>`).join('')}</div>
    <p class="fc-chart-note" id="fcChartNote">${values.length} de ${serie.length} meses com valores completos. Meses não registrados, parciais ou indisponíveis são lacunas; zero declarado é um ponto. Use os seletores para consultar cada mês.</p>
  </div>`;
}

function fcSeriesHTML(serie){
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
    ? `<tr class="fc-srow"><th scope="row">${esc(pfMonthLabel(mm.key))}</th>${['receita','despesa','sobra','divida'].map(n=>`<td>${cel(mm[n])}</td>`).join('')}<td>${celRatio(mm.comprometimento)}</td></tr>`
    : `<tr class="fc-srow fc-virtual"><th scope="row">${esc(pfMonthLabel(mm.key))}</th><td class="fb-aux" colspan="5">Não registrado</td></tr>`
  ).join('');
  return `<div class="card fb-card" id="fcSeries">
    <h2>Valores — 12 meses <span class="art">BRL · comprometimento em % · mês não registrado é lacuna, nunca zero</span></h2>
    <div class="fc-table-scroll" tabindex="0" role="region" aria-label="Valores dos 12 meses">
      <table class="fc-series-table"><thead><tr class="fc-srow fc-head"><th scope="col">Mês</th><th scope="col">Receita</th><th scope="col">Despesa</th><th scope="col">Sobra</th><th scope="col">Dívida</th><th scope="col">Compr.</th></tr></thead>
      <tbody>${linhas}</tbody></table>
    </div>
  </div>`;
}

function fcBind(root){
  const metric = root.querySelector('#fcMetric');
  if(metric) metric.addEventListener('change', () => {
    if(!Object.prototype.hasOwnProperty.call(FC_METRIC_LABELS, metric.value)) return;
    fcMetric = metric.value;
    finpesComparisonRender();
  });
  const month = root.querySelector('#fcMonthSelect');
  if(month) month.addEventListener('change', () => {
    if(!pfMonthKeyValid(month.value)) return;
    fcInspectedMonth = month.value;
    finpesComparisonRender();
  });
  root.querySelectorAll('[data-fc-nav]').forEach(b=>b.addEventListener('click',()=>{
    fcGoTo(pfMonthAdd(fcCurrentKey(), +b.dataset.fcNav));
  }));
  const hoje = root.querySelector('[data-fc-today]');
  if(hoje) hoje.addEventListener('click',()=>{ fcGoTo(pfCurrentMonthKey()); });
}

window.JPWFinComparison = { render: finpesComparisonRender };

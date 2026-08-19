// ============ FINANÇAS PESSOAIS · VISÃO GERAL (PF-06) ============
// Renderizador do workspace #finpesOverview. READ → CONSUME CANONICAL
// DERIVATIONS → PRESENT: consome exclusivamente pfCompMetrics (fronteira
// canônica que já gateia mês virtual, parcialidade e receita zero),
// pfTotalAllocated/pfUnallocatedSurplus, pfCreditKPIs, pfCompCompare/
// pfCompBaselines e pfPendingBefore. Nenhuma fórmula financeira primária
// vive aqui; nada persiste (nem cache de KPI — edição retroativa nos módulos
// reflete aqui no próximo render); navegar/renderizar jamais escreve.
// Postura DESCRITIVA: diz o que os dados demonstram, jamais avalia a pessoa.
// Escopo definitivo da V1 (quatro cards): mês atual, dívida & crédito, vs mês
// anterior e pendências. Patrimônio/Inventário NÃO pertencem a Finanças
// Pessoais — são domínio próprio, com roadmap INV-* separado.
//
// Armadilha provada no Discovery: pfMonthSummary(null) fabrica completo=true
// e realizedSurplus=0 por completude vácua. Por isso este arquivo NUNCA chama
// pfMonthSummary/pfUnallocatedSurplus sem o gate de materialização — a
// fronteira é pfCompMetrics, e alocações só se leem com sobra COMPLETE.

function foPct(x){ return (x*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%'; }
function foRow(nome, corpo){
  return `<div class="fo-row"><span class="fo-name">${nome}</span><span class="fo-val">${corpo}</span></div>`;
}

// Métrica monetária no contrato COMPLETE/PARTIAL/UNAVAILABLE do pfCompMetrics.
// PARTIAL exibe o known DO HELPER com a moldura de cobertura — nunca recomputa
// subtotal, nunca o apresenta como total.
function foMoneyMetricHTML(nome, m){
  if(m.status===PF_METRIC_COMPLETE)
    return foRow(nome, `<b>${formatBRLCents(m.value)}</b>`);
  if(m.status===PF_METRIC_PARTIAL)
    return foRow(nome, `${formatBRLCents(m.known)} conhecidos <span class="fb-partial">PARCIAL ${m.cov.conhecidas}/${m.cov.total}</span>`);
  return foRow(nome, `<span class="fb-aux">${esc(m.motivo)}</span>`);
}

// ---- CARD 1 · MÊS ATUAL -----------------------------------------------------
function foMonthCardHTML(M, met){
  if(!met.materializado){
    // Mês virtual: nenhum realizado monetário e nenhuma projeção aqui (decisão
    // fechada do gate: só existe projeção recorrente de RECEITA no schema —
    // mostrar um lado só fingiria orçamento projetado completo).
    return `<div class="card fb-card fo-card"><h2>Mês atual <span class="art">${esc(pfMonthLabel(M))}</span></h2>
      <p class="fb-empty">◌ Mês ainda não registrado — nenhum realizado existe nesta competência. O registro nasce no primeiro ato do Orçamento Mensal.</p>
    </div>`;
  }
  let sobra;
  if(met.sobra.status===PF_METRIC_COMPLETE)
    sobra = foRow('Sobra realizada', `<b class="${met.sobra.value<0?'fs-neg':''}">${formatBRLCents(met.sobra.value)}</b>`);
  else
    // Parcial: NENHUM valor financeiro de sobra — knownBalance é auxiliar e
    // não se apresenta num consolidado (rotularia leitura errada).
    sobra = foRow('Sobra realizada', `<span class="fb-aux">Dados incompletos — receitas ${met.sobra.cov.income.conhecidas}/${met.sobra.cov.income.total} · despesas ${met.sobra.cov.expense.conhecidas}/${met.sobra.cov.expense.total}</span>`);
  let compr;
  if(met.comprometimento.status===PF_METRIC_COMPLETE)
    compr = foRow('Comprometimento', `<b>${foPct(met.comprometimento.value)}</b>`);
  else if(met.comprometimento.status===PF_METRIC_UNAVAILABLE)
    compr = foRow('Comprometimento', `<span class="fb-aux">${esc(met.comprometimento.motivo)}</span>`);
  else
    compr = foRow('Comprometimento', '<span class="fb-aux">N/A — cobertura incompleta</span>');
  // Destinações: exclusivamente com sobra realizada demonstrada (COMPLETE).
  let aloc = '';
  if(met.sobra.status===PF_METRIC_COMPLETE){
    const m = S.personalFinance.months[M];
    const naoAlocada = pfUnallocatedSurplus(m);
    aloc = foRow('Destinado', formatBRLCents(pfTotalAllocated(m)))
         + foRow('Não alocada', `<span class="${naoAlocada<0?'fs-neg':''}">${formatBRLCents(naoAlocada)}</span>`);
  }
  return `<div class="card fb-card fo-card"><h2>Mês atual <span class="art">${esc(pfMonthLabel(M))}</span></h2>
    ${foMoneyMetricHTML('Receita recebida', met.receita)}
    ${foMoneyMetricHTML('Despesa executada', met.despesa)}
    ${sobra}
    ${compr}
    ${aloc}
  </div>`;
}

// ---- CARD 2 · DÍVIDA & CRÉDITO ---------------------------------------------
function foDebtCreditCardHTML(M, met){
  const d = met.divida;
  let divida;
  if(d.status===PF_METRIC_COMPLETE && d.vazio)
    divida = foRow('Dívida observada', '<span class="fb-aux">Sem dívidas vigentes nesta competência — zero demonstrado</span>');
  else if(d.status===PF_METRIC_COMPLETE)
    divida = foRow('Dívida observada', `<b>${formatBRLCents(d.value)}</b> <span class="fb-aux">todas observadas</span>`);
  else if(d.status===PF_METRIC_PARTIAL)
    divida = foRow('Dívida observada', `${formatBRLCents(d.known)} observados <span class="fb-partial">PARCIAL ${d.cov.observadas}/${d.cov.relevantes}</span>`);
  else
    divida = foRow('Dívida observada', `<span class="fb-aux">${esc(d.motivo)}</span>`);

  // Crédito é ESTADO VIGENTE (pfCreditKPIs não recebe competência por
  // construção) — jamais apresentado como dado do mês M.
  const k = pfCreditKPIs();
  let credito;
  if(k.limitCoverage.total===0){
    credito = '<p class="fb-empty">Nenhuma linha de crédito cadastrada.</p>';
  } else {
    const parcial = cov => cov.completa ? '' : ` <span class="fb-partial">PARCIAL ${cov.conhecidas}/${cov.total}</span>`;
    credito = foRow('Limite conhecido', `${formatBRLCents(k.knownTotalLimit)}${parcial(k.limitCoverage)}`)
      + foRow('Utilizado conhecido', `${formatBRLCents(k.knownUsed)}${parcial(k.usedCoverage)}`)
      + foRow('Livre', k.totalFree!==null
          ? `<span class="${k.totalFree<0?'fs-neg':''}">${formatBRLCents(k.totalFree)}</span>`
          : '<span class="fb-aux">— cobertura incompleta</span>')
      + foRow('Utilização consolidada', k.utilizationConsolidated!==null
          ? `<b>${foPct(k.utilizationConsolidated)}</b>`
          : '<span class="fb-aux">N/A — cobertura incompleta ou limite zero</span>');
  }
  return `<div class="card fb-card fo-card"><h2>Dívida <span class="art">${esc(pfMonthLabel(M))} · observações da competência</span></h2>
    ${divida}
    <div class="fs-sec">CRÉDITO · POSIÇÃO ATUAL <span class="fb-aux">estado vigente — não é dado do mês</span></div>
    ${credito}
  </div>`;
}

// ---- CARD 3 · VS MÊS ANTERIOR ----------------------------------------------
// Consome exclusivamente o contrato público pfCompCompare/pfCompBaselines —
// nenhuma comparação própria, nenhum "último mês disponível", nenhum sniffing
// de motivo por texto. deltaPP chega como FRAÇÃO: a escala ×100 acontece uma
// única vez, aqui na apresentação.
function foPP(x){
  const v = (x*100).toLocaleString('pt-BR',{maximumFractionDigits:1});
  return (x>=0?'+':'')+v+' p.p.';
}
function foSignedMoney(c){ return (c>=0?'+':'−')+formatBRLCents(Math.abs(c)); }

const FO_COMP_LABELS = { receita:'Receita', despesa:'Despesa', sobra:'Sobra',
  divida:'Dívida', comprometimento:'Comprometimento' };

function foCompareCardHTML(M){
  const baseKey = pfCompBaselines(M).previousMonth;
  const comp = pfCompCompare(M, baseKey);
  const linhas = Object.entries(comp.metrics).map(([nome, m])=>{
    const rotulo = FO_COMP_LABELS[nome];
    if(!m.available)
      return foRow(rotulo, `<span class="fb-aux">comparação indisponível — ${esc(m.motivo)}</span>`);
    if(nome==='comprometimento')
      return foRow(rotulo, `${foPct(m.current)} <span class="fb-aux">vs ${foPct(m.baseline)}</span> · Δ ${foPP(m.deltaPP)}`);
    // percentual só existe onde o contrato o emite; sobra jamais tem a chave
    const pct = ('relativeChange' in m)
      ? (m.relativeChange!==null
          ? ` <span class="fb-aux">${(m.relativeChange>=0?'+':'')+foPct(m.relativeChange)}</span>`
          : (m.semAlteracao ? ' <span class="fb-aux">sem alteração</span>' : ' <span class="fb-aux">% N/A — base zero</span>'))
      : '';
    return foRow(rotulo, `${formatBRLCents(m.current)} <span class="fb-aux">vs ${formatBRLCents(m.baseline)}</span> · Δ ${foSignedMoney(m.delta)}${pct}`);
  }).join('');
  return `<div class="card fb-card fo-card"><h2>Vs mês anterior <span class="art">${esc(pfMonthLabel(baseKey))}</span></h2>
    ${linhas}
  </div>`;
}

// ---- CARD 4 · PENDÊNCIAS ----------------------------------------------------
// Fato puro de pfPendingBefore: status PENDENTE em meses materializados
// ESTRITAMENTE anteriores. Sem score, sem severidade, sem ato aqui (V1 é
// read-only — resolver pendência é do Orçamento Mensal).
function foPendingCardHTML(M){
  const pend = pfPendingBefore(M);
  const linhas = pend.length
    ? pend.map(p=>{
        const partes = [];
        if(p.despesas>0) partes.push(`${p.despesas} despesa${p.despesas>1?'s':''} pendente${p.despesas>1?'s':''}`);
        if(p.notas>0) partes.push(`${p.notas} nota${p.notas>1?'s':''} pendente${p.notas>1?'s':''}`);
        return foRow(esc(pfMonthLabel(p.key)), `<span class="fb-partial">${partes.join(' · ')}</span>`);
      }).join('')
    : '<p class="fb-empty">Nenhuma pendência anterior.</p>';
  return `<div class="card fb-card fo-card"><h2>Pendências <span class="art">meses anteriores com itens em aberto</span></h2>
    ${linhas}
  </div>`;
}

// ---- render -----------------------------------------------------------------
function finpesOverviewRender(){
  const root = document.getElementById('finpesOverviewRoot');
  if(!root) return;
  if(!pfMoneyUnitSupported()){
    // Sentinela de LEITURA — recusa integral (padrão PF-04): numa superfície
    // que é 100% consolidados monetários, interpretar QUALQUER montante sob
    // unidade desconhecida seria afirmar semântica que o estado não autoriza.
    // Zero "R$" na raiz; o banner do módulo (#finpesUnitNotice) já avisa.
    root.innerHTML = `<div class="fb-header"><span class="fo-title">Visão Geral</span></div>
      <div class="card fb-card"><h2>Visão Geral <span class="art">consolidado derivado — nunca segunda fonte de verdade</span></h2>
        <p class="risk-note">Unidade monetária do agregado não reconhecida — consolidados financeiros indisponíveis. Nenhum dado foi alterado.</p>
      </div>`;
    return;
  }
  const M = pfCurrentMonthKey();
  const met = pfCompMetrics(M);
  let html = `<div class="fb-header"><span class="fo-title">Visão Geral</span>
    <span class="fb-aux">consolidado derivado — nunca segunda fonte de verdade</span></div>`;
  html += `<div class="fo-grid">`;
  html += foMonthCardHTML(M, met);
  html += foDebtCreditCardHTML(M, met);
  html += foCompareCardHTML(M);
  html += foPendingCardHTML(M);
  html += `</div>`;
  root.innerHTML = html;
}

// Superfície pública consumida pelo mapa de renderers do módulo
// (17-finpes-views.js, FINPES_VIEW_RENDERERS). Só render — V1 é read-only.
window.JPWFinOverview = { render: finpesOverviewRender };

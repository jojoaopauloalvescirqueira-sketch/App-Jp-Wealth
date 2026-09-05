// ============ DASHBOARD · VISÃO EXECUTIVA MACRO (DASH-MACRO-01 · N1) ============
// Panorama transversal dos quatro módulos globais — Forex, Finanças Pessoais,
// Research e Alladin. READ → CONSUME CANONICAL → PRESENT.
//
// FRONTEIRA: este arquivo não contém uma única fórmula financeira. Cada card
// consome a superfície pública do seu domínio e apresenta. Nenhum cálculo é
// reproduzido aqui, nenhum estado é escrito, nenhum mês é materializado.
//
// POR QUE FORA DE #gdDashMain: o motor de layout (13-dashboard-layout.js) governa
// exclusivamente `:scope > [data-layout-card]` dentro de #gdDashMain. Esta seção
// vive FORA daquele container e não carrega [data-layout-card] — é estruturalmente
// invisível ao motor. Assim a preferência de layout salva do operador permanece
// válida, nenhum id persistido muda e nenhuma migração é necessária.
//
// POR QUE AUTO-DISPARO: o hook natural seria o fim de render() em
// 20-ui/03-main-render.js, mas aquele arquivo está fora do escopo autorizado
// desta mudança. O idioma usado aqui é o mesmo do Alladin (24-alladin-views.js):
// MutationObserver na própria section + primeira pintura no load.
//
// SEMÂNTICA INVARIANTE — o que este arquivo jamais faz:
//   PARTIAL      nunca vira total conhecido
//   UNAVAILABLE  nunca vira R$ 0
//   BLOCKING     nunca vira "0 posições"
//   cache nulo   nunca vira "0 eventos"
// Um domínio que recusa responder é exibido como indisponível, com o motivo.

// Faixa de fatos: os números que respondem "como está esta área?" antes do
// detalhe. Cada fato aceita um subtítulo e, quando existe TETO CANÔNICO para
// comparar, uma barra de proporção. Sem teto, nada de barra — proporção sem
// denominador seria número inventado.
function dmFact(k, v, sub, barPct, tom, neg){
  let bar = '';
  if(typeof barPct === 'number' && isFinite(barPct)){
    const w = Math.max(0, Math.min(100, barPct * 100));
    bar = '<span class="dm-bar' + (tom ? ' ' + tom : '') + '"><i style="width:' + w.toFixed(1) + '%"></i></span>';
  }
  return '<div class="dm-fact' + (neg ? ' neg' : '') + '">'
    + '<span class="k">' + esc(k) + '</span>'
    + '<span class="v">' + v + '</span>'
    + (sub ? '<span class="s">' + esc(sub) + '</span>' : '')
    + bar + '</div>';
}
function dmFacts(html){ return '<div class="dm-facts">' + html + '</div>'; }
function dmNote(texto){ return '<p class="dm-note">' + esc(texto) + '</p>'; }

function dmRow(nome, valorHTML){
  return '<div class="dm-row"><span class="dm-k">'+esc(nome)+'</span><span class="dm-v">'+valorHTML+'</span></div>';
}
function dmAux(texto){ return '<span class="dm-aux">'+esc(texto)+'</span>'; }
function dmCard(id, titulo, corpoHTML, rota, ctaLabel, tom){
  return '<article class="dm-card'+(tom?' dm-'+tom:'')+'" data-dm-card="'+esc(id)+'">'
    + '<h3 class="dm-title">'+esc(titulo)+'</h3>'
    + '<div class="dm-body">'+corpoHTML+'</div>'
    + '<button type="button" class="dm-cta" data-dm-route="'+esc(rota)+'">'+esc(ctaLabel)+' <span aria-hidden="true">→</span></button>'
    + '</article>';
}
// Falha de leitura de um domínio não pode derrubar os outros três nem ser
// confundida com ausência de dado: é estado próprio, rotulado.
function dmErro(motivo){
  return '<p class="dm-blocked">Resumo indisponível — falha ao ler o domínio.'
    + (motivo ? ' '+esc(motivo) : '') + '</p>';
}

// ---- FOREX ------------------------------------------------------------------
// compute() UMA vez por render; o resultado `c` é repassado a
// getOperationalClearance(c) — o mesmo padrão de renderOperationalClearance(c).
// Nenhum rótulo de "Equity": ADR-0001 está pendente e esta mudança não decide norma.
function dmForexHTML(c){
  const cl = getOperationalClearance(c);
  const TOM = {clear:'ok', caution:'warn', pending:'warn', reduce:'bad', blocked:'bad'};
  const tom = TOM[cl.status] || null;
  const barTom = tom === 'ok' ? '' : tom;
  // Razões só existem quando o teto é positivo. Denominador zero não vira barra.
  const ddPct = c.mddScaled > 0 ? c.dd / c.mddScaled : null;
  const riscoPct = c.tetoRisco > 0 ? c.riscoTotal / c.tetoRisco : null;
  const alavPct = c.tetoAlav > 0 ? c.alavCar / c.tetoAlav : null;
  let corpo = dmRow('Veredito', '<b class="dm-status dm-status-' + esc(cl.status) + '">' + esc(cl.title) + '</b>');
  corpo += dmFacts(
      dmFact('Fase vigente', esc(c.fase && c.fase.nome ? c.fase.nome : '—'))
    + dmFact('Drawdown', fmtPct(c.dd), 'teto ' + fmtPct(c.mddScaled), ddPct, barTom)
    + dmFact('Risco aberto', fmtMoney(c.riscoTotal), 'teto ' + fmtMoney(c.tetoRisco), riscoPct, barTom)
    // Alavancagem carregada vs teto da fase: grandeza canônica de compute(),
    // inequívoca. Nenhum rótulo de Equity — ADR-0001 segue pendente.
    + dmFact('Alavancagem', fmtX(c.alavCar), 'teto ' + fmtX(c.tetoAlav), alavPct, barTom)
  );
  // O primeiro motivo do veredito já vem quantificado e com remédio pelo
  // domínio — exibi-lo é projetar, não interpretar.
  if(cl.reasons && cl.reasons.length){
    corpo += dmNote(cl.reasons[0] + (cl.reasons.length > 1 ? '  (+' + (cl.reasons.length - 1) + ')' : ''));
  }
  return {html: corpo, tom};
}

// ---- FINANÇAS PESSOAIS ------------------------------------------------------
// Fronteira canônica única: pfCompMetrics(M). Ela já gateia mês virtual,
// parcialidade e receita zero — este card apenas projeta os três status.
function dmMoneyMetric(nome, m){
  if(!m) return dmRow(nome, dmAux('—'));
  if(m.status === PF_METRIC_COMPLETE) return dmRow(nome, '<b>'+formatBRLCents(m.value)+'</b>');
  if(m.status === PF_METRIC_PARTIAL){
    // O known do helper, com a moldura de cobertura. Jamais apresentado como total.
    const cov = m.cov && m.cov.conhecidas!==undefined
      ? ' <span class="dm-partial">PARCIAL '+esc(m.cov.conhecidas)+'/'+esc(m.cov.total)+'</span>' : '';
    return dmRow(nome, (m.known!==undefined ? formatBRLCents(m.known)+' conhecidos' : dmAux('cobertura incompleta'))+cov);
  }
  return dmRow(nome, dmAux(m.motivo || 'indisponível'));
}
function dmFinpesHTML(){
  // Guarda de LEITURA antes de qualquer "R$": sob unidade desconhecida o painel
  // recusa montantes em vez de presumir moeda padrão.
  if(typeof pfMoneyUnitSupported === 'function' && !pfMoneyUnitSupported()){
    return {html:'<p class="dm-blocked">Unidade monetária não reconhecida — consolidados indisponíveis. Nenhum dado foi alterado.</p>', tom:'warn'};
  }
  const M = pfCurrentMonthKey();
  const met = pfCompMetrics(M);          // 1 chamada — traz receita, despesa, sobra, DÍVIDA e COMPROMETIMENTO
  if(!met) return {html: dmErro('competência inválida'), tom:'warn'};
  let corpo = '<div class="dm-sub">' + esc(pfMonthLabel(M)) + '</div>';
  if(!met.materializado){
    // Completude vácua é armadilha conhecida: mês virtual declara-se não
    // registrado em vez de exibir sobra R$ 0 fabricada.
    corpo += '<p class="dm-empty">Mês ainda não registrado — nenhum realizado nesta competência.</p>';
  } else {
    corpo += dmFacts(
        dmFactMoney('Receita', met.receita)
      + dmFactMoney('Despesa', met.despesa)
      + dmFactMoney('Sobra', met.sobra, true)
      // Dívida e comprometimento vêm DE GRAÇA na mesma pfCompMetrics — zero
      // custo adicional, e são exatamente o que faltava para o painel
      // responder "como estão minhas finanças".
      + dmFactMoney('Dívida', met.divida)
    );
    corpo += dmPctMetric('Comprometimento', met.comprometimento);
  }
  // Crédito é POSIÇÃO VIGENTE, não dado da competência — rotulado como tal.
  const k = pfCreditKPIs();              // 1 chamada
  if(k && k.limitCoverage && k.limitCoverage.total > 0){
    corpo += dmRow('Utilização de crédito', k.utilizationConsolidated !== null
      ? '<b>' + foPctDm(k.utilizationConsolidated) + '</b> ' + dmAux('posição vigente')
      : dmAux('N/A — cobertura incompleta'));
  }
  // Pendências independem de unidade monetária — é contagem, não montante.
  const pend = (typeof pfPendingBefore === 'function') ? pfPendingBefore(M) : [];
  corpo += dmRow('Pendências anteriores', pend.length
    ? '<span class="dm-partial">' + pend.length + ' mês(es) em aberto</span>'
    : dmAux('nenhuma'));
  return {html: corpo, tom: pend.length ? 'warn' : null};
}

// Fato monetário no contrato COMPLETE/PARTIAL/UNAVAILABLE. PARTIAL mostra o
// known DO HELPER com a moldura de cobertura — nunca recomputa subtotal, nunca
// o apresenta como total. UNAVAILABLE mostra o motivo, jamais R$ 0.
function dmFactMoney(nome, m, marcaNegativo){
  if(!m) return dmFact(nome, '<span class="dm-aux">—</span>');
  if(m.status === PF_METRIC_COMPLETE)
    return dmFact(nome, formatBRLCents(m.value), null, null, null, !!marcaNegativo && m.value < 0);
  if(m.status === PF_METRIC_PARTIAL){
    const cov = m.cov && m.cov.conhecidas !== undefined
      ? m.cov.conhecidas + '/' + m.cov.total + ' conhecidas' : 'cobertura incompleta';
    return dmFact(nome, m.known !== undefined ? formatBRLCents(m.known) : '—', 'PARCIAL · ' + cov);
  }
  return dmFact(nome, '<span class="dm-aux">indisponível</span>', m.motivo || null);
}
function foPctDm(x){ return (x * 100).toLocaleString('pt-BR', {maximumFractionDigits:1}) + '%'; }
function dmPctMetric(nome, m){
  if(!m) return '';
  if(m.status === PF_METRIC_COMPLETE) return dmRow(nome, '<b>' + foPctDm(m.value) + '</b>');
  if(m.status === PF_METRIC_UNAVAILABLE) return dmRow(nome, dmAux(m.motivo || 'indisponível'));
  return dmRow(nome, dmAux('N/A — cobertura incompleta'));
}

// ---- RESEARCH ---------------------------------------------------------------
// Resumo informacional: não se força métrica financeira onde ela não existe.
function dmResearchHTML(){
  const nc = (S.nocoda && S.nocoda.studies && typeof S.nocoda.studies === 'object') ? Object.keys(S.nocoda.studies) : [];
  const pv = (S.pivotStudies && Array.isArray(S.pivotStudies.studies)) ? S.pivotStudies.studies : [];
  // Cobertura: quantos instrumentos operáveis já têm estudo NoCoda vigente.
  // instrumentCatalog() é a fonte canônica dos seletores das duas telas de
  // estudo — nenhuma delas tem catálogo próprio.
  let cobertura = null;
  if(typeof instrumentCatalog === 'function'){
    const cat = instrumentCatalog();
    if(Array.isArray(cat) && cat.length) cobertura = {com: cat.filter(i => nc.indexOf(i.id) >= 0).length, total: cat.length};
  }
  let corpo = dmFacts(
      dmFact('Estudos NoCoda', nc.length ? String(nc.length) : '<span class="dm-aux">nenhum</span>',
             cobertura ? cobertura.com + ' de ' + cobertura.total + ' instrumentos' : null,
             cobertura && cobertura.total ? cobertura.com / cobertura.total : null)
    + dmFact('Estudos dos Pivots', pv.length ? String(pv.length) : '<span class="dm-aux">nenhum</span>',
             pv.length ? 'amostras registradas' : null)
  );
  // Cache nulo = "sem cache válido", NUNCA "zero eventos": zero não pode ser
  // afirmado sem prova. O calendário permanece de Research por rota canônica
  // (NAV_COMPATIBILITY_TARGETS.ecal -> research-forex); esta revisão apenas o
  // CONSOME, sem redefinir a ownership do widget.
  const cal = (typeof ecalEvents === 'function') ? ecalEvents() : null;
  if(!cal){
    corpo += dmRow('Calendário de hoje', dmAux('dados ainda não carregados'));
  } else {
    const hoje = cal.events.filter(e => typeof ffNewsIsToday === 'function' && ffNewsIsToday(e.when));
    corpo += dmRow('Calendário de hoje', hoje.length
      ? '<b>' + hoje.length + '</b> ' + dmAux('evento(s) de alto impacto')
      : dmAux('nenhum evento de alto impacto'));
    const prox = cal.events.find(e => e.when && e.when.getTime() >= Date.now());
    if(prox) corpo += dmRow('Próximo evento', esc(String(prox.title || '—')).slice(0, 48) + ' ' + dmAux(String(prox.country || '')));
    if(typeof ffNewsCacheStale === 'function' && ffNewsCacheStale())
      corpo += dmRow('Cache', dmAux('desatualizado — atualize no módulo'));
  }
  return {html: corpo, tom: null};
}

// ---- ALLADIN ----------------------------------------------------------------
// Fail-closed é invariante. compat() primeiro: sob schema futuro nenhum número
// econômico pode ser afirmado, e posicoes() sequer é chamada (evita a varredura
// de integridade estrutural). Teto: 1 chamada de posicoes() por render.
function dmAlladinHTML(){
  const compat = JPWAlladin.compat();
  if(compat.readOnly){
    return {html:'<p class="dm-blocked">Base em schema mais novo que este build ('
      + esc(String(compat.storedSchemaVersion)) + ' &gt; ' + esc(String(compat.supportedSchemaVersion))
      + ') — dados econômicos indisponíveis.</p>', tom:'bad'};
  }
  const pos = JPWAlladin.leitura.posicoes();   // 1 chamada — 1 varredura de integridade
  if(!pos.available){
    // positions:[] sob available:false é IDÊNTICO a uma coleção legitimamente
    // vazia — por isso available vem antes de qualquer contagem.
    const issues = (pos.issues || []).slice(0, 3).map(i => esc(i)).join(' · ');
    return {html:'<p class="dm-blocked">Posições indisponíveis — integridade do agregado bloqueada.'
      + (issues ? '<span class="dm-issues">' + issues + '</span>' : '') + '</p>', tom:'bad'};
  }
  const n = pos.positions.length;
  // Contagens CADASTRAIS, atrás do mesmo portão de compat. São estrutura, não
  // afirmação econômica — e por isso rotuladas como cadastro.
  const L = JPWAlladin.leitura;
  const nInstr = L.instruments().length, nContas = L.accounts().length, nCaixas = L.cashAccounts().length;
  let corpo = dmFacts(
      dmFact('Posições abertas', n ? String(n) : '<span class="dm-aux">nenhuma</span>', n ? 'instrumento × conta' : 'nenhuma posição em aberto')
    + dmFact('Contas', String(nContas), nCaixas + ' caixa(s)')
  );
  corpo += dmRow('Instrumentos cadastrados', nInstr ? '<b>' + nInstr + '</b>' : dmAux('nenhum'));
  corpo += dmRow('Schema', dmAux('v' + String(compat.supportedSchemaVersion) + ' · íntegro'));
  return {html: corpo, tom: null};
}

// ---- render -----------------------------------------------------------------
// Cada card em try/catch próprio: falha de um domínio não derruba os demais.
function dmSafe(fn, fallbackTom){
  try { return fn(); }
  catch(e){ return {html: dmErro(e && e.message), tom: fallbackTom || 'warn'}; }
}
function dashMacroRender(){
  const root = document.getElementById('dashMacroGrid');
  if(!root) return;
  const forex = dmSafe(() => dmForexHTML(compute()));
  const finpes = dmSafe(dmFinpesHTML);
  const research = dmSafe(dmResearchHTML);
  const alladin = dmSafe(dmAlladinHTML);
  root.innerHTML =
      dmCard('forex', 'Forex', forex.html, 'forex-overview', 'Abrir Forex', forex.tom)
    + dmCard('personal-finance', 'Finanças Pessoais', finpes.html, 'personal-finance', 'Abrir Finanças Pessoais', finpes.tom)
    + dmCard('research', 'Research', research.html, 'research-forex', 'Abrir Research', research.tom)
    + dmCard('alladin', 'Alladin', alladin.html, 'alladin', 'Abrir Alladin', alladin.tom);
}

function initDashMacro(){
  const section = document.getElementById('dash');
  const root = document.getElementById('dashMacroGrid');
  if(!section || !root) return;
  // Delegação: os CTAs não são filhos de #nav, então o listener global de
  // [data-route] não os alcança. A navegação passa pela API pública — nenhuma
  // segunda implementação de roteamento.
  root.addEventListener('click', e => {
    const btn = e.target.closest('button[data-dm-route]');
    if(btn && window.JPWNavigation) window.JPWNavigation.navigate(btn.dataset.dmRoute);
  });
  // Repinta ao ENTRAR no Dashboard: um valor editado em outro módulo aparece
  // aqui sem recarregar a página. Render jamais escreve.
  new MutationObserver(() => {
    if(section.classList.contains('active')) dashMacroRender();
  }).observe(section, {attributes:true, attributeFilter:['class']});
  dashMacroRender();
}
initDashMacro();

window.JPWDashMacro = Object.freeze({render: dashMacroRender});

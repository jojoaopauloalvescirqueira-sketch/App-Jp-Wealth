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
// Atualização por entrada na tela, render geral, feed, storage e visibilidade.
// Hooks assíncronos são agrupados por frame; o relógio só age na tela visível.
// Preferências de widgets continuam exclusivamente no motor de layout.
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
const DM_AREAS = {
  forex: ['01', 'Risco e operação'],
  'personal-finance': ['02', 'Orçamento e crédito'],
  research: ['03', 'Estudos e agenda'],
  alladin: ['04', 'Contas e patrimônio']
};
function dmLink(label, route, surface, view){
  return '<button type="button" class="dm-link" data-dm-route="'+esc(route)+'"'
    +(surface?' data-dm-surface="'+esc(surface)+'" data-dm-view="'+esc(view)+'"':'')
    +'>'+esc(label)+'<span aria-hidden="true">↗</span></button>';
}
function dmLinks(html){ return '<nav class="dm-links" aria-label="Detalhes da área">'+html+'</nav>'; }
function dmSection(label, html){ return '<div class="dm-section"><h4>'+esc(label)+'</h4>'+html+'</div>'; }
function dmCard(id, titulo, corpoHTML, rota, ctaLabel, tom){
  const meta=DM_AREAS[id];
  return '<article class="dm-card'+(tom?' dm-'+tom:'')+'" data-dm-card="'+esc(id)+'" aria-labelledby="dm-title-'+id+'">'
    + '<header class="dm-card-head"><div><span class="dm-eyebrow">'+esc(meta[1])+'</span><h3 class="dm-title" id="dm-title-'+id+'">'+esc(titulo)+'</h3></div>'
    + '<button type="button" class="dm-cta" data-dm-route="'+esc(rota)+'">'+esc(ctaLabel)+' <span aria-hidden="true">→</span></button></header>'
    + '<div class="dm-body">'+corpoHTML+'</div>'
    + '</article>';
}
// Falha de leitura de um domínio não pode derrubar os outros três nem ser
// confundida com ausência de dado: é estado próprio, rotulado.
function dmErro(motivo){
  return '<p class="dm-blocked">Resumo indisponível — falha ao ler o domínio.'
    + (motivo ? ' '+esc(motivo) : '') + '</p>';
}

function dmDate(value){
  const text=String(value||'');
  const match=/^(\d{4})-(\d{2})-(\d{2})/.exec(text);
  return match ? match[3]+'/'+match[2]+'/'+match[1] : text || '—';
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
  const led = ledgerSorted();
  const last = led.length ? led[led.length-1] : null;
  corpo += dmSection('Apuração', last
    ? dmRow('Último fechamento · '+dmDate(last.data), '<b>'+fmtMoney2(last.saldo)+'</b>')
      + dmRow('Resultado do dia', '<b>'+fmtMoney2(last.resultado)+'</b>')
    : dmNote('Nenhum fechamento registrado neste período.'));
  corpo += dmSection('Planejamento', dmSafe(dmPlanningHTML).html);
  corpo += dmLinks(dmLink('Conta', 'forex-account')+dmLink('Preparação', 'forex-preparation')
    +dmLink('Apuração', 'forex-reconciliation')+dmLink('Planejamento', 'forex-planning'));
  return {html: corpo, tom};
}

// A ponte de estado do Planejamento normaliza S; esta projeção usa o motor
// puro e recusa formas incompletas, sem reparar nem gravar a base ao consultar.
function dmPlanningHTML(){
  const state=S.fxPlanning;
  if(!state || state.schemaVersion!==1) return {html:dmNote('Planejamento indisponível nesta versão da base.')};
  const raw=state.plan;
  if(!raw) return {html:dmNote('Planejamento ainda não aprovado.')};
  const model=window.JPWFx.model;
  if(!raw.baseline || !raw.current || !raw.actuals || !Array.isArray(raw.contributions)
    || model.fxValidateAssumptions(raw.baseline).length || model.fxValidateAssumptions(raw.current).length)
    return {html:dmNote('Planejamento indisponível — revise os dados no módulo.')};
  const plan=window.JPWFx.engine.fxOverview(raw);
  return {html:plan.lastClosedMonth
    ? dmRow('Resultado realizado', '<b>'+fmtMoney2(plan.realizedProfitUsd)+'</b>')
      +dmRow('Desvio vs baseline', '<b>'+fmtMoney2(plan.deviationUsd)+'</b>')
      +dmNote('Até '+pfMonthLabel(plan.lastClosedMonth)+' · valores em USD')
    : dmNote('Plano aprovado · aguardando o primeiro fechamento mensal.')};
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
  const baseKey=pfCompBaselines(M).previousMonth;
  const comp=pfCompCompare(M,baseKey).metrics.sobra;
  corpo += dmSection('Comparação mensal', comp.available
    ? dmRow('Sobra vs '+pfMonthLabel(baseKey), '<b>'+foSignedMoney(comp.delta)+'</b>')
    : dmNote('A comparação da sobra precisa de dois meses com valores completos.'));
  corpo += dmLinks(dmLink('Orçamento', 'personal-finance','finpes','mensal')
    +dmLink('Dívidas e crédito', 'personal-finance','finpes','dividas')
    +dmLink('Comparativo', 'personal-finance','finpes','comparativo')
    +dmLink('Cenários', 'personal-finance','finpes','cenarios'));
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
    if(prox) corpo += dmSection('Próximo evento', '<p class="dm-event">'+esc(String(prox.title || '—'))+'</p>'+dmRow(String(prox.country || ''), dmAux(prox.when.toLocaleDateString('pt-BR')+' · '+prox.when.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}))));
  }
  const cacheIssue = typeof ffNewsCacheIssue === 'function' ? ffNewsCacheIssue() : '';
  if(cacheIssue) corpo += dmRow('Cache', dmAux(cacheIssue));
  else if(cal && typeof ffNewsCacheStale === 'function' && ffNewsCacheStale())
    corpo += dmRow('Cache', dmAux('desatualizado — atualize no módulo'));
  corpo += dmSection('Outras pesquisas', '<div class="dm-research-areas">'
    +dmLink('Ações · B3','research-stocks-br')+dmLink('Stocks','research-stocks-global')
    +dmLink('REITs','research-reits')+dmLink('Others','research-others')
    +'</div>'+dmNote('Áreas em preparação · sem conteúdo publicado.'));
  corpo += dmLinks(dmLink('Calendário','research-forex','research','calendar')
    +dmLink('NoCoda','research-forex','research','nocoda')
    +dmLink('Pivots','research-forex','research','pivots'));
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
  corpo += dmRow('Bens cadastrados', '<b>'+L.assets().length+'</b>');
  const labels=alladinCatalogoLabels();
  const cash=L.cashAccounts();

  // Conta por conta: moedas nunca são somadas e recusa nunca vira saldo zero.
  const balances=cash.slice(0,3).map(account=>{
    const balance=L.saldoDeCaixa(account.cashAccountId);

    return dmRow(alladinCaixaLabel(labels,account.cashAccountId), balance.available
      ? '<b>'+esc(JPWAlladin.money.format({amount:balance.amount,currency:balance.currency}))+'</b>'
      : '<span class="dm-partial">Saldo indisponível</span>');
  }).join('');
  corpo += dmSection('Saldos por conta', balances || dmNote('Cadastre uma conta de caixa para acompanhar os saldos.'));
  if(cash.length>3) corpo+=dmNote('Exibindo 3 de '+cash.length+' contas. Todos os saldos estão no módulo.');
  const ledger=L.ledger();
  const txs=ledger.transactions;
  const last=txs.length?txs[txs.length-1]:null;
  // Mesma ordem econômica do leitor; correção por estorno permanece visível.
  corpo += dmSection('Último lançamento', !ledger.available
    ? '<span class="dm-partial">Lançamentos indisponíveis</span>'
    : last
    ? dmRow(last.eventType==='REVERSAL'?'Estorno':alladinEventoLabel(last.eventType), '<b>'+esc(JPWAlladin.money.format({amount:last.amount,currency:last.currency}))+'</b>')
      +dmRow(dmDate(last.effectiveAt),dmAux(ALLADIN_TX_STATUS_LABEL[last.status]||last.status||'—'))
    : dmNote('Nenhum lançamento registrado.'));
  corpo += dmLinks(dmLink('Saldos','alladin','alladin','balances')+dmLink('Lançamentos','alladin','alladin','ledger')
    +dmLink('Posições','alladin','alladin','positions')+dmLink('Cadastros','alladin','alladin','instruments'));
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
  const html =
      dmCard('forex', 'Forex', forex.html, 'forex-overview', 'Abrir Forex', forex.tom)
    + dmCard('personal-finance', 'Finanças Pessoais', finpes.html, 'personal-finance', 'Abrir Finanças Pessoais', finpes.tom)
    + dmCard('research', 'Research', research.html, 'research-forex', 'Abrir Research', research.tom)
    + dmCard('alladin', 'Alladin', alladin.html, 'alladin', 'Abrir Alladin', alladin.tom);
  if(root.innerHTML!==html){
    const active=root.contains(document.activeElement)?document.activeElement:null;
    const key=active?{route:active.dataset.dmRoute,surface:active.dataset.dmSurface,view:active.dataset.dmView}:null;
    root.innerHTML=html;
    if(key){
      const target=[...root.querySelectorAll('[data-dm-route]')].find(b=>b.dataset.dmRoute===key.route&&b.dataset.dmSurface===key.surface&&b.dataset.dmView===key.view);
      if(target) target.focus({preventScroll:true});
    }
  }
  const date=document.getElementById('dmToday');
  if(date) date.textContent=new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'numeric',month:'long'});

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
    if(btn && window.JPWNavigation){
      const surfaceId=btn.dataset.dmSurface, view=btn.dataset.dmView;
      const local=surfaceId==='finpes'||surfaceId==='research';
      const result=local
        ? window.JPWNavigation.navigateLocal(surfaceId,view)
        : window.JPWNavigation.navigate(btn.dataset.dmRoute);
      if(result===false) return;
      // Alladin mantém vistas efêmeras próprias, fora de NAV_LOCAL_SURFACES.
      if(surfaceId==='alladin' && window.JPWAlladinUI) window.JPWAlladinUI.selectView(view);
      if(btn.dataset.dmView){
        const screen=document.querySelector('#appMain > .screen.active');
        const heading=screen&&[...screen.querySelectorAll('h2,h3')].find(h=>h.getClientRects().length);
        if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
      }else{
        window.JPWNavigation.focusCurrentScreen();
      }
    }
  });
  // Repinta ao ENTRAR no Dashboard: um valor editado em outro módulo aparece
  // aqui sem recarregar a página. Render jamais escreve.
  new MutationObserver(() => {
    if(section.classList.contains('active')) dashMacroRender();
  }).observe(section, {attributes:true, attributeFilter:['class']});
  // A edição de widgets revela a seção, preservando o motor e seu estado.
  new MutationObserver(()=>{
    if(document.documentElement.dataset.layoutEditing==='true'){
      const tools=document.getElementById('dmTools');if(tools) tools.open=true;
    }
  }).observe(document.documentElement,{attributes:true,attributeFilter:['data-layout-editing']});
  dashMacroRender();
}
initDashMacro();

// Agrupa os hooks no próximo frame, sem escrita nem requisição de rede.
let dmRenderQueued=false;
function dashMacroSchedule(){
  if(dmRenderQueued || document.hidden || !document.querySelector('#dash.active')) return;
  dmRenderQueued=true;
  requestAnimationFrame(()=>{dmRenderQueued=false;if(document.querySelector('#dash.active')) dashMacroRender();});
}
window.addEventListener('storage',dashMacroSchedule);
document.addEventListener('visibilitychange',dashMacroSchedule);
setInterval(dashMacroSchedule,60000);
window.JPWDashMacro = Object.freeze({render: dashMacroRender, schedule: dashMacroSchedule});

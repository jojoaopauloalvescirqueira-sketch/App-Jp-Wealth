// ============ FINANÇAS PESSOAIS · ORÇAMENTO MENSAL (PF-02) ============
// Renderizador do workspace #finpesMensal. Consome exclusivamente o núcleo do
// domínio (10-domain/12-personal-finance.js): todo dinheiro passa por
// parseBRLCents/formatBRLCents, toda mutação passa por pfMutate (write gate
// canônico) e todo derivado é recalculado aqui — nunca persistido.
//
// O mês exibido é estado de UI EFÊMERO (variável de módulo, padrão fxpView):
// não entra em S, localStorage, backup nem schema. Navegar é read-only por
// contrato — abrir um mês NÃO o materializa; só o primeiro ato de edição.

let fbMonth = null;          // 'YYYY-MM' exibido; null = resolver para o corrente
let fbPendingPromptShown = false; // flag de SESSÃO do modal de pendências (F) — nunca persiste

function fbCurrentKey(){
  if(!fbMonth || !pfMonthKeyValid(fbMonth)) fbMonth = pfCurrentMonthKey();
  return fbMonth;
}

function fbGoTo(key){
  fbMonth = key;
  finpesBudgetRender();
}

// ---- render raiz ------------------------------------------------------------
function finpesBudgetRender(){
  const root = document.getElementById('finpesBudgetRoot');
  if(!root) return;
  const key = fbCurrentKey();
  const materializado = pfIsMaterialized(key);
  const bloqueado = (typeof pfWriteBlockReason==='function') ? pfWriteBlockReason() : null;

  let html = fbHeaderHTML(key, materializado);
  html += fbPendingBannerHTML(key);
  html += '<div class="fb-grid">';
  html += '<div class="fb-col">';
  html += fbIncomesHTML(key, materializado, bloqueado);
  html += fbNotesHTML(key, materializado, bloqueado);
  html += '</div>';
  html += '<div class="fb-col fb-col-wide">';
  html += fbExpensesHTML(key, materializado, bloqueado);
  html += '</div>';
  html += '<div class="fb-col">';
  html += fbSummaryHTML(key, materializado, bloqueado);
  html += fbAllocationsHTML(key, materializado, bloqueado);
  html += '</div>';
  html += '</div>';
  root.innerHTML = html;
  fbBind(root, key, materializado, bloqueado);
}

// ---- cabeçalho: ← MÊS ANO → · Hoje -----------------------------------------
function fbHeaderHTML(key, materializado){
  const selo = materializado
    ? ''
    : '<span class="fb-virtual-badge" title="Mês virtual: projeção derivada das regras recorrentes vigentes. Nada foi registrado; o mês nasce no primeiro ato de edição.">◌ PROJEÇÃO — mês não registrado</span>';
  return `<div class="fb-header">
    <button type="button" class="reset-btn fb-nav" data-fb-nav="-1" title="Mês anterior">←</button>
    <span class="fb-month-label">${esc(pfMonthLabel(key))}</span>
    <button type="button" class="reset-btn fb-nav" data-fb-nav="1" title="Mês seguinte">→</button>
    <button type="button" class="reset-btn fb-today" data-fb-today title="Ir para o mês corrente">Hoje</button>
    ${selo}
  </div>`;
}

// Placeholders dos blocos B–F: substituídos bloco a bloco. Cada um declara o
// que AINDA não faz — nenhum número fictício.
// ---- RECEITAS (Bloco B) -----------------------------------------------------
// Linha materializada: inputs inline (commit no change, um campo = um ato).
// Linha fantasma (mês virtual): projeção da regra; editar materializa o mês.
// Dinheiro: exibido por formatBRLCents, editado como texto e parseado por
// parseBRLCents — vazio = null, inválido/negativo recusado com reversão.
// Sentinela de LEITURA (PF-CLOSE-02): unidade desconhecida NAO autoriza
// interpretar o inteiro guardado como BRL. A estrutura da tela permanece
// legivel — nomes, status, parcelas, coberturas, notas —, mas todo montante
// vira "—" e nenhum campo monetario expoe valor. Padrao do PF-05; a autoridade
// e a mesma ja usada pelo write gate (pfWriteBlockReason, via `bloqueado`).
function fbMoneyText(cents, bloqueado){
  return bloqueado ? '—' : formatBRLCents(cents);
}
function fbMoneyInput(valor, ds, bloqueado){
  if(bloqueado) return '<span class="fd-money" title="Unidade monetária não reconhecida">—</span>';
  const texto = (valor===null||valor===undefined) ? '' : (valor/100).toFixed(2).replace('.',',');
  return `<input type="text" class="fb-money" value="${esc(texto)}" ${ds} inputmode="decimal" placeholder="—">`;
}
function fbIncomesHTML(key, materializado, bloqueado){
  let linhas='';
  if(materializado){
    const m = S.personalFinance.months[key];
    linhas = (m.incomes||[]).map(i=>`<div class="fb-row" data-income="${esc(i.id)}">
      <span><input type="text" class="fb-text" value="${esc(i.name)}" ${bloqueado?'disabled':''} data-fi-campo="name" data-fi-id="${esc(i.id)}">${i.ruleId?'<span class="fb-rule-mark" title="Receita recorrente (regra vigente)">↻</span>':''}</span>
      <span>${fbMoneyInput(i.projectedAmount,`data-fi-campo="projectedAmount" data-fi-id="${esc(i.id)}"`, bloqueado)}</span>
      <span>${fbMoneyInput(i.receivedAmount,`data-fi-campo="receivedAmount" data-fi-id="${esc(i.id)}"`, bloqueado)}</span>
      <span class="fb-actions"><select class="fb-status-sel" ${bloqueado?'disabled':''} data-fi-status="${esc(i.id)}">
        ${['PROJETADA','RECEBIDA','CANCELADA'].map(st=>`<option value="${st}" ${st===i.status?'selected':''}>${st}</option>`).join('')}
      </select>
      <button type="button" class="row-del" ${bloqueado?'disabled':''} data-fi-cfg="${esc(i.id)}" title="Configurar recorrência">⚙</button>
      <button type="button" class="row-del" ${bloqueado?'disabled':''} data-fi-del="${esc(i.id)}" title="Excluir receita">✕</button></span>
    </div>`).join('');
  } else {
    linhas = pfVirtualIncomes(key).map(v=>`<div class="fb-row fb-ghost" title="Projeção da regra recorrente — editar registra o mês">
      <span>◌ ${esc(v.name)} <span class="fb-rule-mark">↻</span></span>
      <span>${fbMoneyInput(v.projectedAmount,`data-fg-campo="projectedAmount" data-fg-rule="${esc(v.ruleId)}"`, bloqueado)}</span>
      <span>${fbMoneyInput(null,`data-fg-campo="receivedAmount" data-fg-rule="${esc(v.ruleId)}"`, bloqueado)}</span>
      <span class="fb-status">PROJEÇÃO</span>
    </div>`).join('');
  }
  const m = materializado ? S.personalFinance.months[key] : null;
  const totProj = m ? pfProjectedIncome(m) : pfVirtualIncomes(key).reduce((a,v)=>a+(typeof v.projectedAmount==='number'?v.projectedAmount:0),0);
  const totRec  = m ? pfKnownReceivedIncome(m) : null;
  const cob     = m ? pfIncomeCoverage(m) : null;
  const cobTxt  = (cob && cob.total>0 && !cob.completa) ? ` <span class="fb-partial">PARCIAL · ${cob.conhecidas} de ${cob.total} informadas</span>` : '';
  return `<div class="card fb-card" id="fbIncomes">
    <h2>Receitas <span class="art">projetado ≠ recebido · ausência ≠ zero</span></h2>
    <div class="fb-row fb-head"><span>Descrição</span><span>Projetado</span><span>Recebido</span><span></span></div>
    ${linhas || '<p class="fb-empty">Nenhuma receita neste mês.</p>'}
    <div class="fb-totals"><span>Receita projetada: <b>${fbMoneyText(totProj, bloqueado)}</b></span>
      <span>Receita recebida: <b>${m ? fbMoneyText(totRec, bloqueado) : '—'}</b>${cobTxt}</span></div>
    <button type="button" class="reset-btn" data-fi-add ${bloqueado?'disabled title="Módulo em modo leitura"':''}>+ Adicionar receita</button>
  </div>`;
}
function fbExpensesHTML(key, materializado, bloqueado){
  let linhas='';
  if(materializado){
    const m = S.personalFinance.months[key];
    linhas = (m.expenses||[]).map(e=>{
      const parc = e.installments ? `${e.installments.paid}/${e.installments.total}` : '';
      return `<div class="fb-erow" data-expense="${esc(e.id)}">
      <span><input type="text" class="fb-text" value="${esc(e.name)}" ${bloqueado?'disabled':''} data-fe-campo="name" data-fe-id="${esc(e.id)}"></span>
      <span><input type="text" class="fb-money fb-parc" value="${esc(parc)}" ${bloqueado?'disabled':''} placeholder="—" title="Parcelas pagas/total, ex.: 16/24; vazio limpa" data-fe-parc="${esc(e.id)}"></span>
      <span>${fbMoneyInput(e.targetAmount,`data-fe-campo="targetAmount" data-fe-id="${esc(e.id)}"`, bloqueado)}</span>
      <span>${fbMoneyInput(e.expectedAmount,`data-fe-campo="expectedAmount" data-fe-id="${esc(e.id)}"`, bloqueado)}</span>
      <span>${fbMoneyInput(e.executedCash,`data-fe-campo="executedCash" data-fe-id="${esc(e.id)}"`, bloqueado)}</span>
      <span>${fbMoneyInput(e.executedCard,`data-fe-campo="executedCard" data-fe-id="${esc(e.id)}"`, bloqueado)}</span>
      <span class="fb-actions"><select class="fb-status-sel" ${bloqueado?'disabled':''} data-fe-status="${esc(e.id)}">
        ${['PENDENTE','PAGO','CANCELADO'].map(st=>`<option value="${st}" ${st===e.status?'selected':''}>${st}</option>`).join('')}
      </select>
      <button type="button" class="row-del" ${bloqueado?'disabled':''} data-fe-del="${esc(e.id)}" title="Excluir despesa">✕</button></span>
    </div>`;}).join('');
  }
  const m = materializado ? S.personalFinance.months[key] : null;
  const prev = m ? pfPlannedExpenses(m) : 0;
  const exec = m ? pfKnownExecutedExpenses(m) : null;
  const cob  = m ? pfExpenseCoverage(m) : null;
  const cobTxt = (cob && cob.total>0 && !cob.completa) ? ` <span class="fb-partial">PARCIAL · ${cob.conhecidas} de ${cob.total} com os dois canais</span>` : '';
  return `<div class="card fb-card" id="fbExpenses">
    <h2>Despesas <span class="art">Meta ≠ Previsto ≠ Executado (fora do cartão + cartão)</span></h2>
    <div class="fb-erow fb-head"><span>Despesa</span><span>Parc.</span><span>Meta</span><span>Previsto</span><span>Fora cartão</span><span>Cartão</span><span></span></div>
    ${linhas || '<p class="fb-empty">'+(materializado?'Nenhuma despesa neste mês.':'Mês não registrado — adicionar despesa registra o mês.')+'</p>'}
    <div class="fb-totals"><span>Despesa prevista: <b>${fbMoneyText(prev, bloqueado)}</b></span>
      <span>Despesa executada (conhecida): <b>${m ? fbMoneyText(exec, bloqueado) : '—'}</b>${cobTxt}</span></div>
    <button type="button" class="reset-btn" data-fe-add ${bloqueado?'disabled title="Módulo em modo leitura"':''}>+ Adicionar despesa</button>
  </div>`;
}
function fbSummaryHTML(key, materializado, bloqueado){
  const linha=(k,v,extra)=>`<div class="fb-sumrow"><span>${k}</span><b>${v}</b>${extra||''}</div>`;
  if(!materializado){
    const proj = pfVirtualIncomes(key).reduce((a,v)=>a+(typeof v.projectedAmount==='number'?v.projectedAmount:0),0);
    return `<div class="card fb-card" id="fbSummary">
      <h2>Resumo do Mês <span class="art">soma parcial nunca vira total</span></h2>
      ${linha('Receita projetada (regras)', fbMoneyText(proj, bloqueado))}
      ${linha('Sobra projetada', fbMoneyText(proj, bloqueado))}
      <p class="risk-note">Mês não registrado: os números acima são projeção das regras vigentes. Nada de realizado existe aqui.</p>
    </div>`;
  }
  const m = S.personalFinance.months[key];
  const r = pfMonthSummary(m);
  const cobTxt = c => (c.total>0 && !c.completa) ? `<span class="fb-partial">PARCIAL · ${c.conhecidas}/${c.total}</span>` : '';
  const sobraReal = (r.realizedSurplus!==null)
    ? linha('Sobra realizada', fbMoneyText(r.realizedSurplus, bloqueado))
    : linha('Sobra realizada', '—', '<span class="fb-partial">Dados incompletos</span>')
      + linha('Saldo conhecido até agora', fbMoneyText(r.knownBalance, bloqueado), '<span class="fb-aux">auxiliar — não é a sobra</span>');
  // razao derivada de grandezas monetarias de unidade desconhecida: recusada
  const ratio = bloqueado
    ? linha('Comprometimento (desp./rec.)', '—')
    : ((r.incomeExpenseRatio!==null)
        ? linha('Comprometimento (desp./rec.)', (r.incomeExpenseRatio*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%')
        : linha('Comprometimento (desp./rec.)', '—', '<span class="fb-partial">'+(r.completo?'receita zero — N/A':'parcial')+'</span>'));
  return `<div class="card fb-card" id="fbSummary">
    <h2>Resumo do Mês <span class="art">planejado ≠ realizado · soma parcial nunca vira total</span></h2>
    <div class="fb-sumsec">PLANEJADO</div>
    ${linha('Receita projetada', fbMoneyText(r.projectedIncome, bloqueado))}
    ${linha('Despesa prevista', fbMoneyText(r.plannedExpenses, bloqueado))}
    ${linha('Sobra projetada', fbMoneyText(r.projectedSurplus, bloqueado))}
    <div class="fb-sumsec">REALIZADO</div>
    ${linha('Receita recebida', fbMoneyText(r.knownReceivedIncome, bloqueado), cobTxt(r.incomeCoverage))}
    ${linha('Despesa executada', fbMoneyText(r.knownExecutedExpenses, bloqueado), cobTxt(r.expenseCoverage))}
    ${sobraReal}
    ${ratio}
  </div>`;
}
function fbAllocationsHTML(key, materializado, bloqueado){
  const m = materializado ? S.personalFinance.months[key] : null;
  const linhas = m ? (m.allocations||[]).map(a=>`<div class="fb-row fb-alloc" data-alloc="${esc(a.id)}">
      <span><input type="text" class="fb-text" value="${esc(a.label)}" ${bloqueado?'disabled':''} data-fa-campo="label" data-fa-id="${esc(a.id)}"></span>
      <span>${fbMoneyInput(a.amount,`data-fa-campo="amount" data-fa-id="${esc(a.id)}"`, bloqueado)}</span>
      <span></span>
      <span class="fb-actions"><button type="button" class="row-del" ${bloqueado?'disabled':''} data-fa-del="${esc(a.id)}" title="Excluir destinação">✕</button></span>
    </div>`).join('') : '';
  const total = m ? pfTotalAllocated(m) : 0;
  const naoAlocada = m ? pfUnallocatedSurplus(m) : null;
  const resumo = m ? pfMonthSummary(m) : null;
  // alerta e inferencia sobre grandezas monetarias: sob unidade desconhecida
  // nao se afirma excedente
  const excede = !bloqueado && !!(resumo && resumo.realizedSurplus!==null && total > resumo.realizedSurplus);
  return `<div class="card fb-card" id="fbAllocations">
    <h2>Destino do Excedente <span class="art">a sobra é insumo, não resultado</span></h2>
    ${linhas || '<p class="fb-empty">'+(materializado?'Nenhuma destinação neste mês.':'Mês não registrado — destinar registra o mês.')+'</p>'}
    <div class="fb-totals"><span>Total destinado: <b>${fbMoneyText(total, bloqueado)}</b></span>
      <span>Sobra não alocada: <b>${naoAlocada!==null?fbMoneyText(naoAlocada, bloqueado):'—'}</b>${naoAlocada===null && m ? ' <span class="fb-partial">realizado incompleto — sem saldo restante</span>':''}</span></div>
    ${excede ? '<div class="status-banner sb-warn" id="fbAllocExceeds" style="margin-top:8px"><span class="ico">⚠️</span><span>As destinações excedem a sobra realizada deste mês. Pode ser legítimo (saldo anterior) — confira.</span></div>' : ''}
    <button type="button" class="reset-btn" data-fa-add ${bloqueado?'disabled title="Módulo em modo leitura"':''}>+ Adicionar destinação</button>
  </div>`;
}
function fbNotesHTML(key, materializado, bloqueado){
  const m = materializado ? S.personalFinance.months[key] : null;
  const linhas = m ? (m.notes||[]).map(n=>`<div class="fb-noterow ${n.status==='RESOLVIDO'?'fb-note-done':''}" data-note="${esc(n.id)}">
      <button type="button" class="fb-note-toggle" ${bloqueado?'disabled':''} data-fn-toggle="${esc(n.id)}" title="Alternar status">${n.status==='PENDENTE'?'⚠':'✓'}</button>
      <span class="fb-note-text">${esc(n.text)}</span>
      <span class="fb-status">${esc(n.status)}</span>
      <button type="button" class="row-del" ${bloqueado?'disabled':''} data-fn-del="${esc(n.id)}" title="Excluir nota">✕</button>
    </div>`).join('') : '';
  return `<div class="card fb-card" id="fbNotes">
    <h2>Informações Importantes <span class="art">texto + status, nada mais</span></h2>
    ${linhas || '<p class="fb-empty">'+(materializado?'Nenhuma informação neste mês.':'Mês não registrado.')+'</p>'}
    <button type="button" class="reset-btn" data-fn-add ${bloqueado?'disabled title="Módulo em modo leitura"':''}>+ Adicionar informação</button>
  </div>`;
}
function fbPendingBannerHTML(key){
  // Indicação persistente e não intrusiva: existe enquanto houver pendência
  // (status PENDENTE em despesa/nota de mês materializado anterior ao
  // corrente). Nada inferido de null, texto ou cobertura.
  const pend = pfPendingBefore(pfCurrentMonthKey());
  if(!pend.length) return '';
  const total = pend.reduce((a,p)=>a+p.despesas+p.notas,0);
  return `<div class="status-banner sb-warn" id="fbPendingBanner" style="margin-bottom:12px">
    <span class="ico">⚠️</span><span>Existem ${total} pendência(s) em meses anteriores.</span>
    <button type="button" class="reset-btn" data-fb-review="${esc(pend[0].key)}" style="margin-left:auto">Revisar ${esc(pfMonthLabel(pend[0].key))}</button>
  </div>`;
}

// Modal de pendências: UMA vez por sessão de app (flag de módulo, jamais
// persistida), disparado apenas na navegação DELIBERADA ao mês corrente
// (entrada no workspace ou botão Hoje) — nunca por rerender.
function fbMaybePendingPrompt(){
  if(fbPendingPromptShown) return;
  if(fbCurrentKey() !== pfCurrentMonthKey()) return;
  const pend = pfPendingBefore(pfCurrentMonthKey());
  if(!pend.length) return;
  fbPendingPromptShown = true;
  const box=$('modalBox'); $('modalOverlay').classList.add('show');
  const blocos = pend.map(p=>`<div class="fb-pend-month"><b>${esc(pfMonthLabel(p.key))}</b>
    ${p.despesas?`<div>• ${p.despesas} despesa(s) pendente(s)</div>`:''}
    ${p.notas?`<div>• ${p.notas} informação(ões) importante(s) pendente(s)</div>`:''}
  </div>`).join('');
  box.innerHTML = `
    <h3>Existem pendências de meses anteriores.</h3>
    ${blocos}
    <div class="modal-actions">
      <button class="modal-btn" id="fbPendReview">Revisar mês anterior</button>
      <button class="modal-btn confirm" id="fbPendContinue">Continuar para o mês atual</button>
    </div>`;
  $('fbPendContinue').addEventListener('click', ()=>{ closeModal(); });
  $('fbPendReview').addEventListener('click', ()=>{
    closeModal();
    fbGoTo(pend[0].key);   // abre o mês pendente mais antigo — EDITÁVEL
  });
}

// ---- binds ------------------------------------------------------------------
function fbAtoUI(r){
  // resposta padrão a um ato: recusa vira alert (bloqueio de regra, não erro
  // de campo de modal) + re-render para o DOM voltar ao estado real.
  if(r && r.ok===false && r.erro) alert('⛔ ' + r.erro);
  finpesBudgetRender();
}
function fbParseMoneyOr(inp){
  // vazio = null (não informado); inválido/negativo = undefined (recusado)
  const c = parseBRLCents(inp.value);
  if(c===null) return null;
  if(Number.isNaN(c)) { alert('⛔ Valor inválido — ponto ou vírgula decimal, sem separador ambíguo; em branco não é zero.'); return undefined; }
  if(c<0) { alert('⛔ Valor negativo não é aceito: a direção já é do campo.'); return undefined; }
  return c;
}
function fbBind(root, key){
  root.querySelectorAll('[data-fb-nav]').forEach(b=>b.addEventListener('click',()=>{
    fbGoTo(pfMonthAdd(fbCurrentKey(), +b.dataset.fbNav));
  }));
  const hoje = root.querySelector('[data-fb-today]');
  if(hoje) hoje.addEventListener('click',()=>{ fbGoTo(pfCurrentMonthKey()); fbMaybePendingPrompt(); });

  // ---- receitas (B) ----
  const add = root.querySelector('[data-fi-add]');
  if(add) add.addEventListener('click',()=>{
    const nome = prompt('Descrição da receita:');
    if(nome===null) return;                       // cancelar = zero mutação
    fbAtoUI(pfActAddIncome(key, { name: nome, projectedAmount: null }));
  });
  root.querySelectorAll('[data-fi-campo]').forEach(inp=>{
    inp.addEventListener('focus',()=>{ inp.dataset.prevval = inp.value; });
    inp.addEventListener('change',()=>{
      const campo = inp.dataset.fiCampo, id = inp.dataset.fiId;
      let valor;
      if(campo==='name') valor = inp.value;
      else { valor = fbParseMoneyOr(inp); if(valor===undefined){ inp.value = inp.dataset.prevval ?? ''; return; } }
      const r = pfActUpdateIncomeField(key, id, campo, valor);
      if(r.ok===false){ inp.value = inp.dataset.prevval ?? ''; }
      fbAtoUI(r);
    });
  });
  root.querySelectorAll('[data-fg-campo]').forEach(inp=>{
    inp.addEventListener('focus',()=>{ inp.dataset.prevval = inp.value; });
    inp.addEventListener('change',()=>{
      const campo = inp.dataset.fgCampo, ruleId = inp.dataset.fgRule;
      const valor = fbParseMoneyOr(inp);
      if(valor===undefined){ inp.value = inp.dataset.prevval ?? ''; return; }
      fbAtoUI(pfActEditGhost(key, ruleId, campo, valor));   // materializa + aplica
    });
  });
  root.querySelectorAll('[data-fi-status]').forEach(sel=>{
    sel.addEventListener('focus',()=>{ sel.dataset.prevval = sel.value; });
    sel.addEventListener('change',()=>{
      const r = pfActSetIncomeStatus(key, sel.dataset.fiStatus, sel.value);
      if(r.ok===false){ sel.value = sel.dataset.prevval || 'PROJETADA'; }
      fbAtoUI(r);
    });
  });
  root.querySelectorAll('[data-fi-del]').forEach(btn=>btn.addEventListener('click',()=>{
    const id = btn.dataset.fiDel;
    const m = S.personalFinance.months[key];
    const rec = m && m.incomes.find(i=>i.id===id);
    const temDado = rec && (rec.projectedAmount!==null || rec.receivedAmount!==null || (rec.name||'').trim());
    if(temDado && !confirm('Excluir a receita "'+(rec.name||'')+'"?')) return;
    fbAtoUI(pfActDeleteIncome(key, id));
  }));
  root.querySelectorAll('[data-fi-cfg]').forEach(btn=>btn.addEventListener('click',()=>{
    fbOpenRecurrenceModal(key, btn.dataset.fiCfg);
  }));

  // ---- despesas (C) ----
  const addE = root.querySelector('[data-fe-add]');
  if(addE) addE.addEventListener('click',()=>{
    const nome = prompt('Nome da despesa:');
    if(nome===null) return;                       // cancelar = zero mutação
    fbAtoUI(pfActAddExpense(key, { name: nome }));
  });
  root.querySelectorAll('[data-fe-campo]').forEach(inp=>{
    inp.addEventListener('focus',()=>{ inp.dataset.prevval = inp.value; });
    inp.addEventListener('change',()=>{
      const campo = inp.dataset.feCampo, id = inp.dataset.feId;
      let valor;
      if(campo==='name') valor = inp.value;
      else { valor = fbParseMoneyOr(inp); if(valor===undefined){ inp.value = inp.dataset.prevval ?? ''; return; } }
      const r = pfActUpdateExpenseField(key, id, campo, valor);
      if(r.ok===false){ inp.value = inp.dataset.prevval ?? ''; }
      fbAtoUI(r);
    });
  });
  root.querySelectorAll('[data-fe-parc]').forEach(inp=>{
    inp.addEventListener('focus',()=>{ inp.dataset.prevval = inp.value; });
    inp.addEventListener('change',()=>{
      const id = inp.dataset.feParc;
      const t = inp.value.trim();
      let parc;
      if(!t) parc = null;
      else {
        const m2 = /^(\d{1,3})\s*\/\s*(\d{1,3})$/.exec(t);
        if(!m2){ alert('⛔ Parcelamento no formato pagas/total, ex.: 16/24 — ou vazio para limpar.'); inp.value = inp.dataset.prevval ?? ''; return; }
        parc = { paid:+m2[1], total:+m2[2] };
      }
      const r = pfActSetExpenseInstallments(key, id, parc);
      if(r.ok===false){ inp.value = inp.dataset.prevval ?? ''; }
      fbAtoUI(r);
    });
  });
  root.querySelectorAll('[data-fe-status]').forEach(sel=>{
    sel.addEventListener('focus',()=>{ sel.dataset.prevval = sel.value; });
    sel.addEventListener('change',()=>{
      const r = pfActSetExpenseStatus(key, sel.dataset.feStatus, sel.value);
      if(r.ok===false){ sel.value = sel.dataset.prevval || 'PENDENTE'; }
      fbAtoUI(r);
    });
  });
  root.querySelectorAll('[data-fe-del]').forEach(btn=>btn.addEventListener('click',()=>{
    const id = btn.dataset.feDel;
    const m = S.personalFinance.months[key];
    const rec = m && m.expenses.find(e=>e.id===id);
    const temDado = rec && ((rec.name||'').trim() || rec.targetAmount!==null || rec.expectedAmount!==null || rec.executedCash!==null || rec.executedCard!==null);
    if(temDado && !confirm('Excluir a despesa "'+(rec.name||'')+'"?')) return;
    fbAtoUI(pfActDeleteExpense(key, id));
  }));

  // ---- destino do excedente (E) ----
  const addA = root.querySelector('[data-fa-add]');
  if(addA) addA.addEventListener('click',()=>{
    const label = prompt('Destino (ex.: Reserva Emergência):');
    if(label===null) return;                       // cancelar = zero mutação
    const bruto = prompt('Valor destinado (R$):');
    if(bruto===null) return;
    const c = parseBRLCents(bruto);
    if(c===null || Number.isNaN(c) || c<0){ alert('⛔ Destinação exige valor ≥ 0 — linha sem valor não se cria.'); return; }
    fbAtoUI(pfActAddAllocation(key, { label, amount: c }));
  });
  root.querySelectorAll('[data-fa-campo]').forEach(inp=>{
    inp.addEventListener('focus',()=>{ inp.dataset.prevval = inp.value; });
    inp.addEventListener('change',()=>{
      const campo = inp.dataset.faCampo, id = inp.dataset.faId;
      let valor;
      if(campo==='label') valor = inp.value;
      else { valor = fbParseMoneyOr(inp); if(valor===undefined || valor===null){ if(valor===null) alert('⛔ Destinação exige valor — vazio não vale.'); inp.value = inp.dataset.prevval ?? ''; if(valor===null) return; return; } }
      const r = pfActUpdateAllocationField(key, id, campo, valor);
      if(r.ok===false){ inp.value = inp.dataset.prevval ?? ''; }
      fbAtoUI(r);
    });
  });
  root.querySelectorAll('[data-fa-del]').forEach(btn=>btn.addEventListener('click',()=>{
    const id = btn.dataset.faDel;
    const m = S.personalFinance.months[key];
    const rec = m && m.allocations.find(a=>a.id===id);
    if(rec && !confirm('Excluir a destinação "'+(rec.label||'')+'"?')) return;
    fbAtoUI(pfActDeleteAllocation(key, id));
  }));

  // ---- informações importantes (F) ----
  const addN = root.querySelector('[data-fn-add]');
  if(addN) addN.addEventListener('click',()=>{
    const texto = prompt('Informação importante:');
    if(texto===null) return;                       // cancelar = zero mutação
    fbAtoUI(pfActAddNote(key, texto));
  });
  root.querySelectorAll('[data-fn-toggle]').forEach(btn=>btn.addEventListener('click',()=>{
    fbAtoUI(pfActToggleNoteStatus(key, btn.dataset.fnToggle));
  }));
  root.querySelectorAll('[data-fn-del]').forEach(btn=>btn.addEventListener('click',()=>{
    const id = btn.dataset.fnDel;
    const m = S.personalFinance.months[key];
    const rec = m && m.notes.find(n=>n.id===id);
    if(rec && !confirm('Excluir a nota "'+(rec.text||'').slice(0,40)+'"?')) return;
    fbAtoUI(pfActDeleteNote(key, id));
  }));
  const rev = root.querySelector('[data-fb-review]');
  if(rev) rev.addEventListener('click',()=>{ fbGoTo(rev.dataset.fbReview); });
}

// ---- modal de recorrência (formulário ATÔMICO: aplica só no confirmar) ------
function fbOpenRecurrenceModal(key, incomeId){
  const rec = pfFindIncome(S.personalFinance, key, incomeId);
  if(!rec) return;
  const regra = rec.ruleId ? (S.personalFinance.recurringIncome||[]).find(r=>r.id===rec.ruleId) : null;
  const ativa = !!(regra && regra.active!==false);
  const valorIni = regra ? regra.amount : (rec.projectedAmount!==null ? rec.projectedAmount : null);
  const box=$('modalBox'); $('modalOverlay').classList.add('show');
  box.innerHTML = `
    <h3>⚙ Recorrência — ${esc(rec.name)}</h3>
    <div class="modal-q" data-qid="rec">
      <div class="ql"><label><input type="checkbox" id="fbRecOn" ${ativa?'checked':''}> Receita recorrente (gera projeção nos meses futuros)</label></div>
    </div>
    <div class="modal-q" data-qid="valor">
      <div class="ql">Valor mensal da regra (R$)</div>
      <input type="text" id="fbRecAmount" inputmode="decimal" value="${valorIni===null?'':esc((valorIni/100).toFixed(2).replace('.',','))}">
      <div class="modal-err">Informe o valor da regra — ≥ 0, ponto ou vírgula decimal. Em branco não é zero.</div>
    </div>
    <div class="modal-q" data-qid="inicio">
      <div class="ql">Início (YYYY-MM)</div>
      <input type="month" id="fbRecStart" value="${esc(regra?regra.startMonth:key)}">
      <div class="modal-err">Início inválido.</div>
    </div>
    <div class="modal-q" data-qid="fim">
      <div class="ql">Fim (opcional)</div>
      <input type="month" id="fbRecEnd" value="${esc(regra&&regra.endMonth?regra.endMonth:'')}">
      <div class="modal-err">Fim deve ser vazio ou ≥ início.</div>
    </div>
    <p class="risk-note">Regra vigente alcança apenas meses ainda não registrados. Meses já registrados nunca são reescritos; desligar a regra não apaga receitas históricas.</p>
    <div class="modal-actions">
      <button class="modal-btn" id="modalCancel">Cancelar</button>
      <button class="modal-btn confirm" id="modalConfirm">Confirmar</button>
    </div>`;
  box.querySelectorAll('.modal-err').forEach(e=>e.classList.remove('show'));
  $('modalCancel').addEventListener('click', closeModal);   // cancelar = zero mutação
  $('modalConfirm').addEventListener('click', ()=>{
    const ligar = $('fbRecOn').checked;
    let cfg = { recorrente: ligar };
    let falhou = false;
    const marcar = qid => { box.querySelector(`[data-qid="${qid}"] .modal-err`).classList.add('show'); falhou = true; };
    box.querySelectorAll('.modal-err').forEach(e=>e.classList.remove('show'));
    if(ligar){
      const c = parseBRLCents($('fbRecAmount').value);
      if(c===null || Number.isNaN(c) || c<0) marcar('valor');
      const ini = $('fbRecStart').value;
      if(!pfMonthKeyValid(ini)) marcar('inicio');
      const fim = $('fbRecEnd').value || null;
      if(fim!==null && (!pfMonthKeyValid(fim) || fim<ini)) marcar('fim');
      cfg = { recorrente:true, amount:c, startMonth:ini, endMonth:fim };
    }
    if(falhou) return;                                      // nada aplicado
    const r = pfActConfigureRecurrence(key, incomeId, cfg);
    if(r.ok===false && r.erro){ alert('⛔ '+r.erro); return; }
    closeModal();
    finpesBudgetRender();
  });
}

window.JPWFinBudget = { render: finpesBudgetRender, checkPending: fbMaybePendingPrompt };

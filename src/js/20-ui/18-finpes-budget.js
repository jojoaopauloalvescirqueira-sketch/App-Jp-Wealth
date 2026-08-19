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
  html += fbAssetsHTML();
  html += fbNotesHTML(key, materializado, bloqueado);
  html += '</div>';
  html += '<div class="fb-col fb-col-wide">';
  html += fbExpensesHTML(key, materializado, bloqueado);
  html += '</div>';
  html += '<div class="fb-col">';
  html += fbSummaryHTML(key, materializado);
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
function fbMoneyInput(valor, ds){
  const texto = (valor===null||valor===undefined) ? '' : (valor/100).toFixed(2).replace('.',',');
  return `<input type="text" class="fb-money" value="${esc(texto)}" ${ds} inputmode="decimal" placeholder="—">`;
}
function fbIncomesHTML(key, materializado, bloqueado){
  let linhas='';
  if(materializado){
    const m = S.personalFinance.months[key];
    linhas = (m.incomes||[]).map(i=>`<div class="fb-row" data-income="${esc(i.id)}">
      <span><input type="text" class="fb-text" value="${esc(i.name)}" data-fi-campo="name" data-fi-id="${esc(i.id)}">${i.ruleId?'<span class="fb-rule-mark" title="Receita recorrente (regra vigente)">↻</span>':''}</span>
      <span>${fbMoneyInput(i.projectedAmount,`data-fi-campo="projectedAmount" data-fi-id="${esc(i.id)}"`)}</span>
      <span>${fbMoneyInput(i.receivedAmount,`data-fi-campo="receivedAmount" data-fi-id="${esc(i.id)}"`)}</span>
      <span class="fb-actions"><select class="fb-status-sel" data-fi-status="${esc(i.id)}">
        ${['PROJETADA','RECEBIDA','CANCELADA'].map(st=>`<option value="${st}" ${st===i.status?'selected':''}>${st}</option>`).join('')}
      </select>
      <button type="button" class="row-del" data-fi-cfg="${esc(i.id)}" title="Configurar recorrência">⚙</button>
      <button type="button" class="row-del" data-fi-del="${esc(i.id)}" title="Excluir receita">✕</button></span>
    </div>`).join('');
  } else {
    linhas = pfVirtualIncomes(key).map(v=>`<div class="fb-row fb-ghost" title="Projeção da regra recorrente — editar registra o mês">
      <span>◌ ${esc(v.name)} <span class="fb-rule-mark">↻</span></span>
      <span>${fbMoneyInput(v.projectedAmount,`data-fg-campo="projectedAmount" data-fg-rule="${esc(v.ruleId)}"`)}</span>
      <span>${fbMoneyInput(null,`data-fg-campo="receivedAmount" data-fg-rule="${esc(v.ruleId)}"`)}</span>
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
    <div class="fb-totals"><span>Receita projetada: <b>${formatBRLCents(totProj)}</b></span>
      <span>Receita recebida: <b>${m ? formatBRLCents(totRec) : '—'}</b>${cobTxt}</span></div>
    <button type="button" class="reset-btn" data-fi-add ${bloqueado?'disabled title="Módulo em modo leitura"':''}>+ Adicionar receita</button>
  </div>`;
}
function fbExpensesHTML(){
  return `<div class="card fb-card" id="fbExpenses">
    <h2>Despesas <span class="art">Meta ≠ Previsto ≠ Executado</span></h2>
    <p class="risk-note">Em desenvolvimento (Bloco C).</p>
  </div>`;
}
function fbSummaryHTML(){
  return `<div class="card fb-card" id="fbSummary">
    <h2>Resumo do Mês <span class="art">soma parcial nunca vira total</span></h2>
    <p class="risk-note">Em desenvolvimento (Bloco D).</p>
  </div>`;
}
function fbAllocationsHTML(){
  return `<div class="card fb-card" id="fbAllocations">
    <h2>Destino do Excedente <span class="art">a sobra é insumo, não resultado</span></h2>
    <p class="risk-note">Em desenvolvimento (Bloco E).</p>
  </div>`;
}
function fbAssetsHTML(){
  return `<div class="card fb-card" id="fbAssets">
    <h2>Ativos <span class="art">patrimônio sempre derivado</span></h2>
    <p class="risk-note">Integração com Inventário pendente (PF-07/PF-08). Sem digitação aqui.</p>
  </div>`;
}
function fbNotesHTML(){
  return `<div class="card fb-card" id="fbNotes">
    <h2>Informações Importantes <span class="art">texto + status, nada mais</span></h2>
    <p class="risk-note">Em desenvolvimento (Bloco F).</p>
  </div>`;
}
function fbPendingBannerHTML(){ return ''; } // Bloco F

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
  if(hoje) hoje.addEventListener('click',()=>{ fbGoTo(pfCurrentMonthKey()); });

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

window.JPWFinBudget = { render: finpesBudgetRender };

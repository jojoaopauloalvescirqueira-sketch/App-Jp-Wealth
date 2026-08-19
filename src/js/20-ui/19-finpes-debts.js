// ============ FINANÇAS PESSOAIS · DÍVIDAS & CRÉDITO (PF-03) ============
// Renderizador do workspace #finpesDividas. Consome exclusivamente o núcleo do
// domínio: relevância temporal, snapshots, contrato — nada é recalculado aqui
// por conta própria e nenhum derivado persiste. Todo ato passa pelo write gate.
//
// Competência exibida é estado de UI EFÊMERO (padrão fbMonth do PF-02);
// navegar é read-only. O saldo mostrado é SEMPRE o observado na competência —
// a última observação anterior aparece apenas como informação secundária
// DATADA e jamais entra em total (dado antigo não vira fato atual).

let fdMonth = null;

function fdCurrentKey(){
  if(!fdMonth || !pfMonthKeyValid(fdMonth)) fdMonth = pfCurrentMonthKey();
  return fdMonth;
}
function fdGoTo(key){ fdMonth = key; finpesDebtsRender(); }

const PF_DEBT_TYPE_LABELS = {
  FINANCIAMENTO:'Financiamento', EMPRESTIMO:'Empréstimo', CARTAO:'Cartão',
  CREDIARIO:'Crediário', IMPOSTO:'Imposto', PESSOA_FISICA:'Pessoa Física', OUTRO:'Outro',
};

function finpesDebtsRender(){
  const root = document.getElementById('finpesDebtsRoot');
  if(!root) return;
  const key = fdCurrentKey();
  const bloqueado = (typeof pfWriteBlockReason==='function') ? pfWriteBlockReason() : null;
  let html = `<div class="fb-header">
    <button type="button" class="reset-btn fb-nav" data-fd-nav="-1" title="Mês anterior">←</button>
    <span class="fb-month-label">${esc(pfMonthLabel(key))}</span>
    <button type="button" class="reset-btn fb-nav" data-fd-nav="1" title="Mês seguinte">→</button>
    <button type="button" class="reset-btn" data-fd-today title="Ir para o mês corrente">Hoje</button>
  </div>`;
  html += fdDebtsHTML(key, bloqueado);
  html += fdCreditHTML(bloqueado);
  root.innerHTML = html;
  fdBind(root, key, bloqueado);
}

// ---- DÍVIDAS ----------------------------------------------------------------
function fdDebtsHTML(key, bloqueado){
  const todas = (S.personalFinance.debts||[]).filter(Boolean);
  const cov = pfDebtCoverage(key);
  const total = pfKnownDebtTotal(key);
  const linhas = todas.map(d=>{
    const relevante = pfDebtRelevant(d, key);
    const snap = relevante ? pfDebtSnapshotIn(key, d.id) : null;
    let saldo;
    if(!relevante) saldo = '<span class="fb-aux">fora de vigência</span>';
    else if(snap) saldo = `<b>${formatBRLCents(snap.balance)}</b>`;
    else {
      const ult = pfLastObservation(d.id, key);
      saldo = '<span class="fb-partial">Sem observação nesta competência</span>'
        + (ult ? `<br><span class="fb-aux">última: ${formatBRLCents(ult.snapshot.balance)} em ${esc(pfMonthLabel(ult.monthKey))}</span>` : '');
    }
    const pagas = snap && snap.installmentsPaid!=null ? snap.installmentsPaid : '—';
    const rest = pfRemainingInstallments(d, snap);
    const vig = esc(d.startMonth)+' → '+(d.closedMonth ? esc(d.closedMonth) : 'em aberto');
    return `<div class="fd-row ${relevante?'':'fd-irrelevante'}" data-debt="${esc(d.id)}">
      <span>${esc(d.creditor)}${d.description?`<br><span class="fb-aux">${esc(d.description)}</span>`:''}</span>
      <span>${esc(PF_DEBT_TYPE_LABELS[d.type]||d.type)}</span>
      <span class="fd-money">${formatBRLCents(d.originalAmount)}</span>
      <span class="fd-money">${formatBRLCents(d.installmentAmount)}</span>
      <span class="fd-center">${d.installmentsTotal==null?'—':d.installmentsTotal}</span>
      <span>${saldo}</span>
      <span class="fd-center">${pagas}</span>
      <span class="fd-center">${rest==null?'—':rest}</span>
      <span class="fb-aux">${vig}</span>
      <span class="fb-actions">
        <button type="button" class="row-del" data-fd-edit="${esc(d.id)}" title="Editar contrato">✎</button>
        ${relevante?`<button type="button" class="row-del" data-fd-obs="${esc(d.id)}" title="Registrar/corrigir observação desta competência">◉</button>`:''}
        <button type="button" class="row-del" data-fd-del="${esc(d.id)}" title="Excluir (só sem história)">✕</button>
      </span>
    </div>`;
  }).join('');
  const cobTxt = cov.relevantes===0
    ? '<span class="fb-aux">Nenhuma dívida relevante nesta competência</span>'
    : (cov.completa
        ? `<span>Dívida total: <b>${formatBRLCents(total)}</b></span>`
        : `<span>${formatBRLCents(total)} observados <span class="fb-partial">PARCIAL · ${cov.observadas} de ${cov.relevantes} dívidas observadas</span></span>`);
  return `<div class="card fb-card" id="fdDebts">
    <h2>Dívidas <span class="art">identidade temporal · saldo é observação da competência</span></h2>
    <div class="fd-row fd-head"><span>Credor</span><span>Tipo</span><span>V. original</span><span>Parcela</span><span>Parc.</span><span>Saldo na competência</span><span>Pagas</span><span>Rest.</span><span>Vigência</span><span></span></div>
    ${linhas || '<p class="fb-empty">Nenhuma dívida cadastrada.</p>'}
    <div class="fb-totals" id="fdDebtTotals">${cobTxt}</div>
    <button type="button" class="reset-btn" data-fd-add ${bloqueado?'disabled title="Módulo em modo leitura"':''}>+ Nova dívida</button>
  </div>`;
}

// ---- CRÉDITO (Bloco D) ------------------------------------------------------
function fdMoneyInput(valor, ds){
  const texto = (valor===null||valor===undefined) ? '' : (valor/100).toFixed(2).replace('.',',');
  return `<input type="text" class="fb-money" value="${esc(texto)}" ${ds} inputmode="decimal" placeholder="—">`;
}
function fdCreditHTML(bloqueado){
  const linhas = (S.personalFinance.creditLines||[]).filter(Boolean).map(l=>{
    const der = pfCreditLineDerived(l);
    const disp = der.available===null ? '—' : formatBRLCents(der.available);
    const util = der.utilization===null ? '<span class="fb-aux">N/A</span>'
      : (der.utilization*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%';
    return `<div class="fc-row ${der.estouro?'fc-estouro':''}" data-credit="${esc(l.id)}">
      <span><input type="text" class="fb-text" value="${esc(l.institution)}" data-fc-campo="institution" data-fc-id="${esc(l.id)}"></span>
      <span><input type="text" class="fb-text" value="${esc(l.instrument)}" data-fc-campo="instrument" data-fc-id="${esc(l.id)}"></span>
      <span><input type="text" class="fb-text" value="${esc(l.type)}" data-fc-campo="type" data-fc-id="${esc(l.id)}"></span>
      <span>${fdMoneyInput(l.totalLimit,`data-fc-campo="totalLimit" data-fc-id="${esc(l.id)}"`)}</span>
      <span>${fdMoneyInput(l.used,`data-fc-campo="used" data-fc-id="${esc(l.id)}"`)}</span>
      <span class="fd-money">${disp}${der.estouro?' <span class="fb-partial" title="Utilizado acima do limite — legítimo, sem truncar">⚠ estouro</span>':''}</span>
      <span class="fd-center">${util}</span>
      <span class="fb-actions"><button type="button" class="row-del" data-fc-del="${esc(l.id)}" title="Excluir linha">✕</button></span>
    </div>`;
  }).join('');
  const k = pfCreditKPIs();
  const badge = c => c.total>0 && !c.completa ? ` <span class="fb-partial">PARCIAL · ${c.conhecidas}/${c.total}</span>` : '';
  const kpis = `
    <span>Limite total: <b>${k.limitCoverage.completa ? formatBRLCents(k.knownTotalLimit) : formatBRLCents(k.knownTotalLimit)+' conhecidos'}</b>${badge(k.limitCoverage)}</span>
    <span>Total utilizado: <b>${k.usedCoverage.completa ? formatBRLCents(k.knownUsed) : formatBRLCents(k.knownUsed)+' conhecidos'}</b>${badge(k.usedCoverage)}</span>
    <span>Total livre: <b>${k.totalFree===null ? '—' : formatBRLCents(k.totalFree)}</b>${k.totalFree===null?' <span class="fb-partial">componentes incompletos</span>':''}</span>
    <span>Utilização consolidada: <b>${k.utilizationConsolidated===null ? 'N/A' : (k.utilizationConsolidated*100).toLocaleString('pt-BR',{maximumFractionDigits:1})+'%'}</b></span>`;
  return `<div class="card fb-card" id="fdCredit">
    <h2>Limites de Crédito <span class="art">estado vigente · sem série histórica nesta versão</span></h2>
    <div class="fc-row fc-head"><span>Instituição</span><span>Instrumento</span><span>Tipo</span><span>Limite</span><span>Utilizado</span><span>Disponível</span><span>Utilização</span><span></span></div>
    ${linhas || '<p class="fb-empty">Nenhuma linha de crédito.</p>'}
    <div class="fb-totals" id="fdCreditKPIs">${kpis}</div>
    <div class="fb-totals" id="fdRatio">${fdRatioHTML()}</div>
    <button type="button" class="reset-btn" data-fc-add ${bloqueado?'disabled title="Módulo em modo leitura"':''}>+ Adicionar linha de crédito</button>
  </div>`;
}
// Razão dívida/limite — rotulada por extenso para não se confundir com a
// utilização de crédito (used/limit): métricas diferentes.
function fdRatioHTML(){
  const key = fdCurrentKey();
  const ratio = pfDebtToCreditRatio(key);
  if(ratio===null) return `<span>Dívida observada / limite total: <b>N/A</b> <span class="fb-partial">dados parciais ou limite zero</span></span>`;
  return `<span>Dívida observada / limite total (${esc(pfMonthLabel(key))}): <b>${(ratio*100).toLocaleString('pt-BR',{maximumFractionDigits:1})}%</b></span>`;
}

// ---- binds ------------------------------------------------------------------
function fdAtoUI(r){
  if(r && r.ok===false && r.erro) alert('⛔ ' + r.erro);
  finpesDebtsRender();
}
function fdBind(root, key, bloqueado){
  root.querySelectorAll('[data-fd-nav]').forEach(b=>b.addEventListener('click',()=>{
    fdGoTo(pfMonthAdd(fdCurrentKey(), +b.dataset.fdNav));
  }));
  const hoje = root.querySelector('[data-fd-today]');
  if(hoje) hoje.addEventListener('click',()=>{ fdGoTo(pfCurrentMonthKey()); });
  const add = root.querySelector('[data-fd-add]');
  if(add) add.addEventListener('click',()=>{ fdOpenDebtModal(null); });
  root.querySelectorAll('[data-fd-edit]').forEach(b=>b.addEventListener('click',()=>{ fdOpenDebtModal(b.dataset.fdEdit); }));
  root.querySelectorAll('[data-fd-obs]').forEach(b=>b.addEventListener('click',()=>{ fdOpenSnapshotModal(key, b.dataset.fdObs); }));
  root.querySelectorAll('[data-fd-del]').forEach(b=>b.addEventListener('click',()=>{
    const d = pfFindDebt(S.personalFinance, b.dataset.fdDel);
    if(d && !confirm('Excluir a dívida "'+d.creditor+'"? (bloqueado se houver observações)')) return;
    fdAtoUI(pfActDeleteDebt(b.dataset.fdDel));
  }));

  // ---- crédito (D) ----
  const addC = root.querySelector('[data-fc-add]');
  if(addC) addC.addEventListener('click',()=>{
    const inst = prompt('Instituição:');
    if(inst===null) return;                       // cancelar = zero mutação
    fdAtoUI(pfActAddCreditLine({ institution: inst, instrument:'', type:'', totalLimit:null, used:null }));
  });
  root.querySelectorAll('[data-fc-campo]').forEach(inp=>{
    inp.addEventListener('focus',()=>{ inp.dataset.prevval = inp.value; });
    inp.addEventListener('change',()=>{
      const campo = inp.dataset.fcCampo, id = inp.dataset.fcId;
      let valor;
      if(['institution','instrument','type'].includes(campo)) valor = inp.value;
      else {
        const c = parseBRLCents(inp.value);
        if(c===null) valor = null;
        else if(Number.isNaN(c) || c<0){ alert('⛔ Valor inválido (≥ 0 ou vazio).'); inp.value = inp.dataset.prevval ?? ''; return; }
        else valor = c;
      }
      const r = pfActUpdateCreditLineField(id, campo, valor);
      if(r.ok===false){ inp.value = inp.dataset.prevval ?? ''; }
      fdAtoUI(r);
    });
  });
  root.querySelectorAll('[data-fc-del]').forEach(b=>b.addEventListener('click',()=>{
    const l = pfFindCreditLine(S.personalFinance, b.dataset.fcDel);
    if(l && !confirm('Excluir a linha de crédito "'+l.institution+'"?')) return;
    fdAtoUI(pfActDeleteCreditLine(b.dataset.fcDel));
  }));
}

// ---- modal do CONTRATO (formulário atômico: rascunho local, aplica no confirmar)
function fdOpenDebtModal(debtId){
  const d = debtId ? pfFindDebt(S.personalFinance, debtId) : null;
  const money = v => (v===null||v===undefined) ? '' : (v/100).toFixed(2).replace('.',',');
  const box=$('modalBox'); $('modalOverlay').classList.add('show');
  box.innerHTML = `
    <h3>${d?'✎ Editar dívida':'+ Nova dívida'}</h3>
    <div class="modal-q" data-qid="creditor"><div class="ql">Credor / instituição</div>
      <input type="text" id="fdCreditor" value="${esc(d?d.creditor:'')}">
      <div class="modal-err">Credor obrigatório.</div></div>
    <div class="modal-q" data-qid="type"><div class="ql">Tipo</div>
      <select id="fdType">${PF_DEBT_TYPES.map(t=>`<option value="${t}" ${d&&d.type===t?'selected':''}>${PF_DEBT_TYPE_LABELS[t]}</option>`).join('')}</select></div>
    <div class="modal-q" data-qid="description"><div class="ql">Descrição / origem (opcional)</div>
      <input type="text" id="fdDescription" value="${esc(d?d.description:'')}"></div>
    <div class="modal-q" data-qid="originalAmount"><div class="ql">Valor original (R$, opcional)</div>
      <input type="text" id="fdOriginal" inputmode="decimal" value="${money(d?d.originalAmount:null)}">
      <div class="modal-err">Valor inválido (≥ 0 ou vazio).</div></div>
    <div class="modal-q" data-qid="installmentAmount"><div class="ql">Valor da parcela (R$, opcional)</div>
      <input type="text" id="fdInstAmount" inputmode="decimal" value="${money(d?d.installmentAmount:null)}">
      <div class="modal-err">Valor inválido (≥ 0 ou vazio).</div></div>
    <div class="modal-q" data-qid="installmentsTotal"><div class="ql">Total de parcelas (vazio = sem contrato parcelado)</div>
      <input type="number" id="fdInstTotal" min="1" step="1" value="${d&&d.installmentsTotal!=null?d.installmentsTotal:''}">
      <div class="modal-err">Inteiro ≥ 1 ou vazio.</div></div>
    <div class="modal-q" data-qid="startMonth"><div class="ql">Mês inicial</div>
      <input type="month" id="fdStart" value="${esc(d?d.startMonth:fdCurrentKey())}">
      <div class="modal-err">Obrigatório (YYYY-MM).</div></div>
    <div class="modal-q" data-qid="closedMonth"><div class="ql">Mês de encerramento (vazio = em aberto)</div>
      <input type="month" id="fdClosed" value="${esc(d&&d.closedMonth?d.closedMonth:'')}">
      <div class="modal-err">Vazio ou ≥ mês inicial.</div></div>
    <p class="risk-note">Editar o contrato jamais pode orfanar observações históricas — conflitos são bloqueados nomeando a competência. Ao encerrar, considere registrar o saldo final daquela competência (sugestão, não automático).</p>
    <div class="modal-actions">
      <button class="modal-btn" id="modalCancel">Cancelar</button>
      <button class="modal-btn confirm" id="modalConfirm">Confirmar</button>
    </div>`;
  $('modalCancel').addEventListener('click', closeModal);   // cancelar = zero mutação
  $('modalConfirm').addEventListener('click', ()=>{
    box.querySelectorAll('.modal-err').forEach(e=>e.classList.remove('show'));
    let falhou=false;
    const marcar = qid => { box.querySelector(`[data-qid="${qid}"] .modal-err`).classList.add('show'); falhou=true; };
    const parseM = (id,qid)=>{ const c=parseBRLCents($(id).value); if(Number.isNaN(c)||c<0){ marcar(qid); return undefined; } return c; };
    const original = parseM('fdOriginal','originalAmount');
    const parcela  = parseM('fdInstAmount','installmentAmount');
    const totalRaw = $('fdInstTotal').value.trim();
    const total = totalRaw==='' ? null : Number(totalRaw);
    if(total!==null && !(Number.isInteger(total) && total>=1)) marcar('installmentsTotal');
    if(!$('fdCreditor').value.trim()) marcar('creditor');
    if(!pfMonthKeyValid($('fdStart').value)) marcar('startMonth');
    const closed = $('fdClosed').value || null;
    if(closed!==null && (!pfMonthKeyValid(closed) || closed < $('fdStart').value)) marcar('closedMonth');
    if(falhou) return;
    const dados = { creditor:$('fdCreditor').value, type:$('fdType').value,
      description:$('fdDescription').value, originalAmount:original, installmentAmount:parcela,
      installmentsTotal: total, startMonth:$('fdStart').value, closedMonth: closed };
    const r = debtId ? pfActUpdateDebt(debtId, dados) : pfActAddDebt(dados);
    if(r.ok===false && r.erro){ alert('⛔ '+r.erro); return; }   // integridade vs história: bloqueio nomeado
    closeModal();
    finpesDebtsRender();
  });
}

// ---- modal da OBSERVAÇÃO da competência ------------------------------------
function fdOpenSnapshotModal(key, debtId){
  const d = pfFindDebt(S.personalFinance, debtId);
  if(!d) return;
  const snap = pfDebtSnapshotIn(key, debtId);
  const encerrandoAqui = d.closedMonth===key;
  const box=$('modalBox'); $('modalOverlay').classList.add('show');
  box.innerHTML = `
    <h3>◉ Observação — ${esc(d.creditor)} · ${esc(pfMonthLabel(key))}</h3>
    ${snap?'<p class="risk-note">Já existe observação nesta competência — confirmar SUBSTITUI (correção deliberada).</p>':''}
    ${encerrandoAqui?'<p class="risk-note">Esta é a competência de encerramento — considere registrar o saldo final. Saldo diferente de zero é legítimo (acordo, perdão, baixa).</p>':''}
    <div class="modal-q" data-qid="balance"><div class="ql">Saldo devedor observado (R$)</div>
      <input type="text" id="fdBalance" inputmode="decimal" value="${snap?(snap.balance/100).toFixed(2).replace('.',','):''}">
      <div class="modal-err">Saldo obrigatório, ≥ 0 — a observação existe porque foi observada.</div></div>
    <div class="modal-q" data-qid="paid"><div class="ql">Parcelas pagas ${d.installmentsTotal==null?'(sem contrato parcelado — deixe vazio)':'(0 a '+d.installmentsTotal+', opcional)'}</div>
      <input type="number" id="fdPaid" min="0" step="1" value="${snap&&snap.installmentsPaid!=null?snap.installmentsPaid:''}">
      <div class="modal-err">Inteiro entre 0 e o total do contrato, ou vazio.</div></div>
    <div class="modal-actions">
      <button class="modal-btn" id="modalCancel">Cancelar</button>
      <button class="modal-btn confirm" id="modalConfirm">Confirmar</button>
    </div>`;
  $('modalCancel').addEventListener('click', closeModal);
  $('modalConfirm').addEventListener('click', ()=>{
    box.querySelectorAll('.modal-err').forEach(e=>e.classList.remove('show'));
    let falhou=false;
    const marcar = qid => { box.querySelector(`[data-qid="${qid}"] .modal-err`).classList.add('show'); falhou=true; };
    const c = parseBRLCents($('fdBalance').value);
    if(c===null || Number.isNaN(c) || c<0) marcar('balance');
    const paidRaw = $('fdPaid').value.trim();
    const paid = paidRaw==='' ? null : Number(paidRaw);
    if(paid!==null && !(Number.isInteger(paid) && paid>=0)) marcar('paid');
    if(falhou) return;
    const r = pfActRecordDebtSnapshot(key, debtId, { balance:c, installmentsPaid:paid });
    if(r.ok===false && r.erro){ alert('⛔ '+r.erro); return; }
    closeModal();
    finpesDebtsRender();
  });
}

window.JPWFinDebts = { render: finpesDebtsRender };

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
function fbIncomesHTML(key, materializado, bloqueado){
  const virtuais = materializado ? [] : pfVirtualIncomes(key);
  const linhas = materializado
    ? (S.personalFinance.months[key].incomes||[]).map(i=>
        `<div class="fb-row"><span>${esc(i.name)}</span><span>${formatBRLCents(i.projectedAmount)}</span><span>${formatBRLCents(i.receivedAmount)}</span><span class="fb-status">${esc(i.status)}</span></div>`).join('')
    : virtuais.map(v=>
        `<div class="fb-row fb-ghost" title="Projeção da regra recorrente — nada registrado"><span>◌ ${esc(v.name)}</span><span>${formatBRLCents(v.projectedAmount)}</span><span>—</span><span class="fb-status">PROJEÇÃO</span></div>`).join('');
  return `<div class="card fb-card" id="fbIncomes">
    <h2>Receitas <span class="art">projetado ≠ recebido · ausência ≠ zero</span></h2>
    <div class="fb-row fb-head"><span>Descrição</span><span>Projetado</span><span>Recebido</span><span>Status</span></div>
    ${linhas || '<p class="fb-empty">Nenhuma receita neste mês.</p>'}
    <p class="risk-note">Edição de receitas chega no Bloco B.</p>
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
function fbBind(root, key){
  root.querySelectorAll('[data-fb-nav]').forEach(b=>b.addEventListener('click',()=>{
    fbGoTo(pfMonthAdd(fbCurrentKey(), +b.dataset.fbNav));
  }));
  const hoje = root.querySelector('[data-fb-today]');
  if(hoje) hoje.addEventListener('click',()=>{ fbGoTo(pfCurrentMonthKey()); });
}

window.JPWFinBudget = { render: finpesBudgetRender };

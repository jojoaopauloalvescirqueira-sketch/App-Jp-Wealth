// ============ FINANÇAS PESSOAIS · CENÁRIOS (PF-05) ============
// Renderizador do workspace #finpesCenarios. Consome exclusivamente o núcleo
// do domínio (atos pfActScenario*, calculadores pfScenario*). Linguagem
// DESCRITIVA de hipótese: "cenário", "composição", "horizonte" — nunca
// "previsão", "probabilidade" ou "resultado esperado": não há modelo
// estatístico que sustente forecast, e a UI não finge que há.

function fsHorizonLabel(h){ return h===null ? 'HOJE' : pfMonthLabel(h); }
const FS_KIND_LABELS = { PESSIMISTA:'Pessimista', BASE:'Base', OTIMISTA:'Otimista', LIVRE:'Livre' };

function finpesScenariosRender(){
  const root = document.getElementById('finpesScenariosRoot');
  if(!root) return;
  const bloqueado = (typeof pfWriteBlockReason==='function') ? pfWriteBlockReason() : null;
  const cenarios = (S.personalFinance.scenarios||[]).filter(Boolean);
  // agrupamento por horizon: HOJE (null) primeiro, depois YYYY-MM crescente
  const grupos = new Map();
  for(const sc of cenarios){
    const k = sc.horizon===null ? '' : sc.horizon;
    if(!grupos.has(k)) grupos.set(k, []);
    grupos.get(k).push(sc);
  }
  const chaves = [...grupos.keys()].sort();
  let html = `<div class="fb-header">
    <span class="fb-month-label">Cenários</span>
    <button type="button" class="reset-btn" data-fs-new ${bloqueado?'disabled title="Módulo em modo leitura"':''}>+ Novo cenário</button>
    <button type="button" class="reset-btn" data-fs-from ${bloqueado?'disabled title="Módulo em modo leitura"':''}>Criar a partir de mês</button>
  </div>`;
  if(!cenarios.length){
    html += `<div class="card fb-card"><h2>Cenários <span class="art">composições hipotéticas comparáveis por horizonte</span></h2>
      <p class="fb-empty">Nenhum cenário. Uma hipótese é uma composição completa de receitas e despesas — crie do zero ou a partir de um mês registrado.</p></div>`;
  }
  for(const k of chaves){
    const h = k==='' ? null : k;
    html += `<div class="fs-horizon"><h3 class="fs-horizon-title">${esc(fsHorizonLabel(h))}</h3><div class="fs-cards">`;
    for(const sc of grupos.get(k)) html += fsCardHTML(sc, bloqueado);
    html += `</div></div>`;
  }
  root.innerHTML = html;
  fsBind(root, bloqueado);
}

// Sentinela de LEITURA (HA PF-05): read-only não autoriza reinterpretar uma
// unidade desconhecida como BRL — nem em texto, nem em campo editável. A
// estrutura da hipótese (nomes, kind, horizonte, proveniência, ordem da
// cascata) permanece legível; todo montante vira "—" até a unidade voltar.
function fsMoneyText(cents, bloqueado){
  return bloqueado ? '—' : formatBRLCents(cents);
}
function fsMoneyInput(valor, ds, bloqueado){
  if(bloqueado) return '<span class="fs-saldo" title="Unidade monetária não reconhecida">—</span>';
  const texto = (valor===null||valor===undefined) ? '' : (valor/100).toFixed(2).replace('.',',');
  return `<input type="text" class="fb-money" value="${esc(texto)}" ${ds} inputmode="decimal">`;
}

function fsCardHTML(sc, bloqueado){
  const receitas = (sc.incomes||[]).map(i=>`<div class="fs-item" data-fs-item>
      <input type="text" class="fb-text" value="${esc(i.name)}" ${bloqueado?'disabled':''} data-fs-campo="name" data-fs-lista="incomes" data-fs-sc="${esc(sc.id)}" data-fs-id="${esc(i.id)}">
      ${fsMoneyInput(i.amount,`data-fs-campo="amount" data-fs-lista="incomes" data-fs-sc="${esc(sc.id)}" data-fs-id="${esc(i.id)}"`, bloqueado)}
      <span></span>
      <button type="button" class="row-del" data-fs-del-item ${bloqueado?'disabled':''} data-fs-lista="incomes" data-fs-sc="${esc(sc.id)}" data-fs-id="${esc(i.id)}" title="Excluir item">✕</button>
    </div>`).join('');
  const cascata = pfScenarioCascade(sc);
  const despesas = cascata.map(c=>`<div class="fs-item" data-fs-item>
      <input type="text" class="fb-text" value="${esc(c.item.name)}" ${bloqueado?'disabled':''} data-fs-campo="name" data-fs-lista="expenses" data-fs-sc="${esc(sc.id)}" data-fs-id="${esc(c.item.id)}">
      ${fsMoneyInput(c.item.amount,`data-fs-campo="amount" data-fs-lista="expenses" data-fs-sc="${esc(sc.id)}" data-fs-id="${esc(c.item.id)}"`, bloqueado)}
      <span class="fs-saldo ${!bloqueado&&c.saldo<0?'fs-neg':''}" title="Saldo após esta despesa (cascata)">${fsMoneyText(c.saldo, bloqueado)}</span>
      <button type="button" class="row-del" data-fs-del-item ${bloqueado?'disabled':''} data-fs-lista="expenses" data-fs-sc="${esc(sc.id)}" data-fs-id="${esc(c.item.id)}" title="Excluir item">✕</button>
    </div>`).join('');
  const sobra = pfScenarioSurplus(sc);
  return `<div class="card fb-card fs-card" data-fs-card="${esc(sc.id)}">
    <h2>${esc(sc.name)} <span class="art">${esc(FS_KIND_LABELS[sc.kind]||sc.kind)}${sc.baselineFrom?` · criado a partir de ${esc(pfMonthLabel(sc.baselineFrom))}`:''}</span></h2>
    <div class="fb-totals">
      <span>Receita total: <b>${fsMoneyText(pfScenarioIncome(sc), bloqueado)}</b></span>
      <span>Despesa total: <b>${fsMoneyText(pfScenarioExpenses(sc), bloqueado)}</b></span>
      <span>Sobra/Falta: <b class="${!bloqueado&&sobra<0?'fs-neg':''}">${fsMoneyText(sobra, bloqueado)}</b></span>
    </div>
    <div class="fs-sec">RECEITAS DA HIPÓTESE</div>
    ${receitas || '<p class="fb-empty">Nenhuma receita.</p>'}
    <button type="button" class="reset-btn fs-add" data-fs-add-item data-fs-lista="incomes" data-fs-sc="${esc(sc.id)}" ${bloqueado?'disabled':''}>+ receita</button>
    <div class="fs-sec">DESPESAS — CASCATA</div>
    ${despesas || '<p class="fb-empty">Nenhuma despesa.</p>'}
    <button type="button" class="reset-btn fs-add" data-fs-add-item data-fs-lista="expenses" data-fs-sc="${esc(sc.id)}" ${bloqueado?'disabled':''}>+ despesa</button>
    <div class="fs-foot">
      <button type="button" class="row-del" data-fs-edit="${esc(sc.id)}" ${bloqueado?'disabled':''} title="Editar nome/tipo/horizonte">✎</button>
      <button type="button" class="row-del" data-fs-del="${esc(sc.id)}" ${bloqueado?'disabled':''} title="Excluir cenário">✕</button>
    </div>
  </div>`;
}

function fsAtoUI(r){
  if(r && r.ok===false && r.erro) alert('⛔ ' + r.erro);
  finpesScenariosRender();
}

function fsBind(root, bloqueado){
  const novo = root.querySelector('[data-fs-new]');
  if(novo) novo.addEventListener('click',()=>fsOpenScenarioModal(null));
  const from = root.querySelector('[data-fs-from]');
  if(from) from.addEventListener('click',()=>fsOpenFromMonthModal());
  root.querySelectorAll('[data-fs-edit]').forEach(b=>b.addEventListener('click',()=>fsOpenScenarioModal(b.dataset.fsEdit)));
  root.querySelectorAll('[data-fs-del]').forEach(b=>b.addEventListener('click',()=>{
    const sc = pfFindScenario(S.personalFinance, b.dataset.fsDel);
    if(sc && !confirm('Excluir o cenário "'+sc.name+'"? Meses reais não são afetados.')) return;
    fsAtoUI(pfActDeleteScenario(b.dataset.fsDel));
  }));
  root.querySelectorAll('[data-fs-add-item]').forEach(b=>b.addEventListener('click',()=>{
    const nome = prompt('Nome do item:');
    if(nome===null) return;                        // cancelar = zero mutação
    const bruto = prompt('Valor (R$) — obrigatório, 0 vale:');
    if(bruto===null) return;
    const c = parseBRLCents(bruto);
    if(c===null || Number.isNaN(c) || c<0){ alert('⛔ Valor obrigatório (≥ 0) — linha sem valor não se cria.'); return; }
    fsAtoUI(pfActAddScenarioItem(b.dataset.fsSc, b.dataset.fsLista, { name:nome, amount:c }));
  }));
  root.querySelectorAll('[data-fs-campo]').forEach(inp=>{
    inp.addEventListener('focus',()=>{ inp.dataset.prevval = inp.value; });
    inp.addEventListener('change',()=>{
      const { fsCampo, fsLista, fsSc, fsId } = inp.dataset;
      let valor;
      if(fsCampo==='name') valor = inp.value;
      else {
        const c = parseBRLCents(inp.value);
        if(c===null || Number.isNaN(c) || c<0){ alert('⛔ Valor obrigatório (≥ 0) em cenário — vazio não vale.'); inp.value = inp.dataset.prevval ?? ''; return; }
        valor = c;
      }
      const r = pfActUpdateScenarioItem(fsSc, fsLista, fsId, fsCampo, valor);
      if(r.ok===false){ inp.value = inp.dataset.prevval ?? ''; }
      fsAtoUI(r);
    });
  });
  root.querySelectorAll('[data-fs-del-item]').forEach(b=>b.addEventListener('click',()=>{
    fsAtoUI(pfActDeleteScenarioItem(b.dataset.fsSc, b.dataset.fsLista, b.dataset.fsId));
  }));
}

// ---- modal de cenário (novo/editar) — formulário ATÔMICO -------------------
function fsScenarioFormHTML(sc){
  return `
    <div class="modal-q" data-qid="name"><div class="ql">Nome do cenário</div>
      <input type="text" id="fsName" value="${esc(sc?sc.name:'')}">
      <div class="modal-err">Nome obrigatório.</div></div>
    <div class="modal-q" data-qid="kind"><div class="ql">Tipo da hipótese</div>
      <select id="fsKind">${PF_SCENARIO_KINDS.map(k=>`<option value="${k}" ${sc&&sc.kind===k?'selected':''}>${FS_KIND_LABELS[k]}</option>`).join('')}</select></div>
    <div class="modal-q" data-qid="horizon"><div class="ql">Horizonte (vazio = HOJE)</div>
      <input type="month" id="fsHorizon" value="${esc(sc&&sc.horizon?sc.horizon:'')}">
      <div class="modal-err">Vazio ou YYYY-MM.</div></div>`;
}
function fsReadScenarioForm(box, marcar){
  const name = $('fsName').value;
  if(!name.trim()) marcar('name');
  const horizon = $('fsHorizon').value || null;
  if(horizon!==null && !pfMonthKeyValid(horizon)) marcar('horizon');
  return { name, kind: $('fsKind').value, horizon };
}
function fsOpenScenarioModal(scenarioId){
  const sc = scenarioId ? pfFindScenario(S.personalFinance, scenarioId) : null;
  const box=$('modalBox'); $('modalOverlay').classList.add('show');
  box.innerHTML = `<h3>${sc?'✎ Editar cenário':'+ Novo cenário'}</h3>${fsScenarioFormHTML(sc)}
    <div class="modal-actions">
      <button class="modal-btn" id="modalCancel">Cancelar</button>
      <button class="modal-btn confirm" id="modalConfirm">Confirmar</button>
    </div>`;
  $('modalCancel').addEventListener('click', closeModal);   // cancelar = zero mutação
  $('modalConfirm').addEventListener('click', ()=>{
    box.querySelectorAll('.modal-err').forEach(e=>e.classList.remove('show'));
    let falhou=false;
    const marcar = qid => { box.querySelector(`[data-qid="${qid}"] .modal-err`).classList.add('show'); falhou=true; };
    const dados = fsReadScenarioForm(box, marcar);
    if(falhou) return;
    const r = sc ? pfActUpdateScenarioMeta(scenarioId, dados) : pfActAddScenario(dados);
    if(r.ok===false && r.erro){ alert('⛔ '+r.erro); return; }
    closeModal();
    finpesScenariosRender();
  });
}

// ---- modal "Criar a partir de mês" — cópia deliberada e atômica ------------
function fsOpenFromMonthModal(){
  const box=$('modalBox'); $('modalOverlay').classList.add('show');
  box.innerHTML = `<h3>Criar cenário a partir de um mês registrado</h3>
    <p class="risk-note">Cópia deliberada da composição PLANEJADA (projetado/previsto, sem canceladas). O mês precisa estar registrado e completo no planejado. Depois da cópia, cenário e mês são independentes.</p>
    <div class="modal-q" data-qid="mes"><div class="ql">Mês de origem</div>
      <input type="month" id="fsFromMonth" value="${esc(pfCurrentMonthKey())}">
      <div class="modal-err">Informe um mês (YYYY-MM).</div></div>
    ${fsScenarioFormHTML(null)}
    <div class="modal-actions">
      <button class="modal-btn" id="modalCancel">Cancelar</button>
      <button class="modal-btn confirm" id="modalConfirm">Confirmar</button>
    </div>`;
  $('modalCancel').addEventListener('click', closeModal);   // cancelar = zero mutação
  $('modalConfirm').addEventListener('click', ()=>{
    box.querySelectorAll('.modal-err').forEach(e=>e.classList.remove('show'));
    let falhou=false;
    const marcar = qid => { box.querySelector(`[data-qid="${qid}"] .modal-err`).classList.add('show'); falhou=true; };
    const mes = $('fsFromMonth').value;
    if(!pfMonthKeyValid(mes)) marcar('mes');
    const dados = fsReadScenarioForm(box, marcar);
    if(falhou) return;
    const r = pfActCreateScenarioFromMonth(mes, dados);
    if(r.ok===false && r.erro){ alert('⛔ '+r.erro); return; }   // bloqueio nomeando as faltas
    closeModal();
    finpesScenariosRender();
  });
}

window.JPWFinScenarios = { render: finpesScenariosRender };

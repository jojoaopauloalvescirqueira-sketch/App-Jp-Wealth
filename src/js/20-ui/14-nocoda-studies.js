// ============ ESTUDOS NOCODA · INTERFACE (N1 — apresentação) ============
// Workspace do Execution Board para a memória técnica do canal NoCoda.
//
// SEPARAÇÃO DE RESPONSABILIDADES, deliberada:
//   · a lista de instrumentos vem de instrumentCatalog() — NUNCA há símbolo
//     escrito aqui, e nenhuma cópia do catálogo entra no estado NoCoda;
//   · toda a matemática vive em 10-domain/09-nocoda-geometry.js, puro e sem
//     DOM; este arquivo só lê entrada, chama o motor e escreve texto;
//   · a persistência é S.nocoda.studies, gravada apenas no clique em salvar.
//
// PRINCÍPIO DE SEGURANÇA OPERACIONAL: nada aqui autoriza operação. Navegar até
// este workspace ou salvar um estudo não altera fase, clearance, risco,
// alavancagem, ordem, LIFO, quarentena ou qualquer estado estatutário.

const NC_ANCHOR_KEYS = ['anchor1', 'anchor2', 'anchor3'];
const NC_EMPTY_ANCHOR = { datetime: '', price: '' };

// Estado EFÊMERO — instrumento em foco e rascunho não salvo. Não entra em S,
// localStorage, backup, schema ou migração.
let ncSelectedId = null;
let ncDraft = null;
let ncDirty = false;

function ncStudies() {
  return (S.nocoda && S.nocoda.studies && typeof S.nocoda.studies === 'object') ? S.nocoda.studies : {};
}

// Rascunho a partir do estudo persistido — ou vazio quando ainda não há estudo.
function ncDraftFrom(instrumentId) {
  const saved = ncStudies()[instrumentId];
  const draft = {};
  NC_ANCHOR_KEYS.forEach(key => {
    const anchor = (saved && saved[key] && typeof saved[key] === 'object') ? saved[key] : NC_EMPTY_ANCHOR;
    draft[key] = {
      datetime: anchor.datetime == null ? '' : String(anchor.datetime),
      price: (anchor.price == null || anchor.price === '') ? '' : String(anchor.price)
    };
  });
  return draft;
}

// Formatação de apresentação. O app não tem formatador de alta precisão nomeado
// e o catálogo não tem metadado de dígitos por instrumento (auditado); em vez de
// inventar uma segunda tabela de precisão só para o NoCoda, usa-se um formatter
// neutro de até 8 casas com zeros à direita removidos. O cálculo interno NUNCA
// depende deste texto.
function ncFormat(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
  const fixed = value.toFixed(8);
  const trimmed = fixed.replace(/0+$/, '').replace(/\.$/, '');
  return (trimmed === '' || trimmed === '-0' ? '0' : trimmed).replace('.', ',');
}

function ncAnchorFieldsHTML(index) {
  const key = NC_ANCHOR_KEYS[index];
  const anchor = ncDraft[key];
  const n = index + 1;
  return `
    <fieldset class="nc-anchor">
      <legend>Âncora ${n}${n === 3 ? ' <span class="art">linha −1</span>' : (n === 1 ? ' <span class="art">linha 0</span>' : '')}</legend>
      <div class="field">
        <label for="ncDate${n}">Data/hora</label>
        <input type="datetime-local" step="1" id="ncDate${n}" data-nc-field="${key}.datetime"
               value="${esc(anchor.datetime)}" aria-describedby="ncErr${n}">
      </div>
      <div class="field">
        <label for="ncPrice${n}">Valor</label>
        <input type="text" inputmode="decimal" id="ncPrice${n}" data-nc-field="${key}.price"
               value="${esc(anchor.price)}" placeholder="ex.: 1,23412" aria-describedby="ncErr${n}">
      </div>
      <p class="nc-field-err" id="ncErr${n}" role="alert"></p>
    </fieldset>`;
}

function renderNocodaStudies() {
  const root = document.getElementById('execNocoda');
  if (!root) return;
  const catalog = (typeof instrumentCatalog === 'function') ? instrumentCatalog() : [];

  if (!catalog.length) {
    root.innerHTML = `<div class="card"><h2>Estudos NoCoda</h2>
      <p class="expl">Nenhum instrumento operável no Motor de Lote. O catálogo é a fonte canônica desta tela.</p></div>`;
    return;
  }

  if (!ncSelectedId || !catalog.some(i => i.id === ncSelectedId)) {
    ncSelectedId = catalog[0].id;
    ncDraft = ncDraftFrom(ncSelectedId);
    ncDirty = false;
  }
  if (!ncDraft) ncDraft = ncDraftFrom(ncSelectedId);

  const saved = ncStudies()[ncSelectedId];
  const options = catalog.map(i =>
    `<option value="${esc(i.id)}"${i.id === ncSelectedId ? ' selected' : ''}>${esc(i.name)}${ncStudies()[i.id] ? ' ·' : ''}</option>`
  ).join('');

  root.innerHTML = `
    <div class="card">
      <h2>Estudos NoCoda <span class="art">memória técnica do canal — não autoriza operação</span></h2>
      <p class="expl">Guarda as três âncoras do Fibo Channel de cada instrumento e deriva o range entre os níveis −1 e 0 e o de cada subdivisão de 0,125. Os instrumentos vêm do Motor de Lote; esta tela não tem catálogo próprio.</p>

      <div class="field nc-picker">
        <label for="ncInstrument">Instrumento</label>
        <select id="ncInstrument">${options}</select>
        <span class="note">O ponto marca instrumentos que já possuem estudo salvo.</span>
      </div>

      <div class="params-grid nc-anchors">
        ${ncAnchorFieldsHTML(0)}${ncAnchorFieldsHTML(1)}${ncAnchorFieldsHTML(2)}
      </div>

      <div class="metrics nc-results">
        <div class="metric">
          <div class="k">Range −1 → 0</div>
          <div class="v sm" id="ncRange">—</div>
          <div class="sub">medido na projeção da linha 0 até a âncora 3</div>
        </div>
        <div class="metric">
          <div class="k">Subdivisão 0,125</div>
          <div class="v sm" id="ncSubdivision">—</div>
          <div class="sub">um oitavo do range do canal</div>
        </div>
      </div>

      <div id="ncFormErr"></div>
      <div class="nc-actions">
        <button class="reset-btn" id="ncSaveBtn">Salvar parâmetros</button>
        <span class="fx-status" id="ncStatus">${saved && saved.updatedAt ? 'salvo em ' + esc(String(saved.updatedAt).slice(0, 16).replace('T', ' ')) : 'nenhum estudo salvo para este instrumento'}</span>
      </div>
    </div>`;

  ncBind(root);
  ncUpdateDerived();
}

function ncBind(root) {
  const select = root.querySelector('#ncInstrument');
  if (select) select.addEventListener('change', () => ncSelectInstrument(select.value, select));

  root.querySelectorAll('[data-nc-field]').forEach(input => {
    input.addEventListener('input', () => {
      const [anchorKey, field] = input.dataset.ncField.split('.');
      ncDraft[anchorKey][field] = input.value;
      ncDirty = true;
      // Calcular não é salvar: a prévia é recalculada a cada tecla, mas nada
      // é persistido antes do clique explícito em salvar.
      ncUpdateDerived();
    });
  });

  const save = root.querySelector('#ncSaveBtn');
  if (save) save.addEventListener('click', ncSaveStudy);
}

function ncSelectInstrument(nextId, selectEl) {
  if (nextId === ncSelectedId) return;
  // Alterações pendentes: o app não tem arquitetura de rascunho, e o padrão
  // dominante de confirmação é confirm() nativo. Basta impedir descarte
  // silencioso — não se introduz um sistema de drafts só para esta tela.
  if (ncDirty && !confirm('Há parâmetros alterados e não salvos neste instrumento. Trocar de instrumento descarta essas alterações. Continuar?')) {
    if (selectEl) selectEl.value = ncSelectedId;
    return;
  }
  ncSelectedId = nextId;
  ncDraft = ncDraftFrom(ncSelectedId);
  ncDirty = false;
  renderNocodaStudies();
}

// Recalcula somente os dois resultados e as mensagens de erro. Não reconstrói o
// formulário: um innerHTML a cada tecla destruiria foco e posição do cursor.
function ncUpdateDerived() {
  const geometry = window.JPWNocoda && window.JPWNocoda.geometry;
  if (!geometry) return;
  const rangeEl = document.getElementById('ncRange');
  const subEl = document.getElementById('ncSubdivision');
  const result = geometry.compute(ncDraft);
  if (rangeEl) rangeEl.textContent = result ? ncFormat(result.channelRange) : '—';
  if (subEl) subEl.textContent = result ? ncFormat(result.subdivisionRange) : '—';
  return result;
}

// Mensagens por campo (aria-invalid + parágrafo role="alert" associado) e
// resumo em bloco — o app só tinha validação em bloco; a associação por campo
// é o que o contrato de acessibilidade desta feature exige.
function ncShowErrors(errors) {
  NC_ANCHOR_KEYS.forEach((key, index) => {
    const messages = errors.filter(e => e.field.startsWith(key)).map(e => e.message);
    const box = document.getElementById('ncErr' + (index + 1));
    if (box) box.textContent = messages.join(' ');
    ['datetime', 'price'].forEach(field => {
      const input = document.querySelector(`[data-nc-field="${key}.${field}"]`);
      if (!input) return;
      const bad = errors.some(e => e.field === key + '.' + field);
      if (bad) input.setAttribute('aria-invalid', 'true');
      else input.removeAttribute('aria-invalid');
    });
  });
  const summary = document.getElementById('ncFormErr');
  if (summary) {
    summary.innerHTML = errors.length
      ? `<div class="nc-err" role="alert">${errors.map(e => esc(e.message)).join('<br>')}</div>`
      : '';
  }
}

function ncSaveStudy() {
  const geometry = window.JPWNocoda && window.JPWNocoda.geometry;
  if (!geometry || !ncSelectedId) return;
  const validation = geometry.validate(ncDraft);
  ncShowErrors(validation.errors || []);
  const status = document.getElementById('ncStatus');
  if (!validation.ok) {
    if (status) { status.className = 'fx-status err'; status.textContent = 'não salvo — corrija os campos indicados'; }
    return;
  }

  // Persiste somente as CAUSAS, já normalizadas. Nenhum derivado é gravado:
  // range, subdivisão e níveis são recalculados a partir das âncoras.
  const values = validation.values;
  if (!S.nocoda || typeof S.nocoda !== 'object') S.nocoda = structuredClone(DEFAULTS.nocoda);
  if (!S.nocoda.studies || typeof S.nocoda.studies !== 'object') S.nocoda.studies = {};
  const previous = S.nocoda.studies[ncSelectedId];
  S.nocoda.studies[ncSelectedId] = Object.assign({}, previous, {
    anchor1: { datetime: ncDraft.anchor1.datetime, price: values.p1 },
    anchor2: { datetime: ncDraft.anchor2.datetime, price: values.p2 },
    anchor3: { datetime: ncDraft.anchor3.datetime, price: values.p3 },
    updatedAt: new Date().toISOString()
  });
  save();

  ncDraft = ncDraftFrom(ncSelectedId);
  ncDirty = false;
  if (status) { status.className = 'fx-status ok'; status.textContent = 'parâmetros salvos'; }
  ncUpdateDerived();
}

// Superfície pública consumida pelo controlador de views do Execution Board.
window.JPWNocodaUI = { render: renderNocodaStudies };

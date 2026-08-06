// ============ LAYOUT PERSONALIZÁVEL DO DASHBOARD (N1) ============
// Funcionalidade nova, isolada, atrás de feature flag própria e
// independente: html[data-custom-layout="enabled"]. Sem ela: nenhum
// listener de personalização, nenhum botão, nenhuma leitura de preferência,
// nenhuma mudança visual — cada função pública começa com um guard-clause
// que sai cedo se a flag não estiver presente.
//
// Não toca compute(), getOperationalClearance(), nenhum cálculo ou
// persistência financeira — só ORDEM, ZONA (coluna) e TAMANHO discreto de
// cards já existentes, identificados por data-layout-card (nenhum ID
// interno de renderizador muda, nenhum nó é clonado, só movido).
//
// Depende de #gdDashMain/#gdDashSide já existirem no DOM final (após
// relocateGlobalDashboardShell(), 12-global-dashboard.js, ordem 39) — por
// isso este arquivo é ordem 40 no manifest, carregado depois.

/* ======================= CONSTANTES E POLÍTICA ======================= */

const DASH_LAYOUT_STORAGE_KEY_V2 = 'jpwealth.ui.widgetLayout.v2';
const DASH_LAYOUT_STORAGE_KEY_V1 = 'jpwealth.ui.dashboardLayout.v1'; // só para migração — nunca gravado de novo

const DASH_LAYOUT_LABELS = {
  'operational-clearance': 'Operational Clearance',
  'institutional-panel': 'Painel institucional',
  'metric-strip': 'A faixa de métricas principais',
  'thermometers': 'Termômetros',
  'leverage-coherence': 'Coerência de Alavancagem',
  'vrm': 'VRM · Regime de Volatilidade',
  'posture': 'Postura e conformidade',
  'profile-context': 'Perfil e Contexto',
  'onboarding-alert': 'Alerta de onboarding',
  'quick-actions': 'Ações Rápidas'
};
const DASH_WIDGET_SIZE_LABELS = { compact: 'Compacto', medium: 'Médio', large: 'Grande', full: 'Largura total' };
const DASH_LAYOUT_SIZE_VALUES = ['compact', 'medium', 'large', 'full'];

// Tamanho padrão por widget — usado no layout padrão e na migração de
// preferências v1 (que não tinham tamanho). Fonte única desta lista
// específica; zonas e tamanhos PERMITIDOS continuam vindo só do HTML
// (data-layout-allowed-zones / data-widget-allowed-sizes), nunca duplicados
// aqui — isto é só o valor inicial.
const DASH_WIDGET_DEFAULT_SIZE = {
  'operational-clearance': 'large',
  'institutional-panel': 'large',
  'metric-strip': 'full',
  'thermometers': 'compact',
  'leverage-coherence': 'medium',
  'vrm': 'compact',
  'posture': 'full',
  'profile-context': 'medium',
  'onboarding-alert': 'full',
  'quick-actions': 'medium'
};

function dashLayoutDeepFreeze(obj) {
  Object.getOwnPropertyNames(obj).forEach(key => {
    const val = obj[key];
    if (val && typeof val === 'object' && !Object.isFrozen(val)) dashLayoutDeepFreeze(val);
  });
  return Object.freeze(obj);
}

// Layout padrão — constante explícita e profundamente imutável (objeto
// externo, objeto da tela, array de widgets e cada widget individual, todos
// congelados). Nunca derivada do DOM; nenhuma função usa isto como estado de
// trabalho — dashLayoutApply() sempre lê valores, nunca escreve nele.
const DASH_LAYOUT_DEFAULT = dashLayoutDeepFreeze({
  version: 2,
  screens: {
    dashboard: {
      widgets: [
        { id: 'operational-clearance', zone: 'main', size: 'large', order: 0 },
        { id: 'institutional-panel', zone: 'main', size: 'large', order: 1 },
        { id: 'metric-strip', zone: 'main', size: 'full', order: 2 },
        { id: 'thermometers', zone: 'main', size: 'compact', order: 3 },
        { id: 'leverage-coherence', zone: 'main', size: 'medium', order: 4 },
        { id: 'vrm', zone: 'main', size: 'compact', order: 5 },
        { id: 'posture', zone: 'main', size: 'full', order: 6 },
        { id: 'profile-context', zone: 'sidebar', size: 'medium', order: 7 },
        { id: 'onboarding-alert', zone: 'sidebar', size: 'full', order: 8 },
        { id: 'quick-actions', zone: 'sidebar', size: 'medium', order: 9 }
      ]
    }
  }
});
const DASH_LAYOUT_ALL_IDS = DASH_LAYOUT_DEFAULT.screens.dashboard.widgets.map(w => w.id);

const DASH_LAYOUT_HANDLE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><circle cx="9" cy="6" r="1.5"/><circle cx="15" cy="6" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="18" r="1.5"/><circle cx="15" cy="18" r="1.5"/></svg>';

function dashLayoutEnabled() {
  // A grade personalizável só existe estruturalmente sob o shell global
  // (é onde #gdDashMain/#gdDashSide existem) — checar as duas flags evita
  // um estado inválido caso algum dia sejam ativadas independentemente.
  return document.documentElement.dataset.customLayout === 'enabled' && document.documentElement.dataset.shell === 'global-dashboard';
}

function dashLayoutCardEl(id) {
  return document.querySelector('#dash [data-layout-card="' + id + '"]');
}

// Fonte única da política de zonas permitidas: o atributo
// data-layout-allowed-zones no próprio card (index.html). Fonte única dos
// tamanhos permitidos: data-widget-allowed-sizes, mesmo padrão. Toda
// checagem — arraste, menu, validação de preferência salva — passa por
// estas duas funções; nada duplica a política em uma segunda lista JS.
function dashLayoutZonesFor(card) {
  const raw = card && card.dataset.layoutAllowedZones;
  return raw ? raw.trim().split(/\s+/) : [];
}
function dashLayoutZonesForId(id) { return dashLayoutZonesFor(dashLayoutCardEl(id)); }
function dashLayoutZoneLabel(zones) {
  if (zones.length === 1 && zones[0] === 'main') return 'coluna principal';
  if (zones.length === 1 && zones[0] === 'sidebar') return 'coluna lateral';
  return null;
}
function dashLayoutSizesFor(card) {
  const raw = card && card.dataset.widgetAllowedSizes;
  return raw ? raw.trim().split(/\s+/) : [];
}
function dashLayoutSizesForId(id) { return dashLayoutSizesFor(dashLayoutCardEl(id)); }

/* ======================= VALIDAÇÃO E PERSISTÊNCIA ======================= */

function dashLayoutValidateV2(pref) {
  if (!pref || typeof pref !== 'object') return null;
  if (pref.version !== 2) return null;
  const widgets = pref.screens && pref.screens.dashboard && pref.screens.dashboard.widgets;
  if (!Array.isArray(widgets) || widgets.length !== DASH_LAYOUT_ALL_IDS.length) return null;
  const seen = new Set();
  for (const w of widgets) {
    if (!w || typeof w !== 'object') return null;
    const { id, zone, size, order } = w;
    if (typeof id !== 'string' || !DASH_LAYOUT_ALL_IDS.includes(id)) return null; // id desconhecido
    if (seen.has(id)) return null; // duplicado
    seen.add(id);
    if (zone !== 'main' && zone !== 'sidebar') return null;
    if (!dashLayoutZonesForId(id).includes(zone)) return null; // zona proibida — rejeita o payload inteiro
    if (typeof size !== 'string' || !DASH_LAYOUT_SIZE_VALUES.includes(size)) return null; // tamanho desconhecido
    if (!dashLayoutSizesForId(id).includes(size)) return null; // tamanho proibido para este widget
    if (typeof order !== 'number' || !Number.isFinite(order)) return null;
  }
  for (const id of DASH_LAYOUT_ALL_IDS) { if (!seen.has(id)) return null; } // obrigatório ausente
  // normaliza — devolve cópia limpa, nunca a referência recebida, ordenada por 'order'
  const clean = widgets.slice().sort((a, b) => a.order - b.order).map((w, i) => ({ id: w.id, zone: w.zone, size: w.size, order: i }));
  return { version: 2, screens: { dashboard: { widgets: clean } } };
}

// Validação da preferência v1 (ordem + zona, sem tamanho) — só existe para
// permitir a migração; nunca é gravada de novo nessa forma.
function dashLayoutValidateV1(pref) {
  if (!pref || typeof pref !== 'object') return null;
  if (pref.version !== 1) return null;
  const d = pref.dashboard;
  if (!d || !Array.isArray(d.main) || !Array.isArray(d.sidebar)) return null;
  const combined = [...d.main, ...d.sidebar];
  if (combined.length !== DASH_LAYOUT_ALL_IDS.length) return null;
  const seen = new Set();
  for (const id of combined) {
    if (typeof id !== 'string' || !DASH_LAYOUT_ALL_IDS.includes(id)) return null;
    if (seen.has(id)) return null;
    seen.add(id);
  }
  for (const id of DASH_LAYOUT_ALL_IDS) { if (!seen.has(id)) return null; }
  for (const id of d.main) { if (!dashLayoutZonesForId(id).includes('main')) return null; }
  for (const id of d.sidebar) { if (!dashLayoutZonesForId(id).includes('sidebar')) return null; }
  return { version: 1, dashboard: { main: [...d.main], sidebar: [...d.sidebar] } };
}

// Migração v1 → v2: preserva ordem e zona válidas, aplica tamanho padrão por
// widget, valida o resultado antes de aceitar. Nunca corrige parcialmente —
// se o resultado migrado não passar em dashLayoutValidateV2, a migração
// falhou por inteiro e quem chamou usa o padrão.
function dashLayoutMigrateV1(v1) {
  let order = 0;
  const widgets = [];
  v1.dashboard.main.forEach(id => widgets.push({ id, zone: 'main', size: DASH_WIDGET_DEFAULT_SIZE[id], order: order++ }));
  v1.dashboard.sidebar.forEach(id => widgets.push({ id, zone: 'sidebar', size: DASH_WIDGET_DEFAULT_SIZE[id], order: order++ }));
  return dashLayoutValidateV2({ version: 2, screens: { dashboard: { widgets } } });
}

function dashLayoutLoad() {
  try {
    const rawV2 = localStorage.getItem(DASH_LAYOUT_STORAGE_KEY_V2);
    if (rawV2) return dashLayoutValidateV2(JSON.parse(rawV2)); // presente mas inválida → null, não cai para v1
    const rawV1 = localStorage.getItem(DASH_LAYOUT_STORAGE_KEY_V1);
    if (rawV1) {
      const v1 = dashLayoutValidateV1(JSON.parse(rawV1));
      if (v1) {
        const migrated = dashLayoutMigrateV1(v1);
        if (migrated) {
          // promove para v2 (não descarta a preferência antiga silenciosamente) —
          // só grava depois de validado.
          try { localStorage.setItem(DASH_LAYOUT_STORAGE_KEY_V2, JSON.stringify(migrated)); } catch (_) { /* segue só em memória */ }
          return migrated;
        }
      }
    }
  } catch (_) { /* JSON malformado etc. — cai no padrão */ }
  return null;
}

function dashLayoutSave(pref) {
  const valid = dashLayoutValidateV2(pref);
  if (!valid) return false;
  try { localStorage.setItem(DASH_LAYOUT_STORAGE_KEY_V2, JSON.stringify(valid)); } catch (_) { return false; }
  return true;
}

function dashLayoutClearPreference() {
  // Limpa as duas chaves: se só a v1 fosse apagada, uma v2 inválida deixada
  // para trás continuaria bloqueando o padrão; se só a v2, a v1 ressuscitaria
  // no próximo boot via migração. As duas são "a preferência visual" — nada
  // financeiro ou operacional é tocado.
  try { localStorage.removeItem(DASH_LAYOUT_STORAGE_KEY_V2); } catch (_) { /* silencioso */ }
  try { localStorage.removeItem(DASH_LAYOUT_STORAGE_KEY_V1); } catch (_) { /* silencioso */ }
}

function dashLayoutApply(pref) {
  const main = document.getElementById('gdDashMain'), side = document.getElementById('gdDashSide');
  if (!main || !side) return;
  const widgets = pref.screens.dashboard.widgets.slice().sort((a, b) => a.order - b.order);
  widgets.forEach(w => {
    const el = dashLayoutCardEl(w.id);
    if (!el) return;
    el.dataset.widgetSize = w.size;
    (w.zone === 'main' ? main : side).appendChild(el);
  });
}

function dashLayoutCurrentState() {
  const main = document.getElementById('gdDashMain'), side = document.getElementById('gdDashSide');
  const widgets = [];
  let order = 0;
  [[main, 'main'], [side, 'sidebar']].forEach(([root, zone]) => {
    if (!root) return;
    [...root.querySelectorAll(':scope > [data-layout-card]')].forEach(el => {
      widgets.push({ id: el.dataset.layoutCard, zone, size: el.dataset.widgetSize, order: order++ });
    });
  });
  return { version: 2, screens: { dashboard: { widgets } } };
}

function dashLayoutBoot() {
  if (!dashLayoutEnabled()) return;
  const saved = dashLayoutLoad();
  if (saved) dashLayoutApply(saved);
  // preferência ausente ou inválida: a ordem/tamanho já presentes no DOM
  // (index.html, idênticos a DASH_LAYOUT_DEFAULT) são o padrão — nada a fazer.
}

/* ======================= CAMADA GLOBAL DE POPOVERS ======================= */
// Norma registrada em app.css ("NORMA DE POPOVERS"): nenhum popover vive
// dentro de um card animado/transformado. Todo popover nasce em
// #jpPopoverLayer, position:fixed, posicionado por getBoundingClientRect().

const dashLayoutState = { editing: false, snapshot: null, drag: null, openPopover: null };

function dashLayoutPopoverLayer() { return document.getElementById('jpPopoverLayer'); }

function dashLayoutPositionPopover(el, anchor) {
  const margin = 8;
  const r = anchor.getBoundingClientRect();
  const pw = el.offsetWidth, ph = el.offsetHeight;
  // preferência: abaixo e alinhado à direita do botão
  let left = r.right - pw;
  let top = r.bottom + margin;
  if (left < margin) left = margin;
  if (left + pw > window.innerWidth - margin) left = Math.max(margin, window.innerWidth - margin - pw);
  if (top + ph > window.innerHeight - margin) {
    const above = r.top - margin - ph;
    top = above >= margin ? above : Math.max(margin, window.innerHeight - margin - ph);
  }
  el.style.left = left + 'px';
  el.style.top = top + 'px';
}

function dashLayoutClosePopover(opts) {
  const p = dashLayoutState.openPopover;
  if (!p) return;
  p.el.remove();
  dashLayoutState.openPopover = null;
  window.removeEventListener('resize', dashLayoutRepositionPopover);
  window.removeEventListener('scroll', dashLayoutRepositionPopover, true);
  if (p.anchor) { p.anchor.setAttribute('aria-expanded', 'false'); p.anchor.removeAttribute('aria-controls'); }
  if (opts && opts.returnFocus && p.anchor && document.contains(p.anchor)) p.anchor.focus();
}

function dashLayoutRepositionPopover() {
  const p = dashLayoutState.openPopover; if (!p) return;
  if (!document.contains(p.anchor)) { dashLayoutClosePopover(); return; }
  dashLayoutPositionPopover(p.el, p.anchor);
}

function dashLayoutOpenCardMenu(card, anchorBtn) {
  if (dashLayoutState.openPopover && dashLayoutState.openPopover.card === card) { dashLayoutClosePopover({ returnFocus: false }); return; }
  dashLayoutClosePopover({ returnFocus: false }); // só uma instância aberta por vez

  const parent = card.parentElement;
  const inMain = parent && parent.id === 'gdDashMain';
  const allowedZones = dashLayoutZonesFor(card);
  const items = [];
  if (card.previousElementSibling && card.previousElementSibling.hasAttribute('data-layout-card')) items.push(['up', 'Mover para cima']);
  if (card.nextElementSibling && card.nextElementSibling.hasAttribute('data-layout-card')) items.push(['down', 'Mover para baixo']);
  if (!inMain && allowedZones.includes('main')) items.push(['zone-main', 'Mover para coluna principal']);
  if (inMain && allowedZones.includes('sidebar')) items.push(['zone-sidebar', 'Mover para coluna lateral']);

  const sizes = dashLayoutSizesFor(card);
  const currentSize = card.dataset.widgetSize;
  const cardLabel = DASH_LAYOUT_LABELS[card.dataset.layoutCard] || card.dataset.layoutCard;

  const el = document.createElement('div');
  el.className = 'jp-popover dash-layout-card-menu';
  el.id = 'jpPopoverActive';
  el.setAttribute('role', 'menu');
  el.setAttribute('aria-label', 'Opções — ' + cardLabel);

  let html = items.map(([action, label]) => '<button type="button" role="menuitem" data-action="' + action + '">' + label + '</button>').join('');
  if (items.length && sizes.length) html += '<div class="dash-layout-menu-sep" role="separator"></div>';
  if (sizes.length) {
    html += '<div class="dash-layout-menu-heading" id="dashLayoutSizeHeading-' + card.dataset.layoutCard + '">Tamanho</div>';
    html += '<div role="group" aria-labelledby="dashLayoutSizeHeading-' + card.dataset.layoutCard + '">' +
      sizes.map(s => '<button type="button" role="menuitemradio" aria-checked="' + (s === currentSize ? 'true' : 'false') + '" data-size="' + s + '"><span>' + DASH_WIDGET_SIZE_LABELS[s] + '</span><span class="dash-layout-check" aria-hidden="true">✓</span></button>').join('') +
      '</div>';
  }
  el.innerHTML = html;

  el.addEventListener('click', event => {
    const btn = event.target.closest('button[data-action], button[data-size]');
    if (!btn) return;
    if (btn.dataset.action === 'up') { const p = card.previousElementSibling; if (p) p.before(card); dashLayoutRefreshAllLabels(); dashLayoutAnnounce(cardLabel + ' movido. ' + card.getAttribute('aria-label')); }
    else if (btn.dataset.action === 'down') { const n = card.nextElementSibling; if (n) n.after(card); dashLayoutRefreshAllLabels(); dashLayoutAnnounce(cardLabel + ' movido. ' + card.getAttribute('aria-label')); }
    else if (btn.dataset.action === 'zone-main') { document.getElementById('gdDashMain').append(card); dashLayoutRefreshAllLabels(); dashLayoutAnnounce(cardLabel + ' movido. ' + card.getAttribute('aria-label')); }
    else if (btn.dataset.action === 'zone-sidebar') { document.getElementById('gdDashSide').append(card); dashLayoutRefreshAllLabels(); dashLayoutAnnounce(cardLabel + ' movido. ' + card.getAttribute('aria-label')); }
    else if (btn.dataset.size) { dashLayoutChangeSize(card, btn.dataset.size, cardLabel); }
    dashLayoutClosePopover({ returnFocus: false });
    card.focus();
  });

  dashLayoutPopoverLayer().appendChild(el);
  dashLayoutPositionPopover(el, anchorBtn);
  dashLayoutState.openPopover = { el, card, anchor: anchorBtn };
  anchorBtn.setAttribute('aria-expanded', 'true');
  anchorBtn.setAttribute('aria-controls', 'jpPopoverActive');
  window.addEventListener('resize', dashLayoutRepositionPopover);
  window.addEventListener('scroll', dashLayoutRepositionPopover, true);
  const first = el.querySelector('button'); if (first) first.focus();
}

function dashLayoutChangeSize(card, size, cardLabel) {
  if (card.dataset.widgetSize === size) return;
  card.dataset.widgetSize = size;
  dashLayoutAnnounce((cardLabel || DASH_LAYOUT_LABELS[card.dataset.layoutCard] || card.dataset.layoutCard) + ' alterado para tamanho ' + DASH_WIDGET_SIZE_LABELS[size].toLowerCase() + '.');
  // Não salva agora — só ao clicar Concluir (dashLayoutFinish lê o DOM atual).
}

/* ======================= UI DO MODO DE EDIÇÃO ======================= */

function dashLayoutAnnounce(msg) {
  const el = document.getElementById('dashLayoutAnnounce');
  if (el) el.textContent = msg;
}

function dashLayoutAllCardEls() {
  return [...document.querySelectorAll('#dash [data-layout-card]')];
}

function dashLayoutDecorateCard(card) {
  if (card.querySelector(':scope > .dash-layout-handle')) return; // já decorado
  const cardLabel = DASH_LAYOUT_LABELS[card.dataset.layoutCard] || card.dataset.layoutCard;
  const handle = document.createElement('button');
  handle.type = 'button';
  handle.className = 'dash-layout-handle';
  handle.setAttribute('aria-label', 'Arrastar para reposicionar — ' + cardLabel);
  handle.innerHTML = DASH_LAYOUT_HANDLE_SVG;
  const menuBtn = document.createElement('button');
  menuBtn.type = 'button';
  menuBtn.className = 'dash-layout-menu-btn';
  menuBtn.setAttribute('aria-label', 'Mais opções — ' + cardLabel);
  menuBtn.setAttribute('aria-haspopup', 'menu');
  menuBtn.setAttribute('aria-expanded', 'false');
  menuBtn.textContent = '⋮';
  card.append(handle, menuBtn);
  card.tabIndex = 0;
  card.setAttribute('role', 'group');
  dashLayoutUpdateCardLabel(card);
  handle.addEventListener('pointerdown', event => dashLayoutStartDrag(event, card, handle));
  menuBtn.addEventListener('click', event => { event.stopPropagation(); dashLayoutOpenCardMenu(card, menuBtn); });
}

function dashLayoutUndecorateCard(card) {
  card.querySelectorAll(':scope > .dash-layout-handle, :scope > .dash-layout-menu-btn').forEach(el => el.remove());
  card.removeAttribute('tabindex');
  card.removeAttribute('role');
  card.removeAttribute('aria-label');
}

function dashLayoutUpdateCardLabel(card) {
  const parent = card.parentElement;
  const isMain = parent && parent.id === 'gdDashMain';
  const siblings = parent ? [...parent.querySelectorAll(':scope > [data-layout-card]')] : [];
  const pos = siblings.indexOf(card) + 1;
  const label = DASH_LAYOUT_LABELS[card.dataset.layoutCard] || card.dataset.layoutCard;
  const sizeLabel = DASH_WIDGET_SIZE_LABELS[card.dataset.widgetSize] || card.dataset.widgetSize;
  card.setAttribute('aria-label', label + ', tamanho ' + sizeLabel.toLowerCase() + ', posição ' + pos + ' de ' + siblings.length + ', coluna ' + (isMain ? 'principal' : 'lateral'));
}

function dashLayoutRefreshAllLabels() {
  dashLayoutAllCardEls().forEach(dashLayoutUpdateCardLabel);
}

function dashLayoutEnterEdit() {
  if (!dashLayoutEnabled() || dashLayoutState.editing) return;
  dashLayoutState.editing = true;
  dashLayoutState.snapshot = dashLayoutCurrentState();
  document.documentElement.dataset.layoutEditing = 'true';
  dashLayoutAllCardEls().forEach(dashLayoutDecorateCard);
  const bar = document.getElementById('dashLayoutBar');
  if (bar) bar.hidden = false;
  dashLayoutAnnounce('Modo de personalização do Dashboard ativado. Use a alça para arrastar ou o menu de cada card para mover e redimensionar por teclado.');
}

function dashLayoutExitEdit() {
  dashLayoutClosePopover({ returnFocus: false });
  dashLayoutState.editing = false;
  dashLayoutState.snapshot = null;
  delete document.documentElement.dataset.layoutEditing;
  dashLayoutAllCardEls().forEach(dashLayoutUndecorateCard);
  const bar = document.getElementById('dashLayoutBar');
  if (bar) bar.hidden = true;
}

function dashLayoutCancel() {
  if (!dashLayoutState.editing) return;
  if (dashLayoutState.drag) dashLayoutCancelDrag();
  if (dashLayoutState.snapshot) dashLayoutApply(dashLayoutState.snapshot); // ordem + zona + tamanho, os três
  dashLayoutExitEdit();
  dashLayoutAnnounce('Alterações de layout canceladas.');
}

function dashLayoutFinish() {
  if (!dashLayoutState.editing) return;
  if (dashLayoutState.drag) dashLayoutCancelDrag();
  const current = dashLayoutCurrentState();
  if (!dashLayoutSave(current)) {
    dashLayoutApply(DASH_LAYOUT_DEFAULT);
    dashLayoutExitEdit();
    dashLayoutAnnounce('Layout inválido — não foi possível salvar. O Dashboard voltou ao layout padrão.');
    return;
  }
  dashLayoutExitEdit();
  dashLayoutAnnounce('Layout do Dashboard salvo.');
}

function dashLayoutRestoreDefaultConfirm() {
  if (!confirm('Restaurar o layout padrão do Dashboard? Isso apaga só a preferência de posição e tamanho dos cards — nenhum dado financeiro é afetado.')) return;
  dashLayoutClearPreference();
  dashLayoutApply(DASH_LAYOUT_DEFAULT);
  if (dashLayoutState.editing) {
    dashLayoutState.snapshot = dashLayoutCurrentState();
    dashLayoutRefreshAllLabels();
  }
  dashLayoutAnnounce('Layout padrão do Dashboard restaurado.');
}

/* ======================= ARRASTE (Pointer Events) ======================= */

function dashLayoutStartDrag(event, card, handle) {
  if (!dashLayoutState.editing || dashLayoutState.drag) return;
  event.preventDefault();
  dashLayoutClosePopover({ returnFocus: false });
  const rect = card.getBoundingClientRect();
  const originMarker = document.createComment('dash-layout-origin');
  card.parentElement.insertBefore(originMarker, card);
  const placeholder = document.createElement('div');
  placeholder.className = 'dash-layout-placeholder';
  placeholder.dataset.widgetSize = card.dataset.widgetSize; // mesma área de grade do card real
  card.after(placeholder);
  document.body.appendChild(card);
  card.classList.add('dash-layout-dragging');
  Object.assign(card.style, { left: rect.left + 'px', top: rect.top + 'px', width: rect.width + 'px', height: rect.height + 'px' });

  dashLayoutState.drag = {
    card, placeholder, originMarker,
    pointerId: event.pointerId,
    startX: event.clientX, startY: event.clientY,
    originLeft: rect.left, originTop: rect.top,
    allowedZones: dashLayoutZonesFor(card),
    deniedZone: null, lastAnnouncedDenied: null
  };
  try { handle.setPointerCapture(event.pointerId); } catch (_) { /* alguns navegadores móveis recusam — segue sem captura */ }
  document.addEventListener('pointermove', dashLayoutOnDragMove);
  document.addEventListener('pointerup', dashLayoutOnDragEnd);
  document.addEventListener('pointercancel', dashLayoutOnDragCancelEvt);
  handle.addEventListener('lostpointercapture', dashLayoutOnLostCapture);
  document.addEventListener('keydown', dashLayoutOnDragKeydown, true);
}

function dashLayoutOnDragMove(event) {
  const d = dashLayoutState.drag; if (!d) return;
  const dx = event.clientX - d.startX, dy = event.clientY - d.startY;
  d.card.style.left = (d.originLeft + dx) + 'px';
  d.card.style.top = (d.originTop + dy) + 'px';
  dashLayoutUpdatePlaceholderPosition(event.clientX, event.clientY);
}

function dashLayoutUpdatePlaceholderPosition(x, y) {
  const d = dashLayoutState.drag; if (!d) return;
  const main = document.getElementById('gdDashMain'), side = document.getElementById('gdDashSide');
  const mainRect = main.getBoundingClientRect(), sideRect = side.getBoundingClientRect();
  const overSide = x >= sideRect.left - 20 && x <= sideRect.right + 20 && y >= sideRect.top - 40 && y <= sideRect.bottom + 40;
  const hoverContainer = overSide ? side : main;
  const hoverZone = hoverContainer === main ? 'main' : 'sidebar';
  const zoneOk = d.allowedZones.includes(hoverZone);

  main.classList.toggle('dash-layout-dropzone-active', zoneOk && hoverContainer === main);
  side.classList.toggle('dash-layout-dropzone-active', zoneOk && hoverContainer === side);
  main.classList.toggle('dash-layout-dropzone-denied', !zoneOk && hoverContainer === main);
  side.classList.toggle('dash-layout-dropzone-denied', !zoneOk && hoverContainer === side);
  d.card.classList.toggle('dash-layout-denied', !zoneOk);

  if (!zoneOk) {
    d.deniedZone = hoverZone;
    if (d.lastAnnouncedDenied !== hoverZone) {
      d.lastAnnouncedDenied = hoverZone;
      const label = DASH_LAYOUT_LABELS[d.card.dataset.layoutCard] || d.card.dataset.layoutCard;
      const targetLabel = dashLayoutZoneLabel(d.allowedZones) || 'sua coluna permitida';
      dashLayoutAnnounce(label + ' deve permanecer na ' + targetLabel + '.');
    }
    return; // não move o placeholder — ele fica na última posição válida
  }
  d.deniedZone = null; d.lastAnnouncedDenied = null;
  const container = hoverContainer;

  const cards = [...container.querySelectorAll(':scope > [data-layout-card]')];
  let closest = null, closestDist = Infinity, insertBefore = true;
  cards.forEach(c => {
    const r = c.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const dist = Math.hypot(x - cx, y - cy);
    if (dist < closestDist) { closestDist = dist; closest = c; insertBefore = (y < cy) || (Math.abs(y - cy) < r.height / 2 && x < cx); }
  });
  if (!closest) container.appendChild(d.placeholder);
  else if (insertBefore) closest.before(d.placeholder);
  else closest.after(d.placeholder);
}

function dashLayoutEndDragCleanupListeners() {
  document.removeEventListener('pointermove', dashLayoutOnDragMove);
  document.removeEventListener('pointerup', dashLayoutOnDragEnd);
  document.removeEventListener('pointercancel', dashLayoutOnDragCancelEvt);
  document.removeEventListener('keydown', dashLayoutOnDragKeydown, true);
  const main = document.getElementById('gdDashMain'), side = document.getElementById('gdDashSide');
  if (main) main.classList.remove('dash-layout-dropzone-active', 'dash-layout-dropzone-denied');
  if (side) side.classList.remove('dash-layout-dropzone-active', 'dash-layout-dropzone-denied');
}

function dashLayoutOnDragEnd() {
  const d = dashLayoutState.drag; if (!d) return;
  d.placeholder.replaceWith(d.card);
  d.originMarker.remove();
  d.card.classList.remove('dash-layout-dragging', 'dash-layout-denied');
  d.card.style.position = ''; d.card.style.left = ''; d.card.style.top = ''; d.card.style.width = ''; d.card.style.height = '';
  dashLayoutEndDragCleanupListeners();
  dashLayoutState.drag = null;
  dashLayoutRefreshAllLabels();
  dashLayoutAnnounce((DASH_LAYOUT_LABELS[d.card.dataset.layoutCard] || d.card.dataset.layoutCard) + ' reposicionado. ' + d.card.getAttribute('aria-label'));
}

function dashLayoutCancelDrag() {
  const d = dashLayoutState.drag; if (!d) return;
  d.originMarker.parentNode.insertBefore(d.card, d.originMarker);
  d.originMarker.remove();
  d.placeholder.remove();
  d.card.classList.remove('dash-layout-dragging', 'dash-layout-denied');
  d.card.style.position = ''; d.card.style.left = ''; d.card.style.top = ''; d.card.style.width = ''; d.card.style.height = '';
  dashLayoutEndDragCleanupListeners();
  dashLayoutState.drag = null;
}

function dashLayoutOnDragCancelEvt() { dashLayoutCancelDrag(); dashLayoutAnnounce('Arraste cancelado.'); }
function dashLayoutOnLostCapture() { if (dashLayoutState.drag) { dashLayoutCancelDrag(); dashLayoutAnnounce('Arraste cancelado.'); } }
function dashLayoutOnDragKeydown(event) {
  if (event.key === 'Escape' && dashLayoutState.drag) {
    event.preventDefault(); event.stopPropagation();
    dashLayoutCancelDrag();
    dashLayoutAnnounce('Arraste cancelado.');
  }
}

/* ======================= LIGAÇÕES ======================= */

function initDashboardLayout() {
  dashLayoutBoot();

  const customizeBtn = document.getElementById('dashLayoutCustomizeBtn');
  if (customizeBtn) customizeBtn.addEventListener('click', () => {
    if (!dashLayoutEnabled()) return;
    if (typeof closeSettingsModal === 'function') closeSettingsModal();
    if (typeof navigateToScreen === 'function') navigateToScreen('dash');
    dashLayoutEnterEdit();
  });
  const settingsResetBtn = document.getElementById('dashLayoutResetBtn');
  if (settingsResetBtn) settingsResetBtn.addEventListener('click', () => { if (dashLayoutEnabled()) dashLayoutRestoreDefaultConfirm(); });

  const cancelBtn = document.getElementById('dashLayoutCancelBtn');
  if (cancelBtn) cancelBtn.addEventListener('click', dashLayoutCancel);
  const restoreBtn = document.getElementById('dashLayoutRestoreBtn');
  if (restoreBtn) restoreBtn.addEventListener('click', dashLayoutRestoreDefaultConfirm);
  const doneBtn = document.getElementById('dashLayoutDoneBtn');
  if (doneBtn) doneBtn.addEventListener('click', dashLayoutFinish);

  // Fechar popover: clique fora, Escape (fora de um arraste — Escape durante
  // arraste é tratado em dashLayoutOnDragKeydown, que cancela o arraste).
  document.addEventListener('click', event => {
    if (!dashLayoutState.openPopover) return;
    if (event.target.closest('.jp-popover') || event.target.closest('.dash-layout-menu-btn')) return;
    dashLayoutClosePopover();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && dashLayoutState.openPopover && !dashLayoutState.drag) { dashLayoutClosePopover({ returnFocus: true }); }
  });

  // Fechar popover ao trocar de tela — mesmo padrão de wrap-guardado já
  // usado por 10-dashboard-immersive.js (não substitui a função, envolve).
  if (typeof navigateToScreen === 'function' && !navigateToScreen.__layoutWrapped) {
    const original = navigateToScreen;
    navigateToScreen = function (target) {
      dashLayoutClosePopover({ returnFocus: false });
      original(target);
    };
    navigateToScreen.__layoutWrapped = true;
  }
}
initDashboardLayout();

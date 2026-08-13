// ============ MOTOR COMPARTILHADO DE PERSONALIZAÇÃO DE TELAS (N1) ============
// Funcionalidade nova, isolada, atrás de feature flag própria e
// independente: html[data-custom-layout="enabled"]. Sem ela: nenhum
// listener de personalização, nenhum botão, nenhuma leitura de preferência,
// nenhuma mudança visual — cada função pública começa com um guard-clause
// que sai cedo se a flag não estiver presente.
//
// Não toca compute(), getOperationalClearance(), nenhum cálculo ou
// persistência financeira — só ORDEM, ZONA (coluna) e TAMANHO discreto de
// widgets já existentes, identificados por data-layout-card (nenhum ID
// interno de renderizador muda, nenhum nó é clonado, só movido).
//
// Um único motor para todas as telas registradas — não há implementação
// duplicada por tela. O registro abaixo (JP_WIDGET_SCREENS) é só estrutural
// (tela → contêineres → zonas); a política de cada widget (zonas
// permitidas, tamanhos permitidos, se pode mover) continua vindo
// exclusivamente dos atributos no próprio elemento HTML
// (data-layout-allowed-zones / data-widget-allowed-sizes /
// data-layout-movable) — a mesma fonte única já usada no Dashboard, nunca
// duplicada num array JS paralelo.
//
// Depende de todos os *WidgetGrid existirem no DOM final — por isso este
// arquivo é ordem 40 no manifest, carregado depois de
// 12-global-dashboard.js (ordem 39).

/* ======================= REGISTRO ESTRUTURAL ======================= */

// Parâmetros, Motor de Lote e Checklist saíram deste registro quando
// migraram da navegação superior para dentro da Central de Configurações
// (grupo "Operação") — dentro de um modal não existe sessão de edição de
// layout. Preferências v3 salvas para telas fora do registro são
// simplesmente ignoradas pela normalização (itera JP_WIDGET_SCREEN_IDS).
const JP_WIDGET_SCREENS = {
  dash: { label: 'Dashboard', zones: ['main'], main: 'gdDashMain', sidebar: null },
  exec: { label: 'Execution Board', zones: ['main'], main: 'execWidgetGrid', sidebar: null },
  contas: { label: 'Contas', zones: ['main'], main: 'contasWidgetGrid', sidebar: null },
  contab: { label: 'Contabilidade', zones: ['main'], main: 'contabWidgetGrid', sidebar: null }
};
const JP_WIDGET_SCREEN_IDS = Object.keys(JP_WIDGET_SCREENS);

const DASH_LAYOUT_LABELS = {
  'operational-clearance': 'Operational Clearance', 'institutional-panel': 'Status do Sistema',
  'vrm': 'VRM · Regime de Volatilidade',
  'onboarding-alert': 'Alerta de onboarding', 'quick-actions': 'Ações Rápidas',
  'exec-clearance': 'Execution Clearance',
  'exec-metrics-banners': 'Métricas e avisos',
  'exec-vrm': 'VRM com ATR editável', 'exec-phase-grids': 'Grades da Operação Única',
  'exec-lifo-monitor': 'Consolidado LIFO',
  'contas-accounts-table': 'Parque de Contas',
  'contas-order-application': 'Aplicação de Ordem',
  'contab-period-goals': 'Período & Metas', 'contab-daily-close': 'Fechamento Diário',
  'contab-real-vs-projected': 'Real vs Projetado', 'contab-entries': 'Lançamentos'
};
const DASH_WIDGET_SIZE_LABELS = { compact: 'Compacto', medium: 'Médio', large: 'Grande', full: 'Largura total' };
const DASH_LAYOUT_SIZE_VALUES = ['compact', 'medium', 'large', 'full'];
const DASH_LAYOUT_HANDLE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><circle cx="9" cy="6" r="1.5"/><circle cx="15" cy="6" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="18" r="1.5"/><circle cx="15" cy="18" r="1.5"/></svg>';

function dashLayoutDeepFreeze(obj) {
  Object.getOwnPropertyNames(obj).forEach(key => {
    const val = obj[key];
    if (val && typeof val === 'object' && !Object.isFrozen(val)) dashLayoutDeepFreeze(val);
  });
  return Object.freeze(obj);
}

// Layout padrão por tela — constante explícita e profundamente imutável
// (objeto global, objeto por tela, arrays, cada widget). Nunca derivada do
// DOM; nenhuma função usa isto como estado de trabalho — dashLayoutApply()
// sempre LÊ valores daqui/da preferência salva, nunca escreve nestas
// constantes. Espelha exatamente os data-widget-size iniciais de
// index.html — restaurar padrão é voltar a esta constante, não reler o HTML.
const JP_WIDGET_DEFAULTS = dashLayoutDeepFreeze({
  dash: [
    // JPW-789ABC-B2, Fase 2B — o Dashboard fica com SEIS widgets.
    // P1: o cockpit, `full`, dono dos quatro fatos operacionais.
    // P2: Status do Sistema + VRM dividindo a linha seguinte; Notícias abaixo.
    // Sidebar: pendências de governança e atalhos.
    // Saíram por absorção: a faixa de métricas e a Coerência (viraram os fatos
    // e suas escalas), os Termômetros (a escala É a representação), a Postura
    // (o veredito + os motivos dizem o mesmo com número e remédio) e o Perfil e
    // Contexto (duplicava a faixa do header item a item).
    { id: 'onboarding-alert', zone: 'main', size: 'full', order: 0 },
    { id: 'operational-clearance', zone: 'main', size: 'full', order: 1 },
    { id: 'institutional-panel', zone: 'main', size: 'compact', order: 2 },
    { id: 'vrm', zone: 'main', size: 'compact', order: 3 },
    { id: 'news-high-impact', zone: 'main', size: 'compact', order: 4 },
    { id: 'quick-actions', zone: 'main', size: 'compact', order: 5 }
  ],
  exec: [
    // Ordem do protótipo: Clearance → Grade da Operação Única → Consolidado LIFO.
    // `exec-metrics-banners` e `exec-vrm` não existem no protótipo mas ficam por
    // necessidade funcional (o VRM hospeda os inputs de ATR); vão para o fim,
    // abaixo do que o design define como leitura primária.
    { id: 'exec-clearance', zone: 'main', size: 'full', order: 0 },
    { id: 'exec-phase-grids', zone: 'main', size: 'full', order: 1 },
    { id: 'exec-lifo-monitor', zone: 'main', size: 'full', order: 2 },
    { id: 'exec-metrics-banners', zone: 'main', size: 'full', order: 3 }
  ],
  contas: [
    // Fase 2C: a Nota de Governança virou disclosure no cabeçalho do Parque.
    { id: 'contas-accounts-table', zone: 'main', size: 'full', order: 0 },
    { id: 'contas-order-application', zone: 'main', size: 'medium', order: 1 }
  ],
  contab: [
    // Ordem do protótipo: Real vs Projetado PAREADO com Fechamento Diário.
    // Simulação e Projeção Diária vivem em disclosure (P3) e vão para o fim.
    { id: 'contab-period-goals', zone: 'main', size: 'full', order: 0 },
    { id: 'contab-real-vs-projected', zone: 'main', size: 'medium', order: 1 },
    { id: 'contab-daily-close', zone: 'main', size: 'medium', order: 2 },
    { id: 'contab-entries', zone: 'main', size: 'full', order: 3 }
  ]
});

function dashLayoutEnabled() {
  return document.documentElement.dataset.customLayout === 'enabled' && document.documentElement.dataset.shell === 'global-dashboard';
}

/* ======================= ACESSO AO DOM POR TELA ======================= */

function dashLayoutZoneEl(screenId, zone) {
  const cfg = JP_WIDGET_SCREENS[screenId]; if (!cfg) return null;
  const containerId = zone === 'sidebar' ? cfg.sidebar : cfg.main;
  return containerId ? document.getElementById(containerId) : null;
}
function dashLayoutCardEl(screenId, widgetId) {
  const cfg = JP_WIDGET_SCREENS[screenId]; if (!cfg) return null;
  const sel = '[data-layout-card="' + widgetId + '"]';
  const mainEl = document.getElementById(cfg.main);
  if (mainEl) { const found = mainEl.querySelector(sel); if (found) return found; }
  if (cfg.sidebar) { const sideEl = document.getElementById(cfg.sidebar); if (sideEl) { const found = sideEl.querySelector(sel); if (found) return found; } }
  return null;
}
function dashLayoutActiveScreenId() {
  const active = document.querySelector('.screen.active');
  if (!active) return null;
  return JP_WIDGET_SCREENS[active.id] ? active.id : null; // 'config' não está no registro
}
function dashLayoutAllowedWidgetIds(screenId) {
  return (JP_WIDGET_DEFAULTS[screenId] || []).map(w => w.id);
}

// Fonte única da política de cada widget: os atributos no próprio elemento
// (index.html). Toda checagem de zona/tamanho/movibilidade — arraste, menu,
// validação de preferência salva — passa por estas três funções; nada
// duplica a política em uma segunda lista JS.
function dashLayoutZonesFor(card) {
  const raw = card && card.dataset.layoutAllowedZones;
  return raw ? raw.trim().split(/\s+/) : [];
}
function dashLayoutSizesFor(card) {
  const raw = card && card.dataset.widgetAllowedSizes;
  return raw ? raw.trim().split(/\s+/) : [];
}
function dashLayoutIsMovable(card) {
  return !card || card.dataset.layoutMovable !== 'false';
}
function dashLayoutZonesForId(screenId, id) { return dashLayoutZonesFor(dashLayoutCardEl(screenId, id)); }
function dashLayoutSizesForId(screenId, id) { return dashLayoutSizesFor(dashLayoutCardEl(screenId, id)); }

// Vizinho movível mais próximo na direção dada, pulando qualquer card
// data-layout-movable="false" pelo caminho. Um bloqueado nunca é alvo válido
// de reordenação — sem isto, "mover para cima/baixo" trocaria de posição com
// um vizinho bloqueado, deslocando algo que a própria política declara fixo.
function dashLayoutNearestMovableSibling(card, direction) {
  const siblings = [...card.parentElement.querySelectorAll(':scope > [data-layout-card]')];
  const idx = siblings.indexOf(card);
  const step = direction === 'up' ? -1 : 1;
  for (let i = idx + step; i >= 0 && i < siblings.length; i += step) {
    if (dashLayoutIsMovable(siblings[i])) return siblings[i];
  }
  return null;
}

// Troca a posição de dois cards sem afetar a ordem relativa de nenhum outro
// irmão entre eles (inclusive bloqueados) — ao contrário de before()/after()
// direto, que desloca tudo que estiver entre os dois pontos.
function dashLayoutSwapCards(a, b) {
  const marker = document.createComment('dash-layout-swap');
  a.parentElement.insertBefore(marker, a);
  b.parentElement.insertBefore(a, b);
  marker.parentElement.insertBefore(b, marker);
  marker.remove();
}
function dashLayoutZoneLabel(zones) {
  if (zones.length === 1 && zones[0] === 'main') return 'coluna principal';
  if (zones.length === 1 && zones[0] === 'sidebar') return 'coluna lateral';
  return null;
}

/* ======================= VALIDAÇÃO E PERSISTÊNCIA (v3) ======================= */

const JP_WIDGET_STORAGE_KEY_V6 = 'jpwealth.ui.widgetLayouts.v6';
const JP_WIDGET_STORAGE_KEY_V5 = 'jpwealth.ui.widgetLayouts.v5'; // só para migração — nunca gravado de novo
const JP_WIDGET_STORAGE_KEY_V4 = 'jpwealth.ui.widgetLayouts.v4'; // só para migração — nunca gravado de novo
const JP_WIDGET_STORAGE_KEY_V3 = 'jpwealth.ui.widgetLayouts.v3'; // só para migração — nunca gravado de novo
const JP_WIDGET_STORAGE_KEY_V2 = 'jpwealth.ui.widgetLayout.v2'; // só para migração — nunca gravado de novo

// Valida a lista de widgets de UMA tela contra a política real daquela tela
// (inventário de IDs esperados + zonas/tamanhos permitidos por widget, lidos
// do DOM). Cada tela é validada de forma independente — uma tela quebrada
// nunca contamina outra.
// MIGRAÇÃO JPW-789ABC — o painel institucional decorativo virou Status do
// Sistema e perdeu o tamanho 'large' (o footprint 2×2 era exatamente o defeito
// que o redesign corrige). Sem esta coerção o estrago seria silencioso e
// desproporcional: 'large' ERA o padrão antigo, então toda preferência já
// gravada carrega institutional-panel em 'large'; ao reprovar no teste de
// tamanho permitido, dashLayoutValidateScreenWidgets devolve null para a TELA
// INTEIRA e dashLayoutNormalizeV6 joga fora TODA a personalização do Dashboard
// — não só este widget. Coerção pontual, portanto: um widget, um tamanho,
// preservando zona e ordem escolhidas pelo usuário.
//
// Aplicada aqui, no topo do validador, e não em cada chamador: os três
// caminhos (carga v3, promoção da v2 legada e revalidação ao concluir a
// edição) passam obrigatoriamente por esta função, então nenhum fica de fora.
// Nos casos em que não há o que migrar é no-op.
function dashLayoutMigrateWidgets(screenId, widgets) {
  if (!Array.isArray(widgets)) return widgets;
  // Widgets que deixaram de existir: descartá-los é permanente e seguro, porque
  // o id não pode mais ser escolha legítima de ninguém — mesma natureza da
  // coerção de tamanho proibido. Sem isto, a contagem não bate e o validador
  // devolve null para a TELA INTEIRA.
  if (screenId === 'contas') return widgets.filter(w => !w || w.id !== 'contas-governance-note');
  if (screenId === 'exec') return widgets.filter(w => !w || !['exec-onboarding-alert','exec-vrm'].includes(w.id));
  if (screenId === 'contab') return widgets.filter(w => !w || !['contab-cycle-pace','contab-simulation','contab-daily-projection','contab-audit-log'].includes(w.id));
  if (screenId !== 'dash') return widgets;
  return widgets.map(w => {
    if (!w || typeof w !== 'object') return w;
    if (w.id === 'onboarding-alert' || w.id === 'operational-clearance') return { ...w, zone:'main', size:'full' };
    if (['institutional-panel','vrm','news-high-impact','quick-actions'].includes(w.id)) return { ...w, zone:'main', size:'compact' };
    return w;
  });
}

function dashLayoutValidateScreenWidgets(screenId, widgets) {
  widgets = dashLayoutMigrateWidgets(screenId, widgets);
  const expectedIds = dashLayoutAllowedWidgetIds(screenId);
  if (!Array.isArray(widgets) || widgets.length !== expectedIds.length) return null;
  const seen = new Set();
  for (const w of widgets) {
    if (!w || typeof w !== 'object') return null;
    const { id, zone, size, order } = w;
    if (typeof id !== 'string' || !expectedIds.includes(id)) return null; // id desconhecido
    if (seen.has(id)) return null; // duplicado
    seen.add(id);
    const zones = dashLayoutZonesForId(screenId, id);
    if (typeof zone !== 'string' || !zones.includes(zone)) return null; // zona proibida
    const sizes = dashLayoutSizesForId(screenId, id);
    if (typeof size !== 'string' || !DASH_LAYOUT_SIZE_VALUES.includes(size) || !sizes.includes(size)) return null; // tamanho proibido/desconhecido
    if (typeof order !== 'number' || !Number.isFinite(order)) return null;
  }
  for (const id of expectedIds) { if (!seen.has(id)) return null; } // obrigatório ausente
  return widgets.slice().sort((a, b) => a.order - b.order).map((w, i) => ({ id: w.id, zone: w.zone, size: w.size, order: i }));
}

// Normaliza um envelope v4 bruto: cada tela é resolvida de forma
// independente — telas inválidas recebem só o PADRÃO DAQUELA TELA; as
// demais, válidas, são preservadas exatamente como estavam. Nunca retorna
// null para o todo por causa de uma tela quebrada.
function dashLayoutNormalizeV6(raw) {
  const rawScreens = (raw && typeof raw === 'object' && raw.version === 6 && raw.screens && typeof raw.screens === 'object') ? raw.screens : {};
  const screens = {};
  JP_WIDGET_SCREEN_IDS.forEach(screenId => {
    const provided = rawScreens[screenId] && rawScreens[screenId].widgets;
    const validated = dashLayoutValidateScreenWidgets(screenId, provided);
    screens[screenId] = { widgets: validated || JP_WIDGET_DEFAULTS[screenId].map(w => ({ ...w })) };
  });
  return { version: 6, screens };
}

function dashLayoutSaveV6(full) {
  try { localStorage.setItem(JP_WIDGET_STORAGE_KEY_V6, JSON.stringify(full)); } catch (_) { return false; }
  return true;
}
function dashLayoutClearAllPreferences() {
  try { localStorage.removeItem(JP_WIDGET_STORAGE_KEY_V6); } catch (_) { /* silencioso */ }
  try { localStorage.removeItem(JP_WIDGET_STORAGE_KEY_V5); } catch (_) { /* silencioso */ }
  try { localStorage.removeItem(JP_WIDGET_STORAGE_KEY_V4); } catch (_) { /* silencioso */ }
  try { localStorage.removeItem(JP_WIDGET_STORAGE_KEY_V3); } catch (_) { /* silencioso */ }
  try { localStorage.removeItem(JP_WIDGET_STORAGE_KEY_V2); } catch (_) { /* silencioso */ }
}

// MIGRAÇÃO ÚNICA v4 → v5 (JPW-789ABC-B2, Fase 2B — remoção dos redundantes).
//
// Cinco widgets deixam de existir: a faixa de métricas, a Coerência de
// Alavancagem, os Termômetros, a Postura e o Perfil e Contexto. Todos foram
// absorvidos pelo cockpit, pelo Status do Sistema ou pela faixa de contexto do
// header — nenhum dado sumiu, só as representações duplicadas.
//
// Sem esta migração o estrago seria total, não parcial:
// dashLayoutValidateScreenWidgets reprova por TRÊS caminhos independentes —
// contagem diferente (11 salvos vs 6 esperados), id desconhecido e obrigatório
// ausente — e cada um devolve null para a TELA INTEIRA, fazendo
// dashLayoutNormalizeV6 descartar TODA a personalização do Dashboard, não
// apenas os cinco removidos.
//
// A coerção de `operational-clearance` large → full é ÚNICA e deliberada.
// `large` continua sendo tamanho permitido, mas deixou de ser compatível com o
// cockpit de quatro fatos: em duas colunas as células caem para ~98px e
// truncam dado financeiro. Preserva-se a intenção do usuário (ver o cockpit),
// não uma configuração que deixou de ser válida. Por ser única, quem escolher
// `large` de novo depois da migração mantém a escolha.
const DASH_LAYOUT_REMOVIDOS_V5 = ['metric-strip', 'leverage-coherence', 'thermometers', 'posture', 'profile-context'];
// Fase 2C: a mesma limpeza chega ao Execution Board. `exec-vrm` NÃO entra aqui —
// ele hospeda os inputs editáveis de ATR e foi preservado de propósito.
const EXEC_LAYOUT_REMOVIDOS_V6 = ['exec-posture', 'exec-thermometers', 'exec-coherence'];
function dashLayoutMigrateExecV5ToV6(widgets) {
  if (!Array.isArray(widgets)) return widgets;
  return widgets
    .filter(w => w && typeof w === 'object' && EXEC_LAYOUT_REMOVIDOS_V6.indexOf(w.id) < 0)
    .map(w => ({ ...w }))
    .sort((a, b) => a.order - b.order)
    .map((w, i) => ({ ...w, order: i }));
}
function dashLayoutMigrateDashV4ToV5(widgets) {
  if (!Array.isArray(widgets)) return widgets;
  return widgets
    .filter(w => w && typeof w === 'object' && DASH_LAYOUT_REMOVIDOS_V5.indexOf(w.id) < 0)
    .map(w => (w.id === 'operational-clearance' && w.size === 'large') ? { ...w, size: 'full' } : { ...w })
    .sort((a, b) => a.order - b.order)
    .map((w, i) => ({ ...w, order: i }));
}

// Migração v2 (só Dashboard, já com tamanho) → v3 (multitelas). v2 tem
// precedência zero se v3/v4 já existirem — só é olhada se nenhuma das duas
// foi criada. Só promove depois de validar; se a v2 for inválida, não apaga
// nada e cai no padrão.
function dashLayoutValidateV2Legacy(pref) {
  if (!pref || typeof pref !== 'object' || pref.version !== 2) return null;
  // Forma real da v2 (só Dashboard, sem o envelope "screens" da v3):
  // { version:2, dashboard:{ widgets:[...] } }
  const widgets = pref.dashboard && pref.dashboard.widgets;
  // MIGRA ANTES DE VALIDAR. A ordem importa e estava invertida: a v2 carrega os
  // 11 widgets do esquema antigo e o validador exige exatamente os 6 atuais, de
  // modo que validar primeiro reprovaria SEMPRE e a v2 jamais promoveria —
  // silenciosamente, caindo no padrão. Migrada primeiro, ela chega ao validador
  // já na forma vigente.
  return dashLayoutValidateScreenWidgets('dash', dashLayoutPromoteDashParaV5(widgets, 3));
}

// MIGRAÇÃO ÚNICA v3 → v4 (JPW-789ABC, rebalanceamento do Status do Sistema).
//
// Por que ÚNICA e não coerção permanente como a do painel institucional: os
// dois casos são diferentes. 'large' deixou de ser tamanho PERMITIDO para o
// painel, então coagi-lo em toda validação é uma rede de segurança que nunca
// atropela escolha nenhuma — ninguém consegue mais escolher 'large' ali. Já
// 'full' CONTINUA permitido para a faixa de métricas; coagir 'full'→'medium'
// a cada carga tornaria a opção impossível de salvar (dashLayoutFinish também
// valida antes de gravar), quebrando o editor de layout para esse widget.
// Por isso a conversão acontece uma vez, na promoção de envelope — exatamente
// o mecanismo que a v2→v3 já usa: lê a chave antiga, grava a nova, apaga a
// antiga.
//
// A ORDEM só é trocada quando o par ainda está na relação do padrão ANTIGO
// (painel imediatamente antes da faixa). Quem reordenou a tela por conta
// própria mantém a ordem que escolheu — a migração conserta o padrão, não
// sobrescreve personalização.
function dashLayoutMigrateDashV3ToV4(widgets) {
  if (!Array.isArray(widgets)) return widgets;
  const out = widgets.map(w => (w && typeof w === 'object') ? { ...w } : w);
  const strip = out.find(w => w && w.id === 'metric-strip');
  const panel = out.find(w => w && w.id === 'institutional-panel');
  if (!strip || !panel) return out;
  if (strip.size === 'full') strip.size = 'medium';
  if (strip.zone === panel.zone && strip.order === panel.order + 1) {
    const t = strip.order; strip.order = panel.order; panel.order = t;
  }
  return out;
}

// Cada envelope legado é promovido pela CADEIA COMPLETA até a v5, na ordem —
// uma base parada na v2 passa por v3→v4→v5 numa carga só. Sem isso, quem
// abrisse o app pela primeira vez depois desta fase perderia a personalização
// exatamente como se nunca tivesse migrado.
function dashLayoutPromoteDashParaV5(widgets, apartirDe) {
  let w = widgets;
  if (apartirDe <= 3) w = dashLayoutMigrateDashV3ToV4(w);
  return dashLayoutMigrateDashV4ToV5(w);
}

function dashLayoutLoadFullState() {
  const rawV6 = (() => { try { return localStorage.getItem(JP_WIDGET_STORAGE_KEY_V6); } catch (_) { return null; } })();
  if (rawV6 !== null) {
    // v6 existe (mesmo que parcialmente inválida) — tem precedência total e
    // nunca reabre migração (evita remigrar a cada carga).
    let parsed = null;
    try { parsed = JSON.parse(rawV6); } catch (_) { /* trata como ausente abaixo */ }
    return dashLayoutNormalizeV6(parsed);
  }
  // v4 e v3 compartilham a mesma forma de envelope ({version, screens}); só
  // muda por quantos passos de migração o `dash` precisa passar.
  const legado = [
    { chave: JP_WIDGET_STORAGE_KEY_V5, versao: 5 },
    { chave: JP_WIDGET_STORAGE_KEY_V4, versao: 4 },
    { chave: JP_WIDGET_STORAGE_KEY_V3, versao: 3 }
  ];
  for (const { chave, versao } of legado) {
    const raw = (() => { try { return localStorage.getItem(chave); } catch (_) { return null; } })();
    if (raw === null) continue;
    let parsed = null;
    try { parsed = JSON.parse(raw); } catch (_) { /* ignora */ }
    const telas = (parsed && typeof parsed === 'object' && parsed.version === versao && parsed.screens && typeof parsed.screens === 'object') ? parsed.screens : {};
    // A versão do envelope promovido tem de ser a CORRENTE: dashLayoutNormalizeV6
    // exige version===6 e, com 5 aqui, rejeitava tudo e devolvia os padrões de
    // todas as telas — perdendo em silêncio a personalização que a migração
    // acabara de preservar.
    const promoted = { version: 6, screens: {} };
    JP_WIDGET_SCREEN_IDS.forEach(screenId => {
      const widgets = telas[screenId] && telas[screenId].widgets;
      promoted.screens[screenId] = { widgets:
        screenId === 'dash' ? dashLayoutPromoteDashParaV5(widgets, versao)
        : screenId === 'exec' ? dashLayoutMigrateExecV5ToV6(widgets)
        : widgets };
    });
    const candidate = dashLayoutNormalizeV6(promoted);
    dashLayoutSaveV6(candidate);
    try { localStorage.removeItem(chave); } catch (_) { /* silencioso */ }
    return candidate;
  }
  const rawV2 = (() => { try { return localStorage.getItem(JP_WIDGET_STORAGE_KEY_V2); } catch (_) { return null; } })();
  if (rawV2 !== null) {
    let v2Parsed = null;
    try { v2Parsed = JSON.parse(rawV2); } catch (_) { /* ignora */ }
    const migratedDash = dashLayoutValidateV2Legacy(v2Parsed);
    if (migratedDash) {
      // `migratedDash` já veio promovido e validado por dashLayoutValidateV2Legacy.
      const candidate = dashLayoutNormalizeV6({ version: 5, screens: { dash: { widgets: migratedDash } } });
      dashLayoutSaveV6(candidate);
      try { localStorage.removeItem(JP_WIDGET_STORAGE_KEY_V2); } catch (_) { /* silencioso */ }
      return candidate;
    }
    // v2 presente mas inválida — não promove, não apaga, cai no padrão completo
  }
  return dashLayoutNormalizeV6(null); // tudo padrão
}

function dashLayoutApplyScreen(screenId, widgets) {
  widgets.forEach(w => {
    const el = dashLayoutCardEl(screenId, w.id);
    if (!el) return;
    el.dataset.widgetSize = w.size;
    const zoneEl = dashLayoutZoneEl(screenId, w.zone);
    if (zoneEl) zoneEl.appendChild(el);
  });
}
function dashLayoutApplyAllScreens(full) {
  JP_WIDGET_SCREEN_IDS.forEach(screenId => dashLayoutApplyScreen(screenId, full.screens[screenId].widgets));
}
function dashLayoutCurrentScreenState(screenId) {
  const cfg = JP_WIDGET_SCREENS[screenId];
  const widgets = [];
  let order = 0;
  cfg.zones.forEach(zone => {
    const root = dashLayoutZoneEl(screenId, zone);
    if (!root) return;
    [...root.querySelectorAll(':scope > [data-layout-card]')].forEach(el => {
      widgets.push({ id: el.dataset.layoutCard, zone, size: el.dataset.widgetSize, order: order++ });
    });
  });
  return widgets;
}

function dashLayoutBoot() {
  if (!dashLayoutEnabled()) return;
  const full = dashLayoutLoadFullState();
  dashLayoutApplyAllScreens(full);
}

/* ======================= CAMADA GLOBAL DE POPOVERS ======================= */
// Norma registrada em app.css ("NORMA DE POPOVERS"): nenhum popover vive
// dentro de um card animado/transformado. Todo popover nasce em
// #jpPopoverLayer, position:fixed, posicionado por getBoundingClientRect().
// Reutilizado sem alteração por todas as telas — nenhum layer por tela.

// Sessão de edição GLOBAL (não por tela): uma vez iniciada, permanece ativa
// ao navegar pelas telas. `snapshots` guarda uma cópia congelada de ordem+
// zona+tamanho de TODAS as telas, capturada uma única vez na entrada — nunca
// por referência mutável (dashLayoutCurrentScreenState já retorna arrays/
// objetos novos a cada chamada; aqui, além disso, cada um é Object.freeze()).
// `dirtyScreens` é o único critério de "tela alterada": comparação
// estrutural (dashLayoutSnapshotsEqual) contra o snapshot, nunca visita.
const dashLayoutState = { editing: false, activeScreenId: null, snapshots: null, dirtyScreens: null, drag: null, openPopover: null, lastDragEndAt: 0 };

function dashLayoutPopoverLayer() { return document.getElementById('jpPopoverLayer'); }

function dashLayoutPositionPopover(el, anchor) {
  const margin = 8;
  const r = anchor.getBoundingClientRect();
  const pw = el.offsetWidth, ph = el.offsetHeight;
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

function dashLayoutOpenCardMenu(screenId, card, anchorBtn) {
  if (dashLayoutState.openPopover && dashLayoutState.openPopover.card === card) { dashLayoutClosePopover({ returnFocus: false }); return; }
  dashLayoutClosePopover({ returnFocus: false }); // só uma instância aberta por vez

  const movable = dashLayoutIsMovable(card);
  const parentZone = card.parentElement === dashLayoutZoneEl(screenId, 'sidebar') ? 'sidebar' : 'main';
  const allowedZones = dashLayoutZonesFor(card);
  // Widgets não movíveis (categorias "apenas redimensionável" e "totalmente
  // bloqueado") nunca oferecem reordenar/trocar de coluna — só a categoria
  // "totalmente bloqueado" nem chega a abrir menu (ver dashLayoutDecorateCard);
  // esta função só roda para quem tem pelo menos uma ação real.
  const items = [];
  if (movable) {
    // Alvo é o vizinho movível mais próximo, pulando bloqueados — nunca troca
    // de posição com um card que a própria política declara fixo.
    if (dashLayoutNearestMovableSibling(card, 'up')) items.push(['up', 'Mover para cima']);
    if (dashLayoutNearestMovableSibling(card, 'down')) items.push(['down', 'Mover para baixo']);
    if (parentZone !== 'main' && allowedZones.includes('main')) items.push(['zone-main', 'Mover para coluna principal']);
    if (parentZone !== 'sidebar' && allowedZones.includes('sidebar')) items.push(['zone-sidebar', 'Mover para coluna lateral']);
  }

  const sizes = dashLayoutSizesFor(card);
  const currentSize = card.dataset.widgetSize;
  const cardLabel = DASH_LAYOUT_LABELS[card.dataset.layoutCard] || card.dataset.layoutCard;

  const el = document.createElement('div');
  el.className = 'jp-popover dash-layout-card-menu';
  el.id = 'jpPopoverActive';
  el.setAttribute('role', 'menu');
  el.setAttribute('aria-label', 'Opções — ' + cardLabel);

  let html = items.map(([action, label]) => '<button type="button" role="menuitem" data-action="' + action + '">' + label + '</button>').join('');
  if (items.length && sizes.length > 1) html += '<div class="dash-layout-menu-sep" role="separator"></div>';
  if (sizes.length > 1) {
    html += '<div class="dash-layout-menu-heading" id="dashLayoutSizeHeading-' + card.dataset.layoutCard + '">Tamanho</div>';
    html += '<div role="group" aria-labelledby="dashLayoutSizeHeading-' + card.dataset.layoutCard + '">' +
      sizes.map(s => '<button type="button" role="menuitemradio" aria-checked="' + (s === currentSize ? 'true' : 'false') + '" data-size="' + s + '"><span>' + DASH_WIDGET_SIZE_LABELS[s] + '</span><span class="dash-layout-check" aria-hidden="true">✓</span></button>').join('') +
      '</div>';
  }
  el.innerHTML = html;

  el.addEventListener('click', event => {
    const btn = event.target.closest('button[data-action], button[data-size]');
    if (!btn) return;
    if (btn.dataset.action === 'up') { const t = dashLayoutNearestMovableSibling(card, 'up'); if (t) dashLayoutSwapCards(card, t); dashLayoutRefreshAllLabels(screenId); dashLayoutRecomputeDirty(screenId); dashLayoutAnnounce(cardLabel + ' movido. ' + card.getAttribute('aria-label')); }
    else if (btn.dataset.action === 'down') { const t = dashLayoutNearestMovableSibling(card, 'down'); if (t) dashLayoutSwapCards(card, t); dashLayoutRefreshAllLabels(screenId); dashLayoutRecomputeDirty(screenId); dashLayoutAnnounce(cardLabel + ' movido. ' + card.getAttribute('aria-label')); }
    else if (btn.dataset.action === 'zone-main') { dashLayoutZoneEl(screenId, 'main').append(card); dashLayoutRefreshAllLabels(screenId); dashLayoutRecomputeDirty(screenId); dashLayoutAnnounce(cardLabel + ' movido. ' + card.getAttribute('aria-label')); }
    else if (btn.dataset.action === 'zone-sidebar') { dashLayoutZoneEl(screenId, 'sidebar').append(card); dashLayoutRefreshAllLabels(screenId); dashLayoutRecomputeDirty(screenId); dashLayoutAnnounce(cardLabel + ' movido. ' + card.getAttribute('aria-label')); }
    else if (btn.dataset.size) { dashLayoutChangeSize(card, btn.dataset.size, cardLabel); dashLayoutRecomputeDirty(screenId); }
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
function dashLayoutAllCardEls(screenId) {
  const cfg = JP_WIDGET_SCREENS[screenId];
  const out = [];
  cfg.zones.forEach(zone => {
    const root = dashLayoutZoneEl(screenId, zone);
    if (root) out.push(...root.querySelectorAll(':scope > [data-layout-card]'));
  });
  return out;
}

// Quatro categorias, derivadas só dos atributos do próprio card (nenhuma
// política duplicada aqui):
//   1. movível e redimensionável — alça + menu (posição e tamanho)
//   2. apenas movível           — alça + menu só se houver ação de posição
//      útil (sem seção de tamanho, porque só tem 1 tamanho permitido)
//   3. apenas redimensionável   — sem alça, menu só com a seção de tamanho
//   4. totalmente bloqueado     — sem alça, sem menu, só indicador discreto
function dashLayoutWidgetCategory(card) {
  const movable = dashLayoutIsMovable(card);
  const resizable = dashLayoutSizesFor(card).length > 1;
  if (movable && resizable) return 'movable-resizable';
  if (movable) return 'movable-only';
  if (resizable) return 'resizable-only';
  return 'locked';
}

// Telas onde todo widget é "totalmente bloqueado" (ex.: Motor de Lote) não
// têm nenhuma ação real de personalização — checado direto no DOM real,
// nunca por uma lista paralela de telas "sem suporte". Isto NÃO impede a
// sessão global de continuar: só decide se a tela ativa ganha a nota
// discreta abaixo em vez de alças/menus.
function dashLayoutScreenHasAnyAction(screenId) {
  return dashLayoutAllCardEls(screenId).some(card => dashLayoutWidgetCategory(card) !== 'locked');
}

// Nota discreta em tela (não alert/modal) para quando a tela ativa não tem
// nenhum widget acionável — ex.: Motor de Lote. Vive dentro da própria zona
// "main" da tela, como primeiro filho; nasce/some ao trocar de tela ativa.
function dashLayoutShowFixedScreenNote(screenId) {
  const zoneEl = dashLayoutZoneEl(screenId, 'main');
  if (!zoneEl || zoneEl.querySelector(':scope > .dash-layout-fixed-note')) return;
  const note = document.createElement('p');
  note.className = 'dash-layout-fixed-note';
  note.textContent = 'Esta tela possui estrutura operacional fixa.';
  zoneEl.insertBefore(note, zoneEl.firstChild);
}
function dashLayoutRemoveFixedScreenNote() {
  document.querySelectorAll('.dash-layout-fixed-note').forEach(el => el.remove());
}

function dashLayoutDecorateCard(screenId, card) {
  if (card.querySelector(':scope > .dash-layout-handle, :scope > .dash-layout-menu-btn, :scope > .dash-layout-lock')) return; // já decorado
  const cardLabel = DASH_LAYOUT_LABELS[card.dataset.layoutCard] || card.dataset.layoutCard;
  const category = dashLayoutWidgetCategory(card);

  if (category === 'locked') {
    // Totalmente bloqueado: sem alça, sem menu — só um indicador discreto
    // (Etapa 6). Nenhuma ação de clique, nenhum foco, não entra na animação
    // (ver seletor :not([data-layout-movable="false"]) em app.css).
    const lock = document.createElement('span');
    lock.className = 'dash-layout-lock';
    lock.setAttribute('aria-label', 'Posição fixa — ' + cardLabel + ' não pode ser movido ou redimensionado.');
    lock.title = 'Posição fixa';
    lock.textContent = '🔒';
    card.append(lock);
    return;
  }

  if (category === 'movable-resizable' || category === 'movable-only') {
    const handle = document.createElement('button');
    handle.type = 'button';
    handle.className = 'dash-layout-handle';
    handle.setAttribute('aria-label', 'Arrastar para reposicionar — ' + cardLabel);
    handle.innerHTML = DASH_LAYOUT_HANDLE_SVG;
    card.append(handle);
    handle.addEventListener('pointerdown', event => dashLayoutStartDrag(event, screenId, card, handle));
  }

  // Menu: só nasce se houver pelo menos uma ação real (reordenar, trocar de
  // coluna ou redimensionar) — nunca um menu vazio (regra explícita).
  const hasReorderAction = category !== 'resizable-only' && category !== 'locked' && (
    !!dashLayoutNearestMovableSibling(card, 'up') ||
    !!dashLayoutNearestMovableSibling(card, 'down') ||
    dashLayoutZonesFor(card).length > 1
  );
  const hasSizeAction = category === 'movable-resizable' || category === 'resizable-only';
  if (hasReorderAction || hasSizeAction) {
    const menuBtn = document.createElement('button');
    menuBtn.type = 'button';
    menuBtn.className = 'dash-layout-menu-btn';
    menuBtn.setAttribute('aria-label', 'Mais opções — ' + cardLabel);
    menuBtn.setAttribute('aria-haspopup', 'menu');
    menuBtn.setAttribute('aria-expanded', 'false');
    menuBtn.textContent = '⋮';
    card.append(menuBtn);
    menuBtn.addEventListener('click', event => { event.stopPropagation(); dashLayoutOpenCardMenu(screenId, card, menuBtn); });
  }

  card.tabIndex = 0;
  card.setAttribute('role', 'group');
  dashLayoutUpdateCardLabel(screenId, card);
}

function dashLayoutUndecorateCard(card) {
  card.querySelectorAll(':scope > .dash-layout-handle, :scope > .dash-layout-menu-btn, :scope > .dash-layout-lock').forEach(el => el.remove());
  card.removeAttribute('tabindex');
  card.removeAttribute('role');
  card.removeAttribute('aria-label');
}

function dashLayoutUpdateCardLabel(screenId, card) {
  // Bloqueado não é card de reorganização (sem alça, sem menu, sem tabIndex/
  // role) — dashLayoutRefreshAllLabels itera TODOS os cards da tela após
  // qualquer reordenação alheia, então esta guarda evita vazar um aria-label
  // de posição num card que a política exige permanecer sem controles.
  if (dashLayoutWidgetCategory(card) === 'locked') return;
  const parent = card.parentElement;
  const isMain = parent === dashLayoutZoneEl(screenId, 'main');
  const siblings = parent ? [...parent.querySelectorAll(':scope > [data-layout-card]')] : [];
  const pos = siblings.indexOf(card) + 1;
  const label = DASH_LAYOUT_LABELS[card.dataset.layoutCard] || card.dataset.layoutCard;
  const sizeLabel = DASH_WIDGET_SIZE_LABELS[card.dataset.widgetSize] || card.dataset.widgetSize;
  const zoneLabel = JP_WIDGET_SCREENS[screenId].zones.length > 1 ? (', coluna ' + (isMain ? 'principal' : 'lateral')) : '';
  card.setAttribute('aria-label', label + ', tamanho ' + sizeLabel.toLowerCase() + ', posição ' + pos + ' de ' + siblings.length + zoneLabel);
}
function dashLayoutRefreshAllLabels(screenId) {
  dashLayoutAllCardEls(screenId).forEach(c => dashLayoutUpdateCardLabel(screenId, c));
}

// Decora/indica só a tela ATIVA (nunca as 6 restantes) — quem está fora de
// vista não deve animar nem carregar controles interativos (Etapa 3 do
// pedido: "aplique animação e controles somente à .screen.active"). O CSS já
// restringe wobble/handles a `.screen.active` por seletor; isto garante que
// o próprio DOM de decoração (alça/menu/lock/nota) também só existe ali.
function dashLayoutApplyActiveScreenDecoration() {
  const screenId = dashLayoutState.activeScreenId;
  if (!screenId) return;
  dashLayoutAllCardEls(screenId).forEach(c => dashLayoutDecorateCard(screenId, c));
  dashLayoutRemoveFixedScreenNote();
  if (!dashLayoutScreenHasAnyAction(screenId)) dashLayoutShowFixedScreenNote(screenId);
}
function dashLayoutUndecorateScreen(screenId) {
  if (!screenId) return;
  dashLayoutAllCardEls(screenId).forEach(dashLayoutUndecorateCard);
}

// Texto da barra global: título fixo + tela atual + contagem de telas
// alteradas (dirtyScreens.size). Também limpa qualquer erro de validação
// mostrado por dashLayoutShowBarError — qualquer atualização normal da barra
// (troca de tela, nova alteração) volta o rótulo ao estado neutro.
function dashLayoutUpdateBarInfo() {
  const screenId = dashLayoutState.activeScreenId;
  const label = document.getElementById('dashLayoutBarLabel');
  if (label) {
    label.textContent = 'Tela atual: ' + (screenId ? JP_WIDGET_SCREENS[screenId].label : '—');
    label.classList.remove('dash-layout-bar-error');
  }
  const countEl = document.getElementById('dashLayoutBarCount');
  if (countEl) {
    const n = dashLayoutState.dirtyScreens ? dashLayoutState.dirtyScreens.size : 0;
    countEl.textContent = n === 0 ? '0 telas alteradas' : (n === 1 ? '1 tela alterada' : n + ' telas alteradas');
  }
}
function dashLayoutShowBarError(msg) {
  const label = document.getElementById('dashLayoutBarLabel');
  if (label) { label.textContent = msg; label.classList.add('dash-layout-bar-error'); }
  dashLayoutAnnounce(msg);
}

// Compara duas leituras de dashLayoutCurrentScreenState — comparação
// ESTRUTURAL (id/zona/tamanho/ordem), nunca por referência/identidade de
// objeto. Base de dirtyScreens: uma tela só entra/sai do conjunto quando o
// estado real diverge/converge do snapshot da sessão, nunca por ter sido
// simplesmente visitada.
function dashLayoutSnapshotsEqual(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
  return a.every((w, i) => b[i] && w.id === b[i].id && w.zone === b[i].zone && w.size === b[i].size && w.order === b[i].order);
}
function dashLayoutRecomputeDirty(screenId) {
  if (!dashLayoutState.dirtyScreens) return;
  const snap = dashLayoutState.snapshots[screenId];
  const isDirty = !dashLayoutSnapshotsEqual(snap, dashLayoutCurrentScreenState(screenId));
  if (isDirty) dashLayoutState.dirtyScreens.add(screenId); else dashLayoutState.dirtyScreens.delete(screenId);
  dashLayoutUpdateBarInfo();
}

// Troca a tela ATIVA dentro de uma sessão já aberta — nunca cancela, nunca
// salva, nunca restaura, nunca encerra a sessão (Etapa 3 do pedido). Só
// fecha o popover (evita âncora presa numa tela que vai ficar oculta),
// remove a decoração da tela anterior e decora a nova — os rascunhos de
// TODAS as telas (inclusive a que está saindo de vista) continuam
// intocados: vivem no próprio DOM de cada *WidgetGrid, que nunca é
// destruído ao trocar de `.screen.active` (ver 01-navigation.js).
function dashLayoutSetActiveScreen(screenId) {
  if (!screenId || dashLayoutState.activeScreenId === screenId) return;
  dashLayoutClosePopover({ returnFocus: false });
  dashLayoutUndecorateScreen(dashLayoutState.activeScreenId);
  dashLayoutState.activeScreenId = screenId;
  dashLayoutApplyActiveScreenDecoration();
  dashLayoutUpdateBarInfo();
}

// Encerra a sessão global por completo (usado por Cancelar tudo e por
// Concluir bem-sucedido) — remove decoração/nota da tela ativa, limpa todo
// o estado de sessão (snapshots/dirtyScreens somem, não persistem entre
// sessões) e esconde a barra.
function dashLayoutEndSession() {
  dashLayoutClosePopover({ returnFocus: false });
  dashLayoutUndecorateScreen(dashLayoutState.activeScreenId);
  dashLayoutRemoveFixedScreenNote();
  dashLayoutState.editing = false;
  dashLayoutState.activeScreenId = null;
  dashLayoutState.snapshots = null;
  dashLayoutState.dirtyScreens = null;
  delete document.documentElement.dataset.layoutEditing;
  const bar = document.getElementById('dashLayoutBar');
  if (bar) bar.hidden = true;
}

function dashLayoutEnterEdit() {
  if (!dashLayoutEnabled() || dashLayoutState.editing) return;
  const screenId = dashLayoutActiveScreenId();
  if (!screenId) return; // ex.: nenhuma tela operacional ativa
  dashLayoutState.editing = true;
  dashLayoutState.activeScreenId = screenId;
  dashLayoutState.dirtyScreens = new Set();
  // Snapshot de TODAS as telas registradas, capturado uma única vez na entrada —
  // congelado (nunca mutável por referência); usado por Cancelar tudo e
  // pela detecção estrutural de dirty em cada tela.
  dashLayoutState.snapshots = {};
  JP_WIDGET_SCREEN_IDS.forEach(id => {
    dashLayoutState.snapshots[id] = Object.freeze(dashLayoutCurrentScreenState(id).map(w => Object.freeze(w)));
  });
  document.documentElement.dataset.layoutEditing = 'true';
  dashLayoutApplyActiveScreenDecoration();
  const bar = document.getElementById('dashLayoutBar');
  if (bar) bar.hidden = false;
  dashLayoutUpdateBarInfo();
  dashLayoutAnnounce('Modo de personalização ativado para todas as telas. Tela atual: ' + JP_WIDGET_SCREENS[screenId].label + '. Navegue pelas abas para personalizar cada tela; use Concluir para salvar todas as alterações de uma vez.');
}

// "Cancelar tudo": só pergunta se há algo de fato para descartar
// (dirtyScreens.size>0) — sem alteração nenhuma, sai direto. Ao confirmar,
// restaura os snapshots de todas as telas (mesmo as não-dirty, por simetria —
// idempotente para quem já está igual ao snapshot) e encerra a sessão sem
// gravar nada.
function dashLayoutCancelAll() {
  if (!dashLayoutState.editing) return;
  if (dashLayoutState.drag) dashLayoutCancelDrag();
  const dirty = dashLayoutState.dirtyScreens;
  if (dirty && dirty.size > 0 && !confirm('Descartar alterações feitas em todas as telas?')) return;
  JP_WIDGET_SCREEN_IDS.forEach(screenId => {
    const snap = dashLayoutState.snapshots[screenId];
    if (snap) dashLayoutApplyScreen(screenId, snap.map(w => ({ ...w })));
  });
  dashLayoutEndSession();
  dashLayoutAnnounce('Alterações descartadas em todas as telas.');
}

// Concluir é TRANSACIONAL: valida todas as telas em dirtyScreens antes de
// escrever qualquer coisa; se qualquer uma falhar, nada é salvo (sem commit
// parcial), a sessão continua aberta com os rascunhos intactos, e o usuário
// é levado até a tela com problema. Só depois de todas passarem é que ocorre
// UMA ÚNICA escrita no v3, preservando as telas não alteradas exatamente
// como já estavam persistidas.
function dashLayoutFinish() {
  if (!dashLayoutState.editing) return;
  if (dashLayoutState.drag) dashLayoutCancelDrag();
  const dirty = dashLayoutState.dirtyScreens ? [...dashLayoutState.dirtyScreens] : [];
  if (dirty.length === 0) {
    dashLayoutEndSession();
    dashLayoutAnnounce('Nenhuma alteração para salvar.');
    return;
  }
  const validatedByScreen = {};
  for (const screenId of dirty) {
    const validated = dashLayoutValidateScreenWidgets(screenId, dashLayoutCurrentScreenState(screenId));
    if (!validated) {
      if (typeof navigateToScreen === 'function') navigateToScreen(screenId);
      else dashLayoutSetActiveScreen(screenId);
      dashLayoutShowBarError('Layout inválido em ' + JP_WIDGET_SCREENS[screenId].label + ' — corrija ou cancele tudo.');
      return; // nada é gravado — nenhuma das telas alteradas desta sessão
    }
    validatedByScreen[screenId] = validated;
  }
  const full = dashLayoutLoadFullState();
  dirty.forEach(screenId => { full.screens[screenId] = { widgets: validatedByScreen[screenId] }; });
  dashLayoutSaveV6(full); // uma única escrita, com todas as telas alteradas já validadas
  const labels = dirty.map(id => JP_WIDGET_SCREENS[id].label).join(', ');
  dashLayoutEndSession();
  dashLayoutAnnounce((dirty.length === 1 ? '1 tela salva: ' : dirty.length + ' telas salvas: ') + labels + '.');
}

// Restaurar tela atual: dentro de uma sessão global, é PROVISÓRIO (rascunho
// — entra em dirtyScreens se divergir do snapshot, não grava). Fora de uma
// sessão (botão avulso em Configurações), continua imediato como sempre foi.
function dashLayoutRestoreDefaultConfirm() {
  const screenId = dashLayoutState.editing ? dashLayoutState.activeScreenId : dashLayoutActiveScreenId();
  if (!screenId) return;
  const label = JP_WIDGET_SCREENS[screenId].label;
  if (!confirm('Restaurar o layout padrão de ' + label + '? Isso apaga só a preferência de posição e tamanho desta tela — nenhum dado financeiro é afetado.')) return;
  dashLayoutApplyScreen(screenId, JP_WIDGET_DEFAULTS[screenId].map(w => ({ ...w })));
  if (dashLayoutState.editing) {
    dashLayoutRecomputeDirty(screenId);
    if (screenId === dashLayoutState.activeScreenId) dashLayoutRefreshAllLabels(screenId);
    dashLayoutAnnounce('Layout padrão de ' + label + ' aplicado nesta sessão — clique em Concluir para salvar.');
    return;
  }
  const full = dashLayoutLoadFullState();
  full.screens[screenId] = { widgets: dashLayoutCurrentScreenState(screenId) };
  dashLayoutSaveV6(full);
  dashLayoutAnnounce('Layout padrão de ' + label + ' restaurado.');
}

// Restaurar todos: mesma lógica dual — dentro da sessão é provisório em
// TODAS as telas registradas (só entram em dirtyScreens as que realmente mudaram em
// relação ao snapshot — Etapa 4 do pedido); fora da sessão, imediato como
// sempre foi.
function dashLayoutRestoreAllConfirm() {
  if (!confirm('Restaurar o layout padrão de TODAS as telas? Isso apaga só as preferências visuais — nenhum dado financeiro ou configuração operacional é afetado.')) return;
  if (dashLayoutState.editing) {
    JP_WIDGET_SCREEN_IDS.forEach(screenId => {
      dashLayoutApplyScreen(screenId, JP_WIDGET_DEFAULTS[screenId].map(w => ({ ...w })));
      dashLayoutRecomputeDirty(screenId);
    });
    dashLayoutRefreshAllLabels(dashLayoutState.activeScreenId);
    dashLayoutAnnounce('Padrão aplicado a todas as telas nesta sessão — clique em Concluir para salvar.');
    return;
  }
  dashLayoutClearAllPreferences();
  dashLayoutApplyAllScreens(dashLayoutNormalizeV6(null));
  dashLayoutAnnounce('Layout padrão restaurado em todas as telas.');
}

/* ======================= ARRASTE (Pointer Events) ======================= */

function dashLayoutStartDrag(event, screenId, card, handle) {
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
    screenId, card, placeholder, originMarker,
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
  const cfg = JP_WIDGET_SCREENS[d.screenId];
  const main = dashLayoutZoneEl(d.screenId, 'main');
  const side = cfg.sidebar ? dashLayoutZoneEl(d.screenId, 'sidebar') : null;
  let hoverContainer = main, hoverZone = 'main';
  if (side) {
    const sideRect = side.getBoundingClientRect();
    const overSide = x >= sideRect.left - 20 && x <= sideRect.right + 20 && y >= sideRect.top - 40 && y <= sideRect.bottom + 40;
    if (overSide) { hoverContainer = side; hoverZone = 'sidebar'; }
  }
  const zoneOk = d.allowedZones.includes(hoverZone);

  main.classList.toggle('dash-layout-dropzone-active', zoneOk && hoverContainer === main);
  if (side) side.classList.toggle('dash-layout-dropzone-active', zoneOk && hoverContainer === side);
  main.classList.toggle('dash-layout-dropzone-denied', !zoneOk && hoverContainer === main);
  if (side) side.classList.toggle('dash-layout-dropzone-denied', !zoneOk && hoverContainer === side);
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

  // Só cards movíveis entram como alvo de proximidade — o placeholder nunca
  // ancora diretamente num bloqueado (mesma regra do menu de teclado: um
  // card fixo nunca é o "vizinho" que uma reordenação desloca).
  const cards = [...container.querySelectorAll(':scope > [data-layout-card]')].filter(dashLayoutIsMovable);
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
  const d = dashLayoutState.drag; if (!d) return;
  const cfg = JP_WIDGET_SCREENS[d.screenId];
  const main = dashLayoutZoneEl(d.screenId, 'main'), side = cfg.sidebar ? dashLayoutZoneEl(d.screenId, 'sidebar') : null;
  if (main) main.classList.remove('dash-layout-dropzone-active', 'dash-layout-dropzone-denied');
  if (side) side.classList.remove('dash-layout-dropzone-active', 'dash-layout-dropzone-denied');
}

function dashLayoutOnDragEnd() {
  const d = dashLayoutState.drag; if (!d) return;
  d.placeholder.replaceWith(d.card);
  d.originMarker.remove();
  d.card.classList.remove('dash-layout-dragging', 'dash-layout-denied');
  d.card.style.position = ''; d.card.style.left = ''; d.card.style.top = ''; d.card.style.width = ''; d.card.style.height = '';
  const screenId = d.screenId;
  dashLayoutEndDragCleanupListeners();
  dashLayoutState.drag = null;
  dashLayoutState.lastDragEndAt = Date.now(); // absorve o clique residual do drop (ver saída pelo vazio)
  dashLayoutRefreshAllLabels(screenId);
  dashLayoutRecomputeDirty(screenId);
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
  dashLayoutState.lastDragEndAt = Date.now(); // idem dashLayoutOnDragEnd
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

/* ======================= TOQUE LONGO — ARRASTO DIRETO ======================= */
// Segurar um card móvel (~500 ms parado) inicia o arrasto imediatamente,
// entrando na sessão de personalização se necessário. É um atalho de ENTRADA
// no fluxo existente, nunca um bypass: o drop vira rascunho (dirtyScreens) e
// a gravação continua exclusiva do Concluir transacional. Fora da janela nada
// muda — soltar antes é clique normal, mover antes é scroll. Cards locked não
// entram (dashLayoutIsMovable), e alça/menu/controles internos preservam o
// comportamento que já têm.
const DASH_LAYOUT_LONGPRESS_MS = 500;
const DASH_LAYOUT_LONGPRESS_SLOP_PX = 8;
let dashLayoutPress = null;

function dashLayoutPressClear() {
  const p = dashLayoutPress; if (!p) return;
  clearTimeout(p.timer);
  p.card.classList.remove('dash-layout-pressing');
  document.removeEventListener('pointermove', dashLayoutPressOnMove);
  document.removeEventListener('pointerup', dashLayoutPressOnUp);
  document.removeEventListener('pointercancel', dashLayoutPressOnUp);
  document.removeEventListener('pointerdown', dashLayoutPressOnSecondPointer, true);
  document.removeEventListener('touchmove', dashLayoutPressTouchGuard);
  document.removeEventListener('contextmenu', dashLayoutPressOnContextMenu, true);
  window.removeEventListener('scroll', dashLayoutPressOnScroll, true);
  dashLayoutPress = null;
}

// Disparo dos 500 ms: entra na sessão (se preciso) e delega ao motor de
// arraste existente — o mesmo caminho da alça, sem duplicar nada. O press
// permanece vivo (active) até o pointerup para sustentar o guard de touchmove.
function dashLayoutPressFire() {
  const p = dashLayoutPress; if (!p || dashLayoutState.drag) { dashLayoutPressClear(); return; }
  if (!dashLayoutState.editing) dashLayoutEnterEdit();
  if (!dashLayoutState.editing || dashLayoutState.activeScreenId !== p.screenId) { dashLayoutPressClear(); return; }
  const handle = p.card.querySelector(':scope > .dash-layout-handle') || p.card;
  dashLayoutStartDrag(p.lastEvent, p.screenId, p.card, handle);
  if (!dashLayoutState.drag) { dashLayoutPressClear(); return; }
  p.active = true;
  document.removeEventListener('pointerdown', dashLayoutPressOnSecondPointer, true);
}

function dashLayoutOnCardPointerDown(event) {
  if (dashLayoutPress || dashLayoutState.drag) return;
  if (!dashLayoutEnabled()) return;
  if (event.button !== 0 || event.isPrimary === false) return;
  const card = event.target.closest('[data-layout-card]');
  if (!card) return;
  // Controles interativos preservam o próprio gesto (ex.: ↻ das notícias);
  // alça e menu já têm caminhos próprios de arraste/opções.
  if (event.target.closest('button, a, input, select, textarea, [contenteditable="true"], .dash-layout-handle, .dash-layout-menu-btn, .jp-popover')) return;
  const screenEl = card.closest('.screen');
  const screenId = screenEl ? screenEl.id : null;
  if (!screenId || !JP_WIDGET_SCREENS[screenId] || screenId !== dashLayoutActiveScreenId()) return;
  if (!dashLayoutIsMovable(card)) return;
  dashLayoutPress = {
    card, screenId, active: false,
    pointerId: event.pointerId, startX: event.clientX, startY: event.clientY,
    lastEvent: event,
    timer: setTimeout(dashLayoutPressFire, DASH_LAYOUT_LONGPRESS_MS)
  };
  card.classList.add('dash-layout-pressing');
  document.addEventListener('pointermove', dashLayoutPressOnMove);
  document.addEventListener('pointerup', dashLayoutPressOnUp);
  document.addEventListener('pointercancel', dashLayoutPressOnUp);
  document.addEventListener('pointerdown', dashLayoutPressOnSecondPointer, true);
  // Guard nativo {passive:false}: antes do disparo NÃO chama preventDefault —
  // o scroll segue livre (e o pointercancel resultante limpa o press). Depois
  // do disparo, preventDefault impede o navegador de roubar o gesto.
  document.addEventListener('touchmove', dashLayoutPressTouchGuard, { passive: false });
  document.addEventListener('contextmenu', dashLayoutPressOnContextMenu, true);
  window.addEventListener('scroll', dashLayoutPressOnScroll, true);
}

function dashLayoutPressOnMove(event) {
  const p = dashLayoutPress; if (!p || event.pointerId !== p.pointerId) return;
  p.lastEvent = event;
  if (p.active) return; // arraste já entregue ao motor
  if (Math.hypot(event.clientX - p.startX, event.clientY - p.startY) > DASH_LAYOUT_LONGPRESS_SLOP_PX) dashLayoutPressClear();
}
function dashLayoutPressOnUp(event) {
  const p = dashLayoutPress; if (!p || event.pointerId !== p.pointerId) return;
  dashLayoutPressClear(); // o drop em si é do motor (listener próprio no mesmo evento)
}
function dashLayoutPressOnSecondPointer(event) {
  const p = dashLayoutPress; if (!p || p.active || event.pointerId === p.pointerId) return;
  dashLayoutPressClear(); // segundo dedo antes do disparo = pinça/zoom, não intenção de arrastar
}
function dashLayoutPressTouchGuard(event) {
  const p = dashLayoutPress; if (p && p.active && event.cancelable) event.preventDefault();
}
function dashLayoutPressOnContextMenu(event) {
  if (dashLayoutPress) { event.preventDefault(); event.stopPropagation(); }
}
function dashLayoutPressOnScroll() {
  const p = dashLayoutPress; if (p && !p.active) dashLayoutPressClear();
}

// Sair tocando o vazio: clique em área vazia da tela ativa (fora de qualquer
// card, controle, barra ou popover) encerra a sessão pelo MESMO Concluir
// transacional do botão — valida e salva os rascunhos; descartar continua
// sendo ação explícita do Cancelar tudo. Convenção de plataforma (reordenar
// ícones no iOS: tocar fora mantém o arranjo); sair descartando em toque
// acidental perderia trabalho silenciosamente.
// Registrado em CAPTURE para enxergar um popover ainda aberto — o listener
// que fecha popovers roda no bubbling e o anularia antes; com popover aberto,
// o primeiro toque no vazio só fecha o popover (dismissão em duas etapas).
function dashLayoutOnBackdropClick(event) {
  if (!dashLayoutState.editing || dashLayoutState.drag) return;
  if (dashLayoutState.openPopover) return;
  if (dashLayoutPress) return;
  if (Date.now() - dashLayoutState.lastDragEndAt < 400) return; // clique residual do drop
  const screenEl = event.target.closest('.screen');
  if (!screenEl || !screenEl.classList.contains('active')) return; // nav/cabeçalho/barra ficam de fora
  if (event.target.closest('[data-layout-card], button, a, input, select, textarea, .jp-popover, #dashLayoutBar')) return;
  dashLayoutFinish();
}

/* ======================= LIGAÇÕES ======================= */

function initDashboardLayout() {
  dashLayoutBoot();

  const customizeBtn = document.getElementById('dashLayoutCustomizeBtn');
  if (customizeBtn) customizeBtn.addEventListener('click', () => {
    if (!dashLayoutEnabled()) return;
    // Fecha Configurações e mantém a aba atual — a sessão global inicia na
    // tela operacional que já estava por trás do modal, mesmo que ela (ex.:
    // Motor de Lote) não tenha nenhum widget acionável: isso não impede mais
    // a sessão de começar, já que as outras 6 telas têm blocos
    // personalizáveis (regra antiga de bloqueio removida por pedido).
    if (typeof closeSettingsModal === 'function') closeSettingsModal();
    dashLayoutEnterEdit();
  });
  const settingsResetBtn = document.getElementById('dashLayoutResetBtn');
  if (settingsResetBtn) settingsResetBtn.addEventListener('click', () => { if (dashLayoutEnabled()) dashLayoutRestoreDefaultConfirm(); });
  const settingsResetAllBtn = document.getElementById('dashLayoutResetAllBtn');
  if (settingsResetAllBtn) settingsResetAllBtn.addEventListener('click', () => { if (dashLayoutEnabled()) dashLayoutRestoreAllConfirm(); });

  // Toque longo em card móvel → arrasto direto (delegado; um único listener).
  document.addEventListener('pointerdown', dashLayoutOnCardPointerDown);
  // Toque no vazio da tela ativa → Concluir (capture: ver comentário da função).
  document.addEventListener('click', dashLayoutOnBackdropClick, true);

  const cancelAllBtn = document.getElementById('dashLayoutCancelBtn');
  if (cancelAllBtn) cancelAllBtn.addEventListener('click', dashLayoutCancelAll);
  const restoreBtn = document.getElementById('dashLayoutRestoreBtn');
  if (restoreBtn) restoreBtn.addEventListener('click', dashLayoutRestoreDefaultConfirm);
  const restoreAllBarBtn = document.getElementById('dashLayoutRestoreAllBarBtn');
  if (restoreAllBarBtn) restoreAllBarBtn.addEventListener('click', dashLayoutRestoreAllConfirm);
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

  // Trocar de tela durante uma sessão global de edição: NUNCA cancela, NUNCA
  // salva, NUNCA restaura, NUNCA encerra a sessão — só fecha o popover, move
  // `activeScreenId` e redecora (dashLayoutSetActiveScreen). Os rascunhos de
  // todas as telas ficam intactos no próprio DOM. Fora de uma sessão, só
  // fecha popover, como sempre foi. Mesmo padrão de wrap-guardado já usado
  // por 10-dashboard-immersive.js (não substitui a função, envolve).
  if (typeof navigateToScreen === 'function' && !navigateToScreen.__layoutWrapped) {
    const original = navigateToScreen;
    navigateToScreen = function (target) {
      const wasEditing = dashLayoutState.editing;
      original(target);
      if (wasEditing) {
        const newScreenId = dashLayoutActiveScreenId();
        if (newScreenId) dashLayoutSetActiveScreen(newScreenId); // null = destino não trocou .screen.active (ex.: 'config')
      } else {
        dashLayoutClosePopover({ returnFocus: false });
      }
    };
    navigateToScreen.__layoutWrapped = true;
  }

  // beforeunload: só avisa quando há sessão global aberta E pelo menos uma
  // alteração real pendente — nunca com a sessão fechada, nunca sem nenhuma
  // tela em dirtyScreens. Um único listener (initDashboardLayout roda uma
  // vez só); o navegador usa seu próprio texto genérico de confirmação —
  // não é um confirm()/alert() customizado, então não duplica a
  // confirmação já existente em "Cancelar tudo".
  window.addEventListener('beforeunload', event => {
    if (dashLayoutState.editing && dashLayoutState.dirtyScreens && dashLayoutState.dirtyScreens.size > 0) {
      event.preventDefault();
      event.returnValue = '';
    }
  });
}
initDashboardLayout();

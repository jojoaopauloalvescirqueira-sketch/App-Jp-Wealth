// ============ DASHBOARD IMERSIVO (N1 — apresentação) ============
// Camada estritamente de interface: modo imersivo, carrossel do hero, navegação
// interna por seções e menu mobile. Nenhum cálculo, fórmula, persistência ou
// estado financeiro é derivado aqui — os valores continuam vindo dos
// renderizadores existentes, que escrevem nos mesmos IDs.
//
// O estado do modo imersivo vive apenas no atributo data-active-screen do <html>.
// Não é persistido, não entra em backup e não toca o schema.

const DASH_SLIDES = 3;
const dashUI = { slide: 0, menuOpen: false, menuOpener: null };

function dashEl(sel, root) { return (root || document).querySelector(sel); }
function dashAll(sel, root) { return [...(root || document).querySelectorAll(sel)]; }

/* ---------- Modo imersivo ---------- */
// Reflete no <html> qual tela está ativa. Lê o DOM já atualizado pela navegação
// existente; não decide navegação nem mantém um segundo mecanismo de troca.
function syncActiveScreen() {
  const active = dashEl('.screen.active');
  document.documentElement.dataset.activeScreen = active ? active.id : '';
  if (active && active.id !== 'dash') closeDashMenu({ restoreFocus: false });
}

/* ---------- Carrossel do hero ---------- */
function renderDashSlides(focusSlide) {
  const slides = dashAll('[data-slide]');
  if (!slides.length) return;
  slides.forEach((slide, i) => {
    const on = i === dashUI.slide;
    slide.hidden = !on;
    slide.inert = !on;
    slide.setAttribute('aria-hidden', String(!on));
  });
  dashAll('[data-dash-dot]').forEach((dot, i) => {
    const on = i === dashUI.slide;
    dot.classList.toggle('active', on);
    dot.setAttribute('aria-current', on ? 'true' : 'false');
  });
  const live = dashEl('[data-dash-carousel-status]');
  if (live) live.textContent = `Slide ${dashUI.slide + 1} de ${DASH_SLIDES}`;
  if (focusSlide) {
    const target = slides[dashUI.slide];
    const first = target && target.querySelector('button, [href], input, select, textarea');
    if (first) first.focus();
  }
}
function goToDashSlide(index, options) {
  const total = dashAll('[data-slide]').length || DASH_SLIDES;
  dashUI.slide = (index + total) % total;
  renderDashSlides(options && options.focus);
}

/* ---------- Navegação interna por seções ---------- */
// Alguns destinos do menu vivem em slides do hero, não em seções próprias:
// "Risco" é o slide 2 do carrossel. Nesses casos o link leva ao hero e troca o
// slide, para que nenhum item do menu aponte para um destino inexistente.
const DASH_SLIDE_TARGETS = { visao: 0, risco: 1 };

function scrollToDashSection(name) {
  const slide = DASH_SLIDE_TARGETS[name];
  const target = dashEl(`[data-dash-section="${name}"]`) || (slide !== undefined ? dashEl('[data-dash-hero]') : null);
  if (!target) return;
  if (slide !== undefined) goToDashSlide(slide);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  dashAll('[data-dash-link]').forEach(link => {
    link.setAttribute('aria-current', link.dataset.dashLink === name ? 'true' : 'false');
  });
}

/* ---------- Menu mobile do header imersivo ---------- */
function openDashMenu(opener) {
  const menu = dashEl('[data-dash-menu]');
  if (!menu) return;
  dashUI.menuOpen = true;
  dashUI.menuOpener = opener || dashEl('[data-dash-menu-toggle]');
  menu.hidden = false;
  const toggle = dashEl('[data-dash-menu-toggle]');
  if (toggle) toggle.setAttribute('aria-expanded', 'true');
  const first = menu.querySelector('button, [href]');
  if (first) first.focus();
}
function closeDashMenu(options) {
  const menu = dashEl('[data-dash-menu]');
  if (!menu || !dashUI.menuOpen) return;
  dashUI.menuOpen = false;
  menu.hidden = true;
  const toggle = dashEl('[data-dash-menu-toggle]');
  if (toggle) toggle.setAttribute('aria-expanded', 'false');
  const opener = dashUI.menuOpener;
  dashUI.menuOpener = null;
  if (!options || options.restoreFocus !== false) {
    if (opener && document.contains(opener)) opener.focus();
  }
}

/* ---------- Ligação com a navegação existente ---------- */
// Envolve a função real de troca de telas em vez de recriá-la: a navegação
// continua sendo a do aplicativo, e o modo imersivo apenas reage a ela.
function initDashboardImmersive() {
  if (typeof navigateToScreen === 'function' && !navigateToScreen.__dashWrapped) {
    const original = navigateToScreen;
    navigateToScreen = function (target) {
      original(target);
      syncActiveScreen();
    };
    navigateToScreen.__dashWrapped = true;
  }
  syncActiveScreen();

  const hero = dashEl('[data-dash-hero]');
  if (hero) {
    hero.addEventListener('click', event => {
      const prev = event.target.closest('[data-carousel-prev]');
      if (prev) { goToDashSlide(dashUI.slide - 1); return; }
      const next = event.target.closest('[data-carousel-next]');
      if (next) { goToDashSlide(dashUI.slide + 1); return; }
      const dot = event.target.closest('[data-dash-dot]');
      if (dot) { goToDashSlide(Number(dot.dataset.dashDot), { focus: true }); }
    });
    hero.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft') { event.preventDefault(); goToDashSlide(dashUI.slide - 1); }
      else if (event.key === 'ArrowRight') { event.preventDefault(); goToDashSlide(dashUI.slide + 1); }
    });
  }

  // Ações reais: a primária reutiliza a navegação existente; a secundária
  // rola para a seção de detalhes dentro do próprio Dashboard.
  document.addEventListener('click', event => {
    const go = event.target.closest('[data-dash-go]');
    if (go) { navigateToScreen(go.dataset.dashGo); return; }
    const scroll = event.target.closest('[data-dash-scroll]');
    if (scroll) { scrollToDashSection(scroll.dataset.dashScroll); return; }
    const link = event.target.closest('[data-dash-link]');
    if (link) { scrollToDashSection(link.dataset.dashLink); closeDashMenu({ restoreFocus: false }); return; }
    const toggle = event.target.closest('[data-dash-menu-toggle]');
    if (toggle) { dashUI.menuOpen ? closeDashMenu() : openDashMenu(toggle); }
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && dashUI.menuOpen) { event.preventDefault(); closeDashMenu(); }
  });

  renderDashSlides(false);
}
initDashboardImmersive();

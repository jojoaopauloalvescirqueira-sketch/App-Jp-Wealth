// ============ ESTILO DA NAVEGAÇÃO (KineticNav | Floating Pill Nav | Clássica) ============
// Preferência de APRESENTAÇÃO, no mesmo contrato de jpw_rail, jpw_fs e jpw_expl:
// vive em localStorage (é por navegador, não por base), aplica-se como atributo
// em <html> e é exposta como segmentado na Central. Deliberadamente FORA de S —
// nada aqui entra no backup, no schema ou na migração, e por isso trocar de
// estilo não tem como afetar dado operacional.
//
// Os dois primeiros nomes são os que os autores deram aos componentes de
// referência; a terceira é a barra própria do aplicativo, sem autor externo.
// Ambas as aparências foram reescritas aqui do zero a partir do PADRÃO visual —
// nenhum código de terceiro foi copiado para dentro do projeto.
//
// Quem nunca escolheu começa por NAV_STYLE_DEFAULT. Valor desconhecido também
// cai nele, para que uma chave corrompida à mão não deixe a navegação sem
// estilo. O padrão é declarado UMA vez aqui: a Central lê esta constante para
// dizer qual é, em vez de repetir o nome em outro lugar e arriscar divergir.
const NAV_STYLE_KEY='jpw_nav';
const NAV_STYLES=['kinetic','pill','classic'];
const NAV_STYLE_DEFAULT='pill';
function navStyleValue(){
  let v=null;
  try{ v=localStorage.getItem(NAV_STYLE_KEY); }catch(e){}
  return NAV_STYLES.includes(v)?v:NAV_STYLE_DEFAULT;
}
function applyNavStyle(){
  document.documentElement.setAttribute('data-nav-style', navStyleValue());
  positionNavPill();
}
// O destaque é um elemento único que se desloca até a aba ativa. Medimos por
// offsetLeft/offsetWidth, e não por getBoundingClientRect, justamente porque o
// #nav horizontal é um contêiner com overflow-x:auto: offsetLeft é posição de
// layout dentro do padding box e não muda quando a barra é rolada, que é o que
// mantém o destaque colado na aba certa em qualquer posição de rolagem.
// Aplica a MESMA geometria ao destaque e ao brilho especular. Quem produz o
// atraso entre os dois é a folha de estilo (durações e delay diferentes), não
// este código: aqui os dois recebem o mesmo alvo no mesmo instante.
function navPillApplyGeometry(alvo){
  const nav=document.getElementById('nav'); if(!nav) return;
  [document.getElementById('navPillIndicator'), document.getElementById('navPillSpecular')].forEach(el=>{
    if(!el || getComputedStyle(el).display==='none') return;
    el.style.opacity='';
    el.style.width=alvo.offsetWidth+'px';
    el.style.height=alvo.offsetHeight+'px';
    el.style.transform=`translate(${alvo.offsetLeft}px, ${alvo.offsetTop}px)`;
    // A primeira medição não pode ser animada: sem isto os elementos entram
    // deslizando do canto a cada carga da página.
    if(!el.classList.contains('is-ready')) requestAnimationFrame(()=>el.classList.add('is-ready'));
  });
}
function positionNavPill(){
  const nav=document.getElementById('nav'), pill=document.getElementById('navPillIndicator');
  if(!nav||!pill) return;
  const spec=document.getElementById('navPillSpecular');
  const active=nav.querySelector('.tab.active');
  // Em modo clássico, no rail vertical do Dashboard e na gaveta mobile o CSS
  // deixa o destaque em display:none — medir ali devolveria zero e faria o
  // elemento piscar ao voltar para a barra horizontal.
  //
  // A ausência de aba ativa não é hipótese teórica: navigateToScreen() chamado
  // com STRING (CTAs, Ações Rápidas) remove .active de todas as abas e não
  // repõe em nenhuma. Nesse estado o destaque é escondido, em vez de ficar
  // marcando a aba anterior, que seria informação falsa.
  if(getComputedStyle(pill).display==='none'){
    pill.classList.remove('is-ready');
    if(spec) spec.classList.remove('is-ready');
    return;
  }
  if(!active){
    pill.style.opacity='0';
    if(spec) spec.style.opacity='0';
    return;
  }
  navPillApplyGeometry(active);
}
// Remedição nos três eventos que mudam a largura das abas sem trocar a tela:
// redimensionamento, escala de fonte (--fs-scale altera o padding e o texto) e
// recolher/expandir o rail. A troca de tela é tratada em navigateToScreen().
// Mede JÁ e agenda uma segunda passada. A síncrona é a que garante o resultado
// quando requestAnimationFrame não dispara — aba em segundo plano, janela
// oculta, renderização estrangulada. A agendada corrige o caso oposto: quando a
// medição síncrona pega o layout antes de a troca de classe repercutir.
function scheduleNavPill(){
  positionNavPill();
  requestAnimationFrame(positionNavPill);
}
function renderNavStyleSeg(){
  const v=navStyleValue();
  document.querySelectorAll('#navStyleSeg button').forEach(b=>{
    b.classList.toggle('on', b.dataset.navVal===v);
    // Marca de "padrão do sistema". É decorativa: quem carrega a informação em
    // texto é a legenda abaixo, para leitor de tela e para quem não distingue
    // a marca visual.
    b.classList.toggle('is-default', b.dataset.navVal===NAV_STYLE_DEFAULT);
  });
  // O nome do padrão vem do rótulo do próprio botão — a string existe uma vez
  // só, no HTML. Trocar NAV_STYLE_DEFAULT reescreve esta legenda sozinho.
  const nota=document.getElementById('navStyleDefaultNote');
  if(nota){
    const btn=document.querySelector(`#navStyleSeg button[data-nav-val="${NAV_STYLE_DEFAULT}"]`);
    const nome=btn?btn.textContent.trim():NAV_STYLE_DEFAULT;
    const usandoPadrao = v===NAV_STYLE_DEFAULT;
    nota.textContent = usandoPadrao
      ? `Padrão do sistema: ${nome} — é o que você está usando, e o que aparece para quem abre o aplicativo pela primeira vez.`
      : `Padrão do sistema: ${nome} — é o que aparece para quem abre o aplicativo pela primeira vez. A sua escolha atual é outra e vale só neste navegador.`;
  }
}
function bindNavStyleSeg(){
  document.querySelectorAll('#navStyleSeg button').forEach(b=>b.addEventListener('click',()=>{
    const v=NAV_STYLES.includes(b.dataset.navVal)?b.dataset.navVal:'kinetic';
    try{ localStorage.setItem(NAV_STYLE_KEY, v); }catch(e){}
    applyNavStyle(); renderNavStyleSeg(); scheduleNavPill();
  }));
}
// ---- Magnetismo do KineticNav ----
// No componente de referência o destaque acompanha o item sob o cursor e volta
// para o ativo quando o ponteiro sai. Aqui isso é feito movendo o MESMO
// elemento de destaque — não há segundo objeto —, então a volta usa a mesma
// medição de sempre. Só vale no estilo kinetic; nos outros o hover não desloca
// nada. Ponteiros grossos (toque) não têm hover: a mídia coarse fica de fora
// para o destaque não perseguir o dedo.
function bindNavMagnetics(){
  const nav=document.getElementById('nav');
  if(!nav) return;
  const fino=window.matchMedia('(hover:hover) and (pointer:fine)');
  const alvoValido=el=>el && el.classList && el.classList.contains('tab');
  nav.addEventListener('mouseover', e=>{
    if(navStyleValue()!=='kinetic' || !fino.matches) return;
    const alvo=e.target.closest && e.target.closest('.tab');
    if(!alvoValido(alvo)) return;
    const pill=document.getElementById('navPillIndicator');
    if(!pill || getComputedStyle(pill).display==='none') return;
    navPillApplyGeometry(alvo);
  });
  // Volta ao ativo ao sair da barra inteira (e não de cada aba), senão o
  // destaque piscaria a cada passagem de uma aba para a vizinha.
  nav.addEventListener('mouseleave', ()=>{ if(navStyleValue()==='kinetic') positionNavPill(); });
}
bindNavMagnetics();
window.addEventListener('resize', scheduleNavPill);
// O shell é decidido DEPOIS do boot: quando applyNavStyle() roda pela primeira
// vez, data-shell ainda não existe, o seletor da pílula não casa, o destaque
// está display:none e a medição sai vazia — o destaque só apareceria na
// primeira troca de aba. Observar os atributos de <html> cobre isso e mais três
// casos pelo mesmo mecanismo: troca de shell em tempo de execução, mudança de
// tela ativa e recolher/expandir o rail, que alteram a largura das abas.
new MutationObserver(scheduleNavPill).observe(document.documentElement, {
  attributes:true,
  attributeFilter:['data-shell','data-active-screen','data-nav-style','data-rail','data-ui-version'],
});
// Sinal decisivo para a primeira medição: a GEOMETRIA da barra. No boot as abas
// ainda medem zero — o shell só realoca o #nav para dentro da topbar depois —, e
// essa realocação não mexe em nenhum atributo de <html>, então o observador
// acima não a enxerga. O ResizeObserver enxerga, e de quebra cobre pelo mesmo
// mecanismo tudo que altera a largura das abas: escala de fonte, rail e
// redimensionamento da janela.
if(typeof ResizeObserver==='function'){
  const nav=document.getElementById('nav');
  if(nav) new ResizeObserver(()=>positionNavPill()).observe(nav);
}
// Rede de segurança da PRIMEIRA medição. ResizeObserver e requestAnimationFrame
// são entregues no ciclo de quadro: numa aba em segundo plano, ou com a
// renderização estrangulada, eles não chegam, e o destaque ficaria sem medida
// até a primeira troca de aba. `load` e `setTimeout` não dependem de quadro.
window.addEventListener('load', ()=>positionNavPill());
setTimeout(positionNavPill, 0);
setTimeout(positionNavPill, 300);

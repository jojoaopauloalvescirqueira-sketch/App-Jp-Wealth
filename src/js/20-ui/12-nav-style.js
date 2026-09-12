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
const NAV_STYLE_DEFAULT='classic';
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
// offsetLeft/offsetTop são posições no padding box de #nav; a geometria
// permanece relativa ao mesmo contêiner na lateral aberta, compacta e mobile.
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
  // Em modo clássico o CSS deixa o destaque em display:none. Não medir
  // esse estado evita geometria vazia ao selecionar outro estilo.
  //
  // A ausência de aba ativa continua tratada defensivamente para monólitos
  // reduzidos e DOM incompleto. No contrato NAV-01 o resolver valida o destino
  // antes de trocar classes e todo destino físico legado herda um primário.
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
  document.querySelectorAll('#navStyleSeg button').forEach(b=>{if(b.dataset.navBound)return;b.dataset.navBound='true';b.addEventListener('click',()=>{
    const v=NAV_STYLES.includes(b.dataset.navVal)?b.dataset.navVal:'kinetic';
    const message=document.getElementById('navStyleStatus');
    try{ localStorage.setItem(NAV_STYLE_KEY, v); }catch(e){
      if(message)message.textContent='Não foi possível salvar o estilo de navegação neste navegador.';
      return;
    }
    if(message)message.textContent='';
    applyNavStyle(); renderNavStyleSeg(); scheduleNavPill();
  });});
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
// podem mudar de tamanho enquanto o shell monta os slots contextuais, e
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

// Composição por navegador. A persistência pertence aos controles de
// apresentação; o shell recebe apenas a escolha validada para montar o DOM.
const NAV_LAYOUT_KEY='jpw_nav_layout';
const NAV_LAYOUTS=['sidebar','topbar'];
function renderNavLayoutChoice(){
  document.querySelectorAll('#navLayoutSeg [data-nav-layout]').forEach(btn=>{
    const on=btn.dataset.navLayout===document.documentElement.getAttribute('data-navigation');
    btn.classList.toggle('on',on);btn.setAttribute('aria-pressed',String(on));
  });
}
function initNavLayoutChoice(){
  let value=null,message='';
  try{value=localStorage.getItem(NAV_LAYOUT_KEY);
    if(value!==null&&!NAV_LAYOUTS.includes(value))message='Preferência não reconhecida. Menu lateral exibido; a escolha salva foi preservada.';
  }catch(e){message='Não foi possível ler a preferência. Menu lateral exibido sem alterar a escolha salva.';}
  mountNavigationLayout(NAV_LAYOUTS.includes(value)?value:'sidebar');
  const status=document.getElementById('navLayoutStatus');if(status)status.textContent=message;
  const seg=document.getElementById('navLayoutSeg');if(!seg)return;
  seg.addEventListener('click',event=>{
    const btn=event.target.closest('[data-nav-layout]');if(!btn)return;
    const value=btn.dataset.navLayout;if(!NAV_LAYOUTS.includes(value))return;
    try{localStorage.setItem(NAV_LAYOUT_KEY,value);}
    catch(e){if(status)status.textContent='Não foi possível salvar a escolha. A interface anterior foi mantida.';return;}
    mountNavigationLayout(value);
    if(status)status.textContent=(value==='sidebar'?'Menu lateral':'Barra superior')+' salvo neste navegador.';
  });
}

// Ordem visual dos mesmos primários: preferência por navegador, fora de S e
// do envelope de widgets. A lista usa identidades, nunca rótulos ou rotas novas.
const NAV_ORDER_KEY='jpw_nav_order';
const NAV_ORDER_DEFAULT=Object.freeze(['dashboard','research','forex','personal-finance','alladin']);
const navOrderState={confirmed:[],draft:[],raw:null,editing:false,blocked:null,note:'',restoreRequested:false};
function navOrderValid(value){
  return Array.isArray(value)&&value.length===NAV_ORDER_DEFAULT.length&&
    new Set(value).size===value.length&&value.every(id=>NAV_ORDER_DEFAULT.includes(id));
}
function navOrderDirty(){return navOrderState.draft.join('|')!==navOrderState.confirmed.join('|')||
  navOrderState.restoreRequested&&navOrderState.raw!==JSON.stringify(navOrderState.draft);}
function navOrderRead(){
  let raw;
  try{raw=localStorage.getItem(NAV_ORDER_KEY);}
  catch(e){return {raw:null,order:[...NAV_ORDER_DEFAULT],blocked:'read',note:'Não foi possível ler a ordem salva. O padrão é exibido sem alterar a preferência; recarregue para tentar a leitura novamente.'};}
  let order=null;
  if(raw!==null){try{order=JSON.parse(raw);}catch(e){}}
  const valid=navOrderValid(order);
  return {raw,order:valid?order:[...NAV_ORDER_DEFAULT],blocked:null,
    note:raw!==null&&!valid?'Ordem salva não reconhecida. O padrão é exibido; a preferência original permanece intacta até você salvar uma nova ordem.':''};
}
function applyNavOrder(order){
  if(!navOrderValid(order))return;
  const nav=document.getElementById('nav');if(!nav)return;
  // Mantém nós, listeners, foco e identidades. O shell recoloca seu único N2
  // junto do expansor ativo; não resolve rota nem renderiza domínio.
  const focused=document.activeElement;
  const buttons=new Map([...nav.querySelectorAll(':scope > .tab[data-primary]')].map(btn=>[btn.dataset.primary,btn]));
  if(order.some(id=>!buttons.has(id)))return;
  order.forEach((id,index)=>{
    const btn=buttons.get(id),surface=btn.id.replace('NavTrigger','');
    const number=btn.querySelector('.n');if(number)number.textContent=String(index+1).padStart(2,'0');
    nav.append(btn);
    const expander=nav.querySelector('[data-nav-expand="'+surface+'"]');
    if(expander)nav.append(expander);
  });
  if(typeof syncNavSubState==='function')syncNavSubState();
  if(focused&&nav.contains(focused)&&document.activeElement!==focused)focused.focus({preventScroll:true});
  scheduleNavPill();
}
function renderNavOrderEditor(message){
  const list=document.getElementById('navOrderList');if(!list)return;
  const focused=document.activeElement;
  const focusId=focused?.closest('[data-nav-order-id]')?.dataset.navOrderId;
  const focusDirection=focused?.dataset.navOrderMove;
  const rows=navOrderState.draft.map((id,index)=>{
    const label=document.querySelector('#nav > .tab[data-primary="'+id+'"] .lbl')?.textContent.trim()||id;
    const row=document.createElement('li');row.dataset.navOrderId=id;
    const text=document.createElement('span');text.textContent=label;row.append(text);
    [['up','Subir'],['down','Descer']].forEach(([direction,verb])=>{
      const button=document.createElement('button');button.type='button';button.className='reset-btn';button.dataset.navOrderMove=direction;
      button.textContent=direction==='up'?'↑':'↓';button.setAttribute('aria-label',verb+' '+label);
      button.disabled=!!navOrderState.blocked||(direction==='up'?index===0:index===navOrderState.draft.length-1);
      row.append(button);
    });
    return row;
  });
  list.replaceChildren(...rows);
  const dirty=navOrderDirty();
  document.getElementById('navOrderSave').disabled=!!navOrderState.blocked||!dirty;
  document.getElementById('navOrderReset').disabled=!!navOrderState.blocked;
  document.getElementById('navOrderCancel').disabled=navOrderState.blocked==='unknown'||(!dirty&&navOrderState.blocked!=='conflict');
  const status=document.getElementById('navOrderStatus');
  if(status)status.textContent=message===undefined?navOrderState.note:message;
  if(focusId&&focusDirection){
    const row=list.querySelector('[data-nav-order-id="'+focusId+'"]');
    const same=row?.querySelector('[data-nav-order-move="'+focusDirection+'"]');
    (same&&!same.disabled?same:row?.querySelector('button:not([disabled])'))?.focus({preventScroll:true});
  }
}
function beginNavOrderPreview(){
  if(navOrderState.editing||navOrderState.blocked==='unknown')return;
  const read=navOrderRead();
  Object.assign(navOrderState,{confirmed:[...read.order],draft:[...read.order],raw:read.raw,
    blocked:read.blocked,note:read.note,editing:true,restoreRequested:false});
  applyNavOrder(read.order);renderNavOrderEditor();
}
function cancelNavOrderPreview(){
  if(navOrderState.blocked==='unknown')return;
  if(navOrderState.blocked==='conflict'){
    navOrderState.editing=false;beginNavOrderPreview();
    // A releitura resolve a prévia anterior; não mantém uma sessão aberta
    // quando Cancelar é chamado pelo fechamento da Central.
    navOrderState.editing=false;
    return;
  }
  navOrderState.draft=[...navOrderState.confirmed];navOrderState.editing=false;navOrderState.restoreRequested=false;
  applyNavOrder(navOrderState.confirmed);renderNavOrderEditor(navOrderState.note||'Prévia cancelada. A ordem salva foi preservada.');
}
function saveNavOrderPreview(){
  if(navOrderState.blocked||!navOrderDirty()||!navOrderValid(navOrderState.draft))return;
  // Guarda da própria preferência; nunca usa save() ou desbloqueia a base.
  let before;
  try{before=localStorage.getItem(NAV_ORDER_KEY);}
  catch(e){navOrderState.blocked='read';renderNavOrderEditor('Não foi possível conferir a ordem salva. Nenhuma gravação foi tentada; recarregue antes de salvar.');return;}
  if(before!==navOrderState.raw){
    navOrderState.blocked='conflict';
    renderNavOrderEditor('A ordem salva mudou em outra ação ou aba. Nada foi gravado. Cancele a prévia para conferir a preferência atual.');return;
  }
  const payload=JSON.stringify(navOrderState.draft);
  try{localStorage.setItem(NAV_ORDER_KEY,payload);}catch(e){/* O read-back distingue recusa de desfecho desconhecido. */}
  let after;
  try{after=localStorage.getItem(NAV_ORDER_KEY);}catch(e){}
  if(after===payload){
    navOrderState.raw=payload;navOrderState.confirmed=[...navOrderState.draft];navOrderState.editing=false;navOrderState.note='';navOrderState.restoreRequested=false;
    renderNavOrderEditor('Ordem salva neste navegador.');return;
  }
  if(after===before){
    renderNavOrderEditor('Não foi possível salvar. Esta é uma prévia não salva; seus ajustes continuam nesta sessão para cancelar ou tentar novamente.');return;
  }
  navOrderState.blocked='unknown';
  renderNavOrderEditor('Não foi possível determinar o resultado da gravação. A prévia foi preservada e novas alterações estão bloqueadas. Recarregue para conferir a ordem armazenada antes de continuar.');
}
function initNavOrderChoice(){
  const editor=document.getElementById('navOrderEditor');if(!editor||editor.dataset.bound)return;
  editor.dataset.bound='true';beginNavOrderPreview();navOrderState.editing=false;
  editor.addEventListener('click',event=>{
    const move=event.target.closest('[data-nav-order-move]');
    if(move&&!move.disabled&&!navOrderState.blocked){
      if(!navOrderState.editing)beginNavOrderPreview();
      if(navOrderState.blocked)return;
      const id=move.closest('[data-nav-order-id]').dataset.navOrderId,index=navOrderState.draft.indexOf(id);
      const next=index+(move.dataset.navOrderMove==='up'?-1:1);
      if(index<0||next<0||next>=navOrderState.draft.length)return;
      [navOrderState.draft[index],navOrderState.draft[next]]=[navOrderState.draft[next],navOrderState.draft[index]];
      applyNavOrder(navOrderState.draft);renderNavOrderEditor('Prévia não salva. Salve a ordem ou cancele para manter a anterior.');return;
    }
    if(event.target.closest('#navOrderSave'))saveNavOrderPreview();
    else if(event.target.closest('#navOrderCancel'))cancelNavOrderPreview();
    else if(event.target.closest('#navOrderReset')&&!navOrderState.blocked){
      if(!navOrderState.editing)beginNavOrderPreview();
      if(navOrderState.blocked)return;
      navOrderState.draft=[...NAV_ORDER_DEFAULT];navOrderState.restoreRequested=true;applyNavOrder(navOrderState.draft);
      renderNavOrderEditor('Ordem padrão em prévia. Somente a ordem será alterada ao salvar.');
    }
  });
}

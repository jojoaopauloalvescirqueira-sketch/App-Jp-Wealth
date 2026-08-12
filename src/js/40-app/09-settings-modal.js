// ============ CENTRAL DE CONFIGURAÇÕES (N1) ============
// Mantém os controles legados no mesmo DOM: apenas os transporta enquanto a central está aberta.
// Arquitetura de navegação: categorias declarativas na sidebar (algumas são grupos com subpáginas,
// 'general' e 'about' são páginas diretas). Todas as páginas — grupo ou folha — são registradas
// como [data-settings-panel] e alternadas por 'hidden', preservando o contrato já usado pelos
// testes (activateSettingsCategory(id) continua tornando o painel 'id' visível).

const SETTINGS_GROUPS=[
  {id:'general', label:'Geral', icon:'general'},
  {id:'appearance-interface', label:'Aparência e Interface', desc:'Tema, ícone, organização visual e editor.', icon:'appearance', children:['appearance','interface','editor']},
  {id:'method-governance', label:'Método e Governança', desc:'Estatuto operacional, parâmetros e calibração.', icon:'governance', children:['statute','parameters']},
  {id:'operations', label:'Operação', desc:'Parâmetros do ciclo, Motor de Lote e Checklist pré-trade.', icon:'operations', children:['tool-params','tool-motor','tool-check']},
  {id:'knowledge', label:'Conhecimento', desc:'Material educacional e referências do método.', icon:'knowledge', children:['educational']},
  {id:'probability-lab', label:'Laboratório de Probabilidade', desc:'Experimentos locais de física e estatística, isolados do motor financeiro.', icon:'probability', children:['galton-board']},
  {id:'data-security', label:'Dados e Segurança', desc:'Backup, recuperação, armazenamento e integridade.', icon:'data', children:['backup','storage']},
  {id:'about', label:'Sobre', icon:'about'}
];
const SETTINGS_LEAVES={
  about:{label:'Sobre', group:null, terms:['sobre','versão','build','offline','armazenamento','documentação','changelog']},
  appearance:{label:'Aparência', group:'appearance-interface', desc:'Tema e ícone do aplicativo.', terms:['tema','aparência','ícone','paleta','contraste']},
  interface:{label:'Interface', group:'appearance-interface', desc:'Tamanho do texto e instruções do sistema.', terms:['interface','fonte','tamanho','tipografia','sidebar','barra lateral','ajuda','instruções']},
  editor:{label:'Editor', group:'appearance-interface', desc:'Preferências de edição.', terms:['editor']},
  educational:{label:'Centro Educacional', group:'knowledge', desc:'Fundamentos, glossário e perguntas frequentes.', terms:['educacional','centro educacional','forex','pip','spread','glossário','perguntas frequentes']},
  'galton-board':{label:'Galton Board', group:'probability-lab', desc:'Simulador físico de probabilidade e convergência estatística.', terms:['galton','probabilidade','binomial','normal','histograma','estatística','física','seed','convergência','simulação']},
  statute:{label:'Estatuto Operacional', group:'method-governance', desc:'Diretrizes e regras normativas vigentes.', terms:['estatuto','diretrizes','artigos','pdf','governança']},
  parameters:{label:'Parâmetros e Calibração', group:'method-governance', desc:'Valores, limites, perfis e modelo estatístico.', terms:['parâmetros','calibração','mdd','drawdown','alavancagem','gênese','quarentena','mei']},
  'tool-params':{label:'Parâmetros', group:'operations', desc:'Saldo e ciclo, constantes e a matriz quadrifásica ativa.', terms:['parâmetros','saldo','ciclo','constantes','decisões','matriz','quadrifásica','fases']},
  'tool-motor':{label:'Motor de Lote', group:'operations', desc:'Position sizing com câmbio atualizado e teto por operação.', terms:['motor de lote','position sizing','lote','câmbio','nocional','teto','instrumento','perfis de risco']},
  'tool-check':{label:'Checklist', group:'operations', desc:'Checklist pré-trade e pontuação do filtro.', terms:['checklist','pré-trade','pontuação','filtro','nocuda','setup']},
  backup:{label:'Backup e Recuperação', group:'data-security', desc:'Exportar, importar e restaurar o estado completo.', terms:['backup','exportar','importar','recuperação','reset','limpar','pasta padrão','pasta de armazenamento','sequência de exportação','backup confirmado','reautorizar pasta','alterações desde o backup']},
  storage:{label:'Armazenamento Local', group:'data-security', desc:'Informações sobre os dados salvos neste navegador.', terms:['armazenamento','local','schema','integridade','offline']}
};
const SETTINGS_GROUP_BY_ID=Object.fromEntries(SETTINGS_GROUPS.map(g=>[g.id,g]));

const SETTINGS_ICONS={
  general:'<path d="M4 7h11M19 7h1M4 12h6M14 12h6M4 17h13M21 17h-1"/><circle cx="17" cy="7" r="2"/><circle cx="11" cy="12" r="2"/><circle cx="18" cy="17" r="2"/>',
  appearance:'<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M3 12h2M19 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/>',
  governance:'<path d="M4 19h16"/><path d="M6 19V9l6-4 6 4v10"/><path d="M10 19v-6h4v6"/>',
  operations:'<circle cx="12" cy="12" r="8"/><path d="M12 4v3M12 17v3M4 12h3M17 12h3"/><circle cx="12" cy="12" r="2"/>',
  knowledge:'<path d="M12 6c-1.8-1.2-4.2-1.6-6.5-1v12.5c2.3-.6 4.7-.2 6.5 1 1.8-1.2 4.2-1.6 6.5-1V5c-2.3-.6-4.7-.2-6.5 1Z"/><path d="M12 6v12.5"/>',
  probability:'<path d="M5 20h14M8 20v-4l4-2 4 2v4M12 14V8"/><circle cx="12" cy="5" r="2"/><circle cx="8" cy="11" r="1.5"/><circle cx="16" cy="11" r="1.5"/>',
  data:'<path d="M12 3c4 0 7 1.1 7 2.5S16 8 12 8s-7-1.1-7-2.5S8 3 12 3Z"/><path d="M5 5.5V12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V5.5"/><path d="M5 12v6.5c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V12"/>',
  about:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle cx="12" cy="7.5" r=".2" fill="currentColor" stroke-width="2.4"/>',
  calendar:'<rect x="4" y="5.5" width="16" height="15" rx="2"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/><path d="M8 14h2M14 14h2M8 17.2h2"/>',
  back:'<path d="M14.5 5 7 12l7.5 7"/>',
  forward:'<path d="M9.5 5 17 12l-7.5 7"/>',
  chevron:'<path d="m9 6 6 6-6 6"/>'
};
function settingsIconSvg(name){ return `<svg viewBox="0 0 24 24" aria-hidden="true">${SETTINGS_ICONS[name]||''}</svg>`; }

const settingsState={
  open:false, active:'general', query:'', opener:null, legacyNodes:[], railParent:null, railNext:null,
  suspended:false, subdialogLauncher:null, observer:null, highlightTimer:null,
  navStack:['general'], navIndex:0, mobileListVisible:true
};
window.__settingsModalDebug={opens:0,observerInstances:0,focusTrapActive:false};

function settingsEl(id){ return document.getElementById(id); }
function settingsIsOpen(){ return settingsState.open; }
function settingsEsc(v){ return esc(String(v||'')); }
function settingsLeafLabel(id){ return (SETTINGS_LEAVES[id]&&SETTINGS_LEAVES[id].label) || (SETTINGS_GROUP_BY_ID[id]&&SETTINGS_GROUP_BY_ID[id].label) || id; }
function settingsPageTitleFor(id){
  if(id==='general') return 'Geral';
  if(SETTINGS_GROUP_BY_ID[id]) return SETTINGS_GROUP_BY_ID[id].label;
  return settingsLeafLabel(id);
}
function settingsTopLevelFor(id){
  if(id==='general'||id==='about'||SETTINGS_GROUP_BY_ID[id]) return id;
  const leaf=SETTINGS_LEAVES[id];
  return leaf?leaf.group:'general';
}

function buildSettingsMenu(){
  const menu=settingsEl('settingsMenu'), select=settingsEl('settingsMobileCategory');
  if(!menu||menu.dataset.ready) return;
  SETTINGS_GROUPS.forEach(item=>{
    const button=document.createElement('button');
    button.type='button'; button.className='settings-menu-item'; button.dataset.settingsCategory=item.id;
    button.setAttribute('aria-current','false');
    button.innerHTML=`${settingsIconSvg(item.icon)}<span>${settingsEsc(item.label)}</span>`;
    button.addEventListener('click',()=>settingsNavigateTopLevel(item.id));
    menu.append(button);
    const option=document.createElement('option'); option.value=item.id; option.textContent=item.label; select.append(option);
  });
  select.addEventListener('change',()=>settingsNavigateTopLevel(select.value));
  // Calendário Econômico — AÇÃO de nível superior, não categoria: abre o
  // diálogo compartilhado (17-economic-calendar.js) em um passo, como o
  // requisito pede ("Configurações → Calendário Econômico"). Sem
  // data-settings-category de propósito: não é página navegável, não entra na
  // pilha de navegação nem no <select> mobile (cujo change navega categorias),
  // e a contagem de categorias do contrato de testes permanece intacta. O
  // clique é tratado por delegação em 17-economic-calendar.js (mesmo id que
  // marca o lançador do subdiálogo); aqui só se constrói a linha.
  const launch=document.createElement('button');
  launch.type='button'; launch.id='ecalOpenFromSettingsBtn';
  launch.className='settings-menu-item settings-menu-launch';
  launch.setAttribute('aria-haspopup','dialog');
  launch.innerHTML=`${settingsIconSvg('calendar')}<span>Calendário Econômico</span>${settingsIconSvg('chevron')}`;
  menu.append(launch);
  menu.dataset.ready='true';
}

function createSettingsPanel(id,html){
  const panel=document.createElement('section'); panel.className='settings-panel'; panel.dataset.settingsPanel=id; panel.hidden=true; panel.innerHTML=html; settingsEl('settingsContent').append(panel); return panel;
}

function aboutPanel(){
  const build=typeof JP_WEALTH_BUILD_ID==='string'?JP_WEALTH_BUILD_ID:'não informado';
  return `<div class="settings-about-head"><div class="settings-about-mark" aria-hidden="true">JP</div><h3>JP Wealth Risk Terminal</h3><p class="settings-lead">Ferramenta de gestão, registro e controle de risco. O sistema não fornece sinais, não prevê resultados e não transforma expectativas estatísticas em garantias.</p></div><dl class="settings-facts"><dt>Aplicativo</dt><dd>JP Wealth Risk Terminal</dd><dt>Versão</dt><dd>1 beta</dd><dt>Build</dt><dd><code>${settingsEsc(build)}</code></dd><dt>Armazenamento</dt><dd>Local neste navegador.</dd><dt>Funcionamento</dt><dd>Disponível offline após a instalação completa da aplicação.</dd></dl><div class="settings-links"><a href="docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf" target="_blank" rel="noopener">Estatuto Operacional (PDF)</a><a href="CHANGELOG.md" target="_blank" rel="noopener">Changelog</a><a href="README.md" target="_blank" rel="noopener">Documentação do projeto</a></div><p class="note">Dados técnicos não disponíveis no código vigente não são inferidos nesta tela.</p>`;
}

function educationPanel(){
  const groups=[['comece','Começar por aqui'],['fundamentos','Fundamentos do Forex'],['estrutura','Estrutura do mercado'],['pares','Pares e cotações'],['execucao','Execução e custos'],['risco','Risco e alavancagem'],['historia','História do mercado cambial']];
  return `<p class="settings-lead">Referência local, curta e curada. Não substitui o Estatuto Operacional nem os Parâmetros e Calibração.</p>${groups.map(([key,label])=>`<section class="education-section"><h4>${label}</h4>${EDUCATIONAL_CONTENT.filter(x=>x.category===key).map(educationArticle).join('')}</section>`).join('')}<section class="education-section"><h4>Glossário</h4><div class="education-glossary">${EDUCATIONAL_GLOSSARY.map(term=>`<button type="button" data-education-term="${settingsEsc(term)}">${settingsEsc(term)}</button>`).join('')}</div></section><section class="education-section"><h4>Perguntas frequentes</h4>${EDUCATIONAL_FAQ.map(([q,a],i)=>`<details id="education-faq-${i}"><summary>${settingsEsc(q)}</summary><p>${settingsEsc(a)}</p></details>`).join('')}</section>`;
}
function educationArticle(item){ return `<article class="education-article" id="education-${item.id}" data-education-id="${item.id}"><h5>${settingsEsc(item.title)}</h5><p><b>Definição.</b> ${settingsEsc(item.definition)}</p><p><b>Exemplo simples.</b> ${settingsEsc(item.example)}</p><p><b>Risco ou limitação.</b> ${settingsEsc(item.risk)}</p><p><b>Relação com o JP Wealth.</b> ${settingsEsc(item.jpWealth)}</p></article>`; }

function settingsStorageFacts(){
  const facts=[];
  facts.push(['Tipo de armazenamento','localStorage neste navegador']);
  let readState='Nenhum dado salvo ainda neste navegador';
  try{
    const raw=localStorage.getItem('jpwealth_v9_state');
    if(raw){ JSON.parse(raw); readState='Dado salvo é legível e está em formato JSON válido'; }
  }catch(e){ readState='Dado salvo existe, mas não está em formato JSON válido'; }
  facts.push(['Leitura do estado salvo',readState]);
  if(typeof S!=='undefined'&&S&&Array.isArray(S.accounts)) facts.push(['Contas configuradas',String(S.accounts.length)]);
  const offline=(typeof navigator!=='undefined'&&'serviceWorker' in navigator&&navigator.serviceWorker.controller)?'Ativo neste carregamento':'Não confirmado nesta sessão';
  facts.push(['Funcionamento offline',offline]);
  return facts;
}
function storagePanel(){
  const rows=settingsStorageFacts().map(([k,v])=>`<dt>${settingsEsc(k)}</dt><dd>${settingsEsc(v)}</dd>`).join('');
  return `<p class="settings-lead">Informações que o próprio aplicativo consegue verificar sobre os dados salvos neste navegador. Nenhum valor operacional é exibido aqui.</p><dl class="settings-facts">${rows}</dl><p class="note">Se pouca informação estiver disponível, é porque o sistema não a mede — nenhum dado é inventado nesta tela.</p>`;
}

function settingsNavCard(id,label,desc){
  return `<button type="button" class="settings-nav-card" data-nav-to="${settingsEsc(id)}"><span class="settings-nav-card-text"><span class="settings-nav-card-title">${settingsEsc(label)}</span>${desc?`<span class="settings-nav-card-desc">${settingsEsc(desc)}</span>`:''}</span><span class="settings-nav-card-chev" aria-hidden="true">${settingsIconSvg('chevron')}</span></button>`;
}
function generalPanel(){
  const cards=SETTINGS_GROUPS.filter(g=>g.id!=='general'&&g.id!=='about').map(g=>settingsNavCard(g.id,g.label,g.desc)).join('');
  return `<p class="settings-lead">Gerencie as preferências, o método, os dados e a identidade do JP Wealth.</p><div class="settings-nav-list">${cards}</div>`;
}
function groupPanel(group){
  const cards=group.children.map(leafId=>settingsNavCard(leafId,SETTINGS_LEAVES[leafId].label,SETTINGS_LEAVES[leafId].desc)).join('');
  return `<p class="settings-lead">${settingsEsc(group.desc||'')}</p><div class="settings-nav-list">${cards}</div>`;
}

function buildSettingsContent(){
  const content=settingsEl('settingsContent'); if(!content||content.dataset.ready) return;
  createSettingsPanel('general',generalPanel());
  SETTINGS_GROUPS.filter(g=>g.children).forEach(g=>createSettingsPanel(g.id,groupPanel(g)));
  createSettingsPanel('about',aboutPanel());
  createSettingsPanel('appearance','<p class="settings-lead">Estética e identidade visual. O tema atual continua usando a persistência já existente em <code>S.theme</code>.</p><div data-settings-slot="appearance"></div>');
  createSettingsPanel('interface','<p class="settings-lead">Organização, legibilidade e ajuda contextual. Preferências existentes são preservadas.</p><div class="settings-rail-row"><div><h4>Barra lateral</h4><p class="note">Escolha se a barra de navegação permanece expandida ou recolhida neste navegador.</p></div><div id="settingsRailSlot"></div></div><div data-settings-slot="interface"></div>');
  createSettingsPanel('editor','<p class="settings-lead">Preferências de edição e de apresentação da interface neste navegador.</p><div data-settings-slot="editor"></div>');
  createSettingsPanel('educational',educationPanel());
  createSettingsPanel('galton-board',typeof galtonBoardPanelHTML==='function'?galtonBoardPanelHTML():'<p class="settings-empty" role="alert">O laboratório de probabilidade não pôde ser carregado.</p>');
  createSettingsPanel('statute','<p class="settings-lead">Conteúdo predominantemente de leitura. O documento normativo não é editável nesta central.</p><p class="settings-links"><a href="docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf" target="_blank" rel="noopener">Abrir documento integral (PDF)</a></p><div data-settings-slot="statute"></div>');
  createSettingsPanel('parameters','<p class="settings-lead">Controles existentes, com os valores, unidades, validações e persistência originais.</p><section class="settings-safe-period" id="settingsPeriodSummary"><h4>Período Operacional</h4><p>Os dados do período são mantidos pelo questionário de início. Esta central não mostra valores pessoais ou credenciais.</p><button type="button" class="reset-btn" id="settingsReviewPeriodBtn">Revisar dados do período</button></section><div data-settings-slot="period"></div><div data-settings-slot="parameters"></div>');
  createSettingsPanel('tool-params','<p class="settings-lead">A tela de Parâmetros completa — leituras analíticas com os valores, unidades e persistência originais.</p><div data-settings-slot="tool-params"></div>');
  createSettingsPanel('tool-motor','<p class="settings-lead">O Motor de Lote completo — cálculo de position sizing com o câmbio, tetos e validações originais.</p><div data-settings-slot="tool-motor"></div>');
  createSettingsPanel('tool-check','<p class="settings-lead">O Checklist Pré-Trade completo — mesma pontuação, mesmos critérios, mesma persistência.</p><div data-settings-slot="tool-check"></div>');
  createSettingsPanel('backup','<p class="settings-lead">Exportação, importação e recuperação usam as rotinas existentes, sem alteração de formato ou política de credenciais.</p><div data-settings-slot="backup"></div>');
  createSettingsPanel('storage',storagePanel());
  content.addEventListener('click',settingsContentClick,true);
  content.dataset.ready='true';
}

function settingsContentClick(event){
  const navCard=event.target.closest('[data-nav-to]');
  if(navCard){ settingsNavigate(navCard.dataset.navTo,{push:true,focus:true}); return; }
  const review=event.target.closest('#settingsReviewPeriodBtn');
  if(review){ settingsMarkSubdialogLauncher(review); openOnboardingModal('edit'); return; }
  const launch=event.target.closest('#chooseAppIconBtn, #importFullBackupBtn, #wipeAllBtn');
  if(launch) settingsMarkSubdialogLauncher(launch);
  const term=event.target.closest('[data-education-term]');
  if(term){ const item=EDUCATIONAL_CONTENT.find(x=>x.title.toLowerCase()===term.dataset.educationTerm.toLowerCase()||x.keywords.some(k=>k.toLowerCase()===term.dataset.educationTerm.toLowerCase())); if(item) settingsRevealElement(`education-${item.id}`); }
}

// Reposiciona a busca real para o cabeçalho (Fase 4 — fiel à referência:
// título | busca central | fechar). Move o input, o label e o container de
// resultados de verdade — nenhum clone, nenhum ID novo, nenhum listener
// perdido (addEventListener em initSettingsModal aponta para o mesmo nó,
// relocação de DOM não desliga listeners). Roda uma única vez no boot: ao
// contrário dos nós legados (moveLegacySettingsNodes), a busca não precisa
// voltar para lugar nenhum quando o modal fecha — o cabeçalho onde ela vive
// agora é permanente, não é recriado por abertura.
function moveSettingsSearchToHeader(){
  const slot=settingsEl('settingsHeaderSearchSlot'), input=settingsEl('settingsSearch');
  if(!slot||!input||input.parentElement===slot) return;
  const label=document.querySelector('label.settings-search-label[for="settingsSearch"]');
  if(label){ label.classList.add('sr-only'); slot.append(label); }
  slot.append(input);
  const results=settingsEl('settingsSearchResults');
  if(results) slot.append(results);
}

// Telas operacionais que migraram da navegação superior para o grupo
// "Operação": o grid inteiro de cada tela é transportado (nunca clonado —
// IDs, listeners e estado interno preservados) para o slot do painel
// enquanto a central está aberta, e devolvido à <section> hospedeira ao
// fechar — exatamente o contrato dos nós legados do #config.
const SETTINGS_SCREEN_GRIDS={
  'tool-params':{grid:'paramsWidgetGrid',host:'params'},
  'tool-motor':{grid:'motorWidgetGrid',host:'motor'},
  'tool-check':{grid:'checkWidgetGrid',host:'check'}
};
function moveLegacySettingsNodes(){
  const host=settingsEl('config'); if(!host) return;
  if(!settingsState.legacyNodes.length) settingsState.legacyNodes=[...host.children].filter(node=>node.matches('[data-settings-category]'));
  settingsState.legacyNodes.forEach(node=>{
    const category=node.dataset.settingsCategory, slot=settingsEl('settingsContent').querySelector(`[data-settings-slot="${category}"]`);
    if(slot) slot.append(node);
  });
  Object.entries(SETTINGS_SCREEN_GRIDS).forEach(([leafId,cfg])=>{
    const grid=settingsEl(cfg.grid), slot=settingsEl('settingsContent').querySelector(`[data-settings-slot="${leafId}"]`);
    if(grid&&slot&&grid.parentElement!==slot) slot.append(grid);
  });
  const rail=settingsEl('railToggle');
  if(rail&&rail.parentElement!==settingsEl('settingsRailSlot')){ settingsState.railParent=rail.parentElement; settingsState.railNext=rail.nextSibling; settingsEl('settingsRailSlot').append(rail); }
}
function restoreLegacySettingsNodes(){
  const host=settingsEl('config'); if(!host) return;
  settingsState.legacyNodes.forEach(node=>host.append(node));
  Object.values(SETTINGS_SCREEN_GRIDS).forEach(cfg=>{
    const grid=settingsEl(cfg.grid), screenHost=settingsEl(cfg.host);
    if(grid&&screenHost&&grid.parentElement!==screenHost) screenHost.append(grid);
  });
  const rail=settingsEl('railToggle');
  if(rail&&settingsState.railParent){ settingsState.railParent.insertBefore(rail,settingsState.railNext); }
}

// Primitiva de baixo nível preservada: torna o painel 'id' visível, esconde os demais.
// Mantida com este nome e assinatura para compatibilidade com chamadas diretas existentes.
function activateSettingsCategory(id,options={}){
  const exists=document.querySelector(`[data-settings-panel="${id}"]`);
  const targetId=exists?id:'general';
  if(settingsState.active==='galton-board'&&targetId!=='galton-board'&&typeof deactivateGaltonBoard==='function') deactivateGaltonBoard({destroy:false});
  settingsState.active=targetId;
  document.querySelectorAll('[data-settings-panel]').forEach(panel=>panel.hidden=panel.dataset.settingsPanel!==targetId);
  const select=settingsEl('settingsMobileCategory'); if(select) select.value=settingsTopLevelFor(targetId);
  settingsUpdateSidebarActive(targetId);
  settingsUpdatePageHeader(targetId);
  // Mesmo gatilho que vivia em navigateToScreen('motor'): 1ª visita ao
  // Motor de Lote na sessão tenta atualizar o câmbio — silencioso se
  // offline (o status na própria tela informa, nunca falha em silêncio).
  if(targetId==='tool-motor' && typeof fxAutoFetchedThisSession!=='undefined' && !fxAutoFetchedThisSession && typeof updateFxRates==='function'){
    fxAutoFetchedThisSession=true;
    updateFxRates();
  }
  if(targetId==='galton-board'&&typeof activateGaltonBoard==='function') activateGaltonBoard();
  if(options.focus) settingsEl('settingsContent').focus({preventScroll:true});
}

function settingsUpdateSidebarActive(id){
  const topId=settingsTopLevelFor(id);
  document.querySelectorAll('#settingsMenu [data-settings-category]').forEach(button=>{
    const on=button.dataset.settingsCategory===topId; button.classList.toggle('active',on); button.setAttribute('aria-current',on?'page':'false');
  });
}
function settingsUpdatePageHeader(id){
  const titleEl=settingsEl('settingsPageTitle'); if(titleEl) titleEl.textContent=settingsPageTitleFor(id);
  const backBtn=settingsEl('settingsBackBtn'), fwdBtn=settingsEl('settingsForwardBtn');
  if(backBtn) backBtn.disabled=settingsState.navIndex<=0;
  if(fwdBtn) fwdBtn.disabled=settingsState.navIndex>=settingsState.navStack.length-1;
}

// Navegação de alto nível: gerencia pilha de histórico interno, visão mobile e cabeçalho da página.
// Não usa history.pushState nem altera a URL — todo o estado é interno ao modal.
function settingsRenderCurrent(options={}){
  const id=settingsState.navStack[settingsState.navIndex];
  activateSettingsCategory(id,{focus:options.focus});
  const modal=settingsEl('settingsModal');
  if(modal) modal.classList.toggle('settings-mobile-detail',!settingsState.mobileListVisible);
}
function settingsNavigate(id,options={}){
  const push=options.push!==false;
  if(push){
    if(settingsState.navStack[settingsState.navIndex]!==id){
      settingsState.navStack=settingsState.navStack.slice(0,settingsState.navIndex+1);
      settingsState.navStack.push(id);
      settingsState.navIndex=settingsState.navStack.length-1;
    }
  }else{
    settingsState.navStack[settingsState.navIndex]=id;
  }
  settingsState.mobileListVisible=false;
  settingsRenderCurrent({focus:options.focus});
  if(options.reveal) settingsRevealElement(options.reveal);
}
function settingsNavigateTopLevel(id){
  settingsState.mobileListVisible=false;
  settingsNavigate(id,{push:true,focus:true});
}
function settingsGoBack(){
  if(settingsState.navIndex>0){
    settingsState.navIndex--;
    if(settingsState.navIndex===0){
      // topo da pilha: no mobile, voltar ao topo significa voltar à lista de categorias,
      // não exibir a página 'general' em tela cheia (a lista é o ponto de partida real).
      settingsState.mobileListVisible=true;
      const modal=settingsEl('settingsModal'); if(modal) modal.classList.remove('settings-mobile-detail');
      settingsRenderCurrent({focus:false});
      settingsEl('settingsSearch').focus({preventScroll:true});
      return;
    }
    settingsRenderCurrent({focus:true}); return;
  }
  if(!settingsState.mobileListVisible){ settingsState.mobileListVisible=true; const modal=settingsEl('settingsModal'); if(modal) modal.classList.remove('settings-mobile-detail'); settingsEl('settingsSearch').focus({preventScroll:true}); }
}
function settingsGoForward(){
  if(settingsState.navIndex<settingsState.navStack.length-1){ settingsState.navIndex++; settingsState.mobileListVisible=false; settingsRenderCurrent({focus:true}); }
}
function settingsNavigateToLeaf(leafId,options={}){
  const leaf=SETTINGS_LEAVES[leafId];
  settingsState.navStack=['general'];
  if(leaf&&leaf.group) settingsState.navStack.push(leaf.group);
  settingsState.navStack.push(leafId);
  settingsState.navIndex=settingsState.navStack.length-1;
  settingsState.mobileListVisible=false;
  settingsRenderCurrent({focus:options.focus});
  if(options.reveal) settingsRevealElement(options.reveal);
}

function settingsSearchEntries(){
  const core=Object.entries(SETTINGS_LEAVES).flatMap(([id,leaf])=>[...leaf.terms,leaf.label].map(term=>({title:term,category:id})));
  const controls=[['Tema visual','appearance','#themeSeg'],['Ícone do app','appearance','#appIconConfig'],['Escala da fonte','interface','#fsSeg'],['Sidebar','interface','#settingsRailSlot'],['Ajuda contextual','interface','#explSeg'],['Estilo da navegação','editor','#navStyleSeg'],['Barra em pílula','editor','#navStyleSeg'],['MDD máximo','parameters','#pMDD'],['Ordem Gênese','parameters','#pGenLev'],['Período operacional','parameters','#settingsPeriodSummary'],['Exportar base completa','backup','#exportFullBackupBtn'],['Importar backup','backup','#importFullBackupBtn'],
    // Governança de armazenamento (JPW-HJFGDE) — cartão único, vários termos de entrada.
    ['Armazenamento da Base','backup','#dgStorageCard'],['Pasta padrão de exportação','backup','#dgStorageCard'],
    ['Confirmar backup','backup','#dgStorageCard'],['Reautorizar pasta','backup','#dgStorageCard'],
    // Notas do MVP (14-mvp-notes.js) — vários termos apontando para o mesmo card,
    // mesmo padrão de 'core' (multi-termo por entrada), já que aqui cada entrada só
    // casa com o próprio título.
    ['Tickets','interface','#mvpNotesSettingsCard'],['tickets','interface','#mvpNotesSettingsCard'],
    ['Notas do MVP','interface','#mvpNotesSettingsCard'],['notas','interface','#mvpNotesSettingsCard'],
    ['tarefas','interface','#mvpNotesSettingsCard'],['bugs','interface','#mvpNotesSettingsCard'],
    ['funcionalidades','interface','#mvpNotesSettingsCard'],['melhorias','interface','#mvpNotesSettingsCard'],
    ['MVP','interface','#mvpNotesSettingsCard'],['ícone menu superior','interface','#mvpNotesSettingsCard'],
    ['backlog','interface','#mvpNotesSettingsCard']
  ].map(([title,category,selector])=>({title,category,selector}));
  const education=EDUCATIONAL_CONTENT.flatMap(item=>[item.title,...item.keywords].map(term=>({title:term,category:'educational',selector:`#education-${item.id}`})));
  return [...core,...controls,...education];
}
function settingsResultPath(category){
  const leaf=SETTINGS_LEAVES[category];
  if(!leaf) return settingsPageTitleFor(category);
  const group=leaf.group?SETTINGS_GROUP_BY_ID[leaf.group]:null;
  return group?`${group.label} › ${leaf.label}`:leaf.label;
}
function renderSettingsSearch(){
  const root=settingsEl('settingsSearchResults'), query=settingsState.query.trim().toLocaleLowerCase('pt-BR'); if(!root) return;
  if(!query){ root.replaceChildren(); return; }
  const seen=new Set(), results=settingsSearchEntries().map(item=>({...item,path:settingsResultPath(item.category)})).filter(item=>`${item.title} ${item.path}`.toLocaleLowerCase('pt-BR').includes(query)).filter(item=>{ const key=`${item.title}|${item.path}`; if(seen.has(key)) return false; seen.add(key); return true; }).sort((a,b)=>(b.selector?1:0)-(a.selector?1:0)).slice(0,18);
  root.innerHTML=results.length?results.map((item,i)=>`<button type="button" data-settings-result="${i}"><b>${settingsEsc(item.title)}</b><span>${settingsEsc(item.path)}</span></button>`).join(''):'<p class="settings-no-results">Nenhuma configuração ou ajuda encontrada.</p>';
  root.querySelectorAll('[data-settings-result]').forEach((button,i)=>button.addEventListener('click',()=>{ const item=results[i]; settingsNavigateToLeaf(item.category,{focus:false,reveal:item.selector}); }));
}
function settingsRevealElement(selector){
  if(!selector) return;
  requestAnimationFrame(()=>{ const target=document.querySelector(selector); if(!target) return; target.scrollIntoView({block:'center',behavior:'smooth'}); target.classList.add('settings-search-hit'); clearTimeout(settingsState.highlightTimer); settingsState.highlightTimer=setTimeout(()=>target.classList.remove('settings-search-hit'),2200); if(target.matches('details')) target.open=true; });
}

// A-003: os seletores antigos .topbar e #main não existem no DOM (os elementos reais são
// <header> e #appMain) — com a Central aberta, todo o cabeçalho e o conteúdo operacional
// da tela ativa permaneciam expostos à árvore de acessibilidade apesar do aria-modal.
// Corrigido com o mesmo padrão captura-e-restaura do drawer de Notas (mvpNotesApplyInert):
// nunca um clear cego — outro mecanismo pode ter posto inert/aria-hidden próprios nesses
// nós, e o fechamento restaura exatamente os valores capturados na abertura.
// document.querySelector('header') resolve para o <header> de topo do app (primeiro na
// ordem do documento); os <header> internos de modais/drawers vêm todos depois.
let settingsInertSnapshot=null;
function settingsInertTargets(){
  return [document.querySelector('header'),document.querySelector('#nav'),document.querySelector('#appMain'),document.querySelector('.foot-note')].filter(Boolean);
}
function settingsSetAppInert(on){
  if(on){
    if(settingsInertSnapshot) return; // já aplicado — reaplicar sobrescreveria a captura original
    settingsInertSnapshot=settingsInertTargets().map(el=>({el, inert:el.inert, ariaHidden:el.getAttribute('aria-hidden')}));
    settingsInertSnapshot.forEach(({el})=>{ el.inert=true; el.setAttribute('aria-hidden','true'); });
  }else{
    const snapshot=settingsInertSnapshot; if(!snapshot) return;
    snapshot.forEach(({el,inert,ariaHidden})=>{
      el.inert=inert;
      if(ariaHidden===null) el.removeAttribute('aria-hidden'); else el.setAttribute('aria-hidden',ariaHidden);
    });
    settingsInertSnapshot=null;
  }
}
function openSettingsModal(category='general', opener){
  buildSettingsMenu(); buildSettingsContent(); settingsState.opener=opener||document.activeElement||settingsEl('headerConfigBtn'); settingsState.open=true; settingsState.suspended=false;
  settingsState.navStack=['general']; settingsState.navIndex=0; settingsState.mobileListVisible=true;
  moveLegacySettingsNodes(); settingsEl('settingsOverlay').classList.add('show'); settingsEl('settingsOverlay').setAttribute('aria-hidden','false'); settingsSetAppInert(true);
  if(category&&category!=='general') settingsNavigate(category,{push:true,focus:false});
  else settingsRenderCurrent({focus:false});
  window.__settingsModalDebug.opens++;
  requestAnimationFrame(()=>settingsEl('settingsSearch').focus());
}
function closeSettingsModal(){
  if(!settingsState.open||settingsState.suspended) return;
  if(typeof deactivateGaltonBoard==='function') deactivateGaltonBoard({destroy:true});
  settingsState.open=false; settingsEl('settingsOverlay').classList.remove('show'); settingsEl('settingsOverlay').setAttribute('aria-hidden','true'); settingsSetAppInert(false); restoreLegacySettingsNodes();
  const opener=settingsState.opener; settingsState.opener=null; if(opener&&document.contains(opener)) requestAnimationFrame(()=>opener.focus());
}
function settingsMarkSubdialogLauncher(element){ settingsState.subdialogLauncher=element; }
function suspendSettingsForSubdialog(){
  if(!settingsState.open||settingsState.suspended) return; settingsState.suspended=true; settingsEl('settingsModal').inert=true; settingsEl('settingsModal').setAttribute('aria-hidden','true'); window.__settingsModalDebug.focusTrapActive=false;
}
function restoreSettingsAfterSubdialog(){
  if(!settingsState.open||!settingsState.suspended) return; settingsState.suspended=false; settingsEl('settingsModal').inert=false; settingsEl('settingsModal').removeAttribute('aria-hidden'); const target=settingsState.subdialogLauncher; settingsState.subdialogLauncher=null; if(target&&document.contains(target)) requestAnimationFrame(()=>target.focus());
}
function settingsFocusables(root){ return [...root.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])')].filter(el=>!el.closest('[hidden]')&&!el.closest('[inert]')); }
function settingsTrapFocus(event){
  if(!settingsState.open||settingsState.suspended||settingsEl('modalOverlay').classList.contains('show')||event.key!=='Tab') return; const list=settingsFocusables(settingsEl('settingsModal')); if(!list.length) return; window.__settingsModalDebug.focusTrapActive=true; const first=list[0],last=list[list.length-1]; if(event.shiftKey&&document.activeElement===first){ event.preventDefault(); last.focus(); } else if(!event.shiftKey&&document.activeElement===last){ event.preventDefault(); first.focus(); }
}
function initSettingsSubdialogObserver(){
  const overlay=settingsEl('modalOverlay'); if(!overlay||settingsState.observer) return;
  settingsState.observer=new MutationObserver(()=>{ if(!settingsState.open) return; if(overlay.classList.contains('show')) suspendSettingsForSubdialog(); else restoreSettingsAfterSubdialog(); });
  settingsState.observer.observe(overlay,{attributes:true,attributeFilter:['class']}); window.__settingsModalDebug.observerInstances++;
}

function initSettingsModal(){
  const gear=settingsEl('headerConfigBtn'); if(!gear) return;
  moveSettingsSearchToHeader();
  gear.addEventListener('click',()=>openSettingsModal('general',gear));
  settingsEl('settingsCloseBtn').addEventListener('click',closeSettingsModal);
  settingsEl('settingsBackBtn').addEventListener('click',settingsGoBack);
  settingsEl('settingsForwardBtn').addEventListener('click',settingsGoForward);
  settingsEl('settingsSearch').addEventListener('input',event=>{ settingsState.query=event.target.value; renderSettingsSearch(); });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&settingsState.open&&!settingsState.suspended&&!settingsEl('modalOverlay').classList.contains('show')){
      const search=settingsEl('settingsSearch');
      if(document.activeElement===search&&search.value){ event.preventDefault(); search.value=''; settingsState.query=''; renderSettingsSearch(); return; }
      event.preventDefault(); closeSettingsModal(); return;
    }
    settingsTrapFocus(event);
  },true);
  initSettingsSubdialogObserver();
}
initSettingsModal();

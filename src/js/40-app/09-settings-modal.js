// ============ CENTRAL DE CONFIGURAÇÕES (N1) ============
// Mantém os controles legados no mesmo DOM: apenas os transporta enquanto a central está aberta.
const SETTINGS_CATEGORIES=[
  {id:'about',group:'GERAL',label:'Sobre',terms:['sobre','versão','build','offline','armazenamento','documentação','changelog']},
  {id:'appearance',group:'PERSONALIZAÇÃO',label:'Aparência',terms:['tema','aparência','ícone','paleta','contraste']},
  {id:'interface',group:'PERSONALIZAÇÃO',label:'Interface',terms:['interface','fonte','tipografia','sidebar','barra lateral','ajuda','instruções']},
  {id:'editor',group:'PERSONALIZAÇÃO',label:'Editor',terms:['editor']},
  {id:'educational',group:'CONHECIMENTO',label:'Educacional',terms:['educacional','forex','pip','spread','glossário','perguntas frequentes']},
  {id:'statute',group:'GOVERNANÇA',label:'Estatuto Operacional',terms:['estatuto','diretrizes','artigos','pdf','governança']},
  {id:'parameters',group:'GOVERNANÇA',label:'Parâmetros e Calibração',terms:['parâmetros','calibração','mdd','drawdown','alavancagem','gênese','quarentena','mei']},
  {id:'backup',group:'DADOS',label:'Backup e Recuperação',terms:['backup','exportar','importar','recuperação','reset','limpar']}
];

const settingsState={open:false,active:'about',query:'',opener:null,legacyNodes:[],railParent:null,railNext:null,suspended:false,subdialogLauncher:null,observer:null,highlightTimer:null};
window.__settingsModalDebug={opens:0,observerInstances:0,focusTrapActive:false};

function settingsEl(id){ return document.getElementById(id); }
function settingsIsOpen(){ return settingsState.open; }
function settingsEsc(v){ return esc(String(v||'')); }
function settingsCategory(id){ return SETTINGS_CATEGORIES.find(x=>x.id===id)||SETTINGS_CATEGORIES[0]; }
function settingsFocusables(root){ return [...root.querySelectorAll('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])')].filter(el=>!el.closest('[hidden]')&&!el.closest('[inert]')); }

function buildSettingsMenu(){
  const menu=settingsEl('settingsMenu'), select=settingsEl('settingsMobileCategory');
  if(!menu||menu.dataset.ready) return;
  let lastGroup='';
  SETTINGS_CATEGORIES.forEach(item=>{
    if(item.group!==lastGroup){ const title=document.createElement('div'); title.className='settings-menu-group'; title.textContent=item.group; menu.append(title); lastGroup=item.group; }
    const button=document.createElement('button'); button.type='button'; button.className='settings-menu-item'; button.dataset.settingsCategory=item.id; button.setAttribute('aria-current','false'); button.textContent=item.label;
    button.addEventListener('click',()=>activateSettingsCategory(item.id,{focus:true})); menu.append(button);
    const option=document.createElement('option'); option.value=item.id; option.textContent=item.label; select.append(option);
  });
  select.addEventListener('change',()=>activateSettingsCategory(select.value,{focus:true}));
  menu.dataset.ready='true';
}

function createSettingsPanel(id,html){
  const panel=document.createElement('section'); panel.className='settings-panel'; panel.dataset.settingsPanel=id; panel.hidden=true; panel.innerHTML=html; settingsEl('settingsContent').append(panel); return panel;
}

function aboutPanel(){
  const build=typeof JP_WEALTH_BUILD_ID==='string'?JP_WEALTH_BUILD_ID:'não informado';
  return `<h3>Sobre</h3><p class="settings-lead">O JP Wealth é uma ferramenta de gestão, registro e controle de risco. O sistema não fornece sinais, não prevê resultados e não transforma expectativas estatísticas em garantias.</p><dl class="settings-facts"><dt>Aplicativo</dt><dd>JP Wealth Risk Terminal</dd><dt>Versão</dt><dd>9.1</dd><dt>Build</dt><dd><code>${settingsEsc(build)}</code></dd><dt>Armazenamento</dt><dd>Local neste navegador.</dd><dt>Funcionamento</dt><dd>Disponível offline após a instalação completa da aplicação.</dd></dl><div class="settings-links"><a href="docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf" target="_blank" rel="noopener">Estatuto Operacional (PDF)</a><a href="CHANGELOG.md" target="_blank" rel="noopener">Changelog</a><a href="README.md" target="_blank" rel="noopener">Documentação do projeto</a></div><p class="note">Dados técnicos não disponíveis no código vigente não são inferidos nesta tela.</p>`;
}

function educationPanel(){
  const groups=[['comece','Começar por aqui'],['fundamentos','Fundamentos do Forex'],['estrutura','Estrutura do mercado'],['pares','Pares e cotações'],['execucao','Execução e custos'],['risco','Risco e alavancagem'],['historia','História do mercado cambial']];
  return `<h3>Educacional</h3><p class="settings-lead">Referência local, curta e curada. Não substitui o Estatuto Operacional nem os Parâmetros e Calibração.</p>${groups.map(([key,label])=>`<section class="education-section"><h4>${label}</h4>${EDUCATIONAL_CONTENT.filter(x=>x.category===key).map(educationArticle).join('')}</section>`).join('')}<section class="education-section"><h4>Glossário</h4><div class="education-glossary">${EDUCATIONAL_GLOSSARY.map(term=>`<button type="button" data-education-term="${settingsEsc(term)}">${settingsEsc(term)}</button>`).join('')}</div></section><section class="education-section"><h4>Perguntas frequentes</h4>${EDUCATIONAL_FAQ.map(([q,a],i)=>`<details id="education-faq-${i}"><summary>${settingsEsc(q)}</summary><p>${settingsEsc(a)}</p></details>`).join('')}</section>`;
}
function educationArticle(item){ return `<article class="education-article" id="education-${item.id}" data-education-id="${item.id}"><h5>${settingsEsc(item.title)}</h5><p><b>Definição.</b> ${settingsEsc(item.definition)}</p><p><b>Exemplo simples.</b> ${settingsEsc(item.example)}</p><p><b>Risco ou limitação.</b> ${settingsEsc(item.risk)}</p><p><b>Relação com o JP Wealth.</b> ${settingsEsc(item.jpWealth)}</p></article>`; }

function buildSettingsContent(){
  const content=settingsEl('settingsContent'); if(!content||content.dataset.ready) return;
  createSettingsPanel('about',aboutPanel());
  createSettingsPanel('appearance','<h3>Aparência</h3><p class="settings-lead">Estética e identidade visual. O tema atual continua usando a persistência já existente em <code>S.theme</code>.</p><div data-settings-slot="appearance"></div>');
  createSettingsPanel('interface','<h3>Interface</h3><p class="settings-lead">Organização, legibilidade e ajuda contextual. Preferências existentes são preservadas.</p><div class="settings-rail-row"><div><h4>Barra lateral</h4><p class="note">Escolha se a barra de navegação permanece expandida ou recolhida neste navegador.</p></div><div id="settingsRailSlot"></div></div><div data-settings-slot="interface"></div>');
  createSettingsPanel('editor','<h3>Editor</h3><p class="settings-empty">Nenhuma configuração de editor disponível nesta versão.</p>');
  createSettingsPanel('educational',educationPanel());
  createSettingsPanel('statute','<h3>Estatuto Operacional</h3><p class="settings-lead">Conteúdo predominantemente de leitura. O documento normativo não é editável nesta central.</p><p class="settings-links"><a href="docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf" target="_blank" rel="noopener">Abrir documento integral (PDF)</a></p><div data-settings-slot="statute"></div>');
  createSettingsPanel('parameters','<h3>Parâmetros e Calibração</h3><p class="settings-lead">Controles existentes, com os valores, unidades, validações e persistência originais.</p><section class="settings-safe-period" id="settingsPeriodSummary"><h4>Período Operacional</h4><p>Os dados do período são mantidos pelo questionário de início. Esta central não mostra valores pessoais ou credenciais.</p><button type="button" class="reset-btn" id="settingsReviewPeriodBtn">Revisar dados do período</button></section><div data-settings-slot="period"></div><div data-settings-slot="parameters"></div>');
  createSettingsPanel('backup','<h3>Backup e Recuperação</h3><p class="settings-lead">Exportação, importação e recuperação usam as rotinas existentes, sem alteração de formato ou política de credenciais.</p><div data-settings-slot="backup"></div>');
  content.addEventListener('click',settingsContentClick,true);
  content.dataset.ready='true';
}

function settingsContentClick(event){
  const review=event.target.closest('#settingsReviewPeriodBtn');
  if(review){ settingsMarkSubdialogLauncher(review); openOnboardingModal('edit'); return; }
  const launch=event.target.closest('#chooseAppIconBtn, #importFullBackupBtn, #wipeAllBtn');
  if(launch) settingsMarkSubdialogLauncher(launch);
  const term=event.target.closest('[data-education-term]');
  if(term){ const item=EDUCATIONAL_CONTENT.find(x=>x.title.toLowerCase()===term.dataset.educationTerm.toLowerCase()||x.keywords.some(k=>k.toLowerCase()===term.dataset.educationTerm.toLowerCase())); if(item) settingsRevealElement(`education-${item.id}`); }
}

function moveLegacySettingsNodes(){
  const host=settingsEl('config'); if(!host) return;
  if(!settingsState.legacyNodes.length) settingsState.legacyNodes=[...host.children].filter(node=>node.matches('[data-settings-category]'));
  settingsState.legacyNodes.forEach(node=>{
    const category=node.dataset.settingsCategory, slot=settingsEl('settingsContent').querySelector(`[data-settings-slot="${category}"]`);
    if(slot) slot.append(node);
  });
  const rail=settingsEl('railToggle');
  if(rail&&rail.parentElement!==settingsEl('settingsRailSlot')){ settingsState.railParent=rail.parentElement; settingsState.railNext=rail.nextSibling; settingsEl('settingsRailSlot').append(rail); }
}
function restoreLegacySettingsNodes(){
  const host=settingsEl('config'); if(!host) return;
  settingsState.legacyNodes.forEach(node=>host.append(node));
  const rail=settingsEl('railToggle');
  if(rail&&settingsState.railParent){ settingsState.railParent.insertBefore(rail,settingsState.railNext); }
}

function activateSettingsCategory(id,options={}){
  const category=settingsCategory(id); settingsState.active=category.id;
  document.querySelectorAll('[data-settings-panel]').forEach(panel=>panel.hidden=panel.dataset.settingsPanel!==category.id);
  document.querySelectorAll('[data-settings-category]').forEach(button=>{ const on=button.dataset.settingsCategory===category.id; button.classList.toggle('active',on); button.setAttribute('aria-current',String(on)); });
  const select=settingsEl('settingsMobileCategory'); if(select) select.value=category.id;
  if(options.focus) settingsEl('settingsContent').focus({preventScroll:true});
}

function settingsSearchEntries(){
  const core=SETTINGS_CATEGORIES.flatMap(category=>[...category.terms,category.label].map(term=>({title:term,path:category.label,category:category.id})));
  const controls=[['Tema visual','Aparência','appearance','#themeSeg'],['Ícone do app','Aparência','appearance','#appIconConfig'],['Escala da fonte','Interface → Tipografia','interface','#fsSeg'],['Sidebar','Interface → Organização','interface','#settingsRailSlot'],['Ajuda contextual','Interface → Instruções','interface','#explSeg'],['MDD máximo','Parâmetros e Calibração → Perfis de risco','parameters','#pMDD'],['Ordem Gênese','Parâmetros e Calibração','parameters','#pGenLev'],['Período operacional','Parâmetros e Calibração → Período Operacional','parameters','#settingsPeriodSummary'],['Exportar base completa','Backup e Recuperação','backup','#exportFullBackupBtn'],['Importar backup','Backup e Recuperação','backup','#importFullBackupBtn']].map(([title,path,category,selector])=>({title,path,category,selector}));
  const education=EDUCATIONAL_CONTENT.flatMap(item=>[item.title,...item.keywords].map(term=>({title:term,path:`Educacional → ${item.title}`,category:'educational',selector:`#education-${item.id}`})));
  const statute=[{title:'Estatuto Operacional',path:'Estatuto Operacional',category:'statute'}];
  return [...core,...controls,...education,...statute];
}
function renderSettingsSearch(){
  const root=settingsEl('settingsSearchResults'), query=settingsState.query.trim().toLocaleLowerCase('pt-BR'); if(!root) return;
  if(!query){ root.replaceChildren(); return; }
  const seen=new Set(), results=settingsSearchEntries().filter(item=>`${item.title} ${item.path}`.toLocaleLowerCase('pt-BR').includes(query)).filter(item=>{ const key=`${item.title}|${item.path}`; if(seen.has(key)) return false; seen.add(key); return true; }).sort((a,b)=>(b.selector?1:0)-(a.selector?1:0)).slice(0,18);
  root.innerHTML=results.length?results.map((item,i)=>`<button type="button" data-settings-result="${i}"><b>${settingsEsc(item.title)}</b><span>${settingsEsc(item.path)}</span></button>`).join(''):'<p class="settings-no-results">Nenhuma configuração ou ajuda encontrada.</p>';
  root.querySelectorAll('[data-settings-result]').forEach((button,i)=>button.addEventListener('click',()=>{ const item=results[i]; activateSettingsCategory(item.category,{focus:false}); settingsRevealElement(item.selector); }));
}
function settingsRevealElement(selector){
  if(!selector) return;
  requestAnimationFrame(()=>{ const target=document.querySelector(selector); if(!target) return; target.scrollIntoView({block:'center',behavior:'smooth'}); target.classList.add('settings-search-hit'); clearTimeout(settingsState.highlightTimer); settingsState.highlightTimer=setTimeout(()=>target.classList.remove('settings-search-hit'),2200); if(target.matches('details')) target.open=true; });
}

function settingsSetAppInert(on){
  const targets=[document.querySelector('.topbar'),document.querySelector('#nav'),document.querySelector('#main'),document.querySelector('.foot-note')].filter(Boolean);
  targets.forEach(el=>{ if(on){ el.inert=true; el.setAttribute('aria-hidden','true'); }else{ el.inert=false; el.removeAttribute('aria-hidden'); } });
}
function openSettingsModal(category='about', opener){
  buildSettingsMenu(); buildSettingsContent(); settingsState.opener=opener||document.activeElement||settingsEl('headerConfigBtn'); settingsState.open=true; settingsState.suspended=false;
  moveLegacySettingsNodes(); settingsEl('settingsOverlay').classList.add('show'); settingsEl('settingsOverlay').setAttribute('aria-hidden','false'); settingsSetAppInert(true); activateSettingsCategory(category,{focus:false});
  window.__settingsModalDebug.opens++;
  requestAnimationFrame(()=>settingsEl('settingsSearch').focus());
}
function closeSettingsModal(){
  if(!settingsState.open||settingsState.suspended) return;
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
  gear.addEventListener('click',()=>openSettingsModal('about',gear));
  settingsEl('settingsCloseBtn').addEventListener('click',closeSettingsModal);
  settingsEl('settingsSearch').addEventListener('input',event=>{ settingsState.query=event.target.value; renderSettingsSearch(); });
  document.addEventListener('keydown',event=>{ if(event.key==='Escape'&&settingsState.open&&!settingsState.suspended&&!settingsEl('modalOverlay').classList.contains('show')){ event.preventDefault(); closeSettingsModal(); return; } settingsTrapFocus(event); },true);
  initSettingsSubdialogObserver();
}
initSettingsModal();

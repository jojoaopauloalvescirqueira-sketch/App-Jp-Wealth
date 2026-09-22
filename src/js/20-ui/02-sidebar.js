// Larguras desktop são preferências de apresentação independentes. O menu
// lateral legado conserva jpw_rail; a lateral em níveis usa sua própria chave.
// Breakpoints e a expansão temporária de um grupo nunca gravam armazenamento.
const NAV_SUBMENU_RAIL_KEY='jpw_nav_submenu_rail';
const NAV_SUBMENU_RAIL_VALUES=['expanded','collapsed'];
const navSubmenuRailState={confirmed:'expanded',raw:null,readable:true};

function navSubmenuRailRead(){
  try{
    const raw=localStorage.getItem(NAV_SUBMENU_RAIL_KEY);
    navSubmenuRailState.raw=raw;navSubmenuRailState.readable=true;
    navSubmenuRailState.confirmed=NAV_SUBMENU_RAIL_VALUES.includes(raw)?raw:'expanded';
  }catch(_){
    navSubmenuRailState.raw=null;navSubmenuRailState.readable=false;navSubmenuRailState.confirmed='expanded';
  }
  return navSubmenuRailState.confirmed;
}

function railActiveState(){
  return document.documentElement.getAttribute('data-navigation')==='submenu'
    ? navSubmenuRailState.confirmed
    : document.documentElement.getAttribute('data-rail')==='collapsed'?'collapsed':'expanded';
}

function renderRailToggle(){
  const collapsed=railActiveState()==='collapsed';
  const t=$('railToggle');
  if(t){
    const label=collapsed?'Expandir barra lateral':'Recolher barra lateral';
    t.innerHTML=(collapsed?'›':'‹')+' <span class="lbl">'+(collapsed?'Expandir':'Recolher')+'</span>';
    t.setAttribute('aria-label',label);t.title=label;t.setAttribute('aria-expanded',String(!collapsed));
  }
}

function applyRailState(){
  let value=null;try{value=localStorage.getItem('jpw_rail');}catch(_){}
  document.documentElement.setAttribute('data-rail',value==='collapsed'?'collapsed':'expanded');
  navSubmenuRailRead();
  document.documentElement.setAttribute('data-submenu-rail',navSubmenuRailState.confirmed);
  renderRailToggle();
  if(typeof syncSubmenuRailPresentation==='function')syncSubmenuRailPresentation();
  if(typeof scheduleNavPill==='function')scheduleNavPill();
}

function saveSubmenuRail(next){
  const message=$('shellAnnouncement');
  let before;
  try{before=localStorage.getItem(NAV_SUBMENU_RAIL_KEY);}
  catch(_){if(message)message.textContent='Não foi possível conferir a largura da lateral. O último estado confirmado foi mantido.';return false;}
  if(before!==navSubmenuRailState.raw){
    navSubmenuRailRead();document.documentElement.setAttribute('data-submenu-rail',navSubmenuRailState.confirmed);renderRailToggle();
    if(message)message.textContent='A largura mudou em outra ação ou aba. O estado atual foi recarregado; tente novamente.';
    return false;
  }
  let actual;
  try{localStorage.setItem(NAV_SUBMENU_RAIL_KEY,next);actual=localStorage.getItem(NAV_SUBMENU_RAIL_KEY);}catch(_){}
  if(actual!==next){
    document.documentElement.setAttribute('data-submenu-rail',navSubmenuRailState.confirmed);renderRailToggle();
    if(message)message.textContent='Não foi possível salvar a largura da lateral. O último estado confirmado foi restaurado.';
    return false;
  }
  navSubmenuRailState.raw=next;navSubmenuRailState.confirmed=next;navSubmenuRailState.readable=true;
  document.documentElement.setAttribute('data-submenu-rail',next);renderRailToggle();
  if(message)message.textContent=next==='collapsed'?'Lateral em níveis recolhida.':'Lateral em níveis expandida.';
  return true;
}

function bindRailToggle(){
  const t=$('railToggle');if(!t||t.dataset.bound)return;t.dataset.bound='true';
  t.addEventListener('click',()=>{
    if(document.documentElement.getAttribute('data-navigation')==='submenu'){
      const next=navSubmenuRailState.confirmed==='collapsed'?'expanded':'collapsed';
      if(saveSubmenuRail(next)&&typeof submenuRailPreferenceChanged==='function')submenuRailPreferenceChanged(next);
      return;
    }
    try{
      const collapsed=localStorage.getItem('jpw_rail')==='collapsed';
      localStorage.setItem('jpw_rail',collapsed?'expanded':'collapsed');
      applyRailState();
    }catch(_){
      const message=$('shellAnnouncement');if(message)message.textContent='Não foi possível salvar a largura da lateral neste navegador.';
    }
  });
}

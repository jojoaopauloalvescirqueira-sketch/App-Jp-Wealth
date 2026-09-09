// A preferência existente controla a largura desktop; breakpoint não grava.
function applyRailState(){
  let value=null;try{value=localStorage.getItem('jpw_rail');}catch(_){}
  const collapsed=value==='collapsed';
  document.documentElement.setAttribute('data-rail',collapsed?'collapsed':'expanded');
  const t=$('railToggle');
  if(t){
    const label=collapsed?'Expandir barra lateral':'Recolher barra lateral';
    t.innerHTML=(collapsed?'›':'‹')+' <span class="lbl">'+(collapsed?'Expandir':'Recolher')+'</span>';
    t.setAttribute('aria-label',label);t.title=label;t.setAttribute('aria-expanded',String(!collapsed));
  }
  if(typeof scheduleNavPill==='function')scheduleNavPill();
}
function bindRailToggle(){
  const t=$('railToggle');if(!t||t.dataset.bound)return;t.dataset.bound='true';
  t.addEventListener('click',()=>{
    try{
      const collapsed=localStorage.getItem('jpw_rail')==='collapsed';
      localStorage.setItem('jpw_rail',collapsed?'expanded':'collapsed');
      applyRailState();
    }catch(_){
      const message=$('shellAnnouncement');if(message)message.textContent='Não foi possível salvar a largura da lateral neste navegador.';
    }
  });
}

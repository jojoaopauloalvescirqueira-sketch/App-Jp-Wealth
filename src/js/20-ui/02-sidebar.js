// ============ SIDEBAR · COLAPSO ============
function applyRailState(){
  const on=localStorage.getItem('jpw_rail')==='collapsed';
  document.documentElement.setAttribute('data-rail', on?'collapsed':'expanded');
  const t=$('railToggle');
  if(t){ t.innerHTML=(on?'›':'‹')+' <span class="lbl">'+(on?'Expandir':'Recolher')+'</span>'; }
}
function bindRailToggle(){
  const t=$('railToggle'); if(!t) return;
  t.addEventListener('click',()=>{
    const on=localStorage.getItem('jpw_rail')==='collapsed';
    localStorage.setItem('jpw_rail', on?'expanded':'collapsed');
    applyRailState();
  });
}

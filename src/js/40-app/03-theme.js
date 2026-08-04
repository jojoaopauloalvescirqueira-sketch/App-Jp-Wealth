// ============ TEMA claro/escuro (SET 4) ============
function applyTheme(){ document.documentElement.dataset.theme = (S.theme==='dark'?'dark':'light'); }
function renderThemeSeg(){
  document.querySelectorAll('#themeSeg button').forEach(b=>b.classList.toggle('on', b.dataset.themeVal===(S.theme||'dark')));
}

// ============ ESCALA TIPOGRÁFICA · 3 degraus fechados ============
// Preferência de exibição, não dado de negócio: mora em localStorage próprio,
// fora de S, para não entrar no schema, na migração nem no backup do estado.
const FS_STEPS=['0','1','2'];
function currentFontStep(){
  let v=null; try{ v=localStorage.getItem('jpw_fs'); }catch(e){}
  return FS_STEPS.includes(v)?v:'0';   // qualquer valor fora da escala volta ao padrão
}
function applyFontScale(){
  const s=currentFontStep();
  if(s==='0') document.documentElement.removeAttribute('data-fs');
  else document.documentElement.setAttribute('data-fs', s);
}
function renderFsSeg(){
  const s=currentFontStep();
  document.querySelectorAll('#fsSeg button').forEach(b=>b.classList.toggle('on', b.dataset.fsVal===s));
}
function bindFsSeg(){
  document.querySelectorAll('#fsSeg button').forEach(b=>b.addEventListener('click',()=>{
    const v=b.dataset.fsVal;
    if(!FS_STEPS.includes(v)) return;
    try{ localStorage.setItem('jpw_fs', v); }catch(e){}
    applyFontScale(); renderFsSeg();
  }));
}

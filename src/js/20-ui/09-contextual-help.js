// ============ EXPLICAÇÃO DE CAMPO SOB DEMANDA ([i]) ============
// Recolhe a nota de cada campo atrás de um ícone no rótulo. Roda sobre o DOM
// já renderizado, então cobre também os campos gerados por template string
// (onboarding, execution board, MEI) sem tocar em nenhuma função de render.
//
// Critério de inclusão: .field > .note — nota explicativa presa a um campo.
// Ficam de fora:
//   .note-live   → texto de estado ao vivo (origem do ATR). Recolher esconderia sinal operacional.
//   .note fora de .field → validação de bloco (soma do Caixa Central).
//   .risk-note   → alertas condicionais; já aparecem só quando disparam.
//   .art         → referência estatutária inline no rótulo, não é frase.
function enhanceFieldNotes(root){
  const scope = root || document;
  scope.querySelectorAll('.field > .note:not(.note-live):not([data-info])').forEach(n=>{
    const f = n.parentElement;
    const lab = f.querySelector(':scope > label');
    if(!lab) return;                       // sem rótulo não há onde ancorar o ícone: nota fica visível
    if(!n.textContent.trim()) return;      // nota vazia não vira ícone
    const aberto = explAllOn();            // nasce já aberta se o modo global pedir
    n.setAttribute('data-info','');
    n.hidden = !aberto;
    const b = document.createElement('button');
    b.type='button'; b.className='note-i'+(aberto?' on':''); b.textContent='i';
    b.title='Explicação deste campo';
    b.setAttribute('aria-label','Explicação deste campo');
    b.setAttribute('aria-expanded', String(aberto));
    lab.appendChild(b);
  });
  enhanceSectionExpl(scope);
}
// ---- Variante de seção ----
// Prosa doutrinária de painel (.expl) não mora em .field e não tem rótulo:
// ancora no cabeçalho da seção. Toda .expl que resolve para o mesmo cabeçalho
// entra no mesmo grupo e abre junto, com um único [i].
let EXPL_SEQ = 0;
// ---- Interruptor global (Configurações) ----
// Mesma natureza da escala tipográfica: preferência de exibição, não dado de
// negócio — localStorage próprio, fora de S.
function explAllOn(){
  let v=null; try{ v=localStorage.getItem('jpw_expl'); }catch(e){}
  return v==='on';
}
function applyExplMode(){
  const on = explAllOn();
  document.querySelectorAll('[data-info]').forEach(n=>{ n.hidden = !on; });
  document.querySelectorAll('.note-i').forEach(b=>{
    b.classList.toggle('on', on);
    b.setAttribute('aria-expanded', String(on));
  });
}
function renderExplSeg(){
  const v = explAllOn()?'on':'off';
  document.querySelectorAll('#explSeg button').forEach(b=>b.classList.toggle('on', b.dataset.explVal===v));
}
function bindExplSeg(){
  document.querySelectorAll('#explSeg button').forEach(b=>b.addEventListener('click',()=>{
    try{ localStorage.setItem('jpw_expl', b.dataset.explVal==='on'?'on':'off'); }catch(e){}
    applyExplMode(); renderExplSeg();
  }));
}
function explAnchor(el){
  for(let n = el.parentElement; n && n !== document.body; n = n.parentElement){
    const h = n.querySelector(':scope > h2, :scope > summary, :scope > label');
    if(h) return h;
    if(n.classList.contains('leverage-panel') && n.firstElementChild) return n.firstElementChild;
  }
  return null;
}
function enhanceSectionExpl(scope){
  (scope || document).querySelectorAll('.expl:not([data-info])').forEach(p=>{
    if(!p.textContent.trim()) return;
    const anc = explAnchor(p);
    if(!anc) return;                       // sem cabeçalho onde ancorar: prosa fica visível
    const aberto = explAllOn();
    // só reaproveita botão de seção; nunca sequestra o [i] de uma nota de campo
    let b = anc.querySelector(':scope > .note-i[data-expl-group]');
    if(!b){
      b = document.createElement('button');
      b.type='button'; b.className='note-i'+(aberto?' on':''); b.textContent='i';
      b.title='Explicação desta seção';
      b.setAttribute('aria-label','Explicação desta seção');
      b.setAttribute('aria-expanded', String(aberto));
      b.dataset.explGroup = 'g' + (++EXPL_SEQ);
      anc.appendChild(b);
    }
    p.setAttribute('data-info','');
    p.dataset.explGroup = b.dataset.explGroup;
    p.hidden = !aberto;
  });
}
function bindFieldNotes(){
  // delegação: sobrevive a qualquer re-render que troque o innerHTML
  document.addEventListener('click', e=>{
    const b = e.target.closest && e.target.closest('.note-i');
    if(!b) return;
    e.preventDefault();                    // o [i] pode morar dentro de <label>/<summary>; não deve acionar o pai
    e.stopPropagation();
    let alvos;
    if(b.dataset.explGroup){
      alvos = [...document.querySelectorAll('.expl[data-info][data-expl-group="'+b.dataset.explGroup+'"]')];
    } else {
      const f = b.closest('.field');
      const n = f && f.querySelector(':scope > .note[data-info]');
      alvos = n ? [n] : [];
    }
    if(!alvos.length) return;
    const abrir = alvos[0].hidden;
    alvos.forEach(n=>{ n.hidden = !abrir; });
    b.classList.toggle('on', abrir);
    b.setAttribute('aria-expanded', String(abrir));
  });
  enhanceFieldNotes();
  // campos nascem a qualquer momento (modais, grades, abas) — observa e reprocessa
  // setTimeout e não requestAnimationFrame: rAF é suspenso em aba oculta e
  // deixaria a flag presa em true para sempre, matando o observador.
  let pend=false;
  new MutationObserver(()=>{
    if(pend) return; pend=true;
    setTimeout(()=>{ pend=false; enhanceFieldNotes(); }, 0);
  }).observe(document.body, {childList:true, subtree:true});
}

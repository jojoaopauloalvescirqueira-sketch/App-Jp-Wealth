// ============ RESEARCH · WORKSPACES DO MÓDULO (NAV-03 · N1) ============
// Superfície estritamente visual. Calendário, NoCoda e Pivots preservam seus
// IDs e renderizadores; somente o owner DOM/navegação muda. A seleção é
// efêmera: não toca S, storage, schema, backup ou persistência.

const RESEARCH_VIEWS = [
  ['calendar', 'execEcal'],
  ['nocoda', 'execNocoda'],
  ['pivots', 'execPivots'],
  ['stocks-br', 'researchStocksBr'],
  ['stocks-global', 'researchStocksGlobal'],
  ['reits', 'researchReits'],
  ['probability-lab', 'researchProbabilityLab'],
  ['others', 'researchOthers']
];

const RESEARCH_VIEW_RENDERERS = {
  calendar: () => {
    if(window.JPWEcalUI&&typeof window.JPWEcalUI.render==='function') window.JPWEcalUI.render();
  },
  nocoda: () => {
    if(window.JPWNocodaUI&&typeof window.JPWNocodaUI.render==='function') window.JPWNocodaUI.render();
  },
  pivots: () => {
    if(window.JPWPivotsUI&&typeof window.JPWPivotsUI.render==='function') window.JPWPivotsUI.render();
  },
  'probability-lab': () => {
    const slot=document.getElementById('researchGaltonSlot');
    if(slot&&!slot.querySelector('[data-galton-root]')) slot.innerHTML=typeof galtonBoardPanelHTML==='function'?galtonBoardPanelHTML():'<p class="settings-empty" role="alert">O laboratório de probabilidade não pôde ser carregado.</p>';
    researchSetCovered(typeof settingsIsOpen==='function'&&settingsIsOpen());
  }
};

let researchView='calendar';

function researchApplyView(view){
  RESEARCH_VIEWS.forEach(([key,id])=>{
    const el=document.getElementById(id);
    if(!el) return;
    const active=key===view;
    el.hidden=!active;
    el.inert=!active;
  });
}

function researchSelectView(view){
  if(!RESEARCH_VIEWS.some(([key])=>key===view)) return false;
  if(researchView==='probability-lab'&&view!=='probability-lab'&&typeof deactivateGaltonBoard==='function') deactivateGaltonBoard({resume:false});
  researchView=view;
  researchApplyView(view);
  const render=RESEARCH_VIEW_RENDERERS[view];
  if(typeof render==='function') render();
  return true;
}

// Navegação e sobreposições preservam o experimento somente em memória.
// O retorno reativa a superfície, mas a execução exige Continuar explicitamente.
function researchLeaveModule(){
  if(typeof deactivateGaltonBoard==='function') deactivateGaltonBoard({resume:false});
}
function researchSetCovered(covered){
  const root=document.querySelector('#researchGaltonSlot [data-galton-root]');
  if(!root) return;
  covered=Boolean(covered||root.closest('[inert]')||document.querySelector('#settingsOverlay.show,#modalOverlay.show,#mvpNotesOverlay.show'));
  const visible=researchView==='probability-lab'&&document.getElementById('research')?.classList.contains('active');
  if(!covered&&visible){
    if(typeof activateGaltonBoard==='function') activateGaltonBoard();
  }else if(root.__galtonController?.active&&typeof deactivateGaltonBoard==='function') deactivateGaltonBoard({resume:false});
}

function researchGetView(){return researchView;}

researchApplyView(researchView);
window.JPWResearch={ui:{selectView:researchSelectView,getView:researchGetView}};

// `boot()` substitui S em import/wipe/finalização e historicamente repinta a
// ferramenta analítica visível. Como o boot carrega antes desta superfície e
// não pode conhecer Research sem ampliar a allowlist NAV-03, o owner novo
// preserva aqui o mesmo lifecycle: após o boot original, repinta somente o
// workspace Research que depende de S vivo. Calendário usa cache próprio.
const researchBootBase=typeof window.boot==='function'?window.boot:null;
if(researchBootBase){
  window.boot=function(){
    const result=researchBootBase.apply(this,arguments);
    if(researchView==='nocoda'&&window.JPWNocodaUI&&typeof window.JPWNocodaUI.render==='function') window.JPWNocodaUI.render();
    if(researchView==='pivots'&&window.JPWPivotsUI&&typeof window.JPWPivotsUI.render==='function') window.JPWPivotsUI.render();
    return result;
  };
}

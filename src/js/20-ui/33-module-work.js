// Availability protects presentation only. Existing domain writers and their
// in-flight responses remain authoritative; no command is issued by suspension.
(function(root){
  'use strict';
  const screens={research:['research'],forex:['exec','fxconsolidated','fxplan','fxreserves','paramsWidgetGrid'],
    'personal-finance':['finpes'],alladin:['alladin']};
  const names={research:'Research',forex:'Forex','personal-finance':'Finanças Pessoais',alladin:'Alladin'};
  const dialogs={alladinModalOverlay:'alladin',executionBoardDialog:'forex',
    fxcRegistrationDialog:'forex',fxcSetupDialog:'forex',fxAccountsLeaveDialog:'forex',forexChecklistDialog:'forex'};
  const suspended=new Set(),inerted=new Map(),bound=new WeakSet(),focusBefore=new Map(),causes=new Map();
  const byId=id=>document.getElementById(id);
  const available=id=>!root.JPWModuleAvailability||root.JPWModuleAvailability.canAccess(id);
  const visible=node=>node?.tagName==='DIALOG'?node.open:!!node?.classList.contains('show');
  const controls='input,select,textarea';
  function owner(node){
    if(!node?.closest)return null;
    const modal=node.closest('[data-module-work-owner]');if(modal)return modal.dataset.moduleWorkOwner;
    for(const [id,ids]of Object.entries(screens))if(ids.some(key=>node.closest('#'+key)))return id;
    return null;
  }
  function fields(node){
    return [...node.querySelectorAll(controls)].filter(field=>field.type!=='password'&&field.type!=='file'&&
      !/password|senha|secret|token|credential|pin/i.test([field.id,field.name,field.autocomplete].join(' '))&&
      !field.closest('[data-module-work-notice]')).map((field,index)=>({
        field:field.id||field.name||field.getAttribute('aria-label')||'campo '+(index+1),
        value:field.type==='checkbox'||field.type==='radio'?field.checked:String(field.value)}));
  }
  function moduleModals(id){return [...document.querySelectorAll('[data-module-work-owner]')].filter(node=>node.dataset.moduleWorkOwner===id&&visible(node));}
  function changedField(field){
    if(field.type==='checkbox'||field.type==='radio')return field.checked!==field.defaultChecked;
    if(field.tagName==='SELECT')return [...field.options].some(option=>option.selected!==option.defaultSelected);
    return field.value!==field.defaultValue;
  }
  function pendingFields(id){
    return typeof jpwWorkspaceEdited==='undefined'?[]:[...jpwWorkspaceEdited.keys()].filter(field=>
      field.isConnected&&owner(field)===id&&changedField(field)&&!field.closest('[data-module-work-notice]')&&
      (!field.closest('[data-module-work-owner]')||visible(field.closest('[data-module-work-owner]'))));
  }
  function hasPending(id){
    if(!screens[id])return false;
    if(id==='alladin'&&root.JPWAlladinUI?.workState().pending)return true;
    if(id==='research'&&(root.JPWNocodaUI?.hasDrafts()||root.JPWPivotsUI?.hasDrafts()))return true;
    if(id==='forex'&&(root.JPWForex?.executionBoardUI?.hasDrafts()||root.JPWForex?.accountsUI?.hasDrafts()||
      root.JPWFXConsolidatedUI?.workState().pending||jpwWorkspaceDraftProviders.get('planning')?.().length))return true;
    return pendingFields(id).length>0||moduleModals(id).some(node=>node.querySelector(controls));
  }
  function continuation(id,node){
    return id==='alladin'&&node.id==='alladinModalOverlay'&&root.JPWAlladinUI?.workState().continuation;
  }
  function makeInert(node,id){
    if(!inerted.has(node))inerted.set(node,{id,previous:node.inert});
    if(!node.inert)node.inert=true;
  }
  function restoreInert(id,within){
    for(const [node,snapshot]of inerted)if(snapshot.id===id&&(!within||within.contains(node))){
      node.inert=snapshot.previous;inerted.delete(node);
    }
  }
  function notice(node,id){
    const host=node.id==='modalOverlay'?(byId('modalBox')?.querySelector(':scope > [role="dialog"]')||byId('modalBox')):
      node.id==='alladinModalOverlay'?byId('alladinModalBox'):node;
    if(!host)return;
    const focused=document.activeElement,containedFocus=host.contains(focused);
    let bar=host.querySelector(':scope > [data-module-work-notice]');
    if(!bar){
      bar=document.createElement('section');bar.dataset.moduleWorkNotice=id;bar.className='module-work-notice';
      bar.setAttribute('role','status');bar.setAttribute('aria-live','polite');
      const text=document.createElement('p');bar.append(text);
      const resume=document.createElement('button');resume.type='button';resume.textContent='Descongelar para continuar';
      resume.onclick=()=>root.JPWModuleAvailabilityUI?.requestChange(id,'active',resume);bar.append(resume);
      const backup=document.createElement('button');backup.type='button';backup.textContent='Backup Completo';
      backup.onclick=()=>{if(typeof exportFullBackup==='function')exportFullBackup();};bar.append(backup);
      host.prepend(bar);
    }
    const continuing=continuation(id,node);
    const message=names[id]+(causes.get(id)==='storage'?' congelado em outra aba. ':' congelado. ')+(continuing?
      'A confirmação já iniciada deve ser concluída; novas operações permanecem suspensas.':
      'O preenchimento permanece nesta sessão. Descongele explicitamente para continuar ou preserve-o pelo Backup Completo.');
    if(bar.firstElementChild.textContent!==message)bar.firstElementChild.textContent=message;
    if(continuing)restoreInert(id,host);
    else for(const child of host.children)if(child!==bar)makeInert(child,id);
    // Only move focus when it was made unavailable; never steal it from Settings.
    if(containedFocus&&focused.closest('[inert]'))bar.querySelector('button').focus();
  }
  function bind(node,id){
    if(bound.has(node))return;bound.add(node);
    for(const type of ['click','submit','input','change','keydown','cancel'])node.addEventListener(type,event=>{
      const current=node.id==='modalOverlay'?node.dataset.moduleWorkOwner:(node.dataset.moduleWorkOwner||id);
      if(!current)return;
      if(available(current))return;
      if(event.target.closest?.('[data-module-work-notice]'))return;
      if(continuation(current,node))return;
      // The trap for a suspended modal includes its recovery controls only.
      if(type==='keydown'&&event.key==='Tab'&&visible(node)){
        const items=[...node.querySelectorAll('[data-module-work-notice] button')].filter(item=>!item.disabled);
        if(items.length){const index=items.indexOf(document.activeElement),step=event.shiftKey?-1:1;items[(index+step+items.length)%items.length].focus();}
      }
      event.preventDefault();event.stopImmediatePropagation();
    },true);
  }
  function claimModal(id,node){
    if(!screens[id]||!node)return;
    if(node.id==='modalOverlay')node._moduleWorkContent=byId('modalBox')?.firstElementChild;
    node.dataset.moduleWorkOwner=id;bind(node,id);
    if(!available(id)&&visible(node))notice(node,id);
  }
  function refresh(){
    const shared=byId('modalOverlay');
    if(shared?.dataset.moduleWorkOwner&&(!visible(shared)||!shared._moduleWorkContent?.isConnected)){
      delete shared.dataset.moduleWorkOwner;shared._moduleWorkContent=null;
    }
    // Legacy Forex presentation lives beside domain functions. Identify its
    // existing form IDs here rather than editing financial writers or guessing
    // ownership from the current page (Settings and session modals are shared).
    if(visible(shared)&&(byId('modalBox')?.classList.contains('onboarding-modal')||byId('modalBox')?.querySelector('#closeResultInput,#finalReview,[data-compl],input[name="divreason"]')))claimModal('forex',shared);
    for(const [key,id]of Object.entries(dialogs)){const node=byId(key);if(node)claimModal(id,node);}
    for(const id of suspended){
      for(const key of screens[id]){const node=byId(key);if(node){bind(node,id);if(key==='paramsWidgetGrid')notice(node,id);else makeInert(node,id);}}
      for(const node of moduleModals(id))notice(node,id);
    }
  }
  function suspend(id,reason){
    if(!screens[id])return false;
    if(!suspended.has(id))causes.set(id,reason);
    if(!suspended.has(id)&&owner(document.activeElement)===id)focusBefore.set(id,document.activeElement);
    suspended.add(id);
    if(id==='research'&&typeof researchLeaveModule==='function')researchLeaveModule();
    refresh();return true;
  }
  function resume(id){
    if(!screens[id]||!available(id))return false;
    const wasRecoveryControl=document.activeElement.closest?.('[data-module-work-notice]');
    suspended.delete(id);causes.delete(id);restoreInert(id);
    for(const node of document.querySelectorAll('[data-module-work-notice]'))if(node.dataset.moduleWorkNotice===id)node.remove();
    if(id==='alladin')root.JPWAlladinUI?.render();
    const target=focusBefore.get(id);focusBefore.delete(id);
    if(wasRecoveryControl&&target?.isConnected&&!target.closest('[inert],[hidden]')&&target.getClientRects().length)target.focus({preventScroll:true});
    return true;
  }
  function drafts(reset=false){
    // Only explicit base adoption calls reset=true (never freeze/unfreeze).
    // The former drafts were already offered for backup; do not export them as
    // if they belonged to the imported base. No financial command is replayed.
    if(reset){
      root.JPWNocodaUI?.resetDraft();root.JPWPivotsUI?.resetDraft();root.JPWAlladinUI?.resetWork();
      root.JPWFXConsolidatedUI?.resetWork();root.JPWForex?.accountsUI?.resetWork();
      const shared=byId('modalOverlay');if(shared?.dataset.moduleWorkOwner)shared.classList.remove('show');
      return [];
    }
    const result=[];
    for(const id of Object.keys(screens)){
      const entries=[];
      if(id==='research'){
        const nocoda=root.JPWNocodaUI?.backupDraft(),pivots=root.JPWPivotsUI?.backupDraft();
        if(nocoda)entries.push({kind:'nocoda',draft:nocoda});if(pivots)entries.push({kind:'pivots',draft:pivots});
      }
      if(id==='alladin'&&root.JPWAlladinUI?.workState().pending)entries.push({kind:'alladin',state:root.JPWAlladinUI.workState()});
      for(const node of moduleModals(id)){const values=fields(node);if(values.length)entries.push({kind:node.id,fields:values});}
      const pending=pendingFields(id);if(pending.length)entries.push({kind:'campos não confirmados',fields:pending.map(field=>fields({querySelectorAll:()=>[field]})[0]).filter(Boolean)});
      if(entries.length)result.push({label:names[id]+' — trabalho de interface preservado para conferência',text:JSON.stringify(entries)});
    }
    return result;
  }
  root.JPWModuleWork=Object.freeze({hasPending,suspend,resume,claimModal,isSuspended:id=>suspended.has(id)});
  jpwWorkspaceDraftProviders.set('module-work',drafts);
  for(const [id,ids]of Object.entries(screens))for(const key of ids){const node=byId(key);if(node)bind(node,id);}
  refresh();
  // New modal/form nodes are observed locally; input events are not intercepted
  // on document/window and background request responses are not cancelled.
  new MutationObserver(refresh).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['open','class']});
})(window);

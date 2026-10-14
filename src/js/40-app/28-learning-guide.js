// Coordenador do guia: observação do app original; nenhuma mutação financeira.
(function(root){
  'use strict';
  const catalog=root.JPWLearningCatalog,store=root.JPWLearningProgress,view=root.JPWLearningView;
  if(!catalog||!store||!view||root.JPWLearningGuide)return;
  let progress=store.empty(catalog),raw=null,storage='local',blocked=false,notice='',active=false,paused=true,initialized=false,disposed=false,generation=0;
  let cleanup=[],lifecycleCleanup=[],observer=null,centerRoot=null,anchor=null,practicing=false,actionProof=null,frame=0,initialEpoch=null,observedRoute=null,transitionMode=null,pausedTarget=null,deliberateEntry=null;
  const clone=value=>JSON.parse(JSON.stringify(value));
  const track=()=>catalog.tracks.find(t=>t.id===progress.trackId);
  const step=()=>track()?.steps.find(s=>s.id===progress.stepId);
  function epoch(){return [Number(root.JP_WEALTH_SESSION_WIPE_EPOCH)||0,typeof jpWealthPersistenceEpoch==='function'?jpWealthPersistenceEpoch():null].join(':');}
  function accessible(){const t=track();return !t?.module||root.JPWModuleAvailability?.canAccess(t.module)!==false;}
  function readProgress(){
    const result=store.read(catalog);raw=Object.prototype.hasOwnProperty.call(result,'raw')?result.raw:null;
    blocked=result.reason==='incompatible';
    if(result.ok){progress=result.document;storage='local';notice='Progresso local deste navegador.';}
    else if(blocked){progress=store.empty(catalog);storage='blocked';notice='Há progresso de outra versão ou inválido. Ele será preservado até você escolher Reiniciar progresso.';}
    else {storage='memory';notice='Progresso somente nesta sessão: o navegador não permite ler a gravação do guia.';}
  }
  function persist(){
    if(disposed||blocked)return false;
    const result=store.write(progress,catalog,{expectedRaw:raw});
    if(result.ok){raw=result.raw;storage='local';return true;}
    if(result.reason==='concurrent-change'||result.reason==='incompatible'||result.reason==='unknown'){
      stop();readProgress();paused=true;progress.paused=true;notice='A gravação do guia mudou ou não foi confirmada. O guia pausou; confira o progresso na central antes de retomar.';renderCenter();return false;
    }
    if(Object.prototype.hasOwnProperty.call(result,'raw'))raw=result.raw;
    storage='memory';notice='Progresso somente nesta sessão: o navegador não confirmou a gravação do guia.';return true;
  }
  function stop(options={}){
    generation++;if(frame){cancelAnimationFrame(frame);frame=0;}
    cleanup.forEach(fn=>fn());cleanup=[];observer?.disconnect();observer=null;actionProof=null;anchor=null;practicing=false;pausedTarget=null;transitionMode=null;view.hide({preserveFocus:!!options.preserveFocus});
  }
  function snapshot(){return {active,paused,trackId:progress.trackId,stepId:progress.stepId,storage,notice,progress:clone(progress)};}
  function centerModel(){return {...snapshot(),tracks:catalog.tracks.map(t=>({id:t.id,title:t.title,description:t.description,total:t.steps.length,done:t.steps.filter(s=>progress.steps[s.id]).length,seen:t.steps.filter(s=>progress.steps[s.id]?.orientation==='seen').length,skipped:t.steps.filter(s=>progress.steps[s.id]?.orientation==='skipped').length,practiced:t.steps.filter(s=>progress.steps[s.id]?.practice==='confirmed').length,frozen:!!t.module&&root.JPWModuleAvailability?.canAccess(t.module)===false}))};}
  function renderCenter(container){
    if(container)centerRoot=container;
    if(!centerRoot||!document.body.contains?.(centerRoot))centerRoot=document.querySelector('[data-settings-panel="learning-guide"]');
    return view.center(centerRoot,centerModel(),actions);
  }
  function isOwnCenter(){const center=document.querySelector('[data-settings-panel="learning-guide"]');return center&&view.visible(center);}
  function open(opener){
    init();if(typeof openSettingsModal!=='function')return false;
    if(active&&!paused&&!pause('Você abriu a central do guia. Retomar confere novamente a tela atual.'))return false;
    // Opening an unrelated native dialog belongs to its owner, including drafts.
    const host=view.selectHost(null,step());
    if(host.foreign&&!isOwnCenter()){notice='Feche o diálogo atual pelos controles originais para abrir a central do guia.';return false;}
    openSettingsModal('learning-guide',opener||document.activeElement);renderCenter();return true;
  }
  function matchesDestination(s,currentOverride){
    const dest=s.destination;if(!dest)return true;
    if(dest.settings==='tool-check'&&document.getElementById('forexChecklistDialog')?.open&&view.visible(document.getElementById('checkWidgetGrid')))return true;
    if(dest.settings)return view.visible(document.querySelector('[data-settings-panel="'+dest.settings+'"]'));
    const current=currentOverride||root.JPWNavigation.current();
    if(dest.local){
      const resolved=root.JPWNavigation.resolve(dest.route);
      if(!resolved.accepted||current.primary!==resolved.primary||current.screen!==resolved.screen||current.localView?.surface!==dest.local.surface||current.localView?.view!==dest.local.view)return false;
    }else if(dest.route&&current.canonical!==dest.route)return false;
    if(dest.alladin){const tab=document.querySelector('#alladinTabs [data-alladin-view="'+dest.alladin+'"]');if(tab?.getAttribute('aria-pressed')!=='true')return false;}
    return true;
  }
  function targetFor(s){
    if(s.destination?.settings==='tool-check'){const dialog=document.getElementById('forexChecklistDialog'),grid=document.getElementById('checkWidgetGrid');if(dialog?.open&&view.visible(grid))return grid;const opener=document.getElementById('settingsOpenChecklist');if(view.visible(opener))return opener;}
    if(s.practice==='notes'){const metadata=document.getElementById('mvpNotesNewBox');if(view.visible(metadata))return metadata;}
    if(s.action==='menu'){if(typeof shellUI!=='undefined'&&shellUI.open&&typeof shellMenuRoot==='function')return shellMenuRoot();const toggle=document.querySelector('[data-shell-menu-toggle]');if(view.visible(toggle))return toggle;const home=document.querySelector('[data-route="dashboard"]');if(view.visible(home))return home;}
    if(s.action==='notes'&&view.visible(document.getElementById('mvpNotesOverlay')))return document.getElementById('mvpNotesDrawer')||document.getElementById('mvpNotesOverlay');
    if(s.action==='session'&&view.visible(document.getElementById('sessionCancel')))return document.getElementById('sessionCancel');
    if(s.action==='menu'&&typeof shellUI!=='undefined'&&shellUI.open&&typeof shellMenuRoot==='function')return shellMenuRoot();
    return [...document.querySelectorAll(s.anchor)].find(view.visible)||document.querySelector(s.anchor);
  }
  function draw(status,message,target){
    if(paused){status='paused';target=pausedTarget;message=notice;}
    const t=track(),s=step();if(!s)return;
    view.coach({step:s,index:t.steps.indexOf(s),last:t.steps[t.steps.length-1]===s,count:`${t.title} · ${t.steps.indexOf(s)+1}/${t.steps.length}`,anchor:target||null,status,notice:[message,storage!=='local'?notice:''].filter(Boolean).join(' '),done:!!progress.steps[s.id],practicing},actions);
    renderCenter();
  }
  function exitTarget(mode){
    if(mode==='notes'){
      const metadata=document.getElementById('mvpNotesNewCancelBtn');if(view.visible(document.getElementById('mvpNotesNewBox'))&&view.visible(metadata))return metadata;
      if(view.visible(document.getElementById('mvpNotesOverlay')))return document.getElementById('mvpNotesCloseBtn');
    }
    if(mode==='checklist')return document.getElementById('forexChecklistDialog')?.open?document.getElementById('forexChecklistClose'):null;
    if(mode==='settings'){
      if(document.getElementById('forexChecklistDialog')?.open)return document.getElementById('forexChecklistClose');
      if(view.visible(document.getElementById('settingsModal')))return document.getElementById('settingsCloseBtn');
    }
    return null;
  }
  function exitMode(s){
    if((s.practice==='notes'||s.action==='notes')&&view.visible(document.getElementById('mvpNotesOverlay')))return 'notes';
    if(s.destination?.settings&&document.getElementById('forexChecklistDialog')?.open)return 'checklist';
    if(s.destination?.settings&&(view.visible(document.getElementById('settingsModal'))||document.getElementById('forexChecklistDialog')?.open))return 'settings';
    return null;
  }
  function suspend(message,mode){
    stop();paused=true;progress.paused=true;transitionMode=mode||null;pausedTarget=exitTarget(mode);notice=pausedTarget?'Para continuar, feche '+(mode==='notes'?'Notas':'esta janela')+' pelos controles originais. Resolva Salvar ou Cancelar se o app pedir; depois use Ir para esta tela. Nenhum rascunho será descartado pelo guia.':message;
    if(!persist())return false;draw('paused',notice,pausedTarget);
    if(pausedTarget){
      const token=generation;
      // A bounded exit watcher keeps the suspended coach reachable across an
      // original guarded close. It never invokes Close, Save or Discard itself.
      const checkExit=()=>{requestAnimationFrame(()=>{
        if(token!==generation||disposed||!paused)return;
        const target=exitTarget(mode);pausedTarget=view.visible(target)?target:null;
        if(!pausedTarget){observer?.disconnect();observer=null;const ownerTitle=document.getElementById('settingsPageTitle');if(step()?.destination?.settings&&view.visible(ownerTitle))pausedTarget=ownerTitle;notice='A janela foi fechada. Use Ir para esta tela para continuar a trilha pelos controles originais.';}
        draw('paused',notice,pausedTarget);
      });};
      observer=new MutationObserver(checkExit);
      for(const id of ['mvpNotesOverlay','mvpNotesNewOverlay','settingsOverlay','modalOverlay','forexChecklistDialog']){const node=document.getElementById(id);if(node)observer.observe(node,{attributes:true,attributeFilter:['class','hidden','aria-hidden','open']});}
      listen(pausedTarget,'click',event=>{if(event.isTrusted)checkExit();},true);
    }
  }
  function listen(target,type,fn,capture){target.addEventListener(type,fn,capture);cleanup.push(()=>target.removeEventListener(type,fn,capture));}
  function schedule(fn){const token=generation;requestAnimationFrame(()=>{if(token===generation&&!disposed&&!paused&&active)fn();});}
  function mark(orientation,practice){
    if(blocked||disposed||!step())return false;
    const old=progress.steps[step().id];
    progress.steps[step().id]={orientation:practice==='confirmed'||old?.practice==='confirmed'?'seen':orientation,practice:practice||old?.practice||null};if(!persist())return false;renderCenter();return true;
  }
  function orientation(){if(paused||!active)return;const s=step();if(s.kind==='action'&&!s.allowRead)return;if(!mark('seen',null))return;draw('ready','Leitura reconhecida. Isso não confirma uma alteração de dados.',anchor);}
  function evaluateAction(target){
    const s=step();if(!actionProof||actionProof.token!==generation)return;
    let ready=false;
    if(s.action==='menu')ready=target.dataset.route==='dashboard'&&root.JPWNavigation.current().canonical==='dashboard'||target.getAttribute('aria-expanded')==='true'||(typeof shellUI!=='undefined'&&shellUI.open===true);
    if(s.action==='help')ready=target.getAttribute('aria-expanded')==='true';
    if(s.action==='notes')ready=view.visible(document.getElementById('mvpNotesOverlay'))&&document.getElementById('mvpNotesOverlay').getAttribute('aria-hidden')==='false';
    if(s.action==='session')ready=actionProof.opened&&actionProof.cancelled&&!view.visible(document.getElementById('sessionCancel'));
    if(ready){actionProof=null;if(!mark('seen',null))return;anchor=targetFor(s);draw('ready','Ação observada no controle original. Você pode seguir.',view.visible(anchor)?anchor:null);}
  }
  function financialRaw(){try{const value=JSON.parse(root.localStorage.getItem('jpwealth_v9_state'));return value&&typeof value==='object'?value:null;}catch(_){return null;}}
  function result(){try{return typeof jpWealthPersistenceLastResult==='function'?jpWealthPersistenceLastResult():null;}catch(_){return null;}}
  function unknown(){return typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown();}
  function scopedBudget(state,context){return state?.personalFinance?.months?.[context.month]?.[context.collection]?.find(row=>row.id===context.id)?.[context.field];}
  function capturePractice(target){
    const s=step(),before=financialRaw(),beforeResult=result();if(!practicing||!before||!beforeResult||unknown())return null;
    if(s.practice==='budget'){
      if(typeof fbFieldIdentity!=='function'||typeof fbCurrentKey!=='function')return null;
      const context=fbFieldIdentity(target,fbCurrentKey());if(!context||!['incomes','expenses'].includes(context.collection))return null;
      const row=before.personalFinance?.months?.[context.month]?.[context.collection]?.find(row=>row.id===context.id);if(!row)return null;
      const allowed=context.collection==='incomes'?['name','projectedAmount','receivedAmount']:['name','targetAmount','expectedAmount','executedCash','executedCard'];if(!allowed.includes(context.field))return null;
      let desired;
      if(context.field==='name')desired=target.value;
      else {if(typeof parseBRLCents!=='function')return null;desired=target.value.trim()===''?null:parseBRLCents(target.value);if(Number.isNaN(desired)||(typeof desired==='number'&&desired<0))return null;}
      if(JSON.stringify(row[context.field])===JSON.stringify(desired))return null;
      return {kind:'budget',context,desired,previous:clone(row[context.field]??null),beforeResult,resultEpoch:typeof jpWealthPersistenceEpoch==='function'?jpWealthPersistenceEpoch():beforeResult.epoch,epoch:epoch(),token:generation};
    }
    if(s.practice==='notes'){
      if(typeof mvpNotesUI==='undefined'||!mvpNotesUI.draft||!mvpNotesUI.draftDirty)return null;
      const draft=clone(mvpNotesUI.draft),id=mvpNotesUI.selectedId||null;
      if(!draft.content?.trim())return null;
      return {kind:'notes',id,draft,previous:clone(before.mvpNotes?.items||[]),beforeResult,resultEpoch:typeof jpWealthPersistenceEpoch==='function'?jpWealthPersistenceEpoch():beforeResult.epoch,epoch:epoch(),token:generation};
    }
    return null;
  }
  function verifyPractice(proof){
    if(!proof||proof.token!==generation||proof.epoch!==epoch()||unknown()||paused)return;
    const after=financialRaw(),receipt=result();
    if(!after||!receipt||receipt.status!=='CONFIRMED'||receipt.reason!=='READBACK_MATCH'||receipt.context!==proof.beforeResult.context||receipt.epoch!==proof.resultEpoch||JSON.stringify(receipt)===JSON.stringify(proof.beforeResult))return;
    let confirmed=false;
    if(proof.kind==='budget')confirmed=JSON.stringify(scopedBudget(after,proof.context))===JSON.stringify(proof.desired)&&JSON.stringify(scopedBudget(after,proof.context))!==JSON.stringify(proof.previous);
    if(proof.kind==='notes'){
      const id=typeof mvpNotesUI!=='undefined'?mvpNotesUI.selectedId:null;
      const row=after.mvpNotes?.items?.find(item=>item.id===id);
      const before=proof.previous.find(item=>item.id===id);
      const fields=Object.keys(proof.draft).filter(key=>!['id','createdAt','updatedAt','title'].includes(key));
      confirmed=!!row&&(!proof.id||proof.id===id)&&fields.every(key=>JSON.stringify(row[key]??null)===JSON.stringify(proof.draft[key]??null))&&JSON.stringify(before??null)!==JSON.stringify(row)&&mvpNotesUI.draftDirty===false;
    }
    if(confirmed){if(!mark('seen','confirmed'))return;practicing=false;draw('ready','Prática confirmada: o controle original gravou e a base relida contém a alteração desta etapa.',anchor);}
  }
  function bindPractice(){
    const s=step();if(!practicing)return;
    const selector=s.practice==='budget'?'[data-fi-campo],[data-fe-campo]':'#mvpNotesSaveBtn';
    const rootEl=document.querySelector(s.anchor);
    const targets=s.practice==='budget'?(rootEl?.querySelectorAll?.(selector)||document.querySelectorAll(selector)):document.querySelectorAll(selector);
    for(const target of targets){
      if(!view.visible(target)||target.__jpwLearningBound===generation)continue;
      const boundToken=generation;target.__jpwLearningBound=boundToken;
      let pending=null;
      const eventType=s.practice==='budget'?'change':'click';
      listen(target,s.practice==='budget'?'change':'click',event=>{
        if(!event.isTrusted||event.target!==target||paused||!accessible())return;
        pending={event,proof:capturePractice(target)};
      },true);
      // Product handlers are synchronous and were registered earlier. This bubble
      // listener runs immediately after them, before a later unrelated autosave.
      listen(target,eventType,event=>{if(pending?.event===event){const proof=pending.proof;pending=null;verifyPractice(proof);}},false);
      cleanup.push(()=>{pending=null;if(target.__jpwLearningBound===boundToken)delete target.__jpwLearningBound;});
    }
  }
  function observe(){
    const s=step(),token=generation;
    const observeRoot=anchor?.closest('.screen,[role="dialog"],dialog,#appSidebar')||anchor?.parentElement;
    observer=new MutationObserver(records=>{
      if(token!==generation||paused||disposed)return;
      if(records.length&&records.every(r=>r.target.closest?.('#jpwLearningCoach,#jpwLearningCenter')||[...(r.addedNodes||[]),...(r.removedNodes||[])].every(n=>n.id==='jpwLearningCoach'||n.id==='jpwLearningCenter')&&r.type==='childList'))return;
      schedule(()=>{
        if(epoch()!==initialEpoch){suspend('A sessão ou base mudou. Retome depois de conferir os dados.');return;}
        const target=targetFor(s),host=view.selectHost(target,s);
        if(host.foreign){suspend('Outro diálogo está aberto. Resolva ou cancele esse diálogo pelos controles originais e retome o guia.');return;}
        if(!view.visible(target)&&!s.allowRead){suspend('O controle desta etapa não está disponível. Retome quando a tela estiver pronta ou escolha outra trilha.');return;}
        if(practicing)bindPractice();
        if(target!==anchor&&view.visible(target)){anchor=target;draw(progress.steps[s.id]?'ready':'waiting','Continue nos controles originais deste diálogo. Salvar e Cancelar mantêm seu significado.',anchor);}
        if(actionProof)evaluateAction(actionProof.target);
      });
    });
    if(observeRoot)observer.observe(observeRoot,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden','inert','aria-hidden','aria-expanded','class','disabled','open']});
    for(const id of ['modalOverlay','settingsOverlay','mvpNotesOverlay','mvpNotesNewOverlay','alladinModalOverlay','ecalOverlay','forexChecklistDialog']){const node=document.getElementById(id);if(node&&node!==observeRoot)observer.observe(node,{attributes:true,attributeFilter:['hidden','aria-hidden','class','open']});}
    if(s.kind==='action')listen(document,'click',event=>{
      if(!event.isTrusted||paused)return;
      const target=event.target.closest?.(s.anchor);
      if(target&&view.visible(target)){
        actionProof={target,token:generation,opened:s.action==='session'};
        schedule(()=>evaluateAction(target));
      }
      if(s.action==='session'&&event.target.closest?.('#sessionCancel')&&actionProof?.opened){actionProof.cancelled=true;schedule(()=>evaluateAction(actionProof.target));}
    },true);
    listen(document,'keydown',event=>{
      if(event.key!=='Escape'||event.defaultPrevented||event.target.closest?.('input,textarea,select,[contenteditable="true"],[role="dialog"],dialog,[role="menu"]')||(typeof shellUI!=='undefined'&&shellUI.open))return;
      const focus=anchor;event.preventDefault();pause();if(view.visible(focus))focus.focus({preventScroll:true});
    });
  }
  function refresh(){
    if(!active||disposed)return;
    const keepPractice=practicing;stop({preserveFocus:true});practicing=keepPractice;
    const s=step();if(!s)return;
    if(blocked){suspend(notice);return;}
    if(!accessible()){suspend('Este módulo está congelado. O guia não altera a disponibilidade. Escolha outra trilha na central.');return;}
    if(!matchesDestination(s)){suspend('Você está em outra tela. Use Ir para esta tela quando quiser continuar; os guardas originais continuam valendo.');return;}
    const target=targetFor(s),host=view.selectHost(target,s);
    if(host.foreign){suspend('Outro diálogo está aberto. Resolva o diálogo pelos controles originais e retome o guia.');return;}
    if(!view.visible(target)&&!s.allowRead){suspend('O controle desta etapa ainda não está disponível. Retome quando a tela estiver pronta ou escolha outra trilha.');return;}
    anchor=view.visible(target)?target:null;paused=false;progress.paused=false;initialEpoch=epoch();observedRoute=JSON.stringify(root.JPWNavigation.current());
    draw(progress.steps[s.id]?'ready':'waiting',progress.steps[s.id]?'Etapa já conhecida. Você pode revisar ou seguir.':'Observe o controle e escolha Entendi, pratique opcionalmente ou pule.',anchor);observe();bindPractice();
  }
  function hasSettingsDraft(){
    if(typeof settingsState==='undefined'||!settingsState.open)return false;
    if(typeof settingsProfileState!=='undefined'&&settingsProfileState.editing&&JSON.stringify(settingsProfileState.draft)!==JSON.stringify(settingsProfileState.confirmed))return true;
    if(typeof navOrderDirty==='function'&&navOrderDirty())return true;
    if(typeof mvpNotesAppearanceState!=='undefined'&&mvpNotesAppearanceState.editing&&JSON.stringify(mvpNotesAppearanceState.draft)!==JSON.stringify(mvpNotesAppearanceState.confirmed))return true;
    return false;
  }
  function go(){
    if(!active||disposed||blocked)return false;
    progress.paused=false;if(!persist())return false;
    const s=step();if(hasSettingsDraft()&&(typeof settingsState==='undefined'||s.destination?.settings!==settingsState.active||settingsState.mobileListVisible===true)){suspend('Há uma prévia não salva nas Configurações. Salve ou cancele pelos controles originais antes de continuar o guia.');return false;}if(!accessible()){suspend('Módulo congelado. Escolha outra trilha na central.');return false;}
    // Only a guide gesture can close its own center; unrelated settings/drafts stay owned.
    if(isOwnCenter()&&typeof closeSettingsModal==='function')closeSettingsModal({restoreFocus:false});
    const choice=view.selectHost(targetFor(s),s);
    if(choice.foreign){suspend('Resolva o diálogo atual pelos controles originais antes de navegar.',transitionMode);return false;}
    stop({preserveFocus:true});paused=false;progress.paused=false;let accepted=true;
    const dest=s.destination;
    if(dest?.settings){
      if(typeof settingsState!=='undefined'&&settingsState.open){
        if(settingsState.active!==dest.settings||settingsState.mobileListVisible===true){if(typeof settingsNavigateToLeaf==='function')settingsNavigateToLeaf(dest.settings,{focus:false});else accepted=false;}
      }else if(typeof openSettingsModal==='function'){openSettingsModal(dest.settings,document.activeElement);if(typeof settingsNavigateToLeaf==='function')settingsNavigateToLeaf(dest.settings,{focus:false});}else accepted=false;
    }
    else if(dest){
      const current=root.JPWNavigation.current();
      const resolved=dest.local?root.JPWNavigation.resolve(dest.route):null;
      const sameLocalOwner=!!resolved?.accepted&&current.primary===resolved.primary&&current.screen===resolved.screen;
      if(!sameLocalOwner&&current.canonical!==dest.route){
        // The intentional entry publication may precede selecting the local view.
        // Limit this exception to this synchronous native call and resolved owner;
        // later/foreign accepted publications keep their normal pause semantics.
        deliberateEntry=resolved?.accepted?{generation,canonical:resolved.canonical,primary:resolved.primary,screen:resolved.screen}:null;
        try{accepted=root.JPWNavigation.navigate(dest.route);}finally{deliberateEntry=null;}
      }
      if(accepted&&dest.local)accepted=root.JPWNavigation.navigateLocal(dest.local.surface,dest.local.view);
      if(accepted&&dest.alladin)root.JPWAlladinUI?.selectView(dest.alladin);
    }
    // Deferred guards publish acceptance later. While pending, preserve original ownership.
    const token=generation;requestAnimationFrame(()=>{if(token!==generation||disposed)return;if(accepted)refresh();else suspend('A navegação aguarda sua decisão no diálogo original. Depois de resolvê-lo, use Retomar.');});
    return accepted;
  }
  function start(id){
    init();const selected=catalog.tracks.find(t=>t.id===id);if(!selected||disposed||blocked)return false;
    stop();active=true;paused=false;progress.trackId=id;progress.stepId=selected.steps[0].id;progress.paused=false;if(!persist())return false;return go();
  }
  function resume(){
    init();if(disposed||!step()||blocked)return false;
    progress.paused=false;if(!persist())return false;
    if(isOwnCenter()&&typeof closeSettingsModal==='function')closeSettingsModal({restoreFocus:false});
    stop({preserveFocus:true});active=true;paused=false;refresh();return !paused;
  }
  function pause(message){stop();paused=true;progress.paused=true;notice=typeof message==='string'?message:'Guia pausado. Retomar verifica novamente a tela e os controles atuais.';if(!persist())return false;renderCenter();return true;}
  function move(offset){
    if(!step()||disposed)return;const t=track(),index=t.steps.indexOf(step()),target=t.steps[index+offset];
    if(!target){if(offset>0){if(pause('Trilha concluída. Você pode revisar ou escolher outra trilha na central.'))open();}return;}
    const priorExit=exitMode(step());stop({preserveFocus:true});transitionMode=priorExit;progress.stepId=target.id;active=true;paused=false;progress.paused=false;if(!persist())return false;return go();
  }
  function skip(){if(!step()||disposed||blocked)return;if(!mark('skipped',null))return;move(1);}
  function next(){if(paused||!progress.steps[step()?.id])return;move(1);}
  function practice(){
    if(paused||!step()?.practice||disposed||blocked)return false;
    practicing=true;bindPractice();draw('waiting','Prática em observação. Use o controle original; cancelar, recusa ou gravação desconhecida mantém a prática pendente.',anchor);return true;
  }
  function review(){if(!track())return false;return start(track().id);}
  function restart(){
    stop();const result=store.reset(catalog,{expectedRaw:raw});
    if(!result.ok){notice='O progresso não foi removido: '+result.reason+'. A base anterior foi preservada.';if(result.reason==='concurrent-change')readProgress();renderCenter();return false;}
    raw=null;progress=store.empty(catalog);blocked=false;storage='local';active=false;paused=true;notice='Progresso do guia reiniciado. Seus dados e outras preferências foram preservados.';renderCenter();return true;
  }
  function revalidate(reason){
    if(disposed){if(reason!=='boot')return;stop();disposed=false;initialized=false;active=false;paused=true;init();return;}
    stop();paused=true;progress.paused=true;initialEpoch=epoch();notice='Guia pausado após mudança da base'+(reason?' ('+reason+').':'.')+' Retomar verifica a tela novamente.';renderCenter();
  }
  function disposeForSession(){stop();lifecycleCleanup.forEach(fn=>fn());lifecycleCleanup=[];disposed=true;active=false;paused=true;progress=store.empty(catalog);raw=null;blocked=false;storage='memory';notice='Sessão encerrada. O guia não gravará progresso pendente.';renderCenter();}
  const actions={start,resume,review,restart,go,understand:orientation,practice,back:()=>move(-1),next,skip,pause:()=>pause()};
  function init(){
    if(initialized)return true;initialized=true;readProgress();initialEpoch=epoch();paused=true;progress.paused=true;
    lifecycleCleanup.push(root.JPWNavigation.subscribe(event=>{
      if(!active||paused||disposed)return;
      if(deliberateEntry&&deliberateEntry.generation===generation&&event.current.canonical===deliberateEntry.canonical&&event.current.primary===deliberateEntry.primary&&event.current.screen===deliberateEntry.screen)return;
      const s=step(),foreign=s.destination?(!s.destination.settings&&!matchesDestination(s,event.current)):observedRoute!==null&&JSON.stringify(event.current)!==observedRoute;
      schedule(()=>{if(foreign||!matchesDestination(s))suspend('Você mudou de tela. Retome quando quiser continuar esta orientação.');else refresh();});
    }));
    const stopAvailability=root.JPWModuleAvailability?.subscribe(()=>{renderCenter();if(active&&!paused&&!accessible())suspend('Este módulo foi congelado. Escolha outra trilha; o progresso foi preservado.');});
    if(stopAvailability)lifecycleCleanup.push(stopAvailability);
    const storageChanged=event=>{
      if(disposed)return;
      if(event.key===store.KEY||event.key===null){stop();readProgress();paused=true;progress.paused=true;notice='O progresso mudou em outra aba. Confira a central e retome quando quiser.';renderCenter();}
      else if(['jpwealth_v9_state','jpwealth_base_epoch_v1'].includes(event.key))revalidate('outra aba');
    };
    root.addEventListener('storage',storageChanged);lifecycleCleanup.push(()=>root.removeEventListener('storage',storageChanged));
    renderCenter();return true;
  }
  root.JPWLearningGuide=Object.freeze({open,start,resume,pause,restart,snapshot,init,renderCenter,disposeForSession,revalidate});
  init();
})(window);

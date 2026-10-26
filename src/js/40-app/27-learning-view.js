// Apresentação sem acesso ao estado financeiro, roteamento ou armazenamento.
(function(root){
  'use strict';
  let card=null,anchor=null,oldDescription=null,addedClass=false,annotated=false,removeLayout=[],frame=0,pendingFocus=null,currentHost=null,reservedRoot=null,reservedHost=null;
  let speechTimer=0,speechGeneration=0,speechState=null,shownModel=null,removeSpeechPreference=null;
  function cancelSpeech(){speechGeneration++;removeSpeechPreference?.();removeSpeechPreference=null;if(speechTimer){root.clearTimeout(speechTimer);speechTimer=0;}}
  function updateControls(model){
    if(!card)return;
    const speaking=!!speechState&&!speechState.complete,more=!!model.speech&&model.speechIndex<model.speechTotal-1;
    const next=card.querySelector('#jpwLearningNext');if(next){next.hidden=!model.unavailable&&!!model.speech&&(speaking||more);next.disabled=next.hidden||model.status==='paused'||(!model.done&&!model.unavailable);next.textContent=speaking?'Mostrar fala':more?'Continuar fala':model.unavailable?(model.lastChapter?'Encerrar apresentação':'Continuar para a próxima área'):model.last?'Encerrar apresentação':'Próximo';}
    const understand=card.querySelector('#jpwLearningUnderstand');if(understand){const needsAction=model.step.kind==='action'&&!model.step.allowRead;understand.hidden=!!model.unavailable;understand.disabled=model.status==='paused'||needsAction&&!speaking&&!more;understand.textContent=speaking?'Mostrar fala':more?'Continuar fala':needsAction?'Use o controle original':'Entendi (somente leitura)';}
    const practice=card.querySelector('#jpwLearningPracticeStart');if(practice){practice.hidden=!!model.unavailable;practice.disabled=model.status==='paused'||model.practicing;practice.textContent=model.practicing?'Prática em observação':'Praticar com meus dados (opcional)';}
    const go=card.querySelector('#jpwLearningGo');if(go)go.hidden=!!model.unavailable||!model.step.destination;
    const skip=card.querySelector('#jpwLearningSkip');if(skip)skip.hidden=!!model.unavailable;
  }
  function revealSpeech(){
    if(!speechState||speechState.complete)return false;cancelSpeech();speechState.complete=true;speechState.offset=speechState.characters.length;
    const copy=card?.querySelector('#jpwLearningSpeech');if(copy)copy.textContent=speechState.text;updateControls(shownModel);queuePosition();return true;
  }
  function narrate(model){
    cancelSpeech();speechState=null;if(!model.speech)return;
    const preference=root.matchMedia?.('(prefers-reduced-motion: reduce)');
    const text=model.speech,characters=Array.from(text),complete=model.status==='paused'||!!model.speechFull||!!preference?.matches;
    speechState={text,characters,offset:complete?characters.length:0,complete,key:model.speechKey};
    const copy=card.querySelector('#jpwLearningSpeech');copy.textContent=complete?text:'';
    const token=speechGeneration;
    const tick=()=>{speechTimer=0;if(token!==speechGeneration||!card||!speechState)return;speechState.offset++;copy.textContent=characters.slice(0,speechState.offset).join('');if(speechState.offset>=characters.length){speechState.complete=true;updateControls(shownModel);}else speechTimer=root.setTimeout(tick,1000/30);queuePosition();};
    if(!complete){speechTimer=root.setTimeout(tick,1000/30);const changed=event=>{if(event.matches)revealSpeech();};preference?.addEventListener?.('change',changed);removeSpeechPreference=()=>preference?.removeEventListener?.('change',changed);}
  }
  function visible(el){return !!el&&!el.hidden&&!el.disabled&&!el.closest('[hidden],[inert],[aria-hidden="true"]')&&el.getClientRects().length>0&&getComputedStyle(el).visibility!=='hidden'&&getComputedStyle(el).display!=='none';}
  function openDialogs(){
    return [...document.querySelectorAll('[role="dialog"],dialog[open],#modalBox')].filter(el=>visible(el)&&
      (el.closest('#modalOverlay')?el.closest('#modalOverlay').classList.contains('show'):true));
  }
  function selectHost(target,step){
    const dialogs=openDialogs();
    let host=target?.closest('[role="dialog"],dialog,#modalBox');
    if(host&&!visible(host))host=null;
    const follows=node=>(step?.followHosts||[]).some(selector=>[...document.querySelectorAll(selector)].includes(node));
    const owned=!!host&&follows(host);
    // Allowed sibling modals may belong to the same native task; unrelated dialogs keep ownership.
    const foreign=dialogs.some(el=>el!==host&&!(host&&el.contains(host))&&!(owned&&follows(el))&&!(host&&host.contains(el)&&!visible(el)));
    if(foreign)return {host:null,foreign:true};
    if(host)return {host:host.id==='mvpNotesOverlay'?(document.getElementById('mvpNotesDrawer')||host):host,foreign:false};
    // The compact app menu is itself a focus host; use the app's own resolver.
    if(typeof shellUI!=='undefined'&&shellUI.open&&typeof shellMenuRoot==='function')return {host:shellMenuRoot(),foreign:false};
    return {host:document.body,foreign:false};
  }
  function el(tag,text,id){const node=document.createElement(tag);if(id)node.id=id;if(text!==undefined)node.textContent=text;return node;}
  function ownActivation(node){
    node.addEventListener('keydown',event=>{
      if((event.key==='Enter'||event.key===' ')&&!event.ctrlKey&&!event.metaKey&&!event.altKey&&!event.shiftKey)event.stopPropagation();
    });return node;
  }
  function button(id,text,handler){const node=el('button',text,id);node.type='button';node.className='reset-btn';node.addEventListener('click',handler);
    return ownActivation(node);}
  function center(container,model,actions){
    if(!container)return false;
    let center=container.querySelector('#jpwLearningCenter');if(!center){center=el('section',undefined,'jpwLearningCenter');center.setAttribute('aria-label','Guia do site');container.appendChild(center);}
    center.replaceChildren(el('h2','Conhecer com Dante'),el('p','Vou acompanhar você pelos controles reais do JP Wealth. Você escolhe o ritmo; ler, pular e praticar são resultados diferentes.'));
    const portrait=el('img');portrait.className='jpw-dante-center';portrait.alt='Dante, mascote do JP Wealth';portrait.src=root.JPW_PORTABLE_IMAGES?.['assets/dante-guide.png']||'assets/dante-guide.png';center.appendChild(portrait);
    const notice=el('p',model.notice||'Progresso local deste navegador, separado dos seus dados e do backup financeiro.','jpwLearningCenterStatus');notice.setAttribute('role','status');center.appendChild(notice);
    const controls=el('div');controls.className='jpw-learning-controls';
    const resume=button('jpwLearningResume','Continuar',actions.resume);resume.disabled=!model.trackId;
    const review=button('jpwLearningReview','Rever lições',actions.review);review.disabled=!model.trackId;
    const restart=button('jpwLearningRestart','Recomeçar',actions.restart);
    controls.append(button('jpwLearningStartJourney','Começar jornada',()=>actions.startJourney()),resume,review,restart);center.appendChild(controls);
    const index=el('nav',undefined,'jpwLearningJourney');index.setAttribute('aria-label','Índice da jornada');
    for(const chapter of model.journey||[]){const entry=el('article');entry.className='jpw-learning-chapter';const select=button(undefined,chapter.title,()=>actions.startJourney({stepId:chapter.stepIds[0]}));select.dataset.learningChapter=chapter.id;entry.appendChild(select);entry.appendChild(el('p',`${chapter.seen}/${chapter.stepIds.length} leituras ou ações observadas · ${chapter.skipped} puladas · ${chapter.practiced} práticas confirmadas${chapter.frozen?' · Área congelada; é possível seguir sem registrar.':''}`));const lessons=el('details');lessons.appendChild(ownActivation(el('summary','Escolher uma lição')));for(const lesson of chapter.lessons||[]){const choose=button(undefined,lesson.title,()=>actions.startJourney({stepId:lesson.id}));choose.dataset.learningStep=lesson.id;lessons.appendChild(choose);}entry.appendChild(lessons);index.appendChild(entry);}
    center.appendChild(index);center.appendChild(el('h3','Explorar uma trilha'));
    const grid=el('div');grid.className='jpw-learning-tracks';
    for(const track of model.tracks){
      const item=el('article');item.className='jpw-learning-track';item.append(el('h3',track.title),el('p',track.description));
      item.appendChild(el('p',`${track.seen}/${track.total} leituras ou ações observadas · ${track.skipped} puladas · ${track.practiced} práticas confirmadas${track.frozen?' · Módulo congelado; o guia não o ativa.':''}`));
      const start=button(undefined,track.frozen?'Consultar limitação':'Começar trilha',()=>actions.start(track.id));start.dataset.learningTrack=track.id;item.appendChild(start);grid.appendChild(item);
    }
    center.appendChild(grid);return true;
  }
  function restoreAnchor(){
    if(anchor&&annotated){if(oldDescription===null)anchor.removeAttribute('aria-describedby');else anchor.setAttribute('aria-describedby',oldDescription);if(addedClass)anchor.classList.remove('jpw-learning-target');}
    anchor=null;oldDescription=null;addedClass=false;annotated=false;
  }
  function setAnchor(target,status){
    restoreAnchor();anchor=target;
    if(anchor&&status!=='paused'){annotated=true;oldDescription=anchor.getAttribute('aria-describedby');anchor.setAttribute('aria-describedby',[oldDescription,'jpwLearningExpected'].filter(Boolean).join(' '));addedClass=!anchor.classList.contains('jpw-learning-target');anchor.classList.add('jpw-learning-target');}
  }
  function hide(options={}){
    cancelSpeech();speechState=null;shownModel=null;
    const focused=document.activeElement;
    if(options.preserveFocus){if(focused&&card?.contains(focused))pendingFocus={id:focused.id,host:currentHost||card.parentElement};}else pendingFocus=null;
    if(frame){cancelAnimationFrame(frame);frame=0;}removeLayout.forEach(fn=>fn());removeLayout=[];restoreAnchor();card?.remove();card=null;currentHost=null;reservedRoot=null;reservedHost=null;
  }
  function compact(){
    if(card.querySelector('#jpwLearningDetails'))return;
    const details=el('details',undefined,'jpwLearningDetails');
    details.appendChild(ownActivation(el('summary','Orientação e resultado esperado','jpwLearningDetailsSummary')));
    const information=card.querySelector('#jpwLearningDetailsBody');if(information)details.appendChild(information);
    card.insertBefore(details,card.querySelector('#jpwLearningStatus'));
  }
  function flow(){
    compact();card.dataset.learningLayout='flow';card.style.position='static';card.style.left='auto';card.style.top='auto';card.style.width='auto';card.style.maxWidth='100%';card.style.maxHeight='none';
    // Keep dialog focus ownership. On a normal screen, insert beside the stable
    // teaching container so an original innerHTML repaint cannot remove the coach.
    if(!reservedHost&&currentHost===document.body&&anchor?.parentElement&&!anchor.closest('button,input,select,textarea,summary'))anchor.parentElement.insertBefore(card,anchor);
    position();
  }
  function reserveTaskFlow(model){
    const root=model.followRoot;
    if(!root){
      if(reservedHost){reservedRoot=null;reservedHost=null;currentHost.appendChild(card);card.dataset.learningLayout='floating';Object.assign(card.style,{position:'fixed',left:'0px',top:'0px',marginLeft:'0px',width:'360px',maxWidth:'calc(100vw - 24px)',maxHeight:'none'});}
      return false;
    }
    const form=root.matches?.('form');
    const scrollRegion=form?null:[...root.querySelectorAll('*')].find(node=>node!==card&&!card.contains(node)&&visible(node)&&/auto|scroll/.test(getComputedStyle(node).overflowY||'')&&node.querySelector('input,select,textarea,button'));
    const region=form?root.parentElement:(scrollRegion||root);if(!region)return false;
    reservedRoot=root;reservedHost=region;
    const before=form?root:[...region.children].find(node=>node!==card);
    if(card.parentElement!==region||before&&card.nextElementSibling!==before)region.insertBefore(card,before||null);
    flow();return true;
  }
  function clippingBounds(viewport){
    const bounds={...viewport};
    for(let node=card.parentElement;node&&node!==document.body;node=node.parentElement){
      const css=getComputedStyle(node),r=node.getBoundingClientRect();
      const sx=r.width/(node.offsetWidth||r.width||1),sy=r.height/(node.offsetHeight||r.height||1);
      if(/auto|scroll|hidden|clip/.test(css.overflowX||'')){
        const x=r.left+(node.clientLeft||0)*sx;
        bounds.left=Math.max(bounds.left,x);bounds.right=Math.min(bounds.right,x+(node.clientWidth||node.offsetWidth||r.width)*sx);
      }
      if(/auto|scroll|hidden|clip/.test(css.overflowY||'')){
        const y=r.top+(node.clientTop||0)*sy;
        bounds.top=Math.max(bounds.top,y);bounds.bottom=Math.min(bounds.bottom,y+(node.clientHeight||node.offsetHeight||r.height)*sy);
      }
      // Bounding rectangles do not define an inverse for a rotated/skewed plane.
      // Use natural guide-only flow rather than guessing that coordinate system.
      const transform=css.transform||'none',matrix=transform.match(/^matrix\(([^)]+)\)$/);
      if((matrix&&(Number(matrix[1].split(',')[1])!==0||Number(matrix[1].split(',')[2])!==0))||transform.startsWith('matrix3d(')||css.perspective&&css.perspective!=='none')bounds.unsupported=true;
    }
    return bounds;
  }
  function position(){
    frame=0;if(!card)return;
    const viewport=root.visualViewport,left=viewport?.offsetLeft||0,top=viewport?.offsetTop||0,width=viewport?.width||root.innerWidth,height=viewport?.height||root.innerHeight;
    const bounds=clippingBounds({left,top,right:left+width,bottom:top+height});
    if(card.dataset.learningLayout==='flow'){
      const box=card.getBoundingClientRect(),sx=box.width/(card.offsetWidth||box.width||1),pad=12;
      // Natural flow keeps its original focus/scroll owner, but layout width
      // alone ignores browser zoom. Recompute only this guide surface's bounds.
      const origin=box.left-(parseFloat(card.style.marginLeft)||0)*sx;
      const x=Math.max(origin,bounds.left+pad),parentRight=card.parentElement.getBoundingClientRect().right;
      card.style.marginLeft=(x-origin)/sx+'px';
      card.style.width=Math.max(24,Math.min(360,(Math.min(bounds.right,parentRight)-x-pad)/sx))+'px';
      const resized=card.getBoundingClientRect(),sy=resized.height/(card.offsetHeight||resized.height||1);
      card.style.maxHeight=Math.max(24,(bounds.bottom-resized.top-pad)/sy)+'px';
      card.style.overflow='auto';
      return;
    }
    // This original sheet has a filtered scrolling containing block and no safe
    // side margin for the full coach. Natural compact flow cannot intercept its
    // five selects or Confirm/Cancel, and never enlarges horizontal scroll space.
    if(currentHost?.id==='mvpNotesNewBox'){flow();return;}
    if(bounds.unsupported||bounds.right-bounds.left<48||bounds.bottom-bounds.top<48){flow();return;}
    const before=card.getBoundingClientRect(),sx=before.width/(card.offsetWidth||before.width||1),sy=before.height/(card.offsetHeight||before.height||1),pad=12;
    card.style.maxHeight=Math.max(24,(bounds.bottom-bounds.top-pad*2)/sy)+'px';card.style.width=Math.max(24,Math.min(360,(bounds.right-bounds.left-pad*2)/sx))+'px';
    const box=card.getBoundingClientRect(),w=box.width,h=box.height;
    // Measure the current fixed coordinate basis through the card itself. This
    // includes border/scroll offsets and axis-aligned transforms without moving
    // it temporarily to zero on each scroll (which would change scroll extents).
    const originX=box.left-(parseFloat(card.style.left)||0)*sx,originY=box.top-(parseFloat(card.style.top)||0)*sy;
    const clamp=(value,lo,hi)=>Math.max(lo,Math.min(value,Math.max(lo,hi)));
    const r=anchor?.getBoundingClientRect();
    const candidates=r?[{x:r.right+pad,y:r.top},{x:r.left-w-pad,y:r.top},{x:r.left,y:r.bottom+pad},{x:r.left,y:r.top-h-pad},{x:bounds.right-w-pad,y:bounds.bottom-h-pad},{x:bounds.left+pad,y:bounds.top+pad}]:[{x:bounds.right-w-pad,y:bounds.bottom-h-pad}];
    let best=null;
    for(const point of candidates){
      point.x=clamp(point.x,bounds.left+pad,bounds.right-w-pad);point.y=clamp(point.y,bounds.top+pad,bounds.bottom-h-pad);
      const overlap=r?Math.max(0,Math.min(point.x+w,r.right)-Math.max(point.x,r.left))*Math.max(0,Math.min(point.y+h,r.bottom)-Math.max(point.y,r.top)):0;
      if(!best||overlap<best.overlap)best={...point,overlap};
    }
    if(best.overlap>0){flow();return;}
    card.style.left=(best.x-originX)/sx+'px';card.style.top=(best.y-originY)/sy+'px';
  }
  function queuePosition(){if(!frame)frame=requestAnimationFrame(position);}
  function coach(model,actions){
    const nextHost=selectHost(model.anchor,model.step);
    if(card&&!nextHost.foreign&&model.status!=='paused'&&shownModel?.status!=='paused'&&(currentHost===(nextHost.host||document.body)||model.followingHost||shownModel?.followingHost)&&shownModel?.speechKey===model.speechKey&&shownModel?.speech===model.speech&&shownModel?.step.id===model.step.id){
      const desiredHost=nextHost.host||document.body;
      if(currentHost!==desiredHost){const focus=document.activeElement,ownedFocus=card.contains(focus);currentHost=desiredHost;currentHost.appendChild(card);if(ownedFocus&&document.activeElement!==focus)focus.focus({preventScroll:true});}
      if(anchor!==model.anchor){setAnchor(model.anchor,model.status);if(!document.body.contains(card))currentHost.appendChild(card);}
      shownModel=model;reserveTaskFlow(model);card.dataset.learningStatus=model.status;const status=card.querySelector('#jpwLearningStatus');if(status.textContent!==model.notice)status.textContent=model.notice;updateControls(model);queuePosition();return true;
    }
    hide({preserveFocus:true});shownModel=model;
    const focusIntent=pendingFocus;pendingFocus=null;
    const target=model.anchor,choice=selectHost(target,model.step);if(choice.foreign)return false;
    anchor=target;currentHost=choice.host||document.body;card=el('aside',undefined,'jpwLearningCoach');card.className='jpw-learning-coach';card.dataset.learningLayout='floating';card.style.position='fixed';card.style.left='0px';card.style.top='0px';card.dataset.learningStep=model.step.id;card.dataset.learningStatus=model.status;card.setAttribute('aria-label','Orientação do guia');
    card.append(el('p',model.count,'jpwLearningCount'),el('h3',model.step.title,'jpwLearningTitle'));
    if(model.speech){const speech=el('div');speech.className='jpw-dante-speech';const image=el('img');image.alt='';image.className='jpw-dante-guide';image.src=(typeof SETTINGS_PROFILE_AVATARS!=='undefined'?SETTINGS_PROFILE_AVATARS.find(avatar=>avatar.id==='dante-mascote')?.avatarDataUrl:null)||root.JPW_PORTABLE_IMAGES?.['assets/dante-guide.png']||'assets/dante-guide.png';const copy=el('p','', 'jpwLearningSpeech');copy.setAttribute('aria-hidden','true');const accessible=el('p',model.speech,'jpwLearningSpeechAccessible');accessible.className='jpw-learning-sr';accessible.setAttribute('role','status');accessible.setAttribute('aria-live','polite');accessible.setAttribute('aria-atomic','true');speech.append(image,copy,accessible);if(typeof actions.speech==='function')speech.addEventListener('click',actions.speech);card.appendChild(speech);}
    const information=el('div',undefined,'jpwLearningDetailsBody');information.append(el('p',model.unavailable?'Esta área está congelada nesta versão.':model.step.objective,'jpwLearningObjective'),el('p',model.unavailable?'Você pode seguir sem abrir os controles desta área.':model.step.instruction,'jpwLearningBody'),el('p',model.unavailable?'Seguir preserva os registros anteriores e não confirma leitura ou prática.':'Resultado esperado: '+model.step.expected,'jpwLearningExpected'));card.appendChild(information);
    const status=el('p',model.notice,'jpwLearningStatus');status.setAttribute('role','status');status.setAttribute('aria-live','polite');card.appendChild(status);
    const controls=el('div');controls.className='jpw-learning-controls';
    const go=button('jpwLearningGo','Ir para esta tela',actions.go);go.hidden=!model.step.destination;controls.appendChild(go);
    const understand=button('jpwLearningUnderstand','Entendi (somente leitura)',actions.understand);understand.hidden=model.step.kind==='action'&&!model.step.allowRead;understand.disabled=model.status==='paused';controls.appendChild(understand);
    if(model.step.practice&&!model.unavailable){card.appendChild(el('p',model.step.practiceInstruction,'jpwLearningPracticeInstruction'));const practice=button('jpwLearningPracticeStart',model.practicing?'Prática em observação':'Praticar com meus dados (opcional)',actions.practice);practice.disabled=model.status==='paused'||model.practicing;controls.appendChild(practice);}
    const back=button('jpwLearningBack','Voltar',actions.back);back.disabled=model.index===0;
    const next=button('jpwLearningNext',model.last?'Concluir trilha':'Próximo',actions.next);next.disabled=!model.done||model.status==='paused';
    controls.append(back,next,button('jpwLearningSkip','Pular esta orientação',actions.skip),button('jpwLearningPause','Pausar',actions.pause));card.appendChild(controls);
    currentHost.appendChild(card);narrate(model);updateControls(model);if(!reserveTaskFlow(model))position();
    setAnchor(target,model.status);
    for(const [target,event,capture] of [[root,'resize',false],[root,'scroll',true],[root.visualViewport,'resize',false],[root.visualViewport,'scroll',false]])if(target){target.addEventListener(event,queuePosition,{passive:true,capture});removeLayout.push(()=>target.removeEventListener(event,queuePosition,capture));}
    // Initial placement precedes focus restoration, avoiding focus-scroll to an
    // unplaced or clipped card. Later placement is bounded by resize/scroll RAFs.
    const focused=document.activeElement;
    if(focusIntent&&focusIntent.host===(choice.host||document.body)&&!focused?.closest?.('input,textarea,select,[contenteditable="true"]')){
      const restored=[focusIntent.id,'jpwLearningUnderstand','jpwLearningGo','jpwLearningSkip'].map(id=>document.getElementById(id)).find(node=>node&&!node.disabled&&!node.hidden);
      if(restored)restored.focus({preventScroll:true});
    }return true;
  }
  root.JPWLearningView=Object.freeze({center,coach,hide,visible,selectHost,revealSpeech});
})(window);

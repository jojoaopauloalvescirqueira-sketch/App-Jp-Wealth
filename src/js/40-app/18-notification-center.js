// NOTIFICATIONS-CENTER-01: presentation only. No persisted inbox, domain writer,
// permission request, economic fetch or replacement of confirm/prompt.
// The native alert bridge preserves its original synchronous call/return and
// adds an unclassified session message; it never interprets success from words.
(function initNotificationCenter(){
  if(window.JPWNotifications) return;
  const el=id=>document.getElementById(id);
  const names={system:'Sistema',forex:'Forex',pf:'Finanças Pessoais',alladin:'Alladin',research:'Research',notes:'Notas'};
  const rank={critical:0,warning:1,info:2};
  const live=new Map(), history=[], seen=new Map();
  let stateRef=S, serial=0, scheduled=false, rendering=false, paused=false, lastView='', returnFocus=true;
  let focusOpener=null;
  const text=value=>typeof value==='string'?value:'';
  const visible=node=>!!node && !node.hidden && node.getClientRects().length>0;
  const modelArea=node=>{
    if(node?.closest('#mvpNotesOverlay,#mvpNotesLauncher')) return 'notes';
    if(node?.closest('#settingsModal,#settingsOverlay')) return 'system';
    if(node?.closest('#alladinModalBox')) return 'alladin';
    const primary=node?.closest('.screen')?.id;
    return primary==='finpes'?'pf':primary==='alladin'?'alladin':primary==='research'?'research':
      ['exec','op','contab','fxplan','contas','check','onboarding'].includes(primary)?'forex':'system';
  };
  function currentArea(){
    if(el('mvpNotesOverlay')?.getAttribute('aria-hidden')==='false') return 'notes';
    if(el('settingsOverlay')?.getAttribute('aria-hidden')==='false') return 'system';
    if(visible(el('alladinModalBox'))) return 'alladin';
    const primary=window.JPWNavigation?.current().primary;
    return primary==='personal-finance'?'pf':names[primary]?primary:'system';
  }
  function currentGeneration(){
    if(stateRef===S) return;
    stateRef=S; live.clear(); history.length=0; seen.clear(); lastView='';
  }
  function record(message,contextArea='system'){
    currentGeneration();
    const body=text(message).trim().slice(0,1200);
    if(!body) return;
    // Identical immediate repaint is not another action. Actual subsequent
    // alerts still have their own timestamp. Nothing leaves this browser tab.
    const prior=history[0], now=Date.now();
    if(prior && prior.body===body && prior.contextArea===contextArea && now-prior.at<500) return;
    // The shared producer has no domain metadata. Screen context is not proof
    // of the origin of an async operation or cross-tab system message.
    history.unshift({id:'activity:'+ ++serial,area:'system',contextArea,kind:'event',severity:'info',
      title:'Mensagem do aplicativo',body,at:now,revision:String(serial),go:null});
    if(history.length>80){ const old=history.pop(); seen.delete(old.id); }
    schedule();
  }
  function add(next,id,area,severity,title,body,go,revision){
    next.set(id,{id,area,kind:'live',severity,title,body,go,revision:revision||severity+'|'+title+'|'+body});
  }
  function collectSystem(next){
    const failure=typeof jpWealthPersistenceFailure==='object' && jpWealthPersistenceFailure;
    if(jpWealthPersistenceOutcomeIsUnknown())
      add(next,'system:persistence','system','critical','Gravação não confirmada',
        'O resultado da gravação é desconhecido. Novas gravações permanecem bloqueadas; confira a recuperação antes de tentar novamente.','backup');
    else if(typeof jpWealthLoadRecoveryActive==='function' && jpWealthLoadRecoveryActive())
      add(next,'system:persistence','system','critical','Recuperação da base necessária',
        'A base não pôde ser carregada com segurança. O aviso de recuperação e as proteções continuam ativos.','backup');
    else if(failure?.active)
      add(next,'system:persistence','system','critical',failure.kind==='conflict'?'Outra aba atualizou a base':'Falha ao gravar neste navegador',
        'Confira o aviso de armazenamento. Esta mensagem não confirma o salvamento das alterações pendentes.','backup',failure.kind);
    else if(jpWealthPersistenceIsBlocked())
      add(next,'system:persistence','system','warning','Gravação suspensa',
        'O bloqueio do aplicativo permanece ativo. Ler a notificação não libera gravações.','backup');
    const backup=dgBackupStatus();
    if(backup.due || backup.state==='unknown'){
      const days=dgBackupAgeDays();
      add(next,'system:backup','system',backup.tone==='bad'?'critical':'warning',backup.text,
        backup.state==='unknown'?'Confira a gravação e a data antes de considerar o backup confirmado.':
          days===null?'Ainda não há confirmação de backup.':days+' dias desde a última confirmação de backup.',
        'backup',backup.state+'|'+backup.at);
    }
    if(typeof settingsProfileState==='object' && ['error','blocked'].includes(settingsProfileState.status))
      add(next,'system:profile','system','warning','Perfil local precisa de atenção',
        'Confira a mensagem de Configurações → JP Wealth Account. O perfil e o rascunho não são alterados pela central.','profile',settingsProfileState.status+'|'+settingsProfileState.note);
  }
  function collectForex(next){
    const c=compute(), clearance=getOperationalClearance(c), onboarding=getOnboardingCompletionState();
    if(clearance.status!=='clear' || !onboarding.complete)
      add(next,'forex:clearance','forex',['blocked','reduce'].includes(clearance.status)||onboarding.severity==='critical'?'critical':'warning',
        clearance.status==='clear'?'Formulário de Início possui pendências':clearance.title,
        [...(clearance.status==='clear'?[]:[clearance.subtitle,...clearance.reasons]),
          ...(!onboarding.complete?[onboardingCompletionText(onboarding)]:[])].join('\n'),'forex-overview');
    // The detailed completion model can disagree with the summary's done flag.
    // Preserve both producers in one card; never change their financial rules.
    const contexts=S.forex?.accountContexts?.accounts||{};
    for(const [accountId,account] of Object.entries(contexts)){
      const registration=(S.accounts||[]).find(a=>a?.forexAccountId===accountId);
      for(const [periodId,period] of Object.entries(account.periods||{})){
        const orders=(period.phases||[]).flatMap(phase=>Array.isArray(phase.orders)?phase.orders:[]);
        const review=orders.filter(o=>o&&(o.needsReview||o.stopPhaseWarning));
        if(review.length)add(next,'forex:order-review:'+accountId+':'+periodId,'forex','warning',
          'Ordens aguardam revisão · '+(registration?.nome||accountId),
          review.length+' ordem(ns) · período '+period.startedAt+' · '+period.currency+'.',
          'forex-operation@'+accountId+'@'+periodId);
      }
    }
    if(S.protocolBreaches>0) add(next,'forex:protocol','forex','warning','Registros de quebra de protocolo',
      S.protocolBreaches+' registro(s) no ciclo. Este total não indica novos eventos nesta sessão.','forex-operation');
    if(typeof staleInfo==='function' && typeof daysStale==='function' && Array.isArray(S.instruments) && S.instruments.length){
      const worst=S.instruments.reduce((a,b)=>daysStale(a.updated)>=daysStale(b.updated)?a:b);
      const status=staleInfo(worst.updated);
      if(status.cls!=='fresh') add(next,'forex:quotes','forex','warning','Cotações de referência',status.label,'forex-preparation');
    }
    if(window.JPWMarket?.usdBrl){
      const q=JPWMarket.usdBrl.get();
      if(q.status==='unavailable'||q.status==='stale') add(next,'forex:usdbrl','forex','warning','Referência USD/BRL',
        q.status==='unavailable'?'Cotação indisponível. Confira o Planejamento.':'A referência está desatualizada. Confira as datas no Planejamento.',
        'forex-planning',q.status);
    }
  }
  function collectPersonalFinance(next){
    const reason=pfWriteBlockReason();
    if(reason){ add(next,'pf:compatibility','pf','critical','Finanças Pessoais em modo de leitura',
      'A unidade armazenada não é suportada. O módulo mantém seus bloqueios de edição.','pf'); return; }
    const pending=pfPendingBefore(pfCurrentMonthKey());
    if(pending.length) add(next,'pf:pending','pf','warning','Pendências de meses anteriores',
      pending.map(p=>p.key+': '+p.despesas+' despesa(s) e '+p.notas+' nota(s) pendente(s).').join('\n'),'pf-monthly');
    const lines=(S.personalFinance?.creditLines||[]).filter(Boolean);
    const excess=lines.filter(line=>pfCreditLineDerived(line).estouro);
    if(excess.length) add(next,'pf:credit','pf','warning','Crédito acima do limite informado',
      excess.length+' linha(s) sinalizada(s) pelo módulo. Isso não classifica inadimplência.','pf-debts');
  }
  function collectAlladin(next){
    const compat=JPWAlladin.compat();
    if(compat.readOnly){
      add(next,'alladin:compatibility','alladin','critical','Alladin em modo de leitura',
        'A versão dos dados é posterior à suportada. Nenhuma edição será liberada pela central.','alladin');
      return; // The ledger refusal is the same compatibility condition.
    }
    const ledger=JPWAlladin.leitura.ledger();
    // Transaction readability alone does not prove that balances/positions can
    // be derived. Ask the same readers as Alladin, without summing here.
    let issue=!ledger.available || ledger.quality==='BLOCKING'?{source:'ledger',issues:ledger.issues}:null;
    if(!issue){
      const positions=JPWAlladin.leitura.posicoes();
      if(!positions.available)issue={source:'positions',issues:positions.issues};
    }
    if(!issue)for(const account of JPWAlladin.leitura.cashAccounts()){
      const balance=JPWAlladin.leitura.saldoDeCaixa(account.cashAccountId);
      if(!balance.available){issue={source:'balance',id:account.cashAccountId,issues:balance.issues};break;}
    }
    if(issue)
      add(next,'alladin:quality','alladin','critical','Integridade do Alladin precisa de atenção',
        'Uma leitura de lançamentos, posições ou saldos foi recusada. Confira os problemas no próprio módulo; ausência de leitura não significa saldo zero.','alladin',JSON.stringify(issue));
  }
  function collectCalendar(next){
    const cache=ffNewsReadCache(), issue=ffNewsCacheIssue(), now=Date.now();
    const outdated=cache && now-cache.fetchedAt>FF_NEWS_MAX_AGE_MS;
    if(!cache || issue || ffNewsLastError || outdated)
      add(next,'calendar:status','research',!cache && !ffNewsLastError && !issue?'info':'warning',
        !cache?'Calendário sem dados disponíveis':'Calendário precisa de atualização',
        ffNewsStatusText(cache)+(outdated?' · O cache excedeu o prazo de atualização.':''),
        'calendar',[!!cache,issue,ffNewsLastError,!!outdated].join('|'));
    if(!cache) return;
    for(const event of cache.events){
      const when=new Date(event.date), ms=when.getTime()-now;
      if(ms<0 || !ffNewsIsToday(when)) continue;
      const id='calendar:event:'+event.country+'|'+event.date+'|'+event.title;
      const imminent=ms<=FF_NEWS_IMMINENT_MS;
      add(next,id,'research',imminent?'warning':'info',
        (imminent?'Em breve · ':'Hoje · ')+event.title,
        event.country+' · '+when.toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})+
        ' · '+ffNewsCountdownLabel(ms)+(outdated?' · fonte pendente de atualização':''),
        'calendar',id+'|'+imminent+'|'+!!outdated);
      next.get(id).when=when.getTime();
    }
  }
  const localSources=[
    ['#ncFormErr,#ncStatus.err','research','NoCoda','nocoda'],
    ['#pvNewStudyErr,#pvFormErr','research','Pivots','pivots'],
    ['#mvpNotesNewError','notes','Notas','notes'],
    ['#mvpNotesCopyLive,#mvpNotesExportLive','notes','Cópia e exportação de Notas','notes','info'],
    ['#fxFetchStatus.err,#fxFetchStatus.warn','forex','Cotações','forex-preparation'],
    ['#fxpCreateErr,#fxpPlanningErr,#fxpActErr,#fxpCErr','forex','Planejamento','forex-planning'],
    ['#alladinModalBox .session-error,#alladinModalBox .session-warning','alladin','Formulário Alladin',null],
    ['#fbAllocExceeds','pf','Destinações do mês','pf-monthly'],
    ['#dgStorageCard .dg-status-warn,#dgActNote','system','Pasta de exportação','backup'],
    ['[data-galton-storage].is-error,[data-galton-integrity]:not([hidden])','research','Laboratório','probability-lab']
  ];
  function collectLocal(next){
    const localErrors=new Set();
    for(const [selector,area,title,go,severity='warning'] of localSources){
      for(const node of document.querySelectorAll(selector)){
        // These are current messages of an open surface, not newly occurring
        // actions. Remounting a status never manufactures a historical event.
        if(!visible(node)) continue;
        const body=node.textContent.trim();
        if(!body || body==='—') continue;
        add(next,'feedback:'+title,area,severity,title+' · mensagem atual',body,go);
        if(severity==='warning')localErrors.add(area);
        break; // Summary takes priority over a second message of the same form.
      }
    }
    const invalid=new Map();
    document.querySelectorAll('[aria-invalid="true"]').forEach(node=>{
      if(!visible(node) || node.closest('#notificationCenter')) return;
      const area=modelArea(node);
      invalid.set(area,(invalid.get(area)||0)+1);
    });
    invalid.forEach((count,area)=>{if(!localErrors.has(area))add(next,'fields:'+area,area,'warning','Campos precisam de revisão',
      count+' campo(s) com erro no formulário aberto. A mensagem detalhada permanece junto do campo.',
      null,String(count));});
    if(typeof ncDirty!=='undefined' && ncDirty)
      add(next,'research:nocoda-draft','research','info','NoCoda com alterações não salvas','Rascunho mantido nesta sessão.','nocoda');
    if(typeof pvDirty!=='undefined' && pvDirty)
      add(next,'research:pivots-draft','research','info','Pivots com alterações não salvas','Conclua ou cancele a edição no próprio estudo.','pivots');
    if(typeof mvpNotesUI==='object' && mvpNotesUI.draftDirty)
      add(next,'notes:draft','notes','info','Nota com alterações não salvas','O conteúdo permanece no editor desta sessão.','notes');
  }
  function refresh(){
    if(rendering) return;
    currentGeneration();
    const next=new Map();
    // Separate adapters: failure never causes an empty healthy area nor stops
    // the other producers. No exception text containing domain data is copied.
    for(const [area,collect] of [['system',collectSystem],['forex',collectForex],['pf',collectPersonalFinance],
      ['alladin',collectAlladin],['research',collectCalendar],['system',collectLocal]]){
      try{ collect(next); }
      catch(_){ add(next,'unavailable:'+collect.name,area,'warning','Avisos desta área indisponíveis',
        'Não foi possível consultar esta fonte. Abra a área para conferir o estado.','area:'+area); }
    }
    for(const key of live.keys()) if(!next.has(key)) seen.delete(key);
    live.clear(); next.forEach((item,key)=>live.set(key,item));
    paint();
  }
  function entries(){ return [...live.values(),...history].sort((a,b)=>
    rank[a.severity]-rank[b.severity] || (a.kind===b.kind?0:a.kind==='live'?-1:1) ||
    (a.when&&b.when?a.when-b.when:0) || (b.at||0)-(a.at||0)); }
  function unread(item){ return seen.get(item.id)!==item.revision; }
  function button(label,attr,id){
    const b=document.createElement('button'); b.type='button'; b.textContent=label; b.dataset[attr]=id; return b;
  }
  function paint(){
    const trigger=el('headerNotificationsBtn'), badge=el('notificationBadge'), list=el('notificationList');
    if(!trigger || !badge || !list) return;
    rendering=true;
    try{
      const all=entries(), count=all.filter(unread).length;
      badge.hidden=!count; badge.textContent=count>99?'99+':String(count);
      trigger.setAttribute('aria-label','Notificações'+(count?' · '+count+' não lida(s)':' · nenhuma não lida'));
      el('notificationSummary').textContent=count?'Você tem '+count+' notificação(ões) não lida(s).':'Todas as notificações foram lidas.';
      if(!el('notificationCenter').open) return;
      const area=el('notificationArea').value, shown=all.filter(item=>area==='all'||item.area===area||item.contextArea===area);
      const view=JSON.stringify(shown.map(item=>[item.id,item.title,item.body,unread(item),item.at]));
      if(view===lastView) return; lastView=view;
      const focus=document.activeElement, focusId=focus?.closest('[data-notification-id]')?.dataset.notificationId;
      const focusAction=focus?.dataset.notificationGo!==undefined?'notificationGo':'notificationRead';
      const fragment=document.createDocumentFragment();
      for(const item of shown){
        const li=document.createElement('li'); li.dataset.notificationId=item.id;
        li.dataset.kind=item.kind;li.dataset.severity=item.severity;li.dataset.unread=String(unread(item));
        const meta=document.createElement('p'); meta.className='notification-meta';
        meta.textContent=names[item.area]+' · '+(item.kind==='event'?'Mensagem desta sessão · '+
          new Date(item.at).toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'})+
          (item.contextArea!=='system'?' · Exibida em '+names[item.contextArea]:''):'Situação atual');
        const title=document.createElement('h3');title.textContent=item.title;
        const body=document.createElement('p');body.className='notification-body';body.textContent=item.body;
        const actions=document.createElement('div');actions.className='notification-actions';
        if(item.go) actions.append(button('Ver detalhes','notificationGo',item.id));
        actions.append(button(unread(item)?'Marcar como lida':'Lida','notificationRead',item.id));
        li.append(meta,title,body,actions);fragment.append(li);
      }
      list.replaceChildren(fragment);
      el('notificationEmpty').hidden=shown.length>0;
      if(focusId){
        const row=[...list.children].find(node=>node.dataset.notificationId===focusId);
        const target=row?.querySelector(focusAction==='notificationGo'?'[data-notification-go]':'[data-notification-read]');
        (target||el('notificationReadAll')).focus({preventScroll:true});
      }
    }finally{ rendering=false; }
  }
  function schedule(){
    if(paused || scheduled) return;
    scheduled=true;
    queueMicrotask(()=>{scheduled=false;refresh();});
  }
  function open(){
    const dialog=el('notificationCenter');
    if(!dialog || dialog.open) return;
    focusOpener=el('headerNotificationsBtn');
    refresh(); dialog.showModal();lastView='';paint();
    el('headerNotificationsBtn').setAttribute('aria-expanded','true');
    el('notificationClose').focus();
  }
  function close(restore=true){const d=el('notificationCenter');if(d?.open){returnFocus=restore;d.close();}}
  function go(item){
    close(false);
    const opener=el('headerNotificationsBtn'), target=item.go;
    if(target?.startsWith('forex-operation@')){
      const [,accountId,periodId]=target.split('@');
      const navigateScoped=()=>{
        const selected=window.JPWForex?.state?.selectOperationalAccount(accountId);
        const period=selected?.ok?window.JPWForex.state.selectOperationalPeriod(accountId,periodId):null;
        if(period?.ok){JPWNavigation.navigate('forex-operation');JPWNavigation.focusCurrentScreen();}
        else {JPWNavigation.navigate('forex-operation');JPWNavigation.navigateLocal('exec','accounts');
          JPWNavigation.focusCurrentScreen();}
      };
      if(window.JPWForex?.executionBoardUI?.hasDrafts())
        window.JPWForex.executionBoardUI.requestLeave(navigateScoped,'Abrir notificação de outra conta');
      else navigateScoped();
      return;
    }
    if(target==='backup'||target==='profile'){ openSettingsModal(target==='profile'?'account':'backup',opener); return; }
    if(target==='notes'){openMvpNotesDrawer(opener);return;}
    if(target==='calendar'){JPWEcal.open(opener);return;}
    if(target==='pf'||target==='pf-monthly'||target==='pf-debts'){
      JPWNavigation.navigate('finpes');
      if(target!=='pf') JPWNavigation.navigateLocal('finpes',target==='pf-monthly'?'mensal':'dividas');
      JPWNavigation.focusCurrentScreen();
      return;
    }
    if(target?.startsWith('area:')){
      const area=target.slice(5);
      if(area==='system')openSettingsModal('general',opener);
      else {JPWNavigation.navigate(area==='pf'?'finpes':area==='notes'?'dash':area);JPWNavigation.focusCurrentScreen();}
      return;
    }
    JPWNavigation.navigate(target);
    JPWNavigation.focusCurrentScreen();
  }
  window.JPWNotifications=Object.freeze({open,close,refresh});
  // Bridges are installed once and keep original behavior even if the optional
  // centre cannot render. They do not replace blocking decisions.
  const nativeAlert=window.alert;
  window.alert=function(...args){
    try{record(args[0],currentArea());}catch(_){}
    return nativeAlert.apply(this,args);
  };
  for(const name of ['render','ffNewsRender','showSessionNotice']){
    const original=window[name];if(typeof original!=='function')continue;
    window[name]=function(...args){
      const result=original.apply(this,args);
      try{if(name==='showSessionNotice')record(args[0],currentArea());schedule();}catch(_){}
      return result;
    };
  }
  el('headerNotificationsBtn')?.addEventListener('click',open);
  el('notificationClose')?.addEventListener('click',()=>close());
  el('notificationCenter')?.addEventListener('close',()=>{
    el('headerNotificationsBtn')?.setAttribute('aria-expanded','false');lastView='';
    if(returnFocus)shellRestoreHeaderFocus(focusOpener);
    returnFocus=true;
  });
  el('notificationCenter')?.addEventListener('keydown',event=>{
    if(event.key!=='Tab')return;
    const controls=[...event.currentTarget.querySelectorAll('button:not(:disabled),select:not(:disabled),[tabindex="0"]')].filter(visible);
    const first=controls[0],last=controls[controls.length-1],active=document.activeElement;
    if(event.shiftKey && (active===first||!controls.includes(active))){event.preventDefault();last?.focus();}
    else if(!event.shiftKey && (active===last||!controls.includes(active))){event.preventDefault();first?.focus();}
  });
  el('notificationCenter')?.addEventListener('click',event=>{
    if(event.target===el('notificationCenter')){
      const r=event.target.getBoundingClientRect();
      if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)close();
    }
    const mark=event.target.closest('[data-notification-read]'), action=event.target.closest('[data-notification-go]');
    const id=mark?.dataset.notificationRead||action?.dataset.notificationGo;
    if(!id)return;
    const item=live.get(id)||history.find(row=>row.id===id);if(!item)return;
    seen.set(item.id,item.revision);
    if(action)go(item);
    paint();
  });
  el('notificationReadAll')?.addEventListener('click',()=>{entries().forEach(item=>seen.set(item.id,item.revision));paint();});
  el('notificationArea')?.addEventListener('change',()=>{lastView='';paint();});
  // Observe only known feedback roots/field validity, never editor contents or
  // the notification list itself. Replacement of a form reconnects by selector.
  const selector=localSources.map(row=>row[0]).join(',')+',#persistenceAlert,#persistenceRecovery,#settingsProfileStatus,#mvpNotesEditorBar';
  const observer=new MutationObserver(records=>{
    if(rendering)return;
    if(records.some(record=>{
      const node=record.target.nodeType===1?record.target:record.target.parentElement;
      if(!node||node.closest('#notificationCenter,#headerNotificationsBtn'))return false;
      if(record.attributeName==='aria-invalid')return true;
      return !!node.closest(selector) || [...record.addedNodes].some(n=>n.nodeType===1 && (n.matches(selector)||n.querySelector(selector)));
    }))schedule();
  });
  observer.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,
    attributeFilter:['aria-invalid','data-state','data-dirty','hidden','class']});
  document.addEventListener('input',schedule);
  document.addEventListener('change',schedule);
  document.addEventListener('click',schedule);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)schedule();});
  window.addEventListener('storage',schedule);
  window.addEventListener('pagehide',()=>{paused=true;history.length=0;live.clear();seen.clear();});
  window.addEventListener('pageshow',()=>{paused=false;schedule();});
  // Existing quote provider, read only subscription. The existing calendar tick
  // reaches us through ffNewsRender called by ffNewsRenderAll; no second economic poll/timer is created.
  if(window.JPWMarket?.usdBrl?.onChange) JPWMarket.usdBrl.onChange(schedule);
  schedule();
})();

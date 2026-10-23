// NOTIFICATION-ACTIONS: readonly projections, not a financial authority or inbox.
// Counts are active causes; consulting an item never acknowledges a financial act.
(function initNotificationCenter(){
  if(window.JPWNotifications)return;
  const el=id=>document.getElementById(id);
  const names={system:'Sistema',forex:'Forex',planning:'Planejamento',pf:'Finanças Pessoais',alladin:'Alladin',research:'Research',notes:'Notas'};
  const rank={critical:0,warning:1,info:2};
  const catalog=Object.freeze({
    persistence:{source:'system',action:'Ver recuperação'},backup:{source:'system',action:'Revisar backup'},
    integrity:{action:'Ver recuperação'},review:{source:'forex',action:'Revisar ordens'},
    exposure:{source:'forex',action:'Revisar exposição'},context:{source:'forex',action:'Revisar contexto'},
    quotes:{source:'forex',action:'Revisar referências'},closure:{source:'planning',action:'Revisar meses'},
    monthly:{source:'pf',action:'Revisar pendências'},credit:{source:'pf',action:'Revisar crédito'},
    unavailable:{action:'Verificar novamente'}
  });
  const live=new Map(),caches=new Map(),lastKnown=new Map(),dirty=new Set();
  // calendar/local remain accepted invalidation ids for classic-script consumers.
  // They no longer collect agenda, native messages or ordinary form feedback.
  const sources={system:collectSystem,forex:collectForex,planning:collectPlanning,
    pf:collectPersonalFinance,alladin:collectAlladin,calendar:()=>{},local:()=>{}};
  let stateRef=S,generation=0,scheduled=false,rendering=false,paused=false,dayTimer=null,dayKey='';
  let focusOpener=null,returnFocus=true,intent=0;
  const epoch=()=>typeof jpWealthPersistenceEpoch==='function'?jpWealthPersistenceEpoch():null;
  const active=module=>window.JPWModuleAvailability?.canAccess(module)!==false;
  const monthLabel=month=>/^\d{4}-\d{2}$/.test(month||'')?new Date(month+'-15T12:00:00').toLocaleDateString('pt-BR',{month:'short',year:'numeric'}):month;
  const localDay=()=>{const d=new Date();return d.getFullYear()+'-'+d.getMonth()+'-'+d.getDate();};
  function currentGeneration(){
    if(stateRef===S)return;
    stateRef=S;generation++;intent++;live.clear();caches.clear();lastKnown.clear();
    Object.keys(sources).forEach(id=>dirty.add(id));
  }
  function add(next,type,id,options){
    const rule=catalog[type];
    next.set(id,{id,type,area:options.area||rule.source||'system',severity:'warning',state:'active',
      title:'',body:'',context:'',details:'',go:null,action:rule.action,...options});
  }
  function collectSystem(next){
    const failure=typeof jpWealthPersistenceFailure==='object'&&jpWealthPersistenceFailure;
    if(jpWealthPersistenceOutcomeIsUnknown())
      add(next,'persistence','system:persistence',{area:'system',severity:'critical',title:'Gravação não confirmada',
        body:'O aplicativo não conseguiu confirmar o salvamento. Confira a recuperação antes de tentar novamente.',
        details:'O resultado é indeterminado. Novas gravações permanecem bloqueadas; consultar este aviso não permite repetir o comando.',go:'backup'});
    else if(typeof jpWealthLoadRecoveryActive==='function'&&jpWealthLoadRecoveryActive())
      add(next,'persistence','system:persistence',{severity:'critical',title:'Sua base precisa de recuperação',
        body:'Os dados não puderam ser carregados com segurança. Abra as opções de recuperação.',go:'backup'});
    else if(failure?.active)
      add(next,'persistence','system:persistence',{severity:'critical',title:failure.kind==='conflict'?'Outra aba atualizou os dados':'Não foi possível salvar',
        body:'Confira o aviso de armazenamento antes de continuar. As alterações pendentes não estão confirmadas.',go:'backup'});
    else if(jpWealthPersistenceIsBlocked())
      add(next,'persistence','system:persistence',{title:'Gravação suspensa',body:'Confira a recuperação para entender o bloqueio atual.',go:'backup'});
    const backup=dgBackupStatus();
    if(backup.due||backup.state==='unknown'){
      const days=dgBackupAgeDays();
      add(next,'backup','system:backup',{severity:backup.tone==='bad'?'critical':'warning',title:backup.state==='unknown'?'Confira a confirmação do backup':'Seu backup precisa de atenção',
        body:backup.state==='unknown'?'A última cópia não está confirmada. Confira seu estado em Backup e Recuperação.':
          days===null?'Ainda não há confirmação de uma cópia de segurança.':days+' dias desde a última confirmação de backup.',
        details:backup.text,go:'backup'});
    }
  }
  const fact=order=>order&&order.recordStatus!=='voided'&&order.status!=='Migrada'&&
    !(order.recordStatus==='draft'&&!order.status)&&!!(order.status||order.lote>0||order.entry>0||order.sl>0);
  function collectForex(next){
    const fx=window.JPWForex;
    if(!fx.state.supported()){
      add(next,'integrity','forex:compatibility',{area:'system',severity:'critical',context:'Forex',
        title:'Os dados do Forex precisam de atenção',body:'Esta versão não consegue consultar o agregado com segurança. Preserve a base antes de editar.',go:'backup'});return;
    }
    if(!active('forex'))return;
    const contexts=S.forex?.accountContexts?.accounts||{};
    for(const [accountId,account] of Object.entries(contexts)){
      if(account.archived===true)continue;
      const registration=(S.accounts||[]).find(a=>a?.forexAccountId===accountId);
      for(const [periodId,period] of Object.entries(account.periods||{})){
        const raw=(period.phases||[]).flatMap(phase=>Array.isArray(phase.orders)?phase.orders:[]).filter(fact);
        const model=fx.readModel({accountId,periodId});
        const orders=model.orders.raw;
        const context=(registration?.nome||accountId)+' · '+period.startedAt+' · '+period.currency;
        const go='forex-operation@'+accountId+'@'+periodId;
        const scope={accountId,periodId,context,go};
        const reviewed=orders.filter(o=>o.needsReview||o.stopPhaseWarning||o.status==='Aberta'&&(!(o.sl>0)||o.stopValidated!==true));
        // The canonical raw reader can omit an unresolved context. Such facts
        // remain visible as a reconciliation task, never a zero-risk assertion.
        const hasOrders=raw.length>0||orders.length>0;
        const hasReserves=!!model.reserves.unmatchedObservation||Object.keys(model.reserves.observations||{}).length>0;
        const unresolved=raw.length>0&&!orders.length||hasOrders&&model.findings.some(f=>[
          'ORDER_CONTEXT_UNRESOLVED','ORDER_STATUS_UNRESOLVED','ORDER_ACCOUNT_UNRESOLVED'].includes(f.code))||
          hasReserves&&model.findings.some(f=>['RESERVE_CONTEXT_UNRESOLVED','FCR_NOMINAL_CONFLICT'].includes(f.code));
        if(unresolved)add(next,'context','forex:context:'+accountId+':'+periodId,{...scope,severity:'critical',
          title:'Registros precisam de conciliação',body:'Confira a identidade e os dados dos fatos deste período. Ausência de leitura não significa risco zero.',
          details:model.findings.filter(f=>['ORDER_CONTEXT_UNRESOLVED','ORDER_STATUS_UNRESOLVED','ORDER_ACCOUNT_UNRESOLVED','RESERVE_CONTEXT_UNRESOLVED','FCR_NOMINAL_CONFLICT'].includes(f.code)).map(f=>f.message).join('\n')});
        if(reviewed.length)add(next,'review','forex:order-review:'+accountId+':'+periodId,{...scope,
          severity:reviewed.some(o=>o.status==='Aberta'&&(!(o.sl>0)||o.stopValidated!==true))?'critical':'warning',
          title:'Ordens precisam de revisão',body:reviewed.length+' ordem(ns) aguardam conferência neste período.',
          details:'Confira as sinalizações de revisão, o stop informado e sua validação na Operação. A central não corrige nem autoriza ordens.'});
        if(model.accountPhase.compulsoryClose)add(next,'exposure','forex:compulsory:'+accountId+':'+periodId,{...scope,severity:'critical',
          title:'Encerramento compulsório sinalizado',body:'O motor identificou o limite de encerramento neste período. Confira o diagnóstico e as posições na Operação.',
          details:model.accountPhase.findings?.map(f=>f.message).join('\n')||''});
        const exceeded=model.findings.find(f=>f.code==='LEVERAGE_EXCEEDED');
        if(exceeded)add(next,'exposure','forex:leverage:'+accountId+':'+periodId,{...scope,severity:'critical',
          title:'Exposição acima do teto da fase',body:'Confira a exposição registrada e o diagnóstico do motor antes de qualquer nova decisão.',details:exceeded.message});
        const used=new Set(orders.filter(o=>o.status==='Aberta'||o.status==='Pendente'&&o.pendingActive===true&&o.amplifiesExposure===true).map(o=>o.par));
        const references=used.size?fx.executionBoard.priceReferences({accountId,periodId,instrumentIds:[...used]}):[];
        const stale=references.map(item=>{
          const p=item.price,observed=p?.kind==='MANUAL'&&p.observedAt?new Date(p.observedAt):null;
          const date=observed&&Number.isFinite(observed.getTime())?dateISO(observed):p?.referenceDate;
          const dated=typeof date==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(date)&&Number.isFinite(Date.parse(date));
          const status=dated&&Number.isFinite(p?.value)&&p.value>0?staleInfo(date):{cls:'danger',label:'Referência ou data indisponível'};
          return {...item,status};
        }).filter(item=>item.status.cls!=='fresh');
        if(stale.length)add(next,'quotes','forex:quotes:'+accountId+':'+periodId,{...scope,
          title:'Confira as referências das ordens',body:stale.length+' instrumento(s) de ordens ativas têm referências que precisam de revisão.',
          details:stale.map(i=>i.name+' · '+i.status.label+' · '+(i.price?.source||'Fonte indisponível')).join('\n')});
      }
    }
    const legacy=(S.phases||[]).flatMap(p=>p.orders||[]).filter(fact);
    const recorded=S.activeOperation?.recordContext;
    if(legacy.length&&!(recorded?.accountId&&recorded?.periodId&&contexts[recorded.accountId]?.periods?.[recorded.periodId]))
      add(next,'context','forex:legacy-context',{severity:'critical',title:'Registros sem contexto confirmado',
        body:'Há fatos anteriores que precisam de conciliação. Confira sua conta, período e situação na Operação.',go:'forex-operation'});
  }
  function collectPlanning(next){
    const pending=window.JPWPlanning?.queries.pendingActions();
    if(!pending)throw new Error('planning-query-unavailable');
    if(!pending.available){add(next,'integrity','planning:compatibility',{area:'system',severity:'critical',context:'Planejamento',title:'Os dados do Planejamento precisam de atenção',body:'Os registros não puderam ser consultados com segurança. Preserve a base e confira a recuperação.',details:pending.issues.join('\n'),go:'backup'});return;}
    if(!active('planning'))return;
    for(const account of pending.accounts){
      add(next,'closure','planning:close:'+account.accountId+':'+account.planId,{
        title:'Meses aguardam fechamento',context:account.name,accountId:account.accountId,planId:account.planId,month:account.firstMonth,
        body:account.count+' mês(es) com registros precisam de conferência. Comece por '+monthLabel(account.firstMonth)+'.',
        details:account.months.map(m=>monthLabel(m.month)).join(' · ')+(account.dependencyMonth?'\n'+monthLabel(account.dependencyMonth)+' precisa ser conferido antes dos meses seguintes.':''),
        go:'planning-month@'+account.accountId+'@'+account.planId+'@'+account.firstMonth});
    }
  }
  function collectPersonalFinance(next){
    const reason=pfWriteBlockReason();
    if(reason){add(next,'integrity','pf:compatibility',{area:'system',severity:'critical',context:'Finanças Pessoais',
      title:'Os dados de Finanças Pessoais precisam de atenção',body:'A unidade armazenada não é suportada. Preserve a base e consulte a recuperação.',details:reason,go:'backup'});return;}
    if(!active('personal-finance'))return;
    const pending=pfPendingBefore(pfCurrentMonthKey());
    if(pending.length)add(next,'monthly','pf:pending',{title:'Há meses com pendências',
      body:pending.length+' mês(es) anteriores precisam de conferência no orçamento.',
      details:pending.map(p=>monthLabel(p.key)+': '+p.despesas+' despesa(s) e '+p.notas+' nota(s) pendente(s).').join('\n'),go:'pf-monthly'});
    const excess=(S.personalFinance?.creditLines||[]).filter(Boolean).filter(line=>pfCreditLineDerived(line).estouro);
    if(excess.length)add(next,'credit','pf:credit',{title:'Crédito acima do limite informado',
      body:excess.length+' linha(s) foram sinalizadas pelo módulo. Confira os limites cadastrados.',
      details:'O sinal não classifica inadimplência.',go:'pf-debts'});
  }
  function collectAlladin(next){
    const compat=JPWAlladin.compat();
    if(compat.readOnly){add(next,'integrity','alladin:compatibility',{area:'system',severity:'critical',context:'Alladin',
      title:'Os dados do Alladin precisam de atenção',body:'A versão armazenada é posterior à suportada. Preserve a base antes de editar.',go:'backup'});return;}
    const ledger=JPWAlladin.leitura.ledger();
    let issue=!ledger.available||ledger.quality==='BLOCKING'?{source:'ledger',issues:ledger.issues}:null;
    if(!issue){const positions=JPWAlladin.leitura.posicoes();if(!positions.available)issue={source:'positions',issues:positions.issues};}
    if(!issue)for(const account of JPWAlladin.leitura.cashAccounts()){
      const balance=JPWAlladin.leitura.saldoDeCaixa(account.cashAccountId);
      if(!balance.available){issue={source:'balance',id:account.cashAccountId,issues:balance.issues};break;}
    }
    if(issue)add(next,'integrity','alladin:quality',{area:'system',severity:'critical',context:'Alladin',
      title:'Integridade do Alladin precisa de atenção',body:'Uma leitura de lançamentos, posições ou saldos foi recusada. Preserve os dados para recuperação.',
      details:'Ausência de leitura não significa saldo zero.\n'+JSON.stringify(issue),go:'backup'});
  }
  function refreshSources(){
    if(rendering||paused)return;
    currentGeneration();if(!dirty.size)return;
    const pending=[...dirty];dirty.clear();
    for(const id of pending){
      let next=new Map();
      try{sources[id](next);lastKnown.set(id,next);}
      catch(_){
        const previous=lastKnown.get(id);
        add(next,'unavailable','unavailable:'+id,{area:id==='pf'?'pf':names[id]?id:'system',state:'unverified',
          title:'Não foi possível verificar '+(names[id]||'esta fonte'),body:'A consulta está indisponível. Verifique novamente antes de considerar as pendências resolvidas.',
          details:previous?.size?'Última consulta disponível — informação não atual:\n'+[...previous.values()].map(item=>item.title+(item.context?' · '+item.context:'')+'\n'+item.body+(item.details?'\n'+item.details:'')).join('\n\n'):'Não há diagnóstico anterior confirmado nesta sessão.',
          go:'refresh:'+id});
      }
      caches.set(id,next);
    }
    live.clear();for(const cache of caches.values())for(const [key,item] of cache)live.set(key,item);
    paint();
  }
  function refresh(){Object.keys(sources).forEach(id=>dirty.add(id));refreshSources();}
  function invalidate(...ids){currentGeneration();for(const id of ids)if(sources[id])dirty.add(id);schedule();}
  function schedule(){if(paused||scheduled)return;scheduled=true;queueMicrotask(()=>{scheduled=false;refreshSources();});}
  function entries(){return [...live.values()].sort((a,b)=>rank[a.severity]-rank[b.severity]||
    a.area.localeCompare(b.area)||a.context.localeCompare(b.context)||a.id.localeCompare(b.id));}
  function button(label,id){const b=document.createElement('button');b.type='button';b.textContent=label;b.dataset.notificationGo=id;return b;}
  function paint(){
    const trigger=el('headerNotificationsBtn'),badge=el('notificationBadge'),list=el('notificationList');
    if(!trigger||!badge||!list)return;
    rendering=true;
    try{
      const all=entries(),count=all.length;
      badge.hidden=!count;badge.textContent=count>99?'99+':String(count);
      trigger.setAttribute('aria-label','Notificações · '+(count?count+' ação(ões) pendente(s)':'nenhuma ação pendente identificada'));
      el('notificationSummary').textContent=count===1?'1 ação pendente':count?count+' ações pendentes':'Nenhuma ação pendente identificada';
      if(!el('notificationCenter').open)return;
      const area=el('notificationArea').value,shown=all.filter(item=>area==='all'||item.area===area);
      const focus=document.activeElement,focusedId=focus?.closest('[data-notification-id]')?.dataset.notificationId;
      const focusSummary=focus?.tagName==='SUMMARY';
      const scroll=list.closest('.notification-scroll'),scrollTop=scroll.scrollTop;
      const nodes=new Map([...list.querySelectorAll('[data-notification-id]')].map(n=>[n.dataset.notificationId,n]));
      const anchor=[...nodes.values()].find(n=>n.getBoundingClientRect().bottom>scroll.getBoundingClientRect().top);
      const anchorTop=anchor?.getBoundingClientRect().top,anchorId=anchor?.dataset.notificationId;
      const fragment=document.createDocumentFragment();let group=null;
      for(const item of shown){
        const heading=item.severity==='critical'?'Prioritárias':'Pendências';
        if(heading!==group){group=heading;const li=document.createElement('li');li.className='notification-group';li.setAttribute('role','presentation');const p=document.createElement('p');p.setAttribute('role','heading');p.setAttribute('aria-level','3');p.textContent=heading;li.append(p);fragment.append(li);}
        const li=nodes.get(item.id)||document.createElement('li');
        const signature=JSON.stringify(item);
        if(li.__notificationView!==signature){
          const expanded=li.querySelector('details')?.open===true;
          li.__notificationView=signature;li.dataset.notificationId=item.id;li.dataset.kind='live';li.dataset.area=item.area;li.dataset.severity=item.severity;li.dataset.state=item.state;
          const meta=document.createElement('p');meta.className='notification-meta';meta.textContent=names[item.area]+(item.context?' · '+item.context:'');
          const title=document.createElement('h3');title.textContent=(item.severity==='critical'?'! ':'')+item.title;
          const body=document.createElement('p');body.className='notification-body';body.textContent=item.body;
          const actions=document.createElement('div');actions.className='notification-actions';if(item.go)actions.append(button(item.action,item.id));
          li.replaceChildren(meta,title,body,actions);
          if(item.details){const details=document.createElement('details');details.open=expanded;const summary=document.createElement('summary');summary.textContent='Entender este aviso';const p=document.createElement('p');p.textContent=item.details;details.append(summary,p);li.append(details);}
        }
        fragment.append(li);
      }
      list.replaceChildren(fragment);
      el('notificationEmpty').textContent=area==='all'?'Nenhuma ação pendente identificada':'Nenhuma ação pendente identificada nesta área';
      el('notificationEmpty').hidden=shown.length>0;
      if(focusedId){const row=[...list.querySelectorAll('[data-notification-id]')].find(n=>n.dataset.notificationId===focusedId);const target=row?.querySelector(focusSummary?'summary':'[data-notification-go]');(target||el('notificationClose')).focus({preventScroll:true});}
      const newAnchor=[...list.querySelectorAll('[data-notification-id]')].find(n=>n.dataset.notificationId===anchorId);
      scroll.scrollTop=newAnchor&&anchorTop!==undefined?scrollTop+newAnchor.getBoundingClientRect().top-anchorTop:scrollTop;
    }finally{rendering=false;}
  }
  function open(){
    const d=el('notificationCenter');if(!d||d.open||document.querySelector('dialog[open]'))return false;
    focusOpener=el('headerNotificationsBtn');refresh();clock();d.showModal();paint();
    el('headerNotificationsBtn').setAttribute('aria-expanded','true');el('notificationClose').focus();return true;
  }
  function close(restore=true){const d=el('notificationCenter');if(d?.open){returnFocus=restore;d.close();}}
  function notice(){if(typeof showSessionNotice==='function')showSessionNotice('A pendência mudou. Consulte novamente as notificações antes de continuar.');}
  function scopedForex(item,valid){
    const apply=()=>{
      if(!valid())return notice();
      const nav=JPWNavigation,plan=nav.resolve('forex-operation');
      // Resolve each existing guard before navigation can change the screen.
      // Its callback captures the same intent and must pass valid() again.
      if(nav.current().primary==='planning'&&window.JPWPlanning?.ui?.guardNavigation&&
        JPWPlanning.ui.guardNavigation(plan,apply)===false)return;
      if(window.JPWForex?.accountsUI?.guardNavigation&&JPWForex.accountsUI.guardNavigation(plan,apply)===false)return;
      if(!valid())return notice();
      let unsubscribe=()=>{},settled=false;
      const finish=()=>{
        if(settled)return;settled=true;unsubscribe();
        if(!valid())return notice();
        const selected=JPWForex.state.selectOperationalAccount(item.accountId);
        const period=selected?.ok?JPWForex.state.selectOperationalPeriod(item.accountId,item.periodId):null;
        if(period?.ok){render();nav.focusCurrentScreen();}else notice();
      };
      unsubscribe=nav.subscribe(({current})=>{if(current.screen===plan.screen)finish();});
      if(nav.navigate('forex-operation'))finish();
      else for(const d of document.querySelectorAll('dialog[open]'))d.addEventListener('close',()=>queueMicrotask(()=>{if(!settled){settled=true;unsubscribe();}}),{once:true});
    };
    if(window.JPWForex?.executionBoardUI?.hasDrafts())JPWForex.executionBoardUI.requestLeave(apply,'Revisar alterações antes de abrir a notificação');
    else apply();
  }
  function go(item){
    currentGeneration();const gen=generation,expectedRoot=S,expectedEpoch=epoch(),operation=++intent;
    const valid=()=>{
      currentGeneration();if(gen!==generation||S!==expectedRoot||epoch()!==expectedEpoch||operation!==intent)return false;
      refresh();const current=live.get(item.id);
      return !!current&&current.state==='active'&&current.go===item.go;
    };
    if(item.go.startsWith('refresh:')){invalidate(item.go.slice(8));return;}
    if(!valid()){notice();return;}
    close(false);
    if(item.go.startsWith('planning-month@')){
      const openContext=window.JPWPlanning?.ui?.openMonthlyContext;
      if(typeof openContext!=='function'){notice();return;}
      Promise.resolve(openContext({accountId:item.accountId,planId:item.planId,month:item.month})).catch(notice);return;
    }
    if(item.go.startsWith('forex-operation@')){scopedForex(item,valid);return;}
    if(item.go==='backup'){openSettingsModal('backup',el('headerNotificationsBtn'));return;}
    if(item.go==='pf-monthly'||item.go==='pf-debts'){
      if(JPWNavigation.navigateLocal('finpes',item.go==='pf-monthly'?'mensal':'dividas'))JPWNavigation.focusCurrentScreen();return;
    }
    if(JPWNavigation.navigate(item.go))JPWNavigation.focusCurrentScreen();
  }
  function stopClock(){if(dayTimer!==null){clearTimeout(dayTimer);dayTimer=null;}}
  function clock(){
    stopClock();if(paused||document.hidden)return;
    const today=localDay();if(today!==dayKey){dayKey=today;invalidate('system','forex','planning','pf');}
    const now=new Date(),next=new Date(now.getFullYear(),now.getMonth(),now.getDate()+1);
    dayTimer=setTimeout(clock,Math.max(1,next.getTime()-now.getTime()));
  }
  function disposeForSession(){
    intent++;generation++;stopClock();live.clear();caches.clear();lastKnown.clear();dirty.clear();close(false);paint();
  }
  window.JPWNotifications=Object.freeze({open,close,refresh,invalidate,disposeForSession});
  // No native alert/showSessionNotice interception: ordinary feedback stays local.
  const originalRender=window.render;
  if(typeof originalRender==='function')window.render=function(...args){const result=originalRender.apply(this,args);try{invalidate('forex','system');}catch(_){}return result;};
  el('headerNotificationsBtn')?.addEventListener('click',open);
  el('notificationClose')?.addEventListener('click',()=>close());
  el('notificationCenter')?.addEventListener('close',()=>{el('headerNotificationsBtn')?.setAttribute('aria-expanded','false');if(returnFocus)shellRestoreHeaderFocus(focusOpener);returnFocus=true;});
  el('notificationCenter')?.addEventListener('keydown',event=>{
    if(event.key!=='Tab')return;
    const controls=[...event.currentTarget.querySelectorAll('button:not(:disabled),select:not(:disabled),summary,[tabindex="0"]')].filter(n=>n.getClientRects().length);
    const first=controls[0],last=controls.at(-1),focused=document.activeElement;
    if(event.shiftKey&&(focused===first||!controls.includes(focused))){event.preventDefault();last?.focus();}
    else if(!event.shiftKey&&(focused===last||!controls.includes(focused))){event.preventDefault();first?.focus();}
  });
  el('notificationCenter')?.addEventListener('click',event=>{
    if(event.target===el('notificationCenter')){const r=event.target.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)close();}
    const action=event.target.closest('[data-notification-go]');if(!action)return;
    const item=live.get(action.dataset.notificationGo);if(item)go(item);
  });
  el('notificationArea')?.addEventListener('change',paint);
  const observer=new MutationObserver(()=>invalidate('system'));
  for(const id of ['persistenceAlert','persistenceRecovery','dgBackupBanner']){
    const root=el(id);if(root)observer.observe(root,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['hidden','class']});
  }
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopClock();else{refresh();clock();}});
  window.addEventListener('storage',refresh);
  window.addEventListener('jpw-backup-status',()=>invalidate('system'));
  window.JPWNavigation?.subscribe(()=>{invalidate('local');if(dayTimer===null)clock();});
  window.addEventListener('pagehide',()=>{paused=true;intent++;stopClock();live.clear();caches.clear();lastKnown.clear();dirty.clear();close(false);});
  window.addEventListener('pageshow',()=>{paused=false;refresh();clock();});
  window.JPWMarket?.usdBrl?.onChange?.(()=>invalidate('forex','system'));
  invalidate(...Object.keys(sources));clock();
})();

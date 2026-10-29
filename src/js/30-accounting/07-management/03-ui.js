/* Annual accounting: a workbook-shaped view over canonical account facts.
 * Typing, selection and rendering never call a financial writer. */
(function(root){
  'use strict';
  const el=id=>document.getElementById(id);
  const h=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const clone=value=>structuredClone(value);
  const api=()=>root.JPWManagementAnnual;
  const date=()=>root.JPWAnnualEngine.dateKey(new Date());
  const fmtDate=value=>value?new Intl.DateTimeFormat('pt-BR',{timeZone:'UTC',day:'2-digit',month:'2-digit',year:'numeric'}).format(new Date(value+'T12:00:00Z')):'—';
  const num=value=>finite(value)?value.toLocaleString('pt-BR',{maximumFractionDigits:4}):'—';
  const pct=value=>finite(value)?(value*100).toLocaleString('pt-BR',{maximumFractionDigits:4})+'%':'—';
  function money(value,currency=contextRead()?.currency||'USD'){
    if(!finite(value))return '—';
    try{return new Intl.NumberFormat('pt-BR',{style:'currency',currency}).format(value);}
    catch(_){return num(value)+' '+currency;}
  }
  const svgClose='<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m6 6 12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
  const button=(action,label,attrs='',primary=false)=>'<button type="button" data-mg-action="'+action+'" '+attrs+' class="mg-button '+(primary?'mg-primary':'')+'">'+label+'</button>';
  let selection={accountId:'',periodId:'',year:new Date().getFullYear()},surface='accounting',active=false,initialized=false;
  let editor=null,dialog=null,dialogTrigger=null,dialogKind='',guardCallback=null,lastModel=null,notice='',dayTimer=null,resizeObserver=null;
  const drafts=new Map(),reserveDrafts=new Map();
  let reserveMountedKey='';
  const target=()=>({accountId:selection.accountId||null,periodId:selection.periodId||null,year:Number(selection.year)});
  const key=()=>[selection.accountId,selection.periodId,selection.year].join(':');
  const contextRead=()=>api()?.queries.context(target())?.value||null;
  const accountRows=()=>typeof S!=='undefined'&&Array.isArray(S.accounts)?S.accounts:[];
  const accounts=()=>accountRows().filter(a=>a.forexAccountId&&a.archived!==true);
  function periods(){
    const values=typeof S!=='undefined'?S.forex?.accountContexts?.accounts?.[selection.accountId]?.periods:null;
    return Object.values(values||{}).sort((a,b)=>String(a.startedAt).localeCompare(String(b.startedAt)));
  }
  function accountName(){return accountRows().find(a=>a.forexAccountId===selection.accountId)?.nome||'Conta não selecionada';}
  const host=()=>surface==='reserves'?el('fxreserves'):el('management');
  const reserveKey=scope=>JSON.stringify([String(scope?.accountId||''),String(scope?.periodId||'')]);
  const reserveFormScope=form=>({accountId:form?.dataset.fxScopeAccount||'',periodId:form?.dataset.fxScopePeriod||''});
  const reserveDirty=()=>surface==='reserves'&&el('fxReserveFacts')?.dataset.fxTouched==='true';
  function syncConfirmedReserveDraft(){
    const form=el('fxReserveFacts');
    if(reserveMountedKey&&form?.dataset.fxTouched!=='true'&&reserveKey(reserveFormScope(form))===reserveMountedKey){
      reserveDrafts.delete(reserveMountedKey);reserveMountedKey='';
    }
  }
  function rememberReserveDraft(){
    syncConfirmedReserveDraft();const form=el('fxReserveFacts');if(form?.dataset.fxTouched!=='true')return;
    const scope=reserveFormScope(form),id=reserveKey(scope),review={};
    for(const name of ['fxScopeAccount','fxScopePeriod','fxEpoch','fxPeriodRevision','fxFactsFingerprint'])if(form.dataset[name]!==undefined)review[name]=form.dataset[name];
    reserveDrafts.set(id,{key:id,scope,values:fields(form),review,open:form.closest('details')?.open===true});
  }
  function clearReserveForm(){
    const form=el('fxReserveFacts');reserveMountedKey='';if(!form)return;form.reset();
    for(const name of ['fxTouched','fxScopeAccount','fxScopePeriod','fxEpoch','fxPeriodRevision','fxFactsFingerprint'])delete form.dataset[name];
    const response=form.querySelector('.fx-engine-response');if(response)response.textContent='';
    if(el('fxReserveReviewStale'))el('fxReserveReviewStale').hidden=true;
  }
  function restoreReserveDraft(){
    const form=el('fxReserveFacts');if(!form)return;syncConfirmedReserveDraft();
    const id=reserveKey(selection),mounted=reserveKey(reserveFormScope(form));
    if(mounted!==id){rememberReserveDraft();clearReserveForm();}
    if(form.dataset.fxTouched==='true')return;
    const draft=reserveDrafts.get(id);if(!draft)return;
    fillFields(form,draft.values);Object.assign(form.dataset,draft.review);form.dataset.fxTouched='true';reserveMountedKey=id;
    if(draft.open)form.closest('details').open=true;
  }
  const hasPendingWork=()=>{syncConfirmedReserveDraft();return !!editor?.dirty||reserveDirty()||reserveDrafts.size>0||[...drafts.values()].some(d=>d.dirty);};
  function live(){return active&&!document.hidden&&host()?.classList.contains('active');}
  function canEdit(){return root.JPWModuleAvailability?.canAccess('management')!==false;}
  function contextHTML(){
    const a=accounts(),p=periods();
    const accountOptions='<option value="">Selecione uma conta</option>'+a.map(x=>'<option value="'+h(x.forexAccountId)+'" '+(x.forexAccountId===selection.accountId?'selected':'')+'>'+h(x.nome||'Conta cadastrada')+'</option>').join('');
    const periodOptions='<option value="">Selecione um período</option>'+p.map(x=>'<option value="'+h(x.periodId)+'" '+(x.periodId===selection.periodId?'selected':'')+'>'+h(fmtDate(x.startedAt)+' · '+x.currency)+'</option>').join('');
    return '<div class="mg-context" data-mg-context><label>Conta<select data-mg-account>'+accountOptions+'</select></label><label>Período<select data-mg-period '+(!selection.accountId?'disabled':'')+'>'+periodOptions+'</select></label>'+
      (surface==='accounting'?'<label>Ano<input type="number" data-mg-year min="1900" max="9999" step="1" value="'+h(selection.year)+'"></label>':'')+
      '<div class="mg-context-actions">'+button('account-new','Cadastrar conta')+(selection.accountId?button('account-setup','Preparar conta e período'):'')+'</div></div>';
  }
  function installContext(){
    const node=host();if(!node)return;
    let bar=node.querySelector(':scope > [data-mg-context-host]');
    if(!bar){bar=document.createElement('div');bar.dataset.mgContextHost='';bar.className='mg-app';if(surface==='accounting')node.querySelector('.mg-title')?.after(bar);else node.prepend(bar);}
    const markup=contextHTML();
    if(bar.__mgMarkup!==markup){bar.innerHTML=markup;bar.__mgMarkup=markup;}
    if(!bar.__mgBound){bar.__mgBound=true;bar.addEventListener('change',event=>{event.stopPropagation();onChange(event);});bar.addEventListener('click',event=>{event.stopPropagation();onClick(event);});}
  }
  function metric(label,value,note=''){return '<div class="mg-metric"><span>'+h(label)+'</span><strong>'+h(value)+'</strong>'+(note?'<small>'+h(note)+'</small>':'')+'</div>';}
  function summaryHTML(model,result){
    const s=model.summary,c=model.config,t=s.thermometer||{},missing=s.pendingDays||0;
    const pace=t.ok?(t.direction==='AHEAD'?'Adiantado':t.direction==='BEHIND'?'Atrasado':'No ritmo')+' · '+num(Math.abs(t.days))+' dias':t.reason||'Equivalência indisponível';
    const closure=result.closureStatus?.status||result.closureStatus||'OPEN';
    return '<div class="mg-summary">'+
      '<section class="mg-group"><h3>Período e posição</h3><div class="mg-metrics">'+metric('Referência',fmtDate(model.referenceDate||s.referenceDate),s.status==='NOT_STARTED'?'Ainda não iniciado':'Início '+fmtDate(c.startDate))+metric('Saldo inicial',money(c.initialBalance),'Abertura conferida')+metric('Saldo confirmado',money(s.currentBalance),s.balanceDate?'Último fechamento: '+fmtDate(s.balanceDate):'Sem fechamento diário')+metric('Resultado acumulado',money(s.accumulatedResult),missing?'Informação parcial · '+missing+' dias pendentes':'Registros conferidos')+'</div></section>'+
      '<section class="mg-group mg-planned-group"><h3>Objetivo e programação</h3><div class="mg-metrics">'+metric('Meta anual',pct(c.annualTarget),'Valor integral '+money(s.annualTargetAmount))+metric('Meta neste ano',pct(s.partialTarget),num(s.fraction*100)+'% do calendário disponível')+metric('Saldo desejado',money(s.desiredBalance),'Meta proporcional composta')+metric('Data final projetada',s.targetDate?fmtDate(s.targetDate):'Não alcançada','Busca aproximada nos retornos acumulados projetados')+metric('Meta diária',pct(s.dailyTarget),'Meta mensal '+pct(s.monthlyTarget))+metric('Dias programados',num(s.partialProgrammedDays),'Base integral '+num(s.programmedDays))+metric('Datas disponíveis',num(s.eligibleDays),'Segunda a sexta, menos exclusões')+'</div></section>'+
      '<section class="mg-group mg-actual-group"><h3>Realizado e acompanhamento</h3><div class="mg-metrics">'+metric('Dias decorridos',num(s.elapsedDays),'Dias úteis desde o início')+metric('Dias com fechamento',num(s.recordedDays),'Declarações sem resultado: '+num(s.declaredDays))+metric('Acumulado realizado',pct(s.realCumulative),'Saldo confirmado ÷ abertura − 1')+metric('Taxa diária realizada',pct(s.realDailyRate),s.completeActual?'Base completa':'Aguardando pendências')+metric('Extrapolação mensal',pct(s.projectedMonth),'Base de '+num(c.daysPerWeek*4)+' dias')+metric('Extrapolação anual',pct(s.projectedYear),'Base fixa de 240 dias')+'</div><div class="mg-thermometer '+(t.ok?'mg-'+h(t.color):'')+'"><span>Calendário equivalente</span><strong>'+h(pace)+'</strong>'+(t.ok?'<small>'+h(fmtDate(t.equivalentDate))+'</small>':'')+'</div></section></div>'+
      '<details class="mg-reference"><summary>Referências de dias da planilha</summary><div class="mg-metrics">'+metric('Anos',num(s.reference?.years))+metric('Dias brutos',num(s.reference?.days))+metric('Meses de 30 dias',num(s.reference?.daysPerMonth30))+metric('Dias por mês',num(s.reference?.calendarMonthDays))+metric('Semanas',num(s.reference?.weeks))+metric('Dias por semana civil',num(s.reference?.daysPerWeek))+'</div><p>Referências descritivas; a programação financeira usa os dias e meses confirmados acima.</p></details><div class="mg-plan-actions">'+button('other-date','Registrar outra data')+button('edit-plan','Revisar programação')+button('annual-review','Revisar fechamento anual','',true)+'<span class="mg-year-status" data-mg-closure>'+h(closure==='CONFIRMED'?'✓ Ano fechado':closure==='RECONFIRM_REQUIRED'?'Reconferência necessária':'Ano aberto')+'</span></div>'+
      (missing?'<p class="mg-pending">'+h(missing+' dias aguardam resultado ou declaração explícita. O primeiro é '+fmtDate(s.pendingDates?.[0])+'.')+' '+button('first-pending','Ir ao primeiro pendente')+'</p>':'')+
      (s.mismatches?'<p class="mg-pending">Há saldos observados diferentes da cadeia calculada. As observações foram preservadas; confira os detalhes antes do fechamento anual.</p>':'');
  }
  function actualStatus(row){return ({PENDING:'Pendente',RECORDED:'✓ Fechado',NO_RESULT:'Sem resultado declarado',FUTURE:'Projetado',UNAVAILABLE:'Não calculável'})[row.actual?.status]||'Pendente';}
  function dailyRow(row){
    const p=row.planned||{},a=row.actual||{},isToday=row.date===date(),future=row.date>date();
    return '<tr data-mg-date="'+h(row.date)+'" class="mg-day '+(isToday?'mg-today':'')+'">'+
      '<td data-mg-wide>'+h(row.index??'—')+'</td><td data-mg-wide>'+h(root.JPWAnnualEngine.dayDifference?.(row.date,lastModel?.model?.config?.startDate)??'—')+'</td>'+
      '<th scope="row"><button type="button" data-mg-detail="'+h(row.date)+'" aria-expanded="false" aria-controls="mg-details-'+h(row.date)+'">'+h(fmtDate(row.date))+'</button><small>'+h(actualStatus(row))+(row.eligible===false?' · Fora da programação':'')+'</small></th>'+
      '<td class="mg-plan-cell" data-mg-wide>'+h(money(p.opening))+'</td><td class="mg-plan-cell" data-mg-wide>'+h(money(p.result))+'</td><td class="mg-plan-cell"><strong>'+h(money(p.closing))+'</strong></td><td class="mg-plan-cell" data-mg-wide>'+h(pct(p.cumulative))+'</td>'+
      '<td class="mg-real-cell" data-mg-wide>'+h(money(a.opening))+'</td><td class="mg-real-cell" data-mg-wide>'+button(a.status==='NO_RESULT'?'revoke-no-result':'edit-day',h(a.status==='NO_RESULT'?'Revogar declaração':finite(a.result)?money(a.result):future?'—':'Preencher'),'data-mg-date="'+h(row.date)+'" '+(future?'disabled':''))+'</td><td class="mg-real-cell"><strong>'+h(money(a.closing))+'</strong></td><td class="mg-real-cell" data-mg-wide>'+h(pct(a.cumulative))+'</td></tr>'+
      '<tr class="mg-day-details" id="mg-details-'+h(row.date)+'" hidden><td colspan="11"><div class="mg-row-detail"><div>'+metric('Abertura projetada',money(p.opening))+metric('Resultado projetado',money(p.result))+metric('Acumulado projetado',pct(p.cumulative))+'</div><div>'+metric('Abertura real',money(a.opening))+metric('Resultado real',money(a.result))+metric('Acumulado real',pct(a.cumulative))+'</div><p>'+h(a.record?.balanceInput==='OBSERVED'?'Saldo observado preservado.':'O fechamento calculado usa a abertura e o resultado confirmado. Digitar não grava.')+'</p><div class="mg-actions">'+(!future&&a.status!=='NO_RESULT'?button('edit-day',a.record?'Corrigir resultado':'Registrar resultado','data-mg-date="'+h(row.date)+'"','true'):'')+(!future&&!a.record&&a.status!=='NO_RESULT'?button('no-result','Declarar dia sem resultado','data-mg-date="'+h(row.date)+'"'):'')+(a.status==='NO_RESULT'?button('revoke-no-result','Revogar declaração','data-mg-date="'+h(row.date)+'"'):'')+(a.record?button('void-day','Anular fechamento','data-mg-date="'+h(row.date)+'"'):'')+'</div></div></td></tr>';
  }
  function tableHTML(model){
    const rows=model.rows||[];let html='',week=null,planSum=0,actualSum=0,actualCount=0;
    function subtotal(){return '<tr class="mg-subtotal"><th colspan="3">Subtotal da semana</th><td data-mg-wide></td><td class="mg-plan-cell" data-mg-wide>'+h(money(planSum))+'</td><td data-mg-wide></td><td data-mg-wide></td><td data-mg-wide></td><td class="mg-real-cell" data-mg-wide>'+h(actualCount?money(actualSum):'—')+'</td><td data-mg-wide></td><td data-mg-wide></td><td class="mg-compact-subtotal mg-plan-cell" hidden>'+h(money(planSum))+'</td><td class="mg-compact-subtotal mg-real-cell" hidden>'+h(actualCount?money(actualSum):'—')+'</td></tr>';}
    for(const row of rows){
      if(row.weekKey!==week&&week!==null){html+=subtotal();planSum=0;actualSum=0;actualCount=0;}
      week=row.weekKey;planSum+=row.planned?.result||0;if(finite(row.actual?.result)){actualSum+=row.actual.result;actualCount++;}html+=dailyRow(row);
    }
    if(rows.length)html+=subtotal();
    return '<div class="mg-table-wrap"><table class="mg-sheet"><caption class="sr-only">Planejamento anual e fechamentos diários de '+h(accountName())+'</caption><thead><tr class="mg-band"><th colspan="3">Dias</th><th class="mg-plan-cell" colspan="4">Projetado</th><th class="mg-real-cell" colspan="4">Realizado</th></tr><tr><th data-mg-wide>Dia</th><th data-mg-wide>Corridos</th><th>Data</th><th class="mg-plan-cell" data-mg-wide>Inicial</th><th class="mg-plan-cell" data-mg-wide>Resultado</th><th class="mg-plan-cell">Fechamento</th><th class="mg-plan-cell" data-mg-wide>Acumulado</th><th class="mg-real-cell" data-mg-wide>Inicial</th><th class="mg-real-cell" data-mg-wide>Resultado</th><th class="mg-real-cell">Fechamento</th><th class="mg-real-cell" data-mg-wide>Acumulado</th></tr></thead><tbody>'+html+'</tbody></table></div>';
  }
  function closeDialog(returnFocus=true){
    const old=dialog;dialog=null;dialogKind='';if(old){old.close();old.remove();}
    if(returnFocus&&dialogTrigger?.isConnected)dialogTrigger.focus({preventScroll:true});dialogTrigger=null;
  }
  function openDialog(title,content,kind='info'){
    if(document.querySelector('dialog[open]'))return false;
    dialogTrigger=document.activeElement;dialogKind=kind;dialog=document.createElement('dialog');dialog.className='mg-dialog mg-app';dialog.dataset.moduleWorkOwner='management';
    dialog.setAttribute('aria-labelledby','mg-dialog-title');dialog.innerHTML='<header><div><small>Gerenciamento</small><h2 id="mg-dialog-title">'+h(title)+'</h2></div><button type="button" class="mg-close" data-mg-action="close-dialog" aria-label="Fechar">'+svgClose+'</button></header><div class="mg-dialog-body">'+content+'</div>';
    dialog.addEventListener('click',onClick);dialog.addEventListener('cancel',event=>{event.preventDefault();closeDialog();});document.body.append(dialog);dialog.showModal();return true;
  }
  function info(){openDialog('Como funciona o Caixa Anual','<p>O projetado reproduz a primeira aba da planilha de referência. O realizado vem somente dos fechamentos confirmados desta conta e período.</p><p>A meta parcial usa proporcionalidade composta. Dias programados e datas disponíveis são medidas diferentes; não há promessa de resultado.</p><p>As extrapolações reais usam dias por semana × 4 no mês e 240 dias no ano. Não são previsões de mercado.</p><p>O termômetro compara o saldo com as aberturas projetadas. Dias positivos indicam avanço; negativos indicam atraso. As cores seguem a planilha: abaixo de 14 verde, de 14 a 29 amarelo e acima de 29 vermelho. Não representam risco ou autorização.</p><p>Zero informado e ausência são distintos. Fechar este ano não encerra operações nem o período do Forex.</p>');}
  function render(force=false){
    if(!initialized||!host())return;
    installContext();
    if(surface==='reserves'){restoreReserveDraft();root.JPWForex?.ui?.render?.();return;}
    if(editor&&!force){refreshReviewState();return;}
    const body=el('managementContent');if(!body)return;
    lastModel=api()?.queries.model(target())||{ok:false,status:'UNAVAILABLE',errors:['Motor anual indisponível.']};
    let content='';
    if(!selection.accountId||!selection.periodId){content='<section class="mg-empty"><h3>Seu planejamento começa por uma conta</h3><p>'+h(accounts().length?'Selecione a conta e o período acima. Nenhum resultado será preenchido automaticamente.':'Nenhuma conta cadastrada. Cadastre sua conta para preparar o período e começar.')+'</p></section>';}
    else if(!lastModel.ok||!lastModel.model){content='<section class="mg-empty"><h3>'+h(lastModel.status==='NO_PLAN'?'Planeje este ano':'Confira o contexto')+'</h3><p>'+h((lastModel.errors||[]).join(' ')||'Configure a meta e a programação para comparar o projetado com os fechamentos confirmados.')+'</p>'+button('new-plan','Configurar planejamento anual','',true)+'</section>';}
    else content=summaryHTML(lastModel.model,lastModel)+tableHTML(lastModel.model);
    body.innerHTML='<div class="mg-notice" role="status" aria-live="polite" '+(!notice?'hidden':'')+'>'+h(notice)+'</div>'+content;
    if(drafts.has(key()))body.insertAdjacentHTML('afterbegin','<p class="mg-pending">Há um rascunho preservado neste contexto. '+button('resume','Retomar rascunho')+'</p>');
    resize();
  }
  function setNotice(message){notice=String(message||'');const n=el('managementContent')?.querySelector('.mg-notice');if(n){n.textContent=notice;n.hidden=!notice;}}
  function resize(){
    const node=el('managementContent');if(!node)return;const compact=node.getBoundingClientRect().width<900;node.classList.toggle('mg-compact',compact);
    node.querySelectorAll('.mg-day-details>td,.mg-editor-row>td').forEach(td=>td.colSpan=compact?3:11);
    const bands=node.querySelectorAll('.mg-band th');if(bands.length===3){bands[0].colSpan=compact?1:3;bands[1].colSpan=compact?1:4;bands[2].colSpan=compact?1:4;}
    node.querySelectorAll('.mg-subtotal>th').forEach(th=>th.colSpan=compact?1:3);
    node.querySelectorAll('.mg-compact-subtotal').forEach(td=>td.hidden=!compact);
  }
  function scheduleDay(){clearTimeout(dayTimer);dayTimer=null;if(!live())return;const next=new Date();next.setHours(24,0,1,0);dayTimer=setTimeout(()=>{dayTimer=null;if(live()){render();scheduleDay();}},Math.max(1000,+next-Date.now()));}
  function initialize(){
    if(initialized)return;initialized=true;
    const node=el('management');if(!node)return;
    node.classList.add('mg-app');node.addEventListener('click',onClick);node.addEventListener('change',onChange);node.addEventListener('input',onInput);node.addEventListener('keydown',onKey);
    if(typeof ResizeObserver==='function'){resizeObserver=new ResizeObserver(resize);resizeObserver.observe(el('managementContent'));}
    document.addEventListener('visibilitychange',()=>{if(!document.hidden&&active){render();scheduleDay();}else{clearTimeout(dayTimer);dayTimer=null;}});
    window.addEventListener('storage',event=>{if(typeof LSKEY!=='undefined'&&event.key===LSKEY){if(editor){invalidateEditorReview('A base mudou em outra aba. Preserve os campos e atualize a revisão antes de confirmar.');}else if(active)render();}});
  }
  function activate(next='accounting'){surface=next==='reserves'?'reserves':'accounting';active=true;initialize();render();scheduleDay();}
  function deactivate(){active=false;clearTimeout(dayTimer);dayTimer=null;rememberEditor();if(surface==='reserves'){rememberReserveDraft();clearReserveForm();}closeDialog(false);}
  function reset(){deactivate();drafts.clear();reserveDrafts.clear();clearReserveForm();editor=null;selection={accountId:'',periodId:'',year:new Date().getFullYear()};lastModel=null;notice='';api()?.invalidate?.();}
  function setView(){activate('accounting');return true;}
  function context(){return {accountId:selection.accountId||null,periodId:selection.periodId||null};}
  function rememberEditor(){if(editor?.dirty)drafts.set(editor.key,{kind:editor.kind,date:editor.date,values:fields(editor.node),dirty:true,key:editor.key});}
  function fields(node){const values={};node?.querySelectorAll('input,textarea,select').forEach(n=>{if(n.name)values[n.name]=n.type==='checkbox'?n.checked:n.value;});return values;}
  function fillFields(node,values){for(const [name,value]of Object.entries(values||{})){const n=node.querySelector('[name="'+CSS.escape(name)+'"]');if(n){if(n.type==='checkbox')n.checked=!!value;else n.value=value;}}}
  function dropEditor(){if(editor){editor.node.closest('.mg-editor-row')?.remove();if(editor.kind==='plan')editor.node.remove();drafts.delete(editor.key);}editor=null;}
  function guardNavigation(plan,resume){
    if(!editor?.dirty&&!reserveDirty())return true;
    if(dialog)return false;guardCallback=resume;
    openDialog('Há um preenchimento não salvo','<p>'+h(reserveDirty()?'Este rascunho de Reservas pertence à conta e ao período indicados. Trocar o contexto ou sair não registra reservas.':'Escolha como continuar. Abrir outra área não registra o resultado nem a programação.')+'</p><div class="mg-actions">'+button('guard-stay','Continuar editando','',true)+button('guard-preserve','Preservar rascunho e sair')+button('guard-discard','Descartar rascunho e sair')+'</div>','guard');return false;
  }
  function changeContext(next){
    const control=document.activeElement,selector=control?.matches('[data-mg-account]')?'[data-mg-account]':control?.matches('[data-mg-period]')?'[data-mg-period]':control?.matches('[data-mg-year]')?'[data-mg-year]':null;
    const apply=()=>{rememberEditor();dropEditorPreserving();if(surface==='reserves'){rememberReserveDraft();clearReserveForm();}selection=next;notice='';render(true);};
    if(guardNavigation({primary:'management'},apply))apply();else{
      installContext();
      // A native change updates the live value, even when cached markup is
      // unchanged. Keep the accepted context visible while its draft is held.
      for(const [query,value]of [['[data-mg-account]',selection.accountId],['[data-mg-period]',selection.periodId],['[data-mg-year]',selection.year]]){
        const field=host()?.querySelector(query);if(field)field.value=String(value??'');
      }
      if(selector&&dialogKind==='guard')dialogTrigger=host()?.querySelector(selector);
    }
  }
  function dropEditorPreserving(){if(editor){editor.node.closest('.mg-editor-row')?.remove();if(editor.kind==='plan')editor.node.remove();editor=null;}}
  function expand(day){
    const n=el('mg-details-'+day);if(!n)return;
    const was=n.hidden;el('managementContent')?.querySelectorAll('.mg-day-details').forEach(x=>x.hidden=true);
    el('managementContent')?.querySelectorAll('[data-mg-detail]').forEach(x=>x.setAttribute('aria-expanded','false'));
    n.hidden=!was;const b=el('managementContent')?.querySelector('[data-mg-detail="'+day+'"]');b?.setAttribute('aria-expanded',String(was));
  }
  function field(name,label,type,value='',extra=''){return '<label>'+h(label)+'<input name="'+name+'" type="'+type+'" value="'+h(value)+'" '+extra+'></label>';}
  function planEditor(savedDraft){
    if(editor){if(editor.dirty){guardNavigation({},()=>planEditor(savedDraft));return;}dropEditor();}
    const old=lastModel?.plan?.config||lastModel?.model?.config||{},p=contextRead();
    const start=String(selection.year)+'-01-01',first=p?.startedAt&&p.startedAt>start?p.startedAt:start;
    const body=el('managementContent');if(!body)return;
    const box=document.createElement('section');box.className='mg-editor mg-plan-editor';box.dataset.mgEditor='plan';
    box.innerHTML='<h3>'+h(lastModel?.plan?'Revisar programação':'Planejamento anual')+'</h3><p>'+h(accountName())+' · '+h(selection.year)+' · Preencher não grava.</p><div class="mg-fields">'+field('startDate','Data inicial','date',old.startDate||first,'required min="'+selection.year+'-01-01" max="'+selection.year+'-12-31"')+field('annualTarget','Meta anual (%)','number',finite(old.annualTarget)?old.annualTarget*100:'','required step="any" min="-99.999999"')+field('daysPerWeek','Dias na semana','number',old.daysPerWeek??'','required min="0.01" max="7" step="any"')+field('monthsPerYear','Meses no ano','number',old.monthsPerYear??'','required min="0.01" max="12" step="any"')+'<label class="mg-full">Datas excluídas da programação<textarea name="excludedDates" rows="2" placeholder="AAAA-MM-DD, separadas por vírgula">'+h((old.excludedDates||[]).join(', '))+'</textarea><small>Feriados ou folgas planejadas declarados por você; não excluem fechamentos existentes.</small></label></div><details><summary>Referência de dias · planilha</summary><div class="mg-fields">'+field('referenceYears','Anos de referência','number',old.referenceYears??1,'min="0.01" step="any"')+field('referenceDays','Dias brutos de referência','number',old.referenceDays??364,'min="0.01" step="any"')+'</div><p>Referências descritivas da planilha. Não substituem o calendário de dias úteis.</p></details>'+field('reason','Motivo da configuração ou revisão','text','','maxlength="500"')+'<div class="mg-editor-preview" data-mg-preview aria-live="polite"></div><p class="mg-editor-message" role="status"></p><div class="mg-actions">'+button('review-plan','Revisar programação','',true)+button('cancel-edit','Cancelar')+'</div>';
    body.prepend(box);editor={key:key(),kind:'plan',node:box,dirty:false,review:null,date:null};if(savedDraft){fillFields(box,savedDraft.values);editor.dirty=true;}
    box.querySelector('input')?.focus({preventScroll:true});box.scrollIntoView({block:'start',behavior:'instant'});
  }
  function planInput(){const v=fields(editor.node);return {...target(),startDate:v.startDate,annualTarget:v.annualTarget===''?null:Number(v.annualTarget)/100,daysPerWeek:v.daysPerWeek===''?null:Number(v.daysPerWeek),monthsPerYear:v.monthsPerYear===''?null:Number(v.monthsPerYear),excludedDates:v.excludedDates.split(/[\s,;]+/).filter(Boolean),referenceYears:Number(v.referenceYears),referenceDays:Number(v.referenceDays)};}
  function editDay(day,kind='day',savedDraft){
    if(day>date()){setNotice('Datas futuras pertencem à projeção; não recebem fechamento realizado.');return;}
    if(editor){if(editor.dirty){guardNavigation({},()=>editDay(day,kind,savedDraft));return;}dropEditor();}
    let row=lastModel?.model?.rows?.find(r=>r.date===day);
    if(!row){
      const config=lastModel?.model?.config;
      if(!config||root.JPWAnnualEngine.dateKey(day)!==day||day<config.startDate||day.slice(0,4)!==String(selection.year)){setNotice('A data está fora do ano ou do início do plano.');return;}
      row={date:day,eligible:false,planned:{},actual:{status:'PENDING'}};
      const tbody=el('managementContent')?.querySelector('.mg-sheet tbody');
      const next=[...(tbody?.querySelectorAll('.mg-day')||[])].find(n=>n.dataset.mgDate>day);
      if(next)next.insertAdjacentHTML('beforebegin',dailyRow(row));else tbody?.insertAdjacentHTML('beforeend',dailyRow(row));
    }
    const before=el('mg-details-'+day);if(!before)return;
    const tr=document.createElement('tr');tr.className='mg-editor-row';const td=document.createElement('td');td.colSpan=11;tr.append(td);
    const box=document.createElement('section');box.className='mg-editor';box.dataset.mgEditor=kind;td.append(box);
    const title=kind==='revoke'?'Revogar declaração':kind==='void'?'Anular fechamento':kind==='no-result'?'Declarar dia sem resultado':row.actual?.record?'Corrigir resultado':'Registrar resultado';
    box.innerHTML='<h3>'+h(title)+' · '+h(fmtDate(day))+'</h3><p>'+h(accountName())+' · '+h(contextRead()?.currency||'')+'</p>'+
      (kind==='day'?'<div class="mg-fields">'+field('value','Resultado do dia ('+(contextRead()?.currency||'')+')','number',row.actual?.result??'','step="any" required')+field('note','Nota opcional','text',row.actual?.record?.nota||'','maxlength="500"')+'</div>':'')+
      (kind==='revoke'?'<p>A declaração anterior continuará no histórico. A data ficará pendente para receber um fechamento real ou uma nova declaração explícita.</p>':'')+(kind==='no-result'?'<p>Esta declaração afirma que não houve resultado realizado nesta data. Não operar, por si só, não comprova ausência de taxas, juros ou outros resultados.</p>':'')+
      field('reason',kind==='day'&&!row.actual?.record?'Motivo / referência opcional':'Motivo da declaração ou correção','text','','maxlength="500"')+
      '<div class="mg-editor-preview" data-mg-preview aria-live="polite"></div><p class="mg-editor-message" role="status"></p><div class="mg-actions">'+button('review-day','Revisar','',true)+button('cancel-edit','Cancelar')+'</div>';
    before.after(tr);editor={key:key(),kind,date:day,node:box,recordId:row.actual?.record?.id||null,dirty:false,review:null};if(savedDraft){fillFields(box,savedDraft.values);editor.dirty=true;}
    resize();box.querySelector('input')?.focus({preventScroll:true});box.scrollIntoView({block:'nearest',behavior:'instant'});
  }
  function setEditorMessage(value){const n=editor?.node.querySelector('.mg-editor-message');if(n)n.textContent=value;}
  function errors(result){return (result?.errors||[result?.error||'Não foi possível confirmar. Preserve o preenchimento e confira a revisão.']).map(x=>typeof x==='string'?x:x.message||String(x)).join(' ');}
  function invalidateEditorReview(message){
    if(!editor)return;editor.review=null;
    editor.node.querySelectorAll('[name="confirm"],[name="confirmOpening"]').forEach(n=>{n.checked=false;});
    const b=editor.node.querySelector('[data-mg-action="confirm-editor"]');
    if(b){b.dataset.mgAction=editor.kind==='plan'?'review-plan':'review-day';b.textContent='Atualizar revisão';}
    setEditorMessage(message);
  }
  function refreshReviewState(){
    if(!editor?.review)return;
    if(JSON.stringify(api()?.queries.token(target()))!==JSON.stringify(editor.review.token)){
      invalidateEditorReview('Os dados mudaram. Atualize a revisão para conferir os valores atuais; o preenchimento foi preservado.');
    }
  }
  function reviewPlan(){
    const input=planInput(),r=api().queries.previewPlan(input);if(!r.ok){setEditorMessage(errors(r));return;}
    editor.review={...r,input,token:r.token||api().queries.token(target())};const s=r.model?.summary||{};
    editor.node.querySelector('[data-mg-preview]').innerHTML='<h4>Confira antes de salvar</h4><p>Saldo inicial confirmado: <strong>'+h(money(r.config?.initialBalance))+'</strong> · '+h(r.openingSource?.date?fmtDate(r.openingSource.date):'abertura do período')+'</p><p>Meta proporcional '+h(pct(s.partialTarget))+' · meta diária '+h(pct(s.dailyTarget))+' · '+h(num(s.eligibleDays))+' datas disponíveis.</p><label class="mg-check"><input name="confirmOpening" type="checkbox"> Conferi a conta, o período, o saldo e a programação.</label>';
    const b=editor.node.querySelector('[data-mg-action="review-plan"]');b.dataset.mgAction='confirm-editor';b.textContent='Confirmar programação';setEditorMessage('A programação será gravada. Nenhum fechamento diário será criado.');
  }
  function reviewDay(){
    const v=fields(editor.node);let r;
    if(editor.kind==='day')r=api().queries.previewResult({target:target(),date:editor.date,value:v.value===''?null:Number(v.value),id:editor.recordId,note:v.note||''});
    else if(editor.kind==='revoke')r={ok:true,token:api().queries.token(target())};
    else if(editor.kind==='no-result')r=api().queries.previewNoResult?.({target:target(),date:editor.date,reason:v.reason})||{ok:true,token:api().queries.token(target())};
    else r=api().queries.previewVoidResult?.({target:target(),date:editor.date,id:editor.recordId,reason:v.reason})||api().queries.previewResult({target:target(),date:editor.date,value:0,id:editor.recordId});
    if(!r.ok){setEditorMessage(errors(r));return;}
    if((editor.kind!=='day'||editor.recordId)&&!v.reason.trim()){setEditorMessage('Informe o motivo antes de revisar.');return;}
    editor.review={...r,token:r.token||api().queries.token(target()),input:{target:target(),date:editor.date,...(editor.kind==='day'?{value:v.value===''?null:Number(v.value),id:editor.recordId,note:v.note||''}:editor.kind==='void'?{id:editor.recordId}:{})}};
    editor.node.querySelector('[data-mg-preview]').innerHTML='<h4>Confira o registro</h4>'+(editor.kind==='day'?'<div class="mg-review-values">'+metric('Abertura',money(r.opening))+metric('Resultado informado',money(r.result??Number(v.value)))+metric('Fechamento',money(r.closing))+'</div>':'<p>'+h(editor.kind==='revoke'?'A declaração será revogada, com preservação do histórico. A data voltará a ficar pendente.':editor.kind==='void'?'O fechamento será anulado, com preservação do histórico.':'A data será marcada por declaração explícita, sem criar um lançamento zero.')+'</p>')+
      (r.affectedDates?.length?'<p>'+h(r.affectedDates.length+' fechamentos posteriores dependentes poderão ser recalculados. Saldos observados são preservados.')+'</p>':'')+'<label class="mg-check"><input name="confirm" type="checkbox"> Conferi este ato e seus efeitos.</label>';
    const b=editor.node.querySelector('[data-mg-action="review-day"]');b.dataset.mgAction='confirm-editor';b.textContent=editor.kind==='revoke'?'Confirmar revogação':editor.kind==='void'?'Confirmar anulação':editor.kind==='no-result'?'Confirmar declaração':'Confirmar fechamento';setEditorMessage('Nada foi registrado ainda.');
  }
  function confirmEditor(){
    if(!editor?.review||!canEdit())return;refreshReviewState();if(!editor.review)return;
    const v=fields(editor.node),e=editor,r=e.review;
    if(e.kind==='plan'&&!v.confirmOpening||e.kind!=='plan'&&!v.confirm){setEditorMessage('Confira a revisão e marque a confirmação.');return;}
    const opts={token:r.token,confirm:true,confirmOpening:v.confirmOpening===true,reason:v.reason||'Fechamento diário explicitamente confirmado'};
    let result;
    try{
      if(e.kind==='plan')result=api().commands.savePlan(r.input,opts);
      else if(e.kind==='day')result=api().commands.recordResult(r.input,opts);
      else if(e.kind==='revoke')result=api().commands.revokeNoResult(r.input,opts);
      else if(e.kind==='void')result=api().commands.voidResult(r.input,opts);
      else result=api().commands.declareNoResult(r.input,opts);
    }catch(_){setEditorMessage('Confirmação interrompida. Não repita o ato sem conferir a base salva.');return;}
    if(!result?.ok){setEditorMessage(errors(result));editor.review=null;const b=e.node.querySelector('[data-mg-action="confirm-editor"]');if(b){b.dataset.mgAction=e.kind==='plan'?'review-plan':'review-day';b.textContent='Atualizar revisão';}return;}
    const day=e.date;dropEditor();notice=e.kind==='plan'?'Programação confirmada.':'Registro confirmado.';render(true);
    focusEditorReturn(day,e.kind);
    if(typeof renderDash==='function')renderDash();root.JPWNotifications?.invalidate?.('forex');
  }
  function annualReview(){
    if(editor?.dirty){guardNavigation({},annualReview);return;}
    if(editor)dropEditor();
    const r=api().queries.previewAnnualClose(target());
    const pending=r.model?.summary?.pendingDates||lastModel?.model?.summary?.pendingDates||[];
    const content='<p>'+h(accountName())+' · '+h(selection.year)+' · referência em 31/12.</p>'+(!r.ok?'<p class="mg-pending">'+h(errors(r))+'</p>':'<p>O retrato anual preservará a programação e os fechamentos identificados. Não encerra operações nem o período do Forex.</p><label class="mg-check"><input type="checkbox" data-mg-annual-confirm> Conferi o período, os resultados e as declarações.</label>')+(pending.length?'<p>'+h('Primeira pendência: '+fmtDate(pending[0]))+'</p>'+button('annual-pending','Ir à pendência','data-mg-date="'+h(pending[0])+'"'):'')+'<p role="status" data-mg-annual-status></p><div class="mg-actions">'+(r.ok?button('annual-confirm','Confirmar fechamento anual','',true):'')+button('close-dialog','Cancelar')+'</div>';
    if(openDialog('Fechamento anual',content,'annual'))dialog.__review={...r,target:target()};
  }
  function confirmAnnual(){
    const r=dialog?.__review;if(!r)return;const response=dialog.querySelector('[data-mg-annual-status]');
    if(!dialog.querySelector('[data-mg-annual-confirm]')?.checked){response.textContent='Confira e marque a confirmação do período.';return;}
    const result=api().commands.closeAnnual(r.target,{token:r.token,confirm:true});
    if(!result?.ok){response.textContent=errors(result);const b=dialog.querySelector('[data-mg-action="annual-confirm"]');b.dataset.mgAction='annual-refresh';b.textContent='Atualizar revisão';return;}
    closeDialog();notice='Fechamento anual confirmado. O retrato e seu histórico foram preservados.';render(true);el('managementContent')?.querySelector('[data-mg-action="annual-review"]')?.focus({preventScroll:true});
  }
  function history(){
    const plans=api().queries.listPlans(target()),list=Array.isArray(plans)?plans:plans?.plans||[];
    openDialog('Períodos fechados',button('export-audit','Exportar log de auditoria')+'<p>Os retratos anteriores não são sobrescritos por correções posteriores.</p>'+(list.length?list.map(p=>'<section class="mg-history"><h3>'+h(p.year||p.config?.year)+'</h3>'+((p.snapshots||p.closures||[]).map(s=>'<p>'+h(s.confirmedAt||s.at||'Retrato preservado')+' · '+h(s.status||'Confirmado')+' '+button('history-detail','Ver retrato','data-mg-plan="'+h(p.id)+'" data-mg-snapshot="'+h(s.id)+'"')+'</p>').join('')||'<p>Ano ainda sem fechamento anual.</p>')+'</section>').join(''):'<p>Nenhum fechamento anual registrado.</p>'));
  }
  function onInput(event){
    if(!editor?.node.contains(event.target))return;editor.dirty=true;rememberEditor();
    if(['confirm','confirmOpening'].includes(event.target.name))return;
    editor.review=null;editor.node.querySelector('[data-mg-preview]').replaceChildren();
    const b=editor.node.querySelector('[data-mg-action="confirm-editor"]');if(b){b.dataset.mgAction=editor.kind==='plan'?'review-plan':'review-day';b.textContent='Revisar';}setEditorMessage('Rascunho não salvo.');
  }
  function onChange(event){
    const n=event.target;
    if(n.matches('[data-mg-account]'))changeContext({accountId:n.value,periodId:'',year:selection.year});
    else if(n.matches('[data-mg-period]'))changeContext({...selection,periodId:n.value});
    else if(n.matches('[data-mg-year]')){if(Number.isInteger(Number(n.value))&&Number(n.value)>=1900&&Number(n.value)<=9999)changeContext({...selection,year:Number(n.value)});else{n.value=selection.year;setNotice('Informe um ano entre 1900 e 9999.');}}
    else onInput(event);
  }
  function focusEditorReturn(day,kind){
    const body=el('managementContent');
    const node=day?body?.querySelector('[data-mg-detail="'+day+'"]')||body?.querySelector('[data-mg-action="other-date"]'):
      kind==='plan'?body?.querySelector('[data-mg-action="edit-plan"],[data-mg-action="new-plan"]'):null;
    node?.focus({preventScroll:true});
  }
  function onKey(event){if(event.key==='Escape'&&editor&&!dialog){event.preventDefault();event.stopPropagation();editor.node.querySelector('[data-mg-action="cancel-edit"]')?.click();}}
  function onClick(event){
    const detail=event.target.closest('[data-mg-detail]');if(detail){expand(detail.dataset.mgDetail);return;}
    const n=event.target.closest('[data-mg-action]');if(!n)return;const a=n.dataset.mgAction;
    if(a==='info'){info();return;}
    if(a==='close-dialog'||a==='guard-stay'){guardCallback=null;closeDialog();return;}
    if(a==='guard-preserve'||a==='guard-discard'){
      const resume=guardCallback;guardCallback=null;
      if(a==='guard-preserve'){rememberEditor();dropEditorPreserving();if(reserveDirty()){rememberReserveDraft();clearReserveForm();}}
      else{dropEditor();if(reserveDirty()){reserveDrafts.delete(reserveKey(reserveFormScope(el('fxReserveFacts'))));clearReserveForm();}}
      closeDialog();if(resume)resume();return;
    }
    if(a==='account-new'||a==='account-setup'){
      const launch=()=>{const opts={owner:'management',accountId:a==='account-setup'?selection.accountId:null,returnFocus:n,trigger:n,onSaved:()=>render(true)};root.JPWFXConsolidatedUI?.[a==='account-new'?'openAccountRegistration':'openAccountSetup']?.(opts);};
      if(guardNavigation({},launch))launch();return;
    }
    if(a==='new-plan'||a==='edit-plan'){planEditor();return;}
    if(a==='resume'){const d=drafts.get(key());if(d?.kind==='plan')planEditor(d);else if(d)editDay(d.date,d.kind,d);return;}
    if(a==='edit-day'){editDay(n.dataset.mgDate);return;}
    if(a==='revoke-no-result'){editDay(n.dataset.mgDate,'revoke');return;}
    if(a==='no-result'){editDay(n.dataset.mgDate,'no-result');return;}
    if(a==='void-day'){editDay(n.dataset.mgDate,'void');return;}
    if(a==='review-plan'){reviewPlan();return;}
    if(a==='review-day'){reviewDay();return;}
    if(a==='confirm-editor'){confirmEditor();return;}
    if(a==='cancel-edit'){const day=editor?.date,kind=editor?.kind;dropEditor();notice='Edição cancelada. Nenhum registro foi alterado.';render(true);focusEditorReturn(day,kind);return;}
    if(a==='other-date'){
      openDialog('Registrar outra data','<p>Uma data fora da programação também pode ter resultado real. Ela não muda a programação confirmada.</p>'+field('otherDate','Data do fechamento','date','','min="'+h(lastModel?.model?.config?.startDate)+'" max="'+h(date())+'"')+'<p data-mg-date-error role="status"></p><div class="mg-actions">'+button('choose-date','Preencher resultado','',true)+button('close-dialog','Cancelar')+'</div>','date');return;
    }
    if(a==='choose-date'){
      const day=dialog?.querySelector('[name="otherDate"]')?.value,c=lastModel?.model?.config;
      if(!c||root.JPWAnnualEngine.dateKey(day)!==day||day<c.startDate||day>date()||day.slice(0,4)!==String(selection.year)){dialog.querySelector('[data-mg-date-error]').textContent='Escolha uma data deste ano, desde o início do plano até hoje.';return;}
      closeDialog();editDay(day);return;
    }
    if(a==='annual-refresh'){closeDialog();annualReview();return;}
    if(a==='annual-review'){annualReview();return;}
    if(a==='annual-confirm'){confirmAnnual();return;}
    if(a==='export-audit'){if(typeof exportAudit==='function')exportAudit();return;}
    if(a==='history'){history();return;}
    if(a==='history-detail'){
      const p=api().queries.listPlans(target()).find(x=>x.id===n.dataset.mgPlan),snapshot=p?.snapshots?.find(x=>x.id===n.dataset.mgSnapshot);
      if(!snapshot)return;
      const currency=p.history.find(r=>r.revision===snapshot.planRevision)?.config.currency||p.config.currency;
      closeDialog();openDialog('Retrato anual · '+p.year,'<p>Confirmado em '+h(snapshot.at)+' · revisão da programação '+h(snapshot.planRevision)+'.</p><div class="mg-metrics">'+metric('Saldo inicial',money(snapshot.summary.initialBalance,currency))+metric('Saldo confirmado',money(snapshot.summary.currentBalance,currency))+metric('Resultado',money(snapshot.summary.accumulatedResult,currency))+metric('Dias com fechamento',num(snapshot.summary.recordedDays))+'</div><p>Este retrato histórico não muda quando os registros posteriores são corrigidos.</p><div class="mg-snapshot-table"><table><thead><tr><th>Data</th><th>Resultado</th><th>Fechamento</th></tr></thead><tbody>'+snapshot.rows.map(r=>'<tr><td>'+h(fmtDate(r.date))+'</td><td>'+h(money(r.actual?.result,currency))+'</td><td>'+h(money(r.actual?.closing,currency))+'</td></tr>').join('')+'</tbody></table></div>');return;
    }
    if(a==='first-pending'||a==='annual-pending'){
      const day=n.dataset.mgDate||lastModel?.model?.summary?.pendingDates?.[0];if(dialog)closeDialog();const b=el('managementContent')?.querySelector('[data-mg-detail="'+day+'"]');if(b){if(el('mg-details-'+day)?.hidden)b.click();b.focus({preventScroll:true});b.scrollIntoView({block:'center',behavior:'instant'});}return;
    }
  }
  function backupDrafts(clear){
    if(clear){reset();return [];}rememberEditor();rememberReserveDraft();
    return [...drafts.values()].map(d=>({provider:'management-annual',version:1,label:'Gerenciamento — rascunho anual',context:{key:d.key,action:d.kind,date:d.date||null,formVersion:1},baseReference:d.key,text:JSON.stringify({fields:d.values})})).concat(
      [...reserveDrafts.values()].map(d=>({provider:'management-annual',version:1,label:'Gerenciamento — rascunho de Reservas',context:{key:d.key,action:'reserves',accountId:d.scope.accountId,periodId:d.scope.periodId,formVersion:1},baseReference:d.key,text:JSON.stringify({fields:d.values,capturedReview:d.review})})));
  }
  root.JPWManagement=Object.freeze({activate,deactivate,reset,setView,render,context,guardNavigation,hasPendingWork,backupDrafts});
  if(typeof jpwWorkspaceDraftProviders!=='undefined')jpwWorkspaceDraftProviders.set('management-annual',backupDrafts);
  root.JPWWorkspaceDrafts?.registerRestorer('management-annual',{inspect:()=>({compatible:false,reason:'Rascunho de Gerenciamento preservado para leitura e cópia. Reabra a conta, o período e o ano e revise os valores antes de confirmar.'}),reopen:()=>{throw new Error('Confira o contexto atual antes de preencher novamente.');}});
})(globalThis);

// Contas e Período: exploração RAM; fatos e cadastro usam os comandos existentes.
(function(root){
  'use strict';
  const fx=root.JPWForex,el=id=>document.getElementById(id),safe=value=>esc(String(value??''));
  let mounted=false,examinedAccountId=null,examinedPeriodId=null,epoch=null,dirty=false,leaving=false,formScope='',periodAttempt=null,saving=false;
  const records=()=>Array.isArray(S.accounts)?S.accounts:[];
  const idOf=(account,index)=>account.forexAccountId||'live:'+index;
  const find=id=>records().map((account,index)=>({account,index,id:idOf(account,index)})).find(row=>row.id===id)||null;
  const periods=id=>S.forex?.accountContexts?.accounts?.[id]?.periods||{};
  const selectedPeriod=()=>periods(examinedAccountId)[examinedPeriodId]||null;
  const money=(value,currency)=>typeof value==='number'&&Number.isFinite(value)?fmtForexMoney(value,{currency:currency||null}):'Indisponível';
  function status(message,error=false){const node=el('fxAccountsStatus');if(node){node.textContent=message;node.dataset.kind=error?'error':'info';}}
  function examination(){return {accountId:examinedAccountId,periodId:examinedPeriodId};}
  function hasDrafts(){return dirty||el('fxAccountFacts')?.dataset.fxTouched==='true';}
  function resetForms(){
    for(const id of ['accountPeriodStart','accountPeriodSI','accountPeriodBook','accountPeriodSource','accountPeriodReason'])if(el(id))el(id).value='';
    if(el('accountObservedPeriod'))el('accountObservedPeriod').value='';
    if(el('accountPeriodActivate'))el('accountPeriodActivate').checked=false;
    const form=el('fxAccountFacts');if(form){form.reset();form.dataset.fxTouched='';}
    dirty=false;periodAttempt=null;
  }
  function requestLeave(callback){
    if(saving){status('A confirmação do período está em andamento. Aguarde o resultado antes de mudar de contexto.',true);return false;}
    if(leaving||!hasDrafts()){callback();return true;}
    if(el('fxAccountsLeaveDialog')?.open)return false;
    let dialog=el('fxAccountsLeaveDialog');
    if(!dialog){dialog=document.createElement('dialog');dialog.id='fxAccountsLeaveDialog';dialog.className='fxc-registration';dialog.setAttribute('aria-labelledby','fxAccountsLeaveTitle');document.body.append(dialog);}
    const opener=document.activeElement;
    dialog.innerHTML='<h2 id="fxAccountsLeaveTitle">Preservar o preenchimento?</h2><p>Há dados de período ou observação ainda não confirmados. Permaneça para revisar e salvar cada registro, ou descarte apenas este preenchimento.</p><footer><button type="button" id="fxAccountsStay">Permanecer</button><button type="button" id="fxAccountsDiscard">Descartar preenchimento e continuar</button></footer>';
    const restore=()=>{if(root.shellFocusAvailable?.(opener))opener.focus({preventScroll:true});};
    dialog.oncancel=event=>{event.preventDefault();dialog.close();restore();};
    el('fxAccountsStay').onclick=()=>{dialog.close();restore();};
    el('fxAccountsDiscard').onclick=()=>{dialog.close();resetForms();leaving=true;try{callback();}finally{leaving=false;}};
    dialog.showModal();el('fxAccountsStay').focus();return false;
  }
  function examine(accountId,periodId=null){
    const row=find(accountId);if(!row){status('A conta não está mais disponível. Atualize a consulta.',true);return false;}
    if(periodId&&!periods(accountId)[periodId]){status('O período não pertence à conta examinada.',true);return false;}
    return requestLeave(()=>{
      if(!find(accountId)||(periodId&&!periods(accountId)[periodId])){status('A conta ou o período mudou. Atualize a consulta.',true);return;}
      examinedAccountId=accountId;examinedPeriodId=periodId||S.forex?.accountContexts?.accounts?.[accountId]?.currentPeriodId||null;
      formScope='';resetForms();render();el('fxAccountDetailTitle')?.focus({preventScroll:true});
    });
  }
  function validContext(accountId,periodId){
    return fx.state.supported()&&records().filter(a=>a?.forexAccountId===accountId).length===1&&!!periodId&&fx.state.accountContext({accountId,periodId}).status==='OK';
  }
  function guardNavigation(plan,resume){
    if(leaving||!el('exec')?.classList.contains('active')||root.JPWExec?.ui?.getView()!=='accounts'||plan.action==='settings'||plan.action==='checklist')return true;
    if(plan.screen==='exec'&&plan.localView?.view==='accounts')return true;
    if(!hasDrafts())return true;requestLeave(resume);return false;
  }
  function useContext(accountId,periodId,{onAccepted}={}){
    if(!validContext(accountId,periodId)){status('Confirme a conta e um período pertencente a ela antes de abrir a Board.',true);return false;}
    let accepted=false;
    const apply=()=>requestLeave(()=>{
      if(!validContext(accountId,periodId)){status('Conta ou período mudou. Revise o contexto antes de continuar.',true);return;}
      // Nenhuma seleção é aplicada se o destino for recusado. Validação e
      // aplicação do par são síncronas; o repaint usa o contexto já confirmado.
      leaving=true;
      try{
        if(root.JPWNavigation?.navigate('forex-operation')!==true){status('A navegação não foi aceita. O contexto operacional foi preservado.',true);return;}
        const result=fx.state.selectOperationalContext(accountId,periodId);
        if(!result.ok){status(result.error||'Contexto não aplicado.',true);root.JPWNavigation.navigate('forex-management-accounts');return;}
        examinedAccountId=accountId;examinedPeriodId=periodId;accepted=true;
        if(typeof root.render==='function')root.render();
        fx.executionBoardUI?.render?.();if(typeof renderLedger==='function')renderLedger();if(typeof renderMotor==='function')renderMotor();
        render();root.JPWNavigation.focusCurrentScreen?.();if(typeof onAccepted==='function')onAccepted(result);
      }finally{leaving=false;}
    });
    if(fx.executionBoardUI?.requestLeave)fx.executionBoardUI.requestLeave(apply,'Usar outra conta e período');else apply();
    return accepted;
  }
  function mount(){
    if(mounted||!el('contas'))return;mounted=true;epoch=jpWealthPersistenceEpoch();
    const workspace=document.createElement('div');workspace.id='forexAccountsWorkspace';workspace.className='fx-accounts-workspace';
    workspace.innerHTML='<header class="fx-accounts-heading"><div><p class="eb-eyebrow">FOREX · CADASTRO E CONTEXTO</p><h1>Contas e Período</h1><p>Organize suas contas de CFDs e seus períodos. Consultar uma conta não muda a operação em andamento.</p></div><div class="fx-accounts-actions"><button type="button" id="fxAccountsImport">Importar HTML/PDF</button><button type="button" id="fxAccountsCreate" class="fx-accounts-primary">Cadastrar nova conta</button></div></header><p id="fxAccountsOperational" class="fx-accounts-operational"></p><p id="fxAccountsStatus" role="status" aria-live="polite"></p><section aria-labelledby="fxAccountsListTitle" class="card fx-accounts-list"><h2 id="fxAccountsListTitle">Contas cadastradas</h2><div class="jp-table-scroll" tabindex="0" aria-label="Contas cadastradas, tabela com rolagem horizontal"><table class="dtable"><thead><tr><th>Conta e identificação</th><th>Corretora / plataforma</th><th>Moeda</th><th>Perfil cadastral</th><th>Preparação</th><th>Contexto em uso</th><th>Ação</th></tr></thead><tbody id="fxAccountsRows"></tbody></table></div><p id="fxAccountsEmpty" hidden>Nenhuma conta cadastrada. Cadastre a conta que você já utiliza na corretora e prepare seu primeiro período.</p></section><section id="fxAccountDetails" class="fx-account-details" aria-labelledby="fxAccountDetailTitle" hidden><div class="card"><div class="fx-accounts-detail-head"><div><p class="eb-eyebrow">CONTA EM CONSULTA</p><h2 id="fxAccountDetailTitle" tabindex="-1"></h2><p id="fxAccountMetadata"></p></div><div class="fx-accounts-actions"><button type="button" id="fxAccountsEdit">Atualizar cadastro e perfil</button><button type="button" id="fxAccountsPrepare">Preparar período</button><button type="button" id="fxAccountsArchive">Arquivar cadastro</button></div></div><dl id="fxAccountProfiles" class="fx-accounts-profiles"></dl><p class="fx-accounts-help">O perfil cadastral será declarado no próximo período criado explicitamente. O período consultado conserva sua referência; regras e proteções vigentes continuam sendo aplicadas.</p><button type="button" id="fxAccountsUse" class="fx-accounts-primary">Usar conta e período e abrir Execution Board</button><p id="fxAccountsUseHelp" class="fx-accounts-help"></p></div><div id="fxAccountPeriodHost"></div></section><details id="fxAccountsArchives" class="card"><summary>Contas arquivadas</summary><div id="fxAccountsArchivedRows"></div></details><p class="fx-accounts-help">Cadastro, período e observações são confirmações distintas. Nenhum deles equivale a autorização para operar. <button type="button" id="fxAccountsMotor" class="fx-accounts-link">Abrir Fator de Correção</button></p>';
    el('contas').prepend(workspace);
    if(el('accountPeriodCard'))el('fxAccountPeriodHost').append(el('accountPeriodCard'));
    const details=el('accountPeriodFormDetails');if(details?.querySelector('summary'))details.querySelector('summary').textContent='Conciliar uma observação histórica sem período';
    if(el('accountPeriodSave'))el('accountPeriodSave').textContent='Confirmar conciliação do período';
    el('fxAccountsImport').onclick=()=>requestLeave(()=>root.JPWFXConsolidatedUI.openImport({accountId:find(examinedAccountId)?.account.forexAccountId||null,returnFocus:el('fxAccountsImport')}));
    el('fxAccountsCreate').onclick=()=>requestLeave(()=>root.JPWFXConsolidatedUI.openAccountRegistration({trigger:el('fxAccountsCreate'),onSaved:result=>{examinedAccountId=result.accountId;examinedPeriodId=null;formScope='';render();status('Conta cadastrada. Prepare ou selecione seu período para utilizá-la na Board.');}}));
    el('fxAccountsEdit').onclick=()=>requestLeave(()=>root.JPWFXConsolidatedUI.openAccountRegistration({accountId:examinedAccountId,trigger:el('fxAccountsEdit'),onSaved:result=>{examinedAccountId=result.accountId;render();status('Cadastro confirmado. O perfil dos períodos anteriores foi preservado.');}}));
    el('fxAccountsPrepare').onclick=()=>requestLeave(()=>root.JPWFXConsolidatedUI.openAccountSetup({accountId:examinedAccountId,returnFocus:el('fxAccountsPrepare')}));
    el('fxAccountsUse').onclick=()=>useContext(examinedAccountId,examinedPeriodId);
    el('fxAccountsMotor').onclick=()=>root.JPWNavigation.navigate('motor');
    el('fxAccountsArchive').onclick=archive;
    el('fxAccountsRows').addEventListener('click',event=>{const button=event.target.closest('[data-fx-examine]');if(button)examine(button.dataset.fxExamine);});
    el('fxAccountsArchivedRows').addEventListener('click',event=>{const button=event.target.closest('[data-fx-reregister]');if(button)root.JPWFXConsolidatedUI.openAccountRegistration({accountId:button.dataset.fxReregister,trigger:button,onSaved:result=>{examine(result.accountId);render();}});});
    el('accountPeriodSelect')?.addEventListener('change',event=>{const old=examinedPeriodId,choice=event.target.value;event.target.value=old||'';if(choice)examine(examinedAccountId,choice);});
    el('accountObservedPeriod')?.addEventListener('change',()=>{
      const item=observation(examinedAccountId,el('accountObservedPeriod').value);
      if(item){el('accountPeriodSI').value=item.si??'';el('accountPeriodCurrency').value=item.currency||'';el('accountPeriodStart').value=item.observedAt?.slice(0,10)||'';el('accountPeriodActivate').checked=false;}
    });
    el('accountPeriodCard')?.addEventListener('input',event=>{if(event.target.closest('#accountPeriodFormDetails'))dirty=true;});
    el('accountPeriodCard')?.addEventListener('change',event=>{if(event.target.closest('#accountPeriodFormDetails'))dirty=true;});
    el('accountPeriodSave')?.addEventListener('click',saveConciliation);
    render();
  }
  function observation(accountId,periodId){let item=S.forex?.accounts?.[accountId],seen=new Set();while(item&&!seen.has(item)){if(item.periodId===periodId)return item;seen.add(item);item=item.previous;}return null;}
  function profileLabel(value){return value?.name||value?.profileName||value?.label||value?.profileKey||value?.key||'Não informado';}
  function rowStatus(account,id){
    if(!account.forexAccountId||!account.platform||!account.platformLogin)return 'Cadastro incompleto';
    if(!Object.keys(periods(id)).length)return 'Período pendente';
    if(!account.platformCurrency)return 'Moeda cadastral pendente';
    return 'Período disponível';
  }
  function render(){
    if(!mounted){mount();return;}if(typeof S==='undefined'||!S)return;
    if(epoch!==jpWealthPersistenceEpoch()){epoch=jpWealthPersistenceEpoch();examinedAccountId=null;examinedPeriodId=null;formScope='';resetForms();}
    const readable=Array.isArray(S.accounts)&&fx.state.supported();
    if(typeof renderContasMemory==='function'&&readable)renderContasMemory();
    const selection=fx.state.operationalSelection();
    if(!readable)status('Os dados de Forex não podem ser lidos nesta versão. Preserve a base e confira a recuperação antes de cadastrar ou alterar contas.',true);
    if(!find(examinedAccountId)){examinedAccountId=find(selection.accountId)?.id||records().map(idOf)[0]||null;examinedPeriodId=S.forex?.accountContexts?.accounts?.[examinedAccountId]?.currentPeriodId||null;formScope='';}
    if(examinedPeriodId&&!periods(examinedAccountId)[examinedPeriodId])examinedPeriodId=null;
    const operational=find(selection.accountId);
    el('fxAccountsOperational').textContent=operational?'Em uso na Board: '+(operational.account.nome||operational.id)+' · '+(selection.periodId||'período pendente'):'Nenhuma conta operacional selecionada.';
    el('fxAccountsEmpty').hidden=!readable||records().length>0;
    for(const id of ['fxAccountsCreate','fxAccountsImport','fxAccountsEdit','fxAccountsPrepare'])el(id).disabled=!readable;
    if(!readable){el('fxAccountsRows').replaceChildren();el('fxAccountDetails').hidden=true;return;}
    el('fxAccountsRows').innerHTML=records().map((account,index)=>{
      const id=idOf(account,index),profile=fx.state.accountProfileContext({accountId:id}),current=S.forex?.accountContexts?.accounts?.[id]?.currentPeriodId;
      return `<tr ${id===examinedAccountId?'class="fx-account-examined"':''}><th scope="row"><span>${safe(account.nome||'Conta sem nome')}</span><small>${safe(account.platformLogin||'Identificador pendente')} · ${safe(account.tipo||'Tipo não informado')}</small></th><td>${safe(account.broker||'Não informada')}<small>${safe(account.platform||'Plataforma pendente')}</small></td><td>${safe(account.platformCurrency||'Pendente')}</td><td>${safe(profile.current?.name||(account.perfil?account.perfil+' · legado':'Não informado'))}</td><td>${safe(rowStatus(account,id))}<small>${Object.keys(periods(id)).length} período(s)${current?' · atual '+safe(periods(id)[current]?.startedAt||''):''}</small></td><td>${selection.accountId===id?'<strong>Em uso</strong>':'—'}</td><td><button type="button" data-fx-examine="${safe(id)}" aria-pressed="${id===examinedAccountId}" aria-label="Consultar ${safe(account.nome||id)}">Consultar</button></td></tr>`;
    }).join('');
    const row=find(examinedAccountId),account=row?.account,p=selectedPeriod();el('fxAccountDetails').hidden=!row;
    if(row){
      el('fxAccountDetailTitle').textContent=account.nome||'Conta sem nome';
      el('fxAccountMetadata').textContent=[account.platform,account.platformLogin,account.broker,account.platformServer,account.platformCurrency,account.accountEnvironment==='real'?'Real':account.accountEnvironment==='demo'?'Demo':null].filter(Boolean).join(' · ')||'Complete os identificadores no cadastro.';
      const current=periods(examinedAccountId)[S.forex?.accountContexts?.accounts?.[examinedAccountId]?.currentPeriodId];
      const profile=fx.state.accountProfileContext({accountId:examinedAccountId,periodId:examinedPeriodId});
      const currentProfile=current?fx.state.accountProfileContext({accountId:examinedAccountId,periodId:current.periodId}):null;
      const accountProfile=profile.current?profileLabel(profile.current):profile.legacyName?profile.legacyName+' · legado sem atribuição registrada':'Não informado';
      el('fxAccountProfiles').innerHTML=`<div><dt>Perfil cadastral / próximo período</dt><dd>${safe(accountProfile)}</dd></div><div><dt>Perfil do período atual</dt><dd>${safe(current?currentProfile?.period?profileLabel(currentProfile.period):'Sem captura histórica':'Período pendente')}</dd></div><div><dt>Perfil do período consultado</dt><dd>${safe(p?profile.period?profileLabel(profile.period):'Sem captura histórica':'Período pendente')}</dd></div>`;
      const use=el('fxAccountsUse');use.disabled=!account.forexAccountId||!p;use.setAttribute('aria-describedby','fxAccountsUseHelp');
      el('fxAccountsUseHelp').textContent=!account.forexAccountId?'Confirme a identidade cadastral antes de preparar um período.':!p?'Selecione ou prepare um período. Informações financeiras ausentes continuam indicadas como pendentes.':selection.accountId===examinedAccountId&&selection.periodId===examinedPeriodId?'Este é o contexto operacional em uso.':'Consultar esta conta não altera a conta operacional. Use o botão acima para aplicar a escolha.';
      el('fxAccountsArchive').disabled=!account.forexAccountId;
      renderPeriod(account,p);
    }
    const archived=S.forex?.accountContexts?.archivedAccounts||{};
    el('fxAccountsArchivedRows').innerHTML=Object.entries(archived).filter(([id])=>!records().some(a=>a.forexAccountId===id)).map(([id,item])=>`<p><strong>${safe(item.record?.nome||id)}</strong> · ${safe(item.archivedAt||'Data indisponível')} · ${safe(item.reason||'Sem motivo informado')} <button type="button" data-fx-reregister="${safe(id)}">Recadastrar preservando identidade</button></p>`).join('')||'<p>Nenhuma conta arquivada.</p>';
  }
  function renderPeriod(account,p){
    el('accountContextIdentity').textContent=account.forexAccountId||'Identidade estável ainda não confirmada';
    const obs=observation(examinedAccountId,p?.periodId),lastBook=p?.ledger?.slice().sort((a,b)=>a.data.localeCompare(b.data)).at(-1)?.saldo??p?.openingBook??null;
    const entries=[['SI confirmado',money(p?.si,p?.currency)],['Saldo book de abertura',money(p?.openingBook,p?.currency)],['Último saldo book',money(lastBook,p?.currency)],['Equity observada',money(obs?.equity,p?.currency)],['Operação neste período',p?.activeOperation?.operationId||'Nenhuma']];
    el('accountContextMetrics').innerHTML=entries.map(([label,value])=>`<div class="metric"><div class="k">${safe(label)}</div><div class="v sm">${safe(value)}</div></div>`).join('');
    const list=Object.values(periods(examinedAccountId)).sort((a,b)=>a.startedAt.localeCompare(b.startedAt));
    el('accountPeriodSelect').innerHTML='<option value="">Sem período selecionado</option>'+list.map(item=>`<option value="${safe(item.periodId)}">${safe(item.startedAt)} · ${safe(item.currency)} · ${item.activeOperation?'operação em andamento':item.periodId===S.forex.accountContexts.accounts[examinedAccountId].currentPeriodId?'atual':'histórico'} · ${safe(item.periodId)}</option>`).join('');el('accountPeriodSelect').value=examinedPeriodId||'';
    const scope=examinedAccountId+'|'+(examinedPeriodId||'');
    if(scope!==formScope){resetForms();formScope=scope;el('accountPeriodCurrency').value=account.platformCurrency||'';el('accountPeriodFeedback').textContent='';}
    const seen=new Set(),unmatched=[];let item=S.forex?.accounts?.[examinedAccountId];
    while(item&&!seen.has(item)){seen.add(item);if(!periods(examinedAccountId)[item.periodId])unmatched.push(item);item=item.previous;}
    const select=el('accountObservedPeriod'),old=select.value;select.innerHTML='<option value="">Selecione uma observação não conciliada</option>'+unmatched.map(item=>`<option value="${safe(item.periodId)}">${safe(item.periodId)} · SI ${safe(item.si)} ${safe(item.currency)}</option>`).join('');select.value=unmatched.some(item=>item.periodId===old)?old:'';
    el('accountPeriodFormDetails').hidden=!unmatched.length;el('accountPeriodSave').disabled=saving||!account.forexAccountId;
    if(fx.ui?.render)fx.ui.render();
  }
  async function saveConciliation(){
    if(saving)return;
    const accountId=examinedAccountId,observationPeriodId=el('accountObservedPeriod').value,feedback=el('accountPeriodFeedback');
    if(!observationPeriodId){feedback.textContent='Selecione a observação histórica a conciliar.';return;}
    const optional=id=>el(id).value.trim()===''?null:Number(el(id).value);
    const input={startedAt:el('accountPeriodStart').value,currency:el('accountPeriodCurrency').value.trim().toUpperCase(),si:optional('accountPeriodSI'),openingBook:optional('accountPeriodBook'),source:el('accountPeriodSource').value.trim(),reason:el('accountPeriodReason').value.trim(),activateCurrentPeriod:el('accountPeriodActivate').checked,observationPeriodId,confirmPeriod:true};
    if(!periodAttempt){periodAttempt=root.JPWFXConsolidated.beginAccountSetup(accountId);if(!periodAttempt.ok){feedback.textContent=periodAttempt.error;periodAttempt=null;return;}}
    const attempt=periodAttempt;const requestEpoch=epoch;saving=true;el('accountPeriodSave').disabled=true;feedback.textContent='Confirmando conciliação…';
    try{
      const result=await root.JPWFXConsolidated.saveSetupPeriod(attempt.token,input);
      if(requestEpoch!==jpWealthPersistenceEpoch()||accountId!==examinedAccountId||periodAttempt!==attempt)return;
      if(!result.ok){feedback.textContent=result.error||'Conciliação não confirmada.';if(result.persistido===null)periodAttempt.unknown=true;return;}
      dirty=false;periodAttempt=null;examinedPeriodId=result.periodId;formScope='';render();status('Período conciliado. O contexto operacional foi preservado.');
    }catch(_){feedback.textContent='Conciliação não confirmada. Preserve o preenchimento e confira a sessão.';}
    finally{saving=false;if(el('accountPeriodSave'))el('accountPeriodSave').disabled=!!periodAttempt?.unknown;}
  }
  function archive(){
    const row=find(examinedAccountId);if(!row?.account.forexAccountId)return;
    requestLeave(()=>{
      if(row.account.tipo==='MESTRE'&&records().filter(a=>a.tipo==='MESTRE').length===1){status('Mantenha uma conta Mestre como referência para a correção de lote.',true);return;}
      if(!confirm('Arquivar '+(row.account.nome||row.id)+' preservando períodos e históricos?'))return;
      const reason=prompt('Motivo do arquivamento:');if(reason===null)return;
      const result=fx.state.archiveRegisteredAccount(row.id,{reason,expectedEpoch:jpWealthPersistenceEpoch()});
      if(!result.ok){status(result.error,true);return;}
      examinedAccountId=null;examinedPeriodId=null;formScope='';renderContas();fx.executionBoardUI?.render?.();status('Cadastro arquivado. Identidade, períodos e históricos foram preservados.');
    });
  }
  fx.accountsUI=Object.freeze({mount,render,examination,examine,useContext,requestLeave,guardNavigation,hasDrafts});
  mount();
})(globalThis);

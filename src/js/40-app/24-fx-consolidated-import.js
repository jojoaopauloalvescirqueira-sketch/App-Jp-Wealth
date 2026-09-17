// Consolidado FX: preparação em RAM e comandos explícitos sobre o escritor S.
// Não seleciona a conta operacional, não grava arquivos originais e não migra
// operações manuais. A prévia pública nunca é aceita como instrução de escrita.
(function(root){
  'use strict';
  const api=root.JPWFXConsolidated=root.JPWFXConsolidated||{};
  const own=(value,key)=>Object.prototype.hasOwnProperty.call(value,key);
  const text=value=>typeof value==='string'&&value.trim()?value.trim():null;
  const clone=value=>structuredClone(value);
  const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
  const fail=error=>({ok:false,persistido:false,error});
  let pending=null, registration=null, setup=null, generation=0, busy=false;

  function descriptor(account,index){
    const id=text(account.forexAccountId)||'live:'+index;
    const facts=object(S.forex)&&object(S.forex.accounts)?S.forex.accounts[id]:null;
    return {id,name:text(account.nome),type:text(account.tipo),login:text(account.platformLogin),
      broker:text(account.broker),currency:text(account.platformCurrency)||text(facts&&facts.currency),
      server:text(account.platformServer),platform:text(account.platform),
      liveIndex:index,archived:false};
  }
  function catalogDescriptor(account){
    return {id:text(account.id),name:text(account.name),type:text(account.type),login:text(account.login),
      broker:text(account.broker),currency:text(account.currency),server:text(account.server),
      liveIndex:null,archived:true};
  }
  function cleanAccount(account){
    return {id:account.id,name:account.name,type:account.type,login:account.login,
      broker:account.broker,currency:account.currency,server:account.server};
  }
  function stateIssue(){
    if(typeof api.validateState!=='function')return 'O modelo do Consolidado ainda não está disponível.';
    const validation=api.validateState(S.fxConsolidated);
    return validation.ok?'':(validation.errors||[]).join(' ')||'Consolidado incompatível. Preserve a base e confira a versão.';
  }
  function accounts(){
    const rows=[],used=new Set();
    const source=S.fxConsolidated;
    const historical=object(source)&&source.schemaVersion===1&&Array.isArray(source.accounts)
      ?source.accounts.filter(account=>object(account)&&text(account.id)):[];
    if(Array.isArray(S.accounts))S.accounts.forEach((account,index)=>{
      if(!object(account))return;
      const row=descriptor(account,index);
      // IDs duplicados são apresentados como ambíguos e recusados ao confirmar.
      const stored=historical.find(item=>item.id===row.id);
      if(stored){
        for(const key of ['name','type','login','broker','currency','server']){
          if(row[key]===null)row[key]=text(stored[key]);
        }
      }
      rows.push(row);used.add(row.id);
    });
    historical.forEach(account=>{
      if(!used.has(account.id)){rows.push(catalogDescriptor(account));used.add(account.id);}
    });
    const history=S.operationHistory;
    if(object(history)&&history.schemaVersion===DEFAULTS.operationHistory.schemaVersion&&Array.isArray(history.records)){
      history.records.forEach(record=>{
        if(!object(record))return;
        const ids=[record.accountId,record.recordContext&&record.recordContext.accountId,
          record.finalizationContext&&record.finalizationContext.accountId].map(text).filter(Boolean);
        if(new Set(ids).size!==1||used.has(ids[0]))return;
        rows.push(catalogDescriptor({id:ids[0],name:null}));used.add(ids[0]);
      });
    }
    return rows;
  }
  function accountSelected(id){
    const matches=accounts().filter(account=>account.id===id);
    return matches.length===1?matches[0]:null;
  }
  function guard(){
    if(jpWealthPersistenceOutcomeIsUnknown())return 'Gravação indeterminada. Confira a base antes de repetir.';
    if(jpWealthLoadRecoveryActive())return 'Base em recuperação. Nenhuma importação pode ser confirmada.';
    if(jpWealthPersistenceIsBlocked())return 'A sessão está encerrada ou a gravação está bloqueada.';
    const epoch=baseEpoch();
    if(typeof epoch!=='string'||!epoch)return 'Não foi possível verificar a geração da base. Confira a sessão antes de confirmar.';
    return stateIssue();
  }
  const baseEpoch=()=>typeof sessionEpochRead==='function'?sessionEpochRead():null;
  function capture(account){
    return {state:S,epoch:jpWealthPersistenceEpoch(),baseEpoch:baseEpoch(),generation,
      account:clone(account),accountFingerprint:JSON.stringify(account),
      accountObject:account&&account.liveIndex!==null?S.accounts[account.liveIndex]:null,
      consolidated:JSON.stringify(S.fxConsolidated)};
  }
  function stale(context){
    if(context.generation!==generation||context.state!==S||context.epoch!==jpWealthPersistenceEpoch()||
        context.baseEpoch!==baseEpoch())return 'A sessão mudou. Prepare uma nova prévia antes de confirmar.';
    if(context.consolidated!==JSON.stringify(S.fxConsolidated))return 'O Consolidado mudou. Prepare uma nova prévia.';
    if(context.account){
      const current=accountSelected(context.account.id);
      if(!current||JSON.stringify(current)!==context.accountFingerprint||
          context.accountObject&&S.accounts[current.liveIndex]!==context.accountObject)
        return 'A conta foi alterada ou ficou ambígua. Selecione a conta e prepare outra prévia.';
    }
    return '';
  }
  function cancelImport(){pending=null;registration=null;setup=null;generation+=1;}
  function unknown(reason){
    if(!jpWealthPersistenceOutcomeIsUnknown())markJPWealthPersistenceOutcomeUnknown(reason);
    hideStaleSavedTag();
    const banner=typeof persistenceAlertEl==='function'?persistenceAlertEl():null;
    if(banner&&banner.classList.contains('is-recovered')){
      clearTimeout(jpWealthPersistenceFailure.recoveryTimer);
      banner.className='persistence-alert';banner.textContent='';layoutPersistenceBanners();
    }
    return {ok:false,persistido:null,bloqueado:true,
      error:'Não foi possível confirmar a gravação. Preserve a entrada e confira a base; não repita a ação.'};
  }
  // Única escrita física: save(). O rollback cobre apenas os agregados do ato;
  // nenhum snapshot integral de S pode desfazer uma mudança de outro domínio.
  function commit(next,assignment,action,recordId){
    const issue=guard();if(issue)return fail(issue);
    let beforeRaw,before,logBefore,expected;
    const log=S.dataGovernance&&S.dataGovernance.changeLog;
    const account=assignment&&S.accounts[assignment.index];
    const accountHadId=account&&own(account,'forexAccountId');
    const previousId=account&&account.forexAccountId;
    try{
      beforeRaw=localStorage.getItem(LSKEY);
      before=clone(S.fxConsolidated);
      logBefore=Array.isArray(log)?clone(log):null;
    }catch(error){return fail('Não foi possível preparar uma gravação íntegra. Nada foi alterado.');}
    const restore=()=>{
      S.fxConsolidated=before;
      if(account){if(accountHadId)account.forexAccountId=previousId;else delete account.forexAccountId;}
      if(logBefore)S.dataGovernance.changeLog=logBefore;
    };
    try{
      S.fxConsolidated=next;
      if(account)account.forexAccountId=assignment.id;
      if(typeof dgLogChange==='function')dgLogChange('fxConsolidated',action,recordId||'',
        action==='imported'?'Importação confirmada do Consolidado FX':'Preferência de conta do Consolidado FX');
      expected=JSON.stringify(S,(key,value)=>key==='investorPassword'?'':value);
    }catch(error){restore();return fail('Não foi possível preparar os dados para gravação. Nada foi aplicado.');}
    let written;
    try{written=save();}
    catch(error){return unknown('Consolidado FX: exceção no escritor.');}
    if(written===false&&!jpWealthPersistenceOutcomeIsUnknown()){
      restore();hideStaleSavedTag();return fail('Gravação recusada. A prévia foi preservada para nova confirmação.');
    }
    try{
      const actual=localStorage.getItem(LSKEY);
      if(written===true&&actual===expected)return {ok:true,persistido:true};
      if(actual===beforeRaw&&!jpWealthPersistenceOutcomeIsUnknown()){
        restore();jpWealthAdoptPersistedRaw(beforeRaw);hideStaleSavedTag();
        setPersistenceFailureState(new Error('Consolidado FX não gravado.'),'storage');
        return fail('A gravação não foi efetivada. A prévia permanece disponível.');
      }
    }catch(error){return unknown('Consolidado FX: releitura indisponível.');}
    return unknown('Consolidado FX: releitura divergente ou retorno desconhecido.');
  }

  // Import eligibility reads the current registry, never the display catalogue's
  // historical fallback. Missing optional metadata stays unverified, not inferred.
  const identityFields=['login','broker','currency','server'];
  const identityText=value=>(text(value)||'').normalize('NFC').toLowerCase();
  const mt5=account=>platformFor(account.platform)?.key==='mt5';
  const liveAccounts=()=>Array.isArray(S.accounts)?S.accounts.map((a,i)=>object(a)?descriptor(a,i):null).filter(Boolean):[];
  const conflict=(a,b)=>identityFields.some(key=>text(a[key])&&text(b[key])&&identityText(a[key])!==identityText(b[key]));
  const sameIdentity=(a,b)=>!!text(a.login)&&identityText(a.login)===identityText(b.login)&&!conflict(a,b);
  const registryStamp=()=>JSON.stringify(liveAccounts());
  function inspectRegistration(report,selectionId){
    const errors=api.validateReport(report);
    if(errors.length)return {...fail('Documento recusado: '+errors.join(', ')),status:'invalid',matches:[]};
    const issue=guard();if(issue)return {...fail(issue),status:'blocked',matches:[]};
    const identity=report.identity,live=liveAccounts(),catalog=accounts();
    const selectedRows=live.filter(a=>a.id===selectionId),selected=selectedRows.length===1?selectedRows[0]:null;
    const historical=S.fxConsolidated.accounts.filter(a=>sameIdentity(a,identity));
    const matching=live.filter(a=>(!a.platform||mt5(a))&&sameIdentity(a,identity));
    const base={ok:false,persistido:false,matches:matching.map(a=>({id:a.id,name:a.name,login:a.login})),historicalIds:historical.map(a=>a.id)};
    if(selectedRows.length>1||matching.length>1)return {...base,status:'ambiguous',error:'Mais de um cadastro corresponde ao documento. Revise os identificadores em Contas; nenhum destino foi escolhido.'};
    if(matching.length===1&&matching[0].id!==selectionId)return {...base,status:'other',error:'O relatório corresponde a outra conta cadastrada. Selecione-a explicitamente para continuar.'};
    if(selected){
      const old=S.fxConsolidated.accounts.find(a=>a.id===selected.id);
      if(conflict(selected,identity)||(selected.platform&&!mt5(selected))||(old&&(conflict(old,identity)||conflict(old,selected))))
        return {...base,status:'mismatch',error:'A identificação diverge do cadastro ou do vínculo histórico. A conta selecionada não será sobrescrita.'};
      if(!selected.login||!selected.platform)return {...base,status:'incomplete',accountId:selected.id,error:'Complete login e plataforma no cadastro de Contas antes de importar.'};
      if(historical.some(a=>a.id!==selected.id))return {...base,status:'historical-link',error:'Este documento já possui outro vínculo histórico. Recadastre a identidade histórica; não crie um vínculo paralelo.'};
      return {...base,ok:true,status:'ready',accountId:selected.id};
    }
    const archived=catalog.find(a=>a.id===selectionId&&a.archived);
    if(archived&&conflict(archived,identity))return {...base,status:'mismatch',error:'O relatório não corresponde à conta histórica selecionada.'};
    if(historical.length>1)return {...base,status:'ambiguous',error:'O documento possui vínculos históricos ambíguos. Confira a origem antes de cadastrar.'};
    if(historical.length===1||archived)return {...base,status:'historical',accountId:historical[0]?.id||archived.id,error:'Conta apenas histórica. Recadastre-a explicitamente em Contas antes de importar.'};
    return {...base,status:'unregistered',error:'Não há conta correspondente cadastrada em Forex → Contas.'};
  }
  function beginRegistration(report=null,selectionId=null){
    const issue=guard();if(issue)return fail(issue);
    let mode='create',selected=null,identity={};
    if(report){
      const status=inspectRegistration(report,selectionId);
      if(['invalid','blocked','ambiguous','other','ready','historical-link'].includes(status.status))return {...status,ok:false};
      identity=report.identity;
      if(status.status==='incomplete'){selected=liveAccounts().find(a=>a.id===status.accountId);mode='complete';}
      else{
        const matches=accounts().filter(a=>a.archived&&sameIdentity(a,identity));
        if(matches.length>1)return fail('Vínculo histórico ambíguo. Confira os cadastros.');
        selected=matches[0]||null;
        if(!selected&&status.status==='historical')selected=accounts().find(a=>a.id===status.accountId);
        if(selected)mode='reregister';
      }
    }else if(selectionId){
      selected=accountSelected(selectionId);if(!selected)return fail('Cadastro indisponível ou ambíguo.');
      // Explicit entry from Accounts may complete an existing or archived record.
      if(selected.liveIndex!==null)selected=descriptor(S.accounts[selected.liveIndex],selected.liveIndex);
      mode=selected.archived?'reregister':'complete';
    }
    const draft={name:selected?.name||'',type:selected?.type||'SATÉLITE',
      platform:selected?.platform||(report?'MetaTrader 5':''),login:selected?.login||text(identity.login)||'',
      broker:selected?.broker||text(identity.broker)||'',currency:selected?.currency||text(identity.currency)||'',
      server:selected?.server||text(identity.server)||''};
    const token=crypto.randomUUID();
    registration={token,mode,selected:clone(selected),report:report?clone(report):null,context:capture(null),stamp:registryStamp()};
    return {ok:true,persistido:false,token,mode,draft,accountId:selected?.id||null};
  }
  function cancelRegistration(){registration=null;}
  function registrationInput(input,attempt){
    if(!object(input))return fail('Revise a ficha de cadastro.');
    const next={};
    for(const key of ['name','type','platform','login','broker','currency','server']){
      if(input[key]!=null&&typeof input[key]!=='string')return fail('Campo inválido: '+key);
      next[key]=text(input[key])||'';
      if(next[key].length>160||/[\u0000-\u001f\u007f]/.test(next[key]))return fail('Campo inválido ou muito longo: '+key);
    }
    if(!next.name||!next.login||!next.platform||!['MESTRE','PRÓPRIA','SATÉLITE'].includes(next.type))return fail('Informe nome, tipo, plataforma e número/login da conta.');
    next.platform=normalizePlatformName(next.platform);
    if(next.currency&&!/^[A-Z]{3}$/.test(next.currency))return fail('Use o código de moeda com três letras maiúsculas, ou deixe sem informação.');
    if(attempt.report&&(!mt5(next)||!sameIdentity(next,attempt.report.identity)))return fail('Os identificadores da ficha precisam corresponder ao documento MT5.');
    const old=attempt.selected;
    if(old&&(identityFields.some(key=>text(old[key])&&!text(next[key]))||conflict(old,next)||(old.platform&&platformNorm(normalizePlatformName(old.platform))!==platformNorm(next.platform))))return fail('Um identificador existente diverge. Esta ficha completa lacunas; não substitui vínculos.');
    const live=liveAccounts();
    if(live.some(a=>a.id!==old?.id&&(!a.platform||platformNorm(normalizePlatformName(a.platform))===platformNorm(next.platform))&&sameIdentity(a,next)))return fail('Já existe cadastro correspondente. Selecione-o; não será criada uma duplicata.');
    if(old&&live.filter(a=>a.id===old.id).length>(attempt.mode==='complete'?1:0))return fail('A identidade já está cadastrada ou ficou ambígua.');
    const history=S.fxConsolidated.accounts.filter(a=>sameIdentity(a,next));
    if(mt5(next)&&history.some(a=>a.id!==old?.id))return fail('Há vínculo histórico correspondente. Use Recadastrar conta para preservá-lo.');
    return {ok:true,next};
  }
  async function saveRegistration(token,input,options={}){
    if(jpWealthPersistenceOutcomeIsUnknown())return unknown('Cadastro já bloqueado por desfecho desconhecido.');
    if(busy)return fail('Uma confirmação está em andamento.');
    const attempt=registration;
    if(!attempt||attempt.token!==token)return fail('A ficha foi encerrada. Abra o cadastro novamente.');
    const checked=registrationInput(input,attempt);if(!checked.ok)return checked;
    if(attempt.mode==='reregister'&&options.confirmHistorical!==true)return fail('Confirme a reutilização da identidade e do histórico.');
    busy=true;
    try{
      return await sessionAcquireWriteLock(()=>{
        const issue=guard()||stale(attempt.context);
        if(issue)return jpWealthPersistenceOutcomeIsUnknown()?unknown(issue):fail(issue);
        if(registration!==attempt||attempt.stamp!==registryStamp())return fail('O cadastro mudou ou a ficha foi cancelada. Reabra a ficha para revisar a versão atual.');
        const verified=registrationInput(checked.next,attempt);if(!verified.ok)return verified;
        const values=verified.next,accountId=attempt.selected?.id&&!attempt.selected.id.startsWith('live:')?attempt.selected.id:'fxaccount_'+crypto.randomUUID();
        const before={accounts:clone(S.accounts),forex:clone(S.forex),log:clone(S.dataGovernance.changeLog)};
        let rawBefore;try{rawBefore=localStorage.getItem(LSKEY);}catch(error){return fail('Não foi possível ler a base antes da gravação.');}
        const result=JPWForex.state.mutate('account-registration','Cadastro explícito de conta: '+attempt.mode,['accounts'],()=>{
          let account;
          if(attempt.mode==='complete')account=S.accounts[attempt.selected.liveIndex];
          else{account={investorPassword:'',perfil:'',perfilLocked:false,sini:0,satu:0};S.accounts.push(account);}
          Object.assign(account,{forexAccountId:accountId,nome:values.name,tipo:values.type,platform:values.platform,
            platformLogin:values.login,broker:values.broker,platformCurrency:values.currency,platformServer:values.server});
        });
        if(jpWealthPersistenceOutcomeIsUnknown()||result.persistido===null)return unknown('Cadastro de conta: resultado indeterminado.');
        if(!result.ok){hideStaleSavedTag();return result;}
        // The cadastral command retains the canonical writer; verify its durable
        // acknowledgement without replacing save() or other domains' state.
        try{
          const raw=localStorage.getItem(LSKEY),expected=JSON.stringify(S,(key,value)=>key==='investorPassword'?'':value);
          if(raw!==expected){
            if(raw!==rawBefore)return unknown('Cadastro de conta: releitura divergente.');
            S.accounts=before.accounts;S.forex=before.forex;S.dataGovernance.changeLog=before.log;
            jpWealthAdoptPersistedRaw(rawBefore);hideStaleSavedTag();
            setPersistenceFailureState(new Error('Cadastro não gravado.'),'storage');return fail('O cadastro não foi gravado. A ficha permanece disponível.');
          }
        }catch(error){return unknown('Cadastro de conta: releitura indisponível.');}
        registration=null;pending=null;
        return {ok:true,persistido:true,accountId,mode:attempt.mode};
      });
    }catch(error){return jpWealthPersistenceOutcomeIsUnknown()?unknown('Cadastro interrompido.'):fail('Cadastro não confirmado. Confira a sessão.');}
    finally{busy=false;}
  }

  // Preparation is intentionally separate from analytics import. Each confirmed
  // step has one canonical write and its own durable acknowledgement.
  function beginAccountSetup(accountId,report=null){
    const issue=guard();if(issue)return fail(issue);
    const account=accountSelected(accountId);
    if(!account||account.archived||account.id.startsWith('live:'))return fail('Complete o cadastro da conta antes de preparar o período.');
    if(report){const identified=inspectRegistration(report,accountId);if(!identified.ok)return identified;}
    const accountPeriods=S.forex?.accountContexts?.accounts?.[accountId];
    const periods=Object.values(accountPeriods?.periods||{}).map(p=>({periodId:p.periodId,startedAt:p.startedAt,currency:p.currency,si:p.si,openingBook:p.openingBook,source:p.source}));
    const token=crypto.randomUUID();
    const suggestions=report?{balance:typeof report.summary.balance==='number'?report.summary.balance:null,
      equity:typeof report.summary.equity==='number'?report.summary.equity:null,
      date:report.generatedAt||report.period.to||null,from:report.period.from||null,to:report.period.to||null,
      source:'Relatório MT5 · '+report.format+' · '+(report.period.from||'?')+' → '+(report.period.to||'?')}:null;
    setup={token,context:capture(account),forexFingerprint:JSON.stringify(S.forex),stage:'period',report:report?clone(report):null,periodId:null};
    return {ok:true,persistido:false,token,account:cleanAccount(account),periods,currentPeriodId:accountPeriods?.currentPeriodId||null,suggestions};
  }
  function cancelAccountSetup(){setup=null;}
  function setupIssue(attempt){
    const issue=guard()||stale(attempt.context);if(issue)return issue;
    if(attempt!==setup)return 'A preparação foi encerrada. Abra a ficha novamente.';
    if(attempt.forexFingerprint!==JSON.stringify(S.forex))return 'O contexto Forex mudou. Reabra a preparação para revisar a versão atual.';
    if(attempt.report){const status=inspectRegistration(attempt.report,attempt.context.account.id);if(!status.ok)return status.error;}
    return '';
  }
  function confirmedSetupCommand(command,keys){
    const before={},logBefore=clone(S.dataGovernance.changeLog);let rawBefore;
    try{rawBefore=localStorage.getItem(LSKEY);for(const key of keys)before[key]=clone(S[key]);}
    catch(error){return fail('Não foi possível preparar uma gravação íntegra. Nada foi alterado.');}
    const result=command();
    if(jpWealthPersistenceOutcomeIsUnknown()||result.persistido===null)return unknown('Preparação da conta: gravação indeterminada.');
    if(!result.ok){hideStaleSavedTag();return result;}
    try{
      const actual=localStorage.getItem(LSKEY),expected=JSON.stringify(S,(key,value)=>key==='investorPassword'?'':value);
      if(actual===expected)return result;
      if(actual!==rawBefore)return unknown('Preparação da conta: releitura divergente.');
      for(const key of keys)S[key]=before[key];S.dataGovernance.changeLog=logBefore;
      jpWealthAdoptPersistedRaw(rawBefore);hideStaleSavedTag();
      setPersistenceFailureState(new Error('Preparação da conta não gravada.'),'storage');
      return fail('A gravação não foi efetivada. Os campos continuam disponíveis para revisão.');
    }catch(error){return unknown('Preparação da conta: releitura indisponível.');}
  }
  async function saveSetupPeriod(token,input){
    if(busy)return fail('Uma confirmação está em andamento.');
    const attempt=setup;
    if(!attempt||attempt.token!==token||attempt.stage!=='period')return fail('Reabra a preparação do período.');
    if(!object(input)||input.confirmPeriod!==true)return fail('Confirme explicitamente a conta e o período.');
    busy=true;
    try{return await sessionAcquireWriteLock(()=>{
      const issue=setupIssue(attempt);if(issue)return jpWealthPersistenceOutcomeIsUnknown()?unknown(issue):fail(issue);
      const accountId=attempt.context.account.id;
      let periodId=text(input.periodId),result={ok:true,persistido:false};
      if(periodId){
        if(!S.forex?.accountContexts?.accounts?.[accountId]?.periods?.[periodId])return fail('O período selecionado não pertence à conta.');
      }else{
        const oldIds=new Set(Object.keys(S.forex?.accountContexts?.accounts?.[accountId]?.periods||{}));
        result=confirmedSetupCommand(()=>JPWForex.state.recordAccountPeriod({accountId,
          startedAt:input.startedAt,currency:input.currency,si:input.si,openingBook:input.openingBook,
          source:input.source,activateCurrentPeriod:input.activateCurrentPeriod===true},
          {reason:input.reason,expectedEpoch:attempt.context.epoch}),['forex']);
        if(!result.ok)return result;
        periodId=Object.keys(S.forex.accountContexts.accounts[accountId].periods).find(id=>!oldIds.has(id));
        if(!periodId)return unknown('Preparação da conta: período gravado sem identidade confirmável.');
      }
      attempt.stage='observation';attempt.periodId=periodId;
      attempt.context=capture(accountSelected(accountId));attempt.forexFingerprint=JSON.stringify(S.forex);
      return {...result,accountId,periodId,period:clone(S.forex.accountContexts.accounts[accountId].periods[periodId])};
    });}catch(error){return jpWealthPersistenceOutcomeIsUnknown()?unknown('Preparação interrompida.'):fail('Preparação não confirmada. Confira a sessão.');}
    finally{busy=false;}
  }
  async function saveSetupObservation(token,input){
    if(busy)return fail('Uma confirmação está em andamento.');
    const attempt=setup;
    if(!attempt||attempt.token!==token||attempt.stage!=='observation')return fail('Selecione ou registre o período antes da observação.');
    if(!object(input)||input.confirmObservation!==true)return fail('Confirme os valores, a fonte e o instante da observação.');
    busy=true;
    try{return await sessionAcquireWriteLock(()=>{
      const issue=setupIssue(attempt);if(issue)return jpWealthPersistenceOutcomeIsUnknown()?unknown(issue):fail(issue);
      const accountId=attempt.context.account.id,period=JPWForex.state.accountContext({accountId,periodId:attempt.periodId}).value;
      if(!period||typeof period.si!=='number'||period.si<=0)return fail('Este período não possui SI confirmado. Registre um período com SI antes da observação financeira.');
      const observed=Date.parse(input.observedAt);
      if(!Number.isFinite(observed)||observed>Date.now()||String(input.observedAt).slice(0,10)<period.startedAt)
        return fail('Informe o instante real da observação, dentro do período e sem data futura.');
      const selected=accountSelected(accountId);
      const result=confirmedSetupCommand(()=>JPWForex.state.recordAccountFacts({accountIndex:selected.liveIndex,
        periodId:period.periodId,si:period.si,currency:period.currency,equity:input.equity,
        usdToAccountRate:input.usdToAccountRate,netCashflow:input.netCashflow,
        cashflowAdjustmentRecorded:input.cashflowAdjustmentRecorded===true,
        observedAt:input.observedAt,source:input.source}, {reason:input.reason}),['forex','accounts','activeOperation']);
      if(!result.ok){
        // The canonical refusal rollback restores accounts from a clone. Keep
        // this still-valid draft usable without accepting any changed facts.
        const current=accountSelected(accountId);
        if(result.persistido===false&&current&&JSON.stringify(current)===attempt.context.accountFingerprint&&
          JSON.stringify(S.forex)===attempt.forexFingerprint)
          attempt.context.accountObject=S.accounts[current.liveIndex];
        return result;
      }
      attempt.stage='complete';attempt.context=capture(accountSelected(accountId));attempt.forexFingerprint=JSON.stringify(S.forex);
      return {...result,accountId,periodId:period.periodId};
    });}catch(error){return jpWealthPersistenceOutcomeIsUnknown()?unknown('Observação interrompida.'):fail('Observação não confirmada. Confira a sessão.');}
    finally{busy=false;}
  }

  function prepareImport(report,selectionId,meta={}){
    cancelImport();
    const issue=guard();if(issue)return fail(issue);
    const registrationStatus=inspectRegistration(report,selectionId);
    if(!registrationStatus.ok)return registrationStatus;
    const selected=accountSelected(selectionId);
    try{
      if(!object(meta)||typeof meta.fileHash!=='string'||!/^[a-f0-9]{64}$/i.test(meta.fileHash)||
          typeof meta.fileName!=='string'||!meta.fileName.trim()||meta.fileName.length>255||
          /[\u0000-\u001f\u007f]/.test(meta.fileName))
        return fail('O arquivo precisa de nome válido e identificação SHA-256 antes da prévia.');
      const safeMeta={fileHash:meta.fileHash.toLowerCase(),
        fileName:text(meta.fileName)?meta.fileName.split(/[\\/]/).pop():null,
        importedAt:text(meta.importedAt)||new Date().toISOString()};
      if(!Number.isFinite(Date.parse(safeMeta.importedAt)))return fail('O instante da importação é inválido.');
      const preview=api.previewImport(S.fxConsolidated,cleanAccount(selected),clone(report),safeMeta);
      if(!preview.ok)return {...preview,persistido:false};
      const token=crypto.randomUUID();
      pending={token,context:capture(selected),preview:clone(preview)};
      return {...clone(preview),token,persistido:false};
    }catch(error){return fail('Não foi possível preparar o relatório. Verifique o formato e a identidade da conta.');}
  }
  function identifiedAccount(selected){
    const account=cleanAccount(selected);
    let assignment=null;
    if(selected.liveIndex!==null&&!text(S.accounts[selected.liveIndex].forexAccountId)){
      account.id='fxaccount_'+crypto.randomUUID();
      assignment={index:selected.liveIndex,id:account.id};
    }
    return {account,assignment};
  }
  async function confirmImport(preview,options={}){
    if(busy)return fail('Uma confirmação está em andamento. Aguarde o resultado.');
    if(!pending||!preview||preview.token!==pending.token)return fail('Esta prévia não está mais disponível. Prepare a importação novamente.');
    const attempt=pending;
    busy=true;
    try{
      return await sessionAcquireWriteLock(()=>{
        const issue=guard()||stale(attempt.context);
        if(issue)return jpWealthPersistenceOutcomeIsUnknown()?unknown('Consolidado FX já bloqueado por desfecho desconhecido.'):fail(issue);
        if(pending!==attempt)return fail('A importação foi cancelada.');
        const status=inspectRegistration(attempt.preview.report,attempt.context.account.id);
        if(!status.ok)return status;
        const selected=accountSelected(attempt.context.account.id);
        const {account,assignment}=identifiedAccount(selected);
        const currentPreview=api.previewImport(S.fxConsolidated,account,attempt.preview.report,attempt.preview.meta);
        if(!currentPreview.ok)return {...currentPreview,persistido:false};
        const applied=api.applyImport(S.fxConsolidated,currentPreview,
          {acceptRevision:options.acceptRevision===true,confirmIdentity:options.confirmIdentity===true});
        if(!applied.ok)return {...applied,persistido:false};
        if(JSON.stringify(applied.state)===JSON.stringify(S.fxConsolidated)&&!assignment){
          pending=null;return {ok:true,persistido:false,unchanged:true,duplicate:true,accountId:account.id,receipt:applied.receipt||null};
        }
        const result=commit(applied.state,assignment,'imported',applied.receipt&&applied.receipt.id);
        if(result.ok){pending=null;return {...result,accountId:account.id,receipt:applied.receipt||null};}
        return result;
      });
    }catch(error){
      return jpWealthPersistenceOutcomeIsUnknown()?unknown('Consolidado FX: confirmação interrompida.'):
        fail('A confirmação foi interrompida antes de concluir. Preserve a prévia e confira a sessão.');
    }finally{busy=false;}
  }
  async function saveDefaultAccount(id){
    if(busy)return fail('Uma confirmação está em andamento. Aguarde o resultado.');
    const issue=guard();if(issue)return jpWealthPersistenceOutcomeIsUnknown()?unknown(issue):fail(issue);
    const selected=id===null?null:accountSelected(id);
    if(id!==null&&!selected)return fail('Selecione uma conta existente e sem identidade ambígua.');
    const context=capture(selected);
    busy=true;
    try{
      return await sessionAcquireWriteLock(()=>{
        const issue=guard()||stale(context);if(issue)return jpWealthPersistenceOutcomeIsUnknown()?unknown(issue):fail(issue);
        const next=clone(S.fxConsolidated);
        let assignment=null,account=null;
        if(selected){
          ({account,assignment}=identifiedAccount(accountSelected(id)));
          if(!next.accounts.some(item=>item.id===account.id))next.accounts.push({...account,orders:[],deals:[],positions:[],summaries:[]});
        }
        const newId=account?account.id:null;
        if(next.defaultAccountId===newId&&!assignment)return {ok:true,persistido:false,unchanged:true,accountId:newId};
        next.defaultAccountId=newId;
        const result=commit(next,assignment,'default-account',newId);
        if(result.ok){cancelImport();return {...result,accountId:newId};}
        return result;
      });
    }catch(error){return fail('Não foi possível confirmar a conta padrão. Confira a sessão e tente novamente.');}
    finally{busy=false;}
  }
  Object.assign(api,{beginAccountSetup,cancelAccountSetup,saveSetupPeriod,saveSetupObservation,accounts,inspectRegistration,beginRegistration,saveRegistration,cancelRegistration,prepareImport,confirmImport,saveDefaultAccount,cancelImport});
})(globalThis);

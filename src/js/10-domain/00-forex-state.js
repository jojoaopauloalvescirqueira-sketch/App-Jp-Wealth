// FOREX V11 — observations and explicit commands. Pure mathematics lives in .engine.
// There is no migration or write during read/render. The document writer retains
// its epoch, lock, revision, recovery and unknown-outcome protocol.
(function(root){
  'use strict';
  const fx=root.JPWForex;
  const clone=value=>structuredClone(value);
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const text=value=>typeof value==='string'?value.trim():'';
  const id=prefix=>prefix+'_'+crypto.randomUUID();
  const now=()=>new Date().toISOString();
  const empty=()=>({schemaVersion:1,policyVersion:fx.policy.policyVersion||fx.policy.version,
    activeAccountId:null,accounts:{},market:null,h4Closes:[],grid:null,
    reserves:null,proposals:[],auditLog:[],migration:null,
    accountContexts:{schemaVersion:1,revision:0,accounts:{},archivedAccounts:{},legacy:null}});
  const raw=()=>S.forex;
  const object=value=>!!value&&typeof value==='object'&&!Array.isArray(value);
  const positive=value=>finite(value)&&value>0;
  const instant=value=>!!text(value)&&Number.isFinite(Date.parse(value));
  const instrumentKey=value=>text(value).toUpperCase().replace(/[^A-Z0-9]/g,'');
  const civilDate=value=>typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&
    Number.isFinite(Date.parse(value+'T00:00:00Z'))&&new Date(value+'T00:00:00Z').toISOString().slice(0,10)===value;
  const componentKeys=['price','contract','conversion','atr'];
  function componentShape(key,value){
    if(!object(value)||!text(value.source)||!instant(value.observedAt)||value.sourceKind!=='MANUAL')return false;
    if(key==='price')return positive(value.value);
    if(key==='contract')return positive(value.contractSize)&&
      ['minimumVolume','volumeStep'].every(k=>value[k]===undefined||positive(value[k]));
    if(key==='conversion')return positive(value.quoteToAccountRate)&&positive(value.baseToAccountRate);
    return key==='atr'&&finite(value.short)&&value.short>=0&&positive(value.long)&&value.timeframe==='H4'&&value.unit==='PRICE';
  }
  function instrumentRecordShape(record){
    const seen=new Set();let current=record,lastRevision=null;
    while(current!=null){
      if(!object(current)||seen.has(current)||!text(current.id)||!text(current.accountId)||!text(current.periodId)||
        typeof current.currency!=='string'||!/^[A-Z]{3}$/.test(current.currency)||
        !instrumentKey(current.instrumentId)||current.instrumentId!==instrumentKey(current.instrumentId)||
        !Number.isInteger(current.revision)||current.revision<1||!instant(current.recordedAt)||
        (lastRevision!==null&&current.revision!==lastRevision-1)||
        (current!==record&&(current.id!==record.id||current.accountId!==record.accountId||current.periodId!==record.periodId||current.instrumentId!==record.instrumentId||current.currency!==record.currency))||
        !componentKeys.some(k=>current[k]!==undefined)||!componentKeys.every(k=>current[k]===undefined||componentShape(k,current[k])))return false;
      seen.add(current);lastRevision=current.revision;current=current.previous;
    }
    return lastRevision===1;
  }
  function instrumentContextsShape(value){
    if(!object(value)||value.schemaVersion!==1||!Array.isArray(value.records)||!value.records.every(instrumentRecordShape))return false;
    const scopes=value.records.map(r=>JSON.stringify([r.accountId,r.periodId,r.instrumentId]));
    return new Set(scopes).size===scopes.length;
  }
  const dailyQuoteShape=(quote,key)=>object(quote)&&/^[A-Z]{3}$/.test(quote.base)&&/^[A-Z]{3}$/.test(quote.quote)&&
    quote.base!==quote.quote&&quote.base+quote.quote===key&&positive(quote.rate)&&civilDate(quote.referenceDate)&&
    instant(quote.fetchedAt)&&quote.referenceDate<=new Date(quote.fetchedAt).toISOString().slice(0,10)&&
    quote.source==='Frankfurter'&&quote.sourceKind==='DAILY_REFERENCE';
  const dailyReferencesShape=value=>object(value)&&value.schemaVersion===1&&Number.isInteger(value.revision)&&value.revision>=0&&
    object(value.quotes)&&Object.entries(value.quotes).every(([key,q])=>dailyQuoteShape(q,key));
  const budgetShape=b=>object(b)&&b.schemaVersion===1&&text(b.id)&&text(b.accountId)&&text(b.periodId)&&text(b.currency)&&
    (b.operationId===null||!!text(b.operationId))&&Array.isArray(b.versions)&&b.versions.length>0&&
    b.versions.every((v,i)=>object(v)&&v.version===i+1&&finite(v.amount)&&v.amount>=0&&(i===0||v.amount<=b.versions[i-1].amount)&&text(v.source)&&text(v.declaredBy)&&
      Number.isFinite(Date.parse(v.declaredAt))&&Number.isFinite(Date.parse(v.recordedAt))&&object(v.policySnapshot))&&
    (b.association==null||object(b.association));
  const contextPeriodShape=p=>object(p)&&text(p.periodId)&&text(p.accountId)&&
    /^[A-Z]{3}$/.test(p.currency)&&civilDate(p.startedAt)&&
    (p.si===null||positive(p.si))&&(p.openingBook===null||finite(p.openingBook))&&
    Array.isArray(p.phases)&&p.phases.every(ph=>object(ph)&&Array.isArray(ph.orders)&&ph.orders.every(o=>
      object(o)&&(!text(o.accountId)||o.accountId===p.accountId)&&
      (!text(o.periodId)||o.periodId===p.periodId)&&(!text(o.currency)||o.currency===p.currency)&&
      (o.recordStatus!=='recorded'||o.accountId===p.accountId&&o.periodId===p.periodId&&
        o.currency===p.currency&&text(o.operationId))))&&
    Array.isArray(p.ledgerEvents)&&Array.isArray(p.ledger)&&p.ledger.every(r=>object(r)&&r.accountId===p.accountId&&
      r.periodId===p.periodId&&r.currency===p.currency&&civilDate(r.data)&&finite(r.resultado)&&finite(r.saldo))&&
    (p.activeOperation===null||object(p.activeOperation)&&text(p.activeOperation.operationId)&&
      p.activeOperation.recordContext?.accountId===p.accountId&&
      p.activeOperation.recordContext?.periodId===p.periodId)&&
    (p.grid===undefined||p.grid===null||object(p.grid)&&text(p.grid.operationId)&&
      Number.isInteger(p.grid.declaredPhase)&&p.grid.declaredPhase>=1&&p.grid.declaredPhase<=6)&&
    (p.reserves===undefined||p.reserves===null||object(p.reserves)&&p.reserves.accountId===p.accountId&&
      p.reserves.periodId===p.periodId&&p.reserves.currency===p.currency)&&
    Number.isInteger(p.revision)&&p.revision>=1;
  function accountContextsShape(v){
    if(!object(v)||v.schemaVersion!==1||!Number.isInteger(v.revision)||v.revision<0||!object(v.accounts)||
      (v.archivedAccounts!==undefined&&!object(v.archivedAccounts))||
      (v.legacy!==null&&v.legacy!==undefined&&!object(v.legacy))||
      (v.legacy?.associations!==undefined&&(!Array.isArray(v.legacy.associations)||
        !v.legacy.associations.every(link=>object(link)&&['ORDER','LEDGER','OPERATION'].includes(link.kind)&&
          text(link.path)&&['PROVEN','UNRECONCILED'].includes(link.status)&&
          (link.status!=='PROVEN'||v.accounts?.[link.accountId]?.periods?.[link.periodId]?.currency===link.currency))))
      )return false;
    return Object.entries(v.accounts).every(([key,a])=>object(a)&&a.accountId===key&&
      object(a.periods)&&Object.values(a.periods).filter(p=>p?.activeOperation).length<=1&&
      Object.entries(a.periods).every(([pid,p])=>p.periodId===pid&&p.accountId===key&&contextPeriodShape(p))&&
      (a.currentPeriodId===null||text(a.currentPeriodId)&&!!a.periods[a.currentPeriodId]));
  }
  const supported=(value=raw())=>value==null||(object(value)&&value.schemaVersion===1&&
    value.policyVersion===(fx.policy.policyVersion||fx.policy.version)&&
    object(value.accounts)&&Object.values(value.accounts).every(object)&&
    Array.isArray(value.h4Closes)&&value.h4Closes.every(object)&&
    Array.isArray(value.auditLog)&&value.auditLog.every(object)&&
    Array.isArray(value.proposals)&&value.proposals.every(object)&&
    (value.operationBudgets===undefined||(Array.isArray(value.operationBudgets)&&value.operationBudgets.every(budgetShape)))&&
    (value.instrumentContexts===undefined||instrumentContextsShape(value.instrumentContexts))&&
    (value.dailyReferences===undefined||dailyReferencesShape(value.dailyReferences))&&
    (value.accountContexts===undefined||accountContextsShape(value.accountContexts))&&
    ['market','grid','reserves','migration'].every(key=>value[key]==null||object(value[key])));
  const unavailable=(code,message)=>({status:'NOT_COMPUTABLE',value:null,findings:[{code,message}]});
  function unavailableContext(code,message,requested){
    return {...unavailable(code,message),policyVersion:null,statuteVersion:null,parametricAnnexVersion:null,
      effectiveDate:null,accountId:null,periodId:null,observedAt:null,provenance:'UNRESOLVED',
      requested:requested?clone(requested):null,accountInputs:null,marketInputs:null,
      sourcePolicyVersion:raw()&&typeof raw().policyVersion==='string'?raw().policyVersion:null,
      policySnapshot:{policyVersion:null,status:'NOT_COMPUTABLE',source:code}};
  }
  function recordContext(target){
    // Supplying a target is an explicit historical/account lookup. Missing keys
    // never fall back to whichever account happens to be selected in the UI.
    const explicit=arguments.length>0, f=raw();
    if(!supported())return unavailableContext('FOREX_SCHEMA_UNSUPPORTED','Contexto Forex incompatível; sem atribuição da política atual.',target);
    if(explicit&&(!object(target)||!text(target.accountId)||!text(target.periodId)))
      return unavailableContext('CONTEXT_IDENTITY_MISSING','Identifique conta e período do fato; contexto selecionado não os substitui.',target);
    const key=explicit?target.accountId:f&&f.activeAccountId;
    let a=f&&f.accounts&&f.accounts[key]||null;
    if(explicit){
      const seen=new Set();
      while(object(a)&&!seen.has(a)&&a.periodId!==target.periodId){seen.add(a);a=a.previous;}
      if(!object(a)||a.periodId!==target.periodId)return unavailableContext('CONTEXT_NOT_FOUND','A observação da conta/período solicitado não está disponível.',target);
    }
    // The old global ATR has no instrument identity. Keep it in the document,
    // but never assign it to a selected account or instrument during a read.
    let market=null;
    if(explicit&&a&&text(target.instrumentId)){
      const observation=instrumentContext(target).value;
      if(observation&&observation.atr)market={...clone(observation.atr),atrShort:observation.atr.short,atrLong:observation.atr.long,
        accountId:key,periodId:a.periodId,instrumentId:observation.instrumentId,observationId:observation.id,revision:observation.revision};
    }
    return {status:a?'OK':'NOT_COMPUTABLE',policyVersion:fx.policy.policyVersion||fx.policy.version,
      statuteVersion:fx.policy.statuteVersion,parametricAnnexVersion:fx.policy.parametricAnnexVersion,
      effectiveDate:fx.policy.effectiveDate,accountId:a?key:null,
      periodId:a&&a.periodId||null,observedAt:a&&a.observedAt||null,
      provenance:a?'RECORDED':'LEGACY_UNRESOLVED',
      accountInputs:a?clone(a):null,marketInputs:market?clone(market):null,
      policySnapshot:fx.policy.snapshot()};
  }
  function mutate(action,reason,keys,fn){
    if(!text(reason))return {ok:false,persistido:false,error:'Informe o motivo do registro.'};
    if(!supported())return {ok:false,persistido:false,error:'Agregado Forex incompatível. Preserve a base e revise a versão.'};
    if(jpWealthPersistenceOutcomeIsUnknown())return {ok:false,persistido:null,error:'Gravação indeterminada. Confira a base antes de repetir.'};
    const fields=[...new Set(['forex',...keys])]; const before={};
    for(const key of fields)before[key]={exists:Object.prototype.hasOwnProperty.call(S,key),value:clone(S[key])};
    const log=S.dataGovernance&&S.dataGovernance.changeLog;
    const logBefore=Array.isArray(log)?clone(log):null;
    function restore(){
      for(const key of fields){if(before[key].exists)S[key]=before[key].value;else delete S[key];}
      if(logBefore)S.dataGovernance.changeLog=logBefore;
    }
    try{
      if(!S.forex)S.forex=empty();
      fn(S.forex);
      S.forex.auditLog.push({id:id('fxaudit'),timestamp:now(),action,reason:text(reason),
        policyVersion:fx.policy.policyVersion||fx.policy.version,
        previous:before.forex.value?{activeAccountId:before.forex.value.activeAccountId}:null});
      if(typeof dgLogChange==='function')dgLogChange('forex',action,S.forex.activeAccountId||'',text(reason));
    }catch(error){restore();return {ok:false,persistido:false,error:error.message};}
    let written;
    try{written=save();}
    catch(error){markJPWealthPersistenceOutcomeUnknown('registro Forex');return {ok:false,persistido:null,error:'Gravação indeterminada. Não repita antes de conferir a base.'};}
    if(written===false){restore();return {ok:false,persistido:false,error:'Gravação recusada. O registro não foi confirmado; mantenha a entrada para tentar novamente.'};}
    if(written!==true){markJPWealthPersistenceOutcomeUnknown('retorno do registro Forex');return {ok:false,persistido:null,error:'Resultado de gravação desconhecido. Não repetir.'};}
    return {ok:true,persistido:true};
  }
  // Contexto operacional versionado. Seleção é estado efêmero; nenhum dado de
  // uma conta é copiado para S.phases, S.ledger ou S.activeOperation ao navegar.
  let operationalAccountId=null,operationalPeriodId=null;
  const contextEnvelope=f=>f?.accountContexts||{schemaVersion:1,revision:0,accounts:{},archivedAccounts:{},legacy:null};
  function registeredAccount(accountId){
    const matches=(S.accounts||[]).filter(a=>a&&a.forexAccountId===accountId);
    return matches.length===1?matches[0]:null;
  }
  function defaultOperationalAccount(){
    const masters=(S.accounts||[]).filter(a=>a&&a.tipo==='MESTRE'&&text(a.forexAccountId));
    return masters.length===1?masters[0].forexAccountId:null;
  }
  function operationalSelection(){
    const explicit=operationalAccountId&&registeredAccount(operationalAccountId)?operationalAccountId:null;
    const accountId=explicit||defaultOperationalAccount();
    const a=accountId?contextEnvelope(raw()).accounts[accountId]:null;
    const periodId=operationalPeriodId&&a?.periods?.[operationalPeriodId]?operationalPeriodId:a?.currentPeriodId||null;
    return {accountId,periodId,reason:explicit?'EXPLICIT':accountId?'UNIQUE_MASTER':'SELECTION_REQUIRED',
      requiresSelection:!accountId,accounts:(S.accounts||[]).filter(x=>text(x?.forexAccountId)).map(x=>({accountId:x.forexAccountId,
        name:x.nome||x.forexAccountId,type:x.tipo||null,currency:x.platformCurrency||null}))};
  }
  function selectOperationalAccount(accountId){
    if(!registeredAccount(accountId))return {ok:false,error:'Selecione uma conta atualmente cadastrada em Contas.'};
    operationalAccountId=accountId;operationalPeriodId=null;return {ok:true,selection:operationalSelection()};
  }
  function archiveRegisteredAccount(accountId,{reason='',expectedEpoch}={}){
    return mutate('registered-account-archived',reason,['accounts'],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; revise a conta antes de arquivar.');
      const index=(S.accounts||[]).findIndex(a=>a?.forexAccountId===accountId);
      if(index<0||!registeredAccount(accountId))throw new Error('Conta não cadastrada ou identidade ambígua.');
      const e=f.accountContexts||{schemaVersion:1,revision:0,accounts:{},archivedAccounts:{},legacy:null};
      if(Object.values(e.accounts?.[accountId]?.periods||{}).some(p=>p?.activeOperation))
        throw new Error('Finalize a operação em andamento desta conta antes de arquivar o cadastro.');
      if(e.archivedAccounts?.[accountId])throw new Error('Conta já arquivada.');
      e.archivedAccounts=e.archivedAccounts||{};
      const archived=clone(S.accounts[index]);archived.investorPassword='';
      e.archivedAccounts[accountId]={record:archived,archivedAt:now(),reason:text(reason)};
      S.accounts.splice(index,1);e.revision++;f.accountContexts=e;
    });
  }
  function selectOperationalPeriod(accountId,periodId){
    if(operationalSelection().accountId!==accountId||!contextEnvelope(raw()).accounts[accountId]?.periods?.[periodId])
      return {ok:false,error:'Selecione um período confirmado da conta operacional.'};
    operationalPeriodId=periodId;return {ok:true,selection:operationalSelection()};
  }
  function accountContext(target){
    if(!supported())return {...unavailable('ACCOUNT_CONTEXT_UNSUPPORTED','Contextos de conta incompatíveis; preserve a base.'),value:null};
    if(!object(target)||!text(target.accountId))return {...unavailable('ACCOUNT_ID_MISSING','Identifique a conta cadastrada.'),value:null};
    const a=contextEnvelope(raw()).accounts[target.accountId];
    if(!a)return {...unavailable('ACCOUNT_CONTEXT_MISSING','Registre ou reconcilie explicitamente o período desta conta.'),value:null};
    const periodId=text(target.periodId)||a.currentPeriodId;
    if(!periodId||!a.periods[periodId])return {...unavailable('ACCOUNT_PERIOD_MISSING','Selecione um período confirmado desta conta.'),value:null};
    return {status:'OK',value:clone(a.periods[periodId]),account:clone(a),revision:a.periods[periodId].revision,
      envelopeRevision:contextEnvelope(raw()).revision,findings:[]};
  }
  function newContextPeriod({accountId,periodId,startedAt,currency,si,openingBook,source,observedAt}){
    return {periodId,accountId,startedAt,currency,si,openingBook,source,observedAt,
      activeOperation:null,phases:forexNewOperationPhases(),ledger:[],ledgerEvents:[],revision:1,createdAt:now()};
  }
  function recordAccountPeriod(input,{reason='',expectedEpoch}={}){
    if(!object(input)||!text(input.accountId)||!civilDate(input.startedAt)||
      !/^[A-Z]{3}$/.test(input.currency||'')||!text(input.source)||
      (input.si!==null&&!positive(input.si))||(input.openingBook!==null&&!finite(input.openingBook)))
      return {ok:false,persistido:false,error:'Informe conta, início, moeda, fonte e SI/saldo inicial explícitos ou indisponíveis.'};
    return mutate('account-period-record',reason,[],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; revise o período antes de salvar.');
      const account=registeredAccount(input.accountId);
      if(!account)throw new Error('Conta não está cadastrada ou identidade ambígua.');
      if(text(account.platformCurrency)&&account.platformCurrency!==input.currency)throw new Error('Moeda divergente do cadastro; corrija a ficha de Contas antes de registrar.');
      const e=f.accountContexts||{schemaVersion:1,revision:0,accounts:{},legacy:null};
      const a=e.accounts[input.accountId]||{accountId:input.accountId,currentPeriodId:null,periods:{},archived:false};
      if(Object.values(a.periods).some(p=>p?.activeOperation)&&input.activateCurrentPeriod===true)
        throw new Error('Resolva a operação em andamento desta conta antes de abrir outro período ativo.');
      let periodId=id('fxperiod');
      if(text(input.observationPeriodId)){
        let observation=f.accounts[input.accountId],found=null;
        const seen=new Set();
        while(object(observation)&&!seen.has(observation)){seen.add(observation);
          if(observation.periodId===input.observationPeriodId){found=observation;break;}observation=observation.previous;}
        if(!found||found.currency!==input.currency||found.si!==input.si||
          input.startedAt>found.observedAt.slice(0,10))
          throw new Error('A observação histórica não comprova esse período, SI, moeda ou início.');
        if(a.periods[found.periodId])throw new Error('Este período observado já foi conciliado.');
        periodId=found.periodId;
      }
      a.periods[periodId]=newContextPeriod({...input,periodId,observedAt:now()});
      if(!a.currentPeriodId||input.activateCurrentPeriod===true)a.currentPeriodId=periodId;
      e.accounts[input.accountId]=a;e.revision++;f.accountContexts=e;
    });
  }
  function legacyAccountPreview(){
    const rows=(S.phases||[]).flatMap(p=>p.orders||[]).filter(o=>o&&o.recordStatus!=='draft'&&o.recordStatus!=='voided');
    const scopes=new Set(rows.map(o=>JSON.stringify([o.accountId||null,o.periodId||null,o.currency||null])));
    const ledgerScopes=new Set((S.ledger||[]).map(r=>JSON.stringify([r.accountId||null,r.periodId||null,r.currency||null])));
    const operationScope=S.activeOperation?.recordContext||null;
    const envelope=contextEnvelope(raw()),associations=[];
    const classify=(kind,path,item,scope)=>{
      const accountId=text(scope?.accountId),periodId=text(scope?.periodId),currency=text(scope?.currency);
      const account=envelope.accounts?.[accountId],period=account?.periods?.[periodId];
      const status=accountId&&periodId&&currency&&period&&period.currency===currency?'PROVEN':'UNRECONCILED';
      associations.push({kind,path,status,accountId:accountId||null,periodId:periodId||null,
        currency:currency||null,sourceId:text(item?.orderId||item?.id)||null,
        reason:status==='PROVEN'?'Identidade, período e moeda conferidos com o contexto persistido.':
          !accountId||!periodId||!currency?'Identidade, período ou moeda ausente.':
          !period?'Período não pertence à conta registrada.':'Moeda divergente do período.'});
    };
    (S.phases||[]).forEach((phase,pi)=>(phase.orders||[]).forEach((order,oi)=>{
      if(!order||order.recordStatus==='draft'||order.recordStatus==='voided'||
        !['Aberta','Fechada','Pendente','Migrada'].includes(order.status))return;
      classify('ORDER',`phases.${pi}.orders.${oi}`,order,order);
    }));
    (S.ledger||[]).forEach((row,li)=>{if(row)classify('LEDGER',`ledger.${li}`,row,row);});
    if(S.activeOperation)classify('OPERATION','activeOperation',S.activeOperation,{
      accountId:operationScope?.accountId,periodId:operationScope?.periodId,
      currency:operationScope?.accountInputs?.currency});
    return {schemaVersion:1,existing:!!contextEnvelope(raw()).legacy,
      source:{operation:clone(S.activeOperation),phases:clone(S.phases),ledger:clone(S.ledger),ledgerArchive:clone(S.ledgerArchive),
        params:clone(S.params),period:clone(S.period)},orderScopes:[...scopes],ledgerScopes:[...ledgerScopes],
      associations,operationScope:operationScope?{accountId:operationScope.accountId||null,periodId:operationScope.periodId||null,
        currency:operationScope.accountInputs?.currency||null}:null,
      warning:'Sem comprovacao de conta, periodo e moeda, o legado permanece nao conciliado; a Mestre nao recebe atribuicao automatica.'};
  }
  function confirmLegacyAccountSnapshot({reason='',expectedEpoch}={}){
    const preview=legacyAccountPreview();
    if(preview.existing)return {ok:true,persistido:false,unchanged:true};
    return mutate('legacy-account-snapshot',reason,[],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra a prévia do legado.');
      const e=f.accountContexts||{schemaVersion:1,revision:0,accounts:{},legacy:null};
      if(e.legacy)throw new Error('O snapshot do legado já existe.');
      e.legacy={id:id('fxlegacy'),recordedAt:now(),status:'UNRECONCILED',source:preview.source,
        orderScopes:preview.orderScopes,ledgerScopes:preview.ledgerScopes,operationScope:preview.operationScope,
        associations:preview.associations};
      e.revision++;f.accountContexts=e;
    });
  }
  function accountLedger(target){
    const ctx=accountContext(target);
    if(ctx.status!=='OK')return ctx;
    return {status:'OK',value:ctx.value.ledger.slice().sort((a,b)=>a.data.localeCompare(b.data)),
      currency:ctx.value.currency,openingBook:ctx.value.openingBook,revision:ctx.revision,findings:[]};
  }
  function recordAccountLedger(input,{reason='',expectedEpoch,expectedRevision}={}){
    if(!object(input)||!text(input.accountId)||!text(input.periodId)||
      !['RECORDED','CORRECTED','VOIDED'].includes(input.action)||
      (input.action!=='VOIDED'&&(!civilDate(input.data)||!finite(input.resultado)||
        (input.saldo!==null&&!finite(input.saldo)))))
      return {ok:false,persistido:false,error:'Identifique conta, período, ato, data e valores válidos; resultado zero é permitido.'};
    return mutate('account-ledger-'+input.action.toLowerCase(),reason,[],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; revise o fechamento.');
      if(!registeredAccount(input.accountId))throw new Error('Conta cadastrada mudou ou não existe.');
      const e=contextEnvelope(f),p=e.accounts[input.accountId]?.periods?.[input.periodId];
      if(!p)throw new Error('Período não pertence à conta cadastrada.');
      if(expectedRevision!==undefined&&expectedRevision!==p.revision)throw new Error('O período foi alterado; revise antes de salvar.');
      const index=p.ledger.findIndex(r=>r.id===input.id),old=index<0?null:p.ledger[index];
      if(input.action==='RECORDED'&&old||input.action!=='RECORDED'&&!old)throw new Error('Fechamento ausente ou já registrado.');
      if(old&&(old.accountId!==input.accountId||old.periodId!==input.periodId||old.currency!==p.currency))
        throw new Error('Identidade monetária divergente; preserve o registro para revisão.');
      if(input.action!=='VOIDED'){
        if(input.data<p.startedAt)throw new Error('Data anterior ao início do período.');
        if(p.ledger.some(r=>r!==old&&r.data===input.data))throw new Error('Já há fechamento desta conta/período nessa data.');
      }
      let after=null;
      if(input.action!=='VOIDED'){
        const previous=p.ledger.filter(r=>r!==old&&r.data<input.data).sort((a,b)=>a.data.localeCompare(b.data)).at(-1);
        const opening=previous?.saldo??p.openingBook;
        if(input.saldo===null&&!finite(opening))throw new Error('Saldo inicial book ausente; informe o saldo observado sem presumir zero.');
        after={...old,id:old?.id||id('ld'),accountId:input.accountId,periodId:input.periodId,currency:p.currency,
          data:input.data,resultado:input.resultado,saldo:input.saldo===null?opening+input.resultado:input.saldo,
          nota:text(input.nota),version:(old?.version||0)+1,origin:'MANUAL',
          balanceInput:input.saldo===null?'DERIVED_FROM_PREVIOUS':'OBSERVED',
          referenceBalance:p.openingBook,createdAt:old?.createdAt||now(),updatedAt:now()};
        if(old)p.ledger[index]=after;else p.ledger.push(after);
      }else p.ledger.splice(index,1);
      p.ledgerEvents.push({id:id('lde'),action:input.action,at:now(),reason:text(reason),
        before:old?clone(old):null,after:after?clone(after):null});
      // Uma correção anterior altera apenas saldos cuja origem foi declarada
      // DERIVED_FROM_PREVIOUS. Saldos OBSERVED permanecem evidência independente.
      let balance=p.openingBook;
      for(const row of p.ledger.sort((a,b)=>a.data.localeCompare(b.data))){
        if(row.balanceInput==='DERIVED_FROM_PREVIOUS'){
          if(!finite(balance))throw new Error('Cadeia anterior sem saldo confirmado; informe observação explícita.');
          const revised=balance+row.resultado;
          if(!finite(revised))throw new Error('Saldo derivado inválido.');
          if(revised!==row.saldo){const before=clone(row);row.saldo=revised;row.version++;
            row.updatedAt=now();p.ledgerEvents.push({id:id('lde'),action:'BALANCE_RECALCULATED',at:now(),
              reason:'Revisão da cadeia após '+input.action+' · '+text(reason),before,after:clone(row)});}
        }
        balance=row.saldo;
      }
      p.revision++;e.revision++;f.accountContexts=e;
    });
  }
  function recordAccountOrders(edits,{reason='',accountId,periodId,expectedEpoch,expectedRevision}={}){
    if(!Array.isArray(edits)||!edits.length||!text(accountId)||!text(periodId))
      return {ok:false,persistido:false,error:'Identifique conta, período e linhas da operação.'};
    return mutate('account-operation-orders',reason,[],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra as linhas.');
      if(!registeredAccount(accountId))throw new Error('Conta não está cadastrada ou sua identidade mudou.');
      const e=contextEnvelope(f),p=e.accounts[accountId]?.periods?.[periodId];
      if(!p)throw new Error('Período não pertence à conta cadastrada.');
      if(expectedRevision!==undefined&&expectedRevision!==p.revision)throw new Error('O período mudou; revise as ordens antes de salvar.');
      let firstFactOfNewOperation=false;
      for(const edit of edits){
        const {pi,oi}=edit,rows=p.phases?.[pi]?.orders,old=rows?.[oi];
        if(!old)throw new Error('Linha da fase não existe; reabra o rascunho.');
        if(edit.orderId!==undefined&&edit.orderId!==(old.orderId||null)||
          edit.expectedVersion!==undefined&&edit.expectedVersion!==(old.recordVersion||0))
          throw new Error('A identidade ou versão da ordem mudou; revise antes de salvar.');
        if(old.recordStatus==='voided')throw new Error('Ordem anulada não pode ser reaberta.');
        const allowed=['id','par','tipo','role','lote','entry','sl','tp','result','status','costs','stopValidated',
          'amplifiesExposure','pendingActive','costBasis','recordStatus','divergenceChecked','divergenceReason','divergenceTs'];
        if(!object(edit.changes)||Object.keys(edit.changes).some(k=>!allowed.includes(k)))throw new Error('Campo de ordem inválido.');
        const next={...clone(old),...clone(edit.changes)};
        if(old.recordStatus==='recorded'&&!text(reason))throw new Error('Correção de fato exige motivo.');
        if(old.recordStatus==='recorded'&&next.status==='')throw new Error('Fato confirmado não volta a rascunho; use anulação explícita.');
        if(next.recordStatus==='voided'&&!text(reason))throw new Error('Anulação exige motivo.');
        const invalid=typeof operationValidateOrder==='function'?operationValidateOrder(next):null;
        if(invalid)throw new Error(invalid);
        const live=['Aberta','Fechada','Pendente'].includes(next.status)&&next.recordStatus!=='voided';
        if(live&&next.status==='Fechada'&&!finite(next.result))throw new Error('Resultado ausente não é zero.');
        if(live&&!text(next.par))throw new Error('Informe o instrumento do fato; volume ausente permanecerá não calculável.');
        const context=recordContext({accountId,periodId});
        if(live&&context.accountInputs&&context.accountInputs.currency!==p.currency)
          throw new Error('Moeda da observação diverge do período; preserve o fato sem atribuição.');
        if(live&&!p.activeOperation&&Object.values(e.accounts[accountId].periods).some(other=>other!==p&&other?.activeOperation))
          throw new Error('Esta conta já mantém uma operação em outro período; finalize-a antes de registrar nova execução.');
        if(live&&!p.activeOperation){p.activeOperation={schemaVersion:1,operationId:id('fxop'),openedAt:now(),
          recordContext:context.status==='OK'?clone(context):{accountId,periodId,
            accountInputs:{accountId,periodId,currency:p.currency,si:p.si},status:'NOT_COMPUTABLE',
            provenance:'PERIOD_FACTS_ONLY',findings:clone(context.findings||[])},
          policySnapshot:fx.policy.snapshot(),status:'IN_PROGRESS'};
          firstFactOfNewOperation=true;}
        if(live&&p.activeOperation?.recordContext?.accountId!==accountId||live&&p.activeOperation?.recordContext?.periodId!==periodId)
          throw new Error('Operação pertence a outra conta/período.');
        const at=now(),before=clone(old);delete before.revisions;
        next.orderId=old.orderId||id('fxorder');
        next.recordStatus=next.recordStatus==='voided'?'voided':live?'recorded':'draft';
        next.recordVersion=(old.recordVersion||0)+1;
        if(live){next.accountId=accountId;next.periodId=periodId;next.currency=p.currency;
          next.operationId=p.activeOperation.operationId;
          next.policySnapshot=old.policySnapshot?clone(old.policySnapshot):fx.policy.snapshot();
          const observation=instrumentContext({accountId,periodId,instrumentId:next.par});
          const daily=dailyReference(next.par);
          next.calculationInputs={...(context.status==='OK'?clone(fx.orderInputs(next,context.accountInputs)):{}),
            accountId,periodId,currency:p.currency,recordedAt:at,
            instrumentObservation:observation.status==='OK'?clone(observation.value):null,
            dailyReference:daily.status==='OK'?clone(daily.value):null,
            provenance:'RECORDED_FACT_WITHOUT_EXECUTION_CLEARANCE'};
        }
        if(next.recordStatus==='voided'){next.voidedAt=at;next.voidReason=text(reason);}
        const after=clone(next);delete after.revisions;
        next.revisions=[...(Array.isArray(old.revisions)?clone(old.revisions):[]),{
          version:next.recordVersion,recordedAt:at,reason:text(reason),before,after,
          context:{accountId,periodId,currency:p.currency,operationId:next.operationId||null}}];
        rows[oi]=next;
        if(live&&firstFactOfNewOperation){
          // Associate a unique prospectively declared budget with this first
          // confirmed software fact inside the same rollback/save boundary.
          // Missing/ambiguous budgets never block the factual order record.
          attachOperationBudget(f,{accountId,periodId,currency:p.currency,
            operationId:p.activeOperation.operationId,firstRecordedAt:at});
          firstFactOfNewOperation=false;
        }
      }
      p.revision++;e.revision++;f.accountContexts=e;
    });
  }
  function finalizeAccountOperation(record,{accountId,periodId,expectedEpoch,expectedRevision,reason='Finalização confirmada da operação'}={}){
    if(!object(record)||!text(record.operationId)||!text(accountId)||!text(periodId)||
      record.accountId!==accountId||record.periodId!==periodId||!finite(record.netResult)||
      !Array.isArray(record.ordersSnapshot)||!record.ordersSnapshot.length)
      return {ok:false,persistido:false,error:'Revise a identidade e os resultados da operação antes de finalizar.'};
    const result=mutate('account-operation-finalized',reason,['operationHistory','transitionLog'],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra a revisão.');
      if(!registeredAccount(accountId))throw new Error('A conta não está mais cadastrada.');
      const e=contextEnvelope(f),p=e.accounts[accountId]?.periods?.[periodId],op=p?.activeOperation;
      if(!p||!op||op.operationId!==record.operationId||record.currency!==p.currency)
        throw new Error('A conta, o período ou a operação mudaram; reabra a revisão.');
      if(expectedRevision!==undefined&&expectedRevision!==p.revision)
        throw new Error('Fatos mudaram após a revisão; reabra-a antes de confirmar.');
      if((S.operationHistory?.records||[]).some(r=>r?.operationId===record.operationId))
        throw new Error('Esta operação já foi finalizada.');
      const live=p.phases.flatMap(ph=>ph.orders||[]).filter(o=>['Aberta','Fechada','Pendente'].includes(o.status)&&o.recordStatus!=='voided');
      if(live.some(o=>o.status!=='Fechada'||!finite(o.result)||o.accountId!==accountId||
        o.periodId!==periodId||o.currency!==p.currency||o.operationId!==op.operationId))
        throw new Error('Ordens abertas, resultados ausentes ou vínculos divergentes; fatos preservados.');
      const sourceIds=live.map(o=>o.orderId).sort(),snapshotIds=record.ordersSnapshot.map(o=>o.orderId).sort();
      if(JSON.stringify(sourceIds)!==JSON.stringify(snapshotIds))
        throw new Error('As ordens mudaram depois da revisão.');
      // IDs alone do not bind a receipt to the confirmed monetary facts.
      // Reconstruct the exact rows that the review displays, including phase,
      // position, source revision, prices, costs and historical policy.
      const expectedRows=p.phases.flatMap((ph,pi)=>(ph.orders||[]).map((o,oi)=>({o,pi,oi})))
        .filter(({o})=>['Aberta','Fechada','Pendente'].includes(o.status)&&o.recordStatus!=='voided')
        .map(({o,pi,oi})=>({...clone(o),orderId:o.orderId||(op.operationId+'_legacy_'+pi+'_'+oi),
          phase:pi+1,gridIndex:oi,label:typeof o.id==='string'?o.id:'',
          policySnapshot:clone(o.policySnapshot||{policyVersion:'LEGACY_UNRESOLVED'}),
          openedAt:typeof o.openedAt==='string'?o.openedAt:null,
          closedAt:typeof o.closedAt==='string'?o.closedAt:null}));
      if(JSON.stringify(expectedRows)!==JSON.stringify(record.ordersSnapshot))
        throw new Error('O comprovante diverge dos fatos confirmados; reabra a revisão.');
      const closedAt=Date.parse(record.closedAt),openedAt=Date.parse(record.openedAt||op.openedAt);
      if(!Number.isFinite(closedAt)||closedAt>Date.now()||Number.isFinite(openedAt)&&openedAt>closedAt||
        record.closedAtSource!=='formal_confirmation'||
        JSON.stringify(record.policySnapshot)!==JSON.stringify(op.policySnapshot)||
        JSON.stringify(record.recordContext)!==JSON.stringify(op.recordContext))
        throw new Error('Cronologia, política ou contexto do comprovante divergente; reabra a revisão.');
      const currentNet=live.reduce((sum,o)=>{
        const result=fx.executionBoard?.closedNetResult(o);
        return result?.status==='OK'&&finite(result.value)?sum+result.value:NaN;
      },0);
      if(currentNet!==record.netResult)throw new Error('O resultado mudou; reabra a revisão.');
      if(!S.operationHistory||!Array.isArray(S.operationHistory.records))
        throw new Error('Histórico incompatível; preserve a base.');
      S.operationHistory.records.push(clone(record));
      if(!Array.isArray(S.transitionLog))S.transitionLog=[];
      S.transitionLog.push({fase:'operação finalizada',ts:record.closedAt,operationId:record.operationId,
        accountId,periodId,currency:p.currency,resumo:{resultado:record.netResult,scope:'ACCOUNT_PERIOD'}});
      p.phases=fx.state.newOperationPhases();p.activeOperation=null;p.grid=null;
      p.revision++;e.revision++;f.accountContexts=e;
    });
    return result.ok?{...result,record:clone(record)}:result;
  }
  function addAccountOrderDraft(target,{reason='Adicionar rascunho de ordem',expectedEpoch}={}){
    return mutate('account-order-draft-added',reason,[],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra a fase.');
      if(!registeredAccount(target?.accountId))throw new Error('Conta não cadastrada.');
      const e=contextEnvelope(f),p=e.accounts[target.accountId]?.periods?.[target.periodId];
      if(!p||!Array.isArray(p.phases?.[target.pi]?.orders))throw new Error('Conta, período ou fase inválidos.');
      p.phases[target.pi].orders.push({id:'',orderId:id('fxorder'),par:'',tipo:'BUY',lote:0,entry:0,sl:0,tp:0,
        result:null,status:'',recordStatus:'draft',recordVersion:0,revisions:[]});
      p.revision++;e.revision++;f.accountContexts=e;
    });
  }
  function deleteAccountOrderDraft(target,{reason='Excluir rascunho de ordem',expectedEpoch}={}){
    return mutate('account-order-draft-deleted',reason,[],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra a fase.');
      const e=contextEnvelope(f),p=e.accounts[target?.accountId]?.periods?.[target?.periodId],rows=p?.phases?.[target?.pi]?.orders;
      const old=rows?.[target?.oi];if(!old||old.recordStatus!=='draft'||['Aberta','Fechada','Pendente'].includes(old.status))
        throw new Error('Somente rascunho sem fato pode ser excluído.');
      rows.splice(target.oi,1);p.revision++;e.revision++;f.accountContexts=e;
    });
  }
  function instrumentContext(target){
    if(!supported())return unavailable('INSTRUMENT_SCHEMA_UNSUPPORTED','Observações incompatíveis; preserve a base.');
    if(!object(target)||!text(target.accountId)||!text(target.periodId)||!instrumentKey(target.instrumentId))
      return unavailable('INSTRUMENT_SCOPE_MISSING','Identifique conta, período e instrumento; o cadastro global não preenche esse vínculo.');
    if(target.asOf!==undefined&&!instant(target.asOf))return unavailable('INSTRUMENT_TIME_INVALID','Instante da consulta inválido.');
    const key=instrumentKey(target.instrumentId),rows=(raw()?.instrumentContexts?.records||[]).filter(r=>
      r.accountId===target.accountId&&r.periodId===target.periodId&&r.instrumentId===key);
    if(rows.length!==1)return {...unavailable(rows.length?'INSTRUMENT_SCOPE_AMBIGUOUS':'INSTRUMENT_NOT_OBSERVED',
      rows.length?'Há mais de uma observação para esse vínculo.':'Registre observações deste instrumento para a conta e período.'),revision:0};
    let record=rows[0];
    if(target.currency!==undefined&&target.currency!==record.currency)return unavailable('INSTRUMENT_CURRENCY_MISMATCH','A moeda da observação não corresponde à consulta.');
    if(target.asOf!==undefined){
      const at=Date.parse(target.asOf);
      while(record&&(Date.parse(record.recordedAt)>at||componentKeys.some(k=>record[k]&&Date.parse(record[k].observedAt)>at)))record=record.previous;
    }
    if(!record)return {...unavailable('INSTRUMENT_HISTORY_MISSING','Não há observação capturada até esse instante.'),revision:0};
    const value=clone(record);return {status:'OK',value,observation:clone(value),revision:value.revision,findings:[]};
  }
  function recordInstrumentContext(input,{reason='',expectedEpoch}={}){
    if(!object(input)||!text(input.accountId)||!text(input.periodId)||!instrumentKey(input.instrumentId)||
      !Number.isInteger(input.expectedRevision)||input.expectedRevision<0||!object(input.componentChanges)||
      !Object.keys(input.componentChanges).length||Object.keys(input.componentChanges).some(k=>!componentKeys.includes(k)))
      return {ok:false,persistido:false,error:'Identifique conta, período, instrumento, revisão e componentes da observação.'};
    const changes=clone(input.componentChanges),key=instrumentKey(input.instrumentId);
    for(const [name,component] of Object.entries(changes)){
      if(object(component)&&component.sourceKind===undefined)component.sourceKind='MANUAL';
      if(!componentShape(name,component)||Date.parse(component.observedAt)>Date.now())
        return {ok:false,persistido:false,error:'Observação inválida de '+name+': informe valores, fonte e instante já ocorrido.'};
      component.observedAt=new Date(component.observedAt).toISOString();
    }
    return mutate('instrument-context-observation',reason,[],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra o formulário.');
      const accounts=(S.accounts||[]).filter(a=>a&&a.forexAccountId===input.accountId);
      const period=contextEnvelope(f).accounts[input.accountId]?.periods?.[input.periodId];
      const legacy=f.accounts[input.accountId];
      if(accounts.length!==1||!period&&!legacy||!period&&legacy.periodId!==input.periodId)
        throw new Error('Conta cadastrada ou período mudou; confira o vínculo antes de registrar.');
      const currency=period?.currency||legacy.currency;
      if(accounts[0].platformCurrency&&accounts[0].platformCurrency!==currency)
        throw new Error('Moeda da observação diverge do cadastro.');
      if(!(S.instruments||[]).some(ins=>instrumentKey(ins.name)===key))throw new Error('Instrumento não cadastrado.');
      const envelope=f.instrumentContexts||{schemaVersion:1,records:[]};
      const index=envelope.records.findIndex(r=>r.accountId===input.accountId&&r.periodId===input.periodId&&r.instrumentId===key);
      const previous=index<0?null:envelope.records[index];
      if((previous?.revision||0)!==input.expectedRevision)throw new Error('A observação mudou; confira a revisão antes de salvar.');
      for(const [name,component] of Object.entries(changes))if(previous?.[name]&&Date.parse(component.observedAt)<Date.parse(previous[name].observedAt))
        throw new Error('Observação anterior à vigente; não substituir silenciosamente '+name+'.');
      const record={...(previous?clone(previous):{}),id:previous?.id||id('fxinstrument'),accountId:input.accountId,periodId:input.periodId,
        instrumentId:key,currency,revision:(previous?.revision||0)+1,...changes,recordedAt:now(),previous:previous?clone(previous):null};
      if(index<0)envelope.records.push(record);else envelope.records[index]=record;
      f.instrumentContexts=envelope;
    });
  }
  function dailyReference(instrumentId){
    if(!supported())return unavailable('REFERENCE_SCHEMA_UNSUPPORTED','Referências incompatíveis; preserve a base.');
    const key=instrumentKey(instrumentId),quote=raw()?.dailyReferences?.quotes?.[key],revision=raw()?.dailyReferences?.revision||0;
    if(!quote)return {...unavailable('DAILY_REFERENCE_MISSING','Referência diária ainda não disponível para este par.'),revision};
    return {status:'OK',value:clone(quote),revision,findings:[]};
  }
  function dailyReferenceRevision(){return supported()?(raw()?.dailyReferences?.revision||0):null;}
  function recordDailyReferences(input,{reason='Atualização das referências diárias FX'}={}){
    if(!object(input)||!object(input.quotes)||!Object.keys(input.quotes).length||
      !Number.isInteger(input.expectedRevision)||input.expectedRevision<0||input.expectedEpoch===undefined||
      !Object.entries(input.quotes).every(([key,quote])=>dailyQuoteShape(quote,key)&&Date.parse(quote.fetchedAt)<=Date.now()))
      return {ok:false,persistido:false,error:'Lote de referências diárias inválido ou sem revisão/geração.'};
    const quotes=clone(input.quotes);
    function inspectBatch(f){
      if(input.expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; descarte esta atualização anterior.');
      const envelope=f?.dailyReferences||{schemaVersion:1,revision:0,quotes:{}};
      if(envelope.revision!==input.expectedRevision)throw new Error('As referências foram atualizadas; confira antes de repetir.');
      for(const [key,quote] of Object.entries(quotes)){
        const previous=envelope.quotes[key];
        if(previous&&(quote.referenceDate<previous.referenceDate||Date.parse(quote.fetchedAt)<Date.parse(previous.fetchedAt)))
          throw new Error('Referência anterior à vigente para '+key+'.');
      }
      const fields=['base','quote','rate','referenceDate','source','sourceKind'];
      return {envelope,unchanged:Object.entries(quotes).every(([key,quote])=>{
        const previous=envelope.quotes[key];return previous&&fields.every(field=>previous[field]===quote[field]);
      })};
    }
    // A repeated daily observation is not a new financial fact. Preserve its
    // original confirmation timestamp, revision and audit trail byte-for-byte.
    // Validate the same generation/revision and persistence barriers first.
    if(!text(reason))return {ok:false,persistido:false,error:'Informe o motivo do registro.'};
    if(!supported())return {ok:false,persistido:false,error:'Agregado Forex incompatível. Preserve a base e revise a versão.'};
    if(jpWealthPersistenceOutcomeIsUnknown())return {ok:false,persistido:null,error:'Gravação indeterminada. Confira a base antes de repetir.'};
    if(jpWealthPersistenceIsBlocked())return {ok:false,persistido:false,error:'A persistência está bloqueada; confira a base antes de atualizar.'};
    try{if(inspectBatch(raw()).unchanged)return {ok:true,persistido:false,unchanged:true};}
    catch(error){return {ok:false,persistido:false,error:error.message};}
    return mutate('daily-reference-update',reason,[],f=>{
      const {envelope}=inspectBatch(f);
      f.dailyReferences={...envelope,revision:envelope.revision+1,quotes:{...envelope.quotes,...quotes}};
    });
  }
  function migrateLegacy({reason}={}){
    if(raw()&&raw().migration)return {ok:true,persistido:false,alreadyMigrated:true};
    return mutate('legacy-migration',reason,['phases','accounts','activeOperation'],f=>{
      // Snapshot only financial legacy inputs: never account credentials.
      f.migration={id:id('fxmigration'),timestamp:now(),sourcePolicy:'LEGACY_UNRESOLVED',
        sourceParams:clone(S.params),sourceMatrix:clone(S.matrix),sourceProfiles:clone(S.profiles),
        sourcePhases:clone(S.phases),sourceActiveOperation:clone(S.activeOperation),
        historyUnchanged:true};
      for(const phase of S.phases||[]){
        phase.policyVersion=phase.policyVersion||'LEGACY_UNRESOLVED';
        for(const order of phase.orders||[]){
          if(!order.orderId)order.orderId=id('fxorder');
          if(!order.policySnapshot)order.policySnapshot={policyVersion:'LEGACY_UNRESOLVED',
            source:'explicit-migration',originalPhase:phase.faseNome||phase.title||null};
        }
      }
      if(S.activeOperation&&!S.activeOperation.policySnapshot)
        S.activeOperation.policySnapshot={policyVersion:'LEGACY_UNRESOLVED',source:'explicit-migration'};
    });
  }
  function recordAccountFacts(input,{reason}={}){
    if(!input||!Number.isInteger(input.accountIndex)||!S.accounts[input.accountIndex])
      return {ok:false,persistido:false,error:'Selecione explicitamente uma conta existente.'};
    if(!finite(input.si)||input.si<=0||!finite(input.equity)||!text(input.source)||
        !text(input.observedAt)||!Number.isFinite(Date.parse(input.observedAt))||!['USD','BRL','EUR','GBP','JPY','CHF','CAD','AUD','NZD'].includes(input.currency))
      return {ok:false,persistido:false,error:'Informe SI positivo, equity, fonte e instante válido da observação.'};
    if(input.currency!=='USD'&&(!finite(input.usdToAccountRate)||input.usdToAccountRate<=0))return {ok:false,persistido:false,error:'Informe a conversão USD para a moeda da conta, com a mesma fonte da observação.'};
    if(input.netCashflow!=null&&!finite(input.netCashflow))return {ok:false,persistido:false,error:'Fluxo de caixa inválido.'};
    if(input.capitalNominal!=null&&(!finite(input.capitalNominal)||input.capitalNominal<0))return {ok:false,persistido:false,error:'Capital nominal inválido.'};
    if(input.marginLevel!=null&&(!finite(input.marginLevel)||input.marginLevel<0))return {ok:false,persistido:false,error:'Nível de margem inválido.'};
    return mutate('account-observation',reason,['accounts','activeOperation'],f=>{
      const account=S.accounts[input.accountIndex];
      if(!account.forexAccountId)account.forexAccountId=id('fxaccount');
      const key=account.forexAccountId, previous=f.accounts[key]||null;
      const requestedNewPeriod=input.newPeriod===true;
      const e=f.accountContexts||{schemaVersion:1,revision:0,accounts:{},legacy:null};
      const a=e.accounts[key]||{accountId:key,currentPeriodId:null,periods:{},archived:false};
      const selected=input.periodId?a.periods[input.periodId]:!requestedNewPeriod&&a.currentPeriodId?a.periods[a.currentPeriodId]:null;
      const newPeriod=requestedNewPeriod||!!(selected&&previous&&selected.periodId!==previous.periodId);
      if(input.periodId&&!selected)throw new Error('Período selecionado não pertence à conta cadastrada.');
      if(newPeriod&&a.currentPeriodId&&a.periods[a.currentPeriodId]?.activeOperation)
        throw new Error('Resolva a operação desta conta antes de iniciar novo período.');
      if(newPeriod&&selected&&selected.periodId===previous?.periodId)throw new Error('Novo período exige identidade distinta da observação anterior.');
      // SI and currency identify the monetary basis. Keep the old observation
      // intact; neither a currency switch nor an older reading silently resets it.
      if(previous&&(previous.si!==input.si||previous.currency!==input.currency)&&!newPeriod)
        throw new Error('Mudança de SI ou moeda exige registrar explicitamente um novo período. Os fatos anteriores mantêm sua unidade.');
      if(previous&&(!Number.isFinite(Date.parse(previous.observedAt))||Date.parse(input.observedAt)<Date.parse(previous.observedAt)))
        throw new Error('Uma observação mais antiga não pode substituir a observação atual. Preserve a entrada para revisar seu contexto histórico.');
      const fact={si:input.si,equity:input.equity,currency:input.currency,usdToAccountRate:input.currency==='USD'?1:input.usdToAccountRate,capitalNominal:input.capitalNominal==null?null:input.capitalNominal,
        netCashflow:input.netCashflow==null?null:input.netCashflow,
        cashflowAdjustmentRecorded:input.cashflowAdjustmentRecorded===true,
        marginLevel:input.marginLevel==null?null:input.marginLevel,source:text(input.source),
        observedAt:new Date(input.observedAt).toISOString(),
        periodId:previous&&!newPeriod?previous.periodId:selected?.periodId||id('fxperiod'),
        recordedAt:now(),previous:previous?clone(previous):null};
      f.accounts[key]=fact;f.activeAccountId=key;
      if(!a.periods[fact.periodId]){
        a.periods[fact.periodId]=newContextPeriod({accountId:key,periodId:fact.periodId,
          startedAt:fact.observedAt.slice(0,10),currency:fact.currency,si:fact.si,openingBook:null,
          source:'ACCOUNT_OBSERVATION',observedAt:fact.observedAt});
        a.currentPeriodId=fact.periodId;e.accounts[key]=a;e.revision++;f.accountContexts=e;
      }else if(a.periods[fact.periodId].currency!==fact.currency||a.periods[fact.periodId].si!==null&&a.periods[fact.periodId].si!==fact.si){
        throw new Error('SI ou moeda da observação diverge do período registrado em Contas.');
      }
      const dd=fx.engine.computeDrawdown(fact);
      if(dd.status==='OK'){
        const phase=!newPeriod&&previous&&previous.phaseState&&Number.isInteger(previous.phaseState.phase)?fx.engine.resolvePhaseReturnWithHysteresis({ddPercent:dd.value,
          previousPhase:previous&&previous.phaseState?previous.phaseState.phase:null,
          confirmedH4Closes:f.h4Closes.filter(c=>c.accountId===key&&c.periodId===fact.periodId&&Number.isFinite(Date.parse(c.closedAt))&&Date.parse(c.closedAt)<=Date.parse(fact.observedAt)),
          since:previous&&previous.phaseState?previous.phaseState.since:null}):fx.engine.resolveAccountPhase({ddPercent:dd.value});
        const value=phase.value;
        fact.phaseState={phase:typeof value==='number'?value:(value&&value.number)||null,
          since:!newPeriod&&previous&&previous.phaseState&&previous.phaseState.phase===(typeof value==='number'?value:value&&value.number)?previous.phaseState.since:fact.observedAt};
      }
      // Account observations are confirmed facts too. Capture a transient peak
      // in the operation's own account/period before a later recovery hides it.
      // activeOperation participates in the same refusal rollback as the fact.
      if(typeof operationTouchAccountPhase==='function')operationTouchAccountPhase();
    });
  }
  function selectAccount(accountId){
    if(!raw()||!raw().accounts[accountId])return {ok:false,persistido:false,error:'Conta sem observação registrada.'};
    return mutate('select-account','Seleção explícita da conta de referência',[],f=>{f.activeAccountId=accountId;});
  }
  function recordMarket(input,{reason}={}){
    if(!input||!finite(input.atrShort)||input.atrShort<0||!finite(input.atrLong)||input.atrLong<=0||
       !text(input.source)||!Number.isFinite(Date.parse(input.observedAt)))
      return {ok:false,persistido:false,error:'Informe ATR curto não negativo e ATR longo positivo, fonte e instante da observação H4.'};
    return mutate('market-observation',reason,[],f=>{f.market={atrShort:input.atrShort,atrLong:input.atrLong,
      source:text(input.source),observedAt:new Date(input.observedAt).toISOString(),timeframe:'H4',previous:f.market?clone(f.market):null};});
  }
  function recordH4(input,{reason,target,expectedEpoch,expectedRevision}={}){
    if(!input||!finite(input.ddPercent)||input.ddPercent<0||!text(input.source)||
        !Number.isFinite(Date.parse(input.closedAt))||Date.parse(input.closedAt)>Date.now())
      return {ok:false,persistido:false,error:'Registre DD, fonte e fechamento H4 já ocorrido; o relógio não confirma candle.'};
    return mutate('confirmed-h4',reason,[],f=>{
      const closedAt=new Date(input.closedAt).toISOString();
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra o fechamento H4.');
      const accountId=target?.accountId||f.activeAccountId;
      const periodId=target?.periodId||f.accounts[accountId]?.periodId;
      const period=target?contextEnvelope(f).accounts[accountId]?.periods?.[periodId]:null;
      if(target&&(!registeredAccount(accountId)||!period))throw new Error('Conta/período operacional mudou; reabra o fechamento H4.');
      if(target&&expectedRevision!==undefined&&period.revision!==expectedRevision)throw new Error('Período alterado; reabra o fechamento H4.');
      if(!accountId||!periodId||!period&&!f.accounts[accountId])throw new Error('Registre uma conta e seu período antes do fechamento H4.');
      if(f.h4Closes.some(c=>c.closedAt===closedAt&&c.accountId===accountId&&c.periodId===periodId))throw new Error('Esse fechamento H4 já está registrado para a conta/período.');
      f.h4Closes.push({closedAt,ddPercent:input.ddPercent,source:text(input.source),timeframe:'H4',recordedAt:now(),accountId,periodId});
      if(period){period.revision++;f.accountContexts.revision++;}
    });
  }
  function recordGrid(phase,{reason,target,expectedEpoch,expectedRevision}={}){
    if(!Number.isInteger(phase)||phase<1||phase>6)return {ok:false,persistido:false,error:'Fase da grade inválida.'};
    return mutate('grid-observation',reason,['transitionLog'],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra a grade.');
      const period=target?contextEnvelope(f).accounts[target.accountId]?.periods?.[target.periodId]:null;
      if(target&&(!registeredAccount(target.accountId)||!period||!period.activeOperation||
        target.operationId!==period.activeOperation.operationId))throw new Error('Registre a operação nesta conta/período antes de declarar sua grade.');
      if(target&&expectedRevision!==undefined&&period.revision!==expectedRevision)throw new Error('Operação alterada; reabra a grade.');
      if(!target&&!S.activeOperation)throw new Error('Registre a operação antes de declarar sua grade.');
      if(!Array.isArray(S.transitionLog))throw new Error('Histórico de transição incompatível.');
      const operationId=target?period.activeOperation.operationId:S.activeOperation.operationId;
      S.transitionLog.push({at:now(),operationId,accountId:target?.accountId||null,periodId:target?.periodId||null,
        gridPhase:phase-1,action:'grid-observation',reason:text(reason),policyVersion:fx.policy.version});
      const previous=target?period.grid:f.grid;
      const next={declaredPhase:phase,structureKnown:true,recordedAt:now(),operationId,
        previous:previous?clone(previous):null};
      if(target){period.grid=next;period.revision++;f.accountContexts.revision++;}else f.grid=next;
    });
  }
  function recordReserves(input,{reason,target,expectedEpoch,expectedRevision}={}){
    const numeric=['capitalNominal','fcrConstituted','feoConstituted','sixMonthExpenseAmount'];
    if(!input||numeric.some(k=>input[k]!=null&&(!finite(input[k])||input[k]<0))||!text(input.source))
      return {ok:false,persistido:false,error:'Informe valores não negativos ou ausentes e a fonte da apuração.'};
    if(input.determinationRecorded&&(!text(input.expensePeriod)||!text(input.determinationReference)))
      return {ok:false,persistido:false,error:'A apuração exige período e referência do método/documento.'};
    return mutate('reserve-observation',reason,[],f=>{
      if(expectedEpoch!==undefined&&expectedEpoch!==jpWealthPersistenceEpoch())throw new Error('A base mudou; reabra a apuração de reservas.');
      const period=target?contextEnvelope(f).accounts[target.accountId]?.periods?.[target.periodId]:null;
      if(target&&(!registeredAccount(target.accountId)||!period))throw new Error('Conta/período operacional mudou; reabra as reservas.');
      if(target&&expectedRevision!==undefined&&period.revision!==expectedRevision)throw new Error('Período alterado; reabra as reservas.');
      const account=target?period:f.accounts[f.activeAccountId]||null;
      const accountId=target?.accountId||f.activeAccountId;
      const next={...clone(input),recordedAt:now(),accountId:account?accountId:null,
        periodId:account&&text(account.periodId)||null,currency:account&&text(account.currency)||null,
        previous:(target?period.reserves:f.reserves)?clone(target?period.reserves:f.reserves):null};
      if(target){period.reserves=next;period.revision++;f.accountContexts.revision++;}else f.reserves=next;
    });
  }
  const budgetUnavailable=(code,message)=>({...unavailable(code,message),unit:'ACCOUNT_CURRENCY',currency:null,declaration:null,executionEligibility:'BLOCKED'});
  const budgetScopeValid=target=>object(target)&&text(target.accountId)&&text(target.periodId)&&
    Object.prototype.hasOwnProperty.call(target,'operationId')&&(target.operationId===null||!!text(target.operationId));
  function budgetResult(declaration){
    const v=declaration.versions[declaration.versions.length-1];
    return {status:'OK',value:v.amount,unit:'ACCOUNT_CURRENCY',currency:declaration.currency,
      declaration:clone(declaration),policyVersion:v.policyVersion,executionEligibility:'BLOCKED',
      findings:[{code:'BUDGET_DECLARATION_NOT_AUTHORIZATION',message:'Teto interno declarado; não autoriza consumo nem comprova declaração anterior à execução externa.',source:'PDF p71 Art8.4 §§10–12'}]};
  }
  function budgetSnapshot(target){
    // Pure read of an explicitly identified declaration; never selected-account
    // fallback, implicit migration or recursive consultation of the read-model.
    if(!supported())return budgetUnavailable('BUDGET_SCHEMA_UNSUPPORTED','Agregado de orçamento incompatível; preserve os registros.');
    if(!budgetScopeValid(target))return budgetUnavailable('BUDGET_IDENTITY_MISSING','Identifique conta, período e operação, ou operação nula para declaração prospectiva.');
    const rows=(raw()&&raw().operationBudgets||[]).filter(b=>b.accountId===target.accountId&&b.periodId===target.periodId&&b.operationId===target.operationId&&
      (!target.budgetId||b.id===target.budgetId)&&(!target.currency||b.currency===target.currency));
    if(rows.length!==1)return budgetUnavailable(rows.length?'BUDGET_IDENTITY_AMBIGUOUS':'BUDGET_NOT_DECLARED',rows.length?'Mais de uma declaração corresponde ao escopo; não escolher automaticamente.':'Orçamento não declarado para este escopo.');
    return budgetResult(rows[0]);
  }
  function budgetOperationKnown(target){
    const same=op=>{
      const c=op&&op.recordContext;
      return op&&op.operationId===target.operationId&&c&&c.accountId===target.accountId&&c.periodId===target.periodId&&
        c.accountInputs&&c.accountInputs.currency===target.currency;
    };
    const period=contextEnvelope(raw()).accounts[target.accountId]?.periods?.[target.periodId];
    const contextual=period?.activeOperation;
    return !!(contextual&&contextual.operationId===target.operationId&&period.currency===target.currency)||
      same(S.activeOperation)||(S.operationHistory&&Array.isArray(S.operationHistory.records)&&S.operationHistory.records.some(same));
  }
  function budgetCommittedRisk(target){
    // Historical/prospective declarations have no current RC. An active
    // contextual operation is computed from its own confirmed facts only.
    const period=contextEnvelope(raw()).accounts[target.accountId]?.periods?.[target.periodId];
    const contextual=period?.activeOperation?.operationId===target.operationId&&period.currency===target.currency;
    const op=contextual?period.activeOperation:S.activeOperation,c=op&&op.recordContext;
    if(!op||op.operationId!==target.operationId||!c||c.accountId!==target.accountId||c.periodId!==target.periodId||
      (contextual?period.currency!==target.currency:!c.accountInputs||c.accountInputs.currency!==target.currency))
      return budgetUnavailable('BUDGET_RC_UNAVAILABLE','Risco comprometido da operação não está apurado neste contexto.');
    const facts=(contextual?period.phases:S.phases||[]).flatMap(p=>p.orders||[]).filter(o=>o&&o.recordStatus!=='voided'&&['Aberta','Fechada','Pendente'].includes(o.status));
    if(facts.some(o=>o.operationId!==target.operationId))
      return budgetUnavailable('BUDGET_RC_CONTEXT_MISMATCH','Risco comprometido contém fatos sem vínculo inequívoco à operação.');
    const model=fx.readModel({accountId:target.accountId,periodId:target.periodId});
    const rc=model&&model.metrics&&model.metrics.committedRisk;
    return rc&&rc.status==='OK'&&finite(rc.value)&&rc.value>=0?clone(rc):
      budgetUnavailable('BUDGET_RC_UNAVAILABLE','Risco comprometido ausente ou incompleto; não é zero.');
  }
  function recordOperationBudget(input,{reason}={}){
    if(!budgetScopeValid(input)||!finite(input.amount)||input.amount<0||!text(input.currency)||
      !text(input.source)||!text(input.declaredBy)||!Number.isFinite(Date.parse(input.declaredAt))||Date.parse(input.declaredAt)>Date.now())
      return {ok:false,persistido:false,error:'Informe escopo explícito, orçamento não negativo, moeda, fonte, autoria declarada e instante válido não futuro.'};
    const period=contextEnvelope(raw()).accounts[input.accountId]?.periods?.[input.periodId];
    const context=recordContext({accountId:input.accountId,periodId:input.periodId});
    if(!registeredAccount(input.accountId)||
      (period?period.currency!==input.currency:context.status!=='OK'||!context.accountInputs||context.accountInputs.currency!==input.currency))
      return {ok:false,persistido:false,error:'Conta, período ou moeda do orçamento não conciliados; sem uso da conta selecionada.'};
    if(input.operationId!==null&&!budgetOperationKnown(input))
      return {ok:false,persistido:false,error:'A operação informada não possui esse contexto registrado. Use declaração prospectiva somente para o próximo primeiro registro.'};
    return mutate('operation-budget-declaration',reason,[],f=>{
      const rows=f.operationBudgets||[];
      const matching=rows.filter(b=>b.accountId===input.accountId&&b.periodId===input.periodId&&b.operationId===input.operationId);
      if(matching.length>1)throw new Error('Declarações ambíguas; preserve a base e confira a identidade.');
      let entry=matching[0]||null;
      if(entry&&entry.currency!==input.currency)throw new Error('A moeda da declaração diverge da conta/período; preserve e concilie os fatos.');
      if(input.budgetId&&(!entry||entry.id!==input.budgetId))throw new Error('A declaração indicada não corresponde ao contexto.');
      if(entry&&!input.budgetId)throw new Error('Já existe orçamento neste contexto. Identifique essa declaração para uma redução explícita.');
      let committedRiskAtReduction=null;
      if(entry){
        const previous=entry.versions[entry.versions.length-1];
        if(input.amount>=previous.amount)throw new Error('O orçamento existente não pode ser ampliado; a alteração deve ser uma redução explícita.');
        committedRiskAtReduction=budgetCommittedRisk(input);
        if(committedRiskAtReduction.status!=='OK')throw new Error('Risco comprometido ausente ou incompleto: redução não confirmada.');
        if(input.amount<committedRiskAtReduction.value)throw new Error('O novo orçamento não pode ser inferior ao risco comprometido apurado.');
      }else{
        entry={schemaVersion:1,id:id('fxbudget'),accountId:input.accountId,periodId:input.periodId,currency:input.currency,
          operationId:input.operationId,association:null,versions:[]};
        if(!f.operationBudgets)f.operationBudgets=[];
        f.operationBudgets.push(entry);
      }
      entry.versions.push({version:entry.versions.length+1,amount:input.amount,source:text(input.source),declaredBy:text(input.declaredBy),
        declaredAt:new Date(input.declaredAt).toISOString(),recordedAt:now(),reason:text(reason),
        recordingTiming:input.operationId===null?'BEFORE_FIRST_SOFTWARE_RECORD':'RETROSPECTIVE_DECLARATION',
        doesNotProveExternalPreExecution:true,policyVersion:fx.policy.version,policySnapshot:fx.policy.snapshot(),
        committedRiskAtReduction});
    });
  }
  function attachOperationBudget(forex,target){
    // Used only inside the first fact's existing transaction (forex is in its
    // rollback set). No save, authorization, or guard of factual order creation.
    if(forex!==raw()||!supported()||!budgetScopeValid(target)||!text(target.operationId)||!text(target.currency)||
      !Number.isFinite(Date.parse(target.firstRecordedAt)))
      return budgetUnavailable('BUDGET_ASSOCIATION_UNAVAILABLE','Identidade ou instante da associação incompletos; o fato não recebe orçamento presumido.');
    const existing=budgetSnapshot(target);
    if(existing.status==='OK')return existing;
    const rows=(forex.operationBudgets||[]).filter(b=>b.accountId===target.accountId&&b.periodId===target.periodId&&b.currency===target.currency&&b.operationId===null);
    if(rows.length!==1)return budgetUnavailable(rows.length?'BUDGET_IDENTITY_AMBIGUOUS':'BUDGET_NOT_DECLARED','Não há declaração prospectiva única para associar a este primeiro registro.');
    const entry=rows[0],latest=entry.versions[entry.versions.length-1];
    if(Date.parse(target.firstRecordedAt)<Date.parse(latest.recordedAt))
      return budgetUnavailable('BUDGET_RECORDING_CHRONOLOGY','O instante informado antecede o registro da declaração; associação não comprovada.');
    entry.operationId=target.operationId;entry.association={operationId:target.operationId,firstRecordedAt:new Date(target.firstRecordedAt).toISOString(),
      associatedAt:now(),source:'FIRST_SOFTWARE_FACT_RECORD',doesNotProveExternalPreExecution:true};
    return budgetResult(entry);
  }
  // A temporary, operator-created access friction. No supplied credential, no
  // persistence, no server identity and no claim of resistance to DevTools.
  let session=null, verifier=null, verifierSalt=null, editorEpoch=0;
  const SESSION_MS=5*60*1000;
  async function derive(secret,salt){
    const key=await crypto.subtle.importKey('raw',new TextEncoder().encode(secret),'PBKDF2',false,['deriveBits']);
    return new Uint8Array(await crypto.subtle.deriveBits({name:'PBKDF2',salt,iterations:210000,hash:'SHA-256'},key,256));
  }
  function editorStatus(){
    if(session&&session.expiresAt<=Date.now())session=null;
    return {configured:!!verifier,unlocked:!!session,expiresAt:session?session.expiresAt:null,
      security:'LOCAL_SESSION_ONLY',activationAvailable:false};
  }
  async function configureEditor(secret){
    if(!crypto.subtle||typeof secret!=='string'||secret.length<12)return {ok:false,error:'Use uma frase local de ao menos 12 caracteres em contexto seguro.'};
    const epoch=++editorEpoch;const salt=crypto.getRandomValues(new Uint8Array(16));const bits=await derive(secret,salt);
    if(epoch!==editorEpoch)return {ok:false,error:'Sessão local encerrada durante a configuração.'};
    verifierSalt=salt;verifier=bits;session=null;return {ok:true,security:'LOCAL_SESSION_ONLY'};
  }
  async function unlockEditor(secret,editor){
    if(!verifier||!text(editor))return {ok:false,error:'Configure a proteção temporária e identifique o editor local.'};
    const epoch=editorEpoch, expected=verifier, salt=verifierSalt, bits=await derive(secret,salt);
    let diff=bits.length^expected.length;for(let i=0;i<bits.length;i++)diff|=bits[i]^expected[i];
    if(diff||expected!==verifier||epoch!==editorEpoch)return {ok:false,error:'Frase local não corresponde à sessão configurada.'};
    session={editor:text(editor),expiresAt:Date.now()+SESSION_MS};return {ok:true,...editorStatus()};
  }
  function lockEditor(){editorEpoch++;session=null;return editorStatus();}
  function clearEditor(){editorEpoch++;session=null;verifier=null;verifierSalt=null;}
  function proposeParameterChange(input){
    if(!editorStatus().unlocked)return {ok:false,persistido:false,error:'Desbloqueie a sessão local de edição.'};
    const entry=input&&fx.policy.get(input.id);
    if(!entry||!text(input.reason)||!text(input.source)||!finite(input.value))
      return {ok:false,persistido:false,error:'Informe parâmetro, valor finito, motivo e fonte normativa.'};
    const editor=session.editor;
    return mutate('parameter-proposal',input.reason,[],f=>{f.proposals.push({id:id('fxproposal'),timestamp:now(),field:entry.id,
      oldValue:clone(entry.value),newValue:input.value,source:text(input.source),reason:text(input.reason),editor,
      version:fx.policy.policyVersion||fx.policy.version,authorityMode:entry.authorityMode,
      status:entry.authorityMode==='DELEGATED_N3'?'CALIBRATION_PROPOSAL':'NORMATIVE_AMENDMENT_DRAFT',
      active:false,limitation:'Proposta local não homologa norma nem comprova identidade externa.'});});
  }
  function activateProposal(){return {ok:false,persistido:false,status:'BLOCKED',error:'Ativação exige ato normativo e autoridade verificáveis. A sessão local não os comprova.'};}
  fx.state={empty,read:(target)=>target===undefined?fx.readModel():fx.readModel(target),recordContext,context:recordContext,mutate,migrateLegacy,
    operationalSelection,selectOperationalAccount,selectOperationalPeriod,archiveRegisteredAccount,
    accountContext,recordAccountPeriod,legacyAccountPreview,confirmLegacyAccountSnapshot,
    accountLedger,recordAccountLedger,recordAccountOrders,finalizeAccountOperation,addAccountOrderDraft,deleteAccountOrderDraft,
    recordAccountFacts,selectAccount,recordMarket,recordH4,recordGrid,recordReserves,
    recordInstrumentContext,instrumentContext,recordDailyReferences,dailyReference,dailyReferenceRevision,
    recordOperationBudget,budgetSnapshot,attachOperationBudget,
    editorStatus,configureEditor,unlockEditor,lockEditor,clearEditor,proposeParameterChange,activateProposal,
    supported,unavailable,newOperationPhases:forexNewOperationPhases};
  root.addEventListener('pagehide',clearEditor);
})(globalThis);

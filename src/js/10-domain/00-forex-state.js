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
    reserves:null,proposals:[],auditLog:[],migration:null});
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
  const supported=(value=raw())=>value==null||(object(value)&&value.schemaVersion===1&&
    value.policyVersion===(fx.policy.policyVersion||fx.policy.version)&&
    object(value.accounts)&&Object.values(value.accounts).every(object)&&
    Array.isArray(value.h4Closes)&&value.h4Closes.every(object)&&
    Array.isArray(value.auditLog)&&value.auditLog.every(object)&&
    Array.isArray(value.proposals)&&value.proposals.every(object)&&
    (value.operationBudgets===undefined||(Array.isArray(value.operationBudgets)&&value.operationBudgets.every(budgetShape)))&&
    (value.instrumentContexts===undefined||instrumentContextsShape(value.instrumentContexts))&&
    (value.dailyReferences===undefined||dailyReferencesShape(value.dailyReferences))&&
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
      const accounts=(S.accounts||[]).filter(a=>a&&a.forexAccountId===input.accountId),account=f.accounts[input.accountId];
      if(accounts.length!==1||!account||account.periodId!==input.periodId)throw new Error('Conta cadastrada ou período mudou; confira o vínculo antes de registrar.');
      if(!(S.instruments||[]).some(ins=>instrumentKey(ins.name)===key))throw new Error('Instrumento não cadastrado.');
      const envelope=f.instrumentContexts||{schemaVersion:1,records:[]};
      const index=envelope.records.findIndex(r=>r.accountId===input.accountId&&r.periodId===input.periodId&&r.instrumentId===key);
      const previous=index<0?null:envelope.records[index];
      if((previous?.revision||0)!==input.expectedRevision)throw new Error('A observação mudou; confira a revisão antes de salvar.');
      for(const [name,component] of Object.entries(changes))if(previous?.[name]&&Date.parse(component.observedAt)<Date.parse(previous[name].observedAt))
        throw new Error('Observação anterior à vigente; não substituir silenciosamente '+name+'.');
      const record={...(previous?clone(previous):{}),id:previous?.id||id('fxinstrument'),accountId:input.accountId,periodId:input.periodId,
        instrumentId:key,currency:account.currency,revision:(previous?.revision||0)+1,...changes,recordedAt:now(),previous:previous?clone(previous):null};
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
      const newPeriod=input.newPeriod===true;
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
        periodId:previous&&!newPeriod?previous.periodId:id('fxperiod'),
        recordedAt:now(),previous:previous?clone(previous):null};
      f.accounts[key]=fact;f.activeAccountId=key;
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
  function recordH4(input,{reason}={}){
    if(!input||!finite(input.ddPercent)||input.ddPercent<0||!text(input.source)||
        !Number.isFinite(Date.parse(input.closedAt))||Date.parse(input.closedAt)>Date.now())
      return {ok:false,persistido:false,error:'Registre DD, fonte e fechamento H4 já ocorrido; o relógio não confirma candle.'};
    return mutate('confirmed-h4',reason,[],f=>{
      const closedAt=new Date(input.closedAt).toISOString();
      const account=f.accounts[f.activeAccountId];
      if(!f.activeAccountId||!account||!text(account.periodId))throw new Error('Registre uma conta e seu período antes do fechamento H4.');
      if(f.h4Closes.some(c=>c.closedAt===closedAt&&c.accountId===f.activeAccountId&&c.periodId===account.periodId))throw new Error('Esse fechamento H4 já está registrado para a conta/período.');
      f.h4Closes.push({closedAt,ddPercent:input.ddPercent,source:text(input.source),timeframe:'H4',recordedAt:now(),accountId:f.activeAccountId,periodId:account.periodId});
    });
  }
  function recordGrid(phase,{reason}={}){
    if(!Number.isInteger(phase)||phase<1||phase>6)return {ok:false,persistido:false,error:'Fase da grade inválida.'};
    return mutate('grid-observation',reason,['transitionLog'],f=>{if(!S.activeOperation)throw new Error('Registre a operação antes de declarar sua grade.');
      if(!Array.isArray(S.transitionLog))throw new Error('Histórico de transição incompatível.');
      S.transitionLog.push({at:now(),operationId:S.activeOperation.operationId,gridPhase:phase-1,action:'grid-observation',reason:text(reason),policyVersion:fx.policy.version});
      f.grid={declaredPhase:phase,structureKnown:true,recordedAt:now(),
      operationId:S.activeOperation&&S.activeOperation.operationId||null,previous:f.grid?clone(f.grid):null};});
  }
  function recordReserves(input,{reason}={}){
    const numeric=['capitalNominal','fcrConstituted','feoConstituted','sixMonthExpenseAmount'];
    if(!input||numeric.some(k=>input[k]!=null&&(!finite(input[k])||input[k]<0))||!text(input.source))
      return {ok:false,persistido:false,error:'Informe valores não negativos ou ausentes e a fonte da apuração.'};
    if(input.determinationRecorded&&(!text(input.expensePeriod)||!text(input.determinationReference)))
      return {ok:false,persistido:false,error:'A apuração exige período e referência do método/documento.'};
    return mutate('reserve-observation',reason,[],f=>{
      const account=f.accounts[f.activeAccountId]||null;
      f.reserves={...clone(input),recordedAt:now(),accountId:account?f.activeAccountId:null,
        periodId:account&&text(account.periodId)||null,currency:account&&text(account.currency)||null,
        previous:f.reserves?clone(f.reserves):null};
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
    return same(S.activeOperation)||(S.operationHistory&&Array.isArray(S.operationHistory.records)&&S.operationHistory.records.some(same));
  }
  function budgetCommittedRisk(target){
    // The existing read-model examines the active operation's facts. It cannot
    // serve as historical RC for a different/archived/prospective operation.
    const op=S.activeOperation,c=op&&op.recordContext;
    if(!op||op.operationId!==target.operationId||!c||c.accountId!==target.accountId||c.periodId!==target.periodId||
      !c.accountInputs||c.accountInputs.currency!==target.currency)
      return budgetUnavailable('BUDGET_RC_UNAVAILABLE','Risco comprometido da operação não está apurado neste contexto.');
    const facts=(S.phases||[]).flatMap(p=>p.orders||[]).filter(o=>o&&o.recordStatus!=='voided'&&['Aberta','Fechada','Pendente'].includes(o.status));
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
    const context=recordContext({accountId:input.accountId,periodId:input.periodId});
    if(context.status!=='OK'||!context.accountInputs||context.accountInputs.currency!==input.currency)
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
    recordAccountFacts,selectAccount,recordMarket,recordH4,recordGrid,recordReserves,
    recordInstrumentContext,instrumentContext,recordDailyReferences,dailyReference,dailyReferenceRevision,
    recordOperationBudget,budgetSnapshot,attachOperationBudget,
    editorStatus,configureEditor,unlockEditor,lockEditor,clearEditor,proposeParameterChange,activateProposal,
    supported,unavailable,newOperationPhases:forexNewOperationPhases};
  root.addEventListener('pagehide',clearEditor);
})(globalThis);

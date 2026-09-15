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
  let pending=null, generation=0, busy=false;

  function descriptor(account,index){
    const id=text(account.forexAccountId)||'live:'+index;
    const facts=object(S.forex)&&object(S.forex.accounts)?S.forex.accounts[id]:null;
    return {id,name:text(account.nome),type:text(account.tipo),login:text(account.platformLogin),
      broker:text(account.broker),currency:text(facts&&facts.currency),server:null,
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
  function cancelImport(){pending=null;generation+=1;}
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
  function prepareImport(report,selectionId,meta={}){
    cancelImport();
    const issue=guard();if(issue)return fail(issue);
    const selected=accountSelected(selectionId);
    if(!selected)return fail('Selecione uma conta existente e sem identidade ambígua.');
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
  Object.assign(api,{accounts,prepareImport,confirmImport,saveDefaultAccount,cancelImport});
})(globalThis);

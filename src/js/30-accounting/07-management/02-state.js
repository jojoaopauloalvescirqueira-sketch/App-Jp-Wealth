// MANAGEMENT ANNUAL — plans and immutable annual reports over the canonical
// account ledger. Queries never initialize data. Actual results have one writer.
(function(root){
  'use strict';
  const E=root.JPWAnnualEngine,object=v=>!!v&&typeof v==='object'&&!Array.isArray(v),clone=v=>structuredClone(v),
    text=v=>typeof v==='string'?v.trim():'',finite=v=>typeof v==='number'&&Number.isFinite(v),
    own=(v,k)=>Object.prototype.hasOwnProperty.call(v,k),now=()=>new Date().toISOString(),
    id=prefix=>prefix+'_'+(root.crypto?.randomUUID?.()||Date.now().toString(36)+'_'+Math.random().toString(36).slice(2)),epoch=()=>typeof jpWealthPersistenceEpoch==='function'?jpWealthPersistenceEpoch():null;
  const empty=()=>({schemaVersion:1,revision:0,plans:[],audit:[]});
  const session=id('management_session');let generation=0,tracked=null,unknown=false;
  const document=()=>typeof S!=='undefined'&&object(S)?S:null;
  let initialDocument=document()?clone(document()):null,contextEpoch=epoch();
  function stable(v){if(Array.isArray(v))return '['+v.map(stable).join(',')+']';if(object(v))return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+stable(v[k])).join(',')+'}';return JSON.stringify(v);}
  const canonical=v=>stable(JSON.parse(JSON.stringify(v,(k,value)=>k==='investorPassword'?'':value)));
  function sync(){const doc=document();if(tracked!==null&&tracked!==doc)generation++;tracked=doc;return doc;}
  function envelope(){const doc=sync();return doc&&own(doc,'managementAnnual')?doc.managementAnnual:empty();}
  function requireThat(v,message){if(!v)throw Error(message);}
  function safe(value,seen=new Set()){
    if(value===null||['string','boolean'].includes(typeof value)||finite(value))return;
    requireThat(object(value)||Array.isArray(value),'Entrada inválida; use valores finitos e explícitos.');requireThat(!seen.has(value),'Entrada circular incompatível.');seen.add(value);
    for(const key of Object.keys(value)){requireThat(!/password|passwd|senha|secret|token|credential|authorization|api[-_]?key|private[-_]?key/i.test(key)&&!['__proto__','constructor','prototype'].includes(key),'Campo de segredo ou controle não permitido.');safe(value[key],seen);}seen.delete(value);
  }
  function issues(){try{const value=envelope();requireThat(!!document(),'Documento indisponível.');requireThat(typeof jpwValidateManagementAnnual==='function','Validador de Gerenciamento indisponível.');jpwValidateManagementAnnual({managementAnnual:value});return [];}catch(error){return [error.message];}}
  function context(target={}){
    if(unknown||(typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown()))return {status:'UNKNOWN',value:null,findings:[{code:'WRITE_UNCONFIRMED',message:'Gravação indeterminada. Confira a recuperação antes de usar estes dados como confirmados.'}]};
    if(!text(target.accountId)||!text(target.periodId))return {status:'NOT_COMPUTABLE',value:null,findings:[{code:'CONTEXT_REQUIRED',message:'Selecione conta e período confirmados.'}]};
    try{return clone(root.JPWForex?.state?.accountContext?.({accountId:target.accountId,periodId:target.periodId})||{status:'NOT_COMPUTABLE',value:null,findings:[]});}
    catch(error){return {status:'NOT_COMPUTABLE',value:null,findings:[{code:'CONTEXT_UNAVAILABLE',message:'Não foi possível consultar conta e período.'}]};}
  }
  function findPlan(value,target){return Array.isArray(value?.plans)?value.plans.find(p=>p.accountId===target?.accountId&&p.periodId===target?.periodId&&p.year===target?.year)||null:null;}
  const targetKey=t=>({accountId:text(t?.accountId),periodId:text(t?.periodId),year:t?.year});
  function token(target={}){const value=envelope(),ctx=context(target),plan=findPlan(value,target);return {session,generation,epoch:epoch(),revision:value?.revision??null,...targetKey(target),contextRevision:ctx.status==='OK'?ctx.revision:null,planRevision:plan?.revision??null};}
  function matching(t,target){if(!object(t))return false;const fresh=token(target);return Object.keys(fresh).every(k=>t[k]===fresh[k]);}
  function opening(ctx,startDate){
    const previous=ctx.value.ledger.filter(r=>r.data<startDate).sort((a,b)=>a.data.localeCompare(b.data)).at(-1);
    if(previous)return {kind:'LEDGER',id:previous.id,version:previous.version??0,date:previous.data,balance:previous.saldo,balanceInput:previous.balanceInput||null,currency:ctx.value.currency,accountId:ctx.value.accountId,periodId:ctx.value.periodId};
    return {kind:'PERIOD',date:ctx.value.startedAt,balance:ctx.value.openingBook,currency:ctx.value.currency,accountId:ctx.value.accountId,periodId:ctx.value.periodId,source:ctx.value.source||null,observedAt:ctx.value.observedAt||null};
  }
  function today(){return E.dateKey(new Date());}
  function readModel(plan,ctx,reference){
    requireThat(plan.config.currency===ctx.value.currency,'A moeda do plano difere do período confirmado. Preserve o histórico e revise a origem antes de continuar.');
    const source=opening(ctx,plan.config.startDate),model=E.build(plan.config,{ledger:ctx.value.ledger,declarations:plan.declarations,today:reference||today(),periodStart:ctx.value.startedAt,actualOpeningBalance:source.balance});
    const dependencies=E.dependencies(plan.config,{ledger:ctx.value.ledger,declarations:plan.declarations,openingSource:source}),last=plan.snapshots.at(-1);
    return {model,openingSource:source,dependencies,closureStatus:last?(last.dependencies===dependencies?'CONFIRMED':'RECONFIRM_REQUIRED'):'OPEN'};
  }
  function model(target={}){
    const invalid=issues(),value=envelope(),ctx=context(target),plan=findPlan(value,target);
    if(invalid.length)return {ok:false,status:'INVALID',errors:invalid,plan:null,model:null};
    if(ctx.status!=='OK')return {ok:false,status:ctx.status==='UNKNOWN'?'UNKNOWN':'INVALID',errors:[ctx.status==='UNKNOWN'?'Gravação indeterminada; confira a recuperação antes de usar os dados como confirmados.':'Selecione conta e período confirmados.'],plan:clone(plan),model:null,token:token(target)};
    if(!plan)return {ok:false,status:'NO_PLAN',errors:[],plan:null,model:null,token:token(target)};
    try{const data=readModel(plan,ctx,target.today);return {ok:data.model.ok,status:data.model.ok?'OK':'INVALID',errors:data.model.errors||[],plan:clone(plan),...data,snapshots:clone(plan.snapshots),token:token(target)};}
    catch(error){return {ok:false,status:'INVALID',errors:[error.message],plan:clone(plan),model:null,token:token(target)};}
  }
  function previewPlan(input={}){
    try{safe(input);requireThat(!issues().length,issues().join(' '));const ctx=context(input);requireThat(ctx.status==='OK','Selecione conta e período confirmados.');
      const source=opening(ctx,input.startDate);requireThat(finite(source.balance)&&source.balance>0,'Saldo inicial confirmado indisponível ou não positivo. Consulte a origem antes de planejar.');
      const config={accountId:input.accountId,periodId:input.periodId,year:input.year,startDate:input.startDate,initialBalance:source.balance,currency:ctx.value.currency,
        annualTarget:input.annualTarget,daysPerWeek:input.daysPerWeek,monthsPerYear:input.monthsPerYear,excludedDates:clone(input.excludedDates||[]),referenceYears:input.referenceYears===undefined?1:input.referenceYears,referenceDays:input.referenceDays===undefined?364:input.referenceDays};
      const errors=E.validateConfig(config);requireThat(!errors.length,errors.join(' '));requireThat(new Set(config.excludedDates).size===config.excludedDates.length,'As datas excluídas não podem estar repetidas.');requireThat(config.startDate>=ctx.value.startedAt,'O início do plano não pode anteceder o período confirmado.');
      const prior=findPlan(envelope(),input),declarations=prior?.declarations||[];
      requireThat(!declarations.some(d=>d.date<config.startDate),'Existem declarações anteriores ao novo início. Preserve o histórico e mantenha a data de início compatível.');
      const result=E.build(config,{ledger:ctx.value.ledger,declarations,today:today(),periodStart:ctx.value.startedAt,actualOpeningBalance:source.balance});requireThat(result.ok,(result.errors||[]).join(' '));
      return {ok:true,status:'PREVIEW',errors:[],config,openingSource:source,model:result,token:token(input)};
    }catch(error){return {ok:false,status:'INVALID',errors:[error.message]};}
  }
  function previewResult(input={}){
    try{safe(input);const target=input.target||{},read=model(target);requireThat(read.ok,'Configure o plano e confirme conta e período antes de registrar.');const ctx=context(target),date=E.dateKey(input.date);
      requireThat(date===input.date&&date>=read.plan.config.startDate&&date.slice(0,4)===String(target.year),'Data fora do ano ou início do plano.');requireThat(date<=today(),'Resultados reais não podem ser registrados em dias futuros.');requireThat(finite(input.value),'Informe resultado numérico finito. Campo vazio não é zero.');requireThat(!own(input,'note')||typeof input.note==='string'&&input.note.length<=500&&!/[\u0000-\u001f\u007f]/.test(input.note),'A observação deve ser texto de até 500 caracteres, sem controles.');
      const previous=ctx.value.ledger.filter(r=>r.data<date).sort((a,b)=>a.data.localeCompare(b.data)).at(-1),existing=ctx.value.ledger.find(r=>r.data===date)||null;
      requireThat(input.id?existing&&existing.id===input.id:!existing,'A data já tem fechamento ou o identificador mudou. Revise o registro existente.');
      requireThat(!read.plan.declarations.some(d=>d.date===date),'Este dia tem declaração sem resultado. Revise a declaração antes de registrar um resultado.');
      const start=previous?.saldo??ctx.value.openingBook;requireThat(finite(start),'Saldo de abertura confirmado indisponível.');
      const closing=existing?.balanceInput==='OBSERVED'?existing.saldo:start+input.value;requireThat(finite(closing),'Saldo de fechamento não calculável.');
      return {ok:true,status:'PREVIEW',errors:[],opening:start,result:input.value,closing,existingRecord:clone(existing),date,currency:ctx.value.currency,
        affectedDates:ctx.value.ledger.filter(r=>r.data>date&&r.balanceInput==='DERIVED_FROM_PREVIOUS').map(r=>r.data).sort(),token:token(target)};
    }catch(error){return {ok:false,status:'INVALID',errors:[error.message]};}
  }
  function previewAnnualClose(target={}){
    const read=model(target);if(!read.ok)return {...read,ok:false};const errors=[];
    if(today()<=String(target.year)+'-12-31')errors.push('O fechamento anual fica disponível após 31/12.');
    if(!read.model.readyForAnnualClose)errors.push('Resolva os dias pendentes e confira os registros antes de fechar o ano.');
    if(read.closureStatus==='CONFIRMED')errors.push('Este retrato anual já está confirmado e atualizado.');
    return {...read,ok:errors.length===0,status:errors.length?'INVALID':'PREVIEW',errors};
  }
  function response(status,errors=[],extra={}){return {ok:status==='CONFIRMED',status,errors,...extra};}
  function blocked(target,t){
    sync();if(unknown||(typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown()))return response('UNKNOWN',['Gravação indeterminada. Confira a recuperação antes de repetir.']);
    const invalid=issues();if(invalid.length)return response('INVALID',invalid);
    if(!matching(t,target))return response('CONFLICT',['A base, a conta, o período ou a revisão mudou. Atualize a revisão sem descartar o rascunho.']);
    try{const confirmed=typeof jpWealthConfirmedStateSnapshot==='function'?jpWealthConfirmedStateSnapshot():null;
      if(canonical(document())!==canonical(confirmed||initialDocument))return response('CONFLICT',['Há dados não confirmados na memória. Resolva sua gravação antes de confirmar esta ação.']);}
    catch(error){return response('CONFLICT',['Não foi possível conferir o documento confirmado. Preserve o rascunho.']);}
    return null;
  }
  function markUnknown(message){unknown=true;generation++;if(typeof markJPWealthPersistenceOutcomeUnknown==='function'&&!(typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown()))markJPWealthPersistenceOutcomeUnknown(message);return response('UNKNOWN',['Gravação indeterminada. Preserve o rascunho e confira a recuperação; não repita automaticamente.']);}
  function persist(target,t,type,fn,reason=''){
    const refusal=blocked(target,t);if(refusal)return refusal;
    try{const candidate=clone(document()),value=clone(envelope()),at=now(),changed=fn(value,at);value.revision++;value.audit.push({id:id('management_audit'),at,type,planId:changed.id,reason:text(reason),...(changed.auditBefore?{before:changed.auditBefore}:{})});delete changed.auditBefore;candidate.managementAnnual=value;jpwValidateManagementAnnual(candidate);
      requireThat(typeof jpWealthPersistDocument==='function'&&epoch()!==null,'Escritor confirmado indisponível.');let written;
      try{written=jpWealthPersistDocument(candidate,{expectedEpoch:t.epoch,component:'managementAnnual'});}catch(error){return markUnknown('Gerenciamento: escritor interrompido.');}
      if(written?.status==='CONFIRMED'){S=candidate;tracked=candidate;initialDocument=clone(candidate);contextEpoch=epoch();return response('CONFIRMED',[],{planId:changed.id,token:token(target)});}
      generation++;if(written?.status==='REFUSED')return response(written.reason==='CONFLICT'?'CONFLICT':'REFUSED',['A gravação foi recusada. Preserve o preenchimento e atualize a revisão.']);return markUnknown('Gerenciamento: confirmação indisponível.');
    }catch(error){return response('INVALID',[error.message]);}
  }
  function savePlan(input={},options={}){
    const refusal=blocked(input,options.token);if(refusal)return refusal;const preview=previewPlan(input);if(!preview.ok)return response('INVALID',preview.errors);
    if(options.confirmOpening!==true)return response('INVALID',['Confira e confirme o saldo inicial e sua origem.']);
    return persist(input,options.token,'PLAN_SAVED',(value,at)=>{let plan=findPlan(value,input);if(!plan){plan={id:id('management_plan'),...targetKey(input),revision:0,createdAt:at,updatedAt:at,config:null,openingSource:null,history:[],declarations:[],snapshots:[]};value.plans.push(plan);}
      plan.revision++;plan.updatedAt=at;plan.config=clone(preview.config);plan.openingSource=clone(preview.openingSource);plan.history.push({revision:plan.revision,at,config:clone(plan.config),openingSource:clone(plan.openingSource),reason:text(options.reason)});return plan;},options.reason);
  }
  function canonicalResult(input,options,action){
    const target=input?.target||{},refusal=blocked(target,options.token);if(refusal)return refusal;
    if(options.confirm!==true)return response('INVALID',['Revise e confirme o fechamento explicitamente.']);
    if(!text(options.reason))return response('INVALID',['Informe o motivo do registro, correção ou anulação.']);
    const ctx=context(target);if(ctx.status!=='OK')return response('INVALID',['Conta ou período indisponíveis.']);
    let payload;
    if(action==='VOIDED'){const read=model(target),row=ctx.value.ledger.find(r=>r.id===input.id);if(!read.ok||!row||row.data<read.plan.config.startDate||row.data.slice(0,4)!==String(target.year))return response('INVALID',['Fechamento não pertence ao contexto do plano.']);payload={action,id:row.id,accountId:target.accountId,periodId:target.periodId};}
    else {const preview=previewResult(input);if(!preview.ok)return response('INVALID',preview.errors);payload={action:preview.existingRecord?'CORRECTED':'RECORDED',id:preview.existingRecord?.id||null,accountId:target.accountId,periodId:target.periodId,data:input.date,resultado:input.value,saldo:preview.existingRecord?.balanceInput==='OBSERVED'?preview.existingRecord.saldo:null,nota:own(input,'note')?input.note:preview.existingRecord?.nota||''};}
    let written;try{written=root.JPWForex.state.recordAccountLedger(payload,{reason:options.reason,expectedRevision:ctx.revision,expectedEpoch:options.token.epoch});}catch(error){return markUnknown('Gerenciamento: fechamento interrompido.');}
    if(written?.ok===true&&written.persistido===true)return response('CONFIRMED',[],{token:token(target)});
    generation++;if(written?.persistido===false)return response('REFUSED',[written.error||'O fechamento não foi confirmado.']);return markUnknown('Gerenciamento: fechamento sem confirmação.');
  }
  function declareNoResult(input={},options={}){
    const target=input.target||{},refusal=blocked(target,options.token);if(refusal)return refusal;
    try{safe(input);const read=model(target);requireThat(read.ok,'Configure o plano antes de declarar.');requireThat(options.confirm===true&&text(options.reason),'Confirme explicitamente que não houve resultado realizado neste dia e informe o motivo.');
      requireThat(E.dateKey(input.date)===input.date&&input.date>=read.plan.config.startDate&&input.date.slice(0,4)===String(target.year)&&input.date<=today(),'Data fora do plano ou futura.');
      requireThat(!context(target).value.ledger.some(r=>r.data===input.date),'Existe fechamento real nesta data; a declaração não poderá contradizê-lo.');
      requireThat(!read.plan.declarations.some(d=>d.date===input.date),'Este dia já tem declaração.');
      return persist(target,options.token,'NO_RESULT_DECLARED',(value,at)=>{const plan=findPlan(value,target);plan.declarations.push({date:input.date,kind:'NO_RESULT',reason:text(options.reason),at,revision:1});return plan;},options.reason);
    }catch(error){return response('INVALID',[error.message]);}
  }
  function revokeNoResult(input={},options={}){
    const target=input.target||{},refusal=blocked(target,options.token);if(refusal)return refusal;
    try{safe(input);const read=model(target);requireThat(read.ok,'Configure o plano antes de corrigir a declaração.');
      requireThat(options.confirm===true&&text(options.reason),'Confirme a retirada da declaração e informe o motivo.');
      const previous=read.plan.declarations.find(d=>d.date===input.date);requireThat(!!previous,'Declaração não encontrada nesta data.');
      return persist(target,options.token,'NO_RESULT_REVOKED',(value)=>{const plan=findPlan(value,target);plan.declarations=plan.declarations.filter(d=>d.date!==input.date);plan.auditBefore=clone(previous);return plan;},options.reason);
    }catch(error){return response('INVALID',[error.message]);}
  }
  function closeAnnual(target={},options={}){
    const refusal=blocked(target,options.token);if(refusal)return refusal;const preview=previewAnnualClose(target);if(!preview.ok)return response('INVALID',preview.errors);
    if(options.confirm!==true)return response('INVALID',['Confira os registros e confirme o retrato anual explicitamente.']);
    return persist(target,options.token,'ANNUAL_CLOSED',(value,at)=>{const plan=findPlan(value,target);plan.snapshots.push({id:id('management_snapshot'),at,planRevision:plan.revision,dependencies:preview.dependencies,summary:clone(preview.model.summary),rows:clone(preview.model.rows)});return plan;},'Retrato anual conferido e confirmado.');
  }
  function resetContext(){
    // Ordinary writes may replace S without replacing the user's workspace.
    // Only a verified epoch change or explicit recovery clears ephemeral UI.
    try{const doc=document(),currentEpoch=epoch(),confirmed=typeof jpWealthConfirmedStateSnapshot==='function'?jpWealthConfirmedStateSnapshot():null;
      if((typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown())||!doc||!confirmed||canonical(confirmed)!==canonical(doc))return false;
      if(!unknown&&currentEpoch===contextEpoch)return false;
      generation++;unknown=false;initialDocument=clone(confirmed);tracked=doc;contextEpoch=currentEpoch;return true;
    }catch(error){return false;}
  }
  root.JPWManagementAnnual={queries:{context,token,model,previewPlan,previewResult,previewAnnualClose,listPlans(target={}){if(issues().length)return [];return clone(envelope().plans.filter(p=>(!target.accountId||p.accountId===target.accountId)&&(!target.periodId||p.periodId===target.periodId)));},snapshot:()=>clone(envelope())},
    commands:{savePlan,recordResult:(input,options={})=>canonicalResult(input,options,'RECORDED'),voidResult:(input,options={})=>canonicalResult(input,options,'VOIDED'),declareNoResult,revokeNoResult,closeAnnual,resetContext},
    resetContext,invalidate(){generation++;}};
})(globalThis);

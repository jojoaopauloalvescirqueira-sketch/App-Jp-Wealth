// PLANNING — optional aggregate, explicit commands and confirmed document writer.
// Reads never create/migrate data. A candidate is adopted only after read-back.
(function(root){
  'use strict';
  const planning=root.JPWPlanning=root.JPWPlanning||{};
  const engine=planning.engine;
  const object=value=>!!value&&typeof value==='object'&&!Array.isArray(value);
  const clone=value=>structuredClone(value);
  const text=value=>typeof value==='string'?value.trim():'';
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const own=(value,key)=>Object.prototype.hasOwnProperty.call(value,key);
  const now=()=>new Date().toISOString();
  const identity=prefix=>prefix+'_'+(root.crypto?.randomUUID?.()||Date.now().toString(36)+'_'+Math.random().toString(36).slice(2));
  const empty=()=>({schemaVersion:1,revision:0,accounts:[],archive:[],audit:[],operations:[]});
  const money=(value,signed=false)=>finite(value)&&(signed||value>=0)&&Number.isSafeInteger(Math.round(value*100))&&Math.abs(value*100-Math.round(value*100))<1e-7;
  const premiseAmount=value=>finite(value)&&value>=0&&Number.isSafeInteger(Math.round(value*100));
  const secretKey=key=>/password|passwd|senha|secret|token|credential|authorization|api[-_]?key|private[-_]?key/i.test(key);
  let generation=0,trackedRoot=null,trackedAggregate=null,unknown=false;
  const session=identity('planning_session');
  const state=()=>typeof S!=='undefined'&&object(S)?S:null;
  const epoch=()=>typeof jpWealthPersistenceEpoch==='function'?jpWealthPersistenceEpoch():null;
  let emptyContextBaseline=state()?clone(state()):null,contextEpoch=epoch();
  const canonicalDocument=value=>stable(JSON.parse(JSON.stringify(value,(key,item)=>key==='investorPassword'?'':item)));
  function resetContext(){
    const document=state(),confirmed=typeof jpWealthConfirmedStateSnapshot==='function'?jpWealthConfirmedStateSnapshot():null;
    if(!document||(typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown()))return false;
    if(confirmed&&canonicalDocument(document)!==canonicalDocument(confirmed))return false;
    if(!confirmed&&canonicalDocument(document)!==canonicalDocument(emptyContextBaseline)){
      const defaults=typeof DEFAULTS!=='undefined'?DEFAULTS:null;
      if(!defaults||canonicalDocument(document)!==canonicalDocument(defaults))return false;
    }
    const changed=trackedRoot!==null&&(trackedRoot!==document||trackedAggregate!==document.patrimonialPlanning)||contextEpoch!==epoch();
    if(changed)generation++;
    trackedRoot=document;trackedAggregate=document.patrimonialPlanning;contextEpoch=epoch();emptyContextBaseline=clone(document);
    if(confirmed)unknown=false;
    return changed;
  }
  function sync(){
    const document=state(),aggregate=document?.patrimonialPlanning;
    if(trackedRoot!==null&&(trackedRoot!==document||trackedAggregate!==aggregate))generation++;
    trackedRoot=document;trackedAggregate=aggregate;
    return document;
  }
  function adopt(document){S=document;trackedRoot=document;trackedAggregate=document.patrimonialPlanning;emptyContextBaseline=clone(document);contextEpoch=epoch();}
  function envelope(){const document=sync();return document&&own(document,'patrimonialPlanning')?document.patrimonialPlanning:empty();}
  function errorsFor(value){
    if(!engine||typeof engine.validateEnvelope!=='function')return ['Motor de planejamento indisponível.'];
    try{return engine.validateEnvelope(value);}catch(error){return ['Agregado de planejamento incompatível.'];}
  }
  function accountById(value,id){return Array.isArray(value?.accounts)?value.accounts.find(account=>account.id===id)||null:null;}
  function currentMonth(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');}
  function requireThat(condition,message){if(!condition)throw new Error(message);}
  function assertSafeInput(value,seen=new Set()){
    if(value==null||typeof value!=='object'){
      requireThat(value==null||['string','boolean'].includes(typeof value)||finite(value),'Entrada não serializável.');return;
    }
    requireThat(!seen.has(value),'Entrada circular incompatível.');seen.add(value);
    for(const key of Object.keys(value)){
      requireThat(!secretKey(key)&&!['__proto__','prototype','constructor'].includes(key),'Segredos e campos de controle não são permitidos.');
      assertSafeInput(value[key],seen);
    }
    seen.delete(value);
  }
  function sanitizeLegacy(value,seen=new Set()){
    if(value===null||typeof value!=='object')return value;
    if(seen.has(value))return '[circular]';seen.add(value);
    const result=Array.isArray(value)?[]:{};
    for(const key of Object.keys(value))if(!secretKey(key)&&!['__proto__','prototype','constructor'].includes(key))result[key]=sanitizeLegacy(value[key],seen);
    seen.delete(value);return result;
  }
  function quoteSnapshot(value){
    if(!object(value)||value.status==='unavailable'||!finite(value.rate)||value.rate<=0||!text(value.source)||
      !/^\d{4}-\d{2}-\d{2}$/.test(value.referenceDate||''))return null;
    const economic=new Date(value.referenceDate+'T00:00:00.000Z');
    if(!Number.isFinite(economic.getTime())||economic.toISOString().slice(0,10)!==value.referenceDate)return null;
    const fetched=typeof value.fetchedAt==='number'?new Date(value.fetchedAt):new Date(value.fetchedAt||'');
    if(!Number.isFinite(fetched.getTime())||value.referenceDate>fetched.toISOString().slice(0,10)||fetched.getTime()>Date.now()+60000)return null;
    return {rate:value.rate,referenceDate:value.referenceDate,fetchedAt:fetched.toISOString(),source:text(value.source)};
  }
  function publicQuote(){
    try{return quoteSnapshot(typeof getCurrentUsdBrlQuote==='function'?getCurrentUsdBrlQuote():root.JPWMarket?.usdBrl?.get?.());}catch(error){return null;}
  }
  function closureQuote(month){
    if(month===currentMonth())return publicQuote();
    try{
      const quote=quoteSnapshot(root.JPWMarket?.usdBrl?.getHistorical?.(month));
      return quote&&quote.referenceDate<engine.addMonths(month,1)+'-01'?quote:null;
    }catch(error){return null;}
  }
  function goal(input,required){
    if(!required&&(input==null||input===''))return null;
    requireThat(object(input)&&premiseAmount(input.value)&&input.value>0&&['USD','BRL'].includes(input.currency),'Revise o valor e a moeda da meta.');
    const current=input.currency==='BRL'?publicQuote():null;
    const quote=input.currency==='BRL'&&own(input,'quote')?quoteSnapshot(input.quote):current;
    requireThat(input.currency!=='BRL'||!!current&&!!quote&&Date.now()-Date.parse(quote.fetchedAt)<=24*60*60*1000&&Date.now()-Date.parse(current.fetchedAt)<=24*60*60*1000,'Meta em BRL exige consulta USD/BRL nas últimas 24 horas, com origem e data. Atualize a referência; metas já preservadas continuam disponíveis offline.');
    requireThat(input.currency!=='BRL'||Math.abs(current.rate-quote.rate)<=1e-8&&current.referenceDate===quote.referenceDate&&current.source===quote.source,'A cotação mudou após a revisão. Atualize a cotação desta renda e confira novamente antes de confirmar.');
    const usd=Math.round(input.value/(input.currency==='USD'?1:quote.rate)*100)/100;
    requireThat(finite(usd)&&usd>0,'Meta em USD não calculável.');
    return {value:input.value,currency:input.currency,usd,quote};
  }
  const configKeys=['name','broker','login','server','startMonth','initialUsd','profileId','monthlyContributionUsd','goals','stopAfter','stopImpactLimit'];
  function configuration(input,previous){
    requireThat(object(input),'Informe a configuração do plano.');
    requireThat(Object.keys(input).every(key=>configKeys.includes(key)),'Configuração contém campos não permitidos.');
    const base=previous?{name:previous.name,broker:previous.broker,login:previous.login,server:previous.server,
      startMonth:previous.plan.startMonth,initialUsd:previous.plan.initialUsd,profileId:previous.plan.profileId,
      monthlyContributionUsd:previous.plan.monthlyContributionUsd,goals:previous.plan.goals}:{};
    const c={...base,...input};
    requireThat(c.name==null||typeof c.name==='string','Campos de identificação devem ser texto.');
    c.name=text(c.name)||'Conta de investimento';
    requireThat(c.name.length<=120,'Informe um nome de conta com até 120 caracteres.');
    for(const key of ['name','broker','login','server']){
      requireThat(c[key]==null||typeof c[key]==='string','Campos de identificação devem ser texto.');
      c[key]=text(c[key]);requireThat(c[key].length<=200&&!/[\u0000-\u001f\u007f]/.test(c[key]),'Identificação contém texto inválido.');
    }
    requireThat(engine.monthKey(c.startMonth)===c.startMonth,'Mês inicial inválido.');
    requireThat(premiseAmount(c.initialUsd)&&premiseAmount(c.monthlyContributionUsd),'Capital e aporte previsto devem ser USD não negativos e finitos.');
    requireThat(object(c.goals),'Informe as metas do plano.');
    // Existing goal snapshots survive metadata edits without fetching a new rate.
    const unchanged=(next,prior)=>prior&&next&&next.refreshQuote!==true&&next.value===prior.value&&next.currency===prior.currency;
    c.goals={adequate:previous&&unchanged(c.goals.adequate,previous.plan.goals.adequate)?clone(previous.plan.goals.adequate):goal(c.goals.adequate,false),
      ideal:previous&&unchanged(c.goals.ideal,previous.plan.goals.ideal)?clone(previous.plan.goals.ideal):goal(c.goals.ideal,true)};
    return c;
  }
  function token(accountId){
    const value=envelope(),account=accountById(value,accountId);
    return {session,generation,epoch:epoch(),revision:value?.revision??null,accountId:accountId||null,
      planId:account?.plan?.id||null,planRevision:account?.plan?.revision??null};
  }
  function targetMatches(t,value,accountId,allowOldRevision=false){
    const account=accountById(value,accountId);
    return object(t)&&t.session===session&&t.generation===generation&&t.epoch===epoch()&&
      t.accountId===(accountId||null)&&t.planId===(account?.plan?.id||null)&&
      (allowOldRevision||t.revision===value.revision&&t.planRevision===(account?.plan?.revision??null));
  }
  function monthInPlan(plan,month,{future=false}={}){
    requireThat(engine.monthKey(month)===month&&month>=plan.startMonth&&month<=engine.addMonths(plan.startMonth,119),'Mês fora do horizonte do plano.');
    requireThat(future?month>currentMonth():month<=currentMonth(),future?'A projeção só altera meses futuros.':'Registros confirmados não podem usar meses futuros.');
    return month;
  }
  function history(plan,type,at,before,after,reason){
    plan.history.push({id:identity('planning_history'),type,at,reason:reason||'',before:before==null?null:clone(before),after:after==null?null:clone(after)});
  }
  function reopenDependents(plan,month,at,reason){
    for(const key of Object.keys(plan.closures).sort())if(key>=month&&plan.closures[key]?.confirmed===true){
      const previous=clone(plan.closures[key]);
      plan.closures[key]={...previous,confirmed:false,revision:previous.revision+1,reopenedAt:at,reason,previous};
      history(plan,'closure-reopened',at,{month:key,...previous},{month:key,...plan.closures[key]},reason);
    }
  }
  function recalculate(plan){
    const rows=engine.timeline(plan,{month:currentMonth(),quote:publicQuote()});
    requireThat(Array.isArray(rows)&&rows.length===120,'Calendário do plano não calculável.');
    for(const row of rows){
      requireThat(finite(row.openUsd)&&finite(row.closeUsd)&&row.closeUsd>=0,'Os registros produzem saldo negativo ou saldo não calculável.');
      const facts=own(plan.results,row.month)||plan.contributions.some(item=>item.month===row.month&&item.usd!==0)||
        plan.withdrawals.some(item=>item.month===row.month&&item.usd!==0)||plan.closures[row.month]?.confirmed===true;
      if(!facts)continue;
      requireThat(row.openUsd!==0||!own(plan.results,row.month)||plan.results[row.month].usd===0,'Resultado diferente de zero exige saldo de abertura positivo.');
    }
    return rows;
  }
  function applyFlow(plan,kind,input,at){
    requireThat(['result','contribution','withdrawal'].includes(kind),'Escolha o tipo de registro.');
    const month=monthInPlan(plan,input.month);
    if(kind==='result'){
      requireThat(money(input.usd,true),'Resultado deve ser o total em USD com centavos.');
      const previous=plan.results[month]||null;
      plan.results[month]={usd:input.usd,revision:(previous?.revision||0)+1,recordedAt:at,...(previous?{previous:clone(previous)}:{})};
      history(plan,'result-recorded',at,{month,value:previous},{month,value:plan.results[month]});return month;
    }
    const key=kind==='contribution'?'contributions':'withdrawals',items=plan[key],index=input.id==null?-1:items.findIndex(item=>item.id===input.id);
    requireThat(input.id==null||index>=0,'Lançamento original não encontrado.');
    const previous=index>=0?items[index]:null;
    requireThat(!previous||previous.month===month,'A correção deve preservar o mês do lançamento original.');
    requireThat(money(input.usd)&&(input.usd>0||!!previous),'Informe USD positivo ou zero para anular um lançamento existente.');
    if(kind==='contribution')requireThat(money(input.brl)&&(input.usd===0?input.brl===0:input.brl>0),'Aporte exige USD e BRL pagos positivos; anulação usa zero nas duas moedas.');
    else requireThat(input.brl===undefined||input.brl===null||money(input.brl)&&(input.usd===0?input.brl===0:input.brl>0),'BRL recebido inválido.');
    const item={...(previous||{}),id:previous?.id||identity('planning_flow'),month,usd:input.usd,revision:(previous?.revision||0)+1,recordedAt:at,
      ...(input.brl!==undefined&&input.brl!==null?{brl:input.brl}:{}),...(previous?{previous:clone(previous)}:{})};
    if(kind==='withdrawal'&&(input.brl===undefined||input.brl===null))delete item.brl;
    if(index<0)items.push(item);else items[index]=item;
    history(plan,kind==='contribution'?'contribution-recorded':'withdrawal-recorded',at,previous,item,input.reason);
    return month;
  }
  function previewFlow(input={}){
    try{
      assertSafeInput(input);const value=envelope(),issues=errorsFor(value);requireThat(!issues.length,issues.join(' '));
      const account=clone(accountById(value,input.accountId));requireThat(account&&account.active===true,'Conta ativa de planejamento não encontrada.');
      const changed=applyFlow(account.plan,input.kind,input,now());
      reopenDependents(account.plan,changed,now(),'Correção factual exige reconferência dos meses dependentes.');
      const row=recalculate(account.plan).find(item=>item.month===input.month);
      requireThat(!!row,'O mês não pertence ao plano desta conta.');
      const key=input.kind==='contribution'?'contributions':'withdrawals';
      const total=input.kind==='result'?row.resultUsd:account.plan[key].filter(item=>item.month===input.month).reduce((sum,item)=>sum+item.usd,0);
      return {ok:true,status:'PREVIEW',errors:[],row:clone(row),rate:row.rate,monthTotalUsd:total,
        ...(input.kind==='contribution'&&input.usd>0?{paidRate:input.brl/input.usd}:{})};
    }catch(error){return {ok:false,status:'INVALID',errors:[error.message||'Prévia do registro indisponível.']};}
  }
  function previewResultInput(input={}){
    try{
      requireThat(object(input),'Informe os dados do resultado.');assertSafeInput(input);
      requireThat(['PERCENT','USD'].includes(input.unit),'Escolha percentual ou USD para o resultado.');
      requireThat(finite(input.value),'Informe um resultado numérico finito; vazio não equivale a zero.');
      const value=envelope(),issues=errorsFor(value);requireThat(!issues.length,issues.join(' '));
      const account=clone(accountById(value,input.accountId));requireThat(account&&account.active===true,'Conta ativa de planejamento não encontrada.');
      monthInPlan(account.plan,input.month);
      const row=engine.timeline(account.plan,{month:currentMonth(),quote:publicQuote()}).find(item=>item.month===input.month);
      requireThat(!!row,'O mês não pertence ao plano desta conta.');
      requireThat(input.unit!=='PERCENT'||finite(row.openUsd)&&row.openUsd>0,'Resultado percentual exige saldo de abertura disponível e positivo.');
      const usd=input.unit==='PERCENT'?Math.round(row.openUsd*(input.value/100)*100)/100:input.value;
      return {...previewFlow({accountId:input.accountId,month:input.month,kind:'result',usd}),openUsd:row.openUsd,inputUnit:input.unit,inputValue:input.value};
    }catch(error){return {ok:false,status:'INVALID',errors:[error.message||'Prévia do resultado indisponível.']};}
  }
  function archivePlan(value,account,at,scope){
    const full=clone(account),plan=full.plan;delete full.plan;
    value.archive.push({id:identity('planning_archive'),accountId:account.id,reason:'restartPlan',resetScope:scope,archivedAt:at,account:full,plan});
  }
  function resetPreview(value,accountId,scope){
    requireThat(scope==='CONTA'||scope==='TODAS','Escolha o alcance do reinício.');
    const chosen=accountById(value,accountId);requireThat(chosen&&chosen.active===true,'Selecione uma conta ativa para reiniciar.');
    const targets=(scope==='TODAS'?value.accounts.filter(account=>account.active===true):[chosen]);
    const identified=targets.map(account=>{const label='C'+String(value.accounts.indexOf(account)+1).padStart(3,'0');return {id:account.id,name:account.name,label:label+' · '+account.name,code:label};});
    const counts=targets.reduce((sum,account)=>{
      sum.closed+=Object.values(account.plan.closures).filter(item=>item.confirmed===true).length;
      sum.contributions+=account.plan.contributions.filter(item=>item.usd>0).length;
      sum.results+=Object.keys(account.plan.results).length;
      sum.withdrawals+=account.plan.withdrawals.filter(item=>item.usd>0).length;return sum;
    },{closed:0,contributions:0,results:0,withdrawals:0});
    return {ok:true,status:'PREVIEW',errors:[],scope,accountId,phrase:scope==='TODAS'?'REINICIAR TUDO':'REINICIAR '+identified[0].code,targets:identified,counts};
  }
  function previewReset({accountId,scope='CONTA'}={}){
    try{const value=envelope(),issues=errorsFor(value);requireThat(!issues.length,issues.join(' '));return resetPreview(value,accountId,scope);}
    catch(error){return {ok:false,status:'INVALID',errors:[error.message||'Prévia do reinício indisponível.']};}
  }
  function stable(value){
    if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
    if(object(value))return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+stable(value[key])).join(',')+'}';
    return JSON.stringify(value);
  }
  const result=(status,errors=[],details={})=>({ok:status==='CONFIRMED',status,errors,...details});
  function execute(type,payload,t){
    const document=sync(),value=envelope();
    if(unknown||(typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown()))return result('UNKNOWN',['Gravação indeterminada; confira a recuperação antes de repetir.']);
    const incompatibility=errorsFor(value);
    if(!document||incompatibility.length)return result('INVALID',incompatibility.length?incompatibility:['Documento principal indisponível.']);
    if(!object(payload))return result('INVALID',['Informe os dados do comando.']);
    const accountId=type==='createAccount'?null:payload.accountId;
    const target=accountById(value,accountId);
    try{assertSafeInput(payload);}catch(error){return result('INVALID',[error.message]);}
    let clean,signature;
    try{clean=clone(payload);delete clean.operationId;signature=stable({type,payload:clean});}
    catch(error){return result('INVALID',['Entrada de planejamento não serializável.']);}
    if(own(payload,'operationId')){
      const known=value.operations.find(operation=>operation.id===payload.operationId);
      if(!known)return result('INVALID',['Identificador de operação desconhecido.']);
      const originalToken=object(t)&&object(known.base)&&t.session===session&&t.generation===generation&&t.epoch===epoch()&&
        ['epoch','revision','accountId','planId','planRevision'].every(key=>known.base[key]===t[key]);
      const outcomeAccount=accountById(value,known.accountId);
      if(known.signature!==signature||!(targetMatches(t,value,accountId,true)||originalToken)||known.planId!==outcomeAccount?.plan?.id||
        accountId&&known.targetPlanId!==undefined&&known.targetPlanId!==target?.plan?.id)return result('CONFLICT',['A operação ou seu destino mudou; reveja os dados.']);
      return clone(known.result);
    }
    if(!targetMatches(t,value,accountId))return result('CONFLICT',['A base, a conta ou o plano mudou; revise o rascunho antes de salvar.']);
    if(type!=='createAccount'&&(!target||target.active!==true))return result('INVALID',['Conta ativa de planejamento não encontrada.']);
    // A planning confirmation cannot also confirm unrelated or unconfirmed RAM.
    if(typeof jpWealthConfirmedStateSnapshot==='function'){
      const confirmedDocument=jpWealthConfirmedStateSnapshot()||emptyContextBaseline;
      if(confirmedDocument){
        try{if(canonicalDocument(document)!==canonicalDocument(confirmedDocument))return result('CONFLICT',['Há alterações não confirmadas no documento atual. Preserve esse preenchimento e resolva sua gravação antes de confirmar o plano.']);}
        catch(error){return result('INVALID',['Não foi possível conferir o documento confirmado. Preserve o rascunho.']);}
      }
    }
    let candidate,next;
    try{candidate=clone(document);next=clone(value);}catch(error){return result('INVALID',['Documento principal não pode ser copiado com segurança.']);}
    const at=now(),operationId=identity('planning_operation');
    let account=accountById(next,accountId),changedMonth=null,requiresConfiguration=false;
    try{
      if(type==='createAccount'){
        const c=configuration(clean),plan=engine.createPlan(c,{id:identity('planning_plan'),now:at});
        applyConfigStop(plan,c,at,true);
        // A full reset reserves the original primary identity until this explicit
        // form confirmation; there is no active account with fabricated premises.
        const reserved=next.pendingConfiguration&&accountById(next,next.pendingConfiguration.accountId);
        if(reserved){account=reserved;Object.assign(account,{name:c.name,broker:c.broker,login:c.login,server:c.server,active:true,plan});delete next.pendingConfiguration;}
        else {account={id:identity('planning_account'),name:c.name,broker:c.broker,login:c.login,server:c.server,active:true,plan};next.accounts.push(account);}
      }else if(type==='updateAccount'){
        reviseAccount(account,clean.config,clean.replaceFuture,at,true);
      }else if(type==='setProjection'){
        const p=account.plan,month=monthInPlan(p,clean.month,{future:true});
        requireThat(clean.rate===null||finite(clean.rate)&&clean.rate>=-1,'Taxa futura inválida.');
        requireThat(clean.contributionUsd===''||premiseAmount(clean.contributionUsd),'Aporte futuro deve ser vazio ou USD não negativo e finito.');
        const previous=p.future[month]||null;p.future[month]={...(previous||{}),rate:clean.rate,contributionUsd:clean.contributionUsd};
        history(p,'projection-updated',at,{month,value:previous},{month,value:p.future[month]});
      }else if(type==='recordResult'){
        changedMonth=applyFlow(account.plan,'result',clean,at);
      }else if(type==='recordContribution'||type==='recordWithdrawal'){
        changedMonth=applyFlow(account.plan,type==='recordContribution'?'contribution':'withdrawal',clean,at);
      }else if(type==='finalizeMonth'){
        const p=account.plan,month=monthInPlan(p,clean.month),previous=applyClosure(p,month,clean.confirmFlows,at,operationId);
        history(p,'month-finalized',at,{month,value:previous},{month,value:p.closures[month]});
      }else if(type==='reopenMonth'){
        const p=account.plan,month=monthInPlan(p,clean.month);requireThat(text(clean.reason),'Informe o motivo da reabertura.');
        requireThat(p.closures[month]?.confirmed===true,'O mês não tem fechamento confirmado.');
        reopenDependents(p,month,at,text(clean.reason));
      }else if(type==='restartPlan'){
        requireThat(clean.confirmation===true,'Confirme o arquivamento e reinício do plano.');
        requireThat(!hasRecordedFacts(account.plan),'Esta conta já tem lançamentos ou meses confirmados. Use Reiniciar → Somente uma conta antes de começar outro plano.');
        const c=configuration(clean.config),previous=clone(account.plan);
        next.archive.push({id:identity('planning_archive'),accountId:account.id,reason:'restartPlan',archivedAt:at,
          account:{id:account.id,name:account.name,broker:account.broker,login:account.login,server:account.server,active:account.active},plan:previous});
        account.plan=engine.createPlan(c,{id:identity('planning_plan'),now:at});
        applyConfigStop(account.plan,c,at,true);
        for(const key of ['name','broker','login','server'])account[key]=c[key];
        history(account.plan,'plan-restarted',at,{planId:previous.id},{planId:account.plan.id});
      }else if(type==='resetAccount'||type==='resetAll'){
        const scope=type==='resetAll'?'TODAS':'CONTA',preview=resetPreview(next,accountId,scope);
        requireThat(clean.confirmation===preview.phrase,'Digite exatamente '+preview.phrase+' para confirmar o reinício.');
        const targets=scope==='TODAS'?next.accounts.filter(item=>item.active):[account];
        for(const item of targets)archivePlan(next,item,at,scope);
        if(scope==='TODAS'){
          account=targets[0];
          for(const item of targets)item.active=false;
          next.pendingConfiguration={accountId:account.id,scope:'TODAS',at};requiresConfiguration=true;
        }else{
          const previous=account.plan,c={startMonth:previous.startMonth,initialUsd:previous.initialUsd,profileId:previous.profileId,
            monthlyContributionUsd:previous.monthlyContributionUsd,goals:clone(previous.goals)};
          const plan=engine.createPlan(c,{id:identity('planning_plan'),now:at});
          // The native account reset reapplies current premises but preserves the
          // financial reference. Its new income comparison starts from current goals.
          plan.reference={...clone(previous.reference),planId:plan.id};plan.incomeBaselineGoals=clone(previous.goals);
          account.plan=plan;history(plan,'account-reset',at,{planId:previous.id},{planId:plan.id},'Histórico arquivado; premissas reaplicadas.');
        }
      }else if(type==='archiveAccount'){
        requireThat(clean.confirmation===true,'Confirme o arquivamento da conta.');account.active=false;
        history(account.plan,'account-archived',at,{active:true},{active:false});
      }else if(type==='applyStop'){
        const p=account.plan,month=currentMonth(),bounds=engine.stopBounds(p,{month});
        requireThat(clean.stopAfter===null||engine.monthKey(clean.stopAfter)===clean.stopAfter&&clean.stopAfter>=bounds.min&&clean.stopAfter<=bounds.max,'Mês de parada inválido: respeite o período atual e o horizonte do plano.');
        if(clean.stopAfter!==null){
          requireThat(Number.isFinite(clean.impactLimit)&&clean.impactLimit>=0&&clean.impactLimit<=1,'Informe o limite de impacto entre 0% e 100%.');
          const simulation=engine.simulate(p,{month,stopAfter:clean.stopAfter,impactLimit:clean.impactLimit});
          requireThat(simulation.viable&&simulation.withinImpactLimit===true,'A parada ultrapassa o impacto permitido ou não tem projeção viável.');
        }
        const before={stopAfter:p.stopAfter??null,future:clone(p.future)},candidatePlan=engine.withContributionStop(p,{month,stopAfter:clean.stopAfter});
        p.stopAfter=candidatePlan.stopAfter;p.future=candidatePlan.future;
        history(p,'contribution-stop-updated',at,before,{stopAfter:p.stopAfter,future:clone(p.future),impactLimit:clean.impactLimit??null});
      }else throw new Error('Comando de planejamento desconhecido.');
      if(changedMonth)reopenDependents(account.plan,changedMonth,at,'Correção factual exige reconferência dos meses dependentes.');
      recalculate(account.plan);
      account.plan.revision++;next.revision++;
      next.audit.push({id:identity('planning_audit'),at,type,accountId:account.id,planId:account.plan.id,revision:next.revision,operationId});
      const confirmed=result('CONFIRMED',[],{accountId:account.id,planId:account.plan.id,revision:next.revision,operationId,...(requiresConfiguration?{requiresConfiguration:true}:{})});
      next.operations.push({id:operationId,type,accountId:account.id,planId:account.plan.id,at,signature,
        targetPlanId:accountById(next,accountId)?.plan?.id||null,
        base:{epoch:t.epoch,revision:t.revision,accountId:t.accountId,planId:t.planId,planRevision:t.planRevision},result:clone(confirmed)});
      const invalid=errorsFor(next);requireThat(invalid.length===0,invalid.join(' '));
      candidate.patrimonialPlanning=next;
      if(typeof dgLogChange==='function')dgLogChange('patrimonialPlanning',type,account.id,'Planejamento: '+type,candidate);
      requireThat(typeof jpWealthPersistDocument==='function'&&epoch()!==null,'Escritor confirmado indisponível.');
      let written;
      try{written=jpWealthPersistDocument(candidate,{expectedEpoch:t.epoch,component:'patrimonialPlanning'});}
      catch(error){unknown=true;generation++;if(typeof markJPWealthPersistenceOutcomeUnknown==='function')markJPWealthPersistenceOutcomeUnknown('Planejamento: escritor interrompido.');return result('UNKNOWN',['Gravação indeterminada; preserve o rascunho e confira a recuperação.']);}
      if(written?.status==='CONFIRMED'){
        // The existing writer already compared the full serialized read-back.
        adopt(candidate);
        try{root.JPWNotifications?.invalidate('planning');}catch(_error){}
        return confirmed;
      }
      generation++;
      if(written?.status==='REFUSED')return result(written.reason==='CONFLICT'?'CONFLICT':'REFUSED',['Gravação recusada; nenhum registro foi confirmado. Preserve e revise o rascunho.']);
      unknown=true;if(typeof markJPWealthPersistenceOutcomeUnknown==='function'&&!(typeof jpWealthPersistenceOutcomeIsUnknown==='function'&&jpWealthPersistenceOutcomeIsUnknown()))markJPWealthPersistenceOutcomeUnknown('Planejamento: confirmação indisponível.');
      return result('UNKNOWN',['Gravação indeterminada; preserve o rascunho e confira a recuperação.']);
    }catch(error){return result('INVALID',[error.message||'Entrada de planejamento inválida.']);}
  }
  function applyClosure(p,month,confirmFlows,at,operationId){
    requireThat(confirmFlows===true,'Confira e confirme os aportes e saques efetivos.');
    requireThat(own(p.results,month),'Registre o resultado total do mês, inclusive zero, antes de finalizar.');
    const prior=month===p.startMonth?null:p.closures[engine.addMonths(month,-1)];
    requireThat(month===p.startMonth||prior?.confirmed===true,'Reconferir e finalizar os meses anteriores antes deste fechamento.');
    requireThat(p.closures[month]?.confirmed!==true,'Este mês já está finalizado.');
    const previous=p.closures[month]||null,q=closureQuote(month);
    p.closures[month]={confirmed:true,confirmFlows:true,revision:(previous?.revision||0)+1,confirmedAt:at,operationId,
      ...(q?{fxQuote:q}:{}),...(previous?{previous:clone(previous)}:{})};
    const row=recalculate(p).find(item=>item.month===month);
    requireThat(row&&row.finalized&&finite(row.resultUsd)&&finite(row.openUsd)&&finite(row.closeUsd)&&row.closeUsd>=0,'Mês não calculável para fechamento.');
    p.closures[month].snapshot=clone(row);
    return previous;
  }
  function previewFinalizeMonth({accountId,month}={}){
    const blockers=[];let validContext=false;
    try{
      const value=envelope(),issues=errorsFor(value);requireThat(!issues.length,issues.join(' '));
      const account=clone(accountById(value,accountId));requireThat(account&&account.active===true,'Conta ativa de planejamento não encontrada.');
      const p=account.plan;
      validContext=engine.monthKey(month)===month&&month>=p.startMonth&&month<=engine.addMonths(p.startMonth,119);
      if(validContext){
        if(!own(p.results,month))blockers.push({code:'MISSING_RESULT',month});
        for(let prior=p.startMonth;prior<month;prior=engine.addMonths(prior,1)){
          if(p.closures[prior]?.confirmed!==true){blockers.push({code:'PREVIOUS_UNCONFIRMED',month:prior});break;}
        }
        if(p.closures[month]?.confirmed===true)blockers.push({code:'ALREADY_FINALIZED',month});
        if(month>currentMonth())blockers.push({code:'FUTURE_MONTH',month});
      }
      // The existing command validation remains the source of legacy errors and
      // of the effective row. Diagnostics only inspect this detached candidate.
      month=monthInPlan(p,month);applyClosure(p,month,true,now(),'preview-only');
      return {ok:true,status:'PREVIEW',errors:[],row:clone(p.closures[month].snapshot),blockers:[]};
    }catch(error){return {ok:false,status:'INVALID',errors:[error.message||'Prévia de fechamento indisponível.'],
      blockers:validContext?(blockers.length?blockers:[{code:'NOT_COMPUTABLE',month}]):[{code:'INVALID_CONTEXT',month:null}]};}
  }
  function reviseAccount(account,input,replaceFuture,at,record){
    const c=configuration(input,account),p=account.plan;
    const moved=c.startMonth!==p.startMonth||c.initialUsd!==p.initialUsd;
    requireThat(!moved||!hasRecordedFacts(p),'Esta conta já tem lançamentos ou meses confirmados. Use Reiniciar → Somente uma conta para arquivar o histórico antes de mudar o início.');
    const replacement=engine.revisePlan(p,c,{replaceFuture:replaceFuture===true,month:currentMonth(),now:at});
    const before={name:account.name,broker:account.broker,login:account.login,server:account.server,startMonth:p.startMonth,initialUsd:p.initialUsd,profileId:p.profileId,monthlyContributionUsd:p.monthlyContributionUsd,goals:p.goals,future:clone(p.future)};
    for(const key of ['name','broker','login','server'])account[key]=c[key];
    Object.assign(p,replacement); applyConfigStop(p,c,at);
    if(record)history(p,'account-updated',at,before,{name:account.name,broker:account.broker,login:account.login,server:account.server,profileId:p.profileId,monthlyContributionUsd:p.monthlyContributionUsd,goals:p.goals});
    recalculate(p);
    return account;
  }
  function hasRecordedFacts(p){return Object.keys(p.results).length>0||p.contributions.some(r=>r.usd>0)||p.withdrawals.some(r=>r.usd>0)||Object.values(p.closures).some(r=>r.confirmed===true);}
  function applyConfigStop(p,c,at,newPlan=false){
    if(!own(c,'stopAfter')||c.stopAfter===null)return;
    const month=currentMonth(),bounds=engine.stopBounds(p,{month,newPlan});
    requireThat(engine.monthKey(c.stopAfter)===c.stopAfter&&c.stopAfter>=bounds.min&&c.stopAfter<=bounds.max,'A parada deve respeitar o mês atual, o histórico e o horizonte do plano.');
    requireThat(finite(c.stopImpactLimit)&&c.stopImpactLimit>=0&&c.stopImpactLimit<=1,'Escolha um limite de impacto entre 0% e 100%.');
    const simulation=engine.simulate(p,{month,newPlan,stopAfter:c.stopAfter,impactLimit:c.stopImpactLimit});
    requireThat(simulation.viable&&simulation.withinImpactLimit===true,'A simulação mudou ou ultrapassa o limite escolhido. Reabra Planejar quando parar de aportar antes de salvar.');
    const next=engine.withContributionStop(p,{month,newPlan,stopAfter:c.stopAfter});p.stopAfter=next.stopAfter;p.future=next.future;
    history(p,'contribution-stop-updated',at,null,{stopAfter:p.stopAfter,impactLimit:c.stopImpactLimit});
  }
  function previewAccount({accountId,config,replaceFuture=false}={}){
    try{
      const value=envelope(),issues=errorsFor(value);requireThat(!issues.length,issues.join(' '));
      const account=clone(accountById(value,accountId));requireThat(account&&account.active===true,'Conta ativa de planejamento não encontrada.');
      assertSafeInput(config);reviseAccount(account,config,replaceFuture,now(),false);
      return {ok:true,status:'PREVIEW',errors:[],model:engine.account(account,{month:currentMonth(),quote:publicQuote()})};
    }catch(error){return {ok:false,status:'INVALID',errors:[error.message||'Prévia indisponível.']};}
  }
  function view(options={}){
    const value=envelope(),issues=errorsFor(value),quote=own(options,'quote')?options.quote:publicQuote();
    if(issues.length)return {status:'INCOMPATIBLE',issues,accounts:[],rows:[],confirmedThrough:null,
      confirmed:{balanceUsd:null,contributionsUsd:null,resultUsd:null,withdrawalsUsd:null,initialUsd:null}};
    const calculation={...options,month:options.month||currentMonth(),quote};
    if(options.accountId){const account=accountById(value,options.accountId);return account?engine.account(clone(account),calculation):{status:'NOT_FOUND',issues:['Conta de planejamento não encontrada.'],rows:[]};}
    return engine.portfolio(clone(value),calculation);
  }
  function pendingActions({month=currentMonth()}={}){
    // Availability here concerns the factual notification projection only.
    // validateEnvelope also calculates120-month trajectories; this consultation
    // checks only the identities/maps/flags it reads and never certifies balances.
    const unavailable=message=>({available:false,accounts:[],issues:[message]});
    const value=envelope(),accounts=[],accountIds=new Set(),planIds=new Set();
    if(!engine||typeof engine.monthKey!=='function'||typeof engine.addMonths!=='function'||engine.monthKey(month)!==month)
      return unavailable('Referência mensal indisponível para consultar as pendências.');
    const revision=v=>Number.isSafeInteger(v)&&v>=0;
    if(!object(value)||value.schemaVersion!==1||!revision(value.revision)||
      !['accounts','archive','audit','operations'].every(key=>Array.isArray(value[key])))
      return unavailable('Dados de planejamento incompatíveis; preserve a base e confira a recuperação.');
    for(const account of value.accounts){
      if(!object(account)||!text(account.id)||accountIds.has(account.id)||typeof account.name!=='string'||
        !account.name.trim()||typeof account.active!=='boolean'||!object(account.plan)||
        !text(account.plan.id)||planIds.has(account.plan.id))
        return unavailable('Identidades das contas ou dos planos precisam de revisão.');
      accountIds.add(account.id);planIds.add(account.plan.id);
      if(account.active!==true)continue;
      const plan=account.plan;
      if(engine.monthKey(plan.startMonth)!==plan.startMonth||!revision(plan.revision)||
        !object(plan.results)||!object(plan.closures)||!Array.isArray(plan.contributions)||!Array.isArray(plan.withdrawals))
        return unavailable('Registros mensais de planejamento indisponíveis para consulta.');
      const end=engine.addMonths(plan.startMonth,119);
      const inRange=m=>engine.monthKey(m)===m&&m>=plan.startMonth&&m<=end;
      const months=new Set(),invalidated=new Set();
      for(const [key,result] of Object.entries(plan.results)){
        if(!inRange(key)||!object(result)||!finite(result.usd)||!revision(result.revision))
          return unavailable('Há um resultado mensal incompatível; confira os registros de origem.');
        if(key<month)months.add(key); // An explicit zero is a recorded fact.
      }
      for(const flows of [plan.contributions,plan.withdrawals]){
        const ids=new Set();
        for(const flow of flows){
          if(!object(flow)||!text(flow.id)||ids.has(flow.id)||!inRange(flow.month)||
            !finite(flow.usd)||flow.usd<0||!revision(flow.revision))
            return unavailable('Há lançamentos mensais incompatíveis ou duplicados; confira a origem.');
          ids.add(flow.id);
          // A corrected zero annuls the current flow, regardless of its history.
          if(flow.month<month&&flow.usd>0)months.add(flow.month);
        }
      }
      for(const [key,closure] of Object.entries(plan.closures)){
        if(!inRange(key)||!object(closure)||typeof closure.confirmed!=='boolean'||
          typeof closure.confirmFlows!=='boolean'||!revision(closure.revision))
          return unavailable('Há um fechamento mensal incompatível; confira a origem.');
        if(closure.confirmed===true&&(!closure.confirmFlows||!own(plan.results,key)))
          return unavailable('Um fechamento informado não possui os fatos e a conferência correspondentes.');
        if(closure.confirmed===false&&closure.previous?.confirmed===true&&key<month){months.add(key);invalidated.add(key);}
      }
      let firstOpen=null;
      const last=Array.from(months).sort().at(-1);
      if(last)for(let key=plan.startMonth;key<=last;key=engine.addMonths(key,1)){
        if(plan.closures[key]?.confirmed!==true){if(firstOpen===null)firstOpen=key;}
        else if(firstOpen!==null)return unavailable('A sequência dos fechamentos precisa de reconferência na origem.');
      }
      const pending=Array.from(months).sort().filter(key=>plan.closures[key]?.confirmed!==true).map(key=>({month:key,
        codes:['UNCONFIRMED_MONTH',...(!own(plan.results,key)?['MISSING_RESULT']:[]),...(invalidated.has(key)?['CLOSURE_INVALIDATED']:[])]}));
      if(!pending.length)continue;
      const dependencyMonth=firstOpen&&firstOpen<pending[0].month?firstOpen:null;
      accounts.push({accountId:account.id,planId:plan.id,name:account.name,months:pending,count:pending.length,
        firstMonth:dependencyMonth||pending[0].month,dependencyMonth});
    }
    return {available:true,accounts,issues:[]};
  }
  planning.queries={previewAccount,previewFlow,previewResultInput,previewReset,previewFinalizeMonth,pendingActions,snapshot:()=>clone(envelope()),view,sheetView:options=>engine.sheetView(clone(envelope()),{month:currentMonth(),quote:publicQuote(),...(options||{})}),account:id=>clone(accountById(envelope(),id)),token,
    history:id=>{const value=envelope(),account=accountById(value,id);return {planId:account?.plan?.id||null,history:clone(account?.plan?.history||[]),archive:clone(Array.isArray(value?.archive)?value.archive.filter(item=>item.accountId===id):[])};},
    legacy:()=>({schemaVersion:1,source:'S.fxPlanning',exportOnly:true,value:sanitizeLegacy(state()?.fxPlanning??null)})};
  planning.commands={execute,resetContext};
})(window);

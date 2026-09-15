// ============ PLANEJAMENTO FX · ESTADO E MUTAÇÕES (ponte com S) ============
// Única camada autorizada a ler/escrever S.fxPlanning. Leitura para cálculo passa
// por normalização profunda em CÓPIA — o estado persistido preserva campos
// desconhecidos (STATE-SCHEMA.md §3) e a versão limpa nunca é gravada de volta
// sem mutação explícita do operador. Toda mutação valida, audita no
// fxPlanning.auditLog (eventos da especificação, seção 29) e registra em
// dgLogChange — o aviso de "alterações desde o último backup" passa a cobrir o
// Planejamento FX. Nenhum segredo entra no log.

function fxEnvelopeIssue(){
  const fx=S.fxPlanning;
  if(!fx||typeof fx!=='object'||Array.isArray(fx)||fx.schemaVersion!==1||!Array.isArray(fx.auditLog))return 'Planejamento incompatível: preserve o documento e confira a versão antes de editar.';
  if(fx.archivedPlans!==undefined&&!Array.isArray(fx.archivedPlans))return 'Arquivo histórico de planos incompatível.';
  const p=fx.plan;if(p===null)return '';
  if(!p||typeof p!=='object'||Array.isArray(p)||!p.baseline||!p.current||!p.actuals||Array.isArray(p.actuals)||!Array.isArray(p.revisions)||!Array.isArray(p.contributions))return 'Estrutura do plano incompatível; nenhuma normalização automática será gravada.';
  if(!fxInputFinite(p.current.defaultMonthlyReturn)||+p.current.defaultMonthlyReturn<=-1)return 'Premissa de rentabilidade ausente ou inválida; não será convertida em zero.';
  if(p.planningRevision!==undefined&&p.planningRevision!==2)return 'Revisão do planejamento desconhecida; somente leitura.';
  for(const key of ['scenarios','scenarioArchive','rebases','actualHistory'])if(p[key]!==undefined&&!Array.isArray(p[key]))return 'Histórico de planejamento incompatível: '+key+'.';
  for(const rec of Object.values(p.actuals))if(!rec||fxValidateActualInput(rec).length)return 'Fechamento realizado incompleto; ausência não é resultado zero.';
  return '';
}
function fxState(){return S.fxPlanning;}
function fxActivePlanRaw(){ return fxState()&&fxState().plan||null; }
// Cópia normalizada para o motor puro (window.JPWFx.engine).
function fxActivePlan(){
  if(fxEnvelopeIssue())return null;
  const raw=fxActivePlanRaw(); if(!raw) return null;
  const baseline=fxNormalizeAssumptions(raw.baseline);
  return {
    ...structuredClone(raw),
    id:String(raw.id||''), name:String(raw.name||'Planejamento FX'),
    createdAt:String(raw.createdAt||''), updatedAt:String(raw.updatedAt||''),
    baseline:{...baseline, frozenAt:String((raw.baseline&&raw.baseline.frozenAt)||'')},
    current:{...fxNormalizeAssumptions(raw.current||raw.baseline),
      revisedAt:String((raw.current&&raw.current.revisedAt)||'')},
    revisions:(raw.revisions||[]).map(r=>({
      ...structuredClone(r),
      revisedAt:String((r&&r.revisedAt)||''), supersededAt:String((r&&r.supersededAt)||''),
      note:String((r&&r.note)||''), snapshot:fxNormalizeAssumptions(r&&r.snapshot)})),
    actuals:Object.fromEntries(Object.entries(raw.actuals||{})
      .filter(([m])=>fxMonthKey(m))
      .map(([m,rec])=>[fxMonthKey(m),fxNormalizeActual(rec)])),
    contributions:(raw.contributions||[]).map(fxNormalizeContribution)
      .filter(c=>fxMonthKey(c.month)&&c.usdAmount>0)
  };
}
function fxAudit(type,month,detail){
  const fx=fxState();
  fx.auditLog.push({id:fxId('fxa'), ts:new Date().toISOString(), type,
    month:month||null, detail:String(detail||'')});
  if(fx.auditLog.length>400) fx.auditLog=fx.auditLog.slice(-400);
  if(typeof dgLogChange==='function') dgLogChange('fxPlanning',type,month||'',String(detail||''));
}
// Confirma somente a mutação deste agregado e seu evento DG. O save global
// continua responsável por concorrência, recuperação e gravação física.
function fxMutateState(fn){
  const issue=fxEnvelopeIssue();if(issue)return {ok:false,persistido:false,errors:[issue]};
  const unknown=()=>{
    hideStaleSavedTag();
    // Uma exceção posterior ao save pode suceder o aviso verde de recuperação.
    // Só esse aviso transitório é retirado; alertas de falha ficam preservados.
    const banner=persistenceAlertEl();
    if(banner && banner.classList.contains('is-recovered')){
      clearTimeout(jpWealthPersistenceFailure.recoveryTimer);
      banner.className='persistence-alert';banner.textContent='';
      layoutPersistenceBanners();
    }
    return ({ok:false,persistido:null,bloqueado:true,
    errors:['Gravação indeterminada. Não repita a ação; confira a base salva antes de continuar.']});
  };
  if(jpWealthPersistenceOutcomeIsUnknown()){
    hideStaleSavedTag();
    return unknown();
  }
  let before;
  try{ before=structuredClone(fxState()); }
  catch(e){ return {ok:false,persistido:false,errors:['Não foi possível preparar a alteração. Nada foi aplicado.']}; }
  const log=S.dataGovernance&&S.dataGovernance.changeLog;
  const logBefore=Array.isArray(log)?log.slice():null;
  const restore=()=>{
    S.fxPlanning=before;
    // dgLogChange pode substituir o array quando poda o limite de 400.
    if(logBefore){log.splice(0,log.length,...logBefore);S.dataGovernance.changeLog=log;}
  };
  let result;
  try{
    result=fn()||{};
    if(result.ok===false){restore();return {...result,persistido:false};}
    if(S.fxPlanning.plan)S.fxPlanning.plan.planningRevision=2;
  }catch(e){
    restore();hideStaleSavedTag();
    return {ok:false,persistido:false,errors:['Não foi possível aplicar a alteração. Nada foi gravado.']};
  }
  let written;
  try{ written=save(); }
  catch(e){
    markJPWealthPersistenceOutcomeUnknown('Planejamento FX');
    hideStaleSavedTag();
    return unknown();
  }
  if(written===false){
    restore();hideStaleSavedTag();
    return {ok:false,persistido:false,errors:['Gravação recusada. A alteração não foi aplicada; preserve os campos e resolva a falha antes de tentar novamente.']};
  }
  if(written!==true){
    markJPWealthPersistenceOutcomeUnknown('retorno indeterminado do Planejamento FX');
    hideStaleSavedTag();
    return unknown();
  }
  return {...result,ok:true,persistido:true};
}

// ---- Mutações ---------------------------------------------------------------
// MVP: um planejamento ativo por vez (seção 31 da especificação).
function fxPlanCreate({name,assumptions}={}){
  return fxMutateState(()=>{
    if(!assumptions||!fxInputFinite(assumptions.defaultMonthlyReturn))return {ok:false,errors:['Informe a rentabilidade planejada; zero é válido.']};
    const norm=fxNormalizeAssumptions(assumptions);
    const errors=fxValidateAssumptions(norm);
    if(errors.length) return {ok:false,errors};
    const fx=fxState();
    if(fx.plan) return {ok:false,errors:['Já existe um planejamento ativo — o MVP mantém um plano por vez.']};
    fx.plan=fxCreatePlan({name,assumptions:norm});
    fxAudit('FX_PLAN_CREATED',norm.startMonth,`${fx.plan.name} · ${norm.horizonMonths} meses · saldo inicial ${norm.initialBalanceUsd} USD`);
    return {ok:true,plan:fx.plan};
  });
}
// A remoção do plano ativo preserva um arquivo integral. A confirmação explícita
// é responsabilidade da interface.
function fxPlanDelete(){
  return fxMutateState(()=>{
    const fx=fxState();
    if(!fx.plan) return {ok:false,errors:['Nenhum planejamento ativo.']};
    const label=fx.plan.name;
    if(fx.archivedPlans!==undefined&&!Array.isArray(fx.archivedPlans))return {ok:false,errors:['Arquivo de planos incompatível. Preserve o documento.']};
    fx.archivedPlans=fx.archivedPlans||[];fx.archivedPlans.push({archivedAt:new Date().toISOString(),plan:structuredClone(fx.plan)});
    fx.plan=null;
    fxAudit('FX_PLAN_DELETED',null,label);
    return {ok:true};
  });
}
// Revisão de premissas de FUTURO. Estruturais (mês inicial, horizonte, saldo
// inicial) permanecem os do baseline — fxReviseAssumptions preserva o snapshot
// anterior em revisions[] e nunca toca o baseline.
function fxPlanReviseAssumptions(next,note){
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw();
    if(!raw) return {ok:false,errors:['Nenhum planejamento ativo.']};
    const merged=fxNormalizeAssumptions({...next,
      startMonth:raw.baseline.startMonth,
      horizonMonths:raw.baseline.horizonMonths,
      initialBalanceUsd:raw.baseline.initialBalanceUsd});
    const errors=fxValidateAssumptions(merged);
    if(errors.length) return {ok:false,errors};
    fxState().plan=fxReviseAssumptions(raw,merged,{note});
    fxAudit('FX_PLAN_ASSUMPTION_CHANGED',null,String(note||'premissas revisadas'));
    return {ok:true};
  });
}
// Fechamento mensal: contíguo desde o início do plano (fxNextOpenMonth). Editar
// mês já fechado é permitido, auditado como FX_MONTH_ACTUAL_EDITED e preserva o
// closedAt original — carimbo usado na reconstrução de forecasts anteriores.
function fxPlanRecordActual(month,input){
  return fxMutateState(()=>{
    const plan=fxActivePlan();
    if(!plan) return {ok:false,errors:['Nenhum planejamento ativo.']};
    const key=fxMonthKey(month);
    const rec=fxNormalizeActual(input);
    const errors=fxValidateActualInput(rec);
    const existing=key?!!plan.actuals[key]:false;
    if(!key) errors.push('Mês inválido (use AAAA-MM).');
    else if(!existing){
      const next=fxNextOpenMonth(plan);
      if(!next) errors.push('O horizonte do plano já está completamente fechado.');
      else if(key!==next) errors.push(`Fechamentos são contíguos — o próximo mês aberto é ${next}.`);
    }
    if(errors.length) return {ok:false,errors};
    const raw=fxActivePlanRaw(), now=new Date().toISOString();
    const prev=(raw.actuals=raw.actuals||{})[key];
    const source=input.source?structuredClone(input.source):{system:'MANUAL',...ledgerContext()};
    const after={...(prev||{}), ...rec, source,version:(prev&&prev.version||0)+1,
      closedAt:(prev&&prev.closedAt)?prev.closedAt:now, updatedAt:now};
    raw.actualHistory=raw.actualHistory||[];
    raw.actualHistory.push({id:fxId('fxh'),month:key,at:now,before:prev?structuredClone(prev):null,after:structuredClone(after)});
    raw.actuals[key]=after;
    raw.updatedAt=now;
    fxAudit(existing?'FX_MONTH_ACTUAL_EDITED':'FX_MONTH_ACTUAL_RECORDED',key,
      rec.inputType==='usd'?`resultado ${rec.profitUsd} USD`:`taxa ${rec.returnRate}`);
    return {ok:true};
  });
}
function fxPlanAddContribution(input){
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw();
    if(!raw) return {ok:false,errors:['Nenhum planejamento ativo.']};
    const rec=fxNormalizeContribution({...input, id:'', createdAt:new Date().toISOString()});
    const errors=fxValidateContribution(rec);
    if(errors.length) return {ok:false,errors};
    (raw.contributions=raw.contributions||[]).push(rec);
    raw.updatedAt=new Date().toISOString();
    fxAudit('FX_CONTRIBUTION_RECORDED',rec.month,
      `${rec.source==='prop'?'Prop Firm':'Pessoal'} · ${rec.usdAmount} USD${rec.affectsFxCostBasis?` @ R$ ${rec.acquisitionFxRate}`:' (USD nativo — fora do custo médio)'}`);
    return {ok:true,contribution:rec};
  });
}
function fxPlanRemoveContribution(id){
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw();
    if(!raw) return {ok:false,errors:['Nenhum planejamento ativo.']};
    const idx=(raw.contributions||[]).findIndex(c=>c&&c.id===id);
    if(idx<0) return {ok:false,errors:['Aporte não encontrado.']};
    const [gone]=raw.contributions.splice(idx,1);
    raw.updatedAt=new Date().toISOString();
    fxAudit('FX_CONTRIBUTION_REMOVED',fxMonthKey(gone&&gone.month)||null,
      `${gone&&gone.source==='prop'?'Prop Firm':'Pessoal'} · ${gone?gone.usdAmount:''} USD`);
    return {ok:true};
  });
}

// ---- Leitura consolidada ----------------------------------------------------
function fxOverviewLive(){
  const plan=fxActivePlan();
  return plan?{plan,...fxOverview(plan)}:null;
}
// FCR/FEO usam o adaptador compartilhado e a apuração explícita da conta ativa.
// SI, onboarding e despesas mensais não suprem capital nominal ou seis meses.
function fxReservePanelData(){
  const api=window.JPWForex&&window.JPWForex.state;
  const view=api&&api.read?api.read():{},account=view.account||null;
  const active=S.forex&&S.forex.activeAccountId;
  const stored=S.forex&&S.forex.reserves;
  const reserves=stored&&active&&stored.accountId===active?stored:{};
  const number=v=>typeof v==='number'&&Number.isFinite(v)?v:null;
  const accountCapital=account?number(account.capitalNominal):null,declared=number(reserves.capitalNominal);
  const conflict=accountCapital!==null&&declared!==null&&accountCapital!==declared;
  const result=reserveRequirementsCalc({capitalNominal:conflict?null:declared??accountCapital,
    sixMonthExpenseAmount:number(reserves.sixMonthExpenseAmount),determinationRecorded:reserves.determinationRecorded===true,
    expensesApproved:reserves.expensesApproved===true,fcrCurrent:number(reserves.fcrConstituted),feoCurrent:number(reserves.feoConstituted)});
  if(conflict)result.findings.push({code:'NOMINAL_CAPITAL_DIVERGENCE',message:'Capital nominal da conta e da apuração divergem. Reconcilie os registros; nenhuma base foi escolhida automaticamente.'});
  return result;
}

window.JPWFx.state={fxState,fxActivePlanRaw,fxActivePlan,fxPlanCreate,fxPlanDelete,
  fxPlanReviseAssumptions,fxPlanRecordActual,fxPlanAddContribution,
  fxPlanRemoveContribution,fxOverviewLive,fxReservePanelData};

// Commands below extend v1 without rewriting its baseline, historical revisions,
// or unknown fields. All writes still cross fxMutateState exactly once.
function fxPlanningReferences(){
  const p=window.JPWForex&&window.JPWForex.policy&&window.JPWForex.policy.planning;
  return p?{monthly:p.referenceMonthlyReturn,annualRange:p.annualReferenceRange}:null;
}
function fxFutureMonth(raw,month){
  const key=fxMonthKey(month),next=fxNextOpenMonth(fxActivePlan());
  return !!(key&&next&&key>=next&&key>=raw.baseline.startMonth&&key<fxAddMonths(raw.baseline.startMonth,raw.baseline.horizonMonths));
}
function fxPlanReviseFromMonth(month,patch,note,scenarioId=null){
  month=fxMonthKey(month);
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw();if(!raw)return {ok:false,errors:['Nenhum plano ativo.']};
    if(!fxFutureMonth(raw,month))return {ok:false,errors:['Edite uma linha projetada dentro do horizonte. ACTUAL exige correção de fechamento.']};
    const scenario=scenarioId?(raw.scenarios||[]).find(s=>s.id===scenarioId):null;
    if(scenarioId&&!scenario)return {ok:false,errors:['Cenário não encontrado.']};
    if(!String(note||'').trim())return {ok:false,errors:['Informe o motivo da revisão.']};
    for(const key of ['rate','personalUsd','propUsd'])if(Object.prototype.hasOwnProperty.call(patch,key)&&(!fxInputFinite(patch[key])||(key==='rate'?+patch[key]<=-1:+patch[key]<0)))return {ok:false,errors:['Valor inválido para '+key+'.']};
    const before=scenario?scenario.assumptions:raw.current;
    const next=structuredClone(before);next.monthOverrides={...(next.monthOverrides||{})};next.plannedContributions={...(next.plannedContributions||{})};
    if(Object.prototype.hasOwnProperty.call(patch,'rate'))next.monthOverrides[month]=+patch.rate;
    const previous=fxPlannedContribution(next,month);
    next.plannedContributions[month]={personalUsd:patch.personalUsd===undefined?previous.personalUsd:+patch.personalUsd,propUsd:patch.propUsd===undefined?previous.propUsd:+patch.propUsd};
    if(scenario){scenario.revisions=scenario.revisions||[];scenario.revisions.push({at:new Date().toISOString(),month,note,before:structuredClone(scenario.assumptions),rebases:structuredClone(scenario.rebases||[])});scenario.assumptions=next;scenario.version=(scenario.version||0)+1;}
    else fxState().plan=fxReviseAssumptions(raw,next,{note});
    fxAudit(scenario?'FX_SCENARIO_ROW_REVISED':'FX_PLAN_ROW_REVISED',month,note);return {ok:true};
  });
}
function fxPlanRebase(month,openingBalanceUsd,note,scenarioId=null){
  month=fxMonthKey(month);
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw();if(!raw)return {ok:false,errors:['Nenhum plano ativo.']};
    if(!fxFutureMonth(raw,month)||!fxInputFinite(openingBalanceUsd)||+openingBalanceUsd<0||!String(note||'').trim())return {ok:false,errors:['Rebase exige mês projetado, saldo não negativo e motivo explícito.']};
    const scenario=scenarioId?(raw.scenarios||[]).find(s=>s.id===scenarioId):null;
    if(scenarioId&&!scenario)return {ok:false,errors:['Cenário não encontrado.']};
    let target=scenario;
    if(scenario){scenario.revisions=scenario.revisions||[];scenario.revisions.push({at:new Date().toISOString(),month,note,before:structuredClone(scenario.assumptions),rebases:structuredClone(scenario.rebases||[])});scenario.version=(scenario.version||0)+1;}
    if(!target){fxState().plan=fxReviseAssumptions(raw,raw.current,{note:'Rebase: '+note});target=fxActivePlanRaw();}
    target.rebases=target.rebases||[];
    target.rebases.push({id:fxId('fxr'),month,openingBalanceUsd:+openingBalanceUsd,note:String(note),at:new Date().toISOString()});
    fxAudit(scenario?'FX_SCENARIO_REBASED':'FX_PLAN_REBASED',month,note);return {ok:true};
  });
}
function fxScenarioSave({id=null,name}={}){
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw();if(!raw)return {ok:false,errors:['Nenhum plano ativo.']};
    if(!String(name||'').trim())return {ok:false,errors:['Nome do cenário obrigatório.']};
    raw.scenarios=raw.scenarios||[];
    const existing=id?raw.scenarios.find(s=>s.id===id):null;
    if(id&&!existing)return {ok:false,errors:['Cenário não encontrado.']};
    if(existing){existing.name=String(name).trim();existing.version++;}
    else {raw.scenarios.push({id:fxId('fxs'),name:String(name).trim(),version:1,createdAt:new Date().toISOString(),assumptions:structuredClone(raw.current),rebases:structuredClone(raw.rebases||[]),revisions:[]});}
    const scenario=existing||raw.scenarios[raw.scenarios.length-1];fxAudit('FX_SCENARIO_SAVED',null,scenario.name);return {ok:true,id:scenario.id};
  });
}
function fxScenarioDelete(id){
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw(),item=raw&&(raw.scenarios||[]).find(s=>s.id===id);
    if(!item)return {ok:false,errors:['Cenário não encontrado.']};
    raw.scenarioArchive=raw.scenarioArchive||[];raw.scenarioArchive.push({...structuredClone(item),archivedAt:new Date().toISOString()});
    raw.scenarios=raw.scenarios.filter(s=>s.id!==id);fxAudit('FX_SCENARIO_ARCHIVED',null,item.name);return {ok:true};
  });
}
function fxPlanImportLedgerActual(month,options={}){
  const api=window.JPWLedger;if(!api)return {ok:false,errors:['Contabilidade indisponível.']};
  if(jpWealthPersistenceOutcomeIsUnknown())return {ok:false,errors:['Gravação indeterminada. Confira a base salva antes de continuar.']};
  const preview=api.monthlyActual(month,options);
  if(preview.status!=='COMPLETE')return {ok:false,errors:preview.issues};
  if(!options.sourceVersion||options.sourceVersion!==preview.source.version)return {ok:false,errors:['A origem mudou ou a prévia não foi confirmada. Atualize antes de importar.']};
  const plan=fxActivePlan();if(!plan)return {ok:false,errors:['Nenhum plano ativo.']};
  const existing=plan.actuals[month];
  if(existing&&options.replace!==true)return {ok:false,errors:['Já existe realizado. Confirme explicitamente a substituição após revisar a origem.']};
  const row=fxForecastTimeline(plan).find(r=>r.month===month);
  if(!row||Math.abs(row.open-preview.source.openingBalanceUsd)>0.005)return {ok:false,errors:['Saldo de abertura da Contabilidade difere do realizado/plano. Reconcilie a base antes de importar.']};
  const contributions=fxContributionsByMonth(plan.contributions)[month];
  if(contributions&&contributions.totalUsd!==0)return {ok:false,errors:['O mês tem aportes no planejamento. O ledger diário não discrimina fluxos; reconcilie antes de importar.']};
  return fxPlanRecordActual(month,{inputType:'usd',profitUsd:preview.profitUsd,valuationFxRate:options.valuationFxRate||null,notes:options.notes||'Importação explícita da Contabilidade',source:preview.source});
}
Object.assign(window.JPWFx.state,{fxEnvelopeIssue,fxPlanningReferences,fxPlanReviseFromMonth,fxPlanRebase,fxScenarioSave,fxScenarioDelete,fxPlanImportLedgerActual});

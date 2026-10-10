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
  for(const a of [p.baseline,p.current]){
    for(const field of ['yearOverrides','monthOverrides','plannedContributions','absentMonths','recurringContributions']){
      if(a[field]!==undefined&&(!a[field]||typeof a[field]!=='object'||Array.isArray(a[field])))return 'Premissas incompatíveis: '+field+'.';
    }
  }
  if(p.planningRevision!==undefined&&![2,3].includes(p.planningRevision))return 'Revisão do planejamento desconhecida; somente leitura.';
  for(const key of ['scenarios','scenarioArchive','rebases','actualHistory'])if(p[key]!==undefined&&!Array.isArray(p[key]))return 'Histórico de planejamento incompatível: '+key+'.';
  if(fxValidateAssumptions(fxNormalizeAssumptions(p.baseline)).length)return 'Baseline incompleto ou inválido; preserve a origem antes de editar.';
  if(fxValidateAssumptions(fxNormalizeAssumptions(p.current)).length)return 'Premissas mensais incompletas; ausência não será convertida em zero.';
  if(p.current.absentMonths!==undefined&&(!p.current.absentMonths||typeof p.current.absentMonths!=='object'||Array.isArray(p.current.absentMonths)))return 'Mapa de previsões ausentes incompatível.';
  const firstMonth=fxMonthKey(p.baseline.startMonth),lastMonth=fxAddMonths(firstMonth,+p.baseline.horizonMonths-1);
  for(const [month,rec] of Object.entries(p.actuals)){
    if(fxMonthKey(month)!==month||month<firstMonth||month>lastMonth)return 'Mês realizado incompatível ou fora do horizonte; preserve a origem antes de editar.';
    if(!rec||fxValidateActualInput(rec).length)return 'Fechamento realizado incompleto; ausência não é resultado zero.';
    if(rec.closureStatus!==undefined&&!['FINALIZED','REOPENED','REVIEW_REQUIRED'].includes(rec.closureStatus))return 'Estado de finalização desconhecido; preserve o registro.';
  }
  // Validate stored facts before the read-copy normalizer. Filtering a malformed
  // ledger entry would turn an unknown deposit into a confirmed zero.
  for(const c of p.contributions){
    if(!c||typeof c!=='object'||Array.isArray(c)||fxMonthKey(c.month)!==c.month||c.month<firstMonth||c.month>lastMonth)
      return 'Mês do depósito efetivo incompatível; nenhum lançamento será descartado silenciosamente.';
    if(!['personal','prop'].includes(c.source)||!['USD','BRL'].includes(c.originalCurrency)||
      !fxInputFinite(c.originalAmount)||+c.originalAmount<=0||!fxInputFinite(c.usdAmount)||+c.usdAmount<=0)
      return 'Depósito efetivo incompleto ou inválido; ausência não é depósito zero.';
    if(c.originalCurrency==='BRL'&&(!fxInputFinite(c.acquisitionFxRate)||+c.acquisitionFxRate<=0))
      return 'Depósito em BRL sem taxa de aquisição válida; preserve o lançamento e confira sua origem.';
    if(fxValidateContribution(c).length)return 'Depósito efetivo inconsistente com a conversão registrada.';
    if(c.originalCurrency==='USD'&&Math.abs(+c.originalAmount-+c.usdAmount)>Math.max(.01,+c.originalAmount*1e-6))
      return 'Depósito USD inconsistente com seu valor original.';
  }
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
    if(S.fxPlanning.plan)S.fxPlanning.plan.planningRevision=3;
    const candidateIssue=fxEnvelopeIssue();
    if(candidateIssue){restore();return {ok:false,persistido:false,errors:[candidateIssue]};}
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
    const merged=fxNormalizeAssumptions({...raw.current,...next,
      monthOverrides:{...(raw.current.monthOverrides||{}),...(next.monthOverrides||{})},
      plannedContributions:{...(raw.current.plannedContributions||{}),...(next.plannedContributions||{})},
      absentMonths:{...(raw.current.absentMonths||{}),...(next.absentMonths||{})},
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
// Finalization is an explicit command, with a confirmed contribution review.
// This same guard covers the legacy form and accounting imports.
function fxPlanRecordActual(month,input={}){
  return fxPlanFinalizeMonth(month,input);
}
function fxPlanFinalizeMonth(month,input={}){
  return fxMutateState(()=>{
    const plan=fxActivePlan();if(!plan)return {ok:false,errors:['Nenhum planejamento ativo.']};
    const key=fxMonthKey(month),rec=fxNormalizeActual(input),errors=fxValidateActualInput(rec);
    const prev=key&&(plan.actuals||{})[key];
    if(input.inputType!==undefined&&!['rate','usd'].includes(input.inputType))errors.push('Tipo de entrada do realizado deve ser taxa ou USD.');
    if(!key)errors.push('Mês inválido (use AAAA-MM).');
    if(prev&&(prev.closureStatus||'FINALIZED')==='FINALIZED')errors.push('Mês finalizado. Reabra explicitamente com motivo antes de alterar o realizado.');
    if(input.contributionsConfirmed!==true)errors.push('Confira e confirme os depósitos efetivos deste mês, inclusive quando forem zero.');
    const next=fxNextOpenMonth(plan);
    if(!next)errors.push('O horizonte do plano já está completamente finalizado.');
    else if(key!==next)errors.push('Reconcilie cronologicamente. O próximo mês a finalizar é '+next+'.');
    const confirmed=fxActualTimeline(plan),open=confirmed.length?confirmed[confirmed.length-1].close:plan.baseline.initialBalanceUsd;
    if(!Number.isFinite(open))errors.push('Saldo de abertura indisponível. Reconcilie a base anterior.');
    if(errors.length)return {ok:false,errors};
    const contributions=fxContributionsByMonth(plan.contributions)[key]||{personalUsd:0,propUsd:0,totalUsd:0};
    const computed=fxActualRow(key,rec,open,contributions);
    if(!Number.isFinite(computed.close))return {ok:false,errors:['Resultado não finito. Confira valores e base antes de finalizar.']};
    const raw=fxActivePlanRaw(),now=new Date().toISOString(),old=(raw.actuals||{})[key]||null;
    const source=input.source?structuredClone(input.source):old&&old.source?structuredClone(old.source):{system:'MANUAL',...ledgerContext()};
    const snapshot=Object.fromEntries(['month','open','rate','profit','personalUsd','propUsd','contributionUsd','close','inputType','derivedField','valuationFxRate'].map(k=>[k,computed[k]]));
    const after={...(old||{}),...rec,source,closureStatus:'FINALIZED',contributionsConfirmed:true,
      confirmedSnapshot:snapshot,contributionsSnapshot:structuredClone((raw.contributions||[]).filter(c=>fxMonthKey(c.month)===key)),confirmedAt:now,version:(old&&old.version||0)+1,
      closedAt:old&&old.closedAt?old.closedAt:now,updatedAt:now};
    delete after.reviewRequiredBy;delete after.reopenedAt;delete after.reopenNote;
    raw.actualHistory=raw.actualHistory||[];
    raw.actualHistory.push({id:fxId('fxh'),month:key,at:now,action:old?'REFINALIZED':'FINALIZED',before:old?structuredClone(old):null,after:structuredClone(after)});
    raw.actuals[key]=after;raw.updatedAt=now;
    fxAudit(old?'FX_MONTH_REFINALIZED':'FX_MONTH_FINALIZED',key,String(input.notes||'Conferência mensal confirmada'));
    return {ok:true,month:key,row:computed,nextOpenMonth:fxNextOpenMonth(fxActivePlan())};
  });
}
function fxPlanReconcileMonth(month,input={}){return fxPlanFinalizeMonth(month,input);}
function fxPlanReopenMonth(month,note){
  return fxMutateState(()=>{
    const plan=fxActivePlan(),raw=fxActivePlanRaw(),key=fxMonthKey(month),rec=raw&&raw.actuals&&raw.actuals[key];
    if(!plan||!rec)return {ok:false,errors:['Mês realizado não encontrado.']};
    if(!String(note||'').trim())return {ok:false,errors:['Informe o motivo da reabertura.']};
    if((rec.closureStatus||'FINALIZED')==='REOPENED')return {ok:false,errors:['Mês já reaberto. Preserve a edição atual.']};
    const rows=fxForecastTimeline(plan),beforeRows=Object.fromEntries(rows.map(r=>[r.month,r])),now=new Date().toISOString(),affected=[];
    const calculationSnapshot={actuals:structuredClone(raw.actuals),contributions:structuredClone(raw.contributions||[]),rebases:structuredClone(raw.rebases||[])};
    raw.actualHistory=raw.actualHistory||[];
    for(const [m,item] of Object.entries(raw.actuals).sort(([a],[b])=>a.localeCompare(b))){
      if(m<key)continue;
      const before=structuredClone(item),row=beforeRows[m];
      if(!item.confirmedSnapshot&&row&&Number.isFinite(row.close))item.confirmedSnapshot=Object.fromEntries(['month','open','rate','profit','personalUsd','propUsd','contributionUsd','close','inputType','derivedField','valuationFxRate'].map(k=>[k,row[k]]));
      if(m===key){item.closureStatus='REOPENED';item.reopenedAt=now;item.reopenNote=String(note).trim();}
      else if((item.closureStatus||'FINALIZED')==='FINALIZED'){item.closureStatus='REVIEW_REQUIRED';item.reviewRequiredBy=key;}
      else continue;
      item.updatedAt=now;item.version=(item.version||0)+1;affected.push(m);
      raw.actualHistory.push({id:fxId('fxh'),month:m,at:now,action:m===key?'REOPENED':'BASE_REVIEW_REQUIRED',note:String(note).trim(),before,after:structuredClone(item),...(m===key?{calculationSnapshot}:{} )});
    }
    raw.updatedAt=now;fxAudit('FX_MONTH_REOPENED',key,String(note).trim()+' · reconferência: '+affected.join(', '));
    return {ok:true,month:key,affectedMonths:affected};
  });
}
function fxContributionMonthIssue(raw,month){
  const rec=raw.actuals&&raw.actuals[fxMonthKey(month)];
  return rec&&(rec.closureStatus||'FINALIZED')!=='REOPENED'?'Depósitos de mês finalizado ou em reconciliação estão protegidos. Reabra o mês explicitamente antes de alterar.':'';
}
function fxPlanAddContribution(input){
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw();
    if(!raw) return {ok:false,errors:['Nenhum planejamento ativo.']};
    const rec=fxNormalizeContribution({...input, id:'', createdAt:new Date().toISOString()});
    const errors=fxValidateContribution(rec),protectedIssue=fxContributionMonthIssue(raw,rec.month);
    if(protectedIssue)errors.push(protectedIssue);
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
    const protectedIssue=fxContributionMonthIssue(raw,raw.contributions[idx].month);
    if(protectedIssue)return {ok:false,errors:[protectedIssue]};
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
  const reserves=view.reserves&&view.reserves.observations||{};
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
  fxPlanReviseAssumptions,fxPlanRecordActual,fxPlanFinalizeMonth,fxPlanReopenMonth,fxPlanReconcileMonth,fxPlanAddContribution,
  fxPlanRemoveContribution,fxOverviewLive,fxReservePanelData};

// Commands below extend v1 without rewriting its baseline, historical revisions,
// or unknown fields. All writes still cross fxMutateState exactly once.
function fxPlanningReferences(){
  const p=window.JPWForex&&window.JPWForex.policy&&window.JPWForex.policy.planning;
  return p?{monthly:p.referenceMonthlyReturn,annualRange:p.annualReferenceRange}:null;
}
function fxFutureMonth(raw,month){
  const key=fxMonthKey(month),next=fxNextOpenMonth(fxActivePlan());
  return !!(key&&next&&!(raw.actuals||{})[key]&&key>=next&&key>=raw.baseline.startMonth&&key<fxAddMonths(raw.baseline.startMonth,raw.baseline.horizonMonths));
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
    const wasAbsent=fxMonthIsAbsent(next,month);
    if(wasAbsent&&['rate','personalUsd','propUsd'].some(k=>!Object.prototype.hasOwnProperty.call(patch,k)))return {ok:false,errors:['Preencha rentabilidade e os dois depósitos, inclusive zeros, para restaurar uma previsão retirada.']};
    next.absentMonths={...(next.absentMonths||{})};delete next.absentMonths[month];
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
  if(existing&&(existing.closureStatus||'FINALIZED')==='FINALIZED')return {ok:false,errors:['Mês finalizado. Reabra antes de importar, mesmo quando a substituição foi confirmada.']};
  if(existing&&options.replace!==true)return {ok:false,errors:['Já existe realizado. Confirme explicitamente a substituição após revisar a origem.']};
  const row=fxForecastTimeline(plan).find(r=>r.month===month);
  if(!row||!Number.isFinite(row.open)||Math.abs(row.open-preview.source.openingBalanceUsd)>0.005)return {ok:false,errors:['Saldo de abertura da Contabilidade difere do realizado/plano. Reconcilie a base antes de importar.']};
  const contributions=fxContributionsByMonth(plan.contributions)[month];
  if(contributions&&contributions.totalUsd!==0)return {ok:false,errors:['O mês tem aportes no planejamento. O ledger diário não discrimina fluxos; reconcilie antes de importar.']};
  return fxPlanRecordActual(month,{inputType:'usd',profitUsd:preview.profitUsd,valuationFxRate:options.valuationFxRate||null,notes:options.notes||'Importação explícita da Contabilidade',source:preview.source,contributionsConfirmed:options.contributionsConfirmed===true});
}
Object.assign(window.JPWFx.state,{fxEnvelopeIssue,fxPlanningReferences,fxPlanReviseFromMonth,fxPlanRebase,fxScenarioSave,fxScenarioDelete,fxPlanImportLedgerActual});

// Removing a forecast is distinct from returning a monthly exception to defaults.
function fxPlanMonthPremiseCommand(month,note,scenarioId,restore){
  const key=fxMonthKey(month);
  return fxMutateState(()=>{
    const raw=fxActivePlanRaw();if(!raw||!fxFutureMonth(raw,key))return {ok:false,errors:['Selecione um mês projetado dentro do horizonte.']};
    if(!String(note||'').trim())return {ok:false,errors:['Informe o motivo da alteração.']};
    const scenario=scenarioId?(raw.scenarios||[]).find(s=>s.id===scenarioId):null;
    if(scenarioId&&!scenario)return {ok:false,errors:['Cenário não encontrado.']};
    const previous=scenario?scenario.assumptions:raw.current,next=structuredClone(previous),now=new Date().toISOString();
    next.absentMonths={...(next.absentMonths||{})};
    if(restore){delete next.absentMonths[key];if(next.monthOverrides)delete next.monthOverrides[key];if(next.plannedContributions)delete next.plannedContributions[key];}
    else next.absentMonths[key]={reason:String(note).trim(),at:now};
    if(scenario){scenario.revisions=scenario.revisions||[];scenario.revisions.push({at:now,month:key,note:String(note),before:structuredClone(previous),rebases:structuredClone(scenario.rebases||[])});scenario.assumptions=next;scenario.version=(scenario.version||0)+1;}
    else fxState().plan=fxReviseAssumptions(raw,next,{note});
    fxAudit(restore?'FX_MONTH_DEFAULTS_RESTORED':'FX_MONTH_FORECAST_REMOVED',key,String(note));return {ok:true,month:key};
  });
}
function fxPlanClearMonth(month,note='Previsão retirada pelo usuário',scenarioId=null){return fxPlanMonthPremiseCommand(month,note,scenarioId,false);}
function fxPlanRestoreMonth(month,note='Retorno explícito às premissas gerais',scenarioId=null){return fxPlanMonthPremiseCommand(month,note,scenarioId,true);}
Object.assign(window.JPWFx.state,{fxPlanClearMonth,fxPlanRestoreMonth,fxPlanFinalizeMonth,fxPlanReopenMonth,fxPlanReconcileMonth});

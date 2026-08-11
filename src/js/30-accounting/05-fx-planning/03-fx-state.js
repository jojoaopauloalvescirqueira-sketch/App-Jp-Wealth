// ============ PLANEJAMENTO FX · ESTADO E MUTAÇÕES (ponte com S) ============
// Única camada autorizada a ler/escrever S.fxPlanning. Leitura para cálculo passa
// por normalização profunda em CÓPIA — o estado persistido preserva campos
// desconhecidos (STATE-SCHEMA.md §3) e a versão limpa nunca é gravada de volta
// sem mutação explícita do operador. Toda mutação valida, audita no
// fxPlanning.auditLog (eventos da especificação, seção 29) e registra em
// dgLogChange — o aviso de "alterações desde o último backup" passa a cobrir o
// Planejamento FX. Nenhum segredo entra no log.

function fxState(){
  if(typeof fxPlanningNormalizeState==='function') fxPlanningNormalizeState();
  return S.fxPlanning;
}
function fxActivePlanRaw(){ return fxState().plan; }
// Cópia normalizada para o motor puro (window.JPWFx.engine).
function fxActivePlan(){
  const raw=fxActivePlanRaw(); if(!raw) return null;
  const baseline=fxNormalizeAssumptions(raw.baseline);
  return {
    id:String(raw.id||''), name:String(raw.name||'Planejamento FX'),
    createdAt:String(raw.createdAt||''), updatedAt:String(raw.updatedAt||''),
    baseline:{...baseline, frozenAt:String((raw.baseline&&raw.baseline.frozenAt)||'')},
    current:{...fxNormalizeAssumptions(raw.current||raw.baseline),
      revisedAt:String((raw.current&&raw.current.revisedAt)||'')},
    revisions:(raw.revisions||[]).map(r=>({
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
function fxSaveState(){ if(typeof save==='function') save(); }

// ---- Mutações ---------------------------------------------------------------
// MVP: um planejamento ativo por vez (seção 31 da especificação).
function fxPlanCreate({name,assumptions}={}){
  const norm=fxNormalizeAssumptions(assumptions);
  const errors=fxValidateAssumptions(norm);
  if(errors.length) return {ok:false,errors};
  const fx=fxState();
  if(fx.plan) return {ok:false,errors:['Já existe um planejamento ativo — o MVP mantém um plano por vez.']};
  fx.plan=fxCreatePlan({name,assumptions:norm});
  fxAudit('FX_PLAN_CREATED',norm.startMonth,`${fx.plan.name} · ${norm.horizonMonths} meses · saldo inicial ${norm.initialBalanceUsd} USD`);
  fxSaveState();
  return {ok:true,plan:fx.plan};
}
// A exclusão apaga plano E trilha do plano; a confirmação explícita é
// responsabilidade da interface (mesmo padrão dos fluxos destrutivos do app).
function fxPlanDelete(){
  const fx=fxState();
  if(!fx.plan) return {ok:false,errors:['Nenhum planejamento ativo.']};
  const label=fx.plan.name;
  fx.plan=null;
  fxAudit('FX_PLAN_DELETED',null,label);
  fxSaveState();
  return {ok:true};
}
// Revisão de premissas de FUTURO. Estruturais (mês inicial, horizonte, saldo
// inicial) permanecem os do baseline — fxReviseAssumptions preserva o snapshot
// anterior em revisions[] e nunca toca o baseline.
function fxPlanReviseAssumptions(next,note){
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
  fxSaveState();
  return {ok:true};
}
// Fechamento mensal: contíguo desde o início do plano (fxNextOpenMonth). Editar
// mês já fechado é permitido, auditado como FX_MONTH_ACTUAL_EDITED e preserva o
// closedAt original — carimbo usado na reconstrução de forecasts anteriores.
function fxPlanRecordActual(month,input){
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
  raw.actuals[key]={...(prev||{}), ...rec,
    closedAt:(prev&&prev.closedAt)?prev.closedAt:now, updatedAt:now};
  raw.updatedAt=now;
  fxAudit(existing?'FX_MONTH_ACTUAL_EDITED':'FX_MONTH_ACTUAL_RECORDED',key,
    rec.inputType==='usd'?`resultado ${rec.profitUsd} USD`:`taxa ${rec.returnRate}`);
  fxSaveState();
  return {ok:true};
}
function fxPlanAddContribution(input){
  const raw=fxActivePlanRaw();
  if(!raw) return {ok:false,errors:['Nenhum planejamento ativo.']};
  const rec=fxNormalizeContribution({...input, id:'', createdAt:new Date().toISOString()});
  const errors=fxValidateContribution(rec);
  if(errors.length) return {ok:false,errors};
  (raw.contributions=raw.contributions||[]).push(rec);
  raw.updatedAt=new Date().toISOString();
  fxAudit('FX_CONTRIBUTION_RECORDED',rec.month,
    `${rec.source==='prop'?'Prop Firm':'Pessoal'} · ${rec.usdAmount} USD${rec.affectsFxCostBasis?` @ R$ ${rec.acquisitionFxRate}`:' (USD nativo — fora do custo médio)'}`);
  fxSaveState();
  return {ok:true,contribution:rec};
}
function fxPlanRemoveContribution(id){
  const raw=fxActivePlanRaw();
  if(!raw) return {ok:false,errors:['Nenhum planejamento ativo.']};
  const idx=(raw.contributions||[]).findIndex(c=>c&&c.id===id);
  if(idx<0) return {ok:false,errors:['Aporte não encontrado.']};
  const [gone]=raw.contributions.splice(idx,1);
  raw.updatedAt=new Date().toISOString();
  fxAudit('FX_CONTRIBUTION_REMOVED',fxMonthKey(gone&&gone.month)||null,
    `${gone&&gone.source==='prop'?'Prop Firm':'Pessoal'} · ${gone?gone.usdAmount:''} USD`);
  fxSaveState();
  return {ok:true};
}

// ---- Leitura consolidada ----------------------------------------------------
function fxOverviewLive(){
  const plan=fxActivePlan();
  return plan?{plan,...fxOverview(plan)}:null;
}
// Painel normativo: FCR/FEO SEMPRE pela função pura compartilhada (10-domain/07)
// com as fontes canônicas — capital nominal da Conta Mestre em S.params.saldoIni
// (mesma derivação de reserveMasterCapital) e despesas/constituídos declarados
// no onboarding. Nenhuma segunda fonte, nenhuma constante duplicada.
function fxReservePanelData(){
  const ob=S.onboarding||{};
  const parse=v=>parseFloat(String(v||'').replace(',','.'))||0;
  return reserveRequirementsCalc({
    capital:+(S.params&&S.params.saldoIni)||0,
    fcrCurrent:parse(ob.reserveFcrCurrent),
    monthlyExpenses:parse(ob.reserveMonthlyExpenses),
    feoCurrent:parse(ob.reserveFeoCurrent)
  });
}

window.JPWFx.state={fxState,fxActivePlanRaw,fxActivePlan,fxPlanCreate,fxPlanDelete,
  fxPlanReviseAssumptions,fxPlanRecordActual,fxPlanAddContribution,
  fxPlanRemoveContribution,fxOverviewLive,fxReservePanelData};

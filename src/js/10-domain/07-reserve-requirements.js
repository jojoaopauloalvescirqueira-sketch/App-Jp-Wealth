// Compatibility projection for onboarding/planning. Normative requirements are
// calculated only by the versioned Forex engine. Legacy SI/monthly fields are
// not a substitute for nominal Mestre capital or a documented six-month amount.
function reserveRequirementsCalc(input={}){
  const e=JPWForex.engine,n=v=>typeof v==='number'&&Number.isFinite(v)?v:null;
  const fcr=e.computeFCRRequirement({capitalNominal:n(input.capitalNominal),si:n(input.si)});
  const feo=e.computeFEORequirement({sixMonthExpenseAmount:n(input.sixMonthExpenseAmount),
    determinationRecorded:input.determinationRecorded===true,expensesApproved:input.expensesApproved===true});
  const fcrReq=fcr.status==='OK'?fcr.value:null,feoReq=feo.status==='OK'?feo.value:null;
  const fcrCur=n(input.fcrCurrent),feoCur=n(input.feoCurrent),monthly=n(input.monthlyExpenses);
  const coverage=(cur,req)=>cur!==null&&req>0?cur/req*100:null;
  const difference=(cur,req)=>cur!==null&&req!==null?cur-req:null;
  const status=(cur,req)=>cur===null||req===null?'Pendente':cur<req?'Insuficiente':'Constituído — verificar governança';
  const fcrStatus=status(fcrCur,fcrReq),feoStatus=status(feoCur,feoReq);
  const hasDeficit=(fcrReq!==null&&fcrCur!==null&&fcrCur<fcrReq)||(feoReq!==null&&feoCur!==null&&feoCur<feoReq);
  return {capital:n(input.capitalNominal),masterCapital:n(input.capitalNominal),fcrReq,feoReq,fcrCur,feoCur,
    fcrStatus,feoStatus,monthly,fcrCoverage:coverage(fcrCur,fcrReq),feoCoverage:coverage(feoCur,feoReq),
    // Informational quotient is not the approved method of apuração.
    feoMonths:monthly>0&&feoCur!==null?feoCur/monthly:null,
    fcrDiff:difference(fcrCur,fcrReq),feoDiff:difference(feoCur,feoReq),hasDeficit,
    generalStatus:hasDeficit?'Déficit registrado':fcrReq===null||feoReq===null?'Requisitos não calculáveis':'Constituição informada; elegibilidade depende de governança',
    generalTone:hasDeficit?'var(--f4)':'var(--ink-dim)',status:'PENDING_GOVERNANCE',
    requirements:{fcr,feo},findings:[...fcr.findings,...feo.findings]};
}

// ============ RESERVAS ESTATUTÁRIAS · FUNÇÃO PURA COMPARTILHADA (FCR/FEO) ============
// Fonte normativa: Estatuto V10 — Art. 13.1 (FCR ≥ 15% do capital nominal da Conta
// Mestre), Art. 13.2 (FEO ≥ 6 meses das despesas pessoais, operacionais e
// administrativas elegíveis) e Art. 26.2 (os mínimos absolutos prevalecem sobre o
// bloco macro de 15%).
// Extraída de reserveCalc() (04-onboarding.js) por decisão do gestor de 2026-08-11:
// o onboarding e o Planejamento FX consomem ESTA função — constante única, sem
// snapshot como fonte permanente. A matemática é idêntica à original; o teste de
// caracterização em tools/fx_planning_test.py compara campo a campo.
// Entradas canônicas (responsabilidade do chamador):
//   capital          → capital nominal da Conta Mestre (fonte: S.params.saldoIni)
//   monthlyExpenses  → despesas mensais elegíveis (fonte: onboarding)
//   fcrCurrent/feoCurrent → valores efetivamente constituídos, declarados
function reserveRequirementsCalc({capital,fcrCurrent,monthlyExpenses,feoCurrent}){
  const cap=Number.isFinite(+capital)?+capital:0;
  const fcrCur=Number.isFinite(+fcrCurrent)?+fcrCurrent:0;
  const monthly=Number.isFinite(+monthlyExpenses)?+monthlyExpenses:0;
  const feoCur=Number.isFinite(+feoCurrent)?+feoCurrent:0;
  const fcrReq=cap*0.15;
  const feoReq=monthly*6;
  const fcrCoverage=fcrReq>0?(fcrCur/fcrReq)*100:0;
  const feoCoverage=feoReq>0?(feoCur/feoReq)*100:0;
  const feoMonths=monthly>0?feoCur/monthly:0;
  const fcrStatus=fcrCur>=fcrReq?'Regular':'Insuficiente';
  const feoStatus=feoCur>=feoReq?'Regular':'Insuficiente';
  const regularCount=(fcrStatus==='Regular'?1:0)+(feoStatus==='Regular'?1:0);
  return {
    capital:cap,
    fcrReq,
    fcrCur,
    fcrStatus,
    monthly,
    feoReq,
    feoCur,
    feoStatus,
    fcrCoverage,
    feoCoverage,
    feoMonths,
    fcrDiff:fcrCur-fcrReq,
    feoDiff:feoCur-feoReq,
    generalStatus:regularCount===2?'Reservas regulares':(regularCount===1?'Reservas parcialmente insuficientes':'Reservas críticas'),
    generalTone:regularCount===2?'var(--f1)':(regularCount===1?'var(--f2)':'var(--f4)'),
    hasDeficit:(fcrCur<fcrReq)||(feoCur<feoReq)
  };
}

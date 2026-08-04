// ============ CÁLCULOS ============
function compute(){
  const p=S.params;
  // --- Drawdown Operacional — Art. 3.4§2: tudo sobre o Saldo Inicial.
  // DD estatutário = risco aberto + perdas fechadas da operação atual + perdas arquivadas.
  //  · prejuízo fechado NÃO some do termômetro (netOp negativo soma ao DD);
  //  · Lucro Técnico é informativo/patrimonial, mas não amplia teto absoluto nem mascara risco real;
  //  · lucro de operação ARQUIVADA não amortece nada (Art. 4.3 / Proibição de Merge).
  let loteAberto=0, riscoAberto=0, lucroTecnico=0, notionalAberto=0, semStop=0;
  S.phases.forEach(ph=>ph.orders.forEach(o=>{
    if(o.status==='Aberta'){
      riscoAberto += orderRisk(o);
      loteAberto += (+o.lote||0);
      notionalAberto += orderNotional(o);
      if(o.lote>0 && !(o.sl>0)) semStop++;
    } else if(o.status==='Fechada'){
      lucroTecnico += Math.max(0, (+o.result||0)); // só o que foi lucro, per Art. 9.2
    }
  }));
  const netOp=netOpAtual();
  const perdaAtual=Math.max(0,-netOp);
  const perdaCiclo=perdaCicloArq();
  const lucroArquivado=Math.max(0,S.cycleRealizado||0);
  const riscoTotal=riscoAberto;
  const loteTotal=loteAberto;
  const riscoEstatutario = riscoAberto + perdaAtual + perdaCiclo;
  const ddDollar = riscoEstatutario;
  const dd = p.saldoIni>0 ? ddDollar/p.saldoIni : 0;
  // SET 11 — fator do perfil escolhido escala a Matriz Quadrifásica inteira (Base=1.0 = comportamento antigo)
  const profileFator=activeProfileFator();
  const mScaled=activeRiskMatrix();
  const mddScaled=activeMDDLimit(), alarmScaled=activeAlarmLimit();
  // fase vigente
  let fi=0;
  if(dd>mScaled[2].ddmax) fi=3; else if(dd>mScaled[1].ddmax) fi=2; else if(dd>mScaled[0].ddmax) fi=1; else fi=0;
  const fase=mScaled[fi];
  const tetoAlav=fase.alav;
  const tetoRisco=fase.ddmax*p.saldoIni;
  const alavCar = p.saldoIni>0 ? notionalAberto/p.saldoIni : 0; // Art. 3.4§2: base sempre saldo inicial
  // orçamento de risco NOVO: lucro não amplia (Cláusula de Integridade) — só perdas encolhem
  const orcamentoUsado = riscoEstatutario;
  const excesso = Math.max(0, orcamentoUsado-tetoRisco);
  const margemEstatutaria = Math.max(0, tetoRisco-riscoEstatutario);
  const margemInformativa = Math.max(0, tetoRisco+lucroTecnico-riscoEstatutario);
  // VRM
  const vrm = S.atr660>0 ? S.atr55/S.atr660 : 0;
  const regime = vrm>p.vrmHV?'ALTA VOL':(vrm>p.vrmN?'TRANSIÇÃO':'NORMAL');
  // status
  let status, sbCls, ico;
  if(dd>=mddScaled){status='GUILHOTINA — ENCERRAR TUDO + QUARENTENA 90D'; sbCls='sb-danger'; ico='🔴';}
  else if(dd>=alarmScaled){status='ALARME — REDUÇÃO IMEDIATA DE EXPOSIÇÃO'; sbCls='sb-danger'; ico='🔴';}
  else if(excesso>0){status='INCOERÊNCIA — RISCO ACIMA DO TETO DA FASE (PODAR)'; sbCls='sb-alert'; ico='🟠';}
  else if(semStop>0){status='ORDEM ABERTA SEM STOP — VIOLAÇÃO DE PROTOCOLO'; sbCls='sb-alert'; ico='🟠';}
  else if(dd>mScaled[1].ddmax){status=fase.nome+' — CONTROLE DE DANOS'; sbCls='sb-alert'; ico='🟠';}
  else if(dd>mScaled[0].ddmax){status=fase.nome+' — DESACELERAR'; sbCls='sb-warn'; ico='🟡';}
  else {status='FASE 1 — OPERACIONAL NORMAL'; sbCls='sb-good'; ico='🟢';}
  // semaforo coerencia
  let sem, semCls, sug;
  if(excesso>0){
    sem='🟠 PODAR LIFO — risco acima do teto da fase'; semCls='var(--f3)';
    sug=`Pode as ordens <b>mais recentes</b> (fase mais avançada primeiro: F4→F3→F2) até liberar <b>${fmtMoney(excesso)}</b> de risco. Preserve a Gênese e as primeiras defesas estruturais.`;
  }else if(semStop>0){
    sem='🟠 '+semStop+' ordem(ns) aberta(s) SEM STOP'; semCls='var(--f3)';
    sug='Toda ordem aberta precisa de SL registrado (Função de Auditoria). Sem stop, o risco não é mensurável — defina o SL imediatamente ou feche a posição.';
  }else if(alavCar>tetoAlav){
    sem='🟡 ALAVANCAGEM acima do teto da fase'; semCls='var(--f2)';
    sug=`Alavancagem carregada (<b>${fmtX(alavCar)}</b>) acima do teto da fase (<b>${fmtX(tetoAlav)}</b>). Reduza lote via LIFO — encerre as defesas mais recentes até enquadrar a alavancagem, mesmo que o risco em $ ainda caiba.`;
  }else{
    sem='🟢 COERENTE — risco e alavancagem dentro da fase'; semCls='var(--f1)';
    sug='Nenhuma poda necessária — risco e alavancagem coerentes com a fase.';
  }
  // banner de status só aparece em EXCEÇÃO (guilhotina/alarme/incoerência/sem stop) —
  // o estado normal da fase já é comunicado pelo card de postura (SET 5 do 2º lote)
  const excecao = dd>=mddScaled || dd>=alarmScaled || excesso>0 || semStop>0;
  return {dd,ddDollar,fi,fase,tetoAlav,tetoRisco,loteTotal,riscoTotal,riscoEstatutario,lucroTecnico,netOp,perdaAtual,perdaCiclo,lucroArquivado,margemEstatutaria,margemInformativa,semStop,alavCar,excesso,vrm,regime,status,sbCls,ico,sem,semCls,sug,excecao,profileFator,mddScaled,alarmScaled,mScaled};
}
function noExternalProtectionActive(){
  return !!(S.onboarding && S.onboarding.done && S.onboarding.epStatus==='Não vou utilizar.');
}
function noExternalProtectionWarning(){
  return 'Proteção externa desativada: este período está operando sem Equity Protector. Controle manual obrigatório. Risco aumentado de violação operacional.';
}
function shouldWarnManualRiskConfirmation(){
  const c=compute();
  const sameDayLoss=Array.isArray(S.ledger) && S.ledger.some(e=>e && e.data===todayISO() && (+e.result||0)<0);
  return noExternalProtectionActive() && (
    c.dd>0 || c.fi>0 || c.riscoTotal>=0.8*c.tetoRisco || isPropFirm(brokerFor(S.onboarding&&S.onboarding.corretora)||{}) || sameDayLoss
  );
}

// ============ EXECUTION CLEARANCE — veredito antes dos termômetros ============
function renderExecClearance(c){
  const card=$('execClearanceCard'); if(!card) return;
  c=c||compute();
  const model=c.forex,known=value=>typeof value==='number'&&Number.isFinite(value);
  const money=value=>known(value)?fmtForexMoney(value,c.forex.account,0):'Não calculável';
  const multiple=value=>known(value)?fmtX(value):'Não calculável';
  const percent=value=>known(value)?fmtPct(value):'Não calculável';
  const r=getOperationalClearance(c);
  const COLORS={clear:'var(--f1)',caution:'var(--f2)',pending:'var(--violet)',reduce:'var(--f3)',blocked:'var(--f4)'};
  card.style.setProperty('--mc', COLORS[r.status]);
  $('ecTitle').textContent=r.title;
  // ação específica de execução — mesmas condições de compute(), sem lógica nova
  let acao;
  if(model.accountPhase.compulsoryClose)acao='Encerramento compulsório e registro de quarentena. P-24 não permite presumir prazo de retorno.';
  else if(quarantineActive())acao='Quarentena registrada — retorno ainda não autorizado. Registros e redução permanecem acessíveis.';
  else if(c.semStop>0)acao='Definir e validar o stop de '+c.semStop+' ordem(ns). Risco atual não calculável; não confundir o registro com autorização.';
  else if(known(c.alavCar)&&known(c.tetoAlav)&&c.alavCar>c.tetoAlav)acao='Exposição acima do teto da fase da conta: reduzir conforme o contrato, preservando o registro dos fatos.';
  else acao='P-14/P-17/P-18 pendentes: execução normativa bloqueada. Examine os dados e requisitos no Motor Forex.';
  $('ecAcao').textContent=acao;
  $('ecFase').textContent=c.fase.nome;
  $('ecGrade').textContent=model.activeGridPhase.status==='OK'?'FASE '+model.activeGridPhase.value+' · grade declarada':'Grade não identificada';
  // Fase 2C — fidelidade ao protótipo: o TETO vai para o rótulo e o valor
  // carrega só o número corrente. Mesmas fontes, nenhuma fórmula nova.
  const setTxt=(id,v)=>{ const e=$(id); if(e) e.textContent=v; };
  const setBar=(id,pct,color)=>{ const e=$(id); if(e){ e.style.visibility=known(pct)?'':'hidden';e.style.width=(known(pct)?Math.max(0,Math.min(100,pct)):0)+'%'; e.style.background=color; } };
  setTxt('ecRiscoLbl','Risco agregado · TRA pendente');
  setTxt('ecRisco', money(c.riscoTotal));
  setTxt('ecAlavLbl','Alav. / Teto '+multiple(c.tetoAlav));
  setTxt('ecAlav', multiple(c.alavCar));
  // DRAWDOWN entra no cockpit do Execution Board: era o fato que os termômetros
  // removidos carregavam. Mesma escala do gauge (teto ativo do perfil).
  setTxt('ecDD', percent(c.dd));
  setTxt('ecDDsub','limite '+percent(c.mddScaled));
  setBar('ecDDbar',known(c.dd)&&c.mddScaled>0?c.dd/c.mddScaled*100:null,model.accountPhase.compulsoryClose?'var(--f4)':'var(--f1)');
  setBar('ecRiscoBar',null,'var(--ink-dim)');
  setBar('ecAlavBar',known(c.alavCar)&&known(c.tetoAlav)&&c.tetoAlav>0?c.alavCar/c.tetoAlav*100:null,known(c.alavCar)&&known(c.tetoAlav)&&c.alavCar>c.tetoAlav?'var(--f3)':'var(--f1)');
}

// ---- Execution Board phases ----

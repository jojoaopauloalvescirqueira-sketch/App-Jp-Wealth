// ============ EXECUTION CLEARANCE — veredito antes dos termômetros ============
function renderExecClearance(c){
  const card=$('execClearanceCard'); if(!card) return;
  const r=getOperationalClearance(c);
  const COLORS={clear:'var(--f1)',caution:'var(--f2)',pending:'var(--violet)',reduce:'var(--f3)',blocked:'var(--f4)'};
  card.style.setProperty('--mc', COLORS[r.status]);
  $('ecTitle').textContent=r.title;
  // ação específica de execução — mesmas condições de compute(), sem lógica nova
  let acao;
  if(quarantineActive()) acao='Não abrir novas posições — quarentena ativa (Art. 3.10).';
  else if(c.dd>=c.mddScaled) acao='Encerrar tudo e formalizar quarentena (guilhotina — Art. 3.10).';
  else if(c.semStop>0) acao='Definir stop imediatamente — '+c.semStop+' ordem(ns) sem SL.';
  else if(c.excesso>0) acao='Reduzir exposição via LIFO — podar '+fmtMoney(c.excesso)+' (F4→F3→F2).';
  else if(c.alavCar>c.tetoAlav) acao='Reduzir lote via LIFO até reenquadrar a alavancagem no teto da fase.';
  else if(c.dd>=c.alarmScaled) acao='Alarme operacional — reduzir exposição antes da guilhotina.';
  else acao='Nenhuma poda necessária — risco e alavancagem coerentes com a fase.';
  $('ecAcao').textContent=acao;
  $('ecFase').textContent=c.fase.nome;
  const dg=$('dpGrade'); $('ecGrade').textContent=(dg&&dg.textContent)||'—';
  // Fase 2C — fidelidade ao protótipo: o TETO vai para o rótulo e o valor
  // carrega só o número corrente. Mesmas fontes, nenhuma fórmula nova.
  const setTxt=(id,v)=>{ const e=$(id); if(e) e.textContent=v; };
  setTxt('ecRiscoLbl','Risco / Teto '+fmtMoney(c.tetoRisco));
  setTxt('ecRisco', fmtMoney(c.riscoTotal));
  setTxt('ecAlavLbl','Alav. / Teto '+fmtX(c.tetoAlav));
  setTxt('ecAlav', fmtX(c.alavCar));
  // DRAWDOWN entra no cockpit do Execution Board: era o fato que os termômetros
  // removidos carregavam. Mesma escala do gauge (teto ativo do perfil).
  setTxt('ecDD', fmtPct(c.dd));
  setTxt('ecDDsub','de '+fmtPct(c.mddScaled>0?c.mddScaled:0.15));
}

// ---- Execution Board phases ----

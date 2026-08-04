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
  $('ecRisco').textContent=fmtMoney(c.riscoTotal)+' / '+fmtMoney(c.tetoRisco);
  $('ecAlav').textContent=fmtX(c.alavCar)+' / '+fmtX(c.tetoAlav);
}

// ---- Execution Board phases ----

// ============ OPERATIONAL CLEARANCE — veredito executivo (N1) ============
// "Posso operar agora?" — derivado exclusivamente de compute() + estado salvo (S.onboarding).
// Severidade: clear < caution < pending < reduce < blocked.
function getOperationalClearance(c){
  c = c || compute();
  const ob=S.onboarding||{};
  const reasons=[];
  let status='clear';
  const RANK={clear:0,caution:1,pending:2,reduce:3,blocked:4};
  const bump=(lvl)=>{ if(RANK[lvl]>RANK[status]) status=lvl; };
  // BLOQUEIO — quarentena / guilhotina (Art. 3.10)
  if(quarantineActive()){ bump('blocked'); reasons.push('Quarentena operacional ativa (Art. 3.10) — apenas encerramento de posições até '+(S.quarantine&&S.quarantine.fim||'—')+'.'); }
  if(c.dd>=c.mddScaled){ bump('blocked'); reasons.push('DD '+fmtPct(c.dd)+' atingiu o MDD ativo de '+fmtPct(c.mddScaled)+' — guilhotina estatutária.'); }
  else if(c.dd>=c.alarmScaled){ bump('reduce'); reasons.push('Alarme operacional: DD '+fmtPct(c.dd)+' ≥ '+fmtPct(c.alarmScaled)+' — redução imediata.'); }
  // REDUZIR — violações de enquadramento da fase
  if(c.excesso>0){ bump('reduce'); reasons.push('Risco aberto acima do teto da fase — podar '+fmtMoney(c.excesso)+' via LIFO.'); }
  if(c.semStop>0){ bump('reduce'); reasons.push(c.semStop+' ordem(ns) aberta(s) sem stop — risco não mensurável, defina o SL.'); }
  if(c.alavCar>c.tetoAlav){ bump('reduce'); reasons.push('Alavancagem carregada ('+fmtX(c.alavCar)+') acima do teto da fase ('+fmtX(c.tetoAlav)+').'); }
  // PENDÊNCIAS — governança patrimonial / cadastro do período
  if(!ob.done){ bump('pending'); reasons.push('Formulário de Início de Período pendente — complete o questionário.'); }
  const fcrBad = ob.done && ob.reserveFcrStatus && ob.reserveFcrStatus!=='Regular';
  const feoBad = ob.done && ob.reserveFeoStatus && ob.reserveFeoStatus!=='Regular';
  if(fcrBad||feoBad){ bump('pending'); reasons.push('Reservas segregadas abaixo do mínimo estatutário ('+[fcrBad?'FCR':'',feoBad?'FEO':''].filter(Boolean).join(' e ')+') — Título 13.'); }
  if(ob.done && ob.centralCashStatus==='Não.'){ bump('pending'); reasons.push('Caixa Central ausente — rastreabilidade patrimonial fragilizada (Título 27).'); }
  // CAUTELA — atenção sem bloqueio estatutário
  if(noExternalProtectionActive()){ bump('caution'); reasons.push('Proteção externa (Equity Protector) desativada — confirmação manual de risco obrigatória.'); }
  if(ob.done && ob.centralCashStatus==='Em implantação.'){ bump('caution'); reasons.push('Caixa Central em implantação — conclua o livro-razão patrimonial.'); }
  if(c.fi>0 && RANK[status]<RANK.reduce){ bump('caution'); reasons.push(c.fase.nome+' — opere dentro do teto reduzido da fase ('+fmtX(c.tetoAlav)+' · '+fmtMoney(c.tetoRisco)+').'); }
  const MAP={
    clear:{title:'Liberado para operar', subtitle:'Risco, reservas, caixa e proteção externa sem pendências críticas.', action:'Executar apenas setups válidos dentro da fase vigente.'},
    caution:{title:'Operar com cautela', subtitle:'Há pontos de atenção ativos — nenhum bloqueio estatutário.', action:'Verificar drawdown, exposição e fase antes de qualquer registro.'},
    pending:{title:'Corrigir pendências antes de operar', subtitle:'Governança patrimonial ou cadastro do período incompletos.', action:'Resolver as pendências listadas ou formalizar ciência no Formulário de Início.'},
    reduce:{title:'Reduzir exposição', subtitle:'O risco atual viola o enquadramento da fase vigente.', action:'Reduzir exposição via LIFO (mais recentes primeiro) até reenquadrar a fase.'},
    blocked:{title:'Operação bloqueada', subtitle:'Quarentena/guilhotina estatutária ativa. Apenas encerramento de posições permitido.', action:'Não abrir novas operações. Registrar o evento na auditoria.'}
  };
  const m=MAP[status];
  return {status, title:m.title, subtitle:m.subtitle, reasons, action:m.action};
}
function renderOperationalClearance(c){
  const card=$('mcClearanceCard'); if(!card) return;
  const r=getOperationalClearance(c);
  const ob=S.onboarding||{};
  card.className='card mc-hero mc-status-'+r.status;
  const dot=$('mcClearanceDot');
  if(dot){ dot.style.background='var(--mc)'; dot.style.boxShadow='0 0 10px var(--mc)'; }
  $('mcClearanceTitle').textContent=r.title;
  $('mcClearanceSub').textContent=r.subtitle;
  const ul=$('mcClearanceReasons');
  const items=r.reasons.slice(0,3).map(x=>'<li>'+esc(x)+'</li>');
  if(r.reasons.length>3) items.push('<li>+'+(r.reasons.length-3)+' ponto(s) adicional(is) — detalhes no Execution Board.</li>');
  ul.innerHTML=items.join('');
  ul.style.display=items.length?'grid':'none';
  $('mcClearanceAction').innerHTML='<span class="ak">Ação</span>'+esc(r.action);
  // N2 — Mission Metrics (status executivos)
  const set=(id,txt)=>{ const e=$(id); if(e) e.textContent=txt; };
  const chip=(id,cls,txt)=>{ const e=$(id); if(e){ e.className='mc-status '+cls; e.textContent=txt; } };
  set('mcMiniRisco', fmtMoney(c.riscoTotal)+' / '+fmtMoney(c.tetoRisco));
  // Reservas FCR/FEO — lidos do estado salvo no onboarding (fonte única)
  if(!ob.done || !ob.reserveFcrStatus){
    set('mcMiniReservas','—'); chip('mcMiniReservasChip','mc-st-muted','Pendente');
  } else {
    const fcrPct=ob.reserveFcrCoveragePct?Math.round(+ob.reserveFcrCoveragePct)+'%':'—';
    const feoM=ob.reserveFeoMonthsCovered?(+ob.reserveFeoMonthsCovered).toFixed(1).replace('.',',')+'m':'—';
    set('mcMiniReservas','FCR '+fcrPct+' · FEO '+feoM);
    const fcrOk=ob.reserveFcrStatus==='Regular', feoOk=ob.reserveFeoStatus==='Regular';
    if(fcrOk&&feoOk) chip('mcMiniReservasChip','mc-st-good','Regular');
    else if(fcrOk||feoOk) chip('mcMiniReservasChip','mc-st-warn','Parcial');
    else chip('mcMiniReservasChip','mc-st-bad','Crítico');
  }
  // Caixa Central
  if(!ob.done || !ob.centralCashStatus){
    set('mcMiniCaixa','—'); chip('mcMiniCaixaChip','mc-st-muted','Pendente');
  } else {
    set('mcMiniCaixa', ob.centralCashTraceabilityScore?('Score '+ob.centralCashTraceabilityScore+'/100'):'sem score');
    if(ob.centralCashStatus==='Sim.') chip('mcMiniCaixaChip','mc-st-good','Funcional');
    else if(ob.centralCashStatus==='Em implantação.') chip('mcMiniCaixaChip','mc-st-warn','Implantação');
    else chip('mcMiniCaixaChip','mc-st-bad','Ausente');
  }
  // Equity Protector
  if(!ob.done || !ob.epStatus){
    set('mcMiniEP','—'); chip('mcMiniEPChip','mc-st-muted','Pendente');
  } else if(ob.epStatus==='Sim, vou utilizar.'){
    set('mcMiniEP', ob.epPlatform==='Outra.'?(ob.epPlatformOther||'Ativo'):(ob.epPlatform||'Ativo'));
    chip('mcMiniEPChip','mc-st-good','Ativo');
  } else if(ob.epStatus==='Não vou utilizar.'){
    set('mcMiniEP','Controle manual'); chip('mcMiniEPChip','mc-st-bad','Desativado');
  } else if(ob.epStatus==='Não se aplica a esta conta.'){
    set('mcMiniEP','Não se aplica'); chip('mcMiniEPChip','mc-st-muted','N/A');
  } else {
    set('mcMiniEP','Em configuração'); chip('mcMiniEPChip','mc-st-warn','Pendente');
  }
  // Pendências do Formulário de Início — governança/documentação, separada do bloqueio operacional.
  const onb=getOnboardingCompletionState();
  if(onb.complete){
    set('dStatus','Formulário completo');
    chip('mcMiniPendChip','mc-st-good','7/7');
  } else {
    const label=onb.critical?`${onb.critical} pendência crítica`:(onb.warning?`${onb.warning} atenção`:`${onb.pending} pendente(s)`);
    set('dStatus', label);
    chip('mcMiniPendChip',onb.critical?'mc-st-bad':(onb.warning?'mc-st-warn':'mc-st-muted'),`${onb.completed}/${onb.total}`);
  }
}

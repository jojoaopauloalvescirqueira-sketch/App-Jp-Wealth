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
  // Linha de fatos do card de Clearance (fidelidade ao Dashboard Claro) —
  // mesmos valores de c.fase/c.riscoTotal/c.tetoRisco/c.alavCar/c.tetoAlav
  // já usados em mcMiniRisco/dAlav/dFase; só um novo local de leitura.
  // ---- COCKPIT · quatro fatos operacionais (JPW-789ABC-B2, Fase 2A) ----
  // ESPELHO DE LEITURA: cada célula reusa a MESMA fórmula que o componente
  // vigente já aplica; nenhuma é reescrita e nenhuma constante é criada.
  //   DD          ddCeil / (dd/ddCeil) e as faixas de c.mScaled — do gdGaugeDD
  //   Risco       riscoTotal/tetoRisco — da barra gRiscoBar e do card Coerência
  //   Alavancagem alavCar/4 com tick do teto em tetoAlav/4 — do gdGaugeAlav
  //   Cores       as MESMAS regras já vigentes: gRiscoBar usa --f3 acima do
  //               teto, gAlavBar usa --f2, ambas FCOLORS[c.fi] dentro dele.
  // Os componentes antigos seguem na tela nesta fase justamente para que a
  // equivalência seja verificável a olho: qualquer divergência é defeito daqui.
  const cockpitFact=(id,o)=>{
    const cell=$(id); if(!cell) return;
    const v=cell.querySelector('[data-fact-v]');
    if(v){ v.textContent=o.value; v.style.color=o.over?o.color:''; }
    const m=cell.querySelector('[data-fact-meta]'); if(m) m.textContent=o.meta;
    const f=cell.querySelector('[data-fact-fill]');
    if(f){
      // Nunca passa de 100%: estouro é dito por cor e por texto, jamais por
      // transbordo geométrico da barra.
      f.style.width=(o.pct==null?0:Math.max(0,Math.min(100,o.pct)))+'%';
      if(o.color) f.style.background=o.color;
    }
    const k=cell.querySelector('[data-fact-mark]');
    if(k){
      if(o.markPct==null) k.style.display='none';
      else { k.style.display=''; k.style.left='calc('+Math.max(0,Math.min(100,o.markPct))+'% - 1px)'; }
    }
    cell.dataset.over=o.over?'1':'0';
  };
  // FASE — categórica: quatro segmentos, o vigente aceso. Não existe
  // "percentual de fase"; uma barra contínua aqui seria dado inventado.
  const faseCell=$('mcFactFase');
  const segWrap=faseCell && faseCell.querySelector('[data-fact-seg-wrap]');
  if(segWrap) Array.prototype.forEach.call(segWrap.children,(seg,i)=>{
    seg.style.background = (i===c.fi) ? FCOLORS[c.fi] : '';
  });
  const faixaFase = c.mScaled ? fmtPct(c.mScaled[c.fi].ddmin)+'–'+fmtPct(c.mScaled[c.fi].ddmax) : '—';
  cockpitFact('mcFactFase',{ value:c.fase.nome, meta:'faixa de DD '+faixaFase, pct:null, markPct:null, over:false });
  // DRAWDOWN — escala 0 → teto ativo do perfil (mesma ddCeil do gauge), com
  // marcador no limite da fase vigente. Exceção = atingir o MDD ativo, que é o
  // mesmo gatilho que já dispara o aviso de quarentena (Art. 3.10).
  const ddCeil=(c.mddScaled>0?c.mddScaled:0.15);
  const ddOver=c.mddScaled>0 && c.dd>=c.mddScaled;
  cockpitFact('mcFactDD',{
    value:fmtPct(c.dd),
    meta:'de '+fmtPct(ddCeil)+(ddOver?' · NO LIMITE ATIVO':(c.mScaled?' · limite da fase '+fmtPct(c.mScaled[c.fi].ddmax):'')),
    pct:(c.dd/ddCeil)*100,
    markPct:c.mScaled?(c.mScaled[c.fi].ddmax/ddCeil)*100:null,
    color:ddOver?'var(--f4)':FCOLORS[c.fi], over:ddOver
  });
  // RISCO ABERTO — escala 0 → teto da fase. Teto zero (conta sem parâmetro)
  // não vira barra cheia falsa nem divisão por zero: mostra trilho vazio.
  const temTetoRisco=c.tetoRisco>0;
  const riscoPct=temTetoRisco?(c.riscoTotal/c.tetoRisco)*100:0;
  const riscoOver=temTetoRisco && c.riscoTotal>c.tetoRisco;
  cockpitFact('mcFactRisco',{
    value:fmtMoney(c.riscoTotal),
    meta:temTetoRisco
      ? Math.round(riscoPct)+'% do teto · '+fmtMoney(c.tetoRisco)+(riscoOver?' · ACIMA DO TETO':'')
      : 'sem parâmetro de teto',
    pct:riscoPct, markPct:null,
    color:riscoOver?'var(--f3)':FCOLORS[c.fi], over:riscoOver
  });
  // ALAVANCAGEM — escala absoluta 0–4x com tick no teto da fase, igual ao
  // gdGaugeAlav (mostra folga contra o máximo estatutário, não só contra o teto).
  const alavOver=c.alavCar>c.tetoAlav;
  cockpitFact('mcFactAlav',{
    value:fmtX(c.alavCar),
    meta:'teto '+fmtX(c.tetoAlav)+(alavOver?' · ACIMA DO TETO':' · escala 0–4x'),
    pct:(c.alavCar/4)*100, markPct:(c.tetoAlav/4)*100,
    color:alavOver?'var(--f2)':FCOLORS[c.fi], over:alavOver
  });
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
  // Faixa de postura/conformidade (fidelidade ao Claude Design) — só estados
  // reais já calculados em outro lugar do próprio código: PHASE_OBJECTIVE[c.fi]
  // (mesmo dado do objectiveCard do Execution Board), c.excesso, c.alavCar/
  // c.tetoAlav (mesma condição de gAlavBar) e onb (mesma fonte do dStatus
  // acima). Nenhuma checagem nova, nenhum texto fixo — muda com o estado real.
  const posture=(prefix,label,sub,color)=>{
    const l=$(prefix+'Lbl'), s=$(prefix+'Sub');
    if(l){ l.textContent=label; l.style.color=color; }
    if(s) s.textContent=sub;
  };
  const po=PHASE_OBJECTIVE[c.fi];
  posture('gdPostureFase', po.t, 'Fase '+(c.fi+1)+' vigente — postura determinada pela fase atual.', 'var('+OBJ_COL[c.fi]+')');
  posture('gdPostureRisco',
    c.excesso>0?'Risco Acima do Teto':'Risco Controlado',
    c.excesso>0?('Exceder o teto em '+fmtMoney(c.excesso)+' — poda necessária.'):'Dentro dos limites operacionais da fase.',
    c.excesso>0?'var(--jp-danger)':'var(--jp-success)');
  posture('gdPostureAlav',
    c.alavCar>c.tetoAlav?'Alavancagem Acima do Teto':'Alavancagem Segura',
    fmtX(c.alavCar)+' / '+fmtX(c.tetoAlav)+(c.alavCar>c.tetoAlav?' — acima do teto da fase.':' — abaixo do teto permitido.'),
    c.alavCar>c.tetoAlav?'var(--jp-danger)':'var(--jp-success)');
  posture('gdPostureGov',
    onb.complete?'Governança Completa':(onb.critical?`${onb.critical} pendência(s) crítica(s)`:(onb.warning?`${onb.warning} atenção`:`${onb.pending} pendente(s)`)),
    onb.complete?'Formulário de Início sem pendências.':'Formulário de Início incompleto — revise em Configurações.',
    onb.complete?'var(--jp-success)':(onb.critical?'var(--jp-danger)':'var(--jp-warning)'));
}

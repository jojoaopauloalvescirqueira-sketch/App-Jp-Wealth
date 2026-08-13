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
  // Ação primária como BOTÃO curto (o protótipo mostra "Resolver pendências"),
  // com a orientação completa preservada no title para leitor de tela e hover.
  // Os rótulos abaixo são rotulagem de UI derivada do texto de r.action que já
  // existia por estado — nenhuma regra nova, nenhum destino novo.
  const ACAO_CURTA={clear:'Executar dentro da fase', caution:'Revisar antes de operar',
                    pending:'Resolver pendências', reduce:'Reduzir exposição',
                    blocked:'Registrar na auditoria'};
  const btnAcao=$('mcClearanceAction');
  if(btnAcao){ btnAcao.textContent=ACAO_CURTA[r.status]||'Ver detalhes'; btnAcao.title=r.action; }
  // N2 — Mission Metrics (status executivos)
  const set=(id,txt)=>{ const e=$(id); if(e) e.textContent=txt; };
  const chip=(id,cls,txt)=>{ const e=$(id); if(e){ e.className='mc-status '+cls; e.textContent=txt; } };
  // ---- COCKPIT · quatro fatos (Fase 2C — textos fiéis ao protótipo) ----
  // ESPELHO DE LEITURA: toda fórmula é reuso da vigente. As metas passaram a
  // carregar o que o protótipo mostra e que o App tinha perdido:
  //   fase  -> "postura ofensiva" (PHASE_OBJECTIVE, que a faixa de Postura levava)
  //   DD    -> alarme E guilhotina (c.alarmScaled e c.mddScaled, já usados no veredito)
  //   risco -> margem restante (c.margemEstatutaria, já exibida no LIFO)
  const cockpitFact=(id,o)=>{
    const cell=$(id); if(!cell) return;
    const v=cell.querySelector('[data-fact-v]');
    // O protótipo pinta o NÚMERO com a cor do estado, não só a barra.
    if(v){ v.textContent=o.value; v.style.color=o.color||''; }
    const m=cell.querySelector('[data-fact-meta]'); if(m) m.textContent=o.meta;
    const f=cell.querySelector('[data-fact-fill]');
    if(f){
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
  const faseCell=$('mcFactFase');
  const segWrap=faseCell && faseCell.querySelector('[data-fact-seg-wrap]');
  if(segWrap) Array.prototype.forEach.call(segWrap.children,(seg,i)=>{
    seg.style.background = (i===c.fi) ? FCOLORS[c.fi] : '';
  });
  const faixa = c.mScaled ? fmtPct(c.mScaled[c.fi].ddmin)+'–'+fmtPct(c.mScaled[c.fi].ddmax) : '—';
  // Concordância com "postura" (feminino), como o protótipo escreve
  // ("postura ofensiva"). PHASE_OBJECTIVE guarda OFENSIVO/CAUTELA/DEFENSIVO/
  // SALVAGUARDA — só a grafia muda, o dado é o mesmo.
  const POSTURA_F={'OFENSIVO':'ofensiva','CAUTELA':'de cautela','DEFENSIVO':'defensiva','SALVAGUARDA':'de salvaguarda'};
  const postura = (typeof PHASE_OBJECTIVE!=='undefined' && PHASE_OBJECTIVE[c.fi]) ? (POSTURA_F[PHASE_OBJECTIVE[c.fi].t]||PHASE_OBJECTIVE[c.fi].t.toLowerCase()) : '';
  cockpitFact('mcFactFase',{
    value:c.fase.nome,
    meta:(postura?'postura '+postura+' · ':'')+'DD '+faixa+' · teto '+fmtX(c.tetoAlav),
    pct:null, markPct:null, color:FCOLORS[c.fi], over:false });
  const ddCeil=(c.mddScaled>0?c.mddScaled:0.15);
  const ddOver=c.mddScaled>0 && c.dd>=c.mddScaled;
  cockpitFact('mcFactDD',{
    value:fmtPct(c.dd),
    meta:(c.alarmScaled>0?'alarme em '+fmtPct(c.alarmScaled)+' · ':'')+'guilhotina '+fmtPct(ddCeil)+(ddOver?' · NO LIMITE':''),
    pct:(c.dd/ddCeil)*100,
    markPct:c.mScaled?(c.mScaled[c.fi].ddmax/ddCeil)*100:null,
    color:ddOver?'var(--f4)':FCOLORS[c.fi], over:ddOver });
  const temTeto=c.tetoRisco>0;
  const riscoPct=temTeto?(c.riscoTotal/c.tetoRisco)*100:0;
  const riscoOver=temTeto && c.riscoTotal>c.tetoRisco;
  cockpitFact('mcFactRisco',{
    value:fmtMoney(c.riscoTotal),
    meta:temTeto
      ? Math.round(riscoPct)+'% do teto '+fmtMoney(c.tetoRisco)+' · margem '+fmtMoney(c.margemEstatutaria)+(riscoOver?' · ACIMA DO TETO':'')
      : 'sem parâmetro de teto',
    pct:riscoPct, markPct:null,
    color:riscoOver?'var(--f3)':FCOLORS[c.fi], over:riscoOver });
  const alavOver=c.alavCar>c.tetoAlav;
  const alavPctTeto=c.tetoAlav>0?(c.alavCar/c.tetoAlav)*100:0;
  cockpitFact('mcFactAlav',{
    value:fmtX(c.alavCar),
    meta:(c.tetoAlav>0?Math.round(alavPctTeto)+'% do teto '+fmtX(c.tetoAlav):'sem teto definido')+(alavOver?' · ACIMA DO TETO':''),
    pct:(c.alavCar/4)*100, markPct:(c.tetoAlav/4)*100,
    color:alavOver?'var(--f2)':FCOLORS[c.fi], over:alavOver });
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
  // JPW-789ABC-B2, Fase 2B: a faixa de Postura saiu. Ela traduzia números em
  // rótulos binários ("Risco Controlado", "Alavancagem Segura"); quem faz isso
  // agora é a lista de motivos (#mcClearanceReasons, logo abaixo do subtítulo do
  // cockpit) — que nomeia o fato, QUANTIFICA e aponta o remédio ("podar $120 via
  // LIFO") — somada às quatro células, que mostram a margem contra cada teto.
  // PHASE_OBJECTIVE segue vivo em renderObjective() -> #objectiveCard, no
  // Execution Board; só o consumo pela postura do Dashboard deixou de existir.
}

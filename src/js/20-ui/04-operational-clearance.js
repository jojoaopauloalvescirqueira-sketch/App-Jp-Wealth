// ============ OPERATIONAL CLEARANCE — veredito executivo (N1) ============
// "Posso operar agora?" — derivado exclusivamente de compute() + estado salvo (S.onboarding).
// Severidade: clear < caution < pending < reduce < blocked.
function getOperationalClearance(c){
  c=c||compute();
  const model=c.forex, known=value=>typeof value==='number'&&Number.isFinite(value);
  const reasons=[];
  if(model.accountPhase.compulsoryClose)reasons.push('DD '+fmtPct(c.dd)+' atingiu '+fmtPct(c.mddScaled)+' — encerramento compulsório precede as fases.');
  if(quarantineActive())reasons.push('Quarentena registrada. P-24 pendente: não presumir duração ou liberação por data antiga.');
  if(c.semStop>0)reasons.push(c.semStop+' ordem(ns) sem stop validado — risco não calculável. O fato pode ser corrigido sem ocultar seu registro.');
  if(known(c.alavCar)&&known(c.tetoAlav)&&c.alavCar>c.tetoAlav)reasons.push('Alavancagem '+fmtX(c.alavCar)+' acima do teto '+fmtX(c.tetoAlav)+' da fase da conta.');
  reasons.push(model.executionEligibility.reason);
  for(const item of model.findings||[])if(item.message&&!reasons.includes(item.message))reasons.push(item.message);
  const ob=S.onboarding||{};
  if(!ob.done)reasons.push('Formulário de Início de Período pendente. Preenchimento é cadastro, não autorização normativa.');
  if(ob.done&&ob.centralCashStatus==='Não.')reasons.push('Caixa Central declarado ausente — rastreabilidade patrimonial pendente.');
  if(ob.done&&ob.centralCashStatus==='Em implantação.')reasons.push('Caixa Central declarado em implantação.');
  if(noExternalProtectionActive())reasons.push('Proteção externa declarada desativada — mantenha os alertas e o controle manual existentes.');
  return {status:'blocked',title:'Execução normativa bloqueada',
    subtitle:model.canRecord?'Registro e correção de fatos disponíveis; conformidade V11 não demonstrada.':'Registro indisponível para agregado incompatível; preserve a base.',
    reasons,action:'Examinar as pendências no Motor Forex. Questionários e registros não homologam parâmetros nem autorizam exposição.',canRecord:model.canRecord};
}
function renderOperationalClearance(c){
  const card=$('mcClearanceCard'); if(!card) return;
  const r=getOperationalClearance(c);
  const ob=S.onboarding||{}, model=c.forex, metrics=model.metrics;
  const known=value=>typeof value==='number'&&Number.isFinite(value);
  const money=value=>known(value)?fmtForexMoney(value,c.forex.account,0):'Não calculável';
  const percent=value=>known(value)?fmtPct(value):'Não calculável';
  const multiple=value=>known(value)?fmtX(value):'Não calculável';
  const phaseColor=FCOLORS[c.fi]||'var(--ink-dim)';
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
                    blocked:'Examinar pendências'};
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
      f.style.visibility=o.pct==null?'hidden':'';
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
  if(segWrap){
    const count=JPWForex.policy.phases.length;
    while(segWrap.children.length<count)segWrap.appendChild(document.createElement('i'));
    while(segWrap.children.length>count)segWrap.lastElementChild.remove();
    Array.prototype.forEach.call(segWrap.children,(seg,i)=>{seg.style.background=i===c.fi?phaseColor:'';});
  }
  const row=Number.isInteger(c.fi)&&c.mScaled?c.mScaled[c.fi]:null;
  const faixa=row?percent(row.ddmin)+'–'+percent(row.ddmax):'não calculável';
  const grid=model.activeGridPhase;
  cockpitFact('mcFactFase',{
    value:c.fase.nome,
    meta:'DD '+faixa+' · teto '+multiple(c.tetoAlav)+(grid.status==='OK'?' · grade F'+grid.value:' · grade não identificada'),
    pct:null,markPct:null,color:phaseColor,over:false});
  const ddOver=model.accountPhase.compulsoryClose===true;
  cockpitFact('mcFactDD',{
    value:percent(c.dd),meta:'limite '+percent(c.mddScaled)+(ddOver?' · ENCERRAMENTO COMPULSÓRIO':''),
    pct:known(c.dd)&&c.mddScaled>0?c.dd/c.mddScaled*100:null,
    markPct:row&&c.mddScaled>0?row.ddmax/c.mddScaled*100:null,
    color:ddOver?'var(--danger)':phaseColor,over:ddOver});
  cockpitFact('mcFactRisco',{
    value:money(c.riscoTotal),meta:'Aberto + pendentes ampliadoras · TRA P-17 pendente',
    pct:null,markPct:null,color:known(c.riscoTotal)?phaseColor:'var(--ink-dim)',over:false});
  const alavOver=known(c.alavCar)&&known(c.tetoAlav)&&c.alavCar>c.tetoAlav;
  cockpitFact('mcFactAlav',{
    value:multiple(c.alavCar),meta:'Notional bruto / min(SI, equity) · teto '+multiple(c.tetoAlav)+(alavOver?' · ACIMA DO TETO':''),
    pct:known(c.alavCar)?c.alavCar/4*100:null,markPct:known(c.tetoAlav)?c.tetoAlav/4*100:null,
    color:alavOver?'var(--danger)':phaseColor,over:alavOver});
  // Observed reserve amounts and recorded verification, never questionnaire clearance.
  const fcr=metrics.fcrStatus,feo=metrics.feoStatus;
  const fcrAmount=fcr.value&&known(fcr.value.constituted)?money(fcr.value.constituted):'não apurado';
  const feoAmount=feo.value&&known(feo.value.constituted)?money(feo.value.constituted):'não apurado';
  set('mcMiniReservas','FCR '+fcrAmount+' · FEO '+feoAmount);
  if(fcr.status==='OK'&&feo.status==='OK')chip('mcMiniReservasChip','mc-st-muted','Verificação registrada');
  else chip('mcMiniReservasChip','mc-st-warn','Pendências');
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
    chip('mcMiniEPChip','mc-st-muted','Declarado');
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
    set('dStatus','Cadastro completo · execução BLOCKED');
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

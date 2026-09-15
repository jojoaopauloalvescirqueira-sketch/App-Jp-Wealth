// ============ RENDER ============
const FCOLORS=['var(--f1)','var(--f2)','var(--f2)','var(--f3)','var(--f3)','var(--f4)'];
function render(){
  const c=compute(), model=c.forex, metrics=model.metrics, policy=JPWForex.policy, p=S.params;
  const known=value=>typeof value==='number'&&Number.isFinite(value);
  const money=value=>known(value)?fmtForexMoney(value,c.forex.account,0):'Não calculável';
  const money2=value=>known(value)?fmtForexMoney(value,c.forex.account,2):'Não calculável';
  const percent=value=>known(value)?fmtPct(value):'Não calculável';
  const multiple=value=>known(value)?fmtX(value):'Não calculável';
  const decimal=(value,digits=2)=>known(value)?value.toLocaleString('pt-BR',{minimumFractionDigits:digits,maximumFractionDigits:digits}):'Não calculável';
  const phaseColor=model.accountPhase.compulsoryClose?'var(--danger)':FCOLORS[c.fi]||'var(--ink-dim)';
  // header pill
  renderHeaderReadout(c);
  $('hPhaseLbl').textContent=c.fase.nome;
  const hp=$('hPhase'); hp.className='pill'+(Number.isInteger(c.fi)?' f'+(c.fi+1):'');
  hp.querySelector('.dot').style.background=phaseColor;
  hp.querySelector('.dot').style.color=phaseColor;
  // Existing gauge geometry; scales and phase boundaries come from the V11
  // read-model/registry. Missing observations hide needles, never display zero.
  const ddCeil=c.mddScaled;
  const ddPct=known(c.dd)&&known(ddCeil)&&ddCeil>0?Math.min(100,(c.dd/ddCeil)*100):null;
  const alavPct=known(c.alavCar)?Math.min(100,(c.alavCar/4)*100):null;
  const RING=392.0, RING_GAP=3;
  const zoneDash=(fromPct,toPct)=>{
    const start=RING*fromPct/100+(fromPct>0?RING_GAP/2:0);
    const len=Math.max(0,RING*(toPct-fromPct)/100-(fromPct>0?RING_GAP/2:0)-(toPct<100?RING_GAP/2:0));
    return '0 '+start.toFixed(1)+' '+len.toFixed(1)+' 900';
  };
  // Varredura de entrada: na PRIMEIRA alimentação o anel é semeado em zero
  // (dasharray 0, ponto a 225°) e o valor real entra um tique depois — a
  // transição do CSS faz o percurso, como no canvas do design. setTimeout, não
  // requestAnimationFrame: rAF não dispara em aba/painel oculto (lição já
  // paga duas vezes nesta base). Renders seguintes aplicam direto e o CSS
  // anima só o delta.
  // `semi` seleciona a geometria da variante C (semicírculo 180°, do design):
  // arco fino r=80 → 2.5133/pct e ponteiro de -90° a +90° → 1.8°/pct. Sem a
  // flag vale o anel 1b de 270° (3.2044/pct, 225°+2.7°/pct).
  const feedRing=(id,{pct,zones,zi,value,zoneKey,ariaText,ceilingPct,scaleText,semi})=>{
    const g=$(id); if(!g) return;
    const existing=g.querySelectorAll('.jpwg-ring-zone');
    if(existing.length&&zones.length>existing.length){
      for(let i=existing.length;i<zones.length;i++){const extra=existing[0].cloneNode(false);extra.removeAttribute('id');existing[0].parentNode.appendChild(extra);}
    }
    g.querySelectorAll('.jpwg-ring-zone').forEach((el,i)=>{el.style.display=zones[i]?'':'none';if(zones[i]){el.setAttribute('stroke-dasharray',zoneDash(zones[i][0],zones[i][1]));el.setAttribute('stroke',FCOLORS[i]||'var(--ink-dim)');}});
    const fill=g.querySelector('[data-jpwg-arc]');
    const orbit=g.querySelector('[data-jpwg-needle]');
    const tip=g.querySelector('[data-jpwg-needle-tip]');
    [fill,orbit,tip].forEach(el=>{if(el)el.style.visibility=known(pct)?'':'hidden';});
    if(!known(pct)){
      const val=g.querySelector('[data-jpwg-value]');if(val)val.textContent=value;
      const label=g.querySelector('[data-jpwg-zonekey]');if(label)label.textContent=zoneKey;
      const ceiling=g.querySelector('[data-jpwg-ceiling]');if(ceiling)ceiling.style.visibility='hidden';
      g.removeAttribute('aria-valuenow');g.setAttribute('aria-valuetext',ariaText);return;
    }
    const dashFor=p=>((semi?2.5133:3.2044)*p).toFixed(1)+' 900';
    // Ângulo em NÚMERO: o ponteiro consome com sufixo "deg" (CSS transform), o
    // tick do teto consome cru (atributo SVG rotate). Uma fórmula só para os
    // dois — foi tê-las separadas que deixou o teto na geometria do anel
    // enquanto o resto já era semicírculo.
    const degNum=p=>(semi? -90+1.8*p : 225+2.7*p);
    const degFor=p=>degNum(p).toFixed(2)+'deg';
    const aplicar=()=>{
      if(fill){ fill.setAttribute('stroke',FCOLORS[zi]||'var(--ink-dim)'); fill.setAttribute('stroke-dasharray',dashFor(pct)); }
      if(orbit) orbit.style.transform='rotate('+degFor(pct)+')';
      if(tip) tip.setAttribute('fill',(FCOLORS[zi]||'var(--ink-dim)'));
    };
    // Varredura de entrada. Só faz sentido com o instrumento RENDERIZADO: num
    // card de tela inativa (display:none) não há estilo computado nem
    // transição, então a semente não é marcada e a varredura acontece no
    // primeiro render em que ele estiver visível.
    if(!g.dataset.jpwgSeeded && g.offsetHeight>0){
      g.dataset.jpwgSeeded='1';
      if(fill){ fill.setAttribute('stroke',(FCOLORS[zi]||'var(--ink-dim)')); fill.setAttribute('stroke-dasharray',dashFor(0)); }
      if(orbit) orbit.style.transform='rotate('+degFor(0)+')';
      if(tip) tip.setAttribute('fill',(FCOLORS[zi]||'var(--ink-dim)'));
      // LEITURA OBRIGATÓRIA antes de aplicar o alvo: força o recálculo de
      // estilo para que o navegador ENXERGUE o estado semeado. Sem ela as duas
      // escritas colapsam numa só e nenhuma transição é gerada — medido neste
      // projeto: 0 transições com setTimeout(60), 1 com esta leitura. Também
      // elimina a dependência de temporizador e de quadro (aba em segundo
      // plano não avança rAF nem repinta).
      if(fill) void getComputedStyle(fill).strokeDasharray;
      if(orbit) void getComputedStyle(orbit).transform;
      aplicar();
    } else aplicar();
    const ceil=g.querySelector('[data-jpwg-ceiling]');
    if(ceil)ceil.style.visibility=known(ceilingPct)?'':'hidden';
    if(ceil && ceilingPct!=null) ceil.setAttribute('transform','rotate('+degNum(Math.min(100,ceilingPct)).toFixed(2)+' 100 100)');
    const val=g.querySelector('[data-jpwg-value]'); if(val) val.textContent=value;
    const zk=g.querySelector('[data-jpwg-zonekey]'); if(zk && zoneKey){ zk.textContent=zoneKey; zk.style.color=FCOLORS[zi]||'var(--ink-dim)'; }
    // Rótulo de escala no miolo do anel (só onde existe: o DD do Dashboard, cuja
    // escala é o teto do perfil e portanto varia).
    const sc=g.querySelector('[data-jpwg-scale]'); if(sc && scaleText) sc.textContent=scaleText;
    // Classificação abaixo do gauge, no sub-card da faixa do Dashboard. Fica
    // FORA do elemento do gauge, então é procurada no sub-card que o contém.
    const card=g.closest('.jpwg-subcard');
    const sub=card && card.querySelector('[data-jpwg-subzone]');
    if(sub && zoneKey){ sub.textContent=zoneKey; sub.style.color=FCOLORS[zi]||'var(--ink-dim)'; }
    g.setAttribute('aria-valuenow',Math.round(pct));
    g.setAttribute('aria-valuetext',ariaText);
  };
  const zn=policy.phases.map(row=>'F'+row.id+' · '+row.name.toUpperCase());
  const alavBands=['0–1X','1–2X','2–3X','3–4X'];
  // Zonas do DD em % da escala: as quatro fases REAIS (faixas dinâmicas).
  const ddZones=policy.phases.map(row=>[Math.min(100,row.ddMinPercent/(ddCeil*100)*100),Math.min(100,row.ddMaxPercent/(ddCeil*100)*100)]);
  const alavZi=Math.max(0,Math.min(3,Math.floor(c.alavCar)));
  const alavAcima=known(c.alavCar)&&known(c.tetoAlav)&&c.alavCar>c.tetoAlav;
  feedRing('gaugeDD',{pct:ddPct, zones:ddZones, zi:model.accountPhase.compulsoryClose?5:c.fi,
    value:percent(c.dd), zoneKey:zn[c.fi]||c.fase.nome,
    ariaText:(zn[c.fi]||c.fase.nome)+' — DD '+percent(c.dd)+' de '+percent(ddCeil)});
  // Zonas da alavancagem: as quatro bandas fixas de 1x (espelho do gradiente
  // do termômetro antigo); a zona ativa é a banda onde a carga está.
  feedRing('gaugeAlav',{pct:alavPct, zones:[[0,25],[25,50],[50,75],[75,100]], zi:(alavAcima?3:alavZi),
    value:multiple(c.alavCar), zoneKey:!known(c.alavCar)?'NÃO CALCULÁVEL':(alavAcima?'ACIMA DO TETO':alavBands[alavZi]), ceilingPct:known(c.tetoAlav)?(c.tetoAlav/4)*100:null,
    ariaText:'Alavancagem '+multiple(c.alavCar)+' de 4x — teto da fase '+multiple(c.tetoAlav)});
  // Pílulas de classificação sob os gauges (fase vigente / relação com o teto)
  const pills=document.querySelectorAll('.thermo-card [data-jpwg-pill-text]');
  const dots=document.querySelectorAll('.thermo-card [data-jpwg-pill-dot]');
  if(pills.length>=2){
    pills[0].textContent=zn[c.fi]||c.fase.nome; pills[0].style.color=phaseColor;
    pills[1].textContent=!known(c.alavCar)||!known(c.tetoAlav)?'Comparação não calculável':alavAcima?'ACIMA DO TETO '+multiple(c.tetoAlav):'dentro do teto '+multiple(c.tetoAlav);
    pills[1].style.color=alavAcima?'var(--danger)':known(c.alavCar)?(FCOLORS[alavZi]||phaseColor):'var(--ink-dim)';
    if(dots.length>=2){ dots[0].style.background=phaseColor; dots[1].style.background=pills[1].style.color; }
  }
  const rangeEls=document.querySelectorAll('.thermo-card [data-jpwg-range]');
  if(rangeEls.length>=1)rangeEls[0].textContent=c.mScaled&&Number.isInteger(c.fi)?'DD · faixa da fase '+percent(c.mScaled[c.fi].ddmin)+'–'+percent(c.mScaled[c.fi].ddmax):'DD · faixa da fase não calculável';
  // Legenda de fases (mesma tabela dinâmica de antes, agora sob os gauges)
  const zoneEl=$('thermoZoneLabels');
  if(zoneEl){
    zoneEl.innerHTML=policy.phases.slice().reverse().map(row=>`<div class="tz" style="color:${FCOLORS[row.id-1]}">${esc(zn[row.id-1])} ${percent(row.ddMinPercent/100)}–${percent(row.ddMaxPercent/100)}</div>`).join('');
  }
  // JPW-789ABC-B2, Fase 2B: os gauges gdGaugeDD/gdGaugeAlav do Dashboard saíram
  // — a barra com marcador de teto dentro do cockpit É a representação agora.
  // ddPct/alavPct/ddZones seguem calculados acima porque alimentam gaugeDD e
  // gaugeAlav, que são do EXECUTION BOARD e não fazem parte deste bloco.
  // metrics
  $('mSaldo').textContent=fmtForexMoney(p.saldoAtu,null,0);
  $('mSaldoSub').textContent='Cadastro contábil legado · inicial '+fmtForexMoney(p.saldoIni,null,0)+' — não substitui equity observada'
    +(S.cycleRealizado?(' · ciclo arquivado LEGACY '+fmtForexMoney(S.cycleRealizado,null,2)):'');
  $('mDD').textContent=percent(c.dd);
  $('mDDsub').textContent=metrics.drawdown.status==='OK'?'SI e equity da conta observada · fluxos documentados neutralizados':'Registre SI, equity flutuante e ajuste de fluxos com fonte.';
  $('mTetoAlav').textContent=multiple(c.tetoAlav);
  $('mAlavCar').textContent=multiple(c.alavCar);
  $('mRisco').textContent=money(c.riscoTotal);
  $('mRiscoSub').textContent='Exposição aberta + pendentes ampliadoras · TRA P-17 pendente';
  // status — só exibe em exceção (o card de postura cobre o estado normal da fase)
  const sb=$('statusBanner'); sb.className='status-banner '+c.sbCls;
  sb.style.display=c.excecao?'flex':'none';
  $('statusIco').textContent=c.ico; $('statusTxt').textContent=c.status;
  // Read-only warning: duration P-24 is pending, never inferred from an old date.
  const qb=$('quarantineBanner'), qbtn=$('quarantineConfirmBtn');
  if(quarantineActive()){
    qb.style.display='flex';
    $('quarantineTxt').textContent='QUARENTENA REGISTRADA — duração mínima P-24 pendente. Uma data antiga não autoriza retorno; redução e registros permanecem acessíveis.';
    if(qbtn) qbtn.style.display='none';
  } else if(model.accountPhase.compulsoryClose){
    qb.style.display='flex';
    $('quarantineTxt').textContent=`DD ${percent(c.dd)} atingiu ${percent(c.mddScaled)}: encerramento compulsório precede as fases. Formalize o evento; P-24 não permite presumir prazo de retorno.`;
    if(qbtn) qbtn.style.display='inline-block';
  } else { qb.style.display='none'; if(qbtn) qbtn.style.display='none'; }
  // renderObjective saiu: seu alvo (#objectiveCard, na faixa de Postura do
  // Execution Board) foi removido na Fase 2C. PHASE_OBJECTIVE continua vivo —
  // agora alimenta a meta "postura ofensiva" da célula de Fase do cockpit.
  // FINALIZAR OPERAÇÃO: visível sempre que existir uma Operação Única para
  // encerrar — inclusive com posição aberta.
  //
  // Antes o botão SUMIA enquanto houvesse ordem aberta. Esconder a ação em vez
  // de explicar por que ela não pode ocorrer é UX ruim, e contraria o próprio
  // Art. 4.4: a Operação só se extingue quando a posição líquida volta a zero E
  // o Gestor confirma formalmente. O operador precisa ver que o ato existe, e
  // descobrir no clique o que falta para ele acontecer.
  //
  // O bloqueio passou a viver no preflight, que nomeia a ordem que impede a
  // finalização e não muta nada.
  if(typeof renderOperationCopyAction==='function')renderOperationCopyAction();
  const abtn=$('archiveOpBtn');
  if(abtn){
    const temOperacao = (typeof operationLiveOrders==='function')
      ? operationLiveOrders().length>0
      : S.phases.some(ph=>ph.orders.some(o=>o && (o.status==='Aberta'||o.status==='Fechada'||o.status==='Migrada')));
    abtn.style.display = temOperacao ? 'inline-block' : 'none';
  }
  const bn=$('breachNote');
  if(S.protocolBreaches>0){
    bn.style.display='block';
    bn.textContent=`⚠ ${S.protocolBreaches} rompimento(s) de protocolo registrado(s) neste ciclo — fechamentos com stop movido/ignorado sem justificativa.`;
  } else { bn.style.display='none'; }
  // Return follows engine H4 evidence; a questionnaire cannot release a phase.
  const dgBanner=$('downgradeBanner');
  if(model.accountPhase.transition==='HELD'){
    dgBanner.style.display='flex';
    $('downgradeTxt').textContent='Retorno ainda não confirmado: margem e fechamento H4 posterior exigidos. Posições podadas não são restauradas automaticamente.';
  } else { dgBanner.style.display='none'; }
  const dgButton=$('downgradeBtn');if(dgButton)dgButton.style.display='none';
  // Account and declared grid are independent observations, with account limits.
  const grid=model.activeGridPhase;
  $('dpConta').textContent=c.fase.nome;
  $('dpGrade').textContent=grid.status==='OK'?'FASE '+grid.value+' · grade declarada':'Grade não identificada';
  const dualEl=$('dualPhase'); const mmBanner=$('mismatchBanner');
  if(grid.status==='OK'&&grid.diverges){
    dualEl.classList.add('mismatch');
    mmBanner.style.display='flex';
    $('mismatchTxt').textContent=`Grade declarada na fase ${grid.value}; limites da fase ${grid.accountPhase} da conta. A divergência não libera reconstrução nem aumenta o teto.`;
  } else {
    dualEl.classList.remove('mismatch');
    mmBanner.style.display='none';
  }
  // gauges
  // Fase 2C: a Coerência de Alavancagem saiu também do Execution Board — as duas
  // barras já viraram as escalas dos fatos do cockpit, no Dashboard e aqui.
  // JPW-789ABC-B2, Fase 2B: a Coerência de Alavancagem saiu — suas duas barras
  // foram absorvidas pelas escalas dos fatos Risco e Alavancagem do cockpit,
  // com as MESMAS fórmulas (alavPctW/riscoPctW) e as mesmas regras de cor.
  // VRM
  const regimeLabel={NORMAL:'NORMAL',TRANSITION:'TRANSIÇÃO',HIGH:'ALTA VOL'}[c.regime]||'NÃO CALCULÁVEL';
  $('mVRM').textContent=decimal(c.vrm);
  $('mRegime').textContent=regimeLabel;
  const gdVv=$('gdVrmValue'); if(gdVv) gdVv.textContent=decimal(c.vrm);
  const gdVr=$('gdVrmRegime');
  const regimeColor=!known(c.vrm)?'var(--ink-dim)':c.regime==='NORMAL'?'var(--jp-success)':(c.regime==='TRANSITION'?'var(--jp-warning)':'var(--jp-danger)');
  if(gdVr){ gdVr.textContent=regimeLabel; gdVr.style.color=regimeColor; }
  const market=S.forex&&S.forex.market;
  const gdA55=$('gdVrmAtr55'); if(gdA55) gdA55.textContent=decimal(market&&market.atrShort,5);
  const gdA660=$('gdVrmAtr660'); if(gdA660) gdA660.textContent=decimal(market&&market.atrLong,5);
  // Existing visual scale, fed by the canonical VRM thresholds. This does not
  // infer a regime from missing observations or use legacy editable parameters.
  const vrmLimits=policy.get('P-12a').value;
  const vrmEscala=vrmLimits.highAbove*1.15;
  const gdVFill=$('gdVrmFill');
  if(gdVFill){
    const frac=known(c.vrm)?Math.max(0,Math.min(1,c.vrm/vrmEscala)):0;
    gdVFill.style.visibility=known(c.vrm)?'':'hidden';
    gdVFill.style.width=(frac*100).toFixed(2)+'%';
    gdVFill.style.background=regimeColor;
  }
  // Sem parâmetro de regime (vrmHV zerado) os marcadores somem em vez de
  // colapsarem em 0% — marcador em posição falsa é pior que marcador ausente.
  const gdVrmMarca=(id,valor)=>{
    const e=$(id); if(!e) return;
    if(!(vrmEscala>0)){ e.style.display='none'; return; }
    e.style.display='';
    e.style.left='calc('+Math.max(0,Math.min(100,(valor/vrmEscala)*100)).toFixed(2)+'% - 1px)';
  };
  gdVrmMarca('gdVrmMarkN', vrmLimits.normalBelow);
  gdVrmMarca('gdVrmMarkHV', vrmLimits.highAbove);
  const gdVLim=$('gdVrmLimits');
  if(gdVLim){
    gdVLim.textContent='NORMAL abaixo de '+decimal(vrmLimits.normalBelow)+' · TRANSIÇÃO até '+decimal(vrmLimits.highAbove)+' inclusive · acima, ALTA VOL';
  }
  // LIFO
  $('lLote').textContent=decimal(c.loteTotal);
  $('lRisco').textContent=money(c.riscoTotal);
  $('lLucroTec').textContent=money(c.lucroTecnico);
  const ln=$('lNetOp');
  ln.textContent=money2(c.netOp);
  ln.style.color=c.netOp>0?'var(--f1)':(c.netOp<0?'var(--danger)':'var(--ink)');
  const lla=$('lLucroArq');
  if(lla){ lla.textContent=money(c.lucroArquivado); lla.style.color=c.lucroArquivado>0?'var(--f1)':'var(--ink)'; }
  const lpa=$('lPerdaArq');
  if(lpa){ lpa.textContent=money(c.perdaCiclo); lpa.style.color=c.perdaCiclo>0?'var(--danger)':'var(--ink)'; }
  $('lTeto').textContent=money(c.tetoRisco);
  $('lExcesso').textContent=money(c.excesso);
  $('lExcesso').style.color=c.excesso>0?'var(--danger)':'var(--ink)';
  // Margem estatutária não recebe crédito de lucro; margem informativa mostra leitura patrimonial.
  const usada=c.riscoEstatutario;
  const capTotal=c.tetoRisco;
  const livre=c.margemInformativa;
  const lme=$('lMargemEst');
  if(lme){
    lme.textContent=money(c.margemEstatutaria);
    lme.style.color=!known(c.margemEstatutaria)?'var(--ink-dim)':c.margemEstatutaria>0?'var(--f2)':'var(--danger)';
  }
  const lm=$('lMargem');
  if(lm){
    lm.textContent=money(livre);
    const comparable=known(usada)&&known(capTotal)&&capTotal>0;
    const usoPct=comparable?(usada/capTotal)*100:0;
    $('lMargemPct').textContent=comparable?usoPct.toFixed(0)+'% usado · risco comprometido '+money(usada)+' de '+money(capTotal):'Capacidade efetiva não calculável · parâmetros de risco pendentes';
    const bar=$('lMargemBar');
    bar.style.width=Math.min(100,usoPct)+'%';
    bar.style.visibility=comparable?'':'hidden';
    bar.style.background=usoPct<60?'var(--f1)':(usoPct<85?'var(--f2)':'var(--f4)');
  }
  const ls=$('lifoSem'); ls.textContent=c.sem; ls.style.color=c.semCls;
  $('lifoSug').innerHTML=c.sug;
  // dashboard mirror — a faixa de métricas saiu na Fase 2B (os quatro fatos
  // vivem no cockpit). #dStatus permanece: é de outro card, não da faixa.
  $('dStatus').textContent=c.status.split('—')[0].trim();
  // (grade única: a fase ativa é rotulada explicitamente em renderPhases; sem badge dinâmico por índice)
  // Camadas de veredito (UX de decisão): Operational Clearance (dash) + Execution Clearance (exec).
  // Reusam o MESMO c de compute() — nenhum estado paralelo, só leitura.
  renderOperationalClearance(c);
  renderExecClearance(c);
  renderOnboardingIncompleteBanner();
  renderExecutionOnboardingWarning();
  // Status do Sistema — espelho de leitura de persistência/backup/frescor/
  // governança. O guard de typeof segue o idioma já usado no boot para
  // renderDgStorageCard: este arquivo é ordem 11 do manifest e o renderizador
  // vive em 40-app/12-global-dashboard.js (41), então no primeiro render
  // disparado por boot() a função ainda não existe. Aquele arquivo faz a
  // primeira pintura por conta própria assim que todos os scripts carregam.
  if(typeof renderSystemStatus==='function') renderSystemStatus();
  if(window.JPWDashMacro) window.JPWDashMacro.schedule();
  if(window.JPWForex&&JPWForex.ui)JPWForex.ui.render();
  if(document.getElementById('fxconsolidated')?.classList.contains('active')&&window.JPWFXConsolidated?.render)window.JPWFXConsolidated.render();
}

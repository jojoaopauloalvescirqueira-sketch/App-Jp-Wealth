// ============ RENDER ============
const FCOLORS=['var(--f1)','var(--f2)','var(--f3)','var(--f4)'];
function render(){
  const c=compute(), p=S.params;
  // header pill
  renderHeaderReadout(c);
  $('hPhaseLbl').textContent=c.fase.nome;
  const hp=$('hPhase'); hp.className='pill f'+(c.fi+1);
  hp.querySelector('.dot').style.background=FCOLORS[c.fi];
  hp.querySelector('.dot').style.color=FCOLORS[c.fi];
  // ---- JP WEALTH GAUGE — variante 1b "A, circular compacto" ----
  // Troca EXCLUSIVAMENTE a camada visual dos termômetros: os valores canônicos
  // continuam sendo c.dd/ddCeil (SET 11 — escala pelo teto real do perfil),
  // c.mScaled (fases dinâmicas), c.alavCar e c.tetoAlav (SET 6). Nenhum
  // cálculo novo. Geometria do anel de 270° (do design): zonas finas externas
  // r=84 (comprimento ≈392), preenchimento interno r=68 (3.2044/pct), ponto
  // orbital e teto girando 225°→495° (2.7°/pct a partir de 225°).
  const ddCeil=(c.mddScaled>0?c.mddScaled:0.15);
  const ddPct=Math.min(100,(c.dd/ddCeil)*100);
  const alavPct=Math.min(100,(c.alavCar/4)*100);
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
    g.querySelectorAll('.jpwg-ring-zone').forEach((el,i)=>{ if(zones[i]) el.setAttribute('stroke-dasharray',zoneDash(zones[i][0],zones[i][1])); });
    const fill=g.querySelector('[data-jpwg-arc]');
    const orbit=g.querySelector('[data-jpwg-needle]');
    const tip=g.querySelector('[data-jpwg-needle-tip]');
    const dashFor=p=>((semi?2.5133:3.2044)*p).toFixed(1)+' 900';
    // Ângulo em NÚMERO: o ponteiro consome com sufixo "deg" (CSS transform), o
    // tick do teto consome cru (atributo SVG rotate). Uma fórmula só para os
    // dois — foi tê-las separadas que deixou o teto na geometria do anel
    // enquanto o resto já era semicírculo.
    const degNum=p=>(semi? -90+1.8*p : 225+2.7*p);
    const degFor=p=>degNum(p).toFixed(2)+'deg';
    const aplicar=()=>{
      if(fill){ fill.setAttribute('stroke',FCOLORS[zi]); fill.setAttribute('stroke-dasharray',dashFor(pct)); }
      if(orbit) orbit.style.transform='rotate('+degFor(pct)+')';
      if(tip) tip.setAttribute('fill',FCOLORS[zi]);
    };
    // Varredura de entrada. Só faz sentido com o instrumento RENDERIZADO: num
    // card de tela inativa (display:none) não há estilo computado nem
    // transição, então a semente não é marcada e a varredura acontece no
    // primeiro render em que ele estiver visível.
    if(!g.dataset.jpwgSeeded && g.offsetHeight>0){
      g.dataset.jpwgSeeded='1';
      if(fill){ fill.setAttribute('stroke',FCOLORS[zi]); fill.setAttribute('stroke-dasharray',dashFor(0)); }
      if(orbit) orbit.style.transform='rotate('+degFor(0)+')';
      if(tip) tip.setAttribute('fill',FCOLORS[zi]);
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
    if(ceil && ceilingPct!=null) ceil.setAttribute('transform','rotate('+degNum(Math.min(100,ceilingPct)).toFixed(2)+' 100 100)');
    const val=g.querySelector('[data-jpwg-value]'); if(val) val.textContent=value;
    const zk=g.querySelector('[data-jpwg-zonekey]'); if(zk && zoneKey){ zk.textContent=zoneKey; zk.style.color=FCOLORS[zi]; }
    // Rótulo de escala no miolo do anel (só onde existe: o DD do Dashboard, cuja
    // escala é o teto do perfil e portanto varia).
    const sc=g.querySelector('[data-jpwg-scale]'); if(sc && scaleText) sc.textContent=scaleText;
    // Classificação abaixo do gauge, no sub-card da faixa do Dashboard. Fica
    // FORA do elemento do gauge, então é procurada no sub-card que o contém.
    const card=g.closest('.jpwg-subcard');
    const sub=card && card.querySelector('[data-jpwg-subzone]');
    if(sub && zoneKey){ sub.textContent=zoneKey; sub.style.color=FCOLORS[zi]; }
    g.setAttribute('aria-valuenow',Math.round(pct));
    g.setAttribute('aria-valuetext',ariaText);
  };
  const zn=['F1 · ATAQUE','F2 · DESACEL.','F3 · SOBREVIV.','F4 · ABISMO'];
  const alavBands=['0–1X','1–2X','2–3X','3–4X'];
  // Zonas do DD em % da escala: as quatro fases REAIS (faixas dinâmicas).
  const ddZones=c.mScaled?c.mScaled.map(m=>[Math.min(100,m.ddmin/ddCeil*100),Math.min(100,m.ddmax/ddCeil*100)]):[[0,25],[25,50],[50,75],[75,100]];
  const alavZi=Math.max(0,Math.min(3,Math.floor(c.alavCar)));
  const alavAcima=c.alavCar>c.tetoAlav;
  feedRing('gaugeDD',{pct:ddPct, zones:ddZones, zi:c.fi,
    value:fmtPct(c.dd), zoneKey:zn[c.fi],
    ariaText:zn[c.fi]+' — DD '+fmtPct(c.dd)+' de '+fmtPct(ddCeil)});
  // Zonas da alavancagem: as quatro bandas fixas de 1x (espelho do gradiente
  // do termômetro antigo); a zona ativa é a banda onde a carga está.
  feedRing('gaugeAlav',{pct:alavPct, zones:[[0,25],[25,50],[50,75],[75,100]], zi:(alavAcima?3:alavZi),
    value:fmtX(c.alavCar), zoneKey:(alavAcima?'ACIMA DO TETO':alavBands[alavZi]), ceilingPct:(c.tetoAlav/4)*100,
    ariaText:'Alavancagem '+fmtX(c.alavCar)+' de 4x — teto da fase '+fmtX(c.tetoAlav)});
  // Pílulas de classificação sob os gauges (fase vigente / relação com o teto)
  const pills=document.querySelectorAll('.thermo-card [data-jpwg-pill-text]');
  const dots=document.querySelectorAll('.thermo-card [data-jpwg-pill-dot]');
  if(pills.length>=2){
    pills[0].textContent=zn[c.fi]; pills[0].style.color=FCOLORS[c.fi];
    pills[1].textContent=c.alavCar>c.tetoAlav?'ACIMA DO TETO '+fmtX(c.tetoAlav):'dentro do teto '+fmtX(c.tetoAlav);
    pills[1].style.color=c.alavCar>c.tetoAlav?FCOLORS[3]:FCOLORS[alavZi];
    if(dots.length>=2){ dots[0].style.background=FCOLORS[c.fi]; dots[1].style.background=c.alavCar>c.tetoAlav?FCOLORS[3]:FCOLORS[alavZi]; }
  }
  const rangeEls=document.querySelectorAll('.thermo-card [data-jpwg-range]');
  if(rangeEls.length>=1 && c.mScaled) rangeEls[0].textContent='DD · faixa da fase '+fmtPct(c.mScaled[c.fi].ddmin)+'–'+fmtPct(c.mScaled[c.fi].ddmax);
  // Legenda de fases (mesma tabela dinâmica de antes, agora sob os gauges)
  const zoneEl=$('thermoZoneLabels');
  if(zoneEl && c.mScaled){
    zoneEl.innerHTML=[3,2,1,0].map(i=>`<div class="tz f${i+1}">${zn[i]} ${fmtPct(c.mScaled[i].ddmin)}–${fmtPct(c.mScaled[i].ddmax)}</div>`).join('');
  }
  // JPW-789ABC-B2, Fase 2B: os gauges gdGaugeDD/gdGaugeAlav do Dashboard saíram
  // — a barra com marcador de teto dentro do cockpit É a representação agora.
  // ddPct/alavPct/ddZones seguem calculados acima porque alimentam gaugeDD e
  // gaugeAlav, que são do EXECUTION BOARD e não fazem parte deste bloco.
  // metrics
  $('mSaldo').textContent=fmtMoney(p.saldoAtu);
  $('mSaldoSub').textContent='inicial '+fmtMoney(p.saldoIni)+' — contábil, não move o termômetro'
    +(S.cycleRealizado?(' · ciclo arquivado '+fmtMoney2(S.cycleRealizado)):'');
  $('mDD').textContent=fmtPct(c.dd);
  let ddSub='risco aberto − resultado fechado da operação';
  if(c.perdaCiclo>0) ddSub='inclui perda realizada do ciclo: '+fmtMoney(c.perdaCiclo)+' (Art. 3.4§2)';
  else if((S.cycleRealizado||0)>0) ddSub+=' · DDC: lucro arquivado não amortece (Art. 4.3)';
  $('mDDsub').textContent=ddSub;
  $('mTetoAlav').textContent=fmtX(c.tetoAlav);
  $('mAlavCar').textContent=fmtX(c.alavCar);
  $('mRisco').textContent=fmtMoney(c.riscoTotal);
  $('mRiscoSub').textContent='teto fase '+fmtMoney(c.tetoRisco);
  // status — só exibe em exceção (o card de postura cobre o estado normal da fase)
  const sb=$('statusBanner'); sb.className='status-banner '+c.sbCls;
  sb.style.display=c.excecao?'flex':'none';
  $('statusIco').textContent=c.ico; $('statusTxt').textContent=c.status;
  // quarentena (Art. 3.10 §2) — dispara uma vez ao cruzar o MDD e persiste 90 dias,
  // mesmo que o DD caia depois (fechar posições não anula a quarentena)
  // Quarentena (SET 5a): NÃO auto-persiste mais durante o preenchimento — isso latchava a
  // partir de um stop digitado errado e não havia como limpar. Agora o aviso é AO VIVO
  // (some sozinho se o DD real cair) e a quarentena de 90d só é gravada por ação deliberada.
  const hoje=todayISO();
  const qb=$('quarantineBanner'), qbtn=$('quarantineConfirmBtn');
  if(quarantineActive()){
    const rest=Math.ceil((new Date(S.quarantine.fim+'T00:00:00')-new Date(hoje+'T00:00:00'))/86400000);
    qb.style.display='flex';
    $('quarantineTxt').textContent=`QUARENTENA OPERACIONAL (Art. 3.10) até ${S.quarantine.fim} — ${rest} dia(s). Grades travadas: apenas fechamento de posições. Limpe em Configurações se foi engano.`;
    if(qbtn) qbtn.style.display='none';
  } else if(c.dd>=c.mddScaled){
    qb.style.display='flex';
    $('quarantineTxt').textContent=`DD ${fmtPct(c.dd)} atingiu o limite ativo de ${fmtPct(c.mddScaled)} (Art. 3.10). Se for real, formalize a quarentena. Se foi erro de preenchimento (stop errado), corrija — este aviso some sozinho, nada fica travado.`;
    if(qbtn) qbtn.style.display='inline-block';
  } else { qb.style.display='none'; if(qbtn) qbtn.style.display='none'; }
  // renderObjective saiu: seu alvo (#objectiveCard, na faixa de Postura do
  // Execution Board) foi removido na Fase 2C. PHASE_OBJECTIVE continua vivo —
  // agora alimenta a meta "postura ofensiva" da célula de Fase do cockpit.
  // arquivar operação: visível quando não há posição aberta e existe resultado fechado a consolidar
  const abtn=$('archiveOpBtn');
  if(abtn){
    const temAberta=S.phases.some(ph=>ph.orders.some(o=>o.status==='Aberta'));
    const temFechada=S.phases.some(ph=>ph.orders.some(o=>o.status==='Fechada'));
    abtn.style.display=(!temAberta&&temFechada)?'inline-block':'none';
  }
  const bn=$('breachNote');
  if(S.protocolBreaches>0){
    bn.style.display='block';
    bn.textContent=`⚠ ${S.protocolBreaches} rompimento(s) de protocolo registrado(s) neste ciclo — fechamentos com stop movido/ignorado sem justificativa.`;
  } else { bn.style.display='none'; }
  // sugestão de downgrade (recomendação, não bloqueio)
  const dgBanner=$('downgradeBanner');
  const dg=checkDowngrade(c.fi);
  if(dg){
    dgBanner.style.display='flex';
    $('downgradeTxt').textContent=`Drawdown melhorou — caiu abaixo do mínimo da FASE ${dg.fromIdx+1}, hoje sem ordens ativas ali. Reconheça a melhora antes de tratá-la como Fase ${dg.toIdx+1} normal.`;
    $('downgradeBtn').onclick=()=>openDowngradeModal(dg.fromIdx,dg.toIdx);
  } else { dgBanner.style.display='none'; }
  // indicador duplo: Fase da Conta (matemática) vs Grade Ativa (governada pelo questionário)
  const maxUnlocked=getMaxUnlockedIdx();
  $('dpConta').textContent=c.fase.nome;
  $('dpGrade').textContent=S.matrix[maxUnlocked].nome;
  const dualEl=$('dualPhase'); const mmBanner=$('mismatchBanner');
  if(maxUnlocked>c.fi){
    dualEl.classList.add('mismatch');
    if(!dg){
      // divergem, e não é só falta de questionário — tem posição viva prendendo a grade
      const ordensVivas=[];
      for(let i=c.fi+1;i<=maxUnlocked;i++){
        S.phases[i].orders.forEach(o=>{
          if(o.status==='Aberta') ordensVivas.push(`${o.id||'(sem ID)'} (${fmtMoney(orderRisk(o))})`);
        });
      }
      mmBanner.style.display='flex';
      $('mismatchTxt').textContent=`A grade da ${S.matrix[maxUnlocked].nome} segue ativa porque ainda há posição aberta lá: ${ordensVivas.join(', ')||'ordem não identificada'}. Feche ou migre essa posição para liberar o downgrade.`;
    } else { mmBanner.style.display='none'; } // dg cuida do aviso nesse caso (fase vazia, só falta o questionário)
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
  $('mVRM').textContent=c.vrm.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
  $('mRegime').textContent=c.regime;
  const gdVv=$('gdVrmValue'); if(gdVv) gdVv.textContent=c.vrm.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
  const gdVr=$('gdVrmRegime');
  const regimeColor=c.regime==='NORMAL'?'var(--jp-success)':(c.regime==='TRANSIÇÃO'?'var(--jp-warning)':'var(--jp-danger)');
  if(gdVr){ gdVr.textContent=c.regime; gdVr.style.color=regimeColor; }
  const gdA55=$('gdVrmAtr55'); if(gdA55) gdA55.textContent=(S.atr55||0).toLocaleString('pt-BR',{minimumFractionDigits:5,maximumFractionDigits:5});
  const gdA660=$('gdVrmAtr660'); if(gdA660) gdA660.textContent=(S.atr660||0).toLocaleString('pt-BR',{minimumFractionDigits:5,maximumFractionDigits:5});
  // VRM compacto (JPW-789ABC-B2, Fase 2A.5) — a barra substitui o dial e usa a
  // MESMA escala que ele já usava (p.vrmHV × 1,15), com os DOIS limites que
  // governam a classificação em 10-domain/02-risk-calculations.js:47:
  //   vrm > vrmHV → ALTA VOL · vrm > vrmN → TRANSIÇÃO · senão NORMAL
  // Nenhum limite novo, nenhuma escala nova, nenhum cálculo novo — só troca da
  // geometria de leitura. Reusa .mc-fact-track/-fill/-mark do cockpit.
  const vrmEscala = p.vrmHV>0 ? p.vrmHV*1.15 : 0;
  const gdVFill=$('gdVrmFill');
  if(gdVFill){
    const frac = vrmEscala>0 ? Math.max(0,Math.min(1, c.vrm/vrmEscala)) : 0;
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
  gdVrmMarca('gdVrmMarkN', p.vrmN);
  gdVrmMarca('gdVrmMarkHV', p.vrmHV);
  const gdVLim=$('gdVrmLimits');
  if(gdVLim){
    const n2=v=>(v||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
    gdVLim.textContent = vrmEscala>0
      ? 'NORMAL até '+n2(p.vrmN)+' · TRANSIÇÃO até '+n2(p.vrmHV)+' · acima, ALTA VOL'
      : 'sem parâmetro de regime';
  }
  // LIFO
  $('lLote').textContent=c.loteTotal.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
  $('lRisco').textContent=fmtMoney(c.riscoTotal);
  $('lLucroTec').textContent=fmtMoney(c.lucroTecnico);
  const ln=$('lNetOp');
  ln.textContent=fmtMoney2(c.netOp);
  ln.style.color=c.netOp>0?'var(--f1)':(c.netOp<0?'var(--danger)':'var(--ink)');
  const lla=$('lLucroArq');
  if(lla){ lla.textContent=fmtMoney(c.lucroArquivado); lla.style.color=c.lucroArquivado>0?'var(--f1)':'var(--ink)'; }
  const lpa=$('lPerdaArq');
  if(lpa){ lpa.textContent=fmtMoney(c.perdaCiclo); lpa.style.color=c.perdaCiclo>0?'var(--danger)':'var(--ink)'; }
  $('lTeto').textContent=fmtMoney(c.tetoRisco);
  $('lExcesso').textContent=fmtMoney(c.excesso);
  $('lExcesso').style.color=c.excesso>0?'var(--danger)':'var(--ink)';
  // Margem estatutária não recebe crédito de lucro; margem informativa mostra leitura patrimonial.
  const usada=c.riscoEstatutario;
  const capTotal=c.tetoRisco;
  const livre=c.margemInformativa;
  const lme=$('lMargemEst');
  if(lme){
    lme.textContent=fmtMoney(c.margemEstatutaria);
    lme.style.color=c.margemEstatutaria>0?'var(--f2)':'var(--danger)';
  }
  const lm=$('lMargem');
  if(lm){
    lm.textContent=fmtMoney(livre);
    const usoPct=capTotal>0?(usada/capTotal)*100:0;
    $('lMargemPct').textContent=usoPct.toFixed(0)+'% usado · risco estatutário '+fmtMoney(usada)+' de '+fmtMoney(capTotal);
    const bar=$('lMargemBar');
    bar.style.width=Math.min(100,usoPct)+'%';
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
}

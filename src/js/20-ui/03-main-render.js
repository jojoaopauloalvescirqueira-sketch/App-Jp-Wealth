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
  // Faixa de integração do Dashboard: variante C (semicírculo), como o design
  // usa nesta faixa — mais rasa que o anel, para linha densa de KPI. Mesma
  // função, mesmos valores; só a geometria muda (semi:true).
  feedRing('gdGaugeDD',{semi:true, pct:ddPct, zones:ddZones, zi:c.fi, value:fmtPct(c.dd),
    zoneKey:zn[c.fi], scaleText:'DE '+fmtPct(ddCeil),
    ariaText:zn[c.fi]+' — DD '+fmtPct(c.dd)+' de '+fmtPct(ddCeil)});
  feedRing('gdGaugeAlav',{semi:true, pct:alavPct, zones:[[0,25],[25,50],[50,75],[75,100]], zi:(alavAcima?3:alavZi), value:fmtX(c.alavCar),
    zoneKey:(alavAcima?'ACIMA DO TETO '+fmtX(c.tetoAlav):'dentro do teto '+fmtX(c.tetoAlav)), ceilingPct:(c.tetoAlav/4)*100,
    ariaText:'Alavancagem '+fmtX(c.alavCar)+' de 4x — teto da fase '+fmtX(c.tetoAlav)});
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
  renderObjective(c.fi);
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
  const alavPctW=Math.min(100,(c.alavCar/c.tetoAlav)*100);
  $('gAlavVal').textContent=fmtX(c.alavCar)+' / '+fmtX(c.tetoAlav);
  const gAlavBar=$('gAlavBar'); gAlavBar.style.width=alavPctW+'%';
  gAlavBar.style.background = c.alavCar>c.tetoAlav?'var(--f2)':FCOLORS[c.fi];
  const riscoPctW=c.tetoRisco>0?Math.min(100,(c.riscoTotal/c.tetoRisco)*100):0;
  $('gRiscoVal').textContent=fmtMoney(c.riscoTotal)+' / '+fmtMoney(c.tetoRisco);
  const gRiscoBar=$('gRiscoBar'); gRiscoBar.style.width=riscoPctW+'%';
  gRiscoBar.style.background = c.riscoTotal>c.tetoRisco?'var(--f3)':FCOLORS[c.fi];
  const gdCAv=$('gdCoherenceAlavVal'); if(gdCAv) gdCAv.textContent=fmtX(c.alavCar)+' / '+fmtX(c.tetoAlav);
  const gdCAb=$('gdCoherenceAlavBar');
  if(gdCAb){ gdCAb.style.width=alavPctW+'%'; gdCAb.style.background=c.alavCar>c.tetoAlav?'var(--f2)':FCOLORS[c.fi]; }
  const gdCRv=$('gdCoherenceRiscoVal'); if(gdCRv) gdCRv.textContent=fmtMoney(c.riscoTotal)+' / '+fmtMoney(c.tetoRisco);
  const gdCRb=$('gdCoherenceRiscoBar');
  if(gdCRb){ gdCRb.style.width=riscoPctW+'%'; gdCRb.style.background=c.riscoTotal>c.tetoRisco?'var(--f3)':FCOLORS[c.fi]; }
  // VRM
  $('mVRM').textContent=c.vrm.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
  $('mRegime').textContent=c.regime;
  const gdVv=$('gdVrmValue'); if(gdVv) gdVv.textContent=c.vrm.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
  const gdVr=$('gdVrmRegime');
  const regimeColor=c.regime==='NORMAL'?'var(--jp-success)':(c.regime==='TRANSIÇÃO'?'var(--jp-warning)':'var(--jp-danger)');
  if(gdVr){ gdVr.textContent=c.regime; gdVr.style.color=regimeColor; }
  const gdA55=$('gdVrmAtr55'); if(gdA55) gdA55.textContent=(S.atr55||0).toLocaleString('pt-BR',{minimumFractionDigits:5,maximumFractionDigits:5});
  const gdA660=$('gdVrmAtr660'); if(gdA660) gdA660.textContent=(S.atr660||0).toLocaleString('pt-BR',{minimumFractionDigits:5,maximumFractionDigits:5});
  const gdVDial=$('gdVrmDial');
  if(gdVDial){
    const frac=Math.max(0,Math.min(1, p.vrmHV>0 ? c.vrm/(p.vrmHV*1.15) : 0));
    gdVDial.style.background='conic-gradient(from 270deg at 50% 100%, '+regimeColor+' 0turn, '+regimeColor+' '+(frac*0.5).toFixed(4)+'turn, var(--jp-border) '+(frac*0.5).toFixed(4)+'turn, var(--jp-border) .5turn)';
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
  // dashboard mirror
  $('dFase').textContent=c.fase.nome;
  $('dDD').textContent=fmtPct(c.dd);
  $('dAlav').textContent=fmtX(c.tetoAlav);
  $('dStatus').textContent=c.status.split('—')[0].trim();
  // (grade única: a fase ativa é rotulada explicitamente em renderPhases; sem badge dinâmico por índice)
  // Camadas de veredito (UX de decisão): Operational Clearance (dash) + Execution Clearance (exec).
  // Reusam o MESMO c de compute() — nenhum estado paralelo, só leitura.
  renderOperationalClearance(c);
  renderExecClearance(c);
  renderOnboardingIncompleteBanner();
  renderExecutionOnboardingWarning();
}

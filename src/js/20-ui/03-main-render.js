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
  // thermometer DD — escala pelo teto real do perfil ativo (SET 11), não mais fixo em 15%
  const ddCeil=(c.mddScaled>0?c.mddScaled:0.15);
  const ddPct=Math.min(100,(c.dd/ddCeil)*100);
  $('thermoFill').style.height=ddPct+'%';
  $('thermoMarker').style.bottom=ddPct+'%';
  // Espelho de leitura no Dashboard (fidelidade ao Claude Design) — mesma
  // fonte canônica (c.dd/ddCeil) já usada acima; sem cálculo novo, sem input.
  const gdTDf=$('gdThermoDDFill'); if(gdTDf) gdTDf.style.height=ddPct+'%';
  const ticksEl=$('thermoDDticks');
  if(ticksEl){
    ticksEl.innerHTML=[1,0.8,0.6,0.4,0.2,0].map(f=>`<span>${fmtPct(ddCeil*f)}</span>`).join('');
  }
  const zoneEl=$('thermoZoneLabels');
  if(zoneEl && c.mScaled){
    const zn=['F1 · ATAQUE','F2 · DESACEL.','F3 · SOBREVIV.','F4 · ABISMO'];
    zoneEl.innerHTML=[3,2,1,0].map(i=>`<div class="tz f${i+1}">${zn[i]} ${fmtPct(c.mScaled[i].ddmin)}–${fmtPct(c.mScaled[i].ddmax)}</div>`).join('');
  }
  const tdv=$('thermoDDval'); if(tdv) tdv.textContent=fmtPct(c.dd);
  const gdTDv=$('gdThermoDDVal'); if(gdTDv) gdTDv.textContent=fmtPct(c.dd);
  // thermometer ALAVANCAGEM real utilizada (SET 6) — escala 0–4x; marca = teto da fase
  const lf=$('thermoLevFill');
  if(lf){
    lf.style.height=Math.min(100,(c.alavCar/4)*100)+'%';
    $('thermoLevMarker').style.bottom=Math.min(100,(c.tetoAlav/4)*100)+'%';
    $('thermoLevVal').textContent=fmtX(c.alavCar);
    lf.style.opacity=c.alavCar>c.tetoAlav?'1':'.92';
  }
  const gdTAf=$('gdThermoAlavFill');
  if(gdTAf){
    gdTAf.style.height=Math.min(100,(c.alavCar/4)*100)+'%';
    gdTAf.style.opacity=c.alavCar>c.tetoAlav?'1':'.92';
  }
  const gdTAv=$('gdThermoAlavVal'); if(gdTAv) gdTAv.textContent=fmtX(c.alavCar);
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

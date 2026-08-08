// ============ SIMULAÇÃO PATRIMONIAL POR PERFIL (projeção estatística, NÃO promessa de retorno) ============
// Memória de cálculo formal:
//  · Perfil ATIVO vem de getActiveRiskProfile() (via acctModel()).                     [Regra 2]
//  · Saldo inicial e período configurado vêm do modelo contábil existente (acctModel). [Regras 1,3,7]
//  · Retorno esperado anual  μ = alvo do perfil (m.target).
//  · Volatilidade anual       σ = DDR-alvo do perfil (pr.ddrTarget) — HIPÓTESE DECLARADA:
//    o drawdown-alvo do perfil é usado como proxy de 1 desvio-padrão do resultado anual.
//  · Caminho médio:   E(t) = saldoIni · (1+μ)^t        (t = fração do ano; compõe a meta do perfil).
//  · Bandas ±1σ:      σ(t) = σ · √t  (escala raiz-do-tempo de passeio aleatório) → E(t)·(1±σ(t)).
//  · Drawdown esperado = DDR-alvo; Drawdown máximo = cenário mestre 15% (pr.scenarioDD15).
//  · NÃO calculamos probabilidade de ruína (exigiria hipótese de ruína formal — Regra 6).
// Núcleo parametrizável — aceita perfil+saldo explícitos (onboarding, antes de confirmar)
// ou herda do estado global via patrimonialSim() (Contabilidade, período já iniciado).
function patrimonialSimCore(pr, saldoIni){
  const mu=pr.anual;                            // μ anual (pelo perfil)
  const sigma=pr.ddrTarget||0;                  // σ anual ≈ DDR-alvo (hipótese declarada — sem histórico próprio ainda)
  const meses=12, rows=[];
  for(let i=0;i<=meses;i++){
    const t=i/meses;                            // fração do ano
    const mean=saldoIni*Math.pow(1+mu,t);
    const st=sigma*Math.sqrt(t);                // escala raiz-do-tempo
    rows.push({i, mean, pos:mean*(1+st), neg:mean*(1-st)});
  }
  const end=rows[rows.length-1];
  return {pr, saldoIni, mu, sigma, rows,
    esperado:end.mean, pos1:end.pos, neg1:end.neg,
    ddEsperado:pr.ddrTarget||0,
    ddMax:pr.scenarioDD15||pr.ddrTarget||0};
}
function patrimonialSim(){
  const m=acctModel();                          // perfil ATIVO + saldo inicial + meta do período (estado global)
  return {...patrimonialSimCore(m.pr, m.saldoIni||0), m};
}
// Constrói o HTML da simulação (tiles + fan chart ±1σ + linha de MDD hard-stop).
// Reutilizado pela Contabilidade (estado global) e pelo onboarding (perfil/saldo em preview,
// antes de confirmar — SET: "gráfico ao clicar em perfil, ainda no formulário de início").
function buildSimHTML(s){
  const pr=s.pr;
  const yMDD=s.saldoIni*(1-s.ddMax); // linha de hard-stop: saldo inicial menos o MDD real do perfil (Art. 3.7/6.1, escalado)
  // ---- fan chart: caminho médio + banda ±1σ ao longo de 12 meses + linha de MDD
  const W=720,H=230,L=CH.L,R=CH.R,T=CH.T,B=CH.B;
  const ys=[...s.rows.map(r=>r.pos),...s.rows.map(r=>r.neg),yMDD];
  let ymin=Math.min(...ys), ymax=Math.max(...ys);
  const pad=(ymax-ymin)*0.08||Math.max(1,ymax*0.02); ymin-=pad; ymax+=pad;
  const n=s.rows.length-1;
  const X=i=>L+(i/n)*(W-L-R), Y=v=>T+(1-(v-ymin)/((ymax-ymin)||1))*(H-T-B);
  const line=sel=>s.rows.map((r,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(sel(r)).toFixed(1)).join(' ');
  const bandTop=s.rows.map((r,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(r.pos).toFixed(1)).join(' ');
  const bandBot=s.rows.slice().reverse().map((r,i)=>'L'+X(n-i).toFixed(1)+' '+Y(r.neg).toFixed(1)).join(' ');
  const grid=CH.gridY(W,L,R,Y,CH.ticks(ymin,ymax,4),fmtMoney);
  let xlab='';
  for(let i=0;i<=n;i+=3){ xlab+=`<text x="${X(i).toFixed(1)}" y="${H-7}" text-anchor="middle" font-size="8.5" fill="var(--ink-faint)">M${i}</text>`; }
  const last=s.rows[n];
  const stats=CH.stats(L,T,[
    {mark:'□', label:'Cenário médio', value:fmtMoney(last.mean), color:'var(--violet)'},
    {mark:'↑', label:'+1σ',           value:fmtMoney(last.pos),  color:'var(--f1)'},
    {mark:'↓', label:'−1σ',           value:fmtMoney(last.neg),  color:'var(--f4)'},
    {mark:'–', label:'Piso MDD',      value:fmtMoney(yMDD),      color:'var(--danger)'},
  ]);
  const svg=`<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;font-family:var(--mono)">
    <rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}" fill="var(--bg)"/>
    ${grid}
    <path d="${bandTop} ${bandBot} Z" fill="var(--violet)" opacity=".16"/>
    <path d="${line(r=>r.pos)}" fill="none" stroke="var(--f1)" stroke-width="1" stroke-dasharray="4 3" opacity=".75"/>
    <path d="${line(r=>r.neg)}" fill="none" stroke="var(--f4)" stroke-width="1" stroke-dasharray="4 3" opacity=".75"/>
    <path d="${line(r=>r.mean)}" fill="none" stroke="var(--violet)" stroke-width="1.2"/>
    ${CH.limit(W,L,R,Y(yMDD),'MDD '+fmtPct(s.ddMax)+' · '+fmtMoney(yMDD),'var(--danger)')}
    ${xlab}
    ${CH.callout(W,R,Y(last.pos), fmtMoney(last.pos), 'var(--f1)')}
    ${CH.callout(W,R,Y(last.mean),fmtMoney(last.mean),'var(--violet)')}
    ${CH.callout(W,R,Y(last.neg), fmtMoney(last.neg), 'var(--f4)')}
    ${stats}
  </svg>`;
  const tiles=`<div class="metrics">
    <div class="metric"><div class="k">Patrimônio esperado</div><div class="v sm">${fmtMoney2(s.esperado)}</div><div class="sub">cenário médio · 12 meses</div></div>
    <div class="metric" style="border-color:var(--f1)"><div class="k">Cenário +1σ (otimista)</div><div class="v sm" style="color:var(--f1)">${fmtMoney2(s.pos1)}</div><div class="sub">banda positiva</div></div>
    <div class="metric" style="border-color:var(--f4)"><div class="k">Cenário −1σ (pessimista)</div><div class="v sm" style="color:var(--f4)">${fmtMoney2(s.neg1)}</div><div class="sub">banda negativa</div></div>
    <div class="metric"><div class="k">Drawdown esperado</div><div class="v sm">${fmtPct(s.ddEsperado)}</div><div class="sub">DDR-alvo do perfil</div></div>
    <div class="metric" style="border-color:var(--f4)"><div class="k">Drawdown máximo (hard stop)</div><div class="v sm" style="color:var(--f4)">${fmtPct(s.ddMax)}</div><div class="sub">${fmtMoney(yMDD)} · encerramento compulsório</div></div>
    <div class="metric accent"><div class="k">Perfil</div><div class="v sm">${esc(pr.name)} · ${Math.round(pr.pct*100)}%</div><div class="sub">μ ${(s.mu*100).toFixed(1).replace('.',',')}% · σ ${(s.sigma*100).toFixed(1).replace('.',',')}%</div></div>
  </div>`;
  return `${tiles}
    <div style="margin-top:14px">${svg}</div>
    <p class="expl" style="font-size:calc(11px * var(--fs-scale));color:var(--ink-faint);line-height:1.6;margin-top:10px">
      Projeção estatística educativa — <b style="color:var(--ink-dim)">não é promessa de retorno</b>. O caminho médio compõe a meta anual do perfil sobre o saldo inicial; as bandas ±1σ tratam o DDR-alvo como desvio-padrão anual, com escala raiz-do-tempo (σ·√t). A linha vermelha é o teto de drawdown real desse perfil (Art. 3.7/6.1) — atingi-la aciona encerramento compulsório e quarentena, independentemente da projeção. Não expressa probabilidade de ruína.
    </p>`;
}
function renderAcctSim(){
  const box=$('acctSimWrap'); if(!box) return;
  const s=patrimonialSim();
  if(!(s.saldoIni>0)){
    box.innerHTML='<p class="muted" style="font-size:calc(12px * var(--fs-scale))">Defina o saldo inicial do período para ver a simulação patrimonial.</p>';
    return;
  }
  // Correção 6/8: qualidade da amostra e estado de calibração do MEI-JP visíveis também aqui.
  let meiLine='';
  try{
    const cal=meiCalibration((S.period&&S.period.profile)||'base'), st=cal.stats;
    meiLine=`<p style="font-size:calc(11px * var(--fs-scale));color:var(--ink-dim);line-height:1.7;margin-top:10px;font-family:var(--mono)">MEI-JP: ${cal.enabled?`estágio ${meiStageLabel(cal.modelStage)} · σ final ${fmtPct(cal.sigmaUsed)} (CID ${fmtPct(cal.cid)} · peso hist ${fmtPct(cal.historicalWeight||0)})`:esc(cal.reason)} · ${st.observations} retorno(s) válido(s)${st.excludedReturns?` · ${st.excludedReturns} excluído(s)`:''} · qualidade da amostra: ${meiQuality(st.observations)} · fluxos externos: ${st.flowsPresent?'sim (ajustados)':'não'}. Estimativas sujeitas a revisão.</p>`;
  }catch(e){ meiLine=''; }
  box.innerHTML=buildSimHTML(s)+meiLine;
}
function bindAcct(){
  const b=(id,fn)=>{ const el=$(id); if(el) el.addEventListener('input',fn); };
  b('acStart',()=>{ S.params.inicio=$('acStart').value; save(); renderAcct(); renderParams(); render(); });
  b('acSaldoIni',()=>{ S.params.saldoIni=parseFloat($('acSaldoIni').value)||0; save(); renderAcct(); renderParams(); renderMotor(); renderPhases(); render(); });
  b('acDiasSem',()=>{ S.acct.diasSemana=parseFloat($('acDiasSem').value)||4.5; save(); renderAcct(); });
  b('acMesesAno',()=>{ S.acct.mesesAno=parseFloat($('acMesesAno').value)||10.5; save(); renderAcct(); });
  const toggle=$('acctPeriodToggle');
  if(toggle) toggle.addEventListener('click',()=>{ acctDetailOpen=!acctDetailOpen; renderAcct(); });
}

function bindContab(){
  $('ldAddBtn').addEventListener('click',()=>{
    const data=$('ldDate').value;
    const res=parseFloat($('ldResult').value);
    const stEl=$('ldStatus');
    if(!data){ stEl.textContent='✗ informe a data'; stEl.className='fx-status err'; return; }
    if(isNaN(res)){ stEl.textContent='✗ informe o resultado do dia (0 é válido)'; stEl.className='fx-status err'; return; }
    const led=ledgerSorted();
    const anterior=[...led].reverse().find(e=>e.data<data);
    const posteriores=led.filter(e=>e.data>data);
    if(posteriores.length && !confirm('Há '+posteriores.length+' fechamento(s) com data posterior a '+data+'. Os saldos deles NÃO serão recalculados automaticamente — a cadeia de saldo pode ficar inconsistente. Continuar mesmo assim?')) return;
    let saldo=parseFloat($('ldSaldo').value);
    if(isNaN(saldo)) saldo=(anterior?anterior.saldo:S.params.saldoIni)+res;
    const exist=S.ledger.find(e=>e.data===data);
    if(exist){
      if(!confirm('Já existe fechamento em '+data+'. Sobrescrever?')) return;
      exist.resultado=res; exist.saldo=saldo; exist.nota=$('ldNota').value.trim();
      if(typeof dgLogChange==='function') dgLogChange('ledger','updated',data,'Fechamento diário atualizado ('+data+')');
    } else {
      S.ledger.push({data, resultado:res, saldo, nota:$('ldNota').value.trim()});
      if(typeof dgLogChange==='function') dgLogChange('ledger','created',data,'Fechamento diário registrado ('+data+')');
    }
    syncSaldoAtuFromLedger();
    $('ldResult').value=''; $('ldSaldo').value=''; $('ldNota').value='';
    stEl.textContent='✓ fechamento registrado'; stEl.className='fx-status ok';
    setTimeout(()=>{ stEl.textContent=''; },2500);
    save(); renderLedger(); renderDash(); renderParams(); render();
  });
  $('exportAuditBtn').addEventListener('click',exportAudit);
  // arquivamento da operação (Art. 3.5§2) — consolida o resultado no ciclo e zera as grades
  $('archiveOpBtn').addEventListener('click',()=>{
    if(S.phases.some(ph=>ph.orders.some(o=>o.status==='Aberta'))){
      alert('Ainda há posição aberta — a operação só é considerada encerrada quando não houver posição vinculada à tese (Art. 3.5 §2).');
      return;
    }
    const net=netOpAtual();
    if(!confirm(`Arquivar a operação atual?\n\nResultado líquido a consolidar no ciclo: ${fmtMoney2(net)}\n\n· Perda realizada CONTINUA no drawdown do ciclo (Art. 3.4§2).\n· Lucro arquivado NÃO amplia limites de risco (Art. 4.3 — Ilusão do DDC).\n· As grades são zeradas e as Fases 2–4 retravadas.`)) return;
    S.cycleRealizado=(S.cycleRealizado||0)+net;
    S.transitionLog.push({fase:'operação arquivada', ts:new Date().toISOString(),
      resumo:{resultado:net, cicloAcumulado:S.cycleRealizado}});
    // auditoria resumida (JPW-HJFGDE §11); o transitionLog acima segue sendo o registro normativo
    if(typeof dgLogChange==='function') dgLogChange('operation','archived','','Operação arquivada e resultado consolidado no ciclo');
    const sizes=[5,4,3,2];
    S.phases.forEach((ph,pi)=>{ ph.orders=emptyOrders(sizes[pi]||3); });
    S.phaseUnlocked=[true,false,false,false];
    save(); render(); renderPhases(); renderLedger();
  });
}

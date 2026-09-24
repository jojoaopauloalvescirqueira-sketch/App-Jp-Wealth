// ============ STOP ESTATÍSTICO §9 — Múltiplo de ATR estratificado + Raiz-N por horizonte ============
// Tudo em PERCENTUAL (§9.2): ATR% = ATR55/preço × 100. Comparação AO VIVO: usa o preço
// atual do ativo da Gênese (cotações do Motor de Lote), não a entrada.
function genesisOrder(){
  const explicit=(S.phases||[]).flatMap(ph=>ph.orders||[]).filter(o=>o.role==='GENESIS'&&o.recordStatus!=='voided');
  // Several declared Gêneses are ambiguous; do not select a convenient one.
  if(explicit.length)return explicit.length===1?explicit[0]:null;
  if(S.phases?.length===4)return S.phases[0]?.orders?.[0]||null;
  return null;
}
function atrPctCalc(price){
  const atr=S.forex?.market?.atrShort;
  const result=JPWForex.engine.computeStopAtrMultiple({stopPercent:0,atr,currentPrice:price});
  return result.status==='OK'?result.atrPercent:null;
}
function atrStrat(m){
  const minimum=JPWForex.policy.get('P-20').value;
  if(!Number.isFinite(m))return null;
  return {t:m>=minimum?'MÍNIMO ATENDIDO':'ABAIXO DO MÍNIMO',d:'Diagnóstico técnico; não autoriza execução',c:m>=minimum?'var(--f1)':'var(--f3)'};
}
function riskIndicatorsHTML(){
  const gen=genesisOrder(),ins=gen?instFor(gen.par):null,price=ins?.preco;
  const atr=S.forex?.market?.atrShort;
  const stopPercent=price>0&&gen?.sl>0?Math.abs(price-gen.sl)/price*100:null;
  const multiple=JPWForex.engine.computeStopAtrMultiple({stopPercent,atr,currentPrice:price});
  const minimum=JPWForex.engine.computeMinimumStop({atr});
  const number=r=>r.status==='OK'?String(+r.value.toFixed(4)):r.status;
  const strat=atrStrat(multiple.value);
  return `<div class="card" style="margin-bottom:14px"><h2>Stop Loss · diagnóstico V11${gen&&!gen.role?' · referência posicional LEGACY':''}</h2><div class="risk-primary-indicators"><div class="metric"><div class="k">Distância do stop / ATR</div><div class="v sm">${esc(number(multiple))}</div><div class="sub">${strat?esc(strat.t):'Informe ATR H4 e preço com origem registrada.'}</div></div><div class="metric"><div class="k">Distância mínima em preço</div><div class="v sm">${esc(number(minimum))}</div><div class="sub">Parâmetros P-16 / P-20. Análise técnica continua necessária.</div></div></div><details class="jp-p3"><summary>Raiz-N e validação</summary><p>Fator F: ${esc(JPWForex.policy.get('P-21').status)}. Horizonte N: ${esc(JPWForex.policy.get('P-22').status)}. Não há fallback numérico ou veto por esse diagnóstico.</p></details></div>`;
}
// Classe CSS da fase: whitelist semântica, não escaping. Atributo `class` não deve
// aceitar valor arbitrário nem escapado — só os identificadores do catálogo oficial.
function phaseCssClass(ph){
  const permitido=DEFAULTS.phases.map(p=>p.cls);
  return (ph && permitido.includes(ph.cls)) ? ph.cls : '';
}
function renderPhases(){
  if(globalThis.JPWForex?.executionBoardUI){JPWForex.executionBoardUI.renderPhases();return;}
  const cont=$('phaseContainer'); if(!cont)return;
  const model=JPWForex.state.read(), findings=orderComplianceFindings();
  const recordable=model.canRecord===true;
  let html=riskIndicatorsHTML();
  html+=`<div class="risk-note" role="status">${recordable?'Registro de fatos disponível.':'Registro indisponível: versão de dados incompatível.'} Elegibilidade de execução: <b>${esc(model.executionEligibility?.status||'NOT_COMPUTABLE')}</b>. ${findings.map(f=>esc(f.message||f.code)).join(' · ')}</div>`;
  if(S.phases.length===4)html+='<div class="risk-note">LEGACY — quatro grades preservadas em suas posições originais; os fatos serão avaliados pelo motor atual sem atribuir uma norma passada.</div>';
  (S.phases||[]).forEach((p,pi)=>{
    const legacy=S.phases.length===4||p.policyVersion==='LEGACY_UNRESOLVED';
    html+=`<div class="phase ${phaseCssClass(p)}" data-phase="${pi}" style="margin-top:10px"><div class="phase-head" style="cursor:default"><span class="badge">${legacy?'LEGACY · ':''}${esc(p.faseNome||('Grade '+(pi+1)))}</span><span>${esc(p.title||'')}</span><span class="here" style="margin-left:auto">${recordable?'REGISTRO DISPONÍVEL':'SOMENTE LEITURA'}</span></div><div class="phase-body">${phaseBodyHTML(pi,false)}</div></div>`;
  });
  cont.innerHTML=html;
  cont.querySelectorAll('[data-addorder]').forEach(btn=>btn.addEventListener('click',()=>{
    const pi=+btn.dataset.addorder;
    if(!operationRecordFeedback(operationAddDraft(pi)))return;
    renderPhases(); document.querySelector(`.phase[data-phase="${pi}"] tbody tr:last-child input[data-f="id"]`)?.focus();
  }));
  cont.querySelectorAll('[data-delorder]').forEach(btn=>btn.addEventListener('click',()=>{
    const [pi,oi]=btn.dataset.delorder.split(':').map(Number),o=S.phases[pi].orders[oi];
    let reason='Excluir rascunho';
    if(operationOrderIsLive(o)){
      reason=prompt('Anular preserva a ordem, suas versões e o motivo no histórico. Informe o motivo da anulação:');
      if(!reason?.trim())return;
    }else if((o.id||o.par||o.lote)&&!confirm('Excluir este rascunho?'))return;
    if(operationRecordFeedback(operationVoidOrder(pi,oi,reason))){render();renderPhases();}
  }));
  cont.querySelectorAll('[data-orderhistory]').forEach(btn=>btn.addEventListener('click',()=>{
    const [pi,oi]=btn.dataset.orderhistory.split(':').map(Number),o=S.phases[pi].orders[oi];
    $('modalOverlay').classList.add('show');
    $('modalBox').innerHTML='<h3>Versões da ordem '+esc(o.id||o.orderId)+'</h3><p>'+esc(o.orderId)+'</p>'+(o.revisions||[]).map(r=>'<details class="modal-q"><summary>Versão '+r.version+' · '+esc(r.recordedAt)+' · '+esc(r.reason)+'</summary><div class="modal-sub">Contexto '+esc(r.context?.policyVersion||'LEGACY_UNRESOLVED')+'</div><pre style="white-space:pre-wrap">'+esc(JSON.stringify({antes:r.before,depois:r.after},null,2))+'</pre></details>').join('')+'<button class="modal-btn cancel" id="modalCancel">Fechar</button>';
    $('modalCancel').addEventListener('click',closeModal);$('modalCancel').focus();
  }));
  // Typing is a DOM-only draft. Blur/change is the explicit recording act.
  cont.querySelectorAll('input[data-f],select[data-f]').forEach(field=>field.addEventListener('change',()=>{
    const pi=+field.dataset.p,oi=+field.dataset.o,f=field.dataset.f,o=S.phases[pi].orders[oi];
    if(f==='status'&&field.value==='Fechada'){field.value=o.status||'';openCloseOrderModal(pi,oi);return;}
    let value=field.type==='checkbox'?field.checked:field.value;
    if(['lote','entry','sl','tp','result','costs'].includes(f)){
      value=String(value).trim()===''?null:orderParseResult(value);
      if(value!==null&&!Number.isFinite(value)){alert('Informe um número válido.');return;}
    }
    if(value===o[f])return;
    let reason='Registro confirmado de '+f;
    if(operationOrderIsLive(o)){
      reason=prompt('Correção de fato registrado: informe o motivo. A versão anterior será preservada.');
      if(!reason?.trim())return;
    }
    const outcome=operationRecordOrder(pi,oi,{[f]:value},{reason});
    if(!operationRecordFeedback(outcome))return;
    render();
    if(field.tagName==='SELECT'||field.type==='checkbox')renderPhases();else renderPhasesLite(pi);
  }));
}
// re-render só os campos calculados de uma fase (evita perder foco)
function renderPhasesLite(pi){
  if(globalThis.JPWForex?.executionBoardUI){JPWForex.executionBoardUI.render();return;}
  // recalcula R:R e risco$ inline sem reconstruir inputs
  const phaseEl=document.querySelector(`.phase[data-phase="${pi}"]`);
  if(!phaseEl)return;
  const ph=S.phases[pi];
  const rows=phaseEl.querySelectorAll('tbody tr');
  let lsum=0;
  ph.orders.forEach((o,oi)=>{
    const rr=(o.entry>0&&o.sl>0&&o.tp>0)?(Math.abs(o.tp-o.entry)/Math.abs(o.entry-o.sl)):0;
    const risco=o.status==='Aberta'&&o.recordStatus!=='voided'?orderRisk(o):0;
    const cells=rows[oi].querySelectorAll('.calc');
    if(cells[0])cells[0].textContent=rr>0?rr.toFixed(2):'—';
    if(cells[1]){cells[1].textContent=Number.isFinite(risco)&&o.status==='Aberta'&&o.recordStatus!=='voided'?fmtForexMoney(risco,{currency:o.currency}):'—'; cells[1].className='calc '+(risco>0?'neg':'');}
    if(o.recordStatus==='voided')return;
    lsum+=(+o.lote||0);
  });
  const loteSum=phaseEl.querySelector('tfoot .lote-sum');
  const riskSum=phaseEl.querySelector('tfoot .risk-sum');
  const lucroSum=phaseEl.querySelector('tfoot .lucro-sum');
  if(loteSum) loteSum.textContent=lsum.toFixed(2);
  if(riskSum) riskSum.textContent=phaseOpenRiskText(pi);
  if(lucroSum) lucroSum.textContent=phasePositiveResults(pi).text;
}

// ---- Params screen ----
function renderParams(){
  const state=JPWForex.state.read(),p=JPWForex.policy,context=JPWForex.state.recordContext(),facts=context.accountInputs;
  const txt=(id,value)=>{const el=$(id);if(el)el.textContent=value;};
  const pct=id=>{const item=p.get(id);return Number.isFinite(item.value)?item.value.toLocaleString('pt-BR')+'%':item.status;};
  txt('rpSaldoIni',fmtMoney2(facts?.si));txt('rpSaldoAtu',fmtMoney2(facts?.equity));txt('rpInicio',facts?.periodId||'LEGACY / não observado');
  txt('rpMDD',pct('P-03'));txt('rpAlarm','Sem parâmetro V11');txt('rpGenLev',fmtX(p.get('P-15').value));
  txt('rpGenRisk',pct('P-14'));txt('rpFW',p.get('P-30').status);
  txt('rpVrmN',String(p.get('P-12a').value.normalBelow));txt('rpVrmHV',String(p.get('P-12a').value.highAbove));
  txt('rpRefM',fmtPct(p.planning.referenceMonthlyReturn));txt('rpRefA',p.planning.annualReferenceRange.map(fmtPct).join('–'));
  const mb=$('matrixBody');if(mb)mb.innerHTML=p.phases.map(m=>`<tr><td class="hl">${esc(m.name)}</td><td>${m.lower}%</td><td>${m.upper??p.get(m.upperParameter).value}%</td><td>V11 · ${m.id}</td><td>${fmtX(m.maxLeverage)}</td><td>${esc(state.executionEligibility?.status||'BLOCKED')}</td></tr>`).join('');
  for(const id of ['iAtr55','iAtr660']){const el=$(id);if(el){el.value=id==='iAtr55'?(S.forex?.market?.atrShort??''):(S.forex?.market?.atrLong??'');el.disabled=true;el.title='Registre a observação H4 com fonte em Parâmetros.';}}
}

// ---- Atualização automática de câmbio (Frankfurter, ECB, sem chave) ----
// Só cobre os 8 pares de câmbio. US500 permanece suspenso pelo Estatuto V10.0.
// XAUUSD nem entra aqui — banido, sem motivo para infraestrutura.
const FX_MAP = {
  EURUSD:{base:'EUR',quote:'USD'}, GBPUSD:{base:'GBP',quote:'USD'},
  AUDUSD:{base:'AUD',quote:'USD'}, NZDUSD:{base:'NZD',quote:'USD'},
  USDJPY:{base:'USD',quote:'JPY'}, USDCHF:{base:'USD',quote:'CHF'},
  USDCAD:{base:'USD',quote:'CAD'}, AUDCAD:{base:'AUD',quote:'CAD'},
};
let fxAutoFetchedThisSession=false;
async function updateFxRates(){
  if(!JPWForex.marketQuotes){
    document.addEventListener('DOMContentLoaded',()=>updateFxRates(),{once:true});return;
  }
  return JPWForex.marketQuotes.update();
}


function daysStale(dateStr){
  if(!dateStr) return 999;
  const then=new Date(dateStr+'T00:00:00');
  const now=new Date(); now.setHours(0,0,0,0);
  return Math.round((now-then)/86400000);
}
function staleInfo(dateStr){
  const d=daysStale(dateStr);
  if(d<=3) return {cls:'fresh', label:d<=0?'hoje':d+' dia'+(d>1?'s':'')+' atrás'};
  if(d<=20) return {cls:'warn', label:d+' dias atrás'};
  return {cls:'danger', label:d+' dias — não confiável'};
}
function dateISO(d){
  const x=d instanceof Date ? d : new Date(d);
  const y=x.getFullYear();
  const m=String(x.getMonth()+1).padStart(2,'0');
  const day=String(x.getDate()).padStart(2,'0');
  return `${y}-${m}-${day}`;
}
function todayISO(){ return dateISO(new Date()); }
function localDateTimeISO(d=new Date()){
  const x=d instanceof Date ? d : new Date(d);
  const hh=String(x.getHours()).padStart(2,'0');
  const mm=String(x.getMinutes()).padStart(2,'0');
  const ss=String(x.getSeconds()).padStart(2,'0');
  return `${dateISO(x)}T${hh}:${mm}:${ss}`;
}
function addDaysISO(days){ const d=new Date(); d.setDate(d.getDate()+days); return dateISO(d); }

function renderMotor(){
  const exp=$('mExpAlvo');if(exp){exp.value='';exp.disabled=true;exp.title='Teto não dimensiona volume admissível.';}
  const mb=$('motorBody');if(!mb)return;
  const model=JPWForex.state.read();
  mb.innerHTML=S.instruments.map((ins,i)=>{
    const unit=usdPerBase(ins)*ins.cpl,st=staleInfo(ins.updated);
    return `<tr data-idx="${i}"><td class="hl">${esc(ins.name)}</td><td><input type="number" step="0.00001" data-f="preco" value="${esc(ins.preco)}" aria-label="Preço ${esc(ins.name)}"></td><td><span class="stale-pill ${st.cls}">${esc(st.label)}</span></td><td><input type="number" step="1" data-f="cpl" value="${esc(ins.cpl)}" aria-label="Contrato ${esc(ins.name)}"></td><td class="calc-valorlote">${fmtMoney(unit)}</td><td class="calc-lotepad">${esc(model.metrics.admissionRisk.status)}</td><td class="calc-lotehv">${esc(model.executionEligibility.status)}</td><td>Limites: motor V11</td><td>${ins.banned?esc(ins.banReason||'Restrição registrada'):'P-14 / P-18 / P-17 pendentes'}</td></tr>`;
  }).join('');
  mb.querySelectorAll('input').forEach(input=>input.addEventListener('change',()=>{
    const i=+input.closest('tr').dataset.idx,field=input.dataset.f,value=orderParseResult(input.value);
    if(!(value>0)){alert('Informe um valor positivo.');return;}
    const outcome=JPWForex.state.mutate('instrument-observation','Observação confirmada de '+field,['instruments'],()=>{
      S.instruments[i][field]=value;if(field==='preco')S.instruments[i].updated=todayISO();
    });
    if(operationRecordFeedback(outcome)){recomputeMotorRow(i);render();}
  }));
  const pb=$('profileBody');if(pb)pb.innerHTML=`<tr><td colspan="6">${esc(JPWForex.engine.computeReplicationFirewall({}).status)} · P-30: fatores satélites sem homologação. Perfis legados permanecem como descrição histórica e não dimensionam lotes.</td></tr>`;
}
function recomputeMotorRow(i){
  const tr=document.querySelector(`#motorBody tr[data-idx="${i}"]`),ins=S.instruments[i];if(!tr||!ins)return;
  tr.querySelector('.calc-valorlote').textContent=fmtMoney(usdPerBase(ins)*ins.cpl);
  const model=JPWForex.state.read();
  tr.querySelector('.calc-lotepad').textContent=model.metrics.admissionRisk.status;tr.querySelector('.calc-lotehv').textContent=model.executionEligibility.status;
  const st=staleInfo(ins.updated),pill=tr.querySelector('.stale-pill');pill.className='stale-pill '+st.cls;pill.textContent=st.label;
}

// ---- Contas screen ----
function getMaster(){ return S.accounts.find(a=>a.tipo==='MESTRE')||S.accounts[0]; }
function profileFactor(){return JPWForex.engine.computeReplicationFirewall({}).value;}
function contaCalc(a){
  const master=getMaster();
  const lucro=a.sini>0&&Number.isFinite(a.satu)?(a.satu-a.sini)/a.sini:null;
  const corr=master?.sini>0&&Number.isFinite(a.sini)?a.sini/master.sini:null;
  const firewall=JPWForex.engine.computeReplicationFirewall({maxLossPercent:a.maxLossPercent,safetyMarginPercent:a.safetyMarginPercent});
  return {lucro,corr,fw:firewall.value,pf:firewall.value,loteVs:firewall.value,firewall};
}
function accountFactorText(value){return Number.isFinite(value)?value.toFixed(3):'BLOCKED';}
// ---- PIN de alteração de perfil (fricção deliberada, NÃO é criptografia real —
//      qualquer um com DevTools pode editar o localStorage e contornar isso.
//      O objetivo é impedir o clique impulsivo, não resistir a um invasor.) ----
async function sha256Hex(text){
  const enc=new TextEncoder().encode(text);
  const buf=await crypto.subtle.digest('SHA-256',enc);
  return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('');
}
async function requestPinUnlock(operationEpoch=jpWealthPersistenceEpoch()){
  if(!S.riskPinHash){
    const p1=prompt('Nenhuma senha definida ainda.\nCrie uma senha para futuras alterações de perfil de risco:');
    if(p1===null || p1.trim()==='') return false;
    const p2=prompt('Confirme a senha:');
    if(p2!==p1){ alert('As senhas não coincidem. Nada foi alterado.'); return false; }
    const hash=await sha256Hex(p1);
    if(jpWealthPersistenceIsBlocked() || operationEpoch!==jpWealthPersistenceEpoch()) return false;
    S.riskPinHash=hash;
    save();
    alert('Senha definida. Esta alteração de perfil está liberada — as próximas exigirão a senha.');
    return true;
  }
  const p=prompt('Digite a senha para alterar o perfil de risco desta conta:');
  if(p===null) return false;
  const h=await sha256Hex(p);
  if(jpWealthPersistenceIsBlocked() || operationEpoch!==jpWealthPersistenceEpoch()) return false;
  if(h!==S.riskPinHash){ alert('Senha incorreta. Perfil permanece travado.'); return false; }
  return true;
}
// Cadastro e edição possuem uma única fronteira validada no workspace de contas.
// Este quadro conserva somente a memória de correção/replicação existente.
function renderContasMemory(){
  const cb=$('contasBody');
  if(cb)cb.innerHTML=(S.accounts||[]).map(a=>{
    const {corr,fw,pf,loteVs}=contaCalc(a);
    return `<tr><th scope="row">${esc(a.nome||'Conta sem nome')}</th><td>${Number.isFinite(corr)?corr.toFixed(3):'Não apurado'}</td><td>${accountFactorText(fw)}</td><td>${accountFactorText(pf)}</td><td class="hl">${accountFactorText(loteVs)}</td></tr>`;
  }).join('')||'<tr><td colspan="5">Nenhuma conta cadastrada.</td></tr>';
  renderAplicacao();
}
function renderContas(){
  renderContasMemory();
  window.JPWForex?.accountsUI?.render?.();
}
function recomputeContasCalc(){renderContas();}
function renderAplicacao(){
  $('cLoteMaster').value=S.loteMaster;
  const ab=$('aplicBody');
  ab.innerHTML=S.accounts.map(a=>{
    const {loteVs}=contaCalc(a);
    return `<tr><td class="hl">${esc(a.nome)}</td><td>${accountFactorText(loteVs)}</td><td class="hl">${Number.isFinite(loteVs)?(S.loteMaster*loteVs).toFixed(3):'BLOCKED'}</td></tr>`;
  }).join('');
}

// ---- Dashboard — Acompanhamento Mensal estilo MQL5 Signals ----
// Linhas = anos, colunas = Jan..Dez (% do mês) + total composto do ano.
function renderDash(){
  const box=$('mqlMonthly'); if(!box) return;
  const MESES=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
  const selection=JPWForex.state.operationalSelection(),context=JPWForex.state.accountContext(selection);
  const opening=context.status==='OK'?context.value.openingBook:null;
  const led=context.status==='OK'?[...context.value.ledger].sort((a,b)=>a.data.localeCompare(b.data)):[];
  if(context.status!=='OK'||!(typeof opening==='number'&&Number.isFinite(opening)&&opening>0)){
    box.innerHTML='<p class="muted">Selecione uma conta e registre o período com saldo inicial contábil para acompanhar a evolução.</p>';
    for(const id of ['dRetAcum','dDDmax','dMar']){const node=$(id);if(node)node.textContent='—';}
    const charts=$('dashCharts');if(charts)charts.innerHTML='<p class="muted">Série indisponível: conta, período ou saldo inicial contábil não confirmado.</p>';
    return;
  }
  const pivot={}; // {ano:{mes: retorno}}
  let retAcum=0, ddMax=0;
  if(led.length){
    const fimDoMes={}; // último saldo de cada YYYY-MM
    led.forEach(e=>{
      fimDoMes[e.data.slice(0,7)]=e.saldo;
      ddMax=Math.max(ddMax,Math.max(0,(opening-e.saldo)/opening));
    });
    let prev=opening;
    Object.keys(fimDoMes).sort().forEach(k=>{
      const [y,m]=k.split('-');
      (pivot[y]=pivot[y]||{})[+m]=prev>0?fimDoMes[k]/prev-1:null;
      prev=fimDoMes[k];
    });
    retAcum=led[led.length-1].saldo/opening-1;
  }
  const anos=Object.keys(pivot).sort();
  const noEpBanner=noExternalProtectionActive()?`<div class="risk-note" style="margin:0 0 12px; color:var(--f4); border-color:var(--f4)">${noExternalProtectionWarning()}</div>`:'';
  if(!anos.length){
    box.innerHTML=noEpBanner+'<p class="muted" style="font-size:calc(12px * var(--fs-scale))">Sem dados ainda — registre fechamentos diários na aba 07 Contabilidade.</p>';
  } else {
    let html=`<table class="dtable" style="font-size:calc(11px * var(--fs-scale)); min-width:780px">
      <thead><tr><th>Ano</th>${MESES.map(m=>`<th style="text-align:right">${m}</th>`).join('')}<th style="text-align:right; border-left:1px solid var(--line)">Ano</th></tr></thead><tbody>`;
    anos.forEach(y=>{
      let f=1; html+=`<tr><td class="hl">${y}</td>`;
      for(let m=1;m<=12;m++){
        const r=pivot[y][m];
        if(r!=null){ f*=1+r; html+=`<td style="text-align:right"><span class="${r>0?'pos':(r<0?'neg':'muted')}">${(r*100).toFixed(2).replace('.',',')}</span></td>`; }
        else html+='<td style="text-align:right" class="muted">—</td>';
      }
      html+=`<td style="text-align:right; border-left:1px solid var(--line)"><span class="${f-1>=0?'pos':'neg'}" style="font-weight:700">${((f-1)*100).toFixed(2).replace('.',',')}%</span></td></tr>`;
    });
    html+=`</tbody></table><p style="font-size:calc(10px * var(--fs-scale)); color:var(--ink-faint); margin-top:8px">Valores em % ao mês (composto no total do ano) — mesmo formato do acompanhamento MQL5 Signals. Derivado do fechamento diário.</p>`;
    box.innerHTML=noEpBanner+html;
  }
  $('dRetAcum').textContent=led.length?(retAcum*100).toFixed(1)+'%':'—';
  $('dDDmax').textContent=led.length?(ddMax*100).toFixed(1)+'%':'—';
  $('dMar').textContent=led.length&&ddMax>0?(retAcum/ddMax).toFixed(2):'—';
  $('dMeta').textContent=JPWForex.policy.planning.referenceMonthlyReturn.toFixed(1)+'%';
  renderDashCharts();
}

// ---- Dashboard — Gráficos de acompanhamento (evolução patrimonial, drawdown, expectativa vs real) ----
// Reutiliza o ledger (fechamento diário) e a projeção da meta do perfil ativo. NÃO substitui a
// tabela MQL5 acima — complementa. Sem dependência externa; SVG inline; cores por var(--*) => tema claro/escuro.
// Seguro com ledger vazio: a linha de expectativa aparece sempre; a curva real só a partir do 1º fechamento.

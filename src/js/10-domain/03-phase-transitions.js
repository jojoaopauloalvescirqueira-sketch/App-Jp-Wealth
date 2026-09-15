// Forex V11: grade containers are records, never execution authorization.
// Public legacy entry points remain callable and do not move or duplicate facts.
const TRANSITION_QUESTIONNAIRES=Object.freeze({});
const DOWNGRADE_QUESTIONNAIRE=Object.freeze({});
function closeModal(){
  if(typeof operationDiscardReview==='function')operationDiscardReview();
  if(typeof window.__cleanupOnboardingModalUI === 'function'){
    try{ window.__cleanupOnboardingModalUI(); }catch(e){}
    window.__cleanupOnboardingModalUI=null;
  }
  $('modalOverlay').classList.remove('show');
  $('modalBox').classList.remove('onboarding-modal');
  $('modalBox').innerHTML='';
  renderOnboardingIncompleteBanner();
  renderExecutionOnboardingWarning();
  renderConfigOnboarding();
}

function operationOrderIsLive(o){
  return !!o && (o.status === 'Aberta' || o.status === 'Fechada' || o.status === 'Migrada' || o.status === 'Pendente');
}

function operationLiveOrders(){
  const out = [];
  (S.phases || []).forEach((ph, pi) => {
    ((ph && ph.orders) || []).forEach((o, oi) => { if (operationOrderIsLive(o)) out.push({ o, pi, oi }); });
  });
  return out;
}

function operationResolveThesis(vivas){
  const pares = [...new Set(vivas.map(x => String(x.o.par || '').trim().toUpperCase()).filter(Boolean))];
  const tipos = [...new Set(vivas.map(x => String(x.o.tipo || '').trim().toUpperCase()).filter(Boolean))];
  const findings=[];
  if(pares.length>1)findings.push({code:'INSTRUMENT_CONFLICT',instruments:pares});
  if(tipos.length>1)findings.push({code:'DIRECTION_CONFLICT',directions:tipos});
  return {ok:true,instrument:pares.length===1?pares[0]:null,direction:tipos.length===1?tipos[0]:null,instruments:pares,directions:tipos,findings};
}

function activePhaseRangeLabel(idx){
  const row=JPWForex.policy.phases?.[idx];
  return row?`${row.ddMinPercent}%–${row.ddMaxPercent}%`:'Não apurado';
}
function transitionSubtitleFor(faseNum){return 'A fase é apurada pelo motor V11; registrar fatos não exige questionário.';}
function activeLimitQuestionText(txt){return String(txt||'');}
function openTransitionModal(){alert('Registre os fatos livremente. A fase da conta e a elegibilidade são apuradas no motor V11; questionários não liberam ordens.');}
function getMaxUnlockedIdx(){
  const phase=JPWForex.state.read().activeGridPhase;
  const value=phase&&phase.status==='OK'?phase.value:null;
  const number=typeof value==='number'?value:value?.number;
  return Number.isInteger(number)?number-1:null;
}
function phaseVacated(pi){return !(S.phases[pi]?.orders||[]).some(o=>o.status==='Aberta'&&o.recordStatus!=='voided');}
function checkDowngrade(){return null;}
function openDowngradeModal(){openTransitionModal();}
function mirrorPhaseForward(){return false;}
function phaseFrozen(){return false;}
function healSupersededPhases(){return false;}
function phaseTetoRisco(){
  const metric=JPWForex.state.read().metrics?.openRiskLimit;
  return metric?.status==='OK'&&Number.isFinite(metric.value)?metric.value:null;
}
function checkPhaseCap(){
  const model=JPWForex.state.read();
  return {excede:null,recordable:model.canRecord===true,status:model.executionEligibility?.status||'NOT_COMPUTABLE',findings:structuredClone(model.findings||[])};
}
function phaseCapBreachMessage(pi,check){return (check.findings||[]).map(f=>f.message||f.code).join(' · ');}
function phaseSupportForRisk(){return null;}
function stopLimitSummary(pi,oi,check){return {phase:pi,orderId:S.phases[pi]?.orders[oi]?.orderId||null,findings:check.findings||[]};}
function auditStopLimit(){return {ok:false,error:'Registre o fato pelo comando de ordem para preservar a versão e o contexto.'};}
function handleStopLimitBreach(){return JPWForex.state.read().findings;}
function orderGateMsg(pi,oi){return operationValidateOrder(S.phases[pi]?.orders[oi]);}
function orderComplianceFindings(){
  const model=JPWForex.state.read(), thesis=operationResolveThesis(operationLiveOrders());
  return [...(model.findings||[]),...(thesis.findings||[])];
}
const DIVERGENCE_REASONS=['Slippage de execução (gap, liquidez, spread)','Erro de programação da ordem (SL mal calculado/registrado)','Rompimento de protocolo — stop foi movido/ignorado sem justificativa','Outro'];
function orderParseResult(txt){
  const t=String(txt==null?'':txt).trim().replace(',','.');
  if(!t) return NaN;
  if(!/^-?\d+(?:\.\d+)?$/.test(t)) return NaN;
  return parseFloat(t);
}
// Ordem cujo resultado NÃO foi informado. Só reconhece ausência GENUÍNA: valor
// que não é número finito. Ordens gravadas antes desta correção, que receberam
// zero por coerção, são indistinguíveis de um zero verdadeiro — e adivinhar
// quais eram quais seria fabricar dado histórico.
function orderResultMissing(o){
  // Number.isFinite NAO coage: devolve false para undefined, null, '' e '5'.
  // Um typeof extra seria redundante e so tornaria a precedencia confusa.
  return !!o && !Number.isFinite(o.result);
}

function openCloseOrderModal(pi,oi){
  const o=S.phases[pi].orders[oi];
  const box=$('modalBox');
  $('modalOverlay').classList.add('show');
  const projetado=orderRisk(o);
  box.innerHTML=`
    <h3>🔒 Confirmar Fechamento — ${esc(o.id)||'(sem ID)'} ${esc(o.par)}</h3>
    <div class="modal-sub">Correções posteriores exigem motivo e preservam a versão anterior. A anulação mantém a ordem no histórico. ${projetado>0?'Risco programado desta ordem: '+fmtForexMoney(projetado,{currency:o.currency}):''}</div>
    <div class="modal-q" data-qid="resultado">
      <div class="ql">Resultado da ordem (${esc(o.currency||'moeda não capturada')}) — negativo se foi prejuízo, <b>0</b> se fechou no zero a zero:</div>
      <input type="text" inputmode="decimal" id="closeResultInput" placeholder="informe" value="${Number.isFinite(o.result)?esc(String(o.result)):''}">
      <div class="modal-err">Informe o resultado. Em branco não é zero — se a ordem fechou no zero a zero, digite <b>0</b>.</div>
    </div>
    <div class="modal-q" data-qid="confirmtxt">
      <div class="ql">Digite <b>FECHADO</b> para confirmar:</div>
      <input type="text" id="closeConfirmInput" autocomplete="off">
      <div class="modal-err">Precisa digitar exatamente "FECHADO".</div>
    </div>
    <div class="modal-actions">
      <button class="modal-btn cancel" id="modalCancel">Cancelar</button>
      <button class="modal-btn confirm" id="modalConfirm">Confirmar Fechamento</button>
    </div>`;
  $('modalCancel').addEventListener('click', closeModal);
  $('modalConfirm').addEventListener('click',()=>{
    const resultVal=orderParseResult(box.querySelector('#closeResultInput').value);
    const confirmTxt=box.querySelector('#closeConfirmInput').value.trim();
    let falhou=false;
    // RESULTADO EXPLÍCITO é condição de fechamento. Uma ordem não pode nascer
    // fechada sem resultado: ela entra em netOpAtual(), que alimenta o
    // consolidado da Operação Única e, por ele, o registro imutável.
    box.querySelector('[data-qid="resultado"] .modal-err').classList.remove('show');
    if(!Number.isFinite(resultVal)){
      box.querySelector('[data-qid="resultado"] .modal-err').classList.add('show');
      falhou=true;
    }
    if(confirmTxt!=='FECHADO'){
      box.querySelector('[data-qid="confirmtxt"] .modal-err').classList.add('show');
      falhou=true;
    }
    if(falhou) return;
    const saved=operationRecordOrder(pi,oi,{status:'Fechada',result:resultVal},{reason:'Fechamento confirmado pelo operador'});
    if(!operationRecordFeedback(saved))return;
    closeModal();
    render(); renderPhases();
    checkDivergence(pi,oi);
  });
}

function checkDivergence(){return orderComplianceFindings();}
function openDivergenceModal(pi,oi,projetado,result,divergencia){
  const box=$('modalBox');
  const order=S.phases[pi]?.orders?.[oi];
  const pctTxt=((divergencia-1)*100).toFixed(0);
  let html=`<h3>⚠️ Divergência de fechamento</h3>
    <div class="modal-sub">Prejuízo registrado ${fmtForexMoney(Math.abs(result),{currency:order?.currency})}. ${order?.currency?`${pctTxt}% acima do risco programado (${fmtForexMoney(projetado,{currency:order.currency})}).`:'Comparação com o risco indisponível sem unidade conciliada.'} Isso não bloqueia nada; é auditoria, não permissão.</div>
    <div class="modal-q" data-qid="motivo">
      <div class="ql">Qual foi a causa da divergência?</div>`;
  DIVERGENCE_REASONS.forEach((r,i)=>{
    html+=`<label class="check-row"><input type="radio" name="divreason" value="${i}"> ${r}</label>`;
  });
  html+=`<div class="modal-err">Selecione uma causa antes de prosseguir.</div>
    </div>
    <div class="modal-q" data-qid="detalhe" style="display:none">
      <div class="ql">Detalhe (opcional):</div>
      <textarea placeholder="Contexto adicional, se relevante"></textarea>
    </div>
    <div class="modal-actions">
      <button class="modal-btn confirm" id="modalConfirm">Registrar causa</button>
    </div>`;
  box.innerHTML=html;
  $('modalOverlay').classList.add('show');
  box.querySelectorAll('input[name=divreason]').forEach(r=>{
    r.addEventListener('change',()=>{
      box.querySelector('[data-qid="detalhe"]').style.display = r.value==='3'?'block':'none';
      box.querySelector('[data-qid="motivo"] .modal-err').classList.remove('show');
    });
  });
  $('modalConfirm').addEventListener('click',()=>{
    const sel=box.querySelector('input[name=divreason]:checked');
    if(!sel){ box.querySelector('[data-qid="motivo"] .modal-err').classList.add('show'); return; }
    const reasonText=DIVERGENCE_REASONS[+sel.value];
    const detalhe=box.querySelector('[data-qid="detalhe"] textarea')?.value.trim()||'';
    const cause=reasonText+(detalhe?(' — '+detalhe):'');
    if(!operationRecordFeedback(operationRecordOrder(pi,oi,{divergenceReason:cause},{reason:'Causa de divergência: '+cause})))return;
    closeModal();
    render();
  });
}


function phasePositiveResults(pi){
  const closed=(S.phases[pi]?.orders||[]).filter(o=>o.status==='Fechada'&&o.recordStatus!=='voided');
  if(!closed.length)return {present:false,text:'—'};
  const first=closed[0];
  const scoped=first.accountId&&first.periodId&&first.currency&&closed.every(o=>
    o.accountId===first.accountId&&o.periodId===first.periodId&&o.currency===first.currency&&Number.isFinite(o.result));
  return {present:true,text:scoped?fmtForexMoney(closed.reduce((sum,o)=>sum+Math.max(0,o.result),0),{currency:first.currency}):
    'Não consolidado: conta, período ou moeda não conciliados'};
}
function phaseOpenRiskText(pi){
  const open=(S.phases[pi]?.orders||[]).filter(o=>o.status==='Aberta'&&o.recordStatus!=='voided');
  if(!open.length)return '—';
  const first=open[0],risks=open.map(orderRisk);
  const scoped=first.accountId&&first.periodId&&first.currency&&open.every(o=>
    o.accountId===first.accountId&&o.periodId===first.periodId&&o.currency===first.currency)&&risks.every(Number.isFinite);
  return scoped?fmtForexMoney(risks.reduce((sum,risk)=>sum+risk,0),{currency:first.currency}):'Não consolidado: contexto ou risco não apurado';
}
// Constrói o corpo de UMA grade (meta + tabela + botão adicionar).
function phaseBodyHTML(pi, qAct){
  const ph=S.phases[pi], isGen=pi===0, frozen=false;
  const legacy=ph.policyVersion==='LEGACY_UNRESOLVED'||S.phases.length===4;
  const faixaDDLabel=legacy?'LEGACY — faixa não reinterpretada':activePhaseRangeLabel(pi);
  let rows='', lsum=0;
  const positiveResults=phasePositiveResults(pi);
  ph.orders.forEach((o,oi)=>{
    const slot = o.role==='GENESIS'?'GÊNESE':o.role==='DEFENSE'?'DEFESA':(legacy?(isGen&&oi===0?'GÊNESE LEGACY':`SLOT LEGACY ${pi+1}.${oi+1}`):`ORDEM ${pi+1}.${oi+1}`);
    const rr = (o.entry>0&&o.sl>0&&o.tp>0)?(Math.abs(o.tp-o.entry)/Math.abs(o.entry-o.sl)):0;
    const risco = o.status==='Aberta'&&o.recordStatus!=='voided'?orderRisk(o):0;
    const semStop = o.status==='Aberta' && o.lote>0 && !(o.sl>0);
    const isFechada = o.status==='Fechada';
    const isMigrada = o.status==='Migrada';
    const readOnly = o.recordStatus==='voided';
    const dis = readOnly?'disabled':'';
    const disStatus = readOnly?'disabled':'';
    const rowCls = (isMigrada||frozen||isFechada)?'row-migrada':(o.stopPhaseWarning?'stop-breach':(o.needsReview?'needs-review':''));
    const slotLabel = o.recordStatus==='voided' ? slot+' <span class="review-badge">ANULADA · preservada</span>' : isMigrada ? slot+' <span class="review-badge" style="color:var(--ink-faint);background:transparent">→ migrada</span>'
                     : frozen ? slot+' <span class="review-badge" style="color:var(--ink-faint);background:transparent">🔒 histórico</span>'
                     : semStop ? slot+' <span class="review-badge" style="color:var(--danger);background:var(--f4-bg)">✋ SEM STOP</span>'
                     : o.stopPhaseWarning ? slot+' <span class="review-badge" style="color:var(--danger);background:var(--f4-bg)">⚠ stop acima da fase</span>'
                     : o.needsReview ? slot+' <span class="review-badge">⚠ novo stop pendente</span>'
                     : slot;
    rows+=`<tr class="${slot==='GÊNESE'?'slot-gen':''} ${rowCls}">
      <td>${slotLabel}${o.stopPhaseWarning?`<div class="stop-warning">${esc(o.stopPhaseWarning)}</div>`:''}</td>
      <td class="calc">${rr>0?rr.toFixed(2):'—'}</td>
      <td class="calc ${risco>0?'neg':''}">${Number.isFinite(risco)&&o.status==='Aberta'&&o.recordStatus!=='voided'?fmtForexMoney(risco,{currency:o.currency}):(semStop?'<span style="color:var(--danger)">?!</span>':'—')}</td>
      <td><select data-p="${pi}" data-o="${oi}" data-f="role" aria-label="Papel da ordem ${esc(o.id||slot)}" ${dis}><option value="">Não declarado</option><option value="GENESIS" ${o.role==='GENESIS'?'selected':''}>Gênese</option><option value="DEFENSE" ${o.role==='DEFENSE'?'selected':''}>Defesa</option><option value="OTHER" ${o.role==='OTHER'?'selected':''}>Outro</option></select></td>
      <td><input data-p="${pi}" data-o="${oi}" data-f="id" value="${esc(o.id)}" placeholder="—" ${dis}></td>
      <td><select data-p="${pi}" data-o="${oi}" data-f="par" ${dis} style="text-align:center">
        <option value="" ${!o.par?'selected':''}>—</option>
        ${S.instruments.map(ins=>`<option ${String(o.par||'').toUpperCase().replace(/[^A-Z0-9]/g,'')===ins.name?'selected':''}>${esc(ins.name)}</option>`).join('')}
      </select></td>
      <td><select data-p="${pi}" data-o="${oi}" data-f="tipo" ${dis}><option ${o.tipo==='BUY'?'selected':''}>BUY</option><option ${o.tipo==='SELL'?'selected':''}>SELL</option></select></td>
      <td><input type="number" step="0.01" data-p="${pi}" data-o="${oi}" data-f="lote" value="${esc(o.lote||'')}" placeholder="0" ${dis}></td>
      <td><input type="number" step="0.00001" data-p="${pi}" data-o="${oi}" data-f="entry" value="${esc(o.entry||'')}" placeholder="0" ${dis}></td>
      <td class="stop-col"><input type="number" step="0.00001" data-p="${pi}" data-o="${oi}" data-f="sl" value="${esc(o.sl||'')}" placeholder="0" ${dis} title="Stop informado como fato. Desconformidades não impedem o registro."><span class="stop-note">Stop Técnico Quantitativo</span></td>
      <td><input type="number" step="0.00001" data-p="${pi}" data-o="${oi}" data-f="tp" value="${esc(o.tp||'')}" placeholder="0" ${dis} ${o.needsReview?'style="border-color:var(--f2)"':''}></td>
      <td>
        <select data-p="${pi}" data-o="${oi}" data-f="status" ${disStatus}>
          <option value="" ${!o.status?'selected':''}>—</option>
          <option value="Pendente" ${o.status==='Pendente'?'selected':''}>Pendente</option>
          <option value="Aberta" ${o.status==='Aberta'?'selected':''}>Aberta</option>
          <option value="Fechada" ${o.status==='Fechada'?'selected':''}>Fechada</option>
          ${isMigrada?'<option value="Migrada" selected>Migrada</option>':''}
        </select>
      </td>
      <td><input type="number" step="0.01" data-p="${pi}" data-o="${oi}" data-f="result" value="${esc(Number.isFinite(o.result)?o.result:'')}" placeholder="0"
            style="${isFechada?'':'opacity:.35'}" title="Resultado da ordem — só conta quando Fechada (Art. 9.2)" ${dis}><small>${esc(o.currency||'moeda não capturada')}</small></td>
      <td><input type="number" step="0.01" data-p="${pi}" data-o="${oi}" data-f="costs" aria-label="Custos da ordem ${esc(o.id||slot)}" value="${esc(Number.isFinite(o.costs)?o.costs:'')}" placeholder="ausente" ${dis}><small>${esc(o.currency||'moeda não capturada')}</small></td>
      <td><select data-p="${pi}" data-o="${oi}" data-f="costBasis" aria-label="Base dos custos ${esc(o.id||slot)}" ${dis}><option value="">Não declarada</option><option value="SEPARATE_FROM_RESULT" ${o.costBasis==='SEPARATE_FROM_RESULT'?'selected':''}>Separados do resultado</option><option value="INCLUDED_IN_RESULT" ${o.costBasis==='INCLUDED_IN_RESULT'?'selected':''}>Incluídos no resultado</option></select></td>
      <td><input type="checkbox" data-p="${pi}" data-o="${oi}" data-f="stopValidated" aria-label="Stop tecnicamente validado ${esc(o.id||slot)}" ${o.stopValidated===true?'checked':''} ${dis}></td>
      <td><input type="checkbox" data-p="${pi}" data-o="${oi}" data-f="amplifiesExposure" aria-label="Pendente amplia exposição ${esc(o.id||slot)}" ${o.amplifiesExposure===true?'checked':''} ${dis}></td>
      <td><input type="checkbox" data-p="${pi}" data-o="${oi}" data-f="pendingActive" aria-label="Pendente ativa ${esc(o.id||slot)}" ${o.pendingActive===true?'checked':''} ${dis}></td>
      <td>${readOnly?'':`<button class="row-del" data-delorder="${pi}:${oi}" title="${operationOrderIsLive(o)?'Anular preservando o histórico':'Excluir rascunho'}">✕</button>`}${o.revisions?.length?`<button class="reset-btn" data-orderhistory="${pi}:${oi}" aria-label="Ver versões da ordem ${esc(o.id||o.orderId)}">v${o.recordVersion}</button>`:''}</td>
    </tr>`;
  });
  ph.orders.forEach(o=>{ if(o.recordStatus==='voided')return; lsum+=(+o.lote||0); });
  return `
    <div class="phase-meta">
      <span>Faixa DD: <b>${faixaDDLabel}</b></span>
      <span>${legacy?'Descrição histórica: <b>'+esc(ph.alavtxt)+'</b>':'Elegibilidade apurada no motor central'}</span>

      ${positiveResults.present?`<span>Resultados positivos registrados: <b>${esc(positiveResults.text)}</b></span>`:''}

      ${frozen?`<span style="color:var(--ink-faint)">🔒 Fase superada — somente histórico, sem edição</span>`:''}
    </div>
    <div style="overflow-x:auto">
    <table class="otable">
      <thead><tr><th>Slot</th><th>R:R</th><th>Risco na moeda da ordem</th><th>Papel declarado</th><th>ID</th><th>Par</th><th>Tipo</th><th>Lote</th><th>Entrada</th><th>Stop Técnico Quantitativo</th><th>TP</th><th>Status</th><th>Resultado</th><th>Custos assinados</th><th>Base dos custos</th><th>Stop validado</th><th>Pendente amplia</th><th>Pendente ativa</th><th></th></tr></thead>
      <tbody>${rows}</tbody>
      <tfoot><tr><td>Σ ${esc(ph.faseNome)}</td><td></td><td class="calc risk-sum">${esc(phaseOpenRiskText(pi))}</td><td colspan="4"></td><td class="lote-sum">${lsum.toFixed(2)}</td><td colspan="4"></td><td class="calc lucro-sum">${esc(positiveResults.text)}</td><td colspan="6"></td></tr></tfoot>
    </table>
    </div>
    ${`<button class="reset-btn" data-addorder="${pi}" style="margin-top:10px; color:var(--violet); border-color:var(--violet)">+ Adicionar ordem à ${esc(ph.faseNome)}</button>`}`;
}

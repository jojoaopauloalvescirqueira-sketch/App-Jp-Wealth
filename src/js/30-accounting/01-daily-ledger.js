// ============ 07 CONTABILIDADE — fechamento diário, Real vs Projetado, log de auditoria ============
function ledgerOperationalScope(){
  const selection=window.JPWForex?.state?.operationalSelection?.()||{};
  return {accountId:selection.accountId||null,periodId:selection.periodId||null};
}
function ledgerScopedRead(){
  const scope=ledgerOperationalScope();
  return scope.accountId&&scope.periodId?window.JPWForex.state.accountLedger(scope):null;
}
function ledgerSorted(){
  const scoped=ledgerScopedRead();
  return [...(scoped?.status==='OK'?scoped.value:[])].sort((a,b)=>a.data.localeCompare(b.data));
}
function archiveCurrentLedgerForNewPeriod(nextPeriodMeta){
  const led=ledgerSorted();
  if(!led.length) return null;
  if(!Array.isArray(S.ledgerArchive)) S.ledgerArchive=[];
  const snapshot={
    archivedAt:new Date().toISOString(),
    previousInicio:S.params&&S.params.inicio||'',
    previousSaldoIni:S.params&&S.params.saldoIni||0,
    previousSaldoAtu:S.params&&S.params.saldoAtu||0,
    previousProfile:S.period&&S.period.profile||'base',
    count:led.length,
    firstDay:led[0].data||'',
    lastDay:led[led.length-1].data||'',
    nextPeriodMeta:structuredClone(nextPeriodMeta||{}),
    ledger:structuredClone(led)
  };
  S.ledgerArchive.push(snapshot);
  S.ledger=[];
  S.transitionLog.push({fase:'arquivamento de ledger', ts:snapshot.archivedAt,
    resumo:{motivo:'reinício de período', previousInicio:snapshot.previousInicio,
      previousSaldoIni:snapshot.previousSaldoIni, previousSaldoAtu:snapshot.previousSaldoAtu,
      previousProfile:snapshot.previousProfile, count:snapshot.count,
      firstDay:snapshot.firstDay, lastDay:snapshot.lastDay,
      nextInicio:snapshot.nextPeriodMeta.inicio||'', nextSaldoIni:snapshot.nextPeriodMeta.saldoIni||0,
      nextProfile:snapshot.nextPeriodMeta.profile||''}});
  return snapshot;
}
function syncSaldoAtuFromLedger(){
  const led=ledgerSorted();
  S.params.saldoAtu = led.length ? (+led[led.length-1].saldo||0) : (+S.params.saldoIni||0);
  return S.params.saldoAtu;
}
// Ledger e saldo corrente formam um único ato local. Recusa comprovada restaura
// somente esses campos e o log DG; uma exceção do save não prova não-escrita.
function ledgerMutate(fn){
  const unknown=()=>{
    hideStaleSavedTag();
    // Uma exceção posterior ao save pode suceder o aviso verde de recuperação.
    // Só esse aviso transitório é retirado; alertas de falha ficam preservados.
    const banner=persistenceAlertEl();
    if(banner && banner.classList.contains('is-recovered')){
      clearTimeout(jpWealthPersistenceFailure.recoveryTimer);
      banner.className='persistence-alert';banner.textContent='';
      layoutPersistenceBanners();
    }
    return ({ok:false,persistido:null,bloqueado:true,
    error:'Gravação indeterminada. Não repita a ação; confira a base salva antes de continuar.'});
  };
  if(jpWealthPersistenceOutcomeIsUnknown()){hideStaleSavedTag();return unknown();}
  let before,historyBefore;
  try{before=structuredClone(S.ledger);historyBefore=S.ledgerHistory===undefined?undefined:structuredClone(S.ledgerHistory);}
  catch(e){return {ok:false,persistido:false,error:'Não foi possível preparar o fechamento. Nada foi aplicado.'};}
  const balance=S.params.saldoAtu;
  const log=S.dataGovernance&&S.dataGovernance.changeLog;
  const logBefore=Array.isArray(log)?log.slice():null;
  const restore=()=>{
    S.ledger=before;S.params.saldoAtu=balance;
    if(historyBefore===undefined)delete S.ledgerHistory;else S.ledgerHistory=historyBefore;
    if(logBefore){log.splice(0,log.length,...logBefore);S.dataGovernance.changeLog=log;}
  };
  let result;
  try{result=fn()||{};if(result.ok===false){restore();return {...result,persistido:false};}}
  catch(e){restore();hideStaleSavedTag();return {ok:false,persistido:false,error:'Não foi possível aplicar o fechamento. Nada foi gravado.'};}
  let written;
  try{written=save();}
  catch(e){markJPWealthPersistenceOutcomeUnknown('fechamento diário');hideStaleSavedTag();return unknown();}
  if(written===false){
    restore();hideStaleSavedTag();
    return {ok:false,persistido:false,error:'Gravação recusada. O fechamento não foi alterado; resolva a falha antes de tentar novamente.'};
  }
  if(written!==true){markJPWealthPersistenceOutcomeUnknown('retorno indeterminado do fechamento diário');hideStaleSavedTag();return unknown();}
  return {...result,ok:true,persistido:true};
}
let ledgerStatusTimer=null;
function ledgerFeedback(message,ok){
  clearTimeout(ledgerStatusTimer);
  const status=$('ldStatus');if(!status)return;
  status.textContent=message;status.className='fx-status '+(ok?'ok':'err');
  if(ok)ledgerStatusTimer=setTimeout(()=>{status.textContent='';},2500);
}
// Ledger v2 is an explicit command projection over the compatible S.ledger list.
// History preserves facts removed from that projection; reads never assign IDs.
function ledgerContext(input){
  const source=input||ledgerOperationalScope();
  return {accountId:typeof source.accountId==='string'&&source.accountId?source.accountId:null,
    periodId:typeof source.periodId==='string'&&source.periodId?source.periodId:null,
    policyVersion:source.policyVersion||null};
}
function ledgerId(row,index){return row.id||'legacy:'+row.data+':'+index;}
function ledgerRows(){const scoped=ledgerScopedRead();return (scoped?.status==='OK'?scoped.value:[]).map((r,i)=>({...structuredClone(r),id:ledgerId(r,i),version:r.version||0,
  provenance:r.accountId&&r.periodId?'IDENTIFIED':'LEGACY_UNRESOLVED'}));}
function ledgerFind(id){return ledgerRows().find(r=>r.id===id);}
function ledgerValidDate(value){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(String(value)))return false;
  const d=new Date(value+'T12:00:00Z');return Number.isFinite(+d)&&d.toISOString().slice(0,10)===value;
}
function ledgerFinite(value){return (typeof value==='number'||typeof value==='string'&&value.trim()!=='')&&Number.isFinite(Number(value));}
function ledgerEvent(type,before,after,reason){
  if(S.ledgerHistory===undefined)S.ledgerHistory={schemaVersion:1,events:[]};
  if(S.ledgerHistory.schemaVersion!==1||!Array.isArray(S.ledgerHistory.events))throw new Error('Histórico incompatível');
  const event={id:'lde_'+crypto.randomUUID(),type,at:new Date().toISOString(),reason:String(reason||''),
    before:before?structuredClone(before):null,after:after?structuredClone(after):null};
  S.ledgerHistory.events.push(event);
  if(typeof dgLogChange==='function')dgLogChange('ledger',type,(after||before).id||'',type+' · '+(after||before).data);
  return event;
}
function ledgerRecord(input,{id=null,reason='',expectedVersion=null,allowBackdate=false,context,reconcileContext=false}={}){
  const scope=ledgerContext(context),ctx=window.JPWForex?.state?.accountContext?.(scope);
  const selected=ledgerOperationalScope();
  if(scope.accountId!==selected.accountId||scope.periodId!==selected.periodId)
    return {ok:false,persistido:false,error:'A conta/período da ação difere da seleção atual. Reabra o formulário.'};
  if(ctx?.status!=='OK')return {ok:false,persistido:false,error:'Selecione uma conta e período confirmados em Operação → Contas antes do fechamento.'};
  if(!ledgerValidDate(input.data)||!ledgerFinite(input.resultado))return {ok:false,persistido:false,error:'Informe data válida e resultado finito. Campo vazio não é zero.'};
  const old=id?ledgerFind(id):null;
  if(id&&(!old||old.accountId!==scope.accountId||old.periodId!==scope.periodId))return {ok:false,persistido:false,error:'Fechamento não pertence à conta/período selecionados.'};
  if(old&&expectedVersion!==null&&old.version!==expectedVersion)return {ok:false,persistido:false,error:'A linha mudou; revise antes de salvar.'};
  if(old&&!String(reason).trim())return {ok:false,persistido:false,error:'Informe o motivo explícito da correção.'};
  return window.JPWForex.state.recordAccountLedger({action:old?'CORRECTED':'RECORDED',id:old?.id||null,
    accountId:scope.accountId,periodId:scope.periodId,data:input.data,resultado:Number(input.resultado),
    saldo:input.saldo===''||input.saldo==null?null:Number(input.saldo),nota:input.nota||''},
    {reason:reason||'Fechamento diário confirmado em '+scope.accountId+' / '+scope.periodId,
      expectedRevision:ctx.revision,expectedEpoch:jpWealthPersistenceEpoch()});
  return ledgerMutate(()=>{
    const old=id?ledgerFind(id):null;
    if(id&&!old)return {ok:false,error:'Lançamento não encontrado. Atualize a visão.'};
    if(old&&expectedVersion!==null&&(old.version||0)!==expectedVersion)return {ok:false,error:'A versão foi alterada. Revise o lançamento antes de confirmar.'};
    if(old&&!String(reason).trim())return {ok:false,error:'Informe o motivo da correção.'};
    if(!ledgerValidDate(input.data)||!ledgerFinite(input.resultado))return {ok:false,error:'Informe data válida e resultado finito. Zero é válido.'};
    if(S.ledger.some(r=>r!==old&&r.data===input.data))return {ok:false,error:'Já existe fechamento nesta data. Use a correção explícita da linha.'};
    const later=S.ledger.filter(r=>r!==old&&r.data>input.data);
    if(later.length&&!allowBackdate)return {ok:false,error:'Há fechamentos posteriores. Confirme que os saldos históricos serão preservados.'};
    const previous=ledgerSorted().filter(r=>r!==old&&r.data<input.data).slice(-1)[0];
    const opening=previous&&ledgerFinite(previous.saldo)?Number(previous.saldo):ledgerFinite(S.params.saldoIni)?Number(S.params.saldoIni):null;
    const automatic=input.saldo===''||input.saldo==null;
    if((automatic&&!ledgerFinite(opening))||(!automatic&&!ledgerFinite(input.saldo)))return {ok:false,error:'Saldo de referência ou fechamento inválido.'};
    const saldo=automatic?opening+Number(input.resultado):Number(input.saldo);
    const ctx=old&&!reconcileContext?{accountId:old.accountId||null,periodId:old.periodId||null,policyVersion:old.policyVersion||null}:ledgerContext(context);
    if(reconcileContext&&(!ctx.accountId||!ctx.periodId))return {ok:false,error:'Vinculação exige conta e período identificados.'};
    const after={...(old||{}),...ctx,id:old&&old.id||'ld_'+crypto.randomUUID(),version:(old&&old.version||0)+1,
      data:input.data,resultado:Number(input.resultado),saldo,nota:String(input.nota||'').trim(),
      referenceBalance:old?old.referenceBalance??null:ledgerFinite(S.params.saldoIni)?Number(S.params.saldoIni):null,
      createdAt:old&&old.createdAt||null,updatedAt:new Date().toISOString(),
      origin:old&&old.origin||'MANUAL',balanceInput:automatic?'DERIVED_FROM_PREVIOUS':'OBSERVED'};
    if(!old)after.createdAt=after.updatedAt;
    const before=old?structuredClone(old):null;
    if(old)S.ledger[S.ledger.indexOf(old)]=after;else S.ledger.push(after);
    ledgerEvent(old?'CORRECTED':'RECORDED',before,after,reason);
    syncSaldoAtuFromLedger();return {ok:true,row:structuredClone(after)};
  });
}
function ledgerCorrect(id,input,options={}){return ledgerRecord(input,{...options,id});}
function ledgerVoid(id,{reason,expectedVersion=null}={}){
  const scope=ledgerOperationalScope(),ctx=window.JPWForex?.state?.accountContext?.(scope),row=ledgerFind(id);
  if(ctx?.status!=='OK'||!row)return {ok:false,persistido:false,error:'Selecione a conta/período do fechamento antes de anulá-lo.'};
  if(expectedVersion!==null&&row.version!==expectedVersion)return {ok:false,persistido:false,error:'A linha mudou; revise antes de anular.'};
  return window.JPWForex.state.recordAccountLedger({action:'VOIDED',id,accountId:scope.accountId,periodId:scope.periodId},
    {reason,expectedRevision:ctx.revision,expectedEpoch:jpWealthPersistenceEpoch()});
  return ledgerMutate(()=>{
    const row=ledgerFind(id);
    if(!row)return {ok:false,error:'Lançamento não encontrado.'};
    if(!String(reason||'').trim())return {ok:false,error:'Informe o motivo da anulação.'};
    if(expectedVersion!==null&&(row.version||0)!==expectedVersion)return {ok:false,error:'A versão foi alterada. Atualize a visão.'};
    ledgerEvent('VOIDED',row,null,reason);S.ledger.splice(S.ledger.indexOf(row),1);syncSaldoAtuFromLedger();return {ok:true};
  });
}
// Completeness is declared for a specific preview, never inferred from weekdays.
function ledgerMonthlyActual(month,context={}){
  const ctx=ledgerContext(context), all=ledgerRows(), rows=all.filter(r=>r.data.slice(0,7)===month&&r.accountId===ctx.accountId&&r.periodId===ctx.periodId);
  const issues=[];
  if(!/^\d{4}-(0[1-9]|1[0-2])$/.test(month))issues.push('Mês inválido.');
  if(!ctx.accountId||!ctx.periodId)issues.push('Selecione conta e período identificados. Legado sem origem não é vinculado automaticamente.');
  const currency=window.JPWForex?.state?.accountContext?.(ctx)?.value?.currency||null;
  if(currency!=='USD')issues.push('Importação no Planejamento USD exige conversão comprovada; a moeda desta conta não é USD.');
  if((S.ledger||[]).some(r=>r.data?.slice(0,7)===month&&(!r.accountId||!r.periodId)))issues.push('Existe legado contábil não conciliado neste mês; revise-o explicitamente antes de declarar completude.');
  if(!rows.length)issues.push('Nenhum fechamento identificado neste mês.');
  rows.sort((a,b)=>a.data.localeCompare(b.data));
  const previous=all.filter(r=>r.data<month+'-01'&&r.accountId===ctx.accountId&&r.periodId===ctx.periodId).sort((a,b)=>a.data.localeCompare(b.data)).slice(-1)[0];
  const opening=previous?previous.saldo:rows.length?rows[0].referenceBalance:null;
  let expected=ledgerFinite(opening)?Number(opening):null;
  rows.forEach(r=>{if(!ledgerFinite(r.resultado)||!ledgerFinite(r.saldo)||!ledgerFinite(expected)){issues.push('Fechamento incompleto.');return;}expected+=Number(r.resultado);if(Math.abs(expected-Number(r.saldo))>0.005)issues.push('Cadeia de saldos divergente em '+r.data+'. Corrija ou documente os fluxos antes de importar.');});
  if(context.complete!==true)issues.push('Completude mensal ainda não confirmada pelo operador.');
  const source={system:'JPW_DAILY_LEDGER',schemaVersion:1,accountId:ctx.accountId,periodId:ctx.periodId,month,
    rows:rows.map(r=>({id:r.id,version:r.version,data:r.data,resultado:r.resultado,saldo:r.saldo,policyVersion:r.policyVersion||null})),
    currency,openingBalanceUsd:currency==='USD'?opening:null,closingBalanceUsd:currency==='USD'&&rows.length?rows[rows.length-1].saldo:null,
    complete:context.complete===true};
  source.version=JSON.stringify(source);
  return {status:issues.length?'PARTIAL':'COMPLETE',issues,source,profitUsd:currency==='USD'&&rows.length&&rows.every(r=>ledgerFinite(r.resultado))?rows.reduce((sum,r)=>sum+Number(r.resultado),0):null};
}
const ledgerUI={filter:'',month:'',sort:'desc',selected:null,edit:null,draft:null};
function ledgerRefreshConsumers(){renderLedger();if(typeof renderDash==='function')renderDash();if(typeof renderParams==='function')renderParams();if(typeof render==='function')render();}
function ledgerMountTools(tb){
  const card=tb.closest('[data-layout-card]');if(!card||card.querySelector('#ledgerTools'))return;
  const tools=document.createElement('div');tools.id='ledgerTools';tools.className='ledger-tools';
  tools.innerHTML='<label>Buscar <input type="search" id="ledgerFilter" placeholder="Data ou nota"></label><label>Mês <input type="month" id="ledgerMonth"></label><label>Ordem <select id="ledgerSort"><option value="desc">Mais recente primeiro</option><option value="asc">Mais antigo primeiro</option></select></label><span id="ledgerCount" aria-live="polite"></span>';
  card.querySelector('.jp-table-scroll').before(tools);
  [['ledgerFilter','filter'],['ledgerMonth','month'],['ledgerSort','sort']].forEach(([id,key])=>{
    $(id).addEventListener('input',e=>{ledgerUI[key]=e.target.value;renderLedger();});
  });
  const editor=document.createElement('div');editor.id='ledgerInlineEditor';editor.className='ledger-inline-editor';editor.hidden=true;tools.after(editor);
  const legacy=document.createElement('details');legacy.id='legacyLedgerPanel';legacy.className='jp-p3';
  legacy.innerHTML='<summary>Legado e vínculos comprovados</summary><p>Registros anteriores permanecem fora dos totais atuais. Conta, período e moeda completos permitem apenas um vínculo de referência; divergências continuam não conciliadas.</p><pre id="legacyLedgerPreview"></pre><button type="button" id="legacyLedgerSnapshotBtn">Confirmar snapshot do legado</button><p id="legacyLedgerStatus" role="status"></p>';
  editor.after(legacy);
  $('legacyLedgerSnapshotBtn').onclick=()=>{
    const preview=window.JPWForex.state.legacyAccountPreview();
    if(preview.existing){$('legacyLedgerStatus').textContent='Snapshot já registrado.';return;}
    if(!confirm('Preservar o snapshot legado e seus vínculos de referência comprovados? Os registros não entrarão nos totais das contas.'))return;
    const reason=prompt('Motivo da preservação explícita do legado:');if(reason===null)return;
    const result=window.JPWForex.state.confirmLegacyAccountSnapshot({reason,expectedEpoch:jpWealthPersistenceEpoch()});
    $('legacyLedgerStatus').textContent=result.ok?'Snapshot preservado; vínculos comprovados são somente referência.':result.error;
  };
}
function ledgerBeginEdit(id){
  const row=ledgerFind(id);if(!row)return;
  ledgerUI.edit={id,version:row.version||0};ledgerUI.draft={...row};
  const el=$('ledgerInlineEditor');el.hidden=false;
  el.innerHTML=`<h3>Corrigir fechamento de ${esc(row.data)} · ${esc(row.currency)}</h3><div class="params-grid">${[['data','Data','date'],['resultado','Resultado '+row.currency,'number'],['saldo','Saldo '+row.currency,'number'],['nota','Nota','text']].map(([key,label,type])=>`<label>${label}<input data-ledger-edit="${key}" type="${type}" ${type==='number'?'step="0.01"':''} value="${esc(String(row[key]??''))}"></label>`).join('')}<label>Motivo da correção<input id="ledgerEditReason" type="text"></label></div><p>Conta ${esc(row.accountId)} · período ${esc(row.periodId)}. Linhas derivadas posteriores serão revisadas; saldos observados não serão sobrescritos.</p><button type="button" id="ledgerEditSave">Salvar correção</button><button type="button" id="ledgerEditCancel">Cancelar</button><p id="ledgerEditStatus" role="status"></p>`;
  el.querySelectorAll('[data-ledger-edit]').forEach(input=>input.addEventListener('input',()=>{ledgerUI.draft[input.dataset.ledgerEdit]=input.value;}));
  $('ledgerEditCancel').onclick=()=>{el.hidden=true;ledgerUI.edit=null;ledgerUI.draft=null;document.querySelector('[data-ledger-row="'+CSS.escape(id)+'"] [data-ledger-field]')?.focus();};
  $('ledgerEditSave').onclick=()=>{
    const res=ledgerCorrect(id,ledgerUI.draft,{reason:$('ledgerEditReason').value,expectedVersion:ledgerUI.edit.version,
      allowBackdate:true,context:{accountId:row.accountId,periodId:row.periodId}});
    if(!res.ok){$('ledgerEditStatus').textContent=res.error;return;}
    el.hidden=true;ledgerUI.edit=null;ledgerUI.draft=null;ledgerFeedback('✓ correção registrada',true);ledgerRefreshConsumers();
  };
  el.onkeydown=e=>{if(e.key==='Escape'){e.preventDefault();$('ledgerEditCancel').click();}if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();$('ledgerEditSave').click();}};
  el.querySelector('input').focus();
}
function renderLedger(){
  const dEl=$('ldDate');if(dEl&&!dEl.value)dEl.value=todayISO();
  const tb=$('ledgerBody');if(!tb)return;ledgerMountTools(tb);
  const preview=window.JPWForex?.state?.legacyAccountPreview?.();
  if($('legacyLedgerPreview'))$('legacyLedgerPreview').textContent=preview?JSON.stringify({
    operationScope:preview.operationScope,orderScopes:preview.orderScopes,ledgerScopes:preview.ledgerScopes,
    ledgerCount:preview.source.ledger?.length||0,legacyOperation:!!preview.source.operation,
    associations:preview.associations,
    preserved:preview.existing,warning:preview.warning},null,2):'Legado indisponível.';
  const rows=ledgerRows().filter(r=>(!ledgerUI.month||r.data.startsWith(ledgerUI.month))&&(!ledgerUI.filter||(r.data+' '+(r.nota||'')).toLowerCase().includes(ledgerUI.filter.toLowerCase()))).sort((a,b)=>ledgerUI.sort==='asc'?a.data.localeCompare(b.data):b.data.localeCompare(a.data));
  const selected=rows.find(r=>r.id===ledgerUI.selected)||rows[0];
  if(selected)ledgerUI.selected=selected.id;
  tb.innerHTML=rows.map(r=>{
    const ref=ledgerFinite(r.referenceBalance)?r.referenceBalance:null;
    const dd=ref>0?Math.max(0,(ref-r.saldo)/ref):null;
    const cell=(key,text)=>`<td data-ledger-field="${key}" tabindex="${r.id===ledgerUI.selected&&key==='data'?'0':'-1'}">${text}</td>`;
    return `<tr data-ledger-row="${esc(r.id)}" aria-selected="${r.id===ledgerUI.selected}">${cell('data',esc(r.data))}${cell('resultado',fmtForexMoney(r.resultado,{currency:r.currency}))}${cell('saldo',fmtForexMoney(r.saldo,{currency:r.currency}))}<td>${dd==null?'—':fmtPct(dd)}<span class="sr-only"> derivado</span></td>${cell('nota',esc(r.nota||''))}<td><button type="button" data-ledger-correct="${esc(r.id)}">Corrigir</button><button type="button" class="row-del" data-ledger-void="${esc(r.id)}" title="Anular lançamento preservando auditoria">✕</button><small>v${r.version}</small></td></tr>`;
  }).join('');
  if($('ledgerCount'))$('ledgerCount').textContent=rows.length+' de '+ledgerRows().length+' lançamentos desta conta/período';
  tb.querySelectorAll('[data-ledger-correct]').forEach(b=>b.onclick=()=>ledgerBeginEdit(b.dataset.ledgerCorrect));
  tb.querySelectorAll('[data-ledger-void]').forEach(b=>b.onclick=()=>{
    const row=ledgerFind(b.dataset.ledgerVoid);if(!row)return;
    if(!confirm('Anular o lançamento de '+row.data+'? A auditoria preservará o original.'))return;
    const reason=prompt('Motivo da anulação:');if(reason===null)return;
    const res=ledgerVoid(b.dataset.ledgerVoid,{reason,expectedVersion:row.version||0});
    if(!res.ok){ledgerFeedback('✗ '+res.error,false);return;}ledgerFeedback('✓ fechamento anulado',true);ledgerRefreshConsumers();
  });
  tb.querySelectorAll('[data-ledger-field]').forEach(cell=>{
    const select=()=>{tb.querySelectorAll('[data-ledger-field]').forEach(c=>c.tabIndex=-1);cell.tabIndex=0;ledgerUI.selected=cell.closest('tr').dataset.ledgerRow;tb.querySelectorAll('tr').forEach(r=>r.setAttribute('aria-selected',String(r.dataset.ledgerRow===ledgerUI.selected)));};
    cell.onclick=()=>{select();cell.focus();};cell.ondblclick=()=>ledgerBeginEdit(cell.closest('tr').dataset.ledgerRow);
    cell.onkeydown=e=>{
      if(e.key==='Enter'||e.key==='F2'){e.preventDefault();ledgerBeginEdit(cell.closest('tr').dataset.ledgerRow);return;}
      const cells=[...tb.querySelectorAll('[data-ledger-field]')],i=cells.indexOf(cell),delta={ArrowLeft:-1,ArrowRight:1,ArrowUp:-4,ArrowDown:4}[e.key];
      if(delta!==undefined){e.preventDefault();const next=cells[Math.max(0,Math.min(cells.length-1,i+delta))];next.click();}
    };
  });
  renderAcct();renderAuditLog();
}
window.JPWLedger={rows:ledgerRows,record:ledgerRecord,correct:ledgerCorrect,void:ledgerVoid,monthlyActual:ledgerMonthlyActual,render:renderLedger};
function renderAuditLog(){
  const box=$('auditLogBox'); if(!box) return;
  const scope=ledgerOperationalScope(),ctx=window.JPWForex?.state?.accountContext?.(scope);
  const events=ctx?.status==='OK'&&Array.isArray(ctx.value.ledgerEvents)?ctx.value.ledgerEvents:[];
  box.innerHTML=events.length?events.slice().reverse().map(e=>`<div>· <b>${esc(e.action)} · ${esc(e.at)}</b> ${esc(e.reason)}<details><summary>Antes / depois</summary><pre>${esc(JSON.stringify({before:e.before,after:e.after},null,2))}</pre></details></div>`).join(''):'<span class="muted">Nenhum evento desta conta/período.</span>';
}
function exportAudit(){
  const contasSemSegredo=S.accounts.map(a=>({...a, investorPassword: a.investorPassword?'••• (removida da exportação)':''}));
  const payload={
    exportadoEm:new Date().toISOString(), versao:'V9.1',
    params:S.params, cycleRealizado:S.cycleRealizado, quarantine:S.quarantine,
    protocolBreaches:S.protocolBreaches, transitionLog:S.transitionLog,
    accountContext:window.JPWForex?.state?.accountContext?.(ledgerOperationalScope())?.value||null,
    legacyUnreconciled:{ledger:S.ledger,ledgerHistory:S.ledgerHistory||null,phases:S.phases}, contas:contasSemSegredo,
  };
  const blob=new Blob([JSON.stringify(payload,(k,v)=>k==='investorPassword'?'':v,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='jpwealth_auditoria_'+todayISO()+'.json';
  a.click();
  URL.revokeObjectURL(a.href);
}
// ---- Exportação da base (JPW-HJFGDE) ---------------------------------------------
// POLÍTICA DE SEGREDO: o backup NUNCA carrega senha de investidor — a antiga pergunta
// "incluir senhas?" foi removida junto com a opção que ela oferecia. O envelope mantém
// o campo segredosIncluidos (formato normativo) sempre em false.
// Monta o arquivo do backup completo. O ENVELOPE é formato normativo e não muda aqui:
// {tipo, versao, localStorageKey, exportadoEm, dataLocal, segredosIncluidos, state}.
//
// AUTOIDENTIFICAÇÃO (FAIL-04): o snapshot gravado declara a PRÓPRIA exportação. Antes,
// o payload era uma fotografia do estado ANTERIOR ao incremento — o arquivo 000010
// carregava por dentro lastSequence=9, e restaurá-lo fazia a base reemitir o 000010.
// A colisão física só mascarava isso quando o arquivo original estivesse na mesma pasta;
// em máquina nova, pasta vazia ou no fallback Downloads não há sondagem, e o número
// saía duplicado. A sondagem é defesa adicional, nunca o mecanismo de continuidade.
//
// A identidade é escrita numa CÓPIA (structuredClone), nunca no objeto vivo: se a
// gravação falhar, não há o que reverter — o estado em memória jamais foi tocado.
// `estadoFonte` (opcional) — ALD-C3-PRE-PERSISTENCE: o backup oferecido como rede de
// segurança de um ato destrutivo deve representar o DOCUMENTO AUTORITATIVO persistido,
// não o S potencialmente obsoleto desta aba. O fluxo Finalizar Sessão passa o documento
// lido do disco na abertura; todos os outros usos mantêm o comportamento de sempre (S).
// Mapa descritivo do contrato local. O documento inteiro continua sendo exportado;
// a lista não limita módulos futuros nem transporta preferências/capacidades locais.
function dgBackupCoverage(state){
  return {
    storage:'localStorage', key:LSKEY,
    sections:Object.keys(state).sort(),
    includedWorkspace:['perfil e foto','preferências visuais','navegação e widgets','Notas e Laboratório','rascunhos para revisão'],
    excluded:['investorPassword','caches públicos',
      'permissão/handle da pasta','controles de sessão entre abas','cópias brutas de recuperação',
      'simulação em execução e arquivos originais de importação'],
  };
}
function dgBuildBackupBlob(seq, filename, exportadoEm, estadoFonte){
  const stateExport=structuredClone(estadoFonte||S);
  // Incondicional (política de segredo): não existe mais variante de backup com senha.
  if(Array.isArray(stateExport.accounts)) stateExport.accounts.forEach(a=>{ a.investorPassword=''; });
  if(stateExport.onboarding) stateExport.onboarding.investorPassword='';
  if(stateExport.dataGovernance && stateExport.dataGovernance.export){
    stateExport.dataGovernance.export.lastSequence=seq;
    stateExport.dataGovernance.export.lastExportFile=filename;
    stateExport.dataGovernance.export.lastExportAt=exportadoEm;
  }
  const payload={
    tipo:'jpwealth_full_backup',
    versao:'V9.1',
    localStorageKey:LSKEY,
    exportadoEm,
    dataLocal:todayISO(),
    segredosIncluidos:false, // política de segredo: sempre sem senha
    build:typeof JP_WEALTH_BUILD_ID==='string'?JP_WEALTH_BUILD_ID:null,
    cobertura:dgBackupCoverage(stateExport),
    state:stateExport,
    workspace:jpwWorkspaceCapture({recoverAvailability:true}),
  };
  const blob=new Blob([JSON.stringify(payload,(key,value)=>key==='investorPassword'?'':value,2)],{type:'application/json'});
  blob.workspaceFingerprint=JSON.stringify(payload.workspace);
  return blob;
}
// Download tradicional (fallback §15 e escolha excepcional §7). Padrão endurecido:
// âncora no DOM e revogação adiada — revogar de forma síncrona após click() corta o
// download em alguns navegadores.
function dgDownloadViaAnchor(filename,blob){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(()=>{ URL.revokeObjectURL(a.href); if(a.parentNode) a.remove(); },0);
}
// Sucesso confirmado → e SÓ então o estado avança (§8.2): sequência, carimbo, arquivo,
// changeLog e gravação. Uma exportação que falhou não deixa rastro de sucesso.
function dgRegisterExportSuccess(seq,filename,exportadoEm,destino){
  return dgCommitGovernance('export',()=>{
    S.dataGovernance.export.lastSequence=seq;
    S.dataGovernance.export.lastExportAt=exportadoEm;
    S.dataGovernance.export.lastExportFile=filename;
    dgLogChange('database','exported',filename,
      destino==='folder'?'Base exportada para a pasta padrão':'Download da base iniciado pelo navegador');
  });
}
// UI e registro local são posteriores à entrega: falhar aqui não desfaz o arquivo.
function dgFinishExport(meta,quiet){
  let registered=false;
  try{ registered=dgRegisterExportSuccess(meta.sequence,meta.filename,meta.exportedAt,meta.destination==='folder'?'folder':'downloads'); }
  catch(e){}
  meta.localRecordConfirmed=registered===true;
  const delivery=meta.destination==='folder'?'Arquivo gravado na pasta de exportação':'Download iniciado — confira se o navegador salvou o arquivo';
  const warning=registered?'':'\n\nO registro local desta exportação não foi confirmado. Preserve o arquivo e verifique o armazenamento antes de tentar novamente.';
  if(!quiet || !registered) alert(delivery+':\n\n'+meta.filename+warning);
  // Renderizadores async também podem rejeitar; nunca viram erro de entrega.
  try{ if(typeof renderDgStorageCard==='function') Promise.resolve(renderDgStorageCard()).catch(()=>{}); }catch(e){}
  return jpWealthPersistenceOutcomeIsUnknown()?null:meta;
}
// Exportação completa da base — agora async e orquestrada (JPW-HJFGDE §14).
// Retorna meta {filename, exportedAt, segredosIncluidos, destination} em sucesso;
// null quando não há confirmação segura para continuar (cancelamento/falha/UNKNOWN).
// NUNCA lança e NUNCA faz fallback silencioso para Downloads (§7): se a pasta
// configurada está inacessível, o operador decide — reautorizar, trocar de pasta ou
// exportar excepcionalmente para Downloads, por escolha explícita.
// opts.quiet: suprime o alert de sucesso (o fluxo chamador mostra a própria confirmação).
// GUARDA DE REENTRÂNCIA (caça a bugs 2026-08-08): duas execuções simultâneas (duplo
// clique) liam a MESMA lastSequence antes de qualquer registro e, no caminho pasta —
// onde há awaits reais entre a sondagem de colisão e a gravação —, produziam o mesmo
// nome de arquivo: a segunda gravação sobrescrevia a primeira, violando o §8.3.
// Serializar por recusa é a correção honesta: a segunda tentativa não exporta nada,
// diz o porquê, e nenhum estado é tocado.
let dgExportEmAndamento=false;
async function exportFullBackup(opts){
  const quiet=!!(opts&&opts.quiet);
  const estadoFonte=(opts&&opts.estadoFonte)||null;
  if(dgExportEmAndamento){
    alert('Já existe uma exportação da base em andamento — aguarde ela terminar antes de iniciar outra.');
    return null;
  }
  dgExportEmAndamento=true;
  try{
    return await dgExportFullBackupInner(quiet,estadoFonte);
  }finally{
    dgExportEmAndamento=false;
  }
}
async function dgExportFullBackupInner(quiet,estadoFonte){
  try{
    // A pergunta sobre segredos vem primeiro e vale para toda a operação; o ARQUIVO só
    // é montado quando sequência e nome forem definitivos (autoidentificação, FAIL-04).
    const segredosIncluidos=false; // política de segredo: sem pergunta, sem variante com senha
    const exportadoEm=new Date().toISOString();
    const baseSeq=(S.dataGovernance&&S.dataGovernance.export&&S.dataGovernance.export.lastSequence)||0;
    const supported=typeof dgFsSupported==='function' && dgFsSupported();
    const configured=!!(S.dataGovernance&&S.dataGovernance.storage&&S.dataGovernance.storage.configured);
    // Caminho tradicional: navegador sem suporte, ou pasta nunca configurada. Não é o
    // fallback do §7 (não há pasta prometida sendo ignorada) — é o único caminho que
    // existe, com a nomenclatura progressiva preservada. O navegador ainda pode sufixar
    // " (1)" em colisão dentro de Downloads; nunca sobrescreve (comportamento nativo).
    if(!supported || !configured){
      const seq=baseSeq+1;
      const filename=dgExportFileName(seq,new Date());
      const blob=dgBuildBackupBlob(seq,filename,exportadoEm,estadoFonte);
      dgDownloadViaAnchor(filename,blob);
      return dgFinishExport({filename,sequence:seq,exportedAt:exportadoEm,segredosIncluidos,destination:'downloads',workspaceFingerprint:blob.workspaceFingerprint},quiet);
    }
    // Pasta configurada: resolver acesso. Enquanto o operador não resolver (ou optar por
    // Downloads explicitamente), NENHUM arquivo é gerado.
    let {state,handle}=await dgFsStatus();
    for(;;){
      if(state==='authorized'){
        // nome progressivo com proteção física de colisão (§8.3): nunca sobrescrever;
        // em colisão a sequência avança até nome livre (teto de 1000 é rede de segurança)
        let seq=baseSeq+1, filename=dgExportFileName(seq,new Date());
        let writeAttempted=false,workspaceFingerprint=null;
        try{
          let guard=0;
          while(await dgFsFileExists(handle,filename)){
            seq++; filename=dgExportFileName(seq,new Date());
            if(++guard>1000) throw new Error('Não foi possível encontrar um nome de arquivo livre na pasta.');
          }
          // nome definitivo (pós-colisão) → só AGORA o arquivo é montado, já se
          // autoidentificando com esta sequência e este nome
          const blob=dgBuildBackupBlob(seq,filename,exportadoEm,estadoFonte);
          workspaceFingerprint=blob.workspaceFingerprint;
          writeAttempted=true;
          await dgFsWriteFile(handle,filename,blob);
        }catch(e){
          if(writeAttempted){
            alert('Não foi possível confirmar a conclusão do arquivo '+filename+'. O resultado da escrita é desconhecido. Confira a pasta antes de uma nova tentativa; nenhum download alternativo foi iniciado.');
            return null;
          }
          state='invalid';
          continue;
        }
        return dgFinishExport({filename,sequence:seq,exportedAt:exportadoEm,segredosIncluidos,destination:'folder',workspaceFingerprint},quiet);
      }
      // prompt | denied | missing | invalid → decisão explícita do operador (§7).
      // O diálogo vive em 40-app/16-storage-governance.js; sem ele (geometria degenerada
      // de carregamento) não há como decidir — e decidir por Downloads em silêncio é
      // exatamente o que o ticket proíbe.
      if(typeof dgExportRecoveryDialog!=='function'){
        alert('Não foi possível acessar a pasta padrão da base de dados.\n\nNenhum arquivo foi exportado. Abra Configurações → Dados e Segurança → Backup e Recuperação para reautorizar ou trocar a pasta.');
        return null;
      }
      const decision=await dgExportRecoveryDialog(state);
      if(decision==='downloads'){
        const seq=baseSeq+1;
        const filename=dgExportFileName(seq,new Date());
        const blob=dgBuildBackupBlob(seq,filename,exportadoEm,estadoFonte);
      dgDownloadViaAnchor(filename,blob);
        return dgFinishExport({filename,sequence:seq,exportedAt:exportadoEm,segredosIncluidos,destination:'downloads-exception',workspaceFingerprint:blob.workspaceFingerprint},quiet);
      }
      if(decision==='retry'){ ({state,handle}=await dgFsStatus()); continue; }
      return null; // cancelado — nada foi exportado e nada mudou
    }
  }catch(e){
    alert('A exportação não foi concluída: '+(e&&e.message?e.message:'erro inesperado.')+'\n\nVerifique o destino e os avisos antes de repetir. Antes de fechar a página, anote manualmente os registros mais recentes (ordens, fechamentos e notas).');
    return null;
  }
}
function normalizeImportedState(raw){
  if(!raw || typeof raw!=='object' || Array.isArray(raw)) throw new Error('JSON inválido: raiz precisa ser um objeto.');
  const envelope=Object.prototype.hasOwnProperty.call(raw,'state') || Object.prototype.hasOwnProperty.call(raw,'tipo');
  if(envelope){
    if(raw.tipo!==undefined && raw.tipo!=='jpwealth_full_backup') throw new Error('Formato de backup não reconhecido.');
    if(raw.versao!==undefined && raw.versao!=='V9.1') throw new Error('Versão de backup não suportada.');
    if(raw.localStorageKey!==undefined && raw.localStorageKey!==LSKEY) throw new Error('Backup de outra base de dados.');
  }
  const candidate=envelope?raw.state:raw;
  if(!candidate || typeof candidate!=='object' || Array.isArray(candidate)) throw new Error('Backup sem objeto de estado.');
  if(!candidate.params || typeof candidate.params!=='object' || Array.isArray(candidate.params)) throw new Error('Backup com params inválido.');
  if(candidate.ledger && !Array.isArray(candidate.ledger)) throw new Error('Backup com ledger inválido.');
  if(candidate.ledgerArchive && !Array.isArray(candidate.ledgerArchive)) throw new Error('Backup com ledgerArchive inválido.');
  if(candidate.phases && !Array.isArray(candidate.phases)) throw new Error('Backup com phases inválido.');
  // Agregados que os renderizadores percorrem com .map/.forEach SEM guarda de
  // forma em migrate(). Sem esta recusa, um backup com `checklist:{}` atravessava
  // validação e migração inteiras sem lançar, e a exceção só estourava em boot() —
  // DEPOIS de S=imported e da gravação no localStorage. A ordem era fatal: quando
  // o erro aparecia a base original já não existia, e como migrate() não lançara,
  // o modo de recuperação A-005 não entrava (sem cópia _corrompido_, sem bloqueio
  // de gravação, sem faixa de aviso) — o operador ficava com a tela em branco.
  // Recusar ANTES de tocar em qualquer coisa é o mesmo contrato transacional que
  // as quatro linhas acima já expressavam.
  for(const chave of ['checklist','accounts','instruments','profiles','ledgerArchive','transitionLog']){
    if(chave in candidate && candidate[chave]!=null && !Array.isArray(candidate[chave]))
      throw new Error('Backup com '+chave+' inválido: esperava lista.');
  }
  // `alladin` e CONTEINER (objeto), nao lista — e era a unica chave cujo formato
  // nao era recusado na porta. Um array, um escalar ou um null EXPLICITO
  // atravessavam a validacao inteira e so eram normalizados depois, trocando o
  // agregado patrimonial pelo default: perda silenciosa do cadastro, e amanha da
  // historia economica. Chave AUSENTE continua legitima (backup legado, anterior
  // ao agregado); presente e invalida recusa ANTES de tocar em coisa alguma, que
  // e o mesmo contrato transacional das linhas acima. `typeof null` e 'object',
  // por isso o null e testado a parte (ALD-03-H0 · D-2).
  for(const key of ['alladin','personalFinance','fxPlanning','nocoda','pivotStudies','mvpNotes','dataGovernance','fxConsolidated','operationHistory']){
    if(Object.prototype.hasOwnProperty.call(candidate,key) &&
       (candidate[key]===null || typeof candidate[key]!=='object' || Array.isArray(candidate[key])))
      throw new Error('Backup com '+key+' inválido: esperava objeto.');
  }
  if(candidate.forex!=null&&globalThis.JPWForex?.state&&!JPWForex.state.supported(candidate.forex))throw new Error('Backup com observações Forex incompatíveis. O estado atual foi preservado.');
  if(globalThis.JPWForex?.state?.validateExecutionExtensions&&!JPWForex.state.validateExecutionExtensions(candidate))throw new Error('Backup com identidade ou diagnóstico de ordem incompatível. O estado atual foi preservado.');
  const workspace=Object.prototype.hasOwnProperty.call(raw,'workspace')?jpwWorkspaceValidate(raw.workspace):null;
  if(candidate.workspaceRecovery!=null){
    const recovery=candidate.workspaceRecovery;
    if(!jpwWorkspaceObject(recovery)||recovery.schemaVersion!==1||typeof recovery.pending!=='boolean')throw new Error('Registro de retomada inválido.');
    jpwWorkspaceValidate(recovery.pending?recovery.snapshot:{schemaVersion:1,preferences:{},drafts:recovery.drafts});
  }
  const current=S;
  let imported;
  try{
    S=structuredClone(candidate);
    migrate();
    // A restauração não recalcula um saldo global a partir da conta que a UI
    // estava mostrando. A identidade histórica do backup permanece intacta.
    imported=structuredClone(S);
    if(workspace)imported.workspaceRecovery={schemaVersion:1,pending:true,snapshot:workspace};
  }finally{
    S=current;
  }
  return imported;
}
function importFullBackupFile(file){
  if(!file) return;
  // TRANSACIONAL: nenhum portão muda antes de o candidato estar lido, validado,
  // normalizado E confirmado. A versão anterior chamava resumeJPWealthPersistence()
  // já na entrada — antes do FileReader — e um arquivo inválido deixava o portão
  // genérico reaberto mesmo com o modo de recuperação ainda ativo. O epoch capturado
  // aqui congela a legitimidade do pedido: se o operador resolver a recuperação (ou
  // outro fluxo mexer nos portões) entre escolher o arquivo e a leitura terminar,
  // este import deixa de representar uma decisão sobre o estado vigente e é abortado.
  const requestEpoch=jpWealthPersistenceEpoch();
  const reader=new FileReader();
  reader.onload=()=>{
    if(requestEpoch!==jpWealthPersistenceEpoch()) return;
    let imported;
    try{
      imported=normalizeImportedState(JSON.parse(String(reader.result||'')));
    }catch(e){
      // Falha ANTES da aplicação: estado, portões e modo de recuperação intactos.
      alert('Backup inválido: '+(e&&e.message?e.message:'não foi possível ler o JSON.')+'\n\nNada foi alterado: o estado atual e as proteções de gravação permanecem exatamente como estavam.');
      return;
    }
    const availabilityKey=window.JPWModuleAvailability.KEY;
    const availabilityPreferences=imported.workspaceRecovery?.snapshot?.preferences;
    const changesAvailability=!!availabilityPreferences&&Object.prototype.hasOwnProperty.call(availabilityPreferences,availabilityKey);
    let availabilityBefore,availabilityMessage='';
    if(changesAvailability){
      try{availabilityBefore=localStorage.getItem(availabilityKey);}
      catch(error){alert('Não foi possível conferir a disponibilidade atual. Nada foi importado.');return;}
      const previousAvailability=window.JPWModuleAvailability.inspect(availabilityBefore);
      const nextAvailability=window.JPWModuleAvailability.inspect(availabilityPreferences[availabilityKey]);
      const names={research:'Research',forex:'Forex','personal-finance':'Finanças Pessoais',alladin:'Alladin'};
      const label=value=>value==='frozen'?'Congelado':'Ativo';
      const changes=Object.keys(names).filter(id=>!previousAvailability.valid||previousAvailability.states[id]!==nextAvailability.states[id]);
      availabilityMessage=changes.length?'\n\nDisponibilidade após restaurar:\n'+changes.map(id=>names[id]+': '+(previousAvailability.valid?label(previousAvailability.states[id]):'configuração incompatível')+' → '+label(nextAvailability.states[id])).join('\n')+'\nIsso pode descongelar acessos. Não autoriza desenvolvimento.':'';
    }
    if(!confirm('Importar backup completo e sobrescrever o estado atual deste navegador?'+availabilityMessage)) return;
    if(requestEpoch!==jpWealthPersistenceEpoch()) return;
    // ALD-C3-PRE-PERSISTENCE: a substituição da base inteira roda dentro do writer
    // lock cross-tab (mesma serialização da finalização e do wipe). O corpo nunca
    // rejeita: falhas viram alert e a Promise resolve — nenhum fire-and-forget
    // destrutivo. Em modo degraded (sem Web Locks) roda direto, best-effort (DP-3).
    const aplicar=async ()=>{
    if(requestEpoch!==jpWealthPersistenceEpoch()) return;
    if(jpWealthPersistenceOutcomeIsUnknown()){
      alert('A importação não pode substituir uma base com desfecho de gravação desconhecido. Verifique a recuperação antes de continuar.');
      return;
    }
    if(changesAvailability){
      try{if(localStorage.getItem(availabilityKey)!==availabilityBefore){alert('A disponibilidade mudou desde a confirmação. Nada foi importado; selecione o backup novamente para revisar os efeitos.');return;}}
      catch(error){alert('Disponibilidade não confirmável. Nada foi importado.');return;}
    }
    const previous=S, wasBlocked=jpWealthPersistenceIsBlocked();
    const previousRecovery={...jpWealthLoadRecovery};
    const restoreRefusedImport=()=>{
      S=previous;
      Object.assign(jpWealthLoadRecovery,previousRecovery);
      if(wasBlocked) blockJPWealthPersistence();
      if(previousRecovery.active) renderLoadRecoveryWarning();
    };
    let before;
    try{ before=localStorage.getItem(LSKEY); }
    catch(e){ alert('Não foi possível ler a base atual. O backup não foi aplicado.'); return; }
    // ALD-C3-PRE-EPOCH: o backup já foi lido e validado integralmente acima. A nova
    // geração é firmada AQUI, antes de a base ser substituída — nunca depois, porque
    // uma base nova sob geração antiga deixaria uma finalização pendente atuar sobre
    // ela. Falhando a rotação, a importação é abortada e a base atual fica intacta.
    const novaEpoch=(typeof sessionEpochRotate==='function')?sessionEpochRotate():null;
    if(!novaEpoch){
      alert('Não foi possível estabelecer uma nova geração da base neste navegador. O backup NÃO foi aplicado — recarregue a página e tente novamente.');
      return;
    }
    // Só a partir daqui a operação se aplica — candidato validado e confirmado.
    S=imported;
    // Auditoria resumida (JPW-HJFGDE §11): a importação entra no changeLog DA BASE
    // IMPORTADA — é nela que o evento aconteceu e é ela que o próximo backup protege.
    if(typeof dgLogChange==='function') dgLogChange('database','imported',file.name||'','Importação de backup realizada');
    // Integração A-005: uma importação VALIDADA é decisão legítima de sair do modo de
    // recuperação — o portão genérico só reabre AGORA, com candidato aplicado, e o
    // desbloqueio do recovery só se consolida após gravação comprovada; se a escrita
    // falhar, jpWealthResolveRecoveryAndSave() restaura a flag de recuperação e a
    // chave principal fica intacta.
    if(jpWealthPersistenceIsBlocked()) resumeJPWealthPersistence();
    let gravou=false;
    try{
      const expected=JSON.stringify(S,(k,v)=>k==='investorPassword'?'':v);
      let result;
      jpwWorkspaceRestoring=true;
      try{result=(typeof jpWealthResolveRecoveryAndSave==='function')?jpWealthResolveRecoveryAndSave():save();}
      finally{jpwWorkspaceRestoring=false;}
      if(result===false && !jpWealthPersistenceOutcomeIsUnknown()){
        restoreRefusedImport();
      }else{
        const actual=localStorage.getItem(LSKEY);
        if(result===true && actual===expected) gravou=true;
        else if(actual===before && !jpWealthPersistenceOutcomeIsUnknown()){
          restoreRefusedImport();
          jpWealthAdoptPersistedRaw(before);
          hideStaleSavedTag(); setPersistenceFailureState(new Error('Importação não gravada.'),'storage');
        }else{
          hideStaleSavedTag(); markJPWealthPersistenceOutcomeUnknown('Importação com leitura de volta divergente.');
        }
      }
    }catch(e){
      hideStaleSavedTag(); markJPWealthPersistenceOutcomeUnknown('Não foi possível determinar o resultado da importação.');
    }
    const workspaceComplete=gravou?jpwWorkspaceResume():false;
    // A base foi SUBSTITUÍDA — atravessa as abas pelo mesmo canal da Zona de
    // Perigo e da Finalização. Sem isto, outra aba mantinha o S anterior em
    // memória e a primeira gravação dela ressuscitava o documento antigo por
    // cima do backup recém-restaurado, sem aviso nenhum nas duas telas. Só
    // difunde depois da gravação comprovada: avisar sobre uma base que não
    // chegou ao disco faria as outras abas recarregarem o estado errado.
    if(gravou && typeof sessionNotifyBaseImported==='function') sessionNotifyBaseImported(novaEpoch);
    if(gravou && workspaceComplete){jpwWorkspaceAdoptImport();boot();jpwWorkspaceRender();markSessionCheckpoint();}
    alert(gravou?(workspaceComplete?'Backup importado com sucesso. Recarregue para aplicar todas as preferências visuais.':'Base importada; restauração das preferências pendente. Confira o aviso e recarregue para concluir.'):jpWealthPersistenceOutcomeIsUnknown()?'Importação com resultado desconhecido — novas gravações bloqueadas. Preserve o arquivo e verifique a recuperação; não repita às cegas.':'A gravação do backup foi recusada. O estado anterior foi preservado; verifique o armazenamento antes de tentar novamente.');
    };
    if(typeof sessionAcquireWriteLock==='function'){ sessionAcquireWriteLock(aplicar); }
    else{ aplicar(); }
  };
  reader.onerror=()=>alert('Não foi possível ler o arquivo de backup.');
  reader.readAsText(file);
}

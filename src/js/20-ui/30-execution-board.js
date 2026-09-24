// Execution Board: presentation and RAM drafts. Financial projections and all
// writes belong to the existing Forex domain. No draft is part of S or backup.
(function(root){
  'use strict';
  const fx=root.JPWForex;
  const drafts=new Map(), expanded=new Set(), openedPhases=new Set();
  let instrumentChoice=null,tableSignature=null,leaving=false;
  let epoch=jpWealthPersistenceEpoch(),dialog=null,dialogReturn=null,observationDirty=false;
  const num=v=>typeof v==='number'&&Number.isFinite(v);
  const el=id=>document.getElementById(id);
  const key=(pi,oi)=>pi+':'+oi;
  const period=()=>fx.state.accountContext(fx.state.operationalSelection());
  const current=(pi,oi)=>period().value?.phases?.[pi]?.orders?.[oi];
  const draftKey=(pi,oi)=>{const s=fx.state.operationalSelection();
    return [s.accountId||'',s.periodId||'',pi+':'+oi].join('|');};
  const signature=o=>JSON.stringify(o);
  const n=(v,d=2)=>num(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:d}):'Não calculável';
  const label={id:'ID interno',brokerHash:'HASH da corretora',par:'Instrumento',tipo:'Direção',role:'Papel',lote:'Lote',entry:'Entrada',sl:'Stop',tp:'Alvo',status:'Estado',result:'Resultado',costs:'Custos assinados',costBasis:'Tratamento dos custos',stopValidated:'Stop validado',amplifiesExposure:'Pendente amplia exposição',pendingActive:'Pendente ativa'};
  const numericFields=new Set(['lote','entry','sl','tp','result','costs']);
  const calcColumns=[['stopDistance','Dist. SL'],['stopPercent','SL %'],['targetDistance','Dist. TP'],['targetPercent','TP %'],['rewardRisk','Retorno / risco'],['atrMultiple','ATR Multiple'],['rootOne','Raiz-N 1s %'],['rootTwo','Raiz-N 2s %']];
  const tableColumns=['ID interno','HASH corretora','Instrumento','Direção','Papel','Lote','Entrada','Stop Loss','Take Profit',...calcColumns.map(x=>x[1]),'Risco nominal','Risco % saldo','Resultado','Custos','Custos no resultado?','SL validado','Estado','Ações'];
  const columnWidths=[124,160,112,94,108,86,100,100,100,94,84,94,84,88,90,105,105,130,95,120,110,158,86,112,126];
  function syncEpoch(){
    const next=jpWealthPersistenceEpoch();
    if(next!==epoch&&!jpWealthPersistenceOutcomeIsUnknown()){
      drafts.clear();expanded.clear();instrumentChoice=null;tableSignature=null;
      observationDirty=false;if(dialog?.open)dialog.close();
    }
    epoch=next;
  }
  function model(){syncEpoch();return fx.executionBoard.read();}
  function format(m){
    if(!m||!num(m.value))return 'Não calculável';
    if(m.currency)return fmtForexMoney(m.value,{currency:m.currency},2);
    const unit=m.unit||'';
    return n(m.value,/lot|price/i.test(unit)?6:2)+(unit==='%'||/percent/i.test(unit)?'%':/ratio|multiple|leverage|^x$/i.test(unit)?'×':/lots?/i.test(unit)?' lotes':'');
  }
  function reason(m){return m?.reason||m?.findings?.map(x=>x.message||x.code).join(' · ')||'Informação ainda não observada neste contexto.';}
  function provenance(m){
    const s=m?.source, detail=typeof s==='object'&&s?s:m||{};
    const parts=[typeof s==='string'?s:detail.label||detail.source||detail.kind];
    if(detail.referenceDate)parts.push('Referência '+detail.referenceDate);
    if(detail.observedAt)parts.push('Observada '+detail.observedAt);
    else if(detail.recordedAt)parts.push('Registrada '+detail.recordedAt);
    if(detail.fetchedAt)parts.push('Consultada '+detail.fetchedAt);
    return parts.filter(Boolean).join(' · ');
  }
  function metric(title,m,{id='',note='',limit=null}={}){
    const valid=num(m?.value),source=provenance(m),track=valid&&num(limit)&&limit>0;
    return `<div class="eb-metric"${id?` data-eb-metric="${esc(id)}"`:''}><span>${esc(title)}</span><strong>${esc(format(m))}</strong>${num(m?.percent)?`<small>${esc(n(m.percent))}% ${m.percentBasis==='BOOK_BALANCE'?'do saldo atual':'do SI'}</small>`:''}${track?`<meter min="0" max="${limit}" value="${Math.max(0,Math.min(limit,m.value))}" aria-label="${esc(title)}" title="${esc(format(m))} · limite ${esc(String(limit))}"></meter>`:''}<small>${esc(valid?(note||source):reason(m))}</small>${valid&&source&&note?`<small>${esc(source)}</small>`:''}</div>`;
  }
  function updateHTML(id,html){
    const node=el(id);if(!node||node.innerHTML===html)return;
    const active=node.contains(document.activeElement)?document.activeElement:null;
    const focusId=active?.id,details=[...node.querySelectorAll('details')].map(d=>d.open);
    node.innerHTML=html;
    [...node.querySelectorAll('details')].forEach((d,i)=>{if(details[i]!==undefined)d.open=details[i];});
    if(focusId)el(focusId)?.focus({preventScroll:true});
  }
  function prepareShell(){
    const grid=el('execWidgetGrid');if(!grid||el('executionBoard'))return;
    grid.classList.add('execution-board');
    const header=document.createElement('div');header.id='executionBoard';header.className='eb-heading';
    header.innerHTML='<div class="eb-heading-main"><div><p class="eb-eyebrow">FOREX · EXECUTION BOARD</p><h2>Execution Board</h2><p id="ebOperationIdentity"></p></div><div class="eb-heading-controls"><div id="ebChecklistHost"></div></div></div><nav id="ebPhaseNav" aria-label="Ir para a fase da ordem"></nav>';
    header.addEventListener('click',onClick);
    el('exec').prepend(header);
    const checklist=el('execChecklistBtn');if(checklist)el('ebChecklistHost').append(checklist);
    const oldHeading=document.querySelector('#exec .fx-operation-heading');if(oldHeading)oldHeading.hidden=true;
    const regions=[['execClearanceCard','executionBoardAccount'],['execConsolidadoCard','executionBoardRisk'],['execLifoMonitor','executionBoardInstruments']];
    for(const [id,region] of regions){
      const card=el(id);if(!card)continue;
      const legacy=document.createElement('div');legacy.hidden=true;legacy.className='eb-legacy-host';
      while(card.firstChild)legacy.append(card.firstChild);
      card.append(legacy);card.classList.add('eb-card');
      const host=document.createElement('div');host.id=region;card.append(host);
      if(id==='execConsolidadoCard'){
        const actions=legacy.querySelector('.lifo-actions');if(actions){actions.classList.add('eb-actions');card.append(actions);}
      }
    }
    const oldExtra=grid.querySelector('[data-layout-card="exec-metrics-banners"]');
    if(oldExtra){oldExtra.classList.add('eb-legacy-metrics');oldExtra.hidden=true;}
    const phaseCard=el('execPhaseGridsCard');if(phaseCard){phaseCard.classList.add('eb-card');const title=phaseCard.querySelector('h2');if(title)title.textContent='Fases e ordens';}
    grid.addEventListener('click',onClick);
    el('phaseContainer').addEventListener('input',onInput);
    el('phaseContainer').addEventListener('change',onInput);
    el('phaseContainer').addEventListener('toggle',event=>{
      const node=event.target;if(node.matches?.('details[data-phase]')){const pi=+node.dataset.phase;node.open?openedPhases.add(pi):openedPhases.delete(pi);}
      if(node.matches?.('details[data-eb-detail]'))node.open?expanded.add(node.dataset.ebDetail):expanded.delete(node.dataset.ebDetail);
    },true);
  }
  function render(){
    if(!fx.executionBoard||typeof S==='undefined'||!S)return;
    prepareShell();const m=model();
    el('ebOperationIdentity').textContent=m.scope?.operationId?`Operação em andamento · ${m.scope.currency||'moeda não identificada'}`:
      (m.scope?.periodId?'Nova operação neste período.':'Escolha o contexto em Contas e Período.');
    el('ebOperationIdentity').title=[m.scope?.operationId&&'Operação: '+m.scope.operationId,m.scope?.periodId&&'Período: '+m.scope.periodId].filter(Boolean).join(' · ');
    const profile=fx.state.accountProfileContext?.(fx.state.operationalSelection());
    const profileName=profile?.period?.name||'Perfil do período não informado';
    const account=m.accountRecord||m.account||{},capital=m.capital||{},risk=m.risk||{},op=m.operational||{};
    updateHTML('executionBoardAccount',`<div class="eb-section-head"><div><p class="eb-eyebrow">CONTA E PERÍODO</p><h3>${esc(account.name||m.selection?.accountId||'Selecione uma conta')}</h3></div><button type="button" class="reset-btn" data-eb-manage>Gerenciar em Contas e Período</button></div><div class="eb-capital-strip">${metric('Saldo inicial do período',capital.si)}${metric('Saldo atual registrado',capital.book)}${metric('Equity observada',capital.equity)}${metric('Drawdown',capital.drawdown)}</div><p class="eb-context-line">${esc([account.platform,account.login,m.scope?.currency].filter(Boolean).join(' · '))} · Período: ${esc(m.scope?.periodId||'Pendente')} · ${esc(profileName)} · Fase da conta: ${esc(fx.policy.phases[(risk.accountPhase?.value||0)-1]?.name||(risk.accountPhase?.compulsoryClose?'Encerramento compulsório':'Não calculável'))}</p>`);
    updateHTML('executionBoardRisk',`<div class="eb-section-head"><div><p class="eb-eyebrow">RESUMO OPERACIONAL</p><h3>Exposição da conta</h3></div><span class="eb-confirmed">Registros confirmados</span></div><div class="eb-operational-strip">${metric('Hard Stop · Equity Protector',capital.stopoutEquity,{id:'hardStop',note:'Piso de equity: SI × 78% + movimentações conciliadas. Limite de 22%; não aciona a corretora.'})}${metric('Total Exposure · Exposição total',op.exposure,{id:'totalExposure',note:'Risco até o stop das ordens abertas. Percentual sobre o saldo atual registrado.'})}${metric('Compensed Exposure · Compensada',op.compensated,{id:'compensedExposure',note:'Exposição total menos resultado líquido realizado das defesas. Perdas aumentam a exposição.'})}${metric('Alavancagem utilizada',op.leverage,{id:'usedLeverage',note:'Nocional bruto das posições abertas ÷ saldo atual registrado.'})}</div><details class="eb-findings"><summary>Ver bases de cálculo e proteções</summary><p>O resumo usa o saldo contábil registrado deste período. Atualize a Contabilidade quando houver novos lançamentos; saldo e equity são informações diferentes.</p><div class="eb-metrics">${metric('Nocional bruto',op.grossNotional)}${metric('Pendentes ampliadoras',risk.pending)}${metric('Alavancagem normativa',risk.leverage,{note:'Base normativa: menor valor entre saldo inicial e equity.'})}${metric('Risco comprometido',risk.committed)}${metric('Capacidade prudencial',risk.prudentialRemaining)}</div><p>A compensação econômica não amplia os limites normativos. Registrar fatos não autoriza execução.</p><ul>${(m.findings||[]).map(f=>`<li>${esc(f.message||f.reason||f.code||String(f))}</li>`).join('')}</ul><button type="button" class="reset-btn" data-eb-motor>Revisar Fator de Correção e parâmetros</button></details>`);
    renderInstruments(m);
    renderPhases(m);
    const supported=fx.state.supported();
    let notice=el('ebUnsupported');if(!notice){notice=document.createElement('p');notice.id='ebUnsupported';notice.className='eb-row-feedback';el('executionBoard').append(notice);}
    notice.textContent=supported?'':'Versão do agregado Forex incompatível. Apenas leitura; preserve a base.';notice.hidden=supported;
    for(const button of el('execWidgetGrid').querySelectorAll('[data-addorder],[data-eb-save-row],[data-eb-observation],[data-eb-diagnostics],[data-eb-update-quotes],[data-eb-retry-quotes],[data-eb-manage]'))if(!supported)button.disabled=true;
    if(el('exec')?.classList.contains('active')&&typeof renderHeaderReadout==='function')
      renderHeaderReadout(compute());
  }
  function renderInstruments(m){
    const instruments=m.instruments||[];
    if(!instruments.some(x=>x.id===instrumentChoice))instrumentChoice=instruments[0]?.id||null;
    const item=instruments.find(x=>x.id===instrumentChoice)||{};
    const value=x=>esc(num(x?.value)?format(x):'—');
    const diagnostic=x=>value(x)+`<small>${num(x?.n)&&num(x?.f)?'N '+esc(n(x.n))+' · F '+esc(n(x.f)):'Preencher N e F'}</small>`;
    updateHTML('executionBoardInstruments',`<div class="eb-section-head"><div><p class="eb-eyebrow">REFERÊNCIAS POR INSTRUMENTO</p><h3>ATR, VRM e diagnósticos</h3></div><div class="eb-actions"><button type="button" class="reset-btn" data-eb-update-quotes>Atualizar referência diária</button>${fx.marketQuotes?.get()?.canRetry?'<button type="button" class="reset-btn" data-eb-retry-quotes>Repetir gravação da referência</button>':''}<button type="button" class="reset-btn" data-eb-observation>Preencher preço / ATR</button><button type="button" class="reset-btn" data-eb-diagnostics>Preencher N / F</button></div></div><div class="eb-instrument-toolbar"><label>Instrumento<select id="ebInstrumentSelect">${instruments.map(i=>`<option value="${esc(i.id)}" ${i.id===instrumentChoice?'selected':''}>${esc(i.name)}</option>`).join('')}</select></label><p id="ebQuoteStatus" role="status">${esc(fx.marketQuotes?.get()?.message||'Referência diária; não é preço de execução.')}</p></div><div class="eb-table-scroll" role="region" tabindex="0" aria-label="Referências do instrumento"><table class="eb-reference-table"><thead><tr><th>Preço / referência</th><th>ATR55 H4</th><th>ATR660 H4</th><th>VRM</th><th>Raiz-N · 1 semana</th><th>Raiz-N · 2 semanas</th></tr></thead><tbody><tr><td>${value(item.price)}</td><td>${value({value:item.atr?.short,unit:'PRICE'})}</td><td>${value({value:item.atr?.long,unit:'PRICE'})}</td><td>${value(item.vrm)}</td>${['oneWeek','twoWeeks'].map(h=>`<td>${value(item.rootN?.[h])}<small>${num(item.rootN?.[h]?.n)&&num(item.rootN?.[h]?.f)?`N = ${esc(item.rootN[h].n)} · F = ${esc(n(item.rootN[h].f,4))}`:'Preencher N e F'}</small></td>`).join('')}</tr></tbody></table></div><p class="eb-context-line">ATRs em unidades de preço, H4. VRM = ATR55 ÷ ATR660. Raiz-N = ATR55 × √N × F; N em candles H4 e F declarados por horizonte. Diagnóstico em preço; o percentual usa a entrada de cada ordem.</p><details class="eb-findings"><summary>Origem das referências e limites de dimensionamento</summary><p>${esc(provenance(item.price)||'Sem referência de preço identificada.')} · ${esc(item.atr?.source||'ATR não informado')} ${esc(item.atr?.observedAt||'')}</p><div class="eb-metrics">${metric('Stop mínimo normativo',item.minimumStop)}${metric('Lote de referência · normal 0,50×',item.normal)}${metric('Lote de referência · restritivo 0,25×',item.restrictive)}</div><p>Raiz-N é um cenário declarado, não altera P21, o stop executado ou a autorização de lote. Referências de lotes permanecem teóricas.</p>${item.operable===false?'<p>Instrumento com restrição normativa preservada.</p>':''}</details>`);
    const select=el('ebInstrumentSelect');if(select)select.onchange=()=>{instrumentChoice=select.value;renderInstruments(model());};
  }
  function field(pi,oi,o,f,choices){
    const readonly=o.recordStatus==='voided'||!fx.state.supported(),draft=drafts.get(draftKey(pi,oi));
    const value=draft&&Object.prototype.hasOwnProperty.call(draft.values,f)?draft.values[f]:o[f];
    const attrs=`data-p="${pi}" data-o="${oi}" data-f="${f}" aria-label="${esc(label[f])} · ordem ${pi+1}.${oi+1}" aria-describedby="ebError-${pi}-${oi}" ${readonly?'disabled':''}`;
    if(choices)return `<select ${attrs}>${choices.map(([v,t])=>`<option value="${esc(v)}" ${String(value??'')===v?'selected':''}>${esc(t)}</option>`).join('')}</select>`;
    if(['stopValidated','amplifiesExposure','pendingActive'].includes(f))return `<input type="checkbox" ${attrs} ${value===true?'checked':''}>`;
    return `<input ${attrs} type="text" ${numericFields.has(f)?'inputmode="decimal"':''} value="${esc(value??'')}" placeholder="${numericFields.has(f)?'—':f==='brokerHash'?'Referência da corretora':'ID interno'}" autocomplete="off">`;
  }
  function rowHTML(pi,oi,o){
    const k=key(pi,oi),draft=drafts.get(draftKey(pi,oi)),live=operationOrderIsLive(o),readonly=o.recordStatus==='voided'||!fx.state.supported();
    const cell=(f,choices,cls='')=>`<td class="${cls}" data-label="${esc(label[f])}">${field(pi,oi,o,f,choices)}</td>`;
    const instruments=[['','Selecionar'],...(S.instruments||[]).map(i=>[i.name,i.name])];
    if(o.par&&!instruments.some(([x])=>x===o.par))instruments.push([o.par,o.par+' · não cadastrado']);
    return `<tr class="eb-order-row ${draft?'eb-dirty':''}" data-eb-row="${k}"><td class="eb-order-id" data-label="ID interno">${field(pi,oi,o,'id')}<small data-eb-preview="${k}">${draft?'Prévia · não salva':esc(o.recordStatus==='voided'?'Anulada':!fx.state.supported()?'Somente leitura':o.recordStatus==='draft'||!o.status?'Rascunho':'Confirmada')}</small></td>${cell('brokerHash',null,'eb-broker-hash')}${cell('par',instruments)}${cell('tipo',[['BUY','Compra'],['SELL','Venda']])}${cell('role',[['','Não declarado'],['GENESIS','Gênese'],['DEFENSE','Defesa'],['OTHER','Outro']])}${cell('lote')}${cell('entry')}${cell('sl')}${cell('tp')}${calcColumns.map(([f,t])=>`<td class="eb-number eb-calculated" data-label="${t}" data-eb-calc="${f}">—</td>`).join('')}<td class="eb-number eb-calculated" data-label="Risco confirmado" data-eb-row-risk="${k}" data-eb-calc="riskValue">—</td><td class="eb-number eb-calculated" data-label="Risco % saldo" data-eb-calc="riskPercent">—</td>${cell('result')}${cell('costs')}${cell('costBasis',[['','Não declarado'],['SEPARATE_FROM_RESULT','Separados'],['INCLUDED_IN_RESULT','Já incluídos']])}${cell('stopValidated',null,'eb-check-cell')}${cell('status',[['','Rascunho'],['Pendente','Pendente'],['Aberta','Aberta'],['Fechada','Fechada'],...(o.status==='Migrada'?[['Migrada','Migrada']]:[])])}<td class="eb-row-actions" data-label="Ações"><button type="button" data-eb-save-row="${k}" ${readonly?'disabled':''}>Salvar linha</button><button type="button" data-eb-cancel-row="${k}" ${readonly?'disabled':''}>Cancelar</button></td></tr><tr class="eb-detail-row"><td colspan="${tableColumns.length}"><div class="eb-detail-content"><details data-eb-detail="${k}" ${expanded.has(k)||draft?.error?'open':''}><summary>Correção, fechamento e rastreabilidade${draft?' · alterações não salvas':''}</summary><div class="eb-order-details">${['amplifiesExposure','pendingActive'].map(f=>`<label class="eb-check">${field(pi,oi,o,f)}${esc(label[f])}</label>`).join('')}<label class="eb-reason">${live?'Motivo da correção (obrigatório ao salvar)':'Observação do registro (opcional)'}<input type="text" data-eb-reason="${k}" value="${esc(draft?.reason||'')}" ${readonly?'disabled':''}></label></div><p class="eb-context-line">Conta ${esc(o.accountId||'não capturada')} · período ${esc(o.periodId||'não capturado')} · ${esc(o.currency||'moeda não capturada')} · versão ${esc(o.recordVersion??0)} · referência técnica ${esc(o.orderId||'a gerar')}</p><div class="eb-actions">${!readonly?`<button type="button" class="reset-btn" data-eb-close-row="${k}">Fechar ordem</button><button type="button" class="reset-btn" data-delorder="${k}">${live?'Anular com motivo':'Excluir rascunho'}</button>`:''}${o.revisions?.length?`<button type="button" class="reset-btn" data-orderhistory="${k}">Ver ${o.revisions.length} versão(ões)</button>`:''}</div></details><p id="ebError-${pi}-${oi}" class="eb-row-feedback" role="status">${esc(draft?.error||'')}</p></div></td></tr>`;
  }
  function updateRowCalculations(m,pi,oi){
    const row=(m.displayRows||m.rows||[]).find(r=>r.pi===pi&&r.oi===oi),node=el('phaseContainer')?.querySelector(`[data-eb-row="${key(pi,oi)}"]`);
    if(!node)return;
    const draft=drafts.get(draftKey(pi,oi)),o={...current(pi,oi)};
    if(draft)for(const [f,v] of Object.entries(draft.values))o[f]=numericFields.has(f)?String(v).trim()===''?null:orderParseResult(v):v;
    const instrument=m.instruments?.find(i=>i.id===root.instrumentId(o.par));
    const preview=draft&&fx.executionBoard.previewOrder?fx.executionBoard.previewOrder(o,instrument):row;
    const geometry=preview?.geometry||{},risk=row?.operationalRisk;
    const percentage=x=>({value:x?.percent,unit:'PERCENT',reason:reason(x)});
    const cells={...geometry,atrMultiple:preview?.atrMultiple,rootOne:percentage(preview?.rootN?.oneWeek),rootTwo:percentage(preview?.rootN?.twoWeeks),riskValue:risk,riskPercent:percentage(risk)};
    for(const cell of node.querySelectorAll('[data-eb-calc]')){
      const value=cells[cell.dataset.ebCalc];cell.textContent=num(value?.value)?format(value):'—';
      cell.title=num(value?.value)?(draft&&!cell.dataset.ebCalc.startsWith('risk')?'Prévia não salva':'Registro confirmado'):reason(value);
    }
    if(draft){const badge=node.querySelector('[data-eb-preview]');if(badge)badge.textContent='Prévia · não salva';}
  }
  function renderPhases(m){
    if(!fx.executionBoard)return;
    m=m||model();const container=el('phaseContainer');if(!container)return;
    const phaseList=period().value?.phases||[];
    const phaseNames=phaseList.length?phaseList.map((p,pi)=>phaseList.length===4?'LEGACY · '+(p.faseNome||pi+1):fx.policy.phases[pi]?.name||p.faseNome):fx.policy.phases.map(p=>p.name);
    updateHTML('ebPhaseNav','<span>Fases e ordens</span>'+phaseNames.map((name,pi)=>`<button type="button" data-eb-phase-jump="${pi}" aria-controls="ebPhase-${pi}">${esc(name)}</button>`).join(''));
    if(!phaseList.length){
      const emptyKey=JSON.stringify({scope:fx.state.operationalSelection(),supported:fx.state.supported(),empty:true});
      if(tableSignature!==emptyKey){
        container.innerHTML=`<div class="eb-setup-prompt"><h3>Prepare a conta para registrar suas ordens</h3><p>Escolha uma conta e confirme seu período, moeda e capital inicial (SI). Você pode importar um relatório ou preencher os dados manualmente. O saldo do relatório não substitui o SI.</p><button type="button" data-eb-manage>Gerenciar em Contas e Período</button></div>`+phaseNames.map((name,pi)=>`<details class="phase eb-phase" data-phase="${pi}" id="ebPhase-${pi}" ${openedPhases.has(pi)?'open':''}><summary><span>${esc(name)}</span><span>Aguardando contexto</span></summary><div class="phase-body"><p class="eb-context-line">Nesta fase você poderá registrar instrumento, direção, lote, entrada, stop, alvo, estado, custos e resultado. Confirme a conta e o período para começar.</p><button type="button" data-eb-manage>Gerenciar em Contas e Período</button></div></details>`).join('');
        tableSignature=emptyKey;
      }
      return;
    }
    const next=JSON.stringify({scope:fx.state.operationalSelection(),supported:fx.state.supported(),phases:phaseList.map(p=>({name:p.faseNome,policy:p.policyVersion,orders:p.orders}))});
    // Quote/account repaints update numbers only. Live input nodes and cursor stay mounted.
    const firstTable=!container.querySelector('.eb-order-table');
    if(next!==tableSignature||firstTable){
      const focus=document.activeElement,focusKey=focus?.dataset?.f?{p:focus.dataset.p,o:focus.dataset.o,f:focus.dataset.f,start:focus.selectionStart,end:focus.selectionEnd}:null;
      container.innerHTML=`<p class="eb-context-line">${phaseList.length===4?'Grades LEGACY preservadas; os quatro índices não correspondem às seis fases V11.':'Fase de registro da ordem e fase da conta são informações distintas.'} Totais usam somente registros confirmados.</p><details class="eb-table-help"><summary>Como preencher a tabela</summary><p>Use Tab e Shift+Tab entre os campos. Células com fundo de cálculo são somente leitura. Novas ordens executadas exigem ID interno e HASH da corretora; pendentes podem aguardar o HASH. Informe lotes e preços, declare se os custos estão separados ou incluídos e clique em Salvar linha. Custos separados são assinados: despesas negativas, créditos positivos.</p><p>ATR Multiple usa a distância da entrada ao stop. As colunas Raiz-N mostram o percentual da entrada para os cenários N/F declarados. Risco nominal e percentual são confirmados após salvar. Para encerrar uma ordem, use Fechar ordem nos detalhes; correções exigem motivo. Use a rolagem horizontal para acessar todas as colunas.</p></details><div id="ebPhaseSummary" class="eb-table-scroll"></div>`+phaseList.map((p,pi)=>`<details class="phase eb-phase" data-phase="${pi}" id="ebPhase-${pi}" ${openedPhases.has(pi)||(firstTable&&pi===0)?'open':''}><summary><span>${esc(phaseList.length===4?'LEGACY · '+(p.faseNome||pi+1):fx.policy.phases[pi]?.name||p.faseNome)}</span><span>${(p.orders||[]).length} linha(s)</span></summary><div class="phase-body"><div class="eb-table-scroll" tabindex="0" role="region" aria-label="Ordens da fase ${pi+1}"><table class="otable eb-order-table"><colgroup>${columnWidths.map(w=>`<col style="width:${w}px">`).join('')}</colgroup><thead><tr class="eb-column-groups"><th colspan="5" scope="colgroup">Identificação</th><th colspan="4" scope="colgroup">Geometria</th><th colspan="8" scope="colgroup">Cálculos · prévia ao editar</th><th colspan="2" scope="colgroup">Exposição confirmada</th><th colspan="3" scope="colgroup">Resultado</th><th colspan="3" scope="colgroup">Controle</th></tr><tr>${tableColumns.map(t=>'<th scope="col">'+t+'</th>').join('')}</tr></thead><tbody>${(p.orders||[]).map((o,oi)=>rowHTML(pi,oi,o)).join('')}</tbody></table></div><button type="button" class="reset-btn" data-addorder="${pi}">+ Adicionar ordem</button><div id="ebPhaseDiagnostics-${pi}"></div></div></details>`).join('');
      tableSignature=next;
      if(focusKey){const target=container.querySelector(`[data-p="${focusKey.p}"][data-o="${focusKey.o}"][data-f="${focusKey.f}"]`);target?.focus();if(target?.setSelectionRange&&focusKey.start!=null)target.setSelectionRange(focusKey.start,focusKey.end);}
    }
    updateHTML('ebPhaseSummary','<table class="eb-summary-table"><caption>Consolidação por fase · moeda da conta</caption><thead><tr><th>Fase</th><th>Volumes por instrumento</th><th>Nocional</th><th>Risco aberto</th><th>Pendentes</th><th>Resultado líquido</th><th>Custos</th><th>Compensada · defesas</th></tr></thead><tbody>'+(m.phases||[]).map(p=>{const v=p.metrics||{};return `<tr><th>${esc(p.name||p.id)}</th><td>${esc(p.volumeText||(p.instruments||[]).map(i=>[i.name||i.instrumentId,format(i.metrics?.lots)].join(' ')).join(' · ')||'—')}</td><td>${esc(format(v.operational?.grossNotional))}</td><td>${esc(format(v.operational?.exposure))}</td><td>${esc(format(v.pending||v.pendingRisk))}</td><td>${esc(format(v.closedNetAll||v.realized))}</td><td>${esc(format(v.costs))}</td><td>${esc(format(v.operational?.compensated))}</td></tr>`;}).join('')+'</tbody></table>');
    for(const phase of m.phases||[]){
      const instruments=(phase.instruments||[]).map(i=>m.instruments.find(x=>x.id===i.id)).filter(Boolean);
      updateHTML('ebPhaseDiagnostics-'+phase.index,`<details class="eb-findings"><summary>Diagnósticos e limites desta fase</summary><div class="eb-metrics">${metric('Lucro Técnico',phase.technicalProfit)}${metric('Margem normativa',phase.freeNormativeMargin)}${instruments.map(i=>metric('VRM · '+i.name,i.vrm)+metric('Stop mínimo · '+i.name,i.minimumStop)).join('')}</div><p>Dados por instrumento; sem VRM médio artificial. Compensação econômica não é reposição normativa de margem.</p></details>`);
    }
    for(const [pi,p] of phaseList.entries())for(const [oi] of (p.orders||[]).entries())updateRowCalculations(m,pi,oi);
  }
  function getDraft(pi,oi){
    syncEpoch();const k=draftKey(pi,oi);if(!drafts.has(k)){const o=current(pi,oi),ctx=period();
      drafts.set(k,{before:signature(o),orderId:o?.orderId,version:o?.recordVersion,
        operationId:ctx.value?.activeOperation?.operationId||null,contextRevision:ctx.revision,
        values:{},reason:'',error:''});}return drafts.get(k);
  }
  function onInput(event){
    const target=event.target;
    if(target.matches('[data-eb-reason]')){const [pi,oi]=target.dataset.ebReason.split(':').map(Number);getDraft(pi,oi).reason=target.value;return;}
    if(!target.matches('[data-f]'))return;
    const pi=+target.dataset.p,oi=+target.dataset.o,f=target.dataset.f,d=getDraft(pi,oi);
    d.values[f]=target.type==='checkbox'?target.checked:target.value;d.error='';target.removeAttribute('aria-invalid');
    updateRowCalculations(model(),pi,oi);
    el('phaseContainer').querySelector(`[data-eb-row="${key(pi,oi)}"]`)?.classList.add('eb-dirty');
    const feedback=el(`ebError-${pi}-${oi}`);if(feedback)feedback.textContent='Alterações não salvas.';
  }
  function rowError(pi,oi,text,fieldName){
    const d=getDraft(pi,oi);d.error=text;expanded.add(key(pi,oi));
    const details=document.querySelector(`[data-eb-detail="${key(pi,oi)}"]`);if(details)details.open=true;
    const feedback=el(`ebError-${pi}-${oi}`);if(feedback)feedback.textContent=text;
    const field=fieldName?document.querySelector(`[data-p="${pi}"][data-o="${oi}"][data-f="${fieldName}"]`):document.querySelector(`[data-eb-reason="${key(pi,oi)}"]`);field?.setAttribute('aria-invalid','true');field?.focus();return false;
  }
  function saveRow(pi,oi,{allowClose=false}={}){
    if(root.JPWModuleAvailability&&!root.JPWModuleAvailability.canAccess('forex'))return false;
    syncEpoch();const dk=draftKey(pi,oi),d=drafts.get(dk);if(!d)return true;
    if(jpWealthPersistenceOutcomeIsUnknown())return rowError(pi,oi,'Gravação com desfecho desconhecido. Confira a recuperação antes de uma nova tentativa.');
    const old=current(pi,oi);if(!old||signature(old)!==d.before)return rowError(pi,oi,'A versão confirmada mudou. Cancele a linha para reler antes de editar.');
    if(d.operationId&&period().value?.activeOperation?.operationId!==d.operationId)
      return rowError(pi,oi,'A identidade da operação mudou. Reabra este rascunho antes de salvar.');
    if(period().revision!==d.contextRevision)
      return rowError(pi,oi,'O contexto da conta/período foi alterado. Reabra a linha antes de salvar.');
    const changes={};
    for(const [f,raw] of Object.entries(d.values)){
      const value=numericFields.has(f)?String(raw).trim()===''?null:orderParseResult(raw):raw;
      if(numericFields.has(f)&&value!==null&&!num(value))return rowError(pi,oi,'Informe um número válido em '+label[f]+'.',f);
      if(value!==old[f])changes[f]=value;
    }
    if(changes.status==='Fechada'&&old.status!=='Fechada'&&!allowClose){
      return rowError(pi,oi,'Use Fechar ordem nos detalhes para confirmar resultado e encerramento. As outras alterações continuam no rascunho.','status');
    }
    if(!Object.keys(changes).length){drafts.delete(dk);tableSignature=null;render();return true;}
    if(operationOrderIsLive(old)&&!d.reason.trim())return rowError(pi,oi,'Informe um motivo para salvar a correção inteira.');
    const m=model(),scope=m.scope||{};
    if(!m.selection?.accountId||!scope.periodId)return rowError(pi,oi,'Selecione uma conta cadastrada e registre seu período em Contas antes de gravar o fato.');
    const next={...old,...changes},newIdentity=old.identityContractVersion===1||(!['Pendente','Aberta','Fechada','Migrada'].includes(old.status)&&old.recordStatus!=='recorded');
    if(newIdentity&&['Pendente','Aberta','Fechada'].includes(next.status)){
      if(typeof next.id!=='string'||!next.id.trim())return rowError(pi,oi,'Informe o ID interno da nova ordem.','id');
      if(next.status!=='Pendente'&&(typeof next.brokerHash!=='string'||!next.brokerHash.trim()))return rowError(pi,oi,'Informe o HASH da corretora da nova ordem.','brokerHash');
    }
    const options={reason:d.reason.trim()||'Linha confirmada pelo operador'};
    options.accountId=m.selection.accountId;options.periodId=scope.periodId;
    const result=operationRecordOrders([{pi,oi,changes,expectedVersion:d.version,orderId:d.orderId}],options);
    if(!result.ok)return rowError(pi,oi,result.error||result.mensagem||'Registro recusado. O rascunho foi preservado.');
    drafts.delete(dk);
    const latest=period();for(const remaining of drafts.values()){
      if(remaining.operationId===null)remaining.operationId=latest.value?.activeOperation?.operationId||null;
      remaining.contextRevision=latest.revision;
    }
    tableSignature=null;root.render();render();document.querySelector(`[data-eb-save-row="${key(pi,oi)}"]`)?.focus({preventScroll:true});return true;
  }
  function cancelRow(pi,oi){drafts.delete(draftKey(pi,oi));tableSignature=null;render();document.querySelector(`[data-p="${pi}"][data-o="${oi}"][data-f="id"]`)?.focus();return true;}
  function ensureDialog(){
    if(dialog)return dialog;dialog=document.createElement('dialog');dialog.id='executionBoardDialog';dialog.className='eb-dialog';document.body.append(dialog);
    dialog.addEventListener('cancel',event=>{event.preventDefault();if(observationDirty&&!confirm('Descartar os dados não salvos?'))return;observationDirty=false;dialog.close();});
    dialog.addEventListener('close',()=>{dialogReturn?.focus();dialogReturn=null;});return dialog;
  }
  function openDialog(html){const box=ensureDialog();dialogReturn=document.activeElement;box.innerHTML=html;box.setAttribute('aria-labelledby','ebDialogTitle');if(!box.open)box.showModal();return box;}
  function hasDrafts(){syncEpoch();return drafts.size>0||observationDirty;}
  function requestLeave(callback,title='Sair da Operação'){
    if(leaving||!hasDrafts()){callback();return true;}
    if(dialog?.open)return false;
    const box=openDialog(`<h2 id="ebDialogTitle">${esc(title)}</h2><p>Há linhas com alterações não salvas. Salvar confirma cada linha; correções exigem seu motivo. Os rascunhos não são recuperados após recarregar.</p><div class="eb-dialog-actions"><button type="button" id="ebLeaveStay">Permanecer</button><button type="button" id="ebLeaveDiscard">Descartar alterações</button><button type="button" id="ebLeaveSave">Salvar e continuar</button></div>`);
    el('ebLeaveStay').onclick=()=>box.close();
    const proceed=()=>{box.close();leaving=true;try{callback();}finally{leaving=false;}};
    el('ebLeaveDiscard').onclick=()=>{drafts.clear();tableSignature=null;render();proceed();};
    el('ebLeaveSave').onclick=()=>{box.close();for(const k of [...drafts.keys()]){const [pi,oi]=k.split('|').at(-1).split(':').map(Number);if(!saveRow(pi,oi))return;}proceed();};
    el('ebLeaveStay').focus();return false;
  }
  function guardNavigation(plan,resume){
    if(leaving||!el('exec')?.classList.contains('active')||plan.action==='settings'||plan.action==='checklist')return true;
    const view=plan.localView?.view;
    if(plan.screen==='exec'&&(!view||view==='panel'||view==='@current'))return true;
    if(!hasDrafts())return true;requestLeave(resume);return false;
  }
  function showVersions(pi,oi){
    const o=current(pi,oi);openDialog(`<h2 id="ebDialogTitle">Versões da ordem ${esc(o.id||o.orderId)}</h2>${(o.revisions||[]).map(r=>`<details><summary>Versão ${esc(r.version)} · ${esc(r.recordedAt)} · ${esc(r.reason)}</summary><pre>${esc(JSON.stringify({antes:r.before,depois:r.after,contexto:r.context},null,2))}</pre></details>`).join('')}<button type="button" id="ebDialogClose">Fechar</button>`);el('ebDialogClose').onclick=()=>dialog.close();
  }
  function observationForm(){
    const m=model(),scope=m.scope||{};
    if(!scope.accountId||!scope.periodId||!instrumentChoice){alert('Selecione uma conta com contexto registrado e um instrumento.');return;}
    const observationEpoch=epoch;
    const previous=fx.state.instrumentContext({...scope,instrumentId:instrumentChoice}),record=previous?.record||previous?.value||previous;
    openDialog(`<h2 id="ebDialogTitle">Observação · ${esc(instrumentChoice)}</h2><p>${esc(scope.accountId)} · ${esc(scope.periodId)}. Informe preço e/ou o par de ATRs em unidades de preço; cada componente mantém sua origem.</p><form id="ebObservationForm"><div class="eb-observation-fields"><label>Preço observado<input name="price" inputmode="decimal" placeholder="Opcional"></label><label>ATR55 H4<input name="atrShort" inputmode="decimal" placeholder="Opcional"></label><label>ATR660 H4<input name="atrLong" inputmode="decimal" placeholder="Opcional"></label><label>Origem<input name="source" required placeholder="Plataforma / observação manual"></label><label>Instante da observação<input name="observedAt" type="datetime-local" required></label><label>Motivo<input name="reason" required placeholder="Registro ou correção da observação"></label></div><details class="eb-findings"><summary>Contrato e conversões observados (opcional)</summary><div class="eb-observation-fields"><label>Unidades por lote<input form="ebObservationForm" name="contractSize" inputmode="decimal"></label><label>1 unidade da moeda de cotação na moeda da conta<input form="ebObservationForm" name="quoteRate" inputmode="decimal"></label><label>1 unidade da moeda base do instrumento na moeda da conta<input form="ebObservationForm" name="baseRate" inputmode="decimal"></label></div><p>Informe as duas conversões juntas. Campos vazios preservam as observações confirmadas.</p></details><p id="ebObservationError" role="alert"></p><div class="eb-dialog-actions"><button type="button" id="ebObservationCancel">Cancelar</button><button type="submit">Salvar observação</button></div></form>`);
    const form=el('ebObservationForm');form.addEventListener('input',()=>observationDirty=true);
    el('ebObservationCancel').onclick=()=>{if(observationDirty&&!confirm('Descartar os dados não salvos?'))return;observationDirty=false;dialog.close();};
    form.onsubmit=event=>{
      event.preventDefault();const data=new FormData(form),source=String(data.get('source')).trim(),reason=String(data.get('reason')).trim(),local=String(data.get('observedAt')),at=new Date(local);
      if(!source||!reason||!Number.isFinite(at.getTime())){el('ebObservationError').textContent='Informe origem, data válida e motivo.';return;}
      const componentChanges={},price=String(data.get('price')).trim(),short=String(data.get('atrShort')).trim(),long=String(data.get('atrLong')).trim();
      if(price)componentChanges.price={value:orderParseResult(price),source,observedAt:at.toISOString()};
      if(short||long)componentChanges.atr={short:orderParseResult(short),long:orderParseResult(long),timeframe:'H4',unit:'PRICE',source,observedAt:at.toISOString()};
      const contract=String(data.get('contractSize')||'').trim(),quote=String(data.get('quoteRate')||'').trim(),base=String(data.get('baseRate')||'').trim();
      if(contract)componentChanges.contract={contractSize:orderParseResult(contract),source,observedAt:at.toISOString()};
      if(quote||base)componentChanges.conversion={quoteToAccountRate:orderParseResult(quote),baseToAccountRate:orderParseResult(base),source,observedAt:at.toISOString()};
      const result=fx.state.recordInstrumentContext({...scope,instrumentId:instrumentChoice,componentChanges,expectedRevision:record?.revision??0},{reason,expectedEpoch:observationEpoch});
      if(!result.ok){el('ebObservationError').textContent=result.error||'Observação não confirmada; mantenha os dados para conferir.';return;}
      observationDirty=false;dialog.close();root.render();render();
    };
  }
  function diagnosticForm(){
    const m=model(),scope=m.scope||{};
    if(!scope.accountId||!scope.periodId||!instrumentChoice){alert('Selecione uma conta, um período e um instrumento.');return;}
    const target={...scope,instrumentId:instrumentChoice},previous=fx.state.executionDiagnostics(target),record=previous.value,diagnosticEpoch=epoch;
    openDialog(`<h2 id="ebDialogTitle">Raiz-N · ${esc(instrumentChoice)}</h2><p>Cenários diagnósticos em H4. Informe N (quantidade de candles) e F (fator de segurança) para cada horizonte. Não há valores automáticos nem alteração do stop da ordem.</p><form id="ebDiagnosticForm"><table class="eb-diagnostic-inputs"><thead><tr><th>Horizonte</th><th>N · candles H4</th><th>F · fator</th></tr></thead><tbody>${[['oneWeek','1 semana'],['twoWeeks','2 semanas']].map(([k,title])=>`<tr><th scope="row">${title}</th><td><input name="${k}N" inputmode="numeric" aria-label="N · ${title}" value="${esc(record?.[k]?.n??'')}" placeholder="Informar"></td><td><input name="${k}F" inputmode="decimal" aria-label="F · ${title}" value="${esc(record?.[k]?.f??'')}" placeholder="Informar"></td></tr>`).join('')}</tbody></table><p>Deixe os dois campos de um horizonte vazios para mantê-lo sem cenário. Ao retirar valores já salvos, esse horizonte deixará de ser calculado.</p><div class="eb-observation-fields"><label>Responsável pela declaração<input name="declaredBy" required value="${esc(record?.declaredBy||S.onboarding?.operador||'')}"></label><label>Motivo<input name="reason" required placeholder="Declaração ou revisão do cenário"></label></div><p id="ebDiagnosticError" role="alert"></p><div class="eb-dialog-actions"><button type="button" id="ebDiagnosticCancel">Cancelar</button><button type="submit">Salvar cenários</button></div></form>`);
    const form=el('ebDiagnosticForm');form.addEventListener('input',()=>observationDirty=true);
    el('ebDiagnosticCancel').onclick=()=>{if(observationDirty&&!confirm('Descartar os cenários não salvos?'))return;observationDirty=false;dialog.close();};
    form.onsubmit=event=>{
      event.preventDefault();const data=new FormData(form),scenarios={};
      for(const k of ['oneWeek','twoWeeks']){
        const rawN=String(data.get(k+'N')).trim(),rawF=String(data.get(k+'F')).trim();
        if(!rawN&&!rawF){scenarios[k]=null;continue;}
        const n=orderParseResult(rawN),f=orderParseResult(rawF);
        if(!rawN||!rawF||!Number.isSafeInteger(n)||n<=0||!num(f)||f<=0){el('ebDiagnosticError').textContent='Informe N inteiro positivo e F positivo juntos em cada horizonte.';return;}
        scenarios[k]={n,f};
      }
      const result=fx.state.recordExecutionDiagnostics({...target,...scenarios,expectedRevision:previous.revision||0,declaredBy:String(data.get('declaredBy')).trim(),declaredAt:new Date().toISOString()},{reason:String(data.get('reason')).trim(),expectedEpoch:diagnosticEpoch});
      if(!result.ok){el('ebDiagnosticError').textContent=result.error||'Cenário não confirmado; seus dados permanecem no formulário.';return;}
      observationDirty=false;dialog.close();render();
    };
  }
  function onClick(event){
    const button=event.target.closest('button');if(!button)return;
    if(button.hasAttribute('data-eb-phase-jump')){
      if(el('execWidgetGrid').hidden&&!JPWNavigation.navigateLocal('exec','panel'))return;
      const pi=Number(button.dataset.ebPhaseJump),phase=el('ebPhase-'+pi);
      if(phase){phase.open=true;openedPhases.add(pi);phase.scrollIntoView({block:'start'});phase.querySelector('summary')?.focus({preventScroll:true});}return;
    }
    if(button.hasAttribute('data-eb-update-quotes')){updateFxRates();return;}
    if(button.hasAttribute('data-eb-retry-quotes')){fx.marketQuotes.retry();return;}
    if(button.hasAttribute('data-eb-observation')){observationForm();return;}
    if(button.hasAttribute('data-eb-diagnostics')){diagnosticForm();return;}
    if(button.hasAttribute('data-eb-motor')){JPWNavigation.navigateLocal('exec','motor');return;}
    if(button.hasAttribute('data-eb-manage')){
      requestLeave(()=>{
        const selected=fx.state.operationalSelection();
        if(JPWNavigation.navigate('forex-management-accounts'))fx.accountsUI?.examine(selected.accountId,selected.periodId);
      },'Gerenciar conta e período');return;
    }
    const parse=attr=>(button.getAttribute(attr)||'').split(':').map(Number);
    if(button.hasAttribute('data-eb-save-row')){saveRow(...parse('data-eb-save-row'));return;}
    if(button.hasAttribute('data-eb-cancel-row')){cancelRow(...parse('data-eb-cancel-row'));return;}
    if(button.hasAttribute('data-orderhistory')){showVersions(...parse('data-orderhistory'));return;}
    if(button.hasAttribute('data-addorder')){const pi=+button.dataset.addorder;if(operationRecordFeedback(operationAddDraft(pi))){tableSignature=null;openedPhases.add(pi);render();[...document.querySelectorAll(`.phase[data-phase="${pi}"] tr[data-eb-row]`)].at(-1)?.querySelector('input')?.focus();}return;}
    if(button.hasAttribute('data-delorder')){
      const [pi,oi]=parse('data-delorder');requestLeave(()=>{const o=current(pi,oi);const reason=operationOrderIsLive(o)?prompt('Motivo da anulação. A ordem e suas versões serão preservadas:'):'Excluir rascunho';
      if(!reason?.trim())return;if(!operationOrderIsLive(o)&&!confirm('Excluir o rascunho desta linha?'))return;
      if(operationRecordFeedback(operationVoidOrder(pi,oi,reason))){drafts.delete(draftKey(pi,oi));tableSignature=null;root.render();render();}},'Revisar alterações antes de excluir ou anular');return;
    }
    if(button.hasAttribute('data-eb-close-row')){
      const [pi,oi]=parse('data-eb-close-row');
      requestLeave(()=>openCloseOrderModal(pi,oi),'Resolver alterações antes de fechar ordem');return;
    }
  }
  root.addEventListener('jpwealth:forex-quotes',()=>{
    const state=fx.marketQuotes.get();
    for(const id of ['fxFetchStatus','ebQuoteStatus']){const node=el(id);if(node)node.textContent=state.message;}
    for(const button of document.querySelectorAll('[data-eb-update-quotes],#fxUpdateBtn'))button.disabled=state.busy;
    if(!state.busy)render();
  });
  root.addEventListener('beforeunload',event=>{if(hasDrafts()){event.preventDefault();event.returnValue='';}});
  fx.executionBoardUI={render,renderPhases,hasDrafts,
    backupDrafts:()=>hasDrafts()?{rows:[...drafts.entries()],observation:observationDirty&&el('ebObservationForm')?Object.fromEntries(new FormData(el('ebObservationForm'))):null,diagnostics:observationDirty&&el('ebDiagnosticForm')?Object.fromEntries(new FormData(el('ebDiagnosticForm'))):null,instrumentId:instrumentChoice,selection:fx.state.operationalSelection()}:null,saveRow,cancelRow,requestLeave,guardNavigation,
    discard(){drafts.clear();expanded.clear();observationDirty=false;tableSignature=null;if(dialog?.open)dialog.close();},
    getSelection:()=>({accountId:fx.state.operationalSelection().accountId,instrumentId:instrumentChoice})};
  render();
})(globalThis);

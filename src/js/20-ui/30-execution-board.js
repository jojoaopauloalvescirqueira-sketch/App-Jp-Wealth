// Execution Board: presentation and RAM drafts. Financial projections and all
// writes belong to the existing Forex domain. No draft is part of S or backup.
(function(root){
  'use strict';
  const fx=root.JPWForex;
  const drafts=new Map(), expanded=new Set(), openedPhases=new Set();
  let instrumentChoice=null,tableSignature=null,leaving=false;
  let epoch=jpWealthPersistenceEpoch(),dialog=null,dialogReturn=null,observationDirty=false,periodFormAccount=null;
  const num=v=>typeof v==='number'&&Number.isFinite(v);
  const el=id=>document.getElementById(id);
  const key=(pi,oi)=>pi+':'+oi;
  const period=()=>fx.state.accountContext(fx.state.operationalSelection());
  const current=(pi,oi)=>period().value?.phases?.[pi]?.orders?.[oi];
  const draftKey=(pi,oi)=>{const s=fx.state.operationalSelection();
    return [s.accountId||'',s.periodId||'',pi+':'+oi].join('|');};
  const signature=o=>JSON.stringify(o);
  const n=(v,d=2)=>num(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:d}):'Não calculável';
  const label={id:'ID',par:'Instrumento',tipo:'Direção',role:'Papel',lote:'Lote',entry:'Entrada',sl:'Stop',tp:'Alvo',status:'Estado',result:'Resultado',costs:'Custos assinados',costBasis:'Tratamento dos custos',stopValidated:'Stop validado',amplifiesExposure:'Pendente amplia exposição',pendingActive:'Pendente ativa'};
  const numericFields=new Set(['lote','entry','sl','tp','result','costs']);
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
    if(detail.referenceDate)parts.push('Taxa de '+detail.referenceDate);
    if(detail.observedAt)parts.push('Observada '+detail.observedAt);
    else if(detail.recordedAt)parts.push('Registrada '+detail.recordedAt);
    if(detail.fetchedAt)parts.push('Consultada '+detail.fetchedAt);
    return parts.filter(Boolean).join(' · ');
  }
  function metric(title,m,{id='',note='',limit=null}={}){
    const valid=num(m?.value),source=provenance(m),track=valid&&num(limit)&&limit>0;
    return `<div class="eb-metric"${id?` data-eb-metric="${esc(id)}"`:''}><span>${esc(title)}</span><strong>${esc(format(m))}</strong>${num(m?.percent)?`<small>${esc(n(m.percent))}% do SI</small>`:''}${track?`<meter min="0" max="${limit}" value="${Math.max(0,Math.min(limit,m.value))}" aria-label="${esc(title)}" title="${esc(format(m))} · limite ${esc(String(limit))}"></meter>`:''}<small>${esc(valid?(note||source):reason(m))}</small>${valid&&source&&note?`<small>${esc(source)}</small>`:''}</div>`;
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
    header.innerHTML='<div><p class="eb-eyebrow">EXECUTION BOARD</p><h2>Painel Operacional</h2><p id="ebOperationIdentity"></p></div><div class="eb-heading-controls"><label>Conta operacional<select id="ebAccountSelect"></select></label><div id="ebChecklistHost"></div></div>';
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
    el('ebAccountSelect').addEventListener('change',event=>{
      const choice=event.target.value;
      if(!choice){render();return;}
      const previous=fx.state.operationalSelection().accountId;
      requestLeave(()=>{const result=fx.state.selectOperationalAccount(choice);
        if(!result.ok){alert(result.error);return;}
        openedPhases.clear();expanded.clear();tableSignature=null;render();
        if(typeof renderLedger==='function')renderLedger();if(typeof renderContas==='function')renderContas();
        if(typeof renderMotor==='function')renderMotor();},'Trocar a conta operacional');
      if(drafts.size)event.target.value=previous||'';
    });
    grid.addEventListener('click',onClick);
    el('accountPeriodSelect')?.addEventListener('change',event=>{
      const selected=fx.state.operationalSelection(),periodId=event.target.value;
      if(!periodId)return;
      requestLeave(()=>{const result=fx.state.selectOperationalPeriod(selected.accountId,periodId);
        if(!result.ok){el('accountPeriodFeedback').textContent=result.error;return;}
        tableSignature=null;render();if(typeof renderLedger==='function')renderLedger();},'Consultar outro período');
    });
    el('accountObservedPeriod')?.addEventListener('change',event=>{
      const id=event.target.value,accountId=fx.state.operationalSelection().accountId;
      let item=S.forex?.accounts?.[accountId],seen=new Set();
      while(item&&!seen.has(item)&&item.periodId!==id){seen.add(item);item=item.previous;}
      if(item?.periodId===id){el('accountPeriodSI').value=String(item.si);
        el('accountPeriodCurrency').value=item.currency;
        el('accountPeriodStart').value=item.observedAt.slice(0,10);
        el('accountPeriodActivate').checked=false;}
    });
    el('accountPeriodSave')?.addEventListener('click',()=>{
      const selected=fx.state.operationalSelection(),id=selected.accountId;
      const registered=(S.accounts||[]).filter(a=>a?.forexAccountId===id);
      if(registered.length!==1){el('accountPeriodFeedback').textContent='Confirme a identificação da conta no cadastro antes de registrar o período.';return;}
      const amount=id=>{const raw=el(id).value.trim();return raw===''?null:Number(raw);};
      const si=amount('accountPeriodSI'),openingBook=amount('accountPeriodBook');
      if(si!==null&&(!num(si)||si<=0)||openingBook!==null&&!num(openingBook)){
        el('accountPeriodFeedback').textContent='SI e saldo book devem ser números válidos ou ficar explicitamente indisponíveis.';return;}
      const result=fx.state.recordAccountPeriod({accountId:id,startedAt:el('accountPeriodStart').value,
        currency:el('accountPeriodCurrency').value.trim().toUpperCase(),si,openingBook,
        source:el('accountPeriodSource').value.trim(),
        observationPeriodId:el('accountObservedPeriod').value||null,
        activateCurrentPeriod:el('accountPeriodActivate').checked},
        {reason:el('accountPeriodReason').value.trim(),expectedEpoch:jpWealthPersistenceEpoch()});
      el('accountPeriodFeedback').textContent=result.ok?'Período confirmado nesta conta; nenhuma operação antiga foi atribuída.':result.error;
      if(result.ok){const currentId=S.forex?.accountContexts?.accounts?.[id]?.currentPeriodId;
        if(el('accountPeriodActivate').checked&&currentId)fx.state.selectOperationalPeriod(id,currentId);
        tableSignature=null;render();if(typeof renderLedger==='function')renderLedger();}
    });
    el('phaseContainer').addEventListener('input',onInput);
    el('phaseContainer').addEventListener('change',onInput);
    el('phaseContainer').addEventListener('toggle',event=>{
      const node=event.target;if(node.matches?.('details[data-phase]')){const pi=+node.dataset.phase;node.open?openedPhases.add(pi):openedPhases.delete(pi);}
      if(node.matches?.('details[data-eb-detail]'))node.open?expanded.add(node.dataset.ebDetail):expanded.delete(node.dataset.ebDetail);
    },true);
  }
  function renderAccountContext(){
    const selected=fx.state.operationalSelection(),id=selected.accountId,
      registered=(S.accounts||[]).find(a=>a?.forexAccountId===id),
      account=S.forex?.accountContexts?.accounts?.[id],ctx=period(),p=ctx.status==='OK'?ctx.value:null;
    const identity=el('accountContextIdentity');if(!identity)return;
    identity.textContent=registered?`${registered.nome||id} · ${registered.platform||'plataforma não verificada'} · ${registered.platformLogin||'login não verificado'} · ${registered.platformCurrency||'moeda não verificada'}`:
      'Selecione e confirme o cadastro de uma conta. Contas históricas permanecem consultáveis no legado.';
    const lastBook=p?.ledger?.slice().sort((a,b)=>a.data.localeCompare(b.data)).at(-1)?.saldo??p?.openingBook??null;
    let obs=S.forex?.accounts?.[id],seen=new Set();
    while(obs&&!seen.has(obs)&&obs.periodId!==p?.periodId){seen.add(obs);obs=obs.previous;}
    const equity=obs&&p&&obs.periodId===p.periodId?obs.equity:null;
    const fmt=v=>num(v)?fmtForexMoney(v,{currency:p?.currency||registered?.platformCurrency||null}):'Indisponível';
    updateHTML('accountContextMetrics',`<div class="metric"><div class="k">SI do período</div><div class="v sm">${esc(fmt(p?.si))}</div></div><div class="metric"><div class="k">Saldo inicial book</div><div class="v sm">${esc(fmt(p?.openingBook))}</div></div><div class="metric"><div class="k">Último saldo book</div><div class="v sm">${esc(fmt(lastBook))}</div></div><div class="metric"><div class="k">Equity observada</div><div class="v sm">${esc(fmt(equity))}</div></div><div class="metric"><div class="k">Operação em andamento</div><div class="v sm">${esc(p?.activeOperation?.operationId||'Nenhuma')}</div></div>`);
    const periodSelect=el('accountPeriodSelect'),periodList=Object.values(account?.periods||{}).sort((a,b)=>a.startedAt.localeCompare(b.startedAt));
    if(document.activeElement!==periodSelect){periodSelect.innerHTML='<option value="">Sem período confirmado</option>'+periodList.map(x=>`<option value="${esc(x.periodId)}">${esc(x.startedAt)} · ${esc(x.periodId)} · ${esc(x.currency)}</option>`).join('');
      periodSelect.value=selected.periodId||'';}
    if(periodFormAccount!==id){periodFormAccount=id;el('accountPeriodCurrency').value=registered?.platformCurrency||'';
      el('accountPeriodStart').value='';el('accountPeriodSI').value='';el('accountPeriodBook').value='';
      el('accountPeriodSource').value='';el('accountPeriodReason').value='';}
    const obsSelect=el('accountObservedPeriod');if(document.activeElement!==obsSelect){
      let item=S.forex?.accounts?.[id],seenObs=new Set(),observed=[];
      while(item&&!seenObs.has(item)){seenObs.add(item);if(!account?.periods?.[item.periodId])
        observed.push(item);item=item.previous;}
      const prior=obsSelect.value;
      obsSelect.innerHTML='<option value="">Novo período sem vínculo observado</option>'+observed.map(x=>`<option value="${esc(x.periodId)}">${esc(x.periodId)} · SI ${esc(String(x.si))} ${esc(x.currency)}</option>`).join('');
      obsSelect.value=observed.some(x=>x.periodId===prior)?prior:'';
    }
  }
  function render(){
    if(!fx.executionBoard||typeof S==='undefined'||!S)return;
    prepareShell();const m=model();renderAccountContext();
    const select=el('ebAccountSelect');if(!select)return;
    const options=m.selection?.accounts||[];
    if(document.activeElement!==select){
      select.innerHTML='<option value="">Selecionar conta</option>'+options.map(a=>`<option value="${esc(a.accountId||a.forexAccountId||a.id)}">${esc(a.name||a.label||a.nome||a.accountId||a.id)}${(a.tipo||a.type)==='MESTRE'?' · Mestre':''}</option>`).join('');
      select.value=m.selection?.accountId||'';
    }
    select.disabled=!options.length;
    el('ebOperationIdentity').textContent=m.scope?.operationId?`Operação ${m.scope.operationId} · período ${m.scope.periodId||'não identificado'} · ${m.scope.currency||'moeda não identificada'}`:
      `Conta ${m.selection?.accountId||'não selecionada'} · ${m.scope?.periodId?'nova operação neste período':'registre um período em Contas'}.`;
    const account=m.accountRecord||m.account||{},capital=m.capital||{},risk=m.risk||{},eco=m.economics||{};
    updateHTML('executionBoardAccount',`<div class="eb-section-head"><div><p class="eb-eyebrow">01 · CONTEXTO</p><h3>Conta e proteção</h3></div><button type="button" class="reset-btn" data-eb-account-facts>Registrar observação da conta</button></div><p class="eb-context-line">${esc([account.name||account.nome||m.selection?.accountId,account.platform||account.plataforma,account.login||account.accountNumber,m.scope?.currency].filter(Boolean).join(' · ')||m.selection?.reason||'Selecione uma conta cadastrada.')}</p><div class="eb-metrics">${metric('Saldo registrado',capital.book,{note:'Cadastro atual · saldo book; não é equity flutuante.'})}${metric('Equity observada',capital.equity)}${metric('SI do período',capital.si)}${metric('Resultado do período',capital.periodResult||capital.result,{note:'Base e período registrados.'})}${metric('Drawdown',capital.drawdown,{id:'drawdown',limit:22})}${metric('Encerramento estatutário',capital.stopoutEquity,{note:'Limite de DD em 22%; não é stop-out da corretora.'})}</div><div class="eb-phase-scale" aria-label="Faixas de drawdown da conta">${fx.policy.phases.map(p=>`<span>${esc(p.name)}<small>${esc(String(p.ddMinPercent??p.lower??''))}–${esc(String(p.ddMaxPercent??p.upper??22))}%</small></span>`).join('')}</div><p class="eb-context-line">Responsáveis declarados da sessão: ${esc([S.onboarding?.operador,S.onboarding?.supervisor].filter(Boolean).join(' · ')||'Não informados')}. Sem vínculo cadastral por conta.</p><p class="eb-context-line">Fase da conta: <strong>${esc(fx.policy.phases[(risk.accountPhase?.value||0)-1]?.name||(risk.accountPhase?.compulsoryClose?'Encerramento compulsório':'Não calculável'))}</strong> · Grade declarada: <strong>${esc(m.declaredGrid?.name||m.grid?.name||S.forex?.grid?.declaredPhase||'Não declarada')}</strong></p><details class="eb-findings"><summary>Execução normativa bloqueada · consultar motivos</summary><p>Registrar um fato não autoriza sua execução.</p><ul>${(m.findings||[]).map(f=>`<li>${esc(f.message||f.reason||f.code||String(f))}</li>`).join('')}</ul><button type="button" class="reset-btn" data-eb-motor>Revisar dados no Motor</button></details>`);
    updateHTML('executionBoardRisk',`<div class="eb-section-head"><div><p class="eb-eyebrow">02 · RISCO REGISTRADO</p><h3>Exposição e alavancagem</h3></div></div><div class="eb-metrics">${metric('Stops abertos',risk.open,{id:'open'})}${metric('Pendentes ampliadoras',risk.pending||risk.aggregate?.pendingRiskMetric)}${metric('Risco comprometido V11',risk.committed,{id:'committed'})}${metric('Nocional bruto',risk.grossNotional)}${metric('Alavancagem',risk.leverage,{limit:risk.leverageLimit?.value||risk.phaseLeverageLimit?.value,note:'Nocional bruto ÷ min(SI, equity).'})}${metric('Capacidade prudencial restante',risk.prudentialRemaining||risk.prudential,{note:'Não é margem livre da corretora nem autorização de admissão.'})}</div><div class="eb-economic"><p class="eb-eyebrow">LEITURAS ECONÔMICAS · SEM CRÉDITO NORMATIVO</p><div class="eb-metrics">${metric('Compensada pelas defesas',eco.compensatedDefenses,{id:'compensatedDefenses'})}${metric('Compensada da operação',eco.compensatedAll,{id:'compensatedAll'})}${metric('Resultado líquido realizado',eco.closedNetAll,{id:'closedNetAll'})}</div><p>Risco aberto menos resultado líquido assinado. Lucros positivos não aumentam o risco permitido.</p></div>`);
    renderInstruments(m);
    renderPhases(m);
    const supported=fx.state.supported();
    let notice=el('ebUnsupported');if(!notice){notice=document.createElement('p');notice.id='ebUnsupported';notice.className='eb-row-feedback';el('executionBoard').append(notice);}
    notice.textContent=supported?'':'Versão do agregado Forex incompatível. Apenas leitura; preserve a base.';notice.hidden=supported;
    for(const button of el('execWidgetGrid').querySelectorAll('[data-addorder],[data-eb-save-row],[data-eb-observation],[data-eb-update-quotes],[data-eb-retry-quotes],[data-eb-account-facts]'))if(!supported)button.disabled=true;
    if(el('exec')?.classList.contains('active')&&typeof renderHeaderReadout==='function')
      renderHeaderReadout(compute());
  }
  function renderInstruments(m){
    const instruments=m.instruments||[];
    if(!instruments.some(x=>(x.instrumentId||x.id||x.name)===instrumentChoice))instrumentChoice=instruments[0]?.instrumentId||instruments[0]?.id||instruments[0]?.name||null;
    const item=instruments.find(x=>(x.instrumentId||x.id||x.name)===instrumentChoice)||{};
    updateHTML('executionBoardInstruments',`<div class="eb-section-head"><div><p class="eb-eyebrow">03 · INSTRUMENTOS</p><h3>Mercado e dimensionamento</h3></div><div class="eb-actions"><button type="button" class="reset-btn" data-eb-update-quotes>Atualizar referência diária</button>${fx.marketQuotes?.get()?.canRetry?'<button type="button" class="reset-btn" data-eb-retry-quotes>Repetir gravação da referência</button>':''}<button type="button" class="reset-btn" data-eb-observation>Registrar preço / ATR</button></div></div><div class="eb-instrument-toolbar"><label>Instrumento<select id="ebInstrumentSelect">${instruments.map(i=>`<option value="${esc(i.instrumentId||i.id||i.name)}" ${(i.instrumentId||i.id||i.name)===instrumentChoice?'selected':''}>${esc(i.name||i.instrumentId||i.id)}</option>`).join('')}</select></label><p id="ebQuoteStatus" role="status">${esc(fx.marketQuotes?.get()?.message||'Referência diária Frankfurter · não é preço de execução.')}</p></div><div class="eb-metrics">${metric('Preço observado / referência',item.price)}${metric('ATR55 H4',{value:item.atr?.short,unit:'PRICE',source:item.atr})}${metric('ATR660 H4',{value:item.atr?.long,unit:'PRICE',source:item.atr})}${metric('VRM · ATR55/ATR660',item.vrm,{limit:1.5,note:typeof item.regime?.value==='string'?item.regime.value:'Regime ainda não calculável.'})}${metric('Lote de referência · normal 0,50×',item.normal)}${metric('Lote de referência · restritivo 0,25×',item.restrictive)}</div><p class="eb-context-line">Referências nocionais teóricas; não representam dimensionamento autorizado. Cada contrato e conversão exige origem conhecida.</p><details class="eb-findings"><summary>Dimensionamento normativo e diagnóstico de stop</summary>${metric('Dimensionamento autorizado',m.risk?.sizingTrace,{note:'P-14/P-17/P-18 e admissão histórica pendentes.'})}${(m.phases||[]).flatMap(p=>(p.rows||[]).filter(r=>r.instrumentId===instrumentChoice).map(r=>metric('Stop / ATR · '+p.name+' · '+(r.order.id||r.order.orderId),r.atrMultiple))).join('')||'<p>Stop / ATR: nenhuma ordem conciliada deste instrumento.</p>'}${metric('Stop mínimo em preço',item.minimumStop)}<p>Stop Raiz-N: fator F (P-21) pendente e horizonte N dependente do caso. Lucro Técnico e Margem Operacional Reposta não são calculados por analogia à planilha.</p>${item.operable===false?'<p>Instrumento com restrição normativa preservada.</p>':''}<p>${esc(item.reason||'')}</p></details>`);
    const select=el('ebInstrumentSelect');if(select)select.onchange=()=>{instrumentChoice=select.value;renderInstruments(model());};
  }
  function field(pi,oi,o,f,choices){
    const readonly=o.recordStatus==='voided'||!fx.state.supported(),draft=drafts.get(draftKey(pi,oi));
    const value=draft&&Object.prototype.hasOwnProperty.call(draft.values,f)?draft.values[f]:o[f];
    const attrs=`data-p="${pi}" data-o="${oi}" data-f="${f}" aria-label="${esc(label[f])} · ordem ${pi+1}.${oi+1}" aria-describedby="ebError-${pi}-${oi}" ${readonly?'disabled':''}`;
    if(choices)return `<select ${attrs}>${choices.map(([v,t])=>`<option value="${esc(v)}" ${String(value??'')===v?'selected':''}>${esc(t)}</option>`).join('')}</select>`;
    if(['stopValidated','amplifiesExposure','pendingActive'].includes(f))return `<input type="checkbox" ${attrs} ${value===true?'checked':''}>`;
    return `<input ${attrs} type="text" ${numericFields.has(f)?'inputmode="decimal"':''} value="${esc(value??'')}" placeholder="${numericFields.has(f)?'—':'ID'}" autocomplete="off">`;
  }
  function rowHTML(pi,oi,o){
    const k=key(pi,oi),draft=drafts.get(draftKey(pi,oi)),live=operationOrderIsLive(o),readonly=o.recordStatus==='voided'||!fx.state.supported();
    const cell=(f,choices)=>`<td>${field(pi,oi,o,f,choices)}</td>`;
    const instruments=[['','Selecionar'],...(S.instruments||[]).map(i=>[i.name,i.name])];
    if(o.par&&!instruments.some(([x])=>x===o.par))instruments.push([o.par,o.par+' · não cadastrado']);
    return `<tr class="eb-order-row ${draft?'eb-dirty':''}" data-eb-row="${k}"><td class="eb-order-id">${field(pi,oi,o,'id')}<small>${esc(o.recordStatus==='voided'?'Anulada · histórico':!fx.state.supported()?'Somente leitura':o.recordStatus==='draft'||!o.status?'Rascunho':o.orderId||'Identidade não capturada')}</small></td>${cell('par',instruments)}${cell('tipo',[['BUY','Compra'],['SELL','Venda']])}${cell('role',[['','Não declarado'],['GENESIS','Gênese'],['DEFENSE','Defesa'],['OTHER','Outro']])}${cell('lote')}${cell('entry')}${cell('sl')}${cell('tp')}${cell('status',[['','Rascunho'],['Pendente','Pendente'],['Aberta','Aberta'],['Fechada','Fechada'],...(o.status==='Migrada'?[['Migrada','Migrada']]:[])])}<td class="eb-number" data-eb-row-risk="${k}">—</td><td class="eb-row-actions"><button type="button" data-eb-save-row="${k}" ${readonly?'disabled':''}>Salvar linha</button><button type="button" data-eb-cancel-row="${k}" ${readonly?'disabled':''}>Cancelar</button></td></tr><tr class="eb-detail-row"><td colspan="11"><details data-eb-detail="${k}" ${expanded.has(k)||draft?.error?'open':''}><summary>Custos, resultado e rastreabilidade${draft?' · alterações não salvas':''}</summary><div class="eb-order-details">${['result','costs'].map(f=>`<label>${esc(label[f])} (${esc(o.currency||'moeda não capturada')})${field(pi,oi,o,f)}</label>`).join('')}<label>Tratamento dos custos${field(pi,oi,o,'costBasis',[['','Não declarado'],['SEPARATE_FROM_RESULT','Separados do resultado'],['INCLUDED_IN_RESULT','Incluídos no resultado']])}</label>${['stopValidated','amplifiesExposure','pendingActive'].map(f=>`<label class="eb-check">${field(pi,oi,o,f)}${esc(label[f])}</label>`).join('')}<label class="eb-reason">${live?'Motivo da correção (obrigatório ao salvar)':'Observação do registro (opcional)'}<input type="text" data-eb-reason="${k}" value="${esc(draft?.reason||'')}" ${readonly?'disabled':''}></label></div><p class="eb-context-line">Conta ${esc(o.accountId||'não capturada')} · período ${esc(o.periodId||'não capturado')} · ${esc(o.currency||'moeda não capturada')} · versão ${esc(o.recordVersion??0)}</p><div class="eb-actions">${!readonly?`<button type="button" class="reset-btn" data-eb-close-row="${k}">Fechar ordem</button><button type="button" class="reset-btn" data-delorder="${k}">${live?'Anular com motivo':'Excluir rascunho'}</button>`:''}${o.revisions?.length?`<button type="button" class="reset-btn" data-orderhistory="${k}">Ver ${o.revisions.length} versão(ões)</button>`:''}</div></details><p id="ebError-${pi}-${oi}" class="eb-row-feedback" role="status">${esc(draft?.error||'')}</p></td></tr>`;
  }
  function renderPhases(m){
    if(!fx.executionBoard)return;
    m=m||model();const container=el('phaseContainer');if(!container)return;
    const phaseList=period().value?.phases||[];
    const next=JSON.stringify({scope:fx.state.operationalSelection(),supported:fx.state.supported(),phases:phaseList.map(p=>({name:p.faseNome,policy:p.policyVersion,orders:p.orders}))});
    // Quote/account repaints update numbers only. Live input nodes and cursor stay mounted.
    if(next!==tableSignature||!container.querySelector('.eb-order-table')){
      const focus=document.activeElement,focusKey=focus?.dataset?.f?{p:focus.dataset.p,o:focus.dataset.o,f:focus.dataset.f,start:focus.selectionStart,end:focus.selectionEnd}:null;
      container.innerHTML=`<p class="eb-context-line">${phaseList.length===4?'Grades LEGACY preservadas; os quatro índices não correspondem às seis fases V11.':'Fase de registro da ordem e fase da conta são informações distintas.'} Totais usam somente registros confirmados.</p><div id="ebPhaseSummary" class="eb-table-scroll"></div>`+phaseList.map((p,pi)=>`<details class="phase eb-phase" data-phase="${pi}" ${openedPhases.has(pi)||(!tableSignature&&pi===0)?'open':''}><summary><span>${esc(phaseList.length===4?'LEGACY · '+(p.faseNome||pi+1):fx.policy.phases[pi]?.name||p.faseNome)}</span><span>${(p.orders||[]).length} linha(s)</span></summary><div class="phase-body"><div class="eb-table-scroll" tabindex="0" role="region" aria-label="Ordens da fase ${pi+1}"><table class="otable eb-order-table"><thead><tr>${['ID','Instrumento','Direção','Papel','Lote','Entrada','Stop','Alvo','Estado','Risco confirmado','Ações'].map(t=>'<th scope="col">'+t+'</th>').join('')}</tr></thead><tbody>${(p.orders||[]).map((o,oi)=>rowHTML(pi,oi,o)).join('')}</tbody></table></div><button type="button" class="reset-btn" data-addorder="${pi}">+ Adicionar ordem</button><div id="ebPhaseDiagnostics-${pi}"></div></div></details>`).join('');
      tableSignature=next;
      if(focusKey){const target=container.querySelector(`[data-p="${focusKey.p}"][data-o="${focusKey.o}"][data-f="${focusKey.f}"]`);target?.focus();if(target?.setSelectionRange&&focusKey.start!=null)target.setSelectionRange(focusKey.start,focusKey.end);}
    }
    updateHTML('ebPhaseSummary','<table class="eb-summary-table"><caption>Consolidação por fase · moeda da conta</caption><thead><tr><th>Fase</th><th>Volumes por instrumento</th><th>Nocional</th><th>Risco aberto</th><th>Pendentes</th><th>Resultado líquido</th><th>Custos</th><th>Compensada</th></tr></thead><tbody>'+(m.phases||[]).map(p=>{const v=p.metrics||{};return `<tr><th>${esc(p.name||p.id)}</th><td>${esc(p.volumeText||(p.instruments||[]).map(i=>[i.name||i.instrumentId,format(i.metrics?.lots)].join(' ')).join(' · ')||'—')}</td><td>${esc(format(v.grossNotional||v.notional))}</td><td>${esc(format(v.open||v.openRisk))}</td><td>${esc(format(v.pending||v.pendingRisk))}</td><td>${esc(format(v.closedNetAll||v.realized))}</td><td>${esc(format(v.costs))}</td><td>${esc(format(v.compensatedAll))}</td></tr>`;}).join('')+'</tbody></table>');
    for(const phase of m.phases||[]){
      const instruments=(phase.instruments||[]).map(i=>m.instruments.find(x=>x.id===i.id)).filter(Boolean);
      updateHTML('ebPhaseDiagnostics-'+phase.index,`<details class="eb-findings"><summary>Diagnósticos e limites desta fase</summary><div class="eb-metrics">${metric('Lucro Técnico',phase.technicalProfit)}${metric('Margem normativa',phase.freeNormativeMargin)}${instruments.map(i=>metric('VRM · '+i.name,i.vrm)+metric('Stop mínimo · '+i.name,i.minimumStop)).join('')}</div><p>Dados por instrumento; sem VRM médio artificial. Compensação econômica não é reposição normativa de margem.</p></details>`);
    }
    for(const phase of m.phases||[])for(const row of phase.rows||[]){const target=container.querySelector(`[data-eb-row-risk="${row.pi}:${row.oi}"]`);if(target)target.textContent=format(row.risk||row.openRisk);}
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
    d.values[f]=target.type==='checkbox'?target.checked:target.value;d.error='';
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
    const options={reason:d.reason.trim()||'Linha confirmada pelo operador'};
    options.accountId=m.selection.accountId;options.periodId=scope.periodId;
    const result=operationRecordOrders([{pi,oi,changes,expectedVersion:d.version,orderId:d.orderId}],options);
    if(!result.ok)return rowError(pi,oi,result.error||result.mensagem||'Registro recusado. O rascunho foi preservado.');
    drafts.delete(dk);
    const latest=period();for(const remaining of drafts.values()){
      if(remaining.operationId===null)remaining.operationId=latest.value?.activeOperation?.operationId||null;
      remaining.contextRevision=latest.revision;
    }
    tableSignature=null;root.render();render();return true;
  }
  function cancelRow(pi,oi){drafts.delete(draftKey(pi,oi));tableSignature=null;render();document.querySelector(`[data-p="${pi}"][data-o="${oi}"][data-f="id"]`)?.focus();return true;}
  function ensureDialog(){
    if(dialog)return dialog;dialog=document.createElement('dialog');dialog.id='executionBoardDialog';dialog.className='eb-dialog';document.body.append(dialog);
    dialog.addEventListener('cancel',event=>{event.preventDefault();if(observationDirty&&!confirm('Descartar a observação não salva?'))return;observationDirty=false;dialog.close();});
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
    el('ebObservationCancel').onclick=()=>{if(observationDirty&&!confirm('Descartar a observação não salva?'))return;observationDirty=false;dialog.close();};
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
  function onClick(event){
    const button=event.target.closest('button');if(!button)return;
    if(button.hasAttribute('data-eb-update-quotes')){updateFxRates();return;}
    if(button.hasAttribute('data-eb-retry-quotes')){fx.marketQuotes.retry();return;}
    if(button.hasAttribute('data-eb-observation')){observationForm();return;}
    if(button.hasAttribute('data-eb-motor')){JPWNavigation.navigateLocal('exec','motor');return;}
    if(button.hasAttribute('data-eb-account-facts')){requestLeave(()=>{
      JPWNavigation.navigateLocal('exec','accounts');const form=el('fxAccountFacts');
      const idx=model().selection.accountIndex;if(form&&Number.isInteger(idx))form.elements.accountIndex.value=String(idx);
      form?.querySelector('[name=si]')?.focus();},'Registrar observação da conta');return;}
    const parse=attr=>(button.getAttribute(attr)||'').split(':').map(Number);
    if(button.hasAttribute('data-eb-save-row')){saveRow(...parse('data-eb-save-row'));return;}
    if(button.hasAttribute('data-eb-cancel-row')){cancelRow(...parse('data-eb-cancel-row'));return;}
    if(button.hasAttribute('data-orderhistory')){showVersions(...parse('data-orderhistory'));return;}
    if(button.hasAttribute('data-addorder')){const pi=+button.dataset.addorder;if(operationRecordFeedback(operationAddDraft(pi))){tableSignature=null;openedPhases.add(pi);render();document.querySelector(`.phase[data-phase="${pi}"] tr[data-eb-row]:last-of-type input`)?.focus();}return;}
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
    backupDrafts:()=>hasDrafts()?{rows:[...drafts.entries()],observation:observationDirty&&el('ebObservationForm')?Object.fromEntries(new FormData(el('ebObservationForm'))):null,instrumentId:instrumentChoice,selection:fx.state.operationalSelection()}:null,saveRow,cancelRow,requestLeave,guardNavigation,
    discard(){drafts.clear();expanded.clear();observationDirty=false;tableSignature=null;if(dialog?.open)dialog.close();},
    getSelection:()=>({accountId:fx.state.operationalSelection().accountId,instrumentId:instrumentChoice})};
  render();
})(globalThis);

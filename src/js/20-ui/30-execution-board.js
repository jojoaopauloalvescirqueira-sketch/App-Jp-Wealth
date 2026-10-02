// Execution Board: presentation and RAM drafts. Financial projections and all
// writes belong to the existing Forex domain. No draft is part of S or backup.
(function(root){
  'use strict';
  const fx=root.JPWForex;
  const drafts=new Map(), expanded=new Set();
  let instrumentChoice=null,tableSignature=null,leaving=false,toolChoice='matrix';
  let epoch=jpWealthPersistenceEpoch(),dialog=null,dialogReturn=null,observationDirty=false;
  const num=v=>typeof v==='number'&&Number.isFinite(v);
  const el=id=>document.getElementById(id);
  const key=(pi,oi)=>pi+':'+oi;
  const period=()=>fx.state.accountContext(fx.state.operationalSelection());
  const current=(pi,oi)=>period().value?.phases?.[pi]?.orders?.[oi];
  const draftKey=(pi,oi)=>{const s=fx.state.operationalSelection();
    return [s.accountId||'',s.periodId||'',pi+':'+oi].join('|');};
  const signature=o=>JSON.stringify(o);
  function contextLabel(scope){
    const account=(S.accounts||[]).find(a=>a.forexAccountId===scope?.accountId)||S.forex?.accountContexts?.archivedAccounts?.[scope?.accountId]?.record;
    const captured=S.forex?.accountContexts?.accounts?.[scope?.accountId]?.periods?.[scope?.periodId];
    return [account?.nome||scope?.accountId||'Conta não capturada',captured?.startedAt||'Período não capturado'].join(' · ');
  }
  const n=(v,d=2)=>num(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:d}):'Não calculável';
  const label={id:'ID interno',brokerHash:'HASH da corretora',par:'Instrumento',tipo:'Direção',role:'Papel',lote:'Lote',entry:'Entrada',sl:'Stop',tp:'Alvo',status:'Estado',result:'Resultado',costs:'Custos assinados',costBasis:'Tratamento dos custos',stopValidated:'Stop validado',amplifiesExposure:'Pendente amplia exposição',pendingActive:'Pendente ativa'};
  const numericFields=new Set(['lote','entry','sl','tp','result','costs']);
  const calcColumns=[['stopDistance','Dist. SL'],['stopPercent','SL %'],['targetDistance','Dist. TP'],['targetPercent','TP %'],['rewardRisk','Retorno / risco'],['atrMultiple','ATR Multiple'],['rootOne','Raiz-N 1s %'],['rootTwo','Raiz-N 2s %']];
  const tableColumns=['ID interno','HASH corretora','Instrumento','Direção','Papel','Lote','Entrada','Stop Loss','Take Profit',...calcColumns.map(x=>x[1]),'Risco nominal','Risco % saldo','Resultado','Custos','Custos no resultado?','SL validado','Estado','Ações'];
  const columnWidths=[124,160,112,94,108,86,100,100,100,94,84,94,84,88,90,105,105,130,95,120,110,158,86,112,126];
  const workbookCalcs=[calcColumns[4],...calcColumns.slice(0,4),...calcColumns.slice(5)];
  const workbookColumns=['ID interno','Instrumento','Direção','Papel','Lote','Entrada','Stop Loss','Take Profit',...workbookCalcs.map(x=>x[1]),'Risco confirmado','Risco % saldo','Estado','Ações'];
  const workbookWidths=[124,112,90,104,90,104,104,104,86,96,82,96,82,96,104,104,130,98,112,188];
  function visibleOrders(phase,pi){
    return (phase.orders||[]).map((order,oi)=>({order,oi})).filter(({order:o,oi})=>
      drafts.has(draftKey(pi,oi))||!!o.recordStatus||!!o.orderId||
      ['id','par','brokerHash','status','role'].some(f=>typeof o[f]==='string'&&o[f].trim())||
      ['lote','entry','sl','tp'].some(f=>num(o[f])&&o[f]!==0)||
      ['result','costs'].some(f=>o[f]!==null&&o[f]!==undefined));
  }
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
    grid.classList.add('execution-board','execution-workbook');
    const header=document.createElement('div');header.id='executionBoard';header.className='eb-heading';
    header.innerHTML='<div class="eb-heading-main"><div><p class="eb-eyebrow">FOREX · REGISTRO OPERACIONAL</p><h2>Operação</h2><p id="ebOperationIdentity"></p></div><div class="eb-heading-controls"><div id="ebChecklistHost"></div></div></div>';
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
      if(id==='execClearanceCard'){
        const next=document.createElement('div');next.id='ebNextAction';next.className='fx-next-action';next.setAttribute('role','status');card.append(next);
      }
      const host=document.createElement('div');host.id=region;card.append(host);
      if(id==='execConsolidadoCard'){
        const actions=legacy.querySelector('.lifo-actions');if(actions){actions.classList.add('eb-actions');card.append(actions);}
      }
    }
    const oldExtra=grid.querySelector('[data-layout-card="exec-metrics-banners"]');
    if(oldExtra){oldExtra.classList.add('eb-legacy-metrics');oldExtra.hidden=true;}
    const phaseCard=el('execPhaseGridsCard');if(phaseCard){phaseCard.classList.add('eb-card');const title=phaseCard.querySelector('h2');if(title)title.textContent='Execution Board';const nav=document.createElement('nav');nav.id='ebPhaseNav';nav.setAttribute('aria-label','Ir para a fase da ordem');el('phaseContainer').before(nav);}
    // These are the existing widget nodes, with their listeners and preferences.
    // The operational reading order is shared by visual and keyboard navigation.
    for(const id of ['execClearanceCard','execConsolidadoCard','execLifoMonitor','execPhaseGridsCard']){
      const card=el(id);if(card)grid.append(card);
    }
    if(typeof ResizeObserver==='function'&&phaseCard){
      new ResizeObserver(entries=>{const width=entries[0]?.contentRect?.width;
        if(num(width))phaseCard.style.setProperty('--eb-detail-width',Math.max(0,width)+'px');
      }).observe(phaseCard);
    }
    grid.addEventListener('click',onClick);
    el('phaseContainer').addEventListener('input',onInput);
    el('phaseContainer').addEventListener('change',onInput);
    el('phaseContainer').addEventListener('toggle',event=>{
      const node=event.target;
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
    const selectedPeriod=period().value;
    const dateLabel=selectedPeriod?.startedAt||'Período pendente';
    updateHTML('ebNextAction',`<strong>${m.executionEligibility?.status==='OK'?'Elegibilidade informada pelo motor': 'Execução normativa bloqueada'}</strong><span>${!m.scope?.periodId?'Selecione a conta e confirme um período em Contas e Período.':m.canRecord?'O registro factual está disponível. Revise os dados e salve cada linha explicitamente.':'Registro indisponível nesta versão. Preserve a base.'}${m.executionEligibility?.reason?`<small>${esc(m.executionEligibility.reason)}</small>`:''}</span><button type="button" data-eb-parameters>Ver motivos e parâmetros</button>`);
    updateHTML('executionBoardAccount',`<div class="eb-section-head"><div><p class="eb-eyebrow">CONTA E PERÍODO</p><h3>${esc(account.name||m.selection?.accountId||'Selecione uma conta')}</h3></div><button type="button" class="reset-btn" data-eb-manage>Gerenciar em Contas e Período</button></div><div class="eb-capital-strip">${metric('Capital de referência · SI',capital.si,{id:'referenceCapital'})}${metric('Saldo atual registrado',capital.book)}${metric('Equity observada',capital.equity)}${metric('Drawdown',capital.drawdown)}</div><p class="eb-context-line">${esc([account.platform,account.login,m.scope?.currency].filter(Boolean).join(' · '))} · Período desde ${esc(dateLabel)} · ${esc(profileName)} · Fase da conta: ${esc(fx.policy.phases[(risk.accountPhase?.value||0)-1]?.name||(risk.accountPhase?.compulsoryClose?'Encerramento compulsório':'Não calculável'))}</p>`);
    updateHTML('executionBoardRisk',`<div class="eb-section-head"><div><p class="eb-eyebrow">RESUMO OPERACIONAL</p><h3>Exposição da conta</h3></div><span class="eb-confirmed">Registros confirmados</span></div><div class="eb-operational-strip">${metric('Hard Stop · Equity Protector',capital.stopoutEquity,{id:'hardStop',note:'Piso de equity: SI × 78% + movimentações conciliadas. Limite de 22%; não aciona a corretora.'})}${metric('Total Exposure · Exposição total',op.exposure,{id:'totalExposure',note:'Risco até o stop das ordens abertas. Percentual sobre o saldo atual registrado.'})}${metric('Compensed Exposure · Compensada',op.compensated,{id:'compensedExposure',note:'Exposição total menos resultado líquido realizado das defesas. Perdas aumentam a exposição.'})}${metric('Alavancagem utilizada',op.leverage,{id:'usedLeverage',note:'Nocional bruto das posições abertas ÷ saldo atual registrado.'})}</div><details class="eb-findings"><summary>Ver bases de cálculo e proteções</summary><p>O resumo usa o saldo contábil registrado deste período. Atualize a Contabilidade quando houver novos lançamentos; saldo e equity são informações diferentes.</p><div class="eb-metrics">${metric('Saldo inicial do período',capital.si)}${metric('Nocional bruto',op.grossNotional)}${metric('Pendentes ampliadoras',risk.pending)}${metric('Alavancagem normativa',risk.leverage,{note:'Base normativa: menor valor entre saldo inicial e equity.'})}${metric('Risco comprometido',risk.committed)}${metric('Capacidade prudencial',risk.prudentialRemaining)}</div><p>A compensação econômica não amplia os limites normativos. Registrar fatos não autoriza execução.</p><ul>${(m.findings||[]).map(f=>`<li>${esc(f.message||f.reason||f.code||String(f))}</li>`).join('')}</ul><div class="eb-actions"><button type="button" class="reset-btn" data-eb-motor>Ver dimensionamento</button><button type="button" class="reset-btn" data-eb-parameters>Ver parâmetros</button></div></details>`);
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
    if(!el('ebTools')){
      el('executionBoardInstruments').innerHTML='<section id="ebTools" aria-label="Ferramentas da operação"><div class="eb-section-head"><h3>Ferramentas da operação</h3><div class="eb-tool-tabs" role="tablist" aria-label="Ferramenta">'+[['matrix','Matriz Hexafásica','ebToolMatrix'],['rootn','Raiz N','ebToolRootN'],['motor','Motor de Lote','ebToolMotor']].map(([k,t,id])=>`<button type="button" role="tab" id="ebToolTab-${k}" data-eb-tool="${k}" aria-controls="${id}" aria-selected="false" tabindex="-1">${t}</button>`).join('')+'</div></div><div class="eb-tool-toolbar"><label>Instrumento<select id="ebInstrumentSelect" aria-label="Instrumento das ferramentas"></select></label><div class="eb-actions"><button type="button" class="reset-btn" data-eb-observation>Preço / ATR</button><button type="button" class="reset-btn" data-eb-update-quotes>Atualizar referência diária</button><button type="button" class="reset-btn" data-eb-retry-quotes hidden>Repetir gravação</button></div><p id="ebQuoteStatus" role="status"></p></div>'+[['matrix','ebToolMatrix'],['rootn','ebToolRootN'],['motor','ebToolMotor']].map(([k,id])=>`<div id="${id}" class="eb-tool-panel" role="tabpanel" aria-labelledby="ebToolTab-${k}" hidden inert></div>`).join('')+'</section>';
      el('ebInstrumentSelect').onchange=()=>{instrumentChoice=el('ebInstrumentSelect').value;renderInstruments(model());};
      el('ebTools').querySelector('[role="tablist"]').addEventListener('keydown',event=>{
        const keys=['matrix','rootn','motor'],index=keys.indexOf(event.target.dataset.ebTool);if(index<0)return;
        let next;if(event.key==='ArrowRight')next=keys[(index+1)%keys.length];
        if(event.key==='ArrowLeft')next=keys[(index+keys.length-1)%keys.length];
        if(event.key==='Home')next=keys[0];if(event.key==='End')next=keys.at(-1);
        if(next){event.preventDefault();openTool(next);}
      });
    }
    const select=el('ebInstrumentSelect'),options=instruments.map(i=>`<option value="${esc(i.id)}">${esc(i.name)}</option>`).join('');
    if(select.innerHTML!==options)select.innerHTML=options;select.value=instrumentChoice||'';
    el('ebQuoteStatus').textContent=fx.marketQuotes?.get()?.message||'Referência diária; não é preço de execução.';
    el('ebTools').querySelector('[data-eb-retry-quotes]').hidden=!fx.marketQuotes?.get()?.canRetry;
    const cell=(value)=>`<span>${esc(format(value))}</span>${!num(value?.value)?`<small>${esc(reason(value))}</small>`:''}`;
    const conduct={FORBIDDEN:'Vedada',CONDITIONAL:'Condicional',RESTRICTED:'Restrita',DECLARED_ZONES_ONLY:'Zonas declaradas'};
    const accountPhase=m.risk?.accountPhase;
    const ddRange=p=>`${n(p.ddMinPercent)}% ${p.id===fx.policy.phases[0]?.id?'≤':'<'} DD ${p.id===fx.policy.phases.at(-1)?.id?'<':'≤'} ${n(p.ddMaxPercent)}%`;
    updateHTML('ebToolMatrix',`<table class="eb-tool-table eb-matrix-table"><caption>Matriz de referência · ${esc(fx.policy.statuteVersion)} · fase da conta ${esc(num(accountPhase?.value)?fx.policy.phases.find(p=>p.id===accountPhase.value)?.name||'não identificada':'não calculável')}</caption><thead><tr><th>Fase</th><th>Drawdown</th><th>Teto de alavancagem</th><th>Ampliação</th><th>Defesa</th></tr></thead><tbody>${fx.policy.phases.map(p=>`<tr ${p.id===accountPhase?.value?'class="eb-current-phase" aria-current="true"':''}><th scope="row">${esc(p.name)}${p.id===accountPhase?.value?'<small>Fase atual da conta</small>':''}</th><td data-label="Drawdown">${esc(ddRange(p))}</td><td data-label="Teto de alavancagem">${esc(n(p.maxLeverage))}×</td><td data-label="Ampliação">${esc(conduct[p.amplification]||p.amplification||'Não informado')}</td><td data-label="Defesa">${esc(conduct[p.defense]||p.defense||'Não informado')}</td></tr>`).join('')}</tbody></table><p class="eb-tool-note">Fonte: ${esc(fx.policy.get('P-01')?.hostNorm||'Fonte das fases indisponível')} · ${esc(fx.policy.get('P-02')?.hostNorm||'Fonte dos tetos indisponível')}. A faixa de drawdown não é orçamento de stops. Fase da conta e fase de registro são distintas.</p><button type="button" class="reset-btn" data-eb-parameters>Ver parâmetros e pendências</button>`);
    updateHTML('ebToolRootN',`<table class="eb-tool-table"><caption>Raiz N · ${esc(item.name||'selecione um instrumento')} · cenários declarados em H4</caption><thead><tr><th>Horizonte</th><th>N · candles H4</th><th>F · fator</th><th>Distância em preço</th></tr></thead><tbody>${[['oneWeek','1 semana'],['twoWeeks','2 semanas']].map(([h,t])=>{const d=item.rootN?.[h];return `<tr><th scope="row">${t}</th><td data-label="N · candles H4">${esc(num(d?.n)?n(d.n):'Não declarado')}</td><td data-label="F · fator">${esc(num(d?.f)?n(d.f,4):'Não declarado')}</td><td data-label="Distância em preço">${cell(d)}</td></tr>`;}).join('')}</tbody></table><div class="eb-tool-references">${metric('ATR55 H4 · preço',{value:item.atr?.short,unit:'PRICE',reason:'ATR55 H4 não observado.'})}${metric('ATR660 H4 · preço',{value:item.atr?.long,unit:'PRICE',reason:'ATR660 H4 não observado.'})}${metric('VRM',item.vrm)}</div><div class="eb-actions"><button type="button" class="reset-btn" data-eb-diagnostics>Declarar N / F</button></div><p class="eb-tool-note">${esc(item.atr?.source||'ATR sem origem declarada')} · ${esc(item.atr?.observedAt||'horário não informado')}. ${esc(item.diagnostics?.declaredAt?'Cenários declarados em '+item.diagnostics.declaredAt:'N e F ainda não declarados.')} Diagnóstico não modifica o stop nem autoriza lote. O percentual da grade usa a entrada de cada linha.</p>`);
    const lotCell=(id,metricValue)=>`<div data-eb-metric="${id}" data-eb-lot-reference="${id.replace(/[A-Z]/g,c=>'-'+c.toLowerCase())}">${cell(metricValue)}<small>${num(metricValue?.baseValue)?'Base '+esc(fmtForexMoney(metricValue.baseValue,{currency:m.scope?.currency},2)):'Base não calculável'} · ${num(metricValue?.multiple)?'fator '+esc(n(metricValue.multiple,4))+'×':'fator não informado'}</small><small>${esc(provenance(metricValue)||'Origem não identificada')}</small><small>Memória: base × fator ÷ ${esc(format(item.notionalPerLot))} por lote.</small></div>`;
    updateHTML('ebToolMotor',`<table class="eb-tool-table eb-motor-table"><caption>Motor de Lote · ${esc(item.name||'selecione um instrumento')} · referências teóricas</caption><thead><tr><th>Regime</th><th>Referência inicial · SI</th><th>Teto corrente · min(SI, equity)</th></tr></thead><tbody><tr><th scope="row">Normal</th><td data-label="Referência inicial · SI">${lotCell('initialNormal',item.initialNormal)}</td><td data-label="Teto corrente · min(SI, equity)">${lotCell('currentNormal',item.currentNormal)}</td></tr><tr><th scope="row">Restritivo</th><td data-label="Referência inicial · SI">${lotCell('initialRestrictive',item.initialRestrictive)}</td><td data-label="Teto corrente · min(SI, equity)">${lotCell('currentRestrictive',item.currentRestrictive)}</td></tr></tbody></table><details class="eb-findings"><summary>Bases, contrato e conversões</summary><div class="eb-tool-references">${metric('Nocional de um lote',item.notionalPerLot)}${metric('Stop mínimo normativo',item.minimumStop)}</div><p>${esc(item.contract?.source||'Contrato sem fonte')} · ${esc(item.contract?.observedAt||'horário não informado')}. ${esc(item.conversion?.source||'Conversão não observada')}.</p><p>Fonte dos fatores: ${esc(fx.policy.get('P-12b')?.hostNorm||'Não identificada')}. A referência sobre SI não substitui o teto corrente. Volume mínimo, arredondamento e elegibilidade operacional não são autorizados por esta tabela.</p></details><p class="eb-tool-note">${item.operable===false?'Instrumento com restrição normativa preservada. ':''}Nenhum resultado preenche lote, entrada ou stop. Registrar fatos não autoriza execução.</p>`);
    applyTool();
  }
  function applyTool(){
    for(const [key,id] of [['matrix','ebToolMatrix'],['rootn','ebToolRootN'],['motor','ebToolMotor']]){
      const active=key===toolChoice,panel=el(id),button=el('ebToolTab-'+key);
      if(panel){panel.hidden=!active;panel.inert=!active;}
      if(button){button.setAttribute('aria-selected',String(active));button.tabIndex=active?0:-1;}
    }
  }
  function openTool(choice){
    if(!['matrix','rootn','motor'].includes(choice))return false;
    if(!el('ebTools')){prepareShell();renderInstruments(model());}
    toolChoice=choice;applyTool();el('ebToolTab-'+choice)?.focus({preventScroll:true});
    el('ebTools')?.scrollIntoView({block:'nearest',inline:'nearest'});return true;
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
    const entry=(f,choices)=>`<label class="eb-compact-field"><span>${esc(label[f])}</span>${field(pi,oi,o,f,choices)}</label>`;
    const instruments=[['','Selecionar'],...(S.instruments||[]).map(i=>[i.name,i.name])];
    if(o.par&&!instruments.some(([x])=>x===o.par))instruments.push([o.par,o.par+' · não cadastrado']);
    return `<tr class="eb-order-row ${draft?'eb-dirty':''}" data-eb-row="${k}">
      <td class="eb-order-id" data-label="Ordem">${field(pi,oi,o,'id')}<small data-eb-preview="${k}">${draft?'Prévia · não salva':esc(o.recordStatus==='voided'?'Anulada':!fx.state.supported()?'Somente leitura':o.recordStatus==='draft'||!o.status?'Rascunho':'Confirmada')}</small></td>
      <td class="eb-order-instrument" data-label="Instrumento">${field(pi,oi,o,'par',instruments)}</td>
      <td data-label="Direção">${field(pi,oi,o,'tipo',[['BUY','Compra'],['SELL','Venda']])}</td>
      <td data-label="Papel">${field(pi,oi,o,'role',[['','Não declarado'],['GENESIS','Gênese'],['DEFENSE','Defesa'],['OTHER','Outro']])}</td>
      ${['lote','entry','sl','tp'].map(f=>`<td data-label="${esc(label[f])}">${field(pi,oi,o,f)}</td>`).join('')}
      ${workbookCalcs.map(([f,t],index)=>`<td class="eb-number eb-calculated" data-label="${esc(t)}"><span data-eb-calc="${f}">—</span>${index===0?`<small data-eb-diagnostic-state="${k}">${draft?'Prévia não salva':'Versão salva'}</small>`:''}</td>`).join('')}
      <td class="eb-number eb-calculated eb-confirmed-risk" data-label="Risco confirmado"><span data-eb-row-risk="${k}" data-eb-calc="riskValue">—</span><small data-eb-risk-state="${k}">${draft?'Versão salva · anterior à edição':'Versão salva'}</small></td>
      <td class="eb-number eb-calculated eb-confirmed-risk" data-label="Risco % saldo"><span data-eb-calc="riskPercent">—</span><small>Saldo registrado</small></td>
      <td data-label="Estado">${field(pi,oi,o,'status',[['','Rascunho'],['Pendente','Pendente'],['Aberta','Aberta'],['Fechada','Fechada'],...(o.status==='Migrada'?[['Migrada','Migrada']]:[])])}</td>
      <td class="eb-row-actions" data-label="Ações"><button type="button" data-eb-save-row="${k}" ${readonly?'disabled':''}>Salvar linha</button><button type="button" data-eb-cancel-row="${k}" ${readonly?'disabled':''}>Cancelar</button><button type="button" data-eb-open-detail="${k}" aria-controls="ebDetail-${pi}-${oi}">Detalhes</button></td></tr>
      <tr class="eb-detail-row"><td colspan="20"><div class="eb-detail-content"><details id="ebDetail-${pi}-${oi}" data-eb-detail="${k}" ${expanded.has(k)||draft?.error?'open':''}><summary>HASH, resultado, custos e rastreabilidade${draft?' · alterações não salvas':''}</summary><div class="eb-order-details">${entry('brokerHash')}${entry('result')}${entry('costs')}${entry('costBasis',[['','Não declarado'],['SEPARATE_FROM_RESULT','Separados'],['INCLUDED_IN_RESULT','Já incluídos']])}${['stopValidated','amplifiesExposure','pendingActive'].map(f=>`<label class="eb-check">${field(pi,oi,o,f)}${esc(label[f])}</label>`).join('')}<label class="eb-reason">${live?'Motivo da correção (obrigatório ao salvar)':'Observação do registro (opcional)'}<input type="text" data-eb-reason="${k}" value="${esc(draft?.reason||'')}" ${readonly?'disabled':''}></label></div><p class="eb-context-line" title="${esc([o.accountId,o.periodId,o.orderId].filter(Boolean).join(' · '))}">${esc(contextLabel(o))} · ${esc(o.currency||'moeda não capturada')} · versão ${esc(o.recordVersion??0)} · referência técnica ${esc(o.orderId||'a gerar')}</p><div class="eb-actions">${!readonly?`<button type="button" class="reset-btn" data-eb-close-row="${k}">Fechar ordem</button><button type="button" class="reset-btn" data-delorder="${k}">${live?'Anular com motivo':'Excluir rascunho'}</button>`:''}${o.revisions?.length?`<button type="button" class="reset-btn" data-orderhistory="${k}">Ver ${o.revisions.length} versão(ões)</button>`:''}</div></details><p id="ebError-${pi}-${oi}" class="eb-row-feedback" role="status">${esc(draft?.error||'')}</p></div></td></tr>`;
  }
  // Full audit is read-only confirmed data from the same projection. Inputs
  // exist only once, in the compact table and its detail, on every viewport.
  function auditHTML(m,phaseList){
    return '<details class="eb-full-audit"><summary>Tabela completa · auditoria dos registros confirmados</summary><p>Rascunhos não integram os totais confirmados. Use os detalhes da ordem para editar.</p><div class="eb-table-scroll" tabindex="0" role="region" aria-label="Auditoria completa das ordens"><table class="eb-audit-table"><colgroup>'+columnWidths.map(w=>'<col style="width:'+w+'px">').join('')+'</colgroup><thead><tr>'+tableColumns.map(t=>'<th scope="col">'+esc(t)+'</th>').join('')+'</tr></thead><tbody>'+phaseList.flatMap((p,pi)=>(p.orders||[]).flatMap((o,oi)=>{
      // Confirmed audit reads saved facts only, including annulled revisions.
      // Anonymous template slots and explicit drafts are never confirmed rows.
      const confirmed=o.recordStatus!=='draft'&&(['recorded','voided'].includes(o.recordStatus)||
        num(o.recordVersion)&&o.recordVersion>0||['Aberta','Fechada','Pendente','Migrada'].includes(o.status));
      if(!confirmed)return [];
      const r=(m.displayRows||m.rows||[]).find(x=>x.pi===pi&&x.oi===oi),geometry=r?.geometry||{};
      const calculated={...geometry,atrMultiple:r?.atrMultiple,rootOne:{value:r?.rootN?.oneWeek?.percent,unit:'PERCENT'},rootTwo:{value:r?.rootN?.twoWeeks?.percent,unit:'PERCENT'}};
      const values=[o.id,o.brokerHash,o.par,o.tipo,o.role,o.lote,o.entry,o.sl,o.tp,...calcColumns.map(([f])=>format(calculated[f])),format(r?.operationalRisk),format({value:r?.operationalRisk?.percent,unit:'PERCENT'}),o.result,o.costs,o.costBasis,o.stopValidated===true?'Sim':o.stopValidated===false?'Não':'Não informado',o.status||'Rascunho','Detalhes na ordem'];
      return '<tr>'+values.map(v=>'<td>'+esc(v??'—')+'</td>').join('')+'</tr>';
    })).join('')+'</tbody></table></div></details>';
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
    const badge=node.querySelector('[data-eb-preview]');if(draft&&badge)badge.textContent='Prévia · não salva';
    const diagnosticState=node.querySelector('[data-eb-diagnostic-state]');if(diagnosticState)diagnosticState.textContent=draft?'Prévia não salva':'Versão salva';
    const riskState=node.querySelector('[data-eb-risk-state]');if(riskState)riskState.textContent=draft?'Versão salva · anterior à edição':'Versão salva';
  }
  function renderPhases(m){
    if(!fx.executionBoard)return;
    m=m||model();const container=el('phaseContainer');if(!container)return;
    const recordedPhases=period().value?.phases||[],hasContext=recordedPhases.length>0;
    const phaseList=hasContext?recordedPhases:fx.policy.phases.map(p=>({faseNome:p.name,orders:[]}));
    const phaseNames=phaseList.map((p,pi)=>recordedPhases.length===4||p.policyVersion==='LEGACY_UNRESOLVED'?
      m.phases?.find(x=>x.index===pi)?.name||'LEGACY '+(pi+1):fx.policy.phases[pi]?.name||p.faseNome);
    updateHTML('ebPhaseNav','<span>Fases e ordens</span>'+phaseNames.map((name,pi)=>`<button type="button" data-eb-phase-jump="${pi}" aria-controls="ebPhase-${pi}">${esc(name)}</button>`).join(''));
    const next=JSON.stringify({scope:fx.state.operationalSelection(),supported:fx.state.supported(),hasContext,phases:phaseList.map(p=>({name:p.faseNome,policy:p.policyVersion,orders:p.orders}))});
    // Quote/account repaints update numbers only. Live input nodes and cursor stay mounted.
    const firstTable=!container.querySelector('.eb-workbook-table');
    if(next!==tableSignature||firstTable){
      const focus=document.activeElement,focusKey=focus?.dataset?.f?{p:focus.dataset.p,o:focus.dataset.o,f:focus.dataset.f,start:focus.selectionStart,end:focus.selectionEnd}:null;
      const scroll=el('ebOrderScroll'),scrollPosition=scroll?{left:scroll.scrollLeft,top:scroll.scrollTop}:null;
      container.innerHTML=`${!hasContext?'<div class="eb-setup-prompt"><h3>Prepare a conta para registrar suas ordens</h3><p>Confirme conta, período, moeda e capital inicial (SI). O saldo do relatório não substitui o SI.</p><button type="button" data-eb-manage>Gerenciar em Contas e Período</button></div>':''}<p class="eb-context-line">${recordedPhases.length===4?'Grades LEGACY preservadas; os quatro índices não correspondem às seis fases V11.':'Fase de registro da ordem e fase da conta são informações distintas.'} Totais e risco usam a versão salva.</p><details class="eb-table-help"><summary>Como preencher a grade</summary><p>Tab e Shift+Tab percorrem os campos. Diagnósticos recalculam a prévia em memória; risco e totais conservam a versão salva. Informe ID e HASH para novas ordens executadas; pendentes podem aguardar o HASH. Salvar linha confirma explicitamente os fatos. Enter nos campos não salva.</p><p>Distâncias SL/TP são unidades de preço. SL %, TP % e Raiz N % usam a entrada da linha. Custos separados são assinados: despesas negativas e créditos positivos. Correções exigem motivo; o encerramento usa Fechar ordem nos detalhes.</p></details><div id="ebOrderScroll" class="eb-table-scroll eb-workbook-scroll" tabindex="0" role="region" aria-label="Execution Board · ordens de todas as fases"><table class="otable eb-order-table eb-workbook-table"><colgroup>${workbookWidths.map((width,index)=>`<col class="eb-column-${index}" style="width:${width}px">`).join('')}</colgroup><thead><tr class="eb-column-groups"><th colspan="4" scope="colgroup">Identificação</th><th colspan="4" scope="colgroup">Execução</th><th colspan="8" scope="colgroup">Diagnósticos · prévia ao editar</th><th colspan="2" scope="colgroup">Risco · versão salva</th><th colspan="2" scope="colgroup">Acompanhamento</th></tr><tr class="eb-column-labels">${workbookColumns.map(t=>'<th scope="col">'+esc(t)+'</th>').join('')}</tr></thead>${phaseList.map((p,pi)=>`<tbody class="eb-phase-group"><tr class="eb-phase-row" data-phase="${pi}" id="ebPhase-${pi}" tabindex="-1"><th colspan="20" scope="rowgroup"><div class="eb-phase-anchor"><div class="eb-phase-label"><strong>${esc(phaseNames[pi])}</strong><span>${visibleOrders(p,pi).length} linha(s)${!hasContext?' · aguardando contexto':''}</span>${hasContext?`<button type="button" class="reset-btn" data-addorder="${pi}">+ Adicionar ordem nesta fase</button>`:''}</div><div id="ebPhaseDiagnostics-${pi}" class="eb-phase-diagnostics"></div></div></th></tr>${visibleOrders(p,pi).length?visibleOrders(p,pi).map(({order:o,oi})=>rowHTML(pi,oi,o)).join(''):`<tr class="eb-empty-phase"><td colspan="20"><span>${hasContext?'Nenhuma ordem registrada.':'Confirme a conta e o período para registrar ordens.'}</span></td></tr>`}</tbody>`).join('')}</table></div><div id="ebAuditHost"></div><details class="eb-phase-consolidation"><summary>Consolidação por fase · registros confirmados</summary><div id="ebPhaseSummary" class="eb-table-scroll"></div></details>`;
      tableSignature=next;
      if(scrollPosition){el('ebOrderScroll').scrollLeft=scrollPosition.left;el('ebOrderScroll').scrollTop=scrollPosition.top;}
      if(focusKey){const target=container.querySelector(`[data-p="${focusKey.p}"][data-o="${focusKey.o}"][data-f="${focusKey.f}"]`);target?.focus();if(target?.setSelectionRange&&focusKey.start!=null)target.setSelectionRange(focusKey.start,focusKey.end);}
    }
    updateHTML('ebAuditHost',auditHTML(m,phaseList));
    updateHTML('ebPhaseSummary','<table class="eb-summary-table"><caption>Consolidação por fase · moeda da conta</caption><thead><tr><th>Fase</th><th>Volumes por instrumento</th><th>Nocional</th><th>Risco aberto</th><th>Pendentes</th><th>Resultado líquido</th><th>Custos</th><th>Compensada · defesas</th></tr></thead><tbody>'+(m.phases||[]).map(p=>{const v=p.metrics||{};return `<tr><th>${esc(p.name||p.id)}</th><td>${esc(p.volumeText||(p.instruments||[]).map(i=>[i.name||i.instrumentId,format(i.metrics?.lots)].join(' ')).join(' · ')||'—')}</td><td>${esc(format(v.operational?.grossNotional))}</td><td>${esc(format(v.operational?.exposure))}</td><td>${esc(format(v.pending||v.pendingRisk))}</td><td>${esc(format(v.closedNetAll||v.realized))}</td><td>${esc(format(v.costs))}</td><td>${esc(format(v.operational?.compensated))}</td></tr>`;}).join('')+'</tbody></table>');
    for(const phase of m.phases||[]){
      const instruments=(phase.instruments||[]).map(i=>m.instruments.find(x=>x.id===i.id)).filter(Boolean);
      updateHTML('ebPhaseDiagnostics-'+phase.index,`<details class="eb-findings"><summary>Bases e diagnósticos desta fase</summary><div class="eb-metrics">${metric('Lucro Técnico',phase.technicalProfit)}${metric('Margem normativa',phase.freeNormativeMargin)}${instruments.map(i=>metric('VRM · '+i.name,i.vrm)+metric('Stop mínimo · '+i.name,i.minimumStop)).join('')}</div><p>Dados por instrumento; sem VRM médio artificial. Compensação econômica não é reposição normativa de margem.</p></details>`);
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
      if(phase){const scroll=el('ebOrderScroll');if(scroll)scroll.scrollTop=Math.max(0,phase.offsetTop-90);phase.scrollIntoView({block:'nearest',inline:'nearest'});phase.focus({preventScroll:true});}return;
    }
    if(button.hasAttribute('data-eb-tool')){openTool(button.dataset.ebTool);return;}
    if(button.hasAttribute('data-eb-update-quotes')){updateFxRates();return;}
    if(button.hasAttribute('data-eb-retry-quotes')){fx.marketQuotes.retry();return;}
    if(button.hasAttribute('data-eb-observation')){observationForm();return;}
    if(button.hasAttribute('data-eb-diagnostics')){diagnosticForm();return;}
    if(button.hasAttribute('data-eb-open-detail')){const [pi,oi]=(button.dataset.ebOpenDetail||'').split(':').map(Number),detail=el(`ebDetail-${pi}-${oi}`);if(detail){detail.open=true;expanded.add(key(pi,oi));detail.querySelector('summary')?.focus({preventScroll:true});}return;}
    if(button.hasAttribute('data-eb-parameters')){JPWNavigation.navigate('params');return;}
    if(button.hasAttribute('data-eb-motor')){openTool('motor');return;}
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
    if(button.hasAttribute('data-addorder')){const pi=+button.dataset.addorder;if(operationRecordFeedback(operationAddDraft(pi))){tableSignature=null;render();[...el('phaseContainer').querySelectorAll(`tr[data-eb-row^="${pi}:"]`)].at(-1)?.querySelector('input')?.focus();}return;}
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
  fx.executionBoardUI={render,renderPhases,hasDrafts,openTool,
    backupDrafts:()=>hasDrafts()?{rows:[...drafts.entries()],observation:observationDirty&&el('ebObservationForm')?Object.fromEntries(new FormData(el('ebObservationForm'))):null,diagnostics:observationDirty&&el('ebDiagnosticForm')?Object.fromEntries(new FormData(el('ebDiagnosticForm'))):null,instrumentId:instrumentChoice,selection:fx.state.operationalSelection()}:null,saveRow,cancelRow,requestLeave,guardNavigation,
    discard(){drafts.clear();expanded.clear();observationDirty=false;tableSignature=null;if(dialog?.open)dialog.close();},
    getSelection:()=>({accountId:fx.state.operationalSelection().accountId,instrumentId:instrumentChoice})};
  render();
})(globalThis);

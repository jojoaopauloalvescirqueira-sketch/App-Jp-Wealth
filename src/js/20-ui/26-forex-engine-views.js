// Forex views: explicit fact commands and a read-only projection of one engine.
// Forms keep their session drafts through navigation. They never save on input.
(function(root){
  'use strict';
  const fx=root.JPWForex, el=id=>document.getElementById(id), safe=v=>esc(String(v==null?'—':v));
  const number=v=>typeof v==='number'&&Number.isFinite(v)?v.toLocaleString('pt-BR',{maximumFractionDigits:4}):'Não calculável';
  const field=(name,label,type='text',extra='')=>`<label class="fx-engine-field">${label}<input name="${name}" type="${type}" ${type==='number'?'step="any"':''} ${extra}></label>`;
  const check=(name,label)=>`<label class="fx-engine-check"><input type="checkbox" name="${name}">${label}</label>`;
  const reason=()=>field('reason','Motivo do registro','text','required maxlength="500"');
  const source=()=>field('source','Fonte / referência da informação','text','required maxlength="500"');
  const button=(label,extra='')=>`<button type="submit" ${extra}>${label}</button>`;
  const response=()=>'<p class="fx-engine-response" role="status" aria-live="polite"></p>';
  const nullable=(form,name)=>{const v=form.elements.namedItem(name).value.trim();return v===''?null:Number(v);};
  const str=(form,name)=>form.elements.namedItem(name).value.trim();
  const checked=(form,name)=>form.elements.namedItem(name).checked;
  const timestamp=(form,name)=>{const v=str(form,name);return v?new Date(v).toISOString():null;};
  let initialized=false,stateIdentity=null;
  function mount(){
    if(initialized)return;initialized=true;stateIdentity=S;
    el('forexEnginePanel').innerHTML=`<header><span class="cp-kicker">REGISTRO E ELEGIBILIDADE</span><h2>Motor central Forex</h2><p>Registrar um fato não autoriza sua execução. Dados ausentes e parâmetros pendentes permanecem identificados.</p></header>
      <div id="fxEngineState" class="fx-engine-status"></div>
      <details open><summary>Conta de referência e equity</summary><p>O saldo contábil permanece no ledger. Registre aqui uma observação de equity flutuante, SI e moeda, com sua fonte.</p>
      <form id="fxAccountFacts" class="fx-engine-form">
        <label class="fx-engine-field">Conta cadastrada<select name="accountIndex" required></select></label>
        ${field('si','SI fixo do período','number','required min="0.000001"')}${field('equity','Equity flutuante observado','number','required')}
        <label class="fx-engine-field">Moeda dos valores<select name="currency">${['USD','BRL','EUR','GBP','JPY','CHF','CAD','AUD','NZD'].map(c=>`<option>${c}</option>`).join('')}</select></label>
        ${field('usdToAccountRate','Conversão de 1 USD na moeda da conta (se necessária)','number','min="0.000001"')}
        ${field('capitalNominal','Capital nominal da Mestre, se conhecido','number','min="0"')}
        ${field('netCashflow','Aportes líquidos desde o SI (informe 0 quando confirmado)','number')}
        ${check('cashflowAdjustmentRecorded','Ajuste de aportes/retiradas documentado')}
        ${field('marginLevel','Nível de margem informado (%)','number','min="0"')}
        ${field('observedAt','Instante da observação','datetime-local','required')}${source()}${reason()}
        ${check('newPeriod','Registrar novo período — necessário para mudar SI ou moeda')}
        <div class="fx-engine-actions">${button('Registrar observação')}<button type="button" data-fx-load-account>Carregar observação atual</button><button type="button" data-fx-route="forex-account">Abrir cadastro de contas</button></div>${response()}
      </form></details>
      <details><summary>ATR, candle H4 e grade registrada</summary>
      <form id="fxMarketFacts" class="fx-engine-form"><h3>Volatilidade</h3>${field('atrShort','ATR 55 H4, em preço','number','required min="0"')}${field('atrLong','ATR 660 H4, em preço','number','required min="0.000001"')}${field('observedAt','Instante','datetime-local','required')}${source()}${reason()}${button('Registrar ATRs')}${response()}</form>
      <form id="fxH4Facts" class="fx-engine-form"><h3>Fechamento confirmado</h3><p>O relógio do aplicativo não confirma candles. Use uma fonte verificável para o DD no fechamento H4 da conta selecionada.</p>${field('ddPercent','DD no fechamento (%)','number','required min="0"')}${field('closedAt','Fechamento H4 já ocorrido','datetime-local','required')}${source()}${reason()}${button('Registrar fechamento H4')}${response()}</form>
      <form id="fxGridFacts" class="fx-engine-form"><h3>Estrutura efetiva da operação</h3><label class="fx-engine-field">Fase da grade<select name="phase">${fx.policy.phases.map(p=>`<option value="${p.number}">Fase ${p.number}</option>`).join('')}</select></label>${reason()}${button('Registrar fase da grade')}${response()}<p>Não recompõe poda nem eleva o limite da fase da conta.</p></form></details>
      <details><summary>Orçamento declarado da operação</summary><p>Declaração factual específica. Registrar antes da primeira ordem no software não prova execução anterior no mercado. O orçamento não autoriza execução e não pode ser ampliado.</p><p id="fxBudgetContext"></p><form id="fxOperationBudget" class="fx-engine-form">${field('amount','Orçamento total na moeda indicada','number','required min="0"')}${field('declaredBy','Declarante informado','text','required maxlength="120"')}${field('declaredAt','Instante declarado','datetime-local','required')}${source()}${reason()}${button('Registrar orçamento ou redução')}${response()}<p>Uma redução exige risco comprometido conhecido e não superior ao novo valor. O valor anterior e a origem permanecem na trilha.</p></form><div id="fxBudgetHistory"></div></details>
      <details><summary>Catálogo normativo e metadados</summary><p id="fxPolicyIdentity"></p><div class="fx-engine-table-scroll"><table class="dtable"><thead><tr><th>Parâmetro</th><th>Valor / unidade</th><th>Estado</th><th>Fonte, autoridade e vigência</th></tr></thead><tbody id="fxRegistryRows"></tbody></table></div></details>
      <details><summary>Editor local — propostas de calibração</summary><p>A proteção abaixo existe apenas nesta sessão e pode ser contornada por quem controla o navegador. Não é autenticação online nem comprovação de autoridade normativa. Propostas não alteram a política vigente.</p>
      <p id="fxEditorState" role="status"></p>
      <form id="fxEditorConfigure" class="fx-engine-form">${field('phrase','Defina uma frase temporária própria','password','required minlength="12" autocomplete="new-password"')}${button('Configurar proteção temporária')}${response()}</form>
      <form id="fxEditorUnlock" class="fx-engine-form">${field('editor','Identificação declarada do editor','text','required maxlength="120"')}${field('phrase','Frase temporária','password','required autocomplete="off"')}${button('Desbloquear por cinco minutos')}${response()}</form>
      <form id="fxParameterProposal" class="fx-engine-form"><label class="fx-engine-field">Parâmetro<select name="id">${fx.policy.list().filter(p=>p.id).map(p=>`<option value="${safe(p.id)}">${safe(p.id)} · ${safe(p.name||p.label||p.id)}</option>`).join('')}</select></label>${field('value','Valor proposto','number','required')}${source()}${reason()}${button('Registrar proposta')}<button type="button" data-fx-lock>Bloquear editor</button>${response()}</form>
      <div id="fxProposals"></div></details>`;
    el('forexReservesPanel').innerHTML=`<header><span class="cp-kicker">FOREX · GOVERNANÇA PATRIMONIAL</span><h1>Reservas</h1><p>FCR e FEO têm finalidades e requisitos distintos. A apuração registrada não substitui a verificação de liquidez, constituição e autorização.</p></header><div id="fxReserveSummary" class="fx-engine-cards"></div>
      <details open><summary>Registrar constituição e apuração</summary><form id="fxReserveFacts" class="fx-engine-form">
      ${field('capitalNominal','Capital nominal da conta Mestre','number','min="0"')}${field('fcrConstituted','FCR constituído','number','min="0"')}${field('feoConstituted','FEO constituído','number','min="0"')}
      ${field('sixMonthExpenseAmount','Despesas reais apuradas para seis meses','number','min="0"')}${field('expensePeriod','Período coberto pela apuração')}${field('determinationReference','Referência do método/documento de apuração')}
      ${check('determinationRecorded','Apuração documentada')}${check('expensesApproved','Despesas elegíveis aprovadas')}
      ${field('fcrLiquidityDays','Liquidez FCR (dias)','number','min="0"')}${field('feoLiquidityDays','Liquidez FEO (dias)','number','min="0"')}${field('verifiedAt','Instante da verificação','datetime-local')}${check('verificationRecorded','Verificação de constituição e liquidez registrada')}${source()}${reason()}
      ${button('Registrar reservas')}${response()}<p>Valores na moeda da conta selecionada. Deixe em branco o que não foi apurado. Não usar SI como capital nominal nem uma taxa histórica como FEO.</p></form></details><details><summary>Trilha de reservas</summary><div id="fxReserveHistory"></div></details>`;
    document.addEventListener('submit',submit);
    document.addEventListener('click',click);
    render();
  }
  function after(form,result){
    form.querySelector('.fx-engine-response').textContent=result.ok?(result.alreadyMigrated?'Migração já registrada.':result.persistido===false?'Concluído nesta sessão.':'Registro confirmado.'):(result.error||'Registro não confirmado.');
    if(result.ok){if(typeof root.render==='function')root.render();else render();if(typeof root.JPWDashMacro==='object')root.JPWDashMacro.schedule();if(typeof renderPhases==='function')renderPhases();if(typeof renderContas==='function')renderContas();}
  }
  async function submit(event){
    const form=event.target;if(!form.id.startsWith('fx')||!el('forexEnginePanel').contains(form)&&!el('forexReservesPanel').contains(form))return;
    event.preventDefault();let result;
    try{
      const reasonValue=form.elements.namedItem('reason')?str(form,'reason'):null;
      switch(form.id){
        case 'fxAccountFacts':result=fx.state.recordAccountFacts({accountIndex:Number(str(form,'accountIndex')),si:nullable(form,'si'),equity:nullable(form,'equity'),currency:str(form,'currency'),usdToAccountRate:nullable(form,'usdToAccountRate'),capitalNominal:nullable(form,'capitalNominal'),netCashflow:nullable(form,'netCashflow'),cashflowAdjustmentRecorded:checked(form,'cashflowAdjustmentRecorded'),marginLevel:nullable(form,'marginLevel'),source:str(form,'source'),observedAt:timestamp(form,'observedAt'),newPeriod:checked(form,'newPeriod')},{reason:reasonValue});break;
        case 'fxOperationBudget':{const model=fx.state.read(),scope=model.budgetScope,budget=model.metrics.operationBudget;
          result=fx.state.recordOperationBudget({...scope,currency:model.account&&model.account.currency,budgetId:budget.declaration?.id,
            amount:nullable(form,'amount'),declaredBy:str(form,'declaredBy'),declaredAt:timestamp(form,'declaredAt'),source:str(form,'source')},{reason:reasonValue});break;}
        case 'fxMarketFacts':result=fx.state.recordMarket({atrShort:nullable(form,'atrShort'),atrLong:nullable(form,'atrLong'),observedAt:timestamp(form,'observedAt'),source:str(form,'source')},{reason:reasonValue});break;
        case 'fxH4Facts':result=fx.state.recordH4({ddPercent:nullable(form,'ddPercent'),closedAt:timestamp(form,'closedAt'),source:str(form,'source')},{reason:reasonValue});break;
        case 'fxGridFacts':result=fx.state.recordGrid(Number(str(form,'phase')),{reason:reasonValue});break;
        case 'fxReserveFacts':result=fx.state.recordReserves(Object.fromEntries([
          ...['capitalNominal','fcrConstituted','feoConstituted','sixMonthExpenseAmount','fcrLiquidityDays','feoLiquidityDays'].map(k=>[k,nullable(form,k)]),
          ...['expensePeriod','determinationReference','source'].map(k=>[k,str(form,k)]),...['determinationRecorded','expensesApproved','verificationRecorded'].map(k=>[k,checked(form,k)]),['verifiedAt',timestamp(form,'verifiedAt')]]),{reason:reasonValue});break;
        case 'fxEditorConfigure':{const phrase=str(form,'phrase');form.elements.phrase.value='';result=await fx.state.configureEditor(phrase);break;}
        case 'fxEditorUnlock':{const phrase=str(form,'phrase');form.elements.phrase.value='';result=await fx.state.unlockEditor(phrase,str(form,'editor'));break;}
        case 'fxParameterProposal':result=fx.state.proposeParameterChange({id:str(form,'id'),value:nullable(form,'value'),source:str(form,'source'),reason:reasonValue});break;
        default:return;
      }
    }catch(_){result={ok:false,error:'Entrada não processada. Confira formato e versão; preserve o rascunho.'};}
    after(form,result);
  }
  function click(event){
    const b=event.target.closest('button');if(!b)return;
    if(b.hasAttribute('data-fx-route')){navigateToScreen(b.dataset.fxRoute);return;}
    if(b.hasAttribute('data-fx-lock')){fx.state.lockEditor();render();return;}
    if(b.hasAttribute('data-fx-migrate')){
      const reasonText=prompt('Motivo da migração explícita. As grades antigas permanecem LEGACY_UNRESOLVED:');
      if(reasonText){const result=fx.state.migrateLegacy({reason:reasonText});el('fxEngineState').textContent=result.ok?'Migração registrada; histórico preservado.':result.error;render();}return;
    }
    if(b.hasAttribute('data-fx-load-account')){
      const a=fx.state.read().account,form=el('fxAccountFacts');if(!a)return;
      const idx=(S.accounts||[]).findIndex(x=>x.forexAccountId===S.forex.activeAccountId);form.elements.accountIndex.value=String(idx);
      for(const key of ['si','equity','currency','usdToAccountRate','capitalNominal','netCashflow','marginLevel','source'])form.elements.namedItem(key).value=a[key]==null?'':String(a[key]);
      form.elements.cashflowAdjustmentRecorded.checked=a.cashflowAdjustmentRecorded===true;
      const date=new Date(a.observedAt);form.elements.observedAt.value=new Date(date.getTime()-date.getTimezoneOffset()*60000).toISOString().slice(0,16);
      form.elements.newPeriod.checked=false;
    }
  }
  const metric=(name,result,suffix='')=>`<article class="fx-engine-metric"><h3>${safe(name)}</h3><strong>${typeof result.value==='number'?number(result.value)+suffix:safe(typeof result.value==='string'?result.value:result.value===null?'Não calculável':result.status)}</strong><small>${safe(result.status)}</small>${result.findings.length?`<p>${safe(result.findings[0].message)}</p>`:''}</article>`;
  function render(){
    if(!initialized)return;
    if(stateIdentity!==S){stateIdentity=S;document.querySelectorAll('#forexEnginePanel form,#forexReservesPanel form').forEach(f=>f.reset());fx.state.clearEditor();}
    const model=fx.state.read(),m=model.metrics;
    const select=el('fxAccountFacts').elements.accountIndex,selected=select.value;
    const options='<option value="">Selecione uma conta</option>'+(S.accounts||[]).map((a,i)=>`<option value="${i}">${safe(a.apelido||a.nome||a.broker||'Conta sem nome')} · ${safe(a.tipo)}</option>`).join('');
    if(select.innerHTML!==options){select.innerHTML=options;select.value=selected;}
    el('fxEngineState').innerHTML=`<strong>${safe(model.executionEligibility.status)}</strong> · ${safe(fx.policy.version)}<p>Elegibilidade e registro são independentes. Pendências não são convertidas em zero.</p>${model.canRecord&&(!S.forex||!S.forex.migration)?'<button type="button" data-fx-migrate>Adotar agregado V11 explicitamente, preservando legado</button>':''}`;
    el('fxPolicyIdentity').textContent=`${fx.policy.version} · ${fx.policy.statuteVersion} · ${fx.policy.parametricAnnexVersion} · vigência ${fx.policy.effectiveDate}`;
    el('fxRegistryRows').innerHTML=fx.policy.list().map(p=>`<tr><th>${safe(p.id)}<br>${safe(p.name||p.label)}</th><td>${safe(p.value===null?'PENDING':JSON.stringify(p.value))}<br>${safe(p.unit)}</td><td>${safe(p.technicalStatus||p.status)}<br>${safe(p.homologationStatus)}<br>${safe(p.operabilityStatus)}</td><td><details><summary>${safe(p.authorityMode)}</summary><pre>${safe(JSON.stringify(p,null,2))}</pre></details></td></tr>`).join('');
    const status=fx.state.editorStatus();el('fxEditorState').textContent=status.unlocked?'Sessão local desbloqueada até '+new Date(status.expiresAt).toLocaleTimeString('pt-BR'):'Editor bloqueado. Ativação normativa indisponível sem ato e autoridade verificáveis.';
    el('fxProposals').innerHTML=(S.forex&&Array.isArray(S.forex.proposals)?S.forex.proposals:[]).map(p=>`<p>${safe(p.timestamp)} · ${safe(p.field)}: ${safe(p.oldValue)} → ${safe(p.newValue)} · ${safe(p.status)} · ${safe(p.reason)} · não ativada</p>`).join('')||'<p>Nenhuma proposta registrada.</p>';
    const currency=model.account&&model.account.currency,unit=currency?' '+safe(currency):'';
    const reserveMetric=(label,r)=>{const v=r.value&&typeof r.value==='object'?r.value:null;const card=metric(label,{...r,value:v?v.constituted:null},unit);return v?card.replace('</article>','<p class="fx-reserve-detail">Requerido '+number(v.required)+unit+' · Déficit '+number(v.deficit)+unit+'</p></article>'):card;};
    el('fxReserveSummary').innerHTML=metric('FCR requerido',m.fcrRequirement,unit)+metric('FEO requerido',m.feoRequirement,unit)+reserveMetric('Constituição FCR',m.fcrStatus)+reserveMetric('Constituição FEO',m.feoStatus);
    let r=S.forex&&S.forex.reserves,history=[];const seen=new Set();while(r&&!seen.has(r)){seen.add(r);history.push(`<li>${safe(r.recordedAt)} · FCR ${number(r.fcrConstituted)} · FEO ${number(r.feoConstituted)} · ${safe(r.source)}</li>`);r=r.previous;}
    el('fxReserveHistory').innerHTML=history.length?'<ol>'+history.join('')+'</ol>':'<p>Nenhuma constituição registrada.</p>';
    const budget=m.operationBudget;
    el('fxBudgetContext').textContent=`Conta ${model.budgetScope.accountId||'não identificada'} · período ${model.budgetScope.periodId||'não identificado'} · ${model.account?.currency||'moeda não informada'} · ${model.budgetScope.operationId?'operação '+model.budgetScope.operationId:'próximo primeiro registro'}. Orçamento: ${number(budget.value)}. ${budget.status}`;
    el('fxBudgetHistory').innerHTML=budget.declaration?`<details><summary>Declaração e versões capturadas</summary><pre>${safe(JSON.stringify(budget.declaration,null,2))}</pre></details>`:'<p>Nenhuma declaração conciliada com este contexto.</p>';
    const a=model.account;
    const summary=el('fxOperationalSummary');
    if(summary){
      const accountId=model.budgetScope.accountId,registered=(S.accounts||[]).find(row=>row.forexAccountId===accountId);
      const label=registered?(registered.apelido||registered.nome||registered.broker||accountId):(accountId||'Não selecionada');
      const reasons=summary.querySelector('details')?.open===true;
      summary.innerHTML=`<dl class="fx-context-identity"><div><dt>Conta operacional</dt><dd>${safe(label)}</dd></div><div><dt>Período operacional</dt><dd>${safe(model.budgetScope.periodId||'Não identificado')}</dd></div></dl><div class="fx-context-eligibility"><span>Elegibilidade normativa</span><strong>${safe(model.executionEligibility.status)}</strong></div><div class="fx-context-metrics">${metric('Fase da conta',model.accountPhase)}${metric('Drawdown da conta',m.drawdown,'%')}${metric('Risco financeiro aberto e pendente',m.aggregateRisk,unit)}</div><details ${reasons?'open':''}><summary>Motivos e indisponibilidades</summary><ul>${model.findings.map(f=>`<li><b>${safe(f.code)}</b> — ${safe(f.message)}</li>`).join('')||'<li>Nenhum motivo informado pelo motor.</li>'}</ul><button type="button" data-fx-route="params">Ver parâmetros e observações</button></details>`;
    }
    el('forexV11Overview').innerHTML=`<div class="fx-engine-status"><strong>${safe(model.executionEligibility.status)} — elegibilidade normativa</strong><p>${model.canRecord?'O registro factual permanece acessível, sujeito à integridade da gravação.':'Registro indisponível nesta versão do agregado; preserve a base.'} ${safe(fx.policy.version)}</p><button type="button" data-fx-route="params">Registrar observações / ver parâmetros</button></div><div class="fx-engine-cards">
      ${metric('Equity flutuante',{value:a?a.equity:null,status:a?'RECORDED':'NOT_COMPUTABLE',findings:[]},unit)}${metric('Drawdown da conta',m.drawdown,'%')}${metric('Fase da conta',model.accountPhase)}${metric('Fase da grade',model.activeGridPhase)}${metric('Alavancagem bruta',m.leverage,'x')}${metric('Risco financeiro aberto e pendente',m.aggregateRisk,unit)}${metric('Risco de admissão',m.admissionRisk,unit)}${metric('Orçamento declarado da operação',m.operationBudget,unit)}${metric('Risco comprometido',m.committedRisk,unit)}${metric('VRM',m.vrm)}${metric('Orçamento prudencial',m.prudentialCapacity,unit)}${metric('Reservas totais constituídas',{value:model.reserves.totalConstituted,status:model.reserves.totalConstituted===null?'NOT_COMPUTABLE':'RECORDED',findings:[]},unit)}
      </div><nav class="fx-engine-actions" aria-label="Destinos do resumo Forex"><button type="button" data-fx-route="forex-operation">Ordens e fatos</button><button type="button" data-fx-route="forex-account">Contas</button><button type="button" data-fx-route="forex-reserves">Reservas</button><button type="button" data-fx-route="forex-reconciliation">Contabilidade</button><button type="button" data-fx-route="forex-planning">Planejamento</button></nav>
      <details><summary>Sequência de dimensionamento — volume final indisponível</summary><p>O parâmetro de risco inicial está pendente. Não há volume sugerido, arredondado ou autorizado.</p><ol>${(m.sizingTrace.steps||[]).map(step=>`<li><b>${safe(step.id)}</b> — ${safe(step.status)} · ${number(step.value)}</li>`).join('')}</ol></details>
      <details><summary>Findings e limites da apuração</summary><ul>${model.findings.map(f=>`<li><b>${safe(f.code)}</b> — ${safe(f.message)}</li>`).join('')}</ul></details>`;
  }
  fx.ui={render};
  mount();
})(globalThis);

// Consolidado FX: presentation-only selection, descriptive projections and explicit imports.
(function(FX){
  'use strict';
  const ui={accountId:null,source:'mt5',tab:'account',chart:'growth',from:'',to:'',search:'',preview:null,document:null,busy:false,token:0,message:'',kind:'info',mounted:false};
  const tabs=[['account','Conta'],['history','Histórico de negociação'],['statistics','Estatística'],['risks','Riscos']];
  const el=id=>document.getElementById(id);
  const safe=value=>String(value==null?'':value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number=(value,unit='')=>typeof value==='number'&&Number.isFinite(value)?value.toLocaleString('pt-BR',{maximumFractionDigits:2,minimumFractionDigits:unit==='%'?2:0})+(unit?' '+unit:''):'—';
  const aliases={trades:'tradeCount',growth:'growthPct',maxDrawdown:'drawdownAmount',maxDrawdownPct:'drawdownPct',activity:'tradingActivityPct',maxLoad:'maxDepositLoadPct'};
  const metric=(model,key)=>model.metrics?.[aliases[key]||key]||{value:null,availability:'unavailable',reason:'Os dados necessários não estão disponíveis.'};
  function label(model,key,title,unit){
    const m=metric(model,key),state=m.availability||'unavailable';if(state==='imported'&&['maxDrawdown','maxDrawdownPct'].includes(key))title='Rebaixamento informado · base do relatório';
    const displayUnit=unit||({count:'',ratio:'x'}[m.unit]??m.unit)||'';
    return `<div class="fxc-metric"><dt>${safe(title)}</dt><dd class="${typeof m.value==='number'&&m.value<0?'fxc-negative':''}">${m.value==null?'Indisponível':safe(number(m.value,displayUnit))}${state==='imported'?`<small>informado no relatório · ${safe(m.period?.from||'início não informado')} → ${safe(m.period?.to||'fim não informado')}</small>`:''}${m.reason?`<small>${safe(m.reason)}</small>`:''}</dd></div>`;
  }
  function unavailable(title,reason){return `<div class="fxc-unavailable"><strong>${safe(title)}</strong><p>${safe(reason)}</p></div>`;}
  function chart(points,title,color='blue',unit=''){
    const valid=(points||[]).map((p,i)=>({date:p.date||p.time||p.at||String(i+1),value:p.value??p.balance??p.growth})).filter(p=>typeof p.value==='number'&&Number.isFinite(p.value));
    if(!valid.length)return unavailable(title,'Indisponível: falta uma série histórica suficiente para este indicador.');
    const w=1100,h=230,pad=16,min=Math.min(...valid.map(p=>p.value)),max=Math.max(...valid.map(p=>p.value));
    const spread=max-min||Math.max(Math.abs(max)*.05,1),lo=min===max?min-spread/2:min;
    const path=valid.map((p,i)=>(i?'L':'M')+(pad+i*(w-pad*2)/Math.max(1,valid.length-1)).toFixed(2)+','+(h-pad-(p.value-lo)*(h-pad*2)/spread).toFixed(2)).join(' ');
    const grid=Array.from({length:5},(_,i)=>{const y=pad+i*(h-2*pad)/4;return `<line x1="0" x2="${w}" y1="${y}" y2="${y}"/><text x="${w-3}" y="${y-4}" text-anchor="end">${safe(number(lo+spread*(1-i/4),unit))}</text>`;}).join('');
    return `<figure class="fxc-chart"><figcaption>${safe(title)}</figcaption><svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${safe(title)}; ${valid.length} observações. Valores na tabela seguinte." preserveAspectRatio="none"><g class="fxc-grid">${grid}</g><path class="fxc-line fxc-${color}" d="${path}"/></svg><div class="fxc-chart-dates"><span>${safe(valid[0].date)}</span><span>${safe(valid[valid.length-1].date)}</span></div><details><summary>Ver valores do gráfico</summary><div class="fxc-scroll"><table><thead><tr><th>Data / referência</th><th>Valor</th></tr></thead><tbody>${valid.map(p=>`<tr><td>${safe(p.date)}</td><td>${safe(number(p.value,unit))}</td></tr>`).join('')}</tbody></table></div></details></figure>`;
  }
  function bars(model){
    const rows=[['equity','Capital líquido'],['netProfit','Lucro'],['initialBalance','Depósito inicial'],['withdrawals','Retiradas'],['deposits','Depósitos']];
    const max=Math.max(1,...rows.map(([k])=>Math.abs(metric(model,k).value||0)));
    return `<div class="fxc-bars">${rows.map(([key,title])=>{const m=metric(model,key);return `<div><span>${title}</span><strong>${safe(number(m.value,m.unit||''))}</strong><span class="fxc-bar-track" aria-hidden="true">${m.value==null?'':`<i class="${m.value<0?'fxc-bar-negative':''}" style="width:${Math.abs(m.value)/max*100}%"></i>`}</span></div>`;}).join('')}</div>`;
  }
  function radar(model){
    const axes=[['algoTrading','Algotrading'],['winRate','Negociações com lucro'],['lossRate','Negociações com perda'],['activity','Atividade'],['maxLoad','Depósito carregado'],['maxDrawdownPct','Rebaixamento']];
    const values=axes.map(([key])=>metric(model,key).value),ready=values.every(x=>typeof x==='number'&&x>=0&&x<=100);
    if(!ready)return `<div class="fxc-radar-empty"><svg viewBox="0 0 180 140" aria-hidden="true"><path d="M90 12 140 40 140 98 90 126 40 98 40 40Z M90 40 115 54 115 84 90 98 65 84 65 54Z M90 12V126 M40 40 140 98 M40 98 140 40"/></svg><span>Perfil da conta</span><small>Radar indisponível: faltam indicadores completos de atividade, carga e execução.</small></div>`;
    const points=values.map((v,i)=>{const a=-Math.PI/2+i*Math.PI/3;return `${90+55*Math.cos(a)*v/100},${70+55*Math.sin(a)*v/100}`;}).join(' ');
    return `<div class="fxc-radar-empty"><svg viewBox="0 0 180 140" role="img" aria-label="Perfil da conta"><polygon points="${points}" class="fxc-radar-data"/></svg><dl>${axes.map(([key,title])=>label(model,key,title,'%')).join('')}</dl></div>`;
  }
  function monthly(model){
    const rows=model.breakdowns?.monthly||[];
    if(!rows.length)return '<p class="fxc-note">Sem resultados mensais calculáveis nesta seleção.</p>';
    const years=[...new Set(rows.map(r=>String(r.month||r.date||'').slice(0,4)))].filter(Boolean).sort();
    const months=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
    return `<div class="fxc-scroll"><table class="fxc-months"><caption>${ui.source==='manual'?'Resultado realizado por mês':'Crescimento por mês · composição ajustada aos fluxos'}</caption><thead><tr><th>Ano</th>${months.map(m=>'<th>'+m+'</th>').join('')}<th>Total observado</th></tr></thead><tbody>${years.map(y=>'<tr><th>'+safe(y)+'</th>'+months.map((_,i)=>{const key=y+'-'+String(i+1).padStart(2,'0'),r=rows.find(x=>String(x.month||x.date).slice(0,7)===key);return `<td>${safe(number(r?(ui.source==='manual'?r.netProfit??r.netResult:r.growth??r.growthPct):null,ui.source==='manual'?metric(model,'netProfit').unit:'%'))}</td>`;}).join('')+`<td>${safe(number(model.breakdowns.years?.find(r=>r.year===y)?.[ui.source==='manual'?'netProfit':'growthPct'],ui.source==='manual'?metric(model,'netProfit').unit:'%'))}</td></tr>`).join('')}</tbody></table></div>`;
  }
  function history(model){
    const rows=(model.records||[]).filter(r=>JSON.stringify(r).toLocaleLowerCase('pt-BR').includes(ui.search.toLocaleLowerCase('pt-BR')));
    return `<p class="fxc-note">${ui.source==='manual'?'Operações finalizadas do JP Wealth; não equivalem a execuções do MT5.':'Execuções e movimentações importadas. Ordens não são contadas como execuções.'}</p><div class="fxc-scroll"><table><caption>${rows.length} registros nesta seleção</caption><thead><tr><th>Data / hora</th><th>Identificador</th><th>Instrumento</th><th>Tipo</th><th>Resultado líquido</th><th>Detalhes</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${safe(r.time||r.closedAt||r.date||'Não registrada')}</td><td>${safe(r.ticket||r.operationId||r.id||'—')}</td><td>${safe(r.symbol||r.instrument||'—')}</td><td>${safe(r.type||r.direction||r.kind||'Operação')}</td><td>${safe(number(r.netResult,r.currency||''))}</td><td><details><summary>Ver origem e campos</summary><pre>${safe(JSON.stringify(Object.fromEntries(['ticket','id','time','openedAt','closedAt','symbol','direction','executionDirection','type','entry','orderTicket','positionId','volume','price','profit','commission','fee','swap','netResult','source','currency','accountId','facts'].filter(k=>r[k]!=null).map(k=>[k,r[k]])),null,2))}</pre></details></td></tr>`).join('')||'<tr><td colspan="6">Nenhum registro disponível para esta conta, fonte e período.</td></tr>'}</tbody></table></div>`;
  }
  function distribution(rows,title,key){
    if(!rows?.length)return unavailable(title,'Nenhum registro classificável nesta seleção.');
    const resolved=key==='count'?'tradeCount':key,max=Math.max(1,...rows.map(r=>Math.abs(r[resolved]||0)));
    return `<section class="fxc-distribution"><h3>${safe(title)}</h3>${rows.map(r=>`<div><span>${safe(r.symbol||r.direction||r.name||r.key||'—')}</span><strong>${safe(number(r[resolved]))}</strong><span class="fxc-bar-track"><i class="${r[resolved]<0?'fxc-bar-negative':''}" style="width:${Math.abs(r[resolved]||0)/max*100}%"></i></span></div>`).join('')}</section>`;
  }
  function panels(model){
    const stat=[['trades','Negociações / operações'],['wins','Com lucro'],['losses','Com perda'],['neutral','Neutras'],['winRate','Taxa de resultados positivos','%'],['bestTrade','Melhor resultado'],['worstTrade','Pior resultado'],['grossProfit',ui.source==='manual'?'Resultados líquidos positivos':'Lucro bruto antes dos custos'],['grossLoss',ui.source==='manual'?'Resultados líquidos negativos':'Perda bruta antes dos custos'],['profitFactor','Fator de lucro · base declarada'],['expectedPayoff','Valor esperado'],['averageWin','Lucro médio'],['averageLoss','Perda média'],['recoveryFactor','Fator de recuperação'],['maxWinStreak','Máximo de vitórias consecutivas'],['maxLossStreak','Máximo de perdas consecutivas'],['sharpe','Índice de Sharpe'],['maxDrawdown','Rebaixamento máximo do saldo'],['maxDrawdownPct','Rebaixamento relativo do saldo','%']];
    const main=ui.source==='manual'?chart(model.series?.realized,'Resultado realizado acumulado','blue',metric(model,'netProfit').unit||''):chart(model.series?.[ui.chart],ui.chart==='growth'?(ui.from||ui.to?'Crescimento acumulado desde a abertura · recorte selecionado':'Crescimento ajustado aos fluxos'):'Saldo histórico','blue',ui.chart==='growth'?'%':model.account?.currency||'');
    el('fxcPanel-account').innerHTML=`<div class="fxc-chart-head"><dl>${label(model,'growth','Crescimento no período','%')}${label(model,'balance','Saldo')}${label(model,'netProfit','Resultado realizado')}</dl>${ui.source==='mt5'?`<div class="fxc-segment" aria-label="Gráfico principal"><button data-fxc-chart="growth" aria-pressed="${ui.chart==='growth'}">Crescimento</button><button data-fxc-chart="balance" aria-pressed="${ui.chart==='balance'}">Saldo</button></div>`:''}</div>${main}${monthly(model)}${ui.source==='mt5'?chart(model.series?.equity,'Capital líquido (equity) histórico','green',model.account?.currency||''):''}`;
    el('fxcPanel-history').innerHTML=history(model)+(ui.source==='mt5'?['orders','positions'].map(collection=>{const rows=(S.fxConsolidated?.accounts?.find(a=>a.id===ui.accountId)?.[collection]||[]);return `<details class="fxc-entity-details"><summary>${collection==='orders'?'Ordens registradas (históricas e pendentes)':'Snapshots de posições abertas'} · ${rows.length}</summary><p>Entidade distinta de execução; não integra a contagem de negociações. Fotografias importadas não comprovam o estado atual da corretora. Este inventário não é filtrado pelo período das execuções.</p><div class="fxc-scroll"><table><thead><tr><th>Ticket</th><th>Instrumento</th><th>Tipo / estado</th><th>Data observada</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${safe(r.ticket)}</td><td>${safe(r.symbol)}</td><td>${safe([r.type,r.state,r.orderScope].filter(Boolean).join(' · '))}</td><td>${safe(r.time||r.openedAt||'Não informada')}</td></tr>`).join('')}</tbody></table></div></details>`;}).join(''):'');
    el('fxcPanel-statistics').innerHTML=`<dl class="fxc-statistics">${stat.map(([k,t,u])=>label(model,k,t,u)).join('')}</dl><h3 class="fxc-centered">Distribuição</h3><div class="fxc-distributions">${distribution(model.breakdowns?.symbols,'Negociações por instrumento','count')}${distribution(model.breakdowns?.symbols,'Resultado por instrumento','netProfit')}${distribution(model.breakdowns?.directions,'Direção das negociações','count')}</div>`;
    el('fxcPanel-risks').innerHTML=`<p class="fxc-note">Estatísticas históricas descritivas. Não alteram fases, limites ou elegibilidade do motor V11.</p><dl class="fxc-statistics">${label(model,'maxDrawdown','Rebaixamento máximo do saldo')}${label(model,'maxDrawdownPct','Rebaixamento relativo do saldo','%')}${label(model,'maxLoad','Depósito máximo carregado','%')}${label(model,'mfe','MFE — excursão favorável')}${label(model,'mae','MAE — excursão adversa')}</dl>${chart(model.series?.drawdown,'Rebaixamento histórico do saldo','negative','%')}${chart(model.series?.load,'Carga histórica de margem','gray','%')}`;
    for(const [id] of tabs){const active=ui.tab===id;el('fxcPanel-'+id).hidden=!active;el('fxcTab-'+id).setAttribute('aria-selected',String(active));el('fxcTab-'+id).tabIndex=active?0:-1;}
  }
  function notify(message,kind='info'){ui.message=message;ui.kind=kind;if(el('fxcStatus')){el('fxcStatus').textContent=message;el('fxcStatus').dataset.kind=kind;}}
  function options(accounts,selected,automatic=false){return (automatic?'<option value="">Automático — conta Mestre</option>':'<option value="">Selecione uma conta</option>')+accounts.map(a=>`<option value="${safe(a.id)}" ${selected===a.id?'selected':''}>${safe(a.name||a.nome||a.id)}${a.login?' · '+safe(a.login):''}${a.archived?' · histórico':''}</option>`).join('');}
  function mount(){
    const root=el('fxconsolidated');if(!root||ui.mounted)return;
    root.innerHTML=`<div class="fxc-workspace"><header class="fxc-toolbar"><div><h1>Consolidado FX</h1><p>Histórico e desempenho por conta</p></div><button type="button" id="fxcOpenImport">Importar / Atualizar relatório</button></header><div class="fxc-controls"><label>Conta em análise<select id="fxcAccount"></select></label><div class="fxc-segment" aria-label="Fonte dos dados"><button type="button" id="fxcMt5" aria-pressed="true">MT5</button><button type="button" id="fxcManual" aria-pressed="false">Manual</button></div><label>De<input type="date" id="fxcFrom"></label><label>Até<input type="date" id="fxcTo"></label><label>Filtrar registros<input type="search" id="fxcSearch" placeholder="Ticket, instrumento ou operação"></label><button type="button" id="fxcPreferences" aria-label="Configurar conta padrão do Consolidado">Conta padrão</button></div><p id="fxcStatus" role="status" aria-live="polite"></p><section id="fxcImport" hidden aria-label="Importar relatório MT5"><h2>Importar relatório MT5</h2><p>Escolha um relatório HTML ou PDF textual. Processamento local; o arquivo original não será armazenado. Confira a conta selecionada antes de confirmar.</p><label>Arquivo do relatório<input id="fxcFile" type="file" accept=".html,.htm,.pdf"></label><div class="fxc-import-dates"><label>Início declarado, se ausente<input type="date" id="fxcImportFrom"></label><label>Fim declarado, se ausente<input type="date" id="fxcImportTo"></label></div><div class="fxc-import-dates"><label>Separadores numéricos<select id="fxcNumberFormat"><option value="auto">Detectar pelo conteúdo</option><option value="decimal-dot">1,234.56 — ponto decimal</option><option value="decimal-comma">1.234,56 — vírgula decimal</option></select></label><label>Datas sem ano no início<select id="fxcDateOrder"><option value="auto">Detectar pelo conteúdo</option><option value="dmy">Dia / mês / ano</option><option value="mdy">Mês / dia / ano</option></select></label></div><p>Se houver ambiguidade, selecione o formato do documento e analise novamente. Confira os valores originais e interpretados na prévia.</p><button type="button" id="fxcAnalyze">Analisar arquivo</button><button type="button" id="fxcCancelImport">Cancelar</button><div id="fxcPreview"></div></section><section id="fxcImportResult" hidden aria-label="Próximo passo após importar"></section><div class="fxc-summary"><section id="fxcIdentity"></section><section id="fxcRadar"></section><section id="fxcBars"></section></div><p id="fxcCoverage" class="fxc-provenance"></p><div class="fxc-tabs" role="tablist" aria-label="Visões do Consolidado">${tabs.map(([id,title],i)=>`<button type="button" role="tab" id="fxcTab-${id}" aria-controls="fxcPanel-${id}" aria-selected="${!i}" tabindex="${i?-1:0}" data-fxc-tab="${id}">${title}</button>`).join('')}</div>${tabs.map(([id])=>`<section role="tabpanel" id="fxcPanel-${id}" aria-labelledby="fxcTab-${id}" tabindex="0" ${id==='account'?'':'hidden'}></section>`).join('')}<p class="fxc-provenance">MT5 e Manual são bases separadas. Registrar ou importar fatos não autoriza operar. Contexto financeiro ausente continua indisponível.</p></div>`;
    // Move a apresentação existente, nunca clona widgets ou o read model.
    const context=document.createElement('aside');context.id='fxOperationalContext';
    context.setAttribute('aria-labelledby','fxContextTitle');
    context.innerHTML='<header class="fx-context-heading"><span class="cp-kicker">FOREX · AGORA</span><h2 id="fxContextTitle">Contexto operacional</h2><p>Relacionado à conta operacional, independente da conta em análise.</p></header><div id="fxOperationalSummary"></div><button type="button" id="fxContextToggle" aria-expanded="false" aria-controls="execOverview">Ver contexto completo</button>';
    root.classList.add('fx-journey');root.append(context);
    context.append(el('execOverview'));
    el('execOverview').hidden=true;el('execOverview').inert=true;
    el('fxContextToggle').addEventListener('click',()=>fxSetContextExpanded(el('execOverview').hidden));
    root.addEventListener('click',event=>{
      const tab=event.target.closest('[data-fxc-tab]'),toggle=event.target.closest('[data-fxc-chart]');
      if(tab){ui.tab=tab.dataset.fxcTab;render();return;}if(toggle){ui.chart=toggle.dataset.fxcChart;render();return;}
    });
    root.querySelector('[role=tablist]').addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();const i=tabs.findIndex(([id])=>id===ui.tab);ui.tab=tabs[event.key==='Home'?0:event.key==='End'?3:(i+(event.key==='ArrowRight'?1:3))%4][0];render();el('fxcTab-'+ui.tab).focus();});
    el('fxcAccount').addEventListener('change',event=>{ui.accountId=event.target.value||null;cancel();render();});
    el('fxcMt5').onclick=()=>{ui.source='mt5';render();};el('fxcManual').onclick=()=>{ui.source='manual';cancel();render();};
    for(const [id,key] of [['fxcFrom','from'],['fxcTo','to'],['fxcSearch','search']])el(id).addEventListener('input',event=>{ui[key]=event.target.value;render();});
    el('fxcPreferences').onclick=()=>openSettingsModal('forex-consolidated',el('fxcPreferences'));
    el('fxcOpenImport').onclick=()=>openImport({returnFocus:el('fxcOpenImport')});
    el('fxcCancelImport').onclick=()=>{cancel();el('fxcImport').hidden=true;el('fxcOpenImport').focus();};
    for(const id of ['fxcFile','fxcNumberFormat','fxcDateOrder','fxcImportFrom','fxcImportTo'])
      el(id).addEventListener('change',()=>{cancel();notify('Arquivo ou leitura alterados. Analise novamente para conferir a nova prévia.');});
    el('fxcAnalyze').onclick=analyze;ui.mounted=true;
  }
  function cancel(){closeRegistration();closeSetup({force:true});ui.token++;ui.preview=null;ui.document=null;ui.busy=false;FX.cancelImport?.();FX.disposePDF?.();if(el('fxcPreview'))el('fxcPreview').replaceChildren();if(el('fxcImportResult')){el('fxcImportResult').replaceChildren();el('fxcImportResult').hidden=true;}if(el('fxcAnalyze'))el('fxcAnalyze').disabled=false;}
  async function analyze(){
    const file=el('fxcFile').files[0];if(!file)return notify('Escolha um arquivo para analisar.','error');
    cancel();const token=ui.token;ui.busy=true;el('fxcAnalyze').disabled=true;notify('Analisando localmente…');
    try{
      if(file.size>32*1024*1024)throw Error('Arquivo acima do limite de leitura local de 32 MiB. Exporte um período menor; nenhum dado foi importado.');
      const bytes=new Uint8Array(await file.arrayBuffer());if(token!==ui.token)return;
      const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
      const parseOptions={numberFormat:el('fxcNumberFormat').value,dateOrder:el('fxcDateOrder').value};
      let report;
      if(String.fromCharCode(...bytes.slice(0,5))==='%PDF-')report=await FX.parsePDF(bytes,parseOptions);
      else{let encoding='utf-8';if(bytes[0]===255&&bytes[1]===254)encoding='utf-16le';else if(bytes[0]===254&&bytes[1]===255)encoding='utf-16be';let text=new TextDecoder(encoding).decode(bytes);if(encoding==='utf-8'&&/charset\s*=\s*["']?windows-1252/i.test(text.slice(0,4096)))text=new TextDecoder('windows-1252').decode(bytes);report=FX.parseHTML(text,parseOptions);}
      if(token!==ui.token)return;
      const meta={fileName:file.name,fileHash:hash,importedAt:new Date().toISOString(),from:el('fxcImportFrom').value||null,to:el('fxcImportTo').value||null};
      if(meta.from||meta.to)report.period={...report.period,from:report.period?.from||meta.from,to:report.period?.to||meta.to,declared:true};
      ui.document={report,meta};prepareDocument();
    }catch(error){if(token===ui.token)notify(error.message||String(error),'error');}
    finally{if(token===ui.token){ui.busy=false;el('fxcAnalyze').disabled=false;}}
  }

  function prepareDocument(){
    if(!ui.document)return;
    ui.preview=null;
    const {report,meta}=ui.document;
    const status=FX.inspectRegistration(report,ui.accountId);
    if(!status.ok){
      if(status.status==='invalid'){
        el('fxcPreview').innerHTML=`<h3>Revise a leitura do arquivo</h3><p>${safe(status.error)}</p><ul>${(report.issues||[]).map(i=>'<li>'+safe(i.message||i.code||i)+'</li>').join('')}</ul><p>Nenhum registro foi importado. Confira o formato numérico e a ordem das datas acima; depois analise novamente.</p>`;
        notify('O documento contém campos que precisam de revisão.','error');
      }else showRegistrationStatus(status);return;
    }
    const preview=FX.prepareImport(report,ui.accountId,meta);
    if(!preview?.ok){notify(preview?.error?.message||preview?.error||'Não foi possível validar a importação.','error');return;}
      ui.preview=preview;const c=preview.counts||{};
      el('fxcPreview').innerHTML=`<h3>Confira a prévia</h3><dl class="fxc-statistics"><div><dt>Conta do relatório</dt><dd>${safe(report.identity?.login)}</dd></div><div><dt>Moeda</dt><dd>${safe(report.identity?.currency||'Não informada')}</dd></div><div><dt>Novas execuções</dt><dd>${safe(c.newDeals??0)}</dd></div><div><dt>Novas ordens</dt><dd>${safe(c.newOrders??0)}</dd></div><div><dt>Repetidos</dt><dd>${safe(c.duplicates??0)}</dd></div><div><dt>Divergências</dt><dd>${safe(c.conflicts??0)}</dd></div></dl><ul>${(preview.issues||report.issues||[]).map(i=>'<li>'+safe(i.message||i.code||i)+'</li>').join('')}</ul>${preview.conflicts?.length?`<details><summary>Comparar divergências</summary><pre>${safe(JSON.stringify(preview.conflicts,null,2))}</pre></details><label class="fxc-check"><input type="checkbox" id="fxcAcceptRevision"> Confirmo a revisão dos registros divergentes; manter o histórico anterior.</label>`:''}<label class="fxc-check"><input type="checkbox" id="fxcConfirmIdentity"> Conferi a conta de destino e a identidade do relatório. O arquivo não autentica a corretora.</label><button type="button" id="fxcConfirmImport">Confirmar importação</button><p>O comprovante e os dados processados serão salvos. Guarde o original separadamente.</p>`;
      el('fxcConfirmImport').onclick=confirmImport;notify(preview.duplicate?'Relatório já importado. Não serão criadas duplicações.':'Prévia pronta. Nenhuma operação foi gravada.');

  }
  function showRegistrationStatus(status){
    ui.preview=null;FX.cancelImport();
    const labels={incomplete:'Completar cadastro',historical:'Recadastrar conta',mismatch:'Cadastrar conta do relatório',unregistered:'Cadastrar conta do relatório'};
    const action=labels[status.status];
    const identity=ui.document.report.identity||{};
    el('fxcPreview').innerHTML=`<h3>Cadastro necessário</h3><p>${safe(status.error)}</p><p>Documento: ${safe(identity.login||'Sem identificação')} · ${safe(identity.broker||'Corretora não informada')} · ${safe(identity.currency||'Moeda não informada')}</p>${status.status==='other'?(status.matches||[]).map((a,i)=>`<button type="button" data-fxc-select="${i}">Selecionar ${safe(a.name||a.id)} · ${safe(a.login)}</button>`).join(''):''}${action?`<button type="button" id="fxcRegister">${action}</button>`:''}<p>Nenhuma operação importada. Salvar o cadastro não confirma a importação.</p>`;
    el('fxcPreview').querySelectorAll('[data-fxc-select]').forEach(button=>button.onclick=()=>{ui.accountId=status.matches[Number(button.dataset.fxcSelect)].id;render();prepareDocument();});
    if(action)el('fxcRegister').onclick=()=>openAccountRegistration({report:ui.document.report,accountId:ui.accountId,trigger:el('fxcRegister'),onSaved:result=>{
      ui.accountId=result.accountId;render();prepareDocument();el('fxcConfirmIdentity')?.focus();
    }});
    notify(status.error,'error');
  }
  let registrationDialog=null,registrationView=null;
  function closeRegistration(){
    FX.cancelRegistration?.();registrationView=null;
    if(registrationDialog?.open)registrationDialog.close();
  }
  function openAccountRegistration({report=null,accountId=null,trigger=document.activeElement,onSaved=null}={}){
    if(registrationView?.saving)return;
    const prepared=FX.beginRegistration(report,accountId);
    if(!prepared.ok){if(report)notify(prepared.error,'error');else alert(prepared.error);return;}
    if(!registrationDialog){
      registrationDialog=document.createElement('dialog');registrationDialog.id='fxcRegistrationDialog';
      registrationDialog.className='fxc-registration';registrationDialog.setAttribute('aria-labelledby','fxcRegistrationTitle');
      document.body.append(registrationDialog);
      registrationDialog.addEventListener('cancel',event=>{event.preventDefault();if(!registrationView?.saving)closeRegistration();});
      registrationDialog.addEventListener('keydown',event=>{if(event.key==='Escape')event.stopPropagation();});
      registrationDialog.addEventListener('close',()=>{const target=registrationDialog._returnFocus;registrationView=null;FX.cancelRegistration?.();if(target?.isConnected)target.focus();});
    }
    const draft=prepared.draft,mode=prepared.mode;
    const title=mode==='complete'?'Completar cadastro':mode==='reregister'?'Recadastrar conta':'Cadastrar conta';
    registrationView={...prepared,saving:false,onSaved};registrationDialog._returnFocus=trigger;
    const field=(key,label,required=false)=>`<label>${label}<input id="fxcr-${key}" name="${key}" value="${safe(draft[key])}" maxlength="160" ${required?'required':''} autocomplete="off"></label>`;
    registrationDialog.innerHTML=`<form id="fxcRegistrationForm"><header><h2 id="fxcRegistrationTitle">${title}</h2><p>Forex → Contas · cadastro local</p></header><p>Confira os identificadores. Esta ficha não registra saldo, equity ou parâmetros financeiros e não altera a conta operacional.</p><div class="fxc-registration-fields">${field('name','Nome de exibição',true)}<label>Tipo<select name="type" id="fxcr-type">${['MESTRE','PRÓPRIA','SATÉLITE'].map(t=>`<option ${draft.type===t?'selected':''}>${t}</option>`).join('')}</select></label><label>Plataforma<select name="platform" id="fxcr-platform" required>${platformOptions(draft.platform)}</select></label>${field('login','Número / login da conta',true)}${field('broker','Corretora')}${field('server','Servidor (se informado)')}${field('currency','Moeda do cadastro (se informada)')}</div><p>Identificadores sugeridos pelo documento precisam de revisão. Senhas não são necessárias. Metadados ausentes permanecem não verificados.</p>${mode==='reregister'?'<label class="fxc-check"><input id="fxcr-history" type="checkbox" required> Confirmo reutilizar esta identidade e preservar seu histórico, sem restaurar saldos operacionais.</label>':''}<p id="fxcRegistrationStatus" role="status" aria-live="polite"></p><footer><button type="button" id="fxcRegistrationCancel">Cancelar</button><button type="submit" id="fxcRegistrationSave">Salvar cadastro</button></footer></form>`;
    el('fxcRegistrationCancel').onclick=closeRegistration;
    el('fxcRegistrationForm').onsubmit=async event=>{
      event.preventDefault();const view=registrationView;if(!view||view.saving)return;
      const input=Object.fromEntries(new FormData(event.currentTarget));
      view.saving=true;el('fxcRegistrationSave').disabled=true;el('fxcRegistrationCancel').disabled=true;
      el('fxcRegistrationStatus').textContent='Confirmando cadastro…';
      try{
        const result=await FX.saveRegistration(view.token,input,{confirmHistorical:el('fxcr-history')?.checked===true});
        if(registrationView!==view)return;
        if(!result.ok){el('fxcRegistrationStatus').textContent=result.error||'Cadastro não confirmado.';view.unknown=result.persistido===null;return;}
        const callback=view.onSaved;closeRegistration();renderContas();
        if(callback)callback(result);
      }catch(error){if(registrationView===view)el('fxcRegistrationStatus').textContent='Cadastro não confirmado. Confira a sessão.';}
      finally{if(registrationView===view){view.saving=false;el('fxcRegistrationCancel').disabled=false;el('fxcRegistrationSave').disabled=!!view.unknown;}}
    };
    registrationDialog.showModal();el('fxcr-name').focus();
  }
  function openImport({accountId=null,returnFocus=document.activeElement}={}){
    cancel();if(accountId)ui.accountId=accountId;
    ui.source='mt5';window.JPWNavigation?.navigate('forex-consolidated');render();
    el('fxcImport').hidden=false;el('fxcFile').focus();
    el('fxcCancelImport').onclick=()=>{cancel();el('fxcImport').hidden=true;(returnFocus?.isConnected&&returnFocus.getClientRects().length?returnFocus:el('fxcOpenImport')).focus();};
  }
  let setupDialog=null,setupView=null;
  function closeSetup({force=false}={}){
    if(setupView?.saving&&!force)return;
    FX.cancelAccountSetup?.();setupView=null;if(setupDialog?.open)setupDialog.close();
  }
  function accountReport(accountId){
    const account=S.fxConsolidated?.accounts?.find(a=>a.id===accountId),snapshot=account?.summaries?.slice(-1)[0];
    return snapshot?{format:snapshot.format,identity:{login:account.login,broker:account.broker,currency:account.currency,server:account.server},
      period:snapshot.period,generatedAt:snapshot.generatedAt||null,summary:snapshot.values,orders:[],deals:[],positions:[],issues:[]}:null;
  }
  function openAccountSetup({accountId=null,report=null,returnFocus=document.activeElement}={}){
    if(setupView?.saving)return;
    const account=FX.accounts().find(a=>a.id===accountId);
    if(!account||account.archived||account.id.startsWith('live:')){
      openAccountRegistration({accountId:account?.id||null,report,trigger:returnFocus,
        onSaved:result=>openAccountSetup({accountId:result.accountId,report,returnFocus})});return;
    }
    // Suggestions remain read-only until each step is explicitly confirmed.
    report=report||accountReport(accountId);
    const prepared=FX.beginAccountSetup(accountId,report);
    if(!prepared.ok){alert(prepared.error);return;}
    if(!setupDialog){
      setupDialog=document.createElement('dialog');setupDialog.id='fxcSetupDialog';setupDialog.className='fxc-registration';
      setupDialog.setAttribute('aria-labelledby','fxcSetupTitle');document.body.append(setupDialog);
      setupDialog.addEventListener('cancel',event=>{event.preventDefault();closeSetup();});
      setupDialog.addEventListener('keydown',event=>{if(event.key==='Escape')event.stopPropagation();});
      setupDialog.addEventListener('close',()=>{const target=setupDialog._returnFocus;FX.cancelAccountSetup?.();setupView=null;if(target?.isConnected)target.focus();});
    }
    setupView={...prepared,saving:false};setupDialog._returnFocus=returnFocus;
    const suggestions=prepared.suggestions;
    const field=(id,label,type='text',value='',required=false)=>`<label>${label}<input id="${id}" type="${type}" ${type==='number'?'step="any"':''} value="${safe(value)}" ${required?'required':''}></label>`;
    setupDialog.innerHTML=`<header><h2 id="fxcSetupTitle">Preparar conta e período</h2><p>${safe(account.name||account.id)} · ${safe(account.login||'')} · ${safe(account.currency||'Moeda a confirmar')}</p></header><p>Cadastro, importação, período e observação são confirmações separadas. Fechar esta ficha preserva as etapas já salvas.</p>${suggestions?`<section class="fxc-setup-report"><h3>Valores do relatório</h3><dl class="fxc-statistics"><div><dt>Saldo informado</dt><dd>${safe(number(suggestions.balance,account.currency||''))}</dd></div><div><dt>Equity informado</dt><dd>${safe(number(suggestions.equity,account.currency||''))}</dd></div><div><dt>Referência do documento</dt><dd>${safe(suggestions.date||'Data não informada')}</dd></div></dl><p>Saldo e equity são fotografias da conta. Nenhum deles preenche o SI ou o saldo de abertura. Confirme a data e o fuso da observação antes de registrar.</p></section>`:''}<form id="fxcSetupPeriodForm"><h3>1. Período operacional</h3><label>Período<select id="fxcs-period"><option value="">Registrar novo período</option>${prepared.periods.map(p=>`<option value="${safe(p.periodId)}" ${p.periodId===prepared.currentPeriodId?'selected':''}>${safe(p.startedAt)} · ${safe(p.currency)} · SI ${safe(number(p.si))}</option>`).join('')}</select></label><div id="fxcs-new-period" class="fxc-registration-fields">${field('fxcs-start','Início do período','date','',true)}${field('fxcs-currency','Moeda','text',account.currency||'',true)}${field('fxcs-si','SI confirmado (capital inicial) · vazio = indisponível','number')}${field('fxcs-book','Saldo contábil na abertura · vazio = indisponível','number')}${field('fxcs-period-source','Fonte do período e capital','text','Declaração manual',true)}${field('fxcs-period-reason','Motivo do registro','text','Preparação explícita da conta',true)}<label class="fxc-check"><input id="fxcs-active" type="checkbox" checked> Tornar este o período atual da conta</label></div><label class="fxc-check"><input id="fxcs-confirm-period" type="checkbox" required> Conferi a conta, o período, a moeda e o SI informado ou indisponível.</label><button type="submit" id="fxcs-save-period">Confirmar período</button></form><form id="fxcSetupObservationForm" hidden><h3>2. Observação financeira</h3><p id="fxcs-period-summary"></p><p>Opcional para preencher as ordens. Os cálculos que dependem de fatos ausentes continuam indisponíveis. Registrar esta observação torna a conta a referência financeira do motor.</p><div class="fxc-registration-fields">${field('fxcs-equity','Equity observado','number',suggestions?.equity??'',true)}${field('fxcs-observed','Data e hora da observação · fuso deste dispositivo','datetime-local','',true)}${field('fxcs-observation-source','Fonte da observação','text',suggestions?.source||'Declaração manual',true)}${field('fxcs-rate','Conversão: 1 USD na moeda da conta','number')}${field('fxcs-cashflow','Fluxo líquido desde o SI · vazio = desconhecido','number')}${field('fxcs-observation-reason','Motivo do registro','text','Observação financeira revisada',true)}</div><label class="fxc-check"><input id="fxcs-cashflow-confirm" type="checkbox"> Conferi a cobertura do fluxo líquido informado (depósitos menos retiradas).</label><label class="fxc-check"><input id="fxcs-confirm-observation" type="checkbox" required> Conferi equity, fonte, data/hora e unidade. O relatório não comprova valores atuais.</label><button type="submit" id="fxcs-save-observation">Salvar observação financeira</button></form><p id="fxcSetupStatus" role="status" aria-live="polite"></p><footer><button type="button" id="fxcs-close">Fechar</button><button type="button" id="fxcs-open-orders" hidden>Ir para fases e ordens</button></footer>`;
    const updatePeriod=()=>{const existing=!!el('fxcs-period').value;el('fxcs-new-period').hidden=existing;el('fxcs-new-period').querySelectorAll('input').forEach(input=>input.disabled=existing);};
    el('fxcs-period').onchange=()=>{updatePeriod();el('fxcs-confirm-period').checked=false;};updatePeriod();
    const optional=id=>el(id).value.trim()===''?null:Number(el(id).value);
    const run=async(buttonId,command,success)=>{
      const view=setupView;if(!view||view.saving)return;view.saving=true;el(buttonId).disabled=true;el('fxcs-close').disabled=true;
      el('fxcSetupStatus').textContent='Confirmando a gravação…';
      try{const result=await command(view);if(setupView!==view)return;
        if(!result.ok){view.unknown=result.persistido===null;el('fxcSetupStatus').textContent=result.error||'Etapa não confirmada.';return;}
        success(result,view);if(typeof renderContas==='function')renderContas();
      }catch(error){if(setupView===view)el('fxcSetupStatus').textContent='Etapa não confirmada. Confira a sessão antes de continuar.';}
      finally{if(setupView===view){view.saving=false;el('fxcs-close').disabled=false;el(buttonId).disabled=!!view.unknown||view.completed===buttonId;}}
    };
    el('fxcSetupPeriodForm').onsubmit=event=>{event.preventDefault();run('fxcs-save-period',view=>FX.saveSetupPeriod(view.token,{periodId:el('fxcs-period').value||null,startedAt:el('fxcs-start').value,
      currency:el('fxcs-currency').value.trim().toUpperCase(),si:optional('fxcs-si'),openingBook:optional('fxcs-book'),source:el('fxcs-period-source').value,
      reason:el('fxcs-period-reason').value,activateCurrentPeriod:el('fxcs-active').checked,confirmPeriod:el('fxcs-confirm-period').checked}),(result,view)=>{
        view.periodId=result.periodId;view.period=result.period;view.completed='fxcs-save-period';el('fxcSetupPeriodForm').hidden=true;el('fxcs-open-orders').hidden=false;
        el('fxcs-period-summary').textContent='Período '+result.period.startedAt+' · '+result.period.currency+' · SI '+number(result.period.si)+'.';
        const canObserve=typeof result.period.si==='number'&&result.period.si>0;
        el('fxcSetupObservationForm').hidden=!canObserve;
        el('fxcs-rate').closest('label').hidden=result.period.currency==='USD';el('fxcs-rate').required=result.period.currency!=='USD';
        el('fxcSetupStatus').textContent=(result.persistido?'Período salvo. ':'Período selecionado. ')+(canObserve?'Revise a observação ou siga para as ordens.':'O SI permanece indisponível. As ordens já podem ser preenchidas; os cálculos dependentes do SI continuam bloqueados.');
        (canObserve?el('fxcs-equity'):el('fxcs-open-orders')).focus();
      });};
    el('fxcSetupObservationForm').onsubmit=event=>{event.preventDefault();run('fxcs-save-observation',view=>{
      const local=el('fxcs-observed').value,observedAt=local?new Date(local).toISOString():null;
      return FX.saveSetupObservation(view.token,{equity:optional('fxcs-equity'),observedAt,source:el('fxcs-observation-source').value,
        usdToAccountRate:optional('fxcs-rate'),netCashflow:optional('fxcs-cashflow'),cashflowAdjustmentRecorded:el('fxcs-cashflow-confirm').checked,
        reason:el('fxcs-observation-reason').value,confirmObservation:el('fxcs-confirm-observation').checked});
      },(result,view)=>{view.completed='fxcs-save-observation';el('fxcSetupObservationForm').hidden=true;el('fxcSetupStatus').textContent='Observação financeira salva. O motor mantém suas verificações de elegibilidade.';el('fxcs-open-orders').focus();});};
    el('fxcs-close').onclick=closeSetup;
    el('fxcs-open-orders').onclick=()=>{
      const view=setupView;if(!view?.periodId||view.saving)return;
      const selected=window.JPWForex.state.selectOperationalAccount(view.account.id);
      const period=selected.ok&&window.JPWForex.state.selectOperationalPeriod(view.account.id,view.periodId);
      if(!selected.ok||!period?.ok){el('fxcSetupStatus').textContent=selected.error||period?.error||'Período indisponível.';return;}
      closeSetup();window.JPWNavigation?.navigate('forex-operation');window.JPWNavigation?.navigateLocal('exec','panel');
      if(typeof renderPhases==='function')renderPhases();document.getElementById('execPhaseGridsCard')?.scrollIntoView({block:'start'});
    };
    setupDialog.showModal();el('fxcs-period').focus();
  }
  async function confirmImport(){
    if(!ui.preview||ui.busy)return;if(!el('fxcConfirmIdentity').checked)return notify('Confirme a identidade antes da importação.','error');
    if(ui.preview.conflicts?.length&&!el('fxcAcceptRevision')?.checked)return notify('As divergências precisam de confirmação explícita.','error');
    ui.busy=true;const token=ui.token;const button=el('fxcConfirmImport');button.disabled=true;
    try{const result=await FX.confirmImport(ui.preview,{confirmIdentity:true,acceptRevision:!!el('fxcAcceptRevision')?.checked});if(token!==ui.token)return;if(!result?.ok){notify(result?.error?.message||result?.error||'Gravação não confirmada. A prévia foi preservada.','error');return;}ui.accountId=result.accountId||result.receipt?.accountId||ui.preview.account?.id||ui.accountId;const importedReport=ui.document?.report||ui.preview.report,importedAccountId=ui.accountId;ui.preview=null;ui.document=null;el('fxcPreview').replaceChildren();el('fxcImport').hidden=true;el('fxcImportResult').hidden=false;el('fxcImportResult').innerHTML='<h3>Relatório conferido</h3><p>O histórico está disponível no Consolidado. Prepare separadamente o período e os fatos financeiros da conta para preencher as ordens.</p><button type="button" id="fxcPrepareAccount">Preparar conta e período</button>';el('fxcPrepareAccount').onclick=()=>openAccountSetup({accountId:importedAccountId,report:importedReport,returnFocus:el('fxcPrepareAccount')});notify(result.duplicate?'Relatório já existente; nenhum registro duplicado.':'Importação confirmada. Comprovante salvo na base local.');render();}
    catch(error){if(token===ui.token)notify(error.message||String(error),'error');}
    finally{if(token===ui.token)ui.busy=false;if(button.isConnected)button.disabled=false;}
  }
  function render(){
    mount();if(!ui.mounted)return;const accounts=FX.accounts?FX.accounts():[];if(ui.source==='manual'&&S.operationHistory?.schemaVersion===DEFAULTS.operationHistory.schemaVersion&&S.operationHistory?.records?.some(r=>!r.accountId))accounts.push({id:'unassigned',name:'Não conciliados — conta histórica ausente',archived:true});
    if(ui.accountId===null){const preferred=S.fxConsolidated?.defaultAccountId;const masters=accounts.filter(a=>a.type==='MESTRE');ui.accountId=preferred?(accounts.some(a=>a.id===preferred)?preferred:''):(masters.length===1?masters[0].id:'');}
    if(ui.accountId&&!accounts.some(a=>a.id===ui.accountId))ui.accountId='';
    const select=el('fxcAccount');if(document.activeElement!==select)select.innerHTML=options(accounts,ui.accountId);
    const account=accounts.find(a=>a.id===ui.accountId)||null;
    let model={metrics:{},series:{},breakdowns:{},records:[],issues:[]};
    try{if(ui.source==='manual'&&S.operationHistory?.schemaVersion!==DEFAULTS.operationHistory.schemaVersion)throw Error('Versão do histórico não suportada: conteúdo preservado sem interpretação.');if(ui.from&&ui.to&&ui.from>ui.to)throw Error('O início do período deve anteceder o fim.');if(FX.project&&account)model=FX.project(S.fxConsolidated||FX.emptyState(),S.operationHistory?.records||[],{source:ui.source,accountId:account.id,account,from:ui.from||null,to:ui.to||null});}
    catch(error){model.issues=[{message:'Não foi possível calcular esta seleção: '+error.message}];}
    model.account=model.account||account;el('fxcMt5').setAttribute('aria-pressed',String(ui.source==='mt5'));el('fxcManual').setAttribute('aria-pressed',String(ui.source==='manual'));
    el('fxcIdentity').innerHTML=`<div class="fxc-account-heading"><svg viewBox="0 0 48 48" aria-hidden="true"><path d="M8 38V24h6v14m7 0V17h6v21m7 0V9h6v29M5 39h39M7 19 21 10l9 4L41 4"/></svg><div><h2>${safe(account?.name||'Selecione uma conta')}</h2><p>${safe([account?.broker,account?.login,account?.currency].filter(Boolean).join(' · '))}</p><small>${account?.archived?'Conta histórica · consulta':'Seleção analítica independente da operação'}</small></div></div><dl>${label(model,'growth','Crescimento no período','%')}</dl>`;
    if(model.series?.growth?.length)el('fxcIdentity').insertAdjacentHTML('beforeend',chart(model.series.growth,'Crescimento observado','blue','%'));el('fxcRadar').innerHTML=radar(model);el('fxcBars').innerHTML=bars(model);
    const issues=(model.issues||[]).map(i=>i.message||i.code||String(i));
    el('fxcCoverage').textContent=`Fonte: ${ui.source==='manual'?'operações manuais finalizadas':'relatórios MT5'} · ${account?'Conta '+(account.login||account.id):'Conta não selecionada'}${issues.length?' · '+issues.join(' · '):''}`;
    const receipt=S.fxConsolidated?.receipts?.find(r=>r.id===model.coverage?.lastReceiptId);
    el('fxcCoverage').textContent+=` · Período: ${model.period?.from||'início não informado'} → ${model.period?.to||'fim não informado'} · Fuso: ${model.period?.timezone&&model.period.timezone!=='unknown'?model.period.timezone:'não informado'}${ui.source==='mt5'?' · Última importação: '+(receipt?.importedAt||'não disponível'):''}`;
    el('fxcCoverage').title='Metodologia '+(model.methodologyVersion||'não disponível')+'. MT5: custos assinados uma vez; vitórias e médias por execução de saída; lucro bruto antes dos custos. Manual: resultado líquido da operação capturada. Saldo não equivale a equity.';
    panels(model);notify(ui.message,ui.kind);
  }
  function settingsMarkup(){return `<div class="fxc-settings"><p>Escolha a conta aberta inicialmente no Consolidado FX. Esta preferência não altera a conta operacional.</p><label>Conta padrão<select id="fxcDefaultAccount"></select></label><button type="button" id="fxcSaveDefault">Salvar preferência</button><p id="fxcDefaultStatus" role="status" aria-live="polite"></p></div>`;}
  function bindSettings(){const select=el('fxcDefaultAccount');if(!select)return;select.innerHTML=options(FX.accounts?.()||[],S.fxConsolidated?.defaultAccountId||'',true);const button=el('fxcSaveDefault');button.onclick=async()=>{button.disabled=true;try{const result=await FX.saveDefaultAccount(select.value||null);el('fxcDefaultStatus').textContent=result?.ok?'Preferência salva.':(result?.error?.message||result?.error||'Não foi possível confirmar a preferência.');if(result?.ok){cancel();ui.accountId=null;render();}}catch(error){el('fxcDefaultStatus').textContent='Preferência não confirmada: '+(error.message||String(error));}finally{button.disabled=false;}};}
  function reset(){cancel();ui.accountId=null;ui.source='mt5';ui.tab='account';ui.from='';ui.to='';ui.search='';ui.message='';for(const id of ['fxcFrom','fxcTo','fxcSearch','fxcFile'])if(el(id))el(id).value='';if(el('fxcImport'))el('fxcImport').hidden=true;render();}
  Object.assign(FX,{render,settingsMarkup,bindSettings,openAccountRegistration,openAccountSetup,openImport,reset});
  window.JPWFXConsolidatedUI={openAccountSetup,openImport};
})(window.JPWFXConsolidated=window.JPWFXConsolidated||{});

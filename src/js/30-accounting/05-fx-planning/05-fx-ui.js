// ============ PLANEJAMENTO FX · INTERFACE (tela principal própria) ============
// Renderiza dentro de #fxPlanningRoot (index.html, tela #fxplan — quinta tela
// principal da rail, mesma mecânica .tab/data-screen das demais). Quatro modos
// INTERNOS: Visão Geral · Planejamento · Realizado · Tabela mensal.
// Nenhum cálculo financeiro vive aqui — tudo vem de window.JPWFx.engine/state.
// Terminologia obrigatória: premissa/projeção/simulação; campos PLANEJADOS e
// REALIZADOS nunca aparecem com a mesma semântica visual (badges PREMISSA/REAL).

let fxpView='table';           // Tabela mensal é a superfície principal; estado só de UI.
const fxpTimelineDisclosureState={planning:true,table:false};
let fxpChartMode='usd';
// Janela de exibição do gráfico em meses (1c). Recorte VISUAL sobre a série já
// calculada — nunca toca horizonte, baseline, projeção ou persistência. Não
// persiste, como os demais estados de UI desta tela.
let fxpHorizonWin=24;
// Filtro do Histórico (1g): 'all' | 'actual' | 'forecast'. Recorte de leitura,
// não de dado — o resumo anual segue calculado sobre o horizonte inteiro.
let fxpHistFilter='all';
let fxpScenarioId=null;
// Comparison is independent of the editing layer and never enters S/backup.
const fxpChartComparison={scope:null,scenarioIds:[],baseline:false,selectedMonth:null};
function fxpSyncChartComparison(live){
  const scope=JSON.stringify([jpWealthPersistenceEpoch(),live?.plan.id||null]);
  if(fxpChartComparison.scope!==scope){fxpChartComparison.scope=scope;fxpChartComparison.scenarioIds=[];fxpChartComparison.baseline=false;fxpChartComparison.selectedMonth=null;}
  const available=new Set((live?.plan.scenarios||[]).map(item=>item.id));
  fxpChartComparison.scenarioIds=fxpChartComparison.scenarioIds.filter(id=>available.has(id)).slice(0,2);
  return {scenarioIds:[...fxpChartComparison.scenarioIds],baseline:fxpChartComparison.baseline};
}
function fxpChartControlsHTML(live){
  const selection=fxpSyncChartComparison(live),scenarios=live.plan.scenarios||[];
  return `<div class="fxp-chart-controls" role="group" aria-label="Janela e moeda das trajetórias">
    ${fxpHorizonHTML(live.plan)}
    ${['usd','brl'].map(mode=>`<button type="button" class="reset-btn fxp-mode${fxpChartMode===mode?' fxp-mode-on':''}" data-fxp-cur="${mode}" aria-pressed="${fxpChartMode===mode}">${mode.toUpperCase()}</button>`).join('')}</div>
    <details class="fxp-chart-comparison"><summary>Comparar hipóteses · ${selection.scenarioIds.length} de 2 cenários</summary>
    <fieldset><legend>Cenários salvos · escolha até dois</legend>${scenarios.length?scenarios.map(item=>`<label><input type="checkbox" data-fxp-compare-scenario value="${esc(item.id)}" ${selection.scenarioIds.includes(item.id)?'checked':''}> ${esc(item.name||'Cenário sem nome')}</label>`).join(''):'<p class="fxp-note">Nenhum cenário salvo. Crie uma hipótese em Editar projeção para compará-la aqui.</p>'}</fieldset>
    <label><input type="checkbox" data-fxp-compare-baseline ${selection.baseline?'checked':''}> Mostrar baseline original como referência</label>
    <p class="fxp-note" data-fxp-compare-status role="status">PLAN permanece visível. Comparar não altera a camada em edição nem salva dados.</p></details>`;
}
function fxpChartWindow(live){
  const n=Math.min(fxpHorizonWin||live.forecast.length,live.forecast.length);
  return n<live.forecast.length?{...live,forecast:live.forecast.slice(0,n),baseline:live.baseline.slice(0,n)}:live;
}
function fxpRefreshChart(root,live=fxpDisplayLive(root)){
  const box=root.querySelector('#fxpMainChart');if(!box||!live)return;
  const options={...fxpSyncChartComparison(live),reading:jpWealthPersistenceOutcomeIsUnknown()?'previous':'current'},windowed=fxpChartWindow(live);
  const scope=fxpChartComparison.scope;
  if(box.dataset.fxpComparisonScope!==scope)window.JPWScenarioFan?.destroy(box);
  box.dataset.fxpComparisonScope=scope;
  options.selectedMonth=fxpChartComparison.selectedMonth;
  options.onInspect=reading=>{if(fxpChartComparison.scope===scope)fxpChartComparison.selectedMonth=reading.month;};
  window.JPWFx.charts.fxDrawMainChart(box,live.plan,windowed,fxpChartMode,options);
  const summary=root.querySelector('#fxpMainChartSummary');
  if(summary){summary.classList.add('jpw-chart-sr-only');summary.textContent=window.JPWFx.charts.fxMainChartSummaryText(live.plan,windowed,fxpChartMode,options);}
}
function fxpBindChartControls(root,live){
  const status=root.querySelector('[data-fxp-compare-status]');
  const update=()=>{
    const selection=fxpSyncChartComparison(live);
    root.querySelectorAll('[data-fxp-compare-scenario]').forEach(input=>{input.checked=selection.scenarioIds.includes(input.value);input.disabled=selection.scenarioIds.length>=2&&!input.checked;});
    const disclosure=root.querySelector('.fxp-chart-comparison > summary');if(disclosure)disclosure.textContent='Comparar hipóteses · '+selection.scenarioIds.length+' de 2 cenários';
    if(status)status.textContent=selection.scenarioIds.length===2?'Dois cenários selecionados. Desmarque um para escolher outro. PLAN permanece visível.':'PLAN permanece visível. Comparar não altera a camada em edição nem salva dados.';
  };
  root.querySelectorAll('[data-fxp-compare-scenario]').forEach(input=>input.addEventListener('change',()=>{
    fxpSyncChartComparison(live);
    if(input.checked&&!fxpChartComparison.scenarioIds.includes(input.value)&&fxpChartComparison.scenarioIds.length<2)fxpChartComparison.scenarioIds.push(input.value);
    if(!input.checked)fxpChartComparison.scenarioIds=fxpChartComparison.scenarioIds.filter(id=>id!==input.value);
    update();fxpRefreshChart(root,live);
  }));
  root.querySelector('[data-fxp-compare-baseline]')?.addEventListener('change',event=>{fxpChartComparison.baseline=event.target.checked;fxpRefreshChart(root,live);});
  root.querySelectorAll('[data-fxp-cur]').forEach(button=>button.addEventListener('click',()=>{
    fxpChartMode=button.dataset.fxpCur;
    root.querySelectorAll('[data-fxp-cur]').forEach(item=>{const on=item.dataset.fxpCur===fxpChartMode;item.classList.toggle('fxp-mode-on',on);item.setAttribute('aria-pressed',String(on));});
    fxpRefreshChart(root,live);
  }));
  root.querySelectorAll('[data-fxp-win]').forEach(button=>button.addEventListener('click',()=>{
    fxpHorizonWin=+button.dataset.fxpWin;
    root.querySelectorAll('[data-fxp-win]').forEach(item=>{const on=+item.dataset.fxpWin===fxpHorizonWin;item.classList.toggle('fxp-mode-on',on);item.setAttribute('aria-pressed',String(on));});
    fxpRefreshChart(root,live);
  }));
  update();fxpRefreshChart(root,live);
}
let fxpSelectedMonth=null;
let fxpLedgerPreview=null;
// One transient presentation per view/context. Navigation never persists it.
const fxpPresentationByScope=new Map();

const fxpPct=v=>Number.isFinite(v)?(v*100).toFixed(2).replace('.',',')+'%':'—';
const fxpParseNum=v=>{const text=String(v??'').trim().replace(',','.');if(!text)return null;const n=Number(text);return Number.isFinite(n)?n:null;};
const fxpEditablePct=v=>Number.isFinite(v)?String(v*100).replace('.',','):'';
// A percentage representation is not a new original input. Multiplication and
// division can change a double by one ULP even when its text was untouched.
const fxpParsePct=(v,original)=>{const n=fxpParseNum(v);return n==null?null:Number.isFinite(original)&&n===original*100?original:n/100;};
const fxpErrHTML=errors=>`<div class="fxp-err" role="alert">${errors.map(e=>esc(e)).join('<br>')}</div>`;
const fxpBadge=(kind)=>(kind==='REAL'||kind==='ACTUAL')
  ?'<span class="fxp-badge fxp-badge-real">'+kind+'</span>'
  :(kind==='PROJ'?'<span class="fxp-badge fxp-badge-proj">PREMISSA</span>':'<span class="fxp-badge">'+esc(kind)+'</span>');

// Somente entradas recusadas são retidas durante esta sessão, fora de S e do
// armazenamento. Reentrada não apaga o rascunho; recarga não promete recuperá-lo.
// Cada formulário é independente: salvar um aporte não descarta um mês recusado.
const fxpRejectedDrafts={};
// Unsubmitted inputs are session work too. Keep them outside S/storage and
// bind each group to the plan/epoch (and the scenario for the monthly editor).
const fxpInputDrafts=new Map();
let fxpRestoringInputDrafts=false,fxpRendering=false;
const FXP_DRAFT_FIELDS={
  create:['fxpName','fxpStart','fxpHorizon','fxpInitial','fxpDefaultRate','fxpProjFx','fxpRecPersonal','fxpRecProp'],
  planning:['fxpEditRate','fxpEditProjFx','fxpEditYearOvr','fxpEditMonthOvr','fxpEditRecPersonal','fxpEditRecProp','fxpEditNote'],
  actual:['fxpActMonth','fxpActType','fxpActValue','fxpActFx','fxpActNotes','fxpActConfirmed'],
  contribution:['fxpCMonth','fxpCSource','fxpCCurrency','fxpCAmount','fxpCRate'],
  deletion:['fxpDeleteConfirm'],
  removal:[],
  timeline:['fxpRowMonth','fxpRowRate','fxpRowPersonal','fxpRowProp','fxpRowNote','fxpRebaseOpening'],
  ledgerImport:['fxpLedgerMonth','fxpLedgerAccount','fxpLedgerPeriod'],
  scenario:['fxpScenarioName']
};
function fxpDraftKey(root,group){
  const scope=root?.__fxpDraftScope;
  return scope?JSON.stringify([scope.epoch,scope.planId,group,group==='timeline'?scope.scenarioId:null]):null;
}
function fxpBindInputDrafts(root){
  if(root.__fxpDraftBound)return;root.__fxpDraftBound=true;
  const remember=event=>{
    if(fxpRestoringInputDrafts||fxpRendering||!root.contains(event.target))return;
    const group=Object.keys(FXP_DRAFT_FIELDS).find(key=>FXP_DRAFT_FIELDS[key].includes(event.target.id));
    if(!group)return;
    const fields={};
    for(const id of FXP_DRAFT_FIELDS[group]){const input=root.querySelector('#'+id);if(input)fields[id]=input.type==='checkbox'?input.checked:input.value;}
    fxpInputDrafts.set(fxpDraftKey(root,group),{group,fields});
  };
  root.addEventListener('input',remember);root.addEventListener('change',remember);
}
function fxpForgetDraft(group){
  delete fxpRejectedDrafts[group];
  fxpInputDrafts.delete(fxpDraftKey(document.getElementById('fxPlanningRoot'),group));
}
function fxpRestoreInputDrafts(root){
  fxpRestoringInputDrafts=true;
  try{
    for(const group of Object.keys(FXP_DRAFT_FIELDS)){
      const draft=fxpInputDrafts.get(fxpDraftKey(root,group));if(!draft)continue;
      const entries=Object.entries(draft.fields).map(([id,value])=>[root.querySelector('#'+id),value]).filter(([input])=>input);
      for(const [input,value] of entries){
        // Account changes may rebuild the period options. Validate each choice
        // after its predecessor and leave missing identities unselected.
        if(input.type==='checkbox')input.checked=!!value;else input.value=input.tagName==='SELECT'&&![...input.options].some(option=>option.value===value)?'':value;
        input.dispatchEvent(new Event(input.tagName==='SELECT'?'change':'input',{bubbles:true}));
      }
    }
  }finally{fxpRestoringInputDrafts=false;}
}
function fxpCapturePresentation(root,active=document.activeElement){
  let focus=null;
  if(root.contains(active)){
    if(active.id)focus='#'+CSS.escape(active.id);
    else if(active.hasAttribute('data-fxp-month-action'))focus='[data-fxp-month="'+CSS.escape(active.dataset.fxpMonth)+'"][data-fxp-month-action="'+CSS.escape(active.dataset.fxpMonthAction)+'"]';
    else if(active.hasAttribute('data-fxp-hist'))focus='[data-fxp-hist="'+CSS.escape(active.dataset.fxpHist)+'"]';
    else if(active.matches('summary')&&active.parentElement.id)focus='#'+CSS.escape(active.parentElement.id)+' > summary';
  }
  return {scope:root.__fxpPresentationScope,focus,start:active?.selectionStart,end:active?.selectionEnd,scrolls:[...root.querySelectorAll('.fxp-month-scroll,.fxp-tablewrap')].map(node=>({className:node.className,left:node.scrollLeft,top:node.scrollTop})),
    details:[...root.querySelectorAll('details')].filter(node=>node.open).map(node=>node.id||node.querySelector('summary')?.textContent.trim())};
}
function fxpRememberPresentation(root,saved=fxpCapturePresentation(root)){
  if(!saved.scope)return;
  const prior=fxpPresentationByScope.get(saved.scope);
  // Clicking a navigation control blurs the editor before render. Preserve
  // that editor, rather than replacing it with an empty outside-root focus.
  fxpPresentationByScope.set(saved.scope,saved.focus||!prior? saved:{...saved,focus:prior.focus,start:prior.start,end:prior.end});
}
function fxpBindPresentationMemory(root){
  if(root.__fxpPresentationBound)return;root.__fxpPresentationBound=true;
  root.addEventListener('focusout',event=>{
    if(fxpRendering||!event.target.matches('input,textarea,select'))return;
    fxpRememberPresentation(root,fxpCapturePresentation(root,event.target));
  });
}
function fxpRestorePresentation(root,saved){
  if(saved.scope!==root.__fxpPresentationScope)return;
  root.querySelectorAll('details').forEach(node=>{node.open=saved.details.includes(node.id||node.querySelector('summary')?.textContent.trim());});
  for(const item of saved.scrolls||[]){const node=[...root.querySelectorAll('.fxp-month-scroll,.fxp-tablewrap')].find(n=>n.className===item.className);if(node){node.scrollLeft=item.left;node.scrollTop=item.top;}}
  let target=saved.focus&&root.querySelector(saved.focus);
  if(target?.disabled&&target.dataset.fxpMonth)target=root.querySelector('[data-fxp-month-row="'+target.dataset.fxpMonth+'"] [data-fxp-month-action="details"]');
  const modalOpen=[...document.querySelectorAll('dialog[open],[aria-modal="true"]')].some(node=>node.getClientRects().length&&!node.closest('[hidden],[inert]'));
  if(target&&!target.disabled&&!target.closest('[hidden],[inert]')&&target.getClientRects().length&&!modalOpen){
    target.focus({preventScroll:true});
    if(saved.start!=null&&typeof target.setSelectionRange==='function')target.setSelectionRange(saved.start,saved.end);
  }
}
function fxpRememberDraft(root,group,errorId,res){
  const fields={};
  for(const id of FXP_DRAFT_FIELDS[group]){const el=root.querySelector('#'+id);if(el)fields[id]=el.type==='checkbox'?el.checked:el.value;}
  fxpRejectedDrafts[group]={planId:jpWealthPersistenceOutcomeIsUnknown()?root.__fxpDraftScope?.planId||null:fxActivePlanRaw()?.id||null,context:fxpDraftKey(root,group),fields,errorId,errors:res.errors};
  root.querySelector('#'+errorId).innerHTML=fxpErrHTML(res.errors);
  if(jpWealthPersistenceOutcomeIsUnknown())renderFxPlanning();
}
function fxpCaptureRejectedDrafts(root){
  const planId=jpWealthPersistenceOutcomeIsUnknown()?root.__fxpDraftScope?.planId||null:fxActivePlanRaw()?.id||null;
  for(const group of Object.keys(fxpRejectedDrafts)){
    const draft=fxpRejectedDrafts[group];
    if(draft.planId!==planId){delete fxpRejectedDrafts[group];continue;}
    if(draft.context!==fxpDraftKey(root,group))continue;
    for(const id of Object.keys(draft.fields)){const el=root.querySelector('#'+id);if(el)draft.fields[id]=el.type==='checkbox'?el.checked:el.value;}
  }
}

// UNKNOWN retains the tentative aggregate in the domain for recovery. It is
// never a new confirmed reading. This snapshot is presentation only, captured
// before a command; it neither rolls back S nor acknowledges saved bytes.
function fxpRetainUnknownPresentation(root){
  if(!jpWealthPersistenceOutcomeIsUnknown())return;
  const scope=root.__fxpDraftScope,known=root.__fxpConfirmedRead,epoch=jpWealthPersistenceEpoch();
  if(!scope||!known||scope.planId!==known.planId||scope.epoch===epoch)return;
  if(scope.epoch!==known.epoch&&scope.epoch!==root.__fxpUnknownEpoch)return;
  const oldEpoch=scope.epoch,planId=scope.planId;
  const move=map=>{
    for(const [key,value] of [...map]){
      const parts=JSON.parse(key);if(parts[0]!==oldEpoch||parts[1]!==planId)continue;
      parts[0]=epoch;const nextKey=JSON.stringify(parts);
      map.delete(key);map.set(nextKey,map===fxpPresentationByScope?{...value,scope:nextKey}:value);
    }
  };
  for(const map of [fxpInputDrafts,fxpMonthlyDrafts,fxpMonthlyErrors,fxpMonthlyAuxDrafts,fxpPresentationByScope])move(map);
  for(const draft of Object.values(fxpRejectedDrafts)){
    if(!draft.context)continue;const parts=JSON.parse(draft.context);
    if(parts[0]===oldEpoch&&parts[1]===planId){parts[0]=epoch;draft.context=JSON.stringify(parts);}
  }
  if(root.__fxpPresentationScope){const parts=JSON.parse(root.__fxpPresentationScope);if(parts[0]===oldEpoch&&parts[1]===planId){parts[0]=epoch;root.__fxpPresentationScope=JSON.stringify(parts);}}
  root.__fxpDraftScope={...scope,epoch};root.__fxpUnknownEpoch=epoch;
}
function fxpDisplayLive(root){
  return jpWealthPersistenceOutcomeIsUnknown()?root.__fxpConfirmedRead?.live||null:window.JPWFx.state.fxOverviewLive();
}
function fxpUnknownNoticeHTML(hasPrevious=true){
  if(!jpWealthPersistenceOutcomeIsUnknown())return '';
  return `<p class="fxp-read-warning" role="alert"><b>Gravação indeterminada.</b> ${hasPrevious?'Leitura anterior, sem confirmação da tentativa. Rascunhos preservados.':'Valores atuais indisponíveis; nenhuma leitura anterior segura está disponível.'} Não repita ações; confira a base salva na recuperação.</p>`;
}
function fxpQualifyUnknownReading(root){
  if(!jpWealthPersistenceOutcomeIsUnknown())return;
  root.dataset.fxpReading='unknown';
  root.querySelectorAll('[data-fxp-month-row]').forEach(row=>{
    row.dataset.fxpMonthState='UNKNOWN';row.classList.remove('fxp-month-finalized');
    const status=row.querySelector('[data-fxp-status]');if(status)status.textContent='Gravação indeterminada';
  });
  const writes=['fxpCreateBtn','fxpReviseBtn','fxpDeleteBtn','fxpActBtn','fxpCBtn','fxpRowSave','fxpRebaseSave','fxpScenarioCreate','fxpScenarioArchive','fxpLedgerImportBtn'];
  for(const id of writes){const button=root.querySelector('#'+id);if(button){button.disabled=true;button.title='Gravação indeterminada: confira a recuperação antes de continuar';}}
  root.querySelectorAll('[data-fxp-del],[data-fxp-month-action]').forEach(button=>{
    if(['details','ledger','cancel'].includes(button.dataset.fxpMonthAction))return;
    button.disabled=true;button.title='Gravação indeterminada: não repita a ação';
  });
}
function fxpRestoreRejectedDrafts(root){
  for(const [group,draft] of Object.entries(fxpRejectedDrafts)){
    if(draft.context!==fxpDraftKey(root,group))continue;
    for(const [id,value] of Object.entries(draft.fields)){
      const el=root.querySelector('#'+id);if(!el)continue;
      if(el.type==='checkbox')el.checked=!!value;else el.value=value;
      // Mês vem antes dos demais campos: seu prefill roda primeiro. Depois,
      // as prévias recebem os valores originais, sem fórmulas ou gravações novas.
      el.dispatchEvent(new Event(el.tagName==='SELECT'?'change':'input',{bubbles:true}));
    }
    const err=root.querySelector('#'+draft.errorId);if(err)err.innerHTML=fxpErrHTML(draft.errors);
  }
  if(jpWealthPersistenceOutcomeIsUnknown()){
    const notice=document.createElement('div');
    notice.innerHTML=fxpErrHTML(['Gravação indeterminada. Não repita ações; confira a base salva antes de continuar.']);
    root.prepend(notice);
  }
}

function fxpCurrentMonthKey(){ return new Date().toISOString().slice(0,7); }

// ---- Referência USD/BRL corrente (JPW-FGDEKM) -------------------------------
// Indicador único da tela: explica com QUE taxa o presente é convertido. Não se
// repete card a card. Nunca chama o dado de "ao vivo": a fonte publica uma
// referência por dia útil, então mostramos a data econômica (referenceDate) e,
// separadamente, quando consultamos (fetchedAt).
const fxpQuote=()=>(window.JPWMarket&&window.JPWMarket.usdBrl)?window.JPWMarket.usdBrl:null;
function fxpFmtRef(d){
  if(!d) return '—';
  const p=String(d).split('-');
  return p.length===3?`${p[2]}/${p[1]}/${p[0]}`:String(d);
}
function fxpFmtHora(ts){
  return ts?new Date(ts).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}):'—';
}
function fxpQuoteHTML(){
  const m=fxpQuote(); if(!m) return '';
  const q=m.get(), carregando=m.isLoading();
  // O botão só sinaliza disponibilidade; quem narra o estado é a mensagem. Ter
  // os dois dizendo "Consultando…" imprimia o texto duas vezes seguidas.
  const btn=`<button type="button" class="reset-btn fxp-quote-btn" id="fxpQuoteRefresh"${carregando?' disabled':''}>Atualizar cotação</button>`;
  if(carregando && q.status==='unavailable')
    return `<div class="fxp-quote" id="fxpQuoteBox" role="status"><span class="fxp-quote-lbl">USD/BRL de referência</span><span class="fxp-quote-msg">Consultando referência…</span>${btn}</div>`;
  if(q.status==='unavailable')
    return `<div class="fxp-quote fxp-quote-off" id="fxpQuoteBox" role="status">
      <span class="fxp-quote-lbl">USD/BRL de referência</span>
      <span class="fxp-quote-msg">Indisponível — valores presentes exibidos em USD. A premissa de câmbio futuro não é usada para marcar o presente.</span>${btn}</div>`;
  const velha=q.status==='stale';
  return `<div class="fxp-quote${velha?' fxp-quote-stale':''}" id="fxpQuoteBox" role="status">
    <span class="fxp-quote-lbl">USD/BRL de referência</span>
    <span class="fxp-quote-val">R$ ${q.rate.toFixed(4).replace('.',',')}</span>
    <span class="fxp-quote-meta">Referência ${fxpFmtRef(q.referenceDate)} · consultado às ${fxpFmtHora(q.fetchedAt)}</span>
    ${velha?'<span class="fxp-quote-tag">consulta desatualizada — revalidando</span>':''}
    ${btn}</div>`;
}
function fxpBindQuote(root){
  const m=fxpQuote(); if(!m) return;
  const b=root.querySelector('#fxpQuoteRefresh');
  if(b) b.addEventListener('click',()=>m.refresh(true));
}
// Registrado UMA vez: se ficasse dentro do render, cada repintura empilharia
// mais um ouvinte e a tela entraria em laço.
var fxpQuoteWired=false;
function fxpWireQuoteOnce(){
  const m=fxpQuote(); if(!m || fxpQuoteWired) return;
  fxpQuoteWired=true;
  m.onChange(()=>{ if(fxpView==='overview') renderFxPlanning(); });
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState==='visible' && fxpView==='overview') m.refresh(false);
  });
}

// ---- Formulário de criação (estado vazio) -----------------------------------
// Estado vazio (1h): as três camadas explicadas à esquerda com o vocabulário de
// badges do produto, formulário à direita em três blocos. Todos os ids são os
// mesmos — fxpBindCreate e o teste dependem deles; muda a arrumação, não o
// contrato de DOM.
function fxpCreateFormHTML(){
  return `
  <div class="fxp-empty-shell">
    <div class="fxp-empty-kicker"><i aria-hidden="true"></i>Planejamento FX</div>
    <h3>Nenhum planejamento ativo</h3>
    <p class="fxp-empty-lead">Registre a trajetória patrimonial separando <b>premissas</b> ${fxpBadge('PROJ')}, <b>realizado</b> ${fxpBadge('REAL')} e <b>normativo</b> (FCR/FEO). Ao aprovar, as premissas viram o baseline congelado.</p>
    <details class="fxp-empty-method">
      <summary>Como as três camadas funcionam</summary>
      <div class="fxp-empty-method-grid">
        <p><b>Premissas.</b> Rentabilidade mensal, câmbio projetado e aportes. Revisões nunca sobrescrevem o baseline.</p>
        <p><b>Realizado.</b> Fechamentos contíguos e ledger cambial; custo médio do dólar = Σ BRL ÷ Σ USD.</p>
        <p><b>Normativo.</b> FCR e FEO pela mesma função do Formulário de Início; este painel informa e não movimenta capital.</p>
      </div>
    </details>
    <div class="fxp-empty-form-grid">
      <div class="field"><label for="fxpName">Nome do planejamento</label><input type="text" id="fxpName" placeholder="ex.: Trajetória Família 10 anos"></div>
      <div class="field"><label for="fxpStart">Mês inicial</label><input type="month" id="fxpStart" value="${fxpCurrentMonthKey()}"></div>
      <div class="field"><label for="fxpHorizon">Horizonte (meses)</label><input type="number" min="1" max="600" step="1" id="fxpHorizon" value="60"></div>
      <div class="field"><label for="fxpInitial">Saldo inicial (USD)</label><input type="number" step="0.01" id="fxpInitial" placeholder="0.00"><span class="note">Não altera a Conta Mestre.</span></div>
      <div class="field"><label for="fxpDefaultRate">Rentabilidade planejada (% a.m.)</label><input type="text" id="fxpDefaultRate" placeholder="ex.: 1,50"><span class="note">Premissa sua, não meta do sistema.</span></div>
      <div class="field"><label for="fxpProjFx">Câmbio projetado (R$/USD)</label><input type="text" id="fxpProjFx" placeholder="ex.: 5,40"><span class="note">Opcional — só para projeções em BRL.</span></div>
      <div class="field"><label for="fxpRecPersonal">Aporte pessoal mensal (USD)</label><input type="number" step="0.01" id="fxpRecPersonal" placeholder="0.00"></div>
      <div class="field"><label for="fxpRecProp">Aporte Prop Firm mensal (USD)</label><input type="number" step="0.01" id="fxpRecProp" placeholder="0.00"></div>
    </div>
    <div id="fxpCreateErr"></div>
    <div class="fxp-empty-actions"><button class="unlock-phase-btn" id="fxpCreateBtn">Aprovar planejamento</button><span>as premissas congelam como baseline nesta aprovação</span></div>
  </div>`;
}
function fxpRecurringMap(start,horizon,personal,prop){
  const map={};
  if((personal||0)>0||(prop||0)>0)
    for(let t=0;t<horizon;t++) map[fxAddMonths(start,t)]={personalUsd:personal||0,propUsd:prop||0};
  return map;
}
function fxpBindCreate(root){
  const btn=root.querySelector('#fxpCreateBtn'); if(!btn) return;
  btn.addEventListener('click',()=>{
    const g=id=>root.querySelector('#'+id).value;
    const start=fxMonthKey(g('fxpStart')), horizon=Math.round(fxpParseNum(g('fxpHorizon'))||0);
    const assumptions={
      startMonth:start, horizonMonths:horizon,
      initialBalanceUsd:fxpParseNum(g('fxpInitial'))||0,
      defaultMonthlyReturn:fxpParsePct(g('fxpDefaultRate')),
      projectedFxRate:fxpParseNum(g('fxpProjFx')),
      plannedContributions:{},
      recurringContributions:{personalUsd:fxpParseNum(g('fxpRecPersonal'))??0,propUsd:fxpParseNum(g('fxpRecProp'))??0}
    };
    if(assumptions.defaultMonthlyReturn==null){ root.querySelector('#fxpCreateErr').innerHTML=fxpErrHTML(['Informe a rentabilidade planejada em % ao mês.']); return; }
    const res=window.JPWFx.state.fxPlanCreate({name:g('fxpName'),assumptions});
    if(!res.ok){ fxpRememberDraft(root,'create','fxpCreateErr',res); return; }
    fxpForgetDraft('create');
    renderFxPlanning();
  });
}

// ---- Modos expostos à navegação contextual ---------------------------------
// A barra interna duplicada foi removida: o único controle visível vive na
// segunda faixa do header. As chaves continuam estritamente de UI e preservam
// o contrato dos quatro renderizadores existentes.
const FXP_MODES=[['overview','Visão Geral'],['planning','Planejamento FX'],['actuals','Realizado'],['table','Tabela mensal']];
function fxpSelectView(view){
  if(!FXP_MODES.some(([key])=>key===view)) return false;
  const restoreViewFocus=fxpView!==view;
  fxpView=view;
  renderFxPlanning({restoreViewFocus});
  return true;
}
function fxpGetView(){ return fxpView; }

// ---- Visão Geral ------------------------------------------------------------
function fxpOverviewHTML(live){
  const ov=live, plan=live.plan;
  const cb=ov.costBasis;
  const res=window.JPWFx.state.fxReservePanelData();
  const todayKey=fxpCurrentMonthKey();
  const baseToday=ov.baseline.filter(r=>r.month<=todayKey).slice(-1)[0]||null;
  const dev=ov.deviationUsd;
  // Desvio nunca comunicado só por cor (P6/§15): o sinal do número e a palavra
  // acima/abaixo carregam a informação sem depender de matiz.
  const devWord=dev==null?'':(dev>=0?'acima do baseline':'abaixo do baseline');
  const congelado=(plan.baseline.frozenAt||'').slice(0,10).split('-').reverse().join('/');
  const baseMes=ov.lastClosedMonth||(baseToday?baseToday.month:'—');
  // Média realizada para o subtítulo do gráfico mensal — leitura, não cálculo
  // novo: é a média aritmética das taxas dos meses já fechados.
  const reais=(ov.forecast||[]).filter(r=>r.phase==='actual'&&(r.status||'FINALIZED')==='FINALIZED'&&Number.isFinite(r.rate));
  const mediaReal=reais.length?reais.reduce((a,r)=>a+r.rate,0)/reais.length:null;
  const planejado=plan.current.defaultMonthlyReturn;
  const nAportes=(plan.contributions||[]).length;
  return `
  <div class="fxp-grid2">
  <div class="fxp-col-main">
    <!-- Ordem do herói conforme 1c: patrimônio, DESVIO, baseline. O desvio no
         meio porque é a leitura que responde "como estou" — o baseline é a
         referência que sustenta essa comparação, não um número autônomo. -->
    <div class="fxp-kpis fxp-kpis-a">
      <div class="metric"><div class="k">Patrimônio do plano ${ov.lastClosedMonth?fxpBadge('REAL'):fxpBadge('PROJ')}</div><div class="v">${fxpBoardMoney(ov.currentBalanceUsd)}</div><div class="sub">${ov.lastClosedMonth?'fechado em '+esc(ov.lastClosedMonth):'nenhum mês fechado'}</div></div>
      <div class="metric"><div class="k">Desvio vs baseline</div><div class="v" style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${dev!=null?fxpBoardMoney(dev):'—'}</div><div class="sub">${dev!=null?`${ov.deviationPct!=null?fxpPct(ov.deviationPct):'—'} · ${devWord}`:'sem mês fechado'}</div></div>
      <div class="metric"><div class="k">Baseline para ${esc(baseMes)} ${fxpBadge('PROJ')}</div><div class="v">${ov.baselineBalanceAtLastClose!=null?fxpBoardMoney(ov.baselineBalanceAtLastClose):(baseToday?fxpBoardMoney(baseToday.close):'—')}</div><div class="sub">${congelado?'congelado '+esc(congelado):'—'}</div></div>
    </div>

    <section class="fxp-block">
      <div class="fxp-block-head">
        <span class="art">Realizado · PLAN · hipóteses salvas</span>
        <span class="fxp-spacer"></span>

      </div>
      ${fxpChartControlsHTML(live)}
      <div id="fxpMainChart"></div>
      <p class="fxp-note" id="fxpMainChartSummary"></p>
    </section>

    <section class="fxp-block">
      <div class="fxp-block-head">
        <h3>Rentabilidade mensal</h3>
        <span class="art">planejado ${planejado!=null?fxpPct(planejado)+' a.m.':'—'} × realizado${mediaReal!=null?', média '+fxpPct(mediaReal):''}</span>
      </div>
      <div id="fxpReturnsChart"></div>
    </section>

    <div class="fxp-kpis fxp-kpis-c">
      <div class="metric"><div class="k">Aportes realizados ${fxpBadge('REAL')}</div><div class="v">${fxpBoardMoney(ov.contributedTotalUsd)}</div><div class="sub">pessoal ${fxpBoardMoney(ov.contributedPersonalUsd)} · prop ${fxpBoardMoney(ov.contributedPropUsd)}</div></div>
    </div>
  </div>

  <aside class="fxp-col-side">
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Reservas estatutárias</h3><span class="art">Art. 13</span></div>
      ${fxpCovHTML('FCR · Contingência e Reconstituição',res.fcrCoverage,res.fcrStatus,
        `constituído ${fxpMoneyOrPending(res.fcrCur)} · exigido ${fxpMoneyOrPending(res.fcrReq)}`+(res.fcrDiff<0?` · déficit ${fxpBoardMoney(-res.fcrDiff)}`:''))}
      ${fxpCovHTML('FEO · Estabilidade Operacional',res.feoCoverage,res.feoStatus,
        `constituído ${fxpMoneyOrPending(res.feoCur)} · apurado ${fxpMoneyOrPending(res.feoReq)}`+(res.feoDiff<0?` · déficit ${fxpBoardMoney(-res.feoDiff)}`:''))}
      <p class="expl" style="font-size:var(--fs-xs);color:var(--ink-faint);margin:10px 0 0;line-height:1.55">Constituição quantitativa não confirma elegibilidade. Apuração, liquidez e governança permanecem verificações distintas.</p>
      <button type="button" class="fxp-linkish" id="fxpGoOnboarding" style="margin-top:8px">Revisar Reservas</button>
      <div id="fxpReservesPanel">${fxpReservesHTML(res)}</div>
    </section>

    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Ledger cambial</h3></div>
      <dl class="fxp-pairs">
        <dt>Câmbio médio de aquisição</dt><dd class="hl">${cb.weightedAverageFx!=null?'R$ '+cb.weightedAverageFx.toFixed(4).replace('.',','):'—'}</dd>
        <dt>BRL convertido</dt><dd>${cb.totalBrlInvested?'R$ '+Math.round(cb.totalBrlInvested).toLocaleString('pt-BR'):'—'}</dd>
        <dt>USD adquirido</dt><dd>${cb.totalUsdAcquired?fxpBoardMoney(cb.totalUsdAcquired):'—'}</dd>
        <dt>Crédito USD nativo (prop)</dt><dd>${fxpBoardMoney(ov.contributedPropUsd)}</dd>
      </dl>
      ${fxpQuoteHTML()}
      <p class="expl" style="font-size:var(--fs-xs);color:var(--ink-faint);margin:10px 0 0;line-height:1.55">Σ BRL ÷ Σ USD, média ponderada. Crédito USD nativo não entra no custo médio.</p>
      <button type="button" class="fxp-linkish" id="fxpGoLedger" style="margin-top:8px">Ver ${nAportes} lançamento${nAportes===1?'':'s'} ›</button>
    </section>
  </aside>
  </div>`;
}
// Barra de cobertura normativa. O rótulo textual acompanha sempre — estado
// normativo nunca é comunicado só pela cor da barra.
function fxpMoneyOrPending(value){return Number.isFinite(value)?fxpBoardMoney(value):'não informado';}
function fxpCovHTML(rotulo,cobertura,status,meta){
  const known=Number.isFinite(cobertura),cor=status==='Insuficiente'?'var(--f4)':'var(--ink-dim)';
  const larg=known?Math.max(0,Math.min(100,cobertura)):0;
  return `<div class="fxp-cov"><div class="fxp-cov-top"><span class="fxp-cov-lbl">${esc(rotulo)}</span><span class="fxp-cov-val" style="color:${cor}">${known?fxpPct(cobertura/100):'não calculável'}</span></div>${known?`<div class="fxp-cov-bar"><div class="fxp-cov-fill" style="width:${larg.toFixed(1)}%;background:${cor}"></div></div>`:''}<div class="fxp-cov-meta">${meta} · ${esc(status)}</div></div>`;
}
// Janela de exibição do gráfico (1c). É recorte VISUAL da série já calculada:
// não altera horizonte, baseline, projeção nem nada persistido.
function fxpHorizonHTML(plan){
  const H=plan.baseline.horizonMonths;
  const ops=[...new Set([12,24,60,H].filter(n=>n<=H))].sort((a,b)=>a-b);
  if(ops.length<2) return '';
  return ops.map(n=>`<button type="button" class="reset-btn fxp-mode${fxpHorizonWin===n?' fxp-mode-on':''}" data-fxp-win="${n}" aria-pressed="${fxpHorizonWin===n}">${n}m</button>`).join('');
}
// Camada D (P4/P5): os cards FCR/FEO acima já são o resumo; a tabela estatutária
// completa desce para disclosure, eliminando a duplicação perceptiva. Abaixo de
// 700px o CSS converte cada linha em rótulo→valor: antes, no mobile, a coluna de
// valores nascia fora da tela e a tabela mostrava apenas os rótulos.
function fxpReservesHTML(res){
  const row=(k,v)=>`<tr class="fxp-reserve-row"><td>${k}</td><td>${v}</td></tr>`;
  return `<details class="mc-disclosure fxp-disc fxp-reserves"><summary>Detalhes e governança das reservas</summary><div class="mc-disclosure-body"><div class="fxp-tablewrap"><table class="dtable"><tbody>
    ${row('Capital nominal explícito da Conta Mestre',fxpMoneyOrPending(res.capital))}
    ${row('FCR exigido pelo motor V11',fxpMoneyOrPending(res.fcrReq))}
    ${row('FCR constituído',fxpMoneyOrPending(res.fcrCur))}
    ${row('FEO apurado para seis meses de despesas reais',fxpMoneyOrPending(res.feoReq))}
    ${row('FEO constituído',fxpMoneyOrPending(res.feoCur))}
    ${row('Situação quantitativa',esc(res.generalStatus))}
    ${row('Governança',esc(res.status||'PENDING_GOVERNANCE'))}
    </tbody></table></div><ul>${(res.findings||[]).map(f=>`<li>${esc(f.message||f.code)}</li>`).join('')}</ul><p class="fxp-note">Valor calculado não resolve conflitos documentais nem concede autorização operacional. SI não substitui capital nominal; uma média mensal não substitui a apuração explícita de seis meses.</p></div></details>`;
}

// ---- Planejamento (premissas vigentes) --------------------------------------
function fxpPlanningHTML(live){
  const plan=live.plan, cur=plan.current, base=plan.baseline;
  const congeladoEm=(base.frozenAt||'').slice(0,10).split('-').reverse().join('/');
  const nFechados=(live.forecast||[]).filter(r=>r.phase==='actual').length;
  const ovr=(obj)=>Object.entries(obj).map(([k,v])=>`${k}=${fxpEditablePct(v)}%`).join('; ');
  return `
  <p class="fxp-note">Baseline congelado em <b>${esc((base.frozenAt||'').slice(0,10)||'—')}</b> · ${plan.revisions.length} revisão(ões) de premissas registradas.
  Revisar premissas altera apenas a <b>projeção futura</b> — o baseline original e os meses realizados permanecem intactos para comparação.</p>
  <div class="fxp-grid2">
  <div class="fxp-col-main">
  <!-- 1e: estruturais e revisáveis deixam de compartilhar a mesma grade. O que
       está congelado não aparece como campo desabilitado no meio dos editáveis
       — vira leitura, com a data do congelamento. -->
  <section class="fxp-block">
    <div class="fxp-block-head"><h3>Estruturais</h3><span class="art">congelados com o baseline${congeladoEm?' em '+esc(congeladoEm):''} — não editáveis</span></div>
    <dl class="fxp-pairs">
      <dt>Mês inicial</dt><dd>${esc(base.startMonth)}</dd>
      <dt>Horizonte</dt><dd>${base.horizonMonths} meses</dd>
      <dt>Saldo inicial (USD)</dt><dd class="hl">${fxpBoardMoney(base.initialBalanceUsd)}</dd>
    </dl>
  </section>
  <section class="fxp-block">
  <div class="fxp-block-head"><h3>Revisáveis</h3><span class="art">alteram apenas a projeção futura</span></div>
  <div class="params-grid">
    <div class="field"><label for="fxpEditRate">Rentabilidade padrão vigente (% a.m.)</label><input type="text" id="fxpEditRate" value="${fxpEditablePct(cur.defaultMonthlyReturn)}"></div>
    <div class="field"><label for="fxpEditProjFx">Câmbio projetado (R$/USD)</label><input type="text" id="fxpEditProjFx" value="${cur.projectedFxRate!=null?String(cur.projectedFxRate).replace('.',','):''}" placeholder="ex.: 5,40"><span class="note">Premissa de projeção — nunca reescreve o custo histórico de aquisição.</span></div>
    <div class="field"><label for="fxpEditRecPersonal">Depósito pessoal recorrente (USD)</label><input type="number" step="0.01" id="fxpEditRecPersonal" value="${cur.recurringContributions?.personalUsd??0}"><span class="note">Preserva exceções mensais, previsões retiradas e realizados.</span></div>
    <div class="field"><label for="fxpEditRecProp">Depósito Prop recorrente (USD)</label><input type="number" step="0.01" id="fxpEditRecProp" value="${cur.recurringContributions?.propUsd??0}"></div>
    <div class="field"><label for="fxpEditNote">Nota da revisão</label><input type="text" id="fxpEditNote" placeholder="motivo da mudança de premissa"></div>
  </div>
  <details class="mc-disclosure fxp-disc">
    <summary><span class="t">Configurações avançadas — exceções por ano e por mês</span><span class="chev">▾</span></summary>
    <div class="mc-disclosure-body">
      <div class="params-grid">
        <div class="field"><label for="fxpEditYearOvr">Overrides por ano</label><input type="text" id="fxpEditYearOvr" value="${esc(ovr(cur.yearOverrides))}" placeholder="2028=1,20%; 2029=1,00%" aria-describedby="fxpYearOvrEcho"><span class="note">Formato AAAA=%; separados por ponto e vírgula.</span><span class="note" id="fxpYearOvrEcho"></span></div>
        <div class="field"><label for="fxpEditMonthOvr">Overrides por mês</label><input type="text" id="fxpEditMonthOvr" value="${esc(ovr(cur.monthOverrides))}" placeholder="2028-03=0,80%" aria-describedby="fxpMonthOvrEcho"><span class="note">Precedência: mês &gt; ano &gt; padrão.</span><span class="note" id="fxpMonthOvrEcho"></span></div>
      </div>
    </div>
  </details>
  <div id="fxpPlanningErr"></div>
  <button class="unlock-phase-btn fxp-actions" id="fxpReviseBtn">Salvar premissas vigentes</button>
  <p class="fxp-note" style="margin-top:6px">preserva o baseline e os ${nFechados} ${nFechados===1?'mês já fechado':'meses já fechados'}</p>
  </section>
  <div class="fxp-danger">
    <h4>Zona de perigo</h4>
    <p class="fxp-note">Excluir o plano ativo arquiva seu histórico completo no backup, incluindo fechamentos, revisões e aportes. O restante do terminal não é afetado. Digite <b>EXCLUIR</b> para habilitar.</p>
    <div class="fxp-danger-row">
      <input type="text" id="fxpDeleteConfirm" placeholder="EXCLUIR" aria-label="Digite EXCLUIR para confirmar">
      <button class="reset-btn" id="fxpDeleteBtn" style="color:var(--f4);border-color:var(--f4)">Excluir planejamento</button>
    </div>
    <div id="fxpDeleteErr"></div>
  </div>
  </div>

  <aside class="fxp-col-side">
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Efeito da revisão sobre a projeção</h3><span class="art">${fxpBadge('PROJ')}</span></div>
      <dl class="fxp-pairs" id="fxpRevPreview">
        <dt>Vigente antes da revisão</dt><dd id="fxpRevBefore">—</dd>
        <dt>Com as premissas na tela</dt><dd class="hl" id="fxpRevAfter">—</dd>
        <dt>Baseline congelado</dt><dd id="fxpRevBase">—</dd>
      </dl>
      <p class="fxp-derived-preview" id="fxpRevDelta" aria-live="polite"></p>
      <p class="expl" style="font-size:var(--fs-xs);color:var(--ink-faint);margin:10px 0 0;line-height:1.55">Rentabilidade planejada é premissa sua — não deriva de perfil de risco nem constitui promessa de retorno.</p>
    </section>
    <section class="fxp-block">
      <div class="fxp-block-head"><h3>Revisões registradas</h3><span class="art">${plan.revisions.length}</span></div>
      ${plan.revisions.length?`<dl class="fxp-pairs">${plan.revisions.slice().reverse().map(rv=>
        `<dt>${esc(String(rv.supersededAt||'').slice(0,10))}</dt><dd>${esc(rv.note||'revisão de premissas')} · ${rv.calculationSnapshot?'snapshot exato':'legado: reconstrução aproximada'}</dd>`).join('')}</dl>`
        :'<p class="fxp-note" style="margin:0">Nenhuma revisão desde o congelamento do baseline.</p>'}
    </section>
  </aside>
  </div>`;
}
function fxpParseOverrides(str,monthly,originals={}){
  const out={};
  String(str||'').split(';').map(s=>s.trim()).filter(Boolean).forEach(pair=>{
    const [k,v]=pair.split('=').map(s=>String(s||'').trim());
    const key=monthly?fxMonthKey(k):/^\d{4}$/.test(k)?k:null;
    const rate=fxpParsePct(String(v||'').replace('%',''),originals?.[key]);
    if(rate==null) return;
    if(key)out[key]=rate;
  });
  return out;
}
// Preview and writer consume one input adapter, including exact originals for
// untouched values/keys. Omitted monthly exceptions use the writer's merge.
function fxpReadGeneralAssumptions(root,current){
  const value=id=>root.querySelector('#'+id).value;
  return {defaultMonthlyReturn:fxpParsePct(value('fxpEditRate'),current.defaultMonthlyReturn),
    yearOverrides:fxpParseOverrides(value('fxpEditYearOvr'),false,current.yearOverrides),
    monthOverrides:{...current.monthOverrides,...fxpParseOverrides(value('fxpEditMonthOvr'),true,current.monthOverrides)},
    recurringContributions:{personalUsd:fxpParseNum(value('fxpEditRecPersonal')),propUsd:fxpParseNum(value('fxpEditRecProp'))},
    projectedFxRate:fxpParseNum(value('fxpEditProjFx'))};
}
function fxpBindPlanning(root,live){
  const q=id=>root.querySelector('#'+id);
  // Afordância dos overrides (P7): o campo é texto livre com sintaxe própria, e
  // nada dizia ao operador se ele acertou. O eco devolve o que o MESMO parser do
  // salvamento entendeu — sem tocar em schema, domínio ou formato persistido.
  const echo=(inputId,echoId,monthly)=>{
    const inp=q(inputId), out=q(echoId); if(!inp||!out) return;
    const render=()=>{
      const bruto=String(inp.value||'').split(';').map(s=>s.trim()).filter(Boolean);
      const lido=fxpParseOverrides(inp.value,monthly,monthly?live.plan.current.monthOverrides:live.plan.current.yearOverrides);
      const chaves=Object.keys(lido).sort();
      if(!bruto.length){ out.textContent=monthly?'Nenhuma exceção nova informada; as exceções mensais já salvas permanecem.':'Nenhuma exceção anual informada neste campo.'; out.style.color=''; return; }
      const desc=chaves.map(k=>`${k} = ${fxpEditablePct(lido[k])}%`).join(' · ');
      const perdidos=bruto.length-chaves.length;
      out.textContent=(chaves.length?`Entendido: ${desc}.`:'Nada reconhecido.')
        +(perdidos>0?` ${perdidos} trecho(s) não reconhecido(s) e ignorado(s) ao salvar.`:'');
      out.style.color=perdidos>0?'var(--f4)':'';
    };
    inp.addEventListener('input',render); render();
  };
  echo('fxpEditYearOvr','fxpYearOvrEcho',false);
  echo('fxpEditMonthOvr','fxpMonthOvrEcho',true);

  // Prévia do efeito da revisão (1e). Mesmo princípio da prévia do fechamento:
  // as premissas digitadas viram um conjunto CANDIDATO e quem projeta é o motor
  // (fxForecastTimeline já aceita assumptions). Nada é salvo, nada é revisado —
  // o baseline e os meses fechados seguem intactos até o botão ser apertado.
  const fim=serie=>{ const r=(serie||[])[(serie||[]).length-1]; return r?r.close:null; };
  const antes=fim(live.forecast), baseFim=fim(live.baseline);
  const previaRevisao=()=>{
    const E=window.JPWFx.engine; if(!E) return;
    const put=(id,txt)=>{ const e=q(id); if(e) e.textContent=txt; };
    put('fxpRevBefore',antes!=null?fxpBoardMoney(antes):'—');
    put('fxpRevBase',baseFim!=null?fxpBoardMoney(baseFim):'—');
    const draft=fxpReadGeneralAssumptions(root,live.plan.current),taxa=draft.defaultMonthlyReturn;
    if(taxa==null){ put('fxpRevAfter','—'); put('fxpRevDelta','Informe a rentabilidade para simular.'); return; }
    const {personalUsd,propUsd}=draft.recurringContributions;
    if(personalUsd==null||propUsd==null||personalUsd<0||propUsd<0){put('fxpRevAfter','—');put('fxpRevDelta','Informe depósitos recorrentes não negativos para simular; zero é um valor válido.');return;}
    // Match the existing writer's merge: omitted monthly exceptions are kept.
    // This is a transient input projection, not a second financial calculation.
    const candidatas={...live.plan.current,...draft};
    let atuais,candidata;
    try{atuais=E.fxForecastTimeline(live.plan);candidata=E.fxForecastTimeline(live.plan,{assumptions:candidatas});}
    catch(_){put('fxpRevAfter','—');put('fxpRevDelta','Não foi possível conferir o efeito desta revisão.');return;}
    const depois=fim(candidata);
    put('fxpRevAfter',depois!=null?fxpBoardMoney(depois):'—');
    const delta=(depois!=null&&antes!=null)?depois-antes:null;
    // Compare evidence produced by the SAME engine, including availability.
    // Existing months are not evidence that those months change.
    const beforeByMonth=new Map(atuais.map(r=>[r.month,r]));
    const differs=(a,b,fields)=>fields.some(k=>!Object.is(a?.[k],b?.[k])||a?.availability?.[k]!==b?.availability?.[k]);
    const premiseChanges=candidata.filter(r=>differs(beforeByMonth.get(r.month),r,['rate','personalUsd','propUsd']));
    const resultChanges=candidata.filter(r=>differs(beforeByMonth.get(r.month),r,['open','profit','close']));
    const stateChanges=candidata.filter(r=>{const a=beforeByMonth.get(r.month);return a?.status!==r.status||a?.reasonCode!==r.reasonCode;});
    const unavailable=candidata.filter(r=>!['open','profit','close'].every(k=>r.availability?.[k]));
    // Compact only genuinely consecutive affected rows; never bridge a hole.
    const monthRanges=rows=>{
      const selected=new Set(rows.map(r=>r.month)),ranges=[];let start=null,last=null;
      for(const r of candidata){if(selected.has(r.month)){if(start===null)start=r.month;last=r.month;}else if(start!==null){ranges.push(start===last?start:start+' a '+last);start=last=null;}}
      if(start!==null)ranges.push(start===last?start:start+' a '+last);
      return ranges.join(' · ');
    };
    const changedExceptions=[];
    for(const [label,next,previous] of [['Ano',candidatas.yearOverrides,live.plan.current.yearOverrides],['Mês',candidatas.monthOverrides,live.plan.current.monthOverrides]]){
      for(const key of new Set([...Object.keys(previous||{}),...Object.keys(next||{})]))if(!Object.is(previous?.[key],next?.[key]))changedExceptions.push(label+' '+key);
    }
    const messages=[];
    if(!premiseChanges.length&&!resultChanges.length&&!stateChanges.length)messages.push('Nenhuma premissa mensal ou valor USD muda nesta prévia.');
    if(premiseChanges.length)messages.push('Premissas mensais alteradas: '+monthRanges(premiseChanges)+'.');
    if(resultChanges.length)messages.push('Saldos ou resultados alterados: '+monthRanges(resultChanges)+'.');
    if(stateChanges.length)messages.push('Disponibilidade ou estado alterados: '+monthRanges(stateChanges)+'.');
    if(changedExceptions.length)messages.push('Exceções explicitamente alteradas: '+changedExceptions.join(' · ')+'.');
    const absent=unavailable.filter(r=>r.status==='ABSENT'),blocked=unavailable.filter(r=>r.status!=='ABSENT');
    if(absent.length)messages.push('Sem previsão: '+monthRanges(absent)+'.');
    if(blocked.length)messages.push('Cálculos ainda indisponíveis: '+monthRanges(blocked)+'. Premissas podem mudar sem confirmar saldos e resultados.');
    if(!Object.is(candidatas.projectedFxRate,live.plan.current.projectedFxRate))messages.push('Câmbio projetado de apresentação alterado; isso não modifica os valores USD.');
    if(delta!==null&&Math.abs(delta)>=0.005)messages.push(`${delta>0?'+':''}${fxpBoardMoney(delta)} ao fim do horizonte.`);
    put('fxpRevDelta',messages.join(' '));
  };
  ['fxpEditRate','fxpEditProjFx','fxpEditYearOvr','fxpEditMonthOvr','fxpEditRecPersonal','fxpEditRecProp'].forEach(id=>{
    const e=q(id); if(e) e.addEventListener('input',previaRevisao);
  });
  previaRevisao();
  q('fxpReviseBtn').addEventListener('click',()=>{
    const draft=fxpReadGeneralAssumptions(root,live.plan.current),rate=draft.defaultMonthlyReturn;
    if(rate==null){ q('fxpPlanningErr').innerHTML=fxpErrHTML(['Rentabilidade padrão inválida.']); return; }
    const {personalUsd:recP,propUsd:recF}=draft.recurringContributions;
    if(recP==null||recF==null||recP<0||recF<0){q('fxpPlanningErr').innerHTML=fxpErrHTML(['Informe depósitos recorrentes não negativos; zero é um valor válido.']);return;}
    const res=window.JPWFx.state.fxPlanReviseAssumptions(draft,q('fxpEditNote').value);
    if(!res.ok){ fxpRememberDraft(root,'planning','fxpPlanningErr',res); return; }
    fxpForgetDraft('planning');
    renderFxPlanning();
  });
  q('fxpDeleteBtn').addEventListener('click',()=>{
    if(q('fxpDeleteConfirm').value.trim()!=='EXCLUIR'){ q('fxpDeleteErr').innerHTML=fxpErrHTML(['Digite EXCLUIR para confirmar.']); return; }
    const res=window.JPWFx.state.fxPlanDelete();
    if(!res.ok){ fxpRememberDraft(root,'deletion','fxpDeleteErr',res); return; }
    for(const group of Object.keys(fxpRejectedDrafts))delete fxpRejectedDrafts[group];
    renderFxPlanning();
  });
}

// ---- Realizado (fechamento mensal + aportes) --------------------------------
function fxpActualsHTML(live){
  const plan=live.plan, next=live.nextOpenMonth;
  const closed=Object.keys(plan.actuals).sort();
  const contribs=plan.contributions.slice().sort((a,b)=>a.month.localeCompare(b.month)||String(a.createdAt).localeCompare(String(b.createdAt)));
  return `
  <!-- 1f: o mês aberto vira cartão de tarefa no topo, na gramática do
       .mc-exec-clearance do Execution Board — diz QUAL mês, sobre QUE saldo o
       resultado incide e por que a ordem importa, antes de qualquer campo. -->
  <section class="fxp-taskcard">
    <div class="fxp-taskcard-head">
      <span class="fxp-taskcard-lbl">${next?'Próximo mês aberto':'Horizonte fechado'}</span>
      <span class="fxp-taskcard-val">${esc(next||'—')}</span>
    </div>
    <p class="fxp-taskcard-txt">${next
      ?`Fechamentos são contíguos. Saldo de abertura <b>${fxpBoardMoney(fxpOpeningBalance(live,next))}</b> — o resultado do mês incide sobre ele e os aportes entram depois.`
      :'Todos os meses do horizonte estão finalizados. Para corrigir um mês, reabra-o na Tabela mensal com motivo.'}</p>
  </section>
  <div class="fxp-task">
  <h3 class="fxp-h3">Fechamento mensal ${fxpBadge('REAL')}</h3>
  <div class="params-grid">
    <div class="field"><label for="fxpActMonth">Mês</label>
      <select id="fxpActMonth">
        ${next?`<option value="${next}">${next} — próximo aberto</option>`:''}
        ${closed.filter(m=>m!==next).map(m=>`<option value="${m}">${m} — ${FXP_MONTH_STATES[plan.actuals[m].closureStatus||'FINALIZED']}</option>`).join('')}
      </select><span class="note">Finalizados são protegidos. Reabra pela Tabela mensal com motivo; reconfirme na ordem cronológica.</span></div>
    <div class="field"><label for="fxpActType">Entrada original</label>
      <select id="fxpActType"><option value="rate">Rentabilidade (%)</option><option value="usd">Resultado (USD)</option></select>
      <span class="note">O outro campo é derivado — mesma álgebra do MEI (resultado ÷ saldo de abertura).</span></div>
    <div class="field"><label for="fxpActValue">Valor</label><input type="text" id="fxpActValue" placeholder="ex.: -0,70 ou 1234,56"></div>
    <div class="field"><label for="fxpActFx">Câmbio de valuation (R$/USD · opcional)</label><input type="text" id="fxpActFx" placeholder="cotação do mês"><span class="note">Só para exibir o mês em BRL — não é custo de aquisição.</span></div>
    <div class="field fxp-field-wide"><label for="fxpActNotes">Observação do período</label><input type="text" id="fxpActNotes" placeholder="contexto do mês"></div>
  </div>
  <div id="fxpActErr"></div>
  <label class="fxp-month-confirm"><input type="checkbox" id="fxpActConfirmed"> Conferi os depósitos efetivos, inclusive quando forem zero.</label>
  <button class="unlock-phase-btn fxp-actions" id="fxpActBtn">${next?`Fechar ${next}`:'Editar mês selecionado'}</button>
  <!-- Prévia do derivado: calculada pelo MOTOR sobre um plano candidato, nunca
       por aritmética reescrita aqui. Nada é persistido enquanto não se fecha. -->
  <p class="fxp-derived-preview" id="fxpActPreview" aria-live="polite"></p>
  ${next?'':'<p class="fxp-note" style="color:var(--ink-dim)">Horizonte finalizado — reabertura auditada disponível na Tabela mensal.</p>'}
  </div>
  <!-- P9: o ledger é tarefa distinta do fechamento. Seção PRÓPRIA e recolhível
       (o ticket admite "seção própria ou disclosure"), aberta por padrão: o
       fechamento vem primeiro e não exige atravessar o ledger, mas o registro
       continua visível — esconder por padrão o histórico de aportes trocaria um
       problema de hierarquia por um de descoberta. A contagem fica no rótulo. -->
  <details id="fxpContributionsDisclosure" class="mc-disclosure fxp-disc" open>
  <summary><span class="t">Aportes realizados — ledger cambial (${contribs.length} lançamento${contribs.length===1?'':'s'})</span><span class="chev">▾</span></summary>
  <div class="mc-disclosure-body">
  <div class="params-grid">
    <div class="field"><label for="fxpCMonth">Mês</label><input type="month" id="fxpCMonth" value="${next||closed.slice(-1)[0]||plan.baseline.startMonth}"></div>
    <div class="field"><label for="fxpCSource">Origem</label><select id="fxpCSource"><option value="personal">Aporte pessoal</option><option value="prop">Prop Firm / origem operacional</option></select></div>
    <div class="field"><label for="fxpCCurrency">Moeda de origem</label><select id="fxpCCurrency"><option value="BRL">BRL (compra de USD)</option><option value="USD">USD nativo</option></select>
      <span class="note">BRL entra no custo médio; USD nativo (ex.: crédito de prop firm) fica fora dele.</span></div>
    <div class="field"><label for="fxpCAmount">Valor na moeda de origem</label><input type="text" id="fxpCAmount" placeholder="ex.: 10000,00"></div>
    <div class="field" id="fxpCRateField"><label for="fxpCRate">Câmbio efetivamente pago (R$/USD)</label><input type="text" id="fxpCRate" placeholder="ex.: 5,00"><span class="note">USD adquirido = BRL ÷ taxa.</span></div>
  </div>
  <div id="fxpCErr"></div>
  <button class="unlock-phase-btn fxp-actions" id="fxpCBtn">Registrar aporte</button>
  <div class="fxp-tablewrap" style="margin-top:12px"><table class="dtable" style="font-size:calc(11px * var(--fs-scale))">
    <thead><tr><th>Mês</th><th>Origem</th><th>Moeda</th><th>Valor origem</th><th>Taxa aquisição</th><th>USD</th><th>Custo médio?</th><th></th></tr></thead>
    <tbody>${contribs.length?contribs.map(c=>`<tr>
      <td class="hl">${esc(c.month)}</td><td>${c.source==='prop'?'Prop Firm':'Pessoal'}</td><td>${esc(c.originalCurrency)}</td>
      <td>${c.originalCurrency==='BRL'?'R$ '+(+c.originalAmount).toLocaleString('pt-BR',{minimumFractionDigits:2}):fxpBoardMoney(c.originalAmount||c.usdAmount)}</td>
      <td>${c.acquisitionFxRate!=null?'R$ '+(+c.acquisitionFxRate).toFixed(4).replace('.',','):'—'}</td>
      <td>${fxpBoardMoney(c.usdAmount)}</td>
      <td>${c.affectsFxCostBasis?'entra':'não entra'}</td>
      <td><button type="button" class="reset-btn fxp-del" data-fxp-del="${esc(c.id)}" aria-label="Remover aporte de ${esc(c.month)}" ${plan.actuals[c.month]&&(plan.actuals[c.month].closureStatus||'FINALIZED')!=='REOPENED'?'disabled title="Reabra este mês para alterar depósitos efetivos"':''}>remover</button></td>
    </tr>`).join(''):'<tr><td colspan="8" style="color:var(--ink-faint)">Nenhum aporte registrado — indicadores permanecem “—” até existir lançamento real.</td></tr>'}</tbody>
  </table></div>
  </div></details>`;
}
// Saldo de abertura do mês alvo, lido da série que o motor já produziu: é o
// fechamento do mês anterior, ou o saldo inicial quando nada foi fechado.
function fxpOpeningBalance(live,mes){
  const reais=(live.forecast||[]).filter(r=>r.phase==='actual');
  const alvo=(live.forecast||[]).find(r=>r.month===mes);
  if(alvo) return alvo.open;
  const ultima=reais[reais.length-1];
  return ultima?ultima.close:live.plan.baseline.initialBalanceUsd;
}
// Prévia do fechamento (1f). Monta um plano CANDIDATO em memória e pede ao
// motor a linha do mês — o derivado e o saldo final saem da mesma função que
// produz o realizado de verdade. Não reescrevemos a álgebra aqui e nada toca
// S nem save().
function fxpPreviewActual(live,mes,entrada){
  const E=window.JPWFx.engine, M=window.JPWFx.model;
  if(!E||!M||!mes) return null;
  const plan=live.plan;
  const candidato={...plan, actuals:{...(plan.actuals||{}), [mes]:M.fxNormalizeActual(entrada)}};
  let linhas; try{ linhas=E.fxActualTimeline(candidato); }catch(_){ return null; }
  const linha=(linhas||[]).find(r=>r.month===mes);
  return linha||null;
}
function fxpBindActuals(root,live){
  const q=id=>root.querySelector('#'+id);
  const monthSel=q('fxpActMonth');
  const prefill=()=>{
    const rec=live.plan.actuals[monthSel.value];
    const locked=!!rec&&(rec.closureStatus||'FINALIZED')==='FINALIZED';
    ['fxpActType','fxpActValue','fxpActFx','fxpActNotes','fxpActConfirmed','fxpActBtn'].forEach(id=>{if(q(id))q(id).disabled=locked;});
    if(q('fxpActBtn'))q('fxpActBtn').textContent=locked?'Finalizado · reabra na Tabela mensal':'Finalizar '+monthSel.value;
    q('fxpActConfirmed').checked=false;
    if(!rec){ q('fxpActValue').value=''; q('fxpActNotes').value=''; q('fxpActFx').value=''; return; }
    q('fxpActType').value=rec.inputType;
    q('fxpActValue').value=rec.inputType==='usd'?String(rec.profitUsd).replace('.',','):fxpEditablePct(rec.returnRate);
    q('fxpActFx').value=rec.valuationFxRate!=null?String(rec.valuationFxRate).replace('.',','):'';
    q('fxpActNotes').value=rec.notes||'';
  };
  // Prévia ao vivo do derivado e do saldo final estimado.
  const previa=()=>{
    const el=q('fxpActPreview'); if(!el) return;
    const tipo=q('fxpActType').value;
    const bruto=tipo==='usd'?fxpParseNum(q('fxpActValue').value):fxpParsePct(q('fxpActValue').value,live.plan.actuals[monthSel.value]?.returnRate);
    if(bruto==null){ el.textContent=''; return; }
    const linha=fxpPreviewActual(live,monthSel.value,{
      inputType:tipo, returnRate:tipo==='rate'?bruto:null, profitUsd:tipo==='usd'?bruto:null,
      valuationFxRate:fxpParseNum(q('fxpActFx').value), notes:''});
    if(!linha){ el.textContent=''; return; }
    const derivado=tipo==='usd'
      ? `taxa derivada ${fxpPct(linha.rate)}`
      : `resultado derivado ${fxpBoardMoney(linha.profit)}`;
    el.textContent=`${derivado} · saldo final estimado ${fxpBoardMoney(linha.close)}`;
  };
  ['fxpActType','fxpActValue','fxpActFx'].forEach(id=>{
    const e=q(id); if(e){ e.addEventListener('input',previa); e.addEventListener('change',previa); }
  });
  monthSel.addEventListener('change',()=>{ prefill(); previa(); }); prefill(); previa();
  q('fxpActBtn').addEventListener('click',()=>{
    const type=q('fxpActType').value;
    const val=type==='usd'?fxpParseNum(q('fxpActValue').value):fxpParsePct(q('fxpActValue').value,live.plan.actuals[monthSel.value]?.returnRate);
    if(val==null){ q('fxpActErr').innerHTML=fxpErrHTML(['Informe o valor do mês (percentual ou USD conforme a entrada).']); return; }
    const res=window.JPWFx.state.fxPlanRecordActual(monthSel.value,{
      inputType:type, returnRate:type==='rate'?val:null, profitUsd:type==='usd'?val:null,
      valuationFxRate:fxpParseNum(q('fxpActFx').value), notes:q('fxpActNotes').value,contributionsConfirmed:q('fxpActConfirmed').checked});
    if(!res.ok){ fxpRememberDraft(root,'actual','fxpActErr',res); return; }
    fxpForgetDraft('actual');
    renderFxPlanning();
  });
  const curSel=q('fxpCCurrency');
  const syncContributionLock=()=>{const rec=live.plan.actuals[q('fxpCMonth').value],locked=!!rec&&(rec.closureStatus||'FINALIZED')!=='REOPENED';q('fxpCBtn').disabled=locked;q('fxpCBtn').textContent=locked?'Depósitos protegidos · reabra o mês':'Registrar aporte';};
  q('fxpCMonth').addEventListener('input',syncContributionLock);syncContributionLock();
  const syncRate=()=>{ q('fxpCRateField').style.display=curSel.value==='BRL'?'':'none'; };
  curSel.addEventListener('change',syncRate); syncRate();
  q('fxpCBtn').addEventListener('click',()=>{
    const res=window.JPWFx.state.fxPlanAddContribution({
      month:fxMonthKey(q('fxpCMonth').value), source:q('fxpCSource').value,
      originalCurrency:curSel.value, originalAmount:fxpParseNum(q('fxpCAmount').value)||0,
      acquisitionFxRate:curSel.value==='BRL'?fxpParseNum(q('fxpCRate').value):null});
    if(!res.ok){ fxpRememberDraft(root,'contribution','fxpCErr',res); return; }
    fxpForgetDraft('contribution');
    renderFxPlanning();
  });
  root.querySelectorAll('[data-fxp-del]').forEach(b=>b.addEventListener('click',()=>{
    const res=window.JPWFx.state.fxPlanRemoveContribution(b.dataset.fxpDel);
    if(!res.ok){ fxpRememberDraft(root,'removal','fxpCErr',res); return; }
    fxpForgetDraft('removal');
    renderFxPlanning();
  }));
}

// ---- Tabela mensal + resumo anual ------------------------------------------
function fxpAuditTableHTML(live){
  const ov=live;
  const baseByMonth={}; ov.baseline.forEach(r=>{baseByMonth[r.month]=r;});
  // Filtro do 1g: recorte de LEITURA sobre as linhas já calculadas. Nenhuma
  // série é recalculada e nada é escondido do resumo anual, que continua sobre
  // o horizonte inteiro — filtrar a auditoria mudaria o que ela audita.
  const activeSeries=fxpScenarioId?(live.plan.scenarios||[]).find(s=>s.id===fxpScenarioId):null;
  const shownSeries=activeSeries?window.JPWFx.engine.fxScenarioTimeline(live.plan,activeSeries):ov.forecast;
  const visiveis=shownSeries.filter(r=>
    fxpHistFilter==='actual'?r.phase==='actual'
    :fxpHistFilter==='forecast'?r.phase!=='actual':true);
  const rows=visiveis.map(r=>{
    const b=baseByMonth[r.month];
    const dev=b&&Number.isFinite(r.close)&&Number.isFinite(b.close)?r.close-b.close:null;
    const real=r.phase==='actual';
    return `<tr>
      <td class="hl">${r.month}</td>
      <td>${real?fxpBadge('ACTUAL'):fxpBadge(activeSeries?'SCENARIO':'PLAN')}${real&&r.derivedField?`<span class="fxp-derived" title="entrada original: ${r.inputType==='usd'?'resultado USD':'taxa %'}">${r.inputType==='usd'?'$→%':'%→$'}</span>`:''}</td>
      <td class="fxg-b">${b?fxpBoardMoney(b.open):'—'}</td><td class="fxg-b">${b?fxpPct(b.rate):'—'}</td><td class="fxg-b">${b?fxpBoardMoney(b.profit):'—'}</td><td class="fxg-b">${b?fxpBoardMoney(b.contributionUsd):'—'}</td><td class="fxg-b">${b?fxpBoardMoney(b.close):'—'}</td>
      <td class="fxg-v">${fxpBoardMoney(r.open)}</td><td class="fxg-v">${fxpPct(r.rate)}</td><td class="fxg-v">${fxpBoardMoney(r.profit)}</td><td class="fxg-v">${fxpBoardMoney(r.personalUsd)}</td><td class="fxg-v">${fxpBoardMoney(r.propUsd)}</td><td class="fxg-v">${fxpBoardMoney(r.close)}</td>
      <td class="fxg-d" style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${dev!=null?fxpBoardMoney(dev):'—'}</td>
      <td class="fxg-d" style="color:${dev==null?'var(--ink-dim)':(dev>=0?'var(--f1)':'var(--f4)')}">${(dev!=null&&b&&b.close!==0)?fxpPct(dev/b.close):'—'}</td>
    </tr>`;
  }).join('');
  const annual=fxAnnualSummary(shownSeries);
  const annualFx=fxAnnualFxSummary(live.plan.contributions);
  const fxByYear={}; annualFx.forEach(a=>{fxByYear[a.year]=a;});
  const filtros=[['all','Todos'],['actual','Só realizados'],['forecast','Só projetados']];
  return `
  <div class="fxp-modes fxp-histfilter" role="group" aria-label="Filtro da tabela mensal">${filtros.map(([k,l])=>
    `<button type="button" class="reset-btn fxp-mode${fxpHistFilter===k?' fxp-mode-on':''}" data-fxp-hist="${k}" aria-pressed="${fxpHistFilter===k}">${l}</button>`).join('')}
    <span class="fxp-histcount">${visiveis.length} de ${shownSeries.length} meses</span></div>
  <p class="fxp-note" style="font-size:var(--fs-sm);color:var(--ink-dim)">BASELINE = premissas originais congeladas ${fxpBadge('PROJ')} · ${activeSeries?'SCENARIO = ACTUAL até o último fechamento e hipótese independente dali em diante.':'VIGENTE = ACTUAL até o último fechamento e PLAN dali em diante.'} Meses realizados exibem a direção da derivação ($→% ou %→$).</p>
  <div class="fxp-tablewrap"><table class="dtable fxp-hist" style="font-size:calc(10.5px * var(--fs-scale))">
    <thead>
      <tr><th rowspan="2">Mês</th><th rowspan="2">Fase</th><th colspan="5" class="fxg-b">BASELINE · plano original</th><th colspan="6" class="fxg-v">${activeSeries?'SCENARIO · realizado + hipótese':'VIGENTE · realizado + PLAN'}</th><th colspan="2" class="fxg-d">Desvio</th></tr>
      <tr><th class="fxg-b">Inicial</th><th class="fxg-b">%</th><th class="fxg-b">Resultado</th><th class="fxg-b">Aportes</th><th class="fxg-b">Final</th><th class="fxg-v">Inicial</th><th class="fxg-v">%</th><th class="fxg-v">Resultado</th><th class="fxg-v">Ap. pessoal</th><th class="fxg-v">Ap. prop</th><th class="fxg-v">Final</th><th class="fxg-d">USD</th><th class="fxg-d">%</th></tr>
    </thead>
    <tbody>${rows}</tbody>
  </table></div>
  <h3 style="margin:16px 0 6px;font-size:calc(13px * var(--fs-scale))">Resumo anual (derivado automaticamente)</h3>
  <div class="fxp-tablewrap"><table class="dtable" style="font-size:calc(11px * var(--fs-scale))">
    <thead><tr><th>Ano</th><th>Meses</th><th>Saldo inicial</th><th>Resultado</th><th>Rent. composta</th><th>Ap. pessoal</th><th>Ap. prop</th><th>Saldo final</th><th>BRL convertido</th><th>USD adquirido</th><th>Câmbio médio/ano</th></tr></thead>
    <tbody>${annual.map(a=>{
      const f=fxByYear[a.year];
      const months=[a.phases.actual?`${a.phases.actual} ACTUAL`:'',a.phases.forecast?`${a.phases.forecast} PLAN`:'',a.phases.scenario?`${a.phases.scenario} SCENARIO`:''].filter(Boolean).join(' + ');
      return `<tr><td class="hl">${a.year}</td><td>${months}${a.available===false?`<br><span class="fxp-note">${esc(a.reason)}</span>`:''} </td>
        <td>${fxpBoardMoney(a.open)}</td><td>${fxpBoardMoney(a.profitUsd)}</td><td>${fxpPct(a.composedReturn)}</td>
        <td>${fxpBoardMoney(a.personalUsd)}</td><td>${fxpBoardMoney(a.propUsd)}</td><td>${fxpBoardMoney(a.close)}</td>
        <td>${f?'R$ '+Math.round(f.brlInvested).toLocaleString('pt-BR'):'—'}</td><td>${f?fxpBoardMoney(f.usdAcquired):'—'}</td>
        <td>${f&&f.weightedAverageFx!=null?'R$ '+f.weightedAverageFx.toFixed(4).replace('.',','):'—'}</td></tr>`;
    }).join('')}</tbody>
  </table></div>
  <details style="margin-top:12px"><summary style="cursor:pointer;font-size:var(--fs-sm);color:var(--ink-dim)">Trilha de auditoria do Planejamento FX (últimos eventos)</summary>
    <div style="font-family:var(--mono);font-size:calc(10.5px * var(--fs-scale));color:var(--ink-dim);line-height:1.8;margin-top:6px">
      ${(S.fxPlanning.auditLog||[]).slice(-10).reverse().map(e=>`${esc(String(e.ts||'').slice(0,16).replace('T',' '))} · ${esc(e.type)}${e.month?' · '+esc(e.month):''} · ${esc(e.detail||'')}`).join('<br>')||'—'}
    </div>
  </details>`;
}


// ---- Monthly board: drafts are transient; all amounts come from the engine. ----
const fxpMonthlyDrafts=new Map();
const fxpMonthlyErrors=new Map();
const fxpMonthlyAuxDrafts=new Map();
const FXP_MONTH_STATES={PROJECTED:'Projetado',ABSENT:'Sem previsão',FINALIZED:'Finalizado',REOPENED:'Reaberto',REVIEW_REQUIRED:'Base em revisão',BLOCKED:'Indisponível'};
const fxpBoardMoney=v=>Number.isFinite(v)?fmtMoney2(v):'—';
const fxpMonthLabel=month=>{const [year,m]=String(month).split('-');return ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'][Number(m)-1]+' '+year;};
function fxpMonthlyKey(live,month){return JSON.stringify([jpWealthPersistenceEpoch(),live.plan.id,fxpScenarioId,month]);}
function fxpMonthlyDraft(live,month){return fxpMonthlyDrafts.get(fxpMonthlyKey(live,month));}
function fxpMonthAux(live,month,field){return fxpMonthlyAuxDrafts.get(fxpMonthlyKey(live,month))?.[field]||'';}
function fxpMonthlyRows(live,plan=live.plan){
  const scenario=(plan.scenarios||[]).find(s=>s.id===fxpScenarioId);
  return scenario?window.JPWFx.engine.fxScenarioTimeline(plan,scenario):window.JPWFx.engine.fxForecastTimeline(plan);
}
function fxpMonthlyPlanDraft(live,month){
  const row=fxpMonthlyRows(live).find(r=>r.month===month), scenario=(live.plan.scenarios||[]).find(s=>s.id===fxpScenarioId);
  const assumptions=scenario?.assumptions||live.plan.current;
  const planned=window.JPWFx.model.fxPlannedContribution(assumptions,month);
  return {mode:'plan',sourceVersion:live.plan.updatedAt,originalRate:row?.rate,fields:{rate:Number.isFinite(row?.rate)?String(row.rate*100):'',personalUsd:Number.isFinite(row?.personalUsd)?String(row.personalUsd):Number.isFinite(planned?.personalUsd)?String(planned.personalUsd):'',propUsd:Number.isFinite(row?.propUsd)?String(row.propUsd):Number.isFinite(planned?.propUsd)?String(planned.propUsd):'',note:''},dirty:false};
}
function fxpMonthlyActualDraft(live,month){
  const rec=live.plan.actuals[month];
  return {mode:'actual',sourceVersion:live.plan.updatedAt,originalRate:rec?.inputType==='rate'?rec.returnRate:undefined,fields:{inputType:rec?.inputType||'rate',rate:rec&&rec.inputType!=='usd'?String(rec.returnRate*100):'',profitUsd:rec&&rec.inputType==='usd'?String(rec.profitUsd):'',valuationFxRate:rec?.valuationFxRate!=null?String(rec.valuationFxRate):'',note:rec?.notes||'',contributionsConfirmed:false},dirty:false};
}
function fxpMonthlyCandidate(live){
  const plan=structuredClone(live.plan),scenario=(plan.scenarios||[]).find(s=>s.id===fxpScenarioId),a=scenario?.assumptions||plan.current;
  for(const [key,draft] of fxpMonthlyDrafts){
    const [epoch,id,scenarioId,month]=JSON.parse(key);
    if(epoch!==jpWealthPersistenceEpoch()||id!==plan.id||scenarioId!==fxpScenarioId||draft.sourceVersion!==live.plan.updatedAt)continue;
    const f=draft.fields;
    if(draft.mode==='plan'){
      const rate=fxpParsePct(f.rate,draft.originalRate),personal=fxpParseNum(f.personalUsd),prop=fxpParseNum(f.propUsd);
      a.monthOverrides={...(a.monthOverrides||{}),[month]:rate};
      a.plannedContributions={...(a.plannedContributions||{}),[month]:{personalUsd:personal,propUsd:prop}};
      a.absentMonths={...(a.absentMonths||{})};delete a.absentMonths[month];
    }else if(!scenario){
      const val=f.inputType==='usd'?fxpParseNum(f.profitUsd):fxpParsePct(f.rate,draft.originalRate);
      plan.actuals[month]={...(plan.actuals[month]||{}),inputType:f.inputType,returnRate:f.inputType==='rate'?val:null,profitUsd:f.inputType==='usd'?val:null,valuationFxRate:fxpParseNum(f.valuationFxRate),notes:f.note,closureStatus:'FINALIZED',contributionsConfirmed:true};
    }
  }
  return plan;
}
function fxpMonthlyInput(live,row,field,value,label,extra=''){
  const id='fxpMonth-'+row.month+'-'+field;
  return `<input id="${id}" class="fxp-month-input" type="text" inputmode="decimal" data-fxp-month="${row.month}" data-fxp-field="${field}" value="${esc(value??'')}" aria-label="${esc(label+' · '+fxpMonthLabel(row.month))}" ${extra}>`;
}
function fxpMonthlyDetailHTML(live,row,draft){
  const month=row.month,base=live.baseline.find(r=>r.month===month),rec=live.plan.actuals[month],real=row.phase==='actual'||draft?.mode==='actual';
  const ledger=(live.plan.contributions||[]).filter(c=>c.month===month);
  const prior=(live.plan.actualHistory||[]).filter(r=>r.month===month);
  const snapshot=row.confirmedSnapshot||rec?.confirmedSnapshot;
  return `<tr class="fxp-month-detail-row" data-fxp-detail-row="${month}"><td colspan="9"><details id="fxpMonthDetail-${month}" class="fxp-month-detail">
    <summary>Detalhes · ${fxpMonthLabel(month)}</summary><div class="fxp-month-detail-body">
      <p class="fxp-note">${esc(row.reason||'Depósitos entram depois do resultado. Nenhum valor previsto é promovido automaticamente para realizado.')}</p>
      <dl class="fxp-month-comparison"><dt>Baseline · saldo final USD</dt><dd>${fxpBoardMoney(base?.close)}</dd><dt>Vigente · saldo final USD</dt><dd data-fxp-detail-close="${month}">${fxpBoardMoney(row.close)}</dd><dt>Origem</dt><dd>${esc(rec?.source?JSON.stringify(rec.source):real?'Entrada manual original · '+(rec?.inputType==='usd'?'resultado USD':'rentabilidade %'):'Premissas declaradas · '+(fxpScenarioId?'SCENARIO':'PLAN'))}</dd><dt>Câmbio para apresentação BRL</dt><dd>${rec?.valuationFxRate!=null?'R$ '+esc(rec.valuationFxRate):live.plan.current.projectedFxRate!=null?'Premissa: R$ '+esc(live.plan.current.projectedFxRate):'Não informado'}</dd></dl>
      ${draft||!real?`<label>Motivo / observação<input type="text" id="fxpMonth-${month}-note" data-fxp-month="${month}" data-fxp-field="note" value="${esc(draft?.fields.note||'')}" aria-label="Motivo · ${fxpMonthLabel(month)}"></label>`:''}
      ${draft?.mode==='actual'?`<label>Entrada original<select id="fxpMonth-${month}-inputType" data-fxp-month="${month}" data-fxp-field="inputType"><option value="rate" ${draft.fields.inputType==='rate'?'selected':''}>Rentabilidade percentual</option><option value="usd" ${draft.fields.inputType==='usd'?'selected':''}>Resultado nominal USD</option></select></label><label>Câmbio de valuation opcional<input type="text" inputmode="decimal" id="fxpMonth-${month}-valuationFxRate" data-fxp-month="${month}" data-fxp-field="valuationFxRate" value="${esc(draft.fields.valuationFxRate)}"></label><label class="fxp-month-confirm"><input type="checkbox" id="fxpMonth-${month}-contributionsConfirmed" data-fxp-month="${month}" data-fxp-field="contributionsConfirmed" ${draft.fields.contributionsConfirmed?'checked':''}> Conferi os depósitos efetivos deste mês, inclusive se forem zero.</label><p class="fxp-note">Finalizar usa somente a entrada original escolhida. Os valores da linha são prévia não salva.</p>`:''}
      ${real?`<section class="fxp-month-ledger"><h4>Depósitos efetivos · ${ledger.length} lançamento(s)</h4>${ledger.length?`<ul>${ledger.map(c=>`<li>${c.source==='prop'?'Prop':'Pessoal'} · ${esc(c.originalCurrency)} ${esc(c.originalAmount)} → ${fxpBoardMoney(c.usdAmount)} USD · ${esc(c.createdAt||'horário não informado')}</li>`).join('')}</ul>`:'<p>Nenhum lançamento registrado. Zero requer conferência explícita ao finalizar.</p>'}<button type="button" data-fxp-month-action="ledger" data-fxp-month="${month}">Consultar / registrar depósitos</button></section>`:''}
      ${row.status==='FINALIZED'||row.status==='REVIEW_REQUIRED'?`<label>Motivo da reabertura<input type="text" id="fxpReopenNote-${month}" data-fxp-month="${month}" data-fxp-aux="reopenNote" value="${esc(fxpMonthAux(live,month,'reopenNote'))}" aria-label="Motivo para reabrir ${fxpMonthLabel(month)}"></label><button type="button" data-fxp-month-action="reopen" data-fxp-month="${month}">Reabrir mês</button>`:''}
      ${snapshot?`<details><summary>Última versão confirmada preservada</summary><pre>${esc(JSON.stringify(snapshot,null,2))}</pre></details>`:''}
      ${prior.length?`<details><summary>Revisões anteriores (${prior.length})</summary><pre>${esc(JSON.stringify(prior,null,2))}</pre></details>`:''}
      ${!real?`<div class="fxp-month-detail-actions"><button type="button" data-fxp-month-action="clear" data-fxp-month="${month}">Retirar previsão deste mês</button><button type="button" data-fxp-month-action="restore" data-fxp-month="${month}">Voltar às premissas gerais</button>${!fxpScenarioId?`<button type="button" data-fxp-month-action="actual" data-fxp-month="${month}">Registrar realizado</button>`:''}</div>`:''}
      ${!real?`<details><summary>Rebase avançado e explícito</summary><label>Novo saldo inicial USD<input type="text" inputmode="decimal" id="fxpRebase-${month}" data-fxp-month="${month}" data-fxp-aux="rebaseOpening" value="${esc(fxpMonthAux(live,month,'rebaseOpening'))}"></label><label>Motivo<input id="fxpRebaseNote-${month}" data-fxp-month="${month}" data-fxp-aux="rebaseNote" value="${esc(fxpMonthAux(live,month,'rebaseNote'))}"></label><button type="button" data-fxp-month-action="rebase" data-fxp-month="${month}">Confirmar rebase</button></details>`:''}
    </div></details></td></tr>`;
}
function fxpTableHTML(live){
  const source=fxpMonthlyRows(live),preview=fxpMonthlyRows(live,fxpMonthlyCandidate(live)),byMonth=new Map(preview.map(r=>[r.month,r]));
  let year='',html='';
  for(const original of source){
    if(fxpHistFilter==='actual'&&original.phase!=='actual'||fxpHistFilter==='forecast'&&original.phase==='actual')continue;
    const r=byMonth.get(original.month)||original,draft=fxpMonthlyDraft(live,r.month),actual=original.phase==='actual',editingActual=draft?.mode==='actual';
    const status=original.status||(actual?'FINALIZED':'PROJECTED'),fields=draft?.fields||fxpMonthlyPlanDraft(live,r.month).fields;
    if(year!==r.month.slice(0,4)){year=r.month.slice(0,4);html+=`<tr class="fxp-month-year"><th colspan="9" scope="rowgroup">${year}</th></tr>`;}
    const planInput=(field,label)=>fxpMonthlyInput(live,r,field,fields[field],label);
    const deposit=(field,label)=>actual||editingActual?`<button type="button" class="fxp-month-ledger-link" data-fxp-month-action="ledger" data-fxp-month="${r.month}" aria-label="Consultar depósitos ${label} de ${fxpMonthLabel(r.month)}">${fxpBoardMoney(r[field])}</button>`:planInput(field,'Depósito '+label+' USD');
    const rateCell=editingActual&&fields.inputType==='rate'?fxpMonthlyInput(live,r,'rate',fields.rate,'Rentabilidade realizada %'):actual||editingActual?`<span data-fxp-value="rate">${fxpPct(r.rate)}</span>`:planInput('rate','Rentabilidade planejada %');
    const profitCell=editingActual&&fields.inputType==='usd'?fxpMonthlyInput(live,r,'profitUsd',fields.profitUsd,'Resultado realizado USD'):`<span data-fxp-value="profit">${fxpBoardMoney(r.profit)}</span>`;
    const errors=fxpMonthlyErrors.get(fxpMonthlyKey(live,r.month));
    html+=`<tr class="fxp-month-row ${status==='FINALIZED'?'fxp-month-finalized':''}" data-fxp-month-row="${r.month}" data-fxp-month-state="${status}">
      <th scope="row" data-label="Mês">${fxpMonthLabel(r.month)}</th>
      <td data-label="Estado"><span class="fxp-month-status" data-fxp-status>${esc(FXP_MONTH_STATES[status]||status)}</span><span class="fxp-month-dirty" data-fxp-dirty>${draft?.dirty||editingActual?'Não salvo':''}</span><span class="fxp-month-reason" data-fxp-reason>${esc(original.reason||'')}</span></td>
      <td data-label="Saldo inicial USD"><span data-fxp-value="open">${fxpBoardMoney(r.open)}</span></td>
      <td data-label="Depósito pessoal USD">${deposit('personalUsd','pessoais')}</td><td data-label="Depósito Prop USD">${deposit('propUsd','Prop')}</td>
      <td data-label="Rentabilidade %">${rateCell}</td><td data-label="Resultado USD">${profitCell}</td><td data-label="Saldo final USD"><span data-fxp-value="close">${fxpBoardMoney(r.close)}</span></td>
      <td data-label="Ações"><div class="fxp-month-actions">
      ${!actual&&!editingActual?`<button type="button" data-fxp-month-action="save" data-fxp-month="${r.month}" ${draft?.dirty?'':'disabled'}>Salvar mês</button><button type="button" data-fxp-month-action="cancel" data-fxp-month="${r.month}" ${draft?.dirty?'':'disabled'}>Cancelar edição</button>`:editingActual?`<button type="button" data-fxp-month-action="finalize" data-fxp-month="${r.month}">Finalizar mês</button><button type="button" data-fxp-month-action="cancel" data-fxp-month="${r.month}">Cancelar edição</button>`:status==='REOPENED'||status==='REVIEW_REQUIRED'?`<button type="button" data-fxp-month-action="actual" data-fxp-month="${r.month}">Reconferir realizado</button>`:''}
      <button type="button" data-fxp-month-action="details" data-fxp-month="${r.month}">Ver detalhes</button></div><div class="fxp-month-error" role="status" data-fxp-error>${errors?fxpErrHTML(errors):''}</div></td></tr>${fxpMonthlyDetailHTML(live,original,draft)}`;
  }
  return `<section class="fxp-month-board" aria-labelledby="fxpMonthlyTableTitle"><div class="fxp-block-head"><h3 id="fxpMonthlyTableTitle">Tabela mensal</h3><span class="fxp-note">Global · USD · ${fxpScenarioId?'SCENARIO':'PLAN + realizado'}</span></div>${fxpUnknownNoticeHTML()}<p class="fxp-note">Edite depósitos e rentabilidade na linha. Digitar cria uma prévia; somente Salvar mês ou Finalizar mês grava. Finalizados ficam protegidos.</p>
    <div class="fxp-modes fxp-histfilter" role="group" aria-label="Filtro da tabela mensal">${[['all','Todos'],['actual','Realizados'],['forecast','Projetados']].map(([k,label])=>`<button type="button" data-fxp-hist="${k}" class="reset-btn" aria-pressed="${fxpHistFilter===k}">${label}</button>`).join('')}</div>
    <div class="fxp-month-scroll" tabindex="0" aria-label="Grade mensal, rolagem própria"><table class="fxp-month-table"><caption>Previsões e realizados, com bases separadas e edição mensal explícita</caption><thead><tr><th scope="col">Mês</th><th scope="col">Estado</th><th scope="col">Saldo inicial<br>USD</th><th scope="col">Depósito pessoal<br>USD</th><th scope="col">Depósito Prop<br>USD</th><th scope="col">Rentabilidade<br>%</th><th scope="col">Resultado<br>USD</th><th scope="col">Saldo final<br>USD</th><th scope="col">Ações</th></tr></thead><tbody>${html}</tbody></table></div></section>
    <section class="fxp-block fxp-month-charts"><div class="fxp-block-head"><span class="fxp-note">Versões salvas · lacunas permanecem indisponíveis.</span></div>${fxpUnknownNoticeHTML()}${fxpChartControlsHTML(live)}<div id="fxpMainChart"></div><p id="fxpMainChartSummary" class="fxp-note"></p></section>
    <details class="fxp-month-audit"><summary>Resumo anual, baseline e auditoria completa</summary>${fxpAuditTableHTML(live)}</details>`;
}
function fxpMonthlyRefresh(root,live){
  const rows=fxpMonthlyRows(live,fxpMonthlyCandidate(live));
  for(const row of rows){
    const tr=root.querySelector('[data-fxp-month-row="'+row.month+'"]');if(!tr)continue;
    const draft=fxpMonthlyDraft(live,row.month);
    for(const field of ['open','rate','profit','close']){
      const out=tr.querySelector('[data-fxp-value="'+field+'"]');if(out)out.textContent=field==='rate'?fxpPct(row[field]):fxpBoardMoney(row[field]);
    }
    const dirty=tr.querySelector('[data-fxp-dirty]');if(dirty)dirty.textContent=draft?.dirty||draft?.mode==='actual'?'Não salvo':'';
    const reason=tr.querySelector('[data-fxp-reason]');if(reason)reason.textContent=row.reason||'';
    tr.querySelectorAll('[data-fxp-month-action="save"],[data-fxp-month-action="cancel"]').forEach(b=>b.disabled=!draft?.dirty&&draft?.mode!=='actual');
    const detail=root.querySelector('[data-fxp-detail-close="'+row.month+'"]');if(detail)detail.textContent=fxpBoardMoney(row.close);
  }
  fxpQualifyUnknownReading(root);
}
function fxpBindMonthlyBoard(root,live){
  if(root.__fxpMonthlyBound)return;
  root.__fxpMonthlyBound=true;
  const liveNow=()=>fxpDisplayLive(root);
  root.addEventListener('focusin',event=>{const input=event.target;if(input.matches('[data-fxp-field]'))input.__fxpCellBefore=input.type==='checkbox'?input.checked:input.value;});
  const update=event=>{
    const input=event.target;if(!input.matches('[data-fxp-field],[data-fxp-aux]')||fxpRendering)return;
    const live=liveNow();if(!live||!root.__fxpDraftScope||root.__fxpDraftScope.planId!==live.plan.id||root.__fxpDraftScope.epoch!==jpWealthPersistenceEpoch())return;
    const month=input.dataset.fxpMonth,key=fxpMonthlyKey(live,month);
    if(input.hasAttribute('data-fxp-aux')){fxpMonthlyAuxDrafts.set(key,{...(fxpMonthlyAuxDrafts.get(key)||{}),[input.dataset.fxpAux]:input.value});return;}
    let draft=fxpMonthlyDrafts.get(key);
    if(!draft){draft=fxpMonthlyPlanDraft(live,month);draft.originalFields=structuredClone(draft.fields);fxpMonthlyDrafts.set(key,draft);}
    draft.fields[input.dataset.fxpField]=input.type==='checkbox'?input.checked:input.value;
    draft.dirty=!draft.originalFields||JSON.stringify(draft.fields)!==JSON.stringify(draft.originalFields);
    if(draft.mode==='plan'&&!draft.dirty)fxpMonthlyDrafts.delete(key);
    fxpMonthlyErrors.delete(key);
    if(input.dataset.fxpField==='inputType'){renderFxPlanning();document.getElementById('fxpMonthDetail-'+month).open=true;return;}
    fxpMonthlyRefresh(root,live);
  };
  root.addEventListener('input',update);root.addEventListener('change',update);
  root.addEventListener('keydown',event=>{
    const input=event.target;if(!input.matches('[data-fxp-field]')||input.tagName==='SELECT')return;
    if(event.key==='Enter'){event.preventDefault();input.__fxpCellBefore=input.type==='checkbox'?input.checked:input.value;}
    if(event.key==='Escape'){
      event.preventDefault();event.stopPropagation();
      if(input.type==='checkbox')input.checked=!!input.__fxpCellBefore;else input.value=input.__fxpCellBefore??'';
      update({target:input});
    }
  });
  root.addEventListener('click',event=>{
    const button=event.target.closest('[data-fxp-month-action]');if(!button||!root.contains(button))return;
    const live=liveNow();if(!live||root.__fxpDraftScope.planId!==live.plan.id||root.__fxpDraftScope.epoch!==jpWealthPersistenceEpoch())return;
    const month=button.dataset.fxpMonth,action=button.dataset.fxpMonthAction,key=fxpMonthlyKey(live,month),state=window.JPWFx.state,draft=fxpMonthlyDraft(live,month);
    const fail=res=>{const errors=res.errors||['Ação não confirmada.'];fxpMonthlyErrors.set(key,errors);const out=root.querySelector('[data-fxp-month-row="'+month+'"] [data-fxp-error]');if(out)out.innerHTML=fxpErrHTML(errors);if(jpWealthPersistenceOutcomeIsUnknown())renderFxPlanning();};
    const done=res=>{if(!res.ok){fail(res);return;}fxpMonthlyDrafts.delete(key);fxpMonthlyErrors.delete(key);fxpMonthlyAuxDrafts.delete(key);const updated=liveNow();if(updated)for(const [otherKey,other] of fxpMonthlyDrafts){const [epoch,id]=JSON.parse(otherKey);if(epoch===jpWealthPersistenceEpoch()&&id===updated.plan.id)other.sourceVersion=updated.plan.updatedAt;}renderFxPlanning();};
    if(draft&&draft.sourceVersion!==live.plan.updatedAt&&!['cancel','details','ledger'].includes(action)){fail({errors:['A versão do plano mudou durante a edição. O rascunho foi preservado; cancele e confira a leitura atual antes de gravar.']});return;}
    if(action==='details'){const detail=root.querySelector('#fxpMonthDetail-'+month);detail.open=!detail.open;return;}
    if(action==='cancel'){fxpMonthlyDrafts.delete(key);fxpMonthlyErrors.delete(key);renderFxPlanning();return;}
    if(action==='actual'){
      if(draft?.dirty&&!confirm('Trocar para realizado preserva a projeção salva e descarta somente este rascunho. Continuar?'))return;
      fxpMonthlyDrafts.set(key,fxpMonthlyActualDraft(live,month));renderFxPlanning();
      const detail=root.querySelector('#fxpMonthDetail-'+month);if(detail)detail.open=true;
      root.querySelector('#fxpMonth-'+month+'-'+(fxpMonthlyDraft(live,month).fields.inputType==='usd'?'profitUsd':'rate'))?.focus();return;
    }
    if(action==='ledger'){fxpSelectedMonth=month;fxpView='actuals';renderFxPlanning();const el=root.querySelector('#fxpCMonth');if(el){el.value=month;el.dispatchEvent(new Event('input',{bubbles:true}));}root.querySelector('#fxpContributionsDisclosure')?.scrollIntoView({block:'start'});return;}
    if(action==='clear'||action==='restore'){
      if(draft?.dirty&&!confirm('Esta ação descarta o rascunho deste mês. Continuar?'))return;
      const res=action==='clear'?state.fxPlanClearMonth(month,'Previsão retirada pelo usuário',fxpScenarioId):state.fxPlanRestoreMonth(month,'Retorno explícito às premissas gerais',fxpScenarioId);done(res);return;
    }
    if(action==='save'){
      if(!draft)return;
      done(state.fxPlanReviseFromMonth(month,{rate:fxpParsePct(draft.fields.rate,draft.originalRate),personalUsd:fxpParseNum(draft.fields.personalUsd),propUsd:fxpParseNum(draft.fields.propUsd)},draft.fields.note.trim()||'Edição mensal de '+month,fxpScenarioId));return;
    }
    if(action==='reopen'){const note=root.querySelector('#fxpReopenNote-'+month).value;done(state.fxPlanReopenMonth(month,note));return;}
    if(action==='rebase'){done(state.fxPlanRebase(month,fxpParseNum(root.querySelector('#fxpRebase-'+month).value),root.querySelector('#fxpRebaseNote-'+month).value,fxpScenarioId));return;}
    if(action==='finalize'){
      if(!draft||draft.mode!=='actual')return;
      const f=draft.fields,val=f.inputType==='usd'?fxpParseNum(f.profitUsd):fxpParsePct(f.rate,draft.originalRate);
      done(state.fxPlanFinalizeMonth(month,{inputType:f.inputType,returnRate:f.inputType==='rate'?val:null,profitUsd:f.inputType==='usd'?val:null,valuationFxRate:fxpParseNum(f.valuationFxRate),notes:f.note,contributionsConfirmed:!!f.contributionsConfirmed,source:live.plan.actuals[month]?.source}));return;
    }
  });
}

function fxpActivateOverview(root,live){
  // Cadência: entrada na tela + volta à visibilidade + TTL + botão manual.
  // Sem polling — refresh(false) respeita o TTL e o cooldown de falha.
  fxpWireQuoteOnce();
  fxpBindQuote(root);
  const m=fxpQuote(); if(m) m.refresh(false);
  fxpBindChartControls(root,live);
  // Atalhos da lateral: levam para onde o dado é editado, sem duplicar formulário.
  const ob=root.querySelector('#fxpGoOnboarding');
  if(ob) ob.addEventListener('click',()=>{
    // Guarda por typeof: no monólito reduzido o módulo de Configurações pode
    // não estar presente, e o botão não pode quebrar a tela.
    if(window.JPWNavigation)window.JPWNavigation.navigate('forex-reserves');
  });
  const led=root.querySelector('#fxpGoLedger');
  if(led) led.addEventListener('click',()=>{ fxpView='actuals'; renderFxPlanning(); });
  // Estado máximo (≥1120) abre o segundo gráfico; abaixo disso ele nasce
  // recolhido. Medido no container real, não na janela — é o painel que sabe
  // quanto espaço tem. O usuário pode abrir a qualquer largura.
  const caixa=root.querySelector('#fxpReturnsBox');
  if(caixa) caixa.open=root.clientWidth>=1120;
  window.JPWFx.charts.fxDrawReturnsChart(root.querySelector('#fxpReturnsChart'),live);
}

// ---- Versioned monthly editing, scenarios and explicit ledger import -------
function fxpReferenceHTML(){
  const refs=window.JPWFx.state.fxPlanningReferences();
  if(!refs)return '<p class="fxp-note">Referências de planejamento indisponíveis.</p>';
  const annual=Array.isArray(refs.annualRange)?refs.annualRange.map(fxpPct).join(' – '):'pendente';
  return `<p class="fxp-note fxp-policy-reference">Referências distintas: ${fxpPct(refs.monthly)} ao mês · ${annual} ao ano. São referências de planejamento, não promessa. As premissas abaixo são explícitas; a referência anual não é calculada da mensal.</p>`;
}
function fxpTimelineEditorHTML(live){
  const plan=live.plan,scenarios=plan.scenarios||[],scenario=scenarios.find(s=>s.id===fxpScenarioId);
  if(fxpScenarioId&&!scenario)fxpScenarioId=null;
  const rows=(scenario?window.JPWFx.engine.fxScenarioTimeline(plan,scenario):live.forecast).filter(r=>r.phase!=='actual');
  const row=rows.find(r=>r.month===fxpSelectedMonth)||rows[0];
  fxpSelectedMonth=row?row.month:null;
  return `<section class="fxp-block fxp-timeline-editor"><div class="fxp-block-head"><h3>Editar projeção mensal</h3><span>${fxpBadge(scenario?'SCENARIO':'PLAN')}</span></div>${fxpReferenceHTML()}
    <div class="fxp-scenario-tools"><label>Camada<select id="fxpScenarioSelect"><option value="">PLAN · vigente</option>${scenarios.map(s=>`<option value="${esc(s.id)}" ${s.id===fxpScenarioId?'selected':''}>SCENARIO · ${esc(s.name)}</option>`).join('')}</select></label><label>Novo cenário<input id="fxpScenarioName" placeholder="Nome da hipótese"></label><button type="button" id="fxpScenarioCreate">Criar cenário do plano</button>${scenario?'<button type="button" id="fxpScenarioArchive">Arquivar cenário</button>':''}</div>
    <p class="fxp-note">Editar a linha N recalcula o fechamento dessa linha e as seguintes. Os meses anteriores e ACTUAL permanecem intactos.</p>
    ${row?`<div class="params-grid"><label>Linha (mês)<select id="fxpRowMonth">${rows.map(r=>`<option value="${r.month}" ${r.month===fxpSelectedMonth?'selected':''}>${r.month} · ${fxpPct(r.rate)}</option>`).join('')}</select></label><label>Taxa planejada (% a.m.)<input id="fxpRowRate" type="number" step="0.01" value="${Number.isFinite(row.rate)?row.rate*100:''}"></label><label>Aporte pessoal USD<input id="fxpRowPersonal" type="number" min="0" step="0.01" value="${Number.isFinite(row.personalUsd)?row.personalUsd:''}"></label><label>Aporte Prop USD<input id="fxpRowProp" type="number" min="0" step="0.01" value="${Number.isFinite(row.propUsd)?row.propUsd:''}"></label><label>Motivo<input id="fxpRowNote" type="text"></label></div><button type="button" id="fxpRowSave">Salvar linha e recalcular posteriores</button><details class="fxp-rebase"><summary>Rebase explícito a partir desta linha</summary><label>Novo saldo de abertura (USD)<input type="number" min="0" step="0.01" id="fxpRebaseOpening"></label><p>Aplica uma nova âncora somente à projeção selecionada. Não altera baseline nem fechamentos reais.</p><button type="button" id="fxpRebaseSave">Confirmar rebase da projeção</button></details>`:'<p>Todos os meses estão realizados; nenhum mês projetado pode ser editado.</p>'}<div id="fxpTimelineErr" role="status"></div></section>`;
}
function fxpBindTimeline(root,live){
  const g=id=>root.querySelector('#'+id),error=res=>{g('fxpTimelineErr').innerHTML=fxpErrHTML(res.errors);};
  g('fxpScenarioSelect').onchange=e=>{fxpScenarioId=e.target.value||null;renderFxPlanning();};
  g('fxpScenarioCreate').onclick=()=>{const res=window.JPWFx.state.fxScenarioSave({name:g('fxpScenarioName').value});if(!res.ok){error(res);return;}fxpForgetDraft('scenario');fxpScenarioId=res.id;renderFxPlanning();};
  if(g('fxpScenarioArchive'))g('fxpScenarioArchive').onclick=()=>{if(!confirm('Arquivar este cenário preservando sua história?'))return;const res=window.JPWFx.state.fxScenarioDelete(fxpScenarioId);if(!res.ok){error(res);return;}fxpScenarioId=null;renderFxPlanning();};
  if(!g('fxpRowMonth'))return;
  const plan=live.plan,scenario=(plan.scenarios||[]).find(s=>s.id===fxpScenarioId);
  const rows=scenario?window.JPWFx.engine.fxScenarioTimeline(plan,scenario):live.forecast;
  g('fxpRowMonth').onchange=()=>{fxpSelectedMonth=g('fxpRowMonth').value;const row=rows.find(r=>r.month===g('fxpRowMonth').value);g('fxpRowRate').value=Number.isFinite(row.rate)?row.rate*100:'';g('fxpRowPersonal').value=Number.isFinite(row.personalUsd)?row.personalUsd:'';g('fxpRowProp').value=Number.isFinite(row.propUsd)?row.propUsd:'';g('fxpRebaseOpening').value='';};
  const done=res=>{if(!res.ok){fxpRememberDraft(root,'timeline','fxpTimelineErr',res);return;}fxpForgetDraft('timeline');renderFxPlanning();};
  g('fxpRowSave').onclick=()=>done(window.JPWFx.state.fxPlanReviseFromMonth(g('fxpRowMonth').value,{rate:fxpParsePct(g('fxpRowRate').value,rows.find(r=>r.month===g('fxpRowMonth').value)?.rate),personalUsd:fxpParseNum(g('fxpRowPersonal').value),propUsd:fxpParseNum(g('fxpRowProp').value)},g('fxpRowNote').value,fxpScenarioId));
  g('fxpRebaseSave').onclick=()=>{if(!confirm('Aplicar o rebase somente à projeção a partir de '+g('fxpRowMonth').value+'?'))return;done(window.JPWFx.state.fxPlanRebase(g('fxpRowMonth').value,fxpParseNum(g('fxpRebaseOpening').value),g('fxpRowNote').value,fxpScenarioId));};
}
function fxpLedgerPeriodOptions(accountId,selected=''){
  const periods=S.forex?.accountContexts?.accounts?.[accountId]?.periods||{};
  const options=Object.values(periods).sort((a,b)=>String(a.startedAt).localeCompare(String(b.startedAt)));
  if(selected&&!periods[selected])options.push({periodId:selected,startedAt:'Período não conciliado'});
  return '<option value="">Selecione um período</option>'+options.map(p=>`<option value="${esc(p.periodId)}" ${p.periodId===selected?'selected':''}>${esc(p.startedAt||'Data não informada')}${p.currency?' · '+esc(p.currency):''}</option>`).join('');
}
function fxpLedgerImportHTML(live){
  const context=ledgerContext(),accounts=(S.accounts||[]).filter(a=>a.forexAccountId).map(a=>({id:a.forexAccountId,name:a.nome||a.forexAccountId}));
  for(const [id,entry] of Object.entries(S.forex?.accountContexts?.archivedAccounts||{}))if(!accounts.some(a=>a.id===id))accounts.push({id,name:(entry.record?.nome||id)+' · arquivada'});
  if(context.accountId&&!accounts.some(a=>a.id===context.accountId))accounts.push({id:context.accountId,name:'Identidade de origem não conciliada'});
  return `<section class="fxp-block fxp-ledger-import"><h3>Importar ACTUAL da Contabilidade</h3><p class="fxp-note">Confira conta, período, completude e depósitos efetivos. Revisar origem cria uma prévia; importar confirma este fechamento. A importação guarda os IDs e versões de origem; alterações posteriores na Contabilidade não sobrescrevem este fechamento.</p><div class="params-grid"><label>Mês<input type="month" id="fxpLedgerMonth" value="${live.nextOpenMonth||live.lastClosedMonth||''}"></label><label>Conta de origem<select id="fxpLedgerAccount"><option value="">Selecione uma conta</option>${accounts.map(a=>`<option value="${esc(a.id)}" ${a.id===context.accountId?'selected':''}>${esc(a.name)}</option>`).join('')}</select></label><label>Período de origem<select id="fxpLedgerPeriod">${fxpLedgerPeriodOptions(context.accountId,context.periodId)}</select></label></div><label><input type="checkbox" id="fxpLedgerComplete"> Confirmo que os fechamentos deste mês estão completos para esta conta e período</label><label><input type="checkbox" id="fxpLedgerContributionsConfirmed"> Conferi os depósitos efetivos deste mês, inclusive se forem zero.</label><button type="button" id="fxpLedgerPreviewBtn">Revisar origem</button><pre id="fxpLedgerPreview" aria-live="polite" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre><label><input type="checkbox" id="fxpLedgerReplace"> Autorizar substituição explícita se já houver ACTUAL neste mês</label><button type="button" id="fxpLedgerImportBtn" disabled>Importar fechamento revisado</button><div id="fxpLedgerImportErr" role="status"></div></section>`;
}
function fxpBindLedgerImport(root){
  const g=id=>root.querySelector('#'+id);
  const options=()=>({accountId:g('fxpLedgerAccount').value.trim(),periodId:g('fxpLedgerPeriod').value.trim(),complete:g('fxpLedgerComplete').checked,contributionsConfirmed:g('fxpLedgerContributionsConfirmed').checked});
  fxpLedgerPreview=null;
  g('fxpLedgerAccount').addEventListener('change',()=>{g('fxpLedgerPeriod').innerHTML=fxpLedgerPeriodOptions(g('fxpLedgerAccount').value);fxpLedgerPreview=null;g('fxpLedgerImportBtn').disabled=true;g('fxpLedgerPreview').textContent='Conta alterada. Selecione o período e revise a origem novamente.';});
  root.querySelectorAll('#fxpLedgerMonth,#fxpLedgerAccount,#fxpLedgerPeriod,#fxpLedgerComplete,#fxpLedgerContributionsConfirmed').forEach(el=>el.addEventListener('input',()=>{fxpLedgerPreview=null;g('fxpLedgerImportBtn').disabled=true;}));
  g('fxpLedgerPreviewBtn').onclick=()=>{fxpLedgerPreview=window.JPWLedger.monthlyActual(g('fxpLedgerMonth').value,options());const p=fxpLedgerPreview;g('fxpLedgerPreview').textContent=p.status+' · '+p.source.rows.length+' fechamentos\n'+(p.issues.length?p.issues.join('\n'):'Abertura '+fxpBoardMoney(p.source.openingBalanceUsd)+' · resultado '+fxpBoardMoney(p.profitUsd)+' · fechamento '+fxpBoardMoney(p.source.closingBalanceUsd))+(g('fxpLedgerContributionsConfirmed').checked?'':'\nConfira e confirme os depósitos efetivos deste mês, inclusive quando forem zero.');g('fxpLedgerImportBtn').disabled=p.status!=='COMPLETE'||!g('fxpLedgerContributionsConfirmed').checked;};
  g('fxpLedgerImportBtn').onclick=()=>{
    const res=window.JPWFx.state.fxPlanImportLedgerActual(g('fxpLedgerMonth').value,{...options(),sourceVersion:fxpLedgerPreview&&fxpLedgerPreview.source.version,replace:g('fxpLedgerReplace').checked});
    if(!res.ok){fxpRememberDraft(root,'ledgerImport','fxpLedgerImportErr',res);return;}fxpForgetDraft('ledgerImport');renderFxPlanning();
  };
}

// ---- Render principal -------------------------------------------------------
function renderFxPlanning({restoreViewFocus=false}={}){
  const root=document.getElementById('fxPlanningRoot'); if(!root) return;
  // Removing a focused editor can emit change before the old node detaches.
  // Such teardown events must never be captured under the incoming context.
  fxpRendering=true;
  try{
  // Release observers/listeners before replacing the old chart subtree.
  window.JPWScenarioFan?.destroy(root.querySelector('#fxpMainChart'));
  fxpRetainUnknownPresentation(root);
  const presentation=fxpCapturePresentation(root);
  fxpRememberPresentation(root,presentation);
  fxpBindPresentationMemory(root);
  fxpBindInputDrafts(root);
  const previousTimeline=root.querySelector('#fxpTimelineDisclosure');
  if(previousTimeline)fxpTimelineDisclosureState[previousTimeline.dataset.view]=previousTimeline.open;
  fxpCaptureRejectedDrafts(root);
  const unknown=jpWealthPersistenceOutcomeIsUnknown();
  const issue=unknown?'':window.JPWFx.state.fxEnvelopeIssue();
  if(issue){root.innerHTML=fxpErrHTML([issue]);return;}
  const live=fxpDisplayLive(root);
  fxpSyncChartComparison(live);
  if(!unknown){root.__fxpConfirmedRead={epoch:jpWealthPersistenceEpoch(),planId:live?.plan.id||null,live:live?structuredClone(live):null};delete root.dataset.fxpReading;}
  if(fxpScenarioId&&!live?.plan.scenarios?.some(scenario=>scenario.id===fxpScenarioId))fxpScenarioId=null;
  const scope={epoch:jpWealthPersistenceEpoch(),planId:live?.plan.id||null,scenarioId:fxpScenarioId};
  for(const key of fxpInputDrafts.keys()){
    const [epoch,planId]=JSON.parse(key);
    if(epoch!==scope.epoch||planId!==scope.planId)fxpInputDrafts.delete(key);
  }
  root.__fxpDraftScope=scope;
  for(const key of fxpMonthlyDrafts.keys()){const [epoch,planId]=JSON.parse(key);if(epoch!==scope.epoch||planId!==scope.planId){fxpMonthlyDrafts.delete(key);fxpMonthlyErrors.delete(key);}}
  for(const key of fxpMonthlyAuxDrafts.keys()){const [epoch,planId]=JSON.parse(key);if(epoch!==scope.epoch||planId!==scope.planId)fxpMonthlyAuxDrafts.delete(key);}
  root.__fxpPresentationScope=JSON.stringify([scope.epoch,scope.planId,scope.scenarioId,fxpView]);
  for(const key of fxpPresentationByScope.keys()){const [epoch,planId]=JSON.parse(key);if(epoch!==scope.epoch||planId!==scope.planId)fxpPresentationByScope.delete(key);}
  const remembered=presentation.scope!==root.__fxpPresentationScope&&fxpPresentationByScope.get(root.__fxpPresentationScope);
  const incomingPresentation=remembered?{...remembered,focus:restoreViewFocus?remembered.focus:null}:presentation;
  const card=document.getElementById('fxPlanningCard');
  if(card){card.dataset.fxpState=live?'active':'empty';card.dataset.fxpView=fxpView;}
  if(unknown&&!live){root.innerHTML=fxpUnknownNoticeHTML(false);if(card)card.dataset.fxpState='unknown';return;}
  if(!live){ root.innerHTML=fxpReferenceHTML()+fxpCreateFormHTML(); fxpBindCreate(root); fxpRestoreInputDrafts(root); fxpRestoreRejectedDrafts(root); fxpRestorePresentation(root,incomingPresentation); return; }
  const body=fxpView==='overview'?fxpOverviewHTML(live)
    :fxpView==='planning'?(fxpScenarioId?fxpTableHTML(live):fxpPlanningHTML(live))
    :fxpView==='actuals'?fxpActualsHTML(live)
    :fxpTableHTML(live);
  const selectedScenario=(live.plan.scenarios||[]).find(s=>s.id===fxpScenarioId);
  const layers='<div class="fxp-layer-key" aria-label="Camadas do planejamento"><span>'+fxpBadge('ACTUAL')+(unknown?' Realizado da leitura anterior · confirmação indisponível':' Realizado confirmado')+'</span><span>'+fxpBadge('PLAN')+(unknown?' Projeção da leitura anterior':' Projeção vigente')+'</span><span>'+fxpBadge('SCENARIO')+' Hipótese independente</span></div>';
  const timeline=(fxpView==='planning'||fxpView==='table')?`<details id="fxpTimelineDisclosure" class="fxp-edit-disclosure" data-view="${fxpView}" ${fxpTimelineDisclosureState[fxpView]||fxpRejectedDrafts.timeline?'open':''}><summary>Editar projeção · ${selectedScenario?'SCENARIO: '+esc(selectedScenario.name):'PLAN vigente'}</summary>${fxpTimelineEditorHTML(live)}</details>`:'';
  const consultation=body;
  const general=fxpView==='table'?`<details class="fxp-month-general" id="fxpGeneralAssumptions"><summary>Premissas gerais · rentabilidade e depósitos recorrentes</summary>${fxpPlanningHTML(live)}</details>`:'';
  root.innerHTML=`
    <p class="fxp-note fxp-plan-context"><b>${esc(live.plan.name)}</b> · Plano patrimonial global · ${esc(live.plan.baseline.startMonth)} + ${live.plan.baseline.horizonMonths} meses ·
    ${live.lastClosedMonth?`fechado até <b>${live.lastClosedMonth}</b> · próximo aberto <b>${live.nextOpenMonth||'—'}</b>`:'nenhum mês fechado ainda'}${unknown?' · última leitura anterior à tentativa':''}</p>${layers}
    <div class="fxp-section" role="region" id="fxpPanel-${fxpView}" aria-label="${esc(FXP_MODES.find(([key])=>key===fxpView)[1])}" tabindex="0">${fxpUnknownNoticeHTML()}${general}${fxpView==='planning'?timeline:''}${consultation}${fxpView==='table'?timeline:''}${fxpView==='actuals'?fxpLedgerImportHTML(live):''}</div>`;
  if(fxpView==='overview') fxpActivateOverview(root,live);
  if(fxpView==='table'||(fxpView==='planning'&&fxpScenarioId))
    root.querySelectorAll('[data-fxp-hist]').forEach(b=>b.addEventListener('click',()=>{ fxpHistFilter=b.dataset.fxpHist; renderFxPlanning(); }));
  if(fxpView==='table'||fxpView==='planning'&&!fxpScenarioId) fxpBindPlanning(root,live);
  fxpBindMonthlyBoard(root,live);
  if(fxpView==='table'||fxpView==='planning'&&fxpScenarioId)fxpBindChartControls(root,live);
  if(fxpView==='actuals') fxpBindActuals(root,live);
  if(fxpView==='planning'||fxpView==='table')fxpBindTimeline(root,live);
  if(fxpView==='actuals')fxpBindLedgerImport(root);
  fxpRestoreInputDrafts(root);
  fxpRestoreRejectedDrafts(root);
  fxpQualifyUnknownReading(root);
  fxpRestorePresentation(root,incomingPresentation);
  }finally{fxpRendering=false;}
}
// Superfície estritamente visual para o submenu hierárquico do shell. As
// chaves são os quatro modos já existentes; não persiste estado, não chama o
// engine e não cria uma segunda fonte de verdade financeira.
window.JPWFx.ui={renderFxPlanning,selectView:fxpSelectView,getView:fxpGetView,
  chartComparison:()=>({scenarioIds:[...fxpChartComparison.scenarioIds],baseline:fxpChartComparison.baseline})};
// Primeira pintura + repintura ao entrar na tela (dados normativos do painel de
// reservas podem ter mudado via Formulário de Início).
renderFxPlanning();
document.querySelectorAll('.tab[data-screen="fxplan"]').forEach(t=>t.addEventListener('click',()=>renderFxPlanning()));

jpwWorkspaceDraftProviders.set('planning',(reset=false)=>{
  if(reset){for(const key of Object.keys(fxpRejectedDrafts))delete fxpRejectedDrafts[key];fxpInputDrafts.clear();fxpMonthlyDrafts.clear();fxpMonthlyErrors.clear();fxpMonthlyAuxDrafts.clear();fxpPresentationByScope.clear();return [];}
  return Object.keys(fxpRejectedDrafts).length||fxpInputDrafts.size||fxpMonthlyDrafts.size||fxpMonthlyAuxDrafts.size?[{label:'Planejamento — edições pendentes',text:JSON.stringify({rejected:fxpRejectedDrafts,inputs:[...fxpInputDrafts].map(([key,draft])=>({identity:JSON.parse(key),...draft})),months:[...fxpMonthlyDrafts].map(([key,draft])=>({identity:JSON.parse(key),...draft})),auxiliary:[...fxpMonthlyAuxDrafts]})}]:[];
});
const fxpOriginalDraftProvider=jpwWorkspaceDraftProviders.get('planning');
jpwWorkspaceDraftProviders.set('planning',(reset=false)=>fxpOriginalDraftProvider(reset).map(item=>({...item,provider:'planning',version:1,context:{scenarioId:fxpScenarioId},baseReference:JSON.stringify(S.fxPlanning)})));
window.JPWWorkspaceDrafts.registerRestorer('planning',{
  inspect(item){
    try{const value=JSON.parse(item.text),plan=S.fxPlanning?.plan;
      const identityValid=(id,monthly)=>Array.isArray(id)&&id.length===4&&Number.isInteger(id[0])&&id[1]===(plan?.id||null)&&(monthly?/^\d{4}-(0[1-9]|1[0-2])$/.test(id[3])&&(!id[2]||plan?.scenarios?.some(s=>s.id===id[2])):Object.hasOwn(FXP_DRAFT_FIELDS,id[2]));
      const fieldsValid=fields=>jpwWorkspaceObject(fields)&&Object.values(fields).every(v=>typeof v==='string'||typeof v==='boolean');
      const shape=Array.isArray(value.inputs)&&Array.isArray(value.months)&&Array.isArray(value.auxiliary)&&value.inputs.every(e=>identityValid(e.identity,false)&&Object.hasOwn(FXP_DRAFT_FIELDS,e.group)&&e.group===e.identity[2]&&fieldsValid(e.fields)&&Object.keys(e.fields).every(id=>FXP_DRAFT_FIELDS[e.group].includes(id)))&&value.months.every(e=>identityValid(e.identity,true)&&['plan','actual'].includes(e.mode)&&e.sourceVersion===plan?.updatedAt&&fieldsValid(e.fields)&&Object.keys(e.fields).every(k=>['rate','personalUsd','propUsd','note','inputType','profitUsd','valuationFxRate','contributionsConfirmed'].includes(k)))&&value.auxiliary.every(e=>Array.isArray(e)&&e.length===2&&identityValid(JSON.parse(e[0]),true)&&fieldsValid(e[1]));
      return {compatible:shape&&!jpWealthPersistenceOutcomeIsUnknown()&&!fxpInputDrafts.size&&!fxpMonthlyDrafts.size&&!fxpMonthlyAuxDrafts.size&&!Object.keys(fxpRejectedDrafts).length&&item.baseReference===JSON.stringify(S.fxPlanning),reason:'O plano e os campos originais devem corresponder, sem gravação incerta ou outra edição aberta.'};}catch(_){return {compatible:false,reason:'Planejamento incompatível.'};}
  },
  reopen(item){
    if(typeof closeSettingsModal==='function')closeSettingsModal();if(window.JPWNavigation?.navigate('forex-planning')===false)throw new Error('Navegação recusada.');
    const value=JSON.parse(item.text),epoch=jpWealthPersistenceEpoch();fxpScenarioId=item.context?.scenarioId||null;
    for(const [name,draft] of Object.entries(value.rejected||{})){const restored=structuredClone(draft);if(restored.context){const context=JSON.parse(restored.context);context[0]=epoch;restored.context=JSON.stringify(context);}fxpRejectedDrafts[name]=restored;}
    for(const [entries,map] of [[value.inputs,fxpInputDrafts],[value.months,fxpMonthlyDrafts]])for(const entry of entries){const {identity,...draft}=entry;identity[0]=epoch;map.set(JSON.stringify(identity),draft);}
    for(const [key,draft] of value.auxiliary){const identity=JSON.parse(key);identity[0]=epoch;fxpMonthlyAuxDrafts.set(JSON.stringify(identity),draft);}
    renderFxPlanning();document.querySelector('#fxPlanningRoot input:not([disabled])')?.focus();
  }
});

/* Confirmed educational guide. No domain writes; validation is pure and shared with Backup Completo. */
(function(root){
  'use strict';
  const KEY='jpwealth_hedge_guide_v1',VERSION='2026-10-31';
  const MODES=Object.freeze({one:['planned','purchased','phase1','phase1-approved','funded','payout-requested','payout-received'],two:['planned','purchased','phase1','phase1-approved','phase2','phase2-approved','funded','payout-requested','payout-received'],instant:['planned','purchased','funded','payout-requested','payout-received']});
  const CATALOGS=['custom','ftmo-one','ftmo-two','ftmo-instant','ttp-one','ttp-two','ttp-instant'];
  let uncertain=false;
  const object=value=>value&&typeof value==='object'&&!Array.isArray(value);
  const keys=(value,names)=>object(value)&&Object.keys(value).length===names.length&&Object.keys(value).every(key=>names.includes(key));
  const number=(v,min,max=Number.MAX_VALUE)=>typeof v==='number'&&Number.isFinite(v)&&v>=min&&v<=max;
  const iso=value=>typeof value==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(value)&&Number.isFinite(Date.parse(value))&&new Date(value).toISOString()===value;
  const fail=reason=>{throw Error(reason||'Guia incompatível.');};
  function validate(raw){
    if(typeof raw!=='string'||raw.length>65536)fail();
    const value=JSON.parse(raw);
    if(!keys(value,['schemaVersion','revision','plan','stage','confirmedAt','updatedAt','milestones'])||value.schemaVersion!==1||!Number.isSafeInteger(value.revision)||value.revision<1||!iso(value.confirmedAt)||!iso(value.updatedAt)||value.updatedAt<value.confirmedAt)fail();
    const p=value.plan;
    if(!keys(p,['mode','catalogId','catalogVersion','input'])||!Object.hasOwn(MODES,p.mode)||!CATALOGS.includes(p.catalogId)||p.catalogVersion!==VERSION||p.catalogId!=='custom'&&!p.catalogId.endsWith('-'+p.mode))fail();
    const input=p.input;
    if(p.mode==='instant'){
      if(!keys(input,['nominalUSD','feeUSD'])||!number(input.nominalUSD,Number.MIN_VALUE)||!number(input.feeUSD,0))fail();
    }else{
      if(!keys(input,['nominalUSD','feeUSD','payoutPercent','drawdownPercent','targetsPercent','refundUSD','costs'])||!number(input.nominalUSD,Number.MIN_VALUE)||!number(input.feeUSD,0)||!number(input.payoutPercent,Number.MIN_VALUE,100)||!number(input.drawdownPercent,Number.MIN_VALUE,100)||!number(input.refundUSD,0,input.feeUSD)||!Array.isArray(input.targetsPercent)||input.targetsPercent.length!==(p.mode==='one'?1:2)||input.targetsPercent.some(v=>!number(v,Number.MIN_VALUE))||!Array.isArray(input.costs)||input.costs.length!==input.targetsPercent.length+1)fail();
      for(const row of input.costs)if(!keys(row,['passUSD','failUSD'])||Object.values(row).some(v=>v!==null&&!number(v,0)))fail();
    }
    if(!MODES[p.mode].includes(value.stage)||!Array.isArray(value.milestones)||!value.milestones.length||value.milestones.length>500)fail();
    let previous=value.confirmedAt;
    for(const m of value.milestones){if(!keys(m,['stage','confirmedAt'])||!MODES[p.mode].includes(m.stage)||!iso(m.confirmedAt)||m.confirmedAt<previous||m.confirmedAt>value.updatedAt)fail();previous=m.confirmedAt;}
    if(value.milestones[0].stage!=='planned'||value.milestones[0].confirmedAt!==value.confirmedAt||value.milestones.at(-1).stage!==value.stage)fail();
    return JSON.parse(raw);
  }
  function inspect(raw){if(raw===null)return {ok:true,reason:'missing',document:null,raw};try{return {ok:true,reason:'confirmed',document:validate(raw),raw};}catch(_){return {ok:false,reason:'incompatible',document:null,raw};}}
  function stored(){try{const raw=root.localStorage.getItem(KEY);return {ok:true,raw,storage:root.localStorage};}catch(_){return {ok:false,reason:'storage-unavailable',document:null};}}
  function read(){const current=stored();if(!current.ok)return current;const result=inspect(current.raw);if(result.ok)uncertain=false;return result;}
  async function write(document,options){
    if(uncertain)return {ok:false,reason:'unknown',document:null};
    if(!options||!Object.hasOwn(options,'expectedRaw')||options.expectedRaw!==null&&typeof options.expectedRaw!=='string')return {ok:false,reason:'refused',document:null};
    let candidate,raw;try{raw=JSON.stringify(document);candidate=validate(raw);}catch(_){return {ok:false,reason:'incompatible',document:null};}
    // Same origin-wide lock as import/finalization. Never accept its degraded
    // fallback: expectedRaw + readback alone do not serialize simultaneous tabs.
    if(typeof sessionAcquireWriteLock!=='function'||typeof sessionSerializationMode!=='function'||sessionSerializationMode()!=='weblocks')return {ok:false,reason:'locking-unavailable',document:null};
    const expectedRaw=options.expectedRaw,replacePlan=options.replacePlan===true,signal=options.signal;
    try{return await sessionAcquireWriteLock(({degraded})=>{
      if(degraded)return {ok:false,reason:'locking-unavailable',document:null};
      if(signal?.aborted)return {ok:false,reason:'cancelled',document:null};
      if(uncertain)return {ok:false,reason:'unknown',document:null};
      const before=stored();if(!before.ok)return before;
      if(before.raw!==expectedRaw)return {ok:false,reason:'concurrent-change',document:null,raw:before.raw};
      const existing=inspect(before.raw);if(!existing.ok)return existing;
      if(existing.document){
        const old=existing.document;
        if(candidate.revision!==old.revision+1||(replacePlan?candidate.stage!=='planned'||candidate.milestones.length!==1:candidate.confirmedAt!==old.confirmedAt||JSON.stringify(candidate.plan)!==JSON.stringify(old.plan)||candidate.milestones.length<old.milestones.length||old.milestones.some((m,i)=>JSON.stringify(m)!==JSON.stringify(candidate.milestones[i]))))return {ok:false,reason:'refused',document:null,raw:before.raw};
      }
      try{before.storage.setItem(KEY,raw);}catch(_){}
      const after=stored();
      if(after.ok&&after.raw===raw)return {ok:true,reason:'confirmed',document:candidate,raw};
      if(after.ok&&after.raw===before.raw)return {ok:false,reason:'refused',document:null,raw:before.raw};
      uncertain=true;return {ok:false,reason:'unknown',document:null};
    });}catch(_){return {ok:false,reason:'lock-refused',document:null};}
  }
  root.JPWHedgeGuide=Object.freeze({KEY,validate,inspect,read,write,stages:mode=>(MODES[mode]||[]).slice()});
}(window));
/* Mesas Proprietárias: local educational hypotheses, never financial records. */
(function(root){
  'use strict';
  const labels={nominalUSD:'Capital nominal da prop · US$',feeUSD:'Taxa do desafio · US$',payoutPercent:'Payout · %',drawdownPercent:'Drawdown máximo fixo · %',target1Percent:'Meta da avaliação 1 · %',target2Percent:'Meta da avaliação 2 · %',refundUSD:'Reembolso previsto no primeiro payout · US$'};
  const blank=()=>Object.fromEntries(Object.keys(labels).map(key=>[key,'']));
  const fresh=()=>({instant:{fields:blank(),costs:[],example:false},1:{fields:blank(),costs:[{passUSD:'',failUSD:''},{passUSD:'',failUSD:''}],example:false},2:{fields:blank(),costs:[{passUSD:'',failUSD:''},{passUSD:'',failUSD:''},{passUSD:'',failUSD:''}],example:false}});
  let drafts=fresh(),mode=1,host=null,active=false,controller=null;
  const usd=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
  const ratioFormat=new Intl.NumberFormat('pt-BR',{maximumFractionDigits:8});
  const percentage=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
  const esc=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const money=value=>Number.isFinite(value)?(value<=-.005?'−':'')+'US$ '+usd.format(Math.abs(value)<.005?0:Math.abs(value)):'—';
  function parse(raw){
    const text=String(raw??'').trim();
    if(text==='')return null;
    return /^[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)$/.test(text)?Number(text.replace(',','.')):NaN;
  }
  function field(name,label){
    const slider=!name.startsWith('costs.');
    return '<label class="hp-field"'+(name==='target2Percent'?' data-hedge-second-target hidden':'')+'><span>'+esc(label)+'</span><input type="text" inputmode="decimal" autocomplete="off" spellcheck="false" data-hedge-field="'+name+'" aria-describedby="hedgePropNumberHelp">'+(slider?'<input type="range" data-hedge-range="'+name+'" aria-label="Ajustar '+esc(label)+'" step="any">':'')+'<span class="hp-field-error" data-hedge-error="'+name+'"></span></label>';
  }
  function markup(){
    return '<div id="hedgePropRoot" class="hp-root">'+
      '<div class="hp-section-head"><div><p class="hp-eyebrow">Estudo e simulação</p><h3>Hedge Prop Firm</h3><p>Compare os caminhos entre uma avaliação da prop e uma conta pessoal com posições hipoteticamente opostas.</p></div><a href="#hedgePropHelp" data-hedge-action="help">Entenda o método</a></div>'+
      '<p class="hp-contract" id="hedgePropCompliance">A equivalência abaixo é matemática e condicional. FTMO restringe combinações coordenadas entre contas; The Trading Pit proíbe hedge externo coordenado. Esta simulação não autoriza operações. <a href="#hedgePropSources" data-hedge-action="sources">Ver fontes e condições</a>.</p>'+
      ''+catalogMarkup()+'<div class="hp-modes" role="group" aria-label="Etapas do desafio"><button type="button" data-hedge-mode="1" aria-pressed="true">Desafio de uma fase</button><button type="button" data-hedge-mode="2" aria-pressed="false">Desafio de duas fases</button><button type="button" data-hedge-mode="instant" aria-pressed="false">Conta Instant</button></div>'+
      '<div class="hp-workspace"><div class="hp-parameters"><div class="hp-section-head"><h4>Parâmetros da simulação</h4><div class="hp-actions"><button type="button" data-hedge-action="example">Carregar exemplo</button><button type="button" data-hedge-action="clear">Limpar</button></div></div>'+
      '<p id="hedgePropNumberHelp" class="hp-muted">Valores em US$, sem separador de milhar. Use vírgula ou ponto para os decimais; informe zero quando não houver taxa ou reembolso.</p>'+
      '<div class="hp-fields">'+Object.entries(labels).map(([name,label])=>field(name,label)).join('')+'</div><p class="hp-example" id="hedgePropExample" hidden>Exemplo didático das capturas: reembolso integral da taxa como hipótese. Não representa uma oferta ou configuração contratual de uma mesa.</p></div>'+
      '<div class="hp-reading"><section id="hedgePropInstant" class="hp-instant" hidden><span class="hp-eyebrow">Acesso direto</span><h4>Conta Instant: sem avaliação</h4><div class="hp-instant-flow"><span>Conta adquirida</span><span aria-hidden="true">→</span><span>Regras conferidas</span><span aria-hidden="true">→</span><span>Elegibilidade</span><span aria-hidden="true">→</span><span>Reward recebido</span></div><p>Não existe um desafio a compensar neste modo. O hedge de aprovação não se aplica. Limites, consistência e requisitos de Reward continuam válidos.</p></section><p id="hedgePropStatus" role="status" aria-live="polite"></p><div class="hp-budget" aria-label="Orçamento-base"><p>Orçamento-base incluindo a taxa</p><strong data-hedge-value="capitalIncludingFeeUSD">—</strong><span data-hedge-value="multipleIncludingFee">—</span><dl><div><dt>Taxa do desafio</dt><dd data-hedge-value="feeUSD">—</dd></div><div><dt>Reservas teóricas dos hedges</dt><dd data-hedge-value="hedgeCapitalUSD">—</dd></div></dl><p class="hp-muted">Antes de custos adicionais. A reserva não comprova margem da corretora, capital mínimo suficiente ou proteção contra stop-out.</p></div><div id="hedgePropFlow" class="hp-flow" aria-label="Fluxo das etapas"></div><div class="hp-target"><span>Meta da fase financiada para a recuperação ideal</span><strong data-hedge-value="fundedTargetUSD">—</strong></div></div></div>'+
      '<details id="hedgePropCosts" class="hp-disclosure"><summary>Custos adicionais e resultado de cada caminho</summary><p>Estime despesas reais adicionais em US$ para cada desfecho. Exclua a taxa já contabilizada, depósitos, reservas e custos já incluídos; custos simulados da prop não são automaticamente uma despesa real.</p><p class="hp-muted">Os custos mostram o déficit sem aumentar a exposição ou o alvo ideal. Vazio mantém o caminho pendente; zero informa explicitamente ausência de custo estimado.</p><div id="hedgePropCostFields" class="hp-cost-fields"></div><div id="hedgePropOutcomes" class="hp-outcomes"></div></details>'+
      '<details id="hedgePropMath" class="hp-disclosure"><summary>Conferir etapas e memória de cálculo</summary><div id="hedgePropDetails"></div></details>'+
      '<details id="hedgePropHelp" class="hp-disclosure"><summary>Entenda o método e suas hipóteses</summary><ol><li><strong>Começo:</strong> a taxa é uma despesa real; o capital nominal da prop não é um depósito pessoal.</li><li><strong>Avaliações:</strong> no modelo, a conta pessoal ganha se a prop atingir a perda máxima e perde se a prop atingir a meta. Passar na avaliação não gera um recebimento pessoal.</li><li><strong>Fase financiada:</strong> uma nova razão de exposição e uma meta procuram compensar as perdas acumuladas, condicionadas ao payout e ao reembolso informados.</li><li><strong>Custos e recebimento:</strong> compare cada caminho e o caso em que o alvo é atingido, mas payout e reembolso não são recebidos.</li></ol><p>O modelo usa o mesmo capital nominal reiniciado em cada etapa, drawdown fixo comum e equivalência monetária exata entre posições opostas. Limites diários, drawdown móvel, gaps, slippage, arredondamento de lotes, diferenças de contrato e stop-out não estão reproduzidos.</p><p>A reserva adicional de 100% aplica-se somente à perda teórica do hedge da financiada. É uma convenção de reserva, não margem calculada de uma corretora. Nenhum resultado garante aprovação, equilíbrio financeiro real ou autorização pelas regras do JP Wealth.</p><h5>Glossário rápido</h5><dl><div><dt>Capital nominal</dt><dd>Saldo de referência da conta da mesa; não é seu depósito.</dd></div><div><dt>Drawdown</dt><dd>Limite de perda conforme o contrato; pode ser fixo, diário ou móvel.</dd></div><div><dt>Payout / Reward</dt><dd>Pagamento condicionado às regras e à aprovação da mesa.</dd></div><div><dt>Reserva</dt><dd>Verba hipotética do estudo; não é margem calculada nem garantia.</dd></div><div><dt>Breakeven</dt><dd>Equilíbrio entre despesas e recebimentos; só o recebimento efetivo confirma esse resultado.</dd></div></dl></details>'+
      '<details id="hedgePropSources" class="hp-disclosure"><summary>Fontes, reembolso e condições contratuais</summary><p>Consulta em 31/10/2026. As condições dependem do produto e podem mudar; o simulador não comprova permissão contratual.</p><ul><li><a href="https://ftmo.com/en/forbidden-trading-practices/" target="_blank" rel="noopener noreferrer">FTMO — práticas proibidas</a>: restringe combinações manipulativas coordenadas, incluindo posições opostas entre contas e provedores.</li><li><a href="https://www.thetradingpit.com/general-terms-and-conditions" target="_blank" rel="noopener noreferrer">The Trading Pit — termos, §6.8.1</a>: proíbe hedge externo coordenado, inclusive com corretoras.</li><li><a href="https://ftmo.com/en/faq/is-the-entry-fee-refunded/" target="_blank" rel="noopener noreferrer">FTMO — reembolso da taxa</a>: o 2-Step prevê reembolso na primeira solicitação de Reward; 1-Step e Instant não o preveem.</li><li><a href="https://cortextradings.com/hedge-prop-firm/" target="_blank" rel="noopener noreferrer">Cortex — referência visual fornecida</a>: os exemplos foram reconstruídos a partir das capturas, sem acesso ao código da ferramenta.</li></ul></details>'+
      guideMarkup()+'<p class="hp-session-note">A simulação permanece temporária. Somente o plano e as etapas explicitamente confirmados são guardados, separados dos seus registros financeiros.</p></div>';
  }
  function input(){
    const d=drafts[mode],v=Object.fromEntries(Object.entries(d.fields).map(([key,value])=>[key,parse(value)]));
    return {nominalUSD:v.nominalUSD,feeUSD:v.feeUSD,payoutPercent:v.payoutPercent,drawdownPercent:v.drawdownPercent,refundUSD:v.refundUSD,targetsPercent:mode===1?[v.target1Percent]:[v.target1Percent,v.target2Percent],costs:d.costs.map(row=>({passUSD:parse(row.passUSD),failUSD:parse(row.failUSD)}))};
  }
  const catalog={
    custom:{name:'Simulação personalizada',summary:'Parâmetros próprios do estudo. Não representam uma oferta contratual.',rule:'Escolha uma mesa para consultar suas regras. O catálogo não preenche nem homologa esta simulação.',url:'https://ftmo.com/en/comparison-table/'},
    'ftmo-one':{name:'FTMO · 1-Step',summary:'Meta 10% · diário 3% · perda máxima 10% trailing EOD · Reward 90% · sem reembolso.',rule:'Consistência 50%; sem prazo máximo. O motor de perda fixa não reproduz o trailing nem o limite diário.',url:'https://ftmo.com/en/trading-objectives/'},
    'ftmo-two':{name:'FTMO · 2-Step',summary:'Metas 10% / 5% · diário 5% · perda máxima estática 10% · Reward até 90%.',rule:'Quatro dias mínimos por fase; sem prazo máximo. Reembolso no primeiro Reward. A taxa e o Reward efetivo dependem da oferta/conta; conferir antes de usar.',url:'https://ftmo.com/en/comparison-table/'},
    'ftmo-instant':{name:'FTMO · Instant',summary:'Sem avaliação · diário 3% · perda máxima 10% trailing intraday · Reward 90%.',rule:'Consistência 30%; primeiro Reward após 14 dias do primeiro trade; taxa sem reembolso. Saque não reinicia o trailing.',url:'https://ftmo.com/en/trading-objectives/'},
    'ttp-one':{name:'The Trading Pit · CFD Prime 1 fase',summary:'Reward até 80% · metas e limites numéricos: confirmar na oferta/Client Area.',rule:'100K/200K desde 29/04/2026: trailing EOD; demais condições dependem da compra/tamanho. Consistência 50% em 100K/200K desde 06/07/2026. Reembolso a partir do terceiro payout para compras desde 29/04/2026.',url:'https://support.thetradingpit.com/en/articles/835084-cfd-prime-rules'},
    'ttp-two':{name:'The Trading Pit · CFD Prime 2 fases',summary:'Duas avaliações · Reward até 80% · metas e limites: confirmar na oferta/Client Area.',rule:'Sem opção 200K. 100K desde 29/04/2026: trailing EOD; demais contas podem ter limite estático. Dias lucrativos e reembolso dependem da compra. Não presumir reembolso no primeiro payout.',url:'https://support.thetradingpit.com/en/articles/835083-cfd-prime-how-it-works'},
    'ttp-instant':{name:'The Trading Pit · CFD Instant',summary:'Sem avaliação · perda máxima 6% trailing até o saldo inicial · sem limite diário.',rule:'Consistência 20%–30% e risco por posição 0,5%–1% conforme tamanho. Primeiro pedido após 14 dias; limites próprios de Reward. Conferir a oferta.',url:'https://support.thetradingpit.com/en/articles/835380-cfd-instant-rules'}
  };
  const stageNames={planned:'Plano confirmado',purchased:'Conta adquirida',phase1:'Avaliação 1 em andamento','phase1-approved':'Avaliação 1 aprovada',phase2:'Avaliação 2 em andamento','phase2-approved':'Avaliação 2 aprovada',funded:'Conta financiada','payout-requested':'Reward solicitado','payout-received':'Primeiro Reward recebido'};
  const stageHelp={planned:'Confira a oferta, as regras vigentes e os custos antes de adquirir uma conta.',purchased:'Leia as regras da conta recebida e confira seus limites antes de começar.',phase1:'Acompanhe a avaliação e os limites do seu contrato. A razão exibida é teórica e não determina lotes ou ordens.','phase1-approved':'Aguarde a revisão da mesa e confira as regras da próxima etapa.',phase2:'Acompanhe a segunda avaliação; lucro de avaliação não é um recebimento.','phase2-approved':'Aguarde aprovação e liberação da conta. Confira o contrato da fase financiada.',funded:'Confira os requisitos e a elegibilidade do Reward. Meta atingida não equivale a dinheiro recebido.','payout-requested':'Aguarde a conferência e o recebimento; não marque o valor como recebido antes disso.','payout-received':'Confira o valor efetivamente recebido, taxas e eventual reembolso. Atualize as regras antes de um novo ciclo.'};
  const modeName=()=>mode==='instant'?'instant':mode===1?'one':'two';
  const sliderRules={nominalUSD:[1000,200000,1000],feeUSD:[0,5000,1],payoutPercent:[1,100,1],drawdownPercent:[0.1,30,0.1],target1Percent:[0.1,30,0.1],target2Percent:[0.1,30,0.1],refundUSD:[0,5000,1]};
  let guideState=null,guideMessage='',guideBusy=false,guideOperation=null;
  function catalogMarkup(){return '<div class="hp-catalog"><label for="hedgePropCatalog">Referência contratual <span class="hp-muted">· consulta em 31/10/2026</span></label><select id="hedgePropCatalog" aria-describedby="hedgePropCatalogReading"></select><div id="hedgePropCatalogReading"></div></div>';}
  function guideMarkup(){return '<section class="hp-guide" aria-labelledby="hedgePropGuideTitle"><div class="hp-section-head"><div><p class="hp-eyebrow">Seu acompanhamento</p><h4 id="hedgePropGuideTitle">Um marco de cada vez</h4></div><button type="button" data-hedge-action="save-plan">Confirmar plano e guardar</button></div><p class="hp-muted">Somente sua confirmação salva o plano e as etapas neste navegador. Nenhuma ordem é criada. O Backup Completo da versão compatível inclui esse registro.</p><p id="hedgePropGuideCurrent"></p><p id="hedgePropGuideHelp"></p><div class="hp-guide-controls"><label for="hedgePropGuideStage">Etapa atual<select id="hedgePropGuideStage"></select></label><button type="button" data-hedge-action="confirm-stage">Confirmar etapa</button><button type="button" data-hedge-action="load-plan">Retomar parâmetros salvos</button><button type="button" data-hedge-action="verify-guide">Conferir armazenamento</button></div><ol id="hedgePropMilestones" class="hp-milestones"></ol><p id="hedgePropGuideStatus" role="status" aria-live="polite"></p></section>';}
  function renderCatalog(){
    const select=host.querySelector('#hedgePropCatalog'),current=drafts[mode].catalogId||'custom',suffix='-'+modeName();
    select.replaceChildren();for(const [id,item]of Object.entries(catalog)){if(id!=='custom'&&!id.endsWith(suffix))continue;const option=document.createElement('option');option.value=id;option.textContent=item.name;select.append(option);}select.value=current;
    const item=catalog[current];host.querySelector('#hedgePropCatalogReading').innerHTML='<p>'+esc(item.summary)+'</p><details class="hp-catalog-detail"><summary aria-label="Detalhes da referência contratual">ⓘ Regras e fonte</summary><p class="hp-muted">'+esc(item.rule)+'</p><a href="'+item.url+'" target="_blank" rel="noopener noreferrer">Conferir fonte oficial ↗</a></details>';
  }
  function syncRanges(){
    for(const [key,rule] of Object.entries(sliderRules)){
      const range=host.querySelector('[data-hedge-range="'+key+'"]'),raw=drafts[mode].fields[key],value=parse(raw);if(!range)continue;
      range.min=String(Number.isFinite(value)?Math.min(rule[0],value):rule[0]);range.max=String(Number.isFinite(value)?Math.max(rule[1],value):rule[1]);range.step='any';
      range.value=String(Number.isFinite(value)?value:rule[0]);range.setAttribute('aria-valuetext',raw===''?'Não informado. Ajuste para simular.':raw+(key.endsWith('Percent')?' por cento':' dólares'));
    }
  }
  function refreshGuide(){
    if(!host)return;const d=guideState?.document,ready=guideState?.ok&&d;
    host.querySelector('#hedgePropGuideCurrent').textContent=ready?stageNames[d.stage]+' · '+(d.plan.mode==='one'?'Uma fase':d.plan.mode==='two'?'Duas fases':'Instant'):'Nenhum plano confirmado carregado.';
    host.querySelector('#hedgePropGuideHelp').textContent=ready?stageHelp[d.stage]:'Simule e confirme um plano para acompanhar seus marcos. A navegação e a digitação não gravam.';
    const select=host.querySelector('#hedgePropGuideStage');select.replaceChildren();for(const stage of root.JPWHedgeGuide.stages(d?.plan.mode||modeName())){const option=document.createElement('option');option.value=stage;option.textContent=stageNames[stage];select.append(option);}select.value=d?.stage||'planned';select.disabled=!ready;
    host.querySelector('[data-hedge-action="confirm-stage"]').disabled=guideBusy||!ready;host.querySelector('[data-hedge-action="load-plan"]').disabled=guideBusy||!ready;
    host.querySelector('[data-hedge-action="save-plan"]').disabled=guideBusy||guideState?.ok===false;host.querySelector('[data-hedge-action="verify-guide"]').disabled=guideBusy;select.disabled=guideBusy||!ready;host.querySelector('.hp-guide').setAttribute('aria-busy',String(guideBusy));
    host.querySelector('#hedgePropMilestones').innerHTML=ready?d.milestones.map(m=>'<li><span>'+esc(stageNames[m.stage])+'</span><time datetime="'+m.confirmedAt+'">'+esc(new Date(m.confirmedAt).toLocaleString('pt-BR'))+'</time></li>').join(''):'';
    host.querySelector('#hedgePropGuideStatus').textContent=guideMessage||(guideState?.ok===false?'O registro salvo não pôde ser conferido. Ele foi preservado; nenhuma substituição será feita. Use um Backup Completo compatível para recuperação.':'');
  }
  async function saveGuide(){
    if(guideBusy)return;
    const now=new Date().toISOString(),kind=modeName(),prior=guideState?.document;
    let values;if(mode==='instant'){values={nominalUSD:parse(drafts[mode].fields.nominalUSD),feeUSD:parse(drafts[mode].fields.feeUSD)};if(!Number.isFinite(values.nominalUSD)||values.nominalUSD<=0||!Number.isFinite(values.feeUSD)||values.feeUSD<0){guideMessage='Informe capital nominal e taxa válidos antes de confirmar.';refreshGuide();return;}}
    else{values=input();const model=root.JPWHedgeProp.calculate(values);if(!model.ok||model.costErrors.length){guideMessage='Confira os parâmetros e custos antes de confirmar o plano.';refreshGuide();return;}}
    const replacing=!!prior;if(replacing&&!root.confirm('Substituir o plano confirmado e seu histórico de etapas pelos parâmetros desta simulação? O registro anterior só será trocado após conferir a nova gravação.'))return;
    const document={schemaVersion:1,revision:(prior?.revision||0)+1,plan:{mode:kind,catalogId:drafts[mode].catalogId||'custom',catalogVersion:'2026-10-31',input:values},stage:'planned',confirmedAt:now,updatedAt:now,milestones:[{stage:'planned',confirmedAt:now}]};
    await commitGuide(document,{expectedRaw:guideState?.raw??null,replacePlan:replacing},'Plano confirmado e guardado.');
  }
  async function commitGuide(document,options,success){
    if(guideBusy)return;guideBusy=true;guideOperation=new AbortController();const operation=guideOperation,currentHost=host;
    guideMessage='Aguardando gravação segura…';refreshGuide();
    try{
      const result=await root.JPWHedgeGuide.write(document,{...options,signal:operation.signal});
      if(host===currentHost&&!operation.signal.aborted)handleGuideWrite(result,success);
    }finally{
      if(guideOperation===operation){guideOperation=null;guideBusy=false;if(host===currentHost)refreshGuide();}
    }
  }
  function handleGuideWrite(result,success){
    if(result.ok){guideState=result;guideMessage=success;}
    else{guideState={...result,document:guideState?.document||null};guideMessage=result.reason==='unknown'?'Resultado da gravação desconhecido. Seus parâmetros continuam abertos. Confira o armazenamento antes de tentar novamente.':result.reason==='locking-unavailable'?'Gravação segura indisponível nesta origem. Abra o app pelo inicializador local (Abrir JP Wealth.command) para guardar o guia. Seus parâmetros foram preservados.':result.reason==='lock-refused'?'Não foi possível obter acesso seguro ao armazenamento. Seus parâmetros foram preservados; confira antes de tentar novamente.':result.reason==='cancelled'?'Gravação cancelada. Seus parâmetros foram preservados.':result.reason==='concurrent-change'?'Outra aba alterou o guia. Seus parâmetros foram preservados. Confira o armazenamento antes de gravar.':'Não foi possível guardar. Seus parâmetros e o registro anterior foram preservados quando a gravação foi recusada.';}
    refreshGuide();
  }
  async function confirmStage(){
    if(guideBusy||!guideState?.ok||!guideState.document)return;
    const next=host.querySelector('#hedgePropGuideStage').value,old=guideState.document;if(next===old.stage){guideMessage='Esta etapa já está confirmada.';refreshGuide();return;}
    const now=new Date().toISOString(),document=JSON.parse(JSON.stringify(old));document.revision++;document.stage=next;document.updatedAt=now;document.milestones.push({stage:next,confirmedAt:now});
    await commitGuide(document,{expectedRaw:guideState.raw},'Etapa confirmada. O histórico anterior foi preservado.');
  }
  function loadPlan(){
    const d=guideState?.document;if(!guideState?.ok||!d)return;
    mode=d.plan.mode==='one'?1:d.plan.mode==='two'?2:'instant';const v=d.plan.input,target=drafts[mode];target.fields=blank();for(const key of Object.keys(labels))if(Object.hasOwn(v,key))target.fields[key]=String(v[key]);
    if(mode!=='instant'){target.fields.target1Percent=String(v.targetsPercent[0]);target.fields.target2Percent=mode===2?String(v.targetsPercent[1]):'';target.costs=v.costs.map(row=>Object.fromEntries(Object.entries(row).map(([key,value])=>[key,value===null?'':String(value)])));}target.catalogId=d.plan.catalogId;target.example=false;syncFields();guideMessage='Parâmetros retomados para revisão. Alterar a simulação não atualiza o plano salvo.';refreshGuide();
  }
  function onRangeKey(event){const range=event.target.closest('[data-hedge-range]');if(!range||!active)return;const key=range.dataset.hedgeRange,rule=sliderRules[key];if(!['ArrowLeft','ArrowDown','ArrowRight','ArrowUp','Home','End'].includes(event.key))return;event.preventDefault();let value=Number(range.value);value=event.key==='Home'?Number(range.min):event.key==='End'?Number(range.max):value+(['ArrowLeft','ArrowDown'].includes(event.key)?-1:1)*rule[2];range.value=String(Math.max(Number(range.min),Math.min(Number(range.max),Number(value.toPrecision(15)))));onInput({target:range});}
  function onCatalog(event){if(event.target.id!=='hedgePropCatalog'||!active)return;drafts[mode].catalogId=event.target.value;renderCatalog();}
  function syncFields(){
    host.querySelectorAll('[data-hedge-mode]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.hedgeMode===String(mode))));
    host.querySelectorAll('[data-hedge-field]').forEach(node=>{if(!node.dataset.hedgeField.startsWith('costs.'))node.value=drafts[mode].fields[node.dataset.hedgeField];});
    for(const node of host.querySelectorAll('.hp-fields > .hp-field')){const name=node.querySelector('[data-hedge-field]').dataset.hedgeField;node.hidden=name==='target2Percent'?mode!==2:mode==='instant'&&!['nominalUSD','feeUSD'].includes(name);node.querySelectorAll('input').forEach(input=>input.disabled=node.hidden);}
    host.querySelector('#hedgePropExample').hidden=!drafts[mode].example;host.querySelector('.hp-budget').hidden=mode==='instant';
    host.querySelector('#hedgePropInstant').hidden=mode!=='instant';host.querySelector('#hedgePropCosts').hidden=mode==='instant';host.querySelector('#hedgePropMath').hidden=mode==='instant';host.querySelector('.hp-target').hidden=mode==='instant';
    host.querySelector('[data-hedge-action="example"]').hidden=mode==='instant';
    renderCatalog();syncRanges();refreshGuide();
    const costHost=host.querySelector('#hedgePropCostFields');
    costHost.innerHTML=drafts[mode].costs.map((row,i)=>'<fieldset class="hp-cost-stage"><legend>'+(i===mode?'Fase financiada':'Avaliação '+(i+1))+'</legend>'+field('costs.'+i+'.passUSD',i===mode?'Ao atingir a meta · US$':'Ao passar · US$')+field('costs.'+i+'.failUSD',i===mode?'Ao perder a conta · US$':'Ao reprovar · US$')+'</fieldset>').join('');
    costHost.querySelectorAll('input').forEach(node=>{const [,i,key]=node.dataset.hedgeField.split('.');node.value=drafts[mode].costs[i][key];});
    update();
  }
  function errorField(fieldName){
    return fieldName.replace('targetsPercent[0]','target1Percent').replace('targetsPercent[1]','target2Percent').replace(/costs\[(\d+)\]/,'costs.$1');
  }
  function update(){
    if(!host||!controller)return;
    syncRanges();
    if(mode==='instant'){
      host.querySelector('#hedgePropStatus').textContent='Conta direta: confira o contrato e os requisitos antes de solicitar um Reward.';
      for(const key of ['hedgeCapitalUSD','capitalIncludingFeeUSD','fundedTargetUSD','multipleIncludingFee'])host.querySelector('[data-hedge-value="'+key+'"]').textContent='Não se aplica';
      host.querySelector('[data-hedge-value="feeUSD"]').textContent=money(parse(drafts[mode].fields.feeUSD));host.querySelector('#hedgePropFlow').replaceChildren();return;
    }
    const model=root.JPWHedgeProp.calculate(input());
    host.querySelectorAll('[data-hedge-error]').forEach(node=>node.textContent='');
    host.querySelectorAll('[data-hedge-field]').forEach(node=>node.removeAttribute('aria-invalid'));
    [...model.errors,...model.costErrors].forEach(error=>{
      if(error.code==='MISSING')return;
      const name=errorField(error.field),node=[...host.querySelectorAll('[data-hedge-field]')].find(n=>n.dataset.hedgeField===name);
      if(node){node.setAttribute('aria-invalid','true');const note=node.parentElement.querySelector('.hp-field-error');note.textContent=error.code==='PAYOUT_NOT_ABOVE_HEDGE'?'O payout deve superar a razão calculada.':'Confira o valor e a unidade; informe um número válido.';}
    });
    const set=(key,value)=>{const node=host.querySelector('[data-hedge-value="'+key+'"]');node.textContent=value;};
    host.querySelector('#hedgePropExample').hidden=!drafts[mode].example;
    const status=host.querySelector('#hedgePropStatus');
    if(!model.ok){
      const missing=model.errors.filter(e=>e.code==='MISSING').map(e=>labels[errorField(e.field)]).filter(Boolean);
      status.textContent=model.status==='INFEASIBLE'?'Não há recuperação positiva finita: o payout é menor ou igual à razão de exposição da financiada.':model.status==='UNREPRESENTABLE'?'Não é possível representar este cenário com segurança. Revise as grandezas informadas.':missing.length?'Preencha os parâmetros para ver a simulação: '+missing.join('; ')+'.':'Confira os campos indicados. O resultado anterior não está sendo utilizado.';
      ['feeUSD','hedgeCapitalUSD','capitalIncludingFeeUSD','fundedTargetUSD','multipleIncludingFee'].forEach(key=>set(key,'—'));
      host.querySelector('#hedgePropFlow').replaceChildren();
      host.querySelector('#hedgePropDetails').textContent='A memória de cálculo aparecerá após o preenchimento válido dos parâmetros.';
      host.querySelector('#hedgePropOutcomes').textContent='Preencha os parâmetros para comparar os caminhos.';
      return;
    }
    status.textContent=model.totals.feeUSD===0?'Sem custo inicial a recuperar. Os custos adicionais continuam sendo considerados nos caminhos informados.':'Modelo ideal calculado. Confira as hipóteses, os custos de cada caminho e as condições de recebimento.';
    for(const key of ['feeUSD','hedgeCapitalUSD','capitalIncludingFeeUSD'])set(key,money(model.totals[key]));
    set('fundedTargetUSD',money(model.funded.targetUSD));
    set('multipleIncludingFee',model.totals.multipleIncludingFee===null?'Múltiplo indisponível: taxa zero':ratioFormat.format(model.totals.multipleIncludingFee)+' × a taxa, incluindo a própria taxa');
    const evalCards=model.stages.map((stage,i)=>'<article class="hp-stage" data-hedge-stage="evaluation-'+i+'"><span class="hp-stage-number">'+(i+1)+'</span><h5>Avaliação '+(i+1)+'</h5><p class="hp-stage-metric">'+money(stage.hedgeCapitalUSD)+'</p><span class="hp-muted">Perda pessoal teórica ao passar</span><div class="hp-flow-outcome hp-flow-fail"><span>Reprovar</span><strong>'+money(model.outcomes.find(o=>o.id==='evaluation-fail-'+i).idealNetUSD)+'</strong><small>Resultado ideal antes dos custos</small></div><div class="hp-flow-outcome hp-flow-pass"><span>Aprovar → avançar</span><strong>'+money(-stage.accumulatedLossUSD)+'</strong><small>Despesa acumulada; lucro da avaliação não recebido</small></div></article>');
    const funded='<article class="hp-stage hp-funded" data-hedge-stage="funded"><span class="hp-stage-number">'+(mode+1)+'</span><h5>Fase financiada</h5><p class="hp-stage-metric">'+money(model.funded.reserveUSD)+'</p><span class="hp-muted">Reserva teórica com adicional de 100%</span><div class="hp-flow-outcome hp-flow-fail"><span>Perder a conta</span><strong>'+money(model.outcomes.find(o=>o.id==='funded-fail').idealNetUSD)+'</strong><small>Resultado ideal antes dos custos</small></div><div class="hp-flow-outcome hp-flow-pass"><span>Receber payout e reembolso</span><strong>'+money(model.outcomes.find(o=>o.id==='funded-pass').idealNetUSD)+'</strong><small>Condicionado ao recebimento</small></div></article>';
    host.querySelector('#hedgePropFlow').innerHTML='<div class="hp-payment"><span aria-hidden="true">◎</span><span>Taxa do desafio <strong>'+money(model.totals.feeUSD)+'</strong></span></div><div class="hp-diagram">'+evalCards.concat(funded).join('<span class="hp-flow-arrow" aria-hidden="true">→</span>')+'</div><div class="hp-equilibrium"><span aria-hidden="true">◇</span> Equilíbrio ideal condicionado <span class="hp-muted">Custos e execução podem produzir déficit.</span></div>';
    const title=outcome=>outcome.kind==='EVALUATION_FAIL'?'Reprovar na avaliação '+(outcome.stageIndex+1):outcome.kind==='FUNDED_FAIL'?'Perder a conta financiada':outcome.kind==='FUNDED_PASS'?'Atingir o alvo e receber payout/reembolso':'Atingir o alvo sem receber payout nem reembolso';
    const path=outcome=>outcome.kind==='EVALUATION_FAIL'?'failure-'+(outcome.stageIndex+1):outcome.kind==='FUNDED_FAIL'?'funded-stop':outcome.kind==='FUNDED_PASS'?'funded-success':'no-receipt';
    host.querySelector('#hedgePropOutcomes').innerHTML=model.outcomes.map(outcome=>'<div class="hp-outcome"><h5>'+title(outcome)+'</h5><dl><div><dt>Resultado ideal</dt><dd>'+money(outcome.idealNetUSD)+'</dd></div><div><dt>Custos deste caminho</dt><dd>'+(outcome.costStatus==='COMPLETE'?money(outcome.estimatedCostsUSD):outcome.costStatus==='INVALID'?'Revisar os custos':'Pendente')+'</dd></div><div><dt>Resultado após custos</dt><dd data-hedge-cost-path="'+path(outcome)+'"'+(outcome.costStatus==='COMPLETE'&&outcome.netAfterCostsUSD<=-.005?' class="hp-negative"':'')+'>'+(outcome.costStatus==='COMPLETE'?money(outcome.netAfterCostsUSD):outcome.costStatus==='INVALID'?'Custo inválido':'Pendente')+'</dd></div></dl></div>').join('');
    const stageDetails=model.stages.map((stage,i)=>'<div class="hp-math-stage"><h5>Avaliação '+(i+1)+'</h5><dl><div><dt>Meta da prop</dt><dd>'+money(stage.targetUSD)+'</dd></div><div><dt>Razão teórica de exposição</dt><dd>'+ratioFormat.format(stage.hedgeRatio)+'</dd></div></dl></div>').join('');
    host.querySelector('#hedgePropDetails').innerHTML='<p>Perda máxima fixa comum: '+money(model.drawdownUSD)+'. O capital nominal reinicia em cada etapa; as razões não são lotes executáveis.</p><div class="hp-math-stages">'+stageDetails+'<div class="hp-math-stage"><h5>Fase financiada</h5><dl><div><dt>Razão teórica de exposição</dt><dd>'+ratioFormat.format(model.funded.hedgeRatio)+'</dd></div><div><dt>Meta sobre o nominal</dt><dd>'+percentage.format(model.funded.targetPercent)+'%</dd></div></dl></div></div><p class="hp-formula">L₀ = taxa; qᵢ = Lᵢ₋₁ ÷ perda máxima; Hᵢ = qᵢ × meta; Lᵢ = Lᵢ₋₁ + Hᵢ. Na financiada: qf = Lₙ ÷ perda máxima; alvo = (Lₙ − reembolso) ÷ (payout − qf). Reserva financiada = 2 × qf × alvo.</p><p class="hp-muted">Percentuais entram como frações na fórmula. Precisão preservada no cálculo; valores exibidos são arredondados.</p>';
  }
  function onInput(event){
    const node=event.target.closest('[data-hedge-field],[data-hedge-range]');if(!node||!active)return;
    const name=node.dataset.hedgeField||node.dataset.hedgeRange;
    if(node.dataset.hedgeRange){const numeric=host.querySelector('[data-hedge-field="'+name+'"]');numeric.value=node.value;}
    if(name.startsWith('costs.')){const [,i,key]=name.split('.');drafts[mode].costs[i][key]=node.value;}
    else{drafts[mode].fields[name]=node.value;drafts[mode].example=false;}
    update();
  }
  function onClick(event){
    if(!active)return;
    const button=event.target.closest('[data-hedge-mode],[data-hedge-action]');if(!button)return;
    if(button.dataset.hedgeMode){const next=button.dataset.hedgeMode==='instant'?'instant':Number(button.dataset.hedgeMode);if(next!==mode){mode=next;syncFields();}return;}
    const action=button.dataset.hedgeAction;
    if(action==='save-plan'){saveGuide();return;}if(action==='confirm-stage'){confirmStage();return;}if(action==='load-plan'){loadPlan();return;}if(action==='verify-guide'){guideState=root.JPWHedgeGuide.read();guideMessage=guideState.ok?'Armazenamento conferido. Revise o plano antes de confirmar outra alteração.':'';refreshGuide();return;}
    if(action==='example'){
      drafts[mode].fields={nominalUSD:'200000',feeUSD:'1200',payoutPercent:'80',drawdownPercent:mode===1?'7':'10',target1Percent:'10',target2Percent:mode===1?'':'5',refundUSD:'1200'};
      drafts[mode].example=true;syncFields();
    }else if(action==='clear'){drafts[mode]=fresh()[mode];syncFields();}
    else if(action==='help'||action==='sources'){
      event.preventDefault();const details=host.querySelector(action==='help'?'#hedgePropHelp':'#hedgePropSources');details.open=true;details.querySelector('summary').focus({preventScroll:true});details.scrollIntoView({block:'nearest',behavior:'instant'});
    }
  }
  function mount(slot){
    if(controller&&host===slot)return controller;
    if(controller)disposeForSession();
    host=slot;if(!host)return null;
    guideState=root.JPWHedgeGuide.read();guideMessage='';host.innerHTML=markup();host.addEventListener('input',onInput);host.addEventListener('click',onClick);host.addEventListener('keydown',onRangeKey);host.addEventListener('change',onCatalog);
    controller=Object.freeze({activate,deactivate,disposeForSession});syncFields();return controller;
  }
  function activate(){if(controller)active=true;}
  function deactivate(){active=false;}
  function disposeForSession(){
    guideOperation?.abort();guideOperation=null;guideBusy=false;active=false;drafts=fresh();mode=1;
    if(host){host.removeEventListener('input',onInput);host.removeEventListener('click',onClick);host.removeEventListener('keydown',onRangeKey);host.removeEventListener('change',onCatalog);host.replaceChildren();}
    host=null;controller=null;
  }
  root.JPWPropFirms=Object.freeze({mount,activate,deactivate,disposeForSession});
}(window));

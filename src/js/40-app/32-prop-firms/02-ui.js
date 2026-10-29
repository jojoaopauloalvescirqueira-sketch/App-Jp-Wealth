/* Mesas Proprietárias: local educational hypotheses, never financial records. */
(function(root){
  'use strict';
  const labels={nominalUSD:'Capital nominal da prop · US$',feeUSD:'Taxa do desafio · US$',payoutPercent:'Payout · %',drawdownPercent:'Drawdown máximo fixo · %',target1Percent:'Meta da avaliação 1 · %',target2Percent:'Meta da avaliação 2 · %',refundUSD:'Reembolso previsto no primeiro payout · US$'};
  const blank=()=>Object.fromEntries(Object.keys(labels).map(key=>[key,'']));
  const fresh=()=>({1:{fields:blank(),costs:[{passUSD:'',failUSD:''},{passUSD:'',failUSD:''}],example:false},2:{fields:blank(),costs:[{passUSD:'',failUSD:''},{passUSD:'',failUSD:''},{passUSD:'',failUSD:''}],example:false}});
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
    return '<label class="hp-field"'+(name==='target2Percent'?' data-hedge-second-target hidden':'')+'><span>'+esc(label)+'</span><input type="text" inputmode="decimal" autocomplete="off" spellcheck="false" data-hedge-field="'+name+'" aria-describedby="hedgePropNumberHelp"><span class="hp-field-error" data-hedge-error="'+name+'"></span></label>';
  }
  function markup(){
    return '<div id="hedgePropRoot" class="hp-root">'+
      '<div class="hp-section-head"><div><p class="hp-eyebrow">Estudo e simulação</p><h3>Hedge Prop Firm</h3><p>Compare os caminhos entre uma avaliação da prop e uma conta pessoal com posições hipoteticamente opostas.</p></div><a href="#hedgePropHelp" data-hedge-action="help">Entenda o método</a></div>'+
      '<p class="hp-contract">A equivalência abaixo é matemática e condicional. FTMO restringe combinações coordenadas entre contas; The Trading Pit proíbe hedge externo coordenado. <a href="#hedgePropSources" data-hedge-action="sources">Ver fontes e condições</a>.</p>'+
      '<div class="hp-modes" role="group" aria-label="Etapas do desafio"><button type="button" data-hedge-mode="1" aria-pressed="true">Desafio de uma fase</button><button type="button" data-hedge-mode="2" aria-pressed="false">Desafio de duas fases</button></div>'+
      '<div class="hp-workspace"><div class="hp-parameters"><div class="hp-section-head"><h4>Parâmetros da simulação</h4><div class="hp-actions"><button type="button" data-hedge-action="example">Carregar exemplo</button><button type="button" data-hedge-action="clear">Limpar</button></div></div>'+
      '<p id="hedgePropNumberHelp" class="hp-muted">Valores em US$, sem separador de milhar. Use vírgula ou ponto para os decimais; informe zero quando não houver taxa ou reembolso.</p>'+
      '<div class="hp-fields">'+Object.entries(labels).map(([name,label])=>field(name,label)).join('')+'</div><p class="hp-example" id="hedgePropExample" hidden>Exemplo didático das capturas: reembolso integral da taxa como hipótese. Não representa uma oferta ou configuração contratual de uma mesa.</p></div>'+
      '<div class="hp-reading"><p id="hedgePropStatus" role="status" aria-live="polite"></p><div class="hp-budget" aria-label="Orçamento-base"><p>Orçamento-base incluindo a taxa</p><strong data-hedge-value="capitalIncludingFeeUSD">—</strong><span data-hedge-value="multipleIncludingFee">—</span><dl><div><dt>Taxa do desafio</dt><dd data-hedge-value="feeUSD">—</dd></div><div><dt>Reservas teóricas dos hedges</dt><dd data-hedge-value="hedgeCapitalUSD">—</dd></div></dl><p class="hp-muted">Antes de custos adicionais. A reserva não comprova margem da corretora, capital mínimo suficiente ou proteção contra stop-out.</p></div><div id="hedgePropFlow" class="hp-flow" aria-label="Fluxo das etapas"></div><div class="hp-target"><span>Meta da fase financiada para a recuperação ideal</span><strong data-hedge-value="fundedTargetUSD">—</strong></div></div></div>'+
      '<details id="hedgePropCosts" class="hp-disclosure"><summary>Custos adicionais e resultado de cada caminho</summary><p>Estime despesas reais adicionais em US$ para cada desfecho. Exclua a taxa já contabilizada, depósitos, reservas e custos já incluídos; custos simulados da prop não são automaticamente uma despesa real.</p><p class="hp-muted">Os custos mostram o déficit sem aumentar a exposição ou o alvo ideal. Vazio mantém o caminho pendente; zero informa explicitamente ausência de custo estimado.</p><div id="hedgePropCostFields" class="hp-cost-fields"></div><div id="hedgePropOutcomes" class="hp-outcomes"></div></details>'+
      '<details id="hedgePropMath" class="hp-disclosure"><summary>Conferir etapas e memória de cálculo</summary><div id="hedgePropDetails"></div></details>'+
      '<details id="hedgePropHelp" class="hp-disclosure"><summary>Entenda o método e suas hipóteses</summary><ol><li><strong>Começo:</strong> a taxa é uma despesa real; o capital nominal da prop não é um depósito pessoal.</li><li><strong>Avaliações:</strong> no modelo, a conta pessoal ganha se a prop atingir a perda máxima e perde se a prop atingir a meta. Passar na avaliação não gera um recebimento pessoal.</li><li><strong>Fase financiada:</strong> uma nova razão de exposição e uma meta procuram compensar as perdas acumuladas, condicionadas ao payout e ao reembolso informados.</li><li><strong>Custos e recebimento:</strong> compare cada caminho e o caso em que o alvo é atingido, mas payout e reembolso não são recebidos.</li></ol><p>O modelo usa o mesmo capital nominal reiniciado em cada etapa, drawdown fixo comum e equivalência monetária exata entre posições opostas. Limites diários, drawdown móvel, gaps, slippage, arredondamento de lotes, diferenças de contrato e stop-out não estão reproduzidos.</p><p>A reserva adicional de 100% aplica-se somente à perda teórica do hedge da financiada. É uma convenção de reserva, não margem calculada de uma corretora. Nenhum resultado garante aprovação, equilíbrio financeiro real ou autorização pelas regras do JP Wealth.</p></details>'+
      '<details id="hedgePropSources" class="hp-disclosure"><summary>Fontes, reembolso e condições contratuais</summary><p>Consulta em 27/10/2026. As condições dependem do produto e podem mudar; o simulador não comprova permissão contratual.</p><ul><li><a href="https://ftmo.com/en/forbidden-trading-practices/" target="_blank" rel="noopener noreferrer">FTMO — práticas proibidas</a>: restringe combinações manipulativas coordenadas, incluindo posições opostas entre contas e provedores.</li><li><a href="https://www.thetradingpit.com/general-terms-and-conditions" target="_blank" rel="noopener noreferrer">The Trading Pit — termos, §6.8.1</a>: proíbe hedge externo coordenado, inclusive com corretoras.</li><li><a href="https://ftmo.com/en/faq/is-the-entry-fee-refunded/" target="_blank" rel="noopener noreferrer">FTMO — reembolso da taxa</a>: o 2-Step prevê reembolso na primeira solicitação de Reward; 1-Step e Instant não o preveem.</li><li><a href="https://cortextradings.com/hedge-prop-firm/" target="_blank" rel="noopener noreferrer">Cortex — referência visual fornecida</a>: os exemplos foram reconstruídos a partir das capturas, sem acesso ao código da ferramenta.</li></ul></details>'+
      '<p class="hp-session-note">Simulação temporária neste aplicativo. Ela não consulta suas contas, não salva registros e é descartada ao finalizar a sessão ou recarregar a página.</p></div>';
  }
  function input(){
    const d=drafts[mode],v=Object.fromEntries(Object.entries(d.fields).map(([key,value])=>[key,parse(value)]));
    return {nominalUSD:v.nominalUSD,feeUSD:v.feeUSD,payoutPercent:v.payoutPercent,drawdownPercent:v.drawdownPercent,refundUSD:v.refundUSD,targetsPercent:mode===1?[v.target1Percent]:[v.target1Percent,v.target2Percent],costs:d.costs.map(row=>({passUSD:parse(row.passUSD),failUSD:parse(row.failUSD)}))};
  }
  function syncFields(){
    host.querySelectorAll('[data-hedge-mode]').forEach(button=>button.setAttribute('aria-pressed',String(Number(button.dataset.hedgeMode)===mode)));
    host.querySelectorAll('[data-hedge-field]').forEach(node=>{if(!node.dataset.hedgeField.startsWith('costs.'))node.value=drafts[mode].fields[node.dataset.hedgeField];});
    const second=host.querySelector('[data-hedge-second-target]');second.hidden=mode!==2;second.querySelector('input').disabled=mode!==2;
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
    host.querySelector('#hedgePropFlow').innerHTML=model.stages.map((stage,i)=>'<div class="hp-stage"><span class="hp-stage-label">'+(i+1)+' · Avaliação '+(i+1)+'</span><dl><div><dt>Perda pessoal ao passar</dt><dd>'+money(stage.hedgeCapitalUSD)+'</dd></div><div><dt>Despesa acumulada após passar</dt><dd>'+money(stage.accumulatedLossUSD)+'</dd></div></dl><span class="hp-muted">O lucro da avaliação não foi recebido.</span></div>').join('')+'<div class="hp-stage hp-funded"><span class="hp-stage-label">'+(mode+1)+' · Fase financiada</span><dl><div><dt>Perda pessoal teórica no alvo</dt><dd>'+money(model.funded.hedgeLossUSD)+'</dd></div><div><dt>Reserva com 100% adicional</dt><dd>'+money(model.funded.reserveUSD)+'</dd></div></dl><span class="hp-muted">Recuperação condicionada ao recebimento.</span></div>';
    const title=outcome=>outcome.kind==='EVALUATION_FAIL'?'Reprovar na avaliação '+(outcome.stageIndex+1):outcome.kind==='FUNDED_FAIL'?'Perder a conta financiada':outcome.kind==='FUNDED_PASS'?'Atingir o alvo e receber payout/reembolso':'Atingir o alvo sem receber payout nem reembolso';
    const path=outcome=>outcome.kind==='EVALUATION_FAIL'?'failure-'+(outcome.stageIndex+1):outcome.kind==='FUNDED_FAIL'?'funded-stop':outcome.kind==='FUNDED_PASS'?'funded-success':'no-receipt';
    host.querySelector('#hedgePropOutcomes').innerHTML=model.outcomes.map(outcome=>'<div class="hp-outcome"><h5>'+title(outcome)+'</h5><dl><div><dt>Resultado ideal</dt><dd>'+money(outcome.idealNetUSD)+'</dd></div><div><dt>Custos deste caminho</dt><dd>'+(outcome.costStatus==='COMPLETE'?money(outcome.estimatedCostsUSD):outcome.costStatus==='INVALID'?'Revisar os custos':'Pendente')+'</dd></div><div><dt>Resultado após custos</dt><dd data-hedge-cost-path="'+path(outcome)+'"'+(outcome.costStatus==='COMPLETE'&&outcome.netAfterCostsUSD<=-.005?' class="hp-negative"':'')+'>'+(outcome.costStatus==='COMPLETE'?money(outcome.netAfterCostsUSD):outcome.costStatus==='INVALID'?'Custo inválido':'Pendente')+'</dd></div></dl></div>').join('');
    const stageDetails=model.stages.map((stage,i)=>'<div class="hp-math-stage"><h5>Avaliação '+(i+1)+'</h5><dl><div><dt>Meta da prop</dt><dd>'+money(stage.targetUSD)+'</dd></div><div><dt>Razão teórica de exposição</dt><dd>'+ratioFormat.format(stage.hedgeRatio)+'</dd></div></dl></div>').join('');
    host.querySelector('#hedgePropDetails').innerHTML='<p>Perda máxima fixa comum: '+money(model.drawdownUSD)+'. O capital nominal reinicia em cada etapa; as razões não são lotes executáveis.</p><div class="hp-math-stages">'+stageDetails+'<div class="hp-math-stage"><h5>Fase financiada</h5><dl><div><dt>Razão teórica de exposição</dt><dd>'+ratioFormat.format(model.funded.hedgeRatio)+'</dd></div><div><dt>Meta sobre o nominal</dt><dd>'+percentage.format(model.funded.targetPercent)+'%</dd></div></dl></div></div><p class="hp-formula">L₀ = taxa; qᵢ = Lᵢ₋₁ ÷ perda máxima; Hᵢ = qᵢ × meta; Lᵢ = Lᵢ₋₁ + Hᵢ. Na financiada: qf = Lₙ ÷ perda máxima; alvo = (Lₙ − reembolso) ÷ (payout − qf). Reserva financiada = 2 × qf × alvo.</p><p class="hp-muted">Percentuais entram como frações na fórmula. Precisão preservada no cálculo; valores exibidos são arredondados.</p>';
  }
  function onInput(event){
    const node=event.target.closest('[data-hedge-field]');if(!node||!active)return;
    const name=node.dataset.hedgeField;
    if(name.startsWith('costs.')){const [,i,key]=name.split('.');drafts[mode].costs[i][key]=node.value;}
    else{drafts[mode].fields[name]=node.value;drafts[mode].example=false;}
    update();
  }
  function onClick(event){
    if(!active)return;
    const button=event.target.closest('[data-hedge-mode],[data-hedge-action]');if(!button)return;
    if(button.dataset.hedgeMode){const next=Number(button.dataset.hedgeMode);if(next!==mode){mode=next;syncFields();}return;}
    const action=button.dataset.hedgeAction;
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
    host.innerHTML=markup();host.addEventListener('input',onInput);host.addEventListener('click',onClick);
    controller=Object.freeze({activate,deactivate,disposeForSession});syncFields();return controller;
  }
  function activate(){if(controller)active=true;}
  function deactivate(){active=false;}
  function disposeForSession(){
    active=false;drafts=fresh();mode=1;
    if(host){host.removeEventListener('input',onInput);host.removeEventListener('click',onClick);host.replaceChildren();}
    host=null;controller=null;
  }
  root.JPWPropFirms=Object.freeze({mount,activate,deactivate,disposeForSession});
}(window));

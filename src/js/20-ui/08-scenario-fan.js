// JPW Scenario Fan — presentation only. Prepared monthly values belong to the
// caller; this component never reads financial state, persists or forecasts.
// Contract, intended uses and lifecycle: docs/design/SCENARIO-FAN.md.
(function(global){
  'use strict';
  const instances=new WeakMap();
  let sequence=0;
  const validMonth=value=>typeof value==='string'&&/^\d{4}-(0[1-9]|1[0-2])$/.test(value);
  const text=value=>value==null?'':String(value);
  const escape=value=>text(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const monthLabel=value=>validMonth(value)?new Intl.DateTimeFormat('pt-BR',{month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(value+'-01T12:00:00Z')):text(value);
  const monthOrdinal=value=>Number(value.slice(0,4))*12+Number(value.slice(5,7));
  const finite=value=>typeof value==='number'&&Number.isFinite(value);
  const number=value=>Number(value.toFixed(3));
  const palettes={actual:{color:'var(--sf-history)',dash:'',label:'Realizado · linha contínua'},plan:{color:'var(--sf-plan)',dash:'2 4',label:'PLAN · linha pontilhada'},baseline:{color:'var(--ink-faint)',dash:'10 5',label:'Baseline · referência'},scenario:[{color:'var(--sf-scenario-one)',dash:'7 4',label:'Cenário · tracejado'},{color:'var(--sf-scenario-two)',dash:'10 3 2 3',label:'Cenário · traço e ponto'}]};
  const stateLabels={FINALIZED:'Finalizado',PROJECTED:'Projetado',FORECAST:'Projetado',NOT_APPLICABLE:'Fora desta camada',UNAVAILABLE:'Indisponível',ABSENT:'Previsão retirada',BLOCKED:'Base indisponível',REOPENED:'Reaberto',REVIEW_REQUIRED:'Base em revisão',UNKNOWN:'Gravação indeterminada',PREVIOUS:'Leitura anterior',REFERENCE:'Referência'};
  const stateLabel=value=>stateLabels[text(value)]||text(value);

  function prepared(model){
    const months=[...new Set((Array.isArray(model.months)?model.months:[]).filter(validMonth))].sort();
    let scenarioIndex=0;
    const series=(Array.isArray(model.series)?model.series:[]).filter(source=>source&&typeof source==='object').map((source,index)=>{
      const kind=['actual','plan','scenario','baseline'].includes(source.kind)?source.kind:'scenario';
      const style=kind==='scenario'?palettes.scenario[scenarioIndex++%2]:palettes[kind];
      const points=new Map();
      (Array.isArray(source.points)?source.points:[]).forEach(point=>{
        if(!point||!validMonth(point.month)) return;
        const duplicate=points.has(point.month);
        const available=!duplicate&&point.availability!==false&&point.availability!=='UNAVAILABLE'&&finite(point.value);
        points.set(point.month,{month:point.month,value:available?point.value:null,state:duplicate?'UNAVAILABLE':text(point.state),reason:duplicate?'Mais de uma observação informada para este mês.':text(point.reason),origin:text(point.origin)});
      });
      return {id:text(source.id||kind+'-'+index),name:text(source.name||kind),kind,style,points};
    });
    return {months,series};
  }

  // Geometry of the envelope only: include genuine intersections so an upper
  // edge never joins two unrelated endpoints above all selected trajectories.
  function envelopeInterval(left,right){
    const cuts=[0,1];
    for(let a=0;a<left.length;a++) for(let b=a+1;b<left.length;b++){
      const scale=Math.max(1,Math.abs(left[a]),Math.abs(left[b]),Math.abs(right[a]),Math.abs(right[b]));
      const delta0=left[a]/scale-left[b]/scale,delta1=right[a]/scale-right[b]/scale;
      if(delta0!==delta1){const crossing=delta0/(delta0-delta1);if(crossing>0&&crossing<1) cuts.push(crossing);}
    }
    const positions=[...new Set(cuts)].sort((a,b)=>a-b);
    return positions.map(t=>{const values=left.map((value,index)=>value*(1-t)+right[index]*t);return {t,low:Math.min(...values),high:Math.max(...values)};});
  }

  function destroy(container){
    const instance=container&&instances.get(container);
    if(!instance) return;
    instance.dispose();
    instances.delete(container);
  }

  function render(container,model,options){
    if(!container||typeof container.replaceChildren!=='function') return null;
    model=model&&typeof model==='object'?model:{};
    options=options&&typeof options==='object'?options:{};
    const previous=instances.get(container),identity=text(model.identity);
    const savedMonth=previous&&previous.identity===identity?previous.month:null;
    const focus=previous&&previous.root.contains(document.activeElement)?document.activeElement.dataset.sfFocus:null;
    const tableOpen=!!(previous&&previous.table.open),methodOpen=!!(previous&&previous.method.open),provenanceOpen=!!(previous&&previous.provenance.open);
    let inspected=!!(previous&&previous.identity===identity&&previous.inspected),emphasizedId=null;
    destroy(container);
    const data=prepared(model),months=data.months,series=data.series;
    const id='jpw-scenario-fan-'+(++sequence);
    const formatValue=value=>typeof options.formatValue==='function'?text(options.formatValue(value)):new Intl.NumberFormat('pt-BR',{maximumFractionDigits:2}).format(value)+' '+text(model.unit);
    const lastActual=[...months].reverse().find(m=>series.some(s=>s.kind==='actual'&&finite(s.points.get(m)?.value)));
    const initialMonth=lastActual||(months.includes(model.projectionStartMonth)?model.projectionStartMonth:null)||months[0]||null;
    let month=months.includes(savedMonth)?savedMonth:(months.includes(options.selectedMonth)?options.selectedMonth:initialMonth);
    const root=document.createElement('section');root.className='jpw-scenario-fan';root.dataset.sfIdentity=identity;
    const endpointFor=s=>{
      const point=s.kind==='actual'?[...months].reverse().map(m=>s.points.get(m)).find(p=>p&&finite(p.value)):s.points.get(months[months.length-1]);
      return {point,date:s.kind==='actual'?(point?point.month:null):months[months.length-1]};
    };
    const swatchClass=s=>s.kind==='scenario'?(s.style===palettes.scenario[0]?'scenario-one':'scenario-two'):s.kind;
    const planSeries=series.find(s=>s.kind==='plan'),actualSeries=series.find(s=>s.kind==='actual');
    const primarySeries=planSeries||actualSeries||series[0],primary=primarySeries?endpointFor(primarySeries):{};
    const actual=actualSeries?endpointFor(actualSeries):{};
    const labelSeries=series.filter(s=>s.kind!=='actual'||!planSeries);
    root.innerHTML=`<div class="sf-heading"><div class="sf-primary"><h4 id="${id}-title">${escape(model.title||'Trajetórias patrimoniais')}</h4><p class="sf-primary-caption">${escape(primarySeries?primarySeries.name:'Sem trajetória disponível')}${primary.date?' · '+escape(monthLabel(primary.date)):''}</p><strong class="sf-primary-value">${primary.point&&finite(primary.point.value)?escape(formatValue(primary.point.value)):'N/A'}</strong>${model.readingStatus==='PREVIOUS'?'<p class="sf-subtitle">Leitura anterior · atualização indeterminada</p>':''}</div><div class="sf-last-actual"><span class="sf-unit">${escape(model.unit||'Unidade não informada')}</span>${actualSeries&&planSeries?`<span>Último realizado${actual.date?' · '+escape(monthLabel(actual.date)):''}</span><strong>${actual.point&&finite(actual.point.value)?escape(formatValue(actual.point.value)):'N/A'}</strong>`:''}</div></div>
      <ul class="sf-legends" aria-label="Séries apresentadas">${series.map((s,index)=>`<li><button type="button" class="sf-legend-control" data-sf-emphasis="${index}" data-sf-focus="legend-${index}" aria-label="Destacar ${escape(s.name)} · ${escape(s.style.label)}"><span class="sf-swatch sf-swatch--${swatchClass(s)}" aria-hidden="true"></span><span>${escape(s.name)}</span></button></li>`).join('')}</ul>
      <div class="sf-stage"><div class="sf-plot"></div><div class="sf-endpoints" aria-label="Realizado disponível e horizonte projetado">${labelSeries.map(s=>{
        const {point,date}=endpointFor(s),index=series.indexOf(s);
        const endpointValue=point&&finite(point.value)?formatValue(point.value):'N/A';
        const endpointState=point&&point.state?stateLabel(point.state):point&&finite(point.value)?'Estado não informado':'Indisponível';
        const endpointLabel=[s.name,endpointValue,date?monthLabel(date):'Sem mês disponível',endpointState].join(' · ');
        return `<button type="button" class="sf-endpoint sf-endpoint--${swatchClass(s)}" data-sf-endpoint-index="${index}" data-sf-emphasis="${index}" data-sf-focus="endpoint-${index}" aria-label="Consultar ${escape(endpointLabel)}"><span class="sf-swatch sf-swatch--${swatchClass(s)}" aria-hidden="true"></span><span class="sf-endpoint-content"><span class="sf-endpoint-name">${escape(s.name)}</span><strong>${point&&finite(point.value)?escape(formatValue(point.value)):'N/A'}</strong><small>${date?escape(monthLabel(date)):'Sem mês disponível'}${point&&point.state?' · '+escape(stateLabel(point.state)):''}</small></span></button>`;
      }).join('')}</div></div>
      <p class="sf-band-note">${series.filter(s=>s.kind==='plan'||s.kind==='scenario').length>=2?'Faixa entre hipóteses selecionadas · não é probabilidade.':(series.some(s=>s.kind==='plan')?'PLAN sozinho · selecione cenários para comparar hipóteses.':'Sem faixa entre hipóteses nesta janela.')}</p>
      <div class="sf-inspector"><label for="${id}-month">Consultar mês<select id="${id}-month" data-sf-focus="month" aria-label="Mês da consulta">${months.map(m=>`<option value="${m}">${escape(monthLabel(m))}</option>`).join('')}</select></label><div class="sf-reading" data-fan-reading role="status" aria-live="polite" aria-atomic="true"></div></div>
      <div class="sf-secondary"><details class="sf-inspection-detail"><summary data-sf-focus="provenance">Motivos e origens deste mês</summary><div class="sf-reading-provenance"></div></details>
      <details class="sf-table-detail"><summary data-sf-focus="table">Ver dados mensais</summary><div class="sf-table-scroll" tabindex="0" aria-label="Tabela das trajetórias mensais"><table class="sf-data-table"><caption>Mesmos valores e lacunas do gráfico · ${escape(model.unit)}</caption><thead><tr><th scope="col">Mês</th>${series.map(s=>`<th scope="col">${escape(s.name)}</th>`).join('')}</tr></thead><tbody>${months.map(m=>`<tr><th scope="row">${escape(monthLabel(m))}</th>${series.map(s=>{const p=s.points.get(m);return `<td><span class="sf-table-value">${p&&finite(p.value)?escape(formatValue(p.value)):'N/A'}</span>${p&&(p.state||p.reason||p.origin)?`<small>${escape([stateLabel(p.state),p.reason,p.origin].filter(Boolean).join(' · '))}</small>`:''}</td>`;}).join('')}</tr>`).join('')}</tbody></table></div></details>
      <details class="sf-method"><summary data-sf-focus="method">Origem e interpretação</summary>${model.summary?`<p class="sf-summary">${escape(model.summary)}</p>`:''}<p>O desenho conecta apenas meses consecutivos calculáveis. PLAN e cenários são hipóteses condicionais; não preveem rentabilidade. Depósitos podem alterar o patrimônio. A baseline é uma referência separada e não compõe a faixa.</p><p>Selecione um mês, use as setas no gráfico ou toque na trajetória. A leitura é do mês escolhido; lacunas permanecem indisponíveis. Não se reutiliza o valor de outro mês. As cores distinguem séries; não indicam autorização ou nível de risco.</p><p>${escape(model.origin||'Origem não informada pelo produtor.')} · Revisão ${escape(model.revision||'não informada')}</p></details></div>`;
    container.replaceChildren(root);
    const plot=root.querySelector('.sf-plot'),select=root.querySelector('select'),reading=root.querySelector('.sf-reading');
    const table=root.querySelector('.sf-table-detail'),method=root.querySelector('.sf-method'),provenance=root.querySelector('.sf-inspection-detail');table.open=tableOpen;method.open=methodOpen;provenance.open=provenanceOpen;
    select.disabled=!months.length;select.value=month||'';
    let svg=null,geometry=null,observer=null,fontObserver=null,lastWidth=0,lastFontScale=0,disposed=false;
    const handlers=[];
    const on=(target,event,listener)=>{target.addEventListener(event,listener);handlers.push(()=>target.removeEventListener(event,listener));};
    const markOverflowValues=()=>root.querySelectorAll('.sf-primary-value,.sf-last-actual strong,.sf-endpoint strong,.sf-reading-values strong').forEach(value=>{
      const overflow=value.scrollWidth>value.clientWidth+1;
      const endpoint=value.closest('.sf-endpoint');
      if(overflow){
        if(endpoint){endpoint.title='Com o botão focado, use as setas esquerda/direita para rolar o valor; Home/End mostram início/fim. Enter/Espaço consultam o mês.';value.title=endpoint.title;}
        else{value.tabIndex=0;value.title='Valor completo; use as setas para rolar horizontalmente.';}
      }else{value.removeAttribute('tabindex');value.removeAttribute('title');if(endpoint) endpoint.removeAttribute('title');}
    });
    const inspectPayload=()=>({identity,revision:model.revision,month,unit:text(model.unit),series:series.map(s=>{const p=s.points.get(month);return {id:s.id,name:s.name,kind:s.kind,value:p&&finite(p.value)?p.value:null,state:p?text(p.state):'UNAVAILABLE',reason:p?text(p.reason):'Sem observação para este mês.',origin:p?text(p.origin):''};})});
    const updateReading=notify=>{
      const payload=inspectPayload();root.dataset.sfSelectedMonth=month||'';
      select.value=month||'';
      reading.innerHTML=month?`<strong class="sf-reading-month">${escape(monthLabel(month))}</strong><div class="sf-reading-values">${payload.series.map(s=>`<div><span>${escape(s.name)}</span><strong>${finite(s.value)?escape(formatValue(s.value)):'N/A'}</strong><small class="sf-reading-state">${escape(stateLabel(s.state)||(!finite(s.value)?'Indisponível':'Estado não informado'))}</small></div>`).join('')}</div>`:'<p>Sem meses disponíveis nesta consulta.</p>';
      root.querySelector('.sf-reading-provenance').innerHTML=payload.series.map(s=>`<p><strong>${escape(s.name)}</strong> · ${escape([stateLabel(s.state),s.reason,s.origin].filter(Boolean).join(' · ')||'Origem ou estado não informados.')}</p>`).join('');
      markOverflowValues();
      if(svg&&geometry){
        const cursor=svg.querySelector('.sf-cursor');const index=months.indexOf(month);
        cursor.setAttribute('transform',`translate(${number(geometry.X(Math.max(0,index)))} 0)`);cursor.style.display=inspected&&index>=0?'':'none';
        series.forEach((s,index)=>{const dot=svg.querySelector(`[data-sf-dot="${index}"]`),p=s.points.get(month);if(dot){dot.style.display=p&&finite(p.value)?'':'none';if(p&&finite(p.value)) dot.setAttribute('cy',number(geometry.Y(p.value)));}});
      }
      if(notify&&typeof options.onInspect==='function') options.onInspect(payload);
    };
    const pick=selected=>{if(!months.includes(selected)) return;const changed=selected!==month;inspected=true;instance.inspected=true;month=selected;instance.month=month;updateReading(changed);};
    const emphasize=index=>{
      emphasizedId=Number.isInteger(index)&&series[index]?series[index].id:null;
      root.querySelectorAll('[data-fan-series]').forEach(path=>{path.style.opacity=emphasizedId&&path.getAttribute('data-fan-series')!==emphasizedId?'.2':'1';});
      root.querySelectorAll('[data-sf-emphasis]').forEach(control=>control.classList.toggle('sf-emphasized',Number(control.dataset.sfEmphasis)===index));
      root.querySelectorAll('[data-fan-band]').forEach(band=>band.style.opacity=emphasizedId?'.45':'1');
    };
    const pointer=e=>{
      if(!svg||!geometry||!months.length) return;
      if(e.type==='pointermove'&&e.pointerType!=='mouse'&&e.pointerType!=='pen') return;
      const bounds=svg.getBoundingClientRect(),x=(e.clientX-bounds.left)*geometry.width/(bounds.width||1);
      if(x<geometry.left||x>geometry.width-geometry.right) return;
      const index=months.length>1?Math.max(0,Math.min(months.length-1,Math.round((x-geometry.left)/(geometry.width-geometry.left-geometry.right)*(months.length-1)))):0;
      pick(months[index]);
    };
    const key=e=>{
      if(!months.length||!['ArrowLeft','ArrowRight','Home','End'].includes(e.key)) return;
      e.preventDefault();const index=Math.max(0,months.indexOf(month));
      pick(months[e.key==='Home'?0:e.key==='End'?months.length-1:Math.max(0,Math.min(months.length-1,index+(e.key==='ArrowRight'?1:-1)))]);
    };
    const draw=()=>{
      if(disposed) return;
      const width=Math.round(plot.clientWidth);if(width<1) return;
      const restoreFocus=svg&&document.activeElement===svg;
      const fontScale=parseFloat(getComputedStyle(root).getPropertyValue('--fs-scale'))||1;
      const compact=width<480,height=compact?240:320,left=Math.min(78*fontScale,width*.28),top=20,bottom=34;
      const stage=root.querySelector('.sf-stage'),rail=root.querySelector('.sf-endpoints');
      let inline=width>=640*fontScale,railWidth=Math.min(240*fontScale,width*.28);
      stage.dataset.sfLayout=inline?'inline':'stacked';
      rail.style.width=inline?(railWidth-22)+'px':'';
      if(inline&&[...rail.children].reduce((sum,label)=>sum+label.offsetHeight+10,0)-10>height-16){inline=false;stage.dataset.sfLayout='stacked';rail.style.width='';}
      const right=inline?railWidth:16;
      lastWidth=width;
      lastFontScale=fontScale;
      const allValues=series.flatMap(s=>months.map(m=>s.points.get(m)).filter(p=>p&&finite(p.value)).map(p=>p.value));
      if(!allValues.length||!months.length){stage.dataset.sfLayout='stacked';rail.style.left='';rail.style.width='';rail.style.height='';plot.innerHTML='<div class="sf-empty"><strong>Trajetória indisponível</strong><p>Não há valores calculáveis nesta janela. Consulte os motivos nos dados mensais.</p></div>';svg=null;geometry=null;updateReading(false);return;}
      const low=Math.min(...allValues),high=Math.max(...allValues),scale=Math.max(1,Math.abs(low),Math.abs(high));
      let minimum=low/scale,maximum=high/scale;
      const padding=(maximum-minimum)*.1||Math.max(1/scale,Math.abs(maximum)*.03);minimum-=padding;maximum+=padding;
      const X=index=>left+(months.length>1?index/(months.length-1):.5)*(width-left-right);
      const Y=value=>top+(1-(value/scale-minimum)/(maximum-minimum))*(height-top-bottom);
      geometry={X,Y,width,left,right};
      const path=points=>points.map((p,index)=>(index?'L':'M')+number(X(p.index))+' '+number(Y(p.value))).join(' ');
      const segments=s=>{const list=[];let current=[];months.forEach((m,index)=>{const p=s.points.get(m);if(current.length&&monthOrdinal(m)-monthOrdinal(months[index-1])!==1){list.push(current);current=[];}if(p&&finite(p.value)){current.push({index,value:p.value});}else if(current.length){list.push(current);current=[];}});if(current.length) list.push(current);return list;};
      const future=series.filter(s=>s.kind==='plan'||s.kind==='scenario'),projectionIndex=months.indexOf(model.projectionStartMonth);
      let bands='';
      if(future.length>=2&&projectionIndex>=0) for(let index=projectionIndex;index<months.length-1;index++){
        if(monthOrdinal(months[index+1])-monthOrdinal(months[index])!==1) continue;
        const a=future.map(s=>s.points.get(months[index])),b=future.map(s=>s.points.get(months[index+1]));
        if(!a.every(p=>p&&finite(p.value))||!b.every(p=>p&&finite(p.value))) continue;
        const envelope=envelopeInterval(a.map(p=>p.value),b.map(p=>p.value));
        const points=envelope.map(p=>`${number(X(index+p.t))},${number(Y(p.high))}`).concat([...envelope].reverse().map(p=>`${number(X(index+p.t))},${number(Y(p.low))}`)).join(' ');
        bands+=`<polygon class="sf-band" data-fan-band data-sf-band-month="${months[index]}" points="${points}"/>`;
      }
      const normalTicks=typeof CH!=='undefined'&&typeof CH.ticks==='function'?CH.ticks(low/scale,high/scale,compact?3:4):Array.from({length:5},(_,i)=>low/scale+(high/scale-low/scale)*i/4);
      const ticks=low===high?[low]:normalTicks.map(value=>value*scale).filter(finite);
      const grid=ticks.map(v=>`<line x1="${left}" x2="${width-right}" y1="${number(Y(v))}" y2="${number(Y(v))}" class="sf-grid"/>`).join('');
      const markers=projectionIndex>=0?`<line x1="${number(X(projectionIndex))}" x2="${number(X(projectionIndex))}" y1="${top}" y2="${height-bottom}" class="sf-projection-marker"/>`:'';
      const curves=[...series.filter(s=>s.kind!=='actual'),...series.filter(s=>s.kind==='actual')].map(s=>segments(s).map(segment=>segment.length===1?`<circle data-fan-series="${escape(s.id)}" cx="${number(X(segment[0].index))}" cy="${number(Y(segment[0].value))}" r="3" fill="${s.style.color}"/>`:`<path data-fan-series="${escape(s.id)}" d="${path(segment)}" stroke="${s.style.color}" ${s.style.dash?`stroke-dasharray="${s.style.dash}"`:''} class="sf-line"/>`).join('')).join('');
      const xCount=Math.max(2,Math.min(compact?3:6,Math.floor((width-left-right)/((compact?60:110)*fontScale))));
      const xIndices=[...new Set([0,...Array.from({length:xCount},(_,i)=>Math.round(i*(months.length-1)/Math.max(1,xCount-1))),months.length-1])];
      const xLabels=xIndices.map(index=>`<text x="${number(X(index))}" y="${height-8}" text-anchor="${months.length===1?'middle':index===0?'start':index===months.length-1?'end':'middle'}" class="sf-axis-label">${escape(compact?months[index].slice(5)+'/'+months[index].slice(2,4):monthLabel(months[index]))}</text>`).join('');
      // Labels remain HTML at native CSS sizes. Projection/inspection is not
      // shifted to imitate the reference: every X still belongs to its month.
      const axisFormat=value=>{
        const scientific=Math.abs(value)>=1e9||(value!==0&&Math.abs(value)<.01);
        return (scientific?'≈ ':'')+new Intl.NumberFormat('pt-BR',scientific?{notation:'scientific',maximumSignificantDigits:3}:{maximumFractionDigits:2}).format(value);
      };
      const visibleTicks=ticks.filter(value=>Y(value)>=top-1&&Y(value)<=height-bottom+1);
      const scaleLabels=visibleTicks.map(v=>`<span style="top:${number(Y(v))}px;width:${number(left-12)}px">${escape(axisFormat(v))}</span>`).join('');
      const endpointMarks=labelSeries.map(s=>{const {point,date}=endpointFor(s);return point&&finite(point.value)&&months.includes(date)?`<circle class="sf-endpoint-dot" cx="${number(X(months.indexOf(date)))}" cy="${number(Y(point.value))}" r="4" stroke="${s.style.color}"/>`:'';}).join('');
      plot.innerHTML=`<div class="sf-axis-values" aria-hidden="true">${scaleLabels}</div><svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" tabindex="0" data-sf-focus="plot" aria-labelledby="${id}-title" aria-describedby="${id}-plot-description" aria-keyshortcuts="ArrowLeft ArrowRight Home End">${grid}${bands}${markers}${curves}${endpointMarks}<g class="sf-endpoint-leaders"></g>${xLabels}<g class="sf-cursor" pointer-events="none"><line y1="${top}" y2="${height-bottom}" class="sf-cursor-line"/>${series.map((s,index)=>`<circle data-sf-dot="${index}" r="4" fill="${s.style.color}" class="sf-cursor-dot"/>`).join('')}</g></svg><p id="${id}-plot-description" class="sf-chart-description">${projectionIndex>=0?'Projeção a partir de '+escape(monthLabel(months[projectionIndex]))+'.':'Fronteira da projeção indisponível nesta janela.'} ${bands?'Faixa entre hipóteses selecionadas.':'Sem faixa calculável entre hipóteses nesta janela.'} As setas percorrem os meses; os valores completos estão na consulta e na tabela.</p>`;
      const endpointRoot=root.querySelector('.sf-endpoints');
      endpointRoot.style.left=inline?(width-right+22)+'px':'';endpointRoot.style.width=inline?(right-22)+'px':'';endpointRoot.style.height=inline?height+'px':'';
      let leaders='';
      const labels=labelSeries.map(s=>{const element=root.querySelector(`[data-sf-endpoint-index="${series.indexOf(s)}"]`),last=endpointFor(s);return {s,element,...last,height:element.offsetHeight,target:last.point&&finite(last.point.value)?Y(last.point.value):height-bottom};});
      const required=labels.reduce((sum,label)=>sum+label.height+10,0)-10;
      // Many/long labels, larger type, or a narrow plot use complete values
      // beneath the graph rather than hiding them or forcing overlap.
      if(inline&&required<=height-16){
        labels.sort((a,b)=>a.target-b.target);
        let end=8;labels.forEach(label=>{label.top=Math.max(end,label.target-label.height/2);end=label.top+label.height+10;});
        const overshoot=Math.max(0,end-10-(height-8));if(overshoot) labels.forEach(label=>label.top-=overshoot);
        let begin=8;labels.forEach(label=>{label.top=Math.max(begin,label.top);begin=label.top+label.height+10;label.element.style.top=number(label.top)+'px';});
        labels.forEach(label=>{if(label.point&&finite(label.point.value)&&months.includes(label.date)){
          const sourceX=X(months.indexOf(label.date)),sourceY=Y(label.point.value),targetY=label.top+label.height/2;
          leaders+=`<path class="sf-endpoint-leader" d="M${number(sourceX+5)} ${number(sourceY)} L${number(width-right+12)} ${number(targetY)} L${number(width-right+19)} ${number(targetY)}" stroke="${label.s.style.color}"/>`;
        }});
      }else{
        root.querySelector('.sf-stage').dataset.sfLayout='stacked';endpointRoot.style.left='';endpointRoot.style.width='';endpointRoot.style.height='';labels.forEach(label=>label.element.style.top='');
      }
      plot.querySelector('.sf-endpoint-leaders').innerHTML=leaders;
      root.querySelector('.sf-band-note').textContent=bands?'Faixa entre hipóteses selecionadas · não é probabilidade.':future.length>=2?'Sem faixa calculável nesta janela · consulte as lacunas.':future.some(s=>s.kind==='plan')?'PLAN sozinho · selecione cenários para comparar hipóteses.':'Sem faixa entre hipóteses nesta janela.';
      svg=plot.querySelector('svg');
      updateReading(false);if(emphasizedId) emphasize(series.findIndex(s=>s.id===emphasizedId));if(restoreFocus) svg.focus({preventScroll:true});
    };
    const instance={root,table,method,provenance,identity,month,inspected,dispose(){disposed=true;handlers.forEach(remove=>remove());if(observer) observer.disconnect();if(fontObserver) fontObserver.disconnect();}};
    instances.set(container,instance);
    on(select,'change',()=>pick(select.value));on(plot,'pointermove',pointer);on(plot,'pointerup',pointer);on(plot,'keydown',key);
    on(root,'pointerover',e=>{const control=e.target.closest('[data-sf-emphasis]');if(control&&root.contains(control)) emphasize(Number(control.dataset.sfEmphasis));});
    on(root,'pointerout',e=>{if(e.target.closest('[data-sf-emphasis]')&&!e.relatedTarget?.closest('[data-sf-emphasis]')) emphasize(null);});
    on(root,'focusin',e=>{const control=e.target.closest('[data-sf-emphasis]');if(control) emphasize(Number(control.dataset.sfEmphasis));});
    on(root,'focusout',e=>{if(!e.relatedTarget?.closest('[data-sf-emphasis]')) emphasize(null);});
    on(root,'click',e=>{const control=e.target.closest('[data-sf-endpoint-index]');if(control){const s=series[Number(control.dataset.sfEndpointIndex)];if(s) pick(endpointFor(s).date);}});
    on(root,'keydown',e=>{
      const endpoint=e.target.closest('.sf-endpoint');
      if(!endpoint||!['ArrowLeft','ArrowRight','Home','End'].includes(e.key)) return;
      const value=endpoint.querySelector('strong'),maximum=value?value.scrollWidth-value.clientWidth:0;
      if(maximum<=1) return;
      e.preventDefault();e.stopPropagation();
      const step=Math.max(32,Math.round(value.clientWidth*.75));
      value.scrollLeft=e.key==='Home'?0:e.key==='End'?maximum:Math.max(0,Math.min(maximum,value.scrollLeft+(e.key==='ArrowRight'?step:-step)));
    });
    draw();updateReading(false);
    if(typeof ResizeObserver==='function'){
      observer=new ResizeObserver(()=>{if(Math.round(plot.clientWidth)!==lastWidth||(parseFloat(getComputedStyle(root).getPropertyValue('--fs-scale'))||1)!==lastFontScale) draw();});observer.observe(plot);
    }else on(global,'resize',draw);
    // Font preference can change label heights while the measured plot keeps
    // exactly the same dimensions. Observe only root font inputs, and redraw
    // only when their computed scale actually differs. Interaction/child DOM
    // changes are outside this observer, so drawing cannot feed back into it.
    if(typeof MutationObserver==='function'){
      fontObserver=new MutationObserver(()=>{
        if(!disposed&&(parseFloat(getComputedStyle(root).getPropertyValue('--fs-scale'))||1)!==lastFontScale) draw();
      });
      fontObserver.observe(document.documentElement,{attributes:true,attributeFilter:['data-fs','style']});
    }
    if(focus){const target=root.querySelector(`[data-sf-focus="${focus}"]`);if(target) target.focus({preventScroll:true});}
    return {destroy(){if(instances.get(container)===instance) destroy(container);}};
  }
  global.JPWScenarioFan=Object.freeze({render,destroy});
})(window);

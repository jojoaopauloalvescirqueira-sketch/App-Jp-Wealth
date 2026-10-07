// Consolidado FX: presentation-only selection, descriptive projections and explicit imports.
(function(FX){
  'use strict';
  const available=()=>!window.JPWModuleAvailability||window.JPWModuleAvailability.canAccess('forex');
  const ui={accountId:null,source:'mt5',tab:'account',chart:'growth',from:'',to:'',search:'',preset:'all',monthlyMode:null,cashflows:false,sort:'result',historyFilter:null,monthMessage:'',preview:null,document:null,busy:false,token:0,message:'',kind:'info',mounted:false};
  const tabs=[['account','Painel'],['history','Movimentos'],['statistics','Estatísticas'],['risks','Risco']];
  let currentModel=null,fullModel=null,presentationContext=null;
  const el=id=>document.getElementById(id);
  const safe=value=>String(value==null?'':value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number=(value,unit='')=>typeof value==='number'&&Number.isFinite(value)?value.toLocaleString('pt-BR',{maximumFractionDigits:2,minimumFractionDigits:unit==='%'?2:0})+(unit?' '+unit:''):'—';
  // Format the declared calendar fields; never infer or convert a missing timezone.
  function declaredDate(value,dateOnly=false){
    const text=String(value||''),match=text.match(/^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}:\d{2})(:\d{2})?(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?$/);
    if(!match||!chartTime(text))return text;
    return `${match[3]}/${match[2]}/${match[1]}${!dateOnly&&match[4]?', '+match[4]+(match[5]||'')+(match[6]||'')+(match[7]?(match[7]==='Z'?' UTC':' UTC'+match[7]):' · fuso não informado'):''}`;
  }
  const aliases={trades:'tradeCount',growth:'growthPct',maxDrawdown:'drawdownAmount',maxDrawdownPct:'drawdownPct',activity:'tradingActivityPct',maxLoad:'maxDepositLoadPct'};
  const metric=(model,key)=>model.metrics?.[aliases[key]||key]||{value:null,availability:'unavailable',reason:'Os dados necessários não estão disponíveis.'};
  function label(model,key,title,unit){
    const m=metric(model,key),state=m.availability||'unavailable';if(state==='imported'&&['maxDrawdown','maxDrawdownPct'].includes(key))title='Rebaixamento informado · base do relatório';
    const displayUnit=unit||({count:'',ratio:'x'}[m.unit]??m.unit)||'';
    return `<div class="fxc-metric"><dt>${safe(title)}</dt><dd class="${typeof m.value==='number'&&m.value<0?'fxc-negative':''}">${m.value==null?'Indisponível':safe(number(m.value,displayUnit))}${state==='imported'?`<small>informado no relatório · ${safe(declaredDate(m.period?.from)||'início não informado')} → ${safe(declaredDate(m.period?.to)||'fim não informado')}</small>`:''}${m.reason?`<small>${safe(m.reason)}</small>`:''}</dd></div>`;
  }
  function unavailable(title,reason){return `<div class="fxc-unavailable"><strong>${safe(title)}</strong><p>${safe(reason)}</p></div>`;}
  // Presentation only: preserve source order, timestamps and missing values.
  // Calendar arithmetic is deterministic; bare server times are never converted
  // to this device's timezone or presented as UTC observations.
  function chartTime(value){
    const m=String(value||'').match(/^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(\.\d{1,3})?)?)?(Z|[+-]\d{2}:\d{2})?$/);
    if(!m||(!m[4]&&m[8]))return null;
    const y=+m[1],month=+m[2],day=+m[3],hour=+(m[4]||0),minute=+(m[5]||0),second=+(m[6]||0);
    if(y<1000||month<1||month>12||day<1||hour>23||minute>59||second>59)return null;
    const probe=new Date(Date.UTC(y,month-1,day,hour,minute,second,+(m[7]||'').slice(1).padEnd(3,'0')));
    if(probe.getUTCFullYear()!==y||probe.getUTCMonth()!==month-1||probe.getUTCDate()!==day)return null;
    let time=probe.getTime();
    if(m[8]&&m[8]!=='Z'){
      const h=+m[8].slice(1,3),min=+m[8].slice(4);
      if(h>14||min>59||(h===14&&min!==0))return null;
      time-=(m[8][0]==='+'?1:-1)*(h*60+min)*60000;
    }
    return {time,kind:m[8]?'absolute':m[4]?'server':'date'};
  }
  function chartSeries(input){
    const points=(Array.isArray(input)?input:[]).map((raw,index)=>{
      const p=raw&&typeof raw==='object'?raw:{};
      const date=String(p.date||p.time||p.at||'Referência não informada');
      const value=Object.prototype.hasOwnProperty.call(p,'value')?p.value:Object.prototype.hasOwnProperty.call(p,'balance')?p.balance:p.growth;
      const parsed=chartTime(date);
      return {index,date,value:typeof value==='number'&&Number.isFinite(value)?value:null,time:parsed?.time??null,kind:parsed?.kind||null,reason:String(p.reason||'Valor não informado.'),ticket:p.ticket==null?null:String(p.ticket)};
    });
    const temporal=points.length>0&&points.every((p,i)=>p.time!==null&&p.kind===points[0].kind&&(!i||p.time>=points[i-1].time));
    const validCount=points.filter(p=>p.value!==null).length;
    return {points,axisMode:temporal?'time':'sequence',timeKind:temporal?points[0].kind:'sequence',coincidentTimes:temporal&&points.some((p,i)=>i>0&&p.time===points[i-1].time),validCount,gapCount:points.length-validCount};
  }
  function chartGeometry(series,width=880,height=320,domain=null,invertY=false){
    const w=Math.max(1,Number(width)||880),h=Math.max(1,Number(height)||320),pad=Math.min(12,w/4,h/4);
    const valid=series.points.filter(p=>p.value!==null);
    if(!valid.length)return {width:w,height:h,coords:[],positions:[],segments:[],ticks:[]};
    const observedMin=valid.reduce((n,p)=>Math.min(n,p.value),Infinity),min=invertY?Math.min(0,observedMin):observedMin,max=valid.reduce((n,p)=>Math.max(n,p.value),-Infinity);
    // Normalize only drawing coordinates, including very large signed values.
    const scale=Math.max(1,Math.abs(min),Math.abs(max)),low=min/scale,high=max/scale;
    const spread=high-low||Math.max(Math.abs(high)*.05,1/scale),lo=high===low?(invertY?low:low-spread/2):low;
    const first=series.points[0],last=series.points.at(-1),start=domain&&series.axisMode==='time'?domain[0]:first.time,end=domain&&series.axisMode==='time'?domain[1]:last.time;
    const x=p=>series.axisMode==='time'?(end===start?w/2:pad+(p.time-start)/(end-start)*(w-pad*2)):(series.points.length===1?w/2:pad+p.index/(series.points.length-1)*(w-pad*2));
    const y=v=>invertY?pad+(v/scale-lo)*(h-pad*2)/spread:h-pad-(v/scale-lo)*(h-pad*2)/spread;
    const coords=[],segments=[];let run=[];
    const flush=()=>{if(run.length){segments.push({indices:run.map(p=>p.index),path:run.map((p,i)=>(i?'L':'M')+p.x.toFixed(3)+' '+p.y.toFixed(3)).join(' ')});run=[];}};
    series.points.forEach(p=>{if(p.value===null){flush();return;}const point={index:p.index,x:x(p),y:y(p.value),value:p.value};coords.push(point);run.push(point);});flush();
    return {width:w,height:h,coords,positions:series.points.map(p=>({index:p.index,x:x(p)})),segments,ticks:Array.from({length:5},(_,i)=>({value:(lo+spread*(1-i/4))*scale,y:invertY?h-pad-i*(h-pad*2)/4:pad+i*(h-pad*2)/4}))};
  }
  const exactValue=(value,unit='')=>value===null?'Indisponível':String(value)+(unit?' '+unit:'');
  const axisDescription=series=>series.axisMode==='sequence'?'Sequência de observações · datas ausentes, ambíguas, de tipos diferentes ou fora de ordem; intervalos iguais não representam duração.':(series.timeKind==='server'?'Tempo proporcional · horário declarado no relatório; fuso não convertido.':'Tempo proporcional · datas e instantes declarados preservados.')+(series.coincidentTimes?' Instantes coincidentes compartilham posição; consulte cada observação pelos controles.':'');
  function chart(input,title,color='blue',unit='',key='main',provenance='',shared={}){
    const series=chartSeries(input);
    if(!series.validCount)return `<p class="fxc-empty-series" data-fxc-empty-series="${safe(key)}"><strong>${safe(title)}:</strong> indisponível; falta uma série histórica nesta seleção.</p>`;
    const id='fxcCurve-'+key,selected=series.points.findIndex(p=>p.value!==null);
    return `<figure class="fxc-chart" data-fxc-series="${safe(key)}" data-axis-mode="${series.axisMode}" data-time-kind="${series.timeKind}" data-point-count="${series.points.length}" data-gap-count="${series.gapCount}" data-fxc-points="${safe(JSON.stringify(series.points))}" data-axis-domain="${safe(JSON.stringify(shared.domain||null))}" data-fxc-markers="${safe(JSON.stringify(shared.markers||[]))}" data-sync-group="${safe(shared.group||'')}" data-unit="${safe(unit)}" data-color="${safe(color)}"><figcaption id="${id}-title">${safe(title)}</figcaption>${provenance?`<p class="fxc-chart-provenance">${safe(provenance)}</p>`:''}${shared.group?'':`<p class="fxc-chart-axis-note">${safe(axisDescription(series))}${series.gapCount?' · '+series.gapCount+' observação(ões) sem valor; curva interrompida.':''}${series.validCount===1?' · Uma observação; não há trajetória entre pontos.':''}</p>`}<div class="fxc-chart-frame"><div class="fxc-chart-axis" aria-hidden="true"></div><div class="fxc-chart-plot" role="img" aria-labelledby="${id}-title" aria-describedby="${id}-value"></div></div><div class="fxc-chart-dates"><span>${safe(declaredDate(series.points[0].date))}</span><span>${safe(declaredDate(series.points.at(-1).date))}</span></div><div class="fxc-chart-reader"><button type="button" class="fxc-chart-prev" aria-label="Observação anterior: ${safe(title)}">Anterior</button><label for="${id}-cursor">Observação<input id="${id}-cursor" class="fxc-chart-cursor" type="range" min="0" max="${series.points.length-1}" step="1" value="${selected}" aria-label="Observação do gráfico: ${safe(title)}" ${series.points.length===1?'disabled':''}></label><button type="button" class="fxc-chart-next" aria-label="Próxima observação: ${safe(title)}">Próxima</button></div><output id="${id}-value" class="fxc-chart-value" aria-live="polite"></output><details class="fxc-chart-values" data-fxc-disclosure="chart-${safe(key)}-values"><summary>Ver valores do gráfico</summary><div class="fxc-scroll"><table><caption>${safe(title)} · valores das observações, sem arredondamento</caption><thead><tr><th scope="col">Observação</th><th scope="col">Data / referência original</th><th scope="col">Valor</th></tr></thead><tbody>${series.points.map(p=>`<tr data-fxc-value-row="${p.index}"><th scope="row">${p.index+1}</th><td>${safe(p.date)}</td><td data-value="${p.value===null?'':safe(String(p.value))}">${safe(exactValue(p.value,unit))}${p.value===null?' · '+safe(p.reason):''}</td></tr>`).join('')}</tbody></table></div></details></figure>`;
  }
  let chartObserver=null;
  function bindCharts(){
    chartObserver?.disconnect();
    chartObserver=typeof ResizeObserver==='function'?new ResizeObserver(entries=>entries.forEach(entry=>entry.target._fxcDraw?.())):null;
    const readers=[];
    document.querySelectorAll('#fxconsolidated figure[data-fxc-series]').forEach(figure=>{
      const series=chartSeries(JSON.parse(figure.dataset.fxcPoints)),plot=figure.querySelector('.fxc-chart-plot'),axis=figure.querySelector('.fxc-chart-axis'),cursor=figure.querySelector('.fxc-chart-cursor'),output=figure.querySelector('output'),prev=figure.querySelector('.fxc-chart-prev'),next=figure.querySelector('.fxc-chart-next');
      const domain=JSON.parse(figure.dataset.axisDomain||'null'),markers=JSON.parse(figure.dataset.fxcMarkers||'[]');
      let geometry=null;
      const reader={figure,series,select:null};readers.push(reader);
      const select=(index,synchronize=true)=>{
        const i=Math.max(0,Math.min(series.points.length-1,Math.round(index))),p=series.points[i];cursor.value=String(i);figure.dataset.selectedPoint=String(i);figure.dataset.selectedTicket=p.ticket||'';
        const text=`Observação ${i+1} de ${series.points.length} · ${declaredDate(p.date)} · ${exactValue(p.value,figure.dataset.unit)}${p.value===null?' · '+p.reason:''}`;
        output.textContent=text;cursor.setAttribute('aria-valuetext',text);prev.disabled=i===0;next.disabled=i===series.points.length-1;
        plot.querySelectorAll('[data-fxc-point]').forEach(node=>node.classList.toggle('fxc-point-selected',Number(node.dataset.fxcPoint)===i));
        const guide=plot.querySelector('.fxc-guide'),position=geometry?.positions[i];if(guide&&position){guide.setAttribute('x1',position.x);guide.setAttribute('x2',position.x);}
        if(synchronize&&figure.dataset.syncGroup)readers.filter(other=>other!==reader&&other.figure.dataset.syncGroup===figure.dataset.syncGroup).forEach(other=>{
          const match=other.series.points.findIndex(q=>q.date===p.date&&(p.ticket!==null?q.ticket===p.ticket:q.index===p.index));
          if(match>=0)other.select(match,false);
          else{other.figure.querySelector('output').textContent=declaredDate(p.date)+' · Não há observação correspondente nesta série.';delete other.figure.dataset.selectedTicket;}
        });
      };reader.select=select;figure._fxcSelect=select;
      plot._fxcDraw=()=>{
        if(!plot.clientWidth||!plot.clientHeight)return;
        geometry=chartGeometry(series,plot.clientWidth,plot.clientHeight,domain,figure.dataset.fxcSeries==='drawdown');
        axis.innerHTML=geometry.ticks.map(t=>`<span style="top:${t.y/geometry.height*100}%">${safe(number(t.value,figure.dataset.unit))}</span>`).join('');
        const markerHtml=markers.map(m=>{
          const index=series.points.findIndex(p=>p.ticket!==null&&p.ticket===String(m.ticket)&&p.date===m.time);const point=geometry.positions[index];
          return point?`<g data-fxc-cashflow="${safe(m.ticket)}"><title>${safe(m.profit>=0?'Depósito':'Retirada')} · ${safe(declaredDate(m.time))} · ${safe(exactValue(m.profit,m.currency))}</title><line class="fxc-cashflow-line" x1="${point.x}" x2="${point.x}" y1="0" y2="${geometry.height}"/><circle class="fxc-cashflow-dot" cx="${point.x}" cy="7" r="4"/></g>`:'';
        }).join('');
        plot.innerHTML=`<svg viewBox="0 0 ${geometry.width} ${geometry.height}" width="${geometry.width}" height="${geometry.height}" preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false"><g class="fxc-grid">${geometry.ticks.map(t=>`<line x1="0" x2="${geometry.width}" y1="${t.y}" y2="${t.y}"/>`).join('')}</g>${geometry.segments.map(s=>`<path class="fxc-line fxc-${safe(figure.dataset.color)}" data-fxc-segment="${s.indices.join(',')}" d="${s.path}"/>`).join('')}${markerHtml}<line class="fxc-guide" x1="0" x2="0" y1="0" y2="${geometry.height}"/>${geometry.coords.map(p=>`<circle class="fxc-point fxc-${safe(figure.dataset.color)}" data-fxc-point="${p.index}" data-value="${safe(String(p.value))}" data-x="${p.x}" cx="${p.x}" cy="${p.y}" r="3"/>`).join('')}</svg>`;
        select(Number(cursor.value),false);
      };
      const pointer=event=>{if(!geometry)return;const x=event.clientX-plot.getBoundingClientRect().left;const closest=geometry.positions.reduce((a,p)=>Math.abs(p.x-x)<Math.abs(a.x-x)?p:a,geometry.positions[0]);select(closest.index);};
      plot.addEventListener('pointermove',event=>{if(event.pointerType==='mouse')pointer(event);});plot.addEventListener('pointerdown',pointer);
      cursor.addEventListener('input',()=>select(Number(cursor.value)));
      prev.addEventListener('click',()=>select(Number(cursor.value)-1));next.addEventListener('click',()=>select(Number(cursor.value)+1));
      plot._fxcDraw();select(Number(cursor.value),false);chartObserver?.observe(plot);
    });
    const main=readers.find(r=>r.figure.dataset.fxcSeries==='main');if(main)main.select(Number(main.figure.querySelector('.fxc-chart-cursor').value));
  }
  FX.visual=Object.freeze({series:chartSeries,geometry:chartGeometry});
  const hasValue=value=>typeof value==='number'&&Number.isFinite(value);
  function monthly(model){
    const rows=model.breakdowns?.monthly||[],growthAvailable=rows.some(r=>hasValue(r.growthPct)),nominalAvailable=rows.some(r=>hasValue(r.netProfit));
    const mode=ui.monthlyMode||(ui.source==='manual'||!growthAvailable?'nominal':'growth'),field=mode==='growth'?'growthPct':'netProfit',unit=mode==='growth'?'%':projectedCurrency(model)||'';
    const controls=`<div class="fxc-month-head"><div><h3>Resultados mensais</h3><p>Cada valor pertence ao período observado. Ausência não é zero.</p></div><div class="fxc-segment" aria-label="Unidade dos resultados mensais"><button type="button" data-fxc-month-mode="growth" aria-pressed="${mode==='growth'}" ${growthAvailable?'':'disabled'}>Crescimento %</button><button type="button" data-fxc-month-mode="nominal" aria-pressed="${mode==='nominal'}" ${nominalAvailable?'':'disabled'}>Resultado ${safe(projectedCurrency(model)||'nominal')}</button></div></div>`;
    if(!rows.length)return `<section class="fxc-month-section">${controls}<p class="fxc-note">Sem resultados mensais calculáveis nesta seleção. Um resumo global não informa resultados de cada mês.</p></section>`;
    const years=[...new Set(rows.map(r=>String(r.month||'').slice(0,4)))].filter(y=>/^\d{4}$/.test(y)).sort();
    const months=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],max=Math.max(1,...rows.map(r=>hasValue(r[field])?Math.abs(r[field]):0));
    return `<section class="fxc-month-section">${controls}<div class="fxc-scroll"><table class="fxc-months"><caption>${mode==='growth'?(model.coverage?.kind==='summary'?'Crescimento mensal informado no relatório':'Crescimento mensal ajustado aos fluxos'):'Resultado realizado mensal'} · ${safe(unit)} · clique em um mês para consultar os registros</caption><thead><tr><th scope="col">Ano</th>${months.map(m=>'<th scope="col">'+m+'</th>').join('')}<th scope="col">Total observado</th></tr></thead><tbody>${years.map(y=>'<tr><th scope="row">'+safe(y)+'</th>'+months.map((month,i)=>{
      const key=y+'-'+String(i+1).padStart(2,'0'),row=rows.find(r=>r.month===key),value=row?.[field],known=hasValue(value),state=known?(model.coverage?.kind==='summary'?'imported':'calculated'):'unavailable';
      const reason=row?'Valor indisponível nesta seleção; o período pode ser parcial ou faltar a base.':'Sem registros disponíveis neste mês.';
      return `<td data-month="${key}" data-label="${month}" data-availability="${state}" data-value="${known?String(value):''}" class="${known?(value>0?'fxc-month-positive':value<0?'fxc-month-negative':'fxc-month-zero'):'fxc-month-missing'}" style="--fxc-month-intensity:${known?(.08+.16*Math.abs(value)/max).toFixed(3):0}">${row?`<button type="button" data-fxc-month="${key}" aria-label="${month} ${y}: ${known?safe(exactValue(value,unit)):safe(reason)}; consultar registros">${known?safe(number(value,unit)):'—'}</button>`:`<span title="${safe(reason)}" aria-label="${month} ${y}: ${safe(reason)}">—</span>`}</td>`;
    }).join('')+`<td class="fxc-month-total" data-label="Total observado">${safe(number(model.breakdowns.years?.find(r=>r.year===y)?.[field],unit))}</td></tr>`).join('')}</tbody></table></div><p id="fxcMonthStatus" role="status">${safe(ui.monthMessage)}</p>${model.coverage?.kind==='summary'?'<p class="fxc-note">Valores informados no resumo importado; eventos individuais não estão disponíveis para detalhamento.</p>':''}</section>`;
  }
  function recordDetail(r){
    const fields=(items)=>'<dl class="fxc-record-fields">'+items.map(([name,value])=>`<div><dt>${safe(name)}</dt><dd>${safe(value==null?'Não informado':String(value))}</dd></div>`).join('')+'</dl>';
    const money=value=>hasValue(value)?exactValue(value,r.currency||''):null;
    const technical=Object.fromEntries(['ticket','id','time','openedAt','closedAt','symbol','direction','executionDirection','type','entry','orderTicket','positionId','volume','price','profit','commission','fee','swap','netResult','source','currency','accountId','facts'].filter(k=>r[k]!=null).map(k=>[k,r[k]]));
    return `<details class="fxc-record-detail" data-fxc-disclosure="record-${safe(r.ticket||r.operationId||r.id)}"><summary>Ver detalhes do registro ${safe(r.ticket||r.id||'')}</summary><section><h4>Identificação e execução</h4>${fields([['Referência',r.ticket||r.operationId||r.id],['Instrumento',r.symbol||r.instrument],['Horário declarado',declaredDate(r.time||r.closedAt)],['Tipo',r.type||'Operação manual finalizada'],['Direção da operação',r.direction],['Direção do deal',r.executionDirection],['Volume',r.volume],['Preço executado',r.price]])}</section><section><h4>Resultado e custos</h4>${fields([['Resultado líquido',money(r.netResult)],['Resultado antes dos custos',money(r.profit)],['Comissão',money(r.commission)],['Swap',money(r.swap)],['Taxa',money(r.fee)]])}<p>Custos assinados já participam do líquido quando disponíveis; não somar novamente.</p></section><section><h4>Origem</h4><p>${r.source==='manual'?'Fechamento local registrado no JP Wealth; não comprova todas as execuções da corretora.':'Execução ou lançamento informado no relatório MT5; não comprova o estado atual da corretora.'}</p></section><details class="fxc-record-raw" data-fxc-disclosure="record-${safe(r.ticket||r.operationId||r.id)}-raw"><summary>Campos técnicos e rastreabilidade</summary><pre>${safe(JSON.stringify(technical,null,2))}</pre></details></details>`;
  }
  function filteredRecords(model){
    return (model.records||[]).filter(r=>{
      const filter=ui.historyFilter;if(filter?.month&&String(r.time||r.closedAt||'').slice(0,7)!==filter.month)return false;
      if(filter?.field&&(r[filter.field]||'unknown')!==filter.value)return false;
      return JSON.stringify(r).toLocaleLowerCase('pt-BR').includes(ui.search.toLocaleLowerCase('pt-BR'));
    });
  }
  function history(model){
    const rows=filteredRecords(model),filter=ui.historyFilter;
    return `<p class="fxc-note">${ui.source==='manual'?'Operações finalizadas do JP Wealth; não equivalem a execuções do MT5.':'Execuções e movimentações importadas. Deals de saída, inclusive fechamentos parciais, não equivalem necessariamente a posições completas.'}</p><p id="fxcHistoryFilter">${filter?'Filtro da tabela: '+safe(filter.month||filter.value)+'. ':''}Busca e filtros desta tabela não alteram os indicadores da conta. ${filter||ui.search?'<button type="button" data-fxc-clear-history>Limpar filtro da tabela</button>':''}</p><div class="fxc-scroll"><table class="fxc-movements"><caption>${rows.length} registros exibidos de ${model.records?.length||0} no período selecionado</caption><thead><tr><th scope="col">Data / hora</th><th scope="col">Identificador</th><th scope="col">Instrumento</th><th scope="col">Tipo</th><th scope="col">Resultado líquido</th><th scope="col">Detalhes</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${safe(declaredDate(r.time||r.closedAt||r.date)||'Não registrada')}</td><td>${safe(r.ticket||r.operationId||r.id||'—')}</td><td>${safe(r.symbol||r.instrument||'—')}</td><td>${safe(r.type||r.direction||r.kind||'Operação')}</td><td class="fxc-number" data-value="${hasValue(r.netResult)?String(r.netResult):''}">${safe(number(r.netResult,r.currency||''))}</td><td>${recordDetail(r)}</td></tr>`).join('')||'<tr><td colspan="6">Nenhum registro individual disponível para esta conta, fonte, período e filtro. Um resumo importado não permite reconstruir execuções.</td></tr>'}</tbody></table></div>`;
  }
  function distribution(rows,title,field,unit){
    if(!rows?.length)return unavailable(title,'Nenhum registro classificável nesta seleção.');
    const ordered=[...rows].sort((a,b)=>ui.sort==='name'?String(a[field]||'unknown').localeCompare(String(b[field]||'unknown')):(hasValue(b.netProfit)?b.netProfit:-Infinity)-(hasValue(a.netProfit)?a.netProfit:-Infinity));
    const max=Math.max(1,...ordered.map(r=>hasValue(r.netProfit)?Math.abs(r.netProfit):0));
    return `<section class="fxc-distribution"><h3>${safe(title)}</h3><p>Resultado líquido · ${safe(unit||'moeda não conciliada')} · eixo central: zero</p><ul class="fxc-result-bars">${ordered.map(r=>{const value=r.netProfit,name=r[field]||'unknown';return `<li><button type="button" data-fxc-drill-field="${safe(field)}" data-fxc-drill-value="${safe(name)}" data-value="${hasValue(value)?String(value):''}" aria-label="Ver registros de ${safe(name==='unknown'?'Não classificado':name)}"><span>${safe(name==='unknown'?'Não classificado':name)}</span><strong>${safe(number(value,unit))}</strong><span class="fxc-bar-track fxc-bar-diverging" aria-hidden="true"><span class="fxc-bar-zero"></span>${hasValue(value)?`<i class="${value<0?'fxc-bar-negative':''}" style="left:${value<0?50-Math.abs(value)/max*50:50}%;width:${Math.abs(value)/max*50}%"></i>`:''}</span><small>${Number.isFinite(r.tradeCount)?r.tradeCount+' '+(ui.source==='manual'?'operações finalizadas':'deals de saída'):'Contagem indisponível'}</small></button></li>`;}).join('')}</ul></section>`;
  }
  function dateExtent(model){
    const dates=(model.records||[]).map(r=>String(r.time||r.closedAt||'').slice(0,10)).filter(d=>chartTime(d));
    return dates.length?{from:dates.reduce((a,b)=>a<b?a:b),to:dates.reduce((a,b)=>a>b?a:b)}:null;
  }
  function selectPeriod(preset){
    const extent=dateExtent(fullModel||{});ui.preset=preset;ui.historyFilter=null;ui.monthMessage='';
    if(preset==='all'){ui.from='';ui.to='';}
    else if(preset==='custom'){el('fxcDateRange').open=true;el('fxcFrom').focus();updatePeriodControls();return;}
    else if(extent){
      const end=chartTime(extent.to).time,d=new Date(end),months=preset==='12m'?12:3,day=d.getUTCDate();d.setUTCDate(1);d.setUTCMonth(d.getUTCMonth()-months);const last=new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth()+1,0)).getUTCDate();d.setUTCDate(Math.min(day,last));ui.from=d.toISOString().slice(0,10);ui.to=extent.to;
    }else return;
    el('fxcFrom').value=ui.from;el('fxcTo').value=ui.to;render();
  }
  function updatePeriodControls(){
    const extent=dateExtent(fullModel||{});
    document.querySelectorAll('[data-fxc-preset]').forEach(button=>{button.setAttribute('aria-pressed',String(button.dataset.fxcPreset===ui.preset));button.disabled=['12m','3m'].includes(button.dataset.fxcPreset)&&!extent;});
    el('fxcPeriodCaption').textContent=extent?'Atalhos referenciados à última data disponível: '+declaredDate(extent.to)+'. O recorte não rebasa a curva acumulada.':'Sem histórico datado para os atalhos. Resumos preservam o período declarado; filtros menores não criam novas estatísticas.';
  }
  function projectedCurrency(model){
    if(typeof model.currency==='string'&&model.currency.trim())return model.currency;
    return ['netProfit','balance','equity'].map(key=>metric(model,key).unit).find(unit=>typeof unit==='string'&&unit!=='%')||null;
  }
  function chartProvenance(model){
    const coverage=ui.source==='manual'?'operações finalizadas capturadas':model.coverage?.completeHistory?'histórico integral comprovado':model.coverage?.partial?'histórico parcial':model.coverage?.kind==='summary'?'resumo informado':'cobertura não comprovada';
    return `Fonte: ${ui.source==='manual'?'Manual':'MT5'} · Moeda dos dados: ${projectedCurrency(model)||'não conciliada'} · Período: ${declaredDate(model.period?.from||ui.from)||'início não informado'} → ${declaredDate(model.period?.to||ui.to)||'fim não informado'} · Cobertura: ${coverage}`;
  }
  function panels(model){
    const stat=[['trades',ui.source==='manual'?'Operações finalizadas':'Deals de saída (inclui parciais)'],['wins','Resultados positivos'],['losses','Resultados negativos'],['neutral','Resultados zero'],['winRate','Taxa de resultados positivos','%'],['profitFactor','Fator de lucro · base declarada'],['expectedPayoff',ui.source==='manual'?'Resultado líquido / operações':'Resultado líquido / saídas'],['averageWin','Média dos resultados positivos'],['averageLoss','Média dos resultados negativos'],['bestTrade','Melhor resultado'],['worstTrade','Pior resultado'],['maxWinStreak','Maior sequência positiva'],['maxLossStreak','Maior sequência negativa']];
    const seriesInput=ui.source==='manual'?model.series?.realized:model.series?.[ui.chart],mainSeries=chartSeries(seriesInput),ddSeries=chartSeries(model.series?.drawdown);
    const sync=ui.source==='mt5'&&mainSeries.axisMode==='time'&&ddSeries.axisMode==='time'&&mainSeries.timeKind===ddSeries.timeKind&&mainSeries.validCount&&ddSeries.validCount;
    const domain=sync?[Math.min(mainSeries.points[0].time,ddSeries.points[0].time),Math.max(mainSeries.points.at(-1).time,ddSeries.points.at(-1).time)]:null;
    const flows=(model.records||[]).filter(r=>r.type==='balance'&&hasValue(r.profit));
    const title=ui.source==='manual'?'Resultado realizado acumulado no período':ui.chart==='growth'?'Crescimento acumulado desde a origem'+(ui.from||ui.to?' · recorte selecionado':''):'Saldo histórico';
    const main=chart(seriesInput,title,'blue',ui.source==='manual'?metric(model,'netProfit').unit||'':ui.chart==='growth'?'%':metric(model,'balance').unit||projectedCurrency(model)||'','main','',{domain,group:sync?'account':'',markers:ui.cashflows?flows:[]});
    const dd=ui.source==='manual'?'<p class="fxc-empty-series">Drawdown do saldo indisponível: fechamentos manuais não constituem uma série de saldo.</p>':chart(model.series?.drawdown,'Drawdown histórico do saldo','negative','%','drawdown','Inclui depósitos e retiradas. Não é drawdown de equity nem o drawdown operacional JP Wealth.',{domain,group:sync?'account':''});
    const accountFacts=`<dl class="fxc-account-facts">${label(model,'balance','Saldo disponível')}${label(model,'equity','Equity disponível')}</dl><p class="fxc-note">Valores calculados a partir dos registros ou informados no relatório, conforme a origem indicada. Referência do saldo calculado: ${safe(declaredDate(model.series?.balance?.at(-1)?.time)||'sem série calculável')}. Importação não equivale a observação atual da conta.</p>`;
    el('fxcPanel-account').innerHTML=`<dl class="fxc-primary-kpis">${label(model,'growth','Crescimento no período','%')}${label(model,'netProfit','Resultado realizado')}${label(model,'maxDrawdownPct','Drawdown histórico do saldo','%')}</dl><details class="fxc-account-facts-detail" data-fxc-disclosure="account-facts"><summary>Saldo, equity e origem dos valores</summary>${accountFacts}</details><section class="fxc-integrated-panel" aria-label="Evolução e risco histórico"><div class="fxc-chart-head"><div><h3>Evolução da conta</h3><p>${ui.source==='manual'?'Acumulado dos fechamentos locais selecionados.':'Crescimento do período no resumo; curva acumulada desde a origem, mesmo quando recortada.'}</p></div>${ui.source==='mt5'?`<div class="fxc-segment" aria-label="Gráfico principal"><button type="button" data-fxc-chart="growth" aria-pressed="${ui.chart==='growth'}">Crescimento</button><button type="button" data-fxc-chart="balance" aria-pressed="${ui.chart==='balance'}">Saldo</button></div>`:''}</div>${ui.source==='mt5'?`<label class="fxc-check fxc-cashflow-toggle"><input type="checkbox" id="fxcCashflows" ${ui.cashflows?'checked':''} ${flows.length?'':'disabled'}> Marcar depósitos e retiradas registrados (${flows.length})</label>`:''}${main}${dd}${sync?`<details class="fxc-shared-axis" data-fxc-disclosure="shared-axis"><summary>Como ler as duas curvas</summary><p>${safe(axisDescription(mainSeries))} Os cursores consultam o mesmo evento quando ele existe nas duas séries. Valores ausentes interrompem a curva; nenhum ponto é completado.</p></details>`:''}${ui.cashflows&&flows.length?`<details class="fxc-cashflow-values" data-fxc-disclosure="cashflows"><summary>Consultar movimentações de caixa marcadas</summary><ul>${flows.map(r=>`<li>${safe(declaredDate(r.time))} · ${r.profit>=0?'Depósito':'Retirada'} · ${safe(exactValue(r.profit,r.currency))} · ${safe(r.ticket)}</li>`).join('')}</ul></details>`:''}${!mainSeries.validCount?'<button type="button" data-fxc-import-action>Importar histórico da conta</button>':''}</section>${monthly(model)}<details class="fxc-methodology" data-fxc-disclosure="methodology"><summary>Metodologia, cobertura e séries indisponíveis</summary><p>${safe(chartProvenance(model))}</p><p>Três origens distintas: calculado dos registros, informado em resumo para um período e observado em um instante. O gráfico não interpola eventos ausentes, não corrige fluxos por conta própria e não produz uma curva de equity a partir de uma fotografia.</p><p>Equity, flutuante, margem e exposição históricos: sem série observada disponível nesta fonte. Para analisá-los será necessária uma fonte histórica própria. O indicador atual isolado não preenche essas curvas.</p><p>${ui.source==='manual'?'Registros manuais mostram somente fatos capturados no encerramento.':'A unidade de contagem é deal de saída, inclusive parcial, reversão e Close By; não pressupõe uma posição completa.'}</p><p>Resumo importado conserva seu período original. Uma seleção menor sem eventos compatíveis permanece indisponível.</p></details>`;
    el('fxcPanel-history').innerHTML=history(model)+(ui.source==='mt5'?['orders','positions'].map(collection=>{const rows=(S.fxConsolidated?.accounts?.find(a=>a.id===ui.accountId)?.[collection]||[]);return `<details class="fxc-entity-details" data-fxc-disclosure="entity-${collection}"><summary>${collection==='orders'?'Ordens registradas (históricas e pendentes)':'Snapshots de posições abertas'} · ${rows.length}</summary><p>Entidade distinta de execução; não integra a contagem de negociações. Fotografias importadas não comprovam o estado atual da corretora. Este inventário não é filtrado pelo período das execuções.</p><div class="fxc-scroll"><table><thead><tr><th>Ticket</th><th>Instrumento</th><th>Tipo / estado</th><th>Data observada</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${safe(r.ticket)}</td><td>${safe(r.symbol)}</td><td>${safe([r.type,r.state,r.orderScope].filter(Boolean).join(' · '))}</td><td>${safe(declaredDate(r.time||r.openedAt)||'Não informada')}</td></tr>`).join('')}</tbody></table></div></details>`;}).join(''):'');
    const statGroups=[['Contagens e frequência',stat.slice(0,5)],['Resultados',stat.slice(5,11)],['Sequências',stat.slice(11)]];
    const statsMarkup=statGroups.map(([title,items])=>{
      const ready=items.filter(([key])=>hasValue(metric(model,key).value)),missing=items.filter(([key])=>!hasValue(metric(model,key).value));
      return `<section class="fxc-stat-group"><h3>${safe(title)}</h3>${ready.length?`<dl class="fxc-statistics">${ready.map(([k,t,u])=>label(model,k,t,u)).join('')}</dl>`:''}${missing.length?`<details data-fxc-disclosure="missing-${safe(title)}"><summary>Indicadores indisponíveis (${missing.length})</summary><dl class="fxc-statistics">${missing.map(([k,t,u])=>label(model,k,t,u)).join('')}</dl></details>`:''}</section>`;
    }).join('');
    el('fxcPanel-statistics').innerHTML=`<p class="fxc-note">${ui.source==='manual'?'Estatísticas dos resultados líquidos das operações finalizadas no JP Wealth.':'Estatísticas por deal de saída. Fechamentos parciais e reversões podem gerar vários registros para uma posição.'}</p><div class="fxc-stat-groups">${statsMarkup}</div><div class="fxc-distribution-heading"><h3>O que explica o resultado</h3><label>Ordenar distribuições<select id="fxcDistributionSort"><option value="result" ${ui.sort==='result'?'selected':''}>Resultado: maior para menor</option><option value="name" ${ui.sort==='name'?'selected':''}>Nome</option></select></label></div><div class="fxc-distributions">${distribution(model.breakdowns?.symbols,'Resultado por instrumento','symbol',projectedCurrency(model)||'')}${distribution(model.breakdowns?.directions,'Resultado por direção','direction',projectedCurrency(model)||'')}</div><details class="fxc-costs" data-fxc-disclosure="costs"><summary>Custos e movimentações de caixa</summary><h3>Custos já considerados no líquido</h3><dl class="fxc-statistics">${[['commission','Comissões'],['swap','Swaps'],['fee','Taxas']].map(([k,t])=>label(model,k,t)).join('')}</dl><h3>Movimentações de capital</h3><dl class="fxc-statistics">${[['deposits','Depósitos (inclui o inicial quando registrado)'],['withdrawals','Retiradas'],['initialBalance','Primeiro depósito registrado']].map(([k,t])=>label(model,k,t)).join('')}</dl><p>Depósitos e retiradas não são lucro. O primeiro depósito já participa dos depósitos; não somar as duas informações. Custos não são descontados novamente.</p></details>`;
    el('fxcPanel-risks').innerHTML=`<section id="fxcRiskBasis"><h3>Três leituras diferentes de drawdown</h3><dl class="fxc-risk-definitions"><div><dt>Histórico do saldo</dt><dd>Queda em relação ao pico histórico do balance calculado dos registros. Inclui movimentos de caixa. A série aparece junto da evolução no Painel.</dd></div><div><dt>Operacional JP Wealth</dt><dd>Calculado pelo motor no contexto operacional e com sua própria base. Consulte Operação; não é substituído por esta estatística histórica.</dd></div><div><dt>Informado no relatório</dt><dd>Valor declarado na importação para seu período e base. Não comprova uma curva observada e não altera limites ou autorização.</dd></div></dl><dl class="fxc-statistics">${label(model,'maxDrawdown','Drawdown máximo do saldo')}${label(model,'maxDrawdownPct','Drawdown relativo do saldo','%')}</dl><button type="button" data-fxc-tab="account">Ver evolução e drawdown</button><button type="button" data-fxc-go="forex-operation">Consultar risco operacional</button></section><details data-fxc-disclosure="other-risk"><summary>Outras informações de risco disponíveis no relatório</summary><dl class="fxc-statistics">${label(model,'maxLoad','Margem utilizada máxima informada','%')}${label(model,'mfe','MFE — excursão favorável')}${label(model,'mae','MAE — excursão adversa')}</dl><p>Margem utilizada não equivale a perda potencial. Valores isolados não constituem uma trajetória histórica.</p></details>`;
    for(const [id] of tabs){const active=ui.tab===id;el('fxcPanel-'+id).hidden=!active;el('fxcPanel-'+id).inert=!active;el('fxcTab-'+id).setAttribute('aria-selected',String(active));el('fxcTab-'+id).tabIndex=active?0:-1;}
    el('fxcSearch').closest('label').hidden=ui.tab!=='history';
    bindCharts();
  }
  function notify(message,kind='info'){ui.message=message;ui.kind=kind;if(el('fxcStatus')){el('fxcStatus').textContent=message;el('fxcStatus').dataset.kind=kind;}}
  function options(accounts,selected,automatic=false){return (automatic?'<option value="">Automático — conta Mestre</option>':'<option value="">Selecione uma conta</option>')+accounts.map(a=>`<option value="${safe(a.id)}" ${selected===a.id?'selected':''}>${safe(a.name||a.nome||a.id)}${a.login?' · '+safe(a.login):''}${a.archived?' · histórico':''}</option>`).join('');}
  function mount(){
    const root=el('fxconsolidated');if(!root||ui.mounted)return;
    root.innerHTML=`<div class="fxc-workspace"><header class="fxc-toolbar"><div><h1>Desempenho</h1><p>Resultados da conta e do período em análise</p></div><button type="button" id="fxcOpenImport">Importar / Atualizar relatório</button></header><section class="fxc-context-band" aria-label="Contexto da análise"><div class="fxc-summary"><section id="fxcIdentity"></section></div><div class="fxc-controls"><label>Conta em análise<select id="fxcAccount"></select></label><div class="fxc-segment" aria-label="Fonte dos dados"><button type="button" id="fxcMt5" aria-pressed="true">MT5</button><button type="button" id="fxcManual" aria-pressed="false">Manual</button></div><label hidden>Filtrar somente a tabela<input type="search" id="fxcSearch" placeholder="Ticket, instrumento ou operação"></label><button type="button" id="fxcPreferences" aria-label="Configurar conta padrão do Consolidado">Conta padrão</button></div><div class="fxc-period-toolbar"><div class="fxc-segment" aria-label="Período de análise"><button type="button" data-fxc-preset="all" aria-pressed="true">Todo o histórico</button><button type="button" data-fxc-preset="12m" aria-pressed="false">12 meses</button><button type="button" data-fxc-preset="3m" aria-pressed="false">3 meses</button><button type="button" data-fxc-preset="custom" aria-pressed="false">Personalizado</button></div><details id="fxcDateRange"><summary>Datas e referência do recorte</summary><div class="fxc-custom-dates"><label>De<input type="date" id="fxcFrom"></label><label>Até<input type="date" id="fxcTo"></label></div><p id="fxcPeriodCaption"></p></details></div><div class="fxc-context-support"><section id="fxcNextAction" class="fx-next-action" aria-label="Próxima ação no Forex"></section><details class="fxc-coverage-details"><summary>Cobertura e metodologia</summary><p id="fxcCoverage" class="fxc-provenance"></p></details></div></section><p id="fxcStatus" role="status" aria-live="polite"></p><section id="fxcImport" hidden aria-label="Importar relatório MT5"><h2>Importar relatório MT5</h2><p>Escolha um relatório HTML ou PDF textual. Processamento local; após confirmar, o original será preservado em um arquivo de evidências separado neste navegador. Faça também sua cópia externa. Analisar cria uma prévia; só a confirmação seguinte grava a importação. Confira a conta selecionada antes de confirmar.</p><label>Arquivo do relatório<input id="fxcFile" type="file" accept=".html,.htm,.pdf"></label><div class="fxc-import-dates"><label>Início declarado, se ausente<input type="date" id="fxcImportFrom"></label><label>Fim declarado, se ausente<input type="date" id="fxcImportTo"></label></div><div class="fxc-import-dates"><label>Separadores numéricos<select id="fxcNumberFormat"><option value="auto">Detectar pelo conteúdo</option><option value="decimal-dot">1,234.56 — ponto decimal</option><option value="decimal-comma">1.234,56 — vírgula decimal</option></select></label><label>Datas sem ano no início<select id="fxcDateOrder"><option value="auto">Detectar pelo conteúdo</option><option value="dmy">Dia / mês / ano</option><option value="mdy">Mês / dia / ano</option></select></label></div><p>Se houver ambiguidade, selecione o formato do documento e analise novamente. Confira os valores originais e interpretados na prévia.</p><button type="button" id="fxcAnalyze">Analisar arquivo</button><button type="button" id="fxcCancelImport">Cancelar</button><div id="fxcPreview"></div></section><section id="fxcImportResult" hidden aria-label="Próximo passo após importar"></section><div class="fxc-tabs" role="tablist" aria-label="Visões do Consolidado">${tabs.map(([id,title],i)=>`<button type="button" role="tab" id="fxcTab-${id}" aria-controls="fxcPanel-${id}" aria-selected="${!i}" tabindex="${i?-1:0}" data-fxc-tab="${id}">${title}</button>`).join('')}</div>${tabs.map(([id])=>`<section role="tabpanel" id="fxcPanel-${id}" aria-labelledby="fxcTab-${id}" tabindex="0" ${id==='account'?'':'hidden'}></section>`).join('')}<p class="fxc-provenance">MT5 e Manual são bases separadas. Registrar ou importar fatos não autoriza operar. Contexto financeiro ausente continua indisponível.</p></div>`;
    // Move a apresentação existente, nunca clona widgets ou o read model.
    const context=document.createElement('aside');context.id='fxOperationalContext';
    context.setAttribute('aria-labelledby','fxContextTitle');
    context.innerHTML='<header class="fx-context-heading"><span class="cp-kicker">FOREX · AGORA</span><h2 id="fxContextTitle">Em operação</h2><p>Relacionado à conta operacional, independente da conta em análise.</p></header><div id="fxOperationalSummary"></div><button type="button" id="fxContextToggle" aria-expanded="false" aria-controls="execOverview">Ver contexto completo</button>';
    root.classList.add('fx-journey');root.append(context);
    context.append(el('execOverview'));
    el('execOverview').hidden=true;el('execOverview').inert=true;
    el('fxContextToggle').addEventListener('click',()=>fxSetContextExpanded(el('execOverview').hidden));
    root.addEventListener('click',event=>{
      const destination=event.target.closest('[data-fxc-go]');if(destination){JPWNavigation.navigate(destination.dataset.fxcGo);return;}
      const preset=event.target.closest('[data-fxc-preset]');if(preset){selectPeriod(preset.dataset.fxcPreset);return;}
      const tab=event.target.closest('[data-fxc-tab]'),toggle=event.target.closest('[data-fxc-chart]'),monthMode=event.target.closest('[data-fxc-month-mode]'),month=event.target.closest('[data-fxc-month]'),drill=event.target.closest('[data-fxc-drill-field]');
      if(tab){ui.tab=tab.dataset.fxcTab;render();el('fxcTab-'+ui.tab)?.focus();return;}
      if(toggle){ui.chart=toggle.dataset.fxcChart;render();root.querySelector(`[data-fxc-chart="${ui.chart}"]`)?.focus();return;}
      if(monthMode){ui.monthlyMode=monthMode.dataset.fxcMonthMode;render();root.querySelector(`[data-fxc-month-mode="${ui.monthlyMode}"]`)?.focus();return;}
      if(month){
        if(!currentModel.records?.some(r=>String(r.time||r.closedAt||'').slice(0,7)===month.dataset.fxcMonth)){
          ui.monthMessage='Este mês possui somente resumo importado ou nenhum evento individual nesta seleção. Não é possível reconstruir as execuções.';el('fxcMonthStatus').textContent=ui.monthMessage;return;
        }
        ui.historyFilter={month:month.dataset.fxcMonth};ui.search='';el('fxcSearch').value='';ui.tab='history';render();el('fxcPanel-history').focus();return;
      }
      if(drill){ui.historyFilter={field:drill.dataset.fxcDrillField,value:drill.dataset.fxcDrillValue};ui.search='';el('fxcSearch').value='';ui.tab='history';render();el('fxcPanel-history').focus();return;}
      if(event.target.closest('[data-fxc-clear-history]')){ui.historyFilter=null;ui.search='';el('fxcSearch').value='';render();el('fxcSearch').focus();return;}
      if(event.target.closest('[data-fxc-import-action]'))openImport({returnFocus:el('fxcOpenImport')});
    });
    root.addEventListener('change',event=>{
      if(event.target.id==='fxcCashflows'){ui.cashflows=event.target.checked;render();el('fxcCashflows')?.focus();}
      if(event.target.id==='fxcDistributionSort'){ui.sort=event.target.value;render();el('fxcDistributionSort')?.focus();}
    });
    root.querySelector('[role=tablist]').addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();const i=tabs.findIndex(([id])=>id===ui.tab);ui.tab=tabs[event.key==='Home'?0:event.key==='End'?3:(i+(event.key==='ArrowRight'?1:3))%4][0];render();el('fxcTab-'+ui.tab).focus();});
    const clearFilters=()=>{ui.historyFilter=null;ui.monthMessage='';ui.monthlyMode=null;ui.from='';ui.to='';ui.preset='all';el('fxcFrom').value='';el('fxcTo').value='';};
    el('fxcAccount').addEventListener('change',event=>{ui.accountId=event.target.value||null;cancel();clearFilters();render();});
    el('fxcMt5').onclick=()=>{ui.source='mt5';clearFilters();render();};el('fxcManual').onclick=()=>{ui.source='manual';cancel();clearFilters();render();};
    for(const [id,key] of [['fxcFrom','from'],['fxcTo','to'],['fxcSearch','search']])el(id).addEventListener('input',event=>{ui[key]=event.target.value;if(key!=='search'){ui.preset='custom';ui.historyFilter=null;ui.monthMessage='';}render();});
    el('fxcPreferences').onclick=()=>openSettingsModal('forex-consolidated',el('fxcPreferences'));
    el('fxcOpenImport').onclick=()=>openImport({returnFocus:el('fxcOpenImport')});
    el('fxcCancelImport').onclick=()=>{cancel();el('fxcImport').hidden=true;el('fxcOpenImport').focus();};
    for(const id of ['fxcFile','fxcNumberFormat','fxcDateOrder','fxcImportFrom','fxcImportTo'])
      el(id).addEventListener('change',()=>{cancel();notify('Arquivo ou leitura alterados. Analise novamente para conferir a nova prévia.');});
    el('fxcAnalyze').onclick=analyze;ui.mounted=true;
  }
  let evidenceRender=0;
  async function renderOriginalEvidence(receipt,contextToken){
    const seq=++evidenceRender,coverage=el('fxcCoverage');if(!coverage)return;
    let box=el('fxcOriginalEvidence');
    if(!box){box=document.createElement('section');box.id='fxcOriginalEvidence';box.className='jpw-evidence-status';coverage.parentNode.appendChild(box);}
    if(ui.source!=='mt5'||!receipt){box.replaceChildren();return;}
    box.innerHTML='<p>Conferindo original do último comprovante…</p>';
    const state=window.JPWEvidence?await window.JPWEvidence.status(receipt.fileHash):{status:'ABSENT',reason:'Arquivo de evidências indisponível.'};
    if(seq!==evidenceRender||contextToken!==ui.token||!box.isConnected)return;
    box.innerHTML='<p>'+safe(state.reason)+'</p><p class="fxc-note">Original e dados processados têm armazenamentos e backups separados. Abrir o arquivo não registra aceite.</p>'+
      (state.status!=='CONFIRMED'?'<label>Reassociar PDF/HTML original<input type="file" id="fxcReassociateOriginal" accept=".pdf,.html,.htm"></label><button type="button" id="fxcReassociateConfirm">Conferir e preservar original</button>':'')+'<p id="fxcOriginalResult" role="status"></p>';
    const btn=el('fxcReassociateConfirm');if(btn)btn.onclick=async()=>{
      const file=el('fxcReassociateOriginal')?.files[0];if(!file){el('fxcOriginalResult').textContent='Escolha o original correspondente.';return;}
      btn.disabled=true;const r=window.JPWEvidence?await window.JPWEvidence.reassociate(file,receipt):{status:'REFUSED',reason:'Arquivo de evidências indisponível.'};
      if(seq!==evidenceRender||!box.isConnected)return;
      el('fxcOriginalResult').textContent=r.reason;btn.disabled=false;
      if(r.status==='CONFIRMED')renderOriginalEvidence(receipt,contextToken);
    };
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
      const meta={fileName:file.name,fileHash:hash,original:file,importedAt:new Date().toISOString(),from:el('fxcImportFrom').value||null,to:el('fxcImportTo').value||null};
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
      el('fxcPreview').innerHTML=`<h3>Confira a prévia</h3><dl class="fxc-statistics"><div><dt>Conta do relatório</dt><dd>${safe(report.identity?.login)}</dd></div><div><dt>Moeda</dt><dd>${safe(report.identity?.currency||'Não informada')}</dd></div><div><dt>Novas execuções</dt><dd>${safe(c.newDeals??0)}</dd></div><div><dt>Novas ordens</dt><dd>${safe(c.newOrders??0)}</dd></div><div><dt>Repetidos</dt><dd>${safe(c.duplicates??0)}</dd></div><div><dt>Divergências</dt><dd>${safe(c.conflicts??0)}</dd></div></dl><ul>${(preview.issues||report.issues||[]).map(i=>'<li>'+safe(i.message||i.code||i)+'</li>').join('')}</ul>${preview.conflicts?.length?`<details><summary>Comparar divergências</summary><pre>${safe(JSON.stringify(preview.conflicts,null,2))}</pre></details><label class="fxc-check"><input type="checkbox" id="fxcAcceptRevision"> Confirmo a revisão dos registros divergentes; manter o histórico anterior.</label>`:''}<label class="fxc-check"><input type="checkbox" id="fxcConfirmIdentity"> Conferi a conta de destino e a identidade do relatório. O arquivo não autentica a corretora.</label><button type="button" id="fxcConfirmImport">Confirmar importação</button><p>O comprovante e os dados processados serão salvos na base. O original terá confirmação separada no arquivo local de evidências; exporte também esse ZIP.</p>`;
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
  function restoreAccountFocus(target){
    const fallback=el('fxAccountsCreate');
    if(typeof shellRestoreHeaderFocus==='function')shellRestoreHeaderFocus(target?.isConnected?target:fallback);
    else if(target?.isConnected&&!target.closest('[hidden],[inert]')&&target.getClientRects().length)target.focus();
  }
  function closeRegistration(){
    FX.cancelRegistration?.();registrationView=null;
    if(registrationDialog?.open)registrationDialog.close();
  }
  function registrationValues(){return Object.fromEntries(new FormData(el('fxcRegistrationForm')));}
  function requestRegistrationClose(){
    const view=registrationView;if(!view||view.saving)return;
    if(view.confirmingClose){
      view.confirmingClose=false;el('fxcwDiscard').hidden=true;el('fxcwWork').inert=false;el('fxcwFooter').inert=false;
      el('fxcRegistrationCancel').focus();return;
    }
    if(!view.saved&&(view.unknown||JSON.stringify(registrationValues())!==view.initial)){
      view.confirmingClose=true;el('fxcwDiscard').hidden=false;el('fxcwWork').inert=true;el('fxcwFooter').inert=true;
      el('fxcwDiscardText').textContent=view.unknown?'O resultado da gravação está indeterminado. Fechar esta ficha não desfaz uma eventual gravação; confira a base antes de tentar cadastrar novamente.':'Há preenchimento não confirmado. Fechar descarta somente esta ficha; contas e etapas já confirmadas permanecem salvas.';
      el('fxcwKeep').focus();return;
    }
    closeRegistration();
  }
  function trapAccountDialogTab(event,dialog){
    if(event.key!=='Tab')return;
    const targets=[...dialog.querySelectorAll('button,input,select,textarea,a[href],[tabindex]')].filter(node=>
      node.tabIndex>=0&&!node.disabled&&!node.closest('[hidden],[inert]')&&node.getClientRects().length&&getComputedStyle(node).visibility!=='hidden');
    const first=targets[0],last=targets.at(-1),active=document.activeElement;
    if(!first){event.preventDefault();dialog.focus();return;}
    if(event.shiftKey&&(active===first||!targets.includes(active))){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&(active===last||!dialog.contains(active))){event.preventDefault();first.focus();}
  }
  function openAccountRegistration({report=null,accountId=null,trigger=document.activeElement,returnFocus=trigger,onSaved=null}={}){
    if(!available())return false;
    if(registrationView?.saving)return;
    if(registrationDialog?.open){registrationDialog.focus();return;}
    const prepared=FX.beginRegistration(report,accountId);
    if(!prepared.ok){if(report)notify(prepared.error,'error');else alert(prepared.error);return;}
    if(!registrationDialog){
      registrationDialog=document.createElement('dialog');registrationDialog.id='fxcRegistrationDialog';
      registrationDialog.className='fxc-registration fxc-account-wizard';registrationDialog.setAttribute('aria-labelledby','fxcRegistrationTitle');
      document.body.append(registrationDialog);
      registrationDialog.addEventListener('cancel',event=>{event.preventDefault();requestRegistrationClose();});
      registrationDialog.addEventListener('keydown',event=>{if(event.key==='Escape')event.stopPropagation();trapAccountDialogTab(event,registrationDialog);});
      registrationDialog.addEventListener('close',()=>{if(registrationDialog.open)return;const target=registrationDialog._returnFocus;registrationView=null;FX.cancelRegistration?.();restoreAccountFocus(target);});
    }
    const draft=prepared.draft,mode=prepared.mode,creating=mode!=='complete';
    const title=mode==='complete'?'Atualizar cadastro de conta de CFDs':mode==='reregister'?'Recadastrar conta de CFDs':'Cadastro de Nova Conta de CFDs';
    const profileContext=prepared.accountId?window.JPWForex?.state?.accountProfileContext?.({accountId:prepared.accountId,periodId:S.forex?.accountContexts?.accounts?.[prepared.accountId]?.currentPeriodId||null}):null;
    const steps=['Apresentação','Identificação','Metadados','Perfil de risco','Revisão'];
    registrationView={...prepared,saving:false,onSaved,step:0,saved:false};registrationDialog._returnFocus=returnFocus;
    const field=(key,label,required=false)=>`<label>${label}${required?' *':''}<input id="fxcr-${key}" name="${key}" value="${safe(draft[key])}" maxlength="160" ${required?'required':''} autocomplete="off"></label>`;
    registrationDialog.innerHTML=`<form id="fxcRegistrationForm" novalidate>
      <header class="fxcw-header"><div><p class="fxcw-eyebrow">FOREX · CONTAS E PERÍODO</p><h2 id="fxcRegistrationTitle">${title}</h2></div><button type="button" id="fxcwClose" class="fxcw-close" aria-label="Fechar cadastro">×</button></header>
      <ol class="fxcw-steps" aria-label="Etapas do cadastro">${steps.map((label,i)=>`<li data-fxcw-progress="${i}" aria-label="${i+1}. ${label}"><span aria-hidden="true">${i+1}</span><b class="fxcw-step-name">${label}</b></li>`).join('')}</ol><p id="fxcwProgressLabel" class="fxcw-progress-label"></p>
      <div id="fxcwWork" class="fxcw-body">
        <section data-fxcw-step="0"><h3 tabindex="-1">Uma conta, seus períodos e suas operações</h3><p>Cadastre uma conta de CFDs que você já utiliza. Ela terá uma identidade única no JP Wealth, com períodos e operações vinculados a ela.</p><p>Você vai conferir identificação, plataforma e perfil de risco. Depois de cadastrar, poderá preparar um período com moeda, capital inicial e referências financeiras próprias.</p><p class="fxcw-notice">Este cadastro não abre conta na corretora nem autoriza operar. Não são necessárias senhas, tokens ou credenciais.</p></section>
        <section data-fxcw-step="1" hidden inert><h3 tabindex="-1">Identificação da conta</h3><p>Use um nome reconhecível e o identificador fornecido pela plataforma. O número é preservado como texto, inclusive zeros iniciais.</p><div class="fxc-registration-fields">${field('name','Nome de identificação',true)}<label>Tipo da conta *<select name="type" id="fxcr-type">${['MESTRE','PRÓPRIA','SATÉLITE'].map(t=>`<option ${draft.type===t?'selected':''}>${t}</option>`).join('')}</select></label>${field('login','Número / login da conta',true)}</div></section>
        <section data-fxcw-step="2" hidden inert><h3 tabindex="-1">Metadados operacionais</h3><p>Identificadores conhecidos não podem ser substituídos por esta ficha. Corretora, servidor e moeda ausentes permanecem pendentes.</p><div class="fxc-registration-fields"><label>Plataforma *<select name="platform" id="fxcr-platform" required>${platformOptions(draft.platform)}</select></label>${field('broker','Corretora (opcional)')}${field('server','Servidor (se informado)')}${field('currency','Moeda-base · código de 3 letras (opcional)')}<label>Ambiente (opcional)<select id="fxcr-accountEnvironment" name="accountEnvironment">${[['','Não informado'],['real','Real'],['demo','Demo'],['unknown','Desconhecido declarado']].map(([key,label])=>`<option value="${key}" ${draft.accountEnvironment===key?'selected':''}>${label}</option>`).join('')}</select></label></div></section>
        <section data-fxcw-step="3" hidden inert><h3 tabindex="-1">Perfil de risco declarado</h3><p>O perfil pertence a esta conta. Sua atribuição valerá para um período criado explicitamente depois da confirmação; períodos existentes e históricos conservam suas referências.</p>${profileContext?`<p class="fxcw-notice">Perfil documental do período atual: ${safe(profileContext.period?.name||'Não definido nesse período')}. Perfil cadastral para próximo período: ${safe(profileContext.next?.name||'Ainda não declarado')}.</p>`:''}${prepared.legacyProfile&&!draft.profileKey?`<p class="fxcw-notice">Registro legado: ${safe(prepared.legacyProfile)}. Ainda não há atribuição versionada; nenhuma referência histórica será preenchida por este cadastro.</p>`:''}<label>Perfil${creating?' *':''}<select id="fxcr-profileKey" name="profileKey" ${creating?'required':''}><option value="">${creating?'Escolha o perfil':'Manter sem atribuição versionada'}</option>${riskProfilesForState().map(p=>`<option value="${safe(p.key)}" ${draft.profileKey===p.key?'selected':''}>${safe(p.name)}</option>`).join('')}</select></label><p id="fxcwProfileHelp" class="fxcw-notice"></p>${field('profileReason','Motivo da alteração de perfil (quando alterado)')}<p>Perfil cadastral e risco efetivo são leituras distintas. O motor continua verificando as regras vigentes; fatores P-30 pendentes não são liberados.</p></section>
        <section data-fxcw-step="4" hidden inert><h3 tabindex="-1">Revise antes de confirmar</h3><dl id="fxcwReview" class="fxcw-review"></dl><p class="fxcw-notice">Esta confirmação salva somente o cadastro e o perfil declarado. Período, SI, saldo e equity terão suas próprias confirmações. A conta operacional não será trocada.</p>${mode==='reregister'?'<label class="fxc-check"><input id="fxcr-history" name="confirmHistorical" type="checkbox" required> Confirmo reutilizar esta identidade e preservar seu histórico, sem restaurar saldos operacionais.</label>':''}</section>
        <section id="fxcwSuccess" hidden><h3 tabindex="-1">Conta cadastrada</h3><p id="fxcwSuccessText"></p><p>O cadastro não constitui autorização para operar. Prepare ou selecione um período para utilizar esta conta na Execution Board.</p><button type="button" id="fxcwPrepare">Preparar ou selecionar período</button></section>
      </div>
      <p id="fxcRegistrationStatus" class="fxcw-status" role="status" aria-live="polite"></p>
      <div id="fxcwDiscard" class="fxcw-discard" hidden role="group" aria-labelledby="fxcwDiscardTitle"><h3 id="fxcwDiscardTitle">Fechar esta ficha?</h3><p id="fxcwDiscardText"></p><button type="button" id="fxcwKeep">Continuar preenchendo</button><button type="button" id="fxcwDiscardConfirm">Descartar ficha e fechar</button></div>
      <footer id="fxcwFooter"><button type="button" id="fxcRegistrationCancel">Cancelar</button><span class="fxcw-footer-spacer"></span><button type="button" id="fxcwBack" hidden>Voltar</button><button type="button" id="fxcwNext">Continuar</button><button type="submit" id="fxcRegistrationSave" hidden>${creating?'Cadastrar conta':'Salvar alterações'}</button></footer>
    </form>`;
    const view=registrationView;
    const profileHelp=()=>{const key=el('fxcr-profileKey').value;el('fxcwProfileHelp').textContent=key?riskProfileByAny(key).desc:'Escolha explícita, sem perfil automático. Períodos antigos sem referência continuarão identificados como pendentes.';};
    el('fxcr-profileKey').onchange=profileHelp;profileHelp();
    el('fxcr-currency').addEventListener('input',event=>{event.target.value=event.target.value.toUpperCase();});
    function validateStep(step){
      const section=registrationDialog.querySelector(`[data-fxcw-step="${step}"]`);
      if(!section)return true;
      const currency=el('fxcr-currency');currency.setCustomValidity(currency.value&&!/^[A-Z]{3}$/.test(currency.value)?'Use o código de moeda com três letras maiúsculas.':'');
      const reason=el('fxcr-profileReason');reason.required=!!draft.profileKey&&el('fxcr-profileKey').value!==draft.profileKey;
      for(const input of section.querySelectorAll('input,select'))if(!input.checkValidity()){input.reportValidity();return false;}
      return true;
    }
    function showStep(step,focus=true){
      view.step=step;el('fxcRegistrationStatus').textContent='';el('fxcwProgressLabel').textContent='Etapa '+(step+1)+' de 5 · '+steps[step];
      registrationDialog.querySelectorAll('[data-fxcw-step]').forEach(section=>{const active=Number(section.dataset.fxcwStep)===step;section.hidden=!active;section.inert=!active;});
      registrationDialog.querySelectorAll('[data-fxcw-progress]').forEach(item=>{if(Number(item.dataset.fxcwProgress)===step)item.setAttribute('aria-current','step');else item.removeAttribute('aria-current');});
      el('fxcwBack').hidden=step===0;el('fxcwNext').hidden=step===4;el('fxcRegistrationSave').hidden=step!==4;
      if(step===4){const v=registrationValues();el('fxcwReview').innerHTML=[['Identificação',v.name+' · '+v.login,1],['Tipo',v.type,1],['Plataforma',v.platform,2],['Corretora',v.broker||'Pendente',2],['Servidor',v.server||'Não informado',2],['Moeda',v.currency||'Pendente · confirmar na preparação do período',2],['Ambiente',({'real':'Real','demo':'Demo','unknown':'Desconhecido declarado'})[v.accountEnvironment]||'Não informado',2],['Perfil para próximo período',v.profileKey?riskProfileByAny(v.profileKey).name:'Pendente · sem atribuição versionada',3]].map(([label,value,target])=>`<div><dt>${label}</dt><dd>${safe(value)}</dd><button type="button" data-fxcw-edit="${target}" aria-label="Editar ${label.toLowerCase()}">Editar</button></div>`).join('');}
      el('fxcwWork').scrollTop=0;
      if(focus)registrationDialog.querySelector(`[data-fxcw-step="${step}"] h3`).focus({preventScroll:true});
    }
    el('fxcwNext').onclick=()=>{if(validateStep(view.step))showStep(view.step+1);};
    el('fxcwBack').onclick=()=>showStep(Math.max(0,view.step-1));
    el('fxcwReview').onclick=event=>{const button=event.target.closest('[data-fxcw-edit]');if(button)showStep(Number(button.dataset.fxcwEdit));};
    el('fxcRegistrationCancel').onclick=requestRegistrationClose;el('fxcwClose').onclick=requestRegistrationClose;
    el('fxcwKeep').onclick=requestRegistrationClose;el('fxcwDiscardConfirm').onclick=closeRegistration;
    el('fxcRegistrationForm').onsubmit=async event=>{
      event.preventDefault();if(!available())return;if(registrationView!==view||view.saving||view.saved||view.unknown||view.confirmingClose)return;
      if(view.step<4){el('fxcwNext').click();return;}
      for(let step=1;step<5;step++){
        if(![...registrationDialog.querySelectorAll(`[data-fxcw-step="${step}"] input,[data-fxcw-step="${step}"] select`)].every(input=>input.checkValidity())){showStep(step);validateStep(step);return;}
      }
      const input=registrationValues();view.saving=true;
      registrationDialog.querySelectorAll('button').forEach(button=>button.disabled=true);
      el('fxcRegistrationStatus').textContent='Confirmando cadastro…';
      try{
        const result=await FX.saveRegistration(view.token,input,{confirmHistorical:el('fxcr-history')?.checked===true});
        if(registrationView!==view)return;
        if(!result.ok){el('fxcRegistrationStatus').textContent=result.error||'Cadastro não confirmado.';view.unknown=result.persistido===null;return;}
        view.saved=true;view.result=result;
        if(typeof renderContas==='function')renderContas();
        if(view.onSaved){const callback=view.onSaved;closeRegistration();callback(result);return;}
        registrationDialog.querySelectorAll('[data-fxcw-step]').forEach(section=>{section.hidden=true;section.inert=true;});
        el('fxcwSuccess').hidden=false;el('fxcwSuccessText').textContent='Cadastro confirmado. A preparação do período é uma etapa separada; a conta operacional foi preservada.';
        el('fxcRegistrationStatus').textContent='Gravação confirmada.';el('fxcwBack').hidden=true;el('fxcwNext').hidden=true;el('fxcRegistrationSave').hidden=true;
        el('fxcRegistrationCancel').textContent='Fechar';el('fxcwSuccess').querySelector('h3').focus();
      }catch(error){if(registrationView===view)el('fxcRegistrationStatus').textContent='Cadastro não confirmado. Confira a sessão.';}
      finally{if(registrationView===view){view.saving=false;registrationDialog.querySelectorAll('button').forEach(button=>button.disabled=false);el('fxcRegistrationSave').disabled=!!view.unknown||view.saved;}}
    };
    el('fxcwPrepare').onclick=()=>{if(!view.saved||!view.result)return;const id=view.result.accountId;closeRegistration();openAccountSetup({accountId:id,returnFocus});};
    view.initial=JSON.stringify(registrationValues());showStep(0,false);registrationDialog.showModal();registrationDialog.querySelector('[data-fxcw-step="0"] h3').focus();
  }
  function openImport({accountId=null,returnFocus=document.activeElement}={}){
    if(!available())return false;
    const started=FX.beginImportReview();if(!started.ok){alert(started.error);return;}
    cancel();if(accountId)ui.accountId=accountId;
    ui.source='mt5';window.JPWNavigation?.navigate('forex-consolidated');render();
    el('fxcImport').hidden=false;el('fxcFile').focus();
    el('fxcCancelImport').onclick=()=>{cancel();el('fxcImport').hidden=true;(returnFocus?.isConnected&&returnFocus.getClientRects().length?returnFocus:el('fxcOpenImport')).focus();};
  }
  let setupDialog=null,setupView=null;
  function setupValues(){
    return JSON.stringify([...setupDialog.querySelectorAll('form:not([hidden]) input,form:not([hidden]) select')].filter(input=>!input.disabled).map(input=>[input.id,input.type==='checkbox'?input.checked:input.value]));
  }
  function confirmSetupDiscard(){
    if(!setupView)return true;
    if(!setupView.unknown&&setupValues()===setupView.initial)return true;
    return confirm(setupView.unknown?'O resultado da gravação está indeterminado. Fechar não desfaz uma eventual gravação; confira a base antes de repetir. Deseja fechar?':'Há preenchimento não confirmado. Descartar somente este preenchimento e fechar? As etapas já salvas serão preservadas.');
  }
  function closeSetup({force=false}={}){
    if(!force&&(setupView?.saving||!confirmSetupDiscard()))return false;
    FX.cancelAccountSetup?.();setupView=null;if(setupDialog?.open)setupDialog.close();return true;
  }
  function accountReport(accountId){
    const account=S.fxConsolidated?.accounts?.find(a=>a.id===accountId),snapshot=account?.summaries?.slice(-1)[0];
    return snapshot?{format:snapshot.format,identity:{login:account.login,broker:account.broker,currency:account.currency,server:account.server},
      period:snapshot.period,generatedAt:snapshot.generatedAt||null,summary:snapshot.values,orders:[],deals:[],positions:[],issues:[]}:null;
  }
  function openAccountSetup({accountId=null,report=null,returnFocus=document.activeElement}={}){
    if(!available())return false;
    if(setupView?.saving)return;
    if(setupDialog?.open){setupDialog.focus();return;}
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
      setupDialog.addEventListener('keydown',event=>{if(event.key==='Escape')event.stopPropagation();trapAccountDialogTab(event,setupDialog);});
      setupDialog.addEventListener('close',()=>{if(setupDialog.open)return;const target=setupDialog._returnFocus;FX.cancelAccountSetup?.();setupView=null;restoreAccountFocus(target);});
    }
    setupView={...prepared,saving:false};setupDialog._returnFocus=returnFocus;
    const suggestions=prepared.suggestions;
    const field=(id,label,type='text',value='',required=false)=>`<label>${label}<input id="${id}" type="${type}" ${type==='number'?'step="any"':''} value="${safe(value)}" ${required?'required':''}></label>`;
    setupDialog.innerHTML=`<header><h2 id="fxcSetupTitle">Preparar conta e período</h2><p>${safe(account.name||account.id)} · ${safe(account.login||'')} · ${safe(account.currency||'Moeda a confirmar')}</p></header><p>Cadastro, importação, período e observação são confirmações separadas. Fechar esta ficha preserva as etapas já salvas.</p>${suggestions?`<section class="fxc-setup-report"><h3>Valores do relatório</h3><dl class="fxc-statistics"><div><dt>Saldo informado</dt><dd>${safe(number(suggestions.balance,account.currency||''))}</dd></div><div><dt>Equity informado</dt><dd>${safe(number(suggestions.equity,account.currency||''))}</dd></div><div><dt>Referência do documento</dt><dd>${safe(suggestions.date||'Data não informada')}</dd></div></dl><p>Saldo e equity são fotografias da conta. Nenhum deles preenche o SI ou o saldo de abertura. Confirme a data e o fuso da observação antes de registrar.</p></section>`:''}<form id="fxcSetupPeriodForm"><h3>1. Período operacional</h3><label>Período<select id="fxcs-period"><option value="">Registrar novo período</option>${prepared.periods.map(p=>`<option value="${safe(p.periodId)}" ${p.periodId===prepared.currentPeriodId?'selected':''}>${safe(p.startedAt)} · ${safe(p.currency)} · SI ${safe(number(p.si))}</option>`).join('')}</select></label><div id="fxcs-new-period" class="fxc-registration-fields">${field('fxcs-start','Início do período','date','',true)}${field('fxcs-currency','Moeda','text',account.currency||'',true)}${field('fxcs-si','SI confirmado (capital inicial) · vazio = indisponível','number')}${field('fxcs-book','Saldo contábil na abertura · vazio = indisponível','number')}${field('fxcs-period-source','Fonte do período e capital','text','Declaração manual',true)}${field('fxcs-period-reason','Motivo do registro','text','Preparação explícita da conta',true)}<label class="fxc-check"><input id="fxcs-active" type="checkbox" checked> Tornar este o período atual da conta</label></div><label class="fxc-check"><input id="fxcs-confirm-period" type="checkbox" required> Conferi a conta, o período, a moeda e o SI informado ou indisponível.</label><button type="submit" id="fxcs-save-period">Confirmar período</button></form><form id="fxcSetupObservationForm" hidden><h3>2. Observação financeira</h3><p id="fxcs-period-summary"></p><p>Opcional para preencher as ordens. Os cálculos que dependem de fatos ausentes continuam indisponíveis. Registrar esta observação atualiza os fatos desta conta, sem trocar o contexto operacional em uso.</p><div class="fxc-registration-fields">${field('fxcs-equity','Equity observado','number',suggestions?.equity??'',true)}${field('fxcs-observed','Data e hora da observação · fuso deste dispositivo','datetime-local','',true)}${field('fxcs-observation-source','Fonte da observação','text',suggestions?.source||'Declaração manual',true)}${field('fxcs-rate','Conversão: 1 USD na moeda da conta','number')}${field('fxcs-cashflow','Fluxo líquido desde o SI · vazio = desconhecido','number')}${field('fxcs-observation-reason','Motivo do registro','text','Observação financeira revisada',true)}</div><label class="fxc-check"><input id="fxcs-cashflow-confirm" type="checkbox"> Conferi a cobertura do fluxo líquido informado (depósitos menos retiradas).</label><label class="fxc-check"><input id="fxcs-confirm-observation" type="checkbox" required> Conferi equity, fonte, data/hora e unidade. O relatório não comprova valores atuais.</label><button type="submit" id="fxcs-save-observation">Salvar observação financeira</button></form><p id="fxcSetupStatus" role="status" aria-live="polite"></p><footer><button type="button" id="fxcs-close">Fechar</button><button type="button" id="fxcs-open-orders" hidden>Ir para fases e ordens</button></footer>`;
    const updatePeriod=()=>{const existing=!!el('fxcs-period').value;el('fxcs-new-period').hidden=existing;el('fxcs-new-period').querySelectorAll('input').forEach(input=>input.disabled=existing);};
    el('fxcs-period').onchange=()=>{updatePeriod();el('fxcs-confirm-period').checked=false;};updatePeriod();
    const optional=id=>el(id).value.trim()===''?null:Number(el(id).value);
    const run=async(buttonId,command,success)=>{
      const view=setupView;if(!available()||!view||view.saving)return;view.saving=true;el(buttonId).disabled=true;el('fxcs-close').disabled=true;
      el('fxcSetupStatus').textContent='Confirmando a gravação…';
      try{const result=await command(view);if(setupView!==view)return;
        if(!result.ok){view.unknown=result.persistido===null;el('fxcSetupStatus').textContent=result.error||'Etapa não confirmada.';return;}
        success(result,view);view.initial=setupValues();if(typeof renderContas==='function')renderContas();
      }catch(error){if(setupView===view)el('fxcSetupStatus').textContent='Etapa não confirmada. Confira a sessão antes de continuar.';}
      finally{if(setupView===view){view.saving=false;el('fxcs-close').disabled=false;el(buttonId).disabled=!!view.unknown||view.completed===buttonId;}}
    };
    el('fxcSetupPeriodForm').onsubmit=event=>{event.preventDefault();run('fxcs-save-period',view=>FX.saveSetupPeriod(view.token,{periodId:el('fxcs-period').value||null,startedAt:el('fxcs-start').value,
      currency:el('fxcs-currency').value.trim().toUpperCase(),si:optional('fxcs-si'),openingBook:optional('fxcs-book'),source:el('fxcs-period-source').value,
      reason:el('fxcs-period-reason').value,activateCurrentPeriod:el('fxcs-active').checked,confirmPeriod:el('fxcs-confirm-period').checked}),(result,view)=>{
        window.JPWForex?.accountsUI?.examine?.(result.accountId,result.periodId);
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
      const view=setupView;if(!view?.periodId||view.saving||!confirmSetupDiscard())return;
      const use=window.JPWForex?.accountsUI?.useContext;
      if(typeof use!=='function'){el('fxcSetupStatus').textContent='Abra Contas e Período para selecionar o contexto confirmado.';return;}
      use(view.account.id,view.periodId,{onAccepted:()=>{if(setupView===view)closeSetup({force:true});}});
    };
    setupView.initial=setupValues();setupDialog.showModal();el('fxcs-period').focus();
  }
  async function confirmImport(){
    if(!available())return false;
    if(!ui.preview||ui.busy)return;if(!el('fxcConfirmIdentity').checked)return notify('Confirme a identidade antes da importação.','error');
    if(ui.preview.conflicts?.length&&!el('fxcAcceptRevision')?.checked)return notify('As divergências precisam de confirmação explícita.','error');
    ui.busy=true;const token=ui.token;const button=el('fxcConfirmImport');button.disabled=true;
    try{const result=await FX.confirmImport(ui.preview,{confirmIdentity:true,acceptRevision:!!el('fxcAcceptRevision')?.checked});if(token!==ui.token)return;if(!result?.ok){notify(result?.error?.message||result?.error||'Gravação não confirmada. A prévia foi preservada.','error');return;}ui.accountId=result.accountId||result.receipt?.accountId||ui.preview.account?.id||ui.accountId;const importedReport=ui.document?.report||ui.preview.report,importedAccountId=ui.accountId;ui.preview=null;ui.document=null;el('fxcPreview').replaceChildren();el('fxcImport').hidden=true;el('fxcImportResult').hidden=false;el('fxcImportResult').innerHTML='<div id="fxcImportNotice"><h3>Relatório conferido</h3><p>O histórico está disponível em Desempenho. Prepare separadamente o período e os fatos financeiros da conta para preencher as ordens.</p><button type="button" id="fxcDismissImportNotice">Dispensar aviso</button></div><button type="button" id="fxcPrepareAccount">Preparar conta e período</button>';el('fxcDismissImportNotice').onclick=()=>{el('fxcImportNotice').hidden=true;notify('');el('fxcPrepareAccount').focus();};el('fxcPrepareAccount').onclick=()=>openAccountSetup({accountId:importedAccountId,report:importedReport,returnFocus:el('fxcPrepareAccount')});notify((result.duplicate?'Relatório já existente; nenhum registro duplicado.':'Importação confirmada. Comprovante salvo na base local.')+(result.originalEvidence?' '+(result.originalEvidence.status==='CONFIRMED'?'Original preservado neste navegador; exporte o ZIP de evidências.':'Original não preservado: '+result.originalEvidence.reason):' Original indisponível: reassocie o mesmo arquivo pelo comprovante.'));render();}
    catch(error){if(token===ui.token)notify(error.message||String(error),'error');}
    finally{if(token===ui.token)ui.busy=false;if(button.isConnected)button.disabled=false;}
  }
  // Repainting read-only facts must not restart an inspection in the same
  // account/source/range. Keys identify disclosures and captured observations,
  // never their current DOM position or displayed monetary value.
  function capturePresentation(context){
    const same=context===presentationContext;presentationContext=context;
    if(!same)return null;
    const root=el('fxconsolidated'),active=document.activeElement;
    const details=[...root.querySelectorAll('[data-fxc-disclosure]')].filter(node=>node.open).map(node=>node.dataset.fxcDisclosure);
    const points=[...root.querySelectorAll('figure[data-fxc-series]')].map(figure=>({
      series:figure.dataset.fxcSeries,point:JSON.parse(figure.dataset.fxcPoints)[Number(figure.dataset.selectedPoint)]
    }));
    let focus=null;
    if(active?.closest('[id^="fxcPanel-"],#fxcNextAction')){
      if(active.id)focus='#'+CSS.escape(active.id);
      else if(active.matches('summary')&&active.parentElement.dataset.fxcDisclosure)
        focus='[data-fxc-disclosure="'+CSS.escape(active.parentElement.dataset.fxcDisclosure)+'"] > summary';
      else if(active.matches('.fxc-chart-prev,.fxc-chart-next'))
        focus='[data-fxc-series="'+CSS.escape(active.closest('figure').dataset.fxcSeries)+'"] .'+(active.matches('.fxc-chart-prev')?'fxc-chart-prev':'fxc-chart-next');
      else for(const attr of ['data-fxc-chart','data-fxc-month','data-fxc-month-mode','data-fxc-go','data-fxc-tab'])
        if(active.hasAttribute(attr)){focus='['+attr+'="'+CSS.escape(active.getAttribute(attr))+'"]';break;}
    }
    return {details,points,focus};
  }
  function restorePresentation(saved){
    if(!saved)return;
    const root=el('fxconsolidated');
    root.querySelectorAll('[data-fxc-disclosure]').forEach(node=>{node.open=saved.details.includes(node.dataset.fxcDisclosure);});
    for(const selected of saved.points){
      if(!selected.point)continue;
      const figure=root.querySelector('[data-fxc-series="'+CSS.escape(selected.series)+'"]');if(!figure)continue;
      const points=JSON.parse(figure.dataset.fxcPoints),p=selected.point;
      const index=points.findIndex(q=>q.date===p.date&&q.ticket===p.ticket&&(p.ticket!==null||q.index===p.index));
      if(index>=0)figure._fxcSelect?.(index,false);
    }
    const target=saved.focus&&root.querySelector(saved.focus);
    if(target&&!target.disabled&&!target.closest('[hidden],[inert]')&&target.getClientRects().length)target.focus({preventScroll:true});
  }
  function render(){
    mount();if(!ui.mounted)return;const accounts=FX.accounts?FX.accounts():[];if(ui.source==='manual'&&S.operationHistory?.schemaVersion===DEFAULTS.operationHistory.schemaVersion&&S.operationHistory?.records?.some(r=>!r.accountId))accounts.push({id:'unassigned',name:'Não conciliados — conta histórica ausente',archived:true});
    if(ui.accountId===null){const preferred=S.fxConsolidated?.defaultAccountId;const masters=accounts.filter(a=>a.type==='MESTRE');ui.accountId=preferred?(accounts.some(a=>a.id===preferred)?preferred:''):(masters.length===1?masters[0].id:'');}
    if(ui.accountId&&!accounts.some(a=>a.id===ui.accountId))ui.accountId='';
    const presentation=capturePresentation(JSON.stringify([jpWealthPersistenceEpoch(),ui.accountId,ui.source,ui.from,ui.to]));
    const select=el('fxcAccount');if(document.activeElement!==select)select.innerHTML=options(accounts,ui.accountId);
    const account=accounts.find(a=>a.id===ui.accountId)||null;
    let model={metrics:{},series:{},breakdowns:{},records:[],issues:[]};fullModel=null;
    try{
      if(ui.source==='manual'&&S.operationHistory?.schemaVersion!==DEFAULTS.operationHistory.schemaVersion)throw Error('Versão do histórico não suportada: conteúdo preservado sem interpretação.');
      if(FX.project&&account){
        const query={source:ui.source,accountId:account.id,account};
        fullModel=FX.project(S.fxConsolidated||FX.emptyState(),S.operationHistory?.records||[],query);
        if(ui.from&&ui.to&&ui.from>ui.to)throw Error('O início do período deve anteceder o fim.');
        model=ui.from||ui.to?FX.project(S.fxConsolidated||FX.emptyState(),S.operationHistory?.records||[],{...query,from:ui.from||null,to:ui.to||null}):fullModel;
      }
    }catch(error){model.issues=[{message:'Não foi possível calcular esta seleção: '+error.message}];}
    currentModel=model;model.account=model.account||account;el('fxcMt5').setAttribute('aria-pressed',String(ui.source==='mt5'));el('fxcManual').setAttribute('aria-pressed',String(ui.source==='manual'));
    const operational=window.JPWForex.state.operationalSelection(),context=window.JPWForex.state.accountContext(operational),operating=accounts.find(a=>a.id===operational.accountId);
    const nextMessage=!operational.accountId?'Cadastre ou escolha uma conta para preparar seu contexto.':context.status!=='OK'?'Confirme um período para a conta operacional.':'Contexto operacional identificado. Revise as pendências antes de registrar fatos.';
    const next=`<p>${safe(nextMessage)}</p><div class="eb-actions"><button type="button" data-fxc-go="forex-management-accounts">Contas e período</button>${context.status==='OK'?'<button type="button" data-fxc-go="forex-operation">Abrir Operação</button>':''}</div>`;
    el('fxcNextAction').innerHTML=context.status==='OK'?`<details data-fxc-disclosure="next-action"><summary>Próxima ação operacional</summary>${next}</details>`:`<div><strong>Preparar o contexto operacional</strong>${next}</div>`;
    const currency=projectedCurrency(model),coverage=model.coverage?.kind==='summary'?'Resumo do período':model.coverage?.completeHistory?'Histórico integral comprovado':model.coverage?.partial?'Histórico parcial':ui.source==='manual'&&model.records?.length?'Fechamentos locais':'Sem histórico calculável';
    const receipt=S.fxConsolidated?.receipts?.find(r=>r.id===model.coverage?.lastReceiptId);
    el('fxcIdentity').innerHTML=`<div class="fxc-context-identities"><div class="fxc-account-heading"><div><span class="fxc-context-label">Em análise</span><h2>${safe(account?.name||'Selecione uma conta')}</h2><p>${safe([account?.broker,account?.login].filter(Boolean).join(' · '))}${account?.currency&&account.currency!==currency?` · Cadastro: ${safe(account.currency)}`:''}${account?.archived?' · Conta histórica':''}</p></div></div><div class="fxc-operating-identity"><span class="fxc-context-label">Em operação</span><strong>${safe(operating?.name||operational.accountId||'Nenhuma conta selecionada')}</strong><small>${context.status==='OK'?'Período desde '+safe(declaredDate(context.value?.startedAt)||'data não informada'):'Período não confirmado'} · consulta independente</small></div></div><p class="fxc-selection-meta"><span>Fonte: ${ui.source==='manual'?'Manual':'MT5'}</span><span>Moeda: ${safe(currency||'não conciliada')}</span><span>Período: ${safe(declaredDate(model.period?.from||ui.from,true)||'início não informado')} → ${safe(declaredDate(model.period?.to||ui.to,true)||'fim não informado')}</span><span>${safe(coverage)}</span></p>`;
    const issues=(model.issues||[]).map(i=>i.message||i.code||String(i));
    renderOriginalEvidence(receipt,ui.token);
    el('fxcCoverage').textContent=(issues.length?issues.join(' · ')+'. ':'')+`Período declarado: ${declaredDate(model.period?.from||ui.from)||'início não informado'} → ${declaredDate(model.period?.to||ui.to)||'fim não informado'}. ${ui.source==='mt5'?'Importado: '+(declaredDate(receipt?.importedAt)||'não disponível')+'. ':''}Metodologia ${model.methodologyVersion||'não disponível'}. Fuso: ${model.period?.timezone&&model.period.timezone!=='unknown'?model.period.timezone:'não informado'}. MT5: custos assinados uma vez; contagem por deal de saída. Manual: resultado líquido capturado no encerramento. Saldo não equivale a equity. Consultar esta conta não altera a conta operacional.`;
    updatePeriodControls();
    panels(model);restorePresentation(presentation);notify(ui.message,ui.kind);
  }
  function settingsMarkup(){return `<div class="fxc-settings"><p>Escolha a conta aberta inicialmente no Consolidado FX. Esta preferência não altera a conta operacional.</p><label>Conta padrão<select id="fxcDefaultAccount"></select></label><button type="button" id="fxcSaveDefault">Salvar preferência</button><p id="fxcDefaultStatus" role="status" aria-live="polite"></p></div>`;}
  function bindSettings(){const select=el('fxcDefaultAccount');if(!select)return;select.innerHTML=options(FX.accounts?.()||[],S.fxConsolidated?.defaultAccountId||'',true);const button=el('fxcSaveDefault');button.onclick=async()=>{button.disabled=true;try{const result=await FX.saveDefaultAccount(select.value||null);el('fxcDefaultStatus').textContent=result?.ok?'Preferência salva.':(result?.error?.message||result?.error||'Não foi possível confirmar a preferência.');if(result?.ok){cancel();ui.accountId=null;render();}}catch(error){el('fxcDefaultStatus').textContent='Preferência não confirmada: '+(error.message||String(error));}finally{button.disabled=false;}};}
  function reset(){presentationContext=null;cancel();ui.accountId=null;ui.source='mt5';ui.tab='account';ui.from='';ui.to='';ui.search='';ui.preset='all';ui.historyFilter=null;ui.monthlyMode=null;ui.cashflows=false;ui.monthMessage='';ui.message='';for(const id of ['fxcFrom','fxcTo','fxcSearch','fxcFile'])if(el(id))el(id).value='';if(el('fxcImport'))el('fxcImport').hidden=true;render();}
  Object.assign(FX,{render,settingsMarkup,bindSettings,openAccountRegistration,openAccountSetup,openImport,reset});
  window.JPWFXConsolidatedUI={openAccountRegistration,openAccountSetup,openImport,
    resetWork:()=>{closeRegistration();closeSetup({force:true});},
    workState:()=>({pending:!!(ui.busy||ui.preview||registrationView||setupView),
      inflight:!!(ui.busy||registrationView?.saving||setupView?.saving),
      registration:registrationView?{saving:!!registrationView.saving,unknown:!!registrationView.unknown,saved:!!registrationView.saved}:null,
      setup:setupView?{saving:!!setupView.saving,unknown:!!setupView.unknown,completed:setupView.completed||null}:null})};
})(window.JPWFXConsolidated=window.JPWFXConsolidated||{});

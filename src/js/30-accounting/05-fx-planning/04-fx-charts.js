// ============ PLANEJAMENTO FX · GRÁFICOS (SVG sobre o cromo CH) ============
// Só desenho: recebe séries prontas do motor (02-fx-engine.js) e nunca calcula
// valor financeiro. Convenção visual herdada de drawRvpChart2: PROJETADO =
// linha tracejada, REALIZADO = linha sólida var(--f1) com área e pontos.
// Estado nunca é comunicado só por cor: legenda com marcadores, rótulo na
// transição histórico→projeção e resumo textual acompanham cada SVG.
// JPW-PNMKTS · P6 — as três séries também se separam pelo PADRÃO do traço, não
// apenas pela cor. Baseline e forecast usavam o mesmo dasharray "4 3" e só se
// distinguiam pelo matiz, o que quebrava para quem não separa violeta de âmbar:
//   realizado = sólido · baseline = tracejado longo (9 4) · forecast = pontilhado (2 3)
// Nenhuma série, escala ou valor muda — só o atributo de traço.
const FX_DASH_BASELINE='9 4';
const FX_DASH_FORECAST='2 3';

// Conversão de exibição USD→BRL, classificada por TEMPO (JPW-FGDEKM).
//
//   PASSADO   mês fechado com valuationFxRate própria → usa a dele. História
//             não se reprecifica com a referência de hoje.
//   PRESENTE  último mês fechado SEM taxa registrada → referência USD/BRL
//             corrente (10-domain/08-usd-brl-quote.js).
//   FUTURO    linhas de projeção → premissa projectedFxRate da série.
//
// Mês passado sem taxa registrada devolve null e some da curva: não existe taxa
// histórica para ele, e preencher com a premissa futura ou com a cotação de
// hoje seria inventar dado. Premissa futura NUNCA vale como valor presente —
// era exatamente esse vazamento que este ticket corrige.
// O custo médio de aquisição não entra aqui: é conceito contábil, não cotação.
function fxChartConvert(row,mode,ctx){
  if(!row || !Number.isFinite(row.close) || row.availability==='UNAVAILABLE' || row.availability?.close===false) return null;
  if(mode!=='brl') return row.close;
  const c=(ctx&&typeof ctx==='object')?ctx:{projectedRate:ctx};
  let rate;
  if(row.phase==='actual'){
    if(row.valuationFxRate>0) rate=row.valuationFxRate;                 // passado
    else if(c.presentMonth && row.month===c.presentMonth) rate=c.currentRate; // presente
    else rate=null;                                                      // sem taxa histórica
  } else rate=c.projectedRate;                                           // futuro
  const converted=rate>0?row.close*rate:null;
  return Number.isFinite(converted)?converted:null;
}

// Keep the calendar slots. A missing or unconfirmed month ends a segment;
// it must never be connected to a later observation across the gap.
function fxChartSegments(points){
  const segments=[]; let segment=[];
  for(const point of points){
    if(!Number.isFinite(point.y)){
      if(segment.length) segments.push(segment);
      segment=[]; continue;
    }
    if(segment.length && point.i!==segment[segment.length-1].i+1){
      segments.push(segment); segment=[];
    }
    segment.push(point);
  }
  if(segment.length) segments.push(segment);
  return segments;
}

// Presentation adapter: canonical rows stay authoritative. Comparison uses
// saved scenario assumptions, never a monthly draft or the scenario editor.
function fxScenarioFanModel(plan,ov,mode,{scenarioIds=[],baseline=false,reading='current'}={}){
  const previous=reading==='previous';
  const rows=Array.isArray(ov?.forecast)?ov.forecast:[];
  const months=rows.map(row=>row.month);
  const presentMonth=ov?.lastClosedMonth||null;
  const currentRate=typeof currentUsdBrlRate==='function'?currentUsdBrlRate():null;
  const ctx=projectedRate=>({projectedRate,currentRate,presentMonth});
  const firstProjection=rows.find(row=>row.phase!=='actual')?.month||null;
  const point=(row,context,visible=true)=>{
    const validState=row?.phase==='actual'?(!row.status||row.status==='FINALIZED')&&!!presentMonth&&row.month<=presentMonth:
      !['ABSENT','BLOCKED','REOPENED','REVIEW_REQUIRED','UNAVAILABLE'].includes(row?.status);
    const value=visible&&validState?fxChartConvert(row,mode,context):null;
    const reason=!visible?'Esta camada não contém um valor para este mês.':
      row?.reason||(!validState?(row?.phase==='actual'?'Realizado em revisão: não é um saldo confirmado.':'Projeção indisponível: confira o estado e as premissas na tabela.'):
        value===null&&(mode==='brl'&&Number.isFinite(row?.close))?'Taxa de conversão BRL indisponível para este mês.':
        value===null?'Saldo indisponível neste mês.':'');
    return {month:row?.month,value,state:visible?(row?.status||(row?.phase==='actual'?'FINALIZED':'PROJECTED')):'NOT_APPLICABLE',reason,
      origin:row?.phase==='actual'?(validState?'ACTUAL · registro confirmado':'ACTUAL · registro em revisão'):row?.phase==='scenario'?'SCENARIO · premissas salvas':'PLAN · premissas salvas'};
  };
  const currCtx=ctx(plan?.current?.projectedFxRate);
  const actual={id:'actual',kind:'actual',name:previous?'Realizado · leitura anterior':'Realizado confirmado',revision:plan?.updatedAt||'',points:rows.map(row=>point(row,currCtx,row.phase==='actual'))};
  const projected=(source,context)=>{
    const byMonth=new Map(source.map(row=>[row.month,row]));
    return months.map(month=>{
      const row=byMonth.get(month)||{month,close:null,status:'UNAVAILABLE',reason:'Mês fora da cobertura desta hipótese.'};
      // Only the last contiguous confirmed actual is an anchor. Reopened or
      // later recorded months do not gain validity from a neighboring value.
      return point(row,context,row.phase!=='actual'||!!firstProjection&&month===presentMonth||row.phase==='actual'&&row.status&&row.status!=='FINALIZED');
    });
  };
  const series=[actual,{id:'plan',kind:'plan',name:previous?'PLAN · leitura anterior':'PLAN · vigente',revision:plan?.updatedAt||'',points:projected(rows,currCtx)}];
  const selected=[...new Set(scenarioIds)].slice(0,2);
  for(const id of selected){
    const scenario=(plan?.scenarios||[]).find(item=>item.id===id);if(!scenario)continue;
    const scenarioRows=window.JPWFx.engine.fxScenarioTimeline(plan,scenario);
    const item={id:scenario.id,kind:'scenario',name:scenario.name||'Cenário sem nome',revision:scenario.updatedAt||scenario.createdAt||'',
      points:projected(scenarioRows,ctx(scenario.assumptions?.projectedFxRate))};
    item.points.forEach(p=>{if(p.origin.startsWith('PLAN'))p.origin='SCENARIO · '+item.name+' · premissas salvas';});
    series.push(item);
  }
  if(baseline){
    const item={id:'baseline',kind:'baseline',name:'Baseline original',revision:plan?.baseline?.frozenAt||'',
      points:months.map(month=>point((ov?.baseline||[]).find(row=>row.month===month)||{month,close:null,status:'UNAVAILABLE'},ctx(plan?.baseline?.projectedFxRate)))};
    item.points.forEach(p=>{p.origin='BASELINE original · versão congelada'+(item.revision?' em '+item.revision:'');});
    series.push(item);
  }
  if(previous)for(const item of series)for(const p of item.points){
    p.state+=' · leitura anterior';
    p.origin='Leitura anterior à gravação indeterminada · '+p.origin;
  }
  const money=value=>!Number.isFinite(value)?'indisponível':mode==='brl'
    ?'R$ '+value.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}):fmtMoney2(value);
  const parts=previous?['Leitura anterior à gravação indeterminada. A tentativa não foi confirmada; os valores abaixo não incluem sua atualização.']:[];
  if(presentMonth){
    const last=actual.points.find(p=>p.month===presentMonth);
    parts.push('Realizado até '+presentMonth+': '+money(last?.value)+'.');
    if(mode==='brl'&&last&&last.value===null&&Number.isFinite(ov.currentBalanceUsd))parts.push('Saldo confirmado de origem em USD: '+fmtMoney2(ov.currentBalanceUsd)+'. A conversão BRL está indisponível; a premissa futura não marca o realizado.');
  }else parts.push(rows.some(row=>row.phase==='actual')
    ?'Realizados em revisão: ainda não há sequência contígua reconfirmada. Confira os meses na tabela.'
    :'Nenhum mês fechado ainda — a série exibida é integralmente projeção condicional.');
  const finalMonth=months[months.length-1];
  if(finalMonth){
    const last=series[1].points.find(p=>p.month===finalMonth);
    parts.push('Fim do horizonte exibido ('+finalMonth+'): projeção vigente '+money(last?.value)+'.');
    for(const item of series.filter(item=>item.kind==='scenario'||item.kind==='baseline')){
      parts.push(item.name+': '+money(item.points.find(p=>p.month===finalMonth)?.value)+'.');
    }
  }
  const incomplete=rows.filter(row=>!Number.isFinite(row.close)||row.phase==='actual'&&row.status&&row.status!=='FINALIZED');
  if(incomplete.length)parts.push('Cobertura incompleta: '+incomplete.length+' mês(es) sem saldo confirmado ou projetável. As curvas não atravessam essas lacunas.');
  parts.push('A faixa entre hipóteses selecionadas compara saldos condicionais; não representa probabilidade ou intervalo de confiança.');
  parts.push('Depósitos integram o patrimônio: variação patrimonial não equivale a rentabilidade.');
  if(mode==='brl')parts.push('Cada trajetória usa sua própria premissa futura de câmbio; realizados conservam a valuation informada ou a referência corrente apenas no último mês fechado.');
  return {identity:plan?.id||'planning',revision:plan?.updatedAt||plan?.baseline?.frozenAt||'',
    unit:mode==='brl'?'BRL':'USD',title:previous?'Trajetórias patrimoniais · leitura anterior':'Trajetórias patrimoniais',months,series,readingStatus:previous?'PREVIOUS':'CURRENT',
    projectionStartMonth:firstProjection,origin:previous?'Planejamento patrimonial global · leitura anterior à tentativa de gravação indeterminada':'Planejamento patrimonial global · versões salvas',summary:parts.join(' ')};
}
function fxDrawMainChart(box,plan,ov,mode,options={}){
  if(!box)return;
  const model=fxScenarioFanModel(plan,ov,mode,options);
  if(!window.JPWScenarioFan){box.textContent='Visualização indisponível: o componente de trajetórias não foi carregado.';return;}
  window.JPWScenarioFan.render(box,model,{selectedMonth:options.selectedMonth,onInspect:options.onInspect,formatValue:value=>mode==='brl'
    ?'R$ '+value.toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}):fmtMoney2(value)});
}

// Taxa que converte a FOTOGRAFIA PRESENTE: a do próprio mês fechado quando o
// operador a registrou, senão a referência externa corrente. Nunca a premissa
// futura. null significa "não há taxa para o presente" — e aí o presente sai em
// USD, não numa conversão inventada.
function fxPresentRate(ov){
  const rec=ov.lastClosedMonth
    ? (ov.forecast||[]).find(r=>r.month===ov.lastClosedMonth&&r.phase==='actual')
    : null;
  if(rec && rec.valuationFxRate>0) return rec.valuationFxRate;
  const live=(typeof currentUsdBrlRate==='function')?currentUsdBrlRate():null;
  return live>0?live:null;
}
// Resumo textual do gráfico principal — alternativa acessível obrigatória.
function fxMainChartSummaryText(plan,ov,mode,options={}){
  return fxScenarioFanModel(plan,ov,mode,options).summary;
}

// Rentabilidade mensal: barras Planejado (baseline) × Realizado, meses fechados
// (janela das últimas 24). Sem mês fechado, mensagem — nunca série demonstrativa.
function fxDrawReturnsChart(box,ov){
  if(!box) return;
  window.JPWScenarioFan?.destroy(box);
  const baseByMonth={}; ov.baseline.forEach(r=>{baseByMonth[r.month]=r.rate;});
  const rows=ov.actual.filter(r=>Number.isFinite(r.rate)).slice(-24);
  if(!rows.length){ box.innerHTML='<p style="font-size:var(--fs-sm);color:var(--ink-faint)">Sem fechamentos ainda — as barras Planejado × Realizado aparecem a partir do primeiro mês fechado.</p>'; return; }
  // Razão 24:5 invariante (handoff spec §01): se não couber, o gráfico some
  // para dentro do disclosure — nunca é espremido.
  const W=720,H=150,L=CH.L,R=CH.R,T=CH.T,B=28;
  const vals=rows.flatMap(r=>[r.rate,baseByMonth[r.month],0]).filter(Number.isFinite);
  let ymin=Math.min(...vals), ymax=Math.max(...vals);
  const pad=(ymax-ymin)*0.15||0.005; ymin-=pad; ymax+=pad;
  const Y=v=>T+(1-(v-ymin)/((ymax-ymin)||1))*(H-T-B);
  const slot=(W-L-R)/rows.length, bw=Math.min(14,slot*0.32);
  const pctTxt=v=>(v*100).toFixed(2).replace('.',',')+'%';
  const bars=rows.map((r,i)=>{
    const x0=L+i*slot+slot/2, planned=baseByMonth[r.month], y0=Y(0);
    const bar=(v,x,color,hatch)=>{
      const y=Y(v), top=Math.min(y,y0), h=Math.abs(y0-y)||0.5;
      return `<rect x="${(x-bw/2).toFixed(1)}" y="${top.toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" fill="${color}" ${hatch?'opacity=".45"':''}/>`;
    };
    const label=i%Math.max(1,Math.round(rows.length/8))===0?`<text x="${x0.toFixed(1)}" y="${H-B+12}" font-size="8" fill="var(--ink-faint)" text-anchor="middle">${r.month}</text>`:'';
    return (Number.isFinite(planned)?bar(planned,x0-bw*0.55,'var(--violet)',true):'')+bar(r.rate,x0+bw*0.55,r.rate>=0?'var(--f1)':'var(--f4)')+label;
  }).join('');
  const grid=CH.gridY(W,L,R,Y,CH.ticks(ymin,ymax,4),pctTxt);
  const zero=`<line x1="${L}" x2="${W-R}" y1="${Y(0).toFixed(1)}" y2="${Y(0).toFixed(1)}" stroke="var(--ink-faint)" opacity=".6"/>`;
  const stats=CH.stats(L,T,[
    {mark:'▧',label:'Planejado (baseline)',value:'',color:'var(--violet)'},
    {mark:'█',label:'Realizado (+ / −)',value:'',color:'var(--f1)'},
  ],168);
  box.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Rentabilidade mensal: planejado versus realizado" style="width:100%;height:auto;font-family:var(--mono)">
    <rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}" fill="var(--bg)"/>
    ${grid}${zero}${bars}${stats}
  </svg>
  <details style="margin-top:6px"><summary style="cursor:pointer;font-size:var(--fs-sm);color:var(--ink-dim)">Valores mês a mês (texto)</summary>
    <p style="font-size:var(--fs-sm);color:var(--ink-dim);line-height:1.7">${rows.map(r=>`${r.month}: planejado ${Number.isFinite(baseByMonth[r.month])?pctTxt(baseByMonth[r.month]):'indisponível'}, realizado ${pctTxt(r.rate)}`).join(' · ')}</p>
  </details>`;
}

window.JPWFx.charts={fxDrawMainChart,fxDrawReturnsChart,fxMainChartSummaryText,fxChartConvert,fxPresentRate,fxChartSegments,fxScenarioFanModel};

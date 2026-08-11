// ============ PLANEJAMENTO FX · GRÁFICOS (SVG sobre o cromo CH) ============
// Só desenho: recebe séries prontas do motor (02-fx-engine.js) e nunca calcula
// valor financeiro. Convenção visual herdada de drawRvpChart2: PROJETADO =
// linha tracejada, REALIZADO = linha sólida var(--f1) com área e pontos.
// Baseline = violeta tracejado; forecast vigente = var(--f2) tracejado.
// Estado nunca é comunicado só por cor: legenda com marcadores, rótulo na
// transição histórico→projeção e resumo textual acompanham cada SVG.

// Conversão de exibição USD→BRL. Realizado usa a valuationFxRate do próprio mês
// quando registrada; na falta, cai na premissa vigente (aproximação sinalizada
// pelo chamador). Projeções usam a premissa de CADA série (baseline × current) —
// nunca o custo médio de aquisição, que é conceito contábil, não cotação.
function fxChartConvert(row,mode,fallbackRate){
  if(mode!=='brl') return row.close;
  const rate=(row.phase==='actual'&&row.valuationFxRate)?row.valuationFxRate:fallbackRate;
  return rate>0?row.close*rate:null;
}

function fxDrawMainChart(box,plan,ov,mode){
  if(!box) return;
  const brl=mode==='brl';
  const baseRate=plan.baseline.projectedFxRate||null;
  const currRate=plan.current.projectedFxRate||null;
  if(brl&&!(currRate>0)){
    box.innerHTML='<p style="font-size:var(--fs-sm);color:var(--ink-faint)">Defina a premissa de câmbio projetado (Planejamento) para visualizar em BRL.</p>';
    return;
  }
  const months=ov.forecast.map(r=>r.month);
  const n=months.length; if(!n){ box.innerHTML=''; return; }
  const basePts=ov.baseline.map((r,i)=>({i,y:fxChartConvert(r,mode,baseRate||currRate)})).filter(p=>p.y!=null);
  const series=ov.forecast.map((r,i)=>({i,y:fxChartConvert(r,mode,currRate),phase:r.phase})).filter(p=>p.y!=null);
  const actualPts=series.filter(p=>p.phase==='actual');
  // a projeção parte do último ponto real para a linha não abrir buraco visual
  const forecastPts=actualPts.length?series.slice(actualPts.length-1):series;
  const ys=[...basePts.map(p=>p.y),...series.map(p=>p.y)];
  let ymin=Math.min(...ys), ymax=Math.max(...ys);
  const pad=(ymax-ymin)*0.08||Math.max(1,ymax*0.02); ymin-=pad; ymax+=pad;
  const W=720,H=250,L=CH.L,R=CH.R,T=CH.T,B=CH.B;
  const X=i=>L+(n>1?i/(n-1):0)*(W-L-R);
  const Y=v=>T+(1-(v-ymin)/((ymax-ymin)||1))*(H-T-B);
  const path=pts=>pts.map((p,k)=>(k?'L':'M')+X(p.i).toFixed(1)+' '+Y(p.y).toFixed(1)).join(' ');
  const money=v=>brl?'R$'+Math.round(v).toLocaleString('pt-BR'):fmtMoney(v);
  const grid=CH.gridY(W,L,R,Y,CH.ticks(ymin,ymax,4),money);
  // eixo X: até 6 rótulos de mês igualmente espaçados
  const stepX=Math.max(1,Math.round(n/6));
  // rótulos presos ao quadro para não recortarem nas bordas do SVG
  const clampX=x=>Math.max(L+22,Math.min(W-R-22,x));
  const xLabels=months.map((m,i)=>i%stepX===0?`<text x="${clampX(X(i)).toFixed(1)}" y="${H-B+12}" font-size="8" fill="var(--ink-faint)" text-anchor="middle">${m}</text>`:'').join('');
  const lastIdx=actualPts.length?actualPts[actualPts.length-1].i:null;
  const transition=lastIdx!=null?`
    <line x1="${X(lastIdx).toFixed(1)}" x2="${X(lastIdx).toFixed(1)}" y1="${T}" y2="${H-B}" stroke="var(--ink-faint)" stroke-dasharray="2 3" opacity=".7"/>
    <text x="${Math.max(L+52,Math.min(W-R-52,X(lastIdx))).toFixed(1)}" y="${T-3}" font-size="8" fill="var(--ink-dim)" text-anchor="middle">histórico ⇥ projeção</text>`:'';
  const dots=actualPts.map(p=>`<circle cx="${X(p.i).toFixed(1)}" cy="${Y(p.y).toFixed(1)}" r="1.8" fill="var(--f1)"/>`).join('');
  const realArea=actualPts.length>1
    ?`<path d="${CH.area(path(actualPts),X(actualPts[0].i),X(actualPts[actualPts.length-1].i),H-B)}" fill="var(--f1)" opacity=".14"/>`:'';
  const endF=series[series.length-1], endB=basePts[basePts.length-1];
  const stats=CH.stats(L,T,[
    {mark:'─',label:'Realizado',value:actualPts.length?money(actualPts[actualPts.length-1].y):'—',color:'var(--f1)'},
    {mark:'┄',label:'Projeção vigente',value:endF?money(endF.y):'—',color:'var(--f2)'},
    {mark:'┄',label:'Baseline original',value:endB?money(endB.y):'—',color:'var(--violet)'},
  ],168);
  const callouts=(endF?CH.callout(W,R,Y(endF.y),money(endF.y),'var(--f2)'):'')
    +(actualPts.length?CH.callout(W,R,Y(actualPts[actualPts.length-1].y),money(actualPts[actualPts.length-1].y),'var(--f1)'):'');
  box.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Trajetória patrimonial: baseline, projeção vigente e realizado" style="width:100%;height:auto;font-family:var(--mono)">
    <rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}" fill="var(--bg)"/>
    ${grid}${xLabels}${transition}${realArea}
    <path d="${path(basePts)}" fill="none" stroke="var(--violet)" stroke-width="1" stroke-dasharray="4 3"/>
    <path d="${path(forecastPts)}" fill="none" stroke="var(--f2)" stroke-width="1" stroke-dasharray="4 3"/>
    ${actualPts.length>1?`<path d="${path(actualPts)}" fill="none" stroke="var(--f1)" stroke-width="1.2"/>`:''}${dots}
    ${callouts}${stats}
  </svg>`;
}

// Resumo textual do gráfico principal — alternativa acessível obrigatória.
function fxMainChartSummaryText(plan,ov,mode){
  const brl=mode==='brl';
  const cur=v=>brl?'R$ '+Math.round(v).toLocaleString('pt-BR'):fmtMoney2(v);
  const rate=brl?(plan.current.projectedFxRate||0):1;
  const endF=ov.forecast[ov.forecast.length-1], endB=ov.baseline[ov.baseline.length-1];
  const parts=[];
  if(ov.lastClosedMonth){
    parts.push(`Realizado até ${ov.lastClosedMonth}: ${cur(ov.currentBalanceUsd*(brl?rate:1))}.`);
    if(ov.baselineBalanceAtLastClose!=null)
      parts.push(`O baseline original previa ${cur(ov.baselineBalanceAtLastClose*(brl?rate:1))} para o mesmo mês (desvio ${cur((ov.deviationUsd||0)*(brl?rate:1))}).`);
    parts.push('A projeção futura parte do saldo efetivamente realizado, com as premissas vigentes.');
  } else parts.push('Nenhum mês fechado ainda — a série exibida é integralmente projeção condicional.');
  if(endF&&endB) parts.push(`Fim do horizonte (${endF.month}): projeção vigente ${cur(endF.close*(brl?rate:1))} × baseline ${cur(endB.close*(brl?rate:1))}.`);
  if(brl) parts.push('Conversão BRL pela premissa/valuation informadas — nunca pelo custo médio de aquisição.');
  return parts.join(' ');
}

// Rentabilidade mensal: barras Planejado (baseline) × Realizado, meses fechados
// (janela das últimas 24). Sem mês fechado, mensagem — nunca série demonstrativa.
function fxDrawReturnsChart(box,ov){
  if(!box) return;
  const baseByMonth={}; ov.baseline.forEach(r=>{baseByMonth[r.month]=r.rate;});
  const rows=ov.actual.filter(r=>Number.isFinite(r.rate)).slice(-24);
  if(!rows.length){ box.innerHTML='<p style="font-size:var(--fs-sm);color:var(--ink-faint)">Sem fechamentos ainda — as barras Planejado × Realizado aparecem a partir do primeiro mês fechado.</p>'; return; }
  const W=720,H=190,L=CH.L,R=CH.R,T=CH.T,B=28;
  const vals=rows.flatMap(r=>[r.rate,baseByMonth[r.month]||0,0]);
  let ymin=Math.min(...vals), ymax=Math.max(...vals);
  const pad=(ymax-ymin)*0.15||0.005; ymin-=pad; ymax+=pad;
  const Y=v=>T+(1-(v-ymin)/((ymax-ymin)||1))*(H-T-B);
  const slot=(W-L-R)/rows.length, bw=Math.min(14,slot*0.32);
  const pctTxt=v=>(v*100).toFixed(2).replace('.',',')+'%';
  const bars=rows.map((r,i)=>{
    const x0=L+i*slot+slot/2, planned=baseByMonth[r.month]||0, y0=Y(0);
    const bar=(v,x,color,hatch)=>{
      const y=Y(v), top=Math.min(y,y0), h=Math.abs(y0-y)||0.5;
      return `<rect x="${(x-bw/2).toFixed(1)}" y="${top.toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" fill="${color}" ${hatch?'opacity=".45"':''}/>`;
    };
    const label=i%Math.max(1,Math.round(rows.length/8))===0?`<text x="${x0.toFixed(1)}" y="${H-B+12}" font-size="8" fill="var(--ink-faint)" text-anchor="middle">${r.month}</text>`:'';
    return bar(planned,x0-bw*0.55,'var(--violet)',true)+bar(r.rate,x0+bw*0.55,r.rate>=0?'var(--f1)':'var(--f4)')+label;
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
    <p style="font-size:var(--fs-sm);color:var(--ink-dim);line-height:1.7">${rows.map(r=>`${r.month}: planejado ${pctTxt(baseByMonth[r.month]||0)}, realizado ${pctTxt(r.rate)}`).join(' · ')}</p>
  </details>`;
}

window.JPWFx.charts={fxDrawMainChart,fxDrawReturnsChart,fxMainChartSummaryText,fxChartConvert};

// ============ GRÁFICOS · CROSSHAIR + TOOLTIP ============
// Camada puramente visual: lê séries já calculadas e desenha. Não altera nenhum
// número. Usada por todos os SVGs do painel para dar leitura numérica no hover.
//   cfg = {W,H,L,R,T,B,span, xLabel(xVal)->string,
//          series:[{name,color,pts:[{x,y}],fmt(y)->string}]}
function bindChartCrosshair(svg, cfg){
  if(!svg || !svg.parentNode) return;
  const host=svg.parentNode;
  if(getComputedStyle(host).position==='static') host.style.position='relative';

  const NS='http://www.w3.org/2000/svg';
  const g=document.createElementNS(NS,'g');
  g.setAttribute('pointer-events','none');
  g.style.display='none';
  const vline=document.createElementNS(NS,'line');
  vline.setAttribute('y1',cfg.T); vline.setAttribute('y2',cfg.H-cfg.B);
  vline.setAttribute('stroke','var(--violet)'); vline.setAttribute('stroke-width','1');
  vline.setAttribute('stroke-dasharray','2 2');
  g.appendChild(vline);
  const dots=cfg.series.map(s=>{
    const c=document.createElementNS(NS,'circle');
    c.setAttribute('r','2.5'); c.setAttribute('fill',s.color);
    c.setAttribute('stroke','var(--bg)'); c.setAttribute('stroke-width','1');
    g.appendChild(c); return c;
  });
  svg.appendChild(g);

  const tip=document.createElement('div');
  tip.className='chart-tip'; tip.style.display='none';
  host.appendChild(tip);

  const near=(pts,xv)=>{
    if(!pts||!pts.length) return null;
    let best=pts[0], bd=Math.abs(pts[0].x-xv);
    for(let i=1;i<pts.length;i++){ const d=Math.abs(pts[i].x-xv); if(d<bd){bd=d;best=pts[i];} }
    return best;
  };
  const move=e=>{
    const r=svg.getBoundingClientRect(); if(!r.width) return;
    const vx=(e.clientX-r.left)/r.width*cfg.W;
    if(vx<cfg.L || vx>cfg.W-cfg.R){ leave(); return; }
    const xv=(vx-cfg.L)/(cfg.W-cfg.L-cfg.R)*cfg.span;
    g.style.display=''; tip.style.display='block';
    vline.setAttribute('x1',vx.toFixed(1)); vline.setAttribute('x2',vx.toFixed(1));
    let rows='';
    cfg.series.forEach((s,i)=>{
      const p=near(s.pts,xv);
      if(!p){ dots[i].style.display='none'; return; }
      dots[i].style.display='';
      dots[i].setAttribute('cx',(cfg.L+(p.x/cfg.span)*(cfg.W-cfg.L-cfg.R)).toFixed(1));
      dots[i].setAttribute('cy',s.yPx(p.y).toFixed(1));
      rows+=`<div class="r"><i style="background:${s.color}"></i><span>${esc(s.name)}</span><b>${esc(s.fmt(p.y))}</b></div>`;
    });
    tip.innerHTML=`<div class="h">${esc(cfg.xLabel(xv))}</div>${rows}`;
    // mantém o tooltip dentro do host
    const half=tip.offsetWidth/2, px=(vx/cfg.W)*r.width;
    tip.style.left=Math.max(half+2, Math.min(r.width-half-2, px))+'px';
  };
  const leave=()=>{ g.style.display='none'; tip.style.display='none'; };
  svg.addEventListener('mousemove',move);
  svg.addEventListener('mouseleave',leave);
}

function renderDashCharts(){
  const box=$('dashCharts'); if(!box) return;
  const saldoIni=S.params.saldoIni||0;
  const led=ledgerSorted();
  const proj=acctProjection(), m=proj.m;
  const start=proj.start, today=todayISO();
  const dOff=iso=>(new Date(iso+'T00:00:00')-start)/86400000;
  const projLast=proj.rows.length?dOff(proj.rows[proj.rows.length-1].iso):1;
  const realLast=led.length?dOff(led[led.length-1].data):0;
  const span=Math.max(projLast, realLast, 1);
  const projPts=proj.rows.map(r=>({x:dOff(r.iso), y:r.close})).filter(p=>p.x>=0&&p.x<=span);
  const realPts=(saldoIni>0?[{x:0,y:saldoIni}]:[]).concat(
    led.map(e=>({x:dOff(e.data), y:+e.saldo||0})).filter(p=>p.x>=0&&p.x<=span));
  // drawdown real (underwater): pico corrente desde o saldo inicial
  let peak=saldoIni; const ddPts=[{x:0,y:0}];
  led.forEach(e=>{ const b=+e.saldo||0; if(b>peak)peak=b; const dd=peak>0?(b-peak)/peak:0; ddPts.push({x:dOff(e.data), y:dd}); });
  // métricas
  const balNow=led.length?(+led[led.length-1].saldo||0):saldoIni;
  const lucroAcum=balNow-saldoIni;
  const evolPct=saldoIni>0?lucroAcum/saldoIni:0;
  const ddAtual=ddPts.length?ddPts[ddPts.length-1].y:0;
  const ddMaxReal=ddPts.reduce((a,p)=>Math.min(a,p.y),0);
  // Geometria dos gráficos, preenchida pelos geradores e consumida pelo crosshair.
  const chartCfgs={};
  // ---- SVG 1: evolução patrimonial (real) vs expectativa (projeção)
  function svgMoney(){
    const ys=[...projPts.map(p=>p.y),...realPts.map(p=>p.y),saldoIni,m.saldoFim].filter(v=>isFinite(v));
    let ymin=Math.min(...ys), ymax=Math.max(...ys);
    const pad=(ymax-ymin)*0.08||Math.max(1,ymax*0.02); ymin-=pad; ymax+=pad;
    const W=720,H=210,L=CH.L,R=CH.R,T=CH.T,B=CH.B;
    const X=x=>L+(x/span)*(W-L-R), Y=y=>T+(1-(y-ymin)/((ymax-ymin)||1))*(H-T-B);
    const path=pts=>pts.map((a,i)=>(i?'L':'M')+X(a.x).toFixed(1)+' '+Y(a.y).toFixed(1)).join(' ');
    const grid=CH.gridY(W,L,R,Y,CH.ticks(ymin,ymax,4),fmtMoney);
    const todayX=dOff(today);
    // Limite crítico no gráfico de patrimônio: saldo abaixo do qual o MDD
    // estatutário é violado (pico corrente × (1 − MDD)). Só leitura de limite.
    const mddLimit=activeMDDLimit()||0.15;
    const peakAll=Math.max(saldoIni, ...realPts.map(p=>p.y));
    const floorVal=peakAll*(1-mddLimit);
    const floorLine=(floorVal>ymin&&floorVal<ymax)
      ? CH.limit(W,L,R,Y(floorVal),'PISO MDD '+fmtMoney(floorVal),'var(--f4)') : '';
    // Área preenchida sob a curva real — a série primária ganha corpo.
    const realArea=realPts.length>1
      ? `<path d="${CH.area(path(realPts),X(realPts[0].x),X(realPts[realPts.length-1].x),H-B)}" fill="var(--f1)" opacity=".14"/>` : '';
    // Bloco de estatísticas: último, máximo, média, mínimo da série real.
    const ysReal=realPts.map(p=>p.y);
    const stats=ysReal.length ? CH.stats(L,T,[
      {mark:'□', label:'Último',  value:fmtMoney(ysReal[ysReal.length-1]),                     color:'var(--f1)'},
      {mark:'↑', label:'Máximo',  value:fmtMoney(Math.max(...ysReal)),                          color:'var(--data-num)'},
      {mark:'–', label:'Média',   value:fmtMoney(ysReal.reduce((a,b)=>a+b,0)/ysReal.length),    color:'var(--data-drv)'},
      {mark:'↓', label:'Mínimo',  value:fmtMoney(Math.min(...ysReal)),                          color:'var(--data-num)'},
    ]) : '';
    // Caixas de cotação no eixo direito.
    const lastReal=realPts.length?realPts[realPts.length-1]:null;
    const lastProj=projPts.length?projPts[projPts.length-1]:null;
    const callouts=(lastProj?CH.callout(W,R,Y(lastProj.y),fmtMoney(lastProj.y),'var(--violet)'):'')
                 + (lastReal?CH.callout(W,R,Y(lastReal.y),fmtMoney(lastReal.y),'var(--f1)'):'');
    chartCfgs.money={W,H,L,R,T,B,span,
      xLabel:xv=>fmtDateEU(dateISO(new Date(start.getTime()+xv*86400000))),
      series:[
        {name:'Expectativa', color:'var(--violet)', pts:projPts, yPx:Y, fmt:fmtMoney2},
        {name:'Real',        color:'var(--f1)',    pts:realPts, yPx:Y, fmt:fmtMoney2},
      ]};
    return `<svg id="chMoney" viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;font-family:var(--mono)">
      <rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}" fill="var(--bg)"/>
      ${grid}
      ${floorLine}
      ${todayX>=0&&todayX<=span?`<line x1="${X(todayX).toFixed(1)}" x2="${X(todayX).toFixed(1)}" y1="${T}" y2="${H-B}" stroke="var(--ink-faint)" stroke-dasharray="2 3" opacity=".6"/>`:''}
      ${realArea}
      ${projPts.length?`<path d="${path(projPts)}" fill="none" stroke="var(--violet)" stroke-width="1" stroke-dasharray="4 3"/>`:''}
      ${realPts.length>1?`<path d="${path(realPts)}" fill="none" stroke="var(--f1)" stroke-width="1.2"/>`:''}
      ${callouts}
      ${stats}
    </svg>`;
  }
  // ---- SVG 2: drawdown (underwater) — % abaixo do pico, com linha do MDD estatutário
  function svgDD(){
    if(ddPts.length<=1) return '<p style="font-size:var(--fs-sm);color:var(--ink-faint);margin:6px 0">Sem fechamentos ainda — a curva de drawdown aparece a partir do primeiro lançamento.</p>';
    const W=720,H=150,L=CH.L,R=CH.R,T=CH.T,B=CH.B;
    const mddLimit=activeMDDLimit()||0.15;
    const alarmLimit=activeAlarmLimit()||0.13;
    let dmin=ddPts.reduce((a,p)=>Math.min(a,p.y),0); dmin=Math.min(dmin,-mddLimit)*1.05;
    const X=x=>L+(x/span)*(W-L-R), Y=y=>T+(1-(y-dmin)/((0-dmin)||1))*(H-T-B);
    const path=ddPts.map((a,i)=>(i?'L':'M')+X(a.x).toFixed(1)+' '+Y(a.y).toFixed(1)).join(' ');
    const grid=CH.gridY(W,L,R,Y,CH.ticks(dmin,0,3),v=>(v*100).toFixed(1).replace('.',',')+'%');
    const ddNow=ddPts[ddPts.length-1].y, ddMin=Math.min(...ddPts.map(p=>p.y));
    const stats=CH.stats(L,T,[
      {mark:'□', label:'DD atual', value:fmtPct(ddNow), color:'var(--f4)'},
      {mark:'↓', label:'DD máximo',value:fmtPct(ddMin), color:'var(--f4)'},
      {mark:'–', label:'Alarme',   value:fmtPct(-alarmLimit), color:'var(--f2)'},
    ]);
    chartCfgs.dd={W,H,L,R,T,B,span,
      xLabel:xv=>fmtDateEU(dateISO(new Date(start.getTime()+xv*86400000))),
      series:[{name:'Drawdown', color:'var(--f4)', pts:ddPts, yPx:Y, fmt:v=>fmtPct(v)}]};
    return `<svg id="chDD" viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;font-family:var(--mono)">
      <rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}" fill="var(--bg)"/>
      ${grid}
      ${CH.limit(W,L,R,Y(-alarmLimit),'ALARME '+fmtPct(alarmLimit),'var(--f2)')}
      ${CH.limit(W,L,R,Y(-mddLimit),'MDD '+fmtPct(mddLimit),'var(--f4)')}
      <path d="${CH.area(path,X(ddPts[0].x),X(ddPts[ddPts.length-1].x),Y(0))}" fill="var(--f4)" opacity=".16"/>
      <path d="${path}" fill="none" stroke="var(--f4)" stroke-width="1.2"/>
      ${CH.callout(W,R,Y(ddNow),fmtPct(ddNow),'var(--f4)')}
      ${stats}
    </svg>`;
  }
  // ---- comparação mensal: expectativa (meta mensal do perfil) vs realizado
  const fimDoMes={}; led.forEach(e=>{ fimDoMes[e.data.slice(0,7)]=+e.saldo||0; });
  const keys=Object.keys(fimDoMes).sort(); let prev=saldoIni, mrows='';
  keys.forEach(k=>{
    const realRet=prev>0?fimDoMes[k]/prev-1:0, esperRet=m.metaMes, delta=realRet-esperRet;
    mrows+=`<tr><td class="hl">${esc(k)}</td><td style="text-align:right">${(esperRet*100).toFixed(2).replace('.',',')}%</td><td style="text-align:right"><span class="${realRet>=0?'pos':'neg'}">${(realRet*100).toFixed(2).replace('.',',')}%</span></td><td style="text-align:right"><span class="${delta>=0?'pos':'neg'}">${(delta*100).toFixed(2).replace('.',',')}%</span></td></tr>`;
    prev=fimDoMes[k];
  });
  const table=mrows?`<table class="dtable" style="margin-top:14px;max-width:520px">
    <thead><tr><th>Mês</th><th class="num">Esperado</th><th class="num">Real</th><th class="num">Δ real−esper.</th></tr></thead>
    <tbody>${mrows}</tbody></table>`:'';
  box.innerHTML=`<div class="metrics">
    <div class="metric ${lucroAcum>=0?'f1':'f4'}"><div class="k">Lucro acumulado</div><div class="v sm" style="color:${lucroAcum>=0?'var(--f1)':'var(--f4)'}">${fmtMoney2(lucroAcum)}</div></div>
    <div class="metric ${evolPct>=0?'f1':'f4'}"><div class="k">Evolução %</div><div class="v sm" style="color:${evolPct>=0?'var(--f1)':'var(--f4)'}">${(evolPct*100).toFixed(2).replace('.',',')}%</div></div>
    <div class="metric ${ddAtual<0?'f4':''}"><div class="k">Drawdown atual</div><div class="v sm" style="color:${ddAtual<0?'var(--f4)':'var(--ink)'}">${(ddAtual*100).toFixed(2).replace('.',',')}%</div></div>
    <div class="metric ${ddMaxReal<0?'f4':''}"><div class="k">Drawdown máx</div><div class="v sm" style="color:${ddMaxReal<0?'var(--f4)':'var(--ink)'}">${(ddMaxReal*100).toFixed(2).replace('.',',')}%</div></div>
  </div>
  <div class="chart-box" style="margin-top:14px"><div class="chart-cap">Evolução patrimonial · expectativa vs real</div>${svgMoney()}</div>
  <div class="chart-box" style="margin-top:16px"><div class="chart-cap">Drawdown (underwater)</div>${svgDD()}</div>
  ${table}
  ${realPts.length>1?'':'<p style="font-size:var(--fs-sm);color:var(--ink-faint);margin-top:10px">Sem fechamentos ainda — a linha de expectativa já aparece; a curva real surge ao registrar o primeiro fechamento diário (aba 07 Contabilidade).</p>'}`;
  // Crosshair só depois do innerHTML — os nós precisam existir no DOM.
  if(chartCfgs.money) bindChartCrosshair(box.querySelector('#chMoney'), chartCfgs.money);
  if(chartCfgs.dd)    bindChartCrosshair(box.querySelector('#chDD'),    chartCfgs.dd);
}

// ---- Checklist ----
function renderCheck(){
  const cont=$('checkContainer');
  cont.innerHTML=S.checklist.map((g,gi)=>{
    const items=g.items.map((it,ii)=>`<div class="check-item">
        <span class="ci-label">${esc(it.label)}</span>
        <div class="seg" data-g="${gi}" data-i="${ii}">
          ${[0,1,2].map(n=>`<button class="${it.v===n?'on':''}" data-v="${n}">${n}</button>`).join('')}
        </div></div>`).join('');
    return `<div class="check-group"><div class="gh">${esc(g.group)}</div>${items}</div>`;
  }).join('');
  cont.querySelectorAll('.seg button').forEach(b=>b.addEventListener('click',()=>{
    const seg=b.parentElement; const gi=+seg.dataset.g, ii=+seg.dataset.i, v=+b.dataset.v;
    S.checklist[gi].items[ii].v=v;
    seg.querySelectorAll('button').forEach(x=>x.classList.toggle('on',+x.dataset.v===v));
    save(); computeCheck();
  }));
  computeCheck();
}
function computeCheck(){
  let score=0,max=0;
  S.checklist.forEach(g=>g.items.forEach(it=>{score+=it.v; max+=2;}));
  $('chScore').textContent=score; $('chMax').textContent='de '+max;
  let cls,col;
  if(score>=24){cls='SETUP A+ — confiança estrutural';col='var(--f1)';}
  else if(score>=18){cls='EXPOSIÇÃO NORMAL — setup válido';col='var(--f1)';}
  else if(score>=12){cls='EXPOSIÇÃO REDUZIDA — só setups claros';col='var(--f2)';}
  else {cls='PROIBIDO OPERAR — contexto inconsistente';col='var(--f4)';}
  const el=$('chClass'); el.textContent=cls; el.style.color=col;
}

/* Calendar consultation. Stable controls and evidence remain useful without the map. */
(function (global) {
  'use strict';
  const LABELS = Object.freeze({continuous:'Aberta',preopen:'Pré-abertura',auction:'Em leilão',break:'Intervalo',extended:'Sessão estendida',closed:'Fechada',unknown:'Sem confirmação',mixed:'Sessões diferentes'});
  const GROUPS = {open:'Abertas agora',upcoming:'Próximas 24 horas',other:'Outras sessões',closed:'Fechadas',unknown:'Sem confirmação'};
  let helpSerial=0;
  function node(tag, text, cls) {
    const el=document.createElement(tag);
    if(text!==undefined)el.textContent=text;
    if(cls)el.className=cls;
    return el;
  }
  function hook(el, name) {el.dataset.mh=name;return el;}
  function time(utc, zone='UTC', dated=false, seconds=false) {
    return new Intl.DateTimeFormat('pt-BR',{timeZone:zone,...(dated ? {day:'2-digit',month:'2-digit',year:'numeric'}:{}),hour:'2-digit',minute:'2-digit',...(seconds ? {second:'2-digit'}:{}),hourCycle:'h23'}).format(utc);
  }
  function day(utc, zone) {return new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).format(utc);}
  function label(status) {
    if(status.phase!=='mixed')return LABELS[status.phase] || status.phase;
    if(global.JPWMarketSessions.isRegularOpen(status))return 'Parcialmente aberta';
    return [...new Set(status.groups.map(group=>LABELS[group.phase]))].join(' / ');
  }
  function groupFor(status) {return global.JPWMarketSessions.isRegularOpen(status) ? 'open':status.phase==='unknown' ? 'unknown':status.phase==='closed' ? 'closed':'other';}
  function symbol(status) {return {open:'●',other:'◐',closed:'○',unknown:'?'}[groupFor(status)];}
  function transition(value, zone, reference) {
    if(!value)return 'Próxima mudança não confirmada dentro da cobertura.';
    const window=value.earliestUtc!==value.latestUtc;
    const precision=window && (value.earliestUtc%60000!==0 || value.latestUtc%60000!==0);
    const stamp=utc=>time(utc,zone,day(utc,zone)!==day(reference,zone),precision);
    const next=LABELS[value.nextPhase] || value.nextPhase;
    if(window)return 'Janela para '+next+': '+stamp(value.earliestUtc)+'–'+stamp(value.latestUtc);
    const action=value.nextPhase==='continuous' ? 'Abre':value.nextPhase==='closed' ? 'Fecha':'Próxima fase: '+next;
    return action+' às '+stamp(value.earliestUtc);
  }
  function duration(milliseconds, seconds) {
    const total = seconds ? Math.ceil(milliseconds / 1000) : Math.ceil(milliseconds / 60000) * 60;
    const hours = Math.floor(total / 3600), minutes = Math.floor(total % 3600 / 60), remainder = total % 60;
    return (hours ? hours+'h':'')+(minutes ? minutes+'min':'')+(remainder ? remainder+'s':'') || '0s';
  }
  function opening(value, reference) {
    const action = value.kind === 'resume' ? 'Retoma' : 'Abre';
    if (value.earliestUtc <= reference && value.latestUtc > reference) return 'Janela de abertura em andamento';
    const earliest = value.earliestUtc - reference, latest = value.latestUtc - reference;
    const seconds = earliest % 60000 !== 0 || latest % 60000 !== 0;
    if (value.earliestUtc !== value.latestUtc) return action+' entre '+duration(earliest, seconds)+' e '+duration(latest, seconds);
    return action+' em '+duration(earliest, seconds);
  }
  function disclosure(name, title) {const el=hook(node('details'),name);el.append(node('summary',title));return el;}
  function createOverview(host, toggleExpansion, select, retry) {
    const root=node('section',undefined,'mh-overview-shell');root.setAttribute('aria-label','Mercados conforme calendário');
    const heading=node('div',undefined,'mh-overview-heading');
    const toggle=hook(node('button','Explorar bolsas e mapa'),'expansion-toggle');toggle.type='button';toggle.setAttribute('aria-expanded','false');
    toggle.addEventListener('click',toggleExpansion);
    const summary=hook(node('div',undefined,'mh-overview'),'summary');
    const counts=node('p',undefined,'mh-overview-counts'),openCount=hook(node('span'),'summary-open-count'),upcomingCount=hook(node('span'),'summary-upcoming-count'),unknownCount=hook(node('span'),'summary-unknown-count');
    counts.append(openCount,node('span',' · '),upcomingCount,node('span',' · '),unknownCount);
    const clock=hook(node('time',undefined,'mh-overview-note'),'summary-clock');clock.hidden=true;
    heading.append(clock,toggle);
    function section(label,name,emptyText) {
      const section=node('section',undefined,'mh-overview-section'),list=hook(node('ul',undefined,'mh-overview-list'),name),empty=node('p',emptyText,'mh-overview-note');
      section.append(node('h4',label),list,empty);return {section,list,empty,rows:new Map()};
    }
    const open=section('Abertas agora','summary-open-list','Nenhuma bolsa aberta agora conforme calendário.'),upcoming=section('Próximas 24 horas','summary-upcoming-list','Nenhuma abertura confirmada nas próximas 24 horas.');
    const status=node('p',undefined,'mh-overview-status');status.setAttribute('role','status');
    const retryButton=hook(node('button','Tentar carregar o calendário novamente'),'catalog-retry');retryButton.type='button';retryButton.hidden=true;retryButton.addEventListener('click',retry);
    const note=node('p','Conforme calendário de ações; sem cotações ou confirmação operacional.','mh-overview-note');
    counts.hidden=true;open.section.hidden=true;upcoming.section.hidden=true;summary.append(counts,open.section,upcoming.section,note);root.append(heading,summary,status,retryButton);host.append(root);
    function renderList(target,entries,catalog,snapshot) {
      const desired=entries.slice(0,3).map(entry=>{
        const venue=catalog.venues.find(v=>v.id===entry.id);let row=target.rows.get(entry.id);
        if(!row){const element=node('li'),button=node('button',venue.name),location=node('span',venue.city+' · '+venue.country,'mh-overview-location'),stamp=node('span',undefined,'mh-overview-time');button.type='button';button.dataset.mhSummaryVenue=entry.id;button.addEventListener('click',()=>select(entry.id));element.append(button,location,stamp);row={element,stamp};target.rows.set(entry.id,row);}
        const value=entry.nextRegularOpen;
        if(target===open)row.stamp.textContent=symbol(entry)+' '+label(entry)+' · '+transition(entry.nextTransition,venue.timeZone,snapshot.asOf)+' (hora local)';
        else{
          const dated=utc=>day(utc,venue.timeZone)!==day(snapshot.asOf,venue.timeZone),seconds=value.earliestUtc%60000!==0 || value.latestUtc%60000!==0;
          const stamp=utc=>time(utc,venue.timeZone,dated(utc),seconds),window=value.earliestUtc!==value.latestUtc;
          const action=value.kind==='resume' ? 'Retoma':'Abre',minutes=Math.max(1,Math.ceil((value.earliestUtc-snapshot.asOf)/60000));
          const waiting=value.earliestUtc<=snapshot.asOf && window ? 'Janela de abertura em andamento':action+' em cerca de '+minutes+' min';
          row.stamp.textContent=waiting+' · '+stamp(value.earliestUtc)+(window ? '–'+stamp(value.latestUtc):'')+' (hora local)';
        }
        return row.element;
      });
      const actual=Array.from(target.list.children);
      if(actual.length!==desired.length || desired.some((el,i)=>actual[i]!==el)){
        const focused=document.activeElement,keepFocus=desired.some(el=>el.contains(focused));
        if(actual.some(el=>el.contains(document.activeElement) && !desired.includes(el)))toggle.focus({preventScroll:true});
        actual.filter(el=>!desired.includes(el)).forEach(el=>el.remove());desired.forEach(el=>target.list.append(el));
        if(keepFocus && focused.isConnected && document.activeElement!==focused)focused.focus({preventScroll:true});
      }
      target.empty.hidden=entries.length>0;
    }
    return Object.freeze({root,summary,toggle,
      render(snapshot,catalog){
        const opened=snapshot.venues.filter(global.JPWMarketSessions.isRegularOpen),future=snapshot.venues.filter(v=>!global.JPWMarketSessions.isRegularOpen(v) && v.nextRegularOpen && v.nextRegularOpen.latestUtc>snapshot.asOf && v.nextRegularOpen.latestUtc<=snapshot.asOf+86400000);
        future.sort((a,b)=>a.nextRegularOpen.earliestUtc-b.nextRegularOpen.earliestUtc || a.nextRegularOpen.latestUtc-b.nextRegularOpen.latestUtc || catalog.venues.findIndex(v=>v.id===a.id)-catalog.venues.findIndex(v=>v.id===b.id));
        openCount.textContent=opened.length+' abertas agora';upcomingCount.textContent=future.length+' próximas 24 horas';unknownCount.textContent=snapshot.venues.filter(v=>v.phase==='unknown').length+' sem confirmação';
        counts.hidden=false;open.section.hidden=false;upcoming.section.hidden=false;clock.hidden=summary.hidden;clock.textContent='Agora · '+time(snapshot.asOf)+' UTC';clock.dateTime=new Date(snapshot.asOf).toISOString();clock.title='Referência: '+time(snapshot.asOf,'UTC',true)+' UTC';clock.setAttribute('aria-label',clock.title);
        renderList(open,opened,catalog,snapshot);renderList(upcoming,future,catalog,snapshot);
      },
      message(message,canRetry=false){status.textContent=message;status.hidden=!message;retryButton.hidden=!canRetry;},
      setExpanded(value,ready=true){root.dataset.expanded=String(value && ready);summary.hidden=value && ready;clock.hidden=value && ready || !clock.dateTime;toggle.textContent=value ? 'Recolher bolsas':'Explorar bolsas e mapa';toggle.setAttribute('aria-expanded',String(value && ready));},
      dispose(){root.remove();}
    });
  }
  function create(host, catalog, select, retryRenderer, mapVisibilityChanged) {
    const root=node('section',undefined,'market-hours');root.setAttribute('aria-label','Sessões das bolsas globais');
    const heading=node('div',undefined,'mh-heading');
    const summary=hook(node('h3',undefined,'mh-summary'),'summary');
    const clock=hook(node('time'),'clock');heading.append(summary,clock);
    const grid=node('div',undefined,'mh-grid'),list=node('div',undefined,'mh-list'),aside=node('div',undefined,'mh-aside');
    const filters=node('div',undefined,'mh-filters');
    const quickfilters=hook(node('div',undefined,'mh-quickfilters'),'quickfilters');quickfilters.setAttribute('role','group');quickfilters.setAttribute('aria-label','Filtrar bolsas');
    const quickButtons=new Map();
    ['open','all','unknown'].forEach(id=>{const b=node('button');b.type='button';b.dataset.mhQuick=id;b.setAttribute('aria-pressed',String(id==='open'));b.addEventListener('click',()=>{quick=id;visibility();});quickButtons.set(id,b);quickfilters.append(b);});
    const searchLabel=node('label',undefined,'mh-search-label');searchLabel.append(node('span','Pesquisar bolsa ou cidade','mh-search-caption'));
    const search=hook(node('input'),'search');search.type='search';search.placeholder='Buscar bolsa ou cidade';searchLabel.append(search);
    const phaseOptions=disclosure('phase-options','Filtrar por fase');
    const filterLabel=node('label','Fase da sessão');
    const filter=hook(node('select'),'filter');filter.append(new Option('Todas as fases','all'));
    Object.entries(LABELS).forEach(([id,text])=>filter.append(new Option(text,id)));filterLabel.append(filter);phaseOptions.append(filterLabel);
    filters.append(quickfilters,searchLabel,phaseOptions);
    const tableWrap=node('div',undefined,'mh-table-wrap'),table=node('table');
    table.append(node('caption','Bolsas · horários locais'));
    const head=node('thead'),header=node('tr');['Bolsa / cidade','Sessão','Hora local'].forEach(text=>{const th=node('th',text);th.scope='col';header.append(th);});head.append(header);table.append(head);
    const sections=new Map();
    Object.entries(GROUPS).forEach(([id,text])=>{const body=node('tbody');body.dataset.mhGroup=id;const tr=node('tr',undefined,'mh-section-heading'),th=node('th',text);th.colSpan=3;th.scope='rowgroup';tr.append(th);body.append(tr);sections.set(id,{body,title:th,heading:tr});table.append(body);});
    const upcomingEmptyRow=node('tr'),upcomingEmptyCell=node('td');upcomingEmptyCell.colSpan=3;
    const upcomingEmpty=hook(node('p','Nenhuma abertura confirmada nas próximas 24 horas','mh-note'),'upcoming-empty');
    upcomingEmptyCell.append(upcomingEmpty);upcomingEmptyRow.append(upcomingEmptyCell);sections.get('upcoming').body.append(upcomingEmptyRow);
    const rows=new Map();
    catalog.venues.forEach(v=>{
      const row=node('tr');row.dataset.venueId=v.id;
      const title=node('th');title.scope='row';
      const button=node('button',v.name);button.type='button';button.setAttribute('aria-pressed','false');button.addEventListener('click',()=>select(v.id,'table'));
      title.append(button,node('span',v.city+' · '+v.country,'mh-city'));
      const phase=node('td'),phaseLabel=node('span',undefined,'mh-phase'),next=node('span',undefined,'mh-next');phase.append(phaseLabel,next);
      const local=node('td',undefined,'mh-local');row.append(title,phase,local);sections.get('closed').body.append(row);
      row.addEventListener('click',event=>{if(event.target.closest('button,a,input,select,summary'))return;button.focus({preventScroll:true});select(v.id,'table');});
      rows.set(v.id,{row,button,phaseLabel,next,local,venue:v,order:rows.size});
    });
    tableWrap.append(table);
    const empty=hook(node('p','Nenhuma bolsa corresponde à pesquisa e aos filtros.','mh-note'),'empty');empty.hidden=true;empty.setAttribute('role','status');
    const detailDock=node('div');
    list.append(tableWrap,empty,detailDock);
    const globePanel=node('section',undefined,'mh-globe-panel');globePanel.setAttribute('aria-label','Mapa das bolsas');
    const mapToggle=hook(node('button','Explorar mapa'),'map-toggle');mapToggle.type='button';mapToggle.setAttribute('aria-expanded','false');
    const mapContent=hook(node('div'),'map-content');
    const globe=hook(node('div',undefined,'mh-globe'),'globe');
    const globeStatus=hook(node('p','Carregando globo local…','mh-note'),'globe-status');globeStatus.setAttribute('role','status');
    const globeRetry=hook(node('button','Tentar carregar o globo novamente'),'renderer-retry');globeRetry.type='button';globeRetry.hidden=true;
    globeRetry.addEventListener('click',()=>{focusSelected();if(retryRenderer)retryRenderer();});
    const mapCaption=node('div',undefined,'mh-map-caption');mapCaption.append(node('span','Mapa global'));
    mapContent.append(mapCaption,globe,globeStatus,globeRetry);
    globePanel.append(mapToggle,mapContent);
    const detail=node('section',undefined,'mh-detail');detail.setAttribute('aria-label','Detalhe da bolsa selecionada');
    const detailTitle=hook(node('h3'),'detail-title'),location=node('p',undefined,'mh-note'),state=node('p',undefined,'mh-detail-state');
    const localTime=hook(node('time',undefined,'mh-detail-time'),'detail-time');
    const identity=node('div',undefined,'mh-identity'),identityText=node('div');identityText.append(detailTitle,location);identity.append(identityText,localTime);
    const nextTransition=hook(node('p'),'next-transition');
    const outside=hook(node('div',undefined,'mh-selection-outside'),'selection-outside');outside.hidden=true;
    const showSelected=hook(node('button','Mostrar na lista'),'show-selected');showSelected.type='button';outside.append(node('span','Fora do filtro · '),showSelected);
    const cityVenues=hook(node('div',undefined,'mh-city-venues'),'city-venues');cityVenues.setAttribute('role','group');cityVenues.setAttribute('aria-label','Bolsas nesta cidade');
    const schedules=disclosure('schedules','Horários e segmentos'),sources=disclosure('sources','Fontes e cobertura');
    const scheduleBody=node('div'),sourceBody=node('div');schedules.append(scheduleBody);sources.append(sourceBody);
    detail.append(identity,state,nextTransition,outside,cityVenues,globePanel,schedules,sources);
    const inline=node('tr',undefined,'mh-inline-detail'),inlineCell=node('td');inlineCell.colSpan=3;inline.append(inlineCell);
    aside.append(detail);grid.append(list,aside);root.append(filters,heading,grid);host.append(root);
    let current=null,selected=null,quick='open',detailId=null,citySignature='',sourceSignature='',mobileExpanded=false,help=null;
    let compact=root.clientWidth<=800;
    const cityButtons=new Map(),groupNodes=new Map(),sourceLinks=new Map();
    // The global [i] system expands inline notes. These two scoped balloons use
    // the existing portal, without participating in global notes or dialogs.
    const titleRow=host.closest('.market-hours-tool')?.querySelector('.mh-title-row');
    const infoButtons=new Map();
    function infoButton(kind,label,anchor) {
      const button=hook(node('button','i','mh-info-button'),'info-button');button.type='button';button.dataset.mhHelp=kind;
      button.setAttribute('aria-label',label);button.setAttribute('aria-expanded','false');
      button.addEventListener('click',()=>openHelp(kind,button));anchor.append(button);infoButtons.set(kind,button);
    }
    infoButton('calendar','Sobre os horários das bolsas',titleRow || heading);
    if(!titleRow)heading.prepend(infoButtons.get('calendar'));
    infoButton('map','Sobre o mapa das bolsas',mapCaption);
    function closeHelp(returnFocus=false) {
      if(!help)return;
      const previous=help;help=null;previous.element.remove();
      previous.anchor.setAttribute('aria-expanded','false');previous.anchor.removeAttribute('aria-controls');
      document.removeEventListener('pointerdown',helpOutside,true);document.removeEventListener('keydown',helpKey,true);
      global.removeEventListener('resize',positionHelp);global.removeEventListener('scroll',positionHelp,true);
      if(global.visualViewport){global.visualViewport.removeEventListener('resize',positionHelp);global.visualViewport.removeEventListener('scroll',positionHelp);}
      if(returnFocus && previous.anchor.isConnected && !previous.anchor.closest('[hidden],[inert]'))previous.anchor.focus({preventScroll:true});
    }
    function helpOutside(event) {if(help && !help.element.contains(event.target) && !help.anchor.contains(event.target))closeHelp();}
    function helpKey(event) {if(help && event.key==='Escape'){event.preventDefault();event.stopPropagation();closeHelp(true);}}
    function positionHelp() {
      if(!help)return;
      const {element,anchor}=help;
      if(!anchor.isConnected || anchor.closest('[hidden],[inert]') || !anchor.getClientRects().length){closeHelp();return;}
      const viewport=global.visualViewport,margin=16;
      const leftEdge=viewport?.offsetLeft || 0,topEdge=viewport?.offsetTop || 0;
      const width=viewport?.width || global.innerWidth,height=viewport?.height || global.innerHeight;
      // Account for CSS zoom inherited by the body as well as browser zoom.
      const scale=element.getBoundingClientRect().width/element.offsetWidth || 1;
      element.style.maxWidth=Math.max(1,(width-2*margin)/scale)+'px';
      element.style.maxHeight=Math.max(1,(height-2*margin)/scale)+'px';
      const box=element.getBoundingClientRect(),r=anchor.getBoundingClientRect();
      const left=Math.max(leftEdge+margin,Math.min(r.right-box.width,leftEdge+width-margin-box.width));
      let top=r.bottom+8;
      if(top+box.height>topEdge+height-margin)top=r.top-8-box.height;
      top=Math.max(topEdge+margin,Math.min(top,topEdge+height-margin-box.height));
      element.style.left=left/scale+'px';element.style.top=top/scale+'px';
    }
    function openHelp(kind,anchor) {
      if(help?.anchor===anchor){closeHelp(true);return;}
      closeHelp();
      const layer=document.getElementById('jpPopoverLayer');if(!layer)return;
      const element=hook(node('div',undefined,'jp-popover mh-info-popover'),'info-popover');element.id='mhInfo'+(++helpSerial);
      element.setAttribute('role','region');element.tabIndex=-1;
      const title=node('h3',kind==='calendar' ? 'Sobre estes horários':'Explorar o mapa');title.id=element.id+'Title';
      element.setAttribute('aria-labelledby',title.id);element.append(title);
      let reference=null;
      if(kind==='calendar'){
        element.append(node('p','As sessões seguem o calendário de ações; não indicam cotações nem confirmação operacional.'),node('p','Sem confirmação: a cobertura disponível não permite confirmar a sessão.'));
        reference=node('p',undefined,'mh-info-reference');element.append(reference,node('p','A revisão das fontes indica quando os calendários foram conferidos. Consulte as datas e os links em Fontes e cobertura.'));
      }else{
        element.append(node('p','Explore o globo livremente. Após 10 segundos sem manipulação, ele volta à orientação aproximada do meio-dia solar médio. Os horários das bolsas seguem os fusos oficiais.'),node('p','Cada marcador reúne as bolsas de uma cidade.'),node('p','● Aberta · ◐ Outras sessões · ○ Fechada · ? Sem confirmação'));
      }
      const close=hook(node('button','Fechar','mh-info-close'),'info-close');close.type='button';close.setAttribute('aria-label','Fechar explicação');close.addEventListener('click',()=>closeHelp(true));
      const helpHeading=node('div',undefined,'mh-info-heading');helpHeading.append(title,close);element.prepend(helpHeading);
      help={kind,element,anchor,reference};updateHelpReference();layer.append(element);
      anchor.setAttribute('aria-expanded','true');anchor.setAttribute('aria-controls',element.id);
      document.addEventListener('pointerdown',helpOutside,true);document.addEventListener('keydown',helpKey,true);
      global.addEventListener('resize',positionHelp);global.addEventListener('scroll',positionHelp,true);
      if(global.visualViewport){global.visualViewport.addEventListener('resize',positionHelp);global.visualViewport.addEventListener('scroll',positionHelp);}
      positionHelp();element.focus({preventScroll:true});
    }
    function updateHelpReference() {if(help?.reference && current)help.reference.textContent='Referência: '+time(current.asOf,'UTC',true)+' UTC.';}
    const normalize=value=>value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
    function placeDetail() {
      const row=rows.get(selected)?.row;
      const target=compact ? row && !row.hidden ? inlineCell:detailDock:aside;
      const focused=document.activeElement,scroll=tableWrap.scrollTop;
      if(target===inlineCell && (inline.previousElementSibling!==row || inline.parentNode!==row.parentNode))row.after(inline);
      if(detail.parentNode!==target)target.append(detail);
      if(compact){if(globePanel.parentNode!==list)list.prepend(globePanel);}else if(globePanel.parentNode!==detail)detail.insertBefore(globePanel,schedules);
      if(target!==inlineCell)inline.remove();
      if(focused && focused.isConnected && document.activeElement!==focused)focused.focus({preventScroll:true});
      tableWrap.scrollTop=scroll;
    }
    function upcoming(status) {
      const value=status?.nextRegularOpen;
      return !!(value && !global.JPWMarketSessions.isRegularOpen(status) && value.latestUtc>current.asOf && value.latestUtc<=current.asOf+86400000);
    }
    function visibility() {
      const query=normalize(search.value).trim();let visible=0;
      const statuses=new Map((current?.venues || []).map(status=>[status.id,status]));
      const groupCounts={open:0,upcoming:0,other:0,closed:0,unknown:0};
      const expected=new Map(Array.from(sections.keys(),id=>[id,[]]));
      let focused=document.activeElement;const scroll=tableWrap.scrollTop;
      rows.forEach(r=>{
        const status=statuses.get(r.venue.id),regular=global.JPWMarketSessions.isRegularOpen(status);
        const next=quick==='open' && upcoming(status),group=next ? 'upcoming':status ? groupFor(status):'closed';
        const matches=quick==='all' || status && (quick==='open' ? regular || next:status.phase==='unknown');
        const hidden=!(normalize([r.venue.name,r.venue.city,r.venue.country].join(' ')).includes(query) && matches && (filter.value==='all' || status?.phase===filter.value));
        if(hidden && r.row.contains(document.activeElement)){search.focus({preventScroll:true});focused=search;}
        r.row.hidden=hidden;r.row.dataset.viewGroup=group;
        expected.get(group).push(r);
        if(!hidden){visible++;groupCounts[group]++;}
      });
      expected.get('upcoming').sort((a,b)=>{
        const x=statuses.get(a.venue.id).nextRegularOpen,y=statuses.get(b.venue.id).nextRegularOpen;
        return x.earliestUtc-y.earliestUtc || x.latestUtc-y.latestUtc || a.order-b.order;
      });
      sections.forEach((section,id)=>{
        const ordered=expected.get(id).map(r=>r.row),actual=Array.from(section.body.children).filter(e=>e.dataset.venueId);
        if(ordered.length!==actual.length || ordered.some((row,i)=>row!==actual[i]))ordered.forEach(row=>section.body.append(row));
        section.body.hidden=id==='upcoming' ? quick!=='open':quick==='open' && id!=='open';
        section.heading.hidden=id==='upcoming' && quick==='open' ? false:!groupCounts[id];
        section.title.textContent=GROUPS[id]+(groupCounts[id] ? ' · '+groupCounts[id]:'');
      });
      const constrained=!!query || filter.value!=='all';
      upcomingEmptyRow.hidden=quick!=='open' || groupCounts.upcoming>0 || constrained;
      if(constrained && !groupCounts.upcoming)sections.get('upcoming').heading.hidden=true;
      quickButtons.forEach((b,id)=>b.setAttribute('aria-pressed',String(id===quick)));
      empty.hidden=visible>0 || quick==='open' && !constrained;
      empty.textContent=constrained ? 'Nenhuma bolsa corresponde à pesquisa e aos filtros.':quick==='unknown' ? 'Nenhuma bolsa sem confirmação.':'Nenhuma bolsa disponível no catálogo.';
      outside.hidden=!rows.get(selected)?.row.hidden;
      placeDetail();
      if(focused?.isConnected && !focused.closest('[hidden],[inert]') && document.activeElement!==focused)focused.focus({preventScroll:true});
      tableWrap.scrollTop=scroll;
    }
    search.addEventListener('input',visibility);filter.addEventListener('change',visibility);
    showSelected.addEventListener('click',()=>{search.value='';filter.value='all';quick='all';visibility();focusSelected();rows.get(selected)?.row.scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'});});
    function resize() {
      compact=root.clientWidth<=800;root.dataset.compact=String(compact);
      const shown=!compact || mobileExpanded;
      const restoreMapFocus=!shown && (mapContent.contains(document.activeElement) || help?.kind==='map' && help.element.contains(document.activeElement));
      if(!compact && document.activeElement===mapToggle)search.focus();
      mapToggle.hidden=!compact;mapContent.hidden=!shown;mapToggle.setAttribute('aria-expanded',String(shown));
      if(!shown && help?.kind==='map')closeHelp();
      if(restoreMapFocus)mapToggle.focus({preventScroll:true});
      mapToggle.textContent=shown ? 'Recolher mapa':'Explorar mapa';
      placeDetail();if(mapVisibilityChanged)mapVisibilityChanged();
    }
    mapToggle.addEventListener('click',()=>{mobileExpanded=!mobileExpanded;resize();});
    const sizeObserver=new ResizeObserver(()=>{if(!root.hidden && (root.clientWidth<=800)!==compact)resize();});sizeObserver.observe(root);resize();
    function renderSources(venue,status) {
      const signature=JSON.stringify([venue.id,status.groups.map(g=>[g.id,g.coverage,g.sourceIds])]);
      if(signature===sourceSignature)return;sourceSignature=signature;
      const focused=Array.from(sourceLinks).find(([,a])=>a===document.activeElement)?.[0];
      sourceLinks.clear();sourceBody.replaceChildren();
      status.groups.forEach(group=>{
        const section=node('div',undefined,'mh-group');section.append(node('h4',group.label));
        section.append(node('p','Período do catálogo: '+time(group.coverage.fromUtc,'UTC',true)+' a '+time(group.coverage.untilUtc,'UTC',true)+' UTC'),node('p','Revisão da cobertura: '+group.coverage.verifiedAt));
        (group.sourceIds || group.coverage.sourceIds).forEach(id=>{
          const source=catalog.sources.find(s=>s.id===id);if(!source)return;
          const p=node('p'),a=node('a',source.title);a.href=source.url;a.target='_blank';a.rel='noopener noreferrer';p.append(a,node('span',' · Revisão da fonte: '+source.verifiedAt));
          if(source.publishedAt)p.append(node('span',' · Publicação: '+source.publishedAt));
          sourceLinks.set(JSON.stringify([venue.id,group.id,id]),a);section.append(p);
        });sourceBody.append(section);
      });
      if(focused){const equivalent=sourceLinks.get(focused);if(equivalent)equivalent.focus({preventScroll:true});else focusSelected();}
    }
    function render(snapshot,selectedId) {
      current=snapshot;selected=selectedId;
      clock.textContent='Referência: '+time(snapshot.asOf)+' UTC';clock.dateTime=new Date(snapshot.asOf).toISOString();updateHelpReference();
      const open=snapshot.venues.filter(global.JPWMarketSessions.isRegularOpen).length,unknown=snapshot.venues.filter(v=>v.phase==='unknown').length;
      summary.textContent=open===0 ? 'Nenhuma bolsa aberta agora':open===1 ? '1 bolsa aberta agora':open+' bolsas abertas agora';
      quickButtons.get('all').textContent='Todas '+snapshot.venues.length;quickButtons.get('open').textContent='Abertas '+open;quickButtons.get('unknown').textContent='Sem confirmação '+unknown;
      const focused=document.activeElement,scroll=tableWrap.scrollTop;
      snapshot.venues.forEach(status=>{
        const r=rows.get(status.id);if(!r)return;
        r.row.dataset.selected=String(status.id===selectedId);r.row.dataset.phase=status.phase;r.row.dataset.sessionGroup=groupFor(status);r.button.setAttribute('aria-pressed',String(status.id===selectedId));
        r.phaseLabel.textContent=symbol(status)+' '+label(status);r.local.textContent=time(snapshot.asOf,r.venue.timeZone);r.next.textContent=status.nextRegularOpen ? opening(status.nextRegularOpen,snapshot.asOf):status.nextTransition ? transition(status.nextTransition,r.venue.timeZone,snapshot.asOf):'Próximo horário não confirmado';
      });
      if(focused?.isConnected && document.activeElement!==focused)focused.focus({preventScroll:true});
      tableWrap.scrollTop=scroll;
      const venue=catalog.venues.find(v=>v.id===selectedId),status=snapshot.venues.find(v=>v.id===selectedId);
      if(!venue || !status)return;
      detailTitle.textContent=venue.name;location.textContent=venue.city+' · '+venue.country;
      localTime.textContent=time(snapshot.asOf,venue.timeZone);localTime.dateTime=new Date(snapshot.asOf).toISOString();localTime.setAttribute('aria-label','Hora local em '+venue.city+': '+localTime.textContent);localTime.title=venue.timeZone;
      state.textContent=symbol(status)+' '+label(status);nextTransition.textContent=transition(status.nextTransition,venue.timeZone,snapshot.asOf);
      const members=catalog.venues.filter(v=>v.city===venue.city && v.country===venue.country),nextCity=JSON.stringify(members.map(v=>v.id));
      if(nextCity!==citySignature){citySignature=nextCity;cityButtons.clear();cityVenues.replaceChildren();members.forEach(v=>{const b=node('button',v.name);b.type='button';b.addEventListener('click',()=>select(v.id,'city'));cityButtons.set(v.id,b);cityVenues.append(b);});}
      cityVenues.hidden=members.length<2;cityButtons.forEach((b,id)=>b.setAttribute('aria-pressed',String(id===selectedId)));
      if(detailId!==selectedId){
        detailId=selectedId;groupNodes.clear();scheduleBody.replaceChildren();
        status.groups.forEach(group=>{const section=node('div',undefined,'mh-group'),title=node('h4'),reason=node('p'),next=node('p');section.append(title,reason);if(status.groups.length>1)section.append(next);scheduleBody.append(section);groupNodes.set(group.id,{title,reason,next});});
      }
      status.groups.forEach(group=>{const n=groupNodes.get(group.id);n.title.textContent=group.label+' · '+LABELS[group.phase];n.reason.textContent=group.reason;n.next.textContent=transition(group.nextTransition,venue.timeZone,snapshot.asOf);});
      renderSources(venue,status);visibility();
    }
    function focusSelected() {const button=rows.get(selected)?.button;(button?.isConnected && button.getClientRects().length && !button.closest('[hidden],[inert]') ? button:search).focus({preventScroll:true});}
    return Object.freeze({root,globe,render,focusSelected,closeHelp,containsFocus(){return root.contains(document.activeElement) || !!help?.element.contains(document.activeElement);},setExpanded(value){root.hidden=!value;infoButtons.get('calendar').hidden=!value;if(!value)closeHelp();else resize();},get mapVisible(){return !mapContent.hidden;},globeStatus(message,retry=false){globeStatus.textContent=message;globeStatus.hidden=!message;globeRetry.hidden=!retry;},dispose(){closeHelp();sizeObserver.disconnect();infoButtons.forEach(button=>button.remove());root.remove();}});
  }
  global.JPWMarketHoursView=Object.freeze({create,createOverview,labels:LABELS});
})(globalThis);

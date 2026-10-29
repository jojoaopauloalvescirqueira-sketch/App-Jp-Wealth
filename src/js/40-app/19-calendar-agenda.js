// Calendário: presentation only. Personal writes belong to JPWAgenda; economic
// dates and coverage belong to JPWEconomicCalendar. No financial writer here.
(function initCalendarAgenda(){
  if(window.JPWCalendar)return;
  const KEY='jpwealth_calendar_view_v1',CURRENCIES=['USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY'];
  const NEW_CURRENCIES=['EUR','CAD','AUD','CNY'];
  const IMPACTS={high:'Alto',medium:'Médio',low:'Baixo',unclassified:'Não classificado'};
  const CONTENT={economic:'Econômico',personal:'Pessoal',app:'Aplicativo'};
  const coverageNames={confirmed:'Confirmada',partial:'Parcial',pending:'Pendente',stale:'Desatualizada',unavailable:'Indisponível'};
  const instances=new Map();let dialog=null,opener=null,disposed=false,prefsOpaque=false,prefsReadFailed=false;
  const browserZone=()=>Intl.DateTimeFormat().resolvedOptions().timeZone||'UTC';
  const pad=n=>String(n).padStart(2,'0');
  const dateKey=d=>d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());
  const today=()=>dateKey(new Date());
  const dateAt=s=>new Date(s+'T12:00:00');
  const shift=(s,n)=>{const d=dateAt(s);d.setDate(d.getDate()+n);return dateKey(d);};
  const monthStart=s=>s.slice(0,7)+'-01';
  const monthShift=(s,n)=>{const d=dateAt(monthStart(s));d.setMonth(d.getMonth()+n);return dateKey(d);};
  function gridBounds(month){const offset=(dateAt(month).getDay()+6)%7,from=shift(month,-offset),last=shift(monthShift(month,1),-1),count=Math.ceil((offset+dateAt(last).getDate())/7)*7;return {from,to:shift(from,count-1),count};}
  const dayLabel=s=>dateAt(s).toLocaleDateString('pt-BR',{weekday:'long',day:'numeric',month:'long'});
  const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const button=(action,label,icon)=>{const b=el('button',icon?'calendar-icon-button':'calendar-button',icon?undefined:label);b.type='button';b.dataset.calendarAction=action;if(icon){b.setAttribute('aria-label',label);b.title=label;
    const shapes={'economic-detail':['M12 11v6','M12 7h.01'],close:['M6 6l12 12','M18 6L6 18'],previous:['M15 18l-6-6 6-6'],next:['M9 6l6 6-6 6'],new:['M12 5v14','M5 12h14'],filters:['M4 7h16','M4 17h16','M8 4v6','M16 14v6'],info:['M12 11v6','M12 7h.01']};
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');svg.classList.add('shell-lucide');for(const d of shapes[action]||shapes.info){const path=document.createElementNS(svg.namespaceURI,'path');path.setAttribute('d',d);svg.append(path);}if(action==='info'||action==='economic-detail'){const circle=document.createElementNS(svg.namespaceURI,'circle');circle.setAttribute('cx','12');circle.setAttribute('cy','12');circle.setAttribute('r','9');svg.append(circle);}b.append(svg);}return b;};
  const isVisible=n=>!!n&&!n.hidden&&n.getClientRects().length>0&&getComputedStyle(n).visibility!=='hidden';
  function blocked(){
    if(document.querySelector('dialog[open]:not(#calendarDialog)'))return true;
    return [...document.querySelectorAll('#modalOverlay.show,#settingsModal.show,#settingsOverlay.show,#ecalOverlay.open,#ecalOverlay.show,#mvpNotesDrawer.open,#mvpNotesOverlay.show,[aria-modal="true"]')].some(n=>n!==dialog&&!dialog?.contains(n)&&isVisible(n));
  }
  function preferences(){
    const fallback={currencies:[...CURRENCIES],impacts:['high'],content:Object.keys(CONTENT)};
    let raw;try{raw=localStorage.getItem(KEY);prefsReadFailed=false;}catch(_){prefsReadFailed=true;return fallback;}
    if(raw===null)return fallback;
    try{const p=JSON.parse(raw);
      if(!p||typeof p!=='object'||Array.isArray(p)||p.schemaVersion!==1||Object.keys(p).some(k=>!['schemaVersion','currencies','impacts','contents'].includes(k))||!['currencies','impacts','contents'].every(k=>{const allowed=k==='currencies'?CURRENCIES:k==='impacts'?Object.keys(IMPACTS):Object.keys(CONTENT);return Array.isArray(p[k])&&p[k].length<=allowed.length&&new Set(p[k]).size===p[k].length&&p[k].every(v=>allowed.includes(v));})){prefsOpaque=true;return fallback;}
      return {currencies:[...new Set(p.currencies)],impacts:[...new Set(p.impacts)],content:[...new Set(p.contents)]};
    }catch(_){prefsOpaque=true;return fallback;}
  }
  function savePreferences(st){
    if(prefsOpaque||prefsReadFailed||st.prefWriteBlocked)return;
    try{localStorage.setItem(KEY,JSON.stringify({schemaVersion:1,currencies:st.currencies,impacts:st.impacts,contents:st.content}));}
    catch(_){st.notice='Não foi possível guardar os filtros neste navegador.';}
  }
  function state(id){const prefs=preferences();return {id,month:monthStart(today()),selected:today(),focused:today(),...prefs,prefWriteBlocked:prefsOpaque||prefsReadFailed,timeZone:browserZone(),form:null,token:null,baseReference:null,stage:'calendar',notice:prefsReadFailed?'Não foi possível ler seus filtros neste navegador. A consulta continua com filtros temporários nesta sessão.':'' ,errors:[],ambiguities:[],removing:false,request:0,economicByContext:new Map(),expandedEconomicObservation:null,data:{events:[],coverage:[],items:[],app:[]},active:false};}
  function snapshot(){try{return window.JPWAgenda?.queries.snapshot()||{status:'UNAVAILABLE',items:[]};}catch(_){return {status:'UNAVAILABLE',items:[]};}}
  function reference(){const s=snapshot();return JSON.stringify({status:s.status,revision:s.revision,items:s.items});}
  function backupItem(){
    try{
      const status=typeof dgBackupStatus==='function'?dgBackupStatus():null;
      if(!status?.at||status.state==='unknown')return null;
      const d=new Date(status.at);if(!Number.isFinite(d.getTime()))return null;
      const dueDays=typeof DG_BACKUP_DUE_DAYS==='number'?DG_BACKUP_DUE_DAYS:30;if(d.getTime()>Date.now())return null;d.setTime(d.getTime()+dueDays*86400000);
      return {id:'app:backup',date:dateKey(d),title:'Revisar backup',kind:'app',originAt:status.at,status:status.state};
    }catch(_){return null;}
  }
  function eventDay(e,zone){
    if(e.precision==='instant'&&e.at){
      try{const parts=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(e.at));return ['year','month','day'].map(k=>parts.find(p=>p.type===k).value).join('-');}catch(_){}
    }
    return e.date;
  }
  function personalOn(item,date,zone){
    if(item.kind==='task'||item.allDay)return item.date===date||(item.kind==='appointment'&&item.endAt&&date>=item.date&&date<item.endAt.slice(0,10));
    const start=eventDay({precision:'instant',at:item.startAt},zone),end=eventDay({precision:'instant',at:new Date(Date.parse(item.endAt)-1).toISOString()},zone);
    return date>=start&&date<=end;
  }
  function visibleInstance(inst){return inst.st.active&&!disposed&&!document.hidden&&(inst.isDialog?dialog?.open:isVisible(inst.root));}
  function clearClock(inst){if(inst.timer){clearTimeout(inst.timer);inst.timer=null;}}
  function armClock(inst){clearClock(inst);if(!visibleInstance(inst))return;const next=new Date();next.setHours(24,0,0,10);inst.timer=setTimeout(()=>{inst.timer=null;if(!visibleInstance(inst))return;refresh(inst);armClock(inst);},Math.max(10,next.getTime()-Date.now()));}
  async function refresh(inst){
    const st=inst.st;if(!visibleInstance(inst))return;armClock(inst);
    const request=++st.request,{from,to}=gridBounds(st.month),query={from,to,currencies:[...st.currencies],impacts:[...st.impacts],timeZone:st.timeZone};
    const context=JSON.stringify([from,to,st.timeZone,[...st.currencies].sort(),[...st.impacts].sort()]);
    let econ=null,econFailed=false,personal={status:'UNAVAILABLE',items:[]};
    try{econ=await Promise.resolve(window.JPWEconomicCalendar?.queryRange(query));if(!econ||!Array.isArray(econ.events)||!Array.isArray(econ.coverage)||econ.failed)econFailed=true;}catch(_){econFailed=true;}
    try{if(window.JPWAgenda)personal=await Promise.resolve(window.JPWAgenda.queries.range({from,to,timeZone:st.timeZone}));}catch(_){}
    if(request!==st.request||!visibleInstance(inst))return;
    const cached=st.economicByContext.get(context);if(econFailed)econ=cached||{events:[],coverage:[]};else st.economicByContext.set(context,econ);
    st.data={events:econ.events,coverage:econ.coverage,updatedAt:econ.updatedAt,feed:econ.feed||null,econFailed,econStale:econFailed&&!!cached,personalStatus:personal.status,items:personal.items||[],app:[backupItem()].filter(Boolean)};
    // Keep form nodes, input selection, validation and focus intact on feed updates.
    renderMonth(inst);renderAgenda(inst);renderInfo(inst);renderNotice(inst);
  }
  function markerItems(st,date){return {economic:st.content.includes('economic')&&st.data.events.filter(e=>eventDay(e,st.timeZone)===date&&st.currencies.includes(e.currency)&&st.impacts.includes(e.impact)).length,other:(st.content.includes('personal')?st.data.items.filter(i=>personalOn(i,date,st.timeZone)).length:0)+(st.content.includes('app')?st.data.app.filter(i=>i.date===date).length:0)};}
  function factory(root,id,isDialog){
    const st=state(id),panel=el('section','calendar-panel');panel.setAttribute('aria-label','Calendário e Agenda');
    const head=el('div','calendar-header'),title=el('h2','calendar-heading','Calendário e Agenda');title.id=id+'Title';
    const actions=el('div','calendar-header-actions');actions.append(button('info','Fontes e cobertura','i'),button('filters','Filtros','☷'),button('new','Novo','+'));if(isDialog)actions.append(button('close','Fechar calendário','×'));head.append(title,actions);
    const notice=el('p','calendar-notice');notice.setAttribute('role','status');notice.hidden=true;
    const body=el('div','calendar-body'),month=el('section','calendar-month'),agenda=el('section','calendar-agenda');
    const nav=el('div','calendar-month-nav'),label=el('h3','calendar-month-label');label.id=id+'Month';
    const navButtons=el('div','calendar-month-actions');navButtons.append(button('previous','Mês anterior','‹'),button('today','Hoje'),button('next','Próximo mês','›'));nav.append(label,navButtons);
    const week=el('div','calendar-weekdays');week.setAttribute('aria-hidden','true');['S','T','Q','Q','S','S','D'].forEach(t=>week.append(el('span','',t)));
    const grid=el('div','calendar-grid');grid.setAttribute('role','grid');grid.setAttribute('aria-labelledby',label.id);month.append(nav,week,grid);
    const controls=el('section','calendar-controls');controls.hidden=true;
    const info=el('section','calendar-info');info.hidden=true;
    const formHost=el('section','calendar-form-host');formHost.hidden=true;
    body.append(month,agenda);panel.append(head,notice,controls,info,body,formHost);root.replaceChildren(panel);
    const inst={root,panel,st,head,label,grid,agenda,body,controls,info,formHost,notice,isDialog};instances.set(id,inst);
    panel.addEventListener('click',e=>handleClick(inst,e));panel.addEventListener('keydown',e=>gridKeyboard(inst,e));
    panel.addEventListener('change',e=>handleChange(inst,e));panel.addEventListener('input',e=>{if(e.target.closest('.calendar-form'))captureForm(inst);});
    renderControls(inst);renderMonth(inst);renderAgenda(inst);return inst;
  }
  function renderNotice(inst){inst.notice.textContent=inst.st.notice;inst.notice.hidden=!inst.st.notice;}
  function renderMonth(inst){
    const {st,grid}=inst,focused=document.activeElement?.closest('[data-calendar-date]'),hadFocus=focused&&grid.contains(focused);
    inst.label.textContent=dateAt(st.month).toLocaleDateString('pt-BR',{month:'long',year:'numeric'});
    const {from:first,to:last,count}=gridBounds(st.month);
    const fragment=document.createDocumentFragment();
    if(st.focused<first||st.focused>last)st.focused=st.selected>=first&&st.selected<=last?st.selected:st.month;
    for(let index=0;index<count;index++){
      const date=shift(first,index),b=el('button','calendar-day');b.type='button';b.dataset.calendarDate=date;b.setAttribute('role','gridcell');b.tabIndex=date===st.focused?0:-1;
      b.setAttribute('aria-selected',String(date===st.selected));b.setAttribute('aria-label',dayLabel(date));
      if(date===today()){b.classList.add('calendar-day-today');b.setAttribute('aria-current','date');}
      if(date.slice(0,7)!==st.month.slice(0,7))b.classList.add('calendar-day-outside');
      b.append(el('span','calendar-day-number',String(dateAt(date).getDate())));
      const marks=markerItems(st,date),dots=el('span','calendar-day-markers');dots.setAttribute('aria-hidden','true');
      if(marks.economic){dots.classList.add('calendar-has-economic');dots.append(el('span','calendar-economic-dot'));}if(marks.other)dots.append(el('span','calendar-personal-dot'));b.append(dots);
      if(marks.economic||marks.other)b.setAttribute('aria-label',dayLabel(date)+(marks.economic?' · '+marks.economic+' evento'+(marks.economic===1?' econômico':'s econômicos'):'')+(marks.other?' · '+marks.other+' '+(marks.other===1?'item':'itens')+' da agenda':''));
      fragment.append(b);
    }
    const scroll=inst.panel.scrollTop;grid.replaceChildren(fragment);if(hadFocus)grid.querySelector('[tabindex="0"]')?.focus({preventScroll:true});inst.panel.scrollTop=scroll;
  }
  function coverageRows(st){return st.data.coverage.filter(c=>(!c.currency||st.currencies.includes(c.currency))&&(!c.month||c.month===st.selected.slice(0,7))&&typeof c.from==='string'&&typeof c.to==='string'&&c.from<=st.selected&&c.to>=st.selected);}
  function incomplete(st){const rows=coverageRows(st);return st.content.includes('economic')&&(st.data.econFailed||!rows.length||st.currencies.some(currency=>!rows.some(c=>c.currency===currency&&c.status==='confirmed')||rows.some(c=>c.currency===currency&&c.status!=='confirmed')));}
  function economicFailure(st){return st.data.econStale?'Não foi possível atualizar o calendário econômico. Os últimos dados deste recorte estão desatualizados.':'Não foi possível consultar o calendário econômico neste recorte. Consulte as fontes ou tente novamente.';}
  // Presentation identity only. Changing the instant must never retain details,
  // even when a provider reuses an id; duplicate observations are ambiguous.
  const economicObservation=event=>JSON.stringify([event.provider||'',event.sourceId,event.currency,event.title,event.precision,event.at?Date.parse(event.at):null,event.date,event.sourceUrl]);
  function economicLink(host,url,label){
    try{const u=new URL(url);if(u.protocol!=='https:'||u.username||u.password)return;const a=el('a','calendar-source-link',label);a.href=u.href;a.target='_blank';a.rel='noopener noreferrer';host.append(a);}catch(_){}
  }
  function renderAgenda(inst){
    const {st,agenda}=inst,scroll=agenda.scrollTop,panelScroll=inst.panel.scrollTop,active=document.activeElement,focusRow=active?.closest('[data-calendar-personal-id]'),focusId=agenda.contains(active)?focusRow?.dataset.calendarPersonalId:null,focusKind=active?.hasAttribute('data-calendar-complete')?'complete':active?.dataset.calendarAction;
    const activeEconomic=agenda.contains(active)?active?.closest('[data-calendar-economic-id],.calendar-economic-detail-row'):null;
    const focusObservation=activeEconomic?.dataset.calendarEconomicObservation,focusHref=active?.tagName==='A'?active.href:null;
    const heading=el('h3','calendar-agenda-heading',dayLabel(st.selected));heading.tabIndex=-1;
    const zone=el('p','calendar-meta calendar-agenda-summary'),list=el('div','calendar-agenda-list'),economic=st.content.includes('economic')?st.data.events.filter(e=>eventDay(e,st.timeZone)===st.selected&&st.currencies.includes(e.currency)&&st.impacts.includes(e.impact)):[],personal=st.content.includes('personal')?st.data.items.filter(i=>personalOn(i,st.selected,st.timeZone)):[],app=st.content.includes('app')?st.data.app.filter(i=>i.date===st.selected):[];
    const total=economic.length+personal.length+app.length,feed=st.data.feed;
    let update=st.economicRefreshing?'Atualizando eventos…':st.data.econFailed?economicFailure(st):feed?.fetchFailed?'Falha na atualização; dados anteriores preservados':feed?.stale?'Coleta desatualizada':'';
    const at=feed?.collectedAt||st.data.updatedAt;
    if(at&&Number.isFinite(Date.parse(at)))update+=(update?' · ':'')+(feed?.collectedAt?'Coleta: ':'Referência: ')+new Date(at).toLocaleString('pt-BR',{timeZone:st.timeZone,dateStyle:'short',timeStyle:'short'});
    if(!update)update='Atualização não informada';
    zone.textContent=total+' '+(total===1?'item':'itens')+' · '+st.timeZone+(st.content.includes('economic')&&update?' · '+update:'');
    economic.sort((a,b)=>(a.at||'').localeCompare(b.at||''));
    const matching=observation=>economic.filter(e=>economicObservation(e)===observation);
    if(st.expandedEconomicObservation&&matching(st.expandedEconomicObservation).length!==1)st.expandedEconomicObservation=null;
    if(economic.length){
      const table=el('table','calendar-economic-table'),caption=el('caption','calendar-economic-caption calendar-agenda-group','Economia'),thead=el('thead'),head=el('tr'),tbody=el('tbody');thead.setAttribute('role','rowgroup');tbody.setAttribute('role','rowgroup');head.setAttribute('role','row');
      table.setAttribute('role','table');
      for(const label of ['Horário','Moeda','Impacto','Evento','Atual','Projeção','Anterior']){const th=el('th','',label);th.scope='col';th.setAttribute('role','columnheader');head.append(th);}
      thead.append(head);table.append(caption,thead,tbody);list.append(table);
      for(const [index,event] of economic.entries()){
        const row=el('tr','calendar-event-economic'),observation=economicObservation(event);row.setAttribute('role','row');row.dataset.calendarEconomicId=event.id;row.dataset.calendarEconomicObservation=observation;
        const cell=(field,cls,text)=>{const td=el('td',cls,text);td.setAttribute('role','cell');td.dataset.calendarEconomicField=field;row.append(td);return td;};
        const fromFF=event.provider==='forexfactory'||String(event.sourceId||'').startsWith('ff-');
        const time=cell('time','calendar-economic-time calendar-event-time',event.precision==='date'?'Data · horário não informado':new Date(event.at).toLocaleTimeString('pt-BR',{timeZone:st.timeZone,hour:'2-digit',minute:'2-digit'}));
        cell('currency','calendar-economic-currency',event.currency);
        const impact=cell('impact','calendar-economic-impact'),symbol=el('span','calendar-impact-symbol calendar-impact-'+(Object.hasOwn(IMPACTS,event.impact)?event.impact:'unclassified'));
        symbol.setAttribute('role','img');symbol.setAttribute('aria-label','Impacto: '+(IMPACTS[event.impact]||IMPACTS.unclassified)+' · '+(fromFF?'Forex Factory':'editorial JP Wealth'));symbol.title=symbol.getAttribute('aria-label');
        if(event.impact==='unclassified'||!Object.hasOwn(IMPACTS,event.impact))symbol.append(el('span','','?'));else for(let n=1;n<=3;n++){const bar=el('span','calendar-impact-bar');bar.setAttribute('aria-hidden','true');bar.classList.toggle('calendar-impact-filled',n<=({high:3,medium:2,low:1}[event.impact]||0));symbol.append(bar);}impact.append(symbol);
        const title=cell('event','calendar-economic-event'),titleLine=el('div','calendar-economic-title-line'),info=button('economic-detail','Detalhes de '+event.title,'i'),detailId=st.id+'EconomicDetail'+index,expanded=st.expandedEconomicObservation===observation;
        info.setAttribute('aria-expanded',String(expanded));info.setAttribute('aria-controls',detailId);titleLine.append(el('strong','calendar-event-title',event.title),info);title.append(titleLine);
        const warnings=[];
        if(event.precision==='date'||event.timeConfirmed===false)warnings.push('Horário a confirmar.');
        if(event.status==='cancelled')warnings.push('Cancelado na fonte.');
        if(event.status==='published')warnings.push('Publicado na fonte.');
        if(event.observationStatus==='not-in-latest')warnings.push('Não consta na última coleta; não comprova cancelamento.');
        if(event.sourceConflict)warnings.push('As fontes divergem; data ou horário a confirmar.');
        if(warnings.length)title.append(el('p','calendar-event-warning',warnings.join(' ')));
        for(const [field,label] of [['actual','Atual'],['forecast','Projeção'],['previous','Anterior']]){
          const td=cell(field,'calendar-economic-number'),value=field==='actual'?'—':typeof event[field]==='string'&&event[field].trim()!==''?event[field]:'—';
          const labelNode=el('span','calendar-economic-value-label',label);labelNode.setAttribute('aria-hidden','true');const number=el('span','calendar-economic-value',value);number.dataset.calendarEconomicValue=field;
          if(value==='—'){td.setAttribute('aria-label',label+': '+(field==='actual'?'Não fornecido nesta alimentação':'Não informado na fonte'));number.setAttribute('aria-label',label+': '+(field==='actual'?'Não fornecido nesta alimentação':'Não informado na fonte'));number.title=field==='actual'?'Não fornecido nesta alimentação':'Não informado na fonte';}td.append(labelNode,number);
        }
        const detailRow=el('tr','calendar-economic-detail-row');detailRow.dataset.calendarEconomicObservation=observation;detailRow.hidden=!expanded;
        const detailCell=el('td'),detail=el('div','calendar-economic-detail');detailRow.setAttribute('role','row');detailCell.setAttribute('role','cell');detailCell.colSpan=7;detail.id=detailId;detail.setAttribute('role','region');detail.setAttribute('aria-label','Detalhes de '+event.title);
        detail.append(el('p','calendar-meta','Impacto: '+(fromFF?'classificação Forex Factory':'editorial JP Wealth')));
        if(event.sourceUrl)economicLink(detail,event.sourceUrl,fromFF?'Fonte: Forex Factory':'Fonte oficial');
        if(event.precision==='instant'&&event.at){try{detail.append(el('p','calendar-meta','Horário original: '+new Date(event.at).toLocaleString('pt-BR',{timeZone:event.timeZone||'UTC',dateStyle:'short',timeStyle:'short'})+' · '+(event.timeZone||'UTC')+(event.timeConfirmed===false?' · indicativo, confirme na fonte':'')));}catch(_){}}
        detail.append(el('p','calendar-meta','Atual: não fornecido nesta alimentação.'));
        for(const source of Array.isArray(event.officialReferences)?event.officialReferences:[])economicLink(detail,source.url||source.sourceUrl,'Conferir fonte oficial');
        detailCell.append(detail);detailRow.append(detailCell);tbody.append(row,detailRow);
      }
    }
    if(personal.length)list.append(el('h4','calendar-agenda-group','Sua agenda'));
    for(const item of personal){
      const row=el('article','calendar-event calendar-event-personal');row.dataset.calendarPersonalId=item.id;
      if(item.kind==='task'){
        const label=el('label','calendar-completion');const input=el('input');input.type='checkbox';input.checked=!!item.completedAt;input.dataset.calendarComplete=item.id;input.setAttribute('aria-label','Concluir tarefa '+item.title);label.append(input);row.append(label);
      }else row.append(el('span','calendar-event-time',item.allDay?'Dia inteiro':new Date(item.startAt).toLocaleTimeString('pt-BR',{timeZone:st.timeZone,hour:'2-digit',minute:'2-digit'})));
      const detail=el('div','calendar-event-content'),edit=button('edit','Editar '+item.title);edit.dataset.calendarId=item.id;edit.textContent=item.title;edit.classList.add('calendar-entry-title');detail.append(edit,el('span','calendar-meta',item.kind==='task'?(item.completedAt?'Tarefa concluída':'Tarefa'):'Compromisso'));
      if(item.notes)detail.append(el('p','calendar-entry-notes',item.notes));row.append(detail);list.append(row);
    }
    if(app.length)list.append(el('h4','calendar-agenda-group','Do aplicativo'));
    for(const item of app){const row=el('article','calendar-event calendar-event-app'),detail=el('div','calendar-event-content');detail.append(el('strong','calendar-event-title',item.title),el('span','calendar-meta','Aplicativo · 30 dias após a confirmação'));const go=button('backup','Abrir Backup e Recuperação');go.dataset.calendarOrigin=item.originAt;detail.append(go);row.append(detail);list.append(row);}
    if(!economic.length&&!personal.length&&!app.length)list.append(el('p','calendar-empty',st.content.includes('economic')&&st.data.econFailed?'Não foi possível verificar os eventos econômicos deste dia.':incomplete(st)?'Nenhum item disponível neste recorte. A cobertura econômica ainda precisa de confirmação.':'Nenhum item neste dia com os filtros atuais.'));
    if(st.content.includes('economic')&&incomplete(st)){const note=el('div','calendar-coverage-note');note.append(el('p','',st.data.econFailed?economicFailure(st):'Cobertura econômica parcial ou pendente para esta data; consulte as fontes para confirmação.'),button('info','Ver fontes e cobertura'));list.append(note);}
    if(st.content.includes('personal')&&st.data.personalStatus!=='OK')list.append(el('p','calendar-coverage-note',st.data.personalStatus==='INCOMPATIBLE'?'Sua agenda usa uma versão incompatível. Os registros foram preservados.':'Não foi possível consultar sua agenda.'));
    agenda.replaceChildren(heading,zone,list);
    if(focusId){const row=[...agenda.querySelectorAll('[data-calendar-personal-id]')].find(r=>r.dataset.calendarPersonalId===focusId);row?.querySelector(focusKind==='complete'?'[data-calendar-complete]':'[data-calendar-action="edit"]')?.focus({preventScroll:true});}
    else if(focusObservation){
      const rows=[...agenda.querySelectorAll('[data-calendar-economic-id]')].filter(r=>r.dataset.calendarEconomicObservation===focusObservation);
      let target=null;
      if(rows.length===1){const row=rows[0],detail=row.nextElementSibling;target=focusHref?[...row.querySelectorAll('a'),...(!detail.hidden?detail.querySelectorAll('a'):[])].find(a=>a.href===focusHref):row.querySelector('[data-calendar-action="economic-detail"]');}
      (target||heading).focus({preventScroll:true});
    }
    agenda.scrollTop=scroll;inst.panel.scrollTop=panelScroll;
  }

  function renderControls(inst){
    const host=inst.controls,st=inst.st;host.replaceChildren(el('h3','','Filtros'));
    for(const [key,values,labels] of [['currencies',CURRENCIES,null],['impacts',Object.keys(IMPACTS),IMPACTS],['content',Object.keys(CONTENT),CONTENT]]){
      const field=el('fieldset','calendar-filter-group');field.append(el('legend','',key==='currencies'?'Moedas':key==='impacts'?'Impacto':'Conteúdo'));
      for(const value of values){const label=el('label','calendar-filter-option'),input=el('input');input.type='checkbox';input.value=value;input.checked=st[key].includes(value);input.dataset.calendarFilter=key;if(key==='currencies')input.dataset.calendarCurrency=value;label.append(input,document.createTextNode(labels?labels[value]:value));field.append(label);}host.append(field);
    }
    const missing=NEW_CURRENCIES.filter(currency=>!st.currencies.includes(currency));
    if(missing.length){host.append(el('p','calendar-meta','Seus filtros foram preservados. Moedas adicionadas ao calendário que estão desmarcadas: '+missing.join(', ')+'.'),button('include-new-currencies','Incluir moedas novas'));}
    if(prefsOpaque)host.append(el('p','calendar-meta','A preferência salva é incompatível. Seu conteúdo original será preservado.'));
  }
  function renderInfo(inst){
    const host=inst.info,st=inst.st,rows=coverageRows(st),active=document.activeElement,hadFocus=host.contains(active),focusAction=hadFocus?active?.dataset.calendarAction:null,focusHref=hadFocus&&active?.tagName==='A'?active.href:null,scroll=host.scrollTop,panelScroll=inst.panel.scrollTop;host.replaceChildren(el('h3','','Fontes e cobertura'));
    host.append(el('p','calendar-meta','Cobertura de '+dateAt(st.selected).toLocaleDateString('pt-BR',{month:'long',year:'numeric'})));
    host.append(el('p','calendar-meta','Intervalos válidos para '+dateAt(st.selected).toLocaleDateString('pt-BR')+'. Uma semana recebida não confirma as outras semanas do mês.'));
    if(st.data.econFailed)host.append(el('p','calendar-coverage-note',economicFailure(st)));
    host.append(el('p','calendar-meta','Forex Factory é a fonte principal, com complementos oficiais identificados. Ausência de publicação não comprova ausência de evento. Horários são exibidos em '+st.timeZone+'.'));
    host.append(el('p','calendar-meta','O impacto identifica sua origem: classificação Forex Factory ou curadoria editorial JP Wealth. Não representa previsão de preço nem garantia de efeito no mercado.'));
    const list=el('ul','calendar-source-list');
    for(const currency of st.currencies){const matching=rows.filter(c=>c.currency===currency),row=el('li');row.append(el('strong','',currency+' · '));row.append(document.createTextNode(matching.length?matching.map(c=>(coverageNames[c.status]||c.status)+' ('+c.from+' a '+c.to+')'+(c.reason?' — '+c.reason:'')).join('; '):'Cobertura pendente para esta data'));list.append(row);}host.append(list);
    let sources=[];try{sources=window.JPWEconomicCalendar?.sources()||[];}catch(_){}
    if(!Array.isArray(sources))sources=Object.values(sources);
    const links=el('div','calendar-source-links');
    for(const source of sources){
      const url=source.url||source.sourceUrl||source.officialUrl;
      try{
        const u=new URL(url);if(u.protocol!=='https:')continue;
        const row=el('div','calendar-source'),a=el('a','calendar-source-link',source.name||source.label||source.id);
        a.dataset.calendarSource=source.id||'';a.href=u.href;a.target='_blank';a.rel='noopener noreferrer';row.append(a);
        if(source.attribution)row.append(el('p','calendar-meta',source.attribution));
        if(source.license){
          const label=el('span','calendar-meta',source.license);
          try{const licenseUrl=new URL(source.licenseUrl);if(licenseUrl.protocol==='https:'){const license=el('a','calendar-source-link calendar-license-link',source.license);license.href=licenseUrl.href;license.target='_blank';license.rel='noopener noreferrer';label.replaceChildren(license);}}catch(_){}
          row.append(label);
        }
        links.append(row);
      }catch(_){}
    }
    host.append(links);
    if(st.data.updatedAt)host.append(el('p','calendar-meta','Referência do pacote: '+new Date(st.data.updatedAt).toLocaleString('pt-BR')));
    const feed=st.data.feed;
    if(feed){
      host.append(el('p','calendar-meta',feed.stale?'Última coleta válida há mais de duas horas. Consulte as fontes para confirmar atualizações.':'Consulta econômica sobre o último pacote válido.'));
      if(feed.mode==='legacy-partial')host.append(el('p','calendar-meta','O alimentador externo atual fornece somente alto impacto em quatro moedas. A ampliação externa ainda depende de ativação.'));
      if(feed.fetchFailed)host.append(el('p','calendar-event-warning','Não foi possível atualizar a alimentação pública. Os dados anteriores foram preservados.'));
      for(const [key,label] of [['collectedAt','Última coleta válida'],['packagePublishedAt','Geração do pacote'],['sourcePublishedAt','Atualização informada pelo provedor']]){const at=feed[key];host.append(el('p','calendar-meta',label+': '+(at&&Number.isFinite(Date.parse(at))?new Date(at).toLocaleString('pt-BR'):'Não informada')));}
      if(feed.readFailed||feed.writeFailed)host.append(el('p','calendar-event-warning','O cache público não pôde ser lido ou atualizado neste navegador. Seus registros pessoais foram preservados.'));
    }
    if(window.JPWCalendarFeed){const refreshButton=button('refresh-economic',st.economicRefreshing?'Atualizando eventos…':'Atualizar eventos');refreshButton.setAttribute('aria-disabled',String(!!st.economicRefreshing));refreshButton.setAttribute('aria-busy',String(!!st.economicRefreshing));host.append(refreshButton);}
    if(hadFocus){const target=focusAction?[...host.querySelectorAll('[data-calendar-action]')].find(node=>node.dataset.calendarAction===focusAction):focusHref?[...host.querySelectorAll('a')].find(node=>node.href===focusHref):null;target?.focus({preventScroll:true});}
    host.scrollTop=scroll;inst.panel.scrollTop=panelScroll;
  }
  function gridKeyboard(inst,event){
    const target=event.target.closest('[data-calendar-date]');if(!target)return;const date=target.dataset.calendarDate;let next=null;
    const delta={ArrowLeft:-1,ArrowRight:1,ArrowUp:-7,ArrowDown:7};
    if(event.key in delta)next=shift(date,delta[event.key]);
    if(event.key==='Home')next=shift(date,-((dateAt(date).getDay()+6)%7));
    if(event.key==='End')next=shift(date,6-((dateAt(date).getDay()+6)%7));
    if(event.key==='PageUp'||event.key==='PageDown'){const d=dateAt(monthShift(date,event.key==='PageUp'?-1:1));d.setDate(Math.min(dateAt(date).getDate(),dateAt(shift(monthShift(dateKey(d),1),-1)).getDate()));next=dateKey(d);}
    if(event.key==='Enter'||event.key===' '){event.preventDefault();selectDate(inst,date);return;}
    if(!next)return;event.preventDefault();inst.st.focused=next;if(next.slice(0,7)!==inst.st.month.slice(0,7)){inst.st.month=monthStart(next);refresh(inst);}renderMonth(inst);inst.grid.querySelector('[data-calendar-date="'+next+'"]')?.focus({preventScroll:true});
  }
  function selectDate(inst,date){inst.st.selected=date;inst.st.focused=date;renderMonth(inst);renderAgenda(inst);renderInfo(inst);}
  function newForm(inst,id=null){
    const st=inst.st,prepared=window.JPWAgenda?.queries.prepare({id});
    if(!prepared?.ok){st.notice=prepared?.errors?.map(e=>e.message||e).join(' ')||'Não foi possível preparar a edição da agenda.';renderNotice(inst);return;}
    const item=prepared.item;st.token=prepared.token;st.baseReference=reference();st.formId=id;
    const time=(iso,zone)=>{if(!iso)return '';return new Date(iso).toLocaleTimeString('en-GB',{timeZone:zone,hour:'2-digit',minute:'2-digit'});};
    st.form=item?{kind:item.kind,title:item.title,notes:item.notes||'',date:item.date,allDay:!!item.allDay,startTime:time(item.startAt,item.timeZone||st.timeZone),endDate:item.endAt?eventDay({precision:'instant',at:item.endAt},item.timeZone||st.timeZone):item.date,endTime:time(item.endAt,item.timeZone||st.timeZone),timeZone:item.timeZone||st.timeZone}:{kind:'task',title:'',notes:'',date:st.selected,allDay:true,startTime:'09:00',endDate:st.selected,endTime:'10:00',timeZone:st.timeZone};
    st.errors=[];st.ambiguities=[];st.removing=false;st.stage='form';renderForm(inst);inst.formHost.querySelector('[name="title"]')?.focus();
  }
  function captureForm(inst){
    const form=inst.formHost.querySelector('form');if(!form||!inst.st.form)return;
    for(const input of form.elements){if(!input.name)continue;inst.st.form[input.name]=input.type==='checkbox'?input.checked:input.value;}
  }
  function addField(form,name,label,type,value){const wrap=el('label','calendar-form-field');wrap.append(el('span','',label));let input;
    if(type==='textarea')input=el('textarea');else if(type==='select')input=el('select');else {input=el('input');input.type=type;}
    input.name=name;input.id=form.id+'-'+name;if(type!=='checkbox')input.value=value??'';else input.checked=!!value;wrap.append(input);form.append(wrap);return input;}
  function renderForm(inst){
    const {st,formHost}=inst;inst.body.hidden=st.stage==='form';formHost.hidden=st.stage!=='form';inst.controls.hidden=true;inst.info.hidden=true;if(st.stage!=='form'){if(!st.form)formHost.replaceChildren();return;}
    const form=el('form','calendar-form');form.id=st.id+'Form';form.noValidate=true;form.addEventListener('submit',e=>{e.preventDefault();saveForm(inst);});
    form.append(el('h3','',st.formId?'Editar na agenda':'Novo na agenda'));
    const kind=addField(form,'kind','Tipo','select');for(const [value,label] of [['task','Tarefa'],['appointment','Compromisso']]){const o=el('option','',label);o.value=value;kind.append(o);}kind.value=st.form.kind;
    const title=addField(form,'title','Título','text',st.form.title);title.maxLength=200;title.required=true;
    addField(form,'date','Data','date',st.form.date);
    if(st.form.kind==='appointment'){
      addField(form,'allDay','Dia inteiro','checkbox',st.form.allDay);
      if(!st.form.allDay){addField(form,'startTime','Horário inicial','time',st.form.startTime);addField(form,'endDate','Data final','date',st.form.endDate);addField(form,'endTime','Horário final','time',st.form.endTime);const zone=addField(form,'timeZone','Fuso horário','text',st.form.timeZone);zone.required=true;}
    }
    const notes=addField(form,'notes','Notas','textarea',st.form.notes);notes.maxLength=10000;notes.rows=3;
    const errors=el('div','calendar-form-errors');errors.setAttribute('role','alert');form.append(errors);
    const choices=el('div','calendar-form-ambiguities');form.append(choices);
    const actions=el('div','calendar-form-actions'),save=button('save-form','Salvar');save.type='submit';save.classList.add('calendar-primary');actions.append(button('cancel-form','Cancelar'),save);if(st.formId)actions.append(button('remove-form','Excluir'));form.append(actions);
    const revision=button('refresh-revision','Atualizar revisão');revision.hidden=true;form.append(revision);formHost.replaceChildren(form);renderFormErrors(inst);
  }
  function renderFormErrors(inst){
    const st=inst.st,form=inst.formHost.querySelector('form');if(!form)return;
    const host=form.querySelector('.calendar-form-errors');host.replaceChildren();for(const field of form.elements){field.removeAttribute('aria-invalid');field.removeAttribute('aria-describedby');}
    for(const [index,error] of st.errors.entries()){const p=el('p','',typeof error==='string'?error:error.message||error.code||'Não foi possível salvar.');p.id=st.id+'Error'+index;host.append(p);const input=form.elements.namedItem(error.field);if(input){input.setAttribute('aria-invalid','true');input.setAttribute('aria-describedby',p.id);}}
    const choices=form.querySelector('.calendar-form-ambiguities');choices.replaceChildren();
    for(const ambiguity of st.ambiguities){const select=addField(choices,ambiguity.field,ambiguity.field==='startAtChoice'?'Escolha o horário inicial neste fuso':'Escolha o horário final neste fuso','select');const empty=el('option','','Selecione explicitamente');empty.value='';select.append(empty);for(const option of ambiguity.options){const o=el('option','',option.label);o.value=option.value;select.append(o);}select.value=st.form[ambiguity.field]||'';select.required=true;}
    const conflict=st.errors.some(e=>/stale|conflict|revision|context_changed|unconfirmed_document/i.test(e.code||''));form.querySelector('[data-calendar-action="refresh-revision"]').hidden=!conflict;
    let removal=form.querySelector('.calendar-remove-confirm');if(st.removing&&!removal){removal=el('div','calendar-remove-confirm');removal.append(el('p','','Excluir este registro da agenda?'),button('cancel-remove','Manter registro'),button('confirm-remove','Excluir registro'));form.append(removal);}else if(!st.removing)removal?.remove();
  }
  async function saveForm(inst){
    const st=inst.st;if(st.busy)return;captureForm(inst);st.errors=[];st.ambiguities=[];
    const preview=window.JPWAgenda?.queries.previewEntry(st.form);if(!preview?.ok){st.errors=preview?.errors||[{message:'Não foi possível validar este registro.'}];st.ambiguities=preview?.ambiguities||[];renderFormErrors(inst);return;}
    st.busy=true;const submit=inst.formHost.querySelector('[data-calendar-action="save-form"]');if(submit)submit.disabled=true;
    try{const result=await Promise.resolve(window.JPWAgenda.commands.save({input:{...st.form},token:st.token}));
      if(result?.ok){st.form=null;st.token=null;st.baseReference=null;st.stage='calendar';st.notice='Registro salvo na agenda.';renderForm(inst);renderNotice(inst);await refresh(inst);}
      else {st.errors=result?.errors?.length?result.errors:[{code:result?.status,message:result?.status==='UNKNOWN'?'A gravação não pôde ser confirmada. Abra Backup e Recuperação antes de tentar novamente.':'O registro não foi salvo. Confira a revisão e os campos.'}];renderFormErrors(inst);}
    }catch(_){st.errors=[{code:'UNKNOWN',message:'O resultado da gravação não pôde ser confirmado. Consulte Backup e Recuperação.'}];renderFormErrors(inst);}finally{st.busy=false;if(submit?.isConnected)submit.disabled=false;}
  }
  async function complete(inst,input){
    const id=input.dataset.calendarComplete,prepared=window.JPWAgenda?.queries.prepare({id});if(!prepared?.ok){input.checked=!input.checked;inst.st.notice='A tarefa mudou. Consulte a agenda novamente.';renderNotice(inst);refresh(inst);return;}
    input.disabled=true;let result;try{result=await Promise.resolve(window.JPWAgenda.commands.setCompleted({id,completed:input.checked,token:prepared.token}));}catch(_){result={status:'UNKNOWN'};}
    if(!result?.ok){input.checked=!input.checked;inst.st.notice=result?.status==='UNKNOWN'?'A conclusão não pôde ser confirmada. Consulte Backup e Recuperação.':'A conclusão não foi salva. Confira a tarefa novamente.';renderNotice(inst);}input.disabled=false;refresh(inst);
  }
  async function removeForm(inst){const st=inst.st;if(st.busy)return;st.busy=true;try{const result=await Promise.resolve(window.JPWAgenda.commands.remove({id:st.formId,token:st.token}));if(result?.ok){st.form=null;st.token=null;st.stage='calendar';st.notice='Registro excluído da agenda.';renderForm(inst);renderNotice(inst);refresh(inst);}else{st.errors=result?.errors||[{code:result?.status,message:'Não foi possível confirmar a exclusão. O rascunho foi preservado.'}];renderFormErrors(inst);}}finally{st.busy=false;}}
  function handleChange(inst,event){
    const input=event.target,st=inst.st;
    if(input.dataset.calendarFilter){const key=input.dataset.calendarFilter;st[key]=[...inst.controls.querySelectorAll('[data-calendar-filter="'+key+'"]:checked')].map(i=>i.value);savePreferences(st);refresh(inst);return;}
    if(input.dataset.calendarComplete){complete(inst,input);return;}
    if(input.closest('.calendar-form')){captureForm(inst);if(input.name==='kind'&&st.form.kind==='task')st.form.allDay=true;if(['kind','allDay'].includes(input.name))renderForm(inst);}
  }
  function handleClick(inst,event){
    const date=event.target.closest('[data-calendar-date]');if(date){selectDate(inst,date.dataset.calendarDate);return;}
    const target=event.target.closest('[data-calendar-action]');if(!target)return;const action=target.dataset.calendarAction,st=inst.st;
    if(action==='close'){close();return;}
    if(action==='economic-detail'){const row=target.closest('[data-calendar-economic-id]');if(!row)return;const observation=row.dataset.calendarEconomicObservation;st.expandedEconomicObservation=st.expandedEconomicObservation===observation?null:observation;renderAgenda(inst);return;}
    if(action==='previous'||action==='next'){st.month=monthShift(st.month,action==='previous'?-1:1);st.focused=st.month;renderMonth(inst);refresh(inst);return;}
    if(action==='today'){st.month=monthStart(today());selectDate(inst,today());refresh(inst);return;}
    if(action==='include-new-currencies'){st.currencies=CURRENCIES.filter(currency=>st.currencies.includes(currency)||NEW_CURRENCIES.includes(currency));savePreferences(st);renderControls(inst);refresh(inst);return;}
    if(action==='refresh-economic'){if(st.economicRefreshing)return;st.economicRefreshing=true;renderInfo(inst);renderAgenda(inst);Promise.resolve().then(()=>window.JPWCalendarFeed?.refresh(true)).catch(()=>{st.notice='Não foi possível atualizar os eventos. Os dados anteriores foram preservados.';renderNotice(inst);}).finally(()=>{st.economicRefreshing=false;if(visibleInstance(inst))refresh(inst);});return;}
    if(action==='filters'||action==='info'){if(st.stage==='form'){captureForm(inst);st.notice='Conclua ou cancele a edição para consultar '+(action==='filters'?'os filtros.':'as fontes.');renderNotice(inst);return;}const host=action==='filters'?inst.controls:inst.info;host.hidden=!host.hidden;if(action==='info')renderInfo(inst);return;}
    if(action==='new'){if(st.form){st.stage='form';renderForm(inst);}else newForm(inst);return;}
    if(action==='edit'){if(st.form){st.notice='Sua edição atual foi preservada. Salve ou cancele antes de editar outro registro.';renderNotice(inst);return;}newForm(inst,target.dataset.calendarId);return;}
    if(action==='cancel-form'){st.form=null;st.token=null;st.baseReference=null;st.formId=null;st.stage='calendar';st.errors=[];st.ambiguities=[];renderForm(inst);return;}
    if(action==='save-form')return; // Native form submit is the only save trigger.
    if(action==='remove-form'){st.removing=true;renderFormErrors(inst);return;}
    if(action==='cancel-remove'){st.removing=false;renderFormErrors(inst);return;}
    if(action==='confirm-remove'){removeForm(inst);return;}
    if(action==='refresh-revision'){captureForm(inst);const prepared=window.JPWAgenda?.queries.prepare({id:st.formId});if(prepared?.ok){st.token=prepared.token;st.baseReference=reference();st.errors=[];st.notice='Revisão atualizada. Confira seu rascunho antes de salvar.';renderFormErrors(inst);renderNotice(inst);}return;}
    if(action==='backup'){
      const current=backupItem();if(!current||current.originAt!==target.dataset.calendarOrigin){st.notice='A confirmação do backup mudou. Consulte a agenda novamente.';renderNotice(inst);refresh(inst);return;}
      const origin=inst.isDialog?opener:target;if(inst.isDialog)close(false);if(typeof openSettingsModal==='function')openSettingsModal('backup',origin);return;
    }
  }
  function ensureDialog(){
    if(dialog)return instances.get('calendarDialog');dialog=el('dialog','calendar-dialog');dialog.id='calendarDialog';dialog.setAttribute('aria-labelledby','calendarDialogTitle');document.body.append(dialog);const inst=factory(dialog,'calendarDialog',true);
    dialog.addEventListener('cancel',e=>{e.preventDefault();close();});dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)close();});
    dialog.addEventListener('close',()=>{if(dialog.open)return;inst.st.active=false;inst.st.request++;clearClock(inst);document.getElementById('headerCalendarBtn')?.setAttribute('aria-expanded','false');});return inst;
  }
  function positionDialog(){
    if(!dialog?.open)return;for(const key of ['margin','inset','left','top','max-height'])dialog.style.removeProperty(key);
    if(window.innerWidth<=700)return;
    const launcher=document.getElementById('headerCalendarBtn');if(!isVisible(launcher))return;
    const anchor=launcher.getBoundingClientRect(),width=dialog.getBoundingClientRect().width,top=anchor.bottom+12,available=window.innerHeight-top-16;
    if(available<360||anchor.bottom<0||anchor.top>window.innerHeight)return;
    const left=Math.max(16,Math.min(anchor.right-width,window.innerWidth-width-16));
    Object.assign(dialog.style,{margin:'0',inset:'auto',left:left+'px',top:top+'px',maxHeight:available+'px'});
  }
  function open(source){
    if(blocked()||dialog?.open)return false;window.JPWCalendarFeed?.resumeForSession?.();disposed=false;const inst=ensureDialog();opener=source instanceof HTMLElement?source:document.activeElement;inst.st.active=true;dialog.showModal();positionDialog();document.getElementById('headerCalendarBtn')?.setAttribute('aria-expanded','true');
    if(inst.st.form){inst.st.stage='form';renderForm(inst);}refresh(inst);(inst.st.form?inst.formHost.querySelector('[name="title"]'):inst.panel.querySelector('[data-calendar-action="close"]'))?.focus();return true;
  }
  function close(restore=true){if(!dialog?.open)return;const inst=instances.get('calendarDialog');captureForm(inst);inst.st.active=false;inst.st.request++;clearClock(inst);dialog.close();if(restore&&opener?.isConnected){if(typeof shellRestoreHeaderFocus==='function')shellRestoreHeaderFocus(opener);else opener.focus({preventScroll:true});}}
  function mountWorkspace(root=document.getElementById('execEcal')){
    if(typeof root==='string')root=document.getElementById(root);if(!root)return null;window.JPWCalendarFeed?.resumeForSession?.();disposed=false;let inst=instances.get('calendarWorkspace');if(!inst||inst.root!==root)inst=factory(root,'calendarWorkspace',false);inst.st.active=true;refresh(inst);return inst.panel;
  }
  function deactivateWorkspace(){const inst=instances.get('calendarWorkspace');if(inst){captureForm(inst);inst.st.active=false;inst.st.request++;clearClock(inst);}}
  function resetContext(){
    prefsOpaque=false;close(false);for(const inst of instances.values()){clearClock(inst);inst.st.active=false;inst.st.request++;inst.st=state(inst.st.id);renderForm(inst);renderControls(inst);renderMonth(inst);renderAgenda(inst);renderNotice(inst);}
  }
  function disposeForSession(){resetContext();disposed=true;opener=null;}
  function validDraft(value){return value&&typeof value==='object'&&!Array.isArray(value)&&['task','appointment'].includes(value.kind)&&typeof value.title==='string'&&value.title.length<=200&&typeof value.notes==='string'&&value.notes.length<=10000&&/^\d{4}-\d{2}-\d{2}$/.test(value.date)&&typeof value.allDay==='boolean'&&['startTime','endDate','endTime','timeZone'].every(k=>typeof value[k]==='string')&&Object.keys(value).every(k=>['kind','title','notes','date','allDay','startTime','endDate','endTime','timeZone','startAtChoice','endAtChoice'].includes(k));}
  if(typeof jpwWorkspaceDraftProviders!=='undefined')jpwWorkspaceDraftProviders.set('calendar-agenda',(reset=false)=>{
    if(reset){resetContext();return [];}
    const drafts=[];for(const inst of instances.values()){captureForm(inst);if(inst.st.form)drafts.push({label:'Agenda — rascunho não salvo ('+(inst.isDialog?'calendário':'área de trabalho')+')',text:JSON.stringify(inst.st.form),baseReference:inst.st.baseReference,context:{kind:'calendar-agenda',id:inst.st.formId||null,surface:inst.isDialog?'dialog':'workspace'}});}return drafts;
  });
  window.JPWWorkspaceDrafts?.registerRestorer('calendar-agenda',{
    inspect(item){try{const value=JSON.parse(item.text);return {compatible:validDraft(value)&&item.context?.kind==='calendar-agenda'&&item.baseReference===reference()&&!Array.from(instances.values()).some(i=>i.st.form)&&snapshot().status==='OK',reason:'Os registros originais devem corresponder e não pode haver outra edição da agenda.'};}catch(_){return {compatible:false,reason:'Rascunho da agenda incompatível.'};}},
    reopen(item){if(!open())return {ok:false,reason:'Feche a janela atual antes de retomar a agenda.'};const inst=instances.get('calendarDialog'),prepared=window.JPWAgenda.queries.prepare({id:item.context.id});if(!prepared.ok)return {ok:false,reason:'A revisão original não está disponível.'};inst.st.form=JSON.parse(item.text);inst.st.formId=item.context.id;inst.st.token=prepared.token;inst.st.baseReference=reference();inst.st.stage='form';inst.st.errors=[];inst.st.ambiguities=[];renderForm(inst);inst.formHost.querySelector('[name="title"]')?.focus();return {ok:true};}
  });
  const invalidate=()=>Promise.all([...instances.values()].filter(inst=>inst.st.active&&(inst.isDialog?dialog?.open:isVisible(inst.root))).map(inst=>refresh(inst)));
  for(const name of ['jpw-agenda-change','jpw-agenda-changed','jpw-economic-calendar-change','jpw-economic-calendar-updated','jpw-backup-status'])window.addEventListener(name,invalidate);
  window.addEventListener('storage',event=>{if(event.key===KEY){prefsOpaque=false;for(const inst of instances.values()){Object.assign(inst.st,preferences());inst.st.prefWriteBlocked=prefsOpaque||prefsReadFailed;renderControls(inst);}invalidate();}else invalidate();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)for(const inst of instances.values())clearClock(inst);else invalidate();});
  window.addEventListener('focus',invalidate);
  window.addEventListener('resize',positionDialog);
  document.getElementById('headerCalendarBtn')?.addEventListener('click',event=>open(event.currentTarget));
  window.JPWCalendar=Object.freeze({open,close,mountWorkspace,deactivateWorkspace,resetContext,disposeForSession,refresh:invalidate});
})();

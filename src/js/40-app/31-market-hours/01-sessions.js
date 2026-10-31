/* Public exchange calendars only. Pure prepared catalog lookup; no live-market inference. */
(function (global) {
  'use strict';
  const PHASES = ['continuous', 'preopen', 'auction', 'break', 'extended', 'closed', 'unknown'];
  const preparedCatalogs = new WeakSet();
  const nextPhaseIndices = new WeakMap();
  const regularOpeningIndices = new WeakMap();
  const MAX_TIME = 8640000000000000;
  function fail(message) { throw new Error('Calendário de bolsas inválido: ' + message); }
  function object(value, label) { if (!value || typeof value !== 'object' || Array.isArray(value)) fail(label); }
  function string(value, label) { if (typeof value !== 'string' || !value.trim()) fail(label); }
  function instant(value, label) { if (!Number.isSafeInteger(value) || Math.abs(value) > MAX_TIME) fail(label); }
  function date(value, label) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) fail(label);
    const n = Date.parse(value + 'T00:00:00Z');
    if (!Number.isFinite(n) || new Date(n).toISOString().slice(0, 10) !== value) fail(label);
  }
  function unique(items, label) {
    if (!Array.isArray(items) || !items.length) fail(label);
    const ids = new Set();
    items.forEach(item => { object(item, label); string(item.id, label + ' id'); if (ids.has(item.id)) fail(label + ' duplicado: ' + item.id); ids.add(item.id); });
    return ids;
  }
  function refs(value, ids, label) {
    if (!Array.isArray(value) || !value.length || value.some(id => !ids.has(id)) || new Set(value).size !== value.length) fail(label);
  }
  function clone(value) {
    if (Array.isArray(value)) return value.map(clone);
    if (value && typeof value === 'object') {
      const copy = {};
      Object.keys(value).forEach(key => {
        if (key === '__proto__' || key === 'constructor' || key === 'prototype') fail('chave não permitida');
        copy[key] = clone(value[key]);
      });
      return copy;
    }
    if (value !== null && !['string', 'number', 'boolean'].includes(typeof value)) fail('valor não serializável');
    if (typeof value === 'number' && !Number.isFinite(value)) fail('número não finito');
    return value;
  }
  function freeze(value) {
    if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); }
    return value;
  }
  function prepare(raw) {
    object(raw, 'pacote');
    const catalog = clone(raw);
    if (catalog.schemaVersion !== 1) fail('schemaVersion');
    string(catalog.tzdbVersion, 'tzdbVersion');
    const sources = unique(catalog.sources, 'fontes');
    catalog.sources.forEach(s => {
      string(s.title, 'título da fonte');
      if (typeof s.url !== 'string' || !/^https:\/\/[^\s/]+\//.test(s.url)) fail('URL HTTPS da fonte');
      date(s.verifiedAt, 'data de verificação da fonte');
      if (s.publishedAt !== null) date(s.publishedAt, 'data de publicação da fonte');
      if (s.sha256 !== undefined && !/^[a-f0-9]{64}$/.test(s.sha256)) fail('hash da fonte');
    });
    unique(catalog.venues, 'praças');
    catalog.venues.forEach(v => {
      ['name', 'city', 'country', 'region', 'timeZone'].forEach(key => string(v[key], key));
      if (!Number.isFinite(v.lat) || Math.abs(v.lat) > 90 || !Number.isFinite(v.lng) || Math.abs(v.lng) > 180) fail('coordenadas');
      unique(v.groups, 'grupos');
      v.groups.forEach(g => {
        string(g.label, 'nome do grupo'); object(g.coverage, 'cobertura');
        const c = g.coverage;
        instant(c.fromUtc, 'início da cobertura'); instant(c.untilUtc, 'fim da cobertura');
        if (c.fromUtc >= c.untilUtc) fail('cobertura vazia');
        date(c.verifiedAt, 'verificação da cobertura'); refs(c.sourceIds, sources, 'fontes da cobertura');
        if (!Array.isArray(g.periods) || !g.periods.length) fail('períodos ausentes');
        let cursor = c.fromUtc;
        g.periods.forEach((p, i) => {
          object(p, 'período'); instant(p.startUtc, 'início do período'); instant(p.endUtc, 'fim do período');
          if (p.startUtc !== cursor || p.endUtc <= p.startUtc || p.endUtc > c.untilUtc) fail('lacuna ou sobreposição de períodos');
          if (!PHASES.includes(p.phase)) fail('fase ' + p.phase);
          string(p.reason, 'motivo do período');
          if (p.sourceIds !== undefined) refs(p.sourceIds, sources, 'fontes do período');
          if (p.transitionWindow !== undefined) {
            const w = p.transitionWindow; object(w, 'janela de transição');
            instant(w.earliestUtc, 'primeiro instante da janela'); instant(w.latestUtc, 'último instante da janela');
            if (w.earliestUtc < p.startUtc || w.earliestUtc > w.latestUtc || w.latestUtc !== p.endUtc || !PHASES.includes(w.nextPhase) || !g.periods[i + 1] || g.periods[i + 1].phase !== w.nextPhase) fail('janela de transição inconsistente');
          }
          cursor = p.endUtc;
        });
        if (cursor !== c.untilUtc) fail('fim da cobertura não materializado');
        const indices = new Array(g.periods.length).fill(-1);
        for (let i = g.periods.length - 2; i >= 0; i--) {
          indices[i] = g.periods[i + 1].phase !== g.periods[i].phase ? i + 1 : indices[i + 1];
        }
        nextPhaseIndices.set(g, Object.freeze(indices));
      });
    });
    catalog.venues.forEach(prepareRegularOpenings);
    freeze(catalog); preparedCatalogs.add(catalog); return catalog;
  }
  function findPeriod(periods, utcMs) {
    let lo = 0, hi = periods.length - 1;
    while (lo <= hi) {
      const mid = (lo + hi) >>> 1, p = periods[mid];
      if (utcMs < p.startUtc) hi = mid - 1;
      else if (utcMs >= p.endUtc) lo = mid + 1;
      else return mid;
    }
    return -1;
  }
  function groupAt(group, utcMs) {
    const c = group.coverage;
    const index = utcMs < c.fromUtc || utcMs >= c.untilUtc ? -1 : findPeriod(group.periods, utcMs);
    if (index < 0) return {id: group.id, label: group.label, phase: 'unknown', reason: 'Fora da cobertura confirmada do calendário', coverage: c, sourceIds: c.sourceIds, nextTransition: null};
    const p = group.periods[index], nextIndex = nextPhaseIndices.get(group)[index], next = group.periods[nextIndex];
    // The last period before the indexed phase change owns its transition window.
    const transition = p.transitionWindow || (next ? group.periods[nextIndex - 1].transitionWindow || {earliestUtc: next.startUtc, latestUtc: next.startUtc, nextPhase: next.phase} : null);
    return {id: group.id, label: group.label, phase: p.phase, reason: p.reason, coverage: c, sourceIds: p.sourceIds || c.sourceIds, nextTransition: transition ? {...transition} : null};
  }
  function isRegularOpen(status) {
    if (!status || typeof status !== 'object' || Array.isArray(status) || !Array.isArray(status.groups) || !status.groups.length) return false;
    let continuous = false;
    for (const group of status.groups) {
      if (!group || typeof group !== 'object' || Array.isArray(group) || !PHASES.includes(group.phase) || group.phase === 'unknown') return false;
      if (group.phase === 'continuous') continuous = true;
    }
    return continuous;
  }
  function prepareRegularOpenings(venue) {
    const fromUtc = Math.max(...venue.groups.map(g => g.coverage.fromUtc));
    const untilUtc = Math.min(...venue.groups.map(g => g.coverage.untilUtc));
    const times = new Set([fromUtc, untilUtc]), entries = [];
    venue.groups.forEach(group => group.periods.forEach((period, i) => {
      if (period.startUtc > fromUtc && period.startUtc < untilUtc) times.add(period.startUtc);
      const previous = group.periods[i - 1];
      if (period.phase !== 'continuous' || !previous || previous.phase === 'continuous') return;
      let prior = i - 1;
      while (prior >= 0 && group.periods[prior].phase === 'auction') prior--;
      const kind = previous.phase === 'break' || previous.phase === 'auction' && prior >= 0 && ['continuous', 'break'].includes(group.periods[prior].phase) ? 'resume' : 'open';
      entries.push({earliestUtc: previous.transitionWindow?.earliestUtc ?? period.startUtc, latestUtc: period.startUtc, kind});
    }));
    const boundaries = Array.from(times).sort((a, b) => a - b);
    const spans = boundaries.slice(0, -1).map((startUtc, i) => {
      const groups = venue.groups.map(group => groupAt(group, startUtc));
      return {startUtc, endUtc: boundaries[i + 1], open: isRegularOpen({groups}), unknown: groups.some(group => group.phase === 'unknown'), next: null};
    });
    let next = null;
    for (let i = spans.length - 1; i >= 0; i--) {
      const span = spans[i], previous = spans[i - 1];
      if (span.open || span.unknown) next = null;
      span.next = next;
      if (span.open && previous && !previous.open && !previous.unknown) {
        // The first of overlapping segment entries opens the venue: min of both bounds.
        const overlapping = entries.filter(entry => entry.earliestUtc <= span.startUtc && entry.latestUtc >= span.startUtc);
        next = Object.freeze({earliestUtc: Math.min(...overlapping.map(entry => entry.earliestUtc)), latestUtc: span.startUtc, kind: overlapping.every(entry => entry.kind === 'resume') ? 'resume' : 'open'});
      }
    }
    regularOpeningIndices.set(venue, Object.freeze(spans.map(span => Object.freeze({startUtc: span.startUtc, endUtc: span.endUtc, next: span.next}))));
  }
  function regularOpeningAt(venue, utcMs) {
    const spans = regularOpeningIndices.get(venue), index = findPeriod(spans, utcMs);
    return index < 0 || !spans[index].next ? null : {...spans[index].next};
  }
  function at(catalog, utcMs) {
    if (!preparedCatalogs.has(catalog)) fail('prepare deve validar o pacote antes da consulta');
    instant(utcMs, 'instante de consulta');
    const counts = {total: catalog.venues.length, continuous: 0, preopen: 0, auction: 0, break: 0, extended: 0, closed: 0, unknown: 0, mixed: 0, regularOpen: 0};
    const venues = catalog.venues.map(v => {
      const groups = v.groups.map(g => groupAt(g, utcMs));
      const missing = groups.filter(g => g.phase === 'unknown');
      const phase = missing.length ? 'unknown' : groups.every(g => g.phase === groups[0].phase) ? groups[0].phase : 'mixed';
      counts[phase]++;
      if (isRegularOpen({groups})) counts.regularOpen++;
      const transitions = groups.map(g => g.nextTransition).filter(Boolean).sort((a, b) => a.earliestUtc - b.earliestUtc || a.latestUtc - b.latestUtc);
      // No aggregate countdown while a scoped group is unknown; known group details remain visible.
      const untilUtc = Math.min(...groups.map(g => g.coverage.untilUtc));
      const transition = missing.length ? null : transitions.find(w => w.latestUtc < untilUtc);
      const nextGroups = transition ? v.groups.map(g => groupAt(g, transition.latestUtc)) : [];
      const nextPhase = nextGroups.some(g => g.phase === 'unknown') ? 'unknown' : nextGroups.every(g => g.phase === nextGroups[0].phase) ? nextGroups[0]?.phase : 'mixed';
      return {id: v.id, phase, groups, nextRegularOpen: regularOpeningAt(v, utcMs), coverage: {fromUtc: Math.max(...groups.map(g => g.coverage.fromUtc)), untilUtc: Math.min(...groups.map(g => g.coverage.untilUtc))}, reason: missing.length ? 'Cobertura parcial ou não confirmada: ' + missing.map(g => g.id + ' (' + g.reason + ')').join('; ') : [...new Set(groups.map(g => g.reason))].join('; '), nextTransition: transition ? {...transition, nextPhase: nextPhase} : null};
    });
    return {asOf: utcMs, venues, counts};
  }
  global.JPWMarketSessions = Object.freeze({prepare, at, isRegularOpen});
})(globalThis);

/* Independent indicative FX convention. Equity calendars and financial state remain separate. */
(function(global){
  'use strict';
  const zones=Object.freeze(['device','UTC','Australia/Sydney','Asia/Tokyo','Europe/London','America/New_York','America/Sao_Paulo']);
  function validate(raw){
    if(typeof raw!=='string'||raw.length>256)throw Error('Preferência de fuso inválida.');
    const value=JSON.parse(raw);
    if(!value||Array.isArray(value)||typeof value!=='object'||value.schemaVersion!==1||!zones.includes(value.timeZone)||Object.keys(value).length!==2)throw Error('Preferência de fuso incompatível.');
    return Object.freeze({schemaVersion:1,timeZone:value.timeZone});
  }
  const prepared=new WeakSet();
  function prepare(raw){
    if(raw?.convention?.id!=='forex-com-local-v1'||raw?.convention?.kind!=='indicative-fx-session'||!raw.displayDays)throw Error('Convenção Forex incompatível.');
    const catalog=global.JPWMarketSessions.prepare(raw);
    const ids=['fx-sydney','fx-tokyo','fx-london','fx-new-york'];
    if(catalog.venues.length!==4||catalog.venues.some((v,i)=>v.id!==ids[i]))throw Error('Centros Forex incompatíveis.');
    for(const zone of zones.filter(z=>z!=='device')){
      const days=catalog.displayDays[zone];
      if(!Array.isArray(days)||!days.length||days.some((d,i)=>!Number.isSafeInteger(d.fromUtc)||!Number.isSafeInteger(d.untilUtc)||d.untilUtc<=d.fromUtc||i&&days[i-1].untilUtc!==d.fromUtc||!Array.isArray(d.ticks)||d.ticks.some(t=>!Number.isSafeInteger(t.utc)||t.utc<d.fromUtc||t.utc>d.untilUtc||!/^\d{2}:\d{2}$/.test(t.label)||!/^[-+]\d{4}$/.test(t.offset))))throw Error('Dias de exibição Forex inválidos.');
    }
    prepared.add(catalog);return catalog;
  }
  function requirePrepared(catalog){if(!prepared.has(catalog))throw Error('Catálogo Forex não preparado.');}
  function at(catalog,utcMs){requirePrepared(catalog);return global.JPWMarketSessions.at(catalog,utcMs);}
  const deviceDayCache=new Map();
  function browserDay(utcMs,zone){
    const formatter=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});
    function parts(at){return Object.fromEntries(formatter.formatToParts(at).filter(p=>p.type!=='literal').map(p=>[p.type,p.value]));}
    function dateAt(at){const p=parts(at);return p.year+'-'+p.month+'-'+p.day;}
    const day=dateAt(utcMs),key=zone+'|'+day;if(deviceDayCache.has(key))return deviceDayCache.get(key);
    function boundary(target){let lo=utcMs-129600000,hi=utcMs+129600000;while(lo<hi){const mid=Math.floor((lo+hi)/2);if(dateAt(mid)<target)lo=mid+1;else hi=mid;}return lo;}
    const next=new Date(Date.parse(day+'T00:00:00Z')+86400000).toISOString().slice(0,10),fromUtc=boundary(day),untilUtc=boundary(next);
    if(!(fromUtc<=utcMs&&utcMs<untilUtc))throw Error('Dia civil do dispositivo não pôde ser determinado.');
    const ticks=[];
    function tick(utc){const p=parts(utc),local=Date.UTC(+p.year,+p.month-1,+p.day,+p.hour,+p.minute,+p.second),offset=Math.round((local-Math.floor(utc/1000)*1000)/60000),absolute=Math.abs(offset);return Object.freeze({utc,label:p.hour+':'+p.minute,offset:(offset<0?'-':'+')+String(Math.floor(absolute/60)).padStart(2,'0')+String(absolute%60).padStart(2,'0')});}
    for(let utc=fromUtc;utc<=untilUtc;utc+=3600000)ticks.push(tick(utc));if(ticks[ticks.length-1].utc!==untilUtc)ticks.push(tick(untilUtc));
    const value=Object.freeze({date:day,fromUtc,untilUtc,ticks:Object.freeze(ticks),displaySource:'browser-intl'});deviceDayCache.set(key,value);if(deviceDayCache.size>8)deviceDayCache.delete(deviceDayCache.keys().next().value);return value;
  }
  function timeline(catalog,utcMs,zone,options){
    requirePrepared(catalog);if(!Number.isSafeInteger(utcMs))throw Error('Instante Forex inválido.');
    const compiled=Object.hasOwn(catalog.displayDays,zone);if(!compiled&&!options?.device)throw Error('Fuso fora do catálogo temporal.');
    const day=compiled?catalog.displayDays[zone].find(d=>utcMs>=d.fromUtc&&utcMs<d.untilUtc):browserDay(utcMs,zone);if(!day)return null;
    const horizon=catalog.displayDays.UTC;if(!compiled&&(day.date<horizon[0].date||day.date>horizon[horizon.length-1].date))return null;
    return {...day,rows:catalog.venues.map(v=>({id:v.id,segments:v.groups.flatMap(g=>g.periods.filter(p=>p.phase==='continuous'&&p.endUtc>day.fromUtc&&p.startUtc<day.untilUtc).map(p=>({fromUtc:Math.max(day.fromUtc,p.startUtc),untilUtc:Math.min(day.untilUtc,p.endUtc)})))}))};
  }
  global.JPWMarketSessionsViewPreference=Object.freeze({key:'jpwealth_market_sessions_view_v1',validate,zones});
  global.JPWForexSessions=Object.freeze({prepare,at,timeline});
})(globalThis);

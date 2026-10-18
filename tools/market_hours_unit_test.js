'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const cp = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const engineFile = path.join(root, 'src/js/40-app/31-market-hours/01-sessions.js');
let total = 0;
function test(name, fn) { try { fn(); total++; console.log('PASS ' + name); } catch (e) { console.error('FAIL ' + name); throw e; } }
const context = vm.createContext({});
if (fs.existsSync(engineFile)) vm.runInContext(fs.readFileSync(engineFile, 'utf8'), context);
const api = context.JPWMarketSessions;
test('pure sessions API exists', () => assert.equal(typeof api?.prepare, 'function'));
test('shared regular-open predicate API exists', () => assert.equal(typeof api?.isRegularOpen, 'function'));
// These cases catch treating mixed/unknown or a nonempty malformed group as confirmed trading.
test('regular-open predicate requires known groups and at least one continuous group',()=>{
 const cases=[
  [['continuous'],true],[['continuous','extended'],true],[['closed','continuous'],true],
  [['preopen','auction'],false],[['break','extended'],false],[['closed'],false],
  [['continuous','unknown'],false],[['unknown','continuous'],false],[['continuous','open'],false],
  [[],false]
 ];
 for(const [phases,want] of cases){
  const status={phase:phases.length===1?phases[0]:'mixed',groups:phases.map(phase=>({phase}))};
  const before=JSON.stringify(status);
  assert.equal(api.isRegularOpen(status),want,JSON.stringify(phases));
  assert.equal(JSON.stringify(status),before,'predicate must not mutate the status');
 }
});
test('regular-open predicate refuses invalid statuses and malformed or sparse groups',()=>{
 const sparse=[{phase:'continuous'},,];
 const groupArray=[];groupArray.phase='continuous';
 for(const status of [null,undefined,false,0,'continuous',[],{}, {groups:null},{groups:{}},
  {groups:[null]},{groups:[undefined]},{groups:[{}]},{groups:[{phase:7}]},
  {groups:[{phase:'continuous'},null]},{groups:[groupArray]},{groups:sparse}]){
  assert.equal(api.isRegularOpen(status),false);
 }
});
const t = s => Date.parse('2026-10-15T' + s + 'Z');
const source = {id:'s', title:'Synthetic source', url:'https://example.org/official-fixture', publishedAt:'2026-10-01', verifiedAt:'2026-10-15'};
function fixture() {
 const spans = [['00:00','09:00','closed'],['09:00','11:30','continuous'],['11:30','12:30','break'],['12:30','15:25','continuous'],['15:25','15:30','auction'],['15:30','23:59','closed']];
 return {schemaVersion:1,tzdbVersion:'synthetic-UTC',sources:[source],venues:[{id:'x',name:'X',city:'X',country:'XX',region:'test',timeZone:'UTC',lat:0,lng:0,groups:[{id:'cash',label:'Cash',coverage:{fromUtc:t('00:00'),untilUtc:t('23:59'),verifiedAt:'2026-10-15',sourceIds:['s']},periods:spans.map(([a,b,p])=>({startUtc:t(a),endUtc:t(b),phase:p,reason:p,sourceIds:['s']}))}]}]};
}
const raw=fixture(), before=JSON.stringify(raw), prepared=api.prepare(raw);
test('regular-open filter agrees with synthetic snapshot counts including mixed and partial unknown',()=>{
 const f=fixture();
 const second=JSON.parse(JSON.stringify(f.venues[0]));second.id='mixed-open';
 const extended=JSON.parse(JSON.stringify(second.groups[0]));extended.id='extended';extended.periods=extended.periods.map(p=>({...p,phase:'extended'}));second.groups.push(extended);
 const third=JSON.parse(JSON.stringify(second));third.id='partial-unknown';third.groups[1].periods=third.groups[1].periods.map(p=>({...p,phase:'unknown'}));
 f.venues.push(second,third);const c=api.prepare(f);
 for(const [instant,ids] of [[t('09:00'),['x','mixed-open']],[t('11:30'),[]],[t('23:59'),[]]]){
  const snapshot=api.at(c,instant),open=snapshot.venues.filter(api.isRegularOpen);
  assert.deepEqual(Array.from(open,v=>v.id),ids);
  assert.equal(snapshot.counts.regularOpen,ids.length);
  assert.equal(open.length,snapshot.counts.regularOpen);
 }
});
test('prepare preserves raw and freezes every child',()=>{assert.equal(JSON.stringify(raw),before);assert(Object.isFrozen(prepared));assert(Object.isFrozen(prepared.venues[0].groups[0].periods[0]));assert(!Object.isFrozen(raw));});
for(const [time,phase] of [['08:59:59.999','closed'],['09:00','continuous'],['11:30','break'],['12:30','continuous'],['15:25','auction'],['15:30','closed']]) test('half-open boundary '+time,()=>assert.equal(api.at(prepared,t(time)).venues[0].phase,phase));
test('coverage boundaries are unknown with no invented future',()=>{for(const n of [t('00:00')-1,t('23:59'),Date.parse('2027-01-01')]){const s=api.at(prepared,n);assert.equal(s.venues[0].phase,'unknown');assert.equal(s.venues[0].nextTransition,null);assert.equal(s.counts.unknown,1);}});
test('last period has no next transition outside coverage',()=>assert.equal(api.at(prepared,t('20:00')).venues[0].nextTransition,null));
test('next transition exact and deterministic',()=>{const s=api.at(prepared,t('09:00'));assert.equal(s.venues[0].nextTransition.earliestUtc,t('11:30'));assert.equal(s.venues[0].nextTransition.nextPhase,'break');assert.equal(JSON.stringify(s),JSON.stringify(api.at(prepared,t('09:00'))));assert.notEqual(s,api.at(prepared,t('09:00')));});
test('aggregate next transition predicts shared target phase and respects joint coverage',()=>{const f=fixture();const g=JSON.parse(JSON.stringify(f.venues[0].groups[0]));g.id='other';g.periods[1].phase='preopen';f.venues[0].groups.push(g);const p=api.prepare(f);assert.equal(api.at(p,t('09:00')).venues[0].nextTransition.nextPhase,'break');g.coverage.untilUtc=t('10:00');g.periods=g.periods.slice(0,2);g.periods[1].endUtc=t('10:00');assert.equal(api.at(api.prepare(f),t('09:00')).venues[0].nextTransition,null);});
test('countdown skips reason-only boundaries without scanning periods per tick',()=>{const f=fixture();f.venues[0].groups[0].periods[1].phase='closed';const s=api.at(api.prepare(f),t('08:00'));assert.equal(s.venues[0].nextTransition.nextPhase,'break');assert.equal(s.venues[0].nextTransition.earliestUtc,t('11:30'));});
test('random window stays a window',()=>{const f=fixture(),p=f.venues[0].groups[0].periods[4];p.transitionWindow={earliestUtc:t('15:28'),latestUtc:t('15:30'),nextPhase:'closed'};const s=api.at(api.prepare(f),t('15:29'));assert.equal(s.venues[0].phase,'auction');assert.equal(s.venues[0].nextTransition.earliestUtc,t('15:28'));assert.equal(s.venues[0].nextTransition.latestUtc,t('15:30'));});
test('future random window survives reason-only boundaries for group and venue',()=>{
 const f=fixture(),g=f.venues[0].groups[0];
 g.coverage.fromUtc=0;g.coverage.untilUtc=4000;
 g.periods=[
  {startUtc:0,endUtc:1000,phase:'auction',reason:'orders'},
  {startUtc:1000,endUtc:3000,phase:'auction',reason:'limit orders only',transitionWindow:{earliestUtc:2000,latestUtc:3000,nextPhase:'continuous'}},
  {startUtc:3000,endUtc:4000,phase:'continuous',reason:'regular'}
 ];
 const c=api.prepare(f);
 for(const instant of [500,1000,1500,2000,2999]){
  const venue=api.at(c,instant).venues[0];
  assert.equal(venue.phase,'auction');
  for(const status of [venue,venue.groups[0]])assert.deepEqual(JSON.parse(JSON.stringify(status.nextTransition)),{earliestUtc:2000,latestUtc:3000,nextPhase:'continuous'},'window at '+instant);
 }
 assert.equal(api.at(c,3000).venues[0].phase,'continuous');
 assert.equal(api.at(c,3000).venues[0].nextTransition,null);
});
test('reason-only skip stops at unknown before later continuous phase',()=>{
 const f=fixture(),g=f.venues[0].groups[0];
 g.coverage.fromUtc=0;g.coverage.untilUtc=4000;
 g.periods=[
  {startUtc:0,endUtc:1000,phase:'closed',reason:'overnight'},
  {startUtc:1000,endUtc:2000,phase:'closed',reason:'holiday'},
  {startUtc:2000,endUtc:3000,phase:'unknown',reason:'unconfirmed session'},
  {startUtc:3000,endUtc:4000,phase:'continuous',reason:'regular'}
 ];
 const c=api.prepare(f);
 for(const instant of [500,1500]){
  const venue=api.at(c,instant).venues[0];
  for(const status of [venue,venue.groups[0]])assert.deepEqual(JSON.parse(JSON.stringify(status.nextTransition)),{earliestUtc:2000,latestUtc:2000,nextPhase:'unknown'});
 }
 const venue=api.at(c,2500).venues[0];
 assert.equal(venue.phase,'unknown');assert.equal(venue.nextTransition,null);
});
test('group aggregation counts each venue once and preserves unknown groups',()=>{const f=fixture();const a=JSON.parse(JSON.stringify(f.venues[0].groups[0]));a.id='other';a.periods=a.periods.map(p=>({...p,phase:'extended'}));f.venues[0].groups.push(a);let s=api.at(api.prepare(f),t('09:00'));assert.equal(s.venues[0].phase,'mixed');assert.equal(s.counts.mixed,1);assert.equal(s.counts.regularOpen,1);a.periods=a.periods.map(p=>({...p,phase:'unknown',reason:'not confirmed'}));s=api.at(api.prepare(f),t('09:00'));assert.equal(s.venues[0].phase,'unknown');assert.equal(s.venues[0].groups[0].phase,'continuous');assert.equal(s.counts.regularOpen,0);assert.match(s.venues[0].reason,/other/);assert.equal(Object.entries(s.counts).filter(([k])=>!['total','regularOpen'].includes(k)).reduce((n,[,v])=>n+v,0),s.counts.total);});
test('invalid catalog refuses gaps overlaps bad phases missing sources and unsafe dates',()=>{for(const mutate of [f=>f.venues[0].groups[0].periods[1].startUtc++,f=>f.venues[0].groups[0].periods[1].startUtc--,f=>f.venues[0].groups[0].periods[0].phase='open',f=>f.sources=[],f=>f.venues[0].groups[0].coverage.untilUtc=Infinity,f=>f.venues[0].groups[0].coverage.verifiedAt='2026-02-30']){const f=fixture();mutate(f);assert.throws(()=>api.prepare(f));}});
test('instant input rejects coercion invalid dates fractions and unprepared raw',()=>{for(const n of [NaN,Infinity,'2026-10-15',undefined,1.1,8.65e15])assert.throws(()=>api.at(prepared,n));assert.throws(()=>api.at(raw,t('09:00')));});
test('snapshot writes cannot change prepared catalog',()=>{const s=api.at(prepared,t('09:00'));try{s.venues[0].groups[0].coverage.fromUtc=0;}catch(e){}assert.equal(api.at(prepared,t('09:00')).venues[0].groups[0].coverage.fromUtc,t('00:00'));});

// Approved 2026-10-16 upcoming contract: explicit phases/windows, never reason text.
function upcomingFixture(groups) {
 const f=fixture();
 f.venues[0].groups=groups.map((spans,i)=>({id:'group'+i,label:'Group '+i,coverage:{fromUtc:spans[0][0],untilUtc:spans.at(-1)[1],verifiedAt:'2026-10-15',sourceIds:['s']},periods:spans.map(([startUtc,endUtc,phase,window,reason])=>({startUtc,endUtc,phase,reason:reason||phase,...(window?{transitionWindow:{earliestUtc:window[0],latestUtc:endUtc,nextPhase:window[1]}}:{})}))}));
 return api.prepare(f);
}
function nextOpen(c,instant) {const value=api.at(c,instant).venues[0].nextRegularOpen;return value===undefined?value:JSON.parse(JSON.stringify(value));}
const opening=(earliestUtc,latestUtc=earliestUtc,kind='open')=>({earliestUtc,latestUtc,kind});
test('upcoming exact entry is independent of next phase and absent while already regular-open',()=>{
 const c=upcomingFixture([[[0,10,'closed'],[10,20,'preopen'],[20,30,'auction'],[30,40,'continuous'],[40,50,'break'],[50,60,'continuous'],[60,70,'closed']]]);
 assert.deepEqual(nextOpen(c,0),opening(30));assert.deepEqual(nextOpen(c,25),opening(30));
 assert.equal(api.at(c,0).venues[0].nextTransition.nextPhase,'preopen');
 assert.equal(nextOpen(c,30),null);assert.deepEqual(nextOpen(c,40),opening(50,50,'resume'));
 assert.equal(nextOpen(c,60),null);
});
test('upcoming unknown current intermediate and joint coverage are barriers',()=>{
 for(const [groups,instant] of [
  [[[[0,10,'unknown'],[10,20,'continuous']]],0],
  [[[[0,10,'closed'],[10,20,'unknown'],[20,30,'continuous']]],0],
  [[[[0,10,'closed'],[10,20,'continuous']],[[0,10,'closed']]],0],
  [[[[10,20,'closed'],[20,30,'continuous']]],0],
  [[[[0,10,'closed'],[10,20,'continuous']]],20]
 ]) assert.equal(nextOpen(upcomingFixture(groups),instant),null);
});
test('upcoming resumes only from a break or intraday auction with explicit continuous or break predecessor',()=>{
 for(const [phases,kind] of [[['continuous','break'],'resume'],[['continuous','auction'],'resume'],[['break','auction'],'resume'],[['closed','auction'],'open'],[['extended','auction'],'open'],[['closed','preopen'],'open']]){
  const c=upcomingFixture([[...phases.map((phase,i)=>[i*10,(i+1)*10,phase]),[20,30,'continuous']]]);
  assert.deepEqual(nextOpen(c,15),opening(20,20,kind),phases.join('/'));
 }
 const c=upcomingFixture([[[0,10,'closed',null,'Retoma após intervalo'],[10,20,'continuous']]]);
 assert.deepEqual(nextOpen(c,0),opening(10),'free text must not turn opening into resume');
});
test('upcoming skips known holiday and reason-only spans but never unknown to reach a later opening',()=>{
 const c=upcomingFixture([[[0,10,'closed',null,'overnight'],[10,200000000,'closed',null,'holiday'],[200000000,200000100,'auction',[200000050,'continuous']],[200000100,200000200,'continuous']]]);
 for(const n of [0,15,200000075]) assert.deepEqual(nextOpen(c,n),opening(200000050,200000100));
 const blocked=upcomingFixture([[[0,10,'closed'],[10,20,'unknown'],[20,30,'closed'],[30,40,'continuous']]]);
 assert.equal(nextOpen(blocked,0),null);assert.deepEqual(nextOpen(blocked,25),opening(30));
});
test('upcoming aggregates mixed groups and overlapping entry windows without losing either bound',()=>{
 const c=upcomingFixture([
  [[0,12,'auction',[10,'continuous']],[12,30,'continuous']],
  [[0,13,'auction',[9,'continuous']],[13,30,'continuous']],
  [[0,30,'extended']]
 ]);
 assert.deepEqual(nextOpen(c,0),opening(9,12));assert.deepEqual(nextOpen(c,11),opening(9,12));
 assert.equal(nextOpen(c,12),null);assert.equal(api.at(c,12).counts.regularOpen,1);
 const partial=upcomingFixture([[[0,10,'closed'],[10,30,'continuous']],[[0,30,'unknown']]]);
 assert.equal(nextOpen(partial,0),null);
});
test('upcoming ignores segment openings that do not reopen the aggregated venue',()=>{
 const c=upcomingFixture([[[0,10,'continuous'],[10,20,'break'],[20,40,'continuous']],[[0,25,'extended'],[25,40,'continuous']]]);
 assert.equal(nextOpen(c,5),null);assert.deepEqual(nextOpen(c,15),opening(20,20,'resume'));
 assert.equal(nextOpen(c,22),null);
});
test('upcoming prepared results are deterministic copies and preserve indexed window across unrelated boundaries',()=>{
 const c=upcomingFixture([[[0,10,'auction'],[10,30,'auction',[21,'continuous']],[30,50,'continuous']],[[0,5,'closed'],[5,15,'extended'],[15,50,'closed']]]);
 const first=api.at(c,1).venues[0].nextRegularOpen;assert.deepEqual(JSON.parse(JSON.stringify(first)),opening(21,30));
 first.earliestUtc=-100;
 for(const n of [1,6,16,22,29])assert.deepEqual(nextOpen(c,n),opening(21,30));
});

if(process.env.MARKET_HOURS_ENGINE_ONLY!=='1') {
 const python=process.env.MARKET_HOURS_PYTHON || '/private/tmp/jpw-quality-audit-20261012-01a131dc/runtime/bin/python3';
 const tmp=fs.mkdtempSync('/private/tmp/jpw-market-hours-test-');
 const rules={schemaVersion:1,tzdbVersion:'2026b',fromDate:'2026-10-15',untilDate:'2026-11-03',sources:['s'],venues:[{id:'x',name:'X',city:'X',country:'XX',region:'test',timeZone:'America/New_York',lat:0,lng:0,groups:[{id:'cash',label:'Cash',verifiedAt:'2026-10-15',sourceIds:['s'],weekdays:[1,2,3,4,5],schedule:[{validFrom:'2026-10-01',validUntil:'2026-11-01',sourceIds:['s'],sessions:[{start:'09:30',end:'16:00',phase:'continuous',reason:'regular'}]},{validFrom:'2026-11-02',validUntil:'2026-12-31',sourceIds:['s'],sessions:[{start:'10:00',end:'16:00',phase:'continuous',reason:'new schedule'}]}],exceptions:[{date:'2026-10-16',closedReason:'holiday',sourceIds:['s']},{date:'2026-10-18',sessions:[{start:'11:00',end:'12:00',phase:'continuous',reason:'special Sunday'}],sourceIds:['s']},{date:'2026-10-19',unknownReason:'special hours unconfirmed',sourceIds:['s']}]}]}]};
 fs.writeFileSync(path.join(tmp,'sources.json'),JSON.stringify({schemaVersion:1,sources:[source]}));
 const run=(r)=>{fs.writeFileSync(path.join(tmp,'rules.json'),JSON.stringify(r));return cp.spawnSync(python,[path.join(root,'tools/compile_market_hours.py'),'--sources',path.join(tmp,'sources.json'),'--rules',path.join(tmp,'rules.json'),'--out',path.join(tmp,'out.json')],{cwd:root,encoding:'utf8'});};
 let result;
 test('compiler exists and materializes complete deterministic coverage',()=>{result=run(rules);assert.equal(result.status,0,result.stderr);const bytes=fs.readFileSync(path.join(tmp,'out.json'),'utf8');assert.equal(run(rules).status,0);assert.equal(bytes,fs.readFileSync(path.join(tmp,'out.json'),'utf8'));});
 const c=api.prepare(JSON.parse(fs.readFileSync(path.join(tmp,'out.json'),'utf8')));
 test('compiler honors holiday unknown exception and Sunday precedence',()=>{for(const [date,phase] of [['2026-10-16T14:00Z','closed'],['2026-10-18T15:00Z','continuous'],['2026-10-19T14:00Z','unknown']])assert.equal(api.at(c,Date.parse(date)).venues[0].phase,phase);});
 test('compiler selects explicit schedule vigency and timezone DST',()=>{assert.equal(api.at(c,Date.parse('2026-10-30T13:30Z')).venues[0].phase,'continuous');assert.equal(api.at(c,Date.parse('2026-11-02T14:30Z')).venues[0].phase,'closed');assert.equal(api.at(c,Date.parse('2026-11-02T15:00Z')).venues[0].phase,'continuous');assert.equal(c.venues[0].groups[0].coverage.fromUtc,Date.parse('2026-10-15T04:00Z'));assert.equal(c.venues[0].groups[0].coverage.untilUtc,Date.parse('2026-11-04T05:00Z'));});
 test('compiler refuses invalid dates overlapping sessions missing vigency and timezone mismatch',()=>{for(const mutate of [r=>r.fromDate='2026-02-30',r=>r.venues[0].groups[0].schedule[0].sessions.push({start:'10:00',end:'11:00',phase:'auction',reason:'overlap'}),r=>delete r.venues[0].groups[0].schedule[0].validFrom,r=>r.tzdbVersion='2026e',r=>r.venues[0].groups[0].sourceIds=['absent']]){const r=JSON.parse(JSON.stringify(rules));mutate(r);const p=run(r);assert.notEqual(p.status,0,p.stdout);}});
 test('compiler rejects malformed inactive schedules instead of hiding invalid input',()=>{const r=JSON.parse(JSON.stringify(rules));r.untilDate='2026-10-16';r.venues[0].groups[0].schedule[1].sessions.push({start:'11:00',end:'12:00',phase:'auction',reason:'impossible overlap outside compilation dates'});assert.notEqual(run(r).status,0);});
 test('compiler keeps random windows and explicit unknown groups',()=>{const r=JSON.parse(JSON.stringify(rules));r.fromDate='2026-10-15';r.untilDate='2026-10-15';r.venues[0].groups[0].schedule[0].sessions=[{start:'09:00',end:'09:05',phase:'auction',reason:'random opening',transitionWindow:{earliest:'09:04',latest:'09:05',nextPhase:'continuous'}},{start:'09:05',end:'10:00',phase:'continuous',reason:'regular'}];const unknown=JSON.parse(JSON.stringify(r.venues[0].groups[0]));unknown.id='pending';unknown.unknownReason='Unconfirmed group';unknown.schedule=[];r.venues[0].groups.push(unknown);assert.equal(run(r).status,0);const c=api.prepare(JSON.parse(fs.readFileSync(path.join(tmp,'out.json'),'utf8')));const s=api.at(c,Date.parse('2026-10-15T13:04:30Z'));assert.equal(s.venues[0].phase,'unknown');assert.equal(s.venues[0].groups[0].nextTransition.earliestUtc,Date.parse('2026-10-15T13:04Z'));assert.equal(s.venues[0].groups[0].nextTransition.latestUtc,Date.parse('2026-10-15T13:05Z'));assert.equal(s.venues[0].groups[1].phase,'unknown');});
 test('compiler refuses DST ambiguity and preserves previous output on failure',()=>{const previous=fs.readFileSync(path.join(tmp,'out.json'),'utf8');for(const day of ['2026-03-08','2026-11-01']){const r=JSON.parse(JSON.stringify(rules));r.fromDate=day;r.untilDate=day;r.venues[0].groups[0].weekdays=[7];r.venues[0].groups[0].exceptions=[];r.venues[0].groups[0].schedule=[{validFrom:day,validUntil:day,sourceIds:['s'],sessions:[{start:day.includes('03-08')?'02:30':'01:30',end:'04:00',phase:'continuous',reason:'invalid local time'}]}];assert.notEqual(run(r).status,0);assert.equal(fs.readFileSync(path.join(tmp,'out.json'),'utf8'),previous);}});
 fs.rmSync(tmp,{recursive:true});
}

if(process.env.MARKET_HOURS_ENGINE_ONLY!=='1') {
 test('official catalog includes all sixteen contractual venues with preserved coverage',()=>{assert(fs.existsSync(path.join(root,'src/data/market-hours/calendar-v1.json')), 'compiled calendar must exist');const raw=JSON.parse(fs.readFileSync(path.join(root,'src/data/market-hours/calendar-v1.json'),'utf8'));const c=api.prepare(raw);assert.deepEqual(Array.from(c.venues,v=>v.id),['b3','nyse','nasdaq','tsx','lse','xetra','euronext-paris','jpx','hkex','sse','szse','nse','bse','krx','saudi','asx']);assert.equal(c.tzdbVersion,'2026b');for(const date of ['2026-10-15T14:00Z','2026-11-03T20:00Z','2027-01-01T00:00Z']){const s=api.at(c,Date.parse(date));assert.equal(Object.entries(s.counts).filter(([k])=>!['total','regularOpen'].includes(k)).reduce((n,[,v])=>n+v,0),16);}});
 const c=api.prepare(JSON.parse(fs.readFileSync(path.join(root,'src/data/market-hours/calendar-v1.json'),'utf8')));
 const status=(id,date)=>api.at(c,Date.parse(date)).venues.find(v=>v.id===id);
 test('regular-open filter agrees with official snapshot counts across dates and coverage boundaries',()=>{
  for(const date of ['2026-10-15T03:30Z','2026-10-15T14:00Z','2026-10-15T20:00Z','2026-11-03T14:00Z','2026-11-27T18:00Z','2027-01-01T00:00Z']){
   const snapshot=api.at(c,Date.parse(date));
   assert.equal(snapshot.venues.filter(api.isRegularOpen).length,snapshot.counts.regularOpen,date);
  }
  const snapshot=api.at(c,Date.parse('2026-11-03T20:00Z'));
  assert(snapshot.venues.filter(api.isRegularOpen).some(v=>v.id==='b3'));
  assert(!snapshot.venues.filter(api.isRegularOpen).some(v=>v.id==='bse'));
 });
 test('B3 November equity rule starts November 3 and after ambiguity remains unknown',()=>{assert.equal(status('b3','2026-10-26T20:00Z').phase,'unknown');assert.equal(status('b3','2026-10-15T20:00Z').phase,'unknown');assert.equal(status('b3','2026-11-03T20:00Z').phase,'continuous');assert.equal(status('b3','2026-11-03T20:55Z').phase,'auction');assert.equal(status('b3','2026-11-03T21:00Z').phase,'unknown');assert.equal(status('b3','2026-11-02T14:00Z').phase,'closed');assert.equal(status('b3','2026-12-24T14:00Z').phase,'closed');});
 test('NYSE stays continuous during closing imbalance and uses own early days',()=>{assert.equal(status('nyse','2026-10-15T19:55Z').phase,'continuous');assert.equal(status('nyse','2026-11-27T17:59Z').phase,'continuous');assert.equal(status('nyse','2026-11-27T18:00Z').phase,'closed');assert.equal(status('nyse','2026-11-26T15:00Z').phase,'closed');});
 test('official countdown crosses weekend and holiday but stops at unknown coverage',()=>{assert.equal(status('b3','2026-10-31T14:00Z').nextTransition.earliestUtc,Date.parse('2026-11-03T12:45Z'));assert.equal(status('nyse','2026-11-25T22:00Z').nextTransition.earliestUtc,Date.parse('2026-11-27T11:30Z'));const f=fixture();f.venues[0].groups[0].periods[1].phase='unknown';const s=api.at(api.prepare(f),t('08:00'));assert.equal(s.venues[0].nextTransition.nextPhase,'unknown');assert.equal(s.venues[0].nextTransition.earliestUtc,t('09:00'));});
 test('JPX lunch and preclosing preserve phases with official holiday override',()=>{assert.equal(status('jpx','2026-10-15T02:30Z').phase,'break');assert.equal(status('jpx','2026-10-15T03:30Z').phase,'continuous');assert.equal(status('jpx','2026-10-15T06:25Z').phase,'auction');assert.equal(status('jpx','2026-10-15T06:30Z').phase,'closed');assert.equal(status('jpx','2026-11-03T01:00Z').phase,'closed');assert.equal(status('jpx','2026-12-31T01:00Z').phase,'closed');});
}
console.log('PASS '+total+' market-hours tests');

// Approved Portfolio/Management plan. Reuse the existing DOM-boundary harness;
// production catalog, progress and controller run unchanged; no financial data.
import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const base=new URL('../',import.meta.url),source=fs.readFileSync(new URL('tools/learning_controller_test.mjs',base),'utf8');
const start=source.indexOf('class El{'),end=source.indexOf('function test(');assert(start>=0&&end>start,'Existing controller harness remains discoverable');
const helpers={fs,vm,assert,base,console,URL,structuredClone};vm.runInNewContext(source.slice(start,end)+';globalThis.createEnv=env;',helpers);const env=helpers.createEnv,plain=v=>JSON.parse(JSON.stringify(v));
let passed=0,failed=0;function test(id,fn){try{fn();passed++;console.log('PASS '+id);}catch(error){failed++;console.error('FAIL '+id+'\n'+error.stack);}}
const historical=(stepId,trackId='forex',schemaVersion=2,mode='journey')=>({schemaVersion,...(schemaVersion===2?{mode}:{}),catalogVersion:1,trackId,stepId,paused:true,steps:{[stepId]:{orientation:'seen',practice:null}}});
test('MGTGUIDE-01 Portfolio/Analysis has only the approved two visible lessons',()=>{
 const catalog=env().c.JPWLearningCatalog,t=catalog.tracks.find(t=>t.id==='research');assert.equal(t.title,'Portfólio');assert.deepEqual(Array.from(t.steps,s=>s.id),['research-forex','research-pivots']);assert.match(t.steps[0].instruction,/Portfólio.*Análise/);assert(!t.steps[0].instruction.includes('Research > Forex'));
});
test('MGTGUIDE-02 Management chapter is independent and precedes patrimonial planning without duplicate lesson IDs',()=>{
 const c=env().c.JPWLearningCatalog,journey=Array.from(c.journey,x=>x.id),m=c.tracks.find(t=>t.id==='management');assert(m,'Management track exists');assert.equal(m.module,'management');assert.deepEqual(journey.slice(0,4),['basics','research','management','planning']);assert.equal(m.steps[0].id,'forex-reserves');assert(m.steps.some(s=>s.id==='forex-accounting'));const all=c.tracks.flatMap(t=>t.steps).map(s=>s.id),ordered=c.journey.flatMap(t=>t.stepIds);assert.equal(new Set(all).size,all.length);assert.equal(new Set(ordered).size,ordered.length);assert.equal(ordered.length,all.length);
});
for(const id of ['forex-accounting','forex-reserves'])for(const schema of [1,2])test(`MGTGUIDE-03 old owner ${id}/v${schema} reads intact and remaps only on explicit resume`,()=>{
 const old=historical(id,'forex',schema),raw=JSON.stringify(old),e=env(raw),finance=e.data.get('jpwealth_v9_state');e.add('#management');e.add('#forexReservesPanel');assert.equal(e.writes(),0);const read=e.c.JPWLearningProgress.read(e.c.JPWLearningCatalog);assert.equal(read.ok,true);assert.equal(read.document.trackId,'forex');assert.equal(e.data.get('jpwealth_learning_guide_v1'),raw);e.c.JPWLearningGuide.resume();e.flush();const after=e.c.JPWLearningGuide.snapshot();assert.equal(after.trackId,'management');assert.equal(after.stepId,id);assert.deepEqual(plain(after.progress.steps),old.steps);assert.equal(e.data.get('jpwealth_v9_state'),finance);
});
for(const id of ['research-stocks-br','research-stocks-global','research-reits','research-others'])test('MGTGUIDE-04 retired placeholder '+id+' preserves records and resumes active Analysis',()=>{
 const old=historical(id,'research'),raw=JSON.stringify(old),e=env(raw);assert.equal(e.writes(),0);assert.equal(e.c.JPWLearningProgress.read(e.c.JPWLearningCatalog).ok,true);assert.equal(e.data.get('jpwealth_learning_guide_v1'),raw);assert(!e.c.JPWLearningCatalog.journey.flatMap(c=>c.stepIds).includes(id));e.add('#execNocoda');e.c.JPWLearningGuide.resume();e.flush();const after=e.c.JPWLearningGuide.snapshot();assert.equal(after.stepId,'research-forex');assert.deepEqual(plain(after.progress.steps),old.steps);assert.equal(after.progress.steps['research-forex'],undefined);
});
test('MGTGUIDE-05 Management remains reachable when Forex is frozen and pauses when Management is frozen',()=>{
 const e=env();e.c.JPWModuleAvailability.canAccess=id=>id!=='forex';e.add('#management');assert.equal(e.c.JPWLearningGuide.startJourney({stepId:'forex-accounting'}),true);e.flush();assert.equal(e.c.JPWLearningGuide.snapshot().paused,false);assert.equal(e.c.model.unavailable,false);e.c.JPWModuleAvailability.canAccess=id=>id!=='management';e.access();e.flush();assert.equal(e.c.model.unavailable,true);assert.deepEqual(plain(e.c.JPWLearningGuide.snapshot().progress.steps),{});
});
test('MGTGUIDE-06 new annual/daily explanations are read-only and advancing never confirms practice',()=>{
 const e=env(),track=e.c.JPWLearningCatalog.tracks.find(t=>t.id==='management');assert(track,'Management track exists');const steps=track.steps;for(const s of steps){assert.equal(s.kind,'read');assert.equal(s.practice,undefined);for(const speech of s.speech){assert.equal(typeof speech,'string');assert(speech.length<=280);assert((speech.match(/[.!?](?:\s|$)/g)||[]).length<=2);}}e.add('#management');e.c.JPWLearningGuide.startJourney({stepId:'management-plan'});e.flush();const financial=e.data.get('jpwealth_v9_state');e.c.cb.skip();e.flush();assert.equal(e.data.get('jpwealth_v9_state'),financial);assert(Object.values(e.c.JPWLearningGuide.snapshot().progress.steps).every(r=>r.practice===null));
});
test('MGTGUIDE-07 original retired Nocuda and independent Planning ownership remain compatible',()=>{
 const e=env(JSON.stringify(historical('tools-nocuda','tools')));e.add('#jpwLeveragePage');e.c.JPWLearningGuide.resume();e.flush();assert.equal(e.c.JPWLearningGuide.snapshot().stepId,'tools-genetrix');const c=e.c.JPWLearningCatalog;assert.equal(c.tracks.find(t=>t.steps.some(s=>s.id==='forex-planning')).id,'forex');assert.equal(c.tracks.flatMap(t=>t.steps).find(s=>s.id==='forex-planning').availabilityModule,'planning');assert.equal(c.journey.flatMap(t=>t.stepIds).filter(id=>id==='forex-planning').length,1);
});
console.log(JSON.stringify({cases:passed+failed,passed,failed}));process.exitCode=failed?1:0;

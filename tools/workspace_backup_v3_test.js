// Synthetic contract test: backup includes new progress, refuses incompatible data.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path'),root=path.resolve(__dirname,'..');
const store=new Map(),sandbox={console,structuredClone,URL,Set,Map,TextEncoder,TextDecoder};
sandbox.window=sandbox;sandbox.S={};sandbox.document={addEventListener(){}};
sandbox.localStorage={getItem:k=>store.get(k)??null};
sandbox.JPWModuleAvailability={KEY:'jpw_module_availability_v1',inspect:()=>({valid:true}),validate(){}};
vm.createContext(sandbox);
for(const file of ['src/js/40-app/26-learning-catalog.js','src/js/00-core/09-learning-progress.js','src/js/40-app/29-time-twins/02-missions.js','src/js/40-app/29-time-twins/03-progress.js','src/js/40-app/30-capital-currents/03-progress.js','src/js/00-core/07-workspace-backup.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),sandbox,{filename:file});
const run=code=>vm.runInContext(code,sandbox);
const cases={
 'jpwealth_learning_guide_v1':run('JSON.stringify(JPWLearningProgress.empty(JPWLearningCatalog))'),
 'jpwealth_time_twins_v1':JSON.stringify({schemaVersion:1,currentMissionId:'early-start',missions:{'early-start':'demonstrated'}}),
 'jpwealth_capital_field_v1':JSON.stringify({version:1,steps:{'intro-field':'practiced'}}),
 'jpwealth_planning_monthly_view_v1':JSON.stringify({version:1,highlightPast:false,fromCurrent:true})
};
for(const [key,value]of Object.entries(cases))store.set(key,value);
let capture=run('jpwWorkspaceCapture()');
assert.equal(capture.schemaVersion,3,'new export identifies expanded workspace schema3');
for(const [key,value]of Object.entries(cases))assert.equal(capture.preferences[key],value,'missing backup family '+key);
assert.doesNotThrow(()=>run('jpwWorkspaceValidate({schemaVersion:1,preferences:{},drafts:[]})'));
assert.doesNotThrow(()=>run('jpwWorkspaceValidate({schemaVersion:2,preferences:{jpw_fs:"2"},drafts:[]})'));
sandbox.fixture={schemaVersion:3,preferences:{jpwealth_planning_monthly_view_v1:JSON.stringify({version:1,highlightPast:'yes',fromCurrent:false})},drafts:[]};
assert.throws(()=>run('jpwWorkspaceValidate(fixture)'),/prefer|planejamento/i);
store.set('jpwealth_time_twins_v1','{"schemaVersion":99,"newData":"KEEP"}');
store.set('jpwealth_capital_currents_v1','{"legacy":"KEEP"}');
capture=run('jpwWorkspaceCapture()');
assert.equal(Object.hasOwn(capture.preferences,'jpwealth_time_twins_v1'),false,'incompatible progress is not automatically applied');
assert(capture.drafts.some(x=>x.text.includes('newData')&&x.provider==='opaque-preference'));
assert(capture.drafts.some(x=>x.text.includes('legacy')&&x.provider==='opaque-preference'));
assert.equal(store.get('jpwealth_time_twins_v1'),'{"schemaVersion":99,"newData":"KEEP"}');
sandbox.S.workspaceRecovery={schemaVersion:1,pending:false,drafts:capture.drafts};
assert.equal(run('jpwWorkspaceCapture()').drafts.length,capture.drafts.length,'re-export must not duplicate opaque recovery fragments');
store.set('jpwealth_capital_field_v1','{\"version\":99,\"pass\\u0077ord\":\"SYN_SECRET\"}');
assert.throws(()=>run('jpwWorkspaceCapture()'),/segredo/i,'escaped secret keys must not enter opaque recovery');
console.log('PASS workspace3: 4 families, legacy compatibility, invalid/future progress and opaque legacy preservation');

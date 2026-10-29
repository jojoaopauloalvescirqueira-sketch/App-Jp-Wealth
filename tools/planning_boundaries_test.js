'use strict';
// Execute the real shared backup type boundary with inert validators and synthetic data.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/js/30-accounting/01-daily-ledger.js','utf8');
const start=source.indexOf('function dgBackupValidateTypedContainers('),end=source.indexOf('\nwindow.JPWBackup=',start);
assert(start>=0&&end>start);const c={jpwValidateChecklist(){},DEFAULTS:{}};vm.createContext(c);
// The real shared boundary now delegates to the optional annual-family helper.
// Load that exact function into the isolated VM; it is not an inert substitute.
const persistence=fs.readFileSync('src/js/00-core/04-persistence.js','utf8');
const annualStart=persistence.indexOf('function jpwValidateManagementAnnual('),annualEnd=persistence.indexOf('function load(){',annualStart);
assert(annualStart>=0&&annualEnd>annualStart,'actual annual-family validator extraction has exact boundaries');
vm.runInContext(persistence.slice(annualStart,annualEnd),c,{filename:'04-persistence.js annual-family validator'});
vm.runInContext(source.slice(start,end),c);
for(const key of ['password','passwd','masterPassword','secret','accessToken','refreshToken','credentials','authorization','apiKey','api_key','private_key']){
 const doc={patrimonialPlanning:{schemaVersion:99,unknown:{[key]:'synthetic-canary'}}},before=JSON.stringify(doc);
 assert.throws(()=>c.dgBackupValidateTypedContainers(doc),/segredo/i,key);assert.equal(JSON.stringify(doc),before);
}
for(const version of [1,99]){const doc={patrimonialPlanning:{schemaVersion:version,extension:{label:'retained',value:0}}},before=JSON.stringify(doc);c.dgBackupValidateTypedContainers(doc);assert.equal(JSON.stringify(doc),before);}
console.log('PASS backup secret boundary: 11 canaries rejected, 2 compatible unknown/future controls unchanged');

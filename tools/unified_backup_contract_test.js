// Real ZIP encoder/parser and checksums; synthetic bytes, no browser user storage.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),sandbox={console,TextEncoder,TextDecoder,Uint8Array,ArrayBuffer,DataView,Blob,File,URL,crypto:crypto.webcrypto,structuredClone,Set,Map,WeakMap,setTimeout};
sandbox.window=sandbox;sandbox.document={addEventListener(){}};sandbox.dispatchEvent=()=>{};sandbox.CustomEvent=class{};
sandbox.DEFAULTS={params:{},ledger:[],phases:[]};sandbox.LSKEY='jpwealth_v9_state';sandbox.S={};
sandbox.jpwValidateChecklist=()=>{};sandbox.jpwValidateManagementAnnual=()=>{};
vm.createContext(sandbox);
for(const file of ['src/vendor/fflate/fflate-0.8.2.min.js','src/js/00-core/09-evidence-archive.js','src/js/00-core/07-workspace-backup.js','src/js/30-accounting/01-daily-ledger.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),sandbox,{filename:file});
assert.equal(typeof sandbox.JPWBackup.buildPackage,'function','a single package must contain data and original evidence');
(async()=>{
const result=await vm.runInContext(`(async()=>{
 const data={tipo:'jpwealth_full_backup',formatVersion:2,versao:'V9.1',state:{params:{},ledger:[],phases:[]},workspace:{schemaVersion:3,preferences:{},drafts:[]},cobertura:{kind:'CONFIRMED_STATE_AND_SEPARATE_WORKSPACE',sections:['ledger','params','phases']}};
 data.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',checksum:JPWBackup.sha256(dgBackupCanonical(data))};
 const original=new TextEncoder().encode('<html><body>synthetic original</body></html>'),hash=await JPWEvidence.digest(original);
 const body={format:'jpwealth_original_evidence',formatVersion:1,createdAt:'2026-10-31T12:00:00Z',coverage:'original-pdf-html-only',entries:[{fileHash:hash,fileName:'synthetic.html',kind:'html',size:original.length,receiptIds:['receipt1'],storedAt:'2026-10-31T12:00:00Z',path:'originals/'+hash+'.html'}]};
 const evidence={...body,checksum:{algorithm:'SHA-256',value:await JPWEvidence.digest(new TextEncoder().encode(JSON.stringify(body)))}};
 const files={'manifest.json':new TextEncoder().encode(JSON.stringify(evidence))};files[body.entries[0].path]=original;
 const blob=await JPWBackup.buildPackage(new Blob([JSON.stringify(data)],{type:'application/json'}),{manifest:evidence,files});
 const inspected=await JPWBackup.inspectPackage(new File([blob],'synthetic.zip'));
 const raw=new Uint8Array(await blob.arrayBuffer()),entries=fflate.unzipSync(raw);
 const outcomes=[];
 async function rejects(name,changed,directoryReason){
   let directoryRefused=!directoryReason;
   if(directoryReason){try{dgPackageDirectory(changed);}catch(error){directoryRefused=error.message.includes(directoryReason);}}
   let refused=false;try{await JPWBackup.inspectPackage(new File([changed],'bad.zip'));}catch(_){refused=true;}
   outcomes.push({name,refused,directoryRefused});
 }
 const bad={...entries,'../escape.html':new Uint8Array([1])};await rejects('path traversal',fflate.zipSync(bad,{level:0}));
 const changed={...entries,'backup.json':new TextEncoder().encode('{}')};await rejects('tampered content',fflate.zipSync(changed,{level:0}));
 await rejects('compression',fflate.zipSync(entries,{level:9}));
 await rejects('truncation',raw.slice(0,-4));
 const link=raw.slice(),view=new DataView(link.buffer);for(let i=0;i<link.length-46;i++){if(view.getUint32(i,true)===0x02014b50){view.setUint32(i+38,0xa1ff0000,true);break;}}await rejects('symlink',link);
 // Rebuild records with genuine payload/CRC and normal 32-bit sizes. Each fixture
 // targets the directory guard itself, so a later checksum failure cannot hide it.
 function records(){
   const v=new DataView(raw.buffer),end=raw.length-22,rows=[];let pos=v.getUint32(end+16,true);
   for(let i=0;i<v.getUint16(end+10,true);i++){
     const nl=v.getUint16(pos+28,true),el=v.getUint16(pos+30,true),cl=v.getUint16(pos+32,true),local=v.getUint32(pos+42,true),lnl=v.getUint16(local+26,true),lel=v.getUint16(local+28,true),packed=v.getUint32(pos+20,true);
     rows.push({central:raw.slice(pos,pos+46),local:raw.slice(local,local+30),name:raw.slice(pos+46,pos+46+nl),localName:raw.slice(local+30,local+30+lnl),centralExtra:raw.slice(pos+46+nl,pos+46+nl+el),localExtra:raw.slice(local+30+lnl,local+30+lnl+lel),comment:raw.slice(pos+46+nl+el,pos+46+nl+el+cl),data:raw.slice(local+30+lnl+lel,local+30+lnl+lel+packed),packed});
     pos+=46+nl+el+cl;
   }return rows;
 }
 function join(parts){const result=new Uint8Array(parts.reduce((n,p)=>n+p.length,0));let at=0;for(const p of parts){result.set(p,at);at+=p.length;}return result;}
 function rebuilt(edit){
   const rows=records();edit(rows);const locals=[],central=[];let offset=0;
   for(const row of rows){
     const l=new DataView(row.local.buffer),c=new DataView(row.central.buffer);
     l.setUint16(26,row.localName.length,true);l.setUint16(28,row.localExtra.length,true);l.setUint32(18,row.packed,true);l.setUint32(22,row.packed,true);
     c.setUint16(28,row.name.length,true);c.setUint16(30,row.centralExtra.length,true);c.setUint16(32,row.comment.length,true);c.setUint32(20,row.packed,true);c.setUint32(24,row.packed,true);c.setUint32(42,offset,true);
     const bytes=join([row.local,row.localName,row.localExtra,row.data]);locals.push(bytes);offset+=bytes.length;
     central.push(join([row.central,row.name,row.centralExtra,row.comment]));
   }
   const dir=join(central),end=new Uint8Array(22),v=new DataView(end.buffer);
   v.setUint32(0,0x06054b50,true);v.setUint16(8,rows.length,true);v.setUint16(10,rows.length,true);v.setUint32(12,dir.length,true);v.setUint32(16,offset,true);
   return join([...locals,dir,end]);
 }
 await rejects('duplicate filename',rebuilt(rows=>rows.push(structuredClone(rows[0]))),'Entrada ZIP recusada');
 await rejects('encrypted entry',rebuilt(rows=>{new DataView(rows[0].local.buffer).setUint16(6,1,true);new DataView(rows[0].central.buffer).setUint16(8,1,true);}),'Entrada ZIP recusada');
 const zip64=new Uint8Array([1,0,8,0,0,0,0,0,0,0,0,0]);
 await rejects('central ZIP64 extra with normal sizes',rebuilt(rows=>{rows[0].centralExtra=zip64;}),'ZIP64');
 await rejects('local ZIP64 extra with normal sizes',rebuilt(rows=>{rows[0].localExtra=zip64;}),'ZIP64');
 await rejects('local/central name mismatch',rebuilt(rows=>{rows[0].localName=rows[0].localName.slice();rows[0].localName[0]^=1;}),'Cabeçalho ZIP divergente');
 await rejects('overlapping local regions',rebuilt(rows=>{const next=rows[1];rows[0].packed+=30+next.localName.length+next.localExtra.length+next.data.length;}),'sobreposto');
 let reads=0;try{await JPWBackup.inspectPackage({size:168*1024*1024+1,arrayBuffer:async()=>{reads++;return raw.buffer;}});outcomes.push({name:'oversize before read',refused:false,directoryRefused:true});}catch(_){outcomes.push({name:'oversize before read',refused:reads===0,directoryRefused:true});}
 return {valid:inspected.payload.workspace.schemaVersion===3,count:inspected.evidenceCount,outcomes,keys:Object.keys(entries)};
})()`,sandbox);
assert.equal(result.valid,true);assert.equal(result.count,1);
for(const outcome of result.outcomes)assert(outcome.refused&&outcome.directoryRefused,JSON.stringify(outcome));
assert.deepEqual(Array.from(result.keys).sort(),['backup.json','evidence-manifest.json','manifest.json',result.keys.find(x=>x.startsWith('originals/'))].sort());
console.log('PASS unified package:',result.outcomes.map(row=>row.name).join(', '));
})().catch(error=>{console.error(error);process.exitCode=1;});

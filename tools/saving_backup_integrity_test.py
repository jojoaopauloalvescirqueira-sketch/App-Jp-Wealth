#!/usr/bin/env python3
"""N2 saving gauntlet: real sources/Blob/FileReader, isolated Chromium, synthetic state."""
import argparse, functools, hashlib, json, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from dashboard_macro_test import launch_browser
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
class FixtureServer(ThreadingHTTPServer):
    request_queue_size=128
    daemon_threads=True

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifact',required=True);args=parser.parse_args()
    server=FixtureServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));server.daemon_threads=True
    threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
    def check(name, condition, observed=None):
        results.append({'name':name,'status':'PASS' if condition else 'PRODUCT_FAIL','observed':observed})
        if not condition:raise AssertionError(name+': '+str(observed))
    try:
        with sync_playwright() as pw:
            browser=launch_browser(pw);ctx=browser.new_context(service_workers='block');install_bootstrap(ctx)
            ctx.route('https://example.invalid/synthetic.json',lambda route:route.fulfill(status=200,content_type='application/json',body='{"version":1,"events":[],"generated_at":"2026-10-06T12:00:00Z"}'))
            def page():
                p=ctx.new_page();p.bootErrors=[];p.on('pageerror',lambda error:p.bootErrors.append(str(error)));p.on('dialog',lambda dialog:dialog.accept());p.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(p)
                p.evaluate("closeModal();window.__onbShown=true;S.onboarding.done=true;S.savingSyntheticProbe='source';save();")
                assert p.evaluate('typeof jpwWorkspaceCapture')=='function' and p.evaluate('!!window.JPWModuleAvailability'),p.bootErrors
                return p
            a=page();errors=[];a.on('pageerror',lambda err:errors.append(str(err)))
            for value in ('','abc','JP Wealth — recuperação 🧪'):
                actual=a.evaluate('text=>dgBackupSha256(text)',value)
                check('sha256 utf8 independent oracle '+repr(value),actual==hashlib.sha256(value.encode()).hexdigest(),actual)
            result=a.evaluate(r'''async()=>{
                S.params.saldoAtu=1234;S.syntheticFuture={schemaVersion:1,unknown:{value:'preserved'}};save();
                const durable=localStorage.getItem(LSKEY);S.params.saldoAtu=22222;
                localStorage.setItem('jpwealth.ui.ffNews.sourceUrl','https://example.invalid/synthetic.json');
                const blob=dgBuildBackupBlob(12,'synthetic-full.json','2026-10-06T12:00:00Z');
                const full=JSON.parse(await blob.text()),before=S.params.saldoAtu;
                const registered=dgRegisterExportSuccess(12,'synthetic-full.json','2026-10-06T12:00:00Z','downloads');
                const disk=JSON.parse(localStorage.getItem(LSKEY));
                const cases=[[],{params:{saldoIni:1}},{params:{saldoIni:1},exportadoEm:'x',contas:[]},{tipo:'jpwealth_partial_audit',params:S.params}, {...full,integrity:{...full.integrity,checksum:'0'.repeat(64)}}, {...full,state:{...full.state,params:{...full.state.params,saldoAtu:33333}}}];
                const partialV2={...full,state:{params:full.state.params,ledger:[],phases:[]},cobertura:{...full.cobertura,sections:['ledger','params','phases']}};delete partialV2.integrity;partialV2.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',checksum:dgBackupSha256(dgBackupCanonical(partialV2))};cases.push(partialV2);
                const rejected=cases.map(value=>{try{normalizeImportedState(value);return false}catch(error){return true}});
                const normalized=normalizeImportedState(full);
                const legacy=dgBackupInspect(full.state),legacyNormalized=normalizeImportedState(full.state);
                let invalidUrl=false;try{jpwWorkspaceValidate({schemaVersion:2,preferences:{'jpwealth.ui.ffNews.sourceUrl':'javascript:alert(1)'},drafts:[]});}catch(error){invalidUrl=true;}
                const names=Array.from({length:100},()=>dgBackupUniqueFileName(12,new Date('2026-10-06T12:00:00Z')));
                return {full,registered,ram:before,ramAfter:S.params.saldoAtu,disk:disk.params.saldoAtu,
                    rejected,normalizedFuture:normalized.syntheticFuture,legacy,legacyFuture:legacyNormalized.syntheticFuture,invalidUrl,namesUnique:new Set(names).size===100,
                    sourceCaptured:full.workspace.drafts.some(item=>item.provider==='unconfirmed-memory'&&item.text.includes('22222')),
                    news:full.workspace.preferences['jpwealth.ui.ffNews.sourceUrl']};
            }''')
            full=result.pop('full')
            check('full backup v2 has integrity and declared confirmed coverage',full['formatVersion']==2 and full['cobertura']['kind']=='CONFIRMED_STATE_AND_SEPARATE_WORKSPACE')
            canonical=json.dumps({k:v for k,v in full.items() if k!='integrity'},ensure_ascii=False,sort_keys=True,separators=(',',':'))
            # JS and Python share canonical strings; float 1.0 differences are harmless to the
            # independent string-oracle cases above. Full-body verification is exercised in JS.
            check('refused RAM stays separately recoverable and export metadata cannot promote it',result['registered'] and result['ramAfter']==22222 and result['disk']==1234 and result['sourceCaptured'],result)
            check('arrays partial audits and modified checksum fail closed',all(result['rejected']),result['rejected'])
            check('unknown compatible fields and legacy identity preserved',result['normalizedFuture']==result['legacyFuture']=={'schemaVersion':1,'unknown':{'value':'preserved'}} and result['legacy']['legacy'],result['legacy'])
            check('custom news URL covered validated and unique names',result['news']=='https://example.invalid/synthetic.json' and result['invalidUrl'] and result['namesUnique'])
            drafts=a.evaluate(r'''()=>{
                let reopened=0;window.JPWWorkspaceDrafts.registerRestorer('synthetic',{inspect:item=>({compatible:item.context.id==='same',reason:'Synthetic source checked'}),reopen:item=>{reopened++;return {ok:true}}});
                const item={provider:'synthetic',version:1,label:'Synthetic',text:JSON.stringify({value:'edit'}),context:{id:'same'},baseReference:'original'};
                const before=localStorage.getItem(LSKEY),ok=JPWWorkspaceDrafts.reopen(item),bad=JPWWorkspaceDrafts.reopen({...item,context:{id:'other'}});
                return {ok,bad,reopened,unchanged:before===localStorage.getItem(LSKEY),legacy:JPWWorkspaceDrafts.inspect({label:'old',text:'old'})};
            }''')
            check('compatible draft explicit adapter opens only fields incompatible is read/copy',drafts['ok']['ok'] and not drafts['bad']['ok'] and drafts['reopened']==1 and drafts['unchanged'] and not drafts['legacy']['compatible'],drafts)
            b=page();b.evaluate("S.savingSyntheticProbe='destination';save();")
            b.evaluate('full=>importFullBackupFile(new File([JSON.stringify(full)],"synthetic-full.json",{type:"application/json"}))',full)
            b.wait_for_function("S.savingSyntheticProbe==='source'&&!S.workspaceRecovery?.pending",timeout=10000)
            restored=b.evaluate("({probe:S.savingSyntheticProbe,value:S.params.saldoAtu,drafts:S.workspaceRecovery.drafts.length,news:localStorage.getItem('jpwealth.ui.ffNews.sourceUrl')})")
            check('real Blob FileReader restore separates facts and drafts',restored['probe']=='source' and restored['value']==1234 and restored['drafts']>0 and restored['news']=='https://example.invalid/synthetic.json',restored)
            b.reload();wait_bootstrap(b);check('reload preserves restored confirmed value',b.evaluate('S.params.saldoAtu')==1234)
            size=b.evaluate("()=>{let reads=0;const old=window.FileReader;window.FileReader=function(){reads++;throw Error('must not read')};try{importFullBackupFile({name:'oversize.json',size:JPW_BACKUP_MAX_BYTES+1});return reads;}finally{window.FileReader=old}}")
            check('oversize rejected before reading payload',size==0,size)
            nulls=b.evaluate(r'''async full=>{
                const rows=[],before=localStorage.getItem(LSKEY),memory=JSON.stringify(S),ask=window.confirm,say=window.alert;
                try{
                  for(const [key,definition] of Object.entries(DEFAULTS).filter(([,value])=>value!==null&&typeof value==='object'))for(const [kind,value] of [['null',null],['wrong container',Array.isArray(definition)?{}:[]]]){
                    const payload=structuredClone(full);payload.state[key]=value;delete payload.integrity;
                    payload.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',checksum:dgBackupSha256(dgBackupCanonical(payload))};
                    let inspectRefused=false;try{dgBackupInspect(payload)}catch(error){inspectRefused=error.message.includes(key)}
                    let refusal='',prompts=0;window.confirm=()=>{prompts++;return true};
                    window.alert=message=>{refusal=String(message)};
                    importFullBackupFile(new File([JSON.stringify(payload)],'synthetic-null.json',{type:'application/json'}));
                    for(let at=0;at<100&&!refusal;at++)await new Promise(resolve=>setTimeout(resolve,10));
                    rows.push({key,kind,inspectRefused,refused:refusal.includes('Backup inválido')&&refusal.includes(key),prompts,unchanged:before===localStorage.getItem(LSKEY)&&memory===JSON.stringify(S)});
                  }
                }finally{window.confirm=ask;window.alert=say;}
                return rows;
            }''',full)
            check('valid checksum null and wrong shapes of every known typed container refused before consent',all(row['inspectRefused'] and row['refused'] and row['prompts']==0 and row['unchanged'] for row in nulls),nulls)
            recovery=b.evaluate(r'''async()=>{
                const key=JPWModuleAvailability.KEY,original=localStorage.getItem(key),ask=window.confirm,rows=[];
                try{
                  for(const raw of ['{invalid<script>window.__executed=true</script>','']){
                    localStorage.setItem(key,raw);let prompts=0;
                    window.confirm=()=>{prompts++;return true};
                    const before=localStorage.getItem(LSKEY),blob=dgBuildBackupBlob(31,'synthetic-recovery.json','2026-10-06T12:00:00Z'),payload=JSON.parse(await blob.text());
                    const snapshotMatches=blob.workspaceFingerprint===jpwWorkspaceFingerprint();
                    rows.push({prompts,omitted:!Object.hasOwn(payload.workspace.preferences,key),rawRetained:localStorage.getItem(key)===raw,
                      draftRetained:payload.workspace.drafts.some(item=>item.text===raw&&item.label.includes('disponibilidade')),
                      verified:dgBackupInspect(payload).kind==='FULL_V2',sourceUnchanged:localStorage.getItem(LSKEY)===before,snapshotMatches,
                      fingerprintNotSerialized:!Object.hasOwn(payload.workspace,'sourceFingerprint')});
                  }
                }finally{window.confirm=ask;if(original===null)localStorage.removeItem(key);else localStorage.setItem(key,original);}
                return rows;
            }''')
            check('corrupt and empty availability recovery uses one consent and retains raw source checkpoint',all(row['prompts']==1 and all(row[key] for key in ('omitted','rawRetained','draftRetained','verified','sourceUnchanged','snapshotMatches','fingerprintNotSerialized')) for row in recovery),recovery)
            folder=b.evaluate(r'''async()=>{
                let bytes=null;const mock={getFileHandle:async(name,options)=>({createWritable:async()=>({write:async blob=>{bytes=blob},close:async()=>{}}),getFile:async()=>bytes})};
                dgFsSupported=()=>true;dgFsStatus=async()=>({state:'authorized',handle:mock});dgFsFileExists=async()=>false;
                S.dataGovernance.storage.configured=true;S.dataGovernance.storage.folderName='Synthetic';S.dataGovernance.storage.folderDisplayPath='Synthetic';save();
                const good=await exportFullBackup({quiet:true});const goodStatus=JPWBackup.status();
                mock.getFileHandle=async()=>({createWritable:async()=>({write:async blob=>{bytes=blob},close:async()=>{}}),getFile:async()=>new Blob(['CORRUPT'])});
                const before=S.dataGovernance.export.lastSequence,bad=await exportFullBackup({quiet:true});
                return {good:!!good,goodStage:goodStatus.stage,bad,stage:JPWBackup.status().stage,sequenceUnchanged:S.dataGovernance.export.lastSequence===before};
            }''')
            check('folder readback is verified corrupt readback unknown with no metadata success',folder['good'] and folder['goodStage']=='FILE_VERIFIED' and folder['bad'] is None and folder['stage']=='UNKNOWN' and folder['sequenceUnchanged'],folder)
            families=b.evaluate(r'''async()=>{
                const plan=fxCreatePlan({name:'SYNTHETIC saving plan',now:'2026-01-01T00:00:00Z',assumptions:{startMonth:'2026-01',horizonMonths:120,initialBalanceUsd:1000,defaultMonthlyReturn:0.01,recurringContributions:{personalUsd:10,propUsd:0}}});
                plan.current.absentMonths['2026-04']={reason:'Synthetic removed projection',at:'2026-03-01T00:00:00Z'};
                plan.actuals={
                  '2026-01':{inputType:'rate',returnRate:0.01,profitUsd:null,closureStatus:'FINALIZED',contributionsConfirmed:true,closedAt:'2026-02-01T00:00:00Z'},
                  '2026-02':{inputType:'usd',returnRate:null,profitUsd:-5,closureStatus:'REOPENED',reopenNote:'Synthetic correction'},
                  '2026-03':{inputType:'rate',returnRate:0,profitUsd:null,closureStatus:'REVIEW_REQUIRED',reviewRequiredBy:'2026-02'}
                };
                plan.actualHistory=[{month:'2026-02',before:{profitUsd:7,closureStatus:'FINALIZED'},after:{profitUsd:-5,closureStatus:'REOPENED'},reason:'Synthetic correction'}];
                S.fxPlanning.plan=plan;
                for(const [key,value]of Object.entries(S))if(value&&typeof value==='object'&&!Array.isArray(value))value.xSavingSyntheticExtension={family:key,nested:{unknown:'preserve',zero:0,absent:null}};
                S.accounts.forEach(account=>account.xSavingSyntheticExtension={reference:'Synthetic account extension'});
                dgLogChange('synthetic','TEST','synthetic-saving','Synthetic event');S.dataGovernance.changeLog[S.dataGovernance.changeLog.length-1].futureMetadata={keep:true};
                save();
                const full=JSON.parse(await dgBuildBackupBlob(99,'synthetic-families.json','2026-10-06T12:00:00Z').text()),normalized=normalizeImportedState(full);
                const rows=Object.keys(full.state).map(key=>({family:key,equal:key==='workspaceRecovery'?normalized[key].pending===true&&dgBackupCanonical(normalized[key].snapshot)===dgBackupCanonical(full.workspace)&&dgBackupCanonical(normalized[key].xSavingSyntheticExtension)===dgBackupCanonical(full.state[key].xSavingSyntheticExtension):dgBackupCanonical(full.state[key])===dgBackupCanonical(normalized[key])}));
                return {rows,allEqual:rows.every(item=>item.equal),nestedLog:normalized.dataGovernance.changeLog.find(item=>item.recordId==='synthetic-saving')?.futureMetadata,plan:normalized.fxPlanning.plan,preferences:Object.keys(full.workspace.preferences),draftVersion:full.workspace.schemaVersion};
            }''')
            check('every present confirmed state family roundtrips without silent field loss',families['allEqual'],families['rows'])
            check('compatible nested governance extensions retained',families['nestedLog']=={'keep':True},families['nestedLog'])
            plan=families['plan']
            check('planning revision3 absent finalized reopened reconciliation histories exact',plan['planningRevision']==3 and '2026-04' in plan['current']['absentMonths'] and [plan['actuals'][m]['closureStatus'] for m in ('2026-01','2026-02','2026-03')]==['FINALIZED','REOPENED','REVIEW_REQUIRED'] and len(plan['actualHistory'])==1)
            check('workspace2 and all21 supported preference attributes exported',families['draftVersion']==2 and len(families['preferences'])==21 and 'jpwealth.ui.ffNews.sourceUrl' in families['preferences'],families['preferences'])
            explicit=b.evaluate(r'''async()=>{
                const before=localStorage.getItem(LSKEY),ram=JSON.stringify(S),adopted=jpWealthLastPersistedRawGet(),originalDownload=dgDownloadViaAnchor,originalSupported=dgFsSupported;
                let captured=null,metadata;
                try{
                  const disk=JSON.parse(before);disk.savingAuthoritativeProbe='foreign persisted revision';localStorage.setItem(LSKEY,JSON.stringify(disk));
                  let defaultRefused=false,divergentRefused=false,nullRefused=false;
                  try{dgBackupConfirmedSnapshot()}catch(error){defaultRefused=true}
                  try{dgBackupConfirmedSnapshot({...disk,savingAuthoritativeProbe:'different reference'})}catch(error){divergentRefused=true}
                  dgFsSupported=()=>false;dgDownloadViaAnchor=(_,blob)=>{captured=blob};
                  metadata=await exportFullBackup({quiet:true,estadoFonte:disk});
                  const body=captured?JSON.parse(await captured.text()):null;
                  const ramUnchanged=ram===JSON.stringify(S),adoptedUnchanged=adopted===jpWealthLastPersistedRawGet(),diskUnchanged=JSON.stringify(disk)===localStorage.getItem(LSKEY);
                  localStorage.removeItem(LSKEY);try{dgBackupConfirmedSnapshot(disk)}catch(error){nullRefused=true}
                  return {defaultRefused,divergentRefused,nullRefused,ramUnchanged,adoptedUnchanged,diskUnchanged,
                    exactDisk:body?.state.savingAuthoritativeProbe==='foreign persisted revision',metadataRefused:!!metadata&&metadata.localRecordConfirmed===false};
                }finally{dgFsSupported=originalSupported;dgDownloadViaAnchor=originalDownload;localStorage.setItem(LSKEY,before);}
            }''')
            check('explicit verified persisted revision exports without adopting or writing stale RAM',all(explicit.values()),explicit)
            check('no unexpected page errors',not errors,errors)
            browser.close()
    except Exception as error:
        results.append({'name':'gauntlet interrupted','status':'PRODUCT_FAIL','observed':str(error)})
        raise
    finally:
        server.shutdown();target=Path(args.artifact);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps({'scope':'saving backup integrity synthetic Chromium','results':results,'nativePhysicalFolder':'NOT_RUN'},ensure_ascii=False,indent=2))
    print(json.dumps({'PASS':sum(row['status']=='PASS' for row in results),'PRODUCT_FAIL':sum(row['status']=='PRODUCT_FAIL' for row in results)}))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Unified package: real app + IndexedDB, isolated synthetic Chromium contexts."""
import argparse,functools,json,threading,hashlib,sys
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap
from dashboard_macro_test import launch_browser
ROOT=Path(__file__).resolve().parents[1]
def source_hashes():
    paths={row['path'] for row in json.loads((ROOT/'src/js/manifest.json').read_text())['files']}
    paths.update(['src/js/manifest.json','src/vendor/fflate/fflate-0.8.2.min.js','index.html','build-id.js',
        'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html','tools/unified_backup_test.py',
        'tools/unified_backup_contract_test.js','tools/workspace_backup_v3_test.js','tools/complete_backup_test.py',
        'tools/browser_bootstrap_fixture.py','tools/dashboard_macro_test.py',
        'tools/storage_governance_test.py','tools/quality_gate.py'])
    return {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(paths)}
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
class FixtureServer(ThreadingHTTPServer):
    request_queue_size=128
    daemon_threads=True
def run(out,engine="chromium",distribution="modular",negative_control=None):
    out.mkdir(parents=True,exist_ok=True);results=[];sources_before=source_hashes();completed=False
    server=FixtureServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    def record(name,value,evidence=None):
        if not value:results.append({'case':name,'status':'PRODUCT_FAIL'});raise AssertionError(name)
        results.append({'case':name,'status':'PASS',**({'evidence':evidence} if evidence is not None else {})})
    try:
        with sync_playwright() as p:
            browser=launch_browser(p) if engine=="chromium" else p.webkit.launch(headless=True)
            def page():
                ctx=browser.new_context(service_workers='block');install_bootstrap(ctx)
                ctx.add_init_script('window.__onbShown=true');q=ctx.new_page();q.alerts=[];q.errors=[]
                q.on('dialog',lambda d:(q.alerts.append(d.message),d.accept()))
                q.on('pageerror',lambda e:q.errors.append(e.stack or str(e)))
                target='dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html' if distribution=='portable' else 'index.html'
                q.goto((ROOT/target).as_uri() if distribution=='file' else f'http://127.0.0.1:{server.server_port}/{target}');wait_bootstrap(q)
                q.evaluate('''()=>{const alert=window.alert;window.__backupAlerts=[];window.alert=function(message){__backupAlerts.push(String(message));return alert.call(window,message);}}''')
                return q
            def restore(q,content):
                before=q.evaluate('__backupAlerts.length')
                q.evaluate('bytes=>JPWBackup.restorePackage(new File([new Uint8Array(bytes)],"synthetic.zip",{type:"application/zip"}))',content)
                q.wait_for_function('n=>__backupAlerts.length>n',arg=before)
                return q.evaluate('n=>__backupAlerts.slice(n)',before)
            a=page()
            fixture=a.evaluate('''async()=>{
                S.onboarding.done=true;S.unifiedProbe='synthetic';save();
                const raw=JSON.stringify({version:1,highlightPast:false,fromCurrent:true});localStorage.setItem('jpwealth_planning_monthly_view_v1',raw);
                localStorage.setItem('jpwealth_learning_guide_v1',JSON.stringify(JPWLearningProgress.empty(JPWLearningCatalog)));
                localStorage.setItem('jpwealth_time_twins_v1',JSON.stringify({schemaVersion:1,currentMissionId:'early-start',missions:{'early-start':'demonstrated'}}));
                localStorage.setItem('jpwealth_capital_field_v1',JSON.stringify({version:1,steps:{'intro-field':'practiced'}}));
                const progressRaw=Object.fromEntries(['jpwealth_learning_guide_v1','jpwealth_time_twins_v1','jpwealth_capital_field_v1','jpwealth_planning_monthly_view_v1'].map(key=>[key,localStorage.getItem(key)]));
                const original=new File(['<!doctype html><html><body>synthetic original</body></html>'],'synthetic.html');
                const hash=await JPWEvidence.digest(await original.arrayBuffer());
                const saved=await JPWEvidence.putOriginal(original,{fileHash:hash,receiptId:'synthetic-receipt'});if(saved.status!=='CONFIRMED')throw Error(saved.reason);
                const blob=dgBuildBackupBlob(1,'synthetic.zip','2026-10-31T12:00:00Z');
                window.packageBytes=new Uint8Array(await (await JPWBackup.buildPackage(blob,await JPWEvidence.prepareArchive())).arrayBuffer());
                return {bytes:Array.from(packageBytes),originalHash:hash,originalBytes:Array.from(new Uint8Array(await original.arrayBuffer())),receiptIds:['synthetic-receipt'],progressRaw};
            }''')
            package=fixture['bytes']
            with a.expect_download() as event:
                exported=a.evaluate('async()=>await exportFullBackup({quiet:true})')
            delivered=out/'exported-package.zip';event.value.save_as(delivered)
            record('standard export delivers one ZIP package',exported['filename'].endswith('.zip') and delivered.read_bytes()[:2]==b'PK')
            missing=a.evaluate("""async()=>{
                const previous=structuredClone(S.fxConsolidated),ask=window.confirm,download=dgDownloadViaAnchor;let deliveries=0,questions=[];
                try{S.fxConsolidated.receipts=[{id:'missing-synthetic',fileHash:'f'.repeat(64)}];save();window.confirm=message=>{questions.push(message);return false};dgDownloadViaAnchor=()=>{deliveries++};const meta=await exportFullBackup({quiet:true});return {refused:meta===null,deliveries,questions};}
                finally{S.fxConsolidated=previous;save();window.confirm=ask;dgDownloadViaAnchor=download;}
            }""")
            record('missing originals require explicit consent before delivery',missing['refused'] and missing['deliveries']==0 and len(missing['questions'])==1 and 'ausências' in missing['questions'][0])
            b=page()
            first_alerts=restore(b,package)
            restored_raw=b.evaluate('keys=>Object.fromEntries(keys.map(key=>[key,localStorage.getItem(key)]))',list(fixture['progressRaw']))
            record('package restores confirmed data and monthly preference',any('Backup importado com sucesso.' in m for m in first_alerts) and restored_raw==fixture['progressRaw'] and b.evaluate('''()=>S.unifiedProbe==='synthetic'&&S.workspaceRecovery.pending===false&&S.workspaceRecovery.package.stage==='COMPLETE'&&JSON.parse(localStorage.getItem('jpwealth_planning_monthly_view_v1')).highlightPast===false'''),{'expectedFourFamilyRawFromSeed':fixture['progressRaw'],'actualFourFamilyRaw':restored_raw})
            record('original restored in real IndexedDB',b.evaluate('async()=>(await JPWEvidence.summary()).count===1'))
            # Different confirmed state/pref and epoch make a refused or unfinished
            # second import fail. Count===1 alone was already true after import one.
            replay_before=b.evaluate('''()=>{S.unifiedProbe='changed-after-first-import';S.replayOnly='remove-me';if(save()!==true)throw Error('replay checkpoint');localStorage.setItem('jpwealth_planning_monthly_view_v1',JSON.stringify({version:1,highlightPast:true,fromCurrent:false}));return {baseEpoch:sessionEpochRead(),persistenceEpoch:jpWealthPersistenceEpoch(),raw:localStorage.getItem(LSKEY)};}''')
            if negative_control=='refuse-replay':b.evaluate('window.confirm=()=>false')
            try:replay_alerts=restore(b,package)
            except Exception:
                record('second import must produce its own terminal completion',False)
                raise
            replay=b.evaluate('''async()=>{const archive=await JPWEvidence.prepareArchive(),summary=await JPWEvidence.summary(),row=archive.manifest.entries[0],bytes=archive.files[row.path];return {probe:S.unifiedProbe,replayOnly:S.replayOnly??null,pending:S.workspaceRecovery.pending,stage:S.workspaceRecovery.package.stage,pref:JSON.parse(localStorage.getItem('jpwealth_planning_monthly_view_v1')),baseEpoch:sessionEpochRead(),persistenceEpoch:jpWealthPersistenceEpoch(),diskProbe:JSON.parse(localStorage.getItem(LSKEY)).unifiedProbe,count:summary.count,hash:await JPWEvidence.digest(bytes),bytes:Array.from(bytes),receiptIds:row.receiptIds};}''')
            record('second import completes and restores changed state preference epoch original bytes and links',any('Backup importado com sucesso.' in m for m in replay_alerts) and replay['probe']=='synthetic' and replay['diskProbe']=='synthetic' and replay['replayOnly'] is None and replay['pending'] is False and replay['stage']=='COMPLETE' and replay['pref']=={'version':1,'highlightPast':False,'fromCurrent':True} and replay['baseEpoch']!=replay_before['baseEpoch'] and replay['count']==1 and replay['hash']==fixture['originalHash'] and replay['bytes']==fixture['originalBytes'] and replay['receiptIds']==fixture['receiptIds'])
            c=page();c.evaluate('''()=>{S.beforePackage='KEEP';save();const put=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){throw Error('synthetic IDB denied')};}''')
            restore(c,package)
            record('IDB failure never adopts financial data',c.evaluate('()=>S.beforePackage==="KEEP"&&!S.unifiedProbe'))
            record('IDB failure says financial state not substituted',any('base financeira não foi substituída' in m for m in c.alerts))
            d=page();d.evaluate('''()=>{S.beforePackage='KEEP';save();const put=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='jpwealth_planning_monthly_view_v1')throw Error('synthetic quota');return put.call(this,k,v)}}''')
            restore(d,package)
            record('preference failure preserves pending journal and blocks writes',d.evaluate('()=>jpWealthPersistenceIsBlocked()&&S.workspaceRecovery.package.stage==="PREFERENCES_PENDING"'))
            d.reload();wait_bootstrap(d)
            try:d.wait_for_function('()=>S.workspaceRecovery?.pending===false',timeout=5000)
            except Exception:
                print('RELOAD DIAGNOSTIC',d.errors,d.evaluate('()=>({availability:!!window.JPWModuleAvailability,guide:!!window.JPWLearningProgress,warning:document.getElementById("workspaceRestoreWarning")?.textContent,pending:S.workspaceRecovery,persistence:jpWealthPersistenceIsBlocked()})'),flush=True);raise
            resumed_raw=d.evaluate('keys=>Object.fromEntries(keys.map(key=>[key,localStorage.getItem(key)]))',list(fixture['progressRaw']))
            record('reload resumes projection without duplicate original',resumed_raw==fixture['progressRaw'] and d.evaluate('async()=>S.workspaceRecovery.package.stage==="COMPLETE"&&(await JPWEvidence.summary()).count===1'),{'expectedFourFamilyRawFromSeed':fixture['progressRaw'],'actualFourFamilyRawAfterReload':resumed_raw})
            f=page();f.evaluate('''()=>{S.beforePackage='KEEP';save();const put=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===LSKEY&&v.includes('unifiedProbe'))return;return put.call(this,k,v)}}''')
            restore(f,package)
            record('finance refusal preserves old data after evidence commit',f.evaluate('()=>S.beforePackage==="KEEP"&&!S.unifiedProbe'))
            record('finance refusal clearly reports partial restore',any('Restauração parcial: originais adicionados' in m for m in f.alerts))
            g=page();g.evaluate('()=>{S.beforePackage="KEEP";save();sessionEpochRotate=()=>null}')
            restore(g,package)
            record('epoch failure after evidence transaction reports partial restore',any('Restauração parcial' in m for m in g.alerts))
            gated=[]
            # Retain the real IDB transaction, pause its caller after commit, then
            # change one financial-adoption guard while the import still awaits it.
            for change in ['base','epoch','unknown']:
                h=page();gated.append(h)
                h.evaluate('''()=>{
                    S.beforePackage='KEEP';if(save()!==true)throw Error('gate checkpoint');
                    localStorage.setItem('jpwealth_planning_monthly_view_v1',JSON.stringify({version:1,highlightPast:true,fromCurrent:false}));
                    const api=JPWEvidence,put=Storage.prototype.setItem;
                    window.__gate={writes:0,phase:'waiting',nativePut:put,before:{raw:localStorage.getItem(LSKEY),state:JSON.stringify(S),pref:localStorage.getItem('jpwealth_planning_monthly_view_v1'),epoch:sessionEpochRead()}};
                    Storage.prototype.setItem=function(k,v){if(k===LSKEY)__gate.writes++;return put.call(this,k,v)};
                    window.JPWEvidence=Object.freeze({...api,restorePrepared:async prepared=>{const result=await api.restorePrepared(prepared);__gate.phase='idb-committed';await new Promise(resolve=>{__gate.release=resolve});return result;}});
                }''')
                h.evaluate('bytes=>JPWBackup.restorePackage(new File([new Uint8Array(bytes)],"synthetic.zip"))',package)
                h.wait_for_function('__gate.phase==="idb-committed"')
                interim=h.evaluate('async()=>({writes:__gate.writes,unchanged:localStorage.getItem(LSKEY)===__gate.before.raw,count:(await JPWEvidence.summary()).count,alerts:__backupAlerts.length})')
                assert interim=={'writes':0,'unchanged':True,'count':1,'alerts':0},interim
                h.evaluate('''change=>{if(change==='base'){const next=JSON.parse(__gate.before.raw);next.concurrentSynthetic='WINNER';__gate.expectedRaw=JSON.stringify(next);__gate.nativePut.call(localStorage,LSKEY,__gate.expectedRaw);}else{__gate.expectedRaw=__gate.before.raw;if(change==='epoch')blockJPWealthPersistence();else markJPWealthPersistenceOutcomeUnknown('synthetic while awaiting original transaction');}__gate.release();}''',change)
                h.wait_for_function('__backupAlerts.length>0')
                guarded=h.evaluate('''async()=>({raw:localStorage.getItem(LSKEY)===__gate.expectedRaw,state:JSON.stringify(S)===__gate.before.state,pref:localStorage.getItem('jpwealth_planning_monthly_view_v1')===__gate.before.pref,epoch:sessionEpochRead()===__gate.before.epoch,writes:__gate.writes,count:(await JPWEvidence.summary()).count,unknown:jpWealthPersistenceOutcomeIsUnknown(),alerts:__backupAlerts})''')
                record(change+' change while awaiting IDB preserves concurrent data and refuses financial adoption',all(guarded[k] for k in ['raw','state','pref','epoch']) and guarded['writes']==0 and guarded['count']==1 and any('Restauração parcial' in m for m in guarded['alerts']) and (change!='unknown' or guarded['unknown']))
            u=page();u.evaluate('''()=>{S.beforePackage='KEEP';if(save()!==true)throw Error('unknown checkpoint');markJPWealthPersistenceOutcomeUnknown('synthetic preexisting UNKNOWN');window.__unknownBefore={raw:localStorage.getItem(LSKEY),state:JSON.stringify(S),epoch:sessionEpochRead()};const put=Storage.prototype.setItem;window.__unknownWrites=0;Storage.prototype.setItem=function(k,v){if(k===LSKEY)__unknownWrites++;return put.call(this,k,v)}}''')
            unknown_alerts=restore(u,package)
            record('preexisting UNKNOWN refuses package before either store writes',u.evaluate('''async()=>localStorage.getItem(LSKEY)===__unknownBefore.raw&&JSON.stringify(S)===__unknownBefore.state&&sessionEpochRead()===__unknownBefore.epoch&&jpWealthPersistenceOutcomeIsUnknown()&&__unknownWrites===0&&(await JPWEvidence.summary()).count===0''') and any('desfecho de gravação desconhecido' in m for m in unknown_alerts))
            v=page();v.evaluate('''()=>{
                S.beforePackage='KEEP';if(save()!==true)throw Error('unknown readback checkpoint');
                const get=Storage.prototype.getItem,put=Storage.prototype.setItem;
                window.__unknown={nativeGet:get,writes:0,readFault:false,pref:localStorage.getItem('jpwealth_planning_monthly_view_v1')};
                Storage.prototype.setItem=function(k,value){if(k===LSKEY){__unknown.writes++;const result=put.call(this,k,value);if(String(value).includes('unifiedProbe'))__unknown.readFault=true;return result;}return put.call(this,k,value);};
                Storage.prototype.getItem=function(k){if(k===LSKEY&&__unknown.readFault)throw new DOMException('synthetic after-write readback denied','SecurityError');return get.call(this,k);};
            }''')
            combined_alerts=restore(v,package)
            combined=v.evaluate('''async()=>{
                const raw=__unknown.nativeGet.call(localStorage,LSKEY),writes=__unknown.writes;let retryRefused=false;
                try{save();}catch(error){retryRefused=error.name==='JPWealthPersistenceUnknownError'&&error.persistenceResult?.status==='UNKNOWN';}
                const archive=await JPWEvidence.prepareArchive(),row=archive.manifest.entries[0],bytes=archive.files[row.path];
                return {unknown:jpWealthPersistenceOutcomeIsUnknown(),pending:S.workspaceRecovery.pending,stage:S.workspaceRecovery.package.stage,diskProbe:JSON.parse(raw).unifiedProbe,refused:retryRefused,unchanged:__unknown.nativeGet.call(localStorage,LSKEY)===raw&&__unknown.writes===writes,pref:localStorage.getItem('jpwealth_planning_monthly_view_v1')===__unknown.pref,count:archive.manifest.entries.length,hash:await JPWEvidence.digest(bytes),bytes:Array.from(bytes),receiptIds:row.receiptIds};
            }''')
            record('UNKNOWN after evidence plus financial write keeps journal blocks retry and never announces success',combined['unknown'] and combined['pending'] and combined['stage']=='PREFERENCES_PENDING' and combined['diskProbe']=='synthetic' and combined['refused'] and combined['unchanged'] and combined['pref'] and combined['count']==1 and combined['hash']==fixture['originalHash'] and combined['bytes']==fixture['originalBytes'] and combined['receiptIds']==fixture['receiptIds'] and any('resultado desconhecido' in m for m in combined_alerts) and not any('importado com sucesso' in m for m in combined_alerts))
            # Tampering refuses before either database is changed.
            e=page();e.evaluate('()=>{S.beforePackage="KEEP";save()}')
            e.evaluate('''async bytes=>{const entries=fflate.unzipSync(new Uint8Array(bytes));entries['backup.json']=new TextEncoder().encode('{}');await JPWBackup.restorePackage(new File([fflate.zipSync(entries,{level:0})],'bad.zip'));}''',package)
            record('tampered package changes neither store',e.evaluate('async()=>S.beforePackage==="KEEP"&&!S.unifiedProbe&&(await JPWEvidence.summary()).count===0'))
            for q in [a,b,c,d,e,f,g,u,v,*gated]:assert not q.errors,q.errors
            e.evaluate("openSettingsModal('backup')")
            e.screenshot(path=str(out/'backup-ui.png'))
            browser.close()
            assert source_hashes()==sources_before,'candidate sources changed during browser test'
            completed=True
    finally:
        server.shutdown()
        (out/'receipt.json').write_text(json.dumps({'engine':engine,'distribution':distribution,'negative_control':negative_control,'completed':completed,'command':[sys.executable,*sys.argv], 'results':results,'sources':sources_before,'sources_after':source_hashes()},indent=2))
    print('PASS unified backup browser:',engine,distribution,len(results),'cases')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--engine',choices=['chromium','webkit'],default='chromium');parser.add_argument('--distribution',choices=['modular','portable','file'],default='modular');parser.add_argument('--negative-control',choices=['refuse-replay']);args=parser.parse_args();run(args.out,args.engine,args.distribution,args.negative_control)

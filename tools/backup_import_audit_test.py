#!/usr/bin/env python3
"""AUD-01/02: real backup FileReader/export/reload, synthetic Chromium contexts."""
import argparse,functools,hashlib,json,subprocess,tempfile,threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

SOURCE_FILES=['src/js/00-core/04-persistence.js','src/js/30-accounting/01-daily-ledger.js']
FEED='https://raw.githubusercontent.com/jojoaopauloalvescirqueira-sketch/jp-wealth-news-feed/main/ff-high-impact.json'
FX='https://api.frankfurter.dev/v2/rate/'
PAIRS={'EUR/USD','GBP/USD','AUD/USD','NZD/USD','USD/JPY','USD/CHF','USD/CAD','AUD/CAD','USD/BRL'}
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
class FixtureServer(ThreadingHTTPServer):
    request_queue_size=128
    daemon_threads=True
class ProductBootError(RuntimeError):
    """Valid application sources broke while opening the clean synthetic fixture."""

def exception_result(error,phase):
    if isinstance(error,ProductBootError):return 'PRODUCT_FAIL'
    if isinstance(error,OSError) or phase in ('bind','launch'):return 'ENVIRONMENT_ERROR'
    text=str(error).lower()
    if any(value in text for value in ('executable doesn\'t exist','browser executable','failed to launch','operation not permitted','net::err_connection_refused')):
        return 'ENVIRONMENT_ERROR'
    return 'TEST_HARNESS_FAIL'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--artifact',type=Path,required=True);args=parser.parse_args()
    root=args.root.resolve();artifact=args.artifact.resolve();artifact.parent.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix='backup-audit-',dir=artifact.parent))
    hashes=lambda:{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCE_FILES}
    report={'root':str(root),'sourceBefore':hashes(),'checks':[],'contexts':[],'fixture':'synthetic only; native FileReader, Storage, download and reload',
        'git':{'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
               'branch':subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip(),
               'status':subprocess.check_output(['git','status','--short'],cwd=root,text=True)}}
    server=None;contexts=[];phase='bind'
    def check(name,passed,observed):
        result='PASS' if passed else 'PRODUCT_FAIL';report['checks'].append({'name':name,'result':result,'observed':observed});print(result+' '+name,flush=True)
    try:
      server=FixtureServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)));threading.Thread(target=server.serve_forever,daemon=True).start()
      url=f'http://127.0.0.1:{server.server_port}/index.html';phase='launch'
      with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);report['browserVersion']=browser.version
        phase='tests'
        def page(label,seed=None,accept_confirms=True):
            context=browser.new_context(viewport={'width':1280,'height':900},service_workers='block',accept_downloads=True);contexts.append(context)
            trace={'label':label,'errors':[],'console':[],'dialogs':[],'unexpectedNetwork':[]};report['contexts'].append(trace)
            context.add_init_script('window.__onbShown=true;')
            if seed is not None:context.add_init_script('if(localStorage.getItem("jpwealth_v9_state")===null)localStorage.setItem("jpwealth_v9_state",'+json.dumps(json.dumps(seed,ensure_ascii=False))+');')
            def route(r):
                u=r.request.url;s=urlsplit(u)
                if s.scheme in ('file','data','blob') or s.scheme in ('http','https') and s.hostname in ('127.0.0.1','localhost','::1'):r.continue_();return
                if r.request.method=='GET' and u==FEED:payload={'version':1,'generated_at':'2026-10-12T12:00:00Z','events':[]}
                elif r.request.method=='GET' and u.startswith(FX) and u[len(FX):] in PAIRS:
                    base,quote=u[len(FX):].split('/');payload={'date':'2026-10-12','base':base,'quote':quote,'rate':1.2}
                else:trace['unexpectedNetwork'].append({'url':u,'method':r.request.method});r.abort('blockedbyclient');return
                r.fulfill(status=200,content_type='application/json',body=json.dumps(payload))
            context.route('**/*',route);p=context.new_page()
            p.on('pageerror',lambda e:trace['errors'].append(str(e)));p.on('console',lambda m:trace['console'].append({'type':m.type,'text':m.text}))
            def dialog(d):
                trace['dialogs'].append({'type':d.type,'message':d.message})
                if d.type=='confirm' and not accept_confirms:d.dismiss()
                else:d.accept()
            p.on('dialog',dialog);p.goto(url,wait_until='load')
            p.wait_for_function("() => !!window.JPWBackup && typeof importFullBackupFile==='function'",timeout=30000)
            if seed is None:
                p.wait_for_function("() => typeof ffNewsInFlight!=='undefined' && !ffNewsInFlight && !document.getElementById('fxUpdateBtn')?.disabled",timeout=30000)
                if trace['errors']:raise ProductBootError('Clean fixture boot failed: '+str(trace['errors']))
                p.evaluate("closeModal();window.__onbShown=true;S.onboarding.done=true;S.auditFixture='destination';localStorage.setItem('jpw_expl','on');if(save()!==true)throw Error('Baseline not confirmed');")
            if trace['unexpectedNetwork']:raise RuntimeError('Unexpected network: '+str(trace['unexpectedNetwork']))
            return p,trace
        def instrument(p):
            p.evaluate("""() => {
              const put=Storage.prototype.setItem,remove=Storage.prototype.removeItem,send=BroadcastChannel.prototype.postMessage;
              window.__auditWrites=[];window.__auditBroadcasts=[];
              Storage.prototype.setItem=function(k,v){if(this===localStorage)__auditWrites.push({kind:'set',key:k});return put.call(this,k,v);};
              Storage.prototype.removeItem=function(k){if(this===localStorage)__auditWrites.push({kind:'remove',key:k});return remove.call(this,k);};
              BroadcastChannel.prototype.postMessage=function(v){__auditBroadcasts.push({type:v?.type});return send.call(this,v);};
            }""")
        def snapshot(p):return p.evaluate("""() => ({raw:localStorage.getItem(LSKEY),ram:JSON.stringify(S),epoch:jpWealthPersistenceEpoch(),baseEpoch:localStorage.getItem('jpwealth_base_epoch_v1'),preferences:Object.fromEntries(JPW_WORKSPACE_KEYS.map(k=>[k,localStorage.getItem(k)]))})""")
        def full(p):return p.evaluate("""() => {const state=structuredClone(S);state.auditFixture='source';const raw={tipo:'jpwealth_full_backup',formatVersion:2,versao:'V9.1',localStorageKey:LSKEY,state,workspace:{schemaVersion:2,preferences:{jpw_expl:'off'},drafts:[]},cobertura:dgBackupCoverage(state)};raw.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',checksum:dgBackupSha256(dgBackupCanonical(raw))};return raw;}""")
        def checksum(p,payload):
            # Carry JSON as text: Playwright object serialization can drop an own __proto__ key.
            return json.loads(p.evaluate("""rawText => {const raw=JSON.parse(rawText);delete raw.integrity;if(raw.formatVersion===2)raw.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',checksum:dgBackupSha256(dgBackupCanonical(raw))};return JSON.stringify(raw);}""",json.dumps(payload,ensure_ascii=False)))
        def close_page(p):
            context=p.context;context.close();contexts.remove(context)
        def import_file(p,trace,payload,label,cancelled=False):
            file=work/(label+'.json');file.write_text(json.dumps(payload,ensure_ascii=False));start_d=len(trace['dialogs']);start_e=len(trace['errors'])
            p.locator('#importFullBackupInput').set_input_files(str(file))
            for at in range(80):
                if any(d['type']=='alert' or cancelled and d['type']=='confirm' for d in trace['dialogs'][start_d:]) or trace['errors'][start_e:]:break
                p.wait_for_timeout(50)
            p.wait_for_timeout(100)
            return {'dialogs':trace['dialogs'][start_d:],'errors':trace['errors'][start_e:]}

        # A valid history is generated by the original profile command, never by a hand-authored chain.
        for count in (26,27,35):
            p,trace=page('history-'+str(count))
            history=p.evaluate("""count => {
              S=structuredClone(DEFAULTS);S.onboarding.done=true;S.auditFixture='history-'+count;
              S.futureAuditExtension={schemaVersion:1,nested:{kept:true}};
              S.accounts=[{forexAccountId:'synthetic-account',nome:'Conta sintética de histórico',tipo:'MESTRE',broker:'Corretora sintética'}];
              const a=S.accounts[0];
              for(let i=0;i<count;i++)a.riskProfileAssignment=JPWForex.state.createRiskProfileAssignment(a,i%2?'longevity':'base',{source:'Synthetic source',declaredBy:'Synthetic operator',reason:'Synthetic revision'});
              if(save()!==true)throw Error('History not saved');return JSON.stringify(a.riskProfileAssignment);
            }""",count)
            with p.expect_download(timeout=10000) as pending:p.evaluate('exportFullBackup({quiet:true})')
            download=pending.value;file=work/('history-'+str(count)+'.json');download.save_as(str(file));payload=json.loads(file.read_text())
            p.evaluate("S.auditFixture='destination';if(save()!==true)throw Error('Destination not confirmed');")
            observation=import_file(p,trace,payload,'history-import-'+str(count))
            result=p.evaluate("""() => ({marker:S.auditFixture,history:JSON.stringify(S.accounts[0].riskProfileAssignment),pending:S.workspaceRecovery?.pending,extension:S.futureAuditExtension})""")
            error_start=len(trace['errors']);p.reload(wait_until='load');p.wait_for_timeout(100)
            reloaded=p.evaluate("({marker:S.auditFixture,history:JSON.stringify(S.accounts[0].riskProfileAssignment),recovery:jpWealthLoadRecoveryActive()})")
            passed=(result['marker']=='history-'+str(count) and result['history']==history and result['pending']==False and
                    result['extension']=={'schemaVersion':1,'nested':{'kept':True}} and reloaded['marker']==result['marker'] and reloaded['history']==history and not reloaded['recovery'] and not observation['errors'] and not trace['errors'][error_start:])
            check('AUD01 roundtrip '+str(count)+' profile revisions',passed,{'bytes':file.stat().st_size,'marker':result['marker'],'historyPreserved':result['history']==history,'reloaded':reloaded['marker'],'dialogs':observation['dialogs'],'errors':observation['errors']})
            close_page(p)

        malformed=[('root-null',None),('group-null',[None]),('items-null',[{'group':'Synthetic','items':None}]),
                   ('items-object',[{'group':'Synthetic','items':{}}]),('item-null',[{'group':'Synthetic','items':[None]}]),
                   ('item-primitive',[{'group':'Synthetic','items':['bad']}]),
                   ('group-nonstring',[{'group':42,'items':[]}]),
                   ('label-nonstring',[{'group':'Synthetic','items':[{'label':42,'v':0}]}]),
                   ('value-missing',[{'group':'Synthetic','items':[{'label':'Synthetic'}]}]),
                   ('value-string',[{'group':'Synthetic','items':[{'label':'Synthetic','v':'0'}]}]),
                   ('value-negative',[{'group':'Synthetic','items':[{'label':'Synthetic','v':-1}]}]),
                   ('value-fraction',[{'group':'Synthetic','items':[{'label':'Synthetic','v':0.5}]}]),
                   ('value-above-two',[{'group':'Synthetic','items':[{'label':'Synthetic','v':3}]}]),
                   ('value-boolean',[{'group':'Synthetic','items':[{'label':'Synthetic','v':True}]}])]
        corrupt_seed=None
        for label,value in malformed:
            p,trace=page('checklist-'+label);payload=full(p);payload['state']['checklist']=value;payload=checksum(p,payload)
            if label=='items-null':corrupt_seed=payload['state']
            before=snapshot(p);instrument(p);observation=import_file(p,trace,payload,'checklist-'+label);after=snapshot(p)
            side=p.evaluate('({writes:__auditWrites,broadcasts:__auditBroadcasts})')
            refused=any(d['type']=='alert' and 'Backup inválido' in d['message'] for d in observation['dialogs'])
            passed=refused and before==after and not side['writes'] and not side['broadcasts'] and not observation['errors'] and not any(d['type']=='confirm' for d in observation['dialogs'])
            error_start=len(trace['errors']);p.reload(wait_until='load');p.wait_for_timeout(100)
            reload=p.evaluate("({marker:S.auditFixture,recovery:jpWealthLoadRecoveryActive(),raw:localStorage.getItem(LSKEY)})")
            passed=passed and reload['marker']=='destination' and reload['raw']==before['raw'] and not reload['recovery'] and not trace['errors'][error_start:]
            check('AUD02 refuses '+label+' before any write/consent',passed,{'unchanged':before==after,'writes':side['writes'],'broadcasts':side['broadcasts'],'dialogs':observation['dialogs'],'errors':observation['errors'],'reloadErrors':trace['errors'][error_start:]})
            close_page(p)

        # Loading a previously malformed base must preserve the raw and enter the existing recovery flow.
        p,trace=page('malformed-local-state',corrupt_seed);p.wait_for_timeout(100)
        load=p.evaluate("""() => ({active:jpWealthLoadRecoveryActive(),blocked:jpWealthPersistenceIsBlocked(),raw:localStorage.getItem(LSKEY),recoveryRaw:jpWealthLoadRecovery.raw,recoveryKey:jpWealthLoadRecovery.recoveryKey})""")
        expected_raw=json.dumps(corrupt_seed,ensure_ascii=False)
        check('AUD02 existing malformed state enters recovery without rewriting raw',load['active'] and load['blocked'] and load['raw']==expected_raw and load['recoveryRaw']==expected_raw and not trace['errors'],{'active':load['active'],'blocked':load['blocked'],'rawPreserved':load['raw']==expected_raw,'recoveryRawPreserved':load['recoveryRaw']==expected_raw,'recoveryCopy':load['recoveryKey'] is not None,'errors':trace['errors']})
        close_page(p)

        # Compatibility controls: unanswered null differs from declared zero;
        # arbitrary inert labels/extensions and both legacy forms stay supported.
        for label,mode in [('empty','v2'),('zero','v2'),('null-zero','v2'),('workspace-v1','v2'),('legacy-envelope','envelope'),('legacy-state','bare')]:
            p,trace=page('compatible-'+label);payload=full(p)
            payload['state']['checklist']=[] if label=='empty' else [{'group':'Custom inert label','unknownGroup':{'kept':True},'items':[{'label':'Custom item','v':0,'unknownItem':{'kept':True}}]}]
            if label=='null-zero':
                payload['state']['checklist'][0]['items'].insert(0,{'label':'Unanswered synthetic item','v':None})
            if label=='workspace-v1':payload['workspace']['schemaVersion']=1
            if mode!='v2':del payload['state']['checklist'];payload={'tipo':'jpwealth_full_backup','versao':'V9.1','state':payload['state']} if mode=='envelope' else payload['state']
            payload=checksum(p,payload);observation=import_file(p,trace,payload,'compatible-'+label)
            result=p.evaluate("({marker:S.auditFixture,checklist:S.checklist,pending:S.workspaceRecovery?.pending})")
            expected=payload.get('state',payload).get('checklist')
            passed=result['marker']=='source' and not observation['errors'] and (result['checklist']==expected if expected is not None else len(result['checklist'])>0)
            check('AUD02 preserves '+label+' checklist compatibility',passed,{'marker':result['marker'],'checklist':result['checklist'],'dialogs':observation['dialogs'],'errors':observation['errors']})
            if label=='null-zero':
                error_start=len(trace['errors']);p.reload(wait_until='load');p.wait_for_timeout(100)
                reloaded=p.evaluate("({marker:S.auditFixture,checklist:S.checklist,recovery:jpWealthLoadRecoveryActive(),raw:JSON.parse(localStorage.getItem(LSKEY)).checklist})")
                items=reloaded['checklist'][0]['items']
                preserved=(reloaded['marker']=='source' and not reloaded['recovery'] and
                           reloaded['checklist']==expected and reloaded['raw']==expected and
                           items[0]['v'] is None and type(items[1]['v']) is int and items[1]['v']==0 and
                           not trace['errors'][error_start:])
                check('AUD02 reload keeps unanswered null distinct from explicit zero',preserved,{'reloaded':reloaded,'errors':trace['errors'][error_start:]})
            close_page(p)

        # A valid file dismissed at the native confirmation cannot alter any durable or RAM state.
        p,trace=page('cancel-valid-import',accept_confirms=False);payload=full(p)
        before=snapshot(p);instrument(p);observation=import_file(p,trace,payload,'cancel-valid-import',cancelled=True);after=snapshot(p)
        side=p.evaluate('({writes:__auditWrites,broadcasts:__auditBroadcasts})')
        confirm_seen=any(d['type']=='confirm' for d in observation['dialogs'])
        cancelled=confirm_seen and not any(d['type']=='alert' for d in observation['dialogs'])
        error_start=len(trace['errors']);p.reload(wait_until='load');p.wait_for_timeout(100)
        reloaded=p.evaluate("({marker:S.auditFixture,raw:localStorage.getItem(LSKEY),recovery:jpWealthLoadRecoveryActive()})")
        passed=cancelled and before==after and not side['writes'] and not side['broadcasts'] and not observation['errors'] and not trace['errors'][error_start:] and reloaded['marker']=='destination' and reloaded['raw']==before['raw'] and not reloaded['recovery']
        check('AUD02 cancelling a valid import preserves state before any write',passed,{'cancelled':cancelled,'unchanged':before==after,'writes':side['writes'],'broadcasts':side['broadcasts'],'dialogs':observation['dialogs'],'errors':observation['errors'],'reloadErrors':trace['errors'][error_start:]})
        close_page(p)

        # Public inspection is the oracle; the checksum helper only prepares the valid synthetic envelope.
        p,trace=page('public-inspection-reference-controls');payload=full(p);before=snapshot(p);instrument(p)
        api=p.evaluate("""raw => {
          const shared={label:'Synthetic shared extension',kept:true};
          raw.state.futureCompatibleExtension={first:shared,second:shared};
          raw.cobertura=dgBackupCoverage(raw.state);
          delete raw.integrity;raw.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',checksum:dgBackupSha256(dgBackupCanonical(raw))};
          const original=JSON.stringify(raw);let sharedResult=null,sharedError=null;
          try{sharedResult=window.JPWBackup.inspect(raw);}catch(error){sharedError=error.message;}
          const sharedPreserved=raw.state.futureCompatibleExtension.first===raw.state.futureCompatibleExtension.second && JSON.stringify(raw)===original;
          const cyclic={label:'Synthetic cyclic extension'};cyclic.self=cyclic;raw.state.futureCompatibleExtension=cyclic;
          let cycleError=null;try{window.JPWBackup.inspect(raw);}catch(error){cycleError=error.message;}
          return {sharedResult,sharedError,sharedPreserved,cycleError,cyclePreserved:raw.state.futureCompatibleExtension===cyclic && cyclic.self===cyclic};
        }""",payload)
        after=snapshot(p);side=p.evaluate('({writes:__auditWrites,broadcasts:__auditBroadcasts})')
        stable=before==after and not side['writes'] and not side['broadcasts'] and not trace['errors']
        check('AUD01 public inspection preserves a valid shared reference',stable and api['sharedResult'] is not None and api['sharedResult']['kind']=='FULL_V2' and api['sharedError'] is None and api['sharedPreserved'],{'api':api,'unchanged':before==after,'writes':side['writes'],'broadcasts':side['broadcasts'],'errors':trace['errors']})
        check('AUD01 public inspection refuses a cycle without mutating input or state',stable and api['cycleError']=='Estrutura circular no backup.' and api['cyclePreserved'],{'cycleError':api['cycleError'],'cyclePreserved':api['cyclePreserved'],'unchanged':before==after,'writes':side['writes'],'broadcasts':side['broadcasts'],'errors':trace['errors']})
        close_page(p)

        # Establish malformed confirmed bytes through the real writer in this disposable fixture.
        # Then observe the real export command: no build success, download, export journal or durable write.
        p,trace=page('refuse-export-invalid-checklist')
        p.evaluate("S.checklist=[{group:'Synthetic malformed confirmed checklist',items:null}];if(save()!==true)throw Error('Malformed synthetic source was not confirmed');")
        before=snapshot(p);instrument(p);downloads=[]
        p.on('download',lambda download:downloads.append({'suggestedFilename':download.suggested_filename}))
        p.evaluate("window.__auditBackupStages=[];window.addEventListener('jpw-backup-status',event=>__auditBackupStages.push(event.detail.stage));")
        dialog_start=len(trace['dialogs']);error_start=len(trace['errors'])
        result=p.evaluate('exportFullBackup({quiet:true})');p.wait_for_timeout(100)
        after=snapshot(p);exported=p.evaluate('({status:window.JPWBackup.status(),stages:__auditBackupStages,writes:__auditWrites,broadcasts:__auditBroadcasts})')
        export_dialogs=trace['dialogs'][dialog_start:];export_errors=trace['errors'][error_start:]
        passed=result is None and before==after and exported['status']['stage']=='REFUSED' and 'GENERATED' not in exported['stages'] and not downloads and not exported['writes'] and not exported['broadcasts'] and not export_errors and any(d['type']=='alert' and 'Checklist inválido' in d['message'] for d in export_dialogs)
        check('AUD02 invalid confirmed checklist refuses export before GENERATED/download/final record',passed,{'result':result,'unchanged':before==after,'status':exported['status'],'stages':exported['stages'],'downloads':downloads,'writes':exported['writes'],'broadcasts':exported['broadcasts'],'dialogs':export_dialogs,'errors':export_errors})
        close_page(p)

        for label,where,key in [('deep-constructor','state','constructor'),('deep-prototype','state','prototype'),('deep-proto','state','__proto__'),('workspace-depth','workspace',None),('checksum','checksum',None)]:
            p,trace=page('security-'+label);payload=full(p)
            if where=='state':
                leaf=payload['state'].setdefault('futureCompatibleTree',{})
                for n in range(45):leaf['next']={};leaf=leaf['next']
                leaf[key]={'synthetic':True}
            elif where=='workspace':
                value={};leaf=value
                for n in range(35):leaf['next']={};leaf=leaf['next']
                payload['workspace']['drafts']=[{'label':'Synthetic','text':'Synthetic','context':value}]
            if where=='state':payload['cobertura']=p.evaluate('stateText => dgBackupCoverage(JSON.parse(stateText))',json.dumps(payload['state'],ensure_ascii=False))
            payload=checksum(p,payload)
            if where=='state':
                preserved=payload['state']['futureCompatibleTree']
                for n in range(45):preserved=preserved['next']
                if key not in preserved:raise RuntimeError('Test fixture lost own dangerous key before FileReader: '+key)
            if where=='checksum':payload['integrity']['checksum']='0'*64
            before=snapshot(p);instrument(p);observation=import_file(p,trace,payload,'security-'+label);after=snapshot(p)
            side=p.evaluate('({writes:__auditWrites,broadcasts:__auditBroadcasts})')
            passed=before==after and not side['writes'] and not side['broadcasts'] and not observation['errors'] and any(d['type']=='alert' and 'Backup inválido' in d['message'] for d in observation['dialogs']) and not any(d['type']=='confirm' for d in observation['dialogs'])
            check('AUD01 keeps '+label+' refusal before mutation',passed,{'unchanged':before==after,'writes':side['writes'],'dialogs':observation['dialogs'],'errors':observation['errors']})
            close_page(p)
        p,trace=page('oversize');before=snapshot(p);instrument(p)
        read=p.evaluate("""() => {let read=0;const Reader=window.FileReader;window.FileReader=function(){read++;throw Error('Must not read oversized input');};try{importFullBackupFile({name:'synthetic-oversize.json',size:JPWBackup.maxBytes+1});return read;}finally{window.FileReader=Reader;}}""")
        check('AUD01 oversize refused before FileReader',read==0 and snapshot(p)==before and not p.evaluate('__auditWrites.length'),{'fileReaderConstructed':read,'dialogs':trace['dialogs']})
        close_page(p)
        for context in contexts:context.close()
        browser.close()
    except Exception as error:
        result=exception_result(error,phase)
        report['executionFailure']={'error':str(error),'class':type(error).__name__,'phase':phase,'result':result}
        report['checks'].append({'name':'regression execution','result':result,'observed':report['executionFailure']})
    finally:
        if server is not None:server.shutdown();server.server_close()
        report['sourceAfter']=hashes()
        if report['sourceAfter']!=report['sourceBefore']:report['checks'].append({'name':'source freeze','result':'TEST_HARNESS_FAIL','observed':'Source files changed while regression ran.'})
        report['summary']={kind:sum(row['result']==kind for row in report['checks']) for kind in sorted({row['result'] for row in report['checks']})}
        report['syntheticArtifacts']=str(work);artifact.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'summary':report['summary'],'artifact':str(artifact),'syntheticArtifacts':str(work)},ensure_ascii=False),flush=True)
    return 0 if all(row['result']=='PASS' for row in report['checks']) else 1
if __name__=='__main__':raise SystemExit(main())

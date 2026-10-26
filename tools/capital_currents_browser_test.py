#!/usr/bin/env python3
"""Real field regression CLI. Disposable synthetic contexts; no operator profile."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, threading, traceback
from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_OUT=ROOT/'tools/.artifacts/capital-currents-work/browser'
FILES=[f'src/js/40-app/30-capital-currents/{n}.js' for n in ('01-engine','02-scenarios','03-progress','04-field-renderer','04-view','05-controller')]
KEY='jpwealth_capital_field_v1'
OLD='jpwealth_capital_currents_v1'
CHROMIUM=os.environ.get('JP_WEALTH_CHROMIUM') or None
INPUTS=FILES+['src/styles/app.css','index.html','src/js/manifest.json','src/js/20-ui/31-tools-services.js','src/js/40-app/01-navigation.js','src/js/40-app/07-finalize-session.js','src/js/40-app/26-learning-catalog.js','src/js/00-core/07-workspace-backup.js','sw.js','build-id.js','dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html','tools/capital_currents_unit_test.js','tools/capital_currents_progress_test.js','tools/capital_currents_browser_test.py','tools/capital_field_browser_test.py','tools/capital_field_unit_test.js','tools/capital_field_catalog_test.js','tools/learning_guide_test.py','tools/quality_gate.py']
class SuiteFailure(Exception):
    def __init__(self,status,details):
        super().__init__(str(details));self.status=status
def fingerprint():return {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() if (ROOT/f).is_file() else None for f in INPUTS}
class Server(ThreadingHTTPServer):request_queue_size=64
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*_):pass
    def do_GET(self):
        path=(ROOT/('index.html' if self.path.split('?')[0]=='/' else self.path.split('?')[0].lstrip('/'))).resolve()
        if not path.is_file() or ROOT not in path.parents:self.send_error(404);return
        data=path.read_bytes();mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'}.get(path.suffix,'application/octet-stream')
        self.send_response(200);self.send_header('Content-Type',mime);self.end_headers();self.wfile.write(data)
def snap(p):return p.evaluate('ctl.snapshot()')
def act(p,a):p.locator(f'[data-capital-currents-root] [data-action="{a}"]').first.click()
def financial(p):return p.evaluate('JSON.stringify({state:S,raw:localStorage.getItem(LSKEY),galton:localStorage.getItem("jpwealth_galton_preferences_v1"),twins:localStorage.getItem("jpwealth_time_twins_v1"),old:localStorage.getItem("jpwealth_capital_currents_v1"),foreign:localStorage.getItem("foreign-synthetic")})')
def raw(p,k):return p.evaluate('(k)=>localStorage.getItem(k)',k)
def open_game(p):
    assert p.evaluate("JPWNavigation.navigate('capital-currents')")
    p.evaluate('window.ctl=document.getElementById("toolsCapitalCurrentsSlot").__capitalCurrentsController')
    assert p.locator('[data-capital-currents-root]').count()==1
    assert p.locator('#minigamesCapitalCurrentsTitle').evaluate('e=>e===document.activeElement')
def hit(node):return node.evaluate('''e=>{const r=e.getBoundingClientRect();return {w:r.width,h:r.height,points:[.2,.5,.8].flatMap(x=>[.25,.75].map(y=>{const px=r.x+r.width*x,py=r.y+r.height*y,h=document.elementFromPoint(px,py);return {x:px,y:py,own:h===e||e.contains(h),hit:h?.id||h?.tagName}}))}}''')
def geometry(p):return p.evaluate('''()=>{const root=document.querySelector('[data-capital-currents-root]'),c=root?.querySelector('canvas'),r=c?.getBoundingClientRect();return {overflow:Math.max(0,document.documentElement.scrollWidth-innerWidth),canvas:r?{x:r.x,right:r.right,w:r.width,h:r.height}:null,root:root?{client:root.clientWidth,scroll:root.scrollWidth}:null,wide:[...document.querySelectorAll('body *')].map(e=>({tag:e.tagName,id:e.id,cls:typeof e.className==='string'?e.className:'',right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width})).filter(e=>e.right>innerWidth+1&&e.width>0).slice(0,30)}}''')
def run(args):
    out=args.out_dir;out.mkdir(parents=True,exist_ok=True);before=fingerprint();rows=[];server=None;version=None
    def case(name,fn):
        if args.case and args.case not in name:return
        print('[RUN] '+name,flush=True)
        try:
            details=fn();rows.append({'name':name,'status':'PASS','details':details});print('[PASS] '+name,flush=True)
        except Exception as e:
            status=e.status if isinstance(e,SuiteFailure) else 'PRODUCT_FAIL' if isinstance(e,(AssertionError,BrowserTimeout)) else 'ENVIRONMENT_ERROR' if isinstance(e,(OSError,subprocess.TimeoutExpired)) else 'TEST_HARNESS_FAIL'
            rows.append({'name':name,'status':status,'error':str(e),'trace':traceback.format_exc()});print('['+status+'] '+name+' '+traceback.format_exc(),flush=True)
    def focused():
        env=dict(os.environ,JPW_CAPITAL_FIELD_OUT=str(out/'focused-field'))
        cmd=[sys.executable,str(ROOT/'tools/capital_field_browser_test.py')]
        r=subprocess.run(cmd,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        (out/'focused-field.log').write_text(r.stdout);print(r.stdout,flush=True)
        if r.returncode:
            environment=any(token in r.stdout for token in ['PermissionError:', 'ModuleNotFoundError:', 'Executable doesn', 'executable doesn', 'Failed to launch', 'ENOENT', 'Operation not permitted'])
            classification='ENVIRONMENT_ERROR' if environment or r.returncode<0 else 'PRODUCT_FAIL' if 'AssertionError' in r.stdout else 'TEST_HARNESS_FAIL'
            raise SuiteFailure(classification,{'returncode':r.returncode,'command':cmd,'log':str(out/'focused-field.log')})
        assert 'PASS ' in r.stdout,'focused suite emitted no assertions'
        return {'command':cmd,'returncode':r.returncode,'log':str(out/'focused-field.log'),'assertions':r.stdout.count('PASS ')}
    try:
        if args.mode in ('standalone','all'):case('standalone actual field learning lifecycle persistence touch and numeric suite',focused)
        if args.mode!='standalone':
            server=Server(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/'
            with sync_playwright() as pw:
                browser=pw.chromium.launch(executable_path=CHROMIUM,headless=True);version=browser.version
                def page(target=None,sw=False,mobile=False):
                    c=browser.new_context(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 900},has_touch=mobile,is_mobile=mobile,service_workers='allow' if sw else 'block',reduced_motion='reduce',accept_downloads=True)
                    install_bootstrap(c);c.add_init_script('window.__onbShown=true;')
                    p=c.new_page();p.errors=[];p.console_errors=[];p.set_default_timeout(6000)
                    p.on('pageerror',lambda e:p.errors.append(str(e)));p.on('console',lambda m:p.console_errors.append(m.text) if m.type=='error' else None)
                    p.goto(target or url,wait_until='load');wait_bootstrap(p);p.evaluate('closeModal();sessionEpochCurrent()')
                    p.evaluate('''()=>{for(const [k,v] of Object.entries({'jpwealth_capital_currents_v1':'old-campaign-synthetic','foreign-synthetic':'protected-foreign','jpwealth_galton_preferences_v1':'{"synthetic":true}','jpwealth_time_twins_v1':'synthetic-twins'}))localStorage.setItem(k,v);S.params.saldoIni=12345;S.params.saldoAtu=12345;localStorage.setItem(LSKEY,JSON.stringify(S));sessionEpochCurrent();window.fieldWrites=[];window.rafCount=0;const set=Storage.prototype.setItem,raf=requestAnimationFrame;Storage.prototype.setItem=function(k,v){fieldWrites.push(k);return set.call(this,k,v)};window.requestAnimationFrame=function(fn){return raf.call(window,t=>{rafCount++;fn(t)})}}''')
                    return c,p
                def clean(p):
                    assert not p.errors,p.errors;assert not p.console_errors,p.console_errors;assert_fixture_requests(p.context)
                def with_page(fn,**kw):
                    c,p=page(**kw)
                    try:
                        result=fn(p);clean(p);return result
                    finally:c.close()
                def cleanup(p):
                    open_game(p);act(p,'learn');act(p,'seen');saved=raw(p,KEY);assert saved is not None
                    old=raw(p,OLD);state=p.evaluate('JSON.stringify(S)');main=raw(p,'jpwealth_v9_state')
                    report=p.evaluate('clearJPWealthLocalData({removeAuxiliary:false,preserveMain:true})');assert report['ok'] and raw(p,KEY)==saved and raw(p,OLD)==old
                    p.evaluate('window.oldCtl=ctl;window.oldRoot=document.querySelector("[data-capital-currents-root]");sessionResetAuxiliarySurfaces()')
                    assert p.evaluate('oldCtl.snapshot().destroyed && !oldCtl.snapshot().loopScheduled')
                    p.evaluate('''()=>{oldCtl.activate();oldRoot.querySelector('[data-action=seen]').click();window.dispatchEvent(new StorageEvent('storage',{key:'jpwealth_capital_field_v1',newValue:'stale'}));document.dispatchEvent(new Event('visibilitychange'))}''')
                    assert p.locator('[data-capital-currents-root]').count()==0 and raw(p,KEY)==saved
                    report=p.evaluate('clearJPWealthLocalData({removeAuxiliary:true,preserveMain:true})')
                    assert report['ok'] and KEY in report['removedKeys'] and raw(p,KEY) is None,report
                    assert OLD in report['removedKeys'] and raw(p,OLD) is None
                    assert raw(p,'foreign-synthetic')=='protected-foreign' and raw(p,'jpwealth_v9_state')==main and p.evaluate('JSON.stringify(S)')==state
                    return {'newAndOldExplicitlyRemoved':True,'removeAuxiliaryFalsePreservesBoth':True,'staleControllerCannotWrite':True,'mainAndForeignPreserved':True}
                def lazy(p):
                    before=financial(p);assert p.locator('[data-capital-currents-root]').count()==0
                    p.evaluate("JPWNavigation.navigate('tools-minigames')");assert p.locator('[data-capital-currents-root]').count()==0
                    open_game(p);assert not snap(p)['running'] and snap(p)['tick']==0 and not snap(p)['loopScheduled']
                    act(p,'step');first=snap(p);assert first['tick']==15
                    assert abs(first['state']['q']-.08847968677143805)<1e-10 and abs(first['state']['p']-.0230406264567)<1e-8
                    p.evaluate('window.original=ctl');p.locator('#minigamesCapitalCurrentsBack').click();open_game(p)
                    assert p.evaluate('ctl===original') and snap(p)['state']==first['state']
                    for opener,closer in [("openSettingsModal('general')",'closeSettingsModal()'),('openMvpNotesDrawer()',"document.getElementById('mvpNotesCloseBtn').click()"),('openFinalizeSessionFlow()',"document.getElementById('sessionCancel').click()")]:
                        act(p,'play');p.wait_for_timeout(70);p.evaluate(opener);p.wait_for_timeout(70)
                        assert not snap(p)['running'] and not snap(p)['loopScheduled'];tick=snap(p)['tick'];raf=p.evaluate('rafCount')
                        p.wait_for_timeout(70);assert p.evaluate('rafCount')==raf;p.evaluate(closer);p.wait_for_timeout(70);assert snap(p)['tick']==tick and not snap(p)['running']
                    assert financial(p)==before and raw(p,KEY) is None
                    assert p.evaluate("JPWNavigation.navigate('dashboard')") and not snap(p)['active']
                    return {'singleton':True,'actualNumeric15Ticks':True,'threeRealDialogsZeroRAF':True,'noAutoplay':True,'financialBytesUnchanged':True}
                def navigation(p):
                    p.evaluate("JPWNavigation.navigateLocal('research','nocoda')");p.locator('#ncPrice1').fill('1,23412')
                    p.evaluate("openSettingsModal('knowledge')");route=p.evaluate('JPWNavigation.current()');p.wait_for_timeout(150);p.locator('#settingsPageTitle').focus();focus=p.evaluate('document.activeElement.id')
                    for call in ["JPWNavigation.navigate('capital-currents')","JPWNavigation.navigateLocal('tools','capital-currents')"]:
                        assert p.evaluate(call) is False and p.evaluate('JPWNavigation.current()')==route
                        assert p.locator('#ncPrice1').input_value()=='1,23412' and p.locator('[data-capital-currents-root]').count()==0
                        assert p.locator('#settingsOverlay').evaluate('(e)=>e.classList.contains("show")')
                        assert p.evaluate('document.activeElement.id')==focus,{'before':focus,'after':p.evaluate('document.activeElement.id')}
                    p.evaluate('closeSettingsModal()');before=financial(p);p.evaluate("JPWModuleAvailability.setState('research','frozen')")
                    open_game(p);assert not snap(p)['running'] and financial(p)==before
                    return {'pendingDraftPreserved':True,'realModalRefusal':2,'researchFrozenIndependent':True}
                def learning_backup(p):
                    before=financial(p);open_game(p);act(p,'learn');assert raw(p,KEY) is None
                    act(p,'seen');assert json.loads(raw(p,KEY))['steps']['intro-field']=='seen'
                    act(p,'discoveries');p.locator('[data-lesson="release-pressure"]').click()
                    act(p,'compare');assert snap(p)['learning']['comparison'] is not None
                    assert financial(p)==before
                    assert set(p.evaluate('fieldWrites'))<={KEY},p.evaluate('fieldWrites')
                    # Explicit fixture writer only: real confirmed snapshot/export/checksum path.
                    payload=p.evaluate('''async()=>{localStorage.setItem(LSKEY,JSON.stringify(S));sessionEpochCurrent();const blob=dgBuildBackupBlob(1,'synthetic-field.json',new Date().toISOString(),S);const payload=JSON.parse(await blob.text());return {payload,inspected:dgBackupInspect(payload),source:JSON.parse(localStorage.getItem(LSKEY)),capture:jpwWorkspaceCapture({recoverAvailability:true})}}''')
                    data=payload['payload'];assert data['tipo']=='jpwealth_full_backup' and data['integrity']['algorithm']=='SHA-256'
                    assert data['state']['params']==payload['source']['params']
                    def keys(value):
                        if isinstance(value,dict):return set(value).union(*(keys(v) for v in value.values()))
                        if isinstance(value,list):return set().union(*(keys(v) for v in value))
                        return set()
                    assert not {KEY,OLD}&keys(data) and not {KEY,OLD}&keys(payload['capture'])
                    serialized=json.dumps(data);assert 'old-campaign-synthetic' not in serialized and raw(p,KEY) not in serialized
                    return {'onlyNewProgressWrites':True,'actualFullBackupChecksumValidated':True,'financialParamsPreserved':True,'progressAbsentFromPayloadAndWorkspace':True}
                def games(p):
                    open_game(p);p.locator('#minigamesCapitalCurrentsBack').click();p.locator('#minigamesOpenGalton').click()
                    assert p.evaluate('!!document.querySelector("[data-galton-root]").__galtonController && !document.querySelector("[data-galton-root]").__galtonController.snapshot().running')
                    assert not snap(p)['active'];p.evaluate("JPWNavigation.navigate('time-twins')")
                    p.locator('[data-time-twins-root] [data-action=free]').click();p.locator('[data-time-twins-root] [data-action=step-year]').click()
                    assert p.evaluate('document.getElementById("toolsTimeTwinsSlot").__timeTwinsController.snapshot().month')==12
                    return {'actualGaltonPaused':True,'actualTwinsFreeYear':12}
                if args.mode in ('integrated','all'):
                    case('integrated lazy singleton real dialogs numerical engine and financial isolation',lambda:with_page(lazy))
                    case('integrated refused navigation pending draft frozen availability',lambda:with_page(navigation))
                    case('integrated deliberate progress and actual complete backup exclusions',lambda:with_page(learning_backup))
                    case('integrated disposal and explicit auxiliary cleanup key',lambda:with_page(cleanup))
                    case('integrated real Galton and Time Twins remain functional',lambda:with_page(games))
                def matrix(p):
                    entries=[];baseline=[];before=financial(p)
                    session=p.context.new_cdp_session(p)
                    def css_viewport(phase):
                        viewport=p.evaluate('({scale:visualViewport.scale,offsetLeft:visualViewport.offsetLeft,offsetTop:visualViewport.offsetTop})')
                        assert viewport['scale']==1,{'phase':phase,'visualViewport':viewport}
                        if phase=='initial':
                            assert viewport['offsetLeft']==0 and viewport['offsetTop']==0,viewport
                        return viewport
                    def back_to_hub():
                        back=p.locator('#minigamesCapitalCurrentsBack')
                        back.scroll_into_view_if_needed()
                        assert back.evaluate('e=>e.isConnected') and back.is_visible() and back.is_enabled()
                        measure='''e=>{const r=e.getBoundingClientRect(),v=visualViewport,cx=r.x+r.width/2,cy=r.y+r.height/2,h=document.elementFromPoint(cx,cy);return {rect:{x:r.x,y:r.y,width:r.width,height:r.height},viewport:{scale:v.scale,offsetLeft:v.offsetLeft,offsetTop:v.offsetTop,width:v.width,height:v.height},center:{x:cx,y:cy},own:h===e||e.contains(h)}}'''
                        state=back.evaluate(measure);viewport=state['viewport'];center=state['center']
                        assert viewport['scale']==1,state
                        offset=viewport['offsetLeft']!=0 or viewport['offsetTop']!=0
                        mode='native-visual-offset' if offset else 'locator'
                        coordinates={'x':center['x']-viewport['offsetLeft'],'y':center['y']-viewport['offsetTop']}
                        if offset:
                            # A finite stability check precedes the single native input.
                            p.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                            assert back.evaluate(measure)==state,state
                            assert state['own'] and state['rect']['width']>0 and state['rect']['height']>0,state
                            assert 0<=coordinates['x']<viewport['width'] and 0<=coordinates['y']<viewport['height'],state
                        record={'mode':mode,'coordinates':coordinates,'logicalCenter':center,'viewport':viewport}
                        back.evaluate('''e=>{e.__matrixBackEvent=null;e.__matrixBackListener=event=>{e.__matrixBackEvent={isTrusted:event.isTrusted,targetBack:event.target===e,clientX:event.clientX,clientY:event.clientY}};e.addEventListener('click',e.__matrixBackListener,{passive:true})}''')
                        try:
                            if offset:
                                p.mouse.click(coordinates['x'],coordinates['y'])
                            else:
                                p.locator('#minigamesCapitalCurrentsBack').click()
                            event=back.evaluate('e=>e.__matrixBackEvent');record['event']=event
                            assert event and event['isTrusted'] and event['targetBack'],record
                            if offset:
                                assert abs(event['clientX']-center['x'])<=1 and abs(event['clientY']-center['y'])<=1,record
                            assert p.locator('#minigamesHub').is_visible() and p.locator('#minigamesCapitalCurrentsGame').is_hidden(),record
                            assert p.evaluate("JPWNavigation.current().canonical==='tools-minigames' && JPWNavigation.current().localView.view==='minigames'"),record
                            return viewport,record
                        finally:
                            back.evaluate("e=>{e.removeEventListener('click',e.__matrixBackListener);delete e.__matrixBackListener;delete e.__matrixBackEvent}")
                    try:
                        for layout in ['sidebar','topbar','glass','submenu']:
                            p.evaluate('(v)=>mountNavigationLayout(v)',layout)
                            for width in [1440,390]:
                                p.set_viewport_size({'width':width,'height':900 if width==1440 else 844})
                                for theme in ['light','dark']:
                                    p.evaluate('(v)=>document.documentElement.dataset.theme=v',theme)
                                    for zoom in [1,1.25,2]:
                                        p.evaluate('(v)=>{document.documentElement.style.zoom=v;window.dispatchEvent(new Event("resize"));window.visualViewport?.dispatchEvent(new Event("resize"))}',zoom)
                                        # Each CSS presentation starts without native pinch zoom.
                                        session.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1})
                                        p.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                                        initial_viewport=css_viewport('initial')
                                        p.evaluate("JPWNavigation.navigate('tools-minigames')");hub=geometry(p);hub['notes']=p.locator('#headerNotesBtn').evaluate('e=>e.getBoundingClientRect().toJSON()');open_game(p);facts=geometry(p)
                                        row={'layout':layout,'width':width,'theme':theme,'cssZoom':zoom,'hub':hub,'field':facts,'visualViewportInitial':initial_viewport}
                                        assert facts['canvas']['w']>=140 and facts['canvas']['h']>=180 and facts['root']['scroll']<=facts['root']['client']+1,row
                                        assert facts['overflow']<=hub['overflow']+1,row
                                        if width==390 and zoom==2 and hub['overflow']>1:baseline.append(row)
                                        else:assert facts['overflow']<=1,row
                                        for action in ['play','step','reset']:
                                            node=p.locator(f'[data-capital-currents-root] [data-action={action}]');node.evaluate('e=>e.scrollIntoView({block:"center"})');p.wait_for_timeout(150);bounds=hit(node)
                                            if min(bounds['w'],bounds['h'])<44 or not all(x['own'] for x in bounds['points']):
                                                failure={**row,'action':action,'hit':bounds,'notes':p.locator('#headerNotesBtn').evaluate('e=>({html:e.outerHTML,bounds:e.getBoundingClientRect().toJSON()})'),'scroll':p.evaluate('({x:scrollX,y:scrollY})')}
                                                p.screenshot(path=str(out/'matrix-hit-failure.png'),full_page=False);(out/'matrix-hit-failure.json').write_text(json.dumps(failure,indent=2))
                                            assert min(bounds['w'],bounds['h'])>=44 and all(x['own'] for x in bounds['points']),{**row,'action':action,'hit':bounds}
                                        node=p.locator('[data-capital-currents-root] [data-action=step]');node.focus();p.keyboard.press('Tab');p.keyboard.press('Shift+Tab');assert node.evaluate('e=>e===document.activeElement&&e.matches(":focus-visible")')
                                        outline=node.evaluate('e=>{const s=getComputedStyle(e);return {width:parseFloat(s.outlineWidth),style:s.outlineStyle}}');assert outline['width']*zoom>=1.99 and outline['style']!='none',outline
                                        assert not snap(p)['running'] and not snap(p)['loopScheduled'];tick=snap(p)['tick'];raf=p.evaluate('rafCount');p.wait_for_timeout(40);assert snap(p)['tick']==tick and p.evaluate('rafCount')==raf
                                        row['visualViewportPreBack'],row['backInput']=back_to_hub()
                                        row['afterHub']=geometry(p);assert row['afterHub']['overflow']==hub['overflow'],row
                                        if zoom in [1,2] and theme=='light':p.screenshot(path=str(out/f'matrix-{layout}-{width}-{zoom}.png'),full_page=False)
                                        entries.append(row)
                        assert financial(p)==before
                        (out/'matrix.json').write_text(json.dumps(entries,indent=2));assert len(entries)==48
                        if baseline:
                            rows.append({'name':'BASELINE_FAIL shared header 390px CSS zoom200 before during after','status':'BASELINE_FAIL','details':baseline});print('[BASELINE_FAIL] shared header overflow independently reproduced; field delta passed',flush=True)
                        return {'presentations':48,'fieldDeltaAndControlsPass':True,'sharedHeaderBaselineCount':len(baseline),'nativeZoom':'NOT_RUN'}
                    finally:
                        session.detach()
                if args.mode in ('matrix','all'):case('matrix 48 layouts themes widths zoom focus touch targets strict field delta',lambda:with_page(matrix,mobile=True))
                def distributions():
                    results=[]
                    with tempfile.TemporaryDirectory(prefix='jpw-field-portable-') as temp:
                        detached=Path(temp)/'standalone.html';shutil.copyfile(ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html',detached);assert list(Path(temp).iterdir())==[detached]
                        for mode,target in [('http',url),('modular-file',(ROOT/'index.html').as_uri()),('portable-alone',detached.as_uri()),('pwa-offline',url)]:
                            c,p=page(target,sw=mode=='pwa-offline');responses=[];p.on('response',lambda r:responses.append(r.url) if r.from_service_worker else None)
                            try:
                                if mode=='pwa-offline':
                                    p.evaluate('navigator.serviceWorker.ready');p.reload(wait_until='load');wait_bootstrap(p);p.wait_for_function('navigator.serviceWorker.controller!==null')
                                    c.set_offline(True);responses.clear();response=p.reload(wait_until='load');wait_bootstrap(p);p.evaluate('closeModal()');assert response.from_service_worker
                                    assert all(any('/'+path in u for u in responses) for path in FILES),responses
                                before=financial(p);open_game(p);assert snap(p)['tick']==0 and not snap(p)['running'];act(p,'step');s=snap(p)
                                assert s['tick']==15 and abs(s['state']['q']-.08847968677143805)<1e-10 and abs(s['state']['p']-.0230406264567)<1e-8
                                assert p.locator('canvas[data-capital-field]').evaluate('e=>e.width>100&&e.height>100')
                                act(p,'learn');act(p,'skip');assert snap(p)['learning']['progress']['steps']['intro-field']=='skipped'
                                stored=raw(p,KEY);assert stored is not None or 'sessão' in p.locator('[data-capital-currents-root]').inner_text()
                                assert financial(p)==before
                                p.reload(wait_until='load');wait_bootstrap(p);p.evaluate('closeModal()');open_game(p)
                                if stored is not None:assert snap(p)['learning']['progress']['steps']['intro-field']=='skipped' and raw(p,KEY)==stored
                                assert not snap(p)['running'];clean(p);p.screenshot(path=str(out/f'distribution-{mode}.png'),full_page=False)
                                results.append({'mode':mode,'actualStepTick':15,'numericOutcome':s['state'],'cachedSixSources':mode=='pwa-offline','progressReload':stored is not None,'fileRAMWarning':stored is None})
                            finally:c.close()
                    return results
                if args.mode in ('distributions','all'):case('distributions HTTP modular file detached portable native SW offline',distributions)
                browser.close()
    except Exception as e:rows.append({'name':'browser infrastructure','status':'ENVIRONMENT_ERROR','error':str(e),'trace':traceback.format_exc()})
    finally:
        if server:server.shutdown();server.server_close()
    after=fingerprint()
    if before!=after:rows.append({'name':'candidate stable','status':'ENVIRONMENT_ERROR','changed':[k for k in before if before[k]!=after[k]]})
    if not rows:rows.append({'name':'selected cases','status':'TEST_HARNESS_FAIL','error':'No cases matched mode/filter'})
    result={'suite':'capital_currents_browser','mode':args.mode,'passed':sum(r['status']=='PASS' for r in rows),'failed':sum(r['status']!='PASS' for r in rows),'rows':rows,'candidateBefore':before,'candidateAfter':after,'environment':{'python':sys.version,'chromium':CHROMIUM,'browserVersion':version,'command':sys.argv},'limits':['Disposable synthetic contexts only','CSS zoom reflow; native browser zoom NOT_RUN','Human comprehension, screen reader and physical touch NOT_RUN']}
    (out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print('JPW_TEST_RESULT '+json.dumps({k:result[k] for k in ['suite','mode','passed','failed','rows']},ensure_ascii=False),flush=True)
    return int(bool(result['failed']))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',choices=['all','standalone','integrated','matrix','distributions'],default='standalone');parser.add_argument('--out-dir',type=Path,default=DEFAULT_OUT);parser.add_argument('--case',default='');raise SystemExit(run(parser.parse_args()))

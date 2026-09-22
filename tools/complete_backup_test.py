#!/usr/bin/env python3
"""Complete backup: isolated Chromium, real Blob/FileReader round trips, no user data."""
import functools,json,threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap
from dashboard_macro_test import launch_browser
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class BrowserFixtureServer(ThreadingHTTPServer):
    request_queue_size=128
    daemon_threads=True

def main():
    server=BrowserFixtureServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    with sync_playwright() as p:
        browser=launch_browser(p)
        def page(path='index.html'):
            ctx=browser.new_context();install_bootstrap(ctx);q=ctx.new_page();q.errors=[];q.alerts=[]
            q.on('pageerror',lambda e:q.errors.append(str(e)))
            q.on('dialog',lambda d:(q.alerts.append(d.message),d.accept()))
            q.goto(f'http://127.0.0.1:{server.server_port}/{path}');wait_bootstrap(q)
            q.evaluate('closeModal();window.__onbShown=true');return q
        def restore(q,data):
            q.evaluate('data=>importFullBackupFile(new File([JSON.stringify(data)],"synthetic.json",{type:"application/json"}))',data)
            try:q.wait_for_function('()=>S.completeBackupProbe==="synthetic"',timeout=5000)
            except Exception:
                print('IMPORT DIAGNOSTIC',q.alerts,q.errors,flush=True);raise
        for path in ['index.html','dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']:
            a=page(path)
            payload=a.evaluate('''async()=>{
                S.onboarding.done=true;S.theme='light';S.completeBackupProbe='synthetic';
                S.onboarding.investorPassword='NEVER_EXPORT_SECRET';
                S.mei.notes='preserved MEI';save();
                const before=sessionStateFingerprint();
                const preferences={
                    jpwealth_local_profile_v1:JSON.stringify({schemaVersion:1,displayName:'Synthetic gallery',avatarDataUrl:SETTINGS_PROFILE_AVATARS[0].avatarDataUrl}),
                    jpw_fs:'2',jpw_expl:'off',jpw_rail:'collapsed',jpw_nav_submenu_rail:'expanded',jpw_nav:'pill',jpw_nav_layout:'submenu',jpw_nav_glass_tint:'60',
                    jpw_nav_order:JSON.stringify({schemaVersion:1,order:['alladin','forex','personal-finance','research','dashboard']}),
                    jpwealth_v9_icon_choice:'secondary',jpwealth_v9_icon_theme:'dark',
                    'jpwealth.ui.widgetLayouts.v6':JSON.stringify(dashLayoutNormalizeV6(null)),
                    jpwealth_notes_launcher_position_v1:JSON.stringify({schemaVersion:1,x:0.5,y:0.8}),
                    jpwealth_notes_appearance_v1:JSON.stringify({schemaVersion:1,theme:'dark',density:'compact',preview:'show',sidebar:'hide',reading:'full',text:'large'}),
                    jpwealth_galton_preferences_v1:JSON.stringify({schemaVersion:1,preset:'idealized',speed:2,showTheory:false,seed:123,config:{}})
                };
                for(const [k,v]of Object.entries(preferences))localStorage.setItem(k,v);
                if(before===sessionStateFingerprint())throw Error('Preferences ignored by checkpoint');
                mvpNotesUI.draft={content:'Unsaved note',folderId:null,tags:'synthetic'};mvpNotesUI.draftDirty=true;
                const field=document.createElement('textarea');field.id='syntheticDraft';field.value='Unsaved form';document.body.append(field);field.dispatchEvent(new Event('input',{bubbles:true}));
                const secret=document.createElement('input');secret.type='password';secret.id='syntheticPassword';secret.value='NEVER_EXPORT_SECRET';document.body.append(secret);secret.dispatchEvent(new Event('input',{bubbles:true}));
                const result=JSON.parse(await dgBuildBackupBlob(12,'synthetic.json','2026-09-16T00:00:00Z').text());
                const durable=sessionPreserveLongitudinal({});const finalized=emptyJPWealthState(durable.valor);
                const durableState=JSON.parse(durable.raw);
                for(const k of Object.keys(durableState))if(!['riskPinHash','phaseUnlocked','onboarding','accounts'].includes(k)&&JSON.stringify(finalized[k])!==JSON.stringify(durableState[k]))throw Error('Finalization lost '+k);
                return result;
            }''')
            assert 'NEVER_EXPORT_SECRET' not in json.dumps(payload)
            assert len(payload['workspace']['drafts'])==2
            assert payload['workspace']['preferences']['jpwealth_local_profile_v1']
            b=page(path)
            b.evaluate("mvpNotesUI.draft={content:'OLD_DESTINATION_DRAFT'};mvpNotesUI.draftDirty=true")
            restore(b,payload)
            b.wait_for_function('()=>S.workspaceRecovery?.pending===false')
            prefs=b.evaluate('()=>Object.fromEntries(JPW_WORKSPACE_KEYS.map(k=>[k,localStorage.getItem(k)]))')
            assert prefs==payload['workspace']['preferences']
            assert 'OLD_DESTINATION_DRAFT' not in b.evaluate('JSON.stringify(jpwWorkspaceCapture())')
            b.reload();wait_bootstrap(b)
            assert b.evaluate('S.theme')=='light'
            assert b.evaluate('S.mei.notes')=='preserved MEI'
            assert b.evaluate('S.workspaceRecovery.drafts.length')==2
            assert b.locator('#workspaceDraftsButton').count()==1
            assert b.evaluate('document.documentElement.dataset.fs')=='2'
            assert b.evaluate('currentAppIconChoice()')=='secondary'
            assert b.evaluate('mvpNotesAppearancePreference(localStorage.getItem(MVP_NOTES_APPEARANCE_KEY)).theme')=='dark'
            assert b.evaluate('mvpNotesLauncherPreference(localStorage.getItem(MVP_NOTES_LAUNCHER_KEY)).x')==0.5
            assert b.evaluate('settingsProfileState.confirmed.displayName')=='Synthetic gallery'
            b.evaluate('closeModal();jpwWorkspaceShowDrafts()')
            assert 'Unsaved form' in b.locator('#workspaceDraftDialog textarea').evaluate_all('els=>els.map(el=>el.value)')
            b.set_viewport_size({'width':390,'height':844})
            assert b.locator('#workspaceDraftDialog').evaluate('el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth}')
            # Archive deletion must also distinguish a no-op from a confirmed write.
            b.evaluate("""()=>{window.backupTestPut=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===LSKEY)return;return backupTestPut.call(this,k,v);};}""")
            b.get_by_role('button',name='Excluir rascunhos recuperados',exact=True).click()
            assert b.evaluate('S.workspaceRecovery.drafts.length')==2
            assert b.locator('#workspaceDraftDialog').is_visible()
            b.evaluate('()=>{Storage.prototype.setItem=window.backupTestPut;}')
            b.get_by_role('button',name='Excluir rascunhos recuperados',exact=True).click()
            assert b.evaluate('JSON.parse(localStorage.getItem(LSKEY)).workspaceRecovery.drafts.length')==0
            assert b.locator('#workspaceDraftsButton').count()==0
            assert not a.errors and not b.errors,(a.errors,b.errors)
            print('PASS new backup + reload + drafts + full finalization document:',path,flush=True)
            if path=='index.html':
                # Interrupted projection: journal survives a rejected preference write.
                c=page();c.evaluate("""()=>{const put=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='jpw_fs')throw new DOMException('test quota','QuotaExceededError');return put.call(this,k,v);};}""")
                restore(c,payload);c.wait_for_function('()=>S.workspaceRecovery?.pending===true&&jpWealthPersistenceIsBlocked()')
                assert c.locator('#workspaceRestoreWarning').count()==1
                assert c.evaluate('save()') is False
                assert c.evaluate('jpwWorkspaceCapture()')==payload['workspace']
                c.reload();wait_bootstrap(c)
                assert c.evaluate('S.workspaceRecovery.pending') is False,c.errors
                assert c.evaluate("localStorage.getItem('jpw_fs')")=='2'
                assert not c.errors,c.errors
                print('PASS partial import, durable journal, reload recovery',flush=True)
                legacy=json.loads(json.dumps(payload));legacy.pop('workspace');legacy['state'].pop('workspaceRecovery',None)
                d=page();d.evaluate("localStorage.setItem('jpw_fs','1')");restore(d,legacy)
                assert d.evaluate("localStorage.getItem('jpw_fs')")=='1'
                print('PASS legacy backup preserves destination preferences',flush=True)
                old_workspace=json.loads(json.dumps(payload));old_workspace['workspace']['preferences'].pop('jpw_nav_glass_tint',None)
                d2=page();d2.evaluate("localStorage.setItem('jpw_nav_glass_tint','88')");restore(d2,old_workspace)
                assert d2.evaluate("localStorage.getItem('jpw_nav_glass_tint')")=='88'
                print('PASS schema v1 workspace without glass tint preserves destination preference',flush=True)
                old_submenu=json.loads(json.dumps(payload));old_submenu['workspace']['preferences'].pop('jpw_nav_submenu_rail',None)
                d3=page();d3.evaluate("localStorage.setItem('jpw_nav_submenu_rail','collapsed')");restore(d3,old_submenu)
                assert d3.evaluate("localStorage.getItem('jpw_nav_submenu_rail')")=='collapsed'
                print('PASS schema v1 workspace without submenu rail preserves destination preference',flush=True)
                # A custom uploaded-photo raster is self-contained as well.
                custom=a.evaluate("""async()=>{
                  const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
                  canvas.getContext('2d').fillRect(0,0,64,64);
                  localStorage.setItem('jpwealth_local_profile_v1',JSON.stringify({schemaVersion:1,displayName:'Custom photo',avatarDataUrl:canvas.toDataURL('image/jpeg')}));
                  return JSON.parse(await dgBuildBackupBlob(13,'custom.json','2026-09-16T00:00:00Z').text());
                }""")
                e=page();restore(e,custom)
                assert e.evaluate("localStorage.getItem('jpwealth_local_profile_v1')")==custom['workspace']['preferences']['jpwealth_local_profile_v1']
                # A silent no-op on the final journal commit must not claim completion.
                f=page();f.evaluate("""()=>{const put=Storage.prototype.setItem;let n=0;Storage.prototype.setItem=function(k,v){if(k===LSKEY&&++n===2)return;return put.call(this,k,v);};}""")
                restore(f,payload);f.wait_for_function('()=>jpWealthPersistenceIsBlocked()')
                assert f.evaluate('JSON.parse(localStorage.getItem(LSKEY)).workspaceRecovery.pending') is True
                assert not any('com sucesso' in msg for msg in f.alerts)
                f.reload();wait_bootstrap(f)
                assert f.evaluate('S.workspaceRecovery.pending') is False
                print('PASS custom photo + silent write refusal + recovery',flush=True)
                # A change after the artifact was built cannot authorize finalization.
                g=page()
                g.evaluate("""async()=>{
                  S.onboarding.done=true;save();localStorage.setItem('jpw_fs','1');openFinalizeSessionFlow();
                  const finish=dgFinishExport;
                  dgFinishExport=function(meta,quiet){localStorage.setItem('jpw_fs','2');return finish(meta,quiet);};
                  await beginSessionExport();
                }""")
                assert 'mudaram durante a exportação' in g.locator('#modalBox').inner_text()
                assert g.evaluate('sessionFinalizeExportMeta') is None
                h=page()
                h.evaluate("""async()=>{
                  S.onboarding.done=true;save();localStorage.setItem('jpw_fs','1');openFinalizeSessionFlow();
                  await beginSessionExport();
                  localStorage.setItem('jpw_fs','2');
                  await finalizeJPWealthSession();
                }""")
                assert 'Exporte uma nova cópia' in h.locator('#modalBox').inner_text()
                assert h.evaluate('jpWealthPersistenceIsBlocked()') is False
                print('PASS preferences changed during export / before finalization are refused',flush=True)
                for change in ['future','unknown-key','bad-image','bad-drafts','nested-pollution','bad-glass-tint','bad-submenu-rail']:
                    bad=json.loads(json.dumps(payload))
                    if change=='future':bad['workspace']['schemaVersion']=2
                    if change=='unknown-key':bad['workspace']['preferences']['foreign_app']='x'
                    if change=='bad-image':bad['workspace']['preferences']['jpwealth_local_profile_v1']=json.dumps(dict(schemaVersion=1,displayName='x',avatarDataUrl='data:image/jpeg;base64,YWJj'))
                    if change=='bad-drafts':bad['workspace']['drafts']=[{'label':'x','text':{}}]
                    if change=='nested-pollution':bad['workspace']['preferences']['jpwealth_galton_preferences_v1']='{"__proto__":{"x":1}}'
                    if change=='bad-glass-tint':bad['workspace']['preferences']['jpw_nav_glass_tint']='101'
                    if change=='bad-submenu-rail':bad['workspace']['preferences']['jpw_nav_submenu_rail']='wide'
                    outcome=d.evaluate('''bad=>{const before=JSON.stringify(Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)])));try{normalizeImportedState(bad);return false;}catch(e){return before===JSON.stringify(Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)])));}}''',bad)
                    assert outcome,change
                print('PASS invalid workspace rejected before mutation',flush=True)
        browser.close()
    server.shutdown()
if __name__=='__main__':main()

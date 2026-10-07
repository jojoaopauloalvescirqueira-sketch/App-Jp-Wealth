#!/usr/bin/env python3
"""Real application adapters in isolated Chromium; no user profile or data."""
import functools,json,threading,argparse
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap
from dashboard_macro_test import launch_browser
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
class Server(ThreadingHTTPServer):
    request_queue_size=128
    daemon_threads=True

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifact');args=parser.parse_args()
    results=[]
    server=Server(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    with sync_playwright() as p:
        browser=launch_browser(p)
        for path in ['index.html','dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']:
            ctx=browser.new_context();install_bootstrap(ctx);page=ctx.new_page();errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('dialog',lambda d:d.accept())
            page.goto(f'http://127.0.0.1:{server.server_port}/{path}');wait_bootstrap(page)
            page.evaluate("closeModal();window.__onbShown=true;S.onboarding.done=true;save();")
            assert not errors,errors
            def check(name,js):
                value=page.evaluate(js)
                assert value.get('ok'),(name,value,errors)
                results.append({'path':path,'check':name,'status':'PASS','evidence':value})
            check('PF input survives remount and explicit recovery without save',r'''()=>{
                const month='2026-10';fbMonth=month;const added=pfActAddIncome(month,{name:'Synthetic income',projectedAmount:100});
                if(!added.ok)return {ok:false,added};finpesBudgetRender();
                const selector='[data-fi-id="'+added.recordId+'"][data-fi-campo="name"]';
                let input=document.querySelector(selector);input.value='Unsaved synthetic';input.dispatchEvent(new Event('input',{bubbles:true}));
                const before=localStorage.getItem(LSKEY);finpesBudgetRender();input=document.querySelector(selector);
                const captured=jpwWorkspaceDrafts().find(d=>d.provider==='personal-finance-field');
                if(input.value!=='Unsaved synthetic'||!captured)return {ok:false,value:input.value,captured};
                fbPendingFields.clear();finpesBudgetRender();
                const inspect=JPWWorkspaceDrafts.inspect(captured),restored=JPWWorkspaceDrafts.reopen(captured);
                return {ok:inspect.compatible&&restored.ok&&localStorage.getItem(LSKEY)===before&&document.querySelector(selector).value==='Unsaved synthetic',inspect,restored};
            }''')
            check('Incompatible field refuses reopening',r'''()=>{
                const item=jpwWorkspaceDrafts().find(d=>d.provider==='personal-finance-field');
                fbPendingFields.clear();item.baseReference='"different original"';
                const before=localStorage.getItem(LSKEY),result=JPWWorkspaceDrafts.reopen(item);
                return {ok:!result.ok&&localStorage.getItem(LSKEY)===before,result};
            }''')
            check('Navigation draft captured independently of confirmed order',r'''()=>{
                beginNavOrderPreview();navOrderState.draft.reverse();navOrderState.editing=true;
                const item=jpwWorkspaceDrafts().find(d=>d.provider==='navigation-order'),before=localStorage.getItem(NAV_ORDER_KEY);
                cancelNavOrderPreview();const inspected=JPWWorkspaceDrafts.inspect(item),restored=JPWWorkspaceDrafts.reopen(item);
                const ok=!!item&&inspected.compatible&&restored.ok&&navOrderDirty()&&localStorage.getItem(NAV_ORDER_KEY)===before;
                cancelNavOrderPreview();closeSettingsModal();return {ok,inspected,restored};
            }''')
            check('NoCuda programmatically loaded parameters are captured but not validated on recovery',r'''()=>{
                document.getElementById('nocudaPayload').value=JPWNocudaTransfer.example();
                const item=jpwWorkspaceDrafts().find(d=>d.provider==='nocuda-transfer'),before=localStorage.getItem(LSKEY);
                document.getElementById('nocudaClear').click();const restored=JPWWorkspaceDrafts.reopen(item);
                return {ok:restored.ok&&document.getElementById('nocudaPayload').value===item.text&&document.getElementById('nocudaSave').disabled&&localStorage.getItem(LSKEY)===before,restored};
            }''')
            check('Profile explicit reopen preserves stored preference',r'''()=>{
                beginSettingsProfileDraft();settingsProfileState.draft.displayName='Unsaved synthetic profile';settingsProfileState.editing=true;
                const item=jpwWorkspaceDrafts().find(d=>d.provider==='profile'),before=localStorage.getItem(SETTINGS_PROFILE_KEY);
                cancelSettingsProfileDraft();const restored=JPWWorkspaceDrafts.reopen(item);
                const ok=restored.ok&&settingsProfileState.draft.displayName==='Unsaved synthetic profile'&&localStorage.getItem(SETTINGS_PROFILE_KEY)===before;
                cancelSettingsProfileDraft();closeSettingsModal();return {ok,restored};
            }''')
            check('Notes draft reopens without promoting a fact',r'''()=>{
                mvpNotesUI.selectedId=null;mvpNotesUI.draft={...mvpNotesNewDraft(),content:'Recovered synthetic note'};mvpNotesUI.draftDirty=true;
                const item=jpwWorkspaceDrafts().find(d=>d.provider==='notes'),before=localStorage.getItem(LSKEY);
                mvpNotesCloseEditor();const restored=JPWWorkspaceDrafts.reopen(item);
                const ok=restored.ok&&mvpNotesUI.draft.content==='Recovered synthetic note'&&mvpNotesUI.draftDirty&&localStorage.getItem(LSKEY)===before;
                mvpNotesCloseEditor();closeMvpNotesDrawer();return {ok,restored};
            }''')
            check('Notes appearance and folder drafts reopen without saving',r'''()=>{
                mvpNotesBeginAppearance();mvpNotesAppearanceState.draft.text='larger';
                const appearance=jpwWorkspaceDrafts().find(d=>d.provider==='notes'&&d.context.kind==='appearance');
                mvpNotesCancelAppearance();const before=localStorage.getItem(LSKEY),pref=localStorage.getItem(MVP_NOTES_APPEARANCE_KEY);
                const restored=JPWWorkspaceDrafts.reopen(appearance);
                const appearanceOk=restored.ok&&mvpNotesAppearanceState.draft.text==='larger'&&localStorage.getItem(LSKEY)===before&&localStorage.getItem(MVP_NOTES_APPEARANCE_KEY)===pref;
                mvpNotesCancelAppearance();closeSettingsModal();
                mvpNotesUI.folderNameDrafts={new:'Unsaved synthetic folder'};
                const folders=jpwWorkspaceDrafts().find(d=>d.provider==='notes'&&d.context.kind==='folders');
                mvpNotesUI.folderNameDrafts={};const result=JPWWorkspaceDrafts.reopen(folders);
                const ok=appearanceOk&&result.ok&&mvpNotesUI.folderNameDrafts.new==='Unsaved synthetic folder'&&localStorage.getItem(LSKEY)===before;
                mvpNotesUI.folderNameDrafts={};closeMvpNotesDrawer();return {ok};
            }''')
            check('Malformed Notes fields and unavailable folders refuse reopening',r'''()=>{
                const base={provider:'notes',version:1,label:'Synthetic',baseReference:JSON.stringify(S.mvpNotes),context:{kind:'note'}};
                const valid={...mvpNotesNewDraft(),selectedId:null,content:'Synthetic'};
                const invalid=[[],{...valid,content:{}},{...valid,type:'GHOST'},{...valid,folderId:'missing-folder'},{...valid,selectedId:'missing-note'}];
                const before=localStorage.getItem(LSKEY),all=invalid.every(value=>!JPWWorkspaceDrafts.inspect({...base,text:JSON.stringify(value)}).compatible);
                return {ok:all&&localStorage.getItem(LSKEY)===before};
            }''')
            check('Planning fields reopen at new epoch without save',r'''()=>{
                const created=JPWFx.state.fxPlanCreate({name:'Synthetic plan',assumptions:{startMonth:'2026-01',horizonMonths:12,initialBalanceUsd:1000,defaultMonthlyReturn:0.01,projectedFxRate:5}});
                if(!created.ok)return {ok:false,created};renderFxPlanning();
                const group='planning',identity=[jpWealthPersistenceEpoch(),S.fxPlanning.plan.id,group,null];
                fxpInputDrafts.set(JSON.stringify(identity),{group,fields:{fxpEditRate:'2.5'}});
                const item=jpwWorkspaceDrafts().find(d=>d.provider==='planning'),before=localStorage.getItem(LSKEY);
                fxpInputDrafts.clear();const restored=JPWWorkspaceDrafts.reopen(item);
                const field=document.getElementById('fxpEditRate');
                const ok=restored.ok&&fxpInputDrafts.size===1&&field?.value==='2.5'&&localStorage.getItem(LSKEY)===before;
                fxpInputDrafts.clear();return {ok,restored,field:field?.value};
            }''')
            check('Forged draft selectors and malformed identities refuse reopening',r'''()=>{
                const pf={provider:'personal-finance-field',version:1,label:'Synthetic',text:'2',baseReference:'null',context:{month:'2026-10',collection:'incomes',id:S.personalFinance.months['2026-10'].incomes[0].id,field:'doesNotExist',selector:'#pMDD'}};
                const planning={provider:'planning',version:1,label:'Synthetic',baseReference:JSON.stringify(S.fxPlanning),text:JSON.stringify({inputs:[{identity:{}}],months:[],auxiliary:[]}),context:{}};
                return {ok:!JPWWorkspaceDrafts.inspect(pf).compatible&&!JPWWorkspaceDrafts.inspect(planning).compatible};
            }''')
            check('Widget migration preserves old key on refused write',r'''()=>{
                for(const k of [JP_WIDGET_STORAGE_KEY_V6,JP_WIDGET_STORAGE_KEY_V5,JP_WIDGET_STORAGE_KEY_V4,JP_WIDGET_STORAGE_KEY_V3,JP_WIDGET_STORAGE_KEY_V2])localStorage.removeItem(k);
                const layout=dashLayoutNormalizeV6(null),legacy={version:5,screens:structuredClone(layout.screens)};
                const raw=JSON.stringify(legacy);localStorage.setItem(JP_WIDGET_STORAGE_KEY_V5,raw);
                const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===JP_WIDGET_STORAGE_KEY_V6)throw Error('synthetic quota');return original.call(this,k,v);};
                let candidate;try{candidate=dashLayoutLoadFullState();}finally{Storage.prototype.setItem=original;}
                return {ok:localStorage.getItem(JP_WIDGET_STORAGE_KEY_V5)===raw&&localStorage.getItem(JP_WIDGET_STORAGE_KEY_V6)===null&&candidate.version===6};
            }''')
            check('Widget v2 promotes current envelope and verified write before removal',r'''()=>{
                localStorage.removeItem(JP_WIDGET_STORAGE_KEY_V5);
                const current=dashLayoutNormalizeV6(null),widgets=structuredClone(current.screens.dash.widgets);
                const legacy={version:2,dashboard:{widgets}};
                const valid=dashLayoutValidateV2Legacy(legacy);if(!valid)return {ok:false,reason:'synthetic legacy invalid'};
                localStorage.setItem(JP_WIDGET_STORAGE_KEY_V2,JSON.stringify(legacy));const candidate=dashLayoutLoadFullState();
                return {ok:candidate.version===6&&JSON.stringify(candidate.screens.dash.widgets)===JSON.stringify(valid)&&localStorage.getItem(JP_WIDGET_STORAGE_KEY_V2)===null&&JSON.parse(localStorage.getItem(JP_WIDGET_STORAGE_KEY_V6)).version===6};
            }''')
            assert not errors,errors
            ctx.close()
        browser.close()
    server.shutdown()
    receipt={'results':results,'summary':{'PASS':len(results)},'scope':'Synthetic application adapters; native folder/Safari/Firefox/hosted transfer NOT_RUN'}
    if args.artifact:Path(args.artifact).write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Proportion contract over existing browser/domain fixtures, fixed before CSS.

Reports observed geometry separately from pass/fail; baseline mode never changes
expectations. Native 200% uses an isolated Chromium profile and verifies the viewport ratio; text preference is tested separately.
"""
import argparse
import ast
import math
import tempfile
from collections import Counter
from functools import partial
import hashlib
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from design_experience_test import Quiet, SETUP, ALLADIN_SEED, settings_visual_pages
from design_pf_comparison_test import seed as seed_pf
from studies_notes_persistence_contract_test import NC, PV
from nocoda_test import fill_anchors

SURFACES = [
    ('dashboard', 'dashboard', None), ('forex', 'forex-overview', None),
    ('preparation', 'forex-preparation', None), ('account', 'forex-account', None),
    ('operation', 'forex-operation', None), ('reconciliation', 'forex-reconciliation', None),
    ('planning', 'forex-planning', None), ('pf', 'personal-finance', None),
    ('pf-budget', 'personal-finance', ['finpes', 'mensal']),
    ('pf-debts', 'personal-finance', ['finpes', 'dividas']),
    ('pf-comparison', 'personal-finance', ['finpes', 'comparativo']),
    ('pf-scenarios', 'personal-finance', ['finpes', 'cenarios']),
    ('research', 'research-stocks-br', None), ('calendar', 'ecal', None),
    ('nocoda', 'nocoda', None), ('pivots', 'pivots', None),
    ('lab', 'probability-lab', None), ('alladin', 'alladin', None),
    ('notes', 'dashboard', 'notes'), ('settings', 'dashboard', 'settings')]


def note_creator(root):
    # Reuse named helpers without importing the module-level Notes suite.
    source=root/'tools/mvp_notes_test.py';tree=ast.parse(source.read_text())
    names={'click_id','open_inspector','start_new_note','create_note'}
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names
           or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NEW_MODAL_FIELDS' for t in n.targets)]
    assert len(nodes)==5, 'Existing Notes fixture helper contract changed'
    scope={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),scope)
    return scope['create_note']


def populate(page,root):
    seed_pf(page)
    page.evaluate("JPWNavigation.navigate('nocoda')")
    fill_anchors(page,NC);page.locator('#ncSaveBtn').click()
    assert page.evaluate('!ncDirty'), 'NoCoda synthetic save not confirmed'
    page.evaluate("""pv=>{
      const instrument=instrumentCatalog()[0].id;
      S.pivotStudies.studies=[{id:'proportion-synthetic',instrumentId:instrument,periodStart:'2025-01-01',periodEnd:'2025-12-31',createdAt:'2025-01-01',updatedAt:'2025-01-01',pivots:[pv]}];
      pvInstrumentId=instrument;pvStudyId='proportion-synthetic';pvDraft=null;pvDirty=false;pvFormOpen=false;pvNewStudyOpen=false;
      if(save()!==true)throw Error('Pivots synthetic seed refused');
    }""",PV)
    note_creator(root)(page,'task','Conferência sintética de proporção','Texto de leitura com descrição detalhada.\nNenhum dado real foi utilizado.','medium','open')
    page.keyboard.press('Escape')
    page.evaluate('closeModal()')

MEASURE = r"""() => {
 const visible=e=>e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0&&getComputedStyle(e).visibility!=='hidden'&&!e.closest('[inert]');
 const info=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return {tag:e.tagName,id:e.id,cls:String(e.className),text:e.innerText?.slice(0,110),font:parseFloat(s.fontSize),line:s.lineHeight,weight:s.fontWeight,width:r.width,height:r.height,x:r.x,y:r.y,gap:s.gap,padding:s.padding,whiteSpace:s.whiteSpace,overflow:s.overflow,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth}};
 return {build:JP_WEALTH_BUILD_ID,width:innerWidth,height:innerHeight,dpr:devicePixelRatio,zoom:getComputedStyle(document.documentElement).zoom,
 overflow:document.documentElement.scrollWidth>innerWidth+1,
 overflowElements:[...document.querySelectorAll('main,section,article,div,table')].filter(visible).filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,30).map(info),
 headings:[...document.querySelectorAll('h1,h2,h3,h4,.dm-title,.dm-shell-title,.mc-clearance-title')].filter(visible).map(info),
 text:[...document.querySelectorAll('p,label,small,.note,.settings-nav-card-title,.settings-nav-card-desc')].filter(visible).map(info),
 controls:[...document.querySelectorAll('button,input,select,textarea,a[href]')].filter(visible).map(info),
 settings:document.getElementById('settingsOverlay')?.classList.contains('show')};
}"""

def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    identity_files=['index.html','src/styles/app.css','src/js/40-app/09-settings-modal.js',
                    'src/js/manifest.json','build-id.js','tools/visual_proportion_test.py',
                    'tools/design_experience_test.py','tools/apple_experience_test.py']
    inputs_before={f:hashlib.sha256((args.root/f).read_bytes()).hexdigest() for f in identity_files}
    rows, checks = [], []
    def check(name, ok, detail=None):
        checks.append({'name': name, 'result': 'PASS' if ok else 'PRODUCT_FAIL', 'detail': detail})
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(args.root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    cases = [(w,t,1,False) for w in args.widths for t in ['light','dark']]
    if args.stress:
        cases += [(w,t,1.25,True) for w in [390,1440] for t in ['light','dark']]
        cases += [(1440,t,2,False) for t in ['light','dark']]
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('JP_WEALTH_CHROMIUM'): opts['executable_path']=os.environ['JP_WEALTH_CHROMIUM']
            browser=pw.chromium.launch(**opts)
            for width,theme,scale,long in cases:
                label=f'{width}-{theme}-scale{scale}-long{int(long)}'
                if scale==2:
                    profile=Path(tempfile.mkdtemp(prefix='native-200-',dir=args.output))
                    (profile/'Default').mkdir()
                    (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
                    context=pw.chromium.launch_persistent_context(str(profile.resolve()),headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
                else:
                    context=browser.new_context(viewport={'width':width,'height':1000},service_workers='block',reduced_motion='reduce')
                install_bootstrap(context); context.add_init_script('window.__onbShown=true')
                page=context.pages[0] if context.pages else context.new_page(); errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                try:
                    page.goto(f'http://127.0.0.1:{server.server_port}/index.html'); wait_bootstrap(page)
                    page.evaluate(SETUP,theme);page.evaluate(ALLADIN_SEED)
                    if args.populated:populate(page,args.root)
                    if scale==2:check(label+' native 200 percent confirmed',page.evaluate('Math.abs(outerWidth/innerWidth-2)<0.01 && getComputedStyle(document.documentElement).zoom===\"1\"'))
                    elif scale==1.25: page.evaluate("document.documentElement.dataset.fs='2'")
                    for name,route,local in SURFACES:
                        if args.areas and name not in args.areas: continue
                        key=f'{label}-{name}'
                        try:
                            page.evaluate('closeModal()')
                            check(key+' route accessible',page.evaluate('(r)=>JPWNavigation.navigate(r)',route))
                            if isinstance(local,list):check(key+' local accessible',page.evaluate('([s,v])=>JPWNavigation.navigateLocal(s,v)',local))
                            if name=='pf-budget' and page.locator('#modalOverlay').is_visible():
                                if args.screenshots:page.screenshot(path=str(args.output/f'{key}-previous-month-dialog.png'),animations='disabled')
                                page.locator('#fbPendContinue').click()
                            if local=='settings':
                                page.locator('#headerConfigBtn').click()
                                if page.evaluate('innerWidth')<=760:
                                    if args.screenshots:page.screenshot(path=str(args.output/f'{key}-categories.png'),animations='disabled')
                                    # The mobile list is a first-class Settings state.
                            if local=='notes':page.locator('#headerNotesBtn').click()
                            page.wait_for_timeout(80)
                            before=page.evaluate('JSON.stringify({S,storage:Object.entries(localStorage).sort()})')
                            if long and name!='settings':
                                page.evaluate(r"""() => {
                                  const scope=document.querySelector('#settingsOverlay.show')||document.querySelector('.view.active')||document.body;
                                  for(const e of scope.querySelectorAll('h2,h3,h4,.settings-nav-card-desc,.settings-nav-card-title')) {
                                    if(e.children.length||!e.getBoundingClientRect().width)continue;
                                    e.textContent+=' · exemplo sintético de descrição detalhada com palavras e identificação extensa';
                                  }
                                }""")
                            info=page.evaluate(MEASURE);rows.append({'case':key,'surface':name,**info})
                            check(key+' document reflow',not info['overflow'],info['width'])
                            check(key+' title present',bool(info['headings']))
                            legacy=page.locator('.gd-vrm-limits,.account-table-note,.account-chip,.acct-period-link,.pv-mini').evaluate_all('es=>es.filter(e=>e.getBoundingClientRect().width>0&&!e.closest(\"[inert]\")).map(e=>({cls:e.className,font:parseFloat(getComputedStyle(e).fontSize),h:e.getBoundingClientRect().height,action:e.tagName===\"BUTTON\"}))')
                            f=1.25 if scale==1.25 else 1
                            check(key+' residual labels use readable roles',all(x['font']>=12*f for x in legacy),legacy)
                            check(key+' residual actions retain targets',all(x['h']>=24 for x in legacy if x['action']),legacy)
                            if name=='dashboard':
                                labels=page.locator('#headerActions .header-action-label').evaluate_all('''es=>es.map(e=>({text:e.textContent,h:e.getBoundingClientRect().height,line:parseFloat(getComputedStyle(e).lineHeight),zoom:parseFloat(getComputedStyle(document.documentElement).zoom)||1}))''')
                                check(key+' Configurações label not split',all(x['h']<=x['line']*x['zoom']+1 for x in labels if x['text']=='Configurações'),labels)
                            if name=='settings':
                                check(key+' modal actually open',page.locator('#settingsModal').is_visible())
                                page.locator('#settingsSearch').fill('backup')
                                result=page.locator('#settingsSearchResults [data-settings-result]')
                                check(key+' search results',result.count()>0)
                                page.locator('#settingsSearch').fill('')
                                def observe(target,geometry):
                                    rows.append({'case':key+'-'+target,'surface':'settings','page':target,'geometry':geometry})
                                    if args.screenshots:
                                        # Compare resting composition with BEFORE. A real pointer
                                        # click on the heading clears keyboard focus styling without
                                        # disabling focus CSS or invoking any setting action.
                                        if target!='categories':
                                            page.locator('[data-settings-panel]:not([hidden]) .settings-hero-title').click()
                                        page.screenshot(path=str(args.output/f'{key}-{target}.png'),animations='disabled')
                                settings_visual_pages(page,lambda n,v,d=None:check(key+' '+n,v,d),observe,long=long)
                                page.evaluate("settingsNavigate('general',{push:true,focus:true})")
                            if args.screenshots:
                                page.screenshot(path=str(args.output/f'{key}.png'),animations='disabled')
                            after=page.evaluate('JSON.stringify({S,storage:Object.entries(localStorage).sort()})')
                            check(key+' measurement preserves data/preferences',before==after)
                            if local in ['settings','notes']:
                                page.keyboard.press('Escape')
                                opener='headerConfigBtn' if local=='settings' else 'headerNotesBtn'
                                page.wait_for_timeout(80)
                                check(key+' close restores focus',page.evaluate('(id)=>document.activeElement.id===id',opener))
                            print(key,flush=True)
                        except Exception as ex:
                            checks.append({'name':key,'result':'TEST_HARNESS_FAIL','detail':str(ex)})
                            print('INTERRUPTED',key,str(ex)[:140],flush=True)
                    if args.populated and not args.areas:
                        page.evaluate("JPWNavigation.navigateLocal('finpes','mensal');fbGoTo('2026-09')")
                        trigger=page.locator('[data-fi-cfg]').first
                        trigger.focus();page.keyboard.press('Enter');page.locator('#fbRecOn').wait_for()
                        check(label+' recurrence initial focus',page.evaluate("document.activeElement.id==='fbRecOn'"))
                        snapshot=page.evaluate('JSON.stringify(S.personalFinance)')
                        page.locator('#fbRecOn').check();page.locator('#fbRecAmount').fill('');page.locator('#modalConfirm').click()
                        check(label+' invalid field retained in dialog',page.locator('#modalOverlay').is_visible() and page.locator('#fbRecAmount').get_attribute('aria-invalid')=='true')
                        sizes=page.locator('#fbRecAmount,#fbRecStart,#fbRecEnd').evaluate_all('es=>es.map(e=>({w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))')
                        z=1  # DOM rectangles use CSS pixels, including native browser zoom
                        check(label+' month fields share control geometry',len(sizes)==3 and all(x['h']>=40*z for x in sizes) and max(x['w'] for x in sizes)-min(x['w'] for x in sizes)<2,sizes)
                        check(label+' invalid field preserves PF',snapshot==page.evaluate('JSON.stringify(S.personalFinance)'))
                        if args.screenshots:page.screenshot(path=str(args.output/f'{label}-pf-error-dialog.png'),animations='disabled')
                        page.keyboard.press('Escape');check(label+' dialog cancellation returns focus',trigger.evaluate('e=>e===document.activeElement'))
                        page.locator('#headerNotesBtn').click()
                        if page.locator('[data-mvp-folder=all]').is_visible():page.locator('[data-mvp-folder=all]').click()
                        if not page.locator('#mvpNoteContent').is_visible():page.locator('[data-mvp-note-id]:visible').first.click()
                        check(label+' populated ticket editor',page.locator('#mvpNoteContent').is_visible())
                        if args.screenshots:page.screenshot(path=str(args.output/f'{label}-notes-editor.png'),animations='disabled')
                        page.keyboard.press('Escape')
                    check(label+' no uncaught errors' ,not errors,errors)
                    assert_fixture_requests(context)
                finally:context.close()
            browser.close()
    except Exception as ex:
        checks.append({'name':'evaluation interrupted','result':'TEST_HARNESS_FAIL','detail':str(ex)})
        print('INTERRUPTED',str(ex),flush=True)
    finally:
        server.shutdown()
        inputs_after={f:hashlib.sha256((args.root/f).read_bytes()).hexdigest() for f in identity_files}
        if inputs_after!=inputs_before:
            checks.append({'name':'candidate or visual oracle changed during run','result':'ENVIRONMENT_ERROR','detail':inputs_after})
        summary=dict(Counter(c['result'] for c in checks))
        report={'root':str(args.root),'build_file':(args.root/'build-id.js').read_text(),'inputs_before_sha256':inputs_before,'inputs_after_sha256':inputs_after,'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'css_sha256':hashlib.sha256((args.root/'src/styles/app.css').read_bytes()).hexdigest(),'checks':checks,'observations':rows,'summary':summary,'limits':['Native200 uses a temporary Chromium profile; scale1.25 is the existing font preference, not browser zoom','Synthetic Chromium only; no user acceptance or integral accessibility claim']}
        (args.output/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
        print(json.dumps(summary),flush=True)
    return 0 if checks and all(c['result']=='PASS' for c in checks) else 1

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True);p.add_argument('--widths',type=lambda s:list(map(int,s.split(','))),default=[320,390,768,1024,1440]);p.add_argument('--areas',type=lambda s:s.split(','));p.add_argument('--populated',action='store_true');p.add_argument('--stress',action='store_true');p.add_argument('--screenshots',action='store_true')
    raise SystemExit(run(p.parse_args()))

#!/usr/bin/env python3
"""Additive Management geometry contract; reuses the established 2 CSS px oracle.

Financial writes are permitted only for explicit synthetic fixture setup. Native
200% uses a fresh real-Chrome profile, never a CSS/device-scale substitute.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler
import json
import math
from pathlib import Path
import shutil
import tempfile
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options
import management_annual_ui_test as journey
import ui_visual_quality_test as visual

ROOT=Path(__file__).resolve().parents[1]
LAYOUTS=('sidebar','topbar','glass','submenu')
THEMES=('light','dark')
SIZES=((320,700),(390,844),(1440,1000),(1440,480))
SOURCES=('index.html','src/styles/app.css','src/js/30-accounting/07-management/01-engine.js',
         'src/js/30-accounting/07-management/02-state.js','src/js/30-accounting/07-management/03-ui.js',
         'tools/management_visual_quality_test.py','tools/ui_visual_quality_test.py',
         'tools/quality_gate.py','tools/management_annual_ui_test.py','tools/browser_bootstrap_fixture.py',
         'tools/notes_launcher_test.py','src/js/00-core/04-persistence.js',
         'src/js/00-core/08-module-availability.js','src/js/10-domain/00-forex-state.js',
         'src/js/40-app/01-navigation.js','src/js/40-app/11-operational-shell.js')


def required_ids(native=True):
    # Frozen independent of the execution matrix variables above: deleting a
    # runtime layout/size/theme cannot turn incomplete execution into PASS.
    result=[f'management-{layout}-{theme}-{size}'
            for layout in ('sidebar','topbar','glass','submenu')
            for theme in ('light','dark')
            for size in ('320x700','390x844','1440x1000','1440x480')]
    result += [f'management-useful-{layout}-{theme}-{width}'
               for layout in ('sidebar','topbar','glass','submenu')
               for theme in ('light','dark') for width in (899,900,901)]
    result += ['management-draft-cursor-resize','management-counterproof-svg',
               'management-counterproof-text','management-counterproof-overflow',
               'management-counterproof-duplicate']
    if native:
        result += [f'management-native200-{layout}-{theme}'
                   for layout in ('sidebar','topbar','glass','submenu')
                   for theme in ('light','dark')]
    return result


def coverage_proofs(cases,expected):
    return {'empty':visual.rejected(lambda:visual.validate_coverage([],expected)),
            'missing':visual.rejected(lambda:visual.validate_coverage(cases[1:],expected)),
            'duplicate':visual.rejected(lambda:visual.validate_coverage(cases+[cases[0]],expected)),
            'not_run':visual.rejected(lambda:visual.validate_coverage([{**c,'classification':'NOT_RUN'} if i==0 else c for i,c in enumerate(cases)],expected))}


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_):pass


def hashes():
    return {p:sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}


def settle(page):
    page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')


def prepare(context,url):
    install_bootstrap(context,{'USDBRL':5})
    context.add_init_script('window.__onbShown=true;')
    page=context.new_page()
    page.clock.set_fixed_time(datetime(2026,10,26,15,tzinfo=timezone.utc))
    page._management_visual_errors=[]
    page.on('pageerror',lambda e:page._management_visual_errors.append(str(e)))
    page.goto(url,wait_until='load');wait_bootstrap(page);page.evaluate('closeModal()')
    journey.smoke(page);scope=journey.seed(page)
    page.evaluate("navigateToScreen('dashboard');navigateToScreen('management-accounting')")
    journey.choose(page,scope);journey.configure(page,scope)
    receipt=page.evaluate('''t=>JPWManagementAnnual.commands.recordResult({target:{...t,year:2026},date:'2026-10-01',value:-123456789.125},
      {token:JPWManagementAnnual.queries.token({...t,year:2026}),confirm:true,reason:'Synthetic large negative visual fixture'})''',scope)
    assert receipt['ok'],receipt
    page.evaluate('JPWManagement.render()')
    page.evaluate('''()=>{
      window.__mgVisualWrites=[];
      const writer=jpWealthPersistDocument;
      jpWealthPersistDocument=function(...args){__mgVisualWrites.push(args[1]?.component||'state');return writer.apply(this,args)};
    }''')
    return page


def snapshot(page):
    return page.evaluate("({state:JSON.stringify(S),financialRaw:localStorage.getItem(LSKEY)})")


def unchanged(page,before):
    assert snapshot(page)==before,'Visual interaction changed financial state or confirmed document'
    assert page.evaluate('__mgVisualWrites')==[],'Visual interaction attempted a financial write'
    assert not page._management_visual_errors,page._management_visual_errors


GEOMETRY=r'''()=>{
 const box=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
 const visible=e=>!!e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
 const host=document.getElementById('managementContent'),table=host.querySelector('.mg-sheet'),wrap=host.querySelector('.mg-table-wrap'),title=document.querySelector('#management>.mg-title');
 const first=host.querySelector('.mg-day'),lastHeader=table.tHead.rows[1];
 const duplicate=['[data-mg-account]','[data-mg-period]','[data-mg-year]'].map(s=>document.querySelectorAll('#management '+s).length);
 return {pageOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,host:box(host),table:box(table),wrap:box(wrap),
   tableOverflow:wrap.scrollWidth-wrap.clientWidth,titlePosition:getComputedStyle(title).position,columns:[...lastHeader.cells].filter(visible).length,
   compact:host.classList.contains('mg-compact'),duplicate,
   controls:[...document.querySelectorAll('#management :is(button,select,input)')].filter(visible).map(e=>({label:e.getAttribute('aria-label')||e.textContent.trim()||e.closest('label')?.textContent.trim(),tag:e.tagName,...box(e)})),
   cells:[...first.cells].filter(visible).map(e=>{const s=getComputedStyle(e);return {text:e.textContent.trim(),overflow:e.scrollWidth-e.clientWidth,textOverflow:s.textOverflow,...box(e)}})};
}'''


def geometry(page):
    data=page.evaluate(GEOMETRY)
    assert data['pageOverflow']<=visual.EPSILON,('page horizontal overflow',data)
    assert data['tableOverflow']<=visual.EPSILON,('table requires horizontal scrolling',data)
    assert data['titlePosition'] not in ('sticky','fixed'),('Local management heading cannot become an app header',data)
    assert data['duplicate']==[1,1,1],('context controls must be unique',data)
    assert data['columns']==(3 if data['host']['width']<900 else 11),('useful-width column contract',data)
    assert data['compact']==(data['host']['width']<900),('900px useful-width boundary',data)
    for control in data['controls']:
        assert control['height']>=44-visual.EPSILON and control['width']>=44-visual.EPSILON,('44px interaction target',control)
        assert control['label'],('accessible control name missing',control)
    for cell in data['cells']:
        assert cell['overflow']<=visual.EPSILON and cell['textOverflow']!='ellipsis',('full monetary cell text must remain available',cell)
    return data


def dialog_geometry(page):
    trigger=page.locator('#management [data-mg-action=info]')
    trigger.scroll_into_view_if_needed();trigger.click()
    dialog=page.locator('dialog.mg-dialog[open]');close=dialog.locator('[data-mg-action=close-dialog]')
    measured=visual.centered(close,'ink',True)
    bound=dialog.evaluate('e=>({box:e.getBoundingClientRect().toJSON(),w:innerWidth,h:innerHeight,scroll:e.scrollHeight,client:e.clientHeight,overflow:getComputedStyle(e).overflowY})')
    b=bound['box'];assert b['left']>=-visual.EPSILON and b['right']<=bound['w']+visual.EPSILON,('dialog horizontal viewport',bound)
    assert b['top']>=-visual.EPSILON and b['bottom']<=bound['h']+visual.EPSILON,('dialog vertical viewport',bound)
    if bound['scroll']>bound['client']+visual.EPSILON:assert bound['overflow'] in ('auto','scroll'),('dialog overflow inaccessible',bound)
    close.focus();page.keyboard.press('Escape')
    assert dialog.count()==0,'Escape must close local dialog'
    assert trigger.evaluate('e=>document.activeElement===e'),'Escape must return focus to its real trigger'
    return {'close':measured,'viewport':bound}


def scenario(page,capture=None):
    before=snapshot(page);page.evaluate('__mgVisualWrites=[]');settle(page)
    result={'geometry':geometry(page)}
    if capture:
        page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(capture)+'-top.png')
        page.locator('.mg-table-wrap').scroll_into_view_if_needed();page.screenshot(path=str(capture)+'-table.png')
    for selector in ('#management>.mg-title [data-mg-action=history]',
                     '#management>.mg-title [data-mg-action=info]',
                     '#management [data-mg-action=edit-plan]',
                     '#management .mg-day [data-mg-action=edit-day]'):
        node=page.locator(selector).first
        if selector.endswith('[data-mg-action=edit-day]') and result['geometry']['compact']:
            assert not node.is_visible(),'The compact table must move editing into explicit details'
            continue
        node.scroll_into_view_if_needed();result[selector]=visual.centered(node)
    result['dialog']=dialog_geometry(page)
    page.locator('.mg-table-wrap').evaluate('e=>e.scrollTop=e.scrollHeight')
    last=page.locator('#management .mg-day [data-mg-detail]').last
    last.scroll_into_view_if_needed();last.focus();page.keyboard.press('Enter')
    assert last.get_attribute('aria-expanded')=='true','Daily details must be keyboard accessible after full scroll'
    page.keyboard.press('Enter')
    page.locator('.mg-table-wrap').evaluate('e=>e.scrollTop=0')
    unchanged(page,before)
    return result


def draft_resize(page):
    before=snapshot(page)
    button=page.locator('#management .mg-day [data-mg-action=edit-day]').first
    button.scroll_into_view_if_needed();button.click()
    field=page.locator('[data-mg-editor=day] [name=note]')
    field.fill('Synthetic retained cursor');field.focus();field.evaluate('e=>e.setSelectionRange(4,9)')
    handle=field.element_handle()
    page.set_viewport_size({'width':390,'height':700});settle(page)
    assert field.evaluate('(e,old)=>e===old',handle),'Responsive rendering duplicated/replaced the draft control'
    assert field.evaluate('e=>[e.value,e.selectionStart,e.selectionEnd,document.activeElement===e]')==['Synthetic retained cursor',4,9,True]
    for action in ('review-day','cancel-edit'):
        control=page.locator('[data-mg-editor=day] [data-mg-action='+action+']');control.scroll_into_view_if_needed();visual.centered(control)
    page.locator('[data-mg-action=cancel-edit]').click();page.set_viewport_size({'width':1440,'height':1000});settle(page)
    unchanged(page,before)
    return {'same_node':True,'cursor':[4,9],'financial_writes':0}


def record(report,id,run,**meta):
    case={'id':id,**meta}
    try:case['result']=run();case['classification']='PASS'
    except Exception as error:
        case['classification']='PRODUCT_FAIL' if isinstance(error,AssertionError) else 'TEST_HARNESS_FAIL';case['error']=str(error);raise
    finally:report['cases'].append(case);print(case['classification'],id,flush=True)


def front_width(page,wanted):
    for _ in range(5):
        width=page.locator('#managementContent').evaluate('e=>e.getBoundingClientRect().width')
        if abs(width-wanted)<=visual.EPSILON:return width
        size=page.viewport_size;page.set_viewport_size({'width':round(size['width']+wanted-width),'height':1000});settle(page)
    width=page.locator('#managementContent').evaluate('e=>e.getBoundingClientRect().width')
    assert abs(width-wanted)<=visual.EPSILON,('cannot establish required useful width',wanted,width)
    return width


def counterproofs(page,report):
    page.set_viewport_size({'width':1440,'height':1000});settle(page)
    trigger=page.locator('#management [data-mg-action=info]');trigger.scroll_into_view_if_needed();trigger.click()
    close=page.locator('dialog.mg-dialog[open] [data-mg-action=close-dialog]');path=close.locator('svg path')
    visual.centered(close,'ink',True);path.evaluate("e=>e.setAttribute('transform','translate(6 0)')")
    assert path.get_attribute('transform')=='translate(6 0)','SVG mutation must actually be applied'
    record(report,'management-counterproof-svg',lambda:visual.rejected(lambda:visual.centered(close,'ink',True)))
    path.evaluate("e=>e.removeAttribute('transform')");visual.centered(close,'ink',True);page.keyboard.press('Escape')
    button=page.locator('#management [data-mg-action=edit-plan]');button.scroll_into_view_if_needed();original=button.inner_html()
    visual.centered(button);button.evaluate("e=>e.innerHTML='<span style=\"display:inline-block;transform:translateY(6px)\">'+e.innerHTML+'</span>'")
    assert button.locator('span').evaluate('e=>getComputedStyle(e).transform')!='none','Text mutation must actually be applied'
    record(report,'management-counterproof-text',lambda:visual.rejected(lambda:visual.centered(button)))
    button.evaluate('(e,html)=>e.innerHTML=html',original);visual.centered(button)
    table=page.locator('.mg-sheet');style=table.get_attribute('style');table.evaluate("e=>e.style.setProperty('min-width','2500px','important')")
    record(report,'management-counterproof-overflow',lambda:visual.rejected(lambda:geometry(page)))
    table.evaluate('(e,style)=>style===null?e.removeAttribute("style"):e.setAttribute("style",style)',style)
    geometry(page)
    page.locator('#management [data-mg-account]').evaluate('e=>{const copy=e.cloneNode(true);copy.dataset.mgVisualDuplicate="";e.parentElement.append(copy)}')
    record(report,'management-counterproof-duplicate',lambda:visual.rejected(lambda:geometry(page)))
    page.locator('[data-mg-visual-duplicate]').evaluate('e=>e.remove()');geometry(page)


def native_cases(pw,url,report):
    profile=Path(tempfile.mkdtemp(prefix='management-native200-',dir=report['out']))
    (profile/'Default').mkdir();(profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
    options=launch_options();options.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce',timezone_id='UTC')
    try:
        context=pw.chromium.launch_persistent_context(str(profile),**options)
        try:
            page=prepare(context,url);zoom=page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
            assert abs(zoom['outer']/zoom['inner']-2)<.01 and zoom['css']=='1',('Real native200 required; CSS substitution forbidden',zoom)
            report['native_zoom']=zoom
            for layout in LAYOUTS:
                for theme in THEMES:
                    page.evaluate('x=>mountNavigationLayout(x)',layout);page.evaluate('t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme);settle(page)
                    record(report,f'management-native200-{layout}-{theme}',lambda:scenario(page),layout=layout,theme=theme,native_zoom=200)
            assert_fixture_requests(context)
        finally:context.close()
    finally:shutil.rmtree(profile)


def main(out=None,native=True):
    out=Path(out or tempfile.mkdtemp(prefix='jpw-management-visual-'));out.mkdir(parents=True,exist_ok=True)
    before=hashes();report={'out':str(out),'cases':[],'sources_before':before,'native_requested':native,'tolerance_css_px':visual.TOLERANCE,'native_zoom':'NOT_RUN'}
    try:
        with BrowserFixtureServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT))) as server,sync_playwright() as pw:
            threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/index.html'
            browser=pw.chromium.launch(**launch_options())
            try:
                context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',reduced_motion='reduce',timezone_id='UTC');page=prepare(context,url)
                for layout in LAYOUTS:
                    for theme in THEMES:
                        page.evaluate('x=>mountNavigationLayout(x)',layout);page.evaluate('t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme)
                        for width,height in SIZES:
                            page.set_viewport_size({'width':width,'height':height});settle(page)
                            capture=out/f'{layout}-{theme}-{width}x{height}' if layout=='sidebar' and theme=='light' and width in (390,1440) and height!=480 else None
                            record(report,f'management-{layout}-{theme}-{width}x{height}',lambda c=capture:scenario(page,c),layout=layout,theme=theme,viewport=[width,height])
                        for width in (899,900,901):
                            front_width(page,width);record(report,f'management-useful-{layout}-{theme}-{width}',lambda:geometry(page),layout=layout,theme=theme,useful_width=width)
                record(report,'management-draft-cursor-resize',lambda:draft_resize(page))
                counterproofs(page,report);assert_fixture_requests(context);context.close()
            finally:browser.close()
            if native:native_cases(pw,url,report)
        report['coverage']=visual.validate_coverage(report['cases'],required_ids(native))
        report['coverage_counterproofs']=coverage_proofs(report['cases'],required_ids(native))
        report['sources_after']=hashes();report['source_unchanged']=report['sources_after']==before
        if not report['source_unchanged']:raise RuntimeError('ENVIRONMENT_ERROR: source changed concurrently; repeat visual checks on a stable candidate')
        report['classification']='PASS';return 0
    except Exception as error:
        report['classification']='ENVIRONMENT_ERROR' if str(error).startswith('ENVIRONMENT_ERROR:') else 'PRODUCT_FAIL' if isinstance(error,AssertionError) else 'TEST_HARNESS_FAIL';report['error']=str(error);report['traceback']=traceback.format_exc();raise
    finally:
        report['sources_after']=hashes();report['source_unchanged']=report['sources_after']==before
        (out/'management-visual-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);parser.add_argument('--headless-only',action='store_true');args=parser.parse_args()
    main(args.out,native=not args.headless_only)

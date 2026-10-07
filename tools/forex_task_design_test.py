#!/usr/bin/env python3
"""CHG-JPW-FOREX-TASK-DESIGN-20261005-TEST: real DOM, synthetic accounts.
No domain replacements; existing import and record writers seed isolated contexts.
"""
import argparse,json,threading,traceback,hashlib,math,tempfile
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright
from forex_execution_table_test import Server,Quiet,ready,field,set_field
from forex_professional_panel_test import seed,assert_curves,model
from forex_visual_risk_test import risk_seed,financial
from browser_bootstrap_fixture import install_bootstrap
from notes_launcher_test import launch_options,settle
ROOT=Path(__file__).resolve().parents[1]
ROUTES=['forex-consolidated','forex-history','forex-operation','forex-management-accounts','forex-accounting','forex-planning','forex-reserves']
def go(p,route):
 p.evaluate('r=>JPWNavigation.navigate(r)',route);settle(p)
def geometry(p):
 return p.evaluate("""()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,
  tabs:[...document.querySelectorAll('.fxc-tabs button')].filter(e=>e.offsetWidth).map(e=>({text:e.textContent,x:e.getBoundingClientRect().x,right:e.getBoundingClientRect().right})),
  notes:!!document.querySelector('#headerNotesBtn')?.getClientRects().length})""")
def safe(p):
 d=geometry(p);assert d['scroll']<=d['width']+1,d
 assert not d['notes'],'Floating Notes must not cover Forex'
 assert p.locator('#forexNotesToggle').is_visible()
 return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--native-zoom',action='store_true');ap.add_argument('--cases');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 report={'checks':[],'pageErrors':[],'limitations':['Chromium emulated touch; no physical device or screen reader evidence'],'sourceHashes':{}}
 for f in ['index.html','src/styles/app.css','src/js/20-ui/16-operation-history.js','src/js/20-ui/28-fx-consolidated.js','src/js/20-ui/30-execution-board.js']:
  report['sourceHashes'][f]=hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
 server=Server(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(**launch_options())
   c=browser.new_context(service_workers='block',viewport={'width':1440,'height':1000},reduced_motion='reduce');c.add_init_script('window.__onbShown=true');install_bootstrap(c)
   p=c.new_page();p.on('pageerror',lambda e:report['pageErrors'].append(str(e)));p.goto(url);ready(p)
   def check(name,fn):
    if a.cases and name not in a.cases.split(','):return
    try:
     data=fn();report['checks'].append({'name':name,'result':'PASS','evidence':data})
    except Exception as e:
     report['checks'].append({'name':name,'result':'PRODUCT_FAIL','detail':str(e),'trace':traceback.format_exc()});p.screenshot(path=str(a.out/(name.replace('/','-')+'-failure.png')))
    (a.out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
   def overview():
    projected=seed(p);before=financial(p);assert_curves(p,projected)
    assert p.locator('#fxcDismissImportNotice').is_visible();p.locator('#fxcDismissImportNotice').click()
    assert not p.locator('#fxcImportNotice').is_visible()
    assert p.locator('#fxcPrepareAccount').count()==1
    assert p.locator('#fxcIdentity').inner_text().count('Em operação')==1
    assert 'Conta analítica sintética' in p.locator('#fxcIdentity').inner_text()
    assert 'Conta sintética da tabela' in p.locator('#fxcIdentity').inner_text()
    assert financial(p)==before
    p.locator('#fxcTab-statistics').click();settle(p)
    assert p.locator('.fxc-stat-group').count()==3
    bars=p.locator('.fxc-bar-diverging').evaluate_all("""els=>els.map(e=>({text:e.parentElement.textContent,zero:e.querySelector('.fxc-bar-zero')!==null,fill:e.querySelector('i').style.cssText}))""")
    assert bars and all(b['zero'] for b in bars)
    p.screenshot(path=str(a.out/'statistics-1440.png'));p.locator('#fxcTab-account').click()
    return {'bars':bars,'canonicalValuesUnchanged':True}
   check('overview',overview)
   def tools():
    risk_seed(p,10);before=financial(p)
    assert not p.locator('#ebToolsBody').is_visible()
    f=field(p,'id');f.fill('DRAFT-PRESERVED');f.focus();f.evaluate("e=>{e.setSelectionRange(2,7);window.__taskField=e}")
    p.locator('#ebToolsToggle').click();p.locator('[data-eb-tool="rootn"]').click()
    p.locator('#ebToolsToggle').click()
    assert f.input_value()=='DRAFT-PRESERVED';assert f.evaluate('e=>e===window.__taskField')
    p.set_viewport_size({'width':1024,'height':1000});settle(p)
    assert f.evaluate('e=>e===window.__taskField');assert financial(p)==before
    p.locator('#forexNotesToggle').click();settle(p)
    assert p.locator('#mvpNotesOverlay').is_visible();p.locator('#mvpNotesCloseBtn').click();settle(p)
    assert p.evaluate("document.activeElement.id")=='forexNotesToggle'
    assert not p.locator('#headerNotesBtn').is_visible()
    p.locator('[data-eb-cancel-row="0:0"]').click();settle(p)
    return {'financialUnchanged':True,'sameEditor':True}
   check('tools-and-notes',tools)
   # Fixture reset is explicit and separate from presentation assertions.
   seed(p)
   def history():
    go(p,'forex-history');before=financial(p);oper=p.evaluate('JPWForex.state.operationalSelection()')
    p.evaluate("""()=>{S.accounts.push({forexAccountId:'QUERY-B',nome:'Conta de consulta B',tipo:'PROPRIA',currency:'USD'});const r=JPWForex.state.recordAccountPeriod({accountId:'QUERY-B',startedAt:'2026-08-01',currency:'USD',si:1000,openingBook:1000,source:'Synthetic query',activateCurrentPeriod:true},{reason:'Synthetic fixture'});if(!r.ok)throw Error(JSON.stringify(r));JPWForex.state.selectOperationalAccount('TABLE-A');renderOperationHistory();}""")
    before=financial(p);oper=p.evaluate('JPWForex.state.operationalSelection()');opts=p.locator('#histArchiveScope option').evaluate_all('es=>es.map(e=>({value:e.value,text:e.textContent}))')
    value=next(x['value'] for x in opts if x['value'].startswith('QUERY-B|'))
    p.locator('#histArchiveScope').focus();p.evaluate("window.__historyPicker=document.querySelector('#histArchiveScope')")
    p.locator('#histArchiveScope').select_option(value);settle(p)
    assert p.evaluate('JPWForex.state.operationalSelection()')==oper
    assert 'Conta de consulta B' in p.locator('#execHistory').inner_text()
    assert p.locator('#histArchiveScope').evaluate('e=>e===window.__historyPicker')
    go(p,'forex-accounting');go(p,'forex-history')
    assert p.locator('#histArchiveScope').input_value()==value
    p.evaluate("histState.archiveScope='missing|missing';renderOperationHistory()");settle(p)
    assert p.evaluate('histRecords().length')==0
    assert 'indisponível' in p.locator('#execHistory').inner_text().lower()
    assert financial(p)==before
    return {'operationalPreserved':True,'options':opts}
   check('history-query',history)
   def cross_area_keyboard():
    p.set_viewport_size({'width':390,'height':844});p.evaluate("mountNavigationLayout('topbar')");settle(p)
    before=financial(p);results=[]
    for key,expected in [('ArrowDown','forex-consolidated'),('ArrowUp','forex-reserves')]:
     go(p,'research-forex')
     p.locator('[data-shell-menu-toggle]').click();p.locator('#execNavTrigger').focus();p.keyboard.press(key);settle(p)
     assert p.evaluate('JPWNavigation.current().primary')=='forex'
     assert p.locator('#execNavSubmenu').is_visible()
     assert p.evaluate("document.activeElement.dataset.navChild")==expected
     assert not p.locator('#researchNavSubmenu').is_visible()
     p.keyboard.press('Escape');settle(p)
     results.append({'key':key,'focus':expected})
    assert financial(p)==before
    return results
   check('cross-area-keyboard',cross_area_keyboard)
   seed(p);p.locator('#fxcDismissImportNotice').click()
   def matrix():
    before=financial(p);rows=[]
    for layout in ['sidebar','topbar','submenu','glass']:
     p.evaluate('x=>mountNavigationLayout(x)',layout);settle(p)
     for width in [320,390,768,1024,1440]:
      p.set_viewport_size({'width':width,'height':844 if width<900 else 1000})
      for theme in ['light','dark']:
       p.evaluate('t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme)
       for route in ROUTES:
        go(p,route);g=safe(p)
        if route=='forex-consolidated':
         assert all(t['x']>=-1 and t['right']<=width+1 for t in g['tabs']),g
        rows.append({'layout':layout,'width':width,'theme':theme,'route':route,**g})
       go(p,'forex-consolidated')
       if width in [320,390]:
        p.locator('#forexAreasToggle').click();settle(p)
        assert p.locator('#execNavSubmenu [data-forex-nav-group]').count()==3
        assert p.locator('#execNavSubmenu [data-nav-child="forex-history"]').is_visible()
        p.locator('#execNavSubmenu [data-nav-child="forex-history"]').click();settle(p)
        assert p.locator('#execHistory').is_visible()
       if width in [390,1440] and theme=='light':
        go(p,'forex-consolidated');p.evaluate('scrollTo(0,0)');settle(p);p.screenshot(path=str(a.out/f'{layout}-{width}.png'))
    assert financial(p)==before
    return {'visits':len(rows),'geometry':rows,'financialUnchanged':True}
   check('responsive-matrix',matrix)
   c.close();browser.close()
   if a.native_zoom:
    profile=Path(tempfile.mkdtemp(prefix='jpw-design-native200-',dir=a.out))
    (profile/'Default').mkdir();(profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
    opts=launch_options();opts.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
    c=pw.chromium.launch_persistent_context(str(profile),**opts);c.add_init_script('window.__onbShown=true');install_bootstrap(c)
    p=c.pages[0];p.goto(url);ready(p);seed(p)
    def native():
     ratio=p.evaluate('({ratio:outerWidth/innerWidth,zoom:getComputedStyle(document.documentElement).zoom})')
     assert abs(ratio['ratio']-2)<.01 and ratio['zoom']=='1',ratio
     for route in ROUTES:go(p,route);safe(p)
     p.screenshot(path=str(a.out/'native-200.png'))
     return ratio
    check('native-200',native);c.close()
 finally:server.shutdown()
 report['sameBytes']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in report['sourceHashes'].items())
 (a.out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'checks':[{k:v for k,v in x.items() if k not in ['evidence','trace']} for x in report['checks']],'pageErrors':report['pageErrors'],'sameBytes':report['sameBytes']},ensure_ascii=False))
 return 1 if any(x['result']!='PASS' for x in report['checks']) or report['pageErrors'] or not report['sameBytes'] else 0
if __name__=='__main__':raise SystemExit(main())

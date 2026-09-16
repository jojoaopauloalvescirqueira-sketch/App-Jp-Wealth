"""APPLE01 presentation contract; synthetic fixtures and existing bootstrap only."""
import argparse,json,os,threading
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap,assert_fixture_requests
from design_experience_test import Quiet,SETUP,ALLADIN_SEED,settings_geometry_checks
ROOT=Path(__file__).resolve().parents[1]
CONTRAST = r"""selector => {
 const e=document.querySelector(selector); if(!e || !e.getBoundingClientRect().width)return null;
 const rgba=s=>(s.match(/[\d.]+/g)||[]).map(Number);
 const blend=(f,b)=>f.slice(0,3).map((v,i)=>v*(f[3]??1)+b[i]*(1-(f[3]??1)));
 const chain=[];for(let n=e;n;n=n.parentElement)chain.unshift(n);
 let bg=[255,255,255];for(const n of chain)bg=blend(rgba(getComputedStyle(n).backgroundColor),bg);
 const fg=blend(rgba(getComputedStyle(e).color),bg);
 const lum=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
 const a=lum(fg),b=lum(bg);return {ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05),fg,bg};
}"""
"""Completion research focal. Import from the existing Apple runner after official rebuild.
No server, browser, dependency, network fixture or alternate test infrastructure here.
Uses an already bootstrapped synthetic Playwright page; each failed property records
PRODUCT_FAIL through the supplied callback, then raises AssertionError.
"""
import copy
from studies_notes_persistence_contract_test import NC, PV
from nocoda_test import set_datetime


def run_research_focal(page, check, prefix="research"):
    failed = []
    def verify(name, value, detail=None):
        check(prefix + " " + name, bool(value), detail)
        if not value:
            failed.append(name)

    page.evaluate(r"""() => {
      JPWNavigation.navigate('nocoda');
      ncSelectedId=instrumentCatalog()[0].id;
      ncDraft=ncDraftFrom(ncSelectedId);ncDirty=false;renderNocodaStudies();
    }""")
    saved = page.evaluate("JSON.stringify(S)")
    stored = page.evaluate("JSON.stringify(Object.entries(localStorage).sort())")
    examples = [('interpolated', copy.deepcopy(NC)), ('extrapolated', copy.deepcopy(NC)), ('opposite-side', copy.deepcopy(NC))]
    examples[1][1]['anchor3']['datetime'] = '2022-01-04T11:00:00'
    examples[2][1]['anchor3']['price'] = 1.38
    coincident = copy.deepcopy(NC)
    coincident['anchor3']['price'] = page.evaluate("a => JPWNocoda.geometry.levelPrice(0,JPWNocoda.geometry.parseTime(a.anchor3.datetime),a)", NC)
    examples.append(('coincident-lines', coincident))
    for label, anchors in examples:
        for index in range(1, 4):
            anchor = anchors['anchor' + str(index)]
            set_datetime(page, '#ncDate' + str(index), anchor['datetime'])
            page.locator('#ncPrice' + str(index)).fill(str(anchor['price']))
        evidence = page.evaluate(r"""() => {
          const geometry=JPWNocoda.geometry, calls=[], original=geometry.levelPrice;
          const input=document.getElementById('ncPrice3');input.focus();
          geometry.levelPrice=function(level,t,study){calls.push({level,t,sameDraft:study===ncDraft});return original.apply(this,arguments)};
          try {ncUpdateDerived()} finally {geometry.levelPrice=original}
          const v=geometry.validate(ncDraft).values, output=geometry.compute(ncDraft);
          const svg=document.querySelector('#ncPreview svg');
          const lines=svg?[...svg.querySelectorAll('.cp-channel-line')].map(e=>e.getAttribute('d').match(/-?[0-9]+(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?/gi).map(Number)):[];
          const points=svg?[...svg.querySelectorAll('circle')].map(e=>[+e.getAttribute('cx'),+e.getAttribute('cy')]):[];
          const onLine=(point,line)=>Math.abs(point[1]-(line[1]+(point[0]-line[0])/(line[2]-line[0])*(line[3]-line[1])))<1e-6;
          const geometryMatches=points.length===3&&lines.length===2&&onLine(points[0],lines[0])&&onLine(points[1],lines[0])&&onLine(points[2],lines[1]);
          return {calls,expectedTimes:[Math.min(v.t1,v.t2,v.t3),Math.max(v.t1,v.t2,v.t3)],geometryMatches,
            textMatches:document.getElementById('ncRange').textContent===ncFormat(output.channelRange)&&document.getElementById('ncSubdivision').textContent===ncFormat(output.subdivisionRange),
            finite:lines.flat().concat(points.flat()).every(Number.isFinite),
            focusPreserved:document.activeElement===input&&input===document.getElementById('ncPrice3'),
            dirty:ncDirty,caption:document.getElementById('ncPreviewCaption').textContent};
        }""")
        expected = [{'level': level, 't': t, 'sameDraft': True} for level in [0, -1] for t in evidence['expectedTimes']]
        verify(label + ' projects canonical levelPrice without second financial model', evidence['calls'] == expected, evidence['calls'])
        verify(label + ' anchors lie on the displayed canonical lines', evidence['geometryMatches'], evidence)
        verify(label + ' range and subdivision retain canonical outputs', evidence['textMatches'], evidence)
        if label == 'coincident-lines':
            verify('zero channel range remains a valid displayed geometry', page.locator('#ncRange').inner_text() == '0' and page.locator('#ncPreview svg').count() == 1)
        verify(label + ' finite geometry and original input focus', evidence['finite'] and evidence['focusPreserved'], evidence)
        verify(label + ' editing preserves draft and does not confirm save', evidence['dirty'] and page.evaluate('JSON.stringify(S)') == saved)
        verify(label + ' preview never writes preferences or domain storage', page.evaluate('JSON.stringify(Object.entries(localStorage).sort())') == stored)
    page.locator('#ncPrice3').fill('invalid')
    verify('invalid anchor yields no chart rather than fabricated zeros', page.locator('#ncPreview svg').count() == 0 and page.locator('#ncRange').inner_text() == '—')
    verify('invalid anchor remains recoverable in the input', page.locator('#ncPrice3').input_value() == 'invalid' and page.evaluate('ncDirty'))
    verify('invalid preview leaves confirmed memory and storage unchanged', page.evaluate('JSON.stringify(S)') == saved and page.evaluate('JSON.stringify(Object.entries(localStorage).sort())') == stored)

    page.evaluate(r"""p => {
      const instrument=instrumentCatalog()[0].id;
      const second={...p,id:'completion-h1',timeframe:'H1',endPrice:1.1016};
      S.pivotStudies={schemaVersion:1,studies:[{id:'completion-study',instrumentId:instrument,periodStart:'2025-01-01',periodEnd:'2025-12-31',createdAt:'2025-01-01',updatedAt:'2025-01-01',pivots:[p,second]}]};
      pvInstrumentId=instrument;pvStudyId='completion-study';pvNewStudyOpen=false;pvFormOpen=false;pvDirty=false;
      pvFilters={timeframe:'all',direction:'all',criterion:'valid'};
      JPWNavigation.navigate('pivots');
    }""", PV)
    pivots = page.evaluate('JSON.stringify(S.pivotStudies)')
    bars = page.evaluate(r"""() => {
      const stats=pvMath().stats(pvStudyById(pvStudyId).pivots,{scope:pvFilters.criterion});
      return [...document.querySelectorAll('.cp-pv-bar-row')].map((e,i)=>{
        const tf=['H1','H4'][i],s=stats.timeframes[tf];
        return {tf,n:s.n,text:e.innerText,expected:pvFmtPct(s.median),width:parseFloat(e.querySelector('.cp-pv-track>span').style.width)};
      });
    }""")
    verify('Pivots comparison exposes two canonical sample groups', len(bars) == 2 and all(row['expected'] in row['text'] and 'n = ' + str(row['n']) in row['text'] for row in bars), bars)
    verify('Pivots longer median has larger displayed bar', len(bars) == 2 and bars[1]['width'] > bars[0]['width'] > 0, bars)
    page.locator('[data-pv-filter="criterion"][data-pv-value="outside"]').click()
    verify('empty criterion sample says Sem dados rather than zero amplitude', page.locator('.cp-pv-bar-row strong').all_inner_texts() == ['Sem dados', 'Sem dados'])
    verify('Pivots visual comparison and filter never alter records', page.evaluate('JSON.stringify(S.pivotStudies)') == pivots)

    page.evaluate("JPWNavigation.navigate('probability-lab')")
    layout = page.evaluate(r"""() => {
      const roots=document.querySelectorAll('[data-galton-root]'),root=roots[0],canvas=root.querySelector('[data-galton-canvas]');
      const execute=root.querySelector('[data-galton-action="execute"]'),metrics=root.querySelector('.galton-metrics');
      return {roots:roots.length,canvasCount:root.querySelectorAll('canvas').length,
        commandsBeforeCanvas:Boolean(execute.compareDocumentPosition(canvas)&Node.DOCUMENT_POSITION_FOLLOWING),
        canvasBeforeMetrics:Boolean(canvas.compareDocumentPosition(metrics)&Node.DOCUMENT_POSITION_FOLLOWING),
        canvasTop:canvas.getBoundingClientRect().top,viewport:innerHeight};
    }""")
    verify('Lab has one instance and canvas, commands before object and metrics after', layout['roots'] == 1 and layout['canvasCount'] == 1 and layout['commandsBeforeCanvas'] and layout['canvasBeforeMetrics'], layout)
    # No simulation/retry semantics are inferred here; run existing A13 and persistence suites.
    if failed:
        raise AssertionError('Research completion focal failed: ' + '; '.join(failed))


def completion_checks(page, check, prefix):
 # Deliberately new presentation requirements; V2 remains the preserved before.
 page.evaluate("JPWNavigation.navigate('dashboard')")
 check(prefix+' panorama chapters',page.locator('.dm-card').count()==4 and page.locator('.cp-panorama-index a').count()==4)
 check(prefix+' dashboard headers and data fit their chapter',page.evaluate("""() => [...document.querySelectorAll('.dm-card')].every(e=>{const b=e.getBoundingClientRect(),h=e.querySelector('.dm-card-head').getBoundingClientRect(),d=e.querySelector('.dm-body').getBoundingClientRect();return h.width>80&&d.width>b.width*.5&&h.left>=b.left-1&&h.right<=b.right+1&&h.top>=b.top-1&&h.bottom<=b.bottom+1})"""))
 check(prefix+' dashboard symbols stay compact',page.evaluate("() => [...document.querySelectorAll('.cp-area-mark')].every(e=>e.getBoundingClientRect().width<=28)"))
 check(prefix+' original symbols resolve',page.evaluate("() => [...document.querySelectorAll('.cp-area-mark use,#gdNewsMoreBtn use,#gdNewsRefreshBtn use')].every(e=>!!document.querySelector(e.getAttribute('href')))"))
 for route,selector in [('forex-overview','#fxOverviewWidgets .jp-btn-primary'),('alladin','#alladin [data-ald-new="instrument"]'),('ecal','#execEcal .ecal-filters button.on')]:
  page.evaluate('(r)=>JPWNavigation.navigate(r)',route)
  contrast=page.evaluate(CONTRAST,selector)
  check(prefix+' primary or selected action contrast '+route,contrast is not None and contrast['ratio']>=4.5,contrast)
 page.evaluate("JPWNavigation.navigateLocal('finpes','mensal')")
 check(prefix+' PF reading order summary income expense',page.evaluate("() => {const r=document.getElementById('finpesBudgetRoot'),ids=[...r.querySelectorAll('[id]')].map(e=>e.id);return ids.indexOf('fbSummary')<ids.indexOf('fbIncomes')&&ids.indexOf('fbIncomes')<ids.indexOf('fbExpenses')}"))
 page.evaluate("() => {const k=pfCurrentMonthKey(); const r=pfActAddIncome(k,{name:'Receita de contraste sintética',projectedAmount:10000});if(!r||!r.ok)throw Error('PF fixture refused');finpesBudgetRender()}")
 recurring=page.locator('[data-fi-cfg]').first;deleting=page.locator('[data-fi-del]').first
 recurring.hover();neutral=recurring.evaluate('e=>getComputedStyle(e).color')
 deleting.hover();destructive=deleting.evaluate('e=>getComputedStyle(e).color')
 check(prefix+' non-destructive PF hover differs from delete',neutral!=destructive,{'recurrence':neutral,'delete':destructive})
 page.mouse.move(0,0)
 page.evaluate("JPWNavigation.navigate('probability-lab')")
 page.wait_for_selector('[data-galton-canvas]')
 check(prefix+' lab canvas before statistics in DOM',page.evaluate("() => !!(document.querySelector('[data-galton-canvas]').compareDocumentPosition(document.querySelector('.galton-metrics'))&Node.DOCUMENT_POSITION_FOLLOWING)"))
 check(prefix+' lab execute before canvas',page.evaluate("() => !!(document.querySelector('[data-galton-action=execute]').compareDocumentPosition(document.querySelector('[data-galton-canvas]'))&Node.DOCUMENT_POSITION_FOLLOWING)"))
 check(prefix+' one simulation canvas',page.locator('[data-galton-canvas]').count()==1)
 page.evaluate("JPWNavigation.navigate('nocoda')")
 check(prefix+' study figure exists without fabricated data',page.locator('#ncPreview').count()==1 and page.locator('#ncPreviewCaption').count()==1)
 page.evaluate("JPWNavigation.navigate('pivots')")
 check(prefix+' study library and creation remain accessible',page.locator('#pvNewStudyBtn').is_visible())
 page.evaluate("JPWNavigation.navigate('dashboard')")
 page.locator('#headerConfigBtn').click()
 check(prefix+' settings has two semantic grouped lists',page.locator('.cp-settings-collections>section').count()==2)
 check(prefix+' settings preserves five destinations',page.locator('[data-settings-panel=general] [data-nav-to]').count()==5)
 settings_geometry_checks(page,check,prefix+' Settings')
 if page.evaluate('innerWidth')<=760:
  page.locator('#settingsMenu [data-settings-category=general]').click()
  settings_geometry_checks(page,check,prefix+' Settings mobile detail')
 selection=page.evaluate(CONTRAST,'#settingsMenu [aria-current=page]')
 if page.evaluate('innerWidth')>760:
  check(prefix+' settings selected navigation text contrast',selection is not None and selection['ratio']>=4.5,selection)
 check(prefix+' settings grouped destinations share one column',page.evaluate("""() => {
  const groups=[...document.querySelectorAll('[data-settings-panel=general] .settings-nav-list')].map(e=>e.getBoundingClientRect());
  return groups.length===2&&Math.abs(groups[0].x-groups[1].x)<2&&groups[1].y>=groups[0].bottom;
 }"""))
 page.keyboard.press('Escape')
 page.locator('#headerNotesBtn').click()
 check(prefix+' notes keeps collection and writing context',page.locator('.cp-notes-intro').is_visible() and page.locator('#mvpNotesEditorEmpty').count()==1)
 page.keyboard.press('Escape')

def run(a):
 rows=[]
 def check(n,v,detail=None):
  rows.append({'name':n,'result':'PASS' if v else 'PRODUCT_FAIL','detail':detail});print(rows[-1],flush=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(a.root)));threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   b=p.chromium.launch(headless=True,executable_path=os.environ.get('JP_WEALTH_CHROMIUM'))
   for w in a.widths:
    for theme in ['light','dark']:
     c=b.new_context(viewport={'width':w,'height':1000},service_workers='block',reduced_motion='reduce');install_bootstrap(c);c.add_init_script('window.__onbShown=true');page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
     page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page);page.evaluate(SETUP,theme);page.evaluate(ALLADIN_SEED)
     prefix=f'{w}/{theme}'
     for id,label in [('headerNotificationsBtn','Notificações'),('headerConfigBtn','Configurações'),('finalizeSessionBtn','Finalizar sessão')]:
      button=page.locator('#'+id)
      check(prefix+' compact named action '+id,button.locator('.header-action-label').count()==0 and button.get_attribute('title')==label and label.casefold() in (button.get_attribute('aria-label') or '').casefold())
      check(prefix+' icon and touch target '+id,button.evaluate("e=>{const r=e.getBoundingClientRect(),s=e.querySelector('svg[aria-hidden=\"true\"]')?.getBoundingClientRect();return !!s&&r.width===44&&r.height===44&&s.width>=16&&s.width<=18}"))
     check(prefix+' notes leaves header',page.locator('#headerActions #headerNotesBtn').count()==0 and page.locator('#headerActions .header-action').count()==4)
     notes=page.locator('body > #mvpNotesLauncher #headerNotesBtn')
     check(prefix+' floating notes remains named',notes.count()==1 and notes.get_attribute('title')=='Notas' and (notes.get_attribute('aria-label') or '').startswith('Abrir notas'))
     check(prefix+' floating notes icon and touch target',notes.evaluate("e=>{const r=e.getBoundingClientRect();return !!e.querySelector('svg[aria-hidden=\"true\"]')&&r.width>=44&&r.height>=44}"))
     check(prefix+' sidebar icons do not displace labels',page.evaluate("() => [...document.querySelectorAll('#nav .nav-area-icon')].every(e=>e.getBoundingClientRect().width<=24)"))
     for selector in ['.dm-title','.dm-shell-sub','.dm-date','#headerConfigBtn']:
      contrast=page.evaluate(CONTRAST,selector)
      check(prefix+' text contrast '+selector,contrast is not None and contrast['ratio']>=4.5,contrast)
     before=page.evaluate('JSON.stringify(S)')
     for route in ['dashboard','forex-overview','personal-finance','ecal','nocoda','pivots','probability-lab','alladin','dashboard']:
      check(prefix+' destination '+route,page.evaluate('(r)=>JPWNavigation.navigate(r)',route))
      check(prefix+' no page overflow '+route,page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
     check(prefix+' navigation retains domain state',before==page.evaluate('JSON.stringify(S)'))
     completion_checks(page,check,prefix)
     try: run_research_focal(page,check,prefix)
     except Exception as exc:
      rows.append({"name":prefix+" research interrupted","result":"PRODUCT_FAIL" if isinstance(exc,AssertionError) else "TEST_HARNESS_FAIL","detail":str(exc)}); print(rows[-1],flush=True)
     page.locator('#headerConfigBtn').focus();page.keyboard.press('Enter');check(prefix+' settings keyboard opens',page.locator('#settingsModal').is_visible());page.keyboard.press('Escape');page.wait_for_function("document.activeElement.id==='headerConfigBtn'",timeout=2000);check(prefix+' settings returns focus',page.evaluate("document.activeElement.id==='headerConfigBtn'"))
     check(prefix+' no uncaught errors',not errors,errors);assert_fixture_requests(c);c.close()
   b.close()
 finally:server.shutdown()
 result={'base':str(a.root),'checks':rows,'pass':sum(x['result']=='PASS' for x in rows),'fail':sum(x['result']!='PASS' for x in rows)}
 a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2));return 1 if result['fail'] else 0
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);p.add_argument('--widths',type=lambda s:list(map(int,s.split(','))),default=[320,390,768,1024,1440]);raise SystemExit(run(p.parse_args()))

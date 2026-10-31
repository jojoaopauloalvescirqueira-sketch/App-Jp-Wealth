#!/usr/bin/env python3
"""31-Oct approved calendar proportions: red/bold today and compact blue selection.
CLI requires --root explicitly. Fresh synthetic profiles; headless only.
"""
import argparse, functools, hashlib, json, sys, threading, traceback, time
from pathlib import Path
from http.server import SimpleHTTPRequestHandler

TOLERANCE = 2
EPSILON = .25
ROOT = None

MEASURE = '''panel=>{
 const rect=n=>n.getBoundingClientRect().toJSON(),style=n=>{const s=getComputedStyle(n);return {background:s.backgroundColor,color:s.color,opacity:+s.opacity,outline:s.outlineStyle,outlineWidth:parseFloat(s.outlineWidth),outlineColor:s.outlineColor,outlineOffset:parseFloat(s.outlineOffset)}};
 const label=panel.querySelector('.calendar-month-label'),heading=panel.querySelector('.calendar-agenda-heading'),grid=panel.querySelector('.calendar-grid');
 return {label:{text:label.textContent,transform:getComputedStyle(label).textTransform},heading:{text:heading.textContent,transform:getComputedStyle(heading).textTransform},grid:rect(grid),
 cells:[...grid.querySelectorAll('[data-calendar-date]')].map(c=>{const n=c.querySelector('.calendar-day-number'),s=getComputedStyle(n),u=getComputedStyle(n,'::after'),r=document.createRange();r.selectNodeContents(n);return {
 date:c.dataset.calendarDate,current:c.getAttribute('aria-current')==='date',selected:c.getAttribute('aria-selected')==='true',outside:c.classList.contains('calendar-day-outside'),tab:c.tabIndex,
 cell:{...rect(c),...style(c)},number:{...rect(n),...style(n),weight:+s.fontWeight,radius:s.borderRadius,text:rect(r)},
 underline:{content:u.content,width:parseFloat(u.width)||0,height:parseFloat(u.height)||0,bottom:parseFloat(u.bottom)||0,color:u.backgroundColor,opacity:+u.opacity},
 dots:[...c.querySelectorAll('.calendar-economic-dot,.calendar-personal-dot')].map(d=>({kind:d.className,...rect(d),...style(d)}))};})};
}'''

def alpha(color):
    import re
    channels = [float(x) for x in re.findall(r'[\d.]+', color)]
    return channels[3] if len(channels)==4 else 1

def rgb(color):
    import re
    return [float(x) for x in re.findall(r'[\d.]+', color)][:3]

def contrast(a,b):
    def lum(s):
        cs=[c/255 for c in rgb(s)]
        cs=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in cs]
        return sum(c*w for c,w in zip(cs,[.2126,.7152,.0722]))
    x,y=sorted([lum(a),lum(b)])
    return (y+.05)/(x+.05)

def assert_proportions(panel):
    data=panel.evaluate(MEASURE)
    failures=[]
    def check(value,message):
        if not value:failures.append(message)
    check(data['label']['text']=='Outubro de 2026','Month text must be Outubro de 2026')
    check(data['label']['transform']=='none','Month text must not capitalize Portuguese connector')
    check(abs(data['grid']['width']-308)<=EPSILON,'Month grid must remain308px')
    check(len(data['cells']) in (28,35,42),'Month must have complete seven-day weeks')
    check(sum(c['tab']==0 for c in data['cells'])==1,'Single roving tabstop')
    check(sum(c['selected'] for c in data['cells'])==1,'One selected date')
    check(sum(c['current'] for c in data['cells'])==1,'One today date')
    for index,c in enumerate(data['cells']):
        b,n,u=c['cell'],c['number'],c['underline']
        check(abs(b['width']-44)<=EPSILON and abs(b['height']-44)<=EPSILON,'44px outer day target '+c['date'])
        if c['selected']:check(abs(n['width']-32)<=EPSILON and abs(n['height']-32)<=EPSILON,'32px internal selected disk '+c['date'])
        check(abs(n['left']+n['width']/2-b['left']-b['width']/2)<=TOLERANCE,'Disk horizontally centered '+c['date'])
        check(n['top']>=b['top']-EPSILON and n['bottom']<=b['bottom']+EPSILON,'Disk inside day '+c['date'])
        ink=n['text'];check(abs(ink['left']+ink['width']/2-n['left']-n['width']/2)<=TOLERANCE and abs(ink['top']+ink['height']/2-n['top']-n['height']/2)<=TOLERANCE,'Numeral ink centered within2px '+c['date'])
        check(b['opacity']==1,'Outer opacity must not dim selected/outside markers '+c['date'])
        check(alpha(b['background'])==0,'Outer target remains clear; selection lives inside '+c['date'])
        if index%7:check(abs(b['left']-data['cells'][index-1]['cell']['right'])<=EPSILON,'No column gap')
        if c['selected']:
            blue=rgb(n['background'])
            check(alpha(n['background'])>0 and blue[2]>blue[0]+10,'Selected disk remains blue '+c['date'])
            check(n['radius'] in ('50%','16px'),'Selected disk circular '+c['date'])
            check(contrast(n['color'],n['background'])>=4.5,'Selected text contrast>=4.5 '+c['date'])
        if c['current']:
            check(n['weight']>=700,'Today numeral bold')
            check(n['outline']=='none','Today must not use obsolete outline')
            if c['selected']:
                check(all(v>=240 for v in rgb(n['color'])), 'Today selected numeral white')
            else:
                red=rgb(n['color']);check(red[0]>red[1]+10 and red[0]>red[2]+10,'Today numeral red')
        else:check(u['content'] in ('none','normal') or u['width']==0 or u['opacity']==0,'No today decoration on other dates '+c['date'])
        for d in c['dots']:
            check(d['top']>=n['bottom']+1-EPSILON and d['bottom']<=b['bottom']+EPSILON,'Marker below32px disk without collision '+c['date'])
            check(d['width']>0 and d['height']>0 and d['opacity']==1 and alpha(d['background'])>0,'Marker visible '+c['date'])
            check(d['left']>=b['left']-EPSILON and d['right']<=b['right']+EPSILON,'Marker contained '+c['date'])
            if d['kind']=='calendar-economic-dot':
                color=rgb(d['background']);check(color[0]>color[1]+10 and color[0]>color[2]+10,'Economic marker red '+c['date'])
                check(abs(d['left']+d['width']/2-n['left']-n['width']/2)<=TOLERANCE,'Economic marker centered under numeral within2px '+c['date'])
            else:
                color=rgb(d['background']);check(color[2]>color[0]+10 and color[2]>color[1]+10,'Personal marker blue '+c['date'])
        if len(c['dots'])==2:
            a,b=c['dots'];check(a['right']<=b['left'] or b['right']<=a['left'],'Economic/personal markers separate '+c['date'])
            check(a['background']!=b['background'],'Economic/personal markers distinct '+c['date'])
    expected_markers={'2026-10-23':2,'2026-10-24':1,'2026-10-25':1}
    for c in data['cells']:check(len(c['dots'])==expected_markers.get(c['date'],0),'Filtered synthetic marker population '+c['date'])
    selected=next(c['date'] for c in data['cells'] if c['selected'])
    headings={'2026-10-23':'Sexta-feira, 23 de outubro','2026-10-25':'Domingo, 25 de outubro','2026-09-30':'Quarta-feira, 30 de setembro'}
    check(data['heading']['text']==headings[selected] and data['heading']['transform']=='none','Agenda heading sentence case with Portuguese connector preserved')
    if failures:raise AssertionError(json.dumps({'violations':sorted(set(failures)),'measurements':data},ensure_ascii=False))
    return data

def assert_focus(panel):
    from playwright.sync_api import expect
    day=panel.locator('[data-calendar-date="2026-10-23"]');day.focus();day.page.keyboard.press('ArrowRight')
    focus=panel.locator('[data-calendar-date="2026-10-24"]');expect(focus).to_be_focused()
    data=focus.evaluate('e=>({visible:e.matches(":focus-visible"),outline:getComputedStyle(e).outlineStyle,width:parseFloat(getComputedStyle(e).outlineWidth),inner:getComputedStyle(e.querySelector(".calendar-day-number")).outlineStyle,selected:e.getAttribute("aria-selected")})')
    assert data['visible'] and data['outline']!='none' and data['width']>=2 and data['inner']=='none' and data['selected']=='false',('Focus distinct from today/selection',data)
    return data

def journey(page,panel,capture=None):
    from playwright.sync_api import expect
    result={'today_selected':assert_proportions(panel)}
    panel.locator('[data-calendar-date="2026-10-25"]').click()
    result['other_selected']=assert_proportions(panel)
    panel.locator('[data-calendar-date="2026-10-25"]').hover()
    result['selected_hover']=assert_proportions(panel)
    panel.locator('[data-calendar-date="2026-09-30"]').click()
    result['outside_selected']=assert_proportions(panel)
    panel.locator('[data-calendar-date="2026-09-30"]').hover()
    result['outside_selected_hover']=assert_proportions(panel)
    result['focus']=assert_focus(panel)
    panel.locator('[data-calendar-action="today"]').click()
    if capture:panel.screenshot(path=str(capture))
    panel.locator('[data-calendar-action="new"]').click()
    title=panel.locator('[name="title"]');title.fill('SYN proportions unsaved')
    title.evaluate('e=>{e.focus();e.setSelectionRange(4,11)}')
    page.evaluate('JPWCalendar.refresh()')
    expect(title).to_be_focused();expect(title).to_have_value('SYN proportions unsaved')
    assert title.evaluate('e=>[e.selectionStart,e.selectionEnd]')==[4,11],'Draft cursor survives refresh'
    panel.locator('[data-calendar-action="cancel-form"]').click()
    return result

def case(browser,url,out,width,height,layout,theme,counterproofs=False):
    import calendar_visual_quality_test as cv
    from playwright.sync_api import expect
    context=browser.new_context(viewport={'width':width,'height':height},timezone_id='UTC',service_workers='block',reduced_motion='reduce')
    page=None
    try:
        page=cv.prepare_context(context,url)
        page.evaluate('x=>mountNavigationLayout(x)',layout)
        page.evaluate('t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme)
        before=cv.start_probe(page)
        cv.open_calendar(page)
        panel=page.locator('#calendarDialog .calendar-panel')
        prefix=f'{layout}-{theme}-{width}x{height}'
        page.screenshot(path=str(out/(prefix+'-before.png')))
        result={'dialog':journey(page,panel,out/(prefix+'-dialog.png'))}
        # Both surfaces use the actual navigation route and factory.
        page.keyboard.press('Escape');cv.focus_return(page)
        page.evaluate("JPWNavigation.navigate('tools-calendar')")
        work=page.locator('#execEcal>.calendar-panel');expect(work).to_be_visible()
        expect(work.locator('[data-calendar-date="2026-10-23"] .calendar-economic-dot')).to_have_count(1)
        result['workspace']=journey(page,work,out/(prefix+'-workspace.png'))
        assert panel.locator('[data-calendar-date="2026-10-23"]').get_attribute('aria-selected')=='true','Dialog state survives workspace navigation'
        if counterproofs:
            work.locator('[data-calendar-date="2026-10-25"]').click()
            violations={
              'disk44':'.calendar-day[aria-selected=true] .calendar-day-number{width:44px!important;height:44px!important}',
              'today-color':'.calendar-day-today:not([aria-selected=true]) .calendar-day-number{color:blue!important}',
              'today-weight':'.calendar-day-today .calendar-day-number{font-weight:400!important}',
              'today-semibold':'.calendar-day-today .calendar-day-number{font-weight:600!important}',
              'outer-selection':'.calendar-day[aria-selected=true]{background:red!important}',
              'capitalized':'.calendar-month-label{text-transform:capitalize!important}',
              'marker-collision':'.calendar-day-markers{bottom:15px!important}',
              'outside-opacity':'.calendar-day-outside{opacity:.42!important}',
              'contrast':'.calendar-day[aria-selected=true] .calendar-day-number{color:#fff!important;background:#409cff!important}',
            }
            result['counterproofs']={}
            for name,css in violations.items():
                assert_proportions(work)
                style=page.add_style_tag(content=css)
                try:assert_proportions(work)
                except AssertionError as err:result['counterproofs'][name]={'rejected':True,'reason':str(err)[:300]}
                else:raise AssertionError('Same oracle accepted deliberate '+name)
                finally:style.evaluate('e=>e.remove()')
        result['no_writes']=cv.unchanged(page,before)
        from browser_bootstrap_fixture import assert_fixture_requests
        assert_fixture_requests(context)
        assert not page._visual_errors,page._visual_errors
        return result
    except Exception:
        if page:page.screenshot(path=str(out/f'{layout}-{theme}-{width}x{height}-FAIL.png'))
        raise
    finally:context.close()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--matrix',action='store_true')
    args=parser.parse_args()
    global ROOT;ROOT=args.root.resolve()
    assert (ROOT/'tools/calendar_visual_quality_test.py').is_file(),ROOT
    sys.path.insert(0,str(ROOT/'tools'))
    from browser_fixture_server import BrowserFixtureServer
    from dashboard_macro_test import launch_browser
    from playwright.sync_api import sync_playwright
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    args.out.mkdir(parents=True,exist_ok=False)
    files=['src/js/40-app/19-calendar-agenda.js','src/styles/app.css','tools/calendar_visual_quality_test.py','tools/ui_visual_quality_test.py','tools/quality_gate.py','tools/regression-memory.json']
    started=time.perf_counter()
    required=[f'calendar-proportions-{layout}-{theme}-{width}x{height}' for width,height in (((320,700),(390,844),(1440,900),(1440,480)) if args.matrix else ((1440,900),)) for layout in (('sidebar','topbar','glass','submenu') if args.matrix else ('sidebar',)) for theme in (('light','dark') if args.matrix else ('light',))]
    report={'required_case_ids':required,'root':str(ROOT),'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'mode':'headless-only','tolerance_css_px':TOLERANCE,'native200':'NOT_RUN; waiting for agreed native window','full':'NOT_RUN; do not run concurrently','cases':[]}
    server=BrowserFixtureServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}/index.html'
    try:
        with sync_playwright() as pw:
            browser=launch_browser(pw)
            try:
                for width,height in (((320,700),(390,844),(1440,900),(1440,480)) if args.matrix else ((1440,900),)):
                    for layout in (('sidebar','topbar','glass','submenu') if args.matrix else ('sidebar',)):
                        for theme in (('light','dark') if args.matrix else ('light',)):
                            rec={'id':f'calendar-proportions-{layout}-{theme}-{width}x{height}'}
                            try:rec.update(status='PASS',result=case(browser,url,args.out,width,height,layout,theme,counterproofs=True))
                            except AssertionError as error:rec.update(status='PRODUCT_FAIL',error=str(error),trace=traceback.format_exc())
                            except Exception as error:rec.update(status='TEST_HARNESS_FAIL',error=str(error),trace=traceback.format_exc())
                            report['cases'].append(rec);print(rec['id'],rec['status'],flush=True)
            finally:browser.close()
    finally:server.shutdown();server.server_close()
    report['duration_seconds']=time.perf_counter()-started
    report['matrix_complete']=[c['id'] for c in report['cases']]==required
    report['classification']='PASS' if report['matrix_complete'] and all(c['status']=='PASS' for c in report['cases']) else 'PRODUCT_FAIL' if any(c['status']=='PRODUCT_FAIL' for c in report['cases']) else 'TEST_HARNESS_FAIL'
    (args.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'classification':report['classification'],'cases':len(report['cases']),'report':str(args.out/'report.json')}),flush=True)
    return 0 if report['classification']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

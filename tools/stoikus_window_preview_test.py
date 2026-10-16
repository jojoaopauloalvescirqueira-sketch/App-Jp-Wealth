"""Standalone behavioral preview checks; existing Playwright + installed Chrome only."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / 'docs/preview/stoikus-window-controls/index.html').as_uri()

def run():
    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        page = browser.new_page(viewport={'width':1280,'height':900})
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(URL)
        assert page.get_by_text('DADOS FICTÍCIOS', exact=True).is_visible(), 'permanent fictitious badge missing'
        for width in [320,640,1280]:
            for theme in ['light','dark']:
                page.set_viewport_size({'width':width,'height':900})
                page.select_option('#theme',theme)
                for state in ['normal','loading','blocked']:
                    page.select_option('#state',state)
                    for view in ['account','history','nocuda','monitor']:
                        page.select_option('#window-choice',view)
                        assert page.locator('#window').is_visible()
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width,theme,state,view,'document overflow')
                        box=page.locator('#window').bounding_box()
                        assert box['width'] <= width*.85+1, (width,box)
                    page.select_option('#window-choice','account')
                    for section in range(6):
                        page.select_option('#section-choice',str(section)) if width < 481 else page.locator(f'[data-section="{section}"]').click()
                        assert page.locator('#section-title').inner_text()
                        assert page.locator('#content').evaluate('(el)=>el.scrollWidth<=el.clientWidth'), (width,theme,state,section,'content overflow')
                checks.append(f'{width}px/{theme}: states, four windows, six sections, overflow')
        page.set_viewport_size({'width':1280,'height':900})
        page.select_option('#state','normal')
        page.select_option('#window-choice','account')
        page.locator('#minimize').click()
        assert page.locator('#window').is_hidden()
        page.locator('#restore').click()
        assert page.locator('#window').is_visible()
        page.locator('#hud-options-toggle').click()
        page.locator('#full-toggle').click()
        assert page.locator('#hud .metric').count()==7
        page.locator('#hud .metric').last.scroll_into_view_if_needed()
        assert page.locator('#hud .metric').last.is_visible()
        page.locator('#full-toggle').click()
        assert page.locator('#hud .metric').count()==2
        for value in range(0,101,10):
            page.locator('#transparency').fill(str(value))
            page.locator('#transparency').dispatch_event('input')
            assert page.locator('#hud').evaluate('(el)=>getComputedStyle(el).opacity')=='1'
            alpha=page.locator('#hud-background').evaluate('(el)=>getComputedStyle(el).opacity')
            assert abs(float(alpha)-(1-value/100)) < .01
        before=page.locator('#hud').bounding_box()
        handle=page.locator('#hud .drag').bounding_box()
        page.mouse.move(handle['x']+15,handle['y']+15); page.mouse.down(); page.mouse.move(handle['x']+70,handle['y']+50); page.mouse.up()
        after=page.locator('#hud').bounding_box()
        assert after['x'] > before['x']+20
        for target in ['#hud','#window']:
            before=page.locator(target).bounding_box()
            handle=page.locator(target+' .resize').bounding_box()
            page.mouse.move(handle['x']+5,handle['y']+5);page.mouse.down();page.mouse.move(handle['x']+65,handle['y']+35);page.mouse.up()
            bigger=page.locator(target).bounding_box()
            assert bigger['width']>before['width']+20,(target,before,bigger)
            handle=page.locator(target+' .resize').bounding_box()
            page.mouse.move(handle['x']+5,handle['y']+5);page.mouse.down();page.mouse.move(handle['x']-40,handle['y']-15);page.mouse.up()
            assert page.locator(target).bounding_box()['width']<bigger['width']-10
        page.select_option('#window-choice','nocuda')
        page.select_option('#channel','manual')
        assert page.locator('#confirm').is_disabled()
        page.locator('#preview').click(); assert page.locator('#confirm').is_enabled()
        page.locator('#minimize').click();page.locator('#restore').click()
        assert page.locator('#confirm').is_enabled(), 'minimize lost workflow'
        page.locator('#confirm').click()
        assert 'Medidas não verificadas' in page.locator('#flow-status').inner_text()
        page.locator('#cancel').click(); assert page.locator('#confirm').is_disabled()
        page.select_option('#channel','fibo');page.locator('#preview').click();page.locator('#confirm').click()
        for state in ['audit','empty','error']:
            page.select_option('#window-choice','history');page.select_option('#history-state',state)
            assert page.locator('#history-status').inner_text()
        assert not errors, errors
        checks.append('HUD compact/full; 11 transparency steps; drag; grow/shrink HUD+solid window; minimize/restore preserves NoCuda; manual/Fibo preview/confirm/cancel; history audit/empty/error; no JS errors')
        browser.close()
    print(json.dumps({'status':'PASS','checks':checks},ensure_ascii=False,indent=2))
def review_regressions():
    failures=[]
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome',headless=True)
        def case(name,fn):
            page=b.new_page(viewport={'width':1280,'height':900});page.set_default_timeout(2500);page.goto(URL)
            try: fn(page);print('PASS R2 '+name)
            except Exception as e: failures.append(name+': '+str(e).split('\n')[0]);print('FAIL R2 '+failures[-1])
            finally:page.close()
        def sections(page):
            assert page.locator('[data-section]').all_text_contents()==['Visão geral','Posições e stops','Raiz N','Sistema','Ajustes','Histórico Pessoal'], 'six native identities missing'
            page.locator('[data-section="2"]').click()
            assert '7 e 14 dias civis' in page.locator('#content').inner_text()
            for i in [3,4]: assert page.locator(f'#content [data-metric="{i}"]').count()==1
            page.locator('#hud-options-toggle').click()
            page.locator('#full-toggle').click()
            for i in range(7):
                page.locator(f'#hud [data-metric-open="{i}"]').click()
                assert page.locator(f'#content [data-metric="{i}"]').count()==1
                assert page.locator(f'#content [data-action="{50+i}"]').count()==1
            assert page.locator('[data-section="5"]').get_attribute('data-action')=='120'
        def hud(page):
            page.select_option('#window-choice','nocuda');page.select_option('#channel','manual');page.locator('#preview').click()
            page.locator('#hud-minimize').click();assert page.locator('#hud-body').is_hidden();assert page.locator('#hud-restore').is_visible();assert page.locator('#hud-account').is_hidden()
            page.locator('#hud-restore').click();assert page.locator('#hud-body').is_visible();assert page.locator('#confirm').is_enabled()
        def responsive(page):
            grip=page.locator('#window .resize').bounding_box();page.mouse.move(grip['x']+10,grip['y']+10);page.mouse.down();page.mouse.move(grip['x']-450,grip['y']);page.mouse.up()
            assert page.locator('#section-choice').is_visible(), 'selector missing in manually narrow panel'
            assert page.locator('#content .cards').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns').count(' ')==0, 'cards do not stack'
        def availability(page):
            page.select_option('#window-choice','nocuda');page.select_option('#channel','manual');page.locator('#preview').click();page.locator('#confirm').click();page.select_option('#state','blocked')
            assert 'Bloqueado' in page.locator('#flow-status').inner_text(), 'blocked NoCuda still reports confirmed'
            assert page.locator('#content .small-chart').count()==0, 'blocked chart still presented'
            page.select_option('#state','loading');assert 'Carregando' in page.locator('#flow-status').inner_text()
            page.select_option('#window-choice','account');assert '123.456,78' not in page.locator('#content').inner_text(), 'unavailable balance presented'
            page.locator('[data-section="1"]').click();assert '+R$ 1.530,87' not in page.locator('#content').inner_text(), 'unavailable position value presented'
        def bounds(page):
            for target in ['#window','#hud']:
                h=page.locator(target+' .drag').bounding_box();page.mouse.move(h['x']+15,h['y']+15);page.mouse.down();page.mouse.move(1270,1800);page.mouse.up()
                result=page.locator(target).evaluate('(el)=>{let a=el.getBoundingClientRect(),s=document.getElementById("stage").getBoundingClientRect();return a.bottom<=s.bottom+1&&a.right<=s.right+1&&a.left>=s.left-1&&a.top>=s.top-1}')
                assert result, target+' clipped after bottom/corner drag'
                h=page.locator(target+' .resize').bounding_box();page.mouse.move(h['x']+10,h['y']+10);page.mouse.down();page.mouse.move(1280,1800);page.mouse.up()
                assert page.locator(target).evaluate('(el)=>{let a=el.getBoundingClientRect(),s=document.getElementById("stage").getBoundingClientRect();return a.bottom<=s.bottom+1&&a.right<=s.right+1}'), target+' clipped after corner resize'
        def targets(page):
            for el in page.locator('.resize').all():
                r=el.bounding_box();assert r['width']>=36 and r['height']>=36, 'resize target below 36px'
        for name,fn in [('native sections',sections),('independent HUD minimize',hud),('panel width layout',responsive),('unavailable fixtures',availability),('full bounds clamp',bounds),('36px grips',targets)]:case(name,fn)
        b.close()
    assert not failures, '; '.join(failures)
    print('PASS R2: six independent review counterexamples')
def compact_regressions():
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome',headless=True);page=b.new_page(viewport={'width':1280,'height':900});page.goto(URL)
        assert page.locator('#hud-options').is_hidden(), 'options expanded by default'
        before=page.locator('#hud').bounding_box();assert before['height']<=250, ('default HUD too tall',before)
        assert before['width']==280
        for control in page.locator('#hud-header button').all():
            r=control.bounding_box();assert r['width']>=36 and r['height']>=36, ('HUD header target below 36px',r)
        consultation_before=page.locator('#window').is_visible()
        page.locator('#hud-minimize').click();small=page.locator('#hud').bounding_box()
        assert small['height']<before['height']/2 and small['width']<before['width'], ('minimized HUD not a small pill',small)
        assert page.locator('#hud button:visible').count()==1
        assert page.locator('#hud .resize').is_hidden()
        page.locator('#hud-restore').click();assert page.locator('#window').is_visible()==consultation_before
        page.locator('#minimize').click();page.locator('#hud-minimize').click();page.locator('#hud-restore').click()
        assert page.locator('#window').is_hidden(), 'HUD restore reopened consultation'
        page.locator('#hud-options-toggle').click();assert page.locator('#hud-options').is_visible()
        page.locator('#full-toggle').click();assert page.locator('#hud .metric').count()==7
        page.locator('#hud-options-toggle').click();assert page.locator('#hud-options').is_hidden()
        b.close()
    print('PASS R3: compact default; options on demand; one-pill minimize; independent restoration; full mode retained')
if __name__=='__main__':
    import sys
    compact_regressions() if '--round3' in sys.argv else review_regressions() if '--round2' in sys.argv else run()


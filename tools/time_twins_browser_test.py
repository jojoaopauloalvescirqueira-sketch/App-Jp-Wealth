#!/usr/bin/env python3
"""Real Chromium contracts: isolated fixture and integrated application/distributions.
The production changes caught are lifecycle leaks, leaked forecast outcomes, invalid
controlled experiments, false completion, focus replacement and unsafe persistence.
Standalone oracles stay independent of the financial application.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import os
import threading
import traceback
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'tools/.artifacts/time-twins-work'
FILES = [f'src/js/40-app/29-time-twins/{name}.js' for name in
         ('01-simulation','02-missions','03-progress','04-view','05-controller')]
KEY = 'jpwealth_time_twins_v1'

class FixtureServer(ThreadingHTTPServer):
    request_queue_size = 64

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass
    def do_GET(self):
        if self.path == '/':
            data = ('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                    '<link rel="stylesheet" href="/src/styles/app.css"><body style="margin:0;display:block"><div id="host"></div>'
                    + ''.join(f'<script src="/{file}"></script>' for file in FILES)
                    + '<script>window.ctl=window.JPWTimeTwins&&JPWTimeTwins.mount&&JPWTimeTwins.mount(document.getElementById("host"));</script></body></html>').encode()
            mime = 'text/html'
        else:
            path = ROOT / self.path.lstrip('/')
            if not path.is_file() or ROOT not in path.resolve().parents:
                self.send_error(404)
                return
            data = path.read_bytes()
            mime = 'text/css' if path.suffix == '.css' else 'text/javascript'
        self.send_response(200)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.end_headers()
        self.wfile.write(data)


def run():
    server = FixtureServer(('127.0.0.1',0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'
    passed, failed = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'), headless=True)
        def fresh(storage=None, mobile=False, reduced=False, fail_storage=False):
            ctx = browser.new_context(viewport={'width':390 if mobile else 1280,'height':844 if mobile else 900},
                                      reduced_motion='reduce' if reduced else 'no-preference', service_workers='block')
            init = """window.__writes=[];Object.defineProperty(window,'S',{get(){throw Error('Financial S access')}});
              Object.defineProperty(window,'DEFAULTS',{get(){throw Error('Financial DEFAULTS access')}});
              const original=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){window.__writes.push(k);return original.call(this,k,v)};
            """
            if storage is not None:
                init += f'localStorage.setItem({json.dumps(KEY)},{json.dumps(storage)});'
            if fail_storage:
                init += "Object.defineProperty(window,'localStorage',{get(){throw Error('denied')}});"
            ctx.add_init_script(init)
            page = ctx.new_page()
            page.errors = []
            page.failed_requests = []
            page.on('requestfailed', lambda req: page.failed_requests.append((req.url,req.failure)))
            page.on('pageerror', lambda err: page.errors.append(str(err)))
            page.goto(url)
            assert page.evaluate('!!window.ctl'), f'missing real mount/controller: errors={page.errors} network={page.failed_requests}'
            page.evaluate('ctl.activate()')
            return ctx, page
        def snap(p): return p.evaluate('ctl.snapshot()')
        def click(p,a): p.locator(f'[data-action="{a}"]').click()
        def choose(p,k,v): p.locator(f'[data-field="{k}"]').select_option(str(v))
        def fill(p,k,v): p.locator(f'[data-field="{k}"]').fill(str(v))
        def mission(p,id): p.locator(f'[data-mission="{id}"]').click()
        def predict(p,choice='A'):
            choose(p,'prediction',choice)
            click(p,'predict')
        def end(p):
            p.locator('[data-field="month"]').fill(str(p.locator('[data-field="month"]').get_attribute('max')))
            p.locator('[data-field="month"]').dispatch_event('input')
        def reason(p,r): choose(p,'reason',r); click(p,'reason')
        def test(name,fn):
            print('[RUN] '+name, flush=True)
            try:
                fn()
                passed.append(name)
                print('[PASS] '+name, flush=True)
            except Exception:
                failed.append(name)
                print('[FAIL] '+name, flush=True)
                traceback.print_exc()
        def test_mount():
            c,p=fresh()
            assert snap(p)['month']==0 and not snap(p)['running']
            assert p.evaluate('JPWTimeTwins.mount(document.getElementById("host"))===ctl')
            assert p.locator('[data-time-twins-root]').count()==1
            assert p.get_by_role('heading',name='Gêmeos do Tempo',exact=True).is_visible()
            mission(p,'early-start')
            assert p.locator('[data-action="step-next"]').is_disabled()
            assert '4.456' not in p.locator('[data-time-twins-root]').inner_text()
            assert p.locator('[data-output="final-A"]').inner_text()=='Após observar o prazo completo'
            assert p.locator('[data-chart-line="A"]').get_attribute('d').count('L')==0
            click(p,'predict')
            assert snap(p)['prediction'] is None
            assert not snap(p)['running']
            c.close()
        test('mount once, no autoplay and no future disclosed before forecast',test_mount)
        def test_forecast():
            c,p=fresh(); mission(p,'early-start')
            predict(p,'B'); assert snap(p)['prediction']['correct'] is False
            end(p); reason(p,'principal')
            assert p.locator('[data-action="complete"]').is_disabled()
            reason(p,'time'); assert p.locator('[data-action="complete"]').is_disabled()
            click(p,'help'); assert p.locator('[data-action="assisted"]').is_enabled()
            click(p,'assisted')
            assert snap(p)['progress']['missions']['early-start']=='assisted'
            mission(p,'early-start'); predict(p,'A');end(p)
            assert snap(p)['flags']['positiveObserved']
            click(p,'zero');assert snap(p)['prediction'] is None
            predict(p,'equal');end(p);reason(p,'time')
            assert p.locator('[data-action="complete"]').is_enabled()
            click(p,'complete'); assert snap(p)['progress']['missions']['early-start']=='demonstrated'
            mission(p,'early-start');click(p,'help');click(p,'assisted')
            assert snap(p)['progress']['missions']['early-start']=='demonstrated'
            assert all(k==KEY for k in p.evaluate('__writes'))
            c.close()
        test('wrong answers cannot complete; help assisted; positive and zero demonstrated; no demotion',test_forecast)
        def test_controlled():
            c,p=fresh();mission(p,'equal-budget')
            before=snap(p)['draft']['b']['contributions']
            fill(p,'B-start',70)
            after=snap(p)['draft']['b']['contributions']
            assert [d['id'] for d in before]==[d['id'] for d in after]
            assert sum(d['amount'] for d in after)==1200 and len(after)==12
            assert [d['month'] for d in after]==list(range(70,82))
            predict(p);end(p);reason(p,'calendar');click(p,'complete')
            assert snap(p)['progress']['missions']['equal-budget']=='demonstrated'
            mission(p,'early-start');fill(p,'A-deposit',30)
            a=snap(p)['draft']['a'];assert a['initialCapital']==0 and a['contributions'][0]['month']==30 and a['contributions'][0]['amount']==1000
            fill(p,'A-deposit',0);assert snap(p)['draft']['a']['initialCapital']==1000 and not snap(p)['draft']['a']['contributions']
            c.close()
        test('one-variable calendars preserve amounts and stable identities',test_controlled)
        def test_levers():
            c,p=fresh();mission(p,'three-levers')
            for lever,field,value in [('prazo','A-horizon',300),('taxa','A-rate',8),('aporte','A-monthly',150)]:
                choose(p,'lever',lever);fill(p,field,value)
                d=snap(p)['draft']
                if lever=='taxa':assert d['a']['horizonMonths']==240 and d['a']['contributions'][0]['amount']==100
                if lever=='aporte':assert d['a']['annualRate']==.06 and d['a']['horizonMonths']==240
                predict(p);end(p)
                assert snap(p)['flags']['levers'].get(lever)
            reason(p,'lever');assert p.locator('[data-action="complete"]').is_enabled()
            assert 'depositado' in p.locator('[data-output="lever-note"]').inner_text().lower()
            click(p,'complete');assert snap(p)['progress']['missions']['three-levers']=='demonstrated'
            c.close()
        test('three levers restore baseline and require all three observed experiments',test_levers)
        def test_inspect():
            c,p=fresh();mission(p,'contribution-story');predict(p)
            choose(p,'actor','B');choose(p,'cohort','B-month-49')
            assert 'Aporte futuro' in p.locator('[data-output="inspection"]').inner_text()
            assert 'Após observar' in p.locator('[data-output="inspection"]').inner_text()
            end(p)
            click(p,'trace');click(p,'without')
            assert p.locator('[data-output="trace"] tr').count()>100
            assert p.locator('[data-chart-line="without"]').get_attribute('d')
            assert snap(p)['applied']['b']['contributions'][0]['id']=='B-month-49'
            reason(p,'cohort');click(p,'complete')
            assert snap(p)['progress']['missions']['contribution-story']=='demonstrated'
            c.close()
        test('individual future deposit, actual trace and nonmutating without comparison',test_inspect)
        def test_next_cross():
            c,p=fresh();mission(p,'next-contribution');predict(p);end(p)
            reason(p,'extra');assert p.locator('[data-action="complete"]').is_disabled()
            fill(p,'A-extra',2);predict(p);end(p)
            assert 'R$' in p.locator('[data-output="extra-A"]').inner_text()
            assert '%' in p.locator('[data-output="extra-A"]').inner_text()
            assert len(snap(p)['draft']['baselineA']['contributions'])==240
            reason(p,'extra');click(p,'complete')
            assert snap(p)['progress']['missions']['next-contribution']=='demonstrated'
            mission(p,'crossover');predict(p,'late');end(p);click(p,'cross')
            assert '134' in p.locator('[data-output="crossover-A"]').inner_text()
            fill(p,'A-rate',0);predict(p,'never');end(p);click(p,'cross');reason(p,'period')
            assert p.locator('[data-action="complete"]').is_enabled()
            assert 'Não houve' in p.locator('[data-output="crossover-A"]').inner_text()
            assert '-R$' not in p.locator('[data-time-twins-root]').inner_text()
            click(p,'complete');assert snap(p)['progress']['missions']['crossover']=='demonstrated'
            c.close()
        test('extra impact against untouched baseline and causal crossover with changed rate',test_next_cross)
        def test_free():
            c,p=fresh(mobile=True);click(p,'free')
            field=p.locator('[data-field="A-initial"]');field.focus();field.fill('1234.56')
            assert p.evaluate('document.activeElement.dataset.field')=='A-initial'
            assert p.locator('[data-field="A-initial"]').input_value()=='1234.56'
            previous=snap(p)['applied']['a']['initialCapital']
            field.fill('1.234');assert snap(p)['valid'] is False
            assert snap(p)['applied']['a']['initialCapital']==previous
            assert p.locator('[data-action="play"]').is_disabled()
            field.fill('0');fill(p,'A-monthly',0);fill(p,'A-rate',0)
            fill(p,'A-horizon',360);fill(p,'B-horizon',1)
            assert snap(p)['valid'];end(p)
            assert snap(p)['month']==360
            assert 'prazo encerrado' in p.locator('[data-output="status-B"]').inner_text()
            assert 'sem base' in p.locator('[data-output="inspection"]').inner_text()
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
            p.screenshot(path=str(ARTIFACTS/'task-2-mobile.png'),full_page=True)
            click(p,'journey');assert snap(p)['mode']=='home'
            assert not p.errors,p.errors
            c.close()
        test('free inputs refuse fractional cents, preserve focus, 360 and separate horizons at 390px',test_free)
        def test_lifecycle():
            c,p=fresh();click(p,'free');click(p,'play');p.wait_for_timeout(160)
            assert snap(p)['month']>0 and snap(p)['running']
            p.evaluate('ctl.deactivate()');m=snap(p)['month'];p.wait_for_timeout(160)
            assert snap(p)['month']==m and not snap(p)['running']
            p.evaluate('ctl.activate()');assert not snap(p)['running']
            click(p,'play');p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
            assert not snap(p)['running']
            p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'))")
            assert not snap(p)['running']
            click(p,'play');p.evaluate('ctl.pause()');m=snap(p)['month'];p.wait_for_timeout(100);assert snap(p)['month']==m
            p.evaluate('JPWTimeTwins.dispose();ctl.activate();ctl.pause();ctl.destroy()');p.wait_for_timeout(100)
            assert p.locator('[data-time-twins-root]').count()==0
            assert not snap(p)['running'] and snap(p)['destroyed']
            p.evaluate('ctl=JPWTimeTwins.mount(document.getElementById("host"));ctl.activate()')
            assert not snap(p)['running']
            c.close()
        test('playback pauses on lifecycle, hidden and dispose; stale controllers cannot reactivate',test_lifecycle)
        def test_storage():
            c,p=fresh();mission(p,'early-start');click(p,'skip')
            raw=p.evaluate(f'localStorage.getItem({json.dumps(KEY)})');assert json.loads(raw)['missions']['early-start']=='skipped'
            p.reload();assert snap(p)['progress']['missions']['early-start']=='skipped'
            p.evaluate('ctl.activate()');click(p,'restart');click(p,'cancel-restart')
            assert snap(p)['progress']['missions']['early-start']=='skipped'
            click(p,'restart');click(p,'confirm-restart');assert snap(p)['progress']['missions']=={}
            mission(p,'equal-budget');predict(p);p.evaluate(f'localStorage.setItem({json.dumps(KEY)},JSON.stringify({{schemaVersion:1,currentMissionId:"crossover",missions:{{}}}}));window.dispatchEvent(new StorageEvent("storage",{{key:{json.dumps(KEY)}}}))')
            assert snap(p)['prediction'] is None and snap(p)['conflict']
            click(p,'help');click(p,'assisted');assert snap(p)['conflict']
            click(p,'reload');assert not snap(p)['conflict'] and snap(p)['progress']['currentMissionId']=='crossover'
            c.close()
        test('checkpoint reload, explicit restart confirmation and cross-tab conflict blocks writes',test_storage)
        def test_bad_storage():
            c,p=fresh(storage='{"schemaVersion":999}');click(p,'start');click(p,'help');click(p,'assisted')
            assert p.evaluate(f'localStorage.getItem({json.dumps(KEY)})')=='{"schemaVersion":999}'
            click(p,'restart');click(p,'confirm-restart')
            assert json.loads(p.evaluate(f'localStorage.getItem({json.dumps(KEY)})'))['schemaVersion']==1
            c.close()
            c,p=fresh(fail_storage=True);click(p,'start');click(p,'help');click(p,'assisted')
            assert snap(p)['progress']['missions']['early-start']=='assisted'
            assert 'temporário' in p.locator('[data-output="storage"]').inner_text()
            assert not p.errors,p.errors
            c.close()
        test('incompatible bytes preserved until restart; throwing localStorage permits temporary RAM',test_bad_storage)
        def test_keyboard_reduced():
            c,p=fresh(mobile=True,reduced=True);click(p,'free')
            p.locator('[data-action="step-next"]').focus();p.keyboard.press('Enter');assert snap(p)['month']==1
            click(p,'play');p.wait_for_timeout(100);assert snap(p)['month']==1 and not snap(p)['running']
            assert 'reduzido' in p.locator('[data-output="feedback"]').inner_text()
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert p.locator('svg[role="img"]').count()==1
            assert p.locator('[data-output="totals"] th').count()>=3
            c.close()
        test('keyboard stepping and reduced motion retain usable numeric alternatives',test_keyboard_reduced)
        def test_substantive():
            c,p=fresh();mission(p,'three-levers')
            fill(p,'A-horizon',240);predict(p,'equal');end(p)
            assert not snap(p)['flags']['levers'].get('prazo'), 'typing the baseline is not an intervention'
            mission(p,'equal-budget');fill(p,'A-start',1);predict(p);end(p)
            assert not snap(p)['flags']['calendarObserved']
            mission(p,'next-contribution');fill(p,'A-extra',1);predict(p);end(p)
            assert not snap(p)['flags']['dateChanged']
            mission(p,'crossover');fill(p,'A-rate',6);predict(p,'late');end(p)
            assert not snap(p)['flags']['rateChanged']
            c.close()
        test('baseline re-entry never earns a substantive intervention',test_substantive)
        def test_causal_variants():
            c,p=fresh();mission(p,'early-start');fill(p,'A-deposit',120);fill(p,'B-deposit',0)
            predict(p,'B');end(p)
            assert snap(p)['prediction']['correct']
            label=p.locator('[data-field="reason"] option[value="time"]').inner_text()
            assert 'A rende' not in label and 'cada aporte' in label
            reason(p,'time');click(p,'zero');predict(p,'equal');end(p)
            label=p.locator('[data-field="reason"] option[value="time"]').inner_text()
            assert 'Sem rendimentos' in label
            reason(p,'time');assert p.locator('[data-action="complete"]').is_enabled()
            mission(p,'equal-budget');fill(p,'B-start',1);predict(p,'equal');end(p);reason(p,'calendar')
            assert snap(p)['prediction']['correct'] and snap(p)['reasonCorrect']
            assert 'calendários iguais' in p.locator('[data-output="reason-feedback"]').inner_text()
            c.close()
        test('causal explanation agrees with zero rate, inverse and equal calendars',test_causal_variants)
        def test_inactive_live():
            c,p=fresh();mission(p,'early-start')
            p.evaluate('ctl.deactivate();document.querySelector("[data-action=help]").click();document.querySelector("[data-action=assisted]").click()')
            assert snap(p)['progress']['missions']=={}, 'inactive handlers must not complete or write'
            p.evaluate('ctl.activate()');click(p,'journey');click(p,'free')
            p.evaluate('window.feedbackMutations=0;new MutationObserver(r=>window.feedbackMutations+=r.length).observe(document.querySelector("[data-output=feedback]"),{childList:true,subtree:true,characterData:true})')
            click(p,'play');p.wait_for_timeout(300);click(p,'play')
            assert p.evaluate('feedbackMutations')<=1, 'feedback is not rewritten every animation frame'
            c.close()
        test('inactive DOM handlers cannot save and live region does not churn during animation',test_inactive_live)
        def test_focus_trace():
            c,p=fresh();mission(p,'contribution-story');predict(p);end(p)
            assert not snap(p)['flags']['inspect']
            click(p,'trace');click(p,'without')
            assert not snap(p)['flags']['inspect'], 'opening formula alone does not select an individual'
            choose(p,'cohort','A-month-2');click(p,'trace');click(p,'without')
            assert snap(p)['flags']['inspect']
            p.evaluate('document.querySelector("[data-section=trace]").scrollTop=200')
            scrolled=p.locator('[data-section="trace"]').evaluate('(e)=>e.scrollTop')
            p.locator('[data-field="cohort"]').focus();p.keyboard.press('ArrowDown')
            assert p.evaluate('document.activeElement.dataset.field')=='cohort'
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
            c.close()
        test('story requires actual individual selection and keyboard focus is preserved',test_focus_trace)
        def test_themes():
            c,p=fresh();mission(p,'three-levers');fill(p,'A-horizon',360);predict(p);end(p)
            assert p.locator('[data-time-twins-root]').bounding_box()['width'] >= 900, 'desktop fixture must allocate actual Tools-like width'
            p.evaluate('scrollTo(0,0)')
            hero=p.locator('.time-twins-header')
            eyebrow=hero.locator('p').first.bounding_box();title=hero.locator('h2').bounding_box();intro=hero.locator('p').last.bounding_box()
            assert title['y']>=eyebrow['y']+eyebrow['height'], 'header title must follow the eyebrow without overlap'
            assert intro['y']>=title['y']+title['height'], 'header introduction must follow its title without overlap'
            assert hero.bounding_box()['height']>100, 'educational header needs natural height, not the application toolbar height'

            for theme in ['light','dark']:
                p.evaluate('(t)=>document.documentElement.dataset.theme=t',theme)
                assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
                colors=p.evaluate(r"""() => {
                  const luminance = (value) => {
                    const nums=value.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);
                    return .2126*nums[0]+.7152*nums[1]+.0722*nums[2];
                  };
                  const bg=luminance(getComputedStyle(document.querySelector('[aria-label="Linha do tempo"]')).backgroundColor);
                  return ['A','B'].map(actor=>{const line=document.querySelector('[data-chart-line="'+actor+'"]');const l=luminance(getComputedStyle(line).stroke);return (Math.max(l,bg)+.05)/(Math.min(l,bg)+.05)});
                }""")
                assert min(colors)>=3, f'{theme} chart line contrast {colors}'
                p.screenshot(path=str(ARTIFACTS/f'task-2-desktop-{theme}.png'),full_page=True)
            c.close()
        test('desktop inherited light/dark themes retain legible chart lines',test_themes)
        def test_actual_storage():
            initial=json.dumps({'schemaVersion':1,'currentMissionId':'early-start','missions':{}})
            c,p=fresh(storage=initial);click(p,'free');click(p,'play')
            other=c.new_page();other.goto(url);other.evaluate('ctl.activate()')
            click(other,'start');click(other,'help');click(other,'assisted')
            p.wait_for_function('ctl.snapshot().conflict')
            assert not snap(p)['running']
            external=p.evaluate(f'localStorage.getItem({json.dumps(KEY)})')
            click(p,'journey');mission(p,'early-start');click(p,'help');click(p,'assisted')
            assert p.evaluate(f'localStorage.getItem({json.dumps(KEY)})')==external
            click(p,'reload');assert snap(p)['progress']['missions']['early-start']=='assisted'
            c.close()
            c,p=fresh(storage=initial)
            p.evaluate("""() => {localStorage.setItem('foreign-protected','original');const save=Storage.prototype.setItem;
              Storage.prototype.setItem=function(k,v){if(k==='jpwealth_time_twins_v1')throw new DOMException('quota','QuotaExceededError');return save.call(this,k,v)}}""")
            mission(p,'early-start');click(p,'help');click(p,'assisted')
            assert snap(p)['progress']['missions']['early-start']=='assisted'
            assert p.evaluate(f'localStorage.getItem({json.dumps(KEY)})')==initial
            assert p.evaluate('localStorage.getItem("foreign-protected")')=='original'
            assert 'temporário' in p.locator('[data-output="storage"]').inner_text()
            c.close()
        test('real second tab conflict and quota failure preserve existing and foreign bytes',test_actual_storage)
        def test_dynamic_motion():
            c,p=fresh();click(p,'free');click(p,'play');p.wait_for_timeout(100)
            p.emulate_media(reduced_motion='reduce');p.wait_for_timeout(120)
            assert not snap(p)['running'], 'new reduced motion preference must stop the active loop'
            m=snap(p)['month'];p.wait_for_timeout(120);assert snap(p)['month']==m
            click(p,'step-next');assert snap(p)['month']==m+1
            c.close()
        test('changing reduced-motion preference pauses an existing animation',test_dynamic_motion)
        def test_trace_freshness():
            c,p=fresh();click(p,'free');click(p,'trace')
            assert '1.000,00' in p.locator('[data-output="trace"] tbody tr').first.inner_text()
            fill(p,'A-initial',2000);click(p,'trace')
            assert '2.000,00' in p.locator('[data-output="trace"] tbody tr').first.inner_text(), 'trace must use the current principal after parameters change'
            c.close()
        test('formula trace refreshes after a principal-only edit',test_trace_freshness)
        def test_cross_rate_attempt():
            c,p=fresh();mission(p,'crossover');predict(p,'late');end(p);click(p,'cross')
            assert snap(p)['flags']['crossInspected']
            fill(p,'A-rate',0)
            assert not snap(p)['flags']['crossInspected'], 'rate edit invalidates the old investigation'
            predict(p,'never');end(p);reason(p,'period')
            assert p.locator('[data-action="complete"]').is_disabled(), 'new absence must be investigated explicitly'
            click(p,'cross');assert p.locator('[data-action="complete"]').is_enabled()
            c.close()
        test('T2-R1 rate edit requires investigation of the newly observed result',test_cross_rate_attempt)
        def test_cross_actor_attempt():
            c,p=fresh();mission(p,'crossover');fill(p,'A-rate',0);predict(p,'never');end(p);click(p,'cross');reason(p,'period')
            assert p.locator('[data-action="complete"]').is_enabled()
            choose(p,'actor','B')
            assert snap(p)['prediction'] is None
            assert not snap(p)['flags']['crossInspected'], 'actor change invalidates the old investigation'
            predict(p,'late');end(p);reason(p,'period')
            assert p.locator('[data-action="complete"]').is_disabled(), 'the selected actor needs its own investigation'
            click(p,'cross');assert p.locator('[data-action="complete"]').is_enabled()
            c.close()
        test('T2-R1 actor change requires investigation of the selected twin',test_cross_actor_attempt)
        def test_expired_flows():
            c,p=fresh();click(p,'free');fill(p,'A-horizon',360)
            slider=p.locator('[data-field="month"]')
            slider.fill('240');slider.dispatch_event('input')
            balance=p.locator('[data-output="balance-B"]').inner_text()
            assert '234,70' in p.locator('[data-output="interest-B"]').inner_text()
            assert '100,00' in p.locator('[data-output="contribution-B"]').inner_text()
            for month in ['241','360']:
                slider.fill(month);slider.dispatch_event('input')
                assert p.locator('[data-output="balance-B"]').inner_text()==balance
                for metric in ['interest-B','contribution-B']:
                    text=p.locator(f'[data-output="{metric}"]').inner_text()
                    assert '0,00' in text and 'prazo encerrado' in text, 'expired flows must not pretend to be current-month cash flows'
                assert '25.000,00' in p.locator('[data-output="contributed-B"]').inner_text()
            slider.fill('240');slider.dispatch_event('input')
            assert '234,70' in p.locator('[data-output="interest-B"]').inner_text()
            assert 'prazo encerrado' not in p.locator('[data-output="interest-B"]').inner_text()
            c.close()
        test('T2-R2 ended horizon preserves stocks but has no current-month flow',test_expired_flows)
        def test_rate_buttons_validation():
            for actor in ['A','B']:
                for button in ['zero','positive']:
                    c,p=fresh();mission(p,'early-start');fill(p,f'{actor}-deposit',-1)
                    before=snap(p)['applied']
                    assert not snap(p)['valid']
                    click(p,button)
                    assert not snap(p)['valid'], 'rate buttons must not override an invalid calendar'
                    assert p.locator(f'[data-field="{actor}-deposit"]').input_value()=='-1'
                    assert not p.locator(f'[data-field="{actor}-deposit"]').evaluate('(e)=>e.checkValidity()')
                    assert snap(p)['applied']==before
                    assert p.locator('[data-action="predict"]').is_disabled()
                    assert p.locator('[data-action="play"]').is_disabled()
                    assert p.locator('[data-action="step-next"]').is_disabled()
                    assert p.locator('[data-output="validation"]').inner_text()
                    fill(p,f'{actor}-deposit',30);click(p,button)
                    assert snap(p)['valid']
                    assert p.locator(f'[data-field="{actor}-deposit"]').input_value()=='30'
                    applied=snap(p)['applied'][actor.lower()]
                    assert applied['initialCapital']==0 and applied['contributions'][0]['month']==30
                    assert applied['annualRate']==(0 if button=='zero' else .06)
                    assert not p.errors,p.errors
                    c.close()
        test('T2-R3 both rate-repeat controls honor invalid A and B calendars',test_rate_buttons_validation)
        def test_literal_characters():
            c,p=fresh(mobile=True)
            for actor in ['A','B']:
                character=p.locator(f'[data-twin-character="{actor}"]')
                assert character.count()==1 and character.is_visible(), 'each twin needs a represented character'
                assert character.get_by_text('Gêmeo '+actor,exact=True).is_visible()
                assert character.locator('svg').count()==1
                assert character.locator('svg').evaluate('(e)=>e.getBoundingClientRect().width')>=48
            assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
            click(p,'start')
            assert p.get_by_role('group',name='Gêmeo A',exact=True).count()==1
            assert p.get_by_role('group',name='Gêmeo B',exact=True).count()==1
            c.close()
        test('T2-R4 two own characters have literal textual twin identities at 390px',test_literal_characters)
        def viewport_entry(p,obstruction=0,host_bottom=None):
            title=p.locator('[data-output="title"]')
            assert title.evaluate('(e)=>e===document.activeElement'), 'exercise title must retain focus'
            control=p.locator('[aria-label="Preparar experimento"]').locator('input:not(:disabled),select:not(:disabled)').first
            heading=title.bounding_box();box=control.bounding_box();limit=host_bottom or p.viewport_size['height']
            assert heading['y']>=obstruction and heading['y']+heading['height']<=limit, ('heading outside usable viewport',heading)
            assert box['y']>=obstruction and box['y']+box['height']<=limit, ('first preparation control outside usable viewport',box)
        def test_entry_alignment():
            for mobile in [False,True]:
                c,p=fresh(mobile=mobile,reduced=mobile)
                click(p,'start');viewport_entry(p)
                mission(p,'equal-budget');viewport_entry(p)
                click(p,'previous');viewport_entry(p)
                click(p,'next');viewport_entry(p)
                click(p,'journey');click(p,'free');viewport_entry(p)
                p.screenshot(path=str(ARTIFACTS/('task-2-refinement-entry-mobile.png' if mobile else 'task-2-refinement-entry-desktop.png')))
                c.close()
        test('C1 explicit entry and mission navigation show heading and first action on desktop/mobile',test_entry_alignment)
        def test_entry_scroll_host():
            for mobile in [False,True]:
                c,p=fresh(mobile=mobile)
                p.evaluate("""() => {
                  const bar=document.createElement('header');bar.dataset.fixtureHeader='true';bar.textContent='Application header';
                  bar.style.cssText='position:fixed;top:0;left:0;width:100%;height:64px;z-index:9999;display:block';document.body.prepend(bar);
                  const host=document.getElementById('host');host.style.cssText='height:'+Math.min(720,innerHeight-80)+'px;overflow-y:auto;margin-top:64px';
                  const local=document.createElement('div');local.textContent='Scroll host header';local.style.cssText='position:sticky;top:0;height:48px;background:white;z-index:3';host.prepend(local);
                }""")
                click(p,'start')
                bounds=p.locator('#host').bounding_box()
                viewport_entry(p,bounds['y']+48,min(p.viewport_size['height'],bounds['y']+bounds['height']))
                assert p.locator('#host').evaluate('(e)=>e.scrollTop')>0, 'entry must scroll the actual overflowing host'
                c.close()
        test('C1 entry respects an actual scroll host and a visible sticky application header',test_entry_scroll_host)
        def test_entry_no_jumps():
            for mobile in [False,True]:
                c,p=fresh(mobile=mobile);click(p,'start')
                el=p.locator('[data-field="A-deposit"]');el.focus()
                p.evaluate('window.__editingInput=document.activeElement')
                before=p.evaluate('scrollY');el.fill('30')
                assert p.evaluate('document.activeElement===window.__editingInput')
                assert p.evaluate('scrollY')==before, 'typing must not realign the exercise'
                p.evaluate('ctl.activate()')
                assert p.evaluate('document.activeElement===window.__editingInput')
                assert p.evaluate('scrollY')==before, 'activation must not realign the exercise'
                predict(p);click(p,'play');p.wait_for_timeout(120)
                running_scroll=p.evaluate('scrollY');p.wait_for_timeout(120)
                assert p.evaluate('scrollY')==running_scroll, 'animation ticks must not relocate the viewport'
                p.evaluate('ctl.pause()')
                assert p.evaluate('scrollY')==running_scroll
                c.close()
        test('C1 typing activation and animation preserve input identity focus and viewport',test_entry_no_jumps)
        def test_end_next_step_copy():
            c,p=fresh();click(p,'start');predict(p)
            assert 'Use +1 mês' in p.locator('[data-output="feedback"]').inner_text()
            assert p.locator('[data-action="step-next"]').is_enabled()
            end(p)
            text=p.locator('[data-output="feedback"]').inner_text().lower()
            assert 'investig' in text and 'explica' in text, 'finished timeline must point to investigation and explanation'
            assert 'executar' not in text and '+1 mês' not in text and '+12 meses' not in text
            for a in ['step-next','step-year','play']:assert p.locator(f'[data-action="{a}"]').is_disabled()
            flags=snap(p)['flags'];p.evaluate('ctl.pause();ctl.activate()')
            assert snap(p)['flags']==flags, 'bounded copy must not change attempt evidence'
            click(p,'journey');click(p,'free');end(p)
            text=p.locator('[data-output="feedback"]').inner_text().lower()
            assert 'investig' in text and 'executar' not in text
            c.close()
        test('C1 horizon completion points to existing investigation actions instead of disabled advance',test_end_next_step_copy)
        def test_specific_feedback_after_horizon():
            for rate,choice in [(6,'late'),(0,'never')]:
                c,p=fresh();mission(p,'crossover')
                if rate==0:fill(p,'A-rate',0)
                predict(p,choice);end(p)
                generic=p.locator('[data-output="feedback"]').inner_text()
                assert 'Prazo observado.' in generic and 'Investigue' in generic
                before=snap(p);click(p,'cross');after=snap(p)
                shown=p.locator('[data-output="feedback"]').inner_text()
                assert shown==after['feedback'] and shown!=generic, 'final guidance must preserve the investigation response'
                assert 'rendimento e aporte do mesmo mês' in shown
                assert 'não implica independência financeira' in shown
                expected='134' if rate==6 else 'Não houve cruzamento'
                assert expected in p.locator('[data-output="crossover-A"]').inner_text()
                assert after['flags']['crossInspected']
                previous_flags=dict(before['flags']);next_flags=dict(after['flags'])
                previous_flags.pop('crossInspected');next_flags.pop('crossInspected')
                assert next_flags==previous_flags and after['progress']==before['progress']
                for a in ['step-next','step-year','play']:assert p.locator(f'[data-action="{a}"]').is_disabled()
                p.evaluate('ctl.pause();ctl.activate()')
                assert p.locator('[data-output="feedback"]').inner_text()==shown
                p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
                warning=p.locator('[data-output="feedback"]').inner_text()
                assert warning==snap(p)['feedback'] and 'Pausado ao ocultar' in warning, 'end guidance must preserve current warnings too'
                c.close()
        test('T2-P1 final guidance preserves specific crossover feedback and visibility warnings',test_specific_feedback_after_horizon)
        def test_help_completion_cap():
            c,p=fresh();mission(p,'early-start');click(p,'help')
            predict(p,'B');end(p);reason(p,'principal')
            assert p.locator('[data-action="complete"]').is_disabled()
            reason(p,'time');assert p.locator('[data-action="complete"]').is_disabled()
            predict(p,'A');end(p);click(p,'zero');predict(p,'equal');end(p);reason(p,'time')
            assert snap(p)['helped'] and p.locator('[data-action="complete"]').is_enabled()
            click(p,'complete')
            assert snap(p)['progress']['missions']['early-start']=='assisted', 'a helped exercise cannot store demonstrated through the completion button'
            raw=json.loads(p.evaluate(f'localStorage.getItem({json.dumps(KEY)})'))
            assert raw['missions']['early-start']=='assisted'
            mission(p,'early-start');click(p,'skip')
            assert snap(p)['progress']['missions']['early-start']=='assisted', 'skipping cannot demote assisted evidence'
            c.close()
        test('WFR-01 help caps completion after correct retry and both observations at assisted',test_help_completion_cap)
        def test_help_fresh_retry_history():
            c,p=fresh();mission(p,'early-start');click(p,'help')
            assert 'explicação' in p.locator('[data-action="complete"]').inner_text().lower(), 'completion label must disclose assistance'
            click(p,'repeat');assert not snap(p)['helped']
            predict(p,'A');end(p);click(p,'zero');predict(p,'equal');end(p);reason(p,'time');click(p,'complete')
            assert snap(p)['progress']['missions']['early-start']=='demonstrated'
            mission(p,'early-start');click(p,'help');predict(p,'A');end(p);click(p,'zero');predict(p,'equal');end(p);reason(p,'time')
            assert 'explicação' in p.locator('[data-action="complete"]').inner_text().lower()
            click(p,'complete');assert snap(p)['progress']['missions']['early-start']=='demonstrated', 'later help must preserve a historical demonstration'
            c.close()
        test('WFR-01 truthful assistance label, fresh repeat and historical no-demotion',test_help_fresh_retry_history)
        def test_extra_equal_cause():
            c,p=fresh();mission(p,'next-contribution');predict(p,'A');end(p)
            baselines={k:snap(p)['applied'][k] for k in ['baselineA','baselineB']}
            fill(p,'A-extra',120);predict(p,'equal');end(p)
            assert snap(p)['prediction']['correct']
            for actor in ['A','B']:
                impact=p.locator(f'[data-output="extra-{actor}"]').inner_text()
                assert '179,08' in impact and '0,37' in impact
            option=p.locator('[data-field="reason"] option[value="extra"]').inner_text().lower()
            assert ('mesma data' in option or 'mesmo mês' in option) and 'iguais' in option, 'equal dates must not be explained as one extra starting earlier and yielding more'
            reason(p,'share');assert not snap(p)['reasonCorrect'] and p.locator('[data-action="complete"]').is_disabled()
            reason(p,'extra');feedback=p.locator('[data-output="reason-feedback"]').inner_text().lower()
            assert 'iguais' in feedback and 'saldo original' in feedback
            assert all(snap(p)['applied'][k]==baselines[k] for k in baselines)
            click(p,'complete');assert snap(p)['progress']['missions']['next-contribution']=='demonstrated'
            c.close()
        test('WFR-02 equal extra dates use a truthful causal choice and unchanged original denominator',test_extra_equal_cause)
        def test_extra_reversed_cause():
            c,p=fresh();mission(p,'next-contribution');predict(p,'A');end(p)
            fill(p,'A-extra',240);predict(p,'B');end(p)
            assert snap(p)['prediction']['correct']
            option=p.locator('[data-field="reason"] option[value="extra"]').inner_text()
            assert 'Gêmeo B' in option and '120' in option and '240' in option, 'the confirmed reversed calendar must identify B as the earlier extra'
            assert '100,00' in p.locator('[data-output="extra-A"]').inner_text()
            assert '179,08' in p.locator('[data-output="extra-B"]').inner_text()
            reason(p,'extra');feedback=p.locator('[data-output="reason-feedback"]').inner_text()
            assert 'Gêmeo B' in feedback and 'saldo original' in feedback
            click(p,'complete');assert snap(p)['progress']['missions']['next-contribution']=='demonstrated'
            c.close()
        test('WFR-02 reversed extra dates explain the actual earlier twin and marginal impact',test_extra_reversed_cause)
        browser.close()
    server.shutdown()
    result={'suite':'time_twins_browser_standalone','passed':len(passed),'failed':len(failed),'failures':failed}
    print('JPW_TEST_RESULT '+json.dumps(result),flush=True)
    return 1 if failed else 0

def run_integrated(out_dir, case=""):
    """Real application routes and distributions; no substituted financial writers."""
    import shutil
    import tempfile
    from galton_board_test import prepare_page, serve
    from research_navigation_test import launch_browser
    from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
    out_dir.mkdir(parents=True, exist_ok=True)
    passed,failed,rows=[],[],[]
    server,url=serve()
    def financial(p):
        return p.evaluate('JSON.stringify({state:S,raw:localStorage.getItem(LSKEY),pref:localStorage.getItem(JPWGalton.persistence.STORAGE_KEY)})')
    def snap(p): return p.evaluate('document.getElementById("toolsTimeTwinsSlot").__timeTwinsController.snapshot()')
    def act(p,name): p.locator('[data-time-twins-root] [data-action="'+name+'"]').click()
    def fill(p,name,value): p.locator('[data-time-twins-root] [data-field="'+name+'"]').fill(str(value))
    def choose(p,name,value): p.locator('[data-time-twins-root] [data-field="'+name+'"]').select_option(value)
    def mission(p,name):
        if snap(p)['mode']!='home': act(p,'journey')
        p.locator('[data-mission="'+name+'"]').click()
    def predict(p,value='A'): choose(p,'prediction',value);act(p,'predict')
    def end(p):
        field=p.locator('[data-field="month"]');field.fill(field.get_attribute('max'));field.dispatch_event('input')
    def reason(p,value): choose(p,'reason',value);act(p,'reason')
    def settle(p): p.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    def open_game(p):
        assert p.evaluate("JPWNavigation.navigate('tools-minigames')")
        p.locator('#minigamesOpenTimeTwins').click()
        assert p.locator('#minigamesTimeTwinsTitle').evaluate('(e)=>e===document.activeElement')
        assert p.locator('[data-time-twins-root]').count()==1
    def check_clean(p):
        assert not p.jpwealth_observed['pageerror'],p.jpwealth_observed
        assert not [x for x in p.jpwealth_observed['console'] if x[0]=='error'],p.jpwealth_observed
        assert_fixture_requests(p.context)
    def test(name,fn):
        if case and case not in name:return
        print('[RUN] '+name,flush=True)
        try:
            row=fn();rows.append({'name':name,'facts':row});passed.append(name)
            print('[PASS] '+name,flush=True)
        except Exception:
            failed.append(name);print('[FAIL] '+name,flush=True);traceback.print_exc()
    try:
        with sync_playwright() as pw:
            browser=launch_browser(pw)
            def with_page(fn):
                p=prepare_page(browser,url)
                try: result=fn(p);check_clean(p);return result
                finally:p.jpwealth_context.close()
            def lazy_refusal(p):
                p.evaluate('sessionEpochCurrent()');before=financial(p)
                assert p.evaluate("JPWNavigation.navigate('tools-minigames')")
                assert p.locator('#minigamesHub article').count()==3
                assert p.locator('#minigamesHub').get_by_role('button',name='Abrir',exact=True).count()==3
                assert p.locator('#minigamesTimeTwinsCard').get_by_role('heading',name='Gêmeos do Tempo').is_visible()
                assert p.locator('[data-time-twins-root],[data-galton-root]').count()==0
                p.evaluate("JPWNavigation.navigateLocal('research','nocoda')")
                p.locator('#ncPrice1').fill('1,23412')
                p.evaluate("openSettingsModal('knowledge')")
                p.locator('#settingsPageTitle').focus()
                before_route=p.evaluate('JPWNavigation.current()');focus=p.evaluate('document.activeElement.id')
                for call in ["JPWNavigation.navigateLocal('tools','time-twins')","JPWNavigation.navigate('time-twins')","JPWNavigation.navigate('galton-board')"]:
                    assert p.evaluate(call) is False
                    assert p.evaluate('JPWNavigation.current()')==before_route
                    assert p.locator('#settingsOverlay').evaluate('(e)=>e.classList.contains("show")')
                    assert p.evaluate('document.activeElement.id')==focus
                    assert p.locator('#ncPrice1').input_value()=='1,23412'
                    assert p.locator('[data-time-twins-root],[data-galton-root]').count()==0
                    assert p.locator('[data-minigames-navigation-status]').inner_text()=='Feche a janela atual antes de abrir um jogo em MiniGames'
                p.evaluate('closeSettingsModal()');settle(p)
                assert p.evaluate('JPWNavigation.current()')==before_route
                assert p.locator('[data-time-twins-root]').count()==0
                p.evaluate("JPWModuleAvailability.setState('research','frozen')")
                assert p.evaluate("JPWNavigation.navigate('time-twins')")
                assert not snap(p)['running'] and snap(p)['month']==0
                assert p.locator('#minigamesTimeTwinsTitle').evaluate('(e)=>e===document.activeElement')
                p.locator('#minigamesTimeTwinsBack').click()
                assert p.locator('#minigamesOpenTimeTwins').evaluate('(e)=>e===document.activeElement')
                assert financial(p)==before
                return {'refused':3,'researchFrozenIndependent':True,'cards':3}
            test('integrated lazy hub, three refused entries, form/focus and Research independence',lambda:with_page(lazy_refusal))
            def lifecycle(p):
                p.emulate_media(reduced_motion='no-preference')
                p.evaluate('sessionEpochCurrent()');before=financial(p);open_game(p)
                p.evaluate('window.__twins=document.getElementById("toolsTimeTwinsSlot").__timeTwinsController')
                act(p,'free');fill(p,'A-initial',1234);act(p,'play')
                p.wait_for_function('__twins.snapshot().month>0')
                p.locator('#minigamesTimeTwinsBack').click();m=snap(p)['month']
                assert not snap(p)['active'] and not snap(p)['running']
                assert p.locator('#minigamesOpenTimeTwins').evaluate('(e)=>e===document.activeElement')
                p.locator('#minigamesOpenGalton').click()
                p.evaluate("window.__galton=document.querySelector('[data-galton-root]').__galtonController")
                p.locator('[data-galton-add="10"]').click();p.locator('[data-galton-action="execute"]').click()
                p.wait_for_function('__galton.snapshot().spawnedCount>0')
                p.locator('#minigamesBack').click()
                assert p.locator('#minigamesOpenGalton').evaluate('(e)=>e===document.activeElement')
                p.locator('#minigamesOpenTimeTwins').click()
                assert p.evaluate('document.getElementById("toolsTimeTwinsSlot").__timeTwinsController===__twins')
                assert snap(p)['month']==m and not snap(p)['running'] and snap(p)['applied']['a']['initialCapital']==1234
                for call,close in [("openSettingsModal('general')","closeSettingsModal()"),('openMvpNotesDrawer()',"document.getElementById('mvpNotesCloseBtn').click()"),('openFinalizeSessionFlow()',"document.getElementById('sessionCancel').click()")]:
                    act(p,'play');p.evaluate(call);settle(p)
                    assert not snap(p)['active'] and not snap(p)['running']
                    m=snap(p)['month'];p.wait_for_timeout(90);assert snap(p)['month']==m
                    p.evaluate(close);settle(p)
                    assert snap(p)['active'] and not snap(p)['running']
                act(p,'play')
                p.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
                assert not snap(p)['running'];m=snap(p)['month'];p.wait_for_timeout(90);assert snap(p)['month']==m
                p.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'))");settle(p)
                assert snap(p)['active'] and not snap(p)['running']
                p.locator('#minigamesTimeTwinsBack').click();p.locator('#minigamesOpenGalton').click()
                assert p.evaluate("document.querySelector('[data-galton-root]').__galtonController===__galton && __galton.manualPaused && !__galton.snapshot().running")
                assert financial(p)==before
                return {'dialogs':3,'sameInstances':True,'hiddenRequiresContinue':True}
            test('integrated game switching, real dialogs and hidden pause same instances',lambda:with_page(lifecycle))
            def missions(p):
                p.evaluate('sessionEpochCurrent()');before=financial(p);open_game(p)
                mission(p,'early-start');predict(p);end(p);reason(p,'time')
                fill(p,'A-deposit',120)
                assert snap(p)['prediction'] is None and not snap(p)['reasonCorrect'] and snap(p)['month']==0
                assert p.locator('[data-action="complete"]').is_disabled()
                predict(p,'B');end(p);assert snap(p)['prediction']['correct']
                assert '1.790,85' in p.locator('[data-output="final-A"]').inner_text()
                assert '2.396,56' in p.locator('[data-output="final-B"]').inner_text()
                mission(p,'early-start');predict(p,'B');end(p);reason(p,'time')
                assert p.locator('[data-action="complete"]').is_disabled()
                act(p,'help');act(p,'assisted');assert snap(p)['progress']['missions']['early-start']=='assisted'
                mission(p,'early-start');predict(p);end(p);act(p,'zero');predict(p,'equal');end(p);reason(p,'time');act(p,'complete')
                assert snap(p)['progress']['missions']['early-start']=='demonstrated'
                mission(p,'equal-budget');previous=snap(p)['draft']['b']['contributions'];fill(p,'B-start',70)
                changed=snap(p)['draft']['b']['contributions']
                assert sum(x['amount'] for x in changed)==1200 and [x['id'] for x in changed]==[x['id'] for x in previous]
                assert [x['month'] for x in changed]==list(range(70,82))
                predict(p);end(p);reason(p,'calendar');act(p,'complete')
                mission(p,'contribution-story');predict(p);choose(p,'actor','B');choose(p,'cohort','B-month-49');end(p)
                original=snap(p)['applied'];act(p,'trace');act(p,'without')
                assert p.locator('[data-output="trace"] tr').count()>100
                assert p.locator('[data-chart-line="without"]').get_attribute('d') and snap(p)['applied']==original
                reason(p,'cohort');act(p,'complete')
                mission(p,'three-levers')
                for lever,field,value in [('prazo','A-horizon',300),('taxa','A-rate',8),('aporte','A-monthly',150)]:
                    choose(p,'lever',lever);fill(p,field,value);predict(p);end(p)
                    draft=snap(p)['draft']
                    if lever=='taxa':assert draft['a']['horizonMonths']==240 and draft['a']['contributions'][0]['amount']==100
                    if lever=='aporte':assert draft['a']['annualRate']==.06 and draft['a']['horizonMonths']==240
                reason(p,'lever');act(p,'complete')
                mission(p,'next-contribution');predict(p);end(p)
                assert '0,66%' in p.locator('[data-output="extra-A"]').inner_text()
                assert '319,16' in p.locator('[data-output="extra-A"]').inner_text()
                choose(p,'actor','A');choose(p,'cohort','A-extra')
                assert '0,65%' in p.locator('[data-output="inspection"]').inner_text()
                assert '0,66%' not in p.locator('[data-output="inspection"]').inner_text()
                fill(p,'A-extra',2);predict(p);end(p)
                assert len(snap(p)['draft']['baselineA']['contributions'])==240
                assert '%' in p.locator('[data-output="extra-A"]').inner_text()
                reason(p,'extra');act(p,'complete')
                mission(p,'crossover');predict(p,'late');end(p);act(p,'cross')
                assert '134' in p.locator('[data-output="crossover-A"]').inner_text()
                assert 'não implica independência financeira' in p.locator('[data-output="feedback"]').inner_text()
                fill(p,'A-rate',0);predict(p,'never');end(p);act(p,'cross');reason(p,'period');act(p,'complete')
                progress=snap(p)['progress'];assert set(progress['missions'].values())=={'demonstrated'} and len(progress['missions'])==6
                mission(p,'early-start');act(p,'help');act(p,'assisted');assert snap(p)['progress']['missions']['early-start']=='demonstrated'
                act(p,'restart');act(p,'confirm-restart');act(p,'skip');assert snap(p)['progress']['missions']['early-start']=='skipped'
                raw=p.evaluate('(key)=>localStorage.getItem(key)',KEY);saved=json.loads(raw)
                assert set(saved)=={'schemaVersion','currentMissionId','missions'} and saved['schemaVersion']==1
                p.reload(wait_until='load');wait_bootstrap(p);p.evaluate('closeModal()');open_game(p)
                assert snap(p)['progress']==saved
                act(p,'free');applied=snap(p)['applied'];fill(p,'A-initial','1.234')
                assert not snap(p)['valid'] and snap(p)['applied']==applied and p.locator('[data-action="play"]').is_disabled()
                fill(p,'A-initial',4567);fill(p,'A-rate',0);fill(p,'A-horizon',360)
                assert snap(p)['valid'] and p.evaluate('(key)=>localStorage.getItem(key)',KEY)==raw
                assert financial(p)==before
                return {'missionsDemonstrated':6,'assistedSkipped':True,'reload':True,'schemaOnly':True,'firstCrossover':134}
            test('integrated all six experiments, statuses, immutable baseline, invalid input and saved reload',lambda:with_page(missions))
            def dispose(p):
                p.evaluate('sessionEpochCurrent()');open_game(p);act(p,'start');act(p,'skip')
                saved=p.evaluate('(key)=>localStorage.getItem(key)',KEY)
                before=financial(p)
                p.evaluate('window.__oldTwins=document.getElementById("toolsTimeTwinsSlot").__timeTwinsController;window.__oldRoot=document.querySelector("[data-time-twins-root]");window.__oldButton=__oldRoot.querySelector("[data-mission]")')
                p.evaluate("openSettingsModal('general');sessionResetAuxiliarySurfaces()")
                assert p.evaluate('__oldTwins.snapshot().destroyed')
                assert p.locator('[data-time-twins-root]').count()==0
                p.evaluate('closeSettingsModal()');settle(p)
                p.evaluate("document.dispatchEvent(new Event('visibilitychange'));__oldButton.click();__oldTwins.activate()")
                settle(p)
                assert p.locator('[data-time-twins-root]').count()==0, 'closing real dialog after reset must not resurrect controller'
                assert p.evaluate('(key)=>localStorage.getItem(key)',KEY)==saved
                report=p.evaluate('clearJPWealthLocalData({removeAuxiliary:false,preserveMain:true})')
                assert report['ok'] and p.evaluate('(key)=>localStorage.getItem(key)',KEY)==saved
                assert financial(p)==before
                assert p.evaluate("JPWNavigation.navigate('time-twins')")
                assert p.evaluate('document.getElementById("toolsTimeTwinsSlot").__timeTwinsController!==__oldTwins')
                assert snap(p)['mode']=='home' and snap(p)['month']==0 and not snap(p)['running']
                assert snap(p)['progress']['missions']['early-start']=='skipped'
                p.evaluate("localStorage.setItem('synthetic_foreign_aux','preserve')")
                report=p.evaluate('clearJPWealthLocalData({removeAuxiliary:true,preserveMain:true})')
                assert report['ok'] and KEY in report['removedKeys']
                assert p.evaluate('(key)=>localStorage.getItem(key)',KEY) is None
                assert p.evaluate("localStorage.getItem('synthetic_foreign_aux')")=='preserve'
                assert p.evaluate('JSON.stringify({state:S,raw:localStorage.getItem(LSKEY)})')==p.evaluate('(saved)=>JSON.stringify({state:saved.state,raw:saved.raw})',json.loads(before))
                p.evaluate('sessionResetAuxiliarySurfaces()');settle(p)
                assert p.locator('[data-time-twins-root]').count()==0 and p.evaluate('(key)=>localStorage.getItem(key)',KEY) is None
                return {'destroyed':True,'observerNoResurrection':True,'freshExplicitEntry':True,'auxiliaryKeyRemovedOnlyByExplicitCleanup':True}
            test('integrated dispose, real dialog close without resurrection, stale root and auxiliary cleanup',lambda:with_page(dispose))
            def matrix(p):
                import re
                p.evaluate('sessionEpochCurrent()');before=financial(p);open_game(p)
                p.evaluate('window.__matrixTwins=document.getElementById("toolsTimeTwinsSlot").__timeTwinsController')
                matrix_rows=[]
                def lum(color):
                    values=[int(x)/255 for x in re.findall(r'\d+',color)[:3]]
                    return sum((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)*w for v,w in zip(values,[.2126,.7152,.0722]))
                def ratio(a,b):
                    x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
                def arrival():
                    facts=p.evaluate('''() => {
                      const title=document.querySelector('[data-output="title"]'),description=title.nextElementSibling;
                      const first=document.querySelector('[aria-label="Preparar experimento"]').querySelector('button:not(:disabled),input:not(:disabled),select:not(:disabled)');
                      const box=e=>{const r=e.getBoundingClientRect();return {y:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height}};
                      const hits=e=>{const r=e.getBoundingClientRect();return [.2,.5,.8].map(f=>{const x=r.left+r.width*f,y=r.top+r.height*.5,hit=document.elementFromPoint(x,y);return {x,y,own:hit===e||e.contains(hit),hit:hit?.outerHTML.slice(0,180)}})};
                      const h=document.querySelector('body > header'),r=h?.getBoundingClientRect(),pos=h&&getComputedStyle(h).position;
                      return {focus:document.activeElement===title,title:box(title),description:box(description),control:{field:first.dataset.field,...box(first)},titleHits:hits(title),descriptionHits:hits(description),controlHits:hits(first),header:h&&box(h),navShell:document.getElementById('navSubShell')&&box(document.getElementById('navSubShell')),toolsNav:document.getElementById('toolsNavSubmenu')&&box(document.getElementById('toolsNavSubmenu')),height:innerHeight,obstruction:r&&['sticky','fixed'].includes(pos)&&r.top<innerHeight?Math.max(0,r.bottom):0,overflow:document.documentElement.scrollWidth-innerWidth};
                    }''')
                    facts.update(layout=layout,width=width,theme=theme,cssZoom=zoom)
                    if facts['control']['bottom']>facts['height']+1:
                        (out_dir/'arrival-failure.json').write_text(json.dumps(facts,indent=2))
                        p.screenshot(path=str(out_dir/'arrival-failure.png'))
                    assert facts['focus'] and facts['overflow']<=1,facts
                    assert facts['title']['y']>=facts['obstruction']-1 and facts['control']['y']>=facts['obstruction']-1,facts
                    assert facts['title']['bottom']<=facts['height']+1 and facts['control']['bottom']<=facts['height']+1,facts
                    assert facts['description']['y']>=facts['obstruction']-1 and facts['description']['bottom']<=facts['height']+1,facts
                    assert facts['control']['height']>=44,facts
                    assert all(point['own'] for key in ['titleHits','descriptionHits','controlHits'] for point in facts[key]),facts
                    return facts
                for layout in ['sidebar','topbar','glass','submenu']:
                    for width in [1440,390]:
                        p.set_viewport_size({'width':width,'height':900 if width==1440 else 844})
                        p.evaluate('(mode)=>mountNavigationLayout(mode)',layout)
                        for theme in ['dark','light']:
                            p.evaluate('(theme)=>document.documentElement.dataset.theme=theme',theme)
                            for zoom in [1,1.25]:
                                p.evaluate('(zoom)=>document.documentElement.style.zoom=zoom',zoom)
                                open_game(p)
                                if snap(p)['mode']!='home':act(p,'journey')
                                control=p.locator('[data-mission="early-start"]');control.hover()
                                colors=control.evaluate('e=>{const s=getComputedStyle(e),t=getComputedStyle(e.querySelector("small"));return {background:s.backgroundColor,text:s.color,status:t.color}}')
                                colors['textRatio']=ratio(colors['background'],colors['text']);colors['statusRatio']=ratio(colors['background'],colors['status'])
                                assert min(colors['textRatio'],colors['statusRatio'])>=4.5,colors
                                control.focus();p.keyboard.press('Tab');p.keyboard.press('Shift+Tab')
                                assert control.evaluate('e=>e===document.activeElement&&e.matches(":focus-visible")')
                                focus=control.evaluate('e=>{const s=getComputedStyle(e);return {width:s.outlineWidth,style:s.outlineStyle,color:s.outlineColor,shadow:s.boxShadow,focused:e===document.activeElement,matched:e.matches(":focus-visible")}}')
                                assert float(focus['width'].removesuffix('px'))*zoom>=1.99,(layout,width,theme,zoom,focus)
                                control.press('Enter');settle(p);entry=arrival()
                                act(p,'journey');act(p,'start');settle(p);arrival()
                                act(p,'next');settle(p);arrival()
                                assert p.evaluate('document.getElementById("toolsTimeTwinsSlot").__timeTwinsController===__matrixTwins')
                                if layout=='sidebar' and zoom==1:
                                    p.screenshot(path=str(out_dir/f'integrated-{width}-{theme}.png'),full_page=True)
                                matrix_rows.append({'layout':layout,'width':width,'theme':theme,'cssZoom':zoom,'entry':entry,'hover':colors})
                p.evaluate('document.documentElement.style.zoom=1')
                assert len(matrix_rows)==32 and financial(p)==before
                (out_dir/'matrix.json').write_text(json.dumps(matrix_rows,indent=2))
                return {'presentations':len(matrix_rows),'reducedMotion':True,'keyboardHoverFocus':True,'zoomType':'CSS reflow, not native browser zoom'}
            test('integrated 32 layouts themes widths zooms with hover keyboard and explicit arrival',lambda:with_page(matrix))
            def distributions():
                results=[]
                with tempfile.TemporaryDirectory(prefix='jpw-time-twins-portable-') as temp:
                    detached=Path(temp)/'standalone.html';shutil.copyfile(ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html',detached)
                    assert list(Path(temp).iterdir())==[detached]
                    for mode,target in [('http',url),('modular-file',(ROOT/'index.html').as_uri()),('portable-alone',detached.as_uri()),('pwa-offline',url)]:
                        ctx=browser.new_context(service_workers='allow' if mode=='pwa-offline' else 'block',viewport={'width':390,'height':844},reduced_motion='reduce')
                        install_bootstrap(ctx);ctx.add_init_script('window.__onbShown=true;')
                        p=ctx.new_page();errors=[];console=[];sw=[]
                        p.on('pageerror',lambda e:errors.append(str(e)))
                        p.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
                        p.on('response',lambda r:sw.append(r.url) if r.from_service_worker else None)
                        try:
                            p.goto(target,wait_until='load');wait_bootstrap(p);p.evaluate('closeModal()')
                            if mode=='pwa-offline':
                                p.evaluate('navigator.serviceWorker.ready');p.reload(wait_until='load');wait_bootstrap(p)
                                p.wait_for_function('navigator.serviceWorker.controller!==null')
                                sw.clear();ctx.set_offline(True);response=p.reload(wait_until='load');wait_bootstrap(p);p.evaluate('closeModal()')
                                assert response.from_service_worker
                                assert all(any('/'+path in response_url for response_url in sw) for path in FILES),sw
                            p.evaluate('sessionEpochCurrent()');before=financial(p);open_game(p)
                            assert snap(p)['month']==0 and not snap(p)['running']
                            act(p,'free');act(p,'step-year');assert snap(p)['month']==12
                            p.locator('#minigamesTimeTwinsBack').click();p.locator('#minigamesOpenTimeTwins').click()
                            assert snap(p)['month']==12 and not snap(p)['running']
                            mission(p,'early-start');act(p,'skip')
                            assert snap(p)['progress']['missions']['early-start']=='skipped'
                            assert financial(p)==before and not errors and not console,(errors,console)
                            assert_fixture_requests(ctx)
                            results.append({'mode':mode,'newScriptsFromSW':len(FILES) if mode=='pwa-offline' else 0,'stepYear':12,'financialUnchanged':True})
                            print('TIME_TWINS_DISTRIBUTION_PASS '+json.dumps(results[-1]),flush=True)
                        finally:ctx.close()
                return results
            test('integrated HTTP modular file detached portable and native SW offline distributions',distributions)
            browser.close()
    finally:server.shutdown();server.server_close()
    result={'suite':'time_twins_browser_integrated','passed':len(passed),'failed':len(failed),'failures':failed,'rows':rows,
            'limits':['Synthetic disposable profiles; no personal account data.','32 CSS zoom/reflow presentations are not native browser zoom.','Physical touch, screen reader and human learning NOT_RUN.']}
    (out_dir/'integrated-result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('JPW_TEST_RESULT '+json.dumps({k:result[k] for k in ['suite','passed','failed','failures']}),flush=True)
    return 1 if failed else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['standalone','integrated','all'],default='standalone')
    parser.add_argument('--out-dir',type=Path,default=ARTIFACTS/'integrated')
    parser.add_argument('--case',default='',help='Integrated group substring filter')
    args=parser.parse_args()
    if args.mode=='all':
        ARTIFACTS=args.out_dir/'standalone';ARTIFACTS.mkdir(parents=True,exist_ok=True)
    result=run() if args.mode in ('standalone','all') else 0
    if args.mode in ('integrated','all'):
        result=max(result,run_integrated(args.out_dir,args.case))
    raise SystemExit(result)

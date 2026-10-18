#!/usr/bin/env python3
"""Synthetic real-browser contracts: catches auto-run, wrong integration, resets,
invalid input coercion, hidden loops, financial access, persistence and overflow."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading, json, os
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('JPW_CAPITAL_FIELD_OUT', str(ROOT/'tools/.artifacts/capital-field-work-20261015/browser')))
CHROME=os.environ.get('JP_WEALTH_CHROMIUM')
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        if self.path=='/':
            names=['01-engine','02-scenarios','03-progress','04-field-renderer','04-view','05-controller']
            scripts=''.join(f'<script src="/src/js/40-app/30-capital-currents/{n}.js"></script>' for n in names)
            data=('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/src/styles/app.css"><body style="margin:0;display:block"><main id="host"></main>'+scripts+'</body></html>').encode(); mime='text/html'
        else:
            path=ROOT/self.path.lstrip('/')
            if not path.is_file(): self.send_error(404); return
            data=path.read_bytes(); mime='text/css' if path.suffix=='.css' else 'application/javascript'
        self.send_response(200); self.send_header('Content-Type',mime); self.end_headers(); self.wfile.write(data)
def check(value,msg):
    assert value,msg
    print("PASS "+msg,flush=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**({'executable_path':CHROME} if CHROME else {}),headless=True)
            ctx=browser.new_context(viewport={'width':1440,'height':1080},device_scale_factor=2)
            page=ctx.new_page(); errors=[]; page.on('pageerror',lambda err:errors.append(str(err)))
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            page.evaluate('''() => {window.writes=[]; ['jpwealth_capital_currents_v1','jpwealth_capital_field_v1','jpw_financial_sentinel'].forEach(k=>localStorage.setItem(k,'synthetic-preserve')); const set=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){writes.push(k);return set.call(this,k,v)}; ['state','appState','saveState','JPWFinancial'].forEach(k=>Object.defineProperty(window,k,{get(){throw Error('financial access '+k)},configurable:true}));}''')
            # This must fail against old campaign before the visual-field implementation.
            check(page.evaluate("typeof JPWCapitalCurrents.renderer === 'object'"),'dominant field renderer missing: old campaign is not the visual field')
            page.evaluate("window.ctl=JPWCapitalCurrents.mount(document.getElementById('host')); ctl.activate()")
            snap=lambda:page.evaluate('ctl.snapshot()')
            s=snap(); check('learning' in s, 'optional learning diagnostics missing')
            check(page.locator('[data-action=learn]').count()==1,'optional learning entry missing')
            check(s['active'] and not s['running'] and s['tick']==0 and not s['loopScheduled'],'entry must be paused with no RAF')
            check(page.evaluate("JPWCapitalCurrents.mount(document.getElementById('host'))===ctl"),'mount singleton')
            check(page.locator('canvas').count()==1,'single field')
            check(page.locator('canvas').bounding_box()['height']>=580,'desktop field must dominate')
            check(page.evaluate("(()=>{let c=document.querySelector('canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,n=0;for(let i=0;i<d.length;i+=4)if(d[i+1]>90&&d[i+2]>120)n++;return n>10000})()"),'dense field pixels')
            act=lambda name:page.locator(f'[data-action="{name}"]').first.click()
            field=lambda name:page.locator(f'[data-field="{name}"]')
            act('step'); s=snap(); check(s['tick']==15 and abs(s['time']-.25)<1e-10,'step must be fifteen fixed ticks')
            # Hand analytic uniform solution q=.4(1-exp(-.25)), p=.8(.25-1+exp(-.25)).
            check(abs(s['state']['q']-.08847968677143805)<1e-10 and abs(s['state']['p']-.0230406264567)<1e-8,'step numerical result')
            before=s['state']; field('depth').select_option('2')
            depth_status=page.locator('[data-output="status"]').inner_text()
            check('0,177' in depth_status and '0,088' in depth_status and 'pontos/s' in depth_status and 'ilustrativ' in depth_status,'depth status must explain actual same-state illustrative local velocity before and after')
            field('u').fill('0.65'); field('u').dispatch_event('input')
            check(snap()['state']==before,'changing parameters must preserve scenario')
            act('release'); check(snap()['params']['u']==0 and snap()['state']==before,'release must preserve history/time')
            act('step'); s=snap(); check(0<s['state']['q']<before['q'] and s['state']['p']>before['p'],'released positive pressure decays while price keeps rising')
            field('q').fill(''); act('position'); check(page.locator('[role="alert"]').inner_text() and snap()['state']==s['state'],'blank input must reject without reset')
            field('q').fill('-0.3'); field('p').fill('2'); act('position'); check(snap()['state']=={'q':-.3,'p':2,'t':0},'keyboard placement')
            field('q').focus(); field('u').focus(); field('u').press('ArrowRight'); check(page.evaluate('document.activeElement.dataset.field')=='u','parameter patch must preserve focus')
            act('step'); gesture_before=snap()
            page.evaluate('''() => {const c=document.querySelector('canvas'),r=c.getBoundingClientRect();const fire=(type,x,y,id=7)=>c.dispatchEvent(new PointerEvent(type,{bubbles:true,button:0,pointerId:id,isPrimary:true,pointerType:'touch',clientX:r.left+x,clientY:r.top+y}));fire('pointerdown',100,150);fire('pointermove',100,215);fire('pointercancel',100,215);fire('pointerup',100,215);}''')
            check(snap()['state']==gesture_before['state'] and snap()['trailCount']==gesture_before['trailCount'],'touch pan cancellation must preserve selected state/time/trail')
            page.evaluate('''() => {const c=document.querySelector('canvas'),r=c.getBoundingClientRect();const fire=(type,x,y,id=8)=>c.dispatchEvent(new PointerEvent(type,{bubbles:true,button:0,pointerId:id,isPrimary:true,clientX:r.left+x,clientY:r.top+y}));fire('pointerdown',100,150);fire('pointermove',180,150);fire('pointerup',180,150);}''')
            check(snap()['state']==gesture_before['state'],'completed drag must not reposition')
            page.evaluate('''() => {const c=document.querySelector('canvas'),r=c.getBoundingClientRect();const fire=(type,id,primary)=>c.dispatchEvent(new PointerEvent(type,{bubbles:true,button:0,pointerId:id,isPrimary:primary,pointerType:'touch',clientX:r.left+100,clientY:r.top+150}));fire('pointerdown',10,true);fire('pointerdown',11,false);fire('pointerup',11,false);fire('pointerup',10,true);}''')
            check(snap()['state']==gesture_before['state'],'multi-touch must not select')
            for clear in ['ctl.pause()', 'ctl.deactivate()', 'window.dispatchEvent(new Event("blur"))']:
                page.evaluate('ctl.activate()'); pending_before=snap()
                page.evaluate('''() => {const c=document.querySelector('canvas'),r=c.getBoundingClientRect();c.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,button:0,pointerId:12,isPrimary:true,clientX:r.left+100,clientY:r.top+150}));}''')
                page.evaluate(clear)
                page.evaluate('''() => {const c=document.querySelector('canvas'),r=c.getBoundingClientRect();c.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,button:0,pointerId:12,isPrimary:true,clientX:r.left+100,clientY:r.top+150}));}''')
                check(snap()['state']==pending_before['state'],'pending tap must clear on pause/deactivate/blur')
            page.evaluate('ctl.activate()')
            box=page.locator('canvas').bounding_box(); page.mouse.click(box['x']+box['width']*.5,box['y']+box['height']*.5)
            check(not snap()['running'] and snap()['tick']==0 and abs(snap()['state']['q'])<.15,'pointer selects scenario paused')
            act('reset'); act('play'); page.wait_for_timeout(180); page.screenshot(path=str(OUT/'desktop-running.png'),full_page=True); check(snap()['tick']>0,'play actually advects'); act('play'); check(not snap()['loopScheduled'],'pause cancels RAF')
            frozen=snap()['tick']; page.wait_for_timeout(100); check(snap()['tick']==frozen,'paused time must freeze')
            page.screenshot(path=str(OUT/'desktop-paused.png'),full_page=True)
            for trigger in ['window.dispatchEvent(new Event("blur"))','document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape"}))','ctl.deactivate()']:
                page.evaluate('ctl.activate()'); act('play'); page.evaluate(trigger); check(not snap()['running'] and not snap()['loopScheduled'],'lifecycle must cancel animation '+trigger)
            page.evaluate('ctl.activate()'); page.evaluate('''let overlay=document.createElement("div"); overlay.hidden=true;overlay.innerHTML='<section role="dialog">Hidden foreign dialog</section>';document.body.append(overlay);window.hiddenOverlay=overlay'''); act('play'); page.wait_for_timeout(80); check(snap()['running'],'dialog in hidden ancestor must not block play'); act('play'); page.evaluate('hiddenOverlay.remove()'); act('play'); page.evaluate('let d=document.createElement("dialog");document.body.append(d);d.showModal()'); page.wait_for_timeout(60); check(not snap()['running'],'foreign dialog pauses'); page.evaluate('document.querySelector("dialog").remove()')
            page.evaluate('ctl.activate()'); act('play'); page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))"); check(not snap()['running'],'hidden pauses'); page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:false})")
            check(page.evaluate("writes.length===0 && ['jpwealth_capital_currents_v1','jpwealth_capital_field_v1','jpw_financial_sentinel'].every(k=>localStorage.getItem(k)==='synthetic-preserve')"),'storage sentinel unchanged')
            # Layer controls affect rendering independently, not underlying scenario math.
            for layer in ['vectors','streamlines','particles','trail']:
                page.locator(f'[data-layer="{layer}"]').uncheck()
            check(snap()['field']['vectors']==0 and snap()['field']['streamlines']==0 and not any(snap()['layers'].values()),'separate layer switches')
            for layer in ['vectors','streamlines','particles','trail']:
                page.locator(f'[data-layer="{layer}"]').check()
            check(snap()['field']['vectors']>200 and snap()['field']['streamlines']>30,'dense static field returns')
            field('q').fill('0'); field('p').fill('3'); act('position'); act('release'); field('depth').select_option('0.5'); act('step')
            check(snap()['state']['q']==0 and snap()['state']['p']==3,'zero pressure must stay stationary at nonzero price even in shallow depth'); zero_before=snap(); field('depth').select_option('2'); zero_status=page.locator('[data-output="status"]').inner_text(); check('q = 0' in zero_status and 'não move' in zero_status and snap()['state']==zero_before['state'] and snap()['trailCount']==zero_before['trailCount'],'zero-pressure depth change explains absence of movement without advancing')
            field('q').fill('1'); field('p').fill('5.999'); act('position'); act('step')
            check(snap()['exited'] and snap()['tick']==1 and not snap()['running'] and page.locator('[data-action="play"]').is_disabled(),'selected scenario exits and pauses instead of recycling')
            # Scheduler control lives in the test only. Same six ticks delivered through
            # different frame partitions must yield identical states, independent of FPS.
            page.evaluate('''() => {window.frames=new Map();window.nextFrame=0;window.requestAnimationFrame=cb=>{frames.set(++nextFrame,cb);return nextFrame};window.cancelAnimationFrame=id=>frames.delete(id);window.deliverFrame=t=>{const callbacks=Array.from(frames.values());frames.clear();callbacks.forEach(cb=>cb(t))};}''')
            act('reset'); act('play'); page.evaluate('[0,50,100].forEach(deliverFrame)'); partition_a=snap(); act('play')
            act('reset'); act('play'); page.evaluate('[0,20,40,60,80,100].forEach(deliverFrame)'); partition_b=snap(); act('play')
            check(partition_a['tick']==6 and partition_b['tick']==6 and partition_a['state']==partition_b['state'],'frame partitions must preserve fixed-tick outcome')
            act('play'); page.evaluate('deliverFrame(100000)'); check(snap()['tick']==6,'resuming must not catch up paused wall time'); act('play')
            page.evaluate('ctl.destroy(); window.dispatchEvent(new Event("resize")); ctl.activate()'); check(snap()['destroyed'] and not snap()['active'] and not snap()['loopScheduled'],'late events cannot resurrect')
            page.evaluate("window.ctl=JPWCapitalCurrents.activate(document.getElementById('host'))")
            page.evaluate('window.requestAnimationFrame=cb=>setTimeout(()=>cb(performance.now()),16);window.cancelAnimationFrame=id=>clearTimeout(id)'); page.set_viewport_size({'width':390,'height':844}); page.wait_for_timeout(120)
            check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'mobile overflow')
            print('MOBILE_GEOMETRY '+json.dumps({k:page.locator(v).bounding_box() for k,v in {'entry':'[data-action=learn]','canvas':'canvas','play':'[data-action=play]'}.items()}),flush=True)
            check(page.locator('[data-action=learn]').bounding_box()['y']<page.locator('canvas').bounding_box()['y'],'learning entry discoverable before field')
            check(field('u').bounding_box()['y'] < page.locator('canvas').bounding_box()['y'],'mobile primary controls must sit near and above visible field'); check(page.locator('[data-action=play]').bounding_box()['y']<844,'mobile field and transport must fit first screen')
            page.screenshot(path=str(OUT/'mobile-paused.png'),full_page=True)
            # Real Chromium touch pan through CDP: scrolling begins on the canvas,
            # exercising native pointercancel rather than only synthetic events.
            page.evaluate('window.scrollTo(0,0)'); mobile_before=snap(); rect=page.locator('canvas').bounding_box()
            cdp=ctx.new_cdp_session(page); cdp.send('Emulation.setTouchEmulationEnabled',{'enabled':True})
            x=rect['x']+rect['width']/2; y=rect['y']+rect['height']/2
            cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
            for delta in [20,45,75,110]:
                cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':y-delta}]}); page.wait_for_timeout(20)
            cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]}); page.wait_for_timeout(100)
            check(page.evaluate('scrollY')>0 and snap()['state']==mobile_before['state'] and snap()['trailCount']==mobile_before['trailCount'],'native canvas touch-pan must scroll without resetting scenario')
            cdp.send('Emulation.setTouchEmulationEnabled',{'enabled':False}); cdp.detach(); page.evaluate('window.scrollTo(0,0)')
            act('play'); page.wait_for_timeout(100); page.screenshot(path=str(OUT/'mobile-running.png'),full_page=True); act('play')
            page.evaluate('document.documentElement.style.zoom="2"'); page.wait_for_timeout(100); check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'200% zoom overflow'); page.screenshot(path=str(OUT/'mobile-200-percent.png'),full_page=True); page.evaluate('''() => {const c=document.querySelector('canvas'),r=c.getBoundingClientRect(),w=c.clientWidth,h=c.clientHeight; ['pointerdown','pointerup'].forEach(type=>c.dispatchEvent(new PointerEvent(type,{bubbles:true,button:0,pointerId:1,isPrimary:true,clientX:r.left+(44+(w-64)*.25)*r.width/w,clientY:r.top+(32+(h-101)/3)*r.height/h})));}'''); check(abs(snap()['state']['q']+.5)<.015 and abs(snap()['state']['p']-2)<.05,'zoom pointer coordinates must match displayed axes'); page.evaluate('document.documentElement.style.zoom="1"'); page.set_viewport_size({'width':320,'height':740}); page.wait_for_timeout(100); check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'320px overflow'); page.screenshot(path=str(OUT/'mobile-320.png'),full_page=True)
            # Teaching is optional; opening reads only, practice requires observed actions.
            page.set_viewport_size({'width':390,'height':844})
            page.evaluate("localStorage.removeItem(JPWCapitalCurrents.progress.KEY); ctl.destroy(); window.ctl=JPWCapitalCurrents.activate(document.getElementById('host')); writes.length=0")
            act('learn'); check(not snap()['learning']['eligible'] and page.evaluate('writes.length===0'),'opening must not save or award practice')
            check(page.locator('[data-action=practice]').is_disabled(),'practice disabled before selection and advance')
            act('step'); check(not snap()['learning']['eligible'],'pre-selection advance cannot satisfy field practice')
            act('reset');act('step');check(not snap()['learning']['eligible'],'reset is not successful pointer or keyboard selection')
            act('release'); field('q').fill('0'); field('p').fill('0'); act('position'); act('step')
            check(snap()['learning']['eligible'] and 'Antes:' in page.locator('[data-learning-result]').inner_text(),'actual selection and elapsed clock must produce before/after evidence even with no motion')
            page.evaluate("window.lessonNode=document.querySelector('[data-action=seen]');lessonNode.focus();document.querySelector('[data-action=play]').click()");page.wait_for_timeout(80);page.evaluate("document.querySelector('[data-action=play]').click()");check(page.evaluate('document.activeElement===lessonNode && document.querySelector(\'[data-action=seen]\')===lessonNode'),'lesson node and focus survive actual ticks')
            act('seen'); check(snap()['learning']['progress']['steps']['intro-field']=='seen','seen is distinct from practiced')
            act('practice'); check(snap()['learning']['progress']['steps']['intro-field']=='practiced','explicit observed practice persists')
            page.locator('[data-action=seen]').focus();page.keyboard.press('Enter');check(page.evaluate('document.activeElement.dataset.action')=='seen','keyboard seen retains action focus');page.locator('[data-action=next]').focus();page.keyboard.press('Enter');check(page.evaluate('document.activeElement.tagName')=='H4','keyboard next focuses new lesson heading');page.keyboard.press('Tab');check(page.evaluate('document.activeElement.dataset.action')=='seen','keyboard Tab continues into new lesson actions');check(not snap()['learning']['eligible'],'lesson starts with fresh evidence')
            act('prepare'); act('step'); check(not snap()['learning']['eligible'],'applying alone does not complete release practice'); before_release=snap()['state']
            act('release'); act('step'); check(snap()['learning']['eligible'] and abs(snap()['state']['q'])<abs(before_release['q']) and snap()['state']['p']>before_release['p'],'pressure practice observes actual release result')
            act('practice'); act('next'); act('seen'); field('q').fill('0');field('p').fill('0');act('position');field('depth').select_option('0.5');check(not snap()['learning']['eligible'],'zero pressure depth change cannot demonstrate nonzero comparison');field('q').fill('0.2');act('position');field('depth').select_option('2')
            check(snap()['learning']['eligible'] and 'dp/dt passou' in page.locator('[data-learning-result]').inner_text(),'depth practice compares actual nonzero same state derivatives')
            act('practice'); page.screenshot(path=str(OUT/'mobile-intro.png'),full_page=True)
            act('learn');act('next');act('prepare');field('u').fill('-0.4');field('u').dispatch_event('input');act('step');negative=snap()['state'];act('release');act('step');check(snap()['learning']['eligible'] and snap()['state']['q']>negative['q'] and snap()['state']['p']<negative['p'],'negative pressure practice is symmetric');act('learn'); act('skip'); check(snap()['learning']['progress']['steps']['intro-field']=='practiced','skip/revisit cannot downgrade practice')
            for discovery in ['release-pressure','same-pulse-depth','shallow-band']:
                page.locator(f'[data-lesson="{discovery}"]').click(); prior=snap(); act('compare'); after=snap(); result=after['learning']['comparison']
                check(after['state']==prior['state'] and after['params']==prior['params'] and after['trailCount']==prior['trailCount'] and not after['running'],'comparison preserves and pauses main field')
                check(result['a'][0]==result['b'][0] and result['a'][0]==result['initial'],'comparison common initial conditions')
                expected=page.evaluate('(id)=>JPWCapitalCurrents.catalog.experiment(id)',discovery)
                check(result==expected and len(result['a'])>60,'display uses actual catalog trajectories')
                check(page.locator('svg [data-series=a]').count()==1 and page.locator('svg [data-series=b]').get_attribute('stroke-dasharray') and page.locator('svg circle').count()==1 and page.locator('svg rect').count()==2,'shared axes and redundant trajectory/end patterns')
                check('Diferença B − A' in page.locator('[data-comparison-result]').inner_text(),'numeric comparison results visible')
                act('seen'); act('practice'); check(snap()['learning']['progress']['steps'][discovery]=='practiced','explicit experiment practice saved')
            page.screenshot(path=str(OUT/'mobile-discovery.png'),full_page=True)
            saved=snap()['learning']['progress']; scenario=snap()['state']; act('reset'); check(snap()['learning']['progress']==saved,'field reset preserves learning')
            act('restart-progress'); act('cancel-restart'); check(snap()['learning']['progress']==saved,'reset cancel preserves progress')
            check(page.evaluate("writes.every(k=>k==='jpwealth_capital_field_v1')"),'learning writes isolated before reload')
            page.add_init_script("window.writes=[];const originalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){writes.push(k);return originalSet.call(this,k,v)}")
            page.reload(); page.evaluate("window.ctl=JPWCapitalCurrents.activate(document.getElementById('host'))"); check(snap()['learning']['progress']==saved and snap()['state']=={'q':0,'p':0,'t':0},'reload restores progress only')
            act('continue-learning'); check(snap()['learning']['id']=='intro-field','completed learning may review all')
            act('restart-progress'); before=snap(); act('confirm-restart'); check(snap()['learning']['progress']['steps']=={} and snap()['state']==before['state'] and snap()['params']==before['params'],'confirmed progress reset only')
            act('skip');check(snap()['learning']['progress']['steps'].get('intro-field')=='skipped','explicit skip records skipped distinctly');act('learn')
            # A foreign visible modal and conflict must block all completion and stepping.
            act('seen'); old=snap(); page.evaluate("let modal=document.createElement('section');modal.setAttribute('role','dialog');modal.textContent='Foreign dialog';document.body.append(modal);window.foreign=modal")
            page.wait_for_timeout(50); page.evaluate("document.querySelector('[data-action=step]').click();document.querySelector('[data-action=seen]').click()")
            check(snap()['state']==old['state'] and snap()['learning']['progress']==old['learning']['progress'],'foreign modal blocks stepping and progress');page.evaluate('foreign.remove()')
            other=ctx.new_page();other.goto(f'http://127.0.0.1:{server.server_port}/'); other.evaluate("localStorage.setItem('jpwealth_capital_field_v1',JSON.stringify({version:1,steps:{'intro-depth':'seen'}}))")
            page.wait_for_timeout(80); check(snap()['learning']['conflict'] and not snap()['running'],'different-tab storage event suspends learning')
            act('reread');check(not snap()['learning']['conflict'] and snap()['learning']['progress']['steps']=={'intro-depth':'seen'},'explicit reread selects stored IDs without merging');other.close()
            page.evaluate("window.dispatchEvent(new StorageEvent('storage',{key:JPWCapitalCurrents.progress.KEY,newValue:localStorage.getItem(JPWCapitalCurrents.progress.KEY)}))")
            check(snap()['learning']['conflict'],'same-value key event still conflicts');act('reread')
            page.evaluate("window.dispatchEvent(new StorageEvent('storage',{key:'jpwealth_capital_currents_v1'}))");check(not snap()['learning']['conflict'],'old key event irrelevant')
            # A save whose readback differs must suspend further writes until reread.
            act('learn');page.evaluate("() => {window.beforeConflictSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){beforeConflictSet.call(this,k,JSON.stringify({version:1,steps:{'intro-pressure':'skipped'}}))};}")
            act('seen');check(snap()['learning']['conflict'] and snap()['learning']['suspended'] and not snap()['running'],'unconfirmed readback suspends flow');page.evaluate('() => {Storage.prototype.setItem=beforeConflictSet;}');act('reread')
            # Getter and quota failures keep RAM progress without claiming durable save.
            page.evaluate("window.storageRef=localStorage;Object.defineProperty(window,'localStorage',{configurable:true,get(){throw Error('denied')}})")
            act('reread');act('learn');act('seen');check(snap()['learning']['storageMode']=='temporary' and snap()['learning']['progress']['steps']['intro-field']=='seen' and 'Somente nesta sessão' in page.locator('[data-learning-storage]').inner_text(),'denied read permits clearly labelled RAM progress')
            page.evaluate("Object.defineProperty(window,'localStorage',{configurable:true,value:storageRef})");act('reread')
            page.evaluate("() => {window.realSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error('quota')};}")
            act('learn');act('seen');check(snap()['learning']['storageMode']=='temporary' and snap()['learning']['progress']['steps']['intro-field']=='seen','quota keeps local candidate');page.evaluate('() => {Storage.prototype.setItem=realSet;}')
            # Preserve malformed bytes until the dedicated explicit restart confirmation.
            page.evaluate("storageRef.setItem('jpwealth_capital_field_v1','incompatible-bytes')");act('reread');act('learn');page.evaluate("document.querySelector('[data-action=seen]').click()")
            check(snap()['learning']['storageMode']=='incompatible' and page.evaluate("storageRef.getItem('jpwealth_capital_field_v1')")=='incompatible-bytes','incompatible bytes preserved')
            act('restart-progress');page.evaluate("window.dispatchEvent(new StorageEvent('storage',{key:null}))");act('reread');check(page.locator('[data-action=confirm-restart]').count()==0,'reread cancels stale reset confirmation');act('restart-progress');act('confirm-restart');check(snap()['learning']['storageMode']=='ok' and page.evaluate("JSON.parse(storageRef.getItem('jpwealth_capital_field_v1')).version===1"),'explicit restart can replace incompatible bytes')
            page.evaluate("window.stale=ctl;ctl.destroy();window.dispatchEvent(new StorageEvent('storage',{key:null}));window.dispatchEvent(new Event('blur'))")
            check(page.evaluate('stale.snapshot().destroyed && !stale.snapshot().learning.conflict'),'disposed storage listener cannot resurrect')
            check(page.evaluate("writes.every(k=>k==='jpwealth_capital_field_v1') && storageRef.getItem('jpwealth_capital_currents_v1')==='synthetic-preserve' && storageRef.getItem('jpw_financial_sentinel')==='synthetic-preserve'"),'only new learning key may be written')
            check(not errors,'browser errors: '+repr(errors))
            browser.close(); print('PASS capital field browser: desktop/mobile, math, controls, focus, lifecycle, storage isolation; screenshots '+str(OUT))
    finally: server.shutdown(); server.server_close()
if __name__=='__main__': main()

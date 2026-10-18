#!/usr/bin/env python3
"""Functional renderer proof. A missing runtime must fail before vendor/port code exists.
No runtime diagnostics are required: observe canvas, projected DOM labels, callbacks,
resource scheduling, actual pointer interaction, and a file:// fixture offline.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback
import subprocess
from playwright.sync_api import sync_playwright
from PIL import Image
import io

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'src/vendor/aisol-dot-globe/aisol-globe.iife.js'
MARKERS = [dict(id='sao-paulo',venueIds=['B3'],lat=-23.5505,lng=-46.6333,label='São Paulo',phase='OPEN',color='#ff9955'),
           dict(id='london',venueIds=['LSE'],lat=51.5074,lng=-.1278,label='London',phase='CLOSED',color='#66ddee'),
           dict(id='tokyo',venueIds=['TSE'],lat=35.6762,lng=139.6503,label='Tokyo',phase='OPEN',color='#ffdd88')]


def run(args):
    out = (ROOT / args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    fixture = out / 'engine-fixture.html'
    fixture.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#06090d}#host{width:600px;height:600px;position:relative}</style>'
                       '<div id="host"></div><script src="'+BUNDLE.as_uri()+'"></script>')
    result = dict(case=args.case, bundle=str(BUNDLE), bundleSHA256=hashlib.sha256(BUNDLE.read_bytes()).hexdigest() if BUNDLE.exists() else None, checks=[], errors=[], network=[], screenshots=[], viewport=[800,700],DPR=1)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'),headless=True,
                  args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx = browser.new_context(viewport={'width':800,'height':700},device_scale_factor=1, service_workers='block')
        ctx.set_offline(True)
        ctx.add_init_script('''window.__frames=0;window.__pending=new Set();
          const raf=window.requestAnimationFrame.bind(window), caf=window.cancelAnimationFrame.bind(window);
          window.requestAnimationFrame=fn=>{let id=raf(t=>{__pending.delete(id);__frames++;fn(t)});__pending.add(id);return id};
          window.cancelAnimationFrame=id=>{__pending.delete(id);return caf(id)};
          window.__registered=[];const add=EventTarget.prototype.addEventListener,remove=EventTarget.prototype.removeEventListener;
          EventTarget.prototype.addEventListener=function(type,fn,options){if(!__registered.some(x=>x.target===this&&x.type===type&&x.fn===fn))__registered.push({target:this,type,fn});return add.call(this,type,fn,options)};
          EventTarget.prototype.removeEventListener=function(type,fn,options){__registered=__registered.filter(x=>!(x.target===this&&x.type===type&&x.fn===fn));return remove.call(this,type,fn,options)};
          window.__gpu=[];window.__contexts=[];const getContext=HTMLCanvasElement.prototype.getContext;
          HTMLCanvasElement.prototype.getContext=function(type,...args){const gl=getContext.call(this,type,...args);if(gl&&type==='webgl2'&&!gl.__tracked){gl.__tracked=true;const counts={},sets=[];__gpu.push(counts);__contexts.push(gl);add.call(this,'webglcontextlost',()=>{for(const live of sets)live.clear();for(const key of Object.keys(counts))counts[key]=0});
            for(const type of ['Buffer','Program','Shader','Texture','Framebuffer','Renderbuffer','VertexArray']){counts[type]=0;const create=gl['create'+type].bind(gl),del=gl['delete'+type].bind(gl);const live=new Set();sets.push(live);gl['create'+type]=(...a)=>{const obj=create(...a);if(obj){live.add(obj);counts[type]=live.size}return obj};gl['delete'+type]=obj=>{live.delete(obj);counts[type]=live.size;return del(obj)};}}
            return gl};''')
        page = ctx.new_page()
        page.on('pageerror',lambda e: result['errors'].append(str(e)))
        page.on('console',lambda m: result['errors'].append(m.text) if m.type=='error' and 'ERR_FILE_NOT_FOUND' not in m.text else None)
        page.on('request',lambda r: result['network'].append(r.url) if r.url.startswith(('http:','https:')) else None)
        try:
            page.goto(fixture.as_uri())
            assert page.evaluate('!!window.JPWAisolGlobeRuntime && typeof JPWAisolGlobeRuntime.create==="function"'), 'PRODUCT_FAIL: Aisol local renderer factory absent'
            result['checks'].append('factory present (offline file)')
            page.evaluate('''markers=>{window.selected=[];window.rendererErrors=[];window.ctl=JPWAisolGlobeRuntime.create(document.querySelector('#host'),{
              markers,onSelectMarker:id=>selected.push(id),onError:e=>rendererErrors.push(String(e)),
              look:{density:65}, motion:{autoRotate:false,startLng:-20,tilt:18}})}''',MARKERS)
            page.wait_for_function('document.querySelector("#host canvas") && document.querySelector("#host canvas").width>0')
            page.wait_for_timeout(150)
            result['renderer']=page.evaluate('''()=>{const gl=document.querySelector('#host canvas').getContext('webgl2');const ext=gl.getExtension('WEBGL_debug_renderer_info');return ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)}''')
            assert page.evaluate('typeof THREE==="undefined" && typeof React==="undefined" && typeof Framer==="undefined"')
            result['checks'].append('Three encapsulated; no React/Framer globals')
            canvas=page.locator('#host canvas')
            def shot(name):
                path=out/name
                data=canvas.screenshot(path=str(path))
                result['screenshots'].append(str(path.relative_to(ROOT)))
                return data
            initial=shot('engine-dark.png')
            im=Image.open(io.BytesIO(initial)).convert('RGB')
            # A sphere needs thousands of lit pixels, while corners stay dark.
            points=sum(1 for x in range(600) for y in range(600) if max(im.getpixel((x,y)))>45)
            assert points>3000, f'PRODUCT_FAIL: blank/non-spherical canvas ({points} lit pixels)'
            assert max(im.getpixel((3,3)))<25
            result['checks'].append(f'real sphere pixels: {points}')
            for marker in MARKERS:
                page.evaluate('id=>ctl.focusMarker(id,{animate:false})',marker['id'])
                page.wait_for_timeout(80)
                label=page.locator('[data-marker-id="'+marker['id']+'"]')
                assert label.count()==1 and label.inner_text()==marker['label']
                assert label.evaluate('e=>getComputedStyle(e).opacity')!='0', f"front marker hidden: {marker['id']}"
                assert page.evaluate('selected.length')==0, 'focusMarker emitted selection callback'
                shot('city-'+marker['id']+'.png')
            result['checks'].append('three city markers project visibly; programmatic focus has no selection callback')
            # Focus places marker at central longitude; the label carries the marker center.
            pos=page.locator('[data-marker-id="tokyo"]').evaluate('e=>({x:parseFloat(e.style.left),y:parseFloat(e.style.top)})')
            page.mouse.click(pos['x'],pos['y'])
            assert page.evaluate('selected')==[{'markerId':'tokyo','source':'pointer'}], 'PRODUCT_FAIL: actual marker click must select once'
            before=canvas.screenshot()
            page.mouse.move(250,300);page.mouse.down();page.mouse.move(430,310,steps=8);page.mouse.up()
            page.wait_for_timeout(120)
            after=shot('engine-after-drag.png')
            assert hashlib.sha256(before).digest()!=hashlib.sha256(after).digest(), 'PRODUCT_FAIL: pointer drag did not rotate sphere'
            assert page.evaluate('selected')==[{'markerId':'tokyo','source':'pointer'}], 'drag incorrectly selected marker'
            result['checks'].append('real pointer selection and drag rotation without accidental selection')
            page.evaluate('ctl.setActive(false)')
            page.wait_for_timeout(50)
            frames=page.evaluate('__frames')
            page.wait_for_timeout(100)
            assert page.evaluate('__frames')==frames and page.evaluate('__pending.size')==0
            result['checks'].append('setActive(false) cancels RAF')
            page.evaluate('ctl.update({markers:[],selectedMarkerId:null,theme:"light"});ctl.setActive(true)')
            page.wait_for_timeout(80)
            assert page.locator('[data-marker-id]').count()==0, 'empty dataset restored defaults'
            shot('engine-light-empty.png')
            result['checks'].append('empty markers remain empty; light theme renders')
            page.evaluate('window.oldRoot=document.querySelector(".jpw-aisol-root");window.oldCanvas=document.querySelector("#host canvas");ctl.dispose();ctl.dispose()')
            page.wait_for_timeout(100)
            assert page.locator('#host canvas').count()==0 and page.locator('[data-marker-id]').count()==0
            assert page.evaluate('__pending.size')==0
            assert page.evaluate('__registered.filter(x=>x.target===oldRoot||x.target===oldCanvas).length')==0, 'owned listener remains after dispose'
            gpu=page.evaluate('__gpu');result['gpuAfterDispose']=gpu;result['gpuContextsLost']=page.evaluate('__contexts.map(gl=>gl.isContextLost())');assert all(result['gpuContextsLost'])
            assert all(value==0 for counts in gpu for value in counts.values()), gpu
            result['checks'].append('dispose idempotent; canvas/labels/RAF/listeners and tracked GPU objects released')
            assert not page.evaluate('rendererErrors'), page.evaluate('rendererErrors')
            assert not result['errors'], result['errors']
            assert not result['network'], result['network']
            result['checks'].append('offline; zero remote requests; no shader/page errors')
            result['status']='PASS'
            result['browser']=browser.version
        except AssertionError as e:
            result['status']='PRODUCT_FAIL';result['failure']=str(e)
        except Exception as e:
            result['status']='ENVIRONMENT_ERROR';result['failure']=str(e);traceback.print_exc()
        finally:
            ctx.close();browser.close()
    (out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result['status']=='PASS' else 1


def prepare_reference(out,args):
    """Independent oracle: extract raw class straight from frozen original, never engine.js.
    Probe uses engine.js separately; reference and probe are test-only IIFEs.
    """
    source=(ROOT/'src/vendor/aisol-dot-globe/component.original.js').read_text()
    assert hashlib.sha256(source.encode()).hexdigest()=='11208679f0598d6813913d079140f29f620b0a82cc2d27a1ced651b0d67ea7b5'
    head=source[source.index('function _define_property'):source.index('import{jsx')]
    helpers=source[source.index('const MASK_W'):source.index('function describe')]
    engine=source[source.index('const DOT_VERT'):source.index('// ── component')]
    raw='import * as THREE from "three";\n'+head+'\nconst clamp=(v,l,h)=>Math.min(h,Math.max(l,v));\n'+helpers+engine+'\nwindow.AisolReference={GlobeEngine,landDots,toVec,rotate};'
    (out/'reference-raw.js').write_text(raw)
    (out/'extraction-probe.js').write_text('import {landDots,toVec,rotate} from "'+str(ROOT/'src/js/40-app/31-market-hours/aisol/engine.js')+'";window.AisolExtraction={landDots,toVec,rotate};')
    paths=[]
    for name in ['reference-raw','extraction-probe']:
        target=out/(name+'.iife.js')
        subprocess.run([str(args.esbuild_bin),str(out/(name+'.js')),'--bundle','--format=iife','--platform=browser','--target=es2020','--alias:three='+str(args.three_root/'build/three.module.js'),'--outfile='+str(target)],check=True,cwd=ROOT)
        paths.append(target)
    return paths

def extra(args):
    out=(ROOT/args.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    result={'case':args.case,'bundleSHA256':hashlib.sha256(BUNDLE.read_bytes()).hexdigest(),'checks':[],'status':'NOT_RUN','viewport':[800,1250],'DPR':1,'renderer':'Chromium ANGLE SwiftShader (headless)'}
    fixture=out/'extra-fixture.html'
    scripts=[BUNDLE]
    if args.case=='fidelity':scripts += prepare_reference(out,args)
    fixture.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#070A12}#host,#reference{width:600px;height:600px;position:relative}</style><div id="host"></div><div id="reference"></div>'+''.join('<script src="'+p.as_uri()+'"></script>' for p in scripts))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'),headless=True,args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx=browser.new_context(viewport={'width':800,'height':1250},device_scale_factor=1,service_workers='block');ctx.set_offline(True)
        page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(fixture.as_uri())
        try:
            if args.case=='fidelity':
                parity=page.evaluate("""()=>{
                  const result=[];
                  for(const density of [10,55,65,100]){const a=AisolReference.landDots(density),b=AisolExtraction.landDots(density);if(a.length!==b.length||a.some((v,i)=>v!==b[i]))throw Error('landDots differ');result.push({density,dots:a.length/3,maxError:0})}
                  for(const lat of [-89,-23.55,0,35.68,51.51,89])for(const lng of [-179,-74.01,-46.63,0,139.69,179]){
                    const a=AisolReference.toVec(lat,lng),b=AisolExtraction.toVec(lat,lng);if(a.some((v,i)=>v!==b[i]))throw Error('toVec differs');
                    const x=AisolReference.rotate(a,.75,.2),y=AisolExtraction.rotate(b,.75,.2);if(x.some((v,i)=>v!==y[i]))throw Error('rotation differs');}
                  return result;
                }""")
                result['mathParity']=parity;result['checks'].append('exact mask/Fibonacci point arrays at four densities; 36 coordinate/rotation cases identical')
                page.evaluate("""markers=>{
                  const host=document.querySelector('#host');window.ctl=JPWAisolGlobeRuntime.create(host,{markers,motion:{autoRotate:false,startLng:10,tilt:22},look:{density:55}});
                  const root=document.querySelector('#reference'),canvas=document.createElement('canvas'),labels=document.createElement('div');root.append(canvas,labels);
                  canvas.style.width='100%';canvas.style.height='100%';
                  window.ref=new AisolReference.GlobeEngine(canvas,root,labels,canvas.getContext('webgl2',{alpha:true,antialias:true,premultipliedAlpha:true}),()=>{},()=>{});
                  ref.setLook({dot:'#8FA3FF',dotSize:.6,density:55,size:.78,ocean:'#0E1428',oceanOpacity:.85,glow:'#4F6BFF',glowStrength:.6,pin:'#FFB35C',pinSize:1,pulse:true,arcColor:'#FFB35C',arcSpeed:50});
                  ref.setMotion({autoRotate:false,speed:6,drag:true,startLng:10,tilt:22,reduce:false});ref.setData(markers,'off',true);ref.ready();
                }""",[{**m,'color':'#FFB35C'} for m in MARKERS])
                page.wait_for_timeout(200)
                page.add_style_tag(content='#host .adg-label,#reference span{visibility:hidden!important}')
                a=page.locator('#host canvas').screenshot(path=str(out/'adapted-600.png'));b=page.locator('#reference canvas').screenshot(path=str(out/'reference-600.png'))
                from PIL import ImageChops,ImageStat
                aa=Image.open(io.BytesIO(a)).convert('RGB');bb=Image.open(io.BytesIO(b)).convert('RGB');diff=ImageChops.difference(aa,bb);diff.save(out/'difference-600.png')
                mean=sum(ImageStat.Stat(diff).mean)/3
                result['imageMeanAbsoluteError']=mean;result['imageNonzeroPixels']=sum(1 for y in range(diff.height) for x in range(diff.width) if max(diff.getpixel((x,y)))>0)
                assert mean<.05,('appearance differs',mean)
                result['checks'].append('fixed 600x600 DPR1 angle: sphere/density/glow/rim/occlusion mean RGB error <0.05/255')
                for width,height in [(320,320),(480,480),(600,400)]:
                    page.evaluate('dims=>{document.querySelector("#host").style.width=dims[0]+"px";document.querySelector("#host").style.height=dims[1]+"px"}',[width,height]);page.wait_for_timeout(60)
                    page.locator('#host').screenshot(path=str(out/f'adapted-{width}x{height}.png'))
                page.evaluate('ctl.dispose();ref.dispose()')
            else:
                page.evaluate("""markers=>{window.selected=[];window.notices=[];window.ctl=JPWAisolGlobeRuntime.create(document.querySelector('#host'),{markers,onSelectMarker:id=>selected.push(id),onError:e=>notices.push(String(e)),motion:{autoRotate:false}})}""",MARKERS)
                page.evaluate("ctl.focusMarker('tokyo',{animate:false})");page.wait_for_timeout(100)
                if args.case=='secondary-click':
                    pos=page.locator('[data-marker-id="tokyo"]').evaluate('e=>({x:parseFloat(e.style.left),y:parseFloat(e.style.top)})')
                    page.mouse.click(pos['x'],pos['y'],button='right')
                    assert page.evaluate('selected')==[], 'secondary mouse button emitted marker selection'
                    page.mouse.click(pos['x'],pos['y'],button='middle')
                    assert page.evaluate('selected')==[], 'auxiliary mouse button emitted marker selection'
                    page.mouse.click(pos['x'],pos['y'])
                    assert page.evaluate('selected')==[{'markerId':'tokyo','source':'pointer'}], 'primary click stopped selecting once'
                    result['checks'].append('secondary and auxiliary clicks emit nothing; primary click still selects once')
                    page.evaluate('selected=[]')
                if args.case=='lost-focus':
                    page.evaluate("""()=>{window.gl=document.querySelector('#host canvas').getContext('webgl2');window.lose=gl.getExtension('WEBGL_lose_context');lose.loseContext()}""")
                    page.wait_for_function("document.querySelector('.jpw-aisol-root').dataset.state==='fallback'")
                    before=page.locator('.jpw-aisol-fallback path').first.get_attribute('d')
                    assert 'Tokyo' in page.locator('.jpw-aisol-fallback text').all_text_contents()
                    page.evaluate("ctl.focusMarker('london',{animate:false})")
                    assert 'London' in page.locator('.jpw-aisol-fallback text').all_text_contents(), 'focus during loss did not move fallback to London'
                    assert before!=page.locator('.jpw-aisol-fallback path').first.get_attribute('d'), 'fallback projection unchanged after focus during loss'
                    page.evaluate('ctl.update({theme:"light"});lose.restoreContext()')
                    page.wait_for_function("document.querySelector('.jpw-aisol-root').dataset.state==='ready'")
                    label=page.locator('[data-marker-id="london"]')
                    assert label.evaluate('e=>getComputedStyle(e).visibility')=='visible', 'restored WebGL lost pending city focus'
                    assert abs(float(label.evaluate('e=>parseFloat(e.style.left)'))-300)<1 and abs(float(label.evaluate('e=>parseFloat(e.style.top)'))-300)<1, 'restored city is not centered'
                    assert page.evaluate('selected')==[], 'programmatic focus during loss emitted selection'
                    result['checks'].append('focus during loss updates native projection; restore and theme update preserve focused city without callback')
                    page.evaluate("ctl.focusMarker('tokyo',{animate:false})")
                    # Even animate:false projects labels on the next RAF. A
                    # restored software renderer need not draw within 50ms.
                    # Wait for the requested city, retaining the rear-picking
                    # assertions below and a bounded failure if focus is lost.
                    page.wait_for_function("()=>{const e=document.querySelector('[data-marker-id=tokyo]');return e && getComputedStyle(e).visibility==='visible' && Math.abs(parseFloat(e.style.left)-300)<1 && Math.abs(parseFloat(e.style.top)-300)<1}",timeout=2500)
                # Projected back marker cannot be selected at its hidden label center.
                back=page.locator('[data-marker-id="sao-paulo"]');assert back.evaluate('e=>getComputedStyle(e).visibility')=='hidden'
                pos=back.evaluate('e=>({x:parseFloat(e.style.left),y:parseFloat(e.style.top)})');page.mouse.click(pos['x'],pos['y']);assert page.evaluate('selected.length')==0
                result['checks'].append('rear hemisphere cannot select')
                # Snapshot rejects invalid update before changing the existing renderer.
                assert page.evaluate("""()=>{try{ctl.update({markers:[{id:'bad',lat:NaN,lng:0}]});return false}catch{return true}}""")
                assert page.locator('[data-marker-id]').count()==3
                page.evaluate("""()=>{ctl.update({markers:[{id:'hostile',lat:0,lng:0,label:'<img src=x onerror=alert(1)>',color:'#ffaa00'}]});ctl.focusMarker('hostile',{animate:false})}""")
                assert page.locator('#host img').count()==0;assert page.locator('[data-marker-id="hostile"]').inner_text()=='<img src=x onerror=alert(1)>'
                result['checks'].append('invalid coordinates rejected atomically; hostile label stays text')
                page.evaluate("ctl.update({markers:[{id:'unlabelled',lat:0,lng:0,label:''},{id:'labelled',lat:10,lng:10,label:'Visible'}]})")
                assert page.locator('[data-marker-id="labelled"]').count()==1 and page.locator('[data-marker-id="unlabelled"]').count()==0, 'empty label misassigned city ID'
                result['checks'].append('optional empty labels preserve city identity')
                page.evaluate("""()=>{window.gl=document.querySelector('#host canvas').getContext('webgl2');window.lose=gl.getExtension('WEBGL_lose_context');lose.loseContext()}""")
                page.wait_for_function("document.querySelector('.jpw-aisol-root').dataset.state==='fallback'")
                assert page.locator('.jpw-aisol-fallback').count()==1
                page.evaluate('ctl.update({markers:[],theme:"light"});lose.restoreContext()')
                page.wait_for_function("document.querySelector('.jpw-aisol-root').dataset.state==='ready'")
                assert page.locator('#host canvas').count()==1 and page.locator('[data-marker-id]').count()==0
                result['checks'].append('actual WebGL context loss and one restore preserve latest snapshot')
                page.evaluate('ctl.dispose()');page.wait_for_timeout(50)
                # Force unavailable WebGL using browser boundary injection, exercising real native fallback.
                page.evaluate("""()=>{const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(name,...rest){return name==='webgl2'?null:original.call(this,name,...rest)};}""")
                page.evaluate("""markers=>{window.fallback=JPWAisolGlobeRuntime.create(document.querySelector('#host'),{markers,motion:{autoRotate:false},onError:()=>{}})}""",MARKERS)
                assert page.locator('.jpw-aisol-fallback').count()==1 and page.locator('.jpw-aisol-root').get_attribute('data-state')=='fallback'
                page.locator('#host').screenshot(path=str(out/'no-webgl-fallback.png'))
                page.evaluate('fallback.dispose();fallback.dispose()');assert page.locator('.jpw-aisol-root').count()==0
                result['checks'].append('native SVG without WebGL2 and idempotent fallback dispose')
            assert not errors,errors
            result['status']='PASS';result['browser']=browser.version
        except AssertionError as e:result['status']='PRODUCT_FAIL';result['failure']=str(e)
        except Exception as e:result['status']='PRODUCT_FAIL';result['failure']=str(e);traceback.print_exc()
        finally:ctx.close();browser.close()
    (out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,indent=2,ensure_ascii=False));return 0 if result['status']=='PASS' else 1


def labels(args):
    """Opt-in collision policy observes DOM boxes and real pin clicks, not engine state."""
    out=(ROOT/args.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    fixture=out/'labels-fixture.html'
    fixture.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#070A12}#host{width:600px;height:600px;position:relative}</style><div id="host"></div><script src="'+BUNDLE.as_uri()+'"></script>')
    result={'case':'labels','bundleSHA256':hashlib.sha256(BUNDLE.read_bytes()).hexdigest(),'checks':[],'snapshots':[],'status':'NOT_RUN','DPR':1}
    markers=[dict(id=id,label=name,lat=lat,lng=lng,color='#ff9955') for id,name,lat,lng in [
        ('london','Londres',51.5074,-.1278),('paris','Paris',48.8566,2.3522),
        ('frankfurt','Frankfurt',50.1109,8.6821),('zurich','Zurique',47.3769,8.5417)]]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'),headless=True,args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx=browser.new_context(viewport={'width':800,'height':700},device_scale_factor=1,service_workers='block');ctx.set_offline(True)
        ctx.add_init_script("window.labelReads=0;const box=Element.prototype.getBoundingClientRect;Element.prototype.getBoundingClientRect=function(...args){if(this.classList.contains('adg-label'))labelReads++;return box.apply(this,args)}")
        page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(fixture.as_uri())
        def snapshot(name,selected,clean=True):
            data=page.evaluate("""()=>{const host=document.querySelector('#host').getBoundingClientRect();return {width:host.width,height:host.height,labels:[...document.querySelectorAll('[data-marker-id]')].map(el=>{const r=el.getBoundingClientRect();return {id:el.dataset.markerId,visible:getComputedStyle(el).visibility==='visible',x:r.x-host.x,y:r.y-host.y,w:r.width,h:r.height,pinX:parseFloat(el.style.left),pinY:parseFloat(el.style.top)}})}}""")
            visible=[l for l in data['labels'] if l['visible']]
            collisions=[(a['id'],b['id']) for i,a in enumerate(visible) for b in visible[i+1:] if a['x']<b['x']+b['w'] and a['x']+a['w']>b['x'] and a['y']<b['y']+b['h'] and a['y']+a['h']>b['y']]
            result['snapshots'].append({'name':name,**data,'collisions':collisions})
            page.locator('#host').screenshot(path=str(out/(name+'.png')))
            assert len(data['labels'])==4, 'declutter removed marker labels/identity'
            assert any(l['id']==selected for l in visible), 'selected city label was hidden'
            if clean:
                assert not collisions, 'visible city labels overlap: '+str(collisions)
                assert all(l['x']>=0 and l['y']>=0 and l['x']+l['w']<=data['width']+.01 and l['y']+l['h']<=data['height']+.01 for l in visible), 'visible label exceeds host bounds'
            return data,collisions
        try:
            page.evaluate("""markers=>{window.markers=markers;window.selected=[];window.ctl=JPWAisolGlobeRuntime.create(document.querySelector('#host'),{markers,selectedMarkerId:'paris',motion:{autoRotate:false}});ctl.focusMarker('paris',{animate:false})}""",markers)
            page.wait_for_timeout(80)
            data,collisions=snapshot('default-600','paris',False)
            assert all(l['visible'] for l in data['labels']) and collisions, 'default label behavior changed'
            result['checks'].append('default false preserves original four visible overlapping labels')
            page.evaluate("""()=>{ctl.dispose();window.ctl=JPWAisolGlobeRuntime.create(document.querySelector('#host'),{markers,selectedMarkerId:'paris',declutterLabels:true,motion:{autoRotate:false},onSelectMarker:event=>{selected.push(event);ctl.update({selectedMarkerId:event.markerId})}});ctl.focusMarker('paris',{animate:false})}""")
            page.wait_for_timeout(80)
            data,_=snapshot('declutter-600','paris')
            hidden=[l for l in data['labels'] if not l['visible'] and l['id']!='paris']
            assert hidden, 'close secondary labels were not hidden'
            target=hidden[0]
            page.mouse.click(target['pinX'],target['pinY']);page.wait_for_timeout(60)
            assert page.evaluate('selected')==[{'markerId':target['id'],'source':'pointer'}], 'hidden label prevented selecting its pin'
            snapshot('selected-hidden-pin-600',target['id'])
            result['checks'].append('600px selected Paris wins; hidden secondary pin still emits exact city callback and becomes visible')
            page.evaluate("document.querySelector('#host').style.width='310px';document.querySelector('#host').style.height='310px'")
            page.wait_for_timeout(100);snapshot('declutter-310',target['id'])
            page.evaluate('labelReads=0')
            page.locator('.jpw-aisol-root').focus();page.keyboard.press('ArrowUp');page.wait_for_timeout(180)
            assert page.evaluate('labelReads')==0, 'rotation reread cached label dimensions'
            snapshot('rotated-310',target['id'])
            page.evaluate('labelReads=0;document.fonts.dispatchEvent(new Event("loadingdone"))')
            page.wait_for_timeout(80)
            assert page.evaluate('labelReads')==4, 'font loading did not invalidate each label dimension once'
            page.evaluate("document.querySelector('#host').style.width='600px';document.querySelector('#host').style.height='400px'")
            page.wait_for_timeout(100);snapshot('resized-600x400',target['id'])
            result['checks'].append('310px mobile, keyboard rotation and 600x400 resize keep visible labels nonoverlapping and inside bounds')
            result['checks'].append('rotation reuses cached dimensions; font loading invalidates all four labels exactly once')
            page.evaluate('ctl.dispose();labelReads=0;document.fonts.dispatchEvent(new Event("loadingdone"))');page.wait_for_timeout(60)
            assert page.evaluate('labelReads')==0 and page.locator('.jpw-aisol-root').count()==0, 'font listener remains active after disposal'
            assert not errors,errors
            result['status']='PASS';result['browser']=browser.version
        except AssertionError as e:result['status']='PRODUCT_FAIL';result['failure']=str(e)
        except Exception as e:result['status']='ENVIRONMENT_ERROR';result['failure']=str(e);traceback.print_exc()
        finally:ctx.close();browser.close()
    (out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,indent=2,ensure_ascii=False));return 0 if result['status']=='PASS' else 1


def zoom(args):
    """Physical pointer and label boxes must agree with the renderer's local CSS units."""
    out=(ROOT/args.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    fixture=out/'zoom-fixture.html'
    fixture.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#070A12}#host{margin:17px;width:600px;height:600px;position:relative}</style><div id="host"></div><script src="'+BUNDLE.as_uri()+'"></script>')
    result={'case':args.case,'bundleSHA256':hashlib.sha256(BUNDLE.read_bytes()).hexdigest(),'checks':[],'observations':[],'status':'NOT_RUN','DPR':1}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'),headless=True,args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx=browser.new_context(viewport={'width':1500,'height':1500},device_scale_factor=1,service_workers='block',reduced_motion='reduce',has_touch=True);ctx.set_offline(True)
        page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(fixture.as_uri())
        try:
            if args.case=='zoom-picking':
                for width in [600,310]:
                    for scale in [1,.8,1.25,2]:
                        page.evaluate("""({width,scale})=>{window.ctl?.dispose();document.documentElement.style.zoom=scale;const host=document.querySelector('#host');host.style.width=width+'px';host.style.height=width+'px';window.hits=[];window.ctl=JPWAisolGlobeRuntime.create(host,{markers:[{id:'b3',label:'São Paulo',lat:-23.55,lng:-46.63,color:'#ff9955'}],selectedMarkerId:'b3',declutterLabels:true,motion:{autoRotate:false},onSelectMarker:e=>hits.push(e)});ctl.focusMarker('b3',{animate:false})}""",{'width':width,'scale':scale})
                        page.wait_for_timeout(100)
                        box=page.locator('.jpw-aisol-root').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
                        page.mouse.click(x,y);page.wait_for_timeout(35)
                        hits=page.evaluate('hits');result['observations'].append({'width':width,'zoom':scale,'physicalRootBox':box,'centerClick':hits})
                        assert hits==[{'markerId':'b3','source':'pointer'}], 'physical pin center did not select exactly once at zoom '+str(scale)
                        page.evaluate('hits=[]');page.mouse.click(x+15*scale,y)
                        assert page.evaluate('hits')==[{'markerId':'b3','source':'pointer'}], 'inside 16 local CSS px threshold was rejected'
                        page.evaluate('hits=[]');page.mouse.click(x+17*scale,y)
                        assert page.evaluate('hits')==[], 'outside 16 local CSS px threshold selected pin'
                        page.mouse.click(x,y,button='right');page.mouse.click(x,y,button='middle')
                        assert page.evaluate('hits')==[], 'non-primary gesture selected pin at zoom'
                        if width==310:
                            page.touchscreen.tap(x,y);assert page.evaluate('hits')==[{'markerId':'b3','source':'pointer'}], 'mobile native touch tap did not select pin at zoom'
                            page.evaluate('hits=[]')
                        # A real drag still rotates, without becoming a click.
                        before=page.locator('[data-marker-id="b3"]').evaluate('e=>e.style.left')
                        page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+35*scale,y,steps=5);page.wait_for_timeout(120);page.mouse.up();page.wait_for_timeout(35)
                        assert page.evaluate('hits')==[], 'drag emitted marker selection at zoom'
                        assert page.locator('[data-marker-id="b3"]').evaluate('e=>e.style.left')!=before, 'drag stopped rotating at zoom'
                        if width==310:
                            page.evaluate("ctl.focusMarker('b3',{animate:false});hits=[]");page.wait_for_timeout(50)
                            before=page.locator('[data-marker-id="b3"]').evaluate('e=>e.style.left')
                            touch=ctx.new_cdp_session(page)
                            touch.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y,'id':1}]})
                            for step in range(1,6):touch.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+35*scale*step/5,'y':y,'id':1}]})
                            page.wait_for_timeout(120);touch.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});touch.detach();page.wait_for_timeout(35)
                            assert page.evaluate('hits')==[], 'native mobile touch drag emitted selection'
                            assert page.locator('[data-marker-id="b3"]').evaluate('e=>e.style.left')!=before, 'native mobile touch drag stopped rotating'
                        # Focusing the antipode hides the only pin; clicking the projected center cannot select it.
                        page.evaluate("ctl.update({markers:[{id:'b3',label:'São Paulo',lat:-23.55,lng:-46.63},{id:'front',label:'',lat:23.55,lng:133.37}]});ctl.focusMarker('front',{animate:false});ctl.update({markers:[{id:'b3',label:'São Paulo',lat:-23.55,lng:-46.63}]});hits=[]")
                        page.wait_for_timeout(50)
                        assert page.locator('[data-marker-id="b3"]').evaluate('e=>getComputedStyle(e).visibility')=='hidden'
                        page.mouse.click(x,y);assert page.evaluate('hits')==[], 'rear hemisphere pin selected at zoom'
                        result['checks'].append(str(width)+'px zoom '+str(scale)+': center/16px local threshold/primary gesture/drag/occlusion')
            else:
                def boxes(name):
                    data=page.evaluate("""()=>{const host=document.querySelector('#host').getBoundingClientRect();return {host:{x:host.x,y:host.y,w:host.width,h:host.height},labels:[...document.querySelectorAll('[data-marker-id]')].filter(el=>getComputedStyle(el).visibility==='visible').map(el=>{const b=el.getBoundingClientRect();return {id:el.dataset.markerId,x:b.x,y:b.y,w:b.width,h:b.height}})}}""")
                    result['observations'].append({'name':name,**data});visible=data['labels'];host=data['host']
                    assert any(l['id']=='paris' for l in visible), 'selected Paris hidden at zoom'
                    collisions=[(a['id'],b['id']) for i,a in enumerate(visible) for b in visible[i+1:] if a['x']<b['x']+b['w'] and a['x']+a['w']>b['x'] and a['y']<b['y']+b['h'] and a['y']+a['h']>b['y']]
                    assert not collisions, 'scaled visible labels overlap: '+str(collisions)
                    assert all(l['x']>=host['x']-.02 and l['y']>=host['y']-.02 and l['x']+l['w']<=host['x']+host['w']+.02 and l['y']+l['h']<=host['y']+host['h']+.02 for l in visible), 'scaled label exceeds root bounds'
                    page.locator('#host').screenshot(path=str(out/(name+'.png')))
                for width in [600,310]:
                    for scale in [.8,1.25,2]:
                        # Nearby synthetic parallel is chosen to expose a CSS-unit mix at zoom .8.
                        nearby=45.4566 if width==600 else 43.6766
                        page.evaluate("""({width,scale,nearby})=>{window.ctl?.dispose();document.documentElement.style.zoom=scale;const host=document.querySelector('#host');host.style.width=width+'px';host.style.height=width+'px';window.ctl=JPWAisolGlobeRuntime.create(host,{markers:[{id:'paris',label:'Paris',lat:48.8566,lng:2.3522},{id:'nearby',label:'Nearby synthetic',lat:nearby,lng:2.3522}],selectedMarkerId:'paris',declutterLabels:true,motion:{autoRotate:false}});ctl.focusMarker('paris',{animate:false})}""",{'width':width,'scale':scale,'nearby':nearby})
                        page.wait_for_timeout(80);boxes('nearby-'+str(width)+'-zoom-'+str(scale))
                        page.evaluate("ctl.update({markers:[{id:'london',label:'Londres',lat:51.5074,lng:-.1278},{id:'paris',label:'Paris',lat:48.8566,lng:2.3522},{id:'frankfurt',label:'Frankfurt',lat:50.1109,lng:8.6821},{id:'zurich',label:'Zurique',lat:47.3769,lng:8.5417}]})")
                        page.wait_for_timeout(60);boxes('europe-'+str(width)+'-zoom-'+str(scale))
                        # Zoom changes after mounting must not poison cached local dimensions.
                        page.evaluate('document.documentElement.style.zoom=1');page.wait_for_timeout(60);boxes('zoom-reset-'+str(width)+'-from-'+str(scale))
                        result['checks'].append(str(width)+'px zoom '+str(scale)+': selected/nearby pair/Europe/bounds/live zoom reset')
            page.evaluate('ctl.dispose()');assert not errors,errors
            result['status']='PASS';result['browser']=browser.version
        except AssertionError as e:result['status']='PRODUCT_FAIL';result['failure']=str(e)
        except Exception as e:result['status']='ENVIRONMENT_ERROR';result['failure']=str(e);traceback.print_exc()
        finally:ctx.close();browser.close()
    (out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,indent=2,ensure_ascii=False));return 0 if result['status']=='PASS' else 1


def noon_adapter(args):
    """Approved geographic/interaction contract, observed through projection and DOM events.

    Rejects a full-turn longitude interpolation, fabricated selection/pins, non-atomic
    coordinates, lost pointer phases, keyboard no-ops and an observer breaking controls.
    No engine state or production diagnostic API is exposed to this test.
    """
    out=(ROOT/args.out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    fixture=out/'noon-adapter-fixture.html'
    fixture.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#070A12}#host{width:600px;height:600px;position:relative}</style><div id="host"></div><script src="'+BUNDLE.as_uri()+'"></script>')
    result={'case':args.case,'bundleSHA256':hashlib.sha256(BUNDLE.read_bytes()).hexdigest(),'checks':[],'observations':[],'cases':[],'status':'NOT_RUN','DPR':1}
    markers=[dict(id='anchor',label='Anchor',lat=0,lng=0),dict(id='date-line',label='Date line',lat=0,lng=180),dict(id='east',label='East',lat=35,lng=90)]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'),headless=True,args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx=browser.new_context(viewport={'width':800,'height':700},device_scale_factor=1,service_workers='block');ctx.set_offline(True)
        page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(fixture.as_uri())
        def mount(**overrides):
            page.emulate_media(reduced_motion='no-preference')
            page.evaluate("""({markers,overrides})=>{window.ctl?.dispose();window.interactions=[];window.selections=[];window.observerThrows=false;window.ctl=JPWAisolGlobeRuntime.create(document.querySelector('#host'),{markers,selectedMarkerId:'anchor',motion:{autoRotate:false,startLng:0,tilt:0},onSelectMarker:e=>selections.push(e),onInteraction:e=>{interactions.push(e);if(observerThrows)throw Error('synthetic observer failure')},...overrides})}""",{'markers':markers,'overrides':overrides})
            page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        def point(id='anchor'):
            return page.locator('[data-marker-id="'+id+'"]').evaluate("e=>({x:parseFloat(e.style.left),y:parseFloat(e.style.top),visible:getComputedStyle(e).visibility==='visible'})")
        def check(name,fn):
            try:
                fn();result['cases'].append({'id':name,'status':'PASS'});result['checks'].append(name)
            except Exception as e:
                result['cases'].append({'id':name,'status':'PRODUCT_FAIL','failure':str(e)})
            finally:
                page.mouse.up()
        def location():
            mount()
            assert page.evaluate("typeof ctl.focusLocation==='function'"), 'geographic focus API absent'
            page.evaluate('ctl.focusLocation({lat:0,lng:45},{animate:false})')
            # Projection is queued on RAF, including animate:false. Wait for a
            # drawn change, then retain the independent exact geometry oracle.
            page.wait_for_function("()=>{const e=document.querySelector('[data-marker-id=anchor]');return Math.abs(parseFloat(e.style.left)-300)>.1}",timeout=2500)
            p=point()
            # 600px host, default radius .78 * 300, pin radius 1.004, 45 degree west.
            assert abs(p['x']-133.87516126)<.1 and abs(p['y']-300)<.1 and p['visible'], p
            assert page.locator('[data-marker-id]').count()==3, 'geographic focus fabricated a city marker'
            assert page.evaluate("document.querySelector('[data-marker-id=anchor]').style.textDecoration")=='underline', 'geographic focus changed selected city'
            assert page.evaluate('selections')==[] and page.evaluate('interactions')==[], 'programmatic focus emitted an interaction/selection'
            before=page.locator('#host').screenshot()
            rejected=page.evaluate("""()=>[null,{}, {lat:NaN,lng:0},{lat:0,lng:Infinity},{lat:'0',lng:0},{lat:91,lng:0},{lat:0,lng:-181}].map(p=>{try{ctl.focusLocation(p,{animate:false});return false}catch{return true}})""")
            assert all(rejected), 'malformed geographic coordinates accepted: '+str(rejected)
            page.wait_for_timeout(40)
            assert page.locator('#host').screenshot()==before, 'rejected geographic focus changed rendered state'
            assert page.evaluate('selections')==[] and page.evaluate('interactions')==[], 'rejected focus emitted callbacks'
            result['observations'].append({'geographic45':p,'rejected':rejected})
        def shortest():
            mount()
            assert page.evaluate("typeof ctl.focusLocation==='function'"), 'geographic focus API absent'
            page.evaluate('ctl.focusLocation({lat:0,lng:179},{animate:false})');page.wait_for_timeout(35)
            samples=page.evaluate("""()=>{const el=document.querySelector('[data-marker-id="date-line"]'),samples=[];ctl.focusLocation({lat:0,lng:-179},{animate:true});return new Promise(resolve=>{function sample(){samples.push({x:parseFloat(el.style.left),y:parseFloat(el.style.top),visible:getComputedStyle(el).visibility==='visible'});if(samples.length>=120 || samples.at(-1).x<295.95)resolve(samples);else requestAnimationFrame(sample)}requestAnimationFrame(sample)})}""")
            assert all(p['visible'] and abs(p['x']-300)<5 for p in samples), 'antimeridian focus took the long angular path: '+str(samples)
            assert samples[-1]['x']<295.95, 'antimeridian animation never reached target: '+str(samples)
            page.emulate_media(reduced_motion='reduce')
            page.wait_for_function("matchMedia('(prefers-reduced-motion: reduce)').matches")
            page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            page.evaluate('ctl.focusLocation({lat:35,lng:90},{animate:true})')
            # First rendered frame must already be at the target; elapsed animation cannot satisfy it.
            page.evaluate('() => new Promise(resolve=>requestAnimationFrame(resolve))')
            p=point('east');assert abs(p['x']-300)<.1 and abs(p['y']-300)<.1 and p['visible'], 'reduced-motion geographic focus was not immediate'
            assert page.evaluate('interactions')==[] and page.evaluate('selections')==[]
            result['observations'].append({'antimeridian':samples,'reduced':p})
        def pointer():
            mount()
            page.mouse.move(300,300);page.mouse.down();page.wait_for_timeout(100)
            events=page.evaluate('interactions')
            assert len(events)==1 and events[0]['type']=='start' and events[0]['pointerType']=='mouse', 'accepted pointerdown did not establish held phase: '+str(events)
            pointer_id=events[0]['pointerId']
            page.mouse.move(345,300,steps=4);page.wait_for_timeout(80)
            assert len(page.evaluate('interactions'))==1, 'held movement prematurely ended interaction'
            page.mouse.up();events=page.evaluate('interactions')
            assert [e['type'] for e in events]==['start','end'] and events[1]['pointerId']==pointer_id and events[1]['cancelled'] is False, events
            assert page.evaluate('selections')==[], 'drag selected a marker'
            page.evaluate('interactions=[]');page.mouse.down()
            page.evaluate("""()=>{const r=document.querySelector('.jpw-aisol-root'),id=interactions[0].pointerId;r.dispatchEvent(new PointerEvent('pointercancel',{bubbles:true,pointerId:id,pointerType:'mouse',clientX:345,clientY:300}))}""")
            events=page.evaluate('interactions');assert [e['type'] for e in events]==['start','end'] and events[1]['cancelled'] is True, events
            page.mouse.up()
            page.evaluate('interactions=[]');page.mouse.down()
            # Let the native pointer capture become active before explicitly losing it.
            page.mouse.move(346,300)
            page.evaluate("""()=>document.querySelector('.jpw-aisol-root').releasePointerCapture(interactions[0].pointerId)""")
            page.mouse.move(350,300)
            page.wait_for_function("interactions.some(e=>e.type==='end')",timeout=2000)
            events=page.evaluate('interactions');assert [e['type'] for e in events]==['start','end'] and events[1]['cancelled'] is True, 'lost capture did not cancel accepted gesture: '+str(events)
            page.mouse.up()
            result['observations'].append({'pointerPhases':events})
            mount(motion={'autoRotate':False,'startLng':0,'tilt':0,'drag':False})
            page.mouse.click(300,300)
            assert page.evaluate('interactions')==[], 'drag-disabled tap invented a manipulation'
            assert page.evaluate('selections')==[{'markerId':'anchor','source':'pointer'}], 'drag-disabled tap lost native selection'
        def keyboard():
            mount();page.locator('.jpw-aisol-root').focus()
            page.keyboard.press('a');page.keyboard.press('Alt+ArrowRight');page.keyboard.press('Control+ArrowLeft');page.keyboard.press('Meta+ArrowLeft');page.keyboard.press('Home')
            prevented=page.evaluate("""()=>{const e=new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true,cancelable:true});e.preventDefault();document.querySelector('.jpw-aisol-root').dispatchEvent(e);return e.defaultPrevented}""")
            assert prevented and page.evaluate('interactions')==[], 'noop/modified/prevented key counted as manipulation'
            page.keyboard.press('ArrowRight')
            assert page.evaluate('interactions')==[{'type':'key','key':'ArrowRight'}], 'accepted native key not reported'
            page.wait_for_function("parseFloat(document.querySelector('[data-marker-id=anchor]').style.left)>300",timeout=2000)
            assert point()['x']>300, 'accepted key no longer rotates native globe'
            page.evaluate('interactions=[];ctl.setActive(false)');before=point()
            page.keyboard.press('ArrowRight');page.keyboard.press('Home');page.evaluate('ctl.setActive(true)');page.wait_for_timeout(80)
            after=point();assert page.evaluate('interactions')==[] and abs(before['x']-after['x'])<.01 and abs(before['y']-after['y'])<.01, 'inactive key mutated orientation for later activation'
            # At the native 60 degree tilt boundary, ArrowUp remains handled but is no manipulation.
            page.keyboard.press('Home')
            for _ in range(9):page.keyboard.press('ArrowUp')
            page.wait_for_timeout(1000);page.evaluate('interactions=[]')
            handled=page.evaluate("""()=>{const e=new KeyboardEvent('keydown',{key:'ArrowUp',bubbles:true,cancelable:true});document.querySelector('.jpw-aisol-root').dispatchEvent(e);return e.defaultPrevented}""")
            assert handled and page.evaluate('interactions')==[], 'clamped key counted or lost native preventDefault'
        def multipointer():
            # The native engine owns one gesture. A second finger cannot replace its
            # accepted start or release its capture/deadline while finger one stays down.
            touch=ctx.new_cdp_session(page)
            active_touches=set()
            def dispatch(kind,points):
                touch.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':[{'id':id,'x':x,'y':300,'radiusX':1,'radiusY':1,'force':1} for id,x in points]})
                if kind=='touchStart':active_touches.update(id for id,_ in points)
                elif kind=='touchEnd':
                    if points:active_touches.difference_update(id for id,_ in points)
                    else:active_touches.clear()
                elif kind=='touchCancel':active_touches.clear()
            def begin():
                mount()
                page.evaluate("""()=>{window.nativePointers=[];const root=document.querySelector('.jpw-aisol-root');for(const type of ['pointerdown','pointermove','pointerup','pointercancel','gotpointercapture','lostpointercapture'])root.addEventListener(type,e=>nativePointers.push({type:e.type,id:e.pointerId,pointerType:e.pointerType}))}""")
                dispatch('touchStart',[(1,280)]);dispatch('touchMove',[(1,281)])
                dispatch('touchStart',[(1,281),(2,340)])
                downs=page.evaluate("nativePointers.filter(e=>e.type==='pointerdown')")
                assert len(downs)==2 and all(e['pointerType']=='touch' for e in downs), 'native two-touch stimulus missing: '+str(downs)
                return downs[0]['id'],downs[1]['id']
            try:
                first,second=begin()
                # Explicitly end the released point; merely omitting it from a move
                # does not release it in this pinned Chromium/CDP implementation.
                dispatch('touchEnd',[(2,340)])
                native=page.evaluate('nativePointers')
                assert any(e['type']=='pointerup' and e['id']==second for e in native), 'CDP did not release the second native pointer: '+str(native)
                while_first_held=page.evaluate('interactions')
                captured=page.evaluate('id=>document.querySelector(".jpw-aisol-root").hasPointerCapture(id)',first)
                before=point()['x'];dispatch('touchMove',[(1,326)])
                page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                after=point()['x'];dispatch('touchEnd',[])
                final=page.evaluate('interactions')
                result['observations'].append({'multipointerSecondReleased':{'first':first,'second':second,'whileFirstHeld':while_first_held,'firstCaptured':captured,'xBefore':before,'xAfter':after,'final':final,'native':page.evaluate('nativePointers')}})
                assert while_first_held==[{'type':'start','pointerId':first,'pointerType':'touch'}], 'second touch orphaned/released the accepted held gesture: '+str(while_first_held)
                assert captured, 'second touch release dropped the accepted first capture'
                assert abs(after-before)>10, 'first held finger stopped rotating after second finger released'
                assert final==[{'type':'start','pointerId':first,'pointerType':'touch'},{'type':'end','pointerId':first,'pointerType':'touch','cancelled':False}], 'native two-touch sequence did not close exactly its accepted start: '+str(final)
                assert page.evaluate('selections')==[], 'two-finger drag selected a marker'
                first,second=begin()
                dispatch('touchEnd',[(1,281)])
                first_up=page.evaluate('interactions')
                dispatch('touchMove',[(2,360)]);dispatch('touchEnd',[])
                expected=[{'type':'start','pointerId':first,'pointerType':'touch'},{'type':'end','pointerId':first,'pointerType':'touch','cancelled':False}]
                assert first_up==expected and page.evaluate('interactions')==expected, 'releasing first touch let the rejected second touch reopen/close a gesture'
                first,second=begin();dispatch('touchCancel',[])
                final=page.evaluate('interactions')
                assert final==[{'type':'start','pointerId':first,'pointerType':'touch'},{'type':'end','pointerId':first,'pointerType':'touch','cancelled':True}], 'two-touch cancel did not close accepted start exactly once: '+str(final)
            finally:
                if active_touches:dispatch('touchCancel',[])
                touch.detach()
        def pending_key():
            mount()
            home=page.evaluate("""()=>{const root=document.querySelector('.jpw-aisol-root');function key(name,extra={}){const e=new KeyboardEvent('keydown',{key:name,bubbles:true,cancelable:true,...extra});if(extra.prePrevented)e.preventDefault();root.dispatchEvent(e);return e.defaultPrevented}ctl.focusLocation({lat:0,lng:0},{animate:false});const idle=key('Home');ctl.focusLocation({lat:35,lng:90},{animate:true});key('a');key('Home',{altKey:true});key('ArrowUp',{ctrlKey:true});key('Home',{metaKey:true});key('Home',{prePrevented:true});const rejected=interactions.slice();const pending=key('Home'),after=interactions.slice();const again=key('Home');return {idle,pending,again,rejected,after,final:interactions.slice()}}""")
            page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            home_point=point()
            mount(motion={'autoRotate':False,'startLng':0,'tilt':60})
            up=page.evaluate("""()=>{const root=document.querySelector('.jpw-aisol-root');function key(){const e=new KeyboardEvent('keydown',{key:'ArrowUp',bubbles:true,cancelable:true});root.dispatchEvent(e);return e.defaultPrevented}ctl.focusLocation({lat:60,lng:0},{animate:false});const idle=key();ctl.focusLocation({lat:0,lng:0},{animate:true});const pending=key(),after=interactions.slice();const again=key();return {idle,pending,again,after,final:interactions.slice()}}""")
            page.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            up_point=point()
            result['observations'].append({'pendingHome':home,'homeProjection':home_point,'pendingClampedUp':up,'clampedProjection':up_point})
            expected_home=[{'type':'key','key':'Home'}];expected_up=[{'type':'key','key':'ArrowUp'}]
            assert home['after']==expected_home and home['final']==expected_home, 'Home left a pending geographic focus running at native Home fields: '+str(home)
            assert up['after']==expected_up and up['final']==expected_up, 'clamped ArrowUp left a pending geographic focus running: '+str(up)
            assert home['rejected']==[] and all(home[k] and up[k] for k in ['idle','pending','again']), 'pending-focus cancellation changed native guards/default handling'
            assert abs(home_point['x']-300)<.01 and abs(home_point['y']-300)<.01, 'cancelled Home target moved on the next rendered frame'
            assert abs(up_point['x']-300)<.01 and up_point['y']>500, 'cancelled clamped ArrowUp target moved off the native60degree orientation'
        def interruption():
            mount()
            assert page.evaluate("typeof ctl.focusLocation==='function'"), 'geographic focus API absent'
            page.evaluate('ctl.focusLocation({lat:35,lng:90},{animate:true})');page.locator('.jpw-aisol-root').focus();page.keyboard.press('ArrowLeft')
            page.wait_for_timeout(1300)
            p=point('east');assert not p['visible'] or abs(p['x']-300)>20 or abs(p['y']-300)>20, 'focus animation overrode accepted keyboard manipulation'
            assert page.evaluate('interactions')==[{'type':'key','key':'ArrowLeft'}]
            page.evaluate('ctl.focusLocation({lat:0,lng:0},{animate:false});interactions=[];ctl.focusLocation({lat:35,lng:90},{animate:true})')
            page.mouse.move(300,300);page.mouse.down();page.wait_for_timeout(1200)
            p=point('east');assert not p['visible'] or abs(p['x']-300)>20 or abs(p['y']-300)>20, 'held pointer did not immediately cancel geographic animation'
            assert [e['type'] for e in page.evaluate('interactions')]==['start'];page.mouse.up()
        def observer():
            mount();page.evaluate('observerThrows=true');before=point()
            page.mouse.move(300,300);page.mouse.down();page.mouse.move(345,300,steps=4);page.mouse.up();page.wait_for_timeout(80)
            assert point()['x']!=before['x'], 'throwing observer interrupted native drag'
            assert [e['type'] for e in page.evaluate('interactions')]==['start','end']
            page.locator('.jpw-aisol-root').focus();page.keyboard.press('Home');page.wait_for_timeout(80)
            assert abs(point()['x']-300)<.1, 'throwing observer interrupted native Home'
            assert page.evaluate('interactions.at(-1)')=={'type':'key','key':'Home'}
            assert not errors, 'observer escaped controls: '+str(errors)
        def fallback():
            mount();page.mouse.move(300,300);page.mouse.down()
            page.evaluate("""()=>{window.gl=document.querySelector('#host canvas').getContext('webgl2');window.lose=gl.getExtension('WEBGL_lose_context');lose.loseContext()}""")
            page.wait_for_function("document.querySelector('.jpw-aisol-root').dataset.state==='fallback'")
            phases=page.evaluate('interactions');assert [e['type'] for e in phases]==['start','end'] and phases[1]['cancelled'] is True, 'context loss left accepted gesture held: '+str(phases)
            page.mouse.up();page.evaluate('interactions=[]')
            page.locator('.jpw-aisol-root').focus();page.keyboard.press('ArrowRight');page.mouse.click(300,300)
            assert page.evaluate('interactions')==[], 'lost-context native controls emitted manipulation'
            assert page.evaluate("typeof ctl.focusLocation==='function'"), 'geographic focus API absent'
            page.evaluate('ctl.focusLocation({lat:35,lng:90},{animate:true})')
            text=page.locator('.jpw-aisol-fallback text').all_text_contents();assert text==['East'], 'fallback focus did not use requested geographic orientation: '+str(text)
            before=page.locator('.jpw-aisol-fallback').evaluate('e=>e.innerHTML')
            assert page.evaluate("""()=>{try{ctl.focusLocation({lat:0,lng:181});return false}catch{return true}}""")
            assert page.locator('.jpw-aisol-fallback').evaluate('e=>e.innerHTML')==before, 'invalid fallback focus mutated orientation'
            assert page.evaluate('selections')==[] and page.evaluate('interactions')==[]
            page.evaluate('lose.restoreContext()');page.wait_for_function("document.querySelector('.jpw-aisol-root').dataset.state==='ready'");page.wait_for_timeout(60)
            p=point('east');assert abs(p['x']-300)<.1 and abs(p['y']-300)<.1, 'restoration lost fallback geographic orientation'
            page.evaluate("""()=>{ctl.dispose();const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(name,...rest){return name==='webgl2'?null:original.call(this,name,...rest)};window.interactions=[];window.ctl=JPWAisolGlobeRuntime.create(document.querySelector('#host'),{markers:[{id:'east',label:'East',lat:35,lng:90}],onInteraction:e=>interactions.push(e)});ctl.focusLocation({lat:35,lng:90},{animate:true})}""")
            assert page.locator('.jpw-aisol-fallback text').all_text_contents()==['East']
            page.locator('.jpw-aisol-root').focus();page.keyboard.press('ArrowLeft');page.mouse.click(300,300)
            assert page.evaluate('interactions')==[], 'SVG fallback invented manipulation'
            page.locator('#host').screenshot(path=str(out/'geographic-fallback.png'))
        try:
            for name,fn in [('geographic-focus-atomic',location),('shortest-antimeridian-reduced',shortest),('pointer-held-up-cancel-capture',pointer),('keyboard-accepted-noop-lifecycle',keyboard),('pointer-multipointer-hold',multipointer),('keyboard-pending-focus-cancellation',pending_key),('focus-interruption',interruption),('observer-isolation',observer),('geographic-svg-restore',fallback)]:check(name,fn)
            result['errors']=errors;result['status']='PASS' if all(c['status']=='PASS' for c in result['cases']) and not errors else 'PRODUCT_FAIL';result['browser']=browser.version
        finally:
            page.evaluate('window.ctl?.dispose()');ctx.close();browser.close()
    (out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print(json.dumps(result,indent=2,ensure_ascii=False));return 0 if result['status']=='PASS' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--case',choices=['engine','fidelity','lifecycle','lost-focus','secondary-click','labels','zoom-picking','zoom-labels','noon-adapter'],default='engine');parser.add_argument('--out-dir',default='tools/.artifacts/market-hours/engine');parser.add_argument('--three-root',type=Path,default=Path('/private/tmp/jpw-globe-build/node_modules/three'));parser.add_argument('--esbuild-bin',type=Path,default=Path('/private/tmp/jpw-globe-build/node_modules/.bin/esbuild'))
    args=parser.parse_args()
    sys.exit(noon_adapter(args) if args.case=='noon-adapter' else zoom(args) if args.case.startswith('zoom-') else labels(args) if args.case=='labels' else run(args) if args.case=='engine' else extra(args))

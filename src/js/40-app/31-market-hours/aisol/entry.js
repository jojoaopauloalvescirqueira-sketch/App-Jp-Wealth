/* Build-only adapter. Base engine is the preserved Aisol implementation.
 * Extensions: lifecycle, safe DOM, stable city IDs, per-pin colour, selection.
 */
import { GlobeEngine, THREE, PIN_VERT, PIN_FRAG, toVec, rotate, landDots, pointCount, rad, clamp } from './engine.js';

const DEFAULT_LOOK = Object.freeze({dot:'#8FA3FF',dotSize:.6,density:55,size:.78,ocean:'#0E1428',oceanOpacity:.85,
  glow:'#4F6BFF',glowStrength:.6,pin:'#FFB35C',pinSize:1,pulse:true,arcColor:'#FFB35C',arcSpeed:50});
const DEFAULT_MOTION = Object.freeze({autoRotate:true,speed:6,drag:true,startLng:10,tilt:22});
const LIGHT = Object.freeze({dot:'#425caa',ocean:'#e7ecfa',glow:'#869cea'});
const finite = (x,f) => typeof x==='number' && Number.isFinite(x)?x:f;
const colour = (x,f) => typeof x==='string' && /^#[0-9a-f]{6}$/i.test(x)?x:f;
function lookOptions(input={},theme='dark') {
  const p={...DEFAULT_LOOK,...(theme==='light'?LIGHT:{}),...input};
  for (const key of ['dot','ocean','glow','pin','arcColor']) p[key]=colour(p[key],DEFAULT_LOOK[key]);
  for (const [key,min,max] of [['dotSize',.1,1],['density',10,100],['size',.2,1],['oceanOpacity',0,1],['glowStrength',0,1],['pinSize',.4,2.5],['arcSpeed',0,100]]) p[key]=clamp(finite(p[key],DEFAULT_LOOK[key]),min,max);
  p.pulse=!!p.pulse;return p;
}
function cleanMarkers(value) {
  if (!Array.isArray(value) || value.length>40) throw Error('Marcadores inválidos: máximo de 40 cidades.');
  const ids=new Set();return value.map(p=>{
    if (!p || typeof p.id!=='string' || !p.id || ids.has(p.id) || !Number.isFinite(p.lat) || !Number.isFinite(p.lng) || p.lat < -90 || p.lat>90 || p.lng < -180 || p.lng>180) throw Error('Identidade ou coordenadas de marcador inválidas.');
    ids.add(p.id);return {id:p.id,label:typeof p.label==='string'?p.label:'',lat:p.lat,lng:p.lng,
      venueIds:Array.isArray(p.venueIds)?p.venueIds.filter(v=>typeof v==='string'):[],phase:typeof p.phase==='string'?p.phase:'',color:colour(p.color,DEFAULT_LOOK.pin)};
  });
}
function cleanLocation(value) {
  const lat=value?.lat,lng=value?.lng;
  if(!Number.isFinite(lat) || !Number.isFinite(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180)throw Error('Coordenadas geográficas inválidas.');
  return {lat,lng};
}

class MarketEngine extends GlobeEngine {
  constructor(...args) {
    super(...args);
    this.active=true;this.lost=false;this.focusTarget=null;this.selectedMarkerId=null;
    // Only the color input changes; alpha, silhouette, pulse and occlusion stay Aisol.
    for (const material of [this.pinMat,this.ringMat]) {
      material.vertexShader=PIN_VERT.replace('attribute float aPhase;', 'attribute float aPhase;\nattribute vec3 aColor;\nvarying vec3 vPinColor;').replace('void main() {','void main() {\n    vPinColor = aColor;');
      material.fragmentShader=PIN_FRAG.replace('uniform vec3 uColor;','uniform vec3 uColor;\nvarying vec3 vPinColor;').replace('vec4(uColor, a)','vec4(vPinColor, a)');
      material.needsUpdate=true;
    }
    this.selectionGeo=new THREE.BufferGeometry();
    this.selectionMat=new THREE.ShaderMaterial({vertexShader:PIN_VERT,fragmentShader:PIN_FRAG,
      uniforms:{uColor:{value:new THREE.Color('#ffffff')},uSize:{value:16},uPixel:{value:1},uTime:{value:.45},uRing:{value:1},uPulse:{value:1}},
      transparent:true,depthWrite:false,depthTest:false});
    this.selectionMesh=new THREE.Points(this.selectionGeo,this.selectionMat);this.selectionMesh.renderOrder=6;this.selectionMesh.visible=false;this.globe.add(this.selectionMesh);
    const baseTick=this.tick;
    this.tick=t=>{if(this.blocked()){this.stop();return;}try {baseTick(t);}catch(error){this.fail(error);}};
    const originalDown=this.onDown;
    this.root.removeEventListener('pointerdown',originalDown);
    this.onDown=e=>{
      if(this.blocked() || (e.pointerType==='mouse' && e.button!==0))return;
      if(this.interactionPointer)return;
      this.clickStart={x:e.clientX,y:e.clientY,t:e.timeStamp,id:e.pointerId};originalDown(e);
      if(this.dragging && this.pointerId===e.pointerId){this.focusTarget=null;this.interactionPointer={pointerId:e.pointerId,pointerType:e.pointerType};this.notifyInteraction({type:'start',...this.interactionPointer});}
    };
    this.root.addEventListener('pointerdown',this.onDown);
    const originalMove=this.onMove;
    this.root.removeEventListener('pointermove',originalMove);
    this.onMove=e=>{if(!this.blocked())originalMove(e);};this.root.addEventListener('pointermove',this.onMove);
    const originalUp=this.onUp;
    this.root.removeEventListener('pointerup',originalUp);this.root.removeEventListener('pointercancel',originalUp);
    this.onUp=e=>{
      const start=this.clickStart;if(start?.id===e.pointerId)this.clickStart=null;
      const cancelled=e.type!=='pointerup';
      const pointer=this.interactionPointer?.pointerId===e.pointerId?this.interactionPointer:null;
      if(pointer)this.interactionPointer=null;
      if(cancelled && this.pointerId===e.pointerId)this.vel=0;
      originalUp(e);
      if(pointer && !this.blocked())this.notifyInteraction({type:'end',...pointer,cancelled});
      if(!cancelled && (e.pointerType!=='mouse' || e.button===0) && start && start.id===e.pointerId && Math.hypot(e.clientX-start.x,e.clientY-start.y)<6 && e.timeStamp-start.t<650 && !this.blocked()) this.pick(e);
    };
    this.root.addEventListener('pointerup',this.onUp);this.root.addEventListener('pointercancel',this.onUp);
    this.onCaptureLost=e=>{if(e.pointerId===this.pointerId)this.cancelInteraction(!this.blocked());};
    this.root.addEventListener('lostpointercapture',this.onCaptureLost);
    const originalKey=this.onKey;
    this.root.removeEventListener('keydown',originalKey);
    this.onKey=e=>{
      if(this.blocked())return;
      const before={vel:this.vel,spin:this.spin,tiltTarget:this.tiltTarget,prevented:e.defaultPrevented};originalKey(e);
      // A native handled key also interrupts a pending camera change at Home/clamps.
      if(before.vel!==this.vel || before.spin!==this.spin || before.tiltTarget!==this.tiltTarget || (this.focusTarget && !before.prevented && e.defaultPrevented)){this.focusTarget=null;this.notifyInteraction({type:'key',key:e.key});}
    };
    this.root.addEventListener('keydown',this.onKey);
  }
  notifyInteraction(event){try{if(this.onInteraction)this.onInteraction(event);}catch{/* An observer cannot interrupt the native controls. */}}
  cancelInteraction(notify=true){
    const pointer=this.interactionPointer;this.interactionPointer=null;this.clickStart=null;
    const captured=this.pointerId;
    if(this.dragging){this.dragging=false;this.pointerId=-1;this.vel=0;this.root.style.cursor=this.motion.drag?'grab':'';}
    if(captured>=0){try{this.root.releasePointerCapture(captured);}catch{}}
    if(pointer && notify)this.notifyInteraction({type:'end',...pointer,cancelled:true});
  }
  blocked(){return this.disposed || this.active===false || this.lost || document.hidden;}
  invalidate(){if(this.blocked())return;super.invalidate();}
  draw(animating=false){if(this.blocked())return;super.draw(animating);}
  animating(){return !!this.focusTarget || super.animating();}
  step(dt){
    if(this.focusTarget){const target=this.focusTarget;const k=1-Math.exp(-dt*8);this.spin+=(target.spin-this.spin)*k;this.tilt+=(target.tilt-this.tilt)*k;this.tiltTarget=this.tilt;this.vel=0;
      if(Math.abs(target.spin-this.spin)<.0005 && Math.abs(target.tilt-this.tilt)<.0005){this.spin=target.spin;this.tilt=this.tiltTarget=target.tilt;this.focusTarget=null;}
      this.time+=dt;
    }else super.step(dt);
  }
  fail(error){this.lost=true;this.stop();if(this.onFailure)this.onFailure(error);}
  setMarkers(markers,selectedMarkerId){
    const shape=JSON.stringify(markers.map(p=>[p.id,p.lat,p.lng,p.label]));
    if(this.shape!==shape){super.setData(markers,'off',true);this.shape=shape;}
    else this.pins=markers;
    const colors=new Float32Array(markers.length*3);
    markers.forEach((p,i)=>{const c=new THREE.Color(p.color);colors.set([c.r,c.g,c.b],i*3);});
    let attr=this.pinGeo.getAttribute('aColor');
    if(attr && attr.array.length===colors.length){attr.array.set(colors);attr.needsUpdate=true;}
    else this.pinGeo.setAttribute('aColor',new THREE.BufferAttribute(colors,3));
    const labelled=markers.filter(p=>p.label);
    this.labels.forEach((l,i)=>{l.el.dataset.markerId=labelled[i].id;l.el.style.color=labelled[i].color;l.el.style.textDecoration=labelled[i].id===selectedMarkerId?'underline':'none';l.el.style.textUnderlineOffset='4px';});
    this.selectedMarkerId=selectedMarkerId;
    const selected=markers.find(p=>p.id===selectedMarkerId);
    let selectedPosition=this.selectionGeo.getAttribute('position');
    if(!selectedPosition){selectedPosition=new THREE.BufferAttribute(new Float32Array(3),3);this.selectionGeo.setAttribute('position',selectedPosition);this.selectionGeo.setAttribute('aPhase',new THREE.BufferAttribute(new Float32Array([0]),1));}
    selectedPosition.array.set(selected?toVec(selected.lat,selected.lng,1.004):[0,0,0]);selectedPosition.needsUpdate=true;this.selectionGeo.computeBoundingSphere();
    this.selectionMesh.visible=!!selected;this.updateSizes();this.invalidate();
  }
  updateSizes(){super.updateSizes();if(this.selectionMat){this.selectionMat.uniforms.uSize.value=this.pinMat.uniforms.uSize.value*1.85;this.selectionMat.uniforms.uPixel.value=this.renderer.getPixelRatio();}}
  placeLabels(){
    super.placeLabels();
    const fontSize=this.labelLayer.style.fontSize,measure=this.labelFontSize!==fontSize,candidates=[];
    let labelUnits=null;
    for(const l of this.labels){
      this.tmp.copy(l.pos).applyMatrix4(this.globe.matrixWorld);
      const x=this.width/2+this.tmp.x*this.radiusPx,y=this.height/2-this.tmp.y*this.radiusPx,left=this.tmp.x>.55;
      l.el.style.left=x+'px';l.el.style.top=y+'px';
      l.el.style.transform=`translate(${left?'calc(-100% - 0.9em)':'0.9em'}, -50%)`;
      if(!this.declutterLabels)continue;
      // Cache local CSS dimensions: screen rectangles also include ancestor zoom/scale.
      if(measure || !l.labelSize){
        if(!labelUnits){const rootBox=this.root.getBoundingClientRect();labelUnits={x:rootBox.width?this.width/rootBox.width:1,y:rootBox.height?this.height/rootBox.height:1};}
        const box=l.el.getBoundingClientRect();l.labelSize={width:box.width*labelUnits.x,height:box.height*labelUnits.y};
      }
      if(l.el.style.visibility!=='visible')continue;
      const gap=parseFloat(fontSize)*.9,w=l.labelSize.width,h=l.labelSize.height;
      candidates.push({l,x,y,w,h,left:x+(left?-w-gap:gap),top:y-h/2,selected:l.el.dataset.markerId===this.selectedMarkerId});
    }
    if(!this.declutterLabels)return;
    this.labelFontSize=fontSize;
    const accepted=[];
    candidates.sort((a,b)=>Number(b.selected)-Number(a.selected));
    for(const box of candidates){
      if(box.selected){
        const x=clamp(box.left,0,Math.max(0,this.width-box.w)),y=clamp(box.top,0,Math.max(0,this.height-box.h));
        box.l.el.style.left=(box.x+x-box.left)+'px';box.l.el.style.top=(box.y+y-box.top)+'px';box.left=x;box.top=y;
      }
      const outside=box.left<0 || box.top<0 || box.left+box.w>this.width || box.top+box.h>this.height;
      const collision=accepted.some(a=>box.left<a.left+a.w+2 && box.left+box.w+2>a.left && box.top<a.top+a.h+2 && box.top+box.h+2>a.top);
      if(outside || collision)box.l.el.style.visibility='hidden';else accepted.push(box);
    }
  }
  pick(event){
    this.globe.updateMatrixWorld();const box=this.root.getBoundingClientRect();if(!box.width || !box.height)return;
    const x=(event.clientX-box.left)*this.width/box.width,y=(event.clientY-box.top)*this.height/box.height;
    let best=null,distance=16;
    for(const p of this.pins){this.tmp.fromArray(toVec(p.lat,p.lng,1.004)).applyMatrix4(this.globe.matrixWorld);if(this.tmp.z<=.08)continue;
      const d=Math.hypot(x-(this.width/2+this.tmp.x*this.radiusPx),y-(this.height/2-this.tmp.y*this.radiusPx));
      if(d<distance){distance=d;best=p;}}
    if(best && this.onSelectMarker)this.onSelectMarker(best.id);
  }
  focusMarker(id,animate){
    const p=this.pins.find(item=>item.id===id);if(!p)return;
    this.focusLocation(p,animate);
  }
  focusLocation(p,animate){
    const raw=-rad(p.lng),spin=this.spin+Math.atan2(Math.sin(raw-this.spin),Math.cos(raw-this.spin));
    const tilt=rad(p.lat);this.vel=0;this.auto=0;
    if(animate && !this.motion.reduce)this.focusTarget={spin,tilt};
    else {this.focusTarget=null;this.spin=spin;this.tilt=this.tiltTarget=tilt;}
    this.invalidate();
  }
  dispose(releaseContext=true){if(this.disposed)return;this.cancelInteraction(false);this.root.removeEventListener('lostpointercapture',this.onCaptureLost);this.selectionGeo.dispose();this.selectionMat.dispose();super.dispose();if(releaseContext)this.renderer.forceContextLoss();}
}

// Native SVG fallback ports the reference FlatGlobe projection, sample and buckets.
// All labels enter through textContent. No HTML is constructed from marker data.
let fallbackId=0;
function fallbackSvg(root,markers,look,motion,orientation) {
  const ns='http://www.w3.org/2000/svg';
  const node=(tag,attrs,parent)=>{const e=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs||{}))e.setAttribute(k,String(v));if(parent)parent.append(e);return e;};
  const svg=node('svg',{viewBox:'0 0 1000 1000',preserveAspectRatio:'xMidYMid meet','aria-hidden':'true',class:'jpw-aisol-fallback'});
  Object.assign(svg.style,{position:'absolute',inset:'0',width:'100%',height:'100%',pointerEvents:'none'});
  const R=500*look.size,c=500,spin=orientation?orientation.spin:-rad(motion.startLng),tilt=orientation?orientation.tilt:rad(motion.tilt);
  const id='jpw-aisol-glow-'+(++fallbackId),defs=node('defs',{},svg),gradient=node('radialGradient',{id},defs);
  node('stop',{offset:(100/1.22)+'%','stop-color':look.glow,'stop-opacity':.55*look.glowStrength},gradient);node('stop',{offset:'100%','stop-color':look.glow,'stop-opacity':0},gradient);
  node('circle',{cx:c,cy:c,r:R*1.22,fill:'url(#'+id+')'},svg);node('circle',{cx:c,cy:c,r:R,fill:look.ocean,'fill-opacity':look.oceanOpacity},svg);
  const buckets=['','',''],dots=landDots(look.density),spacing=R*Math.sqrt(4*Math.PI/pointCount(look.density));
  for(let i=0;i<dots.length;i+=3){const v=rotate([dots[i],dots[i+1],dots[i+2]],spin,tilt);if(v[2]<0)continue;const b=v[2]<.2?0:v[2]<.55?1:2;const x=c+v[0]*R,y=c-v[1]*R;buckets[b]+=`M${x.toFixed(1)} ${y.toFixed(1)}h0.01`;}
  buckets.forEach((d,i)=>node('path',{d,fill:'none',stroke:look.dot,'stroke-linecap':'round','stroke-width':Math.max(.6,spacing*look.dotSize),'stroke-opacity':[.35,.7,1][i]},svg));
  for(const p of markers){const v=rotate(toVec(p.lat,p.lng),spin,tilt);if(v[2]<=.08)continue;const x=c+v[0]*R,y=c-v[1]*R,pinR=spacing*.95*look.pinSize;
    node('circle',{cx:x,cy:y,r:pinR*2.1,fill:p.color,'fill-opacity':.22},svg);node('circle',{cx:x,cy:y,r:pinR,fill:p.color},svg);
    const text=node('text',{x:x+pinR*2.4,y:y+8,fill:p.color,'font-size':24,'font-weight':600},svg);text.textContent=p.label;}
  return svg;
}

function create(host,options={}) {
  if(!(host instanceof HTMLElement))throw Error('Host do globo ausente.');
  let markers=cleanMarkers(options.markers===undefined?[]:options.markers),selected=options.selectedMarkerId||null,theme='dark';
  let active=true,disposed=false,engine=null,orientation=null,restoreQueued=false;
  const lookInput=options.look||{},motionInput={...DEFAULT_MOTION,...options.motion};
  const media=window.matchMedia('(prefers-reduced-motion: reduce)');
  const motion=()=>({...motionInput,autoRotate:!!motionInput.autoRotate,drag:!!motionInput.drag,speed:clamp(finite(motionInput.speed,6),0,60),startLng:clamp(finite(motionInput.startLng,10),-180,180),tilt:clamp(finite(motionInput.tilt,22),-60,60),reduce:media.matches});
  const root=document.createElement('div');root.className='jpw-aisol-root';root.setAttribute('role','img');root.setAttribute('aria-label','Globo das bolsas globais. Arraste ou use as setas para girar.');root.tabIndex=0;
  Object.assign(root.style,{position:'relative',width:'100%',height:'100%',minHeight:'1px',overflow:'hidden',fontFamily:'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif',outlineOffset:'-2px',userSelect:'none'});
  const canvas=document.createElement('canvas');canvas.setAttribute('aria-hidden','true');Object.assign(canvas.style,{position:'absolute',inset:'0',width:'100%',height:'100%',display:'block'});
  const layer=document.createElement('div');layer.setAttribute('aria-hidden','true');Object.assign(layer.style,{position:'absolute',inset:'0',pointerEvents:'none',color:'#E8ECF7'});
  const labelStyle=document.createElement('style');labelStyle.textContent='.jpw-aisol-root .adg-label{position:absolute;white-space:nowrap;font-weight:600;line-height:1;letter-spacing:.01em;text-shadow:0 0 2px var(--jpw-aisol-halo),0 0 6px var(--jpw-aisol-halo)}';
  root.append(canvas,layer,labelStyle);host.append(root);
  let fallback=null;
  function showFallback(error){if(disposed)return;if(engine){if(root.dataset.state!=='fallback')orientation={spin:engine.spin,tilt:engine.tilt};engine.cancelInteraction();engine.focusTarget=null;engine.lost=true;engine.stop();}
    if(fallback)fallback.remove();fallback=fallbackSvg(root,markers,lookOptions(lookInput,theme),motion(),orientation);root.prepend(fallback);canvas.style.visibility='hidden';layer.style.visibility='hidden';root.dataset.state='fallback';
    if(error && typeof options.onError==='function')options.onError(error);
  }
  function updateTheme(){root.style.setProperty('--jpw-aisol-halo',theme==='light'?'rgba(255,255,255,.8)':'rgba(0,0,0,.55)');}
  function build(){
    if(disposed)return;
    try {
      const gl=canvas.getContext('webgl2',{alpha:true,antialias:true,premultipliedAlpha:true});if(!gl)throw Error('WebGL2 indisponível.');
      engine=new MarketEngine(canvas,root,layer,gl,ready=>{if(!ready)showFallback(Error('Contexto WebGL perdido.'));},()=>{
        if(disposed||restoreQueued)return;restoreQueued=true;queueMicrotask(()=>{restoreQueued=false;if(disposed)return;if(engine){engine.dispose(false);engine=null;}build();});
      });
      engine.onFailure=showFallback;engine.onSelectMarker=id=>{if(typeof options.onSelectMarker==='function')options.onSelectMarker({markerId:id,source:'pointer'});};
      engine.onInteraction=event=>{if(typeof options.onInteraction==='function')options.onInteraction(event);};
      engine.renderer.debug.onShaderError=(_gl,_program,_vs,_fs)=>{throw Error('Shader Aisol incompatível com este WebGL2.');};
      engine.declutterLabels=options.declutterLabels===true;engine.active=active;engine.setLook(lookOptions(lookInput,theme));engine.setMotion(motion());engine.setMarkers(markers,selected);
      if(orientation){engine.spin=orientation.spin;engine.tilt=engine.tiltTarget=orientation.tilt;}
      engine.renderer.compile(engine.scene,engine.camera);engine.draw();
      if(fallback){fallback.remove();fallback=null;}canvas.style.visibility='visible';layer.style.visibility='visible';root.dataset.state='ready';
    }catch(error){if(engine){engine.dispose();engine=null;}showFallback(error);}
  }
  function visibility(){if(!engine)return;if(document.hidden||!active){engine.active=false;engine.stop();engine.focusTarget=null;engine.vel=0;engine.cancelInteraction(false);}else{engine.active=true;engine.last=0;engine.invalidate();}}
  function reduced(){if(engine){engine.setMotion(motion());if(media.matches && engine.focusTarget){const t=engine.focusTarget;engine.spin=t.spin;engine.tilt=engine.tiltTarget=t.tilt;engine.focusTarget=null;engine.invalidate();}}}
  const fonts=options.declutterLabels===true?document.fonts:null;
  function fontLoaded(){if(engine&&!engine.disposed){engine.labelFontSize=null;engine.invalidate();}}
  if(fonts)fonts.addEventListener('loadingdone',fontLoaded);
  document.addEventListener('visibilitychange',visibility);media.addEventListener('change',reduced);updateTheme();build();visibility();
  return Object.freeze({
    update(next={}){if(disposed)return;const nextMarkers=next.markers===undefined?markers:cleanMarkers(next.markers);
      markers=nextMarkers;if(Object.prototype.hasOwnProperty.call(next,'selectedMarkerId'))selected=next.selectedMarkerId;
      if(next.theme==='light'||next.theme==='dark')theme=next.theme;updateTheme();
      if(engine && !engine.lost){engine.setLook(lookOptions(lookInput,theme));engine.setMarkers(markers,selected);}else showFallback();
    },
    focusMarker(id,{animate=true}={}){if(disposed)return;if(engine&&!engine.lost)engine.focusMarker(id,animate);else {const p=markers.find(x=>x.id===id);if(p){orientation={spin:-rad(p.lng),tilt:rad(p.lat)};showFallback();}}},
    focusLocation(location,{animate=true}={}){if(disposed)return;const p=cleanLocation(location);if(engine&&!engine.lost)engine.focusLocation(p,animate);else{orientation={spin:-rad(p.lng),tilt:rad(p.lat)};showFallback();}},
    setActive(value){if(disposed)return;active=!!value;visibility();},
    dispose(){if(disposed)return;disposed=true;if(fonts)fonts.removeEventListener('loadingdone',fontLoaded);document.removeEventListener('visibilitychange',visibility);media.removeEventListener('change',reduced);
      if(engine){engine.dispose();engine=null;}root.remove();}
  });
}
window.JPWAisolGlobeRuntime=Object.freeze({create,version:'1.0.0',threeVersion:'0.186.1',sourceSHA256:'11208679f0598d6813913d079140f29f620b0a82cc2d27a1ced651b0d67ea7b5',author:'Aisol Studio / @ulz-song'});

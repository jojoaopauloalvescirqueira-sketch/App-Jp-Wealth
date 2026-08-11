// ============ GALTON BOARD · CANVAS HIDPI (N1) ============
(function initJPWGaltonRenderer(global){
  'use strict';
  const ns=global.JPWGalton=global.JPWGalton||{};

  function css(name,fallback){
    const value=getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value||fallback;
  }
  function finite(value,fallback=0){ return Number.isFinite(Number(value))?Number(value):fallback; }

  class CanvasRenderer{
    constructor(canvas){
      if(!canvas) throw new Error('Canvas do Galton Board ausente.');
      this.canvas=canvas;
      this.context=canvas.getContext('2d',{alpha:false});
      this.width=1; this.height=1; this.dpr=1; this.lastSnapshot=null; this.lastTransform=null;
      this.frameDurations=[]; this.lastFrameAt=0; this.renderMs=0;
      this.resize();
    }
    resize(){
      const rect=this.canvas.getBoundingClientRect();
      const width=Math.max(1,Math.round(rect.width||this.canvas.clientWidth||640));
      const height=Math.max(1,Math.round(rect.height||this.canvas.clientHeight||520));
      const dpr=Math.min(3,Math.max(1,finite(global.devicePixelRatio,1)));
      if(this.width===width&&this.height===height&&this.dpr===dpr) return false;
      this.width=width; this.height=height; this.dpr=dpr;
      this.canvas.width=Math.round(width*dpr); this.canvas.height=Math.round(height*dpr);
      this.context.setTransform(dpr,0,0,dpr,0,0);
      if(this.lastSnapshot) this.draw(this.lastSnapshot);
      return true;
    }
    colors(){
      return {
        background:css('--jp-surface','#111827'),
        raised:css('--jp-surface-raised','#182235'),
        ink:css('--jp-ink','#f4f7fb'),
        muted:css('--jp-ink-muted','#9aa7b8'),
        border:css('--jp-border','#334155'),
        action:css('--jp-action','#7c8cff'),
        info:css('--jp-info','#3db5e6')
      };
    }
    geometry(snapshot){ return snapshot&&snapshot.geometry? snapshot.geometry : (ns.config&&ns.config.geometry?ns.config.geometry(snapshot&&snapshot.config):null); }
    bounds(snapshot,geometry){
      const declared=geometry&&(geometry.world||geometry.bounds);
      if(declared){
        return {
          minX:finite(declared.minX,finite(declared.left,-6)), maxX:finite(declared.maxX,finite(declared.right,6)),
          minY:finite(declared.minY,finite(declared.bottom,-1)), maxY:finite(declared.maxY,finite(declared.top,12))
        };
      }
      const points=[];
      (geometry&&geometry.pegs||[]).forEach(p=>points.push(p));
      (snapshot&&snapshot.balls||[]).forEach(p=>points.push(p));
      const xs=points.map(p=>finite(p.x)), ys=points.map(p=>finite(p.y));
      const rows=finite(snapshot&&snapshot.config&&snapshot.config.rows,10);
      const half=Math.max(3,rows*.55);
      return {minX:xs.length?Math.min(...xs)-1:-half,maxX:xs.length?Math.max(...xs)+1:half,minY:-1.2,maxY:ys.length?Math.max(...ys)+1.4:rows+2};
    }
    transform(snapshot){
      const geometry=this.geometry(snapshot)||{};
      const bounds=this.bounds(snapshot,geometry);
      const padX=Math.max(18,this.width*.045), padTop=24, padBottom=Math.max(98,this.height*.23);
      const worldWidth=Math.max(.001,bounds.maxX-bounds.minX), worldHeight=Math.max(.001,bounds.maxY-bounds.minY);
      const scale=Math.min((this.width-padX*2)/worldWidth,(this.height-padTop-padBottom)/worldHeight);
      const usedWidth=worldWidth*scale, originX=(this.width-usedWidth)/2-bounds.minX*scale;
      const floorY=this.height-padBottom;
      const tx={geometry,bounds,scale,originX,floorY,padBottom,toScreen:(x,y)=>({x:originX+x*scale,y:floorY-(y-bounds.minY)*scale})};
      this.lastTransform=tx; return tx;
    }
    draw(snapshot){
      const started=performance.now();
      this.lastSnapshot=snapshot||{};
      const ctx=this.context, colors=this.colors(), tx=this.transform(this.lastSnapshot);
      ctx.save(); ctx.setTransform(this.dpr,0,0,this.dpr,0,0);
      ctx.fillStyle=colors.background; ctx.fillRect(0,0,this.width,this.height);
      this.drawGrid(ctx,colors);
      this.drawBoard(ctx,colors,tx,this.lastSnapshot);
      this.drawHistogram(ctx,colors,tx,this.lastSnapshot);
      if(this.lastSnapshot.debug) this.drawDebug(ctx,colors,this.lastSnapshot);
      ctx.restore();
      this.renderMs=performance.now()-started;
      const now=performance.now();
      if(this.lastFrameAt){ this.frameDurations.push(now-this.lastFrameAt); if(this.frameDurations.length>120) this.frameDurations.shift(); }
      this.lastFrameAt=now;
    }
    drawGrid(ctx,colors){
      ctx.strokeStyle=colors.border; ctx.globalAlpha=.18; ctx.lineWidth=1;
      const gap=32;
      for(let x=.5;x<this.width;x+=gap){ ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,this.height);ctx.stroke(); }
      for(let y=.5;y<this.height;y+=gap){ ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(this.width,y);ctx.stroke(); }
      ctx.globalAlpha=1;
    }
    drawBoard(ctx,colors,tx,snapshot){
      const geometry=tx.geometry||{}, config=snapshot.config||{};
      const pegRadius=Math.max(2,finite(config.pegRadius,.1)*tx.scale);
      const ballRadius=Math.max(2.5,finite(config.ballRadius,.17)*tx.scale);
      ctx.lineWidth=1;
      ctx.strokeStyle=colors.border;
      (geometry.walls||geometry.dividers||[]).forEach(line=>{
        const a=tx.toScreen(line.x1,finite(line.y1,tx.bounds.minY));
        const b=tx.toScreen(line.x2===undefined?line.x1:line.x2,finite(line.y2,finite(geometry.binTop,tx.bounds.minY+1.6)));
        ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
      });
      ctx.fillStyle=colors.muted; ctx.strokeStyle=colors.ink;
      (geometry.pegs||[]).forEach(peg=>{
        const p=tx.toScreen(peg.x,peg.y); ctx.beginPath();ctx.arc(p.x,p.y,pegRadius,0,Math.PI*2);ctx.fill();
      });
      ctx.fillStyle=colors.action; ctx.strokeStyle=colors.ink;
      (snapshot.balls||[]).forEach(ball=>{
        const p=tx.toScreen(ball.x,ball.y); ctx.beginPath();ctx.arc(p.x,p.y,Math.max(2,finite(ball.radius,ballRadius/tx.scale)*tx.scale),0,Math.PI*2);ctx.fill();ctx.globalAlpha=.55;ctx.stroke();ctx.globalAlpha=1;
      });
      const releaseWorld=geometry.release&&Number.isFinite(Number(geometry.release.x))?Number(geometry.release.x):finite(snapshot.releasePoint);
      const releaseY=geometry.release&&Number.isFinite(Number(geometry.release.y))?Number(geometry.release.y):tx.bounds.maxY-.25;
      const release=tx.toScreen(releaseWorld,releaseY);
      ctx.strokeStyle=colors.info;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(release.x-8,release.y);ctx.lineTo(release.x+8,release.y);ctx.moveTo(release.x,release.y-5);ctx.lineTo(release.x,release.y+5);ctx.stroke();
    }
    binCount(snapshot,geometry){
      if(Array.isArray(snapshot.histogram)&&snapshot.histogram.length) return snapshot.histogram.length;
      if(Array.isArray(geometry.bins)&&geometry.bins.length) return geometry.bins.length;
      return Math.max(2,Math.round(finite(snapshot.config&&snapshot.config.rows,10))+1);
    }
    binScreenBounds(index,count,tx){
      const geometry=tx.geometry||{}, bins=geometry.bins||[];
      if(bins[index]){
        const bin=bins[index], left=tx.toScreen(finite(bin.minX,finite(bin.left)),tx.bounds.minY).x, right=tx.toScreen(finite(bin.maxX,finite(bin.right)),tx.bounds.minY).x;
        return {left:Math.min(left,right),right:Math.max(left,right)};
      }
      const left=tx.toScreen(tx.bounds.minX,tx.bounds.minY).x, right=tx.toScreen(tx.bounds.maxX,tx.bounds.minY).x;
      const width=(right-left)/count; return {left:left+index*width,right:left+(index+1)*width};
    }
    drawHistogram(ctx,colors,tx,snapshot){
      const histogram=Array.isArray(snapshot.histogram)?snapshot.histogram:[];
      const count=this.binCount(snapshot,tx.geometry), total=histogram.reduce((sum,value)=>sum+finite(value),0);
      const top=tx.floorY+16, bottom=this.height-27, height=Math.max(34,bottom-top);
      const theory=(snapshot.showTheory&&snapshot.theoryEligible&&ns.statistics)?ns.statistics.binomialDistribution(Math.max(1,count-1)):null;
      const expected=theory?theory.map(probability=>probability*total):[];
      const yMax=Math.max(1,...histogram,...expected);
      for(let i=0;i<count;i++){
        const box=this.binScreenBounds(i,count,tx), gap=Math.min(3,(box.right-box.left)*.1), value=finite(histogram[i]);
        const barH=value/yMax*height, x=box.left+gap, width=Math.max(1,box.right-box.left-gap*2);
        ctx.fillStyle=colors.raised;ctx.fillRect(x,top,width,height);
        ctx.fillStyle=colors.action;ctx.globalAlpha=.72;ctx.fillRect(x,bottom-barH,width,barH);ctx.globalAlpha=1;
        ctx.fillStyle=colors.muted;ctx.font='10px ui-monospace, SFMono-Regular, Menlo, monospace';ctx.textAlign='center';ctx.fillText(String(i),box.left+(box.right-box.left)/2,this.height-10);
      }
      if(expected.length===count&&total>0){
        ctx.strokeStyle=colors.info;ctx.lineWidth=2;ctx.beginPath();
        expected.forEach((expectedCount,i)=>{
          const box=this.binScreenBounds(i,count,tx), x=(box.left+box.right)/2, y=bottom-(expectedCount/yMax)*height;
          if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
        });ctx.stroke();
      }
      ctx.fillStyle=colors.muted;ctx.font='10px ui-monospace, SFMono-Regular, Menlo, monospace';ctx.textAlign='left';ctx.fillText('HISTOGRAMA EMPÍRICO',Math.max(8,tx.toScreen(tx.bounds.minX,tx.bounds.minY).x),top-5);
    }
    drawDebug(ctx,colors,snapshot){
      const fps=this.frameDurations.length?1000/(this.frameDurations.reduce((a,b)=>a+b,0)/this.frameDurations.length):0;
      const lines=[`FPS ${fps.toFixed(1)}`,`render ${this.renderMs.toFixed(2)} ms`,`step ${finite(snapshot.physicsMs).toFixed(2)} ms`,`corpos ${finite(snapshot.activeCount)}`,`colisões ${finite(snapshot.collisionCount)}`,`fila ${finite(snapshot.queuedCount)}`];
      ctx.font='10px ui-monospace, SFMono-Regular, Menlo, monospace';
      const width=Math.max(...lines.map(line=>ctx.measureText(line).width))+18;
      ctx.fillStyle='rgba(0,0,0,.66)';ctx.fillRect(this.width-width-8,8,width,lines.length*15+10);
      ctx.fillStyle=colors.ink;ctx.textAlign='left';lines.forEach((line,i)=>ctx.fillText(line,this.width-width+1,24+i*15));
    }
    binAtClientPoint(clientX,clientY){
      if(!this.lastSnapshot||!this.lastTransform) return -1;
      const rect=this.canvas.getBoundingClientRect(), x=clientX-rect.left, y=clientY-rect.top;
      if(y<this.lastTransform.floorY||y>this.height) return -1;
      const count=this.binCount(this.lastSnapshot,this.lastTransform.geometry);
      for(let i=0;i<count;i++){ const box=this.binScreenBounds(i,count,this.lastTransform); if(x>=box.left&&x<=box.right) return i; }
      return -1;
    }
    metrics(){
      const avg=this.frameDurations.length?this.frameDurations.reduce((a,b)=>a+b,0)/this.frameDurations.length:0;
      return {fps:avg?1000/avg:0,frameMs:avg,renderMs:this.renderMs,dpr:this.dpr};
    }
    destroy(){ this.lastSnapshot=null; this.lastTransform=null; this.frameDurations=[]; this.lastFrameAt=0; }
  }

  ns.renderer={CanvasRenderer};
})(window);

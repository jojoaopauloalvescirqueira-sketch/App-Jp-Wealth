/** Browser contract for the isolated preview. Source: CHG-STOIKUS-PAINEL-PERSONALIZAVEL-20261021.
 * Synthetic data only. These checks do not validate MT5 execution, finance or native acceptance.
 * Run through the Python adapter or an existing Node Playwright runtime.
 */
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const require=createRequire(import.meta.url);
const boundPackage=process.env.STOIKUS_PREVIEW_PLAYWRIGHT_PACKAGE;
if(boundPackage) assert.ok(path.isAbsolute(boundPackage),'bound Playwright package must be an absolute existing path');
const {chromium}=boundPackage ? require(boundPackage) : require(require.resolve('playwright',{paths:[path.resolve(path.dirname(process.execPath),'../node_modules'),process.cwd()]}));
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const evidence=process.env.STOIKUS_PREVIEW_EVIDENCE_DIR||path.join(os.tmpdir(),'jpw-stoikus-custom-panel-preview');
await fs.mkdir(evidence,{recursive:true});
const server=http.createServer(async(req,res)=>{try{const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return}const data=await fs.readFile(file);res.setHeader('Content-Type',file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.svg')?'image/svg+xml':'application/octet-stream');res.end(data)}catch{res.writeHead(404).end()}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const url=`http://127.0.0.1:${server.address().port}/docs/preview/stoikus-painel-personalizavel/index.html`;
const checks=[],screenshots=[],errors=[];
let browser;
try{
 browser=await chromium.launch({headless:true,...(process.env.STOIKUS_PREVIEW_BROWSER?{executablePath:process.env.STOIKUS_PREVIEW_BROWSER}:{channel:'chrome'})});
 const page=await browser.newPage({viewport:{width:1280,height:1050}});
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 page.on('requestfailed',r=>errors.push(r.url()+': '+r.failure()?.errorText));
 await page.goto(url);
 const visible=()=>page.locator('#metric-list [data-metric]').evaluateAll(els=>els.map(e=>Number(e.dataset.metric)));
 const edit=()=>page.locator('#open-personalizer').click();
 const close=()=>page.locator('#cancel').click();
 const shot=async(name)=>{const f=path.join(evidence,name+'.png');await page.screenshot({path:f,fullPage:true});screenshots.push(f)};
 const pass=label=>checks.push(label);
 assert.match(await page.locator('.badge').innerText(),/DADOS FICTÍCIOS/);
 assert.deepEqual(await visible(),[0,5,3,4]);
 assert.equal(await page.locator('#panel').evaluate(e=>e.getBoundingClientRect().width),280);
 assert.equal(await page.locator('#panel-background').evaluate(e=>getComputedStyle(e).opacity),'0.7');
 assert.equal(await page.evaluate(()=>localStorage.length),0,'loading must not write preferences');
 assert.equal(await page.locator('#brand').evaluate(e=>e.complete&&e.naturalWidth>0),true);
 await shot('desktop-default');pass('default selection/order, width 280, background 30%, brand, no load write');
 await edit();
 await page.getByRole('button',{name:'Subir Raiz N · 2W',exact:true}).click();
 await page.locator('#choices').getByRole('checkbox',{name:'P/L flutuante',exact:true}).check();
 assert.deepEqual(await visible(),[0,5,3,4],'draft must not alter applied panel');
 await close();assert.deepEqual(await visible(),[0,5,3,4]);
 assert.equal(await page.evaluate(()=>localStorage.length),0,'cancel must not save');pass('cancel preserves selection/order and storage');
 await edit();
 await page.getByRole('button',{name:'Subir Raiz N · 2W',exact:true}).click();
 await page.locator('#choices').getByRole('checkbox',{name:'P/L flutuante',exact:true}).check();
 await page.locator('#width').fill('480');await page.locator('#alpha').fill('60');
 await shot('personalizer-draft');
 await page.locator('#apply').click();
 assert.deepEqual(await visible(),[0,5,4,3]);
 await page.locator('#next').click();assert.deepEqual(await visible(),[1]);
 assert.equal(await page.locator('#panel').evaluate(e=>e.getBoundingClientRect().width),480);
 assert.equal(await page.locator('#panel-background').evaluate(e=>getComputedStyle(e).opacity),'0.4');
 assert.equal(await page.locator('#panel').evaluate(e=>getComputedStyle(e).opacity),'1');
 assert.equal(await page.locator('.metric-value').first().evaluate(e=>getComputedStyle(e).opacity),'1');
 await page.reload();assert.deepEqual(await visible(),[0,5,4,3]);pass('apply changes order, selection, width and only background alpha; reload restores chart preference');
 await edit();for(const cb of await page.locator('#choices input').all())await cb.uncheck();
 await page.locator('#apply').click();assert.deepEqual(await visible(),[]);
 for(const id of['open-account','open-nocuda','open-personalizer'])assert.equal(await page.locator('#'+id).isVisible(),true);
 await page.reload();assert.deepEqual(await visible(),[]);await shot('empty-selection');pass('empty selection persists and retains all three shared accesses');
 await page.locator('#open-nocuda').click();
 assert.equal(await page.locator('#confirm-channel').isDisabled(),true);
 await page.locator('#channel').selectOption('manual');
 await page.locator('#anchor-a').fill('1,08123');
 await page.locator('#preview-channel').click();
 assert.equal(await page.locator('#confirm-channel').isEnabled(),true);
 await page.locator('#min-nocuda').click();
 await page.locator('#collapse').click();assert.equal(await page.locator('#panel').isVisible(),false);
 await page.locator('#restore').click();
 await page.locator('#open-nocuda').click();
 assert.equal(await page.locator('#anchor-a').inputValue(),'1,08123');
 assert.equal(await page.locator('#confirm-channel').isEnabled(),true);
 await page.locator('#confirm-channel').click();assert.match(await page.locator('#flow-status').innerText(),/fictício confirmado/);
 await shot('nocuda-confirmation');await page.locator('#close-nocuda').click();pass('shared NoCuda access and minimize/panel collapse preserve anchor draft and preview phase');
 await edit();await page.locator('#defaults').click();
 assert.deepEqual(await visible(),[],'restore default is a draft until applied');
 await page.locator('#min-personalizer').click();
 await page.locator('#personalizer-restore').click();
 assert.equal(await page.locator('#choices input:checked').count(),4);
 await page.locator('#apply').click();assert.deepEqual(await visible(),[0,5,3,4]);pass('restore default requires Apply; personalizer minimize preserves draft');
 await edit();for(const cb of await page.locator('#choices input').all())await cb.check();await page.locator('#apply').click();
 assert.deepEqual(await visible(),[0,5,3,4]);await page.locator('#next').click();assert.deepEqual(await visible(),[1,2,6]);
 await edit();await page.locator('#defaults').click();await page.locator('#apply').click();pass('all seven metrics selectable and reachable through panel pagination');
 await page.locator('#open-account').click();
 assert.deepEqual(await page.locator('#account-tabs button').allTextContents(),['Visão geral','Posições e stops','Raiz N','Sistema','Ajustes','Histórico Pessoal']);
 await page.locator('#account details').first().locator('summary').click();
 assert.match(await page.locator('#account details').first().innerText(),/Amostra sintética/);
 for(const tab of await page.locator('#account-tabs button').all()){await tab.click();assert.ok((await page.locator('#account-content').innerText()).length>40)}
 await page.getByRole('button',{name:'Sistema',exact:true}).click();await shot('account-system');
 await page.locator('#min-account').click();await page.locator('#account-restore').click();
 assert.equal(await page.getByRole('button',{name:'Sistema',exact:true}).getAttribute('aria-selected'),'true');
 await page.keyboard.press('Escape');assert.equal(await page.locator('#account').isVisible(),false);pass('six Conta sections, visible reasons/details, tab state retention and Escape');
 const before=await page.locator('#panel').boundingBox();
 const handle=await page.locator('#drag').boundingBox();
 await page.mouse.move(handle.x+35,handle.y+16);await page.mouse.down();await page.mouse.move(handle.x+180,handle.y+60);await page.mouse.up();
 const after=await page.locator('#panel').boundingBox();assert.ok(after.x>before.x+100);pass('header drag moves panel within chart');
 // P2 regression: collapsed restore access must survive chart and viewport shrink after a far-right drag.
 const restoreBounds=[];
 for(const scenario of['small-chart','mobile-resize']){
  const probe=await browser.newPage({viewport:{width:1280,height:1050}});await probe.goto(url);
  const grip=await probe.locator('#drag').boundingBox();
  await probe.mouse.move(grip.x+35,grip.y+15);await probe.mouse.down();await probe.mouse.move(1190,grip.y+15);await probe.mouse.up();
  await probe.locator('#collapse').click();
  if(scenario==='small-chart')await probe.locator('#area').selectOption('small');
  else await probe.setViewportSize({width:320,height:1000});
  await probe.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const bounds=await probe.evaluate(()=>{
   const r=document.getElementById('restore').getBoundingClientRect(),s=document.getElementById('stage').getBoundingClientRect();
   return {restore:{x:r.x,y:r.y,width:r.width,height:r.height},stage:{x:s.x,y:s.y,width:s.width,height:s.height},viewport:innerWidth,inChart:r.left>=s.left&&r.right<=s.right&&r.top>=s.top&&r.bottom<=s.bottom,hit:document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)?.id||null};
  });
  restoreBounds.push({scenario,...bounds});const screenshot=path.join(evidence,'collapsed-restore-'+scenario+'.png');await probe.screenshot({path:screenshot,fullPage:true});screenshots.push(screenshot);
  if(bounds.inChart&&bounds.hit==='restore'){await probe.locator('#restore').click();assert.equal(await probe.locator('#panel').isVisible(),true);const panel=await probe.locator('#panel').boundingBox();assert.ok(panel.x>=bounds.stage.x&&panel.x+panel.width<=bounds.stage.x+bounds.stage.width+1,'restored panel remains within chart')}
  await probe.close();
 }
 await fs.writeFile(path.join(evidence,'restore-bounds-probe.json'),JSON.stringify(restoreBounds,null,2)+'\n');
 for(const bounds of restoreBounds)assert.ok(bounds.inChart&&bounds.hit==='restore',`collapsed restore inaccessible after ${bounds.scenario}: ${JSON.stringify(bounds)}`);
 pass('far-right drag/collapse retains clickable restore within chart after small-area change and 320px viewport resize');
 for(const theme of['light','dark']){
  await page.locator('#theme').selectOption(theme);
  for(const width of[1280,375,320]){
   await page.setViewportSize({width,height:1000});
   await page.locator('#area').selectOption('small');
   await page.locator('#long').check();
   for(const quality of['normal','estimated','na']){
    await page.locator('#quality').selectOption(quality);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${theme}/${width}/${quality}: document overflow`);
    const panelBox=await page.locator('#panel').boundingBox(),stageBox=await page.locator('#stage').boundingBox();
    assert.ok(panelBox.x>=stageBox.x&&panelBox.x+panelBox.width<=stageBox.x+stageBox.width+1);
    assert.equal(await page.locator('#pager').isVisible(),true);
    for(let i=0;i<4;i++){
     const v=page.locator('#metric-list .metric-value');
     assert.equal(await v.evaluate(e=>e.scrollWidth<=e.clientWidth+1),true,'financial value must wrap, not truncate');
     assert.equal(await v.evaluate(e=>getComputedStyle(e).fontSize),'14px','financial text cannot silently shrink');
     assert.equal(await v.evaluate(e=>getComputedStyle(e).textOverflow),'clip');
     const geometry=await v.evaluate(e=>{const b=e.getBoundingClientRect(),p=e.closest('.metric-list').getBoundingClientRect();return {bottom:b.bottom,limit:p.bottom,top:b.top,start:p.top}});
     assert.ok(geometry.bottom<=geometry.limit+1&&geometry.top>=geometry.start-1,'full financial value must fit visible metric region');
     if(quality==='normal'&&i===0)assert.equal(await v.innerText(),'123.456.789.012.345.678,901234567890 ×');
     if(quality==='na')assert.equal(await v.innerText(),'N/A');
     if(i<3)await page.locator('#next').click();
    }
   }
   if(width===375){await page.locator('#quality').selectOption('normal');await shot(`small-long-${theme}`)}
  }
 }
 pass('320/375/1280 px × light/dark × Current/Estimated/N/A; small chart pagination; complete long numbers at 14 px');
 await page.setViewportSize({width:1280,height:1050});await page.locator('#area').selectOption('normal');await page.locator('#long').uncheck();await page.locator('#quality').selectOption('estimated');await shot('desktop-dark-estimated');
 await page.locator('#open-personalizer').click();await page.locator('#width').fill('279');await page.locator('#apply').click();
 assert.equal(await page.locator('#personalizer').isVisible(),true);assert.match(await page.locator('#draft-error').innerText(),/280 e 480/);await close();pass('out-of-range geometry rejected without closing or saving');
 // Persistence failure uses the real UI and a storage error fixture, preserving an existing saved payload.
 const saved=await page.evaluate(()=>localStorage.getItem('jpwealth.preview.stoikus.custom-panel.chart-demo-20261021.v1'));
 await page.addInitScript(()=>{Storage.prototype.setItem=function(){throw new DOMException('fixture write denied','QuotaExceededError')}});
 await page.reload();await edit();await page.locator('#choices').getByRole('checkbox',{name:'P/L flutuante',exact:true}).check();await page.locator('#apply').click();
 assert.match(await page.locator('#storage-status').innerText(),/apenas nesta sessão/);
 assert.equal(await page.evaluate(()=>localStorage.getItem('jpwealth.preview.stoikus.custom-panel.chart-demo-20261021.v1')),saved);pass('denied write clearly reports session-only apply and preserves prior stored preference');
 const invalid=await browser.newPage({viewport:{width:1280,height:1050}});
 await invalid.addInitScript(()=>{localStorage.setItem('jpwealth.preview.stoikus.custom-panel.chart-demo-20261021.v1','{invalid-preview');localStorage.setItem('jpwealth.unrelated.fixture','preserve')});
 await invalid.goto(url);
 assert.deepEqual(await invalid.locator('#metric-list [data-metric]').evaluateAll(els=>els.map(e=>Number(e.dataset.metric))),[0,5,3,4]);
 assert.match(await invalid.locator('#storage-status').innerText(),/temporário/);
 assert.equal(await invalid.evaluate(()=>localStorage.getItem('jpwealth.preview.stoikus.custom-panel.chart-demo-20261021.v1')),'{invalid-preview');
 await invalid.locator('#open-personalizer').click();await invalid.locator('#apply').click();
 assert.equal(await invalid.evaluate(()=>localStorage.getItem('jpwealth.unrelated.fixture')),'preserve');
 await invalid.close();pass('invalid stored record preserved on read; explicit Apply affects only the preview chart key');
 assert.deepEqual(errors,[],'browser errors or failed requests');
 const files=['docs/preview/stoikus-painel-personalizavel/index.html','tools/stoikus_custom_panel_preview_test.mjs'];
 const fingerprints=Object.fromEntries(await Promise.all(files.map(async f=>[f,createHash('sha256').update(await fs.readFile(path.join(root,f))).digest('hex')])));
 const result={status:'PASS',date:new Date().toISOString(),browser:browser.version(),fingerprints,scope:'Standalone browser preview only; native MT5 NOT_RUN',checks,screenshots,errors};
 await fs.writeFile(path.join(evidence,'result.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result,null,2));
}catch(error){await fs.writeFile(path.join(evidence,'failure.json'),JSON.stringify({status:browser?'PRODUCT_FAIL':'ENVIRONMENT_ERROR',error:String(error),stack:error.stack,checks,screenshots,errors},null,2)+'\n');throw error}
finally{await browser?.close();await new Promise(resolve=>server.close(resolve))}

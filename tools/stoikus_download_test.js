'use strict';
// Exercise the public downloader with real SHA-256 and DOM/network seams.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { webcrypto, createHash } = require('node:crypto');
const path = require('node:path');
const text = fs.readFileSync(path.join(__dirname, '../src/js/20-ui/31-tools-services.js'), 'utf8');
const start = text.indexOf('  function initLeverageDownloads(){');
const end = text.indexOf('  function initGenetrixUI(){', start);
assert(start >= 0 && end > start);
const payload = Buffer.from('independent daily archive fixture bytes');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const entry = kind => ({ available: true, path: `downloads/jpw-alavancagem-atual/fixture-${kind}.zip`,
  filename: `fixture-${kind}.zip`, bytes: payload.length, sha256: sha(payload) });
const manifest = () => ({ schemaVersion: 1, version: '1.22.1', validation: {
  compilation: { status: 'pending', detail: 'NOT_RUN' }, terminal: { status: 'pending', detail: 'NOT_RUN' } },
  downloads: { dailySource: entry('dailySource'), source: entry('source'), compiled: entry('compiled') } });
function harness({ metadata = manifest(), bytes = payload, protocol = 'https:', embedded = {}, missingButton, duplicateKind, onFetch, responseOK=true, cryptoAvailable=true, networkFailure=false, redirect307=false, pageURL='https://jp.example/sub/index.html', mime='application/zip' } = {}) {
  const downloads = [], requests=[], blobs=[], notices = { textContent: '', dataset: {} }, metas = new Map(), buttons = {}, extraButtons = {};
  const makeButton = () => ({ disabled: false, textContent: 'Instalador .exe · indisponível', handlers: {}, addEventListener(event, fn) { this.handlers[event] = fn; } });
  for (const kind of ['dailySource', 'source', 'compiled','nativeKit','nativePin','preview','installer']) {
    if (kind === missingButton) continue;
    buttons[kind] = makeButton();
    if(kind === duplicateKind)extraButtons[kind] = makeButton();
  }
  const document = {
    baseURI:'https://untrusted.invalid/base/',
    querySelector(selector) { return buttons[selector.match(/download="([^"]+)"/)?.[1]] || null; },
    querySelectorAll(selector) { const kind = selector.match(/download="([^"]+)"/)?.[1];
      if(kind)return [buttons[kind],extraButtons[kind]].filter(Boolean);
      const name = selector.match(/meta="([^"]+)"/)?.[1];
      if (!metas.has(name)) metas.set(name, { textContent: '' }); return [metas.get(name)]; },
    createElement() { return { href: '', download: '', click() { downloads.push(this.download); }, remove() {} }; },
    currentScript:null,
    getElementById(id){const kind=Object.keys(resources).find(key=>payloads[resources[key].payload].elementId===id)?.split('/')[1],data=embedded[kind];
      return (protocol==='file:'||kind==='preview')&&data&&typeof data.base64==='string'?{type:'application/json',textContent:JSON.stringify({schemaVersion:1,buildId:'fixture',id:resources['leverage/'+kind].payload,files:{['leverage/'+kind]:data.base64}})}:null;},
    head:{appendChild(script){queueMicrotask(()=>{document.currentScript=script;script.onerror();document.currentScript=null;});}},
    body: { append() {} }
  };
  const context = vm.createContext({ window: { JPW_LEVERAGE_MANIFEST: metadata, JPW_LEVERAGE_FILES: embedded },
    downloadAction:()=>({signal:undefined,current:()=>true,done(){}}),
    document, el: () => notices, location: { protocol, href:pageURL }, Uint8Array, Blob, crypto:cryptoAvailable?webcrypto:{},
    fetch: async (url, options) => { requests.push({url,options});if(redirect307&&options?.redirect==='error')throw new Error('Hosted 307 redirect refused');if(networkFailure)throw new Error('Network unavailable');if(onFetch)await onFetch({buttons,extraButtons});
      return { ok: responseOK&&!redirect307, headers:{get:()=>mime}, arrayBuffer: async () => Uint8Array.from(bytes).buffer }; },
    URL: class extends URL { static createObjectURL(blob) {blobs.push(blob);return 'blob:fixture';} static revokeObjectURL() {} }, setTimeout() {},
    atob: value => Buffer.from(value, 'base64').toString('binary') });
  const resources={},payloads={};
  const all={...(metadata?.downloads||{}),...(metadata?.interfaceRelease?.artifacts||{})};
  for(const [kind,item] of Object.entries(all))if(item?.available){
    const group='leverage-'+({dailySource:'daily-source',nativeKit:'native-kit',nativePin:'native-pin'}[kind]||kind);
    resources['leverage/'+kind]={...item,mime:kind==='preview'?'text/html':kind==='nativePin'?'application/json':'application/zip',payload:group};
    payloads[group]={path:'src/vendor/downloads/'+group+'-payload.js',elementId:'jpw-download-payload-'+group};
    if(embedded[kind]&&embedded[kind].mime!==resources['leverage/'+kind].mime)resources['leverage/'+kind].mime=embedded[kind].mime;
  }
  context.window.JPW_DOWNLOAD_MANIFEST={schemaVersion:1,buildId:'fixture',resources,payloads};
  Object.assign(context,{TextDecoder,AbortController,DOMException,clearTimeout(){},queueMicrotask});
  vm.runInContext("const JP_WEALTH_BUILD_ID='fixture';",context);
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../src/js/00-core/10-download-assets.js'),'utf8'),context);
  vm.runInContext(text.slice(start, end) + '\ninitLeverageDownloads();', context);
  return { buttons, extraButtons, metas, notices, downloads, requests, blobs,
    async click(kind, second = false) { const button = (second ? extraButtons : buttons)[kind];
      if (button?.handlers.click) await button.handlers.click(); } };
}
(async () => {
  for(const releaseRevision of ['R4','R5']){
  for (const kind of ['dailySource', 'source', 'compiled']) {
    const h = harness();
    assert.equal(h.buttons[kind].disabled, false);
    await h.click(kind);
    assert.deepEqual(h.downloads, [`fixture-${kind}.zip`], `${kind} did not pass integrity verification`);
    assert.match(h.notices.textContent, /verificado/);
  }
  const repeated = harness({ duplicateKind: 'dailySource', onFetch({buttons,extraButtons}) {
    assert(buttons.dailySource.disabled && extraButtons.dailySource.disabled, 'all entries of a kind must lock during verification');
  } });
  await repeated.click('dailySource', true);
  assert.deepEqual(repeated.downloads, ['fixture-dailySource.zip'], 'second daily entry lacks a listener');
  assert(!repeated.buttons.dailySource.disabled && !repeated.extraButtons.dailySource.disabled);
  for (const [bytes, expected] of [[Buffer.concat([payload, Buffer.from('x')]), /Tamanho/],
      [Buffer.alloc(payload.length, 120), /Hash/]]) {
    const h = harness({ bytes }); await h.click('dailySource');
    assert.deepEqual(h.downloads, []); assert.match(h.notices.textContent, expected);
    assert.equal(h.notices.dataset.state, 'error');
  }
  const old = manifest(); delete old.downloads.dailySource;
  const legacy = harness({ metadata: old });
  assert.equal(legacy.buttons.dailySource.disabled, true);
  await legacy.click('dailySource'); assert.deepEqual(legacy.downloads, []);
  await legacy.click('source'); assert.deepEqual(legacy.downloads, ['fixture-source.zip']);
  for (const metadata of [null, { schemaVersion: 99 }, { ...manifest(), version: 'untrusted' }]) {
    const h = harness({ metadata });
    assert(Object.values(h.buttons).every(button => button.disabled));
    await h.click('dailySource'); assert.deepEqual(h.downloads, []);
  }
  for (const delta of [{ path: 'downloads/jpw-alavancagem-atual/../bad.zip' },
      { filename: 'wrong.zip' }, { bytes: 0 }, { bytes: Number.MAX_SAFE_INTEGER + 1 },
      { sha256: '0'.repeat(63) }, { available: false }]) {
    const metadata = manifest(); Object.assign(metadata.downloads.dailySource, delta);
    const h = harness({ metadata }); assert.equal(h.buttons.dailySource.disabled, true);
    await h.click('dailySource'); assert.deepEqual(h.downloads, []);
  }
  const embedded = { dailySource: { mime: 'application/zip', base64: payload.toString('base64') } };
  const offline = harness({ protocol: 'file:', embedded }); await offline.click('dailySource');
  assert.deepEqual(offline.downloads, ['fixture-dailySource.zip']);
  const corrupt = harness({ protocol: 'file:', embedded: { dailySource: {
    mime: 'application/zip', base64: Buffer.alloc(payload.length, 120).toString('base64') } } });
  await corrupt.click('dailySource'); assert.deepEqual(corrupt.downloads, []); assert.match(corrupt.notices.textContent, /Hash/);
  for (const embedded of [{}, { dailySource: { mime: 'text/html', base64: payload.toString('base64') } }]) {
    const h = harness({ protocol: 'file:', embedded }); await h.click('dailySource');assert.deepEqual(h.downloads,[]);
  }
  harness({ missingButton: 'dailySource' });
  const artifactSpecs=releaseRevision==='R4'?{nativeKit:['Kit_Windows_Stoikus_Assinatura_R4.zip','application/zip'],nativePin:['root-pin-R4.json','application/json'],preview:['Previa_Stoikus_Interface_R4.html','text/html']}:{nativeKit:['Kit_Windows_Stoikus_Janelas_R5.zip','application/zip'],nativePin:['root-pin-R5.json','application/json'],preview:['Previa_Stoikus_Janelas_R5.html','text/html']};
  function interfaceManifest(){const m=manifest();m.version=releaseRevision==='R4'?'1.22.3':'1.23.0';m.downloads.compiled={available:false,reason:'SOURCE_ONLY'};
    m.interfaceRelease={revision:releaseRevision,candidate:m.version+'-interface',archiveVariant:releaseRevision==='R4'?'interface':'',state:'SOURCE_ONLY_NATIVE_PENDING',nativeCompilation:'NOT_RUN',nativeRuntime:'NOT_RUN',humanAcceptance:'NOT_RUN',windowsX64:'NOT_RUN',artifacts:{}};
    for(const [kind,[filename]] of Object.entries(artifactSpecs))m.interfaceRelease.artifacts[kind]={available:true,path:'downloads/jpw-alavancagem-atual/'+filename,filename,bytes:payload.length,sha256:sha(payload)};
    return m;}
  // Hosted Sites canonicalizes .html with 307 and injects markup into HTML.
  // Delivery must use the immutable preview already embedded by the build.
  const hostedPreview=fs.readFileSync(path.join(__dirname,'../downloads/jpw-alavancagem-atual/',artifactSpecs.preview[0]));
  const hostedMetadata=interfaceManifest();Object.assign(hostedMetadata.interfaceRelease.artifacts.preview,{bytes:hostedPreview.length,sha256:sha(hostedPreview)});
  for(const network of [{redirect307:true},{bytes:Buffer.concat([hostedPreview,Buffer.from('<script>hosting injection</script>')])}]){
    const hosted=harness({metadata:hostedMetadata,embedded:{preview:{mime:'text/html',base64:hostedPreview.toString('base64')}},...network});
    await hosted.click('preview');assert.deepEqual(hosted.downloads,[artifactSpecs.preview[0]],'hosted preview must use pinned embedded bytes despite 307/injected HTML');
    assert.equal(hosted.requests.length,0,'preview must not depend on the host HTML route');
    assert.equal(sha(Buffer.from(await hosted.blobs[0].arrayBuffer())),sha(hostedPreview));
  }
  function artifactHarness(kind,options={}){
    const bytes=options.bytes||payload;
    const embedded=Object.hasOwn(options,'embedded')?options.embedded:kind==='preview'?{preview:{mime:'text/html',base64:bytes.toString('base64')}}:{};
    return harness({...options,embedded});
  }
  for(const [kind,[filename,mime]] of Object.entries(artifactSpecs)){
    const metadata=interfaceManifest();
    const good=artifactHarness(kind,{metadata});await good.click(kind);
    assert.deepEqual(good.downloads,[filename]);assert.equal(good.blobs[0].type,mime);
    if(kind==='preview')assert.equal(good.requests.length,0);
    else{assert.equal(good.requests[0].url,'https://jp.example/sub/downloads/jpw-alavancagem-atual/'+filename);assert.equal(good.requests[0].options.redirect,'error');}
    assert(good.buttons.compiled.disabled,'interface release must remain source-only');
    for(const [bytes, expected] of [[Buffer.concat([payload,Buffer.from('x')]),/Tamanho/],[Buffer.alloc(payload.length,120),/Hash/]]){
      const h=artifactHarness(kind,{metadata,bytes});await h.click(kind);assert.deepEqual(h.downloads,[]);assert.match(h.notices.textContent,expected);}
    for(const delta of [{path:'https://other.example/'+filename},{path:'downloads/jpw-alavancagem-atual/../'+filename},{path:'downloads/jpw-alavancagem-atual/%2e%2e/'+filename},{path:'downloads/jpw-alavancagem-atual/'+filename+'?x'},{path:'downloads/jpw-alavancagem-atual/other.'+filename.split('.').pop()},{filename:'wrong.zip'},{bytes:0},{sha256:'bad'},{available:false}]){
      const bad=interfaceManifest();Object.assign(bad.interfaceRelease.artifacts[kind],delta);const h=artifactHarness(kind,{metadata:bad});assert(h.buttons[kind].disabled);await h.click(kind);assert.deepEqual(h.downloads,[]);}
    const off=harness({metadata,protocol:'file:',embedded:{[kind]:{mime,base64:payload.toString('base64')}}});await off.click(kind);assert.deepEqual(off.downloads,[filename]);assert.equal(off.requests.length,0);
    const broken=harness({metadata,protocol:'file:',embedded:{[kind]:{mime,base64:Buffer.alloc(payload.length,120).toString('base64')}}});await broken.click(kind);assert.deepEqual(broken.downloads,[]);assert.match(broken.notices.textContent,/Hash/);
    const absent=harness({metadata,protocol:'file:'});await absent.click(kind);assert.deepEqual(absent.downloads,[]);assert.equal(absent.notices.dataset.state,'error');
    assert(harness({metadata,protocol:'file:',embedded:{[kind]:{mime:'bad/mime',base64:payload.toString('base64')}}}).buttons[kind].disabled);
    for(const delta of [{responseOK:false},{networkFailure:true},{redirect307:true},{cryptoAvailable:false}]){const h=artifactHarness(kind,{metadata,...delta});await h.click(kind);if(kind==='preview'&&delta.cryptoAvailable!==false){assert.deepEqual(h.downloads,[filename]);assert.equal(h.requests.length,0);}else{assert.deepEqual(h.downloads,[]);assert.equal(h.notices.dataset.state,'error');}assert(!h.buttons[kind].disabled);}
    // A real concurrent second click must not initiate a second fetch/save.
    let releaseFetch;const lock=artifactHarness(kind,{metadata,duplicateKind:kind,onFetch:()=>new Promise(resolve=>{releaseFetch=resolve;})});
    const first=lock.click(kind);assert(lock.buttons[kind].disabled&&lock.extraButtons[kind].disabled);await lock.click(kind,true);assert.equal(lock.requests.length,kind==='preview'?0:1);if(releaseFetch)releaseFetch();await first;assert.deepEqual(lock.downloads,[filename]);
    const real=fs.readFileSync(path.join(__dirname,'../downloads/jpw-alavancagem-atual/',filename));
    metadata.interfaceRelease.artifacts[kind].bytes=real.length;metadata.interfaceRelease.artifacts[kind].sha256=sha(real);
    const actual=artifactHarness(kind,{metadata,bytes:real});await actual.click(kind);assert.deepEqual(actual.downloads,[filename]);
    const altered=Buffer.from(real);altered[altered.length-1]^=1;const refuse=artifactHarness(kind,{metadata,bytes:altered});await refuse.click(kind);assert.deepEqual(refuse.downloads,[]);
  }
  for(const protocol of ['https:','http:','file:']){
    for(const embedded of [{},{preview:{mime:'text/plain',base64:hostedPreview.toString('base64')}},{preview:{mime:'text/html'}}]){
      const missing=harness({metadata:hostedMetadata,protocol,embedded});await missing.click('preview');assert.deepEqual(missing.downloads,[]);assert.equal(missing.requests.length,0);
    }
    const changed=Buffer.from(hostedPreview);changed[changed.length-1]^=1;
    for(const bytes of [changed,hostedPreview.subarray(0,-1)]){
      const corrupt=harness({metadata:hostedMetadata,protocol,embedded:{preview:{mime:'text/html',base64:bytes.toString('base64')}}});await corrupt.click('preview');assert.deepEqual(corrupt.downloads,[]);assert.equal(corrupt.notices.dataset.state,'error');assert.equal(corrupt.requests.length,0,'corrupt embedded preview must never fall back to HTTP');
    }
  }
  // Embedded availability must not weaken the existing network-only guards
  // for SDK/daily archives or the other two interface artifacts on HTTP/S.
  for(const kind of ['source','dailySource','nativeKit','nativePin']){
    const metadata=interfaceManifest(),mime=artifactSpecs[kind]?.[1]||'application/zip';
    const guarded=harness({metadata,redirect307:true,embedded:{[kind]:{mime,base64:payload.toString('base64')}}});
    await guarded.click(kind);assert.deepEqual(guarded.downloads,[]);assert.equal(guarded.requests.length,1);assert.equal(guarded.requests[0].options.redirect,'error');
  }
  console.log('PASS installer release guard, version, filename, native receipt, MIME, size/hash and portable exclusion');
  console.log('PASS hosted preview pinned bytes despite 307/injected HTML; missing/wrong MIME/corrupt embedded preview refused without network fallback on HTTP/HTTPS/file');
  for(const change of [m=>delete m.interfaceRelease,m=>{m.interfaceRelease.revision='R2';},m=>{m.interfaceRelease.candidate='1.22.1-interface';},m=>{m.interfaceRelease.state='PASSED';},m=>{m.interfaceRelease.nativeCompilation='PASS';},m=>{m.downloads.compiled=entry('compiled');}]){
    const metadata=interfaceManifest();change(metadata);const h=artifactHarness('preview',{metadata});assert(['nativeKit','nativePin','preview'].every(k=>h.buttons[k].disabled));await h.click('source');assert.deepEqual(h.downloads,['fixture-source.zip']);}
  console.log('PASS '+releaseRevision+' nativeKit/nativePin/preview real bytes and MIME; size/hash/corruption/path refusal; offline and network errors; no crypto; optional metadata; page URL; concurrent double click');
  const installer = () => ({ available: true, installerVersion: '1.0.0-beta.1', productVersion: '1.23.0',
    platform: 'win-x64', unsigned: true, filename: 'Stoikus_Setup_1.0.0-beta.1_win-x64.exe',
    path: 'downloads/jpw-alavancagem-atual/Stoikus_Setup_1.0.0-beta.1_win-x64.exe',
    releaseUrl: 'https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/releases/download/installer-v1.0.0-beta.1/Stoikus_Setup_1.0.0-beta.1_win-x64.exe',
    sha256: sha(payload), bytes: payload.length,
    nativeTests: { windowsX64: 'PASS', parallelsArm: 'PASS', browser: 'PASS' },
    nativeEvidence: Object.fromEntries(['windowsX64','parallelsArm','browser'].map(stage => [stage,
      {path: `docs/validation/stoikus-installer/${stage}.json`, sha256: sha(payload)}])) });
  const installerRelease=manifest();installerRelease.version='1.23.0';installerRelease.downloads.installer=installer();
  const enabledInstaller=harness({metadata:installerRelease,mime:'application/octet-stream'});
  assert.equal(enabledInstaller.buttons.installer.disabled,false,'verified installer metadata must enable its explicit download');
  await enabledInstaller.click('installer');assert.deepEqual(enabledInstaller.downloads,[installer().filename]);
  assert.equal(enabledInstaller.requests[0].url,installer().releaseUrl,'installer must use the declared repository release URL');
  const offlineInstaller=harness({metadata:installerRelease,protocol:'file:'});
  assert.equal(offlineInstaller.buttons.installer.disabled,true,'installer must never be embedded in the portable page');
  for(const delta of [{available:false},{productVersion:'1.22.1'},{filename:'Stoikus_Setup_other.exe'},
    {nativeTests:{windowsX64:'NOT_RUN',parallelsArm:'PASS',browser:'PASS'}},
    {releaseUrl:'https://evil.example/setup.exe'},{nativeEvidence:null},{unsigned:false},
    {releaseUrl:installer().releaseUrl+'?unsafe=1'},{path:'downloads/jpw-alavancagem-atual/../bad.exe'}]){
    const metadata=structuredClone(installerRelease);metadata.downloads.installer={...installer(),...delta};
    const h=harness({metadata});assert.equal(h.buttons.installer.disabled,true);
    await h.click('installer');assert.deepEqual(h.downloads,[]);
  }
  for(const [opts,expected] of [[{mime:'text/html'},/Tipo/],
    [{mime:'application/octet-stream',bytes:Buffer.alloc(payload.length,120)},/Hash/],
    [{mime:'application/octet-stream',bytes:Buffer.concat([payload,Buffer.from('x')])},/Tamanho/]]){
    const h=harness({metadata:installerRelease,...opts});await h.click('installer');
    assert.deepEqual(h.downloads,[]);assert.match(h.notices.textContent,expected);
  }
  console.log('PASS daily/source/compiled online; daily offline; corrupt size/hash; legacy and invalid manifests; unsafe records; absent button');
  }
})().catch(error => { console.error(error); process.exitCode = 1; });

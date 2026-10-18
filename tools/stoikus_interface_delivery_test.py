#!/usr/bin/env python3
"""Exercise real derivative build and service-worker code using bounded fixtures.

The package generator is a fixture boundary: sealed R4/R5 source generation is
tested separately. These tests never rebuild the working tree or alter releases.
"""
from copy import deepcopy
from pathlib import Path
import ast
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = (os.environ.get('JPW_NODE') or shutil.which('node') or str(Path.home() /
    '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'))
PREFIX = 'downloads/jpw-alavancagem-atual/'
ARTIFACTS = {
    'nativeKit': ('Kit_Windows_Stoikus_Assinatura_R4.zip', 'application/zip', b'PK\x03\x04kit-fixture'),
    'nativePin': ('root-pin-R4.json', 'application/json', b'{"native":"NOT_RUN"}\n'),
    'preview': ('Previa_Stoikus_Interface_R4.html', 'text/html', b'<!doctype html><p>Fictitious preview</p>'),
}


def record(filename, raw):
    return dict(available=True, path=PREFIX + filename, filename=filename,
                bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def fixture_manifest(interface=True):
    old_zip = b'PK\x03\x04historical-source-fixture'
    manifest = dict(schemaVersion=1, version='1.22.3', sourceFiles=['fixture.mq5'],
                    validation={'compilation': {'status': 'pending'}, 'terminal': {'status': 'pending'}},
                    downloads={'source': record('historical-source.zip', old_zip),
                               'compiled': {'available': False, 'path': None}})
    if interface:
        manifest['interfaceRelease'] = dict(
            revision='R4', candidate='1.22.3-interface', archiveVariant='interface',
            state='SOURCE_ONLY_NATIVE_PENDING', nativeCompilation='NOT_RUN',
            nativeRuntime='NOT_RUN', humanAcceptance='NOT_RUN', windowsX64='NOT_RUN',
            artifacts={key: record(name, raw) for key, (name, _mime, raw) in ARTIFACTS.items()})
    return manifest


# Real WebCrypto/Response bytes; CacheStorage and network are explicit external
# boundaries. Installation and fetch handlers are the unmodified production SW.
SW_HARNESS = r'''
const vm = require('node:vm'), fs = require('node:fs');
const {webcrypto} = require('node:crypto');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const base = 'https://example.test/wealth/sw.js';
const manifestURL = new URL('./downloads/jpw-alavancagem-atual/manifest.json', base).href;
const previewURL = new URL(input.manifest.interfaceRelease?.artifacts?.preview?.path||'downloads/jpw-alavancagem-atual/Previa_Stoikus_Interface_R4.html',base).href;
const normal = value => new URL(value.url || value, base).href;
const listeners = {}, stored = new Map(), requested = [], deleted = [];
let offline = false,workerPayload;
async function network(value) {
  const url = normal(value); requested.push(url);
  if (offline || url === input.missing) throw new Error('fixture network unavailable');
  if (url === manifestURL) return new Response(JSON.stringify(input.manifest));
  if (url.endsWith('/src/vendor/downloads/leverage-preview-payload.json')) {
    if(input.workerMutation?.missing)return new Response('missing',{status:404});
    const path=require('node:path').join(require('node:path').dirname(input.generated),'src/vendor/downloads/leverage-preview-payload.json');
    let raw=fs.readFileSync(path),envelope=JSON.parse(raw);
    if(input.outerCorrupt){raw=Buffer.from(raw);raw[raw.length-1]^=1;return new Response(raw);}
    if(input.workerMutation){const mutation=input.workerMutation;
      if(mutation.staleBuild)envelope.buildId='unrelated-build';
      if(mutation.wrongGroup)envelope.id='leverage-source';
      if(Object.hasOwn(mutation,'base64'))envelope.files['leverage/preview']=mutation.base64;
      if(mutation.corrupt){const bytes=Buffer.from(envelope.files['leverage/preview'],'base64');bytes[bytes.length-1]^=1;envelope.files['leverage/preview']=bytes.toString('base64');}
      raw=Buffer.from(JSON.stringify(envelope));
      // Bind deliberately malformed inner fixture to its outer envelope so the inner guards execute.
      const p=context.self.JPW_DOWNLOAD_MANIFEST.payloads['leverage-preview'];p.envelopeBytes=raw.length;p.envelopeSha256=require('node:crypto').createHash('sha256').update(raw).digest('hex');
    }
    workerPayload={mime:context.self.JPW_DOWNLOAD_MANIFEST.resources['leverage/preview'].mime,base64:envelope.files['leverage/preview']};
    return new Response(raw);
  }
  if (url === previewURL && input.hostedHTML === 'redirect')
    return new Response(null,{status:307,headers:{Location:'https://example.test/wealth/canonical-preview'}});
  if (url === previewURL && input.hostedHTML === 'injection')
    return new Response('<!doctype html><script>hostInjected=true</script><p>Transformed preview</p>');
  if (Object.hasOwn(input.files, url)) return new Response(Buffer.from(input.files[url], 'base64'));
  return new Response('fixture static input');
}
const cache = {
  async addAll(urls) { for(const url of urls) {
    const response=await network(url);
    if(!response.ok)throw new Error('fixture addAll refuses HTTP '+response.status);
    stored.set(normal(url),response);
  } },
  async put(url,response) {stored.set(normal(url),response.clone());},
  async match(url) { return stored.get(normal(url))?.clone(); }
};
const priorCache = 'jp-wealth-previous-build';
const cacheNames = new Set([priorCache]);
const context = {
  URL, Response, Uint8Array, TextDecoder, crypto:webcrypto, JP_WEALTH_BUILD_ID:'fixture',
  atob,btoa,
  importScripts(relative) {
    if(relative!=='./build-id.js')throw new Error('unexpected worker import');
    vm.runInContext(fs.readFileSync(input.generated,'utf8'),context,{filename:input.generated});
    if(input.workerMutation?.mime)context.self.JPW_DOWNLOAD_MANIFEST.resources['leverage/preview'].mime=input.workerMutation.mime;
  }, fetch:network,
  caches:{async open(name){cacheNames.add(name);return cache;},
    async delete(name){deleted.push(name);return cacheNames.delete(name);},
    async keys(){return [...cacheNames];}},
  self:{location:new URL(base), clients:{async claim(){}},
    addEventListener(name, handler){listeners[name] = handler;}}
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(input.sw, 'utf8'), context, {filename:'sw.js'});
(async()=>{
  let install;
  listeners.install({waitUntil(promise){install=promise;}});
  try { await install; }
  catch(error) { process.stdout.write(JSON.stringify({ok:false,error:error.message,requested,deleted,
    priorPreserved:cacheNames.has(priorCache)})); return; }
  if(input.removePreviewCache)stored.delete(previewURL);
  offline = true;
  const offlineFiles = {},offlineTypes={};
  for(const url of input.probes) {
    let result;
    listeners.fetch({request:{method:'GET',url,mode:url.endsWith('.js')?'no-cors':'navigate'},respondWith(value){result=value;}});
    try { const response=await result;offlineTypes[url]=response.headers.get('Content-Type');
      offlineFiles[url] = Buffer.from(await response.arrayBuffer()).toString('base64'); }
    catch(error) { offlineFiles[url] = {error:error.message}; }
  }
  process.stdout.write(JSON.stringify({ok:true,requested,deleted,offlineFiles,offlineTypes,
    workerPayload,windowPresent:Object.hasOwn(context,'window'),
    priorPreserved:cacheNames.has(priorCache)}));
})();
'''


# Execute the actual generated bootstrap, then the real page initializer. No
# MIME metadata is recreated by this harness. Blob/download/network are the DOM
# boundaries; the real consumer performs enablement, size and SHA verification.
PAGE_HARNESS = r'''
const vm=require('node:vm'),fs=require('node:fs');
const {webcrypto}=require('node:crypto');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const notices={textContent:'',dataset:{}},buttons={},blobs=new Map(),downloads=[];
let networkRequests=0,portableSource='',context;
const payloadNodes=new Map();
function mutateEnvelope(envelope){const m=input.mutation;if(!m)return envelope;const key='leverage/'+m.kind;if(m.missing)delete envelope.files[key];if(Object.hasOwn(m,'base64'))envelope.files[key]=m.base64;if(m.corrupt){const raw=Buffer.from(envelope.files[key],'base64');raw[raw.length-1]^=1;envelope.files[key]=raw.toString('base64');}return envelope;}
const document={
  currentScript:null,
  getElementById(id){const value=payloadNodes.get(id);return value?{type:'application/json',textContent:JSON.stringify(mutateEnvelope(JSON.parse(value)))}:null;},
  head:{appendChild(script){queueMicrotask(()=>{document.currentScript=script;
    try{let source=fs.readFileSync(require('node:path').join(require('node:path').dirname(input.generated),new URL(script.src).pathname.split('/src/')[1]?'src/'+new URL(script.src).pathname.split('/src/')[1]:''),'utf8');
      const envelope=mutateEnvelope(JSON.parse(source.split(/,(.*)/s)[1].replace(/\);\s*$/,'')));
      context.window.JPWDownloadAssets.register(envelope.id,envelope);
    }catch(error){script.onerror();}finally{document.currentScript=null;}});}},
  querySelectorAll(selector){
    const kind=selector.match(/download="([^"]+)"/)?.[1];
    if(!kind)return [];
    if(!buttons[kind])buttons[kind]={disabled:false,handlers:{},addEventListener(event,fn){this.handlers[event]=fn;}};
    return [buttons[kind]];
  },
  createElement(){return {dataset:{},href:'',download:'',click(){downloads.push({filename:this.download,blob:blobs.get(this.href)});},remove(){}};},
  body:{append(){}}
};
context=vm.createContext({window:{},document,el:()=>notices,
  downloadAction:()=>({signal:undefined,current:()=>true,done(){}}),TextDecoder,AbortController,DOMException,queueMicrotask,clearTimeout(){},
  location:{protocol:input.protocol||'file:',href:input.pageURL},Uint8Array,Blob,crypto:webcrypto,
  URL:class extends URL {
    static createObjectURL(blob){const url='blob:fixture-'+blobs.size;blobs.set(url,blob);return url;}
    static revokeObjectURL(){}
  },
  fetch(){networkRequests++;
    if(input.hostedHTML==='redirect')return Promise.resolve(new Response(null,{status:307}));
    if(input.hostedHTML==='injection')return Promise.resolve(new Response('<p>Host transformed preview</p>'));
    throw Error('file mode must use generated embedded bytes');},
  setTimeout(){},atob:value=>Buffer.from(value,'base64').toString('binary')});
let bootstrap=fs.readFileSync(input.generated,'utf8');
if(input.portable){
  const match=bootstrap.match(/<script>([\s\S]*?)<\/script>/);
  if(!match)throw Error('Generated portable bootstrap missing');
  portableSource=bootstrap;for(const match of bootstrap.matchAll(/<script type="application\/json" id="([^"]+)">(.*?)<\/script>/g))payloadNodes.set(match[1],match[2]);
  bootstrap=match[1];
}
vm.runInContext(bootstrap,context,{filename:input.generated});
const kinds=Object.keys(context.window.JPW_LEVERAGE_MANIFEST.interfaceRelease.artifacts);
if(input.mutation?.mime)context.window.JPW_DOWNLOAD_MANIFEST.resources['leverage/'+input.mutation.kind].mime=input.mutation.mime;
vm.runInContext(fs.readFileSync(input.loader,'utf8'),context,{filename:input.loader});
const source=fs.readFileSync(input.consumer,'utf8');
const start=source.indexOf('  function initLeverageDownloads(){');
const end=source.indexOf('  function initGenetrixUI(){',start);
if(start<0||end<=start)throw Error('Production downloader initializer missing');
vm.runInContext(source.slice(start,end)+'\ninitLeverageDownloads();',context,{filename:input.consumer});
(async()=>{
  const enabled=Object.fromEntries(kinds.map(kind=>[kind,!buttons[kind].disabled]));
  const outcomes={};
  for(const kind of input.onlyKinds||kinds){
    const first=downloads.length;
    await buttons[kind].handlers.click();
    outcomes[kind]={state:notices.dataset.state,notice:notices.textContent,
      downloads:await Promise.all(downloads.slice(first).map(async item=>({
        filename:item.filename,mime:item.blob.type,base64:Buffer.from(await item.blob.arrayBuffer()).toString('base64')})))};
  }
  process.stdout.write(JSON.stringify({enabled,outcomes,networkRequests}));
})();
'''


class DeliveryTest(unittest.TestCase):
    revision = "R4"
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='jpw-interface-delivery-')
        self.root = Path(self.tmp.name)
        self.manifest = fixture_manifest()
        # Inputs deliberately fixed independently of the generated manifest
        # boundary, so changing a pinned artifact proves its own fingerprint.
        static_files = (
            'index.html', 'src/styles/app.css', 'sw.js', 'fixture.mq5',
            'downloads/jpw-alavancagem-atual/manifest.json',
            'docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf',
            'docs/normative/ANEXO_PARAMETRICO_CANONICO.md',
            'downloads/nocuda/Nocuda_Tool.ex5', 'downloads/nocuda/Nocuda_Tool.pine',
            'downloads/nocuda/Nocuda_Tool.mq5', 'downloads/nocuda/TRADINGVIEW-LEIA-ME.md',
            'downloads/nocuda/MT5-LEIA-ME.md', 'README.md', 'CHANGELOG.md',
            'manifests/jp-wealth.webmanifest', 'manifests/jp-wealth-black.webmanifest',
            'assets/jp-wealth-brand-red.png', 'assets/jp-wealth-brand-black.png',
            'assets/jp-wealth-logo.png', 'assets/nocuda-tradingview.png',
            'assets/nocuda-metatrader.png', 'assets/pwa-icon-primary.png',
            'assets/pwa-icon-primary-192.png', 'assets/pwa-icon-primary-512.png',
            'assets/pwa-icon-secondary.png', 'assets/pwa-icon-secondary-192.png',
            'assets/pwa-icon-secondary-512.png')
        for relative in static_files:
            self.write(relative, b'fixed fixture bytes\n')
        self.write('index.html', b'<html><head><link rel="stylesheet" href="src/styles/app.css"></head><body>\n<script src="build-id.js"></script>\n</body></html>')
        self.write('src/js/manifest.json', b'{"files":[]}')
        self.write(PREFIX + 'historical-source.zip', b'PK\x03\x04historical-source-fixture')
        for name, _mime, raw in ARTIFACTS.values():
            self.write(PREFIX + name, raw)
        self.write('tools/rebuild_monolith.py', (ROOT / 'tools/rebuild_monolith.py').read_bytes())
        # The real offline builder requires its declared Market inputs even in
        # this bounded distribution fixture; preserve the production integrity checks.
        market_inputs = next(ast.literal_eval(node.value)
            for node in ast.parse((ROOT / 'tools/rebuild_monolith.py').read_text()).body
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and
                target.id == 'MARKET_HOURS_BUILD_INPUTS' for target in node.targets))
        for relative in market_inputs:
            self.write(relative, (ROOT / relative).read_bytes())
        self.write('tools/build_leverage_package.py',
            b'import json\ndef build(root):\n    return json.loads((root/"fixture-manifest.json").read_text())\n')

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, relative, raw):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def build(self, manifest=None):
        self.write('fixture-manifest.json', json.dumps(manifest or self.manifest).encode())
        return subprocess.run([sys.executable, 'tools/rebuild_monolith.py'],
                              cwd=self.root, text=True, capture_output=True)

    def payload(self):
        raw = (self.root / 'build-id.js').read_text()
        metadata = json.JSONDecoder().raw_decode(raw.split('window.JPW_DOWNLOAD_MANIFEST = ', 1)[1])[0]
        files = {}
        for key, item in metadata['resources'].items():
            if not key.startswith('leverage/'):
                continue
            script = (self.root / metadata['payloads'][item['payload']]['path']).read_text()
            envelope = json.loads(script.split(',', 1)[1].removesuffix(');\n'))
            files[key.split('/')[1]] = dict(mime=item['mime'], base64=envelope['files'][key])
        return files

    def test_historical_build_retains_zip_payload_and_ignores_undeclared_files(self):
        old = fixture_manifest(False)
        result = self.build(old)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = self.payload()
        self.assertEqual(set(payload), {'source'})
        self.assertEqual(payload['source']['mime'], 'application/zip')
        self.assertEqual(base64.b64decode(payload['source']['base64']), b'PK\x03\x04historical-source-fixture')
        first = (self.root / 'build-id.js').read_bytes()
        self.write(PREFIX + ARTIFACTS['nativeKit'][0], b'undeclared-new-bytes')
        self.assertEqual(self.build(old).returncode, 0)
        self.assertEqual((self.root / 'build-id.js').read_bytes(), first)

    def test_portable_embeds_three_exact_artifacts_with_matching_mime_and_bytes(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = self.payload()
        self.assertEqual(set(payload), {'source', 'nativeKit', 'nativePin', 'preview'})
        portable = (self.root / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').read_text()
        metadata = json.JSONDecoder().raw_decode(portable.split('window.JPW_DOWNLOAD_MANIFEST = ', 1)[1])[0]
        envelopes = [json.loads(raw) for raw in re.findall(r'<script type="application/json" id="jpw-download-payload-[^"]+">(.*?)</script>',portable)]
        portable_payload = {key.split('/')[1]:dict(mime=metadata['resources'][key]['mime'],base64=value) for envelope in envelopes for key,value in envelope['files'].items() if key.startswith('leverage/')}
        self.assertNotIn('base64', (self.root / 'build-id.js').read_text())
        self.assertEqual(portable_payload, payload)
        for kind, (_name, mime, raw) in ARTIFACTS.items():
            self.assertEqual(payload[kind]['mime'], mime)
            self.assertEqual(base64.b64decode(payload[kind]['base64']), raw)

    def test_declared_artifact_bytes_participate_in_build_fingerprint(self):
        self.assertEqual(self.build().returncode, 0)
        first = (self.root / 'build-id.js').read_text().splitlines()[1]
        raw = b'{"native":"NOT_RUN","fixtureRevision":2}\n'
        self.write(PREFIX + ARTIFACTS['nativePin'][0], raw)
        self.manifest['interfaceRelease']['artifacts']['nativePin'] = record(ARTIFACTS['nativePin'][0], raw)
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual((self.root / 'build-id.js').read_text().splitlines()[1], first)

    def pinned_artifact_build(self):
        # Independent historical/current pins: the live R5 manifest cannot stand in for R4.
        from stoikus_interface_package_test import ASSETS as R4_PINS
        from stoikus_r5_release_test import ASSETS as R5_PINS
        pins = R5_PINS if self.revision == 'R5' else R4_PINS
        approved = {}
        for key, (filename, digest) in pins.items():
            raw = (ROOT / (PREFIX + filename)).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
            approved[key] = record(filename, raw)
        raw_files = {}
        for kind, (filename, _mime, _fixture) in ARTIFACTS.items():
            raw = (ROOT / (PREFIX + filename)).read_bytes()
            self.assertEqual(record(filename, raw), approved[kind], 'approved input bytes changed')
            self.write(PREFIX + filename, raw)
            self.manifest['interfaceRelease']['artifacts'][kind] = deepcopy(approved[kind])
            raw_files[kind] = raw
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        return raw_files

    def consume_generated(self, portable=False, mutation=None, protocol='file:', hosted_html=None, only_kinds=None):
        generated = self.root / ('dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html' if portable else 'build-id.js')
        page_url = 'https://example.test/wealth/' + ('portable.html' if portable else 'index.html') if protocol == 'https:' else generated.as_uri()
        data = dict(generated=str(generated), portable=portable, pageURL=page_url,
                    consumer=str(ROOT / 'src/js/20-ui/31-tools-services.js'), loader=str(ROOT / 'src/js/00-core/10-download-assets.js'), mutation=mutation,
                    protocol=protocol, hostedHTML=hosted_html, onlyKinds=only_kinds)
        result = subprocess.run([NODE, '-e', PAGE_HARNESS], input=json.dumps(data), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def check_generated_downloads(self, portable):
        raw_files = self.pinned_artifact_build()
        result = self.consume_generated(portable=portable)
        self.assertEqual(result['enabled'], {'nativeKit': True, 'nativePin': True, 'preview': True})
        self.assertEqual(result['networkRequests'], 0)
        for kind, (filename, mime, _fixture) in ARTIFACTS.items():
            self.assertEqual(result['outcomes'][kind]['downloads'], [dict(filename=filename, mime=mime,
                base64=base64.b64encode(raw_files[kind]).decode())])
            self.assertEqual(result['outcomes'][kind]['state'], 'ok')

    def test_generated_file_payload_enables_real_page_and_downloads_approved_bytes(self):
        self.check_generated_downloads(portable=False)

    def test_generated_portable_enables_real_page_and_downloads_approved_bytes(self):
        self.check_generated_downloads(portable=True)

    def test_real_page_rejects_wrong_mime_in_generated_file_and_portable_payloads(self):
        self.pinned_artifact_build()
        for portable in (False, True):
            for kind, wrong_mime in (('nativeKit', 'text/html'), ('nativePin', 'application/json;charset=utf-8'),
                                      ('preview', 'text/html;charset=utf-8')):
                with self.subTest(portable=portable, kind=kind):
                    result = self.consume_generated(portable, dict(kind=kind, mime=wrong_mime))
                    self.assertFalse(result['enabled'][kind])
                    self.assertEqual(result['outcomes'][kind]['downloads'], [])
                    self.assertEqual(result['networkRequests'], 0)

    def test_real_page_rejects_same_size_corruption_of_generated_file_and_portable_bytes(self):
        self.pinned_artifact_build()
        for portable in (False, True):
            for kind in ARTIFACTS:
                with self.subTest(portable=portable, kind=kind):
                    result = self.consume_generated(portable, dict(kind=kind, corrupt=True))
                    self.assertTrue(result['enabled'][kind])
                    self.assertEqual(result['outcomes'][kind]['downloads'], [])
                    self.assertEqual(result['outcomes'][kind]['state'], 'error')
                    self.assertIn('Hash', result['outcomes'][kind]['notice'])
                    self.assertEqual(result['networkRequests'], 0)

    def test_derivative_build_rejects_unbounded_or_corrupt_artifacts_before_outputs(self):
        variants = []
        for value in ('../root-pin-R4.json', PREFIX + 'arbitrary.json', 'https://elsewhere.test/pin.json'):
            bad = deepcopy(self.manifest)
            bad['interfaceRelease']['artifacts']['nativePin']['path'] = value
            variants.append(bad)
        for key, value in (('bytes', 1), ('sha256', '0' * 64), ('available', False), ('filename', 'arbitrary.json')):
            bad = deepcopy(self.manifest)
            bad['interfaceRelease']['artifacts']['nativePin'][key] = value
            variants.append(bad)
        bad = deepcopy(self.manifest)
        bad['interfaceRelease']['artifacts']['extra'] = record('extra.zip', b'extra')
        variants.append(bad)
        for bad in variants:
            with self.subTest(bad=bad['interfaceRelease']['artifacts']):
                result = self.build(bad)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / 'build-id.js').exists())
                self.assertFalse((self.root / 'dist').exists())

    def sw(self, manifest=None, mutate=None, probes=True, hosted_html=None):
        manifest = manifest or self.manifest
        if not (self.root / 'build-id.js').exists():
            built = self.build()
            self.assertEqual(built.returncode, 0, built.stderr)
        files = {PREFIX + 'historical-source.zip': b'PK\x03\x04historical-source-fixture'}
        files.update({PREFIX + name: raw for name, _mime, raw in ARTIFACTS.values()})
        # Read fixture/approved bytes from the actual producer input files.
        files = {relative: (self.root / relative).read_bytes() for relative in files}
        input_data = dict(sw=str(ROOT / 'sw.js'), manifest=manifest, generated=str(self.root / 'build-id.js'),
            hostedHTML=hosted_html,
            files={'https://example.test/wealth/' + path: base64.b64encode(raw).decode() for path, raw in files.items()},
            probes=(['https://example.test/wealth/' + PREFIX + name for name, _mime, _raw in ARTIFACTS.values()] + ['https://example.test/wealth/src/vendor/downloads/leverage-preview-payload.js']) if probes else [])
        if mutate:
            mutate(input_data)
        result = subprocess.run([NODE, '-e', SW_HARNESS], input=json.dumps(input_data), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_old_sw_manifest_caches_only_historical_available_downloads(self):
        self.assertEqual(self.build(fixture_manifest(False)).returncode, 0)
        result = self.sw(fixture_manifest(False), probes=False)
        self.assertTrue(result['ok'], result)
        requested = {url for url in result['requested'] if '/downloads/jpw-alavancagem-atual/' in url}
        self.assertEqual(requested, {'https://example.test/wealth/' + PREFIX + 'manifest.json',
                                     'https://example.test/wealth/' + PREFIX + 'historical-source.zip'})
        self.assertNotIn('workerPayload', result)

    def test_interface_sw_serves_all_three_exact_bytes_during_offline_navigation(self):
        result = self.sw()
        self.assertTrue(result['ok'], result)
        for name, _mime, raw in ARTIFACTS.values():
            url = 'https://example.test/wealth/' + PREFIX + name
            if name.endswith('.html'):
                self.assertNotIn(url, result['requested'])
            else:
                self.assertIn(url, result['requested'])
            self.assertEqual(result['offlineFiles'][url], base64.b64encode(raw).decode())

        sidecar_url = 'https://example.test/wealth/src/vendor/downloads/leverage-preview-payload.js'
        self.assertEqual(base64.b64decode(result['offlineFiles'][sidecar_url]), (self.root/'src/vendor/downloads/leverage-preview-payload.js').read_bytes())
        self.assertEqual(result['offlineTypes'][sidecar_url], 'application/javascript')

    def test_interface_sw_rejects_corrupt_missing_or_unbounded_artifacts_with_cache_rollback(self):
        pin_url = 'https://example.test/wealth/' + PREFIX + ARTIFACTS['nativePin'][0]
        variants = []
        for key, value in (('path', PREFIX + 'unlisted.json'), ('path', 'https://example.test/wealth/' + PREFIX + ARTIFACTS['nativePin'][0]),
                           ('path', PREFIX + '../root-pin-R4.json'), ('bytes', 1), ('sha256', '0' * 64),
                           ('available', False), ('filename', 'unlisted.json')):
            bad = deepcopy(self.manifest)
            bad['interfaceRelease']['artifacts']['nativePin'][key] = value
            variants.append((bad, None))
        bad = deepcopy(self.manifest)
        bad['interfaceRelease']['artifacts']['extra'] = record('extra.zip', b'extra')
        variants.append((bad, None))
        variants.append((self.manifest, lambda data: data.update(missing=pin_url)))
        variants.append((self.manifest, lambda data: data['files'].update({pin_url: base64.b64encode(b'corrupt').decode()})))
        for manifest, mutate in variants:
            with self.subTest(manifest=manifest, mutation=bool(mutate)):
                result = self.sw(manifest, mutate, probes=False)
                self.assertFalse(result['ok'], result)
                build_id = (self.root / 'build-id.js').read_text().splitlines()[1].split("'")[1]
                self.assertEqual(result['deleted'], ['jp-wealth-' + build_id])
                self.assertTrue(result['priorPreserved'])

    def test_actual_generated_worker_payload_caches_approved_preview_despite_host_html_transformation(self):
        raw = self.pinned_artifact_build()['preview']
        preview_url = 'https://example.test/wealth/' + PREFIX + ARTIFACTS['preview'][0]
        for hosted_html in ('redirect', 'injection'):
            with self.subTest(hosted_html=hosted_html):
                result = self.sw(hosted_html=hosted_html)
                self.assertTrue(result['ok'], result.get('error'))
                self.assertNotIn(preview_url, result['requested'])
                self.assertEqual(result['offlineFiles'][preview_url], base64.b64encode(raw).decode())
                self.assertEqual(result['offlineTypes'][preview_url], 'text/html')
                self.assertEqual(result['workerPayload'], self.payload()['preview'])
                self.assertFalse(result['windowPresent'])

    def test_worker_rejects_bad_generated_preview_payload_without_network_fallback(self):
        self.pinned_artifact_build()
        preview_url = 'https://example.test/wealth/' + PREFIX + ARTIFACTS['preview'][0]
        variants = ({'missing': True}, {'mime': 'application/zip'}, {'mime': 'text/html;charset=utf-8'},
                    {'base64': ''}, {'base64': '!bad base64!'}, {'base64': None},
                    {'base64': 'YWJjZA='}, {'corrupt': True})
        for variant in variants:
            with self.subTest(variant=variant):
                result = self.sw(mutate=lambda data: data.update(workerMutation=variant), probes=False, hosted_html='injection')
                self.assertFalse(result['ok'])
                self.assertNotIn(preview_url, result['requested'])
                build_id = (self.root / 'build-id.js').read_text().splitlines()[1].split("'")[1]
                self.assertEqual(result['deleted'], ['jp-wealth-' + build_id])
                self.assertTrue(result['priorPreserved'])

    def test_worker_refuses_corrupt_outer_envelope_and_stale_inner_build_binding(self):
        self.pinned_artifact_build()
        preview_url = 'https://example.test/wealth/' + PREFIX + ARTIFACTS['preview'][0]
        for mutation in ({'outerCorrupt': True}, {'workerMutation': {'staleBuild': True}},
                         {'workerMutation': {'wrongGroup': True}}):
            with self.subTest(mutation=mutation):
                result = self.sw(mutate=lambda data: data.update(mutation), probes=False, hosted_html='injection')
                self.assertFalse(result['ok'])
                self.assertNotIn(preview_url, result['requested'])
                self.assertTrue(result['priorPreserved'])
                self.assertEqual(len(result['deleted']), 1)

    def test_worker_checks_embedded_preview_size_and_sha_against_declared_manifest(self):
        self.pinned_artifact_build()
        preview_url = 'https://example.test/wealth/' + PREFIX + ARTIFACTS['preview'][0]
        for key, value in (('bytes', 1), ('sha256', '0' * 64)):
            bad = deepcopy(self.manifest)
            bad['interfaceRelease']['artifacts']['preview'][key] = value
            with self.subTest(key=key):
                result = self.sw(bad, probes=False, hosted_html='injection')
                self.assertFalse(result['ok'])
                self.assertNotIn(preview_url, result['requested'])
                self.assertIn('diferente do manifesto', result['error'])
                self.assertTrue(result['priorPreserved'])
                self.assertEqual(len(result['deleted']), 1)

    def test_worker_keeps_sdk_daily_kit_and_pin_network_integrity_guards(self):
        self.pinned_artifact_build()
        base = 'https://example.test/wealth/'
        preview_url = base + PREFIX + ARTIFACTS['preview'][0]
        daily_raw = b'PK\x03\x04daily-network-guard-fixture'
        daily = record('daily-fixture.zip', daily_raw)
        guarded = (PREFIX + 'historical-source.zip', daily['path'],
                   PREFIX + ARTIFACTS['nativeKit'][0], PREFIX + ARTIFACTS['nativePin'][0])
        for relative in guarded:
            for broken in ('missing', 'corrupt'):
                with self.subTest(relative=relative, broken=broken):
                    def mutate(data):
                        data['manifest']['downloads']['dailySource'] = daily
                        data['files'][base + daily['path']] = base64.b64encode(daily_raw).decode()
                        if broken == 'missing':
                            data['missing'] = base + relative
                        else:
                            data['files'][base + relative] = base64.b64encode(b'corrupt').decode()
                    result = self.sw(deepcopy(self.manifest), mutate, probes=False, hosted_html='injection')
                    self.assertFalse(result['ok'])
                    self.assertIn(base + relative, result['requested'])
                    self.assertNotIn(preview_url, result['requested'])
                    self.assertTrue(result['priorPreserved'])
                    self.assertEqual(len(result['deleted']), 1)

    def test_worker_preview_cache_miss_refuses_network_fallback_after_install(self):
        self.pinned_artifact_build()
        preview_url = 'https://example.test/wealth/' + PREFIX + ARTIFACTS['preview'][0]
        result = self.sw(mutate=lambda data: data.update(removePreviewCache=True))
        self.assertTrue(result['ok'], result.get('error'))
        self.assertNotIn(preview_url, result['requested'])
        self.assertIsInstance(result['offlineFiles'][preview_url], dict)
        self.assertIn('error', result['offlineFiles'][preview_url])

    def test_markerized_upgrade_bootstrap_preserves_real_worker_payload(self):
        raw = self.pinned_artifact_build()['preview']
        source = ast.parse((ROOT / 'tools/service_worker_upgrade_test.py').read_text())
        markerize = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == 'markerize')
        namespace = {'Path': Path, 're': re}
        exec(compile(ast.Module(body=[markerize], type_ignores=[]), 'service_worker_upgrade_test.py', 'exec'), namespace)
        namespace['markerize'](self.root, 'old')
        result = self.sw(hosted_html='injection')
        self.assertTrue(result['ok'], result.get('error'))
        preview_url = 'https://example.test/wealth/' + PREFIX + ARTIFACTS['preview'][0]
        self.assertNotIn(preview_url, result['requested'])
        self.assertEqual(result['offlineFiles'][preview_url], base64.b64encode(raw).decode())
        self.assertIn("const JP_WEALTH_BUILD_ID = 'test-old';", (self.root / 'build-id.js').read_text())

    def test_generated_https_preview_download_ignores_host_redirect_and_injection(self):
        raw = self.pinned_artifact_build()['preview']
        for portable in (False, True):
            for hosted_html in ('redirect', 'injection'):
                with self.subTest(portable=portable, hosted_html=hosted_html):
                    result = self.consume_generated(portable, protocol='https:', hosted_html=hosted_html, only_kinds=['preview'])
                    self.assertTrue(result['enabled']['preview'])
                    self.assertEqual(result['networkRequests'], 0)
                    self.assertEqual(result['outcomes']['preview']['downloads'], [dict(
                        filename=ARTIFACTS['preview'][0], mime='text/html', base64=base64.b64encode(raw).decode())])

    def test_generated_https_preview_refuses_invalid_embedded_bytes_without_network_fallback(self):
        self.pinned_artifact_build()
        for portable in (False, True):
            for mutation in ({'missing': True}, {'mime': 'application/zip'}, {'base64': ''}, {'corrupt': True}):
                with self.subTest(portable=portable, mutation=mutation):
                    result = self.consume_generated(portable, dict(kind='preview', **mutation), protocol='https:',
                                                    hosted_html='injection', only_kinds=['preview'])
                    self.assertEqual(result['networkRequests'], 0)
                    self.assertEqual(result['outcomes']['preview']['downloads'], [])


if __name__ == '__main__':
    class R5DeliveryTest(DeliveryTest):
        revision = 'R5'
        def setUp(self):
            super().setUp()
            self.manifest['version'] = '1.23.0'
            self.manifest['interfaceRelease'].update(revision='R5', candidate='1.23.0-interface', archiveVariant='')
            for key, (name, _mime, raw) in ARTIFACTS.items():
                self.manifest['interfaceRelease']['artifacts'][key] = record(name, raw)
        @classmethod
        def setUpClass(cls):
            global ARTIFACTS
            ARTIFACTS = {
                'nativeKit': ('Kit_Windows_Stoikus_Janelas_R5.zip','application/zip',b'PK\x03\x04kit-fixture'),
                'nativePin': ('root-pin-R5.json','application/json',b'{"native":"NOT_RUN"}\n'),
                'preview': ('Previa_Stoikus_Janelas_R5.html','text/html',b'<!doctype html><p>Fictitious preview</p>')}
    unittest.main(verbosity=2)

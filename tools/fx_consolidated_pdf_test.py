#!/usr/bin/env python3
"""PDF text-only import: real module worker, cancellation, no external requests.

All reports here are generated synthetic fixtures. Builds run only in disposable
copies. The original owner report is neither read nor copied by this test.
"""
from __future__ import annotations
import argparse, ast, base64, hashlib, json, shutil, subprocess, sys, tempfile, threading
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = 'src/js/40-app/25-fx-consolidated-pdf.js'
ASSETS = ['src/vendor/pdfjs/pdf.mjs','src/vendor/pdfjs/pdf.worker.mjs','src/vendor/pdfjs/LICENSE.txt','src/vendor/pdfjs/PROVENANCE.json']


def synthetic_pdf(*, login='900001', currency='USD', hostile=False, no_text=False, language='en'):
    """Known Summary layout; independent values fixed before parsing code."""
    translated={'Currency':'Moeda','Gain':'Ganho','Trading Activity':'Atividade','Deposits':'Depositos','Withdrawals':'Retiradas','Summary':'Resumo','Gross Loss':'Perda Bruta','Gross Profit':'Lucro Bruto','Commissions':'Comissoes','Growth':'Crescimento','Drawdown':'Rebaixamento','Balance':'Saldo','Equity':'Capital Liquido'}
    rows=[(20,805,f'SYNTHETIC TRADER {login}'),(256,802,'REAL'),(20,785,'Synthetic Broker Ltd.'),
          (20,762,currency),(80,762,'8.00%'),(145,762,'35%'),(231,762,'1 000.00 (1)'),(322,762,'50.00 (1)'),
          (20,747,'Currency'),(80,747,'Gain'),(144,747,'Trading Activity'),(231,747,'Deposits'),(322,747,'Withdrawals'),
          (20,717,'Summary'),(29,695,'Gross Loss'),(195,695,'Gross Profit'),(259,695,'Sharp Ratio'),
          (20,680,'-100.00'),(201,680,'200.00'),(259,661,'0.40'),
          (90,635,'+'),(104,635,'80.00'),(120,615,'Total'),(216,615,'Swaps'),
          (20,575,'-'),(27,575,'15.00'),(20,559,'Commissions'),(259,561,'999.00'),(213,636.5,'-5.00'),
          (20,510,'8.00%'),(84,510,'12.00%'),(30,494,'Growth'),(94,494,'Drawdown'),
          (20,230,'1 030.00'),(97,230,'1 040.00'),(30,214,'Balance'),(97,214,'Equity')]
    if language=='pt': rows=[(x,y,translated.get(t,t)) for x,y,t in rows]
    def esc(s): return s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
    commands=[] if no_text else [f'BT /F1 9 Tf {x} {y} Td ({esc(t)}) Tj ET' for x,y,t in rows]
    stream='\n'.join(commands).encode('ascii')
    catalog=b'<< /Type /Catalog /Pages 2 0 R'+(b' /OpenAction 6 0 R' if hostile else b'')+b' >>'
    objects=[catalog,b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
       b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R'+(b' /Annots [7 0 R]' if hostile else b'')+b' >>',
       b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
       f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream']
    if hostile: objects += [br'<< /S /JavaScript /JS (app.launchURL\("https://pdf-must-not-fetch.invalid/script"\)) >>',b'<< /Type /Annot /Subtype /Link /Rect [0 0 10 10] /A << /S /URI /URI (https://pdf-must-not-fetch.invalid/link) >> >>']
    result=bytearray(b'%PDF-1.4\n'); offsets=[0]
    for n,obj in enumerate(objects,1): offsets.append(len(result));result.extend(f'{n} 0 obj\n'.encode()+obj+b'\nendobj\n')
    xref=len(result);result.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:result.extend(f'{offset:010d} 00000 n \n'.encode())
    result.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode());return bytes(result)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_): pass


def build_copy(target):
    manifest=json.loads((ROOT/'src/js/manifest.json').read_text())
    if not any(x['path']==ADAPTER for x in manifest['files']):manifest['files'].append({'path':ADAPTER})
    manifest['runtimeAssets']=[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),'type':'module' if p.endswith('/pdf.mjs') else 'worker' if p.endswith('/pdf.worker.mjs') else 'metadata'} for p in ASSETS]
    fixed=['index.html','src/styles/app.css','sw.js','tools/rebuild_monolith.py','docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf','docs/normative/ANEXO_PARAMETRICO_CANONICO.md','manifests/jp-wealth.webmanifest']
    for path in set(fixed+ASSETS+[x['path'] for x in manifest['files']]):
        dest=target/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/path,dest)
    for item in manifest['files']:item['sha256']=hashlib.sha256((target/item['path']).read_bytes()).hexdigest()
    dest=target/'src/js/manifest.json';dest.write_text(json.dumps(manifest,indent=2)+'\n')
    index=(target/'index.html').read_text()
    if f'<script src="{ADAPTER}"></script>' not in index:index=index.replace('</body>',f'<script src="{ADAPTER}"></script>\n</body>')
    (target/'index.html').write_text(index)
    result=subprocess.run([sys.executable,'tools/rebuild_monolith.py'],cwd=target,capture_output=True,text=True)
    assert result.returncode==0, result.stderr
    return manifest


def validator_checks(target,manifest):
    source=ast.parse((ROOT/'tools/agent_preflight.py').read_text())
    function=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='inspect_manifest')
    ns={'ROOT':target,'json':json,'hashlib':hashlib,'Path':Path}
    exec(compile(ast.Module(body=[function],type_ignores=[]),'<actual-preflight>','exec'),ns)
    path=target/'src/js/manifest.json';base=json.loads(json.dumps(manifest))
    def run(m):path.write_text(json.dumps(m));errors=[];ns['inspect_manifest'](errors,{});return errors
    assert run(base)==[],run(base)
    cases=[]
    m=json.loads(json.dumps(base));m['runtimeAssets'][0]['sha256']='0'*64;cases.append(('hash',m,'hash de recurso'))
    m=json.loads(json.dumps(base));m['runtimeAssets'].pop();cases.append(('missing',m,'incompletos'))
    m=json.loads(json.dumps(base));m['runtimeAssets'][0]['path']='../outside.mjs';cases.append(('escape',m,'nao permitido'))
    m=json.loads(json.dumps(base));m['runtimeAssets'].append(m['runtimeAssets'][0]);cases.append(('duplicate',m,'duplicados'))
    m=json.loads(json.dumps(base));m['runtimeAssets'][0]['type']='script';cases.append(('type',m,'invalido'))
    for name,m,expected in cases:
        assert any(expected in x for x in run(m)),name
        p=subprocess.run([sys.executable,'tools/rebuild_monolith.py'],cwd=target,capture_output=True,text=True)
        assert p.returncode!=0,name
    # A symlink to a byte-identical file is rejected, so path checks aren't hash-only.
    resource=target/ASSETS[0];original=resource.read_bytes();outside=target.parent/'escaped.mjs';outside.write_bytes(original);resource.unlink();resource.symlink_to(outside)
    assert any('fora da raiz' in x for x in run(base))
    p=subprocess.run([sys.executable,'tools/rebuild_monolith.py'],cwd=target,capture_output=True,text=True);assert p.returncode!=0
    resource.unlink();resource.write_bytes(original);path.write_text(json.dumps(base,indent=2)+'\n')
    # Old classic-script integrity checks remain effective alongside runtimeAssets.
    m=json.loads(json.dumps(base));m['files'][0]['sha256']='0'*64;assert any('hash divergente' in x for x in run(m));run(base)
    return 8


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out');args=parser.parse_args()
    results=[]
    with tempfile.TemporaryDirectory(prefix='jpw-fx-pdf-') as tmp:
        target=Path(tmp)/'product';target.mkdir();manifest=build_copy(target)
        results.append({'check':'actual_build_and_preflight_adversarial','assertedCases':validator_checks(target,manifest),'result':'PASS'})
        portable=(target/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').read_text()
        marker='window.JPW_RUNTIME_ASSETS = ';start=portable.index(marker)+len(marker);encoded=json.JSONDecoder().raw_decode(portable[start:])[0]
        for p in ASSETS:assert base64.b64decode(encoded[p])==(ROOT/p).read_bytes()
        assert '<script src="src/vendor/pdfjs/pdf.mjs">' not in portable
        # Probe consumes the exact generated bootstrap, with only the public adapter.
        tracking="""window.__workers=[];window.__urls=[];window.__revoked=[];
        const OriginalWorker=window.Worker;window.Worker=class extends OriginalWorker{constructor(...a){super(...a);this.__row={url:String(a[0]).startsWith('data:')?'data:text/javascript;base64,[embedded]':String(a[0]),terminated:false};window.__workers.push(this.__row);this.addEventListener('error',e=>this.__row.error={message:e.message,filename:e.filename,lineno:e.lineno})}terminate(){this.__row.terminated=true;super.terminate()}};
        const make=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL);URL.createObjectURL=b=>{const u=make(b);window.__urls.push(u);return u};URL.revokeObjectURL=u=>{window.__revoked.push(u);return revoke(u)};"""
        adapter=(ROOT/ADAPTER).read_text()
        web='<meta charset="utf-8"><script>'+tracking+'</script><script src="'+ADAPTER+'"></script>'
        inline='<meta charset="utf-8"><script>'+tracking+'window.JP_WEALTH_PORTABLE_BUILD=true;'+marker+json.dumps(encoded)+';</script><script>'+adapter+'</script>'
        (target/'probe.html').write_text(web);(target/'probe-portable.html').write_text(inline)
        # The same local asset cache contract is exercised without economic APIs.
        (target/'probe-sw.js').write_text("self.addEventListener('install',e=>e.waitUntil(caches.open('fx-pdf-test').then(c=>c.addAll("+json.dumps(['./probe.html','./'+ADAPTER]+['./'+p for p in ASSETS[:2]])+"))));self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));self.addEventListener('fetch',e=>e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))));")
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(target)));threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            for mode in ('web','portable-file','offline-cache'):
                print('PDF condition: '+mode,flush=True)
                ctx=browser.new_context();external=[]
                def route(req):
                    if urlsplit(req.request.url).hostname not in ('127.0.0.1',None):external.append(req.request.url);req.abort()
                    else:req.continue_()
                ctx.route('**/*',route);page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m: print('PDF console: '+m.type+' '+m.text,flush=True) if m.type=='error' else None)
                if mode=='portable-file':page.goto((target/'probe-portable.html').as_uri())
                else:
                    page.goto(origin+'/probe.html')
                    if mode=='offline-cache':
                        page.evaluate("async()=>{await navigator.serviceWorker.register('probe-sw.js');await navigator.serviceWorker.ready}")
                        page.reload();page.wait_for_function('navigator.serviceWorker.controller!==null');ctx.set_offline(True)
                def parse(data,extra=None):return page.evaluate("async a=>{try{return {ok:true,report:await JPWFXConsolidated.parsePDF(Uint8Array.from(atob(a.data),c=>c.charCodeAt(0)),a.options||{})}}catch(e){return {ok:false,code:e.code,message:e.message}}}",{'data':base64.b64encode(data).decode(),'options':extra or {}})
                for language in ('en','pt'):
                    result=parse(synthetic_pdf(hostile=True,language=language));assert result['ok'],(mode,result,page.evaluate('__workers'))
                    report=result['report'];assert report['identity']=={'login':'900001','broker':'Synthetic Broker Ltd.','currency':'USD','server':None},report
                    assert report['orders']==report['deals']==report['positions']==[]
                    expected={'netProfit':80,'grossProfit':200,'grossLoss':-100,'commission':-15,'swap':-5,'balance':1030,'equity':1040,'deposits':1000,'withdrawals':50,'growthPct':8,'drawdownPct':12}
                    for key,value in expected.items():assert report['summary'][key]==value,(mode,key,report['summary'])
                    assert report['period']['from'] is None and report['period']['declared'] is False
                    assert any(x['code']=='PERIOD_NOT_REPORTED' for x in report['issues'])
                    assert report['summary']['profitFactor'] is None
                assert parse(synthetic_pdf(no_text=True))['code']=='PDF_NO_TEXT'
                assert parse(synthetic_pdf(login='unknown'))['code']=='PDF_ACCOUNT_MISSING'
                assert parse(b'not a PDF')['code']=='PDF_INPUT'
                cancelled=page.evaluate("async data=>{const pending=JPWFXConsolidated.parsePDF(Uint8Array.from(atob(data),c=>c.charCodeAt(0)));await JPWFXConsolidated.disposePDF();try{await pending;return false}catch(e){return e.code==='PDF_CANCELLED'}}",base64.b64encode(synthetic_pdf()).decode())
                assert cancelled,mode
                assert parse(synthetic_pdf())['ok'],mode
                resourceState=page.evaluate('({workers:__workers,urls:__urls,revoked:__revoked})')
                assert resourceState['workers'] and all(x['terminated'] for x in resourceState['workers']),resourceState
                assert sorted(resourceState['urls'])==sorted(resourceState['revoked']),resourceState
                if mode=='portable-file':assert all(x['url'].startswith('data:text/javascript;base64,') for x in resourceState['workers'])
                else:assert all(x['url'].startswith(origin+'/src/vendor/pdfjs/') for x in resourceState['workers'])
                assert external==[],external
                assert errors==[],errors
                results.append({'check':mode,'result':'PASS','workerInstances':len(resourceState['workers']),'terminated':True,'externalRequests':0,'parsedLanguages':['en','pt'],'syntheticOnly':True})
                ctx.close()
            browser.close()
        server.shutdown()
    report={'result':'PASS','root':str(ROOT),'adapterSha256':hashlib.sha256((ROOT/ADAPTER).read_bytes()).hexdigest(),'checks':results,'limitation':'Offline asset cache fixture is not the product SW upgrade lifecycle; run the existing PWA gate on the final candidate.'}
    if args.out:Path(args.out).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Synthetic PDF regression: lazy local runtime, recognized tables and bounded failure.

All builds and browser state are disposable; this test never reads owner reports.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, shutil, subprocess, sys, tempfile, threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from fx_consolidated_pdf_test import Quiet, synthetic_pdf

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'src/js/10-domain/17-fx-consolidated-model.js'
ADAPTER = 'src/js/40-app/25-fx-consolidated-pdf.js'
PAYLOAD = 'src/vendor/pdfjs/runtime-assets.js'


class PDFQuiet(Quiet):
    def copyfile(self, source, outputfile):
        try: super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError): pass  # Intentional worker cancellation.


def pages_pdf(pages):
    def esc(s): return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>', b'', b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids=[]
    for rows in pages:
        page_id=len(objects)+1;kids.append(f'{page_id} 0 R')
        stream='\n'.join(f'BT /F1 8 Tf {x} {y} Td ({esc(t)}) Tj ET' for x,y,t in rows).encode('ascii')
        objects.extend([f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 1300 842] /Resources << /Font << /F1 3 0 R >> >> /Contents {page_id+1} 0 R >>'.encode(), f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'\nendstream'])
    objects[1]=f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(kids)} >>'.encode()
    result=bytearray(b'%PDF-1.4\n');offsets=[0]
    for index,obj in enumerate(objects,1):offsets.append(len(result));result.extend(f'{index} 0 obj\n'.encode()+obj+b'\nendobj\n')
    xref=len(result);result.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:result.extend(f'{offset:010d} 00000 n \n'.encode())
    result.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode());return bytes(result)


def detailed_pdf(*, conflict=False, missing_header=False, decimal_comma=False, bad_ticket=False):
    xs=[20,160,225,305,375,450,525,600,670,770,830,900,990,1080]
    labels=['Time','Deal','Symbol','Type','Direction','Volume','Price','Order','Commission','Fee','Swap','Profit','Balance','Comment']
    rows=[]
    for index in range(2):
        page=[(20,810,'Trade History Report'),(20,790,'Account: '+('900002' if conflict and index else '900001')),(20,775,'Currency: USD'),(20,760,'Company: Synthetic Broker Ltd.'),(20,745,'Server: Synthetic-Demo'),(20,730,'Period: 2026.09.01 - 2026.09.15'),(20,700,'Deals')]
        if not(index and missing_header):page.extend((x,680,label) for x,label in zip(xs,labels))
        values=['2026.09.15 10:00:00',str(800+index),'EURUSD','buy' if index==0 else 'sell','in' if index==0 else 'out','0.40','1.10300',str(700+index),'-1.00','-0.50','0.00',str(index*100)+'.00',str(1000+index*100)+'.00','synthetic']
        if bad_ticket and index:values[1]='unreadable'
        if decimal_comma:values=[v.replace('.',',') if n in range(5,13) and n!=7 else v for n,v in enumerate(values)]
        page.extend((x,655,value) for x,value in zip(xs,values))
        if index:page.extend([(20,600,'Summary'),(20,580,'Balance: '+('1.100,00' if decimal_comma else '1,100.00')),(20,560,'Equity: '+('1.100,00' if decimal_comma else '1,100.00'))])
        rows.append(page)
    return pages_pdf(rows)


def summary_two_page_pdf():
    rows=[(20,805,'SYNTHETIC TRADER 900001'),(256,802,'REAL'),(20,785,'Synthetic Broker Ltd.'),
          (20,762,'USD'),(20,747,'Currency'),(20,717,'Summary'),(29,695,'Gross Loss'),(195,695,'Gross Profit'),
          (20,680,'-100.00'),(201,680,'200.00'),(20,230,'1 030.00'),(97,230,'1 040.00'),(30,214,'Balance'),(97,214,'Equity')]
    # Same coordinates on another page cannot replace first-page summary values.
    return pages_pdf([rows,[(20,230,'999999.00'),(97,230,'888888.00')]])


def build(target):
    for folder in ['src','assets','manifests','docs/normative']:
        shutil.copytree(ROOT/folder,target/folder)
    for name in ['index.html','sw.js','tools/rebuild_monolith.py']:
        dst=target/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dst)
    def run():
        proc=subprocess.run([sys.executable,'tools/rebuild_monolith.py'],cwd=target,capture_output=True,text=True)
        assert proc.returncode==0,proc.stderr
    run()
    payload=(target/PAYLOAD).read_bytes();build_id=(target/'build-id.js').read_bytes()
    encoded=json.loads(payload.decode().split('window.JPW_RUNTIME_ASSETS = ',1)[1].rstrip(';\n'))
    for path,content in encoded.items():assert base64.b64decode(content)==(target/path).read_bytes()
    (target/PAYLOAD).write_text('// changed generated output\n');run()
    assert (target/PAYLOAD).read_bytes()==payload and (target/'build-id.js').read_bytes()==build_id
    asset=target/'src/vendor/pdfjs/pdf.mjs';original=asset.read_bytes();asset.write_bytes(original+b'\n// mutation\n')
    proc=subprocess.run([sys.executable,'tools/rebuild_monolith.py'],cwd=target,capture_output=True,text=True)
    assert proc.returncode!=0 and 'hash' in proc.stderr
    asset.write_bytes(original);run();return encoded


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out');args=parser.parse_args();checks=[]
    original={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [MODEL,ADAPTER,'tools/rebuild_monolith.py']}
    with tempfile.TemporaryDirectory(prefix='jpw-pdf-local-') as tmp:
        target=Path(tmp)/'product';target.mkdir();encoded=build(target)
        checks.append({'scenario':'generated_payload_reproducible_pinned_inputs','result':'PASS'})
        tracking="""window.__workers=[];window.__urls=[];window.__revoked=[];const W=Worker;window.Worker=class extends W{constructor(...a){super(...a);this.row={terminated:false};__workers.push(this.row)}terminate(){this.row.terminated=true;super.terminate()}};const make=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL);URL.createObjectURL=b=>{const u=make(b);__urls.push(u);return u};URL.revokeObjectURL=u=>{__revoked.push(u);return revoke(u)};"""
        web='<meta charset="utf-8"><script>'+tracking+'</script><script src="'+MODEL+'"></script><script src="'+ADAPTER+'"></script>'
        portable='<meta charset="utf-8"><script>'+tracking+'window.JP_WEALTH_PORTABLE_BUILD=true;window.JPW_RUNTIME_ASSETS='+json.dumps(encoded)+';</script><script>'+(target/MODEL).read_text()+'</script><script>'+(target/ADAPTER).read_text()+'</script>'
        (target/'probe.html').write_text(web);(target/'portable.html').write_text(portable)
        paths=['./probe.html','./'+MODEL,'./'+ADAPTER,'./src/vendor/pdfjs/pdf.mjs','./src/vendor/pdfjs/pdf.worker.mjs']
        (target/'probe-sw.js').write_text("self.addEventListener('install',e=>e.waitUntil(caches.open('pdf-local-test').then(c=>c.addAll("+json.dumps(paths)+"))));self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));self.addEventListener('fetch',e=>e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))));")
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(PDFQuiet,directory=str(target)));threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            for mode in ['modular-file','http','portable-file','offline']:
                ctx=browser.new_context();external=[];page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                def route(req):
                    if urlsplit(req.request.url).hostname not in ('127.0.0.1',None):external.append(req.request.url);req.abort()
                    else:req.continue_()
                ctx.route('**/*',route)
                page.goto((target/('portable.html' if mode=='portable-file' else 'probe.html')).as_uri() if 'file' in mode else origin+'/probe.html')
                if mode=='offline':
                    page.evaluate("async()=>{await navigator.serviceWorker.register('probe-sw.js');await navigator.serviceWorker.ready}");page.reload();page.wait_for_function('navigator.serviceWorker.controller!==null');ctx.set_offline(True)
                assert page.evaluate('Boolean(window.JPW_RUNTIME_ASSETS)')==(mode=='portable-file')
                def parse(data,options=None):return page.evaluate("async a=>{try{const report=await JPWFXConsolidated.parsePDF(Uint8Array.from(atob(a.data),c=>c.charCodeAt(0)),a.options);return {ok:true,report,validation:JPWFXConsolidated.validateReport(report)}}catch(e){return {ok:false,code:e.code,message:e.message}}}",{'data':base64.b64encode(data).decode(),'options':options or {}})
                for language in ['en','pt']:
                    value=parse(synthetic_pdf(language=language,hostile=True));assert value['ok'],(mode,value)
                    report=value['report'];assert report['summary']['balance']==1030 and report['summary']['equity']==1040,(mode,value)
                    assert report['summary']['netProfit']==80 and report['summary']['swap']==-5
                    assert report['deals']==[] and not value['validation'],value
                value=parse(summary_two_page_pdf());assert value['ok'] and value['report']['summary']['balance']==1030 and value['report']['summary']['equity']==1040,value
                for comma in [False,True]:
                    value=parse(detailed_pdf(decimal_comma=comma));assert value['ok'],(mode,value)
                    report=value['report'];assert not value['validation'],value
                    assert report['identity']['login']=='900001' and len(report['deals'])==2,value
                    assert report['deals'][0]['volume']==.4 and report['deals'][0]['price']==1.103,value
                    assert report['deals'][1]['profit']==100 and report['deals'][1]['netResult']==98.5,value
                    assert report['summary']['balance']==1100 and report['coverage']['completeHistory'] is False,value
                    assert any(x['code']=='PDF_TEXT_TABLES' for x in report['issues'])
                for data,expected in [(detailed_pdf(conflict=True),'PDF_IDENTITY_CONFLICT'),(detailed_pdf(missing_header=True),'PDF_TABLE_HEADER_MISSING'),(detailed_pdf(bad_ticket=True),'PDF_TABLE_ROW'),(synthetic_pdf(no_text=True),'PDF_NO_TEXT'),(b'not-pdf','PDF_INPUT'),(pages_pdf([[(20,800,'empty')]]*201),'PDF_PAGE_LIMIT')]:
                    value=parse(data);assert value.get('code')==expected,(mode,expected,value)
                cancelled=page.evaluate("async encoded=>{const pending=JPWFXConsolidated.parsePDF(Uint8Array.from(atob(encoded),c=>c.charCodeAt(0)));await JPWFXConsolidated.disposePDF();try{await pending;return false}catch(e){return e.code==='PDF_CANCELLED'}}",base64.b64encode(detailed_pdf()).decode());assert cancelled
                cancelled_worker=page.evaluate("async encoded=>{const Base=Worker;window.Worker=class extends Base{constructor(...a){super(...a);queueMicrotask(()=>JPWFXConsolidated.disposePDF())}};try{await JPWFXConsolidated.parsePDF(Uint8Array.from(atob(encoded),c=>c.charCodeAt(0)));return false}catch(e){return e.code==='PDF_CANCELLED'}finally{window.Worker=Base}}",base64.b64encode(detailed_pdf()).decode());assert cancelled_worker
                assert parse(detailed_pdf())['ok']
                resources=page.evaluate('({workers:__workers,urls:__urls,revoked:__revoked})');assert all(w['terminated'] for w in resources['workers']) and sorted(resources['urls'])==sorted(resources['revoked']),resources
                assert not external and not errors,(external,errors)
                checks.append({'scenario':mode,'result':'PASS','summaryLanguages':['en','pt'],'crossPageSummaryIsolation':True,'detailPages':2,'decimalFormats':['dot','comma'],'failuresChecked':6,'cancelThenRetry':True,'externalRequests':0,'resourcesReleased':True})
                ctx.close()
            saved_payload=(target/PAYLOAD).read_bytes();(target/PAYLOAD).unlink()
            ctx=browser.new_context();page=ctx.new_page();page.goto((target/'probe.html').as_uri())
            missing=page.evaluate("async data=>{try{await JPWFXConsolidated.parsePDF(Uint8Array.from(atob(data),c=>c.charCodeAt(0)));return 'unexpected_success'}catch(e){return e.code}}",base64.b64encode(synthetic_pdf()).decode())
            assert missing=='PDF_ASSET_MISSING',missing
            (target/PAYLOAD).write_bytes(saved_payload)
            retry=page.evaluate("async data=>{const report=await JPWFXConsolidated.parsePDF(Uint8Array.from(atob(data),c=>c.charCodeAt(0)));return report.summary.balance}",base64.b64encode(synthetic_pdf()).decode());assert retry==1030
            checks.append({'scenario':'missing_local_payload_then_recovery','result':'PASS','failureCode':missing})
            ctx.close();browser.close()
        server.shutdown()
    assert original=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in original},'Source changed during test; rerun on frozen candidate.'
    report={'result':'PASS','syntheticOnly':True,'sourceHashes':original,'checks':checks,'limits':'Recognized separate text columns only. No OCR, completeness inference or arbitrary PDF layout guarantee. Offline fixture tests local PDF cache, not product SW updates.'}
    if args.out:Path(args.out).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()

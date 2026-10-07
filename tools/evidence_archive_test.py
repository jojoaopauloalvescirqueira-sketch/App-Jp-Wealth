#!/usr/bin/env python3
"""Synthetic exact-source browser probe for the independent evidence archive."""
import argparse, functools, hashlib, http.server, json, pathlib, tempfile, threading, traceback
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
JS=ROOT/'src/js/00-core/09-evidence-archive.js'
VENDOR=ROOT/'src/vendor/fflate/fflate-0.8.2.min.js'
def run(out):
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url='http://127.0.0.1:%s/'%server.server_port
    def record(name,fn):
        try:
            data=fn();assert data is True or (isinstance(data,dict) and data.get('pass')),data
            rows.append({'case':name,'status':'PASS','evidence':data})
        except Exception as error:
            rows.append({'case':name,'status':'PRODUCT_FAIL','error':str(error)});raise
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True,args=['--no-sandbox'])
            context=browser.new_context(accept_downloads=True);page=context.new_page()
            def setup(p):
                p.goto(url+'src/vendor/fflate/')
                p.add_script_tag(url=url+'src/vendor/fflate/fflate-0.8.2.min.js')
                p.add_script_tag(url=url+'src/js/00-core/09-evidence-archive.js')
            setup(page)
            page.evaluate("""async()=>{window.syntheticFile=new File(['<!doctype html><html><body>Relatório sintético: 123.45<script>window.evidenceExecuted=true</script></body></html>'],'Relatório mês.html',{type:'text/html'});window.syntheticHash=await JPWEvidence.digest(await syntheticFile.arrayBuffer());localStorage.setItem('synthetic-financial','KEEP');}""")
            record('absent receipt and exact mismatch',lambda:page.evaluate("""async()=>{const missing=await JPWEvidence.status(syntheticHash),r=await JPWEvidence.putOriginal(syntheticFile,{fileHash:'0'.repeat(64),receiptId:'r1'});const s=await JPWEvidence.summary();return {pass:missing.status==='ABSENT'&&r.status==='REFUSED'&&s.count===0,result:r.status};}"""))
            record('transaction confirmed original and no execution',lambda:page.evaluate("""async()=>{const r=await JPWEvidence.putOriginal(syntheticFile,{fileHash:syntheticHash,receiptId:'r1'}),s=await JPWEvidence.summary();return {pass:r.status==='CONFIRMED'&&s.count===1&&s.items[0].fileName==='Relatório mês.html'&&!window.evidenceExecuted,count:s.count};}"""))
            second=context.new_page();setup(second)
            second.evaluate("""async()=>{window.syntheticFile=new File(['<!doctype html><html><body>Relatório sintético: 123.45<script>window.evidenceExecuted=true</script></body></html>'],'Relatório mês.html');window.syntheticHash=await JPWEvidence.digest(await syntheticFile.arrayBuffer());}""")
            # Simultaneous tabs exercise the real shared IDB readwrite transaction.
            page.evaluate("""async()=>{window.parallel=JPWEvidence.putOriginal(syntheticFile,{fileHash:syntheticHash,receiptId:'r2'});}""")
            second.evaluate("""async()=>{window.parallel=JPWEvidence.putOriginal(syntheticFile,{fileHash:syntheticHash,receiptId:'r3'});}""")
            page.evaluate("async()=>await parallel");second.evaluate("async()=>await parallel")
            record('two tabs merge receipt links',lambda:page.evaluate("""async()=>{const s=await JPWEvidence.summary();return {pass:s.count===1&&['r1','r2','r3'].every(x=>s.items[0].receiptIds.includes(x)),links:s.items[0].receiptIds.length};}"""))
            record('write exception aborts real transaction',lambda:page.evaluate("""async()=>{const old=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){throw Error('synthetic write denied')};let r;try{r=await JPWEvidence.putOriginal(syntheticFile,{fileHash:syntheticHash,receiptId:'REFUSED_LINK'});}finally{IDBObjectStore.prototype.put=old;}const s=await JPWEvidence.summary();return {pass:r.status==='REFUSED'&&!s.items[0].receiptIds.includes('REFUSED_LINK'),status:r.status};}"""))
            record('format and size are bounded before writes',lambda:page.evaluate("""async()=>{const png=new File(['PNG'],'bad.png'),big=new File([new Uint8Array(32*1024*1024+1)],'big.html');const a=await JPWEvidence.putOriginal(png,{fileHash:await JPWEvidence.digest(await png.arrayBuffer()),receiptId:'x'}),b=await JPWEvidence.putOriginal(big,{fileHash:syntheticHash,receiptId:'x'});return {pass:a.status==='REFUSED'&&b.status==='REFUSED'&&(await JPWEvidence.summary()).count===1};}"""))
            with page.expect_download() as event:
                export=page.evaluate("async()=>await JPWEvidence.exportArchive()")
            archive=out/'synthetic-evidence.zip';event.value.save_as(archive)
            assert export['status']=='DOWNLOAD_REQUESTED'
            payload=list(archive.read_bytes())
            clean=browser.new_context();restore=clean.new_page();setup(restore)
            restore.evaluate("localStorage.setItem('synthetic-financial','KEEP')")
            record('zip roundtrip and financial separation',lambda:restore.evaluate("""async bytes=>{const r=await JPWEvidence.restoreArchive(new File([new Uint8Array(bytes)],'archive.zip'));const s=await JPWEvidence.summary();return {pass:r.status==='CONFIRMED'&&s.count===1&&s.items[0].receiptIds.length===3&&localStorage.getItem('synthetic-financial')==='KEEP',status:r.status,count:s.count};}""",payload))
            record('zip path traversal refused',lambda:restore.evaluate("""async()=>{const zip=fflate.zipSync({'../bad.html':new TextEncoder().encode('<html>bad</html>'),'manifest.json':new TextEncoder().encode('{}')});const r=await JPWEvidence.restoreArchive(new File([zip],'bad.zip'));return {pass:r.status==='REFUSED'&&(await JPWEvidence.summary()).count===1,reason:r.reason};}"""))
            record('manifest checksum and original tampering refused',lambda:restore.evaluate("""async bytes=>{const entries=fflate.unzipSync(new Uint8Array(bytes));let m=JSON.parse(new TextDecoder().decode(entries['manifest.json']));m.entries[0].fileName='renamed.html';entries['manifest.json']=new TextEncoder().encode(JSON.stringify(m));const r=await JPWEvidence.restoreArchive(new File([fflate.zipSync(entries,{level:0})],'changed.zip'));return {pass:r.status==='REFUSED'&&/Checksum/.test(r.reason)&&(await JPWEvidence.summary()).count===1,reason:r.reason};}""",payload))
            record('compressed archive refused before inflation',lambda:restore.evaluate("""async bytes=>{const entries=fflate.unzipSync(new Uint8Array(bytes)),zip=fflate.zipSync(entries,{level:9});const r=await JPWEvidence.restoreArchive(new File([zip],'compressed.zip'));return {pass:r.status==='REFUSED'&&(await JPWEvidence.summary()).count===1,reason:r.reason};}""",payload))
            record('declared expansion bound before decompression',lambda:restore.evaluate("""async bytes=>{const zip=new Uint8Array(bytes),v=new DataView(zip.buffer);let start=-1;for(let i=0;i<zip.length-4;i++)if(v.getUint32(i,true)===0x02014b50){start=i;break;}v.setUint32(start+24,0xffffffff,true);const r=await JPWEvidence.restoreArchive(new File([zip],'bomb.zip'));return {pass:r.status==='REFUSED'&&(await JPWEvidence.summary()).count===1,reason:r.reason};}""",payload))
            restore.reload();restore.add_script_tag(url=url+'src/vendor/fflate/fflate-0.8.2.min.js');restore.add_script_tag(url=url+'src/js/00-core/09-evidence-archive.js')
            record('reload preserves archive',lambda:restore.evaluate("async()=>({pass:(await JPWEvidence.summary()).count===1})"))
            record('corrupt stored bytes block export',lambda:restore.evaluate("""async()=>{const s=await JPWEvidence.summary();await new Promise((resolve,reject)=>{const r=indexedDB.open('jpwealth_evidence_v1',1);r.onsuccess=()=>{const db=r.result,tx=db.transaction('originals','readwrite'),store=tx.objectStore('originals'),q=store.get(s.items[0].fileHash);q.onsuccess=()=>{const row=q.result;row.blob=new Blob([new Uint8Array(row.size)]);store.put(row);};tx.oncomplete=()=>{db.close();resolve()};tx.onabort=()=>reject(tx.error);};});const status=await JPWEvidence.status(s.items[0].fileHash),r=await JPWEvidence.exportArchive();return {pass:r.status==='REFUSED'&&/corrompido/.test(r.reason)&&status.status==='REFUSED'&&/corrompido/.test(status.reason),reason:r.reason,status:status.status};}"""))
            context.close();clean.close();browser.close()
    finally:
        server.shutdown()
        receipt={'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [JS,VENDOR]},'tests':rows,'summary':{'PASS':sum(r['status']=='PASS' for r in rows),'PRODUCT_FAIL':sum(r['status']=='PRODUCT_FAIL' for r in rows)},'limits':'Synthetic Chromium / real IndexedDB. Physical folder, Safari/Firefox and user-origin transfer NOT_RUN.'}
        (out/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
    assert len(rows)==12 and all(r['status']=='PASS' for r in rows)
    print(json.dumps(receipt['summary']))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=pathlib.Path,required=True);args=parser.parse_args()
    run(args.out)

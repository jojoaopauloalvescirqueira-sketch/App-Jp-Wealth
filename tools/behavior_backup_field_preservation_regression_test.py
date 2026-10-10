#!/usr/bin/env python3
"""Synthetic real v2 backup: field extensions cannot cross anonymous array rows."""
import argparse
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
from http.server import SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from dashboard_macro_test import launch_browser

ROOT = Path(__file__).resolve().parents[1]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--artifact', type=Path, required=True)
    args = parser.parse_args()
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(Quiet, directory=str(args.root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    rows = []
    def check(name, passed, facts):
        rows.append({'name': name, 'status': 'PASS' if passed else 'PRODUCT_FAIL', 'observations': facts})
    with sync_playwright() as pw:
        browser = launch_browser(pw)
        context = browser.new_context(service_workers='block')
        install_bootstrap(context)
        context.add_init_script('window.__onbShown=true;')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('dialog', lambda dialog: dialog.accept())
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
        wait_bootstrap(page)
        prepared = page.evaluate("""async()=>{
            closeModal();S.onboarding.done=true;
            S.accounts=[{forexAccountId:'BACKUP-SYNTHETIC',nome:'Synthetic backup account',tipo:'MESTRE',platformCurrency:'USD'}];
            const period=JPWForex.state.recordAccountPeriod({accountId:'BACKUP-SYNTHETIC',startedAt:'2026-01-01',currency:'USD',si:10000,openingBook:10000,source:'Synthetic backup fixture',activateCurrentPeriod:true},{reason:'Synthetic explicit period'});
            if(!period.ok)throw Error(JSON.stringify(period));
            const selected=JPWForex.state.selectOperationalAccount('BACKUP-SYNTHETIC');if(!selected.ok)throw Error(JSON.stringify(selected));
            const scope=JPWForex.state.operationalSelection();
            const current=()=>S.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId];
            while(current().phases[1].orders.length<2){const r=JPWForex.state.addAccountOrderDraft({...scope,pi:1},{});if(!r.ok)throw Error(JSON.stringify(r));}
            const recorded=JPWForex.state.recordAccountOrders([{pi:1,oi:1,changes:{id:'BACKUP-FACT',brokerHash:'SYNTHETIC-HASH',par:'EURUSD',tipo:'BUY',lote:0.01,entry:1.1,sl:1.09,tp:1.2,result:null,status:'Aberta'}}],{...scope,reason:'Synthetic recorded fact'});
            if(!recorded.ok)throw Error(JSON.stringify(recorded));
            for(let i=0;i<2;i++){const r=JPWForex.state.addAccountOrderDraft({...scope,pi:1},{});if(!r.ok)throw Error(JSON.stringify(r));}
            current().phases[1].orders.forEach((order,index)=>order.syntheticExtension={slot:index,opaque:[index,null,'keep']});
            if(save()!==true)throw Error('Synthetic extension fixture not saved');
            window.__expectedContexts=structuredClone(S.forex.accountContexts);
            window.__backup=JSON.parse(await dgBuildBackupBlob(1,'synthetic-field-preservation.json','2026-01-31T12:00:00Z').text());
            window.__fieldWrites=0;const put=Storage.prototype.setItem;
            Storage.prototype.setItem=function(k,v){if(this===localStorage&&k===LSKEY)__fieldWrites++;return put.call(this,k,v);};
            const before=JSON.stringify(S),raw=localStorage.getItem(LSKEY),normalized=normalizeImportedState(__backup);
            const original=current().phases[1].orders;
            const restored=normalized.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId].phases[1].orders;
            return {scope,exportExact:JSON.stringify(__backup.state.forex.accountContexts)===JSON.stringify(__expectedContexts),normalizeExact:JSON.stringify(normalized.forex.accountContexts)===JSON.stringify(__expectedContexts),pure:before===JSON.stringify(S)&&raw===localStorage.getItem(LSKEY)&&__fieldWrites===0,rows:original.map((row,i)=>({slot:i,id:row.id,originalOrderId:row.orderId||null,restoredOrderId:restored[i].orderId||null,originalExtension:row.syntheticExtension,restoredExtension:restored[i].syntheticExtension,originalVersion:row.recordVersion??null,restoredVersion:restored[i].recordVersion??null,originalRevisions:row.revisions?.length??null,restoredRevisions:restored[i].revisions?.length??null}))};
        }""")
        check('confirmed v2 export is exact', prepared['exportExact'], prepared['rows'])
        check('normalization preserves every order/draft field in its own slot', prepared['normalizeExact'], prepared['rows'])
        check('normalization is read-only', prepared['pure'], {'pure': prepared['pure']})
        helper = page.evaluate("""()=>{
            const test=(original,target,expected)=>{const before=JSON.stringify(original);dgBackupPreserveCompatibleFields(original,target);return {passed:JSON.stringify(target)===JSON.stringify(expected)&&JSON.stringify(original)===before,target};};
            return {
                uniqueReorder:test([{id:'a',name:'A',extra:{owner:'a'}},{id:'b',name:'B',extra:{owner:'b'}}],[{id:'b',name:'B'},{id:'a',name:'A'}],[{id:'b',name:'B',extra:{owner:'b'}},{id:'a',name:'A',extra:{owner:'a'}}]),
                duplicateId:test([{id:'dup',name:'A',extra:1},{id:'dup',name:'B',extra:2}],[{id:'dup',name:'A'},{id:'dup',name:'B'}],[{id:'dup',name:'A',extra:1},{id:'dup',name:'B',extra:2}]),
                emptyId:test([{id:'',name:'A',extra:1},{id:'',name:'B',extra:2}],[{id:'',name:'A'},{id:'',name:'B'}],[{id:'',name:'A',extra:1},{id:'',name:'B',extra:2}]),
                anonymousReorderRefused:test([{id:'',name:'A',extra:1},{id:'',name:'B',extra:2}],[{id:'',name:'B'},{id:'',name:'A'}],[{id:'',name:'B'},{id:'',name:'A'}]),
                changedLengthRefused:test([{id:'',name:'A',extra:1}],[{id:'',name:'A'},{id:'',name:'B'}],[{id:'',name:'A'},{id:'',name:'B'}]),
                schemaBoundary:test({schemaVersion:1,retired:'old'},{schemaVersion:2},{schemaVersion:2})
            };
        }""")
        for name, facts in helper.items():
            check('compatible-field matching: ' + name, facts['passed'], facts)
        page.evaluate("()=>{window.__importAlerts=[];window.alert=message=>__importAlerts.push(String(message));window.confirm=()=>true;importFullBackupFile(new File([JSON.stringify(__backup)],'synthetic-field-preservation.json',{type:'application/json'}));}")
        page.wait_for_function("__importAlerts.some(message=>message.startsWith('Backup importado com sucesso.'))")
        imported = page.evaluate("()=>({exact:JSON.stringify(S.forex.accountContexts)===JSON.stringify(__expectedContexts),diskExact:JSON.stringify(JSON.parse(localStorage.getItem(LSKEY)).forex.accountContexts)===JSON.stringify(__expectedContexts),writes:__fieldWrites,alerts:__importAlerts})")
        check('actual FileReader import and confirmed disk preserve exact context', imported['exact'] and imported['diskExact'], imported)
        expected = page.evaluate('structuredClone(__expectedContexts)')
        page.reload()
        wait_bootstrap(page)
        reloaded = page.evaluate('structuredClone(S.forex.accountContexts)')
        check('reload retains exact order identities and revisions', reloaded == expected, {'expectedHash': hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest(), 'observedHash': hashlib.sha256(json.dumps(reloaded, sort_keys=True).encode()).hexdigest()})
        assert_fixture_requests(context)
        check('no script errors', not errors, errors)
        context.close()
        browser.close()
    server.shutdown()
    server.server_close()
    counts = {status: sum(row['status'] == status for row in rows) for status in ('PASS', 'PRODUCT_FAIL')}
    receipt = {'root': str(args.root.resolve()), 'testHash': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'ledgerHash': hashlib.sha256((args.root/'src/js/30-accounting/01-daily-ledger.js').read_bytes()).hexdigest(), 'summary': counts, 'results': rows, 'scope': 'Real domain commands, v2 Blob/FileReader, confirmed writer and reload; synthetic origin/data only. Helper cases cover correspondence rules without replacing product code.'}
    args.artifact.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    print(json.dumps({'summary': counts, 'artifact': str(args.artifact)}))
    return 1 if counts['PRODUCT_FAIL'] else 0

if __name__ == '__main__':
    raise SystemExit(main())

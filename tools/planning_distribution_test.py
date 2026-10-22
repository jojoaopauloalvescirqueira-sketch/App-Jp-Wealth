#!/usr/bin/env python3
"""Synthetic Planning distribution, confirmed backup round-trip and lifecycle proof."""
import json, os, threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from notes_launcher_test import launch_options
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools/.artifacts/planning-distribution'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
SEED=r'''()=>{
 const before=structuredClone(S),api=JPWPlanning,c={name:'Distribution synthetic',startMonth:'2026-01',initialUsd:1000,profileId:'base',monthlyContributionUsd:100,goals:{adequate:null,ideal:{value:300,currency:'USD'}}};
 const created=api.commands.execute('createAccount',c,api.queries.token());if(!created.ok)throw Error(JSON.stringify(created));
 const id=created.accountId;for(const [type,payload]of [['recordResult',{usd:50}],['recordContribution',{usd:100,brl:500}],['recordWithdrawal',{usd:25}],['finalizeMonth',{confirmFlows:true}]]){
  const r=api.commands.execute(type,{accountId:id,month:'2026-01',...payload},api.queries.token(id));if(!r.ok)throw Error(JSON.stringify(r));
 }
 const after=structuredClone(S);delete before.patrimonialPlanning;delete after.patrimonialPlanning;
 // The existing governance writer may append its technical audit, no financial fact.
 delete before.dataGovernance;delete after.dataGovernance;
 if(JSON.stringify(before)!==JSON.stringify(after))throw Error('Adjacent families changed');
 const model=api.queries.view({accountId:id});if(model.confirmed.balanceUsd!==1125)throw Error('USD oracle mismatch');
 return {aggregate:api.queries.snapshot(),legacy:S.fxPlanning,accountId:id};
}'''
def check(value,msg):
 assert value,msg
 print('PASS '+msg,flush=True)
def boot(browser,url,fixtures=True,workers='block'):
 c=browser.new_context(viewport={'width':1280,'height':900},service_workers=workers)
 c.add_init_script('window.__onbShown=true;')
 if fixtures:install_bootstrap(c,{'USDBRL':5})
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto(url);p.wait_for_function('window.JPWPlanning?.commands&&window.JPWNavigation')
 if fixtures:wait_bootstrap(p)
 return c,p,errors

def main():
 os.chdir(ROOT);OUT.mkdir(parents=True,exist_ok=True)
 s=BrowserFixtureServer(('127.0.0.1',0),Quiet);threading.Thread(target=s.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as pw:
   b=pw.chromium.launch(**launch_options());url=f'http://127.0.0.1:{s.server_port}/index.html'
   c,p,errors=boot(b,url)
   seeded=p.evaluate(SEED);check(p.evaluate("JPWNavigation.navigate('planning')"),'HTTP menu opens')
   p.evaluate("openSettingsModal('backup'); URL.createObjectURL=blob=>{window.__plBackup=blob;return 'blob:synthetic-planning'}; URL.revokeObjectURL=()=>{};HTMLAnchorElement.prototype.click=function(){};")
   p.locator('#exportFullBackupBtn').click();p.wait_for_function('window.__plBackup instanceof Blob')
   text=p.evaluate('window.__plBackup.text()');payload=json.loads(text)
   check(payload['tipo']=='jpwealth_full_backup' and payload['state']['patrimonialPlanning']==seeded['aggregate'],'real Backup Completo exports confirmed aggregate unchanged')
   check(payload['state']['fxPlanning']==seeded['legacy'],'full backup preserves legacy unchanged')
   file=OUT/'synthetic-backup.json';file.write_text(text)
   c2,q,e2=boot(b,url);check(q.evaluate('S.patrimonialPlanning===undefined'),'fresh context has no planning data')
   q.evaluate("openSettingsModal('backup');window.confirm=()=>true;window.alert=()=>{};")
   q.locator('#importFullBackupInput').set_input_files(str(file));q.wait_for_function('S.patrimonialPlanning?.accounts.length===1')
   check(q.evaluate('JPWPlanning.queries.snapshot()')==seeded['aggregate'],'actual import round-trip preserves identifiers, values and reference')
   preserved=q.evaluate('()=>emptyJPWealthState(sessionPreserveLongitudinal().valor).patrimonialPlanning')
   check(preserved==seeded['aggregate'],'session final state preserves the full new aggregate')
   # Reject a secret-bearing import at the real normalization boundary before any write.
   check(q.evaluate('''()=>{const state=structuredClone(S),before=localStorage.getItem(LSKEY);state.patrimonialPlanning.api_key='synthetic-canary';try{normalizeImportedState(state);return false;}catch(e){return /segredo/.test(e.message)&&localStorage.getItem(LSKEY)===before;}}'''),'secret import refused before persistence')
   q.evaluate("closeSettingsModal();JPWModuleAvailability.setState('forex','frozen');")
   check(q.evaluate("JPWNavigation.navigate('forex-planning')&&JPWNavigation.current().primary==='planning'"),'legacy alias independent of frozen Forex')
   q.evaluate("JPWModuleAvailability.setState('planning','frozen');JPWNavigation.navigate('dashboard');JPWDashMacro.render();")
   check(q.locator('[data-dm-card=planning]').count()==0 and q.locator('#nav [data-primary=planning]').is_hidden(),'frozen planning disappears from Dashboard and menu')
   check(not errors and not e2,'HTTP and restore have no page errors')
   c2.close();c.close()
   for label,path in [('modular-file',ROOT/'index.html'),('portable-file',ROOT/'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')]:
    c3,r,er=boot(b,path.as_uri());check(r.evaluate('window.JPWFx===undefined'),'retired engine absent in '+label)
    r.evaluate(SEED);check(r.evaluate("JPWNavigation.navigate('planning')"),label+' renders and writes synthetic confirmed plan')
    check(r.locator('#planning [role=tab][aria-selected=true]').inner_text()=='Comece aqui',label+' has styled native view')
    check(r.evaluate("parseFloat(getComputedStyle(document.querySelector('#planning .pl-shell')).paddingTop)>0"),label+' carries scoped CSS')
    check(not er,label+' no page errors: '+json.dumps(er));c3.close()
   # PWA: actual SW install/cache and offline reload, with no network financial input.
   c4,t,er=boot(b,url,workers='allow');t.wait_for_function('navigator.serviceWorker.controller',timeout=30000)
   t.wait_for_function("caches.keys().then(async keys=>(await caches.open(keys.find(k=>k.startsWith('jp-wealth-')))).match('/src/js/30-accounting/06-planning/03-ui.js').then(Boolean))",timeout=30000)
   t.evaluate(SEED);c4.set_offline(True);t.reload();t.wait_for_function('window.JPWPlanning?.commands')
   check(t.evaluate("JPWNavigation.navigate('planning')&&JPWPlanning.queries.snapshot().accounts.length===1"),'installed PWA reloads Planning offline with confirmed state')
   check(not er,'offline PWA no page errors: '+json.dumps(er));c4.close();b.close()
 finally:s.shutdown()
if __name__=='__main__':main()

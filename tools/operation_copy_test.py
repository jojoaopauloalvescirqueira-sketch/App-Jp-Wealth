#!/usr/bin/env python3
"""A12: clipboard de fatos de operacoes, pela UI e por projecao sem mutacao.

Oraculos fixados antes da implementacao: entradas, composicao, fechamento formal,
whitelist, ausencia != zero, PENDING e feedback real. Dados sinteticos, APIs
controladas pelas fixtures nominais existentes; nenhum clipboard do SO e usado.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import hashlib
import os
import threading

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


SEED = r"""
() => {
  window.__onbShown = true; closeModal();
  S.params.saldoIni = 10000; S.params.saldoAtu = 10240.25;
  S.period = {nome:'Ciclo sintetico 2026', profile:'base'};
  S.phaseUnlocked = [true, false, false, false];
  S.phases.forEach((p, i) => { p.orders = emptyOrders([5, 4, 3, 2][i]); });
  S.activeOperation = {schemaVersion:1, operationId:'op_synthetic_copy',
    openedAt:'2026-09-01T10:00:00.000Z', openedAtSource:'genesis_transition',
    maxAccountPhaseReached:0, privateNote:'SECRET_ACTIVE_NOTE'};
  S.phases[0].orders[0] = {id:'ENTRADA-1',par:'EURUSD',tipo:'BUY',lote:0.0123,
    entry:1.123456789,sl:1.10001,tp:1.23456789,result:0,status:'Aberta',
    openedAt:'2026-09-01T10:00:00.000Z',password:'SECRET_ORDER_PASSWORD',
    token:'SECRET_ORDER_TOKEN',brokerLogin:'SECRET_ORDER_LOGIN'};
  S.accounts = [{nome:'Conta MAM sintetica',tipo:'MESTRE',perfil:'Base',sini:10000,satu:10240.25,
    investorPassword:'SECRET_INVESTOR',platformLogin:'SECRET_LOGIN',token:'SECRET_TOKEN',
    privateKey:'SECRET_PRIVATE_KEY',password:'SECRET_PASSWORD',notes:'SECRET_ACCOUNT_NOTES'}];
  S.onboarding = {...S.onboarding, done:true, brokerLogin:'SECRET_BROKER_LOGIN',
    brokerServer:'SECRET_BROKER_SERVER',investorPassword:'SECRET_OB_INVESTOR'};
  S.riskPinHash = 'SECRET_RISK_PIN_HASH';
  S.operationHistory = {schemaVersion:1,records:[{
    schemaVersion:1,operationId:'op_historical_copy',instrument:'GBPUSD',direction:'SELL',
    openedAt:'2026-08-01T10:00:00.000Z',openedAtSource:'manual_legacy',
    closedAt:'2026-08-05T15:00:00.000Z',closedAtSource:'formal_confirmation',
    finalizedAt:'2026-08-05T15:00:00.001Z',referenceBalance:10000,
    referenceBalanceType:'cycle_initial_balance',netResult:-150.25,
    defenseCount:0,defenseCountSource:'manual',maxAccountPhaseReached:null,
    maxAccountPhaseIntegrity:'unobserved',maxGridPhaseReached:null,
    privateKey:'SECRET_HISTORY_KEY',ordersSnapshot:[{
      phase:1,gridIndex:0,label:'HIST-1',par:'GBPUSD',tipo:'SELL',lote:0.04,
      entry:1.35,sl:1.36,tp:1.3,result:-150.25,status:'Fechada',
      openedAt:'2026-08-01T10:00:00.000Z',closedAt:'2026-08-05T15:00:00.000Z',
      token:'SECRET_HISTORY_ORDER_TOKEN'}]
  }]};
  S.mvpNotes.items = [{id:'draft-fixture',title:'Rascunho',description:'Conteudo sintetico',
    status:'open',updatedAt:'2026-09-01T00:00:00.000Z'}];
  jpWealthPersistenceOutcomeUnknown = false;
  JPWNavigation.navigateLocal('exec', 'panel'); render();
  mvpNotesUI.draft={content:'Rascunho sintetico nao salvo',title:'Rascunho'};
  mvpNotesUI.draftOriginal={content:'Texto original',title:'Rascunho'};
  mvpNotesUI.draftDirty=true;
  localStorage.setItem('a12-synthetic-preservation', 'preference-do-not-touch');
  window.__copyCalls=[]; window.__copyMode='success'; window.__saveCalls=0;
  window.__auditCalls=0; window.__dispatched=[]; window.__fallbackCalls=[];
  Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText(text){
    __copyCalls.push(text);
    if (__copyMode==='pending') return new Promise(resolve => {window.__resolveCopy=resolve;});
    if (__copyMode==='failure') return Promise.reject(new Error('synthetic clipboard denied'));
    return Promise.resolve();
  }}});
  document.execCommand = (command) => {
    __fallbackCalls.push({command,text:document.activeElement && document.activeElement.value});
    return __copyMode==='fallback-success';
  };
  window.__originalSave = save;
  save = (...args) => {__saveCalls++;return __originalSave(...args);};
  window.__originalLog = dgLogChange;
  dgLogChange = (...args) => {__auditCalls++; return __originalLog(...args);};
  window.__originalDispatch = window.dispatchEvent;
  window.dispatchEvent = event => {__dispatched.push(event.type);return __originalDispatch.call(window,event);};
  window.__copySnapshot = () => ({state:JSON.stringify(S), storage:JSON.stringify(
    Object.keys(localStorage).sort().map(key=>[key,localStorage.getItem(key)])),
    notesDraft:JSON.stringify({draft:mvpNotesUI.draft,original:mvpNotesUI.draftOriginal,dirty:mvpNotesUI.draftDirty}),
    saveCalls:__saveCalls,auditCalls:__auditCalls,events:__dispatched.slice()});
}
"""


def run():
    inputs = {name:hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
              ['src/js/20-ui/16-operation-history.js','tools/operation_copy_test.py']}
    print(json.dumps({'input_sha256':inputs}),flush=True)
    handler = partial(Quiet, directory=str(ROOT))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []

    def check(name, passed, detail=None):
        assert passed, f'{name}: {detail}'
        results.append(name)
        print('PASS ' + name, flush=True)

    try:
        with sync_playwright() as pw:
            opts = {'headless':True}
            executable = os.environ.get('JP_WEALTH_CHROMIUM')
            if executable:
                opts['executable_path'] = executable
            browser = pw.chromium.launch(**opts)
            context = browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',has_touch=True)
            install_bootstrap(context)
            context.add_init_script('window.__onbShown=true;')
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='load')
            wait_bootstrap(page)
            page.evaluate(SEED)
            button = page.locator('#copyOperationBtn')
            check('current action visible',button.is_visible())
            before = page.evaluate('__copySnapshot()')
            button.click()
            page.wait_for_function("__copyCalls.length===1 && document.getElementById('operationCopyFeedback').textContent.includes('Operação copiada')")
            text = page.evaluate('__copyCalls[0]')
            check('entry identity and facts',all(s in text for s in ['ABERTA — entrada registrada','op_synthetic_copy','ENTRADA-1','Direção: BUY','2026-09-01T10:00:00.000Z']))
            check('price and lot precision',all(s in text for s in ['Lote: 0,0123','Entrada: 1,123456789','Take profit: 1,23456789']))
            check('open default result not realized','Resultado registrado' not in text and 'Resultado fechado até agora' not in text)
            check('current context identified',all(s in text for s in ['Contexto atual do cadastro','Conta MAM sintetica','Ciclo sintetico 2026','Saldo contábil atual (book, $): $10.240,25']))
            check('no normative labels asserted',all(s not in text for s in ['Liberado para operar','Lucro Técnico:','Alavancagem:','Equity:','Fase da Conta:']))
            check('private fields excluded','SECRET_' not in text,text)
            print('OBSERVED_ENTRY_PAYLOAD ' + json.dumps(text,ensure_ascii=False),flush=True)
            check('copy preserves state storage drafts and counters',page.evaluate('__copySnapshot()')==before)
            button.focus(); page.keyboard.press('Enter')
            page.wait_for_function('__copyCalls.length===2')
            check('keyboard repeat same content',page.evaluate('__copyCalls[1]===__copyCalls[0]'))
            check('keyboard focus retained',button.evaluate('(e)=>e===document.activeElement'))

            page.evaluate("""() => {
              S.phases[0].orders[1]={id:'DEFESA-2',par:'EURUSD',tipo:'BUY',lote:0.01,entry:1.12,sl:1.11,tp:1.14,result:40,status:'Fechada'};
              S.phases[1].orders[0]={id:'MIGRADA-3',par:'EURUSD',tipo:'BUY',lote:0.01,entry:1.11,sl:1.10,tp:1.15,result:99,status:'Migrada'};
              render();
            }""")
            text = page.evaluate('operationCopyProjection(null)')
            check('multi order composition',all(s in text for s in ['EM ANDAMENTO','Ordens registradas nas grades: 3','Ordem F1/1','Ordem F1/2','Ordem F2/1']))
            check('closed sum excludes migrated result','Resultado líquido das ordens fechadas ($): $40,00' in text and '$99,00' not in text)
            check('stable grid order',text.index('ENTRADA-1')<text.index('DEFESA-2')<text.index('MIGRADA-3'))
            page.evaluate("S.phases[0].orders[0].status='Fechada'; S.phases[0].orders[0].result=-10;")
            flat = page.evaluate('operationCopyProjection(null)')
            check('flat not formally finalized','SEM ORDENS ABERTAS — aguarda finalização formal' in flat and 'FINALIZADA' not in flat)
            check('mixed results canonical','Resultado líquido das ordens fechadas ($): $30,00' in flat)
            page.evaluate("S.phases[0].orders[1].par='GBPUSD';")
            check('conflicting thesis explicit','Tese divergente' in page.evaluate('operationCopyProjection(null)'))
            page.evaluate("S.phases[0].orders[1].par='EURUSD'; S.phases[0].orders[1].result=null;")
            check('unknown result no false aggregate','Resultado líquido indisponível' in page.evaluate('operationCopyProjection(null)'))
            page.evaluate("S.phases[0].orders[1].result='PENDING'; S.phases[0].orders[1].tp='PENDING';")
            pending = page.evaluate('operationCopyProjection(null)')
            check('PENDING retained not zero','Take profit: PENDING' in pending and 'Resultado registrado ($): PENDING' in pending and 'Resultado líquido indisponível' in pending)
            page.evaluate("S.phases[0].orders[0].sl=null; S.phases[0].orders[0].tp=0; S.phases[0].orders[0].openedAt=null;")
            first = page.evaluate('operationCopyOrderLines(S.phases[0].orders[0],"F1/1",false).join("\\n")')
            check('absence distinct explicit zero','Stop loss:' not in first and 'Take profit: 0' in first and 'Abertura registrada:' not in first)

            record_text = page.evaluate('operationCopyProjection(S.operationHistory.records[0])')
            check('historical finalized evidence',all(s in record_text for s in ['FINALIZADA — registro histórico','op_historical_copy','Encerramento formal: 2026-08-05T15:00:00.000Z','Resultado líquido registrado ($): -$150,25','Defesas informadas: 0']))
            check('historical absent final context explicit','Conta, perfil, período e métricas finais não foram capturados' in record_text)
            check('historical secrets excluded','SECRET_' not in record_text)
            print('OBSERVED_HISTORY_PAYLOAD ' + json.dumps(record_text,ensure_ascii=False),flush=True)
            missing = page.evaluate("operationCopyProjection({...S.operationHistory.records[0],netResult:null,referenceBalance:null,defenseCount:null})")
            check('historical absent amounts not zero',all(s not in missing for s in ['Resultado líquido registrado ($):','Base do retorno registrada ($):','Defesas informadas:']))
            page.evaluate("S.params.saldoAtu=987654; S.period.nome='Outro ciclo'; S.accounts[0].nome='Outra conta'; S.phases[0].orders[0].entry=3.14;")
            check('history independent current account and grids',page.evaluate('operationCopyProjection(S.operationHistory.records[0])')==record_text)
            page.evaluate("JPWNavigation.navigateLocal('exec','history');")
            page.locator('[data-hist-id="op_historical_copy"]').click()
            historical = page.locator('[data-operation-copy="op_historical_copy"]')
            check('historical action accessible',historical.is_visible())
            before = page.evaluate('__copySnapshot()')
            historical.click()
            page.wait_for_function('__copyCalls.length===3')
            check('historical real click correct payload',page.evaluate('__copyCalls[2]')==record_text)
            check('historical copy immutable',page.evaluate('__copySnapshot()')==before)
            check('historical live feedback',page.locator('[data-operation-copy-feedback]').inner_text().startswith('Operação copiada'))

            page.evaluate("JPWNavigation.navigate('dashboard'); JPWNavigation.navigateLocal('exec','panel'); render(); render(); render();")
            before_count = page.evaluate('__copyCalls.length')
            button.click()
            page.wait_for_function(f'__copyCalls.length==={before_count+1}')
            check('rerenders and navigation single handler',page.evaluate('__copyCalls.length')==before_count+1)
            page.evaluate("__copyMode='pending';")
            before_count = page.evaluate('__copyCalls.length')
            button.click()
            page.wait_for_function('typeof __resolveCopy === "function"')
            check('no early success','Copiando operação' in page.locator('#operationCopyFeedback').inner_text())
            button.click()
            check('pending duplicate suppressed',page.evaluate('__copyCalls.length')==before_count+1)
            page.evaluate('__resolveCopy()')
            page.wait_for_function("document.getElementById('operationCopyFeedback').textContent.includes('Operação copiada')")
            page.evaluate("__copyMode='failure';")
            before = page.evaluate('__copySnapshot()')
            button.click()
            page.wait_for_function("document.getElementById('operationCopyFeedback').textContent.includes('Não foi possível')")
            check('clipboard denial fallback failure visible','Não foi possível copiar' in page.locator('#operationCopyFeedback').inner_text())
            check('denied copy no mutation',page.evaluate('__copySnapshot()')==before)
            check('fallback temporary removed',page.locator('textarea[readonly]').count()==0)
            check('fallback failure focus restored',button.evaluate('(e)=>e===document.activeElement'))
            page.evaluate("__copyMode='fallback-success'; Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined});")
            button.click()
            page.wait_for_function("document.getElementById('operationCopyFeedback').textContent.includes('Operação copiada')")
            check('portable fallback nominal success',page.evaluate('__fallbackCalls.at(-1).command')=='copy')
            check('portable fallback payload',page.evaluate('__fallbackCalls.at(-1).text')==page.evaluate('operationCopyProjection(null)'))
            for width, theme, layout in [(w,t,l) for l in ['sidebar','topbar'] for w in [390,1440] for t in ['light','dark']]:
                page.set_viewport_size({'width':width,'height':950})
                page.evaluate('([theme,layout])=>{document.documentElement.setAttribute("data-theme",theme);mountNavigationLayout(layout);}',[theme,layout])
                button.scroll_into_view_if_needed()
                check(f'action fits viewport {width} {theme} {layout}',button.evaluate('(e)=>{const r=e.getBoundingClientRect();return r.width>0 && r.x>=0 && r.right<=innerWidth+1;}'))
                before = page.evaluate('__copySnapshot()')
                button.tap() if width == 390 else button.click()
                page.wait_for_function("document.getElementById('operationCopyFeedback').textContent.includes('Operação copiada')")
                check(f'copy preserves state {width} {theme} {layout}',page.evaluate('__copySnapshot()')==before)

            page.evaluate('jpWealthPersistenceOutcomeUnknown=true;')
            before = page.evaluate('__copySnapshot()')
            before_count = page.evaluate('__fallbackCalls.length')
            button.click()
            check('unknown persistence not represented confirmed','Persistência indeterminada' in page.locator('#operationCopyFeedback').inner_text())
            check('unknown persistence no copy or mutation',page.evaluate('__fallbackCalls.length')==before_count and page.evaluate('__copySnapshot()')==before)
            page.evaluate('jpWealthPersistenceOutcomeUnknown=false; S.phases.forEach(p=>p.orders=[]); renderOperationCopyAction();')
            check('empty operation action absent',button.is_hidden() and page.evaluate('operationCopyProjection(null)') is None)
            assert_fixture_requests(context)
            check('no unexpected browser errors',not errors,errors)
            build = page.evaluate("typeof JP_WEALTH_BUILD_ID==='undefined'?document.querySelector('script[src*=\"build-id\"]')?.src:JP_WEALTH_BUILD_ID")
            print(json.dumps({'result':'PASS','checks':len(results),'build':build,'passed':results},ensure_ascii=False),flush=True)
            context.close(); browser.close()
    finally:
        server.shutdown();server.server_close()


if __name__ == '__main__':
    run()

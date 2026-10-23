#!/usr/bin/env python3
"""Synthetic, disposable real-browser journeys for the independent Planning UI.

The integration assertion intentionally fails on ea15afc: #planning is absent.
No real browser profile, operator state or live financial records are opened.
"""
from http.server import SimpleHTTPRequestHandler
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse, json, os, threading
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools/.artifacts/planning-ui'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def check(value,message):
    assert value,message
    print('PASS '+message,flush=True)

def account_field(page,name,value):
    """Questionnaire field mapping, not a product adapter or a writer."""
    if name=='startMonth':
        year,month=value.split('-')
        page.locator('#pl-native-ano').fill(year)
        page.locator('#pl-native-mes').select_option(str(int(month)))
        return
    field=page.locator('#planning [name='+name+']')
    # Source groups optional identification and plan choices in collapsed
    # sections. Expand through their real summary before using a field.
    field.evaluate('''el=>{for(let d=el.closest('details');d;d=d.parentElement.closest('details'))d.open=true}''')
    if field.evaluate('el=>el.tagName')=='SELECT':field.select_option(value)
    else:field.fill(value)

def prepare_account_form(page):
    page.locator('#pl-native-sonhoMoeda').select_option('USD')
    page.locator('#pl-native-custoMoeda').select_option('USD')
    if page.locator('#pl-native-perfil').input_value()=='':
        page.locator('#pl-native-openProfiles').click()
        page.locator('[data-pl-choose-profile=base]').click()

def open_create(page):
    if page.evaluate('JPWPlanning.queries.snapshot().accounts.filter(a=>a.active).length')==0:
        page.evaluate("JPWPlanning.ui.selectView('start')")
        page.locator('#planning [data-pl-action=configure]').click()
    else:
        page.evaluate("JPWPlanning.ui.selectView('consolidated')")
        page.locator('#planning [data-pl-action=create]:visible').first.click()
    prepare_account_form(page)

def review_account(page):
    page.locator('#planning dialog.pl-dialog [data-pl-submit]').click()

def confirm_account(page):
    page.locator('#planning dialog.pl-dialog [data-pl-submit]').click()
    done=page.locator('#planning [data-pl-action=native-done]')
    if done.is_visible():done.click()

def flow_field(page,name,value=None):
    field=page.locator('#planning dialog.pl-dialog [name='+name+']')
    for _ in range(4):
        if field.is_visible():
            if value is not None:field.fill(value)
            return field
        page.locator('#planning dialog.pl-dialog [data-pl-submit]').click()
    raise AssertionError('Questionnaire never reached '+name)

def open_flow(page,name):
    page.get_by_role('button',name=name,exact=True).first.click()
    flow_field(page,'usd')

def confirm_flow(page):
    for _ in range(5):
        dialog=page.locator('#planning dialog.pl-dialog')
        if dialog.count()==0:return
        page.locator('#planning dialog.pl-dialog [data-pl-submit]').click()
    raise AssertionError('Questionnaire did not close after deliberate confirmation')

def open_edit(page):
    page.evaluate("JPWPlanning.ui.selectView('accounts')")
    page.get_by_role('button',name='Stoikus ▾',exact=True).click()
    page.locator('#pl-stoikus-menu [data-pl-action=edit-selected]').click()

def future_cell(page,month,field,value):
    page.locator('#planning [data-pl-inline-month="'+month+'"][data-pl-inline-open="'+field+'"]').click()
    cell=page.locator('#planning [data-pl-future-month="'+month+'"][data-pl-future-field="'+field+'"]')
    cell.fill(value)
    cell.press('Tab')
    page.locator('#planning [data-pl-inline-save]').click()
    return page.locator('#planning [data-pl-inline-month="'+month+'"][data-pl-inline-open="'+field+'"]')

def future_visible_value(page,month,field):
    page.locator('#planning [data-pl-inline-month="'+month+'"][data-pl-inline-open="'+field+'"]').click()
    cell=page.locator('#planning [data-pl-future-month="'+month+'"][data-pl-future-field="'+field+'"]')
    value=cell.input_value()
    page.locator('#planning [data-pl-action=inline-cancel]').click()
    return value

def dialog_geometry(page,selector):
    return page.locator(selector).evaluate("""el => {
      const dialog=el.closest('dialog'),form=dialog.querySelector('form'),body=form.querySelector('.pl-form-body');
      const rect=node=>{const r=node.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height}};
      return {element:rect(el),header:rect(form.querySelector('header')),title:rect(form.querySelector('header h2')),close:rect(form.querySelector('header .pl-close')),footer:rect(form.querySelector('footer')),footerItems:[...form.querySelector('footer').children].map(rect),body:rect(body),dialog:rect(dialog),focused:document.activeElement===el,scrollTop:body.scrollTop};
    }""")

def readable_in_dialog(geometry):
    item=geometry['element'];header=geometry['header'];footer=geometry['footer'];body=geometry['body']
    return (item['top']>=max(header['bottom'],body['top'])-1 and
            item['bottom']<=min(footer['top'],body['bottom'])+1 and
            item['left']>=body['left']-1 and item['right']<=body['right']+1)

def mobile_preview_journey(browser,url):
    """Explicit action reveals the whole preview; rendering never moves focus.

    The optional mutation replays the independently observed missing focus/scroll
    interaction over HTTP only. Product files and the official build stay intact.
    This is a geometry/focus regression, not a human-comprehension study.
    """
    mutation=os.environ.get('JPW_PLANNING_PREVIEW_MUTATION')=='1'
    source=(ROOT/'src/js/30-accounting/06-planning/03-ui.js').read_text()
    served=source
    if mutation:
        added="review.focus({preventScroll:true});review.scrollIntoView({block:'start'});"
        assert source.count(added)==1,'Preview mutation must remove exactly the verified focus/scroll delta'
        served=source.replace(added,'')
    ctx=browser.new_context(viewport={'width':390,'height':844},service_workers='block')
    ctx.add_init_script('window.__onbShown=true;');install_bootstrap(ctx,{'USDBRL':5})
    if mutation:ctx.route('**/src/js/30-accounting/06-planning/03-ui.js',lambda route:route.fulfill(status=200,content_type='application/javascript',body=served))
    page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    try:
        page.goto(url);wait_bootstrap(page);page.evaluate("navigateToScreen('planning')")
        open_create(page)
        check(page.locator('#pl-native-custoValor').count()==1 and page.locator('#pl-native-sonhoBRL').count()==1 and 'Qual renda mensal permitiria' in page.locator('#planning dialog.pl-dialog').inner_text(),'account form identifies current monthly cost and desired monthly income separately')
        current=page.evaluate("(() => {const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')})()")
        for key,value in [('name','Prévia mobile sintética'),('startMonth',current),('initialUsd','1000'),('monthlyContributionUsd','100'),('idealValue','300')]:account_field(page,key,value)
        review_account(page)
        geometry=dialog_geometry(page,'#planning [data-pl-native-review] h3')
        review=page.locator('#planning [data-pl-native-review]')
        geometry['focused']=review.evaluate('(el)=>document.activeElement===el')
        suffix='red' if mutation else 'green'
        (OUT/('ui-preview-'+suffix+'-geometry.json')).write_text(json.dumps({'viewport':[390,844],'mutation':mutation,'sourceSha256':sha256(source.encode()).hexdigest(),'servedSourceSha256':sha256(served.encode()).hexdigest(),'geometry':geometry},ensure_ascii=False,indent=2))
        page.screenshot(path=str(OUT/('ui-preview-'+suffix+'-mobile.png')))
        check(readable_in_dialog(geometry),'390px review heading is readable between the dialog header and footer')
        header=geometry['header'];body=geometry['body'];footer=geometry['footer'];dialog=geometry['dialog']
        check(all(rect['top']>=header['top']-1 and rect['bottom']<=min(header['bottom'],body['top'])+1 and rect['left']>=header['left']-1 and rect['right']<=header['right']+1 for rect in [geometry['title'],geometry['close']]) and header['top']>=dialog['top']-1,'390px dialog title and close control remain entirely above the scroll body')
        check(footer['top']>=body['bottom']-1 and footer['bottom']<=dialog['bottom']+1 and all(rect['top']>=footer['top']-1 and rect['bottom']<=footer['bottom']+1 and rect['left']>=footer['left']-1 and rect['right']<=footer['right']+1 for rect in geometry['footerItems']),'390px dialog footer and all its controls remain entirely below the scroll body')
        check(geometry['focused'],'Review preview explicitly focuses the preview region')
        page.evaluate('JPWPlanning.ui.render()')
        check(review.evaluate('(el) => document.activeElement===el'),'ordinary rendering preserves focus in the reviewed preview')
        page.locator('#planning [data-pl-action=native-back]').click()
        account_field(page,'name','Prévia mobile sintética')
        name=page.locator('#planning [name=name]');name.focus()
        before=name.input_value();scroll_before=page.locator('#planning .pl-form-body').evaluate('(el) => el.scrollTop')
        page.evaluate('JPWPlanning.ui.render()')
        check(name.evaluate('(el) => document.activeElement===el') and name.input_value()==before,'ordinary rendering cannot steal focus from an account field')
        check(page.locator('#planning .pl-form-body').evaluate('(el) => el.scrollTop')==scroll_before,'ordinary rendering preserves the focused form scroll position')
        check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length')==0,'reviewing and focusing the preview do not create an account')
        check(not errors,'mobile preview journey has no page errors: '+json.dumps(errors))
        assert_fixture_requests(ctx)
    finally:ctx.close()

def current_month_reading_matches(page,month,amount_text,cost_text):
    """Read the same monthly values through the approved principal/detail layout."""
    trigger=page.locator('#planning [data-pl-select-month="'+month+'"]')
    if trigger.get_attribute('aria-expanded')!='true':trigger.click()
    details=page.locator('#planning [data-pl-month-details="'+month+'"]')
    contribution=page.locator('#planning [data-pl-grid-month="'+month+'"] [data-pl-month-value=contribution], #planning [data-pl-month-details="'+month+'"] [data-pl-month-value=contribution]')
    cost_label=details.get_by_text('Situação do custo',exact=True)
    assert details.is_visible() and contribution.count()==1 and contribution.is_visible(),'one visible current-month contribution remains reachable'
    assert cost_label.count()==1,'one matching current-month cost situation label remains reachable'
    cost=cost_label.locator('..').locator(':scope > dd')
    assert cost.count()==1 and cost.is_visible(),'matching current-month cost situation value remains reachable'
    return amount_text in contribution.inner_text() and cost_text in cost.inner_text()

def current_month_journey(browser,url):
    ctx=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
    ctx.add_init_script('window.__onbShown=true;');install_bootstrap(ctx,{'USDBRL':5})
    page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);wait_bootstrap(page);page.evaluate("navigateToScreen('planning')")
    current=page.evaluate("(() => {const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')})()")
    def create(name):
        open_create(page)
        for key,value in [('name',name),('startMonth',current),('initialUsd','1000'),('monthlyContributionUsd','100'),('idealValue','300')]:account_field(page,key,value)
        review_account(page);confirm_account(page);page.get_by_role('dialog').wait_for(state='hidden')
        page.get_by_role('tab',name='Preenchimento mensal',exact=True).click()
    def result():
        open_flow(page,'Registrar rentabilidade');page.locator('#planning [name=usd]').fill('30');confirm_flow(page);page.get_by_role('dialog').wait_for(state='hidden')
    create('Atual previsto e registrado')
    reading=page.locator('#planning [data-pl-grid-month="'+current+'"]')
    check(current_month_reading_matches(page,current,'100,00','Aporte não confirmado'),'current month qualifies its expected USD100 contribution')
    check('Em andamento' in reading.inner_text() and reading.locator('[data-pl-finalized-month]').input_value()=='Não','current unclosed balance remains explicitly unfinished')
    open_flow(page,'Registrar aporte');page.locator('#planning [name=usd]').fill('20');flow_field(page,'brl','100');confirm_flow(page);page.get_by_role('dialog').wait_for(state='hidden')
    check(current_month_reading_matches(page,current,'20,00','100% do custo informado'),'actual USD20 replaces the expected contribution and has confirmed acquisition cost')
    result();page.get_by_role('button',name='Finalizado = Sim',exact=True).click()
    check('1.050,00' in page.locator('#planning dialog .pl-definition').inner_text(),'finalization preview with USD20 ledger shows effective USD1050')
    page.locator('#planning [name=confirmFlows]').check();page.get_by_role('button',name='Confirmar fechamento',exact=True).click();page.get_by_role('dialog').wait_for(state='hidden')
    check(page.evaluate("JPWPlanning.queries.view({accountId:JPWPlanning.queries.snapshot().accounts[0].id}).confirmed.balanceUsd")==1050,'confirmed USD balance remains separate from current projection')
    create('Atual sem aporte efetivo');result()
    before=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    page.get_by_role('button',name='Finalizado = Sim',exact=True).click()
    check('1.030,00' in page.locator('#planning dialog .pl-definition').inner_text(),'finalization preview excludes the unrecorded USD100 planned contribution')
    check(not page.locator('#planning [name=confirmFlows]').is_checked(),'effective-flow confirmation remains an explicit unchecked choice')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before,'effective USD finalization preview performs zero financial writes')
    page.locator('#planning [name=confirmFlows]').check();page.get_by_role('button',name='Confirmar fechamento',exact=True).click();page.get_by_role('dialog').wait_for(state='hidden')
    check(page.evaluate("JPWPlanning.queries.view({accountId:JPWPlanning.queries.snapshot().accounts[1].id}).confirmed.balanceUsd")==1030,'closure without actual contribution saves effective USD1030')
    check(not errors,'isolated planning journey has no page errors: '+json.dumps(errors))
    assert_fixture_requests(ctx);ctx.close()

def past_start_journey(browser,url):
    """A plan started in the past explains unregistered months instead of a day-one delay."""
    ctx=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
    ctx.add_init_script('window.__onbShown=true;');install_bootstrap(ctx,{'USDBRL':5})
    page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);wait_bootstrap(page);page.evaluate("navigateToScreen('planning')")
    current,past=page.evaluate("(() => {const d=new Date(),k=x=>x.getFullYear()+'-'+String(x.getMonth()+1).padStart(2,'0');return [k(d),k(new Date(d.getFullYear(),d.getMonth()-9,1))]})()")
    deadlines=lambda:page.locator('#planning .pl-native-deadlines').inner_text()
    def create(name,start):
        open_create(page)
        for key,value in [('name',name),('startMonth',start),('initialUsd','1000'),('monthlyContributionUsd','100'),('idealValue','300')]:account_field(page,key,value)
    create('Início no passado',past)
    note=page.locator('#pl-native-pastStart')
    check(note.is_visible() and '9 meses passados sem fechamento' in note.inner_text(),'form preview explains nine past months without closure')
    before=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    review_account(page)
    check('MESES PASSADOS: Há 9 meses passados sem fechamento' in page.locator('#planning [data-pl-preview]').inner_text(),'plan review repeats the past-months notice')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before,'past-months notice performs zero financial writes')
    confirm_account(page);page.get_by_role('dialog').wait_for(state='hidden')
    page.evaluate("JPWPlanning.ui.selectView('consolidated')")
    check('Comparação após registrar 9 meses passados' in deadlines() and 'depois do plano' not in deadlines(),'Consolidado waits for past records instead of a day-one delay')
    page.evaluate('''() => {const api=JPWPlanning,id=api.queries.snapshot().accounts.find(a=>a.active).id;
      for(const row of api.queries.view({accountId:id}).rows.filter(r=>r.phase==='pending')){
        for(const [type,payload] of [['recordResult',{accountId:id,month:row.month,usd:30}],['finalizeMonth',{accountId:id,month:row.month,confirmFlows:true}]]){
          const r=api.commands.execute(type,payload,api.queries.token(id));if(!r.ok)throw Error(JSON.stringify(r));}}
      api.ui.render(true);}''')
    check('Comparação após registrar' not in deadlines() and 'do plano' in deadlines(),'closing every past month restores the plan comparison')
    create('Início no mês atual',current)
    check(page.locator('#pl-native-pastStart').is_hidden(),'counterproof: current-month start shows no past-months notice')
    review_account(page)
    check('MESES PASSADOS' not in page.locator('#planning [data-pl-preview]').inner_text(),'counterproof: current-month review has no past-months line')
    check(not errors,'past-start journey has no page errors: '+json.dumps(errors))
    assert_fixture_requests(ctx);ctx.close()

def native_stop(page,current):
    before=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    account=page.evaluate('JPWPlanning.queries.snapshot().accounts.find(a=>a.active)')
    open_edit(page)
    page.locator('#pl-native-stopOpen').click()
    limit=page.locator('#pl-native-stopLimit')
    check(limit.input_value()=='5','native stop impact limit defaults to five percent')
    bounds=page.evaluate('(month) => JPWPlanning.engine.stopBounds(JPWPlanning.queries.snapshot().accounts.find(a=>a.active).plan,{month})',current)
    month=page.locator('#pl-native-stopMonth')
    check(month.get_attribute('min')==bounds['min'] and month.get_attribute('max')==bounds['max'],'native manual stop month respects existing-plan calendar bounds')
    month.fill(bounds['min']);month.press('Tab')
    check(page.locator('#pl-native-stopUse').is_disabled(),'five percent cap blocks an excessive early stop')
    check('acima do limite' in page.locator('#pl-native-stopMessage').inner_text(),'native stop explains excess impact before accepting the date')
    page.locator('#pl-native-stopFind').click()
    expected=page.evaluate('(month) => JPWPlanning.engine.findContributionStop(JPWPlanning.queries.snapshot().accounts.find(a=>a.active).plan,{month,impactLimit:.05})',current)
    check(expected is not None and month.input_value()==expected['stopAfter'],'native search selects the first stop month within the impact cap')
    check('Dentro do limite' in page.locator('#pl-native-stopMessage').inner_text(),'eligible native stop communicates its impact cap')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before,'native stop search remains a temporary simulation with zero writes')
    page.locator('#pl-native-stopUse').click()
    check(page.locator('#planning dialog.pl-dialog').is_visible(),'using a stop date returns to the unsaved form')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before,'using the native date does not save before complete form confirmation')
    review_account(page)
    check('PARADA DOS APORTES' in page.locator('#planning [data-pl-preview]').inner_text(),'native review includes the pending stop choice')
    confirm_account(page)
    page.get_by_role('dialog').wait_for(state='hidden')
    after=page.evaluate('(id)=>JPWPlanning.queries.account(id)',account['id'])
    model=page.evaluate('(id)=>JPWPlanning.queries.view({accountId:id})',account['id'])
    check(after['plan']['stopAfter']==expected['stopAfter'] and abs(model['rows'][-1]['closeUsd']-expected['result']['finalUsd'])<1e-8,'confirmed native stop matches the searched financial result')
    for key in ['contributions','withdrawals','results']:
        check(after['plan'][key]==account['plan'][key],'native stop preserves actual '+key)
    return before

def contribution_stop_journey(browser,url):
    ctx=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
    ctx.add_init_script('window.__onbShown=true;');install_bootstrap(ctx,{'USDBRL':5})
    page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);wait_bootstrap(page);page.evaluate("navigateToScreen('planning')")
    current=page.evaluate("(() => {const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')})()")
    open_create(page)
    for key,value in [('name','Parada e limite sintéticos'),('startMonth',current),('initialUsd','1000'),('monthlyContributionUsd','100'),('idealValue','300')]:account_field(page,key,value)
    review_account(page);confirm_account(page);page.get_by_role('dialog').wait_for(state='hidden')
    native_stop(page,current)
    check(not errors,'isolated native stop journey has no page errors: '+json.dumps(errors))
    assert_fixture_requests(ctx);ctx.close()

def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=OUT)
    OUT=parser.parse_args().out
    os.chdir(ROOT); OUT.mkdir(parents=True,exist_ok=True)
    server=BrowserFixtureServer(('127.0.0.1',0),Quiet)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            opts={'headless':True}
            if os.environ.get('JP_WEALTH_CHROMIUM'):opts['executable_path']=os.environ['JP_WEALTH_CHROMIUM']
            browser=pw.chromium.launch(**opts)
            ctx=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
            ctx.add_init_script('window.__onbShown=true;')
            install_bootstrap(ctx,{'USDBRL':5})
            page=ctx.new_page(); errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page)
            check(page.locator('section#planning').count()==1,'independent section#planning exists')
            page.evaluate("navigateToScreen('planning')")
            page.locator('#planning [data-pl-action=configure]').wait_for()
            check(page.locator('#planning [role=tab][aria-selected=true]').inner_text()=='Comece aqui','source default view is Comece aqui')
            check(page.evaluate('JPWPlanning.ui.hasPendingWork()') is False,'empty view has no financial drafts')
            check(page.locator('#planning .pl-legacy').count()==0,'empty legacy container does not claim that prior records exist')
            open_create(page)
            check(page.locator('#pl-native-ano').get_attribute('min')=='1900' and page.locator('#pl-native-ano').get_attribute('max')=='2199' and page.locator('#pl-native-mes option').count()==13,'split initial year/month questions expose the approved calendar range')
            account_field(page,'name','Conta sintética UI')
            account_field(page,'startMonth','2026-01')
            page.locator('#planning [name=initialUsd]').fill('100')
            page.locator('#planning [name=monthlyContributionUsd]').fill('20')
            page.locator('#planning [name=idealValue]').fill('300')
            account_field(page,'startMonth','1800-01')
            review_account(page)
            check(page.locator('#pl-native-ano').evaluate('(el) => el.validity.rangeUnderflow'),'out-of-range initial month remains invalid before preview')
            check(page.locator('#planning [data-pl-native-review]').is_hidden() and page.evaluate('JPWPlanning.queries.snapshot().accounts.length')==0,'invalid initial month cannot preview or create an account')
            account_field(page,'startMonth','2026-01')
            review_account(page)
            check(page.locator('#planning [data-pl-preview]').is_visible(),'account creation requires an engine preview')
            confirm_account(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length')==1,'explicit create writes one account')
            page.get_by_role('tab',name='Preenchimento mensal',exact=True).click()
            page.locator('#planning [data-pl-account]').select_option(page.evaluate('JPWPlanning.queries.snapshot().accounts.find(a=>a.active).id'))
            page.locator('#planning [data-pl-month]').select_option('2026-01')
            open_flow(page,'Registrar rentabilidade')
            result_copy=page.locator('#planning [data-pl-flow-step=usd] .pl-flow-prompt')
            result_text=result_copy.inner_text()
            check(all(term in result_text for term in ['RESULTADO TOTAL','Lucro: valor positivo','Prejuízo: valor negativo','Não inclua aportes ou retiradas','substitui o total anterior','não soma']),'result dialog explains USD total, profit/loss sign, excluded flows and replacement semantics')
            check(readable_in_dialog(dialog_geometry(page,'#planning [data-pl-flow-step=usd] .pl-flow-prompt')),'financial result instructions are readable inside the dialog')
            check(page.locator('#planning [data-pl-flow-step=usd]').get_by_text('Resultado total do mês em dólares',exact=True).count()==1,'result field is labeled as the total monthly USD amount')
            page.locator('#planning [name=usd]').fill('5')
            page.evaluate('JPWPlanning.ui.render()')
            check(page.locator('#planning [name=usd]').input_value()=='5','render preserves focused financial draft')
            page.keyboard.press('Escape')
            check(page.evaluate('JPWPlanning.ui.hasPendingWork()'),'closing dialog retains draft')
            page.evaluate('boot()')
            check(page.evaluate('JPWPlanning.ui.hasPendingWork()'),'ordinary boot does not discard a closed planning draft')
            closed_drafts=page.evaluate("jpwWorkspaceCapture().drafts.filter(d=>d.provider==='patrimonial-planning')")
            check(len(closed_drafts)==1,'Backup Completo captures financial drafts after Escape')
            check(json.loads(closed_drafts[0]['text'])['fields']['usd']=='5','closed draft backup retains exact typed value')
            check('token' not in json.dumps(closed_drafts),'closed draft backup excludes operational tokens')
            check(page.evaluate('(item) => JPWWorkspaceDrafts.inspect(item).compatible',closed_drafts[0]) is False,'imported financial draft remains read-only until reviewed')
            open_flow(page,'Registrar rentabilidade')
            check(page.locator('#planning [name=usd]').input_value()=='5','reopened field restores original draft')
            confirm_flow(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            open_flow(page,'Registrar aporte')
            page.locator('#planning [name=usd]').fill('20')
            flow_field(page,'brl','100')
            confirm_flow(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            page.get_by_role('button',name='Finalizado = Sim',exact=True).click()
            page.locator('#planning [name=confirmFlows]').check()
            page.get_by_role('button',name='Confirmar fechamento',exact=True).click()
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate("JPWPlanning.queries.view({accountId:JPWPlanning.queries.snapshot().accounts[0].id}).confirmed.balanceUsd") == 125,'result and end-of-month contribution match independent oracle')
            page.evaluate("JPWPlanning.ui.selectView('reference')")
            check(page.evaluate('JPWPlanning.ui.getView()')=='consolidated','old reference view resolves to Consolidado')
            check(page.evaluate('JPWPlanning.queries.sheetView({accountId:JPWPlanning.queries.snapshot().accounts[0].id}).sheet.reference.rows.length')==120,'immutable reference remains readable internally')
            page.get_by_role('tab',name='Consolidado',exact=True).click()
            check(page.locator('#planning svg[data-pl-chart] path').count()>0,'graph contains prepared trajectories')
            check(page.locator('#planning svg[data-pl-chart] .pl-confirmed-dot').count()==1,'single confirmed month remains visible on the graph')
            check('NOT_INFORMED' not in page.locator('#planning').inner_text(),'goal states use clear Portuguese labels')
            before_sim=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            temporary=page.evaluate('()=>JPWPlanning.engine.simulate(JPWPlanning.queries.snapshot().accounts[0].plan,{month:new Date().toISOString().slice(0,7),increasePct:5})')
            check(temporary['finalUsd'] is not None,'temporary contribution simulation returns an available financial result')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before_sim,'temporary increase simulation does not save financial data')
            current=page.evaluate("new Date().toISOString().slice(0,7)")
            native_stop(page,current)
            check(page.evaluate('JPWPlanning.queries.snapshot().accounts[0].plan.stopAfter') is not None,'explicit native form confirmation saves the future stop')
            page.get_by_role('tab',name='Preenchimento mensal',exact=True).click()
            check(page.locator('#planning [data-pl-annual]').count()==1,'annual summary uses the domain read model')
            check(page.get_by_role('button',name='Consultar referência histórica',exact=True).is_visible(),'past BRL quote is available on demand')
            before_fx=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            ctx.route('https://api.frankfurter.dev/v2/rate/USD/BRL?date=2026-01-31&providers=ecb',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps({'date':'2026-01-30','base':'USD','quote':'BRL','rate':5})))
            page.get_by_role('button',name='Consultar referência histórica',exact=True).click()
            page.wait_for_function("() => document.querySelector('#planning [data-pl-notice]').textContent.includes('2026-01-30')")
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before_fx,'historical FX lookup does not save financial data')
            check('625,00' in page.locator('#planning [data-pl-grid-month="2026-01"]').inner_text(),'past BRL reading uses the month reference')
            delayed=[]
            ctx.route('https://api.frankfurter.dev/v2/rate/USD/BRL?date=2026-02-28&providers=ecb',lambda route:delayed.append(route))
            page.locator('#planning [data-pl-month]').select_option('2026-02')
            page.get_by_role('button',name='Consultar referência histórica',exact=True).click()
            page.wait_for_timeout(100)
            check(len(delayed)==1,'historical lookup is requested only by explicit action')
            delayed_snapshot=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            page.evaluate("navigateToScreen('dashboard'); JPWPlanning.ui.reset()")
            hidden_html=page.locator('#planning').inner_html()
            delayed[0].fulfill(status=200,content_type='application/json',body=json.dumps({'date':'2026-02-27','base':'USD','quote':'BRL','rate':6}))
            page.wait_for_timeout(100)
            check(page.locator('#planning').inner_html()==hidden_html,'late historical response cannot redraw a hidden/reset UI')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==delayed_snapshot,'late historical response cannot write financial state')
            page.evaluate("navigateToScreen('planning'); JPWPlanning.ui.selectView('monthly')")
            page.locator('#planning [data-pl-account]').select_option(page.evaluate('JPWPlanning.queries.snapshot().accounts.find(a=>a.active).id'))
            page.locator('#planning [data-pl-month]').select_option('2026-01')
            page.get_by_role('tab',name='Consolidado',exact=True).click()
            check(page.evaluate("document.getElementById('nav').getBoundingClientRect().width")>150,'desktop navigation retains its usable width after dialogs')
            page.wait_for_timeout(500)
            page.screenshot(path=str(OUT/'ui-desktop-viewport.png'))
            page.screenshot(path=str(OUT/'ui-desktop.png'),full_page=True)
            page.evaluate('() => {window.__planningPrints=0; window.print=()=>{window.__planningPrints++}}')
            page.get_by_role('button',name='Gerar PDF',exact=True).click()
            check(page.evaluate('window.__planningPrints')==1,'PDF action opens native print: '+str(page.evaluate('window.__planningPrints')))
            page.emulate_media(media='print')
            check(page.locator('#planning').is_visible(),'print stylesheet keeps the planning report visible')
            check(not page.locator('#appSidebar').is_visible(),'print stylesheet removes global navigation')
            page.pdf(path=str(OUT/'ui-report.pdf'),format='A4',print_background=True)
            page.emulate_media(media='screen')
            page.locator('#planning [data-pl-view=consolidated]').focus()
            page.keyboard.press('ArrowRight')
            check(page.evaluate('JPWPlanning.ui.getView()')=='monthly','internal tabs support keyboard arrows')
            page.set_viewport_size({'width':390,'height':844})
            page.get_by_role('tab',name='Preenchimento mensal',exact=True).click()
            check(page.locator('#planning [data-pl-month]').is_visible(),'mobile month selector is visible')
            check(page.evaluate("document.querySelector('#planning').scrollWidth <= document.querySelector('#planning').clientWidth+1"),'planning surface fits mobile width')
            page.screenshot(path=str(OUT/'ui-mobile.png'),full_page=True)
            page.set_viewport_size({'width':1440,'height':1000})
            page.get_by_role('button',name='Reabrir mês',exact=True).click()
            page.locator('#planning [name=reason]').fill('Conferência sintética de fluxo')
            page.get_by_role('button',name='Reabrir para corrigir',exact=True).click()
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate("JPWPlanning.queries.snapshot().accounts[0].plan.closures['2026-01'].confirmed") is False,'reopen requires a reason and invalidates closure')
            page.locator('#planning .pl-ledger summary').click()
            page.get_by_role('button',name='Corrigir',exact=True).click();flow_field(page,'usd')
            page.locator('#planning [name=usd]').fill('25')
            flow_field(page,'brl','125')
            confirm_flow(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate('JPWPlanning.queries.snapshot().accounts[0].plan.contributions[0].previous.usd')==20,'correction preserves original flow by ID')
            page.locator('#planning .pl-ledger summary').click()
            before_zero=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            page.get_by_role('button',name='Corrigir',exact=True).click();flow_field(page,'usd','0')
            page.locator('#planning dialog.pl-dialog [data-pl-submit]').click()
            check(page.locator('#planning [data-pl-form-error]').inner_text()!='','native aporte questionnaire rejects a zero-dollar purchase correction')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before_zero,'rejected zero aporte correction preserves the previous purchase and its history')
            page.keyboard.press('Escape')
            open_flow(page,'Registrar saque')
            page.locator('#planning [name=usd]').fill('1')
            confirm_flow(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate('JPWPlanning.queries.snapshot().accounts[0].plan.withdrawals[0].usd')==1,'withdrawal accepts optional BRL without coercing it to zero')
            future=page.evaluate("JPWPlanning.engine.addMonths(new Date().toISOString().slice(0,7),1)")
            page.locator('#planning [data-pl-month]').select_option(future)
            future_cell(page,future,'rate','0')
            future_cell(page,future,'contributionUsd','0')
            check(page.evaluate('(m) => JPWPlanning.queries.snapshot().accounts[0].plan.future[m].rate',future)==0,'future zero rate remains explicit zero')
            rate_cell=page.locator('#planning [data-pl-inline-month="'+future+'"][data-pl-inline-open=rate]')
            check(future_visible_value(page,future,'rate')=='0','explicit zero projection reopens as zero')
            future_cell(page,future,'rate','')
            future_cell(page,future,'contributionUsd','12')
            check(page.evaluate('(m) => JPWPlanning.queries.snapshot().accounts[0].plan.future[m].rate',future) is None,'blank projection saves as provisional null')
            check(future_visible_value(page,future,'rate')=='','provisional rate reopens blank instead of a calculated zero')
            future_cell(page,future,'contributionUsd','17')
            check(page.evaluate('(m) => JPWPlanning.queries.snapshot().accounts[0].plan.future[m].rate',future) is None,'editing only contribution preserves provisional null rate')
            check('Pendente' in page.locator('#planning [data-pl-grid-month="'+future+'"]').inner_text() and future_visible_value(page,future,'rate')=='','monthly table distinguishes provisional blank from explicit zero')
            future_cell(page,future,'contributionUsd','')
            check(page.evaluate('(m)=>JPWPlanning.queries.snapshot().accounts[0].plan.future[m].contributionUsd',future)=='','native future contribution preserves an explicitly blank cell')
            check(future_visible_value(page,future,'contributionUsd')=='','saved blank contribution stays visually blank rather than showing zero')
            check(page.evaluate('(m)=>{const a=JPWPlanning.queries.snapshot().accounts[0];return JPWPlanning.queries.view({accountId:a.id}).rows.find(r=>r.month===m).contributionUsd}',future)==0,'blank future contribution calculates as zero without creating a ledger entry')
            future_cell(page,future,'contributionUsd','17')
            page.evaluate("JPWPlanning.ui.selectView('accounts')")
            original_ref=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot().accounts[0].plan.reference)')
            pre_edit_rows=page.evaluate('JPWPlanning.queries.view({accountId:JPWPlanning.queries.snapshot().accounts[0].id}).rows')
            before_preview=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            open_edit(page)
            account_field(page,'name','Prévia preserva histórico')
            review_account(page)
            preview_model=page.evaluate('() => {const a=JPWPlanning.queries.snapshot().accounts[0];return JPWPlanning.queries.previewAccount({accountId:a.id,config:{name:\'Prévia preserva histórico\'}}).model;}')
            check(preview_model['rows']==pre_edit_rows and 'manter os aportes e as rentabilidades' in page.locator('#planning [data-pl-preview]').inner_text(),'metadata review preserves ledger, future overrides and contribution stop')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before_preview,'edit preview performs zero financial writes')
            confirm_account(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate('JPWPlanning.queries.view({accountId:JPWPlanning.queries.snapshot().accounts[0].id}).rows')==pre_edit_rows,'saved metadata edit matches the previewed financial timeline')
            open_edit(page)
            protected_before=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            account_field(page,'startMonth','2027-01');review_account(page)
            check(page.locator('#planning [data-pl-native-review]').is_hidden() and page.locator('#planning [data-pl-form-error]').inner_text()!='','recorded facts block initial calendar changes at review')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==protected_before,'rejected initial edit preserves recorded facts')
            account_field(page,'startMonth','2026-01')
            account_field(page,'name','Conta sintética revista')
            page.locator('#planning [name=idealCurrency]').select_option('BRL')
            page.locator('#planning [name=replaceFuture]').evaluate("el=>el.closest('details').open=true");page.locator('#planning [name=replaceFuture]').check()
            review_account(page)
            confirm_account(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot().accounts[0].plan.reference)')==original_ref,'metadata edit preserves initial reference')
            quote_cache=page.evaluate('localStorage.getItem(JPWMarket.usdBrl.CACHE_KEY)')
            original_goal=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot().accounts[0].plan.goals.ideal)')
            page.evaluate('localStorage.removeItem(JPWMarket.usdBrl.CACHE_KEY)')
            open_edit(page)
            account_field(page,'broker','Identificação offline')
            review_account(page)
            check(page.locator('#planning button[data-pl-submit]').is_enabled(),'unchanged BRL goal remains editable offline with its original quote')
            confirm_account(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot().accounts[0].plan.goals.ideal)')==original_goal,'offline metadata edit preserves exact BRL goal snapshot')
            page.evaluate('(raw) => localStorage.setItem(JPWMarket.usdBrl.CACHE_KEY,raw)',quote_cache)
            old_plan=page.evaluate('JPWPlanning.queries.snapshot().accounts[0].plan.id')
            original_before_reset=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot().accounts[0].plan.reference)')
            page.get_by_role('button',name='Stoikus ▾',exact=True).click()
            page.locator('#planning [data-pl-action=restart-selected]').click()
            page.locator('#planning [name=resetScope]').select_option('CONTA')
            confirmation=page.locator('#planning [name=confirmation]')
            phrase=page.locator('#planning [data-pl-reset-phrase]').inner_text().split('digite ',1)[-1]
            check(phrase=='REINICIAR C001','native reset requires its original explicit account confirmation phrase')
            confirmation.fill(phrase)
            understanding=page.locator('#planning [name=resetUnderstood]')
            check(not understanding.is_checked(),'native reset understanding confirmation starts unchecked')
            before_understanding=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            check(page.get_by_role('button',name='Confirmar reinício',exact=True).is_disabled(),'correct reset phrase leaves confirmation disabled until the understanding choice')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before_understanding,'correct reset phrase cannot bypass the separate unchecked understanding confirmation')
            understanding.check()
            page.get_by_role('button',name='Confirmar reinício',exact=True).click()
            page.get_by_role('dialog').wait_for(state='hidden')
            reset_plan=page.evaluate('JPWPlanning.queries.snapshot().accounts[0].plan')
            check(reset_plan['id']!=old_plan and not reset_plan['results'] and not reset_plan['contributions'] and not reset_plan['withdrawals'] and not reset_plan['closures'],'dedicated account reset archives the former identity and clears effective facts')
            reset_reference=reset_plan['reference'];reset_reference['planId']=old_plan
            check(reset_reference==json.loads(original_before_reset),'dedicated reset preserves the financial reference and retargets only its plan association')
            page.evaluate("JPWPlanning.ui.selectView('accounts')")
            archive_before=page.evaluate('JPWPlanning.queries.snapshot().archive.length')
            open_edit(page)
            page.locator('#pl-native-novo').evaluate("el=>{el.closest('.optional-section').open=true;el.closest('.advanced-new').open=true}")
            page.locator('#pl-native-novo').check()
            check(page.locator('#pl-native-novo').is_checked(),'native Iniciar outro plano requires its explicit checked archive choice')
            review_account(page)
            confirm_account(page)
            page.get_by_role('dialog').wait_for(state='hidden')
            check(page.evaluate('JPWPlanning.queries.snapshot().accounts[0].plan.id')!=old_plan,'restart creates a new plan identity')
            check(page.evaluate('JPWPlanning.queries.snapshot().archive.length')==archive_before+1,'restart archives the prior plan in addition to prior reset history')
            page.evaluate("JPWPlanning.ui.selectView('accounts')")
            # Archive remains a state/backup capability; its retired accounts page is not a public surface.
            page.evaluate("()=>{const a=JPWPlanning.queries.snapshot().accounts.find(a=>a.active),r=JPWPlanning.commands.execute('archiveAccount',{accountId:a.id,confirmation:true},JPWPlanning.queries.token(a.id));if(!r.ok)throw Error(JSON.stringify(r));JPWPlanning.ui.render(true)}")
            check(page.evaluate('JPWPlanning.queries.snapshot().accounts[0].active') is False,'archive preserves the account as inactive')
            check(page.evaluate('JPWPlanning.queries.snapshot().accounts[0].plan.id') is not None,'archived account plan remains readable internally for recovery')
            before=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            page.evaluate("navigateToScreen('dashboard'); JPWPlanning.ui.render()")
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before,'hidden render does not write financial state')
            check(not errors,'no browser page errors: '+json.dumps(errors))
            page.reload();wait_bootstrap(page);page.evaluate("navigateToScreen('planning'); JPWPlanning.ui.selectView('accounts')")
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before,'confirmed account archive survives a page reload')
            open_create(page)
            for name,value in [('name','Conta de falha sintética'),('startMonth','2026-01'),('initialUsd','100'),('monthlyContributionUsd','20'),('idealValue','300')]:
                account_field(page,name,value)
            review_account(page)
            before_refusal=page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
            page.evaluate("() => {window.__planningSetItem=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){if(k==='jpwealth_v9_state')throw new DOMException('Synthetic quota','QuotaExceededError');return __planningSetItem.call(this,k,v)}}")
            confirm_account(page)
            check(page.get_by_role('dialog').is_visible(),'storage refusal keeps the account draft open')
            check(page.locator('#planning [name=name]').input_value()=='Conta de falha sintética','storage refusal preserves the typed account draft')
            check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')==before_refusal,'storage refusal cannot adopt an unconfirmed account')
            check('não foi confirmada' in page.locator('#planning [data-pl-form-error]').inner_text(),'storage refusal explains the unconfirmed result')
            check('Alteração confirmada' not in page.locator('#planning [data-pl-notice]').inner_text(),'storage refusal cannot leave a misleading success notice')
            page.evaluate('() => {Storage.prototype.setItem=window.__planningSetItem}')
            reset_drafts=page.evaluate("jpwWorkspaceDraftProviders.get('patrimonial-planning')(true)")
            check(reset_drafts==[] and page.evaluate('JPWPlanning.ui.hasPendingWork()') is False,'import/finalization provider reset clears drafts and invalidates their callbacks')
            page.evaluate("navigateToScreen('planning'); JPWPlanning.ui.reset(); S.patrimonialPlanning={schemaVersion:2,accounts:'invalid'}; JPWPlanning.ui.render()")
            check(page.locator('#planning [data-pl-incompatible]').is_visible(),'malformed future aggregate displays a blocking read state')
            check(page.locator('#planning [data-pl-action=create]:enabled').count()==0,'incompatible aggregate cannot offer a misleading create action')
            assert_fixture_requests(ctx)
            ctx.close();current_month_journey(browser,f'http://127.0.0.1:{server.server_port}/index.html');past_start_journey(browser,f'http://127.0.0.1:{server.server_port}/index.html');contribution_stop_journey(browser,f'http://127.0.0.1:{server.server_port}/index.html');mobile_preview_journey(browser,f'http://127.0.0.1:{server.server_port}/index.html');browser.close()
    finally:server.shutdown()
if __name__=='__main__':main()

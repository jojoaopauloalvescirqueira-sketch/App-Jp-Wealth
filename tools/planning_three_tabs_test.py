#!/usr/bin/env python3
"""Approved three-page Planning contract, synthetic browser journeys.

Oracle: docs/superpowers/plans/2026-10-20-planning-three-tabs.md Task1.
The original form remains the question/mathematical oracle; the live Sheet hides
Reference. Tests assert public behavior and unchanged saved data, not markup text.
"""
import argparse
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler
import json
import os
from pathlib import Path
import threading
import traceback
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from notes_launcher_test import launch_options

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tools/.artifacts/planning-three-tabs'
SOURCES = ['src/js/30-accounting/06-planning/03-ui.js', 'src/styles/app.css',
           'src/js/30-accounting/06-planning/01-engine.js', 'src/js/30-accounting/06-planning/02-state.js',
           'tools/planning_three_tabs_test.py']

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args): pass

def check(ok, message):
    assert ok, message
    print('PASS ' + message, flush=True)

def saved(page):
    return page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')

def seed(page, count=2):
    return page.evaluate('''count=>{const ids=[];for(let i=0;i<count;i++){
      const r=JPWPlanning.commands.execute('createAccount',{name:'Conta sintética '+(i+1),
       startMonth:'2026-10',initialUsd:1000,profileId:'base',monthlyContributionUsd:100,
       goals:{adequate:{value:50,currency:'USD'},ideal:{value:100,currency:'USD'}}},JPWPlanning.queries.token());
      if(!r.ok)throw Error(JSON.stringify(r));ids.push(r.accountId);
      }JPWPlanning.ui.render(true);return ids;}''', count)

def form(page):
    return page.locator('#planning dialog.pl-dialog')

def configure(page):
    page.locator('#planning [data-pl-view=start]').click()
    page.locator('#planning [data-pl-action=configure]').click()

def close(page):
    page.keyboard.press('Escape')
    check(not form(page).count(), 'Escape closes outer form/choice')

def tabs_case(page):
    ids = seed(page, 1)
    check(page.locator('#planning [role=tab]').all_text_contents() ==
          ['Comece aqui','Consolidado','Preenchimento mensal'], 'only the three current public pages exist')
    before = saved(page)
    for alias in ['reference', 'accounts']:
        page.evaluate('(name)=>JPWPlanning.ui.selectView(name)', alias)
        check(page.evaluate('JPWPlanning.ui.getView()') == 'consolidated', alias+' alias resolves to Consolidado')
    check(saved(page) == before, 'legacy aliases do not write state')
    check(page.evaluate('(id)=>JPWPlanning.queries.sheetView({accountId:id}).sheet.reference.rows.length', ids[0]) == 120,
          'internal immutable reference still returns all 120 rows')

def public_case(page):
    ids = seed(page, 1)
    page.evaluate("S.fxPlanning={schemaVersion:1,plan:{sentinel:'synthetic-legacy'}};JPWPlanning.ui.render(true)")
    before = saved(page)
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option(ids[0])
    page.locator('#planning [data-pl-action=menu]').click()
    menu = page.locator('#pl-stoikus-menu')
    for action in ['reference','track','refresh']:
        check(menu.locator('[data-pl-action='+action+']').count() == 0, 'Stoikus removes public '+action+' action')
    for action in ['create','edit-selected','restart-selected','history','explain-goals','result',
                   'contribution','withdrawal','contribution-history','withdrawal-history','print']:
        check(menu.locator('[data-pl-action='+action+']').count() == 1, 'Stoikus preserves operational '+action)
    page.locator('#planning [data-pl-action=menu]').click()
    text = page.locator('#planning').inner_text()
    check('O efeito de aumentar os aportes' not in text,
          'retired public effort comparison is absent')
    check(page.locator('#planning .pl-native-objectives').count()==1 and
          'Renda mensal desejada' in text and 'Patrimônio estimado' in text,
          'current source objective and estimated capital remain visible')
    check(page.locator('#planning .pl-account-operations').count()==0,
          'legacy account-management page is not relocated into Consolidado')
    check(page.locator('#planning .pl-legacy').count() == 0 and
          page.locator('#planning [data-pl-action=reference]').count() == 0,
          'legacy warnings and hidden-page shortcuts are absent')
    check(page.evaluate("JPWPlanning.queries.legacy().value.plan.sentinel") == 'synthetic-legacy',
          'hiding old-plan warning preserves legacy recovery data')
    page.locator('#planning [data-pl-view=monthly]').click()
    check(page.locator('#planning [data-pl-action=track]').count()==0,
          'monthly page also removes Acompanhar registro')
    check(saved(page) == before, 'public presentation changes preserve saved accounts')

def account_details_copy_case(page):
    ids=seed(page,2)
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option('')
    before=saved(page)
    details=page.locator('#planning .pl-native-account-summary')
    details.locator('summary').click()
    text=details.inner_text()
    check('esforço' not in text.casefold(),
          'expanded All-account details make no promise of the retired effort comparison')
    check('metas de renda' in text and 'perfis' in text,
          'All-account details retain guidance about individual income goals and profiles')
    check(details.locator('[data-pl-focus-account]').count()==2,
          'All-account details retain both explicit account choices')
    check(saved(page)==before,'opening All-account details performs zero financial writes')


def monthly_scope_case(page):
    seed(page,1)
    page.locator('#planning [data-pl-view=monthly]').click()
    check(page.locator('#planning [data-pl-action=track]').count()==0,
          'monthly actions exclude the retired Acompanhar registro control')


def choice_case(page):
    ids = seed(page)
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option('')
    before = saved(page)
    configure(page)
    check(form(page).is_visible(), 'multiple accounts open a choice instead of redirecting')
    check(page.evaluate('JPWPlanning.ui.getView()') == 'start', 'opening choice preserves current public page')
    picker = form(page).locator('[data-pl-configure-account]')
    check(picker.input_value() == '', 'edit choice starts without an account selected')
    check(form(page).locator('[data-pl-action=configure-edit]').is_disabled(), 'edit requires deliberate account selection')
    picker.select_option(ids[1])
    form(page).locator('[data-pl-action=configure-edit]').click()
    check(page.locator('#pl-native-nome').input_value() == 'Conta sintética 2', 'choice opens exactly the chosen account')
    page.locator('#pl-native-nome').evaluate("el=>el.closest('details').open=true")
    page.locator('#pl-native-nome').fill('Rascunho da segunda conta')
    drafts = page.evaluate('JPWPlanning.ui.backupDrafts(false)')
    check(len(drafts) == 1 and drafts[0]['context']['accountId'] == ids[1], 'draft context binds to chosen account')
    close(page)
    page.locator('#planning [data-pl-view=consolidated]').click()
    check(page.locator('#planning [data-pl-account]').input_value() == '', 'cancel does not change Consolidado All filter')
    configure(page)
    form(page).locator('[data-pl-action=configure-create]').click()
    check(page.locator('#pl-native-perfil').input_value() == '' and
          page.locator('#pl-native-nome').input_value() == '', 'create choice opens a fresh unsaved new account')
    close(page)
    check(saved(page) == before, 'choice, edit draft and cancel perform zero financial writes')
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option(ids[1])
    configure(page)
    check(page.locator('#pl-native-nome').input_value() == 'Rascunho da segunda conta', 'explicit selected account reopens its own draft')
    close(page)

def choice_save_case(page):
    ids=seed(page)
    before=page.evaluate('(id)=>JSON.stringify(JPWPlanning.queries.account(id))',ids[0])
    configure(page)
    form(page).locator('[data-pl-configure-account]').select_option(ids[1])
    form(page).locator('[data-pl-action=configure-edit]').click()
    page.locator('#pl-native-nome').evaluate("el=>el.closest('details').open=true")
    page.locator('#pl-native-nome').fill('Segunda conta confirmada')
    form(page).locator('[data-pl-submit]').click()
    check(page.evaluate('(id)=>JPWPlanning.queries.account(id).name',ids[1])=='Conta sintética 2',
          'chosen account review performs zero writes')
    form(page).locator('[data-pl-submit]').click()
    check(page.evaluate('(id)=>JPWPlanning.queries.account(id).name',ids[1])=='Segunda conta confirmada',
          'final confirmation writes exactly the chosen account')
    check(page.evaluate('(id)=>JSON.stringify(JPWPlanning.queries.account(id))',ids[0])==before,
          'confirming the chosen second account preserves the first account byte for byte')
    page.locator('#planning [data-pl-action=native-done]').click()


def stale_choice_case(page):
    ids=seed(page)
    configure(page)
    form(page).locator('[data-pl-configure-account]').select_option(ids[1])
    form(page).locator('[data-pl-action=configure-edit]').click()
    page.locator('#pl-native-nome').evaluate("el=>el.closest('details').open=true")
    page.locator('#pl-native-nome').fill('Rascunho antigo')
    draft=page.evaluate('JPWPlanning.ui.backupDrafts(false)')[0]
    close(page)
    page.evaluate("""id=>{const r=JPWPlanning.commands.execute('updateAccount',
      {accountId:id,config:{name:'Atualização externa sintética'}},JPWPlanning.queries.token(id));
      if(!r.ok)throw Error(JSON.stringify(r));}""",ids[1])
    before=saved(page)
    configure(page)
    form(page).locator('[data-pl-configure-account]').select_option(ids[1])
    form(page).locator('[data-pl-action=configure-edit]').click()
    check(page.evaluate('JPWPlanning.ui.backupDrafts(false)')[0]['baseReference']==draft['baseReference'],
          'reopening an explicit-choice draft preserves its original conflict token')
    check(form(page).locator('[data-pl-submit]').is_disabled() and
          'mudaram' in form(page).locator('[data-pl-draft-stale]').inner_text(),
          'stale chosen-account draft is blocked before it can overwrite a newer saved revision')
    # The approved22/10 explicit review also rejects a synthetic direct submit;
    # disabled presentation alone must never be the write authorization.
    dispatch=form(page).locator('form').evaluate("el=>{const e=new Event('submit',{bubbles:true,cancelable:true});return {accepted:el.dispatchEvent(e),prevented:e.defaultPrevented}}")
    check(dispatch=={'accepted':False,'prevented':True},
          'the real nested form submission handler consumes and rejects the stale submit')
    check(saved(page)==before,'refusing stale draft preserves the new saved account revision')
    form(page).locator('[data-pl-action=draft-refresh]').click()
    check(page.locator('#pl-native-nome').input_value()=='Rascunho antigo',
          'explicit refreshed review preserves typed fields')
    check(saved(page)==before,'refreshing a chosen-account draft never writes financial data')
    form(page).locator('[data-pl-submit]').click()
    check(form(page).locator('[data-pl-native-review]').is_visible() and saved(page)==before,
          'a refreshed chosen-account draft requires new visible review before confirming')
    close(page)


def pending_quote_case(page):
    page.context.route('https://api.frankfurter.dev/v2/rate/USD/BRL',lambda route:route.abort('internetdisconnected'))
    page.wait_for_function('!JPWMarket.usdBrl.isLoading()')
    page.evaluate('localStorage.removeItem(JPWMarket.usdBrl.CACHE_KEY)')
    configure(page)
    page.locator('#pl-native-ano').fill('2026');page.locator('#pl-native-mes').select_option('10')
    page.locator('#pl-native-saldo').fill('1000');page.locator('#pl-native-aporte').fill('100')
    page.locator('#pl-native-openProfiles').click();page.locator('[data-pl-choose-profile=base]').click()
    page.locator('#pl-native-custoValor').fill('250');page.locator('#pl-native-sonhoBRL').fill('500')
    check('Cotação pendente' in page.locator('#pl-native-lifeSummary').inner_text() and
          'Cotação pendente' in page.locator('#pl-native-dreamSummary').inner_text(),
          'unavailable BRL conversion reserves both forecast blocks with explicit quote status')
    check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length')==0,
          'pending quote never creates an account or a false zero forecast')
    close(page)


def forecast_case(page):
    configure(page)
    forecast = page.locator('#pl-native-forecastArea')
    check(forecast.is_visible() and page.locator('#pl-native-lifeSummary').is_visible() and
          page.locator('#pl-native-dreamSummary').is_visible(), 'opening reserves visible space for both forecast milestones')
    check('Preencha' in forecast.inner_text(), 'incomplete answers receive a visible explanation')
    page.locator('#pl-native-ano').fill('2026')
    page.locator('#pl-native-mes').select_option('10')
    page.locator('#pl-native-saldo').fill('1000')
    page.locator('#pl-native-aporte').fill('100')
    page.locator('#pl-native-openProfiles').click()
    page.locator('[data-pl-choose-profile=base]').click()
    page.locator('#pl-native-custoMoeda').select_option('USD')
    page.locator('#pl-native-sonhoMoeda').select_option('USD')
    page.locator('#pl-native-sonhoBRL').fill('100')
    check('opcional' in page.locator('#pl-native-lifeSummary').inner_text(), 'omitted living cost has an explicit optional placeholder')
    page.locator('#pl-native-custoValor').fill('50')
    life, dream = page.locator('#pl-native-lifeSummary').inner_text(),page.locator('#pl-native-dreamSummary').inner_text()
    check('6 meses' in life and 'mar/2027' in life, 'USD1000 plus100 Base cost50 reaches six months March2027')
    check('16 meses' in dream and 'jan/2028' in dream, 'USD1000 plus100 Base dream100 reaches sixteen months January2028')
    geometry = page.evaluate('''()=>{const a=document.querySelector('#pl-native-saldo').getBoundingClientRect(),
      b=document.querySelector('#pl-native-forecastArea').getBoundingClientRect();return {a:{left:a.left,right:a.right},b:{left:b.left,right:b.right},w:innerWidth};}''')
    check(geometry['b']['left'] >= geometry['a']['right'], 'desktop allocates forecast beside original fields')
    page.screenshot(path=str(OUT/'task1-forecast-desktop.png'))
    page.locator('#pl-native-saldo').fill('2000')
    dream = page.locator('#pl-native-dreamSummary').inner_text()
    check('9 meses' in dream and 'jun/2027' in dream, 'changing capital to2000 updates dream to nine months June2027')
    page.locator('#pl-native-sonhoBRL').fill('999999999')
    check('120 meses' in page.locator('#pl-native-dreamSummary').inner_text(), 'unreached objective is explained within the120-month limit')
    check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length') == 0, 'live forecasts create zero accounts before confirmation')
    page.set_viewport_size({'width':390,'height':844})
    jump = page.get_by_role('button',name='Ver sua previsão',exact=True)
    check(jump.is_visible(), 'narrow screen exposes the forecast navigation control')
    jump.click()
    check(forecast.evaluate('el=>el===document.activeElement'), 'forecast navigation moves keyboard focus to its block')
    page.wait_for_function("()=>{const a=document.querySelector('#pl-native-forecastArea').getBoundingClientRect(),b=document.querySelector('#planning dialog.pl-dialog .pl-form-body').getBoundingClientRect();return a.top>=b.top-1&&a.top<=b.top+30}")
    check(forecast.locator('h2').is_visible(), 'forecast navigation scrolls its heading into the form reading area')
    check(form(page).evaluate('el=>el.scrollWidth<=el.clientWidth+1'), 'forecast/form fits390px without horizontal overflow')
    page.screenshot(path=str(OUT/'task1-forecast-mobile.png'))
    page.locator('#pl-native-saldo').focus()
    page.locator('#pl-native-saldo').fill('')
    check(forecast.is_visible() and 'Preencha' in forecast.inner_text(), 'clearing an answer keeps explicit forecast placeholders visible')
    close(page)

def single_case(page):
    ids = seed(page,1)
    configure(page)
    check(page.locator('#pl-native-nome').input_value() == 'Conta sintética 1', 'single active account opens direct edit')
    close(page)
    check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length') == 1, 'opening and canceling single-account form preserve the account')

CASES={'tabs':tabs_case,'public':public_case,'account-details-copy':account_details_copy_case,'monthly-scope':monthly_scope_case,'choice':choice_case,'choice-save':choice_save_case,'stale-choice':stale_choice_case,'pending-quote':pending_quote_case,'forecast':forecast_case,'single':single_case}

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--case',choices=['all',*CASES],default='all')
    parser.add_argument('--receipt',default='task1-current.json')
    parser.add_argument('--out',type=Path)
    parser.add_argument('--ui-source',type=Path,help='Explicit original UI source for a counterproof; source bytes and hash enter receipt')
    args=parser.parse_args()
    receipt_path=Path(args.receipt)
    if args.out:OUT=args.out
    elif receipt_path.is_absolute():OUT=receipt_path.parent/'planning-three-tabs'
    os.chdir(ROOT);OUT.mkdir(parents=True,exist_ok=True)
    server=BrowserFixtureServer(('127.0.0.1',0),Quiet);threading.Thread(target=server.serve_forever,daemon=True).start()
    receipt={'sources':{name:sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES},'cases':[]}
    if args.ui_source:
      receipt['counterproof_ui']={'path':str(args.ui_source),'sha256':sha256(args.ui_source.read_bytes()).hexdigest()}
    try:
      with sync_playwright() as pw:
        browser=pw.chromium.launch(**launch_options())
        for name,journey in CASES.items():
          if args.case not in ['all',name]:continue
          ctx=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
          ctx.add_init_script('window.__onbShown=true;');install_bootstrap(ctx,{'USDBRL':5})
          if args.ui_source:ctx.route('**/src/js/30-accounting/06-planning/03-ui.js',lambda route:route.fulfill(status=200,content_type='text/javascript',body=args.ui_source.read_bytes()))
          errors=[];page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
          result={'case':name,'status':'PRODUCT_FAIL'}
          try:
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html');wait_bootstrap(page)
            page.evaluate("navigateToScreen('planning')");journey(page)
            check(not errors,name+' has no browser errors: '+json.dumps(errors));assert_fixture_requests(ctx)
            result['status']='PASS'
          except AssertionError as e:result['error']=str(e);print('PRODUCT_FAIL '+name+': '+str(e),flush=True)
          except Exception as e:result.update(status='TEST_HARNESS_FAIL',error=str(e),trace=traceback.format_exc());print('TEST_HARNESS_FAIL '+name+': '+str(e),flush=True)
          finally:receipt['cases'].append(result);ctx.close()
        browser.close()
    finally:
      server.shutdown();receipt['status']='PASS' if all(c['status']=='PASS' for c in receipt['cases']) else 'PRODUCT_FAIL'
      receipt_path=receipt_path if receipt_path.is_absolute() else OUT/receipt_path
      receipt_path.parent.mkdir(parents=True,exist_ok=True)
      receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return 0 if receipt['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

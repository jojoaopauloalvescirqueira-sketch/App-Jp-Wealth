#!/usr/bin/env python3
"""Source-grounded Planning parity journeys with disposable synthetic data.

Reference: original Sheet 1Wo1Qwvfd7okSClnCwKateirerP77Z0fWGHmg51wG2EA,
visible tabs re-read on 2026-10-20; Formulario.verified.gs:519 supplies the
native modal. These assertions specify user-observable behavior, not merely
the presence of a new implementation. No owner's browser profile is opened.
"""
import argparse
import json
import os
import re
import threading
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from notes_launcher_test import launch_options

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tools/.artifacts/planning-parity'


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def check(condition, message):
    assert condition, message
    print('PASS ' + message, flush=True)


def start_journey(page):
    selected = page.locator('#planning [role=tab][aria-selected=true]')
    check(selected.inner_text() == 'Comece aqui',
          'Planning opens at the original Comece aqui page')
    tabs = page.locator('#planning [role=tab]').all_text_contents()
    check(tabs == ['Comece aqui', 'Consolidado', 'Preenchimento mensal'],
          'visible tab names and order match the three current visible sheets')
    check(page.locator('#planning').get_by_role('tab').all_text_contents() == ['Comece aqui'],
          'before first confirmation only Comece aqui is exposed, as in the source access gate')
    check(page.get_by_role('button', name=re.compile(r'^Preencher (o )?formulário$')).is_visible(),
          'Comece aqui offers the original Preencher formulário action')
    normalized = ' '.join(page.locator('#planning [data-pl-start]').inner_text().split())
    # Literal copy read from the native Comece aqui cells on 2026-10-20,
    # including updates supplied by the original month/withdrawal scripts.
    for copy in [
        'Planeje a evolução do seu patrimônio em dólares ao longo de 10 anos, combinando capital inicial, aportes mensais e o perfil de risco escolhido.',
        'Configure uma vez. Depois, registre os resultados de cada mês e acompanhe sua evolução.',
        '1 · Monte seu plano',
        'Escolha mês e ano iniciais. Informe capital inicial, aporte mensal, perfil de risco e renda desejada. A previsão patrimonial é calculada automaticamente.',
        '2 · Registre pelos botões',
        'Em Preenchimento mensal, selecione a conta. Registre o resultado total em dólares, os aportes e os saques pelos respectivos botões. Aguarde a confirmação e marque Finalizado = Sim após conferir.',
        '3 · Compare e acompanhe',
        'Consolidado soma as contas ou mostra uma conta selecionada. Referência mantém o plano do formulário de cada conta para comparar o planejado e o realizado.',
        'Aporte: dinheiro que você adiciona; informe dólares e reais pagos.',
        'Saque: dinheiro que você retira; reais recebidos são opcionais.',
        'Resultado: lucro ou prejuízo do mês, sem incluir aportes e saques.',
        'Juros compostos: os resultados reinvestidos também passam a render.',
        'Os valores do plano são em dólares. Projeções são simulações, sem garantia de retorno. Escolha o perfil considerando sua capacidade de suportar perdas.',
        'Nova conta: Adicionar nova conta no Consolidado. Projeções: Stoikus → Editar conta selecionada. Lançamentos: botões de Preenchimento mensal. PDF: Gerar PDF.'
    ]:
        check(copy in normalized, 'Comece aqui preserves native copy: ' + copy[:65])
    check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length') == 0,
          'reading Comece aqui creates no account or financial fact')


def open_form(page):
    page.get_by_role('button', name=re.compile(r'^Preencher (o )?formulário$')).click()
    return page.locator('#planning dialog.pl-dialog').first


def form_journey(page):
    """Native questions, risk chooser, review/back/confirmation and success."""
    before = page.evaluate('''() => {const d=structuredClone(S);
      delete d.patrimonialPlanning;delete d.dataGovernance;return JSON.stringify(d);}''')
    dialog = open_form(page)
    for copy in ['Seu plano', 'Padrão de vida',
                 'Qual renda mensal permitiria o padrão de vida com que você sonha?',
                 'Dados da conta']:
        check(copy in dialog.inner_text(), 'native form preserves question/section: ' + copy)
    labels = ['Ano inicial', 'Mês inicial', 'Capital inicial · US$', 'Aporte mensal · US$',
              'Custo mensal atual · R$', 'Renda mensal desejada · R$']
    for label in labels:
        check(label in dialog.inner_text(), 'native form preserves exact field wording: ' + label)
    check(page.locator('#pl-native-custoMoeda').input_value() == 'BRL' and
          page.locator('#pl-native-sonhoMoeda').input_value() == 'BRL',
          'current cost and desired income default to BRL independently')
    check(page.locator('#pl-native-perfil').input_value() == '',
          'a new native form does not silently choose a risk profile')
    check(not page.locator('#pl-native-substituir').is_visible(),
          'first configuration hides existing-plan replacement options as the source does')
    check(page.locator('#pl-native-mes option').all_text_contents() ==
          ['Selecione', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
           'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
          'initial month options and empty choice match the source form')
    page.locator('#pl-native-openProfiles').click()
    risk = page.locator('#pl-native-profileDialog')
    check(risk.is_visible() and 'Escolha com consciência do risco' in risk.inner_text(),
          'Comparar opens the original risk comparison dialog')
    for name in ['High Risk', 'Base', 'Conservador', 'Segurança']:
        check(name in risk.inner_text(), 'risk comparison includes source profile ' + name)
    check('66,67%' in risk.inner_text(), 'comparison explains asymmetric recovery from a 40% loss')
    page.locator('[data-pl-choose-profile="base"]').click()
    check(not risk.is_visible(), 'choosing a profile returns to the unsaved form')
    check(page.locator('#pl-native-perfil').input_value() == 'base',
          'risk selection updates only the form draft')
    now = page.evaluate('({year:new Date().getFullYear(),month:new Date().getMonth()+1})')
    page.locator('#pl-native-ano').fill(str(now['year']))
    page.locator('#pl-native-mes').select_option(str(now['month']))
    page.locator('#pl-native-saldo').fill('1000')
    page.locator('#pl-native-aporte').fill('100')
    page.locator('#pl-native-custoMoeda').select_option('USD')
    page.locator('#pl-native-custoValor').fill('150')
    page.locator('#pl-native-sonhoMoeda').select_option('USD')
    page.locator('#pl-native-sonhoBRL').fill('300')
    dialog.locator('summary').filter(has_text='Dados da conta').click()
    page.locator('#pl-native-nome').fill('Conta sintética de paridade')
    for label in ['Nome de exibição', 'Corretora', 'Conta / login', 'Servidor']:
        check(label in dialog.inner_text(), 'optional account details preserve wording: ' + label)
    check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length') == 0,
          'choosing a profile and answering native questions writes no plan')
    submit = dialog.locator('[data-pl-submit]')
    check(submit.inner_text() == 'Revisar plano', 'first form action is the source review step')
    submit.click()
    check('Confira antes de salvar' in dialog.inner_text(), 'review is a separate confirmation step')
    check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length') == 0,
          'reviewing the native plan writes no account')
    page.get_by_role('button', name='Voltar e editar', exact=True).click()
    check(page.locator('#pl-native-saldo').input_value() == '1000' and
          page.locator('#pl-native-nome').input_value() == 'Conta sintética de paridade',
          'Voltar e editar preserves the original answers')
    dialog.locator('[data-pl-submit]').click()
    dialog.locator('[data-pl-submit]').click()
    check('Plano liberado' in dialog.inner_text(), 'confirmed save presents the native success state')
    check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length') == 1,
          'only deliberate final confirmation creates exactly one account')
    page.get_by_role('button', name='Ir para o Consolidado', exact=True).click()
    check(page.locator('#planning [role=tab][aria-selected=true]').inner_text() == 'Consolidado',
          'native success explicitly enters Consolidado')
    check(page.locator('#planning').get_by_role('tab').all_text_contents() ==
          ['Comece aqui', 'Consolidado', 'Preenchimento mensal'],
          'first confirmed plan releases the three current visible pages')
    after = page.evaluate('''() => {const d=structuredClone(S);
      delete d.patrimonialPlanning;delete d.dataGovernance;return JSON.stringify(d);}''')
    check(after == before, 'native form affects no adjacent financial family')


def seed(page):
    """Test setup only; all actions under test below use the real DOM."""
    return page.evaluate('''() => {
      const d=new Date(),month=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');
      const a=JPWPlanning,c={name:'Conta sintética de grade',startMonth:month,initialUsd:1000,
        profileId:'base',monthlyContributionUsd:100,goals:{adequate:{value:150,currency:'USD'},ideal:{value:300,currency:'USD'}}};
      const saved=a.commands.execute('createAccount',c,a.queries.token());
      if(!saved.ok)throw Error(JSON.stringify(saved));a.ui.render(true);return {id:saved.accountId,month};
    }''')


def consolidated_journey(page):
    seeded = seed(page)
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option(seeded['id'])
    surface = page.locator('#planning')
    for label in ['Patrimônio confirmado', 'Aportes confirmados', 'Resultado confirmado',
                  'Capital inicial cadastrado', 'Patrimônio projetado', 'Planejado × realizado']:
        check(label in surface.inner_text(), 'Consolidado preserves source information: ' + label)
    for selector, name in [('[data-pl-projection-year]', 'independent projection year'),
                           ('[data-pl-chart-period]', 'chart period'),
                           ('[data-pl-table-mode]', 'annual/monthly table and indicator')]:
        check(surface.locator(selector).count() == 1, 'Consolidado provides source selector: ' + name)
    check(surface.locator('[data-pl-table-mode] option').all_text_contents() ==
          ['Anual · Resumo completo', 'Mensal · Patrimônio', 'Mensal · Aportes do mês',
           'Mensal · Resultado do mês', 'Mensal · Rentabilidade'],
          'annual/monthly and indicator choices match the source combined selector')
    before = page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    year = surface.locator('[data-pl-projection-year]')
    options = year.locator('option').evaluate_all('(nodes)=>nodes.map(n=>n.value)')
    check(len(options) >= 10, 'projection selector covers the complete source horizon')
    year.select_option(options[0])
    selected_year = year.input_value()
    chart = surface.locator('[data-pl-chart-period]')
    chart_options = chart.locator('option').evaluate_all('(nodes)=>nodes.map(n=>n.value)')
    check(len(chart_options) >= 2, 'chart exposes more than one source period')
    chart.select_option(chart_options[-1])
    check(surface.locator('[data-pl-projection-year]').input_value() == selected_year,
          'changing chart period cannot silently change projection year')
    surface.locator('[data-pl-table-mode]').select_option('Mensal · Patrimônio')
    check(surface.locator('[data-pl-consolidated-table] tbody tr').count() == 12,
          'monthly Consolidado puts all twelve month names on the table rows')
    surface.locator('[data-pl-account]').select_option('')
    check('Renda ideal' in surface.inner_text(),
          'Todas as contas with one active account retains its individual income objectives')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())') == before,
          'Consolidado selectors and view changes perform no financial writes')


def monthly_journey(page):
    seeded = seed(page)
    page.locator('#planning [data-pl-view=monthly]').click()
    page.locator('#planning [data-pl-account]').select_option(seeded['id'])
    surface = page.locator('#planning')
    for name in ['Registrar rentabilidade', 'Registrar aporte', 'Registrar saque']:
        check(surface.get_by_role('button', name=name, exact=True).is_visible(),
              'Preenchimento mensal preserves source button ' + name)
    # The approved compact presentation replaces18 simultaneous headers with
    # seven/three principal columns. All source values remain reachable by month.
    from planning_compact_table_test import monthly_geometry, detail_values
    monthly_geometry(page)
    presentation_before = page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    rows = page.evaluate('''({id,month})=>JPWPlanning.queries.sheetView({accountId:id,month,
      quote:JPWMarket.usdBrl.get()}).sheet.monthlyRows''', seeded)
    check(len(rows) == 120, 'compact table retains all120 source months')
    for row in rows:
        detail_values(page, row)
    surface.locator('[data-pl-month]').select_option(seeded['month'])
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())') == presentation_before,
          'every removed source column remains accessible per month without financial writes')
    before = page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    surface.get_by_role('button', name='Registrar rentabilidade', exact=True).click()
    dialog = surface.locator('dialog.pl-dialog').first
    check('Qual é o mês do resultado?' in dialog.inner_text(),
          'result questionnaire begins with the source month question')
    dialog.locator('[data-pl-submit]').click()
    check('TOTAL' in dialog.inner_text() or 'total' in dialog.inner_text(),
          'rentabilidade asks the total month result without deposits or withdrawals')
    check('aportes' in dialog.inner_text().lower() and 'retiradas' in dialog.inner_text().lower(),
          'result instructions exclude the two cash-flow kinds')
    dialog.locator('[data-pl-action=close]').first.click()
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())') == before,
          'canceling a result questionnaire preserves all financial records')


def reference_journey(page):
    seeded = seed(page)
    before = page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    page.evaluate("JPWPlanning.ui.selectView('reference')")
    check(page.evaluate('JPWPlanning.ui.getView()') == 'consolidated',
          'historical reference view call now opens the public Consolidado')
    reference = page.evaluate('(id)=>JPWPlanning.queries.sheetView({accountId:id}).sheet.reference', seeded['id'])
    check(len(reference['rows']) == 120,
          'internal immutable reference retains all120 original plan months')
    for key in ['version','startMonth','endMonth','createdAt','closedAtSave','initialUsd','profileId']:
        check(key in reference, 'internal reference retains source metadata: '+key)
    for key in ['month','rate','contributionUsd','cumulativeContributionUsd','resultUsd','closeUsd']:
        check(key in reference['rows'][0], 'internal reference retains source financial column: '+key)
    check(page.locator('#planning [data-pl-reference]').count() == 0,
          'the hidden native reference sheet has no separate public presentation')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())') == before,
          'internal reference retrieval and old view alias cannot alter the saved plan')


def reset_counts_journey(page):
    """P2: changing reset scope must update every displayed consequence."""
    first = seed(page)
    second = page.evaluate('''({id,month})=>{
      const a=JPWPlanning;
      let saved=a.commands.execute('recordResult',{accountId:id,month,usd:50},a.queries.token(id));
      if(!saved.ok)throw Error(JSON.stringify(saved));
      saved=a.commands.execute('createAccount',{name:'Segunda conta sintética',startMonth:month,
        initialUsd:1000,profileId:'base',monthlyContributionUsd:100,
        goals:{adequate:null,ideal:{value:300,currency:'USD'}}},a.queries.token());
      if(!saved.ok)throw Error(JSON.stringify(saved));
      const other=saved.accountId;
      saved=a.commands.execute('recordContribution',{accountId:other,month,usd:100,brl:500},a.queries.token(other));
      if(!saved.ok)throw Error(JSON.stringify(saved));return other;
    }''', first)
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option(second)
    before = page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    page.locator('#planning [data-pl-action=menu]').click()
    page.locator('#planning [data-pl-action=restart-selected]').click()
    counts = page.locator('#planning [data-pl-reset-counts]')
    check(re.search(r'\b0\s+resultado', counts.inner_text()) is not None and
          re.search(r'\b1\s+aporte', counts.inner_text()) is not None,
          'CONTA reset preview describes only C002 facts')
    page.locator('#planning [name=confirmation]').fill('REINICIAR C002')
    page.locator('#planning [name=resetScope]').select_option('TODAS')
    check(re.search(r'\b1\s+resultado', counts.inner_text()) is not None and
          re.search(r'\b1\s+aporte', counts.inner_text()) is not None,
          'TODAS reset preview refreshes aggregate counts after changing scope')
    targets = page.locator('#planning [data-pl-reset-targets]').inner_text()
    check('Conta sintética de grade' in targets and 'Segunda conta sintética' in targets,
          'TODAS reset preview names both affected synthetic accounts')
    check(page.locator('#planning [name=confirmation]').input_value() == '',
          'changing reset scope cannot reuse a previous confirmation phrase')
    page.keyboard.press('Escape')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())') == before,
          'reviewing and canceling all-account reset leaves every fact unchanged')


def invalidated_stop_draft_journey(page):
    """Changing a stop premise invalidates both live choice and backup draft."""
    dialog = open_form(page)
    page.locator('#pl-native-openProfiles').click()
    page.locator('[data-pl-choose-profile=base]').click()
    now = page.evaluate('({year:new Date().getFullYear(),month:new Date().getMonth()+1})')
    page.locator('#pl-native-ano').fill(str(now['year']))
    page.locator('#pl-native-mes').select_option(str(now['month']))
    page.locator('#pl-native-saldo').fill('1000')
    page.locator('#pl-native-aporte').fill('100')
    page.locator('#pl-native-sonhoMoeda').select_option('USD')
    page.locator('#pl-native-sonhoBRL').fill('300')
    page.locator('#pl-native-stopOpen').click()
    check(page.locator('#pl-native-stopUse').is_enabled(),
          'a valid source form can choose a stop date before saving')
    page.locator('#pl-native-stopUse').click()
    page.locator('#pl-native-aporte').fill('200')
    dialog.locator('[data-pl-action=close]').first.click()
    dialog = open_form(page)
    captured = page.evaluate("jpwWorkspaceCapture().drafts.filter(d=>d.provider==='patrimonial-planning')")
    check(len(captured) == 1, 'edited unsaved native form remains available as one draft')
    fields = json.loads(captured[0]['text'])['fields']
    check('stopAfter' not in fields and 'stopImpactLimit' not in fields,
          'changing a stop premise removes the stale stop choice from backup and reopened draft')
    dialog.locator('[data-pl-submit]').click()
    check('PARADA DOS APORTES' not in dialog.locator('[data-pl-preview]').inner_text(),
          'reopening and reviewing cannot revive a stop calculated before the premise edit')
    check(page.evaluate('JPWPlanning.queries.snapshot().accounts.length') == 0,
          'invalidating and reviewing a stop draft creates no account or financial facts')


def fx_edit_journey(page):
    """Stored conversions stay fixed until each source Câmbio action is used."""
    page.evaluate('JPWMarket.usdBrl.refresh(true)')
    saved = page.evaluate('''()=>{
      const d=new Date(),month=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0'),a=JPWPlanning;
      const result=a.commands.execute('createAccount',{name:'Metas BRL sintéticas',startMonth:month,
        initialUsd:1000,profileId:'base',monthlyContributionUsd:100,
        goals:{adequate:{value:5000,currency:'BRL'},ideal:{value:10000,currency:'BRL'}}},a.queries.token());
      if(!result.ok)throw Error(JSON.stringify(result));return {id:result.accountId,account:a.queries.account(result.accountId)};
    }''')
    check(saved['account']['plan']['goals']['ideal']['usd'] == 2000 and
          saved['account']['plan']['goals']['adequate']['usd'] == 1000,
          'synthetic BRL objectives initially capture the independent USD/BRL 5 quote')
    day = page.evaluate('new Date().toISOString().slice(0,10)')
    page.context.route('https://api.frankfurter.dev/v2/rate/USD/BRL', lambda route:
                       route.fulfill(status=200, content_type='application/json',
                                     body=json.dumps({'date': day, 'base': 'USD', 'quote': 'BRL', 'rate': 10})))
    page.evaluate('JPWMarket.usdBrl.refresh(true)')
    page.evaluate('JPWPlanning.ui.render(true)')
    check(page.evaluate('JPWMarket.usdBrl.get().rate') == 10,
          'the public quote may move without changing saved goal conversions')
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option(saved['id'])
    before = page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')

    def edit():
        page.locator('#planning [data-pl-action=menu]').click()
        page.locator('#planning [data-pl-action=edit-selected]:visible').first.click()
        return page.locator('#planning dialog.pl-dialog')

    dialog = edit()
    check('2.000,00' in page.locator('#pl-native-sonhoUsd').inner_text() and
          '1.000,00' in page.locator('#pl-native-costUsd').inner_text(),
          'opening an existing form keeps both captured conversions despite a newer public quote')
    quote_text = ' '.join(page.locator('#pl-native-sonhoFxInfo').text_content().split())
    check(re.search(r'R\$\s*5(?:\D|$)', quote_text) is not None,
          'the income quote explanation describes its captured rate, not the newer public rate')
    page.locator('#pl-native-refreshSonhoFx').click()
    page.wait_for_function("document.querySelector('#pl-native-sonhoUsd').textContent.includes('1.000,00')")
    check('1.000,00' in page.locator('#pl-native-costUsd').inner_text(),
          'refreshing desired income does not refresh current living cost')
    check('33.333,34' in page.locator('#pl-native-metaPrevista').inner_text(),
          'explicit income refresh recalculates required capital from USD1000 divided by 3 percent')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())') == before,
          'explicit quote refresh changes the draft only')
    dialog.locator('[data-pl-submit]').click()
    check('1.000,00' in dialog.locator('[data-pl-preview]').inner_text() and
          '33.333,34' in dialog.locator('[data-pl-preview]').inner_text(),
          'review uses the explicitly refreshed income conversion and its new required capital')
    page.keyboard.press('Escape')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())') == before,
          'canceling the refreshed BRL review leaves saved goals unchanged')
    dialog = edit()
    page.locator('#pl-native-refreshSonhoFx').click()
    page.wait_for_function("document.querySelector('#pl-native-sonhoUsd').textContent.includes('1.000,00')")
    dialog.locator('[data-pl-submit]').click()
    dialog.locator('[data-pl-submit]').click()
    page.locator('#planning [data-pl-action=native-done]').click()
    after = page.evaluate('(id)=>JPWPlanning.queries.account(id)', saved['id'])
    check(after['plan']['goals']['ideal']['value'] == 10000 and
          after['plan']['goals']['ideal']['usd'] == 1000 and
          after['plan']['goals']['ideal']['quote']['rate'] == 10,
          'explicit final save reprices the unchanged nominal BRL income amount exactly once')
    check(after['plan']['goals']['adequate'] == saved['account']['plan']['goals']['adequate'],
          'saving an income-only refresh preserves the other goal and its original quote byte for byte')
    check(after['plan']['reference'] == saved['account']['plan']['reference'],
          'refreshing a current income objective preserves the initial reference')


def pdf_scope_journey(page):
    first = seed(page)
    second = page.evaluate('''({month})=>{
      const a=JPWPlanning,result=a.commands.execute('createAccount',{name:'Conta B sintética',startMonth:month,
        initialUsd:2000,profileId:'base',monthlyContributionUsd:100,
        goals:{adequate:null,ideal:{value:300,currency:'USD'}}},a.queries.token());
      if(!result.ok)throw Error(JSON.stringify(result));return result.accountId;
    }''', first)
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option('')
    page.locator('#planning [data-pl-view=monthly]').click()
    page.locator('#planning [data-pl-account]').select_option(second)
    before = page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())')
    page.evaluate('() => {window.__parityPrints=0;window.print=()=>{window.__parityPrints++}}')
    page.locator('#planning [data-pl-action=print]:visible').first.click()
    report = page.locator('#planning [data-pl-report]')
    check('Todas as contas' in report.locator('header').text_content() and
          '3.000,00' in report.text_content(),
          'PDF generated from Monthly B retains the master Consolidado All scope')
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option(first['id'])
    page.locator('#planning [data-pl-view=monthly]').click()
    page.locator('#planning [data-pl-account]').select_option(second)
    page.locator('#planning [data-pl-action=print]:visible').first.click()
    report = page.locator('#planning [data-pl-report]')
    check('Conta sintética de grade' in report.locator('header').text_content() and
          'Conta B sintética' not in report.locator('header').text_content(),
          'PDF generated from Monthly B retains master account A when A is selected in Consolidado')
    check(page.evaluate('window.__parityPrints') == 2,
          'each deliberate PDF action invokes the print boundary once')
    check(page.evaluate('JSON.stringify(JPWPlanning.queries.snapshot())') == before,
          'report generation and independent view selection perform no financial writes')


def main():
    global OUT
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=['start', 'form', 'consolidated', 'monthly', 'reference', 'reset-counts', 'stop-draft', 'fx-edit', 'pdf-scope', 'all'], default='all')
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args()
    OUT = args.out
    os.chdir(ROOT)
    OUT.mkdir(parents=True, exist_ok=True)
    server = BrowserFixtureServer(('127.0.0.1', 0), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    receipt = {'case': args.case, 'status': 'PRODUCT_FAIL', 'candidate': {}}
    for relative in ['src/js/30-accounting/06-planning/03-ui.js',
                     'src/js/30-accounting/06-planning/01-engine.js',
                     'src/js/30-accounting/06-planning/02-state.js', 'build-id.js']:
        receipt['candidate'][relative] = sha256((ROOT / relative).read_bytes()).hexdigest()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch_options())
            cases = {'start': start_journey, 'form': form_journey,
                     'consolidated': consolidated_journey, 'monthly': monthly_journey,
                     'reference': reference_journey, 'reset-counts': reset_counts_journey,
                     'stop-draft': invalidated_stop_draft_journey, 'fx-edit': fx_edit_journey,
                     'pdf-scope': pdf_scope_journey}
            for case, journey in cases.items():
                if args.case not in ['all', case]:
                    continue
                context = browser.new_context(viewport={'width': 1440, 'height': 1000},
                                              service_workers='block')
                context.add_init_script('window.__onbShown=true;')
                install_bootstrap(context, {'USDBRL': 5})
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
                wait_bootstrap(page)
                page.evaluate("navigateToScreen('planning')")
                journey(page)
                check(not errors, case + ' parity journey has no page errors: ' + json.dumps(errors))
                assert_fixture_requests(context)
                context.close()
            browser.close()
        receipt['status'] = 'PASS'
    except Exception as error:
        receipt['error'] = str(error)
        raise
    finally:
        (OUT / 'parity-current.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
        server.shutdown()


if __name__ == '__main__':
    main()

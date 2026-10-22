#!/usr/bin/env python3
"""Approved Planning geometry and five permanent visual regressions.

Oracles: docs/superpowers/plans/2026-10-21-planning-proportions.md.
Uses fresh synthetic Chromium contexts; never an operator browser profile.
--case regressions preserves independent RED evidence before the product fix.
Default execution includes the complete layout/theme/viewport and native zoom
matrix, stateful confirmation journey, and financial milestone characterization.
"""
import argparse
import base64
from datetime import datetime, timezone
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler
import json
import math
from pathlib import Path
import shutil
import tempfile
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from browser_fixture_server import BrowserFixtureServer
from notes_launcher_test import launch_options
from planning_parity_layout_test import financial, table_geometry, tab_word_geometry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.superpowers/sdd/planning-proportions-20261021/default'
LAYOUTS = ['sidebar', 'topbar', 'glass', 'submenu']
THEMES = ['light', 'dark']
OVERRIDES = {}
SIZES = [(320, 700), (390, 844), (700, 600), (701, 601),
         (1099, 720), (1100, 719), (1100, 720), (1101, 721),
         (1440, 1000), (1440, 480)]
SOURCES = [
    'assets/jp-wealth-brand-red.png',
    'assets/jp-wealth-logo.png',
    'assets/nocuda-metatrader.png',
    'assets/nocuda-tradingview.png',
    'assets/pwa-icon-primary-512.png',
    'build-id.js',
    'docs/normative/ANEXO_PARAMETRICO_CANONICO.md',
    'docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf',
    'downloads/nocuda/MT5-LEIA-ME.md',
    'downloads/nocuda/Nocuda_Tool.ex5',
    'downloads/nocuda/Nocuda_Tool.mq5',
    'downloads/nocuda/Nocuda_Tool.pine',
    'downloads/nocuda/TRADINGVIEW-LEIA-ME.md',
    'index.html',
    'manifests/jp-wealth.webmanifest',
    'src/js/00-core/00-forex-policy.js',
    'src/js/00-core/01-risk-profiles.js',
    'src/js/00-core/02-platforms.js',
    'src/js/00-core/03-default-state.js',
    'src/js/00-core/04-persistence.js',
    'src/js/00-core/05-helpers.js',
    'src/js/00-core/06-storage-fs.js',
    'src/js/00-core/07-workspace-backup.js',
    'src/js/00-core/08-module-availability.js',
    'src/js/00-core/09-evidence-archive.js',
    'src/js/00-core/09-learning-progress.js',
    'src/js/00-core/10-download-assets.js',
    'src/js/10-domain/00-forex-engine.js',
    'src/js/10-domain/00-forex-state.js',
    'src/js/10-domain/01-risk-instruments.js',
    'src/js/10-domain/02-risk-calculations.js',
    'src/js/10-domain/03-phase-transitions.js',
    'src/js/10-domain/04-stop-statistics.js',
    'src/js/10-domain/05-brokers-prop-firms.js',
    'src/js/10-domain/06-quarantine.js',
    'src/js/10-domain/07-reserve-requirements.js',
    'src/js/10-domain/08-usd-brl-quote.js',
    'src/js/10-domain/09-nocoda-geometry.js',
    'src/js/10-domain/10-pivot-studies.js',
    'src/js/10-domain/11-operation-lifecycle.js',
    'src/js/10-domain/12-personal-finance.js',
    'src/js/10-domain/13-alladin.js',
    'src/js/10-domain/16-nocuda-transfer.js',
    'src/js/10-domain/17-fx-consolidated-model.js',
    'src/js/10-domain/18-execution-board-model.js',
    'src/js/10-domain/19-execution-market.js',
    'src/js/20-ui/01-header-readout.js',
    'src/js/20-ui/02-sidebar.js',
    'src/js/20-ui/03-main-render.js',
    'src/js/20-ui/04-operational-clearance.js',
    'src/js/20-ui/05-execution-clearance.js',
    'src/js/20-ui/06-chart-terminal-chrome.js',
    'src/js/20-ui/07-chart-crosshair-tooltip.js',
    'src/js/20-ui/08-input-bindings.js',
    'src/js/20-ui/08-scenario-fan.js',
    'src/js/20-ui/09-contextual-help.js',
    'src/js/20-ui/10-font-scale.js',
    'src/js/20-ui/11-phase-posture.js',
    'src/js/20-ui/12-nav-style.js',
    'src/js/20-ui/13-exec-views.js',
    'src/js/20-ui/14-nocoda-studies.js',
    'src/js/20-ui/15-pivot-studies.js',
    'src/js/20-ui/16-operation-history.js',
    'src/js/20-ui/17-finpes-views.js',
    'src/js/20-ui/18-finpes-budget.js',
    'src/js/20-ui/19-finpes-debts.js',
    'src/js/20-ui/20-finpes-comparison.js',
    'src/js/20-ui/21-finpes-scenarios.js',
    'src/js/20-ui/22-finpes-overview.js',
    'src/js/20-ui/23-research-views.js',
    'src/js/20-ui/24-alladin-views.js',
    'src/js/20-ui/25-dash-macro.js',
    'src/js/20-ui/26-forex-engine-views.js',
    'src/js/20-ui/28-fx-consolidated.js',
    'src/js/20-ui/30-execution-board.js',
    'src/js/20-ui/31-forex-accounts.js',
    'src/js/20-ui/31-tools-services.js',
    'src/js/20-ui/32-module-availability.js',
    'src/js/20-ui/33-module-work.js',
    'src/js/20-ui/34-normative-reader.js',
    'src/js/30-accounting/01-daily-ledger.js',
    'src/js/30-accounting/02-accounting-engine.js',
    'src/js/30-accounting/03-mei-jp.js',
    'src/js/30-accounting/04-patrimonial-simulation.js',
    'src/js/30-accounting/06-planning/01-engine.js',
    'src/js/30-accounting/06-planning/02-state.js',
    'src/js/30-accounting/06-planning/03-ui.js',
    'src/js/40-app/01-navigation.js',
    'src/js/40-app/02-reset.js',
    'src/js/40-app/03-theme.js',
    'src/js/40-app/04-onboarding.js',
    'src/js/40-app/05-wipe-all.js',
    'src/js/40-app/06-app-icons.js',
    'src/js/40-app/06-boot.js',
    'src/js/40-app/07-finalize-session.js',
    'src/js/40-app/08-educational-content.js',
    'src/js/40-app/09-profile-avatar-catalog.js',
    'src/js/40-app/09-settings-modal.js',
    'src/js/40-app/10-dashboard-immersive.js',
    'src/js/40-app/11-operational-shell.js',
    'src/js/40-app/12-global-dashboard.js',
    'src/js/40-app/13-dashboard-layout.js',
    'src/js/40-app/14-mvp-notes.js',
    'src/js/40-app/15-ff-news.js',
    'src/js/40-app/16-storage-governance.js',
    'src/js/40-app/17-economic-calendar.js',
    'src/js/40-app/18-galton-board/01-config.js',
    'src/js/40-app/18-galton-board/02-rng.js',
    'src/js/40-app/18-galton-board/03-statistics.js',
    'src/js/40-app/18-galton-board/04-physics.js',
    'src/js/40-app/18-galton-board/05-renderer.js',
    'src/js/40-app/18-galton-board/06-controller.js',
    'src/js/40-app/18-notification-center.js',
    'src/js/40-app/24-fx-consolidated-import.js',
    'src/js/40-app/25-fx-consolidated-pdf.js',
    'src/js/40-app/26-learning-catalog.js',
    'src/js/40-app/27-learning-view.js',
    'src/js/40-app/28-learning-guide.js',
    'src/js/40-app/29-time-twins/01-simulation.js',
    'src/js/40-app/29-time-twins/02-missions.js',
    'src/js/40-app/29-time-twins/03-progress.js',
    'src/js/40-app/29-time-twins/04-view.js',
    'src/js/40-app/29-time-twins/05-controller.js',
    'src/js/40-app/30-capital-currents/01-engine.js',
    'src/js/40-app/30-capital-currents/02-scenarios.js',
    'src/js/40-app/30-capital-currents/03-progress.js',
    'src/js/40-app/30-capital-currents/04-field-renderer.js',
    'src/js/40-app/30-capital-currents/04-view.js',
    'src/js/40-app/30-capital-currents/05-controller.js',
    'src/js/40-app/31-market-hours/01-sessions.js',
    'src/js/40-app/31-market-hours/02-assets.js',
    'src/js/40-app/31-market-hours/03-view.js',
    'src/js/40-app/31-market-hours/04-controller.js',
    'src/js/manifest.json',
    'src/styles/app.css',
    'src/vendor/fflate/fflate-0.8.2.min.js',
    'src/vendor/planck/planck-1.5.0.min.js',
    'tools/browser_bootstrap_fixture.py',
    'tools/browser_fixture_server.py',
    'tools/notes_launcher_test.py',
    'tools/planning_parity_layout_test.py',
    'tools/planning_proportions_test.py',
]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def now():
    return datetime.now(timezone.utc).isoformat()


def hashes():
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}


def settle(page):
    page.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')


def setup(context, url):
    context.add_init_script('window.__onbShown=true;')
    install_bootstrap(context, {'USDBRL': 5})
    for name, source in OVERRIDES.items():
        context.route('**/' + name + '*', lambda route, request, source=source:
                      route.fulfill(status=200, body=source.read_bytes(),
                                    content_type='text/css' if source.suffix == '.css' else 'application/javascript'))
    page = context.pages[0] if context.pages else context.new_page()
    page.set_default_timeout(15000)
    page.goto(url)
    wait_bootstrap(page)
    page.evaluate("navigateToScreen('planning')")
    return page


def open_form(page):
    page.locator('#planning [data-pl-view=start]').click()
    page.locator('#planning [data-pl-action=configure]').click()
    if page.locator('#planning [data-pl-action=configure-create]').is_visible():
        page.locator('#planning [data-pl-action=configure-create]').click()
    page.locator('#pl-native-ano').wait_for(state='visible')
    settle(page)


def rect(page, selector):
    return page.locator(selector).evaluate('''el=>{const r=el.getBoundingClientRect();
      return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};}''')


def dialog_geometry(page, selector, maximum):
    box = rect(page, selector)
    width, height = page.evaluate('[innerWidth,innerHeight]')
    gutter = 12 if width <= 700 or height <= 600 else 24
    assert abs((box['left'] + box['right']) / 2 - width / 2) <= 2, ('horizontal center', box, width)
    assert abs((box['top'] + box['bottom']) / 2 - height / 2) <= 2, ('vertical center', box, height)
    assert box['width'] <= maximum + 1, ('approved dialog maximum', box, maximum)
    assert box['left'] >= gutter - 1 and box['right'] <= width - gutter + 1, ('horizontal gutter', box, gutter)
    assert box['top'] >= gutter - 1 and box['bottom'] <= height - gutter + 1, ('vertical gutter', box, gutter)
    return box


def header_geometry(page, selector):
    dialog = page.locator(selector)
    header = dialog.locator('header').first
    values = header.evaluate('''el=>{const rect=n=>{const r=n.getBoundingClientRect();return {
      left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
      return {header:rect(el),title:rect(el.querySelector('h2')),
        close:rect(el.querySelector('.pl-close,.risk-close'))};}''')
    h, title, close = (values[key] for key in ['header', 'title', 'close'])
    assert abs(close['width'] - 44) <= 1 and abs(close['height'] - 44) <= 1, ('44px close', values)
    assert close['left'] >= title['right'] - 1, ('close stays to the right of the complete title', values)
    assert close['top'] < title['bottom'] and close['bottom'] > title['top'], ('close shares title row', values)
    assert title['left'] >= h['left'] and close['right'] <= h['right'], ('header contents contained', values)
    assert header.locator('h2').evaluate('el=>el.scrollWidth<=el.clientWidth+1'), ('complete header title', values)
    return values


def aligned_money(page):
    result = []
    for currency, value in [('custoMoeda', 'custoValor'), ('sonhoMoeda', 'sonhoBRL')]:
        a, b = rect(page, '#pl-native-' + currency), rect(page, '#pl-native-' + value)
        result.append({'currency': a, 'value': b})
        assert abs(a['bottom'] - b['bottom']) <= 2, ('currency/value bases within 2px', result)
    return result


def pending_copy(page):
    result = page.locator('#planning .milestone').evaluate_all('''els=>els.map(el=>{
      const duration=el.querySelector('.duration'),detail=el.querySelector('.detail');
      return {text:el.innerText,duration:duration?.innerText||'',detail:detail?.innerText||'',
        size:duration?parseFloat(getComputedStyle(duration).fontSize):0};})''')
    assert len(result) == 2, ('both milestones remain available', result)
    for item in result:
        assert not (item['duration'] and item['duration'] == item['detail']), ('pending instruction occurs once', item)
        assert not item['duration'] or item['size'] <= 14, ('large result typography only for calculated numbers', item)
        assert item['detail'] and len(item['text']) < 550, ('readable pending guidance', item)
    return result


def legend_geometry(page):
    result = page.locator('#pl-native-stopLegend i').evaluate_all('''els=>els.map(el=>{
      const r=el.getBoundingClientRect(),s=getComputedStyle(el);return {width:r.width,height:r.height,
        color:s.borderTopColor,style:s.borderTopStyle,border:parseFloat(s.borderTopWidth)};})''')
    paths = page.locator('#pl-native-stopChart polyline').evaluate_all('''els=>els.map(el=>{
      const s=getComputedStyle(el);return {color:s.stroke,dash:s.strokeDasharray};})''')
    assert len(result) == len(paths) == 2, ('two real legend samples and plotted lines', result, paths)
    for sample, path in zip(result, paths):
        assert sample['width'] >= 18 and sample['border'] >= 1, ('visible legend sample', result)
        assert sample['color'] == path['color'], ('legend matches real line color', result, paths)
        assert sample['style'] in ['dashed', 'dotted'] and path['dash'] != 'none', ('legend matches dashed line', result, paths)
    return {'samples': result, 'lines': paths}


def execute(report, case_id, action, page=None, out=None):
    case = {'id': case_id, 'classification': 'NOT_RUN', 'started_at': now()}
    report['cases'].append(case)
    try:
        case['evidence'] = action()
        case['classification'] = 'PASS'
    except AssertionError as error:
        case.update(classification='PRODUCT_FAIL', error=str(error), trace=traceback.format_exc())
    except Exception as error:
        case.update(classification='TEST_HARNESS_FAIL', error=str(error), trace=traceback.format_exc())
    case['finished_at'] = now()
    if page and out and (case['classification'] != 'PASS' or case_id.startswith('bug-')):
        cdp = page.context.new_cdp_session(page)
        (out / (case_id + '.png')).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot', {
            'format': 'png', 'fromSurface': True, 'captureBeyondViewport': False})['data']))
        cdp.detach()
    print(case['classification'] + ' ' + case_id, flush=True)


def regressions(browser, url, report, out):
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block')
    try:
        page = setup(context, url)
        before = financial(page)
        open_form(page)
        execute(report, 'bug-dialog-center', lambda: dialog_geometry(page, '#planning .pl-dialog', 1120), page, out)
        execute(report, 'bug-money-bases', lambda: aligned_money(page), page, out)
        page.set_viewport_size({'width': 320, 'height': 700});settle(page)
        page.locator('#pl-native-openProfiles').click()
        execute(report, 'bug-mobile-header', lambda: header_geometry(page, '#pl-native-profileDialog'), page, out)
        page.keyboard.press('Escape')
        execute(report, 'bug-pending-copy', lambda: pending_copy(page), page, out)
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.locator('#pl-native-stopOpen').click()
        execute(report, 'bug-stop-legend', lambda: legend_geometry(page), page, out)
        assert financial(page) == before, 'five regression inspections wrote financial data'
        assert_fixture_requests(context)
    finally:
        context.close()


def fill_plan(page, capital='1000'):
    for selector, value in [('ano', '2026'), ('saldo', capital), ('aporte', '100'),
                            ('custoValor', '50'), ('sonhoBRL', '100')]:
        page.locator('#pl-native-' + selector).fill(value)
    page.locator('#pl-native-mes').select_option('10')
    page.locator('#pl-native-custoMoeda').select_option('USD')
    page.locator('#pl-native-sonhoMoeda').select_option('USD')
    page.locator('#pl-native-openProfiles').click()
    page.locator('[data-pl-choose-profile=base]').click()


def geometry_journey(page, width, height):
    before = financial(page)
    open_form(page)
    maximum = 1120 if width >= 1100 and height >= 720 else 720
    result = {'viewport': [width, height], 'form': dialog_geometry(page, '#planning .pl-dialog', maximum),
              'header': header_geometry(page, '#planning .pl-dialog'), 'money': aligned_money(page)}
    columns = page.locator('[data-pl-native-fields]').evaluate('el=>getComputedStyle(el).gridTemplateColumns')
    jump = page.locator('.pl-forecast-jump').is_visible()
    assert jump == (maximum == 720), ('forecast jump follows approved 1100x720 boundary', width, height, jump)
    assert (len(columns.split()) == 2) == (maximum == 1120), ('approved two column boundary', columns, width, height)
    # All questions remain inside the scroll body; scrolling cannot hide actions.
    body = page.locator('#planning .pl-form-body')
    body.evaluate('el=>el.scrollTop=el.scrollHeight')
    assert body.evaluate('el=>el.scrollWidth<=el.clientWidth+1'), 'form body has horizontal clipping'
    footer = rect(page, '#planning .pl-form>footer')
    assert footer['bottom'] <= result['form']['bottom'] + 1, ('footer outside dialog', footer)
    page.locator('#pl-native-openProfiles').click()
    result['profiles'] = dialog_geometry(page, '#pl-native-profileDialog', 800)
    header_geometry(page, '#pl-native-profileDialog')
    page.keyboard.press('Escape')
    assert page.locator('#pl-native-openProfiles').evaluate('el=>document.activeElement===el'), 'profile focus return'
    page.locator('#pl-native-stopOpen').click()
    result['stop'] = dialog_geometry(page, '#pl-native-stopDialog', 800)
    header_geometry(page, '#pl-native-stopDialog')
    legend_geometry(page)
    page.keyboard.press('Escape')
    assert page.locator('#pl-native-stopOpen').evaluate('el=>document.activeElement===el'), 'stop focus return'
    page.keyboard.press('Escape')
    assert page.locator('#planning dialog:visible').count() == 0, 'Escape keeps an unintended dialog open'
    assert financial(page) == before, 'layout inspection writes financial data'
    return result


def state_journey(page, out):
    before = financial(page)
    open_form(page)
    # Required field errors, pending quote and BRL remain distinct from a result.
    page.locator('#planning .pl-form [data-pl-submit]').click()
    assert not page.locator('[data-pl-native-review]').is_visible(), 'empty form skips validation'
    fill_plan(page)
    life = page.locator('#pl-native-lifeSummary').inner_text()
    dream = page.locator('#pl-native-dreamSummary').inner_text()
    assert 'mar/2027' in life and 'jan/2028' in dream, ('approved unchanged milestones', life, dream)
    page.locator('#pl-native-saldo').fill('2000')
    assert 'jun/2027' in page.locator('#pl-native-dreamSummary').inner_text(), 'capital 2000 expected June 2027'
    page.locator('#pl-native-saldo').fill('1000')
    page.locator('#pl-native-custoMoeda').select_option('BRL')
    page.locator('#pl-native-sonhoMoeda').select_option('BRL')
    assert 'R$' in page.locator('#pl-native-custoValueLabel').inner_text(), 'BRL label'
    page.locator('#pl-native-custoMoeda').select_option('USD')
    page.locator('#pl-native-sonhoMoeda').select_option('USD')
    page.locator('#pl-native-stopOpen').click()
    stop = page.locator('#pl-native-stopMonth').input_value()
    label = page.evaluate('month=>new Date(month+"-01T12:00:00").toLocaleDateString("pt-BR",{month:"short",year:"numeric"})', stop)
    assert stop and label.replace('.', '')[:3] in page.locator('.stop-footer').inner_text(), 'stop footer identifies the calculated month'
    page.locator('#pl-native-stopClose').click()
    page.locator('#planning .pl-form [data-pl-submit]').click()
    assert page.locator('[data-pl-native-review]').is_visible(), 'review not visible'
    dialog_geometry(page, '#planning .pl-dialog', 720)
    assert financial(page) == before, 'review creates financial writes'
    page.screenshot(path=str(out / 'review-desktop.png'))
    page.locator('[data-pl-action=native-back]').click()
    page.locator('#planning .pl-form>footer [data-pl-action=close]').click()
    assert financial(page) == before, 'cancel creates financial writes'
    open_form(page)
    assert page.locator('#pl-native-saldo').input_value() == '1000', 'cancel loses session draft'
    page.locator('#planning .pl-form [data-pl-submit]').click()
    page.locator('#planning .pl-form [data-pl-submit]').click()
    assert page.locator('[data-pl-native-success]').is_visible(), 'confirmation has no success state'
    dialog_geometry(page, '#planning .pl-dialog', 720)
    page.locator('[data-pl-action=native-done]').click()
    created = page.evaluate('JPWPlanning.queries.snapshot().accounts[0].id')
    # A synthetic setup command creates a second account solely to inspect choice.
    page.evaluate('''()=>{const a=JPWPlanning.queries.snapshot().accounts[0],p=a.plan;
      const r=JPWPlanning.commands.execute('createAccount',{name:'Segunda conta sintética',
      startMonth:p.startMonth,initialUsd:1000,profileId:'base',monthlyContributionUsd:100,
      goals:{adequate:{value:50,currency:'USD'},ideal:{value:100,currency:'USD'}}},JPWPlanning.queries.token());
      if(!r.ok)throw Error(JSON.stringify(r));JPWPlanning.ui.render(true);}''')
    before = financial(page)
    for view in ['start', 'consolidated', 'monthly']:
        page.locator('[data-pl-view=' + view + ']').click()
        table_geometry(page);tab_word_geometry(page)
    page.locator('[data-pl-view=consolidated]').click()
    page.locator('[data-pl-account]').select_option('')
    page.locator('[data-pl-view=start]').click()
    page.locator('[data-pl-action=configure]').click()
    dialog_geometry(page, '#planning .pl-dialog', 720)
    assert not page.locator('[data-pl-configure-account]').input_value(), 'multiple accounts selected implicitly'
    page.locator('[data-pl-configure-account]').select_option(created)
    page.locator('[data-pl-action=configure-edit]').click()
    assert page.locator('#pl-native-saldo').input_value() == '1000', 'edit loads wrong account'
    page.locator('#pl-native-saldo').fill('2000')
    page.locator('#planning .pl-form [data-pl-submit]').click()
    dialog_geometry(page, '#planning .pl-dialog', 720)
    page.locator('#planning .pl-form>footer [data-pl-action=close]').click()
    assert financial(page) == before, 'editing, review, navigation or cancel wrote data'
    return {'milestones': ['mar/2027', 'jan/2028', 'jun/2027'], 'accounts': 2,
            'creation': 'explicit confirmation only', 'edit_and_navigation': 'zero financial writes'}


def matrix(browser, url, report, out):
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block', reduced_motion='reduce')
    try:
        page = setup(context, url)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        for width, height in SIZES:
            page.set_viewport_size({'width': width, 'height': height})
            for layout in LAYOUTS:
                for theme in THEMES:
                    page.evaluate('layout=>mountNavigationLayout(layout)', layout)
                    page.evaluate('theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
                    execute(report, f'matrix-{layout}-{theme}-{width}x{height}',
                            lambda: geometry_journey(page, width, height), page, out)
                    if page.locator('#planning dialog:visible').count():
                        page.keyboard.press('Escape');page.keyboard.press('Escape')
        page.set_viewport_size({'width': 1440, 'height': 1000})
        execute(report, 'journey-confirmation-and-milestones', lambda: state_journey(page, out), page, out)
        assert not errors, errors
        assert_fixture_requests(context)
    finally:
        context.close()


def native_zoom(pw, url, report, out):
    profile = Path(tempfile.mkdtemp(prefix='planning-proportions-native200-', dir=out))
    (profile / 'Default').mkdir()
    (profile / 'Default/Preferences').write_text(json.dumps({'partition': {
        'default_zoom_level': {'x': math.log(2) / math.log(1.2)}}}))
    options = launch_options();options.update(headless=False, no_viewport=True,
        args=['--window-size=1440,1000'], service_workers='block', reduced_motion='reduce')
    try:
        context = pw.chromium.launch_persistent_context(str(profile), **options)
        try:
            page = setup(context, url)
            zoom = page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
            if abs(zoom['outer'] / zoom['inner'] - 2) >= .01 or zoom['css'] != '1':
                raise RuntimeError('Native zoom unavailable: ' + str(zoom))
            report['native_zoom'] = zoom
            for layout in LAYOUTS:
                for theme in THEMES:
                    page.evaluate('layout=>mountNavigationLayout(layout)', layout)
                    page.evaluate('theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
                    width, height = page.evaluate('[innerWidth,innerHeight]')
                    execute(report, f'native200-{layout}-{theme}', lambda: geometry_journey(page, width, height), page, out)
                    if page.locator('#planning dialog:visible').count():
                        page.keyboard.press('Escape');page.keyboard.press('Escape')
            assert_fixture_requests(context)
        finally:
            context.close()
    finally:
        shutil.rmtree(profile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--case', choices=['all', 'regressions'], default='all')
    parser.add_argument('--ui-source', type=Path, help='Explicit synthetic counterproof source; never changes product files')
    parser.add_argument('--css-source', type=Path, help='Explicit synthetic counterproof CSS; never changes product files')
    args = parser.parse_args()
    if args.ui_source:
        OVERRIDES['src/js/30-accounting/06-planning/03-ui.js'] = args.ui_source
    if args.css_source:
        OVERRIDES['src/styles/app.css'] = args.css_source
    args.out.mkdir(parents=True, exist_ok=True)
    report = {'classification': 'NOT_RUN', 'started_at': now(), 'source_sha256': hashes(),
              'test_sha256': sha256(Path(__file__).read_bytes()).hexdigest(), 'cases': [],
              'matrix': {'layouts': LAYOUTS, 'themes': THEMES, 'sizes': SIZES, 'native_zoom': 200},
              'limits': {'human_acceptance': 'NOT_RUN', 'Safari': 'NOT_RUN', 'screen_reader': 'NOT_RUN', 'physical_touch': 'NOT_RUN'}}
    if OVERRIDES:
        report['counterproof_sources'] = {name: {'path': str(source), 'sha256': sha256(source.read_bytes()).hexdigest()}
                                          for name, source in OVERRIDES.items()}
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/index.html'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            report['browser'] = browser.version
            regressions(browser, url, report, args.out)
            if args.case == 'all':
                matrix(browser, url, report, args.out)
            browser.close()
            if args.case == 'all':
                native_zoom(pw, url, report, args.out)
        expected = 5 if args.case == 'regressions' else 94
        assert len(report['cases']) == expected, ('missing mandatory cases', len(report['cases']), expected)
        assert len({case['id'] for case in report['cases']}) == expected, 'duplicate case identity'
        failed = [case for case in report['cases'] if case['classification'] != 'PASS']
        report['classification'] = failed[0]['classification'] if failed else 'PASS'
    except AssertionError as error:
        report.update(classification='PRODUCT_FAIL', error=str(error), trace=traceback.format_exc())
    except Exception as error:
        report.update(classification='ENVIRONMENT_ERROR', error=str(error), trace=traceback.format_exc())
    finally:
        server.shutdown()
        report['source_unchanged'] = report['source_sha256'] == hashes()
        if not report['source_unchanged']:
            report['classification'] = 'TEST_HARNESS_FAIL'
        report['finished_at'] = now()
        (args.out / 'proporcoes-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: report.get(key) for key in ['classification', 'source_unchanged', 'finished_at']}) + ' cases=' + str(len(report['cases'])))
    return 0 if report['classification'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Planning's source-faithful pages at real responsive and browser zoom sizes.

Synthetic setup uses the confirmed command API; interactions under test use the
actual tabs, form and profile dialogs. Nothing opens an operator browser profile.
The default entry runs every layout/theme/width and native Chromium 200% case.
These are geometry/focus/interaction checks, not human visual acceptance.
"""
import argparse
import base64
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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.superpowers/sdd/planning-parity-20261020/layout'
LAYOUTS = ['sidebar', 'topbar', 'glass', 'submenu']
THEMES = ['light', 'dark']
TABS = [('start', 'Comece aqui'), ('consolidated', 'Consolidado'),
        ('monthly', 'Preenchimento mensal')]
SOURCES = ['index.html', 'build-id.js', 'src/js/manifest.json', 'src/styles/app.css',
           'src/js/30-accounting/06-planning/01-engine.js',
           'src/js/30-accounting/06-planning/02-state.js',
           'src/js/30-accounting/06-planning/03-ui.js',
           'src/js/40-app/01-navigation.js']


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def hashes():
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}


def financial(page):
    return page.evaluate('''() => JSON.stringify({planning:S.patrimonialPlanning,
      legacy:S.fxPlanning,forex:S.forex,accounts:S.accounts,finpes:S.finpes,alladin:S.alladin})''')


def seed(page):
    """Setup only: two confirmed observations make both real charts testable."""
    return page.evaluate('''() => {
      const api=JPWPlanning,d=new Date(),today=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');
      const start=api.engine.addMonths(today,-2),config={name:'Conta sintética de layout',
        startMonth:start,initialUsd:1000,profileId:'base',monthlyContributionUsd:100,
        goals:{adequate:{value:150,currency:'USD'},ideal:{value:300,currency:'USD'}}};
      const created=api.commands.execute('createAccount',config,api.queries.token());
      if(!created.ok)throw Error('Synthetic setup create refused: '+JSON.stringify(created));
      for(const [offset,usd] of [[0,30],[1,35]]){
        const month=api.engine.addMonths(start,offset),accountId=created.accountId;
        let result=api.commands.execute('recordResult',{accountId,month,usd},api.queries.token(accountId));
        if(!result.ok)throw Error('Synthetic result refused: '+JSON.stringify(result));
        result=api.commands.execute('finalizeMonth',{accountId,month,confirmFlows:true},api.queries.token(accountId));
        if(!result.ok)throw Error('Synthetic closure refused: '+JSON.stringify(result));
      }
      api.ui.render(true);return {accountId:created.accountId,start,today};
    }''')


def assert_box(page, selector, label, viewport=True):
    box = page.locator(selector).first.evaluate('''el => {
      const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,
        bottom:r.bottom,width:r.width,height:r.height,viewport:innerWidth,viewHeight:innerHeight};
    }''')
    assert box['width'] > 0 and box['height'] > 0, (label, 'zero size', box)
    if viewport:
        assert box['left'] >= -1 and box['right'] <= box['viewport'] + 1, (label, 'horizontal clipping', box)
    return box


def table_geometry(page):
    results = page.locator('#planning .pl-table-scroll:visible').evaluate_all('''els => els.map(el => {
      const r=el.getBoundingClientRect(),table=el.querySelector('table');
      const old=el.scrollLeft;el.scrollLeft=el.scrollWidth;const scrolled=el.scrollLeft;
      const last=table?.querySelector('thead tr:last-child th:last-child')?.getBoundingClientRect();
      el.scrollLeft=old;return {left:r.left,right:r.right,width:r.width,client:el.clientWidth,
        scroll:el.scrollWidth,scrolled,overflow:getComputedStyle(el).overflowX,
        lastRight:last?.right,viewport:innerWidth};
    })''')
    for item in results:
        assert item['left'] >= -1 and item['right'] <= item['viewport'] + 1, ('table wrapper escapes viewport', item)
        assert item['overflow'] in ['auto', 'scroll'], ('table does not own horizontal scrolling', item)
        if item['scroll'] > item['client'] + 1:
            assert item['scrolled'] > 0, ('overflowing table cannot be explored', item)
            assert item['lastRight'] <= item['right'] + 2, ('final table column remains inaccessible', item)
    return results


def tab_word_geometry(page):
    """Measure actual glyph fragments so a word cannot be split across lines."""
    words = page.locator('#planning .pl-tabs [data-pl-view]').evaluate_all(r'''els => els.flatMap(el => {
      const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),result=[];
      let node;while((node=walker.nextNode())){
        for(const match of node.textContent.matchAll(/\S+/gu)){
          const range=document.createRange();range.setStart(node,match.index);
          range.setEnd(node,match.index+match[0].length);
          const rects=Array.from(range.getClientRects()).filter(r=>r.width>0&&r.height>0)
            .map(r=>({left:r.left,right:r.right,top:r.top,bottom:r.bottom}));
          result.push({tab:el.dataset.plView,word:match[0],rects});range.detach();
        }
      }return result;
    })''')
    assert words and all(len(word['rects']) == 1 for word in words), ('tab label splits a word across lines', words)
    return words


def dialog_checks(page, case):
    page.locator('#planning [data-pl-view=start]').click()
    page.locator('#planning [data-pl-action=configure]').click()
    dialog = page.locator('#planning dialog.pl-dialog')
    dialog.wait_for(state='visible')
    geometry = assert_box(page, '#planning dialog.pl-dialog', 'account dialog')
    assert geometry['top'] >= -1 and geometry['bottom'] <= geometry['viewHeight'] + 1, ('dialog vertical clipping', geometry)
    year = page.locator('#pl-native-ano')
    assert year.evaluate('el=>document.activeElement===el'), 'opening source form does not focus its initial question'
    before_scroll = page.locator('#planning .pl-form-body').evaluate('el=>el.scrollTop')
    page.evaluate('JPWPlanning.ui.render()')
    assert year.evaluate('el=>document.activeElement===el'), 'ordinary render steals form focus'
    assert page.locator('#planning .pl-form-body').evaluate('el=>el.scrollTop') == before_scroll, 'ordinary render scrolls the form'
    labels = dialog.locator('input:not([type=hidden]),select').evaluate_all('''els=>els.filter(el=>el.getClientRects().length).map(el=>({
      name:el.name,labelled:!!(el.labels?.length||el.getAttribute('aria-label')||el.getAttribute('aria-labelledby'))}))''')
    assert labels and all(item['labelled'] for item in labels), ('unlabelled source question', labels)
    for selector in ['#planning .pl-form>header', '#planning .pl-form>footer', '#planning .pl-close']:
        item = assert_box(page, selector, selector)
        assert item['top'] >= geometry['top'] - 1 and item['bottom'] <= geometry['bottom'] + 1, ('form control outside dialog', selector, item)
    page.locator('#pl-native-openProfiles').click()
    profile = page.locator('#pl-native-profileDialog')
    profile.wait_for(state='visible')
    profile_box = assert_box(page, '#pl-native-profileDialog', 'profile comparison')
    assert profile_box['top'] >= -1 and profile_box['bottom'] <= profile_box['viewHeight'] + 1, ('profile dialog vertical clipping', profile_box)
    assert profile.locator('[data-pl-choose-profile]').count() == 4, 'native chooser omits a profile'
    plot_sizes = profile.locator('svg.pl-native-chart').evaluate_all('els=>els.map(el=>({w:el.getBoundingClientRect().width,h:el.getBoundingClientRect().height}))')
    assert len(plot_sizes) == 5 and all(plot['w'] > 80 and plot['h'] > 40 for plot in plot_sizes), ('profile/recovery chart geometry', plot_sizes)
    close = assert_box(page, '#pl-native-closeProfiles', 'profile close')
    assert close['top'] >= profile_box['top'] - 1 and close['bottom'] <= profile_box['bottom'] + 1
    page.keyboard.press('Escape')
    assert not profile.is_visible(), 'Escape does not close only the profile comparison'
    assert page.locator('#pl-native-openProfiles').evaluate('el=>document.activeElement===el'), 'profile close loses its initiating focus'
    page.locator('#planning dialog.pl-dialog [data-pl-action=close]').first.click()
    assert not dialog.count(), 'source form did not close'
    case['dialog'] = {'outer': geometry, 'profile': profile_box, 'labels': len(labels), 'plots': plot_sizes}


def journey(page, case):
    assert page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches'), 'reduced motion was not active'
    before = financial(page)
    case['tabs'] = []
    for view, title in TABS:
        button = page.locator('#planning [data-pl-view="' + view + '"]')
        button.click()
        assert button.inner_text().strip() == title, (view, 'native tab label changed')
        assert button.get_attribute('aria-selected') == 'true', (view, 'selected tab state')
        assert page.locator('#planning [role=tabpanel]').get_attribute('aria-labelledby') == 'pl-tab-' + view, (view, 'tabpanel label')
        root = assert_box(page, '#planning', view + ' planning surface')
        widths = page.locator('#planning .pl-shell').evaluate('el=>({client:el.clientWidth,scroll:el.scrollWidth})')
        assert widths['scroll'] <= widths['client'] + 1, (view, 'local surface overflows outside its table', widths)
        tables = table_geometry(page)
        plots = page.locator('#planning [data-pl-chart],#planning [data-pl-real-chart]').evaluate_all('els=>els.map(el=>({w:el.getBoundingClientRect().width,h:el.getBoundingClientRect().height}))')
        if view == 'consolidated':
            assert len(plots) == 2 and all(plot['w'] > 80 and plot['h'] >= 100 for plot in plots), ('planning chart is blank or collapsed', plots)
        case['tabs'].append({'view': view, 'title': title, 'surface': root, 'tables': tables,
                             'plots': plots, 'tab_words': tab_word_geometry(page)})
    # Keyboard navigation uses the actual tab controller, not direct selectView.
    first = page.locator('#planning [data-pl-view=start]')
    first.click();first.focus();page.keyboard.press('ArrowRight')
    assert page.locator('#planning [data-pl-view=consolidated]').evaluate('el=>document.activeElement===el&&el.getAttribute("aria-selected")==="true"'), 'tab keyboard navigation lost focus/selection'
    dialog_checks(page, case)
    assert financial(page) == before, 'inspecting layouts, source pages or profile help wrote financial data'


def long_projection_geometry(page, report):
    """A plausible large projection must remain complete at the mobile width."""
    account_id = page.evaluate('''() => {
      const d=new Date(),api=JPWPlanning,start=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');
      const result=api.commands.execute('createAccount',{name:'Projeção sintética longa',
        startMonth:start,initialUsd:1000000,profileId:'high-risk',monthlyContributionUsd:100000,
        goals:{adequate:{value:1000,currency:'USD'},ideal:{value:10000,currency:'USD'}}},api.queries.token());
      if(!result.ok)throw Error('Long projection fixture refused: '+JSON.stringify(result));
      api.ui.render(true);return result.accountId;
    }''')
    page.locator('#planning [data-pl-view=consolidated]').click()
    page.locator('#planning [data-pl-account]').select_option(account_id)
    report['long_projection_mobile'] = []
    before = financial(page)
    for layout in LAYOUTS:
        for theme in THEMES:
            page.evaluate('layout=>mountNavigationLayout(layout)', layout)
            page.evaluate('theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
            geometry = page.locator('#planning [data-pl-summary-group=projection] .pl-metrics').evaluate('''el => {
              const shell=el.closest('.pl-shell'),value=el.querySelector('.pl-metric:last-child strong'),
                r=value.getBoundingClientRect(),style=getComputedStyle(value);
              return {shellClient:shell.clientWidth,shellScroll:shell.scrollWidth,
                text:value.textContent,client:value.clientWidth,scroll:value.scrollWidth,
                left:r.left,right:r.right,viewport:innerWidth,overflow:style.textOverflow,
                visibility:style.visibility,display:style.display};
            }''')
            report['long_projection_mobile'].append(dict(layout=layout, theme=theme, **geometry))
            assert len(geometry['text']) >= 20 and '…' not in geometry['text'], ('long projection fixture lost complete money', geometry)
            assert geometry['shellScroll'] <= geometry['shellClient'] + 1, ('long projection escapes mobile surface', geometry)
            assert geometry['scroll'] <= geometry['client'] + 1, ('long projection overflows its metric', geometry)
            assert geometry['left'] >= -1 and geometry['right'] <= geometry['viewport'] + 1, ('long projection is outside viewport', geometry)
            assert geometry['overflow'] != 'ellipsis' and geometry['visibility'] == 'visible' and geometry['display'] != 'none', ('long money was hidden or truncated', geometry)
    assert financial(page) == before, 'large-money layout checks changed financial data'


def setup(context, url, errors):
    context.add_init_script('window.__onbShown=true;')
    install_bootstrap(context, {'USDBRL': 5})
    page = context.pages[0] if context.pages else context.new_page()
    page.set_default_timeout(15000)
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('dialog', lambda dialog: dialog.accept())
    page.goto(url);wait_bootstrap(page)
    page.evaluate("navigateToScreen('planning')")
    seed(page)
    return page


def run_case(page, report, name, layout, theme, out, screenshot=False):
    case = {'name': name, 'classification': 'NOT_RUN', 'layout': layout, 'theme': theme}
    report['cases'].append(case)
    try:
        page.evaluate('layout=>mountNavigationLayout(layout)', layout)
        page.evaluate('theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
        case['palette']=page.evaluate('''() => {const style=getComputedStyle(document.documentElement);return {panel:style.getPropertyValue('--panel').trim(),ink:style.getPropertyValue('--ink').trim()}}''')
        journey(page, case)
        case['classification'] = 'PASS'
        if screenshot:
            page.locator('#planning [data-pl-view=consolidated]').click()
            page.screenshot(path=str(out / (name + '.png')), full_page=False)
    except AssertionError as error:
        case.update(classification='PRODUCT_FAIL', error=str(error), trace=traceback.format_exc())
    except Exception as error:
        case.update(classification='TEST_HARNESS_FAIL', error=str(error), trace=traceback.format_exc())
    print(case['classification'] + ' ' + name, flush=True)
    return case


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    source_before = hashes()
    report = {'classification': 'NOT_RUN', 'source_sha256': source_before,
              'test_sha256': sha256(Path(__file__).read_bytes()).hexdigest(), 'cases': [],
              'limits': {'Safari': 'NOT_RUN', 'physical_touch': 'NOT_RUN', 'screen_reader': 'NOT_RUN',
                         'human_visual_acceptance': 'NOT_RUN'}}
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/index.html'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            report['browser'] = browser.version
            for width, height in [(1440, 1000), (390, 844)]:
                context = browser.new_context(viewport={'width': width, 'height': height},
                    service_workers='block', reduced_motion='reduce', has_touch=width==390)
                errors = []
                try:
                    page = setup(context, url, errors)
                    for layout in LAYOUTS:
                        for theme in THEMES:
                            run_case(page, report, f'{layout}-{theme}-{width}', layout, theme, args.out,
                                     screenshot=(width==1440 and layout=='sidebar' and theme=='light') or
                                                (width==390 and layout=='submenu' and theme=='dark'))
                    if width == 390:
                        long_projection_geometry(page, report)
                    assert not errors, errors
                    assert_fixture_requests(context)
                finally:
                    context.close()
            browser.close()
            profile = Path(tempfile.mkdtemp(prefix='planning-native-200-', dir=args.out))
            (profile / 'Default').mkdir()
            (profile / 'Default/Preferences').write_text(json.dumps({'partition': {
                'default_zoom_level': {'x': math.log(2) / math.log(1.2)}}}))
            options = launch_options();options.update(headless=False, no_viewport=True,
                args=['--window-size=1440,1000'], service_workers='block', reduced_motion='reduce')
            try:
                context = pw.chromium.launch_persistent_context(str(profile), **options)
                errors = []
                try:
                    page = setup(context, url, errors)
                    zoom = page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
                    if abs(zoom['outer'] / zoom['inner'] - 2) >= .01 or zoom['css'] != '1':
                        raise RuntimeError('Native zoom unavailable: ' + str(zoom))
                    report['native_zoom'] = zoom
                    for layout in LAYOUTS:
                        for theme in THEMES:
                            case = run_case(page, report, f'{layout}-{theme}-native200', layout, theme, args.out)
                            case['native_zoom'] = zoom
                    page.locator('#planning [data-pl-view=consolidated]').click()
                    cdp = context.new_cdp_session(page)
                    (args.out / 'native-200-dark.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot', {
                        'format': 'png', 'fromSurface': True, 'captureBeyondViewport': False})['data']))
                    assert not errors, errors
                    assert_fixture_requests(context)
                finally:
                    context.close()
            finally:
                shutil.rmtree(profile)
        report['source_unchanged'] = source_before == hashes()
        assert report['source_unchanged'], 'Runtime sources changed during layout verification'
        assert len(report['cases']) == 24, 'Layout matrix omitted a mandatory combination'
        by_name={case['name']:case for case in report['cases']}
        for name,case in by_name.items():
            if '-light-' in name:
                dark=by_name[name.replace('-light-','-dark-')]
                assert case.get('palette')!=dark.get('palette'), ('theme labels did not switch the actual palette',name)
        failed = [case for case in report['cases'] if case['classification'] != 'PASS']
        report['classification'] = failed[0]['classification'] if failed else 'PASS'
    except AssertionError as error:
        report.update(classification='PRODUCT_FAIL', error=str(error), trace=traceback.format_exc())
    except Exception as error:
        report.update(classification='ENVIRONMENT_ERROR', error=str(error), trace=traceback.format_exc())
    finally:
        server.shutdown()
        (args.out / 'layout-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'classification': report['classification'], 'cases': len(report['cases']),
                      'source_unchanged': report.get('source_unchanged'), 'report': str(args.out / 'layout-results.json')}, ensure_ascii=False))
    return 0 if report['classification'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

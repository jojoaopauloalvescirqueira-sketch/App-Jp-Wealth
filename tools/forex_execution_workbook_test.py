#!/usr/bin/env python3
"""Execution Workbook contract: isolated synthetic browser tasks and presentation.

The same suite can characterize the archived pre-change product with --root and
--characterization-only. Existing financial fixtures, writers and network fixtures
are reused unchanged. A screenshot supports an assertion; it is never the oracle.
"""
import argparse
import base64
from functools import partial
import hashlib
import json
import math
import re
import shutil
from pathlib import Path
import tempfile
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, assert_fixture_requests
from forex_clarity_test import SEED
from forex_execution_table_test import Server, Quiet, ready, set_field, field, persisted, projection, order, HASH, near, prepare_drafts
from notes_launcher_test import launch_options, settle

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['index.html', 'build-id.js', 'src/js/manifest.json', 'src/styles/app.css',
           'src/js/20-ui/30-execution-board.js', 'src/js/20-ui/13-exec-views.js',
           'src/js/40-app/01-navigation.js', 'src/js/10-domain/18-execution-board-model.js',
           'src/js/10-domain/00-forex-engine.js', 'src/js/10-domain/00-forex-state.js']
PANELS = {'matrix': 'ebToolMatrix', 'rootn': 'ebToolRootN', 'motor': 'ebToolMotor'}


def hashes(root, portable=False):
    names = SOURCES+(['dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'] if portable else [])
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names}


def seed(page):
    scope = page.evaluate(SEED)
    settle(page)
    page.wait_for_function("JPWNavigation.current().canonical==='forex-operation' && JPWExec.ui.getView()==='panel'")
    prepare_drafts(page)
    return scope


def tool(page, name):
    page.locator(f'[data-eb-tool="{name}"]').click()
    settle(page)
    assert page.locator('#'+PANELS[name]).is_visible(), name


def assert_action_labels(page, row='0:0'):
    for selector in [f'[data-eb-save-row="{row}"]', f'[data-eb-cancel-row="{row}"]', f'[data-eb-open-detail="{row}"]']:
        measured = page.locator(selector).evaluate("""e=>{
          const range=document.createRange();range.selectNodeContents(e.querySelector('[aria-hidden="true"]')||e);
          const text=range.getBoundingClientRect(),button=e.getBoundingClientRect();
          return {label:e.textContent.trim(),icon:!!e.querySelector('[aria-hidden="true"]'),accessible:e.getAttribute('aria-label'),whiteSpace:getComputedStyle(e).whiteSpace,
            width:e.clientWidth,scroll:e.scrollWidth,lines:range.getClientRects().length,
            textLeft:text.left-button.left,textRight:button.right-text.right};
        }""")
        assert not measured['icon'] or measured['accessible'], ('Icon-only action needs an accessible name', measured)
        assert measured['whiteSpace'] == 'nowrap' and measured['lines'] == 1, ('Mobile action label must stay intact', measured)
        assert measured['scroll'] <= measured['width']+1 and measured['textLeft'] >= -1 and measured['textRight'] >= -1, ('Mobile action label overflows its target', measured)


def workbook_contract(page, out, observed):
    seed(page)
    before = persisted(page)
    observed['headers'] = page.locator('.eb-order-table thead').all_text_contents()
    assert page.locator('#ebOrderScroll .eb-workbook-table').count() == 1, 'One continuous editable workbook is required'
    table = page.locator('#ebOrderScroll .eb-workbook-table')
    assert 'SI' in page.locator('#executionBoardAccount .eb-capital-strip').inner_text(), 'The initial SI base must be visible beside account/equity'
    assert table.locator('thead tr.eb-column-labels th').count() == 20, 'The approved workbook has twenty explicit columns'
    assert table.locator('thead tr.eb-column-groups').count() == 1
    assert table.locator('thead tr.eb-column-groups th').evaluate_all("cells=>cells.map(e=>e.colSpan)") == [4, 4, 8, 2, 2]
    assert table.locator('tbody .eb-phase-row').count() == 6
    assert page.locator('details[data-phase]').count() == 0, 'Phase headers must not conceal the order rows in accordions'
    assert page.locator('.eb-order-table').count() == 1, 'There must be one editable order table'
    for pi in range(6):
        assert table.locator(f'#ebPhase-{pi}.eb-phase-row[data-phase="{pi}"]').count() == 1
        assert page.locator(f'[data-eb-row="{pi}:0"]').is_visible(), (pi, 'Phase row is inaccessible')
        for name in ['id', 'brokerHash', 'par', 'tipo', 'role', 'lote', 'entry', 'sl', 'tp', 'status',
                     'result', 'costs', 'costBasis', 'stopValidated', 'amplifiesExposure', 'pendingActive']:
            assert page.locator(f'[data-p="{pi}"][data-o="0"][data-f="{name}"]').count() == 1, (pi, name, 'Duplicated/missing editor')
        for name in ['rewardRisk', 'stopDistance', 'stopPercent', 'targetDistance', 'targetPercent', 'atrMultiple', 'rootOne', 'rootTwo', 'riskValue', 'riskPercent']:
            assert page.locator(f'[data-eb-row="{pi}:0"] [data-eb-calc="{name}"]').count() == 1, (pi, name, 'Missing calculated column')
    assert page.locator('.eb-audit-table input,.eb-audit-table select').count() == 0
    table.screenshot(path=str(out/'workbook-characterization.png'))
    assert persisted(page) == before, 'Inspecting/scrolling the workbook wrote financial state'
    observed.update(columns=20, phases=6, oneEditorPerField=True, noPhaseAccordions=True)


def empty_phase_add(page, out, observed):
    scope = page.evaluate(SEED)
    settle(page)
    page.set_viewport_size({'width':320, 'height':844})
    settle(page)
    assert page.locator('.eb-order-row').count() == 0, 'Anonymous preallocations must not look like operations'
    assert page.locator('.eb-empty-phase').count() == 0, 'Empty phases must not reserve another table row'
    assert page.locator('.eb-phase-row').count() == 6
    assert page.locator('.eb-phase-row').evaluate_all("rows=>rows.every(e=>/0 ordens/.test(e.textContent))"), 'Each empty phase keeps a visible count and Add action'
    placeholder = order(page)
    before = persisted(page)
    for pi in range(6):
        button = page.locator(f'[data-addorder="{pi}"]')
        button.scroll_into_view_if_needed()
        settle(page)
        box = button.bounding_box()
        assert box and box['height'] >= 48 and box['width'] >= 48, (pi, box)
        assert button.evaluate("e=>{const r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))}"), (pi, 'Phase Add button is overlapped')
    assert persisted(page) == before, 'Viewing the empty phases wrote financial facts'
    page.locator('[data-addorder="0"]').click()
    settle(page)
    assert page.locator('[data-eb-row="0:1"]').is_visible(), 'Add must expose the new draft without changing the anonymous slot index'
    assert page.locator('.eb-order-row').count() == 1
    assert_action_labels(page, '0:1')
    assert order(page) == placeholder, 'Add reinterpreted or overwrote the anonymous slot'
    draft = page.evaluate('JPWForex.state.accountContext(JPWForex.state.operationalSelection()).value.phases[0].orders[1]')
    assert draft['recordStatus'] == 'draft' and draft['recordVersion'] == 0 and draft['orderId']
    assert draft['status'] == '' and draft['result'] is None and draft['lote'] == 0
    assert page.evaluate('JPWForex.state.operationalSelection().periodId') == scope['periodId']
    page.locator('#ebOrderScroll').screenshot(path=str(out/'empty-mobile-phase-add.png'))
    observed.update(sixEmptyPhases=True, accessiblePhaseAdd=True, originalAnonymousSlotPreserved=True, draftIndex=1)


def tools_and_lot_bases(page, out, observed):
    scope = seed(page)
    result = page.evaluate("""scope => JPWForex.state.recordAccountFacts({accountIndex:0,periodId:scope.periodId,
      si:10000,equity:7500,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',
      source:'Synthetic reduced equity',observedAt:'2026-09-22T13:00:00Z'},
      {reason:'Synthetic distinct SI and equity'})""", scope)
    assert result['ok'], result
    page.evaluate('render();JPWForex.executionBoardUI.render()')
    before = persisted(page)
    item = next(i for i in projection(page)['instruments'] if i['id'] == 'EURUSD')
    near(item['initialNormal']['value'], 10000*.5/120000)
    near(item['initialRestrictive']['value'], 10000*.25/120000)
    near(item['currentNormal']['value'], 7500*.5/120000)
    near(item['currentRestrictive']['value'], 7500*.25/120000)
    assert item['normal'] == item['currentNormal'] and item['restrictive'] == item['currentRestrictive']
    assert item['initialNormal']['base'] == 10000 and item['currentNormal']['base'] == 7500
    assert projection(page)['executionEligibility']['status'] == 'BLOCKED'
    assert projection(page)['risk']['sizingTrace']['finalVolume'] is None
    set_field(page, 'entry', '1.2345')
    editor = field(page, 'entry').element_handle()
    editor.evaluate("e=>{e.focus();e.setSelectionRange(2,4)}")
    scroll = page.locator('#ebOrderScroll')
    scroll.evaluate('e=>{e.scrollLeft=370;window.__workbookScroll=e.scrollLeft}')
    for name, panel in PANELS.items():
        tool(page, name)
        assert page.locator(f'[data-eb-tool="{name}"]').get_attribute('aria-selected') == 'true'
        for other, other_panel in PANELS.items():
            assert page.locator('#'+other_panel).evaluate('e=>e.hidden && e.inert') == (name != other)
        assert editor.evaluate('e=>e.isConnected') and field(page, 'entry').input_value() == '1.2345'
        assert editor.evaluate('e=>e.selectionStart===2 && e.selectionEnd===4'), 'Tool tabs lost the workbook cursor selection'
        assert page.evaluate('(name)=>document.activeElement.dataset.ebTool===name', name)
        assert page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
        assert scroll.evaluate('e=>e.scrollLeft===window.__workbookScroll'), 'Tool tab reset workbook scroll'
        assert persisted(page) == before, ('Tool selection wrote state', name)
    for key, expected in [('Home', 'matrix'), ('ArrowRight', 'rootn'), ('End', 'motor'), ('ArrowLeft', 'rootn')]:
        page.keyboard.press(key)
        settle(page)
        assert page.evaluate('(name)=>document.activeElement.dataset.ebTool===name', expected)
        assert page.locator('#'+PANELS[expected]).is_visible() and persisted(page) == before
        assert field(page, 'entry').input_value() == '1.2345'
    assert all(page.locator(f'#ebToolMotor [data-eb-metric="{name}"]').count() == 1
               for name in ['initialNormal', 'initialRestrictive', 'currentNormal', 'currentRestrictive'])
    assert 'SI' in page.locator('#ebToolMotor').inner_text()
    assert 'equity' in page.locator('#ebToolMotor').inner_text().lower()
    for call in ["JPWNavigation.navigate('motor')", "JPWNavigation.navigateLocal('exec','motor')", "JPWExec.ui.selectView('motor')"]:
        assert page.evaluate(call), call
        settle(page)
        assert page.locator('#ebToolMotor').is_visible() and page.locator('#executionBoard').is_visible()
        assert field(page, 'entry').input_value() == '1.2345' and persisted(page) == before
        assert not page.locator('#executionBoardDialog').is_visible(), 'A tool alias incorrectly asks to leave the operation'
    page.locator('[data-eb-cancel-row="0:0"]').click()
    settle(page)
    assert not page.evaluate('JPWForex.executionBoardUI.hasDrafts()') and persisted(page) == before
    tool(page, 'rootn')
    page.locator('#ebInstrumentSelect').select_option('EURUSD')
    page.locator('[data-eb-diagnostics]').click()
    for name in ['oneWeekN', 'oneWeekF', 'twoWeeksN', 'twoWeeksF']:
        assert page.locator(f'#ebDiagnosticForm [name="{name}"]').input_value() == ''
    page.locator('#ebDiagnosticCancel').click()
    settle(page)
    assert persisted(page) == before
    page.locator('#ebTools').screenshot(path=str(out/'integrated-tools.png'))
    observed.update(initialNormal=item['initialNormal']['value'], currentNormal=item['currentNormal']['value'],
                    independentBases=True, aliasesPreserveDrafts=True, tabsWriteNothing=True)


def matrix_boundaries(page, out, observed):
    scope = seed(page)
    tool(page, 'matrix')
    ranges = page.locator('#ebToolMatrix tbody [data-label="Drawdown"]').all_text_contents()
    assert len(ranges) == 6, ranges
    for index, upper in enumerate([2, 6, 10, 14, 18]):
        text = ranges[index]
        assert re.search(r'≤\s*'+str(upper)+r'\s*%', text), ('Inclusive upper DD boundary required', text)
        assert not re.search(r'<\s*'+str(upper)+r'\s*%', text), ('Displayed boundary contradicts the engine', text)
    cases = []
    observed['boundaries'] = cases
    for phase, dd in enumerate([2, 6, 10, 14, 18], start=1):
        result = page.evaluate("""x => JPWForex.state.recordAccountFacts({accountIndex:0,periodId:x.periodId,
          si:10000,equity:x.equity,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',
          source:'Synthetic exact drawdown boundary',observedAt:'2026-09-22T14:00:00Z'},
          {reason:'Synthetic exact phase boundary'})""", {'periodId':scope['periodId'], 'equity':10000*(1-dd/100)})
        assert result['ok'], result
        before = persisted(page)
        page.evaluate('render();JPWForex.executionBoardUI.render()')
        settle(page)
        model = projection(page)
        near(model['capital']['drawdown']['value'], dd)
        current = page.locator('#ebToolMatrix tbody tr.eb-current-phase[aria-current="true"]')
        assert current.count() == 1
        actual_phase = model['risk']['accountPhase']['value']
        assert current.evaluate('e=>[...e.parentElement.children].indexOf(e)') == actual_phase-1, (dd, current.inner_text())
        assert persisted(page) == before, 'Matrix projection changed the confirmed boundary facts'
        exact = page.evaluate('(dd)=>JPWForex.engine.resolveAccountPhase({ddPercent:dd}).value', dd)
        assert exact == phase, (dd, 'Exact phase resolver boundary', exact, phase)
        cases.append({'dd':dd, 'equity':10000*(1-dd/100), 'observedDD':model['capital']['drawdown']['value'],
                      'expectedPhase':phase, 'actualPhase':actual_phase, 'exactResolverPhase':exact, 'highlight':current.inner_text()})
    page.locator('#ebToolMatrix').screenshot(path=str(out/'matrix-exact-boundaries.png'))
    observed.update(ranges=ranges, boundaries=cases)
    failures = [case for case in cases if case['actualPhase'] != case['expectedPhase']]
    assert not failures, ('The account DD observation crossed its exact inclusive boundary', failures)


def legacy_six_groups(page, out, observed):
    seed(page)
    page.evaluate("""() => {
      const scope=JPWForex.state.operationalSelection();
      S.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId].phases.forEach((phase,index)=>{
        phase.policyVersion='LEGACY_UNRESOLVED';phase.title='LEGACY '+(index+1);
      });
    }""")
    before = persisted(page)
    page.evaluate('renderPhases();JPWForex.executionBoardUI.render()')
    settle(page)
    projected = projection(page)['phases']
    assert [phase['name'] for phase in projected] == ['LEGACY '+str(i) for i in range(1, 7)]
    assert all(phase['legacy'] is True for phase in projected)
    for index in range(6):
        header = page.locator(f'#ebPhase-{index}.eb-phase-row[data-phase="{index}"]')
        assert header.locator('.eb-phase-label strong').inner_text() == 'LEGACY '+str(index+1), (index, header.inner_text())
        assert header.locator(f'[data-addorder="{index}"]').count() == 1
        assert page.locator(f'[data-eb-row="{index}:0"]').is_visible()
    anchors = page.locator('#ebPhaseNav [data-eb-phase-jump]').all_text_contents()
    assert len(anchors) == 6 and all('LEGACY '+str(index+1) in title for index, title in enumerate(anchors)), anchors
    assert persisted(page) == before, 'Rendering silently mapped unresolved legacy grades to the current phases'
    page.locator('#ebOrderScroll').screenshot(path=str(out/'legacy-six-grades.png'))
    observed.update(names=[phase['name'] for phase in projected], preservedLegacyIndices=True)


def records_and_context(page, out, observed):
    scope = seed(page)
    before = persisted(page)
    fields = dict(id='WORKBOOK-001', par='EURUSD', tipo='BUY', role='GENESIS', lote='0.2', entry='1.2',
                  sl='1.17', tp='1.26', status='Aberta', costs='0', costBasis='SEPARATE_FROM_RESULT', stopValidated=True)
    for name, value in fields.items():
        set_field(page, name, value)
    assert persisted(page) == before
    page.locator('[data-eb-save-row="0:0"]').click()
    settle(page)
    assert persisted(page) == before
    assert field(page, 'brokerHash').evaluate('e=>document.activeElement===e')
    assert field(page, 'brokerHash').get_attribute('aria-invalid') == 'true'
    assert page.locator('[data-eb-detail="0:0"]').evaluate('e=>e.open')
    assert 'HASH' in page.locator('#ebError-0-0').inner_text()
    set_field(page, 'brokerHash', HASH)
    page.locator('[data-eb-save-row="0:0"]').click()
    settle(page)
    original = order(page)
    assert original['accountId'] == 'TABLE-A' and original['periodId'] == scope['periodId']
    assert original['brokerHash'] == HASH and original['recordVersion'] == 1 and len(original['revisions']) == 1
    model = projection(page)
    near(model['operational']['exposure']['value'], 600)
    near(model['operational']['exposure']['percent'], 5)
    near(model['operational']['leverage']['value'], 2)
    saved = persisted(page)
    confirmed_risk_text = page.locator('[data-eb-row="0:0"] [data-eb-calc="riskValue"]').inner_text()
    set_field(page, 'sl', '1.192')
    assert page.locator('[data-eb-row="0:0"] [data-eb-calc="atrMultiple"]').inner_text() == '4×'
    assert page.locator('[data-eb-row="0:0"] [data-eb-calc="riskValue"]').inner_text() == confirmed_risk_text
    assert persisted(page) == saved, 'Preview changed confirmed state'
    near(projection(page)['operational']['exposure']['value'], 600)
    field(page, 'sl').evaluate('e=>{window.__workbookInput=e;e.focus();e.setSelectionRange(2,4)}')
    page.locator('#ebOrderScroll').evaluate('e=>{e.scrollLeft=420;window.__workbookLeft=e.scrollLeft}')
    page.evaluate('JPWForex.executionBoardUI.render()')
    assert field(page, 'sl').evaluate('e=>e===window.__workbookInput && document.activeElement===e && e.selectionStart===2 && e.selectionEnd===4')
    assert page.locator('#ebOrderScroll').evaluate('e=>e.scrollLeft===window.__workbookLeft')
    assert not page.evaluate("JPWNavigation.navigate('forex-management-accounts')")
    page.locator('#ebLeaveStay').click()
    settle(page)
    assert field(page, 'sl').input_value() == '1.192' and persisted(page) == saved
    page.locator('[data-eb-cancel-row="0:0"]').click()
    settle(page)
    assert order(page) == original and persisted(page) == saved
    set_field(page, 'sl', '1.191')
    page.locator('[data-eb-reason="0:0"]').evaluate("e=>{e.closest('details').open=true}")
    page.locator('[data-eb-reason="0:0"]').fill('Synthetic correction refused by writer')
    page.evaluate('() => {window.__workbookSave=save;save=()=>false;}')
    try:
        page.locator('[data-eb-save-row="0:0"]').click()
        settle(page)
        assert persisted(page) == saved and field(page, 'sl').input_value() == '1.191'
        assert page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
    finally:
        page.evaluate('save=window.__workbookSave')
    result = page.evaluate("operationRecordOrder(0,0,{tp:1.28},{reason:'Synthetic competing correction'})")
    assert result['ok'], result
    concurrent = persisted(page)
    page.locator('[data-eb-save-row="0:0"]').click()
    settle(page)
    assert persisted(page) == concurrent and field(page, 'sl').input_value() == '1.191'
    assert 'versão confirmada mudou' in page.locator('#ebError-0-0').inner_text()
    page.locator('[data-eb-cancel-row="0:0"]').click()
    settle(page)
    page.evaluate("JPWNavigation.navigate('forex-management-accounts');JPWForex.accountsUI.examine('TABLE-B')")
    assert page.evaluate('JPWForex.state.operationalSelection().accountId') == 'TABLE-A'
    assert persisted(page) == concurrent
    page.locator('#fxAccountsUse').click()
    settle(page)
    assert page.evaluate('JPWForex.state.operationalSelection().accountId') == 'TABLE-B'
    assert page.locator('#hdrPeriod').inner_text() == '01/08/2026'
    assert persisted(page) == concurrent, 'Applying a registered UI context wrote financial data'
    page.evaluate("JPWNavigation.navigate('forex-management-accounts');JPWForex.accountsUI.examine('TABLE-A')")
    page.locator('#fxAccountsUse').click()
    settle(page)
    assert page.evaluate('JPWForex.state.operationalSelection().periodId') == scope['periodId']
    assert order(page)['tp'] == 1.28 and persisted(page) == concurrent
    page.locator('#ebOrderScroll').screenshot(path=str(out/'recorded-and-cancelled-workbook.png'))
    observed.update(exposure=600, exposurePercent=5, leverage=2, previewDoesNotCommit=True,
                    refusedWriterPreservesDraft=True, staleRevisionCannotOverwrite=True, contextApplyExplicit=True)


def layouts(page, out, observed):
    seed(page)
    page.evaluate("() => {for(let n=0;n<7;n++){const r=operationAddDraft(0);if(!r.ok)throw Error(r.error);}render();renderPhases();}")
    if page.locator('#dgBannerClose').is_visible():
        page.locator('#dgBannerClose').click()
    before = persisted(page)
    measurements = []
    for width in [1440, 1024, 390, 320]:
        page.set_viewport_size({'width': width, 'height': 1000 if width > 900 else 844})
        for theme in ['light', 'dark']:
            page.evaluate("t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}", theme)
            settle(page)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), (width, theme, 'Page overflow')
            box = page.locator('#ebOrderScroll').evaluate("""e=>{
              const row=e.querySelector('.eb-order-row'),header=e.querySelector('tr.eb-column-labels');
              return {width:e.clientWidth,scroll:e.scrollWidth,row:getComputedStyle(row).display,
                header:getComputedStyle(header).display,id:getComputedStyle(row.children[0]).position,
                instrument:getComputedStyle(row.children[1]).position,
                columns:header.querySelectorAll('th').length};
            }""")
            assert box['columns'] == 20
            if box['width'] >= 768:
                assert box['row'] == 'table-row' and box['id'] == box['instrument'] == 'sticky', (width, theme, box)
                assert box['scroll'] > box['width'], (width, theme, 'Dense workbook must scroll locally')
                assert page.locator('#ebOrderScroll').evaluate('e=>{e.scrollLeft=500;return e.scrollLeft>0}')
            else:
                assert box['row'] == 'grid' and box['id'] == box['instrument'] == 'static', (width, theme, box)
                assert box['scroll'] <= box['width']+1, (width, theme, 'Mobile list overflow')
                assert_action_labels(page)
            assert page.locator('.eb-order-row').count() == 13
            for pi in range(6):
                assert page.locator(f'[data-eb-row="{pi}:0"]').is_visible()
            # CHG-JPW-OPERATION-PROPORTIONS-TEST-20261005: explicit compact mouse
            # contract; narrow/coarse input remains comfortable, not globally weakened.
            compact = box['width'] >= 768 and not page.evaluate("matchMedia('(pointer:coarse)').matches")
            minimum_font, minimum_target = (14, 36) if compact else (16, 48)
            for key in ['id', 'par', 'tipo', 'role', 'lote', 'entry', 'sl', 'tp', 'status']:
                size = field(page, key).evaluate('e=>parseFloat(getComputedStyle(e).fontSize)')
                assert size >= minimum_font-.1, (width, theme, key, size, minimum_font)
            for selector in ['[data-eb-save-row="0:0"]', '[data-eb-cancel-row="0:0"]', '[data-eb-open-detail="0:0"]']:
                target = page.locator(selector).bounding_box()
                assert target and target['height'] >= minimum_target-.1 and target['width'] >= minimum_target-.1, (width, theme, selector, target)
            page.locator('#ebOrderScroll').scroll_into_view_if_needed()
            settle(page)
            page.screenshot(path=str(out/f'workbook-{width}-{theme}.png'))
            assert persisted(page) == before, 'Resize/theme/local scroll wrote confirmed data'
            measurements.append({'viewport': width, 'theme': theme, **box})
    observed['measurements'] = measurements


def native_zoom(pw, url, out, observed):
    profile = Path(tempfile.mkdtemp(prefix='workbook-native-200-', dir=out))
    (profile/'Default').mkdir()
    (profile/'Default/Preferences').write_text(json.dumps({'partition': {'default_zoom_level': {'x': math.log(2)/math.log(1.2)}}}))
    options = launch_options()
    options.update(headless=False, no_viewport=True, args=['--window-size=1440,1000'], service_workers='block', reduced_motion='reduce')
    context = pw.chromium.launch_persistent_context(str(profile), **options)
    errors = []
    try:
        context.add_init_script('window.__onbShown=true;')
        install_bootstrap(context)
        page = context.pages[0] if context.pages else context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.bring_to_front()
        page.goto(url)
        ready(page)
        seed(page)
        page.wait_for_function("document.visibilityState==='visible'")
        ratio = page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
        if not (abs(ratio['outer']/ratio['inner']-2) < .01 and ratio['css'] == '1'):
            raise RuntimeError('Native 200% zoom was not established: '+str(ratio))
        before = persisted(page)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert page.locator('#ebOrderScroll').evaluate("e=>e.scrollWidth<=e.clientWidth+1 && getComputedStyle(e.querySelector('.eb-order-row')).display==='grid'")
        assert_action_labels(page)
        field(page, 'id').focus()
        page.keyboard.press('Tab')
        assert page.evaluate("document.activeElement.dataset.f==='par' && document.activeElement.matches(':focus-visible')")
        assert persisted(page) == before
        page.locator('#ebOrderScroll').scroll_into_view_if_needed()
        settle(page)
        cdp = context.new_cdp_session(page)
        (out/'workbook-native-200.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot', {'format':'png','fromSurface':False,'captureBeyondViewport':False})['data']))
        assert not errors, errors
        assert_fixture_requests(context)
        observed['nativeZoom'] = ratio
    finally:
        context.close()
        shutil.rmtree(profile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--characterization-only', action='store_true')
    parser.add_argument('--portable', action='store_true')
    parser.add_argument('--native-zoom', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    before = hashes(args.root, args.portable)
    server = Server(('127.0.0.1', 0), partial(Quiet, directory=str(args.root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    cases = [('continuous-workbook', workbook_contract)]
    if not args.characterization_only:
        cases += [('empty-mobile-phase-add', empty_phase_add), ('integrated-tools-and-bases', tools_and_lot_bases),
                  ('matrix-boundaries', matrix_boundaries), ('legacy-six-grades', legacy_six_groups),
                  ('records-and-context', records_and_context), ('responsive-workbook', layouts)]
    report = {'root': str(args.root), 'source_sha256': before, 'cases': [], 'classification': 'NOT_RUN',
              'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'synthetic_setup':'Anonymous zero slots removed only in disposable layout scenario; explicit version-zero drafts created through Add buttons. Financial inputs/numeric expectations and canonical network fixtures preserved.'}
    entry = 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html' if args.portable else 'index.html'
    url = (args.root/entry).resolve().as_uri() if args.portable else f'http://127.0.0.1:{server.server_port}/{entry}'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            report['browser'] = browser.version
            for name, check in cases:
                case = {'name': name, 'classification': 'NOT_RUN', 'pageerrors': []}
                report['cases'].append(case)
                context = browser.new_context(viewport={'width':1440,'height':1000}, service_workers='block')
                context.add_init_script('window.__onbShown=true;')
                install_bootstrap(context)
                page = context.new_page()
                page.set_default_timeout(10000)
                page.on('pageerror', lambda error, case=case: case['pageerrors'].append(str(error)))
                page.on('dialog', lambda dialog: dialog.accept())
                try:
                    page.goto(url)
                    ready(page)
                    check(page, args.out, case)
                    assert not case['pageerrors'], case['pageerrors']
                    assert_fixture_requests(context)
                    case['classification'] = 'PASS'
                except AssertionError as error:
                    case.update(classification='PRODUCT_FAIL', error=str(error), trace=traceback.format_exc())
                    page.screenshot(path=str(args.out/f'{name}-failure.png'), full_page=True)
                except BaseException as error:
                    case.update(classification='TEST_HARNESS_FAIL', error=str(error), trace=traceback.format_exc())
                    page.screenshot(path=str(args.out/f'{name}-failure.png'), full_page=True)
                finally:
                    context.close()
            browser.close()
            if args.native_zoom and not args.characterization_only:
                case = {'name': 'native-200-percent', 'classification': 'NOT_RUN'}
                report['cases'].append(case)
                try:
                    native_zoom(pw, url, args.out, case)
                    case['classification'] = 'PASS'
                except AssertionError as error:
                    case.update(classification='PRODUCT_FAIL', error=str(error), trace=traceback.format_exc())
                except BaseException as error:
                    case.update(classification='ENVIRONMENT_ERROR', error=str(error), trace=traceback.format_exc())
            elif not args.characterization_only:
                report['cases'].append({'name': 'native-200-percent', 'classification': 'NOT_RUN', 'reason': 'Native zoom requested separately with --native-zoom'})
        assert before == hashes(args.root, args.portable), 'Candidate source changed during the focal; evidence must be rerun on frozen content'
        failed = [case for case in report['cases'] if case['classification'] not in ['PASS', 'NOT_RUN']]
        report['classification'] = failed[0]['classification'] if failed else 'PASS'
    except BaseException as error:
        report.update(classification='ENVIRONMENT_ERROR', error=str(error), trace=traceback.format_exc())
    finally:
        server.shutdown()
        (args.out/'workbook-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['classification'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

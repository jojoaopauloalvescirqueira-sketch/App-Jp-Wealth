#!/usr/bin/env python3
"""Runtime visual contract for Planning; other modules remain NOT_RUN.

The approved plan supplies the independent oracles, not the current CSS.
Fresh synthetic contexts reuse the existing bootstrap and Planning journeys.
Default execution is the complete initial matrix; --case regressions is focal.
"""
import argparse
import ast
import base64
from datetime import datetime, timezone
from functools import partial
from hashlib import sha256
import json
import math
from pathlib import Path
import shutil
import tempfile
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_fixture_server import BrowserFixtureServer
from browser_bootstrap_fixture import assert_fixture_requests
from notes_launcher_test import launch_options
import planning_proportions_test as planning
import planning_compact_table_test as compact
import planning_monthly_inline_test as inline
import planning_monthly_close_test as closure
from planning_parity_layout_test import financial

ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 2
EPSILON = .25  # Subpixel rounding only; clipping is not an alignment allowance.
GROUPS = [
    ('Contas', ['create', 'edit-selected']),
    ('Registros mensais', ['monthly', 'result', 'contribution', 'withdrawal']),
    ('Correções', ['contribution-history', 'pending-cost', 'withdrawal-history']),
    ('Consulta e relatórios', ['explain-goals', 'history', 'print']),
    ('Reinício', ['restart-selected']),
]
ACTION_ORDER = [action for _, actions in GROUPS for action in actions]
REQUIRED_LAYOUTS = ['sidebar', 'topbar', 'glass', 'submenu']
REQUIRED_THEMES = ['light', 'dark']
REQUIRED_SIZES = [(320, 700), (390, 844), (700, 600), (701, 601),
                  (1099, 720), (1100, 719), (1100, 720), (1101, 721),
                  (1440, 1000), (1440, 480)]
SOURCE_FILES = sorted(set(planning.SOURCES + [
    'tools/ui_visual_quality_test.py',
    'tools/quality_gate.py', 'AGENTS.md', 'docs/governance/UI-VISUAL-QUALITY.md',
    'docs/superpowers/plans/2026-10-21-planning-controls-visual-quality.md',
    'docs/superpowers/plans/2026-10-21-planning-consolidated-monthly-compact.md',
    'tools/planning_compact_table_test.py', 'tools/planning_monthly_inline_test.py',
    'tools/planning_monthly_close_test.py',
]))

# Reusable inner-content measurement, including text nodes and transformed SVG
# drawing coordinates. A centered outer box cannot conceal shifted ink/text.
CONTENT_GEOMETRY = r'''el=>{
 const box=r=>({left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height});
 const outer=box(el.getBoundingClientRect()),text=[],ink=[];
 const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
 while(walker.nextNode()){
   const n=walker.currentNode;if(!n.textContent.trim()||n.parentElement.closest('svg'))continue;
   const range=document.createRange();range.selectNodeContents(n);
   for(const r of range.getClientRects())if(r.width&&r.height)text.push(box(r));
 }
 for(const n of el.querySelectorAll('svg path,svg line,svg polyline,svg polygon,svg circle,svg rect')){
   const b=n.getBBox(),m=n.getScreenCTM();if(!m)continue;
   const pts=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
   const xs=pts.map(p=>p.x),ys=pts.map(p=>p.y);
   ink.push(box({left:Math.min(...xs),right:Math.max(...xs),top:Math.min(...ys),bottom:Math.max(...ys),width:Math.max(...xs)-Math.min(...xs),height:Math.max(...ys)-Math.min(...ys)}));
 }
 const union=rs=>rs.length?{left:Math.min(...rs.map(r=>r.left)),right:Math.max(...rs.map(r=>r.right)),top:Math.min(...rs.map(r=>r.top)),bottom:Math.max(...rs.map(r=>r.bottom))}:null;
 const style=getComputedStyle(el);
 return {outer,text:union(text),textRects:text,ink:union(ink),svg:el.querySelectorAll('svg').length,label:el.getAttribute('aria-label')||el.textContent.trim(),textAlign:style.textAlign,declaredLeftInset:parseFloat(style.paddingLeft)+parseFloat(style.borderLeftWidth)};
}'''


def now():
    return datetime.now(timezone.utc).isoformat()


def hashes():
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def setup(context, url):
    page = planning.setup(context, url)
    page._visual_errors = []
    page.on('pageerror', lambda error: page._visual_errors.append(str(error)))
    page.evaluate('''()=>{
      window.__visualWriterCalls=[];window.__visualCommandCalls=[];
      const writer=jpWealthPersistDocument,execute=JPWPlanning.commands.execute;
      jpWealthPersistDocument=function(...args){window.__visualWriterCalls.push({component:args[1]?.component||null});return writer.apply(this,args)};
      JPWPlanning.commands.execute=function(...args){window.__visualCommandCalls.push(args[0]);return execute.apply(this,args)};
    }''')
    return page


def start_write_probe(page):
    page.evaluate('window.__visualWriterCalls=[];window.__visualCommandCalls=[]')


def no_writes(page):
    observed = page.evaluate('({writer_calls:window.__visualWriterCalls,command_calls:window.__visualCommandCalls})')
    assert observed['writer_calls'] == [] and observed['command_calls'] == [], ('unconfirmed interaction called writer/command', observed)
    return observed


def centered(locator, kind='text', close=False):
    assert locator.count() == 1, ('exactly one control required', locator.count())
    data = locator.evaluate(CONTENT_GEOMETRY)
    outer, content = data['outer'], data[kind]
    assert outer['width'] > 0 and outer['height'] > 0, ('zero-size control', data)
    assert content, ('missing measurable ' + kind, data)
    if close:
        assert data['svg'] == 1, ('close requires symmetric SVG', data)
        assert abs(outer['width'] - 44) <= 1 and abs(outer['height'] - 44) <= 1, ('44px close', data)
        assert data['label'], ('close has no accessible name', data)
    data['delta'] = {axis: (content[a] + content[b] - outer[a] - outer[b]) / 2
                     for axis, a, b in [('x', 'left', 'right'), ('y', 'top', 'bottom')]}
    assert all(abs(value) <= TOLERANCE for value in data['delta'].values()), ('inner content center exceeds2CSSpx', data)
    assert content['left'] >= outer['left'] - EPSILON and content['right'] <= outer['right'] + EPSILON, ('content clipped horizontally', data)
    assert content['top'] >= outer['top'] - EPSILON and content['bottom'] <= outer['bottom'] + EPSILON, ('content clipped vertically', data)
    return data


def menu_geometry(page):
    menu = page.locator('#pl-stoikus-menu')
    assert menu.is_visible(), 'menu missing or hidden'
    data = menu.evaluate(r'''el=>{
      const r=n=>{const b=n.getBoundingClientRect();return {left:b.left,right:b.right,top:b.top,bottom:b.bottom,width:b.width,height:b.height}};
      const named=n=>n.getAttribute('aria-label')||(n.getAttribute('aria-labelledby')||'').split(' ').map(id=>document.getElementById(id)?.textContent||'').join(' ').trim()||n.querySelector('legend')?.textContent||'';
      return {box:r(el),viewport:[visualViewport?visualViewport.offsetLeft+visualViewport.width:innerWidth,visualViewport?visualViewport.offsetTop+visualViewport.height:innerHeight],layoutViewport:[innerWidth,innerHeight],scroll:[el.scrollHeight,el.clientHeight],overflow:getComputedStyle(el).overflowY,
        trigger:r(document.querySelector('#planning [data-pl-action=menu]')),
        rows:[...el.querySelectorAll('[data-pl-action]')].map(n=>({action:n.dataset.plAction,...r(n),textAlign:getComputedStyle(n).textAlign,tabIndex:n.tabIndex,disabled:n.disabled})),
        groups:[...el.querySelectorAll('[role=group],fieldset')].map(n=>({label:named(n),actions:[...n.querySelectorAll('[data-pl-action]')].map(b=>b.dataset.plAction)}))};
    }''')
    box, rows = data['box'], data['rows']
    assert len(rows) == 13, ('13 menu actions required', data)
    assert [row['action'] for row in rows] == ACTION_ORDER, ('approved reading order', data)
    assert [(group['label'], group['actions']) for group in data['groups']] == GROUPS, ('five approved named groups', data)
    assert 0 < box['width'] <= 320 + EPSILON, ('menu width limit', data)
    assert box['left'] >= 12 - EPSILON and box['right'] <= data['viewport'][0] - 12 + EPSILON, ('12px horizontal gutter', data)
    assert box['top'] >= 12 - EPSILON and box['bottom'] <= data['viewport'][1] - 12 + EPSILON, ('12px vertical gutter', data)
    trigger = data['trigger']
    assert box['bottom'] <= trigger['top'] + EPSILON or box['top'] >= trigger['bottom'] - EPSILON, ('menu covers trigger', data)
    if data['scroll'][0] > data['scroll'][1] + TOLERANCE:
        assert data['overflow'] in ['auto', 'scroll'], ('menu overflow inaccessible', data)
    text_lefts = []
    for index, row in enumerate(rows):
        assert row['width'] > 0 and row['height'] >= 44 - TOLERANCE, ('visible44px action', row)
        assert abs(row['left'] - rows[0]['left']) <= TOLERANCE and abs(row['right'] - rows[0]['right']) <= TOLERANCE, ('one full-width row per action', data)
        if index:
            assert row['top'] >= rows[index - 1]['bottom'] - EPSILON, ('rows wrap or overlap', data)
        item = menu.locator('[data-pl-action=' + row['action'] + ']')
        item.scroll_into_view_if_needed()
        measured = item.evaluate(CONTENT_GEOMETRY)
        assert measured['text'], ('menu text missing', row)
        assert measured['text']['left'] >= measured['outer']['left'] - EPSILON and measured['text']['right'] <= measured['outer']['right'] + EPSILON, ('menu text cut', measured)
        for line in measured['textRects']:
            assert abs(line['left'] - measured['outer']['left'] - measured['declaredLeftInset']) <= TOLERANCE, ('menu actual text does not start at left inset', measured)
        text_lefts.append(measured['text']['left'] - measured['outer']['left'])
    data['actual_text_left_insets'] = text_lefts
    assert max(text_lefts) - min(text_lefts) <= TOLERANCE, ('menu inner text left edges differ beyond2CSSpx', data)
    by_action = {row['action']: row for row in rows}
    gaps = [by_action[right]['top'] - by_action[left]['bottom'] for _, actions in GROUPS
            for left, right in zip(actions, actions[1:])]
    assert gaps and min(gaps) >= -EPSILON and max(gaps) - min(gaps) <= TOLERANCE, ('equivalent within-group row spacing differs', gaps)
    data['within_group_gaps'] = gaps
    return data


def focus_visible(locator):
    return locator.evaluate('''el=>{const s=getComputedStyle(el);return {
      active:document.activeElement===el,visible:el.matches(':focus-visible'),
      outline:s.outlineStyle,width:parseFloat(s.outlineWidth),shadow:s.boxShadow};}''')


def selector_geometry(page, scope, field_selector='select'):
    result = []
    selectors = page.locator(scope + ' ' + field_selector + ':visible')
    for index in range(selectors.count()):
        select = selectors.nth(index)
        select.evaluate("el=>el.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})")
        planning.settle(page)
        data = select.evaluate(r'''el=>{
          const r=el.getBoundingClientRect(),cuts=[];
          for(let p=el.parentElement;p&&p!==document.body;p=p.parentElement){
            const a=p.getBoundingClientRect(),s=getComputedStyle(p);
            if(['auto','scroll','hidden','clip'].includes(s.overflowX)&&(r.left<a.left-.25||r.right>a.right+.25))cuts.push('horizontal:'+p.className);
            if(['auto','scroll','hidden','clip'].includes(s.overflowY)&&(r.top<a.top-.25||r.bottom>a.bottom+.25))cuts.push('vertical:'+p.className);
          }
          return {id:el.id,label:el.getAttribute('aria-label')||el.closest('label')?.textContent.trim(),
            box:r.toJSON(),tag:el.tagName,options:el.options?.length||0,selected:el.selectedIndex??null,
            disabled:el.disabled,cuts,clientWidth:el.clientWidth,scrollWidth:el.scrollWidth};
        }''')
        assert data['box']['width'] > 0 and data['box']['height'] >= 44 - EPSILON, ('selector target geometry', data)
        if data['tag'] == 'SELECT':
            assert data['options'] > 0 and data['selected'] >= 0, ('native selector options/selection missing', data)
        assert not data['cuts'], ('selector cut by owner', data)
        result.append(data)
    return result


def menu_keyboard(page):
    trigger = page.locator('#planning [data-pl-action=menu]')
    menu = page.locator('#pl-stoikus-menu')
    if menu.is_visible():
        page.keyboard.press('Escape')
    trigger.focus()
    page.keyboard.press('Enter')
    enabled = menu.locator('[data-pl-action]:not(:disabled)')
    assert enabled.count() > 0, 'no keyboard menu actions'
    actions = enabled.evaluate_all('els=>els.map(el=>el.dataset.plAction)')
    assert enabled.first.evaluate('el=>el===document.activeElement'), 'Enter does not focus first action'
    states = []
    for index, action in enumerate(actions):
        if index:
            page.keyboard.press('ArrowDown')
        item = menu.locator('[data-pl-action=' + action + ']')
        state = focus_visible(item)
        assert state['active'] and state['visible'], ('keyboard focus missing', action, state)
        assert (state['outline'] != 'none' and state['width'] > 0) or state['shadow'] != 'none', ('focus indicator absent', action, state)
        states.append({'action': action, **state})
    page.keyboard.press('Home')
    assert enabled.first.evaluate('el=>el===document.activeElement'), 'Home not first'
    page.keyboard.press('End')
    assert enabled.last.evaluate('el=>el===document.activeElement'), 'End not last'
    if enabled.count() > 1:
        page.keyboard.press('ArrowUp')
        assert enabled.nth(enabled.count() - 2).evaluate('el=>el===document.activeElement'), 'ArrowUp not previous'
    page.keyboard.press('Escape')
    assert not menu.is_visible() and trigger.evaluate('el=>el===document.activeElement'), 'Escape focus return'
    trigger.press('Enter')
    page.keyboard.press('Tab')
    assert not menu.is_visible(), 'Tab keeps menu open'
    assert page.locator('#planning [data-pl-view=start]').evaluate('el=>el===document.activeElement'), 'Tab does not continue to first Planning tab'
    trigger.focus();trigger.press('Enter')
    page.keyboard.press('Shift+Tab')
    assert not menu.is_visible(), 'Shift+Tab keeps menu open'
    assert page.locator('#planning .pl-heading-actions [data-pl-action=print]').evaluate('el=>el===document.activeElement'), 'Shift+Tab does not return to preceding PDF control'
    trigger.click()
    page.locator('#planning h1').click()
    assert not menu.is_visible(), 'outside pointer does not close menu'
    trigger.focus();trigger.press('Enter')
    menu.locator('[data-pl-action=create]').press('Enter')
    assert page.locator('#planning .pl-dialog').is_visible(), 'menu Enter does not open action'
    assert not menu.is_visible(), 'selection/dialog keeps menu visible'
    page.keyboard.press('Escape')
    return states


def controls_geometry(page, scope='#planning dialog[open]'):
    """Audit actual contents after scrolling each control into its owner body."""
    dialogs = page.locator(scope)
    assert dialogs.count() > 0, 'required open dialog missing'
    controls = page.locator(scope + ' button:visible')
    assert controls.count() > 0, 'dialog has no measured controls'
    result = []
    for index in range(controls.count()):
        control = controls.nth(index)
        # Center in the real scroll owner: browser if-needed scrolling can leave
        # fractional pixels behind the owner edge after integer scroll rounding.
        control.evaluate("el=>el.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})")
        planning.settle(page)
        kind = 'ink' if control.locator('svg').count() else 'text'
        is_close = control.evaluate("el=>el.matches('.pl-close,.risk-close')")
        result.append(centered(control, kind, is_close))
        box = control.bounding_box()
        assert box and box['width'] >= 24 and box['height'] >= 24, ('nonzero accessible target', result[-1])
        cuts = control.evaluate(r'''el=>{
          const b=el.getBoundingClientRect(),bad=[];
          for(let p=el.parentElement;p&&p!==document.body;p=p.parentElement){
            const r=p.getBoundingClientRect(),s=getComputedStyle(p);
            if(['auto','scroll','hidden','clip'].includes(s.overflowX)&&(b.left<r.left-.25||b.right>r.right+.25))bad.push('horizontal:'+p.className);
            if(['auto','scroll','hidden','clip'].includes(s.overflowY)&&(b.top<r.top-.25||b.bottom>r.bottom+.25))bad.push('vertical:'+p.className);
          }return bad;
        }''')
        assert not cuts, ('control cut by its owner', result[-1], cuts)
    order = page.locator(scope).evaluate_all(r'''dialogs=>dialogs.map(d=>{
      const nodes=[...d.querySelectorAll('button,input,select,textarea,a[href],[tabindex]')].filter(n=>!n.disabled&&n.getBoundingClientRect().width&&n.getBoundingClientRect().height);
      return {count:nodes.length,positive:nodes.filter(n=>n.tabIndex>0).map(n=>n.id),
        footer:[...d.querySelectorAll('footer button')].filter(n=>n.getBoundingClientRect().width&&n.getBoundingClientRect().height).map(n=>({label:n.textContent.trim(),x:n.getBoundingClientRect().left,y:n.getBoundingClientRect().top}))};
    })''')
    for group in order:
        assert group['count'] > 0 and not group['positive'], ('DOM reading/keyboard order overridden', group)
        for left, right in zip(group['footer'], group['footer'][1:]):
            assert right['y'] >= left['y'] - TOLERANCE and (right['y'] > left['y'] + TOLERANCE or right['x'] >= left['x'] - TOLERANCE), ('footer visual reading order', group)
    return {'controls': result, 'reading_keyboard_order': order,
            'selectors': selector_geometry(page, scope),
            'inputs': selector_geometry(page, scope, 'input:not([type=checkbox])')}


def visual_journey(page, width, height):
    before = financial(page)
    start_write_probe(page)
    trigger = page.locator('#planning [data-pl-action=menu]')
    trigger.click()
    result = {'menu': menu_geometry(page), 'keyboard': menu_keyboard(page)}
    planning.open_form(page)
    result['form_empty'] = controls_geometry(page)
    assert result['form_empty']['selectors'], 'form selector coverage is empty'
    help_toggle = page.locator('#planning .pl-dialog .info-toggle').first
    help_toggle.click()
    controlled = help_toggle.get_attribute('aria-controls')
    assert controlled and page.locator('#' + controlled).is_visible(), 'Help disclosure unavailable'
    result['help_open'] = centered(help_toggle)
    help_toggle.click()
    assert not page.locator('#' + controlled).is_visible(), 'Help disclosure does not close'
    assert 'Comparar' in page.locator('#pl-native-openProfiles').inner_text(), 'Compare control missing'
    if page.locator('.pl-forecast-jump').is_visible():
        jump = page.locator('.pl-forecast-jump')
        result['forecast_jump'] = centered(jump)
        jump.click()
        assert page.locator('#pl-native-forecastArea').evaluate('el=>el===document.activeElement'), 'forecast jump focus destination'
    page.locator('#pl-native-openProfiles').click()
    result['profiles'] = controls_geometry(page, '#pl-native-profileDialog[open]')
    page.keyboard.press('Escape')
    assert page.locator('#pl-native-openProfiles').evaluate('el=>el===document.activeElement'), 'Profiles focus return'
    page.locator('#pl-native-stopOpen').click()
    result['stop'] = controls_geometry(page, '#pl-native-stopDialog[open]')
    page.keyboard.press('Escape')
    assert page.locator('#pl-native-stopOpen').evaluate('el=>el===document.activeElement'), 'Stop focus return'
    page.keyboard.press('Escape')
    assert financial(page) == before, 'visual interactions wrote financial state'
    result['writes_before_confirmation'] = no_writes(page)
    return result


def state_journey(page, out):
    # Existing real creation/review/cancel/edit/multiple-account and milestone
    # assertions are reused rather than duplicating their financial harness.
    result = {'existing_journey': planning.state_journey(page, out)}
    before = financial(page)
    start_write_probe(page)
    page.locator('[data-pl-view=consolidated]').click()
    page.locator('[data-pl-account]').select_option('')
    page.locator('[data-pl-view=start]').click()
    page.locator('[data-pl-action=configure]').click()
    result['multiple_account_choice'] = controls_geometry(page)
    account = page.evaluate('JPWPlanning.queries.snapshot().accounts[0].id')
    page.locator('[data-pl-configure-account]').select_option(account)
    page.locator('[data-pl-action=configure-edit]').click()
    result['edit_populated'] = controls_geometry(page)
    page.locator('#planning .pl-form [data-pl-submit]').click()
    assert page.locator('[data-pl-native-review]').is_visible(), 'review state missing'
    result['review'] = controls_geometry(page)
    page.locator('[data-pl-action=native-back]').click()
    result['review_back'] = controls_geometry(page)
    page.locator('#planning .pl-form>footer [data-pl-action=close]').click()
    assert financial(page) == before, 'edit review/back/cancel changed saved data'
    result['cancel_preserves_financial_state'] = True
    result['unconfirmed_writer_and_command_calls'] = no_writes(page)
    result['menu_lifecycle'] = menu_lifecycle(page)
    result['outside_dialog_controls'] = outside_dialog_controls(page)
    return result


def outside_dialog_controls(page):
    before = financial(page)
    start_write_probe(page)
    results = {}
    for view in ['consolidated', 'monthly']:
        page.locator('[data-pl-view=' + view + ']').click()
        buttons = page.locator('#planning :is(.pl-heading-actions,.pl-tabs,.pl-section-title,.pl-chart-toolbar,.pl-native-controls,.pl-month-controls) button:visible')
        assert buttons.count() > 0, ('no outside-dialog button coverage', view)
        measured = []
        for index in range(buttons.count()):
            control = buttons.nth(index)
            control.evaluate("el=>el.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})")
            planning.settle(page)
            measured.append(centered(control))
        selectors = selector_geometry(page, '#planning :is(.pl-toolbar,.pl-native-controls,.pl-chart-toolbar,.pl-native-summary-table .pl-section-title,.pl-month-controls)')
        assert selectors, ('no outside-dialog selector coverage', view)
        results[view] = {'buttons': measured, 'selectors': selectors}
    assert financial(page) == before, 'outside-dialog inspection changed financial state'
    results['unconfirmed_calls'] = no_writes(page)
    return results


def menu_lifecycle(page):
    saved = financial(page)
    start_write_probe(page)
    page.set_viewport_size({'width': 1440, 'height': 1000})
    trigger = page.locator('#planning [data-pl-action=menu]')
    trigger.click()
    before = menu_geometry(page)
    page.set_viewport_size({'width': 390, 'height': 844})
    planning.settle(page)
    resized = menu_geometry(page)
    assert before['viewport'] != resized['viewport'], 'resize stimulus did not happen'
    scroll = trigger.evaluate(r'''el=>{
      let owner=el.parentElement;
      while(owner&&!(owner.scrollHeight>owner.clientHeight+1&&['auto','scroll'].includes(getComputedStyle(owner).overflowY)))owner=owner.parentElement;
      owner=owner||document.scrollingElement;
      const before=owner.scrollTop,max=owner.scrollHeight-owner.clientHeight;
      owner.scrollTop=before<max?Math.min(max,before+30):Math.max(0,before-30);
      return {owner:owner.id||owner.className||owner.tagName,before,after:owner.scrollTop,max};
    }''')
    assert scroll['after'] != scroll['before'], ('scroll stimulus did not move an actual owner', scroll)
    planning.settle(page)
    scrolled = menu_geometry(page)
    page.evaluate('JPWPlanning.ui.deactivate()')
    assert not page.locator('#pl-stoikus-menu').is_visible(), 'deactivate leaves menu open'
    assert trigger.get_attribute('aria-expanded') == 'false', 'deactivate leaves trigger expanded'
    page.set_viewport_size({'width': 1440, 'height': 1000})
    page.evaluate('window.scrollTo(0,0)')
    assert financial(page) == saved, 'menu lifecycle changed saved financial state'
    return {'before': before, 'open_resize': resized, 'scroll_stimulus': scroll,
            'open_scroll': scrolled, 'deactivation_closed': True, 'unconfirmed_calls': no_writes(page)}


def rejected(action):
    try:
        action()
    except AssertionError as error:
        return {'rejected': True, 'measurement_failure': str(error)}
    raise AssertionError('deliberate violation incorrectly accepted by runtime oracle')


def counterproofs(browser, url, report):
    context = browser.new_context(viewport={'width': 700, 'height': 900}, service_workers='block')
    try:
        page = setup(context, url)
        before = financial(page)
        page.locator('#planning [data-pl-action=menu]').click()

        def shifted_menu():
            valid = menu_geometry(page)
            item = page.locator('#pl-stoikus-menu [data-pl-action=create]')
            original = item.inner_html()
            try:
                item.evaluate("el=>{const s=document.createElement('span');s.textContent=el.textContent;el.replaceChildren(s);s.style.cssText='display:inline-block;transform:translateX(5px)'}")
                invalid = rejected(lambda: menu_geometry(page))
            finally:
                item.evaluate('(el,html)=>el.innerHTML=html', original)
            return {'positive_control': valid, 'shifted_content': invalid,
                    'restored_positive_control': menu_geometry(page)}

        record(report, 'counterproof-menu-inner-left', shifted_menu, page,
               criteria='same13realrows,5pxtranslatedtextrejecteddespiteunchangedouterbox')

        def wrapping_menu():
            valid = menu_geometry(page)
            menu = page.locator('#pl-stoikus-menu')
            original = menu.get_attribute('style') or ''
            try:
                menu.evaluate("el=>el.style.setProperty('width','322px','important')")
                invalid = rejected(lambda: menu_geometry(page))
            finally:
                menu.evaluate('(el,style)=>el.setAttribute("style",style)', original)
            return {'positive_control': valid, 'overwide_menu': invalid}

        record(report, 'counterproof-menu-width', wrapping_menu, page,
               criteria='samegeometryoraclerejects322pxmenuagainstmax320')
        page.locator('#planning [data-pl-action=menu]').click()
        planning.open_form(page)

        def shifted_text():
            jump = page.locator('.pl-forecast-jump')
            valid = centered(jump)
            original = jump.inner_html()
            try:
                jump.evaluate("el=>{const s=document.createElement('span');s.textContent=el.textContent;el.replaceChildren(s);s.style.cssText='display:inline-block;transform:translateY(-5px)'}")
                invalid = rejected(lambda: centered(jump))
            finally:
                jump.evaluate('(el,html)=>el.innerHTML=html', original)
            return {'positive_control': valid, 'shifted_text': invalid,
                    'restored_positive_control': centered(jump)}

        record(report, 'counterproof-forecast-inner-text', shifted_text, page,
               criteria='sameactualtextRangeoraclerejects5pxinnertranslation')

        def shifted_svg():
            close = page.locator('#planning .pl-dialog .pl-close')
            valid = centered(close, 'ink', True)
            shapes = close.locator('svg path,svg line,svg polyline,svg polygon,svg circle,svg rect')
            assert shapes.count() > 0, 'no SVG drawing to test'
            originals = shapes.evaluate_all("els=>els.map(el=>el.getAttribute('transform'))")
            try:
                shapes.evaluate_all("els=>els.forEach(el=>el.setAttribute('transform','translate(5 0) '+(el.getAttribute('transform')||'')))")
                invalid = rejected(lambda: centered(close, 'ink', True))
            finally:
                shapes.evaluate_all('(els,values)=>els.forEach((el,i)=>values[i]===null?el.removeAttribute("transform"):el.setAttribute("transform",values[i]))', originals)
            return {'positive_control': valid, 'translated_drawing': invalid,
                    'restored_positive_control': centered(close, 'ink', True)}

        record(report, 'counterproof-svg-drawing', shifted_svg, page,
               criteria='sameSVGdrawingbbox/screenCTMoraclerejects5unittranslation')
        assert financial(page) == before, 'counterproofs changed financial state'
        assert_fixture_requests(context)
    finally:
        context.close()


def reset_transients(page):
    for _ in range(3):
        page.keyboard.press('Escape')
    menu = page.locator('#pl-stoikus-menu')
    if menu.is_visible():
        page.locator('#planning [data-pl-action=menu]').click()


def matrix(browser, url, report):
    context = browser.new_context(viewport={'width': 1440, 'height': 1000},
                                  service_workers='block', reduced_motion='reduce')
    try:
        page = setup(context, url)
        for width, height in planning.SIZES:
            page.set_viewport_size({'width': width, 'height': height})
            for layout in planning.LAYOUTS:
                for theme in planning.THEMES:
                    reset_transients(page)
                    page.evaluate('layout=>mountNavigationLayout(layout)', layout)
                    page.evaluate('theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
                    record(report, f'matrix-{layout}-{theme}-{width}x{height}',
                           lambda: visual_journey(page, width, height), page,
                           criteria='menu/keyboard/focus/text/SVG/clipping/form/Profiles/Stop/no-write',
                           layout=layout, theme=theme, viewport=[width, height], reduced_motion=True,
                           states=['empty', 'create', 'Profiles', 'Stop', 'cancel'])
        reset_transients(page)
        page.set_viewport_size({'width': 1440, 'height': 1000})
        record(report, 'states-confirmation-review-edit-multiple-cancel',
               lambda: state_journey(page, Path(report['out'])), page,
               criteria='existingrealcreationandfinancialmilestonesplusactualcontrolsgeometry',
               states=['populated', 'create-confirm', 'review', 'back', 'edit', 'multiple', 'cancel'])
        assert_fixture_requests(context)
    finally:
        context.close()


def touch(browser, url, report):
    context = browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True,
                                  is_mobile=True, service_workers='block', reduced_motion='reduce')
    try:
        page = setup(context, url)

        def journey():
            before = financial(page)
            start_write_probe(page)
            page.locator('#planning [data-pl-action=menu]').tap()
            menu = menu_geometry(page)
            page.locator('#pl-stoikus-menu [data-pl-action=create]').tap()
            assert not page.locator('#pl-stoikus-menu').is_visible(), 'touch selection keeps menu open'
            form = controls_geometry(page)
            page.locator('.pl-forecast-jump').tap()
            assert page.locator('#pl-native-forecastArea').evaluate('el=>el===document.activeElement'), 'touch jump focus destination'
            page.locator('#planning .pl-close').tap()
            assert financial(page) == before, 'touch/cancel wrote data'
            return {'menu': menu, 'form': form, 'synthetic_touch': True, 'unconfirmed_calls': no_writes(page)}

        record(report, 'touch-390x844', journey, page,
               criteria='realChromiumtouchmenu/jump/close44px/cancel/nofinancialwrite',
               viewport=[390, 844], reduced_motion=True)
        assert_fixture_requests(context)
    finally:
        context.close()


def native_zoom(pw, url, report, legacy=True):
    profile = Path(tempfile.mkdtemp(prefix='visual-native200-', dir=report['out']))
    (profile / 'Default').mkdir()
    (profile / 'Default/Preferences').write_text(json.dumps({'partition': {
        'default_zoom_level': {'x': math.log(2) / math.log(1.2)}}}))
    options = launch_options()
    options.update(headless=False, no_viewport=True, args=['--window-size=1440,1000'],
                   service_workers='block', reduced_motion='reduce')
    try:
        context = pw.chromium.launch_persistent_context(str(profile), **options)
        try:
            page = setup(context, url)
            zoom = page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
            assert abs(zoom['outer'] / zoom['inner'] - 2) < .01 and zoom['css'] == '1', ('native200%notCSSzoom', zoom)
            report['native_zoom'] = zoom
            for layout in planning.LAYOUTS:
                for theme in planning.THEMES:
                    reset_transients(page)
                    page.evaluate('layout=>mountNavigationLayout(layout)', layout)
                    page.evaluate('theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
                    width, height = page.evaluate('[innerWidth,innerHeight]')
                    if legacy:
                        record(report, f'native200-{layout}-{theme}', lambda: visual_journey(page, width, height), page,
                               criteria='browsernative200%/menu/text/SVG/focus/dialogs',
                               layout=layout, theme=theme, viewport=[width, height], native_zoom=200)
                    else:
                        compact.native_case(page, report, __import__(__name__), layout, theme)
            assert_fixture_requests(context)
        finally:
            context.close()
    finally:
        shutil.rmtree(profile)


def required_ids(selection):
    if selection == 'closure-regressions':
        return closure.required_ids('regressions')
    if selection in ['compact-regressions', 'compact']:
        return compact.required_ids('all' if selection == 'compact' else 'regressions')
    if selection == 'inline-regressions':
        return inline.required_ids('regressions')
    ids = ['regression-stoikus-vertical-groups', 'regression-forecast-inner-center', 'regression-close-svg-ink-center']
    if selection == 'all':
        ids += [f'matrix-{layout}-{theme}-{width}x{height}' for width, height in planning.SIZES
                for layout in planning.LAYOUTS for theme in planning.THEMES]
        ids += [f'native200-{layout}-{theme}' for layout in planning.LAYOUTS for theme in planning.THEMES]
        ids += ['states-confirmation-review-edit-multiple-cancel', 'touch-390x844',
                'counterproof-menu-inner-left', 'counterproof-menu-width', 'counterproof-forecast-inner-text',
                'counterproof-svg-drawing', 'coverage-missing-and-zero-rejected']
        ids += compact.required_ids('all')
        ids += inline.required_ids('all')
        ids += closure.required_ids('all')
    return ids


def validate_coverage(cases, expected):
    assert expected and cases, 'empty coverage is invalid'
    actual = [case['id'] for case in cases]
    assert len(actual) == len(set(actual)), ('duplicate case identity', actual)
    assert set(actual) == set(expected), ('missing/unexpected cases', sorted(set(expected) - set(actual)), sorted(set(actual) - set(expected)))
    assert all(case['classification'] in ['PASS', 'PRODUCT_FAIL', 'TEST_HARNESS_FAIL'] for case in cases), 'unexecuted/unknown classification'
    return {'executed': len(actual), 'required': len(expected), 'unique': True}


def coverage_counterproof():
    valid = [{'id': 'positive', 'classification': 'PASS'}]
    return {'positive': validate_coverage(valid, ['positive']),
            'zero_cases': rejected(lambda: validate_coverage([], ['positive'])),
            'zero_expected': rejected(lambda: validate_coverage(valid, [])),
            'missing': rejected(lambda: validate_coverage(valid, ['positive', 'missing'])),
            'not_run': rejected(lambda: validate_coverage([{'id': 'positive', 'classification': 'NOT_RUN'}], ['positive'])),
            'gate_wiring': gate_counterproof(),
            'matrix_dimensions': matrix_counterproof()}


def validate_matrix_config(layouts, themes, sizes):
    assert layouts == REQUIRED_LAYOUTS, ('four approved layout identities required', layouts)
    assert themes == REQUIRED_THEMES, ('both approved themes required', themes)
    assert sizes and all(isinstance(size, (list, tuple)) and len(size) == 2 and all(isinstance(value, int) and value > 0 for value in size) for size in sizes), ('nonempty valid viewport pairs required', sizes)
    assert len(sizes) == len(REQUIRED_SIZES) and set(map(tuple, sizes)) == set(REQUIRED_SIZES), ('approved320..1440/short/boundary viewports required', sizes)
    return {'layouts': 4, 'themes': 2, 'viewports': len(sizes), 'native_zoom': 200}


def matrix_counterproof():
    return {'positive': validate_matrix_config(planning.LAYOUTS, planning.THEMES, planning.SIZES),
            'empty_layouts': rejected(lambda: validate_matrix_config([], planning.THEMES, planning.SIZES)),
            'empty_themes': rejected(lambda: validate_matrix_config(planning.LAYOUTS, [], planning.SIZES)),
            'empty_sizes': rejected(lambda: validate_matrix_config(planning.LAYOUTS, planning.THEMES, [])),
            'missing_short_size': rejected(lambda: validate_matrix_config(planning.LAYOUTS, planning.THEMES, planning.SIZES[:-1]))}


def tier_entries(tree, tier):
    assignments = {node.targets[0].id: node.value for node in tree.body
                   if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)}

    def expand(node, seen):
        if isinstance(node, ast.Name):
            assert node.id not in seen and node.id in assignments, ('unresolved/cyclic tier', node.id)
            return expand(assignments[node.id], seen | {node.id})
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return expand(node.left, seen) + expand(node.right, seen)
        assert isinstance(node, (ast.Tuple, ast.List)), ('unsupported tier expression', ast.dump(node))
        return list(node.elts)

    return expand(ast.Name(id=tier), set())


def validate_gate_source(source):
    """Parse declarations only; importing the runner could execute its CLI."""
    tree = ast.parse(source)
    tiers = {tier: tier_entries(tree, tier) for tier in ['STANDARD', 'FULL']}
    expected = ast.parse("[sys.executable, 'tools/ui_visual_quality_test.py', '--out', full_evidence('ui-visual-quality')]", mode='eval').body
    result = {}
    for tier, entries in tiers.items():
        assert all(isinstance(entry, ast.Tuple) and len(entry.elts) == 2 and isinstance(entry.elts[0], ast.Constant) and isinstance(entry.elts[0].value, str) for entry in entries), ('invalid gate entry', tier)
        ids = [entry.elts[0].value for entry in entries]
        assert len(ids) == len(set(ids)), ('duplicate gate identity', tier)
        selected = [entry for entry in entries if entry.elts[0].value == 'ui-visual-quality']
        assert len(selected) == 1, ('visual check must run exactly once', tier, len(selected))
        assert ast.dump(selected[0].elts[1]) == ast.dump(expected), ('visual gate must invoke default complete CLI and unique output', tier)
        result[tier] = {'entries': len(ids), 'visual_entries': len(selected)}
    assert len(tiers['FULL']) == 96, ('95 existing checks plus visual check required', len(tiers['FULL']))
    return result


def gate_counterproof():
    source = (ROOT / 'tools/quality_gate.py').read_text()
    valid = validate_gate_source(source)

    class RemoveVisual(ast.NodeTransformer):
        def visit_Tuple(self, node):
            if node.elts and isinstance(node.elts[0], ast.Constant) and node.elts[0].value == 'ui-visual-quality':
                return None
            return self.generic_visit(node)

    removed = RemoveVisual().visit(ast.parse(source))
    remaining = tier_entries(removed, 'FULL')
    assert len(remaining) == 95, 'negative fixture must retain all95 other entries'
    focal = ast.parse(source)
    entry = next(item for item in tier_entries(focal, 'STANDARD') if item.elts[0].value == 'ui-visual-quality')
    entry.elts[1].elts.extend([ast.Constant(value='--case'), ast.Constant(value='regressions')])
    return {'positive': valid,
            'removed_new_entry_other95_preserved': rejected(lambda: validate_gate_source(ast.unparse(removed))),
            'focal_instead_of_default': rejected(lambda: validate_gate_source(ast.unparse(focal)))}


def record(report, case_id, action, page=None, criteria=None, **metadata):
    case = {'id': case_id, 'classification': 'NOT_RUN', 'criteria': criteria or case_id,
            'started_at': now(), **metadata}
    report['cases'].append(case)
    error_start = len(page._visual_errors) if page else 0
    try:
        case['evidence'] = action()
        if page:
            assert not page._visual_errors[error_start:], ('runtime page errors', page._visual_errors[error_start:])
        case['classification'] = 'PASS'
    except AssertionError as error:
        case.update(classification='PRODUCT_FAIL', error=str(error), trace=traceback.format_exc())
    except Exception as error:
        case.update(classification='TEST_HARNESS_FAIL', error=str(error), trace=traceback.format_exc())
    case['finished_at'] = now()
    if page:
        case['page_errors'] = page._visual_errors[error_start:]
    if page and case['classification'] != 'PASS':
        try:
            cdp = page.context.new_cdp_session(page)
            (Path(report['out']) / (case_id + '.png')).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot', {
                'format': 'png', 'fromSurface': True, 'captureBeyondViewport': False})['data']))
            cdp.detach()
        except Exception as error:
            case['screenshot_error'] = str(error)
    print(case['classification'] + ' ' + case_id, flush=True)


def regressions(browser, url, report):
    context = browser.new_context(viewport={'width': 700, 'height': 900}, service_workers='block')
    try:
        page = setup(context, url)
        before = financial(page)
        page.locator('#planning [data-pl-action=menu]').click()
        record(report, 'regression-stoikus-vertical-groups', lambda: menu_geometry(page), page,
               criteria='approved13actions/fivegroups/vertical/left/max320/gutter12/nooverlap')
        page.locator('#planning [data-pl-action=menu]').click()
        planning.open_form(page)
        record(report, 'regression-forecast-inner-center', lambda: centered(page.locator('.pl-forecast-jump')), page,
               criteria='actualtextRangecenter<=2CSSpxonbothaxes')
        record(report, 'regression-close-svg-ink-center', lambda: centered(page.locator('#planning .pl-dialog .pl-close'), 'ink', True), page,
               criteria='symmetricSVGinkcenter<=2CSSpxand44pxtarget')
        assert financial(page) == before, 'visual regressions wrote financial state'
        assert_fixture_requests(context)
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=['all', 'regressions', 'compact-regressions', 'compact', 'inline-regressions', 'closure-regressions'], default='all')
    parser.add_argument('--out', type=Path, default=ROOT / 'tools/.artifacts' / ('ui-visual-quality-' + datetime.now().strftime('%Y%m%dT%H%M%S%f')))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    report = {'classification': 'NOT_RUN', 'started_at': now(), 'out': str(args.out),
              'source_sha256': hashes(), 'cases': [], 'selection': args.case,
              'required_case_ids': required_ids(args.case),
              'test_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'matrix': {'layouts': planning.LAYOUTS, 'themes': planning.THEMES,
                         'sizes': planning.SIZES, 'native_zoom': 200, 'reduced_motion': True},
              'tolerance_css_px': TOLERANCE, 'oracle': 'approved planning-controls-visual-quality plan',
              'limits': {'other_modules': 'NOT_RUN', 'human_acceptance': 'NOT_RUN', 'Safari': 'NOT_RUN',
                         'screen_reader': 'NOT_RUN', 'physical_touch': 'NOT_RUN',
                         'native_select_popup_ink': 'NOT_RUN; closed native selector/input boxes, options and reachability measured'}}
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(planning.Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        report['matrix_config_validation'] = validate_matrix_config(planning.LAYOUTS, planning.THEMES, planning.SIZES)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            report['browser'] = browser.version
            url = f'http://127.0.0.1:{server.server_port}/index.html'
            if args.case in ['all', 'regressions']:
                regressions(browser, url, report)
            if args.case in ['all', 'compact', 'compact-regressions']:
                compact.regressions(browser, url, report, __import__(__name__))
            if args.case in ['all','inline-regressions']:
                inline.regressions(browser,url,report,__import__(__name__))
            if args.case in ['all','closure-regressions']:
                closure.regressions(browser,url,report,__import__(__name__))
            if args.case == 'all':
                closure.counterproofs(browser,url,report,__import__(__name__))
                closure.matrix(browser,url,report,__import__(__name__))
                inline.counterproofs(browser,url,report,__import__(__name__))
                counterproofs(browser, url, report)
                matrix(browser, url, report)
                touch(browser, url, report)
            if args.case in ['all', 'compact']:
                compact.counterproofs(browser, url, report, __import__(__name__))
                compact.matrix(browser, url, report, __import__(__name__))
                compact.touch(browser, url, report, __import__(__name__))
            browser.close()
            if args.case in ['all', 'compact']:
                native_zoom(pw, url, report, legacy=args.case == 'all')
            if args.case == 'all':
                # Keep the previous native cases' empty synthetic context intact;
                # the compact financial scenarios get their own disposable one.
                native_zoom(pw, url, report, legacy=False)
                closure.native_zoom(pw,url,report,__import__(__name__))
                record(report, 'coverage-missing-and-zero-rejected', coverage_counterproof,
                       criteria='nonempty/exactrequiredIDs/executedonly;negativefixturesusesamecoveragevalidator')
        report['coverage'] = validate_coverage(report['cases'], report['required_case_ids'])
        failures = [case for case in report['cases'] if case['classification'] != 'PASS']
        report['classification'] = failures[0]['classification'] if failures else 'PASS'
    except AssertionError as error:
        report.update(classification='TEST_HARNESS_FAIL', error=str(error), trace=traceback.format_exc())
    except Exception as error:
        report.update(classification='ENVIRONMENT_ERROR', error=str(error), trace=traceback.format_exc())
    finally:
        server.shutdown()
        report['source_unchanged'] = report['source_sha256'] == hashes()
        if not report['source_unchanged']:
            report['classification'] = 'TEST_HARNESS_FAIL'
        report['finished_at'] = now()
        (args.out / 'ui-visual-quality-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(report['classification'] + ' cases=' + str(len(report['cases'])))
    return 0 if report['classification'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())

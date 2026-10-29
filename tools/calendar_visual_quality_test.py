"""Additive Calendar/Agenda visual contract; fresh synthetic browser profiles only.

Approved source: docs/superpowers/plans/2026-10-23-calendar-agenda.md and
docs/governance/UI-VISUAL-QUALITY.md. The shared verifier supplies the 2 CSS px
inner-ink oracle and result classification. No current CSS is an expectation.
"""
from datetime import datetime, timezone
import base64
import json
import math
from pathlib import Path
import re
import shutil
import tempfile

from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from apple_experience_test import CONTRAST
from calendar_agenda_test import calendar_packet
from notes_launcher_test import launch_options
from playwright.sync_api import expect
from calendar_economic_table_contract import assert_layout, controls

LAYOUTS = ('sidebar', 'topbar', 'glass', 'submenu')
THEMES = ('light', 'dark')
SIZES = ((320, 700), (390, 844), (1440, 900), (1440, 480))
NOW = datetime(2026, 10, 23, 12, tzinfo=timezone.utc)
TOLERANCE = 2
EPSILON = .25
DIALOG = '#calendarDialog'
PANEL = DIALOG + ' .calendar-panel'


def required_ids():
    return ([f'calendar-{layout}-{theme}-{width}x{height}' for width, height in SIZES
             for layout in LAYOUTS for theme in THEMES]
            + [f'calendar-native200-{layout}-{theme}' for layout in LAYOUTS for theme in THEMES]
            + ['calendar-counterproof-' + name for name in
               ('inner-svg', 'economic-dot', 'overflow', 'personal-only-economic-dot',
                'marker-appearance', 'today-selection', 'vertical-clipping', 'focus-return')])


def prepare_context(context, url):
    """Install transport/data fixtures before loading the actual product scripts."""
    install_bootstrap(context)
    calendar_packet(context)
    context.add_init_script('window.__onbShown=true;')
    page = context.new_page()
    page.clock.set_fixed_time(NOW)
    page._visual_errors = []
    page.on('pageerror', lambda error: page._visual_errors.append(str(error)))
    page.goto(url, wait_until='load')
    wait_bootstrap(page)
    page.evaluate('closeModal()')
    assert page.evaluate("typeof window.JPWCalendar?.open === 'function'"), 'Calendar API missing'
    assert page.evaluate("typeof window.JPWAgenda?.commands?.save === 'function'"), 'Agenda writer missing'
    seed_personal(page)
    assert not page._visual_errors, ('Calendar bootstrap/runtime errors', page._visual_errors)
    return page


def seed_personal(page):
    """Only these fresh contexts receive confirmed synthetic agenda writes."""
    result = page.evaluate('''()=>{
      S=structuredClone(DEFAULTS);S.onboarding.done=true;
      S.calendarVisualProbe='SYN_CALENDAR_VISUAL';
      if(save()!==true)throw Error('Synthetic base save refused');
      JPWAgenda.commands.resetContext();
      const receipts=[];
      for(const date of ['2026-10-23','2026-10-24']){
        const prepared=JPWAgenda.queries.prepare({id:null});
        if(!prepared.ok)throw Error('Synthetic agenda prepare refused: '+JSON.stringify(prepared));
        const receipt=JPWAgenda.commands.save({token:prepared.token,input:{kind:'task',
          title:'SYN Visual task '+date,notes:'Synthetic calendar visual observation',
          date,allDay:true,startTime:'',endDate:date,endTime:'',timeZone:'UTC'}});
        if(!receipt.ok||receipt.status!=='CONFIRMED')throw Error('Synthetic agenda save refused: '+JSON.stringify(receipt));
        receipts.push(receipt.status);
      }
      return {receipts,items:JPWAgenda.queries.snapshot().items.length};
    }''')
    assert result == {'receipts': ['CONFIRMED', 'CONFIRMED'], 'items': 2}, result


def start_probe(page):
    page.evaluate('''()=>{
      window.__calendarVisualWrites=[];window.__calendarVisualWriterCalls=[];
      if(window.__calendarVisualInstrumented)return;
      window.__calendarVisualInstrumented=true;
      for(const method of ['setItem','removeItem','clear']){
        const original=Storage.prototype[method];
        Storage.prototype[method]=function(...args){
          __calendarVisualWrites.push({method,area:this===localStorage?'local':'session',key:args[0]||null});
          return original.apply(this,args);
        };
      }
      const writer=jpWealthPersistDocument;
      jpWealthPersistDocument=function(...args){
        __calendarVisualWriterCalls.push({component:args[1]?.component||null});
        return writer.apply(this,args);
      };
    }''')
    return snapshot(page)


def snapshot(page):
    return page.evaluate('''()=>({state:JSON.stringify(S),
      local:JSON.stringify(Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))),
      session:JSON.stringify(Object.fromEntries(Object.keys(sessionStorage).sort().map(k=>[k,sessionStorage.getItem(k)])))})''')


def unchanged(page, before):
    after = snapshot(page)
    calls = page.evaluate('({storage:__calendarVisualWrites,writer:__calendarVisualWriterCalls})')
    assert after == before, ('Calendar visual reads changed state/storage',
                             [key for key in before if before[key] != after[key]], calls)
    assert calls == {'storage': [], 'writer': []}, ('Calendar visual read attempted a write', calls)
    return {'state_and_storage': 'byte-exact', 'storage_calls': 0, 'writer_calls': 0}


def reveal_launcher(page):
    if not page.locator('#headerCalendarBtn').is_visible():
        toggle = page.locator('[data-shell-menu-toggle]').first
        assert toggle.is_visible(), 'No visible route to the calendar launcher'
        toggle.click()
    expect(page.locator('#headerCalendarBtn')).to_be_visible()


def header_geometry(page, visual):
    reveal_launcher(page)
    calendar = page.locator('#headerCalendarBtn')
    data = visual.centered(calendar, 'ink', True)
    adjacent = calendar.evaluate('''e=>{
      const b=e.getBoundingClientRect(),bell=document.getElementById('headerNotificationsBtn'),n=bell.getBoundingClientRect(),s=e.querySelector('svg').getBoundingClientRect();
      return {domAdjacent:e.nextElementSibling===bell,calendar:b.toJSON(),bell:n.toJSON(),svg:s.toJSON(),
        svgHidden:e.querySelector('svg').getAttribute('aria-hidden'),label:e.getAttribute('aria-label'),
        controls:e.getAttribute('aria-controls'),popup:e.getAttribute('aria-haspopup')};
    }''')
    a, b, svg = adjacent['calendar'], adjacent['bell'], adjacent['svg']
    assert adjacent['domAdjacent'], ('Calendar must immediately precede the bell in reading/keyboard order', adjacent)
    assert a['right'] <= b['left'] + EPSILON, ('Calendar must be visually left of the bell', adjacent)
    assert abs((a['top'] + a['bottom'] - b['top'] - b['bottom']) / 2) <= TOLERANCE, ('Calendar and bell need the same visual row', adjacent)
    assert abs(svg['width'] - 20) <= EPSILON and abs(svg['height'] - 20) <= EPSILON, ('20px launcher SVG', adjacent)
    assert adjacent['label'] and adjacent['controls'] == 'calendarDialog' and adjacent['popup'] == 'dialog', adjacent
    assert adjacent['svgHidden'] == 'true', ('Decorative launcher SVG', adjacent)
    return {'ink': data, 'adjacency': adjacent}


def open_calendar(page):
    reveal_launcher(page)
    page.locator('#headerCalendarBtn').click()
    expect(page.locator(DIALOG)).to_be_visible()
    expect(page.locator(PANEL + ' [data-calendar-date="2026-10-23"] .calendar-economic-dot')).to_have_count(1)
    expect(page.locator(PANEL + ' [data-calendar-date="2026-10-23"] .calendar-personal-dot')).to_have_count(1)


def focus_return(page):
    """Judge the visible return path, independently of product focus helpers."""
    page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
    data = page.evaluate('''()=>{
      const selectors=['#headerCalendarBtn','[data-shell-menu-toggle]','#brandHomeBtn'];
      const available=e=>{
        if(!e||!e.isConnected||e.matches(':disabled')||e.closest('[inert]')||e.tabIndex<0)return false;
        const r=e.getBoundingClientRect(),s=getComputedStyle(e);
        return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility==='visible';
      };
      const options=selectors.map(selector=>({selector,node:[...document.querySelectorAll(selector)].find(available)}));
      const expected=options.find(option=>option.node),active=document.activeElement;
      return {expected:expected?.selector||null,actual:active?.id||active?.tagName||null,
        actualAvailable:available(active),matches:!!expected&&active===expected.node,
        available:options.filter(option=>option.node).map(option=>option.selector)};
    }''')
    assert data['expected'] and data['matches'] and data['actualAvailable'], ('Calendar close must return focus to its visible launcher or visible shell fallback', data)
    return data


def marker_geometry(page):
    """Red dots follow economic data, and their x center follows the numeral."""
    data = page.locator(PANEL + ' .calendar-grid').evaluate('''grid=>{
      const rect=n=>n.getBoundingClientRect().toJSON();
      const dot=n=>{const s=getComputedStyle(n);let opacity=1;
        for(let p=n;p;p=p.parentElement)opacity*=parseFloat(getComputedStyle(p).opacity);
        return {...rect(n),color:s.backgroundColor,opacity,display:s.display,visibility:s.visibility};};
      return [...grid.querySelectorAll('[data-calendar-date]')].map(cell=>({
        date:cell.dataset.calendarDate,cell:rect(cell),label:cell.getAttribute('aria-label'),
        selected:cell.getAttribute('aria-selected')==='true',
        number:rect(cell.querySelector('.calendar-day-number')),
        economic:[...cell.querySelectorAll('.calendar-economic-dot')].map(dot),
        personal:[...cell.querySelectorAll('.calendar-personal-dot')].map(dot)}));
    }''')
    assert data, 'Calendar marker population must be nonempty'
    red_dates = [row['date'] for row in data if row['economic']]
    blue_dates = [row['date'] for row in data if row['personal']]
    assert red_dates == ['2026-10-23', '2026-10-25'], ('Only default high-impact economic fixture days get a red dot', red_dates)
    assert blue_dates == ['2026-10-23', '2026-10-24'], ('Confirmed synthetic tasks get personal dots', blue_dates)
    for row in data:
        assert len(row['economic']) <= 1 and len(row['personal']) <= 1, ('One marker per kind/day', row)
        for kind in ('economic', 'personal'):
            for dot in row[kind]:
                color = rgba(dot['color'])
                assert dot['width'] > 0 and dot['height'] > 0 and dot['opacity'] > 0 and color[3] > 0, ('Marker must be rendered visibly', kind, row)
                assert dot['display'] != 'none' and dot['visibility'] == 'visible', ('Hidden marker', kind, row)
                assert dot['left'] >= row['cell']['left'] - EPSILON and dot['right'] <= row['cell']['right'] + EPSILON and dot['top'] >= row['number']['bottom'] - EPSILON and dot['bottom'] <= row['cell']['bottom'] + EPSILON, ('Marker outside its day/below-numeral area', kind, row)
                if kind == 'economic':
                    assert color[0] > color[1] + 10 and color[0] > color[2] + 10, ('Economic marker must remain red', row)
                elif not row['selected']:
                    assert color[2] > color[0] + 10 and color[2] > color[1] + 10, ('Unselected personal marker must remain blue', row)
        if row['economic'] and row['personal']:
            red, blue = row['economic'][0], row['personal'][0]
            assert red['right'] <= blue['left'] + EPSILON or blue['right'] <= red['left'] + EPSILON, ('Economic and personal markers overlap', row)
            # A selected blue day may use a contrast variant for its personal dot.
            assert red['color'] != blue['color'], ('Both marker kinds need distinct visible treatment', row)
        for dot in row['economic']:
            number = row['number']
            delta = (dot['left'] + dot['right'] - number['left'] - number['right']) / 2
            assert abs(delta) <= TOLERANCE, ('Economic dot not centered under numeral, including a simultaneous personal dot', row, delta)
            assert dot['top'] >= number['bottom'] - EPSILON and dot['bottom'] <= row['cell']['bottom'] + EPSILON, ('Economic dot clipped/over numeral', row)
    day23 = next(row for row in data if row['date'] == '2026-10-23')
    assert '2 eventos econômicos' in day23['label'], ('Filtered economic count missing from ARIA label', day23)
    assert 'agenda' in day23['label'], ('Personal state missing from ARIA label', day23)
    day24 = next(row for row in data if row['date'] == '2026-10-24')
    assert 'econômico' not in day24['label'] and 'agenda' in day24['label'], ('Personal-only day must not announce filtered medium economic data', day24)
    return {'economic_dates': red_dates, 'personal_dates': blue_dates, 'days': data}


def rgba(color):
    values = [float(value) for value in re.findall(r'[\d.]+', color)]
    assert len(values) in (3, 4), ('Expected resolved RGB color', color)
    return values if len(values) == 4 else values + [1]


def reachable(locator):
    """Scroll intentionally, then detect clipping and actual pointer occlusion."""
    data = locator.evaluate('''e=>{
      e.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'});
      const b=e.getBoundingClientRect(),x=b.left+b.width/2,y=b.top+b.height/2,hit=document.elementFromPoint(x,y),cuts=[];
      for(let p=e.parentElement;p;p=p.parentElement){
        const s=getComputedStyle(p),r=p.getBoundingClientRect();
        if(['auto','scroll','hidden','clip'].includes(s.overflowX)&&(b.left<r.left-.25||b.right>r.right+.25))cuts.push('horizontal:'+p.className);
        if(['auto','scroll','hidden','clip'].includes(s.overflowY)&&(b.top<r.top-.25||b.bottom>r.bottom+.25))cuts.push('vertical:'+p.className);
      }
      return {box:b.toJSON(),viewport:[innerWidth,innerHeight],cuts,hit:!!hit&&(e===hit||e.contains(hit)),hitTag:hit?.tagName,hitClass:hit?.className};
    }''')
    b = data['box']
    assert b['left'] >= -EPSILON and b['right'] <= data['viewport'][0] + EPSILON and b['top'] >= -EPSILON and b['bottom'] <= data['viewport'][1] + EPSILON, ('Control outside viewport after scrolling', data)
    assert not data['cuts'] and data['hit'], ('Control clipped/occluded after intentional scrolling', data)
    return data


def selection_geometry(page):
    data = page.locator(PANEL + ' .calendar-grid').evaluate('''grid=>{
      const selected=[...grid.querySelectorAll('[aria-selected="true"]')],current=[...grid.querySelectorAll('[aria-current="date"]')];
      const treatment=n=>{const s=getComputedStyle(n),v=getComputedStyle(n.querySelector('.calendar-day-number'));return {date:n.dataset.calendarDate,background:s.backgroundColor,outline:v.outlineStyle,outlineWidth:parseFloat(v.outlineWidth),outlineColor:v.outlineColor};};
      return {selected:selected.map(treatment),today:current.map(treatment)};
    }''')
    assert len(data['selected']) == 1 and len(data['today']) == 1, ('One selected date and one current civil date', data)
    selected, today = data['selected'][0], data['today'][0]
    assert today['date'] == '2026-10-23' and selected['date'] != today['date'], ('Today must remain independent from another selected date', data)
    assert selected['background'] != today['background'] and rgba(selected['background'])[3] > 0, ('Selected date needs visible treatment distinct from today', data)
    assert today['outline'] != 'none' and today['outlineWidth'] > 0 and rgba(today['outlineColor'])[3] > 0, ('Unselected today must retain its visible numeral outline', data)
    return data


def capture_viewport(page, path):
    # Playwright's explicit CSS clip crops a native200 Retina viewport. The
    # shared record() failure capture already uses this unclipped CDP surface.
    cdp = page.context.new_cdp_session(page)
    try:
        png = base64.b64decode(cdp.send('Page.captureScreenshot', {
            'format': 'png', 'fromSurface': True, 'captureBeyondViewport': False})['data'])
        Path(path).write_bytes(png)
        return {'path': str(path), 'method': 'CDP viewport surface',
                'pixels': [int.from_bytes(png[16:20], 'big'), int.from_bytes(png[20:24], 'big')]}
    finally:
        cdp.detach()


def text_contrast(page, selector):
    data = page.evaluate(CONTRAST, selector)
    assert data is not None and data['ratio'] >= 4.5, ('Calendar selected/primary text contrast below4.5', selector, data)
    return data


def geometry(page, visual, header=None):
    dialog = page.locator(DIALOG)
    assert dialog.evaluate("e=>e.open&&e.matches(':modal')"), 'Calendar must use a native modal dialog'
    data = dialog.evaluate('''e=>{
      const r=n=>n.getBoundingClientRect().toJSON(),launcher=document.getElementById('headerCalendarBtn');
      return {box:r(e),viewport:[innerWidth,innerHeight],anchor:r(launcher),
        overflows:[e,...e.querySelectorAll('.calendar-panel,.calendar-body,.calendar-month,.calendar-grid,.calendar-agenda,.calendar-controls:not([hidden]),.calendar-info:not([hidden]),.calendar-form-host:not([hidden])')].map(n=>({
          name:n.id||n.className,client:n.clientWidth,scroll:n.scrollWidth,overflow:getComputedStyle(n).overflowY,clientHeight:n.clientHeight,scrollHeight:n.scrollHeight})),
        cells:[...e.querySelectorAll('.calendar-grid [data-calendar-date]')].map(n=>({date:n.dataset.calendarDate,...r(n)}))};
    }''')
    box, viewport = data['box'], data['viewport']
    assert box['width'] > 0 and box['width'] <= min(760, viewport[0]) + EPSILON, ('Calendar maximum width', data)
    assert box['left'] >= -EPSILON and box['top'] >= -EPSILON and box['right'] <= viewport[0] + EPSILON and box['bottom'] <= viewport[1] + EPSILON, ('Calendar outside viewport', data)
    if viewport[0] == 320:
        assert abs(box['width'] - 320) <= EPSILON, ('320px calendar must use the full available width', data)
    elif viewport[0] <= 700:
        assert box['left'] >= 12 - EPSILON and box['right'] <= viewport[0] - 12 + EPSILON, ('Tablet/mobile bounded calendar', data)
    anchor = data['anchor']
    if viewport[0] > 700 and viewport[1] - anchor['bottom'] - 28 >= 360 and anchor['width'] > 0:
        assert abs(box['top'] - anchor['bottom'] - 12) <= TOLERANCE, ('Desktop calendar must anchor 12px below its launcher when it fits', data)
        expected_left = max(16, min(anchor['right'] - box['width'], viewport[0] - box['width'] - 16))
        assert abs(box['left'] - expected_left) <= TOLERANCE, ('Desktop launcher alignment with viewport bounds', data)
    for owner in data['overflows']:
        assert owner['scroll'] <= owner['client'] + 1, ('Calendar horizontal overflow', owner)
        if owner['scrollHeight'] > owner['clientHeight'] + 1:
            assert owner['overflow'] not in ('hidden', 'clip'), ('Calendar vertical content clipped without scrolling', owner)
    cells = data['cells']
    assert len(cells) in (28, 35, 42), ('Complete month weeks required', len(cells))
    assert page.locator(PANEL + ' .calendar-grid [tabindex="0"]').count() == 1, 'Exactly one roving grid tab stop'
    assert page.locator(PANEL + ' .calendar-grid [aria-selected="true"]').count() == 1, 'Exactly one selected date'
    assert page.locator(PANEL + ' [data-calendar-date="2026-10-23"][aria-current="date"]').count() == 1, 'Today is a civil date, distinct from selection'
    selected = page.locator(PANEL + ' .calendar-grid [aria-selected="true"]').get_attribute('data-calendar-date')
    data['selected_contrast'] = text_contrast(page, PANEL + ' .calendar-grid [aria-selected="true"] .calendar-day-number')
    if page.locator(PANEL + ' .calendar-form .calendar-primary').count():
        data['primary_contrast'] = text_contrast(page, PANEL + ' .calendar-form .calendar-primary')
    if selected != '2026-10-23':
        data['selection_distinction'] = selection_geometry(page)
    for index, cell in enumerate(cells):
        assert cell['width'] >= 44 - EPSILON and abs(cell['height'] - 44) <= EPSILON, ('44px day target', cell)
        assert cell['left'] >= box['left'] - EPSILON and cell['right'] <= box['right'] + EPSILON, ('Grid column clipped', cell, box)
        if index % 7:
            previous = cells[index - 1]
            assert abs(cell['top'] - previous['top']) <= TOLERANCE and cell['left'] >= previous['right'] - EPSILON, ('Seven ordered columns without overlap', previous, cell)
        if index >= 7:
            assert cell['top'] >= cells[index - 7]['bottom'] - EPSILON, ('Month rows overlap', cells[index - 7], cell)
    data['row_reachability'] = [reachable(page.locator(PANEL + ' .calendar-grid [data-calendar-date]').nth(index))
                                for index in (0, len(cells) - 1)]
    icons = {}
    for action in ('info', 'filters', 'new', 'close', 'previous', 'next'):
        control = page.locator(PANEL + f' .calendar-icon-button[data-calendar-action="{action}"]')
        reachable(control)
        icons[action] = visual.centered(control, 'ink', True)
    today = page.locator(PANEL + ' [data-calendar-action="today"]')
    reachable(today)
    icons['today'] = visual.centered(today)
    for numeral in page.locator(PANEL + ' .calendar-day-number').all():
        visual.centered(numeral)
    economic=None
    if page.locator(PANEL+' [data-calendar-economic-id]').count():
        economic=assert_layout(page.locator(PANEL))
        for index,toggle in enumerate(controls(page.locator(PANEL)).all()):
            icons['economic-detail-'+str(index)]=visual.centered(toggle,'ink',True)
    return {'dialog': data, 'header': header, 'icons': icons, 'markers': marker_geometry(page), 'economic_table':economic}


def form_geometry(page, visual):
    result = []
    form = page.locator(PANEL + ' .calendar-form')
    assert form.count() == 1, 'A real unsaved form is required'
    for control in form.locator('input:not([type="checkbox"]),select,textarea,button:visible').all():
        if not control.is_visible():
            continue
        reachability = reachable(control)
        data = control.evaluate('''e=>{const b=e.getBoundingClientRect(),d=e.closest('dialog').getBoundingClientRect();return {tag:e.tagName,name:e.name||e.dataset.calendarAction,box:b.toJSON(),dialog:d.toJSON(),client:e.clientWidth,scroll:e.scrollWidth};}''')
        b, d = data['box'], data['dialog']
        assert b['width'] > 0 and b['height'] >= 44 - EPSILON, ('Form control target', data)
        assert b['left'] >= d['left'] - EPSILON and b['right'] <= d['right'] + EPSILON and b['top'] >= d['top'] - EPSILON and b['bottom'] <= d['bottom'] + EPSILON, ('Form control inaccessible after scrolling', data)
        if data['tag'] == 'BUTTON':
            data['contents'] = visual.centered(control)
            if data['name'] == 'save-form':
                data['contrast'] = text_contrast(page, PANEL + ' .calendar-form .calendar-primary')
        data['reachability'] = reachability
        result.append(data)
    assert any(item['name'] == 'title' for item in result) and any(item['name'] == 'save-form' for item in result), 'Nonempty form/control coverage required'
    return result


def scenario(page, visual, capture=None):
    before = start_probe(page)
    header = header_geometry(page, visual)
    open_calendar(page)
    result = {'populated': geometry(page, visual, header)}
    grid = page.locator(PANEL + ' .calendar-grid')
    grid.locator('[data-calendar-date="2026-10-23"]').focus()
    keyboard = []
    for key, date in (('ArrowRight', '2026-10-24'), ('ArrowLeft', '2026-10-23'),
                      ('ArrowDown', '2026-10-30'), ('ArrowUp', '2026-10-23'),
                      ('Home', '2026-10-19'), ('End', '2026-10-25')):
        page.keyboard.press(key)
        focused = page.locator(':focus')
        assert focused.get_attribute('data-calendar-date') == date, ('Grid keyboard order', key, date)
        focus = visual.focus_visible(focused)
        assert focus['visible'] and ((focus['outline'] != 'none' and focus['width'] > 0) or focus['shadow'] != 'none'), ('Visible keyboard focus required', key, focus)
        keyboard.append({'key': key, 'date': date, 'focus': focus})
    page.keyboard.press('Enter')
    assert grid.locator('[data-calendar-date="2026-10-25"]').get_attribute('aria-selected') == 'true'
    result['today_vs_selection'] = selection_geometry(page)
    result['non_today_markers'] = marker_geometry(page)
    page.locator(PANEL + ' [data-calendar-action="today"]').click()
    expect(page.locator(PANEL + ' [data-calendar-date="2026-10-23"] .calendar-economic-dot')).to_have_count(1)
    result['keyboard'] = keyboard
    for action, target in (('filters', '.calendar-controls'), ('info', '.calendar-info')):
        button = page.locator(PANEL + f' .calendar-header [data-calendar-action="{action}"]')
        button.click()
        expect(page.locator(PANEL + ' ' + target)).to_be_visible()
        result[action] = geometry(page, visual, header)
        button.click()
        expect(page.locator(PANEL + ' ' + target)).to_be_hidden()
    page.locator(PANEL + ' [data-calendar-action="new"]').click()
    result['empty_form'] = form_geometry(page, visual)
    page.locator(PANEL + ' [name="title"]').fill('SYN unsaved calendar visual draft')
    page.locator(PANEL + ' [name="notes"]').fill('SYN observation only. ' * 12)
    result['filled_form'] = form_geometry(page, visual)
    page.keyboard.press('Escape')
    expect(page.locator(DIALOG)).not_to_be_visible()
    result['escape_focus_return'] = focus_return(page)
    reveal_launcher(page)
    page.locator('#headerCalendarBtn').click()
    expect(page.locator(PANEL + ' [name="title"]')).to_have_value('SYN unsaved calendar visual draft')
    cancel = page.locator(PANEL + ' [data-calendar-action="cancel-form"]')
    cancel.scroll_into_view_if_needed()
    cancel.click()
    expect(page.locator(PANEL + ' .calendar-form')).to_have_count(0)
    page.locator(DIALOG).evaluate('e=>e.scrollTop=0')
    if capture:
        result['capture'] = capture_viewport(page, capture)
    close = page.locator(PANEL + ' [data-calendar-action="close"]')
    close.scroll_into_view_if_needed()
    close.click()
    expect(page.locator(DIALOG)).not_to_be_visible()
    result['close_focus_return'] = focus_return(page)
    reveal_launcher(page)
    page.locator('#headerNotificationsBtn').click()
    expect(page.locator('#notificationCenter')).to_be_visible()
    assert page.evaluate('JPWCalendar.open()') is False, 'Calendar must refuse another active modal'
    expect(page.locator(DIALOG)).not_to_be_visible()
    page.keyboard.press('Escape')
    result['no_writes'] = unchanged(page, before)
    return result


def counterproof(page, visual, name, mutation):
    header = header_geometry(page, visual)
    open_calendar(page)
    if name == 'today-selection':
        page.locator(PANEL + ' [data-calendar-date="2026-10-25"]').click()
    rejections = []
    for stimulus in mutation if isinstance(mutation, tuple) else (mutation,):
        oracle = lambda: geometry(page, visual, header)
        if isinstance(stimulus, dict):
            page.evaluate(stimulus['prepare'])
            if stimulus.get('oracle') == 'form':
                # New replaces the calendar body with the form. Its primary
                # action is judged by the same form oracle as the real journey.
                oracle = lambda: form_geometry(page, visual)
            stimulus = stimulus['mutation']
        oracle()  # The same state-specific oracle must first accept a valid surface.
        page.evaluate(stimulus)
        try:
            oracle()
        except AssertionError as error:
            rejections.append(str(error))
        else:
            raise AssertionError('Same calendar oracle accepted deliberate ' + name)
        if isinstance(mutation, tuple):
            page.evaluate('''async()=>{JPWCalendar.refresh();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}''')
    return {'valid_surface_accepted': True, 'deliberate_violation_rejected': name, 'rejections': rejections}


def focus_return_counterproof(page):
    before = start_probe(page)
    open_calendar(page)
    page.locator(PANEL + ' [data-calendar-action="close"]').click()
    expect(page.locator(DIALOG)).not_to_be_visible()
    valid = focus_return(page)
    page.evaluate("()=>{document.body.setAttribute('tabindex','-1');document.body.focus()}")
    assert page.evaluate('document.activeElement===document.body'), 'Focus counterproof did not establish its deliberate body-focus stimulus'
    try:
        focus_return(page)
    except AssertionError as error:
        rejection = str(error)
    else:
        raise AssertionError('Same calendar focus oracle accepted deliberate body focus')
    return {'valid_surface_accepted': valid, 'deliberate_violation_rejected': 'focus-return',
            'rejections': [rejection], 'no_writes': unchanged(page, before)}


def matrix(browser, url, report, visual):
    for width, height in SIZES:
        for layout in LAYOUTS:
            for theme in THEMES:
                context = browser.new_context(viewport={'width': width, 'height': height}, timezone_id='UTC',
                                              service_workers='block', reduced_motion='reduce')
                try:
                    page = prepare_context(context, url)
                    page.evaluate('x=>mountNavigationLayout(x)', layout)
                    page.evaluate('t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}', theme)
                    capture = Path(report['out']) / f'calendar-{layout}-{theme}-{width}x{height}.png'
                    visual.record(report, f'calendar-{layout}-{theme}-{width}x{height}',
                                  lambda: scenario(page, visual, capture), page,
                                  criteria='SVGink<=2CSSpx/44px/7columns/anchored-bounded/default-markers/keyboard/visible-focus-return/read-only',
                                  layout=layout, theme=theme, viewport=[width, height])
                    assert_fixture_requests(context)
                finally:
                    context.close()
    mutations = (
        ('inner-svg', "document.querySelector('#calendarDialog [data-calendar-action=close] svg').style.transform='translateX(5px)'"),
        ('economic-dot', "document.querySelector('#calendarDialog [data-calendar-date=\"2026-10-23\"] .calendar-economic-dot').style.transform='translateX(5px)'"),
        ('overflow', "document.querySelector('#calendarDialog .calendar-grid').style.minWidth='200vw'"),
        ('personal-only-economic-dot', "()=>{const n=document.createElement('span');n.className='calendar-economic-dot';document.querySelector('#calendarDialog [data-calendar-date=\"2026-10-24\"] .calendar-day-markers').append(n)}"),
        ('marker-appearance', (
            "document.querySelector('#calendarDialog [data-calendar-date=\"2026-10-23\"] .calendar-economic-dot').style.opacity='0'",
            "document.querySelector('#calendarDialog [data-calendar-date=\"2026-10-24\"] .calendar-personal-dot').style.backgroundColor='red'")),
        ('today-selection', (
            "document.querySelector('#calendarDialog [data-calendar-date=\"2026-10-23\"] .calendar-day-number').style.outline='none'",
            "()=>{const b=document.querySelector('#calendarDialog .calendar-grid [aria-selected=true]');b.style.setProperty('color','#fff','important');b.style.setProperty('background-color','#409cff','important')}",
            {'prepare': "document.querySelector('#calendarDialog [data-calendar-action=new]').click()", 'oracle': 'form',
             'mutation': "()=>{const b=document.querySelector('#calendarDialog .calendar-form .calendar-primary');b.style.setProperty('color','#fff','important');b.style.setProperty('background-color','#409cff','important')}"})),
        ('vertical-clipping', "Object.assign(document.querySelector('#calendarDialog .calendar-grid').style,{height:'44px',overflow:'hidden'})"),
    )
    for name, mutation in mutations:
        context = browser.new_context(viewport={'width': 1440, 'height': 900}, timezone_id='UTC',
                                      service_workers='block', reduced_motion='reduce')
        try:
            page = prepare_context(context, url)
            visual.record(report, 'calendar-counterproof-' + name,
                          lambda: counterproof(page, visual, name, mutation), page,
                          criteria='same geometry oracle accepts valid surface and rejects representative violation')
            assert_fixture_requests(context)
        finally:
            context.close()
    context = browser.new_context(viewport={'width': 1440, 'height': 900}, timezone_id='UTC',
                                  service_workers='block', reduced_motion='reduce')
    try:
        page = prepare_context(context, url)
        visual.record(report, 'calendar-counterproof-focus-return',
                      lambda: focus_return_counterproof(page), page,
                      criteria='same focus oracle accepts visible return target and rejects deliberate body focus')
        assert_fixture_requests(context)
    finally:
        context.close()


def native_zoom(pw, url, report, visual):
    profile = Path(tempfile.mkdtemp(prefix='calendar-native200-', dir=report['out']))
    (profile / 'Default').mkdir()
    (profile / 'Default/Preferences').write_text(json.dumps({'partition': {'default_zoom_level': {'x': math.log(2) / math.log(1.2)}}}))
    options = launch_options()
    options.update(headless=False, no_viewport=True, args=['--window-size=1440,1000'],
                   service_workers='block', reduced_motion='reduce', timezone_id='UTC')
    try:
        context = pw.chromium.launch_persistent_context(str(profile), **options)
        try:
            page = prepare_context(context, url)
            zoom = page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
            assert abs(zoom['outer'] / zoom['inner'] - 2) < .01 and zoom['css'] == '1', ('Native200 must use browser preferences, not CSS zoom', zoom)
            for layout in LAYOUTS:
                for theme in THEMES:
                    page.evaluate('x=>mountNavigationLayout(x)', layout)
                    page.evaluate('t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}', theme)
                    capture = Path(report['out']) / f'calendar-native200-{layout}-{theme}.png'
                    visual.record(report, f'calendar-native200-{layout}-{theme}',
                                  lambda: scenario(page, visual, capture), page,
                                  criteria='native200/SVGink<=2CSSpx/44px/viewport-nooverflow/keyboard/visible-focus-return/read-only',
                                  layout=layout, theme=theme, native_zoom=200, zoom=zoom)
                    if page.locator(DIALOG).count() and page.locator(DIALOG).evaluate('e=>e.open'):
                        page.evaluate('JPWCalendar.close()')
                    if page.locator('#notificationCenter').evaluate('e=>e.open'):
                        page.keyboard.press('Escape')
            assert_fixture_requests(context)
        finally:
            context.close()
    finally:
        shutil.rmtree(profile)

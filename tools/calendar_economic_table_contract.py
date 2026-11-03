"""Additive economic table assertions. Human contract: table request 2026-10-28.
No renderer/CSS snapshots are expected values. No writer or new runner/gate.
"""
import json
from playwright.sync_api import expect

HEADERS=('Horário','Moeda','Impacto','Evento','Atual','Projeção','Anterior')
FIELDS=('time','currency','impact','event','actual','forecast','previous')
LABELS=dict(zip(FIELDS,HEADERS))
TOLERANCE=2
EPSILON=.25
VALUES=(('0','0.0%'),('−0.5%','1.2M'),('',''),('1.2M','0'),('0.0%','−0.5%'),('2.5%','3.5%'))

def value(cell, label):
    """Allow a visible compact label beside the value, without prescribing spans."""
    exact=cell.locator('[data-calendar-economic-value]')
    if exact.count():
        assert exact.count()==1
        return exact.text_content()
    text=' '.join(cell.inner_text().split())
    return text[len(label):].lstrip(' :') if text.startswith(label) else text


def controls(panel):
    return panel.locator('[data-calendar-action="economic-detail"]')


def details(panel):
    """Only aria-controlled detail nodes belonging to this host; no global guess."""
    ids=controls(panel).evaluate_all('nodes=>nodes.map(n=>n.getAttribute("aria-controls"))')
    assert ids and all(ids) and len(ids)==len(set(ids)), ('Unique nonempty detail IDs within host',ids)
    for identity in ids:
        assert panel.locator('[id='+json.dumps(identity)+']').count()==1, ('Detail target belongs to same host',identity)
        assert panel.page.locator('[id='+json.dumps(identity)+']').count()==1, ('Detail IDs unique across hosts',identity)
    return [panel.locator('[id='+json.dumps(identity)+']') for identity in ids]


def collapsed(panel):
    for toggle,target in zip(controls(panel).all(),details(panel)):
        expect(toggle).to_have_attribute('aria-expanded','false')
        expect(target).not_to_be_visible()
    # Secondary provenance is disclosed only through the controlled detail.
    for row in panel.locator('[data-calendar-economic-id]').all():
        assert not row.locator('a:visible').count(), 'No always-visible secondary source links'
        assert 'Horário original:' not in row.inner_text(), 'Original time is secondary detail'


def assert_values(panel, events):
    """String oracle declared by fixture/source input, independent of product output."""
    observed=[]
    missing='–' if panel.evaluate('p=>!!p.closest("#calendarDialog")') else '—'
    for event in events:
        row=panel.locator('[data-calendar-economic-id='+json.dumps(event['id'])+']')
        expect(row).to_have_count(1)
        assert set(row.locator('[data-calendar-economic-field]').evaluate_all('ns=>ns.map(n=>n.dataset.calendarEconomicField)'))==set(FIELDS), 'Every row retains all7 fields'
        detail=None
        for field,expected in [('actual',missing),('forecast',event.get('forecast') or missing),('previous',event.get('previous') or missing)]:
            cell=row.locator('[data-calendar-economic-field="'+field+'"]')
            assert value(cell,LABELS[field])==expected, (event['id'],field,expected,cell.inner_text())
            if not cell.is_visible():
                if detail is None:
                    toggle=row if row.get_attribute('data-calendar-action')=='economic-detail' else row.locator('[data-calendar-action="economic-detail"]')
                    toggle.click()
                    detail=panel.locator('#'+toggle.get_attribute('aria-controls'))
                number=detail.locator('[data-calendar-detail-value="'+field+'"]')
                expect(number).to_be_visible();expect(number).to_have_text(expected)
                assert LABELS[field] in detail.inner_text(), 'Hidden table values retain their labels in the accessible detail'
            else:expect(cell).to_be_visible()
        if detail is not None:toggle.click()
        # Absence is explained accessibly without assuming the source publishes Actual.
        actual=row.locator('[data-calendar-economic-field="actual"]')
        explanation=actual.evaluate(r'''n=>{
          const referenced=(n.getAttribute('aria-describedby')||'').split(/\s+/).filter(Boolean).map(id=>document.getElementById(id)?.textContent||'').join(' ');
          const visibleNotes=[...n.closest('.calendar-panel').querySelectorAll('p,[role="note"]')].filter(e=>e.getClientRects().length&&!e.hidden).map(e=>e.textContent).join(' ');
          return [n.getAttribute('aria-label')||'',referenced,visibleNotes].join(' ').toLowerCase();
        }''')
        assert 'atual' in explanation and ('não colet' in explanation or 'não dispon' in explanation or 'sem resultado' in explanation or 'não fornecid' in explanation), ('Actual absence needs a clear accessible explanation',explanation)
        observed.append({'id':event['id'],'forecast':event.get('forecast') or missing,'previous':event.get('previous') or missing,'actual':missing})
    return observed


def assert_compact_rows(panel):
    heights=panel.locator('[data-calendar-economic-id]').evaluate_all('ns=>ns.map(n=>n.getBoundingClientRect().height)')
    modal=panel.evaluate('p=>!!p.closest("#calendarDialog")')
    assert heights and all(44-EPSILON<=n<=56+TOLERANCE if modal else abs(n-44)<=TOLERANCE for n in heights), ('44px minimum; modal permits two-line titles; workspace remains44px',heights)


def assert_layout(panel, *, natural_wide=False):
    data=panel.evaluate('''panel=>{
      const box=e=>e.getBoundingClientRect().toJSON(),visible=e=>e.getClientRects().length&&!e.hidden&&getComputedStyle(e).visibility!=='hidden';
      const body=panel.querySelector('.calendar-body'),month=panel.querySelector('.calendar-month'),agenda=panel.querySelector('.calendar-agenda'),s=getComputedStyle(body);
      return {panel:box(panel),body:box(body),month:box(month),agenda:box(agenda),
        useful:body.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight),
        agendaUseful:agenda.clientWidth-parseFloat(getComputedStyle(agenda).paddingLeft)-parseFloat(getComputedStyle(agenda).paddingRight),
        headings:[...agenda.querySelectorAll('th,[role="columnheader"]')].filter(e=>visible(e)&&e.getBoundingClientRect().width>2&&e.getBoundingClientRect().height>2).map(e=>e.textContent.trim()),
        headerBoxes:[...agenda.querySelectorAll('th,[role="columnheader"]')].filter(e=>visible(e)&&e.getBoundingClientRect().width>2&&e.getBoundingClientRect().height>2).map(box),
        scrollRegion:(()=>{const n=agenda.querySelector('.calendar-economic-scroll');return n?{box:box(n),client:n.clientWidth,scroll:n.scrollWidth,tabIndex:n.tabIndex,role:n.getAttribute('role'),label:n.getAttribute('aria-label')}:null})(),
        table:box(agenda.querySelector('.calendar-economic-table')),
        overflow:[panel,body,agenda].map(e=>({name:e.id||e.className,scroll:e.scrollWidth,client:e.clientWidth})),
        rows:[...agenda.querySelectorAll('[data-calendar-economic-id]')].map(e=>({box:box(e),fields:[...e.querySelectorAll('[data-calendar-economic-field]')].filter(visible).map(n=>({name:n.dataset.calendarEconomicField,box:box(n),text:n.innerText,numericInk:(()=>{const v=n.querySelector('[data-calendar-economic-value]');if(!v)return null;const range=document.createRange();range.selectNodeContents(v);const ink=[...range.getClientRects()].filter(r=>r.width>0);return {right:Math.max(...ink.map(r=>r.right)),expectedRight:n.getBoundingClientRect().right-parseFloat(getComputedStyle(n).paddingRight)};})(),label:n.getAttribute('data-label'),labelText:[...n.querySelectorAll('*')].filter(visible).map(x=>x.innerText)}))}))};
    }''')
    assert all(o['scroll']<=o['client']+1 for o in data['overflow']), ('No horizontal overflow',data['overflow'])
    if data['useful']<700-EPSILON:
        assert data['agenda']['top']>=data['month']['bottom']-TOLERANCE, ('Stack below700 useful CSSpx',data)
    else:
        assert abs(data['month']['width']-308)<=TOLERANCE, ('Month grid gets308 CSSpx beside economic area',data)
        assert data['agenda']['left']>=data['month']['right']-TOLERANCE, ('Agenda beside month',data)
    region=data['scrollRegion']
    assert region and region['tabIndex']==0 and region['role']=='region' and region['label'], ('Named keyboard scroll region',data)
    assert region['scroll']<=region['client']+1, ('News must fit without horizontal scrolling',data)
    assert abs(data['table']['width']-region['box']['width'])<=TOLERANCE, ('Fluid news table fills its region',data)
    compact=region['box']['width']<500
    visible_fields=FIELDS[:4] if compact else FIELDS
    assert data['headings']==list(HEADERS[:4] if compact else HEADERS), ('Four headers below500px, seven otherwise',data)
    for row in data['rows']:
        assert len(row['fields'])==len(visible_fields), ('Fields appropriate to available news width',row)
        assert row['box']['height']>=44-EPSILON, ('Rows retain44px target',row)
        fields={f['name']:f for f in row['fields']}
        for key in (() if compact else FIELDS[4:]):
            ink=fields[key]['numericInk']
            assert ink and abs(ink['right']-ink['expectedRight'])<=TOLERANCE, ('Numeric ink must align right within its own cell',key,ink)
        for key,header in zip(visible_fields,data['headerBoxes']):
            cell=fields[key]['box']
            assert abs(header['left']-cell['left'])<=TOLERANCE and abs(header['right']-cell['right'])<=TOLERANCE, ('Real header and cell column bounds align within2 CSSpx',key,header,cell)
        assert max(f['box']['top'] for f in fields.values())-min(f['box']['top'] for f in fields.values())<=TOLERANCE, ('Fields align in one row',row)
        for first,second in zip(visible_fields,visible_fields[1:]):assert fields[first]['box']['right']<=fields[second]['box']['left']+TOLERANCE, ('Ordered columns',row)
        assert all(f['box']['left']>=region['box']['left']-TOLERANCE and f['box']['right']<=region['box']['right']+TOLERANCE for f in row['fields']), ('Every visible cell is inside the region',row)
    for toggle in controls(panel).all():
        b=toggle.bounding_box();assert b and b['width']>=44-EPSILON and b['height']>=44-EPSILON, ('44px detail target',b)
        if toggle.get_attribute('data-calendar-economic-id'):
            assert toggle.locator('[data-calendar-economic-field="event"]').count()==1, 'Clickable row retains its event cell'
        else:
            parent=toggle.locator('xpath=..')
            assert parent.locator('[data-calendar-economic-field="event"]').count() or toggle.locator('xpath=ancestor::*[@data-calendar-economic-field="event"]').count(), 'Workspace i belongs to Evento cell'
    assert panel.locator('.calendar-event-warning').evaluate_all('nodes=>nodes.every(n=>n.scrollWidth<=n.clientWidth+1)'), 'Compact warning labels must remain fully readable'
    return data


def setup(page):
    """View-only controlled domain seam; live transport has its separate cache case."""
    page.evaluate('''()=>{
      closeModal();window.__onbShown=true;
      const api=JPWEconomicCalendar;window.__table={generation:1,moved:false,duplicate:false};
      const values=[['0','0.0%'],['−0.5%','1.2M'],['',''],['1.2M','0'],['0.0%','−0.5%'],['2.5%','3.5%']];
      window.JPWEconomicCalendar={...api,queryRange(query){const events=values.map(([forecast,previous],i)=>({
        id:'SYN-table-'+__table.generation+'-'+i,title:i===1?'SYN long economic event with a deliberately extended title to wrap without clipping or hiding any values':'SYN table event '+i,
        currency:'USD',impact:'high',date:'2026-10-23',at:'2026-10-23T'+String(14+i+(__table.moved&&i===0?1:0)).padStart(2,'0')+':00:00Z',precision:'instant',
        provider:'forexfactory',sourceId:'ff-USD',sourceUrl:'https://www.forexfactory.com/calendar',timeZone:'America/New_York',timeConfirmed:false,status:i===2?'cancelled':'scheduled',
        forecast,previous,observationStatus:i===3?'not-in-latest':'present',sourceConflict:i===4,
        officialReferences:[{id:'SYN-official-'+i,title:'SYN official source',url:'https://example.org/official/'+i}]
      }));if(__table.duplicate)events.push({...events[0],id:'SYN-table-ambiguous'});return {events,coverage:[],updatedAt:null};}};
      JPWNavigation.navigate('tools-calendar');
    }''')
    panel=page.locator('#execEcal .calendar-panel');expect(panel).to_be_visible();expect(panel.locator('[data-calendar-economic-id]')).to_have_count(6)
    return panel


def table_case(page,width,theme,kind):
    page.evaluate('(theme)=>document.documentElement.dataset.theme=theme',theme)
    before=page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),cache:localStorage.getItem("jpwealth.ui.ffNews.v1")})')
    panel=setup(page)
    expected=page.evaluate("JPWEconomicCalendar.queryRange({}).events")
    if kind in ('table-compact','table-fit'):
        page.locator('#headerCalendarBtn').click();panel=page.locator('#calendarDialog .calendar-panel')
    if kind=='table-fit':
        expected_width=width if width<=360 else width-24 if width<=700 else min(912,width-32)
        measured=page.locator('#calendarDialog').bounding_box()
        assert abs(measured['width']-expected_width)<=TOLERANCE, ('Dialog is20% wider, bounded by viewport',width,measured)
        if width>=1024:
            agenda=panel.locator('.calendar-agenda')
            assert agenda.evaluate('n=>n.scrollHeight<=n.clientHeight+1'), 'Six compact news rows and coverage fit without adding a vertical news scroller'
    if kind=='table-wide':
        page.locator('#execEcal').evaluate("e=>{e.style.width='1800px';e.style.maxWidth='none'}")
    if kind=='table-natural':
        natural=[]
        for layout in ('sidebar','topbar','glass','submenu'):
            page.evaluate('x=>mountNavigationLayout(x)',layout)
            natural.append({'layout':layout,'geometry':assert_layout(panel)})
        geometry={'natural':natural}
    else:geometry=assert_layout(panel)
    values=assert_values(panel,expected);collapsed(panel)
    assert_compact_rows(panel)
    fonts=panel.locator('.calendar-event-economic td,.calendar-event-title,.calendar-economic-value,.calendar-event-warning').evaluate_all('ns=>ns.map(n=>parseFloat(getComputedStyle(n).fontSize))')
    assert fonts and all(12<=size<=13 for size in fonts), ('Compact typography12–13px',fonts)
    scroller=panel.locator('.calendar-economic-scroll')
    if scroller.evaluate('n=>n.scrollWidth>n.clientWidth'):
        scroller.focus();page.keyboard.press('ArrowRight')
        page.wait_for_function('n=>n.scrollLeft>0',arg=scroller.element_handle())
        # ArrowRight uses the browser's animated scroll. Its stimulus must finish
        # before an exact-position refresh assertion; resetting scrollLeft alone
        # does not cancel the UA animation on the still-connected old region.
        scroller.evaluate('''n=>new Promise((resolve,reject)=>{
          let last=n.scrollLeft,stable=0;const start=performance.now();
          function frame(){const now=n.scrollLeft;stable=Math.abs(now-last)<.1?stable+1:0;last=now;
            if(stable>=4)return resolve();
            if(performance.now()-start>3000)return reject(new Error('Keyboard scroll did not settle'));
            requestAnimationFrame(frame);
          }requestAnimationFrame(frame);
        })''')
        scroller.evaluate('n=>n.scrollLeft=0')

    if kind=='table-boundaries':
        boundaries=[]
        host=page.locator('#execEcal')
        for area,target in [('useful',699),('useful',700),('agendaUseful',499),('agendaUseful',500),('agendaUseful',719),('agendaUseful',720)]:
            # Resize the container with a fixed viewport. This does not force
            # columns, visibility, media queries or the product's resize observer.
            for adjustment in range(2):
                current=assert_layout(panel)[area] if adjustment else panel.evaluate("(p,k)=>{const n=p.querySelector(k==='useful'?'.calendar-body':'.calendar-agenda'),s=getComputedStyle(n);return n.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight)}",area)
                host.evaluate('(n,delta)=>{n.style.maxWidth="none";n.style.width=(n.getBoundingClientRect().width+delta)+"px"}',target-current)
                page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
            measured=assert_layout(panel)
            assert abs(measured[area]-target)<=EPSILON,(area,target,measured)
            boundaries.append({'area':area,'target':target,'observed':measured})
        row=panel.locator('[data-calendar-economic-id]').first
        row.evaluate('n=>n.style.height="88px"')
        rejected=False
        try:assert_compact_rows(panel)
        except AssertionError:rejected=True
        finally:row.evaluate('n=>n.style.height=""')
        assert rejected,'Row-height oracle must reject an88px regression'
        assert_compact_rows(panel)
        geometry={'boundaries':boundaries,'tall_row_counterproof':'rejected'}
    scroller=panel.locator('.calendar-economic-scroll')
    scroller.focus();scroller.evaluate('n=>n.scrollLeft=37')
    preserved=scroller.evaluate('n=>n.scrollLeft')
    scroll_before=scroller.evaluate('n=>({left:n.scrollLeft,width:n.clientWidth,scroll:n.scrollWidth,fonts:document.fonts.status,active:document.activeElement===n,table:n.firstElementChild.getBoundingClientRect().width})')
    page.evaluate('async()=>{await JPWCalendar.refresh()}')
    expect(panel.locator('.calendar-economic-scroll')).to_be_focused()
    assert panel.locator('.calendar-economic-scroll').evaluate('n=>n.scrollLeft')==preserved, ('Refresh preserves focused news region and scroll',scroll_before,panel.locator('.calendar-economic-scroll').evaluate('n=>({left:n.scrollLeft,width:n.clientWidth,scroll:n.scrollWidth,fonts:document.fonts.status,active:document.activeElement===n,table:n.firstElementChild.getBoundingClientRect().width})'))
    if kind=='table-state':
        # Critical statuses remain legible while secondary provenance is closed.
        rows=panel.locator('[data-calendar-economic-id]')
        assert 'Cancelado' in rows.nth(2).inner_text()
        expect(rows.nth(3).locator('.calendar-event-warning')).to_have_text('Ausente')
        assert 'não comprova cancelamento' in rows.nth(3).locator('.calendar-event-warning').get_attribute('aria-label')
        expect(rows.nth(4).locator('.calendar-event-warning')).to_have_text('Diverge')
        assert 'fontes divergem' in rows.nth(4).locator('.calendar-event-warning').get_attribute('aria-label').lower()
        assert 'Horário a confirmar' in rows.first.locator('.calendar-economic-time').get_attribute('aria-label')
        toggles=controls(panel);targets=details(panel)
        first=toggles.nth(0);first.focus();page.keyboard.press('Enter')
        expect(first).to_have_attribute('aria-expanded','true');expect(targets[0]).to_be_visible()
        expect(targets[0]).to_contain_text(expected[0]['title'])
        expect(targets[0]).to_contain_text('Horário original')
        assert targets[0].get_by_role('link').count()>=2, 'FF and official references remain available'
        toggles.nth(1).focus();page.keyboard.press('Space')
        expect(toggles.nth(1)).to_have_attribute('aria-expanded','true');expect(targets[0]).not_to_be_visible()
        expect(targets[1]).to_contain_text(expected[1]['title'])
        assert sum(t.is_visible() for t in details(panel))==1, 'Only one expanded detail per host'
        first.click();first.focus()
        # Constrain only the scroll viewport, then use a real nonzero scroll.
        agenda=panel.locator('.calendar-agenda');agenda.evaluate("n=>{n.style.maxHeight='160px';n.scrollTop=48}")
        scrolled=agenda.evaluate('n=>n.scrollTop');assert scrolled>0,'Scroll stimulus must be nonzero'
        region=panel.locator('.calendar-economic-scroll')
        region.evaluate('n=>n.scrollLeft=95');horizontal=region.evaluate('n=>n.scrollLeft')
        assert horizontal==0,'News must not acquire horizontal scroll even while details are open'
        marker_count=panel.locator('.calendar-economic-dot').count()
        page.evaluate('async()=>{__table.generation++;await JPWCalendar.refresh()}')
        assert panel.locator('.calendar-economic-scroll').evaluate('n=>n.scrollLeft')==horizontal,'Refresh preserves horizontal news scroll'
        assert agenda.evaluate('n=>n.scrollTop')==scrolled,'Refresh preserves exact agenda scroll'
        assert panel.locator('.calendar-economic-dot').count()==marker_count
        expect(controls(panel).nth(0)).to_be_focused();expect(controls(panel).nth(0)).to_have_attribute('aria-expanded','true')
        # An ID recapture with exactly same observation preserves expansion; a
        # changed instant is a different observation, even on same day/title.
        page.evaluate('async()=>{__table.generation++;__table.moved=true;await JPWCalendar.refresh()}')
        expect(controls(panel).nth(0)).to_have_attribute('aria-expanded','false')
        assert not controls(panel).nth(0).evaluate('n=>n===document.activeElement'), 'Changed observation must not inherit focus'
        controls(panel).nth(0).click();controls(panel).nth(0).focus()
        page.evaluate('async()=>{__table.generation++;__table.duplicate=true;await JPWCalendar.refresh()}')
        assert not controls(panel).evaluate_all('ns=>ns.includes(document.activeElement)'), 'Ambiguous duplicates cannot inherit economic focus'
        assert controls(panel).evaluate_all('ns=>ns.every(n=>n.getAttribute("aria-expanded")==="false")'), 'Ambiguous observation cannot preserve expansion'
        page.evaluate('async()=>{__table.duplicate=false;await JPWCalendar.refresh()}')
        # Both mounted hosts may disclose one detail independently, with unique IDs.
        controls(panel).nth(1).click();page.keyboard.press('Escape')
        expect(controls(panel).nth(1)).to_have_attribute('aria-expanded','true')
        page.locator('#headerCalendarBtn').click()
        modal=page.locator('#calendarDialog .calendar-panel');controls(modal).nth(2).click()
        assert sum(t.is_visible() for t in details(modal))==1
        assert controls(panel).nth(1).get_attribute('aria-expanded')=='true'
        all_ids=controls(panel).evaluate_all('ns=>ns.map(n=>n.getAttribute("aria-controls"))')+controls(modal).evaluate_all('ns=>ns.map(n=>n.getAttribute("aria-controls"))')
        assert len(all_ids)==len(set(all_ids)), 'Host detail IDs must never collide'
        page.keyboard.press('Escape')
        assert not page.locator('#calendarDialog').evaluate('n=>n.open'), 'Escape keeps original modal dismissal contract'
        expect(page.locator('#headerCalendarBtn')).to_be_focused()
        panel.locator('[data-calendar-action="new"]').click();title=panel.locator('[name="title"]');title.fill('SYN table draft');title.evaluate('n=>{n.focus();n.setSelectionRange(4,9)}')
        selected=panel.locator('[data-calendar-date][aria-selected="true"]').get_attribute('data-calendar-date');month=panel.locator('.calendar-month-label').inner_text()
        page.evaluate('async()=>{await JPWCalendar.refresh()}')
        expect(title).to_be_focused();expect(title).to_have_value('SYN table draft')
        assert title.evaluate('n=>[n.selectionStart,n.selectionEnd]')==[4,9]
        assert panel.locator('[data-calendar-date][aria-selected="true"]').get_attribute('data-calendar-date')==selected
        assert panel.locator('.calendar-month-label').inner_text()==month
        assert controls(panel).nth(1).get_attribute('aria-expanded')=='true'
    after=page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),cache:localStorage.getItem("jpwealth.ui.ffNews.v1")})')
    assert before==after, 'Table reading/details/refresh cannot change finance or public cache'
    return {'geometry':geometry,'values':values,'kind':kind,'readonly':'byte-exact'}


def modal_presentation_case(page,width,theme,kind):
    """Human visual contract03/11; controlled data seam, actual modal actions."""
    page.evaluate('''theme=>{
      closeModal();window.__onbShown=true;document.documentElement.dataset.theme=theme;
      localStorage.setItem('jpwealth_calendar_view_v1',JSON.stringify({schemaVersion:1,currencies:['USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY'],impacts:['high','medium','low','unclassified'],contents:['economic']}));
      JPWCalendar.resetContext();
      window.__modalVisual={count:1,complete:true,failed:false,stale:false,collected:true,precision:'date'};
      const original=JPWEconomicCalendar;
      window.JPWEconomicCalendar={...original,queryRange(){
        const m=__modalVisual;if(m.failed)throw Error('Synthetic calendar query failure');
        const events=Array.from({length:m.count},(_,i)=>({id:'SYN-modal-'+i,title:i===0?'Congressional Elections':i===1?'Exemplo de evento econômico com nome suficientemente longo para ocupar duas linhas sem deslocar os valores numéricos':'Evento sintético '+i,
          currency:i%2?'EUR':'USD',impact:i===11?'unclassified':['high','medium','low'][i%3],date:'2026-11-03',at:m.precision==='date'?null:'2026-11-03T'+String(10+i%12).padStart(2,'0')+':30:00Z',precision:m.precision,timeConfirmed:false,timeZone:'America/New_York',
          provider:'forexfactory',sourceId:i%2?'ff-EUR':'ff-USD',sourceUrl:'https://www.forexfactory.com/calendar',status:'scheduled',forecast:m.count===1?'':['0','−0.5%','2.0%'][i%3],previous:m.count===1?'':['0','1.8%','1.2M'][i%3]}));
        const coverage=['USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY'].map(currency=>({currency,month:'2026-11',from:'2026-11-01',to:'2026-11-30',status:m.complete?'confirmed':'partial'}));
        return {events,coverage,updatedAt:'2026-11-03T18:00:00Z',feed:{collectedAt:m.collected?'2026-11-03T18:12:00Z':null,stale:m.stale,fetchFailed:false}};
      }};
      JPWNavigation.navigate('tools-calendar');
    }''',theme)
    work=page.locator('#execEcal .calendar-panel');expect(work.locator('[data-calendar-economic-id]')).to_have_count(1)
    expect(work.locator('button[data-calendar-action="economic-detail"]')).to_have_count(1)
    assert work.locator('.calendar-impact-bar').evaluate_all('ns=>ns.map(n=>n.getBoundingClientRect().height)')==[7,12,17], 'Workspace retains its original impact bars'
    assert 'America/Sao_Paulo' in work.locator('.calendar-agenda-summary').inner_text()
    workspace=work.evaluate('p=>p.outerHTML')
    page.locator('#headerCalendarBtn').click();panel=page.locator('#calendarDialog .calendar-panel')
    row=panel.locator('[data-calendar-economic-id]').first
    expect(row).to_be_visible()
    assert row.get_attribute('tabindex')=='0' and row.get_attribute('data-calendar-action')=='economic-detail', 'Entire row must be the keyboard detail action'
    expect(row.locator('button')).to_have_count(0)
    expect(panel.locator('.calendar-agenda-summary')).to_have_text('1 evento')
    title=row.locator('.calendar-event-title');expect(title).to_have_text('Congressional Elections')
    assert title.get_attribute('title')=='Congressional Elections'
    assert title.evaluate('n=>n.scrollHeight<=n.clientHeight+1'), 'The single event name must be fully visible'
    expect(row.locator('.calendar-economic-time')).to_have_text('Sem hora')
    assert row.locator('.calendar-impact-bar').count()==3
    assert row.locator('.calendar-impact-symbol').get_attribute('aria-label').lower().startswith('impacto alto')
    circles=row.locator('.calendar-impact-bar').evaluate_all('nodes=>nodes.map(n=>{const s=getComputedStyle(n);return {w:n.getBoundingClientRect().width,h:n.getBoundingClientRect().height,r:s.borderRadius}})')
    assert all(abs(n['w']-6)<=EPSILON and abs(n['h']-6)<=EPSILON and n['r']=='50%' for n in circles),circles
    footer=panel.locator('.calendar-agenda-footer');expect(footer).to_be_visible()
    expect(footer).to_contain_text('Horários de');expect(footer).to_contain_text('15:12')
    expect(footer.locator('.calendar-footer-coverage')).to_have_count(0)
    month=panel.locator('.calendar-month').evaluate('n=>({html:n.outerHTML,width:n.getBoundingClientRect().width})')
    header=panel.locator('.calendar-header').evaluate('n=>n.outerHTML')
    saved=page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY)})')
    panel.locator('.calendar-economic-scroll').focus();page.keyboard.press('Tab')
    expect(row).to_be_focused()
    assert row.evaluate('n=>{const s=getComputedStyle(n);return s.outlineStyle!=="none"&&parseFloat(s.outlineWidth)>=2}'), 'Keyboard row focus is visible'
    page.keyboard.press('Enter')
    expect(row).to_have_attribute('aria-expanded','true')
    target=panel.locator('#'+row.get_attribute('aria-controls'));expect(target).to_be_visible()
    expect(target).to_contain_text('Congressional Elections')
    for field in ['actual','forecast','previous']:expect(target.locator('[data-calendar-detail-value="'+field+'"]')).to_have_text('–')
    page.keyboard.press('Space');expect(row).to_have_attribute('aria-expanded','false')
    row.locator('.calendar-economic-currency').click();expect(row).to_have_attribute('aria-expanded','true')
    row.click();expect(row).to_have_attribute('aria-expanded','false')
    assert panel.locator('.calendar-month').evaluate('n=>({html:n.outerHTML,width:n.getBoundingClientRect().width})')==month
    assert panel.locator('.calendar-header').evaluate('n=>n.outerHTML')==header
    assert work.evaluate('p=>p.outerHTML')==workspace, 'Modal reading must leave the workspace unchanged'
    footer.get_by_role('button',name='Fontes e cobertura ›').click()
    expect(panel.locator('.calendar-info')).to_be_visible()
    footer.get_by_role('button',name='Fontes e cobertura ›').click()
    expect(panel.locator('.calendar-info')).not_to_be_visible()
    geometry=assert_layout(panel);assert_compact_rows(panel)
    if kind=='modal-many':
        page.evaluate('async()=>{__modalVisual.count=12;__modalVisual.precision="instant";await JPWCalendar.refresh()}')
        expect(panel.locator('[data-calendar-economic-id]')).to_have_count(12)
        expect(panel.locator('.calendar-agenda-summary')).to_have_text('12 eventos')
        geometry=assert_layout(panel);assert_compact_rows(panel)
        long=panel.locator('.calendar-event-title').nth(1)
        assert long.evaluate('n=>{const s=getComputedStyle(n);return n.clientHeight<=2*parseFloat(s.lineHeight)+1 && getComputedStyle(n).webkitLineClamp==="2"}'), 'Long names clamp only after two lines'
        expect(panel.locator('.calendar-economic-time-note').first).to_have_attribute('title','Horário não confirmado')
        for i,filled in enumerate([3,2,1]):assert panel.locator('[data-calendar-economic-id]').nth(i).locator('.calendar-impact-filled').count()==filled
        expect(panel.locator('.calendar-impact-unclassified')).to_have_attribute('aria-label','Impacto não classificado · Forex Factory')
        panel.locator('[data-calendar-economic-id]').last.scroll_into_view_if_needed()
        panel.locator('[data-calendar-economic-id]').last.focus()
        scroll_host=panel.locator('.calendar-agenda') if panel.locator('.calendar-agenda').evaluate('n=>n.scrollHeight>n.clientHeight+1') else page.locator('#calendarDialog')
        scroll=scroll_host.evaluate('n=>n.scrollTop')
        assert scroll>0,'Twelve events exercise genuine vertical scrolling'
        page.evaluate('async()=>{await JPWCalendar.refresh()}')
        expect(panel.locator('[data-calendar-economic-id]').last).to_be_focused()
        after_scroll=scroll_host.evaluate('n=>n.scrollTop')
        assert after_scroll==scroll, {'owner':scroll_host.get_attribute('id') or 'agenda','before':scroll,'after':after_scroll}
        assert_values(panel,page.evaluate('JPWEconomicCalendar.queryRange({}).events'))
    if kind=='modal-empty':
        page.evaluate('async()=>{__modalVisual.count=0;await JPWCalendar.refresh()}')
        expect(panel.locator('.calendar-empty')).to_have_text('Nenhum evento')
        expect(panel.locator('.calendar-economic-table')).to_have_count(0)
        page.evaluate('async()=>{__modalVisual.complete=false;await JPWCalendar.refresh()}')
        expect(panel.locator('.calendar-empty')).not_to_have_text('Nenhum evento')
        expect(footer.locator('.calendar-footer-coverage')).to_contain_text('Cobertura parcial')
        page.evaluate('async()=>{__modalVisual.failed=true;await JPWCalendar.refresh()}')
        expect(panel.locator('.calendar-empty')).to_contain_text('Não foi possível')
    if kind=='modal-states':
        page.evaluate('async()=>{__modalVisual.complete=false;__modalVisual.stale=true;await JPWCalendar.refresh()}')
        expect(footer.locator('.calendar-footer-coverage')).to_contain_text('Cobertura parcial')
        expect(footer).to_contain_text('Coleta desatualizada')
        page.evaluate('async()=>{__modalVisual.collected=false;await JPWCalendar.refresh()}')
        expect(footer).to_contain_text('Coleta não informada')
        assert '15:12' not in footer.inner_text(), 'Package reference cannot invent a collection time'
        page.evaluate('async()=>{__modalVisual.failed=true;await JPWCalendar.refresh()}')
        expect(footer).to_contain_text('Falha')
    assert page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY)})')==saved, 'Presentation must not write financial state'
    return {'geometry':geometry,'impact_points':circles,'workspace_initial_read_unchanged':True,'financial_readonly':True,'kind':kind}

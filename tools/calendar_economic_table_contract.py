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
    for event in events:
        row=panel.locator('[data-calendar-economic-id='+json.dumps(event['id'])+']')
        expect(row).to_have_count(1)
        assert set(row.locator('[data-calendar-economic-field]').evaluate_all('ns=>ns.map(n=>n.dataset.calendarEconomicField)'))==set(FIELDS), 'Every row retains all7 fields'
        for field,expected in [('actual','—'),('forecast',event.get('forecast') or '—'),('previous',event.get('previous') or '—')]:
            cell=row.locator('[data-calendar-economic-field="'+field+'"]')
            expect(cell).to_be_visible()
            assert value(cell,LABELS[field])==expected, (event['id'],field,expected,cell.inner_text())
        # Absence is explained accessibly without assuming the source publishes Actual.
        actual=row.locator('[data-calendar-economic-field="actual"]')
        explanation=actual.evaluate(r'''n=>{
          const referenced=(n.getAttribute('aria-describedby')||'').split(/\s+/).filter(Boolean).map(id=>document.getElementById(id)?.textContent||'').join(' ');
          const visibleNotes=[...n.closest('.calendar-panel').querySelectorAll('p,[role="note"]')].filter(e=>e.getClientRects().length&&!e.hidden).map(e=>e.textContent).join(' ');
          return [n.getAttribute('aria-label')||'',referenced,visibleNotes].join(' ').toLowerCase();
        }''')
        assert 'atual' in explanation and ('não colet' in explanation or 'não dispon' in explanation or 'sem resultado' in explanation or 'não fornecid' in explanation), ('Actual absence needs a clear accessible explanation',explanation)
        observed.append({'id':event['id'],'forecast':event.get('forecast') or '—','previous':event.get('previous') or '—','actual':'—'})
    return observed


def assert_layout(panel, *, natural_wide=False):
    data=panel.evaluate('''panel=>{
      const box=e=>e.getBoundingClientRect().toJSON(),visible=e=>e.getClientRects().length&&!e.hidden&&getComputedStyle(e).visibility!=='hidden';
      const body=panel.querySelector('.calendar-body'),month=panel.querySelector('.calendar-month'),agenda=panel.querySelector('.calendar-agenda'),s=getComputedStyle(body);
      return {panel:box(panel),body:box(body),month:box(month),agenda:box(agenda),
        useful:body.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight),
        agendaUseful:agenda.clientWidth-parseFloat(getComputedStyle(agenda).paddingLeft)-parseFloat(getComputedStyle(agenda).paddingRight),
        headings:[...agenda.querySelectorAll('th,[role="columnheader"]')].filter(e=>visible(e)&&e.getBoundingClientRect().width>2&&e.getBoundingClientRect().height>2).map(e=>e.textContent.trim()),
        headerBoxes:[...agenda.querySelectorAll('th,[role="columnheader"]')].filter(e=>visible(e)&&e.getBoundingClientRect().width>2&&e.getBoundingClientRect().height>2).map(box),
        overflow:[panel,body,agenda,...agenda.querySelectorAll('[data-calendar-economic-id]')].map(e=>({name:e.id||e.className,scroll:e.scrollWidth,client:e.clientWidth})),
        rows:[...agenda.querySelectorAll('[data-calendar-economic-id]')].map(e=>({box:box(e),fields:[...e.querySelectorAll('[data-calendar-economic-field]')].filter(visible).map(n=>({name:n.dataset.calendarEconomicField,box:box(n),text:n.innerText,numericInk:(()=>{const v=n.querySelector('[data-calendar-economic-value]');if(!v)return null;const range=document.createRange();range.selectNodeContents(v);const ink=[...range.getClientRects()].filter(r=>r.width>0);return {right:Math.max(...ink.map(r=>r.right)),expectedRight:n.getBoundingClientRect().right-parseFloat(getComputedStyle(n).paddingRight)};})(),label:n.getAttribute('data-label'),labelText:[...n.querySelectorAll('*')].filter(visible).map(x=>x.innerText)}))}))};
    }''')
    assert all(o['scroll']<=o['client']+1 for o in data['overflow']), ('No horizontal overflow',data['overflow'])
    if data['useful']<700-EPSILON:
        assert data['agenda']['top']>=data['month']['bottom']-TOLERANCE, ('Stack below700 useful CSSpx',data)
    else:
        assert abs(data['month']['width']-308)<=TOLERANCE, ('Month grid gets308 CSSpx beside economic area',data)
        assert data['agenda']['left']>=data['month']['right']-TOLERANCE, ('Agenda beside month',data)
    wide=data['agendaUseful']>=720-EPSILON
    if natural_wide:assert wide, ('Seven columns must be reachable in natural wide workspace',data)
    assert data['headings']==(list(HEADERS) if wide else []), ('Seven headers only when economic area>=720',data)
    for row in data['rows']:
        assert len(row['fields'])==7, ('All fields visible',row)
        fields={f['name']:f for f in row['fields']}
        for key in FIELDS[4:]:
            ink=fields[key]['numericInk']
            assert ink and abs(ink['right']-ink['expectedRight'])<=TOLERANCE, ('Numeric ink must align right within its own cell',key,ink)
        if wide:
            for key,header in zip(FIELDS,data['headerBoxes']):
                cell=fields[key]['box']
                assert abs(header['left']-cell['left'])<=TOLERANCE and abs(header['right']-cell['right'])<=TOLERANCE, ('Real header and cell column bounds align within2 CSSpx',key,header,cell)
            assert max(f['box']['top'] for f in fields.values())-min(f['box']['top'] for f in fields.values())<=TOLERANCE, ('Wide fields align in one row',row)
            for first,second in zip(FIELDS,FIELDS[1:]):assert fields[first]['box']['right']<=fields[second]['box']['left']+TOLERANCE, ('Seven ordered columns',row)
        else:
            top=[fields[k]['box'] for k in FIELDS[:4]];bottom=[fields[k]['box'] for k in FIELDS[4:]]
            assert min(b['top'] for b in bottom)>=max(b['bottom'] for b in top)-TOLERANCE, ('Identity above all values',row)
            assert max(b['top'] for b in bottom)-min(b['top'] for b in bottom)<=TOLERANCE, ('Three values share the second band',row)
            for key in FIELDS[4:]:
                f=fields[key];label=LABELS[key]
                assert label in f['text'] or (f['label']==label and panel.locator('[data-calendar-economic-field="'+key+'"]').first.evaluate('n=>getComputedStyle(n,"::before").content').strip('"') in (label,label+':')), ('Compact values need visible labels',key,f)
    for toggle in controls(panel).all():
        b=toggle.bounding_box();assert b and b['width']>=44-EPSILON and b['height']>=44-EPSILON, ('44px detail target',b)
        parent=toggle.locator('xpath=..')
        assert parent.locator('[data-calendar-economic-field="event"]').count() or toggle.locator('xpath=ancestor::*[@data-calendar-economic-field="event"]').count(), 'i belongs to Evento cell'
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
    before=page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem(LSKEY),cache:localStorage.getItem("jpwealth.ui.ffNews.v1")})')
    panel=setup(page)
    expected=page.evaluate("JPWEconomicCalendar.queryRange({}).events")
    if kind=='table-compact':
        page.locator('#headerCalendarBtn').click();panel=page.locator('#calendarDialog .calendar-panel')
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
    if kind=='table-boundaries':
        boundaries=[]
        host=page.locator('#execEcal')
        for area,target in [('useful',699),('useful',700),('agendaUseful',719),('agendaUseful',720)]:
            # Resize the container with a fixed viewport. This does not force
            # columns, visibility, media queries or the product's resize observer.
            for adjustment in range(2):
                current=assert_layout(panel)[area] if adjustment else panel.evaluate("(p,k)=>{const n=p.querySelector(k==='useful'?'.calendar-body':'.calendar-agenda'),s=getComputedStyle(n);return n.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight)}",area)
                host.evaluate('(n,delta)=>{n.style.maxWidth="none";n.style.width=(n.getBoundingClientRect().width+delta)+"px"}',target-current)
                page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
            measured=assert_layout(panel)
            assert abs(measured[area]-target)<=EPSILON,(area,target,measured)
            boundaries.append({'area':area,'target':target,'observed':measured})
        geometry={'boundaries':boundaries}
    if kind=='table-state':
        # Critical statuses remain legible while secondary provenance is closed.
        rows=panel.locator('[data-calendar-economic-id]')
        assert 'Cancelado' in rows.nth(2).inner_text()
        assert 'última coleta' in rows.nth(3).inner_text()
        assert 'diverg' in rows.nth(4).inner_text().lower()
        toggles=controls(panel);targets=details(panel)
        first=toggles.nth(0);first.focus();page.keyboard.press('Enter')
        expect(first).to_have_attribute('aria-expanded','true');expect(targets[0]).to_be_visible()
        expect(targets[0]).to_contain_text('Horário original')
        assert targets[0].get_by_role('link').count()>=2, 'FF and official references remain available'
        toggles.nth(1).focus();page.keyboard.press('Space')
        expect(toggles.nth(1)).to_have_attribute('aria-expanded','true');expect(targets[0]).not_to_be_visible()
        assert sum(t.is_visible() for t in details(panel))==1, 'Only one expanded detail per host'
        first.click();first.focus()
        # Constrain only the scroll viewport, then use a real nonzero scroll.
        agenda=panel.locator('.calendar-agenda');agenda.evaluate("n=>{n.style.maxHeight='160px';n.scrollTop=48}")
        scrolled=agenda.evaluate('n=>n.scrollTop');assert scrolled>0,'Scroll stimulus must be nonzero'
        marker_count=panel.locator('.calendar-economic-dot').count()
        page.evaluate('async()=>{__table.generation++;await JPWCalendar.refresh()}')
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

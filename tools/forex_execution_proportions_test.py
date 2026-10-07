#!/usr/bin/env python3
"""Approved compact Execution Board contract, CHG ...PROPORTIONS-TEST-20261005.

Uses the live product and existing disposable synthetic fixture. No financial
oracle, fixture or persistence writer is substituted. This focal is separate
from the unchanged financial assertions of forex_execution_workbook_test.py.
"""
import argparse
from functools import partial
import hashlib
import json
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, assert_fixture_requests
from forex_clarity_test import SEED
from forex_execution_table_test import Server, Quiet, ready, field, persisted, order, set_field, HASH, prepare_drafts
from forex_execution_workbook_test import hashes, seed
from forex_execution_table_test import select_tool as tool
from notes_launcher_test import launch_options, settle

ROOT = Path(__file__).resolve().parents[1]


def financial(page):
    # Preferences/layout changes are legitimate test setup; compare financial
    # state and its persisted envelope, not local presentation preferences.
    value = persisted(page)
    return {'state': value['state'], 'raw': value['raw']}


def controls(page):
    return page.locator('[data-eb-row="0:0"]').evaluate("""row=>{
      const rect=e=>{const r=e.getBoundingClientRect(),c=getComputedStyle(e);return {
        width:r.width,height:r.height,font:parseFloat(c.fontSize),left:r.left,top:r.top,
        whiteSpace:c.whiteSpace,overflow:c.textOverflow,position:c.position};};
      const actions=[...row.querySelectorAll('[data-eb-save-row],[data-eb-cancel-row],[data-eb-open-detail]')];
      return {row:rect(row),columns:row.children.length,
        editors:[...row.querySelectorAll('input,select')].map(e=>({field:e.dataset.f,value:e.value,...rect(e)})),
        actions:actions.map(e=>({label:e.textContent.trim(),accessible:e.getAttribute('aria-label'),disabled:e.disabled,...rect(e)})),
        instrument:rect(row.children[1]),role:rect(row.children[3])};
    }""")


def screenshot(page, out, name):
    scroll=page.locator('#ebOrderScroll')
    scroll.scroll_into_view_if_needed()
    settle(page)
    page.screenshot(path=str(out/(name+'.png')))


def empty_phases(page, out, observed):
    page.evaluate(SEED)
    settle(page)
    before=financial(page)
    assert page.locator('.eb-order-row').count()==0
    assert page.locator('.eb-phase-row').count()==6
    assert page.locator('.eb-empty-phase').count()==0, 'Empty phase adds an unnecessary second row'
    measurements=page.locator('.eb-phase-row').evaluate_all("""rows=>rows.map(e=>({
      text:e.innerText,height:e.getBoundingClientRect().height,buttons:e.querySelectorAll('[data-addorder]').length}))""")
    for item in measurements:
        assert '0 ordens' in item['text'] and item['buttons']==1, item
        assert 44<=item['height']<=56, ('Empty desktop phase should occupy one compact strip',item)
    button=page.locator('[data-addorder="0"]')
    button.click()
    settle(page)
    assert page.locator('.eb-order-row').count()==1
    assert page.locator('[data-eb-row="0:1"]').is_visible()
    after_add=financial(page)
    assert after_add!=before, 'Explicit Add must remain the existing factual draft command'
    screenshot(page,out,'compact-empty-and-added')
    observed['phases']=measurements


def compact_and_details(page, out, observed):
    seed(page)
    before=financial(page)
    m=controls(page)
    assert m['columns']==20
    for e in m['editors']:
        assert abs(e['font']-14)<.15 and 36<=e['height']<=38, e
    assert 48<=m['row']['height']<=56, ('Common desktop row is too tall',m)
    assert m['instrument']['width']>=144 and m['role']['width']>=140, m
    assert len(m['actions'])==3 and all(a['accessible'] for a in m['actions']),m
    assert max(a['top'] for a in m['actions'])-min(a['top'] for a in m['actions'])<1, ('Actions wrap',m)
    assert m['actions'][0]['disabled'] and m['actions'][1]['disabled'], m
    assert not m['actions'][2]['disabled'], m
    details=page.locator('[data-eb-detail="0:0"]')
    assert not details.evaluate('e=>e.open')
    assert details.evaluate("e=>e.closest('tr').getBoundingClientRect().height===0"), 'Closed detail still reserves space'
    detail_field=field(page,'brokerHash').element_handle()
    toggle=page.locator('[data-eb-open-detail="0:0"]')
    toggle.click()
    settle(page)
    assert details.evaluate('e=>e.open') and details.is_visible()
    assert toggle.get_attribute('aria-expanded')=='true'
    assert detail_field.evaluate('e=>e.isConnected')
    field(page,'brokerHash').focus()
    toggle.click()
    settle(page)
    assert not details.evaluate('e=>e.open')
    assert toggle.get_attribute('aria-expanded')=='false'
    assert detail_field.evaluate('e=>e.isConnected'), 'Closing detail destroyed an editor'
    assert toggle.evaluate('e=>document.activeElement===e')
    # One editor per field and ordinary native Tab order, including the far-right
    # actions; hidden detail fields must not enter this sequence.
    fields=['id','par','tipo','role','lote','entry','sl','tp','status']
    field(page,'id').focus()
    for index,key in enumerate(fields):
        if index: page.keyboard.press('Tab')
        assert field(page,key).evaluate('e=>document.activeElement===e'),('Tab sequence',key)
        assert field(page,key).evaluate('e=>{const r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))}'),('Focused editor obscured',key)
    page.keyboard.press('Tab')
    assert toggle.evaluate('e=>document.activeElement===e'),'Disabled Save/Cancel and hidden details should be skipped'
    assert financial(page)==before
    screenshot(page,out,'compact-desktop')
    observed.update(measurements=m,closedDetailZeroHeight=True,detailEditorsMounted=True)


def drafts_focus_validation(page, out, observed):
    seed(page)
    before=financial(page)
    set_field(page,'id','SYNTHETIC-LONG-ID-000123')
    set_field(page,'entry','1.23456789')
    assert page.locator('[data-eb-save-row="0:0"]').is_enabled()
    assert page.locator('[data-eb-cancel-row="0:0"]').is_enabled()
    preview=page.locator('[data-eb-row="0:0"] [data-eb-preview]')
    assert preview.count()==1 and 'Não salvo' in preview.inner_text()
    input_node=field(page,'entry').element_handle()
    input_node.evaluate('e=>{e.focus();e.setSelectionRange(2,6)}')
    page.keyboard.press('Tab')
    assert field(page,'sl').evaluate('e=>document.activeElement===e')
    page.keyboard.press('Shift+Tab')
    assert input_node.evaluate('e=>document.activeElement===e')
    input_node.evaluate('e=>e.setSelectionRange(2,6)')
    page.locator('#ebOrderScroll').evaluate('e=>{e.scrollLeft=480;window.__compactLeft=e.scrollLeft}')
    for selected in ['rootn','motor','matrix']:
        tool(page,selected)
        assert input_node.evaluate('e=>e.isConnected&&e.selectionStart===2&&e.selectionEnd===6')
        assert page.locator('#ebOrderScroll').evaluate('e=>e.scrollLeft===window.__compactLeft')
        assert field(page,'entry').input_value()=='1.23456789'
        assert financial(page)==before
    for width in [390,1440]:
        page.set_viewport_size({'width':width,'height':1000})
        settle(page)
        assert input_node.evaluate('e=>e.isConnected'), 'Responsive change replaced the editor'
        assert field(page,'entry').input_value()=='1.23456789'
        assert financial(page)==before
    page.locator('[data-eb-cancel-row="0:0"]').click()
    settle(page)
    assert financial(page)==before and not page.evaluate('JPWForex.executionBoardUI.hasDrafts()')
    assert page.locator('[data-eb-save-row="0:0"]').is_disabled()
    assert field(page,'id').evaluate('e=>document.activeElement===e'), 'Cancel must return focus to the same order'
    values=dict(id='COMPACT-001',par='EURUSD',tipo='BUY',role='GENESIS',lote='0.2',entry='1.2',sl='1.17',tp='1.26',status='Aberta')
    for key,value in values.items(): set_field(page,key,value)
    page.locator('[data-eb-save-row="0:0"]').click()
    settle(page)
    assert field(page,'brokerHash').is_visible() and field(page,'brokerHash').evaluate('e=>document.activeElement===e')
    assert field(page,'brokerHash').get_attribute('aria-invalid')=='true'
    assert page.locator('[data-eb-detail="0:0"]').evaluate('e=>e.open')
    assert financial(page)==before, 'Validation failure wrote financial data'
    set_field(page,'brokerHash',HASH)
    set_field(page,'costs','0')
    set_field(page,'costBasis','SEPARATE_FROM_RESULT')
    set_field(page,'stopValidated',True)
    page.locator('[data-eb-save-row="0:0"]').click()
    settle(page)
    assert order(page)['recordVersion']==1
    assert page.locator('[data-eb-save-row="0:0"]').is_disabled()
    assert page.locator('[data-eb-cancel-row="0:0"]').is_disabled()
    assert field(page,'id').evaluate('e=>document.activeElement===e'), 'Save must return focus to the same order'
    screenshot(page,out,'compact-confirmed-and-focus')
    observed.update(tabOrder=True,draftPreservedAcrossToolsAndResize=True,failedValidationRevealsDetail=True,explicitSaveVersion=1)


def populate(page,count):
    page.evaluate(SEED)
    settle(page)
    page.evaluate("""count=>{
      const scope=JPWForex.state.operationalSelection();
      const phases=S.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId].phases;
      phases.forEach(p=>{p.orders=[]});
      if(save()!==true)throw Error('Synthetic layout reset refused');
      for(let i=0;i<count;i++){const r=operationAddDraft(i%phases.length);if(!r.ok)throw Error(JSON.stringify(r));}
      renderPhases();
    }""",count)
    settle(page)


def population(page,out,observed):
    sizes=[]
    for count in [1,10,30]:
        populate(page,count)
        before=financial(page)
        assert page.locator('.eb-order-row').count()==count
        assert page.locator('.eb-order-table').count()==1
        assert page.locator('.eb-phase-row').count()==6
        assert page.locator('details[data-phase]').count()==0
        assert page.locator('.eb-order-row').evaluate_all("rows=>rows.every(e=>e.children.length===20)")
        page.locator('.eb-order-row').last.scroll_into_view_if_needed()
        settle(page)
        assert page.locator('.eb-order-row').last.is_visible()
        assert financial(page)==before
        rows=page.locator('.eb-order-row').evaluate_all('rows=>rows.map(e=>e.getBoundingClientRect().height)')
        assert all(48<=h<=56 for h in rows),(count,rows)
        sizes.append({'orders':count,'heights':rows})
        screenshot(page,out,f'compact-{count}-orders')
    observed['populations']=sizes


def layout_matrix(page,out,observed,layout):
    seed(page)
    page.evaluate('l=>mountNavigationLayout(l)',layout)
    settle(page)
    observed['measurements']=[]
    for width in [1440,1024,768,390,320]:
        page.set_viewport_size({'width':width,'height':1000 if width>900 else 844})
        for theme in ['light','dark']:
            page.evaluate("t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}",theme)
            settle(page)
            before=financial(page)
            box=page.locator('#ebOrderScroll').evaluate("e=>({width:e.clientWidth,scroll:e.scrollWidth,mode:getComputedStyle(e.querySelector('.eb-order-row')).display})")
            compact=box['width']>=768
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(layout,width,theme,'global overflow')
            assert box['mode']==('table-row' if compact else 'grid'),(layout,width,theme,box)
            m=controls(page)
            minfont,target=(14,36) if compact else (16,48)
            for e in m['editors']:
                assert abs(e['font']-minfont)<.2 and e['height']>=target-.1,(layout,width,theme,e)
            for a in m['actions']:
                assert a['width']>=target-.1 and a['height']>=target-.1,(layout,width,theme,a)
            if compact:
                assert m['row']['height']<=56,(layout,width,theme,m)
                assert m['instrument']['position']=='sticky'
                assert page.locator('#ebOrderScroll').evaluate('e=>{e.scrollLeft=500;return e.scrollLeft>0}')
                assert max(a['top'] for a in m['actions'])-min(a['top'] for a in m['actions'])<1
            else:
                assert box['scroll']<=box['width']+1,(layout,width,theme,box)
                assert m['instrument']['position']=='static'
            # Native selects must have room for their selected labels. This is a
            # text measurement, independent of the column dimensions themselves.
            fit=page.locator('[data-eb-row="0:0"] select').evaluate_all("""els=>els.map(e=>{
              const c=getComputedStyle(e),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=c.font;
              return {field:e.dataset.f,text:e.selectedOptions[0]?.textContent||'',need:ctx.measureText(e.selectedOptions[0]?.textContent||'').width+parseFloat(c.paddingLeft)+parseFloat(c.paddingRight)+20,width:e.clientWidth};})""")
            assert all(x['need']<=x['width']+1 for x in fit),(layout,width,theme,'select label clipped',fit)
            assert financial(page)==before
            observed['measurements'].append({'layout':layout,'viewport':width,'theme':theme,**box,'row':m['row'],'selects':fit})
            if width in [1440,390]: screenshot(page,out,f'compact-{layout}-{width}-{theme}')


def long_values(page,out,observed):
    page.evaluate(SEED)
    settle(page)
    # A deliberately long *synthetic* catalogue name exercises the same select
    # renderer. No real catalog, user data or historical fixture is changed.
    name='EURUSD.SYNTHETIC-LONG-INSTRUMENT-000123456789'
    page.evaluate("name=>{S.instruments.push({...S.instruments[0],name});}",name)
    # Catalogue setup precedes creation of the disposable explicit rows, so the
    # existing renderer mounts real select options rather than stale test DOM.
    prepare_drafts(page)
    before=financial(page)
    set_field(page,'par',name)
    set_field(page,'id','SYNTHETIC-ORDER-WITH-LONG-ID-000123456789')
    set_field(page,'entry','123456789.123456789')
    set_field(page,'lote','123456789.123456')
    set_field(page,'sl','0.000000123456789')
    set_field(page,'tp','987654321.123456789')
    measures=page.locator('[data-eb-row="0:0"] input,[data-eb-row="0:0"] select').evaluate_all("""els=>els.map(e=>{
      const c=getComputedStyle(e),ctx=document.createElement('canvas').getContext('2d');ctx.font=c.font;
      const text=e.tagName==='SELECT'?e.selectedOptions[0]?.textContent:e.value;
      return {field:e.dataset.f,text,width:e.clientWidth,
        need:ctx.measureText(text||'').width+parseFloat(c.paddingLeft)+parseFloat(c.paddingRight)+(e.tagName==='SELECT'?22:4),ellipsis:c.textOverflow};})""")
    assert all(m['need']<=m['width']+1 for m in measures),('Value clipped despite table local overflow',measures)
    assert all(m['ellipsis']!='ellipsis' for m in measures),measures
    assert field(page,'entry').input_value()=='123456789.123456789'
    assert field(page,'sl').input_value()=='0.000000123456789'
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert financial(page)==before,'Editing/rendering long values wrote facts'
    # Smaller replacement values do not make columns oscillate while editing.
    widths=page.locator('.eb-workbook-table col').evaluate_all('els=>els.map(e=>e.getBoundingClientRect().width)')
    set_field(page,'entry','1.2')
    after=page.locator('.eb-workbook-table col').evaluate_all('els=>els.map(e=>e.getBoundingClientRect().width)')
    assert all(b>=a-.1 for a,b in zip(widths,after)),(widths,after)
    assert financial(page)==before
    screenshot(page,out,'compact-long-values')
    observed.update(fields=measures,valuesNotPersisted=True,columnsDoNotShrinkWhileTyping=True)


def long_frozen_identity(page,out,observed):
    seed(page)
    before=financial(page)
    editor=field(page,'entry').element_handle()
    identifier='SYNTHETIC-'+('1234567890'*10)
    set_field(page,'id',identifier)
    set_field(page,'entry','1.23456789')
    # A long frozen ID must not cover every other column at a desktop width.
    assert page.locator('[data-eb-row="0:0"]').evaluate("e=>getComputedStyle(e).display==='grid'"),'Long frozen identity should use the accessible list when <320px remains'
    field(page,'entry').focus()
    assert editor.evaluate('e=>e.isConnected&&document.activeElement===e')
    assert editor.evaluate('e=>{const r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))}'),'Frozen identity obscures the editor'
    assert field(page,'id').input_value()==identifier
    assert financial(page)==before
    screenshot(page,out,'compact-long-identity-adaptive')
    page.set_viewport_size({'width':2560,'height':1000})
    settle(page)
    # The page has a maximum useful width: 110 characters still leave less
    # than 320px here. Viewport width alone is not evidence of available space.
    assert page.locator('[data-eb-row="0:0"]').evaluate("e=>getComputedStyle(e).display==='grid'")
    assert financial(page)==before
    page.locator('[data-eb-cancel-row="0:0"]').click()
    settle(page)
    identifier='SYNTHETIC-'+('1234567890'*6)+'12345'
    page.set_viewport_size({'width':1440,'height':1000})
    settle(page)
    editor=field(page,'entry').element_handle()
    set_field(page,'id',identifier)
    set_field(page,'entry','1.23456789')
    observations=[]
    for width,mode in [(2560,'table-row'),(1440,'grid'),(390,'grid'),(2560,'table-row')]:
        page.set_viewport_size({'width':width,'height':1000})
        settle(page)
        assert page.locator('[data-eb-row="0:0"]').evaluate('(e,mode)=>getComputedStyle(e).display===mode',mode),(width,mode)
        assert editor.evaluate('e=>e.isConnected') and field(page,'entry').input_value()=='1.23456789'
        assert field(page,'id').input_value()==identifier
        assert financial(page)==before
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        observations.append({'viewport':width,'mode':mode,'entry':field(page,'entry').input_value(),'idLength':len(identifier)})
    observed.update(resizes=observations,editorNotReplaced=True,noFinancialWrites=True)


def mobile_action_focus(page,out,observed):
    seed(page)
    before=financial(page)
    observed['focus']=[]
    def check(label):
        measured=field(page,'id').evaluate("""e=>{const r=e.getBoundingClientRect();return {
          active:document.activeElement===e,top:r.top,bottom:r.bottom,viewport:innerHeight,
          hit:e.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))};}""")
        observed['focus'].append({'action':label,**measured})
        assert measured['active'] and measured['hit'] and measured['top']>=0 and measured['bottom']<=measured['viewport'],('Action returned focus outside the visible mobile viewport',label,measured)
    for width in [390,320]:
        page.set_viewport_size({'width':width,'height':844})
        settle(page)
        set_field(page,'entry','1.23456789')
        page.locator('[data-eb-cancel-row="0:0"]').click()
        settle(page)
        check('Cancel '+str(width))
        assert financial(page)==before
    page.set_viewport_size({'width':390,'height':844})
    settle(page)
    values=dict(id='MOBILE-FOCUS',par='EURUSD',tipo='BUY',role='GENESIS',lote='0.2',entry='1.2',sl='1.17',tp='1.26',status='Aberta',brokerHash=HASH,costs='-1.25',costBasis='SEPARATE_FROM_RESULT',stopValidated=True)
    for key,value in values.items():set_field(page,key,value)
    assert financial(page)==before
    page.locator('[data-eb-save-row="0:0"]').click()
    settle(page)
    assert order(page)['recordVersion']==1 and order(page)['costs']==-1.25
    check('Save 390')
    saved=financial(page)
    page.set_viewport_size({'width':320,'height':844})
    settle(page)
    set_field(page,'sl','1.192')
    page.locator('[data-eb-cancel-row="0:0"]').click()
    settle(page)
    check('Cancel confirmed 320')
    assert financial(page)==saved and field(page,'sl').input_value()=='1.17'
    page.keyboard.press('Tab')
    assert field(page,'par').evaluate('e=>document.activeElement===e')
    assert field(page,'par').evaluate('e=>{const r=e.getBoundingClientRect();return e.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))}')
    screenshot(page,out,'compact-mobile-action-focus')


def header_contrast(page,out,observed):
    seed(page)
    before=financial(page)
    observed['headers']=[]
    failures=[]
    for layout in ['sidebar','topbar','glass','submenu']:
        page.evaluate('l=>mountNavigationLayout(l)',layout)
        for theme in ['light','dark']:
            page.evaluate("t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}",theme)
            settle(page)
            measured=page.locator('.eb-column-labels th').evaluate_all("""els=>{
              const rgba=s=>{const v=s.match(/[\d.]+/g)?.map(Number)||[0,0,0,0];return [v[0],v[1],v[2],v.length>3?v[3]:1];};
              const over=(a,b)=>a.slice(0,3).map((x,i)=>x*a[3]+b[i]*(1-a[3]));
              const bg=e=>{if(!e)return [255,255,255];const c=rgba(getComputedStyle(e).backgroundColor);return c[3]>=1?c.slice(0,3):over(c,bg(e.parentElement));};
              const luminance=c=>c.map(x=>{x/=255;return x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4);}).reduce((s,x,i)=>s+x*[.2126,.7152,.0722][i],0);
              return els.map(e=>{const c=getComputedStyle(e),back=bg(e),front=over(rgba(c.color),back),l=[luminance(front),luminance(back)];
                return {label:e.textContent.trim(),foreground:front,background:back,font:parseFloat(c.fontSize),ratio:(Math.max(...l)+.05)/(Math.min(...l)+.05)};});
            }""")
            assert len(measured)==20
            observed['headers'].append({'layout':layout,'theme':theme,'values':measured})
            failures.extend({'layout':layout,'theme':theme,**x} for x in measured if x['ratio']<4.5)
            assert financial(page)==before,'Header/theme inspection wrote financial state'
    observed['failures']=failures
    assert not failures,('Operational column heading contrast below4.5:1',failures)


def font_scales(page,out,observed):
    seed(page)
    observations=[]
    for scale in [1,1.12,1.25]:
        page.evaluate("s=>document.documentElement.style.setProperty('--fs-scale',String(s))",scale)
        for width in [1440,390]:
            page.set_viewport_size({'width':width,'height':1000 if width>900 else 844})
            settle(page)
            before=financial(page)
            m=controls(page)
            compact=page.locator('#ebOrderScroll').evaluate('e=>e.clientWidth>=768')
            for e in m['editors']:
                assert e['font']>=((14 if compact else 16)*scale)-.2,(scale,width,e)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            if compact:
                assert max(a['top'] for a in m['actions'])-min(a['top'] for a in m['actions'])<1,(scale,width,m)
                assert m['instrument']['width']>=144*scale-.1 and m['role']['width']>=140*scale-.1,(scale,width,m)
            assert financial(page)==before
            observations.append({'scale':scale,'width':width,**m})
    screenshot(page,out,'compact-font125-mobile')
    observed['scales']=observations


def touch(page,out,observed):
    seed(page)
    assert page.evaluate("matchMedia('(pointer:coarse)').matches")
    before=financial(page)
    m=controls(page)
    for e in m['editors']:
        assert e['font']>=16 and e['height']>=48,e
    for a in m['actions']:
        assert a['width']>=48 and a['height']>=48,a
    assert financial(page)==before
    screenshot(page,out,'compact-desktop-touch')
    observed['measurements']=m


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--cases',help='Comma-separated case names; omitted runs all')
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    before=hashes(args.root)
    report={'root':str(args.root),'source_sha256':before,'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':[],'classification':'NOT_RUN'}
    server=Server(('127.0.0.1',0),partial(Quiet,directory=str(args.root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    cases=[('empty-phases',empty_phases),('compact-and-details',compact_and_details),('drafts-focus-validation',drafts_focus_validation),('populations',population)]
    cases += [('layout-'+layout,partial(layout_matrix,layout=layout)) for layout in ['sidebar','topbar','glass','submenu']]
    cases += [('long-values',long_values),('long-frozen-identity',long_frozen_identity),('header-contrast',header_contrast),('mobile-action-focus',mobile_action_focus),('font-scales',font_scales),('desktop-touch',touch)]
    chosen=set(args.cases.split(',')) if args.cases else None
    try:
        if chosen and chosen.difference(name for name,_ in cases): raise ValueError('Unknown cases '+str(chosen))
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options())
            report['browser']=browser.version
            for name,check in cases:
                if chosen and name not in chosen: continue
                case={'name':name,'classification':'NOT_RUN','pageerrors':[]};report['cases'].append(case)
                context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',has_touch=name=='desktop-touch',reduced_motion='reduce')
                context.add_init_script('window.__onbShown=true;')
                install_bootstrap(context)
                page=context.new_page();page.set_default_timeout(10000)
                page.on('pageerror',lambda error,case=case:case['pageerrors'].append(str(error)))
                page.on('dialog',lambda dialog:dialog.accept())
                try:
                    page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
                    ready(page)
                    check(page,args.out,case)
                    assert not case['pageerrors'],case['pageerrors']
                    assert_fixture_requests(context)
                    case['classification']='PASS'
                except AssertionError as error:
                    case.update(classification='PRODUCT_FAIL',error=str(error),trace=traceback.format_exc())
                    page.screenshot(path=str(args.out/(name+'-failure.png')),full_page=True)
                except BaseException as error:
                    case.update(classification='TEST_HARNESS_FAIL',error=str(error),trace=traceback.format_exc())
                    page.screenshot(path=str(args.out/(name+'-failure.png')),full_page=True)
                finally: context.close()
            browser.close()
        assert before==hashes(args.root),'Sources changed during focal; rerun final frozen candidate'
        failures=[c for c in report['cases'] if c['classification']!='PASS']
        report['classification']=failures[0]['classification'] if failures else 'PASS'
    except BaseException as error:
        report.update(classification='ENVIRONMENT_ERROR',error=str(error),trace=traceback.format_exc())
    finally:
        server.shutdown()
        (args.out/'proportions-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['classification']=='PASS' else 1


if __name__=='__main__': raise SystemExit(main())

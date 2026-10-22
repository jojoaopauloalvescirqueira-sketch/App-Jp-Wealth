#!/usr/bin/env python3
"""Permanent browser oracles for the approved monthly inline contract.

Synthetic disposable contexts; actual Planning model, commands and writer.
The visual verifier imports these cases in its default entry.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
from hashlib import sha256
import json
from pathlib import Path
import threading

import planning_proportions_test as planning
import planning_compact_table_test as compact
from planning_parity_layout_test import financial

ROOT = Path(__file__).resolve().parents[1]
COUNTERPROOFS = ['inline-counterproof-row-height', 'inline-counterproof-duplicate-editor',
                 'inline-counterproof-false-green', 'inline-counterproof-typing-write',
                 'inline-counterproof-preference-finance-backup', 'inline-counterproof-wrong-usd',
                 'inline-counterproof-matrix-cell-value',
                 'inline-counterproof-action-target-size', 'inline-counterproof-action-inner-center']
REGRESSIONS = ['inline-ordinary-row-density', 'inline-cell-activation', 'inline-temporal-filters',
               'inline-result-real-writer', 'inline-future-explicit-save', 'inline-individual-flow-ids',
               'inline-dirty-context-guards', 'inline-stale-context-conflict',
               'inline-refused-unknown', 'inline-closed-reconfirmation',
               'inline-preferences-isolation', 'inline-preference-failure-incompatible',
               'inline-resize-focus-cursor', 'inline-reset-lifecycle',
               'inline-review-input-opening', 'inline-modal-escape-ownership',
               'inline-missing-record-fail-closed', 'inline-context-removed-before-save', 'inline-month-turnover',
               'inline-stoikus-context-guard', 'inline-future-context-companion',
               'inline-menu-escape-ownership', 'inline-empty-filter-recovery',
               'inline-editor-action-targets', 'inline-month-context-identity']


def required_ids(selection='all'):
    return list(REGRESSIONS) + (list(COUNTERPROOFS) if selection == 'all' else [])


def density(page, fixture):
    data = page.locator('[data-pl-grid-month]').evaluate_all('''rows=>rows.map(r=>({month:r.dataset.plGridMonth,height:r.getBoundingClientRect().height, controls:[...r.querySelectorAll('button,select')].map(n=>n.getBoundingClientRect().height)}))''')
    ordinary = [r for r in data if r['month'] in [fixture['start'], fixture['pending'], fixture['today'], fixture['negative']]]
    assert len(ordinary) == 4, ('four temporal fixtures', ordinary)
    assert all(0 < r['height'] <= 64 for r in ordinary), ('ordinary read rows must be <=64CSSpx', ordinary)
    assert all(all(h >= 44 for h in r['controls']) for r in ordinary), ('44px row targets', ordinary)
    assert page.locator('[data-pl-grid-month] input').count() == 0, 'reading table has no active fields'
    return ordinary


def activation(page, fixture):
    cell = page.locator('[data-pl-inline-open="result"][data-pl-inline-month="' + fixture['today'] + '"]')
    assert cell.count() == 1, 'one accessible result cell activates editor'
    cell.focus();page.keyboard.press('Enter')
    editor = page.locator('[data-pl-inline-editor]')
    assert editor.count() == 1 and editor.is_visible(), 'exactly one visible inline editor'
    assert editor.locator('[name=unit]').input_value() == 'PERCENT', 'default factual unit is percentage points'
    assert editor.locator('[name=value]').input_value() == '', 'unrecorded facts must start blank'
    editor.locator('[name=value]').fill('3')
    page.locator('#planning h1').click()
    assert editor.locator('[name=value]').input_value() == '3', 'outside click preserves draft'
    page.keyboard.press('Escape')
    assert page.locator('[data-pl-inline-editor]').count() == 0, 'Escape cancels editor'
    return {'empty_fact': True, 'outside_preserved': True, 'escape_cancelled': True}


def filters(page, fixture):
    year = page.locator('[data-pl-year]')
    assert year.input_value() == '', 'Year Todos is the initial selection'
    assert year.locator('option[value=""]').inner_text() == 'Todos', 'Year Todos is available'
    assert page.locator('[data-pl-highlight-past]').is_checked(), 'past highlight initially enabled'
    assert page.locator('[data-pl-period]').input_value() == 'all', 'initially all months'
    page.locator('[data-pl-period]').select_option('current')
    visible = page.locator('[data-pl-grid-month]:visible').evaluate_all('rs=>rs.map(r=>r.dataset.plGridMonth)')
    assert visible and all(m >= fixture['today'] for m in visible), ('current-onward filters by month', visible)
    year.select_option(fixture['start'][:4])
    visible = page.locator('[data-pl-grid-month]:visible').evaluate_all('rs=>rs.map(r=>r.dataset.plGridMonth)')
    assert all(m >= fixture['today'] and m[:4] == fixture['start'][:4] for m in visible), 'combined period and year filters'
    return {'visible': visible}

def open_editor(page, fixture, kind='result', month=None):
    target=page.locator('[data-pl-inline-open="'+kind+'"][data-pl-inline-month="'+(month or fixture['today'])+'"]')
    if not target.is_visible():compact.open_details(page,month or fixture['today'])
    target.click()
    editor=page.locator('[data-pl-inline-editor]')
    assert editor.count()==1 and editor.is_visible(), 'one active visible editor'
    return editor


def saved_cell_context(page,month,kind):
    target=page.locator('[data-pl-inline-open="'+kind+'"][data-pl-inline-month="'+month+'"]')
    assert target.count()==1 and target.is_visible(),'successful save reacquires its actual cell'
    data=target.evaluate("""n=>{const r=n.getBoundingClientRect(),p=n.closest('[data-pl-monthly-viewport]').getBoundingClientRect();return {active:document.activeElement===n,rect:r.toJSON(),pane:p.toJSON(),viewport:[innerWidth,innerHeight],hit:n.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))}}""")
    assert data['active'] and data['hit'],('successful save retains live cell keyboard focus and row context',month,kind,data)
    assert page.locator('[data-pl-inline-editor]').count()==0,'successful save focuses cell without silently reopening editor'
    return data


def result_writer(page, fixture, harness):
    before=financial(page);harness.start_write_probe(page)
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3')
    editor.locator('[data-pl-inline-save]').click()
    assert '31,95' in editor.locator('[data-pl-inline-review]').inner_text(), '3 points on 1065 opening previews31.95USD'
    harness.no_writes(page);assert financial(page)==before, 'review never writes facts'
    editor.locator('[data-pl-action=inline-confirm]').click()
    saved_context=saved_cell_context(page,fixture['today'],'result')
    data=page.evaluate('id=>({result:JPWPlanning.queries.account(id).plan.results,commands:__visualCommandCalls,writers:__visualWriterCalls,persisted:JSON.parse(localStorage.getItem("jpwealth_v9_state")).patrimonialPlanning})',fixture['id'])
    assert data['result'][fixture['today']]['usd']==31.95, ('confirmed rounded USD',data)
    assert data['commands']==['recordResult'] and len(data['writers'])==1, ('one real command and writer',data)
    assert data['persisted']['accounts'][0]['plan']['results'][fixture['today']]['usd']==31.95, 'confirmed value read back from actual storage'
    editor=open_editor(page,fixture);assert float(editor.locator('[name=value]').input_value())==3
    editor.locator('[name=unit]').select_option('USD');assert float(editor.locator('[name=value]').input_value())==31.95
    editor.locator('[name=unit]').select_option('PERCENT');assert float(editor.locator('[name=value]').input_value())==3
    editor.locator('[data-pl-action=inline-cancel]').click()
    return {'usd':31.95,'actual_writer_calls':len(data['writers']),'persisted':True}


def future_save(page,fixture,harness):
    month=fixture['blank'];before=financial(page);harness.start_write_probe(page)
    editor=open_editor(page,fixture,'rate',month);field=editor.locator('[name=rate]');assert field.input_value()==''
    field.fill('0');field.press('Tab');page.locator('#planning h1').click()
    harness.no_writes(page);assert financial(page)==before,'typing and blur never save'
    editor.locator('[data-pl-inline-save]').click();saved_cell_context(page,month,'rate')
    value=page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.future[m]',[fixture['id'],month]);assert value['rate']==0 and value['contributionUsd']=='',value
    editor=open_editor(page,fixture,'contributionUsd',month);editor.locator('[name=contributionUsd]').fill('0');editor.locator('[data-pl-inline-save]').click()
    editor=open_editor(page,fixture,'rate',month);editor.locator('[name=rate]').fill('');editor.locator('[data-pl-inline-save]').click()
    value=page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.future[m]',[fixture['id'],month]);assert value['rate'] is None and value['contributionUsd']==0,value
    editor=open_editor(page,fixture,'contributionUsd',month);editor.locator('[name=contributionUsd]').fill('');editor.locator('[data-pl-inline-save]').click()
    value=page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.future[m]',[fixture['id'],month]);assert value['rate'] is None and value['contributionUsd']=='',value
    far=page.evaluate('m=>JPWPlanning.engine.addMonths(m,100)',fixture['today']);editor=open_editor(page,fixture,'contributionUsd',far);editor.locator('[name=contributionUsd]').fill('17');editor.locator('[data-pl-inline-save]').click();far_context=saved_cell_context(page,far,'contributionUsd')
    far_value=page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.future[m]',[fixture['id'],far]);assert far_value['contributionUsd']==17 and far_value['rate']==.03,far_value
    page.keyboard.press('Enter');assert page.locator('[data-pl-inline-editor] [name=contributionUsd]').input_value()=='17','keyboard continues at the saved far-future cell';page.locator('[data-pl-action=inline-cancel]').click()
    calls=page.evaluate('({commands:__visualCommandCalls,writers:__visualWriterCalls})');assert calls['commands']==['setProjection']*5 and len(calls['writers'])==5,calls
    return {'companion_blank_zero_null_preserved':True,'real_writes':5,'far_future_focus':far_context}


def save_flow(page,fixture,kind,usd,brl=None):
    editor=open_editor(page,fixture,kind);editor.locator('[name=usd]').fill(usd)
    if brl is not None:editor.locator('[name=brl]').fill(brl)
    editor.locator('[data-pl-inline-save]').click();editor.locator('[data-pl-action=inline-confirm]').click()


def individual_flows(page,fixture,harness):
    harness.start_write_probe(page)
    editor=open_editor(page,fixture,'contribution');editor.locator('[name=usd]').fill('10');editor.locator('[data-pl-inline-save]').click()
    assert editor.locator('[data-pl-inline-review]').is_hidden(),'contribution BRL required'
    harness.no_writes(page);editor.locator('[data-pl-action=inline-cancel]').click()
    save_flow(page,fixture,'contribution','10','50');save_flow(page,fixture,'contribution','20','110')
    records=page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.contributions.filter(x=>x.month===m)',[fixture['id'],fixture['today']]);assert len(records)==2
    first,second=records
    editor=open_editor(page,fixture,'contribution');editor.locator('[data-pl-id="'+first['id']+'"]').click()
    editor=page.locator('[data-pl-inline-editor]');assert editor.locator('[name=usd]').input_value()=='10'
    editor.locator('[name=usd]').fill('12');editor.locator('[name=brl]').fill('60');editor.locator('[data-pl-inline-save]').click();editor.locator('[data-pl-action=inline-confirm]').click()
    records=page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.contributions.filter(x=>x.month===m)',[fixture['id'],fixture['today']]);assert len(records)==2 and records[0]['id']==first['id'] and records[0]['usd']==12 and records[1]==second,records
    assert records[0]['previous']['usd']==10,'correction preserves historical individual amount'
    save_flow(page,fixture,'withdrawal','1')
    withdrawal=page.evaluate('id=>JPWPlanning.queries.account(id).plan.withdrawals.at(-1)',fixture['id']);assert withdrawal['usd']==1 and 'brl' not in withdrawal,withdrawal
    return {'individual_ids_preserved':True,'history_preserved':True,'optional_withdrawal_brl':True}


def guards(page,fixture,harness):
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('2,5');before=financial(page);harness.start_write_probe(page)
    probes=[('[data-pl-year]',fixture['today'][:4]),('[data-pl-period]','current'),('[data-pl-month]',fixture['pending']),('[data-pl-account]',fixture['closed']),('[data-pl-finalized-month="'+fixture['today']+'"]','Sim')]
    for selector,value in probes:
        page.locator(selector).select_option(value)
        guard=page.locator('[data-pl-inline-guard]');assert guard.is_visible(),('context guard',selector)
        guard.locator('[data-pl-action=inline-continue]').click()
        assert editor.locator('[name=value]').input_value()=='2,5'
    for action in [lambda:page.locator('[data-pl-view=consolidated]').click(),lambda:page.evaluate("navigateToScreen('dashboard')"),lambda:page.evaluate("navigateToScreen('config')")]:
        action();guard=page.locator('[data-pl-inline-guard]');assert guard.is_visible(),'route/tab/settings guard';guard.locator('[data-pl-action=inline-continue]').click();assert editor.is_visible()
    page.locator('[data-pl-year]').select_option(fixture['today'][:4]);page.locator('[data-pl-inline-guard] [data-pl-action=inline-discard]').click()
    assert page.locator('[data-pl-inline-editor]').count()==0 and page.locator('[data-pl-year]').input_value()==fixture['today'][:4]
    harness.no_writes(page);assert financial(page)==before
    return {'guarded_contexts':8,'discard_explicit':True}


def conflict(page,fixture,harness):
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');editor.locator('[data-pl-inline-save]').click()
    page.evaluate('([id,m])=>{const a=JPWPlanning;const r=a.commands.execute("recordContribution",{accountId:id,month:m,usd:1,brl:5},a.queries.token(id));if(!r.ok)throw Error(JSON.stringify(r));}',[fixture['id'],fixture['today']])
    harness.start_write_probe(page);before=financial(page)
    editor.locator('[data-pl-action=inline-confirm]').click()
    assert 'mudaram' in editor.locator('[data-pl-inline-error]').inner_text(),'old token conflicts'
    assert editor.locator('[name=value]').input_value()=='3' and financial(page)==before
    editor.locator('[data-pl-inline-save]').click();editor.locator('[data-pl-action=inline-confirm]').click()
    assert 'mudaram' in editor.locator('[data-pl-inline-error]').inner_text(),'Save must not silently refresh stale token'
    assert financial(page)==before and page.evaluate('__visualWriterCalls.length')==0,'conflict refuses before writer'
    editor.locator('[data-pl-action=inline-cancel]').click();editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');editor.locator('[data-pl-inline-save]').click();editor.locator('[data-pl-action=inline-confirm]').click()
    assert page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.results[m].usd',[fixture['id'],fixture['today']])==31.95
    return {'stale_refused_twice':True,'explicit_reopen_required':True}


def refusal_unknown(page,fixture,harness):
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');editor.locator('[data-pl-inline-save]').click();before=financial(page)
    # Inject actual persistence-boundary refusals; command and controller remain real.
    page.evaluate('''()=>{window.__inlineOriginalWriter=jpWealthPersistDocument;jpWealthPersistDocument=function(){return {ok:false,status:'REFUSED',reason:'synthetic-refusal'};};}''')
    try:
        editor.locator('[data-pl-action=inline-confirm]').click();assert 'não foi confirmada' in editor.locator('[data-pl-inline-error]').inner_text();assert financial(page)==before
        editor.locator('[data-pl-action=inline-cancel]').click();editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');editor.locator('[data-pl-inline-save]').click()
        page.evaluate("jpWealthPersistDocument=function(){return {ok:false,status:'UNKNOWN',reason:'synthetic-unknown'};}")
        editor.locator('[data-pl-action=inline-confirm]').click();assert 'indeterminado' in editor.locator('[data-pl-inline-error]').inner_text();assert editor.locator('[data-pl-inline-save]').is_disabled() and editor.locator('[data-pl-action=inline-confirm]').is_disabled();assert financial(page)==before
    finally:page.evaluate('jpWealthPersistDocument=window.__inlineOriginalWriter')
    editor.locator('[data-pl-action=inline-cancel]').click()
    return {'refused_draft_retained':True,'unknown_retry_blocked':True,'financial_unchanged':True,'boundary_injection':True}


def closed_correction(page,fixture,harness):
    editor=open_editor(page,fixture,'result',fixture['start']);editor.locator('[name=value]').fill('0');editor.locator('[data-pl-inline-save]').click()
    assert editor.locator('[data-pl-inline-ack]').count()==1 and 'reconferência' in editor.locator('[data-pl-inline-review]').inner_text()
    before=financial(page);harness.start_write_probe(page);editor.locator('[data-pl-action=inline-confirm]').click();harness.no_writes(page);assert financial(page)==before
    editor.locator('[data-pl-inline-ack]').check();editor.locator('[data-pl-action=inline-confirm]').click()
    plan=page.evaluate('id=>JPWPlanning.queries.account(id).plan',fixture['id']);assert plan['results'][fixture['start']]['usd']==0 and plan['results'][fixture['start']]['previous']['usd']==-25
    assert not plan['closures'][fixture['start']]['confirmed'],'existing command reopens corrected closure'
    return {'ack_required':True,'previous_preserved':True,'existing_reopen':True}


def preferences(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page)
    past=page.locator('[data-pl-grid-month="'+fixture['pending']+'"]');current=page.locator('[data-pl-grid-month="'+fixture['today']+'"]')
    green=past.locator('th').evaluate('n=>getComputedStyle(n).backgroundColor');current_color=current.locator('th').evaluate('n=>getComputedStyle(n).backgroundColor')
    page.locator('[data-pl-highlight-past]').uncheck();assert past.locator('th').evaluate('n=>getComputedStyle(n).backgroundColor')!=green
    assert current.locator('th').evaluate('n=>getComputedStyle(n).backgroundColor')==current_color,'toggle leaves current style intact'
    page.locator('[data-pl-period]').select_option('current')
    stored=page.evaluate('JSON.parse(localStorage.getItem("jpwealth_planning_monthly_view_v1"))');assert stored=={'version':1,'highlightPast':False,'fromCurrent':True},stored
    assert page.evaluate('JP_WEALTH_AUX_STORAGE_KEYS.includes("jpwealth_planning_monthly_view_v1")'),'cleanup owns exact auxiliary key'
    backup_isolation(page)
    page.locator('[data-pl-view=consolidated]').click();page.locator('[data-pl-view=monthly]').click();assert not page.locator('[data-pl-highlight-past]').is_checked() and page.locator('[data-pl-period]').input_value()=='current'
    harness.no_writes(page);assert financial(page)==before
    return {'exact_envelope':stored,'outside_finance_backup':True,'reactivation_read':True}


def preference_failure(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page)
    raw='{"version":99,"preserved":"synthetic"}'
    page.evaluate('(raw)=>localStorage.setItem("jpwealth_planning_monthly_view_v1",raw)',raw)
    page.locator('[data-pl-view=consolidated]').click();page.locator('[data-pl-view=monthly]').click();page.locator('[data-pl-highlight-past]').uncheck()
    assert page.evaluate('localStorage.getItem("jpwealth_planning_monthly_view_v1")')==raw,'incompatible payload preserved'
    assert 'temporárias' in page.locator('[data-pl-prefs-notice]').inner_text()
    page.evaluate('''()=>{localStorage.removeItem('jpwealth_planning_monthly_view_v1');window.__inlineOriginalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='jpwealth_planning_monthly_view_v1')throw Error('synthetic quota');return window.__inlineOriginalSet.call(this,k,v)}}''')
    try:
        page.locator('[data-pl-view=consolidated]').click();page.locator('[data-pl-view=monthly]').click();page.locator('[data-pl-period]').select_option('current')
        assert 'temporárias' in page.locator('[data-pl-prefs-notice]').inner_text();assert page.locator('[data-pl-grid-month="'+fixture['start']+'"]').is_hidden()
    finally:page.evaluate('()=>{Storage.prototype.setItem=window.__inlineOriginalSet;}')
    harness.no_writes(page);assert financial(page)==before
    return {'incompatible_preserved':True,'quota_temporary_working':True}


def resize_focus(page,fixture,harness):
    editor=open_editor(page,fixture,'contributionUsd',fixture['negative']);field=editor.locator('[name=contributionUsd]');field.fill('12,');field.evaluate('n=>{window.__inlineNode=n;n.setSelectionRange(1,2)}')
    before=financial(page);harness.start_write_probe(page)
    for width in [390,1440,320,1440]:
        page.set_viewport_size({'width':width,'height':844});planning.settle(page)
        observed=page.evaluate('''()=>({same:document.activeElement===__inlineNode,connected:__inlineNode.isConnected,value:__inlineNode.value,selection:[__inlineNode.selectionStart,__inlineNode.selectionEnd],editors:document.querySelectorAll('[data-pl-inline-editor]').length})''')
        assert observed=={'same':True,'connected':True,'value':'12,','selection':[1,2],'editors':1},observed
    field.press('Escape');harness.no_writes(page);assert financial(page)==before
    return observed


def lifecycle(page,fixture,harness):
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');editor.locator('[data-pl-inline-save]').click();page.locator('[data-pl-period]').select_option('current');assert page.locator('[data-pl-inline-guard]').is_visible()
    before=financial(page);harness.start_write_probe(page);page.evaluate('JPWPlanning.ui.reset();JPWPlanning.ui.render(true)')
    assert page.locator('[data-pl-inline-editor]').count()==0 and page.locator('[data-pl-inline-guard]').count()==0 and not page.evaluate('JPWPlanning.ui.hasPendingWork()')
    page.set_viewport_size({'width':390,'height':844});page.evaluate("JPWPlanning.ui.selectView('monthly')");assert page.locator('[data-pl-inline-editor]').count()==0
    harness.no_writes(page);assert financial(page)==before
    return {'reset_invalidates_editor_review_guard':True}


def review_details(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page);observed=[]
    for width,height in [(1440,1000),(390,844),(1440,480)]:
        page.set_viewport_size({'width':width,'height':height});planning.settle(page)
        editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');editor.locator('[data-pl-inline-save]').click()
        review=editor.locator('[data-pl-inline-review]');text=review.inner_text()
        assert 'Saldo de abertura' in text and '1.065,00' in text,('review shows opening',text)
        assert 'Informado' in text and '3%' in text and '31,95' in text,('review shows entered representation and converted USD',text)
        heading=review.locator('h4');geometry=heading.evaluate("""n=>{const r=n.getBoundingClientRect(),p=n.closest('[data-pl-monthly-viewport]').getBoundingClientRect();return {active:document.activeElement===n,tabindex:n.tabIndex,rect:r.toJSON(),pane:p.toJSON(),viewport:[innerWidth,innerHeight],hit:n.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2))}}""")
        assert geometry['active'] and geometry['tabindex']==-1,('Save visibly focuses noninteractive review heading',geometry)
        r,pane=geometry['rect'],geometry['pane'];assert r['top']>=max(0,pane['top'])-.25 and r['bottom']<=min(height,pane['bottom'])+.25 and geometry['hit'],('review heading is visible inside pane and viewport',geometry)
        assert not editor.locator('[data-pl-action=inline-confirm]').evaluate('n=>n===document.activeElement'),'confirmation must remain deliberate'
        harness.no_writes(page);assert financial(page)==before
        observed.append({'viewport':[width,height],'review':text,'geometry':geometry});editor.locator('[data-pl-action=inline-cancel]').click()
    return observed


def modal_escape(page,fixture,harness):
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3')
    before=financial(page);harness.start_write_probe(page)
    page.evaluate("()=>{const d=document.createElement('dialog');d.dataset.inlineForeignModal='';d.innerHTML='<button>Fechar</button>';document.body.append(d);d.showModal();d.querySelector('button').focus();}")
    page.keyboard.press('Escape')
    assert page.locator('[data-inline-foreign-modal]').is_hidden(),'Escape closes owning native modal'
    assert editor.count()==1 and editor.locator('[name=value]').input_value()=='3','modal Escape preserves underlying editor'
    page.locator('[data-inline-foreign-modal]').evaluate('n=>n.remove()')
    page.locator('#headerNotesBtn').click();assert page.locator('#mvpNotesOverlay').is_visible(),'actual Notes drawer opens'
    page.keyboard.press('Escape');assert page.locator('#mvpNotesOverlay').is_hidden(),'actual Notes drawer handles Escape'
    assert editor.count()==1 and editor.locator('[name=value]').input_value()=='3' and page.evaluate('JPWPlanning.ui.hasPendingWork()'),'already-handled Notes Escape must preserve monthly draft'
    page.locator('[data-pl-period]').select_option('current');page.keyboard.press('Escape')
    assert page.locator('[data-pl-inline-guard]').count()==0 and editor.is_visible(),'guard Escape returns to editing'
    harness.no_writes(page);assert financial(page)==before
    return {'top_modal_owns_escape':True,'guard_cancel_retains':True}


def missing_record(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page)
    page.evaluate('m=>{const b=document.createElement("button");b.dataset.plAction="inline-record";b.dataset.plKind="contribution";b.dataset.plMonth=m;b.dataset.plId="missing-synthetic-id";b.dataset.inlineMissingProbe="";document.querySelector("#planning").append(b);b.click();}',fixture['today'])
    assert page.locator('[data-pl-inline-editor]').count()==0,'missing record ID refuses rather than silently opening new entry'
    assert 'não foi encontrado' in page.locator('[data-pl-notice]').inner_text(),'missing record visible refusal'
    page.locator('[data-inline-missing-probe]').evaluate('n=>n.remove()');harness.no_writes(page);assert financial(page)==before
    return {'unknown_id_refused':True}


def removed_context(page,fixture,harness):
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3')
    page.evaluate('id=>{const a=JPWPlanning,r=a.commands.execute("archiveAccount",{accountId:id,confirmation:true},a.queries.token(id));if(!r.ok)throw Error(JSON.stringify(r));}',fixture['id'])
    before=financial(page);harness.start_write_probe(page);editor.locator('[data-pl-inline-save]').click()
    assert editor.locator('[name=value]').input_value()=='3','removed account retains draft'
    assert editor.locator('[data-pl-inline-review]').is_hidden() and editor.locator('[data-pl-inline-error]').inner_text(),'removed context returns explicit failure'
    harness.no_writes(page);assert financial(page)==before
    return {'removed_account_refused_draft_retained':True}
def backup_isolation(page):
    backup=page.evaluate('''async()=>await dgBuildBackupBlob(1,'synthetic.json',new Date().toISOString()).text()''')
    assert 'jpwealth_planning_monthly_view_v1' not in backup,'preference excluded from actual serialized full backup'
    return {'actual_serialized_backup_checked':True}


def readonly_values(page,fixture):
    """Batch all 120 bound values; no activation, financial writes or UI formulas."""
    rows=compact.model(page,fixture)['monthlyRows']
    observed=page.evaluate(r'''rows=>{
      const errors=[],norm=x=>String(x).replace(/\s+/g,' ').trim(),money=(x,c='USD')=>Number.isFinite(x)?new Intl.NumberFormat('pt-BR',{style:'currency',currency:c}).format(x):'—',pct=x=>Number.isFinite(x)?(x*100).toLocaleString('pt-BR',{maximumFractionDigits:2})+'%':'—',fx=x=>Number.isFinite(x)?x.toLocaleString('pt-BR',{minimumFractionDigits:4,maximumFractionDigits:4}):'— · Indisponível';let checked=0;
      const compare=(month,key,node,wanted)=>{checked++;const actual=node?.textContent;if(!node||norm(actual)!==norm(wanted))errors.push({month,key,expected:wanted,actual:actual??null});};
      for(const r of rows){
        const principal=document.querySelector('[data-pl-grid-month="'+r.month+'"]'),details=document.querySelector('[data-pl-month-details="'+r.month+'"]');
        if(!principal||!details){errors.push({month:r.month,missing:true});continue;}
        const bound=key=>principal.querySelector('[data-pl-month-value="'+key+'"]')||details.querySelector('[data-pl-month-value="'+key+'"]');
        compare(r.month,'openUsd',bound('open'),money(r.openUsd));compare(r.month,'withdrawalUsd',bound('withdrawal'),money(r.withdrawalUsd));
        compare(r.month,'contributionUsd',bound('contribution'),r.contributionBlank&&principal.classList.contains('pl-month-future')?'—':money(r.contributionUsd));
        compare(r.month,'rate',bound('rate'),r.provisional?'—':pct(r.rate));
        const mode=principal.closest('[data-pl-monthly-layout]').dataset.plMonthlyLayout,result=principal.querySelector('[data-pl-inline-open=rate],[data-pl-inline-open=result]'),balance=principal.children[mode==='wide'?5:2];
        compare(r.month,'resultUsd',result?.querySelector('.pl-money-primary'),money(r.resultUsd));compare(r.month,'resultBrl',result?.querySelector('.pl-money-secondary'),money(r.resultBrl,'BRL'));
        compare(r.month,'closeUsd',balance?.querySelector('.pl-money-primary'),money(r.closeUsd));compare(r.month,'closeBrl',balance?.querySelector('.pl-money-secondary'),money(r.closeBrl,'BRL'));
        const final=principal.querySelector('[data-pl-finalized-month]')||details.querySelector('[data-pl-finalized-month]');checked++;if(final?.value!==(r.finalized?'Sim':'Não'))errors.push({month:r.month,key:'finalized',actual:final?.value,expected:r.finalized});
        const extra=label=>Array.from(details.querySelectorAll('.pl-month-extra-details dt')).find(n=>norm(n.textContent)===label)?.nextElementSibling;
        for(const [key,label,wanted] of [['paidBrl','Pago no mês',money(r.paidBrl,'BRL')],['fxRate','Câmbio utilizado · R$/US$',fx(r.fxRate)],['averageRate','Preço médio dos aportes · R$/US$',fx(r.averageRate)],['quoteRate','Última cotação disponível · R$/US$',fx(r.quoteRate)],['fxVariation','Variação cambial',pct(r.fxVariation)],['costCoverage','Cobertura',Number.isFinite(r.costCoverage)?pct(r.costCoverage):'— · Indisponível'],['costStatus','Situação do custo',r.costStatus||'Indisponível']])compare(r.month,key,extra(label),wanted);
      }
      return {months:rows.length,checked_fields:checked,errors};
    }''',rows)
    assert observed['months']==120 and observed['checked_fields']==120*16,('all months and fields checked',observed)
    assert not observed['errors'],('each displayed/bound field must match its own month read model',observed['errors'][:12])
    return observed


def read_oracles(page,fixture):
    data=page.locator('[data-pl-grid-month]').evaluate_all(r'''rs=>rs.map(r=>{const n=r.querySelector('th'),c=getComputedStyle(n).backgroundColor.match(/[\d.]+/g).map(Number);return {month:r.dataset.plGridMonth,height:r.getBoundingClientRect().height,visible:!!r.getClientRects().length,color:c,text:n.textContent,highlight:r.classList.contains('pl-highlight-past'),current:r.classList.contains('pl-month-current')}})''')
    assert len(data)==120 and len({r['month'] for r in data})==120,'every model month remains distinct'
    highlight=page.locator('[data-pl-highlight-past]').is_checked()
    today=page.evaluate("new Date().getFullYear()+'-'+String(new Date().getMonth()+1).padStart(2,'0')")
    for r in data:
        if r['visible'] and r['month']<today and highlight:
            assert r['color'][1]>r['color'][0] and r['color'][1]>r['color'][2],('past temporal green including pending',r)
        if r['month']==today:
            assert r['current'] and 'Em andamento' in r['text'],('current state distinct',r)
    width=page.locator('[data-pl-monthly-viewport]').evaluate('n=>n.clientWidth')
    ordinary=[r for r in data if r['month'] in [fixture['start'],fixture['pending'],fixture['today'],fixture['negative']] and r['visible']]
    if width>=900:assert all(r['height']<=64 for r in ordinary),('ordinary desktop rows<=64',width,ordinary)
    assert page.locator('[data-pl-grid-month] input').count()==0,'readonly row never has active financial input'
    return {'months':120,'ordinary_heights':[r['height'] for r in ordinary],'useful_width':width,'temporal_green':True,'bound_model_values':readonly_values(page,fixture)}


def month_turnover(page,fixture,harness):
    from datetime import datetime
    before=financial(page);harness.start_write_probe(page)
    next_month=page.evaluate('m=>JPWPlanning.engine.addMonths(m,1)',fixture['today'])
    page.clock.install(time=datetime.fromisoformat(next_month+'-15T12:00:00'))
    page.evaluate('JPWPlanning.ui.render(true)')
    old=page.locator('[data-pl-grid-month="'+fixture['today']+'"]');new=page.locator('[data-pl-grid-month="'+next_month+'"]')
    assert 'Pendente' in old.locator('th').inner_text() and old.evaluate('n=>n.classList.contains("pl-highlight-past")'),'elapsed current month becomes pending green'
    assert 'Em andamento' in new.locator('th').inner_text(),'new current month distinct'
    page.locator('[data-pl-period]').select_option('current');assert old.is_hidden() and new.is_visible()
    harness.no_writes(page);assert financial(page)==before
    return {'new_month':next_month,'calendar_only_no_closure_write':True}


def counterproofs(browser,url,report,harness):
    for case_id in COUNTERPROOFS:
        if report.get('only') and case_id not in report['only']:continue
        context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
        try:
            page=harness.setup(context,url)
            fixture=compact.seed(page);compact.select(page,fixture)
            def mutation(case_id=case_id):
                if case_id==COUNTERPROOFS[0]:
                    positive=density(page,fixture);style=page.add_style_tag(content='#planning [data-pl-grid-month]>td{padding-top:80px!important}')
                    try:rejected=harness.rejected(lambda:density(page,fixture))
                    finally:style.evaluate('n=>n.remove()')
                    return {'positive':positive,'rejected':rejected,'restored':density(page,fixture)}
                if case_id==COUNTERPROOFS[1]:
                    def unique():
                        assert page.locator('[data-pl-inline-editor]').count()==1,'one unique active editor'
                        assert page.locator('[data-pl-inline-editor] [name=value]').count()==1,'one unique active input'
                    editor=open_editor(page,fixture);unique();editor.evaluate('n=>{const copy=n.cloneNode(true);copy.dataset.inlineMutation="";n.after(copy)}')
                    try:rejected=harness.rejected(unique)
                    finally:page.locator('[data-inline-mutation]').evaluate('n=>n.remove()')
                    unique();return {'rejected':rejected}
                if case_id==COUNTERPROOFS[2]:
                    read_oracles(page,fixture);target=page.locator('[data-pl-grid-month="'+fixture['pending']+'"] th');target.evaluate('n=>n.style.backgroundColor="rgb(255, 255, 255)"')
                    try:rejected=harness.rejected(lambda:read_oracles(page,fixture))
                    finally:target.evaluate('n=>n.style.removeProperty("background-color")')
                    return {'rejected':rejected,'restored':read_oracles(page,fixture)}
                if case_id==COUNTERPROOFS[3]:
                    open_editor(page,fixture);harness.start_write_probe(page);before=financial(page)
                    page.evaluate('([id,m])=>{document.querySelector("[data-pl-inline-editor] [name=value]").addEventListener("input",()=>JPWPlanning.commands.execute("recordResult",{accountId:id,month:m,usd:1},JPWPlanning.queries.token(id)),{once:true})}',[fixture['id'],fixture['today']])
                    page.locator('[data-pl-inline-editor] [name=value]').fill('3')
                    rejected=harness.rejected(lambda:harness.no_writes(page));assert financial(page)!=before,'deliberate real writer mutation actually changes synthetic facts'
                    return {'rejected':rejected,'actual_write_mutation':True}
                if case_id==COUNTERPROOFS[4]:
                    before=financial(page);harness.start_write_probe(page)
                    page.evaluate('()=>{S.patrimonialPlanning.inlineMutationPreference={highlightPast:true,fromCurrent:false}}')
                    def finance_unchanged():assert financial(page)==before,'preference must stay outside financial S and backup'
                    rejected=harness.rejected(finance_unchanged)
                    page.evaluate('()=>{delete S.patrimonialPlanning.inlineMutationPreference;}')
                    backup_isolation(page)
                    page.evaluate('''()=>{window.__inlineBackupOriginal=dgBuildBackupBlob;dgBuildBackupBlob=function(...args){const blob=window.__inlineBackupOriginal.apply(this,args);return {text:async()=>{const payload=JSON.parse(await blob.text());payload.workspace.preferences['jpwealth_planning_monthly_view_v1']={version:1,highlightPast:true,fromCurrent:false};return JSON.stringify(payload)}}}}''')
                    try:backup_rejected=harness.rejected(lambda:backup_isolation(page))
                    finally:page.evaluate('()=>{dgBuildBackupBlob=window.__inlineBackupOriginal;}')
                    return {'rejected':rejected,'state_contamination_detected':True,'actual_backup_contamination_rejected':backup_rejected,'restored':backup_isolation(page)}
                if case_id in COUNTERPROOFS[7:]:
                    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');editor.locator('[data-pl-inline-save]').click();positive=action_geometry(page,harness)
                    target=editor.locator('[data-pl-inline-save]');original=target.get_attribute('style')
                    try:
                        if case_id==COUNTERPROOFS[7]:target.evaluate('n=>{n.style.setProperty("min-height","30px","important");n.style.setProperty("height","30px","important");n.style.setProperty("padding","0","important")}')
                        else:target.evaluate('n=>{const span=document.createElement("span");span.dataset.inlineInkMutation="";span.style.transform="translateX(8px)";span.textContent=n.textContent;n.replaceChildren(span)}')
                        rejected=harness.rejected(lambda:action_geometry(page,harness))
                    finally:
                        if case_id==COUNTERPROOFS[7]:target.evaluate('(n,s)=>s===null?n.removeAttribute("style"):n.setAttribute("style",s)',original)
                        else:target.evaluate('n=>n.textContent="Salvar"')
                    return {'positive':positive,'rejected':rejected,'restored':action_geometry(page,harness)}
                if case_id==COUNTERPROOFS[6]:
                    positive=readonly_values(page,fixture);target=page.locator('[data-pl-grid-month="'+fixture['today']+'"] .pl-inline-cell .pl-money-primary');original=target.inner_html()
                    try:
                        target.evaluate('n=>n.textContent="US$ 999.999,00"');rejected=harness.rejected(lambda:readonly_values(page,fixture))
                    finally:target.evaluate('(n,html)=>n.innerHTML=html',original)
                    return {'positive':positive,'rejected':rejected,'restored':readonly_values(page,fixture)}
                page.evaluate('''()=>{const original=JPWPlanning.queries.previewResultInput;JPWPlanning.queries.previewResultInput=function(...args){const r=original.apply(this,args);return r.ok?{...r,monthTotalUsd:r.monthTotalUsd*10}:r}}''')
                rejected=harness.rejected(lambda:result_writer(page,fixture,harness))
                return {'rejected':rejected,'query_conversion_mutation':True}
            harness.record(report,case_id,mutation,page,criteria='same permanent oracle must reject deliberately injected violation')
        finally:context.close()

def different_master(page,fixture):
    compact.select(page,fixture,'consolidated',fixture['closed']);compact.select(page,fixture,'monthly',fixture['id'])


def stoikus_monthly(page):
    page.locator('[data-pl-action=menu]').click();page.locator('#pl-stoikus-menu [data-pl-action=monthly]').click()


def stoikus_context(page,fixture,harness):
    different_master(page,fixture);editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');before=financial(page);harness.start_write_probe(page)
    stoikus_monthly(page)
    guard=page.locator('[data-pl-inline-guard]');assert guard.is_visible(),'Stoikus changing to another master account must resolve the active draft'
    guard.locator('[data-pl-action=inline-continue]').click();assert editor.locator('[name=value]').input_value()=='3'
    editor.locator('[data-pl-action=inline-cancel]').click();page.evaluate('JPWPlanning.ui.render(true)')
    assert page.locator('[data-pl-account]').input_value()==fixture['id'],'blocked navigation cannot mutate hidden account selection'
    harness.no_writes(page);assert financial(page)==before
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('2');stoikus_monthly(page);page.locator('[data-pl-inline-guard] [data-pl-action=inline-discard]').click()
    assert page.locator('[data-pl-account]').input_value()==fixture['closed'] and page.locator('[data-pl-inline-editor]').count()==0,'explicit discard resumes entire intended master navigation'
    return {'continue_preserves_account':True,'discard_resumes_entire_navigation':True}


def future_context(page,fixture,harness):
    different_master(page,fixture);month=fixture['blank'];original=page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.future[m]',[fixture['id'],month]);assert original=={'rate':None,'contributionUsd':''},original
    editor=open_editor(page,fixture,'contributionUsd',month);editor.locator('[name=contributionUsd]').fill('17');harness.start_write_probe(page);before=financial(page)
    stoikus_monthly(page);guard=page.locator('[data-pl-inline-guard]');guarded=guard.count()==1
    if guarded:guard.locator('[data-pl-action=inline-continue]').click()
    harness.no_writes(page);assert financial(page)==before
    editor.locator('[data-pl-inline-save]').click()
    actual=page.evaluate('([id,m])=>JPWPlanning.queries.account(id).plan.future[m]',[fixture['id'],month])
    assert actual=={'rate':None,'contributionUsd':17},('editing only B contribution must preserve B null rate despite different master A',original,actual)
    calls=page.evaluate('({commands:__visualCommandCalls,writers:__visualWriterCalls})');assert calls['commands']==['setProjection'] and len(calls['writers'])==1,calls
    return {'before':original,'after':actual,'guarded':guarded,'actual_writer_count':len(calls['writers'])}


def menu_escape(page,fixture,harness):
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('3');before=financial(page);harness.start_write_probe(page)
    page.locator('[data-pl-action=menu]').click();page.keyboard.press('Escape')
    assert page.locator('#pl-stoikus-menu').is_hidden(),'Escape closes menu'
    assert editor.count()==1 and editor.locator('[name=value]').input_value()=='3' and page.evaluate('JPWPlanning.ui.hasPendingWork()'),'menu owns Escape and preserves underlying draft'
    editor.locator('[name=value]').focus();page.keyboard.press('Escape');assert page.locator('[data-pl-inline-editor]').count()==0,'editor still supports explicit Escape after menu closes'
    harness.no_writes(page);assert financial(page)==before
    return {'menu_escape_retains_draft':True,'editor_escape_still_cancels':True}


def empty_filter(page,fixture,harness):
    id=page.evaluate('today=>{const api=JPWPlanning,r=api.commands.execute("createAccount",{name:"Filtro vazio sintético",startMonth:api.engine.addMonths(today,-24),initialUsd:1000,monthlyContributionUsd:0,profileId:"base",goals:{adequate:{value:150,currency:"USD"},ideal:{value:300,currency:"USD"}}},api.queries.token());if(!r.ok)throw Error(JSON.stringify(r));return r.accountId;}',fixture['today'])
    compact.select(page,fixture,account=id);before=financial(page);harness.start_write_probe(page)
    past_year=str(int(fixture['today'][:4])-1);page.locator('[data-pl-period]').select_option('current');page.locator('[data-pl-year]').select_option(past_year)
    assert page.locator('[data-pl-grid-month]:visible').count()==0 and page.locator('[data-pl-filter-empty]').is_visible(),'combined empty filter explains recovery'
    assert page.locator('.pl-phase-heading:visible,[data-pl-phase-total]:visible').count()==0,'empty groups hidden'
    page.locator('[data-pl-action=show-all-months]').click();assert page.locator('[data-pl-grid-month]:visible').count()==120 and page.locator('[data-pl-year]').input_value()=='' and page.locator('[data-pl-period]').input_value()=='all'
    assert page.locator('[data-pl-phase-total]').count()==10 and all('ciclo completo' in text for text in page.locator('[data-pl-phase-total]').all_text_contents()),'subtotals clearly remain full plan cycles'
    harness.no_writes(page);assert financial(page)==before
    return {'empty_recovery':True,'full_cycle_subtotals':True}

def action_geometry(page,harness):
    actions=page.locator('[data-pl-inline-editor] button:visible');assert actions.count()>=2,'nonempty actual inline actions'
    result=[]
    for index in range(actions.count()):
        target=actions.nth(index);box=target.bounding_box();assert box and box['width']>=44 and box['height']>=44,('inline action target must be44x44CSSpx',target.inner_text(),box)
        result.append(harness.centered(target))
    return result


def highlight_geometry(page,harness):
    label=page.locator('.pl-month-controls>.pl-check');data=label.evaluate(harness.CONTENT_GEOMETRY);field=label.locator('input').bounding_box();outer=data['outer'];text=data['text']
    assert label.evaluate('n=>getComputedStyle(n).flexDirection')=='row','past-highlight checkbox and caption share one row'
    assert outer['height']>=44 and outer['width']>=44,'implicit checkbox label retains44px target'
    assert abs((text['top']+text['bottom']-outer['top']-outer['bottom'])/2)<=2,('checkbox caption vertically centered',data)
    assert abs(field['y']+field['height']/2-(outer['top']+outer['bottom'])/2)<=2,('checkbox ink vertically aligned',field,outer)
    period=page.locator('[data-pl-period]').bounding_box();delta=(outer['top']+outer['bottom'])/2-(period['y']+period['height']/2)
    if page.viewport_size['width']>=900:assert abs(delta)<=2,('checkbox and period select centers align within2CSSpx',delta,outer,period)
    data['period_center_delta']=delta
    return data


def action_targets(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page);observed=[]
    for width in [1440,390]:
        page.set_viewport_size({'width':width,'height':1000 if width==1440 else 844});planning.settle(page)
        for kind,month in [('result',fixture['today']),('rate',fixture['blank']),('contribution',fixture['start']),('withdrawal',fixture['start'])]:
            editor=open_editor(page,fixture,kind,month)
            if kind=='result':editor.locator('[name=value]').fill('3')
            elif kind in ['contribution','withdrawal']:
                editor.locator('[name=usd]').fill('1');editor.locator('[name=brl]').fill('5')
                assert editor.locator('.pl-inline-records [data-pl-action=inline-record]').count()>=1,'individual edit actions included'
            if kind!='rate':editor.locator('[data-pl-inline-save]').click();assert editor.locator('[data-pl-action=inline-confirm]').is_visible(),'confirmation target included'
            observed.append({'viewport':width,'kind':kind,'actions':action_geometry(page,harness),'highlight':highlight_geometry(page,harness)})
            editor.locator('[data-pl-action=inline-cancel]').click()
    harness.no_writes(page);assert financial(page)==before
    return observed


def month_identity_oracle(page,expected):
    selector=page.locator('[data-pl-month]');assert selector.input_value()==expected,('visible month must match active month',expected,selector.input_value())
    selected=page.locator('[data-pl-grid-month].pl-row-selected');assert selected.count()==1 and selected.get_attribute('data-pl-grid-month')==expected,'selected row matches visible month'
    label=selector.locator('option:checked').inner_text().split(' · ')[0]
    context=page.locator('[data-pl-month-context]');assert context.locator('[data-pl-action=finalize]').count()==1,'upper action context corresponds to the pending selected month'
    context.locator('[data-pl-action=finalize]').click();dialog=page.locator('dialog[open]');key=dialog.get_attribute('data-pl-draft-key');text=dialog.inner_text()
    try:
        assert key.split(':')[2]==expected and label in text,('upper action uses same month as visible selector and row',expected,key,text)
    finally:dialog.locator('footer [data-pl-action=close]').click()
    return {'selected_month':expected,'upper_action_key':key,'visible_label':label}


def flow_opener_focus_oracle(page,kind):
    assert page.locator('[data-pl-month-context] [data-pl-action='+kind+']').evaluate('n=>document.activeElement===n'),'cancelled legacy flow restores its live semantic opener focus'
    return {'action':kind,'focused_live_opener':True}


def flow_month_context_paths(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page);observed=[]
    for kind in ['result','contribution','withdrawal']:
        for cancel in ['Cancel','Escape']:
            page.locator('[data-pl-month]').select_option(fixture['today'])
            page.locator('[data-pl-month-context] [data-pl-action='+kind+']').click()
            dialog=page.locator('dialog[open]');month=fixture['pending']
            dialog.locator('[name=flowMonth]').fill(month[5:]+'/'+month[:4]);dialog.locator('[data-pl-submit]').click()
            assert dialog.locator('[data-pl-flow-step=usd]').is_visible(),'actual month step accepted'
            assert page.locator('[data-pl-month]').input_value()==month,'flow month step synchronizes visible month before cancellation'
            harness.no_writes(page);assert financial(page)==before
            if cancel=='Escape':page.keyboard.press('Escape')
            else:dialog.locator('footer [data-pl-action=close]').click()
            assert page.locator('dialog[open]').count()==0
            focus=flow_opener_focus_oracle(page,kind)
            if kind=='result' and cancel=='Cancel':
                page.evaluate('document.activeElement.blur()')
                focus['body_focus_counterproof']=harness.rejected(lambda:flow_opener_focus_oracle(page,kind))
                page.locator('[data-pl-month-context] [data-pl-action='+kind+']').focus();flow_opener_focus_oracle(page,kind)
            observed.append({'flow':kind,'cancel':cancel,'focus':focus,'context':month_identity_oracle(page,month)})
            harness.no_writes(page);assert financial(page)==before
    page.locator('[data-pl-month]').select_option(fixture['today'])
    return observed


def finalized_value_oracle(page,fixture,month):
    fact=page.evaluate('([id,m,today])=>JPWPlanning.queries.view({accountId:id,month:today}).rows.find(r=>r.month===m).finalized',[fixture['id'],month,fixture['today']])
    value=page.locator('[data-pl-finalized-month="'+month+'"]').input_value()
    assert value==('Sim' if fact else 'Não'),('visible Finalizado must equal actual model fact',month,fact,value)
    return {'month':month,'model_finalized':fact,'visible':value}


def finalized_selector_paths(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page);observed=[]
    def check_context(month,actual):
        assert page.locator('[data-pl-month]').input_value()==month,'Finalizado selection synchronizes visible month'
        selected=page.locator('[data-pl-grid-month].pl-row-selected')
        assert selected.count()==1 and selected.get_attribute('data-pl-grid-month')==month,'Finalizado selection synchronizes selected row'
        value=page.locator('[data-pl-finalized-month="'+month+'"]').input_value()
        assert value==actual,('Finalizado control displays only confirmed state while confirmation is pending',month,actual,value)
        finalized_value_oracle(page,fixture,month)
        action='reopen' if actual=='Sim' else 'finalize'
        page.locator('[data-pl-month-context] [data-pl-action='+action+']').click()
        dialog=page.locator('dialog[open]');assert dialog.get_attribute('data-pl-draft-key').split(':')[2]==month,'upper action retains same month'
        dialog.locator('footer [data-pl-action=close]').click()
    for month,requested,actual in [(fixture['pending'],'Sim','Não'),(fixture['start'],'Não','Sim')]:
        for cancel in ['Cancel','Escape']:
            page.locator('[data-pl-month]').select_option(fixture['today'])
            page.locator('[data-pl-finalized-month="'+month+'"]').select_option(requested)
            dialog=page.locator('dialog[open]');assert dialog.get_attribute('data-pl-draft-key').split(':')[2]==month,'requested target captured before resetting native value'
            assert page.locator('[data-pl-finalized-month="'+month+'"]').input_value()==actual,'pending confirmation never displays an unconfirmed finalized state'
            harness.no_writes(page);assert financial(page)==before
            if cancel=='Escape':page.keyboard.press('Escape')
            else:dialog.locator('footer [data-pl-action=close]').click()
            assert page.locator('dialog[open]').count()==0
            check_context(month,actual);harness.no_writes(page);assert financial(page)==before
            observed.append({'month':month,'cancel':cancel,'confirmed_display':actual})
    false_control=page.locator('[data-pl-finalized-month="'+fixture['pending']+'"]')
    false_control.evaluate("n=>n.value='Sim'")
    try:counterproof=harness.rejected(lambda:finalized_value_oracle(page,fixture,fixture['pending']))
    finally:false_control.evaluate("n=>n.value='Não'")
    finalized_value_oracle(page,fixture,fixture['pending']);harness.no_writes(page);assert financial(page)==before
    observed.append({'false_finalized_display_counterproof':counterproof})
    page.locator('[data-pl-month]').select_option(fixture['today'])
    editor=open_editor(page,fixture);editor.locator('[name=value]').fill('7')
    target=page.locator('[data-pl-finalized-month="'+fixture['pending']+'"]');target.select_option('Sim')
    guard=page.locator('[data-pl-inline-guard]');assert guard.is_visible() and target.input_value()=='Não'
    guard.locator('[data-pl-action=inline-continue]').click()
    assert editor.locator('[name=value]').input_value()=='7' and page.locator('[data-pl-month]').input_value()==fixture['today']
    harness.no_writes(page);assert financial(page)==before
    target.select_option('Sim');page.locator('[data-pl-inline-guard] [data-pl-action=inline-discard]').click()
    dialog=page.locator('dialog[open]');assert dialog.get_attribute('data-pl-draft-key').split(':')[2]==fixture['pending']
    assert target.input_value()=='Não' and page.locator('[data-pl-month]').input_value()==fixture['pending']
    dialog.locator('footer [data-pl-action=close]').click();check_context(fixture['pending'],'Não');harness.no_writes(page);assert financial(page)==before
    for requested,actual,command in [('Sim','Não','finalizeMonth'),('Não','Sim','reopenMonth')]:
        before=financial(page);harness.start_write_probe(page)
        page.locator('[data-pl-month]').select_option(fixture['today'])
        page.locator('[data-pl-finalized-month="'+fixture['pending']+'"]').select_option(requested)
        dialog=page.locator('dialog[open]');assert page.locator('[data-pl-finalized-month="'+fixture['pending']+'"]').input_value()==actual
        harness.no_writes(page);assert financial(page)==before
        if requested=='Sim':dialog.locator('[name=confirmFlows]').check()
        else:dialog.locator('[name=reason]').fill('Reconferência sintética do seletor')
        dialog.locator('[data-pl-submit]').click();assert page.locator('dialog[open]').count()==0
        calls=page.evaluate('({commands:__visualCommandCalls,writers:__visualWriterCalls})')
        assert calls['commands']==[command] and len(calls['writers'])==1,('one actual confirmation and writer',calls)
        assert financial(page)!=before,'confirmed closure state really changes'
        check_context(fixture['pending'],requested)
        observed.append({'confirm':command,'actual_writer_count':len(calls['writers'])})
    page.locator('[data-pl-month]').select_option(fixture['today'])
    return observed


def month_context_identity(page,fixture,harness):
    flow_paths=flow_month_context_paths(page,fixture,harness)
    finalized_paths=finalized_selector_paths(page,fixture,harness)
    before=financial(page);harness.start_write_probe(page);observed=[]
    assert page.locator('[data-pl-month]').input_value()==fixture['today']
    editor=open_editor(page,fixture,'result',fixture['pending']);editor.locator('[data-pl-action=inline-cancel]').click()
    observed.append(month_identity_oracle(page,fixture['pending']));harness.no_writes(page);assert financial(page)==before
    page.locator('[data-pl-month]').select_option(fixture['today'])
    editor=open_editor(page,fixture,'result',fixture['pending']);editor.locator('[name=value]').focus();page.keyboard.press('Escape')
    assert page.locator('[data-pl-inline-editor]').count()==0,'Escape cancels without changing the synchronized month'
    observed.append(month_identity_oracle(page,fixture['pending']));harness.no_writes(page);assert financial(page)==before
    # Deliberately recreate the discovered visible/private month disagreement.
    selector=page.locator('[data-pl-month]');selector.evaluate('(n,m)=>n.value=m',fixture['today'])
    try:counterproof=harness.rejected(lambda:month_identity_oracle(page,fixture['pending']))
    finally:selector.evaluate('(n,m)=>n.value=m',fixture['pending'])
    observed.append(month_identity_oracle(page,fixture['pending']));harness.no_writes(page);assert financial(page)==before
    page.locator('[data-pl-month]').select_option(fixture['today'])
    editor=open_editor(page,fixture,'result',fixture['pending']);editor.locator('[name=value]').fill('0');editor.locator('[data-pl-inline-save]').click();harness.no_writes(page);assert financial(page)==before
    editor.locator('[data-pl-action=inline-confirm]').click();saved_cell_context(page,fixture['pending'],'result')
    observed.append(month_identity_oracle(page,fixture['pending']))
    calls=page.evaluate('({commands:__visualCommandCalls,writers:__visualWriterCalls})');assert calls['commands']==['recordResult'] and len(calls['writers'])==1,calls
    return {'observed':observed,'visible_mismatch_counterproof':counterproof,'real_writer_count':len(calls['writers']),'finalized_selector_paths':finalized_paths,'flow_month_context_paths':flow_paths}


def regressions(browser,url,report,harness):
    actions=[density,activation,filters,result_writer,future_save,individual_flows,guards,conflict,refusal_unknown,closed_correction,preferences,preference_failure,resize_focus,lifecycle,review_details,modal_escape,missing_record,removed_context,month_turnover,stoikus_context,future_context,menu_escape,empty_filter,action_targets,month_context_identity]
    read_only={density,activation,filters}
    for case_id,action in zip(REGRESSIONS,actions):
        if report.get('only') and case_id not in report['only']:continue
        context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',reduced_motion='reduce')
        try:
            page=harness.setup(context,url)
            if action==modal_escape:page.evaluate('()=>{S.mvpNotes.showHeaderIcon=true;if(save()!==true)throw Error("synthetic Notes setup refused");renderMvpNotesHeader();}')
            fixture=compact.seed(page);compact.select(page,fixture)
            run=(lambda:compact.guard(page,harness,lambda:action(page,fixture))) if action in read_only else lambda:action(page,fixture,harness)
            harness.record(report,case_id,run,page)
        finally:context.close()


def main():
    import ui_visual_quality_test as harness
    from browser_fixture_server import BrowserFixtureServer
    from playwright.sync_api import sync_playwright
    from notes_launcher_test import launch_options
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', nargs='+', choices=REGRESSIONS+COUNTERPROOFS)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args();args.out.mkdir(parents=True, exist_ok=False)
    files = ['src/js/30-accounting/06-planning/03-ui.js', 'src/js/30-accounting/06-planning/02-state.js', 'src/styles/app.css', 'tools/planning_monthly_inline_test.py']
    hashes = lambda: {f: sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
    report = {'out': str(args.out), 'started_at': datetime.now(timezone.utc).isoformat(), 'source_sha256': hashes(), 'cases': [], 'required_case_ids': args.only or required_ids(), 'only':args.only}
    server = BrowserFixtureServer(('127.0.0.1', 0), partial(planning.Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options());report['browser']=browser.version
            regressions(browser, f'http://127.0.0.1:{server.server_port}/index.html', report, harness)
            counterproofs(browser, f'http://127.0.0.1:{server.server_port}/index.html', report, harness)
            browser.close()
        report['coverage']=harness.validate_coverage(report['cases'], report['required_case_ids'])
        failures=[c for c in report['cases'] if c['classification']!='PASS'];report['classification']=failures[0]['classification'] if failures else 'PASS'
    finally:
        server.shutdown();report['source_unchanged']=hashes()==report['source_sha256'];report['finished_at']=datetime.now(timezone.utc).isoformat()
        (args.out/'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(report['classification']+' cases='+str(len(report['cases'])))
    return 0 if report['classification']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())

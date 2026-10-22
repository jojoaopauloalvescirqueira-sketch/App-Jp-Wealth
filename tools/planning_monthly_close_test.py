#!/usr/bin/env python3
"""Approved22/10 closure recovery, real UI/commands with synthetic storage.

Imported by the existing default visual entry; standalone selection preserves RED.
"""
import argparse
from datetime import datetime, timezone
from functools import partial
from hashlib import sha256
import json
import math
from pathlib import Path
import shutil
import tempfile
import threading

import planning_proportions_test as planning
import planning_compact_table_test as compact
import planning_monthly_inline_test as inline
from planning_parity_layout_test import financial

ROOT = Path(__file__).resolve().parents[1]
REGRESSIONS = ['closure-missing-result-recovery', 'closure-cancelled-review-conflict',
               'closure-result-save-cancel', 'closure-previous-pending-navigation',
               'closure-result-units-validation', 'closure-review-changed-data',
               'closure-writer-refusal-unknown', 'closure-shared-flow-draft-refresh',
               'closure-zero-opening-usd', 'closure-draft-backup-retention',
               'closure-invalidated-context-no-refresh']
COUNTERPROOFS = ['closure-counterproof-missing-recovery', 'closure-counterproof-positive-loss',
                 'closure-counterproof-restored-consent']


def required_ids(selection='all'):
    ids=list(REGRESSIONS)
    if selection=='all':
        ids+=list(COUNTERPROOFS)
        ids += [f'closure-matrix-{layout}-{theme}-{width}' for layout in planning.LAYOUTS for theme in planning.THEMES for width in [390,1440]]
        ids += [f'closure-native200-{layout}-{theme}' for layout in planning.LAYOUTS for theme in planning.THEMES]
    return ids


def result_preview_oracle(page, dialog, expected):
    formatted=page.evaluate("v=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'USD'}).format(v)",expected)
    text=dialog.locator('[data-pl-closure-result-review]').inner_text()
    assert formatted in text, ('signed rounded actual USD must be represented exactly',formatted,text)
    return {'expected_usd':expected,'formatted':formatted}


def fresh_consent_oracle(dialog):
    assert not dialog.locator('[name=confirmFlows]').is_checked(), 'fresh closure requires new explicit flow consent'
    return {'unchecked':True}


def seed(page, initial=1000):
    return page.evaluate('''initial=>{
      const a=JPWPlanning,d=new Date(),today=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0'),start=a.engine.addMonths(today,-6);
      const r=a.commands.execute('createAccount',{name:'Fechamento sintético',startMonth:start,initialUsd:initial,monthlyContributionUsd:100,profileId:'base',goals:{ideal:{value:300,currency:'USD'}}},a.queries.token());
      if(!r.ok)throw Error(JSON.stringify(r));a.ui.render(true);return{id:r.accountId,start,today};
    }''', initial)


def command(page, fixture, name, **fields):
    return page.evaluate('''x=>{const a=JPWPlanning,r=a.commands.execute(x.name,{accountId:x.id,...x.fields},a.queries.token(x.id));if(!r.ok)throw Error(JSON.stringify(r));return r}''', {'id':fixture['id'],'name':name,'fields':fields})


def open_close(page, fixture, month=None):
    month=month or fixture['start']
    page.locator('#planning [data-pl-month]').select_option(month)
    page.get_by_role('button',name='Finalizado = Sim',exact=True).click()
    return page.locator('#planning dialog.pl-dialog')


def result_section(dialog):
    section=dialog.locator('[data-pl-closure-result]')
    assert section.count()==1 and section.is_visible(), 'blocked closure must offer result entry in the same dialog'
    assert section.locator('[name=closureResultValue]').input_value()=='', 'missing result must start blank; never assume zero or projection'
    return section


def record_result(dialog, value='0', unit='USD'):
    section=dialog.locator('[data-pl-closure-result]')
    section.locator('[name=closureResultUnit]').select_option(unit)
    section.locator('[name=closureResultValue]').fill(value)
    section.locator('[data-pl-action=closure-preview-result]').click()
    assert dialog.locator('[data-pl-closure-result-review]').is_visible(), 'explicit result preview visible before any save'
    section.locator('[data-pl-action=closure-save-result]').click()


def closure_state(page, fixture, month=None):
    return page.evaluate('''x=>{const p=JPWPlanning.queries.account(x.id).plan;return{result:p.results[x.month]||null,closure:p.closures[x.month]||null,stored:JSON.parse(localStorage.getItem('jpwealth_v9_state')).patrimonialPlanning}}''', {'id':fixture['id'],'month':month or fixture['start']})


def missing_recovery(page, fixture, harness):
    before=financial(page);harness.start_write_probe(page)
    dialog=open_close(page,fixture);section=result_section(dialog)
    label=page.evaluate("m=>new Date(m+'-15T12:00:00').toLocaleDateString('pt-BR',{month:'short',year:'numeric'})",fixture['start'])
    context=dialog.locator('[data-pl-closure-context]').inner_text()
    assert label in context and 'Fechamento sintético' in context, ('exact account/month context is visible',context)
    section.locator('[name=closureResultValue]').fill('0')
    section.locator('[data-pl-action=closure-preview-result]').click()
    harness.no_writes(page);assert financial(page)==before, 'opening, typing and reviewing never write'
    section.locator('[data-pl-action=closure-save-result]').click()
    assert page.locator('#planning dialog.pl-dialog').is_visible(), 'result save stays in closure workflow'
    consent=dialog.locator('[name=confirmFlows]');fresh_consent_oracle(dialog)
    state=closure_state(page,fixture);assert state['result']['usd']==0 and not state['closure'], 'result and closure are distinct confirmed operations'
    assert len(page.evaluate('__visualWriterCalls'))==1
    consent.check();dialog.locator('[data-pl-submit]').click()
    dialog.wait_for(state='hidden')
    state=closure_state(page,fixture);assert state['closure']['confirmed'] is True
    assert 'continua aberto' not in page.locator('[data-pl-notice]').inner_text().lower(), 'successful closure must not retain the saved-result cancellation notice'
    assert page.evaluate('document.activeElement!==document.body'), 'confirmed closure returns focus to a live control'
    assert page.evaluate('__visualCommandCalls')==['recordResult','finalizeMonth']
    assert len(page.evaluate('__visualWriterCalls'))==2, 'one writer per explicit confirmed operation'
    assert state['closure']['snapshot']['closeUsd']==1000, 'planned contribution is never silently recorded'
    return {'confirmed':True,'commands':['recordResult','finalizeMonth'],'effective_usd':1000}


def cancelled_conflict(page, fixture, harness):
    dialog=open_close(page,fixture)
    consent=dialog.locator('[name=confirmFlows]')
    if consent.count() and consent.is_visible():consent.check()
    else:dialog.locator('[name=closureResultValue]').fill('12')
    dialog.get_by_role('button',name='Cancelar',exact=True).click()
    editor=inline.open_editor(page,fixture,month=fixture['start']);editor.locator('[name=unit]').select_option('USD');editor.locator('[name=value]').fill('0');editor.locator('[data-pl-inline-save]').click();editor.locator('[data-pl-action=inline-confirm]').click()
    harness.start_write_probe(page);before=financial(page)
    dialog=open_close(page,fixture)
    refresh=dialog.locator('[data-pl-action=draft-refresh]')
    assert refresh.count()==1 and refresh.is_visible(), 'old reviewed context must have explicit refresh recovery'
    assert dialog.locator('[data-pl-submit]').is_disabled(), 'stale approval cannot authorize a changed context'
    harness.no_writes(page);assert financial(page)==before
    refresh.click()
    assert not dialog.locator('[name=confirmFlows]').is_checked(), 'refresh clears old flow approval'
    dialog.locator('[name=confirmFlows]').check();dialog.locator('[data-pl-submit]').click();dialog.wait_for(state='hidden')
    assert closure_state(page,fixture)['closure']['confirmed'] is True
    assert page.evaluate('__visualCommandCalls')==['finalizeMonth'] and len(page.evaluate('__visualWriterCalls'))==1
    return {'stale_recovered_explicitly':True,'one_close_write':True}


def save_cancel(page, fixture, harness):
    harness.start_write_probe(page);dialog=open_close(page,fixture);result_section(dialog);record_result(dialog,'-25')
    assert closure_state(page,fixture)['result']['usd']==-25
    dialog.get_by_role('button',name='Cancelar',exact=True).click()
    state=closure_state(page,fixture);assert state['result']['usd']==-25 and not state['closure']
    text=page.locator('[data-pl-notice]').inner_text().lower()
    assert 'resultado' in text and 'registrado' in text and 'aberto' in text, ('cancellation must not imply rollback of saved result',text)
    assert page.evaluate('__visualCommandCalls')==['recordResult'] and len(page.evaluate('__visualWriterCalls'))==1
    return {'saved_result':-25,'month_open':True,'notice':text}


def previous_navigation(page, fixture, harness):
    # Both preceding months open; the first pending month must be identified.
    target=page.evaluate('m=>JPWPlanning.engine.addMonths(m,2)',fixture['start'])
    command(page,fixture,'recordResult',month=target,usd=0)
    page.evaluate('JPWPlanning.ui.render(true)');harness.start_write_probe(page);before=financial(page)
    dialog=open_close(page,fixture,target)
    jump=dialog.locator('[data-pl-action=closure-previous]')
    assert jump.count()==1 and jump.is_visible(), 'blocked sequence offers actionable previous month'
    assert jump.get_attribute('data-pl-previous-month')==fixture['start'], 'earliest pending month, not merely previous month'
    jump.click();dialog.wait_for(state='hidden')
    assert page.locator('[data-pl-month]').input_value()==fixture['start']
    harness.no_writes(page);assert financial(page)==before
    return {'target':target,'first_pending':fixture['start'],'no_writes':True}


def units_validation(page, fixture, harness):
    harness.start_write_probe(page);before=financial(page);dialog=open_close(page,fixture);section=result_section(dialog)
    preview=section.locator('[data-pl-action=closure-preview-result]')
    preview.click();assert not section.locator('[data-pl-action=closure-save-result]').is_visible() or section.locator('[data-pl-action=closure-save-result]').is_disabled(), 'empty result cannot be saved'
    section.locator('[name=closureResultUnit]').select_option('PERCENT');section.locator('[name=closureResultValue]').fill('3.333');preview.click()
    summary=dialog.locator('[data-pl-closure-result-review]').inner_text();assert '33,33' in summary, ('percentage rounds actual USD to cents',summary)
    section.locator('[name=closureResultValue]').fill('-1.25');preview.click();result_preview_oracle(page,dialog,-12.5)
    section.locator('[name=closureResultUnit]').select_option('USD');section.locator('[name=closureResultValue]').fill('1.001');preview.click()
    save=section.locator('[data-pl-action=closure-save-result]');assert not save.is_visible() or save.is_disabled(), 'USD fractions beyond cents cannot be confirmed'
    harness.no_writes(page);assert financial(page)==before
    return {'percent_rounded':33.33,'negative_percent':-12.5,'empty_invalid':True}


def changed_review(page, fixture, harness):
    command(page,fixture,'recordResult',month=fixture['start'],usd=10)
    page.evaluate('JPWPlanning.ui.render(true)');dialog=open_close(page,fixture);dialog.locator('[name=confirmFlows]').check()
    command(page,fixture,'recordContribution',month=fixture['start'],usd=20,brl=100)
    harness.start_write_probe(page);before=financial(page)
    dialog.locator('[data-pl-submit]').click()
    refresh=dialog.locator('[data-pl-action=draft-refresh]');assert refresh.is_visible(), 'changed data offers explicit re-review'
    assert closure_state(page,fixture)['closure'] is None;assert len(page.evaluate('__visualWriterCalls'))==0
    refresh.click();assert not dialog.locator('[name=confirmFlows]').is_checked()
    assert '1.030,00' in dialog.locator('[data-pl-closure-review]').inner_text(), 'refreshed closure displays updated effective amounts'
    assert financial(page)==before
    dialog.locator('[name=confirmFlows]').check();dialog.locator('[data-pl-submit]').click();dialog.wait_for(state='hidden')
    assert closure_state(page,fixture)['closure']['snapshot']['closeUsd']==1030
    return {'external_revision_requires_review':True,'updated_close':1030}


def refusal_unknown(page, fixture, harness):
    harness.start_write_probe(page);dialog=open_close(page,fixture);result_section(dialog)
    section=dialog.locator('[data-pl-closure-result]');section.locator('[name=closureResultUnit]').select_option('USD');section.locator('[name=closureResultValue]').fill('5');section.locator('[data-pl-action=closure-preview-result]').click()
    before=financial(page)
    page.evaluate("()=>{window.__closeOriginalWriter=jpWealthPersistDocument;jpWealthPersistDocument=()=>({ok:false,status:'REFUSED',reason:'synthetic-refusal'})}")
    try:
        section.locator('[data-pl-action=closure-save-result]').click()
        assert financial(page)==before and closure_state(page,fixture)['result'] is None
        assert section.locator('[name=closureResultValue]').input_value()=='5', 'refusal retains result draft'
        dialog.locator('[data-pl-action=draft-refresh]').click()
        section=dialog.locator('[data-pl-closure-result]');section.locator('[data-pl-action=closure-preview-result]').click()
        page.evaluate("jpWealthPersistDocument=()=>({ok:false,status:'UNKNOWN',reason:'synthetic-unknown'})")
        section.locator('[data-pl-action=closure-save-result]').click()
        assert financial(page)==before
        assert 'indetermin' in dialog.inner_text().lower()
        save=dialog.locator('[data-pl-action=closure-save-result]');assert not save.is_visible() or save.is_disabled(), 'unknown result cannot be retried blindly'
        refresh=dialog.locator('[data-pl-action=draft-refresh]');assert not refresh.is_visible() or refresh.is_disabled(), 'unknown cannot be reset by refreshing a token'
    finally:page.evaluate('jpWealthPersistDocument=__closeOriginalWriter')
    return {'refused_preserved':True,'unknown_locked':True}


def shared_flow(page, fixture, harness):
    page.get_by_role('button',name='Registrar rentabilidade',exact=True).click()
    dialog=page.locator('#planning dialog.pl-dialog');dialog.locator('[data-pl-submit]').click();dialog.locator('[name=usd]').fill('5');dialog.locator('[data-pl-submit]').click()
    dialog.get_by_role('button',name='Cancelar',exact=True).click()
    command(page,fixture,'recordContribution',month=fixture['start'],usd=10,brl=50)
    harness.start_write_probe(page);before=financial(page)
    page.get_by_role('button',name='Registrar rentabilidade',exact=True).click();dialog=page.locator('#planning dialog.pl-dialog')
    assert dialog.locator('[data-pl-action=draft-refresh]').is_visible(), 'shared modal flow detects old draft revision'
    assert dialog.locator('[name=usd]').input_value()=='5', 'stale legacy flow preserves input'
    dialog.locator('[data-pl-action=draft-refresh]').click()
    harness.no_writes(page);assert financial(page)==before
    # Revalidation follows the existing month/value/review sequence.
    for _ in range(3):
        if dialog.locator('[data-pl-flow-step=review]').is_visible():break
        dialog.locator('[data-pl-submit]').click()
    assert dialog.locator('[data-pl-flow-step=review]').is_visible()
    harness.no_writes(page)
    dialog.locator('[data-pl-submit]').click();dialog.wait_for(state='hidden')
    assert closure_state(page,fixture)['result']['usd']==5
    assert page.evaluate('__visualCommandCalls')==['recordResult']
    return {'shared_flow_preserves_value':5,'explicit_review':True}


def zero_opening(page,fixture,harness):
    fixture=seed(page,initial=0);compact.select(page,fixture);harness.start_write_probe(page)
    dialog=open_close(page,fixture);section=result_section(dialog)
    unit=section.locator('[name=closureResultUnit]');percent_option=unit.locator('option[value=PERCENT]')
    assert unit.input_value()=='USD' and (percent_option.count()==0 or percent_option.evaluate('n=>n.disabled')), 'without positive opening, USD remains available and percentage is disabled'
    unit.focus();unit.press('ArrowUp');assert unit.input_value()=='USD', 'keyboard cannot select unavailable percentage conversion'
    record_result(dialog,'0','USD');assert closure_state(page,fixture)['result']['usd']==0
    dialog.locator('[name=confirmFlows]').check();dialog.locator('[data-pl-submit]').click();dialog.wait_for(state='hidden')
    assert closure_state(page,fixture)['closure']['snapshot']['closeUsd']==0
    return {'zero_opening_usd_closes':True}


def backup_retention(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page);dialog=open_close(page,fixture);section=result_section(dialog)
    section.locator('[name=closureResultUnit]').select_option('USD');section.locator('[name=closureResultValue]').fill('-12.50')
    page.keyboard.press('Escape')
    items=page.evaluate("jpwWorkspaceCapture().drafts.filter(d=>d.provider==='patrimonial-planning')")
    assert len(items)==1, ('one existing-format financial draft',items)
    fields=json.loads(items[0]['text'])['fields']
    assert fields['unit']=='USD' and fields['value']=='-12.50', ('closure input remains readable in backup',fields)
    assert 'token' not in json.dumps(items), 'draft exports no operational token'
    assert page.evaluate('(d)=>JPWWorkspaceDrafts.inspect(d).compatible',items[0]) is False, 'imported financial draft is read-only'
    dialog=open_close(page,fixture)
    assert dialog.locator('[name=closureResultValue]').input_value()=='-12.50', 'in-session restoration preserves exact input'
    assert dialog.locator('[name=closureResultUnit]').input_value()=='USD'
    harness.no_writes(page);assert financial(page)==before
    return {'backup_value':'-12.50','backup_unit':'USD','read_only_import':True}


def invalidated_context(page,fixture,harness):
    observed=[]
    for mode in ['replaced-plan','replaced-root','archived-account']:
        context=page.context.browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',reduced_motion='reduce')
        try:
            target=harness.setup(context,page.url);f=seed(target);compact.select(target,f);dialog=open_close(target,f)
            section=dialog.locator('[data-pl-closure-result]');section.locator('[name=closureResultUnit]').select_option('USD');section.locator('[name=closureResultValue]').fill('17');section.locator('[data-pl-action=closure-preview-result]').click()
            if mode=='replaced-plan':
                phrase=target.evaluate('id=>JPWPlanning.queries.previewReset({accountId:id,scope:"CONTA"}).phrase',f['id']);command(target,f,'resetAccount',confirmation=phrase)
            elif mode=='archived-account':command(target,f,'archiveAccount',confirmation=True)
            else:target.evaluate('S=structuredClone(S)')
            harness.start_write_probe(target);before=financial(target)
            section.locator('[data-pl-action=closure-save-result]').click()
            refresh=dialog.locator('[data-pl-action=draft-refresh]');assert refresh.is_visible()
            if refresh.is_enabled():refresh.click()
            assert dialog.locator('[name=closureResultValue]').input_value()=='17', 'invalidated context preserves readable draft'
            save=dialog.locator('[data-pl-action=closure-save-result]');assert not save.is_visible() or save.is_disabled(), 'invalidated context cannot be refreshed into write authority'
            harness.no_writes(target);assert financial(target)==before
            observed.append({'mode':mode,'retained_value':'17','writes':0})
        finally:context.close()
    return observed


def regressions(browser,url,report,harness):
    actions=[missing_recovery,cancelled_conflict,save_cancel,previous_navigation,units_validation,changed_review,refusal_unknown,shared_flow,zero_opening,backup_retention,invalidated_context]
    for case_id,action in zip(REGRESSIONS,actions):
        if report.get('only') and case_id not in report['only']:continue
        context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',reduced_motion='reduce')
        try:
            page=harness.setup(context,url);fixture=seed(page);compact.select(page,fixture)
            page.locator('[data-pl-month]').select_option(fixture['start'])
            harness.record(report,case_id,lambda:action(page,fixture,harness),page)
        finally:context.close()


def geometry(page,fixture,harness):
    before=financial(page);harness.start_write_probe(page);dialog=open_close(page,fixture)
    assert dialog.locator('[data-pl-closure-result]').is_visible(), 'closure result remains reachable'
    data=dialog.evaluate('''d=>{const r=d.getBoundingClientRect();return{rect:r.toJSON(),viewport:[visualViewport?visualViewport.width:innerWidth,visualViewport?visualViewport.height:innerHeight],roundedInner:[innerWidth,innerHeight],widths:[d.clientWidth,d.scrollWidth],fields:[...d.querySelectorAll('input,select')].filter(n=>n.getClientRects().length).map(n=>({name:n.name,rect:n.getBoundingClientRect().toJSON()}))}}''')
    r=data['rect'];w,h=data['viewport']
    assert r['left']>=11.75 and r['right']<=w-11.75 and r['top']>=11.75 and r['bottom']<=h-11.75, ('dialog remains inside available viewport',data)
    assert abs((r['left']+r['right'])/2-w/2)<=2, ('closure horizontally centered',data)
    assert data['widths'][1]<=data['widths'][0]+1, ('no dialog horizontal overflow',data)
    for selector in ['.pl-close','[data-pl-action=closure-preview-result]']:
        control=dialog.locator(selector);control.scroll_into_view_if_needed()
        harness.centered(control,'ink' if selector=='.pl-close' else 'text',selector=='.pl-close')
        rect=control.bounding_box();assert rect['height']>=44 and rect['width']>=44, ('44px closure action target',selector,rect)
    section=dialog.locator('[data-pl-closure-result]');section.locator('[name=closureResultValue]').fill('0');section.locator('[data-pl-action=closure-preview-result]').click()
    result_preview_oracle(page,dialog,0)
    save=dialog.locator('[data-pl-action=closure-save-result]');save.scroll_into_view_if_needed();harness.centered(save)
    box=save.bounding_box();assert box['height']>=44
    harness.no_writes(page);assert financial(page)==before
    page.keyboard.press('Escape');assert page.locator('#planning dialog.pl-dialog').count()==0
    assert page.evaluate('document.activeElement!==document.body'), 'Escape returns focus to live control'
    return data


def matrix(browser,url,report,harness):
    context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block',reduced_motion='reduce')
    try:
        page=harness.setup(context,url);fixture=seed(page);compact.select(page,fixture)
        for layout in planning.LAYOUTS:
            page.evaluate('v=>mountNavigationLayout(v)',layout)
            for theme in planning.THEMES:
                page.evaluate('v=>{document.documentElement.dataset.theme=v;document.body.dataset.theme=v}',theme)
                for width in [390,1440]:
                    for _ in range(2):page.keyboard.press('Escape')
                    page.set_viewport_size({'width':width,'height':844 if width==390 else 1000})
                    # Each geometry opens a fresh revision; the cancelled input remains a draft.
                    harness.record(report,f'closure-matrix-{layout}-{theme}-{width}',lambda:geometry(page,fixture,harness),page)
    finally:context.close()


def native_zoom(pw,url,report,harness):
    profile=Path(tempfile.mkdtemp(prefix='closure-native200-',dir=report['out']));(profile/'Default').mkdir()
    (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
    from notes_launcher_test import launch_options
    options=launch_options();options.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
    try:
        context=pw.chromium.launch_persistent_context(str(profile),**options)
        try:
            page=harness.setup(context,url);fixture=seed(page);compact.select(page,fixture)
            zoom=page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
            assert abs(zoom['outer']/zoom['inner']-2)<.01 and zoom['css']=='1', ('actual native200 required',zoom)
            for layout in planning.LAYOUTS:
                page.evaluate('v=>mountNavigationLayout(v)',layout)
                for theme in planning.THEMES:
                    for _ in range(2):page.keyboard.press('Escape')
                    page.evaluate('v=>{document.documentElement.dataset.theme=v;document.body.dataset.theme=v}',theme)
                    harness.record(report,f'closure-native200-{layout}-{theme}',lambda:geometry(page,fixture,harness),page,native_zoom=zoom)
        finally:context.close()
    finally:shutil.rmtree(profile)


def counterproofs(browser,url,report,harness):
    for identity in COUNTERPROOFS:
        context=browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
        try:
            page=harness.setup(context,url);fixture=seed(page);compact.select(page,fixture);dialog=open_close(page,fixture)
            def proof():
                before=financial(page);harness.start_write_probe(page)
                if identity.endswith('missing-recovery'):
                    valid=result_section(dialog).is_visible();dialog.locator('[data-pl-closure-result]').evaluate('n=>n.hidden=true')
                    rejected=harness.rejected(lambda:result_section(dialog))
                    dialog.locator('[data-pl-closure-result]').evaluate('n=>n.hidden=false')
                    assert result_section(dialog).is_visible()
                elif identity.endswith('positive-loss'):
                    section=dialog.locator('[data-pl-closure-result]');section.locator('[name=closureResultUnit]').select_option('USD');section.locator('[name=closureResultValue]').fill('-12.5');section.locator('[data-pl-action=closure-preview-result]').click();valid=result_preview_oracle(page,dialog,-12.5)
                    review=dialog.locator('[data-pl-closure-result-review]');original=review.inner_html()
                    review.evaluate("n=>n.textContent=new Intl.NumberFormat('pt-BR',{style:'currency',currency:'USD'}).format(12.5)")
                    rejected=harness.rejected(lambda:result_preview_oracle(page,dialog,-12.5));review.evaluate('(n,x)=>n.innerHTML=x',original)
                    result_preview_oracle(page,dialog,-12.5)
                else:
                    dialog.get_by_role('button',name='Cancelar',exact=True).click();command(page,fixture,'recordResult',month=fixture['start'],usd=0);harness.start_write_probe(page);before=financial(page);dialog2=open_close(page,fixture);valid=fresh_consent_oracle(dialog2)
                    dialog2.locator('[name=confirmFlows]').evaluate('n=>n.checked=true')
                    rejected=harness.rejected(lambda:fresh_consent_oracle(dialog2));dialog2.locator('[name=confirmFlows]').evaluate('n=>n.checked=false');fresh_consent_oracle(dialog2)
                harness.no_writes(page);assert financial(page)==before
                return {'positive':valid,'representative_violation_rejected':rejected}
            harness.record(report,identity,proof,page)
        finally:context.close()


def main():
    import ui_visual_quality_test as harness
    from browser_fixture_server import BrowserFixtureServer
    from playwright.sync_api import sync_playwright
    from notes_launcher_test import launch_options
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--only',nargs='+',choices=REGRESSIONS);args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    sources=['src/js/30-accounting/06-planning/02-state.js','src/js/30-accounting/06-planning/03-ui.js','src/styles/app.css','tools/planning_monthly_close_test.py']
    hashes=lambda:{f:sha256((ROOT/f).read_bytes()).hexdigest() for f in sources}
    report={'started_at':datetime.now(timezone.utc).isoformat(),'out':str(args.out),'only':args.only,'required_case_ids':args.only or required_ids(),'cases':[],'source_sha256':hashes()}
    server=BrowserFixtureServer(('127.0.0.1',0),partial(planning.Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options());report['browser']=browser.version
            url=f'http://127.0.0.1:{server.server_port}/index.html'
            regressions(browser,url,report,harness)
            if not args.only:counterproofs(browser,url,report,harness);matrix(browser,url,report,harness)
            browser.close()
            if not args.only:native_zoom(pw,url,report,harness)
        report['coverage']=harness.validate_coverage(report['cases'],report['required_case_ids'])
        report['classification']='PASS' if all(c['classification']=='PASS' for c in report['cases']) else 'PRODUCT_FAIL'
    finally:
        server.shutdown();server.server_close();report['source_unchanged']=report['source_sha256']==hashes();report['finished_at']=datetime.now(timezone.utc).isoformat();(args.out/'planning-monthly-close-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(report['classification']+' cases='+str(len(report['cases'])))
    return 0 if report['classification']=='PASS' and report['source_unchanged'] else 1


if __name__=='__main__':raise SystemExit(main())

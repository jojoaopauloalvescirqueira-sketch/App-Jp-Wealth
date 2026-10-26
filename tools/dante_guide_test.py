"""Dante integration cases exercised by the existing learning-guide entrypoint.

No replacement navigation, guide, writer or progress store. Inputs below are
synthetic auxiliary guide documents; financial state remains unchanged.
"""
import json
import os
from pathlib import Path
import subprocess

KEY='jpwealth_learning_guide_v1'


def models(page,row):
    """Keep pure model protections on the same permanent full-gate entrypoint."""
    root=Path(__file__).resolve().parents[1]
    node=os.environ.get('JPW_NODE','node');results=[]
    for name in ['learning_foundation_test.mjs','learning_controller_test.mjs','dante_catalog_test.mjs']:
        result=subprocess.run([node,str(root/'tools'/name)],cwd=root,text=True,capture_output=True,timeout=90)
        assert result.returncode==0,(name,result.stdout[-1500:],result.stderr[-1500:])
        results.append({'test':name,'exit':result.returncode,'output':result.stdout[-700:]})
    row['models']=results


def profile(page,row):
    from dante_profile_test import default_contract, welcome_contract
    url=page.url
    browser=page.context.browser
    default_contract(browser,url)
    welcome_contract(browser,url)
    row['profileAndWelcome']='confirmed through disposable real UI, default never writes identity'


def helpers():
    import learning_guide_test as guide
    return guide


def state(page):
    return page.evaluate('JPWLearningGuide.snapshot()')


def journey(page,row):
    g=helpers();g.instrument(page);before=g.financial(page)
    assert page.evaluate('JPWLearningGuide.startJourney()') is True
    page.locator('#jpwLearningCoach').wait_for(state='visible')
    cursor=state(page)
    assert cursor['mode']=='journey' and cursor['stepId']=='basics-home'
    assert cursor['progress']['steps']=={},'Starting is not proof of reading/practice'
    # Snapshot boundaries supplied by the catalog are independent of the controller.
    chapters=page.evaluate('JPWLearningCatalog.journey')
    assert [c['id'] for c in chapters]==['basics','research','planning','forex','personal-finance','tools','alladin','general']
    before_ids=[]
    for index in [0,1,2]:
        last=chapters[index]['stepIds'][-1];target=chapters[index+1]['stepIds'][0]
        assert page.evaluate('(stepId)=>JPWLearningGuide.startJourney({stepId})',last)
        page.locator('#jpwLearningSkip').click()
        page.wait_for_function('id=>JPWLearningGuide.snapshot().stepId===id',arg=target)
        got=state(page);assert got['mode']=='journey' and got['progress']['steps'][last]['orientation']=='skipped'
        owner=page.evaluate('id=>JPWLearningCatalog.tracks.find(t=>t.steps.some(s=>s.id===id)).id',target)
        assert got['trackId']==owner,'Cross-chapter step must retain legacy owner'
        before_ids.append([last,target])
    g.invariant(page,before);row.update(boundaries=before_ids,financialWrites=0)


def legacy(page,row):
    g=helpers();g.instrument(page);before=g.financial(page)
    document={'schemaVersion':1,'catalogVersion':1,'trackId':'basics','stepId':'basics-home','paused':True,
              'steps':{'basics-home':{'orientation':'seen','practice':None},'basics-menu':{'orientation':'skipped','practice':None}}}
    raw=json.dumps(document,separators=(',',':'))
    page.evaluate('([key,raw])=>localStorage.setItem(key,raw)',[KEY,raw]);page.reload();g.wait_bootstrap(page)
    assert page.evaluate('key=>localStorage.getItem(key)',KEY)==raw,'Reading v1 rewrote original bytes'
    cursor=state(page);assert cursor['mode']=='track' and cursor['progress']['steps']==document['steps']
    assert page.evaluate('JPWLearningGuide.resume()') is True
    stored=json.loads(page.evaluate('key=>localStorage.getItem(key)',KEY))
    assert stored['schemaVersion']==2 and stored['mode']=='track' and stored['steps']==document['steps']
    assert set(stored)=={'schemaVersion','catalogVersion','mode','trackId','stepId','paused','steps'}
    assert page.evaluate("JPWLearningGuide.start('basics')") is True
    for _ in range(6):
        page.locator('#jpwLearningSkip').click()
    assert state(page)['paused'] and state(page)['stepId']=='basics-progress','Legacy track leaked into next chapter'
    # Reload normalizes the same confirmed main state, never inventing facts.
    assert page.evaluate('JSON.stringify(S)')==before['state']
    row.update(v1ReadWithoutWrite=True,legacyModePreserved=True,legacyRecords=document['steps'])


def frozen(page,row):
    g=helpers();g.instrument(page);before=g.financial(page)
    assert page.evaluate("JPWModuleAvailability.setState('forex','frozen').ok")
    assert page.evaluate("JPWLearningGuide.startJourney({stepId:'forex-planning'})")
    assert page.evaluate("JPWNavigation.current().primary==='planning'"),'Planning depends on frozen Forex'
    assert page.evaluate("JPWLearningGuide.startJourney({stepId:'forex-accounts'})")
    page.locator('#jpwLearningCoach').wait_for(state='visible')
    page.wait_for_function("document.getElementById('jpwLearningNext').textContent.includes('próxima área')")
    before_progress=state(page)['progress']['steps']
    page.locator('#jpwLearningNext').click()
    got=state(page)
    assert got['stepId']=='personal-finance-overview','Unavailable chapter did not advance to next area'
    for step in page.evaluate("JPWLearningCatalog.tracks.find(t=>t.id==='forex').steps.map(s=>s.id)"):
        assert got['progress']['steps'].get(step)==before_progress.get(step),'Unavailable lessons received fictional progress'
    assert page.evaluate("JPWModuleAvailability.canAccess('forex')") is False
    g.invariant(page,before);row['frozenExplanationTraversable']=True


def speech(page,row):
    g=helpers();g.instrument(page);before=g.financial(page)
    assert page.evaluate('JPWLearningGuide.startJourney()')
    page.locator('#jpwLearningSpeech').wait_for(state='visible')
    whole=page.locator('#jpwLearningSpeechAccessible').inner_text()
    initial=page.locator('#jpwLearningSpeech').inner_text()
    assert whole and len(initial)<len(whole),('Typewriter missing',initial,whole)
    page.locator('#jpwLearningUnderstand').click()
    assert page.locator('#jpwLearningSpeech').inner_text()==whole,'First action must reveal whole phrase'
    assert state(page)['progress']['steps']=={},'Reveal recorded read/practice'
    page.locator('#jpwLearningPause').click()
    raw=page.evaluate('key=>localStorage.getItem(key)',KEY)
    page.wait_for_timeout(150)
    assert page.locator('#jpwLearningCoach').count()==0,'Pause left animated coach mounted'
    assert page.evaluate('JPWLearningGuide.resume()')
    assert page.locator('#jpwLearningSpeech').inner_text()==page.locator('#jpwLearningSpeechAccessible').inner_text()
    assert not state(page)['progress']['steps']
    assert raw and 'speechIndex' not in raw and 'speechText' not in raw
    g.invariant(page,before);row.update(firstRevealOnly=True,pauseCompletePhrase=True)


def reduced(page,row):
    g=helpers();g.instrument(page);before=g.financial(page)
    assert page.evaluate('JPWLearningGuide.startJourney()')
    page.locator('#jpwLearningSpeech').wait_for(state='visible')
    assert page.locator('#jpwLearningSpeech').inner_text()==page.locator('#jpwLearningSpeechAccessible').inner_text()
    assert page.locator('#jpwLearningSpeech').get_attribute('aria-hidden')=='true'
    assert page.locator('#jpwLearningSpeechAccessible').get_attribute('aria-live')=='polite'
    assert state(page)['progress']['steps']=={}
    g.invariant(page,before);row['reducedMotionFullText']=True


def index(page,row):
    g=helpers();g.instrument(page);before=g.financial(page);g.central(page)
    target=page.locator('[data-learning-step="planning-consolidated"]')
    target.locator('xpath=ancestor::details').locator('summary').click()
    target.click();page.wait_for_function("JPWLearningGuide.snapshot().stepId==='planning-consolidated'")
    assert state(page)['mode']=='journey'
    assert page.evaluate('JPWLearningGuide.pause()') is True
    page.reload();g.wait_bootstrap(page)
    assert state(page)['stepId']=='planning-consolidated' and state(page)['paused']
    assert not state(page)['progress']['steps'],'Index click fabricated completion'
    assert page.evaluate('JSON.stringify(S)')==before['state'];row['singleBookmark']='planning-consolidated'


def planning_form(page,row):
    g=helpers();g.instrument(page);before=g.financial(page)
    assert page.evaluate("JPWLearningGuide.startJourney({stepId:'planning-form'})")
    page.locator('#planning [data-pl-action="configure"]').click()
    dialog=page.locator('#planning dialog.pl-dialog[open]')
    dialog.wait_for(state='visible')
    page.wait_for_function("!JPWLearningGuide.snapshot().paused&&!!document.querySelector('#planning dialog[open] #jpwLearningCoach')")
    dialog.locator('details.optional-section:has(#pl-native-nome) > summary').click()
    field=dialog.locator('#pl-native-nome');g.pointer_uncovered(page,'#pl-native-nome');field.fill('Conta apenas em rascunho Dante')
    field.focus();g.settle(page)
    assert field.input_value()=='Conta apenas em rascunho Dante' and field.evaluate('e=>document.activeElement===e')
    assert not state(page)['paused'],'Guide suspended its own account form'
    # Known plan inputs, no submit: the projection must never become a fact.
    for selector,value in [('#pl-native-saldo','1000'),('#pl-native-aporte','100')]:
        dialog.locator(selector).fill(value)
    g.invariant(page,before)
    page.locator('#jpwLearningPause').click()
    assert dialog.is_visible() and field.input_value()=='Conta apenas em rascunho Dante'
    assert page.evaluate('JPWLearningGuide.resume()')
    assert dialog.locator('#jpwLearningCoach').is_visible() and not state(page)['progress']['steps']
    g.invariant(page,before);row['ownedFormDraft']='preserved, no account writer or automatic selection'


def agenda_form(page,row):
    g=helpers();g.instrument(page);before=g.financial(page)
    assert page.evaluate("JPWLearningGuide.startJourney({stepId:'tools-agenda'})")
    panel=page.locator('#execEcal .calendar-panel')
    panel.locator('[data-calendar-action="new"]').click()
    form=panel.locator('.calendar-form')
    form.locator('[name="title"]').fill('Compromisso só em rascunho Dante')
    form.locator('[name="kind"]').select_option('appointment')
    form=panel.locator('.calendar-form');form.locator('[name="allDay"]').uncheck()
    form=panel.locator('.calendar-form');form.locator('[name="timeZone"]').fill('America/Sao_Paulo')
    page.wait_for_function("!JPWLearningGuide.snapshot().paused")
    assert form.locator('[name="title"]').input_value()=='Compromisso só em rascunho Dante'
    g.invariant(page,before)
    form.locator('[data-calendar-action="cancel-form"]').click()
    assert panel.locator('.calendar-form').count()==0
    assert not state(page)['progress']['steps'],'Cancel was recorded as practice'
    g.invariant(page,before);row['agendaDraft']='type/time-zone changes and cancellation preserve finance'


def monthly_form(page,row):
    g=helpers()
    setup=page.evaluate('''()=>{
      const date=new Date(),month=date.getFullYear()+'-'+String(date.getMonth()+1).padStart(2,'0');
      const result=JPWPlanning.commands.execute('createAccount',{name:'SYN Dante month',startMonth:month,
        initialUsd:1000,profileId:'base',monthlyContributionUsd:100,
        goals:{adequate:{value:50,currency:'USD'},ideal:{value:100,currency:'USD'}}},JPWPlanning.queries.token());
      if(!result.ok)throw Error('Synthetic account setup refused: '+JSON.stringify(result));
      JPWPlanning.ui.render(true);return {accountId:result.accountId,month};
    }''')
    g.instrument(page);before=g.financial(page)
    assert page.evaluate("JPWLearningGuide.startJourney({stepId:'planning-monthly'})")
    page.locator('#planning [data-pl-view="monthly"]').click()
    page.locator('[data-pl-inline-open="result"][data-pl-inline-month="'+setup['month']+'"]').click()
    editor=page.locator('#planning .pl-inline-editor')
    editor.locator('[name="unit"]').select_option('USD');editor.locator('[name="value"]').fill('25')
    page.wait_for_function("!JPWLearningGuide.snapshot().paused")
    assert editor.locator('[name="value"]').input_value()=='25'
    g.invariant(page,before)
    editor.locator('[data-pl-inline-save]').click()
    assert editor.locator('[data-pl-inline-review]').is_visible()
    assert not state(page)['paused'] and not state(page)['progress']['steps']
    g.invariant(page,before);row['monthlyDraft']='real editor and review preserved without confirmation/write'


def touch(page,row):
    g=helpers();g.instrument(page);before=g.financial(page)
    assert page.evaluate('JPWLearningGuide.startJourney()')
    page.locator('#jpwLearningSpeech').wait_for(state='visible')
    whole=page.locator('#jpwLearningSpeechAccessible').inner_text()
    page.locator('.jpw-dante-speech').tap()
    assert page.locator('#jpwLearningSpeech').inner_text()==whole
    assert not state(page)['progress']['steps']
    page.locator('.jpw-dante-speech').tap()
    assert page.locator('#jpwLearningSpeechAccessible').inner_text()!=whole
    assert not state(page)['progress']['steps']
    g.invariant(page,before);row['touch']='first reveals, second advances speech, no credit'


def cases():
    return [('dante/model-contracts',models,{}),('dante/profile-and-welcome',profile,{}),
            ('dante/journey-cross-chapter',journey,{}),('dante/v1-and-legacy-track',legacy,{}),
            ('dante/frozen-and-independent-planning',frozen,{}),
            ('dante/typewriter-reveal-pause',speech,{'motion':'no-preference'}),
            ('dante/reduced-motion',reduced,{}),('dante/index-single-bookmark',index,{}),
            ('dante/planning-owned-form',planning_form,{}),('dante/agenda-owned-form',agenda_form,{}),
            ('dante/planning-monthly-editor',monthly_form,{}),
            ('dante/planning-owned-form/mobile',planning_form,{'width':390,'height':844}),
            ('dante/agenda-owned-form/mobile',agenda_form,{'width':390,'height':844}),
            ('dante/touch-balloon',touch,{'touch':True,'motion':'no-preference','width':390,'height':844})]

"""Additive Dante geometry contract; no financial fixtures or writes.

The shared visual runner supplies content-ink centering and classification.
Approved source: Dante plan24/10/2026; previous visual cases remain unchanged.
"""
from pathlib import Path
import json
import math
import tempfile
import shutil

from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options
from calendar_visual_quality_test import reachable

LAYOUTS = ('sidebar', 'topbar', 'glass', 'submenu')
THEMES = ('light', 'dark')
SIZES = ((320, 700), (390, 844), (900, 720), (1440, 900))


def required_ids():
    return ([f'dante-{layout}-{theme}-{w}x{h}' for w,h in SIZES for layout in LAYOUTS for theme in THEMES]
            + [f'dante-native200-{layout}-{theme}' for layout in LAYOUTS for theme in THEMES]
            + ['dante-counterproof-'+name for name in ('inner-text','small-target','speech-overflow')])


def setup(context, url, layout='sidebar', theme='light'):
    install_bootstrap(context)
    context.add_init_script('window.__onbShown=true;localStorage.setItem("jpw_nav_layout",'+json.dumps(layout)+');')
    page=context.new_page();page.set_default_timeout(7000)
    page._dante_errors=[];page._visual_errors=page._dante_errors;page.on('pageerror',lambda error:page._dante_errors.append(str(error)))
    page.goto(url,wait_until='load');wait_bootstrap(page)
    page.evaluate('closeModal()')
    page.evaluate('(theme)=>{S.theme=theme;applyTheme();renderThemeSeg();}',theme)
    return page


def financial(page):
    return page.evaluate('({state:JSON.stringify(S),raw:localStorage.getItem("jpwealth_v9_state"),profile:localStorage.getItem("jpwealth_local_profile_v1")})')


def coach(page):
    assert page.evaluate('typeof JPWLearningGuide.startJourney')=='function','DANTE-G01: journey API missing'
    assert page.evaluate('JPWLearningGuide.startJourney()') is True
    page.locator('#jpwLearningCoach').wait_for(state='visible')


def geometry(page, visual):
    card=page.locator('#jpwLearningCoach')
    data=card.evaluate('''e=>{const b=e.getBoundingClientRect(),s=document.getElementById('jpwLearningSpeech'),r=s.getBoundingClientRect();
      return {box:b.toJSON(),viewport:[innerWidth,innerHeight],scroll:[e.scrollWidth,e.clientWidth],speech:{box:r.toJSON(),scroll:s.scrollWidth,client:s.clientWidth},
      images:[...e.querySelectorAll('img')].map(i=>({complete:i.complete,width:i.naturalWidth,source:i.currentSrc}))};}''')
    b=data['box'];w,h=data['viewport']
    assert b['width']>0 and b['height']>0 and b['left']>=-.25 and b['right']<=w+.25,('Dante card horizontal containment',data)
    assert data['scroll'][0]<=data['scroll'][1]+1,('Dante card horizontal overflow',data)
    assert data['speech']['scroll']<=data['speech']['client']+1,('Speech must wrap without hiding content',data)
    assert data['images'] and all(i['complete'] and i['width']>0 for i in data['images']),('Dante image missing',data)
    measured=[]
    for selector in ['#jpwLearningUnderstand','#jpwLearningNext','#jpwLearningSkip','#jpwLearningPause']:
        button=page.locator(selector)
        if button.is_visible():
            box=button.bounding_box();assert box['width']>=44 and box['height']>=44,(selector,'44px target',box)
            measured.append({'selector':selector,'center':visual.centered(button),'reachable':reachable(button)})
    assert page.locator('#jpwLearningSpeech').get_attribute('aria-hidden')=='true'
    accessible=page.locator('#jpwLearningSpeechAccessible')
    assert accessible.inner_text().strip() and accessible.get_attribute('aria-live')=='polite'
    assert not page._dante_errors,page._dante_errors
    return {'card':data,'controls':measured}


def matrix(browser, url, report, visual):
    for width,height in SIZES:
        for layout in LAYOUTS:
            for theme in THEMES:
                context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce',service_workers='block')
                try:
                    page=setup(context,url,layout,theme);before=financial(page);coach(page)
                    def check():
                        result=geometry(page,visual);assert financial(page)==before,'Dante guide view changed finance/profile'
                        return result
                    visual.record(report,f'dante-{layout}-{theme}-{width}x{height}',check,page=page,
                                  criteria='44pxtarget;innercontent<=2CSSpx;reflow;image;noFinancialWrites',layout=layout,theme=theme,viewport=[width,height])
                    assert_fixture_requests(context)
                finally:context.close()
    counterproofs(browser,url,report,visual)


def counterproofs(browser,url,report,visual):
    mutations={
        'inner-text':"e=>{const s=document.createElement('span');s.textContent=e.textContent;e.replaceChildren(s);s.style.transform='translateY(5px)';s.style.display='inline-block'}",
        'small-target':"e=>{e.style.setProperty('min-height','20px','important');e.style.setProperty('height','20px','important');e.style.padding='0';e.style.lineHeight='12px'}",
        'speech-overflow':"e=>{const s=document.getElementById('jpwLearningSpeech');s.style.whiteSpace='nowrap';s.style.width='80px';s.style.overflow='visible'}",
    }
    for name,mutation in mutations.items():
        context=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce',service_workers='block')
        try:
            page=setup(context,url);coach(page);geometry(page,visual)
            page.locator('#jpwLearningUnderstand').evaluate(mutation)
            def rejects():
                try:geometry(page,visual)
                except AssertionError as error:return {'rejected':True,'reason':str(error)[:900]}
                raise AssertionError('Dante visual oracle accepted deliberately invalid '+name)
            visual.record(report,'dante-counterproof-'+name,rejects,page=page,criteria='samegeometryrejectsrepresentativeviolation')
        finally:context.close()


def native_zoom(pw,url,report,visual):
    for layout in LAYOUTS:
        for theme in THEMES:
            profile=Path(tempfile.mkdtemp(prefix='jpw-dante-native200-'))
            (profile/'Default').mkdir();(profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
            options=launch_options();options.update(headless=True,no_viewport=True,args=['--window-size=1440,1000'],reduced_motion='reduce',service_workers='block')
            context=None
            try:
                context=pw.chromium.launch_persistent_context(str(profile),**options)
                page=setup(context,url,layout,theme);coach(page)
                def check():
                    ratio=page.evaluate('outerWidth/innerWidth');assert abs(ratio-2)<.02,('native zoom not200%',ratio)
                    assert page.evaluate('getComputedStyle(document.documentElement).zoom')=='1'
                    return {'native_ratio':ratio,'geometry':geometry(page,visual)}
                visual.record(report,f'dante-native200-{layout}-{theme}',check,page=page,criteria='native200notCSSzoom;44px;2px;reflow')
            finally:
                if context:context.close()
                shutil.rmtree(profile)

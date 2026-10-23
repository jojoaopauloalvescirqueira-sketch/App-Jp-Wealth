#!/usr/bin/env python3
"""Approved module availability: actual UI, isolated synthetic origins, no user data."""
import json
from pathlib import Path
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from dashboard_macro_test import launch_browser
from dashboard_forex_relocation_test import serve
from browser_bootstrap_fixture import install_bootstrap,wait_bootstrap
ROOT=Path(__file__).resolve().parents[1]
KEY='jpw_module_availability_v1'
ART=ROOT.parent/'evidence'/'availability-ui'

def boot(browser,url,layout='sidebar',width=1440,theme='light'):
    ctx=browser.new_context(viewport={'width':width,'height':1000 if width>900 else 844},service_workers='block')
    install_bootstrap(ctx)
    ctx.add_init_script("window.__onbShown=true;localStorage.setItem('jpw_nav_layout',"+json.dumps(layout)+");")
    q=ctx.new_page();errors=[];q.on('pageerror',lambda e:errors.append(str(e)))
    q.on('dialog',lambda d:d.accept())
    q.goto(url);q.wait_for_function('window.JPWModuleAvailabilityUI && window.JPWModuleWork');wait_bootstrap(q)
    q.evaluate("theme=>{S.theme=theme;applyTheme();}",theme)
    return ctx,q,errors

def notification_and_suspended_work(browser,url):
    """Exercise denial before contextual effects and the real modal transitions."""
    from notification_center_test import seed_review_contexts, REVIEW_CONTEXTS
    passed=[]
    ctx,q,errors=boot(browser,url)
    try:
        seed_review_contexts(q)
        def freeze_then_activate_stale_action():
            # Deliberate replacement: operational reminders disappear when
            # frozen. A click already dispatched before the scheduled collector
            # runs must still be denied before account/period/route effects.
            return q.evaluate("""id=>{
              JPWModuleAvailability.setState('forex','active');
              JPWNotifications.refresh();JPWNotifications.open();
              const action=document.querySelector('[data-notification-go="'+id+'"]');
              if(!action)throw Error('Expected active review action before freeze');
              JPWModuleAvailability.setState('forex','frozen');
              const before=JSON.stringify({state:S,selection:JPWForex.state.operationalSelection(),storage:Object.entries(localStorage).sort()});
              action.click();return before;
            }""",REVIEW_CONTEXTS[0]['notification_id'])
        before=freeze_then_activate_stale_action()
        assert not q.evaluate("document.getElementById('moduleUnavailableDialog')?.open===true"), 'Stale notification may not initiate a new action'
        assert q.locator('#notificationCenter').evaluate('el=>el.open')
        assert q.evaluate('JSON.stringify({state:S,selection:JPWForex.state.operationalSelection(),storage:Object.entries(localStorage).sort()})')==before
        # The unavailable-module decisions retain their own original UI. Invoke
        # that real UI explicitly because frozen operational notifications no
        # longer exist as entry points to it.
        q.evaluate("JPWModuleAvailabilityUI.deny('forex',document.getElementById('notificationClose'))")
        q.locator('[data-availability-stay]').click()
        assert q.locator('#notificationCenter').evaluate('el=>el.open')
        q.evaluate('JPWNotifications.refresh()')
        assert q.locator('[data-notification-id^="forex:"]').count()==0, 'Frozen operational reminders must be suppressed'
        assert q.evaluate("document.getElementById('notificationCenter').contains(document.activeElement)")
        passed.append('stale scoped Forex click: frozen guard prevents account/period/data effects; current operational reminders suppressed')

        before=freeze_then_activate_stale_action()
        q.evaluate("JPWModuleAvailabilityUI.deny('forex',document.getElementById('notificationClose'))")
        q.locator('[data-availability-manage]').click()
        assert not q.locator('#notificationCenter').evaluate('el=>el.open')
        assert not q.locator('#moduleUnavailableDialog').evaluate('el=>el.open')
        assert q.locator('#moduleAvailabilityCard').is_visible()
        q.locator('[data-module-toggle="forex"]').click(trial=True)
        q.locator('#settingsCloseBtn').click()
        before=freeze_then_activate_stale_action()
        q.evaluate("JPWModuleAvailabilityUI.deny('forex',document.getElementById('notificationClose'))")
        q.locator('[data-availability-dashboard]').click()
        assert not q.locator('#notificationCenter').evaluate('el=>el.open')
        assert not q.locator('#moduleUnavailableDialog').evaluate('el=>el.open')
        assert q.evaluate('JPWNavigation.current().primary')=='dashboard'
        q.wait_for_function("document.getElementById('dash').contains(document.activeElement)")
        assert q.evaluate('JSON.stringify({state:S,selection:JPWForex.state.operationalSelection(),storage:Object.entries(localStorage).sort()})')==before
        q.evaluate('S.alladin.schemaVersion=999;JPWNotifications.refresh();JPWNotifications.open()')
        integrity=q.locator('[data-notification-id="alladin:compatibility"]')
        assert integrity.is_visible() and integrity.get_attribute('data-area')=='system', 'Frozen data-integrity issues remain System actions'
        assert q.locator('[data-notification-id^="forex:"]').count()==0
        assert not errors,errors
        passed.append('explicit manage/home preserve data; frozen integrity remains in System without operational reminders')
    finally:ctx.close()

    ctx,q,errors=boot(browser,url,'glass',390)
    try:
        q.evaluate("JPWNavigation.navigate('nocoda')")
        q.locator('#ncPrice1').fill('1.23456')
        q.evaluate("window.__availabilityDraftNode=document.getElementById('ncPrice1');window.__availabilityDraftState=JSON.stringify(S)")
        remote=ctx.new_page();remote.goto(url.rsplit('/',1)[0]+'/build-id.js')
        remote.evaluate("key=>localStorage.setItem(key,JSON.stringify({schemaVersion:1,modules:{research:'frozen'}}))",KEY)
        q.wait_for_function("JPWModuleWork.isSuspended('research')")
        assert q.evaluate("JPWNavigation.current().primary")=='research'
        assert q.locator('#research').evaluate('el=>el.inert')
        q.locator('#moduleAvailabilitySuspended [data-module-manage]').click()
        assert q.locator('#moduleAvailabilityCard').is_visible()
        assert not q.locator('#moduleAvailabilitySuspended').is_visible()
        assert q.locator('#moduleAvailabilitySuspended').evaluate('el=>el.inert')
        q.locator('#moduleAvailabilityReload').click()
        assert q.locator('#settingsOverlay').is_visible()
        q.locator('#settingsCloseBtn').click()
        assert q.locator('#moduleAvailabilitySuspended').is_visible()
        assert q.evaluate("document.getElementById('ncPrice1')===window.__availabilityDraftNode && __availabilityDraftNode.value==='1.23456'")
        q.locator('#brandHomeBtn').click()
        assert q.evaluate("JPWNavigation.current().primary")=='dashboard'
        assert q.evaluate("document.getElementById('ncPrice1')===window.__availabilityDraftNode && __availabilityDraftNode.value==='1.23456'")
        assert q.evaluate('JSON.stringify(S)===window.__availabilityDraftState')
        assert '1.23456' in q.evaluate('JSON.stringify(jpwWorkspaceDrafts())')
        assert not errors,errors
        passed.append('remote Research draft on mobile Glass: Editor stays accessible; home preserves node/value/recoverable work')
    finally:ctx.close()
    return passed

def settings_forex_boundaries(browser,url,passed):
    ctx,q,errors=boot(browser,url)
    q.evaluate("JPWModuleAvailabilityUI.requestChange('forex','frozen')")
    before=q.evaluate('JSON.stringify(S)')
    q.evaluate("openSettingsModal('parameters')")
    q.locator('#settingsReviewPeriodBtn').click()
    assert q.locator('#moduleUnavailableDialog').is_visible()
    assert not q.locator('#modalOverlay').is_visible()
    q.locator('[data-availability-stay]').click()
    q.evaluate("settingsNavigate('tool-check',{push:true,focus:true})")
    assert q.locator('#moduleUnavailableDialog').is_visible()
    assert not q.locator('#forexChecklistDialog').is_visible()
    q.locator('[data-availability-stay]').click()
    assert q.evaluate('JSON.stringify(S)')==before
    passed.append('Settings Forex launchers denied before period/checklist mounting and financial effects')
    q.evaluate("settingsNavigate('tool-params',{push:true,focus:true});document.querySelectorAll('#forexEnginePanel details').forEach(n=>n.open=true)")
    form=q.locator('#fxMarketFacts');field=form.locator('[name="atrShort"]')
    assert field.evaluate("el=>!!el.closest('[inert]')")
    q.evaluate("document.querySelector('#fxMarketFacts').addEventListener('submit',()=>window.__reached=true)")
    form.dispatch_event('submit')
    assert q.evaluate('window.__reached===undefined')
    assert q.evaluate('JSON.stringify(S)')==before
    q.locator('#paramsWidgetGrid [data-module-work-notice] button').first.click()
    field.fill('0.01234')
    q.evaluate("window.__fxField=document.querySelector('#fxMarketFacts [name=atrShort]')")
    assert q.evaluate("JPWModuleWork.hasPending('forex')")
    raw=q.evaluate('localStorage.getItem("'+KEY+'")')
    q.evaluate("JPWModuleAvailabilityUI.requestChange('forex','frozen')")
    assert q.evaluate('localStorage.getItem("'+KEY+'")')==raw
    remote=ctx.new_page();remote.goto(url.rsplit('/',1)[0]+'/build-id.js')
    remote.evaluate("key=>localStorage.setItem(key,JSON.stringify({schemaVersion:1,modules:{forex:'frozen'}}))",KEY)
    q.wait_for_function("JPWModuleWork.isSuspended('forex')")
    assert field.input_value()=='0.01234'
    assert field.evaluate('el=>el===window.__fxField')
    assert field.evaluate("el=>!!el.closest('[inert]')")
    assert '0.01234' in q.evaluate('JSON.stringify(jpwWorkspaceDrafts())')
    assert 'outra aba' in q.locator('#paramsWidgetGrid [data-module-work-notice]').inner_text()
    q.locator('#paramsWidgetGrid [data-module-work-notice] button').first.click()
    assert not field.evaluate("el=>!!el.closest('[inert]')")
    assert field.input_value()=='0.01234'
    assert q.evaluate('JSON.stringify(S)')==before
    assert not errors,errors
    passed.append('Forex grid in Settings: dirty refusal, remote inert, retained node/value/backup and explicit resume')
    ctx.close()
    ctx,q,errors=boot(browser,url)
    q.evaluate("openSettingsModal('parameters')")
    q.locator('#settingsReviewPeriodBtn').click()
    q.locator('#obOperador').fill('SYNTHETIC pending operator')
    q.evaluate("window.__legacyField=document.querySelector('#obOperador')")
    assert q.evaluate("JPWModuleWork.hasPending('forex')")
    before=q.evaluate('JSON.stringify(S)')
    remote=ctx.new_page();remote.goto(url.rsplit('/',1)[0]+'/build-id.js')
    remote.evaluate("key=>localStorage.setItem(key,JSON.stringify({schemaVersion:1,modules:{forex:'frozen'}}))",KEY)
    q.wait_for_function("JPWModuleWork.isSuspended('forex')")
    field=q.locator('#obOperador')
    assert field.input_value()=='SYNTHETIC pending operator'
    assert field.evaluate('el=>el===window.__legacyField')
    assert field.evaluate("el=>!!el.closest('[inert]')")
    assert 'SYNTHETIC pending operator' in q.evaluate('JSON.stringify(jpwWorkspaceDrafts())')
    q.locator('#obStepNext').dispatch_event('click')
    assert q.evaluate('JSON.stringify(S)')==before
    q.locator('#modalOverlay [data-module-work-notice] button').first.click()
    assert field.input_value()=='SYNTHETIC pending operator'
    assert not field.evaluate("el=>!!el.closest('[inert]')")
    assert not errors,errors
    passed.append('Legacy period modal retained and suspended on remote freeze without new actions')
    ctx.close()

def frozen_exploration(browser,url,passed):
    """AV-NAV-FROZEN: freezing a group removes same-route exploration too.

    Omitting the shell's availability recheck leaves a real, clickable submenu
    exposed. No route change may be used to make that stale projection vanish.
    """
    cases=[('personal-finance','finpes','expanded','pin',False),
           ('personal-finance','finpes','collapsed','pin',False),
           ('personal-finance','finpes','expanded','hover',False),
           ('personal-finance','finpes','expanded','hover',True),
           ('research','research','expanded','pin',False),
           ('forex','exec','expanded','pin',False)]
    for module,surface,rail,gesture,valid_pin in cases:
      ctx,q,errors=boot(browser,url)
      try:
        q.evaluate("id=>JPWModuleAvailability.setState(id,'active')",module)
        q.evaluate("rail=>{localStorage.setItem('jpw_rail',rail);applyRailState();}",rail)
        if valid_pin:q.locator('#toolsNavTrigger').click()
        trigger=q.locator('#'+surface+'NavTrigger')
        panel=q.locator('#'+surface+'NavSubmenu')
        if gesture=='pin':trigger.focus();q.keyboard.press('ArrowRight')
        else:
          q.locator('#brandHomeBtn').focus()
          trigger.hover()
        q.wait_for_function("id=>document.getElementById(id).getAttribute('aria-hidden')==='false'",arg=surface+'NavSubmenu')
        assert panel.is_visible()
        before=q.evaluate("JSON.stringify({state:S,route:JPWNavigation.current(),storage:Object.entries(localStorage).filter(([k])=>k!=='jpw_module_availability_v1').sort()})")
        q.evaluate("window.__frozenNavNodes=[...document.querySelectorAll('#nav > .tab,.nav-sub-menu')]")
        remote=ctx.new_page();remote.goto(urljoin(url,'/build-id.js'))
        def remote_state(state):
            remote.evaluate("([key,id,state])=>{const raw=JSON.parse(localStorage.getItem(key))||{schemaVersion:1,modules:{}};raw.modules[id]=state;localStorage.setItem(key,JSON.stringify(raw));}",[KEY,module,state])
            q.wait_for_function("([id,state])=>JPWModuleAvailability.getState(id)===state",arg=[module,state])
        remote_state('frozen')
        assert not trigger.is_visible()
        assert not panel.is_visible(), 'AV-NAV-FROZEN: frozen exploration remains visible'
        assert panel.evaluate("e=>e.inert&&e.getAttribute('aria-hidden')==='true'")
        assert q.evaluate("!!document.activeElement?.getClientRects().length&&!document.activeElement.closest('[hidden],[inert]')&&document.activeElement!==document.body"), 'AV-NAV-FROZEN: focus stranded in hidden navigation'
        if gesture=='pin':assert q.evaluate('document.activeElement.id')=='brandHomeBtn' or q.evaluate('document.activeElement.dataset.primary')=='dashboard'
        if valid_pin:
            assert q.locator('#toolsNavSubmenu').is_visible(), 'Available pinned group was discarded'
        q.wait_for_timeout(500)  # Both existing dwell and close deadlines have elapsed.
        assert not panel.is_visible(), 'AV-NAV-FROZEN: delayed callback reopened frozen group'
        remote_state('active')
        assert not panel.is_visible(), 'AV-NAV-FROZEN: thaw replayed stale exploration'
        assert q.evaluate("JSON.stringify({state:S,route:JPWNavigation.current(),storage:Object.entries(localStorage).filter(([k])=>k!=='jpw_module_availability_v1').sort()})")==before
        assert q.evaluate("__frozenNavNodes.every(e=>e.isConnected&&(!e.id||document.getElementById(e.id)===e))")
        trigger.focus();q.keyboard.press('ArrowRight')
        assert panel.is_visible(), 'Explicit exploration after thaw must still work'
        assert not errors,errors
        passed.append(f'AV-NAV-FROZEN {module}/{rail}/{gesture}/valid-pin={valid_pin}: same route, hide/inert/focus/no replay/no financial write')
      finally:ctx.close()

def main():
    ART.mkdir(parents=True,exist_ok=True);server,url=serve(ROOT);passed=[]
    try:
      with sync_playwright() as p:
        browser=launch_browser(p)
        for layout in ['sidebar','topbar','glass','submenu']:
          for width in [1440,390]:
            for theme in ['light','dark']:
              ctx,q,errors=boot(browser,url,layout,width,theme)
              q.evaluate('window.__beforeState=JSON.stringify(S);window.__orderRaw=localStorage.getItem("jpw_nav_order");window.__navNodes=[...document.querySelectorAll("#nav > .tab")];')
              assert q.evaluate('localStorage.getItem("'+KEY+'")') is None
              for module in ['alladin','personal-finance']:
                assert q.locator('#nav > [data-primary="'+module+'"]').count()==1
                assert not q.locator('#nav > [data-primary="'+module+'"]').is_visible()
                assert q.locator('[data-dm-card="'+module+'"]').count()==0
                assert q.evaluate('id=>JPWNavigation.navigate(id)',module) is False
                assert q.locator('#moduleUnavailableDialog').is_visible()
                q.locator('[data-availability-manage]').click()
                assert q.locator('#moduleAvailabilityCard').is_visible()
                assert q.locator('[data-module-toggle]').evaluate_all('els=>els.every(el=>el.getBoundingClientRect().height>=44)'), 'Availability actions must retain 44px targets inside Settings'
                assert q.locator('[data-module-row="'+module+'"] p').inner_text().startswith('Congelado')
                q.locator('[data-module-toggle="'+module+'"]').click()
                assert q.evaluate('id=>JPWModuleAvailability.getState(id)',module)=='active'
                assert q.evaluate('JPWNavigation.current().primary')=='dashboard'
                assert q.locator('#nav > [data-primary="'+module+'"]').evaluate('el=>!el.hidden')
                assert q.locator('[data-dm-card="'+module+'"]').count()==1
                assert q.evaluate('JSON.stringify(S)===window.__beforeState')
                assert q.evaluate('localStorage.getItem("jpw_nav_order")===window.__orderRaw')
                q.locator('#settingsCloseBtn').click()
                assert q.evaluate('id=>JPWNavigation.navigate(id)',module) is True
                assert q.evaluate('JPWNavigation.current().primary')==module
                assert q.evaluate('JSON.stringify(S)===window.__beforeState')
                assert q.evaluate("JPWNavigation.navigate('dashboard')") is True
                q.evaluate('id=>JPWModuleAvailabilityUI.manage(id)',module)
                q.locator('[data-module-toggle="'+module+'"]').click()
                assert q.evaluate('id=>JPWModuleAvailability.getState(id)',module)=='frozen'
                assert q.locator('[data-dm-card="'+module+'"]').count()==0
                assert q.evaluate('window.__navNodes.every(n=>[...document.querySelectorAll("#nav > .tab")].includes(n))')
                assert q.locator('[data-module-toggle="'+module+'"]').evaluate('el=>el===document.activeElement')
                assert q.evaluate('JSON.stringify(S)===window.__beforeState')
                if module=='alladin':q.locator('#settingsCloseBtn').click()
              # Clickable close and menu prove overlap/focus beyond screenshots.
              q.locator('#settingsCloseBtn').click()
              assert not q.locator('#settingsOverlay').is_visible()
              if width<900:
                q.locator('[data-shell-menu-toggle]').click()
                assert not q.locator('#nav > [data-primary="alladin"]').is_visible()
                assert not q.locator('#nav > [data-primary="personal-finance"]').is_visible()
                assert q.locator('#nav > [data-primary="research"]').is_visible()
                q.keyboard.press('Escape')
              q.evaluate("JPWModuleAvailabilityUI.manage('alladin')")
              q.locator('[data-module-toggle="alladin"]').scroll_into_view_if_needed()
              q.screenshot(path=str(ART/f'{layout}-{width}-{theme}.png'))
              q.reload();q.wait_for_function('window.JPWModuleAvailabilityUI');wait_bootstrap(q)
              assert q.evaluate("JPWModuleAvailability.getState('alladin')")=='frozen'
              assert q.evaluate("JPWModuleAvailability.getState('personal-finance')")=='frozen'
              assert not errors,errors
              passed.append(f'{layout}/{width}/{theme}: PF+Alladin default/admin/explicit-cycle/no-domain-write/order/focus/reload')
              ctx.close()
        # Real storage event between two pages in the same disposable context.
        for module in ['alladin','personal-finance']:
          ctx,a,errors=boot(browser,url)
          a.evaluate("id=>JPWModuleAvailability.setState(id,'active')",module)
          b=ctx.new_page();b.on('dialog',lambda d:d.accept());b.on('pageerror',lambda e:errors.append(str(e)))
          b.goto(url);b.wait_for_function('window.JPWModuleAvailabilityUI');wait_bootstrap(b)
          assert b.evaluate('id=>JPWModuleAvailability.getState(id)',module)=='active'
          assert b.evaluate('id=>JPWNavigation.navigate(id)',module) is True
          before=b.evaluate('JSON.stringify(S)')
          a.evaluate("id=>JPWModuleAvailabilityUI.requestChange(id,'frozen')",module)
          b.wait_for_function("id=>JPWModuleAvailability.getState(id)==='frozen'",arg=module)
          assert b.evaluate('JPWNavigation.current().primary')=='dashboard'
          assert b.evaluate('id=>JPWNavigation.navigate(id)',module) is False
          b.locator('[data-availability-stay]').click()
          assert b.evaluate('JSON.stringify(S)')==before
          assert not errors,errors
          passed.append(module+': cross-tab freeze before route; safe Dashboard without financial writes')
          ctx.close()
        passed.extend(notification_and_suspended_work(browser,url))
        settings_forex_boundaries(browser,url,passed)
        frozen_exploration(browser,url,passed)
        browser.close()
      (ART/'results.json').write_text(json.dumps({'result':'PASS','cases':passed},indent=2))
      print('module_availability_test PASS',len(passed),'contexts')
    finally:server.shutdown();server.server_close()
if __name__=='__main__':main()

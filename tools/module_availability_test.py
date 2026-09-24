#!/usr/bin/env python3
"""Approved module availability: actual UI, isolated synthetic origins, no user data."""
import json
from pathlib import Path
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
        q.evaluate("JPWModuleAvailability.setState('forex','frozen');JPWNotifications.refresh();JPWNotifications.open()")
        before=q.evaluate('JSON.stringify({state:S,selection:JPWForex.state.operationalSelection(),storage:Object.entries(localStorage).sort()})')
        action=q.locator('[data-notification-go="'+REVIEW_CONTEXTS[0]['notification_id']+'"]')
        row=q.locator('[data-notification-id="'+REVIEW_CONTEXTS[0]['notification_id']+'"]')
        unread=row.get_attribute('data-unread')
        action.click()
        assert q.locator('#moduleUnavailableDialog').evaluate('el=>el.open')
        assert q.locator('#notificationCenter').evaluate('el=>el.open')
        assert row.get_attribute('data-unread')==unread
        assert q.evaluate('JSON.stringify({state:S,selection:JPWForex.state.operationalSelection(),storage:Object.entries(localStorage).sort()})')==before
        q.locator('[data-availability-stay]').click()
        assert q.locator('#notificationCenter').evaluate('el=>el.open')
        q.wait_for_function('id=>document.activeElement.dataset.notificationGo===id',arg=REVIEW_CONTEXTS[0]['notification_id'])
        passed.append('scoped Forex notification: frozen before account/period/read/close; stay restores focus')

        action.click();q.locator('[data-availability-manage]').click()
        assert not q.locator('#notificationCenter').evaluate('el=>el.open')
        assert not q.locator('#moduleUnavailableDialog').evaluate('el=>el.open')
        assert q.locator('#moduleAvailabilityCard').is_visible()
        q.locator('[data-module-toggle="forex"]').click(trial=True)
        q.locator('#settingsCloseBtn').click()
        q.evaluate('JPWNotifications.open()')
        q.locator('[data-notification-go="'+REVIEW_CONTEXTS[0]['notification_id']+'"]').click()
        q.locator('[data-availability-dashboard]').click()
        assert not q.locator('#notificationCenter').evaluate('el=>el.open')
        assert q.evaluate('JPWNavigation.current().primary')=='dashboard'
        q.wait_for_function("document.getElementById('dash').contains(document.activeElement)")
        assert q.evaluate('JSON.stringify({state:S,selection:JPWForex.state.operationalSelection(),storage:Object.entries(localStorage).sort()})')==before
        assert not errors,errors
        passed.append('denial explicit manage/home: no residual modal blocks Settings or content focus')
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
              assert q.locator('#nav > [data-primary="alladin"]').count()==1
              assert not q.locator('#nav > [data-primary="alladin"]').is_visible()
              assert q.evaluate('localStorage.getItem("'+KEY+'")') is None
              assert q.evaluate("JPWNavigation.navigate('alladin')") is False
              assert q.locator('#moduleUnavailableDialog').is_visible()
              q.locator('[data-availability-manage]').click()
              assert q.locator('#moduleAvailabilityCard').is_visible()
              assert q.locator('[data-module-toggle]').evaluate_all('els=>els.every(el=>el.getBoundingClientRect().height>=44)'), 'Availability actions must retain 44px targets inside Settings'
              assert q.locator('[data-module-row="alladin"] p').inner_text().startswith('Congelado')
              q.locator('[data-module-toggle="alladin"]').click()
              assert q.evaluate("JPWModuleAvailability.getState('alladin')")=='active'
              assert q.evaluate('JPWNavigation.current().primary')=='dashboard'
              assert q.evaluate('JSON.stringify(S)===window.__beforeState')
              assert q.evaluate('localStorage.getItem("jpw_nav_order")===window.__orderRaw')
              q.locator('[data-module-toggle="alladin"]').click()
              assert q.evaluate("JPWModuleAvailability.getState('alladin')")=='frozen'
              assert q.evaluate('window.__navNodes.every(n=>[...document.querySelectorAll("#nav > .tab")].includes(n))')
              assert q.locator('[data-module-toggle="alladin"]').evaluate('el=>el===document.activeElement')
              assert q.evaluate('JSON.stringify(S)===window.__beforeState')
              # Clickable close and menu prove overlap/focus beyond screenshots.
              q.locator('#settingsCloseBtn').click()
              assert not q.locator('#settingsOverlay').is_visible()
              if width<900:
                q.locator('[data-shell-menu-toggle]').click()
                assert not q.locator('#nav > [data-primary="alladin"]').is_visible()
                assert q.locator('#nav > [data-primary="research"]').is_visible()
                q.keyboard.press('Escape')
              q.evaluate("JPWModuleAvailabilityUI.manage('alladin')")
              q.locator('[data-module-toggle="alladin"]').scroll_into_view_if_needed()
              q.screenshot(path=str(ART/f'{layout}-{width}-{theme}.png'))
              q.reload();q.wait_for_function('window.JPWModuleAvailabilityUI');wait_bootstrap(q)
              assert q.evaluate("JPWModuleAvailability.getState('alladin')")=='frozen'
              assert not errors,errors
              passed.append(f'{layout}/{width}/{theme}: default/admin/explicit-cycle/no-domain-write/order/focus/reload')
              ctx.close()
        # Real storage event between two pages in the same disposable context.
        ctx,a,errors=boot(browser,url)
        a.evaluate("JPWModuleAvailability.setState('alladin','active')")
        b=ctx.new_page();b.on('dialog',lambda d:d.accept());b.goto(url);b.wait_for_function('window.JPWModuleAvailabilityUI');wait_bootstrap(b)
        assert b.evaluate("JPWModuleAvailability.getState('alladin')")=='active'
        b.evaluate("JPWNavigation.navigate('alladin')")
        a.evaluate("JPWModuleAvailabilityUI.requestChange('alladin','frozen')")
        b.wait_for_function("JPWModuleAvailability.getState('alladin')==='frozen'")
        assert b.evaluate('JPWNavigation.current().primary')=='dashboard'
        assert b.evaluate("JPWNavigation.navigate('alladin')") is False
        b.locator('[data-availability-stay]').click()
        passed.append('cross-tab: frozen before route; safe Dashboard when no work')
        ctx.close()
        passed.extend(notification_and_suspended_work(browser,url))
        settings_forex_boundaries(browser,url,passed)
        browser.close()
      (ART/'results.json').write_text(json.dumps({'result':'PASS','cases':passed},indent=2))
      print('module_availability_test PASS',len(passed),'contexts')
    finally:server.shutdown();server.server_close()
if __name__=='__main__':main()

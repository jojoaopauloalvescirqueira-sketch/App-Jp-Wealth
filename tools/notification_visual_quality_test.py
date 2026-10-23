"""Additive notification cases for the existing visual verifier; synthetic only."""
import json
import math
from pathlib import Path
import shutil
import tempfile

from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options
import notification_center_test as notifications

LAYOUTS = ('sidebar','topbar','glass','submenu')
THEMES = ('light','dark')
SIZES = ((320,700),(390,844),(1440,900),(1440,480))


def required_ids():
    return ([f'notification-{layout}-{theme}-{width}x{height}' for width,height in SIZES
             for layout in LAYOUTS for theme in THEMES]
            + [f'notification-native200-{layout}-{theme}' for layout in LAYOUTS for theme in THEMES]
            + ['notification-counterproof-inner-svg','notification-counterproof-overflow','notification-long-context-wrap','notification-counterproof-scroll-contents'])


def open_center(page):
    if not page.locator('#notificationCenter').evaluate('e=>e.open') and not page.locator('#headerNotificationsBtn').is_visible():
        toggle=page.locator('[data-shell-menu-toggle]').first
        assert toggle.is_visible(), 'No visible route to the notification bell'
        toggle.click()
    notifications.open_center(page)


def geometry(page, visual):
    data=page.locator('#notificationCenter').evaluate('''e=>{const b=e.getBoundingClientRect();return {x:b.x,y:b.y,right:b.right,bottom:b.bottom,width:b.width,height:b.height,viewport:[innerWidth,innerHeight],client:e.clientWidth,scroll:e.scrollWidth,bodyScroll:document.documentElement.scrollWidth}}''')
    assert data['x']>=12 and data['y']>=12, ('notification gutter',data)
    assert data['right']<=data['viewport'][0]-12 and data['bottom']<=data['viewport'][1]-12, ('notification outside viewport',data)
    assert data['scroll']<=data['client']+1, ('notification horizontal overflow',data)
    contents=page.locator('.notification-scroll').evaluate('e=>({client:e.clientWidth,scroll:e.scrollWidth})')
    assert contents['scroll']<=contents['client']+1, ('notification contents overflow',contents)
    assert page.locator('#notificationReadAll,[data-notification-read]').count()==0
    close=visual.centered(page.locator('#notificationClose'),'ink',True)
    action=page.locator('#notificationList [data-notification-go]').first
    assert action.count()==1, 'populated notification scenario required'
    action.scroll_into_view_if_needed()
    action_geometry=visual.centered(action)
    assert action_geometry['outer']['height']>=44, action_geometry
    rows=notifications.rows(page)
    assert rows.count()>0, 'nonempty actionable population required'
    for row in rows.all():
        assert row.locator('.notification-body').inner_text().count('\n')<=1, 'summary must remain succinct'
    return {'dialog':data,'close':close,'action':action_geometry,'count':rows.count()}


def scenario(page, visual, *, capture=None):
    notifications.seed_areas(page)
    open_center(page)
    notifications.instrument(page)
    before=notifications.snapshot(page)
    result=geometry(page,visual)
    summary=page.locator('#notificationList details summary').first
    summary.scroll_into_view_if_needed();summary.click()
    assert summary.locator('..').evaluate('e=>e.open'), 'diagnostic expansion unavailable'
    notifications.refresh(page)
    assert summary.locator('..').evaluate('e=>e.open'), 'refresh collapsed diagnostics'
    assert page.evaluate('document.activeElement.tagName')=='SUMMARY', 'refresh lost focus'
    notifications.unchanged(page,before)
    if capture:
        page.screenshot(path=str(capture),full_page=False)
    return result


def matrix(browser,url,report,visual):
    for width,height in SIZES:
        for layout in LAYOUTS:
            for theme in THEMES:
                context,page,_=notifications.prepare(browser,url,{'width':width,'height':height},theme,personal_finance_active=True)
                page._visual_errors=page.notification_errors
                try:
                    page.evaluate('x=>mountNavigationLayout(x)',layout)
                    page.emulate_media(reduced_motion='reduce')
                    capture=Path(report['out'])/f'notifications-{width}-{theme}.png' if layout=='sidebar' and width in (390,1440) and height!=480 else None
                    visual.record(report,f'notification-{layout}-{theme}-{width}x{height}',lambda:scenario(page,visual,capture=capture),page,
                                  criteria='active-actions/SVGinnercenter<=2CSSpx/44px/nooverflow/stablefocus/no-write',layout=layout,theme=theme,viewport=[width,height])
                    assert_fixture_requests(context)
                finally:
                    context.close()
    for name,mutation in [('inner-svg',"document.querySelector('#notificationClose svg').style.transform='translateX(5px)'"),
                          ('overflow',"document.getElementById('notificationCenter').style.maxWidth='none';document.getElementById('notificationCenter').style.width='200vw'")]:
        context,page,_=notifications.prepare(browser,url)
        page._visual_errors=page.notification_errors
        try:
            notifications.seed_areas(page);open_center(page)
            geometry(page,visual)
            page.evaluate(mutation)
            def reject():
                rejected=False
                try:geometry(page,visual)
                except AssertionError:rejected=True
                assert rejected, 'same visual oracle accepted deliberate '+name
                return {'deliberate_violation_rejected':name}
            visual.record(report,'notification-counterproof-'+name,reject,page,criteria='same-geometry-oracle rejects representative violation')
        finally:
            context.close()



    context,page,_=notifications.prepare(browser,url,{'width':320,'height':700})
    page._visual_errors=page.notification_errors
    try:
        notifications.seed_areas(page)
        page.evaluate("S.accounts.find(a=>a.forexAccountId==='SYN_NOTIFY_A').nome='A'.repeat(100);JPWNotifications.refresh()")
        open_center(page)
        visual.record(report,'notification-long-context-wrap',lambda:geometry(page,visual),page,criteria='valid long account name wraps inside scroll container at320')
        page.locator('.notification-meta').first.evaluate("e=>e.style.whiteSpace='nowrap'")
        def reject_contents():
            rejected=False
            try:geometry(page,visual)
            except AssertionError:rejected=True
            assert rejected, 'inner scroll overflow was hidden by the outer dialog bounds'
            return {'inner_overflow_rejected':True}
        visual.record(report,'notification-counterproof-scroll-contents',reject_contents,page,criteria='same oracle rejects overflow inside fixed width dialog')
    finally:
        context.close()


def native_zoom(pw,url,report,visual):
    profile=Path(tempfile.mkdtemp(prefix='notifications-native200-',dir=report['out']))
    (profile/'Default').mkdir()
    (profile/'Default/Preferences').write_text(json.dumps({'partition':{'default_zoom_level':{'x':math.log(2)/math.log(1.2)}}}))
    options=launch_options();options.update(headless=False,no_viewport=True,args=['--window-size=1440,1000'],service_workers='block',reduced_motion='reduce')
    try:
        context=pw.chromium.launch_persistent_context(str(profile),**options)
        try:
            install_bootstrap(context);context.add_init_script('window.__onbShown=true;')
            page=context.new_page();page.clock.set_fixed_time(notifications.NOW)
            page._visual_errors=[];page.on('pageerror',lambda error:page._visual_errors.append(str(error)))
            page.goto(url,wait_until='load');wait_bootstrap(page);page.evaluate('closeModal()')
            page.evaluate("JPWModuleAvailability.setState('personal-finance','active')")
            zoom=page.evaluate('({outer:outerWidth,inner:innerWidth,css:getComputedStyle(document.documentElement).zoom})')
            assert abs(zoom['outer']/zoom['inner']-2)<.01 and zoom['css']=='1', ('native200 not CSS zoom',zoom)
            notifications.seed_areas(page)
            for layout in LAYOUTS:
                for theme in THEMES:
                    if page.locator('#notificationCenter').evaluate('e=>e.open'):page.locator('#notificationClose').click()
                    page.evaluate('x=>mountNavigationLayout(x)',layout)
                    page.evaluate('t=>{document.documentElement.dataset.theme=t;document.body.dataset.theme=t}',theme)
                    open_center(page)
                    visual.record(report,f'notification-native200-{layout}-{theme}',lambda:geometry(page,visual),page,
                                  criteria='native200/SVGink<=2CSSpx/44px/viewport-nooverflow',layout=layout,theme=theme,native_zoom=200,zoom=zoom)
            assert_fixture_requests(context)
        finally:
            context.close()
    finally:
        shutil.rmtree(profile)

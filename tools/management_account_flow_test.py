#!/usr/bin/env python3
"""Shared real account dialogs keep their captured Management/Forex ownership."""
import json
from playwright.sync_api import sync_playwright
from research_navigation_test import serve, launch_browser, boot


def selection(page):
    return page.evaluate("(()=>{const x=JPWForex.state.operationalSelection();return {accountId:x.accountId,periodId:x.periodId,reason:x.reason,requiresSelection:x.requiresSelection}})()")


def wizard_save(page, suffix):
    page.locator('#fxcwNext').click()
    page.locator('#fxcr-name').fill('Synthetic Management '+suffix)
    page.locator('#fxcr-type').select_option('MESTRE')
    page.locator('#fxcr-login').fill('MG-'+suffix)
    page.locator('#fxcwNext').click()
    page.locator('#fxcr-platform').select_option('MetaTrader 5')
    page.locator('#fxcr-currency').fill('USD')
    page.locator('#fxcwNext').click()
    page.locator('#fxcr-profileKey').select_option('base')
    page.locator('#fxcwNext').click()
    page.locator('#fxcRegistrationSave').click()


def prepare_period(page, start='2026-01-01'):
    assert page.locator('#fxcs-active').is_disabled()
    assert not page.locator('#fxcs-active').is_checked()
    page.locator('#fxcs-period').select_option('')
    assert page.locator('#fxcs-active').is_disabled()
    page.locator('#fxcs-start').fill(start)
    page.locator('#fxcs-si').fill('1000')
    page.locator('#fxcs-book').fill('1000')
    page.locator('#fxcs-confirm-period').check()
    page.locator('#fxcs-save-period').click()
    page.wait_for_function("document.getElementById('fxcSetupStatus').textContent.includes('Período salvo')")


def run():
    server, url = serve()
    try:
        with sync_playwright() as p:
            browser = launch_browser(p)
            context, page, errors = boot(browser, url, {'width':1440,'height':1000})
            try:
                page.evaluate("JPWModuleAvailability.setState('forex','frozen');JPWNavigation.navigate('management-accounting')")
                page.evaluate("""()=>{window.__accountDialogOwners=[];const show=HTMLDialogElement.prototype.showModal;HTMLDialogElement.prototype.showModal=function(...args){__accountDialogOwners.push({id:this.id,owner:this.dataset.moduleWorkOwner||null});return show.apply(this,args)};}""")
                before=page.evaluate('JSON.stringify(S)');operational=selection(page)
                page.locator('#management [data-mg-action=account-new]').click()
                registration=page.locator('#fxcRegistrationDialog')
                assert registration.is_visible(), 'Management must open cadastro while Forex is frozen'
                assert registration.get_attribute('data-module-work-owner')=='management'
                assert page.evaluate('__accountDialogOwners.at(-1).owner')=='management', 'Ownership must be captured before showModal'
                page.evaluate("JPWModuleWork.suspend('forex','Synthetic refresh after Forex freeze')")
                assert registration.get_attribute('data-module-work-owner')=='management'
                assert registration.locator('[data-module-work-notice]').count()==0
                assert page.locator('#fxcwWork').evaluate('e=>!e.closest("[inert]")')
                page.locator('#fxcRegistrationCancel').click()
                assert page.evaluate('JSON.stringify(S)')==before
                assert selection(page)==operational
                # The Management callback refreshes its empty selector, without choosing the new account.
                page.locator('#management [data-mg-action=account-new]').click();wizard_save(page,'PUBLIC')
                page.wait_for_function('S.accounts.length===1&&!document.getElementById("fxcRegistrationDialog").open')
                account=page.evaluate('S.accounts[0].forexAccountId')
                assert page.locator('#management [data-mg-account] option').count()==2
                assert page.locator('#management [data-mg-account]').input_value()==''
                assert selection(page)==operational
                page.locator('#management [data-mg-account]').select_option(account)
                page.locator('#management [data-mg-action=account-setup]').click()
                setup=page.locator('#fxcSetupDialog')
                assert setup.is_visible() and setup.get_attribute('data-module-work-owner')=='management'
                assert page.evaluate('__accountDialogOwners.at(-1).owner')=='management'
                prepare_period(page)
                assert page.locator('#management [data-mg-period] option').count()==2, 'Confirmed period callback must refresh Management choices'
                assert page.locator('#management [data-mg-period]').input_value()==''
                assert selection(page)==operational
                page.locator('#fxcs-open-orders').click()
                assert not setup.is_visible()
                assert page.evaluate('JPWNavigation.current().primary')=='management'
                assert selection(page)==operational
                # Registration's own success action forwards the same captured owner.
                page.evaluate("JPWFXConsolidatedUI.openAccountRegistration({owner:'management'})")
                wizard_save(page,'PREPARE')
                page.locator('#fxcwPrepare').wait_for(state='visible')
                page.locator('#fxcwPrepare').click()
                assert setup.is_visible() and setup.get_attribute('data-module-work-owner')=='management'
                assert page.locator('#fxcs-active').is_disabled() and not page.locator('#fxcs-active').is_checked()
                page.locator('#fxcs-close').click()
                # A setup whose cadastro is missing reuses Registration, then returns to the same owner.
                page.evaluate("window.__managementSaved=0;JPWFXConsolidatedUI.openAccountSetup({owner:'management',onSaved:()=>{__managementSaved++}})")
                assert registration.is_visible() and registration.get_attribute('data-module-work-owner')=='management'
                wizard_save(page,'CHAIN')
                setup.wait_for(state='visible');assert setup.get_attribute('data-module-work-owner')=='management'
                prepare_period(page,'2026-02-01')
                assert page.evaluate('__managementSaved')==1
                assert selection(page)==operational
                page.locator('#fxcs-open-orders').click()
                # Freezing the captured owner suspends the real live form, even if Forex is active.
                page.evaluate("JPWModuleAvailability.setState('forex','active');JPWFXConsolidatedUI.openAccountRegistration({owner:'management'})")
                page.locator('#fxcwNext').click();page.locator('#fxcr-name').fill('Preserved when owner freezes')
                frozen_before=page.evaluate('JSON.stringify(S)')
                page.evaluate("JPWModuleAvailability.setState('management','frozen');JPWModuleWork.suspend('management','Synthetic owner freeze')")
                assert registration.get_attribute('data-module-work-owner')=='management'
                assert registration.locator('[data-module-work-notice]').count()==1
                assert page.locator('#fxcwWork').evaluate('e=>!!e.closest("[inert]")')
                assert page.evaluate('JSON.stringify(S)')==frozen_before
                page.evaluate("JPWModuleAvailability.setState('management','active');JPWModuleWork.resume('management')")
                assert page.locator('#fxcr-name').input_value()=='Preserved when owner freezes'
                page.locator('#fxcwClose').click();page.locator('#fxcwDiscardConfirm').click()
                page.evaluate("JPWModuleAvailability.setState('management','frozen');JPWNavigation.navigate('forex-management-accounts')")
                page.evaluate('(accountId)=>JPWFXConsolidatedUI.openAccountSetup({accountId})',account)
                assert setup.is_visible() and setup.get_attribute('data-module-work-owner')=='forex'
                page.locator('#fxcs-period').select_option('')
                assert page.locator('#fxcs-active').is_enabled() and page.locator('#fxcs-active').is_checked(), 'Legacy Forex default must remain active'
                page.once('dialog',lambda dialog:dialog.accept())
                page.locator('#fxcs-close').click()
                assert not errors['pageerror'],errors
                print(json.dumps({'status':'PASS','cases':['Management cadastro with Forex frozen','owner before showModal','real refresh preserves captured owner','cancel no facts','cadastro callback refresh without autoselection','period callback refresh','setup-registration owner chain','operational selection preserved','captured owner freeze preserves draft']}))
            finally:context.close()
            context,page,errors=boot(browser,url,{'width':1440,'height':1000})
            try:
                page.evaluate("JPWModuleAvailability.setState('management','frozen');JPWNavigation.navigate('forex-management-accounts');JPWFXConsolidatedUI.openAccountRegistration()")
                assert page.locator('#fxcRegistrationDialog').is_visible()
                assert page.locator('#fxcRegistrationDialog').get_attribute('data-module-work-owner')=='forex'
                page.locator('#fxcRegistrationCancel').click()
                # Reusing a caller-supplied string outside accepted Management cannot bypass Forex's freeze.
                page.evaluate("JPWModuleAvailability.setState('management','active');JPWNavigation.navigate('dashboard');JPWModuleAvailability.setState('forex','frozen')")
                assert page.evaluate("JPWFXConsolidatedUI.openAccountRegistration({owner:'management'})") is False
                assert not page.locator('#fxcRegistrationDialog').is_visible()
                assert not errors['pageerror'],errors
                print(json.dumps({'status':'PASS','cases':['legacy Forex default owner','frozen Management does not block Forex flow','outside-route owner does not bypass frozen Forex']}))
            finally:context.close();browser.close()
    finally:server.shutdown()


if __name__=='__main__':run()

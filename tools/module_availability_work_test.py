#!/usr/bin/env python3
"""Module suspension: real synthetic forms, cross-tab storage and draft recovery."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from dashboard_macro_test import launch_browser
from dashboard_forex_relocation_test import serve
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap

ROOT=Path(__file__).resolve().parents[1]
KEY='jpw_module_availability_v1'

def main():
    server,url=serve(ROOT)
    try:
      with sync_playwright() as p:
        browser=launch_browser(p)
        context=browser.new_context(service_workers='block')
        install_bootstrap(context)
        context.add_init_script("window.__onbShown=true;")
        page=context.new_page();errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('dialog',lambda dialog:dialog.accept())
        page.goto(url);page.wait_for_function('window.JPWModuleWork && window.JPWModuleAvailabilityUI')
        wait_bootstrap(page);page.evaluate('closeModal()')
        remote=context.new_page();remote.goto(url.rsplit('/',1)[0]+'/build-id.js')
        def freeze(module):
            remote.evaluate("([key,id])=>{const raw=JSON.parse(localStorage.getItem(key)||'{\"schemaVersion\":1,\"modules\":{}}');raw.modules[id]='frozen';localStorage.setItem(key,JSON.stringify(raw));}",[KEY,module])
            page.wait_for_function("id=>JPWModuleWork.isSuspended(id)",arg=module)
        def activate(module):
            page.evaluate("id=>JPWModuleAvailability.setState(id,'active')",module)
            page.wait_for_function("id=>!JPWModuleWork.isSuspended(id)",arg=module)
        def before():
            return page.evaluate('JSON.stringify(S)')
        def unchanged(value):
            assert before()==value,'Availability changed financial state'

        # Default does not mount Alladin, while its shared read helpers remain.
        assert page.evaluate("JPWAlladinUI.selectView('accounts')") is False
        assert page.locator('#alladinAccounts').inner_html()==''
        assert page.evaluate("typeof alladinCatalogoLabels==='function' && typeof JPWAlladin.leitura.accounts==='function'")
        print('PASS frozen default: no operational mount; shared readers preserved',flush=True)

        activate('alladin');page.evaluate("JPWNavigation.navigate('alladin');JPWAlladinUI.selectView('accounts')")
        page.locator('[data-ald-new="account"]').click()
        page.locator('#alladinFldName').fill('Synthetic unsaved account')
        assert page.evaluate("JPWModuleWork.hasPending('alladin')")
        raw=page.evaluate('localStorage.getItem('+json.dumps(KEY)+')')
        page.evaluate("JPWModuleAvailabilityUI.requestChange('alladin','frozen')")
        assert page.evaluate('localStorage.getItem('+json.dumps(KEY)+')')==raw
        value=before();freeze('alladin');unchanged(value)
        assert page.locator('#alladinFldName').input_value()=='Synthetic unsaved account'
        assert page.locator('#alladinModalOverlay').is_visible()
        assert page.locator('#alladinFldName').evaluate("el=>!!el.closest('[inert]')")
        assert page.evaluate("!!document.activeElement.closest('[data-module-work-notice]')")
        assert 'Synthetic unsaved account' in page.evaluate('JSON.stringify(jpwWorkspaceDrafts())')
        page.evaluate('alladinSubmit();alladinModalDismiss()');unchanged(value)
        assert page.locator('#alladinModalOverlay').is_visible()
        page.locator('#alladinModalOverlay [data-module-work-notice] button').first.click()
        assert page.evaluate("JPWModuleAvailability.canAccess('alladin')")
        assert not page.locator('#alladinFldName').evaluate("el=>!!el.closest('[inert]')")
        assert page.locator('#alladinFldName').input_value()=='Synthetic unsaved account'
        assert page.evaluate("document.activeElement.id")=='alladinFldName'
        page.locator('[data-ald-act="cancelar"]').click()
        assert not page.evaluate("JPWModuleWork.hasPending('alladin')")
        print('PASS Alladin draft: local refusal, remote retention, backup and explicit resume',flush=True)

        # A record already committed with warning must still reach its decision.
        page.evaluate("""()=>{const a=JPWAlladin.cadastro.addAccount({name:'Synthetic',institution:'Fixture',accountType:'BANK'});JPWAlladin.cadastro.addCashAccount({accountId:a.recordId,currency:'BRL'});JPWAlladinUI.selectView('cashAccounts');}""")
        page.locator('[data-ald-new="cashaccount"]').click()
        page.locator('#alladinFldCurrency').fill('BRL')
        page.locator('[data-ald-act="salvar"]').click()
        assert page.evaluate("JPWAlladinUI.workState().state")=='COMMITTED_WARNING'
        count=page.evaluate('S.alladin.cashAccounts.length');freeze('alladin')
        page.locator('[data-ald-act="manter"]').click()
        assert page.evaluate('S.alladin.cashAccounts.length')==count
        assert not page.locator('#alladinModalOverlay').is_visible()
        assert page.evaluate("!!document.activeElement.closest('#moduleAvailabilitySuspended') || document.activeElement.id==='headerConfigBtn'")
        assert page.evaluate("JPWModuleAvailability.getState('alladin')")=='frozen'
        print('PASS committed Alladin warning remains resolvable after remote freeze',flush=True)

        page.evaluate("JPWNavigation.navigate('nocoda')")
        page.locator('#ncPrice1').fill('1.23456')
        assert page.evaluate("JPWModuleWork.hasPending('research')")
        value=before();freeze('research');unchanged(value)
        assert page.locator('#ncPrice1').input_value()=='1.23456'
        assert page.evaluate('ncSaveStudy()') is False
        unchanged(value)
        assert '1.23456' in page.evaluate('JSON.stringify(jpwWorkspaceDrafts())')
        activate('research')
        assert page.locator('#ncPrice1').input_value()=='1.23456'
        page.evaluate('ncDirty=false')  # Synthetic draft deliberately resolved for next scenario.
        print('PASS Research draft and guarded save preserved without financial writes',flush=True)

        # PF atomic modal stays in RAM and is guarded before its financial command.
        page.evaluate("JPWNavigation.navigate('personal-finance');JPWNavigation.navigateLocal('finpes','cenarios');fsOpenScenarioModal(null)")
        field=page.locator('#modalBox [data-qid="name"] input');field.fill('Synthetic pending scenario')
        assert page.evaluate("JPWModuleWork.hasPending('personal-finance')")
        value=before();freeze('personal-finance');unchanged(value)
        page.locator('#modalConfirm').dispatch_event('click');unchanged(value)
        assert field.input_value()=='Synthetic pending scenario'
        assert 'Synthetic pending scenario' in page.evaluate('JSON.stringify(jpwWorkspaceDrafts())')
        page.locator('#modalOverlay [data-module-work-notice] button').first.click()
        assert field.input_value()=='Synthetic pending scenario'
        page.locator('#modalCancel').click()
        assert not page.evaluate("JPWModuleWork.hasPending('personal-finance')")
        print('PASS PF modal preserved, blocked before submit, explicit resume',flush=True)

        page.evaluate("JPWNavigation.navigate('forex-operation');openFinalizeCompletionModal([{pi:0,oi:0,o:{id:'SYNTHETIC',currency:'USD'}}])")
        page.locator('[data-compl="0"]').fill('123.45')
        assert page.evaluate("JPWModuleWork.hasPending('forex')")
        value=before();freeze('forex');unchanged(value)
        page.locator('#modalConfirm').dispatch_event('click')
        unchanged(value)
        assert page.locator('[data-compl="0"]').input_value()=='123.45'
        page.locator('#modalOverlay [data-module-work-notice] button').first.click()
        page.locator('#modalCancel').click()
        print('PASS legacy Forex modal detected by real form IDs, draft preserved before command',flush=True)

        # Native Forex modal keeps all steps/fields and recovery controls reachable.
        page.evaluate("JPWNavigation.navigate('forex-management-accounts');JPWFXConsolidatedUI.openAccountRegistration()")
        page.locator('#fxcr-name').evaluate("el=>{el.value='Synthetic registration';el.dispatchEvent(new Event('input',{bubbles:true}));}")
        assert page.evaluate("JPWModuleWork.hasPending('forex')")
        value=before();freeze('forex');unchanged(value)
        assert page.locator('#fxcRegistrationDialog').evaluate('el=>el.open')
        assert page.locator('#fxcr-name').input_value()=='Synthetic registration'
        assert 'Synthetic registration' in page.evaluate('JSON.stringify(jpwWorkspaceDrafts())')
        page.keyboard.press('Escape')
        assert page.locator('#fxcRegistrationDialog').evaluate('el=>el.open')
        page.locator('#fxcRegistrationDialog [data-module-work-notice] button').first.click()
        assert page.evaluate("JPWModuleAvailability.canAccess('forex')")
        assert page.locator('#fxcr-name').input_value()=='Synthetic registration'
        print('PASS Forex native dialog: no close, hidden steps recovered, explicit resume',flush=True)

        # Hold only the fixture call's response; the real writer runs once after
        # a remote freeze. No product retries/timeouts or expectation changes.
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-login').fill('000009999')
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-platform').select_option(label='MetaTrader 5')
        page.locator('#fxcr-currency').fill('USD')
        page.locator('#fxcwNext').click()
        page.locator('#fxcr-profileKey').select_option(page.evaluate('riskProfilesForState()[0].key'))
        page.locator('#fxcwNext').click()
        page.evaluate("""()=>{window._workSaveOriginal=JPWFXConsolidated.saveRegistration;window._workSaveCount=0;
          JPWFXConsolidated.saveRegistration=(...args)=>{_workSaveCount++;return new Promise(resolve=>{window._workFinishSave=async()=>resolve(await _workSaveOriginal(...args));});};}""")
        page.locator('#fxcRegistrationSave').click()
        assert page.evaluate('JPWFXConsolidatedUI.workState().inflight')
        freeze('forex')
        page.evaluate('_workFinishSave()')
        page.wait_for_function('!JPWFXConsolidatedUI.workState().inflight')
        assert page.evaluate('_workSaveCount')==1
        assert page.evaluate("S.accounts.filter(a=>a.nome==='Synthetic registration').length")==1
        assert page.evaluate("JPWModuleAvailability.getState('forex')")=='frozen'
        assert page.locator('#fxcRegistrationStatus').inner_text()=='Gravação confirmada.'
        page.evaluate('JPWFXConsolidated.saveRegistration=_workSaveOriginal')
        print('PASS Forex confirmation already started completes once while frozen',flush=True)
        value=before()
        page.evaluate('jpwWorkspaceEdited.clear();jpwWorkspaceDraftProviders.get("module-work")(true)')
        assert page.evaluate('jpwWorkspaceDraftProviders.get("module-work")().length')==0
        assert page.evaluate("!JPWModuleWork.hasPending('alladin')&&!JPWModuleWork.hasPending('forex')&&!JPWModuleWork.hasPending('research')")
        unchanged(value)
        print('PASS explicit import draft-reset drops former UI work without writing financial data',flush=True)
        assert not errors,errors
        print('PASS module work suite: no page errors',flush=True)
        context.close();browser.close()
    finally:
        server.shutdown();server.server_close()

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Real backup/import/recovery and previous-code rollback, isolated synthetic profiles."""
import copy
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright
from module_availability_test import ROOT, KEY
from dashboard_macro_test import launch_browser
from dashboard_forex_relocation_test import serve
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap

BASE = 'ad5c23e7884be108ceaf35acd26fb1c3b28b57db'
FINANCIAL = ['alladin', 'personalFinance', 'accounts', 'forex', 'phases', 'ledger', 'mei', 'operationHistory']


def dialogs(page):
    policy = {'accept': True}
    page.on('dialog', lambda dialog: dialog.dismiss() if dialog.type == 'confirm' and not policy['accept'] else dialog.accept())
    page.evaluate("""()=>{
      window.__avAlerts=[];window.__avConfirms=[];
      const say=window.alert,ask=window.confirm;
      window.alert=message=>{__avAlerts.push(String(message));return say(message);};
      window.confirm=message=>{__avConfirms.push(String(message));return ask(message);};
    }""")
    return policy


def submit(page, payload, cancelled=False):
    page.evaluate("""data=>{window.__avAlerts=[];window.__avConfirms=[];
      importFullBackupFile(new File([JSON.stringify(data)],'synthetic.json',{type:'application/json'}));}""", payload)
    page.wait_for_function('window.__avConfirms.length>0' if cancelled else 'window.__avAlerts.length>0')
    return page.evaluate('({alerts:__avAlerts,confirms:__avConfirms})')


def financial(page):
    return page.evaluate('keys=>Object.fromEntries(keys.filter(k=>k in S).map(k=>[k,S[k]]))', FINANCIAL)


def expected_financial(payload):
    return {key: payload['state'][key] for key in FINANCIAL if key in payload['state']}


def state_and_storage(page):
    return page.evaluate("""()=>({state:JSON.stringify(S),storage:Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)])),
      blocked:jpWealthPersistenceIsBlocked(),unknown:jpWealthPersistenceOutcomeIsUnknown()})""")


def main():
    server, url = serve(ROOT)
    evidence = ROOT.parent / 'evidence' / 'availability-backup'
    evidence.mkdir(parents=True, exist_ok=True)
    results = []
    baseline_backup = None
    new_backup = None

    def check(name, fn):
        try:
            fn()
        except Exception as error:
            results.append({'name': name, 'result': 'PRODUCT_FAIL', 'error': repr(error)})
            print('PRODUCT_FAIL', name, repr(error), flush=True)
        else:
            results.append({'name': name, 'result': 'PASS'})
            print('PASS', name, flush=True)
        (evidence / 'results.json').write_text(json.dumps({'baseline': BASE, 'results': results}, indent=2))

    try:
        with tempfile.TemporaryDirectory(prefix='jpw-availability-baseline-') as tmp, sync_playwright() as playwright:
            previous_root = Path(tmp)
            archive = subprocess.check_output(['git', 'archive', BASE], cwd=ROOT)
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                # Python 3.9 on the existing host has no tarfile extraction filter.
                # Validate this trusted local Git archive before the equivalent extraction.
                base = previous_root.resolve()
                for member in tar.getmembers():
                    target = (base / member.name).resolve()
                    assert target == base or base in target.parents, member.name
                    assert member.isfile() or member.isdir() or member.issym() or member.islnk(), member.name
                    if member.issym() or member.islnk():
                        link = ((target.parent if member.issym() else base) / member.linkname).resolve()
                        assert link == base or base in link.parents, member.linkname
                tar.extractall(previous_root)
            previous_server, previous_url = serve(previous_root)
            browser = launch_browser(playwright)
            contexts = []

            def current():
                context = browser.new_context(viewport={'width':1440,'height':1000},service_workers='block')
                contexts.append(context)
                install_bootstrap(context)
                context.add_init_script("window.__onbShown=true;localStorage.setItem('jpw_nav_layout','sidebar');")
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                startup_dialog = lambda dialog: dialog.accept()
                page.on('dialog', startup_dialog)
                page.goto(url)
                page.wait_for_function('window.JPWModuleAvailabilityUI && window.JPWModuleWork')
                wait_bootstrap(page)
                page.remove_listener('dialog', startup_dialog)
                policy = dialogs(page)
                return context, page, errors, policy

            def previous():
                context = browser.new_context(service_workers='block')
                contexts.append(context)
                install_bootstrap(context)
                context.add_init_script('window.__onbShown=true;')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                startup_dialog = lambda dialog: dialog.accept()
                page.on('dialog', startup_dialog)
                page.goto(previous_url)
                page.wait_for_function("window.JPWAlladin && typeof dgBuildBackupBlob==='function'")
                wait_bootstrap(page)
                page.remove_listener('dialog', startup_dialog)
                policy = dialogs(page)
                return context, page, errors, policy

            try:
                # The old-format artifact is emitted by the real old build, never by deleting a new field.
                context, old, errors, _ = previous()
                old_data = old.evaluate("""async()=>{
                  S.onboarding.done=true;S.moduleAvailabilityProbe='synthetic baseline';S.mei.notes='Synthetic retained financial note';
                  if(save()!==true)throw Error('Synthetic baseline not saved');
                  const asset=await JPWAlladin.cadastro.addAsset({name:'Synthetic property A',nature:'IMOVEL',recordMode:'INDIVIDUAL',
                    location:'Synthetic location',acquisitionDate:'2020-03-15',tags:['synthetic'],owners:[{name:'Synthetic owner',shareBp:10000,isSelf:true}]});
                  if(!asset.ok||!asset.persistido)throw Error('Synthetic asset not persisted: '+JSON.stringify(asset));
                  return JSON.parse(await dgBuildBackupBlob(1,'previous-version.json','2026-09-24T12:00:00Z').text());
                }""")
                assert KEY not in old_data['workspace']['preferences']
                assert len(old_data['state']['alladin']['assets']) == 1
                assert not errors, errors
                baseline_backup = old_data
                (evidence / 'previous-version-backup.json').write_text(json.dumps(baseline_backup, indent=2))
                context.close()
                results.append({'name': 'authentic previous-build export', 'result': 'PASS', 'build': old_data.get('build')})

                context, source, errors, _ = current()
                receipt = submit(source, baseline_backup)
                assert any('com sucesso' in message for message in receipt['alerts']), receipt
                source.evaluate("""()=>{
                  if(!JPWModuleAvailability.setState('alladin','active').ok)throw Error('Fixture activation failed');
                  if(!JPWModuleAvailability.setState('forex','frozen').ok)throw Error('Fixture freeze failed');
                }""")
                new_backup = source.evaluate("""async()=>JSON.parse(await dgBuildBackupBlob(2,'current.json','2026-09-24T12:00:00Z').text())""")
                assert expected_financial(new_backup) == expected_financial(baseline_backup)
                assert not errors, errors
                (evidence / 'new-backup.json').write_text(json.dumps(new_backup, indent=2))
                context.close()

                def roundtrip():
                    context, page, errors, _ = current()
                    before = financial(page)
                    receipt = submit(page, new_backup)
                    assert any('Alladin: Congelado → Ativo' in message for message in receipt['confirms']), receipt
                    assert any('Forex: Ativo → Congelado' in message for message in receipt['confirms']), receipt
                    assert any('com sucesso' in message for message in receipt['alerts']), receipt
                    assert financial(page) == expected_financial(new_backup) and financial(page) != before
                    assert page.evaluate('localStorage.getItem("'+KEY+'")') == new_backup['workspace']['preferences'][KEY]
                    assert page.evaluate("JPWModuleAvailability.getState('alladin')") == 'active'
                    page.reload();page.wait_for_function('window.JPWModuleAvailability');wait_bootstrap(page)
                    assert financial(page) == expected_financial(new_backup)
                    assert page.evaluate('S.workspaceRecovery.pending') is False
                    assert not errors, errors
                    context.close()
                check('valid import: explicit unfreeze consent, full financial roundtrip and reload', roundtrip)

                def cancellation():
                    context, page, errors, policy = current()
                    before = state_and_storage(page);policy['accept'] = False
                    receipt = submit(page, new_backup, cancelled=True)
                    assert any('Alladin: Congelado → Ativo' in message for message in receipt['confirms']), receipt
                    assert not receipt['alerts'];assert state_and_storage(page) == before
                    assert not errors, errors;context.close()
                check('cancelled restoration leaves state, availability, storage and barriers unchanged', cancellation)

                def rejection():
                    context, page, errors, _ = current()
                    for invalid in ['', '{bad', json.dumps({'schemaVersion':2,'modules':{'alladin':'active'}}),
                                    json.dumps({'schemaVersion':1,'modules':{'alladin':'unknown'}}),
                                    json.dumps({'schemaVersion':1,'modules':{'unknown':'active'}})]:
                        payload = copy.deepcopy(new_backup);payload['workspace']['preferences'][KEY] = invalid
                        before = state_and_storage(page);receipt = submit(page, payload)
                        assert not receipt['confirms'], receipt
                        assert any('Backup inválido' in message for message in receipt['alerts']), receipt
                        assert state_and_storage(page) == before
                    assert not errors, errors;context.close()
                check('invalid/future/unknown import rejected before consent and any write', rejection)

                def read_failure():
                    context, page, errors, _ = current();before = state_and_storage(page)
                    page.evaluate("""key=>{window.__getAvailability=Storage.prototype.getItem;Storage.prototype.getItem=function(k){
                      if(k===key)throw new DOMException('Synthetic blocked read','SecurityError');return __getAvailability.call(this,k);};}""", KEY)
                    receipt = submit(page, new_backup)
                    page.evaluate('()=>{Storage.prototype.getItem=window.__getAvailability;}')
                    assert not receipt['confirms'];assert any('conferir a disponibilidade' in message for message in receipt['alerts']), receipt
                    assert state_and_storage(page) == before
                    assert not errors, errors;context.close()
                check('unreadable destination preference aborts before any import write', read_failure)

                def consent_conflict():
                    context, page, errors, _ = current();before = state_and_storage(page)
                    page.evaluate("""key=>{const ask=window.confirm;window.confirm=message=>{const accepted=ask(message);
                      if(accepted&&message.includes('Importar backup completo'))localStorage.setItem(key,JSON.stringify({schemaVersion:1,modules:{research:'frozen'}}));return accepted;};}""", KEY)
                    receipt = submit(page, new_backup)
                    after = state_and_storage(page)
                    assert any('mudou desde a confirmação' in message for message in receipt['alerts']), receipt
                    assert after['state'] == before['state'];assert after['blocked'] == before['blocked']
                    after['storage'].pop(KEY);before['storage'].pop(KEY, None)
                    assert after['storage'] == before['storage'];assert not errors, errors;context.close()
                check('preference changed after consent refuses stale restore before base replacement', consent_conflict)

                def old_and_null():
                    context, page, errors, _ = current()
                    page.evaluate("JPWModuleAvailability.setState('alladin','active')")
                    explicit = page.evaluate('localStorage.getItem("'+KEY+'")')
                    receipt = submit(page, baseline_backup)
                    assert any('com sucesso' in message for message in receipt['alerts']), receipt
                    assert page.evaluate('localStorage.getItem("'+KEY+'")') == explicit
                    assert financial(page) == expected_financial(baseline_backup)
                    payload = copy.deepcopy(new_backup);payload['workspace']['preferences'][KEY] = None
                    receipt = submit(page, payload)
                    assert any('Alladin: Ativo → Congelado' in message for message in receipt['confirms']), receipt
                    assert page.evaluate('localStorage.getItem("'+KEY+'")') is None
                    assert page.evaluate("JPWModuleAvailability.getState('alladin')") == 'frozen'
                    assert financial(page) == expected_financial(payload);assert not errors, errors;context.close()
                    context, page, errors, _ = current();submit(page, baseline_backup)
                    assert page.evaluate('localStorage.getItem("'+KEY+'")') is None
                    assert page.evaluate("JPWModuleAvailability.getState('alladin')") == 'frozen'
                    assert not errors, errors;context.close()
                check('actual old export preserves explicit choice or absent default; null resets explicitly', old_and_null)

                def recovery():
                    context, page, errors, policy = current();submit(page, baseline_backup)
                    for corrupt in ['{invalid<script>window.__executed=true</script>', '']:
                        page.evaluate("""([key,raw])=>{localStorage.setItem(key,raw);JPWModuleAvailability.reload('fixture');}""", [KEY, corrupt])
                        policy['accept'] = False
                        refused = page.evaluate("""async()=>{try{await dgBuildBackupBlob(3,'recovery.json','2026-09-24T12:00:00Z');return false;}catch(error){return error.message.includes('cancelada');}}""")
                        assert refused;assert page.evaluate('localStorage.getItem("'+KEY+'")') == corrupt
                        policy['accept'] = True
                        payload = page.evaluate("""async()=>JSON.parse(await dgBuildBackupBlob(3,'recovery.json','2026-09-24T12:00:00Z').text())""")
                        assert KEY not in payload['workspace']['preferences']
                        assert any(item['text'] == corrupt and 'disponibilidade' in item['label'] for item in payload['workspace']['drafts'])
                        assert expected_financial(payload) == expected_financial(baseline_backup)
                        assert page.evaluate('localStorage.getItem("'+KEY+'")') == corrupt
                        assert page.evaluate('window.__executed===undefined')
                        suffix = 'empty' if corrupt == '' else 'malformed'
                        (evidence / ('recovery-'+suffix+'-backup.json')).write_text(json.dumps(payload, indent=2))
                        destination, other, other_errors, _ = current()
                        other.evaluate("JPWModuleAvailability.setState('alladin','active')")
                        selected = other.evaluate('localStorage.getItem("'+KEY+'")')
                        submit(other, payload)
                        assert other.evaluate('localStorage.getItem("'+KEY+'")') == selected
                        other.evaluate('jpwWorkspaceShowDrafts()')
                        texts = other.locator('#workspaceDraftDialog textarea').evaluate_all('nodes=>nodes.map(node=>node.value)')
                        assert corrupt in texts;assert other.locator('#workspaceDraftDialog script').count() == 0
                        assert other.evaluate('window.__executed===undefined');assert not other_errors, other_errors;destination.close()
                    assert not errors, errors;context.close()
                check('corrupt/empty recovery requires consent, preserves raw and data, restores as inert text', recovery)

                def interrupted(failure_key, initial_active=False):
                    context, page, errors, _ = current()
                    if initial_active:page.evaluate("JPWModuleAvailability.setState('alladin','active')")
                    payload = copy.deepcopy(new_backup)
                    payload['workspace']['preferences'][KEY] = json.dumps({'schemaVersion':1,'modules':{'alladin':'frozen'}})
                    payload['workspace']['preferences']['jpw_fs'] = '2'
                    page.evaluate("""target=>{window.__originalPut=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){
                      if(k===target)throw new DOMException('Synthetic quota','QuotaExceededError');return __originalPut.call(this,k,v);};}""", failure_key)
                    receipt = submit(page, payload)
                    assert not any('com sucesso' in message for message in receipt['alerts']), receipt
                    assert any('pendente' in message for message in receipt['alerts']), receipt
                    assert page.evaluate('S.workspaceRecovery.pending && jpWealthPersistenceIsBlocked()')
                    assert page.evaluate('JSON.parse(localStorage.getItem(LSKEY)).workspaceRecovery.pending')
                    assert page.locator('#workspaceRestoreWarning').count() == 1
                    assert financial(page) == expected_financial(payload)
                    if initial_active:
                        assert page.evaluate("JPWModuleAvailability.getState('alladin')") == 'frozen'
                    page.reload();page.wait_for_function('window.JPWModuleAvailability');wait_bootstrap(page)
                    assert page.evaluate('S.workspaceRecovery.pending') is False
                    assert page.evaluate('localStorage.getItem("'+KEY+'")') == payload['workspace']['preferences'][KEY]
                    assert financial(page) == expected_financial(payload)
                    assert not errors, errors;context.close()
                check('refused availability write retains durable pending journal and resumes on reload', lambda: interrupted(KEY))
                check('failure after availability projects freeze without claiming completed restoration', lambda: interrupted('jpw_fs', True))

                def unavailable_readback():
                    context, page, errors, _ = current()
                    page.evaluate("""target=>{
                      const put=Storage.prototype.setItem,get=Storage.prototype.getItem;let written=false;
                      Storage.prototype.setItem=function(k,v){const result=put.call(this,k,v);if(k===target)written=true;return result;};
                      Storage.prototype.getItem=function(k){if(k===target&&written)throw new DOMException('Synthetic read-back failure','SecurityError');return get.call(this,k);};
                    }""", KEY)
                    receipt = submit(page, new_backup)
                    assert not any('com sucesso' in message for message in receipt['alerts']), receipt
                    assert page.evaluate('S.workspaceRecovery.pending&&jpWealthPersistenceIsBlocked()')
                    assert page.evaluate('JSON.parse(localStorage.getItem(LSKEY)).workspaceRecovery.pending')
                    assert financial(page) == expected_financial(new_backup)
                    assert page.evaluate('JPWModuleAvailability.snapshot().readable') is False
                    page.reload();page.wait_for_function('window.JPWModuleAvailability');wait_bootstrap(page)
                    assert page.evaluate('S.workspaceRecovery.pending') is False
                    assert page.evaluate('localStorage.getItem("'+KEY+'")') == new_backup['workspace']['preferences'][KEY]
                    assert financial(page) == expected_financial(new_backup)
                    assert not errors, errors;context.close()
                check('unreadable preference read-back retains pending journal and recovers without data duplication', unavailable_readback)

                def refused_final_commit():
                    context, page, errors, _ = current()
                    page.evaluate("""()=>{const put=Storage.prototype.setItem;let journalWrites=0;Storage.prototype.setItem=function(k,v){
                      if(k===LSKEY&&++journalWrites===2)return;return put.call(this,k,v);};}""")
                    receipt = submit(page, new_backup)
                    assert not any('com sucesso' in message for message in receipt['alerts']), receipt
                    assert page.evaluate('JSON.parse(localStorage.getItem(LSKEY)).workspaceRecovery.pending') is True
                    assert page.evaluate('S.workspaceRecovery.pending&&jpWealthPersistenceIsBlocked()')
                    assert financial(page) == expected_financial(new_backup)
                    page.reload();page.wait_for_function('window.JPWModuleAvailability');wait_bootstrap(page)
                    assert page.evaluate('S.workspaceRecovery.pending') is False
                    assert financial(page) == expected_financial(new_backup)
                    assert not errors, errors;context.close()
                check('silent refusal of final journal commit cannot report success and recovers', refused_final_commit)

                def rollback():
                    context, page, errors, _ = previous()
                    pref = new_backup['workspace']['preferences'][KEY]
                    page.evaluate('([key,raw])=>localStorage.setItem(key,raw)', [KEY, pref])
                    before = state_and_storage(page)
                    receipt = submit(page, new_backup)
                    assert any('Backup inválido' in message for message in receipt['alerts']), receipt
                    assert not receipt['confirms'];assert state_and_storage(page) == before
                    receipt = submit(page, baseline_backup)
                    assert any('com sucesso' in message for message in receipt['alerts']), receipt
                    assert page.evaluate('localStorage.getItem("'+KEY+'")') == pref
                    assert financial(page) == expected_financial(baseline_backup)
                    page.reload();page.wait_for_function('window.JPWAlladin');wait_bootstrap(page)
                    assert page.evaluate('localStorage.getItem("'+KEY+'")') == pref
                    assert financial(page) == expected_financial(baseline_backup)
                    assert page.evaluate("JPWNavigation.navigate('alladin')") is True
                    assert not errors, errors;context.close()
                check('real previous code: refuses new key; restores original old backup without deleting new raw', rollback)
            finally:
                for context in contexts:
                    context.close()
                browser.close();previous_server.shutdown();previous_server.server_close()
        failed = [result for result in results if result['result'] != 'PASS']
        receipt = {'result':'PRODUCT_FAIL' if failed else 'PASS','baseline':BASE,
                   'tested_source_sha256': hashlib.sha256((ROOT/'src/js/00-core/07-workspace-backup.js').read_bytes()).hexdigest(),
                   'previous_backup_sha256': hashlib.sha256((evidence/'previous-version-backup.json').read_bytes()).hexdigest(),
                   'new_backup_sha256': hashlib.sha256((evidence/'new-backup.json').read_bytes()).hexdigest(),
                   'checks':results}
        (evidence/'results.json').write_text(json.dumps(receipt,indent=2))
        print('module_availability_backup_test',receipt['result'],len(results)-len(failed),'PASS /',len(failed),'FAIL',flush=True)
        return 1 if failed else 0
    finally:
        server.shutdown();server.server_close()


if __name__ == '__main__':
    raise SystemExit(main())

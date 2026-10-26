from pathlib import Path
import sys,json,importlib.util,hashlib,traceback,os
root=Path.cwd();out=Path('/private/tmp/jpw-dante-20261024/finalization-default-proposal');sys.path.insert(0,str(root/'tools'))
import finalize_session_test as original
from playwright.sync_api import sync_playwright
spec=importlib.util.spec_from_file_location('finalize_proposed_regression',out/'finalize_session_test.proposed.py');candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate);candidate.ROOT=root;os.chdir(root)
files=['tools/finalize_session_test.py','src/js/40-app/09-settings-modal.js','src/js/40-app/07-finalize-session.js','build-id.js'];identity=lambda:{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files};before=identity();negatives=[]
checker=candidate.assert_profile_session_default
mutants={
 'residual-sidebar-photo':"document.querySelector('#settingsProfileAvatar img').src=saved.avatarDataUrl",
 'residual-header-photo':"document.querySelector('#headerProfileAvatar img').src=saved.avatarDataUrl",
 'residual-editor-photo':"document.querySelector('#settingsAccountAvatar img').src=saved.avatarDataUrl",
 'cached-personal-identity':"settingsProfileState.confirmed={...saved}",
 'residual-name-input':"document.querySelector('#settingsProfileNameInput').value=saved.displayName",
 'residual-header-accessible-name':"document.getElementById('headerProfileBtn').setAttribute('aria-label','Abrir configurações do perfil — '+saved.displayName)"
}
def defended_checker(page):
 checker(page)
 state=page.evaluate('({confirmed:structuredClone(settingsProfileState.confirmed),draft:structuredClone(settingsProfileState.draft)})')
 for name,mutation in mutants.items():
  page.evaluate("() => {const saved=settingsProfileRead().value;"+mutation+";}")
  rejected=False
  try:checker(page)
  except AssertionError:rejected=True
  finally:
   page.evaluate('state=>{settingsProfileState.confirmed=state.confirmed;settingsProfileState.draft=state.draft;renderSettingsProfile()}',state)
  assert rejected,'Negative control escaped proposed privacy oracle: '+name
  negatives.append({'mutation':name,'rejected':True,'url':page.url})
 checker(page)
candidate.assert_profile_session_default=defended_checker
server,url=original.start_server();rows=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args=['--no-sandbox'])
  for label,module,entry,expected in [('RED-original-default-oracle',original,'index.html','PRODUCT_FAIL'),('GREEN-source-profile-privacy',candidate,'index.html','PASS'),('GREEN-portable-profile-privacy',candidate,'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html','PASS')]:
   row={'case':label,'expected':expected,'result':'NOT_RUN','entry':entry}
   try:module.run_profile_finalize_contract(b,url+entry);row['result']='PASS'
   except AssertionError as e:row.update(result='PRODUCT_FAIL',error=str(e),traceback=traceback.format_exc())
   except Exception as e:row.update(result='TEST_HARNESS_FAIL',error=str(e),traceback=traceback.format_exc())
   finally:
    for context in b.contexts:context.close()
   rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
  b.close()
finally:server.shutdown();server.server_close()
report={'cases':rows,'negativeControls':negatives,'negativeCount':len(negatives),'source_before':before,'source_after':identity(),'source_unchanged':before==identity(),'proposal_sha256':hashlib.sha256((out/'finalize_session_test.proposed.py').read_bytes()).hexdigest(),'limits':['Scratch candidate test executed; no project file changed.','Real product/profile reader/storage and finalization UI; disposable synthetic contexts.','Stored personal profile intentionally preserved, anonymized session memory/UI enforced.','No headed or native zoom, no gate override.']}
(out/'replay-receipt.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert report['source_unchanged']
assert all(r['result']==r['expected'] for r in rows),[(r['case'],r['result']) for r in rows]
assert len(negatives)==24 and all(x['rejected'] for x in negatives)
print('PROPOSAL PASS: original obsolete oracle rejected; source/portable revised privacy checks and 24 negative controls passed',flush=True)

"""Task-private evidence binding, never changes product/runner or confers approval."""
from pathlib import Path
import sys,json,hashlib,subprocess,tarfile,datetime,ast,os,shlex
A=Path(__file__).resolve().parent;R=A.parents[2];V=R/'docs/validation/planning-monthly-close-20261022'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(*args):return subprocess.check_output(['git',*args],cwd=R).decode().strip()
def links():
 paths=git('ls-files','--cached','--others','--exclude-standard','-z').split('\0')
 return {s:os.readlink(R/s) for s in sorted(set(paths)) if s and (R/s).is_symlink()}
def preserves_ast(old,new):
 if isinstance(old,ast.AST):return type(old)==type(new) and all(preserves_ast(v,getattr(new,k)) for k,v in ast.iter_fields(old))
 if isinstance(old,list):
  if not isinstance(new,list):return False
  at=0
  for item in old:
   while at<len(new) and not preserves_ast(item,new[at]):at+=1
   if at==len(new):return False
   at+=1
  return True
 return old==new
def inventory():
 paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=R).decode().split('\0')
 return {s:H(R/s) for s in sorted(set(paths)) if s and not s.startswith('docs/validation/planning-monthly-close-20261022/') and (R/s).is_file() and not (R/s).is_symlink()}
def check_scope():
 baseline=json.loads((A/'baseline.json').read_text());assert git('branch','--show-current')==baseline['branch'] and git('rev-parse','HEAD')==baseline['head'],'Baseline branch/HEAD drift'
 before=baseline['files'];current=inventory();allowed=['src/js/30-accounting/06-planning/02-state.js','src/js/30-accounting/06-planning/03-ui.js','src/styles/app.css','tools/planning_state_test.js','tools/planning_three_tabs_test.py','tools/ui_visual_quality_test.py','tools/regression-memory.json','docs/architecture/PLANNING.md','README.md','CHANGELOG.md','SESSION_HANDOFF.md','docs/governance/CURRENT-STATE.md','docs/work/ACTIVE-TASK.md','index.html','build-id.js','sw.js','src/js/manifest.json']
 prefixes=['dist/','src/vendor/downloads/','src/vendor/market-hours/runtime-payload.js'];changed=[];unchanged=[]
 for s,item in before.items():
  if 'link' in item:
   assert (R/s).is_symlink() and os.readlink(R/s)==item['link'], 'Baseline symlink changed '+s
   continue
  if current.get(s)==item['sha256']:unchanged.append(s)
  elif s in allowed or any(s.startswith(x) for x in prefixes):changed.append(s)
  else:raise AssertionError('Unauthorized baseline mutation '+s)
 new=[s for s in current if s not in before]
 permittednew={'tools/planning_monthly_close_test.py','docs/superpowers/plans/2026-10-22-planning-monthly-close.md','docs/work/CHG-JPW-PLANNING-CLOSE-PRODUCT-20261022.md','docs/work/CHG-JPW-PLANNING-CLOSE-TESTS-20261022.md'}
 assert set(new)<=permittednew,('Unexpected additions',set(new)-permittednew)
 with tarfile.open(A/'candidate-e08c-before.tar.gz') as tar:
  old=tar.extractfile('src/js/30-accounting/06-planning/02-state.js').read().decode();cur=(R/'src/js/30-accounting/06-planning/02-state.js').read_text()
  assert old.split('  function previewFinalizeMonth')[0]==cur.split('  function previewFinalizeMonth')[0], 'Financial command prefix changed'
  assert old.split('  function reviseAccount',1)[1]==cur.split('  function reviseAccount',1)[1], 'Financial suffix changed'
  runner=tar.extractfile('tools/quality_gate.py').read();assert runner==(R/'tools/quality_gate.py').read_bytes()
  oldstate=tar.extractfile('tools/planning_state_test.js').read().decode();newstate=(R/'tools/planning_state_test.js').read_text();mark='// Approved22/10/2026 closure diagnostics: additive read-only contract.';end="for(const t of require('./planning_monthly_result_input_test.js').tests)test(t.name,t.run);"
  assert newstate.split(mark)[0].rstrip()==oldstate.split(end)[0].rstrip() and newstate.split(end)[1]==oldstate.split(end)[1], 'Existing state tests changed'
  oldvisual=ast.parse(tar.extractfile('tools/ui_visual_quality_test.py').read().decode());newvisual=ast.parse((R/'tools/ui_visual_quality_test.py').read_text());newfunctions={n.name:n for n in newvisual.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
  for n in oldvisual.body:
   if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
    assert n.name in newfunctions and (preserves_ast(n,newfunctions[n.name]) if n.name in ['main','required_ids'] else ast.dump(n,include_attributes=False)==ast.dump(newfunctions[n.name],include_attributes=False)), 'Existing visual oracle/entry removed or changed '+n.name
  oldtabs=ast.parse(tar.extractfile('tools/planning_three_tabs_test.py').read().decode());newtabs=ast.parse((R/'tools/planning_three_tabs_test.py').read_text());newtabfn={n.name:ast.dump(n,include_attributes=False) for n in newtabs.body if isinstance(n,ast.FunctionDef)}
  assert all(n.name=='stale_choice_case' or newtabfn.get(n.name)==ast.dump(n,include_attributes=False) for n in oldtabs.body if isinstance(n,ast.FunctionDef)), 'Other three-tab cases changed'
  oldreg=json.loads(tar.extractfile('tools/regression-memory.json').read());newreg=json.loads((R/'tools/regression-memory.json').read_text())
  # Preserve every previous regression entry as an identical object.
  key=next(k for k,v in oldreg.items() if isinstance(v,list) and v and isinstance(v[0],dict) and 'id' in v[0]);indexed={x['id']:x for x in newreg[key]}
  assert all(indexed.get(x['id'])==x for x in oldreg[key]),'Old regression entry rewritten'
 return {'changed':changed,'unchanged_count':len(unchanged),'new':new,'previous_regression_entries':len(oldreg[key]),'financial_command_bytes_unchanged':True,'runner_bytes_unchanged':True}
def frozen():return json.loads((A/'freeze.json').read_text())
def verify():
 f=frozen();assert all(H(A/p)==h for p,h in f['task_controls'].items()),'Task evidence control changed'
 assert git('branch','--show-current')==f['branch'] and git('rev-parse','HEAD')==f['head'],'Branch/HEAD drift'
 assert links()==f['links'],'Symlink inventory drift'
 actual=inventory();assert actual==f['inputs'], {'changed':[s for s in actual if actual[s]!=f['inputs'].get(s)],'missing':[s for s in f['inputs'] if s not in actual]};check_scope();return f
if sys.argv[1]=='scope':print(json.dumps(check_scope()))
elif sys.argv[1]=='freeze':
 scope=check_scope();sys.path.insert(0,str(R/'tools'));import ui_visual_quality_test as visual,quality_gate as gate
 ids=[x[0] for x in gate.FULL];assert len(ids)==96
 previous=json.loads((R/'docs/validation/planning-monthly-inline-20261021/final-e08c/UI-DEFAULT-240.json').read_text());oldids=[c['id'] for c in previous['cases']];assert len(oldids)==240 and set(oldids)<=set(visual.required_ids('all'))
 data={'branch':git('branch','--show-current'),'head':git('rev-parse','HEAD'),'links':links(),'task_controls':{p:H(A/p) for p in ['brief.md','run_logged.py','release_protocol.py','baseline.json','candidate-e08c-before.tar.gz']},'created_at':now(),'build':__import__('re').search("JP_WEALTH_BUILD_ID = '([^']+)'",(R/'build-id.js').read_text()).group(1),'inputs':inventory(),'scope':scope,'full_check_ids':ids,'visual_ids':visual.required_ids('all')}
 (A/'freeze.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');V.mkdir(exist_ok=True,parents=True);(V/'FROZEN-INPUTS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('FROZEN',data['build'],len(data['inputs']),len(data['visual_ids']))
elif sys.argv[1]=='verify':f=verify();print('PASS frozen identities stable',f['build'])
elif sys.argv[1]=='receipt':
 f=verify();command=json.loads((A/'full-command.json').read_text());assert command['exit_code']==0 and command['finished_at']
 assert Path(command['cwd'])==R and len(command['command'])==6, 'Wrong command context'
 assert Path(command['command'][0]).resolve()==Path(sys.executable).resolve() and command['command'][1:5]==['tools/quality_gate.py','--tier','full','--artifact'] and Path(command['command'][5]).resolve()==(A/'full.json').resolve(), 'Wrong FULL argv'
 assert command['freeze_sha256']==H(A/'freeze.json') and command['frozen_before'] is True and command['frozen_after'] is True,'Execution not bound to frozen inputs'
 raw=json.loads((A/'full.json').read_text());assert raw['tier']=='full' and raw['summary']['PASS']==96 and sum(raw['summary'].values())==96
 stamp=lambda value:datetime.datetime.fromisoformat(value)
 assert stamp(f['created_at'])<=stamp(command['started_at']) and stamp(command['started_at'])-datetime.timedelta(seconds=1)<=stamp(raw['started_at'])<=stamp(raw['finished_at'])<=stamp(command['finished_at']), 'Stale or out-of-run FULL receipt (raw timestamps have second precision)'
 assert raw['git']['head']==f['head'] and raw['git']['branch']==f['branch'],'Raw FULL Git identity mismatch'
 assert [x['name'] for x in raw['checks']]==f['full_check_ids'];assert all(x['result']=='PASS' and x['returncode']==0 for x in raw['checks'])
 visual=Path(raw['full_evidence_directory'])/'ui-visual-quality/ui-visual-quality-results.json';report=json.loads(visual.read_text());assert report['classification']=='PASS' and report['source_unchanged'] is True
 visual_command=shlex.split(next(c['command'] for c in raw['checks'] if c['name']=='ui-visual-quality'));assert visual_command[-2:]==['--out',str(visual.parent)],'Visual receipt path differs from executed command'
 assert all(f['inputs'].get(p)==h for p,h in report['source_sha256'].items()) and report['test_sha256']==f['inputs']['tools/ui_visual_quality_test.py'],'Visual source binding mismatch'
 assert stamp(raw['started_at'])<=stamp(report['started_at'])<=stamp(report['finished_at'])<=stamp(raw['finished_at']),'Visual receipt stale'
 assert set(c['id'] for c in report['cases'])==set(f['visual_ids']) and len(report['cases'])==len(f['visual_ids']);assert all(c['classification']=='PASS' for c in report['cases'])
 out={'build':f['build'],'classification':'PASS','actual_exit_code':0,'full_passed':96,'full_check_ids':f['full_check_ids'],'visual_passed':len(report['cases']),'frozen_inputs_sha256':H(A/'freeze.json'),'full_sha256':H(A/'full.json'),'command_sha256':H(A/'full-command.json'),'log_sha256':H(A/'full.log'),'visual_sha256':H(visual),'created_at':now(),'human_acceptance':'PENDING'}
 for src,dst in [(A/'full.json',V/'FULL-RAW.json'),(A/'full-command.json',V/'FULL-COMMAND.json'),(A/'full.log',V/'FULL.log'),(visual,V/'VISUAL-RAW.json')]:dst.write_bytes(src.read_bytes())
 (V/'FULL-RESULT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out))

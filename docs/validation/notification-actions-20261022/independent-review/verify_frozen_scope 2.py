from pathlib import Path
import ast,hashlib,json,os,re,tarfile,sys
ROOT=Path.cwd();C=ROOT/'.superpowers/sdd/2026-10-22-notification-actions';OUT=ROOT/'docs/validation/notification-actions-20261022/independent-review'
freeze_raw=(C/'freeze-before.json').read_bytes();f=json.loads(freeze_raw);b=json.loads((C/'baseline.json').read_text());mismatch=[];regular=0;links=0
for name,value in f['files'].items():
 path=ROOT/name
 if 'sha256' in value:
  regular+=1
  if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=value['sha256']:mismatch.append(name)
 elif 'link' in value:
  links+=1
  if not path.is_symlink() or os.readlink(path)!=value['link']:mismatch.append(name)
harness=Path(f['external_harness']['path']);harness_ok=harness.is_file() and hashlib.sha256(harness.read_bytes()).hexdigest()==f['external_harness']['sha256']
changed=[name for name,value in b['files'].items() if (ROOT/name).is_file() and hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=value]
def contract(name):return json.loads((ROOT/name).read_text().split('```yaml\n',1)[1].split('\n```',1)[0])
product=contract('docs/work/CHG-JPW-NOTIFICATION-ACTIONS-PRODUCT-20261022.md');tests=contract('docs/work/CHG-JPW-NOTIFICATION-ACTIONS-TESTS-20261022.md')
allowed=set(product['scope']['allowed_files']+tests['scope']['allowed_files']+product['derived_artifacts']['allowed']+tests['derived_artifacts']['allowed'])
def permitted(name):return name in allowed or any(v.endswith('/') and name.startswith(v) for v in allowed)
unexpected=[name for name in changed if not permitted(name)]
with tarfile.open(C/'baseline-recoverable.tar.gz') as tar:
 def old(name):return tar.extractfile(name).read().decode()
 before_memory=json.loads(old('tools/regression-memory.json'));after_memory=json.loads((ROOT/'tools/regression-memory.json').read_text())
 old_entries=before_memory['entries'];new_entries=after_memory['entries'];memory_unchanged=new_entries[:len(old_entries)]==old_entries
 old_planning=re.findall(r"test\('([^']+)'",old('tools/planning_state_test.js'));new_planning=re.findall(r"test\('([^']+)'",(ROOT/'tools/planning_state_test.js').read_text())
 old_visual=ast.parse(old('tools/ui_visual_quality_test.py'));new_visual=ast.parse((ROOT/'tools/ui_visual_quality_test.py').read_text())
 def funcs(tree):return {n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 of,nf=funcs(old_visual),funcs(new_visual)
 visual_functions_unchanged=all(name in nf and ast.dump(node,include_attributes=False)==ast.dump(nf[name],include_attributes=False) for name,node in of.items() if name not in ['required_ids','main'])
 sys.path.insert(0,str(ROOT/'tools'));import ui_visual_quality_test as visual
 old_required=of['required_ids'];scope=dict(vars(visual));exec(compile(ast.Module(body=[old_required],type_ignores=[]),'<preserved-required-ids>','exec'),scope)
 old_ids=scope['required_ids']('all');new_ids=visual.required_ids('all')
 preserved_static={}
 for name in ['notification_center_test.py','notification_efficiency_test.py']:
  osource=old('tools/'+name).split('def main():',1)[1];nsource=(ROOT/'tools'/name).read_text().split('def main():',1)[1]
  pattern=r"\('([a-z0-9-]+)',"
  oids=set(re.findall(pattern,osource));nids=set(re.findall(pattern,nsource));preserved_static[name]={'old_static_case_ids':sorted(oids),'current_static_case_ids':sorted(nids),'missing':sorted(oids-nids)}
 own=json.loads((C/'review-independent/intermediate-fixes-corrected.json').read_text());own_match=[name for name,digest in own['after'].items() if f['files'].get(name,{}).get('sha256')!=digest]
 forbidden_equal={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==b['files'][name] for name in ['src/js/30-accounting/06-planning/01-engine.js','src/js/10-domain/00-forex-engine.js','src/js/00-core/00-forex-policy.js','tools/quality_gate.py','AGENTS.md','tools/planning_ui_test.py']}
 preexisting_source_untouched={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in b['preexisting'].items() if not name.startswith(('dist/','src/vendor/')) and name not in ['build-id.js','src/js/manifest.json','src/js/30-accounting/06-planning/03-ui.js','tools/regression-memory.json']}
 result={'freeze_sha256':hashlib.sha256(freeze_raw).hexdigest(),'head':f['head'],'branch':f['branch'],'build':'8b0b231a1b0c41b7','freeze_regular_files':regular,'freeze_symlinks':links,'freeze_mismatches':mismatch,'external_harness_equal':harness_ok,'changes_vs_task_baseline':changed,'out_of_contract_changes':unexpected,'old_regression_entries':len(old_entries),'new_regression_entries':len(new_entries),'old_regression_entries_equal':memory_unchanged,'old_planning_cases':len(old_planning),'new_planning_cases':len(new_planning),'missing_old_planning_cases':sorted(set(old_planning)-set(new_planning)),'old_visual_ids':len(old_ids),'new_visual_ids':len(new_ids),'missing_old_visual_ids':sorted(set(old_ids)-set(new_ids)),'visual_old_oracle_functions_equal':visual_functions_unchanged,'notification_static_ids':preserved_static,'own_six_browser_receipt_inputs_not_matching_freeze':own_match,'forbidden_and_unrelated_inputs_equal':forbidden_equal,'unaffected_preexisting_source_equal':preexisting_source_untouched,'scope_limits':['Raw other-agent receipts inspected as evidence, never counted as own execution.','Full gate still running; no FULL or distribution PASS is asserted.','Only 12 modular inputs in the six-case own receipt are bound by its hashes; final build distribution is identified by freeze and belongs to the official gate.']}
 (OUT/'scope-and-preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 assert not mismatch and harness_ok and not unexpected and memory_unchanged and not result['missing_old_planning_cases'] and not result['missing_old_visual_ids'] and visual_functions_unchanged and not own_match and all(forbidden_equal.values()) and all(preexisting_source_untouched.values()),result
 print(json.dumps({k:v for k,v in result.items() if k not in ['changes_vs_task_baseline','notification_static_ids','scope_limits']},ensure_ascii=False,indent=2))

#!/usr/bin/env python3
"""Offline, read-only verifier. 0 valid; 1 inconsistent; 2 missing dependency."""
import argparse,hashlib,json,pathlib,sys

def validate_provenance(d,evidence_root=None):
 """Receipt structure; with explicit evidence_root also verify dispatch bytes."""
 if not isinstance(d,dict): return ['receipt must be an object']
 errors=[]
 required=('attempt_id','case_id','fresh_session_id','model_requested','fresh_mode','input_sha256','output_sha256','raw_input_log','raw_output_log','tool_log','dispatch_log','dispatch_sha256','infrastructure_record')
 for field in required:
  if not isinstance(d.get(field),str) or not d[field].strip(): errors.append('required observable '+field)
 for field in ('input_sha256','output_sha256','dispatch_sha256'):
  v=d.get(field)
  if not isinstance(v,str) or len(v)!=64 or any(c not in '0123456789abcdef' for c in v): errors.append('invalid hash '+field)
 if d.get('fresh_mode')!='new_context_session': errors.append('fresh context not demonstrated')
 if type(d.get('repetition')) is not int or d['repetition'] not in (1,2,3): errors.append('invalid repetition')
 if not isinstance(d.get('tools_used'),list): errors.append('missing tools_used; empty list allowed with empty log')
 elif any(not isinstance(tool,str) or not tool.strip() for tool in d['tools_used']): errors.append('tools_used elements must be nonempty strings')
 reasons=d.get('unavailable_reasons',{})
 if not isinstance(reasons,dict): errors.append('unavailable_reasons must be object'); reasons={}
 for field in ('model_backend_exact_build','reasoning_hidden'):
  if d.get(field) is not None and (not isinstance(d[field],str) or not d[field].strip()): errors.append('optional metadata must be nonempty string or null '+field)
  reason=reasons.get(field)
  if d.get(field) is None and (not isinstance(reason,str) or not reason.strip()): errors.append('unknown optional field needs reason '+field)
 if evidence_root is not None:
  try:
   base=pathlib.Path(evidence_root).resolve()
   for field in ('dispatch_log','infrastructure_record'):
    value=d.get(field)
    if not isinstance(value,str) or not value: raise ValueError('missing evidence '+field)
    rel=pathlib.Path(value)
    if rel.is_absolute() or '..' in rel.parts: raise ValueError('evidence path escape')
    target=base/rel; target.resolve().relative_to(base); cursor=base
    for part in rel.parts:
     cursor=cursor/part
     if cursor.is_symlink(): raise ValueError('evidence symlink')
    if not target.is_file(): raise ValueError('missing evidence '+field)
    if field=='dispatch_log' and hashlib.sha256(target.read_bytes()).hexdigest()!=d.get('dispatch_sha256'): raise ValueError('dispatch hash mismatch')
  except (ValueError,TypeError,OSError,RuntimeError) as e: errors.append(str(e))
 return errors

def check(kit,repo,sources):
 errors=[]; missing=[]
 try: roots={'kit':kit.resolve(),'repo':repo.resolve(),'sources':sources.resolve()}
 except (RuntimeError,OSError) as e: return 1,['invalid root: '+str(e)]
 def locate(item):
  if not isinstance(item,dict) or item.get('root') not in roots or not isinstance(item.get('path'),str): raise ValueError('invalid reference/root')
  rel=pathlib.Path(item['path']); base=roots[item['root']]
  if not item['path'] or rel.is_absolute() or '..' in rel.parts: raise ValueError('path escape')
  target=base/rel
  try: target.resolve().relative_to(base)
  except ValueError: raise ValueError('symlink escape')
  # Reject symlinks even inside root: immutable identity must be an ordinary file.
  cursor=base
  for part in rel.parts:
   cursor=cursor/part
   if cursor.is_symlink(): raise ValueError('symlink reference')
  return target
 try:
  path=locate({'root':'kit','path':'manifest.json'})
  if not path.is_file(): return 2,['missing manifest.json']
  m=json.loads(path.read_text(encoding='utf-8'))
  for field in ('schema_version','version','status','revision','state_revision','validation_policy','adoption','native_mt5','behavioral_pilot','files','references'):
   if field not in m: raise ValueError('missing field '+field)
  if m['schema_version']!=1 or m['version']!='0.1.0' or m['status']!='CANDIDATE': raise ValueError('schema/version/status mismatch')
  if m['validation_policy']!='MANUAL_CANDIDATE' or m['adoption']!='NOT_ADOPTED' or m['native_mt5']!='NOT_RUN': raise ValueError('manual candidate policy: NOT_ADOPTED/native NOT_RUN required; new policy requires reviewed revision')
  if not isinstance(m['revision'],str) or not m['revision'].strip() or type(m['state_revision']) is not int or m['state_revision']<1: raise ValueError('invalid revision')
  if m['behavioral_pilot'] not in ('NOT_RUN','IN_PROGRESS','PASS','FAIL','INCONCLUSIVE'): raise ValueError('invalid behavioral state')
  if m['state_revision']==1 and m['behavioral_pilot']!='NOT_RUN': raise ValueError('initial state revision must be NOT_RUN')
  if m['behavioral_pilot']!='NOT_RUN':
   proof=m.get('behavioral_evidence',{}); pp=locate(proof)
   if not isinstance(proof.get('sha256'),str) or len(proof['sha256'])!=64: raise ValueError('state evidence needs hash')
   if not pp.is_file(): missing.append(str(pp))
   else:
    raw=pp.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=proof['sha256']: raise ValueError('state evidence hash mismatch')
    receipt=json.loads(raw)
    if any(receipt.get(k)!=m[k] for k in ('state_revision',)) or receipt.get('kit_revision')!=m['revision'] or receipt.get('result')!=m['behavioral_pilot']: raise ValueError('state evidence identity mismatch')
    attempts=receipt.get('attempt_ids')
    if not isinstance(attempts,list) or not attempts or any(not isinstance(a,str) or not a for a in attempts) or len(set(attempts))!=len(attempts): raise ValueError('invalid evidence attempts')
    if m['behavioral_pilot']=='PASS' and len(attempts)!=36: raise ValueError('PASS evidence requires 36 attempt identities')
  if not isinstance(m['files'],list) or not m['files'] or not isinstance(m['references'],list): raise ValueError('invalid file/reference list')
  seen=set()
  for item in m['files']+m['references']:
   try:
    p=locate(item); key=(item['root'],item['path'])
    if key in seen: raise ValueError('duplicate reference')
    seen.add(key)
    if item in m['files'] and (not isinstance(item.get('sha256'),str) or len(item['sha256'])!=64): raise ValueError('missing hash')
    if p==path: raise ValueError('manifest self hash forbidden')
    if not p.is_file(): missing.append(str(key)); continue
    if 'sha256' in item and hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']: raise ValueError('hash mismatch '+str(key))
   except (ValueError,RuntimeError) as e: errors.append(str(e))
  for item in m.get('documents',[]):
   try:
    p=locate(item)
    if not p.is_file(): missing.append(str(p)); continue
    doc=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(doc,dict): raise ValueError('document must be object')
    for field in item['required_fields']:
     if field not in doc: raise ValueError('document missing field '+field)
    if 'status_allowed' in item and doc.get('status') not in item['status_allowed']: raise ValueError('document invalid status')
   except (ValueError,TypeError,KeyError,OSError,RuntimeError) as e: errors.append(str(e))
 except (ValueError,TypeError,KeyError,OSError,RuntimeError) as e: errors.append(str(e))
 return (1 if errors else 2 if missing else 0),errors+['missing dependency '+x for x in missing]

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('kit','repo','sources'): p.add_argument('--'+name+'-root',required=True,type=pathlib.Path)
 a=p.parse_args(); code,messages=check(a.kit_root,a.repo_root,a.sources_root)
 print(json.dumps({'exit_code':code,'status':('INTEGRITY_OK','INCONSISTENT','DEPENDENCY_MISSING')[code],'messages':messages},ensure_ascii=False)); return code
if __name__=='__main__': sys.exit(main())

from pathlib import Path
import importlib.util,argparse,json,hashlib,subprocess,ast
from unittest.mock import patch
from types import SimpleNamespace
ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
spec=importlib.util.spec_from_file_location('budget_candidate',a.source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
names=list(dict.fromkeys([n for n,_ in m.FULL]+['unknown-control']))
rows=[]
for name in names:
 expected=1800 if name=='ui-visual-quality' else 900
 def invoke(*args,**kw):
  rows.append({'name':name,'expected':expected,'observed':kw['timeout']})
  return SimpleNamespace(stdout='synthetic controlled child',returncode=0)
 with patch.object(m.subprocess,'run',side_effect=invoke):result=m.run_check(name,['synthetic-child-not-executed'])
 assert result['result']=='PASS'
message_cases=[]
for name in ['ui-visual-quality','preflight']:
 expected=1800 if name=='ui-visual-quality' else 900
 with patch.object(m.subprocess,'run',side_effect=subprocess.TimeoutExpired(['synthetic-child'],expected,output=b'synthetic partial')):
  result=m.run_check(name,['synthetic-child-not-executed'])
 message_cases.append({'name':name,'expected':expected,'result':result,'matches':result['returncode']==124 and result['result']=='ENVIRONMENT_ERROR' and f'timeout apos {expected}s' in result['output_tail']})
failures=[r for r in rows if r['expected']!=r['observed']]
record={'sourceSha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'scope':'Actual run_check function with controlled subprocess spy/TimeoutExpired; not wall-clock/browser execution','rows':rows,'mismatches':failures,'timeoutMessageCases':message_cases}
a.out.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'checks':len(rows),'mismatches':failures,'sourceSha256':record['sourceSha256']}))
raise SystemExit(bool(failures) or any(not r['matches'] for r in message_cases))

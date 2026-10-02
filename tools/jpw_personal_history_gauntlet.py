#!/usr/bin/env python3
"""Freeze sources, execute 20 cases in 3 new processes, keep every attempt.
No case-wide/native acceptance follows from host subcriterion status.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
AREA=ROOT/'outputs/genetrix-personal-history'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def inputs():
    paths=set(p for p in (ROOT/'mt5/jpw-alavancagem-atual').rglob('*') if p.is_file())
    for pattern in ('tools/jpw_personal_history*.py','tools/personal_history_host/*','tools/jpw_genetrix*.py','tools/leverage_*.py','tools/build_leverage_package.py','tests/fixtures/genetrix-personal-history/*','docs/work/genetrix-personal-history/*.md','downloads/jpw-alavancagem-atual/manifest.json'):
        paths.update(p for p in ROOT.glob(pattern) if p.is_file())
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)}
def write_new(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--round',required=True);p.add_argument('--freeze-only',action='store_true');a=p.parse_args()
    if not a.round.isalnum():p.error('round must be alphanumeric')
    directory=AREA/a.round;freeze=directory/'FROZEN.json'
    if a.freeze_only:
        mapping=inputs();raw=json.dumps(mapping,sort_keys=True,separators=(',',':')).encode()
        write_new(freeze,{'schema':'jpw-personal-candidate-freeze/v1','round':a.round,'at':utc(),'classification':'CANDIDATE','version':'1.18.0','base':'1.17.0 RC2','fingerprint':hashlib.sha256(raw).hexdigest(),'sources':mapping,'native':'NOT_RUN','operational_acceptance':'NOT_RUN'})
        with zipfile.ZipFile(directory/'FROZEN-INPUTS.zip','x',zipfile.ZIP_DEFLATED) as z:
            for path,expected in mapping.items():
                content=(ROOT/path).read_bytes()
                if hashlib.sha256(content).hexdigest()!=expected:raise RuntimeError('Freeze changed while archiving')
                z.writestr(path,content)
        if inputs()!=mapping:raise RuntimeError('Freeze changed while archiving; revision invalid')
        print(freeze);return 0
    frozen=json.loads(freeze.read_text());mapping=frozen['sources']
    if inputs()!=mapping:raise RuntimeError('Frozen inputs changed; open another revision, do not reuse attempts')
    fixture=json.loads((ROOT/'tests/fixtures/genetrix-personal-history/acceptance-v1.json').read_text());attempts=[]
    for case in fixture['cases']:
        for index in range(1,4):
            out=directory/'attempts'/case['id']/f'attempt-{index}'
            if out.exists():raise RuntimeError('Attempt destination exists; preserved, no retry overwrite')
            out.mkdir(parents=True)
            command=[sys.executable,'tools/jpw_personal_history_test.py','--case',case['id'],'--output',str(out)]
            at=utc();r=subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (out/'runner.log').write_text(r.stdout)
            receipt_path=out/'receipt.json';receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
            attempts.append({'case':case['id'],'attempt':index,'at':at,'exit_code':r.returncode,'classification':receipt.get('classification','ENVIRONMENT_ERROR'),'receipt':str(receipt_path.relative_to(ROOT)),'receipt_sha256':digest(receipt_path) if receipt_path.exists() else None,'case_scopes':receipt.get('cases',[])})
            print(case['id'],index,attempts[-1]['classification'],flush=True)
            if inputs()!=mapping:
                write_new(directory/'INVALIDATED.json',{'at':utc(),'reason':'Inputs changed during gauntlet','attempts_preserved':attempts});return 2
    counts={}
    for attempt in attempts:counts[attempt['classification']]=counts.get(attempt['classification'],0)+1
    failed=any(x['exit_code']!=0 or x['classification']!='PASS' for x in attempts)
    # Preserve the failure boundary: environment/runner errors do not prove a product defect.
    classification='HOST_SCOPES_PASS'
    if failed:
        classification='PRODUCT_FAIL' if counts.get('PRODUCT_FAIL',0) else 'INCOMPLETE'
    write_new(directory/'GAUNTLET.json',{'schema':'jpw-personal-gauntlet/v1','round':a.round,'at':utc(),'fingerprint':frozen['fingerprint'],'classification':classification,'planned_cases':20,'planned_attempts':60,'executed_attempts':len(attempts),'counts':counts,'attempts':attempts,'sources_unchanged':inputs()==mapping,'full_acceptance':'NOT_RUN','native_compile_ex5_mt5':'NOT_RUN','limitations':'Each PASS applies only to executed host subcriteria, never whole-case/native approval. All attempts retained. No real account or trades.'})
    return 1 if failed else 0
if __name__=='__main__':raise SystemExit(main())

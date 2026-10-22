#!/usr/bin/env python3
"""Compatibility forward to the current independent planning contract.

No retired JPWFx API is treated as the active product. The executed target prints
its own case identities; this entrypoint does not count them a second time.
"""
import argparse,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--artifacts',type=Path);p.add_argument('--artifact',type=Path)
    p.add_argument('--baseline',action='store_true');p.add_argument('--skip-ui',action='store_true');p.add_argument('--only')
    a=p.parse_args()
    if a.baseline or a.only:p.error('Retired baseline/filter contracts are unavailable; use the preserved baseline tree or current suite identifiers.')
    target='planning_engine_test.js'
    if a.skip_ui:target='planning_state_test.js'
    node=os.environ.get('JP_WEALTH_NODE') or shutil.which('node') or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
    command=[sys.executable if target.endswith('.py') else node,str(a.root/'tools'/target)]
    print('Compatibility forward; underlying suite owns the following result:',flush=True)
    result=subprocess.run(command,cwd=a.root)
    artifact=a.artifact or (a.artifacts/'compatibility.json' if a.artifacts else None)
    if artifact:
        artifact.parent.mkdir(parents=True,exist_ok=True)
        paths=[a.root/'tools'/target,a.root/'src/js/30-accounting/06-planning/01-engine.js',a.root/'src/js/30-accounting/06-planning/02-state.js',a.root/'src/js/30-accounting/06-planning/03-ui.js']
        artifact.write_text(json.dumps({'delegatedTo':target,'exitCode':result.returncode,'status':'PASS' if result.returncode==0 else 'PRODUCT_FAIL','countsOwnedByTarget':True,'sourceHashes':{str(path.relative_to(a.root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}})+'\n')
    return result.returncode
if __name__=='__main__':raise SystemExit(main())

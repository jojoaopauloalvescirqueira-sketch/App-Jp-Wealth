from pathlib import Path
import sys,json,datetime,subprocess,os,hashlib
base=Path(__file__).resolve().parent
name=sys.argv[1];command=sys.argv[2:]
node='/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',JPW_NODE=node,JP_WEALTH_CHROMIUM='/Users/joaoalvescirqueira/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',PATH=str(Path(node).parent)+os.pathsep+env.get('PATH',''))
receipt={'command':command,'cwd':str(Path.cwd()),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'log':str(base/(name+'.log'))}
assert not (base/(name+'-command.json')).exists(), 'Preserve prior command receipt; use a new attempt name'
is_full=name=='full'
if is_full:
 receipt['freeze_sha256']=hashlib.sha256((base/'freeze.json').read_bytes()).hexdigest()
 check=subprocess.run([sys.executable,str(base/'release_protocol.py'),'verify'],env=env,capture_output=True,text=True)
 assert check.returncode==0, check.stdout+check.stderr
 receipt['frozen_before']=True
(base/(name+'-command.json')).write_text(json.dumps(receipt,indent=2)+'\n')
with (base/(name+'.log')).open('wb') as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env)
receipt.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=result.returncode)
if is_full:
 check=subprocess.run([sys.executable,str(base/'release_protocol.py'),'verify'],env=env,capture_output=True,text=True)
 receipt['frozen_after']=check.returncode==0
 receipt['post_verify_output']=check.stdout+check.stderr
(base/(name+'-command.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt));raise SystemExit(result.returncode if not is_full or receipt['frozen_after'] else 1)

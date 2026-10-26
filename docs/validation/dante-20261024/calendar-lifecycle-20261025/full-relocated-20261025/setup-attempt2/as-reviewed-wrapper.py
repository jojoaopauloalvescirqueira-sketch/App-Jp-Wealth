"""Run the unchanged official gate with only its fresh empty outputs in scratch.
No source, check, timeout, command, financial fixture or old artifact is edited.
"""
from pathlib import Path
import os, re, stat, json, signal, subprocess, sys, time, tempfile, hashlib, select
ROOT=Path('/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS')
OUT=Path('/private/tmp/jpw-dante-calendar-20261025')
PREFIX=re.compile(r'app-efficiency-full-\d{8}T\d{12}')

def redirect(parent, before, target):
    # Caller must stop its own newly spawned gate group before calling this.
    added=set(parent.iterdir())-before
    assert len(added)==1, ('Expected exactly one fresh gate output',list(added))
    source=added.pop()
    assert PREFIX.fullmatch(source.name) and source.parent==parent
    first=source.lstat()
    assert stat.S_ISDIR(first.st_mode) and not source.is_symlink()
    assert first.st_uid==os.geteuid() and source.resolve()==parent.resolve()/source.name
    assert not list(source.iterdir()), 'Never move, remove or overwrite nonempty artifacts'
    assert target.is_dir() and not target.is_symlink() and not list(target.iterdir())
    again=source.lstat()
    assert (first.st_ino,first.st_dev)==(again.st_ino,again.st_dev)
    source.rmdir()  # This run's own empty directory; no data are removed.
    try: source.symlink_to(target,target_is_directory=True)
    except BaseException:
        source.mkdir(exist_ok=False)
        raise
    assert source.is_symlink() and source.resolve()==target.resolve() and source.samefile(target)
    return {'logical':str(source),'resolved':str(source.resolve()),'priorInode':first.st_ino,
            'emptyOwnedFreshDirectoryOnly':True}

def selftest():
    rows=[]
    with tempfile.TemporaryDirectory(prefix='jpw-output-redirection-proof-') as temp:
        base=Path(temp)
        for kind in ['valid','nonempty','existing','symlink','wrong-name','multiple','none']:
            parent=base/kind/'outputs';parent.mkdir(parents=True);target=base/kind/'scratch';target.mkdir()
            source=parent/'app-efficiency-full-20261025T030000123456'
            if kind=='existing':source.mkdir()
            before=set(parent.iterdir())
            if kind not in ['existing','none']:
                if kind=='symlink':source.symlink_to(target,target_is_directory=True)
                elif kind=='wrong-name':source=parent/'user-files';source.mkdir()
                else:source.mkdir()
            if kind=='nonempty':(source/'keep.txt').write_text('KEEP')
            if kind=='multiple':(parent/'app-efficiency-full-20261025T030000654321').mkdir()
            if kind=='valid':
                record=redirect(parent,before,target);(source/'probe.txt').write_text('PROBE')
                assert (target/'probe.txt').read_text()=='PROBE';rows.append({'case':kind,'result':'PASS','evidence':record})
            else:
                try:redirect(parent,before,target)
                except AssertionError:rows.append({'case':kind,'result':'PASS','invalidInputRejected':True})
                else:raise AssertionError('Accepted invalid fixture '+kind)
                if kind=='nonempty':assert (source/'keep.txt').read_text()=='KEEP'
    (OUT/'redirection-selftest.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps({'cases':len(rows),'result':'PASS'}))

def run():
    before_inputs=json.loads((OUT/'frozen-inputs.json').read_text())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in before_inputs['files'].items())
    parent=ROOT/'tools/.artifacts';before=set(parent.iterdir())
    target=OUT/'full-relocated-evidence';target.mkdir(exist_ok=False)
    receipt=OUT/'full-relocated.json';assert not receipt.exists()
    command=[sys.executable,'-u','tools/quality_gate.py','--tier','full','--artifact',str(receipt)]
    env=dict(os.environ,PYTHONUNBUFFERED='1',JPW_NODE='/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node',JP_WEALTH_CHROMIUM='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',JPW_BASELINE_ROOT='/private/tmp/jpw-dante-20261024/source-baseline')
    proc=None;paused=False;mapping=None;start=time.monotonic();exitcode=None
    try:
        with (OUT/'full-relocated.log').open('w') as log:
            proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0,start_new_session=True)
            assert os.getpgid(proc.pid)==proc.pid
            for raw in proc.stdout:
                line=raw.decode('utf-8',errors='replace')
                log.write(line);log.flush();print(line.rstrip(),flush=True)
                if mapping is None:
                    assert line.startswith('[RUN] preflight:'), 'No intervention after the first check boundary'
                    os.killpg(proc.pid,signal.SIGSTOP);paused=True;handshake=time.monotonic()
                    members=[]
                    for attempt in range(50):
                        rows=subprocess.check_output(['ps','-axo','pid,ppid,pgid,stat,args'],text=True).splitlines()[1:]
                        members=[row.split(None,4) for row in rows if len(row.split(None,4))==5 and row.split(None,4)[2]==str(proc.pid)]
                        if members and all(row[3].startswith('T') for row in members):break
                        time.sleep(.01)
                    assert members and all(row[3].startswith('T') for row in members), ('Own gate group did not stop',members)
                    for member in members:
                        pid,ppid,pgid,state,args=member
                        assert pid==str(proc.pid) or 'tools/agent_preflight.py --mode audit --allow-dirty' in args or re.match(r'^(?:\S*/)?git ',args), ('Unexpected later check/consumer',member)
                    assert not select.select([proc.stdout.fileno()],[],[],0)[0], 'Further status already queued: missed first-check handshake'
                    mapping=redirect(parent,before,target)
                    mapping['stoppedGroupMembers']=members
                    os.killpg(proc.pid,signal.SIGCONT);paused=False
                    mapping['pauseSeconds']=round(time.monotonic()-handshake,6)
                    (OUT/'redirection-mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
            exitcode=proc.wait()
    except BaseException:
        if proc and proc.poll() is None:
            if paused:os.killpg(proc.pid,signal.SIGCONT);paused=False
            os.killpg(proc.pid,signal.SIGINT)
            try:proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=15)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=15)
        raise
    finally:
        unchanged=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in before_inputs['files'].items())
        (OUT/'full-relocated-command.json').write_text(json.dumps({'command':command,'mapping':mapping,'exit':exitcode,'seconds':round(time.monotonic()-start,3),'frozenInputs':len(before_inputs['files']),'sourceUnchanged':unchanged,'sourceEdits':False,'timeoutEdits':False,'criteriaEdits':False},indent=2)+'\n')
    assert unchanged and mapping is not None
    return exitcode

if __name__=='__main__':
    if sys.argv[1:]==['--selftest']:selftest()
    elif sys.argv[1:]==['--run']:sys.exit(run())
    else:raise SystemExit('Use --selftest or --run; never reuses output destinations.')

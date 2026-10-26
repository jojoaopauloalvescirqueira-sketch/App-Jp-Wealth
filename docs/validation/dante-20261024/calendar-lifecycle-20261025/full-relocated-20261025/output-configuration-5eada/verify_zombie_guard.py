#!/usr/bin/env python3
"""A0 wrapper guard revision; dummy filesystem + mocked guards only, no gate/browser/signals."""
from pathlib import Path
from unittest import mock
from types import SimpleNamespace
import ast,hashlib,json,os,shutil,tempfile,types
BASE=Path(__file__).resolve().parent
WRAPPER=BASE.parent/'redirect_full.py'
source=WRAPPER.read_bytes()
g=types.ModuleType('redirect_full_a0_snapshot');g.__file__=str(WRAPPER);g.__name__='redirect_full_a0_snapshot'
exec(compile(source,str(WRAPPER),'exec'),g.__dict__)
rows=[]
def ok(name,**details): rows.append(dict(case=name,result='PASS',**details))
def rejected(name,call,keep=None):
    try:call()
    except AssertionError:
        if keep:keep()
        ok(name,invalidInputRejected=True)
    else:raise AssertionError('Invalid input accepted: '+name)
with tempfile.TemporaryDirectory(prefix='independent-output-proof-',dir=BASE) as td:
    temp=Path(td)
    def setup(name):
        parent=temp/name/'outputs';parent.mkdir(parents=True)
        target=temp/name/'scratch';target.mkdir()
        return parent,target,parent/'app-efficiency-full-20261025T030000123456'
    p,t,s=setup('valid');before=set(p.iterdir());s.mkdir()
    mapping=g.redirect(p,before,t)
    assert s.is_symlink() and s.samefile(t) and s.resolve()==t.resolve()
    (s/'probe.txt').write_text('PROBE');assert (t/'probe.txt').read_text()=='PROBE'
    (t/'reverse.txt').write_text('REVERSE');assert (s/'reverse.txt').read_text()=='REVERSE'
    out=s/'ui-visual-quality';out.mkdir(exist_ok=False)
    profile=Path(tempfile.mkdtemp(prefix='native-proof-',dir=out));(profile/'Default').mkdir();(profile/'Default'/'state').write_text('SYNTHETIC')
    physical=profile.resolve();assert physical.is_relative_to(t.resolve())
    shutil.rmtree(profile);assert not physical.exists() and s.is_symlink() and s.samefile(t)
    ok('valid-bidirectional-write-profile-cleanup',logicalAndRealRecorded=bool(mapping.get('logical') and mapping.get('resolved')),samefile=True,profileChildRemoved=True,fullSymlinkRetained=True)
    for kind in ['nonempty-source','source-existing-before','source-symlink','source-file','wrong-name','multiple','none','target-nonempty','target-symlink','target-file']:
        p,t,s=setup(kind)
        if kind=='source-existing-before':s.mkdir();(s/'keep.txt').write_text('KEEP')
        before=set(p.iterdir())
        if kind not in ['source-existing-before','none']:
            if kind=='source-symlink':s.symlink_to(t,target_is_directory=True)
            elif kind=='source-file':s.write_text('KEEP')
            elif kind=='wrong-name':s=p/'user-files';s.mkdir();(s/'keep.txt').write_text('KEEP')
            else:s.mkdir()
        if kind=='nonempty-source':(s/'keep.txt').write_text('KEEP')
        if kind=='multiple':(p/'app-efficiency-full-20261025T030000654321').mkdir()
        if kind=='target-nonempty':(t/'keep.txt').write_text('KEEP')
        if kind=='target-symlink':
            t.rmdir();other=t.parent/'other';other.mkdir();t.symlink_to(other,target_is_directory=True)
        if kind=='target-file':t.rmdir();t.write_text('KEEP')
        keep_files={k:k.read_bytes() for k in temp.rglob('keep.txt')}
        rejected(kind,lambda:g.redirect(p,before,t))
        assert all(k.read_bytes()==v for k,v in keep_files.items())
        if kind in ['source-file','target-file']:assert (s if kind=='source-file' else t).read_text()=='KEEP'
    p,t,s=setup('wrong-owner');before=set(p.iterdir());s.mkdir()
    uid=os.geteuid()
    with mock.patch.object(g.os,'geteuid',return_value=uid+1):rejected('wrong-owner',lambda:g.redirect(p,before,t))
    assert s.is_dir() and not s.is_symlink()
    p,t,s=setup('changed-inode');before=set(p.iterdir());s.mkdir()
    real_lstat=Path.lstat;counts=[0]
    def changing_lstat(path,*a,**kw):
        result=real_lstat(path,*a,**kw)
        if path==s:
            counts[0]+=1
            if counts[0]==3:return SimpleNamespace(st_ino=result.st_ino+1,st_dev=result.st_dev,st_mode=result.st_mode,st_uid=result.st_uid)
        return result
    with mock.patch.object(Path,'lstat',changing_lstat):rejected('changed-inode',lambda:g.redirect(p,before,t))
    assert counts[0]>=3 and s.is_dir() and not s.is_symlink()
    p,t,s=setup('symlink-failure');before=set(p.iterdir());s.mkdir()
    real_symlink=Path.symlink_to
    def fail_symlink(path,*a,**kw):
        if path==s:raise OSError('SYNTHETIC symlink failure')
        return real_symlink(path,*a,**kw)
    with mock.patch.object(Path,'symlink_to',fail_symlink):
        try:g.redirect(p,before,t)
        except OSError:pass
        else:raise AssertionError('Expected symlink failure')
    assert s.is_dir() and not s.is_symlink() and not list(s.iterdir()) and not list(t.iterdir())
    ok('symlink-failure-restores-own-empty-directory',rollback=True)

# Execute the wrapper's actual handshake guard in memory, stopping before redirect.
# All signal/ps/select/sleep calls are mocked; no process or browser is started.
tree=ast.parse(source)
run_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
guard=next(n for n in ast.walk(run_node) if isinstance(n,ast.If) and ast.unparse(n.test)=='mapping is None')
cut=next(i for i,n in enumerate(guard.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='mapping' for t in n.targets))
fn=ast.FunctionDef(name='guard_probe',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='line'),ast.arg(arg='proc')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=guard.body[:cut]+[ast.Return(value=ast.Name(id='members',ctx=ast.Load()))],decorator_list=[])
module=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]))
exec(compile(module,'<actual-wrapper-handshake-guard>','exec'),g.__dict__)
pid=424242
proc=SimpleNamespace(pid=pid,stdout=SimpleNamespace(fileno=lambda:42))
header='PID PPID PGID STAT ARGS\n'
parent=f'{pid} 1 {pid} T python tools/quality_gate.py --tier full\n'
preflight=f'{pid+1} {pid} {pid} T python tools/agent_preflight.py --mode audit --allow-dirty\n'
git=f'{pid+2} {pid+1} {pid} T /usr/bin/git status --porcelain=v1\n'
scenarios=[
 ('handshake-valid-stopped-own-group',[header+parent+preflight+git],False,True,'[RUN] preflight: python tools/agent_preflight.py'),
 ('handshake-calendar-already-active',[header+parent+f'{pid+1} {pid} {pid} T python tools/calendar_agenda_test.py\n'],False,False,None),
 ('handshake-browser-already-active',[header+parent+f'{pid+1} {pid} {pid} T /Applications/Google Chrome.app/Chrome\n'],False,False,None),
 ('handshake-child-not-stopped',[header+parent+preflight.replace(' T ',' S ')],False,False,None),
 ('handshake-parent-not-stopped',[header+parent.replace(' T ',' S ')],False,False,None),
 ('handshake-no-own-group',[header],False,False,None),
 ('handshake-additional-status-queued',[header+parent+preflight],True,False,None),
 ('handshake-first-line-is-later-check',[header+parent],False,False,'[RUN] calendar-agenda: python'),
 ('handshake-wrong-group',[header+parent.replace(str(pid)+' T',str(pid+99)+' T')],False,False,None),
 ('handshake-unrelated-running-group-ignored',[header+parent+preflight+'999 1 999 S unrelated\n'],False,True,None),
 ('handshake-stop-transition',[header+parent.replace(' T ',' S '),header+parent+preflight],False,True,None),
 ('handshake-zombie-rejected',[header+parent+preflight.replace(' T ',' Z ')],False,False,None),
]

zombie=f'{pid+1} {pid} {pid} Z <defunct>\n'
scenarios += [
 ('z-parent-stopped-direct-defunct-accepted',[header+parent+zombie],False,True,None),
 ('z-parent-zombie-rejected',[header+parent.replace(' T ',' Z ')+zombie],False,False,None),
 ('z-indirect-defunct-child-rejected',[header+parent+preflight+f'{pid+2} {pid+1} {pid} Z <defunct>\n'],False,False,None),
 ('z-identified-consumer-rejected',[header+parent+f'{pid+1} {pid} {pid} Z python tools/calendar_agenda_test.py\n'],False,False,None),
 ('z-unrecognized-command-rejected',[header+parent+f'{pid+1} {pid} {pid} Z python\n'],False,False,None),
 ('z-direct-defunct-plus-active-consumer-rejected',[header+parent+zombie+f'{pid+2} {pid} {pid} T python tools/ui_visual_quality_test.py\n'],False,False,None),
 ('z-direct-defunct-plus-queued-status-rejected',[header+parent+zombie],True,False,None),
 ('z-direct-defunct-parent-running-rejected',[header+parent.replace(' T ',' S ')+zombie],False,False,None),
 ('z-direct-defunct-with-preflight-stopped-accepted',[header+parent+zombie+preflight.replace(str(pid+1),str(pid+3),1)],False,True,None),
]

for name,snapshots,queued,accepted,line in scenarios:
    calls=[];seen=[0]
    def fake_ps(*a,**kw):
        i=min(seen[0],len(snapshots)-1);seen[0]+=1;return snapshots[i]
    with mock.patch.object(g.os,'killpg',side_effect=lambda group,sig:calls.append((group,int(sig)))),mock.patch.object(g.subprocess,'check_output',side_effect=fake_ps),mock.patch.object(g.select,'select',return_value=([42] if queued else [],[],[])),mock.patch.object(g.time,'sleep',return_value=None):
        try:members=g.guard_probe(line or '[RUN] preflight: python tools/agent_preflight.py',proc)
        except AssertionError:
            assert not accepted,name
        else:
            assert accepted and members,name
    assert all(group==pid for group,sig in calls),name
    if line and not line.startswith('[RUN] preflight:'):assert not calls
    else:assert calls==[(pid,int(g.signal.SIGSTOP))],name
    ok(name,accepted=accepted,psSnapshots=seen[0],signalsMocked=True)


# Exercise exact first-status-after-resume assertion and final EOF assertion.
post=next(n for n in ast.walk(run_node) if isinstance(n,ast.If) and ast.unparse(n.test)=='not preflight_verified')
post_fn=ast.FunctionDef(name='post_resume_probe',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='line')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=[ast.Assign(targets=[ast.Name(id='preflight_verified',ctx=ast.Store())],value=ast.Constant(False))]+post.body+[ast.Return(value=ast.Name(id='preflight_verified',ctx=ast.Load()))],decorator_list=[])
exec(compile(ast.fix_missing_locations(ast.Module(body=[post_fn],type_ignores=[])),'<actual-wrapper-post-resume>','exec'),g.__dict__)
for name,line,accepted in [
 ('post-official-pass-preflight-accepted','[PASS] preflight (0.314s)\n',True),
 ('post-product-fail-rejected','[PRODUCT_FAIL] preflight (0.314s)\n',False),
 ('post-environment-error-rejected','[ENVIRONMENT_ERROR] preflight (0.314s)\n',False),
 ('post-harness-fail-rejected','[TEST_HARNESS_FAIL] preflight (0.314s)\n',False),
 ('post-later-run-rejected','[RUN] structure: python tools/validate_project.py\n',False),
 ('post-wrong-check-pass-rejected','[PASS] structure (0.314s)\n',False),
 ('post-prefix-collision-rejected','[PASS] preflight-other (0.314s)\n',False),
 ('post-empty-line-rejected','\n',False),
]:
    try:value=g.post_resume_probe(line)
    except AssertionError:assert not accepted,name
    else:assert accepted and value is True,name
    ok(name,accepted=accepted)
last_assert=next(n for n in reversed(run_node.body) if isinstance(n,ast.Assert))
end_fn=ast.FunctionDef(name='end_probe',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='preflight_verified')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=[ast.Assign(targets=[ast.Name(id='unchanged',ctx=ast.Store())],value=ast.Constant(True)),ast.Assign(targets=[ast.Name(id='mapping',ctx=ast.Store())],value=ast.Dict(keys=[],values=[])),last_assert,ast.Return(value=ast.Constant(True))],decorator_list=[])
exec(compile(ast.fix_missing_locations(ast.Module(body=[end_fn],type_ignores=[])),'<actual-wrapper-final-guard>','exec'),g.__dict__)
try:g.end_probe(False)
except AssertionError:ok('post-eof-without-pass-rejected',accepted=False)
else:raise AssertionError('EOF without preflight accepted')
assert g.end_probe(True);ok('post-final-requires-verified-pass',accepted=True)
# Pure helper rejects rows not belonging to this PGID, independent of caller filter.
assert not g.inert_group([[str(pid),'1',str(pid+1),'T','gate']],pid)
ok('z-helper-wrong-pgid-rejected')

root=g.ROOT
frozen=json.loads((BASE.parent/'frozen-inputs.json').read_text())
changed=[p for p,h in frozen['files'].items() if not (root/p).is_file() or hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
assert not changed
result={'classification':'PASS','scope':'dummy filesystem only; wrapper run/selftest and gate/browser not called','wrapper_sha256':hashlib.sha256(source).hexdigest(),'cases':rows,'count':len(rows),'frozen':{'checked':len(frozen['files']),'changed':changed},'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(BASE/'zombie-guard-proof.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'classification':result['classification'],'cases':len(rows),'wrapper_sha256':result['wrapper_sha256'],'frozen':result['frozen']}))

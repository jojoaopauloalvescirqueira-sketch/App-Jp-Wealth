from pathlib import Path, PurePosixPath
from io import BytesIO
from datetime import datetime, timezone
import hashlib, json, re, subprocess, sys, tempfile, shutil, zipfile
sys.dont_write_bytecode = True
ROOT=Path('/private/tmp/jpw-stoikus-renaming-20261012')
OUT=Path('/private/tmp/jpw-stoikus-usability-evidence-20261013/final-code-critic')
PYTHON='/private/tmp/jpw-quality-audit-20261012-01a131dc/runtime/bin/python'
PRODUCT=Path('mt5/jpw-alavancagem-atual')
SCRIPTPATH='MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5'
GUIDE='STOIKUS_USO_DIARIO.md'
sha=lambda b: hashlib.sha256(b).hexdigest()
receipt={'timestampUTC':datetime.now(timezone.utc).isoformat(),'root':str(ROOT),'nativeCompilation':'NOT_RUN','nativeRuntime':'NOT_RUN','checks':{},'mutants':[]}
oldraw=(ROOT/'downloads/jpw-alavancagem-atual/JPW_Stoikus_Fontes_v1.22.0.zip').read_bytes()
assert len(oldraw)==763854 and sha(oldraw)=='79d481a624d37dccb2237f37db7a35b2746a0b8281d183b1ce30fcba0bfc9c95'
old=zipfile.ZipFile(BytesIO(oldraw))
oldgen=(ROOT/'downloads/jpw-alavancagem-atual/JPW_Genetrix_Fontes_v1.21.2.zip').read_bytes()
assert len(oldgen)==760092 and sha(oldgen)=='a9a77be170036747fec8322fdba7d80bd6256fbcae87e4c6dadb1348ff916261'
receipt['checks']['historicalDigests']={'stoikus1220':sha(oldraw),'genetrix1212':sha(oldgen)}
programs=['MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5','MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5','MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5']
inputs={};labels={}
pattern=r'^input\s+(?!group\b)(\w+)\s+(\w+)\s*=\s*([^;]+);'
for name in programs:
    source=(ROOT/PRODUCT/name).read_text()
    before=re.findall(pattern,old.read(name).decode(),re.M)
    after=re.findall(pattern,source,re.M)
    assert before==after,(name,before,after)
    inputs[name]=after
    labels[name]=re.findall(r'^input\s+(?!group\b)[^\n]+;\s*//\s*([^\n]+)',source,re.M)
    assert len(labels[name])==len(after)
    assert all(len(label)<=63 for label in labels[name]),(name,labels[name])
assert sum(map(len,inputs.values()))==20
receipt['checks']['publicInputs']=inputs
receipt['checks']['displayLabels']={'labels':labels,'maximumCharacters':max(len(s) for v in labels.values() for s in v)}
mathfiles=[];nocudafiles=[];changed=[]
for name in old.namelist():
    if name.endswith('.mqh') and '/JPW_NoCuda_' in name:
        assert (ROOT/PRODUCT/name).read_bytes()==old.read(name),name
        nocudafiles.append(name)
    if name.endswith('_Core.mqh') and '/JPW_Alavancagem_' in name:
        assert (ROOT/PRODUCT/name).read_bytes()==old.read(name),name
        mathfiles.append(name)
    if name.endswith(('.mqh','.mq5')) and (ROOT/PRODUCT/name).read_bytes()!=old.read(name):changed.append(name)
version=(ROOT/PRODUCT/'MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh').read_text()
assert '#define JPW_CALCULATION_VERSION "1.9.0"' in version
receipt['checks']['unchangedNoCudaLibraries']=nocudafiles
receipt['checks']['unchangedMathCores']=mathfiles
receipt['checks']['changedMqlVs1220']=changed
manifest=json.loads((ROOT/'downloads/jpw-alavancagem-atual/manifest.json').read_text())
assert manifest['nativeArtifact'] is None
assert manifest['validation']['compilation']['status']=='pending'
assert manifest['validation']['terminal']['status']=='pending'
assert not manifest['downloads']['compiled']['available']
new={}
for kind,count,nprog,expectedsha,expectedbytes in [('source',135,34,'03ccb37824175511108b36e9abb5c9fa0dc28d89a338caea1dc7bf02508b9cae',773801),('dailySource',82,4,'5b2c7ca40736dda976fe97a91a2677d190eb1ccfdf9527703fd471ee702a11e5',441516)]:
    entry=manifest['downloads'][kind];raw=(ROOT/entry['path']).read_bytes();assert sha(raw)==expectedsha==entry['sha256'];assert len(raw)==expectedbytes==entry['bytes']
    archive=zipfile.ZipFile(BytesIO(raw));names=archive.namelist();assert archive.testzip() is None;assert len(names)==len(set(names))==count;assert sum(n.endswith('.mq5') for n in names)==nprog
    assert not any(n.endswith('.ex5') for n in names)
    for name in names:
        relative=PurePosixPath(name);assert relative.as_posix()==name and not relative.is_absolute() and '..' not in relative.parts
        member=GUIDE if name=='LEIA_PRIMEIRO.md' else name
        assert archive.read(name)==(ROOT/PRODUCT/member).read_bytes(),name
    new[kind]=set(names)
    receipt['checks'][kind]={'sha256':sha(raw),'bytes':len(raw),'members':len(names),'programs':nprog,'sourceParity':True}
assert new['source']==set(old.namelist())|{SCRIPTPATH,GUIDE}
assert {n for n in new['dailySource'] if n.endswith('.mq5')}==set(programs)|{SCRIPTPATH}
assert not any(re.search(r'Tests|Lab|Supervisor|Accountant\.mq5|Observer\.mq5',n) for n in new['dailySource'])
# Compute closure independently from ZIP bytes, starting at four exact programs.
dailyraw=(ROOT/manifest['downloads']['dailySource']['path']).read_bytes();daily=zipfile.ZipFile(BytesIO(dailyraw))
pending=list(set(programs)|{SCRIPTPATH});seen=set()
while pending:
    name=pending.pop()
    if name in seen:continue
    seen.add(name);assert name in new['dailySource'],name
    if not name.endswith(('.mq5','.mqh')):continue
    text=daily.read(name).decode()
    # No trading API may be called by any member in this runtime closure.
    stripped=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
    assert not re.search(r'\b(OrderSend|OrderSendAsync)\s*\(',stripped),name
    for include in re.findall(r'^\s*#include\s*<JPWealth[\\/]([^>]+)>',text,re.M):pending.append('MQL5/Include/JPWealth/'+include.replace('\\','/'))
    for include in re.findall(r'^\s*#include\s*"([^"\n]+)"',text,re.M):pending.append(str(PurePosixPath(name).parent/include.replace('\\','/')))
    for resource in re.findall(r'^\s*#resource\s*"([^"\n]+)"',text,re.M):pending.append('MQL5/'+re.sub('/+', '/',resource.replace('\\','/')).lstrip('/'))
assert seen|{'LEIA_PRIMEIRO.md'}==new['dailySource']
receipt['checks']['dailyClosureMembers']=len(seen)
# Negative probes of the shipped startup judge, only in independent temporary fixtures.
script=(ROOT/PRODUCT/SCRIPTPATH).read_text()
mutations=[('relative_icustom',script.replace('"\\\\Indicators\\\\JPWealth\\\\','"JPWealth\\\\')),
('skip_presence_gate',script.replace('if(copies>0)','if(copies>999)')),
('omit_health_boundary',script.replace('A listagem não confirma funcionamento ou compatibilidade.','')),
('omit_release_warning',script.replace('; confira versão e dados"+release_notice','; confira versão e dados"'))]
for name,mutated in mutations:
    assert mutated!=script,name
    with tempfile.TemporaryDirectory(prefix='critic-startup-negative-') as folder:
        root=Path(folder)
        for member in programs+[SCRIPTPATH,'MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh']:
            target=root/PRODUCT/member;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/PRODUCT/member).read_bytes())
        (root/PRODUCT/SCRIPTPATH).write_text(mutated)
        result=subprocess.run([PYTHON,str(ROOT/'tools/stoikus_startup_test.py'),'--root',str(root)],capture_output=True,text=True,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'})
        assert result.returncode!=0,name
        receipt['mutants'].append({'mutation':name,'rejected':True,'exitCode':result.returncode,'output':result.stdout+result.stderr})
receipt['outcome']='PASS'
receipt['limits']='Independent byte/contracts/closure checks and host negative probes only. The shipped C++ harness replaces MT5 APIs; it cannot prove MQL5 compilation, chart lifetime, native indicator handlers, rendering, DPI, real handle reference ownership, scheduling, or account IO.'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'independent-audit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print('PASS independent baseline input comparison: 20; labels <=63 characters; unchanged NoCuda/math cores; exact SDK 135/34 and daily 82/4; full dependency closure; immutable histories; four rejected startup mutants. Native compile/runtime NOT_RUN.')

from pathlib import Path
import ast,copy,hashlib,json,types
B=Path(__file__).resolve().parent
R=Path('/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS')
old=(R/'tools/ui_visual_quality_test.py').read_text();new=(B/'ui_visual_quality_test.py.proposed').read_text()
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
a,b=ast.parse(old),ast.parse(new)
funcs=lambda t:{n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
af,bf=funcs(a),funcs(b)
changed=[k for k in af if ast.dump(af[k])!=ast.dump(bf[k])]
assert changed==['centered','controls_geometry']
for k in changed:
 assert [ast.dump(n) for n in ast.walk(af[k]) if isinstance(n,ast.Assert)]==[ast.dump(n) for n in ast.walk(bf[k]) if isinstance(n,ast.Assert)]
# The original content oracle is identical and reused within the new snapshot.
def content(t):return next(n.value.value for n in t.body if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='CONTENT_GEOMETRY' for v in n.targets))
assert content(a)==content(b)
class Count:
 def __init__(self,n):self.n=n
 def count(self):return self.n
class Control:
 def __init__(self,data,close=False,cuts=None,n=1):self.data=data;self.close=close;self.cuts=cuts or [];self.n=n;self.calls=[]
 def count(self):self.calls.append('count');return self.n
 def locator(self,s):assert s=='svg';self.calls.append('svgCount');return Count(self.data['svg'])
 def evaluate(self,s):
  self.calls.append('evaluate')
  if 'scrollIntoView' in s:return None
  if s==content(a):return copy.deepcopy(self.data)
  if "const geometry=(" in s:return dict(geometry=copy.deepcopy(self.data),isClose=self.close,cuts=self.cuts[:])
  if "el.matches('.pl-close,.risk-close')" in s:return self.close
  if 'return bad' in s:return self.cuts[:]
  raise AssertionError('Unexpected measurement script')
 def bounding_box(self):self.calls.append('boundingBox');return copy.deepcopy(self.data['outer'])
class Collection:
 def __init__(self,c):self.c=c
 def count(self):return 1
 def nth(self,i):assert i==0;return self.c
class Dialog:
 def __init__(self,order):self.order=order
 def count(self):return 1
 def evaluate_all(self,s):return self.order
class Page:
 def __init__(self,c,order):self.c=c;self.order=order
 def locator(self,s):return Collection(self.c) if s.endswith(' button:visible') else Dialog(self.order)
class Planning:
 def __init__(self,c):self.c=c
 def settle(self,page):self.c.calls.append('twoRAF')
def namespace(t,c):
 ns={'TOLERANCE':2,'EPSILON':.25,'CONTENT_GEOMETRY':content(t),'planning':Planning(c),'selector_geometry':lambda *args:[]}
 exec(compile(ast.Module(body=[funcs(t)['centered'],funcs(t)['controls_geometry']],type_ignores=[]),'<actual-functions>','exec'),ns)
 return ns
box={'left':0,'right':44,'top':0,'bottom':44,'width':44,'height':44}
text={'left':10,'right':34,'top':12,'bottom':32}
valid=dict(outer=box,text=text,ink=None,svg=0,label='Valid',textRects=[],textAlign='center',declaredLeftInset=0)
scenarios=[]
def add(name,change=lambda d:None,close=False,cuts=None,n=1,order=None,accept=True):
 d=copy.deepcopy(valid);change(d);scenarios.append((name,d,close,cuts,n,order,accept))
add('valid-text');add('text-shift5',lambda d:d['text'].update(left=15,right=39),accept=False)
add('no-text',lambda d:d.update(text=None),accept=False)
add('zero-target',lambda d:d['outer'].update(width=0),accept=False)
add('small-accessible-target',lambda d:(d['outer'].update(right=23,width=23),d['text'].update(left=5,right=18)),accept=False)
add('ancestor-clipping',cuts=['vertical:owner'],accept=False)
def svg(d):d.update(svg=1,ink=dict(left=18,right=26,top=18,bottom=26))
add('valid-close-svg',svg,close=True)
add('svg-shift5',lambda d:(svg(d),d['ink'].update(left=23,right=31)),close=True,accept=False)
add('missing-ink',lambda d:d.update(svg=1),accept=False)
add('close-size20',lambda d:(svg(d),d['outer'].update(right=20,bottom=20,width=20,height=20)),close=True,accept=False)
add('close-no-label',lambda d:(svg(d),d.update(label='')),close=True,accept=False)
add('multiple-svg-close',lambda d:(svg(d),d.update(svg=2)),close=True,accept=False)
add('zero-locator',n=0,accept=False);add('multiple-locator',n=2,accept=False)
add('positive-tabindex',order=[dict(count=1,positive=['bad'],footer=[])],accept=False)
add('footer-order',order=[dict(count=2,positive=[],footer=[dict(x=5,y=10),dict(x=0,y=10)])],accept=False)
rows=[]
for name,d,close,cuts,n,order,accept in scenarios:
 outcomes=[]
 for tree in [a,b]:
  c=Control(copy.deepcopy(d),close,cuts,n);ns=namespace(tree,c);p=Page(c,order or [dict(count=1,positive=[],footer=[])])
  try:value=ns['controls_geometry'](p)
  except AssertionError as error:outcomes.append(dict(accepted=False,error=str(error),calls=c.calls))
  else:outcomes.append(dict(accepted=True,value=value,calls=c.calls))
 assert outcomes[0]['accepted']==outcomes[1]['accepted']==accept,(name,outcomes)
 if accept:assert outcomes[0]['value']==outcomes[1]['value'],name
 assert outcomes[0]['calls'].count('twoRAF')==outcomes[1]['calls'].count('twoRAF')==1,name
 if name=='valid-text':assert len(outcomes[0]['calls'])==8 and len(outcomes[1]['calls'])==4,outcomes
 rows.append(dict(case=name,matched=True,accepted=accept,originalCalls=len(outcomes[0]['calls']),candidateCalls=len(outcomes[1]['calls'])))
# Locator cardinality cannot be bypassed by explicitly supplied measurement.
for n in [0,2]:
 c=Control(copy.deepcopy(valid),n=n);ns=namespace(b,c)
 try:ns['centered'](c,measurement=copy.deepcopy(valid))
 except AssertionError:pass
 else:raise AssertionError('Measurement bypassed cardinality')
 rows.append(dict(case='provided-measurement-cardinality-'+str(n),matched=True,accepted=False))
frozen=json.loads((B.parent/'frozen-inputs.json').read_text());drift=[p for p,h in frozen['files'].items() if not (R/p).is_file() or hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];assert not drift
result=dict(kind='IN_MEMORY_DECISION_AND_STATIC_ONLY_NOT_BROWSER',source_sha256=sha(old),candidate_sha256=sha(new),changed_functions=changed,assert_AST_identical=True,content_geometry_identical=True,controls=rows,count=len(rows),frozenInputs=len(frozen['files']),drift=drift,limitations=['Browser DOM snapshot and bounding_box equivalence NOT_RUN','413-case candidate runtime and performance NOT_RUN','Fake adapters supply measurement dictionaries; they do not prove browser layout'])
(B/'independent-static-and-decision.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['kind','source_sha256','candidate_sha256','count','frozenInputs','drift']}))

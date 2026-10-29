"""Serve only the old route label in RAM to the unchanged current lifecycle judge."""
from pathlib import Path
import sys,json,hashlib,tarfile
ROOT=Path('/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS')
sys.path.insert(0,str(ROOT/'tools'))
from playwright.sync_api import Page
import contextual_sidebar_test as judge
path=ROOT/'index.html'
before=path.read_bytes()
text=before.decode()
old='<span class="nav-sub-item-title">Caixa Anual</span>'
assert text.count(old)==1
mutant=text.replace(old,'<span class="nav-sub-item-title">Contabilidade</span>')
assert hashlib.sha256((ROOT/'tools/contextual_sidebar_test.py').read_bytes()).hexdigest()=='137039c2b53065acaa72f61cf01f8352ee16d1fd4223029f0a1e47afd6541493'
baseline='--baseline-judge' in sys.argv
if baseline:sys.argv.remove('--baseline-judge')
original=Page.route
served=[]
effective_judge=hashlib.sha256((ROOT/'tools/contextual_sidebar_test.py').read_bytes()).hexdigest()
def register(page,url,handler,*args,**kwargs):
    def route(request):
        if '/index.html' in request.request.url:
            served.append(request.request.url)
            request.fulfill(status=200,content_type='text/html',body=mutant)
        else:handler(request)
    return original(page,url,route,*args,**kwargs)
Page.route=register
try:
    if baseline:
        with tarfile.open('/private/tmp/jpw-caixa-anual-review-20261028/baseline-pending.tar.gz') as archive:
            oldjudge=archive.extractfile('tools/contextual_sidebar_test.py').read()
        expected=json.loads(Path('/private/tmp/jpw-caixa-anual-review-20261028/baseline-hashes.json').read_text())['tools/contextual_sidebar_test.py']
        assert hashlib.sha256(oldjudge).hexdigest()==expected
        effective_judge=expected
        namespace={'__name__':'baseline_judge_read_only','__file__':str(ROOT/'tools/contextual_sidebar_test.py')}
        exec(compile(oldjudge,str(ROOT/'tools/contextual_sidebar_test.py'),'exec'),namespace)
        namespace['main']()
    else:judge.main()
finally:
    Page.route=original
    assert path.read_bytes()==before
    print(json.dumps({'baselineJudge':baseline,'effectiveJudgeSha256':effective_judge,'mutantPath':'index.html menu-label only','inMemoryOldLabel':True,'mutatedResponses':len(served),'diskUnchanged':True}),flush=True)

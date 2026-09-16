#!/usr/bin/env python3
"""Synthetic, isolated backup bank. Outputs must be outside the product tree."""
import argparse, copy, hashlib, html, json, subprocess, sys, threading, traceback
from datetime import datetime, timezone
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
import backup_reliability_test as br
from browser_bootstrap_fixture import wait_bootstrap
from fx_consolidated_storage_test import SEED

ROOT = Path(__file__).resolve().parents[1]
GOALS = ['Contas, operações, históricos e Consolidado FX', 'Planejamento, Finanças Pessoais e Alladin',
         'Notas, pastas, NoCoda e Pivots', 'Tema', 'Nome e foto de perfil',
         'Widgets, navegação, fonte e marca', 'Aparência e posição de Notas', 'Galton', 'Rascunhos']
PREFS = r'''() => {
 S.theme='light';S.syntheticBackupExtension={label:'TESTE — DADOS FICTÍCIOS',preserved:'BR-UNKNOWN-FIELD'};
 S.fxPlanning.plan=fxCreatePlan({name:'TESTE — Plano fictício',now:'2026-01-01T12:00:00Z',assumptions:{startMonth:'2026-01',horizonMonths:12,initialBalanceUsd:1000,defaultMonthlyReturn:0.01,projectedFxRate:5}});
 const prefs={jpwealth_local_profile_v1:JSON.stringify({schemaVersion:1,displayName:'TESTE — DADOS FICTÍCIOS',avatarDataUrl:SETTINGS_PROFILE_AVATARS[0].avatarDataUrl}),
 jpw_fs:'2',jpw_expl:'off',jpw_rail:'collapsed',jpw_nav:'pill',jpw_nav_layout:'topbar',
 jpw_nav_order:JSON.stringify({schemaVersion:1,order:['alladin','forex','personal-finance','research','dashboard']}),
 jpwealth_v9_icon_choice:'secondary',jpwealth_v9_icon_theme:'dark',
 'jpwealth.ui.widgetLayouts.v6':JSON.stringify(dashLayoutNormalizeV6(null)),
 jpwealth_notes_launcher_position_v1:JSON.stringify({schemaVersion:1,x:0.5,y:0.8}),
 jpwealth_notes_appearance_v1:JSON.stringify({schemaVersion:1,theme:'dark',density:'compact',preview:'show',sidebar:'hide',reading:'full',text:'large'}),
 jpwealth_galton_preferences_v1:JSON.stringify({schemaVersion:1,preset:'idealized',speed:2,showTheory:false,seed:123,config:{}})};
 Object.entries(prefs).forEach(([k,v])=>localStorage.setItem(k,v));
 if(save()!==true)throw Error('Fixture checkpoint refused');
 mvpNotesUI.draft={content:'TESTE — Nota ainda não salva',folderId:null,tags:'teste'};mvpNotesUI.draftDirty=true;
 const f=document.createElement('textarea');f.id='bankPending';f.setAttribute('aria-label','Formulário de teste');f.value='TESTE — Formulário pendente';document.body.append(f);f.dispatchEvent(new Event('input',{bubbles:true}));
 S.onboarding.investorPassword='BANK_SECRET_SENTINEL';
}'''

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def translate_path(self, path):
        # Portable preview resolves the same bundled assets as the existing browser tests.
        if path.startswith('/dist/assets/'):
            path=path.replace('/dist/assets/', '/assets/', 1)
        return super().translate_path(path)

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def identity():
    files = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    return {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files if (ROOT/f).is_file()}

def differences(a,b,path='$'):
    if type(a)!=type(b):return [{'path':path,'expected':a,'observed':b}]
    if isinstance(a,dict):
        out=[]
        for k in sorted(a.keys()|b.keys()):
            if k not in a or k not in b:out.append({'path':path+'.'+k,'expected':a.get(k,'<absent>'),'observed':b.get(k,'<absent>')})
            else:out.extend(differences(a[k],b[k],path+'.'+k))
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [{'path':path+'.length','expected':len(a),'observed':len(b)}]
        return sum((differences(x,y,f'{path}[{i}]') for i,(x,y) in enumerate(zip(a,b))),[])
    return [] if a==b else [{'path':path,'expected':a,'observed':b}]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args()
    out=args.output.resolve()
    if out.is_relative_to(ROOT) or out.exists():ap.error('Use a NEW directory outside the product')
    out.mkdir(parents=True);(out/'validos').mkdir();(out/'invalidos').mkdir();(out/'capturas').mkdir()
    before=identity();report={'startedAt':datetime.now(timezone.utc).isoformat(),'build':(ROOT/'build-id.js').read_text().split("'")[1],'cases':[], 'goals':{},'sourcesBefore':before}
    def check(name,goals,expected,observed):
        delta=differences(expected,observed)
        report['cases'].append({'name':name,'goals':goals,'result':'PRODUCT_FAIL' if delta else 'PASS','expected':expected,'observed':observed,'differences':delta})
        print(report['cases'][-1]['result'],name,flush=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/'
    helper=br.load(ROOT,'storage_governance_test')
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            a=br.prepare(helper,browser,url);a.evaluate('''() => {let n=123;Math.random=()=>((n=(1664525*n+1013904223)>>>0)/4294967296);let id=0;crypto.randomUUID=()=>('00000000-0000-4000-8000-'+String(++id).padStart(12,'0'));}''');a.evaluate(SEED);a.evaluate('async()=>await __import()');a.evaluate(br.PREPARE)
            seedcase=br.Case('seed');br.roundtrip(seedcase,a,helper,browser,url,ROOT)
            check('Pré-condições da fixture multimódulo',[1,2,3],True,all(c['result']=='PASS' for c in seedcase.checks))
            a.evaluate(PREFS)
            payload=a.evaluate("async()=>JSON.parse(await dgBuildBackupBlob(1,'TESTE-completo.json','2026-09-16T12:00:00Z').text())")
            check('Credencial sintética excluída',[],False,'BANK_SECRET_SENTINEL' in json.dumps(payload))
            dump(out/'validos/completo-galeria.json',payload)
            custom=copy.deepcopy(payload)
            pic=a.evaluate("()=>{const c=document.createElement('canvas');c.width=c.height=128;const x=c.getContext('2d');x.fillStyle='#a00010';x.fillRect(0,0,128,128);x.fillStyle='white';x.font='bold 30px sans-serif';x.fillText('TESTE',10,72);return c.toDataURL('image/jpeg',0.85)}")
            profile=json.loads(custom['workspace']['preferences']['jpwealth_local_profile_v1']);profile['avatarDataUrl']=pic
            custom['workspace']['preferences']['jpwealth_local_profile_v1']=json.dumps(profile,ensure_ascii=False,separators=(',',':'))
            dump(out/'validos/completo-foto-personalizada.json',custom)
            legacy=copy.deepcopy(payload);legacy.pop('workspace');legacy['state'].pop('workspaceRecovery',None);dump(out/'validos/legado-sem-workspace.json',legacy)
            (out/'invalidos/corrompido.json').write_text('{"tipo":')
            invalid=copy.deepcopy(payload);invalid['workspace']['schemaVersion']=999;dump(out/'invalidos/schema-incompativel.json',invalid)
            dump(out/'esperado.json',{'label':'TESTE — DADOS FICTÍCIOS','state':payload['state'],'workspace':payload['workspace']})
            for entry in ['index.html','dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']:
                for variant,data in [('galeria',payload),('personalizada',custom)]:
                    tag=('modular' if entry=='index.html' else 'portatil')+'-'+variant
                    b=br.prepare(helper,browser,url+entry)
                    b.locator('#importFullBackupInput').set_input_files({'name':'TESTE.json','mimeType':'application/json','buffer':json.dumps(data).encode()})
                    b.wait_for_function("__br.alerts.some(t=>t.includes('importado com sucesso'))")
                    b.reload();wait_bootstrap(b);b.evaluate('closeModal();window.__onbShown=true')
                    actual=b.evaluate('structuredClone(S)')
                    # These two fields are intentionally generated by import: audit/backup acknowledgement and restoration journal.
                    for key,value in data['state'].items():
                        if key in ('dataGovernance','workspaceRecovery'):continue
                        goal=1 if key in ('accounts','forex','operationHistory','fxConsolidated','ledger','ledgerArchive','period') else 2 if key in ('fxPlanning','personalFinance','alladin') else 3 if key in ('mvpNotes','nocoda','pivotStudies') else 4 if key=='theme' else 0
                        check(tag+' / state.'+key,[goal] if goal else [],value,actual.get(key))
                    prefs=b.evaluate('()=>Object.fromEntries(JPW_WORKSPACE_KEYS.map(k=>[k,localStorage.getItem(k)]))')
                    check(tag+' / preferências',[5,6,7,8],data['workspace']['preferences'],prefs)
                    check(tag+' / rascunhos',[9],data['workspace']['drafts'],actual['workspaceRecovery']['drafts'])
                    again=b.evaluate("async()=>JSON.parse(await dgBuildBackupBlob(2,'TESTE-reexport.json','2026-09-16T12:00:00Z').text())")
                    check(tag+' / reexportação workspace',list(range(5,10)),data['workspace'],again['workspace'])
                    for key in data['state']:
                        if key not in ('dataGovernance','workspaceRecovery'):check(tag+' / reexportação '+key,[],data['state'][key],again['state'].get(key))
                    check(tag+' / aparência aplicada',[4,5,6,7],['light','2','secondary','TESTE — DADOS FICTÍCIOS'],b.evaluate('[S.theme,document.documentElement.dataset.fs,currentAppIconChoice(),settingsProfileState.confirmed.displayName]'))
                    check(tag+' / imagem decodificada',[5],True,b.evaluate('''async()=>{const i=new Image();i.src=settingsProfileState.confirmed.avatarDataUrl;await i.decode();return i.naturalWidth>0&&i.naturalHeight>0}'''))
                    b.locator('#workspaceDraftsButton').click()
                    for width,theme in [(390,'light'),(1440,'dark')]:
                        b.set_viewport_size({'width':width,'height':950});b.evaluate('(t)=>{S.theme=t;applyTheme();render()}',theme)
                        check(tag+f' / diálogo {width}',[9],True,b.locator('#workspaceDraftDialog').evaluate('e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth}'))
                        check(tag+f' / tema visual {width}',[4],theme,b.evaluate('document.documentElement.dataset.theme'))
                        b.screenshot(path=str(out/f'capturas/{tag}-{width}-{theme}.png'))
                    check(tag+' / imagens visíveis carregadas',[],[],b.locator('img:visible').evaluate_all('els=>els.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src)'))
                    check(tag+' / erros de execução',[],[],b.jpwealth_observed['pageerror']);b.context.close()
            # Exercise the exact files delivered for manual use, not only equivalent inline data.
            for entry in ['index.html','dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html']:
                b=br.prepare(helper,browser,url+entry)
                for bad in sorted((out/'invalidos').glob('*.json')):
                    snapshot=b.evaluate('localStorage.getItem(LSKEY)')
                    b.locator('#importFullBackupInput').set_input_files(str(bad))
                    b.wait_for_function('__br.alerts.length>0')
                    check(entry+' / rejeição '+bad.name,[],snapshot,b.evaluate('localStorage.getItem(LSKEY)'))
                    check(entry+' / sem falso sucesso '+bad.name,[],False,b.evaluate("__br.alerts.some(t=>t.includes('importado com sucesso'))"))
                    b.evaluate('__br.alerts=[]')
                b.evaluate("localStorage.setItem('jpw_fs','1')")
                b.locator('#importFullBackupInput').set_input_files(str(out/'validos/legado-sem-workspace.json'))
                b.wait_for_function("__br.alerts.some(t=>t.includes('importado com sucesso'))")
                check(entry+' / legado mantém preferência',[6],'1',b.evaluate("localStorage.getItem('jpw_fs')"))
                b.context.close()
            a.context.close();browser.close()
    except Exception as e:
        report['cases'].append({'name':'Execução do banco','goals':list(range(1,10)),'result':'TEST_HARNESS_FAIL','error':str(e),'trace':traceback.format_exc()})
    finally:server.shutdown();server.server_close()
    for name,script,extra,goals in [('backup-completo','complete_backup_test.py',[],list(range(1,10))),('confiabilidade','backup_reliability_test.py',['--artifact',str(out/'confiabilidade.json')],list(range(1,10))),('finalizacao','finalize_session_test.py',[],list(range(1,10)))]:
        print('RUN',name,flush=True)
        try:
            proc=subprocess.run([sys.executable,str(ROOT/'tools'/script),*extra],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
            (out/(name+'.log')).write_text(proc.stdout)
            status='PASS' if proc.returncode==0 else 'TEST_HARNESS_FAIL' if any(t in proc.stdout for t in ['ModuleNotFoundError','Executable doesn\'t exist','TEST_HARNESS_FAIL']) else 'PRODUCT_FAIL'
            report['cases'].append({'name':name,'goals':goals,'result':status,'expected':'exit 0','observed':f'exit {proc.returncode}','log':name+'.log'})
        except Exception as e:report['cases'].append({'name':name,'goals':goals,'result':'TEST_HARNESS_FAIL','error':str(e)})
    after=identity();report['sourcesAfter']=after
    check('Fontes preservadas',[],[],differences(before,after))
    for i,title in enumerate(GOALS,1):
        cases=[c for c in report['cases'] if i in c.get('goals',[])]
        report['goals'][str(i)]={'title':title,'result':'PASS' if cases and all(c['result']=='PASS' for c in cases) else 'FAIL','cases':[c['name'] for c in cases]}
    report['result']='PASS' if all(c['result']=='PASS' for c in report['cases']) else 'FAIL'
    report['comparisonPolicy']={'ignoredStatePaths':['state.dataGovernance','state.workspaceRecovery'],'reason':'Import generates audit/checkpoint metadata and a recovery journal; all other state fields are compared recursively. Draft content is independently compared.'}
    dump(out/'relatorio.json',report)
    rows=''.join('<tr><td>'+html.escape(c['name'])+'</td><td>'+c['result']+'</td><td><pre>'+html.escape(json.dumps(c.get('differences',c.get('error',c.get('observed',''))),ensure_ascii=False))+'</pre></td></tr>' for c in report['cases'])
    goals=''.join(f'<li>Meta {i}: {html.escape(v["title"])} — <b>{v["result"]}</b></li>' for i,v in report['goals'].items())
    pics=''.join(f'<figure><a href="capturas/{p.name}"><img loading="lazy" src="capturas/{p.name}"></a><figcaption>{p.name}</figcaption></figure>' for p in sorted((out/'capturas').glob('*.png')))
    (out/'relatorio.html').write_text('<!doctype html><meta charset="utf-8"><title>Banco de testes — Backup</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#f4f5f7;color:#18202b}td,th{padding:10px;border-bottom:1px solid #ccc;text-align:left}table{width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:160px;overflow:auto}img{max-width:100%;max-height:460px}figure{display:inline-block;max-width:45%;vertical-align:top}a{color:#9b1020}</style><h1>TESTE — DADOS FICTÍCIOS</h1><p>Build '+report['build']+' · Resultado: <b>'+report['result']+'</b></p><p><a href="ROTEIRO.md">Roteiro manual</a> · <a href="relatorio.json">Relatório JSON com esperado/observado</a></p><ol>'+goals+'</ol><h2>Cenários</h2><table><tr><th>Cenário</th><th>Resultado</th><th>Diferenças / observação</th></tr>'+rows+'</table><h2>Capturas</h2>'+pics)
    (out/'ROTEIRO.md').write_text('''# TESTE — DADOS FICTÍCIOS\n\nUse um perfil temporário de navegador ou janela privada, separado da sua sessão pessoal. A importação substitui os dados do destino. Abra a versão local candidata do app; não use um build antigo.\n\n1. Importe `validos/completo-galeria.json` pelo botão de importar base. Confirme e recarregue.\n2. Confira três contas sintéticas, histórico manual e um recibo de Consolidado; dois fechamentos no ledger (123 e 77); plano TESTE de 12 meses; PF com julho/agosto de 2026; Alladin com transações; duas notas na pasta BR-Pasta; NoCoda e Pivots. Os valores completos estão em `esperado.json`.\n3. Confira nome TESTE — DADOS FICTÍCIOS, retrato, tema claro, fonte 2, navegação superior, marca secundária, aparência escura/compacta de Notas, botão em x=0,5/y=0,8 e preferências Galton seed=123.\n4. Abra Rascunhos recuperados: a nota e o formulário pendentes devem estar disponíveis para copiar. Nenhuma operação deve ser criada por esses textos.\n5. Exporte, importe em outro contexto limpo e recarregue: compare com `esperado.json`. Auditoria de importação e journal de recuperação mudam legitimamente; os registros financeiros e preferências não.\n6. Repita com `completo-foto-personalizada.json`: a imagem vermelha TESTE substitui o retrato, sem depender de arquivo externo.\n7. Altere uma preferência no destino e importe `legado-sem-workspace.json`: a preferência deve permanecer. Esse arquivo antigo não contém os novos dados de workspace.\n8. Tente os dois arquivos de `invalidos/`: devem ser recusados sem substituir a base.\n9. Finalize a sessão usando o fluxo de exportação/confirmação. Reabra: registros e preferências devem permanecer.\n\nFalhas de armazenamento, interrupções e concorrência são injetadas somente nos testes automáticos. As APIs de pasta são simuladas nos testes de confiabilidade; isso não certifica um disco físico. Capturas usam dados fictícios.\n''')
    print(report['result'],out/'relatorio.html',flush=True)
    return 0 if report['result']=='PASS' else 1

if __name__=='__main__':sys.exit(main())

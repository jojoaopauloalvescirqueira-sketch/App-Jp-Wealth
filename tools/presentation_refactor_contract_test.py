#!/usr/bin/env python3
"""Campaign characterization through existing functions and real DOM events.

Literal oracles are fixed before production edits. Scripts are loaded whole;
no candidate-only helper is exported or invoked. As in navigation_local_contract,
synthetic readers/commands isolate ordering; the existing browser suites remain
necessary to prove integration with domain, storage, focus and full layouts.
"""
import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "pf": ["src/js/10-domain/12-personal-finance.js", "src/js/20-ui/18-finpes-budget.js"],
    "alladin": ["src/js/20-ui/24-alladin-views.js"],
    "settings": ["src/js/40-app/09-settings-modal.js"],
    "fx": ["src/js/30-accounting/05-fx-planning/05-fx-ui.js"],
}
COMMON = r"""
window.__t={events:[],errors:[],writes:0};
window.esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
window.$=id=>document.getElementById(id);
window.JPWAlladin={leitura:{}}; window.JPWFx={state:{},charts:{}};
window.addEventListener('error',e=>{__t.errors.push(e.message);e.preventDefault();});
window.save=()=>{__t.writes++;throw new Error('UNEXPECTED_WRITE');};
Object.defineProperty(window,'S',{get(){throw new Error('UNEXPECTED_FINANCIAL_READ');}});
Object.defineProperty(window,'localStorage',{get(){throw new Error('UNEXPECTED_STORAGE');}});
Object.defineProperty(window,'sessionStorage',{get(){throw new Error('UNEXPECTED_STORAGE');}});
"""
PF = r"""c=>{
  document.body.innerHTML='<div id="fixture"><input id="field"></div>';
  const root=$('fixture'),inp=$('field'),prefix=c.kind==='income'?'fi':'fe';
  inp.setAttribute('data-'+prefix+'-campo',c.field);inp.setAttribute('data-'+prefix+'-id','initial-id');
  inp.value=c.old;__t.events=[];__t.errors=[];
  window.alert=message=>__t.events.push(['alert',message,inp.value]);
  finpesBudgetRender=()=>__t.events.push(['render',inp.value]);
  pfActUpdateIncomeField=()=>{throw new Error('EARLY_CAPTURE');};
  pfActUpdateExpenseField=()=>{throw new Error('EARLY_CAPTURE');};
  fbBind(root,'2026-09');
  const act=(kind,...args)=>{__t.events.push(['act',kind,...args]);if(c.throw)throw new Error('DOMAIN_TEST_FAILURE');return c.refuse?{ok:false,erro:'RECUSA_SINTÉTICA'}:{ok:true};};
  pfActUpdateIncomeField=(...a)=>act('income',...a);pfActUpdateExpenseField=(...a)=>act('expense',...a);
  if(c.focus!==false)inp.focus();
  inp.setAttribute('data-'+prefix+'-id','event-id');
  if(c.changedField)inp.setAttribute('data-'+prefix+'-campo',c.changedField);
  inp.value=c.value;inp.dispatchEvent(new Event('change',{bubbles:true}));
  const first={events:JSON.parse(JSON.stringify(__t.events)),errors:__t.errors.slice(),value:inp.value,focus:document.activeElement===inp,prev:inp.dataset.prevval??null};
  if(c.repeat){__t.events=[];inp.value=c.value;inp.dispatchEvent(new Event('change',{bubbles:true}));first.repeated=JSON.parse(JSON.stringify(__t.events));}
  return {...first,writes:__t.writes};
}"""
INVALID = '⛔ Valor inválido — ponto ou vírgula decimal, sem separador ambíguo; em branco não é zero.'
NEGATIVE = '⛔ Valor negativo não é aceito: a direção já é do campo.'


def check_pf(page):
    observations = []
    fields = [("income", "name"), ("expense", "name"),
              ("income", "projectedAmount"), ("income", "receivedAmount"),
              ("expense", "targetAmount"), ("expense", "expectedAmount"),
              ("expense", "executedCash"), ("expense", "executedCard")]
    cases = []
    for kind, field in fields:
        values = [('  Curso á <x>  ', '  Curso á <x>  ', None)] if field == 'name' else [
            ('1.234,50', 123450, None), ('', None, None), ('0', 0, None),
            ('2,3,4', None, INVALID), ('-1', None, NEGATIVE)]
        for value, expected, message in values:
            cases.append((dict(kind=kind, field=field, old='17,00', value=value), expected, message))
        cases += [(dict(kind=kind, field=field, old=old, value='10', refuse=True, focus=focus),
                   '10' if field == 'name' else 1000, None)
                  for old, focus in [('17,00', True), ('', True), ('17,00', False)]]
    cases += [(dict(kind='income', field='name', changedField='projectedAmount', old='17', value='2,50', repeat=True), 250, None),
              (dict(kind='expense', field='name', old='x', value='y', throw=True), 'y', None)]
    for case, expected, message in cases:
        got = page.evaluate(PF, case)
        restored = case['old'] if case.get('focus', True) else ''
        if message:
            want = [['alert', message, case['value']]]
            assert got['value'] == restored
        else:
            want = [['act', case['kind'], '2026-09', 'event-id', case.get('changedField', case['field']), expected]]
            if case.get('refuse'):
                want += [['alert', '⛔ RECUSA_SINTÉTICA', restored], ['render', restored]]
                assert got['value'] == restored
            elif not case.get('throw'):
                want += [['render', case['value']]]
                assert got['value'] == case['value']
        assert got['events'] == want, (case, got, want)
        assert got['writes'] == 0
        assert bool(got['errors']) == bool(case.get('throw')), (case, got)
        if case.get('throw'):
            assert len(got['errors']) == 1 and 'DOMAIN_TEST_FAILURE' in got['errors'][0]
        if case.get('repeat'):
            assert got['repeated'] == want
        assert got['focus'] == case.get('focus', True)
        observations.append(dict(case=case, observation=got))
    return observations


ALLADIN = r"""c=>{
  __t.events=[];__t.errors=[];
  const accounts=c.accounts.map(a=>Object.freeze({...a}));
  const instruments=c.instruments.map(a=>Object.freeze({...a}));
  const cash=c.cash.map(a=>Object.freeze({...a}));
  Object.freeze(accounts);Object.freeze(instruments);Object.freeze(cash);
  const before=JSON.stringify({accounts,instruments,cash});
  JPWAlladin.leitura={accounts(){__t.events.push('accounts');return accounts;},instruments(){__t.events.push('instruments');if(c.throw)throw new Error('READ_TEST_FAILURE');return instruments;},cashAccounts(){__t.events.push('cashAccounts');return cash;}};
  let cat=null,error=null;try{cat=alladinCatalogoLabels();}catch(e){error=e.message;}
  return {cat,error,events:__t.events,immutable:before===JSON.stringify({accounts,instruments,cash}),writes:__t.writes,
    labels:cat?c.ids.map(id=>alladinCaixaLabel(cat,id)):[]};
}"""


def check_alladin(page):
    rows = []
    cases = [
        (dict(accounts=[{'accountId':'a','name':'XP'}],instruments=[],cash=[{'cashAccountId':'c','accountId':'a','currency':'BRL'}],ids=['c','missing',None]),
         {'contas':{'a':'XP'},'caixas':{'c':'BRL · XP'},'instrumentos':{}}, ['BRL · XP','missing','—']),
        (dict(accounts=[{'accountId':'a','name':'XP'},{'accountId':'b','name':'XP'}],instruments=[{'instrumentId':'i','name':'Nome','symbol':''}],cash=[{'cashAccountId':'c1','accountId':'a','currency':'BRL'},{'cashAccountId':'c2','accountId':'b','currency':'BRL','recordStatus':'INACTIVE'},{'cashAccountId':'c3','accountId':'a','currency':'USD'}],ids=['c1','c2','c3']),
         {'contas':{'a':'XP','b':'XP'},'caixas':{'c1':'BRL · XP · c1','c2':'BRL · XP · c2','c3':'USD · XP'},'instrumentos':{'i':'Nome'}},['BRL · XP · c1','BRL · XP · c2','USD · XP']),
        (dict(accounts=[{'accountId':'a','name':''},{'name':'ignored'}],instruments=[{'instrumentId':'i','symbol':'S<"&','name':'N'}],cash=[{'cashAccountId':'c1','accountId':'a'},{'cashAccountId':'c2','accountId':'unknown','currency':'EUR'},{'cashAccountId':'c3'},{'accountId':'a','currency':'USD'}],ids=['c1','c2','c3','']),
         {'contas':{'a':''},'caixas':{'c1':'a','c2':'EUR · unknown','c3':'—'},'instrumentos':{'i':'S<"&'}},['a','EUR · unknown','—','—']),
        (dict(accounts=[{'accountId':'a','name':'<img onerror=x>&'}],instruments=[],cash=[{'cashAccountId':'c','accountId':'a','currency':'BRL'}],ids=['c']),
         {'contas':{'a':'<img onerror=x>&'},'caixas':{'c':'BRL · <img onerror=x>&'},'instrumentos':{}},['BRL · <img onerror=x>&']),
        (dict(accounts=[],instruments=[],cash=[],ids=[]), {'contas':{},'caixas':{},'instrumentos':{}}, []),
    ]
    for case, cat, labels in cases:
        got = page.evaluate(ALLADIN,case)
        assert got == dict(cat=cat,error=None,events=['accounts','instruments','cashAccounts'],immutable=True,writes=0,labels=labels), got
        rows.append(dict(case=case,observation=got))
    case=dict(accounts=[],instruments=[],cash=[],ids=[],throw=True)
    got=page.evaluate(ALLADIN,case)
    assert got == dict(cat=None,error='READ_TEST_FAILURE',events=['accounts','instruments'],immutable=True,writes=0,labels=[]),got
    rows.append(dict(case=case,observation=got))
    # A read-order oracle sensitive to moving all reads before projection.
    got=page.evaluate(r"""()=>{__t.events=[];JPWAlladin.leitura={accounts(){__t.events.push('accounts');return [{accountId:'a',get name(){__t.events.push('account-name');return 'A';}}];},instruments(){__t.events.push('instruments');return [{instrumentId:'i',get symbol(){__t.events.push('symbol');return '';},get name(){__t.events.push('instrument-name');return 'I';}}];},cashAccounts(){__t.events.push('cashAccounts');return [];}};alladinCatalogoLabels();return __t.events;}""")
    assert got==['accounts','account-name','instruments','symbol','instrument-name','cashAccounts'],got
    rows.append(dict(case='interleaved-read-projection',observation=got))
    return rows


SETTINGS = r"""c=>{
  if(!c.keepRoot)document.body.innerHTML=c.root===false?'':'<div id="settingsSearchResults"></div>';
  if(c.keepRoot && !$('settingsSearchResults').querySelector('button'))throw new Error('MISSING_PRIOR_RESULTS_FIXTURE');
  __t.events=[];__t.errors=[];
  const entries=c.entries.map(x=>Object.freeze({...x}));Object.freeze(entries);
  settingsSearchEntries=()=>{__t.events.push(['index']);return entries;};
  settingsResultPath=id=>{__t.events.push(['path',id]);return c.paths[id]??id;};
  settingsNavigateToLeaf=(id,options)=>__t.events.push(['click',id,options.focus,options.reveal===undefined?'__undefined__':options.reveal]);
  settingsState.query=c.query;const before=JSON.stringify(entries);renderSettingsSearch();
  const root=$('settingsSearchResults'),buttons=root?[...root.querySelectorAll('[data-settings-result]')]:[];
  const labels=buttons.map(b=>[b.querySelector('b').textContent,b.querySelector('span').textContent,b.dataset.settingsResult]);
  buttons.forEach(b=>b.click());
  return {labels,events:__t.events,html:root?root.innerHTML:null,immutable:before===JSON.stringify(entries),images:document.images.length,writes:__t.writes,errors:__t.errors};
}"""


def check_settings(page):
    observations=[]
    entries=[dict(title='Tema',category='a'),dict(title='Tema',category='a',selector='#later'),
             dict(title='Tema B',category='b',selector='#b'),dict(title='Tema C',category='a',selector='#c'),dict(title='tema',category='a')]
    cases=[(dict(query=' TEMA ',entries=entries,paths={'a':'Interface','b':'Tela'}),[2,3,0,4]),
           (dict(query='AÇÃO',entries=[dict(title='Ação',category='a'),dict(title='Acao',category='a')],paths={'a':'Tela'}),[0]),
           (dict(query='tela',entries=[dict(title='Outro',category='a')],paths={'a':'Tela'}),[0]),
           (dict(query='armazenamento',entries=[dict(title='armazenamento',category='a'),dict(title='armazenamento',category='b')],paths={'a':'Sobre','b':'Dados › Armazenamento'}),[0,1]),
           (dict(query='none',entries=entries,paths={}),[]),
           (dict(query=' ',entries=entries,paths={}),[]),
           (dict(query='tema',root=False,entries=entries,paths={}),[]),
           (dict(query='img',entries=[dict(title='<img src=x onerror=x>&',category='a',selector='#safe')],paths={'a':'<b>Path</b>'}),[0])]
    many=[dict(title=f'Item {i:02}',category='a',**({'selector':f'#i{i}'} if i>=10 else {})) for i in range(21)]
    cases.append((dict(query='Item',entries=many,paths={'a':'Tela'}),list(range(10,21))+list(range(7))))
    cases.append((dict(query=' ',entries=many,paths={'a':'Tela'},keepRoot=True),[]))
    for case,indexes in cases:
        got=page.evaluate(SETTINGS,case)
        expected=[[case['entries'][i]['title'],case['paths'].get(case['entries'][i]['category'],case['entries'][i]['category']),str(n)] for n,i in enumerate(indexes)]
        assert got['labels']==expected,(case,got,expected)
        root_exists=case.get('root',True);active=root_exists and bool(case['query'].strip())
        events=([['index']]+[['path',x['category']] for x in case['entries']]) if active else []
        events += [['click',case['entries'][i]['category'],False,case['entries'][i].get('selector','__undefined__')] for i in indexes]
        assert got['events']==events,(case,got,events)
        assert got['immutable'] and got['images']==0 and got['writes']==0 and not got['errors']
        if not root_exists:assert got['html'] is None
        elif not active:assert got['html']==''
        elif not indexes:assert got['html']=='<p class="settings-no-results">Nenhuma configuração ou ajuda encontrada.</p>'
        observations.append(dict(case=case,observation=got))
    return observations


FX_SETUP = r"""()=>{
  window.__fx={live:{plan:{name:'Sintético',baseline:{startMonth:'2026-01',horizonMonths:32}},forecast:Array.from({length:32},(_,i)=>({id:'f'+i})),baseline:Array.from({length:32},(_,i)=>({id:'b'+i}))},callback:null,sync:false};
  JPWFx.state.fxOverviewLive=()=>{__t.events.push(['read']);return __fx.live;};
  fxpOverviewHTML=()=>{__t.events.push(['html','overview']);return '<button id="fxpQuoteRefresh">Refresh</button><button data-fxp-cur="brl">BRL</button><button data-fxp-win="12">12m</button><button id="fxpGoOnboarding">Settings</button><button id="fxpGoLedger">Ledger</button><canvas id="fxpMainChart"></canvas><p id="fxpMainChartSummary"></p><details id="fxpReturnsBox"><canvas id="fxpReturnsChart"></canvas></details>';};
  fxpPlanningHTML=()=>{__t.events.push(['html','planning']);return 'planning';};fxpActualsHTML=()=>{__t.events.push(['html','actuals']);return 'actuals';};fxpTableHTML=()=>{__t.events.push(['html','table']);return '<button data-fxp-hist="actual">History</button>';};
  fxpCreateFormHTML=()=>{__t.events.push(['html','empty']);return 'empty';};
  fxpBindCreate=()=>__t.events.push(['bind','empty']);fxpBindPlanning=()=>__t.events.push(['bind','planning']);fxpBindActuals=()=>__t.events.push(['bind','actuals']);
  const quoteBind=fxpBindQuote;fxpBindQuote=root=>{__t.events.push(['bind','quote']);quoteBind(root);};
  JPWMarket={usdBrl:{onChange(fn){__t.events.push(['wire']);__fx.callback=fn;},refresh(force){__t.events.push(['refresh',force]);if(__fx.throw)throw new Error('REFRESH_TEST_FAILURE');if(__fx.switchView){fxpView=__fx.switchView;__fx.switchView=null;}if(__fx.sync){__fx.sync=false;__fx.callback();}}}};
  JPWFx.charts={fxDrawMainChart(node,plan,live,mode){__fx.identities.push([node===document.getElementById('fxpMainChart'),plan===__fx.live.plan,live===__fx.live,live.forecast===__fx.live.forecast,live.baseline===__fx.live.baseline]);__t.events.push(['main',node.id,plan===__fx.live.plan,live.forecast.map(x=>x.id),live.baseline.map(x=>x.id),mode]);},fxMainChartSummaryText(plan,live,mode){__t.events.push(['summary',plan===__fx.live.plan,live.forecast.length,mode]);return 'resumo sintético';},fxDrawReturnsChart(node,live){__t.events.push(['returns',node.id,live===__fx.live]);}};
  openSettingsModal=(category,opener)=>__t.events.push(['settings',category,opener.id]);
  document.body.innerHTML='<div id="fxPlanningCard"><div id="fxPlanningRoot" style="width:1120px"></div></div>';
}"""
FX_RUN = r"""c=>{__t.events=[];__t.errors=[];__fx.identities=[];if(c.switchView)__fx.switchView=c.switchView;if(c.fullWindow)fxpHorizonWin=100;if(c.width)$('fxPlanningRoot').style.width=c.width+'px';if(c.sync)__fx.sync=true;if(c.throw)__fx.throw=true;
  let accepted=null,error=null;try{if(c.click)document.querySelector(c.click).click();else accepted=JPWFx.ui.selectView(c.view);}catch(e){error=e.message;}
  __fx.throw=false;const root=$('fxPlanningRoot');return {accepted,error,events:JSON.parse(JSON.stringify(__t.events)),identities:__fx.identities,view:JPWFx.ui.getView(),mode:fxpChartMode,window:fxpHorizonWin,html:root.innerHTML,open:root.querySelector('#fxpReturnsBox')?.open??null,summary:root.querySelector('#fxpMainChartSummary')?.textContent??null,writes:__t.writes,errors:__t.errors};}"""


def fx_draw(mode='usd',n=24):
    return [['main','fxpMainChart',True,[f'f{i}' for i in range(n)],[f'b{i}' for i in range(n)],mode],['summary',True,n,mode],['returns','fxpReturnsChart',True]]


def check_fx(page):
    page.evaluate(FX_SETUP);rows=[]
    cases=[(dict(view='overview'),[['read'],['html','overview'],['wire'],['bind','quote'],['refresh',False]]+fx_draw()),
           (dict(view='overview',width=1119),[['read'],['html','overview'],['bind','quote'],['refresh',False]]+fx_draw()),
           (dict(click='#fxpQuoteRefresh'),[['refresh',True]]),
           (dict(click='[data-fxp-cur]'),[['read'],['html','overview'],['bind','quote'],['refresh',False]]+fx_draw('brl')),
           (dict(click='[data-fxp-win]'),[['read'],['html','overview'],['bind','quote'],['refresh',False]]+fx_draw('brl',12)),
           (dict(click='#fxpGoOnboarding'),[['settings','general','fxpGoOnboarding']]),
           (dict(click='#fxpGoLedger'),[['read'],['html','actuals'],['bind','actuals']]),
           (dict(view='planning'),[['read'],['html','planning'],['bind','planning']]),
           (dict(view='table'),[['read'],['html','table']]),
           (dict(view='unknown'),[]),
           (dict(view='overview',width=1120,sync=True),[['read'],['html','overview'],['bind','quote'],['refresh',False],['read'],['html','overview'],['bind','quote'],['refresh',False]]+fx_draw('brl',12)+fx_draw('brl',12)),
           (dict(click='[data-fxp-cur]'),([['read'],['html','overview'],['bind','quote'],['refresh',False]]+fx_draw('brl',12))*2),
           (dict(view='overview',fullWindow=True),[['read'],['html','overview'],['bind','quote'],['refresh',False]]+fx_draw('brl',32)),
           (dict(view='overview',switchView='actuals'),[['read'],['html','overview'],['bind','quote'],['refresh',False]]+fx_draw('brl',32)+[['bind','actuals']]),
           (dict(view='overview',throw=True),[['read'],['html','overview'],['bind','quote'],['refresh',False]])]
    expected_width=1120
    for case,want in cases:
        expected_width=case.get('width',expected_width)
        got=page.evaluate(FX_RUN,case)
        assert got['events']==want,(case,got,want)
        assert got['identities']==[[True,True,len(event[3])==32,len(event[3])==32,len(event[3])==32] for event in want if event[0]=='main'], (case,got)
        assert got['accepted']==(None if case.get('click') or case.get('throw') else case.get('view')!='unknown')
        assert got['error']==('REFRESH_TEST_FAILURE' if case.get('throw') else None)
        assert not got['errors'] and got['writes']==0
        if got['view']=='overview' and not case.get('throw'):
            assert got['open']==(expected_width>=1120)
            assert got['summary']=='resumo sintético'
        rows.append(dict(case=case,observation=got))
    page.evaluate('()=>{window.JPWMarket=null;}')
    got=page.evaluate(FX_RUN,dict(view='overview'))
    assert got['events']==[['read'],['html','overview'],['bind','quote']]+fx_draw('brl',32)
    assert got['identities']==[[True,True,True,True,True]] and got['writes']==0 and not got['errors']
    rows.append(dict(case='quote-unavailable',observation=got))
    page.evaluate('()=>{__fx.live=null;}')
    got=page.evaluate(FX_RUN,dict(view='overview'))
    assert got['events']==[['read'],['html','empty'],['bind','empty']] and got['accepted'] is True
    assert got['writes']==0 and not got['errors']
    rows.append(dict(case='no-plan',observation=got))
    page.evaluate('()=>{$("fxPlanningRoot").remove();__t.events=[];}')
    got=page.evaluate('()=>({accepted:JPWFx.ui.selectView("overview"),events:__t.events})')
    assert got==dict(accepted=True,events=[])
    rows.append(dict(case='root-absent',observation=got))
    return rows


def check_pf_live(browser):
    """Actual input -> domain/save -> render/rebind, in an isolated full app."""
    from dashboard_forex_relocation_test import serve
    from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
    server, url = serve(ROOT)
    context = browser.new_context(service_workers='block', viewport={'width':1440,'height':1000})
    install_bootstrap(context)
    context.add_init_script('window.__onbShown=true;')
    page=context.new_page();errors=[];rows=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    try:
        page.goto(url,wait_until='load');wait_bootstrap(page)
        seed=page.evaluate("""()=>{
          window.alert=message=>__live.alerts.push(message);closeModal();
          navigateToScreen('finpes');JPWFin.ui.selectView('mensal');
          const key=fbCurrentKey();
          const income=pfActAddIncome(key,{name:'Receita sintética',projectedAmount:100});
          const expense=pfActAddExpense(key,{name:'Despesa sintética'});
          finpesBudgetRender();
          window.__live={key,alerts:[],saves:0,renders:0};
          const originalSave=save,originalRender=finpesBudgetRender;
          save=function(){__live.saves++;return originalSave.apply(this,arguments);};
          finpesBudgetRender=function(){__live.renders++;return originalRender.apply(this,arguments);};
          return {income:income.ok,expense:expense.ok};
        }""")
        assert seed=={'income':True,'expense':True},seed
        for prefix,collection,field in [('fi','incomes','projectedAmount'),('fe','expenses','targetAmount')]:
            for value,expected in [('1,23',123),('2,34',234),('inválido',234)]:
                selector=f'[data-{prefix}-campo="{field}"]'
                page.evaluate('()=>{__live.saves=0;__live.renders=0;__live.alerts=[];}')
                inp=page.locator(selector).first
                inp.focus();inp.fill(value);inp.press('Tab')
                got=page.evaluate("""([collection,field,selector])=>{
                  const record=S.personalFinance.months[__live.key][collection][0];
                  const saved=JSON.parse(localStorage.getItem('jpwealth_v9_state')).personalFinance.months[__live.key][collection][0];
                  const input=document.querySelector(selector),active=document.activeElement;
                  return {value:record[field],saved:saved[field],sameId:record.id===saved.id,
                    count:S.personalFinance.months[__live.key][collection].length,
                    saves:__live.saves,renders:__live.renders,alerts:__live.alerts,
                    display:input.value,focus:{tag:active.tagName,id:active.id,
                      field:active.dataset.fiCampo||active.dataset.feCampo||null}};
                }""",[collection,field,selector])
                accepted=value!='inválido'
                assert got['value']==got['saved']==expected and got['sameId'] and got['count']==1,got
                assert got['saves']==got['renders']==(1 if accepted else 0),got
                assert got['alerts']==([] if accepted else [INVALID]),got
                rows.append(dict(case=[prefix,value],observation=got))
            # Real domain refusal of an empty name must render the confirmed value.
            selector=f'[data-{prefix}-campo="name"]'
            page.evaluate('()=>{__live.saves=0;__live.renders=0;__live.alerts=[];}')
            inp=page.locator(selector).first;inp.focus();inp.fill('');inp.press('Tab')
            got=page.evaluate("""([collection,selector])=>({
              value:S.personalFinance.months[__live.key][collection][0].name,
              saved:JSON.parse(localStorage.getItem('jpwealth_v9_state')).personalFinance.months[__live.key][collection][0].name,
              display:document.querySelector(selector).value,saves:__live.saves,renders:__live.renders,alerts:__live.alerts})""",[collection,selector])
            name='Receita sintética' if prefix=='fi' else 'Despesa sintética'
            assert got==dict(value=name,saved=name,display=name,saves=0,renders=1,
                alerts=['⛔ descrição obrigatória' if prefix=='fi' else '⛔ nome da despesa obrigatório']),got
            rows.append(dict(case=[prefix,'domain-refusal'],observation=got))
        assert_fixture_requests(context);assert not errors,errors
        return rows
    finally:
        context.close();server.shutdown();server.server_close()


CHECKS = {'pf':check_pf,'alladin':check_alladin,'settings':check_settings,'fx':check_fx,'pf-live':check_pf_live}
SOURCES['pf-live']=[item['path'] for item in json.loads((ROOT/'src/js/manifest.json').read_text())['files']]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--area',choices=['all',*CHECKS],default='all')
    parser.add_argument('--artifact',type=Path,required=True)
    args=parser.parse_args();areas=list(CHECKS) if args.area=='all' else [args.area]
    result={'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for a in areas for p in SOURCES[a]},
            'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'observations':{},'passed':False}
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            result['browser']=browser.version
            for area in areas:
                if area=='pf-live':
                    result['observations'][area]=check_pf_live(browser)
                    print(f'PASS pf-live: {len(result["observations"][area])} full-app interaction observations',flush=True)
                    continue
                context=browser.new_context(service_workers='block');requests=[]
                context.route('**/*',lambda route:(requests.append(route.request.url),route.abort()))
                page=context.new_page();page.set_content('<!doctype html><html><body></body></html>');page.add_script_tag(content=COMMON)
                for source in SOURCES[area]:page.add_script_tag(content=(ROOT/source).read_text())
                result['observations'][area]=CHECKS[area](page)
                assert not requests,requests
                context.close();print(f'PASS {area}: {len(result["observations"][area])} literal contract observations',flush=True)
            browser.close()
        result['passed']=True
    finally:
        args.artifact.parent.mkdir(parents=True,exist_ok=True)
        with args.artifact.open('x') as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write('\n')
    print('PASS: presentation refactor contracts; integration remains separately tested')


if __name__=='__main__':main()

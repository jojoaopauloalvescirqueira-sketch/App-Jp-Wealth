#!/usr/bin/env python3
"""Focal V11 views and commands, synthetic data and nominal network fixtures."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
import hashlib,json,threading,traceback
from pathlib import Path
from playwright.sync_api import sync_playwright
import notes_launcher_test as fixture
ROOT=Path(__file__).resolve().parents[1]

def inputs():
    paths=['index.html','src/styles/app.css','src/js/manifest.json','build-id.js']+[f['path'] for f in json.loads((ROOT/'src/js/manifest.json').read_text())['files']]
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}

def goto(page,target):
    assert page.evaluate('(target)=>JPWNavigation.navigate(target)',target),target
    fixture.settle(page)

def fill(form,fields):
    for key,value in fields.items():form.locator('[name="'+key+'"]').fill(str(value))

def actual(page):
    return page.evaluate('({document:JSON.stringify(S),stored:localStorage.getItem(LSKEY)})')

def journey(page,out,label):
    before=actual(page)
    for target in ['forex-overview','forex-reserves','forex-operation','forex-reconciliation','forex-planning','dashboard','forex-overview']*2:goto(page,target)
    assert actual(page)==before,'navigation changed operational state'
    assert page.evaluate('JPWForex.state.read().account') is None
    assert 'Não calculável' in page.locator('#forexV11Overview').inner_text()
    goto(page,'params');form=page.locator('#fxAccountFacts')
    form.locator('[name=accountIndex]').select_option('0')
    fill(form,{'si':10000,'equity':9700,'capitalNominal':12000,'netCashflow':0,'source':'Synthetic broker statement','observedAt':'2026-09-14T12:00','reason':'Synthetic observation'})
    form.get_by_role('button',name='Registrar observação',exact=True).click()
    assert form.locator('[role=status]').inner_text()=='Registro confirmado.'
    model=page.evaluate('JPWForex.state.read()');assert model['account']['si']==10000 and model['metrics']['drawdown']['value']==3 and model['accountPhase']['value']==2,model
    assert model['executionEligibility']['status']=='BLOCKED'
    page.locator('#forexEnginePanel summary',has_text='ATR, candle').click()
    market=page.locator('#fxMarketFacts');fill(market,{'atrShort':2,'atrLong':1,'observedAt':'2026-09-14T12:00','source':'Synthetic H4 series','reason':'Synthetic volatility'})
    market.get_by_role('button',name='Registrar ATRs',exact=True).click()
    assert market.locator('[role=status]').inner_text()=='Registro confirmado.'
    assert page.evaluate('JPWForex.state.read().metrics.vrm.value')==2
    page.evaluate('closeSettingsModal()');goto(page,'forex-reserves')
    form=page.locator('#fxReserveFacts');fill(form,{'capitalNominal':12000,'fcrConstituted':2600,'feoConstituted':3000,'sixMonthExpenseAmount':3000,'expensePeriod':'2026-03 to 2026-08','determinationReference':'Synthetic six-month approved expense ledger','fcrLiquidityDays':1,'feoLiquidityDays':2,'verifiedAt':'2026-09-14T12:00','source':'Synthetic reserve report','reason':'Synthetic reserve observation'})
    for key in ['determinationRecorded','expensesApproved','verificationRecorded']:form.locator('[name='+key+']').check()
    form.get_by_role('button',name='Registrar reservas',exact=True).click()
    assert form.locator('[role=status]').inner_text()=='Registro confirmado.'
    model=page.evaluate('JPWForex.state.read()');assert model['metrics']['fcrRequirement']['value']==2640 and model['metrics']['feoRequirement']['value']==3000,model
    assert model['reserves']['distributionStatus']=='BLOCKED'
    assert model['metrics']['fcrStatus']['value']['deficit']==40,model['metrics']['fcrStatus']
    assert 'Requerido 2.640 USD' in page.locator('#forexReservesPanel').inner_text()
    assert 'Requerido 3.000 USD' in page.locator('#forexReservesPanel').inner_text()
    # Unsubmitted draft survives leaving/return; navigation cannot persist it.
    form.locator('[name=reason]').fill('Unsubmitted synthetic draft');before=actual(page)
    goto(page,'forex-overview');goto(page,'forex-reserves')
    assert form.locator('[name=reason]').input_value()=='Unsubmitted synthetic draft'
    assert actual(page)==before
    page.screenshot(path=str(out/(label+'-reserves.png')),full_page=True)
    goto(page,'forex-overview')
    assert page.locator('#hdrEquity').inner_text()==page.evaluate('fmtForexMoney(JPWForex.state.read().account.equity,JPWForex.state.read().account,0)'), 'context bar lost the observed equity on navigation'
    page.screenshot(path=str(out/(label+'-overview.png')),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'page overflow'
    goto(page,'params')
    assert page.locator('#forexEnginePanel').is_visible()
    page.locator('#fxAccountFacts [name=si]').focus();page.keyboard.press('Tab')
    assert page.evaluate('document.activeElement.name')=='equity','account form keyboard order'
    page.screenshot(path=str(out/(label+'-engine.png')),full_page=True)
    page.locator('#fxOperationBudget').evaluate("form=>form.closest('details').open=true")
    budget=page.locator('#fxOperationBudget')
    fill(budget,{'amount':500,'declaredBy':'Synthetic operator','declaredAt':'2026-09-14T12:00','source':'Synthetic declared budget','reason':'Budget before first software record'})
    budget.get_by_role('button',name='Registrar orçamento ou redução',exact=True).click()
    assert budget.locator('[role=status]').inner_text()=='Registro confirmado.'
    assert page.evaluate('JPWForex.state.read().metrics.operationBudget.value')==500
    before_budget=actual(page);goto(page,'forex-overview')
    assert 'Orçamento declarado da operação' in page.locator('#forexV11Overview').inner_text()
    assert page.evaluate('JPWForex.state.read().metrics.sizingTrace.finalVolume') is None
    assert actual(page)==before_budget
    goto(page,'params')
    # Existing command seeds the same factual operation the grade form identifies.
    result=page.evaluate("operationRecordOrder(0,0,{par:'EURUSD',tipo:'BUY',role:'GENESIS',lote:0.01,entry:1.1,sl:1,tp:1.2,status:'Aberta',stopValidated:true,costs:0,costBasis:'SEPARATE_FROM_RESULT'},{reason:'Synthetic grade journey'})")
    assert result['ok'],result
    page.locator('#fxGridFacts').evaluate("form=>form.closest('details').open=true")
    grade=page.locator('#fxGridFacts');grade.locator('[name=phase]').select_option('2');grade.locator('[name=reason]').fill('Synthetic declared structure')
    grade.get_by_role('button',name='Registrar fase da grade',exact=True).click()
    assert grade.locator('[role=status]').inner_text()=='Registro confirmado.'
    assert page.evaluate('JPWForex.state.read().activeGridPhase.value')==2
    # A filled draft remains a draft across the actual save/load path.
    added=page.evaluate("operationAddDraft(0)");assert added['ok'],added
    draft=page.evaluate("operationRecordOrder(0,1,{par:'EURUSD',tipo:'BUY',lote:0.01,entry:1.1,sl:1,status:''},{reason:'Synthetic recoverable draft'})")
    assert draft['ok'],draft
    assert page.evaluate("S.phases[0].orders[1].recordStatus")=='draft'
    before_orders=page.evaluate('JSON.stringify(S.phases)')
    # Compare the operational envelope after the existing real reload path.
    before=actual(page);page.reload();fixture.wait_bootstrap(page);fixture.settle(page)
    assert page.evaluate('JSON.stringify(S.phases)')==before_orders,'load promoted or altered a filled draft'
    after=actual(page);assert json.loads(before['document'])['forex']==json.loads(after['document'])['forex'],'forex aggregate changed on reload'
    assert json.loads(before['stored'])['forex']==json.loads(after['stored'])['forex'],'stored forex aggregate changed on reload'
    # Currency is explicit; a new period must not borrow the old reserve balances.
    result=page.evaluate("""() => {
      const a=JPWForex.state.read().account;
      return JPWForex.state.recordAccountFacts({...a,accountIndex:0,currency:'BRL',usdToAccountRate:5,newPeriod:true},{reason:'Synthetic BRL period'});
    }""")
    assert result['ok'],result
    page.evaluate('render()');goto(page,'forex-overview')
    assert 'R$' in page.locator('#hdrEquity').inner_text()
    assert page.evaluate('JPWForex.state.read().reserves.totalConstituted') is None
    before=actual(page)
    result=page.evaluate("""() => {
      const original=structuredClone(S);S.forex.schemaVersion=99;S.forex.proposals={future:true};
      const raw=JSON.stringify(S),stored=localStorage.getItem(LSKEY);render();
      const result={same:raw===JSON.stringify(S)&&stored===localStorage.getItem(LSKEY),text:document.getElementById('forexV11Overview').innerText};
      S=original;render();return result;
    }""")
    assert result['same'] and 'Registro indisponível' in result['text'],result
    assert actual(page)==before
    return {'account_phase':2,'drawdown_percent':3,'fcr_required':2640,'fcr_deficit':40,'feo_required':3000,'execution':'BLOCKED','screenshots':[label+'-reserves.png',label+'-overview.png',label+'-engine.png']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--portable',action='store_true');parser.add_argument('--width',type=int);args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(fixture.Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
    report={'suite':'forex-v11-journey','inputs_before':inputs(),'cases':[]}
    try:
      with sync_playwright() as pw:
       browser=pw.chromium.launch(**fixture.launch_options())
       for width,theme in [(1440,'light'),(1440,'dark'),(390,'light'),(390,'dark')]:
        if args.width and width!=args.width:continue
        context=browser.new_context(viewport={'width':width,'height':960},service_workers='block',reduced_motion='reduce');label=str(width)+'-'+theme;row={'name':label}
        try:
          target='dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html' if args.portable else 'index.html'
          page,observed=fixture.prepare(context,f'http://127.0.0.1:{server.server_port}/{target}',theme)
          fixture.assert_clean(context,observed)
          row['build']=page.evaluate('JP_WEALTH_BUILD_ID');row['observations']=journey(page,args.out,label)
          fixture.assert_clean(context,observed);row['result']='PASS'
        except Exception as e:
          row.update(result='PRODUCT_FAIL',detail=str(e),type=type(e).__name__,traceback=traceback.format_exc())
          if 'page' in locals():
            row['active_screen']=page.evaluate("document.querySelector('#appMain>.screen.active')?.id")
            row['responses']=page.locator('.fx-engine-response').all_text_contents()
            page.screenshot(path=str(args.out/(label+'-failure.png')),full_page=True)
        finally:context.close();report['cases'].append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
        if row['result']!='PASS':break # shared bootstrap defect must not be repeated blindly
       browser.close()
    finally:
      server.shutdown();report['inputs_after']=inputs();report['unchanged']=report['inputs_before']==report['inputs_after'];(args.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['unchanged'] and report['cases'] and all(c['result']=='PASS' for c in report['cases']) else 1
if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env python3
"""Pure mathematical/state command probes over the real planning modules.

The application/browser persistence integration is deliberately outside this
probe: save/context are synthetic adapters. The separate monthly board suite
exercises the full page and physical storage. No user data is read.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MODULES = [ROOT / 'src/js/30-accounting/05-fx-planning' / name for name in
           ('01-fx-model.js', '02-fx-engine.js', '03-fx-state.js')]
PROBE = r'''() => {
 const st=JPWFx.state,m=JPWFx.model,e=JPWFx.engine;let assertions=0;const cases=[];
 const yes=(v,n)=>{if(!v)throw Error(n);assertions++};
 const make=()=>m.fxCreatePlan({assumptions:{startMonth:'2026-01',horizonMonths:36,initialBalanceUsd:1000,defaultMonthlyReturn:.012,recurringContributions:{personalUsd:20,propUsd:3}}});
 for(let i=0;i<75;i++){
  const plan=make();plan.current.defaultMonthlyReturn=(i-30)/1000;let open=1000;
  for(const row of e.fxForecastTimeline(plan)){
   const profit=open*plan.current.defaultMonthlyReturn,close=open+profit+23;
   yes(row.open===open&&row.profit===profit&&row.close===close,'complete-input arithmetic equivalence');open=close;
  }
 }
 cases.push('75 complete-input scenarios × 36 months: original arithmetic retained');
 const plan=make();plan.current.absentMonths={'2026-02':{reason:'missing'}};
 plan.rebases=[{month:'2026-04',openingBalanceUsd:2000}];let rows=e.fxForecastTimeline(plan);
 yes(rows[1].close===null&&rows[2].close===null&&rows[3].open===2000,'absence / explicit rebase');
 yes(e.fxAnnualSummary(rows)[0].profitUsd===null,'partial annual result not presented as total');
 yes(e.fxVarianceRows([{month:'2026-01',close:null}],[{month:'2026-01',close:null}])[0].diffUsd===null,'null variance');
 yes(m.fxResolveRate({defaultMonthlyReturn:.02,monthOverrides:{'2026-01':null}},'2026-01')===null,'null override not zero');
 plan.current.defaultMonthlyReturn=1e308;rows=e.fxForecastTimeline(plan);
 yes(rows[0].status==='BLOCKED'&&rows[0].close===null,'overflow unavailable');
 cases.push('absence, explicit rebase, partial summary, null variance and overflow');
 S.fxPlanning={schemaVersion:1,auditLog:[],plan:make()};
 yes(st.fxPlanClearMonth('2026-02','Remove forecast').ok,'clear month');
 yes(!st.fxPlanReviseFromMonth('2026-02',{rate:0},'Incomplete refill').ok,'incomplete refill refused');
 yes(st.fxPlanReviseFromMonth('2026-02',{rate:0,personalUsd:0,propUsd:0},'Explicit zeros').ok,'zero refill');
 rows=e.fxForecastTimeline(st.fxActivePlan());yes(rows[1].close===rows[1].open,'zero not absence');
 yes(st.fxPlanReviseAssumptions({...S.fxPlanning.plan.current,defaultMonthlyReturn:.03,recurringContributions:{personalUsd:40,propUsd:8}},'Global edit').ok,'global edit');
 rows=e.fxForecastTimeline(st.fxActivePlan());yes(rows[1].rate===0&&rows[1].personalUsd===0&&rows[2].personalUsd===40,'global defaults preserve monthly exceptions');
 yes(st.fxPlanRestoreMonth('2026-02','Return to defaults').ok,'restore defaults');
 rows=e.fxForecastTimeline(st.fxActivePlan());yes(rows[1].rate===.03&&rows[1].personalUsd===40,'default inheritance restored');
 cases.push('clear, explicit zero refill, general defaults and restore');
 yes(!st.fxPlanFinalizeMonth('2026-01',{returnRate:.1}).ok,'deposit check required');
 yes(st.fxPlanFinalizeMonth('2026-01',{returnRate:.1,contributionsConfirmed:true}).ok,'finalize');
 yes(st.fxPlanFinalizeMonth('2026-02',{profitUsd:10,inputType:'usd',contributionsConfirmed:true}).ok,'finalize usd');
 yes(!st.fxPlanRecordActual('2026-01',{returnRate:.2,contributionsConfirmed:true}).ok,'legacy overwrite refused');
 yes(!st.fxPlanAddContribution({month:'2026-01',originalCurrency:'USD',originalAmount:5}).ok,'closed deposit refused');
 yes(st.fxPlanReopenMonth('2026-01','Correct result').ok,'reopen');
 const history=S.fxPlanning.plan.actualHistory.find(h=>h.action==='REOPENED');
 yes(history.calculationSnapshot.actuals['2026-02'].closureStatus==='FINALIZED','old calculation state preserved');
 rows=e.fxForecastTimeline(st.fxActivePlan());yes(rows[0].status==='REOPENED'&&rows[1].phase==='actual'&&rows[1].status==='REVIEW_REQUIRED'&&rows[1].close===null,'downstream actual retained');
 yes(!st.fxPlanFinalizeMonth('2026-02',{profitUsd:10,inputType:'usd',contributionsConfirmed:true}).ok,'chronology enforced');
 yes(st.fxPlanFinalizeMonth('2026-01',{returnRate:.2,contributionsConfirmed:true}).ok,'refinalize');
 yes(st.fxPlanFinalizeMonth('2026-02',{profitUsd:10,inputType:'usd',contributionsConfirmed:true}).ok,'reconcile');
 yes(st.fxOverviewLive().coverage==='COMPLETE','coverage restored');
 cases.push('finalization guards, reopening, exact retained state and chronological reconciliation');
 const baseline=JSON.stringify(S.fxPlanning.plan.baseline);yes(st.fxPlanReviseAssumptions({...S.fxPlanning.plan.current,defaultMonthlyReturn:.04},'General').ok,'later premise edit');
 yes(JSON.stringify(S.fxPlanning.plan.baseline)===baseline,'baseline immutable');
 S.fxPlanning.plan.planningRevision=99;yes(st.fxActivePlan()===null,'incompatible revision readonly');
 cases.push('immutable baseline and incompatible revision');
 return {status:'PASS',assertions,cases,limitation:'Pure real-module probe; persistence/context adapters are synthetic. Full integration is reported separately.'};
}'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifact', type=Path)
    args = parser.parse_args()
    source = 'window.S={fxPlanning:{schemaVersion:1,auditLog:[],plan:null}};window.ledgerContext=()=>({});window.save=()=>true;window.jpWealthPersistenceOutcomeIsUnknown=()=>false;\n' + '\n'.join(p.read_text() for p in MODULES)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.add_script_tag(content=source)
        result = page.evaluate(PROBE)
        browser.close()
    result['sourceSha256'] = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in MODULES}
    if args.artifact:
        args.artifact.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()

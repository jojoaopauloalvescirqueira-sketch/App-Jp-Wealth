#!/usr/bin/env python3
"""NAV-REF-01: characterize the existing local navigation API, without app boot.

Explicit expectations apply to both baseline and candidate. The entire source is
loaded into Chromium with real minimal DOM and synthetic UI surfaces. A spy calls
the original navApply; no projection helper is exposed or invoked by this test.
Real renderers, focus and layout preferences need the existing integration tests.
"""
import argparse
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "src/js/40-app/01-navigation.js"
# Independent, literal oracle, fixed before the production transformation.
CASES = [
    ("exec", "overview", "forex-overview", "forex", "forex-overview"),
    ("exec", "panel", "forex-operation", "forex", "forex-operation"),
    ("exec", "motor", "forex-operation", "forex", "forex-operation"),
    ("exec", "history", "forex-reconciliation", "forex", "forex-reconciliation"),
    ("fxplan", "overview", "forex-planning", "forex", "forex-planning"),
    ("fxplan", "planning", "forex-planning", "forex", "forex-planning"),
    ("fxplan", "actuals", "forex-planning", "forex", "forex-planning"),
    ("fxplan", "table", "forex-planning", "forex", "forex-planning"),
    ("finpes", "overview", "personal-finance", "personal-finance", None),
    ("finpes", "mensal", None, "personal-finance", None),
    ("finpes", "dividas", None, "personal-finance", None),
    ("finpes", "comparativo", None, "personal-finance", None),
    ("finpes", "cenarios", None, "personal-finance", None),
    ("research", "calendar", "research-forex", "research", "research-forex"),
    ("research", "nocoda", "research-forex", "research", "research-forex"),
    ("research", "pivots", "research-forex", "research", "research-forex"),
    ("research", "stocks-br", "research-stocks-br", "research", "research-stocks-br"),
    ("research", "stocks-global", "research-stocks-global", "research", "research-stocks-global"),
    ("research", "reits", "research-reits", "research", "research-reits"),
    ("research", "probability-lab", "research-probability-lab", "research", "research-probability-lab"),
    ("research", "others", "research-others", "research", "research-others"),
]

PRELUDE = r"""
window.__navTest={events:[],reads:0,denied:[],fault:null};
function copy(value){return JSON.parse(JSON.stringify(value));}
function event(kind,extra={}){__navTest.events.push({kind,...extra});}
function snapshot(){return {current:JPWNavigation.current(),
  screens:[...document.querySelectorAll('#appMain > .screen.active')].map(e=>e.id),
  primary:[...document.querySelectorAll('#nav > .tab.active')].map(e=>e.dataset.primary),
  aria:[...document.querySelectorAll('#nav > .tab[aria-current="page"]')].map(e=>e.dataset.primary)};}
for(const [id,name] of Object.entries({exec:'JPWExec',finpes:'JPWFin',fxplan:'JPWFx',research:'JPWResearch'})){
  const ui={selectView(view){event('select',{surface:id,view,...snapshot()});},
    getView(){event('getView');return 'overview';}};
  window[name]={get ui(){
    __navTest.reads++; event('resolve',{surface:id});
    if(__navTest.fault==='absent-ui'||(__navTest.fault==='late-ui'&&__navTest.reads===2))return null;
    if(__navTest.fault==='missing-select')return {};
    return ui;
  }};
}
function scheduleNavPill(){event('pill',{current:JPWNavigation.current()});}
window.scrollTo=options=>event('scroll',{options});
function maybeShowOnboardingNavReminder(screen){event('reminder',{screen});}
function syncNavSubState(){event('sub',{current:JPWNavigation.current()});}
function syncActiveScreen(){event('active',{current:JPWNavigation.current()});}
function forbidden(name){__navTest.denied.push(name);throw new Error('Unexpected access: '+name);}
Object.defineProperty(window,'S',{get(){return forbidden('S');},set(){forbidden('S write');}});
Object.defineProperty(window,'localStorage',{get(){return forbidden('localStorage');}});
Object.defineProperty(window,'sessionStorage',{get(){return forbidden('sessionStorage');}});
window.save=()=>forbidden('save');
"""

SPY = r"""
const originalApply=navApply;
navApply=function(plan,target){
  if(__navTest.fault==='wrong-identity')plan={...plan,canonical:'forex-overview'};
  event('apply',{plan:copy(plan),target,last:copy(navLastResult)});
  const result=originalApply(plan,target);
  if(__navTest.fault==='duplicate-apply')originalApply(plan,target);
  return __navTest.fault==='false-return'?false:result;
};
window.__exercise=(surface,view)=>{
  __navTest.events=[]; __navTest.reads=0;
  const before=snapshot(), lastBefore=copy(navLastResult);
  const accepted=JPWNavigation.navigateLocal(surface,view);
  return {before,lastBefore,accepted,after:snapshot(),lastAfter:copy(navLastResult),
    events:copy(__navTest.events),reads:__navTest.reads,denied:copy(__navTest.denied)};
};
"""


def plan_for(case):
    surface, view, canonical, primary, child = case
    return dict(accepted=True, requested=f"{surface}:{view}",
                source="local" if canonical else "compatibility", canonical=canonical,
                primary=primary, child=child, screen=surface,
                localView=dict(surface=surface, view=view))


def check_success(result, case):
    plan = plan_for(case)
    current = {k: v for k, v in plan.items() if k != "accepted"}
    events = result["events"]
    assert result["accepted"] is True, result
    assert [e["kind"] for e in events] == [
        "resolve", "apply", "resolve", "resolve", "select", "pill",
        "scroll", "reminder", "sub", "active"], events
    assert events[1] == dict(kind="apply", plan=plan, target=case[0],
                             last=dict(accepted=False, reason="not-applied")), events[1]
    assert result["reads"] == 3
    assert events[4] == dict(kind="select", surface=case[0], view=case[1],
                             current=result["before"]["current"], screens=[case[0]],
                             primary=[case[3]], aria=[case[3]]), events[4]
    assert events[5] == dict(kind="pill", current=current)
    assert events[6] == dict(kind="scroll", options=dict(top=0, behavior="smooth"))
    assert events[7] == dict(kind="reminder", screen=case[0])
    assert events[8] == dict(kind="sub", current=current)
    assert events[9] == dict(kind="active", current=current)
    assert result["after"] == dict(current=current, screens=[case[0]],
                                    primary=[case[3]], aria=[case[3]])
    assert result["lastAfter"] == dict(accepted=True, reason=None)
    assert result["denied"] == []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    source = (args.source_root / SOURCE).read_text(encoding="utf-8")
    records, failures, blocked = [], [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(service_workers="block")

        def abort(route):
            blocked.append(route.request.url)
            route.abort()

        context.route("**/*", abort)

        def new_page():
            page = context.new_page()
            page.on("pageerror", lambda error: failures.append(f"pageerror: {error}"))
            page.on("console", lambda message: failures.append(f"console: {message.text}")
                    if message.type == "error" else None)
            tabs = "".join(f'<button class="tab" data-primary="{p}" data-route="{p}">{p}</button>'
                           for p in ("dashboard", "forex", "personal-finance", "research", "alladin"))
            screens = "".join(f'<section class="screen{a}" id="{s}"><h1>{s}</h1></section>'
                              for s, a in [("dash", " active"), ("exec", ""), ("fxplan", ""),
                                           ("finpes", ""), ("research", ""), ("contab", ""),
                                           ("alladin", ""), ("check", ""), ("contas", "")])
            page.set_content(f'<nav id="nav">{tabs}</nav><main id="appMain">{screens}</main>')
            page.add_script_tag(content=PRELUDE)
            page.add_script_tag(content=source)
            page.add_script_tag(content=SPY)
            assert page.evaluate("Object.keys(JPWNavigation)") == [
                "routes", "children", "resolve", "navigate", "navigateLocal", "current", "focusCurrentScreen"]
            return page

        def run(name, function):
            try:
                function()
                print(f"PASS {name}", flush=True)
            except Exception as error:
                failures.append(f"{name}: {error}")
                print(f"FAIL {name}: {error}", flush=True)

        page = new_page()
        for case in CASES:
            def valid(case=case):
                # Sequential destinations plus immediate repetition, no fake deduplication.
                for repetition in range(2):
                    result = page.evaluate("([s,v])=>__exercise(s,v)", list(case[:2]))
                    records.append(dict(name=f"{case[0]}:{case[1]}:{repetition}", result=result))
                    check_success(result, case)
            run(f"{case[0]}:{case[1]} + repeat", valid)
        page.close()

        negatives = [("unknown", "overview"), ("alladin", "overview"), (None, "overview"),
                     ("exec", "unknown"), ("exec", None), ("exec", ""), ("exec", 0),
                     ("exec", "@current"), ("finpes", "panel"), ("research", "overview")]
        for surface, view in negatives:
            def negative(surface=surface, view=view):
                p = new_page()
                try:
                    # Establish a prior successful non-default state/result.
                    p.evaluate("JPWNavigation.navigateLocal('exec','motor')")
                    result = p.evaluate("([s,v])=>__exercise(s,v)", [surface, view])
                    records.append(dict(name=f"guard:{surface}:{view}", result=result))
                    assert result["accepted"] is False
                    assert result["after"] == result["before"]
                    assert result["lastAfter"] == result["lastBefore"]
                    assert [e["kind"] for e in result["events"]] == (
                        ["resolve"] if surface in ("exec", "finpes", "fxplan", "research") else [])
                    assert not result["denied"]
                finally:
                    p.close()
            run(f"guard {surface!r}:{view!r}", negative)

        for fault in ("absent-ui", "missing-select", "late-ui", "missing-screen", "missing-primary"):
            def unavailable(fault=fault):
                p = new_page()
                try:
                    p.evaluate("JPWNavigation.navigateLocal('finpes','mensal')")
                    p.evaluate("f=>__navTest.fault=f", fault)
                    if fault == "missing-screen":
                        p.evaluate("document.getElementById('exec').remove()")
                    if fault == "missing-primary":
                        p.evaluate("document.querySelector('[data-primary=forex]').remove()")
                    result = p.evaluate("__exercise('exec','history')")
                    records.append(dict(name=fault, result=result))
                    assert result["accepted"] is False
                    assert result["after"] == result["before"]
                    if fault in ("absent-ui", "missing-select"):
                        assert [e["kind"] for e in result["events"]] == ["resolve"]
                        assert result["lastAfter"] == result["lastBefore"]
                    else:
                        kinds = ["resolve", "apply"] + (["resolve"] if fault == "late-ui" else []) + ["active"]
                        assert [e["kind"] for e in result["events"]] == kinds
                        assert result["events"][1]["plan"] == plan_for(CASES[3])
                        assert result["events"][1]["target"] == "exec"
                        assert result["events"][-1]["current"] == result["before"]["current"]
                        assert result["lastAfter"] == dict(accepted=False, reason="unavailable-target")
                    assert not result["denied"]
                finally:
                    p.close()
            run(fault, unavailable)

        def canonical_history():
            p = new_page()
            try:
                assert p.evaluate("JPWNavigation.navigate('forex-reconciliation')") is True
                assert p.evaluate("JPWNavigation.current()") == dict(
                    canonical="forex-reconciliation", requested="forex-reconciliation", source="canonical",
                    primary="forex", child="forex-reconciliation", screen="contab", localView=None)
                result = p.evaluate("__exercise('exec','history')")
                check_success(result, CASES[3])
                records.append(dict(name="canonical-contab/local-exec", result=result))
            finally:
                p.close()
        run("canonical Apuracao != local history", canonical_history)

        def returned_flag():
            p = new_page()
            try:
                p.evaluate("__navTest.fault='false-return'")
                result = p.evaluate("__exercise('exec','motor')")
                check_success(result, CASES[2])  # navApply return differs from navLastResult.
                records.append(dict(name="return-from-last-result", result=result))
            finally:
                p.close()
        run("public return derives from last result", returned_flag)

        for fault in ("wrong-identity", "duplicate-apply"):
            def counterexample(fault=fault):
                p = new_page()
                try:
                    p.evaluate("f=>__navTest.fault=f", fault)
                    result = p.evaluate("__exercise('exec','history')")
                    detected = False
                    try:
                        check_success(result, CASES[3])
                    except AssertionError:
                        detected = True
                    records.append(dict(name=f"counterexample:{fault}", detected=detected, result=result))
                    assert detected, "The unchanged oracle missed the synthetic violation"
                finally:
                    p.close()
            run(f"oracle detects {fault}", counterexample)
        browser.close()
    if blocked:
        failures.append(f"Unexpected network requests: {blocked}")
    report = dict(source_root=str(args.source_root.resolve()),
                  source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  valid_pairs=len(CASES), observations=records, network_attempts=blocked, failures=failures)
    if args.evidence:
        # Do not overwrite previous runs. The caller provides the existing evidence directory.
        with args.evidence.open("x", encoding="utf-8") as output:
            json.dump(report, output, ensure_ascii=False, indent=2)
            output.write("\n")
    for failure in failures:
        print(f"PRODUCT_FAIL: {failure}")
    print(f"{'FAIL' if failures else 'PASS'}: {len(CASES)} valid pairs + repetition, "
          f"{len(negatives)} guards, 5 unavailable paths, canonical distinction, return and 2 counterexamples")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

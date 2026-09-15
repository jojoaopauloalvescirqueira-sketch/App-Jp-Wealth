#!/usr/bin/env python3
"""Execution Board: real UI, synthetic data, existing isolated bootstrap fixtures.

Run the capability case against the unchanged baseline before implementation.
Every case uses assertions and contributes to the process exit status; screenshots
are supporting evidence, never the pass criterion. No live economic API is used.
"""
import argparse
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from notes_launcher_test import launch_options, settle


ROOT = Path(__file__).resolve().parents[1]
RATES = {"EURUSD": 1.25, "GBPUSD": 1.5, "AUDUSD": .625, "NZDUSD": .5,
         "USDJPY": 150, "USDCHF": .9, "USDCAD": 1.25, "AUDCAD": .78125, "USDBRL": 5}
SEED = r"""() => {
  window.__onbShown=true;closeModal();window.__ebAlerts=[];
  window.alert=m=>__ebAlerts.push(String(m));window.confirm=()=>true;
  const instruments=structuredClone(S.instruments);
  S=structuredClone(DEFAULTS);migrate();S.instruments=instruments;S.onboarding.done=true;
  S.accounts=[
    {forexAccountId:'eb_A',nome:'Mestre sintética EB',tipo:'MESTRE',broker:'Synthetic Broker',platform:'MT5',platformLogin:'10001',sini:10000,satu:9700,perfil:'Base'},
    {forexAccountId:'eb_B',nome:'Conta B sintética EB',tipo:'PRÓPRIA',broker:'Synthetic Broker',platform:'MT5',platformLogin:'20002',sini:5000,satu:4500,perfil:'Base'}
  ];
  S.forex=JPWForex.state.empty();S.forex.activeAccountId='eb_A';
  S.forex.accounts={eb_A:{si:10000,equity:9700,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',periodId:'period_A',capitalNominal:10000,source:'Synthetic observation',observedAt:'2026-09-15T12:00:00Z'},
    eb_B:{si:5000,equity:4500,netCashflow:0,cashflowAdjustmentRecorded:true,currency:'USD',periodId:'period_B',capitalNominal:5000,source:'Synthetic observation',observedAt:'2026-09-15T12:00:00Z'}};
  S.phases=JPWForex.state.newOperationPhases();S.activeOperation=null;
  S.operationHistory={schemaVersion:2,records:[]};S.transitionLog=[];
  S.personalFinance.syntheticUnrelated={value:'preserve'};S.dataGovernance.changeLog=[];
  if(save()!==true)throw Error('Synthetic fixture persistence refused');
  sessionEpochCurrent();markSessionCheckpoint();
  const originalSave=save,nativeSet=Storage.prototype.setItem,nativeGet=Storage.prototype.getItem;
  window.__eb={originalSave,nativeSet,nativeGet,calls:0,writes:0,mode:'normal'};
  Storage.prototype.setItem=function(k,v){
    if(this===localStorage&&k===LSKEY){__eb.writes++;if(__eb.mode==='quota')throw new DOMException('Synthetic quota','QuotaExceededError');}
    return nativeSet.call(this,k,v);
  };
  save=function(){__eb.calls++;if(__eb.mode==='false'){S.personalFinance.syntheticUnrelated.value='legitimate other flow';return false;}
    if(__eb.mode==='unknown')return undefined;return originalSave();};
  window.__ebSnapshot=()=>({phases:structuredClone(S.phases),operation:structuredClone(S.activeOperation),
    forex:structuredClone(S.forex),history:structuredClone(S.operationHistory),log:structuredClone(S.dataGovernance.changeLog),
    raw:nativeGet.call(localStorage,LSKEY),calls:__eb.calls,writes:__eb.writes,
    unknown:jpWealthPersistenceOutcomeIsUnknown(),unrelated:structuredClone(S.personalFinance.syntheticUnrelated)});
  render();JPWNavigation.navigate('forex-operation');renderPhases();
  return {account:'eb_A',period:'period_A',build:JP_WEALTH_BUILD_ID};
}"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def hashes(root):
    manifest = json.loads((root / "src/js/manifest.json").read_text())
    names = sorted({"index.html", "src/styles/app.css", "src/js/manifest.json", "build-id.js",
                    *(f["path"] for f in manifest["files"])})
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}


def field(page, key, pi=0, oi=0):
    return page.locator(f'[data-p="{pi}"][data-o="{oi}"][data-f="{key}"]')


def reveal(locator):
    """Expand only the actual containing detail controls before interacting."""
    locator.evaluate("e=>{let p=e.parentElement;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}}")


def fill_row(page, pi=0, oi=0, **overrides):
    values = dict(id="EB-SYNTHETIC", par="EURUSD", tipo="BUY", role="GENESIS", lote="0.01", entry="1.10",
                  sl="1.00", tp="1.20", status="Aberta", costs="0", costBasis="SEPARATE_FROM_RESULT", stopValidated=True)
    values.update(overrides)
    for key, value in values.items():
        el = field(page, key, pi, oi)
        reveal(el)
        tag = el.evaluate("e=>e.tagName")
        if isinstance(value, bool):
            el.set_checked(value)
        elif tag == "SELECT":
            el.select_option(str(value))
        else:
            el.fill(str(value))
            el.press("Tab")
    settle(page)


def save_row(page, pi=0, oi=0):
    page.locator(f'[data-eb-save-row="{pi}:{oi}"]').click()
    settle(page)


def cancel_row(page, pi=0, oi=0):
    page.locator(f'[data-eb-cancel-row="{pi}:{oi}"]').click()
    settle(page)


def reason(page, text="Correção sintética conjunta", pi=0, oi=0):
    el = page.locator(f'[data-eb-reason="{pi}:{oi}"]')
    reveal(el)
    el.fill(text)


def snapshot(page):
    return page.evaluate("__ebSnapshot()")


def equal_financial(before, after):
    for key in ("phases", "operation", "forex", "history", "log", "raw"):
        assert before[key] == after[key], f"Unexpected change in {key}"


def assert_pristine(page, before):
    assert snapshot(page) == before, "Typing/render/navigation changed persisted or confirmed state"


def capability(page, obs):
    obs["capabilities"] = page.evaluate("""() => ({board:!!document.getElementById('executionBoard'),
      account:!!document.getElementById('executionBoardAccount'),risk:!!document.getElementById('executionBoardRisk'),
      instruments:!!document.getElementById('executionBoardInstruments'),
      api:typeof JPWForex.executionBoardUI?.hasDrafts==='function'})""")
    assert all(obs["capabilities"].values()), "Execution Board capability absent: " + json.dumps(obs["capabilities"])
    assert page.locator("#executionBoard").is_visible()


def draft_commit_cancel(page, obs):
    before = snapshot(page)
    fill_row(page)
    assert_pristine(page, before)
    assert page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
    cancel_row(page)
    assert_pristine(page, before)
    assert not page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
    fill_row(page)
    save_row(page)
    after = snapshot(page)
    order = after["phases"][0]["orders"][0]
    assert order["status"] == "Aberta" and order["accountId"] == "eb_A" and order["periodId"] == "period_A"
    assert after["calls"] - before["calls"] == 1
    assert len(order["revisions"]) == 1 and order["recordVersion"] == 1
    assert json.loads(after["raw"])["phases"][0]["orders"][0] == order
    assert not page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
    saved = snapshot(page)
    field(page, "entry").fill("1.12");field(page, "entry").press("Tab")
    field(page, "sl").fill("1.02");field(page, "sl").press("Tab")
    assert_pristine(page, saved)
    save_row(page)
    assert_pristine(page, saved)
    assert page.locator('[data-eb-reason="0:0"]').evaluate("e=>document.activeElement===e")
    reason(page);save_row(page)
    corrected = snapshot(page);latest = corrected["phases"][0]["orders"][0]
    assert latest["entry"] == 1.12 and latest["sl"] == 1.02
    assert latest["orderId"] == order["orderId"] and len(latest["revisions"]) == 2
    assert latest["revisions"][-1]["reason"] == "Correção sintética conjunta"
    assert corrected["calls"] == saved["calls"] + 1
    obs.update(initial=before, recorded=after, corrected=corrected)


def refusal(mode):
    def run(page, obs):
        before = snapshot(page);fill_row(page)
        page.evaluate("mode=>__eb.mode=mode", mode)
        save_row(page)
        refused = snapshot(page)
        equal_financial(before, refused)
        assert refused["calls"] == before["calls"] + 1
        assert page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
        assert field(page, "entry").input_value() == "1.10"
        assert refused["unknown"] is False
        if mode == "false":
            assert refused["unrelated"]["value"] == "legitimate other flow"
        page.evaluate("__eb.mode='normal';S.personalFinance.syntheticUnrelated.afterRefusal=true;if(save()!==true)throw Error('Independent save failed')")
        independent = snapshot(page)
        assert json.loads(independent["raw"])["phases"] == before["phases"], "Unrelated save incorporated refused order"
        save_row(page)
        committed = snapshot(page)
        order = committed["phases"][0]["orders"][0]
        assert order["status"] == "Aberta" and len(order["revisions"]) == 1
        assert sum(o.get("recordStatus") == "recorded" for ph in committed["phases"] for o in ph["orders"]) == 1
        assert committed["calls"] == independent["calls"] + 1
        expected = committed["phases"]
        page.reload();wait_bootstrap(page);settle(page)
        assert page.evaluate("S.phases") == expected, "Reload altered confirmed orders"
        obs.update(before=before, refused=refused, independent=independent, committed=committed, reload=True)
    return run


def unknown(page, obs):
    fill_row(page);page.evaluate("__eb.mode='unknown'")
    save_row(page);first = snapshot(page)
    assert first["unknown"] and first["calls"] == 1
    assert page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
    # Calling the UI API exercises the guard even if the button is disabled.
    second_result = page.evaluate("JPWForex.executionBoardUI.saveRow(0,0)")
    second = snapshot(page)
    assert second == first, "Unknown result allowed blind retry or changed the attempted state"
    obs.update(first=first, second=second, retry=second_result)


def checklist(page, obs):
    before = snapshot(page);fill_row(page)
    node = field(page, "entry").element_handle()
    trigger = page.locator("#execChecklistBtn");trigger.focus();page.keyboard.press("Enter")
    page.locator("#forexChecklistDialog").wait_for(state="visible")
    assert page.locator("#checkWidgetGrid").count() == 1
    page.keyboard.press("Escape");settle(page)
    assert page.evaluate("document.activeElement.id") == "execChecklistBtn"
    assert node.evaluate("e=>e.isConnected") and field(page, "entry").input_value() == "1.10"
    assert_pristine(page, before)
    assert page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
    obs.update(draftPreserved=True, singleChecklist=True, focusReturned=True)


def close_order(page, obs):
    fill_row(page);save_row(page)
    before = snapshot(page)
    button = page.locator('[data-eb-close-row="0:0"]');reveal(button);button.click()
    page.locator("#modalOverlay.show").wait_for(state="visible")
    page.locator("#modalCancel").click();settle(page)
    assert_pristine(page, before)
    reveal(button);button.click()
    page.locator("#closeConfirmInput").fill("FECHADO")
    page.locator("#closeResultInput").fill("")
    page.locator("#modalConfirm").click();settle(page)
    assert page.locator('[data-qid="resultado"] .modal-err.show').is_visible()
    assert_pristine(page, before)
    page.locator("#closeResultInput").fill("0")
    page.locator("#modalConfirm").click();settle(page)
    after = snapshot(page);order = after["phases"][0]["orders"][0]
    assert order["status"] == "Fechada" and order["result"] == 0
    assert len(order["revisions"]) == 2 and after["calls"] == before["calls"] + 1
    assert not page.locator("#modalOverlay").is_visible()
    assert page.evaluate("JPWForex.state.read().executionEligibility.status") == "BLOCKED"
    obs.update(blankResultRefused=True, explicitZeroAccepted=True, before=before, closed=after)


def metrics_and_identity(page, obs):
    result = page.evaluate("""() => {
      const a=operationRecordOrder(0,0,{id:'EB-OPEN',par:'EURUSD',tipo:'BUY',role:'GENESIS',
        lote:.05,entry:1.1,sl:1,status:'Aberta',stopValidated:true,costs:0,costBasis:'SEPARATE_FROM_RESULT'},
        {reason:'Synthetic current open fact'});
      const b=operationRecordOrder(1,0,{id:'EB-CLOSED',par:'EURUSD',tipo:'BUY',role:'DEFENSE',
        lote:.01,entry:1.1,sl:1,status:'Fechada',result:200,costs:0,costBasis:'INCLUDED_IN_RESULT'},
        {reason:'Synthetic closed defense'});
      render();renderPhases();return {a,b,model:JPWForex.executionBoard.read()};
    }""")
    assert result["a"]["ok"] and result["b"]["ok"], result
    model = result["model"]
    assert abs(model["risk"]["open"]["value"] - 500) < 1e-7
    assert model["economics"]["closedNetAll"]["value"] == 200
    assert abs(model["economics"]["compensatedAll"]["value"] - 300) < 1e-7
    assert page.evaluate("JPWForex.state.read().executionEligibility.status") == "BLOCKED"
    assert page.evaluate("JPWForex.state.read().metrics.sizingTrace.finalVolume") is None
    before = snapshot(page)
    page.evaluate("S.forex.activeAccountId='eb_B';render();JPWForex.executionBoardUI.render()")
    identity = page.locator("#executionBoardAccount").inner_text()
    assert "Mestre sintética EB" in identity and "Conta B sintética EB" not in identity, identity
    assert page.evaluate("S.activeOperation.recordContext.accountId") == "eb_A"
    after = snapshot(page)
    assert after["phases"] == before["phases"] and after["raw"] == before["raw"]
    assert after["calls"] == before["calls"]
    obs.update(model=model, existingOperationKeepsAccount=True, accountText=identity)


def proposed_master(page, obs):
    page.evaluate("S.forex.activeAccountId='eb_B';render();JPWForex.executionBoardUI.render()")
    before = snapshot(page)
    assert page.locator("#ebAccountSelect").input_value() == "eb_A"
    assert page.evaluate("S.forex.activeAccountId") == "eb_B", "Master proposal silently switched account"
    assert_pristine(page, before)
    fill_row(page);save_row(page)
    after = snapshot(page)
    assert after["operation"]["recordContext"]["accountId"] == "eb_A"
    assert after["phases"][0]["orders"][0]["accountId"] == "eb_A"
    assert after["forex"]["accounts"]["eb_B"] == before["forex"]["accounts"]["eb_B"]
    obs.update(before=before, after=after, masterProposedOnlyUntilSave=True)


def source_update_preserves_draft(page, obs):
    fill_row(page)
    node = field(page, "entry").element_handle()
    field(page, "entry").focus()
    before = snapshot(page)
    result = page.evaluate("""() => JPWForex.state.recordInstrumentContext({accountId:'eb_A',periodId:'period_A',
      instrumentId:'EURUSD',expectedRevision:0,componentChanges:{
        price:{value:1.25,source:'Synthetic manual quote',observedAt:'2026-09-15T12:00:00Z'},
        contract:{contractSize:100000,source:'Synthetic specification',observedAt:'2026-09-15T12:00:00Z'},
        atr:{short:.012,long:.01,timeframe:'H4',unit:'PRICE',source:'Synthetic H4 candles',observedAt:'2026-09-15T12:00:00Z'}
      }},{reason:'Synthetic instrument observation',expectedEpoch:jpWealthPersistenceEpoch()})""")
    assert result["ok"], result
    page.evaluate("JPWForex.executionBoardUI.render()");settle(page)
    assert node.evaluate("e=>e.isConnected&&document.activeElement===e"), "Quote refresh rebuilt/focused away from live draft"
    assert field(page, "entry").input_value() == "1.10"
    assert page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
    after = snapshot(page)
    assert after["phases"] == before["phases"] and after["operation"] == before["operation"]
    assert after["calls"] == before["calls"] + 1, "Observation refresh caused another save"
    obs.update(observation=result, rowDOMPreserved=True, draftPreserved=True)


def changed_confirmed_row(page, obs):
    """A newer confirmed fact must win over a stale in-memory editor."""
    fill_row(page);save_row(page)
    field(page, "entry").fill("1.12");field(page, "entry").press("Tab")
    reason(page, "Correção sintética ainda em rascunho")
    changed = page.evaluate("""() => operationRecordOrder(0,0,{entry:1.15},
      {reason:'Synthetic intervening confirmed correction'})""")
    assert changed["ok"], changed
    before = snapshot(page)
    save_row(page)
    assert_pristine(page, before)
    assert page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
    assert field(page, "entry").input_value() == "1.12"
    assert "mudou" in page.locator("#ebError-0-0").inner_text()
    cancel_row(page)
    assert_pristine(page, before)
    assert float(field(page, "entry").input_value()) == 1.15
    assert not page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
    obs.update(interveningChange=changed, staleSaveRefused=True, confirmedVersion=before["phases"][0]["orders"][0]["recordVersion"])


def navigation(choice):
    def run(page, obs):
        before = snapshot(page);fill_row(page)
        page.evaluate("JPWNavigation.navigate('dashboard')")
        page.locator("#executionBoardDialog").wait_for(state="visible")
        assert page.evaluate("JPWNavigation.current().canonical") == "forex-operation"
        page.locator("#ebLeave" + choice.title()).click();settle(page)
        after = snapshot(page)
        current = page.evaluate("JPWNavigation.current().canonical")
        if choice == "stay":
            assert current == "forex-operation"
            assert page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
            assert_pristine(page, before)
        elif choice == "discard":
            assert current == "dashboard"
            assert not page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
            assert_pristine(page, before)
        else:
            assert current == "dashboard" and after["calls"] == before["calls"] + 1
            assert after["phases"][0]["orders"][0]["status"] == "Aberta"
            assert not page.evaluate("JPWForex.executionBoardUI.hasDrafts()")
        obs.update(choice=choice, before=before, after=after, destination=current)
    return run


def phase_geometry(page, obs, directory):
    assert page.locator("#phaseContainer .phase[data-phase]").count() == 6
    before = snapshot(page)
    measured = []
    for width, theme in [(1440, "light"), (1440, "dark"), (768, "light"), (720, "light"), (390, "light"), (390, "dark")]:
        page.set_viewport_size({"width": width, "height": 960})
        page.evaluate("t=>document.documentElement.dataset.theme=t", theme);settle(page)
        bounds = page.locator("#executionBoard").evaluate("e=>{const r=e.getBoundingClientRect();return {width:r.width,height:r.height,left:r.left,right:r.right}}")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), "Document horizontal overflow"
        assert bounds["left"] >= -1 and bounds["right"] <= width + 1, bounds
        for selector in ("#executionBoardAccount", "#executionBoardRisk", "#executionBoardInstruments", "#execChecklistBtn"):
            assert page.locator(selector).is_visible(), selector
        title_size = page.locator("#executionBoard").evaluate("e=>parseFloat(getComputedStyle(e).fontSize)")
        assert title_size >= 12, "Board text shrunk to fit instead of using responsive structure"
        checklist_bounds = page.locator("#execChecklistBtn").bounding_box()
        icon_bounds = page.locator("#execChecklistBtn svg").bounding_box()
        path = directory / f"execution-board-{width}-{theme}.png"
        page.screenshot(path=str(path), full_page=True)
        measured.append(dict(width=width, theme=theme, board=bounds, checklist=checklist_bounds,
                             icon=icon_bounds, screenshot=path.name))
    obs["measured"] = measured
    for view in measured:
        assert view["checklist"] and 32 <= view["checklist"]["height"] <= 56, "Checklist control must retain compact, usable height: " + str(view)
        assert view["icon"] and 12 <= view["icon"]["width"] <= 28 and 12 <= view["icon"]["height"] <= 28, "Checklist icon lost its dimensions: " + str(view)
        assert view["board"]["height"] <= (140 if view["width"] == 1440 else 240), "Board heading regained excess whitespace: " + str(view)
    assert_pristine(page, before)
    page.evaluate("window.__six=structuredClone(S.phases);S.phases=structuredClone(S.phases.slice(0,4));S.phases.forEach((p,i)=>{p.policyVersion='LEGACY_UNRESOLVED';p.title='LEGACY '+i});window.__legacy=JSON.stringify(S.phases);renderPhases();JPWForex.executionBoardUI.render()")
    assert page.locator("#phaseContainer .phase[data-phase]").count() == 4
    assert "LEGACY" in page.locator("#phaseContainer").inner_text()
    assert page.evaluate("JSON.stringify(S.phases)===__legacy"), "Rendering reinterpreted legacy grades"
    obs.update(measured=measured, legacyPreserved=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--capability-only", action="store_true")
    ap.add_argument("--case", default="")
    ap.add_argument("--portable", action="store_true")
    args = ap.parse_args();root = args.root.resolve()
    args.out.mkdir(parents=True, exist_ok=False)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    target = "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html" if args.portable else "index.html"
    report = {"suite": "forex-execution-board", "root": str(root), "target": target,
              "environment": "Existing Chromium; isolated contexts; local server; named synthetic network fixtures",
              "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "inputs_before": hashes(root), "cases": []}
    cases = [("capability", capability)] if args.capability_only else [
        ("capability", capability), ("draft-save-cancel-one-reason", draft_commit_cancel),
        ("refusal-false-unrelated-retry-reload", refusal("false")),
        ("refusal-quota-unrelated-retry-reload", refusal("quota")),
        ("unknown-no-blind-retry", unknown), ("checklist-preserves-draft-focus", checklist),
        ("close-order-explicit-result-and-cancel", close_order),
        ("metrics-existing-account-identity", metrics_and_identity), ("master-proposal-new-operation", proposed_master),
        ("instrument-source-update-preserves-draft", source_update_preserves_draft),
        ("changed-confirmed-row-refuses-stale-draft", changed_confirmed_row),
        *(("navigation-" + v, navigation(v)) for v in ("stay", "discard", "save")),
        ("geometry-and-legacy", lambda p, o: phase_geometry(p, o, args.out))]
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            for name, callback in cases:
                if args.case and args.case not in name:
                    continue
                row = {"name": name, "observations": {}, "pageerrors": [], "console": []}
                ctx = browser.new_context(viewport={"width": 1440, "height": 960}, service_workers="block", reduced_motion="reduce")
                page = None
                try:
                    install_bootstrap(ctx, RATES);ctx.add_init_script("window.__onbShown=true;")
                    page = ctx.new_page();page.set_default_timeout(5000)
                    page.on("pageerror", lambda e, row=row: row["pageerrors"].append(str(e)))
                    page.on("console", lambda m, row=row: row["console"].append({"type": m.type, "text": m.text}))
                    page.goto(f"http://127.0.0.1:{server.server_port}/{target}");wait_bootstrap(page)
                    row["build"] = page.evaluate("JP_WEALTH_BUILD_ID")
                    if name == "capability":
                        page.evaluate("JPWNavigation.navigate('forex-operation')")
                    else:
                        row["seed"] = page.evaluate(SEED)
                    callback(page, row["observations"])
                    assert_fixture_requests(ctx)
                    assert not row["pageerrors"], row["pageerrors"]
                    allowed = ["JP Wealth: falha ao gravar"] if "quota" in name else []
                    if name.startswith("unknown"):
                        allowed += ["[persistência] DESFECHO INDETERMINADO"]
                    unexpected = [m for m in row["console"] if m["type"] == "error" and not any(x in m["text"] for x in allowed)]
                    assert not unexpected, unexpected
                    row["expected_console"] = allowed;row["result"] = "PASS"
                except Exception as error:
                    row.update(result="PRODUCT_FAIL", error=str(error), traceback=traceback.format_exc())
                    if page is not None:
                        try:
                            page.screenshot(path=str(args.out / (name + "-failure.png")), full_page=True)
                            row["active"] = page.evaluate("document.querySelector('#appMain>.screen.active')?.id")
                        except Exception:
                            pass
                finally:
                    ctx.close();report["cases"].append(row)
                    print(json.dumps({"name": name, "result": row["result"], "error": row.get("error")}, ensure_ascii=False), flush=True)
                if name == "capability" and row["result"] != "PASS":
                    break
            browser.close()
    except Exception as error:
        report["cases"].append({"name": "environment", "result": "ENVIRONMENT_ERROR", "error": str(error), "traceback": traceback.format_exc()})
    finally:
        server.shutdown();report["inputs_after"] = hashes(root)
        report["source_unchanged"] = report["inputs_before"] == report["inputs_after"]
        report["passed"] = sum(x["result"] == "PASS" for x in report["cases"])
        report["total"] = len(report["cases"])
        if not report["source_unchanged"]:
            report["result"] = "INPUTS_CHANGED"
        elif any(x["result"] == "ENVIRONMENT_ERROR" for x in report["cases"]):
            report["result"] = "ENVIRONMENT_ERROR"
        elif not report["total"]:
            report["result"] = "NO_CASES_SELECTED"
        else:
            report["result"] = "PASS" if report["passed"] == report["total"] else "PRODUCT_FAIL"
        (args.out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

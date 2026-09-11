#!/usr/bin/env python3
"""Civil dates on ledger acts and historical read quality; stored bytes are untouched.

The fixed table is the oracle, not the implementation's private validator.
--root allows the exact same test to falsify the preserved baseline first.
Domain cases use the existing synthetic fixture; UI cases use real save/storage
and the existing nominal bootstrap resources, never live economic APIs.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright


INVALID = ["2026-99-99", "2026-00-10", "2026-01-00", "2026-04-31",
           "2026-02-29", "2026-02-30", "1900-02-29", "2100-02-29",
           "2026-11-31", "28/02/2026", "2026-2-28", "2026-02-28T00:00:00Z",
           " 2026-02-28", "2026-02-28 ", "", None, 20260228, {}, []]
VALID = ["2026-01-31", "2026-04-30", "2026-02-28", "2024-02-29",
         "2000-02-29", "1900-02-28", "2100-02-28", "1990-01-01",
         "2099-12-31", "0000-01-01"]
# 0000 preserves the pre-existing four-digit representation; this slice does
# not establish a new minimum year or a policy about historical/future dates.


def load(root, name):
    spec = importlib.util.spec_from_file_location(name, root / "tools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    ledger = load(root, "alladin_ledger_test")
    ui = load(root, "alladin_ui_tx_write_test")
    bootstrap = load(root, "browser_bootstrap_fixture")
    source = root / "src/js/10-domain/13-alladin.js"
    result = {"root": str(root), "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "oracle": {"invalid": INVALID, "valid": VALID}, "checks": []}

    def check(name, fn):
        try:
            detail = fn()
            result["checks"].append({"name": name, "status": "PASS", "detail": detail})
        except Exception as exc:
            result["checks"].append({"name": name, "status": "FAIL", "error": str(exc)})

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        domain = browser.new_context(service_workers="block")
        domain.route("**/*", lambda route: route.abort("blockedbyclient"))
        page = domain.new_page()
        page.goto("about:blank")
        page.add_script_tag(content=ledger.PRELUDE)
        page.add_script_tag(content=source.read_text())
        page.evaluate("""() => {
          window.__idCalls=0;
          const originalId=aldId;
          aldId=function(){window.__idCalls++;return originalId.apply(this,arguments);};
          const originalSave=save;
          save=function(){const ok=originalSave();if(ok===true)window.__disk=JSON.stringify(S);return ok;};
        }""")

        def domain_case(value, operation, valid):
            observed = page.evaluate("""({value,operation}) => {
              const f=fixture(), L=JPWAlladin.ledger;
              let id;
              if(operation==='reverse') id=L.addTransaction({eventType:'DEPOSIT',cashAccountId:f.caixaXP,
                amount:100,effectiveAt:'2026-01-10'}).recordId;
              // An existing log at its cap must not be truncated by rejection.
              S.dataGovernance.changeLog=Array.from({length:400},(_,i)=>({action:'before-'+i}));
              save();
              const before=JSON.stringify(S), disk=window.__disk, ids=window.__idCalls,
                    saves=window.__stub.saves, count=S.alladin.transactions.length;
              const r=operation==='reverse'?L.reverseTransaction(id,{effectiveAt:value}):
                L.addTransaction({eventType:'DEPOSIT',cashAccountId:f.caixaXP,amount:100,effectiveAt:value});
              return {r,unchanged:JSON.stringify(S)===before,diskUnchanged:window.__disk===disk,
                idDelta:window.__idCalls-ids,saveDelta:window.__stub.saves-saves,
                countDelta:S.alladin.transactions.length-count,stored:S.alladin.transactions.at(-1)?.effectiveAt,
                diskEqualsMemory:window.__disk===JSON.stringify(S),
                balance:JPWAlladin.leitura.saldoDeCaixa(f.caixaXP).amount};
            }""", {"value": value, "operation": operation})
            r = observed["r"]
            if valid:
                require(r.get("ok") is True and r.get("persistido") is True, str(observed))
                require(observed["stored"] == value and observed["countDelta"] == 1, str(observed))
                require(observed["idDelta"] == 1 and observed["saveDelta"] == 1, str(observed))
                require(observed["diskEqualsMemory"] and observed["balance"] == (0 if operation == "reverse" else 100), str(observed))
            else:
                require(r == {"ok": False, "persistido": False, "erro": "ALD_EFFECTIVE_AT_INVALIDA"}, str(observed))
                require(observed["unchanged"] and observed["diskUnchanged"], str(observed))
                require(observed["idDelta"] == observed["saveDelta"] == observed["countDelta"] == 0, str(observed))
            return observed

        for operation in ("add", "reverse"):
            for index, value in enumerate(INVALID):
                check(f"domain-{operation}-invalid-{index}", lambda v=value, op=operation: domain_case(v, op, False))
            for index, value in enumerate(VALID):
                check(f"domain-{operation}-valid-{index}", lambda v=value, op=operation: domain_case(v, op, True))

        def all_event_types():
            observed = page.evaluate("""() => {
              const f=fixture(), L=JPWAlladin.ledger;
              const out=[];
              for(const eventType of ['DEPOSIT','WITHDRAWAL','TRANSFER','BUY','SELL','FEE','TAX','ADJUSTMENT_CREDIT','ADJUSTMENT_DEBIT']){
                const d={eventType,amount:100,effectiveAt:'2026-02-30'};
                if(eventType==='TRANSFER'){d.sourceCashAccountId=f.caixaXP;d.destinationCashAccountId=f.caixaBTG;}
                else d.cashAccountId=f.caixaXP;
                if(eventType==='BUY'||eventType==='SELL'){d.instrumentId=f.petr4;d.quantity='1';}
                if(eventType.startsWith('ADJUSTMENT'))d.reason='synthetic adjustment';
                const before=JSON.stringify(S),disk=window.__disk,saves=window.__stub.saves;
                const r=L.addTransaction(d);
                out.push({eventType,r,unchanged:before===JSON.stringify(S),diskUnchanged:disk===window.__disk,
                  saveDelta:window.__stub.saves-saves});
              }
              return out;
            }""")
            for item in observed:
                require(item["r"].get("erro") == "ALD_EFFECTIVE_AT_INVALIDA" and item["unchanged"]
                        and item["diskUnchanged"] and item["saveDelta"] == 0, str(item))
            return observed
        check("all-nine-event-types", all_event_types)

        def legacy(value, valid, reverse=False):
            observed = page.evaluate("""({value,reverse}) => {
              const f=fixture(),L=JPWAlladin.ledger;
              L.addTransaction({eventType:'DEPOSIT',cashAccountId:f.caixaXP,
                amount:1000,effectiveAt:'2026-01-01'});
              const buy=L.addTransaction({eventType:'BUY',cashAccountId:f.caixaXP,
                instrumentId:f.petr4,quantity:'1',amount:100,effectiveAt:'2026-01-02'});
              if(reverse)L.reverseTransaction(buy.recordId,{effectiveAt:'2026-01-03'});
              const target=S.alladin.transactions.at(-1);
              target.effectiveAt=value;save();
              const before=JSON.stringify(S),disk=window.__disk,saves=window.__stub.saves,ids=window.__idCalls;
              const tx=JPWAlladin.leitura.transactions(),cash=JPWAlladin.leitura.saldoDeCaixa(f.caixaXP),
                    positions=JPWAlladin.leitura.posicoes();
              return {tx,cash,positions,stored:tx.find(t=>t.transactionId===target.transactionId).effectiveAt,
                unchanged:before===JSON.stringify(S),diskUnchanged:disk===window.__disk,
                saveDelta:window.__stub.saves-saves,idDelta:window.__idCalls-ids};
            }""", {"value": value, "reverse": reverse})
            require(observed["unchanged"] and observed["diskUnchanged"] and observed["saveDelta"] == 0, str(observed))
            require(observed["stored"] == value and observed["idDelta"] == 0
                    and len(observed["tx"]) == (3 if reverse else 2), str(observed))
            cash, positions = observed["cash"], observed["positions"]
            if valid:
                require(cash["available"] and cash["quality"] == "OK" and cash["amount"] == (1000 if reverse else 900), str(observed))
                require(positions["available"] and positions["quality"] == "OK", str(observed))
                require([p["quantity"] for p in positions["positions"]] == ([] if reverse else ["1"]), str(observed))
            else:
                require(not cash["available"] and cash["quality"] == "BLOCKING" and cash["amount"] is None, str(observed))
                require(not positions["available"] and positions["quality"] == "BLOCKING" and not positions["positions"], str(observed))
                require("ALD_TRANSACAO_ILEGIVEL" in cash["issues"] and "ALD_TRANSACAO_ILEGIVEL" in positions["issues"], str(observed))
            return observed
        for index, value in enumerate(INVALID):
            check(f"legacy-invalid-{index}-blocking-preserved", lambda v=value: legacy(v, False))
        for index, value in enumerate(VALID):
            check(f"legacy-valid-{index}-readable-preserved", lambda v=value: legacy(v, True))
        check("legacy-reversal-invalid-blocking-preserved", lambda: legacy("2026-02-30", False, True))
        check("legacy-reversal-leap-day-readable-preserved", lambda: legacy("2024-02-29", True, True))
        domain.close()

        server, url = ui.serve()

        def browser_case(reverse=False):
            ctx = browser.new_context(viewport={"width": 1440, "height": 950}, service_workers="block")
            errors = []
            try:
                bootstrap.install_bootstrap(ctx)
                ctx.add_init_script("window.__onbShown=true;")
                p = ctx.new_page()
                p.on("pageerror", lambda error: errors.append(str(error)))
                p.goto(url, wait_until="load")
                p.wait_for_function(ui.PRONTO)
                bootstrap.wait_bootstrap(p)
                p.evaluate("() => {window.alert=()=>{};closeModal();}")
                ids = p.evaluate(ui.SEMEAR)
                if reverse:
                    original = p.evaluate("""cx=>JPWAlladin.ledger.addTransaction({eventType:'DEPOSIT',
                      cashAccountId:cx,amount:100,effectiveAt:'2026-01-10'}).recordId""", ids["cx"])
                    p.evaluate("() => JPWAlladinUI.render()")
                    p.locator(f"button[data-ald-tx-reverse='{original}']").click()
                    date_field, note_field = "alladinTxRevData", "alladinTxRevNota"
                else:
                    p.locator("button[data-ald-tx-new]").click()
                    p.select_option("#alladinTxConta", ids["cx"])
                    p.fill("#alladinTxValor", "1,00")
                    date_field, note_field = "alladinTxData", "alladinTxNota"
                p.fill("#" + date_field, "2026-02-30")
                p.fill("#" + note_field, "synthetic recoverable draft")
                p.evaluate("""() => {
                  window.__beforeMemory=JSON.stringify(S);window.__beforeDisk=localStorage.getItem('jpwealth_v9_state');
                  window.__beforeCount=S.alladin.transactions.length;
                  window.__dateSaveCalls=0;const prior=save;
                  save=function(){window.__dateSaveCalls++;return prior.apply(this,arguments);};
                }""")
                p.locator("button[data-ald-act=salvar]").click()
                refused = p.evaluate("""({date_field,note_field})=>({
                  open:document.getElementById('alladinModalOverlay').classList.contains('show'),
                  error:document.querySelector('#alladinModalBox .session-error')?.textContent||'',
                  date:document.getElementById(date_field)?.value,note:document.getElementById(note_field)?.value,
                  unchanged:window.__beforeMemory===JSON.stringify(S),
                  diskUnchanged:window.__beforeDisk===localStorage.getItem('jpwealth_v9_state'),
                  saveCalls:window.__dateSaveCalls})""", {"date_field": date_field, "note_field": note_field})
                require(refused["open"] and "Data inválida" in refused["error"], str(refused))
                require(refused["date"] == "2026-02-30" and refused["note"] == "synthetic recoverable draft", str(refused))
                require(refused["unchanged"] and refused["diskUnchanged"] and refused["saveCalls"] == 0, str(refused))
                # A save from an unrelated flow cannot materialize the refused fact.
                subsequent = p.evaluate("""() => {
                  const r=save();return {r,count:S.alladin.transactions.length,
                    diskCount:JSON.parse(localStorage.getItem('jpwealth_v9_state')).alladin.transactions.length,
                    expected:window.__beforeCount};
                }""")
                require(subsequent["r"] is True and subsequent["count"] == subsequent["diskCount"] == subsequent["expected"], str(subsequent))
                p.fill("#" + date_field, "2024-02-29")
                p.locator("button[data-ald-act=salvar]").click()
                completed = p.evaluate("""()=>({open:document.getElementById('alladinModalOverlay').classList.contains('show'),
                  count:S.alladin.transactions.length,expected:window.__beforeCount+1,
                  tx:JSON.stringify(S.alladin.transactions),log:JSON.stringify(S.dataGovernance.changeLog),
                  diskTx:JSON.stringify(JSON.parse(localStorage.getItem('jpwealth_v9_state')).alladin.transactions)})""")
                require(not completed["open"] and completed["count"] == completed["expected"] and completed["tx"] == completed["diskTx"], str(completed))
                p.reload(wait_until="load")
                p.wait_for_function(ui.PRONTO)
                bootstrap.wait_bootstrap(p)
                reloaded = p.evaluate("""()=>({tx:JSON.stringify(S.alladin.transactions),
                  log:JSON.stringify(S.dataGovernance.changeLog)})""")
                require(reloaded["tx"] == completed["tx"] and reloaded["log"] == completed["log"], str(reloaded))
                bootstrap.assert_fixture_requests(ctx)
                require(not errors, str(errors))
                return {"refused": refused, "subsequent": subsequent, "completed": completed, "reloaded": reloaded}
            finally:
                ctx.close()

        def browser_legacy():
            ctx = browser.new_context(viewport={"width": 1440, "height": 950}, service_workers="block")
            errors = []
            try:
                bootstrap.install_bootstrap(ctx)
                ctx.add_init_script("window.__onbShown=true;")
                p = ctx.new_page()
                p.on("pageerror", lambda error: errors.append(str(error)))
                p.goto(url, wait_until="load")
                p.wait_for_function(ui.PRONTO)
                bootstrap.wait_bootstrap(p)
                p.evaluate("() => {window.alert=()=>{};closeModal();}")
                ids = p.evaluate(ui.SEMEAR)
                original = p.evaluate("""ids => {
                  const L=JPWAlladin.ledger;
                  L.addTransaction({eventType:'DEPOSIT',cashAccountId:ids.cx,amount:1000,effectiveAt:'2026-01-01'});
                  L.addTransaction({eventType:'BUY',cashAccountId:ids.cx,instrumentId:ids.pe,
                    quantity:'1',amount:100,effectiveAt:'2026-01-02'});
                  S.alladin.transactions.at(-1).effectiveAt='2026-02-30';
                  if(save()!==true)throw new Error('synthetic historical fixture not saved');
                  return JSON.stringify(S.alladin);
                }""", ids)
                observations = []
                for reloaded in (False, True):
                    if reloaded:
                        p.reload(wait_until="load")
                        p.wait_for_function(ui.PRONTO)
                        bootstrap.wait_bootstrap(p)
                    observed = p.evaluate("""() => {
                      const before=JSON.stringify(S),disk=localStorage.getItem('jpwealth_v9_state');
                      let saves=0;const prior=save;
                      save=function(){saves++;return prior.apply(this,arguments);};
                      const views={};
                      try{
                        for(const [key,id] of [['ledger','alladinLedger'],['balances','alladinBalances'],['positions','alladinPositions']]){
                          JPWAlladinUI.selectView(key);
                          const el=document.getElementById(id);
                          views[key]={text:el.textContent,tables:el.querySelectorAll('table').length,
                            newActions:el.querySelectorAll('[data-ald-tx-new]').length};
                        }
                      }finally{save=prior;}
                      return {views,saves,unchanged:before===JSON.stringify(S),
                        diskUnchanged:disk===localStorage.getItem('jpwealth_v9_state'),
                        aggregate:JSON.stringify(S.alladin),
                        stored:JSON.stringify(JSON.parse(localStorage.getItem('jpwealth_v9_state')).alladin)};
                    }""")
                    require(observed["unchanged"] and observed["diskUnchanged"] and observed["saves"] == 0, str(observed))
                    require(observed["aggregate"] == observed["stored"] == original, str(observed))
                    for view in ("ledger", "positions"):
                        rendered = observed["views"][view]
                        require("indisponíveis" in rendered["text"] and "ALD_TRANSACAO_ILEGIVEL" in rendered["text"], str(observed))
                        require(rendered["tables"] == rendered["newActions"] == 0 and "Nenhum" not in rendered["text"], str(observed))
                    balances = observed["views"]["balances"]["text"]
                    require("Indisponível" in balances and "ALD_TRANSACAO_ILEGIVEL" in balances
                            and "R$" not in balances and "US$" not in balances, str(observed))
                    observations.append({"reloaded": reloaded, **observed})
                bootstrap.assert_fixture_requests(ctx)
                require(not errors, str(errors))
                return observations
            finally:
                ctx.close()

        try:
            check("ui-create-reject-correct-reload", browser_case)
            check("ui-reverse-posted-reject-correct-reload", lambda: browser_case(True))
            check("ui-legacy-invalid-blocking-preserved-reload", browser_legacy)
        finally:
            server.shutdown()
            server.server_close()
            browser.close()

    failures = [item for item in result["checks"] if item["status"] != "PASS"]
    result["summary"] = {"total": len(result["checks"]), "passed": len(result["checks"]) - len(failures), "failed": len(failures)}
    if args.artifact:
        with args.artifact.open("x") as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
    for failure in failures:
        print(failure["name"] + ": " + failure["error"])
    print("ALLADIN CIVIL DATE", "FAIL" if failures else "PASS", json.dumps(result["summary"]))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

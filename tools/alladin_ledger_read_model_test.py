#!/usr/bin/env python3
"""Additive ledger quality contract and V2 characterization, with synthetic data.

Run this same file with --root on the preserved V2 first: the missing ledger()
envelope and the corrupt direct preview should fail. --baseline-results compares the candidate's raw
DTOs, positions, balances and UI HTML against that recorded characterization.
No gate or existing test is replaced by this focused contract.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


SOURCES = ["src/js/10-domain/13-alladin.js", "src/js/20-ui/24-alladin-views.js",
           "src/js/20-ui/25-dash-macro.js"]
# Expected quality is fixed here before the implementation, not derived from
# positions() or from the new helper. E12b deliberately stays readable.
CASES = {
    "valid": (True, [], 2, 900),
    "empty": (True, [], 0, 0),
    "missing-ledger": (True, [], 0, 0),
    "container": (False, ["ALD_TRANSACOES_ILEGIVEIS"], 0, None),
    "nonobject": (False, ["ALD_TRANSACAO_ILEGIVEL"], 2, None),
    "impossible-date": (False, ["ALD_TRANSACAO_ILEGIVEL"], 2, None),
    "future": (False, ["READ_ONLY_FUTURE_SCHEMA"], 2, None),
    "duplicate-tx": (False, ["ALD_TRANSACTION_ID_DUPLICADO:buy"], 3, None),
    "duplicate-account": (False, ["ALD_ID_DUPLICADO:accounts:account"], 2, None),
    "reversal-inconsistent": (False, ["ALD_REVERSAL_INCONSISTENTE:reverse"], 3, None),
    "reversal-orphan": (False, ["ALD_REVERSAL_ORFAO:reverse"], 3, None),
    "cash-missing": (False, ["ALD_CASHACCOUNT_NAO_ENCONTRADA:buy"], 2, None),
    "account-missing": (False, ["ALD_ACCOUNT_NAO_ENCONTRADA:buy"], 2, 900),
    "instrument-missing": (False, ["ALD_INSTRUMENT_NAO_ENCONTRADO:buy"], 2, 900),
    "trade-currency": (False, ["ALD_MOEDA_DIVERGENTE:buy"], 2, None),
    "cash-only-currency": (True, [], 1, None),
    "reversal-valid": (True, [], 3, 1000),
}

PRELUDE = r"""
var S; window.__saves=0;
function save(){window.__saves++;return true;}
function dgLogChange(){throw new Error('read attempted a changelog write');}
function esc(v){const el=document.createElement('span');el.textContent=String(v);return el.innerHTML;}
function seed(kind){
  S={alladin:{schemaVersion:6,reportingCurrency:'BRL',assets:[],
    accounts:[{accountId:'account',name:'Synthetic account',recordStatus:'ACTIVE'}],
    cashAccounts:[{cashAccountId:'cash',accountId:'account',currency:'BRL',recordStatus:'ACTIVE'}],
    instruments:[{instrumentId:'instrument',name:'Synthetic instrument',symbol:'TEST',currency:'BRL'}],
    transactions:[
      {transactionId:'buy',eventType:'BUY',status:'POSTED',amount:100,currency:'BRL',
       effectiveAt:'2026-02-02',recordedAt:'2026-02-02T10:00:00.000Z',cashAccountId:'cash',
       instrumentId:'instrument',quantity:'1.5',fees:0,taxes:0,note:'<img src=x onerror=alert(1)>',unknown:{preserved:true}},
      {transactionId:'deposit',eventType:'DEPOSIT',status:'POSTED',amount:1000,currency:'BRL',
       flowScope:'EXTERNAL',effectiveAt:'2026-02-01',recordedAt:'2026-02-01T10:00:00.000Z',cashAccountId:'cash'}
    ]},dataGovernance:{changeLog:[]}};
  const a=S.alladin, buy=a.transactions[0];
  if(kind==='empty')a.transactions=[];
  if(kind==='missing-ledger')delete a.transactions;
  if(kind==='container')a.transactions={unexpected:'container'};
  if(kind==='nonobject')a.transactions.push(null);
  if(kind==='impossible-date')buy.effectiveAt='2026-02-30';
  if(kind==='future')a.schemaVersion=99;
  if(kind==='duplicate-tx')a.transactions.push({...buy});
  if(kind==='duplicate-account')a.accounts.push({...a.accounts[0]});
  if(kind.startsWith('reversal-')){
    const rev={...buy,transactionId:'reverse',eventType:'REVERSAL',reversedEventType:'BUY',
      reversalOf:'buy',recordedAt:'2026-02-03T10:00:00.000Z',effectiveAt:'2026-02-03'};
    buy.status='REVERSED';
    if(kind==='reversal-inconsistent')rev.amount=99;
    if(kind==='reversal-orphan'){rev.reversalOf='missing';buy.status='POSTED';}
    a.transactions.push(rev);
  }
  if(kind==='cash-missing')a.cashAccounts=[];
  if(kind==='account-missing')a.accounts=[];
  if(kind==='instrument-missing')a.instruments=[];
  if(kind==='trade-currency')buy.currency='USD';
  if(kind==='cash-only-currency'){a.transactions=[a.transactions[1]];a.transactions[0].currency='USD';}
  window.__saves=0;
}
"""

OBSERVE = r"""kind => {
  seed(kind);
  const before=JSON.stringify(S), L=JPWAlladin.leitura;
  const raw=L.transactions(), positions=L.posicoes(), balance=L.saldoDeCaixa('cash');
  const el=document.createElement('div');
  alladinRenderLedger(el);
  const html=el.innerHTML, dash=dmAlladinHTML();
  const present=typeof L.ledger==='function';
  let envelope=null, detached=null, noPositionDependency=null;
  if(present){
    const old=aldPosicoes;
    aldPosicoes=()=>{throw new Error('ledger must not derive positions');};
    JPWAlladin.leitura={...L,posicoes:aldPosicoes,transactions:()=>{throw new Error('UI must consume its quality envelope');}};
    try{envelope=L.ledger();alladinRenderLedger(document.createElement('div'));noPositionDependency=true;}
    finally{aldPosicoes=old;JPWAlladin.leitura=L;}
    const value=JSON.stringify(envelope);
    if(envelope.transactions.length){
      const tx=S.alladin.transactions.find(t=>t&&t.transactionId===envelope.transactions[0].transactionId);
      tx.amount+=1;detached=JSON.stringify(envelope)===value;tx.amount-=1;
    }else detached=true;
  }
  const frozen=v=>!v||typeof v!=='object'||(Object.isFrozen(v)&&Object.values(v).every(frozen));
  let preview=null;
  if(kind==='valid'||kind==='impossible-date'){
    preview={opened:false,notice:null};
    const open=alladinModalOpen;
    alladinModalOpen=html=>{preview.opened=true;preview.html=html;};
    window.showSessionNotice=message=>{preview.notice=message;};
    try{alladinTxReverseAbrir('buy');}finally{alladinModalOpen=open;}
  }
  return {characterization:{raw,positions,balance,html,dash},present,envelope,detached,preview,
    noPositionDependency,frozen:present&&frozen(envelope),rawFrozen:frozen(raw),
    unchanged:before===JSON.stringify(S),saveCalls:window.__saves,
    rowCount:el.querySelectorAll('tr:has(td)').length,unsafeImages:el.querySelectorAll('img').length};
}"""


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--baseline-results", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    result = {"root": str(root), "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_sha256": {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in SOURCES},
              "oracle": CASES, "checks": [], "observations": {}}
    baseline = json.loads(args.baseline_results.read_text()) if args.baseline_results else None
    if baseline:
        require(baseline["test_sha256"] == result["test_sha256"], "baseline and candidate must use the same test bytes")

    def check(name, fn):
        try:
            fn()
            result["checks"].append({"name": name, "status": "PASS"})
        except AssertionError as exc:
            result["checks"].append({"name": name, "status": "PRODUCT_FAIL", "error": str(exc)})

    with sync_playwright() as pw:
        launch = {"executable_path": os.environ["JP_WEALTH_CHROMIUM"]} if os.environ.get("JP_WEALTH_CHROMIUM") else {}
        browser = pw.chromium.launch(**launch)
        context = browser.new_context(service_workers="block")
        context.route("**/*", lambda route: route.abort("blockedbyclient"))
        page = context.new_page()
        page.goto("about:blank")
        page.add_script_tag(content=PRELUDE)
        for source in SOURCES:
            page.add_script_tag(content=(root/source).read_text())
        for name, (available, issues, raw_count, amount) in CASES.items():
            obs = page.evaluate(OBSERVE, name)
            result["observations"][name] = obs

            def characterization():
                c=obs["characterization"]
                require(obs["unchanged"] and obs["saveCalls"] == 0, "reads must preserve state and never save")
                require(len(c["raw"]) == raw_count and obs["rawFrozen"], "legacy raw-array contract changed")
                require(c["positions"]["available"] == available and c["positions"]["issues"] == issues, "quality oracle mismatch")
                require(c["balance"]["amount"] == amount, "cash amount changed")
                require(obs["rowCount"] == (raw_count if available else 0), "ledger UI must project all or none")
                require(obs["unsafeImages"] == 0, "ledger content was not escaped")
                if name == "valid":
                    require([t["transactionId"] for t in c["raw"]] == ["deposit", "buy"], "economic order changed")
                    require(c["positions"]["positions"] == [{"instrumentId":"instrument","accountId":"account","quantity":"1.5","consideradas":1}], "position changed")
                    require("unknown" not in c["raw"][1], "raw whitelist changed")
                if name == "cash-only-currency":
                    require(not c["balance"]["available"] and "Saldo indisponível" in c["dash"]["html"], "E12b unavailable cash must remain explicit")
                if baseline:
                    require(c == baseline["observations"][name]["characterization"], "baseline raw/position/cash/HTML characterization changed")
            check(name+":characterization", characterization)

            def envelope():
                require(obs["present"], "leitura.ledger() quality envelope is absent")
                e=obs["envelope"]
                require(set(e) == {"available","quality","issues","transactions"}, "unexpected envelope shape")
                require(e["available"] == available and e["quality"] == ("OK" if available else "BLOCKING") and e["issues"] == issues, "envelope quality changed")
                require(e["transactions"] == (obs["characterization"]["raw"] if available else []), "envelope must preserve the complete economic sequence or block")
                require(obs["frozen"] and obs["detached"] and obs["noPositionDependency"], "envelope must be independent, immutable and detached")
            check(name+":envelope", envelope)
            if name in ("valid", "impossible-date"):
                def preview():
                    require(obs["preview"]["opened"] == available, "preview must open only for available facts")
                    if available and baseline:
                        require(obs["preview"] == baseline["observations"][name]["preview"], "valid preview changed")
                    if not available:
                        require("indispon" in (obs["preview"]["notice"] or "").lower(), "unavailable preview needs an explicit notice")
                check(name+":preview", preview)
        browser.close()
    result["status"] = "PRODUCT_FAIL" if any(c["status"] != "PASS" for c in result["checks"]) else "PASS"
    args.artifact.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps({"status":result["status"],"checks":len(result["checks"]),
        "passed":sum(c["status"] == "PASS" for c in result["checks"]),"artifact":str(args.artifact)}))
    for check_result in result["checks"]:
        if check_result["status"] != "PASS":print(check_result["name"]+": "+check_result["error"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

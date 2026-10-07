#!/usr/bin/env python3
"""Host synthetic test of the exact MQL stop-risk core, not native MT5 proof."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Core.mqh"
EA = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Observer_Runtime.mqh"
TERMINAL = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh"
STORE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Store.mqh"

SHIM = r'''
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using string=std::string;
const long ACCOUNT_MARGIN_MODE_RETAIL_HEDGING=2;
const long ACCOUNT_MARGIN_MODE_RETAIL_NETTING=0;
bool MathIsValidNumber(double x) { return std::isfinite(x); }
bool JPWFinitePositive(double x) { return std::isfinite(x) && x>0.0; }
double MathMax(double a,double b) { return std::fmax(a,b); }
template<typename T> int ArraySize(const std::vector<T> &a) { return (int)a.size(); }
'''

MAIN = r'''
int checks=0,failures=0;
void check(bool yes,const string &name) {
  checks++; if(!yes) { failures++; std::cerr << "FAIL " << name << "\n"; }
}
int main() {
  JPWStopRiskSample s; JPWStopRiskClearSample(s);
  s.balance=10000; s.currency="USD"; s.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
  std::vector<JPWStopRiskRow> rows(4);
  for(auto &r:rows) JPWStopRiskClearRow(r);
  auto position=[&](int i,long ticket,const string &symbol,double risk,double extra) {
    auto &r=rows[i]; r.kind=JPW_STOP_RISK_POSITION; r.ticket=ticket;
    r.identifier=ticket+100; r.opened_msc=ticket*1000; r.symbol=symbol;
    r.side=1; r.order_type=-1; r.valid=1; r.volume=0.1;
    r.entry=0.6; r.sl=0.59; r.risk_money=risk;
    r.additional_valid=1; r.additional_money=extra;
  };
  position(0,1,"NZDUSD.m",100,4);
  position(1,2,"NZDUSD.m",0,5);
  auto &p=rows[2]; p.kind=JPW_STOP_RISK_PENDING; p.ticket=3;
  p.opened_msc=3000; p.symbol="NZDUSD.m"; p.side=1;
  p.order_type=2; p.valid=1; p.volume=0.03; p.entry=0.59;
  p.sl=0.58; p.risk_money=50; p.additional_reason="not applicable";
  position(3,4,"EURUSD.m",9000,9);
  s.row_count=4;
  double total,pct,open,pending,extra; string reason;
  check(JPWStopRiskAggregate(s,rows,"NZDUSD.m",1,total,pct,open,pending,extra,reason)
        && total==150 && pct==1.5 && open==100 && pending==50 && extra==9,
        "exact symbol and side, unrounded total over current balance");
  double money;
  check(JPWStopRiskLossFromProfit(-60,money) && money==60,
        "adverse OrderCalcProfit result");
  check(JPWStopRiskLossFromProfit(20,money) && money==0,
        "protected stop floors risk at zero");
  rows[2].valid=0; rows[2].sl=0; rows[2].risk_money=0;
  rows[2].reason="missing SL";
  check(!JPWStopRiskAggregate(s,rows,"NZDUSD.m",1,total,pct,open,pending,extra,reason),
        "missing pending SL refuses partial total");
  rows[2].sl=0.58; rows[2].risk_money=50; rows[2].valid=1; rows[2].reason="";
  rows[2].order_type=6; rows[2].valid=0; rows[2].reason="stop-limit unsupported";
  check(!JPWStopRiskAggregate(s,rows,"NZDUSD.m",1,total,pct,open,pending,extra,reason),
        "same-direction stop-limit remains blocking");
  rows[2].order_type=2; rows[2].valid=1; rows[2].reason="";
  rows[0].additional_valid=0; rows[0].additional_money=0;
  rows[0].additional_reason="stale quote";
  check(JPWStopRiskAggregate(s,rows,"NZDUSD.m",1,total,pct,open,pending,extra,reason)
        && total==150 && extra==-1,
        "market quote failure does not erase entry-to-SL total");
  s.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_NETTING;
  check(!JPWStopRiskAggregate(s,rows,"NZDUSD.m",1,total,pct,open,pending,extra,reason),
        "netting totals N/A");
  s.margin_mode=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
  s.currency="USC"; s.balance*=100;
  for(auto &r:rows) { r.risk_money*=100; r.additional_money*=100; }
  check(JPWStopRiskAggregate(s,rows,"NZDUSD.m",1,total,pct,open,pending,extra,reason)
        && total==15000 && pct==1.5,
        "USC numerator and balance remain same account unit");
  s.balance=0;
  check(!JPWStopRiskAggregate(s,rows,"NZDUSD.m",1,total,pct,open,pending,extra,reason),
        "non-positive balance N/A");
  std::cout << "HOST_STOP_RISK: " << checks-failures << " PASS / " << failures
            << " FAIL; native MT5 compilation/execution NOT_RUN\n";
  return failures?1:0;
}
'''


def main() -> int:
    compiler = shutil.which("clang++") or shutil.which("g++")
    if compiler is None:
        print("ENVIRONMENT_ERROR: no host C++ compiler; native MT5 NOT_RUN")
        return 2
    core = CORE.read_text(encoding="utf-8")
    core = re.sub(r"^#include[^\n]*$", "", core, flags=re.MULTILINE)
    core = core.replace("JPWStopRiskRow &rows[]", "std::vector<JPWStopRiskRow> &rows")
    ea = EA.read_text(encoding="utf-8")
    terminal = TERMINAL.read_text(encoding="utf-8")
    store = STORE.read_text(encoding="utf-8")
    assert "OrderCalcProfit(" not in terminal, "indicator-safe adapter calls EA-only API"
    assert "OrderCalcProfit(" in ea, "EA lacks native monetary calculation"
    assert "!JPWStopRiskPublish(first,rows,reason)" in ea
    assert "JPWStopRiskDeactivate" in ea
    assert "ORDER_VOLUME_CURRENT" in terminal and "POSITION_VOLUME" in terminal
    assert "ORDER_TYPE_BUY_STOP_LIMIT" in terminal and "ORDER_TYPE_SELL_STOP_LIMIT" in terminal
    assert "JPWStopRiskSchemaEmpty(db,empty_schema) && empty_schema" in store
    assert "JPWStopRiskLeaseMatches(sample.publisher_token" in store
    assert "GlobalVariableTemp(name)" in ea and "GlobalVariableSetOnCondition(name" in ea
    # GLOB treats '_' literally; LIKE would silently ignore sqliteXforeign.
    schema_count = "SELECT COUNT(*) FROM sqlite_master WHERE name NOT GLOB 'sqlite_*'"
    assert schema_count in store
    with tempfile.TemporaryDirectory(prefix="jpw-stop-risk-sqlite-") as tmp:
        path = Path(tmp) / "interrupted.sqlite"
        with sqlite3.connect(path) as db:
            assert db.execute(schema_count).fetchone() == (0,)
            db.execute("BEGIN")
            db.execute("CREATE TABLE interrupted_setup (id INTEGER)")
            db.rollback()
        with sqlite3.connect(path) as reopened:
            assert reopened.execute(schema_count).fetchone() == (0,), "rolled back empty DB must be retryable"
            reopened.execute("CREATE VIEW unrelated_view AS SELECT 1")
            assert reopened.execute(schema_count).fetchone() == (1,), "unknown schema must be refused"
            reopened.execute("CREATE VIEW sqliteXforeign AS SELECT 1")
            assert reopened.execute(schema_count).fetchone() == (2,), "sqliteXforeign is not an internal SQLite object"
    print("HOST_SQLITE_RECOVERY: rolled-back empty DB retryable; unknown view refused")
    print(f"CORE_SHA256: {hashlib.sha256(CORE.read_bytes()).hexdigest()}")
    print("HOST_SYNTHETIC: exact stop-risk core under C++ MQL shim")
    with tempfile.TemporaryDirectory(prefix="jpw-stop-risk-host-") as tmp:
        source = Path(tmp) / "stop_risk.cpp"
        binary = Path(tmp) / "stop_risk"
        source.write_text(SHIM + core + MAIN, encoding="utf-8")
        for cmd in ([compiler, "-std=c++17", "-Wall", "-Wextra", str(source), "-o", str(binary)],
                    [str(binary)]):
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)
            print(result.stdout, end="")
            print(result.stderr, end="")
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

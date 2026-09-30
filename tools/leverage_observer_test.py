#!/usr/bin/env python3
"""Compile the production MQL episode body with a tiny C++ MT5-free shim.

This verifies only the pure ordering/episode logic. It is not MetaEditor
compilation, native MT5 execution, SQLite validation or terminal observation.
"""

from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_Observer.mqh"


def slice_region(source: str, begin: str, end: str) -> str:
    left = source.index(begin)
    right = source.index(end, left)
    return source[left:right]


source = INCLUDE.read_text(encoding="utf-8")
deal_struct = slice_region(source, "struct JPWObserverDeal", "// A ordem dos campos")
snapshot_struct = slice_region(source, "struct JPWObserverSnapshot", "void JPWObserverClear")
episode_body = slice_region(
    source, "int JPWObserverCompareDeals", "bool JPWObserverSnapshotValid"
)
identity_body = slice_region(
    source, "bool JPWObserverSameExecution", "string JPWObserverDatabasePath"
)
episode_body = episode_body.replace(
    "JPWObserverDeal &deals[]", "std::vector<JPWObserverDeal> &deals"
)
assert episode_body.count("std::vector<JPWObserverDeal> &deals") == 2

cpp = r'''
#include <cmath>
#include <iostream>
#include <string>
#include <vector>
using std::string;
#define ArraySize(v) static_cast<int>((v).size())
#define DEAL_ENTRY_IN 0
#define DEAL_ENTRY_OUT 1
#define DEAL_ENTRY_INOUT 2
#define DEAL_ENTRY_OUT_BY 3
#define JPW_OBSERVER_MAX_DEALS 4096
bool JPWRaizNSymbolValid(const string &value) { return !value.empty(); }
bool JPWFinitePositive(double value) { return std::isfinite(value) && value > 0; }
''' + deal_struct + snapshot_struct + episode_body + identity_body + r'''
JPWObserverDeal deal(long ticket, int entry, int side, double volume, long time) {
  JPWObserverDeal d;
  d.ticket=ticket; d.order_ticket=(ticket==10 ? 555 : 1000+ticket);
  d.position_id=555; d.time_msc=time;
  d.entry=entry; d.side=side; d.symbol="SYNTH.EXACT";
  d.volume=volume; d.price=100.0;
  return d;
}
int main() {
  int pass=0;
  auto check=[&](bool ok,const char *name) {
    if (!ok) { std::cerr << "FAIL: " << name << "\n"; return; }
    ++pass;
  };
  std::vector<JPWObserverDeal> d={
    deal(12,DEAL_ENTRY_OUT,-1,0.4,120000),
    deal(10,DEAL_ENTRY_IN,1,1.0,100000),
    deal(14,DEAL_ENTRY_OUT,1,0.9,140000),
    deal(13,DEAL_ENTRY_INOUT,-1,2.0,130000),
    deal(11,DEAL_ENTRY_IN,1,0.5,110000)};
  JPWObserverDeal start; string reason;
  check(JPWObserverFindEpisode(d,11,start,reason) && start.ticket==10,
        "addition retains first deal");
  check(JPWObserverFindEpisode(d,12,start,reason) && start.ticket==10,
        "partial close retains first deal");
  check(JPWObserverFindEpisode(d,13,start,reason) && start.ticket==13,
        "reversal starts new episode");
  check(!JPWObserverFindEpisode(d,14,start,reason),
        "closed episode has no live start");
  std::vector<JPWObserverDeal> missing={deal(90,DEAL_ENTRY_OUT,-1,1,100000)};
  check(!JPWObserverFindEpisode(missing,90,start,reason),
        "missing opening fails closed");
  std::vector<JPWObserverDeal> tie={deal(100,DEAL_ENTRY_IN,1,.5,100000),
                                     deal(101,DEAL_ENTRY_IN,1,.5,100000)};
  check(!JPWObserverFindEpisode(tie,100,start,reason) &&
        reason=="Ordem de negocios no mesmo milissegundo ambigua",
        "same-ms first execution is ambiguous");
  check(!JPWObserverFindEpisode(tie,101,start,reason),
        "same-ms second execution is ambiguous");
  std::vector<JPWObserverDeal> bad={deal(110,DEAL_ENTRY_IN,1,1,100000)};
  bad[0].order_ticket=555;
  bad[0].price=0;
  check(!JPWObserverFindEpisode(bad,110,start,reason),
        "invalid executed price fails closed");
  std::vector<JPWObserverDeal> added={deal(150,DEAL_ENTRY_IN,1,.5,150000)};
  check(!JPWObserverFindEpisode(added,150,start,reason) &&
        reason=="Ordem original de abertura ausente do historico",
        "history starting with an addition is not an origin");
  added[0].order_ticket=555;
  check(JPWObserverFindEpisode(added,150,start,reason) && start.ticket==150,
        "opening order anchor permits first deal");
  check(JPWObserverInitialPositionMatches(start,555,"SYNTH.EXACT",1,150000),
        "live initial position time agrees with first deal");
  std::vector<JPWObserverDeal> truncated={deal(151,DEAL_ENTRY_IN,1,.5,151000)};
  truncated[0].order_ticket=555;
  check(JPWObserverFindEpisode(truncated,151,start,reason) &&
        !JPWObserverInitialPositionMatches(start,555,"SYNTH.EXACT",1,150000),
        "omitted earlier fill of same order fails live-time witness");
  check(!JPWObserverInitialPositionMatches(start,555,"SYNTH.EXACT",-1,151000),
        "live direction mismatch fails initial witness");
  JPWObserverSnapshot first{}, later{};
  first.episode_key="episode"; first.account_key="account";
  first.symbol="SYNTH.EXACT"; first.position_id=555;
  first.first_deal_ticket=10; first.deal_time_msc=100000;
  first.side=1; first.executed_p0=100;
  later=first; later.provenance=1; later.observer_recorded_utc=200001;
  check(JPWObserverSameExecution(first,later),
        "two observers may record one factual execution at different times");
  later.executed_p0=101;
  check(!JPWObserverSameExecution(first,later),
        "different executed price is never idempotent");
  std::cout << "leverage_observer_host_test: " << pass << "/15 PASS\n";
  return pass==15 ? 0 : 1;
}
'''

with tempfile.TemporaryDirectory(prefix="jpw-observer-host-") as temp:
    source_file = Path(temp) / "observer.cpp"
    binary = Path(temp) / "observer_test"
    source_file.write_text(cpp, encoding="utf-8")
    compiler = shutil.which("clang++") or shutil.which("g++")
    if compiler is None:
        raise SystemExit("NOT_RUN: no C++ compiler for host observer adapter")
    subprocess.run(
        [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", str(source_file), "-o", str(binary)],
        check=True,
    )
    subprocess.run([str(binary)], check=True)

#!/usr/bin/env python3
"""Compile actual PersonalHistory MQL bodies with a syntax-only host shim.

Each invocation uses a new OS process and an isolated real SQLite directory.
Host evidence cannot establish native MQL compilation, terminal races, actual
popup/sound delivery or UI behavior. Unexercised acceptance facets stay NOT_RUN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import tempfile
import time
from decimal import Decimal
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import jpw_personal_history_oracle as oracle

ROOT = Path(__file__).resolve().parents[1]
MQL = ROOT / "mt5/jpw-alavancagem-atual/MQL5"
CORE = MQL / "Include/JPWealth/JPW_PersonalHistory_Core.mqh"
STORE = MQL / "Include/JPWealth/JPW_PersonalHistory_Store.mqh"
EXPORT = MQL / "Include/JPWealth/JPW_PersonalHistory_Export.mqh"
SCRIPT = MQL / "Scripts/JPWealth/JPW_PersonalHistory_Tests.mq5"
STORE_RESULT = MQL / "Include/JPWealth/JPW_Alavancagem_Store_Result.mqh"
UI = MQL / "Include/JPWealth/JPW_PersonalHistory_UI.mqh"
PRESENTATION = MQL / "Include/JPWealth/JPW_Alavancagem_Presentation.mqh"
ACTIONS = MQL / "Include/JPWealth/JPW_Alavancagem_Actions.mqh"
TERMINAL = MQL / "Include/JPWealth/JPW_PersonalHistory_Terminal.mqh"
CONTROLLER = MQL / "Include/JPWealth/JPW_PersonalHistory_Controller.mqh"
MATH_CORE = MQL / "Include/JPWealth/JPW_Alavancagem_Core.mqh"
PROFILE = MQL / "Include/JPWealth/JPW_Alavancagem_Profile.mqh"
SUPPORT = ROOT / "tools/personal_history_host"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def translate(source: str) -> str:
    # Syntax adaptation only: domain control flow/arithmetic are unchanged.
    source = re.sub(r'^\s*#(?:include|property).*$', '', source, flags=re.M)
    source = re.sub(r'\b(\w+)\s+&(\w+)\[\]', r'std::vector<\1> &\2', source)
    def arrays(match: re.Match) -> str:
        kind, declarations = match.groups()
        return ' '.join((f'std::vector<{kind}> {name[:-2]};' if name.endswith('[]') else f'{kind} {name};') for name in declarations.split(','))
    source = re.sub(r'\b(\w+)\s+((?:\w+\[\],)*\w+\[\](?:,\w+)?)\s*;', arrays, source)
    source = re.sub(r'\b(\w+)\s+(\w+)\[\],', r'std::vector<\1> \2; \1 ', source)
    source = re.sub(r'\b(\w+)\s+(\w+)\[\]\s*;', r'std::vector<\1> \2;', source)
    source = source.replace('JPW_PERSONAL_FOLDER+', 'string(JPW_PERSONAL_FOLDER)+')
    source = re.sub(r'("(?:\\.|[^"\\])*")\s*\+', r'string(\1)+', source)
    return source


def extract_function(source: str, name: str) -> str:
    match = re.search(r'\b(?:void|bool|string|int)\s+' + re.escape(name) + r'\s*\(', source)
    if not match:
        raise ValueError(f"production function not found: {name}")
    opening = source.index('{', match.start())
    depth, position = 1, opening + 1
    while depth:
        depth += (source[position] == '{') - (source[position] == '}')
        position += 1
    return source[match.start():position]


def ui_source() -> str:
    ui, presentation, actions = UI.read_text(), PRESENTATION.read_text(), ACTIONS.read_text()
    globals_only = ui[ui.index('string g_personal_scope'):ui.index('void JPWPersonalRequestRead')]
    parts = [(SUPPORT / "ui_seams.cpp").read_text(), r"""
using ENUM_OBJECT_PROPERTY_INTEGER=int;
// Same forward declaration/default as indicator line202.
void JPWInvalidateDialogContent(const int route=-1);
bool g_details_content_dirty=false,g_details_inventory_complete=true;
string g_details_render_reason="";
bool host_design_write_ok=true;
bool JPWUIDesignSetInteger(const string& name,int prop,long value){return host_design_write_ok&&ObjectSetInteger(0,name,prop,value);}
"""]
    for helper in ["JPWInvalidateDialogContent", "JPWPresentationFailure", "JPWPresentationSetInteger"]:
        parts.append(translate(extract_function(presentation, helper)))
    parts.append(translate(globals_only))
    for name in ['JPWPersonalRequestRead', 'JPWPersonalRequestExport', 'JPWPersonalInvalidateContext', 'JPWPersonalResetPage', 'JPWPersonalScopeLabel', 'JPWPersonalPeakLabel']:
        parts.append(translate(extract_function(ui, name)))
    parts.append("#define JPWPersonalExport host_ui_export\n" + translate(extract_function(ui, "JPWPersonalCollectUI")) + "\n#undef JPWPersonalExport")
    for name in ['JPWPersonalSectionName', 'JPWPersonalRowCaption', 'JPWPersonalDetailLines', 'JPWPersonalRenderBody']:
        parts.append(translate(extract_function(presentation, name)))
    for name in ['JPWRaizSwitchTab', 'JPWPersonalHistoryMove', 'JPWPersonalHandleClick']:
        parts.append(translate(extract_function(actions, name)))
    ui_cases=(SUPPORT / "ui_cases.cpp").read_text()
    old_click='JPWPersonalRenderBody(0,0,300,170,200);REQUIRE(JPWPersonalHandleClick'
    refreshed=r"""
REQUIRE(g_personal_read_requested&&!g_personal_available&&g_personal_rows.empty(),"new query invalidates old rows while pending");
REQUIRE(!JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_ROW_FIRST)),"old row cannot open while query pending");
// Explicit synthetic completion of the requested page, same frozen eight rows.
g_personal_read_requested=false;g_personal_available=true;g_personal_rows.resize(8);
for(int i=0;i<8;i++){g_personal_rows[i].sequence=800-i;g_personal_rows[i].category="ALERT";g_personal_rows[i].wall=1000;g_personal_rows[i].payload="INTENT|";}
"""
    assert old_click in ui_cases
    ui_cases=ui_cases.replace(old_click,refreshed+old_click,1)
    ui_cases=ui_cases.replace('g_personal_available=false;g_personal_reason="synthetic corruption preserved";', 'g_personal_read_requested=false;g_personal_available=false;g_personal_reason="synthetic corruption preserved";')
    # Route change queues a detail read and clears rows; model that completion too.
    detail='g_personal_detail=g_personal_rows[0];'
    assert detail in ui_cases
    ui_cases=ui_cases.replace(detail,'g_personal_read_requested=false;g_personal_available=true;g_personal_detail.sequence=800;g_personal_detail.category="ALERT";g_personal_detail.wall=1000;g_personal_detail.payload="INTENT|";')
    extra=r"""
g_raiz_details_open=true;g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY;g_details_content_dirty=false;
JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_DETAIL);REQUIRE(!g_details_content_dirty,"new route invalidation does not dirty unrelated visible view");
JPWInvalidateDialogContent(JPW_ROUTE_PERSONAL_HISTORY);REQUIRE(g_details_content_dirty,"new route invalidation dirties visible view");
g_raiz_details_open=false;g_details_content_dirty=false;JPWInvalidateDialogContent(-1);REQUIRE(!g_details_content_dirty,"closed dialog stays clean");
host_design_write_ok=false;g_details_inventory_complete=true;g_details_render_reason="";
REQUIRE(!JPWPresentationSetInteger("fixture",OBJPROP_STATE,false)&&!g_details_inventory_complete&&!g_details_render_reason.empty(),"failed native property write invalidates frame explicitly");
host_design_write_ok=true;REQUIRE(JPWPresentationSetInteger("fixture",OBJPROP_STATE,false),"successful property delegation retained");
"""
    assert 'host_forbid_io=false;' in ui_cases
    parts.append(ui_cases.replace('host_forbid_io=false;',extra+'\nhost_forbid_io=false;'))
    return '\n'.join(parts)


def controller_source() -> str:
    controller, terminal = CONTROLLER.read_text(), TERMINAL.read_text()
    globals_only = controller[controller.index('JPWPersonalStoreContext g_ph_store'):controller.index('string JPWPersonalControllerMarker')]
    parts = [translate(globals_only), (SUPPORT / "controller_seams.cpp").read_text(), translate(extract_function(terminal, 'JPWPersonalTerminalNotify'))]
    for name in ['JPWPersonalControllerProblem', 'JPWPersonalControllerQueue', 'JPWPersonalControllerCompact', 'JPWPersonalControllerMergeRestored', 'JPWPersonalControllerEnsureStore', 'JPWPersonalControllerPersist', 'JPWPersonalControllerNotifyDue']:
        parts.append(translate(extract_function(controller, name)))
    parts.append((SUPPORT / "controller_cases.cpp").read_text())
    return '\n'.join(parts)



def extract_struct(source: str, name: str) -> str:
    match = re.search(r'\bstruct\s+' + re.escape(name) + r'\s*\{', source)
    if not match:
        raise ValueError(f"production struct not found: {name}")
    return source[match.start():source.index('};', match.start()) + 2]


def terminal_source(terminal: str | None = None) -> str:
    terminal = TERMINAL.read_text() if terminal is None else terminal
    math, profile = MATH_CORE.read_text(), PROFILE.read_text()
    parts = [translate(extract_struct(math, name)) for name in ['JPWAccount', 'JPWPosition', 'JPWInstrument', 'JPWQuote']]
    parts.append(translate(extract_struct(profile, 'JPWProfileEntry')))
    globals_only = terminal[terminal.index('struct JPWPersonalTerminalMeta'):terminal.index('string JPWPersonalTicketText')]
    parts.extend([translate(globals_only), translate(extract_function(math, 'JPWFinitePositive')), (SUPPORT / "terminal_seams.cpp").read_text()])
    for name in ['JPWPersonalTerminalTicket', 'JPWPersonalTerminalOptional', 'JPWPersonalTerminalRowMath', 'JPWPersonalTerminalDetails']:
        parts.append(translate(extract_function(terminal, name)))
    begin = terminal.index("g_ph_capture.leverage_valid=g_ph_math_valid;")
    end = terminal.index("g_ph_capture.details=", begin)
    parts.append(translate("void host_personal_acceptance_assignment(){" + terminal[begin:end] + "}"))
    parts.append((SUPPORT / "terminal_cases.cpp").read_text())
    return '\n'.join(parts)


def check_terminal_json(case_id: str, stdout: str) -> list[dict]:
    if case_id != 'HIS-AC14':
        return []
    payloads = {}
    for line in stdout.splitlines():
        if line.startswith('TERMINAL_JSON|'):
            _, label, raw = line.split('|', 2)
            if label in payloads:
                raise AssertionError('duplicate terminal JSON scenario')
            # Python normally permits NaN; reject it explicitly, and lowercase
            # native/host nan/inf spellings are rejected by grammar already.
            payloads[label] = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    if set(payloads) != {'quote-nan', 'quote-inf', 'spec-nan', 'spec-inf', 'profile-divisor-nan', 'profile-divisor-inf', 'gross-overflow'}:
        raise AssertionError('terminal JSON scenario set mismatch')
    checks = []
    for label, value in payloads.items():
        if label.startswith('quote-'):
            q = value['quotes'][0]
            if q['bid'] is not None or q['ask'] is not None or q['bid_valid'] or q['ask_valid']:
                raise AssertionError(f'{label}: invalid quotes must be unavailable, not zero')
        elif label.startswith('spec-'):
            spec = value['subjects'][0]['specification']
            if spec['contract_size'] is not None or spec['contract_size_valid']:
                raise AssertionError(f'{label}: nonfinite contract size must be unavailable')
        elif label.startswith('profile-divisor-'):
            if value['usc_profile'][0]['scale'] is not None or value['money_divisor'] is not None:
                raise AssertionError(f'{label}: unvalidated producer metadata must serialize null')
        else:
            if value['gross_account_units'] is not None or value['leverage_valid'] or value['quality'] != 0:
                raise AssertionError('overflow cannot serialize confirmed zero or financial peak')
        checks.append({'scenario': label, 'strict_json': 'PASS', 'unavailable_semantics': 'PASS'})
    return checks


def check_vectors(case_id: str, stdout: str) -> list[dict]:
    observed = {}
    for line in stdout.splitlines():
        if not line.startswith("FINANCIAL_VECTOR|"):
            continue
        _, observed_case, label, accepted, ratio, changed = line.split("|")
        if observed_case != case_id or label in observed:
            raise AssertionError("duplicate or mismatched financial vector")
        observed[label] = {"accepted": accepted == "1", "ratio": ratio, "changed": int(changed)}
    expected = oracle.financial_vectors(case_id)
    if set(observed) != {row["label"] for row in expected}:
        raise AssertionError(f"financial vector set mismatch: {case_id}")
    evidence = []
    for row in expected:
        actual = observed[row["label"]]
        wanted = row["ratio_exact"]
        if actual["accepted"] != (wanted is not None):
            raise AssertionError(f"eligibility mismatch: {case_id}/{row['label']}")
        if wanted is not None:
            # Comparing host binary float to an independent Decimal quotient.
            # No display rounding may determine peak replacement.
            tolerance = max(Decimal("1e-14"), abs(Decimal(wanted)) * Decimal("1e-14"))
            if abs(Decimal(actual["ratio"]) - Decimal(wanted)) > tolerance:
                raise AssertionError(f"ratio mismatch: {case_id}/{row['label']}")
        evidence.append({"input": row, "actual": actual, "status": "PASS"})
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", dest="case_id", help="One frozen HIS-AC01..20 case; default all")
    parser.add_argument("--output", type=Path, required=True, help="New evidence directory or .json receipt path")
    args = parser.parse_args()
    fixture = oracle.acceptance()
    ids = [row["id"] for row in fixture["cases"]]
    if args.case_id and args.case_id not in ids:
        parser.error("case must identify one of the frozen 20 cases")
    cases = [args.case_id] if args.case_id else ids
    receipt_path = args.output if args.output.suffix == ".json" else args.output / "receipt.json"
    if receipt_path.exists():
        parser.error("receipt already exists; use a new output to preserve earlier attempts")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix="host-", dir=receipt_path.parent))
    dependencies = [CORE, STORE, EXPORT, STORE_RESULT, SCRIPT, UI, PRESENTATION, ACTIONS, TERMINAL, CONTROLLER, MATH_CORE, PROFILE, SUPPORT / "compat.hpp", SUPPORT / "cases.cpp", SUPPORT / "store_cases.cpp", SUPPORT / "export_cases.cpp", SUPPORT / "ui_seams.cpp", SUPPORT / "ui_cases.cpp", SUPPORT / "controller_seams.cpp", SUPPORT / "controller_cases.cpp", SUPPORT / "terminal_seams.cpp", SUPPORT / "terminal_cases.cpp", Path(__file__), Path(oracle.__file__), oracle.ACCEPTANCE]
    sources = {str(path.relative_to(ROOT)): sha(path) for path in dependencies}
    cpp = attempt / "source.cpp"
    entry = '\nint main(int argc,char**argv){if(argc!=3&&argc!=4)return 2;host_root=argv[1];try{if(argc==4){if(string(argv[2])=="HIS-AC11")ownership_phase(argv[3]);else recovery_phase(argv[2],argv[3]);return 0;}core_case(argv[2]);store_case(argv[2]);export_case(argv[2]);ui_case(argv[2]);controller_case(argv[2]);terminal_case(argv[2]);return 0;}catch(const std::exception& e){std::cerr<<"PRODUCT_FAIL|"<<e.what()<<"\\n";return 1;}}\n'
    cpp.write_text((SUPPORT / "compat.hpp").read_text() + '\n' + translate(STORE_RESULT.read_text()) + '\n' + translate(CORE.read_text()) + '\n' + translate(STORE.read_text()) + '\n' + translate(EXPORT.read_text()) + '\n' + translate(SCRIPT.read_text()) + '\n' + (SUPPORT / "cases.cpp").read_text() + '\n' + (SUPPORT / "store_cases.cpp").read_text() + '\n' + (SUPPORT / "export_cases.cpp").read_text() + '\n' + ui_source() + '\n' + controller_source() + '\n' + terminal_source() + entry)
    binary = attempt / "test"
    command = ["clang++", "-std=c++17", "-Wall", "-Wextra", "-Wno-unused-parameter", "-Wno-deprecated-declarations", str(cpp), "-lsqlite3", "-o", str(binary)]
    if platform.system() != "Darwin":
        command.append("-lcrypto")
    build = subprocess.run(command, text=True, capture_output=True)
    (attempt / "compile.log").write_text(build.stdout + build.stderr)
    results = []
    overall = "PASS" if build.returncode == 0 else "TEST_HARNESS_FAIL"
    if build.returncode == 0:
        for case_id in cases:
            case_dir = attempt / case_id
            case_dir.mkdir()
            execution = subprocess.run([str(binary), str(case_dir), case_id], text=True, capture_output=True)
            (case_dir / "execution.log").write_text(execution.stdout + execution.stderr)
            def facet_status(prefix: str, previous_failed: bool) -> str:
                if f'{prefix}_CASE_PASS|' in execution.stdout:
                    return "PASS"
                if f'{prefix}_NOT_RUN|' in execution.stdout or previous_failed:
                    return "NOT_RUN"
                return "PRODUCT_FAIL" if execution.returncode else "TEST_HARNESS_FAIL"
            status = facet_status('CORE', False)
            sql_status = facet_status('SQLITE', status == 'PRODUCT_FAIL')
            export_status = facet_status('EXPORT', 'PRODUCT_FAIL' in {status, sql_status})
            ui_status = facet_status('UI', 'PRODUCT_FAIL' in {status, sql_status, export_status})
            controller_status = facet_status('CONTROLLER', 'PRODUCT_FAIL' in {status, sql_status, export_status, ui_status})
            terminal_status = facet_status('TERMINAL', 'PRODUCT_FAIL' in {status, sql_status, export_status, ui_status, controller_status})
            terminal_json = []
            if terminal_status == 'PASS':
                try:
                    terminal_json = check_terminal_json(case_id, execution.stdout)
                except (AssertionError, ValueError, KeyError) as error:
                    terminal_status = 'PRODUCT_FAIL'
                    overall = 'PRODUCT_FAIL'
                    (case_dir / 'terminal-json-failure.txt').write_text(str(error) + '\n')
            recovery_evidence = []
            recovery_status = "NOT_RUN"
            owner_status = "NOT_RUN"
            owner_evidence = []
            if case_id == "HIS-AC11" and not execution.returncode:
                owner_dir = case_dir / "cross-process-ownership"
                owner_dir.mkdir()
                holder_log = owner_dir / "hold.log"
                with holder_log.open('w') as output:
                    holder = subprocess.Popen([str(binary), str(owner_dir), case_id, 'hold'], text=True, stdout=output, stderr=subprocess.STDOUT)
                    for _ in range(250):
                        if (owner_dir / 'holder-ready').exists() or holder.poll() is not None:
                            break
                        time.sleep(.02)
                    ready = (owner_dir / 'holder-ready').exists()
                    if ready:
                        contender = subprocess.run([str(binary), str(owner_dir), case_id, 'contend'], text=True, capture_output=True)
                        contender_log = owner_dir / 'contend.log'
                        contender_log.write_text(contender.stdout + contender.stderr)
                        owner_evidence.append({"phase": "contend", "exit_code": contender.returncode, "evidence": str(contender_log)})
                    (owner_dir / 'holder-release').write_text('1')
                    holder.wait(timeout=10)
                owner_evidence.append({"phase": "hold/crash", "exit_code": holder.returncode, "evidence": str(holder_log)})
                if ready and contender.returncode == 0 and holder.returncode == 99:
                    takeover = subprocess.run([str(binary), str(owner_dir), case_id, 'takeover'], text=True, capture_output=True)
                    takeover_log = owner_dir / 'takeover.log'
                    takeover_log.write_text(takeover.stdout + takeover.stderr)
                    owner_evidence.append({"phase": "takeover", "exit_code": takeover.returncode, "evidence": str(takeover_log)})
                    owner_status = "PASS" if takeover.returncode == 0 else "PRODUCT_FAIL"
                else:
                    owner_status = "PRODUCT_FAIL"
                if owner_status == "PRODUCT_FAIL":
                    overall = "PRODUCT_FAIL"
            if case_id in {"HIS-AC16", "HIS-AC18"} and not execution.returncode:
                recovery_dir = case_dir / "cross-process-recovery"
                recovery_dir.mkdir()
                for phase in ['seed', 'crash', 'recover']:
                    recovered = subprocess.run([str(binary), str(recovery_dir), case_id, phase], text=True, capture_output=True)
                    log = recovery_dir / f'{phase}.log'
                    log.write_text(recovered.stdout + recovered.stderr)
                    recovery_evidence.append({"phase": phase, "exit_code": recovered.returncode, "evidence": str(log)})
                    if recovered.returncode != (99 if phase == 'crash' else 0):
                        recovery_status = "PRODUCT_FAIL"
                        overall = "PRODUCT_FAIL"
                        break
                else:
                    recovery_status = "PASS"
                if case_id == "HIS-AC18" and recovery_status == "PASS":
                    called_dir = case_dir / "cross-process-called-recovery"
                    called_dir.mkdir()
                    for phase in ['seed', 'crash-called', 'recover-called']:
                        recovered = subprocess.run([str(binary), str(called_dir), case_id, phase], text=True, capture_output=True)
                        log = called_dir / f'{phase}.log'
                        log.write_text(recovered.stdout + recovered.stderr)
                        recovery_evidence.append({"phase": phase, "exit_code": recovered.returncode, "evidence": str(log)})
                        if recovered.returncode != (99 if phase == 'crash-called' else 0):
                            recovery_status = "PRODUCT_FAIL"
                            overall = "PRODUCT_FAIL"
                            break
            vectors = []
            if status == "PASS":
                try:
                    vectors = check_vectors(case_id, execution.stdout)
                except AssertionError as error:
                    status = "PRODUCT_FAIL"
                    (case_dir / "oracle-failure.txt").write_text(str(error) + '\n')
            if "PRODUCT_FAIL" in {status, sql_status, export_status, ui_status, controller_status, terminal_status}:
                overall = "PRODUCT_FAIL"
            elif "TEST_HARNESS_FAIL" in {status, sql_status, export_status, ui_status, controller_status, terminal_status}:
                overall = "TEST_HARNESS_FAIL"
            results.append({"id": case_id, "host_core": status, "host_sqlite": sql_status, "host_export_restore": export_status,
                            "host_ui_helpers": ui_status,
                            "host_controller_helpers": controller_status, "host_terminal_serializer": terminal_status, "terminal_json": terminal_json, "cross_process_crash_recovery": recovery_status,
                            "recovery_evidence": recovery_evidence,
                            "cross_process_ownership": owner_status, "ownership_evidence": owner_evidence,
                            "full_acceptance": "PRODUCT_FAIL" if 'PRODUCT_FAIL' in {status, sql_status, export_status, ui_status, controller_status, terminal_status, recovery_status, owner_status} else "NOT_RUN", "executed_scope": "Named production Core/Store/Export/UI/Controller/Terminal serializer functions and instrumented primitive seams; see facet statuses and logs",
                            "assertion_count": int(re.search(r'CORE_CASE_PASS\|[^|]+\|(\d+)', execution.stdout).group(1)) if status == "PASS" else None,
                            "sqlite_assertion_count": int(re.search(r'SQLITE_CASE_PASS\|[^|]+\|(\d+)', execution.stdout).group(1)) if sql_status == "PASS" else None,
                            "export_assertion_count": int(re.search(r'EXPORT_CASE_PASS\|[^|]+\|(\d+)', execution.stdout).group(1)) if export_status == "PASS" else None,
                            "ui_assertion_count": int(re.search(r'UI_CASE_PASS\|[^|]+\|(\d+)', execution.stdout).group(1)) if ui_status == "PASS" else None,
                            "controller_assertion_count": int(re.search(r'CONTROLLER_CASE_PASS\|[^|]+\|(\d+)', execution.stdout).group(1)) if controller_status == "PASS" else None,
                            "terminal_assertion_count": int(re.search(r'TERMINAL_CASE_PASS\|[^|]+\|(\d+)', execution.stdout).group(1)) if terminal_status == "PASS" else None,
                            "financial_oracle": vectors, "execution_exit_code": execution.returncode,
                            "evidence": str(case_dir / "execution.log")})
    after = {str(path.relative_to(ROOT)): sha(path) for path in dependencies}
    if after != sources:
        overall = "ENVIRONMENT_ERROR"
    receipt = {"schema": "jpw-personal-history-host/v1", "classification": overall, "acceptance_sha256": oracle.ACCEPTANCE_SHA,
               "source_sha256": sources, "sources_unchanged_during_execution": after == sources,
               "compile_command": command, "compile_exit_code": build.returncode, "compile_log": str(attempt / "compile.log"),
               "cases": results, "native_mql_compile": "NOT_RUN", "native_ex5": "NOT_RUN", "native_mt5_alert_sound": "NOT_RUN",
               "native_terminal_races": "NOT_RUN", "native_ui_events": "NOT_RUN", "real_accounts_or_trades": "NOT_RUN",
               "limits": "Host status applies only to named executed subcriteria. No whole-case acceptance is inferred from host or static wiring."}
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({"classification": overall, "receipt": str(receipt_path), "cases": [{"id": row["id"], "host_core": row["host_core"], "host_sqlite": row["host_sqlite"], "host_export_restore": row["host_export_restore"], "host_ui_helpers": row["host_ui_helpers"], "host_controller_helpers": row["host_controller_helpers"], "host_terminal_serializer": row["host_terminal_serializer"], "cross_process_crash_recovery": row["cross_process_crash_recovery"], "cross_process_ownership": row["cross_process_ownership"]} for row in results]}))
    if build.returncode:
        print(build.stderr)
    return 1 if overall in {"PRODUCT_FAIL", "TEST_HARNESS_FAIL", "ENVIRONMENT_ERROR"} else 0


if __name__ == "__main__":
    raise SystemExit(main())

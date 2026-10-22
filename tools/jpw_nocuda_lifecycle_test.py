#!/usr/bin/env python3
"""Execute NoCuda admission/cleanup callbacks and real ownership code on host.

The MQL lifecycle, controller, focus broker and object cleaners are production
source. MT5 chart APIs are deterministic seams; controller persistence uses real
host SQLite. Existing manual-study loading/rendering and unrelated presentation
seams remain outside this ownership test. This is not a MetaEditor/native test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from leverage_host_shim import source_root
import jpw_nocuda_fibo_controller_test as controller_test

ROOT = source_root()
INC = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"
INDICATOR = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5"


def function(source: str, name: str) -> str:
    match = re.search(r"\b(?:bool|void|int|double|string|datetime)\s+" + re.escape(name) + r"\s*\(", source)
    if not match:
        raise ValueError(f"missing production function {name}")
    opening = source.index("{", match.end())
    depth = 0
    for offset in range(opening, len(source)):
        if source[offset] == "{":
            depth += 1
        elif source[offset] == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():offset + 1]
    raise ValueError(f"unclosed production function {name}")


OWNERSHIP_SEAMS = r'''
#define INIT_SUCCEEDED 0
#define INIT_FAILED 1
#define INIT_PARAMETERS_INCORRECT 2
#define REASON_REMOVE 1
#define REASON_INITFAILED 8
#define PERIOD_CURRENT 0
#define INDICATOR_SHORTNAME 1
#define CHART_WIDTH_IN_PIXELS 20
#define CHART_HEIGHT_IN_PIXELS 21
#define CHARTEVENT_CLICK 20
#define JPW_NOCUDA_SHORTNAME string("JPW STOIKUS · NoCuda Channels")
#define JPW_NOCUDA_CHART_STATE "JPW_NOCUDA_VIEW_V1"
bool timer_available=true,timer_active=false;
int indicator_copies=1,chart_event_writes=0,custom_events=0;
string InpPipSymbol=""; double InpPipSize=0;
int g_nocuda_tab=0,g_nocuda_page=0,g_nocuda_measure_page=0,g_nocuda_ui_pages=1;
long g_nocuda_last_bar=0,g_nocuda_last_width=0,g_nocuda_last_height=0;
bool g_nocuda_show_refs=false;
struct Daily{bool valid=false,no_session=false;} g_nocuda_daily;
string g_nocuda_last_distance,g_nocuda_last_quote,g_nocuda_ui_focus;
string g_nocuda_ui_render_prefix,g_nocuda_ui_preparation_reason;
std::vector<string> g_nocuda_ui_kept,g_nocuda_ui_previous;
bool g_nocuda_ui_inventory_complete=true,g_nocuda_ui_deferred_prune=false;
string g_fc_render_prefix;
std::vector<string>g_fc_keep,g_fc_previous,g_fc_actions,g_fc_action_ids;
bool g_fc_inventory_complete=true,g_fc_force_clear=false,g_fc_deferred_prune=false;
void JPWNoCudaUIFail(){g_nocuda_ui_inventory_complete=false;}
void JPWNoCudaFiboUIFail(){g_fc_inventory_complete=false;}
void JPWUIDesignDeleteIcon(const string&n){ObjectDelete(0,n);}
bool JPWUIDesignDelete(const string&n){return ObjectDelete(0,n);}
template<class T>void ArrayCopy(std::vector<T>&a,const std::vector<T>&b){a=b;}
bool EventChartCustom(long,int,long,double,const string&){custom_events++;return true;}
long ChartID(){return 123456;}
bool IndicatorSetString(int,const string&){return true;}
int ChartIndicatorsTotal(long,int){return indicator_copies;}
string ChartIndicatorName(long,int,int){return JPW_NOCUDA_SHORTNAME;}
bool EventSetTimer(int){timer_active=timer_available;return timer_active;}
void EventKillTimer(){timer_active=false;}
bool ChartRedraw(long){return true;}
long ChartGetInteger(long,int p){return p==CHART_MOUSE_SCROLL?host_nocuda_scroll:(p==CHART_WIDTH_IN_PIXELS?1440:900);}
long iTime(const string&,int,int){return 0;}
bool JPWNoCudaRevalidateDaily(){return false;}
void JPWNoCudaMeasurements(string&,string&){}
bool JPWNoCudaUILauncherReservationChanged(){return false;}
void JPWNoCudaFlushChartClick(){}
void JPWNoCudaChartClick(int,int){}
void JPWNoCudaObjectClick(int,int){}
void JPWNoCudaChartInteraction(int,int){}
void JPWNoCudaDragAnchor(const string&){}
void JPWUIDesignForget(const string&){}
string JPWNoCudaUIFocusCycle(const string&,const string&,bool){return "";}
void JPWNoCudaNewDraft(){}
void JPWNoCudaEditDraft(){}
void JPWNoCudaCancelDraft(){}
bool JPWNoCudaConfirmDraft(){return false;}
int JPWNoCudaNextTf(int tf){return tf;}
void JPWNoCudaSaveChartState(){}
bool JPWNoCudaSelectLevelText(const string&){return false;}
void JPWNoCudaConsultDay(){}
bool JPWNoCudaLoadStudy(int,int=0){return false;}
'''

CASES = r'''
int checks=0,failures=0;
void check(bool ok,const string&message){checks++;if(!ok){failures++;Print("FAIL: ",message);}}
void seed(const string&name,const string&text="fixture"){
 ObjectCreate(0,name,OBJ_LABEL,0,0,0);ObjectSetString(0,name,OBJPROP_TOOLTIP,text);
}
void fresh(){
 objects.clear();g_nocuda_prefix="";g_nocuda_symbol="";g_nocuda_feed="";
 g_nocuda_canvas_ready=false;g_nocuda_panel_open=false;g_nocuda_panel_focus=false;
 g_nocuda_ui_inventory_complete=true;g_nocuda_ui_previous.clear();g_nocuda_ui_kept.clear();
 g_nocuda_ui_deferred_prune=false;g_fc_inventory_complete=true;g_fc_force_clear=false;
 g_fc_previous.clear();g_fc_keep.clear();g_fc_deferred_prune=false;g_fc_editing="";
 g_ncf_mode=true;g_ncf_ui.open=false;g_ncf_clone="";g_ncf_restore_source="";
 g_ncf_restore_requested=false;g_ncf_key="";g_ncf_has=false;g_ncf_link=false;
 timer_available=true;timer_active=false;indicator_copies=1;InpMaxQuoteAgeSeconds=30;
 InpSourceTimeframe=PERIOD_H1;InpPipSymbol="";InpPipSize=0;
 chart_event_writes=0;custom_events=0;manual_paints=0;manual_ui_draws=0;
 // HOST_LIFECYCLE_RESET
 seed("UI_USER_NOTE","manual ui");seed("FC_USER_BUTTON","manual fc");
 seed("DRAW_USER_MARK","manual drawing");seed("DRAW_LABEL_REF_USER","manual reference");
 seed("JPW_NOCUDA_VIEW_V1","saved chart preference");
 seed("JPW_NOCUDA_FIBO_VISUAL_V1","saved visual preference");
 seed("JPW_NOCUDA_FIBO_STUDY_V1","saved study preference");
 seed("OTHER_UI_SAFE","another namespace");
 JPWUIAcquire("OTHER_MODULE_");custom_events=0;
}
void preserved(const string&context){
 check(ObjectGetString(0,"UI_USER_NOTE",OBJPROP_TOOLTIP)=="manual ui",context+": generic UI preserved");
 check(ObjectGetString(0,"FC_USER_BUTTON",OBJPROP_TOOLTIP)=="manual fc",context+": generic FC preserved");
 check(ObjectGetString(0,"DRAW_USER_MARK",OBJPROP_TOOLTIP)=="manual drawing",context+": generic drawing preserved");
 check(ObjectGetString(0,"DRAW_LABEL_REF_USER",OBJPROP_TOOLTIP)=="manual reference",context+": generic reference preserved");
 check(ObjectGetString(0,"JPW_NOCUDA_VIEW_V1",OBJPROP_TOOLTIP)=="saved chart preference",context+": chart preference preserved");
 check(ObjectGetString(0,"JPW_NOCUDA_FIBO_VISUAL_V1",OBJPROP_TOOLTIP)=="saved visual preference",context+": visual preference preserved");
 check(ObjectGetString(0,"JPW_NOCUDA_FIBO_STUDY_V1",OBJPROP_TOOLTIP)=="saved study preference",context+": study preference preserved");
 check(ObjectFind(0,"OTHER_UI_SAFE")>=0&&JPWUIOwner()=="OTHER_MODULE_",context+": foreign namespace/focus preserved");
}
void refused_callbacks(const string&context){
 const int before=chart_event_writes;
 OnTimer(); // Must not reset context and subscribe this rejected instance.
 OnChartEvent(CHARTEVENT_OBJECT_CLICK,0,0,g_nocuda_prefix+"FC_FC_OPEN");
 OnChartEvent(CHARTEVENT_OBJECT_CLICK,0,0,g_nocuda_prefix+"UI_OPEN");
 OnChartEvent(CHARTEVENT_CHART_CHANGE,0,0,"");
 OnChartEvent(CHARTEVENT_MOUSE_MOVE,0,0,"1");
 check(!g_ncf_ui.open&&!g_nocuda_panel_open&&JPWUIOwner()=="OTHER_MODULE_",context+": rejected callbacks cannot acquire a panel");
 check(chart_event_writes==before&&custom_events==0,context+": rejected callbacks cannot subscribe chart events or emit focus changes");
 check(manual_paints==0&&manual_ui_draws==0,context+": rejected callbacks cannot render");
}
void acquired_objects(const string&p){
 seed(p+"UI_BUTTON");seed(p+"FC_BUTTON");seed(p+"DRAW_ANCHOR_A");seed(p+"DRAW_LABEL_REF_00h");
 seed(p+"CLONE");seed(p+"CANVAS");g_nocuda_canvas_ready=true;
 g_ncf_clone=p+"CLONE";JPWUIAcquire(p);custom_events=0;
}
void removed_own(const string&p,const string&context){
 for(const string suffix:{"UI_BUTTON","FC_BUTTON","DRAW_ANCHOR_A","DRAW_LABEL_REF_00h","CLONE","CANVAS"})
  check(ObjectFind(0,p+suffix)<0,context+": own "+suffix+" removed");
 check(!timer_active&&!JPWUIOwns(p),context+": own timer and focus released");
}
int main(int argc,char**argv){
 if(argc!=2)return 2;root_path=argv[1];
 // Missing admission guard would delete foreign objects after invalid-input or duplicate failure.
 for(int failure:{0,1})for(int reason:{REASON_INITFAILED,REASON_REMOVE})for(bool callbacks:{false,true}){
  fresh();if(failure==0)InpMaxQuoteAgeSeconds=0;else indicator_copies=2;
  const string label=(failure==0?"invalid input":"duplicate")+string(reason==REASON_REMOVE?" / remove":" / initfailed");
  check(OnInit()==(failure==0?INIT_PARAMETERS_INCORRECT:INIT_FAILED),label+": init refused");
  if(callbacks)refused_callbacks(label);OnDeinit(reason);preserved(label);
 }
 // Missing empty-prefix guards would broaden destructive helpers to generic namespaces.
 fresh();JPWNoCudaFiboUIClear("");JPWNoCudaUIClear("");JPWNoCudaRemoveDrawingObjects("");
 JPWNoCudaRemoveDailyReferences("");
 g_nocuda_ui_previous={"obsolete"};g_fc_previous={"obsolete"};
 JPWNoCudaUIFinish("");JPWNoCudaFiboUIFinish("");preserved("empty helper prefix");
 // Reversed namespace checks would remove another admitted instance.
 fresh();check(OnInit()==INIT_SUCCEEDED,"normal: initialized");const string first=g_nocuda_prefix;
 OnChartEvent(CHARTEVENT_OBJECT_CLICK,0,0,first+"FC_FC_OPEN");
 check(g_ncf_ui.open&&JPWUIOwns(first),"normal: admitted callback acquires its panel");
 acquired_objects(first);const string second="JPWNC_123456_999999_";
 for(const string suffix:{"UI_BUTTON","FC_BUTTON","DRAW_ANCHOR_A","DRAW_LABEL_REF_00h","CLONE","CANVAS"})seed(second+suffix);
 JPWUIAcquire("OTHER_MODULE_");custom_events=0;OnDeinit(REASON_INITFAILED);
 removed_own(first,"normal cleanup");preserved("normal cleanup");
 for(const string suffix:{"UI_BUTTON","FC_BUTTON","DRAW_ANCHOR_A","DRAW_LABEL_REF_00h","CLONE","CANVAS"})
  check(ObjectFind(0,second+suffix)>=0,"second namespace survives "+suffix);
 OnDeinit(REASON_REMOVE);preserved("repeat deinit");
 // Missing resource-admission state would skip cleanup after post-acquisition timer failure.
 fresh();timer_available=false;check(OnInit()==INIT_FAILED,"timer failure: init refused after namespace admission");
 const string failed=g_nocuda_prefix;check(!failed.empty(),"timer failure: namespace had been acquired");
 acquired_objects(failed);JPWUIAcquire("OTHER_MODULE_");custom_events=0;
 const int subscribed=chart_event_writes;refused_callbacks("timer failure");
 check(chart_event_writes==subscribed,"timer failure: callbacks cannot add subscriptions");
 OnDeinit(REASON_INITFAILED);removed_own(failed,"timer failure cleanup");preserved("timer failure cleanup");
 // Explicit removal keeps the existing admitted-instance chart-preference deletion contract.
 fresh();check(OnInit()==INIT_SUCCEEDED,"remove: initialized");const string removed=g_nocuda_prefix;
 acquired_objects(removed);OnDeinit(REASON_REMOVE);removed_own(removed,"explicit remove");
 check(ObjectFind(0,"JPW_NOCUDA_VIEW_V1")<0,"explicit remove: admitted chart preference removed");
 check(ObjectGetString(0,"JPW_NOCUDA_FIBO_VISUAL_V1",OBJPROP_TOOLTIP)=="saved visual preference"&&
       ObjectGetString(0,"JPW_NOCUDA_FIBO_STUDY_V1",OBJPROP_TOOLTIP)=="saved study preference","explicit remove: shared Fibo preferences survive");
 check(databases.empty()&&statements.empty(),"no database handles retained");
 Print("NoCuda lifecycle: ",checks," checks; failures=",failures,"; native NOT_RUN");return failures?1:0;
}
'''


def build() -> tuple[str, list[Path], list[dict[str, str]]]:
    ct, db, term = controller_test.ct, controller_test.db, controller_test.term
    shim = ct.SHIM.replace("string StringFormat(const char* fmt,double value)", "template<class T> string StringFormat(const char* fmt,T value)")
    termshim = term.SHIM.replace("void ResetLastError(){error=0;}int GetLastError(){return error;}", "").replace("int error=0,period=60,copy_count=0,mode=0;", "int period=60,copy_count=0,mode=0;string synthetic_feed=\"TEST_ONLY\";bool flip_feed_during_time=false,flip_feed_during_rates=false;").replace("error=1", "last_error=1")
    termshim = termshim.replace("OBJPROP_LEVELWIDTH};", "OBJPROP_LEVELWIDTH,OBJPROP_XDISTANCE,OBJPROP_YDISTANCE,OBJPROP_SELECTED};").replace("OBJPROP_LEVELTEXT};", "OBJPROP_LEVELTEXT,OBJPROP_TOOLTIP,OBJPROP_TEXT};")
    termshim = termshim.replace("long t1,double p1,long t2,double p2", "long t1=0,double p1=0,long t2=0,double p2=0")
    termshim = termshim.replace("if(i.second.ints[{OBJPROP_TYPE,0}]==type)", "if(type==-1||i.second.ints[{OBJPROP_TYPE,0}]==type)")
    termshim = termshim.replace("if(i.second.ints[{OBJPROP_TYPE,0}]==type&&index--==0)", "if((type==-1||i.second.ints[{OBJPROP_TYPE,0}]==type)&&index--==0)")
    core, store = db.transform(ct.CORE.read_text()), db.transform(db.STORE.read_text())
    terminal = (INC / "JPW_NoCuda_Fibo_Terminal.mqh").read_text()
    terminal = re.sub(r"^#include.*\n", "", terminal, flags=re.M).replace("string &names[]", "std::vector<string> &names").replace("datetime times[];", "std::vector<datetime> times;").replace("datetime verify[];", "std::vector<datetime> verify;")
    ui = (INC / "JPW_NoCuda_Fibo_UI.mqh").read_text()
    types = ui[ui.index("struct JPWNoCudaFiboUIItem"):ui.index("JPWNoCudaFiboUIPrefs g_fc_pref")]
    types = re.sub(r"JPWNoCudaFiboUIItem (\w+)\[\];", r"std::vector<JPWNoCudaFiboUIItem> \1;", types)
    uiseams = controller_test.UISEAMS
    uiseams = uiseams.replace("#define JPW_UI_OWNER_EVENT 17\n", "")
    for name in ("JPWNoCudaUIClear", "JPWUIAcquire", "JPWUIOwns", "JPWUIOwner", "JPWUIRelease", "JPWNoCudaFiboUIClear"):
        uiseams = uiseams.replace(function(uiseams, name), "")
    uiseams = uiseams.replace("bool ChartSetInteger(long,int p,long value){if(p==CHART_MOUSE_SCROLL)host_nocuda_scroll=value;return true;}", "bool ChartSetInteger(long,int p,long value){chart_event_writes++;if(p==CHART_MOUSE_SCROLL)host_nocuda_scroll=value;return true;}")
    uiseams = uiseams.replace("struct FakeCanvas{void Destroy(){}}g_nocuda_canvas;", "struct FakeCanvas{void Destroy(){ObjectDelete(0,g_nocuda_prefix+\"CANVAS\");}}g_nocuda_canvas;")
    # Counter is an MT5 ChartSetInteger API seam, declared before UISEAMS.
    ownership_seams = OWNERSHIP_SEAMS.replace("int indicator_copies=1,chart_event_writes=0,custom_events=0;", "int indicator_copies=1,custom_events=0;")
    context_seams = controller_test.CONTEXTSEAMS
    context_seams = context_seams.replace(function(context_seams, "JPWNoCudaRemoveDrawingObjects"), "")
    manual_ui = (INC / "JPW_NoCuda_UI.mqh").read_text()
    render = (INC / "JPW_NoCuda_Render.mqh").read_text()
    bodies: list[tuple[Path, str, str]] = []
    for path, source, names in (
        (INC / "JPW_NoCuda_Render.mqh", render, ("JPWNoCudaRemoveDailyReferences", "JPWNoCudaRemoveDrawingObjects")),
        (INC / "JPW_NoCuda_UI.mqh", manual_ui, ("JPWNoCudaUIClear", "JPWNoCudaUIFinish")),
        (INC / "JPW_NoCuda_Fibo_UI.mqh", ui, ("JPWNoCudaFiboUIFinish", "JPWNoCudaFiboUIClear", "JPWNoCudaFiboUIEndInteraction")),
    ):
        bodies += [(path, name, function(source, name)) for name in names]
    focus_path = INC / "JPW_UI_Focus.mqh"
    focus = re.sub(r"^#include.*\n", "", focus_path.read_text(), flags=re.M)
    legacy_path = INC / "JPW_NoCuda_Store.mqh"
    legacy = legacy_path.read_text()
    legacy_defs = db.transform(legacy[legacy.index("struct JPWNoCudaRecord"):legacy.index("bool JPWNoCudaStoreNewStudyId")])
    legacy_defs = re.sub(r"uchar (\w+)\[\];", r"std::vector<uchar> \1;", legacy_defs)
    mainsource = INDICATOR.read_text()
    # New lifecycle state is loaded from production, never replaced by test state.
    lifecycle_state = "\n".join(re.findall(r"^bool g_nocuda_(?:resources_admitted|initialized)=false;", mainsource, re.M))
    state_reset = re.sub(r"\bbool ", "", lifecycle_state)
    main_bodies = [(INDICATOR, name, function(mainsource, name)) for name in ("JPWNoCudaClearAnchors", "JPWNoCudaResetContext", "JPWNoCudaAction", "JPWNoCudaOpenFromPanel", "OnInit", "OnDeinit", "OnTimer", "OnChartEvent")]
    controller = controller_test.transform((INC / "JPW_NoCuda_Fibo_Controller.mqh").read_text())
    sync = (INC / "JPW_NoCuda_Fibo_Sync.mqh").read_text()
    bridge_path = INC / "JPW_Stoikus_PanelBridge.mqh"
    bridge = bridge_path.read_text()
    shared_access = re.search(r"^bool g_nocuda_ui_shared_access=false;", manual_ui, re.M)[0]
    forward = "void JPWNoCudaUIClear(const string);void JPWNoCudaFiboUIClear(const string);"
    # Manual resource and UI globals must exist before the production controller.
    code = shim + db.DBSHIM + termshim + core + store + db.DBREAD + terminal + types + "\nint chart_event_writes=0;\n" + uiseams + legacy_defs + context_seams + ownership_seams + lifecycle_state + forward
    from stoikus_window_nocuda_host import fibo_cancel,FIBO_WINDOW_BOUNDARY,manual_window
    code += fibo_cancel()+FIBO_WINDOW_BOUNDARY+manual_window(code,native_scroll=False)
    code += "\n" + "\n".join(body for _, _, body in bodies) + "\n" + focus + sync + controller
    # MathFloor is an MQL API seam; bridge/open behavior is production code.
    code += "\ndouble MathFloor(double v){return std::floor(v); }\n" + shared_access + "\n" + bridge
    code += "\n" + "\n".join(body for _, _, body in main_bodies) + CASES.replace("// HOST_LIFECYCLE_RESET", state_reset)
    files = [bridge_path, ct.CORE, db.STORE, INC / "JPW_NoCuda_Fibo_Terminal.mqh", INC / "JPW_NoCuda_Fibo_Sync.mqh", INC / "JPW_NoCuda_Fibo_Controller.mqh", INDICATOR, legacy_path, INC / "JPW_NoCuda_Render.mqh", INC / "JPW_NoCuda_UI.mqh", INC / "JPW_NoCuda_Fibo_UI.mqh", focus_path, INC / "JPW_Stoikus_Window.mqh", ROOT / "tools/stoikus_window_nocuda_host.py", Path(__file__), Path(controller_test.__file__), Path(db.__file__), Path(term.__file__)]
    extracted = [{"file": str(path.relative_to(ROOT)), "function": name, "body_sha256": hashlib.sha256(body.encode()).hexdigest()} for path, name, body in bodies + main_bodies]
    return code, files, extracted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--label", default="run")
    args = parser.parse_args()
    compiler = shutil.which("clang++") or shutil.which("g++")
    if not compiler:
        print("ENVIRONMENT_ERROR: C++ compiler unavailable")
        return 1
    code, files, extracted = build()
    with tempfile.TemporaryDirectory(prefix="jpw-nocuda-lifecycle-") as temp:
        source, binary = Path(temp) / "lifecycle.cpp", Path(temp) / "lifecycle"
        source.write_text(code)
        command = [compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-Wno-deprecated-declarations", str(source), "-o", str(binary), "-lsqlite3"]
        if sys.platform != "darwin":
            command.append("-lcrypto")
        compiled = subprocess.run(command, text=True, capture_output=True)
        run = subprocess.run([str(binary), temp], text=True, capture_output=True) if compiled.returncode == 0 else None
        report = {
            "status": "TEST_HARNESS_FAIL" if compiled.returncode else ("PASS" if run and run.returncode == 0 else "PRODUCT_FAIL"),
            "scope": __doc__, "native": "NOT_RUN", "command": command,
            "compile_exit": compiled.returncode, "run_exit": run.returncode if run else None,
            "compiler_log": compiled.stdout + compiled.stderr,
            "output": run.stdout + run.stderr if run else "",
            "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
            "extracted_functions": extracted,
        }
        if args.evidence_dir:
            args.evidence_dir.mkdir(parents=True, exist_ok=True)
            stem = args.evidence_dir / f"task-1-lifecycle-{args.label}"
            stem.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
            stem.with_suffix(".cpp").write_text(code)
            stem.with_suffix(".log").write_text(report["compiler_log"] + report["output"])
        print(report["compiler_log"] + report["output"])
        print(report["status"])
        return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

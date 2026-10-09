#!/usr/bin/env python3
"""Candidate sidecar adapters. Original tests and product sources remain untouched.

The four historical replays retain their original assertions. Missing production
helpers are extracted from the frozen source graph, never reimplemented as an
expected-answer stub. Only native Alert is an additional observable host seam.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
from leverage_panel_test import body_of

INC = ROOT / "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth"
DESIGN = (INC / "JPW_UI_Design.mqh").read_text()
PRESENT = (INC / "JPW_Alavancagem_Presentation.mqh").read_text()


def function(source: str, signature: str) -> str:
    return signature + "{" + body_of(source, signature) + "}\n"


def passes() -> str:
    return ("bool g_jpw_ui_changed=false; int g_jpw_ui_pass_depth=0;\n" +
            function(DESIGN, "void JPWUIDesignBeginPass()") +
            function(DESIGN, "void JPWUIDesignEndPass()"))


def invalidate(default: bool = True) -> str:
    return "void JPWInvalidateDialogContent(const int route" + ("=-1" if default else "") + "){" + body_of(PRESENT, "void JPWInvalidateDialogContent(") + "}\n"


def ui_primitives() -> str:
    # Native object APIs stay in the original map-backed shim. All cache,
    # successful-write and redraw accounting executes actual production code.
    return ("using ENUM_OBJECT_PROPERTY_INTEGER=int; using ENUM_OBJECT_PROPERTY_STRING=int; using ENUM_OBJECT=int; using uint=unsigned int;\n" +
            DESIGN[DESIGN.index("#define JPW_UI_PROPERTY_SLOTS"):DESIGN.index("bool JPWUIDesignDark(")] +
            function(DESIGN, "bool JPWUIDesignDark(const color background)") +
            re.sub(r"C'(\d+),(\d+),(\d+)'", lambda m: str(int(m[1])+(int(m[2])<<8)+(int(m[3])<<16)),
                   function(DESIGN, "color JPWUIDesignFocusInk(const color background)")))


def presentation_adapter():
    module = importlib.import_module("leverage_reliability_test")
    original = module.presentation_runtime
    def runtime(source: str, samples: str) -> str:
        code = original(source, samples)
        marker = "void JPWViewMetric("
        assert code.count(marker) == 1
        return code if "void JPWUIDesignBeginPass()" in code else code.replace(marker, passes() + marker, 1)
    module.presentation_runtime = runtime
    return module


def details_adapter(module):
    # Extract instance state introduced by the retained dialog implementation.
    state = PRESENT[PRESENT.index("const int JPW_FOCUS_SIGNAL_ROLE"):PRESENT.index("void JPWInvalidateDialogContent(")]
    module.SHIM += ("\nbool g_details_content_dirty=true;\n" + state + ui_primitives() +
                    invalidate() + function(PRESENT, "bool JPWPresentationDialogObject(const string name)") +
                    function(PRESENT, "void JPWPresentationFailure(const string reason)") +
                    function(PRESENT, "bool JPWPresentationSetInteger(const string name,const ENUM_OBJECT_PROPERTY_INTEGER property,const long value)") +
                    "\nstd::vector<string> adapter_alerts; void Alert(const string& message){adapter_alerts.push_back(message);}\n")
    # A physical click requires an existing object. The historical renderer seam
    # creates no controls; instantiate only the specifically clicked button.
    # This supplies an input precondition, never event outcomes or expected state.
    module.MAIN = module.MAIN.replace(
        'void click(const string&s){OnChartEvent',
        'void click(const string&s){if(ObjectFind(0,s)<0)ObjectCreate(0,s,OBJ_BUTTON,0,0,0);OnChartEvent')
    module.MAIN = module.MAIN.replace(
        ' std::cout<<"HOST_DETAILS_EVENT:',
        ' g_account_known=false;g_sample_context="";JPWOpenCockpit();\n'
        ' check(!adapter_alerts.empty()&&g_refresh_requested,"unavailable identity requests capture and observable Alert");\n'
        ' std::cout<<"HOST_DETAILS_EVENT:')
    return module


def scheduler_adapter(module):
    module.INDICATOR_BOUNDARY += "\nbool g_details_content_dirty=false;\n" + invalidate()
    # Explicit real-helper controls cover route matching and closed dialog.
    module.INDICATOR_MAIN = module.INDICATOR_MAIN.replace("int main(){", """int main(){
 g_raiz_details_open=false;g_details_content_dirty=false;JPWInvalidateDialogContent();
 check(!g_details_content_dirty,"closed dialog is not invalidated");
 g_raiz_details_open=true;g_raiz_tab=JPW_ROUTE_STOPS;JPWInvalidateDialogContent(JPW_ROUTE_STOP_ROW);
 check(!g_details_content_dirty,"unrelated route is not invalidated");
 JPWInvalidateDialogContent(JPW_ROUTE_STOPS);
 check(g_details_content_dirty,"matching Stop route requests fresh content");
 g_details_content_dirty=false;JPWInvalidateDialogContent();
 check(g_details_content_dirty,"explicit all-route invalidation requests fresh content");
 g_raiz_details_open=false;
""", 1)
    return module



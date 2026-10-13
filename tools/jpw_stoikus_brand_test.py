#!/usr/bin/env python3
"""Replay the production brand header and validate traced bitmap resources.

Chart objects and text metrics are synthetic seams. This test is not proof of
MetaEditor compilation, native bitmap loading, visual DPI or MT5 interaction.
"""
from pathlib import Path
import hashlib
import re
import shutil
import struct
import subprocess
import tempfile
import json
from leverage_panel_test import body_of


import sys, os
from leverage_host_shim import source_root, translate_arrays, complete_design_shim

from jpw_nocuda_fibo_ui_test import SHIM
from leverage_source import expanded_source

from leverage_host_shim import source_root, translate_arrays, complete_design_shim
ROOT = source_root()
BASE = ROOT / 'mt5/jpw-alavancagem-atual/MQL5'
HEADER = BASE / 'Include/JPWealth/JPW_Stoikus_Brand.mqh'
IMAGES = BASE / 'Images/JPWealth'
SOURCE = ROOT / 'assets/jp-wealth-brand-red.png'

MAIN = r'''
int checks=0,failures=0;
void check(bool ok,const string&m){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<m<<"\n";}}
int main(){
 for(int font=9;font<=24;font++)for(int d:{100,125,150,200})for(bool dark:{false,true})
 for(int width:{70,120,280,600,1000})for(int height:{20,32,60,96}){
  objects.clear();dpi=d;
  const bool logo=JPWGenetrixHeader("MARK","TITLE",10,20,width,height,font,
    dark?0xeeeeee:0x222222,dark,"NoCuda · SYNTHETIC",1006);
  check(logo==(ObjectFind(0,"MARK")>=0),"return describes present bitmap object");
  if(logo){
   const auto&o=objects["MARK"];
   check(o.number.at(OBJPROP_XDISTANCE)==10&&o.number.at(OBJPROP_YDISTANCE)>=20,
     "logo retains absolute header origin");
   check(o.number.at(OBJPROP_XSIZE)<=width&&o.number.at(OBJPROP_YDISTANCE)+o.number.at(OBJPROP_YSIZE)<=20+height,
     "scaled logo remains in available header rectangle");
   const string resource=o.text.at(OBJPROP_BMPFILE);
   check(StringFind(resource,dark?"Dark_":"Light_")>=0,"correct theme resource selected");
   check(o.number.at(OBJPROP_SELECTABLE)==0,"logo is decorative and cannot become anchor selection");
  }
  if(ObjectFind(0,"TITLE")>=0){
   const auto&o=objects["TITLE"];
   const string text=o.text.at(OBJPROP_TEXT);
   check(JPWGenetrixTextWidth(text,font)<=o.number.at(OBJPROP_XSIZE),"caption is measured rather than clipped");
   check(o.number.at(OBJPROP_XDISTANCE)+o.number.at(OBJPROP_XSIZE)==10+width,
     "caption stays before independent close control");
   check(StringFind(o.text.at(OBJPROP_TOOLTIP),JPW_PRODUCT_NAME)==0,
     "full identity remains available in tooltip");
  }
 }
 objects.clear();dpi=100;
 JPWGenetrixHeader("MARK","TITLE",10,20,1000,40,11,0,false,"Stops");
 check(ObjectFind(0,"MARK")>=0,"wide header creates logo");
 JPWGenetrixHeader("MARK","TITLE",10,20,120,40,11,0,false,"Stops");
 check(ObjectFind(0,"MARK")<0&&ObjectFind(0,"TITLE")>=0,"narrow transition removes previous logo and retains text");
 JPWGenetrixHeader("MARK","TITLE",10,20,0,40,11,0,false,"Stops");
 check(ObjectFind(0,"MARK")<0&&ObjectFind(0,"TITLE")<0,"zero area removes stale decorative objects");
 objects.clear();refuse_bitmap=true;
 JPWGenetrixHeader("MARK","TITLE",10,20,1000,40,11,0,false,"Stops");
 check(ObjectFind(0,"MARK")<0&&objects["TITLE"].number[OBJPROP_XDISTANCE]==10,
   "bitmap assignment refusal uses full-width textual fallback");
 check(objects["TITLE"].text[OBJPROP_TEXT]=="Stoikus · Stops","fallback retains public name and module");
 std::cout<<"GENETRIX_BRAND_RENDER: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native MT5 NOT_RUN\n";
 return failures?1:0;
}
'''


def indicator_admission_block(path: Path) -> tuple[str, str]:
    """Extract the actual OnInit count and refusal before namespace/preferences."""
    source = path.read_text()
    init = body_of(source, "OnInit")
    start = init.index("int copies=0;")
    refusal = init.index("if(copies>1)", start)
    opening = init.index("{", refusal)
    depth, end = 1, opening + 1
    while depth:
        if init[end] == "{": depth += 1
        elif init[end] == "}": depth -= 1
        end += 1
    namespace = "g_panel_prefix=" if path.name == "JPW_Alavancagem_Atual.mq5" else "g_nocuda_prefix="
    assert end < init.index(namespace), "duplicate refusal must precede retained namespace admission"
    return init[start:refusal], init[refusal:end]


def verify_indicator_admission(compiler: str) -> None:
    account = BASE / "Indicators/JPWealth/JPW_Alavancagem_Atual.mq5"
    nocuda = BASE / "Indicators/JPWealth/JPW_NoCuda_Channels.mq5"
    version = BASE / "Include/JPWealth/JPW_Alavancagem_Version.mqh"
    blocks = {"account": indicator_admission_block(account), "nocuda": indicator_admission_block(nocuda)}
    metadata = version.read_text()
    definitions = []
    for name in ("JPW_PRODUCT_NAME", "JPW_NOCUDA_SHORTNAME"):
        values = re.findall(r'^#define\s+' + name + r'\s+("[^"\n]*")\s*$', metadata, re.M)
        assert len(values) == 1, "public name macro must have one literal declaration"
        definitions.append("const std::string " + name + "=" + values[0] + ";")
    preamble = r'''
#include <string>
#include <vector>
#include <iostream>
using string=std::string;
const int INIT_FAILED=1,INIT_SUCCEEDED=0;
std::vector<string> indicators;int effects=0,last_copies=0;
int ChartIndicatorsTotal(int,int){return indicators.size();}
string ChartIndicatorName(int,int,int i){return indicators.at(i);}
int StringFind(const string&s,const string&n){auto p=s.find(n);return p==string::npos?-1:int(p);}
template<typename... Args> void Print(const Args&...){}
'''
    cases = {
        "account": [
            (["Stoikus · Cockpit 1.22.0"], 1),
            (["Stoikus · Cockpit 1.22.0", "JPW GENETRIX · Cockpit 1.21.2"], 2),
            (["Stoikus · Cockpit 1.22.0", "JPW_Alavancagem_Atual"], 2),
            (["Stoikus · Cockpit 1.22.0", "JPW GENETRIX · Cockpit 1.21.2", "JPW_Alavancagem_Atual"], 3),
            (["Stoikus · Cockpit 1.22.0", "Stoikus · NoCuda Channels", "Other indicator"], 1),
            (["Stoikus · Cockpit 1.22.0", "unrelated Stoikus · Cockpit"], 1),
        ],
        "nocuda": [
            (["Stoikus · NoCuda Channels"], 1),
            (["Stoikus · NoCuda Channels", "JPW GENETRIX · NoCuda Channels"], 2),
            (["Stoikus · NoCuda Channels", "JPW_NoCuda_Channels"], 2),
            (["Stoikus · NoCuda Channels", "JPW GENETRIX · NoCuda Channels", "JPW_NoCuda_Channels"], 3),
            (["Stoikus · NoCuda Channels", "Stoikus · Cockpit 1.22.0", "Other indicator"], 1),
            (["Stoikus · NoCuda Channels", "JPW GENETRIX · NoCuda Channels extra", "Stoikus · NoCuda Channels extra"], 1),
        ],
    }
    main = ["int main(){int failures=0;"]
    for kind, rows in cases.items():
        for names, count in rows:
            literals = ",".join(json.dumps(name, ensure_ascii=False) for name in names)
            main.append("indicators={" + literals + "};effects=0;last_copies=0;")
            main.append("{int result=" + kind + "_admit();if(last_copies!=" + str(count) +
                        "||result!=" + ("INIT_FAILED" if count > 1 else "INIT_SUCCEEDED") +
                        "||effects!=" + str(int(count <= 1)) + ")failures++;}")
    main.append('std::cout<<"ALIAS_GUARD_CASES: 12 / failures="<<failures<<"\\n";return failures?1:0;}')
    legacy_patterns = {
        "account": r'\s*\|\|\s*(?:StringFind\(installed,"JPW GENETRIX · Cockpit"\)==0|installed=="JPW_Alavancagem_Atual")',
        "nocuda": r'\s*\|\|\s*ChartIndicatorName\(0,0,i\)=="(?:JPW GENETRIX · NoCuda Channels|JPW_NoCuda_Channels)"',
    }
    with tempfile.TemporaryDirectory(prefix="stoikus-alias-guards-") as folder:
        folder = Path(folder)
        for trial in ("actual", "without_legacy", "accept_all"):
            functions = []
            for kind, (count_block, refusal) in blocks.items():
                changed = count_block
                if trial == "without_legacy":
                    changed, substitutions = re.subn(legacy_patterns[kind], "", changed)
                    assert substitutions == 2, "counterexample must remove both legacy aliases"
                elif trial == "accept_all":
                    opening = changed.index("if(") + 3
                    depth, closing = 1, opening
                    while depth:
                        if changed[closing] == "(": depth += 1
                        elif changed[closing] == ")": depth -= 1
                        closing += 1
                    changed = changed[:opening] + "true" + changed[closing - 1:]
                functions.append("int " + kind + "_admit(){" + changed +
                                 "last_copies=copies;" + refusal + "effects++;return INIT_SUCCEEDED;}")
            cpp = folder / (trial + ".cpp")
            cpp.write_text(preamble + "\n".join(definitions + functions + main))
            binary = folder / trial
            compiled = subprocess.run([compiler, "-std=c++17", str(cpp), "-o", str(binary)], capture_output=True, text=True)
            assert compiled.returncode == 0, compiled.stderr
            result = subprocess.run([str(binary)], capture_output=True, text=True)
            assert (result.returncode == 0) == (trial == "actual"), trial + ": " + result.stdout
            print("ALIAS_GUARD_TRIAL:", trial, "exit", result.returncode, result.stdout.strip())
    print("ALIAS_GUARD_SOURCE_SHA256:", json.dumps({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (account, nocuda, version)}, sort_keys=True))
    print("PASS actual OnInit count/refusal, old/new aliases, unrelated indicators and two sensitive counterexamples; native MT5 NOT_RUN")


def main():
    compiler = shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        print('ENVIRONMENT_ERROR: C++ compiler unavailable')
        return 2
    verify_indicator_admission(compiler)
    source = expanded_source(HEADER)
    if re.search(r'\b(AccountInfo\w*|CopyRates|CopyBuffer|Database\w*|File\w*|Order\w*|Position\w*|GlobalVariable\w*)\s*\(', source):
        raise AssertionError('Brand header reaches a financial/persistence boundary')
    provenance = (IMAGES / 'JPW_Stoikus_Logo.provenance.md').read_text()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() in provenance
    declared = re.findall(r'^#resource "[^"\n]*?(JPW_Stoikus_[^"\n]+\.bmp)"', source, flags=re.M)
    assert len(declared) == len(set(declared)) == 8
    for name in declared:
        data = (IMAGES / name).read_bytes()
        scale = int(name.rsplit('_', 1)[1].split('.')[0])
        expected = {100: (147, 16), 125: (184, 20), 150: (221, 24), 200: (295, 32)}[scale]
        assert data[:2] == b'BM' and struct.unpack_from('<ii', data, 18) == expected
        assert struct.unpack_from('<H', data, 28)[0] == 24
        assert hashlib.sha256(data).hexdigest() in provenance
        offset = struct.unpack_from('<I', data, 10)[0]
        background = bytes((54, 45, 39) if '_Dark_' in name else (244, 238, 233))
        assert data[offset:offset+3] == background, 'Opaque background must match existing chrome'
    consumers = [BASE / 'Include/JPWealth' / name for name in
                 ('JPW_Alavancagem_Presentation.mqh', 'JPW_NoCuda_UI.mqh', 'JPW_NoCuda_Fibo_UI.mqh')]
    for path in consumers:
        assert '#include <JPWealth/JPW_Stoikus_Brand.mqh>' in path.read_text()
        assert 'JPWGenetrixHeader(' in path.read_text()
    presentation = consumers[0].read_text()
    assert re.search(r'const\s+string\s+launcher_label\s*=\s*"Stoikus · Conta"\s*;', presentation), "actual labelled launcher required"
    assert 'TextGetSize(launcher_label,button_text_width,button_text_height)' in presentation, "launcher label must be measured"
    direct = ('ObjectSetString(0,launcher_text,OBJPROP_TEXT,launcher_label)' in presentation or
              'JPWPresentationSetString(launcher_text,OBJPROP_TEXT,launcher_label)' in presentation)
    painted = 'JPWPresentationSetString(launcher_text,OBJPROP_TEXT,painted_label)' in presentation
    assert direct or painted, "measured label must be assigned"
    if painted:
        assert 'string painted_label=launcher_label;' in presentation, "painted caption originates from full functional label"
        assert 'TextGetSize(painted_label,button_text_width,button_text_height)' in presentation, "painted caption must itself be measured"
        assert re.search(r'if\(button_width>button_budget\)\s*\{\s*painted_label="Conta";', presentation), "compact caption requires demonstrated width shortage"
        assert 'JPWPresentationSetString(launcher_text,OBJPROP_TOOLTIP,launcher_label)' in presentation, "compact caption retains full identity"
        writes = re.findall(r'(?<![A-Za-z_])painted_label\s*=\s*([^;]+);', presentation)
        assert writes == ['launcher_label','"Conta"'], "caption substitutions remain explicit and bounded"
    if direct and 'JPWPresentationSetString(launcher_text,OBJPROP_TEXT,launcher_label)' in presentation or painted:
        wrapper = re.search(r'bool\s+JPWPresentationSetString\s*\([^)]*\)\s*\{[^}]*\}', presentation, re.S)
        assert wrapper and 'JPWUIDesignSetString(name,property,value)' in wrapper.group(0), "assignment wrapper must forward exact property/value"
    assert 'JPWDetailsWrap(JPW_PRODUCT_TAGLINE,inner,lines)' in presentation
    source = re.sub(r'^#(?:if.*|endif.*|resource.*)\n', '', source, flags=re.M)
    source = re.sub(r'^#define\s+(JPW_GENETRIX_BRAND_MQH|JPW_ALAVANCAGEM_VERSION_MQH)\s*\n', '', source, flags=re.M)
    shim = SHIM.replace('int StringFind(const string&s,const string&n){auto p=s.find(n);','int StringFind(const string&s,const string&n,int start=0){auto p=s.find(n,start);').replace('bool ObjectSetString(int,const string&n,int p,const string&v){',
                        'bool refuse_bitmap=false;\nbool ObjectSetString(int,const string&n,int p,const string&v){if(refuse_bitmap&&p==OBJPROP_BMPFILE)return false;')
    with tempfile.TemporaryDirectory(prefix='jpw-genetrix-brand-') as folder:
        path = Path(folder)
        (path / 'brand.cpp').write_text(complete_design_shim(shim) + translate_arrays(source) + MAIN)
        compiled = subprocess.run([compiler, '-std=c++17', '-O1', str(path / 'brand.cpp'), '-o', str(path / 'brand')], text=True, capture_output=True)
        if compiled.returncode:
            print(compiled.stderr)
            return compiled.returncode
        result = subprocess.run([str(path / 'brand')], text=True, capture_output=True)
        print(result.stdout, end='')
        print(result.stderr, end='')
        print('BRAND_SOURCE_SHA256:', hashlib.sha256(HEADER.read_bytes()).hexdigest())
        print('RESOURCES: 8 traced RGB BMPs; site source hash confirmed; native MT5 NOT_RUN')
        return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())

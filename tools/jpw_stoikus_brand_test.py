#!/usr/bin/env python3
"""Replay the production brand header and validate traced bitmap resources.

Chart objects and text metrics are synthetic seams. This test is not proof of
MetaEditor compilation, native bitmap loading, visual DPI or MT5 interaction.
"""
from pathlib import Path
import hashlib
import base64
import xml.etree.ElementTree as ET
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
 // The approved signature stays at its native DPI size; it is never cropped or
 // silently downscaled to fit a shorter slot. Functional labels own the budget.
 const int mark_width[4]={240,300,360,480},mark_height[4]={28,35,42,56};
 const int display_scale[4]={100,125,150,200};
 for(int i=0;i<4;i++){
  objects.clear();dpi=display_scale[i];
  JPWGenetrixHeader("MARK","TITLE",10,20,1600,mark_height[i],11,0,false,"Conta");
  check(ObjectFind(0,"MARK")>=0,"approved signature appears when exact DPI rectangle fits");
  if(ObjectFind(0,"MARK")>=0){
   check(objects["MARK"].number[OBJPROP_XSIZE]==mark_width[i]&&objects["MARK"].number[OBJPROP_YSIZE]==mark_height[i],"approved signature uses exact dimensions per DPI");
   check(objects["MARK"].text[OBJPROP_BMPFILE].find("_"+std::to_string(display_scale[i])+".bmp")!=string::npos,"resource scale agrees with painted dimensions");
   check(objects["MARK"].text[OBJPROP_TOOLTIP]=="Stoikus by JP Wealth","decorative tooltip exposes full attribution");
  }
  JPWGenetrixHeader("MARK","TITLE",10,20,1600,mark_height[i]-1,11,0,false,"NoCuda · Gráficos");
  check(ObjectFind(0,"MARK")<0,"short header removes bitmap instead of shrinking approved lettering");
  check(ObjectFind(0,"TITLE")>=0&&objects["TITLE"].text[OBJPROP_TEXT].find("NoCuda")!=string::npos,"short header retains functional NoCuda title");
  objects.clear();
  JPWGenetrixHeader("MARK","TITLE",10,20,mark_width[i],mark_height[i],11,0,false,"");
  check(ObjectFind(0,"MARK")>=0&&ObjectFind(0,"TITLE")<0,"signature without section is painted once with no duplicate Stoikus caption");
 }
 objects.clear();dpi=100;refuse_logo_geometry=true;
 JPWGenetrixHeader("MARK","TITLE",10,20,1000,40,11,0,false,"Stops");
 check(ObjectFind(0,"MARK")<0&&objects["TITLE"].number[OBJPROP_XDISTANCE]==10,"rejected logo geometry removes partial bitmap and restores full-width text");
 refuse_logo_geometry=false;
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
 check(objects["TITLE"].text[OBJPROP_TEXT]=="Stoikus by JP Wealth · Stops","wide textual fallback retains attribution and module");
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


def verify_header_render(compiler: str, source: str) -> int:
    source = re.sub(r'^#(?:if.*|endif.*|resource.*)\n', '', source, flags=re.M)
    source = re.sub(r'^#define\s+(JPW_GENETRIX_BRAND_MQH|JPW_ALAVANCAGEM_VERSION_MQH)\s*\n', '', source, flags=re.M)
    shim = SHIM.replace('int StringFind(const string&s,const string&n){auto p=s.find(n);','int StringFind(const string&s,const string&n,int start=0){auto p=s.find(n,start);').replace('bool ObjectSetString(int,const string&n,int p,const string&v){',
                        'bool refuse_bitmap=false;\nbool ObjectSetString(int,const string&n,int p,const string&v){if(refuse_bitmap&&p==OBJPROP_BMPFILE)return false;')
    shim = shim.replace('bool ObjectSetInteger(int,const string&n,int p,long v){',
                        'bool refuse_logo_geometry=false;\nbool ObjectSetInteger(int,const string&n,int p,long v){if(refuse_logo_geometry&&n=="MARK"&&p==OBJPROP_YSIZE)return false;')
    with tempfile.TemporaryDirectory(prefix='jpw-genetrix-brand-') as folder:
        path = Path(folder)
        (path / 'brand.cpp').write_text(complete_design_shim(shim) + translate_arrays(source) + MAIN)
        compiled = subprocess.run([compiler, '-std=c++17', '-O1', str(path / 'brand.cpp'), '-o', str(path / 'brand')], text=True, capture_output=True)
        assert compiled.returncode == 0, compiled.stderr or compiled.stdout
        result = subprocess.run([str(path / 'brand')], text=True, capture_output=True)
        print(result.stdout, end='')
        print(result.stderr, end='')
        assert result.returncode == 0, "Production brand renderer failed the declared signature/fallback cases"
        return 0
def functional_launcher_replay(compiler):
    """Approved Conta caption: real renderer, measured target and product action."""
    import leverage_host_layout as host
    geo=host.geometry()
    actions=(BASE/'Include/JPWealth/JPW_Alavancagem_Actions.mqh').read_text()
    start=actions.index('   if(sparam==g_panel_prefix+"RAIZ_DETAILS_BUTTON")')
    stop=actions.index('   if(!g_raiz_details_open) return;',start)
    routing='''int account_open_calls=0,account_front_calls=0;
void JPWOpenCockpit(){account_open_calls++;g_raiz_details_open=true;}
void JPWRenderRaizDetails(){account_front_calls++;}
'''
    routing+='void LauncherAction(const string sparam){'+actions[start:stop]+'}\n'
    geo.HUD_MAIN=geo.HUD_MAIN[:geo.HUD_MAIN.index('int main(){')]+routing+r'''
int main(){
 int checks=0,failures=0,cases=0;
 auto check=[&](bool ok,const string &why){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<why<<"\n";}};
 for(int dpi:{96,120,144,192})for(int width:{160,200,800})for(int failure:{0,1,2})for(bool collapsed:{false,true}){
  mock_screen_dpi=dpi;InpFontSize=10;g_stoikus_options=false;
  host_window_resource_fail=failure==1;host_window_text_fail=failure==2;
  DrawHUD(width,1200,0,0,false);g_stoikus_visual.collapsed=collapsed;JPWRenderHUD();
  const bool pill=objects.count(g_panel_prefix+"HUD_RESTORE");
  const string target=g_panel_prefix+(pill?"HUD_RESTORE":"RAIZ_DETAILS_BUTTON");
  check(objects.count(target)&&WindowTextValid(target,JPWUIDesignPx(4)),"functional Conta has measured opaque text and bounded resource/native target dpi="+IntegerToString(dpi)+" width="+IntegerToString(width)+" failure="+IntegerToString(failure)+" collapsed="+IntegerToString(collapsed));
  if(!objects.count(target)){cases++;continue;}
  const string caption=WindowCaption(target);
  check(caption==(pill?"Stoikus":"Conta"),"approved functional launcher caption follows shared panel contract dpi="+IntegerToString(dpi)+" width="+IntegerToString(width)+" failure="+IntegerToString(failure)+" caption="+caption);
  const auto &n=objects[target].number;long x=n.at(OBJPROP_XDISTANCE)+n.at(OBJPROP_XSIZE)/2;double y=n.at(OBJPROP_YDISTANCE)+n.at(OBJPROP_YSIZE)/2;
  check(n.at(OBJPROP_XDISTANCE)>=0&&n.at(OBJPROP_YDISTANCE)>=0&&n.at(OBJPROP_XDISTANCE)+n.at(OBJPROP_XSIZE)<=width&&n.at(OBJPROP_YDISTANCE)+n.at(OBJPROP_YSIZE)<=1200,"launcher geometry stays inside chart");
  scope_clock_ms+=300;string route;
  check(JPWStoikusHUDEvent(CHARTEVENT_CLICK,x,y,"",route),"actual HUD rectangle dispatch accepts launcher click");
  if(collapsed)check(!g_stoikus_visual.collapsed&&route=="","collapsed Conta restores summary through actual action");
  else {
   check(route==g_panel_prefix+"RAIZ_DETAILS_BUTTON","launcher routes exact canonical account target");
   g_raiz_details_open=false;int opened=account_open_calls;LauncherAction(route);check(account_open_calls==opened+1&&g_raiz_details_open,"actual launcher action opens Conta");
   int fronted=account_front_calls;LauncherAction(route);check(account_front_calls==fronted+1&&JPWUIOwner()==g_panel_prefix,"actual repeated launcher action fronts owned Conta");
  }
  host_window_resource_fail=false;host_window_text_fail=false;cases++;
 }
 std::cout<<"STOIKUS_FUNCTIONAL_CONTA: "<<cases<<" DPI/width/collapse/resource cases, "<<checks<<" checks, "<<failures<<" failures; native MT5 NOT_RUN\n";
 return failures?1:0;
}
'''
    return geo.hud_layout_replay(compiler)


def main():
    compiler = shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        print('ENVIRONMENT_ERROR: C++ compiler unavailable')
        return 2
    verify_indicator_admission(compiler)
    source = expanded_source(HEADER)
    if re.search(r'\b(AccountInfo\w*|CopyRates|CopyBuffer|Database\w*|File\w*|Order\w*|Position\w*|GlobalVariable\w*)\s*\(', source):
        raise AssertionError('Brand header reaches a financial/persistence boundary')
    verify_header_render(compiler, source)
    provenance = (IMAGES / 'JPW_Stoikus_Logo.provenance.md').read_text()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() in provenance
    for theme in ('clara', 'escura'):
        vector = ROOT / 'assets/stoikus' / ('stoikus-assinatura-' + theme + '.svg')
        assert hashlib.sha256(vector.read_bytes()).hexdigest() in provenance
        svg = ET.fromstring(vector.read_text())
        assert (svg.attrib['width'], svg.attrib['height']) == ('240', '28')
        lettering = svg.findall('.//{http://www.w3.org/2000/svg}text')
        assert [(n.text, n.attrib['font-size'], n.attrib['font-weight']) for n in lettering] == [('Stoikus', '24', '400'), ('by', '12', '400')]
        image = svg.find('.//{http://www.w3.org/2000/svg}image')
        assert image.attrib['height'] == '12' and image.attrib['preserveAspectRatio'] == 'xMidYMid meet'
        assert base64.b64decode(image.attrib['href'].split(',', 1)[1]) == SOURCE.read_bytes(), 'Institutional mark must be the original PNG bytes'
    declared = re.findall(r'^#resource "[^"\n]*?(JPW_Stoikus_[^"\n]+\.bmp)"', source, flags=re.M)
    assert len(declared) == len(set(declared)) == 8
    for name in declared:
        data = (IMAGES / name).read_bytes()
        scale = int(name.rsplit('_', 1)[1].split('.')[0])
        expected = {100: (240, 28), 125: (300, 35), 150: (360, 42), 200: (480, 56)}[scale]
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
    # The approved retained HUD uses functional Conta; the full Stoikus
    # signature remains verified above on all8BMPs and actual brand headers.
    assert 'JPWStoikusHUDRender();' in body_of(presentation,'void JPWRenderHUDBody()'), "launcher must delegate to actual retained HUD"
    if functional_launcher_replay(shutil.which('clang++') or shutil.which('g++')):
        return 1
    assert 'JPWDetailsWrap(JPW_PRODUCT_TAGLINE,inner,lines)' in presentation
    print('BRAND_SOURCE_SHA256:', hashlib.sha256(HEADER.read_bytes()).hexdigest())
    print('RESOURCES: 8 traced RGB BMPs; approved signature geometry and source hash confirmed; native MT5 NOT_RUN')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

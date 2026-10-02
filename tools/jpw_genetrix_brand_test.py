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

from jpw_nocuda_fibo_ui_test import SHIM
from leverage_source import expanded_source

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'mt5/jpw-alavancagem-atual/MQL5'
HEADER = BASE / 'Include/JPWealth/JPW_Genetrix_Brand.mqh'
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
 check(objects["TITLE"].text[OBJPROP_TEXT]=="JPW GENETRIX · Stops","fallback retains public name and module");
 std::cout<<"GENETRIX_BRAND_RENDER: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native MT5 NOT_RUN\n";
 return failures?1:0;
}
'''


def main():
    compiler = shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        print('ENVIRONMENT_ERROR: C++ compiler unavailable')
        return 2
    source = expanded_source(HEADER)
    if re.search(r'\b(AccountInfo\w*|CopyRates|CopyBuffer|Database\w*|File\w*|Order\w*|Position\w*|GlobalVariable\w*)\s*\(', source):
        raise AssertionError('Brand header reaches a financial/persistence boundary')
    provenance = (IMAGES / 'JPW_Genetrix_Logo.provenance.md').read_text()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() in provenance
    declared = re.findall(r'^#resource "[^"\n]*?(JPW_Genetrix_[^"\n]+\.bmp)"', source, flags=re.M)
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
        assert '#include <JPWealth/JPW_Genetrix_Brand.mqh>' in path.read_text()
        assert 'JPWGenetrixHeader(' in path.read_text()
    presentation = consumers[0].read_text()
    assert 'TextGetSize("Genetrix",button_text_width,button_text_height)' in presentation
    assert 'ObjectSetString(0,button,OBJPROP_TEXT,"Genetrix")' in presentation
    assert 'JPWDetailsWrap(JPW_PRODUCT_TAGLINE,inner,lines)' in presentation
    source = re.sub(r'^#(?:if.*|endif.*|resource.*)\n', '', source, flags=re.M)
    source = re.sub(r'^#define\s+(JPW_GENETRIX_BRAND_MQH|JPW_ALAVANCAGEM_VERSION_MQH)\s*\n', '', source, flags=re.M)
    shim = SHIM.replace('bool ObjectSetString(int,const string&n,int p,const string&v){',
                        'bool refuse_bitmap=false;\nbool ObjectSetString(int,const string&n,int p,const string&v){if(refuse_bitmap&&p==OBJPROP_BMPFILE)return false;')
    with tempfile.TemporaryDirectory(prefix='jpw-genetrix-brand-') as folder:
        path = Path(folder)
        (path / 'brand.cpp').write_text(shim + source + MAIN)
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

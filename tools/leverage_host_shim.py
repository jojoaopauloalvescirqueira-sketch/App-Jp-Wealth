"""Versioned syntax/API seams only; never a native MQL5 compiler."""
import os
import re
import tempfile
from pathlib import Path

def source_root():
    value = os.environ.get("JPW_TEST_ROOT")
    if not value:
        value = str(Path(__file__).resolve().parents[1])
    keep = os.environ.get("JPW_JUDGE_KEEP_TEMP")
    if keep:
        Path(keep).mkdir(parents=True,exist_ok=True)
        class RetainedTemporaryDirectory:
            def __init__(self,suffix=None,prefix=None,dir=None,**kwargs):
                self.name=tempfile.mkdtemp(suffix=suffix or "",prefix=prefix or "tmp",dir=keep)
            def __enter__(self):return self.name
            def __exit__(self,*args):return False
            def cleanup(self):pass
        tempfile.TemporaryDirectory=RetainedTemporaryDirectory
    return Path(value).resolve()

def translate_arrays(source):
    # Control flow/math stay untouched. MQL dynamic arrays are C++ vectors.
    source = re.sub(r"\b(\w+)\s+((?:\w+\[\]\s*,\s*)+\w+\[\])\s*;",
        lambda m: "std::vector<"+m[1]+"> "+m[2].replace("[]","")+";", source)
    source = re.sub(r"\b(\w+)\s+&(\w+)\[\]", r"std::vector<\1>& \2", source)
    source = re.sub(r"\b(\w+)\s+(\w+)\[\]\s*;", r"std::vector<\1> \2;", source)
    # Only local initialized label lists passed into vector-reference seams.
    source = re.sub(r"\bstring\s+(\w+)\[\d+\]\s*=\s*\{", r"std::vector<string> \1={", source)
    source = re.sub(r"C'(\d+),(\d+),(\d+)'", lambda m: str(int(m[1]) | int(m[2]) << 8 | int(m[3]) << 16), source)
    source = re.sub(r'(JPWUIDesignPrimary(?:Fill|Ink)\()const color background', r'\1[[maybe_unused]] const color background', source)
    return source

DESIGN_API_SHIM = r"""
#include <cmath>
#include <map>
constexpr int FW_NORMAL=400,COLOR_FORMAT_ARGB_NORMALIZE=0;
double MathRound(double v){return std::round(v);}
double MathSqrt(double v){return std::sqrt(v);}
template<class T,class U>void ArrayInitialize(std::vector<T>& values,U value){std::fill(values.begin(),values.end(),(T)value);}
uint StringGetCharacter(const string& s,int at){return at>=0&&at<(int)s.size()?(unsigned char)s[at]:0;}
uint ColorToARGB(color c,uint alpha=255){return (alpha<<24)|((uint(c)&255)<<16)|(uint(c)&65280)|((uint(c)>>16)&255);}
std::map<string,std::vector<uint>> host_resources;
bool ResourceCreate(const string& n,const std::vector<uint>& p,int w,int h,int,int,int,int){if(w<=0||h<=0||p.size()!=(size_t)w*h)return false;host_resources[n]=p;return true;}
bool ResourceFree(const string& n){return host_resources.erase(n)>0;}
"""

def complete_design_shim(shim):
    shim = shim.replace("constexpr int OBJPROP_READONLY=105;", "[[maybe_unused]] constexpr int OBJPROP_READONLY=105;")
    shim = shim.replace("TextSetFont(const string&,int size)", "TextSetFont(const string&,int size,int=FW_NORMAL)")
    # Constants must precede default-argument declaration; resource helpers need aliases.
    shim = shim.replace("constexpr int OBJ_LABEL", "constexpr int FW_NORMAL=400;\nconstexpr int OBJ_LABEL", 1) if "constexpr int OBJ_LABEL" in shim else shim.replace("constexpr int CHART_WIDTH_IN_PIXELS", "constexpr int FW_NORMAL=400;\nconstexpr int CHART_WIDTH_IN_PIXELS", 1)
    extension = DESIGN_API_SHIM.replace("FW_NORMAL=400,", "")
    # New helper types/events are real MQL APIs; missing host definitions are
    # adapter defects, not native compiler diagnostics.
    additions="using ulong=unsigned long;\nusing ENUM_OBJECT_PROPERTY_INTEGER=int;\n"
    if "OBJPROP_SELECTED" not in shim: additions+="constexpr int OBJPROP_SELECTED=500;\n"
    if not re.search(r"\bChartRedraw\s*\(",shim): additions+="int host_redraw_requests=0; void ChartRedraw(int){host_redraw_requests++;}\n"
    additions+="int JPWNoCudaUIQueryHeight(const int,const bool);\n"
    additions+="template<class... T>void Print(const T&... v){((std::cerr<<v),...);std::cerr<<'\\n';}\n"
    return shim + additions + extension

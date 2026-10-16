#!/usr/bin/env python3
"""Actual HUD + overview risk rendering; native MT5 NOT_RUN, canonical inputs unchanged."""
import shutil
import leverage_host_layout as layout
geo=layout.geometry()
geo.HUD_MAIN=geo.HUD_MAIN[:geo.HUD_MAIN.index('int main(){')]+r'''
int checks=0,failures=0;
void check(bool ok,const string&why){checks++;if(!ok){failures++;std::cerr<<"FAIL "<<why<<"\n";}}
string visible(){string all;for(const auto&o:objects)if(o.second.text.count(OBJPROP_TEXT))all+=o.second.text.at(OBJPROP_TEXT)+"\n";for(const auto&o:objects)all+=WindowText(o.first)+"\n";return all;}
string tips(){string all;for(const auto&o:objects)if(o.second.text.count(OBJPROP_TOOLTIP))all+=o.second.text.at(OBJPROP_TOOLTIP)+"\n";return all;}
void risk(const string value,int quality){g_cockpit_prefs.visible_mask=32;g_cockpit_snapshot.metric[5].value=value;g_cockpit_snapshot.metric[5].quality=(JPW_VIEW_QUALITY)quality;JPWRenderHUD();check(g_cockpit_snapshot.metric[5].value==value,"canonical risk string unchanged by painting");}
int main(){
 DrawHUD(1600,1000,0,0,false);g_stop_ready=true;g_stop_scope_valid=true;g_stop_scope_symbol="EURUSD.m";g_stop_scope_side=1;
 g_stop_sample.account_key=g_diagnostic_context;g_stop_sample.observed_mono_ms=1000;g_stop_sample.row_count=1;g_stop_rows={1};g_stop_quality=1;
 risk("125,50 USD · 1,25% balance",1);
 check(visible().find("1,25% saldo")!=string::npos&&visible().find("% balance")==string::npos,"HUD numeric denominator localized without changing tokens");
 check(visible().find("EURUSD.m")!=string::npos&&visible().find("Compra")!=string::npos,"visible attributed group uses accepted symbol and side");
 g_stop_scope_symbol="GBPJPY";g_stop_scope_side=-1;risk("0,00 USD · 0,00% balance",1);
 check(visible().find("GBPJPY")!=string::npos&&visible().find("Venda")!=string::npos&&visible().find("EURUSD.m")==string::npos,"changed accepted context replaces old group");
 g_diagnostic_context="other-account";risk("N/A",0);
 check(visible().find("GBPJPY")==string::npos&&visible().find("Grupo indisponível")!=string::npos,"mismatched account cannot show prior group");
 g_stop_sample.account_key=g_diagnostic_context;g_stop_scope_valid=false;g_stop_sample.row_count=0;g_stop_rows.clear();g_stop_quality=1;
 risk("0,00 USD · 0,00% balance",1);check(visible().find("Sem exposição confirmada")!=string::npos&&visible().find("0,00% saldo")!=string::npos,"confirmed no exposure distinct from unscoped NA");
 g_stop_quality=0;risk("N/A",0);check(visible().find("Sem exposição confirmada")==string::npos&&visible().find("Grupo indisponível")!=string::npos,"NA never inferred as no exposure");
 g_stop_scope_valid=true;g_stop_scope_symbol="LONG_ACCEPTED_SYMBOL_FOR_SCOPE";g_stop_scope_side=1;g_stop_quality=1;g_stop_sample.row_count=1;g_stop_rows={1};chart_width=250;
 risk("125,50 USD · 1,25% balance",1);
 check(visible().find("125,50")==string::npos&&visible().find("1,25%")==string::npos&&visible().find("Risco")!=string::npos,"constrained scope uses orientation only, never an unscoped numeric amount");
 check(tips().find("LONG_ACCEPTED_SYMBOL_FOR_SCOPE")!=string::npos&&tips().find("1,25% saldo")!=string::npos,"compact fallback preserves full accepted scope/value access");
 scope_clock_ms=40000;risk("N/A",0);check(visible().find("LONG_ACCEPTED_SYMBOL_FOR_SCOPE")==string::npos,"expired sample cannot present prior group");
 std::cout<<"TASK2_R1_RISK_HUD: "<<checks-failures<<" PASS / "<<failures<<" FAIL; native NOT_RUN\n";return failures?1:0;
}
'''
hud_result=geo.hud_layout_replay(shutil.which('clang++'))
# Replay the complete production overview branch, instrumenting only text drawing.
geo.LAYOUT_SHIM=geo.LAYOUT_SHIM.replace('struct Drawn{','std::map<string,string> captured;string detail_text;\nstruct Drawn{')
geo.LAYOUT_SHIM='#include <map>\n'+geo.LAYOUT_SHIM
geo.LAYOUT_SHIM=geo.LAYOUT_SHIM.replace('bool JPWCreateProtectedValue(const string&,const string&,int x,int y,int w,int=0){',
 'bool JPWCreateProtectedValue(const string&key,const string&value,int x,int y,int w,int=0){captured[key]=value;')
geo.LAYOUT_SHIM=geo.LAYOUT_SHIM.replace('bool JPWRaizCreateLabel(const string&,const string&,int x,int y,int=0){',
 'bool JPWRaizCreateLabel(const string&key,const string&value,int x,int y,int=0){captured[key]=value;')
source=geo.PRESENTATION.read_text()
first=next(line for line in source.splitlines() if 'JPWDetailsWrap(JPWCockpitMetricTitle(i,metric.title)+": "' in line)
scope=next(line for line in source.splitlines() if 'if(i==5) JPWDetailsWrap(JPWRiskDisplayScope()' in line)
geo.LAYOUT_SHIM+='void RenderRiskDetailFirstLine(){int i=5,inner=700;JPWCockpitMetric metric=g_cockpit_snapshot.metric[i];std::vector<string>lines;'+first+scope+'detail_text="";for(auto&line:lines)detail_text+=line+"\\n";}\n'
geo.LAYOUT_MAIN=r'''
int main(){
 g_stop_ready=true;g_stop_scope_valid=true;g_stop_scope_symbol="EURUSD.m";g_stop_scope_side=1;
 g_stop_sample.account_key=g_diagnostic_context;g_stop_quality=1;
 for(string original:{"125,50 USD · 1,25% balance","0,00 USD · 0,00% balance","N/A"}){
  g_cockpit_snapshot.metric[5].value=original;g_cockpit_snapshot.metric[5].quality=(original=="N/A"?JPW_VIEW_NA:JPW_VIEW_CURRENT);
  g_cockpit_snapshot.metric[5].title="Stop risk";g_cockpit_page=0;captured.clear();
  RenderOverview(0,0,700,700,760);RenderRiskDetailFirstLine();
  string expected=original;StringReplace(expected,"% balance","% saldo");
  if(captured["CARD_5_VALUE"]!=expected||detail_text.find(expected)==string::npos)return 1;
  if(captured["CARD_5_REASON"].find("EURUSD.m")==string::npos||detail_text.find("EURUSD.m")==string::npos)return 2;
  if(g_cockpit_snapshot.metric[5].value!=original)return 3;
 }
 g_diagnostic_context="changed";captured.clear();RenderOverview(0,0,700,700,760);RenderRiskDetailFirstLine();
 if(captured["CARD_5_REASON"].find("EURUSD.m")!=string::npos||detail_text.find("EURUSD.m")!=string::npos)return 4;
 std::cout<<"TASK2_R1_RISK_CARD_DETAIL: three canonical values and changed context PASS; native NOT_RUN\n";return 0;
}
'''
card_result=geo.presentation_layout_replay(shutil.which('clang++'))
raise SystemExit(hud_result or card_result)

#property script_show_inputs
#include <JPWealth/JPW_NoCuda_Fibo_Core.mqh>
int jpw_ncf_asserts=0,jpw_ncf_failed=0;
void NCFCheck(const bool ok,const string message)
  { jpw_ncf_asserts++; if(!ok) { jpw_ncf_failed++; Print("FAIL: ",message); } }
void NCFFixture(JPWNCFSnapshot &s)
  {
   JPWNCFClear(s); s.reference_tf=60; s.source_name="Synthetic Fibo";
   s.symbol="SYNTHETIC"; s.feed="TEST_ONLY"; s.captured_utc=1800000000;
   s.source_created=1799999000; s.timeframes=0x1fffff;
   ArrayResize(s.opens,8);
   for(int i=0;i<8;i++) s.opens[i]=1700000000+i*3600;
   s.domain_from=s.opens[0]; s.domain_to=s.opens[7];
   s.anchor_time[0]=s.opens[0]+900; s.anchor_time[1]=s.opens[4]+1800;
   s.anchor_time[2]=s.opens[2]+1200;
   s.anchor_price[0]=1.1; s.anchor_price[1]=1.10425;
   s.anchor_price[2]=1.1060833333333333;
   for(int i=0;i<JPW_NCF_LEVELS;i++)
     { s.levels[i].value=4.0-i/8.0; s.levels[i].label="linha "+IntegerToString(i)+" : original";
       s.levels[i].line_color=7631988; s.levels[i].line_style=i%5; s.levels[i].line_width=1+i%5; }
  }
void OnStart()
  {
   JPWNCFSnapshot s,t; NCFFixture(s); string reason=""; double p=0,j=0;
   NCFCheck(JPWNCFValidate(s,reason)==JPW_NCF_VALID,"fixture exact intrabar accepted");
   NCFCheck(JPWNCFOrdinal(s,s.anchor_time[0],j) && MathAbs(j-0.25)<1e-12,"intrabar A preserved");
   NCFCheck(JPWNCFOrdinal(s,s.anchor_time[1],j) && MathAbs(j-4.5)<1e-12,"intrabar B preserved");
   NCFCheck(JPWNCFOrdinal(s,s.domain_to,j) && j==7,"domain endpoint");
   NCFCheck(!JPWNCFOrdinal(s,s.domain_to+1,j),"future cannot repeat last candle");
   NCFCheck(!JPWNCFOrdinal(s,s.domain_from-1,j),"past outside domain refused");
   NCFCheck(JPWNCFCandidatePrice(s,0,s.anchor_time[0],p,reason)==JPW_NCF_UNVERIFIED_NATIVE && MathAbs(p-1.1)<1e-12,"candidate A labelled unverified");
   NCFCheck(JPWNCFCandidatePrice(s,1,s.anchor_time[2],p,reason)==JPW_NCF_UNVERIFIED_NATIVE && MathAbs(p-s.anchor_price[2])<1e-12,"candidate C not native proof");
   NCFCheck(JPWNCFMeasure(s,1,s.anchor_time[2],p,reason)==JPW_NCF_UNVERIFIED_NATIVE && p==0,"public measure cannot leak candidate price");
   NCFCheck(JPWNCFCandidatePrice(s,0.3,s.anchor_time[0],p,reason)==JPW_NCF_INVALID,"nonexistent selected level refused");
   NCFCheck(JPWNCFCandidatePrice(s,5,s.anchor_time[0],p,reason)==JPW_NCF_INVALID,"out of grid level refused");
   string packed=JPWNCFPack(s);
   NCFCheck(packed!="" && JPWNCFUnpack(packed,t,reason)==JPW_NCF_VALID,"wire roundtrip");
   NCFCheck(JPWNCFPack(t)==packed,"full immutable snapshot roundtrip");
   NCFCheck(t.source_created==s.source_created,"creation identity retained");
   NCFCheck(t.anchor_time[0]==s.anchor_time[0],"no anchor snap");
   NCFCheck(t.levels[0].value==4 && t.levels[64].value==-4,"array order retained");
   NCFCheck(t.levels[13].label==s.levels[13].label,"labels unchanged");
   for(int i=0;i<65;i++) NCFCheck(t.levels[i].value==s.levels[i].value && t.levels[i].line_style==s.levels[i].line_style && t.levels[i].line_width==s.levels[i].line_width,"level exact "+IntegerToString(i));
   NCFCheck(JPWNCFUnpack(packed+"extra",t,reason)==JPW_NCF_CORRUPT,"trailing bytes rejected");
   NCFCheck(JPWNCFUnpack(StringSubstr(packed,0,StringLen(packed)-1),t,reason)==JPW_NCF_CORRUPT,"truncation rejected");
   NCFCheck(JPWNCFUnpack("99999999:x",t,reason)==JPW_NCF_CORRUPT,"unbounded frame rejected");
   JPWNCFCopy(s,t); t.resolver_version=2;
   NCFCheck(JPWNCFValidate(t,reason)==JPW_NCF_INCOMPATIBLE,"future resolver rejected");
   JPWNCFCopy(s,t); t.opens[3]=t.opens[2];
   NCFCheck(JPWNCFValidate(t,reason)==JPW_NCF_INVALID,"duplicate opening rejected");
   JPWNCFCopy(s,t); t.levels[2].value=t.levels[3].value;
   NCFCheck(JPWNCFValidate(t,reason)==JPW_NCF_INVALID,"duplicate level rejected");
   JPWNCFCopy(s,t); t.levels[2].value=0.3;
   NCFCheck(JPWNCFValidate(t,reason)==JPW_NCF_INVALID,"non grid level rejected without normalization");
   JPWNCFCopy(s,t); t.anchor_time[1]=t.anchor_time[0];
   NCFCheck(JPWNCFValidate(t,reason)==JPW_NCF_INVALID,"same time AB rejected");
   JPWNCFCopy(s,t); t.anchor_price[0]=0;
   NCFCheck(JPWNCFValidate(t,reason)==JPW_NCF_INVALID,"zero price rejected");
   JPWNCFCopy(s,t); t.anchor_price[0]=2; t.anchor_price[1]=1.9; t.anchor_price[2]=1.7;
   NCFCheck(JPWNCFCandidatePrice(t,1,t.anchor_time[2],p,reason)==JPW_NCF_UNVERIFIED_NATIVE && MathAbs(p-1.7)<1e-12,"negative slope and C below");
   JPWNCFCopy(s,t); t.anchor_price[1]=t.anchor_price[0];
   NCFCheck(JPWNCFCandidatePrice(t,0,t.domain_to,p,reason)==JPW_NCF_UNVERIFIED_NATIVE && p==t.anchor_price[0],"horizontal channel");
   JPWNCFCopy(s,t); for(int i=3;i<8;i++) t.opens[i]+=172800;
   t.domain_to=t.opens[7]; t.anchor_time[1]=t.opens[4]+1800;
   NCFCheck(JPWNCFOrdinal(t,t.opens[2]+88200,j) && MathAbs(j-2.5)<1e-12,"weekend interpolation no fabricated candles");
   string before=JPWNCFPack(s);
   for(int i=0;i<65;i++) JPWNCFCandidatePrice(s,s.levels[i].value,s.anchor_time[2],p,reason);
   NCFCheck(JPWNCFPack(s)==before,"queries do not mutate snapshot");
   JPWNCFCopy(s,t); t.source_name="Renamed"; t.captured_utc++;
   NCFCheck(JPWNCFSourceWire(s)==JPWNCFSourceWire(t),"semantic wire excludes volatile timestamp/name");
   t.timeframes=0;
   NCFCheck(JPWNCFSourceWire(s)!=JPWNCFSourceWire(t),"visibility explicitly included for controller normalization");
   Print("JPW NoCuda Fibo core: ",jpw_ncf_asserts," asserts; failures=",jpw_ncf_failed,
         ". NATIVE PARITY NOT TESTED; measurements remain UNVERIFIED_NATIVE.");
  }

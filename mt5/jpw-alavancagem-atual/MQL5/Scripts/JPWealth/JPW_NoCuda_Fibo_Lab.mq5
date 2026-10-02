#property script_show_inputs
#include <JPWealth/JPW_NoCuda_Fibo_Terminal.mqh>
// MANUAL isolated-terminal laboratory. Never reads account/positions or trades.
// This script does not certify Fibo geometry. Preserve the report, screenshot,
// exact source hashes, EX5 hash and terminal build as distinct native evidence.
input bool InpConfirmIsolatedLaboratory=false;
input string InpSourceFingerprint="";
input bool InpKeepSyntheticObjects=false;
void OnStart()
  {
   if(!InpConfirmIsolatedLaboratory || StringLen(InpSourceFingerprint)<16)
     { Print("NOT_RUN: confirme terminal isolado e informe fingerprint exato dos fontes."); return; }
   const long chart=ChartID(); const int tf=(int)ChartPeriod(chart);
   datetime times[]; ArraySetAsSeries(times,false);
   if(CopyTime(ChartSymbol(chart),(ENUM_TIMEFRAMES)tf,1,12,times)!=12)
     { Print("NOT_RUN: requer 12 barras encerradas no grafico de laboratorio."); return; }
   const string prefix="JPWNCF_LAB_"+IntegerToString((long)GetTickCount64())+"_";
   const string original=prefix+"original",clone=prefix+"clone",oracle=prefix+"oracle";
   JPWNCFSnapshot seed; JPWNCFClear(seed);
   seed.source_name="synthetic seed"; seed.symbol=ChartSymbol(chart); seed.feed="SYNTHETIC_LAB_ONLY";
   seed.reference_tf=tf; seed.captured_utc=(long)TimeGMT(); seed.timeframes=OBJ_ALL_PERIODS;
   seed.ray_left=true; seed.ray_right=true; seed.line_color=clrGray;
   // Intrabar anchors intentionally retain their seconds; no Close/OHLC snap.
   seed.anchor_time[0]=(long)times[1]+(long)(times[2]-times[1])/3;
   seed.anchor_time[1]=(long)times[8]+(long)(times[9]-times[8])/2;
   seed.anchor_time[2]=(long)times[4]+(long)(times[5]-times[4])/4;
   seed.anchor_price[0]=100.0; seed.anchor_price[1]=104.0; seed.anchor_price[2]=112.0;
   ArrayResize(seed.opens,12);
   for(int i=0;i<12;i++) seed.opens[i]=(long)times[i];
   seed.domain_from=seed.opens[0]; seed.domain_to=seed.opens[11];
   for(int i=0;i<65;i++)
     { seed.levels[i].value=4.0-i/8.0; seed.levels[i].label="raw "+DoubleToString(seed.levels[i].value,3);
       seed.levels[i].line_color=clrGray; seed.levels[i].line_style=STYLE_DOT; seed.levels[i].line_width=1; }
   string reason=""; JPWNCFSnapshot captured;
   const JPWNCFStatus created=JPWNCFClone(chart,original,seed,reason);
   JPWNCFStatus capture=created==JPW_NCF_VALID ?
      JPWNCFCapture(chart,original,tf,seed.symbol,seed.feed,captured,reason) : created;
   JPWNCFStatus cloned=capture==JPW_NCF_VALID ? JPWNCFClone(chart,clone,captured,reason) : capture;
   double auxiliary0=0,auxiliary1=0,candidate=0,measure=0;
   bool queried=capture==JPW_NCF_VALID && JPWNCFChannelOracle(chart,oracle,captured,
      seed.anchor_time[2],auxiliary0,auxiliary1,reason);
   JPWNCFStatus model=capture==JPW_NCF_VALID ? JPWNCFCandidatePrice(captured,0,seed.anchor_time[2],candidate,reason) : capture;
   JPWNCFStatus measurement=capture==JPW_NCF_VALID ? JPWNCFMeasure(captured,0,seed.anchor_time[2],measure,reason) : capture;
   FolderCreate("JPWealth"); FolderCreate("JPWealth\\NoCuda"); FolderCreate("JPWealth\\NoCuda\\Fibonacci");
   const string report="JPWealth\\NoCuda\\Fibonacci\\"+prefix+"report.txt";
   int f=FileOpen(report,FILE_WRITE|FILE_TXT|FILE_ANSI,0,CP_UTF8);
   string text="JPW Fibonacci isolated lab\r\nSource fingerprint: "+InpSourceFingerprint+
      "\r\nTerminal build: "+IntegerToString((long)TerminalInfoInteger(TERMINAL_BUILD))+
      "\r\nReference TF enum: "+IntegerToString(tf)+
      "\r\nCreated/Read/Clone property statuses: "+IntegerToString(created)+"/"+IntegerToString(capture)+"/"+IntegerToString(cloned)+
      "\r\nOBJ_CHANNEL auxiliary query: "+IntegerToString((int)queried)+
      "\r\nAuxiliary line 0: "+JPWNCFNumber(auxiliary0)+"; line 1: "+JPWNCFNumber(auxiliary1)+
      "\r\nCandidate AB0_C1: "+JPWNCFNumber(candidate)+"; status "+IntegerToString(model)+
      "\r\nPublic measure value: "+JPWNCFNumber(measure)+"; status "+IntegerToString(measurement)+
      "\r\nNative Fibo parity: UNVERIFIED_NATIVE. OBJ_CHANNEL is not a Fibo oracle by itself."+
      "\r\nRequired next evidence: native Fibo vs candidate at all65levels, intrabar, weekends, reversed anchors,"+
      "\r\nC above/below, left/right rays, source TF H1/H4, cross-TF fixed prices, zoom/DPI/theme captures."+
      "\r\nA property clone result is not universal geometry proof. No verification receipt is activated.\r\n";
   if(f!=INVALID_HANDLE) { FileWriteString(f,text); FileFlush(f); FileClose(f); Print("Laboratorio: ",report); }
   else Print("Falha no recibo local: ",GetLastError());
   Print(text);
   if(!InpKeepSyntheticObjects) { ObjectDelete(chart,original); ObjectDelete(chart,clone); }
   ChartRedraw(chart);
  }

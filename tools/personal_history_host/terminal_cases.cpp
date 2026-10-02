void terminal_reset_fixture(){
 JPWPersonalTestCapture(g_ph_capture);g_ph_capture.quality=0;g_ph_capture.leverage_valid=false;g_ph_capture.gross=0;
 g_ph_first.clear();g_ph_meta.clear();g_ph_quotes.clear();g_ph_profile.clear();
 for(int i=0;i<7;i++)g_ph_money_valid[i]=false;
 g_ph_divisor=1;g_ph_target="USD";g_ph_metric_reason="SYNTHETIC_INVALID_FINANCIAL_INPUT";
 g_ph_capture_account={1,"SyntheticServer","USD"};g_ph_math_valid=false;g_ph_estimated=false;
 host_personal_spec={"EURUSD",0,"EUR","USD",100000,true};host_personal_gross=1400;
}
void terminal_subject(){
 JPWPersonalSubject subject;JPWPersonalTestSubject(subject);subject.ticket="700";
 g_ph_first.push_back(subject);JPWPersonalTerminalMeta meta{};meta.specification="null";g_ph_meta.push_back(meta);
}
void terminal_case(const string& id){
 if(id!="HIS-AC14"){Print("TERMINAL_NOT_RUN|",id);return;}int start=host_asserts;
 for(int i=0;i<2;i++){
  terminal_reset_fixture();double invalid=i==0?std::numeric_limits<double>::quiet_NaN():std::numeric_limits<double>::infinity();
  JPWQuote quote{"EURUSD","EUR","USD",invalid,-invalid,1000000,false};g_ph_quotes.push_back(quote);
  Print("TERMINAL_JSON|",i==0?"quote-nan":"quote-inf","|",JPWPersonalTerminalDetails());
  REQUIRE(!g_ph_capture.leverage_valid&&g_ph_capture.quality==0,"invalid quotes do not become a financial peak");
 }
 for(int i=0;i<2;i++){
  terminal_reset_fixture();terminal_subject();host_personal_spec.contract_size=i==0?std::numeric_limits<double>::quiet_NaN():std::numeric_limits<double>::infinity();
  JPWPersonalTerminalRowMath(0,1000000);
  Print("TERMINAL_JSON|",i==0?"spec-nan":"spec-inf","|",JPWPersonalTerminalDetails());
  REQUIRE(g_ph_first[0].sl==0&&g_ph_first[0].sl_readable,"financially invalid specification does not destroy independently readable SL zero");
 }
 for(int i=0;i<2;i++){
  terminal_reset_fixture();JPWProfileEntry entry{string(64,'a'),string(64,'b'),i==0?std::numeric_limits<double>::quiet_NaN():std::numeric_limits<double>::infinity(),1000};g_ph_profile.push_back(entry);g_ph_divisor=entry.scale;
  Print("TERMINAL_JSON|",i==0?"profile-divisor-nan":"profile-divisor-inf","|",JPWPersonalTerminalDetails());
 }
 terminal_reset_fixture();terminal_subject();terminal_subject();g_ph_math_valid=true;host_personal_gross=1e308;
 JPWPersonalTerminalRowMath(0,1000000);REQUIRE(g_ph_math_valid&&g_ph_capture.gross==1e308,"first finite large contribution accepted");
 JPWPersonalTerminalRowMath(1,1000000);
 // Execute the actual final leverage_valid/quality assignment extracted from
 // CaptureStep; the rest of the native collection loop remains NOT_RUN.
 host_personal_acceptance_assignment();
 Print("TERMINAL_JSON|gross-overflow|",JPWPersonalTerminalDetails());
 REQUIRE(!g_ph_math_valid&&g_ph_metric_reason=="NONFINITE_AGGREGATE_NOTIONAL","finite individual contributions that overflow cannot confirm a zero gross");
 JPWPersonalPeak current{},estimated{};int changed=0;
 REQUIRE(!JPWPersonalPeakAccept(g_ph_capture,JPWPersonalTerminalDetails(),current,estimated,changed)&&!current.valid,"actual Core rejects aggregate overflow peak");
 Print("TERMINAL_CASE_PASS|",id,"|",host_asserts-start);
}

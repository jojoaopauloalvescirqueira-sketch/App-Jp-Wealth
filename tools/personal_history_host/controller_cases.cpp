void controller_case(const string& id){
if(id!="HIS-AC18"&&id!="HIS-AC11"&&id!="HIS-AC04"&&id!="HIS-AC12"){Print("CONTROLLER_NOT_RUN|",id);return;}int start=host_asserts;
// Use a distinct namespace so this facet does not reuse earlier case state.
PersonalFixture f;JPWPersonalHash("synthetic-controller-account",f.key);f.capture.account_key=f.key;f.open();f.observe();f.commit();
g_ph_store=f.context;g_ph_context=f.key;g_ph_token=f.token;g_ph_episodes=f.episodes;g_ph_loaded=true;g_ph_exclusive_file=123;
g_ph_current=f.current;g_ph_estimated_peak=f.estimated;g_ph_unwritten.clear();g_ph_pending_current=false;g_ph_pending_estimated=false;
host_alert_calls=0;host_sound_calls=0;host_no_sl=true;host_identity_ok=true;host_test_mode=false;host_sound_ok=true;
if(id=="HIS-AC12"){
 f.clock(2000);int changed=0;REQUIRE(JPWPersonalPeakAccept(f.capture,"durable-seven",f.current,f.estimated,changed),"seed durable Current peak seven");f.commit(changed);
 f.capture.quality=2;f.capture.gross=1600;REQUIRE(JPWPersonalPeakAccept(f.capture,"durable-estimated-eight",f.current,f.estimated,changed),"seed durable Estimated peak eight");f.commit(changed);
 g_ph_current=f.current;g_ph_current.leverage=10;g_ph_current.snapshot="memory-ten";
 g_ph_estimated_peak=f.estimated;g_ph_estimated_peak.leverage=11;g_ph_estimated_peak.snapshot="memory-estimated-eleven";
 g_ph_pending_current=true;g_ph_pending_estimated=true;g_ph_loaded=false;g_ph_restored_once=false;g_ph_next_open=0;
 JPWPersonalHash("synthetic-recovery-contender",g_ph_token);g_ph_store.db=INVALID_HANDLE;g_ph_store.writer=false;
 REQUIRE(!JPWPersonalControllerEnsureStore(GetTickCount64()),"actual EnsureStore falls back read-only under other live owner");
 REQUIRE(g_ph_current.leverage==10&&g_ph_current.snapshot=="memory-ten"&&g_ph_pending_current,"read-only recovery cannot replace pending higher Current maximum with seven");
 REQUIRE(g_ph_estimated_peak.leverage==11&&g_ph_estimated_peak.snapshot=="memory-estimated-eleven"&&g_ph_pending_estimated,"Estimated pending maximum remains independent during read-only recovery");
 f.close();host_wall=2010;host_mono=2010000;
 REQUIRE(JPWPersonalControllerEnsureStore(GetTickCount64()),"actual recovery acquires released writer");
 REQUIRE(g_ph_current.leverage==10&&g_ph_pending_current&&g_ph_estimated_peak.leverage==11&&g_ph_pending_estimated,"writer recovery also preserves higher memory peaks pending persistence");
 JPWPersonalClose(g_ph_store,host_wall,host_mono);host_wall=2000;host_mono=2000000;
}else if(id=="HIS-AC04"){
 host_no_sl=false;JPWPersonalControllerNotifyDue(f.capture,f.due,GetTickCount64());
 REQUIRE(host_alert_calls==0&&host_sound_calls==0&&g_ph_episodes[0].requested_count==0,"actual Controller fresh SL guard suppresses stale due request");
}else if(id=="HIS-AC11"){
 JPWPersonalStoreContext second;string other;JPWPersonalHash("synthetic-controller-owner-B",other);
 REQUIRE(JPWPersonalOpen(f.key,true,other,2010,2010000,second),"different SQLite owner takes expired synthetic lease");
 g_ph_exclusive_file=INVALID_HANDLE;JPWPersonalControllerNotifyDue(f.capture,f.due,GetTickCount64());
 REQUIRE(host_alert_calls==0&&host_sound_calls==0&&!g_ph_store.writer,"actual Controller cannot call channels after fenced owner and absent exclusive handle");
 JPWPersonalClose(second,2010,2010000);
}else{
 JPWPersonalControllerNotifyDue(f.capture,f.due,GetTickCount64());
 REQUIRE(host_alert_calls==1&&host_sound_calls==1&&g_ph_episodes[0].requested_count==1,"actual Controller grouped one popup and sound request");
 REQUIRE(g_ph_episodes[0].next_wall==2060&&g_ph_episodes[0].next_mono==2060000,"actual request instant drives sixty second cooldown");
 std::vector<JPWPersonalRow>rows;REQUIRE(JPWPersonalReadPage(f.key,"ALERT",0,100,rows,f.why)&&rows.size()==3,"actual Controller stores intent called result independently");
 REQUIRE(rows[0].payload.rfind("RESULT|",0)==0&&rows[1].payload.rfind("CALLED|",0)==0&&rows[2].payload.rfind("INTENT|",0)==0,"stage sequence proves requests only");
 string result;REQUIRE(JPWPersonalUnhex(rows[0].payload.substr(7),result)&&result.find("UNAVAILABLE")!=string::npos,"actual TerminalNotify result does not claim operator received channels");
 host_test_mode=true;host_alert_calls=0;host_sound_calls=0;JPWPersonalCapture capture=f.capture;int before=g_ph_episodes[0].requested_count;
 std::vector<int>due={0};JPWPersonalControllerNotifyDue(capture,due,GetTickCount64());
 REQUIRE(host_alert_calls==0&&host_sound_calls==0&&g_ph_episodes[0].requested_count==before+1,"tester channel unavailable explicitly no native requests");
 REQUIRE(JPWPersonalReadPage(f.key,"ALERT",0,100,rows,f.why)&&rows.size()==5,"tester records intent/result never CALLED");host_test_mode=false;
 bool error=false;host_sound_ok=false;string failed=JPWPersonalTerminalNotify("synthetic",error);
 REQUIRE(error&&failed.find("false")!=string::npos&&failed.find("UNAVAILABLE")!=string::npos,"sound request failure explicit without human delivery claim");host_sound_ok=true;
}
g_ph_store.db=INVALID_HANDLE;f.close();Print("CONTROLLER_CASE_PASS|",id,"|",host_asserts-start);
}
void ownership_phase(const string& phase){
PersonalFixture f;JPWPersonalHash("synthetic-process-ownership",f.key);f.capture.account_key=f.key;
if(phase=="hold"){
 f.initial();std::ofstream(host_root+"/holder-ready").put('1');
 for(int i=0;i<250&&!std::filesystem::exists(host_root+"/holder-release");i++)std::this_thread::sleep_for(std::chrono::milliseconds(20));
 REQUIRE(std::filesystem::exists(host_root+"/holder-release"),"controlled owner released by test coordinator");std::_Exit(99);
}else if(phase=="contend"){
 string other;JPWPersonalHash("synthetic-process-contender",other);JPWPersonalStoreContext writer;
 REQUIRE(!JPWPersonalOpen(f.key,true,other,1001,1001000,writer)&&writer.result==JPW_STORE_BUSY&&!writer.writer,"separate OS process cannot acquire live SQLite owner");
 std::vector<JPWPersonalRow>rows;REQUIRE(JPWPersonalReadPage(f.key,"ALERT",0,100,rows,f.why)&&rows.size()==1,"second process no duplicate intent");JPWPersonalClose(writer,1001,1001000);
}else if(phase=="takeover"){
 JPWPersonalHash("synthetic-process-takeover",f.token);f.clock(1016);f.capture.mono_ms=1016001;f.open();
 REQUIRE(f.context.writer&&f.episodes.size()==1&&f.episodes[0].requested_count==1,"new OS process takeover preserves deadline and old episode");f.close();
}else throw std::runtime_error("unknown owner phase");
Print("FRESH_OWNER_PASS|",phase,"|",host_asserts);
}
void recovery_phase(const string& id,const string& phase){
PersonalFixture f;JPWPersonalHash("synthetic-crash-account",f.key);f.capture.account_key=f.key;
if(phase=="seed"){
 f.open();f.observe();f.commit();int changed=0;REQUIRE(JPWPersonalPeakAccept(f.capture,"committed-old-photo",f.current,f.estimated,changed),"seed old maximum");f.commit(changed);f.close();Print("RECOVERY_SEED|PASS");return;
}
if(phase=="crash"||phase=="crash-called"){
 f.clock(2000);f.open();
 if(id=="HIS-AC16"){
  REQUIRE(DatabaseTransactionBegin(f.context.db),"crash transaction begin");auto next=f.current;next.leverage=8;next.snapshot="interrupted-new-photo";
  REQUIRE(JPWPersonalPutPeak(f.context.db,next),"crash stage actual peak and photograph");std::_Exit(99);
 }
 JPWPersonalMarkRequested(f.capture,f.episodes[0]);REQUIRE(JPWPersonalNotify(f.context,"crash-warning","INTENT",2000,2000000,"delivery unknown",f.episodes),"crash durable intention and deadline");
 if(phase=="crash-called"){
  bool error=false;string result=JPWPersonalTerminalNotify("synthetic interrupted request",error);
  REQUIRE(!error&&result.find("UNAVAILABLE")!=string::npos,"instrumented native call cannot prove human receipt");
  REQUIRE(JPWPersonalNotify(f.context,"crash-warning","CALLED",2000,2000000,"API invoked delivery unknown",f.episodes),"crash durable called stage before result");
 }
 std::_Exit(99);
}
if(phase=="recover"||phase=="recover-called"){
 JPWPersonalHash("synthetic-fresh-recovery-owner",f.token);f.clock(2020);f.open();REQUIRE(f.current.valid&&f.current.leverage==7&&f.current.snapshot=="committed-old-photo","fresh process preserves atomic old peak/photo");
 if(id=="HIS-AC18"){
  std::vector<JPWPersonalRow>rows;REQUIRE(JPWPersonalReadPage(f.key,"ALERT",0,100,rows,f.why)&&rows.size()==(phase=="recover-called"?2:1)&&rows.back().payload.rfind("INTENT|",0)==0,"fresh process missing result retains delivery uncertainty");
  if(phase=="recover-called")REQUIRE(rows[0].payload.rfind("CALLED|",0)==0,"called stage without result remains uncertain");
  REQUIRE(f.episodes.size()==1&&f.episodes[0].next_wall==2060&&!f.episodes[0].mono_ready,"fresh process reloads persisted cooldown");
  f.observe();REQUIRE(f.due.empty(),"crash early recovery no burst");f.clock(2120);f.observe();REQUIRE(f.due.size()==1,"late recovery one due only");
 }
 f.close();Print("FRESH_RECOVERY_PASS|",id,"|",host_asserts);return;
}
throw std::runtime_error("unknown recovery phase");
}

// Terminal primitives are controlled synthetic seams; NotifyDue/Persist and
// TerminalNotify are extracted unchanged from the production MQL sources.
constexpr int TERMINAL_CONNECTED=1,MQL_TESTER=1;
int host_alert_calls=0,host_sound_calls=0;bool host_sound_ok=true,host_test_mode=false,host_no_sl=true,host_identity_ok=true;
int MQLInfoInteger(int){return host_test_mode?1:0;}
long TerminalInfoInteger(int){return 1;}
void Alert(const string&){host_alert_calls++;}
bool PlaySound(const string&){host_sound_calls++;if(!host_sound_ok)host_error=123;return host_sound_ok;}
bool JPWPersonalTerminalIdentity(string& key,string& currency){key=g_ph_context;currency="USD";return host_identity_ok;}
bool JPWPersonalTerminalNoSLNow(const string&,JPWPersonalSubject&){return host_no_sl;}
void JPWPersonalControllerBridge(int){}
void JPWPersonalTerminalReset(){}

JPWPersonalCapture host_controller_capture;std::vector<JPWPersonalSubject> host_controller_subjects;bool host_controller_capture_ready=true;
bool JPWPersonalControllerExclusive(){return g_ph_exclusive_file!=INVALID_HANDLE;}
bool JPWPersonalTerminalCaptureStep(const string&,ulong,JPWPersonalCapture &capture,std::vector<JPWPersonalSubject>&subjects,bool &ready,string &reason){capture=host_controller_capture;capture.wall_seconds=TimeGMT();capture.mono_ms=GetTickCount64();capture.started_msc=capture.wall_seconds*1000;capture.finished_msc=capture.started_msc+1;subjects=host_controller_subjects;ready=host_controller_capture_ready;reason="";return true;}
bool JPWPersonalTerminalCompletionProof(JPWPersonalSubject&,string&,string&){return false;}

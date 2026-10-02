// Calls the production MQL Core bodies after syntax-only translation.
// REQUIRE expectations derive from frozen HIS acceptance, not its implementation.
void core_case(const string& id){
JPWPersonalCapture c;JPWPersonalTestCapture(c);
std::vector<JPWPersonalSubject>s(1);JPWPersonalTestSubject(s[0]);
std::vector<JPWPersonalEpisode>e;std::vector<JPWPersonalEvent>v;std::vector<int>due;
auto observe=[&](long wall){c.wall_seconds=wall;c.started_msc=wall*1000;c.finished_msc=wall*1000+1;c.mono_ms=wall*1000;return JPWPersonalReconcile(c,s,e,v,due);};
auto initial=[&](){REQUIRE(observe(1000)&&e.size()==1&&due.size()==1,"initial observed absence");JPWPersonalMarkRequested(c,e[0]);};
if(id=="HIS-AC01"){
 REQUIRE(observe(1000)&&e.size()==1&&e[0].state==JPW_PERSONAL_ACTIVE&&due.size()==1,"one new active episode and initial due");
 REQUIRE(v.size()==1&&v[0].type=="NO_SL_DETECTED","observed NO_SL event");
 JPWPersonalMarkRequested(c,e[0]);REQUIRE(e[0].requested_count==1&&e[0].next_wall==1060,"one marked request with 60s deadline");
 REQUIRE(observe(1001)&&e.size()==1&&due.empty(),"repeat capture does not duplicate episode or early warning");
}else if(id=="HIS-AC02"){
 s[0].sl=1.05;REQUIRE(observe(1000)&&e.empty()&&due.empty()&&v.empty(),"present SL no false episode or warning");
}else if(id=="HIS-AC03"){
 initial();for(long wall:{1001L,1059L})REQUIRE(observe(wall)&&due.empty(),"no repeat before 60s");
 REQUIRE(observe(1060)&&due.size()==1,"repeat exactly at 1060");JPWPersonalMarkRequested(c,e[0]);
 REQUIRE(e[0].next_wall==1120&&e[0].next_mono==1120000,"next repeat 1120");
 REQUIRE(observe(1061)&&due.empty(),"no burst at 1061");
 c.wall_seconds=2000;c.mono_ms=1119000;REQUIRE(JPWPersonalReconcile(c,s,e,v,due)&&due.empty(),"session deadline uses monotonic clock despite wall advancing");
}else if(id=="HIS-AC04"){
 initial();s[0].sl=1.05;REQUIRE(observe(1059)&&e[0].state==JPW_PERSONAL_SL_PRESENT&&due.empty(),"SL presence resolves before repeat");
 REQUIRE(e[0].resolution=="RESOLVED_SL_PRESENT"&&v.size()==1&&v[0].type=="RESOLVED_SL_PRESENT","specific observed SL resolution");
 REQUIRE(observe(1060)&&due.empty(),"resolved episode never rewarns");
}else if(id=="HIS-AC05"){
 initial();string original=e[0].episode_id;s[0].sl=1.05;REQUIRE(observe(1059),"resolve first episode");s[0].sl=0;
 REQUIRE(observe(1060)&&e.size()==2&&due.size()==1&&e[0].episode_id==original&&e[0].state==JPW_PERSONAL_SL_PRESENT,"SL removed creates new episode preserves prior");
 REQUIRE(e[1].episode_id!=original&&e[1].state==JPW_PERSONAL_ACTIVE,"new episode distinct stable subject");
}else if(id=="HIS-AC06"){
 initial();s.clear();REQUIRE(observe(1010)&&e[0].state==JPW_PERSONAL_NO_LONGER_PRESENT&&due.empty(),"complete inventory absence closes");
 REQUIRE(e[0].resolution=="NO_LONGER_PRESENT"&&v.size()==1&&v[0].type=="NO_LONGER_PRESENT","no invented stop fill or cancellation cause");
}else if(id=="HIS-AC07"){
 JPWPersonalTestSubject(s[0],JPW_PERSONAL_PENDING,"900");s[0].order_type=6;s[0].volume=.1;
 initial();string order_episode=e[0].episode_id;s[0].volume=.06;s.resize(2);JPWPersonalTestSubject(s[1],JPW_PERSONAL_POSITION,"700");s[1].volume=.04;s[1].link_id="900";
 REQUIRE(observe(1001)&&e.size()==2&&e[0].state==JPW_PERSONAL_ACTIVE&&due.size()==1,"pending remainder and new position distinct episodes");
 REQUIRE(e[0].episode_id==order_episode&&e[0].subject.volume==.06&&e[1].subject.link_id=="900","supplied proof link preserved no ID promotion");
}else if(id=="HIS-AC08"){
 initial();string raw=JPWPersonalEncodeEpisode(e[0]);c.connected=false;s[0].sl=1.05;
 REQUIRE(!observe(1060)&&due.empty()&&v.empty()&&JPWPersonalEncodeEpisode(e[0])==raw,"offline rejects facts preserves active episode");
 c.connected=true;REQUIRE(observe(1061)&&e[0].state==JPW_PERSONAL_SL_PRESENT&&due.empty(),"reconnection revalidated SL resolves");
}else if(id=="HIS-AC09"){
 initial();string raw=JPWPersonalEncodeEpisode(e[0]);JPWPersonalEpisode restored;
 REQUIRE(JPWPersonalDecodeEpisode(raw,restored)&&!restored.mono_ready,"persisted clock restores without boot-relative deadline");
 e[0]=restored;REQUIRE(observe(1030)&&due.empty()&&e[0].next_mono==1060000,"restart early restores remaining deadline");
 e[0]=restored;REQUIRE(observe(1120)&&due.size()==1,"restart late only one due warning");JPWPersonalMarkRequested(c,e[0]);
 REQUIRE(observe(1121)&&due.empty()&&e[0].next_wall==1180,"late restart no catch-up burst");
}else if(id=="HIS-AC10"){
 initial();string episode=e[0].episode_id;s[0].ticket="755";s[0].volume=.06;
 REQUIRE(observe(1001)&&e.size()==1&&e[0].episode_id==episode&&e[0].subject.id=="700"&&e[0].subject.ticket=="755"&&e[0].subject.volume==.06,"identifier stable across ticket and partial volume changes");
}else if(id=="HIS-AC12"||id=="HIS-AC13"||id=="HIS-AC14"){
 JPWPersonalPeak current{},estimated{};int changed=0;
 auto peak=[&](const string& label,const string& gross,const string& equity,int quality,bool eligible){c.gross=StringToDouble(gross);c.equity=StringToDouble(equity);c.quality=quality;c.leverage_valid=eligible;bool accepted=JPWPersonalPeakAccept(c,label,current,estimated,changed);Print("FINANCIAL_VECTOR|",id,"|",label,"|",accepted?1:0,"|",accepted?JPWPersonalNum(c.gross/c.equity):"NA","|",changed);return accepted;};
 if(id=="HIS-AC12"){
  REQUIRE(peak("first","1400","200",1,true)&&changed==1&&current.snapshot=="first","first maximum");
  REQUIRE(peak("lower","1399.9999999","200",1,true)&&changed==0&&current.snapshot=="first","lower preserves first snapshot");
  REQUIRE(peak("tie","1400","200",1,true)&&changed==0&&current.snapshot=="first","tie preserves first snapshot");
  REQUIRE(peak("higher_without_rounding","1400.0000001","200",1,true)&&changed==1&&current.snapshot=="higher_without_rounding","tiny unrounded increase updates maximum");
  REQUIRE(peak("estimated_separate","1800","200",2,true)&&changed==2&&estimated.snapshot=="estimated_separate"&&current.snapshot=="higher_without_rounding","Estimated peak stored separately");
 }else if(id=="HIS-AC13"){
  REQUIRE(peak("equity_before","1400","200",1,true)&&current.leverage==7,"baseline seven");
  REQUIRE(peak("equity_falls_no_entry","1400","175",1,true)&&current.leverage==8&&changed==1&&current.snapshot=="equity_falls_no_entry","fixed gross falling equity raises peak to eight");
 }else{
  REQUIRE(!peak("zero_equity","1400","0",0,true)&&!current.valid,"zero equity not a peak");
  REQUIRE(!peak("negative_equity","1400","-1",0,true)&&!current.valid,"negative equity not a peak");
  REQUIRE(!peak("missing_conversion","1400","200",0,false)&&!current.valid,"missing conversion not a peak");
  c.inventory_valid=false;REQUIRE(!peak("partial_inventory","1400","200",0,false)&&!current.valid,"partial inventory not a peak");c.inventory_valid=true;
  s[0].sl_readable=false;REQUIRE(observe(1000)&&e.empty()&&due.empty(),"unreadable SL never becomes observed absence");
  REQUIRE(peak("confirmed_empty","0","200",1,true)&&current.valid&&current.leverage==0,"confirmed valid empty zero");
 }
}else if(id=="HIS-AC15"){
 initial();string raw=JPWPersonalEncodeEpisode(e[0]);c.account_key="synthetic-account-B";
 REQUIRE(!observe(1001)&&JPWPersonalEncodeEpisode(e[0])==raw,"old active episode cannot mutate different context");
 std::vector<JPWPersonalEpisode>other;REQUIRE(JPWPersonalReconcile(c,s,other,v,due)&&other.size()==1&&other[0].account_key!=e[0].account_key,"same ticket identifier creates separate account context");
}else if(id=="HIS-AC16"){
 initial();string raw=JPWPersonalEncodeEpisode(e[0]);c.stable=false;s.clear();
 REQUIRE(!observe(1010)&&JPWPersonalEncodeEpisode(e[0])==raw&&due.empty(),"unstable capture cannot close subject");
 JPWPersonalPeak current{},estimated{};int changed=0;REQUIRE(!JPWPersonalPeakAccept(c,"race",current,estimated,changed)&&!current.valid&&!estimated.valid,"unstable capture cannot publish peak or photo");
}else{
 Print("CORE_NOT_RUN|",id);return;
}
Print("CORE_CASE_PASS|",id,"|",host_asserts);
}

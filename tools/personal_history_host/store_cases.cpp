// Actual production Store calls, backed by real sqlite3 built-in shims.
struct PersonalFixture {
 JPWPersonalCapture capture{};JPWPersonalStoreContext context{};
 std::vector<JPWPersonalSubject>subjects;std::vector<JPWPersonalEpisode>episodes;
 std::vector<JPWPersonalEvent>events;std::vector<int>due;JPWPersonalPeak current{},estimated{};
 string key,token,why;
 PersonalFixture(){JPWPersonalTestCapture(capture);JPWPersonalHash("synthetic-account-A",key);JPWPersonalHash("synthetic-owner-A",token);capture.account_key=key;subjects.resize(1);JPWPersonalTestSubject(subjects[0]);}
 void open(){REQUIRE(JPWPersonalOpen(key,true,token,capture.wall_seconds,capture.mono_ms,context),"actual SQLite writer open");REQUIRE(JPWPersonalLoad(context,episodes,current,estimated),"actual SQLite initial/recovery load");}
 void clock(long wall){capture.wall_seconds=wall;capture.started_msc=wall*1000;capture.finished_msc=wall*1000+1;capture.mono_ms=wall*1000;}
 void observe(){REQUIRE(JPWPersonalReconcile(capture,subjects,episodes,events,due),"actual Core observation for Store");}
 void commit(int changed=0){REQUIRE(JPWPersonalCommit(context,capture,episodes,events,current,estimated,changed),"actual transactional history commit");}
 void initial(){open();observe();commit();REQUIRE(episodes.size()==1&&due.size()==1,"first episode stored");JPWPersonalMarkRequested(capture,episodes[0]);REQUIRE(JPWPersonalNotify(context,"synthetic-warning-1","INTENT",capture.wall_seconds,capture.mono_ms,"request only, delivery unknown",episodes),"intent and repeat deadline persisted atomically");}
 void close(){JPWPersonalClose(context,capture.wall_seconds,capture.mono_ms);}
};
void store_projection_state_regressions(){
 for(int variant=0;variant<8;variant++){
  PersonalFixture f;JPWPersonalHash("synthetic-state-projection-"+IntegerToString(variant),f.key);f.capture.account_key=f.key;f.initial();
  if(variant==4||variant==5){f.clock(1001);if(variant==4)f.subjects[0].sl=1.05;else f.subjects.clear();f.observe();f.commit();}
  long count=scalar(f.context.db,"SELECT sequence FROM ph_meta");int bad=variant==0?0:variant==1?2:variant==2?3:variant==3?99:1;
  string bad_text=variant==6?"'1junk'":variant==7?"1.5":IntegerToString(bad);
  REQUIRE(DatabaseExecute(f.context.db,"UPDATE ph_episodes SET state="+bad_text),"synthetic state-only projection corruption");f.close();JPWPersonalStoreContext refused;
  REQUIRE(!JPWPersonalOpen(f.key,true,f.token,1016,1016001,refused)&&refused.result==JPW_STORE_CORRUPT&&refused.db==INVALID_HANDLE,"writer startup refuses state divergent from immutable episode witness");
  JPWPersonalStoreContext read;REQUIRE(!JPWPersonalOpen(f.key,false,"",0,0,read)&&read.result==JPW_STORE_CORRUPT,"reader also cannot present corrupted state projection as valid summary");
  int db=DatabaseOpen(JPWPersonalPath(f.key),DATABASE_OPEN_READONLY);REQUIRE(db!=INVALID_HANDLE&&scalar(db,"SELECT sequence FROM ph_meta")==count,"state corruption refusal preserves sequence without silent repair");
  int q=DatabasePrepare(db,"SELECT quote(state) FROM ph_episodes");string stored;REQUIRE(q!=INVALID_HANDLE&&DatabaseRead(q)&&DatabaseColumnText(q,0,stored)&&stored==bad_text,"state value remains exactly corrupted, never silently repaired");DatabaseFinalize(q);DatabaseClose(db);
 }
 PersonalFixture nullcase;JPWPersonalHash("synthetic-state-null",nullcase.key);nullcase.capture.account_key=nullcase.key;nullcase.initial();long count=scalar(nullcase.context.db,"SELECT sequence FROM ph_meta");
 REQUIRE(!DatabaseExecute(nullcase.context.db,"UPDATE ph_episodes SET state=NULL"),"schema NOT NULL rejects state corruption before it exists");
 REQUIRE(scalar(nullcase.context.db,"SELECT state FROM ph_episodes")==1&&scalar(nullcase.context.db,"SELECT sequence FROM ph_meta")==count,"NULL rejected preserves prior active state and journal");nullcase.close();
 JPWPersonalSummary summary;REQUIRE(JPWPersonalReadSummary(nullcase.key,summary)&&summary.active_episodes==1,"rejected NULL attempt cannot hide valid active episode");
}
void store_case(const string& id){
int start=host_asserts;PersonalFixture f;
if(id=="HIS-AC01"||id=="HIS-AC03"||id=="HIS-AC04"||id=="HIS-AC05"||id=="HIS-AC06"||id=="HIS-AC07"||id=="HIS-AC08"||id=="HIS-AC09"||id=="HIS-AC10"){
 if(id=="HIS-AC07"){JPWPersonalTestSubject(f.subjects[0],JPW_PERSONAL_PENDING,"900");f.subjects[0].order_type=6;}
 f.initial();
 if(id=="HIS-AC03"){for(long wall:{1001L,1059L}){f.clock(wall);f.observe();REQUIRE(f.due.empty(),"stored episode no early repeat");f.commit();}f.clock(1060);f.observe();REQUIRE(f.due.size()==1,"stored episode due at sixty seconds");JPWPersonalMarkRequested(f.capture,f.episodes[0]);REQUIRE(JPWPersonalNotify(f.context,"synthetic-warning-2","INTENT",1060,1060000,"second request",f.episodes),"second intent persisted");}
 if(id=="HIS-AC04"||id=="HIS-AC05"){f.clock(1059);f.subjects[0].sl=1.05;f.observe();f.commit();REQUIRE(f.episodes[0].state==JPW_PERSONAL_SL_PRESENT&&f.due.empty(),"resolved episode persisted");if(id=="HIS-AC05"){f.clock(1060);f.subjects[0].sl=0;f.observe();f.commit();REQUIRE(f.episodes.size()==2&&f.due.size()==1,"second episode saved without removing first");}}
 if(id=="HIS-AC06"){f.clock(1010);f.subjects.clear();f.observe();f.commit();REQUIRE(f.episodes[0].resolution=="NO_LONGER_PRESENT","generic complete absence persisted");}
 if(id=="HIS-AC07"){f.clock(1001);f.subjects.resize(2);f.subjects[0].volume=.06;JPWPersonalTestSubject(f.subjects[1],JPW_PERSONAL_POSITION,"700");f.subjects[1].volume=.04;f.subjects[1].link_id="900";f.observe();f.commit();REQUIRE(f.episodes.size()==2,"position and pending both stored separately");}
 if(id=="HIS-AC08"){f.clock(1060);f.capture.connected=false;auto rows=scalar(f.context.db,"SELECT COUNT(*) FROM ph_rows WHERE category='EPISODE'");REQUIRE(!JPWPersonalReconcile(f.capture,f.subjects,f.episodes,f.events,f.due),"offline no domain facts");REQUIRE(JPWPersonalCoverage(f.context,"GAP",1060,1060000,"offline synthetic"),"coverage gap recorded separately");REQUIRE(scalar(f.context.db,"SELECT COUNT(*) FROM ph_rows WHERE category='EPISODE'")==rows,"offline no new episode row");f.capture.connected=true;f.clock(1061);f.subjects[0].sl=1.05;f.observe();f.commit();REQUIRE(JPWPersonalCoverage(f.context,"RESUMED",1061,1061000,"revalidated"),"coverage resumed");}
 if(id=="HIS-AC09"){f.close();f.clock(1030);f.open();REQUIRE(f.episodes.size()==1&&!f.episodes[0].mono_ready&&f.episodes[0].next_wall==1060,"SQLite restored immutable deadline no boot clock");f.observe();REQUIRE(f.due.empty(),"reloaded early no burst");f.close();f.clock(1120);f.open();f.observe();REQUIRE(f.due.size()==1,"reloaded late only one repeat due");JPWPersonalMarkRequested(f.capture,f.episodes[0]);REQUIRE(JPWPersonalNotify(f.context,"synthetic-warning-restart","INTENT",1120,1120000,"restart one request",f.episodes),"restart deadline persisted");}
 if(id=="HIS-AC10"){f.clock(1001);f.subjects[0].ticket="755";f.subjects[0].volume=.06;f.observe();f.commit();}
 JPWPersonalSummary summary;REQUIRE(JPWPersonalReadSummary(f.key,summary)&&summary.result==JPW_STORE_VALID,"read summary from actual SQLite");
 REQUIRE(summary.total_episodes==(id=="HIS-AC05"||id=="HIS-AC07"?2:1),"old episodes retained in summary");
 std::vector<JPWPersonalEpisode>loaded;JPWPersonalPeak current{},estimated{};REQUIRE(JPWPersonalLoad(f.context,loaded,current,estimated),"load saved active projection");
 if(id=="HIS-AC04"||id=="HIS-AC06"||id=="HIS-AC08")REQUIRE(loaded.empty(),"resolved projection never reloads as active");
 if(id=="HIS-AC10")REQUIRE(loaded.size()==1&&loaded[0].subject.id=="700"&&loaded[0].subject.ticket=="755"&&loaded[0].subject.volume==.06,"updated ticket/volume reload preserves identifier");
 if(id=="HIS-AC08")REQUIRE(summary.gaps==1,"gap count present not continuous coverage claim");
}else if(id=="HIS-AC02"){
 f.open();f.subjects[0].sl=1.05;f.observe();f.commit();REQUIRE(scalar(f.context.db,"SELECT COUNT(*) FROM ph_episodes")==0&&scalar(f.context.db,"SELECT COUNT(*) FROM ph_rows WHERE category='ALERT'")==0,"positive SL saves no false episode or intent");
}else if(id=="HIS-AC11"){
 f.initial();JPWPersonalStoreContext second;string token;JPWPersonalHash("synthetic-owner-B",token);
 REQUIRE(!JPWPersonalOpen(f.key,true,token,1001,1001000,second)&&second.result==JPW_STORE_BUSY&&!second.writer,"second SQLite writer rejected before lease expiry");
 JPWPersonalClose(second,1001,1001000);REQUIRE(JPWPersonalOpen(f.key,true,token,1016,1016001,second)&&second.writer,"takeover after verifiable monotonic expiry");
 REQUIRE(!JPWPersonalKeepAlive(f.context,1017,1017000)&&!f.context.writer,"old owner fenced after takeover");
 REQUIRE(!JPWPersonalNotify(f.context,"old-owner","INTENT",1017,1017000,"must not write",f.episodes),"old owner cannot duplicate warning");
 f.close();REQUIRE(JPWPersonalKeepAlive(second,1018,1018000),"old close cannot release new owner");JPWPersonalClose(second,1018,1018000);
}else if(id=="HIS-AC12"||id=="HIS-AC13"){
 f.open();f.observe();int changed=0;REQUIRE(JPWPersonalPeakAccept(f.capture,"first-photo",f.current,f.estimated,changed)&&changed==1,"peak seven accepted");f.commit(changed);
 if(id=="HIS-AC12"){f.clock(1001);f.capture.gross=1399.9999999;REQUIRE(JPWPersonalPeakAccept(f.capture,"lower-photo",f.current,f.estimated,changed)&&changed==0,"lower no peak transaction");f.commit(changed);f.clock(1002);f.capture.gross=1400;REQUIRE(JPWPersonalPeakAccept(f.capture,"tie-photo",f.current,f.estimated,changed)&&changed==0,"tie retains first immutable photo");f.commit(changed);JPWPersonalSummary tie;REQUIRE(JPWPersonalReadSummary(f.key,tie)&&tie.current.snapshot=="first-photo"&&scalar(f.context.db,"SELECT COUNT(*) FROM ph_rows WHERE category='PEAK'")==1,"tie leaves one stored peak witness");f.capture.gross=1400.0000001;f.clock(1003);REQUIRE(JPWPersonalPeakAccept(f.capture,"higher-photo",f.current,f.estimated,changed)&&changed==1,"strict unrounded increase");f.commit(changed);f.capture.gross=1800;f.capture.quality=2;f.clock(1004);REQUIRE(JPWPersonalPeakAccept(f.capture,"estimated-photo",f.current,f.estimated,changed)&&changed==2,"separate Estimated peak");f.commit(changed);}
 else{f.capture.equity=175;f.clock(1001);REQUIRE(JPWPersonalPeakAccept(f.capture,"equity-photo",f.current,f.estimated,changed)&&changed==1,"equity-only update");f.commit(changed);}
 JPWPersonalSummary summary;REQUIRE(JPWPersonalReadSummary(f.key,summary)&&summary.current.valid&&summary.current.leverage==f.current.leverage&&summary.current.snapshot==f.current.snapshot,"peak and photo same persisted generation");
 if(id=="HIS-AC12")REQUIRE(summary.estimated.valid&&summary.estimated.leverage==9&&summary.current.leverage<9,"Estimated remains separate in SQLite");
 else REQUIRE(summary.current.leverage==8&&summary.current.snapshot=="equity-photo","SQLite maximum eight linked to photo");
}else if(id=="HIS-AC14"){
 f.open();f.subjects[0].sl_readable=false;f.observe();f.commit();REQUIRE(scalar(f.context.db,"SELECT COUNT(*) FROM ph_episodes")==0,"unreadable SL saves no no-stop fact");
}else if(id=="HIS-AC15"){
 f.initial();string keyA=f.key;JPWPersonalStoreContext other;string keyB;JPWPersonalHash("synthetic-account-B-other-server-USC-installation",keyB);
 REQUIRE(JPWPersonalOpen(keyB,true,f.token,1000,1000000,other),"separate context actual SQLite");auto capture=f.capture;capture.account_key=keyB;
 REQUIRE(!JPWPersonalCommit(other,capture,f.episodes,f.events,f.current,f.estimated,0),"old account episodes rejected by other store");
 REQUIRE(!JPWPersonalCommit(f.context,capture,f.episodes,f.events,f.current,f.estimated,0),"old callback cannot write current-account capture to old store");
 REQUIRE(scalar(other.db,"SELECT COUNT(*) FROM ph_episodes")==0&&scalar(f.context.db,"SELECT COUNT(*) FROM ph_episodes")==1,"account context stores remain isolated");
 JPWPersonalClose(other,1000,1000000);std::vector<string>keys;REQUIRE(JPWPersonalListAccounts(keys)&&keys.size()==2,"historical context enumeration only local stores");
 JPWPersonalSummary summary;REQUIRE(JPWPersonalReadSummary(keyB,summary)&&f.context.account_key==keyA,"history query does not change writer operational context");
}else if(id=="HIS-AC16"){
 f.initial();int changed=0;REQUIRE(JPWPersonalPeakAccept(f.capture,"old-photo",f.current,f.estimated,changed),"initial consistent peak");f.commit(changed);
 auto count=scalar(f.context.db,"SELECT COUNT(*) FROM ph_rows");f.capture.stable=false;f.capture.equity=175;
 REQUIRE(!JPWPersonalPeakAccept(f.capture,"unstable-photo",f.current,f.estimated,changed)&&changed==0,"unstable sample rejected before commit");
 REQUIRE(scalar(f.context.db,"SELECT COUNT(*) FROM ph_rows")==count,"rejected unstable capture adds no peak/photo rows");
 // A failed transaction after a new peak witness must roll back both rows.
 REQUIRE(DatabaseTransactionBegin(f.context.db),"begin deliberate incomplete peak transaction");auto next=f.current;next.snapshot="uncommitted-photo";next.leverage=8;
 REQUIRE(JPWPersonalPutPeak(f.context.db,next),"stage real peak/photo projection");REQUIRE(DatabaseTransactionRollback(f.context.db),"rollback incomplete peak transaction");
 JPWPersonalSummary summary;REQUIRE(JPWPersonalReadSummary(f.key,summary)&&summary.current.leverage==7&&summary.current.snapshot=="old-photo","rollback never separates maximum and photograph");
}else if(id=="HIS-AC17"){
 store_projection_state_regressions();
 f.initial();long original=scalar(f.context.db,"SELECT sequence FROM ph_meta");
 int blocker=DatabaseOpen(JPWPersonalPath(f.key),DATABASE_OPEN_READWRITE);REQUIRE(blocker!=INVALID_HANDLE&&DatabaseExecute(blocker,"BEGIN IMMEDIATE"),"real SQLite competing write lock");
 f.clock(1001);REQUIRE(!JPWPersonalCommit(f.context,f.capture,f.episodes,f.events,f.current,f.estimated,0),"BUSY transaction refused");
 REQUIRE(DatabaseTransactionRollback(blocker),"release competing write lock");DatabaseClose(blocker);REQUIRE(scalar(f.context.db,"SELECT sequence FROM ph_meta")==original,"BUSY preserves prior journal");
 REQUIRE(DatabaseExecute(f.context.db,"PRAGMA max_page_count=12"),"set physical SQLite page budget");
 REQUIRE(!JPWPersonalCoverage(f.context,"GAP",1002,1002000,string(200000,'x')),"SQLITE_FULL real write failure reported");
 REQUIRE(scalar(f.context.db,"SELECT sequence FROM ph_meta")==original,"SQLITE_FULL rolls back journal and sequence");
 REQUIRE(DatabaseExecute(f.context.db,"PRAGMA max_page_count=1000000"),"restore synthetic page budget");
 REQUIRE(DatabaseExecute(f.context.db,"UPDATE ph_episodes SET digest='broken'"),"corrupt synthetic latest witness");f.close();JPWPersonalStoreContext refused;
 REQUIRE(!JPWPersonalOpen(f.key,true,f.token,1010,1010000,refused)&&refused.result==JPW_STORE_CORRUPT,"corrupt store refused without reset");
 REQUIRE(FileIsExist(JPWPersonalPath(f.key)),"corrupt database preserved on disk");
 // A separate schema-future context must be refused, never migrated/reset.
 string future;JPWPersonalHash("synthetic-future",future);REQUIRE(JPWPersonalOpen(future,true,f.token,1000,1000000,refused),"future schema fixture open");
 REQUIRE(DatabaseExecute(refused.db,"UPDATE ph_meta SET schema_version=999"),"synthetic future schema stored");JPWPersonalClose(refused,1000,1000000);
 REQUIRE(!JPWPersonalOpen(future,true,f.token,1010,1010000,refused)&&refused.result==JPW_STORE_INCOMPATIBLE,"future schema refused preserved");
}else if(id=="HIS-AC18"){
 f.initial();std::vector<JPWPersonalRow>rows;REQUIRE(JPWPersonalReadPage(f.key,"ALERT",0,100,rows,f.why)&&rows.size()==1&&rows[0].payload.rfind("INTENT|",0)==0,"persisted intent alone cannot prove called/displayed/heard");
 REQUIRE(JPWPersonalNotify(f.context,"synthetic-warning-1","CALLED",1000,1000000,"API invoked, delivery unknown",f.episodes),"actual immutable called stage");
 REQUIRE(JPWPersonalReadPage(f.key,"ALERT",0,100,rows,f.why)&&rows.size()==2,"called without result remains separately auditable");
 REQUIRE(JPWPersonalNotify(f.context,"synthetic-warning-1","RESULT",1000,1000000,"API return only, human receipt unverified",f.episodes),"actual immutable result stage");
 REQUIRE(JPWPersonalReadPage(f.key,"ALERT",0,100,rows,f.why)&&rows.size()==3,"intent called result retain all audit rows");
 f.close();f.clock(1120);f.open();f.observe();REQUIRE(f.due.size()==1,"recovered stage history does not replay elapsed warnings");
}else{Print("SQLITE_NOT_RUN|",id);return;}
if(f.context.db!=INVALID_HANDLE)f.close();Print("SQLITE_CASE_PASS|",id,"|",host_asserts-start);
}

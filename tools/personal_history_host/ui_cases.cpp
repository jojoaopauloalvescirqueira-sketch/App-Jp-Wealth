void host_collect_ui_drain(){bool forbidden=host_forbid_io;host_forbid_io=false;for(int n=0;n<1000000;n++){JPWPersonalCollectUI();if(!g_personal_job_active&&!g_personal_read_requested&&!g_personal_export_requested){host_forbid_io=forbidden;return;}}throw std::runtime_error("UI drain did not terminate");}
void ui_case(const string& id){
if(id!="HIS-AC20"){Print("UI_NOT_RUN|",id);return;}int start=host_asserts;
PersonalFixture a,b;JPWPersonalHash("ui-account-A",a.key);a.capture.account_key=a.key;a.initial();a.close();
JPWPersonalHash("ui-account-B",b.key);b.capture.account_key=b.key;b.initial();
int q=DatabasePrepare(b.context.db,"INSERT INTO ph_rows VALUES(?1,'ALERT','ui-warning',1000,'INTENT|-',?2)");string digest;JPWPersonalHash("INTENT|-",digest);
REQUIRE(DatabaseTransactionBegin(b.context.db),"UI fixture bulk begin");for(long seq=scalar(b.context.db,"SELECT sequence FROM ph_meta")+1;seq<=800;seq++){sqlite3_reset(host_statements.at(q));REQUIRE(DatabaseBind(q,0,seq)&&DatabaseBind(q,1,digest)&&JPWPersonalDone(q),"UI actual fixture row");}DatabaseFinalize(q);REQUIRE(DatabaseExecute(b.context.db,"UPDATE ph_meta SET sequence=800")&&DatabaseTransactionCommit(b.context.db),"UI bulk committed");b.close();
host_forbid_io=true;g_diagnostic_context=a.key;g_personal_operating_key=a.key;g_personal_scope=b.key;
g_personal_accounts={a.key,b.key};g_personal_account_index=1;
g_personal_available=true;g_personal_read_requested=false;g_personal_category="ALERT";g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY;
g_personal_rows.resize(8);for(int i=0;i<8;i++){g_personal_rows[i].sequence=800-i;g_personal_rows[i].category="ALERT";g_personal_rows[i].wall=1000;g_personal_rows[i].payload="INTENT|";}

int pref=g_cockpit_prefs;string operating=g_personal_operating_key;
// A live audit is not a completed failure, and must never expose stale rows.
g_personal_available=false;g_personal_job_active=true;host_labels.clear();
JPWPersonalRenderBody(0,0,300,300,330);
bool auditing=false,failed=false;for(auto& line:host_labels){auditing|=line.second.find("Auditando")!=string::npos;failed|=line.second.find("Consulta indisponível")!=string::npos;}
REQUIRE(auditing&&!failed&&g_personal_button_count==0,"active audit presented distinctly without stale rows");
g_personal_job_active=false;g_personal_available=true;host_labels.clear();

JPWPersonalRenderBody(0,0,300,170,200);
REQUIRE(g_personal_button_count>0&&g_personal_button_count<8,"renderer exposes subset fitting instrumented measured layout");
long last_visible=g_personal_button_seq[g_personal_button_count-1];REQUIRE(last_visible>g_personal_rows.back().sequence,"last visible differs from loaded tail fixture");
g_personal_read_requested=false;JPWPersonalHistoryMove(1);REQUIRE(g_personal_before==last_visible&&g_personal_cursor_page==1&&g_personal_read_requested,"next page cursor follows visible tail no hidden skip");
JPWPersonalHistoryMove(-1);REQUIRE(g_personal_before==0&&g_personal_cursor_page==0,"previous page restores saved cursor");
REQUIRE(g_personal_read_requested&&!g_personal_available&&g_personal_rows.empty(),"new query invalidates old rows while pending");
REQUIRE(!JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_ROW_FIRST)),"pending read refuses obsolete row action");
host_collect_ui_drain();REQUIRE(g_personal_available&&!g_personal_read_requested&&g_personal_rows.size()==8,"real coordinator completes exact previous-page read");
JPWPersonalRenderBody(0,0,300,170,200);REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_ROW_FIRST))&&g_raiz_tab==JPW_ROUTE_PERSONAL_DETAIL&&g_personal_detail_seq==800,"real row action opens selected detail generation");
host_collect_ui_drain();REQUIRE(g_personal_available&&!g_personal_read_requested&&g_personal_detail.sequence==800,"real coordinator completes selected detail before projection");g_personal_detail.digest=string(64,'a');std::vector<string>lines;JPWPersonalDetailLines(300,lines);bool receipt=false;
for(auto& line:lines)if(line.find("não comprova")!=string::npos)receipt=true;REQUIRE(receipt,"detail states requested calls cannot prove human delivery");
g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY;JPWPersonalRenderBody(0,0,300,170,200);
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_ACCOUNT))&&g_personal_scope==b.key&&g_personal_picker==1,"account opener keeps selection pending explicit choice");
JPWPersonalRenderBody(0,0,300,300,330);
REQUIRE(host_buttons[JPWActionObject(JPW_ACTION_HISTORY_CHOICE_FIRST)].find(a.key)!=string::npos,"account choice exposes catalog key without fabricated identity");
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_CHOICE_FIRST))&&g_personal_scope==a.key&&g_personal_operating_key==operating&&g_personal_read_requested,"explicit historical choice requests read never switches operating context");
// Cancelling an account menu keeps the exact selected query, page and snapshot.
g_raiz_tab=JPW_ROUTE_PERSONAL_EXPORT;host_buttons[JPWActionObject(JPW_ACTION_PRIMARY)]="Cancelar seleção";
JPWPersonalRenderBody(0,0,300,300,330);g_cockpit_page=3;long request_before_cancel=g_personal_request_id;
JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_ACCOUNT));
REQUIRE(g_personal_picker==1,"export account picker opens without queueing export");
JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_PRIMARY));
REQUIRE(g_personal_picker==0&&g_cockpit_page==3&&g_personal_request_id==request_before_cancel&&g_personal_scope==a.key&&g_personal_export_requested==0,"cancel selection preserves query page snapshot and export queue");
// Seven category choices preserve keys and operating account; no read/IO on menu open.
g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY;host_buttons[JPWActionObject(JPW_ACTION_PRIMARY)]="Escolher seção";
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_PRIMARY))&&g_personal_picker==2,"explicit category picker opens");
JPWPersonalRenderBody(0,0,300,500,530);REQUIRE(g_personal_choice_count==7,"all seven category choices available");
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_CHOICE_FIRST+5))&&g_personal_category=="COVERAGE"&&g_personal_scope==a.key&&g_personal_operating_key==operating,"explicit coverage choice preserves catalog account and canonical key");
g_personal_available=true; // synthetic successful asynchronous read of selected A
g_raiz_tab=JPW_ROUTE_PERSONAL_EXPORT;host_buttons[JPWActionObject(JPW_ACTION_PRIMARY)]="CSV";g_personal_export_requested=0;
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_PRIMARY))&&g_personal_export_requested==1,"export action queues only CSV IO no writing during click");
REQUIRE(g_personal_export_scope==a.key,"queued CSV captures consulted account A at gesture");
// Frozen HIS20 requires explicit selected account, not mutable queue retargeting.
// The earlier author expectation that a second click replaced the first queue
// was test-specific and is superseded by preservation of the first intent.
g_personal_scope=b.key;host_buttons[JPWActionObject(JPW_ACTION_SECONDARY)]="Backup";
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_SECONDARY))&&g_personal_export_requested==1&&g_personal_export_scope==a.key,"second click cannot replace pending type or account after browsing B");
g_personal_read_requested=false;host_collect_ui_drain();
REQUIRE(g_personal_export_job.account_key==a.key&&!g_personal_export_job.backup&&g_personal_export_job.result==JPW_STORE_VALID,"actual coordinator body exports original A CSV after user browses B");
REQUIRE(g_diagnostic_context==operating&&g_personal_scope==b.key&&g_personal_export_requested==0,"queued historical export does not switch operating account");
g_personal_available=true;g_raiz_tab=JPW_ROUTE_PERSONAL_EXPORT;host_buttons[JPWActionObject(JPW_ACTION_SECONDARY)]="Backup";
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_SECONDARY))&&g_personal_export_requested==2&&g_personal_export_scope==b.key,"after processing new gesture captures B backup independently");
g_personal_read_requested=false;host_collect_ui_drain();REQUIRE(g_personal_export_job.account_key==b.key&&g_personal_export_job.backup&&g_personal_export_job.result==JPW_STORE_VALID,"second processed intent retains B backup");
JPWPersonalInvalidateContext();REQUIRE(!g_personal_available&&g_personal_operating_key.empty()&&g_personal_rows.empty()&&g_personal_live_count==-1&&g_personal_detail_seq==0,"actual invalidation removes old readview and live facts");
REQUIRE(JPWPersonalScopeLabel().find("em confirmação")!=string::npos,"no operating identity cannot be labelled current account");
g_personal_operating_key=operating;
REQUIRE(g_cockpit_prefs==pref,"history navigation and export do not change existing visual prefs");
host_forbid_io=false;int corrupt=DatabaseOpen(JPWPersonalPath(b.key),DATABASE_OPEN_READWRITE);REQUIRE(DatabaseExecute(corrupt,"UPDATE ph_rows SET digest='broken' WHERE sequence=1"),"UI real corruption");DatabaseClose(corrupt);host_forbid_io=true;g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY;JPWPersonalRequestRead();host_collect_ui_drain();REQUIRE(!g_personal_available&&!g_personal_read_requested,"real coordinator refuses the synthetic corrupted read");JPWPersonalRenderBody(0,0,300,170,200);
bool unavailable=false;for(auto& line:host_labels){if(line.second.find("indisponível")!=string::npos)unavailable=true;}
REQUIRE(unavailable&&g_personal_button_count==0,"unavailable history no normal financial rows");
g_personal_scope=b.key;REQUIRE(JPWPersonalScopeLabel().find("histórica")!=string::npos,"historical query labelled explicitly");
host_forbid_io=false;Print("UI_CASE_PASS|",id,"|",host_asserts-start);
}

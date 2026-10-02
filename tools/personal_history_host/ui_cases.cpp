void ui_case(const string& id){
if(id!="HIS-AC20"){Print("UI_NOT_RUN|",id);return;}int start=host_asserts;
host_forbid_io=true;g_personal_operating_key="synthetic-account-A";g_personal_scope="synthetic-account-B";
g_personal_accounts={"synthetic-account-A","synthetic-account-B"};g_personal_account_index=1;
g_personal_available=true;g_personal_category="EPISODE";g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY;
g_personal_rows.resize(8);for(int i=0;i<8;i++){g_personal_rows[i].sequence=800-i;g_personal_rows[i].category="ALERT";g_personal_rows[i].wall=1000;g_personal_rows[i].payload="INTENT|";}
int pref=g_cockpit_prefs;string operating=g_personal_operating_key;
JPWPersonalRenderBody(0,0,300,170,200);
REQUIRE(g_personal_button_count>0&&g_personal_button_count<8,"renderer exposes subset fitting instrumented measured layout");
long last_visible=g_personal_button_seq[g_personal_button_count-1];REQUIRE(last_visible>g_personal_rows.back().sequence,"last visible differs from loaded tail fixture");
g_personal_read_requested=false;JPWPersonalHistoryMove(1);REQUIRE(g_personal_before==last_visible&&g_personal_cursor_page==1&&g_personal_read_requested,"next page cursor follows visible tail no hidden skip");
JPWPersonalHistoryMove(-1);REQUIRE(g_personal_before==0&&g_personal_cursor_page==0,"previous page restores saved cursor");
JPWPersonalRenderBody(0,0,300,170,200);REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_ROW_FIRST))&&g_raiz_tab==JPW_ROUTE_PERSONAL_DETAIL&&g_personal_detail_seq==800,"real row action opens selected detail generation");
g_personal_detail=g_personal_rows[0];g_personal_detail.digest=string(64,'a');std::vector<string>lines;JPWPersonalDetailLines(300,lines);bool receipt=false;
for(auto& line:lines)if(line.find("não comprova")!=string::npos)receipt=true;REQUIRE(receipt,"detail states requested calls cannot prove human delivery");
g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY;JPWPersonalRenderBody(0,0,300,170,200);REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_HISTORY_ACCOUNT))&&g_personal_scope=="synthetic-account-A"&&g_personal_operating_key==operating&&g_personal_read_requested,"historical selector requests read never switches operating context");
g_personal_available=true; // synthetic successful asynchronous read of selected A
g_raiz_tab=JPW_ROUTE_PERSONAL_EXPORT;host_buttons[JPWActionObject(JPW_ACTION_PRIMARY)]="CSV";g_personal_export_requested=0;
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_PRIMARY))&&g_personal_export_requested==1,"export action queues only CSV IO no writing during click");
REQUIRE(g_personal_export_scope=="synthetic-account-A","queued CSV captures consulted account A at gesture");
// Frozen HIS20 requires explicit selected account, not mutable queue retargeting.
// The earlier author expectation that a second click replaced the first queue
// was test-specific and is superseded by preservation of the first intent.
g_personal_scope="synthetic-account-B";host_buttons[JPWActionObject(JPW_ACTION_SECONDARY)]="Backup";
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_SECONDARY))&&g_personal_export_requested==1&&g_personal_export_scope=="synthetic-account-A","second click cannot replace pending type or account after browsing B");
g_personal_read_requested=false;host_ui_export_calls=0;JPWPersonalCollectUI();
REQUIRE(host_ui_export_calls==1&&host_ui_export_key=="synthetic-account-A"&&!host_ui_export_backup,"actual coordinator body exports original A CSV after user browses B");
REQUIRE(g_diagnostic_context==operating&&g_personal_scope=="synthetic-account-B"&&g_personal_export_requested==0,"queued historical export does not switch operating account");
g_personal_available=true;g_raiz_tab=JPW_ROUTE_PERSONAL_EXPORT;host_buttons[JPWActionObject(JPW_ACTION_SECONDARY)]="Backup";
REQUIRE(JPWPersonalHandleClick(JPWActionObject(JPW_ACTION_SECONDARY))&&g_personal_export_requested==2&&g_personal_export_scope=="synthetic-account-B","after processing new gesture captures B backup independently");
g_personal_read_requested=false;JPWPersonalCollectUI();REQUIRE(host_ui_export_calls==2&&host_ui_export_key=="synthetic-account-B"&&host_ui_export_backup,"second processed intent retains B backup");
JPWPersonalInvalidateContext();REQUIRE(!g_personal_available&&g_personal_operating_key.empty()&&g_personal_rows.empty()&&g_personal_live_count==-1&&g_personal_detail_seq==0,"actual invalidation removes old readview and live facts");
REQUIRE(JPWPersonalScopeLabel().find("em confirmação")!=string::npos,"no operating identity cannot be labelled current account");
g_personal_operating_key=operating;
REQUIRE(g_cockpit_prefs==pref,"history navigation and export do not change existing visual prefs");
g_personal_available=false;g_personal_reason="synthetic corruption preserved";g_raiz_tab=JPW_ROUTE_PERSONAL_HISTORY;JPWPersonalRenderBody(0,0,300,170,200);
bool unavailable=false,historical=false;for(auto& line:host_labels){if(line.second.find("indisponível")!=string::npos)unavailable=true;if(line.second.find("histórica")!=string::npos)historical=true;}
REQUIRE(unavailable&&g_personal_button_count==0,"unavailable history no normal financial rows");
g_personal_scope="synthetic-account-B";REQUIRE(JPWPersonalScopeLabel().find("histórica")!=string::npos,"historical query labelled explicitly");
host_forbid_io=false;Print("UI_CASE_PASS|",id,"|",host_asserts-start);
}

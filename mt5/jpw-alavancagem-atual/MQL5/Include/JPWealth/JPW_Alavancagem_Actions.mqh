#ifndef JPW_ALAVANCAGEM_ACTIONS_MQH
#define JPW_ALAVANCAGEM_ACTIONS_MQH
// Indicator runtime component; included after its instance state.
#include <JPWealth/JPW_UI_Focus.mqh>

void JPWCockpitLoadPrefs()
  {
   JPWCockpitDefault(g_cockpit_prefs,(int)InpCorner);
   g_cockpit_pref_invalid=false; g_cockpit_pref_notice="";
   const string object=(ObjectFind(0,JPW_COCKPIT_PREF_OBJECT)>=0 ?
                        JPW_COCKPIT_PREF_OBJECT : JPW_COCKPIT_PREF_LEGACY_OBJECT);
   if(ObjectFind(0,object)<0) return;
   JPWCockpitPrefs stored;
   if(ObjectGetInteger(0,object,OBJPROP_TYPE)!=OBJ_LABEL)
     {
      g_cockpit_pref_invalid=true;
      g_cockpit_pref_notice="Nome da preferência ocupado por outro tipo de objeto; remova-o manualmente para restaurar.";
      return;
     }
   if(!JPWCockpitDecode(ObjectGetString(0,object,OBJPROP_TEXT),stored))
     {
      g_cockpit_pref_invalid=true;
      g_cockpit_pref_notice="Preferência visual inválida; padrão temporário. Use Restaurar para substituir.";
      return;
     }
   g_cockpit_prefs=stored;
  }

bool JPWCockpitOwnedSuffix(const string suffix)
  {
   if(suffix=="HUD_BG" || suffix=="RAIZ_DETAILS_BUTTON") return(true);
   if(StringLen(suffix)==1 && StringGetCharacter(suffix,0)>='0' &&
      StringGetCharacter(suffix,0)<='5') return(true);
   return(StringFind(suffix,"RAIZ_UI_")==0 && StringLen(suffix)>8);
  }

bool JPWCockpitOwnedUIName(const string name)
  {
   const string stem="JPW_LEV_";
   if(StringFind(name,stem)!=0) return(false);
   int at=StringLen(stem);
   const int length=StringLen(name);
   const int chart_start=at;
   while(at<length && StringGetCharacter(name,at)>='0' &&
         StringGetCharacter(name,at)<='9') at++;
   if(at==chart_start || at>=length || StringGetCharacter(name,at)!='_') return(false);
   string suffix=StringSubstr(name,at+1);
   if(JPWCockpitOwnedSuffix(suffix)) return(true);
   // Prior releases added a numeric instance token between chart id and UI name.
   at=0;
   while(at<StringLen(suffix) && StringGetCharacter(suffix,at)>='0' &&
         StringGetCharacter(suffix,at)<='9') at++;
   if(at==0 || at>=StringLen(suffix) || StringGetCharacter(suffix,at)!='_') return(false);
   return(JPWCockpitOwnedSuffix(StringSubstr(suffix,at+1)));
  }

void JPWCockpitRemoveForeignHUD(const string current_prefix)
  {
   // Templates may include graphical objects drawn by the previous chart.
   // Remove only our orphaned UI names; never touch the chart preference or
   // user objects. Same-chart reinitialization reuses the stable prefix.
   // The pre-1.8 prefix appended a microsecond token after ChartID; those
   // saved labels must also be removed on the same chart.
   for(int i=ObjectsTotal(0,-1,-1)-1;i>=0;i--)
     {
      const string name=ObjectName(0,i,-1,-1);
      if(!JPWCockpitOwnedUIName(name)) continue;
      bool orphan=(StringFind(name,current_prefix)!=0);
      if(!orphan)
        {
         const string suffix=StringSubstr(name,StringLen(current_prefix));
         if(!JPWCockpitOwnedSuffix(suffix)) orphan=true;
        }
      if(orphan)
         ObjectDelete(0,name);
     }
  }

bool JPWCockpitSavePrefs(JPWCockpitPrefs &candidate)
  {
   const string encoded=JPWCockpitEncode(candidate);
   if(encoded=="") return(false);
   const bool existed=(ObjectFind(0,JPW_COCKPIT_PREF_OBJECT)>=0);
   if(existed && ObjectGetInteger(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_TYPE)!=OBJ_LABEL)
      return(false);
   if(!existed && !ObjectCreate(0,JPW_COCKPIT_PREF_OBJECT,OBJ_LABEL,0,0,0)) return(false);
   const string previous=(existed ? ObjectGetString(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_TEXT) : "");
   ObjectSetInteger(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_XDISTANCE,100000);
   ObjectSetInteger(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_YDISTANCE,100000);
   ObjectSetInteger(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_FONTSIZE,1);
   ObjectSetInteger(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_SELECTABLE,false);
   ObjectSetInteger(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_HIDDEN,true);
   if(!ObjectSetString(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_TEXT,encoded) ||
      ObjectGetString(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_TEXT)!=encoded)
     {
      if(existed) ObjectSetString(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_TEXT,previous);
      else ObjectDelete(0,JPW_COCKPIT_PREF_OBJECT);
      return(false);
     }
   JPWQueueDiagnostic(JPW_DIAG_SETTINGS_APPLIED);
   g_cockpit_prefs=candidate;
   g_cockpit_pref_invalid=false; g_cockpit_pref_notice="";
   g_cockpit_template_recheck=0;
   return(true);
  }

void JPWLivePopulateFields()
  {
   g_live_draft_generation=(g_live_config_state==JPW_RAIZN_VALID ? g_live_config.generation : 0);
   g_raiz_fields[17]=(g_live_config_state==JPW_RAIZN_VALID ? IntegerToString(g_live_config.n) : "");
   g_raiz_fields[18]=(g_live_config_state==JPW_RAIZN_VALID ? g_live_config.n_reason : "");
   g_raiz_fields[19]=(g_live_config_state==JPW_RAIZN_VALID ? DoubleToString(g_live_config.f,-16) : "");
   g_raiz_fields[20]=(g_live_config_state==JPW_RAIZN_VALID ? g_live_config.f_reason : "");
  }

void JPWFactorPopulateDraft()
  {
   g_factor_draft_generation=(g_factor_state==JPW_RAIZN_VALID ?
                              g_factor_preference.generation : 0);
   g_factor_draft=(g_factor_state==JPW_RAIZN_VALID ?
                   g_factor_preference.factor :
                   (g_factor_state==JPW_RAIZN_ABSENT ? JPW_RAIZN_FACTOR_DEFAULT : 0.0));
  }

void JPWFactorSelect(const double factor)
  {
   if(g_factor_state!=JPW_RAIZN_VALID && g_factor_state!=JPW_RAIZN_ABSENT)
     { JPWRaizFeedback("Registro de F indisponível: "+g_factor_reason); return; }
   if(!JPWRaizNFactorAllowed(factor))
     { JPWRaizFeedback("Apenas F 1,5 ou F 1,8 são permitidos neste diagnóstico."); return; }
   g_factor_draft=factor;
   g_raiz_feedback="F "+(factor==1.8 ? "1,8" : "1,5")+
                   " selecionado no rascunho. Aplicar confirma; Cancelar descarta.";
   JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0);
  }

void JPWFactorApply()
  {
   if(g_factor_state!=JPW_RAIZN_VALID && g_factor_state!=JPW_RAIZN_ABSENT)
     { JPWRaizFeedback("F não gravado: "+g_factor_reason); return; }
   if(!JPWRaizNFactorAllowed(g_factor_draft))
     { JPWRaizFeedback("Selecione F 1,5 ou F 1,8."); return; }
   JPWAccount account,after;
   string currency="",key="",reason=""; double scale=0.0;
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   if(!g_raiz_draft_account_known || g_raiz_draft_symbol!=_Symbol ||
      !JPWReadAccount(account) || !JPWAccountsEqual(account,g_raiz_draft_account) ||
      !JPWAccountUnits(account.currency,currency,scale) ||
      !JPWRaizNFactorKey(account.server,account.login,account.currency,scale,
                         installation,_Symbol,key) || key!=g_factor_key ||
      !JPWReadAccount(after) || !JPWAccountsEqual(account,after))
     { JPWRaizFeedback("Conta, instrumento ou instalação mudou; reabra Details."); return; }
   JPWRaizNFactorPreference draft;
   JPWRaizNFactorClear(draft);
   draft.account_key=key; draft.symbol=_Symbol;
   draft.generation=g_factor_draft_generation;
   draft.factor=g_factor_draft;
   draft.confirmed_at=TimeGMT();
   if(draft.confirmed_at<=0)
     { JPWRaizFeedback("Relógio do computador indisponível; F não gravado."); return; }
   const JPW_RAIZN_STATE saved=JPWRaizNFactorSave(JPW_RAIZN_FOLDER,key,_Symbol,
                                     g_factor_draft_generation,draft,reason);
   if(saved!=JPW_RAIZN_VALID)
     { JPWRaizFeedback("F não gravado: "+reason); return; }
   JPWQueueDiagnostic(JPW_DIAG_SETTINGS_APPLIED);
   g_factor_draft_generation=draft.generation;
   g_raiz_feedback="F "+(draft.factor==1.8 ? "1,8" : "1,5")+
      " gravado para o diagnóstico 1W/2W. P-21 permanece PENDING.";
   g_raiz_due=true;
   JPWRaizPanelDestroy(); g_raiz_tab=JPW_ROUTE_LEGACY_SUMMARY; g_raiz_page=0;
   g_refresh_requested=true; JPWRenderCurrentDisplay();
  }

bool JPWLivePositiveFactor(const string raw,double &value)
  {
   // Ordinary user decimals and the full-precision persisted representation
   // are both accepted. Reopening/editing N must not round or zero F.
   return((JPWRaizPositiveNumber(raw,value) || JPWRaizNDouble(raw,value)) &&
          MathIsValidNumber(value) && value>0.0);
  }

void JPWLiveApply()
  {
   JPWRaizSaveVisibleFields();
   long n=0; double f=0.0;
   if(!JPWRaizPositiveInteger(g_raiz_fields[17],n) || n>2147483647 ||
      !JPWLivePositiveFactor(g_raiz_fields[19],f) ||
      !JPWRaizHasText(g_raiz_fields[18]) || !JPWRaizHasText(g_raiz_fields[20]))
     { JPWRaizFeedback("Informe N inteiro positivo, F positivo e as duas justificativas."); return; }
   JPWAccount account,after;
   string currency="",key="",reason=""; double scale=0.0;
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   if(!g_raiz_draft_account_known || g_raiz_draft_symbol!=_Symbol ||
      !JPWReadAccount(account) || !JPWAccountsEqual(account,g_raiz_draft_account) ||
      !JPWAccountUnits(account.currency,currency,scale) ||
      !JPWRaizNConfigKey(account.server,account.login,account.currency,scale,installation,_Symbol,key) ||
      !JPWReadAccount(after) || !JPWAccountsEqual(account,after))
     { JPWRaizFeedback("Conta/instrumento mudou; feche e reabra Details."); return; }
   JPWRaizNConfig draft;
   draft.account_key=key; draft.symbol=_Symbol; draft.generation=g_live_draft_generation;
   draft.n=(int)n; draft.f=f; draft.n_reason=g_raiz_fields[18]; draft.f_reason=g_raiz_fields[20];
   draft.confirmed_at=TimeGMT();
   const JPW_RAIZN_STATE result=JPWRaizNConfigSave(JPW_RAIZN_FOLDER,key,_Symbol,g_live_draft_generation,draft,reason);
   if(result!=JPW_RAIZN_VALID)
     { JPWRaizFeedback("Não foi possível confirmar N/F: "+reason); return; }
   JPWQueueDiagnostic(JPW_DIAG_SETTINGS_APPLIED);
   g_live_draft_generation=draft.generation;
   g_raiz_feedback="N/F legados salvos; não alteram Raiz N diagnóstica 1W/2W. Cenários preservados.";
   JPWRaizPanelDestroy(); g_raiz_tab=JPW_ROUTE_LEGACY_SUMMARY; g_raiz_page=0;
   g_refresh_requested=true; JPWRenderCurrentDisplay();
  }

void JPWRaizSaveVisibleFields()
  {
   JPWSignalSaveDraft();
   if(!g_raiz_panel_built) return;
   for(int i=0;i<21;i++)
     {
      const string name=JPWRaizUI("EDIT_"+IntegerToString(i));
      if(ObjectFind(0,name)>=0) g_raiz_fields[i]=ObjectGetString(0,name,OBJPROP_TEXT);
     }
  }

void JPWRaizPopulateFields()
  {
   for(int i=0;i<17;i++) g_raiz_fields[i]="";
   g_raiz_fields[3]="MT5";
   g_raiz_fields[11]="DECLARED";
   g_raiz_fields[14]="0";
   if(g_raiz_store_state!=JPW_RAIZN_VALID) return;
   g_raiz_fields[0]=DoubleToString(g_raiz_scenario.p0,8);
   g_raiz_fields[1]=g_raiz_scenario.p0_origin;
   g_raiz_fields[2]=TimeToString(g_raiz_scenario.decision_server_time,TIME_DATE|TIME_SECONDS);
   g_raiz_fields[3]=g_raiz_scenario.atr_source;
   g_raiz_fields[4]=DoubleToString(g_raiz_scenario.atr,8);
   g_raiz_fields[5]=g_raiz_scenario.atr_provenance;
   g_raiz_fields[6]=g_raiz_scenario.atr_variant;
   g_raiz_fields[7]=TimeToString(g_raiz_scenario.atr_bar_server_time,TIME_DATE|TIME_SECONDS);
   g_raiz_fields[8]=IntegerToString(g_raiz_scenario.n_h4);
   g_raiz_fields[9]=g_raiz_scenario.n_reason;
   g_raiz_fields[10]=DoubleToString(g_raiz_scenario.factor,6);
   g_raiz_fields[11]=g_raiz_scenario.factor_status;
   g_raiz_fields[12]=g_raiz_scenario.factor_source;
   g_raiz_fields[13]=g_raiz_scenario.factor_reason;
   g_raiz_fields[14]=IntegerToString(g_raiz_scenario.declared_side);
   g_raiz_fields[15]=""; // revisão precisa de motivo novo, nunca herdado.
  }

bool JPWRaizHasText(const string value)
  {
   for(int i=0;i<StringLen(value);i++)
      if(StringGetCharacter(value,i)>32) return(true);
   return(false);
  }

bool JPWRaizPositiveNumber(const string raw,double &value)
  {
   value=0.0;
   bool digit=false,point=false;
   if(raw=="" || StringLen(raw)>32) return(false);
   for(int i=0;i<StringLen(raw);i++)
     {
      const ushort c=StringGetCharacter(raw,i);
      if(c>='0' && c<='9') { digit=true; continue; }
      if(c=='.' && !point) { point=true; continue; }
      return(false);
     }
   if(!digit) return(false);
   value=StringToDouble(raw);
   return(MathIsValidNumber(value) && value>0.0);
  }

bool JPWRaizPositiveInteger(const string raw,long &value)
  {
   value=0;
   if(raw=="" || StringLen(raw)>18) return(false);
   for(int i=0;i<StringLen(raw);i++)
     {
      const ushort c=StringGetCharacter(raw,i);
      if(c<'0' || c>'9') return(false);
      const long digit=(long)(c-'0');
      if(value>(LONG_MAX-digit)/10) return(false);
      value=value*10+digit;
     }
   return(value>0);
  }

bool JPWRaizServerTime(const string raw,datetime &value)
  {
   value=0;
   if(StringLen(raw)!=19 || StringGetCharacter(raw,4)!='.' ||
      StringGetCharacter(raw,7)!='.' || StringGetCharacter(raw,10)!=' ' ||
      StringGetCharacter(raw,13)!=':' || StringGetCharacter(raw,16)!=':') return(false);
   value=StringToTime(raw);
   return(value>0 && TimeToString(value,TIME_DATE|TIME_SECONDS)==raw);
  }

bool JPWRaizNativeATR(const datetime decision,double &atr,datetime &bar_open,
                      string &reason)
  {
   atr=0.0; bar_open=0; reason="";
   if(g_raiz_atr_handle==INVALID_HANDLE)
     { reason="handle ATR(55) H4 indisponível"; return(false); }
   // TimeTradeServer() depende do relógio local. A última cotação recebida
   // oferece um limite conservador formado no servidor, embora possa estar antiga.
   const datetime last_quote_server=TimeCurrent();
   if(!(bool)TerminalInfoInteger(TERMINAL_CONNECTED) ||
      last_quote_server<=0 || decision>last_quote_server)
     { reason="decisão posterior à última cotação conhecida do servidor"; return(false); }
   long synchronized=0;
   if(!SeriesInfoInteger(_Symbol,PERIOD_H4,SERIES_SYNCHRONIZED,synchronized) ||
      synchronized==0)
     { reason="série H4 não sincronizada"; return(false); }
   int shift=iBarShift(_Symbol,PERIOD_H4,decision,false);
   if(shift<0) { reason="barra H4 não localizada"; return(false); }
   datetime times[];
   if(CopyTime(_Symbol,PERIOD_H4,shift,1,times)!=1)
     { reason="horário da barra H4 não disponível"; return(false); }
   if(!JPWRaizNBarClosedBy(times[0],decision))
     {
      shift++;
      if(CopyTime(_Symbol,PERIOD_H4,shift,1,times)!=1)
        { reason="último H4 encerrado não disponível"; return(false); }
     }
   if(!JPWRaizNBarClosedBy(times[0],decision))
     { reason="barra H4 não encerrada na decisão"; return(false); }
   // O buffer zero pode ainda ser alterado ate a proxima barra existir.
   // Horario decorrido, por si, nao prova que o iATR foi finalizado.
   if(shift==0)
     { reason="barra H4 sem sucessora confirmada no terminal"; return(false); }
   if(shift>0)
     {
      datetime newer[];
      if(CopyTime(_Symbol,PERIOD_H4,shift-1,1,newer)!=1 ||
         newer[0]<=times[0] || JPWRaizNBarClosedBy(newer[0],decision))
        { reason="não foi possível provar a última barra H4 encerrada"; return(false); }
     }
   if(BarsCalculated(g_raiz_atr_handle)<=shift)
     { reason="ATR(55) ainda não calculado para a barra"; return(false); }
   double values[];
   if(CopyBuffer(g_raiz_atr_handle,0,shift,1,values)!=1 ||
      values[0]==EMPTY_VALUE || !MathIsValidNumber(values[0]) || values[0]<=0.0)
     { reason="ATR(55) inválido ou ausente nessa barra"; return(false); }
   datetime rechecked[];
   long checked_sync=0;
   if(CopyTime(_Symbol,PERIOD_H4,shift,1,rechecked)!=1 ||
      rechecked[0]!=times[0] ||
      !SeriesInfoInteger(_Symbol,PERIOD_H4,SERIES_SYNCHRONIZED,checked_sync) ||
      checked_sync==0)
     { reason="histórico H4 mudou durante a leitura"; return(false); }
   atr=values[0]; bar_open=times[0];
   return(true);
  }

void JPWRaizSwitchTab(const int tab)
  {
   if(g_raiz_tab==JPW_SIGNAL_ROUTE && tab!=JPW_SIGNAL_ROUTE) JPWSignalClear();
   if(g_raiz_tab==JPW_ROUTE_SETTINGS && tab!=JPW_ROUTE_SETTINGS)
     {
      g_cockpit_draft=g_cockpit_prefs;
      g_cockpit_reset_requested=false;
      JPWRenderHUD();
     }
   JPWRaizSaveVisibleFields();
   JPWRaizPanelDestroy();
   g_raiz_tab=tab;
   g_raiz_page=0;
   g_cockpit_page=0;
   JPWRenderRaizDetails();
   ChartRedraw(0);
  }

void JPWRaizFeedback(const string message)
  {
   g_raiz_feedback=message;
   JPWRaizSwitchTab(g_raiz_tab);
  }

bool JPWRaizCheckDraft(JPWRaizNScenario &draft,string &reason)
  {
   reason="";
   JPWRaizNClearScenario(draft);
   draft.model_version=JPW_RAIZN_MODEL_VERSION;
   draft.schema=1;
   draft.symbol=_Symbol;
   if(!JPWRaizPositiveNumber(g_raiz_fields[0],draft.p0))
     { reason="P0 deve ser um preço positivo finito."; return(false); }
   draft.p0_origin=g_raiz_fields[1];
   if(!JPWRaizHasText(draft.p0_origin))
     { reason="Informe a origem verificável de P0."; return(false); }
   if(!JPWRaizServerTime(g_raiz_fields[2],draft.decision_server_time))
     { reason="Use AAAA.MM.DD HH:MM:SS para a decisão."; return(false); }
   const datetime last_quote_server=TimeCurrent();
   if((bool)TerminalInfoInteger(TERMINAL_CONNECTED) &&
      last_quote_server>0 && draft.decision_server_time>last_quote_server)
     { reason="Decisão é posterior à última cotação conhecida do servidor."; return(false); }
   draft.atr_source=g_raiz_fields[3];
   if(draft.atr_source=="MT5")
     {
      if(!JPWRaizNativeATR(draft.decision_server_time,draft.atr,
                           draft.atr_bar_server_time,reason)) return(false);
      draft.atr_provenance="MetaTrader 5 iATR";
      draft.atr_variant="ATR nativo MT5/iATR; suavização não homologada pelo artigo";
     }
   else if(draft.atr_source=="DECLARED")
     {
      if(!JPWRaizPositiveNumber(g_raiz_fields[4],draft.atr))
        { reason="ATR declarado deve ser positivo."; return(false); }
      draft.atr_provenance=g_raiz_fields[5];
      draft.atr_variant=g_raiz_fields[6];
      if(!JPWRaizHasText(draft.atr_provenance) ||
         !JPWRaizHasText(draft.atr_variant))
        { reason="Fonte e variante do ATR declarado são obrigatórias."; return(false); }
      if(!JPWRaizServerTime(g_raiz_fields[7],draft.atr_bar_server_time) ||
         !JPWRaizNBarClosedBy(draft.atr_bar_server_time,draft.decision_server_time))
        { reason="Informe o início da barra H4 concluída até a decisão."; return(false); }
     }
   else { reason="ATR deve ser MT5 ou DECLARED."; return(false); }
   long n=0;
   if(!JPWRaizPositiveInteger(g_raiz_fields[8],n) || n>1000000)
     { reason="N deve ser inteiro de 1 a 1.000.000 candles H4."; return(false); }
   draft.n_h4=(int)n;
   draft.n_reason=g_raiz_fields[9];
   if(!JPWRaizHasText(draft.n_reason))
     { reason="Justifique o horizonte N."; return(false); }
   if(!JPWRaizPositiveNumber(g_raiz_fields[10],draft.factor))
     { reason="F deve ser positivo; 1,25 não é padrão homologado."; return(false); }
   draft.factor_status=g_raiz_fields[11];
   draft.factor_source=g_raiz_fields[12];
   draft.factor_reason=g_raiz_fields[13];
   if(draft.factor_status!="DECLARED" &&
      draft.factor_status!="ILLUSTRATIVE" && draft.factor_status!="SOURCED")
     { reason="Classifique F como DECLARED, ILLUSTRATIVE ou SOURCED."; return(false); }
   if(draft.factor_status=="SOURCED" && !JPWRaizHasText(draft.factor_source))
     { reason="F com fonte exige identificação da fonte."; return(false); }
   if(!JPWRaizHasText(draft.factor_reason))
     { reason="Justifique o fator F."; return(false); }
   if(g_raiz_fields[14]!="1" && g_raiz_fields[14]!="-1" &&
      g_raiz_fields[14]!="0")
     { reason="Lado deve ser 1 (BUY), -1 (SELL) ou 0."; return(false); }
   draft.declared_side=(int)StringToInteger(g_raiz_fields[14]);
   const bool revising=(g_raiz_draft_expected_id!="");
   draft.revision_reason=(revising ? g_raiz_fields[15] : "");
   draft.parent_id=(revising ? g_raiz_draft_expected_id : "");
   if(revising && !JPWRaizHasText(draft.revision_reason))
     { reason="Revisão exige motivo e preserva o cenário anterior."; return(false); }
   double dprice=0.0,dpct=0.0;
   if(JPWRaizNCalculate(draft.p0,draft.atr,draft.n_h4,draft.factor,
                        dprice,dpct)!=JPW_RAIZN_OK)
     { reason="A combinação de P0, ATR, N e F é inválida."; return(false); }
   return(true);
  }

void JPWRaizApply()
  {
   JPWRaizSaveVisibleFields();
   if(g_raiz_store_state!=JPW_RAIZN_VALID && g_raiz_store_state!=JPW_RAIZN_ABSENT)
     { JPWRaizFeedback("Registro não íntegro: "+JPWRaizNStoreReason(g_raiz_store_state)); return; }
   JPWRaizNScenario draft,confirmed;
   string reason="";
   if(!JPWRaizCheckDraft(draft,reason))
     { JPWRaizFeedback(reason); return; }
   JPWAccount account,after;
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   if(!g_raiz_draft_account_known || g_raiz_draft_symbol!=_Symbol)
     { JPWRaizFeedback("Conta ou instrumento mudou; feche e reabra Detalhes."); return; }
   if(!JPWReadAccount(account) || installation=="" ||
      !JPWRaizNAccountSymbolKey(account,_Symbol,installation,draft.account_key))
     { JPWRaizFeedback("Conta ou instalação indisponível."); return; }
   if(!JPWAccountsEqual(account,g_raiz_draft_account))
     { JPWRaizFeedback("Conta mudou desde a abertura; declaração recusada."); return; }
   draft.confirmed_at_utc=TimeGMT();
   if(draft.confirmed_at_utc<=0)
     { JPWRaizFeedback("Relógio do computador indisponível."); return; }
   // Only a connected, consistent, empty snapshot can support saying that a
   // declaration preceded any currently open position of this symbol. Even
   // then it does not independently prove the operator's earlier decision.
   draft.retrospective=true;
   if((bool)TerminalInfoInteger(TERMINAL_CONNECTED))
     {
      JPWGenesisPosition first[],second[];
      if(JPWReadGenesisSnapshot(first) && JPWReadGenesisSnapshot(second) &&
         JPWGenesisSnapshotsEqual(first,second))
        {
         bool position_exists=false;
         for(int i=0;i<ArraySize(second);i++)
            if(second[i].symbol==_Symbol) { position_exists=true; break; }
         if(!position_exists) draft.retrospective=false;
        }
     }
   if(!JPWReadAccount(after) || !JPWAccountsEqual(account,after))
     { JPWRaizFeedback("Conta alterada durante a confirmação."); return; }
   const string expected=g_raiz_draft_expected_id;
   const JPW_RAIZN_STATE result=JPWRaizNConfirm(account,_Symbol,installation,
      JPW_RAIZN_FOLDER,draft,expected,confirmed);
   if(result!=JPW_RAIZN_VALID)
     { JPWRaizFeedback("Cenário anterior preservado: "+JPWRaizNStoreReason(result)); return; }
   JPWQueueDiagnostic(JPW_DIAG_SETTINGS_APPLIED);
   g_raiz_feedback=(draft.retrospective ?
      "Cenário retrospectivo confirmado; o anterior foi preservado." :
      "Cenário confirmado; não representa autorização de entrada.");
   g_raiz_draft_expected_id=confirmed.scenario_id;
   JPWRaizPanelDestroy();
   g_raiz_tab=JPW_ROUTE_SCENARIOS;
   g_raiz_due=true;
   g_refresh_requested=true; JPWRenderCurrentDisplay();
   JPWRaizPopulateFields();
  }

void JPWRaizBindTicket()
  {
   JPWRaizSaveVisibleFields();
   if(g_raiz_store_state!=JPW_RAIZN_VALID)
     { JPWRaizFeedback("Confirme primeiro um cenário Raiz N válido."); return; }
   if(g_raiz_draft_expected_id!=g_raiz_scenario.scenario_id)
     { JPWRaizFeedback("Cenário mudou; feche e reabra Detalhes."); return; }
   if(g_raiz_scenario.declared_side==0)
     { JPWRaizFeedback("Declare BUY (1) ou SELL (-1) antes de vincular."); return; }
   long requested=0;
   if(!JPWRaizPositiveInteger(g_raiz_fields[16],requested))
     { JPWRaizFeedback("Informe um ticket positivo aberto."); return; }
   if(!(bool)TerminalInfoInteger(TERMINAL_CONNECTED))
     { JPWRaizFeedback("Conexão necessária para confirmar o vínculo."); return; }
   JPWAccount account,after;
   JPWGenesisPosition first[],second[],chosen;
   JPWGenesisClear(chosen);
   if(!JPWReadAccount(account) || !JPWReadGenesisSnapshot(first) ||
      !JPWReadGenesisSnapshot(second) ||
      !JPWGenesisSnapshotsEqual(first,second) || !JPWReadAccount(after) ||
      !JPWAccountsEqual(account,after))
     { JPWRaizFeedback("Conta ou posições mudaram durante a conferência."); return; }
   if(!g_raiz_draft_account_known || g_raiz_draft_symbol!=_Symbol ||
      !JPWAccountsEqual(account,g_raiz_draft_account))
     { JPWRaizFeedback("Conta mudou desde a abertura; vínculo recusado."); return; }
   bool found=false;
   for(int i=0;i<ArraySize(second);i++)
      if(second[i].ticket==(ulong)requested)
        { chosen=second[i]; found=true; break; }
   if(!found)
     { JPWRaizFeedback("Ticket não está aberto nesta conta."); return; }
   if(chosen.symbol!=_Symbol || chosen.symbol!=g_raiz_scenario.symbol)
     { JPWRaizFeedback("Ticket pertence a outro símbolo; vínculo recusado."); return; }
   if(g_raiz_scenario.declared_side!=0 &&
      ((g_raiz_scenario.declared_side==1 && chosen.direction!=POSITION_TYPE_BUY) ||
       (g_raiz_scenario.declared_side==-1 && chosen.direction!=POSITION_TYPE_SELL)))
     { JPWRaizFeedback("Direção da posição diverge do cenário declarado."); return; }
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   if(installation=="")
     { JPWRaizFeedback("Identidade da instalação indisponível."); return; }
   JPWRaizNBinding confirmed;
   const JPW_RAIZN_STATE result=JPWRaizNBind(account,_Symbol,installation,
      JPW_RAIZN_FOLDER,g_raiz_scenario.scenario_id,chosen.identifier,
      requested,chosen.direction,confirmed);
   if(result!=JPW_RAIZN_VALID)
     { JPWRaizFeedback("Vínculo não gravado: "+JPWRaizNStoreReason(result)); return; }
   JPWQueueDiagnostic(JPW_DIAG_SETTINGS_APPLIED);
   g_raiz_feedback="Vínculo explícito confirmado; SL e ordens não foram alterados.";
   JPWRaizPanelDestroy();
   g_raiz_tab=JPW_ROUTE_SCENARIOS;
   g_raiz_due=true;
   g_refresh_requested=true; JPWRenderCurrentDisplay();
  }

void JPWRaizRecordComparison()
  {
   if(g_raiz_store_state!=JPW_RAIZN_VALID ||
      g_raiz_draft_expected_id!=g_raiz_scenario.scenario_id ||
      g_raiz_binding.state!=JPW_RAIZN_VALID ||
      g_raiz_binding.identifier<=0)
     { JPWRaizFeedback("Cenário ou vínculo mudou; reabra Detalhes."); return; }
   if(!(bool)TerminalInfoInteger(TERMINAL_CONNECTED))
     { JPWRaizFeedback("Conexão necessária para registrar o SL atual."); return; }
   JPWAccount before,after;
   JPWGenesisPosition first[],second[],position;
   JPWGenesisClear(position);
   if(!JPWReadAccount(before) || !JPWReadGenesisSnapshot(first) ||
      !JPWReadGenesisSnapshot(second) ||
      !JPWGenesisSnapshotsEqual(first,second) ||
      !JPWReadAccount(after) || !JPWAccountsEqual(before,after) ||
      !g_raiz_draft_account_known ||
      !JPWAccountsEqual(before,g_raiz_draft_account))
     { JPWRaizFeedback("Conta ou posições mudaram durante a comparação."); return; }
   if(!JPWGenesisFindByIdentifier(second,g_raiz_binding.identifier,position) ||
      position.symbol!=g_raiz_scenario.symbol ||
      position.direction!=g_raiz_binding.direction ||
      !JPWFinitePositive(position.sl))
     { JPWRaizFeedback("Posição ou SL adverso indisponível para comparar."); return; }
   double dprice=0.0,dpct=0.0,slprice=0.0,slpct=0.0;
   double gapprice=0.0,gappct=0.0;
   const JPW_RAIZN_SIDE side=(position.direction==POSITION_TYPE_BUY ?
                              JPW_RAIZN_SIDE_BUY : JPW_RAIZN_SIDE_SELL);
   if(JPWRaizNCalculate(g_raiz_scenario.p0,g_raiz_scenario.atr,
                        g_raiz_scenario.n_h4,g_raiz_scenario.factor,
                        dprice,dpct)!=JPW_RAIZN_OK ||
      JPWRaizNCompareSL(side,g_raiz_scenario.p0,position.sl,dprice,
                        slprice,slpct,gapprice,gappct)!=JPW_RAIZN_SL_OK)
     { JPWRaizFeedback("SL em P0, protetor ou inválido; sem comparação adversa."); return; }
   const datetime observed=TimeGMT();
   const string installation=TerminalInfoString(TERMINAL_DATA_PATH);
   if(observed<=0 || installation=="")
     { JPWRaizFeedback("Relógio ou instalação indisponível."); return; }
   string receipt="";
   const JPW_RAIZN_STATE state=JPWRaizNRecordComparison(before,_Symbol,
      installation,JPW_RAIZN_FOLDER,g_raiz_scenario.scenario_id,
      g_raiz_binding.identifier,position.sl,observed,receipt);
   if(state!=JPW_RAIZN_VALID)
     { JPWRaizFeedback("Comparação não gravada: "+JPWRaizNStoreReason(state)); return; }
   JPWQueueDiagnostic(JPW_DIAG_SETTINGS_APPLIED);
   JPWRaizFeedback("Comparação registrada: "+StringSubstr(receipt,0,12)+
                   ". Cenário inicial preservado.");
  }

bool g_jpw_focus_suspended=false;

void JPWOpenCockpit(const int metric=-1)
  {
   // Opening/navigation uses the accepted snapshot. Explicit Refresh schedules
   // a coordinator cycle; no account financial collection occurs here.
   if(!g_account_known || g_sample_context=="") { g_refresh_requested=true; return; }
   const bool resume=g_jpw_focus_suspended && g_raiz_draft_account_known &&
                     g_raiz_draft_symbol==_Symbol && JPWAccountsEqual(g_raiz_draft_account,g_account);
   if(!JPWUIAcquire(g_panel_prefix)) return;
   if(resume)
     { g_jpw_focus_suspended=false; g_raiz_details_open=true;
       JPWRenderRaizDetails(); ChartRedraw(0); return; }
   g_jpw_focus_suspended=false;
   g_raiz_draft_account=g_account; g_raiz_draft_account_known=true;
   g_raiz_draft_symbol=_Symbol;
   JPWRaizPopulateFields(); JPWLivePopulateFields(); JPWFactorPopulateDraft();
   g_raiz_draft_expected_id=(g_raiz_store_state==JPW_RAIZN_VALID ? g_raiz_scenario.scenario_id : "");
   g_record_read_requested=true;
   g_raiz_details_open=true;
   g_raiz_tab=(metric>=0 && metric<JPW_COCKPIT_METRIC_COUNT ? JPW_ROUTE_METRIC : JPW_ROUTE_OVERVIEW);
   g_cockpit_selected=(metric>=0 && metric<JPW_COCKPIT_METRIC_COUNT ? metric : 0);
   g_cockpit_draft=g_cockpit_prefs;
   g_cockpit_page=0; g_raiz_feedback="";
   JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0);
  }

void JPWHandleChartEvent(const int id,const long &lparam,const double &dparam,const string &sparam)
  {
   if(id==CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT && sparam!=JPWUIOwner()) return;
   if(id==CHARTEVENT_CUSTOM+JPW_UI_OWNER_EVENT && sparam!=g_panel_prefix)
     {
      if(g_raiz_details_open)
        {
         JPWRaizSaveVisibleFields();
         g_jpw_focus_suspended=true;
         g_raiz_details_open=false;
         JPWRaizPanelDestroy(); JPWRenderHUD(); ChartRedraw(0);
        }
      return;
     }
   if(id==CHARTEVENT_KEYDOWN && g_raiz_details_open && !JPWUIOwns(g_panel_prefix)) return;
   JPWAccount event_account;
   if(g_account_known && (!JPWReadAccount(event_account) ||
      !JPWAccountsEqual(g_account,event_account) ||
      (g_cockpit_snapshot.symbol!="" && g_cockpit_snapshot.symbol!=_Symbol)))
     { JPWSignalInvalidate("conta ou símbolo mudou."); JPWInvalidateIdentityPresentation(); g_refresh_requested=true;
       JPWRenderCurrentDisplay(); return; }

   if(id==CHARTEVENT_CHART_CHANGE)
     {
      if(g_raiz_details_open)
        { JPWRaizSaveVisibleFields(); JPWRaizPanelDestroy(); }
      JPWRenderCurrentDisplay();
      return;
     }
   if(id==CHARTEVENT_OBJECT_ENDEDIT) g_editing_field=false;
   if(id==CHARTEVENT_OBJECT_CLICK) g_editing_field=(StringFind(sparam,JPWRaizUI("EDIT_"))==0);
   if(id==CHARTEVENT_OBJECT_ENDEDIT && g_raiz_details_open)
     {
      for(int i=0;i<21;i++)
         if(sparam==JPWRaizUI("EDIT_"+IntegerToString(i)))
           { g_raiz_fields[i]=ObjectGetString(0,sparam,OBJPROP_TEXT); return; }
     }
   if(id==CHARTEVENT_KEYDOWN && g_raiz_details_open && !g_editing_field)
     {
      if(lparam==9)
        { const bool shift=(((int)TerminalInfoInteger(TERMINAL_KEYSTATE_SHIFT)&0x8000)!=0);
          JPWFocusStep(shift); return; }
      if(lparam==13 && g_focus_action>=0)
        { const long unused=0; const double d=0.0;
          const string target=JPWRaizUI("BUTTON_"+IntegerToString(g_focus_action));
          if(ObjectFind(0,target)>=0) JPWHandleChartEvent(CHARTEVENT_OBJECT_CLICK,unused,d,target);
          return; }
     }
   if(id==CHARTEVENT_KEYDOWN && g_editing_field) return;
   if(id==CHARTEVENT_KEYDOWN && lparam==27 && g_raiz_details_open)
     {
      g_cockpit_draft=g_cockpit_prefs;
      g_cockpit_reset_requested=false;
      JPWSignalClear(); g_raiz_details_open=false; JPWUIRelease(g_panel_prefix); g_raiz_draft_account_known=false;
      g_raiz_draft_expected_id=""; JPWRaizPanelDestroy(); JPWRenderHUD(); ChartRedraw(0); return;
     }
   if(id==CHARTEVENT_KEYDOWN && g_raiz_details_open && g_raiz_tab>=JPW_ROUTE_OVERVIEW)
     {
      if(!JPWDetailsContextCurrent()) return;
      // Chart-level keys only; editing pages retain their own input behavior.
      if(g_raiz_tab==JPW_ROUTE_STOPS && !g_stops_show_pending &&
         (lparam==38 || lparam==40))
        {
         const int maximum=MathMax(0,g_positions_total_rows-g_positions_visible_rows);
         g_positions_scroll=JPWPanelClamp(g_positions_scroll+(lparam==38 ? -1 : 1),0,maximum);
         JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return;
        }
      if((lparam==37 || lparam==39))
        { g_cockpit_page+=(lparam==37 ? -1 : 1);
          JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return; }
      if((g_raiz_tab==JPW_ROUTE_OVERVIEW || g_raiz_tab==JPW_ROUTE_METRIC) && lparam>=49 && lparam<=54)
        { g_cockpit_selected=(int)(lparam-49); JPWRaizSwitchTab(JPW_ROUTE_METRIC); return; }
     }
   if(id!=CHARTEVENT_OBJECT_CLICK) return;
   for(int metric=0;metric<JPW_COCKPIT_METRIC_COUNT;metric++)
      if(sparam==g_panel_prefix+IntegerToString(metric))
        {
         const int target=JPWCockpitHUDTarget(g_hud_summary,g_hud_summary_source,metric);
         if(!g_raiz_details_open) JPWOpenCockpit(target);
         else if(target>=0) { g_cockpit_selected=target; JPWRaizSwitchTab(JPW_ROUTE_METRIC); }
         else JPWRaizSwitchTab(JPW_ROUTE_OVERVIEW);
         return;
        }
   if(sparam==g_panel_prefix+"RAIZ_DETAILS_BUTTON")
     {
      ObjectSetInteger(0,sparam,OBJPROP_STATE,false);
      if(g_raiz_details_open)
        {
         g_cockpit_draft=g_cockpit_prefs; g_cockpit_reset_requested=false;
         JPWSignalClear(); g_raiz_details_open=false; JPWUIRelease(g_panel_prefix); g_raiz_draft_account_known=false;
         g_raiz_draft_expected_id=""; JPWRaizPanelDestroy(); JPWRenderHUD();
        }
      else JPWOpenCockpit();
      ChartRedraw(0); return;
     }
   if(!g_raiz_details_open) return;
   if(!JPWDetailsContextCurrent()) return;
   if(JPWSignalHandleClick(sparam)) return;
   for(int i=0;i<100;i++)
      if(sparam==JPWRaizUI("BUTTON_"+IntegerToString(i)))
        { ObjectSetInteger(0,sparam,OBJPROP_STATE,false); break; }
   if(sparam==JPWActionObject(JPW_ACTION_TAB_FIRST)) { JPWRaizSwitchTab(JPW_ROUTE_OVERVIEW); return; }
   if(sparam==JPWActionObject(JPW_ACTION_TAB_STOPS))
     { g_record_read_requested=true; JPWRaizSwitchTab(JPW_ROUTE_STOPS); return; }
   if(sparam==JPWActionObject(JPW_ACTION_TAB_RAIZN)) { JPWRaizSwitchTab(JPW_ROUTE_RAIZN); return; }
   if(sparam==JPWActionObject(JPW_ACTION_TAB_SYSTEM))
     { g_record_read_requested=true; JPWRaizSwitchTab(JPW_ROUTE_SYSTEM); return; }
   if(sparam==JPWActionObject(JPW_ACTION_TAB_SETTINGS))
     { g_cockpit_draft=g_cockpit_prefs; g_cockpit_reset_requested=false;
       JPWRaizSwitchTab(JPW_ROUTE_SETTINGS); return; }
   for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)
      if(sparam==JPWRaizUI("BUTTON_"+IntegerToString(JPW_ACTION_CARD_FIRST+i)) ||
         sparam==JPWRaizUI("CARD_BG_"+IntegerToString(i)) ||
         sparam==JPWRaizUI("CARD_"+IntegerToString(i)+"_VALUE") ||
         sparam==JPWRaizUI("CARD_"+IntegerToString(i)+"_QUALITY") ||
         sparam==JPWRaizUI("CARD_"+IntegerToString(i)+"_REASON"))
        { g_cockpit_selected=i; JPWRaizSwitchTab(JPW_ROUTE_METRIC); return; }
   if(g_raiz_tab==JPW_ROUTE_STOPS)
      for(int i=0;i<g_stop_button_count;i++)
        {
         bool row_click=(sparam==JPWRaizUI("BUTTON_"+IntegerToString(JPW_ACTION_STOP_ROW_FIRST+i)));
         if(!g_stops_show_pending)
            for(int c=0;c<6;c++)
               if(sparam==JPWRaizUI("POSITION_CELL_"+IntegerToString(i)+"_"+IntegerToString(c))) row_click=true;
         if(row_click)
           {
            if(!g_stops_show_pending)
              {
               const int found=JPWPositionsViewFind(g_position_button_ticket[i],g_position_button_identifier[i]);
               if(found<0 || !JPWPositionsViewCurrent(g_sample_context,GetTickCount64()))
                 { g_refresh_requested=true; JPWRaizPanelDestroy(); JPWRenderRaizDetails(); return; }
               g_position_detail_ticket=g_position_views[found].ticket;
               g_position_detail_identifier=g_position_views[found].identifier;
               g_position_detail_open=true;
               JPWRaizSwitchTab(JPW_ROUTE_STOP_ROW); return;
              }
            g_position_detail_open=false; g_stop_selected_row=g_stop_button_row[i];
             g_stop_selected_role=g_stop_button_role[i];
             JPWRaizSwitchTab(JPW_ROUTE_STOP_ROW); return;
           }
        }
   if(sparam==JPWActionObject(JPW_ACTION_POSITIONS_UP) ||
      sparam==JPWActionObject(JPW_ACTION_POSITIONS_DOWN))
     {
      if(g_raiz_tab!=JPW_ROUTE_STOPS || g_stops_show_pending) return;
      const int maximum=MathMax(0,g_positions_total_rows-g_positions_visible_rows);
      g_positions_scroll=JPWPanelClamp(g_positions_scroll+
         (sparam==JPWActionObject(JPW_ACTION_POSITIONS_UP) ? -1 : 1),0,maximum);
      JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return;
     }
   if(sparam==JPWActionObject(JPW_ACTION_PRIMARY))
     {
      if(g_raiz_tab==JPW_ROUTE_METRIC) JPWRaizSwitchTab(JPW_ROUTE_OVERVIEW);
      else if(g_raiz_tab==JPW_ROUTE_PROVENANCE) JPWRaizSwitchTab(JPW_ROUTE_SYSTEM);
      else if(g_raiz_tab==JPW_ROUTE_STOP_ROW)
        {
         if(g_position_detail_open)
           { const int found=JPWPositionsViewFind(g_position_detail_ticket,g_position_detail_identifier);
             if(found>=0) JPWSignalOpen(JPW_SIGNAL_POSITION,g_position_detail_ticket,g_position_detail_identifier);
             else { g_refresh_requested=true; JPWRaizSwitchTab(JPW_ROUTE_STOPS); } }
         else if(g_stop_selected_row>=0 && g_stop_selected_row<ArraySize(g_stop_table_rows))
           { JPWStopRiskRow row=g_stop_table_rows[g_stop_selected_row];
             JPWSignalOpen(row.kind==JPW_STOP_RISK_PENDING ? JPW_SIGNAL_PENDING : JPW_SIGNAL_POSITION,
                           (ulong)row.ticket,row.kind==JPW_STOP_RISK_PENDING ? 0 : row.identifier); }
         else JPWSignalOpen();
        }
      else if(g_raiz_tab==JPW_ROUTE_STOPS)
        { if(g_stops_show_pending) g_stops_show_pending=false;
          else g_positions_operation_only=!g_positions_operation_only;
          g_positions_scroll=0; JPWRaizSwitchTab(JPW_ROUTE_STOPS); }
      else if(g_raiz_tab==JPW_ROUTE_RAIZN) JPWRaizSwitchTab(JPW_ROUTE_FACTOR);
      else if(g_raiz_tab==JPW_ROUTE_SYSTEM)
        { g_record_read_requested=true; JPWRaizSwitchTab(JPW_ROUTE_PROVENANCE); }
      else if(g_raiz_tab==JPW_ROUTE_EXPORT) JPWRaizSwitchTab(JPW_ROUTE_SYSTEM);
      else JPWRaizSwitchTab(JPW_ROUTE_STOPS);
      return;
     }
   if(sparam==JPWActionObject(JPW_ACTION_SECONDARY))
     {
      if(g_raiz_tab==JPW_ROUTE_OVERVIEW) JPWSignalOpen();
      else if(g_raiz_tab==JPW_ROUTE_METRIC) JPWRaizSwitchTab(JPW_ROUTE_PROVENANCE);
      else if(g_raiz_tab==JPW_ROUTE_PROVENANCE)
        { g_record_read_requested=true; g_refresh_requested=true; JPWRaizSwitchTab(g_raiz_tab); }
      else if(g_raiz_tab==JPW_ROUTE_SYSTEM)
        { g_export_preview=""; g_export_result=""; g_export_preview_requested=true;
          JPWRaizSwitchTab(JPW_ROUTE_EXPORT); }
      else if(g_raiz_tab==JPW_ROUTE_EXPORT)
        { if(g_export_preview!="") { g_export_requested=true; g_export_result="Exportação solicitada."; }
          JPWRaizPanelDestroy(); JPWRenderRaizDetails(); }
      else if(g_raiz_tab==JPW_ROUTE_STOPS || g_raiz_tab==JPW_ROUTE_STOP_ROW)
        { g_stops_show_pending=true; JPWRaizSwitchTab(JPW_ROUTE_STOPS); }
      else if(g_raiz_tab==JPW_ROUTE_RAIZN) JPWRaizSwitchTab(JPW_ROUTE_SCENARIOS);
      else JPWRaizSwitchTab(JPW_ROUTE_RAIZN);
      return;
     }
   if(sparam==JPWActionObject(JPW_ACTION_APPLY) && g_raiz_tab==JPW_ROUTE_SETTINGS)
     {
      if(g_cockpit_pref_invalid && !g_cockpit_reset_requested)
        { g_cockpit_pref_notice="Preferência inválida preservada. Use Restaurar antes de aplicar.";
          JPWRaizPanelDestroy(); JPWRenderRaizDetails(); return; }
      if(!JPWCockpitSavePrefs(g_cockpit_draft))
        { g_cockpit_pref_notice=(ObjectFind(0,JPW_COCKPIT_PREF_OBJECT)>=0 &&
             ObjectGetInteger(0,JPW_COCKPIT_PREF_OBJECT,OBJPROP_TYPE)!=OBJ_LABEL ?
             "Nome da preferência ocupado por outro tipo de objeto; remova-o manualmente." :
             "Falha ao salvar; configuração anterior preservada.");
          JPWRaizPanelDestroy(); JPWRenderRaizDetails(); return; }
      g_cockpit_reset_requested=false;
      JPWRenderHUD(); JPWRaizSwitchTab(JPW_ROUTE_OVERVIEW); return;
     }
   if(sparam==JPWActionObject(JPW_ACTION_CANCEL) && g_raiz_tab==JPW_ROUTE_SETTINGS)
     { g_cockpit_draft=g_cockpit_prefs; g_cockpit_reset_requested=false;
       JPWRenderHUD(); JPWRaizSwitchTab(JPW_ROUTE_OVERVIEW); return; }
   if(sparam==JPWActionObject(JPW_ACTION_RESET) && g_raiz_tab==JPW_ROUTE_SETTINGS)
     { JPWCockpitDefault(g_cockpit_draft,(int)InpCorner); g_cockpit_reset_requested=true;
       JPWRenderHUD(); JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return; }
   if(sparam==JPWActionObject(JPW_ACTION_CORNER) && g_raiz_tab==JPW_ROUTE_SETTINGS)
     { g_cockpit_draft.corner=JPWCockpitNextCorner(g_cockpit_draft.corner);
       JPWRenderHUD(); JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return; }
   if(sparam==JPWActionObject(JPW_ACTION_DENSITY) && g_raiz_tab==JPW_ROUTE_SETTINGS)
     { g_cockpit_draft.density=1-g_cockpit_draft.density;
       JPWRenderHUD(); JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return; }
   for(int i=0;i<JPW_COCKPIT_METRIC_COUNT;i++)
      if(sparam==JPWRaizUI("BUTTON_"+IntegerToString(JPW_ACTION_VISIBILITY_FIRST+i)) && g_raiz_tab==JPW_ROUTE_SETTINGS)
        { g_cockpit_draft.visible_mask^=(1<<i);
          JPWRenderHUD(); JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return; }
   if(sparam==JPWActionObject(JPW_ACTION_CLOSE) ||
      sparam==JPWActionObject(JPW_ACTION_HEADER_CLOSE))
     { g_cockpit_draft=g_cockpit_prefs; g_cockpit_reset_requested=false;
       JPWSignalClear(); g_raiz_details_open=false; JPWUIRelease(g_panel_prefix); g_raiz_draft_account_known=false;
       g_raiz_draft_expected_id=""; JPWRaizPanelDestroy(); JPWRenderHUD(); ChartRedraw(0); return; }
   if(sparam==JPWActionObject(JPW_ACTION_PREVIOUS) || sparam==JPWActionObject(JPW_ACTION_NEXT))
     { g_cockpit_page+=(sparam==JPWActionObject(JPW_ACTION_PREVIOUS) ? -1 : 1);
       JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return; }
   // Every navigation path captures edits; only Apply can write configuration.
   if(sparam==JPWActionObject(JPW_ACTION_HOME))
     { JPWRaizSaveVisibleFields(); g_refresh_requested=true; if(!g_raiz_details_open) return;
       g_record_read_requested=true; JPWRaizSwitchTab(JPW_ROUTE_OVERVIEW); return; }
   if(sparam==JPWActionObject(JPW_ACTION_FACTOR)) { JPWRaizSwitchTab(JPW_ROUTE_FACTOR); return; }
   if(sparam==JPWActionObject(JPW_ACTION_LEGACY_NF)) { JPWRaizSwitchTab(JPW_ROUTE_LEGACY_NF); return; }
   if(sparam==JPWActionObject(JPW_ACTION_ADVANCED)) { JPWRaizSwitchTab(JPW_ROUTE_SCENARIOS); return; }
   if(sparam==JPWActionObject(JPW_ACTION_FACTOR_15)) { JPWFactorSelect(1.5); return; }
   if(sparam==JPWActionObject(JPW_ACTION_FACTOR_18)) { JPWFactorSelect(1.8); return; }
   if(sparam==JPWActionObject(JPW_ACTION_REFRESH))
     {
      JPWRaizSaveVisibleFields(); g_refresh_requested=true; if(!g_raiz_details_open) return;
      g_record_read_requested=true;
      JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return;
     }
   if(sparam==JPWActionObject(JPW_ACTION_DECLARE) && g_raiz_tab<=JPW_ROUTE_BIND)
      { JPWRaizSwitchTab(JPW_ROUTE_DECLARE); return; }
   if(sparam==JPWActionObject(JPW_ACTION_BIND) && g_raiz_tab<=JPW_ROUTE_BIND)
      { JPWRaizSwitchTab(JPW_ROUTE_BIND); return; }
   if(sparam==JPWActionObject(JPW_ACTION_LEGACY_PREVIOUS) || sparam==JPWActionObject(JPW_ACTION_LEGACY_NEXT))
     {
      JPWRaizSaveVisibleFields();
      const int delta=(sparam==JPWActionObject(JPW_ACTION_LEGACY_PREVIOUS) ? -1 : 1);
      g_raiz_page=JPWPanelClamp(g_raiz_page+delta,0,g_raiz_pages-1);
      JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0); return;
     }
   if(sparam==JPWActionObject(JPW_ACTION_LEGACY_APPLY))
     {
      if(g_raiz_tab==JPW_ROUTE_DECLARE) JPWRaizSwitchTab(JPW_ROUTE_JUSTIFY);
      else if(g_raiz_tab==JPW_ROUTE_JUSTIFY) JPWRaizApply();
      else if(g_raiz_tab==JPW_ROUTE_BIND) JPWRaizBindTicket();
      else if(g_raiz_tab==JPW_ROUTE_LEGACY_NF) JPWLiveApply();
      else if(g_raiz_tab==JPW_ROUTE_FACTOR) JPWFactorApply();
      else JPWRaizSwitchTab(JPW_ROUTE_FACTOR);
      return;
     }
   if(sparam==JPWActionObject(JPW_ACTION_COMPARE) && g_raiz_tab<=JPW_ROUTE_BIND)
      { JPWRaizRecordComparison(); return; }
   if(sparam==JPWActionObject(JPW_ACTION_LEGACY_CANCEL))
     {
      JPWSignalClear(); g_raiz_details_open=false; JPWUIRelease(g_panel_prefix); g_raiz_draft_account_known=false;
      g_raiz_draft_expected_id=""; JPWRaizPanelDestroy(); ChartRedraw(0);
     }
  }
#endif

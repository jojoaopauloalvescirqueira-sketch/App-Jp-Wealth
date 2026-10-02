#ifndef JPW_SIGNALCOPY_CONTROLLER_MQH
#define JPW_SIGNALCOPY_CONTROLLER_MQH
// Transient message workflow. Financial reads and explicit TXT writes run only
// on the timer, never inside render/navigation. No financial record is changed.
#include <JPWealth/JPW_SignalCopy_Core.mqh>
#include <JPWealth/JPW_SignalCopy_Terminal.mqh>
#define JPW_SIGNAL_ROUTE 16
#define JPW_SIGNAL_UPDATE 101
#define JPW_SIGNAL_POSITIONS 102
#define JPW_SIGNAL_PENDING_LIST 103
#define JPW_SIGNAL_CONFIRM 104
#define JPW_SIGNAL_PREPARE 105
#define JPW_SIGNAL_SAVE 106
#define JPW_SIGNAL_BACK 107
#define JPW_SIGNAL_FOCUS_TEXT 108
#define JPW_SIGNAL_ROLE_APPLY 109
#define JPW_SIGNAL_ROLE_CANCEL 110
#define JPW_SIGNAL_INFO 111
#define JPW_SIGNAL_ROW_FIRST 200
#define JPW_SIGNAL_INCLUDE_FIRST 240
#define JPW_SIGNAL_ROLE_FIRST 280
#define JPW_SIGNAL_FOLDER "JPWealth\\SignalCopy"
void JPWRaizSwitchTab(const int tab);
void JPWSignalRenderBody(const int x,const int y,const int width,const int height,const int footer);

JPWSignalCapture g_signal_capture;
JPWSignalRow g_signal_rows[];
JPWSignalMember g_signal_members[];
JPWSignalMetrics g_signal_metrics;
JPW_SIGNAL_STAGE g_signal_stage=JPW_SIGNAL_SELECT;
int g_signal_selected=-1,g_signal_kind=JPW_SIGNAL_POSITION,g_signal_select_requested=-1;
bool g_signal_known=false,g_signal_stale=false;
bool g_signal_catalog_requested=false,g_signal_preview_requested=false;
bool g_signal_prepare_requested=false,g_signal_export_requested=false;
int g_signal_requested_kind=0,g_signal_role_edit=-1;
string g_signal_role_draft="";
bool g_signal_show_notice=false;
ulong g_signal_requested_ticket=0;
long g_signal_requested_identifier=0;
ulong g_signal_last_check=0,g_signal_export_sequence=0,g_signal_preview_started=0;
string g_signal_message="",g_signal_notice="Selecione uma posição ou pendente.",g_signal_reference_notice="";
int g_signal_button_rows[32],g_signal_button_count=0;
int g_signal_button_members[32],g_signal_member_count=0;

void JPWSignalClear()
  {
   JPWSignalTerminalReset();
   ArrayResize(g_signal_rows,0); ArrayResize(g_signal_members,0);
   JPWSignalClearMetrics(g_signal_metrics);
   g_signal_known=false; g_signal_stale=false; g_signal_selected=-1;
   g_signal_message=""; g_signal_reference_notice="";
   g_signal_role_edit=-1; g_signal_role_draft=""; g_signal_show_notice=false;
   g_signal_catalog_requested=false; g_signal_preview_requested=false;
   g_signal_prepare_requested=false; g_signal_export_requested=false;
   g_signal_requested_ticket=0; g_signal_requested_identifier=0; g_signal_requested_kind=0;
   g_signal_stage=JPW_SIGNAL_SELECT; g_signal_last_check=0; g_signal_select_requested=-1;
  }

void JPWSignalSuspend()
  {
   g_signal_catalog_requested=false; g_signal_select_requested=-1; g_signal_preview_started=0;
   g_signal_preview_requested=false; g_signal_prepare_requested=false; g_signal_export_requested=false;
  }

void JPWSignalInvalidate(const string reason)
  {
   // A changed catalogue may not leave a selectable stale signal behind.
   g_signal_stale=true; g_signal_message="";
   g_signal_prepare_requested=false; g_signal_export_requested=false;
   g_signal_notice="Prévia inválida: "+reason+" Atualize a leitura e confira novamente.";
  }

void JPWSignalRedraw()
  {
   if(!g_raiz_details_open || g_raiz_tab!=JPW_SIGNAL_ROUTE) return;
   JPWRaizPanelDestroy(); JPWRenderRaizDetails(); ChartRedraw(0);
  }

void JPWSignalOpen(const int kind=0,const ulong ticket=0,const long identifier=0)
  {
   JPWSignalClear();
   g_signal_requested_kind=kind; g_signal_requested_ticket=ticket;
   g_signal_requested_identifier=identifier;
   g_signal_catalog_requested=true;
   g_signal_notice="Leitura solicitada. O catálogo não depende do EA observador.";
   JPWRaizSwitchTab(JPW_SIGNAL_ROUTE);
  }

bool JPWSignalSetSelected(const int selected,const ulong started)
  {
   if(selected<0 || selected>=ArraySize(g_signal_rows)) return(false);
   g_signal_selected=selected; g_signal_kind=g_signal_rows[selected].kind;
   g_signal_message=""; g_signal_reference_notice="";
   int reference_row=-1; long reference_identifier=0; bool closed=false; string reason="";
   if(!JPWSignalReadReference(g_signal_capture,g_signal_rows,selected,InpGenesisTicket,
                             reference_row,reference_identifier,closed,reason,started))
     {
      // Unreadable records cannot be silently replaced with an oldest-item inference.
      g_signal_reference_notice="Referência não confirmada: "+reason;
      reference_identifier=-1;
     }
   else if(closed) g_signal_reference_notice="Gênese registrada encerrada; nenhuma sucessora promovida.";
   g_signal_capture.reference_closed=closed;
   g_signal_capture.reference_identifier=reference_identifier;
   string suggestion="";
   if(!JPWSignalSuggestMembers(g_signal_rows,selected,reference_identifier,closed,
                               g_signal_members,suggestion))
      g_signal_notice="Confira manualmente os papéis: "+suggestion;
   else g_signal_notice="Confira a tese, os itens e os papéis. A confirmação vale só para esta mensagem.";
   if(g_signal_reference_notice!="") g_signal_notice+=" "+g_signal_reference_notice;
   g_signal_stage=JPW_SIGNAL_STRUCTURE; g_cockpit_page=0;
   return(true);
  }

bool JPWSignalExportText(string &reason)
  {
   reason="";
   if(g_signal_stale || g_signal_message=="") { reason="Texto indisponível; prepare novamente."; return(false); }
   uchar bytes[];
   int count=StringToCharArray(g_signal_message,bytes,0,WHOLE_ARRAY,CP_UTF8);
   if(count<2) { reason="Conversão UTF-8 falhou."; return(false); }
   count--; // StringToCharArray adds NUL, which is not part of the message.
   if(count>1048576) { reason="Texto excede o limite de 1 MiB; nenhum trecho foi exportado."; return(false); }
   const long observed=(long)TimeGMT();
   if(observed<=0) { reason="Relógio do computador indisponível."; return(false); }
   FolderCreate("JPWealth"); FolderCreate(JPW_SIGNAL_FOLDER);
   g_signal_export_sequence++;
   const string path=JPW_SIGNAL_FOLDER+"\\signal-"+IntegerToString(observed)+"-"+
      StringFormat("%I64d",ChartID())+"-"+StringFormat("%I64u",GetTickCount64())+"-"+
      StringFormat("%I64u",g_signal_export_sequence)+".txt";
   if(FileIsExist(path)) { reason="Nome local já existe; nenhuma mensagem foi substituída."; return(false); }
   int file=FileOpen(path,FILE_WRITE|FILE_BIN);
   if(file==INVALID_HANDLE) { reason="Não foi possível abrir o arquivo local."; return(false); }
   const uint written=FileWriteArray(file,bytes,0,count);
   FileFlush(file); FileClose(file);
   if((int)written!=count) { reason="Escrita incompleta; exportação não confirmada."; FileDelete(path); return(false); }
   file=FileOpen(path,FILE_READ|FILE_BIN);
   if(file==INVALID_HANDLE) { reason="Arquivo escrito, mas releitura não confirmada: MQL5/Files/"+path; return(false); }
   const long size=(long)FileSize(file);
   uchar verified[]; ArrayResize(verified,count);
   const uint read=FileReadArray(file,verified,0,count); FileClose(file);
   bool valid=(size==count && (int)read==count);
   for(int i=0;i<count && valid;i++) if(verified[i]!=bytes[i]) valid=false;
   if(!valid) { FileDelete(path); reason="Releitura divergente; exportação recusada."; return(false); }
   reason="Texto local gravado e relido: MQL5/Files/"+path;
   return(true);
  }

void JPWSignalProcessRequests(const ulong started)
  {
   bool changed=false; string reason="";
   if(g_signal_known)
     {
      JPWAccount account;
      if(!JPWReadAccount(account) || !JPWAccountsEqual(account,g_signal_capture.account))
        { JPWSignalInvalidate("conta alterada ou indisponível."); g_signal_known=false; changed=true; }
     }
   if(g_signal_catalog_requested && GetTickCount64()-started<500)
     {
      g_signal_catalog_requested=false;
      g_signal_message=""; g_signal_known=false; g_signal_stale=true;
      g_signal_selected=-1; ArrayResize(g_signal_members,0);
      JPWSignalCapture capture; JPWSignalRow rows[];
      const bool collected=JPWSignalCollect(capture,rows,reason,started);
      const int row_count=ArraySize(rows);
      if(collected && ArrayResize(g_signal_rows,row_count)==row_count)
        {
         // Exact replacement is required when positions close. Do not use
         // ArrayCopy: it does not shrink and these rows contain a string.
         for(int i=0;i<row_count;i++) g_signal_rows[i]=rows[i];
         g_signal_capture=capture;
         g_signal_known=true; g_signal_stale=false;
         g_signal_stage=JPW_SIGNAL_SELECT; g_cockpit_page=0;
         g_signal_notice="Selecione um item. Posições e pendentes têm catálogos separados.";
         if(g_signal_requested_ticket>0)
           {
            int found=-1;
            for(int i=0;i<ArraySize(rows);i++)
               if(rows[i].kind==g_signal_requested_kind && rows[i].ticket==g_signal_requested_ticket &&
                  (g_signal_requested_identifier==0 || rows[i].identifier==g_signal_requested_identifier)) found=i;
            if(found>=0) JPWSignalSetSelected(found,started);
            else g_signal_notice="O item não está mais no catálogo atual. Selecione outro; a amostra Stops não foi reutilizada.";
           }
        }
      else
        {
         ArrayResize(g_signal_rows,0);
         if(collected) reason="Memória insuficiente para substituir o catálogo completo";
         g_signal_notice="Catálogo indisponível: "+reason;
        }
      changed=true;
     }
   if(g_signal_select_requested>=0 && GetTickCount64()-started<500)
     {
      const int selected=g_signal_select_requested; g_signal_select_requested=-1;
      if(g_signal_known && !g_signal_stale) JPWSignalSetSelected(selected,started);
      changed=true;
     }
   if(g_signal_preview_requested && GetTickCount64()-started<500)
     {
      g_signal_preview_requested=false; g_signal_message="";
      JPWSignalClearMetrics(g_signal_metrics);
      if(!g_signal_known || g_signal_stale || g_signal_selected<0)
         g_signal_notice="Atualize o catálogo antes de gerar a prévia.";
      else if(!JPWSignalRenewCapture(g_signal_capture,g_signal_rows,reason,started))
         JPWSignalInvalidate(reason);
      else
        {
         bool calculated=false; int steps=0;
         if(g_signal_preview_started==0) g_signal_preview_started=GetTickCount64();
         do
           { calculated=JPWSignalCollectMetrics(g_signal_capture,g_signal_rows,
                              g_signal_selected,g_signal_metrics,reason,started); steps++; }
         while(!calculated && JPWSignalAdapterDeferred() && steps<4 &&
               GetTickCount64()-started<450);
         if(!calculated && JPWSignalAdapterDeferred() &&
            GetTickCount64()-g_signal_preview_started<25000)
           { g_signal_preview_requested=true;
             g_signal_notice="Apuração pendente: catálogo cambial ou orçamento. Continuação automática limitada pelo timer.";
             JPWSignalRedraw(); return; }
         g_signal_preview_started=0;
         string blocked="";
         if(calculated && JPWSignalMessage(g_signal_capture,g_signal_rows,g_signal_selected,
                                          g_signal_members,g_signal_metrics,g_signal_message,blocked))
            g_signal_notice="Prévia congelada. Confira o texto e prepare após a revalidação.";
         else g_signal_notice="Preparação bloqueada: "+(blocked!="" ? blocked : reason)+
                     " SL, alavancagem, Raiz N e flutuante completos são obrigatórios.";
         g_signal_stage=JPW_SIGNAL_PREVIEW; g_cockpit_page=0;
        }
      changed=true;
     }
   if((g_signal_prepare_requested || g_signal_export_requested) && GetTickCount64()-started<500)
     {
      const bool exporting=g_signal_export_requested;
      g_signal_prepare_requested=false; g_signal_export_requested=false;
      if(!g_signal_known || g_signal_stale || g_signal_message=="") g_signal_notice="Preparação bloqueada; atualize e confira a prévia.";
      else if(!JPWSignalRevalidate(g_signal_capture,g_signal_rows,reason,started)) JPWSignalInvalidate(reason);
      else if(!JPWSignalCanPrepare(g_signal_capture,g_signal_rows,g_signal_selected,
                                    g_signal_members,g_signal_metrics,reason)) JPWSignalInvalidate(reason);
      else if(exporting) JPWSignalExportText(g_signal_notice);
      else { g_signal_stage=JPW_SIGNAL_TEXT; g_signal_notice="Selecione o texto e use Ctrl+C. A cópia integral ainda exige validação nativa; não há confirmação automática."; g_cockpit_page=0; }
      changed=true;
     }
   // Composition checks never rewrite a frozen message or refresh its prices.
   if(g_signal_known && !g_signal_stale && g_signal_stage>=JPW_SIGNAL_PREVIEW &&
      GetTickCount64()-g_signal_last_check>=5000 && GetTickCount64()-started<500)
     {
      g_signal_last_check=GetTickCount64();
      if(!JPWSignalRevalidate(g_signal_capture,g_signal_rows,reason,started,false))
        { JPWSignalInvalidate(reason); changed=true; }
     }
   if(changed) JPWSignalRedraw();
  }
#endif

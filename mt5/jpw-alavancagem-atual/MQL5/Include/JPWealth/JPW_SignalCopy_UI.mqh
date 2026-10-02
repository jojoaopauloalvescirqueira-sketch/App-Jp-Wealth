#ifndef JPW_SIGNALCOPY_UI_MQH
#define JPW_SIGNALCOPY_UI_MQH
// Presentation only. Clicks enqueue work; no terminal collection or file writes.
string JPWSignalTicket(const ulong ticket) { return(StringFormat("%I64u",ticket)); }

void JPWSignalFooter(const int x,const int width,const int footer,
                      const int first,const string first_text,
                      const int second,const string second_text)
  {
   const int button=(width-2*g_details_pad)/3;
   JPWRaizCreateButton(first,first_text,x,footer,button);
   JPWRaizCreateButton(second,second_text,x+button+g_details_pad,footer,button);
   JPWRaizCreateButton(JPW_ACTION_CLOSE,"Fechar",x+2*(button+g_details_pad),footer,button);
  }

void JPWSignalPager(const int x,const int width,const int footer,const int pages)
  {
   const int button=(width>180 ? 40 : 24);
   JPWRaizCreateButton(JPW_SIGNAL_INFO,"Estado · "+IntegerToString(g_cockpit_page+1)+"/"+
                       IntegerToString(pages),x,footer-g_details_line,width-2*button-2*g_details_pad);
   ObjectSetInteger(0,JPWActionObject(JPW_SIGNAL_INFO),OBJPROP_YSIZE,g_details_line);
   ObjectSetString(0,JPWActionObject(JPW_SIGNAL_INFO),OBJPROP_TOOLTIP,g_signal_notice);
   JPWRaizCreateButton(JPW_ACTION_PREVIOUS,"‹",x+width-2*button-g_details_pad,
                       footer-g_details_line,button);
   JPWRaizCreateButton(JPW_ACTION_NEXT,"›",x+width-button,footer-g_details_line,button);
   ObjectSetInteger(0,JPWActionObject(JPW_ACTION_PREVIOUS),OBJPROP_YSIZE,g_details_line);
   ObjectSetInteger(0,JPWActionObject(JPW_ACTION_NEXT),OBJPROP_YSIZE,g_details_line);
  }

void JPWSignalWrappedPage(const string text,const int x,const int y,
                          const int width,const int height,const int footer)
  {
   string raw[]; string lines[]; StringSplit(text,'\n',raw);
   for(int i=0;i<ArraySize(raw);i++)
     {
      if(raw[i]=="") { const int n=ArraySize(lines); ArrayResize(lines,n+1); lines[n]=""; }
      else JPWDetailsWrap(raw[i],width,lines);
     }
   const int capacity=(height/g_details_line>0 ? height/g_details_line : 1);
   const int pages=(ArraySize(lines)+capacity-1)/capacity;
   g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,(pages>0 ? pages-1 : 0));
   for(int i=0;i<capacity && g_cockpit_page*capacity+i<ArraySize(lines);i++)
      JPWRaizCreateLabel("SIGNAL_LINE_"+IntegerToString(i),lines[g_cockpit_page*capacity+i],x,y+i*g_details_line);
   JPWSignalPager(x,width,footer,(pages>0 ? pages : 1));
  }

bool JPWSignalCopyField(const int x,const int y,const int width,const int height)
  {
   if(width<1 || height<g_details_control || g_signal_message=="" || g_signal_stale) return(false);
   const string name=JPWRaizUI("EDIT_SIGNAL_COPY");
   if(ObjectFind(0,name)<0 && !ObjectCreate(0,name,OBJ_EDIT,0,0,0)) return(false);
   const bool made=ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER) &&
      ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x) && ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y) &&
      ObjectSetInteger(0,name,OBJPROP_XSIZE,width) && ObjectSetInteger(0,name,OBJPROP_YSIZE,height) &&
      ObjectSetInteger(0,name,OBJPROP_COLOR,g_details_text) && ObjectSetInteger(0,name,OBJPROP_BGCOLOR,g_details_card) &&
      ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,g_details_border) &&
      ObjectSetInteger(0,name,OBJPROP_FONTSIZE,g_details_font) && ObjectSetInteger(0,name,OBJPROP_READONLY,true) &&
      ObjectSetInteger(0,name,OBJPROP_ZORDER,5) && ObjectSetInteger(0,name,OBJPROP_HIDDEN,true) &&
      ObjectSetString(0,name,OBJPROP_FONT,"Arial") && ObjectSetString(0,name,OBJPROP_TEXT,g_signal_message) &&
      ObjectSetString(0,name,OBJPROP_TOOLTIP,"Texto inteiro; clique, selecione e use Ctrl+C. Cópia multilinha ainda não validada no MT5.");
   // This verifies the object property, not the OS clipboard or its multiline UI.
   if(!made || ObjectGetString(0,name,OBJPROP_TEXT)!=g_signal_message)
     { ObjectDelete(0,name); return(false); }
   return(true);
  }

void JPWSignalSaveDraft()
  {
   const string object=JPWRaizUI("EDIT_SIGNAL_ROLE");
   if(g_signal_role_edit>=0 && ObjectFind(0,object)>=0)
      g_signal_role_draft=ObjectGetString(0,object,OBJPROP_TEXT);
  }

bool JPWSignalRoleInput(int &role)
  {
   string value=g_signal_role_draft; StringTrimLeft(value); StringTrimRight(value);
   if(value=="" || StringLen(value)>3) return(false);
   for(int i=0;i<StringLen(value);i++)
      if(StringGetCharacter(value,i)<'0' || StringGetCharacter(value,i)>'9') return(false);
   const long defense=StringToInteger(value);
   if(defense<0 || defense>=JPW_SIGNAL_MAX_ROWS) return(false);
   role=(int)defense+1; return(true);
  }

void JPWSignalRoleEditor(const int x,const int y,const int width,const int height,const int footer)
  {
   const string name=JPWRaizUI("EDIT_SIGNAL_ROLE");
   const bool room=(height>=g_details_line+g_details_control);
   if(room) JPWRaizCreateLabel("SIGNAL_ROLE_HINT","0 = Gênese; 1 = Defesa 1; 2 = Defesa 2…",x,y);
   if(ObjectFind(0,name)<0) ObjectCreate(0,name,OBJ_EDIT,0,0,0);
   ObjectSetInteger(0,name,OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSetInteger(0,name,OBJPROP_XDISTANCE,x); ObjectSetInteger(0,name,OBJPROP_YDISTANCE,y+(room ? g_details_line : 0));
   ObjectSetInteger(0,name,OBJPROP_XSIZE,width); ObjectSetInteger(0,name,OBJPROP_YSIZE,g_details_control);
   ObjectSetInteger(0,name,OBJPROP_COLOR,g_details_text); ObjectSetInteger(0,name,OBJPROP_BGCOLOR,g_details_card);
   ObjectSetInteger(0,name,OBJPROP_BORDER_COLOR,g_details_border); ObjectSetInteger(0,name,OBJPROP_FONTSIZE,g_details_font);
   ObjectSetInteger(0,name,OBJPROP_READONLY,false); ObjectSetInteger(0,name,OBJPROP_ZORDER,5);
   ObjectSetString(0,name,OBJPROP_FONT,"Arial"); ObjectSetString(0,name,OBJPROP_TEXT,g_signal_role_draft);
   ObjectSetString(0,name,OBJPROP_TOOLTIP,"Digite 0 para Gênese, ou o número da Defesa (1–511). Papel só para a mensagem; registro financeiro preservado.");
   JPWSignalPager(x,width,footer,1);
   JPWSignalFooter(x,width,footer,JPW_SIGNAL_ROLE_APPLY,"Aplicar papel",JPW_SIGNAL_ROLE_CANCEL,"Cancelar");
  }

void JPWSignalRenderBody(const int x,const int y,const int width,const int height,const int footer)
  {
   g_signal_button_count=0; g_signal_member_count=0;
   if(g_signal_show_notice)
     { JPWSignalWrappedPage(g_signal_notice,x,y,width,height,footer);
       JPWSignalFooter(x,width,footer,JPW_SIGNAL_INFO,"Voltar",JPW_SIGNAL_UPDATE,"Atualizar leitura"); return; }
   if(g_signal_role_edit>=0)
     { JPWSignalRoleEditor(x,y,width,height,footer); return; }
   const string steps[4]={"1 · Selecionar","2 · Conferir estrutura","3 · Gerar prévia","4 · Preparar texto"};
   const bool compact=(height<2*g_details_control+4*g_details_line+g_details_pad);
   const int notice_y=y+g_details_line;
   if(!compact)
     { JPWRaizCreateLabel("SIGNAL_STAGE",steps[(int)g_signal_stage],x,y,g_details_font+1);
       JPWRaizCreateLabel("SIGNAL_NOTICE",g_signal_notice,x,notice_y); }
   const int top=(compact ? y : notice_y+g_details_line+g_details_pad);
   const int available=height-(top-y);
   if(g_signal_stage==JPW_SIGNAL_SELECT)
     {
      const int half=(width-g_details_pad)/2;
      if(!compact)
        { JPWRaizCreateButton(JPW_SIGNAL_POSITIONS,(g_signal_kind==JPW_SIGNAL_POSITION ? "✓ Posições" : "Posições"),x,top,half);
          JPWRaizCreateButton(JPW_SIGNAL_PENDING_LIST,(g_signal_kind==JPW_SIGNAL_PENDING ? "✓ Pendentes" : "Pendentes"),x+half+g_details_pad,top,half); }
      const int row_y=(compact ? top : top+g_details_control+g_details_pad);
      const int stride=(compact ? g_details_control : g_details_control+g_details_line+g_details_pad);
      const int capacity=JPWPanelClamp((available-(compact ? 0 : g_details_control+g_details_pad))/stride,1,32);
      int indices[];
      for(int i=0;i<ArraySize(g_signal_rows);i++)
         if(g_signal_rows[i].kind==g_signal_kind)
           { const int n=ArraySize(indices); ArrayResize(indices,n+1); indices[n]=i; }
      const int pages=(ArraySize(indices)+capacity-1)/capacity;
      g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,(pages>0 ? pages-1 : 0));
      if(ArraySize(indices)==0)
         JPWRaizCreateLabel("SIGNAL_EMPTY",g_signal_known ? "Nenhum item neste catálogo." : "Atualize para obter o catálogo atual.",x,row_y);
      for(int j=0;j<capacity && g_cockpit_page*capacity+j<ArraySize(indices);j++)
        {
         const int index=indices[g_cockpit_page*capacity+j]; JPWSignalRow row=g_signal_rows[index];
         const int py=row_y+j*stride;
         if(py+g_details_control>y+height) break;
         g_signal_button_rows[j]=index; g_signal_button_count=j+1;
         JPWRaizCreateButton(JPW_SIGNAL_ROW_FIRST+j,row.symbol+" · "+(row.side==POSITION_TYPE_BUY ? "Buy" : "Sell")+
                             " · "+JPWSignalTicket(row.ticket),x,py,width);
         if(!compact && py+g_details_control+g_details_line<=y+height)
            JPWCreateProtectedValue("SIGNAL_VOLUME_"+IntegerToString(j),DoubleToString(row.volume,row.volume_digits)+
                                 " lote · "+JPWSignalOrderTypeText(row),x,py+g_details_control,width);
        }
      JPWSignalPager(x,width,footer,(pages>0 ? pages : 1));
      JPWSignalFooter(x,width,footer,JPW_SIGNAL_UPDATE,"Atualizar",
         (compact ? (g_signal_kind==JPW_SIGNAL_POSITION ? JPW_SIGNAL_PENDING_LIST : JPW_SIGNAL_POSITIONS) : JPW_SIGNAL_BACK),
         (compact ? (g_signal_kind==JPW_SIGNAL_POSITION ? "Pendentes" : "Posições") : "Visão geral"));
      return;
     }
   if(!g_signal_known || g_signal_selected<0 || g_signal_stale)
     {
      JPWSignalWrappedPage(g_signal_notice,x,top,width,available,footer);
      JPWSignalFooter(x,width,footer,JPW_SIGNAL_UPDATE,"Atualizar",JPW_SIGNAL_BACK,"Voltar"); return;
     }
   if(g_signal_stage==JPW_SIGNAL_STRUCTURE)
     {
      const bool netting=(g_signal_capture.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);
      if(compact)
        {
         // In small space a member has separate facts/include/role pages.
         // Actions remain reachable; no control is placed over the footer.
         const int pages=(ArraySize(g_signal_members)>0 ? 5*ArraySize(g_signal_members) : 1);
         g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,pages-1);
         const int index=g_cockpit_page/5,part=g_cockpit_page%5;
         if(index<ArraySize(g_signal_members))
           {
            JPWSignalMember member=g_signal_members[index]; JPWSignalRow row=g_signal_rows[member.row];
            g_signal_button_members[0]=index; g_signal_member_count=1;
            if(part<3)
              {
               const string value=(part==0 ? (string)(row.kind==JPW_SIGNAL_PENDING ? "Pendente" : "Posição")+
                     " · "+row.symbol+" · "+(row.side==POSITION_TYPE_BUY ? "Buy" : "Sell") :
                   (part==1 ? "Ticket: "+JPWSignalTicket(row.ticket) :
                              "Volume: "+DoubleToString(row.volume,row.volume_digits)+" lote"));
               JPWCreateProtectedValue("SIGNAL_MEMBER_FACT",value,x,top,width);
              }
            else JPWRaizCreateButton((part==3 ? JPW_SIGNAL_INCLUDE_FIRST : JPW_SIGNAL_ROLE_FIRST),
                 (part==3 ? (member.included ? "✓ Incluir nesta operação" : "○ Excluir: outra tese") :
                  JPWSignalRoleText(member,netting)+(netting ? "" : " · alterar")),x,top,width);
           }
         JPWSignalPager(x,width,footer,pages);
         JPWSignalFooter(x,width,footer,JPW_SIGNAL_BACK,"Voltar",JPW_SIGNAL_CONFIRM,"Conferir e gerar prévia"); return;
        }
      const int stride=2*g_details_control+2*g_details_line+g_details_pad;
      const int capacity=JPWPanelClamp(available/stride,1,32);
      const int pages=(ArraySize(g_signal_members)+capacity-1)/capacity;
      g_cockpit_page=JPWPanelClamp(g_cockpit_page,0,(pages>0 ? pages-1 : 0));
      for(int j=0;j<capacity && g_cockpit_page*capacity+j<ArraySize(g_signal_members);j++)
        {
         const int index=g_cockpit_page*capacity+j;
         JPWSignalMember member=g_signal_members[index]; JPWSignalRow row=g_signal_rows[member.row];
         const int py=top+j*stride;
         if(py+2*g_details_control+2*g_details_line>y+height) break;
         g_signal_button_members[j]=index; g_signal_member_count=j+1;
         JPWRaizCreateLabel("SIGNAL_ITEM_"+IntegerToString(j),(string)(row.kind==JPW_SIGNAL_PENDING ? "Pendente" : "Posição")+
                             " · "+row.symbol+" · "+JPWSignalTicket(row.ticket),x,py);
         JPWCreateProtectedValue("SIGNAL_MEMBER_VOLUME_"+IntegerToString(j),
                       DoubleToString(row.volume,row.volume_digits)+" lote",x,py+g_details_line,width);
         JPWRaizCreateButton(JPW_SIGNAL_INCLUDE_FIRST+j,(member.included ? "✓ Incluir nesta operação" : "○ Excluir: outra tese"),
                             x,py+2*g_details_line,width);
         JPWRaizCreateButton(JPW_SIGNAL_ROLE_FIRST+j,JPWSignalRoleText(member,netting)+
                             (netting ? "" : " · alterar"),x,py+2*g_details_line+g_details_control,width);
        }
      JPWSignalPager(x,width,footer,(pages>0 ? pages : 1));
      JPWSignalFooter(x,width,footer,JPW_SIGNAL_BACK,"Voltar",JPW_SIGNAL_CONFIRM,"Conferir e gerar prévia"); return;
     }
   if(g_signal_stage==JPW_SIGNAL_TEXT)
     {
      const bool field=JPWSignalCopyField(x,top,width,available);
      if(!field) JPWSignalWrappedPage("Campo de cópia indisponível; cópia integral não confirmada.\n"+g_signal_message,
                                      x,top,width,available,footer);
      JPWSignalPager(x,width,footer,1);
      JPWSignalFooter(x,width,footer,JPW_SIGNAL_BACK,"Ver prévia",JPW_SIGNAL_SAVE,"Salvar texto local"); return;
     }
   JPWSignalWrappedPage(g_signal_message=="" ? g_signal_notice : g_signal_message,x,top,width,available,footer);
   JPWSignalFooter(x,width,footer,JPW_SIGNAL_BACK,"Conferir estrutura",JPW_SIGNAL_PREPARE,"Preparar texto");
  }

bool JPWSignalHandleClick(const string object)
  {
   if(g_raiz_tab!=JPW_SIGNAL_ROUTE) return(false);
   if(object==JPWActionObject(JPW_ACTION_PREVIOUS) || object==JPWActionObject(JPW_ACTION_NEXT)) return(false);
   for(int i=101;i<320;i++) if(object==JPWActionObject(i)) ObjectSetInteger(0,object,OBJPROP_STATE,false);
   if(object==JPWActionObject(JPW_SIGNAL_INFO))
     { JPWSignalSaveDraft(); g_signal_show_notice=!g_signal_show_notice; g_cockpit_page=0; }
   else if(object==JPWActionObject(JPW_SIGNAL_ROLE_CANCEL))
     { g_signal_role_edit=-1; g_signal_role_draft=""; }
   else if(object==JPWActionObject(JPW_SIGNAL_ROLE_APPLY))
     {
      JPWSignalSaveDraft(); int role=0;
      if(g_signal_role_edit>=0 && g_signal_role_edit<ArraySize(g_signal_members) && JPWSignalRoleInput(role))
        { g_signal_members[g_signal_role_edit].role=role;
          g_signal_members[g_signal_role_edit].origin=JPW_SIGNAL_CONFIRMED;
          g_signal_role_edit=-1; g_signal_role_draft=""; g_signal_message="";
          g_signal_notice="Papel confirmado só para esta mensagem. Confira os demais itens."; }
      else g_signal_notice="Informe 0 para Gênese ou o número inteiro da Defesa (1–511).";
     }
   else if(object==JPWActionObject(JPW_SIGNAL_UPDATE))
     { g_signal_show_notice=false; g_signal_requested_ticket=0; g_signal_requested_identifier=0; g_signal_catalog_requested=true;
       g_signal_select_requested=-1; g_signal_preview_requested=false;
       g_signal_prepare_requested=false; g_signal_export_requested=false;
       JPWSignalInvalidate("atualização solicitada."); g_signal_stage=JPW_SIGNAL_SELECT; }
   else if(object==JPWActionObject(JPW_SIGNAL_POSITIONS) || object==JPWActionObject(JPW_SIGNAL_PENDING_LIST))
     { g_signal_kind=(object==JPWActionObject(JPW_SIGNAL_POSITIONS) ? JPW_SIGNAL_POSITION : JPW_SIGNAL_PENDING);
       g_cockpit_page=0; }
   else if(object==JPWActionObject(JPW_SIGNAL_BACK))
     {
      if(g_signal_stage==JPW_SIGNAL_SELECT) { JPWRaizSwitchTab(JPW_ROUTE_OVERVIEW); return(true); }
      g_signal_message=(g_signal_stage==JPW_SIGNAL_TEXT ? g_signal_message : "");
      g_signal_stage=(g_signal_stage==JPW_SIGNAL_TEXT ? JPW_SIGNAL_PREVIEW :
                     (g_signal_stage==JPW_SIGNAL_PREVIEW ? JPW_SIGNAL_STRUCTURE : JPW_SIGNAL_SELECT));
      g_cockpit_page=0;
     }
   else if(object==JPWActionObject(JPW_SIGNAL_CONFIRM))
     {
      for(int i=0;i<ArraySize(g_signal_members);i++)
         if(g_signal_members[i].included) g_signal_members[i].origin=JPW_SIGNAL_CONFIRMED;
      g_signal_preview_started=0; g_signal_preview_requested=true; g_signal_notice="Conferência aplicada somente à mensagem. Apuração solicitada ao timer.";
     }
   else if(object==JPWActionObject(JPW_SIGNAL_PREPARE))
     { g_signal_prepare_requested=true; g_signal_notice="Revalidação solicitada antes de liberar o texto."; }
   else if(object==JPWActionObject(JPW_SIGNAL_SAVE))
     { g_signal_export_requested=true; g_signal_notice="Exportação local solicitada; catálogo será revalidado."; }
   else
     {
      bool handled=false;
      for(int i=0;i<g_signal_button_count;i++) if(object==JPWActionObject(JPW_SIGNAL_ROW_FIRST+i))
        { g_signal_select_requested=g_signal_button_rows[i]; g_signal_notice="Seleção solicitada; referência será conferida no timer."; handled=true; }
      for(int i=0;i<g_signal_member_count;i++)
        {
         const int index=g_signal_button_members[i];
         if(object==JPWActionObject(JPW_SIGNAL_INCLUDE_FIRST+i))
           {
            if(g_signal_members[index].row==g_signal_selected) g_signal_notice="O item selecionado precisa permanecer incluído.";
            else { g_signal_members[index].included=!g_signal_members[index].included;
                   g_signal_notice="Itens alterados; confira os papéis antes de gerar a prévia."; }
            g_signal_message=""; handled=true;
           }
         if(object==JPWActionObject(JPW_SIGNAL_ROLE_FIRST+i))
           {
            if(g_signal_capture.margin_mode!=ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
               g_signal_notice="Netting: posição agregada; papéis individuais não serão inventados.";
            else { g_signal_role_edit=index;
                   g_signal_role_draft=(g_signal_members[index].role>0 ? IntegerToString(g_signal_members[index].role-1) : "");
                   g_signal_notice="Informe 0 para Gênese ou o número da Defesa. Aplicar confirma; Cancelar descarta."; }
            g_signal_message=""; handled=true;
           }
        }
      if(!handled) return(false);
     }
   JPWSignalRedraw(); return(true);
  }
#endif

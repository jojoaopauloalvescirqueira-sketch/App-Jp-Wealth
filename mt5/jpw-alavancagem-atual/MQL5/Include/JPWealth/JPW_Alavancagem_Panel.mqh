#ifndef JPW_ALAVANCAGEM_PANEL_MQH
#define JPW_ALAVANCAGEM_PANEL_MQH

// Pixel geometry only. Callers supply measured text height/width at current DPI.
// All rectangles and controls are expressed from the chart's top-left corner.
struct JPWPanelRect { int x; int y; int width; int height; bool compact; };
int JPWPanelClamp(const int value,const int low,const int high)
  { return(value<low ? low : (value>high ? high : value)); }

// MQL colors are BGR integers. Keep neutral grays readable on both chart
// themes while retaining the user's input color for a light chart.
bool JPWPanelDarkBackground(const color background)
  {
   const int packed=(int)background;
   const int red=packed&255,green=(packed>>8)&255,blue=(packed>>16)&255;
   return(299*red+587*green+114*blue<140000);
  }
color JPWPanelSurface(const color background)
  { return(JPWPanelDarkBackground(background) ? C'28,31,37' : C'255,255,255'); }
// The HUD retains white on a light chart so the configurable default gray
// still has 4.5:1 contrast. The large window uses the shared NoCuda theme.
color JPWPanelWindowSurface(const color background)
  { return(JPWPanelDarkBackground(background) ? C'28,31,37' : C'247,249,252'); }
color JPWPanelChromeSurface(const color background)
  { return(JPWPanelDarkBackground(background) ? C'39,45,54' : C'233,238,244'); }
color JPWPanelCardSurface(const color background)
  { return(JPWPanelDarkBackground(background) ? C'34,39,47' : C'255,255,255'); }
color JPWPanelBorderColor(const color background)
  { return(JPWPanelDarkBackground(background) ? C'116,124,136' : C'128,135,147'); }
color JPWPanelInk(const color background)
  { return(JPWPanelDarkBackground(background) ? C'232,234,238' : C'39,45,53'); }
color JPWPanelMutedText(const color background)
  { return(JPWPanelDarkBackground(background) ? C'177,182,188' : C'96,103,112'); }
color JPWPanelAccentColor(const color background)
  { return(JPWPanelDarkBackground(background) ? C'151,185,217' : C'48,79,112'); }
color JPWPanelSelectedSurface(const color background)
  { return(JPWPanelDarkBackground(background) ? C'49,59,71' : C'221,232,244'); }
color JPWPanelPrimaryInk(const color background)
  { return(JPWPanelDarkBackground(background) ? C'28,31,37' : C'255,255,255'); }
int JPWPanelBrightness(const color value)
  {
   const int packed=(int)value;
   return((299*(packed&255)+587*((packed>>8)&255)+114*((packed>>16)&255))/1000);
  }
color JPWPanelTextColor(const color background,const color light_theme_text)
  {
   if(!JPWPanelDarkBackground(background)) return(light_theme_text);
   // Respect an Entradas color if it remains distinct from the HUD surface.
   if(JPWPanelBrightness(light_theme_text)-37>=105) return(light_theme_text);
   return(JPWPanelInk(background));
  }

bool JPWPanelHUD(const int chart_width,const int chart_height,
                 const int block_width,const int block_height,
                 const int inset_x,const int inset_y,
                 const bool right,const bool lower,JPWPanelRect &rect)
  {
   if(chart_width<1 || chart_height<1 || block_width<1 || block_height<1) return(false);
   // A clamped container is not proof that its unchanged children fit.
   if(block_width>chart_width || block_height>chart_height) return(false);
   rect.width=block_width;
   rect.height=block_height;
   rect.compact=false;
   rect.x=JPWPanelClamp(right ? chart_width-inset_x-rect.width : inset_x,0,chart_width-rect.width);
   rect.y=JPWPanelClamp(lower ? chart_height-inset_y-rect.height : inset_y,0,chart_height-rect.height);
   return(true);
  }

// Reserve a HUD width from stable presentation inputs. Live prices, quality
// labels and money values must never resize the corner panel on each timer.
int JPWPanelHUDReservedWidth(const int chart_width,const int measured_text_height,
                             const int padding,const int button_width)
  {
   if(chart_width<80 || measured_text_height<1 || padding<0 || button_width<1) return(0);
   const int available=chart_width-16;
   long target=(long)measured_text_height*25+2*padding;
   const long chart_budget=(long)chart_width*45/100;
   if(target>chart_budget) target=chart_budget;
   const int minimum=button_width+2*padding;
   // A clipped container must never leave the Cockpit button outside it.
   if(available<minimum) return(0);
   if(target<minimum) target=minimum;
   return((int)(target<available ? target : available));
  }

bool JPWPanelCockpit(const int chart_width,const int chart_height,
                     const int desired_width,const int desired_height,JPWPanelRect &rect)
  {
   if(chart_width<80 || chart_height<80) return(false);
   const int margin=8;
   rect.width=(desired_width<chart_width-2*margin ? desired_width : chart_width-2*margin);
   rect.height=(desired_height<chart_height-2*margin ? desired_height : chart_height-2*margin);
   rect.x=(chart_width-rect.width)/2;
   rect.y=(chart_height-rect.height)/2;
   rect.compact=(rect.width<420 || rect.height<400);
   return(rect.width>0 && rect.height>0);
  }

bool JPWPanelDialog(const int chart_width,const int chart_height,
                    const int text_height,const int char_width,JPWPanelRect &rect,
                    int &padding,int &line_height,int &control_height,
                    int &content_y,int &content_height,int &footer_y)
  {
   if(chart_width<1 || chart_height<1 || text_height<1 || char_width<1) return(false);
   padding=(text_height/2>4 ? text_height/2 : 4);
   line_height=text_height+padding;
   control_height=text_height+2*padding;
   const int margin=(chart_width>2*padding && chart_height>2*padding ? padding : 0);
   rect.width=(66*char_width+2*padding<chart_width-2*margin ?
               66*char_width+2*padding : chart_width-2*margin);
   rect.height=(22*line_height<chart_height-2*margin ? 22*line_height : chart_height-2*margin);
   rect.x=(chart_width-rect.width)/2;
   rect.y=(chart_height-rect.height)/2;
   content_y=rect.y+2*padding+line_height+2*(control_height+padding);
   footer_y=rect.y+rect.height-padding-control_height;
   content_height=footer_y-padding-2*line_height-content_y;
   rect.compact=(content_height<line_height+control_height+padding);
   if(rect.compact)
     {
      // Keep one navigation row and the footer. No action row or reserved
      // feedback rows: those live in the paged body/title in short charts.
      padding=4;
      line_height=text_height+padding;
      control_height=text_height+2*padding;
      content_y=rect.y+2*padding+line_height+control_height+padding;
      footer_y=rect.y+rect.height-padding-control_height;
      content_height=footer_y-padding-content_y;
     }
   return(rect.width>0 && rect.height>0);
  }

int JPWPanelPageRows(const int available,const int row_height)
  { return(row_height>0 && available>=row_height ? available/row_height : 0); }
int JPWPanelPageCount(const int total,const int rows)
  { return(rows>0 && total>0 ? (total+rows-1)/rows : 1); }

// A position table scrolls within its own viewport; it never changes cockpit
// pages. Compact measured rows avoid one oversized card per position.
struct JPWPositionsLayout
  {
   int summary_height;
   int header_height;
   int row_height;
   int table_offset;
   int visible_rows;
   bool columns;
  };
void JPWPanelPositionsLayout(const int body_height,const int text_height,
                             const bool columns,JPWPositionsLayout &layout)
  {
   layout.summary_height=0; layout.header_height=0; layout.row_height=0;
   layout.table_offset=0; layout.visible_rows=0; layout.columns=columns;
   if(body_height<=0 || text_height<=0) return;
   const int gap=(text_height/12>2 ? text_height/12 : 2);
   layout.summary_height=text_height+gap;
   layout.header_height=(columns ? text_height+gap : 0);
   layout.row_height=(columns ? text_height+gap : 4*(text_height+gap));
   layout.table_offset=layout.summary_height+layout.header_height+gap;
   if(layout.table_offset+layout.row_height>body_height)
     {
      layout.summary_height=0; layout.header_height=0; layout.table_offset=0;
     }
   if(layout.row_height<=body_height-layout.table_offset)
      layout.visible_rows=JPWPanelClamp((body_height-layout.table_offset)/layout.row_height,1,16);
  }

// The Stops table gives a complete row and its detail action precedence over
// optional summary lines. A large measured font must not hide every position.
struct JPWStopsLayout
  {
   int summary_lines;
   int value_lines;
   int table_offset;
   int row_height;
   int rows_per_page;
  };

void JPWPanelStopsLayout(const int body_height,const int line_height,
                         const int control_height,const int padding,
                         const bool horizontal_values,const bool has_rows,
                         JPWStopsLayout &layout)
  {
   layout.summary_lines=0;
   layout.value_lines=0;
   layout.table_offset=0;
   layout.row_height=0;
   layout.rows_per_page=0;
   if(body_height<=0 || line_height<=0 || control_height<=0 || padding<0)
      return;
   if(!has_rows)
     {
      for(int headers=2;headers>=0;headers--)
        {
         const int offset=headers*line_height+(headers>0 ? padding : 0);
         if(offset+line_height>body_height) continue;
         layout.summary_lines=headers;
         layout.table_offset=offset;
         break;
        }
      return;
     }
   // Full values take priority. On an exceptionally short chart the row
   // remains a focusable detail button, with complete values in its detail.
   const int preferred=(horizontal_values ? 1 : 2);
   for(int pass=0;pass<2;pass++)
     {
      const int value_lines=(pass==0 ? preferred : 0);
      for(int headers=3;headers>=0;headers--)
        {
         const int offset=(headers>0 ? headers*line_height+padding : 0);
         const int row_height=control_height+value_lines*line_height+padding;
         const int available=body_height-offset;
         if(available<row_height) continue;
         layout.summary_lines=headers;
         layout.value_lines=value_lines;
         layout.table_offset=offset;
         layout.row_height=row_height;
         layout.rows_per_page=JPWPanelClamp(available/row_height,1,16);
         return;
        }
     }
  }
#endif

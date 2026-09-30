#ifndef JPW_ALAVANCAGEM_GENESIS_CORE_MQH
#define JPW_ALAVANCAGEM_GENESIS_CORE_MQH

// JPW Alavancagem Atual 1.3.0. Selecao e distancia puras: sem conta,
// arquivos, negociacao, grafico ou relogio. O adaptador confirma os dados.

enum JPW_GENESIS_SELECTION
  {
   JPW_GENESIS_SELECT_OK=0,
   JPW_GENESIS_SELECT_NONE,
   JPW_GENESIS_SELECT_NOT_FOUND,
   JPW_GENESIS_SELECT_AMBIGUOUS,
   JPW_GENESIS_SELECT_INVALID
  };

enum JPW_GENESIS_DISTANCE
  {
   JPW_GENESIS_DISTANCE_POSITIVE=0,
   JPW_GENESIS_DISTANCE_REACHED,
   JPW_GENESIS_DISTANCE_PASSED,
   JPW_GENESIS_DISTANCE_NO_SL,
   JPW_GENESIS_DISTANCE_INVALID
  };

struct JPWGenesisPosition
  {
   ulong ticket;
   long identifier;
   string symbol;
   long direction;
   long opened_msc;
   double sl;
   double volume;
   long updated_msc;
  };

void JPWGenesisClear(JPWGenesisPosition &position)
  {
   position.ticket=0;
   position.identifier=0;
   position.symbol="";
   position.direction=-1;
   position.opened_msc=0;
   position.sl=0.0;
   position.volume=0.0;
   position.updated_msc=0;
  }

bool JPWGenesisPositionIdentityValid(JPWGenesisPosition &position)
  {
   return(position.ticket>0 && position.identifier>0 &&
          position.symbol!="" && position.opened_msc>0 &&
          (position.direction==POSITION_TYPE_BUY ||
           position.direction==POSITION_TYPE_SELL));
  }

// Selector 0: only one exact (symbol,direction) group and a unique oldest
// opening instant. A missing time or a tie never promotes an arbitrary ticket.
// Positive selector: match the currently open ticket exactly.
JPW_GENESIS_SELECTION JPWGenesisSelect(JPWGenesisPosition &positions[],
                                       const ulong requested_ticket,
                                       JPWGenesisPosition &chosen)
  {
   JPWGenesisClear(chosen);
   const int count=ArraySize(positions);
   if(count<=0) return(JPW_GENESIS_SELECT_NONE);
   if(requested_ticket>0)
     {
      int match=-1;
      for(int i=0;i<count;i++)
        {
         if(positions[i].ticket!=requested_ticket) continue;
         if(match>=0) return(JPW_GENESIS_SELECT_AMBIGUOUS);
         match=i;
        }
      if(match<0) return(JPW_GENESIS_SELECT_NOT_FOUND);
      if(!JPWGenesisPositionIdentityValid(positions[match]))
         return(JPW_GENESIS_SELECT_INVALID);
      chosen=positions[match];
      return(JPW_GENESIS_SELECT_OK);
     }
   const string symbol=positions[0].symbol;
   const long direction=positions[0].direction;
   int oldest=-1;
   long oldest_time=0;
   bool tie=false;
   for(int i=0;i<count;i++)
     {
      if(!JPWGenesisPositionIdentityValid(positions[i]))
         return(JPW_GENESIS_SELECT_INVALID);
      if(positions[i].symbol!=symbol || positions[i].direction!=direction)
         return(JPW_GENESIS_SELECT_AMBIGUOUS);
      if(oldest<0 || positions[i].opened_msc<oldest_time)
        {
         oldest=i;
         oldest_time=positions[i].opened_msc;
         tie=false;
        }
      else if(positions[i].opened_msc==oldest_time)
         tie=true;
     }
   if(oldest<0 || tie) return(JPW_GENESIS_SELECT_AMBIGUOUS);
   chosen=positions[oldest];
   return(JPW_GENESIS_SELECT_OK);
  }

// The identifier survives a partial close and, on some netting accounts,
// even a reversal. Return the current position without accepting a duplicate.
// The caller must compare symbol/direction with the saved reference.
bool JPWGenesisFindByIdentifier(JPWGenesisPosition &positions[],
                                const long identifier,
                                JPWGenesisPosition &found)
  {
   JPWGenesisClear(found);
   if(identifier<=0) return(false);
   int match=-1;
   for(int i=0;i<ArraySize(positions);i++)
     {
      if(positions[i].identifier!=identifier) continue;
      if(match>=0 || !JPWGenesisPositionIdentityValid(positions[i]))
         return(false);
      match=i;
     }
   if(match<0) return(false);
   found=positions[match];
   return(true);
  }

// For BUY Q=Bid and D=Bid-SL; for SELL Q=Ask and D=SL-Ask.
// The sign is classified before formatting. The zero tolerance is far below
// one tick, solely to absorb floating point subtraction noise.
JPW_GENESIS_DISTANCE JPWGenesisDistance(const long direction,
                                        const double bid,const double ask,
                                        const double sl,const double point,
                                        const int digits,const double tick_size,
                                        const string symbol,
                                        const string pip_symbol,
                                        const double pip_size,
                                        double &distance,double &points,
                                        double &percent,double &pips,
                                        bool &has_pips)
  {
   distance=0.0;
   points=0.0;
   percent=0.0;
   pips=0.0;
   has_pips=false;
   if(direction!=POSITION_TYPE_BUY && direction!=POSITION_TYPE_SELL)
      return(JPW_GENESIS_DISTANCE_INVALID);
   if(!MathIsValidNumber(sl) || sl<0.0)
      return(JPW_GENESIS_DISTANCE_INVALID);
   if(sl==0.0) return(JPW_GENESIS_DISTANCE_NO_SL);
   if(symbol=="" || digits<0 || digits>16 ||
      !MathIsValidNumber(bid) || bid<=0.0 ||
      !MathIsValidNumber(ask) || ask<=0.0 || bid>ask ||
      !MathIsValidNumber(point) || point<=0.0 ||
      !MathIsValidNumber(tick_size) || tick_size<=0.0)
      return(JPW_GENESIS_DISTANCE_INVALID);
   const double price=(direction==POSITION_TYPE_BUY ? bid : ask);
   const double raw=(direction==POSITION_TYPE_BUY ? price-sl : sl-price);
   if(!MathIsValidNumber(raw)) return(JPW_GENESIS_DISTANCE_INVALID);
   const double tolerance=tick_size*1e-8;
   if(!MathIsValidNumber(tolerance) || tolerance<=0.0)
      return(JPW_GENESIS_DISTANCE_INVALID);
   if(MathAbs(raw)<=tolerance) return(JPW_GENESIS_DISTANCE_REACHED);
   if(raw<0.0) return(JPW_GENESIS_DISTANCE_PASSED);
   const double calc_points=raw/point;
   const double calc_percent=100.0*(raw/price);
   if(!MathIsValidNumber(calc_points) || calc_points<=0.0 ||
      !MathIsValidNumber(calc_percent) || calc_percent<=0.0)
      return(JPW_GENESIS_DISTANCE_INVALID);
   distance=raw;
   points=calc_points;
   percent=calc_percent;
   // A configuracao de pip e exclusivamente opt-in por simbolo exato. A
   // ausencia de pip valido nao invalida a distancia em pontos e percentual.
   if(pip_symbol==symbol && MathIsValidNumber(pip_size) &&
      pip_size>=point && pip_size>=tick_size)
     {
      const double ticks_per_pip=pip_size/tick_size;
      const double calc_pips=raw/pip_size;
      if(MathIsValidNumber(ticks_per_pip) &&
         MathAbs(ticks_per_pip-MathRound(ticks_per_pip))<=
         1e-8*MathMax(1.0,ticks_per_pip) &&
         MathIsValidNumber(calc_pips) && calc_pips>0.0)
        {
         pips=calc_pips;
         has_pips=true;
        }
     }
   return(JPW_GENESIS_DISTANCE_POSITIVE);
  }

#endif

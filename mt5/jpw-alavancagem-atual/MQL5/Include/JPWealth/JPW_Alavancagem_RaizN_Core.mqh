#ifndef JPW_ALAVANCAGEM_RAIZN_CORE_MQH
#define JPW_ALAVANCAGEM_RAIZN_CORE_MQH

// JPW Alavancagem Atual 1.4.0. Calculo diagnostico puro da Raiz N.
// Entradas e saidas de preco usam a unidade de cotacao do mesmo simbolo.
// O percentual e expresso em pontos percentuais: 2.0 significa 2% de P0.
// Esta unidade nao muda em contas USC. Nada aqui le conta, grafico ou arquivo.

enum JPW_RAIZN_RESULT
  {
   JPW_RAIZN_OK=0,
   JPW_RAIZN_BAD_P0,
   JPW_RAIZN_BAD_ATR,
   JPW_RAIZN_BAD_N,
   JPW_RAIZN_BAD_F,
   JPW_RAIZN_CALC_ERROR
  };

// Intencionalmente diferente dos valores de ENUM_POSITION_TYPE do MT5.
// O adaptador deve converter o tipo da posicao explicitamente.
enum JPW_RAIZN_SIDE
  {
   JPW_RAIZN_SIDE_NONE=0,
   JPW_RAIZN_SIDE_BUY=1,
   JPW_RAIZN_SIDE_SELL=-1
  };

enum JPW_RAIZN_SL_RESULT
  {
   JPW_RAIZN_SL_OK=0,
   JPW_RAIZN_SL_NO_SL,
   JPW_RAIZN_SL_AT_P0,
   JPW_RAIZN_SL_PROTECTED,
   JPW_RAIZN_SL_INVALID
  };

// Uncalibrated temporal scale. It is deliberately not a Raiz N distance:
// the latter additionally requires an institutionally approved F. Keep this
// API separate so callers cannot present an implicit F=1 as an approval.
JPW_RAIZN_RESULT JPWRaizNTimeScale(const double p0,const double atr,
                                   const int n,double &distance_price,
                                   double &distance_percent)
  {
   distance_price=0.0;
   distance_percent=0.0;
   if(!MathIsValidNumber(p0) || p0<=0.0) return(JPW_RAIZN_BAD_P0);
   if(!MathIsValidNumber(atr) || atr<=0.0) return(JPW_RAIZN_BAD_ATR);
   if(n<=0) return(JPW_RAIZN_BAD_N);
   const double price=atr*MathSqrt((double)n);
   const double percent=100.0*(price/p0);
   if(!MathIsValidNumber(price) || price<=0.0 ||
      !MathIsValidNumber(percent) || percent<=0.0)
      return(JPW_RAIZN_CALC_ERROR);
   distance_price=price;
   distance_percent=percent;
   return(JPW_RAIZN_OK);
  }

// Dpreco = ATR * sqrt(N) * F; D% = 100 * Dpreco / P0.
// N e uma contagem inteira de candles H4 declarada pelo operador; o periodo
// ATR(55) e outro conceito e nao pode ser usado como N implicitamente.
// Outputs so sao utilizaveis quando o retorno e JPW_RAIZN_OK.
JPW_RAIZN_RESULT JPWRaizNCalculate(const double p0,const double atr,
                                   const int n,const double f,
                                   double &distance_price,
                                   double &distance_percent)
  {
   distance_price=0.0;
   distance_percent=0.0;
   if(!MathIsValidNumber(p0) || p0<=0.0) return(JPW_RAIZN_BAD_P0);
   if(!MathIsValidNumber(atr) || atr<=0.0) return(JPW_RAIZN_BAD_ATR);
   if(n<=0) return(JPW_RAIZN_BAD_N);
   if(!MathIsValidNumber(f) || f<=0.0) return(JPW_RAIZN_BAD_F);

   const double root_n=MathSqrt((double)n);
   const double scaled_atr=atr*root_n;
   if(!MathIsValidNumber(root_n) || root_n<=0.0 ||
      !MathIsValidNumber(scaled_atr) || scaled_atr<=0.0)
      return(JPW_RAIZN_CALC_ERROR);
   const double price=scaled_atr*f;
   const double ratio=price/p0;
   const double percent=100.0*ratio;
   if(!MathIsValidNumber(price) || price<=0.0 ||
      !MathIsValidNumber(ratio) || ratio<=0.0 ||
      !MathIsValidNumber(percent) || percent<=0.0)
      return(JPW_RAIZN_CALC_ERROR);
   distance_price=price;
   distance_percent=percent;
   return(JPW_RAIZN_OK);
  }

// A barra H4 precisa ter encerrado no instante de referencia. O adaptador
// ainda deve comprovar serie sincronizada, ATR(55) calculado para essa barra
// e ausencia de barras fechadas mais recentes ate a referencia. Nao usar
// TimeCurrent() para reinterpretar retrospectivamente a barra declarada.
bool JPWRaizNBarClosedBy(const datetime bar_open,
                         const datetime reference_time)
  {
   if(bar_open<=0 || reference_time<=0 || reference_time<=bar_open)
      return(false);
   const long elapsed=(long)reference_time-(long)bar_open;
   return(elapsed>=4*60*60);
  }

// Compara somente um SL adverso a P0 com a distancia diagnostica da Raiz N.
// Um SL em P0 ou protegendo lucro recebe estado proprio, sem comparacao
// artificial com distancia adversa. Gap positivo = SL mais distante que D.
// Outputs so sao utilizaveis quando o retorno e JPW_RAIZN_SL_OK.
JPW_RAIZN_SL_RESULT JPWRaizNCompareSL(const JPW_RAIZN_SIDE side,
                                      const double p0,const double sl,
                                      const double distance_price,
                                      double &sl_adverse_price,
                                      double &sl_adverse_percent,
                                      double &gap_price,
                                      double &gap_percent)
  {
   sl_adverse_price=0.0;
   sl_adverse_percent=0.0;
   gap_price=0.0;
   gap_percent=0.0;
   if(side!=JPW_RAIZN_SIDE_BUY && side!=JPW_RAIZN_SIDE_SELL)
      return(JPW_RAIZN_SL_INVALID);
   if(!MathIsValidNumber(p0) || p0<=0.0 ||
      !MathIsValidNumber(sl) || sl<0.0 ||
      !MathIsValidNumber(distance_price) || distance_price<=0.0)
      return(JPW_RAIZN_SL_INVALID);
   if(sl==0.0) return(JPW_RAIZN_SL_NO_SL);

   const double adverse=(side==JPW_RAIZN_SIDE_BUY ? p0-sl : sl-p0);
   if(!MathIsValidNumber(adverse)) return(JPW_RAIZN_SL_INVALID);
   if(adverse==0.0) return(JPW_RAIZN_SL_AT_P0);
   if(adverse<0.0) return(JPW_RAIZN_SL_PROTECTED);

   const double percent=100.0*(adverse/p0);
   const double delta=adverse-distance_price;
   const double delta_percent=100.0*(delta/p0);
   if(!MathIsValidNumber(percent) || percent<=0.0 ||
      !MathIsValidNumber(delta) || !MathIsValidNumber(delta_percent))
      return(JPW_RAIZN_SL_INVALID);
   sl_adverse_price=adverse;
   sl_adverse_percent=percent;
   gap_price=delta;
   gap_percent=delta_percent;
   return(JPW_RAIZN_SL_OK);
  }

#endif

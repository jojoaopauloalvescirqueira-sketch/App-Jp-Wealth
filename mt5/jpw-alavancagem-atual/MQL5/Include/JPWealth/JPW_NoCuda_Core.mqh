#ifndef JPW_NOCUDA_CORE_MQH
#define JPW_NOCUDA_CORE_MQH

// Geometria pura dos canais NoCuda. j e o ordinal de uma barra do periodo-fonte,
// nao um numero de horas nem o indice do periodo exibido no grafico.
// Convencao AB0_C1_BARS_V1: A/B pertencem ao nivel 0 e C ao nivel 1.
struct JPWNoCudaGeometry
  {
   long origin_ordinal;
   double origin_price;
   double slope;
   double signed_offset;
   double width;
   double subdivision;
  };

void JPWNoCudaClearGeometry(JPWNoCudaGeometry &geometry)
  {
   geometry.origin_ordinal=0;
   geometry.origin_price=0.0;
   geometry.slope=0.0;
   geometry.signed_offset=0.0;
   geometry.width=0.0;
   geometry.subdivision=0.0;
  }

// reason e um codigo estavel para a camada de apresentacao traduzir.
bool JPWNoCudaBuildGeometry(const long jA,const double pA,
                           const long jB,const double pB,
                           const long jC,const double pC,
                           JPWNoCudaGeometry &geometry,string &reason)
  {
   JPWNoCudaClearGeometry(geometry);
   reason="";
   // 2^53-1 e o maior ordinal inteiro representavel exatamente em double.
   const long MAX_EXACT_ORDINAL=9007199254740991;
   if(jA<0 || jB<0 || jC<0 || jA>MAX_EXACT_ORDINAL ||
      jB>MAX_EXACT_ORDINAL || jC>MAX_EXACT_ORDINAL)
     {
      reason="INVALID_ORDINAL";
      return(false);
     }
   if(jA==jB)
     {
      reason="SAME_AB_BAR";
      return(false);
     }
   if(!MathIsValidNumber(pA) || !MathIsValidNumber(pB) ||
      !MathIsValidNumber(pC))
     {
      reason="INVALID_CLOSE";
      return(false);
     }

   // Faz a subtracao depois da conversao para evitar overflow de long.
   const double delta_j=(double)jB-(double)jA;
   const double slope=(pB-pA)/delta_j;
   const double principal_at_c=pA+slope*((double)jC-(double)jA);
   const double signed_offset=pC-principal_at_c;
   const double width=MathAbs(signed_offset);
   const double subdivision=width/8.0;
   if(!MathIsValidNumber(slope) || !MathIsValidNumber(principal_at_c) ||
      !MathIsValidNumber(signed_offset) || !MathIsValidNumber(width) ||
      !MathIsValidNumber(subdivision))
     {
      reason="NONFINITE_GEOMETRY";
      return(false);
     }
   if(width==0.0 || subdivision==0.0)
     {
      reason="ZERO_WIDTH";
      return(false);
     }
   geometry.origin_ordinal=jA;
   geometry.origin_price=pA;
   geometry.slope=slope;
   geometry.signed_offset=signed_offset;
   geometry.width=width;
   geometry.subdivision=subdivision;
   return(true);
  }

// k=0..64 gera, inclusive, -4,-3.875,...,0,...,0.5,...,1,...,4.
bool JPWNoCudaLevelValue(const int k,double &level)
  {
   level=0.0;
   if(k<0 || k>64) return(false);
   level=-4.0+(double)k/8.0;
   return(true);
  }

// Ordinal fracionario permite projetar um instante entre aberturas consecutivas
// sem converter o canal para inclinacao em horas civis.
bool JPWNoCudaPriceAt(const JPWNoCudaGeometry &geometry,
                     const double level,const double ordinal,double &price)
  {
   price=0.0;
   if(!MathIsValidNumber(level) || !MathIsValidNumber(ordinal) ||
      !MathIsValidNumber(geometry.origin_price) ||
      !MathIsValidNumber(geometry.slope) ||
      !MathIsValidNumber(geometry.signed_offset) ||
      geometry.width<=0.0 || !MathIsValidNumber(geometry.width)) return(false);
   const double computed=geometry.origin_price+
                         geometry.slope*(ordinal-(double)geometry.origin_ordinal)+
                         level*geometry.signed_offset;
   if(!MathIsValidNumber(computed)) return(false);
   price=computed;
   return(true);
  }

// As duas aberturas devem ser adjacentes na sequencia real de candles-fonte.
// A funcao nao supoe duracao fixa nem cria uma barra dentro de lacunas.
bool JPWNoCudaInterpolateOrdinal(const datetime left_open,
                                const datetime right_open,
                                const datetime target_time,
                                const long left_ordinal,double &ordinal)
  {
   ordinal=0.0;
   if(left_open<=0 || right_open<=left_open || left_ordinal<0 ||
      left_ordinal>=9007199254740991 ||
      target_time<left_open || target_time>right_open) return(false);
   const double fraction=((double)target_time-(double)left_open)/
                         ((double)right_open-(double)left_open);
   const double projected=(double)left_ordinal+fraction;
   if(!MathIsValidNumber(projected)) return(false);
   ordinal=projected;
   return(true);
  }

#endif // JPW_NOCUDA_CORE_MQH

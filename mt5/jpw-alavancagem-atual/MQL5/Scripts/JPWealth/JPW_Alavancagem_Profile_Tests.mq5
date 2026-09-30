#property copyright "JP Wealth"
#property version   "1.10"
#property script_show_inputs
#property description "Testes sinteticos do perfil USC; nao le conta nem envia ordens."

#include <JPWealth/JPW_Alavancagem_Profile.mqh>

int g_profile_checks=0;
int g_profile_failures=0;

void JPWProfileAssert(const bool condition,const string label)
  {
   g_profile_checks++;
   if(condition) return;
   g_profile_failures++;
   Print("JPW perfil teste falhou: ",label);
  }

bool JPWProfileTestEntry(const string symbol,const string specification,
                         const double scale,const datetime verified,
                         JPWProfileEntry &entry)
  {
   entry.scale=scale;
   entry.verified_at=verified;
   return(JPWProfileHash(symbol,entry.symbol_hash) &&
          JPWProfileHash(specification,entry.spec_hash));
  }

void JPWProfileTestCodec()
  {
   string known="";
   JPWProfileAssert(JPWProfileHash("abc",known) &&
                    known=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                    "SHA-256 padrao");
   JPWAccount account;
   account.login=123456;
   account.server="SYNTHETIC-ONLY-TEST";
   account.currency="USC";
   string key="";
   JPWProfileAssert(JPWProfileAccountHash(account,key) &&
                    JPWProfileIsHash(key),"chave da conta");
   JPWAccount other=account;
   other.login=123457;
   string other_key="";
   JPWProfileAssert(JPWProfileAccountHash(other,other_key) &&
                    key!=other_key,"identidade de conta diferente");
   JPWProfileEntry entries[];
   ArrayResize(entries,2);
   JPWProfileAssert(JPWProfileTestEntry("EURUSD","spec-a",1.0,
                                        (datetime)2000000000,entries[0]) &&
                    JPWProfileTestEntry("XAUUSD","spec-b",0.01,
                                        (datetime)2000000001,entries[1]),
                    "entradas sinteticas");
   string encoded="";
   JPWProfileAssert(JPWProfileEncode(key,7,entries,encoded),"codifica");
   JPWProfileAssert(StringFind(encoded,account.server)<0 &&
                    StringFind(encoded,"ACCOUNT|"+IntegerToString(account.login))<0 &&
                    StringFind(encoded,"EURUSD")<0 &&
                    StringFind(encoded,"XAUUSD")<0,
                    "sem identidade bruta ou simbolos em disco");
   JPWProfileEntry decoded[];
   long generation=0;
   JPWProfileAssert(JPWProfileDecode(encoded,key,decoded,generation) &&
                    generation==7 && ArraySize(decoded)==2 &&
                    decoded[0].scale==1.0 && decoded[1].scale==0.01 &&
                    decoded[1].spec_hash==entries[1].spec_hash,
                    "ida e volta versionada");
   JPWProfileAssert(!JPWProfileDecode(encoded,other_key,decoded,generation),
                    "conta errada recusada");
   string damaged=encoded;
   StringReplace(damaged,"GEN|7","GEN|8");
   JPWProfileAssert(!JPWProfileDecode(damaged,key,decoded,generation),
                    "checksum recusa alteracao");
   damaged=encoded;
   StringReplace(damaged,"JPWLEVERAGE_PROFILE|1","JPWLEVERAGE_PROFILE|2");
   JPWProfileAssert(!JPWProfileDecode(damaged,key,decoded,generation),
                    "schema desconhecido recusado");
   entries[1].symbol_hash=entries[0].symbol_hash;
   JPWProfileAssert(!JPWProfileEncode(key,8,entries,encoded),
                    "simbolo duplicado recusado");
   entries[1].symbol_hash=other_key;
   entries[1].scale=0.1;
   JPWProfileAssert(!JPWProfileEncode(key,8,entries,encoded),
                    "escala fora da allowlist recusada");
  }

void JPWProfileTestFileRecovery()
  {
   JPWAccount account;
   account.login=123456;
   account.server="SYNTHETIC-ONLY-"+IntegerToString((long)ChartID())+"-"+
                  IntegerToString((long)GetTickCount64());
   account.currency="USC";
   string key="";
   if(!JPWProfileAccountHash(account,key))
     { JPWProfileAssert(false,"hash da fixture local"); return; }
   const string first=JPW_PROFILE_FOLDER+key+".a";
   const string second=JPW_PROFILE_FOLDER+key+".b";
   const string lockfile=JPW_PROFILE_FOLDER+key+".lock";
   // Nunca remover arquivo que existia antes deste teste, mesmo no improvavel
   // caso de colisao de identidade sintetica.
   if(FileIsExist(first) || FileIsExist(second) || FileIsExist(lockfile))
     { JPWProfileAssert(false,"fixture isolada livre"); return; }
   JPWProfileEntry entries[];
   ArrayResize(entries,1);
   JPWProfileAssert(JPWProfileTestEntry("NZDUSD","contract-1",1.0,
                                        (datetime)2000000000,entries[0]),
                    "entrada para escrita");
   JPWProfileAssert(JPWProfileSave(account,entries),"primeira geracao salva");
   JPWProfileEntry readback[];
   long generation=0;
   int active=-1;
   JPWProfileAssert(JPWProfileLoadState(account,readback,generation,active)==
                    JPW_PROFILE_VALID && generation==1 && active==0 &&
                    ArraySize(readback)==1 && readback[0].scale==1.0,
                    "primeira geracao relida");
   entries[0].scale=0.01;
   entries[0].verified_at=(datetime)2000000001;
   JPWProfileAssert(JPWProfileSave(account,entries),"segunda geracao salva");
   JPWProfileAssert(JPWProfileLoadState(account,readback,generation,active)==
                    JPW_PROFILE_VALID && generation==2 && active==1 &&
                    readback[0].scale==0.01,
                    "segunda geracao relida");
   // Simula slot novo truncado; o slot anterior deve permanecer legivel.
   JPWProfileAssert(JPWProfileWriteText(second,"partial"),
                    "injecao de escrita parcial");
   JPWProfileAssert(JPWProfileLoadState(account,readback,generation,active)==
                    JPW_PROFILE_VALID && generation==1 && active==0 &&
                    readback[0].scale==1.0,
                    "fallback ao slot anterior");
   entries[0].scale=1.0;
   entries[0].verified_at=(datetime)2000000002;
   JPWProfileAssert(JPWProfileSave(account,entries),
                    "reparo sem apagar ultimo valido");
   JPWProfileAssert(JPWProfileLoadState(account,readback,generation,active)==
                    JPW_PROFILE_VALID && generation==2 && active==1,
                    "slot reparado confirmado");
   JPWProfileEntry stale[];
   ArrayResize(stale,1);
   stale[0]=entries[0];
   stale[0].scale=0.01;
   stale[0].verified_at=(datetime)2000000001;
   JPWProfileAssert(!JPWProfileSave(account,stale),
                    "verificacao velha divergente recusada");
   JPWProfileAssert(JPWProfileLoadState(account,readback,generation,active)==
                    JPW_PROFILE_VALID && generation==2 && active==1 &&
                    readback[0].scale==1.0,
                    "conflito velho preserva geracao confirmada");
   const int held=FileOpen(lockfile,FILE_READ|FILE_WRITE|FILE_BIN);
   JPWProfileAssert(held!=INVALID_HANDLE,"lock exclusivo disponivel");
   if(held!=INVALID_HANDLE)
     {
      JPWProfileAssert(!JPWProfileSave(account,entries),
                       "segunda escrita sob lock recusada");
      FileClose(held);
     }
   JPWProfileAssert(JPWProfileLoadState(account,readback,generation,active)==
                    JPW_PROFILE_VALID && generation==2 && active==1,
                    "lock preserva perfil confirmado");
   // Mesmo numero de geracao e payloads distintos sao ambiguidade irredutivel.
   JPWProfileEntry conflict[];
   ArrayResize(conflict,1);
   conflict[0]=entries[0];
   conflict[0].scale=0.01;
   string divergent="";
   JPWProfileAssert(JPWProfileEncode(key,2,conflict,divergent) &&
                    JPWProfileWriteText(first,divergent),
                    "injecao de empate divergente");
   JPWProfileAssert(JPWProfileLoadState(account,readback,generation,active)==
                    JPW_PROFILE_INVALID,"empate divergente recusado");
   JPWProfileAssert(!JPWProfileSave(account,entries),
                    "save nao supera perfil ambiguo");
   // O teste remove somente seus tres arquivos de hash sintetico exclusivo.
   JPWProfileAssert(FileDelete(first),"limpeza slot a");
   JPWProfileAssert(FileDelete(second),"limpeza slot b");
   JPWProfileAssert(FileDelete(lockfile),"limpeza lock");
  }

void OnStart()
  {
   JPWProfileTestCodec();
   JPWProfileTestFileRecovery();
   Print("JPW Alavancagem Profile Tests: ",g_profile_checks,
         " verificacoes, ",g_profile_failures," falhas. ",
         (g_profile_failures==0 ? "PASS" : "FAIL"));
  }

#ifndef JPW_ALAVANCAGEM_OBSERVER_PRESENCE_MQH
#define JPW_ALAVANCAGEM_OBSERVER_PRESENCE_MQH

#include <JPWealth/JPW_Alavancagem_RaizN_Store.mqh>
#include <JPWealth/JPW_Alavancagem_Version.mqh>

// Diagnostic only: this signal never validates a Stop risk amount. Each EA
// instance owns one temporary terminal variable, scoped by the exact product
// version, opaque account (including terminal data path) and publisher token.
// Temporary variables disappear when the terminal exits; the monotonic time
// rejects an EA that stopped responding without a clean OnDeinit.
#define JPW_OBSERVER_PRESENCE_PREFIX "JPWOP1_"
#define JPW_OBSERVER_PRESENCE_AGE_MS 30000
#define JPW_OBSERVER_PRESENCE_VERSION_HEX 8
#define JPW_OBSERVER_PRESENCE_ACCOUNT_HEX 24
#define JPW_OBSERVER_PRESENCE_PUBLISHER_HEX 20
#define JPW_OBSERVER_PRESENCE_RADIX 8

enum JPWObserverPresenceState
  {
   JPW_OBSERVER_NOT_CONFIRMED=0,
   JPW_OBSERVER_WAITING=1,
   JPW_OBSERVER_PUBLISHED=2,
   JPW_OBSERVER_FAILED=3,
   // Presentation-only state when no account identity could be established.
   // It is never encoded into a terminal variable by the EA.
   JPW_OBSERVER_CONTEXT_UNAVAILABLE=4
  };

string JPWObserverPresencePrefixForVersion(const string account_key,
                                           const string product_version)
  {
   string version_hash="";
   if(!JPWRaizNIsHash(account_key) || product_version=="" ||
      !JPWRaizNHash(product_version,version_hash)) return("");
   return(JPW_OBSERVER_PRESENCE_PREFIX+
          StringSubstr(version_hash,0,JPW_OBSERVER_PRESENCE_VERSION_HEX)+"_"+
          StringSubstr(account_key,0,JPW_OBSERVER_PRESENCE_ACCOUNT_HEX)+"_");
  }

string JPWObserverPresencePrefix(const string account_key)
  {
   return(JPWObserverPresencePrefixForVersion(account_key,
                                              JPW_PRODUCT_VERSION));
  }

string JPWObserverPresenceNameForVersion(const string account_key,
                                         const string publisher_token,
                                         const string product_version)
  {
   const string prefix=JPWObserverPresencePrefixForVersion(account_key,
                                                            product_version);
   if(prefix=="" || !JPWRaizNIsHash(publisher_token)) return("");
   return(prefix+StringSubstr(publisher_token,0,
                             JPW_OBSERVER_PRESENCE_PUBLISHER_HEX));
  }

string JPWObserverPresenceName(const string account_key,
                               const string publisher_token)
  {
   return(JPWObserverPresenceNameForVersion(account_key,publisher_token,
                                            JPW_PRODUCT_VERSION));
  }

bool JPWObserverPresenceEncode(const ulong monotonic_ms,
                               const JPWObserverPresenceState state,
                               double &encoded)
  {
   encoded=0.0;
   // Doubles represent all integers up to 2^53 exactly. Reserve three bits
   // for the typed state and refuse impossible monotonic clock values.
   if(monotonic_ms==0 || monotonic_ms>1125899906842623 ||
      state<JPW_OBSERVER_WAITING || state>JPW_OBSERVER_FAILED)
      return(false);
   encoded=(double)(monotonic_ms*JPW_OBSERVER_PRESENCE_RADIX+
                    (ulong)state);
   return(true);
  }

bool JPWObserverPresenceDecodeAt(const double encoded,const ulong now_ms,
                                 JPWObserverPresenceState &state)
  {
   state=JPW_OBSERVER_NOT_CONFIRMED;
   if(!MathIsValidNumber(encoded) || encoded<0.0 ||
      encoded>9007199254740991.0 || now_ms==0) return(false);
   const ulong packed=(ulong)encoded;
   if((double)packed!=encoded) return(false);
   const int code=(int)(packed%JPW_OBSERVER_PRESENCE_RADIX);
   const ulong observed_ms=packed/JPW_OBSERVER_PRESENCE_RADIX;
   if(code<(int)JPW_OBSERVER_WAITING || code>(int)JPW_OBSERVER_FAILED ||
      observed_ms==0 || now_ms<observed_ms ||
      now_ms-observed_ms>JPW_OBSERVER_PRESENCE_AGE_MS) return(false);
   state=(JPWObserverPresenceState)code;
   return(true);
  }

// The EA retains the exact value it wrote. A failed CAS can be retried only
// while that value still occupies the marker; another writer's value is never
// adopted as our own merely because the variable name still exists.
bool JPWObserverPresenceBeatOwned(const string account_key,
                                  const string publisher_token,
                                  const JPWObserverPresenceState state,
                                  double &owned_value)
  {
   const string name=JPWObserverPresenceName(account_key,publisher_token);
   double next=0.0;
   if(name=="" || !MathIsValidNumber(owned_value) || owned_value<0.0 ||
      !JPWObserverPresenceEncode(GetTickCount64(),state,next) ||
      !GlobalVariableSetOnCondition(name,next,owned_value)) return(false);
   owned_value=next;
   return(true);
  }

bool JPWObserverPresenceMarkerMatches(const string account_key,
                                      const string publisher_token,
                                      const double owned_value)
  {
   const string name=JPWObserverPresenceName(account_key,publisher_token);
   double current=0.0;
   return(name!="" && owned_value>0.0 && GlobalVariableGet(name,current) &&
          current==owned_value);
  }

bool JPWObserverPresenceStartOwned(const string account_key,
                                   const string publisher_token,
                                   double &owned_value)
  {
   owned_value=0.0;
   const string name=JPWObserverPresenceName(account_key,publisher_token);
   if(name=="") return(false);
   // A prior owned release leaves an invalid zero tombstone in the same
   // temporary variable. Claim it by CAS rather than deleting/recreating it.
   if(!GlobalVariableCheck(name) && !GlobalVariableTemp(name))
      return(false);
   double current=0.0;
   if(!GlobalVariableGet(name,current) || current!=0.0) return(false);
   return(JPWObserverPresenceBeatOwned(account_key,publisher_token,
                                       JPW_OBSERVER_WAITING,owned_value));
  }

void JPWObserverPresenceReleaseOwned(const string account_key,
                                     const string publisher_token,
                                     const double owned_value)
  {
   const string name=JPWObserverPresenceName(account_key,publisher_token);
   if(name!="" && MathIsValidNumber(owned_value) && owned_value>0.0)
      GlobalVariableSetOnCondition(name,0.0,owned_value);
  }

JPWObserverPresenceState JPWObserverPresenceRead(const string account_key)
  {
   const string prefix=JPWObserverPresencePrefix(account_key);
   if(prefix=="") return(JPW_OBSERVER_NOT_CONFIRMED);
   JPWObserverPresenceState best=JPW_OBSERVER_NOT_CONFIRMED;
   const ulong now=GetTickCount64();
   const int count=GlobalVariablesTotal();
   for(int i=0;i<count;i++)
     {
      const string name=GlobalVariableName(i);
      if(StringLen(name)!=StringLen(prefix)+JPW_OBSERVER_PRESENCE_PUBLISHER_HEX ||
         StringFind(name,prefix)!=0) continue;
      double encoded=0.0;
      JPWObserverPresenceState candidate=JPW_OBSERVER_NOT_CONFIRMED;
      if(!GlobalVariableGet(name,encoded) ||
         !JPWObserverPresenceDecodeAt(encoded,now,candidate)) continue;
      // If one instance has published, another waiting/failing instance does
      // not erase that evidence. A valid financial sample is still required.
      if(candidate==JPW_OBSERVER_PUBLISHED) return(candidate);
      if(candidate==JPW_OBSERVER_FAILED) best=candidate;
      else if(best==JPW_OBSERVER_NOT_CONFIRMED) best=candidate;
     }
   return(best);
  }

#endif

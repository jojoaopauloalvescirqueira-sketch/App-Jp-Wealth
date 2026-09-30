#ifndef JPW_ALAVANCAGEM_STORE_RESULT_MQH
#define JPW_ALAVANCAGEM_STORE_RESULT_MQH
// Stable discriminants; localized explanations are presentation only.
enum JPWStoreResult
  {
   JPW_STORE_VALID=0,
   JPW_STORE_ABSENT=1,
   JPW_STORE_BUSY=2,
   JPW_STORE_CORRUPT=3,
   JPW_STORE_INCOMPATIBLE=4,
   JPW_STORE_IO_ERROR=5
  };
#endif

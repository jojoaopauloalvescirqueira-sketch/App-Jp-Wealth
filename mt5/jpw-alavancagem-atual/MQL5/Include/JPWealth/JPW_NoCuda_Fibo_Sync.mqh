#ifndef JPW_NOCUDA_FIBO_SYNC_MQH
#define JPW_NOCUDA_FIBO_SYNC_MQH
enum JPWNCFSyncPhase
  {
   JPW_NCF_FOLLOWING=0,JPW_NCF_EDITING_PREVIEW=1,JPW_NCF_SAVE_PENDING=2,
   JPW_NCF_DETACHED=3,JPW_NCF_SOURCE_INVALID=4,JPW_NCF_SYNC_CONFLICT=5,
   JPW_NCF_PAUSED=6
  };
struct JPWNCFSyncState
  {
   JPWNCFSyncPhase phase;
   string confirmed_digest,preview_digest,finished_digest;
   ulong changed_ms,finished_ms;
   bool finish_requested,mouse_down,armed;
  };
void JPWNCFSyncClear(JPWNCFSyncState &s)
  {
   s.phase=JPW_NCF_DETACHED;s.confirmed_digest="";s.preview_digest="";s.finished_digest="";
   s.changed_ms=0;s.finished_ms=0;s.finish_requested=false;
   s.mouse_down=false;s.armed=false;
  }
void JPWNCFSyncAccept(JPWNCFSyncState &s,const string digest)
  {
   s.confirmed_digest=digest;s.preview_digest=digest;
   s.finish_requested=false;s.finished_digest="";s.phase=(s.armed ? JPW_NCF_FOLLOWING : JPW_NCF_PAUSED);
  }
void JPWNCFSyncObserve(JPWNCFSyncState &s,const string digest,const ulong now)
  {
   if(!s.armed || digest=="") return;
   if(digest!=s.preview_digest)
     { s.preview_digest=digest;s.changed_ms=now;s.phase=JPW_NCF_EDITING_PREVIEW;
       if(s.finished_digest!=digest) { s.finish_requested=false; s.finished_digest=""; } }
  }
void JPWNCFSyncFinished(JPWNCFSyncState &s,const ulong now,const string digest)
  {
   if(!s.armed) return;
   s.finished_digest=digest;
   s.finish_requested=(digest!="" && digest!=s.confirmed_digest);s.finished_ms=now;
  }
bool JPWNCFSyncReady(const JPWNCFSyncState &s,const ulong now)
  {
   return(s.armed && !s.mouse_down && s.finish_requested &&
      s.preview_digest!="" && s.preview_digest!=s.confirmed_digest && s.preview_digest==s.finished_digest &&
      now>=s.changed_ms && now>=s.finished_ms &&
      now-s.changed_ms>=600 && now-s.finished_ms>=600);
  }
void JPWNCFSyncPause(JPWNCFSyncState &s)
  { s.armed=false;s.finish_requested=false;s.finished_digest="";s.phase=JPW_NCF_PAUSED; }
#endif

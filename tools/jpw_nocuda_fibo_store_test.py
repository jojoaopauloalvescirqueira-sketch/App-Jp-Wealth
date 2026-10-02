#!/usr/bin/env python3
"""Exercise the actual DDL/DML extracted from the MQL store in host SQLite.
This validates SQL transactions/CAS/immutable rows, not MT5 database bindings.
"""
from pathlib import Path
import argparse, ast, hashlib, json, re, sqlite3, tempfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Store.mqh'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence-dir');args=ap.parse_args()
    source=SOURCE.read_text();strings=[ast.literal_eval(x) for x in re.findall(r'"(?:[^"\\]|\\.)*"',source)]
    def sql(prefix):
        matches=[x for x in strings if x.startswith(prefix)]
        assert len(matches)==1,(prefix,len(matches));return matches[0]
    checks=[]
    def check(ok,name):
        assert ok,name;checks.append(name)
    def rejects(fn,name):
        try: fn()
        except sqlite3.DatabaseError: checks.append(name);return
        raise AssertionError(name)
    with tempfile.TemporaryDirectory(prefix='jpw-ncf-sql-') as temp:
        path=Path(temp)/'synthetic.sqlite';a=sqlite3.connect(path,timeout=0,isolation_level=None);b=sqlite3.connect(path,timeout=0,isolation_level=None)
        for item in strings:
            if item.startswith('CREATE '): a.execute(item)
        a.execute(sql('INSERT INTO fibo_meta'),(1,'a'*64))
        a.execute('BEGIN IMMEDIATE')
        a.execute(sql('INSERT INTO fibo_revisions('),('study',1,0,'snapshot with actual openings','explicit import',1800000000,'revision1'))
        a.execute(sql('INSERT INTO fibo_heads('),('study',1,1,0,'head1'))
        a.execute('COMMIT')
        check(a.execute(sql('SELECT study_id,generation,revision,paused,checksum'),('study',)).fetchone()==('study',1,1,0,'head1'),'create+read exact head')
        check(a.execute(sql('SELECT study_id,revision,previous_revision,payload,justification,confirmed_utc,checksum'),('study',1)).fetchone()[3]=='snapshot with actual openings','payload retained')
        rejects(lambda:a.execute("UPDATE fibo_revisions SET payload='wrong'"),'revision update rejected')
        rejects(lambda:a.execute('DELETE FROM fibo_revisions'),'revision deletion rejected')
        a.execute('BEGIN IMMEDIATE')
        rejects(lambda:b.execute('BEGIN IMMEDIATE'),'second writer is BUSY without wait')
        a.execute('ROLLBACK')
        a.execute(sql('UPDATE fibo_heads SET'),('study',2,1,1,'should not persist',99))
        check(a.execute('SELECT changes()').fetchone()[0]==0,'stale generation changes zero rows')
        a.execute('BEGIN IMMEDIATE')
        a.execute(sql('INSERT INTO fibo_revisions('),('study',2,1,'snapshot2','gesture finished',1800000001,'revision2'))
        a.execute(sql('UPDATE fibo_heads SET'),('study',2,2,0,'head2',1))
        check(a.execute('SELECT changes()').fetchone()[0]==1,'CAS accepts exact generation')
        a.execute('ROLLBACK')
        check(a.execute('SELECT count(*) FROM fibo_revisions').fetchone()[0]==1,'failed transaction preserves former revision')
        a.execute('BEGIN IMMEDIATE')
        a.execute(sql('INSERT INTO fibo_revisions('),('study',2,1,'snapshot2','gesture finished',1800000001,'revision2'))
        a.execute(sql('UPDATE fibo_heads SET'),('study',2,2,0,'head2',1))
        a.execute('COMMIT')
        a.execute('BEGIN IMMEDIATE')
        a.execute(sql('INSERT INTO fibo_revisions('),('study',3,2,'snapshot with actual openings','restore revision 1',1800000002,'revision3'))
        a.execute(sql('UPDATE fibo_heads SET'),('study',3,3,1,'head3',2));a.execute('COMMIT')
        check(a.execute('SELECT revision,paused FROM fibo_heads').fetchone()==(3,1),'rollback creates new revision and pauses')
        highest=a.execute(sql('SELECT COALESCE(MAX(revision),0)'),('study',)).fetchone()[0]
        check(highest==3,'next revision derives from max')
        a.execute('BEGIN IMMEDIATE')
        a.execute(sql('INSERT INTO fibo_revisions('),('study',highest+1,3,'snapshot4','after rollback',1800000003,'revision4'))
        a.execute(sql('UPDATE fibo_heads SET'),('study',4,4,1,'head4',3));a.execute('COMMIT')
        check(a.execute('SELECT count(*) FROM fibo_revisions').fetchone()[0]==4,'all revisions survive rollback/resume')
        note=(1,'note-id','study',3,4,'observation','manual candle OHLC annotation',1800000000,'checksum')
        a.execute(sql('INSERT OR IGNORE INTO fibo_notes('),note);a.execute(sql('INSERT OR IGNORE INTO fibo_notes('),note)
        check(a.execute('SELECT count(*) FROM fibo_notes').fetchone()[0]==1,'note repetition idempotent')
        rejects(lambda:a.execute("UPDATE fibo_notes SET payload='replacement'"),'note immutable')
        rejects(lambda:a.execute('DELETE FROM fibo_notes'),'note deletion refused')
        a.execute(sql('INSERT OR IGNORE INTO fibo_notes('),(1,'bad','study',3,4,'financial','x',1,'h'))
        check(a.execute('SELECT count(*) FROM fibo_notes').fetchone()[0]==1,'invalid kind not inserted')
        check(a.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity')
        check('nocuda_heads' not in source and 'ACCOUNT_' not in source,'separate namespace no account access')
        check('kind=="projection"' in source and 'return(JPW_NCF_UNVERIFIED_NATIVE)' in source,'projection save guarded')
        check('JPWNCFHeadHash' in source and 'hash!=h.checksum' in source and 'hash!=r.checksum' in source,'head/revision checksum paths present')
        check('BEGIN IMMEDIATE' in source and 'PRAGMA busy_timeout=0' in source,'nonwaiting transaction policy')
        a.close();b.close()
        reopened=sqlite3.connect(path);check(reopened.execute('SELECT generation,revision,paused FROM fibo_heads').fetchone()==(4,4,1),'restart retained head');reopened.close()
        bad=Path(temp)/'bad.sqlite';bad.write_bytes(b'not sqlite')
        corrupt=sqlite3.connect(bad)
        rejects(lambda:corrupt.execute('SELECT name FROM sqlite_master').fetchall(),'corrupt database refused');corrupt.close()
    report={'status':'PASS','checks':len(checks),'results':checks,'scope':'actual production SQL on host sqlite; bindings and native filesystem NOT_RUN','native':'NOT_RUN','sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
    if args.evidence_dir:
        out=Path(args.evidence_dir);out.mkdir(parents=True,exist_ok=True);(out/'fibo-store-sql.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()

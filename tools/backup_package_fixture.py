"""Independent stdlib reader for delivered synthetic backup ZIPs in browser tests.

This is test transport plumbing, not an application parser or recovery path.
Financial/progress oracles inspect decoded content only after this boundary.
"""
from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile


@dataclass
class DeliveredPackage:
    payload: dict
    members: dict
    manifest: dict


def blob_bytes(page, expression):
    """Read a Blob captured at the actual download handoff, never its constructor."""
    return bytes(page.evaluate('async()=>Array.from(new Uint8Array(await ('+expression+').arrayBuffer()))'))


def read_backup_package(source):
    raw=source.read_bytes() if isinstance(source,Path) else bytes(source)
    assert raw.startswith(b'PK\x03\x04'),'delivered backup must be the approved ZIP transport'
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            infos=archive.infolist();names=[row.filename for row in infos]
            assert len(names)==len(set(names)),'delivered ZIP has duplicate member names'
            assert {'manifest.json','backup.json','evidence-manifest.json'}<=set(names),'delivered package misses required members'
            assert all(row.compress_type==zipfile.ZIP_STORED and not row.flag_bits&1 for row in infos),'delivered package must be STORE and unencrypted'
            assert archive.testzip() is None,'delivered ZIP failed independent CRC checks'
            members={name:archive.read(name) for name in names}
    except (zipfile.BadZipFile,RuntimeError) as error:
        raise AssertionError('delivered ZIP unreadable by independent stdlib reader: '+str(error)) from error
    manifest=json.loads(members['manifest.json'].decode('utf-8'))
    assert manifest['format']=='jpwealth_portable_backup' and manifest['formatVersion']==1
    integrity=manifest['integrity'];body={key:value for key,value in manifest.items() if key!='integrity'}
    canonical=json.dumps(body,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    assert integrity['algorithm']=='SHA-256' and integrity['canonicalization']=='JPW_SORTED_JSON_V1'
    assert hashlib.sha256(canonical).hexdigest()==integrity['checksum'],'independent package manifest checksum mismatch'
    entries=manifest['entries'];paths=[entry['path'] for entry in entries]
    assert len(paths)==len(set(paths)) and set(paths)==set(members)-{'manifest.json'},'independent package coverage mismatch'
    for entry in entries:
        content=members[entry['path']]
        assert entry['size']==len(content) and entry['sha256']==hashlib.sha256(content).hexdigest(),'independent package member size/hash mismatch'
    payload=json.loads(members['backup.json'].decode('utf-8'))
    assert payload['tipo']=='jpwealth_full_backup' and payload['formatVersion']==2
    return DeliveredPackage(payload,members,manifest)


def assert_workspace_progress(payload,key,expected_raw):
    workspace=payload['workspace'];preferences=workspace['preferences']
    assert workspace['schemaVersion']==3,'confirmed progress belongs to workspace3'
    assert key in preferences and preferences[key]==expected_raw,'confirmed progress must retain its exact raw snapshot'
    other={**payload,'workspace':{**workspace,'preferences':{k:v for k,v in preferences.items() if k!=key}}}
    assert key not in json.dumps(other),'progress leaked outside its approved workspace preference slot'
    return True


def assert_opaque_progress(payload,key,expected_raw):
    workspace=payload['workspace']
    assert key not in workspace['preferences'],'legacy opaque progress must never be an active preference'
    assert key not in json.dumps(payload['state']),'legacy progress leaked into financial state'
    chunks=[item for item in workspace['drafts'] if key in item.get('label','')]
    assert chunks and all(item.get('provider')=='opaque-preference' and item.get('version')==1 for item in chunks),'legacy progress must be recovered only as opaque consultation text'
    chunks.sort(key=lambda item:int(re.search(r'\(parte (\d+)\)$',item['label']).group(1)))
    assert ''.join(item['text'] for item in chunks)==expected_raw,'opaque legacy bytes must be recoverable exactly'
    return True


def assert_members_absent(members,*markers):
    for marker in markers:
        needle=marker.encode()
        assert all(needle not in content for content in members.values()),'forbidden marker leaked into delivered package: '+marker
    return True


def assert_disk_source(payload,expected,obsolete):
    text=json.dumps(payload['state'])
    assert expected in text,'delivered backup must represent the authoritative disk source'
    assert obsolete not in text,'delivered backup must exclude stale RAM source'
    return True


def expect_assertion(action):
    try:action()
    except AssertionError as error:return str(error)
    raise AssertionError('counterproof failed to reject its deliberate content violation')

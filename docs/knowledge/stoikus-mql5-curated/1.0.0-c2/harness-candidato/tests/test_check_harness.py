import hashlib,json,pathlib,subprocess,sys,tempfile,unittest,runpy
CHECK=pathlib.Path(__file__).resolve().parents[1]/'check_harness.py'
class Verify(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.root=pathlib.Path(self.t.name)
  for n in ('kit','repo','sources'): (self.root/n).mkdir()
  self.k=self.root/'kit'; (self.k/'entry.md').write_text('candidate')
  self.m={'schema_version':1,'version':'0.1.0','status':'CANDIDATE','revision':'R3','state_revision':1,'validation_policy':'MANUAL_CANDIDATE','adoption':'NOT_ADOPTED','native_mt5':'NOT_RUN','behavioral_pilot':'NOT_RUN','files':[{'root':'kit','path':'entry.md','sha256':hashlib.sha256(b'candidate').hexdigest()}],'references':[]}
 def tearDown(self): self.t.cleanup()
 def runcheck(self):
  (self.k/'manifest.json').write_text(json.dumps(self.m))
  return subprocess.run([sys.executable,str(CHECK),'--kit-root',str(self.k),'--repo-root',str(self.root/'repo'),'--sources-root',str(self.root/'sources')],capture_output=True,text=True)
 def test_valid_nonmutation(self):
  r=self.runcheck(); before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}; r=self.runcheck(); self.assertEqual(r.returncode,0,r.stdout+r.stderr); self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
 def test_tamper(self): (self.k/'entry.md').write_text('changed'); self.assertEqual(self.runcheck().returncode,1)
 def test_traversal(self): self.m['files'][0]['path']='../repo/x'; self.assertEqual(self.runcheck().returncode,1)
 def test_absolute(self): self.m['files'][0]['path']='/etc/passwd'; self.assertEqual(self.runcheck().returncode,1)
 def test_dependency_missing(self): self.m['references']=[{'root':'sources','path':'missing.pdf'}]; self.assertEqual(self.runcheck().returncode,2)
 def test_symlink(self):
  (self.k/'entry.md').unlink(); (self.k/'entry.md').symlink_to(self.root/'repo'/'outside'); self.assertEqual(self.runcheck().returncode,1)
 def test_required(self): del self.m['status']; self.assertEqual(self.runcheck().returncode,1)
 def test_status(self): self.m['status']='APPROVED'; self.assertEqual(self.runcheck().returncode,1)
 def test_document_fields(self):
  (self.k/'case.json').write_text('{}'); self.m['documents']=[{'root':'kit','path':'case.json','required_fields':['id','input','expected']}]; self.assertEqual(self.runcheck().returncode,1)
 def test_document_status(self):
  (self.k/'case.json').write_text('{"status":"ADOPTED"}'); self.m['documents']=[{'root':'kit','path':'case.json','required_fields':['status'],'status_allowed':['CANDIDATE']}]; self.assertEqual(self.runcheck().returncode,1)
 def test_adoption(self): self.m['adoption']='ADOPTED'; self.assertEqual(self.runcheck().returncode,1)
 def test_native_claim(self): self.m['native_mt5']='PASS'; self.assertEqual(self.runcheck().returncode,1)
 def test_pilot_without_proof(self): self.m['behavioral_pilot']='PASS'; self.assertEqual(self.runcheck().returncode,1)
 def test_unknown_pilot(self): self.m['behavioral_pilot']='MAYBE'; self.assertEqual(self.runcheck().returncode,1)
 def test_symlink_cycle(self):
  (self.k/'entry.md').unlink(); (self.k/'entry.md').symlink_to('entry.md'); r=self.runcheck(); self.assertEqual(r.returncode,1); self.assertNotIn('Traceback',r.stderr)
 def test_builder_isolation(self):
  for p in (CHECK.parent/'cases').glob('*.json'):
   c=json.loads(p.read_text()); b=CHECK.parent/'builder-inputs'/p.name
   self.assertTrue(b.is_file(),str(b)); d=json.loads(b.read_text()); self.assertEqual(set(d),{'id','topic','prompt','input'}); self.assertEqual(d,{key:c[key] for key in d}); self.assertNotIn('expected',d); self.assertNotIn('rubric',d)
 def test_provenance_optional_unknown(self):
  validator=runpy.run_path(str(CHECK)).get('validate_provenance'); self.assertTrue(callable(validator)); d=self.receipt(); self.assertEqual(validator(d),[])
 def test_provenance_required_unknown(self):
  validator=runpy.run_path(str(CHECK)).get('validate_provenance'); self.assertTrue(callable(validator)); d=self.receipt(); d['fresh_session_id']=None; self.assertTrue(validator(d))
 def test_provenance_optional_reason_required(self):
  validator=runpy.run_path(str(CHECK)).get('validate_provenance'); self.assertTrue(callable(validator)); d=self.receipt(); d['unavailable_reasons']={}; self.assertTrue(validator(d))
 def receipt(self):
  return {'dispatch_log':'dispatch.json','dispatch_sha256':'c'*64,'infrastructure_record':'infra.json','attempt_id':'a','case_id':'S01','repetition':1,'fresh_session_id':'builder-1','model_requested':'explicit-target','fresh_mode':'new_context_session','input_sha256':'a'*64,'output_sha256':'b'*64,'raw_input_log':'input.json','raw_output_log':'output.txt','tool_log':'tools.jsonl','tools_used':[],'model_backend_exact_build':None,'reasoning_hidden':None,'unavailable_reasons':{'model_backend_exact_build':'not exposed','reasoning_hidden':'not exposed'}}
 def test_pilot_new_revision_with_proof(self):
  d={'kit_revision':'R3','state_revision':2,'result':'PASS','attempt_ids':['a'+str(i) for i in range(36)]}; raw=json.dumps(d).encode(); (self.k/'proof.json').write_bytes(raw); self.m.update(revision='R3',state_revision=2,behavioral_pilot='PASS',behavioral_evidence={'root':'kit','path':'proof.json','sha256':hashlib.sha256(raw).hexdigest()}); self.assertEqual(self.runcheck().returncode,0)
 def test_required_handle_explicit(self):
  for folder in ('cases','builder-inputs'):
   d=json.loads((CHECK.parent/folder/'S01.json').read_text()); self.assertIs(d['input'].get('handle_required'),True)
 def test_provenance_dispatch_missing(self):
  validator=runpy.run_path(str(CHECK))['validate_provenance']; d=self.receipt(); d.pop('dispatch_log',None); d.pop('dispatch_sha256',None); self.assertTrue(validator(d))
 def test_provenance_bad_dispatch_hash(self):
  validator=runpy.run_path(str(CHECK))['validate_provenance']; d=self.receipt(); d['dispatch_sha256']='invalid'; self.assertTrue(validator(d))
 def test_provenance_null_reasons(self):
  validator=runpy.run_path(str(CHECK))['validate_provenance']; d=self.receipt(); d['unavailable_reasons']=None; self.assertTrue(validator(d))
 def test_provenance_malformed(self):
  validator=runpy.run_path(str(CHECK))['validate_provenance']
  for d in (None,[],42,'bad',{'unavailable_reasons':[]}): self.assertTrue(validator(d))
 def test_dispatch_bytes(self):
  validator=runpy.run_path(str(CHECK))['validate_provenance']; d=self.receipt(); raw=b'outer payload before dispatch'; (self.root/'dispatch.json').write_bytes(raw); (self.root/'infra.json').write_text('infrastructure identified'); d['dispatch_sha256']=hashlib.sha256(raw).hexdigest(); self.assertEqual(validator(d,self.root),[]); (self.root/'dispatch.json').write_text('tampered'); self.assertTrue(validator(d,self.root))
 def test_dispatch_escape(self):
  validator=runpy.run_path(str(CHECK))['validate_provenance']; d=self.receipt(); d['dispatch_log']='../escape'; self.assertTrue(validator(d,self.root))
 def test_optional_metadata_wrong_type(self):
  validator=runpy.run_path(str(CHECK))['validate_provenance']; d=self.receipt(); d['model_backend_exact_build']={}; self.assertTrue(validator(d))
 def test_tools_wrong_element(self):
  validator=runpy.run_path(str(CHECK))['validate_provenance']; d=self.receipt(); d['tools_used']=[{}]; self.assertTrue(validator(d))
 def test_unknown_root(self): self.m['files'][0]['root']='home'; self.assertEqual(self.runcheck().returncode,1)
if __name__=='__main__': unittest.main()

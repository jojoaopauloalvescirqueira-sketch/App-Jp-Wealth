#!/usr/bin/env python3
"""Build-only ESM -> local classical IIFE. No fetch/install/global tool mutation.
Lock checks inputs; normalized metafile records bundled dependency closure.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VENDOR=ROOT/'src/vendor/aisol-dot-globe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--three-root',required=True,type=Path);p.add_argument('--esbuild-bin',required=True,type=Path);args=p.parse_args()
 lock=json.loads((VENDOR/'build-lock.json').read_text())
 assert sha(VENDOR/'component.original.js')==lock['sourceSHA256'],'Aisol source differs'
 assert sha(args.esbuild_bin)==lock['esbuildBinarySHA256'],'esbuild binary differs from lock'
 assert subprocess.check_output([str(args.esbuild_bin),'--version'],text=True).strip()==lock['esbuildVersion']
 assert json.loads((args.three_root/'package.json').read_text())['version']==lock['threeVersion']
 for name,digest in lock['threeInputSHA256'].items():assert sha(args.three_root/name)==digest,'Three input differs: '+name
 out=VENDOR/'aisol-globe.iife.js';meta=VENDOR/'build-meta.json'
 command=[str(args.esbuild_bin),'src/js/40-app/31-market-hours/aisol/entry.js','--bundle','--format=iife','--platform=browser','--target=es2020',
          '--legal-comments=inline','--charset=utf8','--minify','--alias:three='+str((args.three_root/'build/three.module.js').resolve()),
          '--outfile='+str(out),'--metafile='+str(meta),
          '--banner:js=/*! Aisol Studio / @ulz-song — incorporated JP Wealth adaptation. Limited Commercial License. See NOTICES.md.\n'+(VENDOR/'THREE-LICENSE.txt').read_text()+'\n*/']
 subprocess.run(command,cwd=ROOT,check=True)
 data=json.loads(meta.read_text())
 def normalized(value):
  if isinstance(value,str):
   # Esbuild paths may be relative to cwd. Normalize actual dependency paths.
   candidate=(ROOT/value).resolve()
   if candidate==args.three_root.resolve() or args.three_root.resolve() in candidate.parents:return 'three/'+str(candidate.relative_to(args.three_root.resolve()))
   if candidate==out:return 'src/vendor/aisol-dot-globe/aisol-globe.iife.js'
   return value
  if isinstance(value,list):return [normalized(v) for v in value]
  if isinstance(value,dict):return {normalized(k):normalized(v) for k,v in value.items()}
  return value
 data=normalized(data)
 # No external import is allowed in the executable closure.
 for item in data['inputs'].values():assert not any(x.get('external') for x in item.get('imports',[]))
 meta.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
 receipt={'bundleSHA256':sha(out),'bytes':out.stat().st_size,'three':lock['threeVersion'],'esbuild':lock['esbuildVersion'],
          'sourceSHA256':lock['sourceSHA256'],'engineSHA256':sha(ROOT/'src/js/40-app/31-market-hours/aisol/engine.js'),
          'entrySHA256':sha(ROOT/'src/js/40-app/31-market-hours/aisol/entry.js'),'format':'iife','target':'es2020','legalComments':'inline',
          'inputCount':len(data['inputs']),'externalImports':False}
 (VENDOR/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

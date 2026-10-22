#!/usr/bin/env python3
"""Independent C5 delivery pins and rejecting controls; native NOT_RUN."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,unittest,zipfile
from build_leverage_package import ROOT,PRODUCT,OUTPUT,MANIFEST_PATH,build
from leverage_package_test import C5_MEMBERS,assert_release_inventory
from stoikus_daily_package_test import C5_DAILY_MEMBERS,check_archive
from stoikus_interface_package_test import InterfacePackageTests
ASSETS = {'nativeKit': ('Kit_Windows_Stoikus_Painel_C5_D1.zip', '92a05d3198fcae3dcbea2558f07cf13a20fbdddac63f1c8902e6dd4ac6b28983'), 'nativePin': ('root-pin-Painel-C5-D1.json', 'e0bf392d17e4a28efda316fdc13593101bbb25775be578e8b5f0abec8ef0101d'), 'preview': ('Previa_Stoikus_Painel_C5.html', '380cfe50b26dd6b438e9d5e374482406fe56b86e124e478fcafd05ebebb18afa')}
SDK_SHA256 = 'aa20c1f65f7b3dbc883eadf6babe312c8f30d9944ea787e89e686fe8aac7bbb2'
DAILY_SHA256 = '0d323ea010c21e043922a318252911262ea2dbf9b4b0217d67b0b9a1fe0242b5'
BUILD_ID = '406f16e7265f93dbd76f1c2b063090fa05520fdafc4322ca13ab5e0e0ae82161'
FINGERPRINT = '26473298967abb055d077c3cc440cab1efc9f92e5e8f54f06bcc30ef2dc8f347'

class C5ReleaseTests(InterfacePackageTests):
    version='1.23.0';assets=ASSETS;members=C5_MEMBERS;daily_members=C5_DAILY_MEMBERS
    daily_sha256=DAILY_SHA256;build_id=BUILD_ID;fingerprint=FINGERPRINT;variant='painel-C5'
    def populate_sources(self):
        archive=ROOT / OUTPUT / 'JPW_Stoikus_Fontes_v1.23.0_painel-C5.zip'
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),SDK_SHA256)
        with zipfile.ZipFile(archive) as source:
            self.assertEqual(set(source.namelist()),self.members)
            source.extractall(self.root / PRODUCT)
    def release_contract(self):
        contract=super().release_contract()
        contract.update(revision='C5',candidate='1.23.0-interface')
        return contract
    def test_absent_contract_keeps_default_names_and_archive_bytes(self):
        interface=build(self.root)
        self.manifest.pop('interfaceRelease');self.save();default=build(self.root)
        for kind in ('source','dailySource'):
            self.assertEqual(default['downloads'][kind]['filename'],interface['downloads'][kind]['filename'].replace('_painel-C5.zip','.zip'))
            for field in ('sha256','bytes'):self.assertEqual(default['downloads'][kind][field],interface['downloads'][kind][field])
        self.assertNotIn('interfaceRelease',default)
    def test_standalone_preview_preserves_current_html_and_brand_bytes(self):
        import base64
        source=(ROOT / 'docs/preview/stoikus-painel-personalizavel/index.html').read_text()
        data={theme:'data:image/svg+xml;base64,'+base64.b64encode((ROOT / ('assets/stoikus/stoikus-assinatura-'+theme+'.svg')).read_bytes()).decode()
              for theme in ('clara','escura')}
        old="$('brand').src='../../../assets/stoikus/stoikus-assinatura-'+($('theme').value==='dark'?'escura':'clara')+'.svg'"
        self.assertEqual(source.count(old),1)
        expected=source.replace(old,"$('brand').src=($('theme').value==='dark'?"+json.dumps(data['escura'])+":"+json.dumps(data['clara'])+")")
        expected=expected.replace('../../../assets/stoikus/stoikus-assinatura-clara.svg',data['clara'])
        self.assertNotIn('../../../assets/',expected)
        self.assertEqual((ROOT / OUTPUT / ASSETS['preview'][0]).read_bytes(),expected.encode())
        for theme,uri in data.items():
            self.assertEqual(base64.b64decode(uri.split(',',1)[1]),(ROOT / ('assets/stoikus/stoikus-assinatura-'+theme+'.svg')).read_bytes())

    def test_cross_version_revision_and_native_promotions_rejected(self):
        original=deepcopy(self.manifest)
        for field,value in [('version','1.22.3'),('revision','R5'),('candidate','1.22.3-interface')]:
            changed=deepcopy(original)
            if field=='version':changed[field]=value
            else:changed['interfaceRelease'][field]=value
            self.rejected(changed,field)
        for field in ('nativeCompilation','nativeRuntime','humanAcceptance','windowsX64'):
            changed=deepcopy(original);changed['interfaceRelease'][field]='PASS';self.rejected(changed,field)
        for field in ('compilation','terminal'):
            changed=deepcopy(original);changed['validation'][field]['status']='passed';self.rejected(changed,field)
    def test_exact_panel_header_inventory_rejects_each_omission_and_substitution(self):
        for name in ('PanelPrefs','PanelEditor','PanelBridge'):
            changed=deepcopy(self.manifest)
            path=PRODUCT+'MQL5/Include/JPWealth/JPW_Stoikus_'+name+'.mqh'
            changed['sourceFiles'].remove(path);self.rejected(changed,name)
        changed=deepcopy(self.manifest);changed['sourceFiles'][-1]=PRODUCT+'rogue.md'
        with self.assertRaises(AssertionError):assert_release_inventory(changed)

def candidate():
    manifest=json.loads((ROOT / MANIFEST_PATH).read_text())
    assert manifest['version']=='1.23.0' and manifest['interfaceRelease']['revision']=='C5'
    assert manifest['interfaceRelease']['candidate']=='1.23.0-interface'
    assert manifest['interfaceRelease']['archiveVariant']=='painel-C5'
    assert manifest['interfaceRelease']['state']=='SOURCE_ONLY_NATIVE_PENDING'
    assert_release_inventory(manifest)
    assert manifest['runtimeBuildId']==BUILD_ID and manifest['mqlSourceFingerprint']==FINGERPRINT
    assert manifest['nativeArtifact'] is None and manifest['downloads']['compiled']['available'] is False
    assert manifest['downloads']['installer']['available'] is False
    for field in ('nativeCompilation','nativeRuntime','humanAcceptance','windowsX64'):assert manifest['interfaceRelease'][field]=='NOT_RUN'
    for field in ('compilation','terminal'):assert manifest['validation'][field]['status']=='pending'
    assert hashlib.sha256(check_archive(ROOT,manifest,'source',C5_MEMBERS)).hexdigest()==SDK_SHA256
    daily=check_archive(ROOT,manifest,'dailySource',C5_DAILY_MEMBERS)
    assert hashlib.sha256(daily).hexdigest()==DAILY_SHA256
    for kind,(filename,digest) in ASSETS.items():
        raw=(ROOT / OUTPUT / filename).read_bytes();record=manifest['interfaceRelease']['artifacts'][kind]
        assert record==dict(available=True,path=OUTPUT+filename,filename=filename,sha256=digest,bytes=len(raw))
        assert hashlib.sha256(raw).hexdigest()==digest
    pin=json.loads((ROOT / OUTPUT / ASSETS['nativePin'][0]).read_text())
    assert pin['runtime_build_id']==BUILD_ID and pin['mql_source_fingerprint']==FINGERPRINT
    assert pin['kit_package_sha256']==ASSETS['nativeKit'][1]
    # Native payload is a documentary derivative: every member except the guide is identical.
    import io
    with zipfile.ZipFile(ROOT / OUTPUT / ASSETS['nativeKit'][0]) as kit:
        payload=kit.read('JPW_Stoikus_Uso_Fontes_v1.23.0_interface.zip')
        assert hashlib.sha256(payload).hexdigest()==pin['source_zip_sha256']
    with zipfile.ZipFile(io.BytesIO(payload)) as native,zipfile.ZipFile(io.BytesIO(daily)) as ordinary:
        assert set(native.namelist())==set(ordinary.namelist())
        for name in native.namelist():
            if name=='LEIA_PRIMEIRO.md':assert native.read(name).endswith(ordinary.read(name))
            else:assert native.read(name)==ordinary.read(name)
    print('PASS C5 SDK142/daily89, exact pins and documentary native derivative; native NOT_RUN')

def controls():
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(C5ReleaseTests))
    assert result.wasSuccessful(),'C5 release controls failed'
if __name__=='__main__':controls();candidate()

#!/usr/bin/env python3
"""Reprodutibilidade do Build ID (JPW-BUILD-DSSTORE).

Contrato duplo:
  1. lixo local não rastreado (.DS_Store, temporário de editor, subdiretório ignorado)
     NÃO pode alterar o Build ID, o monólito nem os hashes do manifest;
  2. mudança real num input oficial DEVE alterar o Build ID, ou ser recusada
     quando violar a identidade selada de uma interface aprovada.

Como funciona: monta duas cópias do projeto num diretório temporário a partir dos
arquivos rastreados pelo Git e de qualquer input oficial já declarado no manifest
(com o conteúdo atual do disco, inclusive fontes novas ainda não commitadas), roda
`tools/rebuild_monolith.py` real em cada uma e compara. A árvore de trabalho nunca
é tocada.
"""
from pathlib import Path
import ast, base64, hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

DOCUMENTOS = (
    'docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf',
    'docs/normative/ANEXO_PARAMETRICO_CANONICO.md',
)
BRAND_BUILD_INPUTS = (
    'manifests/jp-wealth.webmanifest', 'manifests/jp-wealth-black.webmanifest',
    'assets/jp-wealth-brand-red.png', 'assets/jp-wealth-brand-black.png',
    'assets/pwa-icon-primary.png', 'assets/pwa-icon-primary-192.png', 'assets/pwa-icon-primary-512.png',
    'assets/pwa-icon-secondary.png', 'assets/pwa-icon-secondary-192.png', 'assets/pwa-icon-secondary-512.png',
)
LEVERAGE_MANIFEST = 'downloads/jpw-alavancagem-atual/manifest.json'
LEVERAGE_BUILDER = 'tools/build_leverage_package.py'
INTERFACE_ARTIFACTS = {
    'nativeKit': ('downloads/jpw-alavancagem-atual/Kit_Windows_Stoikus_Janelas_R5.zip', 'application/zip'),
    'nativePin': ('downloads/jpw-alavancagem-atual/root-pin-R5.json', 'application/json'),
    'preview': ('downloads/jpw-alavancagem-atual/Previa_Stoikus_Janelas_R5.html', 'text/html'),
}
INTERFACE_DAILY_SHA256 = '0bc6c856410b576ebf0412aa341056e8e02463c8f848fe34d2bd4e983ae5f7a3'
# Independent release oracle: version alone cannot select between R5 and C5.
# The historical R5 paths/MIME/daily digest above remain literal and unchanged.
INTERFACE_CONTRACTS = {
    ('1.23.0', 'R5'): {
        'suffix': '', 'artifacts': INTERFACE_ARTIFACTS,
        'daily_sha256': INTERFACE_DAILY_SHA256,
        'hashes': {
            'nativeKit': '5c32d1a5bf3ff2e2023c2c0e7b29c6425d1cc1bd5169f5fdf03f277d8fc9f8f4',
            'nativePin': 'bb6ad986db99b3f9dca2437e83f9fd928f4df7830a9866da5d2b0b7bc731447a',
            'preview': '90fd6a0d542ce9abb538d61f0b5b8e5470d364eae1dd47ceed4504f6b67cbfd7',
        },
    },
    ('1.23.0', 'C5'): {
        'suffix': '_painel-C5',
        'artifacts': {
            'nativeKit': ('downloads/jpw-alavancagem-atual/Kit_Windows_Stoikus_Painel_C5_D1.zip', 'application/zip'),
            'nativePin': ('downloads/jpw-alavancagem-atual/root-pin-Painel-C5-D1.json', 'application/json'),
            'preview': ('downloads/jpw-alavancagem-atual/Previa_Stoikus_Painel_C5.html', 'text/html'),
        },
        'daily_sha256': '0d323ea010c21e043922a318252911262ea2dbf9b4b0217d67b0b9a1fe0242b5',
        'hashes': {
            'nativeKit': '92a05d3198fcae3dcbea2558f07cf13a20fbdddac63f1c8902e6dd4ac6b28983',
            'nativePin': 'e0bf392d17e4a28efda316fdc13593101bbb25775be578e8b5f0abec8ef0101d',
            'preview': '380cfe50b26dd6b438e9d5e374482406fe56b86e124e478fcafd05ebebb18afa',
        },
    },
}


def contrato_interface_esperado(leverage):
    release = leverage.get('interfaceRelease')
    assert isinstance(release, dict), 'contrato de interface deve ser objeto'
    version, revision = leverage.get('version'), release.get('revision')
    assert isinstance(version, str) and isinstance(revision, str), 'versao/revisao da interface invalidas'
    pair = (version, revision)
    assert pair in INTERFACE_CONTRACTS, 'par versao/revisao sem oraculo independente'
    return INTERFACE_CONTRACTS[pair]


def contraprovas_seletor_interface():
    assert contrato_interface_esperado({'version':'1.23.0','interfaceRelease':{'revision':'R5'}})['suffix'] == ''
    assert contrato_interface_esperado({'version':'1.23.0','interfaceRelease':{'revision':'C5'}})['suffix'] == '_painel-C5'
    controls = [('1.22.3','C5'),('1.22.3','R5'),('1.23.0','R4'),('1.23.0','C6'),
                ('1.24.0','C5'),('1.23.0',None),('1.23.0',[])]
    for version, revision in controls:
        try:
            contrato_interface_esperado({'version':version,'interfaceRelease':{'revision':revision}})
        except AssertionError:
            pass
        else:
            raise AssertionError('seletor aceitou versao/revisao inesperada')
    return len(controls)



def artefatos_interface_declarados(leverage, root=ROOT):
    if 'interfaceRelease' not in leverage:
        return {}
    # Use the real package boundary: keys, exact selected release, native pending,
    # safe files, approved hashes/lengths and sealed MQL identity are mandatory.
    spec = importlib.util.spec_from_file_location('jpw_repro_checked_interface', root / LEVERAGE_BUILDER)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    contract = contrato_interface_esperado(leverage)
    assert builder.validate_interface_release(root, leverage) == contract['suffix'], 'sufixo difere do contrato exato'
    records = leverage['interfaceRelease']['artifacts']
    assert set(records) == set(contract['artifacts']), 'inventario de interface nao limitado aos tres inputs'
    for kind, (relative, _mime) in contract['artifacts'].items():
        assert records[kind]['path'] == relative, ('input de interface inesperado', kind)
        assert records[kind]['sha256'] == contract['hashes'][kind], ('pin independente da interface diverge', kind)
    return records
# The official builder owns this explicit list. Parse its literal declaration so
# fixtures include newly added/untracked inputs without executing a build here.
MARKET_HOURS_BUILD_INPUTS = next(
    ast.literal_eval(node.value) for node in ast.parse((ROOT/'tools/rebuild_monolith.py').read_text()).body
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'MARKET_HOURS_BUILD_INPUTS'
                                          for target in node.targets))


def artefatos_nativos_declarados(leverage):
    native = leverage.get('nativeArtifact')
    if native is None:
        return []
    assert isinstance(native, dict), 'declaracao de artefato nativo invalida'
    records = native['artifacts']
    expected = {rel[:-4] + '.ex5' for rel in leverage['sourceFiles'] if rel.endswith('.mq5')}
    assert isinstance(records, list) and len(records) == len(expected), 'conjunto nativo declarado invalido'
    assert {item['path'] for item in records} == expected, 'conjunto nativo nao corresponde aos fontes'
    spec = importlib.util.spec_from_file_location('jpw_repro_checked_native', ROOT / LEVERAGE_BUILDER)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    for item in records:
        rel = item['path']
        assert isinstance(rel, str) and rel.endswith('.ex5'), 'extensao nativa invalida'
        source = builder.checked_file(ROOT, rel, 'mt5/jpw-alavancagem-atual/MQL5/')
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256'], (
            'input nativo diferente da evidencia', rel)
    return records

LIXO = {
    'icons/.DS_Store': b'\x00\x01Finder junk' + b'\xff' * 64,   # o caso real que quebrou
    '.DS_Store': b'\x00\x01raiz' + b'\xee' * 32,
    'src/js/.DS_Store': b'\x00\x01dentro do source' + b'\xdd' * 16,
    'app.css.swp': b'lixo de editor vim',
    'src/styles/.app.css.un~': b'undo file do editor',
    'node_modules/pacote/index.js': b'module.exports = "diretorio ignorado";',
    'tools/.artifacts/relatorio.json': b'{"local":true}',
}

def arquivos_do_candidato():
    saida = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, check=True).stdout
    arquivos = {p for p in saida.decode('utf-8').split('\0') if p}
    manifest = json.loads((ROOT / 'src/js/manifest.json').read_text(encoding='utf-8'))
    arquivos.update(item['path'] for item in manifest['files'])
    arquivos.update(item['path'] for item in manifest.get('runtimeAssets', []))
    arquivos.update(DOCUMENTOS)  # inputs normativos novos, inclusive antes do primeiro commit
    arquivos.update(BRAND_BUILD_INPUTS)
    arquivos.add('assets/dante-guide.png')  # New explicit builder input, including pre-commit candidates.
    arquivos.update(MARKET_HOURS_BUILD_INPUTS)
    leverage = json.loads((ROOT / LEVERAGE_MANIFEST).read_text(encoding='utf-8'))
    arquivos.update((LEVERAGE_MANIFEST, LEVERAGE_BUILDER))
    arquivos.update(leverage['sourceFiles'])
    arquivos.update(item['path'] for item in leverage['downloads'].values() if item['available'])
    # Native inputs may be newly integrated and not yet tracked by Git. Copy
    # exactly the manifest declarations; the real builder still checks every
    # source fingerprint, path, architecture and artifact SHA-256.
    arquivos.update(item['path'] for item in artefatos_nativos_declarados(leverage))
    arquivos.update(item['path'] for item in artefatos_interface_declarados(leverage).values())
    return sorted(arquivos)

def montar(destino: Path, arquivos):
    for rel in arquivos:
        origem = ROOT / rel
        if not origem.is_file():
            continue                       # arquivo removido no disco: o rebuild deve decidir
        alvo = destino / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem, alvo)

def semear_lixo(destino: Path):
    for rel, conteudo in LIXO.items():
        alvo = destino / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_bytes(conteudo)

def rebuild(destino: Path):
    r = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'],
                       cwd=destino, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f'rebuild falhou em {destino.name}: {r.stdout}{r.stderr}')

def fatos(destino: Path):
    leverage = json.loads((destino / LEVERAGE_MANIFEST).read_text(encoding='utf-8'))
    return {
        'market_sidecar': (destino/'src/vendor/market-hours/runtime-payload.js').read_bytes(),
        'download_sidecars': {p.name:p.read_bytes() for p in sorted((destino/'src/vendor/downloads').glob('*-payload.*'))},
        'build_id': (destino / 'build-id.js').read_text(encoding='utf-8').strip(),
        'monolito': (destino / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').read_bytes(),
        'manifest': (destino / 'src/js/manifest.json').read_bytes(),
        'leverage_manifest': (destino / LEVERAGE_MANIFEST).read_bytes(),
        'leverage_source': (destino / leverage['downloads']['source']['path']).read_bytes(),
        'leverage_daily': (destino / leverage['downloads']['dailySource']['path']).read_bytes(),
        'interface_artifacts': {kind: (destino / item['path']).read_bytes()
                                for kind, item in artefatos_interface_declarados(leverage, destino).items()},
        'leverage_compiled': ((destino / leverage['downloads']['compiled']['path']).read_bytes()
                              if leverage['downloads']['compiled']['available'] else None),
    }

def main():
    selector_controls = contraprovas_seletor_interface()
    arquivos = arquivos_do_candidato()
    with tempfile.TemporaryDirectory(prefix='jpw-repro-') as raiz:
        raiz = Path(raiz)
        limpo, sujo, alterado = raiz / 'limpo', raiz / 'sujo', raiz / 'alterado'

        # ---- 1. checkout limpo: referência canônica ----
        montar(limpo, arquivos)
        rebuild(limpo)
        a = fatos(limpo)

        # ---- 2. mesmo checkout + lixo local ignorado ----
        montar(sujo, arquivos)
        semear_lixo(sujo)
        assert (sujo / 'icons/.DS_Store').is_file(), 'o lixo sintético deveria existir'
        rebuild(sujo)
        b = fatos(sujo)

        assert a['build_id'] == b['build_id'], (
            f"LIXO ALTEROU O BUILD ID\n  limpo: {a['build_id']}\n  sujo : {b['build_id']}")
        assert a['market_sidecar'] == b['market_sidecar'], 'lixo alterou payload de Bolsas Globais'
        assert a['download_sidecars'] == b['download_sidecars'], 'lixo alterou payloads de download'
        assert a['monolito'] == b['monolito'], 'lixo alterou o monólito portátil'
        assert a['manifest'] == b['manifest'], 'lixo alterou os hashes do manifest'
        assert a['leverage_manifest'] == b['leverage_manifest'], 'lixo alterou o manifesto de alavancagem'
        assert a['leverage_source'] == b['leverage_source'], 'lixo alterou o ZIP de fontes de alavancagem'
        assert a['leverage_compiled'] == b['leverage_compiled'], 'lixo alterou o ZIP compilado de alavancagem'
        assert a['leverage_daily'] == b['leverage_daily'], 'lixo alterou o ZIP de uso diario'
        assert a['interface_artifacts'] == b['interface_artifacts'], 'lixo alterou os tres artifacts de interface'

        # ---- 3. contraprova: mudar um INPUT OFICIAL deve mudar o Build ID ----
        montar(alterado, arquivos)
        alvo = alterado / 'src/js/00-core/05-helpers.js'
        assert alvo.is_file(), 'input oficial de referência não encontrado'
        alvo.write_bytes(alvo.read_bytes() + b'\n// alteracao real de fonte para o teste\n')
        rebuild(alterado)
        c = fatos(alterado)
        assert a['build_id'] != c['build_id'], (
            'mudanca real de fonte NAO alterou o Build ID — fingerprint cego')

        # ---- 4. originais incorporados byte-idênticos e identificados pelo build ----
        html = a['monolito'].decode('utf-8')
        embedded = re.findall(r'href="data:([^" ]+);base64,([A-Za-z0-9+/=]+)" download="([^"]+)"', html)
        for relative in DOCUMENTOS:
            original = (limpo / relative).read_bytes()
            assert any(base64.b64decode(data) == original for _mime, data, _name in embedded), relative
            assert f'href="{relative}"' not in html, f'link externo ainda presente: {relative}'
            destino = raiz / ('documento-' + Path(relative).suffix.lstrip('.'))
            montar(destino, arquivos)
            alvo_doc = destino / relative
            alvo_doc.write_bytes(original + b'\n')
            rebuild(destino)
            assert fatos(destino)['build_id'] != a['build_id'], f'fingerprint cego ao documento: {relative}'
            alvo_doc.unlink()
            erro = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'], cwd=destino, capture_output=True, text=True)
            assert erro.returncode != 0 and 'input oficial do build ausente' in (erro.stdout + erro.stderr), relative

        # The exact delivered ZIP bytes are present in the portable bootstrap.
        leverage = json.loads(a['leverage_manifest'])
        for item in leverage['downloads'].values():
            if not item['available']:
                continue
            original = (limpo / item['path']).read_bytes()
            assert len(original) == item['bytes'], item['path']
            assert base64.b64encode(original).decode('ascii') in html, item['path']
            assert hashlib.sha256(original).hexdigest() == item['sha256'], item['path']
        interface_records = artefatos_interface_declarados(leverage, limpo)
        if interface_records:
            assert hashlib.sha256(a['leverage_daily']).hexdigest() == contrato_interface_esperado(leverage)['daily_sha256']
        download_metadata = json.JSONDecoder().raw_decode(html.split('window.JPW_DOWNLOAD_MANIFEST = ',1)[1])[0]
        inert_payloads = [json.loads(raw) for raw in re.findall(r'<script type="application/json" id="jpw-download-payload-[^"]+">(.*?)</script>',html)]
        portable_files = {key.removeprefix('leverage/'): {'mime':download_metadata['resources'][key]['mime'],'base64':encoded} for payload in inert_payloads for key,encoded in payload['files'].items() if key.startswith('leverage/')}
        bootstrap = (limpo/'build-id.js').read_text()
        assert 'base64' not in bootstrap and 'JPW_LEVERAGE_FILES' not in bootstrap, 'download bytes leaked into bootstrap'
        for kind, item in interface_records.items():
            original = (limpo / item['path']).read_bytes()
            assert item['path'] in arquivos, ('input oficial da interface ausente do fixture', kind)
            assert len(original) == item['bytes'], kind
            assert hashlib.sha256(original).hexdigest() == item['sha256'], kind
            assert portable_files[kind]['mime'] == contrato_interface_esperado(leverage)['artifacts'][kind][1], kind
            assert base64.b64decode(portable_files[kind]['base64'], validate=True) == original, kind
        for kind, item in leverage['downloads'].items():
            if item['available']:
                assert portable_files[kind]['mime'] == 'application/zip', kind
                assert base64.b64decode(portable_files[kind]['base64'], validate=True) == (limpo / item['path']).read_bytes(), kind
        first_source = leverage['sourceFiles'][0]
        montar(alterado, arquivos)
        (alterado / first_source).write_bytes((alterado / first_source).read_bytes() + b'\n')
        if interface_records:
            erro = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'], cwd=alterado, capture_output=True, text=True)
            reason = 'fingerprint aprovado' if Path(first_source).suffix in ('.mq5','.mqh','.bmp') else 'Pacote ou build da interface diverge da release aprovada'
            assert erro.returncode != 0 and reason in (erro.stdout + erro.stderr), 'fonte selada alterada foi aceita'
        else:
            rebuild(alterado)
            assert fatos(alterado)['build_id'] != a['build_id'], 'fingerprint cego ao pacote de fontes'
        interface_controls = []
        if interface_records:
            # The old/default test above still requires a different build for a
            # changed official source. Selected sealed bytes must instead fail closed.
            sealed_source = next(rel for rel in leverage['sourceFiles'] if rel.endswith('.mq5'))
            destino = raiz / 'interface-source-tampered'
            montar(destino, arquivos)
            target = destino / sealed_source
            target.write_bytes(target.read_bytes() + b'\n// changed sealed source\n')
            erro = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'], cwd=destino, capture_output=True, text=True)
            assert erro.returncode != 0 and 'fingerprint aprovado' in (erro.stdout + erro.stderr), 'fonte MQL selada alterada foi aceita'
            interface_controls.append({'control': 'sealed-source-tampered', 'path': sealed_source, 'result': 'EXPECTED_REFUSAL'})
            for kind, item in interface_records.items():
                for control in ('missing', 'tampered'):
                    destino = raiz / ('interface-' + kind + '-' + control)
                    montar(destino, arquivos)
                    target = destino / item['path']
                    if control == 'missing':
                        target.unlink()
                        reason = 'Arquivo declarado ausente ou inseguro: ' + item['path']
                    else:
                        content = target.read_bytes()
                        assert content, ('controle da interface exige arquivo nao vazio', kind)
                        target.write_bytes(bytes([content[0] ^ 1]) + content[1:])
                        reason = 'Bytes/hash da interface divergem da release aprovada: ' + kind
                    before = {rel: (destino / rel).read_bytes() for rel in (
                        'build-id.js', 'src/js/manifest.json', LEVERAGE_MANIFEST,
                        'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')}
                    erro = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'], cwd=destino, capture_output=True, text=True)
                    assert erro.returncode != 0 and reason in (erro.stdout + erro.stderr), (kind, control, erro.stdout, erro.stderr)
                    assert all((destino / rel).read_bytes() == raw for rel, raw in before.items()), 'recusa de interface alterou outputs'
                    interface_controls.append({'control': control, 'kind': kind, 'path': item['path'],
                                               'returncode': erro.returncode, 'result': 'EXPECTED_REFUSAL'})

        # Market original bytes and notices survive as inert JSON, never as
        # immediately executable renderer code or bulk build-ID metadata.
        market_inert = re.search(r'<script type="application/json" id="jpw-market-hours-payload">(.*?)</script>', html, re.S)
        assert market_inert and '<' not in market_inert[1], 'payload de mercado ausente/inseguro'
        market = json.loads(market_inert[1])
        registered = a['market_sidecar'].decode().split('register(', 1)[1].removesuffix(');\n')
        assert market == json.loads(registered), 'web file e portable usam bytes diferentes'
        for key, rel in (('catalog', 'src/data/market-hours/calendar-v1.json'),
                         ('renderer', 'src/vendor/aisol-dot-globe/aisol-globe.iife.js')):
            assert market['files'][key].encode('utf-8') == (limpo/rel).read_bytes(), rel
        for name in ('NOTICES.md', 'THREE-LICENSE.txt', 'ESBUILD-LICENSE.txt'):
            assert market['notices'][name].encode() == (limpo/'src/vendor/aisol-dot-globe'/name).read_bytes(), name
        assert len(a['build_id'].encode()) < 50000, 'bootstrap de build contem payload volumoso'

        # ---- 5. cada input da marca declarado e ausente precisa falhar alto ----
        for relative in BRAND_BUILD_INPUTS:
            montar(alterado, arquivos)
            (alterado / relative).unlink()
            r = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'],
                               cwd=alterado, capture_output=True, text=True)
            assert r.returncode != 0, f'input oficial ausente deveria interromper o build: {relative}'
            assert 'input oficial do build ausente' in (r.stdout + r.stderr), (relative, r.stdout + r.stderr)

        # ---- 6. declared EX5 remains mandatory and bound to its exact digest ----
        native = leverage.get('nativeArtifact')
        native_controls = []
        if native is not None:
            assert a['leverage_compiled'] is not None, 'artefatos nativos declarados sem ZIP compilado'
            records = native['artifacts']
            assert records, 'conjunto nativo declarado vazio'
            for record in records:
                rel = record['path']
                assert rel in arquivos, f'input nativo ausente do fixture: {rel}'
                assert hashlib.sha256((limpo / rel).read_bytes()).hexdigest() == record['sha256'], rel
            for control, record, reason in (
                ('missing', records[0], 'Arquivo declarado ausente ou inseguro'),
                ('tampered', records[-1], 'Artefato nativo vazio ou diferente da evidencia'),
            ):
                destino = raiz / ('native-' + control)
                montar(destino, arquivos)
                target = destino / record['path']
                if control == 'missing':
                    target.unlink()
                else:
                    content = target.read_bytes()
                    assert content, 'controle nativo exige arquivo nao vazio'
                    target.write_bytes(bytes([content[0] ^ 1]) + content[1:])
                r = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'],
                                   cwd=destino, capture_output=True, text=True)
                assert r.returncode != 0 and reason in (r.stdout + r.stderr), (
                    control, record['path'], r.returncode, r.stdout, r.stderr)
                native_controls.append({'control': control, 'path': record['path'],
                                        'returncode': r.returncode, 'result': 'EXPECTED_REFUSAL'})
        else:
            assert a['leverage_compiled'] is None, 'fallback sem prova nativa deve permanecer sem ZIP compilado'
            # Source-only candidates must also reject an unproved EX5, without changing outputs.
            destino = raiz / 'native-unproved-ex5'
            montar(destino, arquivos)
            source = next(rel for rel in leverage['sourceFiles'] if rel.endswith('.mq5'))
            ex5 = destino / (source[:-4] + '.ex5')
            ex5.write_bytes(b'unproved native binary fixture' * 64)
            before = {rel:(destino/rel).read_bytes() for rel in (
                'build-id.js','src/js/manifest.json',LEVERAGE_MANIFEST,
                'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')}
            erro = subprocess.run([sys.executable,'tools/rebuild_monolith.py'],cwd=destino,capture_output=True,text=True)
            assert erro.returncode != 0 and '.ex5 encontrado sem evidencia nativa' in erro.stdout+erro.stderr, 'EX5 sem prova foi aceito'
            assert all((destino/rel).read_bytes()==raw for rel,raw in before.items()), 'recusa de EX5 alterou outputs'
            native_controls.append({'control':'unproved-ex5','path':source[:-4]+'.ex5','result':'EXPECTED_REFUSAL'})
        print(json.dumps({'independent_release_selector_controls': selector_controls,
                          'selected_interface_revision': leverage.get('interfaceRelease',{}).get('revision'),
                          'native_declared_inputs': len(native['artifacts']) if native else 0,
                          'compiled_zip_deterministic': a['leverage_compiled'] == b['leverage_compiled'],
                          'compiled_fallback_preserved': native is not None or a['leverage_compiled'] is None,
                          'native_integrity_controls': native_controls,
                          'daily_zip_deterministic': a['leverage_daily'] == b['leverage_daily'],
                          'interface_declared_inputs': len(interface_records),
                          'interface_artifacts_deterministic': a['interface_artifacts'] == b['interface_artifacts'],
                          'interface_integrity_controls': interface_controls}, indent=2))

        canonico = a['build_id'].split("'")[1]
        print(f'BUILD REPRODUCIBILITY OK — Build ID canonico {canonico}; '
              f'{len(LIXO)} artefatos locais ignorados (.DS_Store na raiz/icons/src, swap e undo '
              f'de editor, diretorio ignorado) nao alteram Build ID, monolito nem manifest; '
              f'mudanca oficial altera o build ou e recusada se violar fonte selada; originais incorporados identicos; input oficial ausente interrompe o build.')

if __name__ == '__main__':
    main()

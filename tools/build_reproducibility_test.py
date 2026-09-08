#!/usr/bin/env python3
"""Reprodutibilidade do Build ID (JPW-BUILD-DSSTORE).

Contrato duplo:
  1. lixo local não rastreado (.DS_Store, temporário de editor, subdiretório ignorado)
     NÃO pode alterar o Build ID, o monólito nem os hashes do manifest;
  2. mudança real num input oficial do candidato DEVE alterar o Build ID.

Como funciona: monta duas cópias do projeto num diretório temporário a partir dos
arquivos rastreados pelo Git e de qualquer input oficial já declarado no manifest
(com o conteúdo atual do disco, inclusive fontes novas ainda não commitadas), roda
`tools/rebuild_monolith.py` real em cada uma e compara. A árvore de trabalho nunca
é tocada.
"""
from pathlib import Path
import base64, json, os, re, shutil, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

DOCUMENTOS = (
    'docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf',
    'docs/normative/ANEXO_PARAMETRICO_CANONICO.md',
)

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
    arquivos.update(DOCUMENTOS)  # inputs normativos novos, inclusive antes do primeiro commit
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
    return {
        'build_id': (destino / 'build-id.js').read_text(encoding='utf-8').strip(),
        'monolito': (destino / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html').read_bytes(),
        'manifest': (destino / 'src/js/manifest.json').read_bytes(),
    }

def main():
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
        assert a['monolito'] == b['monolito'], 'lixo alterou o monólito portátil'
        assert a['manifest'] == b['manifest'], 'lixo alterou os hashes do manifest'

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

        # ---- 5. o input declarado e ausente precisa falhar alto ----
        (alterado / 'manifests/jp-wealth.webmanifest').unlink()
        r = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'],
                           cwd=alterado, capture_output=True, text=True)
        assert r.returncode != 0, 'input oficial ausente deveria interromper o build'
        assert 'input oficial do build ausente' in (r.stdout + r.stderr), (r.stdout + r.stderr)

        canonico = a['build_id'].split("'")[1]
        print(f'BUILD REPRODUCIBILITY OK — Build ID canonico {canonico}; '
              f'{len(LIXO)} artefatos locais ignorados (.DS_Store na raiz/icons/src, swap e undo '
              f'de editor, diretorio ignorado) nao alteram Build ID, monolito nem manifest; '
              f'mudanca real de fonte/documento altera; originais incorporados identicos; input oficial ausente interrompe o build.')

if __name__ == '__main__':
    main()

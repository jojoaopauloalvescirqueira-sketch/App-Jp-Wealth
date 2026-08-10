#!/usr/bin/env python3
"""Reprodutibilidade do Build ID (JPW-BUILD-DSSTORE).

Contrato duplo:
  1. lixo local não rastreado (.DS_Store, temporário de editor, subdiretório ignorado)
     NÃO pode alterar o Build ID, o monólito nem os hashes do manifest;
  2. mudança real num input oficial rastreado DEVE alterar o Build ID.

Como funciona: monta duas cópias do projeto num diretório temporário a partir dos
arquivos rastreados pelo Git (com o conteúdo atual do disco, para cobrir correções
ainda não commitadas), roda `tools/rebuild_monolith.py` real em cada uma e compara.
A árvore de trabalho nunca é tocada.
"""
from pathlib import Path
import os, shutil, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

LIXO = {
    'icons/.DS_Store': b'\x00\x01Finder junk' + b'\xff' * 64,   # o caso real que quebrou
    '.DS_Store': b'\x00\x01raiz' + b'\xee' * 32,
    'src/js/.DS_Store': b'\x00\x01dentro do source' + b'\xdd' * 16,
    'app.css.swp': b'lixo de editor vim',
    'src/styles/.app.css.un~': b'undo file do editor',
    'node_modules/pacote/index.js': b'module.exports = "diretorio ignorado";',
    'tools/.artifacts/relatorio.json': b'{"local":true}',
}

def arquivos_rastreados():
    saida = subprocess.run(['git', 'ls-files', '-z'], capture_output=True, check=True).stdout
    return [p for p in saida.decode('utf-8').split('\0') if p]

def montar(destino: Path, rastreados):
    for rel in rastreados:
        origem = ROOT / rel
        if not origem.is_file():
            continue                       # arquivo rastreado e removido no disco: ignorar
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
    rastreados = arquivos_rastreados()
    with tempfile.TemporaryDirectory(prefix='jpw-repro-') as raiz:
        raiz = Path(raiz)
        limpo, sujo, alterado = raiz / 'limpo', raiz / 'sujo', raiz / 'alterado'

        # ---- 1. checkout limpo: referência canônica ----
        montar(limpo, rastreados)
        rebuild(limpo)
        a = fatos(limpo)

        # ---- 2. mesmo checkout + lixo local ignorado ----
        montar(sujo, rastreados)
        semear_lixo(sujo)
        assert (sujo / 'icons/.DS_Store').is_file(), 'o lixo sintético deveria existir'
        rebuild(sujo)
        b = fatos(sujo)

        assert a['build_id'] == b['build_id'], (
            f"LIXO ALTEROU O BUILD ID\n  limpo: {a['build_id']}\n  sujo : {b['build_id']}")
        assert a['monolito'] == b['monolito'], 'lixo alterou o monólito portátil'
        assert a['manifest'] == b['manifest'], 'lixo alterou os hashes do manifest'

        # ---- 3. contraprova: mudar um INPUT OFICIAL deve mudar o Build ID ----
        montar(alterado, rastreados)
        alvo = alterado / 'src/js/00-core/05-helpers.js'
        assert alvo.is_file(), 'input oficial de referência não encontrado'
        alvo.write_bytes(alvo.read_bytes() + b'\n// alteracao real de fonte para o teste\n')
        rebuild(alterado)
        c = fatos(alterado)
        assert a['build_id'] != c['build_id'], (
            'mudanca real de fonte NAO alterou o Build ID — fingerprint cego')

        # ---- 4. o input declarado e ausente precisa falhar alto ----
        (alterado / 'manifests/jp-wealth.webmanifest').unlink()
        r = subprocess.run([sys.executable, 'tools/rebuild_monolith.py'],
                           cwd=alterado, capture_output=True, text=True)
        assert r.returncode != 0, 'input oficial ausente deveria interromper o build'
        assert 'input oficial do build ausente' in (r.stdout + r.stderr), (r.stdout + r.stderr)

        canonico = a['build_id'].split("'")[1]
        print(f'BUILD REPRODUCIBILITY OK — Build ID canonico {canonico}; '
              f'{len(LIXO)} artefatos locais ignorados (.DS_Store na raiz/icons/src, swap e undo '
              f'de editor, diretorio ignorado) nao alteram Build ID, monolito nem manifest; '
              f'mudanca real de fonte altera; input oficial ausente interrompe o build.')

if __name__ == '__main__':
    main()

# Baseline Git e recuperação — 03/08/2026

## Estado histórico encontrado

A pasta do projeto foi encontrada sem diretório `.git`. A busca na pasta-mãe, em `Documents` e em `Desktop` encontrou apenas repositórios não correspondentes ao JP Wealth. Não foi localizado um repositório anterior desta estrutura modular.

Os backups internos existentes em `data/backups/` são parciais e foram tratados como artefatos locais, não como histórico. O backup `finalize-session-before-20260803` cobre somente parte dos arquivos; `finalize-session-n2-before-20260803` cobre somente os arquivos críticos da correção N2. O monólito preservado em `archive/original/` é uma baseline de conteúdo anterior, mas não reconstrói a história Git da estrutura modular.

Nenhum commit histórico foi fabricado, nenhuma data foi retroagida e nenhum repositório remoto foi configurado. O primeiro commit, quando autorizado, será a primeira baseline Git rastreável desta cópia recuperada.

## Conteúdo da baseline

Finalizar Sessão já está incluído no estado baseline, juntamente com o código modular, documentação, testes, ferramentas, manifests, service worker, ícones oficiais, PDFs normativos, monólito portátil reconstruível e monólito original preservado.

Backups operacionais, exports JSON, credenciais, caches, temporários, logs, arquivos do macOS e relatórios locais não fazem parte da baseline. A política está em [`.gitignore`](../../.gitignore).

O snapshot externo é:

`/Users/joaopaulocirqueira/Documents/JP-Wealth-Pre-Git-Baseline-2026-08-03.zip`

O manifesto de hashes externo é:

`/Users/joaopaulocirqueira/Documents/JP-Wealth-Pre-Git-Baseline-2026-08-03-SHA256.txt`

O SHA-256 do ZIP é mantido no manifesto externo para evitar uma referência circular entre o ZIP e este documento. Os hashes dos artefatos principais são:

```text
dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
7a9f62290952dfc8a4d8c57c8831304654f8be59879357b4a0d993274187a8e2

archive/original/JP_Wealth_Risk_Terminal_V9.1_ORIGINAL_PRESERVADO.html
9095174aee1954c204d2ecf98c029d4499aa5c587d21dcac84fa129a64223b7e

index.html
80e8de086f34bb33e3991515b7e3f0659f6d47829b905b8b8d7b80fe2334b137

src/js/manifest.json
a569d5af85274a7ad852003360d5b41e00f01f600f094a8b1441c8a36c0c652d

sw.js
a9d9c5b70e2d5b594b67ccd46cc77eec76e614efc642cd26f8f50d62782f8520
```

## Validação registrada

Antes da inicialização Git, foram executados:

```text
python3 tools/rebuild_monolith.py
VALIDAÇÃO OK — 34 arquivos JS, 204 IDs estáticos, portátil reconstruído.
SMOKE OK — estado vazio, resets, ledger real, onboarding e 8 telas verificados.
FINALIZE SESSION OK — fingerprint, gate assíncrono, reload, duas abas, caches externos, fonte/monólito e console/pageerror verificados.
```

O teste de Finalizar Sessão captura programaticamente `console` e `pageerror`, cobre fonte e monólito, checkpoint após reload, importação, fingerprint de preço, corrida assíncrona, duas abas e preservação de cache externo.

## Limitações históricas e operacionais

- Não existe histórico Git anterior disponível para recuperação.
- O backup modular pré-alteração era parcial.
- O navegador não permite comprovar fisicamente que o download foi guardado.
- O teste automatizado usa respostas FX determinísticas e não substitui teste manual em dispositivo móvel.
- O teste de caches é executado separadamente do contexto funcional para controlar o ciclo real do service worker.

## Política para mudanças futuras

1. Criar ou atualizar o plano antes de alterar código.
2. Preservar dados reais fora do Git e exportar antes de mudanças N2/N3.
3. Não versionar credenciais, backups operacionais ou exports privados.
4. Validar a ordem do `src/js/manifest.json` e reconstruir o portátil.
5. Executar validação, smoke test e o teste específico da mudança.
6. Revisar `git diff --check`, riscos e arquivos staged antes de qualquer commit.
7. Registrar mudanças financeiras ou normativas somente com autorização formal.

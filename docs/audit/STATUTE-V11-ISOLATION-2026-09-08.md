# Adoção documental V11 — isolamento em 2026-09-08

**DOCUMENTARY ADOPTION ONLY — RUNTIME REMAINS LEGACY**

Este registro descreve o checkpoint local anterior ao commit. A entrega permitida
é um único commit na branch candidata e um Draft PR para main, condicionados aos
gates e à auditoria independente posterior ao freeze. Não autoriza merge, marcar
PR pronto ou deploy. Commit, SHA remota e URL do PR serão registrados no relatório
externo de entrega e no próprio PR, sem fabricar uma referência ao próprio commit.

## Base, autoridade e preservação

- Base exata: `02d3a6991fe82569c1fe232722d9b8566fc62ecd` (main limpa).
- Nova worktree: `JP Wealth OS V11 Documental`; branch `codex/statute-v11-documental`.
- Origem somente leitura: `JP Wealth OS Dashboard`, `codex/dashboard-complete`,
  mesmo HEAD base, 50 caminhos rastreados alterados e 8 não rastreados, 20 exclusões.
- Origem mista: build `9cf89998aa453da4`, portátil SHA256
  `dc2ffec8d82460cbd3c5ddbd93e8903d44929b424d0bc566a8c5b7b3ef92e4bb`.
  Esses resultados e artefatos não são prova do candidato isolado.
- Snapshot inicial externo: raiz, branch, HEAD, status, diff stat, diff binário,
  índice sem staged changes, hashes de todos os arquivos e manifestos existentes.
  Fingerprint da árvore de origem:
  `0f2852f018bbd09b49228d025c8531fb019508bbec151bf59296d12f1532e223`.
- Não executar reset/clean/stash/descarte, testes com rebuild ou edições na origem.
  A main também permanece intocada. A nova árvore foi inicialmente verificada limpa.
- Autoridade: pedido humano de isolamento e publicação apenas como Draft PR;
  [CHG-2026-0908-V11-ISOLATION](../work/ACTIVE-TASK.md), N3/A4.
  Conteúdo normativo fornecido é fonte documental, não instrução para operar contas.

## Separabilidade

**SAFELY_SEPARABLE**: os 58 caminhos da origem foram classificados em A=33,
B=11, C=10, D=4 e E=0. A = exclusivamente V11; B = entrega Dashboard anterior;
C = compartilhado; D = não relacionado; E = indeterminado. Não houve reconstrução
financeira ou dependência funcional das melhorias locais do Dashboard.
Snapshots pré-V11 de onboarding/settings coincidem byte a byte com a base Git.
Os cinco hunks documentais do index e seis do README aplicaram à base sem conflito.

| Classe | Estado na origem | Caminho | Tratamento no isolado |
|---|---|---|---|
| A | deleted | `00 - FILOSOFIA E PROJETO/Antigo Estatuto/Estatuto Master - JP WEALTH.pdf` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Antigo Estatuto/NEO Estatuto Jp Wealth.pdf` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/00 - 1A ESTATUTO.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/00 - Estatuto V10.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/01 - Preâmbulo Institucional.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/02 - Livro I — Hierarquia Normativa e Definições.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/03 - Livro II — Estatuto Operacional — Arquitetura Quadrifásica de Risco Vertical.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/04 - Livro III — Governança, Funções e Controles Humanos.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/05 - Livro IV — Regime de Mesas Proprietárias (Prop Firms).md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/06 - Livro V — Alocação Patrimonial, Tesouraria e Distribuição.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/07 - Livro VI — Método e Execução Técnica (Nocuda).md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/08 - Livro VII — Disposições Finais, Revisão e Ratificação.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/09 - Anexo A — Tabela Mestra Consolidada de Fases.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/10 - Anexo B — Registro de Deliberações e Alterações da Consolidação.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/11 - Anexo C — Itens Pendentes de Ratificação.md` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/2.  Jp Wealth Prop Firms.docx` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/3. Função de Auditoria.docx` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/4. Alocação Patrimonial Jp Wealth Holding.docx` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/Estatuto JP WEALTH UNIFICADO - cópia.pdf` | delete_only_in_isolated_worktree |
| A | deleted | `00 - FILOSOFIA E PROJETO/Norma Vigente/Planejamento de Mesa Proprietária.pdf` | delete_only_in_isolated_worktree |
| A | modified | `AGENTS.md` | copy_source_bytes |
| C | modified | `CHANGELOG.md` | select_or_recompose |
| C | modified | `README.md` | select_or_recompose |
| C | modified | `SESSION_HANDOFF.md` | select_or_recompose |
| C | modified | `build-id.js` | regenerate_official_pipeline_never_copy_mixed_artifact |
| C | modified | `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` | regenerate_official_pipeline_never_copy_mixed_artifact |
| D | modified | `docs/architecture/ARCHITECTURE.md` | exclude_retain_base |
| B | modified | `docs/architecture/CODE-MAP.md` | exclude_retain_base |
| D | modified | `docs/architecture/NAVIGATION-HIERARCHY.md` | exclude_retain_base |
| A | modified | `docs/architecture/PWA-UPDATE-LIFECYCLE.md` | copy_source_bytes |
| D | modified | `docs/architecture/STATE-SCHEMA.md` | exclude_retain_base |
| D | added | `docs/audit/CONSOLIDATION-2026-09-08.md` | exclude_retain_base |
| B | added | `docs/audit/CURRENT-STATE-HISTORY-2026-09-08.md` | exclude_retain_base |
| B | added | `docs/audit/DASHBOARD-EXECUTIVE-2026-09-08.md` | exclude_retain_base |
| B | added | `docs/audit/DASHBOARD-TASK-HISTORY-2026-09-08.md` | exclude_retain_base |
| B | added | `docs/audit/SESSION-HANDOFF-HISTORY-2026-09-08.md` | exclude_retain_base |
| C | added | `docs/audit/STATUTE-V11-UPDATE-2026-09-08.md` | select_or_recompose |
| A | modified | `docs/decisions/README.md` | copy_source_bytes |
| A | modified | `docs/governance/CONTEXT-MAP.md` | copy_source_bytes |
| C | modified | `docs/governance/CURRENT-STATE.md` | select_or_recompose |
| A | modified | `docs/governance/PROJECT-CONTEXT.md` | copy_source_bytes |
| A | added | `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` | copy_source_bytes |
| A | modified | `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf` | copy_source_bytes |
| A | added | `docs/normative/README.md` | copy_source_bytes |
| C | modified | `docs/work/ACTIVE-TASK.md` | select_or_recompose |
| C | modified | `index.html` | select_or_recompose |
| B | modified | `src/js/20-ui/03-main-render.js` | exclude_retain_base |
| B | modified | `src/js/20-ui/25-dash-macro.js` | exclude_retain_base |
| A | modified | `src/js/40-app/04-onboarding.js` | copy_source_bytes |
| A | modified | `src/js/40-app/09-settings-modal.js` | copy_source_bytes |
| B | modified | `src/js/40-app/15-ff-news.js` | exclude_retain_base |
| C | modified | `src/js/manifest.json` | select_or_recompose |
| B | modified | `src/styles/app.css` | exclude_retain_base |
| A | modified | `sw.js` | copy_source_bytes |
| A | modified | `tools/build_reproducibility_test.py` | copy_source_bytes |
| B | modified | `tools/dashboard_macro_test.py` | exclude_retain_base |
| B | modified | `tools/exec_three_column_test.py` | exclude_retain_base |
| A | modified | `tools/rebuild_monolith.py` | copy_source_bytes |

Os registros acima classificam o diff de origem, não adicionam autorização para
copiar o conteúdo inteiro de C. Reconstituição específica dos compartilhados:

- `index.html`: somente as cinco referências/avisos V11 abaixo; heading, detalhes
  e estrutura do Dashboard permanecem na base.
- `src/js/manifest.json`: somente hashes dos scripts de ordem 32 (onboarding) e 38
  (settings); 78 entradas e ordem inalteradas, inclusive os hashes do Dashboard.
- `README.md`: seis trechos V11 selecionados; nesta tarefa também foi acrescentada
  documentação do novo teste e suas contagens reais 44 standard/55 full/4 fast.
  Essa adição corresponde ao teste documental novo, sem importar ajustes anteriores
  de navegação, Dashboard, Finalizar Sessão ou a correção oportunista 77→78.
- `CHANGELOG.md`: somente uma entrada V11 recomposta; não copiar as entradas de
  consolidação ou Dashboard, nem identificar o build misto como candidato novo.
- CURRENT-STATE, ACTIVE-TASK e SESSION_HANDOFF: recompostos para a identidade,
  autoridade e evidência desta tarefa, com histórico anterior disponível no Git.
- Auditoria mista anterior: não copiada; este arquivo registra o isolado.
  O índice `docs/normative/README.md` conserva o conteúdo V11 da origem, com
  uma exceção explícita a `copy_source_bytes`: seu link UPDATE foi redirecionado
  para esta auditoria ISOLATION, evitando dependência do relatório misto.
- `build-id.js` e portátil: regenerados pelo pipeline oficial no isolado.

Hunks compartilhados: coordenadas zero-context na base e na origem, sem confundir
com a numeração final do novo arquivo. A coluna de ação é a seleção da origem.

| Arquivo | Hunk | Classe | Ação |
|---|---|---|---|
| `README.md` | `-3 +3` | A | copy_hunk |
| `README.md` | `-10,0 +11,9` | A | copy_hunk |
| `README.md` | `-23,2 +32,2` | D | exclude_hunk |
| `README.md` | `-28 +37` | D | exclude_hunk |
| `README.md` | `-30,2 +39,5` | D | exclude_hunk |
| `README.md` | `-35 +47,7` | B | exclude_hunk |
| `README.md` | `-37 +55` | A | copy_hunk |
| `README.md` | `-75 +93` | D | exclude_hunk |
| `README.md` | `-80 +98` | A | copy_hunk |
| `README.md` | `-94 +112,7` | D | exclude_hunk |
| `README.md` | `-99 +123` | D | exclude_hunk |
| `README.md` | `-110 +134` | A | copy_hunk |
| `README.md` | `-129,2 +153,2` | D | exclude_hunk |
| `README.md` | `-132 +156` | D | exclude_hunk |
| `README.md` | `-172 +196` | A | copy_hunk |
| `index.html` | `-604 +604` | A | copy_hunk |
| `index.html` | `-734,2 +734` | B | exclude_hunk |
| `index.html` | `-750,0 +750` | B | exclude_hunk |
| `index.html` | `-1038,0 +1039,2` | B | exclude_hunk |
| `index.html` | `-1360,2 +1362,2` | A | copy_hunk |
| `index.html` | `-1363,5 +1365,3` | A | copy_hunk |
| `index.html` | `-1416 +1416` | A | copy_hunk |
| `index.html` | `-1743 +1743` | A | copy_hunk |
| `src/js/manifest.json` | `-71 +71` | B | retain_base_hash |
| `src/js/manifest.json` | `-197 +197` | A | recompute_selected_hash |
| `src/js/manifest.json` | `-233 +233` | A | recompute_selected_hash |
| `src/js/manifest.json` | `-269 +269` | B | retain_base_hash |
| `src/js/manifest.json` | `-470 +470` | B | retain_base_hash |

A única ampliação de teste desta tarefa é `tools/statute_documentary_test.py`,
mais sua entrada adicional em `tools/quality_gate.py`. Nenhum teste anterior foi
removido, enfraquecido ou substituído. A reprodutibilidade recebeu apenas provas
adicionais relativas aos documentos. Não há segunda fixture normativa.

## Documentos e remoções

| Documento canônico | Bytes | SHA256 |
|---|---:|---|
| `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf` (125 páginas) | 1499074 | `2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769` |
| `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` (JPW-ANNEX-T03) | 57043 | `6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23` |

As fontes externas fornecidas foram copiadas por bytes após comparação de hashes.
O leitor incorpora a extração integral de 125 páginas e o Anexo integral, por
textContent, com SHA256 `f96afc12cec8da07c9f315a63700eff6f152428ede5663c43ea5b0007f32edab`.
Essa extração é consulta derivada; PDF/Anexo são os dois documentos canônicos.
Downloads preservam os originais, inclusive os embutidos base64 no portátil.
Nenhum PDF foi recomposto para ocultar divergências.

As 20 exclusões foram realizadas somente no isolado após verificar SHA256 e blob
na base. Recuperação por leitura: `git show <blob>`; não alterar a worktree original.
O PDF canônico anterior tinha SHA256
`a04bf9e3be2470c7e548620d2a1e889756ffca0cd806f65873348650725d9f2b`,
blob `420c05af3fa3ed631fd7f7ea688ae6aa6256295a`.

| Arquivo removido | SHA256 anterior | Git blob na base |
|---|---|---|
| `00 - FILOSOFIA E PROJETO/Antigo Estatuto/Estatuto Master - JP WEALTH.pdf` | `4c21a0f83fcacef3f113d49454eb537290e9ba10c5b2f39af5be31bf5f48218a` | `027dbdb5b43789d2797b3be9323b90d232a46b83` |
| `00 - FILOSOFIA E PROJETO/Antigo Estatuto/NEO Estatuto Jp Wealth.pdf` | `4eee6de13c68f93cffa0e10289d7a66f055352fcf6dc3edd4400d7a1a2ca9f7d` | `0fdfc6eac4d6e843a5f42e950ff9f9217c565f42` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/00 - 1A ESTATUTO.md` | `b97a4c266f4a4154ada946c76ec9b000ef4cd656fe5a3403eb4e4800a8de8d4d` | `8971d4d50206b849c41c245e0fe1bb90ddbd5e0a` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/00 - Estatuto V10.md` | `4f24d3e6147ba2bf5890b07a67f3bef76db65b789ba890066ca7bb5752a0b67e` | `a6dcdb23be1ecc6561fb5efd163c326676dded33` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/01 - Preâmbulo Institucional.md` | `d06659b0497580358160081deed9ff9360e3e71e561609907d70a5abd7dd11b2` | `43176401efc5b75512bd8ae9165446e9735c9eed` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/02 - Livro I — Hierarquia Normativa e Definições.md` | `51d7ae95354457151a962c12aa0417c88563cbb22e176c85d64899f8cdc1c3bf` | `cc26398dfcae601ced63dffcd1f89c2a9b54a3c6` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/03 - Livro II — Estatuto Operacional — Arquitetura Quadrifásica de Risco Vertical.md` | `001eab2eb3c8e07f3e5ffcbc221b276d2523faa6bc72df276348c595e8b89d8d` | `e1f3d703a000766ee90c7103dec5d53c5af98fe0` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/04 - Livro III — Governança, Funções e Controles Humanos.md` | `9989e5aea47708d8913393e7dbd6ace1926212e29ca00e717b922a5563f63e44` | `a3dc0aa96adfc6f394b9a8a23cb8fe4e7af093b2` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/05 - Livro IV — Regime de Mesas Proprietárias (Prop Firms).md` | `dfc0f80442ccf1f69cdfc5ed72f8f5e0196c70284b81193a98b26ad109a32a3d` | `41eef4225e6b455af7f75988c10904d090ad04fb` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/06 - Livro V — Alocação Patrimonial, Tesouraria e Distribuição.md` | `222475804eb64dc9b32fd8fd57462ba45665a35073e3bba83b98f792c6afb376` | `5da68338120ca16eb00058ee61379b30f10b395b` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/07 - Livro VI — Método e Execução Técnica (Nocuda).md` | `8c4bbffba8a48e01af69a74f1bd5b16402accc5a508a5a82ba0df1f08c0ca17f` | `5476a52506ebacd9ee9fbad39327e14d8ff76772` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/08 - Livro VII — Disposições Finais, Revisão e Ratificação.md` | `84cff8bcb27d922ff96e4531333292a1c0c4feca48afed4503813e6084acbdf9` | `3f8c381bf4361fa99245f27496b10c35d9e8f0d1` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/09 - Anexo A — Tabela Mestra Consolidada de Fases.md` | `b19c71e98b0b4018f5de320787ea8a031d95c93d9afef50750c3665d459256f8` | `f0fe3a8a6d32e90b6e90062a366fd31d6942ea4c` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/10 - Anexo B — Registro de Deliberações e Alterações da Consolidação.md` | `895c08773aff22b7f03f849926b7a1fee8b50a87b5511de5154eff32b52049c7` | `e42951fbe65be4ba4389f3ba683c038cba08b24f` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/11 - Anexo C — Itens Pendentes de Ratificação.md` | `9805321098eec688b58fe7a192aa5c74e549dac366a9c5dc89712d10e36b929b` | `587d7b1981b07e8391b264f174d7fbd29830d1d5` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/2.  Jp Wealth Prop Firms.docx` | `5a481d6148d700c9ef84a72bdcc2a3211f9b9e56328b48bf9742d6e9d7ddb741` | `244a08a22e24a0b0cfab9f74d0adf0dcb45c6c18` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/3. Função de Auditoria.docx` | `a884f8114013bb5e292606bd7a2b0ae88d0cfe2856f3d7bab1cb9afd7ccab084` | `be2c1242d7f3d35813fb02aa199025ee39b31955` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/4. Alocação Patrimonial Jp Wealth Holding.docx` | `717e811673c876911f726b6145b113d07c1e0bf1e50a14bfacc9ecd1d5f861f3` | `db5ce4b8bb8c40cf0c2395ab8d8f897d1bdcb59b` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/Estatuto JP WEALTH UNIFICADO - cópia.pdf` | `a04bf9e3be2470c7e548620d2a1e889756ffca0cd806f65873348650725d9f2b` | `420c05af3fa3ed631fd7f7ea688ae6aa6256295a` |
| `00 - FILOSOFIA E PROJETO/Norma Vigente/Planejamento de Mesa Proprietária.pdf` | `5c0e2e18880159bf42b8a25eeefba34243f2989a882c44c4371ec3f6b8d2678e` | `e0416caec90a76bb2f6d602810ceb1103ff480de` |

Históricos de contexto preservados no Git base: CURRENT-STATE blob
`fdddf782db3bd260899a2da1b4734a87d6b0fdb3`, SESSION_HANDOFF blob
`e8283d5b82499b0639e5ec0d588a0e8b13618807` e ACTIVE-TASK blob
`65a308fd9e9de41ba2c51b8aa3bc6574858295f5`. Não foram copiadas as quatro auditorias
históricas da entrega Dashboard anterior para este candidate.

## Delta semântico e conflitos que permanecem

- Aceite é identificado por `V11.0+JPW-ANNEX-T03`. Aceite de outra versão não
  pré-marca a V11 nem reutiliza sua data. A confirmação grava somente pelo fluxo
  explícito existente; consultar/cancelar não promove ou migra aceite histórico.
- O service worker atende os dois caminhos documentais antes do fallback de
  navegação. Precache recebe os dois originais; o fallback geral permanece igual.
- O builder inclui documentos e gerador no fingerprint; somente o portátil troca
  os hrefs documentais por dados base64 dos originais. Não muda fórmulas.
- A interface identifica adoção documental e motor legado. Fases, DD, TRA,
  satélites, VRM, stop, quarentena, FCR/FEO operacionais e dados não foram adaptados.

| Tema | Fonte documental / divergência | Tratamento desta entrega |
|---|---|---|
| FCR | PDF p86 Art13.2§1 e p91/110: 22% do capital nominal; Anexo X-FCR/M-02/K-01: DD_MAX×SI | Conflito aberto; capital nominal não presumido igual a SI |
| FEO | PDF p87–88 Art13.3§§1/5/7/10: percentual nominal/homologação; Anexo P-29/K: despesas reais, percentual derivado | Não escolher fórmula nem resolver precedência |
| Abertura do ciclo | PDF: verificar fundos antes de fixar SI; redação externa posterior: ato único com ordem lógica | Não inventar sequência executável |
| Risco pendente | Anexo D-11 omite risco reservado de ordens pendentes ampliadoras presente no PDF p70 Art8.4§9 | Registrar omissão, sem implementação |
| Risco comprometido | Fluxo G não explicita camada de orçamento da operação exigida no PDF p66/71 | TRA não substitui essa camada |
| FEO Parte M | BLOCKS_OPERATION=NÃO precisa distinguir operação existente de novo período bloqueado sem fundos (PDF p88/91) | Não remover bloqueios por interpretação |
| TRA e satélites | P-14/P-18/P-17 pendentes; P-30 revogado/pendente, replicação suspensa | PENDING não admite zero/fallback nem prova operabilidade |
| ATR | Limiar delegado incompletamente catalogado | Sem completar parâmetro por suposição |
| Norma × runtime | Runtime quadrifásico, DD15%, fatores66/50/33, FCR15%, quarentena90 automática; V11 descreve seis fases/DD22% e novos contratos | Todos os cálculos existentes permanecem legados |

Atos externos identificados na revisão documental: `4 — Fundos Segregados e
Proteção ao Gestor.md`, `7 — Alocação Patrimonial, Tesouraria e Distribuição.md` e
relatório de execução T04C-R1B-2 indicam redação posterior ao PDF fornecido. Não
foram convertidos em terceira fonte canônica, copiados ou usados para modificar o
PDF. CANONICAL não significa HOMOLOGATED. Os dez ADRs anteriores são propostas
históricas; não adotar seus parâmetros 53/40/27 ou F1,25 por associação documental.

## Impacto agentic e segurança

**IMPACT DETECTED.** A base da conclusão é a troca de autoridade documental em
AGENTS, PROJECT-CONTEXT, CONTEXT-MAP e índices. A reconciliação é limitada a fontes,
estado e autorização desta tarefa. Classificação N3/A4, precedência humana,
guardas financeiras e gates continuam íntegros; o novo teste acrescenta cobertura.
O CURRENT-STATE identifica a base por SHA puro; build/fingerprint identificam o diff.

Navegadores e dados de teste são sintéticos e isolados. Não ler credenciais,
`.env`, bases locais, backups ou contas reais; o sentinela vazio rastreado
`data/backups/.gitkeep` não contém dados. Segurança será verificada no diff e
arquivos pretendidos, com registro externo sem conteúdo sensível.

## Topologia Git e ausência de deploy

A investigação anterior à criação da branch identificou repositório público
`jojoaopauloalvescirqueira-sketch/App-Jp-Wealth`, default main na base solicitada,
sem homepage/Pages identificados, listas públicas de deployments e environments
vazias e status da base apenas Quality Gate/GitHub Actions. O único workflow
versionado executa qualidade com contents:read; não contém comando de deploy.
`netlify.toml` declara build/publish, mas não prova integração ativa. Não há state
local Netlify nas worktrees inspecionadas. Metadados de hooks não estavam acessíveis
sem autenticação; nenhuma credencial foi lida para tentar resolver a lacuna.

O proprietário esclareceu nesta tarefa: “Não foque no netlify por hora, ele ainda
não está em uso”. Portanto não há produção Netlify ativa informada pelo responsável;
prosseguir somente com a branch e Draft PR GitHub. Não afirmar que main já alimenta
produção nem que branch/PR gera preview. Site ID, último deploy, SHA publicada e
rollback de produção não foram identificados e não são necessários nesta etapa.
Rollback documental futuro seria mudança explícita no Git; nesta tarefa não há
produção alterada para reverter. Nenhum merge, ready, deploy ou força de push é permitido.

## Validação do candidato isolado

Build novo: `1ee88bab37539798`. Fingerprint completo dos inputs oficiais:
`1ee88bab3753979862fcd0c428dea50960d23ee0128dd5dfe56e2fbd7b6e4b29`.
Portátil SHA256: `83f63f65e11fea8999e8b6b87403aeb718758fbd02187c41da94bc8dfeb99cbb`.
Resultados produzidos exclusivamente nesta worktree; todos os arquivos da
fotografia anterior à full foram reconferidos byte a byte ao terminar a suíte.
Nenhum PASS da origem foi reaproveitado.

| Verificação | Resultado do isolado |
|---|---|
| Build oficial e reprodutibilidade focal | PASS; originais embutidos, inputs ausentes bloqueados e ruído local ignorado |
| Teste documental focal R4 | PASS: 7 aceites; leitor integral; 4 consultas/navegações e downloads PWA online/offline; 2 downloads reais do portátil file:// offline |
| Full aplicável, com teste documental acrescentado | **55/55 PASS**, inclusive Finalizar Sessão, segurança de importação e upgrade do SW |
| Fast final | **4/4 PASS** após reconciliação documental; este registro apenas acrescenta o resultado |
| Higiene, links e arquivos inesperados | PASS na revisão local; confirmação final vinculada ao freeze |
| Segurança/escopo preliminar | Sem achados; fontes financeiras, Galton/finalização e seis arquivos Dashboard byte-idênticos à base |

Full iniciou em `2026-09-08T20:02:17-03:00` e terminou em `2026-09-08T20:11:09-03:00`;
SHA256 do manifesto full externo: `98a1eedca50083078e95373ef225b32fa160110f97716fe3e19cc6b013be1348`.
SHA256 do manifesto fast final externo: `9aa478d00c61da3e4bafd528bae77f799b685bfb1697e1f0fcc08ae5888e8acd`.
SHA256 da evidência focal R4 externa: `a1b941becb3a862dcc72d0aa896e3071d748aa9dd524e0b2f1a26b168d809e17`.
Os artefatos de execução locais ficam em tools/.artifacts (ignorados pelo Git),
com cópia preservada no dossiê externo de isolamento. A suíte full também executou
novamente o teste documental e a reprodutibilidade sobre este mesmo build.

As três primeiras execuções do teste novo tiveram **TEST_HARNESS_FAIL**, com logs
externos preservados e triagem explícita:

1. R1 esperava persistir uma máscara de senha no novo log de edição. A sanitização
   recursiva já existente na base a remove; histórico antigo e campos do aceite
   persistiram corretamente. O teste passou a exigir exatamente essa sanitização
   do único novo campo e identidade de todo o restante, antes e após recarga.
2. R2 registrava um callback Python builtin (`list.append`) que o wrapper do
   Playwright não aceita. Troca restrita por lambda, sem mudar qualquer assert.
3. R3 comparava bytes expostos por `response.body()` após transformação do Chromium:
   HTML interno do viewer PDF e texto Markdown decodificado/reencodado. A mesma
   transformação ocorre sem service worker. Os seis downloads reais de diagnóstico
   (com/sem SW e offline) preservaram os originais. O teste final exige MIME,
   status, resposta do SW e ausência de app shell na navegação, além do SHA do fetch
   e download real byte-idêntico do mesmo caminho em cada caso online/offline.

Nenhuma dessas correções alterou o produto, contratos financeiros, o teste de
Finalizar Sessão ou timeouts. Limitação do servidor local de teste: Markdown sem
charset pode aparecer com acentos incorretos na visualização bruta do Chromium;
o leitor integrado usa UTF-8 correto e os downloads mantêm os bytes originais.
Não foi alterada infraestrutura para mascarar esse comportamento do viewer.

Comandos oficiais: `python tools/rebuild_monolith.py`,
`python tools/statute_documentary_test.py`,
`python tools/build_reproducibility_test.py`,
`python tools/quality_gate.py --tier full`,
`python tools/quality_gate.py --tier fast`.
Runtime de validação: Python 3.12.14 / Playwright 1.60.0 / Chromium isolado.

## Limitação histórica de Finalizar Sessão / Galton

Os candidatos mistos anteriores e8e9142d3d32fc6e e277588d837daca17 tiveram 53PASS e
1PRODUCT_FAIL na suíte full: depois do reset remoto do portátil, a chave Galton
estava ausente, mas currentSpeed era4 em vez de1. O candidato misto9cf89998aa453da4
passou54/54 posteriormente; isso não encerra a intermitência. Código e teste desse
fluxo permanecem byte-idênticos à main02d3 no isolado.

A triagem estática sugere remontagem antes da limpeza da preferência persistida,
com leitura da velocidade antiga pelo construtor. É hipótese causal, não prova da
sequência exata: não classificar automaticamente BASELINE_FAIL, TEST_HARNESS_FAIL
ou NO_REGRESSION. Não aumentar timeout, alterar seletor, modificar Galton/finalização
ou esconder a falha para publicar este pacote. Um novo PASS não elimina esse risco.

## Freeze, auditoria e próximo gate

Este documento encerra o checkpoint de testes anterior ao freeze final. O
manifesto de freeze de todos os arquivos e o resultado da auditoria independente
read-only são evidências externas posteriores, registradas no relatório de entrega
e no PR. Seu resultado não é antecipado por este checkpoint. A auditoria deve
reconferir fonte → build → runtime, escopo, documentos, aceite, offline e ausência
de drift, inclusive depois do commit. Critical/High impede commit/push.

Após gates válidos, o único próximo ato autorizado é commit único, push da branch
candidata e Draft PR. Revisão humana do escopo documental é o próximo gate;
adequação financeira, resolução FCR/FEO, merge e deploy requerem trabalho e
autorização próprios. Este documento não declara READY_FOR_NEXT_DEVELOPMENT_CYCLE.
